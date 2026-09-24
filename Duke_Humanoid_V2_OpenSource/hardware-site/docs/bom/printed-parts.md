# Printed parts

One row per printed part; **Team ref** is the team BOM line. Material and process are what the reference robot was printed with. Print settings and files: [Printing guide](../fabrication/index.md#printing-guide), [CAD downloads](../fabrication/index.md#cad-downloads).

| Team ref | Part ID | Description | Material | Process | Qty |
| --- | --- | --- | --- | --- | ---: |
{% for r in pd_read_csv("data/printed-parts.csv", dtype="str", keep_default_na=False).to_dict("records") if not r.part_id.startswith("MAT_") %}| {{ team_ref_cell(r) }} | `{{ r.part_id }}` | {{ r.description }} | {{ r.material or "**TODO**{ .dh-missing }" }} | {{ r.process or "**TODO**{ .dh-missing }" }} | {{ r.qty_per_robot or "**TODO**{ .dh-missing }" }} |
{% endfor %}| | | **Printed total** | | | **{{ bom_qty("printed-parts.csv") }}** |

Materials — PLA and TPU filament, nylon 12 SLS powder — are lab consumables, not itemised.
