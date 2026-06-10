import os
import traceback

import ScriptEnv


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "data", "hfss", "periodic_unit")
PROJECT = os.path.join(OUT_DIR, "HFSS_28GHz_Periodic_RIS_UnitCell.aedt")
LOG = os.path.join(OUT_DIR, "hfss_periodic_native_export_log.txt")
PNG = os.path.join(OUT_DIR, "hfss_periodic_native_model_export.png")


def log(msg):
    with open(LOG, "a") as f:
        f.write(str(msg) + "\n")


try:
    if os.path.exists(LOG):
        os.remove(LOG)
    ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
    oDesktop.RestoreWindow()
    log("AEDT initialized")
    oDesktop.OpenProject(PROJECT)
    oProject = oDesktop.SetActiveProject("HFSS_28GHz_Periodic_RIS_UnitCell")
    oDesign = oProject.SetActiveDesign("HFSS_28GHz_Periodic_RIS_UnitCell")
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oBoundary = oDesign.GetModule("BoundarySetup")
    log("Project opened: " + PROJECT)
    try:
        log("Boundaries: " + ", ".join(list(oBoundary.GetBoundaries())))
    except Exception:
        log("Boundary list unavailable")
    try:
        oEditor.FitAll()
        log("FitAll OK")
    except Exception:
        log("FitAll failed")
        log(traceback.format_exc())
    oEditor.ExportModelImageToFile(
        PNG,
        1800,
        1100,
        [
            "NAME:SaveImageParams",
            "ShowAxis:=",
            True,
            "ShowGrid:=",
            True,
            "ShowRuler:=",
            False,
        ],
    )
    log("Exported native HFSS model image: " + PNG)
    oProject.Save()
    log("Project saved")
except Exception:
    log("ERROR")
    log(traceback.format_exc())
    raise
