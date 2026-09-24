# Leg

One leg: 6 degrees of freedom — hip pitch, hip roll, hip yaw, knee, ankle pitch,
ankle roll. Build two. The leg carries the machine's whole mass and is the
subassembly where a press fit done wrong is most expensive to correct.

!!! missing "Structure only — do not attempt a leg from this page"
    The step sequence below follows the kinematic chain and the parts recorded
    for each joint. The *content* of each step — fastener sizes, torques,
    press fits, assembly order within a step — has not been written, because it
    has never been recorded from a build. Do not attempt a leg from this page.

!!! warning "Blocking prerequisite — configure the actuators first"
    Set the CAN ID of all six actuators **on the bench**, before any of them
    goes into a housing. Once an actuator is inside the leg its ID label is not
    visible and its ID cannot be changed without taking the leg apart.
    Label each actuator with its joint name and ID in tape as you go.
    See [Motor ID and config](../bringup/motor-id-and-config.md).

## The six joints

Verified from
[`control/humanoid_config.py`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/humanoid_config.py).
All six actuators of one leg share one CAN bus.

| Joint | Actuator | CAN ID, left | CAN ID, right | Bus (L / R) |
| --- | --- | --- | --- | --- |
| `hip_1` | RobStride 03 | 31 | 41 | `can24` / `can23` |
| `hip_2` | RobStride 03 | 32 | 42 | `can24` / `can23` |
| `hip_3` | RobStride 03 | 33 | 43 | `can24` / `can23` |
| `knee` | RobStride 04 | 34 | 44 | `can24` / `can23` |
| `ankle_1` | RobStride 03 | 35 | 45 | `can24` / `can23` |
| `ankle_2` | RobStride 06 | 36 | 46 | `can24` / `can23` |

!!! unverified "UNVERIFIED — which numbered joint is pitch, roll and yaw"
    The motor table names the joints `hip_1/2/3` and `ankle_1/2`; the hardware
    figure in the repository README labels the leg joints, in the same order,
    *hip pitch, hip roll, hip yaw, knee, ankle pitch, ankle roll*. Matching the
    two by position gives `hip_1` = pitch, `hip_2` = roll, `hip_3` = yaw,
    `ankle_1` = pitch, `ankle_2` = roll.

    Two independent signs agree with that reading — the machined parts named
    `ankle_roll_*` sit next to the part named `RS06_shaft_bearing_retainer`, and
    `ankle_2` is the leg's only RobStride 06; and the model's `hip_2` limit is
    asymmetric and mirrored left to right, as a roll limit would be.

    Two more signs from the team's own records:

    - **`hip_2` = roll.** The design log gives the `hip_2` range as
      "-20 (inwards), 105 (outwards)", an inward/outward motion.
      *Source: team design log, "Joint Limits and Motors Torques".*
    - **`ankle_1` = pitch, `ankle_2` = roll.** The team's April 2025 simulation
      plots title leg joint indices 5 and 11 "ankle pitch" and 6 and 12 "ankle
      roll", which are `ankle_1` and `ankle_2` in the `humanoid_config.py`
      order; the log's ankle-roll experiments change only the second ankle
      motor. This comes from the April 2025 simulation model, not from the CAD.
      *Source: team gait-debugging screen recordings, April 2025; team design
      log, simulation section.*

    The ankles are now supported by the team's own labels. The hips are not:
    the same plots title them only "hip 0/1/2", so `hip_1` = pitch and
    `hip_3` = yaw are still an inference from position.
    **Confirm the hips against the CAD before this page is used.**
    *Owner: hardware lead.*

### Range of motion

Two sets of numbers exist and they do not agree. The **model limit** is what
the published simulation model
(`simulation/asset/duke_v2/humanoid_v21/humanoid_v21.xml`) enforces. The
**design target** is the range of motion the team set at the design stage.
Neither is a measured mechanical hard stop (**UNVERIFIED**{ .dh-unverified }),
and a leg that reaches exactly these angles by hand has not been verified
against anything.

