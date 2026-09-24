# Sourcing

Where to buy, how long it takes, and what to do when something is unavailable.
Order the long-lead items before anything else: machining and the two
supply-risk components set the schedule for the whole build.

## Order these first

| Item | Why |
| --- | --- |
| {{ bom_count("cnc-parts.csv") }} machined parts, {{ bom_subtotal("cnc-parts.csv") }} | Longest lead time in the build **UNVERIFIED**{ .dh-unverified }, and a {{ bom_count("cnc-parts.csv") }}-part quotation is not a same-week job |
| Intel RealSense D436 ×2 | Known supply risk; the RealSense line has had repeated availability gaps |
| RobStride actuators, {{ bom_qty("actuators.csv") }} units, {{ bom_subtotal("actuators.csv") }} | Known supply risk, and the largest single cost **UNVERIFIED**{ .dh-unverified } — see [Which category costs the most](index.md#which-category-costs-the-most) |

!!! missing "MISSING — quoted lead times for the three long-lead items"
    Real quoted lead times for all three, with the date quoted. The
    `lead_time_days` column is blank on every row of every data file.
    *Owner: hardware lead.*

### Which item has the longest lead time

!!! unverified "UNVERIFIED — whether machining or a bought part has the longest lead time"
    This page, [CNC parts](cnc-parts.md) and the [CNC guide](../fabrication/cnc-guide.md)
    call machining the longest lead time in the build. The
    [Fabrication overview](../fabrication/index.md) says the opposite: that some
    off-the-shelf items have longer lead times than the machining does. With no
    quoted lead time anywhere in the data, neither claim is backed. Settle it
    from the quoted lead times above, then correct the page that is wrong.

    *Owner: hardware lead.*

## Supply-risk parts

These are the rows that carry a supply-risk flag in `docs/data/`. Both of them
need an alternate, and neither has one.

{% set risky = pd_read_csv("data/actuators.csv", dtype="str", keep_default_na=False).to_dict("records") + pd_read_csv("data/electronics.csv", dtype="str", keep_default_na=False).to_dict("records") %}
| Part ID | Description | Qty | Alternate | Vendor |
| --- | --- | ---: | --- | --- |
{% for r in risky if "SUPPLY RISK" in r.notes %}| `{{ r.part_id }}` | {{ r.description }} | {{ r.qty_per_robot }} | {{ r.alt_mpn or "**TODO**{ .dh-missing } none published" }} | [{{ r.vendor }}]({{ r.vendor_url }}) |
{% endfor %}

!!! missing "MISSING — alternates for the supply-risk parts"
    - A named alternate for the **D436**, with the mounting and field-of-view
      consequences stated. The workspace study assumes a 90°×65° RGB field of
      view; a different camera changes the result the design was optimised for.
    - Alternates for **each RobStride model**, or an explicit statement that none
      is drop-in and what a substitution costs in CAD changes. The mounting
      interface, the shaft and the CAN configuration all change with the model.
    - Alternates for anything else that has gone out of stock during the
      project's own build.

    The column contract makes `alt_mpn` / `alt_url` mandatory on exactly these
    rows, and they are blank on all of them. The actuators the team compared
    during selection are candidates, not validated alternates; see
    [Design → Actuator selection](../design/actuator-selection.md).
    *Owner: hardware lead.*

## Vendors

Every vendor in the bought-parts files, with the lines that come from each.
Rendered from `docs/data/`.

{% set bought = pd_read_csv("data/actuators.csv", dtype="str", keep_default_na=False).to_dict("records") + pd_read_csv("data/electronics.csv", dtype="str", keep_default_na=False).to_dict("records") + pd_read_csv("data/cables-connectors.csv", dtype="str", keep_default_na=False).to_dict("records") %}
| Vendor | Lines | Part IDs |
| --- | ---: | --- |
{% for vendor, items in bought | selectattr("vendor") | groupby("vendor") %}| {{ vendor }} | {{ items | length }} | {{ items | map(attribute="part_id") | join(", ") }} |
{% endfor %}

Most of this list is a consumer marketplace rather than a distributor, which is
normal for a lab build and a problem for a reproducible one: marketplace listings
go away, and the part behind a listing can change without the listing changing.

!!! missing "MISSING — manufacturer part numbers for the marketplace lines"
    For every marketplace line, either a manufacturer part number that can be
    ordered from a distributor, or a statement that the part is only available
    that way. The `mpn` column is blank on most bought rows.
    *Owner: hardware lead.*

## Machining vendors

The team's material study compared the two aluminium grades JLCPCB CNC
offers, 6061 and 7075, from JLCPCB's own material pages, so JLCPCB CNC was at
least used for material pricing. That JLCPCB machined the reference robot is
**UNVERIFIED**{ .dh-unverified }: the design log never says so. *Source: team
design log, "Material Choice".*

!!! missing "MISSING — the machining vendor for the reference build, and what they were sent"
    Which vendor made the parts for the reference build, what they were quoted,
    and what a builder must send them (file format, tolerance callouts, finish
    specification). If a vendor's own part number can be reused to order the
    validated geometry directly, publish it.

    The machined rows carry a price and nothing else: no `vendor`, no `mpn`, no
    `material`, no `tolerance_finish`. The four quotation batches visible in the
    source sheet suggest at least four separate orders **UNVERIFIED**{ .dh-unverified };
    whether they went to the same shop is not recorded.
    *Owner: hardware lead. See [CNC guide](../fabrication/cnc-guide.md).*

## Price dates

!!! missing "No price on this site is dated"
    The source spreadsheet records no price dates at all, so `priced_as_of` is
    blank on every row of every data file and every "prices checked" line on this
    site reads *not yet published*. Undated prices on a hardware release are
    worse than no prices: a reader cannot tell whether they are six months or
    three years old.

!!! missing "MISSING — a checked date on every price"
    Re-check every price against its vendor link and write the date into
    `priced_as_of`. Do this before any cost figure from this site is quoted
    publicly.
    *Owner: whoever re-sources the parts.*
