# Torque targets and mass budget

How the leg torque targets were set from human gait data and from other legged robots, and the mass budget estimated before the build.

Nothing on this page is a build instruction. For the actuators that were
actually bought, see [Actuators](../bom/actuators.md).

## Method: scale human joint moments by body mass

**DESIGN GOAL (not as-built).** The team grounded the V2 leg torque targets in
human gait data, normalised by body mass (N·m per kg), and then checked them
against the joint torques of other legged robots.
*Source: team design log, "design reference"; team "Human leg torque reference" table.*

### Human leg torque reference

**DESIGN GOAL (not as-built).** The team's reference table, with each row
attributed to the paper the design log derives it from.

| Condition | Hip (N·m/kg) | Knee (N·m/kg) | Ankle (N·m/kg) | Derived from (per design log text) | Team note |
| --- | ---: | ---: | ---: | --- | --- |
| walking (natural) | 4.6 | 5.6 | 3.2 | Frigo 1996 | "using second to biggest values" **UNVERIFIED**{ .dh-unverified } (see below) |
| jogging | 1.4 | 3.5 | 2.2 | Winter 1983: hip 100 N·m, knee 250 N·m, ankle 160 N·m for a 72 kg subject | approximate figure read |
| running | 3.5 | 4.1 | 3.5 | Belli 2002: hip 240 N·m, knee 280 N·m, ankle 240 N·m for a 68 kg subject | approximate figure read |
| walking | 2 | 2 | 1.5 | Simonsen 1997, plot of all 7 subjects | "approximately read from figure and averaged" |

*Source: team "Human leg torque reference" table (rows 2–5); team design log, "design reference".*

The team's table has its source column shifted by one paper on two rows: it
cites the 2002 running paper on the jogging row and the 1996 walking paper on the
running row. The design log text derives the jogging values from Winter 1983 and
the running values from Belli 2002, so this page follows the log text.

!!! unverified "UNVERIFIED — the Frigo 1996 row is variability ratios, not joint moments"
    The log records "normalized moment hip: 5 Nm/kg, knee: 10 Nm/kg, ankle:
    3.5 Nm/kg" from Frigo 1996, and the table uses the second-largest values,
    4.6 / 5.6 / 3.2. Both sets come from the paper's Table 2, which reports the
    inter- and intra-subject ratio of variability (RV) of angles and moments.
    RV is a normalised standard deviation, not a peak moment, and the paper
    normalises moments by body weight × 100. Do not use this row as
    N·m/kg peak moments until it is re-derived from the paper's moment curves.

    *Owner: hardware lead.*

!!! unverified "UNVERIFIED — Winter 1983 and Belli 2002 values are approximate figure reads"
    The newton-metre values behind the jogging and running rows were read by eye
    from the papers' figures and rounded. For Winter 1983, 72 kg is the paper's
    mean subject mass (72.4 kg, 11 subjects), while the plotted curves are for
    one 79 kg subject, and the plotted knee peak is visibly lower than 250 N·m.
    For Belli 2002, the paper is not in the team records, so the 68 kg subject
    mass could not be checked. Treat both rows as approximate.

    *Owner: hardware lead.*

**References** (title, journal, DOI):

- "Moment-Angle Relationship at Lower Limb Joints during Human Walking at
  Different Velocities", *Journal of Electromyography and Kinesiology* 6(3):177–190
  (1996). DOI 10.1016/S1050-6411(96)00030-5 (computed from the publisher's
  article ID, **UNVERIFIED**{ .dh-unverified }).
