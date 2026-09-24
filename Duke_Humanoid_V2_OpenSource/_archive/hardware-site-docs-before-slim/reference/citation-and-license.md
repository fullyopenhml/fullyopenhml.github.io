# Citation and licence

How to cite this work, and what you are legally permitted to do with it. The
second half is an open question, and this page presents it as one rather than
implying an answer.

## Citation

The umbrella repository ships a `CITATION.cff`:

| Field | Value |
| --- | --- |
| Title | Duke Humanoid V2: a 31-DoF bipedal platform with two independently actuated camera gimbals, designed around the visible-reachable workspace |
| Type | software |
| Date released | 2026-08-26 |
| Authors | Boxi Xia, Zijiang Yang, Ryan Shin, Bokuan Li, Eric Lu, Jacob Lee, Jiaxun Liu, Boyuan Chen |
| Licence | Apache-2.0 |
| URL | <https://github.com/generalroboticslab/duke_humanoid_v2> |

The project README gives this BibTeX entry:

```bibtex
@misc{duke_humanoid_v2,
  title  = {Visible-Reachable Workspace for Perception-Aware Humanoid Design},
  author = {Boxi Xia and Zijiang Yang and Ryan Shin and Bokuan Li and Eric Lu
            and Jacob Lee and Jiaxun Liu and Boyuan Chen},
  year   = {2026},
  url    = {https://github.com/generalroboticslab/duke_humanoid_v2}
}
```

!!! unverified "UNVERIFIED — The two citation records give different titles"
    The `CITATION.cff` title (*Duke Humanoid V2: a 31-DoF bipedal platform with
    two independently actuated camera gimbals, designed around the
    visible-reachable workspace*) and the README's BibTeX title (*Visible-Reachable
    Workspace for Perception-Aware Humanoid Design*) do not match, although both
    name the same authors, year and URL. Nothing states which title is
    canonical, so two readers citing this work can produce two different
    references. Confirm which one is intended and make the other agree.

    *Owner: PI.*

The preprint is not posted yet (**TODO**{ .dh-missing }).

!!! missing "MISSING — Paper citation, and which record covers the hardware"
    When the paper is public, add its citation here and say which of the two to
    cite for what — the paper for the workspace method and the benchmark results,
    the software record for the robot and the code. A reader who builds the
    hardware should be told which one covers the hardware.

    *Owner: PI.*

## Licence: what is settled and what is not

| Artefact | Licence |
| --- | --- |
| Code — umbrella, simulation, deploy | **Apache-2.0**, settled |
| Hardware design files — CAD, drawings, BOM | **TODO**{ .dh-missing } **Not yet declared** |
| This documentation, and its figures | **TODO**{ .dh-missing } **Not yet declared** |

!!! missing "You currently have no stated permission to make these parts"
    Apache-2.0 is a software licence. It governs the code in the three
    repositories. It does not grant anyone rights in a mechanical design, and it
    is not the instrument anyone uses to release hardware.

    Until a hardware licence is declared, a reader who machines these parts is
    doing so with no stated permission — which makes the release open-source in
    appearance only. This is the cheapest blocker on the whole list to clear, and
    it blocks everything else.

### The decision to make

Three licences, three artefact classes. Only the first is decided.

**Hardware.** The usual instruments are the CERN Open Hardware Licences. The
choice between them is a strategy decision for the lab, not a technical one:

- **CERN-OHL-S** (strongly reciprocal) requires anyone who distributes modified
  hardware to release their design files too. It keeps derivatives open, and it
  deters companies that want to build on the design privately.
- **CERN-OHL-W** (weakly reciprocal) requires reciprocity for the design itself
  but lets it be combined with proprietary parts in a larger product. It is
  friendlier to industrial adoption and gives up some of the guarantee.
- A permissive option or a Creative Commons licence is also possible. Note that a
  **non-commercial** clause — the route one comparable project took — makes the
  design unusable by anyone selling kits, which is usually the opposite of what a
  lab wants from an open hardware release.

