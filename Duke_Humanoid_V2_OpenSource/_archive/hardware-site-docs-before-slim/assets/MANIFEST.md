# Image manifest

Every image this site needs and does not have, with the exact path it must be
saved to and one line on what it must show. **158 images are missing.**

This is the list to hand to whoever renders the exploded views. It is not a
wish list: each path below is already named on a page, so dropping a file at
that path is all that is needed — no page has to be rewritten to accept it.

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
| 1 | `assets/images/exploded-overview.png` | **The team already has this render.** One file, four pages: the home page, What you get, Bill of materials and Assembly all want the whole-robot exploded view, and it is the single image that makes the machine legible |
| 2 | The 5 subassembly exploded views (leg, arm, torso, head, gripper) | Each one makes its assembly page usable as a whole rather than step by step |
| 3 | The 40 step renders | Written steps without a figure are the site's largest readability gap |
| 4 | The 6 routing photographs | A routing decision does not survive being written down. These must be taken during a build, not reconstructed after one |
| 5 | Everything else | — |

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

## Missing — referenced by a page (54)

Each of these already has a placeholder blockquote on the page named.

| Path | Page | What it must show |
| --- | --- | --- |
| `assets/assembly/arm-exploded.png` | `assembly/arm.md` | The animation above carries no labels or part IDs. Still needed: the same view with every part labelled with its part ID and the seven actuators called out with their joint names |
| `assets/assembly/arm-step-01.png` | `assembly/arm.md` | The seven actuators laid out in chain order and labelled, with the shoulder-pitch actuator visibly marked for its different bus |
| `assets/assembly/arm-step-02.png` | `assembly/arm.md` | Shoulder-pitch actuator and its back cover, with the torso mounting face called out |
| `assets/assembly/arm-step-03.png` | `assembly/arm.md` | Shoulder-roll actuator, both shafts and both bearing housings exploded along the roll axis |
| `assets/assembly/arm-step-04.png` | `assembly/arm.md` | Shoulder-yaw actuator with its shaft bearing and coupler, joined to the shoulder-roll output |
| `assets/assembly/arm-step-05.png` | `assembly/arm.md` | Elbow actuator, output shaft and both bearing housings, exploded along the elbow axis |
| `assets/assembly/arm-step-06.png` | `assembly/arm.md` | Wrist-roll body and actuator joined to the elbow output |
| `assets/assembly/arm-step-07.png` | `assembly/arm.md` | Wrist-pitch body and its actuator joined to the wrist-roll output |
| `assets/assembly/arm-step-08.png` | `assembly/arm.md` | Wrist-yaw actuator and coupler, with the gripper mounting face called out and dimensioned |
| `assets/assembly/arm-step-09.png` | `assembly/arm.md` | The finished arm with harness routed and retained, every crossing of a moving joint marked, and the three cable groups distinguishable |
| `assets/assembly/final-robot-hanging.png` | `assembly/final-integration.md` | The finished robot hanging with the legs straight, for comparison against a bent-leg hang |
| `assets/assembly/final-step-02.png` | `assembly/final-integration.md` | Leg offered up to the pelvis, showing the interface, the fastener pattern and where the leg is supported during the join |
| `assets/assembly/final-step-04.png` | `assembly/final-integration.md` | Arm at the shoulder interface, both cable groups visible entering the torso |
| `assets/assembly/final-step-07.png` | `assembly/final-integration.md` | The torso with every branch connected, each connector labelled with its bus or function |
| `assets/assembly/final-support-rig.png` | `assembly/final-integration.md` | The stand or frame holding the torso during integration, with the sling route and lifting points marked |
| `assets/assembly/gripper-aperture.png` | `assembly/gripper.md` | The gripper at fully open and at fingers-touch, with the measured gap dimensioned |
| `assets/assembly/gripper-exploded.png` | `assembly/gripper.md` | One gripper exploded — base, servo, pinion, both racks, flange, jaw pads and the eight tag pads — every part labelled, with the slide direction and the jaw travel drawn |
| `assets/assembly/gripper-step-02.png` | `assembly/gripper.md` | Servo seated in the base, with the pinion axis and the slide direction drawn |
| `assets/assembly/gripper-step-03.png` | `assembly/gripper.md` | Both racks engaging the pinion, with the tooth alignment that produces a symmetric jaw position highlighted |
| `assets/assembly/gripper-step-05.png` | `assembly/gripper.md` | Both hands, every tag slot labelled with its tag ID, showing which four are on the jaws and which four on the base |
| `assets/assembly/head-axes-diagram.png` | `assembly/head-and-camera-gimbal.md` | A dimensioned line diagram of the P-frame, both yaw axes, the pitch axis and the optical centre — the drawing a machinist and a calibration engineer can both work from |
| `assets/assembly/head-exploded.png` | `assembly/head-and-camera-gimbal.md` | The animation above has no labels and no axes drawn. Still needed: one gimbal column exploded along its axis, each part labelled, with the yaw and pitch axes drawn through the assembly |
| `assets/assembly/head-step-01.png` | `assembly/head-and-camera-gimbal.md` | Four labelled RobStride 05 actuators and two D436 cameras with their serial labels visible |
| `assets/assembly/head-step-02.png` | `assembly/head-and-camera-gimbal.md` | Yaw actuator seated in the gimbal mount, yaw axis drawn, mount bottom face called out as the plate datum |
| `assets/assembly/head-step-03.png` | `assembly/head-and-camera-gimbal.md` | Neck on the yaw output, with the 105.44 mm yaw-to-pitch distance dimensioned |
| `assets/assembly/head-step-04.png` | `assembly/head-and-camera-gimbal.md` | Pitch actuator and arm on the neck, both axes drawn, showing the perpendicular intersection |
| `assets/assembly/head-step-05.png` | `assembly/head-and-camera-gimbal.md` | Camera and adapter on the arm, with the optical centre marked and the 250 mm height above the plate dimensioned |
| `assets/assembly/head-step-06.png` | `assembly/head-and-camera-gimbal.md` | The cable route drawn through the column at three yaw positions — full left, centre, full right — showing the service loop and every retention point |
| `assets/assembly/head-step-08.png` | `assembly/head-and-camera-gimbal.md` | Both finished columns side by side in their installed orientations, making the 180° rotation visible |
| `assets/assembly/head-step-09.png` | `assembly/head-and-camera-gimbal.md` | Both columns bolted to the top plate, with the 130 mm axis spacing and the 213.44 mm pitch-axis height dimensioned, and the cable exits through the plate visible |
| `assets/assembly/leg-exploded.png` | `assembly/leg.md` | The animation above carries no labels or part IDs. Still needed: one complete leg exploded along the kinematic chain, every part labelled with its part ID, the six actuators called out with their joint names |
| `assets/assembly/leg-step-01.png` | `assembly/leg.md` | The six actuators laid out and labelled, with a USB-CAN adapter connected to one of them on the bench |
| `assets/assembly/leg-step-02.png` | `assembly/leg.md` | The hip-pitch actuator, its coupler and its bearing retainer, exploded along the output axis; only these parts highlighted |
| `assets/assembly/leg-step-03.png` | `assembly/leg.md` | Hip-roll actuator, output shaft, support shaft and both bearing retainers exploded along the roll axis |
| `assets/assembly/leg-step-04.png` | `assembly/leg.md` | Hip-yaw actuator joined to the hip-roll output, showing how the yaw axis is oriented relative to the roll axis |
| `assets/assembly/leg-step-05.png` | `assembly/leg.md` | Knee actuator with its front bearing retainer and back cover, exploded along the knee axis |
| `assets/assembly/leg-step-06.png` | `assembly/leg.md` | Both shank halves and the lower-leg bearing going onto the knee, with the actuator cable route through the shank visible |
| `assets/assembly/leg-step-07.png` | `assembly/leg.md` | The ankle-pitch front and back parts closing around the actuator, exploded along the pitch axis |
| `assets/assembly/leg-step-08.png` | `assembly/leg.md` | Ankle-roll actuator, output shaft, support shaft and retainer, exploded along the roll axis |
| `assets/assembly/leg-step-09.png` | `assembly/leg.md` | Foot plate mounted to the ankle-roll output, viewed from underneath |
| `assets/assembly/leg-step-10.png` | `assembly/leg.md` | The finished leg with the harness routed and retained, showing every point where a cable crosses a moving joint |
| `assets/assembly/subassembly-map.png` | `assembly/index.md` | Build-order diagram showing that the two legs, two arms, two gimbal columns and two grippers are independent of each other and of the torso, and that all of them block final integration |
| `assets/assembly/tools-kitting-tray.png` | `assembly/tools.md` | A divided tray with fasteners counted into it by size, labelled — the kitting protocol above, made concrete |
| `assets/assembly/tools-limb-stand.png` | `assembly/tools.md` | The limb stand or jig used to hold a leg during assembly, once one exists |
| `assets/assembly/torso-exploded.png` | `assembly/torso-and-waist.md` | The animations above carry no labels. Still needed: the torso exploded — four plate types, waist actuator, computer, both packs, the six CAN adapters, the hubs and the IMU — every item labelled and every electronics item shown in its mounting position |
| `assets/assembly/torso-lifting-points.png` | `assembly/torso-and-waist.md` | The sling route and lifting points, once defined |
| `assets/assembly/torso-step-02.png` | `assembly/torso-and-waist.md` | The plate frame exploded, showing how the bottom, side and front plates join and in what order |
| `assets/assembly/torso-step-03.png` | `assembly/torso-and-waist.md` | The waist actuator in the frame, showing which side is pelvis and which is upper body, and the yaw axis |
| `assets/assembly/torso-step-04.png` | `assembly/torso-and-waist.md` | Top plate with the two gimbal mounting interfaces dimensioned, the ±65 mm offsets called out, and the through-holes for the camera cabling marked |
| `assets/assembly/torso-step-05.png` | `assembly/torso-and-waist.md` | Computer in position, airflow path shown, port face and cable exits visible |
| `assets/assembly/torso-step-06.png` | `assembly/torso-and-waist.md` | Both packs in position with their retention, and the swap path out of the torso |
| `assets/assembly/torso-step-07.png` | `assembly/torso-and-waist.md` | The six CAN adapters, three hubs, servo driver boards and converters in their mounting positions, each labelled with its bus or function |
| `assets/assembly/torso-step-08.png` | `assembly/torso-and-waist.md` | IMU in position with its axes drawn and labelled against the robot's base frame axes |
| `assets/images/exploded-overview.png` | `assembly/index.md` | Whole-robot exploded view, the seven subassemblies pulled apart along the axes they are joined on, each one labelled with the page that builds it. This is the one image a reader looks at before deciding whether to attempt the build, and it is the same file the home page and [What you get](../before-you-start/what-you-get.md) use — one render, four pages, so it lives under `assets/images/` rather than in this section's folder |

