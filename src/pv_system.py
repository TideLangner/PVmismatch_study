# Tide Langner
# 25 August 2025
# Creates PV system using pvmismatch

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from pvmismatch import pvsystem, pvstring
from data.module_specs import std_module, degraded_module, Rsh_degraded_module, Rs_degraded_module

def create_system(num_strings=2, num_modules=30, module_type='std', Rsh=0.25):
    """Create a PV system with a given number of strings and modules per string."""
    if module_type == 'std':
        mod = std_module()
    elif module_type == 'degraded':
        mod = degraded_module(Rsh=Rsh)
    pvstrs = [pvstring.PVstring(pvmods=[mod]*num_modules) for _ in range(num_strings)]
    sys = pvsystem.PVsystem(pvstrs=pvstrs)
    sys.setTemps(25.0 + 273.15)  # default temperature
    return sys

def create_Rsh_degraded_system(num_strings=2, num_modules=30):
    """Create a PV system with a given number of strings and modules per string."""
    pvstrs = []
    for s in range(num_strings):
        mods = [Rsh_degraded_module(p) for p in range(num_modules)]
        pvstrs.append(pvstring.PVstring(pvmods=mods))
    sys = pvsystem.PVsystem(pvstrs=pvstrs)
    sys.setTemps(25.0 + 273.15)  # default temperature
    return sys

def create_Rs_degraded_system(num_strings=2, num_modules=30):
    """Create a PV system with a given number of strings and modules per string."""
    pvstrs = []
    for s in range(num_strings):
        mods = [Rs_degraded_module(p) for p in range(num_modules)]
        pvstrs.append(pvstring.PVstring(pvmods=mods))
    sys = pvsystem.PVsystem(pvstrs=pvstrs)
    sys.setTemps(25.0 + 273.15)  # default temperature
    return sys

def plot_pv_system(system, title='Rsh'):
    """
    Plot PV system modules as a 2D image (imshow style), where shading corresponds to module Pmp values.
    """
    num_strings = len(system.pvstrs)
    num_modules = len(system.pvstrs[0].pvmods)

    # Collect scalar Pmp values (max over IV curve)
    outputs = np.array([
        [np.max(mod.Pmod) for mod in string.pvmods]
        for string in system.pvstrs
    ])

    fig, ax = plt.subplots(figsize=(15, 4))

    im = ax.imshow(
        outputs,
        cmap='viridis',
        interpolation='none',
        norm=colors.Normalize(vmin=outputs.min(), vmax=outputs.max()),
        aspect='auto',
        origin='upper'   # makes string 0 at top
    )

    # Titles & labels
    if title == 'Rsh':
        ax.set_title("Degraded Rsh PV System Output Map")
    else:
        ax.set_title("Degraded Rs PV System Output Map")
    ax.set_xlabel("Module Index")
    ax.set_ylabel("String Index")

    # Fix axes to show discrete ticks
    ax.set_xticks(np.arange(num_modules))
    ax.set_yticks(np.arange(num_strings))
    ax.set_xticklabels([f"{m}" for m in range(num_modules)])
    ax.set_yticklabels([f"String {s}" for s in range(num_strings)])

    # Draw gridlines around cells
    ax.set_xticks(np.arange(-0.5, num_modules, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, num_strings, 1), minor=True)
    ax.grid(which="minor", color="black", linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    # Add colorbar
    fig.colorbar(im, ax=ax, label="Module Pmp (W)")

    plt.show()
    return fig, ax, im

