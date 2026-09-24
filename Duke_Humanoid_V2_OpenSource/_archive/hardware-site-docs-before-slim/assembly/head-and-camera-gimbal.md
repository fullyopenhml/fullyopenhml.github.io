# Head and camera gimbal

The module this robot exists to demonstrate: two RGB-D cameras, each on its own
independently actuated 2-DoF yaw–pitch gimbal, so the machine can look at two
separated things at once instead of pointing one fixed head at a compromise
between them. Everything else on this robot is a competent humanoid. This part
is the contribution.

Build **two identical columns**. They are not handed: the right column is the
left column *rotated 180° about the vertical*, using the same parts.

<figure markdown>
  <video class="dh-clip" autoplay loop muted playsinline preload="metadata" width="800" height="800" poster="../../assets/images/hardware_close_front_back-poster.webp" aria-label="The two camera modules on the reference robot, each aiming at a different target">
    <source src="../../assets/images/hardware_close_front_back.mp4" type="video/mp4">
    <a href="../../assets/images/hardware_close_front_back.mp4">The two camera modules on the reference robot, each aiming at a different target</a>
  </video>
  <figcaption markdown="span">
    The finished modules on the reference robot, aiming independently. A
    photograph of a working machine is not an assembly figure — it shows what
    the built result looks like and nothing about how it goes together. The
    renders this page needs are listed in the
    [image manifest](../assets/MANIFEST.md).
  </figcaption>
</figure>

!!! missing "Structure only — do not attempt a column from this page"
    The mounting geometry below is real and comes from a CAD parse. The
    *assembly procedure* — fastener sizes, torques, the order the parts go
    together, how the camera cable survives the yaw axis — has never been
    recorded. Do not attempt a column from this page.

!!! warning "Blocking prerequisite — configure the four actuators first"
    All four gimbal joints sit on one bus, `can25`, and the IDs are not
    contiguous with anything else. Set and label them on the bench.
    See [Motor ID and config](../bringup/motor-id-and-config.md).

## The four joints

Verified from
[`control/humanoid_config.py`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/humanoid_config.py).

| Joint | Actuator | CAN ID | Bus |
| --- | --- | --- | --- |
| `cam_yaw_right` | RobStride 05 | 5 | `can25` |
| `cam_pitch_right` | RobStride 05 | 6 | `can25` |
| `cam_yaw_left` | RobStride 05 | 7 | `can25` |
| `cam_pitch_left` | RobStride 05 | 8 | `can25` |

!!! note "The gimbals are RobStride, not servos"
    The parts list contains two Feetech HL-3915 servos, and it is a natural
    guess that they drive the gimbals. They do not: the Feetech servos are the
    two [grippers](gripper.md), one per hand, on a serial bus. The motor table
    above assigns all four camera joints to RobStride 05 actuators, and the
    actuator count in the parts list agrees exactly — six RobStride 05 in total,
    four of them here and one in each wrist.

## Mounting geometry

These numbers are parsed from the CAD (`HeadCameraV2.step`, Fusion 360 AP214
export, millimetres) by the project's own extraction script, recorded in
`simulation/asset/duke_v2/head_cam/PositionDeter/`, and cross-checked against
the published MuJoCo model. They are geometry from the design, **not**
measurements from a built robot.

Reference frame **P**: origin at the centre of the top plate's central large
hole, on the plate's **top face**; +Z vertically up; +X and +Y along the plate's
own axes.

| Quantity | Value |
| --- | --- |
| Top plate (`CNC_body03_x1_top_plate`) | 130 (X) × 180 (Y) × 8 (Z) mm |
| Holes in the plate's top face | 31 — one central large hole plus 30 bolt and small holes |
| Gimbal mount bottom face | **Flush** with the plate top face (P-frame z = 0) |
| Yaw axis, column A | Vertical line through x = 0, y = −65 mm |
| Yaw axis, column B | Vertical line through x = 0, y = +65 mm |
| Distance between the two yaw axes | **130.00 mm** (self-check tolerance ±0.01 mm) |
| Column B orientation | The same column, **rotated 180°** about the plate's central vertical axis |
| Pitch axis | Along Y, through x ≈ 0, at P-frame z = **+213.44 mm**; the two columns' pitch axes are collinear |
| Yaw-axis reference height to pitch axis | **105.44 mm** along the column |
| Camera optical centre | P-frame z ≈ **+250 mm** **UNVERIFIED**{ .dh-unverified } — approximate, and the camera body the bracket was designed around is unconfirmed (see below) |
| Gimbal mount envelope | 80 × 66.3 × 84 mm |

