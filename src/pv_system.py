# Tide Langner
# 25 August 2025
# Creates PV system using pvmismatch

from pvmismatch import pvsystem, pvstring
from datasheets.module_specs import std_module, degraded_module

def create_system(num_strings=12, num_modules=12, module_type='std', Rsh=0.25):
    """Create a PV system with a given number of strings and modules per string."""
    if module_type == 'std':
        mod = std_module()
    elif module_type == 'degraded':
        mod = degraded_module(Rsh=Rsh)
    pvstrs = [pvstring.PVstring(pvmods=[mod]*num_modules) for _ in range(num_strings)]
    sys = pvsystem.PVsystem(pvstrs=pvstrs)
    sys.setTemps(25.0 + 273.15)  # default temperature
    return sys
