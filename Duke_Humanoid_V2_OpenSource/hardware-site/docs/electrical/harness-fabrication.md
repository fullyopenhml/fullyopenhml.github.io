# Harness fabrication

Every cable on the robot is one of the types below. Red is +, black is −; CAN_H is yellow and CAN_L is blue throughout the harness. Solder the XT30 cups (iron about 480 °C), do not crimp them; never mate or unmate a power connector under power.

| Cable | Conductors | End A | End B | Carries |
| --- | --- | --- | --- | --- |
| Actuator drop | 2 × 18 AWG power + 1 twisted pair CAN | XT30(2+2) female, cable side (Amass XT30(2+2)-F.G.B) | XT30(2+2) female | 48 V and CAN in one shell: pin 1 +, pin 2 −, pin 3 CAN_L, pin 4 CAN_H. Every actuator has an in and an out socket (board side XT30PB(2+2)-M.G.B), so the drops chain motor to motor |
| Bus head | 1 twisted pair | CANable PRO screw terminals, 120 Ω across H–L | XT30(2+2) female, power pins unused | CAN only, adapter to the first motor |
| Bus tail terminator | — | 120 Ω resistor across CAN_H–CAN_L in an XT30(2+2) shell | — | Plugs into the last motor's out socket |
| CAN twisted pair | One pair from Ethernet cable | — | — | Coloured conductor → CAN_H (yellow lead), white → CAN_L (blue lead); 3/32 in heat-shrink per lead, 1/4 in over the pair |
| Pack lead and series link | 10 AWG silicone | EC5 | EC5 / screw terminal | 48 V trunk |
| Block feeds | 12 AWG silicone | Screw terminal | Screw terminal | 48 V bus to each power block; pack − to each ground block |
| Computer feed | 16 AWG silicone | Converter (E11) 12 V terminals | Computer DC plug | 12 V; 10 A inline fuse on the 48 V side |
| Gripper servo feed | 18 AWG silicone | Converter (E12) 12 V terminals | Servo driver board (E10) terminals | 12 V, one per gripper |
| Camera USB | Belkin USB-A to USB-C (E9) | Computer / hub 1 | Right-angle USB-C adapter (E21) on the camera | USB 3 (5 Gbit/s) |
| Gripper servo signal | Servo's own lead | Servo (E15) | Driver board (E10) | Serial bus |

## Connectors and consumables

| Item | Part | Where |
| --- | --- | --- |
| Actuator connector, cable side | Amass XT30(2+2)-F.G.B (female, 4-pin: 2 power + 2 signal) | Both ends of every actuator drop, bus head, terminator |
| Actuator connector, board side | Amass XT30PB(2+2)-M.G.B (male, PCB mount) | Already on every RobStride board, in and out |
| Pack connector | EC5 | Pack leads, series link |
| Bus terminator | 120 Ω resistor | Adapter end and last motor of each bus |
| CAN pair | One twisted pair from Ethernet cable | All CAN runs |
| Power wire | Silicone, 12 / 16 / 18 AWG | Trunks / computer / actuator drops and grippers |
| Heat-shrink | 3/32 in per lead, 1/4 in over a pair or joint | Every solder joint |
| Loom | 1/4 in and 3/8 in | Limb runs |

XT30(2+2) is rated 15 A with 18 AWG wire. Quantities are yours to size: [Cables and connectors](../bom/index.md#cables-and-connectors).

✅ **Check:** each finished cable conducts pin to pin, has no short between pins, and is labelled at both ends with its bus or rail.
{ .dh-check }
