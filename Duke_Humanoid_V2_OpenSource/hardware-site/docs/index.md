# Duke Humanoid V2 — Hardware

Everything needed to build an identical Duke Humanoid V2: what to buy, what to machine and print, how to assemble, wire and bring it up. The control code is open too: [Software](software.md).

<figure markdown>
  ![Duke Humanoid V2 hardware overview with joints numbered](assets/images/hardware.webp){ loading=lazy }
  <figcaption>Orange: the 31 actuated joints — (1–7) shoulder pitch / roll / yaw, elbow, wrist roll / pitch / yaw; (8) waist; (9–14) hip pitch / roll / yaw, knee, ankle pitch / roll; (15–16) camera yaw / pitch. Green: (I) camera, (II) gripper, (III) onboard computer. Dimensions in mm.</figcaption>
</figure>

## Build path

<div class="grid cards" markdown>

-   :material-cart: **1 · Buy** — every part, quantity and price. [Bill of materials →](bom/index.md)
-   :material-hammer-screwdriver: **2 · Make** — CAD files, {{ bom_count("cnc-parts.csv") }} machined parts, {{ bom_count("printed-parts.csv") }} printed parts. [Fabrication →](fabrication/index.md)
-   :material-wrench: **3 · Assemble** — legs, arms, torso, camera columns, grippers, then the whole robot. [Assembly →](assembly/index.md)
-   :material-flash: **4 · Wire** — 48 V power, six CAN buses, every cable to make. [Electrical →](electrical/index.md)
-   :material-power: **5 · Bring up** — motor IDs, zeroing, camera calibration. [Bring-up →](bringup/index.md)
-   :material-check-decagram: **6 · Verify** — eleven acceptance tests, hung then walking. [Acceptance tests →](bringup/index.md#acceptance-tests)

</div>

## At a glance

| | |
| --- | --- |
| Joints | 31 RobStride quasi-direct-drive actuators: waist 1, each leg 6, each arm 7, each camera gimbal 2 |
| Size and mass | 1.26 m tall with camera masts; 35 kg (CAD) |
| Cameras | 2 × Intel RealSense D436, each on its own yaw–pitch gimbal |
| Grippers | 2 × rack-and-pinion parallel grippers, one Feetech bus servo each |
| Power | 2 × 6S 10 000 mAh LiPo in series (44.4 V); 12 V for the computer and grippers |
| Computer | MINISFORUM X1-470 mini PC onboard; a separate CUDA machine runs the planner |
| Structure | Machined aluminium 6061 frame and joints; printed PLA, TPU and SLS nylon covers and brackets |
| Parts cost | {{ bom_total() }} for the parts list; consumables, tools and shipping not included |
| Also needed | A gantry rated 50 kg or more with 1.4 m of clear height, and two people |

Full numbers: [Reference](reference/index.md).
