# CNC parts

{{ bom_count("cnc-parts.csv") }} machined part rows,
{{ bom_subtotal("cnc-parts.csv") }} — the second largest cost after actuators
**UNVERIFIED**{ .dh-unverified } and the longest lead time in the build
**UNVERIFIED**{ .dh-unverified }. The first claim contradicts the subtotals on this
site; see [Which category costs the most](index.md#which-category-costs-the-most).
The second has no quoted lead time behind it; see
[Which item has the longest lead time](sourcing.md#which-item-has-the-longest-lead-time).
This page is the machined-part list; how to have them made and how to inspect
them on arrival are in
[CNC guide](../fabrication/cnc-guide.md) and
[Incoming inspection](../fabrication/incoming-inspection.md).

## How to read this page

The source spreadsheet's machined sheet has 63 rows. This page has
{{ bom_count("cnc-parts.csv") }}, because two of those rows are the same part
and one is not a robot part. Three things were changed on the way in, and each
one is recorded on the [BOM index](index.md#known-issues-with-this-bom):

- **The column named `UNIT COST` held line totals, not unit costs.** It is
  published here as **Line total**. A true **Unit cost** is derived from it by
  dividing by the quoted lot quantity, and is left blank **TODO**{ .dh-missing }
  on the three rows where that division is not exact to the cent.
- **Quantity is no longer part of the part ID.** The source IDs carry `_xN`
  *and* a separate quantity column, and the two disagree on 25 of 63 rows. The
  `_xN` is stripped; the source ID is preserved verbatim in each row's notes.
- **The single-leg test fixture was removed** from the machined subtotal and
  moved to `test-fixtures.csv`.

!!! unverified "The quantities on this page are lot sizes, not verified part counts"
    The **Qty** column is the quantity each price was quoted for. It is not a
    count checked against CAD, and on the rows flagged *qty conflict* it
    contradicts the part's own source name. Do not order from this column until
    the CAD cross-check in the MISSING box below is done. No quantity on this
    page is confirmed; the rows where the source also contradicts itself carry
    an extra red marker in the **Qty** cell.

**Flags**: *qty conflict* — the source part name and the source quantity column
disagree. *deduped* — the source sheet carries this part twice. *legacy ID* —
older numbering from the single-leg test rig, not yet reconciled
(**UNVERIFIED**{ .dh-unverified }). *B-series ID* —
a third scheme, origin unresolved (**UNVERIFIED**{ .dh-unverified }). *no unit cost* — the quoted lot price does not
divide evenly by the lot quantity.

**Red markers in the tables**: **UNVERIFIED**{ .dh-unverified } in **Qty** — the
quantity is contradicted by the part's own source name, or the row was
deduplicated. **TODO**{ .dh-missing } in **Unit cost** — no unit cost can be
derived. **UNVERIFIED**{ .dh-unverified } in **Flags** — a legacy or B-series row
that may be an old name for a current part, or a part the robot no longer uses.

## Leg

{{ bom_count("cnc-parts.csv", subassembly="leg") }} rows,
{{ bom_subtotal("cnc-parts.csv", subassembly="leg") }}.

| Part ID | Description | Qty | Unit cost | Line total | Flags |
| --- | --- | ---: | ---: | ---: | --- |
{% for r in pd_read_csv("data/cnc-parts.csv", dtype="str", keep_default_na=False).to_dict("records") if r.subassembly == "leg" %}| `{{ r.part_id }}` | {{ r.description }} | {{ r.qty_per_robot or "**TODO**{ .dh-missing }" }}{{ " **UNVERIFIED**{ .dh-unverified }" if ("QUANTITY CONFLICT" in r.notes or "DEDUPED" in r.notes) else "" }} | {{ money(r.unit_cost_usd|float) if r.unit_cost_usd else "**TODO**{ .dh-missing }" }} | {{ money(r.total_cost_usd|float) }} | {{ (("qty conflict; " if "QUANTITY CONFLICT" in r.notes else "") ~ ("deduped; " if "DEDUPED" in r.notes else "") ~ ("legacy ID; " if "Legacy numbering" in r.notes else "") ~ ("B-series ID; " if "B-series" in r.notes else "") ~ ("no unit cost; " if not r.unit_cost_usd else "")).rstrip("; ") or "—" }}{{ " **UNVERIFIED**{ .dh-unverified }" if ("Legacy numbering" in r.notes or "B-series" in r.notes) else "" }} |
{% endfor %}| | **Leg subtotal** | | | **{{ bom_subtotal("cnc-parts.csv", subassembly="leg") }}** | |

## Arm

{{ bom_count("cnc-parts.csv", subassembly="arm") }} rows,
{{ bom_subtotal("cnc-parts.csv", subassembly="arm") }}.

| Part ID | Description | Qty | Unit cost | Line total | Flags |
| --- | --- | ---: | ---: | ---: | --- |
{% for r in pd_read_csv("data/cnc-parts.csv", dtype="str", keep_default_na=False).to_dict("records") if r.subassembly == "arm" %}| `{{ r.part_id }}` | {{ r.description }} | {{ r.qty_per_robot or "**TODO**{ .dh-missing }" }}{{ " **UNVERIFIED**{ .dh-unverified }" if ("QUANTITY CONFLICT" in r.notes or "DEDUPED" in r.notes) else "" }} | {{ money(r.unit_cost_usd|float) if r.unit_cost_usd else "**TODO**{ .dh-missing }" }} | {{ money(r.total_cost_usd|float) }} | {{ (("qty conflict; " if "QUANTITY CONFLICT" in r.notes else "") ~ ("deduped; " if "DEDUPED" in r.notes else "") ~ ("legacy ID; " if "Legacy numbering" in r.notes else "") ~ ("B-series ID; " if "B-series" in r.notes else "") ~ ("no unit cost; " if not r.unit_cost_usd else "")).rstrip("; ") or "—" }}{{ " **UNVERIFIED**{ .dh-unverified }" if ("Legacy numbering" in r.notes or "B-series" in r.notes) else "" }} |
{% endfor %}| | **Arm subtotal** | | | **{{ bom_subtotal("cnc-parts.csv", subassembly="arm") }}** | |

## Body

{{ bom_count("cnc-parts.csv", subassembly="body") }} rows,
{{ bom_subtotal("cnc-parts.csv", subassembly="body") }}.

| Part ID | Description | Qty | Unit cost | Line total | Flags |
| --- | --- | ---: | ---: | ---: | --- |
{% for r in pd_read_csv("data/cnc-parts.csv", dtype="str", keep_default_na=False).to_dict("records") if r.subassembly == "body" %}| `{{ r.part_id }}` | {{ r.description }} | {{ r.qty_per_robot or "**TODO**{ .dh-missing }" }}{{ " **UNVERIFIED**{ .dh-unverified }" if ("QUANTITY CONFLICT" in r.notes or "DEDUPED" in r.notes) else "" }} | {{ money(r.unit_cost_usd|float) if r.unit_cost_usd else "**TODO**{ .dh-missing }" }} | {{ money(r.total_cost_usd|float) }} | {{ (("qty conflict; " if "QUANTITY CONFLICT" in r.notes else "") ~ ("deduped; " if "DEDUPED" in r.notes else "") ~ ("legacy ID; " if "Legacy numbering" in r.notes else "") ~ ("B-series ID; " if "B-series" in r.notes else "") ~ ("no unit cost; " if not r.unit_cost_usd else "")).rstrip("; ") or "—" }}{{ " **UNVERIFIED**{ .dh-unverified }" if ("Legacy numbering" in r.notes or "B-series" in r.notes) else "" }} |
{% endfor %}| | **Body subtotal** | | | **{{ bom_subtotal("cnc-parts.csv", subassembly="body") }}** | |

**Machined total: {{ bom_subtotal("cnc-parts.csv") }}.** Rows with no usable
price: {{ bom_unpriced("cnc-parts.csv") }}. Prices checked:
{{ bom_priced_as_of("cnc-parts.csv") }}.

## Excluded: the single-leg test fixture

`B6_single_leg_tester_plate`, {{ bom_subtotal("test-fixtures.csv") }}, is
development tooling for the single-leg test rig, not a robot part. It sits inside
the machined subtotal of the source spreadsheet. It is published here so the
exclusion is auditable, in `docs/data/test-fixtures.csv`, and it is not counted
anywhere on this site.

The team design log compared two single-leg test rigs, a linear rail with a
slider and a V1-style tether, and records no final choice. A March 2025 photo
shows a machined "slider mount", an angle bracket on top of the body frame.
Whether `B6_single_leg_tester_plate` is that slider mount is
**UNVERIFIED**{ .dh-unverified }. *Source: team design log, "slider"; single-leg
phase photos.* See [Design → Single-leg phase](../design/single-leg-phase.md).

## Full data

!!! missing "Blank columns in the full data are missing data, not empty fields"
    In the table below, `mpn`, `vendor`, `vendor_url`, `alt_mpn`, `alt_url`,
    `material`, `tolerance_finish`, `lead_time_days` and `priced_as_of` are blank
    on every row, and `unit_cost_usd` is blank on some. Each blank is a value
    that does not exist yet. They are tracked on
    [CNC guide](../fabrication/cnc-guide.md#the-data-every-machined-part-needs)
    (material, tolerance, finish), [Sourcing](sourcing.md#machining-vendors)
    (vendor) and [Sourcing](sourcing.md#which-item-has-the-longest-lead-time)
    (lead time).

??? note "All {{ bom_count("cnc-parts.csv") }} rows, every column, as published"

    {{ read_csv("data/cnc-parts.csv", dtype="str", keep_default_na=False, disable_numparse=True) | add_indentation(spaces=4) }}

## The team's CNC part list

The team design log carries its own machined-part list, separate from the
purchasing spreadsheet this page is generated from. It has **32 parts in one
ID scheme**, `CNC_<location><NN>_x<count>`: 18 leg, 10 arm and 4 body parts,
82 pieces per robot (46 leg, 28 arm, 8 body; computed). On every row the `_xN`
in the ID equals the count column, and the type column reads `CNC`. The list
has no material, finish, tolerance-value, vendor or price column; it does carry
the design-rule checks summarised on [CNC guide](../fabrication/cnc-guide.md#the-teams-design-rules).
*Source: team design log, "CNC Part List".*

### Where it disagrees with this page

The two lists agree on 18 IDs, name and count: `arm03`, `body01`–`body04`,
`leg01`, `leg03`–`leg08` and `leg13`–`leg18` (computed). Everywhere else they
differ, and **neither is confirmed against the CAD**. Both are stated; do not
order by ID until the owner settles them.

| ID | Team CNC part list | `cnc-parts.csv` (this site) | |
| --- | --- | --- | --- |
| `arm01` | `shoulder_roll_front_bearing_retainer` × 2 | shoulder roll front bearing, 2 | Name differs **UNVERIFIED**{ .dh-unverified } |
| `arm02` | `shoulder_roll_back_bearing_retainer` × 2 | shoulder roll back bearing, 2 | Name differs **UNVERIFIED**{ .dh-unverified } |
| `arm04` | `arm_support_shaft` × 4 | shoulder roll support shaft, 4 | Name differs **UNVERIFIED**{ .dh-unverified } |
| `arm05` | `RS02_back_cover` × 4 | RS02 shaft bearing, 4 | Different part **UNVERIFIED**{ .dh-unverified } |
| `arm06` | `RS02_shaft_bearing_retainer` × 4 | RS02 shaft coupler, 4 | Different part **UNVERIFIED**{ .dh-unverified } |
| `arm07` | `RS02_shaft_coupler` × 4 | elbow front bearing, 2 | Different part; 4 vs 2 **UNVERIFIED**{ .dh-unverified } |
| `arm08` | `elbow_front_bearing_retainer` × 2 | elbow back bearing, 2 | Different part **UNVERIFIED**{ .dh-unverified } |
| `arm09` | `elbow_back_bearing_retainer` × 2 | elbow output shaft, 2 | Different part **UNVERIFIED**{ .dh-unverified } |
| `arm10` | `elbow_output_shaft` × 2 | r03 back cover, 4 | Different part; 2 vs 4 **UNVERIFIED**{ .dh-unverified } |
| `arm11`–`arm13` | absent | wrist roll 2, wrist pitch 2, RS05 shaft coupler 3 | Not in the team list **UNVERIFIED**{ .dh-unverified } |
| `leg02` | `RS03_shaft_coupler` × 7 | RS03 shaft coupler, 8 (two quoted lots) | 7 vs 8 **UNVERIFIED**{ .dh-unverified } |
| `leg09` | `knee_back` × 2 | knee motor back cover, 2 | Name differs **UNVERIFIED**{ .dh-unverified } |
| `leg10` | `lower_leg_output_shank` × 2 | knee output shank, 2 | Name differs **UNVERIFIED**{ .dh-unverified } |
| `leg11` | `lower_leg_support_shank` × 2 | knee support shank, 2 | Name differs **UNVERIFIED**{ .dh-unverified } |
| `leg12` | `lower_leg_bearing_cap` × 4 | lower leg bearing, 5 | 4 vs 5 **UNVERIFIED**{ .dh-unverified } |
| 22 legacy and 4 B-series rows | absent | present | Not in the team list **UNVERIFIED**{ .dh-unverified } |

*Source: team design log, "CNC Part List"; `docs/data/cnc-parts.csv`.* From
`arm05` to `arm10` the two lists name the same parts shifted by one ID, which
is where the `arm07` and `arm10` quantity differences come from: the site list
has no RS02 back cover and the team list has no RS03 back cover. The team name
`lower_leg_bearing_cap` says what the site's "lower leg bearing" is: a cap. The
absence of the legacy and B-series rows from the team list supports, but does
not prove, that they are not current parts.

## Naming

### The team's labelling convention

The design log sets one part-ID order: kind of part, then body region with its
number tag, then count, then an optional description.

- **Kind:** `CNC` (CNC part), `ELEC` (electronic part, non-actuator), `MTR`
  (actuator or motor), `HWR` (hardware: nuts, screws, bearings, tape),
  `DIY` (made in house: 3D printing, moulding).
- **Region tag:** `legxx`, `armxx`, `bodyxx`, e.g. `leg01`, `arm01`, `body01`.
- **Count:** `xN`, e.g. `x1`, `x2`.
- **Side:** optional `L` or `R`.

The log's example is `CNC_leg02_x7` followed by the description
`RS03_shaft_coupler`. *Source: team design log, "Labeling Conventions".*

The convention is not consistent with itself, and this site departs from it,
both **UNVERIFIED**{ .dh-unverified } until the owner decides:

- The log's example text calls the RS03 shaft part "repeated 5 times in the
  leg" but gives it the ID `CNC_leg02_x7`. In the team list `leg02`
  `RS03_shaft_coupler` has count 7, and `leg03` `RS03_shaft_bearing_retainer`
  has count 5.
- This site assigns its own prefixes to bought parts (`EL_*`, `ACT_*`,
  `CBL_*`) instead of the team's `ELEC`, `MTR` and `HWR`, and drops the count
  from the part ID, which the team convention puts in it.

### The IDs on this page

Part IDs on this page still follow three different schemes, which is a
defect, not a convention:

- `CNC_leg01`…`CNC_leg18`, `CNC_arm01`…`CNC_arm13`, `CNC_body01`…`CNC_body04` —
  35 rows after deduplication, the team's scheme.
- `01_m03_shaft`, `08_hip_1_back_shaft` — 22 rows, an older scheme that appears
  to date from the single-leg test rig **UNVERIFIED**{ .dh-unverified }.
- `B1_body_base_plate` and similar — 4 rows. `B4` is absent from the source
  sheet entirely **TODO**{ .dh-missing }.

!!! missing "MISSING — reconcile this list with the team's 32-part list and the CAD; machining data for every row"
    - **Settle the `arm05`–`arm13` IDs and the `leg02` and `leg12` counts**
      against the CAD, using the comparison table above, and adopt one
      part-ID scheme that matches the CAD filenames and the assembly steps.
    - **Resolve the 22 legacy rows and the 4 B-series rows**, which the team's
      32-part list does not contain: which are current parts under an old name,
      and which are test-rig leftovers to delete; and whether the absent `B4`
      is a part missing from this list. Until this is done the machined
      subtotal may be counting parts twice under two names, or counting parts
      the robot no longer uses.
    - **Verify every quantity against CAD.** 25 of 63 source rows disagree with
      the count embedded in their own part name.
    - **Add material, tolerance, surface finish and supplier** to every row.
      Neither list has any of the four per part, and no machine shop can quote
      from a part name alone.
    - State which parts are turned rather than milled, and which need more than
      3 axes. Every row is marked `CNC`, which is a group label in both lists,
      not a per-part process.

    *Owner: hardware lead, from the CAD and the machining quotations.*

The team list has `CNC_leg02_x7_RS03_shaft_coupler` once, as one part with
count 7, which supports merging the two source rows into one part.
*Source: team design log, "CNC Part List".* The count is still open:

!!! unverified "UNVERIFIED — RS03 shaft coupler per robot: 7 (team list) or 8 (quoted lots)"
    The team's part list gives `CNC_leg02` `RS03_shaft_coupler` a count of 7;
    the two quoted lots merged into `CNC_leg02_RS03_shaft_coupler` on this page
    total 8. Count the couplers in the CAD.

    *Owner: hardware lead, from the CAD and the machining quotations.*
