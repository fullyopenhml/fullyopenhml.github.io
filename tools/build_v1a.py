#!/usr/bin/env python3
"""Fully Open Humanoid v1a: the aesthetic variant of the production design (work in progress).

Same mechanics, materials and electronics as v1 (tools/build_v1.py); adds printed PLA shells so the robot
reads as one continuous body in the manner of Unitree G1 and ROBOTIS AI Sapiens: tapered limb covers, round
knee and shoulder discs, a shell torso with shoulder bezels, a pelvis cover, a rounded head with a visor and
low shoes. Two tones: warm white shells, graphite discs, bezels and visor. The polycarbonate torso panels and
the boxy v1 head go; everything structural stays exactly where v1 put it.

Imports build_v1 (which writes the v1 files), then adds the cover parts to the same links and writes:

    assets/data/robot_v1a.json   assets/data/bom_v1a.json   assets/model/foh_v1_0a.urdf

Run:  python3 tools/build_v1a.py
Then: python3 tools/check_collisions.py --model v1a --poses --sweep --steps 13
      tools/.venv/bin/python tools/build_parts.py --model v1a
      tools/.venv/bin/python tools/sim_stand.py --model v1a --render
"""
from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_data as bd      # noqa: E402
import build_v1 as v1        # noqa: E402  (builds and writes v1 first)

ROOT, OUT = bd.ROOT, bd.OUT
VERSION = "1.0a"
bd.VERSION = VERSION
CATALOG, LINKS, JOINTS, LINK_BY_ID = bd.CATALOG, bd.LINKS, bd.JOINTS, bd.LINK_BY_ID
part, place, box, cyl, cone = bd.part, bd.place, bd.box, bd.cyl, bd.cone
feat_cut_cyl, feat_cut_box, CLEAR = bd.feat_cut_cyl, bd.feat_cut_box, bd.CLEAR
P = "printed"

MATERIALS = dict(v1.MATERIALS)
MATERIALS["shell"] = {"name": "PLA shell, printed (warm white)", "color": "#e9e7e2", "density": 1.24, "fill": 1.0}
MATERIALS["shell_dark"] = {"name": "PLA shell, printed (graphite)", "color": "#262a30", "density": 1.24, "fill": 1.0}
bd.MATERIALS = MATERIALS

HIP_Z, KNEE_Z, ANKLE_Z, ROLL_Z = v1.HIP_Z, v1.KNEE_Z, v1.ANKLE_Z, v1.ROLL_Z
HIP_Y, ANKLE_Y, ARM_Y = v1.HIP_Y, v1.ANKLE_Y, v1.ARM_Y
SH_Z, ELBOW_Z, WRIST_Z, Z0, UPRIGHT, TOP = v1.SH_Z, v1.ELBOW_Z, v1.WRIST_Z, v1.Z0, v1.UPRIGHT, v1.TOP
W_LIMB, W_SHELL = 2.0, 1.6     # wall thickness: limb covers (5 perimeters of 0.4), large shells (4 perimeters)
A = bd.ACTUATORS
# rear face of an RS06 cup behind its lug face F: lug, body, cover and back plate
RS06_BACK = A["RS06"]["lug_t"] + A["RS06"]["body_l"] + A["RS06"]["cover_l"] + A["RS06"]["back_t"]      # 50.5

# --------------------------------------------------------------------------- catalogue
part("3DP_cov01_thigh_cover", "Thigh cover", P, "shell", process="FDM", mirror=True,
     notes="Tapered open shell over the thigh tube, from just under the hip-yaw socket plate to above the knee cup; two halves split along the sides, four magnet pairs; 2 mm wall.")
part("3DP_cov02_shank_cover", "Shank cover", P, "shell", process="FDM", mirror=True,
     notes="As the thigh cover, between the shank yoke's socket boss and the ankle cup.")
