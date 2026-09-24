# Assembly

How the robot goes together, subassembly by subassembly. Build the limbs and
modules first, integrate last: a leg that has to come apart again is far cheaper
than a whole robot that does.

!!! missing "Structure only — do not build from this section yet"
    Every page here is a **skeleton**: the step sequence, the parts that belong
    to each step, and the checks that gate each step are laid out, but the
    fastener schedule, the torque values, the press fits and the published CAD
    do not exist yet. Each missing item is marked with a red **MISSING** box where it belongs,
    with the person who can supply it. Nothing on these pages has been verified
    against a photographed build.

## The whole robot

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/images/exploded-overview.png`: whole-robot exploded view, the seven
> subassemblies pulled apart along the axes they are joined on, each one
> labelled with the page that builds it. This is the one image a reader looks
> at before deciding whether to attempt the build, and it is the same file the
> home page and [What you get](../before-you-start/what-you-get.md) use — one
> render, four pages, so it lives under `assets/images/` rather than in this
> section's folder.

No labelled overview exists yet, but the team's unlabelled CAD animations of
each subassembly are on the pages that build them: one arm on [Arm](arm.md);
one leg and the pelvis block on [Leg](leg.md); the torso frame, front bay,
rear bay and covers on [Torso and waist](torso-and-waist.md); one camera
column on [Head and camera gimbal](head-and-camera-gimbal.md); and the camera
columns and grippers coming off the whole robot on
[Final integration](final-integration.md).

The machine is 31 DoF, 36 kg, 1.2 m tall: a waist, two 6-DoF legs, two 7-DoF
arms, two 2-DoF camera gimbals and two single-DoF grippers. Thirty-one
RobStride quasi-direct-drive actuators carry every joint except the grippers,
which are Feetech bus servos.

## Order of work

Build in this order. It is the order in which a mistake is cheapest to undo,
and it matches the way the actuator buses are grouped.

| # | Subassembly | Build | Page | Actuators in it |
| --- | --- | --- | --- | --- |
| 0 | Tools and consumables | once | [Tools](tools.md) | — |
| 1 | Leg | ×2 | [Leg](leg.md) | 6 RobStride per leg |
| 2 | Arm | ×2 | [Arm](arm.md) | 7 RobStride per arm |
| 3 | Torso and waist | ×1 | [Torso and waist](torso-and-waist.md) | 1 RobStride (waist) — or 3 if the shoulder-pitch actuators go in here **UNVERIFIED**{ .dh-unverified } |
| 4 | Camera gimbal column | ×2 | [Head and camera gimbal](head-and-camera-gimbal.md) | 2 RobStride per column |
| 5 | Gripper | ×2 | [Gripper](gripper.md) | 1 Feetech servo per gripper |
| 6 | Whole robot | ×1 | [Final integration](final-integration.md) | — |

Then go to [Electrical](../electrical/index.md), and only then to
[Bring-up](../bringup/index.md).

!!! unverified "UNVERIFIED — this build order has not been confirmed against a real build"
    Confirm this ordering against a real build. Two things could change it:

    - Whether the harness must be partly installed **inside** a limb before that
      limb is closed up. If so, [Electrical](../electrical/index.md) has to
      interleave with this section rather than follow it, and each limb page
      needs an inline "install this harness branch now" step.
    - Whether the torso must exist before a limb can be supported for its own
      final checks.
    - Where the hips and shoulders split. The team's CAD animations group the
      waist and both legs' `hip_1` and `hip_2` actuators into one pelvis block,
      while the [Leg](leg.md) page builds all three hip joints into each leg.
      The torso-frame CAD also holds both shoulder-pitch actuators in the side
      plates, while the [Arm](arm.md) page builds them as the first joint of
      each arm, and the table above counts them in the arms.

    *Owner: hardware lead.*

## Configure the motors before you pick up a tool

Every subassembly page opens with the same blocking prerequisite, because every
RobStride joint on this robot is addressed by a CAN ID that has to be set with
the actuator on a bench, not buried inside a limb.

The ID and bus for all 31 joints are fixed by
[`control/humanoid_config.py`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/humanoid_config.py)
in the deploy repository — that file is the source of truth, and each assembly
page reproduces the rows it needs. Six CAN buses run at 1 Mbit/s:
`can9`, `can21`, `can22`, `can23`, `can24`, `can25`.

See [Motor ID and config](../bringup/motor-id-and-config.md).

## Time and effort

!!! missing "MISSING — build time and crew size per subassembly"
    No build has been timed. The site must not publish a guess, because a reader
    plans shop time, shipping and help around this number.

    What has to be recorded during the first documented build, per subassembly:
    elapsed hands-on hours, how many people were needed at once, and which
    steps needed the hoist. Publish the numbers for a *second* build rather than
    the first — the first build includes discovering the procedure.

    *Owner: whoever performs the first externally documented build.*

## The shape of a step page

The convention here is taken from two projects that publish working build
guides, plus one addition of our own.

- **From [Asimov](https://docs.menlo.ai/asimov/1/assembly-steps)** — a
  **Parts needed** table at the top of every step, listing exact part IDs and
  counts, with `Threadlocker | As needed` as a line item. Asimov puts one such
  table on 78 of its 83 step pages, which is what lets a builder kit a step out
  before touching it. The threadlocker *grade* is named once, on the tools page,
  and never repeated in a step — we do the same, on [Tools](tools.md).
- **From [OpenArm](https://docs.openarm.dev/1.0/hardware/assembly-guide/)** —
  subassemblies ordered along the kinematic chain, one figure per step showing
  only the parts being joined, every step naming its fastener size and count,
  and a **blocking warning at the top of each subassembly page** that gates
  mechanical work behind motor-ID configuration.
- **Our addition: torque.** Neither project publishes a single N·m value.
  Every step on this site therefore has an explicit torque field. Where the
  value is not known it says so, in a red **MISSING** box, rather than being
  left silently absent — this is the one gap a careful reader cannot close by
  reading more carefully.

We deliberately did **not** copy Asimov's one-page-per-step structure. Asimov
has 83 pages because it ships an interactive 3D player per instruction; with
still renders, one page per subassembly keeps a whole limb on one screen and
makes the parts for a limb searchable in one place.

Each step gives, in this order:

1. a **numbered imperative title** — what this step accomplishes,
2. a **Parts needed** table — part ID, quantity, description,
3. the **figure** for the step,
4. the **fastener, torque and threadlocker** fields,
5. a **Checkpoint** — what must be true before the next step starts.

### How to read the parts tables

- **Part IDs** are the CNC part numbers from the internal machining sheet and
  the actuator models from the motor table. They are reproduced here exactly as
  they are recorded, including the `_xN` suffix.
- **Machined-part quantities are withheld almost everywhere, on purpose**, and
  the Qty cell reads **TODO**{ .dh-missing } instead. In the source
  sheet the `_xN` count embedded in 25 of 63 part names disagrees with the
  sheet's own quantity column. Publishing either number would make a reader
  order the wrong quantity of a machined part. The conflict is tracked on
  [CNC parts](../bom/cnc-parts.md); until it is resolved, the honest value is
  no value.
- Part IDs will move: the sheet mixes three naming systems (`CNC_leg01…`,
  `01_m03_shaft_x3…`, `B1_body_base_plate`), and the older two look like
  single-leg test-rig leftovers. See [Part index](../reference/part-index.md).

### A worked example of the format

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| `RS03` — motor ID 31, bus `can24` | 1 | RobStride 03 actuator, pre-configured |
| `CNC_leg01_x2_hip_center_back` | **TODO**{ .dh-missing } | Hip centre, back |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

{{ step(1, "Example step") }}

Step text, in the imperative: *press the bearing into the bore until it seats
against the shoulder*.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/<page>-step-NN.png`: the two parts being joined, highlighted,
> everything else ghosted. *(Illustrative only — this example needs no figure.)*