| Joint | Design target | Model limit, left | Model limit, right |
| --- | --- | --- | --- |
| `hip_1` | −105° to +105° | ±105° | ±105° |
| `hip_2` | −20° (inwards) to +105° (outwards) | −105° to +30° | −30° to +105° |
| `hip_3` | −45° to +45° | ±90° | ±90° |
| `knee` | −105° to +105° | ±130° | ±130° |
| `ankle_1` | −45° to +45° | ±50° | ±50° |
| `ankle_2` | −45° to +45° | ±60° | ±60° |

*Source: design targets from the team design log, "Joint Limits and Motors
Torques" (one value per joint, no left/right split); model limits from
`humanoid_v21.xml`. Only `hip_1` (and the waist) agree.*

!!! missing "MISSING — mechanical limits"
    Whether each joint has a mechanical hard stop, where it is, and how the
    mechanical limit relates to the commanded limit above. A robot whose
    software limit is wider than its mechanical limit will drive a joint into
    its own stop under load. The team's mechanical design checklist called for
    an end-stop on every DOF ("DOF should have an end-stop to prevent the motor
    from going crazy"); whether any was implemented is
    **UNVERIFIED**{ .dh-unverified }. *Owner: hardware lead.*

## Machined parts in this leg

Recorded in the internal machining sheet. Quantities are withheld, and read
**TODO**{ .dh-missing } in the step tables, for the reason given on the
[Assembly index](index.md#how-to-read-the-parts-tables).

| Part ID | Belongs to |
| --- | --- |
| `CNC_leg01_x2_hip_center_back` | Hip |
| `CNC_leg02_x7_RS03_shaft_coupler` | Every RobStride 03 output in the leg |
| `CNC_leg03_x5_RS03_shaft_bearing_retainer` | Every RobStride 03 output in the leg |
| `CNC_leg04_x2_hip_roll_front_bearing_retainer` | Hip roll |
| `CNC_leg05_x2_hip_roll_back_bearing_retainer` | Hip roll |
| `CNC_leg06_x2_hip_roll_output_shaft` | Hip roll |
| `CNC_leg07_x2_hip_roll_support_shaft` | Hip roll |
| `CNC_leg08_x2_knee_front_bearing_retainer` | Knee |
| `CNC_leg09_x2_knee_motor_back_cover` | Knee |
| `CNC_leg10_x2_knee_output_shank` | Knee / shank |
| `CNC_leg11_x2_knee_support_shank` | Knee / shank |
| `CNC_leg12_x4_lower_leg_bearing` | Shank |
| `CNC_leg13_x2_ankle_pitch_front` | Ankle pitch |
| `CNC_leg14_x2_ankle_pitch_back` | Ankle pitch |
| `CNC_leg15_x2_RS06_shaft_bearing_retainer` | Ankle roll |
| `CNC_leg16_x2_ankle_roll_output_shaft` | Ankle roll |
| `CNC_leg17_x2_ankle_roll_support_shaft` | Ankle roll |
| `CNC_leg18_x2_foot_plate` | Foot |

!!! unverified "Two of these rows are known to be wrong"
    - `CNC_leg02_x7_RS03_shaft_coupler` appears **twice** in the sheet with
      different prices and different quantities. Which row is current is
      unknown. The team's own CNC part list carries it **once**, with a count
      of **7** per robot; the site's parts data sums the two quoted lots to
      **8**. **UNVERIFIED**{ .dh-unverified } which count is right.
      *Source: team design log, CNC Part List.*
    - The sheet also carries 22 rows in an older numbering — `08_hip_1_back_shaft_x2`,
      `13_knee_front_shaft_x2`, `15_ankle_cap_x4` and similar — which look like a
      superseded single-leg test rig, and several of which appear to describe the
      same hardware as the `CNC_legNN` rows above. **Do not order both sets.**
      Resolving this is tracked on [CNC parts](../bom/cnc-parts.md).
    *Owner: hardware lead.*

!!! missing "MISSING — the leg has no printed-part, bearing, shaft, spacer or fastener list"
    There is no printed part, bearing, shaft, spacer or fastener list for the leg at
    all yet. The steps below therefore name machined parts and actuators only, and
    every step's Parts-needed table is incomplete by construction. The CAD
    animations below are a visual inventory only: they give no part IDs, sizes
    or quantities.

    *Owner: hardware lead, from the CAD.*

### The RobStride 03 mounting interface

Four of the six leg actuators are RobStride 03s, so most leg parts meet this
interface. From the vendor's dimension drawing, in words:

- **Housing face:** 8 × M4 tapped holes, 8 mm deep, equally spaced on a
  Ø98 mm circle.
- **Output face:** 6 × M4 tapped holes, 6 mm deep (blind), plus 3 × Ø4 mm pin
  holes, 7 mm deep (blind), and a Ø70 mm pilot protruding 2.5 mm.

**Screws must not go deeper than the housing thread depth.** The RobStride 02,
03 and 04 manuals all say this. Check every screw length against the thickness
of the part it clamps and the thread depths above.

*Source: RobStride 03 user manual, §1.1 dimension drawing (available from the
vendor, [robstride.com](https://www.robstride.com/products/robStride03)); the
team filed the same drawing in its design log. The drawing is not reproduced
here.*

### Fit-critical notes from the design review

The team's CNC part list carries review notes on these leg parts. Treat them as
the features to measure at [Incoming inspection](../fabrication/incoming-inspection.md).
Whether each was addressed before the parts were made is
**UNVERIFIED**{ .dh-unverified }.

| Part | Team review note |
| --- | --- |
| `CNC_leg03` (RS03 shaft bearing retainer) | "mating feature with motor needs tolerance, could benefit from chamfers instead of fillets" |
| `CNC_leg08` (knee front bearing retainer) | "could benefit from a chamfer on the bearing OD area, needs tolerancing on circular areas that interface with motor and the 03shaft, also change motor screw base to 4mm" |
| `CNC_leg09` (team list: knee_back) | "could benefit from chamfers on multiple location, and tolerance on the interface with the 03shaft" |
| `CNC_leg10` (team list: lower_leg_output_shank) | "missing circular patter on 04motor, also needs fillet/chamfer on 03 side" |
| `CNC_leg11` (team list: lower_leg_support_shank) | "question on top/down symmetry" |
| `CNC_leg13` (ankle pitch front) | "question on clearance fit for 06 motor" |
| `CNC_leg14` (ankle pitch back) | "same as part 13, also check screw hole sizing" |

*Source: team design log, CNC Part List, note column.*

## What the CAD animations show

<figure markdown>
  <video class="dh-clip" autoplay loop muted playsinline preload="metadata" width="1280" height="720"
    poster="../../assets/exploded/leg-poster.webp" aria-label="Exploded view of one leg hanging from the pelvis block"><source src="../../assets/exploded/leg.mp4" type="video/mp4"><a href="../../assets/exploded/leg.mp4">Exploded view of one leg hanging from the pelvis block</a></video>
  <figcaption>Team's unlabelled CAD animation: one leg below the assembled pelvis block, exploded downward: hip yaw, knee, the two shank links, ankle pitch, ankle roll and the foot plate.</figcaption>
</figure>

> **Figure** <span class="pending-figure">labelled version not produced yet</span> —
> `assets/assembly/leg-exploded.png`: the animation above carries no labels or
> part IDs. Still needed: one complete leg exploded along the kinematic chain,
> every part labelled with its part ID, the six actuators called out with their
> joint names.

<figure markdown>
  <video class="dh-clip" autoplay loop muted playsinline preload="metadata" width="1280" height="720"
    poster="../../assets/exploded/hip-assembly-poster.webp" aria-label="Exploded view of the pelvis block with the waist and four hip actuators"><source src="../../assets/exploded/hip-assembly.mp4" type="video/mp4"><a href="../../assets/exploded/hip-assembly.mp4">Exploded view of the pelvis block with the waist and four hip actuators</a></video>
  <figcaption>Team's unlabelled CAD animation: the pelvis block. The waist actuator lifts off with its flange, ring and coupler; the four hip actuators (two per side) move out along their axes.</figcaption>
</figure>

- **The pelvis block** holds five finned actuators. The top one stands
  vertically with its driver board facing up: it is the waist actuator (the
  same actuator sits in the torso bottom plate in the torso-frame animation).
  The other four sit two per side. By count this matches the waist plus the
  left and right `hip_1` and `hip_2`, all RobStride 03: 1 + 2 × 2 = 5
  (computed).
- **Below the pelvis block**, the leg explodes downward in this order: a
  vertical finned actuator (hip yaw) between two ear brackets; a star-shaped
  flange, a thin ring and a square coupler; the largest actuator in the leg
  (knee) with a round front housing and a star-shaped back plate; two separate
  shank links running from knee to ankle; a finned actuator with its driver
  board exposed (ankle pitch); a shorter, wider finned actuator (ankle roll)
  with a star plate, a ring and an ear bracket; and a flat rectangular foot
  plate with a pocket grid and two rectangular windows. Four actuators below
  the pelvis block matches `hip_3`, `knee`, `ankle_1`, `ankle_2` (RobStride 03,
  04, 03, 06) as an inference. Neither animation carries a label or part ID.

*Source: team exploded-view CAD animations of the leg and the pelvis block;
actuator list from `deploy/control/humanoid_config.py`.*

!!! unverified "UNVERIFIED — whether hip pitch and hip roll are built into the leg or into the pelvis block"
    This page builds hip pitch, hip roll and hip yaw inside each leg (steps
    2–4), and [Final integration](final-integration.md) then attaches the leg to
    the pelvis. The team's CAD animations group things differently: the waist
    actuator and **both legs'** first two hip actuators form one pelvis block,
    and the leg animation treats that whole block as the top of the leg, with
    hip yaw as the first joint below it. Which subassembly `hip_1` and `hip_2`
    belong to, and where the leg-to-pelvis joint actually is, is not settled.
    The steps below are left as written until the build order is confirmed.
    *Owner: hardware lead.*

## Sub-assembly A — hip

{{ step(1, "Configure and label the six leg actuators") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 03 | 4 | `hip_1`, `hip_2`, `hip_3`, `ankle_1` |
| RobStride 04 | 1 | `knee` |
| RobStride 06 | 1 | `ankle_2` |
| Masking tape and marker | As needed | One label per actuator |

</div>

Set each actuator's CAN ID on the bench, one at a time, to the value in the
table above for the leg you are building. Write the joint name and the ID on
the actuator body before putting it down. Do not connect two un-configured
actuators to the same bus at once — they ship with the same default ID.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/leg-step-01.png`: the six actuators laid out and labelled,
> with a USB-CAN adapter connected to one of them on the bench.

{{ checkpoint("All six actuators answer on the bus at their assigned IDs, one at a time, and each one carries a physical label with its joint name and ID.") }}

{{ step(2, "Build the hip-pitch joint") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 03 — ID 31 (left) / 41 (right) | 1 | `hip_1` |
| `CNC_leg01_x2_hip_center_back` | **TODO**{ .dh-missing } | Hip centre, back |
| `CNC_leg02_x7_RS03_shaft_coupler` | **TODO**{ .dh-missing } | RobStride 03 output coupler |
| `CNC_leg03_x5_RS03_shaft_bearing_retainer` | **TODO**{ .dh-missing } | RobStride 03 shaft bearing retainer |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/leg-step-02.png`: the hip-pitch actuator, its coupler and its
> bearing retainer, exploded along the output axis; only these parts highlighted.

!!! missing "MISSING — hip-pitch joint: assembly order, press fits, bearings, fasteners, torque, threadlocker"
    Assembly order within the joint, and which fits are pressed.
    Bearing sizes and whether they are supplied pressed into a retainer.
    Fasteners: size, count, head type, tightening pattern.
    Torque: no N·m value exists for this interface.
    Threadlocker: whether this interface takes it.
    *Owner: hardware lead, from a photographed build.*

{{ checkpoint("The hip-pitch output rotates freely by hand through its full travel, with no detectable axial play and no change in drag through the rotation.") }}

{{ step(3, "Build the hip-roll joint onto the hip") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 03 — ID 32 (left) / 42 (right) | 1 | `hip_2` |
| `CNC_leg06_x2_hip_roll_output_shaft` | **TODO**{ .dh-missing } | Hip-roll output shaft |
| `CNC_leg07_x2_hip_roll_support_shaft` | **TODO**{ .dh-missing } | Hip-roll support shaft |
| `CNC_leg04_x2_hip_roll_front_bearing_retainer` | **TODO**{ .dh-missing } | Front bearing retainer |
| `CNC_leg05_x2_hip_roll_back_bearing_retainer` | **TODO**{ .dh-missing } | Back bearing retainer |
| `CNC_leg02_x7_RS03_shaft_coupler` | **TODO**{ .dh-missing } | RobStride 03 output coupler |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

The hip roll is the only leg joint with both an output shaft and a separate
support shaft, so it is carried on bearings at both ends. Getting the two
retainers concentric before anything is tightened is the whole difficulty of
this step.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/leg-step-03.png`: hip-roll actuator, output shaft, support
> shaft and both bearing retainers exploded along the roll axis.

!!! missing "MISSING — hip-roll joint: bearings, fits, alignment, preload, fasteners, torque, threadlocker"
    Which bearings, and which fits are pressed and which are slip.
    Whether the two retainers are aligned with a fixture or by feel, and how
    preload is set.
    Fasteners: size, count, head type, tightening pattern.
    Torque: no N·m value exists for this interface.
    Threadlocker grade and where it is applied.
    *Owner: hardware lead, from a photographed build.*

{{ checkpoint("The roll axis turns freely end to end with no binding at any angle, no axial play at either bearing, and the same drag in both directions.") }}

{{ step(4, "Build the hip-yaw joint") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 03 — ID 33 (left) / 43 (right) | 1 | `hip_3` |
| `CNC_leg02_x7_RS03_shaft_coupler` | **TODO**{ .dh-missing } | RobStride 03 output coupler |
| `CNC_leg03_x5_RS03_shaft_bearing_retainer` | **TODO**{ .dh-missing } | RobStride 03 shaft bearing retainer |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

!!! missing "MISSING — hip yaw: no machined part is named for it; fasteners, torque, threadlocker"
    No machined part in the sheet is named for hip yaw. Either the yaw joint is
    built from the shared `RS03` coupler and retainer parts only, or a part is
    missing from the list. Resolve before ordering.

    Visual evidence for the first option: under the hip-yaw actuator, the leg
    CAD animation shows the same star-shaped flange, thin ring and square
    coupler that sit under the waist actuator in the pelvis-block animation.
    Part IDs are not visible, so this is **UNVERIFIED**{ .dh-unverified }.
    Fasteners, torque, threadlocker: unknown.
    *Owner: hardware lead.*

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/leg-step-04.png`: hip-yaw actuator joined to the hip-roll
> output, showing how the yaw axis is oriented relative to the roll axis.

{{ checkpoint("The three hip joints move independently through their full travel with no interference between them and no cable pulled taut at any combination of angles.") }}

## Sub-assembly B — knee and shank

{{ step(5, "Build the knee joint") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 04 — ID 34 (left) / 44 (right) | 1 | `knee`, the leg's only RobStride 04 |
| `CNC_leg08_x2_knee_front_bearing_retainer` | **TODO**{ .dh-missing } | Knee front bearing retainer |
| `CNC_leg09_x2_knee_motor_back_cover` | **TODO**{ .dh-missing } | Knee motor back cover |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/leg-step-05.png`: knee actuator with its front bearing
> retainer and back cover, exploded along the knee axis.

!!! missing "MISSING — knee joint: bearing fit, fasteners, torque, threadlocker, role of the back cover"
    Bearing size and fit. Fastener size, count and pattern. Torque.
    Threadlocker. Whether the back cover is structural or a guard.
    *Owner: hardware lead, from a photographed build.*

!!! unverified "UNVERIFIED — M5 or M4 holes on the Motor04 shaft part"
    The team's first-article fit check recorded: "Motor04 Shaft NEEDS m5 holes,
    but the cad has m4 holes. Same in the knee motor." The RobStride 04 is the
    knee actuator. This also contradicts the team's "M4x12 and M3x12 only"
    screw standard (see [Tools](tools.md)). Separately, the CNC part list note
    on `CNC_leg08` asks to "change motor screw base to 4mm". Whether the
    released CAD has M5 or M4 here is unknown: check the holes on the part you
    receive before choosing screws.
    *Source: team CNC tolerance-check slides, February 2025; team design log,
    CNC Part List.*
    *Owner: hardware lead.*

{{ checkpoint("The knee rotates freely through its full travel with no axial play, and the back cover is seated with no gap.") }}

{{ step(6, "Join the shank to the knee") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| `CNC_leg10_x2_knee_output_shank` | **TODO**{ .dh-missing } | Shank, driven side |
| `CNC_leg11_x2_knee_support_shank` | **TODO**{ .dh-missing } | Shank, support side |
| `CNC_leg12_x4_lower_leg_bearing` | **TODO**{ .dh-missing } | Lower-leg bearing |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

The shank is two parts, one on the driven side of the knee and one on the
support side. Both must be on before the leg can carry load. The team CAD
confirms the two-part shank: a flat plate link with round ends on one side and
a pocketed truss link on the other, both running from knee to ankle. Which of
them is `CNC_leg10` and which is `CNC_leg11` is **UNVERIFIED**{ .dh-unverified }.
*Source: team exploded-view CAD animation of the leg.*

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/leg-step-06.png`: both shank halves and the lower-leg bearing
> going onto the knee, with the actuator cable route through the shank visible.

!!! missing "MISSING — shank: whether ankle cabling must be routed first; fasteners, torque, bearing fit"
    Whether the actuator cabling for the ankle joints must be routed through the
    shank **before** it is closed. If so this step blocks, and the harness
    branch has to be fabricated first — see
    [Harness fabrication](../electrical/harness-fabrication.md).
    Fasteners, torque, threadlocker, bearing fit: unknown.
    *Owner: hardware lead.*

{{ checkpoint("Both shank halves are on, the knee still rotates freely through its full travel, and the ankle cabling is inside the shank and free to move.") }}

## Sub-assembly C — ankle and foot

{{ step(7, "Build the ankle-pitch joint") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 03 — ID 35 (left) / 45 (right) | 1 | `ankle_1` |
| `CNC_leg13_x2_ankle_pitch_front` | **TODO**{ .dh-missing } | Ankle pitch, front |
| `CNC_leg14_x2_ankle_pitch_back` | **TODO**{ .dh-missing } | Ankle pitch, back |
| `CNC_leg02_x7_RS03_shaft_coupler` | **TODO**{ .dh-missing } | RobStride 03 output coupler |
| `CNC_leg03_x5_RS03_shaft_bearing_retainer` | **TODO**{ .dh-missing } | RobStride 03 shaft bearing retainer |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/leg-step-07.png`: the ankle-pitch front and back parts closing
> around the actuator, exploded along the pitch axis.

!!! missing "MISSING — ankle-pitch joint: assembly order, fasteners, torque, threadlocker, bearing fits"
    Assembly order of front and back around the actuator. Fasteners, torque,
    threadlocker, bearing fits. *Owner: hardware lead.*

{{ checkpoint("Ankle pitch rotates freely through its full travel with no axial play and no interference with the shank at either extreme.") }}

{{ step(8, "Build the ankle-roll joint") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 06 — ID 36 (left) / 46 (right) | 1 | `ankle_2`, the leg's only RobStride 06 |
| `CNC_leg16_x2_ankle_roll_output_shaft` | **TODO**{ .dh-missing } | Ankle-roll output shaft |
| `CNC_leg17_x2_ankle_roll_support_shaft` | **TODO**{ .dh-missing } | Ankle-roll support shaft |
| `CNC_leg15_x2_RS06_shaft_bearing_retainer` | **TODO**{ .dh-missing } | RobStride 06 shaft bearing retainer |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

Like the hip roll, this joint is carried on an output shaft and a support shaft,
so both ends must be concentric before anything is tightened.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/leg-step-08.png`: ankle-roll actuator, output shaft, support
> shaft and retainer, exploded along the roll axis.

!!! missing "MISSING — ankle-roll joint: bearings, fits, alignment, preload, fasteners, torque, threadlocker"
    Bearing sizes and fits, alignment method, preload. Fasteners, torque,
    threadlocker. *Owner: hardware lead.*

{{ checkpoint("Ankle roll turns freely end to end, ankle pitch and roll do not interfere at any combination of angles, and there is no axial play at either bearing.") }}

{{ step(9, "Fit the foot plate") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| `CNC_leg18_x2_foot_plate` | **TODO**{ .dh-missing } | Foot plate |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

!!! missing "MISSING — foot sole or pad, and foot-plate fasteners, torque, threadlocker"
    Whether the foot carries a compliant sole, a pad or a printed cover, and
    what material it is. Nothing in the parts list names one, and a bare
    machined aluminium foot on a hard floor is a different machine to walk than
    one with a sole. The leg CAD animation draws no sole or pad: the foot plate
    is the lowest part. That is only an absence in the animation, not proof
    that the built robot has no sole. Fasteners, torque, threadlocker: unknown.
    *Owner: hardware lead.*

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/leg-step-09.png`: foot plate mounted to the ankle-roll output,
> viewed from underneath.

{{ checkpoint("The foot plate is square to the ankle-roll axis and sits flat on a flat surface when both ankle joints are at their zero positions.") }}

## Sub-assembly D — close out

{{ step(10, "Route the leg harness and close the leg") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| Leg harness branch | 1 | **TODO**{ .dh-missing } — not yet designed, see [Harness fabrication](../electrical/harness-fabrication.md) |
| Cable ties / anchors | As needed | **TODO**{ .dh-missing } — retention scheme not documented |

</div>

All six actuators of one leg sit on **one** CAN bus — `can24` for the left leg,
`can23` for the right — so the leg harness is a single daisy chain plus power.
It leaves the leg at the hip and joins the torso harness during
[Final integration](final-integration.md).

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/leg-step-10.png`: the finished leg with the harness routed and
> retained, showing every point where a cable crosses a moving joint.

!!! missing "MISSING — leg harness: gauge, connectors, lengths, service loops, retention"
    The whole harness: wire gauge, connector choice, branch lengths, service
    loops at each joint, and how each cable is retained.
    *Owner: hardware lead + electrical.*

{{ checkpoint("Every one of the six joints moves through its full travel, one at a time and in combination, with the harness installed, and no cable is stretched, rubbed or pinched at any extreme. Nothing rattles when the leg is shaken by hand.") }}

## Mirroring

!!! missing "MISSING — which leg parts are handed and which are common"
    Which leg parts are handed and which are common. Two things are known and
    neither is sufficient:

    - The machined part names carry no `left` / `right` distinction, and the
      quantities are recorded as one number for the robot, which is consistent
      with either handed or common parts.
    - In the published model the two legs are **not** identical: `hip_2` has
      mirrored asymmetric limits, and the left and right bodies carry different
      orientations. That is geometry, not necessarily different parts.

    Building two identical legs when one should have been mirrored is a
    predictable and expensive mistake, so this must be stated explicitly, part
    by part, before the page is usable. *Owner: hardware lead, from the CAD.*

## Figures this page needs

None of these figures exists yet **TODO**{ .dh-missing }.

| File | Step | What it must show |
| --- | --- | --- |
| `assets/assembly/leg-exploded.png` | page header | Whole leg exploded along the chain, all parts labelled (an unlabelled CAD animation is already on the page) |
| `assets/assembly/leg-step-01.png` | 1 | Six actuators laid out, labelled, one on the bench adapter |
| `assets/assembly/leg-step-02.png` | 2 | Hip-pitch actuator, coupler, bearing retainer |
| `assets/assembly/leg-step-03.png` | 3 | Hip-roll actuator, both shafts, both retainers |
| `assets/assembly/leg-step-04.png` | 4 | Hip-yaw actuator joined to hip roll, axes visible |
| `assets/assembly/leg-step-05.png` | 5 | Knee actuator, front retainer, back cover |
| `assets/assembly/leg-step-06.png` | 6 | Both shank halves and the lower-leg bearing, cable route visible |
| `assets/assembly/leg-step-07.png` | 7 | Ankle-pitch front and back around the actuator |
| `assets/assembly/leg-step-08.png` | 8 | Ankle-roll actuator, output and support shafts, retainer |
| `assets/assembly/leg-step-09.png` | 9 | Foot plate from underneath |
| `assets/assembly/leg-step-10.png` | 10 | Finished leg with harness routed and retained |
