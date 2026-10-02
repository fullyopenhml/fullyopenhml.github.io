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
def foh_modules(rid="foh", robot_file="robot.json", bom_file="bom.json"):
    robot = json.loads((ROOT / "assets/data" / robot_file).read_text())
    bom = json.loads((ROOT / "assets/data" / bom_file).read_text())
    cat = robot["catalog"]
    acts = robot["actuators"]
    v1 = rid != "foh"

    def link_slot(lid):
        if lid == "torso":
            return "torso"
        if lid == "pelvis":
            return "torso" if v1 else "lower"       # v1 has no waist: pelvis bars and torso share the root link
        if lid.startswith(("hip_", "thigh", "shank", "ankle", "foot")):
            return "lower"
        if lid.startswith(("shoulder", "upper_arm", "forearm", "hand")):
            return "arms"
        raise KeyError(lid)

    def part_slot(pid, lid, occ=""):
        if occ.startswith("hip_"):            # hip-pitch actuators, bearings and cups live on the root link but belong to the legs
            return "lower"
        if pid.startswith("3DP_hea") or pid in ("EL_CAMERA_D435I",):
            return "head"
        if pid.startswith(("3DP_grp", "EL_SERVO", "KIT_AMAZING", "3DP_arm27")):
            return "hands"
        if pid.startswith(("3DP_pel", "HW_2020_300", "AL_FOOT")):
            return "lower"
        if pid.startswith(("EL_", "CB_", "PC_", "AL_TORSO", "HW_2020_4", "3DP_tor")):
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
            slot = part_slot(pid, lnk["id"], o["occ"])
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

    modules = {s: dict(id=f"{rid}-{s}", robot=rid, slot=s, bom=[], dof=dof[s], mass_kg=0.0) for s in ("lower", "torso", "arms", "hands", "head")}

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
    # electronics, harness -> torso, except camera/servo rows; v1 sections hands and structure by part
    tube_count = defaultdict(int)
    for lnk in robot["links"]:
        for o in lnk["parts"]:
            if o["part"].startswith("CF_TUBE"):
                tube_count[link_slot(lnk["id"])] += 1
    for rid_, r in rows_by_id.items():
        if r["section"] in ("electronics", "harness"):
            add("torso", rid_, r["qty"], "harness and power for the whole robot" if r["section"] == "harness" else None)
        elif r["section"] == "perception":
            add("head", rid_, r["qty"], "optional")
        elif r["section"] in ("grippers", "hands"):
            add("hands", rid_, r["qty"], "optional" if r["section"] == "grippers" else None)
        elif r["section"] == "structure":
            if rid_ == "CF_TUBE_30" or rid_.startswith(("HW_2020_300", "AL_FOOT")):
                add("lower", rid_, r["qty"])
            elif rid_ == "CF_TUBE_25":
                add("arms", rid_, r["qty"])
            elif rid_ == "HW_EPOXY":
                add("lower", rid_, r["qty"], "shared with the arm tubes")
            else:
                add("torso", rid_, r["qty"])
    # hardware: bearings by occurrence, screws/pins by joints of the model, frame and consumables -> torso
    screws = {"HW_OUT_RS03": ("RS03", 6), "HW_LUG_RS03": ("RS03", 8), "HW_OUT_RS06": ("RS06", 6), "HW_LUG_RS06": ("RS06", 8),
              "HW_OUT_RS02": ("RS02", 6), "HW_LUG_RS02": ("RS02", 9), "HW_OUT_RS05": ("RS05", 6), "HW_REAR_RS05": ("RS05", 4),
              "HW_OUT_RS04": ("RS04", 9), "HW_LUG_RS04": ("RS04", 10)}
    for rid_, r in rows_by_id.items():
        if r["section"] != "hardware":
            continue
        if rid_ in screws:
            m, per = screws[rid_]
            for s in modules:
                add(s, rid_, act_count[s].get(m, 0) * per)
        elif rid_ == "HW_PIN_4X10":
            for s in modules:
                add(s, rid_, 3 * (dof[s] - act_count[s].get("RS04", 0)))
        elif rid_ == "HW_PIN_6X12":
            for s in modules:
                add(s, rid_, 3 * act_count[s].get("RS04", 0))
        elif rid_ == "HW_TUBE_BOLT":
            for s in modules:
                add(s, rid_, 4 * tube_count.get(s, 0))
        elif rid_.startswith("HW_6"):
            for s in modules:
                add(s, rid_, hw_count[s].get(rid_, 0))
        else:
            add("torso", rid_, r["qty"], "shared consumables and frame")
    # filament by printed mass; the BOM's spool count includes waste, so scale by share of printed mass
    tot_printed = {m: sum(printed_g[s][m] for s in printed_g) for m in ("petg_cf", "pla", "tpu")}
    fil = {"petg_cf": "MAT_PETG_CF", "pla": "MAT_PLA", "tpu": "MAT_TPU"}
    for s in modules:
        for m, frow in fil.items():
            if tot_printed.get(m):
                share = printed_g[s][m] / tot_printed[m]
                add(s, frow, rows_by_id[frow]["qty"] * share, f"{printed_g[s][m]/1000:.2f} kg of printed parts")

    total_mass = sum(mass.values())
    if not v1:
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
        note = "Computed from the v0.2 BOM: actuators and kit hardware by joint, printed filament by mass, electronics and harness in the torso. Unbuilt design."
        scale = 1114
    else:
        names = dict(lower="FOH v1 legs and pelvis bars (tube links)", torso="FOH v1 torso (extrusion, aluminium plates)", arms="FOH v1 arms (tube links)",
                     hands="FOH v1 hands (2 × Amazing Hand)", head="FOH v1 head (camera optional)")
        ifaces = dict(
            lower=dict(top=dict(joint="pelvis bars", mount="2020-bars", desc="Two 2020 pelvis bars; the torso bottom plate bolts to them with M5 T-nuts"), payload_kg=r2(total_mass - mass["lower"])),
            torso=dict(bottom=dict(joint="pelvis bars", mount="2020-bars", desc="5 mm aluminium bottom plate on the two pelvis bars"),
                       side=dict(joint="shoulder pitch", mount="rs03-output", desc="Shoulder-pitch RS03 in the torso; the arm's shoulder-roll bracket bolts to its output coupler"),
                       top=dict(joint="head", mount="2020-top", desc="Neck post on the aluminium top plate")),
            arms=dict(top=dict(joint="shoulder pitch", mount="rs03-output", desc="Shoulder-roll bracket on the torso's RS03 output"),
                      bottom=dict(joint="wrist roll", mount="rs05-output", desc="Wrist-roll RS05 output boss (6 × M4 on Ø24) to the hand flange")),
            hands=dict(top=dict(joint="wrist roll", mount="rs05-output", desc="Hand flange on the RS05 adapter")),
            head=dict(bottom=dict(joint="head", mount="2020-top", desc="Neck post on the top plate")),
        )
        note = "Computed from the v1 BOM: actuators and kit hardware by joint, tubes by link, filament by mass, electronics, plates and harness in the torso. Unbuilt production design."
        scale = robot["specs"]["height_mm"]
    out = []
    for s, m in modules.items():
        core = sum(b["total"] for b in m["bom"] if b["tier"] == "core")
        opt = sum(b["total"] for b in m["bom"] if b["tier"] != "core")
        fam = "robstride-rs" if m["dof"] else ("feetech-sts" if s == "hands" and v1 else "none")
        out.append(dict(id=m["id"], robot=rid, slot=s, name=names[s], dof=m["dof"], mass_kg=r2(mass[s]), price_usd=r2(core), price_optional_usd=r2(opt),
                        price_basis="itemised", scale_mm=scale, family=fam, bom=m["bom"], notes=note, **ifaces[s]))
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
    fohv1, _ = foh_modules("foh-v1", "robot_v1.json", "bom_v1.json")
    duke = duke_modules() or []
    modules = foh + fohv1 + duke + [dict(m) for m in S.MODULES]
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
               criteria=S.CRITERIA, forms=S.FORMS, slots=S.SLOTS, families=S.FAMILIES, robots=robots, closed=S.CLOSED, modules=modules, verified_combos=S.VERIFIED_COMBOS)
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(robots)} robots, {len(modules)} modules")
    for m in modules:
        if m["robot"] in ("foh", "foh-v1", "duke2"):
            print(f"  {m['id']:14s} dof {m['dof']:>3}  mass {m['mass_kg']!s:>6} kg  ${m['price_usd']!s:>9}  (+opt {m['price_optional_usd']})  rows {len(m['bom'])}")
    for rid in ("foh", "foh-v1", "duke2"):
        ms = [m for m in modules if m["robot"] == rid]
        print(f"  {rid}: modules total ${sum(m['price_usd'] or 0 for m in ms):,.0f}, mass {sum(m['mass_kg'] or 0 for m in ms):.1f} kg, dof {sum(m['dof'] or 0 for m in ms)}")


if __name__ == "__main__":
    main()
