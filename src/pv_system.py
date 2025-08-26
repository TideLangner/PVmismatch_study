# Tide Langner
# 25 August 2025
# Creates PV system using pvmismatch

from pvmismatch import pvsystem, pvstring
from datasheets.module_specs import std_module, degraded_module

def create_system(num_strings=12, num_modules=12, module_type='std'):
    """Create a PVsystem with given number of strings and modules per string."""
    if module_type == 'std':
        mod = std_module()
    elif module_type == 'degraded':
        mod = degraded_module()
    pvstrs = [pvstring.PVstring(pvmods=[mod]*num_modules) for _ in range(num_strings)]
    sys = pvsystem.PVsystem(pvstrs=pvstrs)
    sys.setTemps(50.0 + 273.15)  # default temperature
    return sys


"""
from datasheets.module_specs import Jinko_module
from pvmismatch.pvmismatch_lib.pvsystem import PVsystem

def create_pv_system(n_strings=2, m_modules=10):
    module = Jinko_module
    system = PVsystem(numberStrs=n_strings, numberMods=m_modules, pvmods=module)
    return system
"""