# Fully Open Humanoid

Three things in one site, at https://fullyopenhml.github.io/:

- **Catalog** (`catalog.html`): open-source humanoids, bipeds and hands scored on nine
  openness criteria, with cost, size, DOF, actuators, licences and sources.
- **Builder** (`builder.html`): mix legs, torso, arms, hands and head across projects;
  get a compatibility checklist (verified / unverified / adapter needed), a merged BOM
  with prices and a sourcing list.
- **Our reference design**: a 23-DOF, 1.1 m humanoid on RobStride actuators and
  3D-printed structure, keeping the joint layout of [Duke Humanoid V2](https://generalroboticslab.github.io/Duke_Humanoid_V2_OpenSource/)
  and the no-machining build of [Berkeley Humanoid Lite](https://berkeley-humanoid-lite.gitbook.io/docs).
  About $5.8k in parts, zero CNC parts, unbuilt.

## Layout

| Path | What |
| --- | --- |
| `index.html`, `design.html`, `viewer.html`, `bom.html`, `printing.html`, `assembly.html`, `electrical.html`, `bringup.html`, `software.html`, `reference.html` | The site: plain HTML, no build step |
| `catalog.html`, `builder.html`, `assets/js/builder.js` | The catalog and the mix-and-match builder, both rendered from `assets/data/catalog.json` |
| `tools/catalog_src.py` | **The catalog.** One dictionary per robot with sources, criteria, families, static modules; `tools/build_catalog.py` merges it with the computed modules of our design and Duke V2 |
| `tools/build_data.py` | **The model.** Every part, joint, price. Writes the three files below |
| `assets/data/robot.json` | Links, joints, part occurrences as primitive solids, catalogue, poses, specs |
| `assets/data/bom.json` | Bill of materials by section and tier |
| `assets/model/foh_v0_2.urdf` | Robot description with masses and inertias |
| `assets/print/` | One STL per printed part plus a zip; `assets/data/print_files.json` is the manifest |
| `tools/build_parts.py` | STL generator (CSG with manifold3d); `tools/check_collisions.py` is the self-collision audit |
| `assets/js/robot-viewer.js` | The CAD-style viewer (three.js from a CDN), builds the robot from `robot.json` |
| `assets/js/site.js`, `assets/css/site.css` | Shared behaviour and styles |
| `Duke_Humanoid_V2_OpenSource/`, `berkeley-humanoid-lite/` | The two parent projects, kept for reference |

## Working on it

```bash
python3 tools/build_data.py          # regenerate robot.json, bom.json and the URDF after any change
python3 tools/check_collisions.py --poses --sweep   # self-collision audit
python3 tools/build_catalog.py       # regenerate catalog.json after editing tools/catalog_src.py
uv venv tools/.venv --python 3.12 && uv pip install --python tools/.venv/bin/python manifold3d trimesh numpy
tools/.venv/bin/python tools/build_parts.py         # regenerate the STLs and the manifest
python3 -m http.server 8000          # then open http://localhost:8000/
```

Change a dimension, a part or a price in `tools/build_data.py`; every page, the
viewer and the URDF follow. Never edit the generated files by hand.

## Status

v0.2 is a design release: kinematics, part list, cost model, wiring, URDF and every printed part as STL.
Nothing has been built yet. The roadmap on the home page lists what each
version adds and which numbers turn from estimates into measurements.

## Licence

Code is MIT (`LICENSE`). Hardware design files and documentation are CC BY 4.0.
See the [reference page](https://fullyopenhml.github.io/reference.html#license).