Bolt holes in the mount's bottom face are concentric with holes in the plate:
**align by holes**, not by measurement.

!!! unverified "UNVERIFIED — shape of the top plate's central opening"
    The CAD parse above describes "one central large hole" and uses its centre
    as the P-frame origin. The team's torso-frame CAD animation shows the top
    plate's central opening as roughly **hexagonal**, not round. The parse
    wording may simply not state the shape. Check against the CAD before using
    the opening as a datum. *Owner: hardware lead.*

!!! missing "MISSING — which physical side is which"
    The CAD frame and the published simulation model use **opposite signs for
    y** on the left column: the CAD spec above places the left gimbal at
    y = −65 mm, and the MuJoCo model places `base_left` at y = +0.065 m. Both
    are internally consistent; they are different frame conventions, not a
    contradiction. But a builder mounting hardware has to know which physical
    side of the robot carries `cam_yaw_left` (ID 7) and `cam_pitch_left` (ID 8).

    Get this wrong and nothing complains: the operations manual records that a
    left/right camera swap is **silent** — tags land in the wrong camera frame
    and the gaze drives the wrong gimbal while every log line looks healthy.
    State the physical side explicitly, with a photograph, before this page is
    used. *Owner: hardware lead + controls.*

The robot's cameras are **RealSense D436**. The parts list, the repository
README and the extrinsics script all say so; the team data wiring diagram
labels both cameras "RealSense Depth Camera D436"; and the team log upgrades
librealsense to 2.58.1, the version that adds D436 support (the repository pins
`pyrealsense2` 2.58.1). *Source: team data wiring diagram (V2); team design
log, RealSense setup; `deploy/requirements.txt`.*

!!! unverified "UNVERIFIED — which camera body the gimbal bracket CAD was designed around"
    The CAD provenance table names the camera component
    `IntelRealsense_D435_Multibody` and one row of the mounting spec says
    "D435". Almost certainly a naming slip in the CAD, but the mounting
    envelopes differ between RealSense models, so confirm which body the bracket
    was designed around before machining anything. *Owner: hardware lead.*

## Range of motion

| Joint | Range in the published model | What that number is |
| --- | --- | --- |
| Yaw | ±270° | **Not a mechanical limit.** The model comment records it as ±2π narrowed to ±1.5π *to ease reinforcement learning*. It is a training choice |
| Pitch | ±90° about a level zero **UNVERIFIED**{ .dh-unverified } | Derived from the CAD, then symmetrised: the raw fit gave −89.71° to +87.91°, and the model rounds it to a symmetric ±90° |

!!! missing "MISSING — SAFETY — the yaw axis and the camera cable"
    A USB-C cable crossing a joint that turns ±270° cannot simply be looped.
    Either the hardware yaw travel is much smaller than the modelled ±270°, or
    the column contains something that lets the cable cross the axis — a slip
    ring, a service helix with a defined number of turns, or a hard stop that
    protects the cable.

    Nothing in the project says which. This is the single most important open
    question on this page, because the failure mode is a cable that survives
    assembly, survives the first bench test, and fails after a few hundred
    gaze cycles in a place that needs the whole column stripped to reach.

    Required: the real mechanical yaw travel, the cable's minimum bend radius
    and the number of turns it tolerates, and the commanded yaw limit that
    respects both. Until this exists, do not command the yaw axis beyond the
    travel you have verified by hand.
    *Owner: hardware lead.*

## Parts in one column

The CAD assembly names four mechanical components plus the actuators and the
camera. There is **no machined-part row in the BOM for any of them** — the
machining sheet covers leg, arm and body only, so the gimbal parts are unpriced
and unspecified as to material, process and tolerance.