part("3DP_cov03_knee_disc", "Knee disc", P, "shell_dark", process="FDM", mirror=True,
     notes="3 mm graphite disc on the outer shank plate, over the knee coupler screws; three M3 into inserts in the plate.")
part("3DP_cov04_shoe", "Shoe", P, "shell", process="FDM", mirror=True,
     notes="Rounded toe cap, two side rails and a heel cap in one print, sitting on the foot plate between the ankle actuators; M3 into the sole bolts' nuts. The ankle actuators stay visible on purpose (G1 style).")
part("3DP_cov05_upper_arm_cover", "Upper-arm cover", P, "shell", process="FDM", mirror=True,
     notes="Short tapered shell between the shoulder-yaw socket and the elbow cup; two halves, two magnet pairs.")
part("3DP_cov06_forearm_cover", "Forearm cover", P, "shell", process="FDM", mirror=True,
     notes="Tapered shell from the wrist housing to the elbow yoke's cross member; two halves, three magnet pairs.")
part("3DP_cov07_shoulder_disc", "Shoulder rear disc", P, "shell_dark", process="FDM", mirror=True,
     notes="4 mm graphite disc on the back plate of the shoulder-roll cup; three M3 into inserts.")
part("3DP_cov08_torso_shell", "Torso shell", P, "shell", process="FDM",
     notes="Rounded shell around the extrusion frame, 1.6 mm wall, 200 x 240 x 500. Printed as eight panels (four sides, two heights) with magnet pockets and lap joints; "
           "openings for the shoulders, the neck, the E-stop and the breaker. Replaces the polycarbonate side, front and back panels.")
part("3DP_cov09_shoulder_bezel", "Shoulder bezel", P, "shell_dark", process="FDM", mirror=True,
     notes="Graphite ring in the torso shell's shoulder opening, Ø124 / Ø100, 8 mm; the shoulder bracket beam turns inside it.")
part("3DP_cov10_pelvis_cover", "Pelvis cover", P, "shell", process="FDM",
     notes="U-shaped cover (front, back and bottom) around the hip-pitch cups, 4 mm; four standoffs bolt to the outer slots of the pelvis bars with M5 T-nuts. The bottom narrows to clear the hip-yaw cups at full adduction.")
part("3DP_cov11_head_shell", "Head shell", P, "shell", process="FDM",
     notes="Rounded hollow head, 1.6 mm wall, 120 x 130 x 100; sits on the neck post (four M3 from inside), camera on a printed cradle behind the visor.")
part("3DP_cov12_visor", "Visor", P, "shell_dark", process="FDM",
     notes="Graphite strip set into a recess across the face; the camera window is cut in it.")
part("HW_MAGNET_8X3", "Neodymium disc magnet Ø8 x 3 mm, N52", "hardware", "steel", price=0.25, vendor="Amazon (50-pack)", mass_g=1,
     notes="Pairs along the split lines of the two-piece covers and the torso panels; glued into printed pockets.")

pelvis = LINK_BY_ID["pelvis"]


def occ(link_id, name):
    for o in LINK_BY_ID[link_id]["parts"]:
        if o["occ"] == name:
            return o
    raise KeyError(name)


def remove_occ(link_id, name):
    L = LINK_BY_ID[link_id]
    o = occ(link_id, name)
    L["parts"].remove(o)
    CATALOG[o["part"]]["qty"] -= 1
    if CATALOG[o["part"]]["qty"] == 0:       # a part this variant no longer uses leaves the catalogue (and the STL set)
        del CATALOG[o["part"]]


# --------------------------------------------------------------------------- torso, pelvis, head
for n in ("side_panel_L", "side_panel_R", "back_panel", "front_panel"):     # polycarbonate panels give way to the shell
    remove_occ("pelvis", n)
