"""Fusion 360 script: one STEP per sub-assembly (module) of the robot.

Run with humanoid_2.1_latest open and pick the dated export folder written by
fusion_export (the one with tree.csv). Writes into it:

  modules/<component>.step       one STEP per component that has child components,
                                 down to two levels below the root (the whole robot is
                                 exported by fusion_export): lower body, torso, arms,
                                 gripper; legs, camera columns, wrists, hip / knee /
                                 shoulder / elbow modules, the electronics tray; and the
                                 vendor assemblies used at those levels (actuators,
                                 servo, controller). Grouping folders (protections,
                                 bearings, schematics, wires) are skipped.
  modules.csv                    file, fusion name, path, depth, qty, children, mass
  joints.csv                     every joint and as-built joint of every component (the
                                 joints live inside the linked designs, so the root's
                                 own list is empty): component, joint, type, the two
                                 occurrences, origin (mm) and axis in that component's
                                 frame, limits and current value (rad or cm)
  transforms.csv                 every occurrence with bodies: path, fusion name, the
                                 file name tree.csv uses for that component (same
                                 first-seen numbering as fusion_export), visible, and
                                 the 4x4 transform to the root (cm, row-major)
  export_modules.log

File names are unique per component (name, name~2, ...) like tree.csv.
"""

import csv
import os
import re
import traceback

import adsk.core
import adsk.fusion

MAX_DEPTH = 2                       # 0 = direct child of the root
SKIP = {"protections", "bearings", "schematics", "WIRES", "BEARING", "Relationships",
        "Construction", "Named Views", "Origin"}


def safe_name(name):
    name = re.sub(r"\s*v\d+$", "", name.strip())
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "unnamed"


JOINT_COLS = ["component", "component_path", "joint", "kind", "type", "occurrence_one", "occurrence_two",
              "origin_x_mm", "origin_y_mm", "origin_z_mm", "axis_x", "axis_y", "axis_z",
              "min", "max", "value", "units", "is_suppressed", "note"]
JOINT_TYPES = {0: "rigid", 1: "revolute", 2: "slider", 3: "cylindrical", 4: "pin_slot", 5: "planar", 6: "ball"}


def joint_row(comp, path, j, kind):
    r = dict.fromkeys(JOINT_COLS, "")
    r.update(component=comp.name, component_path=path, joint=j.name, kind=kind)
    try:
        r["is_suppressed"] = j.isSuppressed
    except Exception:
        pass
    try:
        r["occurrence_one"] = j.occurrenceOne.fullPathName if j.occurrenceOne else ""
        r["occurrence_two"] = j.occurrenceTwo.fullPathName if j.occurrenceTwo else ""
    except Exception:
        pass
    try:
        m = j.jointMotion
        r["type"] = JOINT_TYPES.get(m.jointType, str(m.jointType))
        for attr in ("rotationAxisVector", "slideDirectionVector"):
            v = getattr(m, attr, None)
            if v:
                r.update(axis_x=round(v.x, 6), axis_y=round(v.y, 6), axis_z=round(v.z, 6))
                break
        for lim_attr, val_attr, units in (("rotationLimits", "rotationValue", "rad"),
                                          ("slideLimits", "slideValue", "cm")):
            lim = getattr(m, lim_attr, None)
            if lim is not None:
                if lim.isMinimumValueEnabled:
                    r["min"] = round(lim.minimumValue, 6)
                if lim.isMaximumValueEnabled:
                    r["max"] = round(lim.maximumValue, 6)
                r["value"] = round(getattr(m, val_attr), 6)
                r["units"] = units
                break
    except Exception:
        r["note"] = "motion unreadable"
    try:
        o = j.geometryOrOriginOne.origin
        r.update(origin_x_mm=round(o.x * 10, 3), origin_y_mm=round(o.y * 10, 3), origin_z_mm=round(o.z * 10, 3))
    except Exception:
        r["note"] = (r["note"] + "; " if r["note"] else "") + "origin unreadable"
    return r


