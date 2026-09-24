"""Build the interactive part viewer assets from a fusion_export folder (v2 scene builder).

    python tools/build_viewer.py ../cad/<export> [--old ../cad/<older export>] [--wait 25]
        [--part-faces 10000 --vendor-faces 6000 --hardware-faces 200 --total-faces 3000000]
        [--qbits 14 --level 10] [--normals] [--cache DIR] [--out docs/assets/viewer]

Writes docs/assets/viewer/robot.glb and docs/assets/viewer/parts.json for the page
script (docs/javascripts/viewer.js).

The scene is every visible occurrence with bodies of the robot, each placed from
Fusion's own transform, in Fusion's appearance colours: there is no whole-robot
backdrop any more, the robot is made of its real parts.

Inputs (all in <export>, written by tools/fusion_export and tools/fusion_export_modules):
  tree.csv        one row per component: file_name (unique; a second component with
                  the same name is `name~2`), kind, qty, bodies, material, mass_g, bbox,
                  path (the first occurrence), color_rgb (sRGB 0-255 from the
                  appearance), appearance, COM and inertia.
  print/<file_name>.stl   the component's own bodies, component coordinates, mm.
  transforms.csv  every occurrence with bodies: path, fusion_name, file_name, visible and
                  Occurrence.transform2 (row-major 4x4, translation in m3/m7/m11 in cm).
                  Written by fusion_export_modules; until it exists the transforms of an
                  older export (--old, same model) are used and every row is mapped to
                  the tree by structure: an occurrence is the component whose first
                  occurrence sits at <parent's first path>+<same segment>; same-named
                  components that this cannot separate are told apart by their top-level
                  subassembly, by identical bounding boxes, or by which candidate's STL
                  lands on the older export's viewer/context.stl. Ambiguities are printed.
  modules.csv     optional (fusion_export_modules): the sub-assemblies, for parts.json. A
                  module gets every occurrence of its component: the ancestors of the placed
                  occurrences are resolved to tree.csv components, same-named ones
                  (`name`, `name~2`) by the sub-structure below them (Tree.settle). A
                  same-named component the modules export wrote no STEP of its own for is
                  shown under the one stem of that name (printed as a NOTE).
  export.log      appears when fusion_export has finished; the build waits for it.

Scene rules:
  * Fusion is Z up in mm, glTF is Y up in m: FUSION_TO_GLTF (det +1) is applied last.
  * Pieces of a component's STL with an extent over 450 mm are not parts (the two field
    of view wedges of the RealSense D435) and are dropped; components with `schematic`
    in the name or path are skipped.
  * Site parts (cnc-parts.csv + printed-parts.csv, matched like stage_cad_export.py
    with gen_printed's `|leg` scope) get one mesh and one material per occurrence
    named `<part_id>#<n>`; every other component gets `vendor:<file_name>#<n>`, so it
    is clickable too. Fasteners (name matching screw|bolt|nut|washer|insert|magnet|pin|
    rivet, or under 3 g) are merged per colour into a few flat-shaded `hardware:<k>`
    meshes.
  * Colour: tree.csv color_rgb, sRGB -> linear; metallic/roughness from the appearance
    and material text. A blank colour is derived from that text.
  * Decimation: pymeshlab quadric edge collapse (boundary, topology, planar) to a
    per-mesh cap by class, caps scaled down together until the whole scene fits
    --total-faces. Draco positions only by default (three.js flat-shades a primitive
    without normals): measured 2.2 MB for 887k faces. --normals adds smooth normals
    (30 deg sharp-edge split, int8 accessor next to the Draco positions, see
    tools/glb_tools.py) at about 2.5x the bytes per face: 3.9 MB for 500k faces.
  * Axis triad: X red, Y green, Z blue, 150 mm, at the Fusion origin, in Fusion axes;
    the tips (glTF metres) are in parts.json "axes" for hotspot labels.

parts.json: {"parts": {part_id: [{node, path, center, radius}]},
             "vendor": {file_name: [{node, path, center, radius}]},
             "info": {part_id | "vendor:"+file_name: {desc, kind, qty, material, team_ref,
                      mass_g, bbox, fusion_name, appearance, module_path}},
                      (team_ref: the line of the team BOM the part comes from, "" for a
                       part the team BOM does not list; purchased components carry the
                       ref of the BOM line vendor-parts.csv maps their file_name to)
             "hardware": {"hardware:k": {n, desc}},
             "axes": {"x": [..], "y": [..], "z": [..]},
             "modules": {module_file_name: {name, path, path_prefix, mass_g, depth, qty,
                         prefixes}}}
Centre and radius are in metres, model-viewer axes. A mesh belongs to a module when its
path starts with one of the module's `prefixes` + "+"; `path` (= `path_prefix`) is the
first one, the modules.csv path, and `qty` the number of prefixes: how often the module
occurs in the model.
Mass, COM and inertia come from Fusion (tree.csv), nothing is recomputed here.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import trimesh

SITE = Path(__file__).resolve().parent.parent
OUT = SITE / "docs" / "assets" / "viewer"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_printed import PRINTED  # noqa: E402
from glb_tools import GlbWriter, pbr_material, srgb_to_linear  # noqa: E402
from stage_cad_export import ALIASES, DUPLICATE_NAMES, strip_qty, site_ids  # noqa: E402

# Fusion exports Z up in millimetres; glTF/model-viewer is Y up in metres.
# Rotation block [[1,0,0],[0,0,1],[0,-1,0]]: det +1, a -90 deg turn about X.
FUSION_TO_GLTF = np.array([[0.001, 0, 0, 0], [0, 0, 0.001, 0], [0, -0.001, 0, 0], [0, 0, 0, 1]])
VENDOR_MODEL_NAMES = ("IntelRealsense_D435",)   # vendor sub-assemblies whose children never match a site part


def clean_label(name: str) -> str:
    """A vendor model's Fusion name, fit for the site: no CJK (the site is English), no
    parenthesised CJK tag (`(开模版)`), no copy suffix, no doubled separators."""
    name = re.sub(r"\([^()]*[\u4e00-\u9fff][^()]*\)", "", name)
    name = re.sub(r"[\u4e00-\u9fff]+", "", name)
    name = strip_copy_suffix(name)
    return re.sub(r"[ _]{2,}", lambda m: m.group(0)[0], name).strip(" _")


def strip_copy_suffix(name: str) -> str:
    """Fusion names a copied component `gimbal_neck (1)`; the part is the same."""
    return re.sub(r" \(\d+\)$", "", name)


LEG_SCOPE_PREFIX = "v2.1_lower_body"      # gen_printed: `|leg` names live under the lower body
MAX_PIECE_MM = 450.0                      # larger connected pieces are not parts (D435 view wedges)
FASTENER_RE = re.compile(r"(?<![a-z])(screw|bolt|nut|washer|insert|magnet|pin|rivet)(?![a-z])", re.I)  # as stage_cad_export
FASTENER_MAX_G = 3.0
SPLIT_ANGLE = np.radians(30.0)            # edges sharper than this stay sharp under smooth shading
CURVE_MIN = np.radians(2.5)               # edges bent less than this are planar: no normals needed
AXIS_LEN_MM, AXIS_R_MM = 150.0, 3.0
CLASS_RANK = {"part": 2, "vendor": 1, "hardware": 0}
RNG = np.random.default_rng(0)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ----------------------------------------------------------------------------- matching

class PartLookup:
    """Fusion component name (qty token stripped) + where the occurrence sits -> site part_id.

    gen_printed lists some `ComponentNN` covers twice, `Component42` for the arm
    and `Component42|leg` for the lower body: the `|leg` entry is used only under
    the lower body and the plain entry only elsewhere."""

    def __init__(self):
        ids = site_ids()
        self.scoped: dict[tuple[str, str], str] = {}
        for name, pid, _, _ in PRINTED:
            base, _, scope = name.partition("|")
            if scope and pid in ids:
                self.scoped[(strip_qty(base), scope)] = pid
        self.plain: dict[str, str] = {}
        for pid in ids:
            key = strip_qty(ALIASES.get(pid, pid))
            if self.scoped.get((key, "leg")) == pid:
                continue
            self.plain[key] = pid
        for dup, canon in DUPLICATE_NAMES.items():
            if strip_qty(canon) in self.plain:
                self.plain[strip_qty(dup)] = self.plain[strip_qty(canon)]

    def pid(self, fusion_name: str, path: str) -> str | None:
        # A component inside a vendor model (the D435's own `Component34`..`Component37`)
        # is never a site part, whatever it is called.
        if any(v in path for v in VENDOR_MODEL_NAMES):
            return None
        key = strip_qty(strip_copy_suffix(fusion_name))
        scope = "leg" if path.startswith(LEG_SCOPE_PREFIX) else "arm"
        if (key, scope) in self.scoped:
            return self.scoped[(key, scope)]
        if scope == "leg" and key.startswith("Component"):
            return None       # gen_printed.pick: a plain `ComponentNN` entry never counts lower-body occurrences
        return self.plain.get(key)


_CJK_GROUP = re.compile(r"\([^()]*[\u4e00-\u9fff][^()]*\)")
_CJK = re.compile(r"[\u4e00-\u9fff]+")


def clean_path(s: str) -> str:
    """Occurrence paths are published in parts.json; the site carries no CJK, so a vendor
    model's `(开模版)` tag is dropped from every path segment (consistently, so prefixes still match)."""
    return _CJK.sub("", _CJK_GROUP.sub("", s))


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for k, v in r.items():
            if k and "path" in k and v:
                r[k] = clean_path(v)
    return rows


