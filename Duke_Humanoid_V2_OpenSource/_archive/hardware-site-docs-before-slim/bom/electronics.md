# Electronics

Compute, power conversion, sensing and bus hardware — everything electrical that
is bought rather than made, {{ bom_subtotal("electronics.csv") }} across
{{ bom_count("electronics.csv") }} lines. The harness built from these parts is
documented separately under [Electrical](../electrical/index.md); the raw
cabling is on [Cables and connectors](cables-and-connectors.md).

## The list

Rendered from `docs/data/electronics.csv`.

| Part ID | Description | MPN | Qty | Unit cost | Line total | Vendor |
| --- | --- | --- | ---: | ---: | ---: | --- |
{% for r in pd_read_csv("data/electronics.csv", dtype="str", keep_default_na=False).to_dict("records") %}| `{{ r.part_id }}` | {{ r.description }}{{ " **UNVERIFIED**{ .dh-unverified }" if "read from the vendor link" in r.notes else "" }} | {{ r.mpn or "**TODO**{ .dh-missing }" }} | {{ r.qty_per_robot }} | {{ money(r.unit_cost_usd|float) }} | {{ money((r.unit_cost_usd|float) * (r.qty_per_robot|int)) }} | [{{ r.vendor }}]({{ r.vendor_url }}) |
{% endfor %}| | | | | **Total** | **{{ bom_subtotal("electronics.csv") }}** | |

Part IDs (`EL_*`) are assigned by this release; the source spreadsheet carries no
part numbers for bought parts. A **TODO**{ .dh-missing } in the **MPN** column
is a manufacturer part number the column contract requires and the source does
not record. Rows with no usable price:
{{ bom_unpriced("electronics.csv") }}. Prices checked:
{{ bom_priced_as_of("electronics.csv") }}.

### Per-row notes

{% for r in pd_read_csv("data/electronics.csv", dtype="str", keep_default_na=False).to_dict("records") if r.notes %}
- **`{{ r.part_id }}`** — {{ "**UNVERIFIED**{ .dh-unverified } " if ("read from the vendor link" in r.notes or "role of these two servos" in r.notes or "bus topology that needs six" in r.notes) else "" }}{{ "**TODO**{ .dh-missing } " if ("How many packs one robot needs" in r.notes or "no alternate published" in r.notes or "diodes are installed is not documented" in r.notes) else "" }}{{ r.notes }}
{% endfor %}

## Topology

Six CANable PRO V2.0 USB-to-CAN adapters, all at 1 Mbit/s: can9 = left arm (left_shoulder_2, left_shoulder_3, left_elbow, left_wrist_1, left_wrist_2, left_wrist_3); can21 = right arm (right_shoulder_2 to right_wrist_3); can22 = waist, left_shoulder_1, right_shoulder_1; can23 = right leg (right_hip_1–3, right_knee, right_ankle_1–2); can24 = left leg (left_hip_1–3, left_knee, left_ankle_1–2); can25 = cam_yaw_left, cam_pitch_left, cam_yaw_right, cam_pitch_right. The team data wiring diagram, deploy/control/humanoid_config.py and the CAN bus page agree.

That is why the list carries six adapters. Wiring detail is on
[CAN bus](../electrical/can-bus.md).

### Power distribution

Two Zeee 6S 10000 mAh LiPo packs are connected in series (one pack's + to the other's −) and feed a bus labelled 48V through a surge protector. Computed, not stated in the diagram: 2 × 22.2 V = 44.4 V nominal and 2 × 25.2 V = 50.4 V at full charge. *Source: team power wiring diagram (V2).*

A March 2025 single-leg-phase photo shows two packs of different brands, one labelled 5200 mAh. **UNVERIFIED**{ .dh-unverified } which packs the finished robot carries; the power diagram and the BOM both name the Zeee 6S 10000 mAh.

Power is split between two distribution-block pairs (power + ground). The lower-body pair feeds both legs and the waist (13 actuators, computed); the upper-body pair feeds both arms, both shoulder_1 joints and the four gaze motors (18 actuators, computed). TVS diodes sit across power and ground at each pair; the number fitted at each location is **UNVERIFIED**{ .dh-unverified } (the BOM carries 10 × M1.5KE62CA).

The only fuse drawn is a 10 A fuse on the onboard-computer branch: upper-body power distribution block → 10 A fuse → 48V-to-12V buck converter → MINISFORUM X1-470 mini PC. No pack-path fuse, e-stop, main disconnect, pre-charge circuit or pack monitoring is drawn, and the surge protector's part number is not identified. Neither the 10 A fuse nor the surge protector is in the BOM.

**UNVERIFIED**{ .dh-unverified } — converter conflict: the team power diagram draws one 48V-to-12V buck converter (computer branch only) and no 5 V rail; the BOM lists 2 × generic 48 V-to-12 V buck converters plus 1 × DC 20–60 V to 12 V encased buck converter; the design log proposed Delta isolated bricks (2 × V48SC12007NRFA, 12 V 7 A, and 1 × V36SE05010NRFA, 5 V 10 A), which appear only in Design as considered.

