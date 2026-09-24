# Final integration

Joining the finished subassemblies into a robot: legs to pelvis, arms to torso,
camera columns to the top plate, grippers to the wrists, and every harness
branch into one machine. This is the stage where the parts stop being parts you
can pick up.

**The battery stays disconnected for every step on this page.**

!!! missing "Structure only — do not attempt final integration from this page"
    Interface fasteners, torques, lifting points and the harness join have never
    been recorded. Do not attempt final integration from this page.

!!! danger "Two people, or a hoist, from here on"
    The finished robot is **36 kg** and 1.2 m tall. Every step below moves a
    mass that will injure someone if it falls, and the assembly gets
    progressively less stable as limbs go on. Read
    [Safety](../before-you-start/safety.md) first.

## Before you start

Every subassembly must be finished and checked on its own bench first. Bringing
an unverified limb to this stage means diagnosing it inside a robot.

- [ ] Two legs, each passing its own final checkpoint
- [ ] Two arms, each passing its own final checkpoint
- [ ] Torso with waist, computer, packs, converters, CAN adapters and IMU installed
- [ ] Two camera columns, each bench-tested with its camera streaming
- [ ] Two grippers, each with open and closed positions recorded
- [ ] Every actuator labelled with its joint name, CAN ID and bus
- [ ] Both camera serials recorded against their physical sides
- [ ] Both gripper servo IDs and driver-board serials recorded against their hands

!!! missing "MISSING — SAFETY — lifting points and support"
    No lifting point, stand, frame or support fixture is defined anywhere for
    this robot. Every step on this page needs one. Decide before the first lift:
    where the sling attaches, what holds the torso while the legs go on, and
    what holds the robot between stages.

    The operations manual already constrains how the finished robot hangs — the
    legs must hang straight, because a bent-leg hang tilts the torso and
    corrupts the geometry the perception stack depends on. The stand chosen here
    has to make that hang the natural one.
    *Owner: hardware lead + [Safety](../before-you-start/safety.md).*

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/final-support-rig.png`: the stand or frame holding the torso
> during integration, with the sling route and lifting points marked.

## The six buses, in one picture

Every branch joins during this stage. Nothing about this arrangement is
symmetric, so check each join against the table rather than against the other
side.

| Bus | Carries |
| --- | --- |
| `can22` | Waist (ID 1) **and** both shoulder-pitch actuators (IDs 10, 20) — spans the torso and both shoulders |
| `can9` | Left arm, six joints (IDs 11–16) |
| `can21` | Right arm, six joints (IDs 21–26) |
| `can24` | Left leg, six joints (IDs 31–36) |
| `can23` | Right leg, six joints (IDs 41–46) |
| `can25` | All four camera-gimbal joints (IDs 5–8) |

Plus two serial links to the gripper servos, and two USB-C runs from the
cameras. See [CAN bus](../electrical/can-bus.md) and
[Routing](../electrical/routing.md).

## Steps

{{ step(1, "Support the torso") }}

Get the torso onto its stand or into the sling, level and stable, with the waist
free to move and with access to both hip interfaces and both shoulder
interfaces.

!!! missing "MISSING — how the torso is supported during integration, upright or lying down"
    What the torso is supported by and how. Whether the robot is built upright
    or lying down. *Owner: hardware lead.*

{{ checkpoint("The torso is supported so that it cannot fall or rotate when a 6 kg <strong class='dh-unverified'>UNVERIFIED</strong> limb is offered up to one side of it, and both hip and both shoulder interfaces are reachable.") }}

{{ step(2, "Attach the first leg to the pelvis") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| Leg subassembly | 1 | Left leg first, or right — **TODO**{ .dh-missing }, if it matters |
| Hip interface fasteners | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } — not specified |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/final-step-02.png`: leg offered up to the pelvis, showing the
> interface, the fastener pattern and where the leg is supported during the join.

