---
render_macros: false
---

# BOM data — column contract

Every cost figure on this site is computed from a CSV in this directory by the
macros in `main.py`. No cost is ever typed into page prose. If a number is not in
a CSV here, the page shows *not yet published* instead of a guess.

This file is documentation for content authors. It is excluded from the site nav
and is not meant to be read by builders.

**These CSVs are generated, not hand-edited.** The scripts that derive them from
the two source spreadsheets are in `tools/`, with their own README. Re-source a
price in the spreadsheet and re-run the generator; do not patch a CSV in place,
because the next run will overwrite it.

## Files

One CSV per **part category**, because the site nav is organised by category and
every page's macro calls are written against these filenames. Nothing is split
per subassembly at the file level; the per-subassembly view comes from the
`subassembly` column, so `bom_subtotal("cnc-parts.csv", subassembly="leg")`
answers the "what does one leg's machining cost" question without a second file.

### Published

| File | Rows | Contents |
| --- | --- | --- |
| `actuators.csv` | 6 | RobStride models, quantity and price per model |
| `electronics.csv` | 11 | Compute, power conversion, CAN adapters, IMU, cameras, battery |
| `cnc-parts.csv` | 61 | Every machined part, `subassembly` = `leg` / `arm` / `body` |
| `cables-connectors.csv` | 8 | Connectors, sleeving, USB cabling — the harness raw material |
| `fasteners.csv` | 1 | Placeholder. The real schedule does not exist yet **TODO**{ .dh-missing } |
| `printed-parts.csv` | 3 | Print materials by consumable, not yet by part **TODO**{ .dh-missing } |

### Published, but not robot parts

| File | Rows | Contents |
| --- | --- | --- |
| `test-fixtures.csv` | 1 | `B6_single_leg_tester_plate`. Development tooling. Never in a robot total |
| `bom-reconciliation.csv` | 7 | Audit trail: how the published figures reconcile against the source spreadsheet. Different schema; no part rows |

### Not published yet

| File | Blocked on | Renders as |
| --- | --- | --- |
| `tools.csv` | The tool list on [Assembly → Tools](../assembly/tools.md) is still mostly unspecified **TODO**{ .dh-missing } | *not yet published* wherever it is called |
| `optional.csv` | The third camera module (~$600 **UNVERIFIED**{ .dh-unverified }, an approximate figure in no data file), spares, upgrades **TODO**{ .dh-missing } | *not yet published* |
| `print_profiles.csv` | Slicer profiles from the reference build **TODO**{ .dh-missing } | The per-part table on [Printing guide](../fabrication/printing-guide.md) is gated on `data_file_exists()` and simply does not render |

A page may call a macro on a file that does not exist yet. The macro returns the
*not yet published* marker and the build stays green. That is the design: an
honest hole, never an invented number.

### What counts as a robot part

`bom_total()` **called with no arguments** is the whole-robot parts total. It
sums every CSV in this directory that carries the parts schema below, minus the
set `NON_ROBOT_FILES` in `/main.py` — today `test-fixtures.csv`, `tools.csv`,
`optional.csv`, `spares.csv`.

!!! danger "Never hand-write the file list into a page"
    Three pages once carried their own six-filename list inside `bom_total([...])`.
    The moment a seventh parts file lands, those pages are silently wrong and
    disagree with each other. Call `bom_total()` bare. If a new file is a robot
    part it is picked up automatically; if it is not, add it to `NON_ROBOT_FILES`
    and to the table above in the same commit.

    The reason the guard exists: a bare `bom_total()` used to sweep in
    `test-fixtures.csv` and quietly added $101.38 of single-leg development
    tooling to the advertised price of a robot.

### Rendering a table from a CSV

Two ways, and the difference matters:

- **`read_csv("data/x.csv", ...)`** renders through `tabulate`, which re-parses
  numeric-looking cells — `"$14,881.99"` comes out as `14882` and `"217.00"` as
  `217`. Always pass `dtype="str", keep_default_na=False, disable_numparse=True`.
  `dtype` must be the **quoted string** `"str"`; bare `str` is undefined in the
  Jinja environment and fails the build.
- **`{% for r in pd_read_csv(...).to_dict("records") %}`** builds the table row by
  row and is unaffected. A `{% set %}` statement must sit *above* the table
  header, never between the separator row and the loop, or its newline ends the
  table.

`allow_missing_files: false` is set in `mkdocs.yml`, so `read_csv` on a file that
does not exist is a hard build failure. Only the `bom_*` macros degrade
gracefully. Gate any `read_csv` of a file that may not exist on
`{% if data_file_exists("x.csv") %}`.

