# Actuators

Every joint is a RobStride quasi-direct-drive actuator:
{{ bom_qty("actuators.csv") }} units, {{ bom_count("actuators.csv") }} models,
{{ bom_subtotal("actuators.csv") }}.

| Team ref | Model | Part ID | Qty | Unit cost | Line total | Vendor |
| --- | --- | --- | ---: | ---: | ---: | --- |
{% for r in pd_read_csv("data/actuators.csv", dtype="str", keep_default_na=False).to_dict("records") %}| {{ team_ref_cell(r) }} | {{ r.mpn }} | `{{ r.part_id }}` | {{ r.qty_per_robot or "**TODO**{ .dh-missing }" }} | {{ money_cell(r.unit_cost_usd) }} | {{ line_total_cell(r) }} | [{{ r.vendor }}]({{ r.vendor_url }}) |
{% endfor %}| | **Total** | | **{{ bom_qty("actuators.csv") }}** | | **{{ bom_subtotal("actuators.csv") }}** | |

## Which model goes in which joint

| Model | Qty | Joints (both sides unless noted) |
| --- | ---: | --- |
| RS00 | 2 | wrist_2 |
| RS02 | 6 | shoulder_3, elbow, wrist_1 |
| RS03 | 11 | waist (1), hip_1, hip_2, hip_3, ankle_1, shoulder_1 |
| RS04 | 2 | knee |
| RS05 | 6 | wrist_3; cam_yaw and cam_pitch on both camera gimbals |
| RS06 | 4 | ankle_2, shoulder_2 |
