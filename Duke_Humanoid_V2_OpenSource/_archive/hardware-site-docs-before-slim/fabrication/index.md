# Fabrication

Turning files into parts. This section covers the CAD release itself, how to
have the machined parts made, how to print the additive parts, and what to check
when a box of parts arrives.

<div class="grid cards" markdown>

- **[CAD downloads](cad-downloads.md)** — what is published, in what format, pinned to what revision.
- **[CNC guide](cnc-guide.md)** — material, tolerance, finish, and what to send a vendor.
- **[Printing guide](printing-guide.md)** — FDM and SLS profiles as numbers.
- **[Incoming inspection](incoming-inspection.md)** — catch a bad part before it is inside a limb.

</div>

!!! missing "Fabrication is the blocked part of this release"
    The software is open, the parts list mostly exists, and the assembly can be
    described. **The manufacturing data cannot**, because it has not been
    written down yet. Concretely, as verified against the repository:

    | | |
    | --- | --- |
    | Robot STEP files published | 0 — the only three `.step` files in the repository are perception fixtures |
    | Dimensioned drawings | 0 |
    | Machined parts with a material, tolerance, finish or supplier | 0 — every one of the 63 source rows is blank on all four |
    | Printed parts with a published profile | 0 |

    Until those land, this section is a specification of what must be published
    rather than a guide you can follow. Each page states exactly what is missing
    and who can supply it.

## Read in this order

1. [CAD downloads](cad-downloads.md) — pick a release tag and verify the files
   before you spend a cent. Everything downstream cites that tag.
2. [CNC guide](cnc-guide.md) — machining is the long pole
   **UNVERIFIED**{ .dh-unverified }. Order it first, then do everything else
   while you wait.
3. [Printing guide](printing-guide.md) — printing runs in parallel with the
   machining lead time.
4. [Incoming inspection](incoming-inspection.md) — before assembly, without
   exception.

Read [Sourcing](../bom/sourcing.md) alongside the first two: some off-the-shelf
items on this robot have longer lead times than the machining does
**UNVERIFIED**{ .dh-unverified }, and two of them have no published alternate
**TODO**{ .dh-missing }. The two lead-time claims on this page contradict each
other, and no lead time has been quoted; see
[Which item has the longest lead time](../bom/sourcing.md#which-item-has-the-longest-lead-time).
