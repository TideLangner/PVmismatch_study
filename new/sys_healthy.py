# Healthy system

import numpy as np
import matplotlib.pyplot as plt
from pvmismatch.pvmismatch_lib import pvcell, pvmodule, pvstring, pvsystem

# Healthy cell characteristics
"""
Rs=0.00641575, Rsh=285.79
Isc0_T0=8.69, alpha_Isc=0.00060
Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5
"""

def create_healthy():
    cell_healthy = pvcell.PVcell(Rs=0.00641575, Rsh=285.79,
                                 Isc0_T0=8.69, alpha_Isc=0.00060, Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5)
    Icell, Vcell, Pcell = cell_healthy.Icell, cell_healthy.Vcell, cell_healthy.Pcell

    module_healthy = pvmodule.PVmodule(cell_pos=pvmodule.STD72, pvcells=[cell_healthy] * 72)
    Imod, Vmod, Pmod = module_healthy.Imod, module_healthy.Vmod, module_healthy.Pmod

    string_healthy = pvstring.PVstring(pvmods=module_healthy, numberMods=30)
    Istr, Vstr, Pstr = string_healthy.Istring, string_healthy.Vstring, string_healthy.Pstring

    system_healthy = pvsystem.PVsystem(pvstrs=string_healthy, numberStrs=150)
    Isys, Vsys, Psys = system_healthy.Isys, system_healthy.Vsys, system_healthy.Psys

    healthy = {
        "cell_healthy": cell_healthy,
        "Icell": Icell, "Vcell": Vcell, "Pcell": Pcell,
        "module_healthy": module_healthy,
        "Imod": Imod, "Vmod": Vmod, "Pmod": Pmod,
        "string_healthy": string_healthy,
        "Istr": Istr, "Vstr": Vstr, "Pstr": Pstr,
        "system_healthy": system_healthy,
        "Isys": Isys, "Vsys": Vsys, "Psys": Psys,
    }

    return healthy

def plot_healthy(Imod, Vmod, Pmod, Istr, Vstr, Pstr, Isys, Vsys, Psys):
    fig, (ax_iv, ax_pv) = plt.subplots(1, 2, figsize=(10, 6))

    # IV subplot
    # ax_iv.plot(Vcell, Icell, label="Cell",   color="tab:blue")
    ax_iv.plot(Vmod,  Imod,  label="Module", color="tab:red")
    ax_iv.plot(Vstr,  Istr,  label="String", color="tab:orange")
    ax_iv.plot(Vsys,  Isys,  label="System", color="tab:green")
    ax_iv.set_title("I–V Curves for Healthy Module, String and System")
    ax_iv.set_xlabel("Voltage [V]")
    ax_iv.set_xlim(0, 1.1*np.max(Vsys))
    ax_iv.set_ylabel("Current [A]")
    ax_iv.set_ylim(0, 1.1*np.max(Isys))
    ax_iv.grid(True, linestyle="--", alpha=0.4)
    ax_iv.legend()

    # PV subplot
    # ax_pv.plot(Vcell, Pcell, label="Cell",   color="tab:blue")
    ax_pv.plot(Vmod,  Pmod,  label="Module", color="tab:red")
    ax_pv.plot(Vstr,  Pstr,  label="String", color="tab:orange")
    ax_pv.plot(Vsys,  Psys,  label="System", color="tab:green")
    ax_pv.set_title("P–V Curves for Healthy Module, String and System")
    ax_pv.set_xlabel("Voltage [V]")
    ax_pv.set_xlim(0, 1.1*np.max(Vsys))
    ax_pv.set_ylabel("Power [W]")
    ax_pv.set_ylim(0, 1.1*np.max(Psys))
    ax_pv.grid(True, linestyle="--", alpha=0.4)
    ax_pv.legend()

    plt.tight_layout()
    plt.show()