def team_refs() -> tuple[dict[str, str], dict[str, str]]:
    """(part_id -> team BOM line, Fusion file_name -> team BOM line).

    The team's spreadsheet numbers every line (`E3`, `C21`, `P20`, `H1`) and that
    number is what the team calls the part, so the viewer shows it first. gen_bom.py
    writes it into the `team_ref` column of every parts CSV in docs/data/; a purchased
    component is keyed in the model by its Fusion file name, which vendor-parts.csv
    maps to the BOM part_id. Blank means the team BOM has no line for the part."""
    data = SITE / "docs" / "data"
    by_pid: dict[str, str] = {}
    for f in sorted(data.glob("*.csv")):
        rows = read_csv(f)
        if not rows or "part_id" not in rows[0] or "team_ref" not in rows[0]:
            continue
        for r in rows:
            ref = (r.get("team_ref") or "").strip()
            if ref and r.get("part_id"):
                by_pid.setdefault(r["part_id"], ref)
    by_file: dict[str, str] = {}
    vp = data / "vendor-parts.csv"
    if vp.is_file():
        for r in read_csv(vp):
            ref = by_pid.get((r.get("part_id") or "").strip(), "")
            if ref and r.get("file_name"):
                by_file.setdefault(r["file_name"], ref)
    return by_pid, by_file


def fnum(s: str, default: float = 0.0) -> float:
    try:
        return float(s)
    except (TypeError, ValueError):
        return default


