# Image manifest

Every image this site needs and does not have, with the exact path it must be
saved to and one line on what it must show. **74 images are missing.**

This is the list to hand to whoever renders the remaining figures. It is not
a wish list: each path below is already named on a page, so dropping a file
at that path is all that is needed — no page has to be rewritten to accept it.

!!! warning "Why no page shows a broken image"
    `mkdocs build --strict` fails on a link to an image that does not exist, so
    a placeholder cannot be a real `![](…)`. Pages mark a missing figure as a
    blockquote instead:

    ```markdown
    > **Figure** <span class="pending-figure">not produced yet</span> —
    > `assets/assembly/leg-step-02.png`: what the render must show.
    ```

    When the file lands, swap those three lines for the image and delete the
    row from this manifest. Both happen in the same commit or neither does.

## What to produce first

| Priority | What | Why it is first |
| --- | --- | --- |
| 1 | Step renders, `assets/assembly/<page>-step-NN.png` | Not one exists, and not one is named on a page yet. A step with no figure is the site's largest readability gap |
| 2 | The 6 routing photographs | A routing decision does not survive being written down. These must be taken during a build, not reconstructed after one |
| 3 | Everything else | — |

The whole-robot and subassembly exploded views are no longer on this list:
the team's exploded-view booklet delivers 12 of them, labelled with the
team BOM ids and placed on the Assembly pages.

## Format and size

| | |
| --- | --- |
| CAD renders, diagrams | `.png`, or `.svg` for anything with text in it. Long edge 1600 px, transparent or white background |
| Photographs | `.jpg`, long edge 2000 px, under 500 KB. The part in focus, the rest of the bench not |
| Wiring and pinout drawings | `.svg` — they will be read at 200% and they will be corrected |
| Anything animated | `.webp`. Keep it under 5 MB; the existing demo loops are the ceiling, not the target |

Filenames are lowercase with hyphens, except the per-part families below, whose
filenames must match a `part_id` character for character so the page can find
them without a lookup table.

## Missing — referenced by a page (0)

Each of these already has a placeholder blockquote on the page named.

| Path | Page | What it must show |
| --- | --- | --- |

## Missing — named on a page but not yet placed (23)

These are named in a TODO block or an image manifest but have no placeholder
in the page body yet; add the placeholder in the commit that adds the file.

| Path | Page that will use it | What it must show |
| --- | --- | --- |
| `assets/images/camera-module.png` | `index.md, reference/faq.md` | One camera gimbal module alone, off the robot, dimensioned — so it can be judged as a component by someone who wants only the module. |
| `assets/images/safety-pinch-points.png` | `fabrication/safety.md` | The robot with every pinch point marked on the real link geometry: between limb and torso, inside each joint, and the jaw closing line. |
| `assets/images/safety-lifting-points.png` | `fabrication/safety.md, assembly/final-integration.md` | The sanctioned lifting points marked on the machine, with the sling route drawn, and the places that look like handles but are not. |
| `assets/images/safety-hanging-legs-straight.png` | `fabrication/safety.md` | The robot correctly suspended with the legs hanging straight, next to the same robot hung wrong with the legs bent. Three bring-up sessions were lost to this exact mistake; the pair of images is the whole lesson. |
| `assets/bom/fasteners/fastener-size-chart.png` | `bom/fasteners-and-hardware.md` | One-page visual size chart for every fastener in the build, printed 1:1 so a screw can be laid on the page and identified. Blocked on the fastener schedule existing at all. |
| `assets/electrical/system-wiring-diagram.svg` | `electrical/index.md` | Every load, rail, bus and connector on one sheet. The single most valuable missing artefact in the Electrical section. |
| `assets/electrical/power-tree.svg` | `electrical/power-system.md` | Packs, their series/parallel configuration, each converter, each rail and what it feeds, with the fusing and the disconnect drawn where they belong. |
| `assets/electrical/connector-xt30-2p2-pinout.svg` | `electrical/harness-fabrication.md` | XT30(2+2) pinout drawn from the mating face, with the orientation feature and the wire-colour convention. |
| `assets/electrical/connector-actuator-pinout.svg` | `electrical/harness-fabrication.md` | Actuator connector pinout from the mating face, both halves, with the mating part number. |
| `assets/electrical/connector-gripper-servo-pinout.svg` | `electrical/harness-fabrication.md` | Gripper servo connector pinout from the mating face, both halves. |
| `assets/electrical/routing-leg.jpg` | `electrical/routing.md, assembly/leg.md` | Photograph of the finished leg routing before the shank closes, every clamp point visible. Prose does not transfer a routing decision. |
| `assets/electrical/routing-arm.jpg` | `electrical/routing.md, assembly/arm.md` | Photograph of the finished arm routing, showing the service loop at the shoulder and at the wrist. |
| `assets/electrical/routing-waist.jpg` | `electrical/routing.md, assembly/torso-and-waist.md` | Photograph of the waist crossing, the one place a bus spans three subassemblies. |
| `assets/electrical/routing-torso.jpg` | `electrical/routing.md, assembly/torso-and-waist.md` | Photograph of the torso interior with the computer, converters, CAN adapters and packs installed and the harness dressed. |
| `assets/electrical/routing-camera-gimbal.jpg` | `electrical/routing.md, assembly/head-and-camera-gimbal.md` | Photograph of the camera cable through a gimbal column at both yaw extremes, showing the loop and every retention point. The cable across the yaw axis is the highest-risk routing on the robot. |
| `assets/electrical/routing-gripper.jpg` | `electrical/routing.md, assembly/gripper.md` | Photograph of the gripper servo cable and its strain relief at the wrist. |
| `assets/bringup/zero-pose-front.jpg` | `bringup/joint-zeroing.md` | The reference robot held in the zero pose, front view, with the mechanical feature that defines each joint's zero called out. |
| `assets/bringup/zero-pose-side.jpg` | `bringup/joint-zeroing.md` | The same zero pose from the side. Two views are the minimum: one view cannot show both pitch and roll zeros. |
| `assets/bringup/joint-direction-convention.svg` | `bringup/motor-id-and-config.md` | Every joint with its positive direction drawn as an arrow on the real geometry. A backwards joint passes every other check in the site. |
| `assets/bringup/tag-cube-wrist-mounting.jpg` | `bringup/camera-calibration.md` | The tag cube mounted on the wrist interface, with the tag family, tag size and orientation visible. Without this fixture the robot cannot be calibrated. |
| `assets/fabrication/cad-release-assets.png` | `fabrication/cad-downloads.md` | Screenshot of a tagged release page with the CAD archives attached, so a reader knows what a correct release looks like when they see one. |
| `assets/fabrication/printed-parts-orientation.png` | `fabrication/printing-guide.md` | Each structural printed part shown in its validated print orientation, with the load direction the layer lines must not align with drawn on it. |
| `assets/fabrication/heat-set-insert-seated.jpg` | `fabrication/printing-guide.md` | A heat-set insert correctly seated, next to one pressed in too far and one left proud. |

