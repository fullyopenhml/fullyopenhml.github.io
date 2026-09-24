# Revisions

Which physical robot this site describes, and what happens to these pages when
the hardware changes. A builder must be able to tell whether a page applies to
the machine in front of them.

## Why a hardware site needs this and a software site does not

Software users upgrade. Hardware users cannot. Once someone has had 63 parts
**UNVERIFIED**{ .dh-unverified } machined (63 is the source sheet's row count;
the per-robot part count has not been checked against CAD), they own that revision forever, and a documentation site that silently
edits its pages to describe a newer robot has destroyed their build instructions
without telling them.

The comparable projects show both outcomes. OpenArm keeps a complete
documentation tree per hardware version: its 1.0 tree still carries the full
seven-page bill of materials, the ten-page assembly guide and the wiring guide,
so somebody who built a 1.0 arm still has their instructions even though the
current version's tree does not yet have an assembly guide at all. That is the
behaviour to copy. The failure mode is the opposite one — one mutable tree, edited
in place, where a reader cannot tell which robot a page is about.

## What this site documents

The published robot model lives under an asset directory named `humanoid_v21`,
which is the closest thing to a revision identifier this release has. It has
never been declared as one.

!!! missing "Nothing can be pinned today"
    None of the three repositories carries a tag or a release. There is no commit,
    no version string and no archive that a builder can cite as "the robot I
    built". Until there is, every link on this site points at a moving target —
    including the links to the CAD a builder would machine from.

!!! missing "MISSING — Revision identifier, tagged release, documentation model, bump rule"
    The four decisions that make this page real:

    1. **Declare the revision identifier** this site documents, and say whether
       `humanoid_v21` is it or whether the hardware gets its own scheme
       independent of the asset directory name.
    2. **Tag the repositories** and cut a release that pins the code, the assets
       and the CAD together. A hardware revision that cannot be downloaded as a
       fixed set is not a revision.
    3. **Choose the documentation model** — a separate tree per hardware revision,
       or a single documented revision with old ones archived. Either is
       defensible; editing in place is not.
    4. **Write the bump rule**: what change forces a new revision. A starting
       point is any change that makes a previously made part non-interchangeable,
       any change to mass or geometry the policy depends on, and any change to the
       harness or bus layout.

    *Owner: hardware lead + PI.*

## Changelog

### V1 to V2, at design-goal level

The team's design-spec table compares V1 with the V2 **design goal**. This is
the intent, not a physical changelog, and the V2 goal is not the as-built robot
(see [Full specifications](full-specifications.md#design-goals-design-goal-not-as-built)).

| | Duke Humanoid V1 | V2 design goal |
| --- | --- | --- |
| Leg length | 0.5 m | 0.3 m |
| Leg DoF | 5, no ankle roll | 6, adds ankle roll (AR) |
| Mass | 30 kg | 24 kg, without arms |
| Joint torques (N·m) | HAA 238, HA 238, HFE 264, KFE 238, AFE 132 | HAA 60, HA 60, HFE 60, KFE 80, AFE 45, AR 20 |

*Source: team design log, "V2 humanoid actuator design spec" table.*

### Development timeline

Dates come from on-screen logs, photo metadata and the documents themselves.

| When | What | Where it is described |
| --- | --- | --- |
| October–November 2024 | Actuator bench tests and teardown: RS04, RS03 and RS01 run from the vendor tool, actuators weighed, a Teensy CAN prototype built and dropped | [Actuator selection](../design/actuator-selection.md), [Electronics and sensing](../design/electronics-and-sensing.md) |
| 27 February 2025 | First-article fit check of the CNC parts: four rework cases and one CAD thread error (M4 holes where M5 were needed) | [Structure and manufacturing](../design/structure-and-manufacturing.md), [Incoming inspection](../fabrication/incoming-inspection.md) |
| 1 March 2025 | Single-leg-phase build: body box, batteries, IMU, computer and slider mount | [Single-leg phase](../design/single-leg-phase.md) |
| April 2025 | Simulation study of actuator sizing (Isaac Gym, not in the release) | [Actuator sizing in simulation](../design/actuator-sizing-simulation.md) |

*Source: team design log; team CNC tolerance-check deck; team photos and
videos.*

### Superseded during development

These appear in the team records but are **not** the robot this site documents.
Do not build to them.

| Earlier record | As built | Source of the as-built value |
| --- | --- | --- |
| Jetson Orin NX onboard computer (setup notes linked from the team log; a "Jetson" in the pre-build mass budget) | MINISFORUM X1-470 mini PC | This site's BOM; team power wiring diagram (V2) |
| Single-leg motor CAN IDs: waist 26 (0x1A), left leg 27–32, right leg 43–48 | Waist 1, left leg 31–36, right leg 41–46 | `deploy/control/humanoid_config.py` |
| udev interface names `can10`–`can15` (a block labelled "v2 humanoid" in the team log) | `can9`, `can21`–`can25` | `deploy/control/humanoid_config.py`; team data wiring diagram (V2) |

*Source: team design log (earlier records).*

!!! missing "MISSING — Hardware changelog: V1 to V2, and any V2 revisions"
    There is no physical hardware changelog. The design-goal comparison above
    narrows it, but two entries are still owed:

    - **V1 → V2**, at the hardware level: what physically changed, and which V1
      parts, if any, carry over. The two-independently-aimed camera modules are
      the headline, but a changelog has to cover the rest.
    - **Any V2 revision** made during development. If the robot in the lab is not
      the robot the published meshes describe, that has to be stated here before
      anyone machines anything.

    *Owner: hardware lead.*

## Licence change between generations

Duke Humanoid V1 was released under MIT. V2 is Apache-2.0. Downstream users who
worked from V1 will assume the MIT terms carry over unless this is stated
explicitly — and neither licence covers the hardware design files, which have no
licence at all yet (**TODO**{ .dh-missing }). See [Citation and licence](citation-and-license.md).

!!! missing "MISSING — V1 (MIT) to V2 (Apache-2.0) migration note"
    Add a one-paragraph migration note stating the V1 (MIT) → V2 (Apache-2.0)
    change and what it means for anyone reusing V1 material.

    *Owner: PI.*
