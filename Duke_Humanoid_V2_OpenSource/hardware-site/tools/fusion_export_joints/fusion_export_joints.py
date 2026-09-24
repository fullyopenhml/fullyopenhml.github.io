"""Fusion 360 script: joints and world transforms only (30 s, no STEP export).

Run with humanoid_2.1_latest open; pick the dated export folder (the one with
tree.csv). Writes joints.csv and transforms.csv there, exactly as
fusion_export_modules does, for a run that was made with an older version.
"""

import csv
import os
import re
import traceback

import adsk.core
import adsk.fusion


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
        n = write_joints(root, out, log)
        write_transforms(root, out, log)
        with open(os.path.join(out, "export_joints.log"), "w", encoding="utf-8") as fh:
            fh.write("Fusion %s" % app.version + chr(10) + chr(10).join(log) + chr(10))
        ui.messageBox("Done. %d joints written; transforms.csv written." % n + chr(10) + out)
    except Exception:
        ui.messageBox("Failed:" + chr(10) + traceback.format_exc())
