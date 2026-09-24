# Before you start

Four things to settle before any money is spent: whether the build is safe for
you to attempt, what this release actually hands you, whether you have the skills
and shop access it assumes, and what it will cost in money and in time.

Read [Safety](safety.md) first. It is first in the nav on purpose, and it is the
only page here that can prevent an injury.

<div class="grid cards" markdown>

- **[Safety](safety.md)** — lithium packs, back-drivable legs that collapse on power loss, e-stop doctrine, lifting.
- **[What you get](what-you-get.md)** — the release manifest, artefact by artefact, and what is deliberately out of scope.
- **[Skills and shop access](skills-and-shop.md)** — the machines and the hands this build assumes you already have.
- **[Cost and time](cost-and-time.md)** — what a second build costs, and why there is more than one answer.

</div>

## Go / no-go

Run this before committing. Any unchecked box is a reason to wait rather than a
reason to improvise, and several of them cannot be checked by anybody today.

**Safety and people**

- [ ] You have read [Safety](safety.md) in full, and your institution's safety
      office has seen it.
- [ ] A second person is available for every lift and every powered test.
- [ ] A gantry or hoist rated well above 36 kg is available, with a place to hang
      the robot and clear floor beneath it. **TODO**{ .dh-missing }: the required
      rating is not specified yet — see [Safety](safety.md).
- [ ] Lithium-polymer charging, storage and fire-response procedures exist in
      your space, in writing.
- [ ] An emergency stop can be reached from outside the robot's working envelope.
      **TODO**{ .dh-missing }: no e-stop is in the parts list and the working
      envelope distances are not defined — see [Safety](safety.md).

**Shop and supply**

- [ ] You can have machined parts made, to a tolerance you can inspect.
      **TODO**{ .dh-missing }: no tolerances are published for any machined part.
- [ ] You have FDM printing, and SLS printing or a service bureau.
- [ ] You can solder high-current connectors and crimp signal connectors.
- [ ] You have quoted the long-lead items and can accept the dates.

**Release readiness** — these are about this release, not about you

- [ ] The CAD you need has actually been published. See
      [CAD downloads](../fabrication/cad-downloads.md). **TODO**{ .dh-missing }:
      no robot CAD is published yet.
- [ ] A hardware licence has been declared, so you are permitted to make the
      parts. See [Citation and licence](../reference/citation-and-license.md).
      **TODO**{ .dh-missing }: none has been declared yet.
- [ ] The parts list has no unpriced rows in the subassemblies you are buying.
      See [Bill of materials](../bom/index.md). **TODO**{ .dh-missing }: fasteners
      and printed materials are still unpriced placeholder rows.

!!! missing "MISSING — Budget and calendar thresholds, and the point of no return"
    Two things this checklist still needs before it is trustworthy:

    - A **budget threshold** and a **calendar threshold** a reader can check
      against, which requires the cost and build-time figures to exist first.
    - A **decision point**: at what stage can a builder still stop cheaply? Long-
      lead machining and actuator orders are the point of no return, and a reader
      deserves to be told where it is before they cross it.

    *Owner: hardware lead.*