**Documentation.** CC-BY-4.0 is the normal answer for prose and figures, and it
is what the comparable projects that got this right use for their docs.

!!! missing "MISSING — Hardware and documentation licences"
    - Choose and declare the **hardware licence**, then put the licence file in
      the repository beside the CAD, not only in a web page.
    - Choose and declare the **documentation licence** for this site.
    - Re-state the hardware licence **on the CAD download page itself**, where a
      reader is about to download files. A licence does not travel with a
      downloaded STEP file, so the statement has to be where the download is.
      See [CAD downloads](../fabrication/cad-downloads.md).
    - State the **V1 (MIT) → V2 (Apache-2.0)** change, so downstream users do not
      assume the V1 terms carry over. See [Revisions](revisions.md).

    *Owner: PI + the university's licensing office. Blocks the release.*

## Third-party material

Two things a downstream user must know about the assets shipped alongside the
robot model, both stated in the project README's acknowledgements:

- The comparison platforms used in the workspace study are third-party models
  redistributed under their own licences. Most are Apache-2.0 or MIT — **the
  Fourier GR-3 model is GPL-3.0**, which the README calls out in bold along with
  a one-line instruction for removing it if that matters for your use. It is a
  comparison column in the workspace figures and nothing depends on it.
- The README states that each third-party asset keeps its upstream `LICENSE`
  beside its meshes. That is not true of every directory: the Unitree G1 assets
  ship as two URDF files with no licence file, and the acknowledgements table
  points elsewhere for their terms. G1 is the study's primary baseline, so this
  is worth resolving rather than leaving to the reader.

!!! missing "MISSING — Licence file for the Unitree G1 assets"
    The Unitree G1 licence question described above is unresolved: the two G1
    URDF files have no licence file beside them. Either add the licence file, or
    correct the README's statement and say where the G1 terms are.

    *Owner: PI.*

### Third-party sources cited, not redistributed

The Design section and the build pages cite these sources. None is copied onto
this site, and no figure from them is reproduced; get them from their
publishers.

- Frigo et al. (1996), "Moment-angle relationship at lower limb joints during
  human walking at different velocities", *J. Electromyogr. Kinesiol.* 6(3):177–190.
- Winter (1983), "Moments of force and mechanical power in jogging",
  *J. Biomech.* 16(1):91–97.
- Belli et al. (2002), "Moment and power of lower limb joints in running",
  *Int. J. Sports Med.* 23(2):136–141,
  [DOI 10.1055/s-2002-20136](https://doi.org/10.1055/s-2002-20136).
- Simonsen et al. (1997), "Mechanisms contributing to different joint moments
  observed during human walking", *Scand. J. Med. Sci. Sports*,
  [DOI 10.1111/j.1600-0838.1997.tb00110.x](https://doi.org/10.1111/j.1600-0838.1997.tb00110.x).
- RobStride 02, 03 and 04 product manuals (RobStride,
  [robstride.com/download](https://www.robstride.com/download)).
- SYD Dynamics TransducerM user guide (SYD Dynamics,
  [download centre](https://syd-dynamics.com/download-center)).
- Amass XT30(2+2)-F.G.B connector datasheet (Changzhou Amass Electronics).
- maxon support article
  ["CAN bus topology and bus termination"](https://support.maxongroup.com/hc/en-us/articles/360009241840-CAN-bus-topology-and-bus-termination).

The team's raw design log is not published either; see
[What you get](../before-you-start/what-you-get.md#what-is-deliberately-not-included).

!!! missing "MISSING — Third-party terms on purchased components and vendor-derived CAD"
    For the **hardware** side specifically, which this site is about:

    - List every purchased component whose own terms a builder should know about —
      vendor SDKs, firmware, and anything shipped under a EULA.
    - Confirm that no part of the published CAD is derived from a vendor model
      that cannot be redistributed. Actuator and camera mounting geometry is the
      usual place this goes wrong: a mount modelled around a vendor's STEP file
      may carry that file's terms.

    *Owner: hardware lead.*
