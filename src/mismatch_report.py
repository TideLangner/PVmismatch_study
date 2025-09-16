# Tide Langner
# 25 August 2025
# Mismatch Loss Calculator
from functools import total_ordering

import numpy as np
import matplotlib.pyplot as plt

def mpp_from_curve(I, V, P):
    k = np.argmax(P)
    return P[k].squeeze().item(), I[k].squeeze().item(), V[k].squeeze().item()

def mismatch_report(pvsys, pvsys_healthy=None):
    """
    Reports degradation-only vs mismatch-only loss_report at the module, string, and system levels.
    """

    # --- actual system degraded MPP (with mismatch) ---
    Pmp_sys, _, _ = mpp_from_curve(pvsys.Isys, pvsys.Vsys, pvsys.Psys)

    # --- per-string degraded (with mismatch inside strings) ---
    Pmp_str = []
    for pvstr in pvsys.pvstrs:
        Pmp_s, _, _ = mpp_from_curve(pvstr.Istring, pvstr.Vstring, pvstr.Pstring)
        Pmp_str.append(Pmp_s)
    Pmp_str_sum = float(np.sum(Pmp_str))

    # --- per-module degraded (isolated, no mismatch inside strings) ---
    Pmp_mod = []
    for pvstr in pvsys.pvstrs:
        for mod in pvstr.pvmods:
            Pmp_m, _, _ = mpp_from_curve(mod.Imod, mod.Vmod, mod.Pmod)
            Pmp_mod.append(Pmp_m)
    Pmp_mod_sum = float(np.sum(Pmp_mod))

    # --- healthy baseline (if provided) ---
    Pmp_mod_healthy_sum = None
    Pmp_str_healthy_sum = None
    Pmp_sys_healthy = None
    if pvsys_healthy is not None:
        # Healthy modules
        Pmp_mod_healthy = []
        for pvstr in pvsys_healthy.pvstrs:
            for mod in pvstr.pvmods:
                Pmp_m, _, _ = mpp_from_curve(mod.Imod, mod.Vmod, mod.Pmod)
                Pmp_mod_healthy.append(Pmp_m)
        Pmp_mod_healthy_sum = float(np.sum(Pmp_mod_healthy))

        # Healthy strings
        Pmp_str_healthy = []
        for pvstr in pvsys_healthy.pvstrs:
            Pmp_s, _, _ = mpp_from_curve(pvstr.Istring, pvstr.Vstring, pvstr.Pstring)
            Pmp_str_healthy.append(Pmp_s)
        Pmp_str_healthy_sum = float(np.sum(Pmp_str_healthy))

        # Healthy system
        Pmp_sys_healthy, _, _ = mpp_from_curve(pvsys_healthy.Isys,
                                               pvsys_healthy.Vsys,
                                               pvsys_healthy.Psys)

    # --- Loss decomposition ---
    loss_report = {}

    # Module degradation losses
    loss_mods_total = (Pmp_mod_healthy_sum - Pmp_mod_sum) if Pmp_mod_healthy_sum is not None else None
    loss_mods_degradation = loss_mods_total

    # Module >> String mismatch losses
    loss_mods_to_strs_mismatch = Pmp_mod_sum - Pmp_str_sum

    # String degradation losses
    loss_strs_total = (Pmp_str_healthy_sum - Pmp_str_sum) if Pmp_str_healthy_sum else None
    loss_strs_degradation = loss_strs_total - loss_mods_to_strs_mismatch

    # String >> System mismatch losses
    loss_strs_to_sys_mismatch = Pmp_str_sum - Pmp_sys

    # Total system losses
    loss_total = (Pmp_sys_healthy - Pmp_sys) if Pmp_sys_healthy else None
    loss_total_mismatch = loss_mods_to_strs_mismatch + loss_strs_to_sys_mismatch
    loss_total_degradation = (loss_total - loss_total_mismatch) if Pmp_sys_healthy else None

    loss_report.update({
        # System power levels (degraded and healthy)
        "total_system_power_degraded": Pmp_sys,
        "total_system_power_healthy": Pmp_sys_healthy,
        "total_string_power_degraded": Pmp_str_sum,
        "total_string_power_healthy": Pmp_str_healthy_sum,
        "total_module_power_degraded": Pmp_mod_sum,
        "total_module_power_healthy": Pmp_mod_healthy_sum,

        # Mismatch components
        "  Mismatch Components": "",
        "mismatch_modules_to_strings": loss_mods_to_strs_mismatch,
        "mismatch_strings_to_system": loss_strs_to_sys_mismatch,
        "mismatch_total": loss_total_mismatch,

        # Degradation components
        "  Degradation Components": "",
        "degradation_modules_only": loss_mods_degradation,
        "degradation_strings_only": loss_strs_degradation,
        "degradation_total": loss_total_degradation,

        # Total system loss
        "  Total System Loss": "",
        "loss_total": loss_total,

        # Percentages (relative to healthy)
        "  Percentages": "",
        "percent_mismatch": 100.0 * loss_total_mismatch / Pmp_sys_healthy if Pmp_sys_healthy else None,
        "percent_degradation": 100.0 * loss_total / Pmp_sys_healthy if (Pmp_sys_healthy and loss_total) else None,
        "percent_total": 100.0 * loss_total_degradation / Pmp_sys_healthy if Pmp_sys_healthy else None,
    })

    return loss_report

