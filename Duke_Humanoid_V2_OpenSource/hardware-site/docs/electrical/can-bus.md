# CAN bus

<figure markdown>
  ![Data wiring diagram, Duke Humanoid V2](../assets/wiring/data-wiring-v2.webp){ loading=lazy }
  <figcaption>Data wiring: USB from the computer to three hubs; six CAN buses from hub 2. [Full size](../assets/wiring/data-wiring-v2.png).</figcaption>
</figure>

Six buses at **1 Mbit/s**, one CANable PRO V2.0 adapter (E13) each. Every bus is a single daisy chain — adapter → motor → motor — with a 120 Ω terminator at each physical end and no stubs.

| Bus | Actuators | CAN IDs | Powered from |
| --- | --- | --- | --- |
| `can22` | waist, left and right `shoulder_1` | 1, 10, 20 | lower (waist) and upper (shoulders) blocks |
| `can9` | left arm: `shoulder_2` to `wrist_3` | 11–16 | upper block |
| `can21` | right arm: `shoulder_2` to `wrist_3` | 21–26 | upper block |
| `can24` | left leg: `hip_1` to `ankle_2` | 31–36 | lower block |
| `can23` | right leg: `hip_1` to `ankle_2` | 41–46 | lower block |
| `can25` | camera yaw and pitch, left and right | 7, 8, 5, 6 | upper block |

| USB hub (E16) | Devices |
| --- | --- |
| Hub 1 | Both RealSense D436 (E14, USB 3 required), IMU (E17) |
| Hub 2 | The six CAN adapters (E13) |
| Hub 3 | Both gripper servo driver boards (E10) |

✅ **Check:** an unpowered bus reads about 60 Ω between CAN_H and CAN_L (120 Ω: a terminator missing; 40 Ω: one too many).
{ .dh-check }

## The actuator map

??? info "Every joint's ID, bus and model"
    | Joint | ID | Bus | Model | Joint | ID | Bus | Model |
    | --- | ---: | --- | --- | --- | ---: | --- | --- |
    | `waist` | 1 | `can22` | RS03 | | | | |
    | `left_shoulder_1` | 10 | `can22` | RS03 | `right_shoulder_1` | 20 | `can22` | RS03 |
    | `left_shoulder_2` | 11 | `can9` | RS06 | `right_shoulder_2` | 21 | `can21` | RS06 |
    | `left_shoulder_3` | 12 | `can9` | RS02 | `right_shoulder_3` | 22 | `can21` | RS02 |
    | `left_elbow` | 13 | `can9` | RS02 | `right_elbow` | 23 | `can21` | RS02 |
    | `left_wrist_1` | 14 | `can9` | RS02 | `right_wrist_1` | 24 | `can21` | RS02 |
    | `left_wrist_2` | 15 | `can9` | RS00 | `right_wrist_2` | 25 | `can21` | RS00 |
    | `left_wrist_3` | 16 | `can9` | RS05 | `right_wrist_3` | 26 | `can21` | RS05 |
    | `left_hip_1` | 31 | `can24` | RS03 | `right_hip_1` | 41 | `can23` | RS03 |
    | `left_hip_2` | 32 | `can24` | RS03 | `right_hip_2` | 42 | `can23` | RS03 |
    | `left_hip_3` | 33 | `can24` | RS03 | `right_hip_3` | 43 | `can23` | RS03 |
    | `left_knee` | 34 | `can24` | RS04 | `right_knee` | 44 | `can23` | RS04 |
    | `left_ankle_1` | 35 | `can24` | RS03 | `right_ankle_1` | 45 | `can23` | RS03 |
    | `left_ankle_2` | 36 | `can24` | RS06 | `right_ankle_2` | 46 | `can23` | RS06 |
    | `cam_yaw_left` | 7 | `can25` | RS05 | `cam_yaw_right` | 5 | `can25` | RS05 |
    | `cam_pitch_left` | 8 | `can25` | RS05 | `cam_pitch_right` | 6 | `can25` | RS05 |

    IDs are unique robot-wide. Setting them: [Motor ID and config](../bringup/index.md#motor-id-and-config).
