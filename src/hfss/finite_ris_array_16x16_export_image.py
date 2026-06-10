import os
import traceback

import ScriptEnv


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "data", "hfss", "finite_array")
PROJECT = os.path.join(OUT_DIR, "HFSS_28GHz_16x16_Finite_RIS_Array.aedt")
LOG = os.path.join(OUT_DIR, "hfss_16x16_finite_array_export_log.txt")
PNG = os.path.join(OUT_DIR, "hfss_16x16_native_model_export.png")


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
    oProject = oDesktop.SetActiveProject("HFSS_28GHz_16x16_Finite_RIS_Array")
    oDesign = oProject.SetActiveDesign("HFSS_28GHz_16x16_Finite_RIS_Array")
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    log("Project opened: " + PROJECT)
    try:
        oBoundary = oDesign.GetModule("BoundarySetup")
        log("Boundaries: " + ", ".join(list(oBoundary.GetBoundaries())))
    except Exception:
        log("Boundary list unavailable")
        log(traceback.format_exc())
    try:
        oEditor.FitAll()
        log("FitAll OK")
    except Exception:
        log("FitAll failed")
        log(traceback.format_exc())
    oEditor.ExportModelImageToFile(
        PNG,
        2200,
        1350,
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
    log("Exported native HFSS 16x16 model image: " + PNG)
    oProject.Save()
    log("Project saved")
except Exception:
    log("ERROR")
    log(traceback.format_exc())
    raise
