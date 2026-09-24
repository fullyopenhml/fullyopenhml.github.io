"""Generate the six parts-list CSVs from the team's BOM spreadsheet.

    python tools/gen_bom.py [path/to/Duke_Humanoid_V2_BOM_WIP.xlsx] [path/to/tree.csv]

The team's spreadsheet ``reference/bom/Duke_Humanoid_V2_BOM_WIP.xlsx`` (one
sheet, 100 part lines) is THE source for every parts list on this site. It
replaces the two exported CSVs the retired ``gen_sheet1.py`` / ``gen_cnc.py``
read; where the two disagree, the spreadsheet wins.

    Category    rows          -> CSV
    Electronics E0-E20 (21)   -> actuators.csv (E1-E6), cables-connectors.csv
                                 (E9), electronics.csv (the rest)
    CNC         C0-C29 (30)   -> cnc-parts.csv
    3DP         P0-P39 (40)   -> printed-parts.csv
    Hardware    H0-H8  (9)    -> fasteners.csv

Every CSV carries the column contract of ``docs/data/README.md`` plus a last
column ``team_ref``: the spreadsheet's ``#`` value (``E3``, ``C21``, ``P20``,
``H1``) the row came from, blank for a row the spreadsheet has no line for.

What this script will not do
----------------------------
* **No invented price.** A blank or ``0`` unit cost becomes a *blank*
  ``unit_cost_usd`` and the note "Team BOM: no price yet", so the cost macros
  skip it and the pages print a red TODO. 39 of the 100 lines are unpriced: the
  30 unpriced 3DP lines and all 9 Hardware lines.
* **No invented mapping.** The CNC and 3DP rows of the spreadsheet carry no
  part IDs, so ``CNC_MAP`` / ``PRINTED_MAP`` below map them to the CAD-derived
  ``part_id``s the rest of the release keys on (``docs/files/<kind>/<part_id>_
  rev<NN>.*``, the viewer, ``part-properties.csv``). Every entry carries its
  evidence in a comment and, where the evidence is a group of parts rather
  than one part, the row itself says so and is marked UNVERIFIED.
* **No dropped CAD part.** A printed or machined part that is in the CAD but
  not in the spreadsheet is kept, unpriced, with the note "not in the team
  BOM". A spreadsheet row with no CAD match keeps its ``team_ref`` as its
  ``part_id`` and says "no CAD match yet".

What settles the mapping
------------------------
The team's exploded-view booklet ``reference/team/duke_humanoid_v2_hardware.pdf``
(15 pages, rendered as ``docs/assets/exploded/team/NN-*.webp``) labels the parts
of every assembly with the spreadsheet's own ids, so it is the evidence for
which CAD component each id is. ``BOOKLET`` below records, per id, the page(s)
that label it and what the label points at; ``OPEN`` records the ids the
booklet does **not** settle. Both are written to ``docs/data/team-map.csv``
together with the CAD counts, one row per spreadsheet line.

Run order: ``gen_bom.py`` (this file, writes all six CSVs and
``team-map.csv``, reads the newest ``cad/*/tree.csv``) then ``gen_cad_manifest.py``,
``gen_punchlist.py``, ``gen_image_manifest.py``. ``gen_printed.py`` is now the
``PRINTED`` mapping module (Fusion component -> ``part_id``) that this script,
``stage_cad_export.py``, ``build_viewer.py`` and ``gen_part_properties.py``
import; it no longer writes a CSV.
"""

from __future__ import annotations

import csv
import os
import re
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_printed import PRINTED, find_tree, load_tree, material_of, pick  # noqa: E402

SITE = Path(__file__).resolve().parent.parent
DATA = SITE / "docs" / "data"
SOURCE = Path(os.environ.get("BOM_SOURCE_DIR", SITE.parent / "reference" / "bom"))
XLSX = SOURCE / "Duke_Humanoid_V2_BOM_WIP.xlsx"

# The spreadsheet's own date: the file the team handed over on 2026-09-19.
PRICED_AS_OF = "2026-09-19"

COLS = ["subassembly", "class", "part_id", "description", "mpn", "vendor", "vendor_url",
        "alt_mpn", "alt_url", "qty_per_robot", "unit_cost_usd", "total_cost_usd",
        "material", "process", "tolerance_finish", "lead_time_days", "priced_as_of",
        "notes", "team_ref"]

NO_PRICE = "Team BOM: no price yet."
NOT_IN_BOM = "Not in the team BOM (Duke_Humanoid_V2_BOM_WIP.xlsx, 2026-09-19): no price and no quantity from it."
RS_ALT = ("SUPPLY RISK, no alternate published. A different actuator model changes the "
          "mounting interface, the shaft and the CAN configuration, so it is not a drop-in "
          "substitution.")

# Link domain -> vendor name. A domain that is not here keeps its host name and
# is reported, so no vendor is ever guessed silently.
VENDORS = {
    "mcmaster.com": "McMaster-Carr",
    "amazon.com": "Amazon",
    "aliexpress.us": "AliExpress",
    "digikey.com": "DigiKey",
    "aifitlab.com": "AiFitLab",
    "waveshare.com": "Waveshare",
    "robotshop.com": "RobotShop",
    "store.realsenseai.com": "RealSense Store",
    "zeeebattery.com": "Zeee",
    "epowerhobby.com": "ePowerHobby",
}

