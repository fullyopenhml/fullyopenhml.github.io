# Bring-up

Hang the robot from the hoist, legs straight, for the whole chapter; power the 48 V bus from a current-limited bench supply until the acceptance tests say otherwise. Every command runs in `control/` of the [deploy repository](https://github.com/generalroboticslab/duke_humanoid_v2_deploy); install it per its [`SETUP.md`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/docs/SETUP.md), operate per [`OPERATIONS.md`](https://github.com/generalroboticslab/duke_humanoid_v2_deploy/blob/main/control/docs/OPERATIONS.md).

1. [Robot computer setup](#robot-computer-setup)
2. [First power-on](#first-power-on)
3. [Motor ID and config](#motor-id-and-config)
4. [Joint zeroing](#joint-zeroing)
5. [Camera calibration](#camera-calibration)
6. [Acceptance tests](#acceptance-tests)

{% include "bringup/robot-computer-setup.md" %}

{{ step_ns("first-power-on") }}
{% include "bringup/first-power-on.md" %}

{{ step_ns("motor-id-and-config") }}
{% include "bringup/motor-id-and-config.md" %}

{{ step_ns("joint-zeroing") }}
{% include "bringup/joint-zeroing.md" %}

{{ step_ns("camera-calibration") }}
{% include "bringup/camera-calibration.md" %}

{{ step_ns("acceptance-tests") }}
{% include "bringup/acceptance-tests.md" %}
