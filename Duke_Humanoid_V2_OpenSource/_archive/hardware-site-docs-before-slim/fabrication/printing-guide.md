# Printing guide

Print settings for the additive parts, written as **numbers in a table**.

A slicer screenshot is not a profile. It cannot be searched, diffed, applied on
a different printer, read by a translation tool, or checked by a script. Berkeley
Humanoid Lite documents its two print profiles as thirteen screenshots with no
layer height, wall count, infill or temperature anywhere in the text; a builder
on any non-Bambu printer is left guessing. This page does the opposite: every
setting is a number in a row, and the 3MF ships as a convenience on top of that,
never as a substitute for it.

!!! missing "No print profile has been published"
    The internal parts sheet names three additive materials — TPU, PLA and nylon
    powder for SLS — as three bare rows under *Materials*, with no cost, no
    quantity, no part list, no printer and no settings. There is no list of which
    parts are printed, and no STL or 3MF has been released. See
    [CAD downloads](cad-downloads.md) and
    [Printed parts](../bom/printed-parts.md).

    Everything below is the structure the data must land in. It cannot yet be
    used to print anything.

## Processes in this build

Two processes, because the three named materials span both.

| Process | Materials named in the BOM | Typically used for |
| --- | --- | --- |
| FDM | PLA, TPU | Covers, brackets, soft pads and grips |
| SLS | Nylon powder | Parts needing isotropic strength or fine features |

!!! missing "MISSING — which parts are FDM or SLS, which are structural, and whether SLS parts have an FDM fallback"
    Which parts use which process, and which are structural. A part that is
    load-bearing must not be silently downgraded to whatever the builder's
    printer has loaded, and right now nothing on this site says which ones those
    are.

    Also state whether the SLS parts can be FDM-printed as a fallback, and what
    the strength penalty is. Most builders have an FDM printer and no access to
    SLS; if the answer is "no fallback", say so, because that turns a print job
    into a purchase.
    *Owner: hardware lead.*

## The profile table

One row per printed part, in `docs/data/print_profiles.csv`. This is the
deliverable — not a screenshot, not a slicer project file.

| Column | Meaning | Example of what is needed |
| --- | --- | --- |
| `part_id` | Matches the STL/3MF filename and the assembly step | Not a description, an ID |
| `material` | Exact grade, not the family | The difference between generic PLA and a filled PLA is structural |
| `layer_height_mm` | Numeric | — |
| `walls` | Perimeter count | The dominant strength parameter on FDM parts, ahead of infill |
| `infill_pct` | Numeric | State the pattern too if it matters |
| `orientation` | How the part sits on the plate, in words | And *why* — which face is down, which load the layer lines must not align with |
| `supports` | `none` / `tree` / `normal`, plus where | — |
| `printer_tested` | The exact machine the profile was validated on | So a reader knows what "validated" covers |

{% if data_file_exists("print_profiles.csv") %}
{{ read_csv('data/print_profiles.csv') }}
{% else %}
!!! missing "MISSING — `print_profiles.csv` does not exist"
    `docs/data/print_profiles.csv` does not exist. Once it lands, this page
    renders the full per-part table here automatically. Populate it from the
    slicer profiles the reference build actually used — export the values, do not
    re-derive them from memory.
    *Owner: hardware lead, from the printer the reference build used.*
{% endif %}

## Settings that belong in prose, not in the table

Per material, and per printer family, these are the settings a table row does not
carry well. All of them are currently unknown **TODO**{ .dh-missing }.

### PLA parts

The design log lists some print materials the team looked at, as links with no
decision; they are on
[Design → Structure and manufacturing](../design/structure-and-manufacturing.md).
None is recorded as used or validated.

!!! missing "MISSING — PLA print settings and the validated filament"
    Nozzle diameter, nozzle temperature, bed temperature, cooling, print speed,
    and the exact filament brand and grade that was validated. State whether the
    profile assumes an enclosed printer.
    *Owner: hardware lead.*

### TPU parts

