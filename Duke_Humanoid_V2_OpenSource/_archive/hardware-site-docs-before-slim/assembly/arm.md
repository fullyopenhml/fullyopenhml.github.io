# Arm

One arm: 7 degrees of freedom — shoulder pitch, shoulder roll, shoulder yaw,
elbow, wrist roll, wrist pitch, wrist yaw. Build two. Reach is 0.46 m. The
gripper mounts at the end and is built separately, on [Gripper](gripper.md).

!!! missing "Structure only — do not attempt an arm from this page"
    The step sequence follows the kinematic chain and the parts recorded for
    each joint. Fastener sizes, torques, press fits and the assembly order
    inside each step have never been recorded from a build. Do not attempt an
    arm from this page.

!!! warning "Blocking prerequisite — configure the actuators first"
    Set the CAN ID of all seven actuators **on the bench** and label each one,
    before any of them goes into a housing. The wrist packs three axes into a
    small volume; an actuator whose ID is wrong there is the most expensive one
    on the robot to reach again.
    See [Motor ID and config](../bringup/motor-id-and-config.md).

## The seven joints

Verified from
[`control/humanoid_config.py`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/humanoid_config.py).

| Joint | Actuator | CAN ID, left | CAN ID, right | Bus, left | Bus, right |
| --- | --- | --- | --- | --- | --- |
| `shoulder_1` | RobStride 03 | 10 | 20 | `can22` | `can22` |
| `shoulder_2` | RobStride 06 | 11 | 21 | `can9` | `can21` |
| `shoulder_3` | RobStride 02 | 12 | 22 | `can9` | `can21` |
| `elbow` | RobStride 02 | 13 | 23 | `can9` | `can21` |
| `wrist_1` | RobStride 02 | 14 | 24 | `can9` | `can21` |
| `wrist_2` | RobStride 00 | 15 | 25 | `can9` | `can21` |
| `wrist_3` | RobStride 05 | 16 | 26 | `can9` | `can21` |

!!! danger "The shoulder-pitch actuator is not on the arm's bus"
    `shoulder_1` sits on `can22` — the same bus as the waist and as the *other*
    arm's `shoulder_1` — while the other six joints of the arm sit on `can9`
    (left) or `can21` (right). Two buses therefore enter each shoulder. A
    harness built on the assumption that one arm equals one bus will be wrong,
    and the mistake will not show up until bring-up.

!!! unverified "UNVERIFIED — which numbered joint is pitch, roll and yaw"
    The motor table names the joints `shoulder_1/2/3` and `wrist_1/2/3`; the
    hardware figure in the repository README labels the arm joints, in the same
    order, *shoulder pitch, roll, yaw, elbow, wrist roll, pitch, yaw*. Matching
    by position gives `shoulder_2` = roll and `wrist_1` = roll, `wrist_2` =
    pitch, `wrist_3` = yaw.

    The machined part names agree — `CNC_arm01…04` are all named
    `shoulder_roll_*`, `CNC_arm11_x2_wrist_roll`, `CNC_arm12_x2_wrist_pitch`,
    and the `RS05` coupler part matches `wrist_3`, the arm's only RobStride 05.
    It is still an inference from two documents. **Confirm against the CAD.**
    *Owner: hardware lead.*

### Range of motion

Two sets of numbers exist and they do not agree. The **model limit** is what
the published simulation model
(`simulation/asset/duke_v2/humanoid_v21/humanoid_v21.xml`) enforces. The
**design target** is the range of motion the team set at the design stage.
Neither is a measured mechanical stop (**UNVERIFIED**{ .dh-unverified }).

| Joint | Design target | Model limit, left | Model limit, right |
| --- | --- | --- | --- |
| `shoulder_1` | −105° to +105° | ±180° | ±180° |
| `shoulder_2` | −30° to +90° | −180° to +30° | −30° to +180° |
| `shoulder_3` | −90° to +90° | ±180° | ±180° |
| `elbow` | 0° to +135° | ±125° | ±125° |
| `wrist_1` | −90° to +90° | ±180° | ±180° |
| `wrist_2` | −90° to +90° | ±92° | ±92° |
| `wrist_3` | not given | ±90° | ±90° |

*Source: design targets from the team design log, "Joint Limits and Motors
Torques" (one value per joint, no left/right split); model limits from
`humanoid_v21.xml`.*

