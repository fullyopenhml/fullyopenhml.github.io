"""Fusion 360 script: re-export the components whose STL failed in fusion_export.

Run with humanoid_2.1_latest open; pick the dated export folder (the one with
tree.csv). It reads export.log, finds every "STL <file_name>: EXCEPTION/FAILED"
line, and exports those components again, body by body, through a short
temporary path (the failures were Windows' 260-character path limit on the
long vendor names, and body exports that Fusion silently skipped). Files land
under the same print/<file_name>.stl and step/<file_name>.step names tree.csv
uses, so the site tools pick them up unchanged. Bodies that still cannot be
exported are listed in export_missing.log.
"""

import csv
import os
import re
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
        dlg.title = "Pick the dated export folder (the one with tree.csv and export.log)"
        if dlg.showDialog() != adsk.core.DialogResults.DialogOK:
            return
        out = dlg.folder
        wanted = set()
        with open(os.path.join(out, "export.log"), encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"STL (.+?): (EXCEPTION|FAILED)", line.strip())
                if m:
                    wanted.add(m.group(1))
        # file_name -> component name via tree.csv
        by_file = {}
        with open(os.path.join(out, "tree.csv"), encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                by_file[r["file_name"]] = r["fusion_name"]
        comps = {}
        for occ in root.allOccurrences:
            comps.setdefault(occ.component.name, occ.component)

        em = design.exportManager
        tmp = tempfile.mkdtemp(prefix="dh_")
        done = 0
        for fn in sorted(wanted):
            comp = comps.get(by_file.get(fn, ""))
            if comp is None:
                log.append("%s: component not found" % fn)
                continue
            chunks = []
            for i, body in enumerate(comp.bRepBodies):
                p = os.path.join(tmp, "b%d.stl" % i)
                if os.path.exists(p):
                    os.remove(p)
                try:
                    o = em.createSTLExportOptions(body, p)
                    o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
                    o.isBinaryFormat = True
                    em.execute(o)
                except Exception:
                    log.append("%s body %d: %s" % (fn, i, traceback.format_exc().splitlines()[-1]))
                if os.path.exists(p):
                    with open(p, "rb") as f:
                        data = f.read()
                    n = int.from_bytes(data[80:84], "little")
                    chunks.append((n, data[84:84 + n * 50]))
                else:
                    log.append("%s body %d (%s): Fusion wrote no STL" % (fn, i, body.name))
            total = sum(n for n, _ in chunks)
            if total:
                dst = long_path(os.path.join(out, "print", fn + ".stl"))
                with open(dst, "wb") as f:
                    f.write(bytes(80) + total.to_bytes(4, "little"))
                    for _, d in chunks:
                        f.write(d)
                log.append("%s: STL ok (%d bodies, %d triangles)" % (fn, len(chunks), total))
                done += 1
            else:
                log.append("%s: STL FAILED (no body exported)" % fn)
            ps = os.path.join(tmp, "c.step")
            try:
                if em.execute(em.createSTEPExportOptions(ps, comp)):
                    shutil.copyfile(ps, long_path(os.path.join(out, "step", fn + ".step")))
                    log.append("%s: STEP ok" % fn)
            except Exception:
                log.append("%s: STEP %s" % (fn, traceback.format_exc().splitlines()[-1]))
        with open(os.path.join(out, "export_missing.log"), "w", encoding="utf-8") as fh:
            fh.write("Fusion %s" % app.version + chr(10) + chr(10).join(log) + chr(10))
        ui.messageBox("Done. %d of %d components re-exported. See export_missing.log." % (done, len(wanted)))
    except Exception:
        ui.messageBox("Failed:" + chr(10) + traceback.format_exc())
