# Plot mismatch components and scenarios

import numpy as np
import matplotlib.pyplot as plt
from sys_mismatch_calculator import mpp_from_curve, loss_calculator

def plot_system_comparisons(healthy=None, degraded=None, mismatched=None):
    """Plot all system curves"""

    # Extract data
    Isys, Vsys, Psys = healthy["Isys"], healthy["Vsys"], healthy["Psys"]
    Isys_deg, Vsys_deg, Psys_deg = degraded["Isys_deg"], degraded["Vsys_deg"], degraded["Psys_deg"]
    deg_label = degraded["deg_label"]
    Vsys_mis, Isys_mis, Psys_mis = mismatched.Vsys, mismatched.Isys, mismatched.Psys

    fig, (ax_iv, ax_pv) = plt.subplots(1, 2, figsize=(11, 6))

    # IV subplot
    ax_iv.plot(Vsys, Isys, label="Healthy System", color="tab:green")
    ax_iv.plot(Vsys_deg, Isys_deg, label=f"{deg_label} System", color="tab:red")
    ax_iv.plot(Vsys_mis, Isys_mis, label="Mismatched System", color="tab:purple")
    ax_iv.set_title("I–V Curves for All Systems")
    ax_iv.set_xlabel("Voltage [V]")
    ax_iv.set_xlim(0, 1.1 * np.max(Vsys))
    ax_iv.set_ylabel("Current [A]")
    ax_iv.set_ylim(0, 1.1 * np.max(Isys))
    ax_iv.grid(True, linestyle="--", alpha=0.4)
    ax_iv.legend()

    # PV subplot
    ax_pv.plot(Vsys, Psys, label="Healthy System", color="tab:green")
    ax_pv.plot(Vsys_deg, Psys_deg, label=f"{deg_label} System", color="tab:red")
    ax_pv.plot(Vsys_mis, Psys_mis, label="Mismatched System", color="tab:purple")
    ax_pv.set_title("P–V Curves for All Systems")
    ax_pv.set_xlabel("Voltage [V]")
    ax_pv.set_xlim(0, 1.1 * np.max(Vsys))
    ax_pv.set_ylabel("Power [W]")
    ax_pv.set_ylim(0, 1.1 * np.max(Psys))
    ax_pv.grid(True, linestyle="--", alpha=0.4)
    ax_pv.legend()

    plt.tight_layout()
    plt.show()


