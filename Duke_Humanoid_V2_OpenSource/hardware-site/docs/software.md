# Software

| Repository | Use |
| --- | --- |
| [`duke_humanoid_v2`](https://github.com/generalroboticslab/duke_humanoid_v2) | Umbrella: README, citation, licence, submodules |
| [`duke_humanoid_v2_simulation`](https://github.com/generalroboticslab/duke_humanoid_v2_simulation) | Training, paper reproduction, robot model |
| [`duke_humanoid_v2_deploy`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy) | Control stack on the robot |

```bash
git submodule update --init --recursive   # umbrella cloned without submodules
```

The cuRobo plan/MPC (model-predictive control) server needs a separate GPU
machine, not in the bill of materials. The robot computer needs no CUDA.

## Robot computer setup

On-robot setup (flash CANables, name adapters, configure IMU, install
librealsense2, build `deploy/control`) lives in
[Bring-up · Robot computer setup](bringup/index.md#robot-computer-setup).

Deploy has no lower-body gravity compensation; the reinforcement-learning (RL)
policy stands the robot.

| Control | What deploy does |
| --- | --- |
| Gravity compensation | `humanoid_real_env.py --grav-comp` (off by default) adds a MuJoCo gravity feed-forward to the arm motors only; the ramp to the initial pose adds none |
| Standing | The RL policy drives the legs; `humanoid_auto_operator.py --no-walk` zeroes every velocity command so the robot balances in place |
| Bench stand | `humanoid_static_stand.py` holds legs and waist at zero under PD (kp 100, kd 8, 30 % torque ceiling) while the arms step through poses; no policy |

## Robot model

`simulation/asset/duke_v2/`: `humanoid_v21/`, `head_cam/`, `parallel_gripper/`.

The asset READMEs cite these paths, which are not in the export:

| README | Absent paths |
| --- | --- |
| `duke_v2/README.md` | `cartesian_hand/` (`cartesian_hand.xml`) |
| `humanoid_v21/README.md` | `humanoid_v21_high_res.xml`, `humanoid_v21_resolved.xml`, `meshes/source_stp/`, `cartesian_hand/`, `cartesian_hand_v2/`, `asset/robot_studio`, `tests/test_studio.py` |
| `cartesian_hand_v3/README.md` | `source/vertical_translation_v8.step`, `cold/` (`cold/cartesian_hand`, `cold/cartesian_hand_v2`, `../cold/README.md`), `mj_envs/asset_zoo/cartesian_hand_v3.py` |
| `head_cam/README.md` | `source/HeadCameraV2.step`, `source/HeadCameraV2_dual.step`, `meshes/components_high_res/` |
| `parallel_gripper/README.md` | `mini_gripper_old/ParallelGripper0710/` (`ParallelGripper0710.step`), `CNC.step` |

!!! note "Yours to check — a few asset READMEs cite paths absent from the export"
    Whether the files above will be published, and where a builder gets the
    STEP originals, is not stated.

    *Owner: controls lead.*

The model sets joint order, directions and link masses. Never machine from its
meshes; see [CAD downloads](fabrication/index.md#cad-downloads).

| Contract item | Where deploy sets it |
| --- | --- |
| Joint vector (index, name) | `motor_setup_dict` order in `deploy/control/humanoid_config.py`; table on [CAN bus](electrical/index.md#can-bus) |
| Encoder vs training frame | The calibrated `robot.xml` differs from the training model at three joints: `left_wrist_1` (−π/2 reference), `right_wrist_1` (+π/2 reference), `left_wrist_2` (axis flipped); `humanoid_real_env.py --obs-frame-fix` or `--lw2-mirror` (both off by default, mutually exclusive) rewrites the wrist observations the policy sees |
| Checkpoint | `humanoid_site.DEPLOY_TASK` (`…BankFlatDecoupledCosine`, `policy_deployed.pt`) runs on the calibrated `robot.xml` of `DEPLOY_MODEL_TASK` (`…v159bMixedArmsCam`); both ship in `deploy/control/legged_env_bundle/` |
| Fresh install | Deploy `control/docs/SETUP.md`: Python 3.12, `requirements.txt` pins, CMake ≥ 3.26, CAN, servo ports, hand-eye calibration, network, RealSense; the robot runs `torch` 2.9.1+rocm6.3 |

!!! note "Yours to determine — the OS, kernel and driver baseline you run"
    Still unknown: the positive rotation direction of each joint as a builder
    checks it on a freshly wired robot, which checkpoint matches which hardware
    revision, and the tested OS, kernel, driver and firmware versions.

    *Owner: controls lead.*

Code is Apache-2.0; see [Citation and licence](reference/index.md#citation-and-licence).