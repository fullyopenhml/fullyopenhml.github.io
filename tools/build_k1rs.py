#!/usr/bin/env python3
"""FOH v2 (work in progress): ROBOTIS AI Sapiens K1 as the design, cheaper parts inside.

Instead of drawing our own body (v1a, retired), this takes a published open-hardware humanoid whose look we want
(AI Sapiens K1: hardware CERN-OHL-P-2.0, software Apache-2.0, docs CC BY 4.0) and keeps its design: the shells,
the proportions, the 23-joint kinematics. What changes is the expensive content: DYNAMIXEL-Q actuators (not yet
on sale, 48 V, RS-485) become RobStride CAN actuators, the Jetson Orin NX becomes the N100 mini PC and CAN
electronics of our v1, the aluminium frame becomes printed brackets where the loads allow, the rubber hands are
printed in TPU from the published hand mesh.

The one hard question is whether a cheaper actuator fits the K1's housings. This script reads the K1 URDF and
meshes (the STLs contain the actuators themselves, so the skin around every joint is measurable), measures the
skin's inscribed radius along each joint axis, and for every joint lists which RobStride model fits the K1
actuator's envelope and which needs the shell to grow, with two variants: shape-first (smallest growth) and
torque-first (closest torque). Everything is written to assets/data/k1rs.json for aesthetic.html.

Run:  tools/.venv/bin/python tools/build_k1rs.py        (needs trimesh + rtree in the venv)
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
OUT = ROOT / "assets/data/k1rs.json"
PRICED_AS_OF = "2026-10"
WALL = 3.0          # mm of printed housing wall around an actuator body, as in our joint kits

# --------------------------------------------------------------------------- the K1, from its published description and docs
K1 = dict(
    name="ROBOTIS AI Sapiens K1 (rev 1)", height_mm=1355, mass_kg=35.0, dof=23, arm_dof=5, leg_dof=6, waist_dof=1,
    computer="NVIDIA Jetson Orin NX 16 GB", battery="46.8 V, 9000 mAh (published for the K0 generation)", bus="RS-485, 6 Mbit/s", frame="aluminium alloy", covers="polymer",
    price_usd=[7000, 8700], price_note="announced at 'mid-to-low 10 million KRW'; the DYNAMIXEL-Q actuators themselves are listed for Q1 2027 without a price",
    licence=dict(hardware="CERN-OHL-P-2.0", software="Apache-2.0", documentation="CC BY 4.0"),
    published=["URDF and STL meshes (ai_sapiens_description)", "MJCF model", "hardware drawing (PDF)", "ROS 2 bring-up, controllers, hardware interface", "walking, squat and dance policies (ONNX)"],
    coming_soon=["hardware bill of materials", "STEP files", "3D-printable covers", "USD models"],
    sources=[
        ("ai_sapiens repository", "https://github.com/ROBOTIS-GIT/ai_sapiens"),
        ("AI Sapiens K1 hardware specifications", "https://docs.robotis.com/docs/systems/aisapiens/specifications/hardware"),
        ("AI Sapiens open source resources and licences", "https://docs.robotis.com/docs/systems/aisapiens/resources/open_source"),
        ("DYNAMIXEL-Q lineup", "https://robotis.us/collections/dynamixel-q"),
        ("Launch coverage with the price range", "https://robohorizon.com/en-gb/news/2026/04/robotis-crashes-humanoid-party-with-sub-9000-ai-sapiens/"),
    ],
)
QC = {
    "QC060": dict(name="DYNAMIXEL-Q QC060-200-R020-RE", dia=58, length=60, mass_g=455, peak_nm=30.0, rated_nm=10.6, rpm=200, ratio="20:1", power_w=200, qty=12),
    "QC080": dict(name="DYNAMIXEL-Q QC080-240-R020-RE", dia=78, length=65, mass_g=865, peak_nm=72.6, rated_nm=24.2, rpm=110, ratio="20:1", power_w=240, qty=11),
}
# RobStride, from our interface table (measured from the manuals, see build_data.py); housing length = what our joint kit wraps around the body
RS_SRC = json.loads((ROOT / "assets/data/robot_v1.json").read_text())["actuators"]
RS = {}
for k in ("RS04", "RS03", "RS06", "RS02", "RS05"):
    a = RS_SRC[k]
    RS[k] = dict(name=a["name"], dia=2 * a["body_r"], length=a["lug_t"] + a["body_l"] + a["cover_l"], kit_length=a["lug_t"] + a["body_l"] + a["cover_l"] + a["back_t"] + a["mount_t"] + a["sh_t"],
                 mass_g=a["mass_g"], peak_nm=a["peak_nm"], rated_nm=a["rated_nm"], price=a["price"], ratio=a["ratio"], url=a.get("url", ""))

# --------------------------------------------------------------------------- the K1 model
URDF = "https://raw.githubusercontent.com/ROBOTIS-GIT/ai_sapiens/main/ai_sapiens_description/urdf/k1_rev1/k1.urdf"
MESHES = "https://raw.githubusercontent.com/ROBOTIS-GIT/ai_sapiens/main/ai_sapiens_description/meshes/k1_rev1"
u = bg.Urdf(URDF, MESHES, "ref-k1")
mesh = {l: trimesh.util.concatenate(u.link_meshes(l)) for l in u.links if u.link_meshes(l)}
mass = {l: float(u.links[l].find("inertial/mass").get("value")) for l in u.links}
GROUND = min(m.bounds[0][2] for m in mesh.values())
HEIGHT = max(m.bounds[1][2] for m in mesh.values()) - GROUND
caster = {l: trimesh.ray.ray_triangle.RayMeshIntersector(m) for l, m in mesh.items()}


def far_hits(ri, P, D):
    """Distance to the farthest intersection along each ray: the outer skin, past the internal parts the STLs contain."""
    locs, idx_ray, _ = ri.intersects_location(P, D, multiple_hits=True)
    d = np.zeros(len(P))
    for L, r in zip(locs, idx_ray):
        d[r] = max(d[r], np.linalg.norm(L - P[r]))
    return d


def radial_frame(a):
    e1 = np.cross(a, [0, 0, 1.0])
    if np.linalg.norm(e1) < 1e-6:
        e1 = np.cross(a, [0, 1.0, 0])
    e1 /= np.linalg.norm(e1)
    return e1, np.cross(a, e1)


def inscribed_profile(link, o, a, stations, n=48):
    """Inscribed radius of the link's skin around axis (o, a) at each station (mm along the axis): the smallest outer-skin distance over n directions."""
    e1, e2 = radial_frame(a)
    dirs = np.array([math.cos(t) * e1 + math.sin(t) * e2 for t in np.linspace(0, 2 * math.pi, n, endpoint=False)])
    out = {}
    for s in stations:
        p = o + a * (s / 1000)
        d = far_hits(caster[link], np.repeat(p[None], n, 0), dirs) * 1000
        out[s] = float(np.min(d)) if np.all(d > 0) else 0.0
    return out


