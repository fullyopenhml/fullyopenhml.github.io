#!/usr/bin/env python3
"""Fully Open Humanoid v2 (work in progress): the AI Sapiens K1 skeleton, built our way.

ROBOTIS' AI Sapiens K1 (hardware CERN-OHL-P-2.0) gives the skeleton: joint positions, limb lengths, the 23-joint
layout (6 per leg, 5 per arm, a waist yaw), the 1.36 m size, the forearm-forward zero pose. This script builds
that skeleton with our v1 toolkit: RobStride actuators in printed PETG-CF cups (the joint kits of build_data.py),
carbon-fibre tubes where a link is long enough to have one (thigh and shank), one-piece printed blocks where it
is not (the arms), 2020 extrusion and laser-cut plates for the torso, Amazing Hands. No covers: a 1X-style skin
goes over this skeleton later, so the structure only has to be right, not pretty.

Where our parts are bigger than the K1's, the skeleton moves by the difference and the deviation is recorded in
SPECS["k1_deviation"]: the hip line is 10 mm further out per side (RS03 Ø98 against QC080 Ø78), the ankle axis
26 mm higher (an RS03 at the K1's 64 mm ankle would touch the ground), the shoulder-yaw stack 45 mm longer.

Writes:  assets/data/robot_v2.json   assets/data/bom_v2.json   assets/model/foh_v2_0.urdf
Run:     python3 tools/build_v2.py
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
MATERIALS["cf_tube"] = {"name": "Carbon-fibre tube, 3K roll-wrapped", "color": "#2b2d31", "density": 1.55, "fill": 1.0}
MATERIALS["al_plate"] = {"name": "Aluminium 6061 plate, laser-cut", "color": "#b9bec6", "density": 2.70, "fill": 1.0}
MATERIALS["pc_sheet"] = {"name": "Polycarbonate sheet", "color": "#c9ced6", "color_alpha": 0.6, "density": 1.20, "fill": 1.0}
MATERIALS["hand"] = {"name": "Amazing Hand (printed, bus servos)", "color": "#8a93a0"}
bd.MATERIALS = MATERIALS

# --------------------------------------------------------------------------- actuators (the v1 interface table, RS04 unused here)
ACT = copy.deepcopy(bd.ACTUATORS)
ACT["RS03"]["mount_t"] = 22
ACT["RS06"]["mount_t"] = 20
ACT["RS02"]["mount_t"] = 12
bd.ACTUATORS = ACT
CLEAR["M5"] = 5.5
CBORE["M5"] = (10.0, 5.3)
PLATE = {"RS03": 10, "RS06": 8, "RS02": 8, "RS05": 5}      # child-plate thickness per model
MODELS = ("RS03", "RS06", "RS02", "RS05")


def screw_lengths():
    """Standard screw lengths for every kit, with thread-engagement checks (as v1)."""
    std = (8, 10, 12, 16, 20, 25, 30, 35, 40)
    out = {}
    for m in MODELS:
        I = ACT[m]
        res = {}
        if I["mount_t"]:
            through = I["mount_t"] - CBORE[I["lug_screw"]][1]
            ok = [L for L in std if 0.75 * I["lug_depth"] <= L - through <= I["lug_depth"]]
            assert ok, f"{m}: no standard lug screw engages 75-100 % of {I['lug_depth']} mm through {through} mm"
            res["lug"] = (I["lug_screw"], ok[0], round(ok[0] - through, 1))
            through_out = PLATE[m] + (I["mount_t"] + 2) - (I["step_h"] + I["boss_h"])
        else:
            res["rear"] = (I["rear_screw"], 10, None)
            through_out = I["sh_t"]
        ok = [L for L in std if 0.75 * I["out_depth"] <= L - through_out <= I["out_depth"]]
        assert ok, f"{m}: no standard output screw engages 75-100 % of {I['out_depth']} mm through {through_out} mm"
        res["out"] = (I["out_screw"], ok[0], round(ok[0] - through_out, 1))
        out[m] = res
    return out


SCREWS = screw_lengths()

# --------------------------------------------------------------------------- catalogue
P, H, E = "printed", "hardware", "electronics"
part("3DP_kit03_coupler", "RS03 coupler (output hub)", P, "petg_cf", process="FDM",
     notes="On the RS03 output boss, 3 x Ø4 dowels; six M4 x 30 through the child plate and coupler into the boss (PCD 30.36). Ø45 hub for the 6809 bearing.")
part("3DP_kit06_coupler", "RS06 coupler (output hub)", P, "petg_cf", process="FDM",
     notes="On the RS06 output boss, 3 x Ø4 dowels; six M4 x 25 through the child plate and coupler (PCD 24). Ø35 hub for the 6807 bearing.")
part("3DP_kit02_coupler", "RS02 coupler (output hub)", P, "petg_cf", process="FDM",
     notes="On the RS02 output boss, 3 x Ø4 dowels; six M4 x 25 through the child plate and coupler (PCD 24). Ø35 hub for the 6707 bearing.")
part("3DP_kit05_adapter", "RS05 output adapter", P, "petg_cf", process="FDM",
     notes="Ø44 x 5 disc: 6 x M4 x 8 counterbored on PCD 24 into the RS05 output, 3 x M3 inserts on Ø34 for the hand flange.")
# pelvis and waist
part("3DP_pel11_hip_cup", "Hip-pitch cup", P, "petg_cf", process="FDM", mirror=True,
     notes="RS03 mount ring (8 x M4 on PCD 98, 6809 pocket), collar straps open at the top, and a tab that bolts to the two pelvis bars with four M5 T-nuts.")
part("3DP_pel12_waist_plate", "Waist plate", P, "petg_cf", process="FDM",
     notes="8 mm plate across the pelvis bars (four M5 T-nuts); carries the waist coupler on its top face: the torso turns on it.")
part("3DP_tor13_waist_cup", "Waist cup", P, "petg_cf", process="FDM",
     notes="RS06 mount ring, collar and a flange that bolts to the underside of the torso bottom plate; the waist actuator hangs in it, output down onto the pelvis.")
# legs
part("3DP_leg21_hip_roll_bracket", "Hip-roll bracket", P, "petg_cf", process="FDM", mirror=True,
     notes="Plate on the hip-pitch coupler, web to the hip-roll RS03 cup: mount ring, straps and back plate, open on the inboard side.")
part("3DP_leg22_hip_yaw_housing", "Hip-yaw housing", P, "petg_cf", process="FDM", mirror=True,
     notes="Front plate on the hip-roll coupler, RS03 mount ring and collar for the hip-yaw actuator (axis vertical, output down).")
part("3DP_leg23_thigh_socket", "Thigh socket", P, "petg_cf", process="FDM", mirror=True,
     notes="Plate on the hip-yaw coupler with the Ø30 tube socket below it: 40 mm bond length, two M4 cross bolts.")
part("3DP_leg24_knee_cup", "Knee cup", P, "petg_cf", process="FDM", mirror=True,
     notes="Tube socket on top; full RS03 cup below: mount ring, collar, back plate and the Ø35 stub for the inner shank plate's bearing.")
part("3DP_leg25_shank_yoke", "Shank yoke", P, "petg_cf", process="FDM", mirror=True,
     notes="One print: outer plate on the knee coupler, inner plate on the stub bearing, cross member and the Ø30 tube socket under it.")
part("3DP_leg26_ankle_cup", "Ankle cup", P, "petg_cf", process="FDM", mirror=True,
     notes="Tube socket on top; RS03 ankle-pitch cup below with straps open to the front.")
part("3DP_leg27_ankle_bracket", "Ankle bracket", P, "petg_cf", process="FDM", mirror=True,
     notes="Plate on the ankle-pitch coupler; RS06 mount ring, collar and back plate for the ankle-roll actuator behind the shank.")
part("3DP_leg28_foot_bracket", "Foot bracket", P, "petg_cf", process="FDM", mirror=True,
     notes="Upright on the ankle-roll coupler, base flange with 4 x M5 to the aluminium foot plate.")
part("AL_FOOT_PLATE", "Foot plate, 3 mm 6061, laser-cut, 215 x 90", H, "al_plate", price=8.0, vendor="SendCutSend / local laser cutter", mirror=True,
     notes="Four M5 holes for the bracket, eight M4 for the sole. DXF generated from the model.")
part("3DP_leg29_sole", "Foot sole", P, "tpu", process="FDM", mirror=True, notes="TPU 95A, 100 % infill, 6 mm.")
# torso and head
part("AL_TORSO_PLATE", "Torso plate, 5 mm 6061, laser-cut, 200 x 150", H, "al_plate", price=22.0, vendor="SendCutSend / local laser cutter",
     notes="Two per robot (bottom and top). Four M5 for the uprights; the bottom one carries the waist cup, the top one the neck post.")
part("3DP_tor14_shoulder_mount", "Shoulder-pitch mount", P, "petg_cf", process="FDM", mirror=True,
     notes="RS06 mount ring, collar and back plate hung from the top plate; the ring passes through the side panel.")
part("PC_SIDE_PANEL", "Torso side panel, 3 mm polycarbonate", H, "pc_sheet", price=4.5, vendor="hardware store sheet, hand-cut", mirror=True,
     notes="Clearance hole for the shoulder-pitch ring and coupler.")
part("PC_BACK_PANEL", "Torso back panel, 3 mm polycarbonate", H, "pc_sheet", price=4.5, vendor="hardware store sheet, hand-cut", notes="Carries the E-stop and breaker.")
part("PC_FRONT_PANEL", "Torso front panel, 3 mm polycarbonate", H, "pc_sheet", price=4.5, vendor="hardware store sheet, hand-cut", notes="Removable; magnets.")
part("PC_TRAY", "Electronics tray, 3 mm polycarbonate", H, "pc_sheet", price=4.5, vendor="hardware store sheet, hand-cut", notes="Vertical, on the torso centreline; the power parts mount on it.")
part("3DP_tor19_battery_cradle", "Battery cradle", P, "pla", process="FDM", notes="One per pack.")
part("3DP_hea11_neck_post", "Neck post", P, "petg_cf", process="FDM")
part("3DP_hea12_head_shell", "Head shell", P, "pla", process="FDM", notes="Blank head with a RealSense pocket, the K1's head height. Camera optional.")
# arms
part("3DP_arm21_shoulder_bracket", "Shoulder-roll bracket", P, "petg_cf", process="FDM", mirror=True,
     notes="Plate on the shoulder-pitch coupler and the full RS06 cup for the shoulder-roll actuator, almost touching: the K1's shoulders are close together.")
part("3DP_arm22_upper_arm_yoke", "Upper-arm yoke", P, "petg_cf", process="FDM", mirror=True,
     notes="Front plate on the shoulder-roll coupler, shelf under it, RS02 mount ring and collar for the shoulder-yaw actuator (output down).")
part("3DP_arm23_upper_arm", "Upper arm", P, "petg_cf", process="FDM", mirror=True,
     notes="One print, no tube: plate on the shoulder-yaw coupler, a Ø36 boss, and the full RS02 elbow cup with the Ø35 stub for the inner forearm plate. The K1's upper arm is 115 mm; there is no room for a tube.")
part("3DP_arm25_forearm_yoke", "Forearm yoke with wrist collar", P, "petg_cf", process="FDM", mirror=True,
     notes="Outer plate on the elbow coupler, inner plate on the stub bearing, cross member at the far end, and the RS05 collar and rear plate on the cross member (4 x M3 into the RS05's rear face). The forearm points forward at the zero pose, as the K1's does.")
part("3DP_arm27_hand_flange", "Hand flange", P, "petg_cf", process="FDM",
     notes="50 x 50 x 6 plate: 3 x M3 to the RS05 adapter's inserts, four M3 inserts on a 25 mm square for the Amazing Hand's wrist.")
part("KIT_AMAZING_HAND", "Amazing Hand (Pollen Robotics), left or right", E, "hand", mass_g=400, price=220.0,
     vendor="Pollen Robotics BOM (printed parts + 8 bus servos + board)", mirror=True,
     notes="8-DOF printed hand, Apache-2.0, under 200 EUR in parts per Pollen. Its servo bus goes to the forearm's USB drop.")
# tubes and extrusion
part("CF_TUBE_30", "Carbon-fibre tube Ø30 x 26 mm, 3K roll-wrapped", H, "cf_tube", price=23.0, vendor="Amazon (WHABEST / cncarbonfiber) 1000 mm",
     notes="Thigh and shank links. One 1000 mm tube yields all four pieces. Bonded 40 mm into each socket with structural epoxy, plus two M4 cross bolts.")
part("HW_2020_330", "Aluminium 2020 extrusion, 329 mm, ends tapped M5", H, "al_ext", price=4.0, vendor="Amazon / Misumi", notes="Torso uprights.")
part("HW_2020_240", "Aluminium 2020 extrusion, 240 mm", H, "al_ext", price=3.5, vendor="Amazon / Misumi", notes="Pelvis bars: the hip cups and the waist plate bolt to them with T-nuts. 240 mm so the hanging hands pass beside them.")
# bearings
part("HW_6809_2RS", "Ball bearing 6809-2RS, 45 x 58 x 7 mm", H, "steel", price=3.0, vendor="Amazon", notes="Output support bearing of every RS03 joint.")
part("HW_6807_2RS", "Ball bearing 6807-2RS, 35 x 47 x 7 mm", H, "steel", price=4.0, vendor="Amazon", notes="Output support bearing of every RS06 joint.")
part("HW_6707_2RS", "Ball bearing 6707-2RS, 35 x 44 x 5 mm", H, "steel", price=3.0, vendor="Amazon",
     notes="Output support bearing of every RS02 joint, and the inner-plate support bearing at the knees and elbows.")
# electronics on the model (same as v0.2 / v1)
for pid in ("EL_PC_N100", "EL_BATTERY_6S", "EL_CANABLE", "EL_USB_HUB", "EL_BUCK_12V", "EL_DIST_BLOCK", "EL_IMU", "EL_ESTOP", "EL_BREAKER", "EL_CONTACTOR", "EL_CAMERA_D435I"):
    src = json.loads((OUT / "robot.json").read_text())["catalog"][pid]
    d = {k: v for k, v in src.items() if k not in ("qty", "dims")}
    d["qty"] = 0
    CATALOG[pid] = d

# --------------------------------------------------------------------------- key dimensions (mm): the K1 skeleton, with our deviations
K1 = dict(hip_pitch_z=714.5, hip_roll_z=684.5, hip_yaw_z=594, knee_z=357.5, ankle_z=63.5, hip_y=125, waist_z=795.5,
          shoulder_z=1114, shoulder_pitch_y=69, arm_y=146, shoulder_yaw_z=1045.3, elbow_z=930, wrist_x=68.7, head_top=1364, height=1355)
ROLL_Z = 70          # ankle-roll axis (K1: at the ankle, 63.5; the RS06 ring behind the shank needs 20 mm over the foot plate)
ANKLE_Z = 100        # ankle-pitch axis (K1 63.5: an RS03 body, r 49, would touch the ground; and at 25 deg of roll the foot plate rises into the ankle mount ring)
KNEE_Z = 357.5       # knee axis, as the K1
HIP_Z = 714.5        # hip-pitch axis, as the K1; the roll axis at the same height (K1: 30 lower)
HIP_Y = 135          # hip-roll / hip-yaw / knee centreline (K1 125: the RS03 roll cup needs 10 mm more than the QC080)
ANKLE_Y = HIP_Y      # ankle and foot centreline
BAR_Z = HIP_Z + 85   # pelvis 2020 bars, centre (z HIP_Z+75..+95)
WAIST_Z = BAR_Z + 10 + 8   # waist joint: the top of the 8 mm waist plate on the bars (K1 795.5)
TORSO_Z0 = WAIST_Z + 22 + 50.5   # torso bottom plate underside: above the waist cup's ring and the RS06 body with its back plate
SH_Z = 1114          # shoulder-pitch and shoulder-roll axes, as the K1
UPRIGHT = SH_Z - TORSO_Z0 + 105  # the top plate 100 mm over the shoulder axis
ARM_Y = 156          # shoulder-roll / yaw / elbow / wrist centreline (K1 146: at 120 deg of roll the upper-arm yoke reaches the shoulder-pitch ring)
ELBOW_Z = 930        # elbow axis, as the K1 (the shoulder-yaw output lands 45 mm lower than the K1's; the upper arm is a printed block)
TUBE30 = 30.0
BOND = 40            # tube bond length in every socket
Z0 = TORSO_Z0
TOP = Z0 + 5 + UPRIGHT + 5
tube_lengths = {}


def tube(lnk, occ, pid, z_lo, z_hi, y, r, inside):
    place(lnk, occ, pid, [cyl("z", r, z_hi - z_lo, (0, y, (z_lo + z_hi) / 2), r_in=r - 2.0)], inside=inside)
    tube_lengths[occ] = round(z_hi - z_lo, 1)


def socket_bore(occ, y, z_open, z_bottom, d):
    """Tube bore in a socket boss (axis z) from the open end to the bond bottom, plus two M4 cross bolts."""
    feat_cut_cyl(occ, "z", (0, y, min(z_open, z_bottom)), d + 0.4, 0, abs(z_open - z_bottom))
    for dz in (12, 28):
        zc = z_open - dz if z_open > z_bottom else z_open + dz
        feat_cut_cyl(occ, "x", (-25, y, zc), CLEAR["M4"], 0, 50)


# --------------------------------------------------------------------------- pelvis (root link) and waist
pelvis = link("pelvis", "Pelvis", "torso", (0, 0, 0))
for sx, tag in ((1, "F"), (-1, "B")):
    place(pelvis, f"pelvis_bar_{tag}", "HW_2020_240", [box((20, 240, 20), (66.5 * sx, 0, BAR_Z))])
hipk, cups = {}, {}
for S, s in (("L", 1), ("R", -1)):
    k = Kit("RS03", "y", s, 50 * s, 0, HIP_Z)      # body y 2.5..42, ring 50..72, child face 74
    hipk[S] = k
    cup = place(pelvis, f"hip_cup_{S}", "3DP_pel11_hip_cup", [box((170, 22, 15), (0, 61 * s, HIP_Z + 67.5), 2)])   # tab up to the bars, z HIP_Z+60..+75
    for sx in (1, -1):
        for yy in (55, 67):
            feat_cut_cyl(cup, "z", (66.5 * sx, yy * s, HIP_Z + 60), CLEAR["M5"], 0, 15)
    cups[S] = cup
wp = place(pelvis, "waist_plate", "3DP_pel12_waist_plate", [box((180, 160, 8), (0, 0, BAR_Z + 10 + 4), 2)])     # on the bars, z BAR_Z+10..+18
for sx in (1, -1):
    for sy in (1, -1):
        feat_cut_cyl(wp, "z", (66.5 * sx, 60 * sy, BAR_Z + 10), CLEAR["M5"], 0, 8)
# waist: RS06 in the torso, output down onto the waist plate
kw_ = Kit("RS06", "z", -1, WAIST_Z + 22, 0, 0)     # ring z WAIST_Z..+22 hmm: ring F-20..F, child face F-22 = WAIST_Z
torso = link("torso", "Torso and head", "torso", kw_.joint_origin(), "waist_yaw")
joint("waist_yaw", "Waist yaw", "pelvis", "torso", kw_.joint_origin(), (0, 0, 1), (-90, 90), "RS06", "C", "can0", 1, "yaw")
wcup = place(torso, "waist_cup", "3DP_tor13_waist_cup", [box((120, 120, 6), (0, 0, Z0 - 3), 4)])     # flange under the bottom plate
add_kit(torso, pelvis, kw_, "waist_yaw", "3DP_kit06_coupler", mount_owner=wcup, collar="full", back=True, ring_r=50)
kw_.child_plate_features(wp, PLATE["RS06"])

# --------------------------------------------------------------------------- torso frame, electronics, head (torso link)
UX, UY = 86.5, 65                       # uprights: x 76.5..96.5, y 55..75 (frame 200 deep, 150 wide; the K1 torso is 205 x 220)
bp = place(torso, "bottom_plate", "AL_TORSO_PLATE", [box((200, 150, 5), (0, 0, Z0 + 2.5))])
tp = place(torso, "top_plate", "AL_TORSO_PLATE", [box((200, 150, 5), (0, 0, Z0 + 5 + UPRIGHT + 2.5))])
for sx in (1, -1):
    for sy in (1, -1):
        feat_cut_cyl(bp, "z", (UX * sx, UY * sy, Z0), CLEAR["M5"], 0, 5)
        feat_cut_cyl(tp, "z", (UX * sx, UY * sy, Z0 + 5 + UPRIGHT), CLEAR["M5"], 0, 5)
        tag = ("F" if sx > 0 else "B") + ("L" if sy > 0 else "R")
        place(torso, f"upright_{tag}", "HW_2020_330", [box((20, 20, UPRIGHT), (UX * sx, UY * sy, Z0 + 5 + UPRIGHT / 2))])
for i in range(4):
    feat_cut_cyl(bp, "z", (45 * (1 if i < 2 else -1), 45 * (1 if i % 2 else -1), Z0), CLEAR["M4"], 0, 5)      # waist cup flange bolts
for S, s in (("L", 1), ("R", -1)):
    place(torso, f"side_panel_{S}", "PC_SIDE_PANEL", [box((190, 3, UPRIGHT - 20), (0, (UY + 11.5) * s, Z0 + 5 + UPRIGHT / 2))], inside=[f"shoulder_mount_{S}", f"shoulder_pitch_{S}_bearing"])
place(torso, "back_panel", "PC_BACK_PANEL", [box((3, 150, UPRIGHT), (-(UX + 11.5), 0, Z0 + 5 + UPRIGHT / 2))])
place(torso, "front_panel", "PC_FRONT_PANEL", [box((3, 150, UPRIGHT), (UX + 11.5, 0, Z0 + 5 + UPRIGHT / 2))])
place(torso, "electronics_tray", "PC_TRAY", [box((3, 110, 166), (1, 0, Z0 + 5 + 83))])      # up to the shoulder actuators' back plates
# back: the two packs; front: the computer with the IMU under it; above them the small boards; above the shoulder actuators the power parts
place(torso, "battery_cradle_L", "3DP_tor19_battery_cradle", [box((56, 70, 6), (-48, 36, Z0 + 8), 2)])
place(torso, "battery_cradle_R", "3DP_tor19_battery_cradle", [box((56, 70, 6), (-48, -36, Z0 + 8), 2)])
place(torso, "battery_1", "EL_BATTERY_6S", [box((52, 64, 166), (-48, 33, Z0 + 94), 3)])
place(torso, "battery_2", "EL_BATTERY_6S", [box((52, 64, 166), (-48, -33, Z0 + 94), 3)])
place(torso, "computer", "EL_PC_N100", [box((45, 128, 128), (52, 0, Z0 + 85), 4)])
place(torso, "imu", "EL_IMU", [box((36, 36, 14), (52, 0, Z0 + 12.5), 2)])
for i, (sy, z) in enumerate(((1, 156), (-1, 156), (1, 170), (-1, 170))):
    place(torso, f"can_adapter_{i}", "EL_CANABLE", [box((60, 25, 12), (46, 42.5 * sy, Z0 + z))])
place(torso, "usb_hub", "EL_USB_HUB", [box((30, 60, 14), (19, 0, Z0 + 157), 2)])
place(torso, "buck_12v", "EL_BUCK_12V", [box((60, 45, 25), (34, 0, Z0 + 310), 2)])
place(torso, "dist_block", "EL_DIST_BLOCK", [box((50, 60, 20), (29, 0, Z0 + 286), 2)])
place(torso, "contactor", "EL_CONTACTOR", [box((44, 60, 40), (-30, 0, Z0 + 296), 3)])
place(torso, "estop", "EL_ESTOP", [box((10, 44, 44), (-(UX + 18), 0, Z0 + 230)), cyl("x", 20, 22, (-(UX + 34), 0, Z0 + 230))])
place(torso, "breaker", "EL_BREAKER", [box((18, 36, 60), (-(UX + 22), -50, Z0 + 150), 2)])
place(torso, "neck_post", "3DP_hea11_neck_post", [cyl("z", 22, 34, (10, 0, TOP + 17))])
hs = place(torso, "head_shell", "3DP_hea12_head_shell", [box((90, 110, 100), (15, 0, TOP + 34 + 50), 8)])
feat_cut_box(hs, (84, 104, 94), (15, 0, TOP + 34 + 47))
feat_cut_box(hs, (30, 92, 28), (60, 0, TOP + 34 + 60))
place(torso, "camera", "EL_CAMERA_D435I", [box((26, 90, 26), (55, 0, TOP + 34 + 60), 3)], optional="perception", inside=["head_shell"])


# --------------------------------------------------------------------------- legs
def build_leg(side):
    s = 1 if side == "L" else -1
    S = side
    base_id, bus = {"L": (11, "can0"), "R": (21, "can1")}[S]
    Y = HIP_Y
    # hip pitch: RS03 in the pelvis cup, output outboard
    kp = hipk[S]
    o1 = kp.joint_origin()
    l1 = link(f"hip_roll_bracket_{S}", f"Hip-roll bracket ({S})", f"leg_{S}", o1, f"hip_pitch_{S}")
    joint(f"hip_pitch_{S}", f"Hip pitch ({S})", "pelvis", l1["id"], o1, (0, 1, 0), (-90, 100), "RS03", S, bus, base_id, "pitch")
    add_kit(pelvis, l1, kp, f"hip_pitch_{S}", "3DP_kit03_coupler", mount_owner=cups[S], collar="+z", back=False)
    y1 = kp.child                                                     # 74
    # hip roll: RS03 on the bracket, axis x, output forward
    kr = Kit("RS03", "x", +1, 22, Y * s, HIP_Z)                       # body x -25.5..14, ring 22..44, child face 46
    bracket = place(l1, f"hip_roll_bracket_{S}", "3DP_leg21_hip_roll_bracket", [
        box((60, 10, 90), (-16, (abs(y1) + 5) * s, HIP_Z + 8), 3),     # plate on the coupler, y 74..84
        box((16, 56, 60), (-34, (abs(y1) + 33) * s, HIP_Z - 6), 3),    # web to the back plate, y 79..135
    ])
    kp.child_plate_features(bracket, PLATE["RS03"])
    o2 = kr.joint_origin()
    l2 = link(f"hip_yaw_housing_{S}", f"Hip-yaw housing ({S})", f"leg_{S}", o2, f"hip_roll_{S}")
    joint(f"hip_roll_{S}", f"Hip roll ({S})", l1["id"], l2["id"], o2, (1, 0, 0), (-8, 45), "RS03", S, bus, base_id + 1, "roll")   # -8: the yaw collar meets the hip-pitch ring (10 mm closer than v1)
    add_kit(l1, l2, kr, f"hip_roll_{S}", "3DP_kit03_coupler", mount_owner=bracket, collar=("-y" if s > 0 else "+y"), back=True, back_r=49)
    # hip yaw: RS03 hanging under the roll actuator, output down
    FY = HIP_Z - 112.5
    ky = Kit("RS03", "z", -1, FY, 0, Y * s)                            # body z FY+8..FY+47.5, ring FY..FY-22, child face FY-24
    housing = place(l2, f"hip_yaw_housing_{S}", "3DP_leg22_hip_yaw_housing", [
        box((12, 96, 185), (kr.child + 6, (Y + 5) * s, FY + 42), 3),    # front plate on the roll coupler
    ])
    kr.child_plate_features(housing, 12)
    o3 = ky.joint_origin()
    l3 = link(f"thigh_{S}", f"Thigh ({S})", f"leg_{S}", o3, f"hip_yaw_{S}")
    joint(f"hip_yaw_{S}", f"Hip yaw ({S})", l2["id"], l3["id"], o3, (0, 0, 1), (-90, 90), "RS03", S, bus, base_id + 2, "yaw")
    add_kit(l2, l3, ky, f"hip_yaw_{S}", "3DP_kit03_coupler", mount_owner=housing, collar="full", back=True)
    # thigh: socket plate on the yaw coupler, Ø30 tube down to the knee cup
    zc = ky.child                                                      # FY-24
    sock = place(l3, f"thigh_socket_{S}", "3DP_leg23_thigh_socket", [
        cyl("z", 45, 10, (0, Y * s, zc - 5)),                           # round plate z zc-10..zc
        cyl("z", 21, BOND + 10, (0, Y * s, zc - 10 - (BOND + 10) / 2)),  # boss below the plate
    ])
    ky.child_plate_features(sock, 10)
    t_top = zc - 10 - 10
    kk = Kit("RS03", "y", s, (Y + 27.75) * s, 0, KNEE_Z)              # body centred on the leg line: y 115.25..154.75, ring to 184.75, child face 186.75
    knee_sock_top = KNEE_Z + 115
    t_bot = knee_sock_top - 5 - BOND
    socket_bore(sock, Y * s, zc - 10 - (BOND + 10), t_top, TUBE30)
    tube(l3, f"thigh_tube_{S}", "CF_TUBE_30", t_bot, t_top, Y * s, TUBE30 / 2, [f"thigh_socket_{S}", f"knee_cup_{S}"])
    kcup = place(l3, f"knee_cup_{S}", "3DP_leg24_knee_cup", [
        cyl("z", 21, knee_sock_top - (KNEE_Z + 51), (0, Y * s, (knee_sock_top + KNEE_Z + 51) / 2)),   # socket boss on the collar wall (body r 49)
    ])
    socket_bore(kcup, Y * s, knee_sock_top, t_bot, TUBE30)
    o4 = kk.joint_origin()
    l4 = link(f"shank_{S}", f"Shank ({S})", f"leg_{S}", o4, f"knee_{S}")
    joint(f"knee_{S}", f"Knee ({S})", l3["id"], l4["id"], o4, (0, 1, 0), (0, 120), "RS03", S, bus, base_id + 3, "pitch")
    add_kit(l3, l4, kk, f"knee_{S}", "3DP_kit03_coupler", mount_owner=kcup, collar="full", back=True, stub=True)
    # shank: one printed yoke, Ø30 tube, ankle cup
    yo = kk.child
    yi_near, yi_far = kk.inner
    yoke = place(l4, f"shank_yoke_{S}", "3DP_leg25_shank_yoke", [
        box((72, 10, 150), (0, yo + 5 * s, KNEE_Z - 25), 4),           # outer plate z KNEE_Z+50..-100
        box((72, 10, 150), (0, yi_far + 5 * s, KNEE_Z - 25), 4),       # inner plate
        box((72, abs(yo - yi_far) + 10, 20), (0, (yo + yi_far) / 2 + 5 * s, KNEE_Z - 90), 3),   # cross member z -100..-80
        cyl("z", 21, BOND + 10, (0, Y * s, KNEE_Z - 100 - (BOND + 10) / 2)),                     # socket boss under it
    ], inside=[f"knee_cup_{S}"])
    kk.child_plate_features(yoke, 10)
    kk.inner_plate_features(yoke)
    place(l4, f"knee_support_bearing_{S}", kk.I["sup_bearing"], [kk.sup_bearing()], inside=[f"shank_yoke_{S}", f"knee_cup_{S}"])
    s_top = KNEE_Z - 100 - 10
    ka = Kit("RS03", "y", s, (ANKLE_Y + 28) * s, 0, ANKLE_Z)           # body y 115.5..155, ring 163..185, child face 187
    ank_sock_top = ANKLE_Z + 105           # 2.5 mm under the yoke's socket boss on this short shank
    s_bot = ank_sock_top - 5 - BOND
    socket_bore(yoke, Y * s, KNEE_Z - 100 - (BOND + 10), s_top, TUBE30)
    tube(l4, f"shank_tube_{S}", "CF_TUBE_30", s_bot, s_top, Y * s, TUBE30 / 2, [f"shank_yoke_{S}", f"ankle_cup_{S}"])
    acup = place(l4, f"ankle_cup_{S}", "3DP_leg26_ankle_cup", [
        cyl("z", 21, ank_sock_top - (ANKLE_Z + 51), (0, Y * s, (ank_sock_top + ANKLE_Z + 51) / 2)),   # socket boss on the collar wall
    ])
    socket_bore(acup, Y * s, ank_sock_top, s_bot, TUBE30)
    o5 = ka.joint_origin()
    l5 = link(f"ankle_block_{S}", f"Ankle block ({S})", f"leg_{S}", o5, f"ankle_pitch_{S}")
    joint(f"ankle_pitch_{S}", f"Ankle pitch ({S})", l4["id"], l5["id"], o5, (0, 1, 0), (-45, 45), "RS03", S, bus, base_id + 4, "pitch")
    add_kit(l4, l5, ka, f"ankle_pitch_{S}", "3DP_kit03_coupler", mount_owner=acup, collar="+x", back=True)
    # ankle roll: RS06 behind the shank, axis x, output forward; foot upright on its coupler
    kroll = Kit("RS06", "x", +1, -93, ANKLE_Y * s, ROLL_Z)             # body x -130..-97, ring -93..-73, child face -71
    ab = place(l5, f"ankle_bracket_{S}", "3DP_leg27_ankle_bracket", [
        box((180, 10, 90), (-45, ka.child + 5 * s, ANKLE_Z + 5), 3),    # plate y 187..197, x -135..45
    ])
    ka.child_plate_features(ab, PLATE["RS03"])
    o6 = kroll.joint_origin()
    l6 = link(f"foot_{S}", f"Foot ({S})", f"leg_{S}", o6, f"ankle_roll_{S}")
    joint(f"ankle_roll_{S}", f"Ankle roll ({S})", l5["id"], l6["id"], o6, (1, 0, 0), (-25, 25), "RS06", S, bus, base_id + 5, "roll")   # 25: the foot plate edge rises to the ankle-pitch ring
    add_kit(l5, l6, kroll, f"ankle_roll_{S}", "3DP_kit06_coupler", mount_owner=ab, collar="full", back=True)
    fbk = place(l6, f"foot_bracket_{S}", "3DP_leg28_foot_bracket", [
        box((10, 54, 72), (kroll.child + 5, ANKLE_Y * s, 56), 3),       # upright x -67..-57, z 20..92
        box((44, 54, 8), (kroll.child + 22, ANKLE_Y * s, 23), 2),       # base flange on the foot plate, z 19..27
    ])
    kroll.child_plate_features(fbk, PLATE["RS06"])
    fp = place(l6, f"foot_plate_{S}", "AL_FOOT_PLATE", [box((215, 90, 3), (-7.5, ANKLE_Y * s, 17.5))])       # x -115..100, z 16..19: toe 100 ahead of the ankle, the roll actuator overhangs the heel
    sole = place(l6, f"sole_{S}", "3DP_leg29_sole", [box((215, 90, 6), (-7.5, ANKLE_Y * s, 13), 2)])         # z 10..16
    for occ_, t0, t1 in ((fbk, 19, 27), (fp, 16, 19), (sole, 10, 16)):
        for dx in (-14, 14):
            for dy in (-18, 18):
                feat_cut_cyl(occ_, "z", (kroll.child + 22 + dx, ANKLE_Y * s + dy, t0), CLEAR["M5"], 0, t1 - t0)


# --------------------------------------------------------------------------- arms (forearm forward at the zero pose, as the K1)
def build_arm(side):
    s = 1 if side == "L" else -1
    S = side
    base_id, bus = {"L": (31, "can2"), "R": (41, "can3")}[S]
    # shoulder pitch: RS06 inside the torso, output outboard through the side panel
    kp = Kit("RS06", "y", s, 60 * s, 0, SH_Z)                          # body y 17.5..56, ring 60..80, child face 82
    mount = place(torso, f"shoulder_mount_{S}", "3DP_tor14_shoulder_mount", [
        box((30, 14, TOP - 5 - (SH_Z + 50)), (0, 40 * s, (TOP - 5 + SH_Z + 50) / 2), 2),   # tab up to the top plate
    ])
    o1 = kp.joint_origin()
    a1 = link(f"shoulder_roll_bracket_{S}", f"Shoulder-roll bracket ({S})", f"arm_{S}", o1, f"shoulder_pitch_{S}")
    joint(f"shoulder_pitch_{S}", f"Shoulder pitch ({S})", "torso", a1["id"], o1, (0, 1, 0), (-180, 180), "RS06", S, bus, base_id, "pitch")
    add_kit(torso, a1, kp, f"shoulder_pitch_{S}", "3DP_kit06_coupler", mount_owner=mount, collar="full", back=True, coupler_inside=[f"side_panel_{S}"])
    # shoulder roll: RS06 right beside the pitch coupler, axis x, output forward
    kr = Kit("RS06", "x", +1, 14, ARM_Y * s, SH_Z)                     # body x -23..10, ring 14..34, child face 36
    y1 = kp.child                                                      # 82
    pt = PLATE["RS06"]
    br = place(a1, f"shoulder_bracket_{S}", "3DP_arm21_shoulder_bracket", [
        box((54, pt, 90), (-13, (abs(y1) + pt / 2) * s, SH_Z), 3),       # plate y 82..90
        box((50, ARM_Y - 49 - (abs(y1) + pt), 56), (-16, ((abs(y1) + pt) + (ARM_Y - 49)) / 2 * s, SH_Z), 3),   # short beam to the roll cup
    ])
    kp.child_plate_features(br, pt)
    o2 = kr.joint_origin()
    a2 = link(f"upper_arm_yoke_{S}", f"Upper-arm yoke ({S})", f"arm_{S}", o2, f"shoulder_roll_{S}")
    joint(f"shoulder_roll_{S}", f"Shoulder roll ({S})", a1["id"], a2["id"], o2, (1, 0, 0), (0, 150), "RS06", S, bus, base_id + 1, "roll")
    add_kit(a1, a2, kr, f"shoulder_roll_{S}", "3DP_kit06_coupler", mount_owner=br, collar="full", back=True, ring_r=49)
    # shoulder yaw: RS02 under the roll actuator, output down
    FYa = SH_Z - 99.5
    ky = Kit("RS02", "z", -1, FYa, 0, ARM_Y * s)
    yoke = place(a2, f"upper_arm_yoke_{S}", "3DP_arm22_upper_arm_yoke", [
        box((12, 96, 104), (kr.child + 6, ARM_Y * s, SH_Z - 2), 3),      # front plate on the roll coupler
        box((76, 96, 10), (12, ARM_Y * s, SH_Z - 56), 3),                # shelf under the roll cup
    ])
    kr.child_plate_features(yoke, 12)
    o3 = ky.joint_origin()
    a3 = link(f"upper_arm_{S}", f"Upper arm ({S})", f"arm_{S}", o3, f"shoulder_yaw_{S}")
    joint(f"shoulder_yaw_{S}", f"Shoulder yaw ({S})", a2["id"], a3["id"], o3, (0, 0, 1), (-12, 90), "RS02", S, bus, base_id + 2, "yaw")   # with the forearm forward, inward yaw meets the torso from 13 deg
    add_kit(a2, a3, ky, f"shoulder_yaw_{S}", "3DP_kit02_coupler", mount_owner=yoke, collar="full", back=False, ring_r=40)
    # upper arm: one printed block from the yaw coupler plate down to the elbow cup (no tube: 70 mm)
    zc = ky.child
    ke = Kit("RS02", "y", s, (ARM_Y + 19) * s, 0, ELBOW_Z)
    ublock = place(a3, f"upper_arm_{S}", "3DP_arm23_upper_arm", [
        box((70, 70, 8), (0, ARM_Y * s, zc - 4), 3),
        cyl("z", 18, (zc - 8) - (ELBOW_Z + 34), (0, ARM_Y * s, ((zc - 8) + (ELBOW_Z + 34)) / 2)),   # boss down to the elbow collar (body r 32.5)
    ])
    ky.child_plate_features(ublock, PLATE["RS02"])
    o4 = ke.joint_origin()
    a4 = link(f"forearm_{S}", f"Forearm ({S})", f"arm_{S}", o4, f"elbow_{S}")
    # elbow: zero = forearm horizontal (90 deg flexed, as the K1); positive = more flexion (hand toward the shoulder)
    joint(f"elbow_{S}", f"Elbow ({S})", a3["id"], a4["id"], o4, (0, -1, 0), (-60, 40), "RS02", S, bus, base_id + 3, "pitch")
    add_kit(a3, a4, ke, f"elbow_{S}", "3DP_kit02_coupler", mount_owner=ublock, collar="full", back=True, stub=True, ring_r=40)
    # forearm: yoke pointing forward (+x) from the elbow, cross member at its far end, RS05 wrist on the cross member, axis x
    yo = ke.child
    yi_near, yi_far = ke.inner
    kw = Kit("RS05", "x", +1, 96, ARM_Y * s, ELBOW_Z)                  # rear plate x 47..55, body 55..96, adapter face 104
    fyoke = place(a4, f"forearm_yoke_{S}", "3DP_arm25_forearm_yoke", [
        box((100, 8, 60), (5, yo + 4 * s, ELBOW_Z), 4),                 # outer plate x -45..55
        box((100, 8, 60), (5, yi_far + 4 * s, ELBOW_Z), 4),             # inner plate
        box((8, abs(yo - yi_far) + 8, 60), (51, (yo + yi_far) / 2 + 4 * s, ELBOW_Z), 3),   # cross member x 47..55, outside the elbow ring (r 45)
        kw.seg(-41, -12, 29, r_in=23.25), kw.seg(-49, -41, 25),         # RS05 collar and rear plate (x 47..55, on the cross member)
    ], inside=[f"upper_arm_{S}"])
    ke.child_plate_features(fyoke, PLATE["RS02"])
    ke.inner_plate_features(fyoke)
    place(a4, f"elbow_support_bearing_{S}", ke.I["sup_bearing"], [ke.sup_bearing()], inside=[f"forearm_yoke_{S}", f"upper_arm_{S}"])
    feat_holes(fyoke, "x", kw.pt(-41), kw.I["rear_pcd"], kw.I["rear_n"], CLEAR["M3"], 0, -8.0, phase=45)
    o5 = kw.joint_origin()
    a5 = link(f"hand_{S}", f"Hand ({S})", f"arm_{S}", o5, f"wrist_roll_{S}")
    joint(f"wrist_roll_{S}", f"Wrist roll ({S})", a4["id"], a5["id"], o5, (1, 0, 0), (-180, 180), "RS05", S, bus, base_id + 4, "roll")
    act = place(a4, f"wrist_roll_{S}_act", "ACT_RS05", kw.actuator_shapes(), actuator="RS05", inside=[f"forearm_yoke_{S}"])
    wa = place(a5, f"wrist_roll_{S}_coupler", "3DP_kit05_adapter", kw.coupler_shapes(), inside=[f"wrist_roll_{S}_act"])
    kw.coupler_features(wa)
    WX = kw.child                                                      # adapter face, x 104
    fl = place(a5, f"hand_flange_{S}", "3DP_arm27_hand_flange", [box((6, 50, 50), (WX + 3, ARM_Y * s, ELBOW_Z), 2)])
    feat_holes(fl, "x", (WX, ARM_Y * s, ELBOW_Z), 34, 3, CLEAR["M3"], 0, 6, phase=30)
    feat_holes(fl, "x", (WX + 6, ARM_Y * s, ELBOW_Z), 25 * math.sqrt(2), 4, INSERT["M3"], 0, -4, phase=45)
    # Amazing Hand: palm forward from the flange, four fingers beyond, palm facing inboard
    hand = place(a5, f"hand_{S}", "KIT_AMAZING_HAND", [
        box((95, 28, 70), (WX + 6 + 47.5, ARM_Y * s, ELBOW_Z), 6),
        *[box((75, 20, 14), (WX + 6 + 95 + 37.5, (ARM_Y + 2) * s, ELBOW_Z + z), 4) for z in (-24, -8, 8, 24)],
    ])
    return hand


build_leg("L"); build_leg("R")
build_arm("L"); build_arm("R")
for j in JOINTS:
    if j["side"] == "R":
        ax = j["axis"]
        j["axis"] = [-ax[0], ax[1], -ax[2]]

# --------------------------------------------------------------------------- derived data (as v1)
for lnk in LINKS:
    ox, oy, oz = lnk["origin"]
    for o in lnk["parts"]:
        cat = CATALOG[o["part"]]
        lo = [1e9] * 3; hi = [-1e9] * 3; v = 0.0
        for sh in o["shapes"]:
            a, b = bd.shape_bbox(sh)
            lo = [min(lo[k], a[k]) for k in range(3)]; hi = [max(hi[k], b[k]) for k in range(3)]
            if cat["category"] in ("printed", "hardware"):
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
mass["fasteners_and_harness"] = 1000
mass_total = sum(mass.values())

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
        "Twenty-three RobStride actuators in four models, chosen by the K1's own torque classes: RS03 (60 N·m) where the K1 has a QC080 in the legs, RS06 (36 N·m) at the waist, the ankle roll and the two big shoulder joints, RS02 and RS05 down the arm.",
        act_rows)
section("hands", "Hands", "core",
        "Pollen Robotics' Amazing Hand, printed, eight bus servos each. The K1's own hands are passive rubber; their published mesh printed in TPU is the cheaper option on the same flange.", [
            row("KIT_AMAZING_HAND", "Amazing Hand parts, one hand (8 bus servos, printed parts, board, fasteners)", 2, 220.0, "Pollen Robotics BOM", "https://github.com/pollen-robotics/AmazingHand", "Left and right. Print in PLA; servos on the forearm's USB drop."),
        ])
section("structure", "Tubes, extrusion and plates", "core",
        "One carbon-fibre tube per thigh and shank; the arms are too short for tubes at this size and are printed blocks. Aluminium where a flat plate is cheaper than a print.", [
            row("CF_TUBE_30", CATALOG["CF_TUBE_30"]["name"] + ", 1000 mm", 1, 23.0, "Amazon", "https://www.amazon.com/s?k=carbon+fiber+tube+30mm+26mm+1000mm",
                f"Cut: thigh {tube_lengths['thigh_tube_L']} mm x 2, shank {tube_lengths['shank_tube_L']} mm x 2 = {2*tube_lengths['thigh_tube_L'] + 2*tube_lengths['shank_tube_L']:.0f} mm."),
            row("HW_EPOXY", "Structural epoxy, 25 ml (tube bonds)", 1, 9.0, "Amazon / hardware store", "", "Loctite EA 9460 class or JB Weld original. Abrade the tube ends; 40 mm bond length; cross bolts carry the torque."),
            row("HW_2020_330", CATALOG["HW_2020_330"]["name"], CATALOG["HW_2020_330"]["qty"], 4.0, "Amazon / Misumi", "", CATALOG["HW_2020_330"]["notes"]),
            row("HW_2020_240", CATALOG["HW_2020_240"]["name"], CATALOG["HW_2020_240"]["qty"], 3.5, "Amazon / Misumi", "", CATALOG["HW_2020_240"]["notes"]),
            row("AL_TORSO_PLATE", CATALOG["AL_TORSO_PLATE"]["name"], CATALOG["AL_TORSO_PLATE"]["qty"], 22.0, "SendCutSend", "https://sendcutsend.com/", CATALOG["AL_TORSO_PLATE"]["notes"]),
            row("AL_FOOT_PLATE", CATALOG["AL_FOOT_PLATE"]["name"], CATALOG["AL_FOOT_PLATE"]["qty"], 8.0, "SendCutSend", "https://sendcutsend.com/", CATALOG["AL_FOOT_PLATE"]["notes"]),
            row("PC_SHEET", "Polycarbonate sheet 3 mm, 600 x 600 (panels and tray)", 1, 18.0, "hardware store", "", "Cut by hand to the panel drawings."),
            row("HW_TNUT_M5", "2020 T-nuts, M5, 50 pack", 1, 9.0, "Amazon", "", "Pelvis bars, waist plate, torso plates."),
            row("HW_CORNER", "2020 inner corner brackets", 12, 0.7, "Amazon"),
        ])
section("electronics", "Electronics and power", "core",
        "As v1: one computer, one IMU, four CAN buses, two 6S packs in series (44.4 V), breaker, contactor, E-stop. The K1 has a Jetson Orin NX and a 46.8 V pack; the published policies are ONNX files the N100 runs at control rate.", [
            row("EL_PC_N100", CATALOG["EL_PC_N100"]["name"], 1, 160.0, "Amazon", "", CATALOG["EL_PC_N100"]["notes"]),
            row("EL_IMU", CATALOG["EL_IMU"]["name"], 1, 57.0, "RobotShop", "https://www.robotshop.com/", CATALOG["EL_IMU"]["notes"]),
            row("EL_CANABLE", CATALOG["EL_CANABLE"]["name"], 4, 20.8, "Amazon", "https://www.amazon.com/", "One per bus: left leg and waist, right leg, left arm, right arm."),
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
        "Every limb is a daisy chain of XT30(2+2) drops; the leg tubes carry the loom inside them.", [
            row("CB_XT30_2P2_F", "Amass XT30(2+2)-F cable-side connector", 60, 0.75, "Amazon / AliExpress"),
            row("CB_EC5", "EC5 connector pair", 4, 2.0, "Amazon"),
            row("CB_WIRE_18", "18 AWG silicone wire, red + black, 10 m each", 1, 20.0, "Amazon", "", "Actuator drops."),
            row("CB_WIRE_12", "12 AWG silicone wire, red + black, 3 m each", 1, 14.0, "Amazon"),
            row("CB_CAT5", "Ethernet cable, 10 m (twisted pairs for CAN)", 1, 8.0, "Amazon"),
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
                        f"{I['out_n']} per joint through the {PLATE[m]} mm child plate and the coupler into the output boss; {sc['out'][2]} mm engaged of {I['out_depth']}."))
        if I["mount_t"]:
            rows.append(row(f"HW_LUG_{m}", f"{sc['lug'][0]} x {sc['lug'][1]} socket-head screw, mount rings ({m})", n[m] * I["lug_n"], 0.12, "Amazon / McMaster", "",
                            f"{I['lug_n']} per joint through the {I['mount_t']} mm ring (counterbored) into the front lugs; {sc['lug'][2]} mm engaged of {I['lug_depth']}."))
        else:
            rows.append(row(f"HW_REAR_{m}", f"{I['rear_screw']} x 10 socket-head screw, wrist mount ({m})", n[m] * I["rear_n"], 0.12, "Amazon / McMaster"))
    rows.append(row("HW_PIN_4X10", "Dowel pin Ø4 x 10 mm, steel", sum(n[m] for m in MODELS) * 3, 0.3, "Amazon / McMaster", "", "Three per joint."))
    rows.append(row("HW_TUBE_BOLT", "M4 x 45 socket-head screw + nyloc, tube cross bolts", 8, 0.2, "Amazon / McMaster", "", "Two per tube end, drilled through the tube after bonding."))
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
printed = lambda mat: sum(CATALOG[p]["mass_g"] * CATALOG[p]["qty"] for p in CATALOG if CATALOG[p]["category"] == "printed" and CATALOG[p]["material"] == mat and not CATALOG[p].get("optional"))
kg = lambda g: math.ceil(g * 1.35 / 1000 * 2) / 2
section("filament", "Printed parts (filament)", "core",
        f"About {printed('petg_cf')/1000:.1f} kg of structural prints, {printed('pla')/1000:.1f} kg of PLA and {printed('tpu')/1000:.1f} kg of TPU; quantities add 35 % for supports and failed prints.", [
            row("MAT_PETG_CF", "PETG-CF filament, 1 kg spool", kg(printed("petg_cf")), 30.0, "Bambu / Polymaker / Overture", "", "Every structural part. PA-CF for the hip and knee cups.", unit_label="kg"),
            row("MAT_PLA", "PLA filament, 1 kg spool", kg(printed("pla")), 20.0, "Any", "", "Head, cradles.", unit_label="kg"),
            row("MAT_TPU", "TPU 95A filament, 1 kg spool", kg(printed("tpu")), 28.0, "Any", "", "Soles.", unit_label="kg"),
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
    row("TL_STAND", "Gantry or hoist rated 60 kg, 1.7 m clear height", 1, 180.0),
])
tiers = {}
for sec in BOM_SECTIONS:
    sec["subtotal"] = round(sum(r["total"] for r in sec["rows"]), 2)
    tiers[sec["tier"]] = round(tiers.get(sec["tier"], 0) + sec["subtotal"], 2)

# --------------------------------------------------------------------------- poses, specs, outputs
POSES = {"zero": {"name": "Zero (standing, forearms forward)", "q": {}}, "crouch": {"name": "Crouch", "q": {}}, "reach": {"name": "Reach forward", "q": {}},
         "wave": {"name": "Wave", "q": {}}, "default": {"name": "Default standing (policy)", "q": {}}, "abduct": {"name": "Abduct 45", "q": {}}, "hang": {"name": "Arms hanging (elbow -60)", "q": {}}}
for S in ("L", "R"):
    POSES["crouch"]["q"].update({f"hip_pitch_{S}": -35, f"knee_{S}": 70, f"ankle_pitch_{S}": -35, f"shoulder_pitch_{S}": -20})
    POSES["reach"]["q"].update({f"shoulder_pitch_{S}": -80, f"elbow_{S}": -40, f"hip_pitch_{S}": -8, f"knee_{S}": 16, f"ankle_pitch_{S}": -8})
    POSES["default"]["q"].update({f"hip_pitch_{S}": -8, f"knee_{S}": 16, f"ankle_pitch_{S}": -8, f"shoulder_pitch_{S}": -10})
    POSES["abduct"]["q"].update({f"hip_roll_{S}": 45, f"shoulder_pitch_{S}": -10})
    POSES["hang"]["q"].update({f"elbow_{S}": -60})
POSES["wave"]["q"].update({"shoulder_pitch_R": -30, "shoulder_roll_R": 120, "elbow_R": 30, "wrist_roll_R": 40, "shoulder_pitch_L": -10})

lo = [1e9] * 3; hi = [-1e9] * 3
for lnk in LINKS:
    for o in lnk["parts"]:
        for sh in o["shapes"]:
            gc = [sh["c"][k] + lnk["origin"][k] for k in range(3)]
            a, b = bd.shape_bbox(dict(sh, c=gc))
            lo = [min(lo[k], a[k]) for k in range(3)]; hi = [max(hi[k], b[k]) for k in range(3)]
jz = {j["id"]: j["origin"] for j in JOINTS}
k1_dev = {   # ours minus the K1's, mm
    "hip pitch height": round(HIP_Z - K1["hip_pitch_z"], 1), "hip roll height": round(HIP_Z - K1["hip_roll_z"], 1), "hip yaw output height": round(jz["hip_yaw_L"][2] - K1["hip_yaw_z"], 1),
    "knee height": round(KNEE_Z - K1["knee_z"], 1), "ankle height": round(ANKLE_Z - K1["ankle_z"], 1), "hip line (per side)": round(HIP_Y - K1["hip_y"], 1),
    "waist height": round(jz["waist_yaw"][2] - K1["waist_z"], 1), "shoulder height": round(SH_Z - K1["shoulder_z"], 1), "shoulder pitch actuator (per side)": round(abs(jz["shoulder_pitch_L"][1]) - K1["shoulder_pitch_y"], 1),
    "arm line (per side)": round(ARM_Y - K1["arm_y"], 1), "shoulder yaw output height": round(jz["shoulder_yaw_L"][2] - K1["shoulder_yaw_z"], 1), "elbow height": round(ELBOW_Z - K1["elbow_z"], 1),
    "wrist (forward of the elbow)": round(jz["wrist_roll_L"][0] - K1["wrist_x"], 1), "head top": round(hi[2] - K1["head_top"], 1),
}
SPECS = dict(
    dof=len(JOINTS), hand_dof=16, height_mm=round(hi[2]), width_mm=round(hi[1] - lo[1]), depth_mm=round(hi[0] - lo[0]),
    hip_spacing_mm=2 * HIP_Y, shoulder_spacing_mm=2 * ARM_Y, leg_hip_to_ground_mm=HIP_Z, thigh_mm=round(jz["hip_yaw_L"][2] - KNEE_Z, 1), shank_mm=KNEE_Z - ANKLE_Z,
    ankle_height_mm=ANKLE_Z, upper_arm_mm=round(jz["shoulder_yaw_L"][2] - ELBOW_Z, 1), forearm_mm=round(jz["wrist_roll_L"][0], 1), foot_length_mm=215, hand_spacing_mm=2 * ARM_Y,
    tube_lengths_mm=tube_lengths, screws=SCREWS, mass_g=mass, mass_total_g=mass_total, optional_mass_g=optional_mass,
    bus_voltage="44.4 V nominal (2 x 6S), 50.4 V full", can_buses=4, can_bitrate="1 Mbit/s", k1=K1, k1_deviation=k1_dev,
)
robot = dict(
    meta=dict(name="Fully Open Humanoid", short="FOH", version=VERSION, variant="k1-skeleton", units="mm",
              frame="X forward, Y left, Z up; ground at z = 0", generated_by="tools/build_v2.py",
              basis="ROBOTIS AI Sapiens K1 skeleton (joint positions, 23 joints, 1.36 m) built with RobStride joint kits, carbon tubes and printed blocks"),
    materials=MATERIALS, actuators={m: ACT[m] for m in MODELS}, catalog=CATALOG, links=LINKS, joints=JOINTS,
    poses=POSES, specs=SPECS,
    groups={"torso": "Pelvis, torso and head", "leg_L": "Left leg", "leg_R": "Right leg", "arm_L": "Left arm", "arm_R": "Right arm"},
)
bom = dict(meta=dict(version=VERSION, variant="k1-skeleton", priced_as_of=PRICED_AS_OF, currency="USD"), sections=BOM_SECTIONS, tiers=tiers)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "robot_v2.json").write_text(json.dumps(robot, separators=(",", ":")) + "\n")
(OUT / "bom_v2.json").write_text(json.dumps(bom, indent=1) + "\n")
bd.write_urdf(ROOT / "assets" / "model" / "foh_v2_0.urdf")

if __name__ == "__main__":
    n_parts = sum(len(l["parts"]) for l in LINKS)
    print(f"FOH v{VERSION} (K1 skeleton): {len(LINKS)} links, {len(JOINTS)} joints, {n_parts} part occurrences, {len(CATALOG)} catalogue entries")
    print(f"Envelope: {SPECS['depth_mm']} x {SPECS['width_mm']} x {SPECS['height_mm']} mm; tubes {tube_lengths}")
    for k, v in mass.items():
        print(f"  mass {k:22s} {v/1000:6.2f} kg")
    print(f"  mass total (core)        {mass_total/1000:6.2f} kg   (+{optional_mass/1000:.2f} kg optional)")
    for sec in BOM_SECTIONS:
        print(f"  ${sec['subtotal']:9,.2f}  {sec['title']}")
    for t, v in tiers.items():
        print(f"  {t:8s} ${v:,.2f}")
    print("K1 deviations (mm):", k1_dev)
