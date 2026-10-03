#!/usr/bin/env python3
"""Berkeley Humanoid Lite's printed parts, cut from its published link meshes for the extended build (v2).

BHL publishes one STL per link (Hybrid Robotics, berkeley-humanoid-lite-assets, CC BY-SA 4.0): each file is the
whole link, printed bracket and cycloidal actuator module together, decimated. This tool takes the pieces the
extended design keeps, removes the actuator modules (a Ø88 x 65 cylinder for the 6512, Ø70 x 65 for the 5010,
measured from the meshes) and the bracket rings that held them, cuts the long arms where a carbon tube takes
over, straightens the arm links out of BHL's 15 deg zero-pose abduction, and writes:

    assets/geom/v2/<piece>_L.glb, <piece>_R.glb   (mm, vertices relative to the piece's reference joint)
    assets/data/bhl_pieces.json                     (per piece: reference joint, bbox, surface samples, convex
                                                     hull planes, mass estimate, plate section at the cut, and
                                                     the ring that was removed)

tools/build_v2.py places the pieces on the extended skeleton. Run with the venv:
    tools/.venv/bin/python tools/bhl_pieces.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_geometry as bg      # noqa: E402  (URDF loader with its download cache)

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets/geom/v2"
OUT_JSON = ROOT / "assets/data/bhl_pieces.json"
BASE = "https://raw.githubusercontent.com/HybridRobotics/berkeley-humanoid-lite-assets/main/data/robots/berkeley_humanoid/berkeley_humanoid_lite"
FACES = 7000                    # face budget per piece GLB
MODULE = {"6512": dict(r=44.0, l=65.0, mass_g=500), "5010": dict(r=35.0, l=65.0, mass_g=300)}   # measured Ø and length; mass from BHL's link masses
# Our joint kit replaces BHL's cradle ring: the RobStride's child face sits on BHL's output plane (ax = 0), its lug face
# mount_t + 2 behind it, the printed mount ring between. BHL faces inside that ring's envelope are removed; the rest of
# BHL's cradle (the saddle or sleeve around the body) stays as the collar.  ring_r: our ring radius; t: axial band.
RING_CUT = {"6512": dict(r=50.0 + 1.0, t0=-12.0, t1=24.0), "5010": dict(r=41.0 + 1.0, t0=-12.0, t1=16.0)}   # RS06 ring r 50, mount_t 20; RS02 ring r 41, mount_t 12
N_SAMPLES = 320

u = bg.Urdf(BASE + "/urdf/berkeley_humanoid_lite.urdf", BASE + "/meshes", "bhl")
LINK_MASS = {l: float(u.links[l].find("inertial/mass").get("value")) * 1000 for l in u.links}


def world_mesh(link):
    return trimesh.util.concatenate(u.link_meshes(link)).apply_scale(1000.0)   # mm, BHL world frame, zero pose


def joint_world(jn):
    return np.array(u.joint_pos[jn]) * 1000.0


def joint_axis_world(jn):
    j = u.joints[jn]
    parent = j.find("parent").get("link")
    a = np.array([float(v) for v in j.find("axis").get("xyz").split()])
    return u.T[parent][:3, :3] @ bg.origin_T(j.find("origin"))[:3, :3] @ a


# --------------------------------------------------------------------------- straighten the left arm
# BHL's zero pose holds the arms 15 deg abducted. Rotate everything below the shoulder-roll joint about that joint's
# axis (world x) so the shoulder-yaw joint hangs straight under the roll joint.
ROLL = joint_world("arm_left_shoulder_roll_joint")
YAW = joint_world("arm_left_shoulder_yaw_joint")
v = YAW - ROLL
ang = math.atan2(v[1], -v[2])          # positive = abducted outboard (+y) for the left arm
STRAIGHTEN = trimesh.transformations.rotation_matrix(-ang, [1, 0, 0], ROLL)
ARM_LINKS = ("arm_left_shoulder_roll", "arm_left_shoulder_yaw", "arm_left_elbow_pitch", "arm_left_elbow_roll", "arm_left_hand_link")


def straight(p):
    return (STRAIGHTEN @ np.append(p, 1.0))[:3]


def link_mesh(link):
    m = world_mesh(link)
    if link in ARM_LINKS:
        m.apply_transform(STRAIGHTEN)
    return m


# straightened joint positions (mm, world)
P = {}
for jn in u.joints:
    p = joint_world(jn)
    P[jn] = straight(p) if u.joints[jn].find("child").get("link") in ARM_LINKS else p    # the roll joint lies on the axis: unchanged
print(f"arm straightened by {math.degrees(ang):.1f} deg; yaw joint now at {np.round(P['arm_left_shoulder_yaw_joint'], 1).tolist()} under the roll joint {np.round(ROLL, 1).tolist()}")


def axis_straight(jn):
    a = joint_axis_world(jn)
    return STRAIGHTEN[:3, :3] @ a if u.joints[jn].find("child").get("link") in ARM_LINKS else a


# --------------------------------------------------------------------------- piece definitions (left side)
# module: (joint whose actuator this is, module class, direction of the body along the joint axis (+1 = along the axis
# vector, -1 against), host link). keep: list of (normal, point) half-spaces to keep. cut_at: the plate section plane.
K = P["leg_left_knee_pitch_joint"]; A = P["leg_left_ankle_pitch_joint"]; RJ = P["leg_left_ankle_roll_joint"]
SP = P["arm_left_shoulder_pitch_joint"]; SR = ROLL; SY = P["arm_left_shoulder_yaw_joint"]; EL = P["arm_left_elbow_pitch_joint"]; WR = P["arm_left_elbow_roll_joint"]
Z, Y, X = np.array([0, 0, 1.0]), np.array([0, 1.0, 0]), np.array([1.0, 0, 0])
PIECES = {
    "knee_cradle":  dict(link="leg_left_hip_pitch", ref="leg_left_knee_pitch_joint", keep=[(-Z, K + Z * 60)], cut=("z", K[2] + 60, -Z),
                         bore=50.5, ring_cut=dict(r=57.0, t0=-12.0, t1=26.0),   # RS03: body r 49 in a Ø101 bore, ring r 56 in the mouth
                         modules=[("leg_left_knee_pitch_joint", "6512")], ring_of="leg_left_knee_pitch_joint",
                         name="Thigh, lower part (knee cradle)", bhl="leg_hip_pitch link: the lower 60 mm of the thigh arm and the knee ring"),
    "shank_upper":  dict(link="leg_left_knee_pitch", ref="leg_left_knee_pitch_joint", keep=[(Z, K - Z * 60)], cut=("z", K[2] - 60, Z),
                         modules=[], name="Shank, upper part (knee boss)", bhl="leg_knee_pitch link: the knee output boss and the upper 60 mm of the shank arm"),
    "ankle_cradle": dict(link="leg_left_knee_pitch", ref="leg_left_ankle_pitch_joint", keep=[(-Z, A + Z * 60)], cut=("z", A[2] + 60, -Z),
                         modules=[("leg_left_ankle_pitch_joint", "5010")], ring_of="leg_left_ankle_pitch_joint",
                         name="Shank, lower part (ankle cradle)", bhl="leg_knee_pitch link: the lower 60 mm of the shank arm and the ankle-pitch ring"),
    "ankle_bracket": dict(link="leg_left_ankle_pitch", ref="leg_left_ankle_pitch_joint", keep=[], modules=[],
                          name="Ankle bracket", bhl="leg_ankle_pitch link, whole"),
    "foot":         dict(link="leg_left_ankle_roll", ref="leg_left_ankle_roll_joint", keep=[], modules=[("leg_left_ankle_roll_joint", "5010")], modified="cradle raised 15 mm: the RS02 cup needs 45 mm under the roll axis where the 5010 saddle gave 11", ring_of="leg_left_ankle_roll_joint", floor=RJ[2] - 33, shift=[0, 0, -15.0],
                         name="Foot (plate, shoe and ankle-roll cradle)", bhl="leg_ankle_roll link, whole, minus the 5010 module"),
    "shoulder_bracket": dict(link="arm_left_shoulder_pitch", ref="arm_left_shoulder_pitch_joint", keep=[], modules=[("arm_left_shoulder_roll_joint", "5010")], ring_of="arm_left_shoulder_roll_joint",
                             name="Shoulder bracket (pitch output to roll cradle)", bhl="arm_shoulder_pitch link, whole, minus the 5010 module"),
    # BHL's upper arm: roll output boss, a plate 50 mm down, then a flange that holds the yaw module by its rear face
    "upper_arm_upper": dict(link="arm_left_shoulder_roll", ref="arm_left_shoulder_roll_joint", keep=[(Z, SR - Z * 44)], cut=("z", SR[2] - 44, Z),
                            modules=[], name="Upper arm, upper part (roll boss)", bhl="arm_shoulder_roll link: the roll output boss and the arm plate, cut 44 mm below the roll axis"),
    "upper_arm_lower": dict(link="arm_left_shoulder_roll", ref="arm_left_shoulder_yaw_joint", keep=[(-Z, SR - Z * 48)], cut=("z", SR[2] - 48, -Z),
                            modules=[("arm_left_shoulder_yaw_joint", "5010")], ring_of="arm_left_shoulder_yaw_joint",
                            name="Upper arm, lower part (yaw flange)", bhl="arm_shoulder_roll link: the flange that carried the shoulder-yaw module"),
    "elbow_bracket": dict(link="arm_left_shoulder_yaw", ref="arm_left_shoulder_yaw_joint", keep=[], modules=[("arm_left_elbow_pitch_joint", "5010")], ring_of="arm_left_elbow_pitch_joint",
                          name="Elbow bracket (yaw output to elbow cradle)", bhl="arm_shoulder_yaw link, whole, minus the 5010 module"),
    "forearm_upper": dict(link="arm_left_elbow_pitch", ref="arm_left_elbow_pitch_joint", keep=[(Z, EL - Z * 44)], cut=("z", EL[2] - 44, Z),
                          modules=[], name="Forearm, upper part (elbow boss)", bhl="arm_elbow_pitch link: the elbow output boss and the arm plate, cut 44 mm below the elbow axis"),
    "forearm_lower": dict(link="arm_left_elbow_pitch", ref="arm_left_elbow_roll_joint", keep=[(-Z, EL - Z * 48)], cut=("z", EL[2] - 48, -Z),
                          modules=[("arm_left_elbow_roll_joint", "5010")], ring_of="arm_left_elbow_roll_joint",
                          name="Forearm, lower part (wrist flange)", bhl="arm_elbow_pitch link: the flange that carried the wrist module"),
}
# which link hosts which modules (for the bracket mass: link mass minus its modules)
HOSTED = {"leg_left_hip_pitch": ["6512"], "leg_left_knee_pitch": ["5010"], "leg_left_ankle_pitch": [], "leg_left_ankle_roll": ["5010"],
          "arm_left_shoulder_pitch": ["5010"], "arm_left_shoulder_roll": ["5010"], "arm_left_shoulder_yaw": ["5010"], "arm_left_elbow_pitch": ["5010"]}
# body direction along the joint axis vector for each module (from the measured axial ranges: + = 0..65, - = -65..0)
BODY_DIR = {"leg_left_knee_pitch_joint": +1, "leg_left_ankle_pitch_joint": +1, "leg_left_ankle_roll_joint": +1,
            "arm_left_shoulder_roll_joint": -1, "arm_left_shoulder_yaw_joint": -1, "arm_left_elbow_pitch_joint": -1, "arm_left_elbow_roll_joint": -1}


def module_cyl(jn, cls):
    """Axis point, unit axis (pointing into the body) and the body span [a0, a1] (mm from the output plane) of a module."""
    a = axis_straight(jn) * BODY_DIR[jn]
    return P[jn], a / np.linalg.norm(a), MODULE[cls]


def radial_axial(V, o, a):
    d = V - o
    ax = d @ a
    rad = np.linalg.norm(d - np.outer(ax, a), axis=1)
    return ax, rad


def ring_band(mesh, o, a, r_mod):
    """Axial band (from the output plane, along the body direction) and outer radius of the bracket ring around a module."""
    ax, rad = radial_axial(mesh.vertices, o, a)
    sel = (rad > r_mod + 1.0) & (rad < r_mod + 14.0) & (ax > -25) & (ax < 70)
    if sel.sum() < 50:
        return None
    h, edges = np.histogram(ax[sel], bins=np.arange(-25, 71, 1.0))
    dense = np.where(h > max(10, 0.15 * h.max()))[0]
    t0, t1 = float(edges[dense.min()]), float(edges[dense.max() + 1])
    band = sel & (ax >= t0) & (ax <= t1)
    e1 = np.cross(a, [0, 0, 1.0]); e1 = np.cross(a, [0, 1.0, 0]) if np.linalg.norm(e1) < 1e-6 else e1; e1 /= np.linalg.norm(e1); e2 = np.cross(a, e1)
    d = mesh.vertices[band] - o
    th = np.arctan2(d @ e2, d @ e1); sec = ((th + np.pi) / (2 * np.pi) * 12).astype(int) % 12
    rr = rad[band]
    r_out = float(np.median([rr[sec == k].max() for k in range(12) if (sec == k).any()]))
    return dict(t0=round(t0, 1), t1=round(t1, 1), r_out=round(r_out, 1))


def extract(name, spec):
    m = link_mesh(spec["link"])
    whole_area = float(m.area)
    # faces inside module cylinders (and their rings) are removed
    cen = m.triangles_center
    drop = np.zeros(len(m.faces), dtype=bool)
    mod_area = 0.0
    rings = {}
    for jn, cls in spec["modules"]:
        o, a, M = module_cyl(jn, cls)
        ax, rad = radial_axial(cen, o, a)
        inside = (rad < M["r"] + 1.5) & (ax > -12) & (ax < M["l"] + 4)
        rc = spec.get("ring_cut", RING_CUT[cls])
        if spec.get("bore"):                                     # a bigger RobStride than the module class: the channel is bored to its body
            inside |= (rad < spec["bore"]) & (ax > -12) & (ax < M["l"] + 4)
        ring = (rad < rc["r"]) & (ax >= rc["t0"]) & (ax <= rc["t1"])
        if spec.get("floor") is not None:                       # the foot: keep the plate under the module
            ring &= cen[:, 2] > spec["floor"]
        rb = ring_band(m, o, a, M["r"])
        if rb:
            rings[jn] = rb
        mod_area += float(m.area_faces[(inside | ring) & ~drop].sum())
        drop |= inside | ring
    # modules hosted by this link but not in this piece still count against the bracket area
    for jn in [j for j, h in [(j, u.joints[j].find("parent").get("link")) for j in u.joints if u.joints[j].get("type") == "revolute"]
               if (h == spec["link"] or (j == "leg_left_ankle_roll_joint" and spec["link"] == "leg_left_ankle_roll"))]:
        if jn not in [x[0] for x in spec["modules"]] and jn in BODY_DIR:
            cls = "6512" if jn in ("leg_left_knee_pitch_joint",) else "5010"
            o, a, M = module_cyl(jn, cls)
            ax, rad = radial_axial(cen, o, a)
            mod_area += float(m.area_faces[(rad < M["r"] + 1.5) & (ax > -12) & (ax < M["l"] + 4) & ~drop].sum())
    piece = trimesh.Trimesh(vertices=m.vertices, faces=m.faces[~drop], process=False)
    piece.remove_unreferenced_vertices()
    for n, p0 in spec["keep"]:
        piece = trimesh.intersections.slice_mesh_plane(piece, plane_normal=n, plane_origin=p0, cap=False)
    piece.remove_unreferenced_vertices()
    bracket_area = whole_area - mod_area
    link_bracket_mass = LINK_MASS[spec["link"]] - sum(MODULE[c]["mass_g"] for c in HOSTED[spec["link"]])
    mass = link_bracket_mass * float(piece.area) / bracket_area
    ref = P[spec["ref"]]
    rel = piece.copy(); rel.apply_translation(-ref)
    if spec.get("shift"):
        rel.apply_translation(spec["shift"])
    # plate section at the cut: the bbox of vertices within 4 mm of the cut plane
    section = None
    if spec.get("cut"):
        axname, z, _ = spec["cut"]
        k = "xyz".index(axname)
        near = np.abs(piece.vertices[:, k] - z) < 4.0
        others = [i for i in range(3) if i != k]
        near &= np.all(np.abs(piece.vertices[:, others] - ref[others]) < 32.0, axis=1)
        if near.any():
            vv = piece.vertices[near] - ref
            lo, hi = vv.min(axis=0), vv.max(axis=0)
            section = dict(plane=axname, at=round(float(z - ref[k]), 1), lo=[round(float(x), 1) for x in lo], hi=[round(float(x), 1) for x in hi],
                           centre=[round(float(x), 1) for x in (lo + hi) / 2])
            section["centre"][k] = round(float(z - ref[k]), 1)
    if len(rel.faces) == 0:
        raise SystemExit(f"{name}: nothing left after the cuts")
    hull = rel.convex_hull
    planes = [[*map(float, n), float(n @ hull.vertices[hull.faces[i][0]])] for i, n in enumerate(hull.face_normals)]
    # merge near-duplicate planes
    uniq = []
    for pl in planes:
        if not any(abs(np.dot(pl[:3], q[:3]) - 1) < 1e-3 and abs(pl[3] - q[3]) < 0.5 for q in uniq):
            uniq.append([round(v, 4) for v in pl])
    pts, _ = trimesh.sample.sample_surface(rel, N_SAMPLES)
    out = dict(name=spec["name"], bhl_source=spec["bhl"], link=spec["link"], ref_joint=spec["ref"], ref_world_mm=[round(float(x), 1) for x in ref],
               bbox=[[round(float(x), 1) for x in rel.bounds[0]], [round(float(x), 1) for x in rel.bounds[1]]], mass_g=round(mass),
               area_cm2=round(float(piece.area) / 100, 1), faces=int(len(piece.faces)), section=section, rings=rings,
               hull=uniq, pts=[[round(float(x), 1) for x in p] for p in pts])
    # export left and mirrored right, decimated
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dec = bg.decimate(rel, FACES) if len(rel.faces) > FACES else rel
    for side, mesh in (("L", dec), ("R", None)):
        mm = mesh.copy() if mesh is not None else dec.copy()
        if side == "R":
            mm.vertices[:, 1] *= -1
            mm.faces = mm.faces[:, ::-1]
        mm.export(OUT_DIR / f"{name}_{side}.glb", file_type="glb")
    out["file"] = f"assets/geom/v2/{name}_{{side}}.glb"
    out["glb_faces"] = int(len(dec.faces))
    return out


if __name__ == "__main__":
    result = {}
    for name, spec in PIECES.items():
        r = extract(name, spec)
        result[name] = r
        sec = r["section"]
        print(f"{name:18s} {r['faces']:6d} faces -> {r['glb_faces']:5d}  mass {r['mass_g']:4d} g  bbox {r['bbox'][0]}..{r['bbox'][1]}"
              + (f"  cut section {sec['lo']}..{sec['hi']}" if sec else "") + (f"  rings {r['rings']}" if r["rings"] else ""))
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        from matplotlib.collections import LineCollection
        names = list(result)
        fig, axes = plt.subplots(len(names), 3, figsize=(15, 3.6 * len(names)))
        for r_, name in enumerate(names):
            mm = trimesh.load(OUT_DIR / f"{name}_L.glb", force="mesh"); v_ = mm.vertices
            for c_, (i, k, lab) in enumerate(((0, 1, "x-y"), (0, 2, "x-z"), (1, 2, "y-z"))):
                ax_ = axes[r_, c_]
                f_ = mm.faces[np.random.choice(len(mm.faces), min(6000, len(mm.faces)), replace=False)]
                segs = np.concatenate([np.stack([v_[f_[:, 0]][:, [i, k]], v_[f_[:, 1]][:, [i, k]]], axis=1), np.stack([v_[f_[:, 1]][:, [i, k]], v_[f_[:, 2]][:, [i, k]]], axis=1)])
                ax_.add_collection(LineCollection(segs, colors="k", linewidths=0.2, alpha=0.6)); ax_.autoscale(); ax_.set_aspect("equal"); ax_.grid(True, lw=0.3)
                ax_.plot(0, 0, "r+", ms=12, mew=2); ax_.set_title(f"{name} {lab}", fontsize=9)
        plt.tight_layout(); plt.savefig(ROOT / "tools/.cache/bhl_pieces.png", dpi=55); print("preview: tools/.cache/bhl_pieces.png")
    except Exception as e:  # noqa: BLE001
        print("preview failed:", e)
    meta = dict(units="mm", frame="BHL world at the zero pose with the arms straightened; vertices relative to ref_world_mm",
                source="HybridRobotics/berkeley-humanoid-lite-assets (CC BY-SA 4.0), link STLs", modules=MODULE, straighten_deg=round(math.degrees(ang), 2),
                joints={k: [round(float(x), 1) for x in v] for k, v in P.items() if "left" in k})
    OUT_JSON.write_text(json.dumps(dict(meta=meta, pieces=result), separators=(",", ":")) + "\n")
    print("wrote", OUT_JSON.relative_to(ROOT), "and", len(result) * 2, "GLBs in", OUT_DIR.relative_to(ROOT))
