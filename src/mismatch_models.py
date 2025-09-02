# Tide Langner
# 25 August 2025
# Define mismatch models to be used in simulation.py

from pvmismatch import pvsystem
from pvmismatch import pvstring

def shade_modules(system, shading_dict):
    """Apply shading to modules or cells.
    shading_dict example: {string_index: {module_index: irradiance or cell tuples}}
    """
    system.setSuns(shading_dict)
    return system

def remove_modules(system, n_missing=1, strings_with_missing=1):
    """Simulate module removal."""
    pvstrs_degraded = []
    num_modules = len(system.pvstrs[0].pvmods)
    for i, s in enumerate(system.pvstrs):
        if i < strings_with_missing:
            pvstrs_degraded.append(
                pvstring.PVstring(pvmods=s.pvmods[:num_modules-n_missing])
            )
        else:
            pvstrs_degraded.append(s)
    pvsys_degraded = pvsystem.PVsystem(pvstrs=pvstrs_degraded)
    pvsys_degraded.setTemps(50.0 + 273.15)
    return pvsys_degraded

# TODO: add degradation model
# TODO: add irradiance model
# TODO: add temperature model
# TODO: add combination model