# the breaker sat flush with the old back panel; 3 mm inboard it clears the shell wall (still outside the rear uprights)
occ("pelvis", "breaker")["shapes"][0]["c"][0] += 3.0
HIP_PARTS = {"hip_cup_L", "hip_cup_R", "pelvis_bar_F", "pelvis_bar_B", "hip_pitch_L_act", "hip_pitch_R_act", "hip_pitch_L_bearing", "hip_pitch_R_bearing"}
torso_inside = [o["occ"] for o in pelvis["parts"] if o["occ"] not in HIP_PARTS]
shell = place(pelvis, "torso_shell", "3DP_cov08_torso_shell", [dict(box((200, 240, 500), (0, 0, Z0 + 1 + 250), 40), w=W_SHELL)],
              inside=torso_inside + ["shoulder_bracket_L", "shoulder_bracket_R", "shoulder_pitch_L_coupler", "shoulder_pitch_R_coupler"])
for s in (1, -1):
    feat_cut_cyl(shell, "y", (0, 110 * s, SH_Z), 100, 0, 12 * s)            # shoulder openings (the bracket beam, corner radius 37.5, turns inside)
    place(pelvis, f"shoulder_bezel_{'L' if s > 0 else 'R'}", "3DP_cov09_shoulder_bezel", [cyl("y", 62, 8, (0, 124 * s, SH_Z), r_in=50)],
          inside=["torso_shell"])
feat_cut_cyl(shell, "z", (10, 0, Z0 + 1 + 500 - 5), 48, 0, 10)                 # neck post Ø44 through the top
feat_cut_cyl(shell, "x", (-105, 0, Z0 + 420), 46, 0, 10)                       # E-stop head Ø40 through the back
feat_cut_box(shell, (10, 40, 64), (-100, -55, Z0 + 350))                        # breaker toggle
# pelvis cover: front and back panels joined by a bottom panel under the hip actuators, standoffs to the pelvis bars
# widths: the hip-yaw cups (r 56 at y 140) reach y 84 at the zero pose and y 67 at z 878 when the leg adducts 12 deg
pc = place(pelvis, "pelvis_cover", "3DP_cov10_pelvis_cover", [
    box((4, 164, 171), (94, 0, 959.5), 3), box((4, 164, 171), (-94, 0, 959.5), 3),     # z 874..1045, flush under the bottom plate
    box((192, 128, 4), (0, 0, 876), 2),                                                  # bottom, 4 mm under the RS04 mount rings (r 68 at z 950)
    *[box((15.5, 14, 18), (84.25 * sx, 80 * sy, 1035)) for sx in (1, -1) for sy in (1, -1)],   # standoffs on the bars' outer faces (x 76.5)
])
for sx in (1, -1):
    for sy in (1, -1):
        feat_cut_cyl(pc, "x", (76.5 * sx, 80 * sy, 1035), CLEAR["M5"], 0, 19.5 * sx)
# head: rounded hollow shell on the neck post, camera inside, graphite visor in a recess
remove_occ("pelvis", "head_shell")
HEAD_C = (20, 0, TOP + 34 + 50)
hs = place(pelvis, "head_shell", "3DP_cov11_head_shell", [dict(box((120, 130, 100), HEAD_C, 30), w=W_SHELL)], inside=["neck_post"])
feat_cut_box(hs, (6, 96, 26), (80, 0, HEAD_C[2]))                               # visor recess
feat_cut_box(hs, (6, 60, 14), (80, 0, HEAD_C[2]))                               # camera window
cam = occ("pelvis", "camera")
cam["shapes"][0]["c"][0] = 54.0                                                 # 6 mm back from v1: the camera sits behind the visor
cam["inside"] = ["head_shell"]
place(pelvis, "visor", "3DP_cov12_visor", [box((5, 96, 26), (78, 0, HEAD_C[2]), 2)], inside=["head_shell"])

