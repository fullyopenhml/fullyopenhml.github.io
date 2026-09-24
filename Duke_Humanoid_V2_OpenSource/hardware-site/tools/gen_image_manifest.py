"""Generate IMAGES_NEEDED.md (site root, not published) — every image the site needs and lacks.

The site marks a missing figure with a blockquote placeholder rather than a real
``![](…)``, because ``mkdocs build --strict`` fails the whole build on a link to
an image that does not exist. This script reads those placeholders back out,
adds the figures named on pages that have no placeholder yet, and expands the
per-part families from the BOM CSVs, so the manifest is a derived artefact
rather than a list somebody has to remember to update.

Usage:  python tools/gen_image_manifest.py
"""

from __future__ import annotations

import csv
import os
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
DOCS = SITE / "docs"
OUT = SITE / "IMAGES_NEEDED.md"
SKIP = {"data/README.md", "reference/todo.md", "assets/MANIFEST.md"}


def extract_figures() -> dict[str, dict]:
    """Figure placeholders and figure-manifest table rows, path -> brief."""
    out: dict[str, dict] = {}
    for root, _, files in os.walk(DOCS):
        for fn in sorted(files):
            if not fn.endswith(".md"):
                continue
            path = Path(root) / fn
            rel = path.relative_to(DOCS).as_posix()   # '/' on every OS; SKIP uses '/'
            if rel in SKIP or rel.startswith("data/"):
                continue
            txt = path.read_text(encoding="utf-8")
            for m in re.finditer(r"((?:^>.*\n)+)", txt, re.M):
                blk = m.group(1)
                if "pending-figure" not in blk:
                    continue
                flat = " ".join(l.lstrip("> ").rstrip() for l in blk.strip().split("\n"))
                fm = re.search(r"`(assets/[^`]+)`\s*:?\s*(.*)$", flat)
                if not fm:
                    continue
                out.setdefault(fm.group(1), {
                    "page": rel, "desc": re.sub(r"\s+", " ", fm.group(2)).strip()})
            for m in re.finditer(r"^\|\s*`(assets/[^`]+)`\s*\|([^|]*)\|([^|]*)\|", txt, re.M):
                e = out.setdefault(m.group(1), {"page": rel, "desc": m.group(3).strip()})
                if not e["desc"]:
                    e["desc"] = m.group(3).strip()
    return out


def part_ids(csv_name: str) -> list[str]:
    path = DOCS / "data" / csv_name
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return [r["part_id"] for r in csv.DictReader(fh) if r["part_id"].strip()]


figs = extract_figures()
cnc, elec, act = part_ids("cnc-parts.csv"), part_ids("electronics.csv"), part_ids("actuators.csv")

# figures referenced by a page, minus the illustrative template
placed = {k: v for k, v in figs.items() if "<page>" not in k}

