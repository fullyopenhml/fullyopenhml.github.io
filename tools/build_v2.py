#!/usr/bin/env python3
"""Fully Open Humanoid v2 (work in progress): Berkeley Humanoid Lite's extended configuration, from BHL's own parts.

The paper's Fig. 5 shows an adult-sized Berkeley Humanoid Lite: the same self-contained actuator modules, carbon-fibre
tubes between them to bring the limbs to adult length, a hip arranged as pitch, abduction and rotation, a dexterous
hand. This design builds that figure with two substitutions and as many of BHL's published printed parts as the
figure keeps:

  * RobStride actuators in place of the printed cycloidal modules, by BHL's own classes: an RS06 where BHL has a 6512
    (knee, shoulder pitch), an RS02 where it has a 5010 (ankle pitch and roll, shoulder roll and yaw, elbow, wrist),
    and RS03 in the new hip stack. Each kept BHL cradle keeps its channel around the body and gets our mount ring
    (with the output support bearing) in its mouth, re-drilled to the RobStride's lug pattern.
  * The thigh, shank, upper-arm and forearm arms are cut and a tube inserted on printed socket flanges. The cradle
    ends, the knee and elbow yokes (with BHL's own 6803 bearings), the ankle bracket, the foot with its shoe and the
    shoulder bracket are BHL's parts (tools/bhl_pieces.py cuts them from the published link meshes, CC BY-SA 4.0).
  * New: the hip stack and pelvis (as the figure's inset), the 2020 torso, the tube sockets, the hand flange.

Writes:  assets/data/robot_v2.json   assets/data/bom_v2.json   assets/model/foh_v2_0.urdf
Run:     tools/.venv/bin/python tools/bhl_pieces.py       (once; writes assets/data/bhl_pieces.json + assets/geom/v2)
         python3 tools/build_v2.py
Then:    python3 tools/check_collisions.py --model v2 --poses --sweep --steps 13
         tools/.venv/bin/python tools/build_parts.py --model v2
         tools/.venv/bin/python tools/sim_stand.py --model v2 --render
"""
from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_data as bd  # noqa: E402  (importing it writes the v0.2 files; harmless)

ROOT = bd.ROOT
OUT = bd.OUT
VERSION = "2.0"
PRICED_AS_OF = "2026-10"

# --------------------------------------------------------------------------- fresh state
bd.CATALOG.clear(); bd.LINKS.clear(); bd.JOINTS.clear(); bd.LINK_BY_ID.clear()
bd.VERSION = VERSION
CATALOG, LINKS, JOINTS = bd.CATALOG, bd.LINKS, bd.JOINTS
part, place, link, joint, Kit, add_kit = bd.part, bd.place, bd.link, bd.joint, bd.Kit, bd.add_kit
cyl, box, vol, feat_holes, feat_cut_cyl, feat_cut_box = bd.cyl, bd.box, bd.vol, bd.feat_holes, bd.feat_cut_cyl, bd.feat_cut_box
CLEAR, CBORE, INSERT = bd.CLEAR, bd.CBORE, bd.INSERT

MATERIALS = dict(bd.MATERIALS)
MATERIALS["bhl_pla"] = {"name": "PLA, printed (Berkeley Humanoid Lite part)", "color": "#e8e3d6", "density": 1.24, "fill": 0.35}
MATERIALS["cf_tube"] = {"name": "Carbon-fibre tube, 3K roll-wrapped", "color": "#2b2d31", "density": 1.55, "fill": 1.0}
MATERIALS["al_plate"] = {"name": "Aluminium 6061 plate, laser-cut", "color": "#b9bec6", "density": 2.70, "fill": 1.0}
MATERIALS["pc_sheet"] = {"name": "Polycarbonate sheet", "color": "#c9ced6", "color_alpha": 0.6, "density": 1.20, "fill": 1.0}
MATERIALS["hand"] = {"name": "Amazing Hand (printed, bus servos)", "color": "#8a93a0"}
bd.MATERIALS = MATERIALS

# --------------------------------------------------------------------------- actuators (the v1 interface table)
ACT = copy.deepcopy(bd.ACTUATORS)
ACT["RS03"]["mount_t"] = 22
ACT["RS06"]["mount_t"] = 20
ACT["RS02"]["mount_t"] = 12
bd.ACTUATORS = ACT
CLEAR["M5"] = 5.5
CBORE["M5"] = (10.0, 5.3)
PLATE = {"RS03": 10, "RS06": 8, "RS02": 8}       # child-plate thickness per model: our plates, and BHL's bosses counterbored to it
MODELS = ("RS03", "RS06", "RS02")
BHL_CLASS = {"RS06": "6512", "RS02": "5010"}
RING_IN_BHL = {"RS03": 56, "RS06": 50, "RS02": 41}          # our mount ring radius inside a BHL cradle (its mouth is bored to this + 1); 41 is the RS02 lug counterbores plus 1.5 mm


def screw_lengths():
    """Standard screw lengths for every kit, with thread-engagement checks (as v1)."""
    std = (8, 10, 12, 16, 20, 25, 30, 35, 40)
    out = {}
    for m in MODELS:
        I = ACT[m]
        through = I["mount_t"] - CBORE[I["lug_screw"]][1]
        ok = [L for L in std if 0.75 * I["lug_depth"] <= L - through <= I["lug_depth"]]
        assert ok, f"{m}: no standard lug screw engages 75-100 % of {I['lug_depth']} mm through {through} mm"
        res = {"lug": (I["lug_screw"], ok[0], round(ok[0] - through, 1))}
        through_out = PLATE[m] + (I["mount_t"] + 2) - (I["step_h"] + I["boss_h"])
        ok = [L for L in std if 0.75 * I["out_depth"] <= L - through_out <= I["out_depth"]]
        assert ok, f"{m}: no standard output screw engages 75-100 % of {I['out_depth']} mm through {through_out} mm"
        res["out"] = (I["out_screw"], ok[0], round(ok[0] - through_out, 1))
        out[m] = res
    return out


SCREWS = screw_lengths()

# --------------------------------------------------------------------------- BHL's pieces
BHL = json.loads((OUT / "bhl_pieces.json").read_text())
PIECES = BHL["pieces"]


def bhl_piece(lnk, occ, name, ref, s, inside=None, notes=""):
    """Place one of BHL's printed parts (cut by tools/bhl_pieces.py) by its reference joint at the global point `ref`,
    mirrored for the right side (s = -1). The shape is a mesh: the viewer loads the GLB, the audit uses its surface
    samples and convex hull, the URDF its bounding box, the BOM its mass."""
    P = PIECES[name]
    side = "L" if s > 0 else "R"
    bb = P["bbox"] if s > 0 else [[P["bbox"][0][0], -P["bbox"][1][1], P["bbox"][0][2]], [P["bbox"][1][0], -P["bbox"][0][1], P["bbox"][1][2]]]
    sh = dict(t="mesh", file=P["file"].format(side=side), c=list(ref), bb=bb, mass_g=P["mass_g"],
              pts=[[x, y * s, z] for x, y, z in P["pts"]], hull=[[nx, ny * s, nz, d] for nx, ny, nz, d in P["hull"]], m="bhl_pla")
    pid = "BHL_" + name
    if pid not in CATALOG:
        part(pid, P["name"], "printed", "bhl_pla", process="FDM", mirror=True, source="bhl",
             notes=f"Berkeley Humanoid Lite part ({P['bhl_source']}; CC BY-SA 4.0, Hybrid Robotics). " + notes)
    return place(lnk, occ, pid, [sh], inside=inside)


def section_xy(name, s):
    """Centre of the arm's section at the cut, relative to the piece's reference joint (x, y), mirrored for the right side."""
    c = PIECES[name]["section"]["centre"]
    return c[0], c[1] * s


# --------------------------------------------------------------------------- catalogue (our parts)
P, H, E = "printed", "hardware", "electronics"
part("3DP_kit03_coupler", "RS03 coupler (output hub)", P, "petg_cf", process="FDM",
     notes="On the RS03 output boss, 3 x Ø4 dowels; six M4 x 30 through the child plate and coupler into the boss (PCD 30.36). Ø45 hub for the 6809 bearing.")
part("3DP_kit06_coupler", "RS06 coupler (output hub)", P, "petg_cf", process="FDM",
     notes="On the RS06 output boss, 3 x Ø4 dowels; six M4 x 25 through the child plate and coupler (PCD 24). Ø35 hub for the 6807 bearing.")
part("3DP_kit02_coupler", "RS02 coupler (output hub)", P, "petg_cf", process="FDM",
     notes="On the RS02 output boss, 3 x Ø4 dowels; six M4 x 25 through the child plate and coupler (PCD 24). Ø35 hub for the 6707 bearing.")
# pelvis and hip stack (the figure's inset: new parts)
part("3DP_pel11_hip_cup", "Hip-pitch cup", P, "petg_cf", process="FDM", mirror=True,
     notes="RS03 mount ring (8 x M4 on PCD 98, 6809 pocket), collar straps open at the top, and a tab that bolts to the two pelvis bars with four M5 T-nuts.")
part("3DP_leg21_hip_roll_bracket", "Hip-roll bracket", P, "petg_cf", process="FDM", mirror=True,
     notes="Plate on the hip-pitch coupler, web to the hip-roll RS03 cup: mount ring, straps and back plate, open on the inboard side.")
