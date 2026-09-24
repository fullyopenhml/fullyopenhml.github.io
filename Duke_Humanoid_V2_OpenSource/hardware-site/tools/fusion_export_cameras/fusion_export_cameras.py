"""Fusion 360 script: export the RealSense camera components as whole-occurrence STLs.

The D435 component holds its housing as a mesh body, which a body-by-body
BRep export skips (fusion_export wrote no STL for it). An occurrence export
includes mesh bodies and children and is written in the component's own
coordinates, which is exactly what tools/build_viewer.py places with
transforms.csv. The field-of-view wedges come along and are dropped there by
the 450 mm rule.

Run with humanoid_2.1_latest open; pick the dated export folder (the one with
tree.csv). Overwrites print/<file_name>.stl for every component whose name
contains "IntelRealsense" (file names from tree.csv), high resolution.
"""

import csv
import os
import shutil
import tempfile
import traceback

import adsk.core
import adsk.fusion


def long_path(p):
    p = os.path.abspath(p)
    return p if p.startswith("\\\\?\\") else "\\\\?\\" + p


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
        names = {}
        with open(os.path.join(out, "tree.csv"), encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                if "intelrealsense" in r["fusion_name"].lower():
                    names.setdefault(r["fusion_name"], r["file_name"])
        em = design.exportManager
        tmp = tempfile.mkdtemp(prefix="dh_cam_")
        done = set()
        for occ in root.allOccurrences:
            comp = occ.component
            if comp.name not in names or comp.name in done:
                continue
            done.add(comp.name)
            try:
                nmesh = comp.meshBodies.count
            except Exception:
                nmesh = -1
            p = os.path.join(tmp, "occ.stl")
            o = em.createSTLExportOptions(occ, p)
            o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            o.isBinaryFormat = True
            ok = em.execute(o) and os.path.exists(p)
            if ok:
                shutil.copyfile(p, long_path(os.path.join(out, "print", names[comp.name] + ".stl")))
            log.append("%s (%d BRep bodies, %d mesh bodies): %s" % (
                comp.name, comp.bRepBodies.count, nmesh, "ok %d bytes" % os.path.getsize(p) if ok else "FAILED"))
        with open(os.path.join(out, "export_cameras.log"), "w", encoding="utf-8") as fh:
            fh.write("Fusion %s" % app.version + chr(10) + chr(10).join(log) + chr(10))
        ui.messageBox("Done." + chr(10) + chr(10).join(log))
    except Exception:
        ui.messageBox("Failed:" + chr(10) + traceback.format_exc())