!!! missing "MISSING — TPU grade, print settings and what the TPU parts are for"
    Shore hardness of the TPU used, nozzle and bed temperature, retraction
    settings, and maximum print speed. TPU is the material most likely to fail on
    a different printer, so name the extruder type the profile was validated on
    (direct drive or Bowden).

    Also state what the TPU parts are *for*. A soft part used as a foot pad and a
    soft part used as a cable grommet have different acceptance criteria.
    *Owner: hardware lead.*

### SLS parts

!!! missing "MISSING — SLS powder grade, service bureau, finish and tolerance"
    Powder grade, the service bureau used, the finish ordered (as-sintered, bead
    blast, dyed) and the nominal dimensional tolerance that service quotes.
    Unlike FDM, this is a purchase, so it needs a vendor and a lead time in the
    BOM rather than a print profile.
    *Owner: hardware lead.*

## Orientation and supports

Two rules that hold regardless of the numbers, and are worth stating because
they are the failures that reach the assembly bench:

1. **Layer lines must not run across the principal tensile load.** An FDM part is
   weakest between layers. For every structural printed part, the profile row
   must say which face is down and which load direction that choice protects.
   "Any orientation" is a valid answer only for non-structural parts, and it
   should be written explicitly rather than left blank.
2. **Mirrored parts are two files, not one instruction.** Left and right parts
   ship as separate STL/3MF files with `_left` and `_right` in the name. A note
   telling the builder to mirror in the slicer is how a robot ends up with two
   left covers, and Berkeley's documentation does exactly that.

!!! missing "MISSING — per-part orientation and supports, with the reason"
    Per-part orientation and support decisions, with the reason. This is the
    knowledge that exists only in whoever sliced the parts the first time, and is
    lost the moment they leave the lab.
    *Owner: hardware lead.*

## Post-processing

Printed parts are not finished when the printer stops.

<figure markdown>
  ![Heat-set inserts being installed in a printed battery holder with a soldering iron](../assets/photos/body-heat-set-inserts.webp){ loading=lazy width="400" }
  <figcaption>Single-leg phase build, March 2025: heat-set inserts melted into a printed battery holder with a soldering iron.</figcaption>
</figure>

During the single-leg phase the team fitted heat-set inserts into a printed
battery holder with a soldering iron. The insert size and the iron temperature
are not recorded, and whether this holder is in the finished robot is
**UNVERIFIED**{ .dh-unverified }. *Source: team design log, single-leg phase
photos.*

!!! missing "MISSING — post-processing: supports, reaming, heat-set inserts, annealing"
    Document, per part where it applies:

    - **Support removal** — where supports touch a mating face, and whether that
      face needs cleaning up before assembly.
    - **Hole reaming** — FDM holes come out undersize. State which holes are
      designed for reaming, and to what diameter.
    - **Heat-set inserts** — which parts take them, insert size, and the
      installation temperature. Every insert on the robot must be listed here or
      in [Fasteners and hardware](../bom/fasteners-and-hardware.md), with a
      quantity.
    - **Annealing or curing**, if any part requires it.
    *Owner: hardware lead.*

## Planning the print

!!! missing "MISSING — print time and material mass per part"
    Expected print time and material mass per part, so a builder can decide how
    many printers and how many spools to line up before starting. Total filament
    mass for the robot is a number people ask for before they commit, and it is
    trivial to export from the slicer that produced the profiles.
    *Owner: hardware lead.*

## Ship the 3MF alongside the STL

Once the numbers exist, also export a 3MF per part. A 3MF carries the profile
with the geometry, so a builder on a compatible printer cannot mis-apply a
setting, and a builder on an incompatible printer can still open it to read the
orientation and support choices. This is ToddlerBot's one clearly superior
practice, and it is worth copying — but as an addition to the table, not instead
of it. A 3MF that only opens in one vendor's slicer is not documentation.

## Before you print the whole set

{{ checkpoint("Print one small fit-critical part first — one that mates with a machined part or takes a heat-set insert — and check it against the drawing before committing a spool and three days of printer time to the full set. Shrinkage and hole size vary by printer far more than layer height does.") }}

## On arrival

Printed parts fail differently from machined parts: warp, first-layer elephant
foot on a mating face, undersize holes, and poorly seated inserts. Check for each
before assembly — see [Incoming inspection](incoming-inspection.md).
