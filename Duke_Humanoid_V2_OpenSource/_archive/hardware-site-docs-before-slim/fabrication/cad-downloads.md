# CAD downloads

A hardware release is only reproducible if the geometry is **pinned**: a builder
must be able to say, two years later, which version of which file they had a
part made from, and prove the file they hold is the file we published.

This page is the specification for how Duke Humanoid V2 geometry is released.
It is written before the release exists, deliberately, so that the mechanism is
agreed before anyone uploads a zip to a shared drive and calls it open hardware.

!!! missing "Nothing on this page is downloadable yet"
    No manufacturing CAD for the robot has been published. The download table,
    the checksums and the release tag below describe **what must be published**,
    not what exists. Until the first release is cut, this page cannot be used to
    build anything. Every unfulfilled item is in its own red **MISSING** box
    below.

## What exists in the repository today

Verified against the repository as mirrored for this site.

| Item | Count | Where | Usable for manufacturing? |
| --- | --- | --- | --- |
| `.step` files, whole repository | 3 | `deploy/perception/asset/` | **No** — all three are perception fixtures |
| Simulation meshes (`.obj` / `.stl`) | 338 | `simulation/asset/duke_v2/` | No — visual and collision geometry |
| Dimensioned drawings | 0 | — | No |
| Tolerance callouts | 0 | — | No |
| Print profiles | 0 | — | No |

The three `.step` files are:

- `deploy/perception/asset/tripod_base/tripod_platform_v6.step`
- `deploy/perception/asset/tripod_base/tripod_platform_v8.step`
- `deploy/perception/asset/tag_cube_creation/v2_wrist_interface.step`

All three live under the perception asset tree and belong to the calibration
rig — a camera tripod platform and the wrist interface for the AprilTag cube.
None of them is a robot part.

The simulation export says so itself. `simulation/README.md`, under *What this
export leaves out*, names "The original CAD (`*.step`)" as excluded. The
published geometry is therefore simulation geometry: visual and inertial meshes
plus MJCF and URDF. It is correct for training and for the workspace study, and
it is **not** a manufacturing package. A mesh carries no tolerance, no thread
spec, no surface finish and no material, so a shop that receives one will make
something that looks right and does not fit.

The mesh count is also unevenly distributed, which matters when judging what is
actually released:

| Asset directory | Meshes | Comment |
| --- | --- | --- |
| `cartesian_hand_v3/` | 288 | A superseded end effector |
| `parallel_gripper/` | 28 | The current gripper |
| `humanoid_v21/` | 17 | The entire robot body |
| `head_cam/` | 5 | The camera gimbal — the paper's headline module |

## The release mechanism

**Geometry ships as assets on a tagged GitHub Release.** Not a branch, not a
folder, not a shared drive. A tag is immutable, dated, citable and mirrorable;
the other three are none of those.

### Why this is stated so bluntly

Two comparable projects got this wrong in opposite directions, and both failures
are visible in the material mirrored for this site.

=== "Berkeley Humanoid Lite"

    Both published releases carry **zero assets**:

    | Tag | Published | Assets |
    | --- | --- | --- |
    | `v1.0.0` | 2025-09-07 | 0 |
    | `v1.1.0` | 2025-09-07 | 0 |

    The releases exist; the files do not. What makes it instructive is that the
    project's own assets submodule contains a working GitHub Actions workflow
    (`.github/workflows/release.yml`) that zips a data directory and uploads it
    on every `v*` tag. The mechanism was written and simply never pointed at the
    hardware. **Cutting a tag is not publishing. Attaching the files is.**

=== "OpenArm"

    OpenArm 1.0 published CAD as a dedicated GitHub repository — STEP for
    manufacturing, STL for printed parts, wiring diagrams, and a CERN-OHL-S
    licence file next to the geometry.

    OpenArm 2.0, CELL and KER each replaced that with a single *View Drive*
    link to a Google Drive folder. A Drive folder has no tag, no checksum, no
    diff between revisions, no licence adjacency and no archive copy. A builder
    cannot cite which version they built from, and the owner can silently
    replace a file underneath them. **This is a regression, not a shortcut.**

=== "ToddlerBot"

    ToddlerBot ships pre-sliced 3MF on MakerWorld plus an Onshape link. For
    printed parts this is genuinely good — the profile travels with the geometry
    — but it is again unversioned and dependent on two third-party services
    staying up. Take the 3MF idea; keep the hosting on the release.

### Formats, per part class

