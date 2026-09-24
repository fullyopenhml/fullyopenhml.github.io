# CNC guide

How to get the machined parts made correctly, and how to hand a shop a package
they can quote from without phoning you.

A part list is not a manufacturing package. Given only a name and a STEP file, a
shop will pick a material, pick a tolerance and pick a finish — all reasonably,
all differently from what the design assumed — and the parts will arrive looking
correct and refusing to fit. The difference between a list and a package is four
columns: **material, tolerance, finish, and who makes it.**

!!! missing "The machined package does not exist yet"
    All 63 machined rows in the internal sheet have **no material, no tolerance,
    no surface finish and no supplier**, and no dimensioned drawings exist. The
    STEP files are not published either; see [CAD downloads](cad-downloads.md).

    This page is therefore the specification for the package, plus the structure
    the data must land in. It cannot yet be used to place an order.

## What the machined list actually is

Before the data can be filled in, the list itself has to be cleaned. Read
[CNC parts](../bom/cnc-parts.md) for the full defect list. The short version,
because it changes how you read every table below — figures refer to the 63 rows
of the source spreadsheet, from which the migrated CSV is derived:

- 63 rows, in **three different naming schemes** — 36 `CNC_leg*` / `CNC_arm*` /
  `CNC_body*`, 22 legacy numeric names such as `08_hip_1_back_shaft_x2`, and 5
  `B*` names.
- The 22 legacy rows appear to predate the current scheme
  **UNVERIFIED**{ .dh-unverified }, so **63 rows is not 63 distinct parts**. Some
  are almost certainly the same part twice under two names
  **UNVERIFIED**{ .dh-unverified }.
- One row, `B6_single_leg_tester_plate`, is a development fixture and not a
  robot part at all.
- `CNC_leg02_x7_RS03_shaft_coupler` appears twice, with different price and
  quantity.