## Columns — parts CSVs

All columns must be present in the header row. A cell may be empty only where
the table below says so.

| Column | Required | Meaning |
| --- | --- | --- |
| `subassembly` | yes | Controlled vocabulary. In use today: `leg` / `arm` / `body` (machined parts) and `actuators` / `electronics` / `harness` / `fasteners` / `printed` / `test_fixture` (everything the source data does not assign to a limb). Reserved for when those modules can be quoted alone: `head_camera` / `gripper`. Add a term here before using it |
| `class` | yes | `off_the_shelf` / `machined` / `printed` / `consumable` |
| `part_id` | yes | Internal part number. Must match the CAD filename and the ID used in assembly steps. **Do not encode quantity in the part ID** (no `_x4`); that is the source of 25 known quantity conflicts in the legacy sheet |
| `description` | yes | Human-readable name |
| `mpn` | off-the-shelf: yes | Manufacturer part number, or the machine shop's quote/registration number for machined parts |
| `vendor` | off-the-shelf: yes | Vendor name |
| `vendor_url` | off-the-shelf: yes | Direct purchase link |
| `alt_mpn` | may be empty | Alternate part number. **Mandatory** for the RealSense D436 and every RobStride actuator — both are known supply risks |
| `alt_url` | may be empty | Link for the alternate |
| `qty_per_robot` | yes | Plain integer for the whole robot. Never `2pcs`, never a range |
| `unit_cost_usd` | yes if priced | True cost of **one** piece, in USD, digits only (no `$`, no thousands separator) |
| `total_cost_usd` | may be empty | `qty_per_robot × unit_cost_usd`. Leave empty and let the macro compute it; fill only when a vendor quotes a lot price that is not a clean multiple |
| `material` | machined/printed: yes | `Al6061-T6`, `PA12`, `TPU95A`, … |
| `process` | machined/printed: yes | `CNC` / `sheet_metal` / `FDM` / `SLS` / `turning` |
| `tolerance_finish` | machined: yes | Tolerance class and surface finish, e.g. `±0.05 mm, anodised clear` |
| `lead_time_days` | may be empty | Quoted lead time in days |
| `priced_as_of` | yes if priced | ISO date `YYYY-MM-DD` the price was checked. Macros surface the newest date on the page so no price is undated |
| `notes` | may be empty | Free text: pitfalls, substitutions, "ships with the kit" |

### Rules that exist because the legacy sheet broke them

1. `unit_cost_usd` is a **unit** cost. The legacy `Sheet2` put line totals in a
   column named `UNIT COST`; a reader could not quote a single spare from it.
2. Test-fixture parts are not robot parts. `B6_single_leg_tester_plate` lives in
   `test-fixtures.csv`, which is in `NON_ROBOT_FILES` and therefore outside every
   robot total. It is kept as data rather than as prose so that the $101.38
   exclusion is printed by a macro instead of typed into a sentence that will
   drift.
3. No duplicate `part_id`. The legacy sheet has `CNC_leg02_x7_RS03_shaft_coupler`
   twice with different price and quantity.
4. Empty is not zero. Leave a price blank if it is unknown; do not write `0.00`.
   A `$0.00` fastener row is how a 31-DoF robot came to have uncosted hardware.
5. Every priced row carries `priced_as_of`.

## Columns — `print_profiles.csv`

| Column | Meaning |
| --- | --- |
| `part_id` | Matches a `class=printed` row in a parts CSV |
| `material` | `PLA`, `PLA-CF`, `TPU95A`, `PA12` |
| `layer_height_mm` | Numeric |
| `walls` | Perimeter count |
| `infill_pct` | Numeric |
| `orientation` | How the part sits on the plate, in words |
| `supports` | `none` / `tree` / `normal`, plus where |
| `printer_tested` | The exact printer the profile was validated on |

## Macros that read these files

Defined in `/main.py`, called from pages as `{{ macro_name(...) }}`:

`bom_subtotal(csv, subassembly=, part_class=, exclude_ids=)`,
`bom_total(csv_names=, exclude_ids=)`, `bom_count(csv, ...)`, `bom_qty(csv, ...)`,
`bom_unpriced(csv)`, `bom_priced_as_of(csv)`, `data_file_exists(csv)`, `money(x)`.

A missing file makes the macro return a *not yet published* marker. It does not
break the build, and it must never be worked around by typing the number in.
