# Tool for defining a system from an Excel file

import pandas as pd
import re
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from pvmismatch.pvmismatch_lib import pvcell, pvmodule, pvstring, pvsystem
from new.sys_mismatch_calculator import loss_calculator


num_inverters = 43
num_channels_per_inv = 14
num_strs_per_channel = 2
num_strs = num_inverters * num_channels_per_inv * num_strs_per_channel
num_modules_per_str = 30

# Healthy cell characteristics (STC baseline)
HEALTHY_PARAMS = dict(
    Rs=0.00641575,
    Rsh=285.79,
    Isc0_T0=8.69,
    alpha_Isc=0.00060,
    Isat1_T0=1.79556E-10,
    Isat2_T0=1.2696E-5,
)

# Degradation multipliers for levels 1-6
# Matches the factors used for 10%, 20%, 30% degradation etc.
DEG_LEVELS = {
    1: (1.965, 1.965),  # Rs*1.965 ; Rsh/1.965
    2: (2.980, 2.980),  # Rs*2.980 ; Rsh/2.980
    3: (4.070, 4.070),  # Rs*4.070 ; Rsh/4.070
    4: (5.300, 5.300),  # Rs*5.300 ; Rsh/5.300
    5: (6.815, 6.815),  # Rs*6.815 ; Rsh/6.815
    6: (8.970, 8.970),  # Rs*8.970 ; Rsh/8.970
}

def _inv_code(inverter: int) -> str:
    return f"I0{inverter}" if inverter < 10 else f"I{inverter}"

def _parse_str_index(string_name: str) -> int:
    """
    Extracts the global string index (1..28) from names like '..._STR06'.
    Returns 1-based int. Raises ValueError if not found.
    """
    m = re.search(r"STR(\d+)", str(string_name))
    if not m:
        raise ValueError(f"Could not parse string index from StringName='{string_name}'")
    return int(m.group(1))

def _make_cell(rs: float, rsh: float) -> pvcell.PVcell:
    return pvcell.PVcell(Rs=rs, Rsh=rsh, **{k: HEALTHY_PARAMS[k] for k in ("Isc0_T0", "alpha_Isc", "Isat1_T0", "Isat2_T0")})

def _make_module_from_cell(cell: pvcell.PVcell) -> pvmodule.PVmodule:
    # 72-cell module layout
    return pvmodule.PVmodule(cell_pos=pvmodule.STD72, pvcells=[cell] * 72)

def _get_module_prototypes() -> Dict[str, pvmodule.PVmodule]:
    """
    Build one prototype PVmodule for each level (H, L1, L2, L3).
    We will clone (construct new instances) when composing strings to avoid
    state sharing between modules.
    """
    # Healthy module
    healthy_cell = _make_cell(HEALTHY_PARAMS["Rs"], HEALTHY_PARAMS["Rsh"])
    mod_H = _make_module_from_cell(healthy_cell)

    # Degraded modules by level
    prototypes = {"H": mod_H}
    for lvl, (rs_mult, rsh_div) in DEG_LEVELS.items():
        cell = _make_cell(HEALTHY_PARAMS["Rs"] * rs_mult, HEALTHY_PARAMS["Rsh"] / rsh_div)
        prototypes[f"L{lvl}"] = _make_module_from_cell(cell)
    return prototypes

def _instantiate_modules(proto: pvmodule.PVmodule, count: int) -> List[pvmodule.PVmodule]:
    """
    Create 'count' fresh PVmodule instances with the same cell parameters as 'proto'.
    """
    # Extract the first cell to replicate parameters
    c = proto.pvcells[0]
    cell_copy = pvcell.PVcell(Rs=float(c.Rs), Rsh=float(c.Rsh),
                              Isc0_T0=float(c.Isc0_T0), alpha_Isc=float(c.alpha_Isc),
                              Isat1_T0=float(c.Isat1_T0), Isat2_T0=float(c.Isat2_T0))
    return [_make_module_from_cell(cell_copy) for _ in range(count)]