# --------------------------------------------------------------------------- #
# The team's exploded-view booklet: what each label points at.
#
# reference/team/duke_humanoid_v2_hardware.pdf, 15 pages, rendered as
# docs/assets/exploded/team/NN-<name>.webp. Page numbers below are the
# booklet's own (01-torso-frame = p.1 ... 15-whole-robot = p.15). Each entry
# describes what the label points at in the picture and nothing else: what is
# visible, never what is inferred from it. `—` means no page labels that id.
# --------------------------------------------------------------------------- #
BOOKLET: dict[str, tuple[str, str]] = {
    # --- electronics -------------------------------------------------------
    "E0": ("p.2", "the one large light box standing against the printed spine inside the torso"),
    "E1": ("p.9", "the small actuator at the wrist, one per arm"),
    "E2": ("p.9", "the three medium actuators of one arm (shoulder_3, elbow and wrist_1): "
                  "six positions for two arms, which is this line's count"),
    "E3": ("p.1, p.4, p.5", "three actuators in the torso plus four per leg (hip 1 and hip 2 on p.4, "
                            "hip 3 and ankle on p.5): eleven positions, which is this line's count"),
    "E4": ("p.5", "the wide actuator at the knee, one per leg"),
    "E5": ("p.9, p.14", "the short cylinder at the wrist (one per arm) and two per camera gimbal: "
                        "six positions, which is this line's count"),
    "E6": ("p.5, p.9", "the actuator at the ankle roll (one per leg) and at the shoulder (one per arm): "
                       "four positions, against this line's quantity of 2"),
    "E7": ("p.2", "two prismatic packs beside the torso"),
    "E8": ("—", "not labelled in the booklet"),
    "E9": ("—", "not labelled in the booklet"),
    "E10": ("p.13", "the green driver board above the gripper body, one per gripper"),
    "E11": ("—", "not labelled in the booklet"),
    "E12": ("p.13", "the grey converter on its plate beside the gripper body, one per gripper"),
    "E13": ("p.2", "six light boxes with a black connector, in two columns in the tray"),
    "E14": ("p.14", "the camera on the gimbal, one per column"),
    "E15": ("p.13", "the red and grey servo inside the gripper body, one per gripper"),
    "E16": ("p.2", "three port strips on the spine"),
    "E17": ("p.2", "the small module on the top plate of the torso"),
    "E18": ("p.2", "the stepped light block beside the torso"),
    "E19": ("p.2", "two small terminal blocks in the tray"),
    "E20": ("p.2", "two small blocks beside the torso"),
    # --- machined ----------------------------------------------------------
    "C0": ("p.1", "the rectangular plate closing the top of the torso, one off"),
    "C1": ("p.1", "the plate closing the bottom of the torso, with the large round bore, one off"),
    "C2": ("p.1", "the two tall side plates"),
    "C3": ("p.1", "four identical cross braces between the plates"),
    "C4": ("p.4, p.5", "the toothed ring in front of the H0 bearing on the output of the waist actuator "
                       "(p.4, the unlabelled actuator marked Body) and of the hip-1 (p.4) and hip-3 (p.5) "
                       "actuator of each leg: five positions, which is this line's count"),
    "C5": ("p.4, p.5, p.9", "the square coupler plate on the output of the same five RS03 joints (waist, "
                            "hip 1 and hip 3 of each leg) and of the shoulder-1 RS03 of each arm: seven "
                            "positions, which is this line's count"),
    "C6": ("p.4", "the ring bracket carrying the hip-1 actuator, one per leg"),
    "C7": ("p.4", "the flanged ring in front of the hip-2 actuator, one per leg"),
    "C8": ("p.4", "the forked bracket behind the hip-2 actuator, one per leg"),
    "C9": ("p.5", "the shaft arm on the driven side of the hip-3 joint, one per leg"),
    "C10": ("p.5", "the shaft arm on the support side of the hip-3 joint, one per leg"),
    "C11": ("p.5", "the ring bracket in front of the knee actuator, one per leg"),
    "C12": ("p.5", "the round cover behind the knee actuator, one per leg"),
    "C13": ("p.5", "the long shank arm on the driven side, one per leg"),
    "C14": ("p.5", "the long shank arm on the support side, one per leg"),
    "C15": ("p.5", "two small rings at the lower end of the shank arms, two per leg, which is this line's 4"),
    "C16": ("p.5", "the ring bracket at the ankle-pitch joint, one per leg"),
    "C17": ("p.5", "the forked retainer behind the ankle-pitch actuator, one per leg"),
    "E21": ("p.14", "the small angled connector between the camera and the arms, drawn with an unlabelled arrow"),
    "C18": ("p.5", "the ring on the RS06 ankle-roll actuator, one per leg"),
    "C19": ("p.5", "the short shaft arm on the driven side of the ankle roll, one per leg"),
    "C20": ("p.5", "the short shaft arm on the support side of the ankle roll, one per leg"),
    "C21": ("p.5", "the flat foot plate, one per leg"),
    "C22": ("p.9", "the ring plate in front of the shoulder-roll actuator, one per arm"),
    "C23": ("p.9", "the forked retainer behind the shoulder-roll actuator, one per arm"),
    "C24": ("p.9", "the flat shaft bracket at the shoulder, one per arm"),
    "C25": ("p.9", "the same rectangular bracket twice per arm, once at the shoulder and once at the "
                   "elbow, which is this line's name and its count of 4"),
    "C26": ("p.9", "the flat shaft bracket at the elbow, one per arm"),
    "C27": ("p.9", "the same round dished cover twice per arm, one in the shoulder joint stack and one "
                   "in the elbow joint stack, which is this line's name and its count of 4"),
    "C28": ("p.9", "the ring plate in front of the elbow actuator, one per arm"),
    "C29": ("p.9", "the forked retainer behind the elbow actuator, one per arm"),
    # --- printed -----------------------------------------------------------
    "P0": ("p.1", "the interior spine that stands inside the torso frame, one off"),
    "P1": ("p.3", "two identical window frames, one on the front face and one on the back"),
    "P2": ("p.3", "the perforated removable panel on one face of the torso"),
    "P3": ("p.3", "the perforated removable panel on the other face of the torso"),
    "P4": ("p.9", "the cone on the output of the first and of the third RS02 actuator of the arm "
                  "(shoulder_3 and wrist_1), two per arm"),
    "P5": ("p.9", "the square coupler block between the shoulder cone and the elbow actuator, one per arm"),
    "P6": ("p.9", "the barrel at the wrist roll, one per arm"),
    "P7": ("p.9", "the wrist housing of the arm drawn on p.9"),
    "P8": ("p.9", "the end-effector plate below the wrist, one per arm"),
    "P9": ("p.11", "the wrist housing of the mirrored arm: the same shape as P7 on p.9"),
    "P10": ("p.13", "the gripper body, one per gripper"),
    "P11": ("p.13", "the long slide arm with the rack teeth cut along it, two per gripper"),
    "P12": ("p.13", "the double-helix pinion on the servo, one per gripper"),
    "P13": ("p.13", "the curved ribbed finger pad, two per gripper"),
    "P14": ("p.13", "the flat tag holder, two per gripper"),
    "P15": ("p.13", "eight square tiles per gripper, at six label positions (two of them point at a pair): "
                    "sixteen for two grippers, against this line's 12"),
    "P16": ("p.14", "the wide tripod base at the foot of the column"),
    "P17": ("p.14", "the neck above the lower gimbal actuator"),
    "P18": ("p.14", "the thicker of the two gimbal arms: bent, ending in the bolt-circle pad that sits on "
                    "the actuator face"),
    "P19": ("p.14", "the thinner of the two gimbal arms: flat, ending in a plain disc beside the H5 bearing"),
    "P20": ("p.6", "one of the four curved vented covers around the hip-1 and hip-3 motors of one leg"),
    "P21": ("p.6", "one of the four curved vented covers around the hip-1 and hip-3 motors of one leg"),
    "P22": ("p.6", "one of the two curved covers around the hip-2 motor of one leg"),
    "P23": ("p.6", "one of the two curved covers around the hip-2 motor of one leg"),
    "P24": ("p.6", "one of the four curved vented covers around the hip-1 and hip-3 motors of one leg"),
    "P25": ("p.6", "one of the four curved vented covers around the hip-1 and hip-3 motors of one leg"),
    "P26": ("p.6", "one of the two curved covers around the knee motor of one leg"),
    "P27": ("p.6", "one of the two curved covers around the knee motor of one leg"),
    "P28": ("p.6", "two long flat straps with an eye at each end, one on each side of the shank of one leg, "
                   "which is this line's 4 over two legs"),
    "P29": ("p.6", "one of the two curved covers around the ankle-roll motor of one leg"),
    "P30": ("p.6", "one of the two curved covers around the ankle-roll motor of one leg"),
    "P31": ("p.6", "the small teardrop cap at the front of the foot, one per leg"),
    "P32": ("p.6", "the wedge sole under the foot plate, one per leg"),
    "P33": ("p.10", "one of the two curved covers around the shoulder-pitch motor of one arm"),
    "P34": ("p.10", "one of the two curved covers around the shoulder-pitch motor of one arm"),
    "P35": ("p.10", "two curved vented covers labelled P35 on one arm, both drawn at the shoulder end: "
                    "with P36's two they are the four halves of the two-piece roll cover, which is this "
                    "line's 4 over two arms"),
    "P36": ("p.10", "two curved vented covers labelled P36 on one arm, both drawn at the forearm end, "
                    "which is this line's 4 over two arms"),
    "P37": ("p.10", "one of the two curved covers around the elbow motor of one arm"),
    "P38": ("p.10", "one of the two curved covers around the elbow motor of one arm"),
    "P39": ("p.10", "four smooth flat covers per arm, two on the shoulder-roll shaft and two on the elbow "
                    "shaft: eight for two arms, which is this line's count"),
    # --- hardware ----------------------------------------------------------
    "H0": ("p.1, p.4, p.5", "the large bearing at the RS03 joints of the torso and of the legs"),
    "H1": ("p.5", "the bearing at the knee joint, one per leg"),
    "H2": ("p.5, p.9", "the bearings at the shank and at every arm joint"),
    "H3": ("p.5", "the bearings at the ankle, two per leg"),
    "H4": ("p.9", "the small bearing under the wrist housing, one per arm"),
    "H5": ("p.14", "the small bearing on the support side of the gimbal, one per column"),
    "H6": ("—", "screws are not labelled in the booklet"),
    "H7": ("—", "screws are not labelled in the booklet"),
    "H8": ("—", "screws are not labelled in the booklet"),
}

