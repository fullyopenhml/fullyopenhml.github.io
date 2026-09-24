# Duke Humanoid V2 — open-source hardware release (working rules)

This folder prepares the **hardware** open-source release of Duke Humanoid V2
(General Robotics Lab, Duke). The code is already public at
github.com/generalroboticslab/duke_humanoid_v2. V1/V2 are **our own** robots,
not reference material.

## How to talk to the user
- The user is often waiting; give honest time estimates and check background
  work by looking at real signals (file mtimes, build output), not assumptions.

## Site rules (`hardware-site/`, MkDocs Material)
- **100 % English** on the site. Zero Chinese characters anywhere under `docs/`.
- **One job:** let a stranger build an identical robot — buy, make, assemble,
  wire, bring up, verify, safety, specs. No dev diary, dates, options
  considered-and-dropped, selection process, comparisons with other projects,
  or meta-commentary. Design rationale belongs in the paper, not the site.
- **One page per section.** `nav` holds eight entries and no sub-entries. Each
  `<section>/index.md` ends with `{% include "<section>/<page>.md" %}` lines, in
  build order, and `exclude_docs` keeps those files from also building as pages
  of their own; the site's section links are that page's headings
  (`toc.integrate`). Add a page = add the file, add its `{% include %}`, nothing
  in `nav`. Cross-page links are `../<section>/index.md#<heading-slug>`, in-page
  ones are bare `#<heading-slug>`. Repeated heading text on one page needs an
  explicit `{ #id }`; `{{ step() }}` anchors are namespaced by the
  `{{ step_ns("<file stem>") }}` that precedes each include.
- **Clear and scannable:** imperative headings, numbered steps (one action
  each), tables, figures above the steps they explain, `✅ **Check:**` lines,
  an `!!! abstract "At a glance"` box on build pages, no paragraph over ~3
  sentences, no stacked boxes.
- **Never invent a hardware fact.** Every number traces to the code repo
  (`reference/duke-humanoid-v2/repo`, not in git — reclone if needed), the BOM
  CSVs, the team wiring diagrams (`hardware/`), or the team's Fusion 360 model.
  If unknown → a gap, not a guess.
- **A gap is a fact needed to build *this* robot** — a dimension, a torque, a
  part number, a procedure specific to this design. Lab process, institutional
  policy (EHS, PPE, lock-out/tag-out, incident registers) and telemetry nobody
  measured on our robot are the builder's to determine: those go in a plain
  `!!! note`, never a red block. Scope creep here is not harmless — it buries
  the real stoppers and stalls the release.
- **Every gap is RED and BOLD**, one line, with an owner:
  `!!! missing "MISSING — …"` / `!!! unverified "UNVERIFIED — …"` (+ `*Owner: role.*`),
  inline `**TODO**{ .dh-missing }` / `**UNVERIFIED**{ .dh-unverified }`.
  A block gates the release **only** when its owner line says `Blocks release.` —
  declared, never inferred from wording. Styles in `docs/stylesheets/extra.css`.
- As-built only in build pages. Conflicts between sources: state both values, mark UNVERIFIED.
- Generated files — never hand-edit: `hardware-site/PUNCHLIST.md` (punch list, not published),
  `hardware-site/IMAGES_NEEDED.md` (images needed, not published), `docs/data/cad-files.csv`,
  `docs/files/SHA256SUMS.txt`. Regenerate with the scripts in `tools/`.
- `mkdocs build --strict` must pass with zero warnings before you stop.

## Build / preview
```
cd hardware-site
uv venv .venv                                                  # once; .venv already exists
uv pip install --python .venv/bin/python -r requirements.txt   # once
.venv/bin/mkdocs serve -a 127.0.0.1:8321
# open http://127.0.0.1:8321/Duke_Humanoid_V2_OpenSource/
```
`python -m venv` fails on this machine — no `ensurepip` (the `python3-venv` package is
not installed and needs root). `uv` is installed and needs no root; use it.

The `/Duke_Humanoid_V2_OpenSource/` path prefix is not magic: `mkdocs serve` reuses the path of
`site_url` in `mkdocs.yml`, which currently points at the project's GitHub Pages URL.
Point `site_url` elsewhere and the prefix follows; no page, script or link depends on
the site being hosted on GitHub Pages.

Regenerate after edits: `python tools/gen_punchlist.py`, `tools/gen_image_manifest.py`,
`tools/gen_cad_manifest.py` (indexes `docs/files/`; its 95 MB-per-file and 900 MB-total
ceilings are GitHub's limits, so relax them if the site moves to another host).

After `mkdocs build`, run `python tools/check_links.py`. `--strict` only validates
Markdown links; raw HTML (`<video>`, `<model-viewer>`, `poster=`) it never looks at,
so a path left at the wrong URL depth 404s silently. Must report 0 broken links.

## Layout
- `hardware-site/` — the site; its generator scripts live in `hardware-site/tools/`.
  `docs/files/{step,print,drawings,plates,assembly,modules,vendor}/` receive CAD exports;
  download links appear automatically once files are named `<part_id>_rev<NN>.<ext>`.
- `hardware/` — team power and data wiring diagrams (source of truth for electrical pages).
- `reference/bom/` — the team's BOM spreadsheets the `docs/data/*.csv` are generated from.
- `reference/team/` — the team's exploded-view booklet (`duke_humanoid_v2_hardware.pdf`); its pages are the
  site's assembly figures, rendered to `hardware-site/docs/assets/exploded/team/`.
- `_archive/hardware-site-docs-before-slim/` — the verbose pre-slim site, for recovering facts.
- `CAD_RELEASE_COMPARISON.md` — CAD-format analysis (Chinese), for the team.
- `HANDOFF.md` — the single working document: status, the items that block release,
  and the benchmark evidence behind those calls. Read it first. (It absorbed
  `V2_RELEASE_PLAYBOOK.md` on 2026-09-20; that file is gone.)
