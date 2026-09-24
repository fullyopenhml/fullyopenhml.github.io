# Electrical

Power, buses, harness and the checks that must pass before a battery is ever
connected. Read this section end to end before building any cable — a harness
is much easier to build right than to rework inside an assembled limb.

<div class="grid cards" markdown>

- **[Power system](power-system.md)** — packs, rails, protection, e-stop.
- **[CAN bus](can-bus.md)** — topology, IDs, termination.
- **[Harness fabrication](harness-fabrication.md)** — building the cables.
- **[Routing](routing.md)** — getting them through a machine that moves.
- **[Pre-power checks](pre-power-checks.md)** — the gate before first power-on.

</div>

!!! danger "Battery stays disconnected"
    Nothing in this section is done with a battery connected. The gate for
    connecting one is [Pre-power checks](pre-power-checks.md), and the first
    connection happens under [First power-on](../bringup/first-power-on.md) with
    the robot suspended.

## What the electrical system has to carry

One robot, from the release parts list and the control stack's own motor table:

| Domain | Count | Interface | Where the number comes from |
| --- | --- | --- | --- |
| Actuators | 31 | CAN, 1 Mbit/s, 6 buses | `control/humanoid_config.py` |
| Gripper servos | 2 | USB serial (CH340 driver board) | `docs/SETUP.md` §4 |
| Depth cameras | 2 | USB 3 (5 Gbit/s required) | `docs/OPERATIONS.md` T1 |
| IMU | 1 | USB serial | `hardware_bindings/README.md` |
| Onboard computer | 1 | — | release BOM |
| USB hubs | 3 | USB | release BOM |

All references above are to the [deploy
repository](https://github.com/generalroboticslab/duke_humanoid_v2_deploy),
which is the authoritative source for anything the software has to agree with.
Where this section states a number, it cites the file it came from. Where it
does not, the number is not published yet and the page says so.

## The two team diagrams

The team drew the V2 electrical system on two sheets: one for power, one for
data. They are the closest thing this release has to a system wiring diagram.
Open each at full size to read the labels.

<figure markdown>
  ![Team power wiring diagram, Duke Humanoid V2](../assets/wiring/power-supply-v2.webp){ loading=lazy }
  <figcaption>Team power wiring diagram (V2): two 6S packs in series, surge protector, 48V bus to upper- and lower-body distribution blocks, TVS diodes, 10 A fuse and 48V-to-12V buck converter to the onboard computer.</figcaption>
</figure>

[Power diagram at full size](../assets/wiring/power-supply-v2.png)

**The power tree, in one paragraph.** Two Zeee 6S 10000 mAh packs in series
(44.4 V nominal, 50.4 V full; computed) feed a bus labelled 48V through a surge
protector. The bus goes to two distribution-block pairs (power + ground): the
lower-body pair feeds both legs and the waist, the upper-body pair feeds both
arms, both `shoulder_1` joints and the four gaze motors. TVS diodes sit across
power and ground at each pair. The onboard computer is fed from the upper-body
block through a 10 A fuse and one 48V-to-12V buck converter. No pack-path fuse,
e-stop, main disconnect or pre-charge circuit is drawn. Detail, conflicts and
the open safety items are on [Power system](power-system.md).
*Source: team power wiring diagram (V2).*

<figure markdown>
  ![Team data wiring diagram, Duke Humanoid V2](../assets/wiring/data-wiring-v2.webp){ loading=lazy }
  <figcaption>Team data wiring diagram (V2): onboard computer, three USB hubs, six CANable PRO V2.0 adapters (can9, can21-can25), two D436 cameras, IMU and two gripper servo boards.</figcaption>
</figure>

[Data diagram at full size](../assets/wiring/data-wiring-v2.png)

USB Hub #1 carries the two RealSense D436 cameras and the IMU; USB Hub #2 the CANable PRO V2.0 adapters; USB Hub #3 the left and right gripper servo driver boards. Hub power and the USB power budget are not shown. Whether the first D436 and the can9 and can25 adapters plug into their hub or directly into the computer is **UNVERIFIED**{ .dh-unverified }.

*Source: team data wiring diagram (V2).*

The joint-by-joint CAN assignment read off the data diagram is on
[CAN bus](can-bus.md#topology).

Options the team considered and did not use for the electronics (a
microcontroller CAN and IMU path, isolated DC/DC bricks, a relay, foot force
sensing) are described in
[Design: electronics and sensing](../design/electronics-and-sensing.md). None
of them is part of the as-built robot.

## How solid each page is

Be honest with yourself about this before you start buying wire.

| Page | State |
| --- | --- |
| [CAN bus](can-bus.md) | **Mostly solved.** The complete 31-actuator bus and ID map is published and agrees with the team data wiring diagram and the purchasing BOM; the order of the four camera joint indices is **UNVERIFIED**{ .dh-unverified }. Terminator placement and physical cable construction are not published: **TODO**{ .dh-missing } |
| [Power system](power-system.md) | **Partly solved.** The team power diagram gives the pack topology (series) and the distribution tree; the pack-path fuse, the e-stop, disconnect and pre-charge, and which converters are fitted are not: **TODO**{ .dh-missing } |
| [Harness fabrication](harness-fabrication.md) | **Partly solved.** The team's soldering checklists and two labelled gauges are published; the harness schedule, most gauges and all lengths are not: **TODO**{ .dh-missing } |
| [Routing](routing.md) | **Structure only.** Needs photographs of a real build: **TODO**{ .dh-missing } |
| [Pre-power checks](pre-power-checks.md) | **Structure only.** The checklist shape is here; most pass criteria are missing: **TODO**{ .dh-missing } |

## Reading order

1. [Power system](power-system.md) — learn the power tree before anything else.
   Every gauge, connector and fuse downstream follows from it.
2. [CAN bus](can-bus.md) — the bus split determines which motors share a cable,
   which determines the harness.
3. [Harness fabrication](harness-fabrication.md) — build and test each cable on
   the bench.
4. [Routing](routing.md) — install them, in step with
   [Assembly](../assembly/index.md). Several cables must be threaded before a
   limb is closed.
5. [Pre-power checks](pre-power-checks.md) — the gate.

!!! missing "MISSING — connector-level detail missing from the team diagrams"
    The two [team diagrams](#the-two-team-diagrams) show every load, the power
    tree and every bus. They do not show connectors, the gauge of most runs,
    the gripper-servo 12 V supply or hub power. A builder still needs those on
    one sheet, with a connector part number at every junction.

    *Owner: electrical lead.*
