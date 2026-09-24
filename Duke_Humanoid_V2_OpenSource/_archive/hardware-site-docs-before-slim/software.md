# Software

The code for this robot is already open and is **not** duplicated here. This page
is the bridge: which repository does what, in what order you meet them, what the
software expects the hardware to be, and which document to read before the
machine moves.

## The three repositories

| Repository | What it is |
| --- | --- |
| [`duke_humanoid_v2`](https://github.com/generalroboticslab/duke_humanoid_v2) | The umbrella. Project README, citation metadata, licence, and the two submodules below. Start here to understand the project; you will not run anything from it. |
| [`duke_humanoid_v2_simulation`](https://github.com/generalroboticslab/duke_humanoid_v2_simulation) | Policy training and the paper's reproduction package: the visible-reachable-workspace study, the two-target reach-and-grasp benchmark, the robot assets, and the checkpoints behind the published numbers. This is also where the **robot model** lives, which makes it relevant to a builder who has never trained anything. |
| [`duke_humanoid_v2_deploy`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy) | The onboard control stack: the 50 Hz policy loop, the perception bridge, the cuRobo planning client, the gripper service, and the autonomous operator. This is what runs on the robot you build. |

If you cloned the umbrella repository without its submodules:

```bash
git submodule update --init --recursive
```

The full project with both submodules is close to a gigabyte, most of it meshes
and recorded video. If you only want to reproduce the paper's figures, clone the
simulation repository alone; if you only want to run a finished robot, clone
deploy.

## When each one matters to a builder

| Stage | What you need from the software side |
| --- | --- |
| Before you buy | Nothing. Read the hardware pages. |
| During fabrication | The robot model, for cross-checking geometry — with the caveat below |
| Wiring | The CAN bus naming the control stack expects, so you label harnesses to match |
| First power-on | `deploy`'s setup documentation, then its operator runbook |
| Bring-up and acceptance | `deploy`, end to end |
| Changing behaviour | `simulation` |

## What the software expects your hardware to be

These are the points where a wiring decision on your bench has to match an
assumption in the code. Get them wrong and the robot is wired "correctly" and
still does not work.

**Six CAN buses.** Six CANable PRO V2.0 USB-to-CAN adapters, all at 1 Mbit/s:
can9 = left arm (left_shoulder_2, left_shoulder_3, left_elbow, left_wrist_1,
left_wrist_2, left_wrist_3); can21 = right arm (right_shoulder_2 to
right_wrist_3); can22 = waist, left_shoulder_1, right_shoulder_1; can23 = right
leg (right_hip_1–3, right_knee, right_ankle_1–2); can24 = left leg (left_hip_1–3,
left_knee, left_ankle_1–2); can25 = cam_yaw_left, cam_pitch_left, cam_yaw_right,
cam_pitch_right. The team data wiring diagram, deploy/control/humanoid_config.py
and the CAN bus page agree.
*Source: team data wiring diagram (V2); `deploy/control/humanoid_config.py`.*

Those names are what the setup script and the motor layer expect, so the
adapters get stable names from a `udev` rule keyed to each adapter's USB serial
rather than from plug order (see [Host setup](#host-setup-recorded-by-the-team)
below). Label the physical adapters to match the names before the harness goes
into the machine — see [CAN bus](electrical/can-bus.md).

**Three machines, not one.** The stack splits across a *robot computer* (runs
everything except the planner, needs no CUDA), a *GPU machine* running the cuRobo
plan and MPC server, and an *operator console*, which is any laptop with `ssh`.
The GPU machine is not part of the robot and is not in the robot's parts list.

**An ordered bring-up.** The operator runbook is a numbered ladder of
long-running processes with a stated reason for each ordering constraint, plus a
gates-only dry run before anything executes. It is not a single command, and the
order is not advisory.

## Host setup recorded by the team

These steps come from the team's own design log, for the robot computer that
talks to the adapters, the IMU and the cameras. They are what the team did on
Ubuntu; they are not a tested fresh-install procedure (that is still missing,
see the box at the end of this page).

### Prerequisites

```bash
sudo apt remove brltty                         # Ubuntu 22.04: brltty grabs USB-serial devices
sudo adduser $USER netdev                      # bring CAN interfaces up without sudo
sudo adduser $USER dialout                     # serial devices
sudo apt install can-utils libsocketcan-dev
modinfo gs_usb                                 # the candleLight driver is available
lsmod | grep can                               # and loaded
```

Log out and back in after the two `adduser` lines. With `brltty` installed,
`/dev/ttyUSB0` never appears (see
[askubuntu question 1403705](https://askubuntu.com/questions/1403705)). To find
the device node of something you have just plugged in, compare `ls -1 /dev`
before and after.
*Source: team design log, "CAN bus" host setup.*

### Adapter firmware: candleLight

The adapters must run **candleLight** (`gs_usb`) firmware. The team reflashes
them with the ElmueSoft
[CANable Firmware Update](https://netcult.ch/elmue/CANable%20Firmware%20Update/)
tool; the older canable.io web updater is marked deprecated in the log. Press
the button on the adapter to enter flash mode, and connect the adapter directly
to the computer. **UNVERIFIED**{ .dh-unverified }: the firmware version flashed
on the reference robot's adapters is not recorded.
*Source: team design log, "CAN bus".*

### Stable adapter names: the udev rule

Read each adapter's USB serial with `sudo dmesg`, `lsusb -v` or `usb-devices`,
then write one line per adapter to `/etc/udev/rules.d/99-candlelight.rules`.
That is the file `deploy/control/humanoid_setup_can.py` reads to map each
interface name to its adapter.

```text
SUBSYSTEM=="net", ACTION=="add", ATTRS{serial}=="<adapter-serial>", NAME="can9"
SUBSYSTEM=="net", ACTION=="add", ATTRS{serial}=="<adapter-serial>", NAME="can21"
SUBSYSTEM=="net", ACTION=="add", ATTRS{serial}=="<adapter-serial>", NAME="can22"
SUBSYSTEM=="net", ACTION=="add", ATTRS{serial}=="<adapter-serial>", NAME="can23"
SUBSYSTEM=="net", ACTION=="add", ATTRS{serial}=="<adapter-serial>", NAME="can24"
SUBSYSTEM=="net", ACTION=="add", ATTRS{serial}=="<adapter-serial>", NAME="can25"
SUBSYSTEM=="net", KERNEL=="can[0-9]*", GROUP="can", MODE="0660"
```

The team also uses a form that adds `ATTRS{idVendor}=="1d50",
ATTRS{idProduct}=="606f"` (the candleLight USB ID) to each line. Replace every
`<adapter-serial>` with your own adapter's serial. Then reload and replug:

```bash
sudo udevadm control --reload-rules && sudo systemctl restart systemd-udevd && sudo udevadm trigger
```

Disconnect and reconnect the adapters afterwards. Keep **exactly one line per
name**: where a name appears twice, `humanoid_setup_can.py` keeps the last line
(computed from the code), so its USB-reset recovery can target the wrong
adapter. See [Troubleshooting](reference/troubleshooting.md).
*Source: team design log, "CAN bus"; `deploy/control/humanoid_setup_can.py`.*

### IMU output configuration

The team configured the IMU in the vendor's ImuAssistant tool (Windows) with
**Composite** as the only data output (plus Status), an output data rate of
**800 Hz**, and **USB** as the interface (UART unchecked). The control stack
depends on this: `deploy/control/hardware_bindings/imu/imu.hpp` opens the port at
4000000 baud and parses only the EasyProfile Combo packet.
*Source: team design log, IMU section, and its ImuAssistant screenshot;
`deploy/control/hardware_bindings/imu/imu.hpp`.*

### RealSense D436

The team upgraded the librealsense2 packages (`librealsense2`, `-utils`, `-dev`,
`-gl`, `-udev-rules`, `-dbg`) to **2.58.1**, the version the log gives as adding
D436 support, from the RealSense apt repository at
`librealsense.realsenseai.com`, with the older Intel repository commented out.
Reload the udev rules afterwards so the D436 gets USB permissions. The deploy
requirements pin `pyrealsense2==2.58.1.10581`, and the deploy repository's
`control/docs/SETUP.md` covers the same step.
*Source: team design log, camera setup; `deploy/requirements.txt`.*

### Build toolchain

The C++ CAN layer is built with CMake and vcpkg (Ninja presets) and exposed to
Python through **nanobind** (`deploy/control/CMakeLists.txt`). The team chose
nanobind over pybind11 for faster compiles, smaller binaries and lower runtime
overhead, citing
[nanobind's own benchmarks](https://nanobind.readthedocs.io/en/latest/benchmark.html).
The repository uses **mink** for inverse kinematics only (`mj_envs.utils.ik_mink`).
The team log also lists mink for a collision-avoidance or safety layer; no such
layer was found in the repository, so that use is
**UNVERIFIED**{ .dh-unverified }.
*Source: team design log, "Control"; `deploy/control/CMakeLists.txt`,
`deploy/requirements.txt`.*

### Scripts you do not need for this robot

`deploy/control/torque_sensor_test.py` reads a rotary torque sensor over serial
and publishes the reading as telemetry. It is a bench tool for the torque-sensor
fixture the team used to test actuators. That fixture is **not on the robot**,
and a build does not need the script. See
[Actuator selection](design/actuator-selection.md).
*Source: `deploy/control/torque_sensor_test.py`; team design log, torque-sensor
section.*

### The actuator-sizing simulations are not in the release

The April 2025 gait study that sized the leg actuators used Isaac Gym, which is
not in the repositories. The released simulation uses mjlab and MuJoCo, so those
runs cannot be reproduced from the release. The recordings and what the team
concluded from them are on
[Actuator sizing in simulation](design/actuator-sizing-simulation.md).
*Source: team design log, "simulation verification"; `simulation/requirements.txt`.*

## Control work recorded but not published

The team log's "Lower Body Stable Dynamics" section states its goal: "provide a
control that allows the v2 lower body to hold the upper body's pose stable while
the arms complete tasks". It splits the work into lower-body gravity
compensation (making the real lower-body dynamics match the expected dynamics)
and a stable-stand control loop.
*Source: team design log, "Lower Body Stable Dynamics".*

!!! missing "MISSING — Lower Body Stable Dynamics: the source pages are not in the records"
    The section links separate pages for gravity compensation, the stable-stand
    loop and related notes. None of them is in the team records this site was
    written from, so whether this control exists, and where it lives in the
    deploy code, is not documented.

    *Owner: controls lead.*

## Read this before you move the robot

The deploy repository's
[`control/docs/OPERATIONS.md`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/docs/OPERATIONS.md)
is the operating manual for a stack that, in its own words, drives a 36 kg
humanoid with people beside it. Its safety gates have real incidents behind them,
recorded in
[`auto_operator_incidents.md`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/docs/auto_operator_incidents.md),
and the mechanisms those incidents produced are enumerated in
`auto_operator_safety_contract.md`.

Read both before [Acceptance tests](bringup/acceptance-tests.md), and read
[Safety](before-you-start/safety.md) before either — the control-stack safety
contract protects the controller, not the people standing next to it.

## Assets shared between hardware and software

The robot model, meshes, camera modules and gripper live at
[`simulation/asset/duke_v2/`](https://github.com/generalroboticslab/duke_humanoid_v2_simulation/tree/main/asset/duke_v2):
`humanoid_v21/` for the body, `head_cam/` for the camera modules,
`parallel_gripper/` for the end effectors. They are the link between what you
built and what the policy assumes — joint order, joint directions and link masses
all come from there.

!!! warning "These are simulation assets, not manufacturing data"
    The simulation export states that it leaves the original CAD (`*.step`) out.
    Collision meshes are simplified, visual meshes carry no tolerances, threads or
    finishes, and nothing in that directory is a drawing. Do not send a mesh from
    `asset/` to a machine shop. See [CAD downloads](fabrication/cad-downloads.md).

!!! missing "MISSING — Asset README paths that do not exist in the published export"
    An internal audit of this release found several paths referenced by the
    asset README files that do not exist in the published export. If a link in
    those READMEs leads nowhere, that is a known defect and not something you
    have misread. The list of broken paths is not published here, so a reader
    cannot tell in advance which links are dead.

    *Owner: controls lead.*

Two parts of the hardware/software contract are now answered: which actuator
model sits at which joint (see the as-built map on
[Full specifications](reference/full-specifications.md#actuator-complement)) and
which bus each joint is on (the six-bus list above). The rest is still missing.

!!! missing "MISSING — The hardware/software contract a builder needs"
    The hardware/software contract a builder needs and cannot currently find
    anywhere. This is the single largest remaining gap between a finished
    chassis and a working robot:

    - The **31-DoF joint vector layout** — index → joint name → sign convention —
      exactly as the policy consumes it, so a freshly wired robot can be checked
      against it before it is asked to stand.
    - Which **policy checkpoint** corresponds to which hardware revision.
    - The onboard computer's expected **OS, kernel, driver and firmware**
      versions, as a tested configuration rather than as a minimum.
    - The install path for the stack on a **fresh machine**, start to finish.

    *Owner: controls lead.*

## Licence

The code in all three repositories is Apache-2.0. **That covers the code only.**
The hardware design files and this documentation have no declared licence yet
(**TODO**{ .dh-missing }); see [Citation and licence](reference/citation-and-license.md).