EXTRA = [
 # (path, page that will use it, brief)
 ("assets/images/camera-module.png", "index.md, reference/faq.md",
  "One camera gimbal module alone, off the robot, dimensioned — so it can be judged as a component by someone who wants only the module."),
 ("assets/images/safety-pinch-points.png", "fabrication/safety.md",
  "The robot with every pinch point marked on the real link geometry: between limb and torso, inside each joint, and the jaw closing line."),
 ("assets/images/safety-lifting-points.png", "fabrication/safety.md, assembly/final-integration.md",
  "The sanctioned lifting points marked on the machine, with the sling route drawn, and the places that look like handles but are not."),
 ("assets/images/safety-hanging-legs-straight.png", "fabrication/safety.md",
  "The robot correctly suspended with the legs hanging straight, next to the same robot hung wrong with the legs bent. Three bring-up sessions were lost to this exact mistake; the pair of images is the whole lesson."),
 ("assets/bom/fasteners/fastener-size-chart.png", "bom/fasteners-and-hardware.md",
  "One-page visual size chart for every fastener in the build, printed 1:1 so a screw can be laid on the page and identified. Blocked on the fastener schedule existing at all."),
 ("assets/electrical/system-wiring-diagram.svg", "electrical/index.md",
  "Every load, rail, bus and connector on one sheet. The single most valuable missing artefact in the Electrical section."),
 ("assets/electrical/power-tree.svg", "electrical/power-system.md",
  "Packs, their series/parallel configuration, each converter, each rail and what it feeds, with the fusing and the disconnect drawn where they belong."),
 ("assets/electrical/connector-xt30-2p2-pinout.svg", "electrical/harness-fabrication.md",
  "XT30(2+2) pinout drawn from the mating face, with the orientation feature and the wire-colour convention."),
 ("assets/electrical/connector-actuator-pinout.svg", "electrical/harness-fabrication.md",
  "Actuator connector pinout from the mating face, both halves, with the mating part number."),
 ("assets/electrical/connector-gripper-servo-pinout.svg", "electrical/harness-fabrication.md",
  "Gripper servo connector pinout from the mating face, both halves."),
 ("assets/electrical/routing-leg.jpg", "electrical/routing.md, assembly/leg.md",
  "Photograph of the finished leg routing before the shank closes, every clamp point visible. Prose does not transfer a routing decision."),
 ("assets/electrical/routing-arm.jpg", "electrical/routing.md, assembly/arm.md",
  "Photograph of the finished arm routing, showing the service loop at the shoulder and at the wrist."),
 ("assets/electrical/routing-waist.jpg", "electrical/routing.md, assembly/torso-and-waist.md",
  "Photograph of the waist crossing, the one place a bus spans three subassemblies."),
 ("assets/electrical/routing-torso.jpg", "electrical/routing.md, assembly/torso-and-waist.md",
  "Photograph of the torso interior with the computer, converters, CAN adapters and packs installed and the harness dressed."),
 ("assets/electrical/routing-camera-gimbal.jpg", "electrical/routing.md, assembly/head-and-camera-gimbal.md",
  "Photograph of the camera cable through a gimbal column at both yaw extremes, showing the loop and every retention point. The cable across the yaw axis is the highest-risk routing on the robot."),
 ("assets/electrical/routing-gripper.jpg", "electrical/routing.md, assembly/gripper.md",
  "Photograph of the gripper servo cable and its strain relief at the wrist."),
 ("assets/bringup/zero-pose-front.jpg", "bringup/joint-zeroing.md",
  "The reference robot held in the zero pose, front view, with the mechanical feature that defines each joint's zero called out."),
 ("assets/bringup/zero-pose-side.jpg", "bringup/joint-zeroing.md",
  "The same zero pose from the side. Two views are the minimum: one view cannot show both pitch and roll zeros."),
 ("assets/bringup/joint-direction-convention.svg", "bringup/motor-id-and-config.md",
  "Every joint with its positive direction drawn as an arrow on the real geometry. A backwards joint passes every other check in the site."),
 ("assets/bringup/tag-cube-wrist-mounting.jpg", "bringup/camera-calibration.md",
  "The tag cube mounted on the wrist interface, with the tag family, tag size and orientation visible. Without this fixture the robot cannot be calibrated."),
 ("assets/fabrication/cad-release-assets.png", "fabrication/cad-downloads.md",
  "Screenshot of a tagged release page with the CAD archives attached, so a reader knows what a correct release looks like when they see one."),
 ("assets/fabrication/printed-parts-orientation.png", "fabrication/printing-guide.md",
  "Each structural printed part shown in its validated print orientation, with the load direction the layer lines must not align with drawn on it."),
 ("assets/fabrication/heat-set-insert-seated.jpg", "fabrication/printing-guide.md",
  "A heat-set insert correctly seated, next to one pressed in too far and one left proud."),
]

FAMILIES = [
 ("assets/bom/cnc/<part_id>.png", len(cnc), "bom/cnc-parts.md",
  "One render per machined part, filename exactly the `part_id` in `cnc-parts.csv`. A machined part a builder cannot see is a part they will order wrong.", cnc),
 ("assets/bom/electronics/<part_id>.jpg", len(elec), "bom/electronics.md",
  "One photograph per bought electronic part, filename exactly the `part_id` in `electronics.csv`, so a builder can confirm the thing in the box is the thing on the list.", elec),
 ("assets/bom/actuators/<part_id>.jpg", len(act), "bom/actuators.md",
  "One photograph per Robstride model, filename exactly the `part_id` in `actuators.csv`. The models look alike and are not interchangeable.", act),
]

fam_total = sum(f[1] for f in FAMILIES)
total = len(placed) + len(EXTRA) + fam_total

