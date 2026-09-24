# Actuators

Every joint on this robot is quasi-direct-drive. The parts list carries
{{ bom_qty("actuators.csv") }} RobStride units across {{ bom_count("actuators.csv") }}
models, {{ bom_subtotal("actuators.csv") }} — the largest single line in the build
**UNVERIFIED**{ .dh-unverified } (the machined parts may cost more; see
[Which category costs the most](index.md#which-category-costs-the-most)).
This page is where a builder confirms which model goes in which joint, what each
one costs, and what to do when a model is out of stock.

## Counts and cost, by model

Rendered from `docs/data/actuators.csv`. Quantities and prices are transcribed
from the source spreadsheet; on that sheet the unit-cost column really is a unit
cost, and every line total is a clean multiple of it.

| Model | Part ID | Qty | Unit cost | Line total | Vendor |
| --- | --- | ---: | ---: | ---: | --- |
{% for r in pd_read_csv("data/actuators.csv", dtype="str", keep_default_na=False).to_dict("records") %}| {{ r.mpn }} | `{{ r.part_id }}` | {{ r.qty_per_robot }} | {{ money(r.unit_cost_usd|float) }}{{ " **UNVERIFIED**{ .dh-unverified }" if "re-check" in r.notes else "" }} | {{ money((r.unit_cost_usd|float) * (r.qty_per_robot|int)) }} | [{{ r.vendor }}]({{ r.vendor_url }}) |
{% endfor %}| | **Total** | **{{ bom_qty("actuators.csv") }}** | | **{{ bom_subtotal("actuators.csv") }}** | |

Part IDs (`ACT_*`) are assigned by this release. The source spreadsheet carries
no part numbers for bought parts, so these IDs are provisional
**UNVERIFIED**{ .dh-unverified } until the CAD and the assembly pages agree on a
scheme.

Rows with no usable price: {{ bom_unpriced("actuators.csv") }}.
Prices checked: {{ bom_priced_as_of("actuators.csv") }}.

### Per-row notes

{% for r in pd_read_csv("data/actuators.csv", dtype="str", keep_default_na=False).to_dict("records") if r.notes %}
- **`{{ r.part_id }}`** — {{ "**UNVERIFIED**{ .dh-unverified } " if "re-check" in r.notes else "" }}{{ "**TODO**{ .dh-missing } " if "no alternate published" in r.notes else "" }}{{ r.notes }}
{% endfor %}

## Which model goes in which joint

As-built joint-to-model map (deploy/control/humanoid_config.py): waist R03; hip_1, hip_2, hip_3 R03; knee R04; ankle_1 R03; ankle_2 R06; shoulder_1 R03; shoulder_2 R06; shoulder_3 R02; elbow R02; wrist_1 R02; wrist_2 R00; wrist_3 R05; cam_yaw/cam_pitch (4) R05 — 31 actuators.

The team design log's joint table gives the same model for every body joint it
fills in. It leaves wrist_3 blank and does not list the four camera joints.
*Source: team design log, "Joint Limits and Motors Torques".* Counted from the
map, per robot (computed): RS00 2, RS02 6, RS03 11, RS04 2, RS05 6, RS06 4,
which is the **Qty** column above, model for model. The same map, with CAN IDs
and buses, is on [CAN bus → The actuator map](../electrical/can-bus.md#the-actuator-map).

!!! unverified "UNVERIFIED — joint-to-model map not yet checked against the built robot"
    The map above comes from the control code, and the design log agrees with
    it for every body joint except wrist_3, which the log leaves blank. No check
    against the built robot is recorded, so wrist_3 (R05) and the four camera
    joints (R05) rest on the code alone. The `subassembly` column in
    `actuators.csv` still reads `actuators` on every row; name the limb there
    when the CSV is next generated.

    *Owner: hardware lead + controls lead.*

## Why these models

The selection trade study, the bench tests and the torque sizing behind these
six models are in [Design → Actuator selection](../design/actuator-selection.md)
and [Design → Actuator sizing in simulation](../design/actuator-sizing-simulation.md).
This page carries only the as-built data.

## Per-model data

### The team's motor spec

| Model | Rated torque (N·m) | Max torque (N·m) | 10 s overload torque (N·m) | Mass (kg) | Rated torque / mass (N·m/kg) | Rated power (W) | Torque constant (N·m/Arms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| RS00 | 5 | 14 | 12 | 0.31 | 16 | N/A | 1.48 |
| RS02 | 6 | 17 | 17 | 0.41 | 14 | 170 | 1.22 |
| RS03 | 20 | 60 | 55 | 0.88 | 23 | 380 | 2.36 |
| RS04 | 40 | 120 | 120 | 1.42 | 28 | 700 | 2.1 |
| RS05 | 1.6 | 5.5 | 4.1 | 0.192 | 8.3 | N/A | 0.94 |
| RS06 | 11 | 36 | 27 | 0.63 | 17 | 680 | 1.1 |

*Source: team design log, "Motor spec (robostride & more)".* These are
team-recorded values with no retrieval date. The max-torque and torque-constant
columns equal `MAX_TORQUE` and `MOTOR_TORQUE_CONSTANTS` in
`deploy/control/hardware_bindings/motor/py_motor.py`, model for model.

Two torque ratings appear in the team's records, and they are different
quantities, not a conflict. The **10 s overload** rating is the one the design
log's joint table uses: RS00 12, RS02 17, RS03 55, RS04 120 and RS06 27 N·m,
the same as the column above; RS05 is not in that joint table. The **max
torque** column is what the control code clamps to. Always say which rating a
figure is. *Source: team design log, "Joint Limits and Motors Torques".*

### Vendor data for the RS02, RS03 and RS04

Read from the RobStride product manuals filed in the team records (RobStride,
[robstride.com](https://www.robstride.com/download)). The manuals are cited,
not reproduced.

| | RS02 | RS03 | RS04 |
| --- | --- | --- | --- |
| Rated / operating voltage | 48 VDC / 24–60 VDC | 48 VDC / 24–60 VDC | 48 VDC / 24–60 VDC |
| Rated load | 6 N·m at 360 rpm | 20 N·m at 180 rpm | 40 N·m at 167 rpm |
| No-load speed | 410 rpm | 200 rpm | 200 rpm |
| Rated phase current | 7 Apk | 13 Apk | 27 Apk |
| Peak torque at maximum phase current | 17 N·m at 23 Apk | 60 N·m at 43 Apk | 120 N·m at 90 Apk |
| Torque constant | 1.22 N·m/Arms | 2.36 N·m/Arms | 2.1 N·m/Arms |
| Back-EMF | 0.096 Vrms/rpm | 17 Vrms/krpm | 16.9 Vrms/krpm |
| Reduction | 7.75:1 | 9:1 | 9:1 |
| Mass | 380 ±3 g | 880 ±20 g | 1420 ±20 g |
| Encoder | 14-bit single-turn absolute, 2 × AS5047P | 14-bit single-turn absolute, 2 × AS5047P | 14-bit single-turn absolute, 1 × AS5047P listed |
| CAN | 1 Mbps | 1 Mbps | 1 Mbps |

*Source: RobStride 02, 03 and 04 product manuals, specification sections.*

The RobStride 02, 03 and 04 manuals give a rated voltage of 48 VDC and an operating range of 24–60 VDC. The RS00, RS05 and RS06 manuals are not in the team records, so their range is **UNVERIFIED**{ .dh-unverified }.

The team's own records disagree with these manuals in three places, each
**UNVERIFIED**{ .dh-unverified } until checked against a unit:

- **Speed and reduction.** The team's selection sheet gives the RS02 100 rpm
  and a 7.76 reduction, and the RS04 150 rpm; the selection sheet and the
  design log give the RS03 160 rpm; the design log gives the RS04 100 rpm. The
  manuals give the figures in the table above.
- **RS04 encoder.** The selection sheet says "14 bit, dual"; the RS04 manual
  lists one AS5047P.
- **Current-limit units.** `py_motor.py` labels `MOTOR_CURRENT_LIMIT_DEFAULTS`
  as Arms; the RS03 manual gives the matching 43 A figure as Apk.

### Current-limit register 0x7018

The manuals give register `0x7018` (`limit_cur`, the current limit in speed and
position modes) a range that depends on the model: **RS02 0–23 A, RS03 0–43 A,
RS04 0–90 A**. The `0~23A` comment in `py_motor.py` matches the RS02 manual, and
the per-model defaults in the same file (R02 23.0, R03 43.0, R04 60.0 with the
inline comment `# 90`) are inside those ranges. *Source: RobStride 02, 03 and 04
product manuals, `0x7018` row; `py_motor.py`.* This settles the RS02, RS03 and
RS04 part of the discrepancy on
[Motor ID and config](../bringup/motor-id-and-config.md). The RS00, RS05 and
RS06 ranges are **UNVERIFIED**{ .dh-unverified }: their manuals are not in the
team records.

### Back-EMF

The back-EMF constants in `py_motor.py` are unit conversions of the manual
figures, and the code comments keep the originals: RS02 0.096 Vrms/rpm becomes
0.92 Vrms/(rad/s), RS03 17 Vrms/krpm becomes 0.16, RS04 16.9 Vrms/krpm becomes
0.16. The roughly tenfold spread between the RS02 and the RS03/RS04 is in the
vendor manuals as published, not a transcription error.
*Source: RobStride 02, 03 and 04 product manuals; `py_motor.py`
`MOTOR_BACK_EMF_CONSTANTS`.*

The manuals do not say whether their back-EMF figure is referred to rotor speed
or to output speed, so the spread between models may be a difference of basis
**UNVERIFIED**{ .dh-unverified }. That question, and the RS00, RS05 and RS06
figures, are tracked on [Power system](../electrical/power-system.md), whose
speed self-check divides by these constants.

### Measured masses

The team weighed its units during selection. The scale readings are above the
vendor figures.

| Model | With rear cover | Without rear cover | Rear cover alone | Vendor or team-spec figure |
| --- | ---: | ---: | ---: | --- |
| RS02 | 404 g | 396 g | 8 g | 380 ±3 g (manual) |
| RS03 | 909 g | 893 g | 14 g | 880 ±20 g (manual) |
| RS04 | 1496 g | 1439 g | 56.94 g | 1420 ±20 g (manual) |
| RS06 | 614 g | 599 g | 16 g | 0.63 kg (team motor spec; manual not in the records) |

*Source: team design log, actuator weighing photos; RobStride 02, 03 and 04
manuals.* Whether the readings include cable
pigtails is not recorded. The photos are on
[Design → Actuator selection](../design/actuator-selection.md).

### Still missing

!!! missing "MISSING — RS00, RS05 and RS06 vendor data, configured limits as run, and firmware"
    What is still missing after the tables above:

    - The RS00, RS05 and RS06 manuals: rated voltage and operating range,
      gear ratio, encoder, back-EMF basis and the `0x7018` range, with a
      retrieval date.
    - Configured per-joint current and torque limits as actually run on the
      reference robot.
    - Whether any unit ships needing a firmware update before first use, and
      the firmware version the reference robot runs.

    *Owner: hardware lead + controls lead.*

## Prices

Three undated team sources give three sets of prices, US$ per unit. None is
confirmed.

| Model | Team motor spec | Team selection sheet | `actuators.csv` (this site) |
| --- | ---: | ---: | ---: |
| RS00 | 135 **UNVERIFIED**{ .dh-unverified } | 125 **UNVERIFIED**{ .dh-unverified } | 125 **UNVERIFIED**{ .dh-unverified } |
| RS02 | 160 **UNVERIFIED**{ .dh-unverified } | 145 **UNVERIFIED**{ .dh-unverified } | 145 **UNVERIFIED**{ .dh-unverified } |
| RS03 | 250 **UNVERIFIED**{ .dh-unverified } | 265 **UNVERIFIED**{ .dh-unverified } | 225 **UNVERIFIED**{ .dh-unverified } |
| RS04 | 280 **UNVERIFIED**{ .dh-unverified } | 303 **UNVERIFIED**{ .dh-unverified } | 255 **UNVERIFIED**{ .dh-unverified } |
| RS05 | 120 **UNVERIFIED**{ .dh-unverified } | 110 **UNVERIFIED**{ .dh-unverified } | 110 **UNVERIFIED**{ .dh-unverified } |
| RS06 | 230 **UNVERIFIED**{ .dh-unverified } | not listed | 210 **UNVERIFIED**{ .dh-unverified } |

*Source: team design log, "Motor spec" and "motor selection" tables;
`docs/data/actuators.csv`.* The totals on this site are computed from the last
column. The low RS05 price is explained by size, not by an error: the RS05 is
the smallest RobStride in both team tables (1.6 N·m rated, 5.5 N·m max,
0.192 kg).

!!! unverified "UNVERIFIED — the per-model prices: three undated sources disagree"
    The team motor spec, the team selection sheet and `actuators.csv` agree on
    no model's price across all three, and none of them is dated. Re-check each
    price against the vendor, write the date into `priced_as_of`, and regenerate
    `actuators.csv` from the corrected source.

    *Owner: hardware lead.*

Two further servos — Feetech HL-3915-C001, 12 V, quantity 2 — are listed under
[Electronics](electronics.md) rather than here, which is where the source
spreadsheet puts them. Their role is not stated anywhere in the release
**UNVERIFIED**{ .dh-unverified }; the robot has four camera-gimbal axes, so two
servos do not cover them alone.

!!! unverified "UNVERIFIED — the role of the two Feetech servos"
    The paragraph above says the role of the two Feetech HL-3915-C001 servos is
    not stated anywhere in the release. Other pages of this site do state it:
    [Gripper](../assembly/gripper.md) and
    [Power system](../electrical/power-system.md) give one servo to each
    gripper, and [Head and camera gimbal](../assembly/head-and-camera-gimbal.md)
    says the four gimbal axes are RobStride actuators, not these servos. Confirm
    which is right, and correct the page that is wrong.

    *Owner: hardware lead.*

## Supply risk

The RobStride family is one of two items on this build with known supply risk.
A builder who cannot get one model cannot substitute freely: the mounting
interface, the shaft, and the CAN configuration all change.

The team compared other actuator families while choosing these models. Those
were selection candidates, not validated alternates: none was fitted to this
robot or tested in it. They are on
[Design → Actuator selection](../design/actuator-selection.md) and do not close
the box below.

!!! missing "MISSING — no alternate for any RobStride model"
    A named alternate for each model, or an explicit statement that no drop-in
    alternate exists and what a substitution would require in CAD changes. The
    `alt_mpn` and `alt_url` columns are blank on all
    {{ bom_count("actuators.csv") }} rows, and the column contract makes them
    mandatory here.
    *Owner: hardware lead. See [Sourcing](sourcing.md) and
    [Design → Actuator selection](../design/actuator-selection.md).*

## Incoming checks

What the team records establish for a unit on arrival is on
[Incoming inspection → Actuators](../fabrication/incoming-inspection.md#step-4-actuators):
the factory CAN ID seen on the team's bench units, the vendor tool and adapter
it needs, the encoder recalibration warning, and the measured masses above.

!!! missing "MISSING — acceptance criteria and run-in procedure for each actuator"
    What a good unit looks like, per model: expected firmware version, free
    rotation, encoder counts through a full turn, an accepted mass window, and
    any run-in procedure. Finding a bad unit after the leg is closed up costs a
    full disassembly.
    *Owner: hardware lead. See [Incoming inspection](../fabrication/incoming-inspection.md).*