def _compose_string_modules(counts: Dict[str, int], protos: Dict[str, pvmodule.PVmodule]) -> List[pvmodule.PVmodule]:
    """
    Compose a list of 30 PVmodule instances for one string using counts:
    counts = {"H": L0_healthy, "L1": L1, "L2": L2, "L3": L3}
    """
    modules: List[pvmodule.PVmodule] = []
    for key in ("H", "L1", "L2", "L3"):
        if counts.get(key, 0) > 0 and key in protos:
            modules.extend(_instantiate_modules(protos[key], counts[key]))
    # Ensure total = 30; if fewer, pad with healthy; if more, trim (safety)
    if len(modules) < num_modules_per_str:
        short = num_modules_per_str - len(modules)
        modules.extend(_instantiate_modules(protos["H"], short))
    elif len(modules) > num_modules_per_str:
        modules = modules[:num_modules_per_str]
    return modules

def _blank_inverter_dataframe(path: str, sheet: str, inv_code: str) -> pd.DataFrame:
    file = pd.read_excel(
        path,
        sheet_name=sheet,
        usecols="A:G",
        skiprows=1,
        engine="openpyxl",
    )
    # keep only the selected inverter
    df = file.loc[file["Inverter"].astype(str) == inv_code].copy()
    return df

def _build_inverter_strings(df: pd.DataFrame, protos: Dict[str, pvmodule.PVmodule]) -> Tuple[List[pvstring.PVstring], Dict[int, Dict[str, int]]]:
    """
    Build 28 PVstrings for an inverter, mapping any missing string to healthy.
    Returns:
      - list of PVstring objects
      - metadata dict per string index with counts used
    """
    # Initialize all 28 strings as healthy
    base_counts = {"H": num_modules_per_str, "L1": 0, "L2": 0, "L3": 0}
    per_str_counts: Dict[int, Dict[str, int]] = {i: dict(base_counts) for i in range(1, 28 + 1)}

    # Apply degradation where mentioned
    for _, row in df.iterrows():
        try:
            sidx = _parse_str_index(row["StringName"])
        except ValueError:
            continue
        if 1 <= sidx <= 28:
            # enforce that counts sum to TotalMods if provided; otherwise trust columns
            healthy = int(row.get("L0_healthy", 0))
            c_l1 = int(row.get("L1", 0))
            c_l2 = int(row.get("L2", 0))
            c_l3 = int(row.get("L3", 0))
            total = int(row.get("TotalMods", num_modules_per_str))
            # Safety adjustments
            healthy = min(healthy, total)
            c_l1 = min(c_l1, total - healthy)
            c_l2 = min(c_l2, total - healthy - c_l1)
            c_l3 = min(c_l3, total - healthy - c_l1 - c_l2)

            per_str_counts[sidx] = {"H": healthy, "L1": c_l1, "L2": c_l2, "L3": c_l3}

    pvstrings: List[pvstring.PVstring] = []
    for sidx in range(1, 28 + 1):
        counts = per_str_counts[sidx]
        mods = _compose_string_modules(counts, protos)
        pvstrings.append(pvstring.PVstring(pvmods=mods))
    return pvstrings, per_str_counts

def create_system_from_excel(path="string_summary_edited.xlsx", sheet="Sheet2", inverter=1) -> Tuple[pvsystem.PVsystem, Dict[int, Dict[str, int]]]:
    """Creates a PVsystem for a single inverter (28 strings) from the Excel file.

    Returns:
      (system, metadata) where metadata per string index has counts for {"H","L1","L2","L3"}.
    """
    inv = _inv_code(inverter)
    df = _blank_inverter_dataframe(path, sheet, inv)
    protos = _get_module_prototypes()
    pvstrings, per_str_counts = _build_inverter_strings(df, protos)
    system = pvsystem.PVsystem(pvstrs=pvstrings)
    return system, per_str_counts

# ... existing code ...

def create_all_inverters(path="string_summary_edited.xlsx", sheet="Sheet2") -> Dict[int, pvsystem.PVsystem]:
    """Build PVsystem for all inverters present (1..43). Missing entries default to healthy."""
    systems: Dict[int, pvsystem.PVsystem] = {}
    protos = _get_module_prototypes()
    # Read once to avoid repeated IO
    file = pd.read_excel(path, sheet_name=sheet, usecols="A:G", skiprows=1, engine="openpyxl")
    for inv_num in range(1, num_inverters + 1):
        inv = _inv_code(inv_num)
        df = file.loc[file["Inverter"].astype(str) == inv].copy()
        pvstrings, _ = _build_inverter_strings(df, protos)
        systems[inv_num] = pvsystem.PVsystem(pvstrs=pvstrings)
    return systems