| Component | What it is |
| --- | --- |
| `gimbal_mount` | The base that bolts flush to the top plate and carries the yaw actuator |
| `gimbal_neck` | The link driven by the yaw actuator, carrying the pitch actuator |
| `gimbal_arm` | The link driven by the pitch actuator, carrying the camera. The CAD animation draws **two** separate L-shaped arms (see below) |
| `U-joint_type_C_adapter` | An adapter between the pitch stage and the camera. In the CAD animation it looks like a U-shaped USB-C adapter (see below) |
| Flanged ball bearing | Pitch idler: carries the arm on the side opposite the pitch actuator. Size **TODO**{ .dh-missing }; not in any list |
| RobStride 05 | Yaw actuator, its body centred on the yaw axis |
| RobStride 05 | Pitch actuator, mounted with its own axis remapped to the pitch direction |
| Intel RealSense D436 | The camera |

The published module weighs **0.58 kg** per column in the model — 0.246 kg base,
0.233 kg yaw link, 0.100 kg pitch link, from Fusion 360 mass properties. Two
columns therefore put a little over a kilogram on the top plate, all of it above
the plate and most of it moving. **UNVERIFIED**{ .dh-unverified } These are CAD
masses for parts whose material is not specified, not the weight of a built
column.

!!! missing "MISSING — the gimbal parts are not in any bill of materials"
    Four machined or printed components, their material, process, tolerance,
    finish and cost, plus the bearings, fasteners and the adapter. The CAD
    animation adds at least one part no list names: a small flanged ball
    bearing on the pitch axis, one per column, size unknown. The camera
    module is the headline contribution of this robot and it is the one
    subassembly that cannot currently be quoted at all.
    *Owner: hardware lead + BOM owner. See
    [Bill of materials](../bom/index.md).*

<figure markdown>
  <video class="dh-clip" autoplay loop muted playsinline preload="metadata" width="1280" height="720"
    poster="../../assets/exploded/twincities-poster.webp" aria-label="Exploded view of one camera gimbal column"><source src="../../assets/exploded/twincities.mp4" type="video/mp4"><a href="../../assets/exploded/twincities.mp4">Exploded view of one camera gimbal column</a></video>
  <figcaption>Team's unlabelled CAD animation: one camera gimbal column: pedestal, yaw actuator, neck, pitch actuator, two L-shaped arms with an idler bearing, and the RGB-D camera.</figcaption>
</figure>

> **Figure** <span class="pending-figure">labelled version not produced yet</span> —
> `assets/assembly/head-exploded.png`: the animation above has no labels and
> no axes drawn. Still needed: one gimbal column exploded along its axis, each
> part labelled, with the yaw and pitch axes drawn through the assembly.

### What the CAD animation shows

From the bottom of one column:

- a four-fin tapered pedestal (`gimbal_mount`);
- the yaw actuator, standing in the pedestal's top recess. No separate yaw
  bearing is drawn;
- a neck column ending in a U-cradle (`gimbal_neck`);
- the pitch actuator, lying across the cradle;
- **two separate L-shaped arms** that close around the camera as a yoke. One
  bolts to the pitch actuator's six-hole output disc; the other pivots on a
  **small flanged ball bearing** seated in a boss on the neck. So the pitch
  axis is supported on both sides;
- the RGB-D camera bar on top;
- a small U-shaped part at the camera's end that looks like a USB-C
  plug-to-socket adapter, and on the outer face of the idle-side arm a small
  U-shaped clip centred on the pitch axis, possibly a cable clip.

The explode is vertical, and the pitch-stage parts move out along the pitch
axis. The layout matches the numbered hardware figure in the repository
(joints 15 yaw, 16 pitch). The animation's file name, "twincities", is not
defined in any source; probably a nickname for the twin columns.

*Source: team exploded-view CAD animation of one gimbal column.*

!!! unverified "UNVERIFIED — one `gimbal_arm` or two arm pieces"
    The CAD parse lists a single `gimbal_arm` component. The animation shows two
    separate L-shaped arm pieces, left and right. Whether `gimbal_arm` is one
    part, two different parts or two instances of one part is not settled.
    *Owner: hardware lead.*

!!! unverified "UNVERIFIED — what `U-joint_type_C_adapter` is"
    This page has described it as a mechanical adapter between the pitch stage
    and the camera. In the animation it looks like a U-shaped USB-C cable
    adapter at the camera port. Which it is changes both the parts list and the
    cable design in step 6. *Owner: hardware lead.*

## Sub-assembly A — one column

