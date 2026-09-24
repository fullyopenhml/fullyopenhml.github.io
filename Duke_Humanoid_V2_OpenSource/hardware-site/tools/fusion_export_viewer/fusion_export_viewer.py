"""Fusion 360 script: export the meshes for the interactive part viewer.

Run it from Fusion 360 with humanoid_2.1_latest open:
  UTILITIES > ADD-INS > Scripts and Add-Ins > Scripts > fusion_export_viewer > Run

It asks for an output folder and writes, in WORLD coordinates (assembly position):

  <out>/context.stl              the whole robot, low resolution, one mesh (grey backdrop)
  <out>/parts/<NNNN>.stl         one low-resolution mesh per occurrence of a releasable part
  <out>/occurrences.csv          NNNN, fusion component name, occurrence path, subassembly
  <out>/export.log

A part is releasable when its component name starts with CNC_ or 3DP_, or is one
of the named printed components below (same list as tools/gen_printed.py).
tools/build_viewer.py turns this folder into docs/assets/viewer/*.glb.
"""

import csv
import os
import re
import traceback

import adsk.core
import adsk.fusion

EXTRA = {"Component5", "Component34", "Component35", "Component36", "Component37", "Component38",
         "Component39", "Component40", "Component41", "Component42", "Component43", "Component44",
         "Component45", "Component194", "Component195", "Component196", "Component197",
         "Component198", "Component199", "symmetric_sole", "foot_front"}

_log = []


def releasable(name):
    return name.startswith(("CNC_", "3DP_")) or name in EXTRA


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Open the robot design first.")
            return
        root = design.rootComponent
        dlg = ui.createFolderDialog()
        dlg.title = "Folder for the viewer meshes (a 'viewer' subfolder is created)"
        if dlg.showDialog() != adsk.core.DialogResults.DialogOK:
            return
        out = os.path.join(dlg.folder, "viewer")
        os.makedirs(os.path.join(out, "parts"), exist_ok=True)
        em = design.exportManager

        occs = [o for o in root.allOccurrences if releasable(o.component.name) and o.isVisible]
        _log.append("Fusion %s; %d releasable occurrences" % (app.version, len(occs)))
        prog = ui.createProgressDialog()
        prog.isCancelButtonShown = True
        prog.show("Viewer export", "context mesh", 0, len(occs) + 1)

        opts = em.createSTLExportOptions(root, os.path.join(out, "context.stl"))
        opts.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementLow
        opts.isBinaryFormat = True
        _log.append("context: %s" % ("ok" if em.execute(opts) else "FAILED"))
        prog.progressValue = 1
        adsk.doEvents()

        rows = []
        for i, occ in enumerate(occs):
            if prog.wasCancelled:
                _log.append("cancelled")
                break
            name = occ.component.name
            prog.message = name
            fn = "%04d.stl" % i
            try:
                opts = em.createSTLExportOptions(occ, os.path.join(out, "parts", fn))
                opts.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementLow
                opts.isBinaryFormat = True
                ok = em.execute(opts)
            except Exception:
                ok = False
                _log.append("%s %s: EXCEPTION %s" % (fn, name, traceback.format_exc().splitlines()[-1]))
            path = occ.fullPathName
            rows.append([fn if ok else "", name, path, path.split("+")[0].split(":")[0]])
            if not ok:
                _log.append("%s %s: FAILED" % (fn, name))
            prog.progressValue += 1
            adsk.doEvents()
        prog.hide()

        with open(os.path.join(out, "occurrences.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["file", "fusion_name", "path", "top_level"])
            w.writerows(rows)
        with open(os.path.join(out, "export.log"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(_log) + "\n")
        bad = sum(1 for l in _log if "FAILED" in l or "EXCEPTION" in l)
        ui.messageBox("Done. %d meshes, %d problems.\n%s" % (len(rows), bad, out))
    except Exception:
        ui.messageBox("Failed:\n" + traceback.format_exc())
