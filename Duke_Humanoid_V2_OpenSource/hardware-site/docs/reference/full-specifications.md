# Full specifications

## Actuators

| Model | Joints (both sides unless noted) | Qty | Peak torque (N·m) | Kt (N·m/A~rms~) | Current limit default / written (A) |
| --- | --- | ---: | ---: | ---: | ---: |
| RS00 | wrist_2 | 2 | 14 | 1.48 | 16 / 9.6 |
| RS02 | shoulder_3, elbow, wrist_1 | 6 | 17 | 1.22 | 23 / 13.8 |
| RS03 | waist (1), hip_1, hip_2, hip_3, ankle_1, shoulder_1 | 11 | 60 | 2.36 | 43 / 25.8 |
| RS04 | knee | 2 | 120 | 2.10 | 60 / 36.0 |
| RS05 | wrist_3; camera yaw and pitch (4) | 6 | 5.5 | 0.94 | 11 / 6.6 |
| RS06 | ankle_2, shoulder_2 | 4 | 36 | 1.1 | 57 / 34.2 |
| **Total** | | **{{ bom_qty("actuators.csv") }}** | | | |

Written current limit = default × 0.6 (`humanoid_set_current_limit.py`), capped at 40 A. Torque limit at run time = peak × `--torque-limit` (0.1–0.8). 48 V bus, CAN at 1 Mbit/s; over-temperature warning 75 °C, fault 80 °C. IDs and buses: [CAN bus](../electrical/index.md#can-bus). Manuals: [robstride.com/download](https://www.robstride.com/download).

## Joint limits

Software limits in the deployed model, not mechanical stops.

| Joint | Limit | Joint | Limit |
| --- | --- | --- | --- |
| waist | ±90° | shoulder_1 | ±180° |
| hip_1 | ±105° | shoulder_2 | L −180° to +30°, R −30° to +180° |
| hip_2 | L −105° to +30°, R −30° to +105° | shoulder_3 | ±180° |
| hip_3 | ±90° | elbow | ±125° |
| knee | ±130° | wrist_1 | ±180° |
| ankle_1 | ±50° | wrist_2 | ±92° |
| ankle_2 | ±60° | wrist_3 | ±90° |
| camera yaw | ±270° | camera pitch | ±90° |

## Robot

| | |
| --- | --- |
| Degrees of freedom | 31 RobStride joints + 2 gripper servos |
| Size | 1256 mm tall standing with camera masts; 346 mm across the shoulders; torso 483 mm; foot 235 mm ([overall drawing](../files/drawings/humanoid_2.1_latest_overall_rev01.pdf)) |
| Mass (CAD) | 35.3 kg: lower body 17.5 (each leg 5.6), torso 7.9 (camera columns 0.59 each), each arm 4.6, each gripper 0.35. Per part: [part-properties.csv](../data/part-properties.csv){ download="" } |
| Structure | Machined aluminium 6061; printed PLA, TPU and SLS nylon 12 |
| Computer | MINISFORUM X1-470 mini PC, 12 V |
| IMU | SYD Dynamics TransducerM TM171, 9-axis, USB |
| Cameras | 2 × Intel RealSense D436, each on a 2-axis gimbal |
| CAN | 6 × CANable PRO V2.0, 1 Mbit/s |
| Grippers | 2 × Feetech HL-3915-C001 (12 V) on Waveshare ST/SC bus servo adapters |
| Battery | 2 × Zeee 6S 10000 mAh LiPo in series: 44.4 V nominal, 50.4 V full |
| Control | 50 Hz policy, 200 Hz motor loop; cuRobo planner on a separate CUDA machine |
