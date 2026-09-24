# tools/

Everything in `docs/data/`, the files under `docs/files/` and `docs/assets/viewer/`, and two of the pages in
`docs/` are **derived**, not written. This directory holds the derivations, so that the published data can be
reproduced from its source and the published lists cannot drift away from the pages they describe.

Run them from the site root with the site's virtualenv:

```console
$ python tools/gen_bom.py                                # every parts list + team-map.csv -> docs/data/ (team BOM)
$ python tools/gen_printed.py                            # prints the printed-part mapping; writes nothing
$ python tools/gen_part_properties.py ../cad/<export>    # mass properties, joints
$ python tools/gen_modules.py ../cad/<export>            # module list
$ python tools/gen_vendor_map.py ../cad/<export>         # vendor components -> BOM
$ python tools/stage_cad_export.py ../cad/<export> --apply   # -> docs/files/, viewer/downloads.json
$ python tools/gen_cad_manifest.py                       # -> cad-files.csv, SHA256SUMS.txt
$ python tools/build_viewer.py ../cad/<export>           # -> docs/assets/viewer/
$ python tools/gen_punchlist.py                          # TODO blocks  -> docs/reference/todo.md
$ python tools/gen_image_manifest.py                     # figure gaps  -> docs/assets/MANIFEST.md
$ python -m mkdocs build --strict
```

That is also the order to run them in: the BOM defines the part IDs, the CAD
generators attach geometry to those IDs, staging publishes the files, and the
two list generators read the finished pages.

