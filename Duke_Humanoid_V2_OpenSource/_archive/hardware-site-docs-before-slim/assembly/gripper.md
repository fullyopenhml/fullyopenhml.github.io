# Gripper

A single-servo, rack-and-pinion **parallel-jaw** gripper. Two jaws ride mirrored
slides and are coupled 1:1, so one servo opens and closes both. Build two.

Unlike every other joint on this robot, the gripper is **not** a RobStride on
CAN: it is a Feetech bus servo on a serial link from its own driver board in the
torso. That difference runs all the way through the build, the harness and the
software.

!!! missing "Structure only — do not attempt a gripper from this page"
    The structure below comes from the published gripper model and its
    generator. Fastener sizes, torques, the pinion and rack fit, the jaw pad
    material and the assembly order have never been recorded. Do not attempt a
    gripper from this page.

!!! warning "Blocking prerequisite — set the servo ID first"
    Set and label each servo's ID on its driver board before it goes into a
    gripper body.

## What drives it

| Item | Left hand | Right hand |
| --- | --- | --- |
| Actuator | Feetech HL-3915-C001, 12 V | Feetech HL-3915-C001, 12 V |
| Servo ID | 5 | 0 **UNVERIFIED**{ .dh-unverified } — a bench script uses 19 |
| Link | Serial, own Waveshare ST/SC bus driver board | Serial, own driver board |
| Board identity | Bound by the CH340 board's USB serial number | Bound by the CH340 board's USB serial number |

Both gripper servo driver boards plug into USB Hub #3 in the torso.
*Source: team data wiring diagram (V2).*

!!! unverified "UNVERIFIED — the servo IDs are not consistent across the project"
    The end-effector service names left = 5 and right = 0. A bench script in the
    same repository uses ID 19 for the right gripper. One of these is stale, and
    a builder cannot tell which from the outside.

    Pin the IDs, state them here, and label the physical servo — the board-to-hand
    mapping has already caused one recorded field failure, when a udev rule
    still named a driver board that was no longer plugged in.
    *Owner: controls + hardware lead.*

## What it weighs and how far it opens

From the published model and its Fusion 360 mass properties.

| Quantity | Value | Source |
| --- | --- | --- |
| Mass, gripper with mounting flange | ≈ 346 g **UNVERIFIED**{ .dh-unverified } | Model; the paper's spec table rounds this to 350 g |
| Mass split | 324 g gripper + 22 g flange **UNVERIFIED**{ .dh-unverified } | Model |
| Jaw coupling | 1:1, enforced by an equality constraint; one actuator | Model |
| Fingertip reach from the mount face | ≈ 120 mm **UNVERIFIED**{ .dh-unverified } | Model |
| Jaw travel | −0.05 m to +0.0347 m of jaw coordinate | Model |
| Fully open | jaw coordinate −0.05 m | Model |
| Fingers touch | near jaw coordinate +0.018 m **UNVERIFIED**{ .dh-unverified } | Model |

!!! missing "MISSING — SAFETY — two different jaw openings are published"
    The gripper model's own documentation gives a finger gap of about **184 mm**
    at fully open. The running gripper service maps its open and close positions
    to an aperture of **90 mm to 0 mm**, and says in the source that this map is
    *uncalibrated*.

    These cannot both describe the same hardware. A reader designing a workcell,
    or anyone sizing an object for the two-target benchmark, needs one number.
    Measure the built gripper, publish the measured aperture, and correct
    whichever source is wrong. *Owner: hardware lead + controls.*

## Parts in one gripper

The gripper model names three mechanical bodies plus a mounting flange. As with
the camera module, **none of them appears in the machining sheet**, so the
gripper cannot currently be quoted.

| Component | What it is |
| --- | --- |
| `base` | The body: carries the servo, the slides, the two tag-holder plates and their four tag pads, and a USB-C protector |
| `left_rack` | One jaw, on a slide |
| `right_rack` | The other jaw, on the mirrored slide |
| `cnc_flange` | The machined mounting disc with the bolt-hole ring; the wrist interface |
| Feetech HL-3915-C001 | The one actuator |

!!! missing "MISSING — the gripper is not in any bill of materials"
    Material, process, tolerance, finish and cost for the base, both racks and
    the flange; the pinion; the slide or rail components; the fasteners; the jaw
    pads. The gripper is quoted in the parts list only as its servo.
    *Owner: hardware lead + BOM owner.*

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/gripper-exploded.png`: one gripper exploded — base, servo,
> pinion, both racks, flange, jaw pads and the eight tag pads — every part
> labelled, with the slide direction and the jaw travel drawn.

## Steps

{{ step(1, "Configure and label the two servos") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| Feetech HL-3915-C001 servo | 2 | One per hand |
| Waveshare ST/SC bus servo driver board | 2 | One per hand |
| Masking tape and marker | As needed | Labels |

</div>

Set each servo's ID on its driver board, one at a time. Write the ID **and the
hand** on the servo body, and write the driver board's USB serial number down
against the hand it serves — the software resolves boards by serial, and a board
swapped between hands without updating that mapping routes right-hand commands
to the left hand.

{{ checkpoint("Each servo answers at its assigned ID on its own driver board, each servo carries a hand label, and each board's USB serial is recorded against its hand.") }}

{{ step(2, "Build the gripper base") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| `base` | 1 | Gripper body |
| Feetech HL-3915-C001 servo | 1 | With its ID already set |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/gripper-step-02.png`: servo seated in the base, with the
> pinion axis and the slide direction drawn.

!!! missing "MISSING — servo location and retention in the base, pinion mounting, backlash control"
    How the servo is located and retained. Whether the pinion is on the servo
    horn or on a separate shaft, and how backlash between pinion and racks is
    controlled. Fasteners, torque, threadlocker.
    *Owner: hardware lead, from a photographed build.*