def create_combined_system(inverters: List[int], path="string_summary_edited.xlsx", sheet="Sheet2") -> pvsystem.PVsystem:
    """Create a single PVsystem by concatenating strings from the selected inverters."""
    file = pd.read_excel(path, sheet_name=sheet, usecols="A:G", skiprows=1, engine="openpyxl")
    protos = _get_module_prototypes()
    all_strings: List[pvstring.PVstring] = []
    for inv_num in inverters:
        inv = _inv_code(inv_num)
        df = file.loc[file["Inverter"].astype(str) == inv].copy()
        pvstrings, _ = _build_inverter_strings(df, protos)
        all_strings.extend(pvstrings)
    return pvsystem.PVsystem(pvstrs=all_strings)

def plot_system_iv_pv(sys: pvsystem.PVsystem, title: str = "System"):
    """Quick IV/PV plot for a PVsystem."""
    Isys, Vsys, Psys = sys.Isys, sys.Vsys, sys.Psys
    fig, (ax_iv, ax_pv) = plt.subplots(1, 2, figsize=(10, 5))
    # IV
    ax_iv.plot(Vsys, Isys, label=title, color="tab:blue")
    ax_iv.set_title(f"I–V: {title}")
    ax_iv.set_xlabel("Voltage [V]")
    ax_iv.set_ylabel("Current [A]")
    ax_iv.grid(True, linestyle="--", alpha=0.4)
    ax_iv.legend()
    # PV
    ax_pv.plot(Vsys, Psys, label=title, color="tab:red")
    ax_pv.set_title(f"P–V: {title}")
    ax_pv.set_xlabel("Voltage [V]")
    ax_pv.set_ylabel("Power [W]")
    ax_pv.grid(True, linestyle="--", alpha=0.4)
    ax_pv.legend()
    plt.tight_layout()
    plt.show()

def plot_inverters(inverters: List[int], path="string_summary_edited.xlsx", sheet="Sheet2"):
    """Plot IV/PV for given inverter indices, each on its own figure."""
    for inv in inverters:
        sys, _ = create_system_from_excel(path=path, sheet=sheet, inverter=inv)
        plot_system_iv_pv(sys, title=f"Inverter {inv}")

def create_healthy_inverter(inverter: int = 1) -> pvsystem.PVsystem:
    """
    Create a fully-healthy PVsystem for a single inverter (28 strings x 30 modules).
    Matches the electrical parameters used elsewhere in this module.
    """
    protos = _get_module_prototypes()
    # Build one healthy string
    mods_healthy = _instantiate_modules(protos["H"], num_modules_per_str)
    str_healthy = pvstring.PVstring(pvmods=mods_healthy)
    # Replicate to 28 strings
    pvstrings = []
    for _ in range(28):
        # fresh instances for each string to avoid shared state
        mods = _instantiate_modules(protos["H"], num_modules_per_str)
        pvstrings.append(pvstring.PVstring(pvmods=mods))
    return pvsystem.PVsystem(pvstrs=pvstrings)

def create_healthy_combined(inverters: List[int]) -> pvsystem.PVsystem:
    """
    Create one fully-healthy PVsystem by concatenating healthy strings
    for the selected inverter indices.
    """
    protos = _get_module_prototypes()
    all_strings: List[pvstring.PVstring] = []
    for _ in inverters:
        # 28 healthy strings per inverter
        for _s in range(28):
            mods = _instantiate_modules(protos["H"], num_modules_per_str)
            all_strings.append(pvstring.PVstring(pvmods=mods))
    return pvsystem.PVsystem(pvstrs=all_strings)


# Single Inverter System and Plot
inv = 1
sys_i01, meta = create_system_from_excel(path="string_summary_edited.xlsx", sheet="Sheet2", inverter=inv)
healthy_sys = create_healthy_inverter(inverter=inv)
print("String 6 counts:", meta[6])  # example
plot_system_iv_pv(sys_i01, title="Inverter 1")

report = loss_calculator(sys_i01, healthy_sys, num_strs_affected=28)
print(f"\n=== Mismatch Report for Inverter {inv} ===")
for k, v in report.items():
    print(f"{k}: {v}")

# # Multiple Inverter System and Plot
# inverters = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
# sys_all = create_combined_system(inverters)
# plot_system_iv_pv(sys_all, title="All Inverters")

# # Create all inverters
# system = create_all_inverters(path="string_summary_edited.xlsx", sheet="Sheet2")
# # system[1], system[2], ...