!!! missing "MISSING — hip interface: fasteners, torque, location, crew size, leg support"
    The hip interface: fastener size, count, pattern, torque, threadlocker, and
    whether anything locates the leg besides the fasteners. How many people this
    step needs. How the leg is supported while it is bolted on.
    *Owner: hardware lead.*

Where this joint is, is itself **UNVERIFIED**{ .dh-unverified }. The team's CAD
animations put the waist and both legs' `hip_1` and `hip_2` actuators in one
pelvis block, with hip yaw as the first joint of the leg below it; this site
builds all three hip joints into the leg. See
[Leg](leg.md#what-the-cad-animations-show).

{{ checkpoint("The leg is fully fastened to the pelvis, all six of its joints still move through their full travel, and the leg's harness branch is routed to the torso but not yet connected.") }}

{{ step(3, "Attach the second leg") }}

Repeat step 2 for the other leg. Check as you go that you are fitting the
correct leg to the correct side — the two legs differ at least electrically, by
CAN bus and by ID, and may differ mechanically **UNVERIFIED**{ .dh-unverified } —
see [Leg → Mirroring](leg.md#mirroring).

{{ checkpoint("Both legs are on, both move freely, and the robot is symmetric: measure the same dimension on both sides rather than assuming.") }}

{{ step(4, "Attach both arms to the torso") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| Arm subassembly | 2 | |
| Shoulder interface fasteners | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } — not specified |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

Remember that each shoulder takes **two** buses: `can22` for the shoulder-pitch
actuator, and `can9` or `can21` for the other six joints of that arm. Confirm
which arm you are holding before it goes on.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/final-step-04.png`: arm at the shoulder interface, both cable
> groups visible entering the torso.

!!! missing "MISSING — shoulder interface: fasteners, torque, and the build order of the shoulder-pitch actuator"
    Where the shoulder-pitch actuator sits is now known from the CAD: its body
    sits in the round opening of the torso side plate, and the arm bolts to its
    output through a square adapter. Still missing: whether the actuator goes
    into the side plate before the arm is attached or arrives already on the
    arm, and the interface's fastener size, count, pattern, torque and
    threadlocker. *Source for the location: team exploded-view CAD animations
    of the torso frame and the arm.* *Owner: hardware lead.*

{{ checkpoint("Both arms are fastened, all seven joints of each move through their full travel, and neither arm contacts the torso or a leg anywhere in its travel.") }}

<figure markdown>
  <video class="dh-clip" autoplay loop muted playsinline preload="metadata" width="1154" height="650"
    poster="../../assets/exploded/camera-mount-poster.webp" aria-label="Whole robot with camera columns and grippers lifting off"><source src="../../assets/exploded/camera-mount.mp4" type="video/mp4"><a href="../../assets/exploded/camera-mount.mp4">Whole robot with camera columns and grippers lifting off</a></video>
  <figcaption>Team's unlabelled CAD animation: whole robot; the two camera gimbal columns lift off the top plate and the two grippers come off the wrists (steps 5 and 6 below). It is not the full exploded overview, which is still pending on the Assembly index.</figcaption>
</figure>

{{ step(5, "Install the camera columns") }}

Both columns go onto the top plate as described in
[Head and camera gimbal](head-and-camera-gimbal.md), step 9. If the plate was
fitted with the columns already on it, verify here that nothing moved.

{{ checkpoint("Both columns are flush and fastened, the two yaw axes measure 130.00 mm apart, and each column moves through its verified travel without contacting the other column, the plate or an arm at any arm pose.") }}

{{ step(6, "Install the grippers") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| Gripper subassembly | 2 | With their measured open and closed positions recorded |
| Wrist interface fasteners | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } — not specified |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

Each gripper's flange bolts to its arm's `wrist_3` output, and its servo cable
runs back up the arm to its driver board in the torso.

!!! missing "MISSING — wrist-to-gripper interface dimensions, jaw clocking, fasteners, torque"
    The wrist-to-gripper interface, dimensioned from both sides, plus the
    clocking that sets the jaw orientation relative to the wrist. Fasteners,
    torque, threadlocker. *Owner: hardware lead.*

{{ checkpoint("Both grippers are fastened, both open and close on their servos, and each gripper's eight AprilTags are visible to the cameras in at least one arm pose.") }}

{{ step(7, "Join the harnesses") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| Torso harness | 1 | **TODO**{ .dh-missing } — not yet designed |
| Cable ties / anchors | As needed | **TODO**{ .dh-missing } |

</div>

Join each limb's branch to the torso harness: six CAN buses, two gripper serial
links, two camera USB-C runs, plus power to each branch. Work one branch at a
time and check it off the bus table above as you go.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/final-step-07.png`: the torso with every branch connected,
> each connector labelled with its bus or function.

!!! missing "MISSING — the entire torso harness"
    The entire torso harness. Connector types, branch lengths, service loops at
    the hip, shoulder and waist, retention, and the order branches are joined
    in. See [Harness fabrication](../electrical/harness-fabrication.md).
    *Owner: electrical.*

{{ checkpoint("Every branch is connected and labelled, no connector is under tension, and the waist, both hips and both shoulders move through their full travel with the harness in place and nothing pulled, rubbed or pinched.") }}

{{ step(8, "Full mechanical inspection") }}

Before any power, go over the whole machine once, deliberately:

- every fastener the build called for is present;
- nothing is left over from the kitting trays — a leftover fastener means a
  missed step, not a spare;
- every joint moves through its full travel by hand, one at a time and in the
  combinations that bring parts close together;
- no cable is stretched, rubbed, pinched or kinked at any combination of joint
  angles;
- nothing rattles when the robot is rocked gently on its stand;
- both camera columns are clean and their lenses undamaged;
- the packs are still disconnected.

!!! missing "MISSING — written inspection checklist keyed to the fastener schedule"
    A written inspection checklist keyed to the fastener schedule, so the
    inspection can be signed rather than remembered.
    *Owner: hardware lead.*

{{ checkpoint("Every joint moves freely through its full travel, no cable is under strain at any pose, no fastener is missing, nothing is left over, and the battery is still disconnected.") }}

{{ step(9, "Weigh and hang the robot") }}

Record the as-built mass and compare it with the published 36 kg. A large
difference means something was substituted, omitted or doubled, and it is far
cheaper to find that now than during the first walk.

Hang the robot as the operations doctrine requires: **legs straight**. A
bent-leg hang tilts the torso and corrupts the geometry the perception stack
depends on — three test sessions were lost to that before it was written down.

!!! missing "MISSING — as-built mass by subassembly, and how the robot is rigged to hang legs straight"
    The as-built mass of a real robot, broken down by subassembly, and how the
    robot is rigged so the legs hang straight.
    *Owner: whoever performs the first documented build.*

{{ checkpoint("The robot hangs stable and level from its lifting points with the legs straight, the as-built mass is recorded, and nothing shifts or sags when it is suspended.") }}

## Hand-off

The mechanical build is finished. Do **not** connect a battery here.

1. [Electrical](../electrical/index.md) — power system, CAN bus, routing.
2. [Pre-power checks](../electrical/pre-power-checks.md) — the gate before the
   first connection.
3. [Bring-up](../bringup/index.md) — first power-on, motor configuration, joint
   zeroing, camera calibration, acceptance tests.

## Figures this page needs

None of these figures exists yet **TODO**{ .dh-missing }.

| File | Step | What it must show |
| --- | --- | --- |
| `assets/assembly/final-support-rig.png` | before you start | The stand or frame and the sling route |
| `assets/assembly/final-step-02.png` | 2 | Leg at the pelvis interface, fastener pattern, support |
| `assets/assembly/final-step-04.png` | 4 | Arm at the shoulder interface, both cable groups entering the torso |
| `assets/assembly/final-step-07.png` | 7 | Torso with every branch connected and labelled |
| `assets/assembly/final-robot-hanging.png` | 9 | The finished robot hanging with the legs straight, for comparison against a bent-leg hang |
