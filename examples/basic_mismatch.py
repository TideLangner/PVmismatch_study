import numpy as np
from pvmismatch.pvmismatch_lib import pvcell, pvmodule, pvstring, pvsystem
import matplotlib.pyplot as plt

### Healthy System
my_cell = pvcell.PVcell(Rs=0.00641575, Rsh=285.79,
                       Isc0_T0=8.69, alpha_Isc=0.00060, Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5)
Icell, Vcell, Pcell = my_cell.Icell, my_cell.Vcell, my_cell.Pcell

my_module = pvmodule.PVmodule(cell_pos=pvmodule.STD72, pvcells=[my_cell]*72)
Imod, Vmod, Pmod = my_module.Imod, my_module.Vmod, my_module.Pmod

my_string = pvstring.PVstring(pvmods=my_module, numberMods=2)
Istr, Vstr, Pstr = my_string.Istring, my_string.Vstring, my_string.Pstring

my_system = pvsystem.PVsystem(pvmods=[my_module]*4, pvstrs=my_string, numberStrs=2)
Isys, Vsys, Psys = my_system.Isys, my_system.Vsys, my_system.Psys

def plot_healthy():
    fig, (ax_iv, ax_pv) = plt.subplots(1, 2, figsize=(10, 6))

    # IV subplot
    # ax_iv.plot(Vcell, Icell, label="Cell",   color="tab:blue")
    ax_iv.plot(Vmod,  Imod,  label="Module", color="tab:red")
    ax_iv.plot(Vstr,  Istr,  label="String", color="tab:orange")
    ax_iv.plot(Vsys,  Isys,  label="System", color="tab:green")
    ax_iv.set_title("I–V Curves for Healthy Module, String and System\nIn a 2x2 System", wrap=True)
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
    ax_pv.set_title("P–V Curves for Healthy Module, String and System\nIn a 2x2 System", wrap=True)
    ax_pv.set_xlabel("Voltage [V]")
    ax_pv.set_xlim(0, 1.1*np.max(Vsys))
    ax_pv.set_ylabel("Power [W]")
    ax_pv.set_ylim(0, 1.1*np.max(Psys))
    ax_pv.grid(True, linestyle="--", alpha=0.4)
    ax_pv.legend()

    plt.tight_layout()
    plt.show()


### Fully Degraded System
# degrade cell, mod, sys by doubling Rs and halving Rsh
my_degraded_cell_1 = pvcell.PVcell(Rs=0.00641575*2, Rsh=285.79/2,
                       Isc0_T0=8.69, alpha_Isc=0.00060, Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5)
Icell_1, Vcell_1, Pcell_1 = my_degraded_cell_1.Icell, my_degraded_cell_1.Vcell, my_degraded_cell_1.Pcell

my_degraded_module_1 = pvmodule.PVmodule(cell_pos=pvmodule.STD72, pvcells=[my_degraded_cell_1]*72)
Imod_1, Vmod_1, Pmod_1 = my_degraded_module_1.Imod, my_degraded_module_1.Vmod, my_degraded_module_1.Pmod

my_degraded_string_1 = pvstring.PVstring(pvmods=my_degraded_module_1, numberMods=2)
Istr_1, Vstr_1, Pstr_1 = my_degraded_string_1.Istring, my_degraded_string_1.Vstring, my_degraded_string_1.Pstring

my_degraded_system_1 = pvsystem.PVsystem(pvmods=[my_degraded_module_1]*4, numberMods=2, numberStrs=2)
Isys_1, Vsys_1, Psys_1 = my_degraded_system_1.Isys, my_degraded_system_1.Vsys, my_degraded_system_1.Psys

