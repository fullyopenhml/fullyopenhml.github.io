#!/usr/bin/env python3
"""Build the builder's 3D modules: one small GLB per module (and side) plus anchor points.

Sources
  foh      primitives from assets/data/robot.json
  duke2    the project's published viewer model (Draco GLB), split by assembly path
  bhl, lerobot, duck, mevita   the projects' URDFs and STL meshes on GitHub, posed at zero

Meshes are cached in tools/.cache/geom (git-ignored), decimated and merged per module,
and written to assets/geom/<module>[-L|-R].glb. Anchors (metres, X forward, Y left,
Z up, zero pose) go to assets/data/module_geom.json; the builder composes modules by
matching anchors: lower.top = torso.bottom, torso.shoulder_L = arms.shoulder_L, ...

Run:  tools/.venv/bin/python tools/build_geometry.py
Needs: trimesh, numpy, open3d, DracoPy, pycollada (uv pip install ... into tools/.venv)
"""
from __future__ import annotations

import json
import math
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools/.cache/geom"
OUT_DIR = ROOT / "assets/geom"
OUT_JSON = ROOT / "assets/data/module_geom.json"
FACE_BUDGET = 36000          # faces per exported GLB

Y_UP_TO_Z_UP = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=float)


def r2(v, n=4):
    return [round(float(x), n) for x in v]


def fetch(url: str, name: str | None = None) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / (name or re.sub(r"[^A-Za-z0-9._-]", "_", url.split("://", 1)[1]))
    if not p.exists():
        print("  fetch", url)
        with urllib.request.urlopen(url, timeout=60) as r:
            p.write_bytes(r.read())
    return p


def rpy_matrix(r, p, y):
    cr, sr, cp, sp, cy, sy = math.cos(r), math.sin(r), math.cos(p), math.sin(p), math.cos(y), math.sin(y)
    Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def origin_T(el):
    T = np.eye(4)
    if el is None:
        return T
    xyz = [float(v) for v in el.get("xyz", "0 0 0").split()]
    rpy = [float(v) for v in el.get("rpy", "0 0 0").split()]
    T[:3, :3] = rpy_matrix(*rpy)
    T[:3, 3] = xyz
    return T


def cluster(mesh: trimesh.Trimesh, cell: float) -> trimesh.Trimesh:
    """Vertex-clustering decimation: snap vertices to a grid of size `cell`, drop collapsed faces.
    Robust on triangle soups and non-manifold STL exports, which quadric decimation refuses."""
    v = mesh.vertices
    key = np.floor((v - v.min(axis=0)) / cell).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    n = inv.max() + 1
    acc = np.zeros((n, 3)); cnt = np.zeros(n)
    np.add.at(acc, inv, v); np.add.at(cnt, inv, 1)
    nv = acc / cnt[:, None]
    f = inv[mesh.faces]
    keep = (f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])
    f = np.unique(np.sort(f[keep], axis=1), axis=0) if keep.any() else f[keep]
    return trimesh.Trimesh(vertices=nv, faces=f, process=False)


def decimate(mesh: trimesh.Trimesh, faces: int) -> trimesh.Trimesh:
    if len(mesh.faces) <= faces:
        return mesh
    m = mesh
    try:
        import open3d as o3d
        om = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(mesh.vertices), o3d.utility.Vector3iVector(mesh.faces))
        sm = om.simplify_quadric_decimation(target_number_of_triangles=int(faces))
        if len(sm.triangles) > 0:
            m = trimesh.Trimesh(vertices=np.asarray(sm.vertices), faces=np.asarray(sm.triangles), process=False)
    except Exception as e:  # noqa: BLE001
        print("  open3d decimation failed:", e)
    if 0 < len(m.faces) <= faces * 1.6:
        return m
    # quadric decimation stalled on this mesh: cluster with a growing cell until under budget
    ext = float(np.max(mesh.extents)) or 0.1
    cell = ext / 200
    for _ in range(12):
        c = cluster(mesh, cell)
        if 0 < len(c.faces) <= faces:
            return c
        cell *= 1.35
    return c if len(c.faces) else mesh