| Part class | Ships as | Also ships | Why |
| --- | --- | --- | --- |
| Machined (CNC, turned) | `.step` (AP214 or AP242), one file per part ID | Dimensioned drawing as PDF for every part with a tolerance, fit or finish callout | STEP alone carries no tolerance or finish. A shop needs the drawing to quote and to inspect |
| Printed (FDM) | `.stl` | `.3mf` carrying the validated profile | STL is universal; 3MF keeps geometry and settings together |
| Printed (SLS) | `.stl` | Order-ready STEP if the service wants it | — |
| Assembly | Assembly `.step`, plus the MJCF/URDF already published | — | A builder must be able to see how parts relate, not only their outlines |
| Native CAD | **TODO**{ .dh-missing } — see the MISSING box below | — | Decides whether the design is modifiable or only manufacturable |

!!! missing "MISSING — the native CAD tool, whether native files ship, and the STEP flavour"
    Decide and state:

    - The CAD tool and version the native files come from, and **whether native
      files are published at all**. If only STEP ships, say so plainly — a
      reader can then judge how modifiable the design is before investing.
    - Whether STEP is AP214 or AP242. AP242 can carry PMI; AP214 cannot, which
      changes whether drawings are optional or mandatory.

    *Owner: hardware lead.*

### Release assets

One release carries this exact asset set. Fixed names, so that a script can
fetch them and so a mirror is obviously complete or obviously not.

| Asset | Contents |
| --- | --- |
| `duke_humanoid_v2_<tag>_step.zip` | Every machined part, one STEP per part ID |
| `duke_humanoid_v2_<tag>_drawings.zip` | One PDF drawing per part that has a tolerance, fit or finish |
| `duke_humanoid_v2_<tag>_stl.zip` | Every printed part |
| `duke_humanoid_v2_<tag>_3mf.zip` | Every printed part, with its validated profile |
| `duke_humanoid_v2_<tag>_assembly.zip` | Assembly STEP and the exploded views |
| `MANIFEST.csv` | One row per file — see below |
| `SHA256SUMS.txt` | `sha256sum`-compatible checksum file covering every asset |

### Naming convention

One rule, applied everywhere:

```text
<part_id>_rev<NN>.<ext>
```

- `<part_id>` is **byte-identical** to the `part_id` column in the BOM CSVs and
  to the ID used in the assembly step pages. One part, one identifier, three
  places. See [Part index](../reference/part-index.md).
- `<NN>` is the two-digit part revision, which advances independently of the
  release tag. A part that has not changed keeps its revision across releases.
- **Quantity never appears in a filename.** Not `_x2`, not `_x7`. Quantity lives
  in the `qty_per_robot` column and nowhere else. Encoding it in the name is
  precisely what produced 25 quantity conflicts in the legacy sheet; see
  [CNC parts](../bom/cnc-parts.md).
- Mirrored parts are two files, `_left` and `_right`. A note saying "mirror this
  one in your slicer" is how builders end up with two left feet.
- Lower case, underscores, ASCII only. No spaces, no `#`, no parentheses.

### Release tags

```text
hw-<major>.<minor>.<patch>
```

Hardware tags are namespaced with `hw-` so they never collide with software
tags in the same organisation. The proposed meaning, not yet confirmed
**UNVERIFIED**{ .dh-unverified }:

| Field advances when | Meaning for a builder |
| --- | --- |
| `major` | A part changed such that it no longer interchanges with the previous revision. **You cannot mix releases.** |
| `minor` | A part was added or changed but remains interchangeable, or a new subassembly is published |
| `patch` | Drawings, manifest, checksums or documentation fixed. Geometry unchanged |

!!! missing "MISSING — SAFETY — no CAD release: tag scheme unconfirmed, `hw-1.0.0` not cut"
    Confirm the tag scheme above, then cut `hw-1.0.0` from the geometry the
    reference robot was actually built from — not from the newest CAD in the
    lab. The first release must describe a machine that exists.
    *Owner: hardware lead.*

### Known CAD errors from the reference build

The team's first-article fit check (February 2025) found two errors in the CAD
the parts were made from:

- **Thread size.** "Motor04 Shaft NEEDS m5 holes, but the cad has m4 holes.
  Same in the knee motor." A shop working from that CAD cuts M4 where M5 is
  needed.
- **03 motor shaft bearing retainer above the knee.** It had to be enlarged by
  hand (caliper reading 57.88 mm), and the deck records it as a "Design error".