def plot_degraded_1():
    fig, (ax_iv, ax_pv) = plt.subplots(1, 2, figsize=(10, 4))

    # IV subplot
    # ax_iv.plot(Vcell_1, Icell_1, label="Cell",   color="tab:blue")
    ax_iv.plot(Vmod_1,  Imod_1,  label="Module", color="tab:red")
    ax_iv.plot(Vstr_1,  Istr_1,  label="String", color="tab:orange")
    ax_iv.plot(Vsys_1,  Isys_1,  label="System", color="tab:green")
    ax_iv.set_title("I–V Curves for Degraded Module, String and System\nIn a 2x2 System", wrap=True)
    ax_iv.set_xlabel("Voltage [V]")
    ax_iv.set_xlim(0, 1.1*np.max(Vsys_1))
    ax_iv.set_ylabel("Current [A]")
    ax_iv.set_ylim(0, 1.1*np.max(Isys_1))
    ax_iv.grid(True, linestyle="--", alpha=0.4)
    ax_iv.legend()

    # PV subplot
    # ax_pv.plot(Vcell_1, Pcell_1, label="Cell",   color="tab:blue")
    ax_pv.plot(Vmod_1,  Pmod_1,  label="Module", color="tab:red")
    ax_pv.plot(Vstr_1,  Pstr_1,  label="String", color="tab:orange")
    ax_pv.plot(Vsys_1,  Psys_1,  label="System", color="tab:green")
    ax_pv.set_title("P–V Curves for Degraded Module, String and System\nIn a 2x2 System", wrap=True)
    ax_pv.set_xlabel("Voltage [V]")
    ax_pv.set_xlim(0, 1.1*np.max(Vsys_1))
    ax_pv.set_ylabel("Power [W]")
    ax_pv.set_ylim(0, 1.1*np.max(Psys_1))
    ax_pv.grid(True, linestyle="--", alpha=0.4)
    ax_pv.legend()

    plt.tight_layout()
    plt.show()


### Mismatch System (1 str healthy, 1 str degraded by 1 module)
mismatch_str_1 = pvstring.PVstring(pvmods=[my_module, my_degraded_module_1], numberMods=2)
Imis_str_1, Vmis_str_1, Pmis_str_1 = mismatch_str_1.Istring, mismatch_str_1.Vstring, mismatch_str_1.Pstring

mismatch_sys_1 = pvsystem.PVsystem(pvstrs=[my_string, mismatch_str_1], numberStrs=2)
Imis_sys_1, Vmis_sys_1, Pmis_sys_1 = mismatch_sys_1.Isys, mismatch_sys_1.Vsys, mismatch_sys_1.Psys

def mpp_from_curve(I, V, P):
    """Return (Pmp, Imp, Vmp) from sampled I-V-P arrays"""
    k = np.argmax(P)
    return float(P[k]), float(I[k]), float(V[k])

def sum_module_mpps(pvsys):
    total = 0.0
    for s in pvsys.pvstrs:
        for m in s.pvmods:
            Pmp, _, _ = mpp_from_curve(m.Imod, m.Vmod, m.Pmod)
            total += Pmp
    return total

def sum_string_mpps(pvsys):
    total = 0.0
    for s in pvsys.pvstrs:
        Pmp, _, _ = mpp_from_curve(s.Istring, s.Vstring, s.Pstring)
        total += Pmp
    return total

def system_mpp(pvsys):
    Pmp, _, _ = mpp_from_curve(pvsys.Isys, pvsys.Vsys, pvsys.Psys)
    return Pmp

def mismatch_components(pvsys):
    Pmods = sum_module_mpps(pvsys)
    Pstrs = sum_string_mpps(pvsys)
    Psys = system_mpp(pvsys)
    mods_to_strs_mismatch = Pmods - Pstrs
    strs_to_sys_mismatch = Pstrs - Psys
    return {
        "module_MPPs_sum": Pmods,
        "string_MPPs_sum": Pstrs,
        "system_MPP": Psys,
        "mismatch_modules_to_strings": mods_to_strs_mismatch,
        "mismatch_strings_to_system": strs_to_sys_mismatch,
        "mismatch_total": mods_to_strs_mismatch + strs_to_sys_mismatch,
    }

