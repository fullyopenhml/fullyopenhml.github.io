# Joint zeroing

Establishing, for every joint, the encoder reading that corresponds to the zero
pose in the robot model. Everything downstream — the policy, the planner, the
workspace, the camera extrinsics — is expressed in those coordinates, so an error
here is silent and systematic.

## What the tool actually does

```bash
cd <deploy-repo>/control
python humanoid_set_zero.py
```

From
[`control/humanoid_set_zero.py`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/humanoid_set_zero.py):

- It writes the **current position of every motor in the motor table** as that
  motor's zero.
- It sets `zero_sta = 1` on every motor, which changes the reported range from
  `0..2π` to `−π..+π`.
- It **saves both to the drives**. This is persistent.
- It asks for a typed `yes` first. It has no command-line flags.

The RobStride vendor tool also offers a **set mechanical zero** function (see
[Motor ID and config](motor-id-and-config.md#the-vendor-tool)). Per the vendor
manual, a zero set that way is lost at power-off. This page gives no procedure
for it; the robot's zeros come from `humanoid_set_zero.py`.
*Source: team design log, "Robstride setup"; RobStride RS03 manual (cited, not
redistributed).*

So the entire procedure is: move every joint to its mechanical zero by hand, then
run the script. The precision of your robot's coordinate frame is exactly the
precision with which you positioned 31 joints by hand.

!!! danger "It is all 31 motors, every time. There is no per-joint zeroing."
    The script zeroes every motor in the table. There is no way to re-zero one
    joint, one limb, or the arms but not the cameras.

    This has already cost the reference robot a session. On 2026-07-29 a
    whole-robot zeroing run done **to fix the arms** silently destroyed the
    camera gimbal zero, which the perception chain assumes means *the camera
    looks straight ahead*. The result was a stationary cube reporting a different
    position on every run — once at 1.03 m radially, once apparently behind the
    robot — while every log line looked healthy. The diagnostic tool
    `humanoid_gimbal_zero_check.py` exists because of that day.

    **If you re-zero anything, you have re-zeroed everything.** Re-verify the
    gimbals and re-run [Camera calibration](camera-calibration.md) afterwards,
    every time, without exception.

## Prerequisites

- [Motor ID and config](motor-id-and-config.md) complete, including the 5 %
  smoke test.
- Robot suspended, legs hanging straight, e-stop held.
- Motors **not** enabled — the joints must be back-driveable so you can position
  them by hand.

## The zero pose

!!! missing "MISSING — Zero pose: figure, per-joint angle table, holding method and fixture"
    **The zero pose is not defined anywhere in this release.** This is the
    blocking item on the page, and no amount of care with the tooling
    compensates for it.

    What is needed:

    - A **figure** of the robot in the zero pose, from at least two views.
    - A **per-joint angle table**: joint name, the mechanical feature that
      defines its zero, and the angle in the robot model. "Standing straight" is
      not a specification; "the hip roll axis zero is where the machined face of
      the hip bracket is parallel to the pelvis plate" is.
    - How each joint is **physically held** at zero while the script runs: hard
      stop, machined witness face, dowel pin, or a fixture.
    - If a **zeroing fixture** is needed, it belongs in the BOM and in the CAD
      release. It is in neither today.
    - The order to do the joints in, since holding 31 joints simultaneously is
      not possible for one person.

    *Owner: hardware lead + controls lead.*

!!! note "Watch the wrists"
    The wrist encoders have a known ±π wrap, which the hardware choreography tool
    works around by capping its sweep. A wrist zeroed close to that boundary will
    wrap during normal motion. When the zero pose is defined (**TODO**{ .dh-missing }), it should place the
    wrists well away from the wrap, and the definition should say so explicitly.

## Verifying a zero

A zero set by hand must be checked by something other than the hand that set it.
Three independent checks exist, in increasing strength.

{{ step(1, "Ramp every joint to zero under power") }}

```bash
python humanoid_config.py --zero
```

This ramps all joints to their zero at a **10 % torque ceiling**, on a smooth
300-step profile at 200 Hz, publishing telemetry as it goes. What you are
watching for is the physical robot arriving at the pose your figure shows (the
zero-pose figure does not exist yet: **TODO**{ .dh-missing }, see
[The zero pose](#the-zero-pose)). A joint that ends up somewhere else was zeroed
somewhere else.

!!! danger "Low torque, but it is 31 joints moving at once"
    Suspended, clear, e-stop in hand. 10 % of an RS04's torque is still enough to
    trap a finger.

{{ step(2, "Check the camera gimbal zeros") }}

```bash
python humanoid_gimbal_zero_check.py
```

Read-only, a few seconds, commands nothing. It prints where the robot model
believes each camera is looking, given the live encoders; you then look at the
physical robot. Agreement means the gimbal zero survived. Disagreement gives you
the offset directly.

It needs `humanoid_real_env.py` up in any profile that publishes telemetry — the
arm need not be powered.

{{ step(3, "Check the model against measured gravity torque") }}

```bash
python humanoid_mass_check.py
```

This holds the arm still, reads measured joint effort and position, and compares
them against the gravity torque the model predicts at the **measured** posture.
It was written to settle a question about the deploy model's arm masses, but it
is also the strongest end-to-end check available that the robot's joint angles
and the model's joint angles mean the same thing.

Note its own caveat: only `shoulder_2`, `shoulder_3`, `elbow` and `wrist_1` carry
meaningful gravity load in a hanging arm. The other joints sit near their own
gravity null and are reported but not scored. A residual that **grows from the
wrist down to the shoulder** localises the offending link — every joint carries
everything distal to it.

{{ checkpoint("Every joint's measured position at the defined zero pose matches the robot model, the gimbal zero check agrees with what the cameras are physically pointing at, and the offsets are saved to the drives and backed up.") }}

## Backing up the zeros

!!! missing "MISSING — Backing up, restoring and replacing the 31 zero offsets"
    The zeros live in the drives' non-volatile memory. Publish:

    - **How to read all 31 offsets back out** into a file.
    - Where that file should live and how it is restored to a replacement drive.
    - What happens to the zero when a drive is replaced, and therefore what a
      builder must redo after swapping one actuator.

    Re-zeroing 31 joints by hand because a drive was swapped, or because a
    configuration was lost, is a day of work and a fresh opportunity to introduce
    a systematic error. There is no reason for it to be unrecoverable.

    *Owner: controls lead.*

## Accuracy

!!! missing "MISSING — Zeroing accuracy target per joint"
    The zeroing accuracy achieved per joint on the reference robot, and what a
    builder should do about a joint that cannot be zeroed to it. Without a target
    number, a builder has no way to know whether the hand-positioned zero they
    just committed is good enough for the published policy to transfer.

    *Owner: controls lead + hardware lead.*
