# FAQ

Questions a prospective builder asks before committing money or months. Where
there is an answer today, it is here. Where there is not, that is said plainly
rather than filled in.

## Can I build this robot today?

**No.** The CAD is not published (**TODO**{ .dh-missing }), there is no fastener
schedule (**TODO**{ .dh-missing }), no torque values (**TODO**{ .dh-missing }),
no assembly instructions (**TODO**{ .dh-missing }) and no hardware licence
(**TODO**{ .dh-missing }). The
[home page](../index.md) carries the full blocker list and the page each one is
tracked on. That banner comes down when the last blocker does.

## What does it cost?

{{ bom_total() }}
of parts, computed from this site's own data — and that is a floor.
**TODO**{ .dh-missing }: every fastener and every printed part is still a
placeholder rather than a price, and tools, shipping and machining setup fees are
outside it. See
[Cost and time](../before-you-start/cost-and-time.md).

## How long does it take?

**TODO**{ .dh-missing }: unknown. No build-time figure exists for this machine
and none is estimated here. Machining and actuator lead time is expected to
dominate **UNVERIFIED**{ .dh-unverified } — no lead time has been quoted.

## Can I build only the camera gimbal module?

It is the project's headline contribution, so it should be separately buildable
and separately quotable, and the bill of materials is structured to price it on
its own. The only published figure is from the design study: a camera module is
about 0.58 kg, two gimbal DoF and approximately $600 in hardware
**UNVERIFIED**{ .dh-unverified } — an approximate figure from the study, not a
sum of priced rows in this site's data.

!!! missing "MISSING — The camera module's interface for use on another robot"
    Whether a module can be *used* on something other than this robot — its
    mounting interface, its power and its bus requirements — is not documented
    yet.

    *Owner: hardware lead.*

<figure markdown>
  ![Visible-reachable workspace volumes compared across six humanoid platforms](../assets/images/workspace.webp){ loading=lazy }
  <figcaption>
    Why the module is the contribution: visible-reachable workspace measured
    across six humanoid platforms. The mechanism is small, and it is the part of
    this design that does not already exist on a robot you could buy.
  </figcaption>
</figure>

## Why RobStride?

The team's actuator comparison, bench tests and teardown are on
[Actuator selection](../design/actuator-selection.md), including the options
that were considered and not used.

## Why is the knee an RS04?

Two records point the same way. The V2 design goal set the knee torque target
at 80 N·m (KFE), and the RS04's 10 s overload torque in the team's Motor spec
table is 120 N·m, against 55 N·m for the RS03 (comparison computed from the two
tables). In the April 2025 simulation study, the configuration with an RS03 knee
saturated the knee and both ankle joints when walking. The log's "tuned best"
configuration used an RS04 knee with all-RS03 hips (configurations 3 and 4),
which matches the as-built hips and knee.
*Source: team design log, design-spec table, "Motor spec" and "simulation
verification".* See
[Actuator sizing in simulation](../design/actuator-sizing-simulation.md).

Why the ankle roll (ankle_2) is an RS06 is not explained in the team records
**UNVERIFIED**{ .dh-unverified }; the simulation study tried only RS02 and RS03
there.

## Can I substitute the RealSense D436, or the RobStride actuators?

**TODO**{ .dh-missing }: no alternate part is recorded for either, and they are
the two known supply risks in the build. See [Sourcing](../bom/sourcing.md).

## Do I need a 5-axis mill?

**TODO**{ .dh-missing }: unknown. The machined parts have not been characterised
for material, tolerance, finish or machining strategy, so nobody can currently tell you whether a 3-axis
shop is sufficient. See [Skills and shop access](../before-you-start/skills-and-shop.md).

## Do I need a GPU?

Yes, but not on the robot. The onboard computer runs the policy without CUDA; the
cuRobo plan and MPC server runs on a separate CUDA machine. That machine is not
in the robot's parts list, so budget for it separately. See
[Software](../software.md).

## Will the published policy run on my build?

Only if your joint ordering, joint directions and calibration match what the
policy expects — and that contract is not published yet (**TODO**{ .dh-missing }).
It is the largest gap between a finished chassis and a moving robot; see the red
MISSING box on [Software](../software.md).

## What licence is the hardware under?

**TODO**{ .dh-missing }: none has been declared. Apache-2.0 covers the code only. See
[Citation and licence](citation-and-license.md).

## How does this relate to Duke Humanoid V1?

V1 is a different robot and was released under MIT; V2 is Apache-2.0 for its
code. The team compared the two at design-goal level (leg length, leg DoF, mass
and joint torques), and that comparison is on [Revisions](revisions.md). There is
no physical hardware changelog between the two yet (**TODO**{ .dh-missing }).

## Where do I ask for help?

The three repositories have GitHub issue trackers, and that is the only channel
that exists.

!!! missing "MISSING — Issue template, contribution guide and support policy"
    There is no issue template, no contribution guide and no stated response
    policy, so a builder has no way to know what a useful report looks like or
    whether anyone will read it. Two maintainers cannot support an open build
    without saying what they will and will not answer — a one-sided support
    contract, stated up front, is more honest than silence.

    *Owner: PI + hardware lead.*

!!! missing "MISSING — Answers to builder questions that cannot be answered yet"
    Questions that will be asked and cannot be answered yet: what to do when a
    machined part arrives out of tolerance; whether a kit or a partial kit will
    ever be offered; whether the lab will review a build log; and whether anyone
    outside the lab has built one. Today the answer to the last is no.

    *Owner: hardware lead.*
