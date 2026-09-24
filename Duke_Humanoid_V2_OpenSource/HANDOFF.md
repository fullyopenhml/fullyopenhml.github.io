# Handoff — Duke Humanoid V2 hardware release

Read `CLAUDE.md` first for the working rules. This file is the single working
document for the release: status, what is left, and the benchmark evidence
behind those decisions. It replaces the old `V2_RELEASE_PLAYBOOK.md`.

Last worked on: 2026-09-20.

## Status

| Item | State |
|---|---|
| Site (`hardware-site/`, MkDocs Material) | 50 pages, English, `mkdocs build --strict` exits 0 with zero `WARNING` |
| Punch list (`hardware-site/PUNCHLIST.md`, generated, not published) | **27 open items across 17 pages, 9 block release.** Recalibrated 2026-09-20, down from 184 items / 56 blockers. See *How the punch list was recalibrated* |
| Images still needed (`hardware-site/IMAGES_NEEDED.md`, generated, not published) | **83** (2 placed, 26 named, 55 per-part). The whole-robot exploded view is no longer among them: the booklet's page 15 fills it on the home page and on `assembly/index.md` |
| Team exploded-view booklet | `reference/team/duke_humanoid_v2_hardware.pdf` (Eric Lu, 2026-09-19, 15 pages). Rendered to `docs/assets/exploded/team/NN-<name>.webp` (2400 × 1350) and **published as the site's assembly figures**. The PDF is staged as `docs/files/drawings/duke_humanoid_v2_exploded_views_rev01.pdf` (untracked until committed) and indexed in `cad-files.csv`. Pages 08 and 12 read "switch A ↔ B": on the other leg / arm the covers labelled A and B swap sides (confirmed by the user) |
| Exploded-view animations | 9 web MP4s in `docs/assets/exploded/`, embedded on the assembly pages |
| Wiring diagrams | `hardware/*.jpg` → `docs/assets/wiring/`, on the electrical pages |
| CAD downloads (`docs/files/`) | **329 files, 706 MB** (672.9 MiB as `gen_cad_manifest.py` prints it): 1 whole-robot STEP (zip, 34 MB), 80 module STEPs (481 MB), 76 part STEPs (77 MB), 45 printed-part STLs (51 MB), 125 vendor files (55 MB), 2 PDFs under `drawings/`. `.f3z` (319 MB) is release asset `cad-v2.1-rc1` (sha256 `f440621d…`). No per-part drawings exist |
| Canonical CAD export | `cad/humanoid_2.1_latest_2026-09-19_1607/` — **complete**. Holds `tree.csv` (629 components), `assembly/`, `step/` (410), `print/` (408), `modules/` (128), `joints.csv` (1205), `transforms.csv` (2088) and the export logs |
| BOM source | **The team's spreadsheet `reference/bom/Duke_Humanoid_V2_BOM_WIP.xlsx` is the parts list**; where the robot is known to differ, `QTY_OVERRIDE` / `PRINTED_QTY_OVERRIDE` in `gen_bom.py` publish the robot's count (see *What the team must supply*, item 4). `tools/gen_bom.py` writes all six parts CSVs and `team-map.csv` from it. Unpriced rows carry a **blank** cost and render a red TODO, never `$0.00` |
| Parts data (generated, `docs/data/`) | `cnc-parts.csv` 35, `printed-parts.csv` 48, `electronics.csv` 14, `actuators.csv` 6, `fasteners.csv` 9, `cables-connectors.csv` 1; `part-properties.csv` 76, `joints.csv` 1205, `modules.csv` 128, `vendor-parts.csv` 287, `cad-files.csv` 329; `team-map.csv` 100 (77 settled, 23 open) |
| 3D viewer (`docs/assets/viewer/`) | `robot.glb` (2.3 MB, Draco), `parts.json`, `downloads.json`, `vendor-map.json`. Fusion appearance colours, joint axes, preview and download per part, hide/show and x-ray |
| Code repo (for fact-checking) | Recloned 2026-09-20 to `reference/duke-humanoid-v2/repo/`. Submodules use SSH URLs; clone `duke_humanoid_v2_deploy` and `duke_humanoid_v2_simulation` over HTTPS separately and move them into place. Not in git |
| Local preview | `.venv/bin/mkdocs serve -a 127.0.0.1:8321` → `http://127.0.0.1:8321/duke_humanoid_v2/` |

## The 9 items that block release

