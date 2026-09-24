"""The printed parts of our own design: Fusion component -> site `part_id`.

    python tools/gen_printed.py [path/to/tree.csv]       # prints the mapping

This module no longer writes a CSV: `tools/gen_bom.py` writes
`docs/data/printed-parts.csv` from the team BOM spreadsheet and this table.
What lives here is the mapping itself, which `gen_bom.py`,
`stage_cad_export.py`, `build_viewer.py` and `gen_part_properties.py` all
import so that one part has one ID everywhere (`docs/files/<kind>/<part_id>_
rev<NN>.*`, the viewer, `part-properties.csv`).

Which components are listed is the `PRINTED` table below: the `3DP_` components,
the unnamed `ComponentNN` covers (known only by their `*_protection` material),
the gripper's own parts, the camera-column parts and the end-effector
attachment. `material_of` maps a Fusion material name to a site material and
process only when it is a print material (`MATERIALS`); a custom material name
(`rail`, `Base`, `hip3_protection`, ...) returns blanks, never a guess.
Quantities are the occurrence counts in the tree, summed over the left and
right copies of a component (the arms and legs are separate linked designs, so
one part is two Fusion components with distinct `file_name`s).

Keys of `PRINTED` are Fusion component names, optionally scoped `name|scope`
to one region of the tree (`leg`, `arm`, `body`, `gripper`, `cam`) because the
same name is reused elsewhere: `Component42` is a shank cover in the lower body
and a shoulder cover in the arms; `Component34`..`Component37` are also
RealSense parts in the torso. An unscoped `ComponentNN` key means the arms.
`name` also matches Fusion's `name (1)` copies (the second camera column).

Run it on its own to check a fresh Fusion export: it prints one line per part
(quantity, CAD mass, material) and warns about any entry the tree has no
component for.
"""

from __future__ import annotations

import csv
import glob
import os
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent

# (fusion component name[|scope], part_id, subassembly, description). Roles of the
# unnamed `ComponentNN` covers come from their Fusion material name and position only.
PRINTED = [
    ("3DP_arm05_x4_RS02_shaft_bearing_retainer", "3DP_arm05_RS02_shaft_bearing_retainer", "arm", "RS02 shaft bearing retainer"),
    ("3DP_arm11_x2_wrist_roll", "3DP_arm11_wrist_roll", "arm", "Wrist-roll link"),
    ("Component5", "3DP_arm14_wrist_block", "arm", "Wrist block (Fusion `Component5`, next to the wrist-roll link; role not labelled in CAD)"),
    ("v15_right_end_effector_attachment", "3DP_arm15_end_effector_attachment", "arm", "End-effector attachment between wrist and gripper (Fusion `v15_right_end_effector_attachment`, one per wrist)"),
    ("Component38", "3DP_armP01_elbow_cover_a", "arm", "Elbow cover, half A (Fusion `Component38`, material `elbow_protection`)"),
    ("Component39", "3DP_armP02_elbow_cover_b", "arm", "Elbow cover, half B (Fusion `Component39`, material `elbow_protection`)"),
    ("Component40", "3DP_armP03_shoulder_cover_a", "arm", "Shoulder cover A (Fusion `Component40`, material `shoulder_protection`)"),
    ("Component41", "3DP_armP04_shoulder_cover_b", "arm", "Shoulder cover B (Fusion `Component41`, material `shoulder_protection`)"),
    ("Component42", "3DP_armP05_shoulder_cover_c", "arm", "Shoulder cover C (Fusion `Component42`, material `shoulder_protection`)"),
    ("Component43", "3DP_armP06_shoulder_cover_d", "arm", "Shoulder cover D (Fusion `Component43`, material `shoulder_protection`)"),
    ("Component34", "3DP_armP07_shoulder_cover_e", "arm", "Shoulder cover E (Fusion `Component34`, material `measured_shoulder_protection`)"),
    ("Component35", "3DP_armP08_shoulder_cover_f", "arm", "Shoulder cover F (Fusion `Component35`, material `measured_shoulder_protection`)"),
    ("Component36", "3DP_armP09_shoulder_yaw_cover_a", "arm", "Shoulder-yaw cover A (Fusion `Component36`, material `shoulder_yaw_protection`)"),
    ("Component37", "3DP_armP10_shoulder_yaw_cover_b", "arm", "Shoulder-yaw cover B (Fusion `Component37`, material `shoulder_yaw_protection`)"),
    ("shoulder_yaw_protection|arm", "3DP_armP11_shoulder_yaw_cover_c", "arm", "Shoulder-yaw cover C: the own body of the Fusion `shoulder_yaw_protection` cover group (role not labelled in CAD)"),
    ("3DP_arm06_x4_RS02_shaft_coupler", "3DP_arm06_RS02_shaft_coupler", "arm", "RS02 shaft coupler (with M3 heat-set inserts)"),
    ("3DP_body_05_x1_interior_plate", "3DP_body05_interior_plate", "body", "Torso interior plate (carries the electronics)"),
    ("3DP_body_06_x1_front_plate_fixed", "3DP_body06_front_plate", "body", "Torso front plate"),
    ("3DP_body_07_x1_front_plate_removable", "3DP_body07_front_plate_removable", "body", "Torso front plate, removable"),
    ("3DP_body_09_x1_back_plate_removable", "3DP_body09_back_plate_removable", "body", "Torso back plate, removable"),
    ("3DP_body_08_x1_back_plate_fixed", "3DP_body08_back_plate", "body", "Torso back plate"),
    ("Component194|leg", "3DP_legP01_hip3_cover_a", "leg", "Hip-yaw cover A (Fusion `Component194`, material `hip3_protection`)"),
    ("Component195|leg", "3DP_legP02_hip3_cover_b", "leg", "Hip-yaw cover B (Fusion `Component195`, material `hip3_protection`)"),
    ("Component198|leg", "3DP_legP03_hip3_cover_c", "leg", "Hip-yaw cover C (Fusion `Component198`, material `hip3_protection`)"),
    ("Component199|leg", "3DP_legP04_hip3_cover_d", "leg", "Hip-yaw cover D (Fusion `Component199`, material `hip3_protection`)"),
    ("Component196|leg", "3DP_legP05_hip2_cover_a", "leg", "Hip-roll cover A (Fusion `Component196`, material `hip2_protection`)"),
    ("Component197|leg", "3DP_legP06_hip2_cover_b", "leg", "Hip-roll cover B (Fusion `Component197`, material `hip2_protection`)"),
    ("Component44|leg", "3DP_legP07_knee_cover_a", "leg", "Knee cover A (Fusion `Component44`, material `knee protection`)"),
    ("Component45|leg", "3DP_legP08_knee_cover_b", "leg", "Knee cover B (Fusion `Component45`, material `knee protection`)"),
    ("Component42|leg", "3DP_legP09_shank_cover_a", "leg", "Shank cover A (Fusion `Component42` in the lower body, material `shank protection`)"),
    ("Component43|leg", "3DP_legP10_shank_cover_b", "leg", "Shank cover B (Fusion `Component43` in the lower body, material `shank protection`)"),
    ("Component46|leg", "3DP_legP11_ankle_cover_a", "leg", "Ankle cover A on the ankle-roll motor (Fusion `Component46`, material `ANKLE_1_PROTECTION`)"),
    ("Component47|leg", "3DP_legP12_ankle_cover_b", "leg", "Ankle cover B on the ankle-roll motor (Fusion `Component47`, material `ANKLE_1_PROTECTION`)"),
    ("symmetric_sole", "3DP_leg19_sole", "leg", "Foot sole (Fusion `symmetric_sole`, material `foot_protection`)"),
    ("foot_front", "3DP_leg20_foot_front", "leg", "Foot front cap (Fusion `foot_front`, material `foot_protection`)"),
    # Gripper (Fusion `dovetail_umi_gripper`, two per robot). Its machined mounting
    # flange is CNC_arm13_RS05_shaft_coupler (cnc-parts.csv); servo, servo board and
    # buck converter are vendor parts (electronics.csv).
    ("base|gripper", "3DP_grip01_base", "gripper", "Gripper base (Fusion `base`; carries the two AprilTag holders)"),
    ("custom_umi_gripper v6|gripper", "3DP_grip02_finger", "gripper", "Gripper finger (Fusion `custom_umi_gripper v6`, two per gripper; role read from the name and count, not labelled in CAD)"),
    ("rail|gripper", "3DP_grip03_rail", "gripper", "Gripper slide rail (Fusion `rail`, two per gripper)"),
    ("apriltag_holder|gripper", "3DP_grip04_apriltag_holder", "gripper", "AprilTag holder on the gripper base (Fusion `apriltag_holder`, two per gripper)"),
    ("Component9|gripper", "3DP_grip05_pinion", "gripper", "Double-helix drive pinion, 16 teeth, 6 mm (Fusion `Component9` in `double_helix_pinion_16teeth_6mm`)"),
    ("apriltag|gripper", "3DP_grip06_apriltag_tile", "gripper", "AprilTag tile (Fusion `apriltag`, eight per gripper: four on the fingers, four on the base holders)"),
    # Camera columns (Fusion `twincities_v2_nolock`, two per robot; the second is Fusion's `(1)` copy).
    ("gimbal_mount|cam", "3DP_cam01_gimbal_mount", "head_camera", "Camera-column base (Fusion `gimbal_mount`, one per column)"),
    ("gimbal_neck|cam", "3DP_cam02_gimbal_neck", "head_camera", "Camera-column neck (Fusion `gimbal_neck`, one per column)"),
    ("gimbal_arm|cam", "3DP_cam03_gimbal_arm", "head_camera", "Camera-column arm (Fusion `gimbal_arm`; carries `Component92`)"),
    ("Component92|cam", "3DP_cam04_gimbal_arm_link", "head_camera", "Camera-column arm link (Fusion `Component92`, child of `gimbal_arm`; role not labelled in CAD)"),
]