def group_of(jn):
    side = "L" if jn.startswith("left_") else "R" if jn.startswith("right_") else "C"
    g = jn.replace("left_", "").replace("right_", "").replace("_joint", "")
    return side, g


STATIONS = list(range(-40, 41, 5))
joints = []
print(f"K1: {len(u.links)} links, height {HEIGHT*1000:.0f} mm, URDF mass {sum(mass.values()):.2f} kg, ground z {GROUND:.4f}")
for jn, j in u.joints.items():
    if j.get("type") != "revolute":
        continue
    parent, child = j.find("parent").get("link"), j.find("child").get("link")
    T = u.T[child]
    o = T[:3, 3]
    a = T[:3, :3] @ np.array([float(v) for v in j.find("axis").get("xyz").split()])
    a /= np.linalg.norm(a)
    lim = j.find("limit")
    eff = float(lim.get("effort"))
    k1a = "QC080" if eff > 60 else "QC060"
    side, group = group_of(jn)
    prof = {who: inscribed_profile(L, o, a, STATIONS) for who, L in (("parent", parent), ("child", child))}
    housing_link, housing_r, housing_s = max(((who, r, s) for who in prof for s, r in prof[who].items()), key=lambda t: t[1])
    # skin extent along the axis through the joint (rays along +-axis from 8 points 10 mm off the axis, against both links)
    e1, e2 = radial_frame(a)
    P = np.array([o + 0.01 * (math.cos(t) * e1 + math.sin(t) * e2) for t in np.linspace(0, 2 * math.pi, 8, endpoint=False)])
    both = trimesh.ray.ray_triangle.RayMeshIntersector(trimesh.util.concatenate([mesh[parent], mesh[child]]))
    plus = float(np.min(far_hits(both, P, np.repeat(a[None], 8, 0)))) * 1000
    minus = float(np.min(far_hits(both, P, np.repeat(-a[None], 8, 0)))) * 1000
    linkage = group.startswith("ankle")        # the K1 ankle: both axes meet at the ankle, no room for a body there, the shank link carries 2.5 kg
    joints.append(dict(id=jn, side=side, group=group, parent=parent, child=child, k1_actuator=k1a, effort_urdf=eff,
                       origin=[round(float(v), 4) for v in (o - [0, 0, GROUND])], axis=[round(float(v), 3) for v in a],
                       limits_deg=[round(math.degrees(float(lim.get("lower"))), 1), round(math.degrees(float(lim.get("upper"))), 1)],
                       housing=dict(link=housing_link, r_mm=round(housing_r, 1), at_mm=housing_s), axial_room_mm=[round(minus, 1), round(plus, 1)], linkage=linkage))
    print(f"  {jn:28s} {k1a} housing skin r {housing_r:5.1f} mm ({housing_link} at {housing_s:+d}); along axis -{minus:.0f}..+{plus:.0f} mm")

