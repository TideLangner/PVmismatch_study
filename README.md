# PVmismatch_study
## Created by Tide Langner (LNGTID001)
### MEC4128S at the University of Cape Town (UCT)

A project to model **electrical mismatch losses** in PV arrays using the
[SunPower PVMismatch library] to plot I–V curves, P–V curves and calculate losses.

---

## Project layout

```
PVmismatch_study/
├── LICENSE
├── README.md
├── requirements.txt
├── case_study_data/
│   └── Rs_curve.csv
│   └── Rsh_curve.csv
│   └── find_curves.py
│   └── module_specs.py
│   └── pv_system.py
├── case_study_simulation/
│   └── mismatch_models.py
│   └── mismatch_report.py
│   └── simulation.py
│   └── simulation.ipynb
├── examples/
│   └── ...
├── excel_tool/
│   └── string_summary_edited.xlsx
│   └── system_from_excel.ipynb
│   └── system_from_excel.py
└── mismatch_study/
    └── sys_healthy.py
    └── sys_degraded_fully.py
    └── sys_mismatched.py
    └── sys_mismatch_calculator.py
    └── sys_simulate.py
    └── sys_plotter.py  
    └── results/
    │   └── mode_1/
    │       └── surface_res1.metadata.json
    │       └── surface_res1.npz
    │   └── mode_2/
    │   └── mode_3/
    │   └── mode_4/
    │   └── mode_5/
    │   └── mode_6/
    ├── results_plotted/       
    │   └── mode_1/
    │   └── mode_2/
    │   └── mode_3/
    │   └── mode_4/
    │   └── mode_5/
    │   └── mode_6/          
```

---

## How it works 
### case_study_data
- Find Rs and Rsh curve shapes in `find_curves.py` from study *Korgaonkar & Shiradkar, 
"Viability of performance improvement of degraded Photovoltaic plants through reconfiguration of PV modules,"* 2025. 
- Define a custom module in `module_specs.py`.
- Define a PV system in `pv_system.py` with Rs or Rsh degradation as found above.

### case_study_simulation
- Define a mismatch system model in `mismatch_models.py`.
- Define a mismatch-calculating tool in `mismatch_report.py` to analyse losses in mismatch system. 
- Simulate examples and mismatched systems in `simulation.py` and analyse results.

### examples
- Define a basic 2x2 system and plots its I-V and P-V curves in `basic_mismatch.py`
- Basic tool for showing changes in I-V curve when changing Rs, Rsh, Ee in `iv_curve_shaper.py`

### excel_tool
- Define a PV system in `system_from_excel.py` from an Excel file and analyse its mismatch results.

### mismatch_study
- Define healthy and fully degraded baseline PV systems in `sys_healthy.py` and `sys_degraded_fully.py`. 
- Create mismatch system in `sys_mismatched.py` in numerous ways.
- Define a mismatch calculator/report in `sys_mismatch_calculator.py`.
- Run functions, simulations and plots in `sys_simulate.py`. This is the central file.
- Plot the results in `sys_plotter.py` which optionally save to `results_plotted` folder.
- `sys_save.py` saves simulation results in `results` folder in JSON format npz files.

---

## Quickstart

### 1) Create a virtual environment and install requirements
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> If PVMismatch fails to build on your platform, try Python 3.10–3.12 and a fresh venv.

---

## Citing / References

- **PVMismatch docs & API** (Quickstart, PVmodule/PVstring/PVsystem): sunpower.github.io/PVMismatch  
- **Definition of mismatch loss** (system MPP vs sum of module MPPs): PVsyst Help and
  *Chaudhari & Kimball et al., “Quantification of System‑Level Mismatch Losses using PVMismatch,”* 2018.
- **Study with Rs and Rsh degradation data** *Korgaonkar & Shiradkar, 
"Viability of performance improvement of degraded Photovoltaic plants through reconfiguration of PV modules,"* 2025.
- PyCharm AI assistant used to help build `iv_curve_shaper.py` in `examples`.
- PyCharm AI assistant used to populate some scripts with additional comments. 

---

## License

MIT