# What the booklet does NOT settle, one line per team BOM id. Everything else
# is `settled` in docs/data/team-map.csv.
OPEN: dict[str, str] = {
    "C25": "Unit price: the team BOM's 57.56 is exactly twice the retired machining quote's 28.78 for the "
           "same part. A drawing cannot price a part.",
    "P20": "Which of the four hip covers this line is, and whether Hip 1 has a cover of its own: the "
           "booklet draws four covers over two motors that do not all look alike, the 2026-09-19 CAD "
           "holds one two-piece design for all eight pieces, and neither names a line.",
    "P21": "Which of the four hip covers this line is (see P20).",
    "P22": "Which half of the hip-2 cover is A and which is B.",
    "P23": "Which half of the hip-2 cover is A and which is B.",
    "P24": "Which of the four hip covers this line is (see P20).",
    "P25": "Which of the four hip covers this line is (see P20).",
    "P26": "Which half of the knee cover is A and which is B.",
    "P27": "Which half of the knee cover is A and which is B.",
    "P29": "Which half of the ankle-roll cover is Top and which is Bot.",
    "P30": "Which half of the ankle-roll cover is Top and which is Bot.",
    "P33": "Which half of the shoulder-pitch cover is A and which is B.",
    "P34": "Which half of the shoulder-pitch cover is A and which is B.",
    "P35": "Which Fusion half is Front and which is Back; the booklet labels P35 twice at the shoulder "
           "end and P36 twice at the forearm end, so the two lines may split by joint rather than by half.",
    "P36": "Which Fusion half is Front and which is Back (see P35).",
    "P37": "Which half of the elbow cover is A and which is B.",
    "P38": "Which half of the elbow cover is A and which is B.",
    "H6": "Quantity: the team BOM gives none, and screws are not labelled in the booklet.",
    "H7": "Quantity: the team BOM gives none, and screws are not labelled in the booklet.",
    "H8": "Quantity: the team BOM gives none, and screws are not labelled in the booklet.",
}

# --------------------------------------------------------------------------- #
# purchased parts: Electronics (E0-E20) and Hardware (H0-H8)
#
# (team_ref, csv, part_id, subassembly, description, mpn, extra note). The
# part_ids of rows that were already published keep their IDs (gen_vendor_map.py
# and docs/assets/viewer/vendor-map.json key on them); new rows follow the same
# scheme. `description` is the curated English name where the item is unchanged,
# the spreadsheet's own text where it is new; the spreadsheet's text is in the
# notes of every row either way.
# --------------------------------------------------------------------------- #
ACT_FILE, EL_FILE, CAB_FILE, FAS_FILE = (
    "actuators.csv", "electronics.csv", "cables-connectors.csv", "fasteners.csv")

# Quantities the site publishes instead of the team sheet's, where the robot is known to
# differ from the spreadsheet. The line total follows the published quantity.
QTY_OVERRIDE: dict[str, str] = {
    "E6": "4",   # RS06: ankle_2 + shoulder_2, both sides (team sheet: 2)
}

# Printed-part quantities the site publishes instead of the Fusion occurrence count. The
# 2026-09-19 model carries the shank covers on the right leg only; the team BOM (P28, 4 off)
# and every other leg cover (both legs) say the robot has them on both legs.
PRINTED_QTY_OVERRIDE: dict[str, int] = {
    "3DP_legP09_shank_cover_a": 2,
    "3DP_legP10_shank_cover_b": 2,
}

# Small purchased parts the robot has that the team xlsx has no line for. Numbered on from
# the team's series (decided with the user, 2026-09-21) and listed as lab consumables: no
# price, no vendor, by decision ("鸡毛蒜皮的东西不标价"). (ref, csv, part_id, subassembly,
# description, mpn, qty, note)
SITE_PURCHASED: list[tuple[str, str, str, str, str, str, str, str]] = [
    ("E21", EL_FILE, "EL_USBC_ADAPTER", "electronics",
     "USB-C right-angle adapter, camera cable to the D436", "", "2",
     "Site-added line E21 (2026-09-21): the Fusion component `U-joint_type_C_adapter v3`, one per "
     "camera column, drawn on booklet p.14 with an unlabelled arrow. Not in the team xlsx yet: "
     "no price, no vendor."),
]

PURCHASED: list[tuple[str, str, str, str, str, str, str]] = [
    # --- actuators ---------------------------------------------------------
    ("E1", ACT_FILE, "ACT_RS00", "actuators", "RobStride 00 quasi-direct-drive actuator", "RobStride 00", RS_ALT),
    ("E2", ACT_FILE, "ACT_RS02", "actuators", "RobStride 02 quasi-direct-drive actuator", "RobStride 02", RS_ALT),
    ("E3", ACT_FILE, "ACT_RS03", "actuators", "RobStride 03 quasi-direct-drive actuator", "RobStride 03", RS_ALT),
    ("E4", ACT_FILE, "ACT_RS04", "actuators", "RobStride 04 quasi-direct-drive actuator", "RobStride 04", RS_ALT),
    ("E5", ACT_FILE, "ACT_RS05", "actuators", "RobStride 05 quasi-direct-drive actuator", "RobStride 05",
     "Quoted below the RS 02 and the RS 00, which does not follow the model numbering; "
     "re-check with the vendor before ordering. " + RS_ALT),
    ("E6", ACT_FILE, "ACT_RS06", "actuators", "RobStride 06 quasi-direct-drive actuator", "RobStride 06",
     "Quantity is the robot's, not the team BOM's: the sheet buys 2, the robot has four RS06 "
     "joints (ankle_2 and shoulder_2 on both sides, `deploy/control/humanoid_config.py`; booklet "
     "p.5 and p.9). Decided 2026-09-21 by the team: build to the robot. " + RS_ALT),
    # --- electronics -------------------------------------------------------
    ("E0", EL_FILE, "EL_COMPUTE_MINIPC", "electronics", "MINISFORUM X1-470 mini PC (onboard computer)", "X1-470",
     "Module (III) on the hardware overview figure. The 2026-09-19 link is the X1-Pro-470 listing; "
     "the model on the site is the X1-470 **UNVERIFIED**."),
    ("E7", EL_FILE, "EL_BATTERY_6S", "electronics", "Zeee 6S LiPo battery, 10000 mAh, 22.2 V, 2-pack", "10000mah-22-2v-120c-ec5",
     "Priced as one 2-pack, which is how the team BOM records it (its item text ends in x2). "
     "Whether both packs are carried at once is not stated there."),
    ("E8", EL_FILE, "EL_TVS_DIODE", "electronics", "TVS diode, 53 V working / 85 V clamping", "M1.5KE62CA",
     "Manufacturer part number read from the DigiKey link. Where the ten diodes are installed "
     "is not documented in the team BOM."),
    ("E10", EL_FILE, "EL_SERVO_DRIVER", "electronics", "Waveshare serial bus servo driver board, ST/SC series", "25514",
     "Two boards for the two Feetech bus servos."),
    ("E11", EL_FILE, "EL_BUCK_12V_ENC", "electronics", "DC 20-60 V to 12 V encased buck converter", "B0G2SV9PFY", ""),
    ("E12", EL_FILE, "EL_BUCK_48V_12V", "electronics", "48 V to 12 V buck converter", "6.5V-60V To 5V/12V Dc", ""),
    ("E13", EL_FILE, "EL_CAN_ADAPTER", "electronics", "CANable PRO V2.0 USB-CAN controller", "CANable PRO V2.0",
     "Six adapters, one per CAN bus."),
    ("E14", EL_FILE, "EL_CAM_D436", "electronics", "Intel RealSense D436 depth camera", "D436",
     "SUPPLY RISK, no alternate published. One per camera gimbal. The workspace study assumes "
     "this camera's 90x65 degree RGB field of view, so a substitute changes the result the "
     "design was optimised for."),
    ("E15", EL_FILE, "EL_SERVO_FEETECH", "electronics", "Feetech HL-3915-C001 12 V servo, 14.2 kg-cm",
     "HL-3915-C001", "One servo per gripper."),
    ("E16", EL_FILE, "EL_USB_HUB", "electronics", "Vention USB hub", "B0D2XWJ99H", ""),
    ("E17", EL_FILE, "EL_IMU_TM171", "electronics", "SYD Dynamics TransducerM TM171 9-axis AHRS, dual-port",
     "TM171", "Listed in the team BOM only as \"IMU\"; the model is read from the vendor link."),
    ("E18", EL_FILE, "EL_SURGE_PROTECTOR", "electronics", "TTocas surge protector", "E9",
     "New in the 2026-09-19 team BOM. The power wiring diagram puts a surge protector in the "
     "pack lead before the 48 V bus; that this is that part is **UNVERIFIED**, and the link is "
     "a vendor storefront, not one product."),
    ("E19", EL_FILE, "EL_DIST_BLOCK", "electronics", "Power distribution block terminals", "6x8-7",
     "New in the 2026-09-19 team BOM. Four off, which matches the two power + ground pairs "
     "drawn on the power wiring diagram; that the drawn blocks are this part is **UNVERIFIED**."),
    ("E20", EL_FILE, "EL_VOLTAGE_CHECKER", "electronics", "LiPo voltage checker, 1-8S, with case", "Aoicrie 1S-8S 2-pack",
     "New in the 2026-09-19 team BOM. Two off; where they sit on the robot is not stated."),
    # --- cables and connectors --------------------------------------------
    ("E9", CAB_FILE, "CBL_USBA_USBC_BELKIN", "harness", "Belkin USB-A to USB-C cable, 6.6 ft, 2-pack", "",
     "Grouped under Electronics in the team BOM; filed here with the rest of the cabling. "
     "Quantity 2 means two 2-packs."),
    # --- fasteners and bearings -------------------------------------------
    ("H0", FAS_FILE, "FAS_BEARING_45X58X7", "fasteners", "Ball bearing, 45 x 58 x 7 mm", "", ""),
    ("H1", FAS_FILE, "FAS_BEARING_50X65X7", "fasteners", "Ball bearing, 50 x 65 x 7 mm", "",
     "The team design log calls the 50 x 65 x 7 mm bearing the main bearing and models "
     "McMaster-Carr 6656K229; the team BOM gives no part number or link."),
    ("H2", FAS_FILE, "FAS_BEARING_35X44X5", "fasteners", "Ball bearing, 35 x 44 x 5 mm", "", ""),
    ("H3", FAS_FILE, "FAS_BEARING_35X47X7", "fasteners", "Ball bearing, 35 x 47 x 7 mm", "", ""),
    ("H4", FAS_FILE, "FAS_BEARING_30X37X4", "fasteners", "Ball bearing, 30 x 37 x 4 mm", "", ""),
    ("H5", FAS_FILE, "FAS_BEARING_10X15X4", "fasteners", "Ball bearing, 10 x 15 x 4 mm", "", ""),
    ("H6", FAS_FILE, "FAS_SCREW_M3X10_TORX_BH", "fasteners", "M3 x 10 Torx button-head screw", "",
     "The team BOM gives no quantity. It also conflicts with the team design log, which "
     "specifies M3x12 (McMaster-Carr 90991A115) **UNVERIFIED**."),
    ("H7", FAS_FILE, "FAS_SCREW_M4X8_TORX_BH", "fasteners", "M4 x 8 Torx button-head screw", "",
     "The team BOM gives no quantity."),
    ("H8", FAS_FILE, "FAS_SCREW_M4X10_TORX_BH", "fasteners", "M4 x 10 Torx button-head screw", "",
     "The team BOM gives no quantity. It also conflicts with the team design log, which "
     "specifies M4x12 (McMaster-Carr 90991A123) **UNVERIFIED**."),
]

