# Troubleshooting

Symptom to cause. This page is worth more than any other reference page once a
second robot exists, and it can only be written from real failures — so it starts
nearly empty and grows.

## Seeded from failures already on record

These few entries come from the published operations and setup documentation,
where a failure was hit hard enough that somebody wrote it down.

| Symptom | Cause | What to do |
| --- | --- | --- |
| The CAN interfaces come up as `can0`, `can1`, … and the setup script cannot find its buses | Without a `udev` rule the USB-CAN adapters are named in plug order, not by identity. The scripts expect `can9` and `can21`–`can25` | Add one `udev` rule per adapter keyed to its USB serial, reload rules and replug. See [CAN bus](../electrical/can-bus.md) |
| A CAN bus refuses to come up and the setup script cannot reset it | `usbreset` is missing. It ships with `usbutils`, which a minimised Ubuntu image can drop | Install `usbutils` before first bring-up; check with `which usbreset` |
| The torso is tilted and the perception geometry is wrong, with no obvious mechanical fault | The robot is hanging with **bent legs**. Bent legs tilt the torso, which corrupts the geometry the stack assumes | Re-hang with the legs straight. Three sessions were lost to this before it was written down |
| A pinned process exits immediately with an affinity error, which reads like a robot fault | A CPU core list copied from the reference rig onto a machine with fewer cores | Re-derive the core sets from your own CPU count; keep the partitioning rule, not the numbers |
| On Ubuntu 22.04, a USB-serial device such as `/dev/ttyUSB0` never appears | `brltty` claims USB-serial devices | `sudo apt remove brltty`, then replug. See [Software](../software.md#prerequisites). *Source: team design log.* |
| The setup script's USB reset hits the wrong adapter, or a bus name maps to an adapter you did not expect | Two lines in `/etc/udev/rules.d/99-candlelight.rules` give the same `NAME`. `humanoid_setup_can.py` keeps the last line for each name (computed from the code); the team's own rules file had three lines for `can9`, one marked damaged | Keep exactly one line per name, reload the rules and replug. *Source: team design log; `deploy/control/humanoid_setup_can.py`.* |
| A joint misbehaves after an actuator's driver board was re-mounted on the motor, or its three phase leads were reconnected in a different order | The magnetic encoder calibration no longer matches the motor | Re-calibrate the encoder from the vendor tool before running the joint. *Source: RobStride 02, 03 and 04 product manuals.* |
| An actuator faults or jumps when you change its control mode | The mode was switched while the joint was running | Send a stop command first, then switch mode. *Source: RobStride 02, 03 and 04 product manuals.* |

## Looking at a CAN bus

The commands the team uses to inspect a bus (`can-utils` and `iproute2`):

```bash
ip -details -statistic link show canN        # state and error counters
candump any,0:0,#FFFFFFFF -extA              # every frame on every interface, error frames included, decoded
canbusload canN@1000000 -cbr                 # bus load, run in a second terminal
```

Replace `canN` with the interface, for example `can23`. The team's references
are the Pengutronix note "First steps using the candleLight" and the Linux
kernel [SocketCAN documentation](https://docs.kernel.org/networking/can.html).
*Source: team design log, "CAN bus".*

## Everything else

!!! missing "MISSING — Troubleshooting entries from the original build's failures"
    Seed the rest from failures the original build actually hit. Each entry needs
    the symptom **as a builder would describe it**, the cause, and the fix —
    generic advice is worse than an empty table because it looks like coverage.

    Areas where entries are expected:

    - An actuator does not appear on its bus, or appears with the wrong ID.
    - A joint moves in the wrong direction after assembly.
    - A joint binds, or has backlash, after a bearing is pressed.
    - A machined part does not fit its mating part.
    - A camera does not enumerate, or enumerates without depth.
    - The robot draws more current than expected while standing still.
    - A pack goes flat faster than expected.
    - A harness conductor fails at a joint after some hours of motion.

    The deploy repository already keeps a numbered incident register for the
    control stack, and that pattern works well enough that it should simply be
    extended to mechanical and electrical failures. See the incident-register
    MISSING box on [Safety](../before-you-start/safety.md).

    *Owner: hardware lead, continuously.*