class Tree:
    """tree.csv: components by file_name, by first path, by name; occurrence path -> component."""

    def __init__(self, path: Path):
        self.rows = read_csv(path)
        self.by_file = {r["file_name"]: r for r in self.rows}
        self.by_path = {r["path"]: r for r in self.rows}
        self.by_name: dict[str, list[dict]] = defaultdict(list)
        for r in self.rows:
            self.by_name[r["fusion_name"]].append(r)
        self._cache: dict[str, tuple[dict | None, str]] = {}
        self._settled: dict[str, tuple[dict | None, str]] = {}
        self.sig: dict[str, set] = {}
        self.how: dict[str, int] = defaultdict(int)

    def resolve(self, path: str, name: str | None = None) -> tuple[dict | None, str]:
        """(component row, how): 'direct' (the row's own path), 'parent' (the parent's
        component + the same segment), 'name' (only one component of that name),
        'ambiguous' (several; row is None, decided by the caller) or 'missing'."""
        if path in self._cache:
            return self._cache[path]
        segs = path.split("+")
        name = name or segs[-1].rsplit(":", 1)[0]
        res: tuple[dict | None, str]
        if path in self.by_path and self.by_path[path]["fusion_name"] == name:
            res = (self.by_path[path], "direct")
        else:
            res = (None, "missing")
            if len(segs) > 1:
                parent, _ = self.resolve("+".join(segs[:-1]))
                if parent is not None:
                    cand = self.by_path.get(parent["path"] + "+" + segs[-1])
                    if cand is not None and cand["fusion_name"] == name:
                        res = (cand, "parent")
            if res[0] is None:
                cands = self.by_name.get(name, [])
                if len(cands) == 1:
                    res = (cands[0], "name")
                elif cands:
                    res = (None, "ambiguous")
        self._cache[path] = res
        return res

    def load_signatures(self, trows: list[dict]) -> None:
        """Sub-structure of every occurrence prefix in transforms.csv: the set of (relative
        path, file_name) of the occurrences with bodies below it, hidden ones included.
        Same-named components (`name`, `name~2`) are told apart by it: every occurrence of
        a component repeats the sub-structure of its first occurrence (the tree.csv path)."""
        self.sig = defaultdict(set)
        for r in trows:
            segs = r["path"].split("+")
            for i in range(1, len(segs)):
                self.sig["+".join(segs[:i])].add(("+".join(segs[i:]), r["file_name"]))

    def settle(self, path: str, name: str | None = None) -> tuple[dict | None, str]:
        """Component of a subassembly occurrence, same-named components included. In order:
        'direct' (the tree.csv path itself), 'name' (only one component of that name),
        'signature' (the one candidate whose first occurrence has the same sub-structure),
        'parent' (the parent's first path + the same segment), 'overlap' (most sub-structure
        in common), 'top-level' (only one candidate under this top-level subassembly),
        'first'."""
        name = name or path.split("+")[-1].rsplit(":", 1)[0]
        cands = self.by_name.get(name, [])
        if not cands:
            return None, "missing"
        row, how = self.resolve(path, name)
        if row is not None and (how == "direct" or len(cands) == 1):
            return row, how
        sig = self.sig.get(path, set())
        if sig:
            same = [c for c in cands if self.sig.get(c["path"], set()) == sig]
            if len(same) == 1:
                return same[0], "signature"
        if row is not None:
            return row, how
        if sig:
            common = sorted(((len(sig & self.sig.get(c["path"], set())), -i) for i, c in enumerate(cands)), reverse=True)
            if common[0][0] and common[0][0] > common[1][0]:
                return cands[-common[0][1]], "overlap"
        top = path.split("+")[0]
        same_top = [c for c in cands if c["path"].split("+")[0] == top]
        if len(same_top) == 1:
            return same_top[0], "top-level"
        return (same_top or cands)[0], "first"

    def ancestors(self, path: str) -> list[tuple[str, dict, str]]:
        """(prefix path, component row, how) for every ancestor occurrence of `path` whose
        name is a tree.csv component, nearest first."""
        segs = path.split("+")
        out = []
        for i in range(len(segs) - 1, 0, -1):
            pre = "+".join(segs[:i])
            if pre not in self._settled:
                self._settled[pre] = self.settle(pre, segs[i - 1].rsplit(":", 1)[0])
                self.how[self._settled[pre][1]] += 1
            row, how = self._settled[pre]
            if row is not None:
                out.append((pre, row, how))
        return out

def read_transforms(path: Path) -> list[dict]:
    rows = read_csv(path)
    for r in rows:
        M = np.array([float(r[f"m{i}"]) for i in range(16)]).reshape(4, 4)
        M[:3, 3] *= 10.0          # Fusion API lengths are cm; the meshes are mm
        r["M"] = M
    return rows


# ----------------------------------------------------------------------------- looks

def material_look(appearance: str, material: str) -> tuple[float, float, str]:
    """(metallic, roughness, class) from Fusion's appearance and material names."""
    t = f"{appearance} {material}".lower()
    if "glass" in t:
        return 0.0, 0.15, "glass"
    if "fr4" in t or "board" in t or "pcb" in t:
        return 0.0, 0.6, "board"
    if "rubber" in t or "silicone" in t or "tpu" in t:
        return 0.0, 0.9, "rubber"
    if "polished" in t and any(k in t for k in ("platinum", "chrome", "silver", "nickel")):
        return 1.0, 0.2, "chrome"
    if "brass" in t or "copper" in t or "bronze" in t:
        return 0.9, 0.35, "brass"
    if any(k in t for k in ("aluminum", "aluminium", "a356", "6061")):
        return 0.9, 0.45, "aluminum"
    if any(k in t for k in ("stainless", "steel", "iron", "titanium")):
        return 0.9, 0.4, "steel"
    if any(k in t for k in ("abs", "nylon", "pla", "petg", "paht", "acetal", "plastic", "protection",
                            "resin", "polycarbonate", "delrin")):
        return 0.0, 0.55, "plastic"
    return 0.0, 0.6, "unknown"


FALLBACK_RGB = {"aluminum": (204, 204, 206), "steel": (140, 140, 142), "chrome": (220, 220, 222),
                "brass": (200, 160, 80), "plastic": (235, 235, 235), "board": (30, 90, 50),
                "glass": (200, 220, 230), "rubber": (40, 40, 40), "unknown": (153, 153, 153)}


# The parts the team makes (CNC and printed, plus the fasteners) are black /
# dark grey on the real robot; every purchased component (actuators, cameras,
# computer, IMU, batteries, boards) keeps the colour Fusion gives it. Fusion's
# appearance colours are unreliable for the team's own parts ("ABS (White)"
# reads back as 0,0,0), so the team's statement wins there. Finish (metallic /
# roughness) still follows the material class.
ROBOT_RGB = (42, 42, 44)
# Purchased components that also deserve extra mesh detail in the viewer.
KEEP_FUSION_COLOUR_KEYS = ("intelrealsense", "d435", "d436", "robstride", "r06", "3_1_02_090", "feetech",
                           "fl46", "gr-2202", "00mini", "double_helix_pinion", "minisforum")


