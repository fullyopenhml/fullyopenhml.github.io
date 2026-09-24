# Structure and manufacturing

Why the structure is machined aluminium, the design rules every machined part was checked against, and what the first-article fit check found.

Nothing on this page is a build instruction. To have parts made, follow the
[CNC guide](../fabrication/cnc-guide.md) and
[Incoming inspection](../fabrication/incoming-inspection.md).

## Material

**AS-BUILT.** Aluminium is the main structural material, chosen in the design log
as "the best lightweight and affordable material".

**CONSIDERED — NOT USED** as a decision: the grade. The log weighs the two grades
JLCPCB CNC offered and does not pick one.

| Property (as written in the log) | 6061 | 7075 |
| --- | --- | --- |
| Tensile strength | ~276 MPa | ~503 MPa ("80% stronger than 6061") |
| Young's modulus | ~68.9 GPa | ~71.7 GPa ("similar") |
| Density | 2.7 g/cc | 2.81 g/cc ("marginally heavier") |
| Corrosion | – | less resistant ("irrelevant") |
| Cost | – | about 20% more for the same part, "potentially cheaper if parts can be designed lighter" |

*Source: team design log, "Material Choice".*

!!! unverified "UNVERIFIED — aluminium grade of the machined parts (6061 or 7075)"
    The design log never decides between 6061 and 7075. Two hints in the
    published repo, neither of them a statement about every CNC part, point to
    6061: a comment in `simulation/asset/duke_v2/humanoid_v21/humanoid_v21_creation_v3.py`
    reads "hard-anodized 6061", and the gripper flange's material in
    `parallel_gripper_fusion_info.py` is "Aluminum 6061". Temper, finish and
    per-part material are not recorded.

    *Owner: hardware lead.*

!!! unverified "UNVERIFIED — JLCPCB CNC as the machining vendor"
    The material study quotes JLCPCB CNC's two grade options, so the team was
    pricing parts there. The log never says JLCPCB machined the reference robot.

    *Owner: hardware lead.*

## CNC design rules

**AS-BUILT** (the rules the team applied to its machined parts).

Team CNC design rules: walls ≥ 1 mm (structural walls ≥ 4 mm); blind holes end in a standard cone; screws need ≥ 4 mm of usable thread, 6 mm preferred; no sharp internal corners; chamfers preferred over fillets; tolerance 0.03 mm on radius, 0.06 mm on diameter, 0.03 mm on length; safety factor ≥ 3 under normal load. Whether the tolerances are ± or a total band is not stated (**UNVERIFIED**{ .dh-unverified }), and the SF ≥ 3 column is empty for all 32 parts. *Source: team design log, CNC checklist and CNC Part List.*

The same checklist sizes the screw bosses: for M4 screws, "outer radius of the
base should be 8.6mm, and 0.2mm chamfer"; for M3, 7 mm with a 0.2 mm chamfer.
Set against standard button-head sizes, 8.6 mm and 7 mm read more like diameters
than radii (**UNVERIFIED**{ .dh-unverified }).

**Review status.** The team's CNC Part List carries one check column per rule.
23 of the 32 parts (arm01–arm10, leg02, leg03, leg08–leg18) are ticked on all six
geometry and tolerance checks. Nine parts (body01–body04, leg01, leg04–leg07) have
no check recorded.
*Source: team CNC Part List, check columns.*

!!! unverified "UNVERIFIED — the SF ≥ 3 target was never recorded as met"
    The design rules set a safety factor of at least 3 under normal load, but
    the "SF >= 3 under normal load" column is empty for all 32 parts. No part
    has a recorded structural check, and the body plates and hip-roll parts
    were not recorded as reviewed at all.

    *Owner: hardware lead.*

!!! unverified "UNVERIFIED — whether the pre-machining review notes were acted on"
    The review notes in the CNC Part List name the fit-critical interfaces.
    Whether each note was addressed before machining is not recorded, so they
    are not the final geometry. They are a useful list of what to measure first.

    - RS03_shaft_coupler (leg02): "certain diameters have 0.03mm tolerance instead of 0.06mm".
    - RS03_shaft_bearing_retainer (leg03): the mating feature with the motor needs a tolerance; chamfers preferred over fillets.
    - knee_front_bearing_retainer (leg08): chamfer on the bearing OD area; tolerance on the circular areas that meet the motor and the 03 shaft; "also change motor screw base to 4mm".
    - knee_back (leg09): chamfers in several places; tolerance on the interface with the 03 shaft.
    - lower_leg_output_shank (leg10): circular pattern missing on the 04-motor side; needs a fillet or chamfer on the 03 side.
    - lower_leg_support_shank (leg11): question on top/bottom symmetry.
    - ankle_pitch_front (leg13): question on the clearance fit for the 06 motor; diameters toleranced at 0.06 mm, to be double-checked.
    - ankle_pitch_back (leg14): as leg13, and check the screw-hole sizing.

    *Owner: hardware lead.*

## Hardware standard

**AS-BUILT** (design rule; not a counted schedule).

