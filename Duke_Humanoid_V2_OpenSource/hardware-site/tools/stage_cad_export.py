"""Stage a Fusion export (from tools/fusion_export/ + tools/fusion_export_modules/) into docs/files/.

    python tools/stage_cad_export.py ../cad/humanoid_2.1_latest_<stamp> [--rev 01] [--apply]

Three download levels, all read from <export>/tree.csv (the `file_name` column is
unique per component: a second, different component with the same name is
`name~2`, and that is the name of its STEP/STL in the export):

  parts    <export>/step/<file_name>.step -> docs/files/step/<part_id>_rev<NN>.step
           <export>/print/<file_name>.stl -> docs/files/print/<part_id>_rev<NN>.stl   (printed parts)
           for every part the site lists (docs/data/cnc-parts.csv, printed-parts.csv).
  vendor   <export>/step/<file_name>.step -> docs/files/vendor/<file_name>.step
           for every other component with bodies (actuator internals, electronics,
           bearings, cables ...) except fasteners: a name containing screw / bolt /
           nut / washer / insert / magnet / pin / rivet, or a Fusion mass under 3 g.
           A file name over 80 characters is cut to 80 plus a hash of the full name
           (Windows path limit); downloads.json still keys it by the full name.
  modules  <export>/modules/<file>.step   -> docs/files/modules/<module_id>_rev<NN>.step
           for every row of docs/data/modules.csv (tools/gen_modules.py) with class
           `module` or `vendor`; a STEP over 95 MB is zipped.
  robot    <export>/assembly/*.step/.f3z  -> docs/files/assembly/<design>_rev<NN>.*  (zipped over 95 MB)

Budget: docs/files/ must stay under 700 MB. When the vendor STEP files would
push it over, only vendor components above 20 g are staged and the run says so.

Also writes docs/assets/viewer/downloads.json: {key: [{label, href}]} for every
file under docs/files/, key = site part_id, `vendor:<file_name>` or module_id
(plus `robot` for the whole-robot files), href relative to the docs root
(`files/...`; the page prefixes it with its data-base).

Run gen_vendor_map.py and gen_modules.py first (the vendor list and the module
classes come from their CSVs), and gen_cad_manifest.py afterwards. Nothing here
edits a page.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
DATA = SITE / "docs" / "data"
FILES = SITE / "docs" / "files"
DOWNLOADS_JSON = SITE / "docs" / "assets" / "viewer" / "downloads.json"

# Site IDs that were truncated or renamed relative to the Fusion component names.
ALIASES = {
    "CNC_arm01_shoulder_roll_front_bearing": "CNC_arm01_shoulder_roll_front_bearing_retainer",
    "CNC_arm02_shoulder_roll_back_bearing": "CNC_arm02_shoulder_roll_back_bearing_retainer",
    "CNC_arm04_shoulder_roll_support_shaft": "CNC_arm04_shoulder_elbow_support_shaft",
    "CNC_arm07_elbow_front_bearing": "CNC_arm07_elbow_front_bearing_retainer",
    "CNC_arm08_elbow_back_bearing": "CNC_arm08_elbow_back_bearing_retainer",
    "CNC_leg12_lower_leg_bearing": "CNC_leg12_lower_leg_bearing_cap",
    "CNC_arm09_elbow_output_shaft": "CNC_arm09_elbow_roll_output_shaft",
}
PRINTED_PREFIX = "3DP_"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_printed import PRINTED, pick as printed_pick  # noqa: E402  (fusion name[|scope], part_id, ...)
ALIASES.update({pid: name.split("|")[0] for name, pid, _, _ in PRINTED})
PRINTED_KEYS = {pid: name for name, pid, _, _ in PRINTED}      # part_id -> "Component42|leg" etc.
PRINTED_IDS = set(PRINTED_KEYS)
# Fusion components that are the same geometry under a second name (left/right
# copies renamed): their occurrences belong to the same part_id.
DUPLICATE_NAMES = {
    "CNC_leg09_knee_back": "CNC_leg09_knee_motor_back_cover",
    "CNC_leg10_lower_leg_output_shank": "CNC_leg10_knee_output_shank",
    "CNC_leg11_lower_leg_support_shank": "CNC_leg11_knee_support_shank",
    "CNC_leg12_lower_leg_bearing_cap_1": "CNC_leg12_lower_leg_bearing_cap",
    "CNC_leg12_lower_leg_bearing_cap (1)": "CNC_leg12_lower_leg_bearing_cap",
}
FASTENER = re.compile(r"(?<![a-z])(screw|bolt|nut|washer|insert|magnet|pin|rivet)(?![a-z])", re.I)
FASTENER_MAX_G = 3.0
VENDOR_MIN_G_WHEN_TIGHT = 20.0
MAX_FILE = 95 * 1024 * 1024
MAX_TOTAL = 700 * 1024 * 1024
MAX_NAME = 80
LABELS = {".step": "STEP", ".stp": "STEP", ".stl": "STL", ".3mf": "3MF", ".pdf": "PDF",
          ".f3z": "Fusion archive", ".f3d": "Fusion archive", ".zip": "STEP (zip)"}


# Component names inherited from vendor CAD carry CJK text: RobStride's RS06
# STEP is named "...(开模版)...", its tooling-version tag. The site is English
# only, data files included, so those runs are translated on the way out. An
# unknown run becomes a marker rather than a guess.
CJK_TERMS = {"开模版": "tooling-version"}
CJK_RUN = re.compile(r"[　-〿一-鿿＀-￯]+")


def englishise(text: str) -> str:
    """Replace every CJK run in ``text`` with its English tag."""
    return CJK_RUN.sub(lambda m: CJK_TERMS.get(m.group(0), "cjk-name"), text)


def strip_qty(name: str) -> str:
    return re.sub(r"_x\d+(?=_)", "", name)


def base_name(file_name: str) -> str:
    """tree.csv file_name without the `~N` uniqueness suffix."""
    return re.sub(r"~\d+$", "", file_name)


def slug(name: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", name.lower())).strip("-")


def short_name(file_name: str) -> str:
    """A file name that keeps Windows paths under the 260-character limit."""
    if len(file_name) <= MAX_NAME:
        return file_name
    return file_name[:MAX_NAME].rstrip("_-.") + "-" + hashlib.sha1(file_name.encode()).hexdigest()[:8]


def site_ids() -> dict[str, str]:
    out = {}
    for f in ("cnc-parts.csv", "printed-parts.csv"):
        with open(DATA / f, encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                pid = r["part_id"].strip()
                if pid and not pid.startswith("MAT_"):
                    out[pid] = f
    return out


def load_tree(export: Path) -> list[dict]:
    with open(export / "tree.csv", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if rows and "file_name" not in rows[0]:
        sys.exit(f"{export / 'tree.csv'} has no file_name column: re-export with the current tools/fusion_export")
    return rows


def mass_of(row: dict) -> float:
    try:
        return float(row.get("mass_g") or 0)
    except ValueError:
        return 0.0


def is_fastener(row: dict) -> bool:
    return bool(FASTENER.search(row["fusion_name"])) or mass_of(row) < FASTENER_MAX_G


def _candidates(tree: list[dict], name: str) -> list[dict]:
    want = strip_qty(name)
    out = []
    for r in tree:
        if int(r["bodies"]) == 0:
            continue
        b = base_name(r["file_name"])
        if b == name or strip_qty(b) == want or r["fusion_name"] == name:
            out.append(r)
    return out


def resolve_site_parts(tree: list[dict]) -> tuple[dict[str, dict], dict[str, str]]:
    """Site part_id -> {"src": file_name, "qty": n, "rows": [...]} for every part the site
    lists that is in the tree, and file_name -> part_id for every tree component that
    belongs to a site part (duplicates and left/right copies included).

    Printed parts are resolved exactly as gen_printed.py resolves them (`pick`, with
    its `name|scope` keys), machined parts by Fusion name with the `_x<qty>` token
    and the `~N` suffix ignored plus DUPLICATE_NAMES. A part's source file is its
    first component in tree (path) order, the one gen_printed.py reports."""
    by_fusion: dict[str, list[dict]] = {}
    for r in tree:
        if int(r["bodies"]) > 0:
            by_fusion.setdefault(re.sub(r" \(\d+\)$", "", r["fusion_name"]), []).append(r)
    parts: dict[str, dict] = {}
    owner: dict[str, str] = {}
    for pid in site_ids():
        if pid in PRINTED_KEYS:
            cands = list(printed_pick(by_fusion, PRINTED_KEYS[pid]))
        else:
            name = ALIASES.get(pid, pid)
            cands = _candidates(tree, name)
            for dup, canon in DUPLICATE_NAMES.items():
                if strip_qty(canon) == strip_qty(name):
                    cands += [r for r in _candidates(tree, dup) if r not in cands]
        if not cands:
            continue
        parts[pid] = {"src": cands[0]["file_name"], "qty": sum(int(r["qty"]) for r in cands), "rows": cands}
        for r in cands:
            owner.setdefault(r["file_name"], pid)
    return parts, owner


def vendor_rows(tree: list[dict], owner: dict[str, str]) -> list[dict]:
    """Every component with bodies that is not a site part, in tree order."""
    return [r for r in tree if int(r["bodies"]) > 0 and r["file_name"] not in owner]


def read_modules() -> list[dict]:
    p = DATA / "modules.csv"
    if not p.is_file():
        return []
    with open(p, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def copy_or_zip(src: Path, dst: Path) -> tuple[Path, int]:
    """Copy src to dst, or to dst.zip when it is over 95 MB. Returns (path written, bytes)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.stat().st_size > MAX_FILE and src.suffix.lower() in (".step", ".stp"):
        z = dst.with_name(dst.name + ".zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            zf.write(src, dst.name)
        return z, z.stat().st_size
    shutil.copy2(src, dst)
    return dst, dst.stat().st_size


def folder_bytes(folder: Path) -> int:
    return sum(p.stat().st_size for p in folder.rglob("*") if p.is_file()) if folder.is_dir() else 0


def write_downloads_json(module_ids: dict[str, str], vendor_keys: dict[str, str]) -> int:
    """downloads.json from what is under docs/files/ now.

    module_ids: staged module file stem (without _rev) -> module_id
    vendor_keys: vendor file stem -> full tree file_name"""
    out: dict[str, list[dict]] = {}
    for kind in ("step", "print", "drawings", "plates", "assembly", "modules", "vendor"):
        folder = FILES / kind
        if not folder.is_dir():
            continue
        for p in sorted(folder.iterdir()):
            if not p.is_file() or p.name.startswith("."):
                continue
            zipped = p.suffix.lower() == ".zip" and p.stem.lower().endswith(".step")
            stem = p.stem[:-5] if zipped else p.stem      # a Fusion name may itself end in .STEP
            stem = re.sub(r"_rev\d+$", "", stem)
            if kind == "vendor":
                key = "vendor:" + vendor_keys.get(stem, stem)
            elif kind == "modules":
                key = module_ids.get(stem, stem)
            else:
                key = stem
            label = LABELS.get(p.suffix.lower(), p.suffix.lstrip(".").upper())
            entry = {"label": label, "href": f"files/{kind}/{p.name}"}
            out.setdefault(key, []).append(entry)
            if kind == "assembly":
                out.setdefault("robot", []).append(entry)
    DOWNLOADS_JSON.parent.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_JSON.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return len(out)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")       # Windows console: keep the em dashes
    ap = argparse.ArgumentParser()
    ap.add_argument("export")
    ap.add_argument("--rev", default="01")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--no-vendor", action="store_true", help="skip the vendor STEP files")
    ap.add_argument("--no-modules", action="store_true", help="skip the module STEP files")
    a = ap.parse_args()
    exp = Path(a.export)
    tree = load_tree(exp)
    parts, owner = resolve_site_parts(tree)
    ids = site_ids()
    missing = [pid for pid in ids if pid not in parts]

    # ---- parts -------------------------------------------------------------
    plan = []
    for pid, e in parts.items():
        printed = pid in PRINTED_IDS or ALIASES.get(pid, pid).startswith(PRINTED_PREFIX)
        plan.append((pid, e["src"], printed, e["qty"]))
    print(f"{len(plan)} site parts matched to Fusion components, {len(missing)} not in the CAD:")
    for pid in missing:
        print(f"  NOT IN CAD  {pid}")
    for pid, src, printed, qty in plan:
        print(f"  {'3DP' if printed else 'CNC'}  {pid:45} <- {src}  (qty {qty})")
    fusion_only = sorted({strip_qty(base_name(r["file_name"])) for r in tree
                          if int(r["bodies"]) > 0 and r["file_name"] not in owner
                          and base_name(r["file_name"]).startswith(("CNC_", "3DP_"))})
    if fusion_only:
        print(f"{len(fusion_only)} CNC/3DP components in the CAD with no site row:")
        for k in fusion_only:
            print(f"  NOT ON SITE {k}")

    # ---- vendor ------------------------------------------------------------
    vend = [] if a.no_vendor else [r for r in vendor_rows(tree, owner) if not is_fastener(r)]
    vend_files = [(r, exp / "step" / (r["file_name"] + ".step")) for r in vend]
    vend_absent = [r["file_name"] for r, p in vend_files if not p.is_file()]
    vend_bytes = sum(p.stat().st_size for _, p in vend_files if p.is_file())
    print(f"\n{len(vend)} vendor/other components to stage as STEP "
          f"({vend_bytes / 2**20:.1f} MB; {len(vend_absent)} not in the export yet)")

    # ---- modules -----------------------------------------------------------
    mods = [] if a.no_modules else [m for m in read_modules() if m["class"] in ("module", "vendor") and m["file"]]
    mod_files = [(m, exp / "modules" / m["file"]) for m in mods]
    mod_absent = [m["file"] for m, p in mod_files if not p.is_file()]
    mod_bytes = sum(p.stat().st_size for _, p in mod_files if p.is_file())
    print(f"{len(mods)} modules to stage ({mod_bytes / 2**20:.1f} MB; {len(mod_absent)} not in the export yet)"
          + ("" if mods or a.no_modules else " — run gen_modules.py first"))

    # ---- budget ------------------------------------------------------------
    existing = sum(folder_bytes(FILES / k) for k in ("step", "print", "drawings", "plates", "assembly"))
    if a.no_vendor:                     # a skipped folder keeps what it holds now
        existing += folder_bytes(FILES / "vendor")
    if a.no_modules:
        existing += folder_bytes(FILES / "modules")
    total = existing + vend_bytes + mod_bytes
    print(f"budget: {existing / 2**20:.0f} MB staged now + {vend_bytes / 2**20:.0f} MB vendor + "
          f"{mod_bytes / 2**20:.0f} MB modules = {total / 2**20:.0f} MB of {MAX_TOTAL / 2**20:.0f} MB")
    tight = total > MAX_TOTAL
    if tight:
        vend_files = [(r, p) for r, p in vend_files if mass_of(r) > VENDOR_MIN_G_WHEN_TIGHT]
        vend_bytes = sum(p.stat().st_size for _, p in vend_files if p.is_file())
        total = existing + vend_bytes + mod_bytes
        print(f"  OVER BUDGET: vendor STEP limited to components above {VENDOR_MIN_G_WHEN_TIGHT:.0f} g "
              f"({len(vend_files)} files, {vend_bytes / 2**20:.0f} MB) -> {total / 2**20:.0f} MB")
        if total > MAX_TOTAL:
            print("  STILL OVER BUDGET after the vendor cut; nothing copied", file=sys.stderr)
            return 1

    if not a.apply:
        print("\n(dry run; add --apply to copy)")
        return 0

    copied, absent, sizes = 0, [], {}
    for pid, src, printed, _ in plan:
        pairs = [("step", ".step", "step")]
        if printed:
            pairs.append(("print", ".stl", "print"))
        for sub, ext, dst_sub in pairs:
            s = exp / sub / (src + ext)
            if not s.is_file():
                absent.append(str(s.relative_to(exp)))
                continue
            d = FILES / dst_sub / f"{pid}_rev{a.rev}{ext}"
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, d)
            copied += 1
    for s in sorted((exp / "assembly").glob("*")):
        if s.suffix.lower() not in (".step", ".stp", ".f3z") or s.name.endswith(".f3z.f3d"):
            continue
        d = FILES / "assembly" / f"{s.stem}_rev{a.rev}{s.suffix.lower()}"
        if s.stat().st_size > MAX_FILE and s.suffix.lower() == ".f3z":
            print(f"  skipped (over 95 MB, publish as a release asset): {s.name}")
            continue
        w, _ = copy_or_zip(s, d)
        if w != d:
            print(f"  zipped (over 95 MB): {w.name}")
        copied += 1

    # short file stem -> full tree file_name for every component, so downloads.json keys
    # the vendor folder by the full name even on a run that skips the vendor files
    vendor_keys = {short_name(r["file_name"]): r["file_name"] for r in tree}
    if vend_files:
        (FILES / "vendor").mkdir(parents=True, exist_ok=True)
        for old in (FILES / "vendor").glob("*"):
            old.unlink()          # the vendor set is regenerated whole
    for r, s in vend_files:
        if not s.is_file():
            absent.append(str(s.relative_to(exp)))
            continue
        stem = short_name(r["file_name"])
        w, n = copy_or_zip(s, FILES / "vendor" / (stem + ".step"))
        sizes["vendor"] = sizes.get("vendor", 0) + n
        copied += 1

    module_ids: dict[str, str] = {}
    for m, s in mod_files:
        if not s.is_file():
            absent.append(str(s.relative_to(exp)))
            continue
        stem = f"{m['module_id']}_rev{a.rev}"
        module_ids[m["module_id"]] = m["module_id"]
        w, n = copy_or_zip(s, FILES / "modules" / (stem + ".step"))
        if w.suffix == ".zip":
            print(f"  zipped (over 95 MB): {w.name}")
        sizes["modules"] = sizes.get("modules", 0) + n
        copied += 1

    keys = write_downloads_json(module_ids, vendor_keys)
    grand = folder_bytes(FILES)
    print(f"\ncopied {copied} files into docs/files/ "
          f"(vendor {sizes.get('vendor', 0) / 2**20:.1f} MB, modules {sizes.get('modules', 0) / 2**20:.1f} MB); "
          f"docs/files is now {grand / 2**20:.0f} MB; downloads.json has {keys} keys")
    for x in absent:
        print(f"  export missing: {x}")
    if grand > MAX_TOTAL:
        print(f"ERROR: docs/files is over the {MAX_TOTAL / 2**20:.0f} MB budget", file=sys.stderr)
        return 1
    print("now run: python tools/gen_cad_manifest.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
