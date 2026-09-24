# Power system

<figure markdown>
  ![Power wiring diagram, Duke Humanoid V2](../assets/wiring/power-supply-v2.webp){ loading=lazy }
  <figcaption>Power wiring. Red: 48 V; black: ground. [Full size](../assets/wiring/power-supply-v2.png).</figcaption>
</figure>

| From | To | Voltage | Wire | Connectors |
| --- | --- | --- | --- | --- |
| Pack 1 − | Pack 2 + (series link) | 44.4 V nominal, 50.4 V full | 10 AWG silicone | EC5 |
| Pack + | Surge protector (E18) → 48 V bus | 48 V | 12 AWG silicone | EC5 at the pack; screw terminals |
| 48 V bus, pack − | Lower-body power and ground blocks (E19): both legs, waist | 48 V | 12 AWG silicone | Screw terminals |
| 48 V bus, pack − | Upper-body power and ground blocks (E19): both arms, both `shoulder_1`, four camera motors | 48 V | 12 AWG silicone | Screw terminals |
| Power block | Each actuator, daisy-chained | 48 V | 18 AWG silicone | XT30(2+2), see [Harness fabrication](#harness-fabrication) |
| Upper-body power block | 10 A inline fuse → 48 V→12 V converter (E11) → computer (E0) | 48 V → 12 V | 16 AWG silicone (12 V side) | Converter terminals; computer DC jack |
| Upper-body power block | 48 V→12 V converter (E12, one per gripper) → servo driver board (E10) | 48 V → 12 V | 18 AWG silicone | Board screw terminals |

- TVS diodes (E8, ten) sit across power and ground at each block pair.
- A voltage checker (E20) rides on each pack's balance lead.
- The computer is powered only when the upper-body block is live.
