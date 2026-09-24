---
render_macros: false
---

# BOM data — column contract

Bill of materials (BOM) CSV rules, for content authors; not in the site nav.

- Every site cost is computed from these CSVs by the macros in `main.py`, never
  typed into prose. A missing value renders as *not yet published*.
- The scripts in `tools/` generate the CSVs from the source: change the source
  and re-run the generator; never edit a CSV by hand.
- The six parts lists all come from one source, the team's own BOM
  (`reference/bom/Duke_Humanoid_V2_BOM_WIP.xlsx`), through `tools/gen_bom.py`.
  Where that spreadsheet and any older sheet disagree, the spreadsheet wins.

## Files

| File | Rows | Contents |
| --- | --- | --- |
| `actuators.csv` | 6 | RobStride models (team BOM `E1`-`E6`) |
| `electronics.csv` | 14 | Computer, battery, power conversion, CAN adapters, IMU, cameras, servos, surge protector, distribution blocks, voltage checkers |
| `cnc-parts.csv` | 35 | Machined parts, `subassembly` = `leg` / `arm` / `body`: the team BOM's 30 machined lines mapped to part IDs, plus 5 published part IDs the team BOM has no line for |
| `cables-connectors.csv` | 1 | The one cable line of the team BOM |
| `fasteners.csv` | 9 | Six bearing sizes and three screw sizes; none priced |
| `printed-parts.csv` | 49 | 45 printed parts from the Fusion tree, 1 team BOM line with no CAD match, then 3 print-material rows (`MAT_*`) |
| `part-properties.csv` | one per part in the Fusion model | Mass, bounding box, volume, centre of mass, inertia; no cost column, so never in a total |
| `vendor-parts.csv` | one per vendor/other component with bodies in the Fusion model | Which BOM row each vendor component of the CAD belongs to; no cost column, so never in a total |
| `modules.csv` | one per sub-assembly STEP the Fusion modules export wrote | The module (sub-assembly) download level: id, English name, class; no cost column |

Not yet created: `tools.csv`, `optional.csv`, `print_profiles.csv`. A `bom_*`
macro on a missing file returns *not yet published*; the build stays green.

## Rules

- `bom_total()` is called with **no arguments** everywhere. It sums every parts
  CSV here except `NON_ROBOT_FILES` in `main.py` (`test-fixtures.csv`,
  `tools.csv`, `optional.csv`, `spares.csv` — none of which exists today); add
  any new non-robot file to it in the same commit.
- `read_csv(...)` re-parses numbers: always pass `dtype="str",
  keep_default_na=False, disable_numparse=True` (the quoted string `"str"`).
- In a `{% for %}` table, put any `{% set %}` above the header row, never
  between the separator and the loop.
- `allow_missing_files: false` makes `read_csv` on a missing file fail the
  build. Gate it with `{% if data_file_exists("x.csv") %}`.
- Leave an unknown price blank, never `0.00`: blank is skipped, zero is summed.
  A team BOM line priced `0` is an unknown price, not a free part, so it lands
  here blank with the note "Team BOM: no price yet" and the page prints a red
  TODO. `bom_unpriced(csv)` lists exactly those rows.
- No duplicate `part_id`.

## Columns — parts CSVs

Every column must be in the header row.

| Column | Required | Meaning |
| --- | --- | --- |
| `subassembly` | yes | `leg` / `arm` / `body` / `actuators` / `electronics` / `harness` / `fasteners` / `printed` / `head_camera` / `gripper` |
| `class` | yes | `off_the_shelf` / `machined` / `printed` / `consumable` |
| `part_id` | yes | Matches the CAD filename and the assembly steps. No quantity in the ID (no `_x4`) |
| `description` | yes | Human-readable name |
| `mpn` | off-the-shelf | Manufacturer part number, or the shop's registration number |
| `vendor` | off-the-shelf | Vendor name |
| `vendor_url` | off-the-shelf | Direct purchase link |
| `alt_mpn`, `alt_url` | D436 and every RobStride | Alternate part and link |
| `qty_per_robot` | yes | Plain integer for the whole robot |
| `unit_cost_usd` | if priced | Cost of one piece, digits only |
| `total_cost_usd` | optional | Only for a lot price that is not a clean multiple |
| `material` | machined, printed | e.g. `Al6061-T6`, `PA12`, `TPU95A` |
| `process` | machined, printed | `CNC` / `turning` / `sheet_metal` / `FDM` / `SLS` |
| `tolerance_finish` | machined | e.g. `±0.05 mm, anodised clear` |
| `lead_time_days` | optional | Quoted lead time |
| `priced_as_of` | if priced | ISO date the price was checked |
| `notes` | optional | Free text. Every generated row starts with the team BOM line it came from, verbatim, then anything the mapping leaves open |
| `team_ref` | yes, when the team BOM has the row | The `#` value of the team BOM line the row came from (`E3`, `C21`, `P20`, `H1`). Several refs, comma-separated, mean the row's part is covered by several lines, or that a group of lines was matched to a group of parts without resolving which is which (the `notes` say so). Blank means the team BOM has no line for this part |

