# Bill of materials

Everything that goes into one robot, split the way the three procurement paths
actually differ: parts you buy, parts you have machined, and parts you print.
Each page below is one of those paths, or one cross-cutting category.

Every figure on these pages is computed from a CSV in `docs/data/` by the site's
macros. None of them is typed into prose, so a re-sourced part changes the total
everywhere at once. Where a CSV has no usable price, the figure reads
*not yet published* rather than a guess.

<div class="grid cards" markdown>

- **[Actuators](actuators.md)** — {{ bom_qty("actuators.csv") }} quasi-direct-drive units, the single largest line **UNVERIFIED**{ .dh-unverified } — see [the note below the cost summary](#which-category-costs-the-most).
- **[Electronics](electronics.md)** — compute, power conversion, CAN, IMU, cameras.
- **[CNC parts](cnc-parts.md)** — {{ bom_count("cnc-parts.csv") }} machined part rows.
- **[Printed parts](printed-parts.md)** — FDM and SLS, not yet costed **TODO**{ .dh-missing }.
- **[Fasteners and hardware](fasteners-and-hardware.md)** — one placeholder row, unpriced **TODO**{ .dh-missing }.
- **[Cables and connectors](cables-and-connectors.md)** — harness raw material.
- **[Sourcing](sourcing.md)** — vendors, lead times, alternates.

</div>

## Cost summary

Tiered the way a builder spends money: what the robot itself costs, what you
additionally need to own to build it, and what is optional. Read the exclusions
below the table before quoting any of these figures — the robot tier is
**incomplete**, and the size of the hole is not known **TODO**{ .dh-missing }.

| Tier | | Subtotal |
| --- | --- | --- |
| **Robot** | Actuators — {{ bom_qty("actuators.csv") }} units, {{ bom_count("actuators.csv") }} models | {{ bom_subtotal("actuators.csv") }} |
| | Electronics — compute, power, CAN, sensing | {{ bom_subtotal("electronics.csv") }} |
| | Machined parts — {{ bom_count("cnc-parts.csv") }} rows; quantities are quoted lots, not CAD counts **UNVERIFIED**{ .dh-unverified } | {{ bom_subtotal("cnc-parts.csv") }} |
| | Cables and connectors | {{ bom_subtotal("cables-connectors.csv") }} |
| | Fasteners, bearings, hardware | {{ bom_subtotal("fasteners.csv") }} |
| | Printed parts — filament and SLS powder | {{ bom_subtotal("printed-parts.csv") }} |
| | **Robot subtotal, as far as it is costed** | **{{ bom_total() }}** |
| **Tools** | Tools a builder must own | {{ bom_subtotal("tools.csv") }} |
| **Optional** | Third camera module, spares, upgrades | {{ bom_subtotal("optional.csv") }} |
| *Excluded* | *Single-leg test fixture — development tooling, not a robot part* | *{{ bom_subtotal("test-fixtures.csv") }}* |

!!! missing "What the robot subtotal does not include"

    The figure above is a **floor, not an estimate**. It is missing whole
    categories, not rounding:

    - **Every fastener, bearing, dowel pin and threadlocker.** The source
      spreadsheet has one unpriced placeholder row for all of it. See
      [Fasteners and hardware](fasteners-and-hardware.md).
    - **Every printed part.** Three bare material rows, no cost, no quantity.
      See [Printed parts](printed-parts.md).
    - **Bulk wire.** Only connectors and sleeving are in the parts list; not one
      metre of wire. See [Cables and connectors](cables-and-connectors.md).
    - **The gripper and the camera gimbal as modules.** Neither is separable in
      the source data, so neither can be quoted on its own — and the camera
      gimbal is the paper's entire contribution.
    - **Tools, shipping, duty, tax, scrap and re-machining.** None of these is
      in any source file.
    - **Labour.** See [Cost and time](../before-you-start/cost-and-time.md).

    There is also no date on any price: the source spreadsheet records none.
    See [Price dates](sourcing.md#price-dates).

    Each category above is tracked where it lives: the linked BOM pages, and
    [Cost and time](../before-you-start/cost-and-time.md) for tools, shipping,
    duty and labour. The one exclusion tracked nowhere else is boxed next.

!!! missing "MISSING — allowance for tax, scrap and re-machining"
    The robot subtotal carries no allowance for tax, for scrapped parts, or for
    re-machining a part that arrives out of tolerance. None of these is in any
    source file, and no other page tracks them.

    *Owner: hardware lead.*

### Which category costs the most

!!! unverified "UNVERIFIED — whether actuators or machined parts are the largest cost"
    Four pages call the actuators the largest cost: this page ("the single
    largest line"), [Actuators](actuators.md), [CNC parts](cnc-parts.md) ("the
    second largest cost after actuators") and [Sourcing](sourcing.md) ("the
    largest single cost"). The subtotals this site computes disagree: machined
    parts {{ bom_subtotal("cnc-parts.csv") }}, actuators
    {{ bom_subtotal("actuators.csv") }}.

    The machined figure is itself not confirmed. Its quantities are quoted lot
    sizes, and until the 22 legacy and 4 B-series rows are resolved it may count
    parts twice under two names (see [CNC parts](cnc-parts.md#naming)). Settle the
    machined per-robot cost against CAD, then correct whichever claim loses.

    *Owner: hardware lead.*

## Known issues with this BOM

The internal spreadsheet this release starts from has defects that are
arithmetic, not cosmetic. They are listed here rather than quietly fixed,
because a reader who recomputes a total and gets a different answer than we
published has every reason to distrust the rest of the documentation.

### Cleanups applied, and what each one changed

Each of these was applied when the spreadsheet was split into `docs/data/`. The
transformation is recorded so it can be checked against the source.

| # | Defect in the source spreadsheet | What was done |
| --- | --- | --- |
| 1 | The published grand total counted four machining quotations, not the machined parts list. Three rows added after those quotations were never folded back in. | All three rows folded in. The machined subtotal is now the sum of the parts list itself. |
| 2 | A single-leg test fixture sat inside the robot total. | Moved to `test-fixtures.csv` and excluded from every total on this site. It is still published, so the exclusion is auditable. |
| 3 | The machined sheet's column named `UNIT COST` actually held **line totals**, so no single spare could be quoted from it. | Renamed to `total_cost_usd`. A true `unit_cost_usd` is derived by dividing by the quoted lot quantity, and left blank **TODO**{ .dh-missing } on the three rows where the division is not exact to the cent. |
| 4 | `CNC_leg02_x7_RS03_shaft_coupler` appeared twice, with different price and quantity. | Collapsed to one row carrying both quoted lots, so the subtotal is unchanged and the part ID is unique. The per-robot quantity is flagged as unconfirmed **UNVERIFIED**{ .dh-unverified }. |
| 5 | Quantities were embedded in part names (`_x4`) **and** carried in a quantity column, and the two disagree on 25 of 63 rows. | Quantity removed from every part ID. The source ID is kept verbatim in the row's notes, and every conflict is flagged per-row. |
| 6 | Unpriced rows risked being dropped to make the total look clean. | Every unpriced row is kept, with a blank price. Blank is skipped by the cost macros; `$0.00` would have been summed as zero. |
| 7 | The fastener row was `$0.00`, not blank, so a 31-DoF machine's entire hardware schedule was silently summed as nil. | Price blanked. The robot subtotal no longer claims the fasteners are free — it now visibly omits them. |

### Reconciliation

Why the figure on this site differs from the one in the internal spreadsheet.
Every number here is quoted **from the source**; none of them is a cost claim
this site makes.

{{ read_csv("data/bom-reconciliation.csv", dtype="str", keep_default_na=False, disable_numparse=True, colalign=("left", "right", "left", "left")) }}

### Still open

!!! missing "Still open — nine defects, each tracked on its own page"
    These defects are **not** fixed. They need information that is not in any
    source file. Each one is tracked as its own item on the page linked from it.

    1. **No fastener schedule.** Generate it from CAD: thread, pitch, length,
       head, drive, material, finish, quantity — plus bearings, dowel pins and
       torque values. The team standard (Torx button-head M4x12 and M3x12,
       Loctite 222) fixes the screw types but not the counts.
       *Owner: hardware lead. Blocks every page under [Assembly](../assembly/index.md).*
       See [Fasteners and hardware](fasteners-and-hardware.md).
    2. **No printed-part list.** Three material rows stand in for every printed
       part. Needs a row per part, FDM vs SLS, grade, and cost by consumable.
       *Owner: hardware lead. See [Printed parts](printed-parts.md).*
    3. **Part numbering is unresolved.** {{ bom_count("cnc-parts.csv") }} machined rows use three schemes:
       {{ bom_count("cnc-parts.csv", subassembly="leg") }}/{{ bom_count("cnc-parts.csv", subassembly="arm") }}/{{ bom_count("cnc-parts.csv", subassembly="body") }}
       rows split leg/arm/body, but 22 of them carry legacy single-leg-rig
       numbering and 4 carry a `B`-series scheme with `B4` missing. The team
       design log has a clean 32-part list in one scheme that contains none of
       those 26 rows, but it disagrees with this site on `arm05`–`arm10` (the
       same parts shifted by one ID), on the `leg02` and `leg12` counts, and
       has no `arm11`–`arm13` **UNVERIFIED**{ .dh-unverified }. Which list is
       right can only be decided against the CAD.
       *Owner: hardware lead. See [CNC parts](cnc-parts.md#the-teams-cnc-part-list).*
    4. **No material, tolerance, finish or supplier** on any machined row.
       The team design log gives aluminium as the main material and general
       tolerances of 0.03 mm and 0.06 mm, but no grade, finish or per-part
       callout. *Owner: hardware lead, from the machining quotations. See
       [CNC guide](../fabrication/cnc-guide.md).*
    5. **Per-robot quantities are unverified.** The quantities published here are
       the lots the prices were quoted for, not counts checked against CAD.
       The team's part list gives a count per part (82 pieces for its 32
       parts, computed); its counts differ from this site's on four IDs.
       *Owner: hardware lead. See [CNC parts](cnc-parts.md).*
    6. **No alternates** for the two supply-risk items, the RealSense D436 and
       the RobStride actuators. *Owner: hardware lead. See [Sourcing](sourcing.md).*
    7. **No price is dated.** The source spreadsheet records no price dates, so
       `priced_as_of` is blank on every row and every "priced as of" figure on
       this site reads *not yet published*. Re-check and date the prices before
       any of them is quoted publicly. *Owner: whoever re-sources the parts.*
       See [Price dates](sourcing.md#price-dates).
    8. **No tools tier and no optional tier.** Both read *not yet published*
       above because `tools.csv` and `optional.csv` do not exist yet. The
       ~$600 **UNVERIFIED**{ .dh-unverified } third camera module belongs in the
       optional tier; the figure is approximate and is in no data file.
       *Owner: hardware lead. See [Open items](../reference/todo.md#items-that-are-not-todo-blocks).*
    9. **No module-level quote.** Neither the gripper nor the camera gimbal can
       be priced on its own from this data. *Owner: hardware lead.* See
       [Gripper](../assembly/gripper.md) and
       [Head and camera gimbal](../assembly/head-and-camera-gimbal.md).

## Data files

| File | Rows | Contents |
| --- | --- | --- |
| `actuators.csv` | {{ bom_count("actuators.csv") }} | RobStride models, quantity and price per model |
| `electronics.csv` | {{ bom_count("electronics.csv") }} | Compute, power conversion, CAN, IMU, cameras |
| `cnc-parts.csv` | {{ bom_count("cnc-parts.csv") }} | Machined parts, split leg / arm / body |
| `cables-connectors.csv` | {{ bom_count("cables-connectors.csv") }} | Connectors, sleeving, USB cabling |
| `fasteners.csv` | {{ bom_count("fasteners.csv") }} | Placeholder only **TODO**{ .dh-missing } |
| `printed-parts.csv` | {{ bom_count("printed-parts.csv") }} | Print materials, unpriced **TODO**{ .dh-missing } |
| `test-fixtures.csv` | {{ bom_count("test-fixtures.csv") }} | Not robot parts; excluded from every total |
| `bom-reconciliation.csv` | — | The audit above. Carries no cost columns, so the macros ignore it |
| `tools.csv` | — | **TODO**{ .dh-missing } **Not published yet.** This is why the Tools tier above reads *not yet published* |
| `optional.csv` | — | **TODO**{ .dh-missing } **Not published yet.** Third camera module, spares, upgrades |

The robot subtotal is `bom_total()` called with no arguments: every parts file in
the table above except the ones marked as not being robot parts. Nothing on this
site hand-lists the files that go into a total, because three pages once did and
they would have disagreed the moment a seventh file landed.

The column contract for these files is in
[`docs/data/README.md`](https://github.com/generalroboticslab/duke_humanoid_v2/blob/main/hardware-site/docs/data/README.md).
They are plain CSV in the repository on purpose: a spreadsheet in the cloud
cannot be diffed, pinned to a release, or archived.