part("3DP_leg22_hip_yaw_housing", "Hip-yaw housing", P, "petg_cf", process="FDM", mirror=True,
     notes="Front plate on the hip-roll coupler, RS03 mount ring and collar for the hip-yaw actuator (axis vertical, output down).")
part("3DP_leg23_thigh_socket", "Thigh socket (hip-yaw output)", P, "petg_cf", process="FDM", mirror=True,
     notes="Round plate on the hip-yaw coupler with the Ø30 tube socket below it: 40 mm bond length, two M4 cross bolts.")
part("3DP_v2_socket30", "Tube socket flange, Ø30 (legs)", P, "petg_cf", process="FDM",
     notes="60 x 60 x 8 flange with four M4 holes, bolted to the cut end of a BHL arm; Ø30 tube boss, 40 mm bond, two M4 cross bolts.")
part("3DP_v2_socket25", "Tube socket flange, Ø25 (arms)", P, "petg_cf", process="FDM",
     notes="8 mm flange with M4 holes, bolted to the cut end of a BHL arm plate (36 x 50 at the upper arm, 50 x 14 under the elbow yoke) or the top of a wrist or yaw flange (50 x 50); Ø25 tube boss, 40 mm bond, two M4 cross bolts.")
# torso and head
part("AL_TORSO_PLATE", "Torso plate, 5 mm 6061, laser-cut, 180 x 360", H, "al_plate", price=28.0, vendor="SendCutSend / local laser cutter",
     notes="Two per robot (bottom and top). Four M5 for the uprights, four M5 into the pelvis bars (bottom) or the head post (top).")
part("3DP_tor14_shoulder_mount", "Shoulder-pitch mount", P, "petg_cf", process="FDM", mirror=True,
     notes="RS06 mount ring, collar and back plate hung from the top plate; the actuator passes through the side panel, its output face outside the torso as BHL's does.")
part("PC_SIDE_PANEL", "Torso side panel, 3 mm polycarbonate", H, "pc_sheet", price=4.5, vendor="hardware store sheet, hand-cut", mirror=True,
     notes="Clearance hole for the shoulder-pitch actuator.")
part("PC_BACK_PANEL", "Torso back panel, 3 mm polycarbonate", H, "pc_sheet", price=4.5, vendor="hardware store sheet, hand-cut", notes="Carries the E-stop and breaker.")
part("PC_FRONT_PANEL", "Torso front panel, 3 mm polycarbonate", H, "pc_sheet", price=4.5, vendor="hardware store sheet, hand-cut", notes="Removable; magnets.")
part("PC_TRAY", "Electronics tray, 3 mm polycarbonate", H, "pc_sheet", price=4.5, vendor="hardware store sheet, hand-cut")
part("3DP_tor19_battery_cradle", "Battery cradle", P, "pla", process="FDM", notes="One per pack.")
part("3DP_hea11_neck_post", "Neck post", P, "petg_cf", process="FDM")
part("3DP_hea12_head_shell", "Head shell", P, "pla", process="FDM", notes="Blank head with a RealSense pocket. Camera optional.")
# arms
part("3DP_arm27_hand_flange", "Hand flange", P, "petg_cf", process="FDM",
     notes="50 x 50 x 6 plate: six M4 through the RS02 coupler into the wrist output, four M3 inserts on a 25 mm square for the Amazing Hand's wrist.")
part("KIT_AMAZING_HAND", "Amazing Hand (Pollen Robotics), left or right", E, "hand", mass_g=400, price=220.0,
     vendor="Pollen Robotics BOM (printed parts + 8 bus servos + board)", mirror=True,
     notes="8-DOF printed hand, Apache-2.0, under 200 EUR in parts per Pollen. The figure's dexterous hand is not named; this is the open one.")
# tubes, extrusion, studs
part("CF_TUBE_30", "Carbon-fibre tube Ø30 x 26 mm, 3K roll-wrapped", H, "cf_tube", price=23.0, vendor="Amazon (WHABEST / cncarbonfiber) 1000 mm",
     notes="Thigh and shank links. One 1000 mm tube yields all four pieces. Bonded 40 mm into each socket with structural epoxy, plus two M4 cross bolts.")
part("CF_TUBE_25", "Carbon-fibre tube Ø25 x 22 mm, 3K roll-wrapped", H, "cf_tube", price=18.0, vendor="Amazon (WHABEST) 1000 mm",
     notes="Upper-arm and forearm links. One 1000 mm tube yields all four pieces.")
part("HW_2020_480", "Aluminium 2020 extrusion, 480 mm, ends tapped M5", H, "al_ext", price=5.0, vendor="Amazon / Misumi", notes="Torso uprights.")
part("HW_2020_300", "Aluminium 2020 extrusion, 300 mm", H, "al_ext", price=4.0, vendor="Amazon / Misumi", notes="Pelvis bars: the hip cups and the torso bottom plate bolt to them with T-nuts.")
part("HW_STUD_17", "Yoke stud, Ø17 steel dowel, 30 mm", H, "steel", price=1.5, vendor="McMaster / Amazon",
     notes="Through the cradle's end cap into the yoke's 6803 bearing: the second bearing of BHL's knee, ankle and elbow joints.")
# bearings
part("HW_6809_2RS", "Ball bearing 6809-2RS, 45 x 58 x 7 mm", H, "steel", price=3.0, vendor="Amazon", notes="Output support bearing of every RS03 joint.")
part("HW_6807_2RS", "Ball bearing 6807-2RS, 35 x 47 x 7 mm", H, "steel", price=4.0, vendor="Amazon", notes="Output support bearing of every RS06 joint.")
part("HW_6707_2RS", "Ball bearing 6707-2RS, 35 x 44 x 5 mm", H, "steel", price=3.0, vendor="Amazon", notes="Output support bearing of every RS02 joint.")
part("HW_6803_2RS", "Ball bearing 6803-2RS, 17 x 26 x 5 mm", H, "steel", price=2.87, vendor="Amazon (BHL BOM)",
     notes="BHL's yoke bearing: the outer plate of the knee, ankle and elbow yokes rides on it. Six per robot, as in BHL.")
# electronics on the model (same as v0.2 / v1)
for pid in ("EL_PC_N100", "EL_BATTERY_6S", "EL_CANABLE", "EL_USB_HUB", "EL_BUCK_12V", "EL_DIST_BLOCK", "EL_IMU", "EL_ESTOP", "EL_BREAKER", "EL_CONTACTOR", "EL_CAMERA_D435I"):
    src = json.loads((OUT / "robot.json").read_text())["catalog"][pid]
    d = {k: v for k, v in src.items() if k not in ("qty", "dims")}
    d["qty"] = 0
    CATALOG[pid] = d

# --------------------------------------------------------------------------- key dimensions (mm)
# BHL (0.8 m): thigh 150, shank 160, upper arm 123 + 43, forearm 123, ankle pitch 100 above the ground. Adult-sized as the
# paper's figure: hip pitch at 950, knee at 530, shoulders at 1425 (as our v1), the limbs stretched by tubes.
HIP_Z = 950          # hip-pitch and hip-roll axes
HIP_Y = 140          # hip-roll / hip-yaw / thigh-tube centreline
KNEE_Z = 530
KX, KY = -11.5, 130  # knee axis x (BHL's thigh arm is 11.5 mm forward of its knee axis: the tube hangs at x = 0) and the knee output plane (BHL's arm plate sits 10 mm outboard of it)
ANKLE_Z = 115        # ankle-pitch axis (BHL 100; the RS02 cup in BHL's foot needs 45 mm under the roll axis, BHL's saddle gave 11, so the roll axis sits 65 up)
AX, AY = KX, KY      # the shank tube is straight under the knee
ROLL_Z = ANKLE_Z - 50       # BHL's ankle bracket: roll axis 50 below the pitch axis, 30 forward, 25 outboard
RX, FOOT_Y = AX + 40, AY + 25      # BHL's bracket puts the roll output 30 forward; a 10 mm spacer under its roll boss keeps the two RS02 rings apart
BAR_Z = HIP_Z + 85          # pelvis 2020 bars (z HIP_Z+75..+95)
TORSO_Z0 = HIP_Z + 95
UPRIGHT = 480
SH_Z = TORSO_Z0 + 380       # shoulder-pitch and shoulder-roll axes
SPY = 220                   # shoulder-pitch output face (BHL's shoulder bracket puts the roll axis 43 mm outboard of it)
ARM_Y = SPY + 43            # roll / yaw line
UX, UY = 66.5, 160          # torso uprights
TUBE30, TUBE25 = 30.0, 25.0
BOND = 40
Z0 = TORSO_Z0
TOP = Z0 + 5 + UPRIGHT + 5
# arm heights from BHL's own offsets plus the tube extensions
E_UA, E_FA = 174, 147       # upper-arm and forearm extensions (BHL roll -> yaw 123, yaw -> elbow 43 down and 24.5 in; elbow -> wrist 123)
TX = 25.5 + section_xy("upper_arm_upper", 1)[0]       # upper-arm tube line: the centre of BHL's plate end, 44 mm below the roll axis
YAW_X = TX - section_xy("upper_arm_lower", 1)[0]       # the yaw joint such that BHL's flange top centres on the tube line
YAW_Z = SH_Z - 123 - E_UA
EX, EY, ELBOW_Z = YAW_X, ARM_Y - 24.5, YAW_Z - 43
FY = ARM_Y + 4              # forearm tube line: under the base of BHL's elbow yoke, on the arm line (BHL's wrist sits there too), 4 mm outboard to clear the elbow ring
WX, WY, WRIST_Z = EX, FY - section_xy("forearm_lower", 1)[1], ELBOW_Z - 123 - E_FA
tube_lengths = {}