def look_for(row: dict, own: bool = True) -> tuple[list[float], float, float, str]:
    """(linear rgb, metallic, roughness, class) for a tree row. own=True for the
    team's own parts and the fasteners (robot colour), False for purchased
    components (Fusion colour)."""
    metallic, rough, cls = material_look(row.get("appearance", ""), row.get("material", ""))
    rgb = row.get("color_rgb", "")
    if own:
        rgb = "%d,%d,%d" % ROBOT_RGB
    try:
        srgb = tuple(int(x) for x in rgb.split(","))
        assert len(srgb) == 3
    except (ValueError, AssertionError):
        srgb = FALLBACK_RGB[cls]
    lin = srgb_to_linear(srgb)
    if metallic > 0.5 and max(lin) < 0.02:
        # A black metal with baseColor 0 reflects nothing at all; keep a hint of sheen so
        # anodised black parts still read as shapes (still black on screen).
        lin = [0.02, 0.02, 0.02]
        metallic, rough = 0.7, 0.45
    return lin, metallic, rough, cls


# ----------------------------------------------------------------------------- meshes

class MeshStore:
    """print/<file_name>.stl -> cleaned, decimated component-frame mesh (mm), cached on disk."""

    def __init__(self, print_dir: Path, cache: Path):
        self.print_dir = print_dir
        self.cache = cache
        self.cache.mkdir(parents=True, exist_ok=True)
        self.mem: dict[tuple[str, int], tuple[trimesh.Trimesh | None, dict]] = {}
        self.dropped: dict[str, str] = {}
        self.time_decimate = 0.0

    def stl(self, file_name: str) -> Path:
        return self.print_dir / f"{file_name}.stl"

    def get(self, file_name: str, target: int) -> tuple[trimesh.Trimesh | None, dict]:
        key = (file_name, target)
        if key in self.mem:
            return self.mem[key]
        src = self.stl(file_name)
        st = src.stat()
        tag = hashlib.sha1(f"{file_name}|{st.st_size}|{int(st.st_mtime)}|{target}|v2".encode()).hexdigest()[:16]
        cp = self.cache / f"{tag}.npz"
        if cp.is_file():
            z = np.load(cp, allow_pickle=False)
            meta = json.loads(str(z["meta"]))
            m = trimesh.Trimesh(z["v"], z["f"], process=False) if len(z["f"]) else None
        else:
            # A coarser cap of the same file starts from the finer decimation already in
            # memory (the budget loop's earlier round) instead of the full STL.
            finer = [(t, v) for (f, t), v in self.mem.items() if f == file_name and t > target and v[0] is not None]
            if finer:
                t, (fm, fmeta) = min(finer)
                meta = dict(fmeta)
                m = decimate(fm, target) if len(fm.faces) > target else fm
                m = trimesh.Trimesh(m.vertices, m.faces, process=True)
            else:
                m, meta = self._build(src, target)
            tmp = cp.with_suffix(".tmp.npz")
            np.savez_compressed(tmp, v=(m.vertices if m is not None else np.zeros((0, 3))).astype(np.float32),
                                f=(m.faces if m is not None else np.zeros((0, 3))).astype(np.uint32),
                                meta=json.dumps(meta))
            os.replace(tmp, cp)
        if meta.get("dropped"):
            self.dropped[file_name] = meta["dropped"]
        if m is not None:
            # the cache holds float32: use the same values now, so a rebuild from the cache
            # gives a byte-identical robot.glb
            m = trimesh.Trimesh(np.asarray(m.vertices, np.float32), np.asarray(m.faces, np.uint32), process=False)
        self.mem[key] = (m, meta)
        return m, meta

    def _build(self, src: Path, target: int) -> tuple[trimesh.Trimesh | None, dict]:
        raw = trimesh.load(src, force="mesh")
        meta = {"orig_faces": int(len(raw.faces)), "dropped": ""}
        if len(raw.faces) == 0:
            return None, meta
        m = raw
        if float(m.extents.max()) > MAX_PIECE_MM:
            keep, gone = [], []
            for c in m.split(only_watertight=False):
                (gone if float(c.extents.max()) > MAX_PIECE_MM else keep).append(c)
            if gone:
                meta["dropped"] = (f"{len(gone)} piece(s) over {MAX_PIECE_MM:.0f} mm dropped "
                                   f"({', '.join(str(np.round(g.extents).astype(int).tolist()) for g in gone)} mm), "
                                   f"{len(keep)} kept")
            if not keep:
                return None, meta
            m = trimesh.util.concatenate(keep) if len(keep) > 1 else keep[0]
        m.merge_vertices()
        t0 = time.time()
        if len(m.faces) > target:
            m = decimate(m, target)
        self.time_decimate += time.time() - t0
        m = trimesh.Trimesh(m.vertices, m.faces, process=True)
        m.remove_unreferenced_vertices()
        return m, meta


def decimate(m: trimesh.Trimesh, target: int) -> trimesh.Trimesh:
    """pymeshlab quadric edge collapse; topology preservation is dropped when it stops
    the mesh from getting near the cap (bearings with many balls, threads)."""
    import pymeshlab
    best = None
    for topo in (True, False):
        ms = pymeshlab.MeshSet()
        ms.add_mesh(pymeshlab.Mesh(np.asarray(m.vertices, dtype=np.float64), np.asarray(m.faces, dtype=np.int32)))
        ms.meshing_decimation_quadric_edge_collapse(
            targetfacenum=int(target), preserveboundary=True, preservetopology=topo, planarquadric=True,
            preservenormal=True, optimalplacement=True, qualitythr=0.3)
        cm = ms.current_mesh()
        out = trimesh.Trimesh(cm.vertex_matrix(), cm.face_matrix(), process=False)
        if best is None or len(out.faces) < len(best.faces):
            best = out
        if len(out.faces) <= target * 1.25:
            break
    return best


