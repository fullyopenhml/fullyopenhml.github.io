# Acceptance tests

Run in order; each adds energy. On a failure, fix the cause and re-run from that test. Robot hung, legs straight, until A11.

| Test | Command | Pass |
| --- | --- | --- |
| A1 Bus integrity | `humanoid_setup_can.py`, then `humanoid_motor_temps.py`, from a cold power-up, three times | Six buses ERROR-ACTIVE and 31 answers every time; no error frames |
| A2 CAN latency | `humanoid_profile_motor_latency.py` (1 % torque) | Every bus well inside the 5 ms motor loop |
| A3 Harness wiggle | `humanoid_wiggle_watch.py` while flexing every connector, clamp and limb entry | Zero dropout alarms, both arms |
| A4 Per-joint motion | `humanoid_test_motor.py` (5 % torque) | Arm and gimbal joints move as commanded; nothing else moves; no grinding or knocking |
| A5 Zero and model | `humanoid_config.py --zero`, then `humanoid_mass_check.py` with `real_env` at `--torque-limit 0.4 --grav-comp` | Zero pose reached; `arm is static`; every residual `MATCH` (≤ 0.35 N·m) |
| A6 Perception | [Camera calibration](#camera-calibration) | Ports survive a power cycle; both cameras `5000M`; depth 0.1–3 m; gimbal zeros agree; hand-eye `VALID` |
| A7 Grippers | `humanoid_end_effector_service.py --gui` → **Zero Gripper** per hand (finds the closed stall); then `humanoid_grip_slip_test.py --side left` / `right` with a cube in the fingers | Full travel both hands; lowest no-slip hold level recorded per side |
| A8 Posture | `humanoid_static_stand.py`; then `humanoid_real_env.py --task <task> --torque-limit 0.8 --enable-motor true --no-use-ik --grav-comp --ee-service`, still hung | Poses reached smoothly; two minutes under the policy with no `WATCHDOG` or `TORSO-TILT` banner |
| A9 Arm transit | `humanoid_real_env.py … --torque-limit 0.2 --enable-motor arm --no-use-ik`, then `humanoid_stage_walk_test.py --arm left` / `right` | Each arm completes front → side → rear → side → front without contact; Ctrl+C returns it to the power-on pose |
| A10 Reach and grasp | `OPERATIONS.md` section 2, ladder T0–T6; objects at \|y\| ≥ 0.15 m, z ≥ 0.09 m, 0.45–0.55 m out, turned about 45° | T0–T5 pass, T6 dry run gates pass, then `--execute` grasps |
| A11 Walk | `humanoid_nav_step_test.py` on the floor, hoist attached and slack, path clear | Robot walks one velocity step and stops; Ctrl+C zeroes the command |

Before A11 confirm the software stop layers: Ctrl+C zeroes the command; process death zeroes after 1 s; the gamepad seizes control; stream silence fires the nav 1 s / arm 0.5 s / gaze 2 s failsafes. Pulling the pack connector is the last stop.
