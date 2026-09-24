# Camera calibration

Two RealSense D436 units, each on its own 2-DoF yaw-pitch gimbal. This is the
calibration the whole visible-reachable-workspace argument depends on: if the
cameras do not agree with the robot about where things are, the machine is a
well-built statue.

Both cameras are labelled **D436** in the
[team data wiring diagram](../electrical/can-bus.md#the-team-data-wiring-diagram),
both on USB Hub #1. The D436 needs **librealsense 2.58.1** or later, the release
that adds D436 support. The team upgrades `librealsense2`, `-utils`, `-dev`,
`-gl`, `-udev-rules` and `-dbg` to 2.58.1 from the RealSense apt repository
(`https://librealsense.realsenseai.com/Debian/apt-repo`, signed with the key at
`https://librealsense.realsenseai.com/Debian/librealsenseai.asc`), comments out
the old Intel repository, and reloads udev so the camera gets USB permissions.
The deploy repository pins `pyrealsense2==2.58.1.10581` to match.
*Source: team design log, RealSense setup; team data wiring diagram (V2);
deploy `requirements.txt`.*

It is also four separate calibrations that are easy to confuse with each other.
Do them in this order — each one assumes the one above it is right.

| # | Calibration | Establishes | Tool |
| --- | --- | --- | --- |
| 1 | Camera identity | Which physical camera is which port | Serial numbers |
| 2 | Gimbal encoder zero | Encoder 0 means the camera looks straight ahead | `humanoid_gimbal_zero_check.py` |
| 3 | Gear ratio | Motor radians per camera radian | `calibrate_cam_gear.py` |
| 4 | Hand-eye extrinsics | Camera pose in the robot base frame | `humanoid_monitor.py` + `humanoid_handeye_calibration.py` |

Nothing here is shipped as data. Calibration is per-rig by nature: it describes
*your* camera bodies at *your* mount points. The deploy repository deliberately
ships the workflow and not the numbers.

## The two modules are not symmetric

One module is **forward-mounted** and one is **rear-mounted**. That is the
point of the design — it is what lets the robot see targets in front of and
behind itself without turning the whole body. It also means the two modules are
not interchangeable, and a calibration that is fine for one is meaningless for
the other.

| Port | Module | Model site | Gimbal joints |
| --- | --- | --- | --- |
| 5555 | LEFT, forward-mounted | `cam_left_rgb` | `cam_yaw_left`, `cam_pitch_left` |
| 5556 | RIGHT, rear-mounted | `cam_right_rgb` | `cam_yaw_right`, `cam_pitch_right` |

Source:
[`control/humanoid_gimbal_zero_check.py`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/humanoid_gimbal_zero_check.py)
and `control/docs/SETUP.md` §6.

!!! unverified "UNVERIFIED — Camera arrangement: forward and rear modules on two gimbals, or side by side on one"
    The sources disagree about the physical arrangement. The operator runbook's
    camera section describes both cameras as sitting
    "side by side on the head gimbal", while the gimbal check tool, the gear
    calibration tool and the port table all describe one forward-mounted and one
    rear-mounted module on two independent gimbals. The hardware overview in the
    project README also describes two independent 2-DoF gimbals.

    This page follows the tools, because they are the code that runs. Confirm the
    physical arrangement against your own build and against
    [Head and camera gimbal](../assembly/head-and-camera-gimbal.md), and get the
    runbook sentence corrected upstream.

    *Owner: perception lead.*

## 1. Camera identity

The most expensive mistake in this section is also the cheapest to prevent.

Everything downstream binds a camera by **port**, not by serial number: the tag
mounts, the site mapping, the gaze slots. If the two cameras swap ports, tags
land in the wrong camera frame and the gaze drives the wrong gimbal — and **every
log line still looks healthy**. There is no error. There is just a robot that
reaches for the wrong place.

With no configuration, the camera server takes the RealSense devices in USB
enumeration order, which can change across a replug or a power cycle.

{{ step(1, "Read both serial numbers") }}

```bash
rs-enumerate-devices -s
```

If Intel's `librealsense2-utils` is not installed, the Python wheel can do it:

```bash
python -c "import pyrealsense2 as rs; print([d.get_info(rs.camera_info.serial_number) for d in rs.context().query_devices()])"
```

{{ step(2, "Pin each serial to a port, once, per rig") }}

Set `CAMERA_SERIALS` in `perception/vs_site_local.py` — **left camera first** —
or pass `--devices <left-serial> <right-serial>` to the camera server. An
explicit `--devices` wins.

Note that `humanoid_site.CAMERA_SERIALS` also exists and has **no reader**. Set
the `perception` one.

{{ step(3, "Write the serials on the robot") }}

Physically label each camera with its serial and its side. You will need this
again every time a camera is replaced.

{{ checkpoint("Both camera serials are recorded in the rig configuration with the forward-mounted camera first, both cameras are physically labelled, and the port-to-camera mapping survives a power cycle and a replug.") }}

## 2. Gimbal encoder zero

Every AprilTag detection reaches the robot base frame through the gimbal's
forward kinematics, and that FK assumes exactly one calibrated fact: **encoder
zero means the camera looks straight ahead**.

```bash
python humanoid_gimbal_zero_check.py
python humanoid_gimbal_zero_check.py --robot-ip 127.0.0.1 --seconds 5
```

Read-only. It prints where the model believes each camera is looking, given the
live encoders, as an azimuth and elevation in the base frame; you then look at the
physical robot. Agreement means the gimbal zero is good, disagreement gives you
the offset directly. It also reports drift and noise over the sampling window, so
a wandering gimbal is obvious.

!!! danger "A whole-robot re-zero destroys this"
    [`humanoid_set_zero.py`](joint-zeroing.md) zeroes all 31 motors, including
    the four gimbal joints. If it is run for any reason — most likely to fix an
    arm — the gimbal zero is gone, and the failure mode is a stationary object
    reporting a *different* position on every run, because the error depends on
    where the gimbal happens to be pointing. Re-run this check after any zeroing
    operation.

!!! missing "MISSING — Procedure for setting the gimbal encoder zero, and its tolerance"
    The **physical procedure for setting** the gimbal zero, as opposed to
    checking it: what "straight ahead" is referenced against, what holds each
    gimbal there, and the acceptable error in degrees. The check tool tells you
    when it is wrong; nothing tells you how to make it right.

    *Owner: perception lead + hardware lead.*

## 3. Motor-to-camera gear ratio

There is a reduction between each gimbal motor and the camera it points, and the
real ratio is a property of your build, not a constant.

```bash
python calibrate_cam_gear.py
```

The principle is clean: hold a tagged cube fixed in view, move one gimbal axis by
an amount read exactly from the motor encoder, and measure how far the cube's
bearing in the image shifts. Then

```text
gear = -Δmech_pos / Δbearing        # motor-rad per camera-rad
```

The tool moves only the forward (left) camera, by small amounts — 0.4 rad yaw and
0.3 rad pitch on the **motor** side — on slow rate-limited ramps, returns to zero
and shuts down on exit. The rear camera is untouched.

Prerequisites: camera streaming on 5555, motors powered, CAN up, and **no**
`humanoid_real_env.py` or tracker running. Hold the tagged cube still in front of
the forward camera for the whole run.

!!! missing "MISSING — Rear-gimbal gear calibration, designed gear ratio, storage and tolerance"
    - The **rear (right) gimbal has no equivalent tool**. Either extend the tool
      or publish the manual procedure — the rear module cannot be left
      uncalibrated just because it is harder to see.
    - The **designed** gear ratio from the CAD, so a builder has something to
      compare the measured value against. A measured ratio that disagrees with
      the design is a build error, and right now there is nothing to disagree
      with.
    - Where the measured ratio is stored and how it is loaded.
    - The acceptable spread between the two axes and between the two modules.

    *Owner: perception lead.*

## 4. Hand-eye extrinsics

This refines the camera extrinsics and the tagged-cube mounting offsets from live
robot data, replacing hard-coded values. Full procedure:
[`control/docs/SETUP.md` §5](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/docs/SETUP.md).

**Prerequisites**: robot telemetry on port 9870, both cameras on 5555/5556, and
`tag_cube_0` / `tag_cube_1` bolted to the wrists.

All three commands run from `<deploy-repo>/control`, and everything lands in
`control/calibration/`, which is created on first use and is not shipped.

{{ step(1, "Record") }}

```bash
python humanoid_monitor.py --record-handeye
```

Ten-second countdown, then it records until you press Ctrl+C, saving on exit. A
live counter shows frames and valid detections per port.

While recording:

- Move **both** arms through at least **30° of rotation and 50 mm of translation
  at each wrist**.
- **Include wrist roll.** Without it, cube rotation about the camera axis is
  unobservable and the solve is underdetermined.
- Moderate speed. Fast motion is downweighted; slow static poses waste time.
- Both cubes visible from at least one camera simultaneously is ideal.
- Aim for **`n_valid ≥ 100` per port**. Observability warnings print if the
  motion was insufficient — read them rather than proceeding.

{{ step(2, "Solve") }}

```bash
python humanoid_handeye_calibration.py
```

Auto-selects the most recent recording, runs a linear warm start then a Huber
refinement, and writes `calibration/camera_handeye.yaml`.

Reference residuals from a good solve on the original rig
**UNVERIFIED**{ .dh-unverified }:

| Quantity | Reference | Hard failure |
| --- | --- | --- |
| Translation, mean | 2.3 mm | — |
| Translation, max | 8.1 mm | `> 20 mm` |
| Rotation, mean | 0.21° | — |
| Rotation, max | 0.89° | `> 5°` |
| Valid frames per port | aim `≥ 100` | `< 50` |

!!! unverified "UNVERIFIED — Provenance of the hand-eye reference residuals"
    The four reference figures above (2.3 mm, 8.1 mm, 0.21°, 0.89°) are
    presented as the result of a good solve on the original rig. Their only
    source found is the "Expected output" example listing in
    `control/docs/SETUP.md` §5, which may be illustrative rather than a
    recorded calibration of the reference robot. Acceptance test A6 uses the
    same figures as its targets.

    Confirm by locating the recorded solve (the YAML and its log) from the
    reference robot, or by re-running the calibration on it, and publish the
    date and rig the figures belong to. The hard-failure thresholds are the
    solver's own and are not in question.

    *Owner: perception lead.*

A run that trips any hard failure still **writes the YAML**, with
`calibration_valid: false`. Do not mistake the presence of a file for a
successful calibration.

If the warm start warns that the max rotation residual exceeds 15°, the cube is
physically twisted relative to the wrist. Measure the rotation and give the
solver an initial guess in radians:

```bash
python humanoid_handeye_calibration.py \
    --obj-rot-inits '{"tag_cube_0": [0.0, 0.0, 0.35]}'
```

Other useful overrides: `--logs` for explicit input files, `--output` for the
path, `--subsample` (default 5) for how many frames to use, and `--dq-thresh` /
`--v-link-thresh` for the motion-speed downweighting thresholds.

{{ step(3, "Apply") }}

```bash
python humanoid_monitor.py --handeye-yaml calibration/camera_handeye.yaml
```

!!! danger "An invalid calibration fails quietly"
    A YAML carrying `calibration_valid: false` is **silently ignored** — the
    monitor falls back to hard-coded defaults with a warning. If you are not
    reading the startup warnings, a failed calibration looks exactly like a
    successful one, and you will blame the robot for the next week.

    Check the solver's own output for `VALID` before you apply anything.

{{ checkpoint("Both cameras produce depth at the expected range, the hand-eye solve reports VALID with residuals within the reference figures above, and the applied YAML is confirmed loaded rather than silently rejected.") }}

## Intrinsics

!!! missing "MISSING — Whether D436 factory intrinsics are trusted or re-estimated"
    Whether the D436's **factory intrinsics are used as-is or re-estimated**, and
    if re-estimated, with what target and what procedure. Nothing in the released
    stack re-estimates them, which suggests the factory values are trusted — but
    "suggests" is not a decision, and a builder needs to know whether to trust
    them too.

    *Owner: perception lead.*

## The calibration fixtures

!!! missing "MISSING — Calibration fixtures: tag cubes, tag family and size, wrist mounts, artwork"
    The hand-eye procedure requires `tag_cube_0` and `tag_cube_1` **bolted to the
    wrists**, and the gear calibration requires a tagged cube held in view. These
    are fixtures, and they are in neither the BOM nor the CAD release.

    Publish: the cube geometry, the tag family and size, how each mounts to a
    wrist, and printable artwork. Note that the mission tooling elsewhere reports
    30 mm tags becoming undecodable past about 2 m, so tag size is a real design
    parameter and not an afterthought.

    Until this exists, a builder can follow every word of this page and still be
    unable to calibrate the robot.

    *Owner: perception lead. Blocks
    [CAD downloads](../fabrication/cad-downloads.md).*

## When to redo it

!!! missing "MISSING — Re-calibration triggers and intervals"
    A re-calibration trigger list with intervals: what invalidates a calibration
    (a replaced camera, a disassembled gimbal, a dropped robot, any whole-robot
    re-zero) and how often it should be redone even when nothing has changed.

    Two triggers are already certain from the sources above and can go in
    unchanged: **any run of `humanoid_set_zero.py`**, and **any replacement of a
    camera** — which also invalidates the serial-to-port mapping in step 1.

    *Owner: perception lead.*
