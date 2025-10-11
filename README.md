# PVmismatch_study

A project to model **electrical mismatch losses** in PV arrays using the
[SunPower PVMismatch library] to plot basic I–V curves, P–V curves and losses.

---

## Project layout

```
PVmismatch_study/
├── LICENSE
├── README.md
├── requirements.txt
├── alternate_data/
│   └── Rs_curve.csv
│   └── Rsh_curve.csv
│   └── find_curves.py
│   └── module_specs.py
│   └── pv_system.py
├── alternate_simulation/
│   └── mismatch_models.py
│   └── mismatch_report.py
│   └── parametric_study.py
│   └── simulation.py
│   └── simulation.ipynb
├── examples/
│   └── ...
├── excel_tool/
│   └── string_summary_edited.xlsx
│   └── system_from_excel.py
└── mismatch_study/
    └── sys_healthy.py
    └── sys_degraded_fully.py
    └── sys_mismatched.py
    └── sys_mismatch_calculator.py
    └── sys_simulate.py
    └── sys_plotter.py                   
```

---

## How it works 
### alternate_data
- Find Rs and Rsh curve shapes in `find_curves.py` from study *Korgaonkar & Shiradkar, 
"Viability of performance improvement of degraded Photovoltaic plants through reconfiguration of PV modules,"* 2025. 
- Define a custom module in `module_specs.py`
- Define a PV system in `pv_system.py` with Rs or Rsh degradation as found above.

### alternate_simulation
- Define a mismatch model in `mismatch_models.py`
- Simulate the system in `simulation.py` and analyse its results.

### mismatch_study
- Define a healthy, fully degraded and mismatched PV system in `sys_healthy.py`, `sys_degraded_fully.py` and `sys_mismatched.py`
- Define a mismatch calculator in `sys_mismatch_calculator.py`
- Simulate the system in `sys_simulate.py` and analyse its results.
- Plot the results in `sys_plotter.py`

### excel_tool
- Define a PV system in `system_from_excel.py` from an Excel file and analyse its mismatch results.

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

---

## License

MIT