| # | Item | Page | Owner |
|---|---|---|---|
| 1 | Lifting points on the robot, sling route, clearance zone | `before-you-start/safety.md` | hardware lead |
| 2 | E-stop: none in the BOM or power diagram, yet the run scripts assume one | `before-you-start/safety.md` | electrical lead |
| 3 | Physical power-on / power-off order of the rails | `before-you-start/safety.md` | electrical lead |
| 4 | Shank-cover STEP/STL are byte-identical to the shoulder covers — wrong geometry ships today | `bom/printed-parts.md` | whoever stages the export |
| 6 | Which printed parts are FDM, which are SLS, and which are structural | `fabrication/printing-guide.md` | hardware lead |
| 7 | Pack-path fuse (none drawn); surge protector part number and rating | `electrical/power-system.md` | electrical lead |
| 8 | Hardware and documentation licence not declared | `reference/citation-and-license.md` | PI + licensing office |
| 9 | Licence file for the two Unitree G1 URDFs | `reference/citation-and-license.md` | PI |

Everything else on the site is either an honest note (the builder's call, or
never measured on our robot) or a source conflict that does not stop a build.

## How the punch list was recalibrated

184 items / 56 blockers → 27 / 9, on four rules. Apply them to anything new.

1. **A gap is a fact needed to build *this* robot.** Institutional process — EHS,
   PPE, lock-out/tag-out, incident registers, inspection intervals — and telemetry
   nobody measured on our robot are the builder's to determine. They are `!!! note`,
   never red.
2. **The published CAD answers dimensions.** Bolt circles, fastener sizes, fits,
   cut lengths, pilot diameters: 76 part STEPs and 45 STLs are published, so
   those are "read off the model" notes pointing at CAD downloads, not gaps.
3. **The published model is authoritative** where the team's spreadsheet
   disagrees on a count, an ID or a material. The spreadsheet is a working
   document.
4. **One fact, one page.** The missing e-stop was four separate blocking rows on
   four pages; duplicates now cross-link to one canonical page.

`Blocks release` is now **declared, not inferred**: `gen_punchlist.py` gates only
when an owner line says `Blocks release.` The old heuristics keyed on `SAFETY` in
a title, a hardcoded page set, and the word *block* anywhere in the body — which
fired on *"4 distribution blocks"*.

The deployed MJCF and the released URDF closed the rest: joint travel and axes,
gimbal sides, IMU frame, limb handedness, jaw opening and clocking, gripper
servo IDs, the canonical citation title.

### The joint-direction rule (from the user, 2026-09-20)

**Every joint's positive rotation axis points from the motor's output shaft
towards the back of the motor.** Fit the actuator the way the model orients it
and the sign follows; no per-joint sign table is needed. The deployed MJCF
(`deploy/control/legged_env_bundle/mj_envs/deploy/runs/…/robot.xml`) is the
reference for what the robot does. Where the simulation model mirrors a mesh and
flips an axis sign for the same joint, that is a modelling convention, not a
hardware difference.

This is the pattern to repeat: one sentence from someone who built the robot
closes a red box that no amount of document archaeology could.

### Still worth asking the team

1. **Charger** — the team log links an "ISDT … DC600Wx2"; which model, what rate?
2. **Power-on / power-off order** — computer, USB-CAN adapters, motor bus, gimbals.
3. **Torques** — even a generic ISO class per screw size, flagged as generic.
4. **Hard stops** — do the legs, arms or gimbals have mechanical end stops at all?
5. **FDM vs SLS** — which printed parts are which, and which are structural.

## What the team must supply

1. **Licence** — hardware and docs licence undecided. Blocking.
2. **E-stop / main disconnect** — none in the power diagram, but the run scripts
   assume one. Blocking.
3. **Joint limits** — the Fusion model has none (see below); the site takes them
   from the MJCF.
