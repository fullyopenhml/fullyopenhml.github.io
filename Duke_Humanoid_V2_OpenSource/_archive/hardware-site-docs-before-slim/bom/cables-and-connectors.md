# Cables and connectors

The raw material for the harness — {{ bom_subtotal("cables-connectors.csv") }}
across {{ bom_count("cables-connectors.csv") }} lines. How the harness is built
from it is in [Harness fabrication](../electrical/harness-fabrication.md); how it
is routed through the machine is in [Routing](../electrical/routing.md).

## The list

Rendered from `docs/data/cables-connectors.csv`.

| Part ID | Description | Qty | Unit cost | Line total | Vendor |
| --- | --- | ---: | ---: | ---: | --- |
{% for r in pd_read_csv("data/cables-connectors.csv", dtype="str", keep_default_na=False).to_dict("records") %}| `{{ r.part_id }}` | {{ r.description }}{{ " **UNVERIFIED**{ .dh-unverified }" if "confirm the length" in r.notes else "" }} | {{ r.qty_per_robot }} | {{ money(r.unit_cost_usd|float) }} | {{ money((r.unit_cost_usd|float) * (r.qty_per_robot|int)) }} | [{{ r.vendor }}]({{ r.vendor_url }}) |
{% endfor %}| | | | **Total** | **{{ bom_subtotal("cables-connectors.csv") }}** | |

Part IDs (`CBL_*`) are assigned by this release. Rows with no usable price:
{{ bom_unpriced("cables-connectors.csv") }}. Prices checked:
{{ bom_priced_as_of("cables-connectors.csv") }}.

### Per-row notes

{% for r in pd_read_csv("data/cables-connectors.csv", dtype="str", keep_default_na=False).to_dict("records") if r.notes %}
- **`{{ r.part_id }}`** — {{ "**UNVERIFIED**{ .dh-unverified } " if "confirm the length" in r.notes else "" }}{{ r.notes }}
{% endfor %}

!!! missing "There is no wire in this list"
    Every line above is a connector, a sleeve or a finished USB cable. Not one
    metre of bulk wire appears anywhere in the source spreadsheet, and neither
    does a single crimp terminal, ferrule or CAN termination resistor. A builder
    cannot fabricate the harness from this page as it stands. Each gap is
    itemised in the boxes below.

## Actuator-side connectors

The RobStride manuals give two different connector arrangements. They are
cited here, not reproduced.

| Model (units per robot) | Power | CAN |
| --- | --- | --- |
| RS02 (6) | One Amass XT30(2+2) shell carries power and CAN: board side XT30PB(2+2)-M.G.B, cable side XT30(2+2)-F.G.B. Pins 1 = power +, 2 = power −, 3 = CAN_L, 4 = CAN_H | In the same XT30(2+2) shell |
| RS03 (11), RS04 (2) | Amass XT30: board side XT30APW-M, cable side XT30UW-F | Separate GH1.25 2-pin: board side GH1.25-2PWT, cable side GH1.25-T |
| RS00, RS05, RS06 | Manuals not in the team records **UNVERIFIED**{ .dh-unverified } | **UNVERIFIED**{ .dh-unverified } |

