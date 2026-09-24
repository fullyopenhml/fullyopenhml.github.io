# Open items — the punch list

Every unresolved item on this site, in one table: **0 open items** across **0 pages**, of which **0 block the public release**.

This page is the team's working list. It is generated from the `MISSING` / `UNVERIFIED`
blocks on the pages themselves, so it cannot drift away from them: close a block
on its page and it leaves this table when the list is regenerated. Nothing is
tracked here that is not also marked in place, and nothing is marked in place
that is not here.

!!! note "How to read a row"
    **Page** links to the exact section or step the gap sits in — that is where
    the surrounding facts are, and where the answer must be written. **Who can
    supply it** is copied from the block's own owner line; it names a role, not
    a person, because roles survive a graduation. **Blocks release** is `yes`
    only when the block's own owner line says `Blocks release.` — it is declared,
    never inferred from wording, so a row carries that weight only because
    somebody decided it should.

## Where the work sits

| Section | Open items | Blocking release |
| --- | ---: | ---: |
| **Total** | **0** | **0** |

## Who is holding what

An item owned jointly counts once against each role, so this column sums to
more than 0.

| Role | Open items | Of those, blocking |
| --- | ---: | ---: |

## What the release still owes

These are the home page's own blocker rows, read from that page and restated
as work. Everything else in this list makes a build harder; these are the
ones somebody has to close before this counts as a finished release.

| Blocker | Where it is tracked |
| --- | --- |

## Items that are not TODO blocks

These gaps are structural rather than a missing fact, so they have no block
on a page to generate a row from. Their presence here is checked against
`docs/data/` on every run, so a row leaves this table when the file lands.

| Gap | What it means | Who can supply it | Blocks release |
| --- | --- | --- | :-: |
| `print_profiles.csv` does not exist | The per-part profile table on [Printing guide](../fabrication/index.md#printing-guide) is gated on the file and does not render. Material and process per part are published without it, on [Printed parts](../bom/index.md#printed-parts) | hardware lead | no |

## Images

Missing figures are not in this table. They are tracked separately, with the
exact path and a one-line brief for each, in the
[image manifest](IMAGES_NEEDED.md) — the list to hand to whoever renders
the exploded views.

## Regenerating this page

This table is derived from the pages, not maintained by hand:

```console
$ python tools/gen_punchlist.py
```

Every TODO block in `docs/` has the same shape, and that shape is what makes
the derivation possible:

```markdown
!!! missing "MISSING — short statement of the gap"
    What is missing, in enough detail that the person who has the answer
    recognises it as theirs.
    *Owner: role who can supply it.*
```

For something that is stated but not confirmed, use `!!! unverified` with a
title starting `UNVERIFIED —`. Both kinds render red and bold. Write
`MISSING — SAFETY — ...` when the gap is a safety item or stops a build
outright; the generator reads that as *blocks release*. The
`*Owner:*` line is mandatory — the generator refuses to run without it, because
an unowned TODO is a wish rather than a work item.