**Quantities.** A purchased, machined or fastener row carries the team BOM's
quantity. A printed row carries the Fusion occurrence count, because the team
BOM's printed lines are grouped by cover half rather than by component; where
the two differ, the row says both.

**`print_profiles.csv` columns:** `part_id` (a `class=printed` row), `material`, `layer_height_mm`, `walls`,
`infill_pct`, `orientation`, `supports` (`none` / `tree` / `normal`, plus
where), `printer_tested`.

## Macros

In `main.py`: `bom_subtotal(csv, subassembly=, part_class=, exclude_ids=)`,
`bom_total(csv_names=, exclude_ids=)`, `bom_count(csv, ...)`, `bom_qty(csv, ...)`,
`bom_unpriced(csv)`, `bom_unpriced_count(csv=)`, `bom_row_count(csv=)`, `bom_priced_as_of(csv)`,
`data_file_exists(csv)`, `money(x)`, `cad_links(part_id)`, `part_props(part_id)`, and for table cells
`money_cell(value)`, `line_total_cell(row)`, `team_ref_cell(row)` — the only way a cost or a team
ref reaches a cell, so a blank renders a red TODO and never `$0.00`.

## Downloadable CAD files

`cad-files.csv` is generated by `tools/gen_cad_manifest.py` from the files under `docs/files/` — never
edit it by hand. Columns: `part_id`, `rev`, `kind` (`step` / `print` / `drawings` / `plates` /
`assembly` / `modules` / `vendor`), `format`, `path`, `bytes`, `sha256`. It has no cost column, so it
never enters a BOM total. For a `modules` file `part_id` is the `module_id` of `modules.csv`; for a
`vendor` file it is the export file name (`file_name` of `vendor-parts.csv`, cut to 80 characters plus a
hash when longer).

| Folder | Holds | Name |
| --- | --- | --- |
| `docs/files/step/` | one STEP per machined or printed part | `<part_id>_rev<NN>.step` |
| `docs/files/print/` | printable mesh per printed part | `<part_id>_rev<NN>.3mf` (or `.stl`) |
| `docs/files/drawings/` | drawing per machined part | `<part_id>_rev<NN>.pdf` |
| `docs/files/plates/` | slicer projects, ready to print | any name, `.3mf` |
| `docs/files/assembly/` | whole-robot STEP and Fusion 360 archive | any name, `.step` / `.f3z` |
| `docs/files/modules/` | one STEP per sub-assembly (`modules.csv`, classes `module` and `vendor`) | `<module_id>_rev<NN>.step` (`.step.zip` over 95 MB) |
| `docs/files/vendor/` | one STEP per vendor component (`vendor-parts.csv`, fasteners and parts under 3 g left out) | `<file_name>.step` (`.step.zip` over 95 MB) |

`<part_id>` must match the parts CSVs exactly; the `cad_links(part_id)` macro puts the download links in
each parts table. The generator fails on any file over 95 MB or a total over 900 MB (GitHub limits);
`tools/stage_cad_export.py`, which fills the folders from a Fusion export, keeps the total under 700 MB
(when the vendor STEP files would exceed it, only vendor components above 20 g are staged).

`docs/assets/viewer/downloads.json` (also written by `stage_cad_export.py`) lists every file under
`docs/files/` for the 3D viewer: `{key: [{label, href}]}`, key = a site `part_id`, `vendor:<file_name>`
(the full export file name) or a `module_id`, plus `robot` for the whole-robot files; `href` is relative to
the docs root (`files/...`). `docs/assets/viewer/vendor-map.json` (from `gen_vendor_map.py`) maps the
export `file_name` of every matched vendor component to `{part_id, bom_file, description, qty_in_model,
via}`.

## Vendor components of the CAD

