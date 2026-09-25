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

VERSION = "0.2"
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
# Actuator catalogue.  Envelope, mounting and output interfaces are read from the
# RobStride user manuals (Product_Information repository, 2026-07 revision,
# section 1.1 "Outline and mounting dimensions"); torque, Kt and current limits
# from the same manuals and the Duke Humanoid V2 release.  Prices are the Duke
# V2 team BOM's Amazon US / AiFitLab prices, 2026-09; verify before ordering.
#
# Every model mounts by threaded holes in its FRONT face (lug_*) and drives a
# coupler through threaded holes in the output boss (out_*) located by dowel
# pins (pin_*).  The printed joint kit built on that:
#   mount ring (parent): sits on the lug face, bore clears the front step, a
#                        pocket holds the output support bearing
#   coupler (child):     shoulder on the output boss, hub through the bearing,
#                        child plate bolts to the hub face
#   back plate + stub (parent): where the child has a second (inner) plate, a
#                        printed stub carries a 35 mm support bearing
# All offsets are measured from the lug (front) face along the output direction.
# ---------------------------------------------------------------------------
ACTUATORS = {
    "RS03": dict(name="RobStride RS03", peak_nm=60, rated_nm=20, kt=2.36, i_limit=43, mass_g=880, ratio="9:1",
                 dia=98, flange_dia=106, length=56.6, price=225.0,
                 url="https://www.amazon.com/RobStride-60N-m-Integrated-Actuator-Module/dp/B0GY8PJ1MF",
                 body_r=49, body_l=39.5, cover_r=40, cover_l=0, lug_r=53, lug_t=8, step_r=39.75, step_h=6.6, boss_r=35, boss_h=2.5,
                 lug_pcd=98, lug_n=8, lug_screw="M4", lug_depth=8, out_pcd=30.36, out_n=6, out_screw="M4", out_depth=6,
                 pin_pcd=30.36, pin_n=3, pin_d=4, pin_depth=7,
                 mount_t=20, bore_r=40.25, sh_r=31, sh_t=3.5, hub_r=22.5, out_bearing="HW_6809_2RS", ob_od=58, ob_w=7,
                 ring_r=56, back_t=8, sup_bearing="HW_6707_2RS", sb_od=44, sb_id=35, sb_w=5),
    "RS06": dict(name="RobStride RS06", peak_nm=36, rated_nm=11, kt=1.09, i_limit=57, mass_g=621, ratio="9:1",
                 dia=84.5, flange_dia=92, length=49, price=210.0, url="https://www.robstride.com/",
                 body_r=42.25, body_l=33, cover_r=35, cover_l=5.5, lug_r=46, lug_t=4, step_r=41, step_h=9, boss_r=26, boss_h=1.5,
                 lug_pcd=88, lug_n=8, lug_screw="M3", lug_depth=8.5, out_pcd=24, out_n=6, out_screw="M4", out_depth=6,
                 pin_pcd=24, pin_n=3, pin_d=4, pin_depth=4,
                 mount_t=22, bore_r=41.5, sh_r=23, sh_t=3, hub_r=17.5, out_bearing="HW_6807_2RS", ob_od=47, ob_w=7,
                 ring_r=50, back_t=8, sup_bearing="HW_6707_2RS", sb_od=44, sb_id=35, sb_w=5),
    "RS02": dict(name="RobStride RS02", peak_nm=17, rated_nm=6, kt=1.22, i_limit=23, mass_g=405, ratio="7.75:1",
                 dia=65, flange_dia=78.5, length=41.5, price=145.0,
                 url="https://www.amazon.com/RobStride-Integrated-Actuator-Module-Encoders/dp/B0GS5945VP",
                 body_r=32.5, body_l=28, cover_r=30, cover_l=5, lug_r=39.25, lug_t=5, step_r=21.5, step_h=0, boss_r=21.5, boss_h=3.5,
                 lug_pcd=73, lug_n=9, lug_screw="M3", lug_depth=8, out_pcd=24, out_n=6, out_screw="M4", out_depth=7,
                 pin_pcd=24, pin_n=3, pin_d=4, pin_depth=4,
                 mount_t=12, bore_r=23, sh_r=22, sh_t=3, hub_r=17.5, out_bearing="HW_6707_2RS", ob_od=44, ob_w=5,
                 ring_r=45, back_t=8, sup_bearing="HW_6707_2RS", sb_od=44, sb_id=35, sb_w=5),
    "RS05": dict(name="RobStride RS05", peak_nm=5.5, rated_nm=1.6, kt=0.94, i_limit=11, mass_g=191, ratio="7.75:1",
                 dia=46, flange_dia=46, length=44, price=110.0, url="https://www.robstride.com/",
                 body_r=23, body_l=41, cover_r=23, cover_l=0, lug_r=23, lug_t=0, step_r=17.5, step_h=0, boss_r=15, boss_h=3,
                 lug_pcd=41.5, lug_n=8, lug_screw="M3", lug_depth=7, rear_pcd=38.5, rear_n=4, rear_screw="M3", rear_depth=10,
                 out_pcd=24, out_n=6, out_screw="M4", out_depth=3.5, pin_pcd=19, pin_n=3, pin_d=4, pin_depth=3,
                 mount_t=0, bore_r=0, sh_r=22, sh_t=5, hub_r=0, out_bearing=None, ob_od=0, ob_w=0,
                 ring_r=29, back_t=8, sup_bearing=None, sb_od=0, sb_id=0, sb_w=0),
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


P = "printed"
# Joint kits: one coupler per actuator model, shared by every joint of that model
part("3DP_kit03_coupler", "RS03 coupler (output hub)", P, "petg_cf", process="FDM",
     notes="Sits on the RS03 output boss, located by 3 x Ø4 dowels; six M4 x 35 pass through the child plate and this coupler into the boss (PCD 30.36). The Ø45 hub carries the 6809 support bearing. Print in PA-CF if PETG-CF creeps.")
part("3DP_kit06_coupler", "RS06 coupler (output hub)", P, "petg_cf", process="FDM",
     notes="Sits on the RS06 output boss, located by 3 x Ø4 dowels; six M4 x 35 pass through the child plate and this coupler into the boss (PCD 24). Ø35 hub for the 6807 bearing.")
part("3DP_kit02_coupler", "RS02 coupler (output hub)", P, "petg_cf", process="FDM",
     notes="Sits on the RS02 output boss, located by 3 x Ø4 dowels; six M4 x 30 pass through the child plate and this coupler into the boss (PCD 24). Ø35 hub for the 6707 bearing.")
part("3DP_kit05_adapter", "RS05 output adapter", P, "petg_cf", process="FDM",
     notes="Ø44 x 5 disc: 6 x M4 counterbored on PCD 24 into the RS05 output, 4 x M3 inserts on a 30 mm square for the gripper. No support bearing at the wrist.")
# Pelvis and legs
part("3DP_pel01_pelvis_shell", "Pelvis shell", P, "petg_cf", process="FDM",
     notes="One print: box shell, the two RS03 hip-pitch mount rings (8 x M4 on PCD 98, 6809 pocket) on its sides, the waist mount ring on top. 145 x 130 x 190 mm; needs a 250 mm bed.")
part("3DP_leg02_hip_roll_bracket", "Hip-roll bracket", P, "petg_cf", process="FDM", mirror=True,
     notes="Plate on the hip-pitch coupler, web to the hip-roll RS03 mount: mount ring, sleeve, three straps and back plate, open on the inboard side.")
part("3DP_leg04_hip_yaw_housing", "Hip-yaw housing", P, "petg_cf", process="FDM", mirror=True,
     notes="Front plate on the hip-roll coupler, RS03 mount ring and collar for the hip-yaw actuator (axis vertical, output down).")
part("3DP_leg05_thigh_block", "Thigh block with knee mount", P, "petg_cf", process="FDM", mirror=True,
     notes="Plate on the hip-yaw coupler; full RS03 cup for the knee: mount ring, collar, back plate and Ø35 stub for the inner shank plate's bearing.")
part("3DP_leg06_shank_outer_plate", "Shank plate, outer (driven)", P, "petg_cf", process="FDM", mirror=True,
     notes="Bolts to the knee coupler; its lower end is the ankle-pitch RS03 mount ring (8 x M4 on PCD 98, 6809 pocket).")
part("3DP_leg07_shank_inner_plate", "Shank plate, inner (support)", P, "petg_cf", process="FDM", mirror=True,
     notes="Rides on the 6707 bearing on the thigh block's stub; free at the ankle.")
part("3DP_leg08_shank_cross", "Shank cross member", P, "petg_cf", process="FDM", mirror=False,
     notes="Ties the two shank plates together above the ankle-pitch actuator; loom slots for the leg harness.")
part("3DP_leg10_ankle_bracket", "Ankle bracket", P, "petg_cf", process="FDM", mirror=True,
     notes="Plate on the ankle-pitch coupler; RS06 mount ring, collar and back plate for the ankle-roll actuator behind the shank.")
part("3DP_leg11_foot_bracket", "Foot bracket", P, "petg_cf", process="FDM", mirror=True,
     notes="Upright on the ankle-roll coupler, base flange with 4 x M5 to the foot plate.")
part("3DP_leg12_foot_plate", "Foot plate", P, "petg_cf", process="FDM", mirror=True)
part("3DP_leg13_sole", "Foot sole", P, "tpu", process="FDM", mirror=True, notes="TPU 95A, 100 % infill.")
# Torso and head
part("3DP_tor02_bottom_plate", "Torso bottom plate", P, "petg_cf", process="FDM",
     notes="Bolts to the waist coupler (4 x M4 on PCD 32) and to the four 2020 uprights (M5 into tapped ends).")
part("3DP_tor03_top_plate", "Torso top plate", P, "petg_cf", process="FDM")
part("3DP_tor04_shoulder_mount", "Shoulder-pitch mount", P, "petg_cf", process="FDM", mirror=True,
     notes="RS06 mount ring, collar and back plate hung from the top plate; the ring's front face is flush with the torso side.")
part("3DP_tor05_side_panel", "Torso side panel", P, "pla", process="FDM", mirror=True,
     notes="Cosmetic; 4 mm, with a clearance hole for the shoulder-pitch coupler.")
part("3DP_tor06_back_panel", "Torso back panel", P, "pla", process="FDM", notes="Carries the E-stop and the main breaker.")
part("3DP_tor07_front_panel", "Torso front panel", P, "pla", process="FDM", notes="Removable; magnets.")
part("3DP_tor08_electronics_tray", "Electronics tray", P, "pla", process="FDM",
     notes="Mounts the computer, CAN adapters, hub and power parts inside the frame.")
part("3DP_tor09_battery_cradle", "Battery cradle", P, "pla", process="FDM", mirror=False,
     notes="One per pack; straps the pack to the rear of the frame.")
part("3DP_hea01_neck_post", "Neck post", P, "petg_cf", process="FDM")
part("3DP_hea02_head_shell", "Head shell", P, "pla", process="FDM", notes="Blank head with a RealSense mounting pocket. Camera is optional.")
# Arms
part("3DP_arm02_shoulder_bracket", "Shoulder-roll bracket", P, "petg_cf", process="FDM", mirror=True,
     notes="Plate on the shoulder-pitch coupler, 64 mm beam outboard, full RS06 cup (mount ring, collar, back plate) for the shoulder-roll actuator.")
part("3DP_arm04_upper_arm_yoke", "Upper-arm yoke", P, "petg_cf", process="FDM", mirror=True,
     notes="Front plate on the shoulder-roll coupler, shelf under the roll actuator, RS02 mount ring and collar for the shoulder-yaw actuator (output down).")
part("3DP_arm06_upper_arm", "Upper-arm link with elbow mount", P, "petg_cf", process="FDM", mirror=True,
     notes="Plate on the shoulder-yaw coupler; full RS02 cup for the elbow with the Ø35 stub for the inner forearm plate.")
part("3DP_arm08_forearm_outer", "Forearm plate, outer (driven)", P, "petg_cf", process="FDM", mirror=True,
     notes="Bolts to the elbow coupler.")
part("3DP_arm09_forearm_inner", "Forearm plate, inner (support)", P, "petg_cf", process="FDM", mirror=True,
     notes="Rides on the 6707 bearing on the upper arm's stub.")
part("3DP_arm10_forearm_body", "Forearm body with wrist mount", P, "petg_cf", process="FDM", mirror=True,
     notes="Joins both forearm plates; bore and rear pattern (4 x M3 on PCD 38.5) hold the wrist-roll RS05.")
part("3DP_grp01_gripper_body", "Gripper body", P, "pla", process="FDM", mirror=True, optional="grippers",
     notes="Rack-and-pinion parallel gripper after Duke V2; one STS3215 bus servo. Optional kit.")
part("3DP_grp02_finger", "Gripper finger", P, "pla", process="FDM", optional="grippers")
part("3DP_grp03_finger_pad", "Finger pad", P, "tpu", process="FDM", optional="grippers")

# Bearings and metal
H = "hardware"
part("HW_6809_2RS", "Ball bearing 6809-2RS, 45 x 58 x 7 mm", H, "steel", price=3.0,
     vendor="Amazon", notes="Output support bearing of every RS03 joint, on the coupler hub.")
part("HW_6807_2RS", "Ball bearing 6807-2RS, 35 x 47 x 7 mm", H, "steel", price=4.0, vendor="Amazon",
     notes="Output support bearing of every RS06 joint.")
part("HW_6707_2RS", "Ball bearing 6707-2RS, 35 x 44 x 5 mm", H, "steel", price=3.0, vendor="Amazon",
     notes="Output support bearing of every RS02 joint, and the inner-plate support bearing at the knees and elbows.")
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


CLEAR = {"M3": 3.4, "M4": 4.5, "M5": 5.5}          # clearance hole diameters
CBORE = {"M3": (6.0, 3.3), "M4": (8.0, 4.3), "M5": (10.0, 5.3)}   # counterbore diameter, depth
INSERT = {"M3": 4.0, "M4": 5.6, "M5": 6.4}         # heat-set insert hole diameters


def feat(occ, f):
    occ.setdefault("features", []).append(f)


def feat_holes(occ, axis, c, pcd, n, d, t0, t1, phase=0.0, cbore=None):
    f = {"t": "holes", "axis": axis, "c": list(c), "pcd": pcd, "n": n, "d": d, "t0": t0, "t1": t1, "phase": phase}
    if cbore:
        f["cbore"] = list(cbore)      # [dia, depth, side(+1: at t1 end, -1: at t0 end)]
    feat(occ, f)


def feat_cut_cyl(occ, axis, c, d, t0, t1):
    feat(occ, {"t": "cut_cyl", "axis": axis, "c": list(c), "d": d, "t0": t0, "t1": t1})


def feat_cut_box(occ, size, c):
    feat(occ, {"t": "cut_box", "s": list(size), "c": list(c)})


def axpt(axis, t, a, b):
    """Point with axial coordinate t; (a, b) are the other two coordinates in x, y, z order."""
    return {"x": [t, a, b], "y": [a, t, b], "z": [a, b, t]}[axis]


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


def place(lnk, occ, pid, shapes, kind=None, actuator=None, optional=None, inside=None):
    """Place a part occurrence on a link.  shapes are authored in global coords.

    inside: occurrences this part legitimately sits within (a bearing in its seat,
    a hub through a clearance hole, a servo in its housing); the collision audit
    skips those pairs."""
    o = dict(occ=occ, part=pid, shapes=shapes)
    if actuator:
        o["actuator"] = actuator
    if optional:
        o["optional"] = optional
    if inside:
        o["inside"] = [inside] if isinstance(inside, str) else list(inside)
    lnk["parts"].append(o)
    if pid in CATALOG:
        CATALOG[pid]["qty"] += 1
    return o


class Kit:
    """One actuator joint stack, authored from the lug (front) face F along the output direction."""

    def __init__(self, model, axis, out, F, a, b):
        self.I = I = ACTUATORS[model]
        self.model, self.axis, self.out, self.F, self.a, self.b = model, axis, out, F, a, b
        if "ACT_" + model not in CATALOG:
            part("ACT_" + model, I["name"] + " quasi-direct-drive actuator", "actuator", "actuator", mass_g=I["mass_g"],
                 price=I["price"], vendor="RobStride (Amazon US / AiFitLab)", model=model,
                 notes=f"{I['peak_nm']} N·m peak, {I['rated_nm']} N·m rated, Ø{I['dia']} x {I['length']} mm, {I['mass_g']} g. "
                       f"Mounts by {I['lug_n']} x {I['lug_screw']} on PCD {I['lug_pcd']}; output {I['out_n']} x {I['out_screw']} on PCD {I['out_pcd']}.")
        self.back = -(I["lug_t"] + I["body_l"] + I["cover_l"] + I["back_t"])   # back plate's rear face
        self.child_face = I["mount_t"] + 2 if I["mount_t"] else I["boss_h"] + I["sh_t"]

    def pt(self, t):
        return axpt(self.axis, self.F + self.out * t, self.a, self.b)

    def seg(self, t0, t1, r, r_in=None, m=None):
        d = cyl(self.axis, r, abs(t1 - t0), self.pt((t0 + t1) / 2), r_in)
        if m:
            d["m"] = m
        return d

    def actuator_shapes(self):
        I = self.I
        s = []
        b0 = -(I["lug_t"] + I["body_l"])
        s.append(self.seg(b0, -I["lug_t"], I["body_r"], m="actuator"))
        if I["lug_t"]:
            s.append(self.seg(-I["lug_t"], 0, I["lug_r"], m="flange"))
        if I["step_h"]:
            s.append(self.seg(0, I["step_h"], I["step_r"], m="actuator"))
        s.append(self.seg(I["step_h"], I["step_h"] + I["boss_h"], I["boss_r"], m="flange"))
        if I["cover_l"]:
            s.append(self.seg(b0 - I["cover_l"], b0, I["cover_r"], m="enclosure"))
        else:
            s.append(self.seg(b0, b0 + 3, I["body_r"] - 6, m="enclosure"))
        return s

    def mount_shapes(self, collar="full", back=True, stub=False, ring_r=None, back_r=None):
        """Parent-side printed geometry: mount ring (with the bearing pocket), sleeve over the lug
        plate, collar over the body (full tube or three straps leaving `collar` = '-y' etc. open),
        collar over the rear cover, back plate and support stub."""
        I = self.I
        R = ring_r or I["ring_r"]
        s = []
        if I["mount_t"]:
            s.append(self.seg(0, I["mount_t"] - I["ob_w"], R, r_in=I["bore_r"]))
            s.append(self.seg(I["mount_t"] - I["ob_w"], I["mount_t"], R, r_in=I["ob_od"] / 2 + 0.1))
        if I["lug_t"]:
            s.append(self.seg(-I["lug_t"], 0, R, r_in=I["lug_r"] + 0.5))
        b0 = -(I["lug_t"] + I["body_l"])
        if collar == "full":
            s.append(self.seg(b0, -I["lug_t"], R, r_in=I["body_r"] + 0.5))
        elif collar:
            s += self.straps(b0, -I["lug_t"], I["body_r"] + 0.5, R, open_dir=collar)
        if I["cover_l"] and (collar or back):
            s.append(self.seg(b0 - I["cover_l"], b0, back_r or R, r_in=I["cover_r"] + 0.5))
        if back:
            s.append(self.seg(self.back, self.back + I["back_t"], back_r or R))
        if stub:
            s.append(self.seg(self.back - 8, self.back, I["sb_id"] / 2))
        return s

    def straps(self, t0, t1, r_in, r_out, open_dir):
        """Three 20 mm straps along the body, leaving the side `open_dir` ('+y','-y','+z',...) open."""
        axis = self.axis
        others = [ax for ax in "xyz" if ax != axis]
        dirs = []
        for ax in others:
            for sgn in (1, -1):
                if f"{'+' if sgn > 0 else '-'}{ax}" != open_dir:
                    dirs.append((ax, sgn))
        s = []
        L = abs(t1 - t0)
        mid = self.pt((t0 + t1) / 2)
        for ax, sgn in dirs:
            c = list(mid)
            k = "xyz".index(ax)
            c[k] += sgn * (r_in + r_out) / 2
            size = [20, 20, 20]
            size["xyz".index(axis)] = L
            size[k] = r_out - r_in
            s.append(box(size, c, 2))
        return s

    def mount_features(self, occ):
        I = self.I
        if not I["mount_t"]:
            return
        n = I["lug_n"]
        feat_holes(occ, self.axis, self.pt(0), I["lug_pcd"], n, CLEAR[I["lug_screw"]], 0, self.out * I["mount_t"],
                   phase=(22.5 if n == 8 else 0.0), cbore=[CBORE[I["lug_screw"]][0], CBORE[I["lug_screw"]][1], 1])

    def coupler_features(self, occ):
        I = self.I
        t0 = I["step_h"] + I["boss_h"]
        if not I["mount_t"]:      # RS05 adapter: counterbored screws, three insert holes for the end effector
            feat_holes(occ, self.axis, self.pt(t0), I["out_pcd"], I["out_n"], CLEAR[I["out_screw"]], 0, self.out * I["sh_t"],
                       cbore=[CBORE[I["out_screw"]][0], 3.0, 1])
            feat_holes(occ, self.axis, self.pt(t0 + I["sh_t"]), 34, 3, INSERT["M3"], -self.out * 4.0, 0, phase=30)
            return
        feat_holes(occ, self.axis, self.pt(t0), I["out_pcd"], I["out_n"], CLEAR[I["out_screw"]], 0, self.out * (self.child_face - t0))
        feat_holes(occ, self.axis, self.pt(t0), I["pin_pcd"], I["pin_n"], I["pin_d"] + 0.15, 0, self.out * 5.0, phase=30)

    def child_plate_features(self, occ, plate_t):
        """The child plate bolts through the coupler into the output boss: clearance holes, counterbores on
        its outer face, dowel clearance and a locating recess for the hub."""
        I = self.I
        c = self.pt(self.child_face)
        feat_holes(occ, self.axis, c, I["out_pcd"], I["out_n"], CLEAR[I["out_screw"]], 0, self.out * plate_t,
                   cbore=[CBORE[I["out_screw"]][0], CBORE[I["out_screw"]][1], 1])
        if I["mount_t"]:
            feat_holes(occ, self.axis, c, I["pin_pcd"], I["pin_n"], I["pin_d"] + 0.6, 0, self.out * 5.0, phase=30)
            feat_cut_cyl(occ, self.axis, c, 2 * I["hub_r"] + 0.4, 0, self.out * 1.0)

    def inner_plate_features(self, occ):
        I = self.I
        far = self.back - 11
        near = self.back - 1
        feat_cut_cyl(occ, self.axis, self.pt(near), I["sb_od"] + 0.2, 0, -self.out * (I["sb_w"] + 0.3))
        feat_cut_cyl(occ, self.axis, self.pt(far), I["sb_id"] + 4, 0, self.out * 10.0)

    def coupler_shapes(self):
        I = self.I
        t0 = I["step_h"] + I["boss_h"]
        if not I["mount_t"]:
            return [self.seg(t0, t0 + I["sh_t"], I["sh_r"])]
        return [self.seg(t0, t0 + I["sh_t"], I["sh_r"]), self.seg(t0 + I["sh_t"], self.child_face, I["hub_r"])]

    def out_bearing(self):
        I = self.I
        return self.seg(I["mount_t"] - I["ob_w"], I["mount_t"], I["ob_od"] / 2, r_in=I["hub_r"])

    def sup_bearing(self):
        I = self.I
        return self.seg(self.back - 1 - I["sb_w"], self.back - 1, I["sb_od"] / 2, r_in=I["sb_id"] / 2)

    # axial coordinates (global, along the axis) of useful faces
    def at(self, t):
        return self.F + self.out * t

    @property
    def child(self):      # where the child plate's back face sits
        return self.at(self.child_face)

    @property
    def inner(self):      # (near, far) global axial coords of the inner child plate
        return (self.at(self.back - 1), self.at(self.back - 11))

    @property
    def rear(self):       # global axial coordinate of the actuator's rearmost face
        I = self.I
        return self.at(-(I["lug_t"] + I["body_l"] + I["cover_l"]))

    def joint_origin(self):
        return self.pt(self.child_face)


def add_kit(parent_link, child_link, k, occ, coupler_pid, mount_owner=None, mount_pid=None, collar="full", back=True, stub=False,
            ring_r=None, back_r=None, mount_extra=None, optional=None, coupler_inside=None):
    """Place the actuator, its mount geometry and its coupler.  The mount shapes are appended to an
    existing occurrence (mount_owner) or placed as their own part (mount_pid)."""
    side = occ[-1] if occ[-1] in "LR" else None
    act = place(parent_link, f"{occ}_act", "ACT_" + k.model, k.actuator_shapes(), actuator=k.model,
                inside=[f"{occ}_mount"] if mount_pid else ([mount_owner["occ"]] if mount_owner else None))
    mount_shapes = k.mount_shapes(collar=collar, back=back, stub=stub, ring_r=ring_r, back_r=back_r) + (mount_extra or [])
    if mount_owner is not None:
        mount_owner["shapes"] += mount_shapes
        mount_occ = mount_owner["occ"]
    else:
        m = place(parent_link, f"{occ}_mount", mount_pid, mount_shapes)
        mount_occ = m["occ"]
    act["inside"] = [mount_occ]
    k.mount_features(mount_owner if mount_owner is not None else m)
    cp = place(child_link, f"{occ}_coupler", coupler_pid, k.coupler_shapes(), inside=[mount_occ, f"{occ}_act"] + (coupler_inside or []))
    k.coupler_features(cp)
    if k.I["mount_t"]:
        place(parent_link, f"{occ}_bearing", k.I["out_bearing"], [k.out_bearing()], inside=[mount_occ, cp["occ"]])
    return act, mount_occ, cp


# Key dimensions (mm) --------------------------------------------------------
HIP_Z = 460      # hip-pitch and hip-roll axes
HIP_Y = 132      # hip-roll / hip-yaw / knee centreline (hip spacing 264 mm)
KNEE_Z = 263
ANKLE_Z = 100    # ankle-pitch axis
ROLL_Z = 70      # ankle-roll axis
SH_Z = 940       # shoulder-pitch and shoulder-roll axes
ARM_Y = 232      # straight arm: shoulder-roll / yaw / elbow / wrist centreline
ELBOW_Z = 730
TORSO_Z0 = 590   # torso bottom plate's underside = waist coupler face
SHANK_Y = None   # set below from the knee kit
ANKLE_Y = 148    # ankle-roll actuator and foot centreline

# --- Pelvis (root) -----------------------------------------------------------
pelvis = link("pelvis", "Pelvis", "pelvis", (0, 0, 0))
shell = place(pelvis, "pelvis_shell", "3DP_pel01_pelvis_shell", [
    box((130, 144, 10), (0, 0, 515), 3),                                            # top plate z 510..520
    box((130, 32, 10), (0, 34, 405), 3), box((130, 32, 10), (0, -34, 405), 3),        # bottom straps under the actuators
    box((10, 144, 100), (60, 0, 460), 3), box((10, 144, 100), (-60, 0, 460), 3),     # front and back plates x +-55..65
])
hipk = {}
for S, s in (("L", 1), ("R", -1)):
    k = Kit("RS03", "y", s, 52 * s, 0, HIP_Z)       # body y 4.5..44, lug face 52, boss face 61.1, child face 74
    hipk[S] = k
waistk = Kit("RS03", "z", +1, 568, 0, 0)            # body z 520.5..560, child face 590

# --- Torso ---------------------------------------------------------------------
torso = link("torso", "Torso", "torso", (0, 0, TORSO_Z0), "waist")
joint("waist", "Waist yaw", "pelvis", "torso", (0, 0, TORSO_Z0), (0, 0, 1), (-90, 90), "RS03", "centre", "can2", 1, "yaw")
add_kit(pelvis, torso, waistk, "waist", "3DP_kit03_coupler", mount_owner=shell, collar="full", back=False)
Z0 = TORSO_Z0
bp = place(torso, "bottom_plate", "3DP_tor02_bottom_plate", [box((160, 210, 10), (0, 0, Z0 + 5), 4)])
waistk.child_plate_features(bp, 10)
tp = place(torso, "top_plate", "3DP_tor03_top_plate", [box((160, 210, 10), (0, 0, Z0 + 415), 4)])
for sx in (1, -1):
    for sy in (1, -1):
        feat_cut_cyl(bp, "z", (62.5 * sx, 87.5 * sy, Z0), CLEAR["M5"], 0, 10)
        feat_cut_cyl(tp, "z", (62.5 * sx, 87.5 * sy, Z0 + 410), CLEAR["M5"], 0, 10)
for sx in (1, -1):
    for sy in (1, -1):
        tag = ("F" if sx > 0 else "B") + ("L" if sy > 0 else "R")
        place(torso, f"upright_{tag}", "HW_2020_400", [box((20, 20, 400), (62.5 * sx, 87.5 * sy, Z0 + 210))])   # corners x 52.5..72.5, y 77.5..97.5
for S, s in (("L", 1), ("R", -1)):
    place(torso, f"side_panel_{S}", "3DP_tor05_side_panel", [box((145, 4, 270), (0, 99.5 * s, Z0 + 155))])   # z 610..880, below the shoulder bracket sweep
place(torso, "back_panel", "3DP_tor06_back_panel", [box((4, 175, 400), (-74.5, 0, Z0 + 210))])
place(torso, "front_panel", "3DP_tor07_front_panel", [box((4, 175, 400), (74.5, 0, Z0 + 210))])
place(torso, "electronics_tray", "3DP_tor08_electronics_tray", [box((4, 140, 278), (2, 0, Z0 + 159))])   # z 610..888
place(torso, "battery_cradle_L", "3DP_tor09_battery_cradle", [box((56, 70, 6), (-32, 35, Z0 + 21), 2)])
place(torso, "battery_cradle_R", "3DP_tor09_battery_cradle", [box((56, 70, 6), (-32, -35, Z0 + 21), 2)])
place(torso, "battery_1", "EL_BATTERY_6S", [box((52, 64, 166), (-32, 35, Z0 + 107), 3)])
place(torso, "battery_2", "EL_BATTERY_6S", [box((52, 64, 166), (-32, -35, Z0 + 107), 3)])
place(torso, "computer", "EL_PC_N100", [box((45, 128, 128), (28, 0, Z0 + 94), 4)])
for i, (sy, z) in enumerate(((1, 170), (-1, 170), (1, 188), (-1, 188))):
    place(torso, f"can_adapter_{i}", "EL_CANABLE", [box((60, 25, 12), (34, 45 * sy, Z0 + z))])
place(torso, "usb_hub", "EL_USB_HUB", [box((30, 60, 14), (19, 0, Z0 + 170), 2)])
place(torso, "buck_12v", "EL_BUCK_12V", [box((60, 45, 25), (-30, 0, Z0 + 208), 2)])
place(torso, "dist_block", "EL_DIST_BLOCK", [box((50, 60, 20), (29, 0, Z0 + 216), 2)])
place(torso, "contactor", "EL_CONTACTOR", [box((44, 60, 40), (-30, 0, Z0 + 254), 3)])
place(torso, "imu", "EL_IMU", [box((36, 36, 14), (30, 0, Z0 + 17), 2)])
place(torso, "estop", "EL_ESTOP", [box((10, 44, 44), (-81.5, 0, 950)), cyl("x", 20, 22, (-97.5, 0, 950))])
place(torso, "breaker", "EL_BREAKER", [box((18, 36, 60), (-85.5, -55, 880), 2)])
place(torso, "neck_post", "3DP_hea01_neck_post", [cyl("z", 22, 34, (10, 0, Z0 + 437))])
hs = place(torso, "head_shell", "3DP_hea02_head_shell", [box((90, 110, 70), (15, 0, Z0 + 489), 8)])
feat_cut_box(hs, (84, 104, 64), (15, 0, Z0 + 486))            # hollow, 3 mm walls, open at the bottom
feat_cut_box(hs, (30, 92, 28), (60, 0, Z0 + 499))             # camera pocket in the front face
place(torso, "camera", "EL_CAMERA_D435I", [box((26, 90, 26), (55, 0, Z0 + 499), 3)], optional="perception", inside=["head_shell"])

# hip-pitch actuators live on the pelvis; their mounts are part of the shell
# (added when the legs are built so the child link exists)


def build_leg(side):
    s = 1 if side == "L" else -1
    S = side
    base_id, bus = {"L": (11, "can0"), "R": (21, "can1")}[S]
    Y = HIP_Y

    # --- hip pitch: RS03 in the pelvis, output outboard ---
    kp = hipk[S]
    o1 = kp.joint_origin()                                            # (0, 74, 460)
    l1 = link(f"hip_roll_bracket_{S}", f"Hip-roll bracket ({S})", f"leg_{S}", o1, f"hip_pitch_{S}")
    joint(f"hip_pitch_{S}", f"Hip pitch ({S})", "pelvis", l1["id"], o1, (0, 1, 0), (-105, 105), "RS03", S, bus, base_id, "pitch")
    add_kit(pelvis, l1, kp, f"hip_pitch_{S}", "3DP_kit03_coupler", mount_owner=shell, collar="full", back=False)
    y1 = kp.child                                                     # 74: bracket plate back face
    # --- hip roll: RS03 on the bracket, axis x, output forward ---
    kr = Kit("RS03", "x", +1, 22, Y * s, HIP_Z)                       # body x -25.5..14, child face 44
    bracket = place(l1, f"hip_roll_bracket_{S}", "3DP_leg02_hip_roll_bracket", [
        box((54, 8, 70), (-13, y1 + 4 * s, HIP_Z + 11), 3),          # plate on the coupler, y 74..82, x -40..14, z 436..506
        box((15, 30, 60), (-33, y1 + 19 * s, HIP_Z - 4), 3),         # web to the back plate, y 74..104
    ])
    kp.child_plate_features(bracket, 8)
    o2 = kr.joint_origin()                                            # (44, 132, 460)
    l2 = link(f"hip_yaw_housing_{S}", f"Hip-yaw housing ({S})", f"leg_{S}", o2, f"hip_roll_{S}")
    joint(f"hip_roll_{S}", f"Hip roll ({S})", l1["id"], l2["id"], o2, (1, 0, 0), (-12, 105), "RS03", S, bus, base_id + 1, "roll")
    add_kit(l1, l2, kr, f"hip_roll_{S}", "3DP_kit03_coupler", mount_owner=bracket, collar=("-y" if s > 0 else "+y"), back=True, back_r=49)
    # --- hip yaw: RS03 hanging under the roll actuator, output down ---
    ky = Kit("RS03", "z", -1, 347.5, 0, Y * s)                        # body z 355.5..395, back plate to 403, child face 325.5
    housing = place(l2, f"hip_yaw_housing_{S}", "3DP_leg04_hip_yaw_housing", [
        box((12, 90, 175), (kr.child + 6, (Y + 5) * s, 415), 3),       # front plate x 44..56, y 92..182, z 327.5..502.5
    ])
    kr.child_plate_features(housing, 12)
    o3 = ky.joint_origin()                                            # (0, 132, 325.5)
    l3 = link(f"thigh_{S}", f"Thigh ({S})", f"leg_{S}", o3, f"hip_yaw_{S}")
    joint(f"hip_yaw_{S}", f"Hip yaw ({S})", l2["id"], l3["id"], o3, (0, 0, 1), (-90, 90), "RS03", S, bus, base_id + 2, "yaw")
    add_kit(l2, l3, ky, f"hip_yaw_{S}", "3DP_kit03_coupler", mount_owner=housing, collar="full", back=True)
    # --- knee: RS03 in the thigh block, output outboard; full cup with a support stub ---
    kk = Kit("RS03", "y", s, (Y + 27.75) * s, 0, KNEE_Z)              # body y 112.25..151.75, child face 181.75
    thigh = place(l3, f"thigh_block_{S}", "3DP_leg05_thigh_block", [
        box((80, 90, 12), (0, Y * s, ky.child - 6), 3),                # plate z 313.5..325.5 on the yaw coupler
    ])
    ky.child_plate_features(thigh, 12)
    o4 = kk.joint_origin()
    l4 = link(f"shank_{S}", f"Shank ({S})", f"leg_{S}", o4, f"knee_{S}")
    joint(f"knee_{S}", f"Knee ({S})", l3["id"], l4["id"], o4, (0, 1, 0), (0, 105), "RS03", S, bus, base_id + 3, "pitch")
    add_kit(l3, l4, kk, f"knee_{S}", "3DP_kit03_coupler", mount_owner=thigh, collar="full", back=True, stub=True)
    # --- shank: outer plate on the knee coupler + ankle mount ring; inner plate on the stub bearing ---
    yo = kk.child                                                     # 181.75
    yi_near, yi_far = kk.inner                                        # 103.25, 93.25
    global SHANK_Y
    SHANK_Y = (abs(yo) + abs(yi_far) + 10) / 2                        # 142.5
    ka = Kit("RS03", "y", s, 176 * s, 0, ANKLE_Z)                     # ankle pitch: body y 128.5..168, ring 176..196, child face 198
    outer = place(l4, f"shank_outer_{S}", "3DP_leg06_shank_outer_plate", [
        box((72, 10, 220), (0, yo + 5 * s, 190), 4),                   # y 181.75..191.75, z 80..300
    ])
    kk.child_plate_features(outer, 10)
    inner = place(l4, f"shank_inner_{S}", "3DP_leg07_shank_inner_plate", [box((72, 10, 220), (0, yi_far + 5 * s, 190), 4)], inside=[f"thigh_block_{S}"])
    kk.inner_plate_features(inner)
    place(l4, f"knee_support_bearing_{S}", kk.I["sup_bearing"], [kk.sup_bearing()], inside=[f"shank_inner_{S}", f"thigh_block_{S}"])
    place(l4, f"shank_cross_{S}", "3DP_leg08_shank_cross", [box((60, abs(yo - yi_near), 16), (0, (yo + yi_near) / 2, 188), 3)])
    # --- ankle pitch: actuator in the shank (mount ring merged into the outer plate), single-plate child ---
    o5 = ka.joint_origin()                                            # (0, 198, 100)
    l5 = link(f"ankle_block_{S}", f"Ankle block ({S})", f"leg_{S}", o5, f"ankle_pitch_{S}")
    joint(f"ankle_pitch_{S}", f"Ankle pitch ({S})", l4["id"], l5["id"], o5, (0, 1, 0), (-50, 50), "RS03", S, bus, base_id + 4, "pitch")
    add_kit(l4, l5, ka, f"ankle_pitch_{S}", "3DP_kit03_coupler", mount_owner=outer, collar=None, back=False)
    # --- ankle roll: RS06 behind the shank, axis x, output forward; foot upright on its coupler ---
    kroll = Kit("RS06", "x", +1, -89, ANKLE_Y * s, ROLL_Z)            # body x -126..-93, ring -89..-67, child face -65
    ab = place(l5, f"ankle_bracket_{S}", "3DP_leg10_ankle_bracket", [
        box((176, 10, 90), (-43, ka.child + 5 * s, 105), 3),           # plate y 198..208, x -131..45, z 60..150
    ])
    ka.child_plate_features(ab, 10)
    o6 = kroll.joint_origin()                                         # (-61, 148, 70)
    l6 = link(f"foot_{S}", f"Foot ({S})", f"leg_{S}", o6, f"ankle_roll_{S}")
    joint(f"ankle_roll_{S}", f"Ankle roll ({S})", l5["id"], l6["id"], o6, (1, 0, 0), (-30, 30), "RS06", S, bus, base_id + 5, "roll")
    add_kit(l5, l6, kroll, f"ankle_roll_{S}", "3DP_kit06_coupler", mount_owner=ab, collar="full", back=True)
    fbk = place(l6, f"foot_bracket_{S}", "3DP_leg11_foot_bracket", [
        box((10, 54, 72), (kroll.child + 5, ANKLE_Y * s, 56), 3),      # upright x -65..-55, y 121..175, z 20..92
        box((40, 54, 8), (kroll.child + 20, ANKLE_Y * s, 24), 2),      # base flange on the foot plate
    ])
    kroll.child_plate_features(fbk, 10)
    fp = place(l6, f"foot_plate_{S}", "3DP_leg12_foot_plate", [box((235, 92, 12), (-24.5, ANKLE_Y * s, 14), 4)])   # x -142..93
    sole = place(l6, f"sole_{S}", "3DP_leg13_sole", [box((235, 92, 8), (-24.5, ANKLE_Y * s, 4), 3)])
    for occ_, t0, t1 in ((fbk, 20, 28), (fp, 8, 20), (sole, 0, 8)):       # 4 x M5 through the bracket flange, plate and sole
        for dx in (-12, 12):
            for dy in (-18, 18):
                feat_cut_cyl(occ_, "z", (kroll.child + 20 + dx, ANKLE_Y * s + dy, t0), CLEAR["M5"], 0, t1 - t0)


def build_arm(side):
    s = 1 if side == "L" else -1
    S = side
    base_id, bus = {"L": (31, "can2"), "R": (41, "can3")}[S]

    # --- shoulder pitch: RS06 inside the torso, output outboard through the side panel ---
    kp = Kit("RS06", "y", s, 75 * s, 0, SH_Z)                         # body y 38..71, ring 75..97, child face 99
    mount = place(torso, f"shoulder_mount_{S}", "3DP_tor04_shoulder_mount", [
        box((30, 12, 45), (0, 40 * s, 977.5), 2),                      # tab up to the top plate, z 955..1000
    ])
    o1 = kp.joint_origin()                                            # (0, 99, 940)
    a1 = link(f"shoulder_roll_bracket_{S}", f"Shoulder-roll bracket ({S})", f"arm_{S}", o1, f"shoulder_pitch_{S}")
    joint(f"shoulder_pitch_{S}", f"Shoulder pitch ({S})", "torso", a1["id"], o1, (0, 1, 0), (-180, 180), "RS06", S, bus, base_id, "pitch")
    add_kit(torso, a1, kp, f"shoulder_pitch_{S}", "3DP_kit06_coupler", mount_owner=mount, collar="full", back=True,
            coupler_inside=[f"side_panel_{S}"])
    # --- shoulder roll: RS06 on the long bracket, axis x, output forward ---
    kr = Kit("RS06", "x", +1, 14, ARM_Y * s, SH_Z)                    # body x -23..10, ring 14..36, child face 38
    y1 = kp.child                                                     # 99
    br = place(a1, f"shoulder_bracket_{S}", "3DP_arm02_shoulder_bracket", [
        box((54, 12, 80), (-13, y1 + 6 * s, SH_Z), 3),                 # plate y 99..111, x -40..14, z 900..980
        box((50, ARM_Y - 49 - (abs(y1) + 12), 56), (-16, ((abs(y1) + 12) + (ARM_Y - 49)) / 2 * s, SH_Z), 3),   # beam y 111..183
    ])
    kp.child_plate_features(br, 12)
    o2 = kr.joint_origin()                                            # (38, 232, 940)
    a2 = link(f"upper_arm_yoke_{S}", f"Upper-arm yoke ({S})", f"arm_{S}", o2, f"shoulder_roll_{S}")
    joint(f"shoulder_roll_{S}", f"Shoulder roll ({S})", a1["id"], a2["id"], o2, (1, 0, 0), (0, 150), "RS06", S, bus, base_id + 1, "roll")
    add_kit(a1, a2, kr, f"shoulder_roll_{S}", "3DP_kit06_coupler", mount_owner=br, collar="full", back=True, ring_r=49)
    # --- shoulder yaw: RS02 under the roll actuator, output down ---
    ky = Kit("RS02", "z", -1, 840.5, 0, ARM_Y * s)                    # body z 845.5..873.5, cover to 878.5, child face 826.5
    yoke = place(a2, f"upper_arm_yoke_{S}", "3DP_arm04_upper_arm_yoke", [
        box((12, 96, 104), (kr.child + 6, ARM_Y * s, 938), 3),         # front plate x 38..50, z 886..990
        box((76, 96, 10), (12, ARM_Y * s, 884), 3),                    # shelf z 879..889 under the roll cup (bottom 891)
    ])
    kr.child_plate_features(yoke, 12)
    o3 = ky.joint_origin()                                            # (0, 232, 826.5)
    a3 = link(f"upper_arm_{S}", f"Upper arm ({S})", f"arm_{S}", o3, f"shoulder_yaw_{S}")
    joint(f"shoulder_yaw_{S}", f"Shoulder yaw ({S})", a2["id"], a3["id"], o3, (0, 0, 1), (-180, 180), "RS02", S, bus, base_id + 2, "yaw")
    add_kit(a2, a3, ky, f"shoulder_yaw_{S}", "3DP_kit02_coupler", mount_owner=yoke, collar="full", back=False, ring_r=40)
    # --- elbow: RS02 in the upper-arm link, output outboard; full cup with stub ---
    ke = Kit("RS02", "y", s, (ARM_Y + 19) * s, 0, ELBOW_Z)           # body y 218..246, child face 265
    ua = place(a3, f"upper_arm_{S}", "3DP_arm06_upper_arm", [
        box((50, 64, ky.child - 763), (0, ARM_Y * s, (ky.child + 763) / 2), 6),   # link z 763..826.5
    ])
    ky.child_plate_features(ua, 12)
    o4 = ke.joint_origin()                                            # (0, 265, 730)
    a4 = link(f"forearm_{S}", f"Forearm ({S})", f"arm_{S}", o4, f"elbow_{S}")
    joint(f"elbow_{S}", f"Elbow ({S})", a3["id"], a4["id"], o4, (0, 1, 0), (0, 120), "RS02", S, bus, base_id + 3, "pitch")
    add_kit(a3, a4, ke, f"elbow_{S}", "3DP_kit02_coupler", mount_owner=ua, collar="full", back=True, stub=True, ring_r=40)
    # --- forearm: two plates, body below, RS05 wrist inside the body ---
    yo = ke.child                                                     # 265
    yi_near, yi_far = ke.inner                                        # 204, 194
    fo = place(a4, f"forearm_outer_{S}", "3DP_arm08_forearm_outer", [box((60, 10, 110), (0, yo + 5 * s, 680), 4)])
    ke.child_plate_features(fo, 10)
    fi = place(a4, f"forearm_inner_{S}", "3DP_arm09_forearm_inner", [box((60, 10, 110), (0, yi_far + 5 * s, 680), 4)], inside=[f"upper_arm_{S}"])
    ke.inner_plate_features(fi)
    place(a4, f"elbow_support_bearing_{S}", ke.I["sup_bearing"], [ke.sup_bearing()], inside=[f"forearm_inner_{S}", f"upper_arm_{S}"])
    kw = Kit("RS05", "z", -1, 545, 0, ARM_Y * s)                      # body z 545..586, boss to 542, adapter to 537
    fb = place(a4, f"forearm_body_{S}", "3DP_arm10_forearm_body", [
        box((56, abs(yo - yi_far) + 10, 55), (0, (yo + yi_far) / 2 + 5 * s, 597.5), 6),   # y 194..275, z 570..625
        kw.seg(-41, -12, 29, r_in=23.25), kw.seg(-49, -41, 25),        # collar and rear plate around the RS05
    ])
    o5 = kw.joint_origin()                                            # (0, 232, 537)
    a5 = link(f"hand_{S}", f"Hand ({S})", f"arm_{S}", o5, f"wrist_roll_{S}")
    joint(f"wrist_roll_{S}", f"Wrist roll ({S})", a4["id"], a5["id"], o5, (0, 0, 1), (-180, 180), "RS05", S, bus, base_id + 4, "yaw")
    feat_holes(fb, "z", kw.pt(-41), kw.I["rear_pcd"], kw.I["rear_n"], CLEAR["M3"], 0, -8.0, phase=45)   # RS05 rear screws through the rear plate
    act = place(a4, f"wrist_roll_{S}_act", "ACT_RS05", kw.actuator_shapes(), actuator="RS05", inside=[f"forearm_body_{S}"])
    wa = place(a5, f"wrist_roll_{S}_coupler", "3DP_kit05_adapter", kw.coupler_shapes(), inside=[f"wrist_roll_{S}_act"])
    kw.coupler_features(wa)
    gb = place(a5, f"gripper_body_{S}", "3DP_grp01_gripper_body", [box((80, 56, 44), (0, ARM_Y * s, 515), 6)], optional="grippers")
    feat_cut_box(gb, (46.6, 24.6, 41), (0, ARM_Y * s, 512.5))     # servo pocket, open at the bottom
    feat_holes(gb, "z", (0, ARM_Y * s, 537), 34, 3, CLEAR["M3"], 0, -6, phase=30)   # to the wrist adapter's inserts
    place(a5, f"gripper_servo_{S}", "EL_SERVO_STS3215", [box((46, 24, 40), (0, ARM_Y * s, 513), 2)], optional="grippers", inside=[f"gripper_body_{S}"])
    for fs, tag in ((1, "a"), (-1, "b")):   # jaws open front-to-back at wrist zero
        place(a5, f"finger_{S}{tag}", "3DP_grp02_finger", [box((12, 16, 86), (30 * fs, ARM_Y * s, 450), 3)], optional="grippers")
        place(a5, f"finger_pad_{S}{tag}", "3DP_grp03_finger_pad", [box((4, 14, 40), (22 * fs, ARM_Y * s, 433), 1)], optional="grippers")


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
    a = dict(a)
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

def kit_fastener_rows():
    """Screws and pins for the 23 joint kits, counted from the joints and the actuator interfaces."""
    n = {m: sum(1 for j in JOINTS if j["actuator"] == m) for m in ACTUATORS}
    plate = {"RS03": 12, "RS06": 12, "RS02": 10, "RS05": 5}      # thickest child plate per model
    rows = []
    for m in ("RS03", "RS06", "RS02", "RS05"):
        I = ACTUATORS[m]
        if not n[m]:
            continue
        L = (plate[m] + I["mount_t"] + 2 - I["step_h"] - I["boss_h"] if I["mount_t"] else I["sh_t"]) + I["out_depth"]
        L = int(5 * math.ceil(L / 5))
        rows.append(row(f"HW_OUT_{m}", f"{I['out_screw']} x {L} socket-head screw, output couplers ({m})", n[m] * I["out_n"], 0.15, "Amazon / McMaster", "",
                        f"{I['out_n']} per joint through the child plate and coupler into the output boss, PCD {I['out_pcd']}."))
        if I["mount_t"]:
            Lm = int(5 * math.ceil((I["mount_t"] + I["lug_depth"] - 1) / 5))
            rows.append(row(f"HW_LUG_{m}", f"{I['lug_screw']} x {Lm} socket-head screw, mount rings ({m})", n[m] * I["lug_n"], 0.12, "Amazon / McMaster", "",
                            f"{I['lug_n']} per joint through the mount ring into the actuator's front lugs, PCD {I['lug_pcd']}."))
        else:
            rows.append(row(f"HW_REAR_{m}", f"{I['rear_screw']} x 10 socket-head screw, wrist mount ({m})", n[m] * I["rear_n"], 0.12, "Amazon / McMaster", "",
                            f"{I['rear_n']} per joint through the forearm body into the RS05 rear holes, PCD {I['rear_pcd']}."))
    rows.append(row("HW_PIN_4X10", "Dowel pin Ø4 x 10 mm, steel", sum(n.values()) * 3, 0.3, "Amazon / McMaster", "", "Three per joint, locate the coupler on the output boss."))
    return rows


section("hardware", "Bearings, fasteners and extrusion", "core",
        "Thin-section bearings support the back of every joint so the printed adapters see torque, not bending. Sizes follow Duke V2.", [
            row("HW_6809_2RS", CATALOG["HW_6809_2RS"]["name"], CATALOG["HW_6809_2RS"]["qty"], 3.0, "Amazon", "", CATALOG["HW_6809_2RS"]["notes"]),
            row("HW_6807_2RS", CATALOG["HW_6807_2RS"]["name"], CATALOG["HW_6807_2RS"]["qty"], 4.0, "Amazon", "", CATALOG["HW_6807_2RS"]["notes"]),
            row("HW_6707_2RS", CATALOG["HW_6707_2RS"]["name"], CATALOG["HW_6707_2RS"]["qty"], 3.0, "Amazon", "", CATALOG["HW_6707_2RS"]["notes"]),
            row("HW_2020_400", CATALOG["HW_2020_400"]["name"], CATALOG["HW_2020_400"]["qty"], 4.5, "Amazon / Misumi", "", CATALOG["HW_2020_400"]["notes"]),
            row("HW_TNUT_M4", "2020 T-nuts, M4, 50 pack", 1, 8.0, "Amazon"),
            row("HW_CORNER", "2020 inner corner brackets", 8, 0.7, "Amazon"),
        ] + kit_fastener_rows() + [
            row("HW_SCREWS", "M3 / M4 / M5 socket-head screw assortment, stainless", 1, 25.0, "Amazon", "", "Plates, panels, tray, cradles, head."),
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
    POSES["crouch"]["q"].update({f"hip_pitch_{S}": -35, f"knee_{S}": 70, f"ankle_pitch_{S}": -35,
                                 f"shoulder_pitch_{S}": -20, f"elbow_{S}": 40})
    POSES["reach"]["q"].update({f"shoulder_pitch_{S}": -80, f"elbow_{S}": 20, f"hip_pitch_{S}": -8, f"knee_{S}": 16, f"ankle_pitch_{S}": -8})
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
    upper_arm_mm=SH_Z - ELBOW_Z, forearm_mm=round(ELBOW_Z - 537, 1), foot_length_mm=235,
    hand_spacing_mm=2 * ARM_Y,
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
           '  <!-- Generated by tools/build_data.py. X forward, Y left, Z up. -->',
           '  <!-- MuJoCo reads this block; other parsers ignore it. Keeps the coloured visual geoms (group 1) beside the collision geoms (group 0). -->',
           '  <mujoco><compiler discardvisual="false" balanceinertia="true"/></mujoco>']
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
        for k, (sh, m, mat, occ) in enumerate(shapes):
            c = [v / 1000 for v in sh["c"]]
            if sh["t"] == "box":
                geom = f'<box size="{f(sh["s"][0] / 1000)} {f(sh["s"][1] / 1000)} {f(sh["s"][2] / 1000)}"/>'
                rpy = "0 0 0"
            else:
                geom = f'<cylinder radius="{f(sh["r"] / 1000)}" length="{f(sh["l"] / 1000)}"/>'
                rpy = {"x": "0 1.5707963 0", "y": "1.5707963 0 0", "z": "0 0 0"}[sh["axis"]]
            org = f'<origin xyz="{f(c[0])} {f(c[1])} {f(c[2])}" rpy="{rpy}"/>'
            out.append(f'    <visual name="{lnk["id"]}.{occ}#{k}">{org}<geometry>{geom}</geometry><material name="{mat}"/></visual>')
            out.append(f'    <collision name="{lnk["id"]}.{occ}#{k}.col">{org}<geometry>{geom}</geometry></collision>')
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
