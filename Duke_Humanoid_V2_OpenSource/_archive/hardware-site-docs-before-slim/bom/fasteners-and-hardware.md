# Fasteners and hardware

Screws, nuts, washers, dowel pins, bearings and threadlocker. This is the
largest single hole in the release: a 31-DoF, 36 kg machine currently has
**{{ bom_count("fasteners.csv") }} spreadsheet row** standing in for all of it.

!!! missing "The fastener list does not exist"
    The source spreadsheet contains a single row reading
    `example: fasteners, nuts`, priced at `$0.00`, with no vendor link and no
    quantity. Every screw, nut, washer and bearing in the robot is behind that
    placeholder.

    A `$0.00` row is worse than a blank one: it was **summed into the grand
    total as zero**, so the published cost silently claimed that the fasteners
    of a 36 kg humanoid are free. That price is blank in `fasteners.csv`, which
    is why the fastener subtotal below reads *not yet published* rather than
    `$0.00`, and why the robot subtotal on the [BOM index](index.md#cost-summary)
    visibly omits this category instead of understating it.

    What the schedule must contain is itemised in the boxes below.

## What the data file contains

Rendered from `docs/data/fasteners.csv`.

| Part ID | Description | Qty | Unit cost | Vendor |
| --- | --- | ---: | ---: | --- |
{% for r in pd_read_csv("data/fasteners.csv", dtype="str", keep_default_na=False).to_dict("records") %}| `{{ r.part_id }}` | {{ r.description }} | {{ r.qty_per_robot or "**TODO**{ .dh-missing }" }} | {{ money(r.unit_cost_usd|float) if r.unit_cost_usd else "**TODO**{ .dh-missing }" }} | {{ r.vendor or "**TODO**{ .dh-missing }" }} |
{% endfor %}
Subtotal: {{ bom_subtotal("fasteners.csv") }}. Rows with no usable price:
{{ bom_unpriced("fasteners.csv") }}.

Without this list a builder cannot order hardware, cannot check a delivery, and
cannot assemble anything: the assembly pages have nothing to reference.

## The team hardware standard

Team hardware standard: Torx button-head M4x12 (McMaster-Carr 90991A123) and M3x12 (90991A115) only; main bearing 50x65x7 mm; threadlocker Loctite 222. The first-article check contradicts 'M4/M3 only': 'Motor04 Shaft NEEDS m5 holes, but the cad has m4 holes. Same in the knee motor' (**UNVERIFIED**{ .dh-unverified } which the released CAD has).

*Source: team design log, "Hardware Choice"; first-article fit check, February
2025.* The log links the main bearing to McMaster-Carr 6656K229 for its CAD
model and says it was bought on Amazon. It leaves the ankle thrust bearing
blank: "Thrust bearing for ankle: _______". Whether the as-built ankle has a
thrust bearing, and which one, is **UNVERIFIED**{ .dh-unverified }. The M4/M5
finding is on [Incoming inspection](../fabrication/incoming-inspection.md#what-the-reference-build-found).

The team's CNC design rules add two screw rules: a screw needs at least 4 mm of
usable thread, 6 mm preferred, and the screw base around an M4 screw has an
outer radius of 8.6 mm (7 mm for M3) with a 0.2 mm chamfer. *Source: team design
log, "CNC checklist".*

### Screwing into an actuator

The RS03 mounting interface, per the dimension drawing in the RobStride 03
product manual §1.1 (cited, not reproduced): the housing face takes 8 × M4
threaded holes, 8 mm deep, equally spaced on a Ø98 ±0.2 mm circle; the output
face has 6 × M4 blind threaded holes, 6 mm deep, and 3 × Ø4 (+0.1/0) blind
holes, 7 mm deep, equally spaced, dimensioned on Ø30.36 ±0.2 mm; a Ø70
(0/−0.1) pilot stands 2.5 mm proud of the housing. The RS02, RS03 and RS04
manuals all say that a fastening screw must not go deeper than the housing
thread depth. Check every screw that goes into an actuator against that rule.

!!! missing "MISSING — SAFETY — no fastener schedule, no bearing list, no torque values"
    Generate a real fastener schedule from CAD. What it must contain:

    - One row per unique fastener: thread and pitch, length, head type, drive,
      material and finish, quantity for the whole robot.
    - Bearings: designation, quantity, and fit (press, slip) per location. The
      machined list has bearing *retainers* and bearing *housings* on almost
      every joint, but not one bearing. The team standard names only the
      50x65x7 mm main bearing, and leaves the ankle thrust bearing blank.
    - Dowel pins, retaining rings, shims, and any pressed bushings.
    - Where the threadlocker (Loctite 222, per the team standard) goes, and
      where it must **not** be used.
    - Every screw that is not M4x12 or M3x12, starting with the M5 holes the
      first-article check found on the Motor04 shaft and the knee.
    - **Torque value per fastener size and per joint.** No comparable open
      humanoid project publishes torque values; this build's joints are
      quasi-direct-drive and preloaded, so the values matter more here than
      usual. An under-torqued shaft coupler on a 36 kg machine is a safety
      problem, not a cosmetic one.
    - A purchase link per line, or a named assortment that covers the list.

    A comparable project's step-by-step manual resolved to 22 distinct fastener
    sizes between M2.5 and M6; that is the granularity to aim for.
    *Owner: hardware lead, from the CAD. Blocks every page under
    [Assembly](../assembly/index.md), and blocks any honest whole-robot cost.*

## Consumables

The threadlocker is Loctite 222, a removable grade. *Source: team design log,
"Hardware Choice".*

!!! missing "MISSING — where threadlocker is used, retaining compound and grease"
    Where Loctite 222 is applied and where it must not be, retaining compound,
    grease type per bearing and per sliding surface, and anything else consumed
    during assembly. None of it appears in any source file.
    *Owner: hardware lead.*