# Calculate for healthy and mismatch systems
report_healthy  = mismatch_components(my_system)
report_mismatch = mismatch_components(mismatch_sys_1)

# Print concise comparison
print("\n=== Mismatch Breakdown (Healthy) ===")
for k, v in report_healthy.items():
    print(f"{k}: {v:.2f} W")

print("\n=== Mismatch Breakdown (Mismatch System) ===")
for k, v in report_mismatch.items():
    print(f"{k}: {v:.2f} W")

print("\n=== Delta (Healthy - Mismatch) ===")
for k in report_mismatch:
    dh = report_healthy[k] - report_mismatch[k]
    print(f"{k}: {dh:.2f} W")

def plot_mismatch():
    fig, (ax_iv, ax_pv) = plt.subplots(1, 2, figsize=(10, 4))

    # IV subplot
    ax_iv.plot(Vmis_str_1, Imis_str_1, label="String", color="tab:red")
    ax_iv.plot(Vmis_sys_1, Imis_sys_1, label="System", color="tab:green")
    ax_iv.set_title("I–V Curves for Mismatch Scenario 1")
    ax_iv.set_xlabel("Voltage [V]")
    ax_iv.set_xlim(0, 1.1 * np.max(Vmis_sys_1))
    ax_iv.set_ylabel("Current [A]")
    ax_iv.set_ylim(0, 1.1 * np.max(Imis_sys_1))
    ax_iv.grid(True, linestyle="--", alpha=0.4)
    ax_iv.legend()

    # PV subplot
    ax_pv.plot(Vmis_str_1, Pmis_str_1, label="String", color="tab:red")
    ax_pv.plot(Vmis_sys_1, Pmis_sys_1, label="System", color="tab:green")
    ax_pv.set_title("P–V Curves for Mismatch Scenario 1")
    ax_pv.set_xlabel("Voltage [V]")
    ax_pv.set_xlim(0, 1.1 * np.max(Vmis_sys_1))
    ax_pv.set_ylabel("Power [W]")
    ax_pv.set_ylim(0, 1.1 * np.max(Pmis_sys_1))
    ax_pv.grid(True, linestyle="--", alpha=0.4)
    ax_pv.legend()

    plt.tight_layout()
    plt.show()