# Pages of the team's exploded-view booklet
# (docs/files/drawings/duke_humanoid_v2_exploded_views_rev01.pdf), rendered one
# image per page. These are the exploded views the manifest used to list as
# missing: they are delivered, labelled with the team BOM ids, and placed.
# Pages 7, 8 and 12 are not published as figures — 8 and 12 carry only the
# "switch A <-> B" mirror note, which the leg and arm pages state in words.
TEAM_EXPLODED = [
 ("01-torso-frame.webp", "assembly/torso-and-waist.md",
  "Torso frame: plates C0–C3, spine P0, actuators E3, bearings H0."),
 ("02-electronics-tray.webp", "assembly/torso-and-waist.md",
  "Torso electronics: E0, E7, E13, E16, E17, E18, E19, E20."),
 ("03-torso-printed-plates.webp", "assembly/torso-and-waist.md",
  "Printed torso plates P1–P3."),
 ("04-leg-upper.webp", "assembly/leg.md",
  "Hip pitch and roll: C4–C8, actuators E3, bearings H0."),
 ("05-leg-lower.webp", "assembly/leg.md",
  "Hip yaw to foot plate: C4, C5, C9–C21, actuators E3, E4, E6, bearings H0–H3."),
 ("06-leg-covers.webp", "assembly/leg.md", "Printed leg covers P20–P32."),
 ("09-arm.webp", "assembly/arm.md",
  "Right arm: C5, C22–C29, P4–P8, actuators E1, E2, E5, E6, bearings H2, H4."),
 ("10-arm-covers.webp", "assembly/arm.md", "Printed arm covers P33–P39."),
 ("11-torso-p9.webp", "assembly/arm.md",
  "Left arm, with the left wrist housing P9 in place of the right housing P7."),
 ("13-gripper.webp", "assembly/gripper.md",
  "One gripper: P10–P15, servo E15, driver board E10, converter E12."),
 ("14-camera-gimbal.webp", "assembly/head-and-camera-gimbal.md",
  "One camera column: P16–P19, actuators E5, camera E14, bearing H5."),
 ("15-whole-robot.webp", "index.md, assembly/index.md",
  "The robot with both camera columns and both grippers lifted off."),
]

HAVE = [
 ("assets/images/teaser.webp", "index.md", "The robot in simulation and on hardware, side by side."),
 ("assets/images/hardware.webp", "index.md", "Hardware overview with all joints numbered and the three modules labelled."),
 ("assets/images/hardware_tracking.mp4", "index.md", "The reference robot tracking two independently moving targets."),
 ("assets/images/vrw_fixed_vs_actuated.mp4", "index.md", "Visible-reachable workspace, fixed head versus actuated camera modules."),
 ("assets/images/hardware_close_front_back.mp4", "assembly/head-and-camera-gimbal.md", "The two finished camera modules aiming independently."),
 ("assets/images/two_target_handoff_left_right.mp4", "bringup/acceptance-tests.md", "What passing acceptance test A10 looks like."),
 ("assets/images/workspace.webp", "reference/faq.md", "Visible-reachable workspace across six humanoid platforms."),
] + [
 (f"assets/exploded/team/{p}", page, desc) for p, page, desc in TEAM_EXPLODED
]

L=[]; w=L.append
w("# Image manifest")
w("")
w("Every image this site needs and does not have, with the exact path it must be")
w(f"saved to and one line on what it must show. **{total} images are missing.**")
w("")
w("This is the list to hand to whoever renders the remaining figures. It is not")
w("a wish list: each path below is already named on a page, so dropping a file")
w("at that path is all that is needed — no page has to be rewritten to accept it.")
w("")
w('!!! warning "Why no page shows a broken image"')
w("    `mkdocs build --strict` fails on a link to an image that does not exist, so")
w("    a placeholder cannot be a real `![](…)`. Pages mark a missing figure as a")
w("    blockquote instead:")
w("")
w("    ```markdown")
w('    > **Figure** <span class="pending-figure">not produced yet</span> —')
w("    > `assets/assembly/leg-step-02.png`: what the render must show.")
w("    ```")
w("")
w("    When the file lands, swap those three lines for the image and delete the")
w("    row from this manifest. Both happen in the same commit or neither does.")
w("")
w("## What to produce first")
w("")
steps = sum(1 for k in placed if re.search(r"-step-", k))
prio = []
if steps:
    prio.append((f"The {steps} step renders",
                 "Written steps without a figure are the site's largest readability gap"))
else:
    prio.append(("Step renders, `assets/assembly/<page>-step-NN.png`",
                 "Not one exists, and not one is named on a page yet. A step with no figure is the "
                 "site's largest readability gap"))
prio.append(("The 6 routing photographs",
             "A routing decision does not survive being written down. These must be taken during a "
             "build, not reconstructed after one"))