def export_group(name: str, meshes: list[trimesh.Trimesh]) -> tuple[str | None, list | None]:
    meshes = [m for m in meshes if m is not None and len(m.faces) > 0]
    if not meshes:
        return None, None
    total = sum(len(m.faces) for m in meshes)
    if total > FACE_BUDGET:
        meshes = [decimate(m, max(200, FACE_BUDGET * len(m.faces) / total)) for m in meshes]
    merged = trimesh.util.concatenate(meshes)
    merged.merge_vertices()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{name}.glb"
    path.write_bytes(merged.export(file_type="glb"))
    print(f"  {path.name}: {len(merged.faces)} faces, {path.stat().st_size // 1024} kB")
    return f"assets/geom/{path.name}", [r2(merged.bounds[0]), r2(merged.bounds[1])]


# ---------------------------------------------------------------- URDF ---------------
class Urdf:
    def __init__(self, url: str, mesh_base: str, name: str):
        self.name = name
        self.path = fetch(url, f"{name}.urdf")
        self.mesh_base = mesh_base
        root = ET.parse(self.path).getroot()
        self.links = {l.get("name"): l for l in root.findall("link")}
        self.joints = {j.get("name"): j for j in root.findall("joint")}
        self.parent_of = {j.find("child").get("link"): (j.find("parent").get("link"), origin_T(j.find("origin")), j.get("name")) for j in self.joints.values()}
        self.T = {}
        for l in self.links:
            self.T[l] = self.world(l)
        self.joint_pos = {}
        for jn, j in self.joints.items():
            parent = j.find("parent").get("link")
            self.joint_pos[jn] = (self.T[parent] @ origin_T(j.find("origin")))[:3, 3]

    def world(self, link):
        if link in self.T:
            return self.T[link]
        if link not in self.parent_of:
            return np.eye(4)
        parent, T, _ = self.parent_of[link]
        return self.world(parent) @ T

    def mesh_url(self, fn: str) -> str:
        # every source keeps its meshes in one folder, so the basename is enough
        return self.mesh_base + "/" + fn.split("/")[-1]

    def link_meshes(self, link) -> list[trimesh.Trimesh]:
        out = []
        for vis in self.links[link].findall("visual"):
            g = vis.find("geometry")
            if g is None:
                continue
            Tv = self.T[link] @ origin_T(vis.find("origin"))
            m = None
            mesh = g.find("mesh")
            if mesh is not None:
                url = self.mesh_url(mesh.get("filename"))
                try:
                    loaded = trimesh.load(fetch(url, f"{self.name}__{url.split('/')[-1]}"), force="mesh")
                except Exception as e:  # noqa: BLE001
                    print("  mesh failed", url, e)
                    continue
                m = loaded
                sc = mesh.get("scale")
                if sc:
                    m.apply_scale([float(v) for v in sc.split()])
            elif g.find("box") is not None:
                m = trimesh.creation.box(extents=[float(v) for v in g.find("box").get("size").split()])
            elif g.find("cylinder") is not None:
                c = g.find("cylinder"); m = trimesh.creation.cylinder(radius=float(c.get("radius")), height=float(c.get("length")))
            elif g.find("sphere") is not None:
                m = trimesh.creation.icosphere(subdivisions=2, radius=float(g.find("sphere").get("radius")))
            if m is None:
                continue
            m = m.copy(); m.apply_transform(Tv)
            out.append(m)
        return out


def build_urdf_robot(name, urdf_url, mesh_base, slot_of, side_of, anchors_fn):
    print(f"== {name}")
    u = Urdf(urdf_url, mesh_base, name)
    groups = {}
    for link in u.links:
        slot = slot_of(link)
        if slot is None:
            continue
        side = side_of(link) if slot in ("arms", "hands") else "C"
        groups.setdefault((slot, side), []).extend(u.link_meshes(link))
    bounds = {}
    files = {}
    for (slot, side), meshes in groups.items():
        mid = f"{name}-{slot}"
        f, b = export_group(mid if side == "C" else f"{mid}-{side}", meshes)
        if f:
            files.setdefault(mid, {})[side] = f
            bounds.setdefault(mid, []).append(b)
    modules = {}
    for mid, parts in files.items():
        bb = np.array([[min(b[0][i] for b in bounds[mid]) for i in range(3)], [max(b[1][i] for b in bounds[mid]) for i in range(3)]])
        modules[mid] = dict(parts=parts, bbox=[r2(bb[0]), r2(bb[1])], anchors=anchors_fn(mid.split("-", 1)[1], u, bb))
    return modules