def plot_healthy_vs_mismatch(healthy_sys, mismatch_sys):
    """
    Plot healthy vs mismatched system IV and PV curves.
    - Marks MPPs with dots.
    - Shows dashed guide lines at each MPP.
    - Annotates total loss vs healthy and mismatch-only loss.
    - Draws an arrow showing delta-P between the two MPPs on the PV plot.
    """
    # Healthy curves and MPP
    Ih, Vh, Ph = healthy_sys.Isys, healthy_sys.Vsys, healthy_sys.Psys
    Pmp_h, Imp_h, Vmp_h = mpp_from_curve(Ih, Vh, Ph)

    # Mismatch curves and MPP
    Im, Vm, Pm = mismatch_sys.Isys, mismatch_sys.Vsys, mismatch_sys.Psys
    Pmp_m, Imp_m, Vmp_m = mpp_from_curve(Im, Vm, Pm)

    # Compute mismatch-only loss from the mismatched system
    mis = mismatch_components(mismatch_sys)
    mismatch_only_W = float(mis["mismatch_total"])

    # Total loss vs healthy (includes degradation + mismatch if present)
    total_loss_W = max(Pmp_h - Pmp_m, 0.0)
    degradation_only_W = max(total_loss_W - mismatch_only_W, 0.0)

    # Axes limits
    Vmax = 1.05 * max(np.nanmax(Vh), np.nanmax(Vm))
    Imax = 1.10 * max(np.nanmax(Ih), np.nanmax(Im))
    Pmax = 1.10 * max(np.nanmax(Ph), np.nanmax(Pm))

    fig, (ax_iv, ax_pv) = plt.subplots(1, 2, figsize=(11, 4.5))

    # --- IV subplot ---
    ax_iv.plot(Vh, Ih, label="Healthy (IV)", color="tab:blue", lw=1.8)
    ax_iv.plot(Vm, Im, label="Mismatch (IV)", color="tab:green", lw=1.8)

    # Mark MPPs on IV
    ax_iv.plot([Vmp_h], [Imp_h], 'o', color="tab:blue", ms=7)
    ax_iv.plot([Vmp_m], [Imp_m], 'o', color="tab:green", ms=7)

    # Vertical guides at Vmp
    ax_iv.axvline(Vmp_h, color="tab:blue", ls="--", lw=1, alpha=0.7)
    ax_iv.axvline(Vmp_m, color="tab:green", ls="--", lw=1, alpha=0.7)

    ax_iv.set_title("I–V: Healthy vs Mismatch")
    ax_iv.set_xlabel("Voltage [V]")
    ax_iv.set_xlim(0, Vmax)
    ax_iv.set_ylabel("Current [A]")
    ax_iv.set_ylim(0, Imax)
    ax_iv.grid(True, linestyle="--", alpha=0.4)
    ax_iv.legend(loc="best")

    # Text box with losses
    txt_iv = (
        f"Pmp Healthy = {Pmp_h:.1f} W\n"
        f"Pmp Mismatch = {Pmp_m:.1f} W\n"
        f"Total loss vs Healthy = {total_loss_W:.1f} W\n"
        f"  - Mismatch only = {mismatch_only_W:.1f} W\n"
        f"  - Degradation only = {degradation_only_W:.1f} W"
    )
    ax_iv.text(0.98, 0.02, txt_iv, transform=ax_iv.transAxes,
               ha="right", va="bottom", fontsize=9,
               bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="0.6", alpha=0.9))

    # --- PV subplot ---
    ax_pv.plot(Vh, Ph, label="Healthy (PV)", color="tab:blue", lw=1.8)
    ax_pv.plot(Vm, Pm, label="Mismatch (PV)", color="tab:green", lw=1.8)

    # Mark MPPs on PV
    ax_pv.plot([Vmp_h], [Pmp_h], 'o', color="tab:blue", ms=7)
    ax_pv.plot([Vmp_m], [Pmp_m], 'o', color="tab:green", ms=7)

    # Horizontal guides at Pmp
    ax_pv.axhline(Pmp_h, color="tab:blue", ls="--", lw=1, alpha=0.7)
    ax_pv.axhline(Pmp_m, color="tab:green", ls="--", lw=1, alpha=0.7)

    # Visual delta-P arrow between MPP powers
    x_arrow = 0.82 * Vmax
    ax_pv.annotate(
        "", xy=(x_arrow, Pmp_h), xytext=(x_arrow, Pmp_m),
        arrowprops=dict(arrowstyle="<->", color="crimson", lw=1.6)
    )
    ax_pv.text(x_arrow + 0.01 * Vmax, (Pmp_h + Pmp_m) / 2,
               f"ΔP total = {total_loss_W:.1f} W\n(mismatch={mismatch_only_W:.1f} W)",
               va="center", ha="left", color="crimson", fontsize=9)

    ax_pv.set_title("P–V: Healthy vs Mismatch (MPP highlighted)")
    ax_pv.set_xlabel("Voltage [V]")
    ax_pv.set_xlim(0, Vmax)
    ax_pv.set_ylabel("Power [W]")
    ax_pv.set_ylim(0, Pmax)
    ax_pv.grid(True, linestyle="--", alpha=0.4)
    ax_pv.legend(loc="best")

    plt.tight_layout()
    plt.show()

# Plot healthy vs mismatched system
plot_healthy()
# plot_degraded_1()
# plot_healthy_vs_mismatch(my_system, mismatch_sys_1)