prio.append(("Everything else", "—"))
w("| Priority | What | Why it is first |")
w("| --- | --- | --- |")
for i, (what, why) in enumerate(prio, 1):
    w(f"| {i} | {what} | {why} |")
w("")
w("The whole-robot and subassembly exploded views are no longer on this list:")
w(f"the team's exploded-view booklet delivers {len(TEAM_EXPLODED)} of them, labelled with the")
w("team BOM ids and placed on the Assembly pages.")
w("")
w("## Format and size")
w("")
w("| | |")
w("| --- | --- |")
w("| CAD renders, diagrams | `.png`, or `.svg` for anything with text in it. Long edge 1600 px, transparent or white background |")
w("| Photographs | `.jpg`, long edge 2000 px, under 500 KB. The part in focus, the rest of the bench not |")
w("| Wiring and pinout drawings | `.svg` — they will be read at 200% and they will be corrected |")
w("| Anything animated | `.webp`. Keep it under 5 MB; the existing demo loops are the ceiling, not the target |")
w("")
w("Filenames are lowercase with hyphens, except the per-part families below, whose")
w("filenames must match a `part_id` character for character so the page can find")
w("them without a lookup table.")
w("")
w(f"## Missing — referenced by a page ({len(placed)})")
w("")
w("Each of these already has a placeholder blockquote on the page named.")
w("")
w("| Path | Page | What it must show |")
w("| --- | --- | --- |")
for k in sorted(placed):
    v = placed[k]
    d = v["desc"].rstrip(".").replace("|", "/")
    d = d[0].upper() + d[1:] if d else "—"
    w(f"| `{k}` | `{v['page']}` | {d} |")
w("")
w(f"## Missing — named on a page but not yet placed ({len(EXTRA)})")
w("")
w("These are named in a TODO block or an image manifest but have no placeholder")
w("in the page body yet; add the placeholder in the commit that adds the file.")
w("")
w("| Path | Page that will use it | What it must show |")
w("| --- | --- | --- |")
for p, page, d in EXTRA:
    w(f"| `{p}` | `{page}` | {d} |")
w("")
w(f"## Missing — per-part families ({fam_total})")
w("")
w("One image per row of a BOM CSV. The filename **is** the `part_id`, so these")
w("can be produced in a batch and dropped in without touching a page.")
w("")
w("| Path pattern | Count | Page | What each must show |")
w("| --- | ---: | --- | --- |")
for pat, n, page, d, _ in FAMILIES:
    w(f"| `{pat}` | {n} | `{page}` | {d} |")
w("")
for pat, n, page, d, lst in FAMILIES:
    w(f'??? note "The {n} filenames for `{pat}`"')
    w("")
    for i in lst:
        w(f"    - `{i}`")
    w("")
w(f"## Already here ({len(HAVE)})")
w("")
w("Photographs and clips of the reference robot from the project repository's")
w("`media/` directory, plus the pages of the team's exploded-view booklet")
w("(`files/drawings/duke_humanoid_v2_exploded_views_rev01.pdf`), one image per")
w("page, labelled with the team BOM ids. None of these replaces a step render.")
w("")
w("| Path | Used on | What it shows |")
w("| --- | --- | --- |")
for p, page, d in HAVE:
    w(f"| `{p}` | `{page}` | {d} |")
w("")
w("## Counting")
w("")
w("| | |")
w("| --- | ---: |")
w(f"| Referenced by a page, missing | {len(placed)} |")
w(f"| Named on a page, not yet placed | {len(EXTRA)} |")
w(f"| Per-part families | {fam_total} |")
w(f"| **Missing, total** | **{total}** |")
w(f"| Present | {len(HAVE)} |")
w("")
w("## Regenerating this page")
w("")
w("Derived from the placeholders on the pages and from the BOM CSVs, not")
w("maintained by hand:")
w("")
w("```console")
w("$ python tools/gen_image_manifest.py")
w("```")
w("")
w("The per-part families come from `part_id` columns, so a new row in")
w("`cnc-parts.csv` adds its render to this list automatically. Figures that are")
w("named on a page but have no placeholder yet are the one hand-maintained part,")
w("in the `EXTRA` table at the top of that script.")
w("")
OUT.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
print(f"{OUT.relative_to(SITE).as_posix()}: {total} images missing "
      f"({len(placed)} placed, {len(EXTRA)} named, {fam_total} per-part)")
