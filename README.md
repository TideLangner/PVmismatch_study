# PV Mismatch Basic (PVMismatch)

A small, beginner-friendly project to model **electrical mismatch losses** in PV strings/arrays using the
[SunPower PVMismatch library] and to plot basic I–V and P–V curves.

> **Scope (now):** basic STC-style modeling from datasheet-like inputs (Voc, Isc, Vmp, Imp), put modules into a string, then into an array, and quantify mismatch as
> \(1 - P_{mpp,system} / \sum P_{mpp,module}\).  
> **Future:** extend to **non‑uniform degradation** scenarios and more rigorous parameter fitting.

---

## Quickstart

### 1) Create a virtual environment and install deps
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> If PVMismatch fails to build on your platform, try Python 3.10–3.12 and a fresh venv.


### 2) Run the basic demo
```bash
python scripts/basic_demo.py \
  --voc 40.1 --isc 9.7 --vmp 33.2 --imp 9.3 \
  --nrows 10 --ncols-per-substr 2 2 2 \
  --mods-per-string 12 --n-strings 2 \
  --area-tol-pct 3 --seed 42
```

This will:
- Build a **60‑cell** module (10 rows, 3 substrings with 2 columns/substring → 20 cells/substring).
- Assemble a **2×12** (2 strings × 12 modules per string) array.
- Apply a **±3% current tolerance** (as cell area scaling) to emulate manufacturing dispersion.
- Plot **I–V** and **P–V** curves for the **system** and the **first string** to `outputs/`.
- Print the **STC mismatch loss** for the string and the system.

Example output files:
```
outputs/
  system_iv.png
  system_pv.png
  string0_iv.png
  string0_pv.png
```

---

## How it works (short)

- We build a module layout using `standard_cellpos_pat(nrows, ncols_per_substr)` from PVMismatch.  
- We **scale cell area** to match the datasheet **Isc** at STC (Ee=1.0, Tc=25°C). This is a simple
  first‑order calibration that preserves voltages reasonably for common c‑Si modules.
- We compute the **MPP** of each module *in isolation* and the **MPP** of the connected **string/system**.
- **Mismatch loss [%]** = `100 * (1 - Pmp_system / sum(Pmp_modules_isolated))`.

> Notes:
> - This is **basic** and not a full datasheet parameter fit. For close tracking of (Vmp, Voc) / FF,
>   you can extend `pv_builders.fit_module_to_datasheet()` later by tuning cell Rs/Rsh or per‑cell parameters.
> - You can add non‑uniform **degradation** or **soiling/shading** by using `setSuns()`/`setTemps()`
>   at cell/substring/module granularity on `PVmodule`, `PVstring`, or `PVsystem` objects.


---

## Citing / References

- **PVMismatch docs & API** (Quickstart, PVmodule/PVstring/PVsystem): sunpower.github.io/PVMismatch  
- **Definition of mismatch loss** (system MPP vs sum of module MPPs): PVsyst Help and
  *Chaudhari & Kimball et al., “Quantification of System‑Level Mismatch Losses using PVMismatch,”* 2018.

---

## Project layout

```
pv-mismatch-basic/
├── LICENSE
├── README.md
├── requirements.txt
├── examples/
│   └── datasheets/
│       └── sample_60cell.yaml
├── scripts/
│   └── basic_demo.py
└── src/
    └── mismatch_model/
        ├── __init__.py
        ├── datasheet.py
        ├── mismatch.py
        └── pv_builders.py
```

---

## FAQ / Tips

- **Matching a 60‑cell module**: use `--nrows 10 --ncols-per-substr 2 2 2` (3 substrings × 20 cells).
- **Different layouts**: change rows/columns per substring to get 72‑cell (12×2 2 2), 66‑cell, etc.
- **Uniform degradation / soiling**: scale all modules with `--area-tol-pct -2` (or use `setSuns()`).
- **Non‑uniform degradation**: later, extend `apply_degradation()` to target substrings or cells.


---

## License

MIT
