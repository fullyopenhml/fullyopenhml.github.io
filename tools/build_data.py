#!/usr/bin/env python3
"""Single source of truth for the Fully Open Humanoid (FOH) v0.1 design.

Defines the kinematic tree, every part occurrence (as simple solids the web
viewer can render), the actuator catalogue and the purchased-parts list, then
writes:

    assets/data/robot.json   -- read by the 3D viewer, the printed-parts page
                                and the reference page
    assets/data/bom.json     -- read by the bill of materials and the home page

Run:  python3 tools/build_data.py            (prints a mass and cost summary)

Frame convention: X forward, Y left, Z up, millimetres, ground at z = 0.
All part positions are authored in this global frame at the zero pose; the
script converts them to link-local coordinates.  Left limbs are authored and
the right limbs are mirrored (y -> -y; X and Z joint axes flipped so that a
positive angle means the same thing on both sides).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "data"

VERSION = "0.1"
PRICED_AS_OF = "2026-09"

# ---------------------------------------------------------------------------
# Materials (colour is what the viewer shows; density x fill gives the mass
# estimate of a printed or extruded part from its solid volume)
# ---------------------------------------------------------------------------
MATERIALS = {
    "petg_cf": {"name": "PETG-CF, printed", "color": "#d6d9de", "density": 1.27, "fill": 0.45},
    "pla": {"name": "PLA, printed", "color": "#eceef1", "density": 1.24, "fill": 0.35},
    "tpu": {"name": "TPU 95A, printed", "color": "#33363b", "density": 1.21, "fill": 0.70},
    "al_ext": {"name": "Aluminium 6063 extrusion", "color": "#a8aeb6", "density": 2.70, "fill": 0.39},
    "steel": {"name": "Bearing steel", "color": "#b6babf", "density": 7.80, "fill": 0.55},
    "actuator": {"name": "RobStride housing", "color": "#3a3e45"},
    "flange": {"name": "Actuator output flange", "color": "#c5c9ce"},
    "enclosure": {"name": "Electronics enclosure", "color": "#24262a"},
    "pcb": {"name": "Bare board", "color": "#2f6b48"},
    "battery": {"name": "LiPo pack", "color": "#35507f"},
    "estop": {"name": "E-stop", "color": "#d1302e"},
    "camera": {"name": "Camera", "color": "#e9e9e9"},
    "servo": {"name": "Bus servo", "color": "#1f2a3a"},
}

# ---------------------------------------------------------------------------
# Actuator catalogue.  Peak torque, Kt, current limit, mass and envelope are
# the values published with the Duke Humanoid V2 hardware release (its Fusion
# model and full-specifications page), which in turn come from the RobStride
# manuals.  Prices are the Duke V2 team BOM's Amazon US / AiFitLab prices,
# 2026-09; verify before ordering.
# ---------------------------------------------------------------------------
ACTUATORS = {
    "RS03": dict(name="RobStride RS03", peak_nm=60, kt=2.36, i_limit=43, mass_g=909,
                 dia=99.6, length=56.6, flange_r=32, r=49.8, l=56,
                 bearing="6809-2RS (45 x 58 x 7)", price=225.0,
                 url="https://www.amazon.com/RobStride-60N-m-Integrated-Actuator-Module/dp/B0GY8PJ1MF"),
    "RS06": dict(name="RobStride RS06", peak_nm=36, kt=1.10, i_limit=57, mass_g=620,
                 dia=84.5, length=46, flange_r=28, r=42.25, l=46,
                 bearing="6807-2RS (35 x 47 x 7)", price=210.0,
                 url="https://www.robstride.com/"),
    "RS02": dict(name="RobStride RS02", peak_nm=17, kt=1.22, i_limit=23, mass_g=420,
                 dia=95.1, length=46, flange_r=28, r=47.5, l=46,
                 bearing="6707-2RS (35 x 44 x 5)", price=145.0,
                 url="https://www.amazon.com/RobStride-Integrated-Actuator-Module-Encoders/dp/B0GS5945VP"),
    "RS05": dict(name="RobStride RS05", peak_nm=5.5, kt=0.94, i_limit=11, mass_g=194,
                 dia=65.1, length=47.1, flange_r=20, r=32.5, l=47,
                 bearing="6704-2RS (20 x 27 x 4)", price=110.0,
                 url="https://www.robstride.com/"),
}

# ---------------------------------------------------------------------------
# Part catalogue: everything that is not an actuator.  qty is filled in from
# the number of occurrences placed on the robot.
# ---------------------------------------------------------------------------
CATALOG: dict[str, dict] = {}


def part(pid, name, category, material, **kw):
    d = dict(id=pid, name=name, category=category, material=material, qty=0)
    d.update(kw)
    CATALOG[pid] = d
    return pid


# Printed structural parts (PETG-CF unless noted).  "mirror" = print the mirrored
# STL for the other side.
P = "printed"
part("3DP_pel01_pelvis_shell", "Pelvis shell", P, "petg_cf", process="FDM",
     notes="Carries the two hip-pitch actuators and the waist actuator. Printed in two halves joined with M4 bolts and heat-set inserts.")
part("3DP_leg01_hip_pitch_adapter", "Hip-pitch output adapter", P, "petg_cf", process="FDM", mirror=True,
     notes="Bolts to the RS03 output flange; carries the hip-roll bracket.")
part("3DP_leg02_hip_roll_bracket", "Hip-roll bracket", P, "petg_cf", process="FDM", mirror=True,
     notes="L-bracket: plate on the hip-pitch adapter, cup around the rear of the hip-roll RS03.")
part("3DP_leg03_hip_roll_adapter", "Hip-roll output adapter", P, "petg_cf", process="FDM", mirror=True)
part("3DP_leg04_hip_yaw_housing", "Hip-yaw housing", P, "petg_cf", process="FDM", mirror=True,
     notes="Hangs from the hip-roll output; collar holds the hip-yaw RS03 with its axis vertical.")
part("3DP_leg05_thigh_block", "Thigh block", P, "petg_cf", process="FDM", mirror=True,
     notes="Short thigh: bolts the knee actuator body to the hip-yaw output, as on Duke V2.")
part("3DP_leg06_shank_outer_plate", "Shank plate, outer (driven)", P, "petg_cf", process="FDM", mirror=True,
     notes="Driven by the knee output flange. 10 mm plate; print flat, 6 walls.")
part("3DP_leg07_shank_inner_plate", "Shank plate, inner (support)", P, "petg_cf", process="FDM", mirror=True,
     notes="Rides on a 6809 bearing on the back of the knee actuator.")
part("3DP_leg08_shank_cross", "Shank cross member", P, "petg_cf", process="FDM", mirror=False,
     notes="Ties the two shank plates together above the ankle-pitch actuator.")
part("3DP_leg09_ankle_adapter", "Ankle-pitch output adapter", P, "petg_cf", process="FDM", mirror=True)
part("3DP_leg10_ankle_bracket", "Ankle bracket", P, "petg_cf", process="FDM", mirror=True,
     notes="Carries the ankle-roll RS06 behind the ankle-pitch actuator.")
part("3DP_leg11_foot_bracket", "Foot bracket", P, "petg_cf", process="FDM", mirror=True,
     notes="Driven by the ankle-roll output; bolts to the foot plate.")
part("3DP_leg12_foot_plate", "Foot plate", P, "petg_cf", process="FDM", mirror=True)
part("3DP_leg13_sole", "Foot sole", P, "tpu", process="FDM", mirror=True, notes="TPU 95A, 100 % infill.")
part("3DP_tor01_waist_adapter", "Waist output adapter", P, "petg_cf", process="FDM")
part("3DP_tor02_bottom_plate", "Torso bottom plate", P, "petg_cf", process="FDM",
     notes="Bolts to the waist adapter and to the four 2020 uprights (M5 into tapped ends).")
part("3DP_tor03_top_plate", "Torso top plate", P, "petg_cf", process="FDM")
part("3DP_tor04_shoulder_mount", "Shoulder-pitch mount", P, "petg_cf", process="FDM", mirror=True,
     notes="Cup for the shoulder-pitch RS06, hangs from the top plate.")
part("3DP_tor05_side_panel", "Torso side panel", P, "pla", process="FDM", mirror=True,
     notes="Cosmetic; 4 mm, with a clearance hole for the shoulder-pitch flange.")
part("3DP_tor06_back_panel", "Torso back panel", P, "pla", process="FDM",
     notes="Carries the E-stop and the main breaker.")
part("3DP_tor07_front_panel", "Torso front panel", P, "pla", process="FDM", notes="Removable; magnets.")
part("3DP_tor08_electronics_tray", "Electronics tray", P, "pla", process="FDM",
     notes="Mounts the computer, CAN adapters, hub and power parts inside the frame.")
part("3DP_tor09_battery_cradle", "Battery cradle", P, "pla", process="FDM", mirror=False,
     notes="One per pack; straps the pack to the rear of the frame.")
part("3DP_hea01_neck_post", "Neck post", P, "petg_cf", process="FDM")
part("3DP_hea02_head_shell", "Head shell", P, "pla", process="FDM",
     notes="Blank head with a RealSense mounting pocket. Camera is optional.")
part("3DP_arm01_shoulder_adapter", "Shoulder-pitch output adapter", P, "petg_cf", process="FDM", mirror=True)
part("3DP_arm02_shoulder_bracket", "Shoulder-roll bracket", P, "petg_cf", process="FDM", mirror=True,
     notes="Plate on the shoulder-pitch adapter, cup around the rear of the shoulder-roll RS06.")
part("3DP_arm03_roll_adapter", "Shoulder-roll output adapter", P, "petg_cf", process="FDM", mirror=True)
part("3DP_arm04_upper_arm_yoke", "Upper-arm yoke", P, "petg_cf", process="FDM", mirror=True,
     notes="Hangs from the shoulder-roll output; collar holds the shoulder-yaw RS02.")
part("3DP_arm05_yaw_adapter", "Shoulder-yaw output adapter", P, "petg_cf", process="FDM", mirror=True)
part("3DP_arm06_upper_arm", "Upper-arm link", P, "petg_cf", process="FDM", mirror=True,
     notes="Bridges the shoulder-yaw output to the elbow cup.")
part("3DP_arm07_elbow_adapter", "Elbow output adapter", P, "petg_cf", process="FDM", mirror=True)
part("3DP_arm08_forearm_outer", "Forearm plate, outer (driven)", P, "petg_cf", process="FDM", mirror=True)
part("3DP_arm09_forearm_inner", "Forearm plate, inner (support)", P, "petg_cf", process="FDM", mirror=True,
     notes="Rides on a 6707 bearing on the back of the elbow actuator.")
part("3DP_arm10_forearm_body", "Forearm body", P, "petg_cf", process="FDM", mirror=True,
     notes="Joins both forearm plates and holds the wrist-roll RS05.")
part("3DP_arm11_wrist_adapter", "Wrist-roll output adapter", P, "petg_cf", process="FDM", mirror=True)
part("3DP_grp01_gripper_body", "Gripper body", P, "pla", process="FDM", mirror=True, optional="grippers",
     notes="Rack-and-pinion parallel gripper after Duke V2; one STS3215 bus servo. Optional kit.")
part("3DP_grp02_finger", "Gripper finger", P, "pla", process="FDM", optional="grippers")
part("3DP_grp03_finger_pad", "Finger pad", P, "tpu", process="FDM", optional="grippers")

# Bearings and metal
H = "hardware"
part("HW_6809_2RS", "Ball bearing 6809-2RS, 45 x 58 x 7 mm", H, "steel", price=3.0,
     vendor="Amazon", notes="Support bearing on the back of every RS03 joint.")
part("HW_6807_2RS", "Ball bearing 6807-2RS, 35 x 47 x 7 mm", H, "steel", price=4.0, vendor="Amazon",
     notes="Support bearing on every RS06 joint.")
part("HW_6707_2RS", "Ball bearing 6707-2RS, 35 x 44 x 5 mm", H, "steel", price=3.0, vendor="Amazon",
     notes="Support bearing on every RS02 joint.")
part("HW_2020_400", "Aluminium 2020 extrusion, 400 mm, ends tapped M5", H, "al_ext", price=4.5,
     vendor="Amazon / Misumi", notes="Torso uprights. Cut to length or order pre-cut.")

# Electronics that appear on the model
E = "electronics"
part("EL_PC_N100", "Mini PC, Intel N100, 16 GB RAM, 500 GB SSD", E, "enclosure", mass_g=450, price=160.0,
     vendor="Amazon", notes="Runs the 50 Hz policy and the 500 Hz motor loop. No GPU needed on the robot.")
part("EL_BATTERY_6S", "LiPo 6S 8000 mAh 100C, EC5", E, "battery", mass_g=1000, price=90.0, vendor="Amazon",
     notes="Two in series: 44.4 V nominal, 50.4 V full. Zeee or equivalent.")
part("EL_CANABLE", "CANable PRO V2.0 USB-CAN adapter", E, "pcb", mass_g=15, price=20.8, vendor="Amazon",
     notes="One per bus, four buses.")
part("EL_USB_HUB", "USB 3 hub, 4 port, powered", E, "enclosure", mass_g=40, price=13.0, vendor="Amazon")
part("EL_BUCK_12V", "48 V to 12 V buck converter, 10 A, encased", E, "enclosure", mass_g=120, price=19.0,
     vendor="Amazon", notes="Feeds the computer, the hub and the gripper servos.")
part("EL_DIST_BLOCK", "Power distribution block with 60 A fuse", E, "enclosure", mass_g=80, price=18.0,
     vendor="Amazon", notes="48 V bus and ground bars; ANL/MIDI fuse on the pack lead.")
part("EL_IMU", "USB 9-axis AHRS IMU (SYD Dynamics TM171 or equivalent)", E, "pcb", mass_g=25, price=57.0,
     vendor="RobotShop", notes="Mounted rigidly to the torso bottom plate, axes aligned with the base frame.")
part("EL_ESTOP", "E-stop, 22 mm mushroom, NC contact", E, "estop", mass_g=60, price=12.0, vendor="Amazon",
     notes="Opens the 48 V bus contactor coil. Duke V2 shipped without one; do not.")
part("EL_BREAKER", "DC circuit breaker, 100 A, panel mount", E, "enclosure", mass_g=90, price=20.0,
     vendor="Amazon", notes="Main disconnect and pack over-current protection.")
part("EL_CONTACTOR", "DC contactor, 100 A, 12 V coil", E, "enclosure", mass_g=180, price=25.0,
     vendor="Amazon", notes="Switched by the E-stop loop; carries the motor bus.")
part("EL_CAMERA_D435I", "Intel RealSense D435i", E, "camera", mass_g=72, price=300.0, vendor="Intel",
     optional="perception", notes="Optional perception kit. Any USB camera fits the head pocket with an adapter.")
part("EL_SERVO_STS3215", "Feetech STS3215 bus servo, 12 V", E, "servo", mass_g=60, price=16.0,
     vendor="Feetech / Amazon", optional="grippers", notes="One per gripper; both on one Waveshare bus driver.")

# ---------------------------------------------------------------------------
# Geometry helpers: every shape is a dict the viewer knows how to build.
# ---------------------------------------------------------------------------


def cyl(axis, r, l, c, r_in=None):
    d = {"t": "cyl", "axis": axis, "r": r, "l": l, "c": list(c)}
    if r_in:
        d["ri"] = r_in
    return d


def box(size, c, round=0):
    d = {"t": "box", "s": list(size), "c": list(c)}
    if round:
        d["rd"] = round
    return d


def vol(shape):
    if shape["t"] == "box":
        return math.prod(shape["s"])
    r_out = shape["r"]
    r_in = shape.get("ri", 0)
    return math.pi * (r_out ** 2 - r_in ** 2) * shape["l"]


def actuator_shapes(model, axis, c, out_sign):
    """RobStride actuator: dark body, silver front ring, output flange."""
    a = ACTUATORS[model]
    r, l, fr = a["r"], a["l"], a["flange_r"]
    i = "xyz".index(axis)
    face = list(c)
    face[i] += out_sign * l / 2
    ring_c = list(c)
    ring_c[i] += out_sign * (l / 2 - 3)
    flange_c = list(face)
    flange_c[i] += out_sign * 2
    back_c = list(c)
    back_c[i] -= out_sign * (l / 2 + 1.5)
    return [
        dict(cyl(axis, r, l, c), m="actuator"),
        dict(cyl(axis, r + 1.5, 6, ring_c), m="flange"),
        dict(cyl(axis, fr, 4, flange_c), m="flange"),
        dict(cyl(axis, r - 6, 3, back_c), m="enclosure"),
    ]


# ---------------------------------------------------------------------------
# Robot definition
# ---------------------------------------------------------------------------
LINKS: list[dict] = []
JOINTS: list[dict] = []
LINK_BY_ID: dict[str, dict] = {}


def link(lid, name, group, origin, parent_joint=None):
    d = dict(id=lid, name=name, group=group, origin=list(origin), parent_joint=parent_joint, parts=[])
    LINKS.append(d)
    LINK_BY_ID[lid] = d
    return d


def joint(jid, name, parent, child, origin, axis, limits, actuator, side, can_bus, can_id, kind):
    d = dict(id=jid, name=name, parent=parent, child=child, origin=list(origin), axis=list(axis),
             limits=list(limits), actuator=actuator, side=side, bus=can_bus, can_id=can_id, kind=kind)
    JOINTS.append(d)
    return d


def place(lnk, occ, pid, shapes, kind=None, actuator=None, optional=None):
    """Place a part occurrence on a link.  shapes are authored in global coords."""
    o = dict(occ=occ, part=pid, shapes=shapes)
    if actuator:
        o["actuator"] = actuator
    if optional:
        o["optional"] = optional
    lnk["parts"].append(o)
    if pid in CATALOG:
        CATALOG[pid]["qty"] += 1
    return o


def actuator(lnk, occ, model, axis, c, out_sign, optional=None):
    pid = "ACT_" + model
    if pid not in CATALOG:
        a = ACTUATORS[model]
        part(pid, a["name"] + " quasi-direct-drive actuator", "actuator", "actuator", mass_g=a["mass_g"],
             price=a["price"], vendor="RobStride (Amazon US / AiFitLab)", model=model,
             notes=f"{a['peak_nm']} N·m peak, Ø{a['dia']} × {a['length']} mm, {a['mass_g']} g. Support bearing {a['bearing']}.")
    return place(lnk, occ, pid, actuator_shapes(model, axis, c, out_sign), actuator=model, optional=optional)


# Key dimensions (mm) --------------------------------------------------------
HIP_Y = 135      # hip-roll / hip-yaw centreline
HIP_Z = 460      # hip-pitch and hip-roll axes
KNEE_Z = 277
ANKLE_Z = 100    # ankle-pitch axis
ROLL_Z = 68      # ankle-roll axis
SHANK_Y = 140    # shank centreline (knee output is outboard)
SH_Y_OUT = 101   # torso side face where the shoulder-pitch flange emerges
SH_Z = 940       # shoulder-pitch and shoulder-roll axes
ARM_Y = 165      # shoulder-roll / yaw / elbow centreline
ELBOW_Z = 730
FORE_Y = 170
WRIST_Z = 528.5  # wrist-roll output face

# --- Pelvis (root) -----------------------------------------------------------
pelvis = link("pelvis", "Pelvis", "pelvis", (0, 0, 0))
place(pelvis, "pelvis_shell", "3DP_pel01_pelvis_shell", [
    box((124, 160, 10), (0, 0, 515), 3), box((124, 160, 10), (0, 0, 409), 3),
    box((10, 160, 96), (57, 0, 462), 3), box((10, 160, 96), (-57, 0, 462), 3),
])
actuator(pelvis, "hip_pitch_L_act", "RS03", "y", (0, 40, HIP_Z), +1)
actuator(pelvis, "hip_pitch_R_act", "RS03", "y", (0, -40, HIP_Z), -1)
actuator(pelvis, "waist_act", "RS03", "z", (0, 0, 548), +1)

# --- Torso ---------------------------------------------------------------------
TORSO_O = (0, 0, 580)
torso = link("torso", "Torso", "torso", TORSO_O, "waist")
joint("waist", "Waist yaw", "pelvis", "torso", TORSO_O, (0, 0, 1), (-90, 90), "RS03", "centre", "can2", 1, "yaw")
place(torso, "waist_adapter", "3DP_tor01_waist_adapter", [cyl("z", 34, 6, (0, 0, 583))])
place(torso, "bottom_plate", "3DP_tor02_bottom_plate", [box((150, 210, 10), (0, 0, 591), 4)])
place(torso, "top_plate", "3DP_tor03_top_plate", [box((150, 210, 10), (0, 0, 1001), 4)])
for sx in (1, -1):
    for sy in (1, -1):
        tag = ("F" if sx > 0 else "B") + ("L" if sy > 0 else "R")
        place(torso, f"upright_{tag}", "HW_2020_400", [box((20, 20, 400), (55 * sx, 85 * sy, 796))])
for sy, tag in ((1, "L"), (-1, "R")):
    place(torso, f"side_panel_{tag}", "3DP_tor05_side_panel", [box((130, 4, 400), (0, 99 * sy, 796))])
    place(torso, f"shoulder_mount_{tag}", "3DP_tor04_shoulder_mount", [
        cyl("y", 47, 20, (0, 60 * sy, SH_Z), r_in=43), box((30, 10, 70), (0, 47 * sy, 960)),
    ])
    actuator(torso, f"shoulder_pitch_{tag}_act", "RS06", "y", (0, 72 * sy, SH_Z), sy)
place(torso, "back_panel", "3DP_tor06_back_panel", [box((4, 170, 400), (-69, 0, 796))])
place(torso, "front_panel", "3DP_tor07_front_panel", [box((4, 170, 400), (69, 0, 796))])
place(torso, "electronics_tray", "3DP_tor08_electronics_tray", [box((4, 140, 380), (2, 0, 796))])
place(torso, "battery_cradle_L", "3DP_tor09_battery_cradle", [box((56, 70, 6), (-32, 35, 607), 2)])
place(torso, "battery_cradle_R", "3DP_tor09_battery_cradle", [box((56, 70, 6), (-32, -35, 607), 2)])
place(torso, "battery_1", "EL_BATTERY_6S", [box((52, 64, 166), (-32, 35, 693), 3)])
place(torso, "battery_2", "EL_BATTERY_6S", [box((52, 64, 166), (-32, -35, 693), 3)])
place(torso, "computer", "EL_PC_N100", [box((45, 128, 128), (28, 0, 660), 4)])
for i, (sy, z) in enumerate(((1, 736), (-1, 736), (1, 754), (-1, 754))):
    place(torso, f"can_adapter_{i}", "EL_CANABLE", [box((60, 25, 12), (20, 45 * sy, z))])
place(torso, "usb_hub", "EL_USB_HUB", [box((95, 30, 14), (20, 0, 737), 2)])
place(torso, "buck_12v", "EL_BUCK_12V", [box((60, 45, 25), (-30, 0, 794), 2)])
place(torso, "dist_block", "EL_DIST_BLOCK", [box((50, 60, 20), (20, 0, 790), 2)])
place(torso, "contactor", "EL_CONTACTOR", [box((44, 60, 40), (-30, 0, 840), 3)])
place(torso, "imu", "EL_IMU", [box((36, 36, 14), (-25, 0, 603), 2)])
place(torso, "estop", "EL_ESTOP", [box((10, 44, 44), (-76, 0, 950)), cyl("x", 20, 22, (-92, 0, 950))])
place(torso, "breaker", "EL_BREAKER", [box((18, 36, 60), (-80, -55, 880), 2)])
place(torso, "neck_post", "3DP_hea01_neck_post", [cyl("z", 22, 34, (10, 0, 1023))])
place(torso, "head_shell", "3DP_hea02_head_shell", [box((90, 110, 70), (15, 0, 1075), 8)])
place(torso, "camera", "EL_CAMERA_D435I", [box((26, 90, 26), (55, 0, 1085), 3)], optional="perception")


# --- Legs ---------------------------------------------------------------------
def build_leg(side):
    s = 1 if side == "L" else -1
    S = side
    ids = {"L": (11, "can0"), "R": (21, "can1")}[S]
    base_id, bus = ids
    lim_roll = (-30, 105) if S == "L" else (-30, 105)  # positive = abduction on both sides after mirroring

    # hip pitch joint: output face of the pelvis actuator
    o1 = (0, 72 * s, HIP_Z)
    l1 = link(f"hip_roll_bracket_{S}", f"Hip-roll bracket ({S})", f"leg_{S}", o1, f"hip_pitch_{S}")
    joint(f"hip_pitch_{S}", f"Hip pitch ({S})", "pelvis", l1["id"], o1, (0, 1, 0), (-105, 105), "RS03", S, bus, base_id, "pitch")
    place(l1, f"hip_pitch_adapter_{S}", "3DP_leg01_hip_pitch_adapter", [cyl("y", 34, 6, (0, 75 * s, HIP_Z))])
    place(l1, f"hip_roll_bracket_{S}", "3DP_leg02_hip_roll_bracket", [
        box((100, 10, 104), (-10, 83 * s, HIP_Z), 3),
        cyl("x", 54, 8, (-32, HIP_Y * s, HIP_Z)),
        cyl("x", 54, 26, (-15, HIP_Y * s, HIP_Z), r_in=50),
    ])
    actuator(l1, f"hip_roll_{S}_act", "RS03", "x", (0, HIP_Y * s, HIP_Z), +1)
    place(l1, f"hip_roll_bearing_{S}", "HW_6809_2RS", [cyl("x", 29, 7, (-33, HIP_Y * s, HIP_Z), r_in=22.5)])

    # hip roll joint
    o2 = (32, HIP_Y * s, HIP_Z)
    l2 = link(f"hip_yaw_housing_{S}", f"Hip-yaw housing ({S})", f"leg_{S}", o2, f"hip_roll_{S}")
    joint(f"hip_roll_{S}", f"Hip roll ({S})", l1["id"], l2["id"], o2, (1, 0, 0), lim_roll, "RS03", S, bus, base_id + 1, "roll")
    place(l2, f"hip_roll_adapter_{S}", "3DP_leg03_hip_roll_adapter", [cyl("x", 34, 6, (35, HIP_Y * s, HIP_Z)), cyl("x", 34, 12, (44, HIP_Y * s, HIP_Z))])
    place(l2, f"hip_yaw_housing_{S}", "3DP_leg04_hip_yaw_housing", [
        box((12, 100, 140), (56, HIP_Y * s, 430), 3),
        cyl("z", 54, 28, (0, HIP_Y * s, 393), r_in=50),
    ])
    actuator(l2, f"hip_yaw_{S}_act", "RS03", "z", (0, HIP_Y * s, 379), -1)

    # hip yaw joint
    o3 = (0, HIP_Y * s, 347)
    l3 = link(f"thigh_{S}", f"Thigh ({S})", f"leg_{S}", o3, f"hip_yaw_{S}")
    joint(f"hip_yaw_{S}", f"Hip yaw ({S})", l2["id"], l3["id"], o3, (0, 0, 1), (-90, 90), "RS03", S, bus, base_id + 2, "yaw")
    place(l3, f"hip_yaw_adapter_{S}", "3DP_leg05_thigh_block", [
        cyl("z", 34, 6, (0, HIP_Y * s, 344)),
        box((110, 90, 14), (0, HIP_Y * s, 334), 3),
        cyl("y", 54, 24, (0, 119 * s, KNEE_Z), r_in=50),
    ])
    actuator(l3, f"knee_{S}_act", "RS03", "y", (0, HIP_Y * s, KNEE_Z), s)

    # knee joint (output outboard)
    o4 = (0, 167 * s, KNEE_Z)
    l4 = link(f"shank_{S}", f"Shank ({S})", f"leg_{S}", o4, f"knee_{S}")
    joint(f"knee_{S}", f"Knee ({S})", l3["id"], l4["id"], o4, (0, 1, 0), (0, 135), "RS03", S, bus, base_id + 3, "pitch")
    place(l4, f"knee_adapter_{S}", "3DP_leg06_shank_outer_plate", [
        cyl("y", 34, 6, (0, 170 * s, KNEE_Z)),
        box((72, 10, 220), (0, 178 * s, 190), 4),
    ])
    place(l4, f"shank_inner_{S}", "3DP_leg07_shank_inner_plate", [box((72, 10, 220), (0, 102 * s, 190), 4)])
    place(l4, f"knee_bearing_{S}", "HW_6809_2RS", [cyl("y", 29, 7, (0, 103.5 * s, KNEE_Z), r_in=22.5)])
    place(l4, f"shank_cross_{S}", "3DP_leg08_shank_cross", [box((60, 66, 16), (0, SHANK_Y * s, 200), 3)])
    actuator(l4, f"ankle_pitch_{S}_act", "RS03", "y", (0, SHANK_Y * s, ANKLE_Z), s)

    # ankle pitch joint (outer face of the shank plate)
    o5 = (0, 183 * s, ANKLE_Z)
    l5 = link(f"ankle_block_{S}", f"Ankle block ({S})", f"leg_{S}", o5, f"ankle_pitch_{S}")
    joint(f"ankle_pitch_{S}", f"Ankle pitch ({S})", l4["id"], l5["id"], o5, (0, 1, 0), (-50, 50), "RS03", S, bus, base_id + 4, "pitch")
    place(l5, f"ankle_adapter_{S}", "3DP_leg09_ankle_adapter", [cyl("y", 34, 6, (0, 186 * s, ANKLE_Z))])
    place(l5, f"ankle_bracket_{S}", "3DP_leg10_ankle_bracket", [
        box((150, 10, 110), (-30, 192 * s, 95), 3),
        cyl("x", 50, 8, (-103, SHANK_Y * s, ROLL_Z)),
        cyl("x", 47, 20, (-89, SHANK_Y * s, ROLL_Z), r_in=43),
    ])
    actuator(l5, f"ankle_roll_{S}_act", "RS06", "x", (-76, SHANK_Y * s, ROLL_Z), +1)
    place(l5, f"ankle_roll_bearing_{S}", "HW_6807_2RS", [cyl("x", 23.5, 7, (-101, SHANK_Y * s, ROLL_Z), r_in=17.5)])

    # ankle roll joint
    o6 = (-49, SHANK_Y * s, ROLL_Z)
    l6 = link(f"foot_{S}", f"Foot ({S})", f"leg_{S}", o6, f"ankle_roll_{S}")
    joint(f"ankle_roll_{S}", f"Ankle roll ({S})", l5["id"], l6["id"], o6, (1, 0, 0), (-30, 30), "RS06", S, bus, base_id + 5, "roll")
    place(l6, f"foot_bracket_{S}", "3DP_leg11_foot_bracket", [
        cyl("x", 30, 6, (-46, SHANK_Y * s, ROLL_Z)),
        box((10, 90, 100), (-38, SHANK_Y * s, 58), 3),
    ])
    place(l6, f"foot_plate_{S}", "3DP_leg12_foot_plate", [box((230, 92, 12), (-5, SHANK_Y * s, 14), 4)])
    place(l6, f"sole_{S}", "3DP_leg13_sole", [box((230, 92, 8), (-5, SHANK_Y * s, 4), 3)])


def build_arm(side):
    s = 1 if side == "L" else -1
    S = side
    base_id, bus = {"L": (31, "can2"), "R": (41, "can3")}[S]

    o1 = (0, SH_Y_OUT * s, SH_Z)
    a1 = link(f"shoulder_roll_bracket_{S}", f"Shoulder-roll bracket ({S})", f"arm_{S}", o1, f"shoulder_pitch_{S}")
    joint(f"shoulder_pitch_{S}", f"Shoulder pitch ({S})", "torso", a1["id"], o1, (0, 1, 0), (-180, 180), "RS06", S, bus, base_id, "pitch")
    place(a1, f"shoulder_adapter_{S}", "3DP_arm01_shoulder_adapter", [cyl("y", 30, 6, (0, 104 * s, SH_Z))])
    place(a1, f"shoulder_bracket_{S}", "3DP_arm02_shoulder_bracket", [
        box((96, 12, 100), (-10, 113 * s, SH_Z), 3),
        cyl("x", 48, 8, (-37, ARM_Y * s, SH_Z)),
        cyl("x", 47, 22, (-22, ARM_Y * s, SH_Z), r_in=43),
    ])
    actuator(a1, f"shoulder_roll_{S}_act", "RS06", "x", (-10, ARM_Y * s, SH_Z), +1)
    place(a1, f"shoulder_roll_bearing_{S}", "HW_6807_2RS", [cyl("x", 23.5, 7, (-36, ARM_Y * s, SH_Z), r_in=17.5)])

    o2 = (17, ARM_Y * s, SH_Z)
    a2 = link(f"upper_arm_yoke_{S}", f"Upper-arm yoke ({S})", f"arm_{S}", o2, f"shoulder_roll_{S}")
    joint(f"shoulder_roll_{S}", f"Shoulder roll ({S})", a1["id"], a2["id"], o2, (1, 0, 0), (-20, 150), "RS06", S, bus, base_id + 1, "roll")
    place(a2, f"roll_adapter_{S}", "3DP_arm03_roll_adapter", [cyl("x", 30, 6, (20, ARM_Y * s, SH_Z)), cyl("x", 30, 10, (28, ARM_Y * s, SH_Z))])
    place(a2, f"upper_arm_yoke_{S}", "3DP_arm04_upper_arm_yoke", [
        box((10, 96, 104), (38, ARM_Y * s, 938), 3),
        box((76, 96, 10), (5, ARM_Y * s, 891), 3),
        cyl("z", 52, 20, (0, ARM_Y * s, 876), r_in=48),
    ])
    actuator(a2, f"shoulder_yaw_{S}_act", "RS02", "z", (0, ARM_Y * s, 861), -1)

    o3 = (0, ARM_Y * s, 834)
    a3 = link(f"upper_arm_{S}", f"Upper arm ({S})", f"arm_{S}", o3, f"shoulder_yaw_{S}")
    joint(f"shoulder_yaw_{S}", f"Shoulder yaw ({S})", a2["id"], a3["id"], o3, (0, 0, 1), (-180, 180), "RS02", S, bus, base_id + 2, "yaw")
    place(a3, f"yaw_adapter_{S}", "3DP_arm05_yaw_adapter", [cyl("z", 30, 6, (0, ARM_Y * s, 831))])
    place(a3, f"upper_arm_{S}", "3DP_arm06_upper_arm", [
        box((64, 64, 50), (0, ARM_Y * s, 803), 6),
        cyl("y", 52, 20, (0, 150 * s, ELBOW_Z), r_in=48),
    ])
    actuator(a3, f"elbow_{S}_act", "RS02", "y", (0, ARM_Y * s, ELBOW_Z), s)

    o4 = (0, 192 * s, ELBOW_Z)
    a4 = link(f"forearm_{S}", f"Forearm ({S})", f"arm_{S}", o4, f"elbow_{S}")
    joint(f"elbow_{S}", f"Elbow ({S})", a3["id"], a4["id"], o4, (0, 1, 0), (0, 125), "RS02", S, bus, base_id + 3, "pitch")
    place(a4, f"elbow_adapter_{S}", "3DP_arm07_elbow_adapter", [cyl("y", 30, 6, (0, 195 * s, ELBOW_Z))])
    place(a4, f"forearm_outer_{S}", "3DP_arm08_forearm_outer", [box((64, 10, 110), (0, 203 * s, 680), 4)])
    place(a4, f"forearm_inner_{S}", "3DP_arm09_forearm_inner", [box((64, 10, 110), (0, 137 * s, 680), 4)])
    place(a4, f"elbow_bearing_{S}", "HW_6707_2RS", [cyl("y", 22, 5, (0, 139.5 * s, ELBOW_Z), r_in=17.5)])
    place(a4, f"forearm_body_{S}", "3DP_arm10_forearm_body", [box((56, 76, 60), (0, FORE_Y * s, 610), 6)])
    actuator(a4, f"wrist_roll_{S}_act", "RS05", "z", (0, FORE_Y * s, 556), -1)

    o5 = (0, FORE_Y * s, WRIST_Z)
    a5 = link(f"hand_{S}", f"Hand ({S})", f"arm_{S}", o5, f"wrist_roll_{S}")
    joint(f"wrist_roll_{S}", f"Wrist roll ({S})", a4["id"], a5["id"], o5, (0, 0, 1), (-180, 180), "RS05", S, bus, base_id + 4, "yaw")
    place(a5, f"wrist_adapter_{S}", "3DP_arm11_wrist_adapter", [cyl("z", 22, 5, (0, FORE_Y * s, 526))])
    place(a5, f"gripper_body_{S}", "3DP_grp01_gripper_body", [box((60, 84, 44), (0, FORE_Y * s, 501.5), 6)], optional="grippers")
    place(a5, f"gripper_servo_{S}", "EL_SERVO_STS3215", [box((24, 46, 40), (0, FORE_Y * s, 500), 2)], optional="grippers")
    for fs, tag in ((1, "a"), (-1, "b")):
        place(a5, f"finger_{S}{tag}", "3DP_grp02_finger", [box((16, 12, 86), (0, (FORE_Y + 30 * fs) * s, 436), 3)], optional="grippers")
        place(a5, f"finger_pad_{S}{tag}", "3DP_grp03_finger_pad", [box((14, 4, 40), (0, (FORE_Y + 22 * fs) * s, 420), 1)], optional="grippers")


build_leg("L")
build_leg("R")
build_arm("L")
build_arm("R")

# Mirrored right-side joints: flip X and Z axes so that a positive angle is
# the same motion (abduction / outward yaw) on both sides.
for j in JOINTS:
    if j["side"] == "R":
        ax = j["axis"]
        j["axis"] = [-ax[0], ax[1], -ax[2]]

# ---------------------------------------------------------------------------
# Derived data: link-local coordinates, masses, dims
# ---------------------------------------------------------------------------


def shape_bbox(shape):
    c = shape["c"]
    if shape["t"] == "box":
        h = [v / 2 for v in shape["s"]]
    else:
        i = "xyz".index(shape["axis"])
        h = [shape["r"]] * 3
        h[i] = shape["l"] / 2
    return [c[k] - h[k] for k in range(3)], [c[k] + h[k] for k in range(3)]


for lnk in LINKS:
    ox, oy, oz = lnk["origin"]
    for o in lnk["parts"]:
        cat = CATALOG[o["part"]]
        lo = [1e9] * 3
        hi = [-1e9] * 3
        v = 0.0
        for sh in o["shapes"]:
            a, b = shape_bbox(sh)
            lo = [min(lo[k], a[k]) for k in range(3)]
            hi = [max(hi[k], b[k]) for k in range(3)]
            if cat["category"] in ("printed", "hardware"):
                v += vol(sh)
            sh["c"] = [round(sh["c"][0] - ox, 3), round(sh["c"][1] - oy, 3), round(sh["c"][2] - oz, 3)]
        centre = [(lo[k] + hi[k]) / 2 for k in range(3)]
        o["center"] = [round(centre[0] - ox, 2), round(centre[1] - oy, 2), round(centre[2] - oz, 2)]
        o["center_world"] = [round(c, 1) for c in centre]
        dims = [round(hi[k] - lo[k], 1) for k in range(3)]
        if "dims" not in cat:
            cat["dims"] = dims
        if cat["category"] in ("printed", "hardware") and "mass_g" not in cat:
            m = MATERIALS[cat["material"]]
            cat["mass_g"] = round(v / 1000.0 * m["density"] * m["fill"])

# Mass budget
mass = {"actuators": 0, "printed": 0, "hardware": 0, "electronics": 0}
optional_mass = 0
for lnk in LINKS:
    for o in lnk["parts"]:
        cat = CATALOG[o["part"]]
        mg = cat.get("mass_g", 0)
        if o.get("optional"):
            optional_mass += mg
            continue
        key = "actuators" if cat["category"] == "actuator" else cat["category"]
        mass[key] += mg
MISC_MASS_G = 900  # fasteners, inserts, harness, panels not modelled: estimate
mass["fasteners_and_harness"] = MISC_MASS_G
mass_total = sum(mass.values())

# ---------------------------------------------------------------------------
# Bill of materials.  Modelled parts take their quantity from the model; the
# rest are consumables and kits with hand-entered quantities.
# ---------------------------------------------------------------------------
BOM_SECTIONS = []


def section(sid, title, tier, blurb, rows):
    BOM_SECTIONS.append(dict(id=sid, title=title, tier=tier, blurb=blurb, rows=rows))


def row(pid, desc, qty, unit, vendor="", url="", notes="", part_id=None, unit_label="ea"):
    return dict(id=pid, part_id=part_id or pid, description=desc, qty=qty, unit_cost=unit, total=round(qty * unit, 2),
                vendor=vendor, url=url, notes=notes, unit_label=unit_label)


act_rows = []
for model in ("RS03", "RS06", "RS02", "RS05"):
    pid = "ACT_" + model
    a = ACTUATORS[model]
    joints_using = sorted({j["name"].split(" (")[0] for j in JOINTS if j["actuator"] == model})
    act_rows.append(row(pid, f"{a['name']} ({a['peak_nm']} N·m peak)", CATALOG[pid]["qty"], a["price"],
                        "RobStride / Amazon US / AiFitLab", a["url"],
                        "Joints: " + ", ".join(joints_using) + ". Supply risk: no drop-in substitute; a different model changes the bolt pattern, the bearing and the CAN setup."))
section("actuators", "Actuators", "core",
        "Twenty-three RobStride quasi-direct-drive actuators in four models. Every joint of one model uses the same printed adapter, cup and support bearing, so the printed parts are a small family.",
        act_rows)

section("electronics", "Electronics and power", "core",
        "One computer, one IMU, four CAN buses, two packs in series, and the safety chain Duke V2 lacked: breaker, contactor, E-stop.", [
            row("EL_PC_N100", CATALOG["EL_PC_N100"]["name"], 1, 160.0, "Amazon", "", CATALOG["EL_PC_N100"]["notes"]),
            row("EL_IMU", CATALOG["EL_IMU"]["name"], 1, 57.0, "RobotShop", "https://www.robotshop.com/", CATALOG["EL_IMU"]["notes"]),
            row("EL_CANABLE", CATALOG["EL_CANABLE"]["name"], 4, 20.8, "Amazon", "https://www.amazon.com/", "One per bus: left leg, right leg, left arm + waist, right arm."),
            row("EL_USB_HUB", CATALOG["EL_USB_HUB"]["name"], 1, 13.0, "Amazon"),
            row("EL_BATTERY_6S", CATALOG["EL_BATTERY_6S"]["name"], 2, 90.0, "Amazon", "", CATALOG["EL_BATTERY_6S"]["notes"]),
            row("EL_BUCK_12V", CATALOG["EL_BUCK_12V"]["name"], 1, 19.0, "Amazon", "", CATALOG["EL_BUCK_12V"]["notes"]),
            row("EL_DIST_BLOCK", CATALOG["EL_DIST_BLOCK"]["name"], 1, 18.0, "Amazon", "", CATALOG["EL_DIST_BLOCK"]["notes"]),
            row("EL_BREAKER", CATALOG["EL_BREAKER"]["name"], 1, 20.0, "Amazon", "", CATALOG["EL_BREAKER"]["notes"]),
            row("EL_CONTACTOR", CATALOG["EL_CONTACTOR"]["name"], 1, 25.0, "Amazon", "", CATALOG["EL_CONTACTOR"]["notes"]),
            row("EL_ESTOP", CATALOG["EL_ESTOP"]["name"], 1, 12.0, "Amazon", "", CATALOG["EL_ESTOP"]["notes"]),
            row("EL_TVS", "TVS diode, 53 V working / 85 V clamping (1.5KE62CA)", 6, 1.2, "DigiKey", "", "One across each power block and at the bus ends."),
            row("EL_VOLT_ALARM", "LiPo voltage alarm, 1-8S", 2, 7.0, "Amazon", "", "One on each pack's balance lead."),
            row("EL_FUSE_10A", "Blade fuse holder + 10 A fuse", 1, 4.0, "Amazon", "", "Computer feed, 48 V side."),
        ])

section("harness", "Cables and connectors", "core",
        "RobStride actuators carry power and CAN in one XT30(2+2) shell, in and out, so every limb is a daisy chain of identical drops.", [
            row("CB_XT30_2P2_F", "Amass XT30(2+2)-F cable-side connector", 60, 0.75, "Amazon / AliExpress", "", "Two per actuator drop plus bus heads and terminators; buy spares."),
            row("CB_EC5", "EC5 connector pair", 4, 2.0, "Amazon", "", "Pack leads and series link."),
            row("CB_WIRE_18", "18 AWG silicone wire, red + black, 10 m each", 1, 20.0, "Amazon", "", "Actuator drops."),
            row("CB_WIRE_12", "12 AWG silicone wire, red + black, 3 m each", 1, 14.0, "Amazon", "", "Pack trunk, breaker, contactor, distribution block."),
            row("CB_CAT5", "Ethernet cable, 10 m (twisted pairs for CAN)", 1, 8.0, "Amazon", "", "One pair per CAN run."),
            row("CB_TERM", "120 Ω resistors, 1/4 W", 10, 0.2, "Amazon", "", "One at each end of each bus."),
            row("CB_SHRINK", "Heat-shrink assortment", 1, 8.0, "Amazon"),
            row("CB_LOOM", "Braided loom, 6 mm and 10 mm, 5 m each", 1, 10.0, "Amazon"),
            row("CB_USB", "USB-A to USB-C cables, 0.5 m", 3, 3.0, "Amazon", "", "Hub to CAN adapters and IMU."),
        ])

section("hardware", "Bearings, fasteners and extrusion", "core",
        "Thin-section bearings support the back of every joint so the printed adapters see torque, not bending. Sizes follow Duke V2.", [
            row("HW_6809_2RS", CATALOG["HW_6809_2RS"]["name"], CATALOG["HW_6809_2RS"]["qty"], 3.0, "Amazon", "", CATALOG["HW_6809_2RS"]["notes"]),
            row("HW_6807_2RS", CATALOG["HW_6807_2RS"]["name"], CATALOG["HW_6807_2RS"]["qty"], 4.0, "Amazon", "", CATALOG["HW_6807_2RS"]["notes"]),
            row("HW_6707_2RS", CATALOG["HW_6707_2RS"]["name"], CATALOG["HW_6707_2RS"]["qty"], 3.0, "Amazon", "", CATALOG["HW_6707_2RS"]["notes"]),
            row("HW_2020_400", CATALOG["HW_2020_400"]["name"], CATALOG["HW_2020_400"]["qty"], 4.5, "Amazon / Misumi", "", CATALOG["HW_2020_400"]["notes"]),
            row("HW_TNUT_M4", "2020 T-nuts, M4, 50 pack", 1, 8.0, "Amazon"),
            row("HW_CORNER", "2020 inner corner brackets", 8, 0.7, "Amazon"),
            row("HW_SCREWS", "M3 / M4 / M5 socket-head screw assortment, stainless", 1, 35.0, "Amazon", "", "Actuator flanges take M4 (RS03/RS06) and M3 (RS02/RS05); read the pattern off the actuator manual."),
            row("HW_INSERT_M3", "Heat-set inserts M3 x 5, 200 pack", 1, 15.0, "Amazon"),
            row("HW_INSERT_M4", "Heat-set inserts M4 x 6, 100 pack", 1, 12.0, "Amazon"),
            row("HW_INSERT_M5", "Heat-set inserts M5 x 8, 50 pack", 1, 10.0, "Amazon"),
            row("HW_NUTS", "Nyloc nuts and washers M3 / M4 / M5", 1, 8.0, "Amazon"),
            row("HW_LOCTITE", "Threadlocker, medium strength", 1, 8.0, "Amazon", "", "Every actuator flange screw."),
        ])

printed_petg = sum(CATALOG[p]["mass_g"] * CATALOG[p]["qty"] for p in CATALOG
                   if CATALOG[p]["category"] == "printed" and CATALOG[p]["material"] == "petg_cf" and not CATALOG[p].get("optional"))
printed_pla = sum(CATALOG[p]["mass_g"] * CATALOG[p]["qty"] for p in CATALOG
                  if CATALOG[p]["category"] == "printed" and CATALOG[p]["material"] == "pla" and not CATALOG[p].get("optional"))
printed_tpu = sum(CATALOG[p]["mass_g"] * CATALOG[p]["qty"] for p in CATALOG
                  if CATALOG[p]["category"] == "printed" and CATALOG[p]["material"] == "tpu" and not CATALOG[p].get("optional"))
kg = lambda g: math.ceil(g * 1.35 / 1000 * 2) / 2  # +35 % for supports, purge and failures, rounded to 0.5 kg
section("filament", "Printed parts (filament)", "core",
        f"About {printed_petg/1000:.1f} kg of structural prints, {printed_pla/1000:.1f} kg of covers and {printed_tpu/1000:.1f} kg of TPU on the robot; the quantities below add 35 % for supports and failed prints.", [
            row("MAT_PETG_CF", "PETG-CF filament, 1 kg spool", kg(printed_petg), 30.0, "Bambu / Polymaker / Overture", "", "Every structural part. Hardened nozzle. PA-CF is a drop-in upgrade for the hip and knee brackets.", unit_label="kg"),
            row("MAT_PLA", "PLA filament, 1 kg spool", kg(printed_pla), 20.0, "Any", "", "Panels, head, trays.", unit_label="kg"),
            row("MAT_TPU", "TPU 95A filament, 1 kg spool", kg(printed_tpu), 28.0, "Any", "", "Soles and finger pads.", unit_label="kg"),
        ])

section("perception", "Optional: perception kit", "optional",
        "The base robot walks on IMU and joint encoders only, like Berkeley Humanoid Lite. Add a camera when you need it.", [
            row("EL_CAMERA_D435I", CATALOG["EL_CAMERA_D435I"]["name"], 1, 300.0, "Intel / RealSense store", "https://www.intelrealsense.com/", "Fits the head pocket. Needs USB 3 to the hub."),
            row("CB_USB3", "USB 3 cable, USB-C, 1 m", 1, 10.0, "Amazon"),
        ])

section("grippers", "Optional: gripper kit (two hands)", "optional",
        "Duke V2's printed rack-and-pinion parallel gripper, driven by the cheapest widely stocked bus servo.", [
            row("EL_SERVO_STS3215", CATALOG["EL_SERVO_STS3215"]["name"], 2, 16.0, "Feetech / Amazon", "", "One per gripper."),
            row("EL_SERVO_DRIVER", "Waveshare serial bus servo driver board", 1, 5.0, "Waveshare", "", "Both servos on one bus; USB to the hub."),
            row("MAT_GRIPPER", "Filament for both grippers (PLA + TPU)", 1, 8.0, "Any", unit_label="lot"),
        ])

section("tools", "Tools (one-time)", "tools",
        "Not part of the robot. Estimates for a lab or workshop that starts from nothing.", [
            row("TL_PRINTER", "FDM printer with a hardened nozzle and 250 mm bed (e.g. Bambu P1S / X1C class)", 1, 700.0, "", "", "Largest part is the foot plate, 230 mm."),
            row("TL_CHARGER", "LiPo balance charger, 6S, 200 W+", 1, 60.0),
            row("TL_PSU", "Bench power supply, 0-60 V, 10 A", 1, 90.0, "", "", "Bring-up on a current-limited supply before the packs go in."),
            row("TL_SOLDER", "Soldering station + heat-set insert tips", 1, 50.0),
            row("TL_DRIVERS", "Hex driver set, torque wrench 1-10 N·m", 1, 45.0),
            row("TL_METER", "Multimeter", 1, 20.0),
            row("TL_CANTOOL", "RobStride USB-CAN tool (for ID setting) or use a CANable", 1, 20.0),
            row("TL_STAND", "Gantry or hoist rated 50 kg, 1.4 m clear height", 1, 150.0, "", "", "Hang the robot for every bring-up step."),
        ])

# Totals
tiers = {}
for sec in BOM_SECTIONS:
    sec["subtotal"] = round(sum(r["total"] for r in sec["rows"]), 2)
    tiers[sec["tier"]] = round(tiers.get(sec["tier"], 0) + sec["subtotal"], 2)

# ---------------------------------------------------------------------------
# Poses for the viewer (degrees, joint id -> angle)
# ---------------------------------------------------------------------------
POSES = {
    "zero": {"name": "Zero (standing)", "q": {}},
    "crouch": {"name": "Crouch", "q": {}},
    "reach": {"name": "Reach forward", "q": {}},
    "wave": {"name": "Wave", "q": {}},
}
for S in ("L", "R"):
    POSES["crouch"]["q"].update({f"hip_pitch_{S}": 35, f"knee_{S}": 70, f"ankle_pitch_{S}": -35,
                                 f"shoulder_pitch_{S}": -20, f"elbow_{S}": 40})
    POSES["reach"]["q"].update({f"shoulder_pitch_{S}": -80, f"elbow_{S}": 20, f"hip_pitch_{S}": 8, f"knee_{S}": 16, f"ankle_pitch_{S}": -8})
POSES["wave"]["q"].update({"shoulder_pitch_R": -30, "shoulder_roll_R": 120, "elbow_R": 100, "wrist_roll_R": 40,
                           "shoulder_pitch_L": -10, "elbow_L": 25, "waist": 10})

# ---------------------------------------------------------------------------
# Specs summary
# ---------------------------------------------------------------------------
lo = [1e9] * 3
hi = [-1e9] * 3
for lnk in LINKS:
    for o in lnk["parts"]:
        if o.get("optional") == "grippers":
            continue
        for sh in o["shapes"]:
            gc = [sh["c"][k] + lnk["origin"][k] for k in range(3)]
            a, b = shape_bbox(dict(sh, c=gc))
            lo = [min(lo[k], a[k]) for k in range(3)]
            hi = [max(hi[k], b[k]) for k in range(3)]

SPECS = dict(
    dof=len(JOINTS), height_mm=round(hi[2]), width_mm=round(hi[1] - lo[1]), depth_mm=round(hi[0] - lo[0]),
    hip_spacing_mm=2 * HIP_Y, shoulder_spacing_mm=2 * ARM_Y,
    leg_hip_to_ground_mm=HIP_Z, thigh_mm=HIP_Z - KNEE_Z, shank_mm=KNEE_Z - ANKLE_Z, ankle_height_mm=ROLL_Z,
    upper_arm_mm=SH_Z - ELBOW_Z, forearm_mm=round(ELBOW_Z - WRIST_Z, 1), foot_length_mm=230,
    mass_g=mass, mass_total_g=mass_total, optional_mass_g=optional_mass,
    bus_voltage="44.4 V nominal (2 x 6S), 50.4 V full", can_buses=4, can_bitrate="1 Mbit/s",
)

robot = dict(
    meta=dict(name="Fully Open Humanoid", short="FOH", version=VERSION, units="mm",
              frame="X forward, Y left, Z up; ground at z = 0", generated_by="tools/build_data.py"),
    materials=MATERIALS, actuators=ACTUATORS, catalog=CATALOG, links=LINKS, joints=JOINTS, poses=POSES, specs=SPECS,
    groups={"pelvis": "Pelvis", "torso": "Torso and head", "leg_L": "Left leg", "leg_R": "Right leg",
            "arm_L": "Left arm", "arm_R": "Right arm"},
)
bom = dict(meta=dict(version=VERSION, priced_as_of=PRICED_AS_OF, currency="USD"),
           sections=BOM_SECTIONS, tiers=tiers)

# ---------------------------------------------------------------------------
# URDF export (metres, radians).  Link frames coincide with the joint frames
# used above; the pelvis is the base link.  Visual and collision geometry are
# the same primitives the viewer draws; tubes become solid cylinders.
# ---------------------------------------------------------------------------


def shape_inertia(sh, m):
    """Inertia tensor (kg m^2) of one shape about its own centre, in metres."""
    if sh["t"] == "box":
        a, b, c = [v / 1000 for v in sh["s"]]
        return [m / 12 * (b * b + c * c), m / 12 * (a * a + c * c), m / 12 * (a * a + b * b)]
    r = sh["r"] / 1000
    ri = sh.get("ri", 0) / 1000
    l = sh["l"] / 1000
    i_axis = m * (r * r + ri * ri) / 2
    i_perp = m * (3 * (r * r + ri * ri) + l * l) / 12
    i = {"x": [i_axis, i_perp, i_perp], "y": [i_perp, i_axis, i_perp], "z": [i_perp, i_perp, i_axis]}[sh["axis"]]
    return i


def write_urdf(path: Path):
    f = lambda v: f"{v:.5f}"
    out = ['<?xml version="1.0"?>',
           f'<robot name="foh_v{VERSION.replace(".", "_")}">',
           '  <!-- Generated by tools/build_data.py. X forward, Y left, Z up. -->']
    for k, m in MATERIALS.items():
        r, g, b = [int(m["color"][i:i + 2], 16) / 255 for i in (1, 3, 5)]
        out.append(f'  <material name="{k}"><color rgba="{r:.3f} {g:.3f} {b:.3f} 1"/></material>')
    for lnk in LINKS:
        shapes = []   # (shape, mass_kg, material)
        for o in lnk["parts"]:
            cat = CATALOG[o["part"]]
            vols = [vol(sh) for sh in o["shapes"]]
            vt = sum(vols) or 1.0
            mg = cat.get("mass_g", 0)
            for sh, v in zip(o["shapes"], vols):
                shapes.append((sh, mg / 1000 * v / vt, sh.get("m") or cat["material"], o["occ"]))
        mass_kg = sum(s[1] for s in shapes)
        if mass_kg > 0:
            com = [sum(s[1] * s[0]["c"][k] / 1000 for s in shapes) / mass_kg for k in range(3)]
        else:
            com = [0, 0, 0]
        I = [[0.0] * 3 for _ in range(3)]
        for sh, m, _, _ in shapes:
            d = [sh["c"][k] / 1000 - com[k] for k in range(3)]
            ii = shape_inertia(sh, m)
            d2 = sum(x * x for x in d)
            for a in range(3):
                for b in range(3):
                    I[a][b] += (ii[a] if a == b else 0.0) + m * ((d2 if a == b else 0.0) - d[a] * d[b])
        out.append(f'  <link name="{lnk["id"]}">')
        out.append(f'    <inertial><origin xyz="{f(com[0])} {f(com[1])} {f(com[2])}" rpy="0 0 0"/><mass value="{max(mass_kg, 0.001):.4f}"/>'
                   f'<inertia ixx="{I[0][0]:.6e}" ixy="{I[0][1]:.6e}" ixz="{I[0][2]:.6e}" iyy="{I[1][1]:.6e}" iyz="{I[1][2]:.6e}" izz="{I[2][2]:.6e}"/></inertial>')
        for sh, m, mat, occ in shapes:
            c = [v / 1000 for v in sh["c"]]
            if sh["t"] == "box":
                geom = f'<box size="{f(sh["s"][0] / 1000)} {f(sh["s"][1] / 1000)} {f(sh["s"][2] / 1000)}"/>'
                rpy = "0 0 0"
            else:
                geom = f'<cylinder radius="{f(sh["r"] / 1000)}" length="{f(sh["l"] / 1000)}"/>'
                rpy = {"x": "0 1.5707963 0", "y": "1.5707963 0 0", "z": "0 0 0"}[sh["axis"]]
            org = f'<origin xyz="{f(c[0])} {f(c[1])} {f(c[2])}" rpy="{rpy}"/>'
            out.append(f'    <visual name="{occ}">{org}<geometry>{geom}</geometry><material name="{mat}"/></visual>')
            out.append(f'    <collision>{org}<geometry>{geom}</geometry></collision>')
        out.append('  </link>')
    for j in JOINTS:
        parent = LINK_BY_ID[j["parent"]]
        o = [(j["origin"][k] - parent["origin"][k]) / 1000 for k in range(3)]
        a = ACTUATORS[j["actuator"]]
        out.append(f'  <joint name="{j["id"]}" type="revolute">')
        out.append(f'    <parent link="{j["parent"]}"/><child link="{j["child"]}"/>')
        out.append(f'    <origin xyz="{f(o[0])} {f(o[1])} {f(o[2])}" rpy="0 0 0"/><axis xyz="{j["axis"][0]} {j["axis"][1]} {j["axis"][2]}"/>')
        out.append(f'    <limit lower="{math.radians(j["limits"][0]):.4f}" upper="{math.radians(j["limits"][1]):.4f}" effort="{a["peak_nm"]}" velocity="20"/>')
        out.append('    <dynamics damping="0.2" friction="0.0"/>')
        out.append('  </joint>')
    out.append('</robot>')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out) + "\n")


OUT.mkdir(parents=True, exist_ok=True)
(OUT / "robot.json").write_text(json.dumps(robot, separators=(",", ":")) + "\n")
(OUT / "bom.json").write_text(json.dumps(bom, indent=1) + "\n")
write_urdf(ROOT / "assets" / "model" / f"foh_v{VERSION.replace('.', '_')}.urdf")

if __name__ == "__main__":
    n_parts = sum(len(l["parts"]) for l in LINKS)
    print(f"FOH v{VERSION}: {len(LINKS)} links, {len(JOINTS)} joints, {n_parts} part occurrences, {len(CATALOG)} catalogue entries")
    print(f"Envelope: {SPECS['depth_mm']} x {SPECS['width_mm']} x {SPECS['height_mm']} mm")
    for k, v in mass.items():
        print(f"  mass {k:22s} {v/1000:6.2f} kg")
    print(f"  mass total (core)        {mass_total/1000:6.2f} kg   (+{optional_mass/1000:.2f} kg optional kits)")
    for sec in BOM_SECTIONS:
        print(f"  ${sec['subtotal']:9,.2f}  {sec['title']}")
    for t, v in tiers.items():
        print(f"  {t:8s} ${v:,.2f}")
    print("Printed parts:")
    for p in CATALOG.values():
        if p["category"] == "printed":
            print(f"   {p['id']:36s} x{p['qty']:<3d} {p['mass_g']:5d} g  {p['material']}")
    print(f"wrote {OUT/'robot.json'}, {OUT/'bom.json'} and assets/model/foh_v{VERSION.replace('.', '_')}.urdf")
