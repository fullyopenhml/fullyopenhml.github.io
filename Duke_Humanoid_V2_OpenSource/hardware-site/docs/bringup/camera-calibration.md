# Camera calibration

Four steps, in order, with both cameras streaming.

{{ step(1, "Bind the cameras to their ports") }}

```bash
rs-enumerate-devices -s     # serials; left camera first
```

Set `CAMERA_SERIALS` in `perception/vs_site_local.py`, or pass `--devices <left-serial> <right-serial>` to the camera server. Left camera → port 5555, right → 5556.

{{ step(2, "Check the gimbal zero") }}

`python humanoid_gimbal_zero_check.py` prints each camera's predicted azimuth and elevation at encoder zero; the left should read about 0° / 0°, the right about 180° / 0° (it faces aft). Off? Re-zero the four `cam_*` motors alone with `humanoid_set_zero.py` (comment the other joints out of `motor_setup_dict` for that run, then restore them).

{{ step(3, "Calibrate the gimbal gear ratio") }}

Hold the 40 mm tag cube in front of the camera; the tool moves that gimbal 0.4 rad yaw and 0.3 rad pitch and prints `gear ≈`.

```bash
python calibrate_cam_gear.py               # left gimbal
python calibrate_cam_gear.py --side right  # right gimbal
```

{{ step(4, "Calibrate hand-eye") }}

Bolt `tag_cube_0` / `tag_cube_1` to the left / right wrist, telemetry on port 9870.

```bash
python humanoid_monitor.py --record-handeye        # move both arms ≥ 30° and ≥ 50 mm, wrist roll included; ≥ 100 valid frames per port; Ctrl+C saves
python humanoid_handeye_calibration.py             # → calibration/camera_handeye.yaml; must print VALID
python humanoid_monitor.py --handeye-yaml calibration/camera_handeye.yaml
```

✅ **Check:** the solve prints `VALID` with translation residual under 20 mm and rotation under 5°.
{ .dh-check }

## Tag fixtures

AprilTag `tag36h11`, 30 mm marker with a 5 mm quiet zone per face; any rigid 40 mm cube. Files: `perception/tagged_bodies/` in the deploy repository.

| Fixture | Use | Tag IDs |
| --- | --- | --- |
| `tag_cube_0` | Hand-eye, left wrist: 40 mm core, tags on top and four sides | 582–586 |
| `tag_cube_1` | Hand-eye, right wrist | 577–581 |
| `grasp_cube_40mm` | Gear calibration, hand-held; tags on all six faces | 501–506 |
