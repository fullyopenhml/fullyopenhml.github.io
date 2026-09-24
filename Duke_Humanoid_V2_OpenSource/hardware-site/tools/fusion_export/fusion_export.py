"""Fusion 360 script: export the Duke Humanoid V2 release CAD in one run.

Run it from Fusion 360 with the robot design (humanoid_2.1_latest) open:
  UTILITIES > ADD-INS > Scripts and Add-Ins > Scripts > fusion_export > Run

It asks for an output folder, then writes:

  <out>/tree.csv                 every component: path, name, qty, bodies, material,
                                 mass, bounding box, linked?, out-of-date?  (always)
  <out>/assembly/<design>.step   whole-robot STEP                            (full run)
  <out>/assembly/<design>.f3z    native Fusion archive, linked designs included
  <out>/step/<component>.step    one STEP per component that has bodies (parts, and
  <out>/print/<component>.stl    plates that carry inserts), plus a high-resolution STL
                                 of its own bodies. Two different components with the same
                                 name get distinct file names (name, name~2, ...); tree.csv
                                 records the file name of every component.
  <out>/joints.csv               every joint in the design: type, the two occurrences,
                                 origin (mm, root frame), axis, limits and current value
  <out>/export.log               what was written, what failed, Fusion version

tree.csv carries Fusion's own mass properties per component (mass, centre of
mass in the component frame, moments and products of inertia about the centre
of mass) so nothing is recomputed from meshes downstream.

tools/stage_cad_export.py copies the files the site publishes into
hardware-site/docs/files/ under the site's part IDs.

Nothing here modifies the design. Out-of-date linked components are reported,
not updated: use Get Latest in the browser before a release export.
"""

import csv
import datetime
import os
import re
import traceback

import adsk.core
import adsk.fusion

_app = None
_ui = None
_log_lines = []

# Printed covers that carry no CNC_/3DP_ prefix in Fusion (same list as
# hardware-site/tools/gen_printed.py and fusion_export_viewer).
EXTRA = {"Component5", "Component34", "Component35", "Component36", "Component37", "Component38",
         "Component39", "Component40", "Component41", "Component42", "Component43", "Component44",
         "Component45", "Component194", "Component195", "Component196", "Component197",
         "Component198", "Component199", "symmetric_sole", "foot_front"}


def releasable(name):
    return name.startswith(("CNC_", "3DP_")) or name in EXTRA


def log(msg):
    _log_lines.append(msg)


def safe_name(name):
    name = re.sub(r"\s*v\d+$", "", name.strip())          # drop Fusion's " v12" version suffix
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name.strip("_") or "unnamed"


def bbox_mm(comp):
    try:
        bb = comp.boundingBox
        return [round((bb.maxPoint.x - bb.minPoint.x) * 10, 1),
                round((bb.maxPoint.y - bb.minPoint.y) * 10, 1),
                round((bb.maxPoint.z - bb.minPoint.z) * 10, 1)]
    except Exception:
        return ["", "", ""]


def mass_g(comp):
    try:
        return round(comp.physicalProperties.mass * 1000, 1)
    except Exception:
        return ""


def phys(comp):
    """Fusion mass properties: centre of mass (mm, component frame) and the
    moments/products of inertia about the centre of mass (g*mm^2)."""
    blank = [""] * 9
    try:
        pp = comp.physicalProperties
        c = pp.centerOfMass
        ok, xx, yy, zz, xy, yz, xz = pp.getXYZMomentsOfInertia()
        if not ok:
            return [round(c.x * 10, 3), round(c.y * 10, 3), round(c.z * 10, 3)] + [""] * 6
        k = 1e5   # kg*cm^2 -> g*mm^2
        return [round(c.x * 10, 3), round(c.y * 10, 3), round(c.z * 10, 3),
                round(xx * k, 1), round(yy * k, 1), round(zz * k, 1),
                round(xy * k, 1), round(yz * k, 1), round(xz * k, 1)]
    except Exception:
        return blank


def appearance_rgb(comp):
    """Fusion appearance of the component's first body as 'r,g,b' (0-255) and
    its appearance name, or ('', '') when the appearance carries no colour."""
    try:
        for b in comp.bRepBodies:
            app = b.appearance
            if not app:
                continue
            for prop in app.appearanceProperties:
                if prop.objectType != adsk.core.ColorProperty.classType():
                    continue
                if prop.id not in ("opaque_albedo", "surface_albedo", "metal_f0", "transparent_color",
                                   "layered_diffuse", "generic_diffuse", "glazing_transmission_color"):
                    continue
                cols = prop.values if prop.hasMultipleValues else [prop.value]
                for c in cols:
                    if c is not None:
                        return "%d,%d,%d" % (c.red, c.green, c.blue), app.name
            return "", app.name
    except Exception:
        pass
    return "", ""


