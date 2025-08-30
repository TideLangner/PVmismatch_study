# PV Mismatch Basic (PVMismatch)

A project to model **electrical mismatch losses** in PV arrays using the
[SunPower PVMismatch library] and to plot basic I–V and P–V curves.

> **Current Scope:** basic STC module modelling from datasheet inputs (Voc, Isc, Vmp, Imp), put into arrays and quantifying mismatch over 
> varying scenarios such as module degradation, shading, decreased irradiance and increased temperature.
> **Goal:** compute the STC mismatch losses as a percentage of the system MPP and/or module equivalence. 
> **Future:** extend to non‑uniform degradation scenarios and more rigorous parameter fitting.

---

## Quickstart

### 1) Create a virtual environment and install requirements
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> If PVMismatch fails to build on your platform, try Python 3.10–3.13 and a fresh venv.

---

## How it works (short)

- Build a custom module in module_specs.py
- Build a healthy PV system in pv_system.py 
- Create degraded/shaded/hot/combination systems in mismatch_models.py
- Simulate the systems in simulation.py and analyse their results.

---

## Citing / References

- **PVMismatch docs & API** (Quickstart, PVmodule/PVstring/PVsystem): sunpower.github.io/PVMismatch  
- **Definition of mismatch loss** (system MPP vs sum of module MPPs): PVsyst Help and
  *Chaudhari & Kimball et al., “Quantification of System‑Level Mismatch Losses using PVMismatch,”* 2018.

---

## Project layout

```
PVmismatch_study/
├── LICENSE
├── README.md
├── requirements.txt
├── data/
│   └── module_specs.py
│   └── find_Rsh_curve.py
│   └── Rsh_curve.csv
└── src/
    ├── pv_system.py
    ├── mismatch_models.py
    ├── simulation.py
    └── simulation.ipynb
```

---

## License

MIT
