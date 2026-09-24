"""Mass properties of every downloadable part -> docs/data/part-properties.csv,
and the robot's joints -> docs/data/joints.csv.

    python tools/gen_part_properties.py ../cad/<export>

Every value is Fusion's own, read from ``<export>/tree.csv`` (written by
tools/fusion_export/ from ``Component.physicalProperties``); nothing is
measured and nothing but the volume is derived from a mesh.

Sources
-------
* ``mass_g``, ``bbox_*_mm``, ``material`` — Fusion: the component's mass with
  the material assigned in CAD, and its axis-aligned bounding box in its own
  coordinates.
* ``com_*_mm`` — Fusion ``physicalProperties.centerOfMass``, in the component
  frame (the frame of the STEP and STL downloads), mm.
* ``ixx``..``iyz`` — Fusion ``physicalProperties.getXYZMomentsOfInertia()``,
  which returns the inertia tensor **about the component-frame origin**, not
  about the centre of mass, with tensor-form products (``ixy`` = −∫ x y dm).
  Checked numerically against trimesh on the export's own STLs: the six
  Fusion numbers match the STL tensor shifted to the origin, on four parts, to
  within the mesh error. This script shifts them to the centre of mass with
  the parallel-axis theorem (I_com = I_o − m (|d|² E − d dᵀ), d = the Fusion
  centre of mass) so the published values are what a URDF/MJCF ``<inertial>``
  takes. tree.csv rounds the mass to 0.1 g, so a shift over a long |d| loses
  precision: the row's ``notes`` gives the bound (±0.05 g · |d|²) when it
  exceeds 2 % of the largest moment, and the inertia is left blank when the
  shift exceeds the exported precision altogether.
* ``ixx_origin``..``iyz_origin`` — the same six Fusion numbers unchanged
  (about the component-frame origin, g·mm²), so the exact export is on record
  and a reader with the unrounded mass can redo the shift.
* ``volume_cm3`` — the only mesh-derived column: the volume of the closed
  STL in ``<export>/print/`` (mm³ / 1000). Blank while the export has not
  written that STL yet, or when the mesh is not closed.

Units in the CSV: g, cm³, mm, g·mm².

A part is still listed when a value cannot be given; the column is blank and
``notes`` says why:

* the Fusion component carries child components (inserts, magnets, mounted
  electronics): its CAD mass, bounding box, centre of mass and inertia include
  them, so ``mass_g`` and the inertia are blank; size, volume and centre of
  mass come from the STL of the component's own bodies when it is closed;
* the STL is not closed: no volume;
* the STL bounding box differs from Fusion's for a leaf part: the conflict is
  recorded (the site marks it);
* a part exists twice in Fusion (the left and right arm and leg designs are
  separate linked designs): the copies are compared and a difference in mass,
  size or centre of mass is recorded.

Rows are matched to site part IDs the way ``stage_cad_export.py`` matches
files; the printed parts use ``gen_printed.PRINTED`` with its scopes
(``Component42|leg`` is the shank cover, ``Component42`` the shoulder cover).

Joints
------
When ``<export>/joints.csv`` was written by tools/fusion_export_modules/ (it
has a ``component`` column: one row per joint of every component, origin and
axis in that component's frame), it is copied to ``docs/data/joints.csv``
with the limits and current value converted to degrees for revolute joints
(``min_deg``, ``max_deg``, ``value_deg``; slider limits stay in mm as
``min_mm``, ``max_mm``, ``value_mm``). The reference page renders the
revolute joints from it. Without that file nothing is written and the page
shows its MISSING box.
"""

from __future__ import annotations

import csv
import math
import re
import sys
from pathlib import Path

import numpy as np
import trimesh

SITE = Path(__file__).resolve().parent.parent
OUT = SITE / "docs" / "data" / "part-properties.csv"
OUT_JOINTS = SITE / "docs" / "data" / "joints.csv"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage_cad_export import ALIASES, englishise, strip_qty, site_ids  # noqa: E402
from gen_printed import PRINTED, load_tree, pick  # noqa: E402