# ---------------------------------------------------------------- FOH ------------------
def build_foh():
    print("== foh")
    robot = json.loads((ROOT / "assets/data/robot.json").read_text())
    joints = {j["id"]: j for j in robot["joints"]}

    def link_slot(lid):
        if lid == "torso":
            return "torso"
        if lid == "pelvis" or lid.startswith(("hip_", "thigh", "shank", "ankle", "foot")):
            return "lower"
        return "arms"

    def part_slot(pid, lid):
        if pid.startswith("3DP_hea") or pid == "EL_CAMERA_D435I":
            return "head"
        if pid.startswith("3DP_grp") or pid.startswith("EL_SERVO"):
            return "hands"
        return link_slot(lid)

    groups = {}
    head_min = 1e9
    for lnk in robot["links"]:
        o = np.array(lnk["origin"]) / 1000
        for part in lnk["parts"]:
            slot = part_slot(part["part"], lnk["id"])
            side = "C" if slot not in ("arms", "hands") else ("L" if lnk["id"].endswith("_L") else "R")
            for sh in part["shapes"]:
                c = o + np.array(sh["c"]) / 1000
                if sh["t"] == "box":
                    m = trimesh.creation.box(extents=np.array(sh["s"]) / 1000)
                else:
                    r, l = sh["r"] / 1000, sh["l"] / 1000
                    m = trimesh.creation.cylinder(radius=r, height=l, sections=24)
                    if sh["axis"] == "x":
                        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
                    elif sh["axis"] == "y":
                        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
                m.apply_translation(c)
                groups.setdefault((slot, side), []).append(m)
                if slot == "head":
                    head_min = min(head_min, float(m.bounds[0][2]))
    modules = {}
    files, bounds = {}, {}
    for (slot, side), meshes in groups.items():
        mid = f"foh-{slot}"
        f, b = export_group(mid if side == "C" else f"{mid}-{side}", meshes)
        files.setdefault(mid, {})[side] = f
        bounds.setdefault(mid, []).append(b)
    J = lambda n: (np.array(joints[n]["origin"]) / 1000).tolist()
    anchors = dict(
        lower=dict(top=J("waist")),
        torso=dict(bottom=J("waist"), shoulder_L=J("shoulder_pitch_L"), shoulder_R=J("shoulder_pitch_R"), top=[0, 0, round(head_min, 4)]),
        arms=dict(shoulder_L=J("shoulder_pitch_L"), shoulder_R=J("shoulder_pitch_R"), wrist_L=J("wrist_roll_L"), wrist_R=J("wrist_roll_R")),
        hands=dict(wrist_L=J("wrist_roll_L"), wrist_R=J("wrist_roll_R")),
        head=dict(bottom=[0, 0, round(head_min, 4)]),
    )
    for mid, parts in files.items():
        bb = [[min(b[0][i] for b in bounds[mid]) for i in range(3)], [max(b[1][i] for b in bounds[mid]) for i in range(3)]]
        modules[mid] = dict(parts=parts, bbox=bb, anchors=anchors[mid.split("-", 1)[1]], credit="Fully Open Humanoid v0.2 model (this site)")
    return modules