## Missing — named on a page but not yet placed (26)

These are named in a TODO block or an image manifest but have no placeholder
in the page body yet; add the placeholder in the commit that adds the file.

| Path | Page that will use it | What it must show |
| --- | --- | --- |
| `assets/images/camera-module.png` | `index.md, reference/faq.md` | One camera gimbal module alone, off the robot, dimensioned — so it can be judged as a component by someone who wants only the module. |
| `assets/images/safety-pinch-points.png` | `before-you-start/safety.md` | The robot with every pinch point marked on the real link geometry: between limb and torso, inside each joint, and the jaw closing line. |
| `assets/images/safety-lifting-points.png` | `before-you-start/safety.md, assembly/final-integration.md` | The sanctioned lifting points marked on the machine, with the sling route drawn, and the places that look like handles but are not. |
| `assets/images/safety-hanging-legs-straight.png` | `before-you-start/safety.md` | The robot correctly suspended with the legs hanging straight, next to the same robot hung wrong with the legs bent. Three bring-up sessions were lost to this exact mistake; the pair of images is the whole lesson. |
| `assets/images/safety-estop-location.png` | `before-you-start/safety.md, electrical/power-system.md` | Where the e-stop is mounted and how far an operator has to reach to hit it from outside the robot's envelope. Cannot be produced until an e-stop exists — see the punch list. |
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
| `assets/fabrication/machined-parts-laid-out.jpg` | `fabrication/incoming-inspection.md` | The full machined batch laid out and counted on arrival, grouped as the inspection procedure groups them. |
| `assets/fabrication/bearing-bore-measurement.jpg` | `fabrication/incoming-inspection.md` | A bearing bore being measured correctly, showing the instrument and where it sits on the part. |
| `assets/fabrication/printed-parts-orientation.png` | `fabrication/printing-guide.md` | Each structural printed part shown in its validated print orientation, with the load direction the layer lines must not align with drawn on it. |
| `assets/fabrication/heat-set-insert-seated.jpg` | `fabrication/printing-guide.md` | A heat-set insert correctly seated, next to one pressed in too far and one left proud. |