# Fusion material name (substring, first match wins) -> site material, process.
MATERIALS = [
    ("protection", "TPU", "FDM"),   # team rule 2026-09-21: every protection cover is TPU, FDM-printed
    ("Nylon 12", "Nylon 12, SLS (Formlabs Fuse 1)", "SLS"),
    ("ABS Plastic 60%", "ABS, 60 % infill", "FDM"),
    ("ABS Plastic", "ABS", "FDM"),
    ("PLA (for Bambu H2D)", "PLA (Bambu H2D filament)", "FDM"),
    ("PAHT-CF (for Bambu H2D)", "PAHT-CF (Bambu H2D filament)", "FDM"),
]

# Scope -> prefix of the occurrence path in tree.csv.
SCOPES = {
    "leg": "v2.1_lower_body",
    "arm": "000_",
    "body": "body_LATEST",
    "gripper": "dovetail_umi_gripper",
    "cam": "body_LATEST:1+twincities_v2_nolock",
}


def find_tree(arg: str | None) -> Path:
    if arg:
        return Path(arg)
    trees = sorted(glob.glob(str(SITE.parent / "cad" / "*" / "tree.csv")), key=os.path.getmtime)
    if not trees:
        sys.exit("no cad/*/tree.csv found; run tools/fusion_export in Fusion first")
    return Path(trees[-1])


def load_tree(path: Path) -> dict[str, list[dict]]:
    """Rows with geometry, by Fusion component name (a `name (N)` copy is filed under `name`)."""
    by: dict[str, list[dict]] = {}
    with open(path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if int(r["bodies"]) == 0:
                continue
            by.setdefault(re.sub(r" \(\d+\)$", "", r["fusion_name"]), []).append(r)
    return by


def pick(by: dict[str, list[dict]], key: str) -> list[dict]:
    """Tree rows for one PRINTED key, in tree order."""
    name, _, scope = key.partition("|")
    rows = by.get(name, [])
    if not scope and name.startswith("Component"):
        scope = "arm"
    if scope:
        return [r for r in rows if r["path"].startswith(SCOPES[scope])]
    return rows


def material_of(fusion_material: str) -> tuple[str, str]:
    for needle, material, process in MATERIALS:
        if needle in fusion_material:
            return material, process
    return "", ""


def main() -> int:
    """Print the mapping against a Fusion export; writes nothing."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    path = find_tree(sys.argv[1] if len(sys.argv) > 1 else None)
    tree = load_tree(path)
    print(f"{path}")
    missing = 0
    for key, pid, sub, desc in PRINTED:
        occ = pick(tree, key)
        if not occ:
            print(f"WARNING {pid}: `{key}` is not in the tree", file=sys.stderr)
            missing += 1
            continue
        first = occ[0]
        qty = sum(int(r["qty"]) for r in occ)
        material, process = material_of(first["material"])
        print(f"{pid:42s} {sub:12s} x{qty:<3d} {first['mass_g'] or '?':>7s} g  "
              f"{material or '(no print material)':34s} {process:4s} `{first['material']}`")
    print(f"{len(PRINTED)} printed parts, {missing} not found in this export. "
          f"tools/gen_bom.py writes docs/data/printed-parts.csv from this table.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
