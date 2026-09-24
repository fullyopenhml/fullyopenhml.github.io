# Routing

Where each cable physically goes through a machine whose joints rotate. Routing
errors show up as a cable that is fine on the bench and severed after a thousand
cycles, so this page needs photographs, not descriptions.

What each cable connects is drawn in the two team diagrams: the
[power diagram](power-system.md#the-team-power-diagram) (packs, distribution
blocks, computer branch) and the
[data diagram](can-bus.md#the-team-data-wiring-diagram) (USB hubs, CAN
adapters, cameras, IMU, gripper boards). Both are shown together on
[Electrical](index.md#the-two-team-diagrams). Neither shows cable paths through
the robot; that is what this page is for.

## Why this page is hard on this robot

Three things make routing here worse than on a fixed-base arm.

**Every limb cable crosses several rotating joints.** A left-arm bus cable
reaches the wrist through six axes. It cannot simply be long enough; it has to be
long enough *at every pose the joint reaches*, and short enough not to be caught
at the opposite extreme.

**Cable wrap at the wrist is a documented, live constraint.** The hardware
joint-monkey choreography caps its sweep margin and its speed explicitly because
"hard limits risk cable wrap and the wrist encoders' known ±π wrap"
([`control/humanoid_joint_monkey_hw.py`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/humanoid_joint_monkey_hw.py)).
The software is working around a routing property. If your build routes
differently, that workaround does not transfer.

**The camera cables are the fussiest runs on the machine.** Each RealSense sits
on a 2-DoF gimbal, so its USB-C cable crosses two rotating axes and must still
hold a USB 3 link. The release includes a 40 Gbit/s short extension and a
right-angle USB-C plug specifically for these runs. A camera that negotiates USB2
instead of USB 3 is a documented, recurring symptom — the operations runbook
tells operators to replug or change ports until `lsusb -t` shows `5000M`. A
marginal routing job produces that symptom intermittently and you will chase it
for days.

## Routing record, per subassembly

This table is the deliverable. It is empty: every cell is marked **TODO**{ .dh-missing }.

| Subassembly | Cables crossing it | Bend radius limit | Service loop | Loop sized at pose | Clamp points | Photograph |
| --- | --- | --- | --- | --- | --- | --- |
| Leg (per side) | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| Arm (per side) | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| Waist | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| Torso | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| Camera gimbal (per module) | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| Gripper (per side) | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |

!!! missing "MISSING — routing record and photographs for every subassembly"
    Per subassembly:

    - A **photograph or render of the finished routing**, with the cable visible.
      Prose does not transfer a routing decision; a photograph does. This is the
      single highest-value missing artefact in the electrical section.
    - **Bend radius limit** for each cable type on that path, especially the
      camera USB-C runs, where too tight a bend costs the USB 3 link rather than
      breaking anything visibly.
    - **Service loop length** at each rotating joint, and — this is the part
      usually left out — **the joint position the loop is sized for**. A loop
      sized at mid-travel and a loop sized at one extreme are different lengths.
    - **Clamp and tie-down points**, and where sleeving starts and stops.
    - **Clearance from every pinch point** at the extremes of joint travel.
    - Which cables must be threaded **before** the limb is closed, called out in
      the matching [Assembly](../assembly/index.md) step.

    *Owner: electrical lead, from a photographed build.*

## Verifying a routing job

Two checks, in this order. Both are done with the robot suspended and the motors
unpowered.

{{ step(1, "Drive every joint to both extremes by hand") }}

Slowly, one joint at a time, watching the cable rather than the joint. You are
looking for: a cable that goes taut, a cable that gets pinched between two
moving parts, a cable rubbing on an edge, and a cable bent tighter than its rated
radius.

Do this before the limb is closed if you possibly can. A routing fault found with
the cover off is a five-minute fix.

{{ step(2, "Run the wiggle test with live telemetry") }}

Hand-inspection finds cables that are obviously wrong. It does not find a marginal
crimp or a conductor already broken inside its insulation. For that, use the tool
written after the 2026-07-24 dropout:

```bash
cd <deploy-repo>/control
python humanoid_wiggle_watch.py
```

It watches the telemetry stream and raises an immediate console alarm the moment
any joint's feedback freezes, so pressing a connector by hand gives you instant
cause and effect — *I pressed this connector and that pair dropped*.

How to run it so the result means something, from the tool's own notes:

- It is run with the arm **unpowered** **UNVERIFIED**{ .dh-unverified } and moved by hand.
- **Keep the whole limb stirring.** The detector requires at least two other
  joints on the same limb to be genuinely moving as a trustworthy reference; a
  still limb produces false alarms. The first hardware run of an earlier version
  logged 104 bogus events in 74 seconds for exactly this reason.
- It flags a joint whose position, velocity and effort triple is bit-identical
  for five consecutive telemetry rows (about 100 ms) while frozen mid-motion. The
  real 2026-07-24 events lasted 15–20 rows, so there is a large margin — but the
  margin only exists if the limb is moving.

!!! unverified "UNVERIFIED — what unpowered means for the wiggle test"
    This page says both checks are done with the motors unpowered, and the
    tool's notes say the arm is unpowered. But the wiggle test watches live
    telemetry — position, velocity and effort — which a motor can only report
    while its electronics are powered and on the bus. It is not stated whether
    unpowered means the motor bus is off, or only that no joint is enabled, and
    this page does not say what has to be running to produce the telemetry
    stream the tool reads. Until both are written down it is also unclear
    whether this check can be part of [Pre-power checks](pre-power-checks.md),
    whose check A5 requires both routing checks to pass before any pack is
    connected, or has to wait for
    [First power-on](../bringup/first-power-on.md). Confirm against the usage
    notes in the tool's own docstring, which name the controller setup it is
    meant to run against.

    *Owner: controls lead + electrical lead.*

Work along the whole harness: every connector, every clamp, every point where a
cable enters or leaves a limb. Squeeze, wiggle, and flex each one.

{{ checkpoint("With every joint driven slowly to both extremes of its travel by hand, no cable is stretched, pinched, rubbed, or bent tighter than its rated radius; and a full wiggle test along every connector and clamp raises no dropout alarm.") }}

## Trapped-cable check at final integration

!!! missing "MISSING — trapped-cable check at final integration"
    A last check, run once the robot is fully assembled, that no cable was
    trapped during closing: the list of places to look, and how to look at them
    without disassembly. This belongs alongside
    [Final integration](../assembly/final-integration.md).

    *Owner: electrical lead + assembly lead.*