# --------------------------------------------------------------------------- #
# CNC rows C0-C29 -> the CAD-derived part_id.
#
# Evidence per line: the spreadsheet's item name and unit cost x quantity, and
# the same figures in the superseded machining quote
# (reference/bom/duke-humanoid-v2_BOM_sheet2_cnc-parts.csv), whose part names
# ARE the CAD names. Every price below matches that quote's line total divided
# by its lot, which is what ties a team name such as "Foot" to `CNC_leg18`.
# --------------------------------------------------------------------------- #
CNC_MAP: list[tuple[str, str, str]] = [
    # team_ref, part_id, note beyond the price/quantity match
    ("C0", "CNC_body03_top_plate", ""),                      # Body Plate - Top 64.53 x1 = quote CNC_body03_x1_top_plate 64.53
    ("C1", "CNC_body01_bottom_plate", ""),                   # Body Plate - Bottom 64.03 x1 = quote CNC_body01_x1_bottom_plate
    ("C2", "CNC_body02_side_plate", ""),                     # Body Plate - Side 109.14 x2 = quote CNC_body02_x2_side_plate
    ("C3", "CNC_body04_front_plate", ""),                    # Body Plate - Front/Back 47.08 x4 = quote CNC_body04_x4_front_plate
    ("C4", "CNC_leg03_RS03_shaft_bearing_retainer",
     "Booklet p.4 and p.5: the toothed ring in front of the H0 bearing on the output of the waist "
     "actuator (p.4, the unlabelled actuator marked Body) and of the hip-1 (p.4) and hip-3 (p.5) "
     "actuator of each leg: five positions, which is the team BOM's 5 and the Fusion tree's 5."),
    # Robstride 03 Bearing Retainer 49.34 x5 = quote CNC_leg03_x5 49.34 x5
    ("C5", "CNC_leg02_RS03_shaft_coupler",
     "Booklet p.4, p.5 and p.9: the square coupler plate on the output of the waist actuator and of "
     "the hip-1 and hip-3 actuator of each leg (the same joints as C4) and of the shoulder-1 actuator "
     "of each arm: seven positions, which is the team BOM's 7 and the Fusion tree's 7 (5 in "
     "`hip_center`, 1 in the right leg's `knee_assembly`, 1 in the left arm). "
     "The quote carries this part as two lots (6 pcs at 274.02 and 2 pcs at 100.26, 374.28 for 8); "
     "the team BOM prices it at 46.785 each, which is that 374.28 divided by 8, for 7 pieces."),
    # Robstride 03 Output Shaft 46.785 x7; quote name CNC_leg02_x7_RS03_shaft_coupler
    ("C6", "CNC_leg01_hip_center_back", ""),                 # Hip 1 Motor Bracket 81.59 x2 = quote CNC_leg01_x2_hip_center_back
    ("C7", "CNC_leg04_hip_roll_front_bearing_retainer", ""), # Hip 2 Motor Bracket 48.59 x2 = quote CNC_leg04_x2
    ("C8", "CNC_leg05_hip_roll_back_bearing_retainer", ""),  # Hip 2 Bearing Retainer 68.02 x2 = quote CNC_leg05_x2
    ("C9", "CNC_leg06_hip_roll_output_shaft", ""),           # Hip 3 Output Shaft 59.96 x2 = quote CNC_leg06_x2
    ("C10", "CNC_leg07_hip_roll_support_shaft", ""),         # Hip 3 Supporting Shaft 57.43 x2 = quote CNC_leg07_x2
    ("C11", "CNC_leg08_knee_front_bearing_retainer", ""),    # Knee Motor Bracket 54.81 x2 = quote CNC_leg08_x2
    ("C12", "CNC_leg09_knee_motor_back_cover", ""),          # Knee Bearing Retainer 81.35 x2 = quote CNC_leg09_x2
    ("C13", "CNC_leg10_knee_output_shank", ""),              # Shank Shaft 113.29 x2 = quote CNC_leg10_x2
    ("C14", "CNC_leg11_knee_support_shank", ""),             # Shank Support 50.05 x2 = quote CNC_leg11_x2
    ("C15", "CNC_leg12_lower_leg_bearing",
     "Booklet p.5 labels two rings at the lower end of the shank arms of one leg, which is the team "
     "BOM's 4 and the Fusion tree's 4. The quote's name says x4 and its lot was 5 pieces."),
    # Shank Joint Cap 16.50 x4 = quote CNC_leg12_x4_lower_leg_bearing 16.50
    ("C16", "CNC_leg13_ankle_pitch_front", ""),              # Ankle Motor Bracket 78.82 x2 = quote CNC_leg13_x2
    ("C17", "CNC_leg14_ankle_pitch_back", ""),               # Ankle Bearing Retainer 95.85 x2 = quote CNC_leg14_x2
    ("C18", "CNC_leg15_RS06_shaft_bearing_retainer", ""),    # Robstride 06 Bearing Retainer 37.81 x2 = quote CNC_leg15_x2
    ("C19", "CNC_leg16_ankle_roll_output_shaft", ""),        # Foot Shaft 39.40 x2 = quote CNC_leg16_x2
    ("C20", "CNC_leg17_ankle_roll_support_shaft", ""),       # Foot Support 34.60 x2 = quote CNC_leg17_x2
    ("C21", "CNC_leg18_foot_plate", ""),                     # Foot 53.76 x2 = quote CNC_leg18_x2_foot_plate
    ("C22", "CNC_arm01_shoulder_roll_front_bearing", ""),    # Shoulder Motor Bracket 46.69 x2 = quote CNC_arm01_x2
    ("C23", "CNC_arm02_shoulder_roll_back_bearing", ""),     # Shoulder Bearing Retainer 99.24 x2 = quote CNC_arm02_x2
    ("C24", "CNC_arm03_shoulder_roll_output_shaft", ""),     # Shoulder Shaft 31.72 x2 = quote CNC_arm03_x2
    ("C25", "CNC_arm04_shoulder_roll_support_shaft",
     "Booklet p.9 labels the same rectangular bracket twice per arm, once at the shoulder and once at "
     "the elbow: four pieces, which is the team BOM's Shoulder/Elbow Support and the Fusion component "
     "`CNC_arm04_x4_shoulder_elbow_support_shaft` (4 occurrences). PRICE CONFLICT: the quote prices it "
     "at 28.78 each for 4, exactly half the team BOM's 57.56 each for 4. Which unit price holds is "
     "UNVERIFIED; the team BOM's is used here."),
    # Shoulder/Elbow Support 57.56 x4
    ("C26", "CNC_arm09_elbow_output_shaft", ""),             # Elbow Shaft 31.42 x2 = quote CNC_arm09_x2
    ("C27", "CNC_arm10_r03_back_cover",
     "Booklet p.9 labels the same round dished cover twice per arm, once in the shoulder joint stack "
     "and once in the elbow joint stack: four pieces, which is this line and the Fusion component "
     "`CNC_arm10_x4_r03_back_cover` (4 occurrences). One part, two names: the team BOM calls it a "
     "coupler, the CAD a back cover. Price and quantity are the quote's exactly."),
    # Shoulder/Elbow Coupler 54.25 x4 = quote CNC_arm10_x4 54.25 x4
    ("C28", "CNC_arm07_elbow_front_bearing", ""),            # Elbow Motor Bracket 57.94 x2 = quote CNC_arm07_x2
    ("C29", "CNC_arm08_elbow_back_bearing", ""),             # Elbow Bearing Retainer 65.65 x2 = quote CNC_arm08_x2
]

