# Tide Langner
# 25 August 2025
# Define mismatch models to be used in simulation.py

import numpy as np
from copy import deepcopy
from pvmismatch.pvmismatch_lib.pvsystem import PVsystem

def _iteration_modules(pvsys: PVsystem):
    """
    Yields string_idx, module_idx and module_obj for each module in the system.
    Supports both nested and flat lists of modules.
    """
    mods = pvsys.pvmods
    if not mods:
        return
    if isinstance(mods[0], list):
        for string_idx, row in enumerate(mods):
            for module_idx, module in enumerate(row):
                yield string_idx, module_idx, module
    else:
        for module_idx, module in enumerate(mods):
            yield None, module_idx, module

def _iteration_selected_modules(pvsys: PVsystem, selection):
    """
    Yields module objects based on selection:
    - linst[int] - module indices across all strings
    - list[tuple[int, int]] - explicit (string_idx, module_idx) pairs
    - dict[int, linst[int]]: {string_idx: [module_idx, ...]}
    """
    if not selection:
        return
    mods = pvsys.pvmods
    if not mods:
        return
    nested = isinstance(mods[0], list)

    # helper to safely yield a module, if indices are valid
    def try_yield(string_idx, module_idx):
        if nested:
            if 0 <= string_idx < len(mods):
                row = mods[string_idx]
                if 0 <= module_idx < len(row):
                    yield row[module_idx]
        else:
            # flat layout ignores s_idx; m_idx indexes the flat list
            if 0 <= module_idx < len(mods):
                yield mods[module_idx]

    # Case A: list of ints => same module positions in every string (flat)
    if isinstance(selection, (list, tuple)) and selection and all(isinstance(x, int) for x in selection):
        if nested:
            for string_idx in range(len(mods)):
                for module_idx in selection:
                    yield from try_yield(string_idx, module_idx)
        else:
            for module_idx in selection:
                yield from try_yield(None, module_idx)
        return

    # Case B: list of (string_idx, module_idx) pairs
    if isinstance(selection, (list, tuple)) and selection and all(
            isinstance(x, (list, tuple)) and len(x) == 2 for x in selection
    ):
        for string_idx, module_idx in selection:
            if not isinstance(string_idx, int) or not isinstance(module_idx, int):
                continue
            yield from try_yield(string_idx, module_idx)
        return

        # Case C: dict string_idx -> [module_idx, ...]
    if isinstance(selection, dict):
        for string_idx, module_list in selection.items():
            if not isinstance(string_idx, int):
                continue
            if not isinstance(module_list, (list, tuple)):
                continue
            for module_idx in module_list:
                if not isinstance(module_idx, int):
                    continue
                yield from try_yield(string_idx, module_idx)
        return


# 1. Apply degradation to selected modules
def apply_degradation(system: PVsystem, degraded_modules=None, severity=0.1):
    """
    Degrade selected modules by adjusting each cell's Rs and Rsh:
    - Rs increased by severity fraction: Rs *= (1 + severity)
    - Rsh decreased by severity fraction: Rsh *= (1 - severity)
    """
    degraded_sys = deepcopy(system)
    if not degraded_modules:
        return degraded_sys

    rs_factor = 1.0 + float(severity)
    rsh_factor = max(0.0, 1.0 - float(severity))
    RS_MIN = 1e-6
    RSH_MIN = 1e-3

    # CHANGED: after modifying per-cell parameters, call mod.calcMod() before system calc
    modified_modules = set()
    for mod in _iteration_selected_modules(degraded_sys, degraded_modules):
        for cell in mod.pvcells:
            cell.Rs = max(cell.Rs * rs_factor, RS_MIN)
            cell.Rsh = max(cell.Rsh * rsh_factor, RSH_MIN)
        mod.calcMod()  # CHANGED: ensure module model is rebuilt
        modified_modules.add(id(mod))

    degraded_sys.calcSystem()
    return degraded_sys

# 2. Apply irradiance variation
def apply_irradiance(system: PVsystem, irradiance=1000.0):
    """
    Adjust irradiance level across the system.
    """
    sys = deepcopy(system)
    suns = float(irradiance) / 1000.0       # normalised to 1000 W/m^2
    # CHANGED: set Ee per cell AND recalc each module afterwards
    for _, _, mod in _iteration_modules(sys):
        for cell in mod.pvcells:
            cell.Ee = suns
        mod.calcMod()  # CHANGED: recalc module after Ee change
    sys.calcSystem()
    return sys

# 3. Apply temperature variation
def apply_temperature(system: PVsystem, temperature=25.0):
    """
    Adjust cell/module operating temperature.
    """
    sys = deepcopy(system)
    Tkelvin = float(temperature) + 273.15
    for _, _, mod in _iteration_modules(sys):
        for cell in mod.pvcells:
            cell.Tcell = Tkelvin   # PVMismatch uses Kelvin
        mod.calcMod()  # CHANGED: recalc module after temperature change
    sys.calcSystem()
    return sys

# 4. Combine scenarios
def apply_mismatch(system: PVsystem,
                   degraded_modules=None,
                   severity=0.1,
                   irradiance=1000.0,
                   temperature=25.0):
    """
    Apply combination of mismatch factors at once.
    Degradation affects per-cell Rs/Rsh (more physical for many faults).
    """
    sys = deepcopy(system)

    # 1) Set base irradiance per cell
    suns = float(irradiance) / 1000.0
    for _, _, mod in _iteration_modules(sys):
        for cell in mod.pvcells:
            cell.Ee = suns
        mod.calcMod()  # CHANGED

    # 2) Apply degradation via Rs/Rsh
    if degraded_modules and severity > 0.0:
        rs_factor = 1.0 + float(severity)
        rsh_factor = max(0.0, 1.0 - float(severity))
        RS_MIN = 1e-6
        RSH_MIN = 1e-3
        for mod in _iteration_selected_modules(sys, degraded_modules):
            for cell in mod.pvcells:
                cell.Rs = max(cell.Rs * rs_factor, RS_MIN)
                cell.Rsh = max(cell.Rsh * rsh_factor, RSH_MIN)
            mod.calcMod()  # CHANGED

    # 3) Temperature
    Tkelvin = float(temperature) + 273.15
    for _, _, mod in _iteration_modules(sys):
        for cell in mod.pvcells:
            cell.Tcell = Tkelvin
        mod.calcMod()  # CHANGED

    sys.calcSystem()
    return sys