def split_sharp(m: trimesh.Trimesh, angle: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Vertices split at edges sharper than `angle`, faces in the SAME order as m.faces,
    angle-weighted smooth normals per split vertex: (V, F, N)."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    adj, ang = m.face_adjacency, m.face_adjacency_angles
    n = len(m.faces)
    smooth = adj[ang < angle]
    g = coo_matrix((np.ones(len(smooth)), (smooth[:, 0], smooth[:, 1])), shape=(n, n))
    ncomp, label = connected_components(g, directed=False)
    keys = m.faces.ravel().astype(np.int64) * ncomp + np.repeat(label, 3)
    uniq, inv = np.unique(keys, return_inverse=True)
    F = inv.reshape(-1, 3).astype(np.uint32)
    V = np.asarray(m.vertices)[uniq // ncomp]
    N = trimesh.geometry.weighted_vertex_normals(len(V), F, m.face_normals, m.face_angles)
    return V, F, np.asarray(N)


def bounding_sphere(w: trimesh.Trimesh) -> tuple[np.ndarray, float]:
    """Minimum enclosing sphere; the bounding box's sphere when Qhull fails on a
    degenerate (flat or tiny) mesh."""
    try:
        s = w.bounding_sphere
        return np.asarray(s.primitive.center), float(s.primitive.radius)
    except Exception:
        lo, hi = w.bounds
        return (lo + hi) / 2, float(np.linalg.norm(hi - lo) / 2)


def make_prims(w: trimesh.Trimesh, flat: bool) -> list[tuple]:
    """The one primitive of a placed mesh: positions only (flat shading) or split at
    sharp edges with smooth normals. A mesh without any bent edge below SPLIT_ANGLE
    (a plain box) is left flat, which is exact there and saves the normal bytes.
    (Splitting each mesh into a smooth and a planar primitive was tried: what it saved
    in normals it lost in Draco connectivity, planar patches being many small open
    pieces.)"""
    if flat or len(w.faces) < 8:
        return [(np.asarray(w.vertices), np.asarray(w.faces, dtype=np.uint32), None)]
    ang = w.face_adjacency_angles
    if not np.any((ang > CURVE_MIN) & (ang < SPLIT_ANGLE)):
        return [(np.asarray(w.vertices), np.asarray(w.faces, dtype=np.uint32), None)]
    return [split_sharp(w, SPLIT_ANGLE)]


def axis_meshes() -> tuple[list[tuple[str, trimesh.Trimesh, list[float]]], dict]:
    """Three arrows (cylinder + cone) along Fusion +X, +Y, +Z at the origin, in mm."""
    shaft_len = AXIS_LEN_MM - 10 * AXIS_R_MM
    out, tips = [], {}
    for name, rot, rgb in (("axis_x", trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]), [0.8, 0.05, 0.05]),
                           ("axis_y", trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]), [0.05, 0.5, 0.05]),
                           ("axis_z", np.eye(4), [0.05, 0.15, 0.9])):
        shaft = trimesh.creation.cylinder(radius=AXIS_R_MM, height=shaft_len, sections=24)
        shaft.apply_translation([0, 0, shaft_len / 2])
        head = trimesh.creation.cone(radius=2.5 * AXIS_R_MM, height=AXIS_LEN_MM - shaft_len, sections=24)
        head.apply_translation([0, 0, shaft_len])
        arrow = trimesh.util.concatenate([shaft, head])
        arrow.apply_transform(rot)
        tip = trimesh.transform_points(np.array([[0, 0, AXIS_LEN_MM]]), rot)[0]
        tips[name[-1]] = [round(float(v), 4) for v in trimesh.transform_points(tip[None], FUSION_TO_GLTF)[0]]
        out.append((name, arrow, rgb))
    return out, tips


# ----------------------------------------------------------------------------- build

def wait_for(path: Path, minutes: float) -> None:
    t0 = time.time()
    while not path.is_file():
        waited = time.time() - t0
        if waited > minutes * 60:
            raise SystemExit(f"gave up after {minutes:g} min waiting for {path}")
        print(f"waiting for {path} ({waited:.0f} s)", flush=True)
        time.sleep(30)


def rel(p: Path) -> str:
    try:
        return p.relative_to(SITE).as_posix()
    except ValueError:
        return str(p)