`vendor-parts.csv` is generated by `tools/gen_vendor_map.py <cad export>` — never edit it by hand. It
has one row for every component with bodies in `tree.csv` that is not one of the site's own parts
(`cnc-parts.csv`, `printed-parts.csv`), and says which BOM row it belongs to. Matching is by the explicit
rules in the script (the component's own Fusion name, then its ancestors nearest first, so an actuator's
rotor is matched through its `Robstride 0N` parent); nothing is inferred from an uncovered name.

| Column | Meaning |
| --- | --- |
| `file_name` | Export file name from `tree.csv` (unique: `name`, `name~2`, ...); the key of `vendor-map.json` and of `downloads.json` (`vendor:<file_name>`) |
| `fusion_name` | Fusion component name |
| `qty_in_model` | Occurrences of the component in the Fusion model |
| `part_id`, `bom_file` | The BOM row (in `actuators.csv`, `electronics.csv`, `cables-connectors.csv` or `fasteners.csv`) it belongs to; blank when no rule matches |
| `description`, `mpn`, `vendor`, `vendor_url` | Copied from that BOM row; blank when unmatched |
| `note` | `via` the ancestor that carried the match; model-vs-BOM differences (model name, modelled count vs `qty_per_robot`); for an unmatched row, why the BOM has no row for it |

## Modules (sub-assemblies)

`modules.csv` is generated by `tools/gen_modules.py <cad export>` from `<export>/modules.csv`
(written by `tools/fusion_export_modules` in Fusion: one STEP per component with child components, two
levels below the root) — never edit it by hand.

| Column | Meaning |
| --- | --- |
| `module_id` | Slug of the export file name; the staged file is `docs/files/modules/<module_id>_rev<NN>.step` and the key in `downloads.json` |
| `fusion_name` | Fusion component name |
| `english_name` | Name for the site, from the table in the script; a name used more than once carries its side (left/right arm or leg) or its Fusion copy; an unknown name keeps the Fusion name (see `note`) |
| `class` | `module` (a sub-assembly of this robot's design), `vendor` (a purchased assembly modelled by its vendor), `internal` (a sub-assembly inside a vendor assembly), `sketch` (a sketch/section carrier). Only `module` and `vendor` are staged |
| `depth` | 0 = direct child of the root |
| `qty` | Occurrences of the component in the model |
| `children` | Child components |
| `mass_g` | Fusion mass with children, g |
| `path` | Occurrence path of the first occurrence |
| `file` | STEP file name in the export's `modules/` folder; blank when Fusion's export failed |
| `note` | Why a row is not staged, or that it has no English name yet |

## Part mass properties

`part-properties.csv` is generated by `tools/gen_part_properties.py <cad export>` from the Fusion export
(`tree.csv` and `print/*.stl`) — never edit it by hand. It has a `part_id` column but no cost column, so
`bom_total()` skips it by shape. `part_props(part_id)` renders `mass g · X × Y × Z mm` from it in the parts
tables (a red TODO for a part or value that is not there; an UNVERIFIED mark on a size the STL and the Fusion
component disagree on). Every value is CAD-derived; the site never calls it measured.

| Column | Unit | Meaning |
| --- | --- | --- |
| `part_id` | — | Matches the parts CSVs exactly; only a part found in the Fusion tree gets a row |
| `fusion_name` | — | Fusion component the row was derived from |
| `material` | — | Fusion material *name* of the component (not a verified grade) |
| `mass_g` | g | Fusion CAD mass with that material; blank when the Fusion component carries child components (its mass would include them) |
| `volume_cm3` | cm³ | Volume of the part's STL (closed mesh) |
| `bbox_x_mm`, `bbox_y_mm`, `bbox_z_mm` | mm | Axis-aligned bounding box in the part's own frame: Fusion's, or the STL's for a component with children |
| `com_x_mm`, `com_y_mm`, `com_z_mm` | mm | Centre of mass in the part's STEP/STL frame, from the STL |
| `ixx`, `iyy`, `izz`, `ixy`, `ixz`, `iyz` | g·mm² | Inertia matrix about the centre of mass, axis-aligned with the STEP/STL frame; off-diagonals in tensor form (`ixy` = −∫ x y dm); uniform density `mass_g / volume` (trimesh's density-1 tensor in mm⁵ × g/mm³) |
| `notes` | — | Why a value is blank or in doubt; `part_props` and the part index read it |

Blank means *not derivable from this export* (see `notes`), never zero. The generator's docstring lists the
cases: a component with child components, two components sharing one STL file name, a mesh that is not
watertight, an STL whose bounding box differs from Fusion's.