# --------------------------------------------------------------------------- limbs
for S, s in (("L", 1), ("R", -1)):
    Y = HIP_Y * s
    # thigh: between the yaw socket plate (bottom z 803.5) and the knee cup boss (top z 648)
    place(LINK_BY_ID[f"thigh_{S}"], f"thigh_cover_{S}", "3DP_cov01_thigh_cover", [cone("z", 40, 46, 145, (0, Y, 727.5), W_LIMB)],
          inside=[f"thigh_tube_{S}", f"thigh_socket_{S}", f"knee_cup_{S}"])
    # shank: between the yoke's socket boss (bottom z 380) and the ankle cup boss (top z 228)
    place(LINK_BY_ID[f"shank_{S}"], f"shank_cover_{S}", "3DP_cov02_shank_cover", [cone("z", 36, 40, 137, (0, Y, 303.5), W_LIMB)],
          inside=[f"shank_tube_{S}", f"shank_yoke_{S}", f"ankle_cup_{S}"])
    yo = (183 + 10) * s                                                          # outer face of the shank yoke's outer plate
    place(LINK_BY_ID[f"shank_{S}"], f"knee_disc_{S}", "3DP_cov03_knee_disc", [cyl("y", 72, 3, (0, yo + 1.5 * s, KNEE_Z))])
    # shoe on the foot: toe cap in front of the ankle-pitch actuator, rails along the plate edges under the ankle-roll ring, heel cap behind its back plate
    YF = ANKLE_Y * s
    place(LINK_BY_ID[f"foot_{S}"], f"shoe_{S}", "3DP_cov04_shoe", [
        dict(box((42, 88, 47), (79, YF, 42.5), 14), w=W_SHELL),                    # toe cap x 58..100, z 19..66
        box((208, 6, 13), (-46, YF + 41 * s, 25.5)), box((208, 6, 13), (-46, YF - 41 * s, 25.5)),   # rails x -150..58, z 19..32
        box((8, 88, 30), (-146, YF, 34), 6),                                       # heel cap x -150..-142 (RS06 back plate ends at -139.5)
    ])
    # arms
    AY = ARM_Y * s
    place(LINK_BY_ID[f"upper_arm_{S}"], f"upper_arm_cover_{S}", "3DP_cov05_upper_arm_cover", [cone("z", 32, 36, 65, (0, AY, 1217.5), W_LIMB)],
          inside=[f"upper_arm_tube_{S}", f"upper_arm_socket_{S}", f"elbow_cup_{S}"])
    place(LINK_BY_ID[f"forearm_{S}"], f"forearm_cover_{S}", "3DP_cov06_forearm_cover", [cone("z", 38, 44, 147, (0, AY, 939.5), W_LIMB)],
          inside=[f"forearm_tube_{S}", f"forearm_yoke_{S}", f"wrist_housing_{S}"])
    bx = 14 - RS06_BACK                                                           # shoulder-roll cup rear face, x -36.5
    place(LINK_BY_ID[f"shoulder_roll_bracket_{S}"], f"shoulder_disc_{S}", "3DP_cov07_shoulder_disc", [cyl("x", 48, 4, (bx - 2, AY, SH_Z))])   # r 48: the bracket beam ends 1 mm inside r 50

N_MAG = 2 * (4 + 4 + 2 + 3) + 16 + 4           # limb covers both sides, torso panels, head to neck
CATALOG["HW_MAGNET_8X3"]["qty"] = N_MAG

# --------------------------------------------------------------------------- derived data for the new occurrences (as v1)
for lnk in LINKS:
    ox, oy, oz = lnk["origin"]
    for o in lnk["parts"]:
        if "center" in o:
            continue
        cat = CATALOG[o["part"]]
        lo = [1e9] * 3; hi = [-1e9] * 3; v = 0.0
        for sh in o["shapes"]:
            a, b = bd.shape_bbox(sh)
            lo = [min(lo[k], a[k]) for k in range(3)]; hi = [max(hi[k], b[k]) for k in range(3)]
            v += bd.vol(sh)
            sh["c"] = [round(sh["c"][0] - ox, 3), round(sh["c"][1] - oy, 3), round(sh["c"][2] - oz, 3)]
        for f in o.get("features", []):
            f["c"] = [round(f["c"][0] - ox, 3), round(f["c"][1] - oy, 3), round(f["c"][2] - oz, 3)]
        centre = [(lo[k] + hi[k]) / 2 for k in range(3)]
        o["center"] = [round(centre[0] - ox, 2), round(centre[1] - oy, 2), round(centre[2] - oz, 2)]
        o["center_world"] = [round(c, 1) for c in centre]
        if "dims" not in cat:
            cat["dims"] = [round(hi[k] - lo[k], 1) for k in range(3)]
        if "mass_g" not in cat:
            m = MATERIALS[cat["material"]]
            cat["mass_g"] = round(v / 1000.0 * m["density"] * m["fill"])