# ankle actuators live in the shank: where along the shank is there room, and how much?
shank = {}
for side, S in (("L", "left"), ("R", "right")):
    knee = next(J for J in joints if J["id"] == f"{S}_knee_joint")
    ankle = next(J for J in joints if J["id"] == f"{S}_ankle_pitch_joint")
    o = np.array(knee["origin"]) + [0, 0, GROUND]
    oa = np.array(ankle["origin"]) + [0, 0, GROUND]
    a = (oa - o) / np.linalg.norm(oa - o)
    L = np.linalg.norm(oa - o) * 1000
    prof = inscribed_profile(knee["child"], o, a, list(range(20, int(L) - 20, 10)))
    best_s, best_r = max(prof.items(), key=lambda kv: kv[1])
    shank[side] = dict(link=knee["child"], length_mm=round(L, 1), profile={s: round(r, 1) for s, r in prof.items()}, best=dict(at_mm=best_s, r_mm=round(best_r, 1)),
                       axis=[round(float(v), 3) for v in a], origin=knee["origin"])
    print(f"  shank {side}: {L:.0f} mm knee to ankle, skin r {best_r:.1f} mm at {best_s} mm below the knee; profile {[round(r) for r in prof.values()]}")

# --------------------------------------------------------------------------- the swap
def fit(model, k1a, J):
    """How a RobStride model sits in the K1 actuator's place: growth of the shell radius needed (mm, 0 = fits), and length against the K1 part."""
    q, r = QC[k1a], RS[model]
    growth = max(0.0, (r["dia"] - q["dia"]) / 2)
    return dict(growth_mm=round(growth, 2), fits=growth == 0, length_mm=r["length"], length_ok=r["length"] <= q["length"] + 10,
                torque_ratio=round(r["peak_nm"] / q["peak_nm"], 2), rated_ratio=round(r["rated_nm"] / q["rated_nm"], 2))


SHAPE_FIRST = {"QC080": "RS06", "QC060": "RS02"}     # smallest shell growth at a torque worth having (RS05 fits everywhere but gives 5.5 N·m)
TORQUE_FIRST = {"QC080": "RS03", "QC060": "RS06"}    # the RobStride whose peak is closest to the DYNAMIXEL-Q's
for J in joints:
    J["candidates"] = {m: fit(m, J["k1_actuator"], J) for m in RS}
    J["shape_first"] = SHAPE_FIRST[J["k1_actuator"]]
    J["torque_first"] = TORQUE_FIRST[J["k1_actuator"]]


def variant(pick):
    counts, m, cost, growth, ratios = {}, 0, 0.0, 0.0, []
    for J in joints:
        model = J[pick]
        counts[model] = counts.get(model, 0) + 1
        m += RS[model]["mass_g"]; cost += RS[model]["price"]
        c = J["candidates"][model]
        growth = max(growth, c["growth_mm"]); ratios.append(c["torque_ratio"])
    return dict(counts=counts, actuator_mass_g=m, actuator_cost=round(cost, 2), shell_growth_max_mm=growth, torque_ratio_min=min(ratios), torque_ratio_max=max(ratios),
                leg_peak_nm=RS[TORQUE_FIRST["QC080"] if pick == "torque_first" else SHAPE_FIRST["QC080"]]["peak_nm"],
                arm_peak_nm=RS[TORQUE_FIRST["QC060"] if pick == "torque_first" else SHAPE_FIRST["QC060"]]["peak_nm"])