# ---------------------------------------------------------------- Duke V2 -------------
def build_duke():
    d = ROOT / "Duke_Humanoid_V2_OpenSource/hardware-site/docs/assets/viewer"
    if not d.exists():
        print("== duke2: source folder missing, skipped")
        return {}
    print("== duke2")
    pj = json.loads((d / "parts.json").read_text())
    node_path = {}
    for name, occs in list(pj["parts"].items()) + list(pj["vendor"].items()):
        for o in occs:
            node_path[o["node"]] = o["path"]
    sc = trimesh.load(d / "robot.glb", force="scene")

    def slot_side(path):
        top = path.split("+")[0]
        if top.startswith("v2.1_lower_body"):
            return "lower", "C"
        if top.startswith("000_left_arm"):
            return "arms", "L"
        if top.startswith("000_right_arm"):
            return "arms", "R"
        if top.startswith("dovetail_umi_gripper"):
            return "hands", None       # side from position
        if "twincities" in path:
            return "head", "C"
        return "torso", "C"

    groups, centers = {}, {}
    for node in sc.graph.nodes_geometry:
        path = node_path.get(node)
        if not path:
            continue
        T, gname = sc.graph[node]
        m = sc.geometry[gname].copy()
        m.apply_transform(Y_UP_TO_Z_UP @ T)
        slot, side = slot_side(path)
        if side is None:
            side = "L" if m.centroid[1] > 0 else "R"
        groups.setdefault((slot, side), []).append(m)
        centers.setdefault(path, []).append(m.centroid)

    def mean_center(pred):
        pts = [c for p, cs in centers.items() if pred(p) for c in cs]
        return r2(np.mean(pts, axis=0)) if pts else None

    shoulder_L = mean_center(lambda p: p.startswith("000_left_arm") and "Robstride 03 - full" in p)
    shoulder_R = mean_center(lambda p: p.startswith("000_right_arm") and "Robstride 03 - full" in p)
    wrist_L = mean_center(lambda p: "001_left_wrist" in p and "FL46" in p)
    wrist_R = mean_center(lambda p: "001_right_wrist" in p and "FL46" in p)
    head_b = mean_center(lambda p: "3DP_cam01" in p or "gimbal_mount" in p)
    waist = [0, 0, 0]
    # the shoulder-1 RS03 sits inside the body; the arm bracket bolts to its output at the body's side face,
    # so the shoulder anchor is moved out to the torso's lateral extent (same point on both modules)
    torso_meshes = groups.get(("torso", "C"), [])
    if torso_meshes and shoulder_L and shoulder_R:
        half_w = max(float(np.max(np.abs(m.bounds[:, 1]))) for m in torso_meshes)
        shoulder_L = [shoulder_L[0], round(half_w, 4), shoulder_L[2]]
        shoulder_R = [shoulder_R[0], round(-half_w, 4), shoulder_R[2]]
    files, bounds = {}, {}
    for (slot, side), meshes in groups.items():
        mid = f"duke2-{slot}"
        f, b = export_group(mid if side == "C" else f"{mid}-{side}", meshes)
        files.setdefault(mid, {})[side] = f
        bounds.setdefault(mid, []).append(b)
    anchors = dict(
        lower=dict(top=waist), torso=dict(bottom=waist, shoulder_L=shoulder_L, shoulder_R=shoulder_R, top=[0, 0, head_b[2]] if head_b else None),
        arms=dict(shoulder_L=shoulder_L, shoulder_R=shoulder_R, wrist_L=wrist_L, wrist_R=wrist_R), hands=dict(wrist_L=wrist_L, wrist_R=wrist_R),
        head=dict(bottom=[0, 0, head_b[2]] if head_b else None),
    )
    modules = {}
    for mid, parts in files.items():
        bb = [[min(b[0][i] for b in bounds[mid]) for i in range(3)], [max(b[1][i] for b in bounds[mid]) for i in range(3)]]
        modules[mid] = dict(parts=parts, bbox=bb, anchors=anchors[mid.split("-", 1)[1]], credit="Duke Humanoid V2 viewer model, General Robotics Lab (Apache-2.0)")
    return modules


