# Routing

| Run | Route |
| --- | --- |
| Leg bus (`can24` / `can23`) + 48 V | From the lower-body blocks in the pelvis, down each leg motor to motor under the covers; the tail terminator at the ankle |
| Arm bus (`can9` / `can21`) + 48 V | From the upper-body blocks, out through the shoulder, motor to motor to the wrist under the covers |
| `can22` | Waist actuator in the pelvis; both `shoulder_1` in the torso side plates |
| `can25` + 48 V | Up the top plate to both camera columns |
| Camera USB, gripper servo feed and signal | Down each camera column; up each arm to the wrist |

- Leave a service loop at every joint sized for the joint's full travel, not one pose; keep CAN pairs twisted to the connector.
- Sleeve limb runs in 1/4 in or 3/8 in loom; tie to the printed covers, never across a moving edge.
- Turn every joint to both ends by hand before a limb is closed: no cable taut, pinched or rubbing.

✅ **Check:** with the robot suspended, every joint moves through its travel with every cable free.
{ .dh-check }
