# First power-on

Prove that every device answers, with no motor enabled.

{{ step(1, "Power up on the bench supply") }}

Bench supply on the 48 V bus, current limit low; boot the computer. A supply current that climbs to the limit is a short: cut power, back to [Pre-power checks](../electrical/index.md#pre-power-checks).

{{ step(2, "Inventory the USB devices") }}

```bash
lsusb -t                  # both RealSense at 5000M (USB 3), not 480M
ip link show type can     # six CAN interfaces, still down
rs-enumerate-devices -s   # two cameras; note the serials and sides
ls -la /dev/ttyACMservo*  # both gripper driver boards
```

{{ step(3, "Bring up the CAN buses") }}

```bash
python humanoid_setup_can.py
for c in can9 can21 can22 can23 can24 can25; do echo -n "$c: "; ip -details link show $c | grep -o "can state [A-Z-]*" | head -1; done
```

✅ **Check:** all six buses ERROR-ACTIVE.
{ .dh-check }

{{ step(4, "Read every motor") }}

```bash
python humanoid_motor_temps.py   # read-only
```

✅ **Check:** 31 rows; ID and bus match the [actuator map](../electrical/index.md#the-actuator-map); bus voltage equals the supply on every motor; temperatures near ambient.
{ .dh-check }

{{ step(5, "Power down") }}

`python humanoid_setup_can.py --down`, shut the computer down, then cut the supply.
