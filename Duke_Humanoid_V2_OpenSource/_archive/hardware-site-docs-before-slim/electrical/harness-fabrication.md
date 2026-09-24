# Harness fabrication

Building the cables. Each one needs a length, a gauge, a connector at each end
with a defined pinout, and a label. This page holds the structure those four
things go into, and is explicit about which of them are not published yet.

!!! danger "The harness is this robot's known weak point"
    On 2026-07-24 the reference robot drove into a collision because
    `right_shoulder_2` and `right_shoulder_3` — CAN IDs 21 and 22, both on
    `can21` — went silent on the bus for 0.3–0.4 s. That is far too short to see
    by eye and long enough to lose control of an arm. The deploy repository
    carries two tools written specifically to hunt it
    (`humanoid_wiggle_watch.py`, `humanoid_dropout_probe.py`), and the operations
    runbook's triage table sends recurring executor and follow faults straight to
    "wiring or torque" as the first suspect.

    Build these cables as if an intermittent one will cost you a limb, because
    on this machine it has.

## Raw material

What the release parts list actually contains for the harness:

| Item | Qty | Note |
| --- | --- | --- |
| XT30(2+2) connectors, 5-piece packs | 4 packs | Two power + two signal contacts in one shell |
| XT30 connector set, male and female | 30 pairs | Power only |
| Cord protector wire loom, 1/4 inch, 25 ft | 1 | Sleeving |
| Cord protector wire loom, 3/8 inch, 25 ft | 1 | Sleeving |
| USB A to USB C 3.1 Gen 2 cable | 6 | Finished cable |
| USB A to USB C cable, 6.6 ft (2-pack) | 2 packs | Finished cable |
| Short USB-C extension, 40 Gbit/s | 2 | Camera runs |
| 1 ft USB-C cable, right-angle plug | 1 | Camera runs |

The harness subtotal computed from the release data is
{{ bom_subtotal("cables-connectors.csv") }}; the full list is on
[Cables and connectors](../bom/cables-and-connectors.md). The three USB hubs are
counted with [Electronics](../bom/electronics.md), not here.

