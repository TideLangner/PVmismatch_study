# Mismatch System Builder

import numpy as np
from pvmismatch.pvmismatch_lib import pvstring, pvsystem

# choose resolution (1, 5, 10, 30)
# choose min degraded modules (>=1)
# choose max degraded modules (<=30)

def create_mismatched(degraded_sets=1, min_degraded_modules=1, max_degraded_modules=30, clamp_after_max=False,
                      module_healthy=None, module_degraded=None):
    """
    Build a pyramid-like mismatched PV system:
    - 150 strings organised into 5 "sets" (30 strings each)
    - 30 modules per string

    Pattern:
    Degraded modules from min_degraded_modules to max_degraded_modules with an increment of 1 per string.

    clamp_after_max:
      - clamp_after_max=True: remain at max_degraded_modules for remaining strings in the set
      - clamp_after_max=False: remaining strings in the set are healthy (0 degraded)
      - Non-affected sets are fully healthy.
    """
    total_strings = 150
    mods_per_string = 30
    total_sets = total_strings // 30                # == 5
    strings_per_set = total_strings // total_sets   # == 30

    # Build degradation pattern (pyramid from min_degraded_modules to max_degraded_modules) across strings
    if clamp_after_max:
        # Lock remaining strings in affected sets to max_degraded_modules
        affected_pattern = []
        count = min_degraded_modules
        for i in range(strings_per_set):
            affected_pattern.append(min(count, max_degraded_modules))
            if count < max_degraded_modules:
                count += 1
    else:
        # Set remaining strings in affected sets from max_degraded_modules to 0 (fully healthy)
        affected_pattern = []
        count = min_degraded_modules
        reached_max = False
        for i in range(strings_per_set):
            if reached_max:
                affected_pattern.append(0)
            else:
                affected_pattern.append(min(count, max_degraded_modules))
                if count < max_degraded_modules:
                    count += 1
                else:
                    reached_max = True

    # Build a string with k degraded modules
    def make_string(k_degraded):
        k = int(np.clip(k_degraded, 0, mods_per_string))  # Ensure int k is in valid range [0, mods_per_string]
        mods = [module_degraded] * k + [module_healthy] * (mods_per_string - k)
        return pvstring.PVstring(pvmods=mods)

    pv_strings = []
    for set_idx in range(total_sets):
        is_affected = set_idx < degraded_sets  # True/False if this set is affected
        for str_idx in range(strings_per_set):
            if is_affected:
                k_deg = affected_pattern[str_idx]
            else:
                k_deg = 0  # non-affected sets remain healthy
            pv_strings.append(make_string(k_deg))

    # Assemble the full system
    system = pvsystem.PVsystem(pvstrs=pv_strings)
    return system

def create_mismatched_parametric(min_degraded_modules=None, num_degraded_strings=None,
                                 module_healthy=None, module_degraded=None):
    """
    Build a mismatched PV system by specifying:
      - min_degraded_modules: K degraded modules per affected string (0..30)
      - num_degraded_strings: N affected strings (0..150), taken from the start

    Remaining strings are healthy. This is a simple builder to support parametric loops.
    """

    total_strings = 150
    mods_per_string = 30

    # Clamp inputs
    k = int(np.clip(min_degraded_modules, 0, mods_per_string))
    n = int(np.clip(num_degraded_strings, 0, total_strings))

    # Make a string with k degraded modules
    def make_string(k_local):
        mods = [module_degraded] * k_local + [module_healthy] * (mods_per_string - k_local)
        return pvstring.PVstring(pvmods=mods)

    pv_strings = []
    for s_idx in range(total_strings):
        if s_idx < n:
            pv_strings.append(make_string(k))
        else:
            pv_strings.append(make_string(0))

    return pvsystem.PVsystem(pvstrs=pv_strings)

def system_binary_matrix(pvsys, module_degraded=None):
    """
    Return a 150x30 matrix of 0/1 where 0=healthy module, 1=degraded module
    """
    rows = []
    for s in pvsys.pvstrs:
        row = [1 if (m is module_degraded) else 0 for m in s.pvmods]
        rows.append(row)
    return np.array(rows, dtype=int)

def print_system(pvsys, module_degraded=None):
    """
    Print full system as lines of 30 characters per string.
    - '0' denotes healthy modules
    - '1' denotes degraded modules
    Groups output by the 5 sets (30 strings each).
    """
    mat = system_binary_matrix(pvsys, module_degraded)
    strings_per_set = 30
    total_sets = 5
    for set_idx in range(total_sets):
        start = set_idx * strings_per_set
        end = start + strings_per_set
        print(f"Set {set_idx} (strings {start}-{end-1})")
        for si in range(start, end):
            line = "".join(str(x) for x in mat[si])
            print(f"str {si:3d}: {line}")
        print()

