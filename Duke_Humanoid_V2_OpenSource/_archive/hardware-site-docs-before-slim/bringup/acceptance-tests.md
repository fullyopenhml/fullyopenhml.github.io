# Acceptance tests

The tests that say a newly built robot is the same machine as the reference one.
Without these, a builder has an assembled robot and no way to know whether it
works — which is the difference between open hardware and a photo album.

## How to use this page

Eleven tests, ordered so that each one puts more energy into the machine than the
one before it. **Run them in order. Do not skip.** A test that fails is a stop:
fix the cause, then re-run that test and everything after it.

Every test below is run with the robot **suspended, legs hanging straight**,
until A8 says otherwise.

| ID | Test | Proves | Risk |
| --- | --- | --- | --- |
| [A0](#a0-physical-conformance) | Physical conformance | You built the right machine | None |
| [A1](#a1-bus-integrity) | Bus integrity | All 31 actuators are reachable | None — nothing enabled |
| [A2](#a2-can-latency) | CAN latency | The buses are fast enough for a 200 Hz loop | 1 % torque |
| [A3](#a3-harness-robustness) | Harness robustness | No intermittent connection | None — motors off |
| [A4](#a4-per-joint-motion) | Per-joint motion | Every joint moves, correctly, alone | 5 % torque |
| [A5](#a5-zero-and-model-fidelity) | Zero and model fidelity | The robot and the model agree | 10 % torque |
| [A6](#a6-perception) | Perception | The cameras agree with the robot | Gimbals only |
| [A7](#a7-grippers) | Grippers | The hands hold a known object | Gripper only |
| [A8](#a8-whole-body-posture) | Whole-body posture | 27 joints coordinate under load | 30 % torque |
| [A9](#a9-arm-transit) | Arm transit | The audited staging chain runs on your geometry | Crawl rate |
| [A10](#a10-reach-and-grasp) | Reach and grasp | The headline capability | Full stack |
| [A11](#a11-walking) | Walking | Free locomotion | Highest |

!!! missing "Reference values are the missing half of this page"
    **Reference values from the original robot are the missing half of this
    page.** Several tests below have a tool and a procedure but no number to
    compare against, and a test without a published reference cannot tell a
    builder whether their machine matches the paper's machine — only that it did
    something.

    Every `— TODO` in a *Pass* column on this page is one measurement on the
    reference robot away from being closed. Each one is itemised in its own
    box below.

    *Owner: controls lead. This page is the gate on the whole build.*

---

## A0. Physical conformance

Before anything is energised. A scale, a tape measure, and the published
specification.

| Quantity | Published value | Measured | Tolerance |
| --- | --- | --- | --- |
| Total mass | 36 kg | | **TODO**{ .dh-missing } |
| Height | 1.2 m | | **TODO**{ .dh-missing } |
| Arm reach | 0.46 m | | **TODO**{ .dh-missing } |
| Leg length | 0.39 m | | **TODO**{ .dh-missing } |
| Gripper mass, each | 350 g | | **TODO**{ .dh-missing } |
| Degrees of freedom | 31 | | exact |
| Actuator count by model | 2 / 6 / 11 / 2 / 6 / 4 (RS00 / RS02 / RS03 / RS04 / RS05 / RS06) | | exact |

Published values are from the hardware table in the
[project README](https://github.com/generalroboticslab/duke_humanoid_v2). The
actuator counts cross-check against both the purchasing BOM and the control
stack's motor table.

The team weighed several actuators with and without the rear cover. They all
came out above the vendor figures; whether the readings include the cable
pigtails is not recorded.

| Actuator | Team scale, with cover | Without cover | Vendor figure |
| --- | --- | --- | --- |
| RS02 | 404 g | 396 g | 380 ± 3 g (manual) |
| RS03 | 909 g | 893 g | 880 ± 20 g (manual) |
| RS04 | 1496 g | 1439 g | 1420 ± 20 g (manual) |
| RS06 | 614 g | 599 g | 0.63 kg (team motor specification) |

*Source: team teardown photos and design log; RobStride RS02, RS03 and RS04
manuals.* Use them as a sanity check on a single actuator, not as a tolerance.

**Why this is first**: mass is the input to gravity compensation and to the
policy's dynamics. A robot 4 kg heavier than the reference is not a robot that
works slightly worse; it is a robot the published policy was not trained for. If
your mass is off, find out now rather than at A8.

!!! missing "MISSING — A0 tolerances and a mass breakdown by subassembly"
    Tolerances for every row, and a **mass breakdown by subassembly**, so a
    builder whose total is wrong can find out where. Note that the deploy model
    carries a 967 g cable-mass compensation that exists only in the exported
    model and in no committed source — a builder whose harness differs will have
    a mass the model does not know about.

    *Owner: hardware lead.*

---

## A1. Bus integrity

```bash
cd <deploy-repo>/control
python humanoid_setup_can.py
python humanoid_motor_temps.py
```

| Check | Pass |
| --- | --- |
| CAN buses up | All six report **ERROR-ACTIVE** |
| Actuators answering | **31 of 31**, no row marked *no feedback yet* |
| ID and bus per actuator | Exact match to the [actuator map](../electrical/can-bus.md#the-actuator-map) |
| Bus voltage | Every motor within the supply's tolerance of the expected bus voltage (not yet published: **TODO**{ .dh-missing }, see [Power system](../electrical/power-system.md)) |
| Temperature | All near ambient |
| Repeatability | Passes from a cold power cycle, three times in a row |

**Abort**: any bus in ERROR-WARNING, any error frame, fewer than 31 answers.

Three cold cycles matters more than one. A bus that comes up two times out of
three is a fault, and it will not become less of a fault under load.

---

## A2. CAN latency

```bash
python humanoid_profile_motor_latency.py
```

Runs the control loop at a 1 % torque ceiling with no position command, then
prints average, standard deviation, min, max and p99 round-trip latency per motor
and per bus.

| Check | Pass |
| --- | --- |
| Per-bus average latency | **TODO**{ .dh-missing } |
| Per-bus p99 latency | **TODO**{ .dh-missing } |
| Spread across motors on one bus | **TODO**{ .dh-missing } |
| Headroom against the 200 Hz motor loop | **TODO**{ .dh-missing } |

!!! missing "MISSING — A2 reference latency figures and pass thresholds"
    The reference latency figures. The motor loop runs at 200 Hz — a 5 ms budget
    — so there is a number above which a bus cannot keep up, and it is not
    written down. Publish the reference robot's per-bus figures and the threshold
    at which a builder should suspect their harness.

    *Owner: controls lead.*

---

## A3. Harness robustness

The test that catches the fault that ruined the reference robot's July.

```bash
python humanoid_wiggle_watch.py
```

Motors unpowered. Work along the entire harness — every connector, every clamp,
every limb entry and exit — pressing, wiggling and flexing, while keeping the
limb stirring so the detector has a valid reference. Full instructions on
[Routing](../electrical/routing.md#verifying-a-routing-job).

| Check | Pass |
| --- | --- |
| Dropout alarms during a full harness sweep | **Zero** |
| Repeat on the opposite limb | Zero |

**Abort**: a single alarm. One dropout found by hand is an unknown number of
dropouts under load. Find it, fix it, re-run A1 through A3.

---

## A4. Per-joint motion

```bash
python humanoid_test_motor.py
```

The repository's own smoke test: 5 % torque ceiling, 0.1 rad sine on the arm
joints at 300 Hz. Which joints it actually drives is **UNVERIFIED**{ .dh-unverified } — see
[Motor ID and config](motor-id-and-config.md#verifying-the-configuration).

| Check | Pass |
| --- | --- |
| The commanded joints move | Every arm joint responds **UNVERIFIED**{ .dh-unverified } |
| No other joint moves | Confirmed visually **UNVERIFIED**{ .dh-unverified } |
| Direction | Each joint moves the way the direction convention says (the convention does not exist yet: **TODO**{ .dh-missing }) |
| Tracking error | **TODO**{ .dh-missing } |
| Current draw per joint | **TODO**{ .dh-missing } |
| Noise | No grinding, knocking or binding from any joint |

!!! missing "Direction is the one to watch"
    A joint configured backwards passes A1, A2 and A3 and then inverts a feedback
    loop under policy control. The direction convention itself does not exist
    yet — it is tracked as a safety item on
    [Motor ID and config](motor-id-and-config.md#direction-convention).

!!! missing "MISSING — A4 motion test for legs, waist and gimbals; reference tracking and current; range-of-motion sweep"
    - The shipped smoke test drives **arm joints only**. An equivalent for the
      legs, waist and gimbals is needed, or this test covers 14 of 31 joints
      **UNVERIFIED**{ .dh-unverified } (the joint count depends on the open question of which joints the
      smoke test drives).
    - Per-joint tracking error and current draw from the reference robot, so
      "it moved" can become "it moved correctly".
    - A **full range-of-motion sweep** per joint, one joint at a time, with each
      joint's travel limits published. A0 says you built the right parts; nothing
      yet says they assembled into the right travel.

    *Owner: controls lead.*

---

## A5. Zero and model fidelity

```bash
python humanoid_config.py --zero      # ramp to zero, 10 % torque ceiling
python humanoid_mass_check.py         # measured gravity torque vs the model
```

| Check | Pass |
| --- | --- |
| Robot reaches the defined zero pose | Matches the zero-pose figure (neither the pose nor the figure exists yet: **TODO**{ .dh-missing }, see [Joint zeroing](joint-zeroing.md#the-zero-pose)) |
| Gravity-torque residual at `shoulder_2` / `shoulder_3` / `elbow` / `wrist_1` | **TODO**{ .dh-missing } |
| Residual pattern | Does **not** grow monotonically from wrist to shoulder |

A residual that grows from the wrist down to the shoulder localises a mis-massed
link: every joint carries everything distal to it. The other joints sit near
their own gravity null and are reported but not scored.

!!! missing "MISSING — A5 acceptable gravity-torque residual per joint"
    The acceptable residual. This is the strongest available end-to-end check
    that your robot and the model agree about geometry and mass, and it currently
    has no threshold. Publish the reference robot's residuals per joint.

    *Owner: controls lead.*

---

## A6. Perception

Both camera modules. Full procedure on
[Camera calibration](camera-calibration.md).

| Check | Pass |
| --- | --- |
| Camera-to-port mapping | Survives a power cycle and a replug |
| USB link | Both cameras at `5000M` in `lsusb -t` |
| Depth range | Produces depth across the specified 0.1–3.0 m |
| Gimbal zero, both modules | Model's predicted look direction agrees with the physical robot |
| Hand-eye translation residual | mean ≈ 2.3 mm, max ≈ 8.1 mm **UNVERIFIED**{ .dh-unverified }; **hard fail above 20 mm** |
| Hand-eye rotation residual | mean ≈ 0.21°, max ≈ 0.89° **UNVERIFIED**{ .dh-unverified }; **hard fail above 5°** |
| Valid frames per port | ≥ 100; **hard fail below 50** |
| Solve verdict | `VALID`, and the YAML is confirmed applied rather than silently rejected |
| Gimbal tracking a moving target | **TODO**{ .dh-missing } |

The hand-eye figures are the reference rig's; treat them as the target rather
than as a guaranteed outcome, and treat the hard-fail thresholds as absolute.
Where those reference figures come from is itself unconfirmed
(**UNVERIFIED**{ .dh-unverified }) — see
[Camera calibration](camera-calibration.md#4-hand-eye-extrinsics).

!!! missing "MISSING — A6 gimbal tracking test, with tracking-error and lag figures"
    A **gimbal tracking test**: both modules following a moving target, with a
    tracking error and a lag figure. Coordinated gaze is the robot's headline
    capability and there is currently no acceptance test for it at all.

    *Owner: perception lead.*

---

## A7. Grippers

```bash
python humanoid_grip_slip_test.py --side left
python humanoid_grip_slip_test.py --side right
```

Per torque level, high to low: full squeeze, settle, hold at the level, then an
8-second window in which you tug the object the way a carry would load it.

| Check | Pass |
| --- | --- |
| Open and close, both grippers | Full travel, both sides |
| Lowest hold level with **zero** slip | Recorded, per side |
| Carry and park torques | Set to about 1.5× the lowest no-slip level |
| Left/right symmetry | **TODO**{ .dh-missing } |
| Cycle endurance | **TODO**{ .dh-missing } |

!!! missing "MISSING — A7 reference no-slip levels, test object, symmetry and endurance criteria"
    The reference robot's no-slip levels, the test object's mass and surface, and
    how much asymmetry between the two hands is acceptable. "Lowest level with
    zero slip" is a good procedure attached to no published result.

    The *Cycle endurance* row has neither a procedure nor a pass criterion:
    how many open-close cycles, at what load, and what counts as a failure.

    *Owner: controls lead.*

---

## A8. Whole-body posture

The first time all 27 body joints are driven together.

```bash
python humanoid_static_stand.py     # 30 % torque ceiling, arm poses over zeroed legs
```

Then the real stack, still suspended:

```bash
python -u humanoid_real_env.py --task <deploy-task> \
  --torque-limit 0.8 --enable-motor true --no-use-ik --grav-comp --ee-service \
  --arm-sender-ip 127.0.0.1 --high-level-controller-ip 127.0.0.1 2>&1 | tee /tmp/realenv.log
```

| Check | Pass |
| --- | --- |
| Scripted poses reached | All, smoothly, no binding |
| **Two minutes suspended under the policy** | **No `WATCHDOG` banner** |
| Torso tilt gate | No `TORSO-TILT` refusal at startup or during the 5 s tilt watch |
| Motor temperatures after the run | **TODO**{ .dh-missing } |
| Current draw standing | **TODO**{ .dh-missing } |

RobStride's protection defaults are a motor over-temperature **fault at 80 °C**
and a **warning at 75 °C**; the driver board is rated to 80 °C. The parameter is
stored as temperature × 10. The manual warns against changing the torque limit,
protection temperature or over-temperature time. *Source: RobStride RS03 manual
fault and parameter tables; the RS02 and RS04 manuals give the same fault and
warning defaults.*

!!! unverified "UNVERIFIED — RS04 over-temperature setting: 1450 on the bench unit vs the 80 °C default"
    The team's RS04 bench unit read `motorOverTemp` 1450, which at the × 10
    scale is 145.0 °C (computed), against the vendor's 80 °C fault default. It
    is not known whether the robot's drives carry the same value. Read it back
    from every drive before trusting the fault as a thermal limit.

    *Owner: controls lead.*

!!! missing "MISSING — A8 reference motor temperatures after the run, and standing current draw"
    The last two rows of the table above have no pass value. Publish, from the
    reference robot under the same two-minute suspended run: each motor's
    temperature at the end of the run (or the rise from ambient), and the
    motor-bus current while the policy holds the robot, each with the value
    that counts as a failure.

    *Owner: controls lead.*

!!! danger "Two minutes, watching, before anything else"
    The runbook is explicit: stand it two minutes watching for the watchdog
    banner before any further step. This is where a marginal harness, a bad zero
    or a wrong mass finally shows itself, and it shows itself on a machine that is
    holding its own weight.

!!! note "If the tilt gate refuses"
    It is refusing because the robot is hanging tilted, which corrupts the
    body-frame geometry end to end — table objects read at chest height, the
    learned gate goes out of distribution, the IK diverges from the commanded
    frame. Straighten the hang. Do not widen the envelope; incident INC-4 in the
    register is four separate sessions lost to exactly this.

---

## A9. Arm transit

```bash
python humanoid_stage_walk_test.py
```

Walks one arm through the audited staged transit postures — front, side, rear,
side, front — in joint space, at the failsafe crawl rate of 0.025 rad/s. Slow on
purpose: the biggest hop takes about 89 s and the full out-and-back about 4.5
minutes **UNVERIFIED**{ .dh-unverified } (estimates; no timed run is published).

| Check | Pass |
| --- | --- |
| Full out-and-back completes | Both arms, separately |
| Clearance | No contact with the torso, the other arm, or itself, at any point |
| Ctrl+C failsafe | Arm ramps back to the power-on pose at the crawl rate |
| Joint limit margins | Offline audit certifies ≥ 40°; confirm nothing on your build is tighter |
| Arm-to-everything clearance | Offline audit certifies ≥ 49.9 mm; confirm on your build |

The certified margins above were computed for the reference geometry. If your
build differs — a different harness, a different camera mount, a printed part at
a different tolerance — they are the numbers to re-verify, not to assume.

!!! missing "MISSING — A9 launch conditions for the stage-walk test"
    This section gives the bare command and nothing else. It does not say what
    must already be running when the test starts, how the arm under test is
    selected (the *Pass* column asks for both arms, separately), or at what
    torque ceiling and motor group the robot should be enabled for it. The
    script's own usage notes are the place to start; reconcile them with this
    page and write the full invocation here.

    *Owner: controls lead.*

---

## A10. Reach and grasp

<figure markdown>
  <video class="dh-clip" autoplay loop muted playsinline preload="metadata" width="800" height="450" poster="../../assets/images/two_target_handoff_left_right-poster.webp" aria-label="The reference robot grasping one target from a bench while a person holds the second">
    <source src="../../assets/images/two_target_handoff_left_right.mp4" type="video/mp4">
    <a href="../../assets/images/two_target_handoff_left_right.mp4">The reference robot grasping one target from a bench while a person holds the second</a>
  </video>
  <figcaption>
    What passing A10 looks like on the reference robot: one target on a bench,
    one held by a person, each camera module tracking its own. If your machine
    does this, you have built this machine.
  </figcaption>
</figure>

The headline capability, and the point at which this page hands off to the
operator runbook. Do not reinvent it here: follow
[`control/docs/OPERATIONS.md`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/docs/OPERATIONS.md)
section 2, the terminal ladder T0 through T6, exactly.

Acceptance checks along that ladder:

| Stage | Check | Pass |
| --- | --- | --- |
| T0 | CAN buses | All six ERROR-ACTIVE |
| T1 | Camera server | Both streams up; port order matches the serials |
| T2 | Gripper service | `Connected left/right hand`, both |
| T3 | `real_env` | Two minutes suspended, no watchdog |
| T4 | Monitor | First line includes `[detection] publishing detected targets` |
| T5 | Plan server probe | **Three PASS lines** |
| T6 | Grasp, dry run first | Gates-only run passes before `--execute` |
| T6 | Grasp, executing | **TODO**{ .dh-missing }: success rate over N attempts |

Placement is not a detail — it is derived from the hardware and the runbook says
not to guess it:

- Objects rotated about 45° so **two** tag faces are visible. One-face evidence is
  the leading cause of off-centre grasps and mid-track freezes.
- Front-left object at **|y| ≥ 0.15 m**. Midline placements are rejected by a
  gate and simply burn plan retries.
- Object **z ≥ 0.09 m**, in the MPC-validated radial band of about **0.45–0.55 m**.

When it aborts, it prints a coded `[verdict]` banner naming the trigger and the
culprit, and the run ends with a tally. Triage from the runbook's table: recurring
executor or follow triggers point first at **wiring or torque**; envelope or
no-progress triggers point at **perception** — tag faces and placement; a
clearance-standoff trigger means the object is too close to the torso.

!!! missing "MISSING — A10 reference grasp success rate over a stated number of attempts"
    The **success rate the reference robot achieves** on the standing two-object
    grasp, over a stated number of attempts, with the placement above. This is
    the single number that tells a builder their robot matches the paper's robot,
    and it is the most important missing value on this site.

    *Owner: controls lead.*

---

## A11. Walking

The last and highest-risk test. First free locomotion.

```bash
python humanoid_nav_step_test.py
```

One commanded velocity step, measured, rather than a gamepad — a stick cannot
hold a steady velocity or stamp the release instant, and pushing it far enough
latches a manual-control pause that makes the run meaningless.

| Check | Pass |
| --- | --- |
| Commanded step executes | Robot walks, hoist slack, nobody in the path |
| Coast distance after command drops to zero | **TODO**{ .dh-missing } — the constant that pays for it was estimated, never measured **UNVERIFIED**{ .dh-unverified } |
| Post-stop yaw rate | Recorded and compared against the stack's stillness threshold of 0.10 rad/s **UNVERIFIED**{ .dh-unverified }. The tool exists because that threshold is untested — record the trace rather than assuming it passes |
| Safety layers, verified before the run | Ctrl+C zeroes; process death zeroes after 1.0 s; gamepad seizes control; physical e-stop (not in the parts list or specified anywhere: **TODO**{ .dh-missing }, see [Power system](../electrical/power-system.md#protection-disconnect-and-e-stop)) |

!!! missing "MISSING — SAFETY — A11 coast distance after a stop, and the coast constant behind it"
    The distance the robot travels after the commanded velocity drops to zero
    has no published value and no pass threshold, and the constant the stack
    uses to account for it was estimated, never measured. This is the number
    that decides how much clear floor a walking test needs and how far people
    must stand from the robot's path.

    Measure the coast distance on the reference robot, publish it with the pass
    threshold, and state whether the constant was re-derived from the
    measurement.

    *Owner: controls lead.*

!!! unverified "UNVERIFIED — A11 post-stop stillness threshold of 0.10 rad/s"
    The stack treats a yaw rate below 0.10 rad/s after a stop as still. The
    page itself says this threshold is untested, and that
    `humanoid_nav_step_test.py` exists to test it. Confirm it by recording
    post-stop yaw-rate traces on the reference robot and publishing them next
    to the threshold, or publish a corrected value.

    *Owner: controls lead.*

!!! danger "Everything before this was suspended"
    A8 was the first time the machine held its own weight. A11 is the first time
    it moves across a floor with people in the room. Hoist attached and slack,
    path clear, e-stop held, and the four safety layers above confirmed in that
    order before the first command.

!!! note "Walk-based missions are the least mature mode"
    The maintainers are explicit that walk-then-grasp missions have run on
    hardware but succeed far less often than the standing grasp, that their
    arrival and coast constants are rig-specific and were tuned individually, and
    that 30 mm tags are undecodable past about 2 m **UNVERIFIED**{ .dh-unverified }. Expect to re-tune. Treat A11
    as the beginning of that work rather than as a pass/fail gate on your build.

---

## Offline, no hardware required

Run these before you touch the robot, and again after any software change:

```bash
cd <deploy-repo>/control && python -m unittest discover -s tests
```

Some modules error at import until the C++ extensions are built, and some tests
skip when cuRobo or the deploy model is absent; the repository README states the
expected result.

## Before you declare the robot working

Read
[`auto_operator_incidents.md`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/docs/auto_operator_incidents.md).
Ten entries, each with what happened on hardware, the root cause, the mechanism
that now prevents it, and the "simplification" that would bring it back. A robot
that passes A0 through A11 is a robot that works today; that document is how it
keeps working.

{{ checkpoint("Every acceptance test passes against the published reference values. Until then the robot is a test article, not a robot.") }}