def tube(lnk, occ, pid, z_lo, z_hi, x, y, r, inside):
    place(lnk, occ, pid, [cyl("z", r, z_hi - z_lo, (x, y, (z_lo + z_hi) / 2), r_in=r - 2.0)], inside=inside)
    tube_lengths[occ] = round(z_hi - z_lo, 1)


def socket_bore(occ, x, y, z_open, z_bottom, d):
    """Tube bore in a socket boss (axis z) from the open end to the bond bottom, plus two M4 cross bolts."""
    feat_cut_cyl(occ, "z", (x, y, min(z_open, z_bottom)), d + 0.4, 0, abs(z_open - z_bottom))
    for dz in (12, 28):
        zc = z_open - dz if z_open > z_bottom else z_open + dz
        feat_cut_cyl(occ, "x", (x - 25, y, zc), CLEAR["M4"], 0, 50)


def tube_socket(lnk, occ, pid, cx, cy, z_face, dirn, r_tube, bx=None, by=None, inside=None, size=(60, 60)):
    """Socket flange bolted to a cut BHL arm: 8 mm plate on the cut face, tube boss 50 mm along dirn.
    Returns the occurrence and the z where the tube ends (bonded 40 mm from the boss's free end)."""
    bx = cx if bx is None else bx
    by = cy if by is None else by
    zb0, zb1 = z_face + dirn * 8, z_face + dirn * 58
    o = place(lnk, occ, pid, [box((size[0], size[1], 8), (cx, cy, z_face + dirn * 4), 2), cyl("z", r_tube + 6, 50, (bx, by, (zb0 + zb1) / 2))], inside=inside)
    socket_bore(o, bx, by, zb1, zb1 - dirn * 42, 2 * r_tube)
    n = 2 if min(size) < 30 else 4
    for i in range(n):
        hx = cx + (size[0] / 2 - 8) * (1 if i % 2 else -1) if size[0] >= 30 else cx
        hy = cy + (size[1] / 2 - 8) * (1 if i // 2 else -1) if size[1] >= 30 else cy
        if n == 2:
            hx, hy = (cx + (size[0] / 2 - 8) * (1 if i else -1), cy) if size[0] >= 30 else (cx, cy + (size[1] / 2 - 8) * (1 if i else -1))
        feat_cut_cyl(o, "z", (hx, hy, min(z_face, z_face + dirn * 8)), CLEAR["M4"], 0, 8)
    return o, zb0 + dirn * 10


def stud_and_bearing(parent_occ, child_lnk, occ, axis_pt, s, t_from, t_to, bearing_t, child_inside):
    """BHL's yoke bearing: a Ø17 stud from the cradle's end cap (part of the modified BHL part) into a 6803 in the yoke's outer plate."""
    x, y, z = axis_pt
    parent_occ["shapes"].append(cyl("y", 8.5, abs(t_to - t_from), (x, (y + (t_from + t_to) / 2) * s, z)))
    CATALOG["HW_STUD_17"]["qty"] += 1
    place(child_lnk, occ, "HW_6803_2RS", [cyl("y", 13, 5, (x, (y + bearing_t) * s, z), r_in=8.5)], inside=[parent_occ["occ"]] + child_inside)


# --------------------------------------------------------------------------- pelvis + torso (root link)
pelvis = link("pelvis", "Pelvis and torso", "torso", (0, 0, 0))
for sx, tag in ((1, "F"), (-1, "B")):
    place(pelvis, f"pelvis_bar_{tag}", "HW_2020_300", [box((20, 300, 20), (66.5 * sx, 0, BAR_Z))])
hipk, cups = {}, {}
for S, s in (("L", 1), ("R", -1)):
    k = Kit("RS03", "y", s, 50 * s, 0, HIP_Z)      # body y 2.5..42, ring 50..72, child face 74
    hipk[S] = k
    cup = place(pelvis, f"hip_cup_{S}", "3DP_pel11_hip_cup", [box((170, 22, 15), (0, 61 * s, HIP_Z + 67.5), 2)])   # tab over the ring up to the bars
    for sx in (1, -1):
        for yy in (55, 67):
            feat_cut_cyl(cup, "z", (66.5 * sx, yy * s, HIP_Z + 60), CLEAR["M5"], 0, 15)
    cups[S] = cup
bp = place(pelvis, "bottom_plate", "AL_TORSO_PLATE", [box((180, 2 * UY + 40, 5), (0, 0, Z0 + 2.5))])
tp = place(pelvis, "top_plate", "AL_TORSO_PLATE", [box((180, 2 * UY + 40, 5), (0, 0, Z0 + 5 + UPRIGHT + 2.5))])
for sx in (1, -1):
    for sy in (1, -1):
        feat_cut_cyl(bp, "z", (UX * sx, UY * sy, Z0), CLEAR["M5"], 0, 5)
        feat_cut_cyl(tp, "z", (UX * sx, UY * sy, Z0 + 5 + UPRIGHT), CLEAR["M5"], 0, 5)
        tag = ("F" if sx > 0 else "B") + ("L" if sy > 0 else "R")
        place(pelvis, f"upright_{tag}", "HW_2020_480", [box((20, 20, UPRIGHT), (UX * sx, UY * sy, Z0 + 5 + UPRIGHT / 2))])
for S, s in (("L", 1), ("R", -1)):
    place(pelvis, f"side_panel_{S}", "PC_SIDE_PANEL", [box((145, 3, UPRIGHT - 20), (0, (UY + 11.5) * s, Z0 + 5 + UPRIGHT / 2))])
place(pelvis, "back_panel", "PC_BACK_PANEL", [box((3, 2 * UY + 10, UPRIGHT), (-(UX + 13), 0, Z0 + 5 + UPRIGHT / 2))])
place(pelvis, "front_panel", "PC_FRONT_PANEL", [box((3, 2 * UY + 10, UPRIGHT), (UX + 13, 0, Z0 + 5 + UPRIGHT / 2))])
place(pelvis, "electronics_tray", "PC_TRAY", [box((3, 140, 300), (2, 0, Z0 + 170))])
place(pelvis, "battery_cradle_L", "3DP_tor19_battery_cradle", [box((56, 70, 6), (-32, 40, Z0 + 8), 2)])
place(pelvis, "battery_cradle_R", "3DP_tor19_battery_cradle", [box((56, 70, 6), (-32, -40, Z0 + 8), 2)])
place(pelvis, "battery_1", "EL_BATTERY_6S", [box((52, 64, 166), (-32, 40, Z0 + 94), 3)])
place(pelvis, "battery_2", "EL_BATTERY_6S", [box((52, 64, 166), (-32, -40, Z0 + 94), 3)])
place(pelvis, "computer", "EL_PC_N100", [box((45, 128, 128), (28, 0, Z0 + 85), 4)])
for i, (sy, z) in enumerate(((1, 157), (-1, 157), (1, 175), (-1, 175))):
    place(pelvis, f"can_adapter_{i}", "EL_CANABLE", [box((60, 25, 12), (34, 45 * sy, Z0 + z))])
place(pelvis, "usb_hub", "EL_USB_HUB", [box((30, 60, 14), (19, 0, Z0 + 157), 2)])
place(pelvis, "buck_12v", "EL_BUCK_12V", [box((60, 45, 25), (-30, 0, Z0 + 195), 2)])
place(pelvis, "dist_block", "EL_DIST_BLOCK", [box((50, 60, 20), (29, 0, Z0 + 203), 2)])
place(pelvis, "contactor", "EL_CONTACTOR", [box((44, 60, 40), (-30, 0, Z0 + 241), 3)])
place(pelvis, "imu", "EL_IMU", [box((36, 36, 14), (30, 0, Z0 + 12.5), 2)])
place(pelvis, "estop", "EL_ESTOP", [box((10, 44, 44), (-(UX + 20), 0, Z0 + 420)), cyl("x", 20, 22, (-(UX + 36), 0, Z0 + 420))])
place(pelvis, "breaker", "EL_BREAKER", [box((18, 36, 60), (-(UX + 24), -55, Z0 + 350), 2)])
place(pelvis, "neck_post", "3DP_hea11_neck_post", [cyl("z", 22, 34, (10, 0, TOP + 17))])
hs = place(pelvis, "head_shell", "3DP_hea12_head_shell", [box((90, 110, 70), (15, 0, TOP + 34 + 35), 8)])
feat_cut_box(hs, (84, 104, 64), (15, 0, TOP + 34 + 32))
feat_cut_box(hs, (30, 92, 28), (60, 0, TOP + 34 + 45))
place(pelvis, "camera", "EL_CAMERA_D435I", [box((26, 90, 26), (55, 0, TOP + 34 + 45), 3)], optional="perception", inside=["head_shell"])


# --------------------------------------------------------------------------- legs
def build_leg(side):
    s = 1 if side == "L" else -1
    S = side
    base_id, bus = {"L": (11, "can0"), "R": (21, "can1")}[S]
    Y = HIP_Y
    # hip pitch: RS03 in the pelvis cup, output outboard (the figure's inset, green)
    kp = hipk[S]
    o1 = kp.joint_origin()
    l1 = link(f"hip_roll_bracket_{S}", f"Hip-roll bracket ({S})", f"leg_{S}", o1, f"hip_pitch_{S}")
    joint(f"hip_pitch_{S}", f"Hip pitch ({S})", "pelvis", l1["id"], o1, (0, 1, 0), (-90, 100), "RS03", S, bus, base_id, "pitch")
    add_kit(pelvis, l1, kp, f"hip_pitch_{S}", "3DP_kit03_coupler", mount_owner=cups[S], collar="+z", back=False)
    y1 = kp.child                                                     # 74
    # hip roll (abduction, red): RS03 on the bracket, axis x, output forward
    kr = Kit("RS03", "x", +1, 22, Y * s, HIP_Z)                       # body x -25.5..14, ring 22..44, child face 46
    bracket = place(l1, f"hip_roll_bracket_{S}", "3DP_leg21_hip_roll_bracket", [
        box((60, 10, 90), (-16, (abs(y1) + 5) * s, HIP_Z + 8), 3),
        box((16, 56, 60), (-34, (abs(y1) + 33) * s, HIP_Z - 6), 3),
    ])
    kp.child_plate_features(bracket, PLATE["RS03"])
    o2 = kr.joint_origin()
    l2 = link(f"hip_yaw_housing_{S}", f"Hip-yaw housing ({S})", f"leg_{S}", o2, f"hip_roll_{S}")
    joint(f"hip_roll_{S}", f"Hip roll ({S})", l1["id"], l2["id"], o2, (1, 0, 0), (-12, 45), "RS03", S, bus, base_id + 1, "roll")
    add_kit(l1, l2, kr, f"hip_roll_{S}", "3DP_kit03_coupler", mount_owner=bracket, collar=("-y" if s > 0 else "+y"), back=True, back_r=49)
    # hip rotation (blue): RS03 hanging under the roll actuator, output down onto the thigh socket
    FY = HIP_Z - 112.5
    ky = Kit("RS03", "z", -1, FY, 0, Y * s)                            # body z FY+8..FY+47.5, ring FY..FY-22, child face FY-24
    housing = place(l2, f"hip_yaw_housing_{S}", "3DP_leg22_hip_yaw_housing", [box((12, 96, 185), (kr.child + 6, (Y + 5) * s, FY + 42), 3)])
    kr.child_plate_features(housing, 12)
    o3 = ky.joint_origin()
    l3 = link(f"thigh_{S}", f"Thigh ({S})", f"leg_{S}", o3, f"hip_yaw_{S}")
    joint(f"hip_yaw_{S}", f"Hip yaw ({S})", l2["id"], l3["id"], o3, (0, 0, 1), (-90, 90), "RS03", S, bus, base_id + 2, "yaw")
    add_kit(l2, l3, ky, f"hip_yaw_{S}", "3DP_kit03_coupler", mount_owner=housing, collar="full", back=True)
    # thigh: our socket on the yaw coupler, Ø30 tube, then BHL's thigh end with the knee cradle
    zc = ky.child                                                      # FY-24
    sock = place(l3, f"thigh_socket_{S}", "3DP_leg23_thigh_socket", [
        cyl("z", 45, 10, (0, Y * s, zc - 5)),
        cyl("z", 21, BOND + 10, (0, Y * s, zc - 10 - (BOND + 10) / 2)),
    ])
    ky.child_plate_features(sock, 10)
    t_top = zc - 10 - 10
    socket_bore(sock, 0, Y * s, zc - 10 - (BOND + 10), t_top, TUBE30)
    kref = (KX, KY * s, KNEE_Z)
    kc = bhl_piece(l3, f"knee_cradle_{S}", "knee_cradle", kref, s, inside=[f"thigh_tube_{S}"],
                   notes="Cut 60 mm above the knee axis and drilled for the socket flange; the channel bored from Ø88 to Ø101 for the RS03 body and its mouth to Ø114, re-drilled 8 x M4 on PCD 98 for the ring; the walls thickened to 6 mm where the bore thins them. The end cap with the yoke stud stays.")
    cxk, cyk = section_xy("knee_cradle", s)
    ks, t_bot = tube_socket(l3, f"knee_socket_{S}", "3DP_v2_socket30", KX + cxk, KY * s + cyk, KNEE_Z + 60, +1, TUBE30 / 2, bx=0, by=Y * s, inside=[f"knee_cradle_{S}"])
    tube(l3, f"thigh_tube_{S}", "CF_TUBE_30", t_bot, t_top, 0, Y * s, TUBE30 / 2, [f"thigh_socket_{S}", f"knee_socket_{S}"])
    # knee: RS06 in BHL's cradle, output inboard to BHL's shank yoke; the yoke's outer plate on BHL's 6803 bearing
    kk = Kit("RS03", "y", -s, (KY + 24) * s, KX, KNEE_Z)              # child face at the output plane y = KY, body outboard; an RS03, not the 6512's RS06 class: 36 N·m does not hold the crouch at 28 kg
    o4 = kk.joint_origin()
    l4 = link(f"shank_{S}", f"Shank ({S})", f"leg_{S}", o4, f"knee_{S}")
    joint(f"knee_{S}", f"Knee ({S})", l3["id"], l4["id"], o4, (0, 1, 0), (0, 120), "RS03", S, bus, base_id + 3, "pitch")
    act, mount_occ, cp = add_kit(l3, l4, kk, f"knee_{S}", "3DP_kit03_coupler", mount_owner=kc, collar=None, back=False, ring_r=RING_IN_BHL["RS03"],
                                 coupler_inside=[f"shank_upper_{S}"])
    act["inside"] += [f"shank_upper_{S}"]
    su = bhl_piece(l4, f"shank_upper_{S}", "shank_upper", kref, s, inside=[f"knee_cradle_{S}", f"knee_{S}_bearing", f"shank_tube_{S}"],
                   notes="BHL's knee yoke: inner plate on the RS03 coupler (re-drilled 6 x M4 on PCD 30.36), outer plate on the 6803 stud bearing, cut 60 mm below the knee axis and drilled for the socket flange.")
    kk.child_plate_features(su, PLATE["RS03"])
    stud_and_bearing(kc, l4, f"knee_{S}_yoke_bearing", (KX, KY, KNEE_Z), s, 73, 94, 87.5, [f"shank_upper_{S}"])
    # shank: BHL's yoke end, our socket, Ø30 tube, our socket, BHL's shank end with the ankle cradle
    cxs, cys = section_xy("shank_upper", s)
    ss_, s_top = tube_socket(l4, f"shank_socket_top_{S}", "3DP_v2_socket30", KX + cxs, KY * s + cys, KNEE_Z - 60, -1, TUBE30 / 2, bx=AX, by=(AY + 11) * s, inside=[f"shank_upper_{S}"])
    aref = (AX, AY * s, ANKLE_Z)
    ac = bhl_piece(l4, f"ankle_cradle_{S}", "ankle_cradle", aref, s, inside=[f"shank_tube_{S}"],
                   notes="Cut 60 mm above the ankle axis and drilled for the socket flange; the cradle mouth bored to Ø86 and re-drilled 9 x M3 on PCD 73 for the RS02 ring.")
    cxa, cya = section_xy("ankle_cradle", s)
    as_, s_bot = tube_socket(l4, f"shank_socket_bottom_{S}", "3DP_v2_socket30", AX + cxa, AY * s + cya, ANKLE_Z + 60, +1, TUBE30 / 2, bx=AX, by=(AY + 11) * s, inside=[f"ankle_cradle_{S}"])
    tube(l4, f"shank_tube_{S}", "CF_TUBE_30", s_bot, s_top, AX, (AY + 11) * s, TUBE30 / 2, [f"shank_socket_top_{S}", f"shank_socket_bottom_{S}"])
    # ankle pitch: RS02 in BHL's cradle, output inboard to BHL's ankle bracket (a yoke on the 6803 stud bearing)
    ka = Kit("RS02", "y", -s, (AY + 14) * s, AX, ANKLE_Z)
    o5 = ka.joint_origin()
    l5 = link(f"ankle_block_{S}", f"Ankle bracket ({S})", f"leg_{S}", o5, f"ankle_pitch_{S}")
    joint(f"ankle_pitch_{S}", f"Ankle pitch ({S})", l4["id"], l5["id"], o5, (0, 1, 0), (-45, 45), "RS02", S, bus, base_id + 4, "pitch")
    act, mount_occ, cp = add_kit(l4, l5, ka, f"ankle_pitch_{S}", "3DP_kit02_coupler", mount_owner=ac, collar=None, back=False, ring_r=RING_IN_BHL["RS02"],
                                 coupler_inside=[f"ankle_bracket_{S}"])
    act["inside"] += [f"ankle_bracket_{S}"]
    ab = bhl_piece(l5, f"ankle_bracket_{S}", "ankle_bracket", aref, s, inside=[f"ankle_cradle_{S}", f"ankle_pitch_{S}_bearing", f"ankle_roll_{S}_coupler", f"foot_{S}"],
                   notes="BHL's ankle bracket, whole: inner plate on the RS02 coupler (re-drilled), outer plate on the 6803 stud bearing, roll boss on the ankle-roll coupler through a 10 mm spacer.")
    ka.child_plate_features(ab, PLATE["RS02"])
    stud_and_bearing(ac, l5, f"ankle_pitch_{S}_yoke_bearing", (AX, AY, ANKLE_Z), s, 58, 87, 82.5, [f"ankle_bracket_{S}"])
    # ankle roll: RS02 in BHL's foot cradle (axis forward, output backward onto the bracket's boss), BHL's foot and shoe
    kroll = Kit("RS02", "x", -1, RX + 14, FOOT_Y * s, ROLL_Z)
    o6 = kroll.joint_origin()
    l6 = link(f"foot_{S}", f"Foot ({S})", f"leg_{S}", o6, f"ankle_roll_{S}")
    joint(f"ankle_roll_{S}", f"Ankle roll ({S})", l5["id"], l6["id"], o6, (1, 0, 0), (-25, 25), "RS02", S, bus, base_id + 5, "roll")
    ft = bhl_piece(l6, f"foot_{S}", "foot", o6, s, inside=[f"ankle_bracket_{S}"],
                   notes="BHL's foot plate, shoe (TPU in BHL's build) and ankle-roll cradle, whole; the cradle raised 15 mm and its mouth bored for the RS02 ring (9 x M3 on PCD 73).")
    act, mount_occ, cp = add_kit(l6, l5, kroll, f"ankle_roll_{S}", "3DP_kit02_coupler", mount_owner=ft, collar="-z", back=True, ring_r=RING_IN_BHL["RS02"],
                                 coupler_inside=[f"ankle_bracket_{S}"])
    act["inside"] += [f"ankle_bracket_{S}"]
    kroll.child_plate_features(ab, PLATE["RS02"])
    ab["shapes"].append(cyl("x", 22, 10, (RX - 5, FOOT_Y * s, ROLL_Z)))          # the spacer, printed with the bracket


# --------------------------------------------------------------------------- arms
def build_arm(side):
    s = 1 if side == "L" else -1
    S = side
    base_id, bus = {"L": (31, "can2"), "R": (41, "can3")}[S]
    # shoulder pitch: RS06 (BHL's 6512 class) through the torso side, output face outside, as BHL's
    kp = Kit("RS06", "y", s, (SPY - 22) * s, 0, SH_Z)                 # body inboard of the lug face, ring outside the panel, child face at SPY
    mount = place(pelvis, f"shoulder_mount_{S}", "3DP_tor14_shoulder_mount", [
        box((30, 20, TOP - 5 - (SH_Z + 50)), (0, (UY - 23) * s, (TOP - 5 + SH_Z + 50) / 2), 2),   # tab up to the top plate, inside the uprights
    ])
    o1 = kp.joint_origin()
    a1 = link(f"shoulder_bracket_{S}", f"Shoulder bracket ({S})", f"arm_{S}", o1, f"shoulder_pitch_{S}")
    joint(f"shoulder_pitch_{S}", f"Shoulder pitch ({S})", "pelvis", a1["id"], o1, (0, 1, 0), (-180, 180), "RS06", S, bus, base_id, "pitch")
    act, mount_occ, cp = add_kit(pelvis, a1, kp, f"shoulder_pitch_{S}", "3DP_kit06_coupler", mount_owner=mount, collar="full", back=True,
                                 coupler_inside=[f"side_panel_{S}", f"shoulder_bracket_{S}"])
    act["inside"] += [f"side_panel_{S}"]
    panel = next(o for o in pelvis["parts"] if o["occ"] == f"side_panel_{S}")
    panel["inside"] = [f"shoulder_mount_{S}", f"shoulder_pitch_{S}_act", f"shoulder_pitch_{S}_bearing"]
    feat_cut_cyl(panel, "y", (0, (UY + 10) * s, SH_Z), 2 * RING_IN_BHL["RS06"] + 1, 0, 3 * s)
    # BHL's shoulder bracket: pitch output boss to the roll cradle (axis x, output forward)
    sref = (0, SPY * s, SH_Z)
    sb = bhl_piece(a1, f"shoulder_bracket_{S}", "shoulder_bracket", sref, s, inside=[f"shoulder_pitch_{S}_bearing", f"shoulder_pitch_{S}_coupler"],
                   notes="BHL's shoulder bracket, whole: boss on the RS06 coupler (re-drilled 6 x M4 on PCD 24); the roll cradle's mouth bored to Ø86 and re-drilled for the RS02 ring.")
    kp.child_plate_features(sb, PLATE["RS06"])
    kr = Kit("RS02", "x", +1, 25.5 - 14, ARM_Y * s, SH_Z)              # child face at x = 25.5, BHL's roll output plane
    o2 = kr.joint_origin()
    a2 = link(f"upper_arm_{S}", f"Upper arm ({S})", f"arm_{S}", o2, f"shoulder_roll_{S}")
    joint(f"shoulder_roll_{S}", f"Shoulder roll ({S})", a1["id"], a2["id"], o2, (1, 0, 0), (0, 150), "RS02", S, bus, base_id + 1, "roll")
    act, mount_occ, cp = add_kit(a1, a2, kr, f"shoulder_roll_{S}", "3DP_kit02_coupler", mount_owner=sb, collar=None, back=False, ring_r=RING_IN_BHL["RS02"],
                                 coupler_inside=[f"upper_arm_upper_{S}"])
    act["inside"] += [f"upper_arm_upper_{S}"]          # BHL's upper arm wraps around the roll module
    # upper arm: BHL's roll boss and plate end, our socket, Ø25 tube, our socket on BHL's yaw flange, RS02 in our cup under it
    uu = bhl_piece(a2, f"upper_arm_upper_{S}", "upper_arm_upper", o2, s, inside=[f"shoulder_bracket_{S}", f"shoulder_roll_{S}_bearing"],
                   notes="BHL's upper arm, top: the roll output boss (re-drilled for the RS02 coupler) and the plate, cut 40 mm below the axis and drilled for the socket flange.")
    kr.child_plate_features(uu, PLATE["RS02"])
    tx, ty = TX, ARM_Y * s
    us, u_top = tube_socket(a2, f"upper_arm_socket_top_{S}", "3DP_v2_socket25", tx, ty, SH_Z - 44, -1, TUBE25 / 2, inside=[f"upper_arm_upper_{S}"], size=(36, 50))
    yref = (YAW_X, ARM_Y * s, YAW_Z)
    ul = bhl_piece(a2, f"upper_arm_lower_{S}", "upper_arm_lower", yref, s, inside=[f"upper_arm_tube_{S}"],
                   notes="BHL's upper arm, bottom: the flange that carried the shoulder-yaw module, drilled for the socket flange on top and for our RS02 cup under it.")
    cxl, cyl_ = section_xy("upper_arm_lower", s)
    ls, u_bot = tube_socket(a2, f"upper_arm_socket_bottom_{S}", "3DP_v2_socket25", YAW_X + cxl, ARM_Y * s + cyl_, YAW_Z + 123 - 48, +1, TUBE25 / 2, bx=tx, by=ty, inside=[f"upper_arm_lower_{S}"], size=(50, 50))
    tube(a2, f"upper_arm_tube_{S}", "CF_TUBE_25", u_bot, u_top, tx, ty, TUBE25 / 2, [f"upper_arm_socket_top_{S}", f"upper_arm_socket_bottom_{S}"])
    ky = Kit("RS02", "z", -1, YAW_Z + 14, YAW_X, ARM_Y * s)             # output down, child face at YAW_Z
    o3 = ky.joint_origin()
    a3 = link(f"elbow_bracket_{S}", f"Elbow bracket ({S})", f"arm_{S}", o3, f"shoulder_yaw_{S}")
    joint(f"shoulder_yaw_{S}", f"Shoulder yaw ({S})", a2["id"], a3["id"], o3, (0, 0, 1), (-90, 90), "RS02", S, bus, base_id + 2, "yaw")
    act, mount_occ, cp = add_kit(a2, a3, ky, f"shoulder_yaw_{S}", "3DP_kit02_coupler", mount_owner=ul, collar="full", back=True, ring_r=45,
                                 coupler_inside=[f"elbow_bracket_{S}"])
    # BHL's elbow bracket: yaw output boss to the elbow cradle (axis y, output inboard); the forearm yoke on the 6803 stud bearing
    eb = bhl_piece(a3, f"elbow_bracket_{S}", "elbow_bracket", yref, s, inside=[f"shoulder_yaw_{S}_bearing", f"shoulder_yaw_{S}_coupler"],
                   notes="BHL's elbow bracket, whole: boss on the RS02 coupler (re-drilled); the elbow cradle's mouth bored to Ø86 and re-drilled for the RS02 ring; the end cap carries the yoke stud.")
    ky.child_plate_features(eb, PLATE["RS02"])
    ke = Kit("RS02", "y", -s, (EY + 14) * s, EX, ELBOW_Z)
    o4 = ke.joint_origin()
    a4 = link(f"forearm_{S}", f"Forearm ({S})", f"arm_{S}", o4, f"elbow_{S}")
    joint(f"elbow_{S}", f"Elbow ({S})", a3["id"], a4["id"], o4, (0, -1, 0), (0, 100), "RS02", S, bus, base_id + 3, "pitch")   # axis -y: positive flexion brings the hand forward; BHL allows 90
    act, mount_occ, cp = add_kit(a3, a4, ke, f"elbow_{S}", "3DP_kit02_coupler", mount_owner=eb, collar=None, back=False, ring_r=RING_IN_BHL["RS02"],
                                 coupler_inside=[f"forearm_upper_{S}"])
    act["inside"] += [f"forearm_upper_{S}"]
    eref = (EX, EY * s, ELBOW_Z)
    fu = bhl_piece(a4, f"forearm_upper_{S}", "forearm_upper", eref, s, inside=[f"elbow_bracket_{S}", f"elbow_{S}_bearing", f"forearm_tube_{S}"],
                   notes="BHL's forearm, top: the elbow yoke (inner plate on the RS02 coupler, outer plate on the 6803 stud bearing) and the plate, cut 40 mm below the axis and drilled for the socket flange.")
    ke.child_plate_features(fu, PLATE["RS02"])
    stud_and_bearing(eb, a4, f"elbow_{S}_yoke_bearing", (EX, EY, ELBOW_Z), s, 58, 91, 87.5, [f"forearm_upper_{S}"])
    fx, fy = EX, FY * s
    fs, f_top = tube_socket(a4, f"forearm_socket_top_{S}", "3DP_v2_socket25", fx, fy, ELBOW_Z - 44, -1, TUBE25 / 2, inside=[f"forearm_upper_{S}"], size=(50, 14))
    wref = (WX, WY * s, WRIST_Z)
    fl = bhl_piece(a4, f"forearm_lower_{S}", "forearm_lower", wref, s, inside=[f"forearm_tube_{S}"],
                   notes="BHL's forearm, bottom: the flange that carried the wrist module, drilled for the socket flange on top and for our RS02 cup under it.")
    cxw, cyw = section_xy("forearm_lower", s)
    ws, f_bot = tube_socket(a4, f"forearm_socket_bottom_{S}", "3DP_v2_socket25", WX + cxw, WY * s + cyw, WRIST_Z + 123 - 48, +1, TUBE25 / 2, bx=fx, by=fy, inside=[f"forearm_lower_{S}"], size=(50, 50))
    tube(a4, f"forearm_tube_{S}", "CF_TUBE_25", f_bot, f_top, fx, fy, TUBE25 / 2, [f"forearm_socket_top_{S}", f"forearm_socket_bottom_{S}"])
    kw = Kit("RS02", "z", -1, WRIST_Z + 14, WX, WY * s)
    o5 = kw.joint_origin()
    a5 = link(f"hand_{S}", f"Hand ({S})", f"arm_{S}", o5, f"wrist_roll_{S}")
    joint(f"wrist_roll_{S}", f"Wrist roll ({S})", a4["id"], a5["id"], o5, (0, 0, 1), (-180, 180), "RS02", S, bus, base_id + 4, "yaw")
    act, mount_occ, cp = add_kit(a4, a5, kw, f"wrist_roll_{S}", "3DP_kit02_coupler", mount_owner=fl, collar="full", back=True, ring_r=45,
                                 coupler_inside=[f"hand_flange_{S}"])
    flange = place(a5, f"hand_flange_{S}", "3DP_arm27_hand_flange", [box((50, 50, 6), (WX, WY * s, WRIST_Z - 3), 2)])
    kw.child_plate_features(flange, 6)
    feat_holes(flange, "z", (WX, WY * s, WRIST_Z - 6), 25 * math.sqrt(2), 4, INSERT["M3"], 0, 4, phase=45)
    # Amazing Hand: palm hanging from the flange, four fingers below, palm facing inboard
    place(a5, f"hand_{S}", "KIT_AMAZING_HAND", [
        box((70, 28, 95), (WX, WY * s, WRIST_Z - 6 - 47.5), 6),
        *[box((14, 20, 75), (WX + x, (WY + 2) * s, WRIST_Z - 6 - 95 - 37.5), 4) for x in (-24, -8, 8, 24)],
    ])


build_leg("L"); build_leg("R")
build_arm("L"); build_arm("R")
for j in JOINTS:
    if j["side"] == "R":
        ax = j["axis"]
        j["axis"] = [-ax[0], ax[1], -ax[2]]

# --------------------------------------------------------------------------- derived data (as v1, plus mesh masses)
for lnk in LINKS:
    ox, oy, oz = lnk["origin"]
    for o in lnk["parts"]:
        cat = CATALOG[o["part"]]
        lo = [1e9] * 3; hi = [-1e9] * 3; v = 0.0; mesh_g = 0
        for sh in o["shapes"]:
            a, b = bd.shape_bbox(sh)
            lo = [min(lo[k], a[k]) for k in range(3)]; hi = [max(hi[k], b[k]) for k in range(3)]
            if sh["t"] == "mesh":
                mesh_g += sh["mass_g"]
            elif cat["category"] in ("printed", "hardware"):
                v += vol(sh)
            sh["c"] = [round(sh["c"][0] - ox, 3), round(sh["c"][1] - oy, 3), round(sh["c"][2] - oz, 3)]
        for f in o.get("features", []):
            f["c"] = [round(f["c"][0] - ox, 3), round(f["c"][1] - oy, 3), round(f["c"][2] - oz, 3)]
        centre = [(lo[k] + hi[k]) / 2 for k in range(3)]
        o["center"] = [round(centre[0] - ox, 2), round(centre[1] - oy, 2), round(centre[2] - oz, 2)]
        o["center_world"] = [round(c, 1) for c in centre]
        dims = [round(hi[k] - lo[k], 1) for k in range(3)]
        if "dims" not in cat:
            cat["dims"] = dims
        if cat["category"] in ("printed", "hardware") and "mass_g" not in cat:
            m = MATERIALS[cat["material"]]
            cat["mass_g"] = round(v / 1000.0 * m["density"] * m["fill"]) + mesh_g
            if mesh_g:
                cat["bhl_mass_g"] = mesh_g
mass = {"actuators": 0, "printed": 0, "hardware": 0, "electronics": 0}
optional_mass = 0
for lnk in LINKS:
    for o in lnk["parts"]:
        cat = CATALOG[o["part"]]
        mg = cat.get("mass_g", 0)
        if o.get("optional"):
            optional_mass += mg; continue
        mass["actuators" if cat["category"] == "actuator" else cat["category"]] += mg
mass["fasteners_and_harness"] = 1000
mass_total = sum(mass.values())
bhl_parts = [p for p in CATALOG if p.startswith("BHL_")]
bhl_mass = sum(CATALOG[p]["bhl_mass_g"] * CATALOG[p]["qty"] for p in bhl_parts)
new_printed = [p for p in CATALOG if CATALOG[p]["category"] == "printed" and not p.startswith("BHL_") and CATALOG[p]["qty"] > 0]

# --------------------------------------------------------------------------- BOM
BOM_SECTIONS = []
row = bd.row


def section(sid, title, tier, blurb, rows):
    BOM_SECTIONS.append(dict(id=sid, title=title, tier=tier, blurb=blurb, rows=rows))


act_rows = []
for model in MODELS:
    pid = "ACT_" + model; a = ACT[model]
    joints_using = sorted({j["name"].split(" (")[0] for j in JOINTS if j["actuator"] == model})
    act_rows.append(row(pid, f"{a['name']} ({a['peak_nm']} N·m peak)", CATALOG[pid]["qty"], a["price"], "RobStride / Amazon US / AiFitLab", a["url"],
                        "Joints: " + ", ".join(joints_using) + "."))
section("actuators", "Actuators", "core",
        "Twenty-two RobStride actuators by BHL's own classes, one step up at the knee: RS02 (17 N·m) where BHL has a 5010, RS06 (36 N·m) where it has a 6512 at the shoulder pitch, RS03 (60 N·m) in the new hip stack and in the knee cradle, which is bored out for it (the 6512 class could not hold the crouch at adult size). BHL's 6512 costs $189 and its 5010 $136 in parts, each with a week of printing and assembly; the RobStrides cost more and arrive assembled.",
        act_rows)
section("hands", "Hands", "core",
        "The figure's dexterous hand, as an open design: Pollen Robotics' Amazing Hand, printed, eight bus servos each. BHL's own servo gripper fits the same flange.", [
            row("KIT_AMAZING_HAND", "Amazing Hand parts, one hand (8 bus servos, printed parts, board, fasteners)", 2, 220.0, "Pollen Robotics BOM", "https://github.com/pollen-robotics/AmazingHand", "Left and right. Print in PLA; servos on the forearm's USB drop."),
        ])
section("bhl", "Berkeley Humanoid Lite parts (printed from BHL's CAD)", "core",
        f"The {len(bhl_parts)} BHL part types this design keeps, {bhl_mass/1000:.2f} kg of PLA as BHL prints them, each cut or re-drilled as its note says; print from BHL's Onshape document (CC BY-SA 4.0) with the modifications applied. Their bearings and shoes come from BHL's bill of materials.", [
            row("MAT_PLA_BHL", "PLA filament for the BHL parts, 1 kg spool", math.ceil(bhl_mass * 1.35 / 1000 * 2) / 2, 26.0, "Bambu Lab / Hatchbox (BHL's choices)", "https://berkeley-humanoid-lite.gitbook.io/docs/getting-started-with-hardware/materials-and-parts-bom", "35 % for supports and failed prints.", unit_label="kg"),
            row("MAT_TPU_SHOE", "TPU 95A filament for the shoes, 1 kg spool", 0.5, 28.0, "Any", "", "BHL's shoe on the foot plate."),
            row("HW_6803_2RS", CATALOG["HW_6803_2RS"]["name"], CATALOG["HW_6803_2RS"]["qty"], 2.87, "Amazon (BHL BOM)", "https://www.amazon.com/dp/B09P21T5QV", CATALOG["HW_6803_2RS"]["notes"]),
            row("HW_STUD_17", CATALOG["HW_STUD_17"]["name"], CATALOG["HW_STUD_17"]["qty"], 1.5, "McMaster / Amazon", "", CATALOG["HW_STUD_17"]["notes"]),
        ])
section("structure", "Tubes, extrusion and plates", "core",
        "Carbon-fibre tubes between BHL's parts, as in the paper's figure; aluminium where a flat plate is cheaper than a print.", [
            row("CF_TUBE_30", CATALOG["CF_TUBE_30"]["name"] + ", 1000 mm", 1, 23.0, "Amazon", "https://www.amazon.com/s?k=carbon+fiber+tube+30mm+26mm+1000mm",
                f"Cut: thigh {tube_lengths['thigh_tube_L']} mm x 2, shank {tube_lengths['shank_tube_L']} mm x 2 = {2*tube_lengths['thigh_tube_L'] + 2*tube_lengths['shank_tube_L']:.0f} mm."),
            row("CF_TUBE_25", CATALOG["CF_TUBE_25"]["name"] + ", 1000 mm", 1, 18.0, "Amazon", "https://www.amazon.com/s?k=carbon+fiber+tube+25mm+22mm+1000mm",
                f"Cut: upper arm {tube_lengths['upper_arm_tube_L']} mm x 2, forearm {tube_lengths['forearm_tube_L']} mm x 2 = {2*tube_lengths['upper_arm_tube_L'] + 2*tube_lengths['forearm_tube_L']:.0f} mm."),
            row("HW_EPOXY", "Structural epoxy, 25 ml (tube bonds)", 1, 9.0, "Amazon / hardware store", "", "Loctite EA 9460 class or JB Weld original. Abrade the tube ends; 40 mm bond length; cross bolts carry the torque."),
            row("HW_2020_480", CATALOG["HW_2020_480"]["name"], CATALOG["HW_2020_480"]["qty"], 5.0, "Amazon / Misumi", "", CATALOG["HW_2020_480"]["notes"]),
            row("HW_2020_300", CATALOG["HW_2020_300"]["name"], CATALOG["HW_2020_300"]["qty"], 4.0, "Amazon / Misumi", "", CATALOG["HW_2020_300"]["notes"]),
            row("AL_TORSO_PLATE", CATALOG["AL_TORSO_PLATE"]["name"], CATALOG["AL_TORSO_PLATE"]["qty"], 28.0, "SendCutSend", "https://sendcutsend.com/", CATALOG["AL_TORSO_PLATE"]["notes"]),
            row("PC_SHEET", "Polycarbonate sheet 3 mm, 600 x 600 (panels and tray)", 1, 18.0, "hardware store", "", "Cut by hand to the panel drawings."),
            row("HW_TNUT_M5", "2020 T-nuts, M5, 50 pack", 1, 9.0, "Amazon", "", "Pelvis bars, plates, uprights."),
            row("HW_CORNER", "2020 inner corner brackets", 12, 0.7, "Amazon"),
        ])
section("electronics", "Electronics and power", "core",
        "As v1: one computer, one IMU, four CAN buses, two 6S packs in series (44.4 V, inside every RobStride model's 24-60 V range), breaker, contactor, E-stop. BHL runs 24 V with one 6S pack; the RobStrides want 48 V.", [
            row("EL_PC_N100", CATALOG["EL_PC_N100"]["name"], 1, 160.0, "Amazon", "", CATALOG["EL_PC_N100"]["notes"]),
            row("EL_IMU", CATALOG["EL_IMU"]["name"], 1, 57.0, "RobotShop", "https://www.robotshop.com/", CATALOG["EL_IMU"]["notes"]),
            row("EL_CANABLE", CATALOG["EL_CANABLE"]["name"], 4, 20.8, "Amazon", "https://www.amazon.com/", "One per bus: left leg, right leg, left arm, right arm."),
            row("EL_USB_HUB", CATALOG["EL_USB_HUB"]["name"], 1, 13.0, "Amazon"),
            row("EL_BATTERY_6S", CATALOG["EL_BATTERY_6S"]["name"], 2, 90.0, "Amazon", "", CATALOG["EL_BATTERY_6S"]["notes"]),
            row("EL_BUCK_12V", CATALOG["EL_BUCK_12V"]["name"], 1, 19.0, "Amazon", "", "Feeds the computer, the hub and the hand servos."),
            row("EL_DIST_BLOCK", CATALOG["EL_DIST_BLOCK"]["name"], 1, 18.0, "Amazon", "", CATALOG["EL_DIST_BLOCK"]["notes"]),
            row("EL_BREAKER", CATALOG["EL_BREAKER"]["name"], 1, 20.0, "Amazon", "", CATALOG["EL_BREAKER"]["notes"]),
            row("EL_CONTACTOR", CATALOG["EL_CONTACTOR"]["name"], 1, 25.0, "Amazon", "", CATALOG["EL_CONTACTOR"]["notes"]),
            row("EL_ESTOP", CATALOG["EL_ESTOP"]["name"], 1, 12.0, "Amazon", "", CATALOG["EL_ESTOP"]["notes"]),
            row("EL_TVS", "TVS diode, 53 V working / 85 V clamping (1.5KE62CA)", 6, 1.2, "DigiKey"),
            row("EL_VOLT_ALARM", "LiPo voltage alarm, 1-8S", 2, 7.0, "Amazon"),
            row("EL_FUSE_10A", "Blade fuse holder + 10 A fuse", 1, 4.0, "Amazon"),
        ])
section("harness", "Cables and connectors", "core",
        "Every limb is a daisy chain of XT30(2+2) drops; the tubes carry the loom inside them.", [
            row("CB_XT30_2P2_F", "Amass XT30(2+2)-F cable-side connector", 60, 0.75, "Amazon / AliExpress"),
            row("CB_EC5", "EC5 connector pair", 4, 2.0, "Amazon"),
            row("CB_WIRE_18", "18 AWG silicone wire, red + black, 12 m each", 1, 24.0, "Amazon", "", "Actuator drops."),
            row("CB_WIRE_12", "12 AWG silicone wire, red + black, 3 m each", 1, 14.0, "Amazon"),
            row("CB_CAT5", "Ethernet cable, 12 m (twisted pairs for CAN)", 1, 9.0, "Amazon"),
            row("CB_TERM", "120 Ω resistors, 1/4 W", 10, 0.2, "Amazon"),
            row("CB_SHRINK", "Heat-shrink assortment", 1, 8.0, "Amazon"),
            row("CB_LOOM", "Braided loom, 6 mm and 10 mm, 6 m each", 1, 12.0, "Amazon"),
            row("CB_USB", "USB-A to USB-C cables, 0.5 m and 1.5 m", 5, 3.0, "Amazon", "", "Hub to CAN adapters, IMU, and one per arm for the hand servo board."),
        ])


def kit_fastener_rows():
    n = {m: sum(1 for j in JOINTS if j["actuator"] == m) for m in ACT}
    rows = []
    for m in MODELS:
        I = ACT[m]
        if not n[m]:
            continue
        sc = SCREWS[m]
        rows.append(row(f"HW_OUT_{m}", f"{sc['out'][0]} x {sc['out'][1]} socket-head screw, output couplers ({m})", n[m] * I["out_n"], 0.15, "Amazon / McMaster", "",
                        f"{I['out_n']} per joint through the child plate and the coupler into the output boss; {sc['out'][2]} mm engaged of {I['out_depth']}."))
        rows.append(row(f"HW_LUG_{m}", f"{sc['lug'][0]} x {sc['lug'][1]} socket-head screw, mount rings ({m})", n[m] * I["lug_n"], 0.12, "Amazon / McMaster", "",
                        f"{I['lug_n']} per joint through the {I['mount_t']} mm ring (counterbored) into the front lugs; {sc['lug'][2]} mm engaged of {I['lug_depth']}."))
    rows.append(row("HW_PIN_4X10", "Dowel pin Ø4 x 10 mm, steel", sum(n[m] for m in MODELS) * 3, 0.3, "Amazon / McMaster", "", "Three per joint."))
    rows.append(row("HW_TUBE_BOLT", "M4 x 45 socket-head screw + nyloc, tube cross bolts", 16, 0.2, "Amazon / McMaster", "", "Two per tube end, drilled through the tube after bonding."))
    rows.append(row("HW_SOCKET_BOLT", "M4 x 16 socket-head screw + nyloc, socket flanges", 7 * 4 * 2, 0.15, "Amazon / McMaster", "", "Four per socket flange into the cut BHL arm."))
    return rows


section("hardware", "Bearings and fasteners", "core",
        "Thin-section bearings behind every joint; screw lengths computed from ring thickness, counterbore and thread depth so that every screw engages 75-100 % of the actuator's thread.", [
            row("HW_6809_2RS", CATALOG["HW_6809_2RS"]["name"], CATALOG["HW_6809_2RS"]["qty"], 3.0, "Amazon", "", CATALOG["HW_6809_2RS"]["notes"]),
            row("HW_6807_2RS", CATALOG["HW_6807_2RS"]["name"], CATALOG["HW_6807_2RS"]["qty"], 4.0, "Amazon", "", CATALOG["HW_6807_2RS"]["notes"]),
            row("HW_6707_2RS", CATALOG["HW_6707_2RS"]["name"], CATALOG["HW_6707_2RS"]["qty"], 3.0, "Amazon", "", CATALOG["HW_6707_2RS"]["notes"]),
        ] + kit_fastener_rows() + [
            row("HW_SCREWS", "M3 / M4 / M5 socket-head screw assortment, stainless", 1, 25.0, "Amazon"),
            row("HW_INSERT_M3", "Heat-set inserts M3 x 5, 200 pack", 1, 15.0, "Amazon"),
            row("HW_INSERT_M4", "Heat-set inserts M4 x 6, 100 pack", 1, 12.0, "Amazon"),
            row("HW_INSERT_M5", "Heat-set inserts M5 x 8, 50 pack", 1, 10.0, "Amazon"),
            row("HW_NUTS", "Nyloc nuts and washers M3 / M4 / M5", 1, 8.0, "Amazon"),
            row("HW_LOCTITE", "Threadlocker, medium strength", 1, 8.0, "Amazon", "", "Every actuator screw."),
        ])
printed = lambda mat: sum((CATALOG[p]["mass_g"] - CATALOG[p].get("bhl_mass_g", 0)) * CATALOG[p]["qty"] for p in CATALOG if CATALOG[p]["category"] == "printed" and CATALOG[p]["material"] == mat and not CATALOG[p].get("optional"))
kg = lambda g: math.ceil(g * 1.35 / 1000 * 2) / 2
section("filament", "Our printed parts (filament)", "core",
        f"About {printed('petg_cf')/1000:.1f} kg of structural prints (hip stack, sockets, couplers, mount rings and cups added to BHL's cradles) and {printed('pla')/1000:.1f} kg of PLA; quantities add 35 % for supports and failed prints. BHL's own parts are in their section.", [
            row("MAT_PETG_CF", "PETG-CF filament, 1 kg spool", kg(printed("petg_cf")), 30.0, "Bambu / Polymaker / Overture", "", "Every structural part of ours. PA-CF for the hip cups.", unit_label="kg"),
            row("MAT_PLA", "PLA filament, 1 kg spool", kg(printed("pla")), 20.0, "Any", "", "Head, cradles.", unit_label="kg"),
        ])
section("perception", "Optional: perception kit", "optional", "A camera when you need one.", [
    row("EL_CAMERA_D435I", CATALOG["EL_CAMERA_D435I"]["name"], 1, 300.0, "Intel / RealSense store", "https://www.intelrealsense.com/"),
    row("CB_USB3", "USB 3 cable, USB-C, 1 m", 1, 10.0, "Amazon"),
])
section("tools", "Tools (one-time)", "tools", "Not part of the robot.", [
    row("TL_PRINTER", "FDM printer with a hardened nozzle and 250 mm bed", 1, 700.0),
    row("TL_CHARGER", "LiPo balance charger, 6S, 200 W+", 1, 60.0),
    row("TL_PSU", "Bench power supply, 0-60 V, 10 A", 1, 90.0),
    row("TL_SOLDER", "Soldering station + heat-set insert tips", 1, 50.0),
    row("TL_DRIVERS", "Hex driver set, torque wrench 1-10 N·m", 1, 45.0),
    row("TL_TUBE", "Tube cutter for carbon fibre (abrasive), Ø30 drill guide", 1, 30.0, "", "", "Cut with an abrasive wheel, not a tube cutter; wear a mask."),
    row("TL_METER", "Multimeter", 1, 20.0),
    row("TL_STAND", "Gantry or hoist rated 60 kg, 1.9 m clear height", 1, 180.0),
])
tiers = {}
for sec in BOM_SECTIONS:
    sec["subtotal"] = round(sum(r["total"] for r in sec["rows"]), 2)
    tiers[sec["tier"]] = round(tiers.get(sec["tier"], 0) + sec["subtotal"], 2)

# --------------------------------------------------------------------------- poses, specs, outputs
POSES = {"zero": {"name": "Zero (standing)", "q": {}}, "crouch": {"name": "Crouch", "q": {}}, "reach": {"name": "Reach forward", "q": {}}, "wave": {"name": "Wave", "q": {}},
         "default": {"name": "Default standing (policy)", "q": {}}, "abduct": {"name": "Abduct 45, default arms", "q": {}}}
for S in ("L", "R"):
    POSES["crouch"]["q"].update({f"hip_pitch_{S}": -35, f"knee_{S}": 70, f"ankle_pitch_{S}": -35, f"shoulder_pitch_{S}": -20, f"elbow_{S}": 40})
    POSES["reach"]["q"].update({f"shoulder_pitch_{S}": -80, f"elbow_{S}": 20, f"hip_pitch_{S}": -8, f"knee_{S}": 16, f"ankle_pitch_{S}": -8})
    POSES["default"]["q"].update({f"hip_pitch_{S}": -8, f"knee_{S}": 16, f"ankle_pitch_{S}": -8, f"shoulder_pitch_{S}": -10, f"elbow_{S}": 30})
    POSES["abduct"]["q"].update({f"hip_roll_{S}": 45, f"shoulder_pitch_{S}": -10, f"elbow_{S}": 30})
POSES["wave"]["q"].update({"shoulder_pitch_R": -30, "shoulder_roll_R": 120, "elbow_R": 100, "wrist_roll_R": 40, "shoulder_pitch_L": -10, "elbow_L": 25})

lo = [1e9] * 3; hi = [-1e9] * 3
for lnk in LINKS:
    for o in lnk["parts"]:
        for sh in o["shapes"]:
            gc = [sh["c"][k] + lnk["origin"][k] for k in range(3)]
            a, b = bd.shape_bbox(dict(sh, c=gc))
            lo = [min(lo[k], a[k]) for k in range(3)]; hi = [max(hi[k], b[k]) for k in range(3)]
BHL_BASIS = dict(height_mm=800, mass_kg=16.3, thigh_mm=150, shank_mm=160, ankle_height_mm=100, upper_arm_mm=123, elbow_drop_mm=43, forearm_mm=123, hip_spacing_mm=160, arm_line_mm=176,
                 joints=22, actuators="10 x 6512 (M6C12 motor, printed cycloidal gearbox), 12 x 5010", licence="CC BY-SA 4.0 (assets), MIT (code)",
                 extensions_mm=dict(thigh=round(HIP_Z - 136.5 - KNEE_Z - 150, 1), shank=KNEE_Z - ANKLE_Z - 160, upper_arm=E_UA, forearm=E_FA))
SPECS = dict(
    dof=len(JOINTS), hand_dof=16, height_mm=round(hi[2]), width_mm=round(hi[1] - lo[1]), depth_mm=round(hi[0] - lo[0]),
    hip_spacing_mm=2 * HIP_Y, shoulder_spacing_mm=2 * ARM_Y, leg_hip_to_ground_mm=HIP_Z, thigh_mm=HIP_Z - KNEE_Z, shank_mm=KNEE_Z - ANKLE_Z,
    ankle_height_mm=ANKLE_Z, upper_arm_mm=round(SH_Z - ELBOW_Z, 1), forearm_mm=round(ELBOW_Z - WRIST_Z, 1), foot_length_mm=220, hand_spacing_mm=round(2 * WY, 1),
    tube_lengths_mm=tube_lengths, screws=SCREWS, mass_g=mass, mass_total_g=mass_total, optional_mass_g=optional_mass,
    bus_voltage="44.4 V nominal (2 x 6S), 50.4 V full", can_buses=4, can_bitrate="1 Mbit/s",
    bhl=BHL_BASIS, bhl_parts=bhl_parts, bhl_mass_g=bhl_mass, new_printed=new_printed,
)
robot = dict(
    meta=dict(name="Fully Open Humanoid", short="FOH", version=VERSION, variant="extended-bhl", units="mm",
              frame="X forward, Y left, Z up; ground at z = 0", generated_by="tools/build_v2.py",
              basis="Berkeley Humanoid Lite extended configuration (paper Fig. 5) from BHL's published parts, RobStride actuators, carbon-fibre tubes"),
    materials=MATERIALS, actuators={m: ACT[m] for m in MODELS}, catalog=CATALOG, links=LINKS, joints=JOINTS,
    poses=POSES, specs=SPECS,
    groups={"torso": "Pelvis, torso and head", "leg_L": "Left leg", "leg_R": "Right leg", "arm_L": "Left arm", "arm_R": "Right arm"},
)
bom = dict(meta=dict(version=VERSION, variant="extended-bhl", priced_as_of=PRICED_AS_OF, currency="USD"), sections=BOM_SECTIONS, tiers=tiers)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "robot_v2.json").write_text(json.dumps(robot, separators=(",", ":")) + "\n")
(OUT / "bom_v2.json").write_text(json.dumps(bom, indent=1) + "\n")
bd.write_urdf(ROOT / "assets" / "model" / "foh_v2_0.urdf")

if __name__ == "__main__":
    n_parts = sum(len(l["parts"]) for l in LINKS)
    print(f"FOH v{VERSION} (extended BHL): {len(LINKS)} links, {len(JOINTS)} joints, {n_parts} part occurrences, {len(CATALOG)} catalogue entries")
    print(f"Envelope: {SPECS['depth_mm']} x {SPECS['width_mm']} x {SPECS['height_mm']} mm; tubes {tube_lengths}")
    for k, v in mass.items():
        print(f"  mass {k:22s} {v/1000:6.2f} kg")
    print(f"  mass total (core)        {mass_total/1000:6.2f} kg   (+{optional_mass/1000:.2f} kg optional); BHL parts {bhl_mass/1000:.2f} kg in {len(bhl_parts)} types; our printed types {len(new_printed)}")
    for sec in BOM_SECTIONS:
        print(f"  ${sec['subtotal']:9,.2f}  {sec['title']}")
    for t, v in tiers.items():
        print(f"  {t:8s} ${v:,.2f}")
    print("arm line", ARM_Y, "yaw", (round(YAW_X, 1), YAW_Z), "elbow", (round(EX, 1), EY, ELBOW_Z), "wrist", (round(WX, 1), round(WY, 1), WRIST_Z))
