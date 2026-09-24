# Tools

Everything needed to build the robot, separate from the robot's own parts.
Costing tools separately matters: a reader who already owns them sees a very
different total from one who does not.

Tools subtotal: {{ bom_subtotal("tools.csv") }}
(prices checked {{ bom_priced_as_of("tools.csv") }};
unpriced entries: {{ bom_unpriced("tools.csv") }}).

The linked products in this list, once they exist, are references and not a
requirement to buy a particular brand. No product link exists yet
**TODO**{ .dh-missing }. **None of them will be affiliate links.**

!!! unverified "UNVERIFIED — this tool list is not complete and has not been checked against a build"
    Most of the tool list is derived from what the parts list and the assembly
    pages imply, not from a build that has actually been performed. Items whose
    *specification* depends on documents that do not exist yet — the fastener
    schedule, the torque values, the press fits — say so. Do not treat the
    absence of a tool from this page as evidence you will not need it.

    *Owner: hardware lead, from the first documented build.*

## Before you start: kit the hardware out

Adopted from [ToddlerBot](https://toddlerbot.github.io/), whose manual opens
with it: **count every fastener into a divided tray before the first step, by
size.** At the end of the build, a leftover fastener is not a spare — it is
evidence that a step was missed. This only works once the fastener schedule
exists; see [Fasteners and hardware](../bom/fasteners-and-hardware.md).

## Required

### Hand tools

| Tool | What this build needs it for | Specification |
| --- | --- | --- |
| Torx drivers — or metric hex drivers / Allen keys **UNVERIFIED**{ .dh-unverified } | Almost every fastener on the robot | The team hardware standard specifies **Torx** button-head screws, so Torx drivers, not hex keys, are the likely need (see *UNVERIFIED — Torx or hex drive* further down this page). Driver size is not given anywhere **TODO**{ .dh-missing }; the full set of sizes is whatever the fastener schedule contains, and that schedule does not exist yet |
| Torque driver or torque wrench, bits to match the screw drive | Every fastener that has a torque value | **TODO**{ .dh-missing } — range cannot be chosen until torque values exist. A driver whose range does not cover the values is worse than none |
| Screwdrivers | Battery-switch and cover screws | **TODO**{ .dh-missing } — head types not yet catalogued |
| Flush cutters | Trimming cable ties and sleeving | Any |
| Wire strippers | Harness fabrication | Sized for the harness wire gauge — **TODO**{ .dh-missing }, see [Harness fabrication](../electrical/harness-fabrication.md) |
| Soldering iron and solder | XT30 connector joints. The parts list carries 30 pairs of XT30 connectors and four 5-piece XT30 (2+2) sets, so soldered power joints are unavoidable. Also used to melt heat-set inserts into printed parts | The team's XT30 soldering checklist sets the iron at about **480 °C** for the XT30 solder cups. *Source: team design log, motor power wire (XT30) soldering checklist.* The team's single-leg-phase build photos (March 2025) show heat-set inserts being installed with a soldering iron |
| Heat gun | Heat-shrink over soldered joints | Any |
| Multimeter | Continuity and polarity before power, voltage checks after | Any. Required by [Pre-power checks](../electrical/pre-power-checks.md) |
| Crimp tool | Signal-side connectors | **TODO**{ .dh-missing } — the harness does not yet name its signal connector, so the crimp tool cannot be named either |

### Lifting and support

| Tool | What this build needs it for | Specification |
| --- | --- | --- |
| Hoist or gantry, plus sling | The finished robot is **36 kg**. It is lifted during final integration and every time it is hung for bring-up | Rated **well above 36 kg**, with the margin your local rules require. See [Safety](../before-you-start/safety.md) |
| Limb stand or jig | Holding a leg or arm while it is built and while its joints are checked | **TODO**{ .dh-missing } — no jig is documented. If the first build used one, publish it as a printed part |

The operations manual for the built robot requires that the **legs hang
straight** when the robot is suspended; a bent-leg hang tilts the torso and
corrupts the geometry the perception stack depends on. Whatever you hang the
robot from has to allow that, so choose the hoist and the hang point together.

### Electrical and battery

| Tool | What this build needs it for | Specification |
| --- | --- | --- |
| LiPo balance charger | The robot runs on two 6S 22.2 V 10000 mAh LiPo packs | 6S-capable, with balance leads matching the packs |
| LiPo charging bag or case, fire-rated | Charging and storing those packs | Sized for a 10000 mAh 6S pack |
| Computer with USB | Setting actuator CAN IDs and Feetech servo IDs before assembly | Linux, per [Software](../software.md) |
| USB-CAN adapter | Talking to a RobStride actuator on the bench | The robot's own CANable PRO V2.0 adapters can be used for bench configuration |
| Feetech servo driver board | Setting gripper servo IDs on the bench | The robot's own Waveshare ST/SC bus servo driver boards can be used |

### Consumables

| Item | Where it is used | Specification |
| --- | --- | --- |
| Threadlocker | Named per step as *As needed*; the **grade is named only here**, never in a step | **Loctite 222**, a removable grade. *Source: team design log, "Hardware Choice".* Do not substitute a higher-strength grade, and do not apply it to every fastener indiscriminately. Which interfaces take it is not recorded **TODO**{ .dh-missing } |
| Heat-shrink tubing | Every soldered power joint | Assorted, sized over XT30 joints |
| Cable ties and anchors | Harness retention | **TODO**{ .dh-missing } — retention scheme not documented |
| Masking tape and a marker | Labelling each actuator with its joint name and CAN ID **before** it goes into a limb. Once an actuator is inside a leg, its ID is no longer visible and is no longer changeable without disassembly | Any |
| Isopropyl alcohol and lint-free wipes | Cleaning machined parts of cutting fluid before assembly, cleaning the camera glass | Any |
| Gloves | Handling freshly machined aluminium | Cut-resistant |

!!! unverified "UNVERIFIED — Torx or hex drive"
    Team hardware standard: Torx button-head M4x12 (McMaster-Carr 90991A123)
    and M3x12 (90991A115) only; main bearing 50x65x7 mm; threadlocker Loctite
    222. The first-article check contradicts 'M4/M3 only': 'Motor04 Shaft
    NEEDS m5 holes, but the cad has m4 holes. Same in the knee motor'
    (**UNVERIFIED**{ .dh-unverified } which the released CAD has).

    *Source: team design log, "Hardware Choice"; team CNC tolerance-check
    slides.* This site previously listed metric hex drivers. The design log
    names Torx drive but no driver size, and no fastener has been checked
    against a build.
    *Owner: hardware lead.*

## Optional

| Tool | Why you might want it |
| --- | --- |
| Soft-face mallet | Seating a tight part where a step permits it. Never on an actuator, a bearing or the camera |
| Powered screwdriver | Repetitive fasteners. Start every thread by hand, and do the final tightening with the torque tool |
| Third-hand clamp | Holding wire ends for soldering |
| Bench power supply | Bringing a single actuator up on the bench without the robot's battery |
| Thermal camera | Finding a hot actuator or converter during bring-up |
| Digital calipers | Incoming inspection of machined parts against the drawings — see [Incoming inspection](../fabrication/incoming-inspection.md). The team's reference fit check used a hand-held digital caliper reading to 0.01 mm. *Source: team CNC tolerance-check slides.* |

## Tools we cannot yet specify

!!! missing "MISSING — specifications for tools that depend on documents that do not exist"
    Each of these is a real, probably unavoidable tool whose specification
    depends on a document that does not exist. Listing them without a
    specification is deliberate — a builder should be able to see that the
    question is open, not discover it mid-build.

    - **Bearing / arbor press and arbors.** The machined parts list contains
      bearing retainers, output shafts and support shafts throughout the leg and
      arm, so press fits are very likely. Nothing states which fits are pressed,
      what force they take, or what arbor diameters are needed.
      *Owner: hardware lead, from the CAD.*
    - **Driver sizes.** Blocked on the fastener schedule. The team standard
      names Torx button-head M4x12 and M3x12 screws but not the driver size.
    - **Torque tool range.** Blocked on the torque values.
    - **Crimp tool and dies.** Blocked on the harness connector choice.
    - **Retaining-ring pliers**, if any retaining rings are used.
    - **Alignment or setting fixtures** for joint zeroing, if the zero position
      is set mechanically rather than in software — see
      [Joint zeroing](../bringup/joint-zeroing.md).

## Tools in the bill of materials

`tools.csv` does not exist yet **TODO**{ .dh-missing }. Once it lands, this
page's list and that file must agree: every tool
above becomes a row with a vendor link, a price and a `priced_as_of` date, and
the subtotal at the top of this page fills in by itself. The hoist in
particular must be a row — today it exists only as a sentence in the operations
manual and in no list at all.

## Figures this page needs

Neither figure exists yet **TODO**{ .dh-missing }.

| File | Section | What it must show |
| --- | --- | --- |
| `assets/assembly/tools-kitting-tray.png` | Before you start: kit the hardware out | A divided tray with fasteners counted into it by size, labelled — the kitting protocol above, made concrete |
| `assets/assembly/tools-limb-stand.png` | Lifting and support | The limb stand or jig used to hold a leg during assembly, once one exists |