# ---------------------------------------------------------------- URDF robots ----------
def build_bhl():
    base = "https://raw.githubusercontent.com/HybridRobotics/berkeley-humanoid-lite-assets/main/data/robots/berkeley_humanoid/berkeley_humanoid_lite"
    def slot_of(l):
        return "lower" if l.startswith("leg_") else "arms" if l.startswith("arm_") else "torso"
    def side_of(l):
        return "L" if "_left_" in l else "R"
    def anchors(slot, u, bb):
        jp = u.joint_pos
        hips = np.mean([jp["leg_left_hip_roll_joint"], jp["leg_right_hip_roll_joint"]], axis=0)
        a = dict(lower=dict(top=r2(hips)), torso=dict(bottom=r2(hips), shoulder_L=r2(jp["arm_left_shoulder_pitch_joint"]), shoulder_R=r2(jp["arm_right_shoulder_pitch_joint"]), top=[0, 0, round(float(bb[1][2]), 4)]),
                 arms=dict(shoulder_L=r2(jp["arm_left_shoulder_pitch_joint"]), shoulder_R=r2(jp["arm_right_shoulder_pitch_joint"]), wrist_L=r2(jp["arm_left_hand_l"]), wrist_R=r2(jp["arm_hand_r"])))
        return a[slot]
    mods = build_urdf_robot("bhl", base + "/urdf/berkeley_humanoid_lite.urdf", base + "/meshes", slot_of, side_of, anchors)
    for m in mods.values():
        m["credit"] = "Berkeley Humanoid Lite assets, Hybrid Robotics (CC BY-SA 4.0)"
    return mods


def build_lerobot():
    base = "https://raw.githubusercontent.com/huggingface/lerobot-humanoid-model/main/models/bipedal_plateform/urdf"
    def anchors(slot, u, bb):
        top = u.joint_pos.get("upper_body")
        return dict(top=r2(top) if top is not None else [0, 0, round(float(bb[1][2]), 4)])
    # the "bipedal_plateform" URDF also carries a folded upper body (torso_assembly, torso_mesh); the legs module stops at the pelvis
    mods = build_urdf_robot("lerobot", base + "/robot.urdf", base + "/assets", lambda l: None if l in ("torso_assembly", "torso_mesh") else "lower", lambda l: "C", anchors)
    for m in mods.values():
        m["credit"] = "LeRobot Humanoid model, Hugging Face (Apache-2.0)"
    return mods


def build_duck():
    base = "https://raw.githubusercontent.com/apirrone/Open_Duck_Mini/v2/mini_bdx/robots/open_duck_mini_v2"
    def slot_of(l):
        return None if re.search("head|neck|antenna", l) else "lower"
    def anchors(slot, u, bb):
        top = u.joint_pos.get("neck_pitch")
        return dict(top=r2(top) if top is not None else [0, 0, round(float(bb[1][2]), 4)])
    mods = build_urdf_robot("duck", base + "/robot.urdf", base, slot_of, lambda l: "C", anchors)
    for m in mods.values():
        m["credit"] = "Open Duck Mini v2, Antoine Pirrone (Apache-2.0); head omitted"
    return mods


def build_mevita():
    base = "https://raw.githubusercontent.com/haraduka/mevita/master/models"
    def anchors(slot, u, bb):
        return dict(top=[0, 0, round(float(bb[1][2]), 4)])
    mods = build_urdf_robot("mevita", base + "/mevita_stl.urdf", base + "/meshes", lambda l: "lower", lambda l: "C", anchors)
    for m in mods.values():
        m["credit"] = "MEVITA, JSK Lab, University of Tokyo (MIT)"
    return mods


def main():
    modules = {}
    modules.update(build_foh())
    modules.update(build_duke())
    for fn in (build_bhl, build_lerobot, build_duck, build_mevita):
        try:
            modules.update(fn())
        except Exception as e:  # noqa: BLE001
            print(f"  {fn.__name__} failed: {e}")
    for mid, m in modules.items():
        m["ground_z"] = round(float(m["bbox"][0][2]), 4)
    OUT_JSON.write_text(json.dumps(dict(frame="metres, X forward, Y left, Z up, zero pose", modules=modules), indent=1) + "\n")
    total = sum(p.stat().st_size for p in OUT_DIR.glob("*.glb"))
    print(f"wrote {OUT_JSON.relative_to(ROOT)}: {len(modules)} modules, {total // 1024} kB of GLB")


if __name__ == "__main__":
    main()