# Machined parts outside the team BOM are not listed (CNC_arm05/06/11 are the SLS-printed
# 3DP_arm05/06/11; CNC_arm12 is not in the model; CNC_arm13 is the gripper flange).
CNC_EXTRA: list[tuple[str, str, str, str]] = []   # team decision 2026-09-21: the parts list is the team BOM's machined lines only

# --------------------------------------------------------------------------- #
# 3DP rows P0-P39 -> the CAD-derived part_id(s).
#
# (team_refs, part_ids, note). Several refs on one part = the spreadsheet
# splits one CAD component into left/right or A/B lines; several parts on one
# ref = one spreadsheet line covers several CAD components. The quantity
# written to the CSV is always the Fusion occurrence count, and the row says so
# when the spreadsheet's count differs.
#
# Eight of the ten priced rows are matched by MASS: the spreadsheet's `weight`
# column times its `price per unit weight` is its unit cost, and that weight, read
# as kilograms, equals the Fusion mass of the component in tree.csv to 0.1 g
# (with its child components for body07/body09). P5 matches by STL volume at the
# Nylon 12 density the other nylon lines imply; P0 matches by name and material
# only. Every row's note says which case it is (`weight_check`). The unpriced
# rows have no weight, so they are matched by Fusion material group, piece count
# and name.
# --------------------------------------------------------------------------- #
PRINTED_MAP: list[tuple[tuple[str, ...], tuple[str, ...], str]] = [
    # ---- priced rows: mass-matched ---------------------------------------
    (("P0",), ("3DP_body05_interior_plate",),
     "Booklet p.1: the one printed interior spine that stands inside the torso frame and carries the "
     "computer, which is this component. Its weight cannot be checked against the export (see below)."),
    # PC Mount, PLA x1; weight 0.3175725 -> 317.6 g; Fusion mass 4637.4 g includes 36 children
    (("P1",), ("3DP_body06_front_plate", "3DP_body08_back_plate"),
     "Booklet p.3: two identical window frames, one on the front face of the torso and one on the back, "
     "which is this line's 2 pieces. Its weight (73.888 g) is the CAD mass of the front plate "
     "(73.9 g); the back plate is 73.2 g and is priced at the same rate here."),
    (("P2",), ("3DP_body07_front_plate_removable",),
     "Booklet p.3: one of the two perforated removable panels of the torso; which face is the front is "
     "settled by the weight, not by the drawing."),
    # Front Plate, PLA x1; weight 0.096876586 -> 96.9 g = CAD mass of body07
    (("P3",), ("3DP_body09_back_plate_removable",),
     "Booklet p.3: the other perforated removable panel of the torso."),
    # Back Plate, PLA x1; weight 0.113809991 -> 113.8 g = CAD mass of body09
    (("P4",), ("3DP_arm05_RS02_shaft_bearing_retainer",),
     "Booklet p.9: the cone on the output of the first and of the third RS02 actuator of the arm "
     "(shoulder_3 and wrist_1), two per arm, which is this line's 4 and the component's 4 occurrences. "
     "The booklet draws it as a printed part, not a machined one."),  # Arm Shaft Cover, Nylon 12 x4; weight 70.62 g = CAD 70.6 g
    (("P5",), ("3DP_arm06_RS02_shaft_coupler",),
     "Booklet p.9: the square coupler block between the shoulder cone and the elbow actuator, one per "
     "arm. The weight (64.6 g) is this part's STL volume in part-properties.csv (63.67 cm3) at the "
     "density the other Nylon 12 lines imply (1.014 g/cm3); the Fusion mass, 67.5 g, includes "
     "the component's 6 child components."),  # Elbow Shaft Coupler, Nylon 12 x2; 2 occurrences
    (("P6",), ("3DP_arm11_wrist_roll",),
     "Booklet p.9: the barrel at the wrist roll, one per arm."),
    # Wrist Shaft, Nylon 12 x2; weight 72.10 g = CAD 72.1 g, 2 occurrences
    (("P7", "P9"), ("3DP_arm14_wrist_block",),
     "The team BOM splits this component into a right-hand and a left-hand line of one piece each "
     "(Wrist Housing R and L); both carry the same weight, 138.0 g, which is this part's CAD mass. "
     "Booklet p.9 labels the housing P7 on one arm and p.11 labels the same shape P9 on the mirrored "
     "arm, so the two lines are one part built twice."),
    (("P8",), ("3DP_arm15_end_effector_attachment",),
     "Booklet p.9: the end-effector plate below the wrist, one per arm."),
    # Wrist Output, Nylon 12 x2; weight 130.22 g = CAD 130.2 g, 2 occurrences
    # ---- unpriced rows: settled by the booklet ---------------------------
    (("P10",), ("3DP_grip01_base",),
     "Booklet p.13: the gripper body, one per gripper."),  # Gripper Housing, PLA x2
    (("P11",), ("3DP_grip03_rail",),
     "Booklet p.13: the long slide arm with the rack teeth cut along it, two per gripper, which is "
     "this line's 4 and this component's 4 occurrences. The team BOM calls it a rack because the "
     "teeth are part of the arm; the separate Fusion component `double_helix_rack_30teeth_6mm v2` "
     "holds no body."),
    (("P12",), ("3DP_grip05_pinion",),
     "Booklet p.13: the double-helix pinion on the servo, one per gripper."),  # Gear, Nylon 12 x2
    (("P13",), ("3DP_grip02_finger",),
     "Booklet p.13: the curved ribbed finger pad, two per gripper."),  # UMI Fingers, TPU x4
    (("P14",), ("3DP_grip04_apriltag_holder",),
     "Booklet p.13: the flat tag holder, two per gripper."),  # AprilTag Housing, PLA x4
    (("P15",), ("3DP_grip06_apriltag_tile",),
     "QUANTITY CONFLICT: booklet p.13 draws eight tiles on one gripper (six labels, two of which "
     "point at a pair), which is the Fusion count of 16 for two grippers; the team BOM line says 12."),
    (("P16",), ("3DP_cam01_gimbal_mount",),
     "Booklet p.14: the wide tripod base at the foot of the column, one per column."),
    (("P17",), ("3DP_cam02_gimbal_neck",),
     "Booklet p.14: the neck above the lower gimbal actuator, one per column."),
    (("P18",), ("3DP_cam03_gimbal_arm",),
     "Booklet p.14 draws two gimbal arms: P18 (Gimbal Shaft) is the thicker one, bent, ending in the "
     "bolt-circle pad on the actuator face. Of the two Fusion arm components it is the heavier: "
     "`gimbal_arm` is 16.5 g on its own (26.0 g with its child) against 9.5 g for the child."),
    (("P19",), ("3DP_cam04_gimbal_arm_link",),
     "Booklet p.14: P19 (Gimbal Support) is the thinner, flat arm that ends in a plain disc beside "
     "the H5 bearing, which is the lighter Fusion component (`Component92`, 9.5 g)."),
    (("P20", "P21", "P24", "P25"),
     ("3DP_legP01_hip3_cover_a", "3DP_legP02_hip3_cover_b", "3DP_legP03_hip3_cover_c", "3DP_legP04_hip3_cover_d"),
     "Booklet p.6 draws four curved vented covers on one leg, over the hip-1 and the hip-3 motor: "
     "four lines of 2 = 8 pieces, which is the 8 occurrences of the four Fusion `hip3_protection` "
     "components (3, 3, 1, 1, the last pair mirrored). In the 2026-09-19 export those four are one "
     "two-piece design (identical mass and box) placed at four motors, all named `hip_pitch_motor`, "
     "while the booklet's four covers do not all look alike. Whether Hip 1 has a cover of its own, "
     "which line is which cover, and which pair is Hip 1, are UNVERIFIED."),
    (("P22", "P23"), ("3DP_legP05_hip2_cover_a", "3DP_legP06_hip2_cover_b"),
     "Booklet p.6: the two curved covers around the hip-2 motor of one leg, which are the two Fusion "
     "components on `hip_roll_motor` (material `hip2_protection`, 2 occurrences each). Which line is "
     "A and which is B is UNVERIFIED."),
    (("P26", "P27"), ("3DP_legP07_knee_cover_a", "3DP_legP08_knee_cover_b"),
     "Booklet p.6: the two curved covers around the knee motor of one leg, which are the two Fusion "
     "components on `knee_motor` (2 occurrences each). Which line is A and which is B is UNVERIFIED."),
    (("P28",), ("3DP_legP09_shank_cover_a", "3DP_legP10_shank_cover_b"),
     "Booklet p.6 labels P28 twice on one leg: the two long flat straps, one on each side of the "
     "shank, which is this line's 4 pieces over two legs. The Fusion tree carries the pair on the "
     "right leg only (1 occurrence each), so the CAD is short of the booklet, not the team BOM."),
    (("P29", "P30"), ("3DP_legP11_ankle_cover_a", "3DP_legP12_ankle_cover_b"),
     "Booklet p.6: the two curved covers around the ankle-roll motor of one leg, which are the two "
     "Fusion components on `ankle_roll_motor` (material `ANKLE_1_PROTECTION`, 2 occurrences each). "
     "The team BOM calls them Foot Protection Top and Bot; they sit on the ankle, not on the foot. "
     "Which line is Top and which is Bot is UNVERIFIED."),
    (("P31",), ("3DP_leg20_foot_front",),
     "Booklet p.6: the small teardrop cap at the front of the foot, one per leg."),
    # Foot Protection - Front, TPU x2 = Fusion `foot_front`, 2 occurrences
    (("P32",), ("3DP_leg19_sole",),
     "Booklet p.6: the wedge sole under the foot plate, one per leg."),
    # Foot Protection - Sole, TPU x2 = Fusion `symmetric_sole`, 2 occurrences
    (("P33", "P34"), ("3DP_armP07_shoulder_cover_e", "3DP_armP08_shoulder_cover_f"),
     "Booklet p.10: the two curved covers around the shoulder-pitch motor of one arm, which are the "
     "two Fusion components on `shoulder_pitch_protection` (2 occurrences each) once the four smooth "
     "shaft covers of the same page are settled as `P39`. Which line is A and which is B is UNVERIFIED."),
    (("P35", "P36"), ("3DP_armP09_shoulder_yaw_cover_a", "3DP_armP10_shoulder_yaw_cover_b", "3DP_armP11_shoulder_yaw_cover_c"),
     "Booklet p.10 labels P35 twice and P36 twice on one arm: four curved covers, which is 4 pieces "
     "per line over two arms and the 4 occurrences of each Fusion half of the two-piece cover "
     "`shoulder_yaw_protection`, placed twice per arm. Which Fusion half is Front and which is Back "
     "is UNVERIFIED; the booklet draws both P35 at the shoulder end and both P36 at the forearm end, "
     "so the lines may split by joint rather than by half."),
    (("P37", "P38"), ("3DP_armP01_elbow_cover_a", "3DP_armP02_elbow_cover_b"),
     "Booklet p.10: the two curved covers around the elbow motor of one arm, which are the two Fusion "
     "components on `elbow_motor_protection` (2 occurrences each). Which line is A and which is B is "
     "UNVERIFIED."),
    (("P39",), ("3DP_armP03_shoulder_cover_a", "3DP_armP04_shoulder_cover_b",
                "3DP_armP05_shoulder_cover_c", "3DP_armP06_shoulder_cover_d"),
     "Booklet p.10 labels P39 four times on one arm: the smooth flat covers over the roll shafts, "
     "eight for two arms, which is this line's count. They are the four Fusion components on "
     "`shoulder_roll_shaft` and `elbow_shaft` (2 occurrences each, 11 mm thick), and this is the only "
     "team BOM line whose name (Arm Roll Shaft Protection) and count fit them."),
]

