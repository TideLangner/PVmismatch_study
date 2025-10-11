# Fully degraded system

import numpy as np
import matplotlib.pyplot as plt
from pvmismatch.pvmismatch_lib import pvcell, pvmodule, pvstring, pvsystem

# Healthy cell characteristics
"""
Rs=0.00641575, Rsh=285.79,
Isc0_T0=8.69, alpha_Isc=0.00060, 
Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5
"""

# ======== SET DEGRADATION MODE: ======== #
"""
# 1 = 90.0% healthy -> Rs*1.965 ; Rsh/1.965
# 2 = 80.0% healthy -> Rs*2.980 ; Rsh/2.980
# 3 = 70.0% healthy -> Rs*4.070 ; Rsh/4.070
# 4 = 60.0% healthy -> Rs*5.300 ; Rsh/5.300
# 5 = 50.0% healthy -> Rs*6.815 ; Rsh/6.815
# 6 = 40.0% healthy -> Rs*8.970 ; Rsh/8.970
"""
# ======================================= #
# degradation_mode = 1
# ======================================= #


def create_degraded(degradation_mode=1):
    """Create a degraded system based on cell degradation mode"""
    if degradation_mode == 1:
        cell_degraded = pvcell.PVcell(Rs=0.00641575*1.965, Rsh=285.79/1.965,
                                      Isc0_T0=8.69, alpha_Isc=0.00060, Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5)
        deg_label = "10% Degraded"
    elif degradation_mode == 2:
        cell_degraded = pvcell.PVcell(Rs=0.00641575*2.980, Rsh=285.79/2.980,
                                      Isc0_T0=8.69, alpha_Isc=0.00060, Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5)
        deg_label = "20% Degraded"
    elif degradation_mode == 3:
        cell_degraded = pvcell.PVcell(Rs=0.00641575*4.070, Rsh=285.79/4.070,
                                      Isc0_T0=8.69, alpha_Isc=0.00060, Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5)
        deg_label = "30% Degraded"
    elif degradation_mode == 4:
        cell_degraded = pvcell.PVcell(Rs=0.00641575*5.300, Rsh=285.79/5.300,
                                      Isc0_T0=8.69, alpha_Isc=0.00060, Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5)
        deg_label = "40% Degraded"
    elif degradation_mode == 5:
        cell_degraded = pvcell.PVcell(Rs=0.00641575*6.815, Rsh=285.79/6.815,
                                      Isc0_T0=8.69, alpha_Isc=0.00060, Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5)
        deg_label = "50% Degraded"
    else:
        cell_degraded = pvcell.PVcell(Rs=0.00641575*8.970, Rsh=285.79/8.970,
                                      Isc0_T0=8.69, alpha_Isc=0.00060, Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5)
        deg_label = "60% Degraded"

    Icell_deg, Vcell_deg, Pcell_deg = cell_degraded.Icell, cell_degraded.Vcell, cell_degraded.Pcell

    module_degraded = pvmodule.PVmodule(cell_pos=pvmodule.STD72, pvcells=[cell_degraded] * 72)
    Imod_deg, Vmod_deg, Pmod_deg = module_degraded.Imod, module_degraded.Vmod, module_degraded.Pmod

    string_degraded = pvstring.PVstring(pvmods=module_degraded, numberMods=30)
    Istr_deg, Vstr_deg, Pstr_deg = string_degraded.Istring, string_degraded.Vstring, string_degraded.Pstring

    system_degraded = pvsystem.PVsystem(pvstrs=string_degraded, numberStrs=150)
    Isys_deg, Vsys_deg, Psys_deg = system_degraded.Isys, system_degraded.Vsys, system_degraded.Psys

    degraded = {
        "cell_degraded": cell_degraded,
        "Icell_deg": Icell_deg, "Vcell_deg": Vcell_deg, "Pcell_deg": Pcell_deg,
        "module_degraded": module_degraded,
        "Imod_deg": Imod_deg, "Vmod_deg": Vmod_deg, "Pmod_deg": Pmod_deg,
        "string_degraded": string_degraded,
        "Istr_deg": Istr_deg, "Vstr_deg": Vstr_deg, "Pstr_deg": Pstr_deg,
        "system_degraded": system_degraded,
        "Isys_deg": Isys_deg, "Vsys_deg": Vsys_deg, "Psys_deg": Psys_deg,
        "deg_label": deg_label
    }

    return degraded