def write_joints(root, out, log):
    rows, done = [], set()
    comps = [(root, "")]
    for occ in root.allOccurrences:
        comps.append((occ.component, occ.fullPathName))
    for comp, path in comps:
        key = comp.id if hasattr(comp, "id") else comp.name
        if key in done:
            continue
        done.add(key)
        try:
            for j in comp.joints:
                rows.append(joint_row(comp, path, j, "joint"))
            for j in comp.asBuiltJoints:
                rows.append(joint_row(comp, path, j, "as_built"))
        except Exception:
            log.append("joints unreadable in %s" % comp.name)
    with open(os.path.join(out, "joints.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=JOINT_COLS, lineterminator=chr(10))
        w.writeheader()
        w.writerows(rows)
    log.append("wrote joints.csv (%d joints from %d components)" % (len(rows), len(done)))
    return len(rows)


def write_transforms(root, out, log):
    """Occurrence world transforms, with the component file names of fusion_export:
    both scripts number same-named components in root.allOccurrences order."""
    rows, used, names = [], {}, {}
    for occ in root.allOccurrences:
        comp = occ.component
        key = comp.id if hasattr(comp, "id") else comp.name
        if key not in names:
            base = safe_name(comp.name)
            n = used.get(base, 0) + 1
            used[base] = n
            names[key] = base if n == 1 else "%s~%d" % (base, n)
        if comp.bRepBodies.count == 0:
            continue
        t = occ.transform2 if hasattr(occ, "transform2") else occ.transform
        rows.append([occ.fullPathName, comp.name, names[key], occ.isVisible] + ["%.6f" % x for x in t.asArray()])
    with open(os.path.join(out, "transforms.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator=chr(10))
        w.writerow(["path", "fusion_name", "file_name", "visible"] + ["m%d" % i for i in range(16)])
        w.writerows(rows)
    log.append("wrote transforms.csv (%d occurrences)" % len(rows))


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    log = []
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        root = design.rootComponent
        dlg = ui.createFolderDialog()
        dlg.title = "Pick the dated export folder (the one with tree.csv)"
        if dlg.showDialog() != adsk.core.DialogResults.DialogOK:
            return
        out = dlg.folder
        os.makedirs(os.path.join(out, "modules"), exist_ok=True)
        em = design.exportManager
        n_joints = write_joints(root, out, log)
        write_transforms(root, out, log)

        seen, used, rows = {}, {}, []
        for occ in root.allOccurrences:
            comp = occ.component
            path = occ.fullPathName
            depth = path.count("+")
            if depth > MAX_DEPTH or comp.occurrences.count == 0 or comp.name in SKIP:
                continue
            key = comp.id if hasattr(comp, "id") else comp.name
            if key in seen:
                seen[key]["qty"] += 1
                continue
            base = safe_name(comp.name)
            n = used.get(base, 0) + 1
            used[base] = n
            fn = base if n == 1 else "%s~%d" % (base, n)
            try:
                mass = round(comp.physicalProperties.mass * 1000, 1)
            except Exception:
                mass = ""
            seen[key] = dict(file=fn + ".step", name=comp.name, path=path, depth=depth, qty=1,
                             children=comp.occurrences.count, mass=mass, comp=comp)

        prog = ui.createProgressDialog()
        prog.isCancelButtonShown = True
        prog.show("Module STEP export", "", 0, len(seen))
        for e in seen.values():
            if prog.wasCancelled:
                log.append("cancelled")
                break
            prog.message = e["name"]
            try:
                ok = em.execute(em.createSTEPExportOptions(os.path.join(out, "modules", e["file"]), e["comp"]))
            except Exception:
                ok = False
                log.append("%s: EXCEPTION %s" % (e["file"], traceback.format_exc().splitlines()[-1]))
            log.append("%s: %s" % (e["file"], "ok" if ok else "FAILED"))
            rows.append([e["file"] if ok else "", e["name"], e["path"], e["depth"], e["qty"], e["children"], e["mass"]])
            prog.progressValue += 1
            adsk.doEvents()
        prog.hide()

        with open(os.path.join(out, "modules.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["file", "fusion_name", "path", "depth", "qty", "children", "mass_g"])
            w.writerows(rows)
        with open(os.path.join(out, "export_modules.log"), "w", encoding="utf-8") as fh:
            fh.write("Fusion %s\n" % app.version + "\n".join(log) + "\n")
        bad = sum(1 for l in log if "FAILED" in l or "EXCEPTION" in l)
        ui.messageBox("Done. %d modules, %d joints, %d problems.\n%s" % (len(rows), n_joints, bad, os.path.join(out, "modules")))
    except Exception:
        ui.messageBox("Failed:\n" + traceback.format_exc())