def plot_healthy_vs_mismatch(healthy=None, mismatched=None):
    """
    Plot details for healthy vs mismatched system IV and PV curves.
    - Mark MPPs.
    - Dashed guide lines at each MPP.
    - Annotate healthy output, total loss and mismatch-only loss.
    - Show delta-P between MPPs on PV plot.
    """
    # Healthy curves and MPP
    Isys, Vsys, Psys = healthy.Isys, healthy.Vsys, healthy.Psys
    Pmp_sys, Imp_sys, Vmp_sys = mpp_from_curve(Isys, Vsys, Psys)

    # Mismatch curves and MPP
    Vsys_mis, Isys_mis, Psys_mis = mismatched.Vsys, mismatched.Isys, mismatched.Psys
    Pmp_mis, Imp_mis, Vmp_mis = mpp_from_curve(Isys_mis, Vsys_mis, Psys_mis)

    # Retrieve losses from mismatch calculator
    report = loss_calculator(mismatched, healthy)
    total_system_loss = float(report["total_system_loss"])
    mismatch_total = float(report["mismatch_total"])
    degradation_only = float(report["degradation_only"])

    # Axes limits
    Vmax = 1.1 * np.max(Vsys)
    Imax = 1.1 * np.max(Isys)
    Pmax = 1.1 * np.max(Psys)

    fig, (ax_iv, ax_pv) = plt.subplots(1, 2, figsize=(11, 6))

    # --- IV subplot ---
    ax_iv.plot(Vsys, Isys, label="Healthy System", color="tab:green", lw=1.4)
    ax_iv.plot(Vsys_mis, Isys_mis, label="Mismatched System", color="tab:purple", lw=1.4)

    # Mark MPPs on IV
    ax_iv.plot([Vmp_sys], [Imp_sys], 'o', color="tab:green", ms=6)
    ax_iv.plot([Vmp_mis], [Imp_mis], 'o', color="tab:purple", ms=6)

    # Vertical guides at Vmp
    ax_iv.axvline(Vmp_sys, color="tab:green", ls="--", lw=1, alpha=0.7)
    ax_iv.axvline(Vmp_mis, color="tab:purple", ls="--", lw=1, alpha=0.7)

    ax_iv.set_title("I–V: Healthy vs Mismatch")
    ax_iv.set_xlabel("Voltage [V]")
    ax_iv.set_xlim(0, Vmax)
    ax_iv.set_ylabel("Current [A]")
    ax_iv.set_ylim(0, Imax)
    ax_iv.grid(True, linestyle="--", alpha=0.4)
    ax_iv.legend(loc="best")

    # Text box with losses
    txt_iv = (
        f"Pmp Healthy = {Pmp_sys:.1f} W\n"
        f"Pmp Mismatch = {Pmp_mis:.1f} W\n"
        f"Total loss = {total_system_loss:.1f} W\n"
        f"Mismatch-only = {mismatch_total:.1f} W\n"
        f"Degradation-only = {degradation_only:.1f} W"
    )
    ax_iv.text(0.98, 0.02, txt_iv, transform=ax_iv.transAxes,
               ha="right", va="bottom", fontsize=9,
               bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="0.6", alpha=0.9))

    # --- PV subplot ---
    ax_pv.plot(Vsys, Psys, label="Healthy System", color="tab:green", lw=1.4)
    ax_pv.plot(Vsys_mis, Psys_mis, label="Mismatched System", color="tab:purple", lw=1.4)

    # Mark MPPs on PV
    ax_pv.plot([Vmp_sys], [Pmp_sys], 'o', color="tab:green", ms=6)
    ax_pv.plot([Vmp_mis], [Pmp_mis], 'o', color="tab:purple", ms=6)

    # Horizontal guides at Pmp
    ax_pv.axhline(Pmp_sys, color="tab:green", ls="--", lw=1, alpha=0.7)
    ax_pv.axhline(Pmp_mis, color="tab:purple", ls="--", lw=1, alpha=0.7)

    # Visual delta-P arrow between MPP powers
    x_arrow = 0.85 * Vmax
    # delta-P arrow
    ax_pv.annotate(
        "", xy=(x_arrow, Pmp_sys), xytext=(x_arrow, Pmp_mis),
        arrowprops=dict(arrowstyle="<->", color="crimson", lw=1.6),zorder=3
    )
    # text
    ax_pv.annotate(
        f"ΔP total = {total_system_loss:.1f} W\nMismatch={mismatch_total:.1f} W",
        xy=(x_arrow + 0.01 * Vmax, (Pmp_sys + Pmp_mis) / 2),
        xytext=(0, -6),  # move 6 points down
        textcoords="offset points",
        va="top", ha="left", color="crimson", fontsize=9
    )

    ax_pv.set_title("P–V: Healthy vs Mismatch")
    ax_pv.set_xlabel("Voltage [V]")
    ax_pv.set_xlim(0, Vmax)
    ax_pv.set_ylabel("Power [W]")
    ax_pv.set_ylim(0, Pmax)
    ax_pv.grid(True, linestyle="--", alpha=0.4)
    ax_pv.legend(loc="best")

    plt.tight_layout()
    plt.show()