## Missing — per-part families (51)

One image per row of a BOM CSV. The filename **is** the `part_id`, so these
can be produced in a batch and dropped in without touching a page.

| Path pattern | Count | Page | What each must show |
| --- | ---: | --- | --- |
| `assets/bom/cnc/<part_id>.png` | 30 | `bom/cnc-parts.md` | One render per machined part, filename exactly the `part_id` in `cnc-parts.csv`. A machined part a builder cannot see is a part they will order wrong. |
| `assets/bom/electronics/<part_id>.jpg` | 15 | `bom/electronics.md` | One photograph per bought electronic part, filename exactly the `part_id` in `electronics.csv`, so a builder can confirm the thing in the box is the thing on the list. |
| `assets/bom/actuators/<part_id>.jpg` | 6 | `bom/actuators.md` | One photograph per Robstride model, filename exactly the `part_id` in `actuators.csv`. The models look alike and are not interchangeable. |

??? note "The 30 filenames for `assets/bom/cnc/<part_id>.png`"

    - `CNC_leg01_hip_center_back`
    - `CNC_leg02_RS03_shaft_coupler`
    - `CNC_leg03_RS03_shaft_bearing_retainer`
    - `CNC_leg04_hip_roll_front_bearing_retainer`
    - `CNC_leg05_hip_roll_back_bearing_retainer`
    - `CNC_leg06_hip_roll_output_shaft`
    - `CNC_leg07_hip_roll_support_shaft`
    - `CNC_leg08_knee_front_bearing_retainer`
    - `CNC_leg09_knee_motor_back_cover`
    - `CNC_leg10_knee_output_shank`
    - `CNC_leg11_knee_support_shank`
    - `CNC_leg12_lower_leg_bearing`
    - `CNC_leg13_ankle_pitch_front`
    - `CNC_leg14_ankle_pitch_back`
    - `CNC_leg15_RS06_shaft_bearing_retainer`
    - `CNC_leg16_ankle_roll_output_shaft`
    - `CNC_leg17_ankle_roll_support_shaft`
    - `CNC_leg18_foot_plate`
    - `CNC_arm01_shoulder_roll_front_bearing`
    - `CNC_arm02_shoulder_roll_back_bearing`
    - `CNC_arm03_shoulder_roll_output_shaft`
    - `CNC_arm04_shoulder_roll_support_shaft`
    - `CNC_arm07_elbow_front_bearing`
    - `CNC_arm08_elbow_back_bearing`
    - `CNC_arm09_elbow_output_shaft`
    - `CNC_arm10_r03_back_cover`
    - `CNC_body01_bottom_plate`
    - `CNC_body02_side_plate`
    - `CNC_body03_top_plate`
    - `CNC_body04_front_plate`

