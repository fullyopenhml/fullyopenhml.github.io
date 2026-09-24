# Printed parts

The additively manufactured parts: FDM and SLS. In the source spreadsheet these
are three bare material rows with no cost, no quantity, no printer and no
supplier — so this page is currently structure and a list of what is missing.

## What the parts list actually contains

Rendered from `docs/data/printed-parts.csv`.

| Part ID | Description | Material | Process | Qty | Unit cost | Vendor |
| --- | --- | --- | --- | ---: | ---: | --- |
{% for r in pd_read_csv("data/printed-parts.csv", dtype="str", keep_default_na=False).to_dict("records") %}| `{{ r.part_id }}` | {{ r.description }} | {{ r.material or "**TODO**{ .dh-missing }" }} | {{ r.process or "**TODO**{ .dh-missing }" }} | {{ r.qty_per_robot or "**TODO**{ .dh-missing }" }} | {{ money(r.unit_cost_usd|float) if r.unit_cost_usd else "**TODO**{ .dh-missing }" }} | {{ r.vendor or "**TODO**{ .dh-missing }" }} |
{% endfor %}
Subtotal: {{ bom_subtotal("printed-parts.csv") }}. Rows with no usable price:
{{ bom_unpriced("printed-parts.csv") }} — that is every row.

These are **materials, not parts**. Not one printed part of this robot is named
anywhere in the release. The rows are carried here rather than dropped so that
the gap is visible in the data, not only in prose.

### Per-row notes

{% for r in pd_read_csv("data/printed-parts.csv", dtype="str", keep_default_na=False).to_dict("records") if r.notes %}
- **`{{ r.part_id }}`** — {{ "**TODO**{ .dh-missing } " if ("No cost" in r.notes or "not recorded" in r.notes) else "" }}{{ r.notes }}
{% endfor %}

## Candidates, not a list

Two team sources hint at which parts are printed. Neither is a parts list, and
every item below is **UNVERIFIED**{ .dh-unverified } until the owner confirms
it against the CAD.

- **From the team CAD animations.** Parts rendered black that have no row in
  `cnc-parts.csv`: the arm's conical upper-arm and forearm shells and a black
  square block; the camera gimbal's pedestal, neck and two L-shaped arms; the
  torso's central spine; and the front and back cover frames and panels.
  Colour in the animations is a render appearance, not a material code, so
  this is a shortlist to check, nothing more. *Source: team CAD animations,
  compared with `docs/data/cnc-parts.csv`.*
- **From the single-leg phase photos (March 2025).** Printed battery holders
  with heat-set inserts, a printed X-shaped IMU bracket and printed T-brackets
  holding the computer. Whether these parts are in the finished robot is not
  recorded. The photos are on
  [Design → Single-leg phase](../design/single-leg-phase.md).

!!! missing "MISSING — SAFETY — no list of printed parts"
    - **Which parts are printed.** A row per printed part with a part ID that
      matches the CAD file and the assembly step pages, not a material heading.
      Until this exists the robot cannot be built, because no one knows what to
      print.
    - Which of them are FDM and which are SLS, and whether the SLS parts can be
      substituted with FDM. The source sheet names SLS only through the powder
      row; it does not say FDM anywhere, so the process column is blank on the
      two filament rows rather than assumed.
    - Material grade per part: plain PLA or a filled grade such as PLA-CF, TPU
      shore hardness, PA11 or PA12 for the SLS parts.
    - Cost, priced by filament and powder consumed rather than per part, so the
      printed tier can enter the [cost summary](index.md#cost-summary).
    - A vendor and a link per material, and a service bureau for the SLS parts if
      they are not printed in house.
    - Which printed parts are structural and therefore must not be substituted
      in a weaker material.
    *Owner: hardware lead. See [Printing guide](../fabrication/printing-guide.md).*

## Print profiles

{{ "**TODO**{ .dh-missing } `print_profiles.csv` does not exist yet, so there are no print profiles to render." if not data_file_exists("print_profiles.csv") else "" }}

!!! missing "MISSING — a print profile for every printed part"
    A `docs/data/print_profiles.csv` entry per printed part: layer height, wall
    count, infill, orientation on the plate, supports, and the exact printer the
    profile was validated on. Written as numbers in a table, not as slicer
    screenshots — screenshots cannot be diffed, searched or re-used on a
    different printer.
    *Owner: hardware lead. Column contract is in `docs/data/README.md`.*