mass = {"actuators": 0, "printed": 0, "hardware": 0, "electronics": 0}
optional_mass = 0
for lnk in LINKS:
    for o in lnk["parts"]:
        cat = CATALOG[o["part"]]
        mg = cat.get("mass_g", 0)
        if o.get("optional"):
            optional_mass += mg; continue
        mass["actuators" if cat["category"] == "actuator" else cat["category"]] += mg
mass["hardware"] += N_MAG * CATALOG["HW_MAGNET_8X3"]["mass_g"]
mass["fasteners_and_harness"] = 1100
mass_total = sum(mass.values())
cover_ids = [p for p in CATALOG if p.startswith("3DP_cov")]
cover_mass = sum(CATALOG[p]["mass_g"] * CATALOG[p]["qty"] for p in cover_ids)

# --------------------------------------------------------------------------- BOM: v1's sections plus the covers
BOM_SECTIONS = copy.deepcopy(v1.BOM_SECTIONS)
row = bd.row
printed = lambda *mats: sum(CATALOG[p]["mass_g"] * CATALOG[p]["qty"] for p in CATALOG if CATALOG[p]["category"] == "printed" and CATALOG[p]["material"] in mats and not CATALOG[p].get("optional"))
kg = lambda g: math.ceil(g * 1.35 / 1000 * 2) / 2
for sec in BOM_SECTIONS:
    if sec["id"] == "structure":
        sec["rows"] = [r for r in sec["rows"] if r["id"] != "PC_SHEET"] + [
            row("PC_SHEET_SMALL", "Polycarbonate sheet 3 mm, 300 x 300 (electronics tray)", 1, 9.0, "hardware store", "", "The torso panels are printed shells in this variant.")]
    if sec["id"] == "filament":
        for r in sec["rows"]:
            if r["id"] == "MAT_PLA":
                r["qty"] = kg(printed("pla", "shell"))
                r["total"] = round(r["qty"] * r["unit_cost"], 2)
                r["description"] = "PLA filament, 1 kg spool (warm white)"
                r["notes"] = f"Head, cradles and {printed('shell')/1000:.2f} kg of cover shells."
        sec["rows"].append(row("MAT_PLA_DARK", "PLA filament, 1 kg spool (graphite)", kg(printed("shell_dark")), 20.0, "Any", "", "Knee and shoulder discs, shoulder bezels, visor.", unit_label="kg"))
        sec["blurb"] = (f"About {printed('petg_cf')/1000:.1f} kg of structural prints, {printed('pla', 'shell', 'shell_dark')/1000:.1f} kg of PLA "
                        f"(of which {cover_mass/1000:.1f} kg is cover shells) and {printed('tpu')/1000:.1f} kg of TPU; quantities add 35 % for supports and failed prints.")