variants = {"shape_first": variant("shape_first"), "torque_first": variant("torque_first")}
k1_act_mass = sum(QC[k]["mass_g"] * QC[k]["qty"] for k in QC)
k1_mass_urdf = sum(mass.values())

# --------------------------------------------------------------------------- what else changes: shells, hands, frame, electronics
# printed shells: outer skin area estimated from each link's convex hull (the STLs merge skin and internals, so their own area overstates)
shells = {}
for l, m in mesh.items():
    hull_area = float(m.convex_hull.area)
    shells[l] = dict(hull_area_cm2=round(hull_area * 1e4, 1), mass_g=round(hull_area * 1e4 * 0.16 * 1.24))     # 1.6 mm PLA wall, 1.24 g/cm3
shell_mass = sum(v["mass_g"] for l, v in shells.items() if "hand" not in l)
hand_mass = sum(mass[l] for l in mass if "hand" in l)
bom1 = json.loads((ROOT / "assets/data/bom_v1.json").read_text())
sec1 = {s["id"]: s for s in bom1["sections"]}


def row(pid, desc, qty, unit, vendor="", url="", notes="", unit_label="ea"):
    return dict(id=pid, part_id=pid, description=desc, qty=qty, unit_cost=unit, total=round(qty * unit, 2), vendor=vendor, url=url, notes=notes, unit_label=unit_label)


def act_rows(pick):
    rows = []
    for model, n in sorted(variants[pick]["counts"].items(), key=lambda kv: -RS[kv[0]]["peak_nm"]):
        js = sorted({J["group"] for J in joints if J[pick] == model})
        rows.append(row("ACT_" + model, f"{RS[model]['name']} ({RS[model]['peak_nm']} N·m peak)", n, RS[model]["price"], "RobStride / Amazon US / AiFitLab", RS[model]["url"], "Joints: " + ", ".join(js)))
    return rows


sections_common = [
    dict(id="electronics", title="Electronics", tier="core", blurb="Our v1 electronics in place of the K1's: an N100 mini PC instead of the Jetson Orin NX 16 GB (the published policies are ONNX files a CPU runs at control rate), four CAN buses instead of the RS-485 bus, two 6S packs for the K1's 46.8 V pack. The K1's camera set is not published; the RealSense stays optional.", rows=sec1["electronics"]["rows"]),
    dict(id="harness", title="Harness", tier="core", blurb=sec1["harness"]["blurb"], rows=sec1["harness"]["rows"]),
    dict(id="hands", title="Hands", tier="core", blurb="The K1's hands are passive rubber hands; their mesh is published, so they print in TPU.", rows=[row("3DP_K1_HAND", "K1 rubber hand, printed in TPU 95A from the published mesh (pair)", 1, 28.0, "filament", "", f"About {hand_mass*1000:.0f} g the pair in the K1 model.")]),
    dict(id="structure", title="Structure and covers", tier="core",
         blurb=f"The K1 skin printed as 1.6 mm PLA shells from the published link meshes, about {shell_mass/1000:.1f} kg by convex-hull area; the aluminium frame kept where the drawings show it carrying the leg loads and printed in PETG-CF elsewhere. Until ROBOTIS publishes the STEP files and BOM, the frame is a placeholder figure.",
         rows=[row("MAT_PLA_SHELL", "PLA filament for the shells, 1 kg spool", math.ceil(shell_mass * 1.35 / 1000 * 2) / 2, 20.0, "Any", "", "35 % for supports and failed prints.", unit_label="kg"),
               row("MAT_PETG_CF_FRAME", "PETG-CF filament for printed brackets, 1 kg spool", 3.0, 30.0, "Bambu / Polymaker / Overture", "", "Estimate: the actuator cups and brackets of our joint kits, re-made to the K1's joint positions.", unit_label="kg"),
               row("AL_FRAME_K1", "Aluminium frame parts kept from the K1 (laser-cut plates, extrusion)", 1, 250.0, "SendCutSend / Misumi", "", "Placeholder estimate until the K1 STEP files are published; the drawings give dimensions only."),
               row("HW_ASSORT", "Bearings, screws, inserts, dowels, threadlocker", 1, 230.0, "Amazon", "", "Our v1 hardware section's figure, pending the K1 BOM.")]),
]
bom = dict(meta=dict(version="2.0-wip", variant="k1-derivative", priced_as_of=PRICED_AS_OF, currency="USD"),
           variants={pick: dict(sections=[dict(id="actuators", title="Actuators", tier="core", blurb=f"{'Shape-first' if pick == 'shape_first' else 'Torque-first'}: {', '.join(f'{n} × {m}' for m, n in variants[pick]['counts'].items())}.", rows=act_rows(pick))] + sections_common) for pick in variants})
