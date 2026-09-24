# Final integration

Join the subassemblies into one robot, battery disconnected throughout. Two people or a hoist from here on: lift by the top plate.

!!! abstract "At a glance"
    - **You will:** attach legs, arms, camera columns and grippers to the torso, join the harnesses, inspect and hang the robot.
    - **Before this:** [Gripper](#gripper); every actuator labelled with joint, ID and bus.

{{ step(1, "Support the torso") }}

Support it level, waist free, hips and shoulders reachable.

✅ **Check:** the torso cannot fall or rotate when a limb is offered up.
{ .dh-check }

{{ step(2, "Attach the legs") }}

Bolt each leg's hip-pitch bracket (C6) to the pelvis, supporting the leg's weight. Check the side: the legs differ by bus and IDs.

✅ **Check:** all twelve leg joints move; each harness tail reaches the torso, unconnected.
{ .dh-check }

{{ step(3, "Attach the arms") }}

Bolt each arm to its shoulder-pitch coupler (C27). Check the side: the arms differ by bus, IDs and wrist housing.

✅ **Check:** each arm moves through its travel without touching the torso or a leg.
{ .dh-check }

<figure markdown>
  <video class="dh-clip" autoplay loop muted playsinline preload="metadata" width="1154" height="650"
    poster="../assets/exploded/camera-mount-poster.webp" aria-label="Whole robot with camera columns and grippers lifting off"><source src="../assets/exploded/camera-mount.mp4" type="video/mp4"><a href="../assets/exploded/camera-mount.mp4">MP4</a></video>
  <figcaption>Camera columns onto the top plate; grippers onto the wrists. Click to pause; drag the bar to scrub.</figcaption>
</figure>

{{ step(4, "Mount the camera columns") }}

Bolt both columns to the top plate as in [Head and camera gimbal](#head-and-camera-gimbal), step 9.

✅ **Check:** yaw axes 130 mm apart; no column touches an arm in any pose.
{ .dh-check }

{{ step(5, "Mount the grippers") }}

Bolt each gripper to its wrist output (P8) as in [Gripper](#gripper), step 7; run the servo cable up the arm to its driver board.

✅ **Check:** both grippers work; their tags face the cameras in some arm pose.
{ .dh-check }

{{ step(6, "Join the harnesses") }}

Join one branch at a time against the bus table; wiring detail is on [Electrical](../electrical/index.md).

| Bus | Carries |
| --- | --- |
| `can22` | Waist (ID 1), both `shoulder_1` (10, 20) |
| `can9` / `can21` | Left / right arm, IDs 11–16 / 21–26 |
| `can24` / `can23` | Left / right leg, IDs 31–36 / 41–46 |
| `can25` | Camera gimbals, IDs 5–8 |

✅ **Check:** every branch is labelled; waist, hips and shoulders move with nothing pulled or pinched.
{ .dh-check }

{{ step(7, "Inspect and hang the robot") }}

Every joint moves by hand, alone and in combination; no cable is stretched, pinched or kinked in any pose; nothing rattles; lenses clean; packs disconnected. Hang the robot from the top plate with the legs straight.

✅ **Check:** it hangs level, legs straight.
{ .dh-check }

Next: [Electrical](../electrical/index.md), then [Bring-up](../bringup/index.md).
