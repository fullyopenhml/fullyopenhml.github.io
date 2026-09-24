# Actuator sizing in simulation

How the team checked candidate motor configurations in simulation in April 2025, what saturated, and how the result compares with the robot as built.

Nothing on this page is a build instruction, and nothing here can be rerun from
the published repo (see the toolchain box below). The actuators actually fitted
are listed on [Actuators](../bom/actuators.md).

## What the recordings are

**CONSIDERED — NOT USED** (design exploration). The team kept eleven screen
recordings from this study. All are simulation, not hardware: an Isaac Gym viewer
beside PlotJuggler plots, recorded 2025-04-23 and 2025-04-24, plus three debugging
runs dated 2025-04-30 (computed from the on-screen Unix timestamps).

- The 04-23/24 runs plot the joint torque targets of one simulated robot for
  waist, hip_1, hip_2, hip_3, knee, ankle_1 and ankle_2, left and right, on rough
  terrain with other robots training in the distance.
- The 04-30 runs plot three columns (actuation force, reaction force and power)
  for hip 0, hip 1, hip 2, knee, ankle pitch, ankle roll and waist, on a flat
  plane.
- The simulated robot is a simplified model (box torso, flat-plate hands) with no
  camera columns and no grippers.

*Source: the team's 11 gait recordings (window titles, file names, plot panels); team design log, "simulation verification".*

## Five configurations

**CONSIDERED — NOT USED** as a set; see the comparison with the build below.
"Weak" means the smaller motor and "strong" the larger one. Motor numbers are
RobStride models. Every configuration uses the same simulated 6-DoF "weak arm":
shoulder 3 × 03, elbow 03, wrist 03 + 02. Each was recorded walking and
running; the running experiments are named for a stance ratio of 0.5.

| # | Log heading | Leg motors | Design log conclusion (paraphrased) | Recordings |
| --- | --- | --- | --- | --- |
| 1 | weak arm, weak hip, weak knee, weak ankle roll | hip 3 × 03, knee 03, ankle 03 + 02 | Knee and both ankle joints saturate when walking, and the same when running. | walk `..._weak_leg_stance_ratio_05_2025-04-23_14-44-00`; run `..._weak_leg_stance_ratio_05_run_2025-04-24_11-47-49` |
| 2 | weak arm, strong hip, strong knee, weak ankle roll (ticked) | hip 03 × 2 + 04, knee 04, ankle 03 + 02 | Motion looks more natural than (1); both ankle joints show signs of saturation. | walk `v2_baseline_2025-04-23_14-40-10`; run `v2_stance_ratio_05_run_2025-04-24_10-02-18` |
| 3 | weak arm, weak hip, strong knee, weak ankle roll (ticked) | hip 3 × 03, knee 04, ankle 03 + 02 | Similar to (2), "indicating a hip might work fine with all 03 motors for the walking task". | walk `..._weak_hip_2025-04-23_18-53-36`; run `..._weak_hip_stance_ratio_05_run_2025-04-24_11-43-44` |
| 4 | weak arm, weak hip, strong knee, strong ankle roll | hip 3 × 03, knee 04, ankle 03 + 03 | Ankle-roll torque no longer saturates constantly; the leg is more bottom-heavy and the policy learns a pendulum-like walk. | walk `..._strong_ankle_2025-04-24_11-51-31`; run `..._strong_ankle_stance_ratio_05_run_2025-04-24_11-34-45` |
| 5 | weak arm, weak hip, strong knee, weak ankle roll (OFFSET) | as (3), with an offset ankle | Walks "like a blade runner"; the gait looks awkward. The feet appear as narrow blades. | `..._strong_offet_ankle_stance_ratio_05_debug_gait` (see the filename box) |

*Source: team design log, configurations (1)–(5); recording file names. Names shortened with "..." start `v2_debug_weak_arm`.*

The log's "tuned best configuration and gait" is weak arm, weak hip, strong knee,
run once with a weak ankle roll and once with a strong ankle roll (the two
`..._debug_gait_2` recordings, shown below).

## What the plots show (approximate)

**CONSIDERED — NOT USED** (design exploration). Read by eye from the plot axes;
these are approximate plot readings of simulated torque targets, not measured
actuator limits.

- Weak-ankle-roll runs clip the ankle_2 / ankle-roll torque target flat at about
  ±15. The strong-ankle-roll runs swing to about ±40–50 without a flat top.
- Ankle_1 / ankle pitch is flat-topped near ±50 in every run.
- With the 03 knee (configuration 1) the knee target is flat near ±50; with the
  04 knee it peaks near ±100.
- The strong-hip baseline reaches about -80 on hip_1; the weak-hip runs stay
  within about ±50.

These readings agree with the saturation the design log describes.
*Source: PlotJuggler panels in the team recordings.*

