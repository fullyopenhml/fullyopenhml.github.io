"""Module (sub-assembly) list from the Fusion modules export -> docs/data/modules.csv

    python tools/gen_modules.py ../cad/<export>        (needs <export>/modules.csv from tools/fusion_export_modules)

One row per STEP that fusion_export_modules wrote (every component with child
components down to two levels below the root, grouping folders skipped):

  module_id     slug of the export file name (`Robstride_03_-_no_back_cover` ->
                `robstride-03-no-back-cover`); the staged file is
                docs/files/modules/<module_id>_rev<NN>.step
  english_name  from ENGLISH below, keyed by the Fusion name without the `~N`
                uniqueness suffix; a name that occurs more than once gets the side
                it sits on from its path (left/right arm, left/right leg) or its
                Fusion name in brackets. A name not in ENGLISH keeps the Fusion name
                and gets a note.
  class         module   a sub-assembly of this robot's design
                vendor   a purchased assembly modelled by its vendor (actuator, servo,
                         driver board, camera, IMU, hub, adapter)
                internal a sub-assembly inside a vendor assembly (an actuator's gear
                         stage, a resistor on the servo board): not staged
                sketch   a sketch / section carrier with no manufacturing content: not staged
  depth, qty, children, mass_g, path, file   as exported (mass from Fusion, g)

stage_cad_export.py stages the `module` and `vendor` rows.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
OUT = SITE / "docs" / "data" / "modules.csv"
COLS = ["module_id", "fusion_name", "english_name", "class", "depth", "qty", "children", "mass_g", "path",
        "file", "note"]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage_cad_export import base_name, slug  # noqa: E402

VENDOR = re.compile(r"robstride|^FEETECH|^HL-3608|^wa[rv]eshare|^IntelRealsense|^IMU_syd|^CAN_Isolated"
                    r"|^Vention_USB_Hub|^VEMONT|^bearing_", re.I)
SKETCH = re.compile(r"schematic|cross_section|_face$|sketch", re.I)
# Only what the Fusion tree itself says: the children of each module, and the joint it spans.
ENGLISH = {
    "v2.1_lower_body_latest": "Lower body (pelvis and both legs)",
    "body_LATEST": "Torso (frame, electronics, camera columns)",
    "000_left_arm_long_wrist_latest": "Left arm",
    "000_right_arm_long_wrist_latest": "Right arm",
    "dovetail_umi_gripper": "Gripper",
    "001_left_wrist_long_latest": "Left wrist",
    "001_right_wrist_long_latest": "Right wrist",
    "wrist_3-left": "Wrist-roll drive (RS05 actuator, bearing, wrist block)",
    "elbow_wrist_roll": "Elbow-to-wrist-roll module",
    "shoulder_pitch_shoulder_roll": "Shoulder pitch-to-roll module",
    "shoulder_roll_shoulder_yaw": "Shoulder roll-to-yaw module",
    "shoulder_yaw_elbow": "Shoulder yaw-to-elbow module",
    "elbow_motor_protection": "Elbow motor covers (pair)",
    "elbow_shaft": "Elbow shaft covers (pair)",
    "shoulder_pitch_protection": "Shoulder pitch covers (pair)",
    "shoulder_roll_shaft": "Shoulder roll shaft covers (pair)",
    "shoulder_yaw_protection": "Shoulder yaw cover group",
    "3DP_arm06_x4_RS02_shaft_coupler": "RS02 shaft coupler with its heat-set inserts (one printed part)",
    "3DP_body_05_x1_interior_plate": "Electronics tray (torso interior plate with the electronics mounted)",
    "3DP_body_07_x1_front_plate_removable": "Torso front plate, removable, with its magnets",
    "3DP_body_09_x1_back_plate_removable": "Torso back plate, removable, with its magnets",
    "twincities_v2_nolock": "Camera gimbal column",
    "twincities_v2_nolock_1": "Camera gimbal column (Fusion `twincities_v2_nolock (1)`)",
    "gimbal_arm": "Camera gimbal arm with its link",
    "gimbal_arm_1": "Camera gimbal arm with its link (second column)",
    "power_block_casing": "Power distribution block with casing",
    "base": "Gripper base with its AprilTag holders",
    "double_helix_pinion_16teeth_6mm": "Gripper drive pinion, 16 teeth, double helix",
    "double_helix_rack_30teeth_6mm": "Gripper rack, 30 teeth, double helix",
    "hip_center": "Hip centre (pelvis) module",
    "hip_pitch_hip_roll_L": "Left hip pitch-to-roll module",
    "hip_pitch_hip_roll_R": "Right hip pitch-to-roll module",
    "hip_roll_hip_yaw_L": "Left hip roll-to-yaw module",
    "hip_roll_hip_yaw_R": "Right hip roll-to-yaw module",
    "v2.1_lower_leg_L_copy": "Left leg (knee, shank, ankle, foot)",
    "v2.1_lower_leg_R": "Right leg (knee, shank, ankle, foot)",
    "foot_assembly": "Foot and ankle-roll module",
    "knee_assembly": "Knee module",
    "shanks": "Shank (lower-leg) module",
    "CNC_leg18_x2_foot_plate": "Foot plate with its sole",
    "hip_pitch_motor": "Hip pitch motor covers (pair)",
    "hip_pitch_motor_Mirror": "Hip pitch motor covers, mirrored (pair)",
    "hip_roll_motor": "Hip roll motor covers (pair)",
    "knee_motor_protection": "Knee motor covers",
    "knee_motor": "Knee motor covers (pair)",
    "ankle_roll_motor_protection": "Ankle roll motor covers",
    "ankle_roll_motor": "Ankle roll motor covers (pair)",
    "ankle_roll_structural_part_protection": "Ankle roll structural covers",
    "output_shank": "Output shank covers with cables",
    "ankle_top_cover": "Ankle top cover",
    # vendor assemblies
    "robstride00": "RobStride RS00 actuator (vendor assembly)",
    "robstride_02-No_back_cover": "RobStride RS02 actuator, back cover removed (vendor assembly)",
    "Robstride_03_-_full": "RobStride RS03 actuator with back cover (vendor assembly)",
    "Robstride_03_-_no_back_cover": "RobStride RS03 actuator, back cover removed (vendor assembly)",
    "robstride04": "RobStride RS04 actuator (vendor assembly)",
    "robstride05": "RobStride RS05 actuator (vendor assembly)",
    "robstride05_v16_1": "RobStride RS05 actuator, camera gimbal (vendor assembly)",
    "robstride05_v16_2": "RobStride RS05 actuator, camera gimbal (vendor assembly)",
    "robstride05_v16_1_1": "RobStride RS05 actuator, camera gimbal (vendor assembly)",
    "robstride05_v16_2_1": "RobStride RS05 actuator, camera gimbal (vendor assembly)",
    "Robstride_06-No_Back_Cover": "RobStride RS06 actuator, back cover removed (vendor assembly)",
    "FEETECH_HL_3915_Servo_Motor": "Feetech HL-3915 gripper servo (vendor assembly)",
    "wareshare_st_servo_controller": "Waveshare bus servo driver board (vendor assembly)",
    "IntelRealsense_D435_Multibody": "Intel RealSense D435 camera (vendor model)",
    "IntelRealsense_D435_Multibody_v9_1": "Intel RealSense D435 camera (vendor model, second column)",
    "IMU_syd_dynamics_TM171": "SYD Dynamics TM171 IMU (vendor model)",
    "CAN_Isolated": "USB-CAN adapter with its cables (vendor model)",
    "Vention_USB_Hub": "Vention USB hub (vendor model)",
    "bearing_35x44x5_6707_1.6kN_15g": "Ball bearing 35 x 44 x 5 mm, 6707 (vendor model, two halves)",
    "bearing_45x58x7_6809_5.4kN_40g": "Ball bearing 45 x 58 x 7 mm, 6809 (vendor model, two halves)",
    "bearing_35x47x7_6807_4.0kN_29g": "Ball bearing 35 x 47 x 7 mm, 6807 (vendor model, two halves)",
    "bearing_50x65x7_6810_6.1kN_52g": "Ball bearing 50 x 65 x 7 mm, 6810 (vendor model, two halves)",
    # internals of vendor assemblies and sketch carriers
    "3_1_02_090_0073_ASM_1_1_ASM": "RS03 actuator internals",
    "BACK_COVER1_1_06_EB903-538_1": "RS03 back cover with its screws",
    "R06": "RS06 actuator internals",
    "MAIN": "RS06 stator",
    "HL-3608_ASM_121_ASM": "HL-3915 servo internals",
    "leg_schematics_latest": "Leg sketches and sections",
    "schematics": "Camera column sketches",
    "schematics_1": "Camera column sketches (second column)",
}
SIDE = [("000_left_arm", "left arm"), ("000_right_arm", "right arm"),
        ("v2.1_lower_leg_L", "left leg"), ("v2.1_lower_leg_R", "right leg")]


def side_of(path: str) -> str:
    for needle, word in SIDE:
        if any(seg.startswith(needle) for seg in path.split("+")):
            return word
    return ""


def classify(stem: str, path: str) -> tuple[str, str]:
    """(class, the vendor assembly an `internal` row sits in)."""
    if SKETCH.search(stem):
        return "sketch", ""
    ancestors = [re.sub(r":\d+$", "", s) for s in path.split("+")[:-1]]
    inside = [a for a in ancestors if VENDOR.search(a)]
    if inside:
        return "internal", inside[-1]
    if VENDOR.search(stem):
        return "vendor", ""
    return "module", ""


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1]) / "modules.csv"
    if not src.is_file():
        sys.exit(f"{src} not found: run tools/fusion_export_modules in Fusion first")
    with open(src, encoding="utf-8-sig", newline="") as fh:
        mods = list(csv.DictReader(fh))
    stems = [Path(m["file"]).stem if m["file"] else "" for m in mods]
    bases = [base_name(s) for s in stems]
    dup = {b for b in bases if bases.count(b) > 1}
    rows, unknown, failed = [], [], []
    for m, stem, base in zip(mods, stems, bases):
        if not stem:
            failed.append(m["fusion_name"])
            continue
        cls, inside = classify(base, m["path"])
        note = ""
        name = ENGLISH.get(base)
        if name is None:
            name = m["fusion_name"]
            if cls == "module":
                note = "no English name yet"
                unknown.append(base)
        if base in dup:
            side = side_of(m["path"]) if cls == "module" else ""
            name += f" ({side})" if side else f" (Fusion `{stem}`)"
        if cls == "internal":
            note = f"inside `{inside}`; not staged"
        elif cls == "sketch":
            note = "not staged"
        rows.append(dict(module_id=slug(stem), fusion_name=m["fusion_name"], english_name=name, **{"class": cls},
                         depth=m["depth"], qty=m["qty"], children=m["children"], mass_g=m["mass_g"],
                         path=m["path"], file=m["file"], note=note))
    ids = [r["module_id"] for r in rows]
    clash = sorted({i for i in ids if ids.count(i) > 1})
    if clash:
        sys.exit(f"module_id clash: {clash}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    by_class = {c: sum(1 for r in rows if r["class"] == c) for c in ("module", "vendor", "internal", "sketch")}
    print(f"{OUT.relative_to(SITE).as_posix()}: {len(rows)} modules "
          + ", ".join(f"{n} {c}" for c, n in by_class.items()))
    if failed:
        print(f"  {len(failed)} STEP exports failed in Fusion (no file): {', '.join(failed)}")
    if unknown:
        print(f"  {len(unknown)} without an English name: {', '.join(sorted(set(unknown)))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