!!! missing "MISSING — SAFETY — the harness cannot be ordered from this release"
    - **Bulk wire.** Not one metre, in any gauge. Every conductor on this robot
      that is not a finished USB cable has no line item.
    - **Crimp terminals, ferrules, or the crimp tool** for anything.
    - **Heat-shrink**, other than what is bundled with one XT30 kit. The team's
      soldering checklists call for heat-shrink on every joint.
    - **Ethernet cable**, which the team's CAN-lead procedure uses (see
      [below](#the-teams-soldering-methods)).
    - **Motor-side connectors.** The RobStride manuals name the mates (see
      [Connector pinouts](#connector-pinouts)); the GH1.25 CAN connectors the
      RS03 and RS04 need are not in the list.
    - **Fuses, fuse holders, a disconnect switch, or an e-stop** — see
      [Power system](power-system.md).
    - **CAN termination resistors** — see [CAN bus](can-bus.md).

    A builder cannot order the harness from this release. Closing the list is
    the first job on this page.

    *Owner: electrical lead. Blocks [Sourcing](../bom/sourcing.md).*

## The harness schedule

One row per physical cable. This is the deliverable of this page: with it a
builder can cut, crimp, label and test every cable on a bench before any of it
goes near the robot. Without it, cables get made to fit during assembly, which is
how you end up with the intermittent above.

The endpoints below follow from the published bus topology. Everything
electrical is unpublished.

| Cable ID | From | To | Cond. | Gauge | Connector A | Connector B | Length | Sleeve |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **TODO**{ .dh-missing } | CAN adapter `can9` | Left arm trunk | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| **TODO**{ .dh-missing } | CAN adapter `can21` | Right arm trunk | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| **TODO**{ .dh-missing } | CAN adapter `can22` | Waist / shoulder-pitch trunk | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| **TODO**{ .dh-missing } | CAN adapter `can23` | Right leg trunk | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| **TODO**{ .dh-missing } | CAN adapter `can24` | Left leg trunk | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| **TODO**{ .dh-missing } | CAN adapter `can25` | Camera gimbal trunk | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| **TODO**{ .dh-missing } | Pack | Pack (series link, + to −) | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } (EC5 **UNVERIFIED**{ .dh-unverified }) | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| **TODO**{ .dh-missing } | Pack + | Surge protector | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| **TODO**{ .dh-missing } | Surge protector | Upper-body power distribution block (48V riser) | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| **TODO**{ .dh-missing } | 48V bus | Lower-body power distribution block | **TODO**{ .dh-missing } | 12 AWG | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| **TODO**{ .dh-missing } | Pack − | Upper- and lower-body ground distribution blocks | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| **TODO**{ .dh-missing } | Upper-body power distribution block | 10 A fuse, then 48V-to-12V buck converter | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| **TODO**{ .dh-missing } | 48V-to-12V buck converter | Onboard computer | **TODO**{ .dh-missing } | 16 AWG | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| **TODO**{ .dh-missing } | 12 V converter | Left gripper servo | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| **TODO**{ .dh-missing } | 12 V converter | Right gripper servo | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |

The power rows follow the [team power diagram](power-system.md#the-team-power-diagram);
the two gauges are the only ones it labels. *Source: team power wiring diagram
(V2).* The gripper-servo supply is not drawn, so its two rows have no drawn
source.

Each bus trunk then breaks out to its actuators — six drops on the arm and leg
buses, four on the camera bus, three on the waist bus — and each drop is its own
row once the daisy-chain order exists.

!!! missing "MISSING — the harness schedule, and one row per motor drop"
    Fill every `— TODO` above, and add one row per motor drop. A row is only
    complete when it carries a cable ID that is printed on a physical label, both
    endpoints, conductor count, gauge, connector part number at each end, the
    finished length **including the service loop**, and the sleeving size.

    *Owner: electrical lead, measured on a real build. Blocks
    [Routing](routing.md) and several
    [Assembly](../assembly/index.md) steps.*

## Connector pinouts

A pinout has to be written down once and then obeyed, because a connector
assembled to a different convention at the two ends of one cable is invisible
until it is powered.

### XT30(2+2), at the RS02

Two power contacts and two signal contacts in one shell. The RS02 manual gives
board side XT30PB(2+2)-M.G.B and cable side XT30(2+2)-F.G.B (Amass), numbered as
below. *Source: RobStride RS02 manual, driver interface.*

| Pin | Signal | Wire colour | Gauge |
| --- | --- | --- | --- |
| 1 | Power + | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| 2 | Power − | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| 3 | CAN_L | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| 4 | CAN_H | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |

This site earlier guessed "Signal 1 = CANH, Signal 2 = CANL". That guess has not
been checked against the vendor numbering above **UNVERIFIED**{ .dh-unverified };
use the pin numbers, not the guess.

### Actuator connectors, RS03 and RS04

The RS03 and RS04 do **not** use XT30(2+2). Power and CAN are on separate
connectors. *Source: RobStride RS03 and RS04 manuals, §2.2.2–2.2.3.*

| Connector | Board side | Cable side | Signals and lead colours |
| --- | --- | --- | --- |
| Power | XT30APW-M | XT30UW-F | RS04 leads: red VBAT+, black GND |
| CAN | GH1.25-2PWT | GH1.25-T | RS04 leads: blue CAN_H, brown CAN_L |

Team photos of an opened RS03 show two XT30 and two small 2-pin sockets on the
driver board, an in and an out for daisy-chaining. The RS00, RS05 and RS06
manuals are not in the team records, so their connectors are **TODO**{ .dh-missing }.

!!! unverified "UNVERIFIED — XT30(2+2) on every actuator, and the CAN lead colours"
    This site has said that motor power and the CAN pair share XT30(2+2)
    shells on every actuator. Per the manuals that is true at the RS02 only;
    the RS03 and RS04 use a separate XT30 plus a GH1.25 2-pin connector. The
    trunk harness between actuators may still use XT30(2+2); that is not
    recorded. Colours also disagree: the RS04 manual gives blue CAN_H and brown
    CAN_L, team photos show a blue/yellow twisted pair, and the team's
    Ethernet-cable procedure uses yellow = CAN High, blue = CAN Low. Confirm
    the connector on each trunk segment and one colour convention.

    *Owner: electrical lead.*

### XT30(2+2) ratings

From the Amass XT30(2+2)-F.G.B datasheet (LCSC C19268028; cited, not
redistributed): rated 15 A with 18 AWG wire; 30 A for 1 min at under 80 °C;
withstand DC 500 V; contact resistance 1.20 mΩ; 100 mating cycles; IP40;
−20 to 120 °C. Recommended wire, at 60 °C / 85 °C temperature rise: 16 AWG
20 A / 25 A, 18 AWG 15 A / 20 A, 20 AWG 10 A / 15 A. **Do not mate or unmate the
connector under power.** These are the connector's ratings, not the gauge the
robot uses.

The team power diagram labels 12 AWG on the pack-to-lower-body power run and 16 AWG on the 12 V run from the buck converter to the computer. No other run is labelled; the gauge of the 48V riser, the ground returns and the motor branches is still missing.

*Source: team power wiring diagram (V2).*

### Gripper servo connector

| Contact | Signal | Wire colour | Gauge |
| --- | --- | --- | --- |
| **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |

!!! missing "MISSING — connector pinouts, mating parts, crimp tooling and colour convention"
    - Fill the three tables above, with the **mating part number** and the
      **crimp tool and die** for each, not just the pin order.
    - Name the orientation feature: which way is pin 1 when you look into the
      shell, and how a builder confirms it before crimping.
    - State the **colour convention** and apply it everywhere. The team
      diagrams use red for positive and black for ground; the CAN pair colour
      is in conflict (see the box above). A comparable project states its
      convention in one line, and that single sentence removes an entire class
      of build error.
    - Note anywhere a connector is **physically reversible**. XT30 pairs can be
      assembled to mate with reversed polarity if a shell is loaded wrong, which
      is exactly why [Pre-power checks](pre-power-checks.md) tests polarity at
      every connector rather than trusting the build.

    *Owner: electrical lead.*

## Wire gauge

Gauge follows from current, length and the acceptable drop, and the current has
never been measured (**TODO**{ .dh-missing }) — see the measured-bus-current item marked MISSING on
[Power system](power-system.md#configured-current-limits). Until it is, no gauge
on this robot can be justified, only copied.

| Run | Continuous current | Peak current | Length | Gauge | Basis |
| --- | --- | --- | --- | --- | --- |
| Pack to lower-body distribution block | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | 12 AWG | Labelled on the team power diagram; basis not recorded |
| 48V riser, pack to upper-body block | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| Ground returns | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| Bus trunk, per limb | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| Motor drop, RS04 (knee) | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| Motor drop, RS03 | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| Motor drop, RS05 (camera, wrist yaw) | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| 12 V, buck converter to computer | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | 16 AWG | Labelled on the team power diagram; basis not recorded |
| 12 V, gripper servos | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |
| CAN pair | n/a | n/a | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |

!!! missing "MISSING — wire gauge, insulation rating and strand count for every run"
    Choose gauges from measured current and publish the basis, including the
    insulation temperature rating and the strand count. **Strand count matters
    more than gauge on this machine**: every conductor that crosses a joint
    flexes for the life of the robot, and solid or coarse-stranded wire work-
    hardens and breaks inside the insulation, which presents as exactly the
    intermittent dropout described at the top of this page.

    *Owner: electrical lead.*

## The team's soldering methods

The team solders its power and CAN joints; it does not crimp the XT30. These are
the team's own checklists, in order.
*Source: team design log, "CAN bus" (soldering checklists and CAN bus wiring).*

### Motor power wire, XT30

1. Confirm polarity before starting: which side is +?
2. Choose a wire gauge appropriate for the current.
3. Slide the heat-shrink on **before** soldering.
4. Hold the connector in a vise or helping hands.
5. Iron at about 480 °C.
6. Tin the wire fully, with no dry strands.
7. Tin the XT30 cup until the solder wets the gold plating.
8. Reheat the cup, insert the wire fully, and stop feeding solder.
9. Hold perfectly still until the solder solidifies.
10. Check the joint: smooth and shiny, not domed or grainy; no solder overflow
    blocking mating; the wire exits straight, with no side load.
11. Shrink the heat-shrink over the joint and the insulation gap.
12. Tug test: did anything move?
13. Verify continuity, then **recheck polarity again**.
14. The connector mates cleanly, and no conductor is exposed anywhere.

### CAN pair

1. Power off.
2. Identify CAN_H and CAN_L, and check the orientation.
3. Strip minimal insulation, and keep the twist to within 10–15 mm of the
   solder joint.
4. Slide the heat-shrink on **before** soldering.
5. Lightly pre-tin the wires and the terminal.
6. Align the wires inline, with no branch stubs.
7. Solder quickly, for a shiny, smooth joint.
8. Keep CAN_H and CAN_L at **equal length**.
9. Shrink the heat-shrink for strain relief.
10. Continuity-check CAN_H and CAN_L; verify no CAN_H–CAN_L short and no short
    to ground.
11. Measure about 60 Ω across the finished, terminated bus (see
    [CAN bus](can-bus.md#termination)).
12. Restore the twist through the joint area.

### CAN lead from Ethernet cable

The team's procedure for a CAN lead made from Ethernet cable. Materials:
Ethernet cable; two small heat-shrinks (3/32 in); one large heat-shrink (1/4 in)
that fits over the cable; one CAN High + CAN Low connector with yellow and blue
wires; wire strippers; a soldering setup.

1. Strip about 2.5 cm of jacket. There are 8 conductors in 4 twisted pairs.
2. Separate the pairs, and strip about 8 mm from each conductor.
3. Group the coloured conductors together and the white conductors together,
   and twist each group back together.
4. Put the small heat-shrinks on the connector's wires.
5. Solder the white bundle to CAN Low (blue) and the coloured bundle to CAN
   High (yellow).
6. Shrink the small sleeves, then slide the large sleeve over the cable onto
   them and shrink it.

!!! unverified "UNVERIFIED — where the Ethernet-cable CAN lead is used"
    The team log does not say which runs use this lead (adapter to first motor,
    motor to motor, or a bench fixture), nor whether its yellow/blue connector
    is the GH1.25 CAN connector of an RS03/RS04 or the signal half of an
    XT30(2+2). Confirm before building one for the robot.

    *Owner: electrical lead.*

## Building a cable

{{ step(1, "Cut to the schedule length, not to the robot") }}

Cut from the schedule, with the service loop already included in the number.
Fitting a cable by holding it against a half-built robot produces a harness that
only fits that one robot in that one pose.

{{ step(2, "Solder each contact, then tug-test it") }}

Solder the XT30 contacts at about 480 °C and the CAN pair, following
[the team's soldering methods](#the-teams-soldering-methods) above: heat-shrink
on first, fully tinned wire and cup, no overflow, then a tug test and a
continuity check on every joint. *Source: team design log, soldering
checklists.* The team solders the XT30; it does not crimp it.

!!! missing "MISSING — pull-out force for a finished joint, and specification for any crimped contact"
    The team's tug test is qualitative ("Did anything move?"); no pull-out
    force is recorded. Publish the force a finished joint must survive. For any
    contact on this robot that is crimped rather than soldered, publish the
    tool, die and strip length. Without a number, "firmly" is whatever that
    day's builder thought it meant.

    *Owner: electrical lead.*

{{ step(3, "Assemble the shells to the pinout") }}

Load both ends from the pinout tables above, then check continuity pin-to-pin
before sleeving — after sleeving it is a rework, not a check.

{{ step(4, "Sleeve, label both ends, and record") }}

Label both ends with the cable ID from the schedule. A label at one end only is
half a label: you find the mystery end inside a closed limb.

!!! missing "MISSING — cable labelling scheme"
    The **labelling scheme**: what a cable ID looks like, what printer or label
    stock survives being pulled through a limb, and where the label sits so it is
    readable after installation.

    *Owner: electrical lead.*

{{ step(5, "Test the finished cable on the bench") }}

Every cable is tested before it is installed. Reaching a fault inside an
assembled limb costs a disassembly.

| Test | Instrument | Pass criterion |
| --- | --- | --- |
| Pin-to-pin continuity, both directions | Multimeter, continuity mode | Every intended pair conducts; **no** unintended pair conducts |
| Insulation between power conductors | Multimeter | **TODO**{ .dh-missing } |
| Insulation, each conductor to sleeving/shield | Multimeter | **TODO**{ .dh-missing } |
| Flex test at each end | Hand | No change in continuity while the cable is flexed at the strain relief |

!!! missing "MISSING — pass criteria for the two bench insulation tests"
    The two insulation rows above have no pass criterion: neither the minimum
    resistance between power conductors, nor the minimum resistance from each
    conductor to its sleeving or shield, nor the meter range to read it on. As
    written, neither test can be failed.

    *Owner: electrical lead.*

The flex test is the one that catches a bad crimp. Hold a continuity meter on the
pair and work the cable at both strain reliefs; a crimp that is going to fail in
six months usually flickers today.

{{ checkpoint("Every cable in the schedule exists, is labelled at both ends, has passed pin-to-pin continuity with no unintended path, and has passed the flex test at both strain reliefs — all before any of it is installed in the robot.") }}

## Cables that must exist before assembly closes

!!! missing "MISSING — cables that must be threaded before each limb is closed"
    List, per subassembly, which cables must be **finished and threaded** before
    a limb is closed, and cross-reference the exact assembly step that closes it.
    On a machine with internal routing this is the difference between a two-hour
    job and a two-day one.

    *Owner: electrical lead + assembly lead. Blocks
    [Leg](../assembly/leg.md), [Arm](../assembly/arm.md),
    [Torso and waist](../assembly/torso-and-waist.md) and
    [Head and camera gimbal](../assembly/head-and-camera-gimbal.md).*
