# Reproduce The Evidence

Run commands from the repository root.

## Python Figures

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Regenerate the clean Python evidence figures:

```powershell
python .\src\python\generate_periodic_ris_codebook.py
python .\src\python\make_periodic_unitcell_geometry_diagram.py
python .\src\python\make_hfss_to_system_interface_dashboard.py
python .\src\python\generate_statistical_ci_chart.py
```

## MATLAB Figures

Open MATLAB at the repository root and run:

```matlab
run('src/matlab/generate_ris_reproducibility_evidence.m')
run('src/matlab/generate_qkd_ris_system_evidence.m')
```

These scripts regenerate array-level RIS evidence and QKD/weather/key-pool system evidence under `data/figures/`.

## HFSS / AEDT Projects

Open the included projects directly in Ansys Electronics Desktop:

- `data/hfss/periodic_unit/HFSS_28GHz_Periodic_RIS_UnitCell.aedt`
- `data/hfss/finite_array/HFSS_28GHz_16x16_Finite_RIS_Array.aedt`
- `data/hfss/finite_array/HFSS_28GHz_8x8_Finite_RIS_Array.aedt`

The corresponding automation scripts are under `src/hfss/`. They are intended to be run from the AEDT scripting environment because they use `ScriptEnv`.

The periodic unit-cell model uses patch/substrate/ground geometry, lattice-pair periodic boundaries, and Floquet-port plane-wave excitation. The finite-array projects provide native HFSS engineering evidence for large RIS-array geometry; 16x16 solves may require more memory than a normal laptop or desktop.