{{ step(1, "Configure the four actuators and record the camera serials") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 05 | 4 | IDs 5, 6, 7, 8 — all on `can25` |
| Intel RealSense D436 | 2 | One per column |
| Masking tape and marker | As needed | Labels |

</div>

Set each actuator's CAN ID on the bench and label it with its joint name.

Then, before either camera goes into a bracket, **read and write down both
RealSense serial numbers** and decide which serial is the left camera. The
control stack binds a camera to a port by serial; with no serial pinned, USB
enumeration order decides, and that order changes across replugs and power
cycles. Tape the serial to the column it goes into.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/head-step-01.png`: four labelled RobStride 05 actuators and
> two D436 cameras with their serial labels visible.

{{ checkpoint("All four actuators answer at IDs 5, 6, 7 and 8 on can25, each carries a label, and both camera serial numbers are written down against the column they will be installed in.") }}

{{ step(2, "Install the yaw actuator in the gimbal mount") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| `gimbal_mount` | 1 | Base component, 80 × 66.3 × 84 mm envelope |
| RobStride 05 | 1 | Yaw actuator; ID 7 for the left column, 5 for the right |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

The yaw actuator body is centred on the yaw axis, so its own alignment in the
mount **is** the column's alignment. Anything eccentric here tilts the whole
column, and the tilt is multiplied by the 250 mm to the camera's optical centre.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/head-step-02.png`: yaw actuator seated in the gimbal mount,
> yaw axis drawn, mount bottom face called out as the plate datum.

!!! missing "MISSING — yaw actuator location in the mount, yaw bearing, fasteners, torque"
    How the actuator is located in the mount, and whether any bearing carries
    the yaw load alongside the actuator's own. The CAD animation shows the yaw
    actuator sitting directly in the pedestal's top recess with no separate yaw
    bearing drawn; that absence is from the animation only.
    Fasteners, torque, threadlocker: unknown.
    *Owner: hardware lead.*

{{ checkpoint("The yaw output turns freely by hand with no axial play, and the mount's bottom face is clean, flat and undamaged — it is the datum the whole module is aligned by.") }}

{{ step(3, "Fit the neck to the yaw output") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| `gimbal_neck` | 1 | Yaw-driven link |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

The neck carries the pitch axis **105.44 mm** from the yaw reference, so an
angular error at this interface becomes a position error at the camera.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/head-step-03.png`: neck on the yaw output, with the 105.44 mm
> yaw-to-pitch distance dimensioned.

!!! missing "MISSING — neck-to-yaw-output fastening, keying, and what sets the yaw zero"
    Fasteners, torque, threadlocker. Whether the neck is keyed or clocked to the
    yaw output, and what sets the yaw zero position.
    *Owner: hardware lead.*

{{ checkpoint("The neck is square to the yaw axis and the assembly rotates without wobble when spun by hand.") }}

{{ step(4, "Install the pitch actuator and the arm") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| RobStride 05 | 1 | Pitch actuator; ID 8 for the left column, 6 for the right |
| `gimbal_arm` | 1 **UNVERIFIED**{ .dh-unverified } | Pitch-driven link, carries the camera; drawn as two L-shaped pieces in the CAD animation |
| Flanged ball bearing | 1 | Pitch idler on the neck boss; size **TODO**{ .dh-missing } |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

The pitch actuator mounts with its axis across the column — in the CAD its local
z is remapped to the global y direction. The pitch axis must end up
**perpendicular to and intersecting** the yaw axis; if it does not, the two
columns cannot be calibrated to a common frame later.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/head-step-04.png`: pitch actuator and arm on the neck, both
> axes drawn, showing the perpendicular intersection.

!!! missing "MISSING — pitch stage fasteners, what sets the pitch zero, whether a mechanical stop exists"
    Fasteners, torque, threadlocker. What sets the pitch zero, given that the
    model defines pitch zero as *level* and the raw CAD fit was not symmetric
    about it (−89.71° / +87.91°). Whether a mechanical stop exists.
    *Owner: hardware lead.*

{{ checkpoint("Pitch moves through its travel with no binding, the pitch axis is perpendicular to the yaw axis, and the arm does not strike the neck or the mount at either extreme of pitch at any yaw angle.") }}

{{ step(5, "Mount the camera") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| Intel RealSense D436 | 1 | The serial recorded in step 1 for this column |
| `U-joint_type_C_adapter` | 1 | Adapter between the pitch stage and the camera |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

The camera's pose relative to the two gimbal axes is what
[Camera calibration](../bringup/camera-calibration.md) later has to solve for.
A repeatable, rigid mount is worth more here than a precise one: calibration can
absorb a known offset, but it cannot absorb a camera that shifts.

Handle the camera by its body, never by the glass, and leave the protective film
on until the column is finished.

!!! note "Every camera is individually calibrated at the factory"
    The RGB-to-depth extrinsics in this project were read off one specific
    physical camera (the model constants are annotated with its serial number).
    A rebuilt robot has different cameras, so those constants do not transfer:
    read your own units' extrinsics during bring-up.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/head-step-05.png`: camera and adapter on the arm, with the
> optical centre marked and the 250 mm height above the plate dimensioned.

!!! missing "MISSING — camera fasteners and torque, and the camera pose tolerance"
    Fasteners and torque for the camera — a plastic-bodied camera is easy to
    distort with an over-torqued screw, and a distorted camera body is a
    calibration that will not hold.
    The tolerance on the camera pose relative to the gimbal axes.
    *Owner: hardware lead + perception.*

{{ checkpoint("The camera is rigid in the bracket, cannot be moved by hand pressure, and its glass is clean and unmarked.") }}

{{ step(6, "Route the camera cable across both axes") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| USB-C cable | 1 | **TODO**{ .dh-missing } — length and type per column not specified |
| Cable retention | As needed | **TODO**{ .dh-missing } — scheme not documented |

</div>

This is the step that decides whether the module lasts. The cable crosses two
moving axes, one of which is modelled at ±270°, and it carries a USB 3 signal
that degrades with tight bends and repeated flexing. A camera that drops to USB 2
after a power cycle is a documented failure on this robot; a cable damaged at
assembly is one of the ways to get there permanently.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/head-step-06.png`: the cable route drawn through the column at
> three yaw positions — full left, centre, full right — showing the service loop
> and every retention point.

!!! missing "MISSING — SAFETY — camera cable design across the yaw and pitch axes"
    The whole cable design: cable type and length, the minimum bend radius it
    tolerates, where the service loop lives, how many turns of yaw it survives,
    every retention point, and the strain relief at the camera connector.
    A partial hint only: the CAD animation shows what looks like a U-shaped
    USB-C adapter at the camera and a small clip on the pitch axis, which
    suggests how the cable crosses the pitch axis (both
    **UNVERIFIED**{ .dh-unverified }). Nothing shows how it survives the yaw
    axis.
    Until this exists, the verified-safe yaw travel is whatever you have turned
    by hand while watching the cable.
    *Owner: hardware lead + electrical.*

{{ checkpoint("With the cable installed, both axes move through their verified travel and back with no tension, no rubbing and no change in cable position at the connector; the camera enumerates at USB 3 speed at every extreme, not only at centre.") }}

{{ step(7, "Bench-test the column before it goes on the robot") }}

The camera module is the one subassembly that can be fully tested on its own,
and it should be — it is the headline capability, it is the hardest part to
reach once the robot is assembled, and a fault found here costs an afternoon
rather than a teardown.

What the bench test has to cover:

- both actuators enable, move and report position on `can25`;
- the camera streams colour and depth at the serial you recorded;
- the image moves the way the commanded axis says it should — yaw commands
  produce horizontal motion, pitch commands vertical;
- the whole verified travel of both axes, with the cable installed;
- nothing warms up, binds or changes drag over a few hundred cycles.

!!! missing "MISSING — bench harness and written test procedure for a single column"
    A standalone bench harness and a written test procedure for a single column:
    power, one CAN adapter, a USB port, and a script. This does not exist yet
    and it is the highest-value missing piece of test equipment in the project.
    *Owner: hardware lead + controls.*

{{ checkpoint("One complete column has moved through its full verified travel on both axes while streaming colour and depth, with no binding, no cable strain and no camera dropout.") }}

## Sub-assembly B — the second column and the mount

{{ step(8, "Build the second column") }}

Build it from the **same parts** as the first. The two columns are identical:
the right one is the left one rotated 180° about the plate's central vertical
axis, not a mirror image. Nothing is handed, and no part needs to be remade.

Use IDs 5 and 6 for the column that carries `cam_yaw_right` and
`cam_pitch_right`, and the camera serial you assigned to that side.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/head-step-08.png`: both finished columns side by side in their
> installed orientations, making the 180° rotation visible.

{{ checkpoint("The second column passes the same bench test as the first, at its own IDs and with its own camera serial.") }}

{{ step(9, "Mount both columns on the top plate") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| Gimbal column | 2 | From steps 2–8 |
| `CNC_body03_x1_top_plate` | 1 | Fitted during [Torso and waist](torso-and-waist.md) |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

Align each mount by its bolt holes, which are concentric with the holes in the
plate. Both mount bottom faces sit **flush** on the plate top face. The second
column goes on rotated 180° about the plate's central hole.

Target geometry, from the CAD:

- the two yaw axes **130.00 mm** apart, symmetric about the plate's central
  hole, within ±0.01 mm at the self-check;
- both pitch axes collinear, 213.44 mm above the plate's top face;
- both mount bottom faces flush, with no shim and no gap.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/head-step-09.png`: both columns bolted to the top plate, with
> the 130 mm axis spacing and the 213.44 mm pitch-axis height dimensioned, and
> the cable exits through the plate visible.

!!! missing "MISSING — mount-to-plate fasteners, torque and location method"
    Fasteners, count, pattern and torque for the mount-to-plate interface — this
    is the joint that holds the robot's perception geometry, and it sees the
    inertia of a moving mass every time the gaze slews.
    Whether a dowel or pilot locates the mount, or the bolts alone do.
    *Owner: hardware lead.*

{{ checkpoint("Both columns are bolted flush to the plate, the two yaw axes measure 130.00 mm apart, both pitch axes are collinear, and each column moves through its full verified travel without contacting the other column, the plate or its own cabling.") }}

{{ step(10, "Record the as-built geometry") }}

Before the head goes onto a robot, write down what you actually built:
which camera serial is on which side, which actuator ID is in which column, the
measured yaw-axis spacing, and the verified travel of each of the four joints.

These four numbers are the input to
[Camera calibration](../bringup/camera-calibration.md), and they are the first
thing anyone will ask for when a gaze behaviour looks wrong.

{{ checkpoint("An as-built record exists for this head: two camera serials bound to physical sides, four actuator IDs bound to columns, the measured axis spacing, and the verified travel of each joint.") }}

## Why this module deserves the extra care

Every other subassembly on this robot has an equivalent somewhere else in the
open-source humanoid world. This one does not: two independently aimed RGB-D
cameras on their own gimbals is the design claim the project is making, and the
visible–reachable workspace results depend on the two columns being where the
model thinks they are. A leg built 0.5° out is a leg with a slightly odd gait.
A camera column built 0.5° out is a perception system that reports the world in
the wrong place, quietly, for as long as nobody checks.

## Figures this page needs

None of these figures exists yet **TODO**{ .dh-missing }.

| File | Step | What it must show |
| --- | --- | --- |
| `assets/assembly/head-exploded.png` | page header | One column fully exploded, both axes drawn, all parts labelled (an unlabelled CAD animation is already on the page) |
| `assets/assembly/head-step-01.png` | 1 | Four labelled actuators, two cameras with serial labels |
| `assets/assembly/head-step-02.png` | 2 | Yaw actuator in the mount, yaw axis, mount datum face |
| `assets/assembly/head-step-03.png` | 3 | Neck on the yaw output, 105.44 mm dimensioned |
| `assets/assembly/head-step-04.png` | 4 | Pitch actuator and arm, perpendicular intersecting axes |
| `assets/assembly/head-step-05.png` | 5 | Camera and adapter on the arm, optical centre and 250 mm height |
| `assets/assembly/head-step-06.png` | 6 | Cable route at full-left, centre and full-right yaw |
| `assets/assembly/head-step-08.png` | 8 | Both columns side by side in installed orientation, 180° rotation visible |
| `assets/assembly/head-step-09.png` | 9 | Both columns on the top plate, 130 mm and 213.44 mm dimensioned |
| `assets/assembly/head-axes-diagram.png` | geometry | A dimensioned line diagram of the P-frame, both yaw axes, the pitch axis and the optical centre — the drawing a machinist and a calibration engineer can both work from |
