# Skills and shop access

What this build assumes you can already do and already reach. This is the page
that tells an interested reader whether the project is realistic for them before
they spend anything.

## Fabrication access

| Capability | Why it is needed |
| --- | --- |
| 3-axis CNC milling, or a machining vendor you can send geometry to. **UNVERIFIED**{ .dh-unverified }: nobody has checked that 3-axis work is enough — see below | 63 machined part rows in the source parts list; {{ bom_count("cnc-parts.csv") }} on this site, after removing a duplicate and the test fixture |
| FDM 3D printing | PLA and TPU appear in the materials list |
| SLS 3D printing, or an SLS service bureau | Nylon powder appears in the materials list |
| Bearing and press fits | Quasi-direct-drive joints put bearings directly in machined housings |
| Inspection — at minimum a digital caliper, ideally a bore gauge and a surface plate | Machined parts arrive wrong; the time to find out is before assembly, not during. The team's own first-article check in February 2025 used a hand-held digital caliper reading in mm to two decimal places, and recorded four rework cases (*source: team CNC tolerance-check deck*). See [Incoming inspection](../fabrication/incoming-inspection.md) |

!!! missing "MISSING — Machining axes, work envelope, SLS substitution and finish"
    Four answers a reader needs before they can tell whether their shop is
    enough, all of which come straight out of the CAD:

    - Whether any part requires **4- or 5-axis** work, or turning. If even one
      does, a reader with a 3-axis mill needs to know exactly which part.
    - **Minimum work envelope**, from the largest part's bounding box.
    - Whether the **SLS parts can be substituted with FDM**, and at what cost in
      strength — SLS access is the narrowest constraint on this list.
    - Whether anodising or another **finish** is required, and on which parts.

    *Owner: hardware lead, from the CAD. Blocks [CNC guide](../fabrication/cnc-guide.md).*

## Electrical and assembly skills

| Skill | Where it is used |
| --- | --- |
| Soldering high-current connectors | The power distribution uses XT30 connectors throughout. The team solders the XT30 solder cups with the iron at about 480 °C, tinning the cup until solder wets the gold plating (*source: team design log, motor-power soldering checklist*) |
| Crimping and terminating signal connectors | Motor, encoder and sensor harnesses |
| Soldering twisted-pair CAN joints | The team solders CAN_H and CAN_L inline with no branch stubs, keeps the twist to within 10–15 mm of the joint, and checks for about 60 Ω across a terminated bus (*source: team design log, CAN soldering checklist*) |
| Building a multi-drop CAN bus, including termination | The body motors sit on **six** CAN buses at 1 Mbit/s |
| Installing heat-set inserts with a soldering iron | The team melted heat-set inserts into printed battery holders this way in the single-leg phase build (*source: team build photos, March 2025*). See [Single-leg phase](../design/single-leg-phase.md) |
| Working safely with lithium-polymer packs | Two 6S packs. See [Safety](safety.md) |
| Reading a mechanical drawing well enough to reject a part | Incoming inspection |

## Software and systems skills

You are not done when the robot is assembled. The machine is brought up through a
Linux stack that assumes real administration.

| Skill | Why |
| --- | --- |
| Linux administration on the onboard computer | Kernel modules, `udev` rules to give the six CAN adapters stable names, and per-process CPU pinning are all part of documented bring-up |
| Comfort with a terminal ladder | The operator runbook brings the stack up as an ordered sequence of long-running processes, not as one command |
| Basic Python | Configuration and calibration are Python scripts, not a GUI |

!!! note "You need a second, CUDA-capable machine"
    The control stack splits across three roles: the **robot computer**, which
    runs everything except the planner and needs no CUDA; a **GPU machine** that
    runs the cuRobo plan and MPC server; and an **operator console**, which can be
    any laptop with `ssh`. Budget for the GPU machine — it is not in the robot's
    parts list, and the robot cannot do a planned grasp without it.

!!! missing "MISSING — minimum specification and cost of the GPU machine"
    The page tells a builder to budget for a GPU machine that runs the cuRobo
    plan and MPC server, but no page on this site states what it needs: GPU
    model or minimum VRAM, CPU, RAM, operating system and CUDA version, the
    machine used on the reference robot, or what it cost. Without this a builder
    cannot budget for it.

    *Owner: controls lead.*

## People, space and equipment

The machine is 36 kg. Several assembly steps and every lift are two-person
operations, and powered testing needs a second person whose only job is the
emergency stop.

You also need a place to do this: a bench that can take the subassemblies, a
gantry or hoist to hang the robot from during bring-up, a charging station away
from anything flammable, and clear floor under the robot.

!!! missing "MISSING — Two-person and hoist steps, bench and floor space, gantry spec"
    - Which specific steps require a **second person**, and which require a
      **hoist** rather than a person. Mark them on the step pages as well.
    - Bench and floor space actually used, so a reader can check their room.
    - The gantry specification, which today exists only as an assumption inside
      an operations document. See [Safety](safety.md).

    *Owner: hardware lead.*

!!! missing "MISSING — A prerequisite-skills list confirmed by a real build"
    Turn the skill tables above into an honest "you should have done X before"
    list, confirmed against the real build rather than assumed. The candidates
    are already listed here; what is missing is somebody who has done the build
    saying which of them actually mattered and which were easy.

    *Owner: whoever performs the first external build.*