<figure markdown>
  <video class="dh-clip" autoplay loop muted playsinline preload="metadata" width="960" height="540"
    poster="../../assets/video/gait-weak-ankle-roll-poster.webp" aria-label="Simulated gait with a weak ankle-roll actuator; ankle-roll torque clips flat"><source src="../../assets/video/gait-weak-ankle-roll.mp4" type="video/mp4"><a href="../../assets/video/gait-weak-ankle-roll.mp4">Simulated gait with a weak ankle-roll actuator; ankle-roll torque clips flat</a></video>
  <figcaption>Simulation (Isaac Gym + PlotJuggler, April 2025): "tuned best" gait, weak arm, weak hip, strong knee, <strong>weak ankle roll</strong>. The ankle-roll torque target clips flat at about ±15. Earlier toolchain, not in the published repo.</figcaption>
</figure>

<figure markdown>
  <video class="dh-clip" autoplay loop muted playsinline preload="metadata" width="960" height="540"
    poster="../../assets/video/gait-strong-ankle-roll-poster.webp" aria-label="Simulated gait with a strong ankle-roll actuator; no clipping"><source src="../../assets/video/gait-strong-ankle-roll.mp4" type="video/mp4"><a href="../../assets/video/gait-strong-ankle-roll.mp4">Simulated gait with a strong ankle-roll actuator; no clipping</a></video>
  <figcaption>Same gait with a <strong>strong ankle roll</strong>: the ankle-roll torque swings about ±40 without clipping. Simulation, April 2025; the as-built ankle_2 is an RS06, which this study did not test.</figcaption>
</figure>

## The study against the robot as built

**AS-BUILT** column from `deploy/control/humanoid_config.py`.

| Joint group | Simulated | As built | Match |
| --- | --- | --- | --- |
| Hip (hip_1, hip_2, hip_3) | 3 × 03 in configurations (3), (4) and the tuned best | R03, R03, R03 | yes |
| Knee | 04 in configurations (2)–(5) | R04 | yes |
| ankle_1 (ankle pitch in the simulation plots) | 03 | R03 | yes |
| ankle_2 (ankle roll in the simulation plots) | 02 (weak) or 03 (strong) | R06 | no: the RS06 was never simulated |
| Arm | 6 DoF: shoulder 3 × 03, elbow 03, wrist 03 + 02 | 7 DoF: R03, R06, R02, R02, R02, R00, R05 | no |

The hip and knee of the finished robot match the "weak hip, strong knee"
conclusion of configurations (3) and (4). The ankle roll and the arm do not match
anything that was simulated. The design log's joint table does list ankle_2 as an
RS06 with a 10 s torque of 27 N·m.

!!! unverified "UNVERIFIED — why the ankle roll and the arm differ from every simulated configuration"
    The gait study tested only 02 and 03 motors on the ankle roll and a 6-DoF
    arm, while the robot has an RS06 on ankle_2 and a 7-DoF arm. The records do
    not say why RS06 was chosen for the ankle roll, or whether the as-built
    ankle and arm were checked in simulation afterwards.

    *Owner: controls lead.*

!!! warning "SUPERSEDED — earlier toolchain; these runs cannot be reproduced from the release"
    The recordings come from an Isaac Gym setup launched through a training
    script that is not in the published repo, with a stance ratio of 0.5. The
    published simulation uses mjlab/MuJoCo, and its gait-phase reward defaults to
    `stance_ratio` 0.55. Treat the study as design history. For the published
    simulation, see [Software](../software.md).

    *Source: team design log, "simulation verification"; `simulation/requirements.txt` and `simulation/mj_envs/tasks/humanoid_velocity/reward.py` in the published repo.*

!!! unverified "UNVERIFIED — offset-ankle recording: file name and log heading disagree"
    The file name says `strong_offet_ankle`. The log heading for configuration
    (5) says "weak ankle roll (OFFSET)" with ankle 03 + 02, and the recording's
    ankle-roll torque clips at about ±15 like the other weak-ankle-roll runs.
    Which ankle motor the run used is not confirmed.

    *Owner: controls lead.*

## Evidence for ankle pitch and roll

**AS-BUILT** naming, evidence from the simulation model. The team's 2025-04-30
plots label leg joint indices 5/11 "ankle pitch" and 6/12 "ankle roll". In the
order of `humanoid_config.py`, indices 5/11 are ankle_1 and 6/12 are ankle_2. The
log's ankle-roll experiments also change only the second ankle motor (02 vs 03).
Together these support ankle_1 = pitch and ankle_2 = roll, but they come from the
April 2025 simulation model, not from the CAD or the built robot. The hip panels
are labelled only hip 0/1/2. The build-side question stays open on
[Leg](../assembly/leg.md).
*Source: plot panel titles in the 2025-04-30 recordings; team design log, configurations (1)–(4).*

## Next: lower-body stable dynamics

**DESIGN GOAL (not as-built).** The log's last section states its goal: "provide
a control that allows the v2 lower body to hold the upper body's pose stable while
the arms complete tasks". Part 1 is to "ensure the real lower body dynamics match
the expected dynamics" (lower-body gravity compensation); part 2 is the "actual
control loop" (stable stand).
*Source: team design log, "Lower Body Stable Dynamics".*

!!! missing "MISSING — lower-body stable dynamics: the subpages are not in the records"
    The section links four subpages (lower-body gravity compensation, stable
    stand, and two others) that are not in the exported design log. What was
    done, and whether it reached the published controller, is not recorded.

    *Owner: controls lead.*
