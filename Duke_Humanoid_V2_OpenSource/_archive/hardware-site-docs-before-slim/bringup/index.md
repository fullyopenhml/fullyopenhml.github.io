# Bring-up

Turning an assembled, wired robot into a working one. The order is fixed: power,
then motor identity, then joint zeros, then cameras, then acceptance. Each stage
assumes the previous one passed.

1. [First power-on](first-power-on.md)
2. [Motor ID and config](motor-id-and-config.md)
3. [Joint zeroing](joint-zeroing.md)
4. [Camera calibration](camera-calibration.md)
5. [Acceptance tests](acceptance-tests.md)

!!! danger "The robot hangs for all of this"
    The onboard control stack's own operations guide assumes the robot is
    suspended during bring-up, and the joints are quasi-direct-drive: cutting
    power drops the machine. Nothing here is done free-standing.

    Hang it with the **legs straight**. A bent-leg hang tilts the torso and
    corrupts the body-frame geometry every downstream stage depends on; it is
    operational rule #0 in the runbook and it cost three sessions before it
    became a rule.

## Before you start

- [Pre-power checks](../electrical/pre-power-checks.md) passes in full, signed.
- The control stack is installed and builds on the robot computer. That is a
  software job with its own document — read
  [`control/docs/SETUP.md`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/docs/SETUP.md)
  in the deploy repository first, and see [Software](../software.md).
- You have read
  [`control/docs/OPERATIONS.md`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/docs/OPERATIONS.md),
  the operator runbook, end to end. This section does not duplicate it; it tells
  you what is specific to a robot that has never been powered.

## The division of labour

| Document | Covers |
| --- | --- |
| This section | A newly built machine: proving the hardware, once |
| [`SETUP.md`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/docs/SETUP.md) | Installing and building the control stack on the robot computer |
| [`OPERATIONS.md`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/docs/OPERATIONS.md) | Running the robot, every session, once it works |
| [`auto_operator_incidents.md`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/docs/auto_operator_incidents.md) | What has gone wrong on this hardware and what now prevents it |

Read the incident register before you move an arm. Ten entries, each with what
happened, why, and the mechanism that stops it recurring. It is the shortest
route to understanding which of this machine's behaviours are deliberate.

## The bring-up toolkit

Everything below ships in the deploy repository under `control/`. Ordered
roughly by how much energy it puts into the robot — work down the list, never
skip ahead.

| Tool | Enables motors? | What it does |
| --- | --- | --- |
| `humanoid_setup_can.py` | No | Brings the six CAN buses up; reports what refused |
| `humanoid_motor_temps.py` | **No** | Read-only: temperature and bus voltage for every motor |
| `humanoid_dropout_probe.py` | No (passive mode) | Reads motor RAM after a fault without disturbing the evidence |
| `humanoid_profile_motor_latency.py` | 1 % torque ceiling | Per-motor CAN round-trip latency, per bus |
| `humanoid_config.py` | Self-check only | Motor table; run directly it self-checks every motor. `--zero` ramps to zero at a 10 % torque ceiling |
| `humanoid_set_current_limit.py` | Writes limits | Sets per-motor current limits and saves them to the drives |
| `humanoid_set_zero.py` | Writes zeros | **Destructive**: writes the current position of every motor as its zero |
| `humanoid_test_motor.py` | 5 % torque ceiling | Small sine on the arm joints **UNVERIFIED**{ .dh-unverified } — which joints it drives is in doubt, see [Motor ID and config](motor-id-and-config.md#verifying-the-configuration). The repository's own first power-on smoke test |
| `humanoid_wiggle_watch.py` | No | Live dropout alarm for the harness wiggle test |
| `humanoid_gimbal_zero_check.py` | No | Is the camera-gimbal encoder zero still calibrated? |
| `calibrate_cam_gear.py` | Moves one gimbal | Measures the real motor-to-camera gear ratio |
| `humanoid_monitor.py --record-handeye` | No | Records hand-eye calibration data |
| `humanoid_handeye_calibration.py` | No | Solves the hand-eye calibration |
| `humanoid_mass_check.py` | Holds a pose | Verifies the deploy model's arm masses against the real arm |
| `humanoid_static_stand.py` | 30 % torque ceiling | Scripted arm poses over zeroed legs |
| `humanoid_grip_slip_test.py` | Gripper only | Finds the grip torque at which a cube stops slipping |
| `humanoid_stage_walk_test.py` | Arm, crawl rate | Walks one arm through the staged transit postures |
| `humanoid_nav_step_test.py` | Legs | One commanded velocity step. The first hardware walk |

!!! note "One owner per CAN bus"
    Almost every tool above talks to the motors directly. Stop
    `humanoid_real_env.py` before running any of them. Two clients on one bus
    produces symptoms indistinguishable from a harness fault.
