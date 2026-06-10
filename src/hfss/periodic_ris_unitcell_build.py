import os
import traceback

import ScriptEnv


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "data", "hfss", "periodic_unit")
if not os.path.isdir(OUT_DIR):
    os.makedirs(OUT_DIR)

LOG = os.path.join(OUT_DIR, "hfss_periodic_ris_unitcell_log.txt")
PROJECT = os.path.join(OUT_DIR, "HFSS_28GHz_Periodic_RIS_UnitCell.aedt")


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

    oProject = oDesktop.NewProject()
    oProject.InsertDesign("HFSS", "HFSS_28GHz_Periodic_RIS_UnitCell", "DrivenModal", "")
    oDesign = oProject.SetActiveDesign("HFSS_28GHz_Periodic_RIS_UnitCell")
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    oEditor.SetModelUnits(["NAME:Units Parameter", "Units:=", "mm", "Rescale:=", False])
    log("Project and design created")

    # 28 GHz: lambda0 ~= 10.71 mm, p ~= lambda0/2.
    p = "5.36mm"
    half = "2.68mm"
    h_sub = "0.508mm"
    air_h = "5.0mm"
    patch_l = "3.20mm"
    patch_half = "1.60mm"

    make_box(oEditor, "AirCell", ["-2.68mm", "-2.68mm", "0mm"], [p, p, air_h], "air", "(180 230 255)", 0.88, True)
    make_box(oEditor, "Substrate", ["-2.68mm", "-2.68mm", "-0.508mm"], [p, p, h_sub], "Rogers RT/duroid 5880 (tm)", "(132 180 220)", 0.35, True)
    make_rect(oEditor, "Ground_PEC", "-2.68mm", "-2.68mm", "-0.508mm", p, p, "Z", "copper", "(180 180 180)", 0.0)
    make_rect(oEditor, "Patch_PEC", "-1.60mm", "-1.60mm", "0mm", patch_l, patch_l, "Z", "copper", "(255 170 0)", 0.0)
    make_rect(oEditor, "Floquet_Port_Top", "-2.68mm", "-2.68mm", air_h, p, p, "Z", "vacuum", "(80 160 255)", 0.78, True)
    log("Standard RIS unit geometry created: patch/substrate/ground/air cell/Floquet sheet")

    oBoundary = oDesign.GetModule("BoundarySetup")
    oBoundary.AssignPerfectE(
        [
            "NAME:PEC_Metals",
            "Objects:=", ["Ground_PEC", "Patch_PEC"],
            "InfGroundPlane:=", False,
        ]
    )
    log("PEC assigned to patch and ground")

    # HFSS 2020 R1 supports automatic lattice-pair identification for square periodic cells.
    # This replaces the previous lumped-port/feedline model and represents an infinite periodic RIS surface.
    try:
        before = list(oBoundary.GetBoundaries())
        oBoundary.AutoIdentifyLatticePair("Global:XY", "AirCell")
        after = list(oBoundary.GetBoundaries())
        log("AutoIdentifyLatticePair created: " + ", ".join([x for x in after if x not in before]))
    except Exception:
        log("AutoIdentifyLatticePair failed")
        log(traceback.format_exc())
        raise

    try:
        oBoundary.AssignFloquetPort(
            [
                "NAME:FloquetPort1",
                "Objects:=", ["Floquet_Port_Top"],
                "NumModes:=", 2,
                "DoDeembed:=", False,
                "DeembedDist:=", "0mm",
                "RenormalizeAllTerminals:=", True,
                [
                    "NAME:Modes",
                    ["NAME:Mode1", "ModeNum:=", 1, "UseIntLine:=", False, "CharImp:=", "Zpi"],
                    ["NAME:Mode2", "ModeNum:=", 2, "UseIntLine:=", False, "CharImp:=", "Zpi"],
                ],
                "ShowReporterFilter:=", True,
                "ReporterFilter:=", [True, True],
                [
                    "NAME:LatticeAVector",
                    "Coordinate System:=", "Global",
                    "Start:=", ["-2.68mm", "-2.68mm", air_h],
                    "End:=", ["2.68mm", "-2.68mm", air_h],
                ],
                [
                    "NAME:LatticeBVector",
                    "Coordinate System:=", "Global",
                    "Start:=", ["-2.68mm", "-2.68mm", air_h],
                    "End:=", ["-2.68mm", "2.68mm", air_h],
                ],
            ]
        )
        log("Floquet port assigned on top sheet with normal-incidence lattice vectors")
    except Exception:
        log("AssignFloquetPort failed")
        log(traceback.format_exc())
        raise

    oAnalysis = oDesign.GetModule("AnalysisSetup")
    oAnalysis.InsertSetup(
        "HfssDriven",
        [
            "NAME:Setup1",
            "SolveType:=", "Single",
            "Frequency:=", "28GHz",
            "MaxDeltaS:=", 0.04,
            "UseMatrixConv:=", False,
            "MaximumPasses:=", 5,
            "MinimumPasses:=", 1,
            "MinimumConvergedPasses:=", 1,
            "PercentRefinement:=", 25,
            "IsEnabled:=", True,
            "BasisOrder:=", 1,
        ],
    )
    oProject.SaveAs(PROJECT, True)
    log("Project saved: " + PROJECT)

    # Keep the script lightweight for course delivery: the project is ready for
    # single-point solve and patch-length parametric sweeps in the HFSS GUI.
    # Full phase library derivation is documented in the companion CSV/plot script.
    log("Done: standard periodic RIS unit cell project built")


try:
    main()
except Exception:
    log("ERROR")
    log(traceback.format_exc())
    raise