{{ checkpoint("The servo is retained with no movement in its seat, and its output turns the pinion with no perceptible lost motion.") }}

{{ step(3, "Fit both racks") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| `left_rack` | 1 | Jaw on the positive slide |
| `right_rack` | 1 | Jaw on the mirrored slide |
| Slide / rail components | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } — not identified in any list |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

Both racks engage the same pinion from opposite sides; that is what makes the
jaws move together and stay parallel. Engage them in the position that puts the
jaws symmetric about the centreline, not in whatever position they fall into.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/gripper-step-03.png`: both racks engaging the pinion, with the
> tooth alignment that produces a symmetric jaw position highlighted.

!!! missing "MISSING — rack timing and symmetry setting; slide or rail parts, preload, lubrication"
    Which pinion tooth each rack starts on, and how symmetry is set and checked.
    The slide or rail parts, their preload and their lubrication.
    Fasteners, torque, threadlocker.
    *Owner: hardware lead, from a photographed build.*

{{ checkpoint("Both jaws move together through their whole travel, stay parallel and stay symmetric about the centreline, and the mechanism does not bind at either end of travel.") }}

{{ step(4, "Fit the jaw pads") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| Jaw pad | 2 **UNVERIFIED**{ .dh-unverified } | **TODO**{ .dh-missing } — material not specified; whether pads exist at all is open, see below |

</div>

!!! missing "MISSING — jaw pads: whether they exist, their material, how they are attached"
    Whether the jaws carry a pad at all, what it is made of, and how it is
    attached. The parts list has a TPU line with no part, no quantity and no
    price, which suggests a printed compliant pad exists somewhere; nothing
    names it. The pad decides what the robot can actually pick up, so it is not
    a detail. *Owner: hardware lead.*

{{ checkpoint("Both pads are attached, sit parallel to each other, and meet flat across their whole face when the jaws close.") }}

{{ step(5, "Apply the AprilTag fiducials") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| AprilTag decal, tag36h11 | 8 per hand | 4 on the jaw plates, 4 on the base tag-holder pads |

</div>

The tags are not decoration: the visual-servoing loop measures the gripper's
pose from them, so a tag in the wrong slot, on the wrong hand, or misaligned in
its pocket becomes a pose error the control stack cannot see.

Each tag is seated in a machined or printed pocket, so the pockets set the
alignment. The tag IDs are assigned per hand in the project's tag layout
(`simulation/asset/duke_v2/parallel_gripper/tag_layout.py`), which is the source
of truth for which ID goes in which slot.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/gripper-step-05.png`: both hands, every tag slot labelled with
> its tag ID, showing which four are on the jaws and which four on the base.

!!! missing "MISSING — AprilTag production and application: substrate, printed size, adhesive, replacement"
    How the tags are produced and applied: printed on what, at what size,
    adhered how, and how a tag is replaced when it is scuffed. A printed tag at
    the wrong scale is a silent pose error.
    *Owner: perception + hardware lead.*

{{ checkpoint("All eight tags on this hand are seated square in their pockets, carry the IDs the layout assigns to this hand, and are readable by a detector at the working distance.") }}

{{ step(6, "Fit the mounting flange") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| `cnc_flange` | 1 | Machined mounting disc with the bolt-hole ring |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

The flange is the gripper's half of the wrist interface. The arm's half is on
[Arm](arm.md), step 8, and neither half is dimensioned anywhere yet — the two
have to be documented together.

!!! missing "MISSING — gripper flange dimensions, jaw clocking, fasteners, torque"
    Bolt circle, pilot diameter, keying, and the clocking that puts the jaws in
    a known orientation relative to `wrist_3`. Fasteners, torque, threadlocker.
    *Owner: hardware lead.*

{{ checkpoint("The flange is square to the gripper body, its bolt ring matches the wrist interface, and the jaw plane is in the documented orientation relative to the wrist.") }}

{{ step(7, "Set the open and closed positions") }}

!!! danger "Crush hazard"
    This gripper is one actuator driving two jaws through a rack and pinion, and
    the servo has no idea what is between them. Keep fingers out of the jaws
    while it is powered. Set a torque limit before the first close, not after.

Establish and record, for this hand:

- the servo position at fully open and the servo position at fully closed;
- the servo torque limit used to close;
- the measured finger gap at fully open, in millimetres, and at the fingers-touch
  position.

The last of these is the measurement that settles the 184 mm versus 90 mm
conflict above, so record it carefully and publish it.

!!! missing "MISSING — gripper commissioning procedure: finding end stops, safe torque limit, matching hands"
    The commissioning procedure: how the end stops are found without driving the
    mechanism into them at full torque, what torque limit is safe for the rack
    and pinion, and how the two hands are made to agree.
    *Owner: controls + hardware lead.*

{{ checkpoint("Both jaws travel from fully open to fully closed and back under the servo, symmetrically and without binding; the open and closed servo positions, the torque limit and the measured finger gap are written down for this hand.") }}

## Figures this page needs

None of these figures exists yet **TODO**{ .dh-missing }.

| File | Step | What it must show |
| --- | --- | --- |
| `assets/assembly/gripper-exploded.png` | page header | Whole gripper exploded, slide direction and jaw travel drawn |
| `assets/assembly/gripper-step-02.png` | 2 | Servo in the base, pinion axis and slide direction |
| `assets/assembly/gripper-step-03.png` | 3 | Both racks on the pinion, symmetric tooth engagement highlighted |
| `assets/assembly/gripper-step-05.png` | 5 | Both hands with all eight tag slots labelled by tag ID |
| `assets/assembly/gripper-aperture.png` | 7 | The gripper at fully open and at fingers-touch, with the measured gap dimensioned |
