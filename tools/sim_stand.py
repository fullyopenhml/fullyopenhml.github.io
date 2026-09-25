#!/usr/bin/env python3
"""Physics check: does the robot stand?  MuJoCo simulation of the generated URDF.

Loads assets/model/foh_v0_2.urdf, gives it a floating base, a floor and one
position-controlled actuator per joint with the real peak-torque limits, then
runs the tests below and reports numbers (and frames, when a renderer is available):

  stand   drop from 10 mm at the zero pose, hold it for 5 s
  crouch  ramp to the crouch pose (hip -35, knee 70, ankle -35 deg), hold, return
  push    while standing, push the torso forward with 4 to 12 N.s impulses (0.2 s)

Pass criteria are printed with every number.  Gains here are simulation gains
for stiff position control; the real actuators' MIT-mode gains are tuned later.

Run:  tools/.venv/bin/python tools/sim_stand.py [--render]
Writes assets/data/sim_results.json and, with --render, assets/img/sim/*.png.
"""
from __future__ import annotations

import argparse
import json
import math
import signal
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
URDF = ROOT / "assets/model/foh_v0_2.urdf"
robot = json.loads((ROOT / "assets/data/robot.json").read_text())
PEAK = {m: a["peak_nm"] for m, a in robot["actuators"].items()}
GAINS = {"RS03": (220.0, 9.0), "RS06": (150.0, 6.0), "RS02": (80.0, 3.0), "RS05": (25.0, 1.0)}   # kp N.m/rad, kd N.m.s/rad
JOINT_MODEL = {j["id"]: j["actuator"] for j in robot["joints"]}
CROUCH = {"hip_pitch_L": -35, "hip_pitch_R": -35, "knee_L": 70, "knee_R": 70, "ankle_pitch_L": -35, "ankle_pitch_R": -35}


def build(dt=0.002):
    spec = mujoco.MjSpec.from_file(str(URDF))
    spec.option.timestep = dt
    root = spec.worldbody.first_body()
    root.add_freejoint()
    floor = spec.worldbody.add_geom(name="floor", type=mujoco.mjtGeom.mjGEOM_PLANE, size=[5, 5, 0.1], friction=[1.0, 0.005, 0.0001])
    # name collision geoms after their body so contacts are readable
    for b in spec.bodies:
        for i, g in enumerate(b.geoms):
            if not g.name:
                g.name = f"{b.name}#{i}"
    for j in spec.joints:
        if j.type != mujoco.mjtJoint.mjJNT_HINGE:
            continue
        model = JOINT_MODEL[j.name]
        kp, kd = GAINS[model]
        j.armature = 0.02
        a = spec.add_actuator(name=j.name)
        a.trntype = mujoco.mjtTrn.mjTRN_JOINT
        a.target = j.name
        a.gaintype = mujoco.mjtGain.mjGAIN_FIXED
        a.biastype = mujoco.mjtBias.mjBIAS_AFFINE       # PD position servo: force = kp*(ctrl - q) - kd*qdot
        g = np.zeros(10); g[0] = kp
        b = np.zeros(10); b[1] = -kp; b[2] = -kd
        a.gainprm = g
        a.biasprm = b
        a.forcerange = [-PEAK[model], PEAK[model]]
        a.ctrlrange = [j.range[0], j.range[1]]
    spec.visual.global_.offwidth = 1280
    spec.visual.global_.offheight = 800
    m = spec.compile()
    return m


def tilt_deg(q):
    w, x, y, z = q
    # angle between body z-axis and world z-axis
    zz = 1 - 2 * (x * x + y * y)
    return math.degrees(math.acos(max(-1.0, min(1.0, zz))))


class Sim:
    def __init__(self, render=False):
        self.m = build()
        self.d = mujoco.MjData(self.m)
        self.torso = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_BODY, "torso")
        self.act_names = [mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_ACTUATOR, i) for i in range(self.m.nu)]
        self.renderer = None
        if render:
            try:
                signal.alarm(90)
                self.renderer = mujoco.Renderer(self.m, 540, 720)
                self.cam = mujoco.MjvCamera()
                self.cam.distance = 1.75
                self.cam.elevation = -12
                self.cam.azimuth = 135
                self.cam.lookat[:] = [0, 0, 0.52]
                signal.alarm(0)
            except Exception as e:  # noqa: BLE001
                signal.alarm(0)
                print("  renderer unavailable:", e)
        self.reset()

    def reset(self):
        mujoco.mj_resetData(self.m, self.d)
        self.d.qpos[2] = 0.01          # 10 mm above the floor
        self.d.qpos[3:7] = [1, 0, 0, 0]
        self.d.ctrl[:] = 0
        mujoco.mj_forward(self.m, self.d)

    def targets(self, pose_deg):
        for i, n in enumerate(self.act_names):
            self.d.ctrl[i] = math.radians(pose_deg.get(n, 0.0))

    def step(self, seconds, log, push=None):
        n = int(seconds / self.m.opt.timestep)
        for k in range(n):
            if push and push[0] <= self.d.time < push[1]:
                self.d.xfrc_applied[self.torso, :3] = push[2]
            else:
                self.d.xfrc_applied[self.torso, :] = 0
            mujoco.mj_step(self.m, self.d)
            if k % 5 == 0:
                log.append(dict(t=self.d.time, z=float(self.d.qpos[2]), tilt=tilt_deg(self.d.qpos[3:7]),
                                tau={n_: float(f) for n_, f in zip(self.act_names, self.d.actuator_force)},
                                com=self.d.subtree_com[1].copy()))

    def frame(self, path):
        if not self.renderer:
            return
        self.renderer.update_scene(self.d, camera=self.cam)
        img = self.renderer.render()
        try:
            from PIL import Image
            Image.fromarray(img).save(path)
        except Exception as e:  # noqa: BLE001
            print("  frame save failed:", e)