!!! missing "Example gap box — illustrative only, not a tracked item"
    Fasteners: size, count, head type, tightening pattern.
    Torque: no N·m value exists for this interface.
    Threadlocker: whether this interface takes it.
    *Owner: hardware lead.*

{{ checkpoint("The shaft turns freely by hand with no detectable axial play.") }}

## Figures this section needs

Every page ends with its own figure manifest. The whole-section list, for
whoever renders them. None of these figures exists yet **TODO**{ .dh-missing }.

| File | Page | What it must show |
| --- | --- | --- |
| `assets/images/exploded-overview.png` | this page, home, What you get, Bill of materials | Whole robot exploded into its seven subassemblies, each labelled with the page that builds it |
| `assets/assembly/subassembly-map.png` | this page | The build order as a diagram: which subassemblies can be built in parallel and which block others |

Naming rule for everything else: `assets/assembly/<page>-step-NN.png`, where
`<page>` is the filename of the page it appears on — `leg-step-03.png`,
`head-step-07.png`. Overview renders are `<page>-exploded.png`. Once a file
exists, replace the figure placeholder line with a normal image, for example
`![Hip pitch actuator seated in the hip centre](../assets/assembly/leg-step-02.png)`,
and delete its row from the manifest.

Every figure this section is waiting for is listed, with the brief for each, in
the site-wide [image manifest](../assets/MANIFEST.md). Do not write a real
`![](…)` before the file exists: `mkdocs build --strict` fails on a link to a
missing image, and it fails the whole site, not just this page.

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/subassembly-map.png`: build-order diagram showing that the
> two legs, two arms, two gimbal columns and two grippers are independent of
> each other and of the torso, and that all of them block final integration.
