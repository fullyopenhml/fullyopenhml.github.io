# Design

Why Duke Humanoid V2 is built the way it is: the engineering record behind the build instructions, including the options the team tried and dropped.

This section is written from the team's own design log, its spreadsheets, its
bench videos and its simulation recordings. It is history and rationale, not a
build guide. Nothing on these pages is an instruction; when a page here and a
build page disagree, the build page (and its red boxes) is the one to follow.
For what to buy and how to make it, go to [Actuators](../bom/actuators.md),
[CNC guide](../fabrication/cnc-guide.md) and
[Power system](../electrical/power-system.md).

## How to read the labels

Every block in this section carries one of four labels.

| Label | Meaning |
| --- | --- |
| **AS-BUILT** | Matches the finished reference robot, as far as the published code, BOM and team diagrams show. |
| **CONSIDERED — NOT USED** | Evaluated, prototyped or bought during design, and not on the finished robot. |
| **SUPERSEDED** | Was true at an earlier stage (for example the single-leg phase), and has since been replaced. |
| **DESIGN GOAL (not as-built)** | A target or estimate set before the build. The robot that was built differs from it. |

Anything the records do not settle is marked in red, exactly as on the build
pages: **UNVERIFIED**{ .dh-unverified } or **TODO**{ .dh-missing }.

## Design goals are not the as-built robot

**DESIGN GOAL (not as-built).** The team's design goal for V2 was a leg length of
0.3 m and a mass of 24 kg without arms (with a 1-DoF lower back). The robot as
built has a 0.39 m leg and weighs 36 kg with arms. The pre-build estimate with
arms was 34 kg, 2 kg under the as-built figure (computed). Read every goal and
estimate in this section against those numbers.
*Source: team actuator design spec, row "V2 DESGIN GOAL" (sic); team design log, "Estimated mass"; [Full specifications](../reference/full-specifications.md).*

## Timeline

| Date | What happened | Label | Page |
| --- | --- | --- | --- |
| 2024-10-26 to 2024-11-06 | Actuator teardown and weighing (RobStride 01, 02, 03, 04, 06), then bench tests in the vendor tool: RS04 jog (2024-11-04), RS01 stiffness sweep and RS03 back-drive (2024-11-06). | AS-BUILT models; RS01 CONSIDERED — NOT USED | [Actuator selection](actuator-selection.md) |
| 2025-02-27 | First-article fit check of the V2 CNC parts: four rework cases and one CAD thread error. | AS-BUILT (history) | [Structure and manufacturing](structure-and-manufacturing.md) |
| 2025-03-01 | Single-leg phase: body box, battery holders, IMU and computer mounts, and the slider mount built. | SUPERSEDED | [Single-leg phase](single-leg-phase.md) |
| 2025-04-23, 04-24 and 04-30 | Actuator sizing study in simulation: five motor configurations, walking and running. | CONSIDERED — NOT USED (earlier toolchain) | [Actuator sizing in simulation](actuator-sizing-simulation.md) |

*Sources: photo and video dates (EXIF and on-screen logs) for the bench work; title slide of the team deck "Tolerance Check V2 CNC"; single-leg photo dates; simulation recording filenames and on-screen timestamps.*

## Pages in this section

<div class="grid cards" markdown>

-   :material-scale-balance: **[Torque targets and mass](torque-targets-and-mass.md)**

    Leg torque targets from human gait papers and other robots, the V2 design
    goal, design ranges of motion, and the pre-build mass budget.

-   :material-engine: **[Actuator selection](actuator-selection.md)**

    The six RobStride models on the robot, the 19-candidate trade study,
    teardown masses, bench tests and the torque-sensor bench.

-   :material-chart-line: **[Actuator sizing in simulation](actuator-sizing-simulation.md)**

    Five weak/strong motor configurations tried in simulation, what saturated,
    and how the result compares with the robot as built.

-   :material-hammer-wrench: **[Structure and manufacturing](structure-and-manufacturing.md)**

    Aluminium, the team's CNC design rules, the fastener standard, part
    labelling and the first-article fit check.

-   :material-chip: **[Electronics and sensing](electronics-and-sensing.md)**

    The IMU, cameras and software bindings that made it onto the robot, and the
    CAN, power and sensing options that did not.

-   :material-walk: **[Single-leg phase](single-leg-phase.md)**

    The March 2025 single-leg build: test plan, rig options, the first CAN ID
    scheme and photos of the body build.

</div>