# Sheet rows with no CAD match: part_id = team_ref. Empty since the booklet
# settled `P39`.
PRINTED_NO_CAD: dict[str, tuple[str, str, str]] = {}

# Team BOM lines whose piece count the booklet settles against the sheet, so
# the row says which count holds instead of leaving the difference open.
QTY_SETTLED = {"P15"}

# Notes for printed CAD components that no team BOM line covers.
PRINTED_EXTRA_NOTE: dict[str, str] = {
}

# The three filament / powder rows. The team BOM has no line for them, but it
# does carry a price per unit weight per material, which is recorded here.
MATERIAL_ROWS = [
    ("MAT_TPU", "TPU filament (printed parts)", "TPU", "FDM", "34.99"),
    ("MAT_PLA", "PLA filament (printed parts)", "PLA", "FDM", "12.47"),
    ("MAT_SLS_NYLON", "Nylon 12 powder for SLS (printed parts)", "Nylon 12", "SLS", "99.9"),
]


# --------------------------------------------------------------------------- #
# spreadsheet
# --------------------------------------------------------------------------- #
class Sheet:
    """The spreadsheet's part rows, keyed by the `#` column (E0, C21, P20, H1)."""

    def __init__(self, path: Path):
        import openpyxl  # imported here so the module can be read without it

        ws = openpyxl.load_workbook(path, data_only=True)["Sheet1"]
        self.rows: dict[str, dict] = {}
        self.order: list[str] = []
        self.sum_total = self.sum_qty = None
        for cells in ws.iter_rows(min_row=2, values_only=True):
            category, ref, item, link, unit, qty, total = (cells + (None,) * 7)[:7]
            weight, per_weight = cells[8], cells[9]
            if category == "SUM":
                self.sum_total, self.sum_qty = _dec(unit), _dec(qty)
                continue
            if not ref or not item:
                continue
            self.rows[str(ref).strip()] = dict(
                ref=str(ref).strip(), category=str(category).strip(), item=str(item).strip(),
                link=(link or "").strip(), unit=_dec(unit), qty=_dec(qty), total=_dec(total),
                weight=_dec(weight), per_weight=_dec(per_weight))
            self.order.append(str(ref).strip())

    def __getitem__(self, ref: str) -> dict:
        return self.rows[ref]

    def of_category(self, category: str) -> list[dict]:
        return [self.rows[r] for r in self.order if self.rows[r]["category"] == category]


def _dec(value) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _plain(value: Decimal | None) -> str:
    """Decimal -> the digits the CSV carries, without exponent or trailing zeros."""
    if value is None:
        return ""
    text = format(value.normalize(), "f")
    return text


def vendor_of(link: str, seen_unknown: set[str]) -> str:
    if not link:
        return ""
    host = re.sub(r"^https?://", "", link).split("/")[0].lower()
    host = host[4:] if host.startswith("www.") else host
    for domain, name in VENDORS.items():
        if host == domain or host.endswith("." + domain):
            return name
    seen_unknown.add(host)
    return host


def price_note(row: dict, cad: tuple[str, str] | None = None) -> list[str]:
    """The note a row gets for its price and its weight column.

    `cad` is (mass_g, children) of the Fusion component the row maps to, so the
    sheet's weight is checked against the export rather than asserted to match.
    """
    notes = []
    if row["unit"] is None or row["unit"] == 0:
        notes.append(NO_PRICE)
    if row["weight"] is not None:
        grams = row["weight"] * 1000
        notes.append(
            f"Team BOM weight {_plain(row['weight'])} and price per unit weight "
            f"{_plain(row['per_weight'])}; their product is the unit cost. The sheet states no "
            f"unit for the weight (its column is headed `weight (check urdf)`); read as "
            f"kilograms it is {grams:.1f} g, " + weight_check(grams, cad))
    elif row["per_weight"] is not None:
        notes.append(f"Team BOM price per unit weight {_plain(row['per_weight'])}, no weight.")
    return notes


