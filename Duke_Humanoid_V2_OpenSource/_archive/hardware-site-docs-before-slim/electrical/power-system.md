# Power system

How energy gets from two lithium packs to 31 actuators, an onboard computer, two
depth cameras and two gripper servos. This page must let a builder draw the whole
power tree before cutting a single wire.

## The team power diagram

<figure markdown>
  ![Team power wiring diagram, Duke Humanoid V2](../assets/wiring/power-supply-v2.webp){ loading=lazy }
  <figcaption>Team power wiring diagram (V2): two 6S packs in series, surge protector, 48V bus to upper- and lower-body distribution blocks, TVS diodes, 10 A fuse and 48V-to-12V buck converter to the onboard computer.</figcaption>
</figure>

Open the diagram at [full size](../assets/wiring/power-supply-v2.png) to read the
labels. It is the team's own drawing of the V2 power tree, and everything below
that cites it is read off it.

Power is split between two distribution-block pairs (power + ground). The lower-body pair feeds both legs and the waist (13 actuators, computed); the upper-body pair feeds both arms, both shoulder_1 joints and the four gaze motors (18 actuators, computed). TVS diodes sit across power and ground at each pair; the number fitted at each location is **UNVERIFIED**{ .dh-unverified } (the BOM carries 10 × M1.5KE62CA).

*Source: team power wiring diagram (V2); actuator counts computed from `control/humanoid_config.py`.*