!!! unverified "UNVERIFIED — whether the arm's four ±180° joints really reach their modelled range"
    Four joints in each arm are modelled as full ±180° revolutes, against design
    targets of ±90° to ±105°. Whether the hardware actually turns that far, or is
    limited by its own cabling, is exactly the question the checkpoints on this
    page exist to answer. Nothing on this page states whether any arm joint has
    a mechanical hard stop. The team's mechanical design checklist called for
    an end-stop on every DOF ("DOF should have an end-stop to prevent the motor
    from going crazy"); whether any was implemented is
    **UNVERIFIED**{ .dh-unverified }.

    *Owner: hardware lead.*

## Machined parts in this arm

| Part ID | Belongs to |
| --- | --- |
| `CNC_arm01_x2_shoulder_roll_front_bearing` | Shoulder roll |
| `CNC_arm02_x2_shoulder_roll_back_bearing` | Shoulder roll |
| `CNC_arm03_x2_shoulder_roll_output_shaft` | Shoulder roll |
| `CNC_arm04_x4_shoulder_roll_support_shaft` | Shoulder roll |
| `CNC_arm05_x4_RS02_shaft_bearing` | Every RobStride 02 output in the arm |
| `CNC_arm06_x4_RS02_shaft_coupler` | Every RobStride 02 output in the arm |
| `CNC_arm07_x2_elbow_front_bearing` | Elbow |
| `CNC_arm08_x2_elbow_back_bearing` | Elbow |
| `CNC_arm09_x2_elbow_output_shaft` | Elbow |
| `CNC_arm10_x4_r03_back_cover` | Shoulder pitch (the arm's RobStride 03) |
| `CNC_arm11_x2_wrist_roll` | Wrist roll |
| `CNC_arm12_x2_wrist_pitch` | Wrist pitch |
| `CNC_arm13_x2_RS05_shaft_coupler` | Wrist yaw |

Quantities are withheld, and read **TODO**{ .dh-missing } in the step tables,
for the reason given on the [Assembly index](index.md). `CNC_arm05` and `CNC_arm06` are named `_x4` but
each arm has **three** RobStride 02 joints, which is one of the 25 recorded
name-versus-quantity conflicts — see [CNC parts](../bom/cnc-parts.md).

!!! missing "MISSING — the arm has no bearing, shaft, spacer, printed-part or fastener list"
    No bearing, shaft, spacer, printed-part or fastener list exists for the arm.
    Every Parts-needed table below is incomplete by construction. The CAD
    animation below is a visual inventory only: it gives no part IDs, sizes or
    quantities.

    *Owner: hardware lead, from the CAD.*

<figure markdown>
  <video class="dh-clip" autoplay loop muted playsinline preload="metadata" width="1280" height="720"
    poster="../../assets/exploded/arm-poster.webp" aria-label="Exploded view of one arm, shoulder-pitch actuator to wrist"><source src="../../assets/exploded/arm.mp4" type="video/mp4"><a href="../../assets/exploded/arm.mp4">Exploded view of one arm, shoulder-pitch actuator to wrist</a></video>
  <figcaption>Team's unlabelled CAD animation: one complete arm, shoulder-pitch actuator to wrist (no gripper), exploded along the arm; each joint's side plates and bearing rings move out along that joint's axis.</figcaption>
</figure>

> **Figure** <span class="pending-figure">labelled version not produced yet</span> —
> `assets/assembly/arm-exploded.png`: the animation above carries no labels or
> part IDs. Still needed: the same view with every part labelled with its part
> ID and the seven actuators called out with their joint names.

### What the CAD animation shows

- **Seven actuator bodies, in chain order:** a large finned actuator; a lighter
  finned actuator; three smooth cylindrical actuators; a small silver
  disc-shaped actuator; a small flanged cylindrical actuator. Seven matches the
  seven arm joints in `humanoid_config.py` (RobStride 03, 06, 02, 02, 02, 00,
  05), but matching each body to a joint by its appearance is an inference
  (**UNVERIFIED**{ .dh-unverified }).
- **Shoulder roll and elbow are built the same way.** In each, the actuator
  sits in the middle of a yoke of two side plates, and each plate carries a
  thin ring drawn as a bearing, so the joint is supported on both sides of the
  actuator. That fits the machined part names (front and back bearing
  housings, an output shaft, and at the shoulder a support shaft). Which plate
  is which `CNC_armNN` part is **UNVERIFIED**{ .dh-unverified }.
- **The shoulder-pitch actuator starts the arm, but its body sits in the
  torso.** In the torso-frame animation, one large finned actuator sits in the
  round opening of each torso side plate, output face outward. In the arm
  animation, a square X-ribbed adapter bolts to that actuator's output face.
  So in the CAD the actuator body belongs to the torso side plate and the arm
  attaches to its output. The build order is still not recorded (see step 2).
- Also visible: two conical shells (upper-arm and forearm links), a square
  block, a forearm link, the wrist housings, and an end housing with a six-hole
  circular pattern. No labels or part IDs appear anywhere in the animation.

*Source: team exploded-view CAD animations of the arm and the torso frame;
actuator list from `deploy/control/humanoid_config.py`.*

## Sub-assembly A — shoulder

{{ step(1, "Configure and label the seven arm actuators") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 03 | 1 | `shoulder_1` |
| RobStride 06 | 1 | `shoulder_2` |
| RobStride 02 | 3 | `shoulder_3`, `elbow`, `wrist_1` |
| RobStride 00 | 1 | `wrist_2` |
| RobStride 05 | 1 | `wrist_3` |
| Masking tape and marker | As needed | One label per actuator |

</div>

Set each actuator's CAN ID on the bench, one at a time, to the value for the arm
you are building. Write the joint name, the ID **and the bus** on the actuator
body — `shoulder_1` goes on a different bus from the rest of its own arm, and
that is the single easiest thing to get wrong on this robot.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/arm-step-01.png`: the seven actuators laid out in chain order
> and labelled, with the shoulder-pitch actuator visibly marked for its
> different bus.

{{ checkpoint("All seven actuators answer at their assigned IDs, one at a time, and each carries a label with joint name, ID and bus.") }}

{{ step(2, "Build the shoulder-pitch joint") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 03 — ID 10 (left) / 20 (right) | 1 | `shoulder_1`, on `can22` |
| `CNC_arm10_x4_r03_back_cover` | **TODO**{ .dh-missing } | RobStride 03 back cover |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

This joint bolts to the torso rather than to the rest of the arm. In the team
CAD the actuator **body** sits in the round opening of the torso side plate,
output face outward, and the arm starts with a square adapter bolted to that
output face. *Source: team exploded-view CAD animations of the torso frame and
the arm.* The CAD does not say whether the actuator is fitted to the arm here
or to the torso in [Final integration](final-integration.md), so decide before
you build.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/arm-step-02.png`: shoulder-pitch actuator and its back cover,
> with the torso mounting face called out.

!!! missing "MISSING — shoulder pitch: build order at the torso side plate; fasteners, torque, threadlocker"
    The CAD answers *which* side is the torso interface: the actuator body sits
    in the torso side plate and the arm bolts to its output. Still missing:
    whether the actuator goes into the side plate before or after the arm is
    built, and whether the arm is built outward from it or joined to it last.
    Fasteners, torque, and whether this interface takes threadlocker: unknown.
    *Owner: hardware lead.*

{{ checkpoint("The shoulder-pitch output rotates freely by hand through its full travel with no axial play, and the back cover is seated with no gap.") }}

{{ step(3, "Build the shoulder-roll joint") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 06 — ID 11 (left) / 21 (right) | 1 | `shoulder_2`, the arm's only RobStride 06 |
| `CNC_arm03_x2_shoulder_roll_output_shaft` | **TODO**{ .dh-missing } | Output shaft |
| `CNC_arm04_x4_shoulder_roll_support_shaft` | **TODO**{ .dh-missing } | Support shaft |
| `CNC_arm01_x2_shoulder_roll_front_bearing` | **TODO**{ .dh-missing } | Front bearing housing |
| `CNC_arm02_x2_shoulder_roll_back_bearing` | **TODO**{ .dh-missing } | Back bearing housing |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

Like the hip roll, this joint runs on an output shaft and a separate support
shaft, carried at both ends. Concentricity before tightening is the whole
difficulty.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/arm-step-03.png`: shoulder-roll actuator, both shafts and both
> bearing housings exploded along the roll axis.

!!! missing "MISSING — shoulder-roll joint: bearings, press fits, alignment, preload, fasteners, torque, threadlocker"
    Bearing sizes and which fits are pressed. Alignment method and preload.
    Fasteners, torque, threadlocker: unknown.
    *Owner: hardware lead, from a photographed build.*

{{ checkpoint("The roll axis turns freely end to end with equal drag in both directions and no axial play at either bearing.") }}

{{ step(4, "Build the shoulder-yaw joint") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 02 — ID 12 (left) / 22 (right) | 1 | `shoulder_3` |
| `CNC_arm05_x4_RS02_shaft_bearing` | **TODO**{ .dh-missing } | RobStride 02 shaft bearing |
| `CNC_arm06_x4_RS02_shaft_coupler` | **TODO**{ .dh-missing } | RobStride 02 output coupler |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/arm-step-04.png`: shoulder-yaw actuator with its shaft bearing
> and coupler, joined to the shoulder-roll output.

!!! missing "MISSING — shoulder-yaw joint: fasteners, torque, bearing fit, shoulder cable routing order"
    Fasteners, torque, threadlocker, bearing fit. Whether the shoulder cabling
    must be routed through this joint before it is closed — the shoulder moves
    in three axes and carries the cabling for four joints below it.
    *Owner: hardware lead.*

{{ checkpoint("All three shoulder joints move independently through their full travel with no interference, and nothing is pulled taut at any combination of the three.") }}

## Sub-assembly B — elbow

{{ step(5, "Build the elbow joint") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 02 — ID 13 (left) / 23 (right) | 1 | `elbow` |
| `CNC_arm09_x2_elbow_output_shaft` | **TODO**{ .dh-missing } | Elbow output shaft |
| `CNC_arm07_x2_elbow_front_bearing` | **TODO**{ .dh-missing } | Elbow front bearing housing |
| `CNC_arm08_x2_elbow_back_bearing` | **TODO**{ .dh-missing } | Elbow back bearing housing |
| `CNC_arm05_x4_RS02_shaft_bearing` | **TODO**{ .dh-missing } | RobStride 02 shaft bearing |
| `CNC_arm06_x4_RS02_shaft_coupler` | **TODO**{ .dh-missing } | RobStride 02 output coupler |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/arm-step-05.png`: elbow actuator, output shaft and both
> bearing housings, exploded along the elbow axis.

!!! missing "MISSING — elbow joint: bearings, fits, assembly order, fasteners, torque, threadlocker"
    Bearing sizes and fits, assembly order, fasteners, torque, threadlocker.
    *Owner: hardware lead.*

{{ checkpoint("The elbow rotates freely through its full travel with no axial play, and does not contact the upper arm at either extreme.") }}

## Sub-assembly C — wrist

The wrist is three axes in the smallest volume on the robot, and it is where
cable service loops are hardest to fit. Build it on the bench and check each
axis as it goes on; a wrist that binds after all three are assembled is very
hard to diagnose.

{{ step(6, "Build the wrist-roll joint") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 02 — ID 14 (left) / 24 (right) | 1 | `wrist_1` |
| `CNC_arm11_x2_wrist_roll` | **TODO**{ .dh-missing } | Wrist-roll body |
| `CNC_arm05_x4_RS02_shaft_bearing` | **TODO**{ .dh-missing } | RobStride 02 shaft bearing |
| `CNC_arm06_x4_RS02_shaft_coupler` | **TODO**{ .dh-missing } | RobStride 02 output coupler |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/arm-step-06.png`: wrist-roll body and actuator joined to the
> elbow output.

!!! missing "MISSING — wrist-roll joint: fasteners, torque, threadlocker, bearing fit, cable pass-through"
    Fasteners, torque, threadlocker, bearing fit, cable pass-through.
    *Owner: hardware lead.*

{{ checkpoint("Wrist roll turns freely through its full travel with no axial play.") }}

{{ step(7, "Build the wrist-pitch joint") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 00 — ID 15 (left) / 25 (right) | 1 | `wrist_2`, the arm's only RobStride 00 |
| `CNC_arm12_x2_wrist_pitch` | **TODO**{ .dh-missing } | Wrist-pitch body |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

The RobStride 00 is the smallest actuator on the robot. Check its fastener sizes
against the rest of the arm rather than assuming they match.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/arm-step-07.png`: wrist-pitch body and its actuator joined to
> the wrist-roll output.

!!! missing "MISSING — wrist-pitch joint: fasteners, torque, threadlocker, bearing fit"
    Fasteners, torque, threadlocker, bearing fit.
    *Owner: hardware lead.*

{{ checkpoint("Wrist pitch moves through its full travel with no binding, and does not collide with the wrist-roll body at either extreme.") }}

{{ step(8, "Build the wrist-yaw joint and the end-effector interface") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 05 — ID 16 (left) / 26 (right) | 1 | `wrist_3`, the arm's only RobStride 05 |
| `CNC_arm13_x2_RS05_shaft_coupler` | **TODO**{ .dh-missing } | RobStride 05 output coupler |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

The wrist-yaw output carries the gripper. The gripper brings its own mounting
flange — a machined disc that is part of the gripper assembly, not of the arm —
so this step ends at the interface, and the gripper goes on during
[Final integration](final-integration.md).

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/arm-step-08.png`: wrist-yaw actuator and coupler, with the
> gripper mounting face called out and dimensioned.

!!! missing "MISSING — wrist-to-gripper interface, and wrist-yaw fasteners, torque, threadlocker"
    The wrist-to-gripper interface: bolt circle, pilot diameter, orientation
    keying, and the electrical pass-through for the gripper servo cable. This
    interface is the one place the arm and the end effector have to agree, and
    it is undocumented in both directions.
    Fasteners, torque, threadlocker: unknown.
    *Owner: hardware lead.*

{{ checkpoint("Wrist yaw turns freely through its full travel, and all three wrist axes move in combination without contact.") }}

## Sub-assembly D — close out

{{ step(9, "Route the arm harness and close the arm") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| Arm harness branch | 1 | **TODO**{ .dh-missing } — not yet designed |
| Gripper servo cable | 1 | Runs the length of the arm to the wrist |
| Cable ties / anchors | As needed | **TODO**{ .dh-missing } — retention scheme not documented |

</div>

Two buses enter the shoulder: `can22` for `shoulder_1` only, and `can9` (left)
or `can21` (right) for the other six joints. The gripper servo is **not** on
CAN — it is a Feetech bus servo on a serial link from its own driver board in
the torso, so a third cable runs the length of the arm. See
[Harness fabrication](../electrical/harness-fabrication.md).

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/arm-step-09.png`: the finished arm with harness routed and
> retained, every crossing of a moving joint marked, and the three cable groups
> distinguishable.

!!! missing "MISSING — arm harness: gauge, connectors, lengths, service loops, cabling at ±180° joints"
    Wire gauge, connectors, branch lengths, service loops at the shoulder and
    the wrist, and how cabling survives ±180° at four joints. If the cabling
    limits a joint to less than its modelled range, that limit must be
    published here and enforced in software.
    *Owner: hardware lead + electrical.*

{{ checkpoint("All seven joints move through their full travel, one at a time and in combination, with the harness installed. No cable is stretched, rubbed or pinched at any extreme, and the measured travel of each joint is recorded against the modelled limit.") }}

## Mirroring

!!! missing "MISSING — which arm parts are handed and which are common"
    Which arm parts are handed and which are common. What is known:

    - The machined part names carry no `left` / `right` distinction.
    - In the published model the two arms are not identical: `shoulder_2` has
      mirrored asymmetric limits and the left and right chains carry different
      orientations.
    - The two arms differ electrically for certain: `can9` versus `can21`, and
      different CAN IDs throughout.

    Whether any *part* differs is unresolved. State it part by part before this
    page is used. *Owner: hardware lead, from the CAD.*

## Figures this page needs

None of these figures exists yet **TODO**{ .dh-missing }.

| File | Step | What it must show |
| --- | --- | --- |
| `assets/assembly/arm-exploded.png` | page header | Whole arm exploded along the chain, all parts labelled (an unlabelled CAD animation is already on the page) |
| `assets/assembly/arm-step-01.png` | 1 | Seven actuators in chain order, labelled, shoulder pitch marked for its bus |
| `assets/assembly/arm-step-02.png` | 2 | Shoulder-pitch actuator and back cover, torso face called out |
| `assets/assembly/arm-step-03.png` | 3 | Shoulder-roll actuator, both shafts, both bearing housings |
| `assets/assembly/arm-step-04.png` | 4 | Shoulder-yaw actuator, bearing and coupler on the roll output |
| `assets/assembly/arm-step-05.png` | 5 | Elbow actuator, output shaft, both bearing housings |
| `assets/assembly/arm-step-06.png` | 6 | Wrist-roll body and actuator on the elbow output |
| `assets/assembly/arm-step-07.png` | 7 | Wrist-pitch body and actuator on the wrist-roll output |
| `assets/assembly/arm-step-08.png` | 8 | Wrist-yaw actuator and coupler, gripper mounting face dimensioned |
| `assets/assembly/arm-step-09.png` | 9 | Finished arm with harness routed, three cable groups distinguishable |