def weight_check(grams: Decimal, cad: tuple[str, str] | None) -> str:
    """How the sheet's weight compares with the Fusion mass of the mapped component."""
    if not cad or not cad[0]:
        return "which no Fusion mass is available to check."
    mass, children = Decimal(cad[0]), int(cad[1] or 0)
    close = abs(grams - mass) <= Decimal("0.15")
    if close and not children:
        return f"which equals the Fusion mass of the component ({mass} g)."
    if close:
        return (f"which equals the Fusion mass of the component with its {children} child "
                f"component(s) ({mass} g).")
    if children:
        return (f"which cannot be checked against the export: the Fusion mass ({mass} g) includes "
                f"{children} child component(s) and the component's own mass is not exported.")
    return f"which does NOT equal the Fusion mass of the component ({mass} g). UNVERIFIED."


def joined(notes: list[str]) -> str:
    """Notes as one sentence stream, each sentence once, in the order given."""
    seen, out = set(), []
    for n in notes:
        n = n.strip()
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return " ".join(out)


def new_row(**kw) -> dict:
    row = {c: "" for c in COLS}
    row.update(kw)
    return row


def costs(row: dict) -> dict:
    """unit_cost_usd / priced_as_of for a spreadsheet row, blank when unpriced."""
    if row["unit"] is None or row["unit"] == 0:
        return dict(unit_cost_usd="", priced_as_of="")
    return dict(unit_cost_usd=_plain(row["unit"]), priced_as_of=PRICED_AS_OF)


