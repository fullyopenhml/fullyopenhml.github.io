# First power-on

The first time the robot is energised. Done once per machine, with it suspended,
with two people, and with the e-stop in someone's hand.

The goal of this page is deliberately small: **prove the robot can be energised
and that all 31 actuators answer, without enabling a single one of them.** Motion
comes later, on [Motor ID and config](motor-id-and-config.md). Resist the urge to
skip ahead — every stage below exists to catch a class of build fault while it is
still cheap.

## Prerequisites

- [Pre-power checks](../electrical/pre-power-checks.md) passes in full, signed.
- The robot is suspended from a rated hoist, **legs hanging straight**, with
  clear space beneath it.
- The control stack builds and runs on the robot computer.
- A second person holds the e-stop and is not the person connecting power.

!!! missing "The e-stop this page relies on is not specified yet"
    Every stage below assumes an e-stop in the safety person's hand, but no
    e-stop is in the parts list, drawn in the team power diagram, or described
    anywhere in the project: what it is, where it mounts, and what it cuts are
    all unpublished. This is tracked,
    as a release blocker, on
    [Power system](../electrical/power-system.md#protection-disconnect-and-e-stop),
    [Safety](../before-you-start/safety.md) and
    [Torso and waist](../assembly/torso-and-waist.md). Do not treat this page
    as runnable until those are closed.

## Host prerequisites

Set up the robot computer before the first power-on. These are the team's own
host steps (Ubuntu 22.04):

```bash
sudo apt remove brltty                    # it grabs USB-serial devices, so /dev/ttyUSB0 never appears
sudo adduser $USER netdev                 # bring CAN interfaces up without sudo
sudo adduser $USER dialout                # serial access
# log out and back in
sudo apt update
sudo apt install can-utils libsocketcan-dev
modinfo gs_usb                            # the CAN adapter driver is present
lsmod | grep can                          # and loaded
```

To find which device node a new USB device creates, list `/dev` before and
after plugging it in and compare:

```bash
ls -1 /dev > before.txt
# plug the device in
ls -1 /dev > after.txt
diff before.txt after.txt
```

*Source: team design log, "CAN bus"; the brltty issue is described on
[Ask Ubuntu 1403705](https://askubuntu.com/questions/1403705/dev-ttyusb0-not-present-in-ubuntu-22-04).*
The deploy repository's `control/docs/SETUP.md` §3 covers `dialout` and the
kernel modules; the `brltty` and `netdev` steps are additions from the team log.
The adapter udev rules and firmware are on
[CAN bus](../electrical/can-bus.md#interface-naming).

## Roles

| Role | Does | Does not |
| --- | --- | --- |
| **Operator** | Connects power, runs commands, reads output aloud | Touch the robot |
| **Safety** | Holds the e-stop, watches the machine, calls the abort | Touch the keyboard |

One person doing both is how the first fault becomes the second fault. Two
people, every time, for the whole of this page.

## Use a bench supply, not a pack

For everything on this page, energise the motor bus from a **current-limited
bench supply** rather than from the packs. A supply with the current limit set
low turns a wiring fault into a supply that folds back and beeps. A 10 000 mAh
LiPo turns the same fault into a fire.

!!! missing "MISSING — SAFETY — Bench-supply voltage and per-stage current limit"
    The bench supply settings: the voltage and the current limit for each stage
    below. The pack configuration is now published (two 6S packs in series,
    44.4 V nominal and 50.4 V full, computed; see
    [Power system](../electrical/power-system.md#pack-configuration-and-bus-voltage)),
    but the team has not stated what bench voltage to use. Publish a limit per stage, because
    the right limit for "computer only" and for "all 31 drives idle" are not the
    same number. Without a published limit, the current limit this page relies
    on to turn a wiring fault into a beep rather than a fire has no value to be
    set to.

    Also publish what to do if no bench supply of that rating is available,
    because many builders will not have one, and "use a pack instead" needs to be
    an explicit decision rather than a default.

    *Owner: electrical lead.*

## The sequence

{{ step(1, "Energise the computer only") }}

Motor bus still disconnected. Bring up the onboard computer alone and confirm it
boots to a known state and you can log in.

!!! unverified "UNVERIFIED — SAFETY — how to power the computer without the motor bus"
    The team power diagram feeds the computer from the **same upper-body
    distribution block** as both arms, both `shoulder_1` joints and the four
    gaze motors (upper-body block, 10 A fuse, 48V-to-12V buck converter,
    computer), and draws no switch or disconnect on that path. As drawn, the
    computer cannot be powered from the packs without energising that block,
    so "motor bus still disconnected" has no drawn way to happen. How the team
    does step 1 is not recorded. Do not improvise it: get the owner to state
    the method in writing.

    *Owner: electrical lead.*

Watch and smell. Anything hot, anything that smells, any unexpected noise: cut
power.

{{ step(2, "Inventory the USB devices") }}

Still no motor bus. Every peripheral on this robot is a USB device, and it is far
easier to find a missing one now than to misread it as a robot fault later.

```bash
lsusb                         # everything present?
lsusb -t                      # each RealSense must show 5000M, not 480M
ip link show type can         # six interfaces present (still down)
rs-enumerate-devices -s       # two cameras, with their serial numbers
ls -la /dev/ttyACMservo*      # both gripper driver boards
```

USB Hub #1 carries the two RealSense D436 cameras and the IMU; USB Hub #2 the CANable PRO V2.0 adapters; USB Hub #3 the left and right gripper servo driver boards. Hub power and the USB power budget are not shown. Whether the first D436 and the can9 and can25 adapters plug into their hub or directly into the computer is **UNVERIFIED**{ .dh-unverified }.

*Source: team data wiring diagram (V2).* Use it to check that every device is
on the hub the diagram gives; the diagram is on
[Electrical](../electrical/index.md#the-two-team-diagrams).

Two things to do here and not later:

- **Record both camera serial numbers.** They are how each camera is pinned to a
  port; without them the server takes USB enumeration order, and a left/right
  swap is completely silent — tags land in the wrong camera frame while every log
  line looks healthy. See [Camera calibration](camera-calibration.md).
- **A camera showing `480M` is on USB 2.** Replug or move ports until `lsusb -t`
  shows `5000M`. If it will not hold USB 3, that is a routing or hub problem, not
  a camera problem — go back to [Routing](../electrical/routing.md).

{{ step(3, "Bring up the CAN buses") }}

Still no motor bus power. The adapters are USB-powered, so they enumerate without
the drives.

```bash
cd <deploy-repo>/control
python humanoid_setup_can.py
for c in can9 can21 can22 can23 can24 can25; do
  echo -n "$c: "; ip -details link show $c | grep -o "can state [A-Z-]*" | head -1
done
```

All six must report **ERROR-ACTIVE**. A bus that will not come up is an adapter,
a udev rule, or a USB problem — none of which is improved by adding motor power.
Fix it here.

To look closer at one bus, use the team's inspection commands:

```bash
ip -details -statistic link show can22   # state and error counters
candump any,0:0,#FFFFFFFF -extA          # listen to every interface, error frames included
```

*Source: team design log, "CAN bus".* `candump` only listens; stop it before
running any tool that transmits.

{{ checkpoint("All six CAN buses report ERROR-ACTIVE with the motor bus still unpowered.") }}

{{ step(4, "Energise the motor bus") }}

The safety person has the e-stop. The operator brings the bench supply up to the
bus voltage with the current limit set, and watches the current reading rather
than the robot.

| Observation | Action |
| --- | --- |
| Supply goes into current limit | **Cut power immediately.** There is a short. Return to [Pre-power checks](../electrical/pre-power-checks.md) group B |
| Any smell, smoke, or heat | **Cut power immediately** |
| Any actuator moves | **Cut power immediately.** Nothing has been enabled; a motor that moves is a motor that is not in the state you think it is |
| Quiescent current settles at a steady low value (expected value: **TODO**{ .dh-missing }) | Continue |

!!! missing "MISSING — Expected quiescent current, all 31 drives powered and none enabled"
    The expected quiescent current with all 31 drives powered and none enabled.
    This is the single most useful number on this page — it is the one reading
    that says *the machine is wired correctly* before anything moves — and it
    does not exist. Measure it on the reference robot and publish it, with the
    tolerance that counts as a pass.

    *Owner: electrical lead.*

{{ step(5, "Read every motor, without enabling any") }}

```bash
cd <deploy-repo>/control
python humanoid_motor_temps.py
```

This tool is read-only by construction: it solicits feedback frames, prints one
row per motor in URDF order — joint name, CAN ID, temperature, bus voltage — and
never sends a position command or enables anything. Run it with
`humanoid_real_env.py` stopped.

Check three things in its output:

| Check | Pass |
| --- | --- |
| Row count | **31 rows**, every one answering. A row marked *no feedback yet* is a motor that is not on its bus |
| Bus voltage | Every motor reports the bus voltage you set, within the supply's own tolerance. A motor reading low is at the far end of a bad conductor |
| Temperature | All near ambient. The tool flags anything above 60 °C |

Compare every row against the [actuator map](../electrical/can-bus.md#the-actuator-map).
A motor that answers at the wrong ID, or on the wrong bus, is a build error to be
fixed now — not a thing to work around in software later.

{{ checkpoint("All 31 actuators answer, at the ID and on the bus the actuator map gives, reporting the expected bus voltage and near-ambient temperature. No actuator has been enabled.") }}

{{ step(6, "Profile the bus, at a 1 % torque ceiling") }}

```bash
python humanoid_profile_motor_latency.py
```

This runs the motion-control loop at a 1 % torque ceiling and sends no position
command, then prints average, standard deviation, minimum, maximum and p99
round-trip latency per motor and per bus. It is the last diagnostic before
anything is allowed to move, and it is sensitive to marginal wiring in a way that
a continuity meter is not.

!!! missing "MISSING — Reference CAN latency per bus, and the suspect-harness threshold"
    The reference latency figures from the original robot: per bus, the average
    and p99 a healthy machine shows, and the value above which a builder should
    suspect the harness. The tool produces numbers; nobody has published what a
    good number looks like.

    *Owner: controls lead.*

{{ step(7, "Power down, in order") }}

Stop here. Enabling actuators is [Motor ID and config](motor-id-and-config.md),
and it is a separate session with a fresh head.

Controlled shutdown **UNVERIFIED**{ .dh-unverified } — a sensible order, not a
specified one (see below):

1. Stop every tool talking to the motors.
2. `python humanoid_setup_can.py --down` to tear the buses down.
3. Shut the computer down cleanly.
4. Remove motor bus power.
5. Disconnect the supply or the packs.

!!! missing "MISSING — SAFETY — Power-on and power-off order for the rails"
    The **power-on and power-off order for the rails themselves** — compute, CAN
    adapters, motor bus, 12 V, camera servos — as a specified sequence rather
    than the sensible-looking one above. On a machine where the CAN adapters are
    USB-powered from the computer and the drives are not, the order determines
    what sees a bus partner disappear. This is the largest remaining unknown on
    the page.

    *Owner: electrical lead + controls lead.*

## Abort criteria

Stop immediately, cut power, and do not restart to "see if it does it again":

- Any smell, smoke, or discoloration.
- Anything hot to the touch.
- The bench supply entering current limit.
- Any unexpected motion, at any stage.
- Any actuator answering at an ID or on a bus other than the map gives.
- Any CAN bus stuck in ERROR-WARNING, or error frames in the log.
- Anyone present calling the abort, for any reason, including none.

For a fault that appeared and then went away, run the dropout probe **before**
restarting or power-cycling — a power cycle destroys the evidence that separates
a link break from an MCU reboot. See
[CAN bus](../electrical/can-bus.md#bus-health-and-fault-diagnosis).

## What comes next

The control stack enables motors in groups — `--enable-motor` accepts
`true`, `false`, `leg`, `arm`, `camera` or `arm_camera` — so the first motion can
be limited to one part of the robot. That staged path is the whole design of
[Motor ID and config](motor-id-and-config.md) and
[Acceptance tests](acceptance-tests.md).