4. **BOM: decided 2026-09-21 — the robot wins over the spreadsheet.** The site publishes
   the robot's quantity where the team sheet or the Fusion model disagrees with it, through
   `QTY_OVERRIDE` / `PRINTED_QTY_OVERRIDE` in `tools/gen_bom.py`; the xlsx is not edited.
   Corrections the team should carry into the xlsx so the two stop disagreeing:
   - `E6` RS06: sheet buys 2, robot has 4 (`ankle_2`, `shoulder_2`, both sides).
   - `P15` AprilTag tiles: sheet 12, booklet and CAD 16.
   - `P35`/`P36` arm-roll covers: sheet 4 + 4, CAD has three halves × 4 = 12 (`3DP_armP11_shoulder_yaw_cover_c` has no line).
   - `C25` unit price 57.56 is exactly twice the old machining quote for the same part.
   - `P28` shank covers: the sheet's 4 is right; the **Fusion model has them on the right leg only** — add the left-leg pair to the CAD.
   Consumables (XT30 / XT30(2+2) / GH1.25 / EC5, loom, Ethernet, heat-shrink, bulk wire,
   120 Ω terminators, fuse + holder, filament, SLS powder) are listed without prices by decision.
   Machined parts are the team BOM's lines only (the five extra CNC rows were dropped).

   **Model ↔ BOM audit (2026-09-21, `tools/build_viewer.py` output vs `docs/data/*.csv` vs the booklet):**
   - All 75 CNC + printed part ids: BOM quantity = Fusion occurrences, STEP (and STL for prints) present, no two part ids share a byte-identical file.
   - Every label in the booklet (`[CPEH]n`) is a team BOM line; `team-map.csv` page references all agree with the PDF text. Never drawn in the booklet: `C8`, `C9`, `E8`, `E9`, `E11`, `H6`–`H8` (mapped by name / not drawable).
   - Fusion components in the model that are **in no BOM at all** — the team must say whether each is a real part on the robot: `150A relay` (interior plate, 87.6 g), ~~`U-joint_type_C_adapter v3` ×2~~ (settled 2026-09-21: the USB-C right-angle adapter, site line **E21**, price and vendor still to come from the team), `casing` ×2 (power-block casing, ABS, 8.7 g — a print?), `dovetail_umi_gripper` ×2 (351 g gripper body — how does it relate to `3DP_grip01`–`06`?). Wires/cable dummies ignored.
   - **Viewer resolution — deferred (user, 2026-09-21: not needed for now).** If it is ever wanted, rebuild the GLB at the new defaults — `build_viewer.py` now caps a part at 10 000 faces, a vendor component at 6 000, a fastener at 200, the whole model at 3 M (was 3 000 / 1 500 / 100 / 900 k: actuator housings and other round parts rendered as polygons). Expect roughly 7–9 MB Draco instead of 2.3 MB. Needs the Fusion export's `print/` STLs, which only the Windows machine has: `python tools/build_viewer.py ../cad/humanoid_2.1_latest_2026-09-19_1607` after `fusion_export_viewer`, then commit `docs/assets/viewer/`.
   - Two viewer bugs fixed in `build_viewer.py` (Fusion copy suffix ` (1)` on the second camera column; the D435's internal `Component34`–`37` matched the shoulder covers). **`parts.json` was hand-patched to match; the next Fusion export + `build_viewer.py` run regenerates it properly** (the STL exports are no longer on the Mac — re-export on the Windows machine).
5. **CAD, remaining**: no per-part drawings, so machined parts are ordered from
   STEP. Slicer plates (3MF) → `docs/files/plates/` if the team has them. The
   `.f3z` must be re-released on the public repo.
6. **Hardware revision id**: Fusion says `2.1`, MJCF is `humanoid_v21` → v2.1.

## CAD export pipeline — three download levels

Principle (the user's): everything visible in the Fusion model is downloadable at
three levels — **whole robot** (`assembly/`), **module** (`modules/`: every
sub-assembly down to two levels below the root, vendor assemblies included) and
**part** (`step/` + `print/`: every component with bodies, vendor parts
included). `hardware-site/tools/README.md` documents every script.

Folders under `cad/` (`.gitignore` ignores `cad/*/assembly/`, `step/`, `print/`,
`modules/`, `viewer/` and `cad/_scratch/`; tracked are `tree.csv`, `joints.csv`,
`transforms.csv`, `modules.csv`, the logs and `…_1423/drawings/`):

- `humanoid_2.1_latest_2026-09-19_1423/` — OLD. Complete (317 STEP/STL) but the
  export wrote one file per component *name*, so same-named components overwrote
  each other. Nothing on the site comes from it.
- `humanoid_2.1_latest_2026-09-19_1607/` — **canonical**. All site data and every
  staged file come from here.
- `_scratch/` — Draco / decimation experiments (`reencode_glb.py`: DracoPy q14
  level 10 takes the 15 MB GLB to 1.6 MB; `decim_compare.py`: pymeshlab quadric
  collapse is ~10× more accurate than fast_simplification at equal face count).

Fusion scripts (`hardware-site/tools/fusion_export*/`, run inside Fusion, all
into one dated folder): `fusion_export` (tree, whole robot, per-part STEP + STL),
`fusion_export_modules` (module STEPs + `joints.csv` + `transforms.csv`),
`fusion_export_joints` (30 s), `fusion_export_missing` (re-export STLs that
failed on Windows' 260-character path limit), `fusion_export_cameras`,
`fusion_export_viewer` (optional), `fusion_export_transforms` (superseded).

Site-side, in order: `gen_bom.py` → `gen_printed.py` → `gen_part_properties.py
<export>` → `gen_modules.py <export>` → `gen_vendor_map.py <export>` →
`stage_cad_export.py <export> --apply` → `gen_cad_manifest.py` → `build_viewer.py`
→ `gen_punchlist.py` → `gen_image_manifest.py` → `mkdocs build --strict`.

Watch the GitHub limits (95 MB/file, 900 MB total, both as `gen_cad_manifest.py`
measures them in MiB — the staged tree is at 672.9 MiB, largest file 70.1 MiB;
`stage_cad_export.py` has its own 700 MB budget).

### Findings from `tree.csv` (2026-09-19)

- **Fusion's `getXYZMomentsOfInertia()` is about the component-frame origin, not
  the centre of mass**, with tensor-form products (`ixy` = −∫xy dm). Verified
  against trimesh on four parts' STLs (`CNC_arm13`: Fusion Ixx 381 692 = STL
  about origin 382 472, not the 3 223 about the COM). `fusion_export.py`'s
  docstring says "about the COM" — wrong, not fixed. `gen_part_properties.py`
  shifts to the COM (parallel-axis) and keeps raw values in `*_origin` columns.
  Because `tree.csv` rounds mass to 0.1 g, the shift is uncertain by ±0.05 g ×
  |COM|². Fix: have `fusion_export.py` write `mass_g` to 0.001 g.
- The left and right arm designs, and the two leg designs, are separate linked
  designs, so most parts are 2–3 Fusion components (`name`, `name~2`, `name_1`,
  `name (1)`); `gen_printed.py` sums their quantities and `gen_part_properties.py`
  compares the copies (`CNC_leg12` copies differ in the sign of the COM z;
  `3DP_arm06` copies differ in COM by ~2 mm).
- Printed parts listed: 45 from the Fusion tree. Materials `rail` / `Base` /
  `Neck` / `Arm` are custom Fusion names → material and process blank.
  `3DP_body05` is `PLA (for Bambu H2D)` → PLA, FDM.
- The gripper's `cnc_flange` of the code repo **is**
  `CNC_arm13_RS05_shaft_coupler` (Aluminum 6061, 22.05 g there, 22.1 g here).
  The gripper rack `double_helix_rack_30teeth_6mm v2` has **no geometry**.
- Not listed, noted on Printed parts: `Hub` (Bambu PAHT-CF), `ankle_top_cover`
  (Steel, right leg only), the gripper root's own body. Torso spine, battery
  holders, IMU bracket and computer T-brackets are not in the Fusion tree at all.
- **The Fusion model carries no joint limits**: of 1205 joints (1162 rigid, 37
  revolute, 4 slider, 2 planar) exactly one has a limit value. Limits come from
  the MJCF.
- Model masses (CAD): 35.27 kg total (lower body 17.51, torso 7.85, arms
  4.61/4.60, grippers 0.35 each); 33.4 kg without grippers and camera columns vs
  34.5 kg in the MJCF → UNVERIFIED.

## Benchmark: what a hardware release actually ships

Four published projects, surveyed 2026-09. Mirrors under `reference/` (4.4 GB,
not in git). Use this to settle "is X a deliverable?" arguments.

| Project | BOM | Assembly docs | CAD | Docs site | Licence | Cost |
|---|---|---|---|---|---|---|
| **Menlo / Asimov 1** | No public BOM; per-step "Parts needed" tables (78 of 83 pages) | 83 step pages, 430 deep-linkable 3D animations, 0 photos | STEP (v0) / MJCF+URDF (v1), bare GitHub paths, no Release | Next.js + Fumadocs, 136 pages, `llms.txt` + `llms-full.txt` | **None at all** — the word "license" appears zero times site-wide | No prices anywhere |
| **OpenArm 2.0** | 7 pages by sub-assembly × manufacturing class, with photos, part numbers, unit and line prices (JPY) | 1.0 has 10 pages / ~71 steps + 5 wiring pages; 2.0 has **none** | STEP/STL/F360; 1.0 in its own repo, 2.0 on a bare Google Drive link | Docusaurus 3.10, Algolia, versioned | CERN-OHL-S-2.0 (hardware) / Apache-2.0 (code + docs), marked per repo | Line-by-line JPY + 9 page subtotals, but never a cross-page total |
| **ToddlerBot 2.0** | Google Sheet + `toddlerbot_BOM_release.csv` in-repo, 100 rows, two configs side by side | One page + an outdated 11-page PDF + 14 sub-assembly videos | Onshape (unversioned) + MakerWorld 3MF; repo holds only simulation STLs | Sphinx + Furo, 42 pages | MIT (code) / **CC BY-NC-SA 4.0** (hardware) | Tiered subtotals: robot $5,727.94 / tools $1,976.13 / optional $2,252.73 |
| **Berkeley Humanoid Lite** | A Google Sheet iframe only; no file in the repo | 6 text pages + 9 YouTube videos; mechanical steps are almost entirely video | Onshape (4 live documents) + MakerWorld 3MF; **GitHub Release assets are empty** | GitBook, 27 pages, search + AI Q&A + `llms.txt` | MIT (code) / CC BY-SA 4.0 (assets); **docs unlicensed** | $4,312 US / $3,236 China, but only inside the paper PDF |

**Four conclusions.**

1. None of the four passes on every axis, so there is no "just copy one" option.
   Copy per axis: BOM from OpenArm 1.0, assembly visuals from Asimov, cost
   tiering from ToddlerBot, engineering notes and reproduction experiments from
   Berkeley.
2. **The most expensive mistakes are not technical.** Asimov has the best
   assembly manual in the world and is legally unusable downstream because the
   word "license" never appears. Berkeley stakes a $5,000 claim on a Google
   Sheet that cannot be diffed, pinned or archived.
3. **Nobody publishes torque values.** All four omit them. It is the cheapest
   axis on which V2 can beat every one of them.
4. V2's own `deploy/control/docs/auto_operator_safety_contract.md` (261 numbered
   `SAFE-*-NNN` mechanisms, 3,411 lines) and `auto_operator_incidents.md` have no
   equivalent in any of the four mirrors. That habit belongs on the mechanical
   side too — but note it is software-side only and buys no personal safety.

### Patterns worth copying

Paths are in the `reference/` mirrors (not in git).

**BOM and purchasing**
- BOM split by sub-assembly × manufacturing class —
  `reference/openarm/md/1.0/hardware/bill-of-materials/` (7 pages).
- Subtotals that cannot drift — `reference/openarm/repo/website/src/components/BoMTable.tsx`,
  `priceUtils.ts`; the `.mdx` pages are 4 lines each.
- Multi-config single-table BOM with upgrade-delta rows —
  `reference/bom/toddlerbot_BOM_release.csv`.
- Machinist part numbers in the BOM — OpenArm's `procuring-components.md`
  Method 2 (paste a MEVIY number, "ensures you get the exact geometry we've
  validated").
- Exact substitutes for chronically out-of-stock parts —
  `reference/toddlerbot/docs-site/md/hardware/02_pcb8ch.md`.

**Assembly and fabrication**
- Per-step "Parts needed" table including "Threadlocker | As needed" — any
  Asimov step page.
- Tool list with photos, explicit non-affiliate marking, and which tools ship
  with a kit — `reference/asimov/md/asimov/1/assembly-preparations/assembly-tools.md`.
- Withdrawing an unverified procedure and saying why —
  `reference/asimov/md/asimov/1/assembly-verifications.md` ("Do not use earlier
  drafts to approve power-on…"). Safer than leaving a wrong checklist up.
- Firmware preconditions gating a hardware step — the blocking WARNING at the
  top of OpenArm's `j1-j2-sub-assembly.md`.
- Bring-up checkpoints with expected symptom *and* remedy —
  Berkeley's `flashing-the-motor-controllers.md` (LED ~1 Hz, `ping.py` prints
  "Motor is online", calibration draws ~1 A; if direction is reversed, swap two
  phases or set `MOTOR_PHASE_ORDER = -1`).
- Print parameters as numbers, not screenshots — Berkeley's
  `3d-printing-instructions.md` is the counter-example: 13 screenshots, zero
  numbers in the text.

**Release mechanics**
- A 57-line workflow that packages and uploads assets on a tag —
  `reference/berkeley-humanoid-lite/repo/source/berkeley_humanoid_lite_assets/.github/workflows/release.yml`
  (and `releases.json`'s `"assets": []` shows why it went unused).
- A dated, handwritten changelog that admits geometry errors —
  `reference/berkeley-humanoid-lite/docs-site/md/releases.md`.
- Docs inside the repo, built on every push —
  `reference/toddlerbot/repo/docs/` + `deploy_page.yml`.
- Versioned hardware revisions with a migration page — OpenArm's
  `docusaurus.config.ts` + `whats-new-in-2.0.md`. **Copy the versioning, not the
  silent `removedInV2` redirects** — they send someone holding 2.0 hardware into
  the complete 1.0 manual without telling them.

**Licence and community**
- Per-repo licence marking *and* a restatement on the CAD download page —
  OpenArm's 9-repo README table + the "📌 Licensing" section of `find-cad-files.md`.
- Hardware/code licence split in full text —
  `reference/berkeley-humanoid-lite/repo/source/berkeley_humanoid_lite_assets/LICENCE`
  (CC BY-SA 4.0) + `repo/LICENCE` (MIT). Three traps there: the assets
  `pyproject.toml` says `license = "MIT"`, contradicting the LICENCE beside it;
  the lowlevel submodule has no licence file at all; the file is spelled
  `LICENCE` while the README links `LICENSE`.
- Hardware-aware issue template — ToddlerBot's `bug_report.yml` (required OS
  dropdown including Jetson / ROG Ally X).
- A safety guide written around *this* design's specific hazards — OpenArm's
  `safety-guide.md` names back-drivable joints dropping their load the instant
  an e-stop cuts power, with four periodic checks.

**Reproducibility**
- Reproducibility as a falsifiable Results experiment — ToddlerBot's
  "Reproducibility: Hardware and Policies" (cross-unit policy transfer,
  two-robot collaboration, 1000× build timelapse).
- Cross-printer consistency and a 60-hour endurance protocol — Berkeley's paper
  §D (6 actuators × 2 printers). Note §B's backlash figures (0.0229 rad, std
  0.0042) come from a *different* set of 6 actuators; do not merge the two.
- Publish the ugly numbers beside the good ones — ToddlerBot's project page
  (19-minute overheat, 7 falls, a 21 min print + 14 min assembly repair, a
  cartwheel blooper reel). That is *why* its positive claims read as credible.
- Release notes written as a community report — Berkeley's `releases.json`
  v1.1.0 names 12 external builders and honestly pre-announces V2.

## Repo layout

- `hardware-site/` — the site. `tools/` regenerates everything derived (see
  `tools/README.md`).
- `hardware/` — team power and data wiring diagrams (source of truth for the
  electrical pages).
- `reference/bom/` — the team's BOM spreadsheet (the parts list).
- `reference/team/` — the team's exploded-view booklet (the assembly figures).
- `reference/_meta/cad-trees/` — evidence for `CAD_RELEASE_COMPARISON.md`.
- The rest of `reference/` (mirrors of Asimov / OpenArm / ToddlerBot / Berkeley,
  clones of our repos, papers; 4.4 GB) is **not in git**.
- Not in git either: the Notion design-log export (1.7 GB; vendor PDFs — do not
  redistribute) and the AVI originals of the exploded views.
- `_archive/hardware-site-docs-before-slim/` — the 96k-word pre-slim site, to
  recover a fact if needed.
- `CAD_RELEASE_COMPARISON.md` — CAD-format analysis, still in Chinese.

## Windows notes

```
cd hardware-site
py -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\mkdocs serve -a 127.0.0.1:8321
```

`.claude/launch.json` has `hardware-site` (Windows) and `hardware-site-macos`.
Line endings are forced to LF by `.gitattributes`, and every generator in
`tools/` writes LF and POSIX paths on both systems (before 2026-09-19
`gen_punchlist.py` and `gen_image_manifest.py` produced wrong counts on Windows
because they compared backslash paths). Set `PYTHONIOENCODING=utf-8` when a
generator prints `×` or `·` to a cp1252 console.

## Publishing

Decided 2026-09-20 (Boxi Xia): **Pages public, repository private.** Every push to `main` runs the strict build
(`.github/workflows/docs.yml` at the repo root — GitHub reads only that location) and deploys to
`https://generalroboticslab.github.io/Duke_Humanoid_V2_OpenSource/` (Settings → Pages → Source: GitHub Actions).
Collaborators need only write access. Everything under `docs/files/` is publicly downloadable from the site;
the 319 MB `.f3z` release asset stays collaborator-only while the repository is private.
**Do not force-push `main`**: a force push on 2026-09-21 dropped the publish configuration and the live site
stopped updating until it was merged back.

