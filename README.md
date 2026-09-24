# Fully Open Humanoid

A 23-DOF, 1.1 m humanoid on RobStride actuators and 3D-printed structure.
It keeps the joint layout of [Duke Humanoid V2](https://generalroboticslab.github.io/Duke_Humanoid_V2_OpenSource/)
and the no-machining build of [Berkeley Humanoid Lite](https://berkeley-humanoid-lite.gitbook.io/docs).
About $5.6k in parts, zero CNC parts.

**Site:** https://fullyopenhml.github.io/ — design, interactive 3D model, bill of
materials, printing, assembly, electrical, bring-up, software, reference.

## Layout

| Path | What |
| --- | --- |
| `index.html`, `design.html`, `viewer.html`, `bom.html`, `printing.html`, `assembly.html`, `electrical.html`, `bringup.html`, `software.html`, `reference.html` | The site: plain HTML, no build step |
| `tools/build_data.py` | **The model.** Every part, joint, price. Writes the three files below |
| `assets/data/robot.json` | Links, joints, part occurrences as primitive solids, catalogue, poses, specs |
| `assets/data/bom.json` | Bill of materials by section and tier |
| `assets/model/foh_v0_1.urdf` | Robot description with masses and inertias |
| `assets/js/robot-viewer.js` | The CAD-style viewer (three.js from a CDN), builds the robot from `robot.json` |
| `assets/js/site.js`, `assets/css/site.css` | Shared behaviour and styles |
| `Duke_Humanoid_V2_OpenSource/`, `berkeley-humanoid-lite/` | The two parent projects, kept for reference |

## Working on it

```bash
python3 tools/build_data.py          # regenerate robot.json, bom.json and the URDF after any change
python3 -m http.server 8000          # then open http://localhost:8000/
```

Change a dimension, a part or a price in `tools/build_data.py`; every page, the
viewer and the URDF follow. Never edit the generated files by hand.

## Status

v0.1 is a design release: kinematics, part list, cost model, wiring and URDF.
Nothing has been built yet. The roadmap on the home page lists what each
version adds and which numbers turn from estimates into measurements.

## Licence

Code is MIT (`LICENSE`). Hardware design files and documentation are CC BY 4.0.
See the [reference page](https://fullyopenhml.github.io/reference.html#license).