def plot_mismatch_sweeps(k_values, mod2str_values, set_values, str2sys_values,
                         percent_strs_values=None, percent_total_values=None,
                         mod2str_percents_vs_loss=None, str2sys_percents_vs_loss=None):
    """
    Plot mismatch as a function of (a) degraded modules per string and (b) number of affected sets.
    - Top: modules->strings mismatch vs degraded modules per string.
    - Bottom: strings->system mismatch vs number of affected sets (with num degraded modules constant).

    Parameters:
      k_values: array-like of integers (degraded modules per string)
      mod2str_values: array-like of floats [W] mismatch modules->strings (corresponding to k_values)
      set_values: array-like of integers (number of affected sets)
      str2sys_values: array-like of floats [W] mismatch strings->system (corresponding to set_values)
      percent_strs_values: optional array-like of floats [%] percent_mismatch_strs (aligned with k_values)
      percent_total_values: optional array-like of floats [%] percent_mismatch_total (aligned with set_values)
      mod2str_percents_vs_loss: optional array-like of floats [%] percent_mismatch_strs_vs_loss (aligned with k_values)
      str2sys_percents_vs_loss: optional array-like of floats [%] percent_mismatch_total_vs_loss (aligned with set_values)
    """

    fig, axes = plt.subplots(2, 1, figsize=(11, 7))

    # Top subplot: mod -> str mismatch vs degraded modules per string
    ax0 = axes[0]
    ln_w, = ax0.plot(k_values, mod2str_values, marker="o", color="mediumvioletred", label="String Mismatch (mods->str) [W]")
    ax0.set_title("(String-Normalised) Module -> String Mismatch vs Degraded Modules per String")
    ax0.set_xlabel("Degraded modules per string")
    ax0.set_ylabel("Mismatch [W]")
    ax0.grid(True, linestyle="--", alpha=0.4)

    # Optional secondary y-axis for percentages
    lines0 = [ln_w]
    labels0 = [ln_w.get_label()]
    if (
            (percent_strs_values is not None and len(percent_strs_values) == len(k_values))
            or (mod2str_percents_vs_loss is not None and len(mod2str_percents_vs_loss) == len(k_values))
    ):
        ax0p = ax0.twinx()
        perc_ylim_values = []

        if percent_strs_values is not None and len(percent_strs_values) == len(k_values):
            ln_pct, = ax0p.plot(k_values, percent_strs_values, marker="x", color="deeppink",
                                label="Percent String Mismatch [%]")
            lines0.append(ln_pct)
            labels0.append(ln_pct.get_label())
            perc_ylim_values.extend(percent_strs_values)

        if mod2str_percents_vs_loss is not None and len(mod2str_percents_vs_loss) == len(k_values):
            ln_pct_vs, = ax0p.plot(k_values, mod2str_percents_vs_loss, marker="x", color="hotpink",
                                   label="Percent vs Loss (mods->str) [%]")
            lines0.append(ln_pct_vs)
            labels0.append(ln_pct_vs.get_label())
            perc_ylim_values.extend(mod2str_percents_vs_loss)

        ax0p.set_ylabel("Percent mismatch [%]")
        if perc_ylim_values:
            ax0p.set_ylim(0, max(1.05 * max(perc_ylim_values), 1e-9))
    ax0.legend(lines0, labels0, loc="best")

    # Bottom subplot: str -> sys mismatch vs affected sets/strings
    ax1 = axes[1]
    ln_w2, = ax1.plot(set_values, str2sys_values, marker="o", color="tab:purple", label="Mismatch (strs->sys) [W]")
    ax1.set_title("Total String -> System Mismatch vs Affected Strings")
    ax1.set_xlabel("Number of affected strings")
    ax1.set_ylabel("Mismatch [W]")
    ax1.grid(True, linestyle="--", alpha=0.4)

    # Optional secondary y-axis for percentages
    lines1 = [ln_w2]
    labels1 = [ln_w2.get_label()]
    if (
            (percent_total_values is not None and len(percent_total_values) == len(set_values))
            or (str2sys_percents_vs_loss is not None and len(str2sys_percents_vs_loss) == len(set_values))
    ):
        ax1p = ax1.twinx()
        perc2_ylim_values = []

        if percent_total_values is not None and len(percent_total_values) == len(set_values):
            ln_pct2, = ax1p.plot(set_values, percent_total_values, marker="x", color="mediumorchid",
                                 label="Percentage Total Mismatch [%]")
            lines1.append(ln_pct2)
            labels1.append(ln_pct2.get_label())
            perc2_ylim_values.extend(percent_total_values)

        if str2sys_percents_vs_loss is not None and len(str2sys_percents_vs_loss) == len(set_values):
            ln_pct2_vs, = ax1p.plot(set_values, str2sys_percents_vs_loss, marker="x", color="plum",
                                    label="Percent vs Loss (total) [%]")
            lines1.append(ln_pct2_vs)
            labels1.append(ln_pct2_vs.get_label())
            perc2_ylim_values.extend(str2sys_percents_vs_loss)

        ax1p.set_ylabel("Percent mismatch [%]")
        if perc2_ylim_values:
            ax1p.set_ylim(0, max(1.05 * max(perc2_ylim_values), 1e-9))
    ax1.legend(lines1, labels1, loc="best")

    plt.tight_layout()
    plt.show()


