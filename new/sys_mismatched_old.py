# Mismatch System Builder

import numpy as np
from pvmismatch.pvmismatch_lib import pvstring, pvsystem
from sys_healthy import create_healthy
from sys_degraded_fully import create_degraded

# choose how many degraded sets (1 set = 30 strings, so 5 sets total)
# choose min degraded modules (>=1)
# choose max degraded modules (<=30)

def system_mismatched(degraded_sets=1, min_degraded_modules=1, max_degraded_modules=30,
                      run_sets_strings="sets", clamp_after_max=False,
                      min_degraded_strings=0, max_degraded_strings=0):
    """
    Build a mismatched PV system consisting of 5 sets x 30 strings (total 150 strings),
    each string has 30 modules.

    Modes:
    - run_sets_strings == "sets":
      - Variability via: degraded_sets, min_degraded_modules, max_degraded_modules, clamp_after_max.
      - In each affected set, strings ramp degraded modules from min_degraded_modules to
        max_degraded_modules by +1 per string. Behaviour after reaching max is set by
        clamp_after_max:
          - clamp_after_max=True: remain at max_degraded_modules for remaining strings
          - clamp_after_max=False: remaining strings are healthy (0 degraded)
      - Non-affected sets are fully healthy.

    - run_sets_strings == "strings":
      - Variability via: min_degraded_modules, max_degraded_modules, min_degraded_strings, max_degraded_strings.
      - Degraded strings are identical (no ramp between strings).
      - Number of degraded strings N is picked from the provided bounds (use N = min_degraded_strings,
        assuming the sweep/loop is driven by the caller function; pass equal values for a single configuration).
      - Each degraded string has K degraded modules, where K is taken from min_degraded_modules (pass equal
        min=max for a fixed configuration). Remaining strings are healthy.

    """

    total_sets = 5
    strings_per_set = 30
    total_strings = total_sets * strings_per_set
    mods_per_string = 30

    if run_sets_strings == "sets":
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

    elif run_sets_strings == "strings":
        # Number of degraded strings (use min_degraded_strings; caller should loop externally)
        n_degraded = int(np.clip(min_degraded_strings, 0, total_strings))
        # Degraded modules per degraded string (use min_degraded_modules; caller should loop externally)
        k_degraded = int(np.clip(min_degraded_modules, 0, mods_per_string))

        # Build a string with k degraded modules
        def make_string(k_degraded_local):
            k = int(np.clip(k_degraded_local, 0, mods_per_string))
            mods = [module_degraded] * k + [module_healthy] * (mods_per_string - k)
            return pvstring.PVstring(pvmods=mods)

        pv_strings = []
        # First n_degraded strings are degraded identically; remaining are healthy
        for str_idx in range(total_strings):
            if str_idx < n_degraded:
                pv_strings.append(make_string(k_degraded))
            else:
                pv_strings.append(make_string(0))

        # Assemble the full system
        system = pvsystem.PVsystem(pvstrs=pv_strings)
        return system

    else:
        raise ValueError("run_sets_strings must be 'sets' or 'strings'")


def system_binary_matrix(pvsys: pvsystem.PVsystem) -> np.ndarray:
    """
    Return a 150x30 matrix of 0/1 where 0=healthy module, 1=degraded module
    """
    rows = []
    for s in pvsys.pvstrs:
        row = [1 if (m is module_degraded) else 0 for m in s.pvmods]
        rows.append(row)
    return np.array(rows, dtype=int)

def print_system(pvsys: pvsystem.PVsystem) -> None:
    """
    Print full system as lines of 30 characters per string.
    - '0' denotes healthy modules
    - '1' denotes degraded modules
    Groups output by the 5 sets (30 strings each).
    """
    mat = system_binary_matrix(pvsys)
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