BOM_SECTIONS.insert(3, dict(
    id="covers", title="Covers (aesthetic variant)", tier="core",
    blurb="What the shells add on top of v1: magnets, inserts and glue. The filament is in the printed-parts section; the polycarbonate panels they replace are gone from the structure section.",
    rows=[row("HW_MAGNET_8X3", CATALOG["HW_MAGNET_8X3"]["name"], N_MAG, 0.25, "Amazon", "", CATALOG["HW_MAGNET_8X3"]["notes"]),
          row("HW_INSERT_M3_COV", "Heat-set inserts M3 x 4, 100 pack", 1, 9.0, "Amazon", "", "Knee and shoulder discs, pelvis cover, head."),
          row("HW_TNUT_M5_COV", "2020 T-nuts M5 with M5 x 12 screws, 10 pack", 1, 6.0, "Amazon", "", "Pelvis cover standoffs."),
          row("HW_GLUE_CA", "Cyanoacrylate glue, thick", 1, 6.0, "Amazon", "", "Magnets into pockets, visor into its recess."),
          row("MAT_FINISH", "Filler primer and matte clear coat, spray cans", 2, 9.0, "hardware store", "", "Optional: sand and coat the shells for a smooth finish.")]))
tiers = {}
for sec in BOM_SECTIONS:
    sec["subtotal"] = round(sum(r["total"] for r in sec["rows"]), 2)
    tiers[sec["tier"]] = round(tiers.get(sec["tier"], 0) + sec["subtotal"], 2)

# --------------------------------------------------------------------------- specs, outputs
lo = [1e9] * 3; hi = [-1e9] * 3
for lnk in LINKS:
    for o in lnk["parts"]:
        for sh in o["shapes"]:
            gc = [sh["c"][k] + lnk["origin"][k] for k in range(3)]
            a, b = bd.shape_bbox(dict(sh, c=gc))
            lo = [min(lo[k], a[k]) for k in range(3)]; hi = [max(hi[k], b[k]) for k in range(3)]
SPECS = dict(v1.SPECS)
SPECS.update(height_mm=round(hi[2]), width_mm=round(hi[1] - lo[1]), depth_mm=round(hi[0] - lo[0]), mass_g=mass, mass_total_g=mass_total,
             optional_mass_g=optional_mass, cover_mass_g=cover_mass, cover_parts=cover_ids, base_mass_g=v1.mass_total, base_core_usd=v1.tiers["core"])
robot = dict(
    meta=dict(name="Fully Open Humanoid", short="FOH", version=VERSION, variant="aesthetic", units="mm", frame="X forward, Y left, Z up; ground at z = 0",
              generated_by="tools/build_v1a.py", basis="v1 production design with printed cover shells (work in progress)"),
    materials=MATERIALS, actuators=v1.robot["actuators"], catalog=CATALOG, links=LINKS, joints=JOINTS, poses=v1.POSES, specs=SPECS, groups=v1.robot["groups"],
)
bom = dict(meta=dict(version=VERSION, variant="aesthetic", priced_as_of=v1.PRICED_AS_OF, currency="USD"), sections=BOM_SECTIONS, tiers=tiers)
(OUT / "robot_v1a.json").write_text(json.dumps(robot, separators=(",", ":")) + "\n")
(OUT / "bom_v1a.json").write_text(json.dumps(bom, indent=1) + "\n")
bd.write_urdf(ROOT / "assets" / "model" / "foh_v1_0a.urdf")

if __name__ == "__main__":
    print(f"FOH v{VERSION} (aesthetic): {len(LINKS)} links, {len(JOINTS)} joints, {sum(len(l['parts']) for l in LINKS)} occurrences")
    print(f"Envelope {SPECS['depth_mm']} x {SPECS['width_mm']} x {SPECS['height_mm']} mm; mass {mass_total/1000:.2f} kg (v1 {v1.mass_total/1000:.2f}); covers {cover_mass/1000:.2f} kg")
    print(f"core ${tiers['core']:,.2f} (v1 ${v1.tiers['core']:,.2f}); PLA {printed('pla','shell','shell_dark')/1000:.2f} kg")
    for p in cover_ids:
        c = CATALOG[p]; print(f"   {p:28s} x{c['qty']:<2d} {c['mass_g']:5d} g  {c['material']:10s} {c.get('dims')}")