def materials(comp):
    names = []
    for b in comp.bRepBodies:
        try:
            n = b.material.name
        except Exception:
            n = ""
        if n and n not in names:
            names.append(n)
    return "; ".join(names)


def walk(root):
    """Collect every component once, with qty = number of occurrences and the first path.
    file_name is unique per component: a second, different component with the same
    name gets a ~2 suffix (the first export overwrote such pairs)."""
    comps = {}
    used = {}
    for occ in root.allOccurrences:
        comp = occ.component
        key = comp.id if hasattr(comp, "id") else comp.name
        entry = comps.get(key)
        if entry is None:
            base = safe_name(comp.name)
            n = used.get(base, 0) + 1
            used[base] = n
            entry = dict(
                comp=comp,
                name=comp.name,
                file_name=base if n == 1 else "%s~%d" % (base, n),
                path=occ.fullPathName,
                qty=0,
                children=comp.occurrences.count,
                bodies=comp.bRepBodies.count,
                linked=occ.isReferencedComponent,
                out_of_date="",
                visible=occ.isVisible,
            )
            for attr in ("isOutOfDate",):
                try:
                    entry["out_of_date"] = bool(getattr(occ, attr))
                except Exception:
                    pass
            comps[key] = entry
        entry["qty"] += 1
    return list(comps.values())


