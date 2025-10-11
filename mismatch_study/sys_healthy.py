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

def plot_healthy(Icell=None, Vcell=None, Pcell=None,
                 Imod=None, Vmod=None, Pmod=None,
                 Istr=None, Vstr=None, Pstr=None,
                 Isys=None, Vsys=None, Psys=None):
    """
    Plot IV and PV curves for a healthy cell, module, string, system or combination.
    Edits of below necessary for changes:
    - ax_iv title, axis and limits
    - ax_pv title, axis and limits
    - arguments passed in run_baselines() sys_simulate.py
    """

    # Helper to compute key points: Isc, Voc, MPP(Vmp, Imp, Pmp)
    def key_points(V, I, P):
        # Short-circuit current Isc at V≈0
        idx_v0 = int(np.argmin(np.abs(V)))
        Isc = I[idx_v0]
        V_at_Isc = V[idx_v0]

        # Open-circuit voltage Voc at I≈0
        idx_i0 = int(np.argmin(np.abs(I)))
        Voc = V[idx_i0]
        I_at_Voc = I[idx_i0]

        # Maximum power point
        idx_mpp = int(np.argmax(P))
        Vmp = V[idx_mpp]
        Imp = I[idx_mpp]
        Pmp = P[idx_mpp]

        return {
            "Isc": Isc, "V_at_Isc": V_at_Isc,
            "Voc": Voc, "I_at_Voc": I_at_Voc,
            "Vmp": Vmp, "Imp": Imp, "Pmp": Pmp,
            "idx_mpp": idx_mpp
        }

    fig, (ax_iv, ax_pv) = plt.subplots(1, 2, figsize=(10, 6))

    # Prepare available datasets
    curves = []
    if Vcell is not None and Icell is not None and Pcell is not None:
        curves.append(("Cell", Vcell, Icell, Pcell, "tab:blue"))
    if Vmod is not None and Imod is not None and Pmod is not None:
        curves.append(("Module", Vmod, Imod, Pmod, "tab:red"))
    if Vstr is not None and Istr is not None and Pstr is not None:
        curves.append(("String", Vstr, Istr, Pstr, "tab:orange"))
    if Vsys is not None and Isys is not None and Psys is not None:
        curves.append(("System", Vsys, Isys, Psys, "tab:green"))

    # Compute global axis limits from available data
    all_V = np.concatenate([c[1] for c in curves]) if curves else np.array([0.0, 1.0])
    all_I = np.concatenate([c[2] for c in curves]) if curves else np.array([0.0, 1.0])
    all_I = all_I[np.abs(all_I) < 1e1]  # filter outliers for cell level
    all_P = np.concatenate([c[3] for c in curves]) if curves else np.array([0.0, 1.0])

    # IV subplot
    # ax_iv.plot(Vcell, Icell, label="Cell",   colour="tab:blue")
    for label, V, I, P, colour in curves:
        ax_iv.plot(V, I, label=label, color=colour)
        pts = key_points(V, I, P)
        # Highlight Isc (at V≈0)
        ax_iv.scatter(pts["V_at_Isc"], pts["Isc"], color=colour, marker="s", zorder=5)
        ax_iv.annotate(f"{label} Isc", (pts["V_at_Isc"], pts["Isc"]),
                       textcoords="offset points", xytext=(6, 6), fontsize=8, color=colour)
        # Highlight Voc (at I≈0)
        ax_iv.scatter(pts["Voc"], pts["I_at_Voc"], color=colour, marker="o", zorder=5)
        ax_iv.annotate(f"{label} Voc", (pts["Voc"], pts["I_at_Voc"]),
                       textcoords="offset points", xytext=(6, -12), fontsize=8, color=colour)
        # Highlight MPP on IV curve
        ax_iv.scatter(pts["Vmp"], pts["Imp"], color=colour, marker="D", zorder=6)
        ax_iv.annotate(f"{label} MPP", (pts["Vmp"], pts["Imp"]),
                       textcoords="offset points", xytext=(6, 6), fontsize=8, color=colour)
        # Guidelines for MPP: Vmp (vertical) and Imp (horizontal)
        ax_iv.axvline(pts["Vmp"], color=colour, linestyle=":", alpha=0.6)
        ax_iv.axhline(pts["Imp"], color=colour, linestyle=":", alpha=0.6)
    ax_iv.set_title("I–V Curves for Healthy Module, String and System")
    ax_iv.set_xlabel("Voltage [V]")
    ax_iv.set_xlim(0, 1.1 * np.max(all_V))
    ax_iv.set_ylabel("Current [A]")
    ax_iv.set_ylim(0, 1.1 * np.sort(all_I)[-2]) # filter initial current outlier for cell level
    ax_iv.grid(True, linestyle="--", alpha=0.4)
    ax_iv.legend()

    # PV subplot
    # ax_pv.plot(Vcell, Pcell, label="Cell",   colour="tab:blue")
    for label, V, I, P, colour in curves:
        ax_pv.plot(V, P, label=label, color=colour)
        pts = key_points(V, I, P)
        # Highlight MPP on PV curve
        ax_pv.scatter(pts["Vmp"], pts["Pmp"], color=colour, marker="D", zorder=6)
        ax_pv.annotate(f"{label} MPP", (pts["Vmp"], pts["Pmp"]),
                       textcoords="offset points", xytext=(6, 6), fontsize=8, color=colour)
        # Guidelines for MPP on PV: Vmp (vertical) and Pmp (horizontal)
        ax_pv.axvline(pts["Vmp"], color=colour, linestyle=":", alpha=0.6)
        ax_pv.axhline(pts["Pmp"], color=colour, linestyle=":", alpha=0.6)
    ax_pv.set_title("P–V Curves for Healthy Module, Cell and System")
    ax_pv.set_xlabel("Voltage [V]")
    ax_pv.set_xlim(0, 1.1 * np.max(all_V))
    ax_pv.set_ylabel("Power [W]")
    ax_pv.set_ylim(0, 1.1 * np.max(all_P))
    ax_pv.grid(True, linestyle="--", alpha=0.4)
    ax_pv.legend()

    plt.tight_layout()
    plt.show()

