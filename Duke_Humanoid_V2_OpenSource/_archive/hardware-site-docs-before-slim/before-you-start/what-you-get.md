# What you get

The manifest for this release: which artefacts exist, where they live, and what
is deliberately not included. Read it before you plan a build, so that you
discover a missing artefact now rather than halfway through fabrication.

## Status of every artefact a build needs

Legend: **published** — you can download it today. **partial** — something exists
but not in a form you can build from. **not published** — it does not exist
outside the lab yet. Every row that is not *published* carries a red
**TODO**{ .dh-missing } mark.

| Artefact | Status | Where it is, or what is missing |
| --- | --- | --- |
| Policy training and paper reproduction package | published | [`duke_humanoid_v2_simulation`](https://github.com/generalroboticslab/duke_humanoid_v2_simulation) |
| Onboard control stack | published | [`duke_humanoid_v2_deploy`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy) |
| Robot model (MJCF), collision and visual meshes | published | `simulation/asset/duke_v2/humanoid_v21/` |
| Camera gimbal and gripper models | published | `simulation/asset/duke_v2/head_cam/` and `parallel_gripper/` |
| Code licence | published | Apache-2.0, all three repositories |
| Citation metadata | published | `CITATION.cff` in each repository |
| Operator runbook and software safety contract | published | `deploy/control/docs/` |
| Team power and data wiring diagrams (V2) | published | [Power system](../electrical/power-system.md) and [CAN bus](../electrical/can-bus.md) |
| Exploded-view CAD animations, 9 clips | published | On the [assembly](../assembly/index.md) pages. The animations carry no part labels, so each clip's caption says what moves |
| Design record: torque targets, actuator selection, simulation sizing study, single-leg phase, with team photos and videos | published | [Design](../design/index.md) |
| **Original CAD (STEP) for machined parts** | **TODO**{ .dh-missing } not published | The simulation export states plainly that it leaves the original `*.step` files out. Simulation meshes are not manufacturing geometry: they carry no tolerances, no threads and no finish. |
| **STL / 3MF for printed parts** | **TODO**{ .dh-missing } not published | — |
| **Print profiles** | **TODO**{ .dh-missing } not published | Material, layer height, walls, infill, orientation, supports, per part |
| **Bill of materials** | **TODO**{ .dh-missing } partial | Published here as versioned CSV data and reconciled against the source spreadsheet — but fasteners and printed materials are still placeholder rows, so every total is a floor. See [Bill of materials](../bom/index.md) |
| **Fastener schedule** | **TODO**{ .dh-missing } not published | Every screw, nut, washer and bearing is one `$0.00` placeholder row today |
| **Torque values** | **TODO**{ .dh-missing } not published | No torque value exists for any fastener. The threadlocker is answered: Loctite 222 (*source: team design log, "Hardware Choice"*) |
| **Assembly instructions** | **TODO**{ .dh-missing } not published | — |
| **Harness drawings and connector pinouts** | **TODO**{ .dh-missing } not published | The team wiring diagrams above are not harness drawings |
| **Dimensioned drawings, tolerances, surface finishes** | **TODO**{ .dh-missing } not published | None of the 63 machined part rows carries material, tolerance, finish or supplier |
| **Hardware licence** | **TODO**{ .dh-missing } not declared | See [Citation and licence](../reference/citation-and-license.md) |
| **Documentation licence** | **TODO**{ .dh-missing } not declared | Same page |
| **A tagged release that pins all of the above** | **TODO**{ .dh-missing } not published | None of the three repositories has a tag, so nothing can be pinned to a known-good state |

!!! missing "A build is not currently possible"
    The bolded rows are the ones that stop a second builder, and there are enough
    of them that no amount of care on the reader's side closes the gap. This site
    exists to get those rows to *published*, in the open, with their holes
    visible while they are being filled.

## What this site adds

Everything a second builder needs that code cannot provide: the bill of
materials, the fabrication data, the assembly sequence, the wiring, and the
bring-up procedure — plus the safety material that has to come before any of it.

See [Software](../software.md) for what the three repositories do and where the
boundary between them and this site lies.

## What is deliberately not included

The team's raw design log is **not** published. The facts this
site uses from it are transcribed into the [Design](../design/index.md) section
and the build pages, each with a short source note, and the vendor manuals,
papers and figures it cites are listed, not copied, on
[Citation and licence](../reference/citation-and-license.md).

!!! missing "MISSING — The scope boundary: what is deliberately not included"
    State the scope boundary explicitly, so a builder stops hunting for files
    that were never meant to ship. For each of the following, say *in scope* or
    *out of scope*:

    - The teleoperation setup used for data collection.
    - The training workstation and its GPU requirements.
    - Any motion-capture or instrumentation rig.
    - Development test fixtures — in particular the single-leg tester, whose
      plate sits inside the source spreadsheet's machining subtotal (this site
      holds it in `test-fixtures.csv` and excludes it from every total).
    - The cube targets and tripod fixtures in the perception assets.
    - The charging bench and gantry, which are needed to build but are not part
      of the robot.

    *Owner: hardware lead.*

## Which robot this describes

The published robot model lives under an asset directory named `humanoid_v21`,
which is the closest thing to a hardware revision identifier that exists today.
This site documents exactly one physical revision, and every page should be
readable as applying to that revision only.

!!! missing "MISSING — The hardware revision identifier this site documents"
    Confirm the revision identifier this site documents, state whether
    `humanoid_v21` is it, and map it to a tagged commit of the assets. See
    [Revisions](../reference/revisions.md).

    *Owner: hardware lead.*
