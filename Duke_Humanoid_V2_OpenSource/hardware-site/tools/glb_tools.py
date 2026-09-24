"""GLB writer with Draco-compressed primitives for the part viewer (tools/build_viewer.py).

Grown out of cad/_scratch/reencode_glb.py: pure numpy + DracoPy, no trimesh in the writer.

* Positions go through Draco (KHR_draco_mesh_compression, edgebreaker, quantised to
  `qbits` over each mesh's bounding cube, compression level `level`). model-viewer
  fetches the decoder from Google's CDN by default.
* Smooth shading needs vertex normals. DracoPy cannot quantise a NORMAL attribute
  (it is stored as raw float32, 8x the size of the positions) and only accepts
  unsigned or float generic attributes, so the normals travel outside the Draco
  stream as a plain glTF accessor of normalised int8 (KHR_mesh_quantization allows
  that; three.js loads the accessors the Draco attribute map does not list, see
  GLTFLoader.addPrimitiveAttributes). That accessor must follow the vertex order
  the Draco *decoder* produces, which edgebreaker changes, so every blob is decoded
  once here (DracoPy) and the normals are permuted to match.
* Vertices split along sharp edges (same position, different normal) would be
  merged by the Draco encoder's point deduplication. A one-byte generic attribute,
  the vertex's rank among the vertices sharing its position, keeps them apart at
  about 0.25 B/vertex and doubles as the key that pairs decoded and input vertices.
  With that attribute present DracoPy no longer gives POSITION unique id 0, so the
  id is read back from the decoded blob.
* A primitive without normals is flat-shaded by three.js (GLTFLoader sets
  flatShading when NORMAL is missing); used for the merged hardware meshes.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

import DracoPy
import numpy as np
from scipy.spatial import cKDTree

GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER = 34962, 34963
DRACO_POSITION = 0            # draco::GeometryAttribute::POSITION
RANK_UID = 1                  # unique id of the split-rank generic attribute
CHUNK_JSON, CHUNK_BIN = 0x4E4F534A, 0x004E4942


def srgb_to_linear(rgb255) -> list[float]:
    """sRGB 0-255 (Fusion appearance colour) -> linear 0..1 for glTF baseColorFactor."""
    c = np.asarray(rgb255, dtype=float) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return [round(float(x), 4) for x in lin]


def pbr_material(name: str, rgb_linear, metallic: float, roughness: float,
                 double_sided: bool = True) -> dict:
    m = {"name": name,
         "pbrMetallicRoughness": {"baseColorFactor": [float(rgb_linear[0]), float(rgb_linear[1]),
                                                      float(rgb_linear[2]), 1.0],
                                  "metallicFactor": round(float(metallic), 3),
                                  "roughnessFactor": round(float(roughness), 3)}}
    if double_sided:
        m["doubleSided"] = True
    return m


def split_ranks(V: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """For vertices that may share exact positions: (merged id per vertex, rank of the
    vertex among those sharing its position, merged positions)."""
    Vm, inv = np.unique(V, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    n = len(V)
    order = np.argsort(inv, kind="stable")
    si = inv[order]
    starts = np.r_[0, np.flatnonzero(np.diff(si)) + 1]
    group_start = np.repeat(starts, np.diff(np.r_[starts, n]))
    rank = np.empty(n, np.int64)
    rank[order] = np.arange(n) - group_start
    return inv, rank, Vm


def encode_draco(V: np.ndarray, F: np.ndarray, normals: np.ndarray | None = None,
                 qbits: int = 14, level: int = 10) -> dict:
    """Draco-encode a triangle mesh. Returns dict(blob, n_points, n_faces, position_uid,
    normals_i8 (n_points, 3) int8 or None, unmatched, index16)."""
    V = np.ascontiguousarray(V, dtype=np.float32)
    F = np.ascontiguousarray(F, dtype=np.uint32)
    generic = None
    if normals is not None:
        inv, rank, Vm = split_ranks(V)
        if rank.max() > 255:
            raise ValueError("more than 256 vertices share one position")
        generic = {RANK_UID: rank.astype(np.uint8).reshape(-1, 1)}
    blob = DracoPy.encode(V, F, quantization_bits=qbits, compression_level=level,
                          generic_attributes=generic)
    d = DracoPy.decode(blob)
    pos_uid = next(a["unique_id"] for a in d.attributes if a["attribute_type"] == DRACO_POSITION)
    n_points, n_faces = len(d.points), len(d.faces)
    out = {"blob": blob, "n_points": n_points, "n_faces": n_faces, "position_uid": int(pos_uid),
           "normals_i8": None, "unmatched": 0,
           "pmin": [round(float(x) - 1e-5, 5) for x in d.points.min(axis=0)],
           "pmax": [round(float(x) + 1e-5, 5) for x in d.points.max(axis=0)]}
    if normals is None:
        return out
    # Pair every decoded point with its input vertex: nearest merged position + rank.
    rk = np.asarray(d.get_attribute_by_unique_id(RANK_UID)["data"]).reshape(-1).astype(np.int64)
    dist, mid = cKDTree(Vm).query(d.points, workers=-1)
    key_in = inv.astype(np.int64) * 256 + rank
    order = np.argsort(key_in)
    sk = key_in[order]
    key_out = mid.astype(np.int64) * 256 + rk
    pos = np.clip(np.searchsorted(sk, key_out), 0, len(sk) - 1)
    found = sk[pos] == key_out
    src = order[pos]
    # Fallback for a decoded point whose (position, rank) pair is missing (a vertex the
    # encoder split or merged): any input vertex at that position.
    first_of_group = np.full(len(Vm), -1, np.int64)
    first_of_group[inv[order[::-1]]] = order[::-1]
    src = np.where(found, src, first_of_group[mid])
    extent = float(np.max(np.ptp(V, axis=0))) or 1.0
    far = dist > 4.0 * extent / ((1 << qbits) - 1) + 1e-7
    out["unmatched"] = int((~found).sum() + far.sum())
    N = np.asarray(normals, dtype=np.float64)[src]
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
    out["normals_i8"] = np.clip(np.round(N * 127.0), -127, 127).astype(np.int8)
    return out


class GlbWriter:
    """Minimal glTF 2.0 binary writer: one node per mesh, one material per primitive."""

    def __init__(self, generator: str = "build_viewer.py"):
        self.generator = generator
        self.bin = bytearray()
        self.bufferViews: list[dict] = []
        self.accessors: list[dict] = []
        self.meshes: list[dict] = []
        self.nodes: list[dict] = []
        self.materials: list[dict] = []
        self.ext_used = {"KHR_draco_mesh_compression"}
        self.ext_req = {"KHR_draco_mesh_compression"}
        self.stats = {"meshes": 0, "faces": 0, "points": 0, "draco_bytes": 0, "normal_bytes": 0, "unmatched": 0}

    def add_bv(self, raw: bytes, target: int | None = None, stride: int | None = None) -> int:
        while len(self.bin) % 4:
            self.bin += b"\0"
        bv = {"buffer": 0, "byteOffset": len(self.bin), "byteLength": len(raw)}
        if target:
            bv["target"] = target
        if stride:
            bv["byteStride"] = stride
        self.bin += raw
        self.bufferViews.append(bv)
        return len(self.bufferViews) - 1

    def add_acc(self, **a) -> int:
        self.accessors.append(a)
        return len(self.accessors) - 1

    def add_material(self, material: dict) -> int:
        self.materials.append(material)
        return len(self.materials) - 1

    def add_mesh(self, name: str, material: dict, prims: list[tuple], qbits: int = 14, level: int = 10,
                 extras: dict | None = None) -> dict:
        """Draco-compressed mesh as its own node (node, mesh and material all called
        `name`). prims: [(V, F, normals-or-None), ...] — V in metres (glTF axes), F (n, 3)
        uint32; a primitive without normals is flat-shaded. All primitives share the one
        material, so the viewer still sees one material per mesh. Returns summed stats."""
        mat = self.add_material(material)
        out_prims, faces, points, blob_bytes, unmatched = [], 0, 0, 0, 0
        for V, F, normals in prims:
            if len(F) == 0:
                continue
            enc = encode_draco(V, F, normals, qbits, level)
            bv = self.add_bv(enc["blob"])
            n = enc["n_points"]
            pa = self.add_acc(componentType=5126, count=n, type="VEC3", min=enc["pmin"], max=enc["pmax"])
            ia = self.add_acc(componentType=5123 if n < 65536 else 5125, count=enc["n_faces"] * 3, type="SCALAR")
            prim = {"attributes": {"POSITION": pa}, "indices": ia, "material": mat,
                    "extensions": {"KHR_draco_mesh_compression": {"bufferView": bv,
                                                                  "attributes": {"POSITION": enc["position_uid"]}}}}
            if enc["normals_i8"] is not None:
                self.ext_used.add("KHR_mesh_quantization")
                self.ext_req.add("KHR_mesh_quantization")
                padded = np.zeros((n, 4), np.int8)
                padded[:, :3] = enc["normals_i8"]
                raw = padded.tobytes()
                nbv = self.add_bv(raw, GL_ARRAY_BUFFER, stride=4)
                prim["attributes"]["NORMAL"] = self.add_acc(bufferView=nbv, componentType=5120, count=n,
                                                            type="VEC3", normalized=True)
                self.stats["normal_bytes"] += len(raw)
            out_prims.append(prim)
            faces += enc["n_faces"]
            points += n
            blob_bytes += len(enc["blob"])
            unmatched += enc["unmatched"]
        if not out_prims:
            self.materials.pop()
            return {"n_faces": 0, "n_points": 0, "prims": 0}
        mesh = {"name": name, "primitives": out_prims}
        if extras:
            mesh["extras"] = extras
        self.meshes.append(mesh)
        self.nodes.append({"name": name, "mesh": len(self.meshes) - 1})
        self.stats["meshes"] += 1
        self.stats["faces"] += faces
        self.stats["points"] += points
        self.stats["draco_bytes"] += blob_bytes
        self.stats["unmatched"] += unmatched
        return {"n_faces": faces, "n_points": points, "prims": len(out_prims)}

    def write(self, path: Path | str, extras: dict | None = None) -> int:
        g = {"asset": {"version": "2.0", "generator": self.generator},
             "scene": 0, "scenes": [{"name": "robot", "nodes": list(range(len(self.nodes)))}],
             "nodes": self.nodes, "meshes": self.meshes, "materials": self.materials,
             "accessors": self.accessors, "bufferViews": self.bufferViews,
             "buffers": [{"byteLength": len(self.bin)}],
             "extensionsUsed": sorted(self.ext_used), "extensionsRequired": sorted(self.ext_req)}
        if extras:
            g["asset"]["extras"] = extras
        js = json.dumps(g, separators=(",", ":")).encode()
        js += b" " * (-len(js) % 4)
        bin_ = bytes(self.bin) + b"\0" * (-len(self.bin) % 4)
        out = struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(js) + 8 + len(bin_))
        out += struct.pack("<II", len(js), CHUNK_JSON) + js + struct.pack("<II", len(bin_), CHUNK_BIN) + bin_
        Path(path).write_bytes(out)
        return len(out)


def read_glb_json(path: Path | str) -> dict:
    """The JSON chunk of a GLB (for checks and reports)."""
    data = Path(path).read_bytes()
    off = 12
    while off < len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        if ctype == CHUNK_JSON:
            return json.loads(data[off + 8: off + 8 + clen])
        off += 8 + clen
    raise ValueError(f"{path}: no JSON chunk")