Do not send this list to a shop as it stands. You will pay for parts you do not
need and be short of parts you do. The team design log has a cleaner 32-part
list in one scheme; how it differs from the site list is on
[CNC parts → The team's CNC part list](../bom/cnc-parts.md#the-teams-cnc-part-list).

### Grouped by what they are

Grouped by the noun in the part name. This is an inference from names, not from
the CAD **UNVERIFIED**{ .dh-unverified }, and is here to shape the questions you
ask — not to substitute for the real data.

| Family | Rows | Likely process (**UNVERIFIED**{ .dh-unverified }) | The thing that matters most |
| --- | --- | --- | --- |
| Shafts | 14 | Turning, possibly with milled flats | Diameter tolerance at the bearing fit, concentricity, surface finish |
| Retainers | 11 | Milling | Bore diameter, bolt-circle position, flatness of the clamped face |
| Plates | 10 | Milling, possibly waterjet then faced | Flatness, hole position, thread depth |
| Covers | 6 | Milling | Clearance to what it covers — the cheapest family to get wrong harmlessly |
| Bearing housings | 6 | Milling | Bore diameter and roundness. The tightest features on the robot |
| Couplers | 4 | Turning + milling | Bore-to-shaft fit, keyway or clamp slot, balance |
| Brackets | 3 | Milling | Squareness between mounting faces |
| Caps | 1 | Milling or turning | — |
| Other named parts | 8 | Mixed | Includes the wrist roll/pitch bodies and the knee shanks |

The shafts, couplers, bearing housings and retainers — 35 of the 63 rows
**UNVERIFIED**{ .dh-unverified } — are all **fit-critical**. They are where a
general tolerance note is not good enough.

!!! unverified "UNVERIFIED — the part families, processes and the 35 fit-critical rows are inferred from part names"
    The family table above, its *Likely process* column, and the count of 35
    fit-critical rows all come from the nouns in the source part names, not from
    the CAD. The 63 source rows include one part listed twice and one test
    fixture, and the legacy rows may repeat current parts under old names, so
    the count of distinct fit-critical parts is not known. The same figure of
    35 drives the first-article checkpoint below and the measure-every-piece
    rule on [Incoming inspection](incoming-inspection.md). Confirm the family,
    the process and the fit-critical flag of every part against the CAD and
    the drawings.

    *Owner: hardware lead, from the CAD.*

## The team's design rules

### Material

Aluminium is the team's main building material, chosen in the design log as
"the best lightweight and affordable material". The log compares the two grades
JLCPCB CNC offers, 6061 and 7075, and does not record a decision, so the grade
is **UNVERIFIED**{ .dh-unverified }. *Source: team design log, "Material
Choice".* Two comments in the published repository point to 6061, though
neither is a statement about every machined part:
`simulation/asset/duke_v2/humanoid_v21/humanoid_v21_creation_v3.py` describes
the parts as "hard-anodized 6061", and
`simulation/asset/duke_v2/parallel_gripper/parallel_gripper_fusion_info.py`
gives the gripper flange the material "Aluminum 6061". The trade-off the team
weighed is on [Design → Structure and manufacturing](../design/structure-and-manufacturing.md).

### Design-for-manufacture rules

Team CNC design rules: walls ≥ 1 mm (structural walls ≥ 4 mm); blind holes end in a standard cone; screws need ≥ 4 mm of usable thread, 6 mm preferred; no sharp internal corners; chamfers preferred over fillets; tolerance 0.03 mm on radius, 0.06 mm on diameter, 0.03 mm on length; safety factor ≥ 3 under normal load. Whether the tolerances are ± or a total band is not stated (**UNVERIFIED**{ .dh-unverified }), and the SF ≥ 3 column is empty for all 32 parts. *Source: team design log, CNC checklist and CNC Part List.*

The same checklist sets the screw base: an outer radius of 8.6 mm for M4
screws and 7 mm for M3, each with a 0.2 mm chamfer. *Source: team design log,
"CNC checklist".*

### Which parts were checked

The team's CNC part list records the checks per part. 23 of its 32 parts have
all six geometric checks ticked (walls, blind-hole cone, threads, internal
corners, chamfers, tolerance): `arm01`–`arm10`, `leg02`, `leg03` and
`leg08`–`leg18`. **Nine parts have no check recorded: `body01`–`body04`,
`leg01` and `leg04`–`leg07`**: the four body plates, the hip centre back and
the four hip-roll parts. No part has
a recorded safety-factor check: the SF ≥ 3 target was never recorded as met
**UNVERIFIED**{ .dh-unverified }. *Source: team design log, "CNC Part List"
(computed from its check columns).*

Two review notes give tolerance values. On `RS03_shaft_coupler` (`CNC_leg02`):
"certain diameters have 0.03mm tolerance instead of 0.06mm". On
`ankle_pitch_front` (`CNC_leg13`): "the diameters here are tolerance with
0.06mm, double check on". Which features, and whether these are ± or a total
band, is not recorded **UNVERIFIED**{ .dh-unverified }.

### Fit-critical interfaces named in the team review

The review notes name these interfaces as needing tolerance or a second look.
Whether each note was acted on before the parts were made is
**UNVERIFIED**{ .dh-unverified }; measure them first on arrival.

- `RS03_shaft_bearing_retainer` (`leg03`): the mating feature with the motor
  needs a tolerance; chamfers suggested instead of fillets.
- `knee_front_bearing_retainer` (`leg08`): tolerance on the circular areas
  that meet the motor and the 03 shaft; a chamfer on the bearing OD area; the
  motor screw base to be changed to 4 mm.
- `knee_back` (`leg09`): tolerance on the interface with the 03 shaft;
  chamfers in several places.
- `lower_leg_output_shank` (`leg10`): a missing circular pattern on the 04
  motor side; a fillet or chamfer needed on the 03 side.
- `lower_leg_support_shank` (`leg11`): an open question on top/bottom symmetry.
- `ankle_pitch_front` (`leg13`): an open question on the clearance fit for the
  06 motor.
- `ankle_pitch_back` (`leg14`): as `leg13`, plus a check of screw-hole sizing.

*Source: team design log, "CNC Part List", note column.*

## What the reference build had to rework

The team's first-article fit check (deck dated 2/27/2025) found four parts
that had to be reworked by hand and one thread-size error in the CAD. The
readings are on [Incoming inspection](incoming-inspection.md#what-the-reference-build-found).

1. Waist motor shaft, filed down; "same with the knee motor shaft".
2. Motor04 shaft, hole enlarged for fit.
3. Motor04 shaft, filed smaller.
4. 03 motor shaft bearing retainer above the knee, enlarged; recorded as a
   "Design error".
5. Motor04 shaft and knee motor: the parts need M5 holes, the CAD has M4.

*Source: team first-article fit check, "Tolerance Check V2 CNC".* Whether the
released CAD fixes items 4 and 5 is **UNVERIFIED**{ .dh-unverified }; see
[CAD downloads](cad-downloads.md#known-cad-errors-from-the-reference-build).

<figure markdown>
  ![CAD render of an actuator and its output shaft part](../assets/photos/tolerance-cad-m4-vs-m5.webp){ loading=lazy }
  <figcaption>"Motor04 Shaft NEEDS m5 holes, but the cad has m4 holes. Same in the knee motor." Whether the released CAD has M5 is <strong class="dh-unverified">UNVERIFIED</strong>.</figcaption>
</figure>

<figure markdown>
  ![Caliper reading 57.88 mm on an 03 shaft bearing retainer](../assets/photos/tolerance-rs03-retainer-design-error.webp){ loading=lazy }
  <figcaption>"Had to enlarge, 03 motor shaft bearing retainer, above the knee", recorded as a design error. Reading 57.88 mm. Whether the CAD was corrected is <strong class="dh-unverified">UNVERIFIED</strong>.</figcaption>
</figure>

## The data every machined part needs

This is the per-part contract. It maps directly onto the machined columns in the
BOM CSVs, so filling this in fills the BOM at the same time (see the column
contract in `docs/data/README.md`).

| Field | Example of what is needed | Why a shop needs it |
| --- | --- | --- |
| `part_id` | Matches the STEP filename and the assembly step | Otherwise the delivery note cannot be reconciled |
| `material` | Alloy **and** temper for aluminium; grade for steel shafts | Temper changes strength and machinability, not just price |
| `process` | `CNC` (3- or 5-axis) / `turning` / `sheet_metal` | Decides which shop can even quote |
| General tolerance | One ISO 2768 class, stated once for the whole package | Covers the 80 % of features nobody needs to think about |
| Feature tolerances | Per bearing bore, shaft journal, dowel hole and mating face | The 20 % that decides whether the robot assembles |
| Surface finish | As-machined / bead-blast / anodise, **and on which faces** | Anodising builds up on surfaces and will close a press-fit bore |
| Threads | Size, depth, tapped or helicoil | A blind tapped hole that is 2 mm short is discovered at assembly |
| Quantity + spares | From `qty_per_robot`, plus a spares policy | Setup cost dominates; a second piece is cheap on the same setup |

!!! missing "MISSING — SAFETY — no alloy grade, temper, finish or per-feature callouts for any machined part"
    The team records fix the material family (aluminium) and a general
    tolerance rule (0.03 mm on radius and length, 0.06 mm on diameter; see
    [The team's design rules](#the-teams-design-rules)). None of the eight
    fields above exists per part for any of the 63 machined rows. Still
    missing:

    - **Alloy grade and temper per part.** 6061 or 7075 was never decided in
      the design log, and no temper is recorded. State each part explicitly
      rather than writing one blanket alloy across the package.
    - **Whether the general tolerances are ± or a total band**, and
      per-feature tolerances on every bearing seat, shaft journal, dowel hole
      and mating face. Bearing fits must be stated as a fit class or as a
      toleranced diameter, never as a nominal number.
    - **Surface finish and treatment**, per face, including whether anodised
      bores are masked or reamed after treatment.
    - **Thread specification** for every tapped hole: size, pitch, depth, and
      whether a helicoil is required. The one recorded correction is M5, not
      M4, on the Motor04 shaft and the knee.
    - **Which parts need 5-axis**, and which are turned rather than milled.

    *Owner: hardware lead, from the CAD and the machining quotations that were
    actually placed for the reference robot.* This is the single largest
    remaining gap in the hardware release.

## Handing a shop the package

{{ step(1, "Freeze the revision") }}

Pick one release tag and build the whole robot from it. Write it down. Mixing
geometry from two revisions is the most expensive mistake available here,
because it is invisible until assembly. See [CAD downloads](cad-downloads.md).

{{ step(2, "Send one archive, not a thread of attachments") }}

A quotable package is one zip containing:

- STEP, one file per part ID, named per the convention.
- A PDF drawing for every part that has a tolerance, a fit, or a finish callout.
- A parts table: part ID, quantity, material, finish, and any note.
- A cover sheet with the general tolerance class, the default finish, your
  deadline, and a contact who can answer a question the same day.

The cover sheet matters more than it sounds. Most shop queries are one question
that blocks the whole batch for a day.

{{ step(3, "Ask for a first-article on the fit-critical parts") }}

Before the full batch runs, ask for one piece of each bearing housing, shaft and
coupler, and measure it yourself against the drawing. A first-article costs one
setup; a wrong batch of 35 fit-critical parts costs the schedule.

{{ step(4, "Get the measurement report in writing") }}

Ask for measured values on the toleranced features, not a pass/fail stamp. You
will need those numbers again at
[incoming inspection](incoming-inspection.md) and when a joint binds three weeks
later.

{{ step(5, "Order spares on the same setup") }}

Thin plates, long slender shafts and anything with a deep pocket are the usual
casualties. Adding a spare while the fixture is still on the machine is a
fraction of the cost of a re-run.

!!! missing "MISSING — which machined parts to order spares of, and how many"
    Which parts to order spares of, and how many. This should come from what
    actually broke or was scrapped during the reference build, not from a guess.
    *Owner: hardware lead.*

{{ checkpoint("Do not release the full batch until a first article of each fit-critical part has been measured against the drawing. 35 of the 63 rows are fit-critical <strong class='dh-unverified'>UNVERIFIED</strong> — see the box under Grouped by what they are.") }}

## Two ways to order

=== "Route A — upload STEP"

    Upload the STEP files to an online machining service, choose material,
    finish and tolerance yourself, and accept their quote.

    **Works anywhere in the world.** The cost is that every builder re-makes the
    same material and tolerance decisions, and each gets slightly different
    parts. Batch-to-batch variation between builds of this robot will show up
    here first.

    This route is only safe once the per-part material, tolerance and finish data
    above exists. Without it, the service's defaults decide your robot's fits.

=== "Route B — pre-registered part numbers (recommended once it exists)"

    Register every machined part with one online machining service, publish the
    service's own part numbers in the BOM, and let a builder paste the number in
    and order the exact geometry we validated — no upload, no CAD interpretation,
    no re-deciding tolerances.

    OpenArm does this for all of its machined and sheet-metal parts and can
    therefore write "this method ensures you get the exact geometry we've
    validated". It removes the largest source of build-to-build variation in a
    machined robot.

    !!! missing "MISSING — whether to pre-register the machined parts with one service"
        Decide whether to register the 63 machined rows with a machining service, and if
        so, which one and whether the registration numbers can be published.
        Note the trade-off honestly on this page: pre-registration is convenient
        and ties a builder to one vendor, which may not be reachable from every
        country.
        *Owner: hardware lead.*

## Cost and lead time

Machining is the long pole of this build **UNVERIFIED**{ .dh-unverified } — see
[Which item has the longest lead time](../bom/sourcing.md#which-item-has-the-longest-lead-time).
Order it first and do everything else while you wait.

| | |
| --- | --- |
| Machined subtotal, leg **UNVERIFIED**{ .dh-unverified } | {{ bom_subtotal("cnc-parts.csv", subassembly="leg", part_class="machined") }} |
| Machined subtotal, arm **UNVERIFIED**{ .dh-unverified } | {{ bom_subtotal("cnc-parts.csv", subassembly="arm", part_class="machined") }} |
| Machined subtotal, body **UNVERIFIED**{ .dh-unverified } | {{ bom_subtotal("cnc-parts.csv", subassembly="body", part_class="machined") }} |
| Machined part rows | {{ bom_count("cnc-parts.csv", part_class="machined") }} |
| Rows with no usable price | {{ bom_unpriced("cnc-parts.csv") }} |
| Prices last checked | {{ bom_priced_as_of("cnc-parts.csv") }} |

These figures compute from the BOM CSVs; anything shown as *not yet published*
is missing from the data, not hidden. They are never typed in by hand — see
[Bill of materials](../bom/index.md) for why the existing `$14,881.99` total
cannot be quoted, and note that the subtotals above are **quoted lot prices
carried over from the source sheet**, not a clean per-robot cost: the source
rows disagree with themselves on quantity, so a subtotal is a budgeting figure
and not a purchase order.

!!! missing "MISSING — the reference machining shop, its quote, lead time and setup cost"
    - The shop used for the reference build, what they were sent, and what they
      quoted.
    - Quoted lead time per batch, in days, and whether that was a rush.
    - Setup cost versus per-piece cost, so a builder can judge whether ordering
      two robots' worth at once is worth it.
    *Owner: hardware lead.*

## On arrival

Do not start assembly out of an unchecked box. Go to
[Incoming inspection](incoming-inspection.md).