def plot_mismatch_3d(k_mesh, set_mesh, z_mesh, z_mode="W", title=None, mode=1):
    """
    Plot a 3D surface where:
      x-axis: number of degraded modules per string (0..30)
      y-axis: number of affected sets (0..5)
      z-axis: mismatch in W or %

    Parameters:
      k_mesh: 2D array (same shape as z_mesh) meshgrid of k values
      set_mesh: 2D array (same shape as z_mesh) meshgrid of set values
      z_mesh: 2D array of mismatch values (W or %)
      z_mode: "W" for watts, "%" for percentage
      title: currently "Total Mismatch Surface [W or %]"
    """
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    from pathlib import Path

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection="3d")

    surf = ax.plot_surface(k_mesh, set_mesh, z_mesh, cmap="viridis", linewidth=0, antialiased=True, alpha=0.9)
    ax.set_xlabel("Degraded modules per string")
    # Label y-axis based on range: if <=5 then sets, otherwise strings
    y_label = "Affected strings"
    ax.set_ylabel(y_label)
    if z_mode == "%":
        ax.set_zlabel("Total Mismatch [%]")
    else:
        ax.set_zlabel("Total Mismatch [W]")
    if title:
        ax.set_title(title)

    fig.colorbar(surf, shrink=0.7, aspect=18, pad=0.08, label="%" if z_mode == "%" else "W")
    plt.tight_layout()

    # Highlight and report the highest Z point (ignoring NaNs)
    if np.isfinite(z_mesh).any():
        flat_idx = np.nanargmax(z_mesh)
        imax, jmax = np.unravel_index(flat_idx, z_mesh.shape)
        k_max = float(k_mesh[imax, jmax])
        y_max = float(set_mesh[imax, jmax])
        z_max = float(z_mesh[imax, jmax])

        # Scatter marker at the max point
        ax.scatter([k_max], [y_max], [z_max], color="crimson", s=45, depthshade=False)

        # Vertical guide from base plane to max point
        ax.plot([k_max, k_max], [y_max, y_max], [0, z_max], color="crimson", lw=1.4, alpha=0.9)

        # Side annotation (outside the 3D axes)
        unit = "%" if z_mode == "%" else "W"
        side_text = (
            "Max mismatch\n"
            f"z = {z_max:.2f} {unit}\n"
            f"K (mods/str) = {k_max:.0f}\n"
            f"{y_label} = {y_max:.0f}"
        )
        # Place text in the right margin; adjust x/y if needed
        fig.text(
            0.06, 0.5, side_text,
            ha="left", va="center",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="crimson", alpha=0.9),
        )

        # Also print to console for quick reference
        print(f"[plot_mismatch_3d] Max mismatch at K={k_max:.0f}, {y_label.lower()}={y_max:.0f}: {z_max:.3f} {unit}")

    # Save to ~/Plots
    save_dir = Path.home() / "Plots"
    save_dir.mkdir(parents=True, exist_ok=True)
    if z_mode == "%":
        plt.savefig(save_dir / f"{mode}{mode}strs_mismatch_3d_surface_per.png", dpi=600)
        plt.savefig(save_dir / f"{mode}{mode}strs_mismatch_3d_surface_per.pdf")
    else:
        plt.savefig(save_dir / f"{mode}{mode}strs_mismatch_3d_surface_W.png", dpi=600)
        plt.savefig(save_dir / f"{mode}{mode}strs_mismatch_3d_surface_W.pdf")

    # plt.show()