Team hardware standard: Torx button-head M4x12 (McMaster-Carr 90991A123) and M3x12 (90991A115) only; main bearing 50x65x7 mm; threadlocker Loctite 222. The first-article check contradicts 'M4/M3 only': 'Motor04 Shaft NEEDS m5 holes, but the cad has m4 holes. Same in the knee motor' (**UNVERIFIED**{ .dh-unverified } which the released CAD has).

The main bearing was bought on Amazon; McMaster-Carr 6656K229 was used for the
CAD model. The ankle thrust bearing is left blank in the log ("Thrust bearing for
ankle: _______"). Quantities, locations and torque values are not in the design
log; the build-side list is [Fasteners and hardware](../bom/fasteners-and-hardware.md).
*Source: team design log, "Hardware Choice".*

!!! unverified "UNVERIFIED — M4 or M5 holes on the Motor04 (knee) shaft in the released CAD"
    The design rule says M4x12 and M3x12 only, but the first-article check found
    the Motor04 shaft and the knee motor need M5 holes where the CAD had M4.
    Which the released CAD has now is not recorded.

    *Owner: hardware lead.*

<figure markdown>
  ![CAD render of an actuator and its output shaft part](../assets/photos/tolerance-cad-m4-vs-m5.webp){ loading=lazy }
  <figcaption>"Motor04 Shaft NEEDS m5 holes, but the cad has m4 holes. Same in the knee motor." Whether the released CAD has M5 is <strong class="dh-unverified">UNVERIFIED</strong>.</figcaption>
</figure>

## Part labelling convention

**AS-BUILT** (the team's convention; the site uses its own prefixes). A part ID
reads: kind of part, then body region with its number, then count, then an
optional description.

| Field | Values |
| --- | --- |
| Kind | CNC (CNC part), ELEC (electronic part, non-actuator), MTR (actuator/motor), HWR (hardware: nuts, screws, bearings, tape), DIY (in-house: 3D printing, moulding) |
| Region and number | legxx, armxx, bodyxx (for example leg01, arm01, body01) |
| Count | xn (for example x1, x2, x3) |
| Side (optional) | L or R |

The log's example is `CNC_leg02_x7` followed by the description
`RS03_shaft_coupler`.
*Source: team design log, "Labeling Conventions".*

!!! unverified "UNVERIFIED — labelling convention: internal contradiction and site departures"
    The log's example calls the RS03 shaft part "repeated 5 times in the leg"
    but names it `CNC_leg02_x7`; in the CNC Part List, leg02 RS03_shaft_coupler
    has count 7 and leg03 RS03_shaft_bearing_retainer has count 5. This site
    uses its own prefixes (`EL_`, `ACT_`, `CBL_`) instead of ELEC/MTR/HWR/DIY and
    drops the count from the part ID. The owner should say which scheme the
    release keeps.

    *Owner: BOM owner.*

## Joint pattern: actuator in a two-plate yoke

**AS-BUILT** (from the team's CAD animation). In the arm, the shoulder-roll
joint and the elbow are built the same way: the actuator sits in the middle of a
yoke of two side plates, each plate carries a ring drawn as a bearing, and so
the joint is supported on both sides of the actuator. The machined-part names
fit this (front and back bearing retainers plus an output shaft for each joint).
Which plate is which `CNC_armNN` part is **UNVERIFIED**{ .dh-unverified }.
*Source: team exploded-view animation of the arm; team CNC Part List names.*

## First-article fit check, February 2025

**AS-BUILT** (history of the reference build). On 2025-02-27 the team checked the
first V2 CNC parts with a hand-held digital caliper and recorded the result in a
short deck. It found four parts that needed rework and one CAD thread error:

- waist motor shaft and knee motor shaft: filed down;
- motor04 shaft: hole enlarged for fit;
- Motor04 shaft: filed smaller;
- 03 motor shaft bearing retainer above the knee: enlarged, recorded as a
  "Design error";
- Motor04 shaft and knee motor: M5 holes needed where the CAD has M4 (above).

The deck gives no nominal dimensions, tolerances or accept/reject limits; every
value in it is a reading with no target. The photos are on
[Incoming inspection](../fabrication/incoming-inspection.md).
*Source: team deck "Tolerance Check V2 CNC" (title slide dated 2/27/2025).*

## End stops

**DESIGN GOAL (not as-built).** The team's mechanical design checklist has one
item: "DOF should have an end-stop to prevent the motor from going crazy".
*Source: team design log, "mechanical design checklist".*

!!! unverified "UNVERIFIED — whether any joint has a mechanical end stop"
    The checklist called for an end stop on every degree of freedom. No record
    shows that end stops were implemented on any joint of the built robot.

    *Owner: hardware lead.*

## 3D-print materials looked at

**CONSIDERED — NOT USED** (as far as the records show). The log lists three
links under "3d print material" and does not say which, if any, was used:
[TCPoly Flex ICE9](https://tcpoly.com/flex-ice9/),
[Bambu Lab PPA-CF](https://us.store.bambulab.com/collections/fiber-reinforced/products/ppa-cf)
and a [Clough42 video](https://www.youtube.com/watch?v=OWH_N9PmjeY). The
validated filament for printed parts is a question for the
[Printing guide](../fabrication/printing-guide.md).
*Source: team design log, "3d print material".*
