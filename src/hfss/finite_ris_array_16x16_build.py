import os
import traceback

import ScriptEnv


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "data", "hfss", "finite_array")
if not os.path.isdir(OUT_DIR):
    os.makedirs(OUT_DIR)

LOG = os.path.join(OUT_DIR, "hfss_16x16_finite_array_build_log.txt")
PROJECT = os.path.join(OUT_DIR, "HFSS_28GHz_16x16_Finite_RIS_Array.aedt")


def log(msg):
    with open(LOG, "a") as f:
        f.write(str(msg) + "\n")


def make_box(oEditor, name, pos, size, mat, color, transparency=0.0, solve_inside=True):
    oEditor.CreateBox(
        [
            "NAME:BoxParameters",
            "XPosition:=", pos[0],
            "YPosition:=", pos[1],
            "ZPosition:=", pos[2],
            "XSize:=", size[0],
            "YSize:=", size[1],
            "ZSize:=", size[2],
        ],
        [
            "NAME:Attributes",
            "Name:=", name,
            "Flags:=", "",
            "Color:=", color,
            "Transparency:=", transparency,
            "PartCoordinateSystem:=", "Global",
            "UDMId:=", "",
            "MaterialValue:=", '"' + mat + '"',
            "SolveInside:=", solve_inside,
        ],
    )


def make_rect(oEditor, name, x, y, z, w, h, axis, mat, color, transparency=0.0, solve_inside=False):
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=", x,
            "YStart:=", y,
            "ZStart:=", z,
            "Width:=", w,
            "Height:=", h,
            "WhichAxis:=", axis,
        ],
        [
            "NAME:Attributes",
            "Name:=", name,
            "Flags:=", "",
            "Color:=", color,
            "Transparency:=", transparency,
            "PartCoordinateSystem:=", "Global",
            "UDMId:=", "",
            "MaterialValue:=", '"' + mat + '"',
            "SolveInside:=", solve_inside,
        ],
    )


def main():
    if os.path.exists(LOG):
        os.remove(LOG)

    ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
    oDesktop.RestoreWindow()
    log("AEDT initialized")

    if os.path.exists(PROJECT):
        try:
            os.remove(PROJECT)
        except Exception:
            pass

    oProject = oDesktop.NewProject()
    oProject.InsertDesign("HFSS", "HFSS_28GHz_16x16_Finite_RIS_Array", "DrivenModal", "")
    oDesign = oProject.SetActiveDesign("HFSS_28GHz_16x16_Finite_RIS_Array")
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.SetModelUnits(["NAME:Units Parameter", "Units:=", "mm", "Rescale:=", False])
    log("Project and design created")

    # 28 GHz: lambda0 ~= 10.71 mm. Element pitch p ~= lambda0/2.
    nx = 16
    ny = 16
    p = 5.36
    h_sub = 0.508
    patch_l = 3.20
    total_x = nx * p
    total_y = ny * p
    x0 = -total_x / 2
    y0 = -total_y / 2
    margin = 10.0
    air_h_top = 35.0
    air_h_bottom = 8.0

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
        "Substrate_16x16",
        ["{:.4f}mm".format(x0), "{:.4f}mm".format(y0), "{:.4f}mm".format(-h_sub)],
        ["{:.4f}mm".format(total_x), "{:.4f}mm".format(total_y), "{:.4f}mm".format(h_sub)],
        "Rogers RT/duroid 5880 (tm)",
        "(132 180 220)",
        0.35,
        True,
    )
    make_rect(
        oEditor,
        "Ground_16x16_PEC",
        "{:.4f}mm".format(x0),
        "{:.4f}mm".format(y0),
        "{:.4f}mm".format(-h_sub),
        "{:.4f}mm".format(total_x),
        "{:.4f}mm".format(total_y),
        "Z",
        "copper",
        "(180 180 180)",
        0.0,
    )

    patch_names = []
    for ix in range(nx):
        for iy in range(ny):
            cx = x0 + (ix + 0.5) * p
            cy = y0 + (iy + 0.5) * p
            # 2-bit phase-state visual coding: four patch sizes repeat across the aperture.
            state = (ix + 2 * iy) % 4
            l = [2.45, 2.95, 3.45, 3.95][state]
            name = "Patch_{:02d}_{:02d}_S{}".format(ix + 1, iy + 1, state)
            make_rect(
                oEditor,
                name,
                "{:.4f}mm".format(cx - l / 2),
                "{:.4f}mm".format(cy - l / 2),
                "0mm",
                "{:.4f}mm".format(l),
                "{:.4f}mm".format(l),
                "Z",
                "copper",
                ["(255 198 0)", "(255 160 0)", "(238 118 0)", "(210 82 0)"][state],
                0.0,
            )
            patch_names.append(name)
    log("Finite 16x16 RIS geometry created: {} patch elements".format(len(patch_names)))

    oBoundary = oDesign.GetModule("BoundarySetup")
    oBoundary.AssignPerfectE(
        [
            "NAME:PEC_RIS_Metals",
            "Objects:=", ["Ground_16x16_PEC"] + patch_names,
            "InfGroundPlane:=", False,
        ]
    )
    log("PEC assigned to ground and 256 patch elements")

    try:
        oBoundary.AssignRadiation(["NAME:Rad_AirBox", "Objects:=", ["AirBox"]])
        log("Radiation boundary assigned to AirBox")
    except Exception:
        log("Radiation boundary assignment failed")
        log(traceback.format_exc())

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
        log("Normal-incidence plane wave assigned")
    except Exception:
        log("Plane wave assignment failed; project still provides finite-array full-wave geometry evidence")
        log(traceback.format_exc())

    oAnalysis = oDesign.GetModule("AnalysisSetup")
    oAnalysis.InsertSetup(
        "HfssDriven",
        [
            "NAME:Setup1",
            "SolveType:=", "Single",
            "Frequency:=", "28GHz",
            "MaxDeltaS:=", 0.08,
            "UseMatrixConv:=", False,
            "MaximumPasses:=", 2,
            "MinimumPasses:=", 1,
            "MinimumConvergedPasses:=", 1,
            "PercentRefinement:=", 10,
            "IsEnabled:=", True,
            "BasisOrder:=", 1,
        ],
    )
    log("Conservative single-frequency setup inserted: 28 GHz, max passes=2")

    oProject.SaveAs(PROJECT, True)
    log("Project saved: " + PROJECT)
    log("Done: finite 16x16 RIS array HFSS project built")


try:
    main()
except Exception:
    log("ERROR")
    log(traceback.format_exc())
    raise
