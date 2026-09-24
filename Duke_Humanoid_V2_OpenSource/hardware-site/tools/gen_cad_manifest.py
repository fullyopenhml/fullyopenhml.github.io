"""Index the downloadable CAD files under docs/files/ and guard GitHub's size limits.

Put files here, named after the part IDs in docs/data/*.csv:

    docs/files/step/<part_id>_rev<NN>.step       one STEP per part (machined and printed)
    docs/files/print/<part_id>_rev<NN>.3mf       printable mesh per printed part (.stl also accepted)
    docs/files/drawings/<part_id>_rev<NN>.pdf    drawing per machined part
    docs/files/plates/<name>.3mf                 slicer projects, ready to print
    docs/files/assembly/<name>.(step|f3z)        whole-robot STEP and the native Fusion 360 archive
    docs/files/assembly/<name>.step.zip          the whole-robot STEP zipped when it is over 95 MB
    docs/files/modules/<module_id>_rev<NN>.step  one STEP per sub-assembly (docs/data/modules.csv),
                                                 `.step.zip` when it is over 95 MB
    docs/files/vendor/<file_name>.step           one STEP per vendor component (docs/data/vendor-parts.csv),
                                                 `.step.zip` when it is over 95 MB

`_rev<NN>` is optional. Writes docs/data/cad-files.csv (read by the cad_* macros, which
put a download link next to every part; `part_id` is the module_id for a module file
and the export file name for a vendor file) and docs/files/SHA256SUMS.txt.

Fails (exit 1) if any file exceeds 95 MB (GitHub rejects files over 100 MB) or the total
exceeds 900 MB (a GitHub Pages site may not exceed 1 GB).

Usage:  python tools/gen_cad_manifest.py
"""

from __future__ import annotations

import csv
import hashlib
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
FILES = SITE / "docs" / "files"
OUT = SITE / "docs" / "data" / "cad-files.csv"
SUMS = FILES / "SHA256SUMS.txt"

KINDS = {
    "step": {".step", ".stp"},
    "print": {".3mf", ".stl"},
    "drawings": {".pdf"},
    "plates": {".3mf"},
    "assembly": {".step", ".stp", ".f3z", ".f3d", ".zip"},   # .zip: a whole-robot STEP over 95 MB, zipped
    "modules": {".step", ".stp", ".zip"},                     # .zip: a module STEP over 95 MB, zipped
    "vendor": {".step", ".stp", ".zip"},                      # .zip: a vendor STEP over 95 MB, zipped
}

# Files at the top of docs/files/ that ship with the design but are not
# categorised CAD: LICENCE, NOTICE, release notes.
TOP_LEVEL = {"LICENSE", "NOTICE", "RELEASE_NOTES"}
MAX_FILE = 95 * 1024 * 1024
MAX_TOTAL = 900 * 1024 * 1024
NAME = re.compile(r"^(?P<part>.+?)(?:_rev(?P<rev>\d+))?$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    rows, errors, total = [], [], 0
    for kind, exts in KINDS.items():
        folder = FILES / kind
        for path in sorted(folder.glob("*"), key=lambda p: p.name.lower()) if folder.is_dir() else []:
            if path.name.startswith(".") or not path.is_file():
                continue
            if path.suffix.lower() not in exts:
                errors.append(f"{path.relative_to(SITE).as_posix()}: {path.suffix} does not belong in files/{kind}/")
                continue
            size = path.stat().st_size
            total += size
            if size > MAX_FILE:
                errors.append(f"{path.relative_to(SITE).as_posix()}: {size / 2**20:.1f} MB is over the 95 MB limit — zip or split it")
            zipped = path.suffix.lower() == ".zip" and path.stem.lower().endswith(".step")
            stem = path.stem[:-5] if zipped else path.stem      # a Fusion name may itself end in .STEP
            m = NAME.match(stem)
            rows.append({
                "part_id": m.group("part"),
                "rev": m.group("rev") or "",
                "kind": kind,
                "format": ("STEP (zip)" if zipped
                           else path.suffix.lower().lstrip(".").upper()),
                "path": f"files/{kind}/{path.name}",
                "bytes": size,
                "sha256": sha256(path),
            })

    for path in sorted(FILES.glob("*"), key=lambda p: p.name.lower()):
        if not path.is_file() or path.name.startswith(".") or path.name not in TOP_LEVEL:
            continue
        rows.append({
            "part_id": path.stem,
            "rev": "",
            "kind": "release",
            "format": "TEXT",
            "path": f"files/{path.name}",
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })

    if total > MAX_TOTAL:
        errors.append(f"total {total / 2**20:.0f} MB is over the 900 MB budget for a GitHub Pages site")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["part_id", "rev", "kind", "format", "path", "bytes", "sha256"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    SUMS.write_text("".join(f"{r['sha256']}  {r['path'][len('files/'):]}\n" for r in rows),
                    encoding="utf-8", newline="\n")
    n_release = sum(1 for r in rows if r["kind"] == "release")

    print(f"{OUT.relative_to(SITE).as_posix()}: {len(rows)} files, {total / 2**20:.1f} MB"
          + (f", {n_release} release artefact(s)" if n_release else ""))
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