*Source: team first-article fit check, "Tolerance Check V2 CNC".* The readings
and photos are on
[Incoming inspection](incoming-inspection.md#what-the-reference-build-found).

<figure markdown>
  ![CAD render of an actuator and its output shaft part](../assets/photos/tolerance-cad-m4-vs-m5.webp){ loading=lazy }
  <figcaption>"Motor04 Shaft NEEDS m5 holes, but the cad has m4 holes. Same in the knee motor." Whether the released CAD has M5 is <strong class="dh-unverified">UNVERIFIED</strong>.</figcaption>
</figure>

!!! unverified "UNVERIFIED — whether the CAD to be released fixes the M4/M5 holes and the knee bearing retainer"
    Nothing records whether the CAD was corrected after the fit check. Before
    `hw-1.0.0` is cut, confirm that the Motor04 shaft and the knee part carry
    M5 holes and that the 03 shaft bearing retainer above the knee has the
    enlarged dimension, or publish both as known errata with the rework.

    *Owner: hardware lead.*

## The file manifest

`MANIFEST.csv` is the contract between the release and this site. Every file in
every archive gets exactly one row.

| Column | Meaning |
| --- | --- |
| `file` | Path inside the archive, e.g. `step/CNC_leg18_foot_plate_rev01.step` |
| `part_id` | Matches the BOM and the assembly steps |
| `class` | `machined` / `printed` / `assembly` / `drawing` |
| `format` | `step` / `stl` / `3mf` / `pdf` |
| `part_rev` | The `<NN>` in the filename |
| `qty_per_robot` | Copied from the BOM, so a reader can cross-check the two |
| `bytes` | File size |
| `sha256` | Checksum of that single file |
| `source` | The native CAD document and version the file was exported from |

The `sha256` column is not decoration. It is the only way a builder who
downloads a mirror, or who returns to a file after a year, can prove they are
holding what we published — and the only way we can tell a re-exported file from
an unchanged one when a release is re-cut.

Once the release exists, this page renders the manifest directly rather than
restating it in prose.

!!! missing "MISSING — `MANIFEST.csv` for the release, and a copy for this site"
    Publish `MANIFEST.csv` as a release asset **and** commit a copy under
    `hardware-site/docs/data/` so this page can render it as a table. The rows
    must reconcile 1:1 with the machined and printed rows in the BOM; a part in
    the BOM with no file, or a file with no BOM row, is a release blocker.
    *Owner: hardware lead.*

## How a builder verifies a download

Run this before sending anything to a shop. A truncated download that still
opens in a CAD viewer is a real failure mode.

```bash
# 1. Download every asset for the tag you intend to build.
# 2. Verify the whole set against the published checksums.
sha256sum -c SHA256SUMS.txt

# 3. Record the tag. Write it on the box the parts arrive in.
echo "built from: hw-1.0.0" >> build-log.txt
```

Every line must report `OK`. If any line reports `FAILED`, do not proceed:
re-download that asset, and if it fails twice, open an issue — a checksum
mismatch on a hosted file is either corruption in transit or a file that was
replaced after publication, and both are worth knowing about.

{{ checkpoint("Record the release tag you built from in your build log, before you order a single part. A build that cannot name its CAD revision cannot be supported, diagnosed, or compared with ours.") }}

## Keeping the release honest

Two automated gates, both cheap, both catching failures that this project has
already demonstrated:

1. **Attach-on-tag.** A workflow that builds the archives, writes
   `SHA256SUMS.txt` and `MANIFEST.csv`, and uploads them on every `hw-*` tag.
   Berkeley's 57-line `release.yml` is a working template; the failure there was
   not applying it, not the workflow itself.
2. **Link and manifest checking.** A job that fails the release if any README or
   docs page points at a path that does not exist, or if `MANIFEST.csv` and the
   BOM disagree. Six dead paths currently ship inside
   `simulation/asset/duke_v2/` READMEs, which is exactly what this gate catches.

!!! missing "MISSING — the release workflow and the link and manifest checker"
    Write both jobs. The release workflow blocks the hardware release; the link
    checker can land after it.
    *Owner: whoever maintains CI.*

## Licence — a hard blocker

!!! missing "The geometry cannot be published until a licence is declared"
    The code is Apache-2.0. The hardware design files and this documentation have
    **no declared licence**. Without one, a reader has no right to make, modify
    or redistribute the parts, and publishing the files anyway leaves both sides
    guessing.

    A hardware licence (the CERN-OHL family is the usual choice; OpenArm uses
    CERN-OHL-S) and a separate documentation licence must be agreed before the
    first release. The licence file ships **inside every archive**, not only in
    the repository root, because archives get copied and repositories do not
    follow them.

    *Owner: PI + university licensing office.* Tracked on
    [Citation and licence](../reference/citation-and-license.md).

## Next

Once the files exist, go to [CNC guide](cnc-guide.md) for the machined parts and
[Printing guide](printing-guide.md) for the additive parts.
