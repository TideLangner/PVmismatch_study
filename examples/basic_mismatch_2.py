import numpy as np
import matplotlib.pyplot as plt
from alternate_simulation.mismatch_report import mismatch_report, plot_mismatch_report
from basic_mismatch import *

def build_all_reports(healthy_sys, degraded_sys, mismatch_sys):
    """
    Build comparable mismatch/degradation reports for each scenario using the
    healthy system as the baseline reference.
    """
    reports = {
        "Healthy": mismatch_report(healthy_sys, pvsys_healthy=healthy_sys),
        "Fully Degraded": mismatch_report(degraded_sys, pvsys_healthy=healthy_sys),
        "Mismatch": mismatch_report(mismatch_sys, pvsys_healthy=healthy_sys),
    }
    return reports

def plot_mismatch_comparison(reports):
    """
    Grouped bar chart comparing mismatch components across scenarios:
      - mismatch_modules_to_strings
      - mismatch_strings_to_system
      - mismatch_total
    """
    labels = list(reports.keys())
    components = [
        ("mismatch_modules_to_strings", "Modules → Strings", "#f39c12"),
        ("mismatch_strings_to_system",  "Strings → System",  "#c0392b"),
        ("mismatch_total",              "Total Mismatch",    "#7f8c8d"),
    ]

    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, (key, disp, color) in enumerate(components):
        vals = [float(reports[name].get(key) or 0.0) for name in labels]
        ax.bar(x + (i - 1) * width, vals, width, label=disp, color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Power [W]")
    ax.set_title("Mismatch Components Across Scenarios")
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.legend(loc="best")
    plt.tight_layout()
    plt.show()

def plot_mismatch_dashboard_for(name, reports):
    """
    Optional: use the existing single-report dashboard to inspect one scenario.
    """
    print(f"Showing mismatch dashboard for: {name}")
    plot_mismatch_report(reports[name], show_values=True)

# Example usage:
# Build reports for Healthy, Fully Degraded, and Mismatch systems
reports = build_all_reports(my_system, my_degraded_system_1, mismatch_sys_1)

# 1) Compact comparison (recommended)
plot_mismatch_comparison(reports)

# 2) Optional detailed dashboard per scenario
# plot_mismatch_dashboard_for("Mismatch", reports)
# plot_mismatch_dashboard_for("Fully Degraded", reports)
# plot_mismatch_dashboard_for("Healthy", reports)


# ========

def interp_at_x(x, xp, fp):
    """
    Safe 1D interpolation: returns f(x) given sample (xp, fp).
    Assumes xp is 1D, can be unsorted; clamps x to [min(xp), max(xp)].
    """
    xp = np.asarray(xp).astype(float)
    fp = np.asarray(fp).astype(float)
    order = np.argsort(xp)
    xp_s = xp[order]
    fp_s = fp[order]
    x_clamped = np.clip(x, xp_s[0], xp_s[-1])
    return float(np.interp(x_clamped, xp_s, fp_s))

def compute_module_mismatch_map(pvsys):
    """
    For each module, compute mismatch loss [W] at the system MPP operating point:
      loss_mod = Pmp_mod - P_operating_at_system_MPP
    Returns:
      losses: 2D array [n_strings x n_modules]
      Vmp_sys, Imp_sys, Pmp_sys
    """
    # System MPP
    Pmp_sys, Imp_sys, Vmp_sys = mpp_from_curve(pvsys.Isys, pvsys.Vsys, pvsys.Psys)

    n_strings = len(pvsys.pvstrs)
    n_modules = len(pvsys.pvstrs[0].pvmods)
    losses = np.zeros((n_strings, n_modules), dtype=float)

    # Each string runs at V = Vmp_sys (parallel), get its operating current there
    for si, s in enumerate(pvsys.pvstrs):
        I_str_at_Vsys = interp_at_x(Vmp_sys, s.Vstring, s.Istring)

        # In series, each module current equals the string current
        for mi, m in enumerate(s.pvmods):
            # Module operating voltage at that current (invert I->V via interpolation)
            # We build V(I) by interpolating V as a function of I.
            # IV arrays can be monotonic decreasing in I vs V; interpolation handles that by sorting.
            V_mod_at_I = interp_at_x(I_str_at_Vsys, m.Imod, m.Vmod)
            P_oper = I_str_at_Vsys * V_mod_at_I

            # Module own MPP
            Pmp_mod = float(np.max(m.Pmod))

            # Mismatch loss contribution (clamped to >= 0 for display)
            losses[si, mi] = max(Pmp_mod - P_oper, 0.0)

    return losses, Vmp_sys, Imp_sys, Pmp_sys

def plot_mismatch_hotspots(pvsys, title="Module-level mismatch at system MPP"):
    """
    Visualize where mismatch occurs:
    - Heatmap of per-module mismatch loss [W] at the system MPP operating point.
    - Per-string loss sidebar annotations and total mismatch in the title.
    """
    losses, Vmp_sys, Imp_sys, Pmp_sys = compute_module_mismatch_map(pvsys)
    per_string = losses.sum(axis=1)
    total_mismatch = float(losses.sum())

    fig, ax = plt.subplots(figsize=(14, 4.5))
    im = ax.imshow(losses, aspect='auto', cmap='Reds')

    # Axes, labels
    ax.set_title(f"{title}\nSystem MPP: Vmp={Vmp_sys:.1f} V, Imp={Imp_sys:.1f} A, Pmp={Pmp_sys:.1f} W"
                 f"\nTotal mismatch (modules→strings + strings→system) ≈ {total_mismatch:.1f} W")
    ax.set_xlabel("Module Index")
    ax.set_ylabel("String Index")
    num_strings, num_modules = losses.shape
    ax.set_xticks(np.arange(num_modules))
    ax.set_yticks(np.arange(num_strings))
    ax.set_xticklabels([str(i) for i in range(num_modules)])
    ax.set_yticklabels([f"{i}" for i in range(num_strings)])

    # Gridlines
    ax.set_xticks(np.arange(-0.5, num_modules, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, num_strings, 1), minor=True)
    ax.grid(which="minor", color="black", linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    # Annotate values (optional; disable for large arrays)
    if num_modules <= 24 and num_strings <= 12:
        for i in range(num_strings):
            for j in range(num_modules):
                val = losses[i, j]
                if val > 0:
                    ax.text(j, i, f"{val:.0f}", ha="center", va="center",
                            fontsize=8, color="black")

    # Colourbar
    cbar = fig.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label("Module mismatch loss [W] at system MPP")

    # Right-side per-string annotations
    x_text = num_modules + 0.35
    ax.set_xlim(-0.5, num_modules - 0.5 + 2.0)
    for i, loss_w in enumerate(per_string):
        ax.text(x_text, i, f"String {i}: {loss_w:.0f} W", va="center",
                fontsize=9, color="dimgray")

    plt.tight_layout()
    plt.show()

# Example usage:
# plot_mismatch_hotspots(mismatch_sys_1)