*Source for this section: team power wiring diagram (V2); team design log,
"Power".* What each converter in the BOM feeds is tracked on
[Power system](../electrical/power-system.md), which also shows the diagram;
the converters the team considered are on
[Design → Electronics and sensing](../design/electronics-and-sensing.md).

## Parts on the team diagrams that are not in this list

These parts are drawn on the team power diagram or named in the design log's
Power section, and none of them has a row in `electronics.csv`. Connectors and
cable are on [Cables and connectors](cables-and-connectors.md#parts-the-team-used-that-are-not-in-this-list).

| Item | Evidence | Status |
| --- | --- | --- |
| Surge protector | Drawn in the pack lead, before the 48V bus | Part not identified **TODO**{ .dh-missing } |
| 10 A fuse | Drawn on the onboard-computer branch only | Part not identified **TODO**{ .dh-missing } |
| Power distribution blocks, 4 | Two pairs (power + ground) drawn, upper and lower body. The design log links AliExpress item 3256806176225478, variant "Double row 8" | Quantity of 4 inferred from the diagram **UNVERIFIED**{ .dh-unverified }; whether this variant is fitted at every block **UNVERIFIED**{ .dh-unverified } |
| Battery charger | The design log links Amazon listing B09WKN863V; the listing slug says ISDT | Model **UNVERIFIED**{ .dh-unverified } |

*Source: team power wiring diagram (V2); team design log, "Power".*

!!! missing "MISSING — BOM rows for the parts drawn on the team power diagram"
    Add a row, with manufacturer part number, quantity and link, for the surge
    protector, the 10 A fuse (and its holder), the four power distribution
    terminal bars and the charger. Confirm the bar count and variant against
    the built robot, and name the charger model the lab uses.

    *Owner: electrical lead.*

## Purchase links that disagree with the design log

!!! unverified "UNVERIFIED — battery and CAN-adapter purchase links: BOM and design log disagree"
    - **Battery.** The design log's Power section links Amazon B0CS5RD74Y; the
      BOM row `EL_BATTERY_6S` links Amazon B0BHQX8XQX. Both may be the Zeee 6S
      10000 mAh; that is not confirmed.
    - **USB-to-CAN adapter.** The design log links Amazon B0CY9R7PBP; the BOM
      row `EL_CAN_ADAPTER` links the CANable PRO V2.0 at Amazon B0GJSRZLBV. The
      data wiring diagram labels all six adapters "CANable PRO V2.0", so the BOM
      link stands; the log's listing may be an earlier adapter.

    Confirm which listing each part on the reference robot came from.

    *Owner: electrical lead.*

## IMU

The SYD Dynamics TransducerM TM171 measures 40 × 34 × 12.6 mm. The design log
says "Mounting holes: M3", but the vendor drawing dimensions four flange holes
at Ø2.10 on 30 × 31 mm centres, which is too small for M3 clearance
**UNVERIFIED**{ .dh-unverified }. *Source: team design log, IMU section; SYD
Dynamics TM171 drawing,
[syd-dynamics.com/download-center](https://www.syd-dynamics.com/download-center/).*

!!! unverified "UNVERIFIED — IMU mounting fastener: M3 (design log) or Ø2.10 holes (vendor drawing)"
    Confirm which screw holds the IMU on the reference robot, and add it to the
    fastener schedule.

    *Owner: hardware lead.*

!!! unverified "UNVERIFIED — TVS diode part number and count per location"
    The source records only a distributor link for the TVS diode.
    [Power system](../electrical/power-system.md) names Microchip M1.5KE62CA,
    read from that link. Confirm the part on the robot, and how many of the ten
    sit at each distribution-block pair.

    *Owner: electrical lead.*

!!! missing "MISSING — computer configuration, camera firmware and bring-up peripherals"
    - Onboard computer configuration as actually used: RAM, storage, OS,
      and whether the stock power input is used or bypassed. The team design
      log and its mass budget name a Jetson; the BOM and the power diagram name
      the MINISFORUM X1-470 **UNVERIFIED**{ .dh-unverified }.
    - Camera firmware version the perception stack was validated against.
    - IMU mounting orientation and its frame relative to the robot base.
    - Whether a display, keyboard or network connection is needed at bring-up.

    *Owner: electrical lead.*

## Supply risk

The Intel RealSense D436 is the second of the two known supply-risk items on
this build. The RealSense product line has had repeated availability
discontinuities.

!!! missing "MISSING — no alternate depth camera for the RealSense D436"
    An alternate depth camera, with the consequences spelled out: mounting
    changes to the gimbal, field-of-view difference against the 90°×65° the
    workspace study assumes, and what breaks in the perception bridge. The
    `alt_mpn` and `alt_url` columns on `EL_CAM_D436` are blank, and the column
    contract makes them mandatory for this part.
    *Owner: hardware lead + perception lead. See [Sourcing](sourcing.md).*
