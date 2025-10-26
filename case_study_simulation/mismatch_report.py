# Tide Langner
# 25 August 2025
# Mismatch Loss Calculator

import numpy as np
import matplotlib.pyplot as plt
from textwrap import fill

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
    Plot mismatch report in stacked bar chart

      1) "healthy system output": single bar (system healthy Pmp).
      2) "degradation-only output": one stacked bar:
            - bottom: degradation-only output (healthy - degradation loss)
            - top: degradation loss
         (module/string/system degradation-only outputs are equal by construction)
      3) "module->string mismatch loss": one stacked bar:
            - bottom: total_string_actual (with module->string mismatch applied)
            - top: mismatch_modules_to_strings
      4) "string->system mismatch loss": one stacked bar:
            - bottom: total_system_actual (final actual)
            - top: mismatch_strings_to_system

      Also annotates percentages of:
        - degradation loss
        - mismatch (mod->str)
        - mismatch (str->sys)
        - mismatch_total
    """

    # Healthy references (equal at module/string/system levels in this report's formulation)
    total_sys_healthy = report.get("total_system_power_healthy")
    H = total_sys_healthy if total_sys_healthy is not None else 0.0

    # Degradation-only (equal across levels so use system level)
    deg_loss = report.get("degradation_total") or 0.0
    deg_only_output = max(H - deg_loss, 0.0)

    # Actual outputs and mismatch components
    total_str_actual = report.get("total_string_power_degraded") or 0.0
    total_sys_actual = report.get("total_system_power_degraded") or 0.0
    mismatch_mod_to_str = report.get("mismatch_modules_to_strings") or 0.0
    mismatch_str_to_sys = report.get("mismatch_strings_to_system") or 0.0
    mismatch_total = report.get("mismatch_total") or 0.0

    # Helper for percentages relative to healthy
    def pct(x):
        return 100.0 * x / H if H else 0.0

    pct_deg = pct(deg_loss)
    pct_mm_mod_str = pct(mismatch_mod_to_str)
    pct_mm_str_sys = pct(mismatch_str_to_sys)
    pct_mm_total = pct(mismatch_total)

    # Layout
    labels = [
        "healthy system output",
        "degradation-only output",
        "module->string mismatch loss",
        "string->system mismatch loss",
    ]
    x = np.arange(len(labels))
    width = 0.5

    fig, ax = plt.subplots(figsize=(10, 6))

    # 1) Healthy system output
    ax.bar(x[0], H, width, color='lightgreen', label='Healthy')

    # 2) Degradation-only stacked bar
    ax.bar(x[1], deg_only_output, width, color='skyblue', label='Degradation-only Output')
    ax.bar(x[1], deg_loss, width, bottom=deg_only_output, color='dodgerblue', alpha=0.7, label='Degradation-only Loss')

    # 3) Module->String mismatch stacked bar
    ax.bar(x[2], total_str_actual, width, color='peachpuff', label='String Output')
    ax.bar(x[2], mismatch_mod_to_str, width, bottom=total_str_actual, color='orangered', alpha=0.75, label='Mismatch (mod->str)')

    # 4) String->System mismatch stacked bar
    ax.bar(x[3], total_sys_actual, width, color='mistyrose', label='System Output')
    ax.bar(x[3], mismatch_str_to_sys, width, bottom=total_sys_actual, color='crimson', alpha=0.75, label='Mismatch (str->sys)')

    # Axes/labels
    wrapped_labels = [fill(lbl, width=16) for lbl in labels]
    ax.set_xticks(x)
    ax.set_xticklabels(wrapped_labels, rotation=0)
    ax.set_ylabel("Power [W]")
    ax.set_title("Healthy vs Degradation-only and Mismatch Losses")

    # Numeric annotations
    if show_values:
        # Healthy
        if H:
            ax.text(x[0], H * 1.01, f"{H:.0f} W", ha="center", va="bottom", fontsize=9, color="black")

        # Degradation-only
        if deg_only_output:
            ax.text(x[1], deg_only_output / 2, f"{deg_only_output:.0f} W", ha="center", va="center", color="black",
                    fontsize=9)
        if deg_loss:
            ax.text(x[1], deg_only_output + deg_loss / 2, f"{deg_loss:.0f} W\n({pct_deg:.1f}%)",
                    ha="center", va="center", color="black", fontsize=9)

        # Mod->Str mismatch
        if total_str_actual:
            ax.text(x[2], total_str_actual / 2, f"{total_str_actual:.0f} W", ha="center", va="center", color="black",
                    fontsize=9)
        if mismatch_mod_to_str:
            ax.text(x[2], total_str_actual + mismatch_mod_to_str / 2,
                    f"{mismatch_mod_to_str:.0f} W\n({pct_mm_mod_str:.1f}%)",
                    ha="center", va="center", color="black", fontsize=9)

        # Str->Sys mismatch
        if total_sys_actual:
            ax.text(x[3], total_sys_actual / 2, f"{total_sys_actual:.0f} W", ha="center", va="center", color="black",
                    fontsize=9)
        if mismatch_str_to_sys:
            ax.text(x[3], total_sys_actual + mismatch_str_to_sys / 2,
                    f"{mismatch_str_to_sys:.0f} W\n({pct_mm_str_sys:.1f}%)",
                    ha="center", va="center", color="black", fontsize=9)

        # Total mismatch note
        ymax = max(
            H,
            deg_only_output + deg_loss,
            total_str_actual + mismatch_mod_to_str,
            total_sys_actual + mismatch_str_to_sys
        )
        if mismatch_total:
            ax.text(x[-1] + 0.55, ymax * 0.95, f"Total Mismatch: {mismatch_total:.0f} W ({pct_mm_total:.1f}%)",
                    ha="left", va="top", fontsize=9, color="dimgray")

    # Legend
    handles, labels_ = ax.get_legend_handles_labels()
    uniq = dict(zip(labels_, handles))
    ax.legend(uniq.values(), uniq.keys(), loc="best")

    ax.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.show()