def plot_mismatch_report(report, show_values=True):
    """
    Grouped & stacked bar chart of module, string and system levels:
      • Healthy baseline (100%)
      • Degraded (no mismatch) – stacked actual + lost
      • Degraded + Mismatch – stacked actual + lost (string & system only)
    """

    # Healthy baselines
    total_mod_healthy = report["total_module_power_healthy"]
    total_str_healthy = report["total_string_power_healthy"]
    total_sys_healthy = report["total_system_power_healthy"]

    # Modules
    total_mod_actual = report["total_module_power_degraded"]
    mod_degradation = report["degradation_modules_only"] or 0.0

    # Strings
    total_str_actual = report["total_string_power_degraded"]
    str_degradation = report["degradation_strings_only"] or 0.0
    mismatch_mod_to_str = report["mismatch_modules_to_strings"]

    # Systems
    total_sys_actual = report["total_system_power_degraded"]
    sys_degradation = report["degradation_total"] or 0.0
    mismatch_str_to_sys = report["mismatch_strings_to_system"]

    # Total
    mismatch_total = report["mismatch_total"]

    levels = ["Module", "String", "System"]
    x = np.arange(len(levels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))

    # 1. Healthy baseline
    ax.bar(x - width, [total_mod_healthy, total_str_healthy, total_sys_healthy],
           width, color='lightgreen', label='Healthy')

    # 2. Degraded (no mismatch)
    ax.bar(x, [total_mod_healthy-mod_degradation, total_str_healthy-str_degradation, total_sys_healthy-sys_degradation],
           width, color='skyblue', label='Degraded – Actual')
    ax.bar(x, [mod_degradation, str_degradation, sys_degradation], width,
           bottom=[total_mod_healthy-mod_degradation, total_str_healthy-str_degradation, total_sys_healthy-sys_degradation],
           color='dodgerblue', alpha=0.6, label='Degraded – Lost')

    # 3. Degraded + Mismatch (only string & system)
    ax.bar(x + width, [0, total_str_actual, total_sys_actual],
           width, color='salmon', label='Degraded+Mismatch – Actual')
    ax.bar(x + width, [0, mismatch_mod_to_str, mismatch_total], width,
           bottom=[0, total_str_actual, total_sys_actual],
           color='red', alpha=0.6, label='Degraded+Mismatch – Lost')

    # Labels & annotations
    ax.set_xticks(x)
    ax.set_xticklabels(levels)
    ax.set_ylabel("Power [W]")
    ax.set_title("PV System Production at Module, String, and System Levels")

    if show_values:
        for i, val in enumerate([total_mod_healthy, total_str_healthy, total_sys_healthy]):
            ax.text(i - width, val + 0.02 * val, f"{val:.0f}", ha='center', va='bottom', fontsize=9)

        for i, (a, l) in enumerate(zip(
                [total_mod_healthy-mod_degradation, total_str_healthy-str_degradation, total_sys_healthy-sys_degradation],
                [mod_degradation, str_degradation, sys_degradation])):
            ax.text(i, a / 2, f"{a:.0f}", ha='center', va='center', color='white', fontsize=9)
            ax.text(i, a + l / 2, f"{l:.0f}", ha='center', va='center', color='white', fontsize=9)

        for i, (a, l) in enumerate(zip(
                [0, total_str_actual, total_sys_actual], [0, mismatch_mod_to_str, mismatch_total])):
            if a + l > 0:
                ax.text(i + width, a / 2, f"{a:.0f}", ha='center', va='center', color='white', fontsize=9)
                ax.text(i + width, a + l / 2, f"{l:.0f}", ha='center', va='center', color='white', fontsize=9)

    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.show()
