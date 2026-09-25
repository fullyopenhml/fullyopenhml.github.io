#!/usr/bin/env python3
"""Printable parts: turn every printed part of assets/data/robot.json into an STL.

Each printed part is the union of its primitive solids (as the viewer draws
them) minus the features the model recorded for it: bolt-hole patterns with
counterbores, dowel-pin clearances, bearing pockets, locating recesses and
box cuts.  Left-side parts are exported; the right side is the same STL
mirrored in the slicer (the manifest says which).

Run with the CSG environment:
    uv venv tools/.venv --python 3.12 && uv pip install --python tools/.venv/bin/python manifold3d trimesh numpy
    tools/.venv/bin/python tools/build_parts.py [--only PART_ID] [--no-zip]

Writes assets/print/<part_id>_v<ver>.stl, assets/print/foh_v<ver>_printable_parts.zip
and assets/data/print_files.json (file sizes, SHA-256, mesh volume, mass estimate,
bounding box, print notes) which the printing page reads.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import zipfile
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import Manifold, OpType

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "print"
robot = json.loads((ROOT / "assets/data/robot.json").read_text())
VER = robot["meta"]["version"].replace(".", "_")
SEG = 96          # circle segments for holes and cylinders

AXIS_ROT = {"z": None, "x": [0, 90, 0], "y": [-90, 0, 0]}   # rotate a z-cylinder onto the axis


def cylinder(axis, r, l, c, r_in=0.0, seg=SEG):
    """Solid or hollow cylinder centred at c along axis."""
    m = Manifold.cylinder(l, r, r, seg).translate([0, 0, -l / 2])
    if r_in > 0:
        m = m - Manifold.cylinder(l + 2, r_in, r_in, seg).translate([0, 0, -l / 2 - 1])
    if AXIS_ROT[axis]:
        m = m.rotate(AXIS_ROT[axis])
    return m.translate(list(c))


def rbox(size, c, rd=0.0):
    sx, sy, sz = size
    if rd and rd > 0.01:
        rd = min(rd, min(size) / 2 - 0.01)
        pts = []
        sph = Manifold.sphere(rd, 24)
        hx, hy, hz = sx / 2 - rd, sy / 2 - rd, sz / 2 - rd
        parts = [sph.translate([ix * hx, iy * hy, iz * hz]) for ix in (-1, 1) for iy in (-1, 1) for iz in (-1, 1)]
        m = Manifold.batch_hull(parts)
    else:
        m = Manifold.cube([sx, sy, sz], True)
    return m.translate(list(c))


def shape_solid(sh):
    if sh["t"] == "box":
        return rbox(sh["s"], sh["c"], sh.get("rd", 0))
    return cylinder(sh["axis"], sh["r"], sh["l"], sh["c"], sh.get("ri", 0))


def axis_vec(axis):
    return {"x": np.array([1.0, 0, 0]), "y": np.array([0, 1.0, 0]), "z": np.array([0, 0, 1.0])}[axis]


def perp_vecs(axis):
    return {"x": (np.array([0, 1.0, 0]), np.array([0, 0, 1.0])),
            "y": (np.array([0, 0, 1.0]), np.array([1.0, 0, 0])),
            "z": (np.array([1.0, 0, 0]), np.array([0, 1.0, 0]))}[axis]


def feature_solid(f):
    """Solid to subtract for one feature."""
    a = axis_vec(f["axis"]) if "axis" in f else None
    if f["t"] == "cut_box":
        return rbox([v + 0.0 for v in f["s"]], f["c"])
    c = np.array(f["c"], dtype=float)
    if f["t"] == "cut_cyl":
        t0, t1 = sorted((f["t0"], f["t1"]))
        mid = c + a * (t0 + t1) / 2
        return cylinder(f["axis"], f["d"] / 2, abs(t1 - t0) + 0.02, mid, seg=64)
    # hole pattern
    t0, t1 = sorted((f["t0"], f["t1"]))
    u, v = perp_vecs(f["axis"])
    r = f["pcd"] / 2
    solids = []
    for i in range(f["n"]):
        ang = math.radians(f.get("phase", 0) + 360.0 * i / f["n"])
        p = c + u * (r * math.cos(ang)) + v * (r * math.sin(ang))
        mid = p + a * (t0 + t1) / 2
        solids.append(cylinder(f["axis"], f["d"] / 2, abs(t1 - t0) + 0.02, mid, seg=32))
        if f.get("cbore"):
            cd, depth, side = f["cbore"]
            end = t1 if (side > 0) == (f["t1"] >= f["t0"]) else t0
            # counterbore sits at the `end` face and reaches `depth` into the part
            sgn = 1 if end == t1 else -1
            cmid = p + a * (end - sgn * depth / 2)
            solids.append(cylinder(f["axis"], cd / 2, depth + 0.02, cmid, seg=48))
    return Manifold.batch_boolean(solids, OpType.Add) if len(solids) > 1 else solids[0]


def build_part(pid):
    """Union of the first (left-side) occurrence's shapes minus its features."""
    occ = None
    for L in robot["links"]:
        for P in L["parts"]:
            if P["part"] == pid and (occ is None or not P["occ"].endswith("_R")):
                if occ is None or occ["occ"].endswith("_R"):
                    occ = P
    if occ is None:
        raise KeyError(pid)
    solids = [shape_solid(sh) for sh in occ["shapes"]]
    m = Manifold.batch_boolean(solids, OpType.Add) if len(solids) > 1 else solids[0]
    feats = [feature_solid(f) for f in occ.get("features", [])]
    if feats:
        cut = Manifold.batch_boolean(feats, OpType.Add) if len(feats) > 1 else feats[0]
        m = m - cut
    return occ, m


