# Motor ID and config

Each of the 31 actuators needs a unique CAN ID on its bus and a configuration
that matches its joint. This is done once, and it must be done before any joint
is commanded.

## Prerequisites

- [First power-on](first-power-on.md) complete: all 31 actuators answer, none
  has been enabled.
- The robot suspended, legs straight, e-stop held by a second person.
- `humanoid_real_env.py` stopped. Every tool on this page owns the CAN buses.

## What has to be true of every actuator

| Property | Set by | Verified by |
| --- | --- | --- |
| Unique CAN ID, on the right bus | Vendor tool — see below | `humanoid_motor_temps.py`, the actuator map |
| Correct actuator model at the joint | Assembly | The model column of the actuator map |
| Firmware version | Vendor tool (device information) | **TODO**{ .dh-missing } — no robot baseline is recorded |
| Current limit | `humanoid_set_current_limit.py` | `self_check`, re-read after power cycle |
| Torque limit | Runtime, per group | `self_check` |
| Mechanical zero, and the `-π..+π` flag | `humanoid_set_zero.py` — see [Joint zeroing](joint-zeroing.md) | Model comparison |
| Direction convention | **TODO**{ .dh-missing } | **TODO**{ .dh-missing } |

## The ID map

The complete joint → CAN ID → bus → model table for all 31 actuators is on
[CAN bus](../electrical/can-bus.md#the-actuator-map), where it sits next to the
topology it belongs to. Work from that table; do not keep a second copy.

Its numbering is one decade per limb — `1` waist, `5`–`8` cameras, `10`–`16` left
arm, `20`–`26` right arm, `31`–`36` left leg, `41`–`46` right leg — and every ID
is unique across the whole robot, not just within its bus.

## Setting an ID

!!! missing "Read this before you assemble anything"
    The team's bench units all came up at the **same factory CAN ID, 127**:
    RS03 and RS04 units (and a third RobStride model tested during
    [selection](../design/actuator-selection.md), not used on the robot) each
    appear in the vendor tool as motor 127, and the RS04 parameter table reads
    `CAN_ID = 127`. RS00, RS02, RS05 and RS06 were not observed
    **UNVERIFIED**{ .dh-unverified }. *Source: team actuator test videos and
    design log, "Robstride setup".* If setting an ID requires the motor to be
    alone on a bus — which is the usual case, but not confirmed for these
    drives **UNVERIFIED**{ .dh-unverified } — then all 31 actuators must be
    addressed **before they are installed in the robot**, one at a time, on a
    bench.

    Discovering this after the legs are closed costs a disassembly. It is called
    out here rather than in [Assembly](../assembly/index.md) because the
    procedure is not yet written down, and a builder needs to know the risk even
    while the procedure is missing. The individual gaps are itemised in the box
    below.

### The vendor tool

The team uses RobStride's configuration software, downloaded from
[robstride.com/download](https://www.robstride.com/download); in the team's
videos its window is titled "Lingzu v0.0.4". Its device module has a
**modify motor CAN ID** function, alongside connect, device information,
encoder calibration, set mechanical zero and firmware upgrade; its config
module reads and writes the parameter table. The parameter table can only be
edited while the motor is in standby.
*Source: team design log, "Robstride setup"; team actuator test videos;
RobStride RS03 and RS04 manuals (cited, not redistributed).*

Per the manuals, the tool talks to the motor through the vendor's own serial
USB-CAN module (CH340 driver, AT mode), not through a `gs_usb` adapter like the
robot's CANable PRO V2.0. The deploy repository has no RobStride ID-setting
code (its only `change_id.py` is for the Feetech gripper servos). So a builder
probably needs the vendor module to set IDs; that is an inference, not a
documented step **UNVERIFIED**{ .dh-unverified }.

!!! missing "MISSING — Motor ID-setting steps, bus-isolation rule, firmware baseline and label scheme"
    - The **exact ID-setting steps** in the vendor tool, and confirmation of
      which USB-CAN interface they need. RobStride's software and manuals are
      the manufacturer's to distribute — this release ships neither (see
      `control/CALIBRATION.md` in the deploy repository) — so what is needed
      here is the procedure and a pointer, not a copy.
    - Whether the motor must be **alone on the bus** to be addressed. The
      RS02, RS03 and RS04 manuals do not say. This single yes/no answer
      determines whether ID assignment happens before or after assembly, and
      therefore where it sits in the build order.
    - The **firmware version** the reference robot runs. The only version in
      the team records is one RS04 bench unit (below), which is not a robot
      baseline. A mixed-firmware fleet of 31 drives is a class of bug nobody
      wants to debug at 200 Hz.
    - A **label scheme**: write each actuator's ID and joint name on the actuator
      itself before it goes into the robot. Once installed, reading an ID
      requires powering the bus. Team photos show hexadecimal CAN-ID labels
      such as `0X1A` from the [single-leg phase](../design/single-leg-phase.md),
      whose ID table is superseded by the actuator map; the label scheme on the
      finished robot is **UNVERIFIED**{ .dh-unverified }.

    *Owner: controls lead + hardware lead. Blocks
    [Assembly](../assembly/index.md).*

### One RS04 bench unit, for reference

The team read the full parameter table of one RS04 on the bench, at factory
settings. It is **not** the robot's configuration or firmware baseline; it is
the only complete parameter read-out in the team records.

| Parameter | Value |
| --- | --- |
| Firmware | `AppCodeVersion` 0.1.0.5 (build Aug 23 2024; boot build Mar 26 2024) |
| `CAN_ID` / `CAN_TIMEOUT` | 127 / 0 |
| `GearRatio` | 9 |
| `Kt_Nm/Amp` | 1.5 |
| `limit_cur` / `rated_i` | 90 / 19 |
| `cur_kp` / `cur_ki` | 0.17 / 0.012 |
| `motorOverTemp` / `overTempTime` | 1450 / 1 |
| `VBUS` at read-out | 29.26 (bench supply) |

*Source: team design log, RS04 "parameters (from upper computer software)".*

!!! unverified "UNVERIFIED — RS04 torque constant: 1.5 in firmware vs 2.1 N·m per A rms"
    The bench unit's firmware reports `Kt_Nm/Amp` 1.5; the datasheet, the
    team's motor specification and `py_motor.py` use 2.1 N·m/A<sub>rms</sub>.
    Computed: 2.1 / √2 ≈ 1.48, so the firmware figure may be per peak ampere.
    Likewise `rated_i` 19 against 27 A peak in the manual (27 / √2 ≈ 19.1,
    computed). Confirm the unit basis with RobStride before using either in a
    current or torque calculation.

    *Owner: controls lead.*

## Writing the current limits

```bash
cd <deploy-repo>/control
python humanoid_set_current_limit.py            # default scale 0.6
python humanoid_set_current_limit.py --scale 0.5
```

The script computes `min(default × scale, 40 A)` per motor from the per-model
defaults, prints the planned table, waits for you to type `yes`, writes the
limits, **saves them to the drives**, self-checks, and disables. The per-model
defaults and the resulting written values are tabulated on
[Power system](../electrical/power-system.md#configured-current-limits).

Because the script saves to the drives, this is persistent configuration, not a
runtime setting. Re-read it after a power cycle to confirm it stuck.

The range of register `0x7018` (current limit) depends on the model: RS02
0–23 A, RS03 0–43 A, RS04 0–90 A. The `0~23A` comment in
[`py_motor.py`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/hardware_bindings/motor/py_motor.py)
matches the RS02 manual, and the per-model defaults for these three models
(23, 43 and 60 A) sit inside their ranges. The team's RS04 bench unit read
`limit_cur` 90. *Source: RobStride RS02, RS03 and RS04 manuals, `0x7018` rows;
team design log.*

!!! unverified "UNVERIFIED — Current-limit register 0x7018 range for RS00, RS05 and RS06"
    The RS00, RS05 and RS06 manuals are not in the team records, so the range
    of `0x7018` for those models is unchecked. The RS04 firmware parameter
    table also lists a maximum of 150 for `limit_cur`, against the manual's
    0–90 A. Check each model's datasheet before writing limits to a robot you
    built.

    *Owner: controls lead.*

## Runtime torque limits

Current limits live in the drives. Torque limits are applied per run, as a
fraction, and per group:

```bash
python humanoid_real_env.py --task <task> --torque-limit 0.8 --enable-motor true ...
```

- `--torque-limit` is a global ratio. The runbook's standing profile uses `0.8`;
  the hardware joint-monkey uses `0.5`; the bench smoke test uses `0.05`.
- `--enable-motor` accepts `true`, `false`, `leg`, `arm`, `camera` or
  `arm_camera`, so a session can power exactly one group. **Use this.** On a new
  robot there is no reason to energise the legs while you are proving an arm.
- The camera gimbals can be capped below the global ratio independently.

Start low. Raise it only when the stage below has passed.

## The motor parameter registers

For anyone writing their own tooling or reading a trace. From
[`py_motor.py`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/hardware_bindings/motor/py_motor.py):

| Register | Name | Access | Notes |
| --- | --- | --- | --- |
| `0x7005` | `run_mode` | W/R | 0 operation control, 1 position, 2 speed, 3 current, 4 zero |
| `0x7006` | `iq_ref` | W/R | Current-mode Iq command |
| `0x700A` | `mech_vel_ref` | W/R | Speed-mode command |
| `0x700B` | `torque_limit` | W/R | Torque limit |
| `0x7010` / `0x7011` | `cur_kp` / `cur_ki` | W/R | Current loop gains — manual defaults differ from the code, see below |
| `0x7016` | `mech_pos_ref` | W/R | Position-mode angle command, rad |
| `0x7017` | `spd_limit` | W/R | Position-mode speed limit |
| `0x7018` | `cur_limit` | W/R | Current limit — RS02 0–23 A, RS03 0–43 A, RS04 0–90 A; other models **UNVERIFIED**{ .dh-unverified } |
| `0x7019` | `mech_pos` | R | Load-end mechanical angle, rad |
| `0x701B` | `mech_vel` | R | Load-end speed |
| `0x701C` | `v_bus` | R | Bus voltage |
| `0x701E`–`0x7020` | `loc_kp`, `spd_kp`, `spd_ki` | W/R | Position and speed loop gains |
| `0x7029` | `zero_sta` | W/R | 0: reports 0–2π (default). 1: reports −π..+π |
| `0x7028` | CAN timeout | W/R | The host writes `5000` at every startup — this is what the [dropout probe](../electrical/can-bus.md#bus-health-and-fault-diagnosis) reads as a witness of whether a motor rebooted. 0 disables it; the seconds scale differs between manuals **UNVERIFIED**{ .dh-unverified } |

!!! unverified "UNVERIFIED — current-loop gains and CAN-timeout scale the drives actually run"
    Manual defaults and the code disagree. Current loop: the RS02 manual gives
    `cur_kp` 0.17 and `cur_ki` 0.012, the RS04 manual 0.05 and 0.05.
    `py_motor.py` carries 0.17 / 0.012 for RS03, RS04 and RS06 and 0.12 / 0.016
    for RS00, RS02 and RS05, and the team's RS04 bench unit read 0.17 / 0.012.
    In the published `py_motor.py` the lines that would write these gains are
    commented out. CAN timeout: the RS02 manual scales 20000 = 1 s, the RS04
    manual 12000 = 1 s, so the `5000` the host writes is about 0.25 s or about
    0.42 s (computed; see [CAN bus](../electrical/can-bus.md#bus-health-and-fault-diagnosis)).
    Read back what the robot's drives actually hold, per model.

    *Owner: controls lead.*

## Verifying the configuration

{{ step(1, "Self-check every motor") }}

```bash
cd <deploy-repo>/control
python humanoid_config.py
```

Run directly, the motor table self-checks every motor and prints its type, bus
voltage, position, torque limit and current limit. Nothing moves.

{{ step(2, "Power-cycle and re-read") }}

Configuration that is not saved is configuration you will lose at the worst
moment. Power the robot down, back up, bring the CAN buses up again, and run the
self-check a second time. Every value must read back the same.

{{ step(3, "Smoke-test the arm joints at a 5 % torque ceiling") }}

The repository's own first-motion test:

```bash
python humanoid_test_motor.py
```

It enables the motors at a **5 % torque ceiling**, starts the motion-control loop
and drives the arm joints through a 0.1 rad sine at 300 Hz, publishing telemetry.
It has no flags — read it before you run it.

!!! unverified "UNVERIFIED — Which joints the smoke test actually drives"
    This page, the toolkit table and acceptance test A4 all say the sine goes to
    the **arm joints only**. The script's own description says "the arm joints
    (index 13 onward)", but in the motor table's order in `humanoid_config.py`
    the entries after the fourteen arm joints are the four camera-gimbal
    joints, so "index 13 onward" may also cover the gimbals. If it does, a
    builder watching for "the wrong joint moving" will see the gimbals move and
    either abort a healthy robot or learn to ignore unexpected motion.

    Confirm by checking the index range the script writes against the motor
    table, then state here exactly which joints move.

    *Owner: controls lead.*

!!! danger "This is the first time this robot moves under its own power"
    Robot suspended, legs straight, e-stop in hand, everyone clear. 0.1 rad is a
    small motion, and 5 % torque is a small torque, and this is still the moment
    a reversed direction or a mis-mapped ID announces itself.

    Watch for: the *wrong* joint moving, a joint moving the *wrong way*, any
    joint that does not move, and any noise from a joint that does.

{{ checkpoint("Every actuator responds at its assigned ID on its assigned bus, its configuration reads back unchanged after a power cycle, and the 5 % smoke test moves the expected joints in the expected directions with no unexpected noise.") }}

## Direction convention

!!! missing "MISSING — SAFETY — Positive direction and travel limits for each of the 31 joints"
    **Which way is positive for each of the 31 joints**, matching the robot model
    in the
    [simulation repository](https://github.com/generalroboticslab/duke_humanoid_v2_simulation).
    Publish it as a per-joint table with a figure, alongside each joint's travel
    limits.

    This is the most dangerous gap on the page. A joint wired or configured
    backwards passes every check above — it answers at the right ID, it reports
    the right voltage, it self-checks, it moves when told — and then inverts a
    feedback loop the moment the machine is under policy control. There is no
    cheap test for it after the fact.

    What is needed: a table of joint name, positive direction in words, the
    travel limit at each end, and a figure a builder can hold against the robot.
    Plus a procedure: drive each joint a small positive amount and confirm the
    physical direction against the figure, one joint at a time, at a low torque
    ceiling, before anything runs a policy.

    *Owner: controls lead. Blocks [Acceptance tests](acceptance-tests.md).*