*Source: RobStride 02 manual, driver interface; RobStride 03 and 04 manuals,
§2.2.2; units per robot from the joint-to-model map on
[Actuators](actuators.md#which-model-goes-in-which-joint).* The RS04 manual
gives the lead colours as blue CAN_H, brown CAN_L, black GND and red VBAT+; the
team's photos show a blue/yellow CAN pair. Team photos of an opened RS03 show
two XT30 sockets and two small 2-pin sockets on the driver board, an in and an
out for daisy-chaining. No GH1.25 part is in this list.

!!! unverified "UNVERIFIED — trunk-harness connector: XT30(2+2) on every actuator, or XT30 plus GH1.25"
    [Harness fabrication](../electrical/harness-fabrication.md) and
    [CAN bus](../electrical/can-bus.md) say motor power and CAN share an
    XT30(2+2) shell on every actuator. The manuals agree for the RS02 only; the
    RS03 and RS04 have a separate XT30 and a GH1.25 2-pin connector. The trunk
    harness may still use XT30(2+2) with adapters at the RS03 and RS04; that is
    not recorded. Confirm on the built robot which connector each run uses, the
    CAN colour convention, and the pin that carries CAN_H.

    *Owner: electrical lead.*

The XT30(2+2)-F.G.B datasheet rates the connector at 15 A with 18 AWG wire,
30 A for one minute below 80 °C, 500 V DC withstand and 100 mating cycles, and
says not to mate or unmate it under power. These are ratings of the connector,
not the wire gauge this robot uses. *Source: Amass XT30(2+2)-F.G.B datasheet, LCSC part C19268028.*

## Wire gauge

The team power diagram labels 12 AWG on the pack-to-lower-body power run and 16 AWG on the 12 V run from the buck converter to the computer. No other run is labelled; the gauge of the 48V riser, the ground returns and the motor branches is still missing.

*Source: team power wiring diagram (V2).*

!!! missing "MISSING — SAFETY — wire gauge of the 48V riser, the ground returns and the motor branches"
    **Wire gauge per run** for every run the diagram leaves unlabelled: the
    48V riser to the upper body, the ground returns, and the branches from each
    distribution block to the actuators, plus the CAN signal wire. A builder
    cannot guess it on a bus that carries 31 actuators. Getting this wrong is a
    fire, not a defect.

    *Owner: electrical lead.*

## Parts the team used that are not in this list

| Item | Evidence | Status |
| --- | --- | --- |
| EC5 battery connectors | The design log names EC5 "to connect from the battery" (example purchase: Amazon B073ZG47H3). The power diagram draws unlabelled blue connector pairs at both pack leads and at the series link | Not in the BOM. That the drawn connectors are EC5 is **UNVERIFIED**{ .dh-unverified } |
| Ethernet cable | The design log's CAN cable procedure builds CAN leads from Ethernet cable, twisting its pairs into a CAN High and a CAN Low bundle | Not in the BOM. Which runs use it is **UNVERIFIED**{ .dh-unverified } |
| Heat-shrink | The same procedure uses 3/32 in heat-shrink on the connector wires and 1/4 in heat-shrink over the cable | Not in the BOM; quantity per cable only |
| Two unidentified parts | The design log's "electronics misc parts" lists Amazon B0774VBJ3J and a 200-piece connector-housing kit (Amazon B0BHZTQ1WV), with no role | Not identified **UNVERIFIED**{ .dh-unverified } |

*Source: team design log, "Power" and the CAN cable procedure; team power
wiring diagram (V2).* The procedure records yellow = CAN High and
blue = CAN Low. Power distribution blocks, the fuse and the charger are on
[Electronics](electronics.md#parts-on-the-team-diagrams-that-are-not-in-this-list).

!!! missing "MISSING — BOM rows for EC5 connectors, Ethernet cable and heat-shrink"
    Add rows, with quantity and link, for the battery connectors, the Ethernet
    cable used for CAN leads and both heat-shrink sizes. Confirm that the blue
    connectors on the power diagram are EC5, and which CAN runs use the
    Ethernet cable.

    *Owner: electrical lead.*

!!! unverified "UNVERIFIED — two unidentified parts in the design log's misc list"
    Amazon B0774VBJ3J and the connector-housing kit Amazon B0BHZTQ1WV are each
    listed twice in the design log with no description or role. Confirm what
    they are and whether they are on the robot before either gets a BOM row.

    *Owner: electrical lead.*

!!! missing "MISSING — bulk wire, CAN wiring, crimps, pinouts and cable lengths"
    - **Bulk wire**, by gauge, insulation rating and colour, with quantity.
    - **CAN wiring**: shielding and termination resistors. The team procedure
      uses Ethernet-cable pairs; no termination resistor appears anywhere in
      the parts list.
    - Crimp terminals and ferrules, with the matching housings, including the
      GH1.25 cable-side housings the RS03 and RS04 need.
    - Connector pinout for every custom-made cable.
    - Cable lengths per run, so a builder can cut before installing.
    - Crimp tooling required, listed in [Tools](../assembly/tools.md).
    - Strain relief and service loops at each joint that moves.

    *Owner: electrical lead.*

!!! unverified "UNVERIFIED — length of the 1/4 inch wire loom: 25 ft or 10 ft"
    Confirm the sleeving lengths: one line is described as 25 ft but its vendor
    link reads 10 ft. Check the listing, or measure the delivered loom, and
    correct the description or the link.

    *Owner: electrical lead.*
