# Cables and connectors

The team BOM has one cable line. Connectors, wire, sleeving, heat-shrink and termination resistors are lab consumables: listed below without prices.

| Team ref | Part ID | Description | Qty | Unit cost | Line total | Vendor |
| --- | --- | --- | ---: | ---: | ---: | --- |
{% for r in pd_read_csv("data/cables-connectors.csv", dtype="str", keep_default_na=False).to_dict("records") %}| {{ team_ref_cell(r) }} | `{{ r.part_id }}` | {{ r.description }} | {{ r.qty_per_robot or "**TODO**{ .dh-missing }" }} | {{ money_cell(r.unit_cost_usd) }} | {{ line_total_cell(r) }} | [{{ r.vendor }}]({{ r.vendor_url }}) |
{% endfor %}| | | | | **Total** | **{{ bom_subtotal("cables-connectors.csv") }}** | |

## Consumables (not itemised)

Standard lab stock; buy to suit your build. Which connector and gauge goes where: [Harness fabrication](../electrical/index.md#harness-fabrication).

| Item | Use |
| --- | --- |
| Amass XT30 and XT30(2+2) connectors, male and female | Power branches; every actuator trunk |
| GH1.25 2-pin housings and cable contacts | CAN on RS03 / RS04 |
| EC5 connectors | Battery leads and the series link |
| Silicone wire, 12 / 16 / 18 AWG | Pack trunk, computer branch, motor branches |
| Ethernet cable | CAN leads: a twisted pair becomes CAN_H / CAN_L |
| Wire loom / sleeving, 1/4 in and 3/8 in | Limb runs |
| Heat-shrink, 3/32 in and 1/4 in | Connector wires; cable jackets |
| 120 Ω CAN termination resistors | Both ends of each bus |
| 10 A fuse and inline fuse holder | Computer branch, after the 48 V→12 V buck converter |