COLS = ["part_id", "fusion_name", "material", "mass_g", "volume_cm3", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm",
        "com_x_mm", "com_y_mm", "com_z_mm", "ixx", "iyy", "izz", "ixy", "ixz", "iyz",
        "ixx_origin", "iyy_origin", "izz_origin", "ixy_origin", "ixz_origin", "iyz_origin", "notes"]
PRINTED_KEYS = {pid: key for key, pid, _, _ in PRINTED}   # part_id -> "Component42|leg" etc.
JOINT_COLS = ["component", "component_path", "joint", "kind", "type", "occurrence_one", "occurrence_two",
              "origin_x_mm", "origin_y_mm", "origin_z_mm", "axis_x", "axis_y", "axis_z",
              "min", "max", "value", "units", "min_deg", "max_deg", "value_deg", "min_mm", "max_mm", "value_mm",
              "is_suppressed", "note"]

# STL-vs-Fusion bounding-box agreement for one and the same component is within
# the tessellation error (< 1.1 mm over 300 exported components); anything
# beyond this is a hidden body or construction geometry in the CAD.
BBOX_TOL_MM = 1.5
BBOX_TOL_REL = 0.01
MASS_ROUNDING_G = 0.05        # tree.csv carries the mass to 0.1 g
UNC_REPORT_FRACTION = 0.02    # note the bound when it exceeds this fraction of the largest moment


def rnd(value: float, digits: int) -> float:
    r = round(float(value), digits)
    return 0.0 if r == 0 else r          # no "-0.0" in the CSV


def fmt_bbox(v) -> str:
    return " × ".join(f"{float(x):g}" for x in v) + " mm"


def resolve(pid: str, by_name: dict[str, list[dict]]) -> list[dict]:
    """Tree rows for one site part ID (every Fusion copy), leaf parts first."""
    if pid in PRINTED_KEYS:
        rows = pick(by_name, PRINTED_KEYS[pid])
    else:
        key = ALIASES.get(pid, pid)
        rows = by_name.get(key) or by_name.get(strip_qty(key)) or []
        if not rows:
            # CNC names carry the `_x<qty>` token in Fusion: match on the stripped name.
            rows = [r for name, rs in by_name.items() if strip_qty(name) == strip_qty(key) for r in rs]
    return sorted(rows, key=lambda r: (r["kind"] != "part", r["file_name"]))


def tree_vec(t: dict, keys: tuple[str, ...]) -> np.ndarray | None:
    try:
        return np.array([float(t[k]) for k in keys])
    except ValueError:
        return None


def bbox_matches(ext: np.ndarray, bb: np.ndarray | None) -> bool:
    if bb is None:
        return False
    return float(np.abs(ext - bb).max()) <= max(BBOX_TOL_MM, BBOX_TOL_REL * float(bb.max()))


def inertia_about_com(t: dict) -> tuple[np.ndarray | None, float, str]:
    """Fusion's tensor about the component origin, shifted to the centre of mass.

    Returns (3x3 tensor in g·mm² or None, precision bound in g·mm², note)."""
    try:
        m = float(t["mass_g"])
        d = np.array([float(t["com_x_mm"]), float(t["com_y_mm"]), float(t["com_z_mm"])])
        xx, yy, zz, xy, yz, xz = (float(t[k]) for k in ("ixx", "iyy", "izz", "ixy", "iyz", "ixz"))
    except ValueError:
        return None, 0.0, "no inertia in the Fusion export"
    if m <= 0:
        return None, 0.0, "no mass in CAD: inertia not given"
    I_o = np.array([[xx, xy, xz], [xy, yy, yz], [xz, yz, zz]])
    d2 = float(d @ d)
    I_c = I_o - m * (d2 * np.eye(3) - np.outer(d, d))
    bound = MASS_ROUNDING_G * d2
    diag = np.diag(I_c)
    # A real tensor has positive moments with Ixx + Iyy >= Izz (and cyclic); a
    # violation beyond the rounding bound means the shift from the origin is
    # larger than the 0.1 g mass resolution of the export can support.
    if (diag <= 0).any() or 2 * diag.max() - diag.sum() > 3 * bound + 1:
        return None, bound, (f"inertia about the centre of mass not given: the centre of mass is {math.sqrt(d2):.0f} mm "
                             f"from the component origin and Fusion's origin-referenced tensor, shifted with a mass "
                             f"rounded to 0.1 g, is uncertain by ±{bound:.0f} g·mm², more than the part's own moments "
                             f"(the `*_origin` columns hold Fusion's values unchanged)")
    note = ""
    if bound > UNC_REPORT_FRACTION * float(diag.max()):
        note = (f"inertia about the centre of mass carries up to ±{bound:.0f} g·mm² from the 0.1 g mass "
                f"rounding in the export (centre of mass {math.sqrt(d2):.0f} mm from the component origin)")
    return I_c, bound, note