for pick, v in bom["variants"].items():
    for sec in v["sections"]:
        sec["subtotal"] = round(sum(r["total"] for r in sec["rows"]), 2)
    v["tiers"] = {"core": round(sum(sec["subtotal"] for sec in v["sections"] if sec["tier"] == "core"), 2)}
    variants[pick]["core_usd"] = v["tiers"]["core"]
    variants[pick]["mass_kg_est"] = round(k1_mass_urdf + (variants[pick]["actuator_mass_g"] - k1_act_mass) / 1000, 1)

# --------------------------------------------------------------------------- kinematic dimensions, for the page
def jo(name):
    return np.array(next(J for J in joints if J["id"] == name)["origin"]) * 1000


dims = dict(height_mm=round(HEIGHT * 1000), hip_pitch_height_mm=round(float(jo("left_hip_pitch_joint")[2])), hip_spacing_mm=round(float(abs(jo("left_hip_roll_joint")[1] - jo("right_hip_roll_joint")[1]))),
            thigh_mm=round(float(jo("left_hip_yaw_joint")[2] - jo("left_knee_joint")[2])), shank_mm=round(float(jo("left_knee_joint")[2] - jo("left_ankle_pitch_joint")[2])),
            ankle_height_mm=round(float(jo("left_ankle_pitch_joint")[2])), shoulder_height_mm=round(float(jo("left_shoulder_pitch_joint")[2])),
            shoulder_spacing_mm=round(float(abs(jo("left_shoulder_roll_joint")[1] - jo("right_shoulder_roll_joint")[1]))),
            upper_arm_mm=round(float(jo("left_shoulder_yaw_joint")[2] - jo("left_elbow_joint")[2])), forearm_mm=round(float(np.linalg.norm(jo("left_wrist_roll_joint") - jo("left_elbow_joint")))),
            foot_length_mm=round(float((mesh["left_ankle_roll_link"].bounds[1][0] - mesh["left_ankle_roll_link"].bounds[0][0]) * 1000)))

out = dict(
    meta=dict(name="Fully Open Humanoid v2 (K1 derivative)", version="2.0-wip", generated_by="tools/build_k1rs.py", priced_as_of=PRICED_AS_OF,
              basis="ROBOTIS AI Sapiens K1 rev 1 description, kept as published; actuators, electronics, hands and covers substituted", ground_z=round(float(GROUND), 4),
              model_file="assets/geom/ref-k1.glb", wall_mm=WALL),
    k1=K1, k1_actuators=QC, rs=RS, dims=dims, link_mass_kg={l: round(m, 3) for l, m in mass.items()}, k1_mass_urdf_kg=round(k1_mass_urdf, 2), k1_actuator_mass_g=k1_act_mass,
    joints=joints, shank=shank, variants=variants, shells=shells, shell_mass_g=shell_mass, bom=bom,
)
OUT.write_text(json.dumps(out, indent=1) + "\n")
print(f"K1 actuators {k1_act_mass/1000:.1f} kg of {k1_mass_urdf:.1f} kg")
for pick, v in variants.items():
    print(f"{pick:13s} {v['counts']}  actuators {v['actuator_mass_g']/1000:.1f} kg ${v['actuator_cost']:,.0f}  shell growth up to {v['shell_growth_max_mm']} mm  torque {v['torque_ratio_min']}..{v['torque_ratio_max']} of the K1's  core ${v['core_usd']:,.0f}  robot ~{v['mass_kg_est']} kg")
print("dims", dims)
print(f"shells {shell_mass/1000:.2f} kg PLA; hands {hand_mass*1000:.0f} g")
print("wrote", OUT.relative_to(ROOT))
