# Part index

Part ID to page, in both directions. Given a part in your hand, find the step it
belongs to. Given a step, find the part and where to buy or make it.

## Why this page exists

A part ID is the join key of the whole release. The same string has to appear in
four places and mean the same thing in all of them:

| Where the ID appears | What it is for |
| --- | --- |
| The CAD filename | So the STEP you send to the shop is the part the BOM priced |
| A row in a BOM CSV under `docs/data/` | So the part has a price, a material and a lead time |
| The *Parts needed* table at the top of an assembly step | So a builder can count out a step's hardware before starting it |
| This index | So a part found loose on the bench can be traced back to its step |

If those four drift apart, every other page on this site quietly becomes wrong.
That is why the data contract forbids encoding quantity in a part ID and forbids
duplicate IDs — both rules exist because the source spreadsheet broke them.

## Rules for a part ID

- **Stable.** An ID is never reused for a different part, and never renamed
  without a revision note.
- **No quantity inside the ID.** `..._x4` in a name is how 25 of 63 machined rows
  ended up with a quantity column that contradicts their own name.
- **Unique.** One row, one ID. The legacy sheet has one coupler ID appearing
  twice with different prices and different quantities.
- **Matches the CAD filename**, character for character.
- **Namespaced by subassembly**, so the ID says where the part lives.

## The index

!!! missing "MISSING — The part index, blocked on settling part numbering"
    This index cannot be generated until part numbering is settled. Three naming
    schemes currently coexist in the machined-part list — a `CNC_leg01` family, an
    older `01_m03_shaft` family, and a `B1_body_base_plate` family — and the last
    two appear to be leftovers from a single-leg test rig rather than parts of
    this robot. Settling that is a human judgement call on each row, not a
    rename. See [CNC parts](../bom/cnc-parts.md).

    Once numbering is settled, **this page should be generated, not written**: a
    script reads the BOM CSVs and the assembly pages and emits the table, so that
    a renamed part cannot leave a stale entry behind. A hand-maintained index on a
    600-part machine **UNVERIFIED**{ .dh-unverified } (no part count exists: the
    fastener schedule is one placeholder row) is wrong within a month.

    The generated table's shape:

    | Part ID | Description | Qty | Subassembly | Where it is used |
    | --- | --- | --- | --- | --- |
    | *`part_id` from the CSV* | *`description`* | *`qty_per_robot`* | *page in the BOM* | *every assembly step that names it* |

    *Owner: hardware lead for the numbering, then whoever writes the generator.*

## The team's own CNC part list and labelling convention

The team kept its own list of machined parts and a labelling convention for the
full humanoid. Both are recorded here because a builder will meet these IDs on
parts, in photos and in the CAD, and they do not match this site's IDs.

**Labelling convention.** Kind of part, then body region with its number tag,
then count, then an optional description:

| Element | Values |
| --- | --- |
| Kind prefix | `CNC` (CNC part), `ELEC` (electronic part, not an actuator), `MTR` (actuator or motor), `HWR` (hardware: nuts, screws, bearings, tape and so on), `DIY` (made in-house: 3D printing, moulding and so on) |
| Region tag | `legxx`, `armxx`, `bodyxx` (for example `leg01`, `arm01`, `body01`) |
| Count | `xN` (for example `x1`, `x2`) |
| Side | optional `L` or `R` |

The team's example is `CNC_leg02_x7`, described as `RS03_shaft_coupler`. Note
that this convention puts the quantity inside the ID, which this site's rules
above forbid.

**The team's CNC part list** has 32 machined parts in this one scheme:
`CNC_arm01`–`arm10` (10 rows), `CNC_body01`–`body04` (4 rows) and
`CNC_leg01`–`leg18` (18 rows). The counts sum to 82 pieces: arm 28, body 8,
leg 46 (computed). This site's `cnc-parts.csv` has 63 rows, so the two lists do
not correspond one to one.

*Source: team design log, "Labeling Conventions" and "CNC Part List".*

!!! unverified "UNVERIFIED — CNC IDs arm05–arm10 and four quantities disagree between the team list and this site"
    The same IDs point to different parts:

    | ID | Team CNC part list | This site's `cnc-parts.csv` |
    | --- | --- | --- |
    | arm05 | RS02_back_cover ×4 | RS02_shaft_bearing ×4 |
    | arm06 | RS02_shaft_bearing_retainer ×4 | RS02_shaft_coupler ×4 |
    | arm07 | RS02_shaft_coupler ×4 | elbow_front_bearing ×2 |
    | arm08 | elbow_front_bearing_retainer ×2 | elbow_back_bearing ×2 |
    | arm09 | elbow_back_bearing_retainer ×2 | elbow_output_shaft ×2 |
    | arm10 | elbow_output_shaft ×2 | r03_back_cover ×4 |

    This site's arm11 (wrist_roll), arm12 (wrist_pitch) and arm13
    (RS05_shaft_coupler) do not exist in the team list. Quantities also
    differ: leg02 7 (team) vs 8 (site), leg12 4 vs 5, arm07 4 vs 2, arm10 2 vs 4.
    Neither source is chosen here. Confirm each row against the CAD before
    ordering.

    *Owner: hardware lead. See [CNC parts](../bom/cnc-parts.md).*

## Meanwhile

Until this index exists, use the search box at the top of the page. It covers
every page on this site, including the parts tables inside assembly steps.