def plot_degraded(Icell_deg=None, Vcell_deg=None, Pcell_deg=None,
                  Imod_deg=None, Vmod_deg=None, Pmod_deg=None,
                  Istr_deg=None, Vstr_deg=None, Pstr_deg=None,
                  Isys_deg=None, Vsys_deg=None, Psys_deg=None, deg_label=None):
    """
        Plot IV and PV curves for a fully-degraded cell, module, string, system or combination.
        Edits of below necessary for changes:
        - ax_iv title, axis and limits
        - ax_pv title, axis and limits
        - arguments passed in run_baselines() sys_simulate.py
        """

    fig, (ax_iv, ax_pv) = plt.subplots(1, 2, figsize=(10, 6))

    # IV subplot
    # ax_iv.plot(Vcell_deg, Icell_deg, label="Cell",   color="tab:blue")
    ax_iv.plot(Vmod_deg, Imod_deg, label="Module", color="tab:green")
    ax_iv.plot(Vstr_deg, Istr_deg, label="String", color="tab:orange")
    ax_iv.plot(Vsys_deg, Isys_deg, label="System", color="tab:red")
    ax_iv.set_title(f"I–V Curves for {deg_label} Module, String and System")
    ax_iv.set_xlabel("Voltage [V]")
    ax_iv.set_xlim(0, 1.1 * np.max(Vsys_deg))
    ax_iv.set_ylabel("Current [A]")
    ax_iv.set_ylim(0, 1.1 * np.max(Isys_deg))
    ax_iv.grid(True, linestyle="--", alpha=0.4)
    ax_iv.legend()

    # PV subplot
    # ax_pv.plot(Vcell_1, Pcell_1, label="Cell",   color="tab:blue")
    ax_pv.plot(Vmod_deg, Pmod_deg, label="Module", color="tab:green")
    ax_pv.plot(Vstr_deg, Pstr_deg, label="String", color="tab:orange")
    ax_pv.plot(Vsys_deg, Psys_deg, label="System", color="tab:red")
    ax_pv.set_title(f"P–V Curves for {deg_label} Module, String and System")
    ax_pv.set_xlabel("Voltage [V]")
    ax_pv.set_xlim(0, 1.1 * np.max(Vsys_deg))
    ax_pv.set_ylabel("Power [W]")
    ax_pv.set_ylim(0, 1.1 * np.max(Psys_deg))
    ax_pv.grid(True, linestyle="--", alpha=0.4)
    ax_pv.legend()

    plt.tight_layout()
    plt.show()


def plot_deg_vs_healthy_mods(Imod=None, Vmod=None, Pmod=None,
                             Imod_deg=None, Vmod_deg=None, Pmod_deg=None, deg_label=None):
    """
    Plot details for healthy vs degraded modules.
    """

    fig, (ax_iv, ax_pv) = plt.subplots(1, 2, figsize=(10, 6))

    # IV subplot
    ax_iv.plot(Vmod, Imod, label="Healthy Module", color="tab:green")
    ax_iv.plot(Vmod_deg, Imod_deg, label="Degraded Module", color="tab:red")
    ax_iv.set_title(f"I–V Curves for Healthy vs {deg_label} Module")
    ax_iv.set_xlabel("Voltage [V]")
    ax_iv.set_xlim(0, 1.1 * np.max(Vmod))
    ax_iv.set_ylabel("Current [A]")
    ax_iv.set_ylim(0, 1.1 * np.max(Imod))
    ax_iv.grid(True, linestyle="--", alpha=0.4)
    ax_iv.legend()

    # PV subplot
    # ax_pv.plot(Vcell_1, Pcell_1, label="Cell",   color="tab:blue")
    ax_pv.plot(Vmod, Pmod, label="Healthy Module", color="tab:green")
    ax_pv.plot(Vmod_deg, Pmod_deg, label="Degraded Module", color="tab:red")
    ax_pv.set_title(f"P–V Curves for Healthy vs {deg_label} Module")
    ax_pv.set_xlabel("Voltage [V]")
    ax_pv.set_xlim(0, 1.1 * np.max(Vmod))
    ax_pv.set_ylabel("Power [W]")
    ax_pv.set_ylim(0, 1.1 * np.max(Pmod))
    ax_pv.grid(True, linestyle="--", alpha=0.4)
    ax_pv.legend()

    plt.tight_layout()
    plt.show()


def plot_degradation_modes(Imod=None, Vmod=None, Pmod=None, all_modes=None):
    """
    Plot module outputs for all degradation modes.
    """

    fig, (ax_iv, ax_pv) = plt.subplots(1, 2, figsize=(10, 6))

    # Shades of red for plots
    c = ["#500000", "#700000", "#900000", "#bb0000", "#dd0000", "#ff0000"]

    # Plot healthy
    ax_iv.plot(Vmod, Imod, label="Healthy Module", color="tab:green")
    ax_pv.plot(Vmod, Pmod, label="Healthy Module", color="tab:green")

    # Unpack degraded plots
    for i, s in enumerate(all_modes):
        ax_iv.plot(s["Vmod_deg"], s["Imod_deg"], label=s["deg_label"], color=c[i])
        ax_pv.plot(s["Vmod_deg"], s["Pmod_deg"], label=s["deg_label"], color=c[i])

    # IV subplot
    ax_iv.set_title("I–V Curves for All Degraded Modules")
    ax_iv.set_xlabel("Voltage [V]")
    ax_iv.set_xlim(0, 1.1 * np.max(Vmod))
    ax_iv.set_ylabel("Current [A]")
    ax_iv.set_ylim(0, 1.1 * np.max(Imod))
    ax_iv.grid(True, linestyle="--", alpha=0.4)
    ax_iv.legend()

    # PV subplot
    ax_pv.set_title(f"P–V Curves for All Degraded Modules")
    ax_pv.set_xlabel("Voltage [V]")
    ax_pv.set_xlim(0, 1.1 * np.max(Vmod))
    ax_pv.set_ylabel("Power [W]")
    ax_pv.set_ylim(0, 1.1 * np.max(Pmod))
    ax_pv.grid(True, linestyle="--", alpha=0.4)
    ax_pv.legend()

    plt.tight_layout()
    plt.show()

