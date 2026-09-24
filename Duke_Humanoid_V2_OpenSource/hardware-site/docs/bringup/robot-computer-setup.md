# Robot computer setup

Once, before any bus is touched. Ubuntu 22.04 on the MINISFORUM X1-470.

| Item | Do |
| --- | --- |
| CAN adapters | Flash each CANable PRO V2.0 with candleLight (ElmueSoft [CANable Firmware Update](https://netcult.ch/elmue/CANable%20Firmware%20Update/), button held for flash mode, adapter plugged straight into the computer) |
| Host | `sudo apt remove brltty`; `sudo adduser $USER netdev dialout`; `sudo apt install can-utils libsocketcan-dev`; log out and in |
| Bus names | One udev rule per adapter serial, below; then `sudo udevadm control --reload-rules && sudo udevadm trigger` and replug |
| IMU | TransducerM TM171 in the vendor's ImuAssistant: output Composite + Status, 800 Hz, USB port, gyro / accelerometer / magnetometer on, GyroErrFilter and self-adapt filter on |
| Cameras | librealsense2 **2.58.1** (`librealsense2 -utils -dev -gl -udev-rules`) from `librealsense.realsenseai.com`; deploy pins `pyrealsense2==2.58.1.10581` |
| Control stack | Build `deploy/control` with the CMake + vcpkg + Ninja presets |

```text
# /etc/udev/rules.d/99-candlelight.rules — one line per adapter, serial from `sudo dmesg`
SUBSYSTEM=="net", ACTION=="add", ATTRS{serial}=="<serial>", NAME="can9"     # left arm
SUBSYSTEM=="net", ACTION=="add", ATTRS{serial}=="<serial>", NAME="can21"    # right arm
SUBSYSTEM=="net", ACTION=="add", ATTRS{serial}=="<serial>", NAME="can22"    # waist, shoulder_1
SUBSYSTEM=="net", ACTION=="add", ATTRS{serial}=="<serial>", NAME="can23"    # right leg
SUBSYSTEM=="net", ACTION=="add", ATTRS{serial}=="<serial>", NAME="can24"    # left leg
SUBSYSTEM=="net", ACTION=="add", ATTRS{serial}=="<serial>", NAME="can25"    # camera gimbals
SUBSYSTEM=="net", KERNEL=="can[0-9]*", GROUP="can", MODE="0660"
```
