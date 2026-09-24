# Bill of materials

Everything to buy for one robot. Quantities and prices are the team's own bill of materials for the reference robot; **Team ref** is the line of that list a row comes from.

## Find a part on the robot

Click **Preview** in any row below to see where that part sits; click a component on the robot to find its row.

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

| Category | Covers | Subtotal |
| --- | --- | --- |
| [Actuators](#actuators) | {{ bom_qty("actuators.csv") }} RobStride units, {{ bom_count("actuators.csv") }} models | {{ bom_subtotal("actuators.csv") }} |
| [Electronics](#electronics) | Computer, battery, power conversion, Controller Area Network (CAN) adapters, inertial measurement unit (IMU), cameras | {{ bom_subtotal("electronics.csv") }} |
| [CNC parts](#cnc-parts) | {{ bom_count("cnc-parts.csv") }} machined parts | {{ bom_subtotal("cnc-parts.csv") }} |
| [Cables and connectors](#cables-and-connectors) | One cable line; connectors, wire, sleeving and heat-shrink are lab consumables, not itemised | {{ bom_subtotal("cables-connectors.csv") }} |
| [Fasteners and hardware](#fasteners-and-hardware) | {{ bom_count("fasteners.csv") }} bearing and screw lines | {{ bom_subtotal("fasteners.csv") }} |
| [Printed parts](#printed-parts) | {{ bom_count("printed-parts.csv") }} rows of fused-deposition (FDM) and laser-sintered (SLS) prints | {{ bom_subtotal("printed-parts.csv") }} |
| **Robot total** | | **{{ bom_total() }}** |

Prices are the team BOM's as of {{ bom_priced_as_of("actuators.csv") }}. The tables as CSV: [actuators](../data/actuators.csv), [electronics](../data/electronics.csv), [cnc-parts](../data/cnc-parts.csv), [printed-parts](../data/printed-parts.csv), [fasteners](../data/fasteners.csv), [cables-connectors](../data/cables-connectors.csv).

{% include "bom/actuators.md" %}

{% include "bom/electronics.md" %}

{% include "bom/cnc-parts.md" %}

{% include "bom/printed-parts.md" %}

{% include "bom/fasteners-and-hardware.md" %}

{% include "bom/cables-and-connectors.md" %}

{% include "bom/sourcing.md" %}
