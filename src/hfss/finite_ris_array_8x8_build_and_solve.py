import os
import traceback

import ScriptEnv


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "data", "hfss", "finite_array")
if not os.path.isdir(OUT_DIR):
    os.makedirs(OUT_DIR)

LOG = os.path.join(OUT_DIR, "hfss_8x8_finite_array_build_solve_log.txt")
PROJECT = os.path.join(OUT_DIR, "HFSS_28GHz_8x8_Finite_RIS_Array.aedt")
PNG = os.path.join(OUT_DIR, "hfss_8x8_native_model_export.png")


def log(msg):
    with open(LOG, "a") as f:
        f.write(str(msg) + "\n")


def make_box(oEditor, name, pos, size, mat, color, transparency=0.0, solve_inside=True):
    oEditor.CreateBox(
        ["NAME:BoxParameters", "XPosition:=", pos[0], "YPosition:=", pos[1], "ZPosition:=", pos[2], "XSize:=", size[0], "YSize:=", size[1], "ZSize:=", size[2]],
        ["NAME:Attributes", "Name:=", name, "Flags:=", "", "Color:=", color, "Transparency:=", transparency, "PartCoordinateSystem:=", "Global", "UDMId:=", "", "MaterialValue:=", '"' + mat + '"', "SolveInside:=", solve_inside],
    )


def make_rect(oEditor, name, x, y, z, w, h, axis, mat, color, transparency=0.0, solve_inside=False):
    oEditor.CreateRectangle(
        ["NAME:RectangleParameters", "IsCovered:=", True, "XStart:=", x, "YStart:=", y, "ZStart:=", z, "Width:=", w, "Height:=", h, "WhichAxis:=", axis],
        ["NAME:Attributes", "Name:=", name, "Flags:=", "", "Color:=", color, "Transparency:=", transparency, "PartCoordinateSystem:=", "Global", "UDMId:=", "", "MaterialValue:=", '"' + mat + '"', "SolveInside:=", solve_inside],
    )


try:
    if os.path.exists(LOG):
        os.remove(LOG)

    ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
    oDesktop.RestoreWindow()
    log("AEDT initialized")

    oProject = oDesktop.NewProject()
    oProject.InsertDesign("HFSS", "HFSS_28GHz_8x8_Finite_RIS_Array", "DrivenModal", "")
    oDesign = oProject.SetActiveDesign("HFSS_28GHz_8x8_Finite_RIS_Array")
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.SetModelUnits(["NAME:Units Parameter", "Units:=", "mm", "Rescale:=", False])
    log("Project and design created")

    nx = 8
    ny = 8
    p = 5.36
    h_sub = 0.508
    total_x = nx * p
    total_y = ny * p
    x0 = -total_x / 2
    y0 = -total_y / 2
    margin = 8.0
    air_h_top = 24.0
    air_h_bottom = 6.0

    make_box(
        oEditor,
        "AirBox",
        ["{:.4f}mm".format(x0 - margin), "{:.4f}mm".format(y0 - margin), "{:.4f}mm".format(-h_sub - air_h_bottom)],
        ["{:.4f}mm".format(total_x + 2 * margin), "{:.4f}mm".format(total_y + 2 * margin), "{:.4f}mm".format(air_h_top + air_h_bottom + h_sub)],
        "air",
        "(185 225 255)",
        0.88,
        True,
    )
    make_box(
        oEditor,
        "Substrate_8x8",
        ["{:.4f}mm".format(x0), "{:.4f}mm".format(y0), "{:.4f}mm".format(-h_sub)],
        ["{:.4f}mm".format(total_x), "{:.4f}mm".format(total_y), "{:.4f}mm".format(h_sub)],
        "Rogers RT/duroid 5880 (tm)",
        "(132 180 220)",
        0.35,
        True,
    )
    make_rect(oEditor, "Ground_8x8_PEC", "{:.4f}mm".format(x0), "{:.4f}mm".format(y0), "{:.4f}mm".format(-h_sub), "{:.4f}mm".format(total_x), "{:.4f}mm".format(total_y), "Z", "copper", "(180 180 180)")

    patch_names = []
    for ix in range(nx):
        for iy in range(ny):
            cx = x0 + (ix + 0.5) * p
            cy = y0 + (iy + 0.5) * p
            state = (ix + 2 * iy) % 4
            l = [2.45, 2.95, 3.45, 3.95][state]
            name = "Patch_{:02d}_{:02d}_S{}".format(ix + 1, iy + 1, state)
            make_rect(oEditor, name, "{:.4f}mm".format(cx - l / 2), "{:.4f}mm".format(cy - l / 2), "0mm", "{:.4f}mm".format(l), "{:.4f}mm".format(l), "Z", "copper", ["(255 198 0)", "(255 160 0)", "(238 118 0)", "(210 82 0)"][state])
            patch_names.append(name)
    log("Finite 8x8 RIS geometry created: {} patch elements".format(len(patch_names)))

    oBoundary = oDesign.GetModule("BoundarySetup")
    oBoundary.AssignPerfectE(["NAME:PEC_RIS_Metals", "Objects:=", ["Ground_8x8_PEC"] + patch_names, "InfGroundPlane:=", False])
    log("PEC assigned to ground and 64 patch elements")

    oBoundary.AssignRadiation(["NAME:Rad_AirBox", "Objects:=", ["AirBox"]])
    log("Radiation boundary assigned")

    try:
        oBoundary.AssignPlaneWave(
            [
                "NAME:PW_Normal_Incidence",
                "Objects:=", ["AirBox"],
                "IsCartesian:=", True,
                "EoX:=", "1V_per_meter",
                "EoY:=", "0V_per_meter",
                "EoZ:=", "0V_per_meter",
                "kX:=", "0",
                "kY:=", "0",
                "kZ:=", "-1",
                "OriginX:=", "0mm",
                "OriginY:=", "0mm",
                "OriginZ:=", "{:.4f}mm".format(air_h_top / 2),
            ]
        )
        log("Plane wave assigned")
    except Exception:
        log("Plane wave assignment failed")
        log(traceback.format_exc())

    oAnalysis = oDesign.GetModule("AnalysisSetup")
    oAnalysis.InsertSetup(
        "HfssDriven",
        [
            "NAME:Setup1",
            "SolveType:=", "Single",
            "Frequency:=", "28GHz",
            "MaxDeltaS:=", 0.10,
            "UseMatrixConv:=", False,
            "MaximumPasses:=", 1,
            "MinimumPasses:=", 1,
            "MinimumConvergedPasses:=", 1,
            "PercentRefinement:=", 5,
            "IsEnabled:=", True,
            "BasisOrder:=", 1,
        ],
    )
    log("Conservative 8x8 single-frequency setup inserted")

    oProject.SaveAs(PROJECT, True)
    log("Project saved: " + PROJECT)
    oEditor.FitAll()
    oEditor.ExportModelImageToFile(PNG, 1900, 1200, ["NAME:SaveImageParams", "ShowAxis:=", True, "ShowGrid:=", True, "ShowRuler:=", False])
    log("Native HFSS 8x8 model image exported: " + PNG)

    log("AnalyzeAll started: 8x8 finite-array sanity full-wave solve")
    oDesign.AnalyzeAll()
    log("AnalyzeAll completed")
    oProject.Save()
    log("Project saved after solve")
except Exception:
    log("ERROR")
    log(traceback.format_exc())
    raise
