"""Map the vendor components of the Fusion model to the BOM -> docs/data/vendor-parts.csv
and docs/assets/viewer/vendor-map.json.

    python tools/gen_vendor_map.py ../cad/<export>            (needs <export>/tree.csv with file_name)

A *vendor/other* component is every component with bodies in tree.csv that is
not one of the site's own parts (docs/data/cnc-parts.csv, printed-parts.csv,
resolved the way stage_cad_export.py resolves them). Each gets one row in
vendor-parts.csv; `part_id` is filled only when a rule below matches.

Matching is by explicit rules (RULES) tested against the component's own Fusion
name first and then against each ancestor in its occurrence path, nearest first:
an actuator's rotor, stator core or PCB is matched through its `Robstride 0N`
parent, a RealSense lens through `IntelRealsense_D435...`. `note` says which
ancestor carried the match and what the model and the BOM disagree on (model
name vs BOM model number, modelled count vs BOM quantity). Bearings and screws
match on the size in their Fusion name, which is how the team BOM lists them
(H0-H8). A component named in NO_ANCESTOR_MATCH (the USB cables inside the CAN
adapters) is never credited to an ancestor's row. The wiring lumps, the inserts
and magnets the BOM has no line for, and the site's own unlisted parts (gripper
prints, covers under `protections`) are left unmatched with a note that says
why. Nothing is guessed from a name that no rule covers.

tree.csv has one row per component with the count of all its occurrences and
the path of the first one only, so it cannot say how many of a bearing sit
inside a purchased actuator, and it lumps every ISO 14583 screw size the model
uses under one component. Both come from <export>/transforms.csv (one row per
leaf occurrence, each with its own name and full path) when it exists: each
FAS_* row gets the count fitted loose and the count inside a purchased assembly
(a bearing is one `bearing_<size>` assembly, its two `half-bearing` leaves
share the prefix), and a component whose occurrences carry more than one name
is left unmatched with the per-name breakdown in its note. Without
transforms.csv the counts fall back to tree.csv and the run says so.

vendor-map.json holds the matched components only:
    {"<file_name>": {"part_id", "bom_file", "description", "qty_in_model", "via"}}

Prints per BOM row the modelled count of the matched assemblies against
`qty_per_robot` (for FAS_* rows: fitted loose, plus the count inside a
purchased assembly), and the unmatched components above 20 g.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
DATA = SITE / "docs" / "data"
OUT_CSV = DATA / "vendor-parts.csv"
OUT_JSON = SITE / "docs" / "assets" / "viewer" / "vendor-map.json"
BOM_FILES = ("actuators.csv", "electronics.csv", "cables-connectors.csv", "fasteners.csv")
COLS = ["file_name", "fusion_name", "qty_in_model", "part_id", "bom_file", "description", "mpn", "vendor",
        "vendor_url", "note"]
REPORT_MIN_G = 20.0

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage_cad_export import (FASTENER, base_name, englishise, is_fastener, load_tree, mass_of,  # noqa: E402
                              resolve_site_parts, vendor_rows)

ACTUATOR = re.compile(r"robstride[ _-]*0*(\d)(?!\d)", re.I)
ACTUATOR_IDS = {"0": "ACT_RS00", "2": "ACT_RS02", "3": "ACT_RS03", "4": "ACT_RS04", "5": "ACT_RS05", "6": "ACT_RS06"}

# (regex on a Fusion component name, part_id, note). Tested on the component
# itself, then on its ancestors nearest first; the first hit wins.
RULES: list[tuple[re.Pattern, str, str]] = [
    (re.compile(r"^U-joint[ _-]*type[ _-]*C[ _-]*adapter", re.I), "EL_USBC_ADAPTER",
     "Fusion name `U-joint_type_C_adapter v3`: the USB-C right-angle adapter on each camera (site line E21)"),
    (re.compile(r"^bearing$", re.I), "FAS_BEARING_10X15X4",
     "Fusion component `bearing` in the camera column, 15 x 15 x 4 mm box: the 10 x 15 x 4 bearing H5"),
    (re.compile(r"^FEETECH[ _-]*HL[ _-]*3915", re.I), "EL_SERVO_FEETECH", ""),
    (re.compile(r"^wa[rv]eshare[ _-]*st[ _-]*servo", re.I), "EL_SERVO_DRIVER",
     "Fusion name `wareshare_st_servo_controller`; BOM row is the Waveshare bus servo driver"),
    (re.compile(r"^IntelRealsense[ _-]*D435", re.I), "EL_CAM_D436",
     "Fusion component is the Intel RealSense D435 model; the BOM row is the D436"),
    (re.compile(r"^IMU[ _-]*syd[ _-]*dynamics[ _-]*TM171", re.I), "EL_IMU_TM171", ""),
    (re.compile(r"^CAN[ _-]*Isolated", re.I), "EL_CAN_ADAPTER",
     "Fusion name `CAN_Isolated`; BOM row is the CANable PRO V2.0"),
    (re.compile(r"^MINISFORUM", re.I), "EL_COMPUTE_MINIPC",
     "Fusion name `MINISFORUM_AI_X1`; BOM row is the X1-470"),
    (re.compile(r"^battery[ _-]*zeee", re.I), "EL_BATTERY_6S",
     "2 packs modelled; the BOM counts one 2-pack"),
    (re.compile(r"^Vention[ _-]*USB[ _-]*Hub", re.I), "EL_USB_HUB", ""),
    (re.compile(r"^VEMONT[ _-]*USB-C[ _-]*Hub", re.I), "EL_USB_HUB",
     "Fusion names it a VEMONT USB-C hub; the BOM row (qty 3) is a Vention hub — 1 Vention + 2 VEMONT are modelled"),
    (re.compile(r"^buck[ _-]*converter[ _-]*48[ _-]*to[ _-]*12", re.I), "EL_BUCK_48V_12V", ""),
    (re.compile(r"^battery[ _-]*tester", re.I), "EL_VOLTAGE_CHECKER",
     "Fusion name `battery_tester`, 2 modelled; the team BOM's only matching row is the 1-8S LiPo "
     "voltage checker, also 2 off — the BOM does not name the modelled part **UNVERIFIED**"),
    (re.compile(r"^block$", re.I), "EL_DIST_BLOCK",
     "the four conductor blocks inside `power_block_casing`; the BOM row is 4 off. Its casing and "
     "`6x10-7holes` carrier are separate components with no BOM row **UNVERIFIED**"),
    # Bearings: the model names every bearing by its bore x OD x width, which is exactly how the
    # team BOM lists them (H0-H5). The assembly `bearing_<size>_<series>` is one bearing; its two
    # `half-bearing_<size>` children are the modelled halves of that same bearing.
    (re.compile(r"bearing[ _-]*45x58x7", re.I), "FAS_BEARING_45X58X7", ""),
    (re.compile(r"bearing[ _-]*50x65x7", re.I), "FAS_BEARING_50X65X7", ""),
    (re.compile(r"bearing[ _-]*35x44x5", re.I), "FAS_BEARING_35X44X5", ""),
    (re.compile(r"bearing[ _-]*35x47x7", re.I), "FAS_BEARING_35X47X7", ""),
    (re.compile(r"bearing[ _-]*30x37x4", re.I), "FAS_BEARING_30X37X4", ""),
    (re.compile(r"bearing[ _-]*10x15x4", re.I), "FAS_BEARING_10X15X4", ""),
    # Screws: ISO 14583 hexalobular socket = the Torx drive the BOM's screw lines name.
    # Fusion models them as *pan* head, the BOM lines say button head: UNVERIFIED (SCREW_NOTE).
    # `M3x10` does not match `M3.5x10`; the occurrence names come from transforms.csv.
    (re.compile(r"ISO[ _-]*14583.*[ _-]M3x10", re.I), "FAS_SCREW_M3X10_TORX_BH", ""),
    (re.compile(r"ISO[ _-]*14583.*[ _-]M4x8", re.I), "FAS_SCREW_M4X8_TORX_BH", ""),
    (re.compile(r"ISO[ _-]*14583.*[ _-]M4x10", re.I), "FAS_SCREW_M4X10_TORX_BH", ""),
]
SCREW_NOTE = ("Fusion models ISO 14583 hexalobular *pan*-head screws; the team BOM's screw lines say "
              "button head **UNVERIFIED**, and give no quantity")

# The BOM rows that are fasteners: counted per occurrence from transforms.csv, because a
# bearing of one size sits both loose in a joint and inside a purchased actuator.
FASTENER_PREFIX = "FAS_"

# Components never credited to an ancestor's row: they are inside a matched assembly in
# the model but are not part of that purchase.
NO_ANCESTOR_MATCH = [
    re.compile(r"^USB-C[ _-]*Cable$", re.I),      # inside `CAN_Isolated`; not part of the CANable row
]

# Why a component stays unmatched (regex on its own name; first hit wins).
UNMATCHED_NOTES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^150A[ _-]*relay", re.I), "no BOM row: the 150 A relay (power page: main disconnect gap)"),
    (re.compile(r"^(lumped[ _-]*wires|Small[ _-]*Wires|cables|8AWG)", re.I),
     "wiring harness lump; no single BOM row (see cables-connectors.csv and the wiring pages)"),
    (re.compile(r"^USB-C[ _-]*Cable$", re.I),
     "USB cable (Fusion material `USB C to A`), 12 modelled; the team BOM's only cable row is the "
     "Belkin 2-pack and does not say where it goes"),
    (re.compile(r"^(power[ _-]*block[ _-]*casing|casing|6x10-7holes)$", re.I),
     "casing/carrier of the power distribution block; the EL_DIST_BLOCK row counts the four blocks only"),
    (re.compile(r"^(schematics|.*cross_section|.*_face)", re.I), "sketch/section carrier; no manufacturing content"),
    (re.compile(r"bearing", re.I),
     "bearing of unstated size (Fusion name `bearing`, inside the purchased camera gimbal column); "
     "fasteners.csv lists bearings by size only, so no row can be tied to it"),
    (re.compile(r"^apriltag", re.I), "AprilTag fiducial / holder of the gripper; no BOM row"),
    (re.compile(r"^(gimbal_|U-joint|Component92)", re.I),
     "camera gimbal column part (`twincities_v2_nolock`); no BOM row"),
    (re.compile(r"^(custom_umi_gripper|rail|base|dovetail_umi_gripper|Component9)$", re.I),
     "gripper part designed for this robot; no row in printed-parts.csv or cnc-parts.csv"),
    (re.compile(r"^v15_right_end_effector_attachment", re.I),
     "wrist end-effector attachment (Nylon 12); no row in printed-parts.csv"),
    (re.compile(r"^ankle_top_cover", re.I), "cover under `protections` (Fusion material Steel); not in printed-parts.csv"),
]


def segments(path: str) -> list[str]:
    """Occurrence path -> component names, nearest ancestor first, self excluded."""
    names = [re.sub(r":\d+$", "", s) for s in path.split("+")]
    return list(reversed(names[:-1]))


def match(name: str) -> tuple[str, str] | None:
    m = ACTUATOR.search(name)
    if m and m.group(1) in ACTUATOR_IDS:
        return ACTUATOR_IDS[m.group(1)], ""
    for rx, pid, note in RULES:
        if rx.search(name):
            return pid, note
    return None


def match_row(r: dict) -> tuple[str, str, str]:
    """(part_id, via, note) for one tree row: own name first, then the ancestors
    nearest first, unless the component is one NO_ANCESTOR_MATCH names."""
    hit = match(r["fusion_name"])
    if hit:
        return hit[0], "", hit[1]
    if any(rx.search(r["fusion_name"]) for rx in NO_ANCESTOR_MATCH):
        return "", "", ""
    for anc in segments(r["path"]):
        hit = match(anc)
        if hit:
            return hit[0], anc, hit[1]
    return "", "", ""


def load_transforms(exp: Path) -> list[dict]:
    """<export>/transforms.csv rows (one per leaf occurrence: path, fusion_name, file_name), or []."""
    p = exp / "transforms.csv"
    if not p.is_file():
        return []
    with open(p, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def lumped_names(trows: list[dict]) -> dict[str, dict[str, int]]:
    """file_name -> {occurrence name: count} for every tree component whose occurrences
    carry more than one name (the export keeps one component per standard-part family)."""
    names: dict[str, dict[str, int]] = {}
    for r in trows:
        d = names.setdefault(r["file_name"], {})
        d[r["fusion_name"]] = d.get(r["fusion_name"], 0) + 1
    return {k: v for k, v in names.items() if len(v) > 1}


def fastener_occurrences(trows: list[dict]) -> dict[str, dict]:
    """Per FAS_* row: {"loose": n, "inside": {assembly part_id: n}} from transforms.csv.

    Walks each occurrence path from the root; the first segment whose name matches a
    FAS_* rule is the fastener occurrence (a `bearing_<size>` assembly, or the screw
    leaf itself under its own occurrence name), keyed by the path prefix so a bearing's
    two halves count once. It is `inside` when a nearer-to-root segment matches a
    purchased-assembly row (a bearing inside a RobStride)."""
    seen: dict[str, tuple[str, str]] = {}
    for r in trows:
        segs = r["path"].split("+")
        names = [re.sub(r":\d+$", "", s) for s in segs]
        names[-1] = r["fusion_name"]
        for i, n in enumerate(names):
            hit = match(n)
            if not hit or not hit[0].startswith(FASTENER_PREFIX):
                continue
            inside = ""
            for a in reversed(names[:i]):
                h = match(a)
                if h and not h[0].startswith(FASTENER_PREFIX):
                    inside = h[0]
                    break
            seen["+".join(segs[:i + 1])] = (hit[0], inside)
            break
    out: dict[str, dict] = {}
    for pid, inside in seen.values():
        d = out.setdefault(pid, {"loose": 0, "inside": {}})
        if inside:
            d["inside"][inside] = d["inside"].get(inside, 0) + 1
        else:
            d["loose"] += 1
    return out


def occurrence_note(pid: str, occ: dict[str, dict], row: dict) -> str:
    """`13 modelled per transforms.csv, all fitted loose` / `26 modelled ...: 22 fitted loose,
    4 inside ACT_RS06 (bought with it)`; a half-bearing row also says what its count is."""
    o = occ.get(pid)
    if not o:
        return ""
    total = o["loose"] + sum(o["inside"].values())
    if o["inside"]:
        parts = [f"{o['loose']} fitted loose"] + [f"{n} inside {a} (bought with it)"
                                                   for a, n in sorted(o["inside"].items())]
        text = f"{total} of this size modelled per transforms.csv: " + ", ".join(parts)
    else:
        text = f"{total} of this size modelled per transforms.csv, all fitted loose"
    if "half-bearing" in row["fusion_name"].lower():
        text += f"; each is two `half-bearing` components, so qty_in_model {row['qty']} = {int(row['qty']) // 2} bearings"
    return text


def size_token(name: str) -> str:
    m = re.search(r"\bM\d+(?:\.\d+)?x\d+\b", name)
    return m.group(0) if m else name


def lumped_note(counts: dict[str, int]) -> str:
    total = sum(counts.values())
    by_size: dict[str, int] = {}
    for n, c in counts.items():
        by_size[size_token(n)] = by_size.get(size_token(n), 0) + c
    breakdown = ", ".join(f"{s} {c}" for s, c in sorted(by_size.items(), key=lambda x: -x[1]))
    return (f"one tree.csv component for {total} occurrences of {len(counts)} different names in "
            f"transforms.csv ({breakdown}); no single BOM row can be tied to a lumped family, the "
            f"per-size counts are reported against the screw rows instead. {SCREW_NOTE}")


def unmatched_note(r: dict, top: str) -> str:
    n = base_name(r["file_name"])
    if FASTENER.search(r["fusion_name"]):
        return ("fastener with no team BOM row: the BOM's only fastener lines are three screw sizes "
                "(M3x10, M4x8, M4x10) and six bearing sizes")
    for rx, note in UNMATCHED_NOTES:
        if rx.search(n) or rx.search(r["fusion_name"]):
            return note
    if "protection" in r["material"].lower() or "+protections" in r["path"]:
        return "cover under `protections`; not in printed-parts.csv"
    if mass_of(r) < 3:
        return "no BOM row; under 3 g"
    return f"no BOM row; Fusion material `{r['material']}`, under `{top}`"


def load_bom() -> dict[str, dict]:
    bom = {}
    for f in BOM_FILES:
        p = DATA / f
        if not p.is_file():
            continue
        with open(p, encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                bom[row["part_id"].strip()] = row | {"bom_file": f}
    return bom


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    exp = Path(sys.argv[1])
    tree = load_tree(exp)
    _, owner = resolve_site_parts(tree)
    bom = load_bom()
    trows = load_transforms(exp)
    lumped = lumped_names(trows)
    occ = fastener_occurrences(trows)
    if not trows:
        print(f"WARNING no {exp / 'transforms.csv'}: fastener counts come from tree.csv, which lumps "
              "every size of a standard-part family under one component", file=sys.stderr)
    rows, vmap = [], {}
    per_bom: dict[str, dict] = {}
    for r in vendor_rows(tree, owner):
        pid, via, note = match_row(r)
        top = r["path"].split("+")[0].split(":")[0]
        if r["file_name"] in lumped:
            pid, note = "", lumped_note(lumped[r["file_name"]])
        b = bom.get(pid)
        if pid and b is None:
            print(f"WARNING rule points at {pid} which is in no BOM CSV ({r['file_name']})", file=sys.stderr)
            pid, note = "", ""
        if pid:
            note = "; ".join(x for x in (f"via `{via}`" if via else "", note, occurrence_note(pid, occ, r)) if x)
            rows.append(dict(file_name=r["file_name"], fusion_name=r["fusion_name"], qty_in_model=r["qty"],
                             part_id=pid, bom_file=b["bom_file"], description=b["description"], mpn=b["mpn"],
                             vendor=b["vendor"], vendor_url=b["vendor_url"], note=note))
            vmap[r["file_name"]] = {"part_id": pid, "bom_file": b["bom_file"], "description": b["description"],
                                    "qty_in_model": int(r["qty"]), "via": via}
            per_bom.setdefault(pid, {"components": 0})["components"] += 1
        else:
            rows.append(dict(file_name=r["file_name"], fusion_name=r["fusion_name"], qty_in_model=r["qty"],
                             part_id="", bom_file="", description="", mpn="", vendor="", vendor_url="",
                             note=note or unmatched_note(r, top)))

    # Modelled count of each matched assembly root: a component whose OWN name matches,
    # that is not empty (the `*_cross_section` sketches) and has no ancestor matching
    # the same BOM row (an actuator inside an actuator would count twice). FAS_* rows
    # come from transforms.csv instead (loose count; the inside count is printed after it).
    roots: dict[str, int] = {}
    for r in tree:
        hit = match(r["fusion_name"])
        if not hit or hit[0] not in per_bom or r["kind"] == "empty":
            continue
        if hit[0] in occ:
            continue
        if any((match(a) or ("",))[0] == hit[0] for a in segments(r["path"])):
            continue
        roots[hit[0]] = roots.get(hit[0], 0) + int(r["qty"])
    for pid, o in occ.items():
        if pid in bom:
            roots[pid] = o["loose"]
    listed = sorted(set(per_bom) | {p for p in occ if p in bom})

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows({k: englishise(v) if isinstance(v, str) else v for k, v in r.items()}
                    for r in rows)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(vmap, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    matched = [r for r in rows if r["part_id"]]
    print(f"{OUT_CSV.relative_to(SITE).as_posix()}: {len(rows)} vendor/other components with bodies, "
          f"{len(matched)} matched to {len(per_bom)} BOM rows, {len(rows) - len(matched)} unmatched")
    print(f"{OUT_JSON.relative_to(SITE).as_posix()}: {len(vmap)} entries")
    print("\nBOM row                  components  modelled  bom_qty   (FAS_* modelled = fitted loose, per transforms.csv)")
    for pid in listed:
        q = bom[pid]["qty_per_robot"]
        flag = "" if str(roots.get(pid, "")) == q else "   <- differs"
        inside = occ.get(pid, {}).get("inside", {})
        extra = "".join(f"   +{n} inside {a}" for a, n in sorted(inside.items()))
        print(f"  {pid:23} {per_bom.get(pid, {}).get('components', 0):>10}  {roots.get(pid, 0):>8}  {q:>7}{flag}{extra}")
    unmatched_bom = sorted(p for p in bom if p not in listed)
    print(f"\nBOM rows with no component in the model: {', '.join(unmatched_bom)}")
    big = [(r, mass_of(t)) for r in rows for t in tree
           if not r["part_id"] and t["file_name"] == r["file_name"] and mass_of(t) > REPORT_MIN_G]
    print(f"\nunmatched components over {REPORT_MIN_G:.0f} g ({len(big)}):")
    for r, m in sorted(big, key=lambda x: -x[1]):
        print(f"  {m:7.1f} g  x{r['qty_in_model']:<3} {r['file_name']:45} {r['note']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
