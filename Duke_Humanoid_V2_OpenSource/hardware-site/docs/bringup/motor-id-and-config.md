# Motor ID and config

| Property | Set with | Notes |
| --- | --- | --- |
| CAN ID | RobStride vendor tool ([robstride.com/download](https://www.robstride.com/download)) over the vendor's USB-CAN module (CH340), one motor at a time on the bench, before it goes into a limb | RS03 and RS04 ship at ID 127; the ID table is editable in standby only |
| Current limit | `python humanoid_set_current_limit.py` (default scale 0.6; type `yes`) | Writes `min(default × 0.6, 40 A)` per model and saves it to the drive; values on [Full specifications](../reference/index.md#actuators) |
| Torque limit | `--torque-limit <ratio>` on every `humanoid_real_env.py` run | 0.05 smoke test, 0.5 joint sweep, 0.8 standing |
| Zero | [Joint zeroing](#joint-zeroing) | |

{{ step(1, "Verify and smoke-test") }}

```bash
python humanoid_config.py       # reads type, bus voltage, position and limits of every motor; nothing moves
# power-cycle, bring the buses up, run it again: every value must read back the same
python humanoid_test_motor.py   # 5 % torque, 0.1 rad sine on the 14 arm joints and 4 gimbal joints
```

✅ **Check:** every actuator reads back unchanged after a power cycle; the smoke test moves the arm and gimbal joints only, the right way, quietly.
{ .dh-check }

**Positive direction:** every joint's positive rotation axis points from the actuator's output shaft towards its back; fit the actuator as the model orients it and the sign follows. The reference is the deployed MuJoCo model, `robot.xml` in the deploy run directory.
