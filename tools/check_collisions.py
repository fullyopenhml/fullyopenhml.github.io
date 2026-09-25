#!/usr/bin/env python3
"""Self-collision audit of the FOH model.

Three passes:
  zero    exact overlap test of every part pair at the zero pose (all shapes are
          axis-aligned there: box/box, box/cylinder and coaxial cylinder pairs are
          exact; skew cylinder pairs go through bounding boxes and can over-report)
  poses   the preset poses, tested by sampling each shape's surface and asking
          whether the samples lie inside the other solid (rotated boxes and
          cylinders handled exactly per sample; thin slivers between samples can
          be missed, so the tolerance is 1 mm)
  sweep   every joint alone through its range in steps, moving subtree against
          the rest of the robot, same sampled test; reports the worst angle

Pairs declared `inside` in the model (a bearing in its seat, a flange through a
clearance hole, a servo in its housing) are skipped.

Usage:  python3 tools/check_collisions.py [--tol 0.5] [--poses] [--sweep] [--steps 9]
Exit code 1 when the zero pass finds a pair deeper than --tol.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
robot = json.loads((ROOT / "assets/data/robot.json").read_text())
LINKS = {L["id"]: L for L in robot["links"]}
JOINT_BY_CHILD = {J["child"]: J for J in robot["joints"]}
AX = {"x": 0, "y": 1, "z": 2}


# --------------------------------------------------------------------------- zero pose
def shapes_zero():
    out = []
    for L in robot["links"]:
        for P in L["parts"]:
            for k, sh in enumerate(P["shapes"]):
                c = [sh["c"][i] + L["origin"][i] for i in range(3)]
                out.append(dict(occ=P["occ"], link=L["id"], sh=sh, c=c, inside=set(P.get("inside", []))))
    return out


def allowed(a, b):
    return b["occ"] in a["inside"] or a["occ"] in b["inside"]


def half_extents(sh):
    if sh["t"] == "box":
        return [v / 2 for v in sh["s"]]
    h = [sh["r"]] * 3
    h[AX[sh["axis"]]] = sh["l"] / 2
    return h


def aabb(s):
    h = half_extents(s["sh"])
    return [s["c"][i] - h[i] for i in range(3)], [s["c"][i] + h[i] for i in range(3)]


def aabb_pen(a, b):
    (alo, ahi), (blo, bhi) = a, b
    return min(min(ahi[i], bhi[i]) - max(alo[i], blo[i]) for i in range(3))


def rect_annulus_pen(cx, cy, r, ri, rx0, rx1, ry0, ry1):
    nx = min(max(cx, rx0), rx1)
    ny = min(max(cy, ry0), ry1)
    dmin = math.hypot(nx - cx, ny - cy)
    if dmin >= r:
        return r - dmin
    if ri:
        fx = rx0 if abs(rx0 - cx) > abs(rx1 - cx) else rx1
        fy = ry0 if abs(ry0 - cy) > abs(ry1 - cy) else ry1
        dmax = math.hypot(fx - cx, fy - cy)
        if dmax <= ri:
            return dmax - ri
        return min(r - dmin, dmax - ri)
    return r - dmin


def cyl_box_pen(cy, bx):
    C, B = cy["sh"], bx["sh"]
    k = AX[C["axis"]]
    i, j = [m for m in range(3) if m != k]
    along = min(cy["c"][k] + C["l"] / 2, bx["c"][k] + B["s"][k] / 2) - max(cy["c"][k] - C["l"] / 2, bx["c"][k] - B["s"][k] / 2)
    if along <= 0:
        return along
    p = rect_annulus_pen(cy["c"][i], cy["c"][j], C["r"], C.get("ri", 0),
                         bx["c"][i] - B["s"][i] / 2, bx["c"][i] + B["s"][i] / 2,
                         bx["c"][j] - B["s"][j] / 2, bx["c"][j] + B["s"][j] / 2)
    return min(along, p)


def as_box(s):
    return dict(sh={"t": "box", "s": [h * 2 for h in half_extents(s["sh"])]}, c=s["c"])


def pen_zero(a, b):
    A, B = a["sh"], b["sh"]
    if A["t"] == "box" and B["t"] == "box":
        return aabb_pen(aabb(a), aabb(b))
    if A["t"] == "cyl" and B["t"] == "box":
        return cyl_box_pen(a, b)
    if A["t"] == "box" and B["t"] == "cyl":
        return cyl_box_pen(b, a)
    if A["axis"] == B["axis"]:
        k = AX[A["axis"]]
        along = min(a["c"][k] + A["l"] / 2, b["c"][k] + B["l"] / 2) - max(a["c"][k] - A["l"] / 2, b["c"][k] - B["l"] / 2)
        if along <= 0:
            return along
        i, j = [m for m in range(3) if m != k]
        d = math.hypot(a["c"][i] - b["c"][i], a["c"][j] - b["c"][j])
        ra, ria, rb, rib = A["r"], A.get("ri", 0), B["r"], B.get("ri", 0)
        radial = ra + rb - d
        if radial <= 0:
            return min(along, radial)
        if ria and d + rb <= ria:
            return min(along, d + rb - ria)
        if rib and d + ra <= rib:
            return min(along, d + ra - rib)
        return min(along, radial)
    return min(cyl_box_pen(a, as_box(b)), cyl_box_pen(b, as_box(a)))


def pass_zero(tol):
    shapes = shapes_zero()
    boxes = [aabb(s) for s in shapes]
    seen = {}
    for (ia, a), (ib, b) in itertools.combinations(enumerate(shapes), 2):
        if a["occ"] == b["occ"] or allowed(a, b):
            continue
        if aabb_pen(boxes[ia], boxes[ib]) <= tol:
            continue
        p = pen_zero(a, b)
        if p > tol:
            key = tuple(sorted((a["occ"], b["occ"])))
            seen[key] = max(seen.get(key, 0), p)
    print(f"Zero pose: {len(shapes)} shapes, tolerance {tol} mm")
    for (o1, o2), p in sorted(seen.items(), key=lambda kv: -kv[1]):
        print(f"  {p:6.1f} mm  {o1}  <->  {o2}")
    print(f"  {len(seen)} overlapping pairs" if seen else "  no overlaps")
    return len(seen)


# --------------------------------------------------------------------------- posed passes
def q_axis(axis, deg):
    a = math.radians(deg) / 2
    n = math.sqrt(sum(v * v for v in axis))
    s = math.sin(a) / n
    return (math.cos(a), axis[0] * s, axis[1] * s, axis[2] * s)


def q_mul(p, q):
    w1, x1, y1, z1 = p
    w2, x2, y2, z2 = q
    return (w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2)


def q_mat(q):
    w, x, y, z = q
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]


def mat_vec(R, v):
    return [R[0][0] * v[0] + R[0][1] * v[1] + R[0][2] * v[2],
            R[1][0] * v[0] + R[1][1] * v[1] + R[1][2] * v[2],
            R[2][0] * v[0] + R[2][1] * v[1] + R[2][2] * v[2]]


def mat_t_vec(R, v):
    return [R[0][0] * v[0] + R[1][0] * v[1] + R[2][0] * v[2],
            R[0][1] * v[0] + R[1][1] * v[1] + R[2][1] * v[2],
            R[0][2] * v[0] + R[1][2] * v[1] + R[2][2] * v[2]]


def link_frames(q_by_joint):
    frames = {}

    def frame(lid):
        if lid in frames:
            return frames[lid]
        J = JOINT_BY_CHILD.get(lid)
        if not J:
            frames[lid] = ([0.0, 0.0, 0.0], (1.0, 0.0, 0.0, 0.0))
            return frames[lid]
        pp, pq = frame(J["parent"])
        parent = LINKS[J["parent"]]
        off = [J["origin"][i] - parent["origin"][i] for i in range(3)]
        R = q_mat(pq)
        pos = [pp[i] + v for i, v in enumerate(mat_vec(R, off))]
        q = q_mul(pq, q_axis(J["axis"], q_by_joint.get(J["id"], 0.0)))
        frames[lid] = (pos, q)
        return frames[lid]

    for lid in LINKS:
        frame(lid)
    return frames


_sample_cache = {}


def samples_local(sh):
    """Surface sample points of a shape in its own (unrotated) frame, about its centre."""
    key = json.dumps([sh["t"], sh.get("s"), sh.get("axis"), sh.get("r"), sh.get("ri"), sh.get("l")])
    if key in _sample_cache:
        return _sample_cache[key]
    pts = []
    if sh["t"] == "box":
        h = [v / 2 for v in sh["s"]]
        n = 5
        grid = [-1 + 2 * t / (n - 1) for t in range(n)]
        for axis in range(3):
            for sign in (-1, 1):
                for u in grid:
                    for v in grid:
                        p = [0, 0, 0]
                        o = [m for m in range(3) if m != axis]
                        p[axis] = sign * h[axis]
                        p[o[0]] = u * h[o[0]]
                        p[o[1]] = v * h[o[1]]
                        pts.append(p)
    else:
        k = AX[sh["axis"]]
        i, j = [m for m in range(3) if m != k]
        r, ri, hl = sh["r"], sh.get("ri", 0), sh["l"] / 2
        nang = 32
        for t in range(nang):
            ang = 2 * math.pi * t / nang
            for rad in ([r, ri] if ri else [r]):
                for z in (-hl, 0, hl):
                    p = [0, 0, 0]
                    p[i] = rad * math.cos(ang)
                    p[j] = rad * math.sin(ang)
                    p[k] = z
                    pts.append(p)
        if not ri:
            for z in (-hl, hl):
                for rad in (r * 0.5,):
                    for t in range(8):
                        ang = 2 * math.pi * t / 8
                        p = [0, 0, 0]
                        p[i] = rad * math.cos(ang)
                        p[j] = rad * math.sin(ang)
                        p[k] = z
                        pts.append(p)
                p = [0, 0, 0]
                p[k] = z
                pts.append(p)
    _sample_cache[key] = pts
    return pts


def depth_in(sh, local):
    """How deep a point (in the shape's own frame, about its centre) lies inside the solid; <= 0 outside."""
    if sh["t"] == "box":
        return min(sh["s"][i] / 2 - abs(local[i]) for i in range(3))
    k = AX[sh["axis"]]
    i, j = [m for m in range(3) if m != k]
    radial = math.hypot(local[i], local[j])
    d = min(sh["l"] / 2 - abs(local[k]), sh["r"] - radial)
    if sh.get("ri"):
        d = min(d, radial - sh["ri"])
    return d


def shapes_posed(q_by_joint):
    frames = link_frames(q_by_joint)
    out = []
    for L in robot["links"]:
        pos, q = frames[L["id"]]
        R = q_mat(q)
        for P in L["parts"]:
            for sh in P["shapes"]:
                c = [pos[i] + v for i, v in enumerate(mat_vec(R, sh["c"]))]
                out.append(dict(occ=P["occ"], link=L["id"], sh=sh, c=c, R=R, inside=set(P.get("inside", []))))
    return out


def world_aabb(s):
    h = half_extents(s["sh"])
    R = s["R"]
    e = [sum(abs(R[i][k]) * h[k] for k in range(3)) for i in range(3)]
    return [s["c"][i] - e[i] for i in range(3)], [s["c"][i] + e[i] for i in range(3)]


def pen_sampled(a, b):
    """Max depth of a's surface samples inside b, and b's inside a."""
    best = -1e9
    for src, dst in ((a, b), (b, a)):
        Rs, Rd = src["R"], dst["R"]
        for p in samples_local(src["sh"]):
            w = [src["c"][i] + v for i, v in enumerate(mat_vec(Rs, p))]
            local = mat_t_vec(Rd, [w[i] - dst["c"][i] for i in range(3)])
            d = depth_in(dst["sh"], local)
            if d > best:
                best = d
    return best


def pairs_posed(shapes, tol, only_between=None):
    boxes = [world_aabb(s) for s in shapes]
    hits = {}
    for (ia, a), (ib, b) in itertools.combinations(enumerate(shapes), 2):
        if a["occ"] == b["occ"] or a["link"] == b["link"] or allowed(a, b):
            continue
        if only_between and not ((a["link"] in only_between) != (b["link"] in only_between)):
            continue
        if aabb_pen(boxes[ia], boxes[ib]) <= tol:
            continue
        p = pen_sampled(a, b)
        if p > tol:
            key = tuple(sorted((a["occ"], b["occ"])))
            hits[key] = max(hits.get(key, 0), p)
    return hits


def pass_poses(tol):
    for name, pose in robot["poses"].items():
        if not pose["q"]:
            continue
        hits = pairs_posed(shapes_posed(pose["q"]), tol)
        print(f"Pose '{name}': {len(hits)} pairs deeper than {tol} mm")
        for (o1, o2), p in sorted(hits.items(), key=lambda kv: -kv[1])[:15]:
            print(f"  {p:6.1f} mm  {o1}  <->  {o2}")


def subtree(link_id):
    out = {link_id}
    changed = True
    while changed:
        changed = False
        for J in robot["joints"]:
            if J["parent"] in out and J["child"] not in out:
                out.add(J["child"])
                changed = True
    return out


def pass_sweep(tol, steps):
    print(f"Joint sweep: each joint alone through its range in {steps} steps, moving subtree vs the rest, tolerance {tol} mm")
    total = 0
    for J in robot["joints"]:
        if J["side"] == "R":
            continue  # mirror of the left side
        lo, hi = J["limits"]
        moving = subtree(J["child"])
        worst = {}
        for t in range(steps):
            ang = lo + (hi - lo) * t / (steps - 1)
            hits = pairs_posed(shapes_posed({J["id"]: ang}), tol, only_between=moving)
            for key, p in hits.items():
                if p > worst.get(key, (0, 0))[0]:
                    worst[key] = (p, ang)
        if worst:
            total += len(worst)
            print(f"  {J['id']} ({lo}..{hi} deg): {len(worst)} pairs")
            for (o1, o2), (p, ang) in sorted(worst.items(), key=lambda kv: -kv[1][0])[:8]:
                print(f"     {p:6.1f} mm at {ang:6.1f} deg  {o1}  <->  {o2}")
        else:
            print(f"  {J['id']} ({lo}..{hi} deg): clear")
    return total


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tol", type=float, default=0.5)
    ap.add_argument("--poses", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--steps", type=int, default=9)
    args = ap.parse_args()
    bad = pass_zero(args.tol)
    if args.poses:
        pass_poses(max(args.tol, 1.0))
    if args.sweep:
        pass_sweep(max(args.tol, 1.0), args.steps)
    sys.exit(1 if bad else 0)
