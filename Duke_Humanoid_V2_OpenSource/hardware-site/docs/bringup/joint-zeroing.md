# Joint zeroing

The zero pose is the deployed model at all joint angles zero; the control stack assumes encoder 0 is that pose. Cameras look straight ahead at zero.

{{ step(1, "Set the zeros") }}

Motors unpowered for movement but on the bus. Hold every joint at the model's zero pose by hand, then:

```bash
python humanoid_set_zero.py     # writes the current position of all 31 motors as zero and saves it to the drives
```

Do not use the vendor tool's *set mechanical zero*: it is lost at power-off. Any later run re-zeroes all 31 motors, the gimbals included, so redo [Camera calibration](#camera-calibration) afterwards.

{{ step(2, "Verify the zeros") }}

```bash
python humanoid_config.py --zero          # ramps every joint to zero at 10 % torque — stay clear
python humanoid_gimbal_zero_check.py      # prints where the model thinks each camera looks
python humanoid_mass_check.py             # gravity torque vs the model on shoulder_2, shoulder_3, elbow, wrist_1
```

✅ **Check:** every joint ends at the zero pose; both cameras look straight ahead; every arm residual ≤ 0.35 N·m.
{ .dh-check }