def to_trimesh(m):
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    f = np.asarray(mesh.tri_verts)
    return trimesh.Trimesh(vertices=v, faces=f, process=False)


ORIENTATION = {
    "3DP_kit03_coupler": "shoulder face down (hub up)",
    "3DP_kit06_coupler": "shoulder face down (hub up)",
    "3DP_kit02_coupler": "shoulder face down (hub up)",
    "3DP_kit05_adapter": "flat, output face down",
    "3DP_pel01_pelvis_shell": "upright as modelled; supports under the side mount rings",
    "3DP_leg02_hip_roll_bracket": "mount-ring face down",
    "3DP_leg04_hip_yaw_housing": "front plate down",
    "3DP_leg05_thigh_block": "plate down, cup up; supports inside the cup",
    "3DP_leg06_shank_outer_plate": "flat",
    "3DP_leg07_shank_inner_plate": "flat, bearing pocket up",
    "3DP_leg08_shank_cross": "flat",
    "3DP_leg10_ankle_bracket": "plate down; supports under the cup",
    "3DP_leg11_foot_bracket": "base flange down",
    "3DP_leg12_foot_plate": "flat",
    "3DP_leg13_sole": "flat, TPU",
    "3DP_tor02_bottom_plate": "flat",
    "3DP_tor03_top_plate": "flat",
    "3DP_tor04_shoulder_mount": "ring face down",
    "3DP_tor05_side_panel": "flat",
    "3DP_tor06_back_panel": "flat",
    "3DP_tor07_front_panel": "flat",
    "3DP_tor08_electronics_tray": "flat",
    "3DP_tor09_battery_cradle": "flat",
    "3DP_hea01_neck_post": "upright",
    "3DP_hea02_head_shell": "open side down",
    "3DP_arm02_shoulder_bracket": "plate down; supports under the cup",
    "3DP_arm04_upper_arm_yoke": "front plate down",
    "3DP_arm06_upper_arm": "plate down, cup up",
    "3DP_arm08_forearm_outer": "flat",
    "3DP_arm09_forearm_inner": "flat, bearing pocket up",
    "3DP_arm10_forearm_body": "wrist bore up",
    "3DP_grp01_gripper_body": "servo pocket up",
    "3DP_grp02_finger": "flat",
    "3DP_grp03_finger_pad": "flat, TPU",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--no-zip", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cat = robot["catalog"]
    mats = robot["materials"]
    manifest = {"version": robot["meta"]["version"], "units": "mm", "parts": []}
    pids = [p for p, c in cat.items() if c["category"] == "printed" and (not args.only or p == args.only)]
    files = []
    for pid in pids:
        c = cat[pid]
        occ, m = build_part(pid)
        tm = to_trimesh(m)
        if not tm.is_watertight:
            print(f"  WARNING {pid}: mesh not watertight")
        fname = f"{pid}_v{VER}.stl"
        path = OUT / fname
        tm.export(path, file_type="stl")
        data = path.read_bytes()
        mat = mats[c["material"]]
        vol = float(tm.volume) / 1000.0
        bb = tm.bounds
        entry = dict(
            id=pid, name=c["name"], file=f"assets/print/{fname}", bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
            material=c["material"], material_name=mat["name"], qty=c["qty"], mirror=bool(c.get("mirror")),
            optional=c.get("optional"), volume_cm3=round(vol, 1), mass_g_solid=round(vol * mat["density"]),
            mass_g_est=round(vol * mat["density"] * mat["fill"]), bbox_mm=[round(float(v), 1) for v in (bb[1] - bb[0])],
            faces=int(len(tm.faces)), features=len(occ.get("features", [])), orientation=ORIENTATION.get(pid, ""),
            source_occurrence=occ["occ"],
        )
        manifest["parts"].append(entry)
        files.append(path)
        print(f"  {pid:34s} {vol:8.1f} cm3  {entry['mass_g_est']:5d} g  {entry['bbox_mm']}  {entry['faces']} faces  {'MIRROR' if entry['mirror'] else ''}")
    (ROOT / "assets/data/print_files.json").write_text(json.dumps(manifest, indent=1) + "\n")
    if not args.no_zip and not args.only:
        zpath = OUT / f"foh_v{VER}_printable_parts.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for f in files:
                z.write(f, f.name)
            z.writestr("README.txt", "Fully Open Humanoid printable parts. Left-side files; mirror the parts marked mirror in print_files.json for the right side. Units mm. Generated by tools/build_parts.py.\n")
        manifest["zip"] = dict(file=f"assets/print/{zpath.name}", bytes=zpath.stat().st_size, sha256=hashlib.sha256(zpath.read_bytes()).hexdigest())
        (ROOT / "assets/data/print_files.json").write_text(json.dumps(manifest, indent=1) + "\n")
        print(f"zip: {zpath} ({zpath.stat().st_size/1e6:.1f} MB)")
    print(f"{len(files)} parts written to {OUT}")


if __name__ == "__main__":
    main()
