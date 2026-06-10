import os
import traceback

import ScriptEnv


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "data", "hfss", "periodic_unit")
LOG = os.path.join(OUT_DIR, "hfss_periodic_ris_unitcell_solve_log.txt")
PROJECT = os.path.join(OUT_DIR, "HFSS_28GHz_Periodic_RIS_UnitCell.aedt")


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
    log("Project opened")
    try:
        oBoundary = oDesign.GetModule("BoundarySetup")
        log("Boundaries: " + ", ".join(list(oBoundary.GetBoundaries())))
    except Exception:
        log("Boundary list unavailable")
        log(traceback.format_exc())
    oDesign.AnalyzeAll()
    log("AnalyzeAll completed")
    oProject.Save()
    log("Project saved")
except Exception:
    log("ERROR")
    log(traceback.format_exc())
    raise
