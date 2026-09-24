# CAD downloads

Download the whole robot, one module, or one part. Part files are named `<part_id>_rev<NN>`, matching the parts lists; left and right parts are separate files.

## Find a part on the robot

<div class="dh-viewer-block">
<model-viewer id="dh-viewer" data-base="../" src="../assets/viewer/robot.glb" camera-controls
  camera-orbit="35deg 75deg auto" min-camera-orbit="auto auto 0.3m" max-camera-orbit="auto auto 6m"
  interaction-prompt="none" shadow-intensity="0.6" exposure="1.1" loading="eager"
  alt="Duke Humanoid V2, every component in its Fusion 360 appearance">
  <button slot="hotspot-x" class="dh-axis dh-axis-x" type="button" tabindex="-1" data-position="0m 0m 0m" aria-label="X axis">X</button>
  <button slot="hotspot-y" class="dh-axis dh-axis-y" type="button" tabindex="-1" data-position="0m 0m 0m" aria-label="Y axis">Y</button>
  <button slot="hotspot-z" class="dh-axis dh-axis-z" type="button" tabindex="-1" data-position="0m 0m 0m" aria-label="Z axis">Z</button>
</model-viewer>
<div class="dh-viewer-bar">
  <button id="dh-viewer-reset" class="md-button" type="button">Show all</button>
  <span class="dh-viewer-legend"><span>Colours are the Fusion appearances</span><span><i class="dh-sw-amber"></i>hovered row</span><span><i class="dh-sw-red"></i>selected on the model</span><span><i class="dh-sw-blue"></i>selected row</span></span>
  <div id="dh-viewer-info" hidden></div>
</div>
<p class="dh-viewer-note">Axes are the STEP file axes (right-handed, Z up).</p>
</div>

Click **Preview** in a row to see a part on the robot; click a component on the robot to jump to its row. **Hide selected** removes the selected part from view; **Show all** resets.

## Files

### Whole robot

Assembly STEP (zipped: over GitHub's file-size limit) and the Fusion 360 archive for editing. All STEP files are AP214, written by Fusion 360 from the `humanoid_2.1_latest` design.

{{ cad_table("assembly") }}

| File | Size | SHA-256 |
| --- | ---: | --- |
| [humanoid_2.1_latest.f3z](https://github.com/generalroboticslab/Duke_Humanoid_V2_OpenSource/releases/download/cad-v2.1-rc1/humanoid_2.1_latest.f3z) (101 linked designs included, release `cad-v2.1-rc1`) | 319 MB | `f440621df68f0775f521c87d02f8a644ae0a65f64ef76b385fdd2bc22a04d420` |

### Modules

One STEP per sub-assembly, parts assembled, in the sub-assembly's own coordinates. Depth 0 is directly under the robot.

??? note "Module files ({{ cad_count("modules") }})"
    {{ cad_table_modules() | indent(4) }}

### Parts

One file per component, in the component's own coordinates.

??? note "Machined and printed parts — STEP ({{ cad_count("step") }})"
    {{ cad_table("step") | indent(4) }}

??? note "Printable meshes — STL ({{ cad_count("print") }}); units are millimetres"
    {{ cad_table("print") | indent(4) }}

??? note "Purchased parts — vendor STEP ({{ cad_count("vendor") }}); for fit checks only, buy the parts"
    {{ cad_table("vendor", "Component") | indent(4) }}

### Drawings

The overall-dimension drawing and the exploded-view booklet, whose part labels are the team BOM ids used in the parts lists and on [Assembly](../assembly/index.md). There are no per-part drawings: machined parts are ordered from the STEP files.

{{ cad_table("drawings") }}

Everything ships under [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) ([`LICENSE`](../files/LICENSE){ download="" }).

Checksums: [SHA256SUMS.txt](../files/SHA256SUMS.txt){ download="" } (`shasum -a 256 <file>`).