def module_of(path: str, prefixes: list[tuple[str, str]]) -> str:
    """Longest module occurrence prefix that contains this path (prefixes: (prefix, module))."""
    best, best_len = "", -1
    for pre, mod in prefixes:
        if path.startswith(pre + "+") and len(pre) > best_len:
            best, best_len = mod, len(pre)
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("folder", help="fusion_export folder with tree.csv and print/")
    ap.add_argument("--old", help="older export of the same model: its transforms.csv (and viewer/context.stl) "
                                  "are used while <folder>/transforms.csv does not exist")
    ap.add_argument("--transforms", help="use this transforms.csv (overrides the folder's and --old)")
    ap.add_argument("--modules", help="use this modules.csv (default: the folder's, else the one next to --transforms)")
    ap.add_argument("--wait", type=float, default=25, help="minutes to wait for <folder>/export.log")
    ap.add_argument("--part-faces", type=int, default=10_000)
    ap.add_argument("--vendor-faces", type=int, default=6000)
    ap.add_argument("--hardware-faces", type=int, default=200)
    ap.add_argument("--total-faces", type=int, default=3_000_000)
    ap.add_argument("--qbits", type=int, default=14)
    ap.add_argument("--level", type=int, default=10)
    ap.add_argument("--normals", action="store_true",
                    help="smooth vertex normals (int8 accessor next to the Draco positions): about 2.5x the "
                         "bytes per face, so pair it with --total-faces 350000 to stay under 3 MB")
    ap.add_argument("--cache", help="decimation cache directory (default: %TEMP%/dh_viewer_cache)")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()

    src = Path(a.folder).resolve()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cache = Path(a.cache) if a.cache else Path(os.environ.get("TEMP", "/tmp")) / "dh_viewer_cache"
    t_start = time.time()

    wait_for(src / "tree.csv", a.wait)
    wait_for(src / "export.log", a.wait)
    tree = Tree(src / "tree.csv")
    print(f"tree.csv: {len(tree.rows)} components, {sum(int(r['bodies'] or 0) > 0 for r in tree.rows)} with bodies")

    # --- occurrences: which transforms
    if a.transforms:
        tpath, mapped = Path(a.transforms), False
    elif (src / "transforms.csv").is_file():
        tpath, mapped = src / "transforms.csv", False
    elif a.old and (Path(a.old) / "transforms.csv").is_file():
        tpath, mapped = Path(a.old) / "transforms.csv", True
    else:
        raise SystemExit(f"no transforms.csv in {src} and no --old export with one")
    trows = read_transforms(tpath)
    tree.load_signatures(trows)
    print(f"transforms: {tpath} ({len(trows)} occurrences, "
          f"{'mapped to the tree by structure' if mapped else 'file_name column used directly'})")
    if not mapped:
        bad = [r["file_name"] for r in trows if r["file_name"] not in tree.by_file]
        if bad:
            print(f"WARNING: {len(bad)} transforms rows name a file_name that is not in tree.csv, "
                  f"falling back to structural mapping for those: {sorted(set(bad))[:10]}")
        lumped = defaultdict(int)
        for r in trows:
            t = tree.by_file.get(r["file_name"])
            if t is not None and t["fusion_name"] != r["fusion_name"]:
                lumped[f"{r['fusion_name']} -> {t['fusion_name']}"] += 1
        if lumped:
            print(f"NOTE: {sum(lumped.values())} occurrences are drawn with another component's STL because Fusion "
                  f"gives both the same component id (tree.csv lists only the first name):")
            print("\n".join(f"  {n:4d} x {k}" for k, n in sorted(lumped.items(), key=lambda kv: -kv[1])))

    lookup = PartLookup()
    store = MeshStore(src / "print", cache)
    occ: list[dict] = []          # placed occurrences
    skipped: dict[str, list[str]] = defaultdict(list)
    ambiguous: list[str] = []
    ctx_tree = None

    def context_tree():
        nonlocal ctx_tree
        if ctx_tree is None:
            from scipy.spatial import cKDTree
            cpath = Path(a.old) / "viewer" / "context.stl" if a.old else None
            if cpath and cpath.is_file():
                print(f"loading {cpath} to settle same-named components")
                ctx_tree = cKDTree(trimesh.load(cpath, force="mesh").vertices)
            else:
                ctx_tree = False
        return ctx_tree

    def fit(m: trimesh.Trimesh, M: np.ndarray) -> float:
        kd = context_tree()
        if kd is False:
            return float("nan")
        v = trimesh.transform_points(m.vertices, M)
        sample = v[RNG.choice(len(v), size=min(400, len(v)), replace=False)]
        return float(np.median(kd.query(sample)[0]))

    _vm = SITE / "docs" / "assets" / "viewer" / "vendor-map.json"
    vendor_mapped = set(json.loads(_vm.read_text(encoding="utf-8")).keys()) if _vm.is_file() else set()
    for r in trows:
        path, name = r["path"], r["fusion_name"]
        if r["visible"] != "True":
            skipped["hidden in Fusion"].append(f"{name} @ {path}")
            continue
        if "schematic" in path.lower() or "schematic" in name.lower():
            skipped["schematic"].append(path)
            continue
        row, how = (tree.by_file.get(r["file_name"]), "file_name") if not mapped else (None, "")
        if row is None:
            row, how = tree.resolve(path, name)
        if how == "ambiguous":
            cands = tree.by_name[name]
            top = path.split("+")[0]
            same_top = [c for c in cands if c["path"].split("+")[0] == top]
            bboxes = {tuple(round(fnum(c[k]), 1) for k in ("bbox_x_mm", "bbox_y_mm", "bbox_z_mm")) for c in cands}
            if len(same_top) == 1:
                row, how = same_top[0], "ambiguous/top-level"
            elif len(bboxes) == 1:
                row, how = (same_top or cands)[0], "ambiguous/same-geometry"
            else:
                scored = []
                for c in (same_top or cands):
                    m, _ = store.get(c["file_name"], a.vendor_faces)
                    if m is not None:
                        scored.append((fit(m, r["M"]), c))
                scored.sort(key=lambda x: (np.isnan(x[0]), x[0]))
                row = scored[0][1] if scored else cands[0]
                how = "ambiguous/context-fit" if scored and not np.isnan(scored[0][0]) else "ambiguous/first"
                ambiguous.append(f"{path}: {[c['file_name'] for c in cands]} -> {row['file_name']} ({how}"
                                 + (f", median {scored[0][0]:.1f} mm" if how.endswith("fit") else "") + ")")
        if row is None:
            skipped[f"no component in tree.csv ({how})"].append(f"{name} @ {path}")
            continue
        if int(row["bodies"] or 0) == 0:
            skipped["component has no bodies"].append(path)
            continue
        if not store.stl(row["file_name"]).is_file():
            skipped["print/<file_name>.stl missing"].append(row["file_name"])
            continue
        pid = lookup.pid(name, path)
        if pid:
            cls = "part"
        elif row["file_name"] in vendor_mapped:
            cls = "vendor"      # a BOM part (vendor-map.json), however light: the H5 bearing is 2.5 g
        elif FASTENER_RE.search(name) or fnum(row["mass_g"], 1e9) < FASTENER_MAX_G:
            cls = "hardware"
        else:
            cls = "vendor"
        occ.append({"path": path, "name": name, "row": row, "M": r["M"], "pid": pid, "cls": cls, "how": how})

    n_by_cls = defaultdict(int)
    for o in occ:
        n_by_cls[o["cls"]] += 1
    print(f"{len(occ)} occurrences to place: {dict(n_by_cls)}; "
          f"{sum(len(v) for v in skipped.values())} skipped")

    # --- face budget: caps by class, scaled together until the scene fits
    file_cls: dict[str, str] = {}
    for o in occ:
        fn = o["row"]["file_name"]
        if fn not in file_cls or CLASS_RANK[o["cls"]] > CLASS_RANK[file_cls[fn]]:
            file_cls[fn] = o["cls"]
    caps = {"part": a.part_faces, "vendor": a.vendor_faces, "hardware": a.hardware_faces}
    # Actuators and cameras keep their own colours and are what a reader looks at
    # first, so they get four times the vendor cap (the housings carry the detail).
    detailed = {o["row"]["file_name"] for o in occ
                if any(k in " ".join((o["row"].get("fusion_name", ""), o["row"].get("path", ""))).lower()
                       for k in KEEP_FUSION_COLOUR_KEYS)}

    def cap_for(fn: str) -> int:
        c = caps[file_cls[fn]]
        return c * 4 if fn in detailed and file_cls[fn] == "vendor" else c

    for _round in range(4):
        total = 0
        for o in occ:
            fn = o["row"]["file_name"]
            m, _ = store.get(fn, cap_for(fn))
            total += len(m.faces) if m is not None else 0
        print(f"caps {caps}: {total} faces over all occurrences (target {a.total_faces})")
        if total <= a.total_faces:
            break
        scale = a.total_faces / total * 0.97
        caps = {k: max(60, int(v * scale)) for k, v in caps.items()}
    print(f"decimation time {store.time_decimate:.0f} s (cache {cache})")
    for fn, msg in store.dropped.items():
        print(f"  {fn}: {msg}")

    # --- scene
    writer = GlbWriter()
    parts: dict[str, list] = defaultdict(list)
    vendor: dict[str, list] = defaultdict(list)
    counts: dict[str, int] = defaultdict(int)
    hardware: dict[tuple, dict] = {}
    faces_by_cls = defaultdict(int)
    empty: list[str] = []

    def world(o: dict, m: trimesh.Trimesh) -> trimesh.Trimesh:
        w = m.copy()
        w.apply_transform(FUSION_TO_GLTF @ o["M"])
        return w

    def add_single(o: dict, key: str, mat_prefix: str, into: dict):
        m, _ = store.get(o["row"]["file_name"], cap_for(o["row"]["file_name"]))
        if m is None:
            empty.append(o["path"])
            return
        w = world(o, m)
        n = counts[key]
        counts[key] += 1
        node = f"{mat_prefix}{key}#{n}"
        rgb, metallic, rough, _cls = look_for(o["row"], own=(o["cls"] != "vendor"))
        enc = writer.add_mesh(node, pbr_material(node, rgb, metallic, rough), make_prims(w, not a.normals),
                              a.qbits, a.level)
        faces_by_cls[o["cls"]] += enc["n_faces"]
        center, radius = bounding_sphere(w)
        into[key].append({"node": node, "path": o["path"],
                          "center": [round(float(x), 4) for x in center], "radius": round(float(radius), 4)})

    for o in occ:
        if o["cls"] == "part":
            add_single(o, o["pid"], "", parts)
    for o in occ:
        if o["cls"] == "vendor":
            add_single(o, o["row"]["file_name"], "vendor:", vendor)
    for o in occ:
        if o["cls"] != "hardware":
            continue
        m, _ = store.get(o["row"]["file_name"], cap_for(o["row"]["file_name"]))
        if m is None:
            empty.append(o["path"])
            continue
        rgb, metallic, rough, cls = look_for(o["row"], own=True)   # fasteners: robot colour
        key = (tuple(rgb), metallic, rough)
        g = hardware.setdefault(key, {"V": [], "F": [], "n": 0, "off": 0, "cls": cls, "rgb": rgb,
                                      "metallic": metallic, "rough": rough})
        w = world(o, m)
        g["V"].append(np.asarray(w.vertices, np.float32))
        g["F"].append(np.asarray(w.faces, np.uint32) + g["off"])
        g["off"] += len(w.vertices)
        g["n"] += 1
    hw_info = {}
    for k, (key, g) in enumerate(sorted(hardware.items(), key=lambda kv: -kv[1]["n"])):
        node = f"hardware:{k}"
        enc = writer.add_mesh(node, pbr_material(node, g["rgb"], g["metallic"], g["rough"]),
                              [(np.vstack(g["V"]), np.vstack(g["F"]), None)], a.qbits, a.level)
        faces_by_cls["hardware"] += enc["n_faces"]
        hw_info[node] = {"n": g["n"], "desc": f"{g['n']} fasteners and small hardware ({g['cls']})"}

    arrows, tips = axis_meshes()
    for name, arrow, rgb in arrows:
        arrow.apply_transform(FUSION_TO_GLTF)
        writer.add_mesh(name, pbr_material(name, rgb, 0.0, 0.5), make_prims(arrow, not a.normals),
                        a.qbits, a.level)

    glb = out / "robot.glb"
    size = writer.write(glb, extras={"source": src.name, "transforms": tpath.name,
                                     "caps": caps, "normals": bool(a.normals)})

    # --- parts.json
    modules: dict[str, dict] = {}
    mod_csv = Path(a.modules) if a.modules else src / "modules.csv"
    if not mod_csv.is_file() and a.transforms and (Path(a.transforms).parent / "modules.csv").is_file():
        mod_csv = Path(a.transforms).parent / "modules.csv"
    prefixes: list[tuple[str, str]] = []
    if mod_csv.is_file():
        stem_of_row: dict[str, str] = {}               # tree.csv file_name -> module stem
        stems_by_name: dict[str, list[str]] = defaultdict(list)
        notes: list[str] = []
        for r in read_csv(mod_csv):
            if not r["file"]:
                continue
            fn = r["file"][:-5] if r["file"].lower().endswith(".step") else r["file"]
            modules[fn] = {"name": r["fusion_name"], "path": r["path"], "path_prefix": r["path"],
                           "mass_g": fnum(r["mass_g"]), "depth": int(r["depth"] or 0), "prefixes": [r["path"]]}
            stems_by_name[r["fusion_name"]].append(fn)
            row, how = tree.settle(r["path"], r["fusion_name"])
            if row is None:
                notes.append(f"{fn}: no component named {r['fusion_name']!r} in tree.csv")
            elif row["file_name"] in stem_of_row:
                notes.append(f"{fn} resolves to tree.csv {row['file_name']} like {stem_of_row[row['file_name']]} ({how})")
            else:
                if row["file_name"] != fn:
                    print(f"WARNING: modules.csv {fn} is tree.csv {row['file_name']} at {r['path']} ({how}): "
                          f"the two Fusion scripts number same-named components differently")
                stem_of_row[row["file_name"]] = fn
        # A same-named component the modules export wrote no STEP of its own for (numbered
        # differently, or one STEP for the name): its occurrences go under the stem of that name.
        for name, stems in stems_by_name.items():
            orphans = [t for t in tree.by_name.get(name, []) if t["file_name"] not in stem_of_row]
            free = [st for st in stems if st not in stem_of_row.values()]
            for t in orphans:
                if len(free) == 1 and len(orphans) == 1:
                    stem = free[0]
                elif len(stems) == 1:
                    stem = stems[0]
                else:
                    notes.append(f"tree.csv {t['file_name']} (first at {t['path']}) is under none of {stems}")
                    continue
                stem_of_row[t["file_name"]] = stem
                notes.append(f"tree.csv {t['file_name']} (first at {t['path']}) has no module STEP of its own: "
                             f"its occurrences are shown under {stem}")
        # every occurrence of a module, not only the first: each ancestor of a placed path
        for o in occ:
            for pre, row, _how in tree.ancestors(o["path"]):
                stem = stem_of_row.get(row["file_name"])
                if stem and pre not in modules[stem]["prefixes"]:
                    modules[stem]["prefixes"].append(pre)
        for mod in modules.values():
            mod["qty"] = len(mod["prefixes"])
        prefixes = [(pre, fn) for fn, mod in modules.items() for pre in mod["prefixes"]]
        print(f"modules.csv: {len(modules)} modules, {len(prefixes)} module occurrences; "
              f"ancestor components settled by {dict(tree.how)}")
        for n in notes:
            print(f"  NOTE: {n}")
    else:
        print(f"no {mod_csv.name} yet: parts.json has no modules (run fusion_export_modules)")

    def mod_path(row: dict) -> str:
        if prefixes:
            return module_of(row["path"], prefixes)
        return row["path"].rpartition("+")[0]

    ref_by_pid, ref_by_file = team_refs()
    info: dict[str, dict] = {}
    for f in ("cnc-parts.csv", "printed-parts.csv"):
        for r in read_csv(SITE / "docs" / "data" / f):
            info[r["part_id"]] = {"desc": r["description"], "kind": r["process"] or r["class"],
                                  "qty": r["qty_per_robot"], "material": r["material"],
                                  "team_ref": r.get("team_ref", "")}
    rows_by_pid: dict[str, dict] = {}
    for o in occ:
        if o["pid"] and o["pid"] not in rows_by_pid:
            rows_by_pid[o["pid"]] = o["row"]
    for pid, row in rows_by_pid.items():
        d = info.setdefault(pid, {"desc": row["fusion_name"], "kind": "part", "qty": row["qty"], "material": ""})
        d.setdefault("team_ref", ref_by_pid.get(pid, ""))
        d.update(material=d.get("material") or row["material"], mass_g=fnum(row["mass_g"]),
                 bbox=[fnum(row[k]) for k in ("bbox_x_mm", "bbox_y_mm", "bbox_z_mm")],
                 fusion_name=row["fusion_name"], appearance=row["appearance"], module_path=mod_path(row))
    info = {k: v for k, v in info.items() if k in parts}
    for fn in vendor:
        row = tree.by_file[fn]
        info["vendor:" + fn] = {"desc": clean_label(row["fusion_name"]), "kind": "vendor", "qty": row["qty"],
                                "material": row["material"], "team_ref": ref_by_file.get(fn, ""),
                                "mass_g": fnum(row["mass_g"]),
                                "bbox": [fnum(row[k]) for k in ("bbox_x_mm", "bbox_y_mm", "bbox_z_mm")],
                                "fusion_name": clean_label(row["fusion_name"]), "appearance": row["appearance"],
                                "module_path": mod_path(row)}
    pj = out / "parts.json"
    pj.write_text(json.dumps({"parts": parts, "vendor": vendor, "info": info, "hardware": hw_info,
                              "axes": tips, "modules": modules}, separators=(",", ":")), encoding="utf-8")

    # --- report
    st = writer.stats
    print(f"\n{rel(glb)}: {size / 2**20:.2f} MB "
          f"(Draco {st['draco_bytes'] / 2**20:.2f} MB, normals {st['normal_bytes'] / 2**20:.2f} MB), "
          f"{st['meshes']} meshes / {len(writer.materials)} materials, {st['faces']} faces, {st['points']} vertices")
    print(f"  faces by class: {dict(faces_by_cls)}; caps {caps}; q{a.qbits} level {a.level}"
          + ("; flat shading (positions only)" if not a.normals else
             f"; smooth normals ({st['unmatched']} vertices fell back to the position's first normal)"))
    print(f"  parts: {sum(len(v) for v in parts.values())} meshes for {len(parts)} part IDs; "
          f"vendor: {sum(len(v) for v in vendor.values())} meshes for {len(vendor)} components; "
          f"hardware: {len(hw_info)} merged meshes for {sum(v['n'] for v in hw_info.values())} occurrences")
    print(f"  {rel(pj)}: {pj.stat().st_size / 1024:.0f} KB; axes tips (m) {tips}")
    n_ref = sum(1 for k, v in info.items() if v.get("team_ref"))
    n_vref = sum(1 for k, v in info.items() if k.startswith("vendor:") and v.get("team_ref"))
    print(f"  team BOM refs: {n_ref}/{len(info)} info entries ({n_vref}/{sum(1 for k in info if k.startswith('vendor:'))} "
          f"purchased components, via vendor-parts.csv)")
    if mapped:
        hows = defaultdict(int)
        for o in occ:
            hows[o["how"]] += 1
        print(f"  structural mapping: {dict(hows)}")
    if ambiguous:
        print(f"  {len(ambiguous)} same-named components settled by fit/first choice:")
        print("\n".join(f"    {s}" for s in ambiguous))
    for why, lst in skipped.items():
        print(f"  {len(lst)} occurrences skipped, {why}: {sorted(set(lst))[:8]}{' ...' if len(set(lst)) > 8 else ''}")
    if empty:
        print(f"  {len(empty)} occurrences had no geometry left after cleaning: {empty[:8]}")
    over = []
    for fn, cls in file_cls.items():
        m, _ = store.get(fn, cap_for(fn))
        if m is not None and len(m.faces) > cap_for(fn) * 1.3:
            over.append(f"{fn}: {len(m.faces)} faces for a cap of {cap_for(fn)}")
    if over:
        print(f"  {len(over)} meshes stayed above their cap (topology kept): {over[:8]}")
    if size > 3 * 2**20:
        print(f"WARNING: robot.glb is over 3 MB; lower --total-faces or --qbits, or drop --normals")
    print(f"done in {time.time() - t_start:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
