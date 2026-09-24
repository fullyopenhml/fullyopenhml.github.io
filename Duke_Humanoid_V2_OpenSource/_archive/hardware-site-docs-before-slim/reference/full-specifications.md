# Full specifications

The complete specification table for the robot this site documents. The
[home page](../index.md) carries a summary; this page is the one to cite, and it
is careful about where each row comes from — a number quoted from a project
README and a number read off a purchasing spreadsheet are not equally
authoritative, and this page does not mix them.

## Quoted from the project README

These rows are authoritative. They are reproduced exactly as the project README
states them.

| | |
| --- | --- |
| DoF | 31: 27-DoF body (waist ×1, legs 2×6, arms 2×7) + two 2-DoF camera gimbals, +1 per gripper |
| Mass / height | 36 kg / 1.2 m |
| Arm reach / leg length | 0.46 m / 0.39 m |
| Cameras | 2 × Intel RealSense D436, 90°×65° RGB FoV, 0.1–3.0 m, each on its own yaw-pitch gimbal |
| End effectors | parallel grippers, 350 g each, one mimic-coupled jaw slide |
| Actuation | quasi-direct-drive throughout |
| Control | 50 Hz learned whole-body policy onboard, 200 Hz CAN motor loop |

One further figure from the same source, because it is the only published price
anchor in the whole release: adding a *third* camera module raised pairwise
workspace coverage from 0.95 to 0.97 while adding **0.58 kg, two gimbal DoF and
approximately $600 in hardware cost** **UNVERIFIED**{ .dh-unverified } — the
cost is approximate and is not a sum of priced rows in this site's data. The
design adopted two modules.

## Design goals (design goal, not as-built)

The team's "V2 humanoid actuator design spec" table set these targets before the
build. They are **design goals, not as-built figures**, and two of them differ
from the robot that was built.

| | Design goal | As built (project README) |
| --- | --- | --- |
| Leg length | 0.3 m | 0.39 m |
| Leg DoF | 6 | 6 |
| Mass | 24 kg, without arms, with a 1-DoF lower back | 36 kg, whole robot |
| Peak joint torque targets (N·m) | HAA 60, HA 60, HFE 60, KFE 80, AFE 45, AR 20 | See the actuator map below |

*Source: team design log, "V2 humanoid actuator design spec" table, row "V2
design goal". Joint abbreviations as in the team table.* How these targets were
derived is on [Torque targets and mass](../design/torque-targets-and-mass.md).

## Read off the internal parts list

These rows describe the parts the lab actually bought. They are useful and they
are not a specification: a purchasing line tells you what was ordered, not what
is required, and nothing here has been confirmed as a design requirement.

| | | |
| --- | --- | --- |
| Onboard computer | MINISFORUM X1-470 mini PC | 1 |
| IMU | SYD Dynamics TransducerM TM171, 9-axis AHRS | 1 |
| Battery | 6S LiPo, 10000 mAh, 22.2 V nominal | 2 |
| Depth cameras | Intel RealSense D436 | 2 |
| USB-CAN adapters | CANable Pro v2.0 class | 6 |
| Gripper servo | Feetech HL-3915-C001, 12 V | 2 |
| Serial bus servo driver | Waveshare ST/SC bus servo adapter | 2 |

## Actuator complement

31 RobStride quasi-direct-drive units in six models:

| Model | Count |
| --- | --- |
| RobStride 00 | 2 |
| RobStride 02 | 6 |
| RobStride 03 | 11 |
| RobStride 04 | 2 |
| RobStride 05 | 6 |
| RobStride 06 | 4 |
| **Total** | **{{ bom_qty("actuators.csv") }}** |

The per-model counts are read from `actuators.csv`; the total is computed from it.

As-built joint-to-model map (deploy/control/humanoid_config.py): waist R03; hip_1, hip_2, hip_3 R03; knee R04; ankle_1 R03; ankle_2 R06; shoulder_1 R03; shoulder_2 R06; shoulder_3 R02; elbow R02; wrist_1 R02; wrist_2 R00; wrist_3 R05; cam_yaw/cam_pitch (4) R05 — 31 actuators.
*Source: `deploy/control/humanoid_config.py`.* Leg and arm joints are per side.
See [Actuators](../bom/actuators.md).

## Power

Two Zeee 6S 10000 mAh LiPo packs are connected in series (one pack's + to the other's −) and feed a bus labelled 48V through a surge protector. Computed, not stated in the diagram: 2 × 22.2 V = 44.4 V nominal and 2 × 25.2 V = 50.4 V at full charge.
*Source: team power wiring diagram (V2).*

The RobStride 02, 03 and 04 manuals give a rated voltage of 48 VDC and an operating range of 24–60 VDC. The RS00, RS05 and RS06 manuals are not in the team records, so their range is **UNVERIFIED**{ .dh-unverified }.
*Source: RobStride 02, 03 and 04 product manuals.*

See [Power system](../electrical/power-system.md) and
[Safety](../before-you-start/safety.md).

## Actuator environmental limits

These apply to the **actuators only**, not to the robot as a whole.

| | |
| --- | --- |
| Operating temperature | −20 to 50 °C |
| Storage temperature | −30 to 70 °C |
| Humidity | 5–85 % RH, non-condensing |

*Source: RobStride 02, 03 and 04 product manuals, §1.2.*

## Control and buses

| | |
| --- | --- |
| Policy rate | 50 Hz, learned whole-body policy, onboard |
| Motor loop | 200 Hz over CAN |
| CAN buses | 6, at 1 Mbit/s, named `can9` and `can21`–`can25`; `can9` carries the left arm |
| Planning | cuRobo plan/MPC server, on a separate CUDA machine |

## What is not specified anywhere

Everything below is a specification a rebuilder needs and the release does not
contain. They are listed individually rather than as "documentation to be
written", so that each can be closed and struck off.

!!! missing "MISSING — Specifications a rebuilder needs that the release does not contain"
    **Mechanical**

    - Per-joint range of motion, and whether each limit is mechanical or only
      commanded.
    - Per-joint peak and continuous torque **as configured** — the enforced
      current limit, not the actuator datasheet.
    - Mass breakdown by subassembly. 36 kg is the total; a builder checking their
      own build against it needs the parts.
    - Centre of mass and inertia at the zero pose. These are derivable from the
      published robot model, but a specification page should state them rather
      than make a reader compute them.
    - Foot geometry and the support polygon it produces.

    **Electrical**

    - Peak and idle system current, and the resulting runtime — standing and
      walking, as two numbers.
    - Confirmation that the robot as built matches its power diagram, which
      draws no fuse, breaker or contactor between the packs and the bus.

    **Performance**

    - Payload, per arm and for the whole machine.
    - Walking speed achieved, and on what surface.
    - Camera gimbal **mechanical** range and slew rate. The headline subsystem
      has no hardware specification at all: the only published figures are the
      simulation model's joint limits, and the model's own comment records the
      yaw range as a reinforcement-learning choice rather than a hard stop. See
      [Head and camera gimbal](../assembly/head-and-camera-gimbal.md#range-of-motion).

    **Environment**

    - Ingress protection against dust and water, if any. Assume none.
    - Operating temperature range of the whole robot. Only the actuator limits
      are known (above); battery, computer and camera limits are not collected.
    - Noise level, which matters for a lab that shares a room with it.

    *Owner: hardware lead + controls lead.*
