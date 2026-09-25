#!/usr/bin/env python3
"""Build assets/data/catalog.json: the open-humanoid catalog and the builder's modules.

Merges tools/catalog_src.py (curated) with
  - Fully Open Humanoid modules computed from assets/data/robot.json and bom.json
  - Duke Humanoid V2 modules computed from its hardware-site CSVs (if the folder is present)

Run:  python3 tools/build_catalog.py
"""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import catalog_src as S  # noqa: E402

OUT = ROOT / "assets/data/catalog.json"


def r2(x):
    return None if x is None else round(float(x), 2)


# ---------------------------------------------------------------- FOH modules --------
def foh_modules():
    robot = json.loads((ROOT / "assets/data/robot.json").read_text())
    bom = json.loads((ROOT / "assets/data/bom.json").read_text())
    cat = robot["catalog"]
    acts = robot["actuators"]

    def link_slot(lid):
        if lid == "torso":
            return "torso"
        if lid == "pelvis" or lid.startswith(("hip_", "thigh", "shank", "ankle", "foot")):
            return "lower"
        if lid.startswith(("shoulder", "upper_arm", "forearm", "hand")):
            return "arms"
        raise KeyError(lid)

    def part_slot(pid, lid):
        if pid.startswith("3DP_hea") or pid in ("EL_CAMERA_D435I",):
            return "head"
        if pid.startswith("3DP_grp") or pid.startswith("EL_SERVO"):
            return "hands"
        if pid.startswith(("EL_", "CB_")):
            return "torso"
        return link_slot(lid)

    joint_slot = {}
    for j in robot["joints"]:
        joint_slot[j["id"]] = "torso" if j["id"] == "waist" else link_slot(j["child"])

    # occurrences per slot: printed mass, hardware counts, masses
    mass = defaultdict(float)          # kg per slot (parts)
    printed_g = defaultdict(lambda: defaultdict(float))  # slot -> material -> g
    hw_count = defaultdict(lambda: defaultdict(int))     # slot -> part id -> occurrences
    for lnk in robot["links"]:
        for o in lnk["parts"]:
            pid = o["part"]
            slot = part_slot(pid, lnk["id"])
            c = cat.get(pid, {})
            mg = c.get("mass_g", 0) or 0
            mass[slot] += mg / 1000
            if c.get("category") == "printed":
                printed_g[slot][c.get("material", "petg_cf")] += mg
            if pid.startswith("HW_"):
                hw_count[slot][pid] += 1
    dof = defaultdict(int)
    act_count = defaultdict(lambda: defaultdict(int))   # slot -> model -> n
    for j in robot["joints"]:
        s = joint_slot[j["id"]]
        dof[s] += 1
        act_count[s][j["actuator"]] += 1
        if not any(o["part"].startswith("ACT_") for l in robot["links"] for o in l["parts"]):
            mass[s] += acts[j["actuator"]]["mass_g"] / 1000   # only if actuators are not already link parts

    rows_by_id = {}
    for sec in bom["sections"]:
        for r in sec["rows"]:
            rows_by_id[r["id"]] = dict(r, section=sec["id"], tier=sec["tier"])

    modules = {s: dict(id=f"foh-{s}", robot="foh", slot=s, bom=[], dof=dof[s], mass_kg=0.0) for s in ("lower", "torso", "arms", "hands", "head")}

    def add(slot, rid, qty, note=None):
        r = rows_by_id[rid]
        if qty <= 0:
            return
        unit = r["unit_cost"]
        modules[slot]["bom"].append(dict(item=r["description"], part_id=rid, qty=r2(qty), unit=unit, total=r2(qty * unit),
                                         vendor=r["vendor"], url=r.get("url"), note=note, section=r["section"], tier=r["tier"]))

    # actuators by joint
    for s, models in act_count.items():
        for m, n in models.items():
            add(s, f"ACT_{m}", n)
    # electronics, harness -> torso, except camera/servo rows
    for rid, r in rows_by_id.items():
        if r["section"] in ("electronics", "harness"):
            add("torso", rid, r["qty"], "harness and power for the whole robot" if r["section"] == "harness" else None)
        elif r["section"] == "perception":
            add("head", rid, r["qty"], "optional")
        elif r["section"] == "grippers":
            add("hands", rid, r["qty"], "optional")
    # hardware: bearings by occurrence, screws/pins by joints of the model, frame and consumables -> torso
    screws = {"HW_OUT_RS03": ("RS03", 6), "HW_LUG_RS03": ("RS03", 8), "HW_OUT_RS06": ("RS06", 6), "HW_LUG_RS06": ("RS06", 8),
              "HW_OUT_RS02": ("RS02", 6), "HW_LUG_RS02": ("RS02", 9), "HW_OUT_RS05": ("RS05", 6), "HW_REAR_RS05": ("RS05", 4)}
    for rid, r in rows_by_id.items():
        if r["section"] != "hardware":
            continue
        if rid in screws:
            m, per = screws[rid]
            for s in modules:
                add(s, rid, act_count[s].get(m, 0) * per)
        elif rid == "HW_PIN_4X10":
            for s in modules:
                add(s, rid, 3 * dof[s])
        elif rid.startswith("HW_6"):
            for s in modules:
                add(s, rid, hw_count[s].get(rid, 0))
        else:
            add("torso", rid, r["qty"], "shared consumables and frame")
    # filament by printed mass; the BOM's spool count includes waste, so scale by share of printed mass
    tot_printed = {m: sum(printed_g[s][m] for s in printed_g) for m in ("petg_cf", "pla", "tpu")}
    fil = {"petg_cf": "MAT_PETG_CF", "pla": "MAT_PLA", "tpu": "MAT_TPU"}
    for s in modules:
        for m, rid in fil.items():
            if tot_printed.get(m):
                share = printed_g[s][m] / tot_printed[m]
                add(s, rid, rows_by_id[rid]["qty"] * share, f"{printed_g[s][m]/1000:.2f} kg of printed parts")

    total_mass = sum(mass.values())
    names = dict(lower="Fully Open Humanoid legs and pelvis", torso="Fully Open Humanoid torso", arms="Fully Open Humanoid arms",
                 hands="Fully Open Humanoid grippers (optional)", head="Fully Open Humanoid head (camera optional)")
    ifaces = dict(
        lower=dict(top=dict(joint="waist", mount="rs03-output", desc="Waist RS03 in the pelvis; its output boss (6 × M4 on Ø30.36, 3 dowels) drives the torso plate"), payload_kg=r2(total_mass - mass["lower"])),
        torso=dict(bottom=dict(joint="waist", mount="rs03-output", desc="Torso bottom plate bolts through a printed coupler to the waist RS03 output"),
                   side=dict(joint="shoulder pitch", mount="rs06-output", desc="Shoulder-pitch RS06 in the torso; the arm's shoulder-roll bracket bolts to its output"),
                   top=dict(joint="head", mount="2020-top", desc="Head bracket bolts to the tops of the four 2020 extrusions")),
        arms=dict(top=dict(joint="shoulder pitch", mount="rs06-output", desc="Shoulder-roll bracket on the torso's RS06 output"),
                  bottom=dict(joint="wrist roll", mount="rs05-output", desc="Wrist-roll RS05 output boss (6 × M4 on Ø24)")),
        hands=dict(top=dict(joint="wrist roll", mount="rs05-output", desc="Gripper adapter on the RS05 output boss")),
        head=dict(bottom=dict(joint="head", mount="2020-top", desc="Bracket on the four extrusion tops")),
    )
    out = []
    for s, m in modules.items():
        core = sum(b["total"] for b in m["bom"] if b["tier"] == "core")
        opt = sum(b["total"] for b in m["bom"] if b["tier"] != "core")
        out.append(dict(id=m["id"], robot="foh", slot=s, name=names[s], dof=m["dof"], mass_kg=r2(mass[s]), price_usd=r2(core), price_optional_usd=r2(opt),
                        price_basis="itemised", scale_mm=1114, family="robstride-rs" if m["dof"] else "none", bom=m["bom"],
                        notes="Computed from the v0.2 BOM: actuators and kit hardware by joint, printed filament by mass, electronics and harness in the torso. Unbuilt design.",
                        **ifaces[s]))
    return out, total_mass