| Script | Reads | Writes |
| --- | --- | --- |
| `gen_bom.py` | `reference/bom/Duke_Humanoid_V2_BOM_WIP.xlsx` (the team BOM, the source for every parts list) and the newest `cad/*/tree.csv` | `actuators.csv`, `electronics.csv`, `cables-connectors.csv`, `fasteners.csv`, `cnc-parts.csv`, `printed-parts.csv` — all six under the column contract of `docs/data/README.md` plus `team_ref`; and `team-map.csv`, one row per team BOM line (the booklet page that labels it, the CAD count, a `status`) |
| `gen_printed.py` | the newest `cad/*/tree.csv` | nothing. It is the `PRINTED` mapping table (Fusion component -> site `part_id`: torso plates, wrist parts, covers, gripper parts, camera-column parts, end-effector attachment) that `gen_bom.py`, `stage_cad_export.py`, `build_viewer.py` and `gen_part_properties.py` import; run on its own it prints the mapping against an export and warns about a component the tree has lost |
| `gen_part_properties.py` | `cad/<export>/tree.csv` (+ `print/*.stl` for volume, `joints.csv` from `fusion_export_modules`) | `part-properties.csv`: Fusion mass, bounding box, centre of mass and inertia per site part (inertia about the centre of mass, shifted from Fusion's origin-referenced tensor, and the raw `*_origin` values); `joints.csv`: every joint with limits in degrees |
| `gen_modules.py` | `cad/<export>/modules.csv` (from `fusion_export_modules`) | `docs/data/modules.csv`: one row per module STEP — `module_id` (the slug the staged file is named after), Fusion name, English name, `class` (`module` / `vendor` / `internal` / `sketch`; `stage_cad_export.py` stages the first two), depth, qty, children, mass, path, export file, note |
| `gen_vendor_map.py` | `cad/<export>/tree.csv` | `docs/data/vendor-parts.csv` and `docs/assets/viewer/vendor-map.json`: every component with bodies that is not one of the site's own parts, matched to a BOM line by explicit rules on its own name and on each ancestor in its occurrence path. Nothing is guessed from a name no rule covers; `note` records what the model and the BOM disagree on |
| `stage_cad_export.py` | a `cad/<export>/` folder from `fusion_export` + `fusion_export_modules`, plus `docs/data/modules.csv` and `vendor-parts.csv` | copies part STEP/STL (as `<part_id>_rev<NN>.<ext>`), module STEPs (`<module_id>_rev<NN>.step`, classes `module` and `vendor`) and vendor STEPs (`vendor/<file_name>.step`; fasteners and parts under 3 g excluded) into `docs/files/`; zips a STEP over 95 MB; skips a `.f3z` over 95 MB (release asset) and the `.f3z.f3d`; keeps `docs/files/` under its 700 MB budget by dropping vendor parts under 20 g; writes `docs/assets/viewer/downloads.json`. Does not touch `docs/files/drawings/` |
| `gen_cad_manifest.py` | files under `docs/files/` | `docs/data/cad-files.csv`, `docs/files/SHA256SUMS.txt`; fails on files over GitHub's limits |
| `build_viewer.py` | `cad/<export>/print/*.stl` placed with `transforms.csv`, or a `fusion_export_viewer` folder | `docs/assets/viewer/robot.glb` (Draco, via `glb_tools.py`) and `parts.json` for the part viewer on the CAD downloads page (`downloads.json` comes from `stage_cad_export.py`, `vendor-map.json` from `gen_vendor_map.py`) |
| `glb_tools.py` | — | library, not a command: the Draco-compressing GLB writer `build_viewer.py` uses (pure numpy + DracoPy; normals travel outside the Draco stream as quantised int8, and a one-byte rank attribute keeps vertices split along sharp edges apart) |
| `gen_punchlist.py` | every `!!! missing` and `!!! unverified` block in `docs/` | `docs/reference/todo.md` |
| `gen_image_manifest.py` | figure placeholders in `docs/`, plus `part_id` columns | `docs/assets/MANIFEST.md` |

## Fusion 360 scripts (run inside Fusion: Utilities > Add-Ins > Scripts and Add-Ins)

With `humanoid_2.1_latest` open, in this order, all into one dated folder `cad/humanoid_2.1_latest_<stamp>/`:

| Script | Writes | Notes |
| --- | --- | --- |
| `fusion_export/` | `tree.csv` (every component: `fusion_name`, `file_name`, kind, qty, bodies, children, material, mass, bounding box, linked / out-of-date, path, `color_rgb` and appearance name, centre of mass, moments and products of inertia); `assembly/<design>.step` and the Fusion archive, which lands as `<design>.f3z.f3d` (1.2 MB in both exports; the 319 MB `.f3z` release asset sits only in `…_1423/assembly/`, dated 17 minutes after that run's STEP); `step/<file_name>.step` and `print/<file_name>.stl` for **every** component with bodies, vendor parts included; `joints.csv` (root only, empty: the joints live in the linked designs); `export.log` when done | `file_name` is unique per component: a second component with the same name is `name~2`. Mass to 0.1 g. **The inertia columns are about the component-frame origin, not the centre of mass** (verified against the STLs); `gen_part_properties.py` shifts them. |
| `fusion_export_modules/` | `modules/<file_name>.step` (one STEP per sub-assembly down to two levels below the root: lower body, torso, arms, gripper; legs, camera columns, wrists, hip / knee / shoulder / elbow modules, electronics tray, and the vendor assemblies at those levels); `modules.csv`; `joints.csv` (every joint of every component: type, the two occurrences, origin and axis **in that component's frame**, limits and value in rad or cm, suppressed flag); `transforms.csv` (every occurrence with bodies: path, name, the `file_name` of `tree.csv`, visible, 4×4 transform to the root in cm, row-major); `export_modules.log` | Pick the same dated folder. Overwrites the root-only `joints.csv`. |
| `fusion_export_missing/` | the `print/<file_name>.stl` and `step/<file_name>.step` that `fusion_export` failed to write; `export_missing.log` | Run after `fusion_export`. It reads `export.log`, finds every `STL …: EXCEPTION/FAILED` line and re-exports those components body by body through a short temporary path (the failures are Windows' 260-character path limit on the long vendor names). |
| `fusion_export_cameras/` | `print/<file_name>.stl` for every component whose name contains `IntelRealsense`, high resolution; `export_cameras.log` | Run after `fusion_export`, whose body-by-body STL of the two D435 components failed (`export.log`: `STL IntelRealsense_D435_Multibody: EXCEPTION FileNotFoundError` on the temporary path). Exports each as one occurrence — children and any mesh bodies included, component coordinates — which is what `build_viewer.py` places with `transforms.csv`; the field-of-view wedges come along and are dropped there by the 450 mm rule. The 16:07 log records 3 BRep bodies and 0 mesh bodies per camera, so the script's docstring ("the housing is a mesh body") is not what that export saw. |
| `fusion_export_joints/` | `joints.csv` and `transforms.csv` only (30 s, no STEP export) | For an export folder written by an older `fusion_export_modules` that had no joint writer. Same columns as `fusion_export_modules`. |
| `fusion_export_transforms/` | `transforms.csv` (old naming) and bodies-only STL/STEP of the `CNC_`/`3DP_` components that carry children | Superseded by `fusion_export` + `fusion_export_modules`; kept for the 14:23 export. |
| `fusion_export_viewer/` | `viewer/context.stl` (whole robot, world coordinates, low resolution), `viewer/parts/NNNN.stl` per occurrence of a releasable part, `occurrences.csv` | Optional: `build_viewer.py` can place `print/*.stl` with `transforms.csv` instead. |

## Three download levels

Everything visible in the Fusion model is downloadable at three levels, all from the dated export folder:

1. **Whole robot** — `assembly/<design>.step` (+ `.f3z` as a release asset), staged into `docs/files/assembly/`.
2. **Module** — `modules/<file_name>.step`, one per sub-assembly (see `modules.csv` for name, path, depth, mass).
3. **Part** — `step/<file_name>.step` and `print/<file_name>.stl` per component with bodies, machined, printed
   and vendor parts alike; `stage_cad_export.py` stages the ones with a site part ID into `docs/files/step/` and
   `docs/files/print/` under that ID.

## Where the BOM source lives

`reference/bom/Duke_Humanoid_V2_BOM_WIP.xlsx` is the team's own BOM and the one
source for every parts list. `gen_bom.py` looks for it in `../reference/bom/`
next to the site; `BOM_SOURCE_DIR` overrides that, and a path argument
overrides both:

```console
$ BOM_SOURCE_DIR=/path/to/sheets python tools/gen_bom.py
```

Every transformation is recorded per row, in the `notes` and `team_ref` columns
of the CSV the row lands in, so nothing is lost to a reader who never runs the
script. They exist so that a re-sourced price is a one-line edit to the
spreadsheet and a re-run, rather than an afternoon of hand-editing CSVs.

The two exported CSVs of the older two-sheet BOM
(`duke-humanoid-v2_BOM_sheet1_main.csv`, `_sheet2_cnc-parts.csv`) and their
generators `gen_sheet1.py`, `gen_cnc.py`, `gen_recon.py` and `audit_sheet2.py`
are superseded by `gen_bom.py` and have been removed, together with
`bom-reconciliation.csv` (an audit of the older sheet's arithmetic) and
`test-fixtures.csv` (the single-leg test-rig plate, which only that sheet
carried). The older machining quote is still what ties a team BOM machined line
to a part ID; the evidence is in the `CNC_MAP` comments of `gen_bom.py`.

## Rules these scripts enforce

`gen_punchlist.py` **fails** if any TODO block has no `*Owner:*` line. That is
deliberate: an unowned TODO is a wish rather than a work item, and this site's
whole claim is that its holes are tracked.

`gen_bom.py` never invents a figure. A team BOM line with no unit cost, or one
priced at `0`, is written with a **blank** `unit_cost_usd` and the note "Team
BOM: no price yet", so the cost macros skip it and the pages print a red TODO
instead of a `$0.00` that reads like a free part. Its `CNC_MAP` and
`PRINTED_MAP` carry the evidence for every team BOM line -> part ID mapping,
and a mapping that rests on a group of parts rather than one part says so in
the row and is marked UNVERIFIED.

`gen_printed.py`'s table and `gen_part_properties.py` never guess a material or a
value: a custom Fusion material name gives a blank cell and a note, a component
that carries child components gets no own mass, and an inertia the export's
0.1 g mass rounding cannot support is left blank with the bound in `notes`.

## Generated files — never hand-edit

`docs/data/*.csv` (all of them, including `part-properties.csv`, `joints.csv`, `cad-files.csv`),
`docs/reference/todo.md`, `docs/assets/MANIFEST.md`, `docs/files/SHA256SUMS.txt`, `docs/assets/viewer/*`.
Change the source (spreadsheet, Fusion model, page text) and re-run the generator.

## After running any of them

```console
$ python -m mkdocs build --strict
```

The build must exit 0 with no `WARNING` line. The one expected `INFO` is that
`data/README.md` and `assets/MANIFEST.md` are outside the nav, which they are on
purpose.
