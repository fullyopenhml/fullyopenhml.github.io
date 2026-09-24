"""Fusion 360 script: world transforms of every part, plus bodies-only meshes.

Run with humanoid_2.1_latest open; pick the SAME dated export folder as before.
Writes into it:

  transforms.csv                 one row per occurrence that has bodies:
                                 path, fusion component name, and the 4x4 transform
                                 from component coordinates to the root (cm, row-major)
  print/<component>.stl          only for CNC_/3DP_ components that also contain
                                 children: their own bodies, component coordinates
  step/<component>.step          same components (STEP includes the children)

tools/build_viewer.py places the per-component meshes with these transforms, so
the viewer no longer depends on how Fusion positions an occurrence export.
"""

import csv
import os
import re
import tempfile
import traceback

import adsk.core
import adsk.fusion


def safe_name(name):
    name = re.sub(r"\s*v\d+$", "", name.strip())
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "unnamed"


def stl_bodies(em, bodies, path):
    tmp = tempfile.mkdtemp()
    chunks = []
    for i, b in enumerate(bodies):
        p = os.path.join(tmp, "%d.stl" % i)
        o = em.createSTLExportOptions(b, p)
        o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        o.isBinaryFormat = True
        if em.execute(o):
            with open(p, "rb") as fh:
                data = fh.read()
            n = int.from_bytes(data[80:84], "little")
            chunks.append((n, data[84:84 + n * 50]))
    total = sum(n for n, _ in chunks)
    with open(path, "wb") as fh:
        fh.write(b"\0" * 80 + total.to_bytes(4, "little"))
        for _, d in chunks:
            fh.write(d)
    return total > 0


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
        for sub in ("step", "print"):
            os.makedirs(os.path.join(out, sub), exist_ok=True)
        em = design.exportManager

        rows = []
        done = set()
        for occ in root.allOccurrences:
            comp = occ.component
            if comp.bRepBodies.count == 0:
                continue
            t = occ.transform2 if hasattr(occ, "transform2") else occ.transform
            m = t.asArray()
            rows.append([occ.fullPathName, comp.name, safe_name(comp.name), occ.isVisible] + ["%.6f" % x for x in m])
            name = comp.name
            if name.startswith(("CNC_", "3DP_")) and comp.occurrences.count > 0 and name not in done:
                done.add(name)
                fn = safe_name(name)
                ok1 = em.execute(em.createSTEPExportOptions(os.path.join(out, "step", fn + ".step"), comp))
                ok2 = stl_bodies(em, list(comp.bRepBodies), os.path.join(out, "print", fn + ".stl"))
                log.append("%s: STEP %s, STL %s" % (fn, ok1, ok2))
        with open(os.path.join(out, "transforms.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["path", "fusion_name", "file_name", "visible"] + ["m%d" % i for i in range(16)])
            w.writerows(rows)
        with open(os.path.join(out, "export_transforms.log"), "w", encoding="utf-8") as fh:
            fh.write("Fusion %s\n" % app.version + "\n".join(log) + "\n")
        ui.messageBox("Done. %d occurrences, %d mixed components exported.\n%s" % (len(rows), len(done), out))
    except Exception:
        ui.messageBox("Failed:\n" + traceback.format_exc())