## Missing — per-part families (78)

One image per row of a BOM CSV. The filename **is** the `part_id`, so these
can be produced in a batch and dropped in without touching a page.

| Path pattern | Count | Page | What each must show |
| --- | ---: | --- | --- |
| `assets/bom/cnc/<part_id>.png` | 61 | `bom/cnc-parts.md` | One render per machined part, filename exactly the `part_id` in `cnc-parts.csv`. A machined part a builder cannot see is a part they will order wrong. |
| `assets/bom/electronics/<part_id>.jpg` | 11 | `bom/electronics.md` | One photograph per bought electronic part, filename exactly the `part_id` in `electronics.csv`, so a builder can confirm the thing in the box is the thing on the list. |
| `assets/bom/actuators/<part_id>.jpg` | 6 | `bom/actuators.md` | One photograph per Robstride model, filename exactly the `part_id` in `actuators.csv`. The models look alike and are not interchangeable. |

??? note "The 61 filenames for `assets/bom/cnc/<part_id>.png`"

    - `01_m03_shaft`
    - `02_hip_0_m04_back_bracket`
    - `03_hip_1_m04_front_retainer`
    - `04_hip_1_m04_shaft`
    - `05_hip_1_front_bracket`
    - `06_hip_1_back_bracket`
    - `07_hip_1_front_shaft`
    - `08_hip_1_back_shaft`
    - `09_hip_2_back_cover`
    - `10_m03_front_retainer`
    - `11_knee_m04_front_retainer`
    - `12_knee_m04_back_cover`
    - `13_knee_front_shaft`
    - `14_knee_back_shaft`
    - `15_ankle_cap`
    - `16_ankle_0_front_retainer`
    - `17_ankle_0_back_cover`
    - `18_ankle_1_back_retainer`
    - `19_ankle_1_m02_back_cover`
    - `20_ankle_1_front_retainer`
    - `21_ankle_1_front_shaft`
    - `22_foot_plate`
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
    - `CNC_arm05_RS02_shaft_bearing`
    - `CNC_arm06_RS02_shaft_coupler`
    - `CNC_arm07_elbow_front_bearing`
    - `CNC_arm08_elbow_back_bearing`
    - `CNC_arm09_elbow_output_shaft`
    - `CNC_arm10_r03_back_cover`
    - `CNC_arm11_wrist_roll`
    - `CNC_arm12_wrist_pitch`
    - `CNC_arm13_RS05_shaft_coupler`
    - `B1_body_base_plate`
    - `B2_body_top_plate`
    - `B3_body_side_plate`
    - `B5_body_shelf`
    - `CNC_body01_bottom_plate`
    - `CNC_body02_side_plate`
    - `CNC_body03_top_plate`
    - `CNC_body04_front_plate`