# ---------------------------------------------------------------- Duke V2 modules ----
def duke_modules():
    d = ROOT / "Duke_Humanoid_V2_OpenSource/hardware-site/docs/data"
    if not d.exists():
        return None
    rows = []
    for f in ("actuators", "electronics", "cnc-parts", "printed-parts", "fasteners", "cables-connectors"):
        for r in csv.DictReader(open(d / f"{f}.csv", newline="")):
            rows.append(dict(r, file=f))
    # joints per model per slot, from the project's full-specifications table
    act_slots = {
        "ACT_RS00": dict(arms=2), "ACT_RS02": dict(arms=6), "ACT_RS03": dict(lower=8, torso=1, arms=2), "ACT_RS04": dict(lower=2),
        "ACT_RS05": dict(arms=2, head=4), "ACT_RS06": dict(lower=2, arms=2),
    }
    sub_slot = dict(leg="lower", body="torso", arm="arms", gripper="hands", head_camera="head", printed="torso", harness="torso")
    dof = dict(lower=12, torso=1, arms=14, hands=2, head=4)
    share = {s: n / 31 for s, n in dict(lower=12, torso=1, arms=14, head=4).items()}
    modules = {s: dict(id=f"duke2-{s}", robot="duke2", slot=s, bom=[]) for s in ("lower", "torso", "arms", "hands", "head")}

    def add(slot, r, qty, note=None):
        if qty <= 0:
            return
        unit = float(r["unit_cost_usd"] or 0)
        modules[slot]["bom"].append(dict(item=r["description"], part_id=r["part_id"], qty=r2(qty), unit=unit, total=r2(qty * unit),
                                         vendor=r["vendor"] or ("CNC shop" if r["file"] == "cnc-parts" else "print"), url=r["vendor_url"] or None,
                                         note=note, section=r["file"], tier="core"))

    for r in rows:
        q = float(r["qty_per_robot"] or 0)
        pid = r["part_id"]
        if r["file"] == "actuators":
            for s, n in act_slots[pid].items():
                add(s, r, n)
        elif r["file"] == "electronics":
            if pid.startswith("EL_CAM"):
                add("head", r, q)
            elif pid.startswith("EL_SERVO"):
                add("hands", r, q)
            else:
                add("torso", r, q)
        elif r["file"] == "fasteners":
            for s, f in share.items():
                add(s, r, round(q * f), "apportioned by joint count")
        elif r["file"] == "cables-connectors":
            add("torso", r, q)
        else:
            add(sub_slot.get(r["subassembly"], "torso"), r, q)
    masses = dict(lower=17.5, torso=7.9 - 2 * 0.59, arms=2 * 4.6, hands=2 * 0.35, head=2 * 0.59)
    names = dict(lower="Duke Humanoid V2 legs and hip centre", torso="Duke Humanoid V2 body", arms="Duke Humanoid V2 arms",
                 hands="Duke Humanoid V2 grippers", head="Duke Humanoid V2 camera gimbals")
    ifaces = dict(
        lower=dict(top=dict(joint="waist", mount="rs03-output", desc="Waist RS03 in the hip centre; machined coupler on its output boss to the body bottom plate"), payload_kg=r2(35.3 - 17.5)),
        torso=dict(bottom=dict(joint="waist", mount="rs03-output", desc="Body bottom plate on the waist RS03 output coupler"),
                   side=dict(joint="shoulder_1", mount="rs03-output", desc="Shoulder-1 RS03 in the body; machined coupler on its output"),
                   top=dict(joint="camera columns", mount="duke-top-plate", desc="Two camera columns on the body top plate")),
        arms=dict(top=dict(joint="shoulder_1", mount="rs03-output", desc="Arm bracket on the body's RS03 output coupler"),
                  bottom=dict(joint="wrist_3", mount="rs05-output", desc="Wrist-3 RS05 output")),
        hands=dict(top=dict(joint="wrist_3", mount="rs05-output", desc="Gripper on the RS05 output")),
        head=dict(bottom=dict(joint="camera columns", mount="duke-top-plate", desc="Gimbal columns on the body top plate")),
    )
    out = []
    for s, m in modules.items():
        out.append(dict(id=m["id"], robot="duke2", slot=s, name=names[s], dof=dof[s], mass_kg=r2(masses[s]), price_usd=r2(sum(b["total"] for b in m["bom"])),
                        price_basis="itemised", scale_mm=1256, family="feetech-sts" if s == "hands" else "robstride-rs", bom=m["bom"],
                        notes="Computed from the project's curated BOM CSVs (priced 2026-09-19): actuators by joint, machined and printed parts by subassembly, fasteners apportioned by joint count, electronics in the body. Consumables not itemised.",
                        **ifaces[s]))
    return out


