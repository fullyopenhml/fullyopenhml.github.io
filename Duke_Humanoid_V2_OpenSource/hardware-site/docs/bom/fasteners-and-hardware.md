# Fasteners and hardware

{{ bom_count("fasteners.csv") }} hardware lines — six bearing sizes and three Torx button-head screw sizes — totalling {{ bom_subtotal("fasteners.csv") }}. Screw lines are McMaster-Carr packs, not pieces on the robot.

| Team ref | Part ID | Description | Qty | Unit cost | Line total | Vendor |
| --- | --- | --- | ---: | ---: | ---: | --- |
{% for r in pd_read_csv("data/fasteners.csv", dtype="str", keep_default_na=False).to_dict("records") %}| {{ team_ref_cell(r) }} | `{{ r.part_id }}` | {{ r.description }} | {{ r.qty_per_robot or "**TODO**{ .dh-missing }" }} | {{ money_cell(r.unit_cost_usd) }} | {{ line_total_cell(r) }} | {{ "[" ~ r.vendor ~ "](" ~ r.vendor_url ~ ")" if r.vendor else "**TODO**{ .dh-missing }" }} |
{% endfor %}| | | **Total** | | | **{{ bom_subtotal("fasteners.csv") }}** | |

Threadlocker (Loctite 222) is a lab consumable, not itemised.