??? note "The 11 filenames for `assets/bom/electronics/<part_id>.jpg`"

    - `EL_COMPUTE_MINIPC`
    - `EL_BATTERY_6S`
    - `EL_CAM_D436`
    - `EL_IMU_TM171`
    - `EL_CAN_ADAPTER`
    - `EL_BUCK_12V_ENC`
    - `EL_BUCK_48V_12V`
    - `EL_TVS_DIODE`
    - `EL_SERVO_DRIVER`
    - `EL_SERVO_FEETECH`
    - `EL_USB_HUB`

??? note "The 6 filenames for `assets/bom/actuators/<part_id>.jpg`"

    - `ACT_RS00`
    - `ACT_RS02`
    - `ACT_RS03`
    - `ACT_RS04`
    - `ACT_RS05`
    - `ACT_RS06`

## Already here (7)

Real photographs of the reference robot, copied from the project repository's
`media/` directory. They show a working machine; none of them is an assembly
figure, and none of them substitutes for a render.

| Path | Used on | What it shows |
| --- | --- | --- |
| `assets/images/teaser.webp` | `index.md` | The robot in simulation and on hardware, side by side. |
| `assets/images/hardware.webp` | `index.md` | Hardware overview with all joints numbered and the three modules labelled. |
| `assets/images/hardware_tracking.mp4` | `index.md` | The reference robot tracking two independently moving targets. |
| `assets/images/vrw_fixed_vs_actuated.mp4` | `index.md` | Visible-reachable workspace, fixed head versus actuated camera modules. |
| `assets/images/hardware_close_front_back.mp4` | `assembly/head-and-camera-gimbal.md` | The two finished camera modules aiming independently. |
| `assets/images/two_target_handoff_left_right.mp4` | `bringup/acceptance-tests.md` | What passing acceptance test A10 looks like. |
| `assets/images/workspace.webp` | `reference/faq.md` | Visible-reachable workspace across six humanoid platforms. |

## Counting

| | |
| --- | ---: |
| Referenced by a page, missing | 54 |
| Named on a page, not yet placed | 26 |
| Per-part families | 78 |
| **Missing, total** | **158** |
| Present | 7 |

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