def main():
    foh, foh_mass = foh_modules()
    duke = duke_modules() or []
    modules = foh + duke + [dict(m) for m in S.MODULES]
    for m in modules:
        m.setdefault("price_optional_usd", 0)
        m.setdefault("mass_kg", None)
        m.setdefault("payload_kg", None)
        m.setdefault("scale_mm", None)
        for b in m["bom"]:
            b.setdefault("total", r2(b["qty"] * b["unit"]) if b.get("unit") is not None and b.get("qty") is not None else None)
    robots = []
    for r in S.ROBOTS:
        r = dict(r)
        score = sum(1 for v in r["open"].values() if v == "yes") + sum(0.5 for v in r["open"].values() if v == "partial")
        r["score"] = score
        r["oshwa"] = r["open"]["lic"] == "yes"
        r["modules"] = [m["id"] for m in modules if m["robot"] == r["id"]]
        robots.append(r)
    out = dict(meta=dict(generated=date.today().isoformat(), robots=len(robots), modules=len(modules), foh_mass_kg=r2(foh_mass)),
               criteria=S.CRITERIA, slots=S.SLOTS, families=S.FAMILIES, robots=robots, closed=S.CLOSED, modules=modules, verified_combos=S.VERIFIED_COMBOS)
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(robots)} robots, {len(modules)} modules")
    for m in modules:
        if m["robot"] in ("foh", "duke2"):
            print(f"  {m['id']:14s} dof {m['dof']:>3}  mass {m['mass_kg']!s:>6} kg  ${m['price_usd']!s:>9}  (+opt {m['price_optional_usd']})  rows {len(m['bom'])}")
    for rid in ("foh", "duke2"):
        ms = [m for m in modules if m["robot"] == rid]
        print(f"  {rid}: modules total ${sum(m['price_usd'] or 0 for m in ms):,.0f}, mass {sum(m['mass_kg'] or 0 for m in ms):.1f} kg, dof {sum(m['dof'] or 0 for m in ms)}")


if __name__ == "__main__":
    main()