def summarize(log, name, t_from=0.0):
    seg = [r for r in log if r["t"] >= t_from]
    peak = {}
    for r in seg:
        for j, tau in r["tau"].items():
            model = JOINT_MODEL[j]
            key = j.replace("_L", "").replace("_R", "")
            peak[key] = max(peak.get(key, 0.0), abs(tau))
    worst = {}
    for key, tau in peak.items():
        model = JOINT_MODEL[key + "_L"] if key + "_L" in JOINT_MODEL else JOINT_MODEL[key]
        worst[key] = dict(peak_nm=round(tau, 1), limit_nm=PEAK[model], ratio=round(tau / PEAK[model], 2))
    last = seg[-1]
    return dict(name=name, final_z_mm=round(last["z"] * 1000, 1), final_tilt_deg=round(last["tilt"], 2),
                max_tilt_deg=round(max(r["tilt"] for r in seg), 2), min_z_mm=round(min(r["z"] for r in seg) * 1000, 1),
                com_xy_mm=[round(float(last["com"][0]) * 1000, 1), round(float(last["com"][1]) * 1000, 1)],
                torques=dict(sorted(worst.items(), key=lambda kv: -kv[1]["ratio"])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    args = ap.parse_args()
    out_img = ROOT / "assets/img/sim"
    if args.render:
        out_img.mkdir(parents=True, exist_ok=True)
    sim = Sim(render=args.render)
    results = dict(mass_kg=round(float(sum(sim.m.body_mass)), 2), timestep=sim.m.opt.timestep,
                   gains=GAINS, support_polygon_mm=dict(x=[-142, 93], y_abs=[102, 194]))
    print(f"model: {sim.m.nbody - 1} bodies, {sim.m.nu} actuators, {results['mass_kg']} kg")

    # 1. stand
    sim.reset(); sim.targets({}); log = []
    sim.step(5.0, log)
    r = summarize(log, "stand", t_from=1.0)
    r["pass"] = r["final_tilt_deg"] < 2 and r["min_z_mm"] > -30 and all(v["ratio"] < 0.8 for v in r["torques"].values())
    results["stand"] = r
    sim.frame(out_img / "stand.png")
    print(f"stand : tilt {r['final_tilt_deg']}°, base z {r['final_z_mm']} mm, CoM xy {r['com_xy_mm']} mm, "
          + ", ".join(f"{k} {v['peak_nm']}/{v['limit_nm']}" for k, v in list(r['torques'].items())[:4]) + f"  -> {'PASS' if r['pass'] else 'FAIL'}")

    # 2. crouch and return
    sim.reset(); sim.targets({}); log = []
    sim.step(1.0, log)
    n = 250
    for k in range(n):                       # ramp down over 1.5 s
        a = (k + 1) / n
        sim.targets({j: v * a for j, v in CROUCH.items()})
        sim.step(1.5 / n, log)
    sim.frame(out_img / "crouch.png")
    sim.step(1.5, log)
    for k in range(n):                       # ramp back up
        a = 1 - (k + 1) / n
        sim.targets({j: v * a for j, v in CROUCH.items()})
        sim.step(1.5 / n, log)
    sim.step(1.5, log)
    r = summarize(log, "crouch", t_from=1.0)
    r["pass"] = r["max_tilt_deg"] < 10 and r["final_tilt_deg"] < 3 and all(v["ratio"] < 0.9 for v in r["torques"].values())
    results["crouch"] = r
    print(f"crouch: max tilt {r['max_tilt_deg']}°, lowest base z {r['min_z_mm']} mm, "
          + ", ".join(f"{k} {v['peak_nm']}/{v['limit_nm']}" for k, v in list(r['torques'].items())[:4]) + f"  -> {'PASS' if r['pass'] else 'FAIL'}")

    # 3. push while standing: a forward force on the torso for 0.2 s (impulse / 0.2 s = 20..60 N)
    for impulse in (4.0, 6.0, 8.0, 10.0, 12.0):
        sim.reset(); sim.targets({}); log = []
        sim.step(1.5, log)
        t0 = sim.d.time
        sim.step(0.2, log, push=(t0, t0 + 0.2, [impulse / 0.2, 0, 0]))
        sim.frame(out_img / f"push_{int(impulse)}.png") if impulse in (8.0, 12.0) else None
        sim.step(3.0, log)
        r = summarize(log, f"push_{int(impulse)}Ns", t_from=1.5)
        r["impulse_Ns"] = impulse
        r["pass"] = r["final_tilt_deg"] < 5 and r["min_z_mm"] > -50
        results[f"push_{int(impulse)}Ns"] = r
        print(f"push {impulse:4.0f} N·s: max tilt {r['max_tilt_deg']}°, final tilt {r['final_tilt_deg']}°, "
              + ", ".join(f"{k} {v['peak_nm']}/{v['limit_nm']}" for k, v in list(r['torques'].items())[:3]) + f"  -> {'PASS' if r['pass'] else 'FAIL'}")

    (ROOT / "assets/data/sim_results.json").write_text(json.dumps(results, indent=1) + "\n")
    print("wrote assets/data/sim_results.json")


if __name__ == "__main__":
    main()