- "Moments of force and mechanical power in jogging", *Journal of Biomechanics*
  16(1):91–97 (1983). DOI 10.1016/0021-9290(83)90050-7 (computed from the
  publisher's article ID, **UNVERIFIED**{ .dh-unverified }).
- "Moment and power of lower limb joints in running", *International Journal of
  Sports Medicine* 23(2):136–141 (2002).
  DOI [10.1055/s-2002-20136](https://doi.org/10.1055/s-2002-20136).
- "Mechanisms contributing to different joint moments observed during human
  walking", *Scandinavian Journal of Medicine & Science in Sports* 7:1–13 (1997).
  DOI [10.1111/j.1600-0838.1997.tb00110.x](https://doi.org/10.1111/j.1600-0838.1997.tb00110.x).

### Other legged robots

**DESIGN GOAL (not as-built).** The benchmark table the V2 goal was set against.
Torques are peak joint torques in N·m. Column names are the team's; the source
never defines HA, so it is left unexpanded.

| Robot | Leg length (m) | Leg DoF | Mass (kg) | HAA | HA | HFE | KFE | AFE | AR | Team comment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| MIT | 0.28 | 5 | 24 | 34 | 34 | 68 | 136 | 52 | – | |
| Berkeley | 0.4 | 6 | 16 | 63 | 63 | 63 | 81 | 45 | 10 | mass w/o arm |
| Unitree G1 | 0.6 | 6 | 35 | 88 | 88 | 88 | 120 | 40 | 40 | "all values from URDF"; see note |
| arXiv 2408.01056 | 0.5 | 5 | 20 | 40 | 40 | 150 | 150 | 12 | – | can hop on one leg |
| HECTOR | 0.22 | 5 | 16 | 34 | 34 | 34 | 52 | 34 | – | modified from Unitree A1 |
| ARTEMIS | 0.7 | 5 | 37 | 90 | 90 | 250 | 250 | 28 | – | leg length estimated |
| Duke Humanoid V1 | 0.5 | 5 | 30 | 238 | 238 | 264 | 238 | 132 | – | |
| Fourier GR1 | 0.75 | 6 | 55 | 66 | 48 | 225 | 225 | 30 | 15 | |
| Boodter T1 (sic) | 0.5 | 6 | 30 | | | | 130 | | | estimated leg length, mass; 23 dof |
| COMAN | 0.44 | 6 | 32 | | | 55 | 40 | | | SEA joint |
| iCub | 0.2 | 6 | 24 | | | 40 | 40 | | | |
| **V2 design goal** | **0.3** | **6** | **24** | **60** | **60** | **60** | **80** | **45** | **20** | mass w/o arm, w 1DOF lower back |

*Source: team "V2 humanoid actuator design spec" table (all rows). Blank cells are blank in the source.*

**Unitree G1 knee.** The team's own comment on this row reads "according to urdf
the max KFE is 139 Nm, according to website it is 120 Nm", yet the table cell
holds 120. Both values are given here; the table is not corrected.

!!! unverified "UNVERIFIED — robot name 'Boodter T1' in the benchmark table"
    The row is kept as the source spells it. It is probably the Booster T1
    humanoid, but the team has not confirmed which robot the row describes, and
    its values are marked "estimated" in the source.

    *Owner: hardware lead.*

### The V2 design goal

**DESIGN GOAL (not as-built).** Leg length 0.3 m, 6 leg DoF, mass 24 kg ("mass
w/o arm, w 1DOF lower back"). Peak joint torque targets: HAA 60, HA 60, HFE 60,
KFE 80, AFE 45, AR 20 N·m.
*Source: team actuator design spec, row "V2 DESGIN GOAL" (sic).*

The robot as built has a 0.39 m leg and weighs 36 kg with arms
([Full specifications](../reference/full-specifications.md)).

**V1 to V2, at design-goal level.** V1 had a 0.5 m leg, a 5-DoF leg with no ankle
roll, 30 kg, and HAA 238, HA 238, HFE 264, KFE 238, AFE 132 N·m. The V2 goal is a
0.3 m, 6-DoF leg (adding AR at 20 N·m), 24 kg without arms, and torques of
60 (HAA, HA, HFE), 80 (KFE) and 45 (AFE) N·m. This compares design targets only, not the physical changes between
the two robots.
*Source: team actuator design spec, rows "dukeHumanoid V1" and "V2 DESGIN GOAL".*

## Targets against the chosen actuators

**AS-BUILT** actuator map; comparison **computed**. The joint-to-actuator
allocation in the design log names the same models as the code for every joint
it fills in; the log leaves wrist_3 blank.

> As-built joint-to-model map (deploy/control/humanoid_config.py): waist R03; hip_1, hip_2, hip_3 R03; knee R04; ankle_1 R03; ankle_2 R06; shoulder_1 R03; shoulder_2 R06; shoulder_3 R02; elbow R02; wrist_1 R02; wrist_2 R00; wrist_3 R05; cam_yaw/cam_pitch (4) R05 — 31 actuators.

The comparison below sets the V2 goal against two different ratings. The design
log quotes the 10 s overload torque; the code's `MAX_TORQUE` is the peak rating.
The team's Motor spec table lists both.

| Joint | Target (design goal) | As-built model | 10 s overload | Peak | Computed result |
| --- | --- | --- | ---: | ---: | --- |
| hip_1, hip_2, hip_3 | HAA / HA / HFE 60 N·m | RS03 | 55 N·m | 60 N·m | peak meets the target exactly; 10 s rating is 5 N·m under it |
| knee | KFE 80 N·m | RS04 | 120 N·m | 120 N·m | 1.5 × the target |
| ankle_1 | AFE 45 N·m (if ankle_1 is pitch) | RS03 | 55 N·m | 60 N·m | above the target **UNVERIFIED**{ .dh-unverified } |
| ankle_2 | AR 20 N·m (if ankle_2 is roll) | RS06 | 27 N·m | 36 N·m | above the target **UNVERIFIED**{ .dh-unverified } |

*Source: computed from the team design log, "Joint Limits and Motors Torques"; the team actuator design spec, row "V2 DESGIN GOAL"; `MAX_TORQUE` in `deploy/control/hardware_bindings/motor/py_motor.py`.*

!!! unverified "UNVERIFIED — the ankle rows assume ankle_1 is pitch and ankle_2 is roll"
    The ankle half of the comparison depends on which ankle joint is pitch and
    which is roll. The team's April 2025 simulation plots label ankle_1 "ankle
    pitch" and ankle_2 "ankle roll" (see
    [Actuator sizing in simulation](actuator-sizing-simulation.md)), but that is
    the simulation model, not the CAD or the built robot. Confirm on the robot
    before relying on the ankle rows.

    *Owner: hardware lead.*

## Design range of motion against the model limits

**DESIGN GOAL (not as-built)** for the first column; the second column is the
published simulation model. Neither is a measured mechanical stop. Degrees.

| Joint | Design-stage ROM (design log) | Model limit (`humanoid_v21.xml`) |
| --- | --- | --- |
| waist | [-90, 90] | ±90 |
| hip_1 | [-105, 105] | ±105 |
| hip_2 | [-20 (inwards), 105 (outwards)] | L [-105, 30] / R [-30, 105] |
| hip_3 | [-45, 45] | ±90 |
| knee | [-105, 105] | ±130 |
| ankle_1 | [-45, 45] | ±50 |
| ankle_2 | [-45, 45] | ±60 |
| shoulder_1 | [-105, 105] | ±180 |
| shoulder_2 | [-30, 90] | L [-180, 30] / R [-30, 180] |
| shoulder_3 | [-90, 90] | ±180 |
| elbow | [0, 135] | ±125 |
| wrist_1 | [-90, 90] | ±180 |
| wrist_2 | [-90, 90] | ±92 |
| wrist_3 | blank | ±90 |

*Source: team design log, "Joint Limits and Motors Torques"; `simulation/asset/duke_v2/humanoid_v21/humanoid_v21.xml` in the published repo.*

!!! unverified "UNVERIFIED — design ROM and model limits disagree on 11 of 13 joints"
    Only waist (±90) and hip_1 (±105) agree between the design log and the
    published model. Neither source is a measured hard stop on the built robot,
    so neither can be used as a mechanical limit. The design log's hip_2 range
    is labelled "-20 (inwards), 105 (outwards)", which describes an
    inward/outward motion and so is one more sign that hip_2 is the hip roll
    joint; it does not settle hip_1, hip_3, ankle_1 or ankle_2.

    *Owner: hardware lead.*

## Mass budget (estimate, pre-build)

**DESIGN GOAL (not as-built).** The team's mass estimate before the build. Not
measured.

| Item | Estimate |
| --- | ---: |
| Hip (3 DoF), per leg | 4 kg |
| Knee and thigh, per leg | 2 kg |
| Ankle (2 DoF) and calf, per leg | 2.25 kg |
| Foot, per leg | 0.25 kg |
| **Each leg** | **8.5 kg** |
| **Both legs** | **17 kg** |
| Waist (1 DoF) | 1 kg |
| Body: electronics and wires | 1 kg |
| Body: structures | 2 kg |
| Body: battery | 2.2 kg |
| Body: Jetson (**SUPERSEDED**: the robot carries a MINISFORUM X1-470 mini PC) | 0.75 kg |
| **Body, as stated** | **7 kg** |
| **Subtotal without arms** | **24 kg** |
| Shoulder (3 DoF), per arm | 2 kg |
| Forearm (4 DoF), per arm | 2 kg |
| End-effector, per arm | 1 kg |
| **Each arm** | **5 kg** |
| **Both arms** | **10 kg** |
| **Estimated total with arms** | **34 kg** |

*Source: team design log, "Estimated mass".*

The log also estimates the actuators in one arm as "1x RS03 + 1x RS06 + 3x RS02
+ 2x RS00 = 0.88 + 0.62 + 0.41x3 + 0.31x2 = 3.4 kg".
**SUPERSEDED:** the "2x RS00" per arm; the as-built arm has one R00 (wrist_2) and
one R05 (wrist_3).

Computed from the table: the four body items add to 5.95 kg (6.95 kg with the
waist) against the stated 7 kg, and the 34 kg estimate is 2 kg under the 36 kg
the finished robot weighs. A measured mass breakdown by subassembly is not in the
records; it is tracked on [Full specifications](../reference/full-specifications.md).

## Knee and leg references

**CONSIDERED — NOT USED.** The design log files three robots under "knee
reference" and related headings, as references only. It does not say what V2
took from any of them. The as-built robot is quasi-direct-drive RobStride at
every joint; none of these designs (cable drives, harmonic drives, knee springs)
is on it.

- "A Reconfigurable Leg for Walking Robots" (2021), IEEE Xplore document 9667211:
  knee-forward and knee-backward leg configurations with a knee spring.
- "Design of Humanoid JAXON3-P" (2019), IEEE Xplore document 9035049 (IROS):
  cable-driven hip, knee and ankle.
- ergoCub humanoid, arXiv 2410.12685: ankle-roll joint with a harmonic drive and
  optical and magnetic encoders.

*Source: team design log, "knee reference", "Design of Humanoid JAXON3-P", "ergoCub humanoid".*
