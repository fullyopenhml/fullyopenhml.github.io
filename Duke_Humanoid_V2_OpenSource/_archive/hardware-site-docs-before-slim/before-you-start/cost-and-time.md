# Cost and time

What a second build costs and how long it takes. Both answers are currently
partial, and this page states exactly how partial rather than rounding to
something quotable.

## What this site says today

All figures are computed from the CSVs in `docs/data/` by the site's macros. None
is typed into this page, so a re-sourced part changes it here and everywhere else
at once.

| | |
| --- | --- |
| Actuators — {{ bom_qty("actuators.csv") }} units in {{ bom_count("actuators.csv") }} models | {{ bom_subtotal("actuators.csv") }} |
| Electronics — compute, power, CAN, sensing | {{ bom_subtotal("electronics.csv") }} |
| Machined parts — {{ bom_count("cnc-parts.csv") }} rows, test fixture excluded | {{ bom_subtotal("cnc-parts.csv") }} |
| Cables and connectors | {{ bom_subtotal("cables-connectors.csv") }} |
| Fasteners, nuts, washers, bearings | {{ bom_subtotal("fasteners.csv") }} |
| Printed parts — filament and SLS powder | {{ bom_subtotal("printed-parts.csv") }} |
| **Parts, as far as they are costed** | **{{ bom_total() }}** |

!!! missing "That total is a floor, not a price"
    Two whole categories are still placeholders rather than prices, and the rows
    are named rather than hidden: {{ bom_unpriced("fasteners.csv") }} in the
    fastener list, and {{ bom_unpriced("printed-parts.csv") }} in the printed
    materials. Every screw, nut, washer and bearing in a 31-joint machine, and
    every gram of filament and powder, is currently outside that number.

    It also excludes **tools**, **shipping and duty**, and **machining setup
    fees**, which on an order of 63 machined rows are not a rounding error. A builder should
    plan above this figure, not at it.

The single-leg test fixture in the source spreadsheet is deliberately **not** in
any figure on this site. It is development tooling, and it is held in its own
data file so that it stays visible while staying out of the robot's cost.

## Why the figure above is not the one on the spreadsheet

!!! danger "Do not quote $14,881.99"
    That is the grand total on the internal spreadsheet this release starts from.
    It is four machining quotations plus the bought-parts list — it is **not** the
    sum of the parts list on the same spreadsheet. Anyone who recomputes it from
    the parts gets a different number, which is the worst possible outcome for a
    published cost: it makes a reader distrust everything else too.

The discrepancy is explainable rather than mysterious. The four quotations cover
60 of the 63 machined rows; the three they skip were added to the sheet
afterwards and never folded back into the total. One of those three is a
single-leg test-fixture plate, which is development tooling and not a robot part
at all.

Every step of that reconciliation — each figure, where it comes from, and whether
this site publishes it — is laid out line by line on
[Bill of materials](../bom/index.md). It is on that page rather than this one so
that there is exactly one place where the arithmetic lives.

## Where the money is

Two things about the shape of the cost, both from line items rather than totals:

- **The actuators are the largest single block**: {{ bom_subtotal("actuators.csv") }}
  for {{ bom_qty("actuators.csv") }} quasi-direct-drive units in
  {{ bom_count("actuators.csv") }} models. Nothing else on the list is close, and
  they are also one of the two supply risks.
- **One camera gimbal module is cheap relative to the robot.** The design study
  puts a third module at *approximately $600 in hardware cost* plus 0.58 kg and
  two gimbal DoF. That is the best available anchor for what the project's
  headline subassembly costs on its own, and it means the feature that
  distinguishes this robot is a few per cent of its price.
  **UNVERIFIED**{ .dh-unverified }: the $600 is an approximate figure quoted
  from the design study, not a sum of priced rows in this site's data, and the
  "few per cent" is derived from it and from a total that is itself a floor.

### Actuator prices: three sets that disagree

The team records hold two actuator price lists of their own, and this site's
`actuators.csv` holds a third. None is dated, and no model has the same price
in all three. All figures are US$ per unit.

| Model | Team "Motor spec" table | Team "motor selection" sheet | This site's `actuators.csv` |
| --- | --- | --- | --- |
| RobStride 00 | 135 | 125 | 125 |
| RobStride 02 | 160 | 145 | 145 |
| RobStride 03 | 250 | 265 | 225 |
| RobStride 04 | 280 | 303 | 255 |
| RobStride 05 | 120 | 110 | 110 |
| RobStride 06 | 230 | — | 210 |

*Source: team design log, "Motor spec" table and "motor selection" sheet;
`docs/data/actuators.csv`.*

!!! unverified "UNVERIFIED — Actuator unit prices: three undated sets that disagree"
    The actuator subtotal above is computed from `actuators.csv` only. Which of
    the three price sets was actually paid, and when, is not recorded, so the
    actuator subtotal is **UNVERIFIED**{ .dh-unverified } and no total on this
    site has been recomputed from the other two sets. Get a dated quotation
    before you budget.

    *Owner: hardware lead.*

!!! missing "MISSING — What the cost figure needs before it is a price, not a floor"
    What the cost figure still needs before it is a price rather than a floor:

    - A **fastener and bearing schedule** with real prices, generated from the CAD
      rather than estimated.
    - **Printed-part cost**, priced by filament and powder consumed — by the spool,
      the way a print shop prices it, not by the part.
    - A **tools tier**, listed separately so a reader who already owns the tools
      can see the difference. The gantry belongs here, and today it is in no list
      at all.
    - An **options tier**: a third camera module, spares, and anything a builder
      can choose to skip.
    - **Shipping, duty and machining setup fees**, at least as a stated percentage
      with the assumption written next to it.
    - A `priced_as_of` date on every row, so that no figure on this site is
      undated.

    *Owner: hardware lead. Blocks any public cost claim.*

## Time

!!! missing "MISSING — Build time: no figure exists for any stage of the build"
    **No build-time figure exists, and none is estimated here.** A wrong
    build-time figure costs a reader weeks of planning, so this page would rather
    be empty than wrong.

    What is needed is an elapsed-time and person-hours record from one complete
    build, split into: procurement and machining lead time, fabrication,
    assembly, wiring, and bring-up. A first pass can come from the team's own
    last assembly, as long as it is labelled as the time taken by people who
    designed the machine — a first-time builder should be told to expect a
    multiple of that, and told what multiple.

    *Owner: whoever performs the first complete build with a stopwatch.*

## Lead time is the real constraint

Money is knowable in advance; dates are what actually decide when a robot exists.
Two items in this build carry known supply risk and neither has an alternate part
recorded anywhere:

- the **Intel RealSense D436** depth cameras, on a product line whose
  availability has been unstable; and
- the **RobStride** actuator family, 31 units across six models.

!!! missing "MISSING — Lead times, alternates and ordering sequence for long-lead items"
    - Quoted lead time for the cameras and for each actuator model, with the date
      quoted.
    - The machining vendor's quoted turnaround for an order of 63 machined rows, which is
      likely to be the longest single line on the schedule.
    - A named, tested **alternate** for both risk items. Until one exists, a
      builder's schedule depends on two single-source parts.
    - An order-of-operations recommendation: what to order first so that lead
      time overlaps fabrication instead of following it.

    *Owner: hardware lead. See [Sourcing](../bom/sourcing.md).*
