# Electronics

Computer, battery, power conversion, Controller Area Network (CAN) and sensing:
{{ bom_subtotal("electronics.csv") }} across {{ bom_count("electronics.csv") }}
lines (MPN: manufacturer part number).

| Team ref | Part ID | Description | MPN | Qty | Unit cost | Line total | Vendor |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
{% for r in pd_read_csv("data/electronics.csv", dtype="str", keep_default_na=False).to_dict("records") %}{% set c = r["class"] == "consumable" %}| {{ team_ref_cell(r) }} | `{{ r.part_id }}` | {{ r.description }} | {{ r.mpn or ("—" if c else "**TODO**{ .dh-missing }") }} | {{ r.qty_per_robot or "**TODO**{ .dh-missing }" }} | {{ "—" if c else money_cell(r.unit_cost_usd) }} | {{ "—" if c else line_total_cell(r) }} | {{ "[" ~ r.vendor ~ "](" ~ r.vendor_url ~ ")" if r.vendor else ("—" if c else "**TODO**{ .dh-missing }") }} |
{% endfor %}| | | | | | **Total** | **{{ bom_subtotal("electronics.csv") }}** | |

Small connectors such as the USB-C adapter (`E21`) are lab consumables, not priced.