??? note "The 15 filenames for `assets/bom/electronics/<part_id>.jpg`"

    - `EL_COMPUTE_MINIPC`
    - `EL_BATTERY_6S`
    - `EL_TVS_DIODE`
    - `EL_SERVO_DRIVER`
    - `EL_BUCK_12V_ENC`
    - `EL_BUCK_48V_12V`
    - `EL_CAN_ADAPTER`
    - `EL_CAM_D436`
    - `EL_SERVO_FEETECH`
    - `EL_USB_HUB`
    - `EL_IMU_TM171`
    - `EL_SURGE_PROTECTOR`
    - `EL_DIST_BLOCK`
    - `EL_VOLTAGE_CHECKER`
    - `EL_USBC_ADAPTER`

??? note "The 6 filenames for `assets/bom/actuators/<part_id>.jpg`"

    - `ACT_RS00`
    - `ACT_RS02`
    - `ACT_RS03`
    - `ACT_RS04`
    - `ACT_RS05`
    - `ACT_RS06`

## Already here (19)

Photographs and clips of the reference robot from the project repository's
`media/` directory, plus the pages of the team's exploded-view booklet
(`files/drawings/duke_humanoid_v2_exploded_views_rev01.pdf`), one image per
page, labelled with the team BOM ids. None of these replaces a step render.

| Path | Used on | What it shows |
| --- | --- | --- |
| `assets/images/teaser.webp` | `index.md` | The robot in simulation and on hardware, side by side. |
| `assets/images/hardware.webp` | `index.md` | Hardware overview with all joints numbered and the three modules labelled. |
| `assets/images/hardware_tracking.mp4` | `index.md` | The reference robot tracking two independently moving targets. |
| `assets/images/vrw_fixed_vs_actuated.mp4` | `index.md` | Visible-reachable workspace, fixed head versus actuated camera modules. |
| `assets/images/hardware_close_front_back.mp4` | `assembly/head-and-camera-gimbal.md` | The two finished camera modules aiming independently. |
| `assets/images/two_target_handoff_left_right.mp4` | `bringup/acceptance-tests.md` | What passing acceptance test A10 looks like. |
| `assets/images/workspace.webp` | `reference/faq.md` | Visible-reachable workspace across six humanoid platforms. |
| `assets/exploded/team/01-torso-frame.webp` | `assembly/torso-and-waist.md` | Torso frame: plates C0–C3, spine P0, actuators E3, bearings H0. |
| `assets/exploded/team/02-electronics-tray.webp` | `assembly/torso-and-waist.md` | Torso electronics: E0, E7, E13, E16, E17, E18, E19, E20. |
| `assets/exploded/team/03-torso-printed-plates.webp` | `assembly/torso-and-waist.md` | Printed torso plates P1–P3. |
| `assets/exploded/team/04-leg-upper.webp` | `assembly/leg.md` | Hip pitch and roll: C4–C8, actuators E3, bearings H0. |
| `assets/exploded/team/05-leg-lower.webp` | `assembly/leg.md` | Hip yaw to foot plate: C4, C5, C9–C21, actuators E3, E4, E6, bearings H0–H3. |
| `assets/exploded/team/06-leg-covers.webp` | `assembly/leg.md` | Printed leg covers P20–P32. |
| `assets/exploded/team/09-arm.webp` | `assembly/arm.md` | Right arm: C5, C22–C29, P4–P8, actuators E1, E2, E5, E6, bearings H2, H4. |
| `assets/exploded/team/10-arm-covers.webp` | `assembly/arm.md` | Printed arm covers P33–P39. |
| `assets/exploded/team/11-torso-p9.webp` | `assembly/arm.md` | Left arm, with the left wrist housing P9 in place of the right housing P7. |
| `assets/exploded/team/13-gripper.webp` | `assembly/gripper.md` | One gripper: P10–P15, servo E15, driver board E10, converter E12. |
| `assets/exploded/team/14-camera-gimbal.webp` | `assembly/head-and-camera-gimbal.md` | One camera column: P16–P19, actuators E5, camera E14, bearing H5. |
| `assets/exploded/team/15-whole-robot.webp` | `index.md, assembly/index.md` | The robot with both camera columns and both grippers lifted off. |

## Counting

| | |
| --- | ---: |
| Referenced by a page, missing | 0 |
| Named on a page, not yet placed | 23 |
| Per-part families | 51 |
| **Missing, total** | **74** |
| Present | 19 |

## Regenerating this page

Derived from the placeholders on the pages and from the BOM CSVs, not
maintained by hand:

```console
$ python tools/gen_image_manifest.py
```

The per-part families come from `part_id` columns, so a new row in
`cnc-parts.csv` adds its render to this list automatically. Figures that are
named on a page but have no placeholder yet are the one hand-maintained part,
in the `EXTRA` table at the top of that script.

