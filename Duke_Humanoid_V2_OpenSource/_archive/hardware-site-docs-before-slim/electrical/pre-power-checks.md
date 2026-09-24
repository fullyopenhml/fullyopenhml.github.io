# Pre-power checks

The gate between a wired robot and a powered one. Every check on this page must
pass, in order, before a battery is connected for the first time.

!!! danger "Battery disconnected until this page passes"
    Perform all of these with no pack in the machine. Connecting a battery to
    find a wiring fault is how a fault becomes a fire.

Work through the groups in order: A before B before C. Each group assumes the
previous one passed. A check without a number in its *Expected* column cannot be
failed, which makes it useless — where this page still has `— TODO` there, the
check is not yet a check, and the missing number is named in the block that
follows each table.

## A. Mechanical and site

| # | Check | Instrument | Expected |
| --- | --- | --- | --- |
| A1 | Robot suspended from a rated hoist, taking its full weight | Visual, hoist rating plate | Hoist rated well above 36 kg, safety factor **TODO**{ .dh-missing } (see [Safety](../before-you-start/safety.md#2-suspend-the-robot-for-every-early-test)); robot's full mass on the hoist |
| A2 | **Legs hang straight** | Visual | No leg bent, no torso tilt |
| A3 | Floor under and around the robot is clear | Visual | Nothing within the robot's reach or fall path |
| A4 | Fastener check from final integration complete and signed | Build record | Every fastener checked |
| A5 | No cable trapped, pinched, or under tension at any joint pose | Hand, per [Routing](routing.md) | Passes both routing checks **UNVERIFIED**{ .dh-unverified } — the second one reads live motor telemetry, see [Routing](routing.md#verifying-a-routing-job) |
| A6 | Two people present; one holds the e-stop and is not the person connecting the battery | — | Confirmed aloud |

!!! note "A2 is not cosmetic"
    Hanging the robot with bent legs tilts the torso, and a tilted torso corrupts
    the body-frame geometry the whole perception and planning chain is built on.
    The operations runbook lists it as operational rule #0 — "legs hang
    STRAIGHT when hanging the robot" — after three sessions were lost to it. Get
    it right from the first hang and it never becomes a habit you have to break.

## B. Harness continuity and isolation

Done with a multimeter, no pack, nothing energised.

| # | Check | Instrument | Expected |
| --- | --- | --- | --- |
| B1 | Every power conductor matches the harness schedule end to end | Multimeter, continuity | Every scheduled pair conducts |
| B2 | No unintended conductor pair conducts | Multimeter, continuity | Open on every unscheduled pair |
| B3 | Motor bus positive to motor bus negative | Multimeter, resistance | Reading rises as drive capacitance charges and settles high. **A steady low reading is a short — stop.** Settled value: **TODO**{ .dh-missing } |
| B4 | Each bus rail to chassis | Multimeter, resistance | **TODO**{ .dh-missing } |
| B5 | 12 V rail positive to 12 V rail negative | Multimeter, resistance | **TODO**{ .dh-missing } |
| B6 | Each conductor to its sleeving / shield | Multimeter, resistance | **TODO**{ .dh-missing } |

!!! missing "MISSING — SAFETY — resistance thresholds for isolation checks B3–B6"
    B3–B6 need real numbers, taken from a known-good robot with the same
    converters and drives installed, because "high" depends on what is connected.
    Publish the settled resistance a healthy machine shows, and the threshold
    below which a builder must stop.

    *Owner: electrical lead.*

## C. Polarity

XT30 shells can be assembled so that a cable mates with reversed polarity. The
connector will not tell you; it mates happily.

| # | Check | Instrument | Expected |
| --- | --- | --- | --- |
| C1 | Polarity at every power connector, against the pinout | Multimeter, DC volts, from a bench supply on the source side | Positive at the pin the pinout names |
| C2 | Pack connector polarity, both packs | Multimeter | Matches the robot-side connector |
| C3 | Series pack link wired as the team power diagram shows | Visual + multimeter continuity, packs disconnected | The link joins one pack's + to the other pack's −; the free − goes to the ground blocks and the free + to the surge protector |
| C4 | CAN pair orientation at every drop (CAN_H to CAN_H) | Multimeter, continuity against the pinout | Consistent at every connector on the bus |
| C5 | Polarity rechecked at every soldered XT30, a second time | Multimeter | Positive at the pin the pinout names, again |
| C6 | Tug test at every soldered XT30 joint | Hand | Nothing moves |

C3 checks against the series topology in the
[team power diagram](power-system.md#pack-configuration-and-bus-voltage): two
6S packs in series, 44.4 V nominal and 50.4 V full (computed). C5 and C6 come
from the team's XT30 soldering checklist ("Polarity rechecked. Again." and
"Tug test. Did anything move?"). *Source: team power wiring diagram (V2); team
design log, motor power wire soldering checklist.* The tug test is qualitative;
the pull-out force is still missing (see
[Harness fabrication](harness-fabrication.md#step-2)).

## D. Converters, on the bench

Every converter is verified **before** it is ever fed from a pack, on a bench
supply with its current limit set low. A converter wired backwards or a wrong
part fitted is cheap to find this way and expensive to find any other way.

Which of the three converters in the BOM are fitted is
**UNVERIFIED**{ .dh-unverified }: the team power diagram draws one 48V-to-12V
buck converter, on the computer branch (see
[Power system](power-system.md#the-12-v-rail)). Test every converter you fit.

| # | Check | Instrument | Expected |
| --- | --- | --- | --- |
| D1 | 20–60 V → 12 V converter output, no load | Bench supply + multimeter | 12 V nominal, tolerance **TODO**{ .dh-missing } |
| D2 | 48 V → 12 V converter #1 output, no load | Bench supply + multimeter | 12 V nominal, tolerance **TODO**{ .dh-missing } |
| D3 | 48 V → 12 V converter #2 output, no load | Bench supply + multimeter | 12 V nominal, tolerance **TODO**{ .dh-missing } |
| D4 | Each converter at its expected load | Bench supply + electronic load | **TODO**{ .dh-missing } |
| D5 | Bench supply current draw at each step | Bench supply readout | **TODO**{ .dh-missing } — a draw above this means stop |

!!! missing "MISSING — bench supply settings and pass tolerances for converter checks D1–D5"
    - The **bench supply voltage and current limit** to use for each converter.
    - Output tolerance that counts as a pass.
    - The expected load per converter, which depends on the unpublished power
      tree.

    *Owner: electrical lead.*

## E. CAN buses

| # | Check | Instrument | Expected |
| --- | --- | --- | --- |
| E1 | Termination resistance across CAN_H–CAN_L, each bus, unpowered | Multimeter | About 60 Ω (two 120 Ω terminators in parallel) |
| E1a | CAN_H and CAN_L continuity, adapter end to last motor, each bus | Multimeter, continuity | Both conduct |
| E1b | No CAN_H–CAN_L short, and no short from either line to ground | Multimeter, resistance | No short on any bus |
| E2 | Each adapter is labelled and matches its udev rule | Visual + `/etc/udev/rules.d/99-candlelight.rules` | Label agrees with rule |
| E3 | Each adapter's USB connection is mechanically secured | Hand | Does not move under a firm pull |
| E4 | Every motor drop lands on the bus the [actuator map](can-bus.md#the-actuator-map) gives | Continuity, against the schedule | Exact match |

E1's expected reading and checks E1a–E1b come from the team's CAN soldering
checklist: continuity-check H and L, verify no short H–L or to ground, and
"Measure ~60 Ω across bus (terminated)". *Source: team design log, CAN bus
soldering checklist.* Where the two terminators sit on each bus is still
missing; it is tracked on [CAN bus](can-bus.md#termination). A reading near
120 Ω means one terminator is missing; a reading near 40 Ω means a third one
is fitted (both computed from 120 Ω terminators).

## F. Packs

Measured on the bench, before either pack goes into the machine.

| # | Check | Instrument | Expected |
| --- | --- | --- | --- |
| F1 | Pack terminal voltage, each pack | Multimeter | 6S: 22.2 V nominal, 25.2 V at full charge; lowest voltage that still passes **TODO**{ .dh-missing } |
| F2 | Per-cell voltage, each pack | Cell checker / balance lead | **TODO**{ .dh-missing } — maximum acceptable cell spread |
| F3 | Physical condition | Visual | No swelling, no damaged wrap, no damaged lead |
| F4 | Both packs at a comparable state of charge before they are joined | Multimeter | **TODO**{ .dh-missing } — maximum acceptable difference between packs |

!!! danger "F4 matters: the packs are in series"
    The team power diagram joins the two packs in series. Joining two packs at
    different states of charge is a bad idea in any topology. Do not connect
    the two packs to each other until F1–F4 are signed off and the open SAFETY
    items on [Power system](power-system.md#pack-configuration-and-bus-voltage)
    are closed.

!!! missing "MISSING — SAFETY — pack acceptance thresholds and the charging procedure"
    F2 and F4 need thresholds, plus the charger, the charge rate, and where
    charging happens. F1 states the nominal and fully charged voltages but no
    voltage below which a pack fails, so as written it cannot be failed. The
    only charging information is a charger listing linked in the team design
    log, whose exact model is **UNVERIFIED**{ .dh-unverified } (see
    [Power system](power-system.md#protection-disconnect-and-e-stop)).

    *Owner: electrical lead + safety officer.*

## G. Safety systems

| # | Check | Instrument | Expected |
| --- | --- | --- | --- |
| G1 | E-stop mounted, reachable by the second person from outside the robot's reach | Visual | Reachable without stepping under the robot |
| G2 | E-stop contacts open when pressed, close when released and reset | Multimeter, continuity | Correct in both states |
| G3 | E-stop interrupts what it is specified to interrupt | Multimeter | **TODO**{ .dh-missing } — the specification does not exist |
| G4 | Everyone present knows where the e-stop is and who is holding it | — | Confirmed aloud |

!!! missing "MISSING — SAFETY — what the e-stop de-energises (check G3)"
    G3 is the important one and it is empty. Until someone writes down what the
    e-stop de-energises — motor bus, logic, both — nobody can check that it does.
    A machine whose e-stop function is undefined is not ready for first power-on.
    Note also that the joints are quasi-direct-drive: **cutting power drops the
    machine**, so the e-stop is a last resort on a suspended robot, not a routine
    stop. See [Safety](../before-you-start/safety.md).

    *Owner: safety officer. Blocks
    [First power-on](../bringup/first-power-on.md).*

## Sign-off

| Group | Signed | Date |
| --- | --- | --- |
| A. Mechanical and site | | |
| B. Continuity and isolation | | |
| C. Polarity | | |
| D. Converters | | |
| E. CAN buses | | |
| F. Packs | | |
| G. Safety systems | | |

{{ checkpoint("Every check above passes, the robot is suspended from a rated hoist with its legs hanging straight, the area under it is clear, and the person holding the e-stop is not the person connecting the battery.") }}
