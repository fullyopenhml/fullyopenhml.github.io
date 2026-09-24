# Citation and licence

```bibtex
@misc{duke_humanoid_v2,
  title  = {Visible-Reachable Workspace for Perception-Aware Humanoid Design},
  author = {Boxi Xia and Zijiang Yang and Ryan Shin and Bokuan Li and Eric Lu
            and Jacob Lee and Jiaxun Liu and Boyuan Chen},
  year   = {2026},
  url    = {https://github.com/generalroboticslab/duke_humanoid_v2}
}
```

The umbrella repository's `CITATION.cff` is the machine-readable form.

| Artefact | Licence |
| --- | --- |
| Code (umbrella, simulation, deploy) | [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) |
| Hardware design files (CAD, drawings, BOM) | Apache-2.0 ([`LICENSE`](../files/LICENSE){ download="" } ships with the CAD) |
| This documentation and its figures | Apache-2.0 |

Vendored in `deploy/control/hardware_bindings/`: the FEETECH serial servo SDK (MIT, `ft_servo/NOTICE.md`) and the SYD Dynamics EasyProfile SDK (BSD-2-Clause, `imu/EasyProfile/NOTICE.md`). Vendor manuals (RobStride, SYD Dynamics, Amass) are linked, not redistributed.
