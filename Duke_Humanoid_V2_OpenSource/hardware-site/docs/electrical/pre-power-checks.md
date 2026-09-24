# Pre-power checks

With no pack connected:

1. Every 48 V conductor conducts end to end; + to − on each bus reads open (drive capacitors charge slowly, no steady short).
2. Every XT30(2+2): + at pin 1, − at pin 2, CAN_H at pin 4, checked against the pinout, not the colour.
3. Each of the six buses reads about 60 Ω between CAN_H and CAN_L.
4. Each 48 V→12 V converter gives 12 V on a bench supply before it sees a pack.
5. Both packs: no swelling, cells balanced, then the series link: one pack's + to the other's −.

Then [First power-on](../bringup/index.md#first-power-on), robot suspended.