!!! note "The power split is not the CAN split"
    The waist shares bus `can22` with both `shoulder_1` joints (see
    [CAN bus](can-bus.md#topology)), but it is powered from the lower-body
    block, while the two `shoulder_1` joints are powered from the upper-body
    block. Do not assume that a CAN bus and a power branch fail together.

The team power diagram labels 12 AWG on the pack-to-lower-body power run and 16 AWG on the 12 V run from the buck converter to the computer. No other run is labelled; the gauge of the 48V riser, the ground returns and the motor branches is still missing.

*Source: team power wiring diagram (V2).*

The only fuse drawn is a 10 A fuse on the onboard-computer branch: upper-body power distribution block → 10 A fuse → 48V-to-12V buck converter → MINISFORUM X1-470 mini PC. No pack-path fuse, e-stop, main disconnect, pre-charge circuit or pack monitoring is drawn, and the surge protector's part number is not identified. Neither the 10 A fuse nor the surge protector is in the BOM.

*Source: team power wiring diagram (V2); release BOM.*

## What the parts list contains

Every row below is in the release parts list. Priced detail is on
[Electronics](../bom/electronics.md); the electronics subtotal computed from the
release data is {{ bom_subtotal("electronics.csv") }}.

| Item | Qty | Role |
| --- | --- | --- |
| Zeee 6S LiPo 10000 mAh 22.2 V (sold as a 2-pack) | 2 packs | Energy storage |
| DC 20–60 V to 12 V encased buck converter | 1 | 12 V rail |
| 48 V to 12 V buck converter | 2 | 12 V rail |
| TVS diode, 53 V stand-off / 85 V clamp (Microchip M1.5KE62CA) | 10 | Transient protection |
| XT30(2+2) connectors | 4 packs of 5 | Power + signal in one shell |
| XT30 connector set, 30 pairs | 1 set | Power |
| MINISFORUM X1-470 mini PC | 1 | Onboard computer |
| Feetech HL-3915-C001 12 V servo | 2 | One gripper each |
| Waveshare ST/SC bus servo driver board | 2 | One per gripper servo |
| SYD Dynamics TransducerM TM171 9-axis AHRS | 1 | IMU |
| Intel RealSense D436 | 2 | Depth cameras |
| CANable PRO V2.0 USB-CAN controller | 6 | One per CAN bus |
| USB hub | 3 | USB fan-out |

### Drawn or used by the team, but not in the parts list

| Item | Where it appears | Status |
| --- | --- | --- |
| Power distribution blocks | Four drawn in the team power diagram (upper and lower body, power and ground; the count is inferred from the diagram). The team design log links a double-row, 8-hole copper terminal bar (AliExpress item 3256806176225478): 114 mm between mounts, 126 mm overall, M5 × 8 plus M8 × 1 screws. | Not in the BOM. Whether this variant is fitted at every block is **UNVERIFIED**{ .dh-unverified } |
| EC5 battery connectors | The team design log names EC5 "to connect from the battery". The diagram draws blue connector pairs at both pack leads and at the series link, unlabelled. | Not in the BOM. That the drawn connectors are EC5 is **UNVERIFIED**{ .dh-unverified } |
| 10 A fuse | Computer branch only | Not in the BOM; part not identified |
| Surge protector | Pack positive lead | Not in the BOM; part not identified |
| Charger | The team design log links a charger listing (Amazon B09WKN863V) whose slug reads "ISDT ... DC600Wx2" | Not in the BOM. The exact model is **UNVERIFIED**{ .dh-unverified } |

*Source: team power wiring diagram (V2); team design log, "Power".*

## Pack configuration and bus voltage

Two Zeee 6S 10000 mAh LiPo packs are connected in series (one pack's + to the other's −) and feed a bus labelled 48V through a surge protector. Computed, not stated in the diagram: 2 × 22.2 V = 44.4 V nominal and 2 × 25.2 V = 50.4 V at full charge.

*Source: team power wiring diagram (V2).*

The diagram also shows both packs carried at the same time. Getting this wrong
destroys hardware: the same two packs in parallel would give 22.2 V (25.2 V
charged), which will not run a system built for the series bus and will be
misdiagnosed as a dozen other faults. Wire the series link as the diagram
shows, then measure it (check C3 on [Pre-power checks](pre-power-checks.md)).

The RobStride 02, 03 and 04 manuals give a rated voltage of 48 VDC and an operating range of 24–60 VDC. The RS00, RS05 and RS06 manuals are not in the team records, so their range is **UNVERIFIED**{ .dh-unverified }.

*Source: RobStride RS02, RS03 and RS04 product manuals (RobStride; cited, not redistributed).*

The rest of the release agrees with the series topology. This is supporting
evidence, not the specification; the diagram is the specification:

1. Two identical 6S packs are bought together as one line item.
2. Two of the three converters in the BOM are nameplated **48 V to 12 V**, which
   fits a 44.4 V nominal bus and not a 22.2 V one.
3. The third converter accepts **20–60 V**, which brackets 44.4 V. Its lower
   bound also brackets 22.2 V, so on its own it discriminates nothing.
4. The TVS diode has a **53 V stand-off** voltage. A stand-off must sit above the
   highest normal bus voltage or the diode conducts continuously and cooks. Two
   6S packs at full charge are 50.4 V, just under 53 V.
5. Computed from the vendor ranges above: a single 6S pack at 22.2 V nominal is
   below the 24 V minimum; two in series, 44.4 V nominal and 50.4 V full, sit
   inside the 24–60 VDC range.

!!! missing "Do not connect a pack until the open SAFETY items on this page are closed"
    The topology is now written down by the team. What is still missing is
    everything that makes connecting a pack safe: the series-link hardware,
    balance-lead handling, pack retention, charging, a pack-path fuse, a
    surge-protector part, and an e-stop, disconnect and pre-charge path. Each
    is itemised in its own box below and on
    [Protection, disconnect and e-stop](#protection-disconnect-and-e-stop).

!!! unverified "UNVERIFIED — which packs the finished robot carries, and the battery purchase link"
    A March 2025 single-leg-phase photo shows two packs of different brands, one labelled 5200 mAh. **UNVERIFIED**{ .dh-unverified } which packs the finished robot carries; the power diagram and the BOM both name the Zeee 6S 10000 mAh.

    The purchase links also differ: the team design log links the battery at
    Amazon B0CS5RD74Y, the release BOM at Amazon B0BHQX8XQX. They may be the
    same product; that is not confirmed.

    *Owner: hardware lead.*

!!! missing "MISSING — SAFETY — series-link connector part number and gauge"
    The diagram draws the link between the two packs (one pack's + to the
    other's −) as a blue connector pair, but names neither the connector part
    nor the wire gauge. The design log's EC5 note suggests EC5; that is an
    inference. Publish the part number, the gauge and the length of the series
    link.

    *Owner: hardware lead.*

!!! missing "MISSING — SAFETY — balance-lead handling and pack monitoring"
    No balance lead, cell monitor or low-voltage alarm is drawn. Publish how
    the balance leads are protected on the robot, how the operator sees the
    pack state, and the voltage at which the robot must be shut down. The
    motors report bus voltage (see
    [Reading the bus](#reading-the-bus-on-the-assembled-robot)), but nothing in
    the released stack acts on it.

    *Owner: electrical lead + safety officer.*

!!! missing "MISSING — SAFETY — pack retention in the rear bay"
    The team CAD animation of the torso rear bay shows two packs standing
    upright side by side, and no retention part is drawn (see
    [Torso and waist](../assembly/torso-and-waist.md)). Publish what holds the
    packs in place, and how their leads are protected where they leave the
    bay.

    *Owner: hardware lead.*

!!! unverified "UNVERIFIED — operating voltage range of RS00, RS05 and RS06"
    The 24–60 VDC range above comes from the RS02, RS03 and RS04 manuals. The
    RS00, RS05 and RS06 manuals are not in the team records. Confirm each
    against its RobStride datasheet before energising a bus that carries it.

    *Owner: hardware lead.*

## Actuator electrical data

These constants are what the control stack actually writes to and reasons about.
They are published in
[`control/hardware_bindings/motor/py_motor.py`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/hardware_bindings/motor/py_motor.py);
the per-robot counts come from the motor table in
[`control/humanoid_config.py`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/humanoid_config.py).

| Model | Qty | Max torque (N·m) | Default current limit (A) | Torque constant (N·m/A<sub>rms</sub>) | Winding resistance (Ω ±10 %) | Back-EMF (V<sub>rms</sub>/(rad/s)) |
| --- | --- | --- | --- | --- | --- | --- |
| RS00 | 2 | 14 | 16.0 | 1.48 | 1.5 | 0.91 |
| RS02 | 6 | 17.0 | 23.0 | 1.22 | 0.55 | 0.92 |
| RS03 | 11 | 60.0 | 43.0 | 2.36 | 0.39 | 0.16 |
| RS04 | 2 | 120.0 | 60.0 | 2.10 | 0.16 | 0.16 |
| RS05 | 6 | 5.5 | 11.0 | 0.94 | 2.72 | 0.071 |
| RS06 | 4 | 36 | 57.0 | 1.1 | 0.23 | 0.073 |

!!! success "This table cross-checks against the purchasing list"
    The per-model counts derived from the software's motor table — 2 / 6 / 11 /
    2 / 6 / 4 — match the RobStride quantities in the purchasing BOM exactly,
    and sum to 31. Two independently maintained documents agreeing to the unit
    is the strongest evidence in this release that the actuator count is right.

The current-limit register `0x7018` has a range that depends on the model:
RS02 0–23 A, RS03 0–43 A, RS04 0–90 A. The defaults above for those three models
(23.0, 43.0 and 60.0 A) sit inside those ranges.
*Source: RobStride RS02, RS03 and RS04 manuals, `0x7018` rows; `py_motor.py`.*

The back-EMF figures for RS02, RS03 and RS04 are faithful unit conversions of
the vendor manual values, and the code comments carry the originals: RS02
0.096 V<sub>rms</sub>/rpm → 0.92, RS03 17 V<sub>rms</sub>/krpm → 0.16, RS04
16.9 V<sub>rms</sub>/krpm → 0.16. The roughly tenfold spread between models
therefore comes from the vendor manuals as stated, not from a transcription
error.
*Source: RobStride RS02, RS03 and RS04 manuals; `py_motor.py`
`MOTOR_BACK_EMF_CONSTANTS`.*

!!! unverified "UNVERIFIED — back-EMF basis (rotor or output speed), and the RS00, RS05 and RS06 figures"
    Torque constant divided by back-EMF constant comes out at about 1.3–1.6
    for RS00 and RS02 but about 13–15 for RS03, RS04, RS05 and RS06, yet the
    two constants describe the same motor property and should scale together
    across models. The RS02, RS03 and RS04 figures match their manuals, and no
    manual says whether its figure refers to rotor speed or output speed. The
    speed self-check below divides by this column, so its result is
    unconfirmed for at least one group of models. Confirm the basis with
    RobStride, and check RS00, RS05 and RS06, whose manuals are not in the team
    records.

    *Owner: controls lead.*

### Why the bus voltage decides what the robot can do

The controller's own self-check computes the speed a joint can still reach while
holding its torque limit as

```text
max_vel_at_max_torque = (v_bus - torque_limit / kt * r) / ke
```

with `kt`, `r` and `ke` the torque constant, resistance and back-EMF constant
above. Bus voltage sits in the numerator: a bus at half the intended voltage does
not give you a slightly slower robot, it gives you a robot whose joints stall
under load partway through a motion. This is why the pack must be wired in
series as drawn, and measured before anything moves.

### Configured current limits

[`control/humanoid_set_current_limit.py`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/humanoid_set_current_limit.py)
writes `min(default × scale, 40 A)` to every motor, with `scale` defaulting to
`0.6`. At that default the written limits are:

| Model | Written limit at `--scale 0.6` (A) |
| --- | --- |
| RS00 | 9.6 |
| RS02 | 13.8 |
| RS03 | 25.8 |
| RS04 | 36.0 |
| RS05 | 6.6 |
| RS06 | 34.2 |

!!! danger "These are per-motor phase limits. Do not add them up to size a bus."
    Summing this column gives a number in the hundreds of amps. That number is
    meaningless as a supply requirement: it is motor-side phase current, not
    bus current, and 31 actuators never reach their ceilings simultaneously. It
    is recorded here only so a builder can see what the drives are configured to
    allow. **The actual bus current — continuous and peak — has never been
    published or measured** **TODO**{ .dh-missing }, and it is the number every
    wire gauge, connector and fuse on this robot depends on.

!!! missing "MISSING — SAFETY — measured bus current and peak inrush"
    - **Measured bus current**: quiescent, standing, and walking, with the
      instrument and the shunt point named. Until this exists, no gauge on
      [Harness fabrication](harness-fabrication.md) can be justified.
    - **Peak inrush** at pack connection, which sets the pre-charge requirement.

    *Owner: electrical lead + controls lead.*

!!! unverified "UNVERIFIED — the current-limit scale the reference robot ran"
    The written current limits above are the script's default. Whether that
    default is the configuration the reference robot ran is not recorded; the
    script carries a bare comment `04 --> scale=0.55` suggesting at least one
    model was run at a different scale. Publish the scale the reference robot
    used.

    *Owner: controls lead.*

## The 12 V rail

**UNVERIFIED**{ .dh-unverified } — converter conflict: the team power diagram draws one 48V-to-12V buck converter (computer branch only) and no 5 V rail; the BOM lists 2 × generic 48 V-to-12 V buck converters plus 1 × DC 20–60 V to 12 V encased buck converter; the design log proposed Delta isolated bricks (2 × V48SC12007NRFA, 12 V 7 A, and 1 × V36SE05010NRFA, 5 V 10 A), which appear only in [Design](../design/electronics-and-sensing.md) as considered.

*Source: team power wiring diagram (V2); release BOM; team design log, "Power".*

Known 12 V loads:

- **Onboard computer** — the MINISFORUM X1-470, fed from the upper-body block
  through the 10 A fuse and the 48V-to-12V buck converter, on a 16 AWG run
  (team power diagram).
- **Gripper servos** — the Feetech HL-3915-C001 is a 12 V part, two of them.
  Their supply is not drawn in the team power diagram.

Everything else on the robot is a USB device (cameras, IMU, gripper driver
boards, CAN adapters) and is therefore powered by the computer's USB ports
through the three hubs, unless a separate injection scheme exists
**UNVERIFIED**{ .dh-unverified } — this is inferred from the device list and the
team data wiring diagram, which shows no hub power (see
[Electrical](index.md#the-two-team-diagrams)).

!!! missing "MISSING — power tree: converter allocation, gripper-servo supply, USB power budget"
    - Which **physical converter** feeds the computer, and what the other two
      12 V converters in the BOM feed, if they are fitted at all.
    - The **gripper-servo 12 V supply**: its source, fuse and wiring, none of
      which is drawn.
    - **USB power budget**: two RealSense D436 at USB 3 speeds, six CAN adapters,
      an IMU and two servo driver boards across three hubs. Whether the hubs are
      powered or bus-powered is not stated, and an under-powered hub shows up as
      a camera dropping to USB2 — a failure the operations guide already
      documents chasing.

    *Owner: electrical lead.*

## Protection, disconnect and e-stop

| Function | In the parts list? | In the team power diagram? |
| --- | --- | --- |
| Transient suppression | Yes — 10 × TVS diode, 53 V stand-off / 85 V clamp | Yes — across power and ground at each distribution-block pair; count per location **UNVERIFIED**{ .dh-unverified } |
| Surge protector | **No** | Yes — in the pack positive lead; part number **TODO**{ .dh-missing } |
| Fuse, computer branch | **No** | Yes — 10 A |
| Fuse, pack path | **No** | **No** — **TODO**{ .dh-missing } |
| Main disconnect switch | **No** | **No** — **TODO**{ .dh-missing } |
| Pre-charge circuit | **No** | **No** — **TODO**{ .dh-missing } |
| E-stop | **No** | **No** — **TODO**{ .dh-missing } |
| Pack monitoring / low-voltage alarm | **No** | **No** — **TODO**{ .dh-missing } |
| Charger | **No** | Not drawn; listing linked in the design log, model **UNVERIFIED**{ .dh-unverified } |

*Source: team power wiring diagram (V2); release BOM; team design log, "Power".*

The control stack's own runbooks assume an e-stop exists: the hardware walk test
lists "the physical E-stop" as the last safety layer, and the joint-monkey
choreography refuses to start without "E-stop within reach". The team power
diagram shows no e-stop, disconnect or pre-charge. The two sources conflict, and
[Torso and waist](../assembly/torso-and-waist.md) records that no document in the
project describes any hardware stop at all.

!!! missing "MISSING — SAFETY — e-stop, main disconnect and pre-charge (none drawn)"
    The deploy runbooks (`humanoid_nav_step_test.py`,
    `humanoid_joint_monkey_hw.py`) assume a physical e-stop; the team power
    diagram draws no e-stop, no main disconnect and no pre-charge circuit.
    Publish:

    - **E-stop**: part number, contact rating, mounting location, whether it is
      wired in the pack path or as a logic input, and exactly what it
      de-energises. An e-stop that cuts logic but not the motor bus, or vice
      versa, is worth knowing about before you need it.
    - **Main disconnect** and **pre-charge**: connecting a pack directly to a
      bank of drive capacitors arcs the connector and pits the contacts.

    *Owner: electrical lead + safety officer. Blocks
    [Pre-power checks](pre-power-checks.md) and
    [Safety](../before-you-start/safety.md).*

!!! missing "MISSING — SAFETY — pack-path fuse (none drawn)"
    The only fuse drawn is the 10 A fuse on the computer branch. Nothing
    protects the pack leads, the 48V riser or the distribution blocks. A
    10 000 mAh LiPo will deliver hundreds of amps into a short. Publish the
    value, type, interrupt rating and location of a pack-path fuse, or state
    in writing that the robot runs without one and why.

    *Owner: electrical lead + safety officer.*

!!! missing "MISSING — SAFETY — surge protector part number"
    The diagram draws a surge protector in the pack positive lead. Its part
    number, rating and function are not identified anywhere, and it is not in
    the BOM.

    *Owner: electrical lead.*

!!! missing "MISSING — SAFETY — charging procedure and charge rate"
    The charger listing linked in the design log (Amazon B09WKN863V, slug
    "ISDT ... DC600Wx2") is the only charging information; its exact model is
    **UNVERIFIED**{ .dh-unverified } and it is not in the BOM. Publish the
    charger, the charge rate, the balance-charging procedure, where the packs
    are charged, and whether they are charged in the robot.

    *Owner: electrical lead + safety officer.*

!!! unverified "UNVERIFIED — TVS diode count at each distribution-block pair"
    The diagram draws TVS diodes at the upper-body and the lower-body pair; the
    BOM carries ten M1.5KE62CA. How many are fitted at each location, and
    whether any sit elsewhere, is not recorded.

    *Owner: electrical lead.*

## Reading the bus on the assembled robot

Every actuator reports its own bus voltage and temperature, and there is a
read-only tool that collects them without enabling anything:

```bash
cd <deploy-repo>/control
python humanoid_motor_temps.py
```

It prints one row per motor in URDF order — joint name, CAN ID, temperature,
`v_bus` — and commands nothing. Run it with `humanoid_real_env.py` stopped, so
there is a single owner on each CAN bus. This is the cheapest confirmation that
the bus voltage at the far end of the harness is what you think it is, and it is
a step in [First power-on](../bringup/first-power-on.md).

{{ checkpoint("Before any pack is connected: the two packs are wired in series as the team power diagram shows, the bus voltage is measured and written down, every converter on the robot is rated for it, and every MISSING — SAFETY item on this page is closed.") }}
