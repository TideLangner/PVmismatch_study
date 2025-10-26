# Tide Langner
# 25 August 2025
# Define mismatch models to be used in simulation.py

from pvmismatch import pvsystem
from pvmismatch import pvstring

# This function may not be necessary, as one can just use pvsystem.setSuns() directly
def shade_modules(system, shading_dict):
    """Apply shading to modules or cells.
    shading_dict example: {string_index: {module_index: irradiance or cell tuples}}
    """
    system.setSuns(shading_dict)
    return system

def remove_modules(system, n_missing=1, strings_with_missing=1, show_map=False):
    """Simulate module removal by removing n_missing modules from the end of each affected string
    in strings_with_missing strings starting from the beginning."""
    pvstrs_rmvd = []
    num_modules = len(system.pvstrs[0].pvmods)

    # System map: 1 = module present, 0 = removed
    layout_map = []

    for i, s in enumerate(system.pvstrs):
        if i < strings_with_missing:
            # clamp to at least 1 module left
            modules_present = max(1, num_modules - n_missing)

            # build a row map: 1 for present modules, 0 for removed
            row_map = [1] * modules_present + [0] * (num_modules - modules_present)
            layout_map.append(row_map)

            pvstrs_rmvd.append(
                pvstring.PVstring(pvmods=s.pvmods[:modules_present])
            )
        else:
            row_map = [1] * num_modules
            layout_map.append(row_map)
            pvstrs_rmvd.append(s)

    pvsys_rmvd = pvsystem.PVsystem(pvstrs=pvstrs_rmvd)
    pvsys_rmvd.setTemps(25.0 + 273.15)

    if show_map:
        print("Array layout (rows=strings, 1=present, 0=removed):")
        for row in layout_map:
            print(row)

    return pvsys_rmvd, layout_map