# --------------------------------------------------------------------------- #
# builders
# --------------------------------------------------------------------------- #
def build_purchased(sheet: Sheet, unknown_hosts: set[str]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {ACT_FILE: [], EL_FILE: [], CAB_FILE: [], FAS_FILE: []}
    for ref, csv_name, pid, sub, desc, mpn, extra in PURCHASED:
        src = sheet[ref]
        notes = [f"Team BOM {ref}: \"{src['item']}\"."]
        if extra:
            notes.append(extra)
        notes += price_note(src)
        out[csv_name].append(new_row(
            subassembly=sub, **{"class": "off_the_shelf"}, part_id=pid, description=desc, mpn=mpn,
            vendor=vendor_of(src["link"], unknown_hosts), vendor_url=src["link"],
            qty_per_robot=QTY_OVERRIDE.get(ref, _plain(src["qty"])), **costs(src),
            notes=joined(notes), team_ref=ref))
    for ref, csv_name, pid, sub, desc, mpn, qty, note in SITE_PURCHASED:
        # class "consumable": the tables print a dash, not a red TODO, for price and vendor.
        out[csv_name].append(new_row(
            subassembly=sub, **{"class": "consumable"}, part_id=pid, description=desc, mpn=mpn,
            qty_per_robot=qty, notes=note, team_ref=ref))
    return out


def build_cnc(sheet: Sheet) -> list[dict]:
    rows = []
    for ref, pid, extra in CNC_MAP:
        src = sheet[ref]
        notes = [f"Team BOM {ref}: \"{src['item']}\", {_plain(src['qty'])} off."]
        if extra:
            notes.append(extra)
        notes += price_note(src)
        rows.append(new_row(
            subassembly=subassembly_of(pid), **{"class": "machined"}, part_id=pid,
            description=src["item"], qty_per_robot=_plain(src["qty"]), **costs(src),
            process="CNC", notes=joined(notes), team_ref=ref))
    for pid, sub, desc, extra in CNC_EXTRA:
        rows.append(new_row(
            subassembly=sub, **{"class": "machined"}, part_id=pid, description=desc,
            process="CNC", notes=joined([NOT_IN_BOM, extra]), team_ref=""))
    rank = {"leg": 0, "arm": 1, "body": 2}
    rows.sort(key=lambda r: (rank[r["subassembly"]], r["part_id"]))
    return rows


def subassembly_of(part_id: str) -> str:
    for key in ("leg", "arm", "body"):
        if part_id.startswith("CNC_" + key):
            return key
    raise SystemExit("unclassified machined part: " + part_id)


SHEET_MATERIALS = [("Nylon 12", "SLS"), ("TPU", "FDM"), ("PLA", "FDM")]


def sheet_material(item: str) -> tuple[str, str]:
    """Material and process from the 3DP item name's suffix, e.g. `..., TPU`."""
    for needle, process in SHEET_MATERIALS:
        if re.search(r"[,\s]" + re.escape(needle) + r"\s*$", item):
            return needle, process
    return "", ""


def build_printed(sheet: Sheet, tree: dict[str, list[dict]]) -> tuple[list[dict], list[str]]:
    """One row per CAD printed part, then the sheet rows with no CAD part."""
    cad = {pid: (key, sub, desc) for key, pid, sub, desc in PRINTED}
    mapped: dict[str, tuple[tuple[str, ...], str]] = {}
    for refs, pids, note in PRINTED_MAP:
        for pid in pids:
            if pid not in cad:
                raise SystemExit(f"PRINTED_MAP points at {pid}, which gen_printed.PRINTED has no entry for")
            mapped[pid] = (refs, note)

    rows, warnings = [], []
    for key, pid, sub, desc in PRINTED:
        occ = pick(tree, key)
        if not occ:
            warnings.append(f"{pid}: Fusion component `{key}` is not in the tree; row skipped")
            continue
        first = occ[0]
        qty = sum(int(r["qty"]) for r in occ)
        if pid in PRINTED_QTY_OVERRIDE:
            cad_qty, qty = qty, PRINTED_QTY_OVERRIDE[pid]
            override_note = (f"Quantity is the robot's ({qty}), not the model's: the Fusion model places "
                             f"{cad_qty} (right leg only); the team BOM and the other leg covers give both legs.")
        else:
            override_note = ""
        cad_material, cad_process = material_of(first["material"])
        fusion_name = re.sub(r" \(\d+\)$", "", first["fusion_name"])
        cad_note = (f"Fusion component `{fusion_name}`, material `{first['material']}`, "
                    f"{qty} occurrence(s), {first['mass_g'] or '?'} g each in CAD.")

        refs, map_note = mapped.get(pid, ((), ""))
        notes: list[str] = []
        material, process, unit, priced = cad_material, cad_process, "", ""
        if refs:
            src = [sheet[r] for r in refs]
            items = "; ".join(f"{r['ref']} \"{r['item']}\" x{_plain(r['qty'])}" for r in src)
            notes.append(f"Team BOM {items}.")
            if map_note:
                notes.append(map_note)
            sheet_qty = sum((r["qty"] or 0) for r in src)
            if len(mapped_ids(pid)) == 1 and sheet_qty != qty:
                settled = set(refs) <= QTY_SETTLED
                notes.append(f"The team BOM says {_plain(sheet_qty)} pieces, the Fusion model {qty}"
                             + (f"; the booklet shows {qty}." if settled else ". UNVERIFIED."))
            material, process = sheet_material(src[0]["item"])
            if cad_material and material and material.lower() not in cad_material.lower():
                notes.append(f"MATERIAL CONFLICT: the team BOM says {material}, Fusion says "
                             f"`{first['material']}` ({cad_material}). UNVERIFIED.")
            elif not cad_material:
                notes.append(f"Material from the team BOM line only; the Fusion material name "
                             f"`{first['material']}` is not a print material.")
            unit_costs = {_plain(r["unit"]) for r in src if r["unit"]}
            if len(unit_costs) > 1:
                notes.append(f"The team BOM prices its lines differently ({', '.join(sorted(unit_costs))}); "
                             f"no unit cost is written here. UNVERIFIED.")
            elif unit_costs:
                unit, priced = unit_costs.pop(), PRICED_AS_OF
            else:
                notes.append(NO_PRICE)
            for r in src:
                notes += [n for n in price_note(r, (first["mass_g"], first["children"])) if n != NO_PRICE]
        else:
            notes.append(NOT_IN_BOM)
            if pid in PRINTED_EXTRA_NOTE:
                notes.append(PRINTED_EXTRA_NOTE[pid])
        if override_note:
            notes.append(override_note)
        notes.append(cad_note)
        if int(first["children"]):
            notes.append(f"The Fusion component carries {first['children']} child component(s): "
                         f"its CAD mass includes them.")
        rows.append(new_row(
            subassembly=sub, **{"class": "printed"}, part_id=pid, description=desc,
            qty_per_robot=str(qty), unit_cost_usd=unit, priced_as_of=priced,
            material=material, process=process, notes=joined(notes),
            team_ref=", ".join(refs)))

    for ref, (sub, desc, note) in PRINTED_NO_CAD.items():
        src = sheet[ref]
        material, process = sheet_material(src["item"])
        notes = [f"Team BOM {ref}: \"{src['item']}\", {_plain(src['qty'])} off.", note]
        notes += price_note(src)
        rows.append(new_row(
            subassembly=sub, **{"class": "printed"}, part_id=ref, description=desc,
            qty_per_robot=_plain(src["qty"]), **costs(src), material=material, process=process,
            notes=joined(notes), team_ref=ref))

    for pid, desc, material, process, per_weight in MATERIAL_ROWS:
        rows.append(new_row(
            subassembly="printed", **{"class": "consumable"}, part_id=pid, description=desc,
            material=material, process=process, team_ref="",
            notes=(f"The team BOM has no line for the filament or powder itself; it prices the "
                   f"{material} parts at {per_weight} per unit weight (no unit stated). Grade, "
                   f"vendor and quantity are not recorded anywhere in the release.")))
    return rows, warnings


def mapped_ids(part_id: str) -> tuple[str, ...]:
    """The CAD part_ids the same team BOM line(s) as `part_id` cover."""
    for _, pids, _ in PRINTED_MAP:
        if part_id in pids:
            return pids
    return (part_id,)


# --------------------------------------------------------------------------- #
def write(name: str, rows: list[dict]) -> Decimal:
    ids = [r["part_id"] for r in rows]
    assert len(ids) == len(set(ids)), f"{name}: duplicate part_id"
    with open(DATA / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows([{k: (v.strip() if isinstance(v, str) else v) for k, v in r.items()} for r in rows])
    total = sum((Decimal(r["unit_cost_usd"]) * Decimal(r["qty_per_robot"])
                 for r in rows if r["unit_cost_usd"] and r["qty_per_robot"]), Decimal(0))
    unpriced = [r["part_id"] for r in rows if not r["unit_cost_usd"]]
    print(f"{name:24s} rows={len(rows):3d}  unpriced={len(unpriced):3d}  subtotal={total:12.4f}")
    if unpriced:
        print(f"{'':26s}no price: {', '.join(unpriced)}")
    return total


TEAM_MAP = "team-map.csv"
TEAM_MAP_COLS = ["team_ref", "item", "category", "part_id", "qty_team", "qty_cad",
                 "booklet_page", "evidence", "status"]


def cnc_cad_counts(tree: dict[str, list[dict]]) -> dict[str, int]:
    """Fusion occurrence count per `CNC_<module><nn>` stem, over every alias of it."""
    out: dict[str, int] = {}
    for name, rows in tree.items():
        if not name.startswith("CNC_"):
            continue
        stem = "_".join(name.split("_")[:2])
        out[stem] = out.get(stem, 0) + sum(int(r["qty"]) for r in rows)
    return out


def write_team_map(sheet: Sheet, cnc: list[dict], printed: list[dict],
                   tree: dict[str, list[dict]]) -> None:
    """One row per team BOM line: which CAD part it is and what settles that.

    ``part_id`` and ``qty_cad`` are the whole group's where several lines share
    one group of parts (the cover lines), and the evidence says so.
    """
    counts = cnc_cad_counts(tree)
    groups: dict[str, tuple[tuple[str, ...], list[str]]] = {}
    for refs, pids, _ in PRINTED_MAP:
        for ref in refs:
            groups[ref] = (refs, list(pids))

    printed_qty = {r["part_id"]: int(r["qty_per_robot"] or 0) for r in printed}
    purchased = {ref: pid for ref, _, pid, *_ in PURCHASED}
    machined = {ref: pid for ref, pid, _ in CNC_MAP}

    rows = []
    for ref in sheet.order:
        src = sheet[ref]
        page, seen = BOOKLET.get(ref, ("—", "not labelled in the booklet"))
        evidence = [f"Booklet {page}: {seen}." if page != "—" else f"{seen.capitalize()}."]
        pids: list[str] = []
        cad = ""
        if ref in purchased:
            pids = [purchased[ref]]
        elif ref in machined:
            pids = [machined[ref]]
            cad = str(counts.get("_".join(machined[ref].split("_")[:2]), ""))
        elif ref in groups:
            refs, pids = groups[ref]
            cad = str(sum(printed_qty.get(p, 0) for p in pids))
            if len(refs) > 1:
                evidence.append(f"One of {len(refs)} team BOM lines over {len(pids)} CAD parts; "
                                f"`part_id` and `qty_cad` are that group's.")
            elif len(pids) > 1:
                evidence.append(f"This line covers {len(pids)} CAD parts; `qty_cad` is their total.")
        if ref in OPEN:
            evidence.append("OPEN: " + OPEN[ref])
        rows.append(dict(team_ref=ref, item=src["item"], category=src["category"],
                         part_id=" ".join(pids), qty_team=_plain(src["qty"]), qty_cad=cad,
                         booklet_page=page, evidence=joined(evidence),
                         status="open" if ref in OPEN else "settled"))

    for ref, _, pid, _, desc, _, qty, note in SITE_PURCHASED:
        page, seen = BOOKLET.get(ref, ("—", "not labelled in the booklet"))
        rows.append(dict(team_ref=ref, item=desc, category="Electronics", part_id=pid,
                         qty_team=qty, qty_cad="", booklet_page=page,
                         evidence=joined([f"Booklet {page}: {seen}." if page != "—" else "", note]),
                         status="settled"))

    with open(DATA / TEAM_MAP, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=TEAM_MAP_COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    open_rows = [r["team_ref"] for r in rows if r["status"] == "open"]
    print(f"{TEAM_MAP:24s} rows={len(rows):3d}  open={len(open_rows):3d}  "
          f"settled={len(rows) - len(open_rows)}")
    print(f"{'':26s}open: {', '.join(open_rows)}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    xlsx = Path(sys.argv[1]) if len(sys.argv) > 1 else XLSX
    if not xlsx.is_file():
        sys.exit(f"team BOM not found: {xlsx}")
    sheet = Sheet(xlsx)
    tree = load_tree(find_tree(sys.argv[2] if len(sys.argv) > 2 else None))

    unknown_hosts: set[str] = set()
    bought = build_purchased(sheet, unknown_hosts)
    cnc = build_cnc(sheet)
    printed, warnings = build_printed(sheet, tree)

    grand = Decimal(0)
    for name, rows in ((ACT_FILE, bought[ACT_FILE]), (EL_FILE, bought[EL_FILE]),
                       (CAB_FILE, bought[CAB_FILE]), (FAS_FILE, bought[FAS_FILE]),
                       ("cnc-parts.csv", cnc), ("printed-parts.csv", printed)):
        grand += write(name, rows)
    write_team_map(sheet, cnc, printed, tree)

    # Which spreadsheet rows ended up where, and what the arithmetic says.
    used = {r["team_ref"] for rows in (list(bought.values()) + [cnc, printed]) for r in rows} - {""}
    used = {ref.strip() for group in used for ref in group.split(",")}
    unused = [r for r in sheet.order if r not in used]
    sheet_total = sum((sheet[r]["total"] or 0) for r in sheet.order)
    sheet_qty = sum((sheet[r]["qty"] or 0) for r in sheet.order)

    print(f"\nsite subtotal (6 CSVs):      {grand:12.4f}")
    print(f"team BOM, sum of Total Cost: {sheet_total:12.4f}   (its SUM cell: {sheet.sum_total})")
    print(f"team BOM, sum of Quantity:   {sheet_qty:12.0f}   (its SUM cell: {sheet.sum_qty})")
    print(f"difference:                  {grand - sheet_total:12.4f}")
    print(f"\nteam BOM rows: {len(sheet.order)}, used: {len(used)}, not used: {unused or 'none'}")
    if unknown_hosts:
        print(f"vendor name not in VENDORS, host used as the name: {', '.join(sorted(unknown_hosts))}")
    for w in warnings:
        print("WARNING " + w, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