def write_tree(entries, out):
    path = os.path.join(out, "tree.csv")
    cols = ["fusion_name", "file_name", "kind", "qty", "bodies", "children", "material",
            "mass_g", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "linked", "out_of_date", "path",
            "color_rgb", "appearance",
            "com_x_mm", "com_y_mm", "com_z_mm", "ixx", "iyy", "izz", "ixy", "iyz", "ixz"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(cols)
        for e in sorted(entries, key=lambda e: e["path"]):
            kind = "part" if e["children"] == 0 and e["bodies"] > 0 else (
                "mixed" if e["children"] and e["bodies"] else "subassembly" if e["children"] else "empty")
            bx, by, bz = bbox_mm(e["comp"])
            rgb, app_name = appearance_rgb(e["comp"]) if e["bodies"] else ("", "")
            w.writerow([e["name"], e["file_name"], kind, e["qty"], e["bodies"], e["children"],
                        materials(e["comp"]) if e["bodies"] else "",
                        mass_g(e["comp"]), bx, by, bz, e["linked"], e["out_of_date"], e["path"],
                        rgb, app_name] + (phys(e["comp"]) if e["bodies"] or e["children"] else [""] * 9))
    log("wrote %s (%d components)" % (path, len(entries)))
    return path


def write_joints(design, out):
    """joints.csv: every joint and as-built joint reachable from the root."""
    path = os.path.join(out, "joints.csv")
    cols = ["joint", "kind", "type", "occurrence_one", "occurrence_two", "origin_x_mm", "origin_y_mm",
            "origin_z_mm", "axis_x", "axis_y", "axis_z", "min", "max", "value", "units", "is_suppressed", "note"]
    names = {0: "rigid", 1: "revolute", 2: "slider", 3: "cylindrical", 4: "pin_slot", 5: "planar", 6: "ball"}
    rows = []

    def desc(j, kind):
        r = dict.fromkeys(cols, "")
        r.update(joint=j.name, kind=kind)
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
            r["type"] = names.get(m.jointType, str(m.jointType))
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
            g = j.geometryOrOriginOne
            o = g.origin
            r.update(origin_x_mm=round(o.x * 10, 3), origin_y_mm=round(o.y * 10, 3), origin_z_mm=round(o.z * 10, 3))
        except Exception:
            r["note"] = (r["note"] + "; " if r["note"] else "") + "origin unreadable"
        return r

    try:
        for j in design.rootComponent.allJoints:
            rows.append(desc(j, "joint"))
    except Exception:
        log("allJoints unreadable")
    try:
        for j in design.rootComponent.allAsBuiltJoints:
            rows.append(desc(j, "as_built"))
    except Exception:
        log("allAsBuiltJoints unreadable")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    log("wrote joints.csv (%d joints)" % len(rows))


def export_step(em, comp, path):
    opts = em.createSTEPExportOptions(path, comp)
    return em.execute(opts)


def export_stl(em, comp, path):
    """High-resolution binary STL of the component's OWN bodies only (children such
    as heat-set inserts or mounted electronics are left out), by concatenating
    one export per body."""
    import tempfile
    tmp = tempfile.mkdtemp()
    chunks = []
    for i, body in enumerate(comp.bRepBodies):
        p = os.path.join(tmp, "%d.stl" % i)
        opts = em.createSTLExportOptions(body, p)
        opts.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        opts.isBinaryFormat = True
        if em.execute(opts):
            with open(p, "rb") as fh:
                data = fh.read()
            n = int.from_bytes(data[80:84], "little")
            chunks.append((n, data[84:84 + n * 50]))
    total = sum(n for n, _ in chunks)
    with open(path, "wb") as fh:
        fh.write(b"\x00" * 80 + total.to_bytes(4, "little"))
        for _, d in chunks:
            fh.write(d)
    return total > 0


def export_archive(em, design, path):
    opts = em.createFusionArchiveExportOptions(path)
    return em.execute(opts)


def run(context):
    global _app, _ui
    _app = adsk.core.Application.get()
    _ui = _app.userInterface
    try:
        design = adsk.fusion.Design.cast(_app.activeProduct)
        if not design:
            _ui.messageBox("Open the robot design first.")
            return
        root = design.rootComponent
        design_name = safe_name(_app.activeDocument.name)

        dlg = _ui.createFolderDialog()
        dlg.title = "Choose the export folder (a new dated subfolder is created inside)"
        if dlg.showDialog() != adsk.core.DialogResults.DialogOK:
            return
        stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        out = os.path.join(dlg.folder, "%s_%s" % (design_name, stamp))
        for sub in ("assembly", "step", "print"):
            os.makedirs(os.path.join(out, sub), exist_ok=True)

        log("Fusion %s, design %s, root %s" % (_app.version, _app.activeDocument.name, root.name))
        entries = walk(root)
        stale = [e["name"] for e in entries if e["out_of_date"] is True]
        if stale:
            log("OUT OF DATE linked components: " + ", ".join(stale))
        write_tree(entries, out)
        write_joints(design, out)

        parts = [e for e in entries if e["bodies"] > 0]   # every component with geometry; the site decides what to publish
        choice = _ui.messageBox(
            "%d components, %d components with geometry.\n%s\n\n"
            "YES = full export (whole-robot STEP + f3z, STEP and STL per component).\n"
            "NO  = tree.csv only.\n\nOutput: %s"
            % (len(entries), len(parts),
               ("WARNING: %d linked components are out of date. Use Get Latest first for a release export." % len(stale))
               if stale else "No out-of-date linked components detected.", out),
            "Duke Humanoid V2 export", adsk.core.MessageBoxButtonTypes.YesNoCancelButtonType)
        if choice == adsk.core.DialogResults.DialogCancel:
            return
        if choice == adsk.core.DialogResults.DialogYes:
            em = design.exportManager
            prog = _ui.createProgressDialog()
            prog.isCancelButtonShown = True
            prog.show("Exporting", "Whole robot STEP", 0, len(parts) * 2 + 2)

            for label, fn in (("whole-robot STEP", lambda: export_step(em, root, os.path.join(out, "assembly", design_name + ".step"))),
                              ("Fusion archive", lambda: export_archive(em, design, os.path.join(out, "assembly", design_name + ".f3z")))):
                prog.message = label
                try:
                    log("%s: %s" % (label, "ok" if fn() else "FAILED"))
                except Exception:
                    log("%s: EXCEPTION %s" % (label, traceback.format_exc().splitlines()[-1]))
                prog.progressValue += 1
                adsk.doEvents()

            for e in parts:
                if prog.wasCancelled:
                    log("cancelled by user")
                    break
                fname = e["file_name"]
                for kind, sub, ext, fn in (("STEP", "step", ".step", export_step), ("STL", "print", ".stl", export_stl)):
                    prog.message = "%s %s" % (kind, fname)
                    path = os.path.join(out, sub, fname + ext)
                    try:
                        ok = fn(em, e["comp"], path)
                        log("%s %s: %s" % (kind, fname, "ok" if ok else "FAILED"))
                    except Exception:
                        log("%s %s: EXCEPTION %s" % (kind, fname, traceback.format_exc().splitlines()[-1]))
                    prog.progressValue += 1
                    adsk.doEvents()
            prog.hide()

        with open(os.path.join(out, "export.log"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(_log_lines) + "\n")
        failed = sum(1 for l in _log_lines if "FAILED" in l or "EXCEPTION" in l)
        _ui.messageBox("Done. %d problems (see export.log).\n%s" % (failed, out))
    except Exception:
        if _ui:
            _ui.messageBox("Failed:\n" + traceback.format_exc())