def copies_differ(rows: list[dict]) -> str:
    """Where the Fusion copies of one part disagree (left/right designs)."""
    fields = {"mass": ("mass_g",), "size": ("bbox_x_mm", "bbox_y_mm", "bbox_z_mm"),
              "centre of mass": ("com_x_mm", "com_y_mm", "com_z_mm")}
    diffs = []
    for label, keys in fields.items():
        values = {tuple(r[k] for k in keys) for r in rows}
        if len(values) > 1:
            shown = "; ".join(f"`{r['file_name']}` " + " × ".join(r[k] for k in keys) for r in rows)
            diffs.append(f"{label} ({shown})")
    return ", ".join(diffs)


def load_stl(path: Path) -> tuple[trimesh.Trimesh | None, int]:
    if not path.is_file():
        return None, 0
    m = trimesh.load(path, force="mesh")
    m.merge_vertices()
    return m, len(m.split(only_watertight=False))


def write_joints(exp: Path) -> str:
    src = exp / "joints.csv"
    if not src.is_file():
        return "no joints.csv in the export"
    with open(src, encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        header = rd.fieldnames or []
        rows = list(rd)
    if "component" not in header:
        return "joints.csv is the root-only file of fusion_export (no `component` column): run fusion_export_modules"
    if not rows:
        return "joints.csv from fusion_export_modules holds no joints"
    out = []
    for r in rows:
        o = dict.fromkeys(JOINT_COLS, "")
        o.update({k: r.get(k, "") for k in JOINT_COLS if k in r})
        units = r.get("units", "")
        for src_k, deg_k, mm_k in (("min", "min_deg", "min_mm"), ("max", "max_deg", "max_mm"),
                                   ("value", "value_deg", "value_mm")):
            v = r.get(src_k, "")
            if v == "":
                continue
            try:
                x = float(v)
            except ValueError:
                continue
            if units == "rad":
                o[deg_k] = rnd(math.degrees(x), 2)
            elif units == "cm":
                o[mm_k] = rnd(x * 10, 3)
        out.append(o)
    with open(OUT_JOINTS, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=JOINT_COLS, lineterminator="\n")
        w.writeheader()
        w.writerows({k: englishise(v) if isinstance(v, str) else v for k, v in o.items()}
                    for o in out)
    n_rev = sum(1 for o in out if o["type"] == "revolute" and o["is_suppressed"] != "True")
    return (f"{OUT_JOINTS.relative_to(SITE).as_posix()}: {len(out)} joints from "
            f"{len({o['component'] for o in out})} components, {n_rev} revolute and not suppressed")


def main() -> int:
    exp = Path(sys.argv[1])
    by_name = load_tree(exp / "tree.csv")
    rows, skipped = [], []
    for pid in site_ids():
        cands = resolve(pid, by_name)
        if not cands:
            skipped.append(pid)
            continue
        t = cands[0]
        name, children = re.sub(r" \(\d+\)$", "", t["fusion_name"]), int(t["children"])
        copies = [r for r in cands if int(r["children"]) == children]
        row = dict.fromkeys(COLS, "")
        row.update(part_id=pid, fusion_name=name, material=t["material"])
        notes = []
        bb = tree_vec(t, ("bbox_x_mm", "bbox_y_mm", "bbox_z_mm"))
        if len(copies) > 1:
            d = copies_differ(copies)
            if d:
                notes.append(f"the {len(copies)} Fusion copies of this part differ in {d}: values are of `{t['file_name']}`")

        stl = exp / "print" / (t["file_name"] + ".stl")
        m, shells = load_stl(stl)
        if m is not None:
            ext = m.bounding_box.extents
        else:
            notes.append(f"no STL `print/{stl.name}` in the export (yet): volume not computed")

        if children:
            # A component with child components: Fusion's mass properties are
            # of the whole subtree, so none of them is the part's own.
            notes.append(f"Fusion component `{name}` carries {children} child component(s): its CAD mass "
                         f"({t['mass_g']} g), bounding box ({fmt_bbox(bb) if bb is not None else '?'}), centre "
                         f"of mass and inertia include them, so no own mass or inertia is in this export")
            if m is not None and shells == int(t["bodies"]) and m.is_watertight and m.volume > 0:
                com = m.center_mass
                row.update(bbox_x_mm=rnd(ext[0], 1), bbox_y_mm=rnd(ext[1], 1), bbox_z_mm=rnd(ext[2], 1),
                           volume_cm3=rnd(m.volume / 1000, 2),
                           com_x_mm=rnd(com[0], 2), com_y_mm=rnd(com[1], 2), com_z_mm=rnd(com[2], 2))
                notes.append("size, volume and centre of mass are of the component's own body, from the STL")
            elif m is not None:
                notes.append(f"the STL holds {shells} shell(s) for {t['bodies']} own body/bodies, or is not closed: not used")
            row["notes"] = "; ".join(notes)
            rows.append(row)
            continue

        # Leaf part: every Fusion value is the part's own.
        row.update(mass_g=t["mass_g"], bbox_x_mm=t["bbox_x_mm"], bbox_y_mm=t["bbox_y_mm"], bbox_z_mm=t["bbox_z_mm"])
        com = tree_vec(t, ("com_x_mm", "com_y_mm", "com_z_mm"))
        if com is not None:
            row.update(com_x_mm=rnd(com[0], 3), com_y_mm=rnd(com[1], 3), com_z_mm=rnd(com[2], 3))
        else:
            notes.append("no centre of mass in the Fusion export")
        I, _, inote = inertia_about_com(t)
        if I is not None:
            row.update(ixx=rnd(I[0, 0], 1), iyy=rnd(I[1, 1], 1), izz=rnd(I[2, 2], 1),
                       ixy=rnd(I[0, 1], 1), ixz=rnd(I[0, 2], 1), iyz=rnd(I[1, 2], 1))
        if inote:
            notes.append(inote)
        # Fusion's own numbers, unchanged: the tensor about the component-frame origin.
        row.update(ixx_origin=t["ixx"], iyy_origin=t["iyy"], izz_origin=t["izz"],
                   ixy_origin=t["ixy"], ixz_origin=t["ixz"], iyz_origin=t["iyz"])
        if m is not None:
            if not bbox_matches(ext, bb):
                notes.append(f"STL bounding box {fmt_bbox(ext.round(1))} differs from the Fusion bounding box "
                             f"{fmt_bbox(bb) if bb is not None else '?'}: check the component for a hidden body")
            if m.is_watertight and m.volume > 0:
                row["volume_cm3"] = rnd(m.volume / 1000, 2)
            else:
                notes.append(f"mesh not closed ({shells} shells): volume not computed")
        row["notes"] = "; ".join(notes)
        rows.append(row)

    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["part_id"]))
    n_mass = sum(1 for r in rows if r["mass_g"] != "")
    n_in = sum(1 for r in rows if r["ixx"] != "")
    n_vol = sum(1 for r in rows if r["volume_cm3"] != "")
    print(f"{OUT.relative_to(SITE).as_posix()}: {len(rows)} parts, mass for {n_mass}, inertia for {n_in}, "
          f"volume for {n_vol}")
    for r in rows:
        if r["notes"]:
            print(f"  {r['part_id']}: {r['notes']}")
    if skipped:
        print(f"{len(skipped)} site part IDs not in the Fusion tree (no row): {', '.join(skipped)}")
    print(write_joints(exp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
