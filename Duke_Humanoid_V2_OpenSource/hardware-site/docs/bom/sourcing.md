# Sourcing

Order these first — long lead time or supply risk, and no drop-in substitute:

| Item | Why |
| --- | --- |
| {{ bom_count("cnc-parts.csv") }} machined parts, {{ bom_subtotal("cnc-parts.csv") }} | Large custom order ([CNC guide](../fabrication/index.md#cnc-guide)) |
| RobStride actuators, {{ bom_qty("actuators.csv") }} units, {{ bom_subtotal("actuators.csv") }} | Supply risk |
| Intel RealSense D436 ×2 | Supply risk |

## Vendors

{% set bought = pd_read_csv("data/actuators.csv", dtype="str", keep_default_na=False).to_dict("records") + pd_read_csv("data/electronics.csv", dtype="str", keep_default_na=False).to_dict("records") + pd_read_csv("data/cables-connectors.csv", dtype="str", keep_default_na=False).to_dict("records") + pd_read_csv("data/fasteners.csv", dtype="str", keep_default_na=False).to_dict("records") %}
| Vendor | Lines | Part IDs |
| --- | ---: | --- |
{% for vendor, items in bought | selectattr("vendor") | groupby("vendor") %}| {{ vendor }} | {{ items | length }} | {{ items | map(attribute="part_id") | join(", ") }} |
{% endfor %}
