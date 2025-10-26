# Tide Langner
# Plot mismatch components and scenarios

import numpy as np
import matplotlib.pyplot as plt
from sys_mismatch_calculator import mpp_from_curve, loss_calculator

def plot_system_comparisons(healthy=None, degraded=None, mismatched=None):
    """Plot all system curves

    Parameters:
    - healthy: healthy PVMismatch system
    - degraded: fully degraded PVMismatch system
    - mismatched: partially degraded PVMismatch system
    """
    from matplotlib.ticker import EngFormatter

    # Extract case_study_data
    Isys, Vsys, Psys = healthy["Isys"], healthy["Vsys"], healthy["Psys"]
    Isys_deg, Vsys_deg, Psys_deg = degraded["Isys_deg"], degraded["Vsys_deg"], degraded["Psys_deg"]
    deg_label = degraded["deg_label"]
    Vsys_mis, Isys_mis, Psys_mis = mismatched.Vsys, mismatched.Isys, mismatched.Psys

    fig, (ax_iv, ax_pv) = plt.subplots(1, 2, figsize=(11, 6))

    formatter = EngFormatter()
    ax_iv.xaxis.set_major_formatter(formatter)
    ax_iv.yaxis.set_major_formatter(formatter)
    ax_pv.xaxis.set_major_formatter(formatter)
    ax_pv.yaxis.set_major_formatter(formatter)

    # IV subplot
    ax_iv.plot(Vsys, Isys, label="Healthy System", color="tab:green")
    ax_iv.plot(Vsys_deg, Isys_deg, label=f"{deg_label} System", color="tab:red")
    ax_iv.plot(Vsys_mis, Isys_mis, label="Mismatched System", color="tab:purple")
    ax_iv.set_title("I–V Curves for All Systems", fontweight="bold")
    ax_iv.set_xlabel("Voltage [V]", fontweight="bold")
    ax_iv.set_xlim(0, 1.1 * np.max(Vsys))
    ax_iv.set_ylabel("Current [A]", fontweight="bold")
    ax_iv.set_ylim(0, 1.1 * np.max(Isys))
    ax_iv.grid(True, linestyle="--", alpha=0.4)
    ax_iv.legend()

    # PV subplot
    ax_pv.plot(Vsys, Psys, label="Healthy System", color="tab:green")
    ax_pv.plot(Vsys_deg, Psys_deg, label=f"{deg_label} System", color="tab:red")
    ax_pv.plot(Vsys_mis, Psys_mis, label="Mismatched System", color="tab:purple")
    ax_pv.set_title("P–V Curves for All Systems", fontweight="bold")
    ax_pv.set_xlabel("Voltage [V]", fontweight="bold")
    ax_pv.set_xlim(0, 1.1 * np.max(Vsys))
    ax_pv.set_ylabel("Power [W]", fontweight="bold")
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

    Parameters:
    - healthy: healthy PVMismatch system
    - mismatched: partially degraded PVMismatch system
    """
    from matplotlib.ticker import EngFormatter

    # Healthy curves and MPP
    Isys, Vsys, Psys = healthy.Isys, healthy.Vsys, healthy.Psys
    Pmp_sys, Imp_sys, Vmp_sys = mpp_from_curve(Isys, Vsys, Psys)

    # Mismatch curves and MPP
    Vsys_mis, Isys_mis, Psys_mis = mismatched.Vsys, mismatched.Isys, mismatched.Psys
    Pmp_mis, Imp_mis, Vmp_mis = mpp_from_curve(Isys_mis, Vsys_mis, Psys_mis)

    # Losses from mismatch calculator
    report = loss_calculator(mismatched, healthy)
    total_system_loss = float(report["total_system_loss"])
    mismatch_total = float(report["mismatch_total"])
    degradation_only = float(report["degradation_only"])

    # Axes limits
    Vmax = 1.1 * np.max(Vsys)
    Imax = 1.1 * np.max(Isys)
    Pmax = 1.1 * np.max(Psys)

    fig, (ax_iv, ax_pv) = plt.subplots(1, 2, figsize=(11, 6))

    formatter = EngFormatter()
    ax_iv.xaxis.set_major_formatter(formatter)
    ax_iv.yaxis.set_major_formatter(formatter)
    ax_pv.xaxis.set_major_formatter(formatter)
    ax_pv.yaxis.set_major_formatter(formatter)

    # --- IV subplot ---
    ax_iv.plot(Vsys, Isys, label="Healthy System", color="tab:green", lw=1.4)
    ax_iv.plot(Vsys_mis, Isys_mis, label="Mismatched System", color="tab:purple", lw=1.4)

    # Mark MPPs on IV
    ax_iv.plot([Vmp_sys], [Imp_sys], 'o', color="tab:green", ms=6)
    ax_iv.plot([Vmp_mis], [Imp_mis], 'o', color="tab:purple", ms=6)

    # Vertical guides at Vmp
    ax_iv.axvline(Vmp_sys, color="tab:green", ls="--", lw=1, alpha=0.7)
    ax_iv.axvline(Vmp_mis, color="tab:purple", ls="--", lw=1, alpha=0.7)

    ax_iv.set_title("I–V: Healthy vs Mismatch", fontweight="bold")
    ax_iv.set_xlabel("Voltage [V]", fontweight="bold")
    ax_iv.set_xlim(0, Vmax)
    ax_iv.set_ylabel("Current [A]", fontweight="bold")
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

    ax_pv.set_title("P–V: Healthy vs Mismatch", fontweight="bold")
    ax_pv.set_xlabel("Voltage [V]", fontweight="bold")
    ax_pv.set_xlim(0, Vmax)
    ax_pv.set_ylabel("Power [W]", fontweight="bold")
    ax_pv.set_ylim(0, Pmax)
    ax_pv.grid(True, linestyle="--", alpha=0.4)
    ax_pv.legend(loc="best")

    plt.tight_layout()
    plt.show()


def plot_parametric_2d(k_values, mod2str_values, set_values, str2sys_values,
                       percent_strs_values=None, percent_total_values=None,
                       mod2str_percents_vs_loss=None, str2sys_percents_vs_loss=None):
    """
    Plot mismatch as a function of (a) degraded modules per string and (b) number of affected sets.
    - Top: modules->strings mismatch vs degraded modules per string.
    - Bottom: strings->system mismatch vs number of affected sets (with num degraded modules constant).

    Parameters:
    - k_values: array-like of integers (degraded modules per string)
    - mod2str_values: array-like of floats [W] mismatch modules->strings (corresponding to k_values)
    - set_values: array-like of integers (number of affected sets)
    - str2sys_values: array-like of floats [W] mismatch strings->system (corresponding to set_values)
    - percent_strs_values: optional array-like of floats [%] percent_mismatch_strs (aligned with k_values)
    - percent_total_values: optional array-like of floats [%] percent_mismatch_total (aligned with set_values)
    - mod2str_percents_vs_loss: optional array-like of floats [%] percent_mismatch_strs_vs_loss (aligned with k_values)
    - str2sys_percents_vs_loss: optional array-like of floats [%] percent_mismatch_total_vs_loss (aligned with set_values)
    """
    from matplotlib.ticker import EngFormatter
    formatter = EngFormatter()

    fig, axes = plt.subplots(2, 1, figsize=(11, 7))

    # Top subplot: mod -> str mismatch vs degraded modules per string
    ax0 = axes[0]
    ln_w, = ax0.plot(k_values, mod2str_values, marker="o", color="mediumvioletred", label="String Mismatch (mods->str) [W]")
    ax0.set_title("(String-Normalised) Module -> String Mismatch vs Degraded Modules per String", fontweight="bold")
    ax0.set_xlabel("Degraded modules per string", fontweight="bold")
    ax0.set_ylabel("Mismatch [W]", fontweight="bold")
    ax0.grid(True, linestyle="--", alpha=0.4)
    ax0.xaxis.set_major_formatter(formatter)
    ax0.yaxis.set_major_formatter(formatter)

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
    ax1.set_title("Total String -> System Mismatch vs Affected Strings", fontweight="bold")
    ax1.set_xlabel("Number of affected strings", fontweight="bold")
    ax1.set_ylabel("Mismatch [W]", fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.xaxis.set_major_formatter(formatter)
    ax1.yaxis.set_major_formatter(formatter)

    # Secondary y-axis for percentages
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


def plot_parametric_3d(k_mesh, set_mesh, z_mesh, z_mode="W", title=None, mode=1, z_label=None, z_unit=None, deg_label=None):
    """
    Plot a 3D surface where:
      x-axis: number of degraded modules per string (0..30)
      y-axis: number of affected strings (0..150)
      z-axis: generic surface (units/label configurable)

    Parameters:
      k_mesh: 2D array (same shape as z_mesh) meshgrid of k values
      set_mesh: 2D array (same shape as z_mesh) meshgrid of set values
      z_mesh: 2D array of values (e.g., W or %)
      z_mode: legacy parameter ("W" or "%"); ignored if z_unit is provided
      title: figure title
      mode: degradation mode (for optional saving)
      z_label: axis label for Z (e.g., "Total System Loss")
      z_unit: unit string for Z (e.g., "W", "%")
      deg_label: optional degradation label to include in the plot title
    """
    from matplotlib.ticker import EngFormatter
    from mpl_toolkits.mplot3d import Axes3D

    # Backward compatibility for callers that pass only z_mode
    unit = z_unit if z_unit is not None else ("%" if z_mode == "%" else "W")
    label = z_label if z_label is not None else ("Total Mismatch" if unit in ("W", "%") else "Z Value")

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection="3d")

    formatter = EngFormatter()
    ax.set_proj_type('ortho')
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax.zaxis.set_major_formatter(formatter)

    surf = ax.plot_surface(k_mesh, set_mesh, z_mesh, cmap="viridis", linewidth=0, antialiased=True, alpha=0.9)
    ax.set_xlabel("Degraded modules per string", fontweight="bold")
    y_label = "Affected strings"
    ax.set_ylabel(y_label, fontweight="bold")
    ax.set_zlabel(f"{label} [{unit}]", fontweight="bold")
    if title:
        if deg_label:
            ax.set_title(f"{title}", fontweight="bold")
        elif mode is not None:
            ax.set_title(f"{title} for Mode {mode}", fontweight="bold")
        else:
            ax.set_title(title, fontweight="bold")

    fig.colorbar(surf, shrink=0.7, aspect=18, pad=0.08, label=unit)
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
        side_text = (
            f"Max value\n"
            f"z = {z_max:.2f} {unit}\n"
            f"K (mods/str) = {k_max:.0f}\n"
            f"{y_label} = {y_max:.0f}"
        )
        fig.text(
            0.06, 0.5, side_text,
            ha="left", va="center",
            fontsize=9,
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="crimson", alpha=0.9),
        )

        # Also print to console for quick reference
        print(f"[plot_mismatch_3d] Max at K={k_max:.0f}, {y_label.lower()}={y_max:.0f}: {z_max:.3f} {unit}")

    plt.show()


def save_parametric_3d(k_mesh, set_mesh, z_mesh, title=None, z_label=None, z_unit="W", cmap="viridis",
                       save_path=None, show=False, view=None):
    """
    Save a 3D surface plot to disk (optionally show).

    Parameters:
      k_mesh: 2D array meshgrid of K values (same shape as z_mesh)
      set_mesh: 2D array meshgrid of N values (same shape as z_mesh)
      z_mesh: 2D array of values to plot
      title: figure title text
      z_label: Z axis label (e.g., 'Total System Loss')
      z_unit: unit string for Z (e.g., 'W' or '%')
      cmap: matplotlib colormap name (e.g., 'viridis', 'Reds', 'magma', 'cividis')
      save_path: path to save (PDF recommended). If None, will not save.
      show: whether to display the window (False by default for batch use)
    """
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib.ticker import EngFormatter

    unit = z_unit or "W"
    label = z_label or ("Total Mismatch" if unit in ("W", "%") else "Z Value")

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection="3d")

    formatter = EngFormatter()
    ax.set_proj_type('ortho')
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax.zaxis.set_major_formatter(formatter)

    # top view option
    if view == 'top':
        ax.view_init(elev=90, azim=270)  # top-down, rotated 270deg for clarity
    else:
        ax.set_zlabel(f"{label} [{unit}]", fontweight="bold")

    surf = ax.plot_surface(k_mesh, set_mesh, z_mesh, cmap=cmap, linewidth=0, antialiased=True,
                           alpha=0.8, zorder=1)
    ax.set_xlabel("Degraded Modules per String", fontweight="bold")
    ax.set_ylabel("Affected Strings", fontweight="bold")
    if title:
        ax.set_title(title, fontweight="bold")

    cbar = fig.colorbar(surf, shrink=0.7, aspect=18, pad=0.08, label=unit, format=formatter)
    cbar.set_label(unit, rotation=0, labelpad=6, va='center')
    plt.tight_layout()

    # Annotate maximum (if any finite values)
    if np.isfinite(z_mesh).any():
        flat_idx = np.nanargmax(z_mesh)
        imax, jmax = np.unravel_index(flat_idx, z_mesh.shape)
        k_max = float(k_mesh[imax, jmax])
        y_max = float(set_mesh[imax, jmax])
        z_max = float(z_mesh[imax, jmax])

        # Skip scatter points and annotations for specified metrics
        if label in ["System Mpp Degraded", "Total System Loss"]:
            # scatter marker and guide at the max point
            ax.scatter([k_max], [y_max], [z_max], color="crimson", s=45, alpha=1, depthshade=False)
            ax.plot([k_max, k_max], [y_max, y_max], [0, z_max], color="crimson", lw=1.4, alpha=1)

            # side annotation (outside the 3D axes)
            side_text = (
                f"Max value = {z_max:.2f} {unit}\n"
                f"Degraded mods/str = {k_max:.0f}\n"
                f"Affected strings = {y_max:.0f}"
            )
            fig.text(
                0.0, 0.5, side_text,
                ha="left", va="center",
                fontsize=14,
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="crimson", alpha=0.9),
            )

        else:
            # scatter marker and guide at the max point
            ax.scatter([k_max], [y_max], [z_max], color="crimson", s=45, alpha=1, depthshade=False)
            ax.plot([k_max, k_max], [y_max, y_max], [0, z_max], color="crimson", lw=1.4, alpha=1)

            # side annotation (outside the 3D axes)
            side_text = (
                f"Max value = {z_max:.2f} {unit}\n"
                f"Degraded mods/str = {k_max:.0f}\n"
                f"Affected strings = {y_max:.0f}"
            )
            fig.text(
                0.0, 0.8, side_text,
                ha="left", va="center",
                fontsize=14,
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="crimson", alpha=0.9),
            )

            # Find all points where k * n matches k_max * n_max
            product = k_max * y_max
            tolerance = 1e-6
            valid_mask = np.abs(k_mesh * set_mesh - product) < tolerance
            k_valid, n_valid, z_valid = k_mesh[valid_mask], set_mesh[valid_mask], z_mesh[valid_mask]

            # Sort the valid points
            sorted_indices = np.argsort(z_valid)
            k_valid, n_valid, z_valid = k_valid[sorted_indices], n_valid[sorted_indices], z_valid[sorted_indices]

            if view == "top":
                # Secondary axes in front for high-contrast markers
                ax_overlay = fig.add_subplot(111, projection="3d")
                ax_overlay.set_xlim(ax.get_xlim())
                ax_overlay.set_ylim(ax.get_ylim())
                ax_overlay.set_zlim(ax.get_zlim())
                # Match view
                ax_overlay.view_init(elev=90, azim=270)

                # Make overlay axes visually transparent and on top
                ax_overlay.set_facecolor('none')
                ax_overlay.patch.set_alpha(0.0)
                ax_overlay.axis('off')
                ax_overlay.set_zorder(ax.get_zorder() + 1)

                # Scatter points with a halo + path effects for maximum contrast
                for i in range(0, len(k_valid)-1):
                    # 1) Halo underlay (bigger, white with black edge)
                    halo = ax_overlay.scatter(
                        k_valid[i], n_valid[i], z_valid[i],
                        s=45, color="white", edgecolor="white", linewidths=0.8,
                        alpha=1.0, depthshade=False, zorder=20
                    )

                    # 2) Foreground marker (dodgerblue) with stroke for extra contrast
                    fg = ax_overlay.scatter(
                        k_valid[i], n_valid[i], z_valid[i],
                        s=30, color="dodgerblue", edgecolor="black", linewidths=0.6,
                        alpha=1.0, depthshade=False, zorder=21
                    )

                    # 2D side text
                    point_text = (
                        f"z = {z_valid[i]:.2f} {unit}\n"
                        f"Degraded mods/str = {k_valid[i]:.0f}\n"
                        f"Affected strings = {n_valid[i]:.0f}"
                    )
                    fig.text(
                        0.0, 0.78 - ((i + 1) * 0.1), point_text,
                        ha="left", va="center", fontsize=10,
                        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="dodgerblue", alpha=0.9),
                    )

            else:
                # Normal markers for non-top views (no overlay/halo)
                for i in range(0, len(k_valid) - 1):
                    ax.scatter(k_valid[i], n_valid[i], z_valid[i], s=45, color="dodgerblue",
                               linewidths=0.4, alpha=1.0, depthshade=False, zorder=20)
                    # 2D side text
                    point_text = (
                        f"z = {z_valid[i]:.2f} {unit}\n"
                        f"Degraded mods/str = {k_valid[i]:.0f}\n"
                        f"Affected strings = {n_valid[i]:.0f}"
                    )
                    fig.text(
                        0.0, 0.78 - ((i + 1) * 0.1), point_text,
                        ha="left", va="center", fontsize=10,
                        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="dodgerblue", alpha=0.9),
                    )

    # Save or show the plot
    if save_path is not None:
        fig.savefig(save_path, dpi=600, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close(fig)


def plot_and_save_trend_surfaces(k_mesh, set_mesh, surfaces_by_metric, scenario_order=None, metric_meta=None,
                                 cmaps=None, alpha=0.4, out_root="results_plotted/trends", show=False):
    """
    Plot and save 3D surfaces for ALL degradation scenarios on a shared Z axis
    and connect their surface peaks with a line. Done separately for each metric.

    Parameters:
    - k_mesh: 2D numpy array meshgrid of K values (degraded modules per string)
    - set_mesh: 2D numpy array meshgrid of N values (affected strings)
    - surfaces_by_metric: dict mapping metric_key -> dict(scenario_label -> z_mesh_2d)
          Example:
              {"total_mismatch_W": {"Scenario A": Z_W_A,  # 2D array same shape as k_mesh
                                    "Scenario B": Z_W_B},
               "total_mismatch_%": {"Scenario A": Z_pct_A,
                                    "Scenario B": Z_pct_B}
              }
    - scenario_order: optional list of scenario labels; if provided, peaks will be connected in this order.
                      Otherwise, insertion order of the inner dict is used.
    - metric_meta: optional dict mapping metric_key -> {"label": "...", "unit": "...", "title": "..."}
                   If missing, sensible defaults are inferred from the metric key.
    - cmaps: optional dict mapping scenario_label -> matplotlib colormap name
             or a list of colormap names to cycle through.
    - alpha: float transparency for surfaces (0..1)
    - out_root: output directory. Results saved under results_plotted/trends by default.
    - show: whether to display figures interactively in addition to saving.

    Outputs per metric (under out_root):
    - <metric_key>_trend_surfaces.png: overlayed 3D surfaces and peak-connecting line
    - <metric_key>_peaks.csv: CSV with peak K, N, Z per scenario
    """
    from pathlib import Path
    import csv
    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    from matplotlib.ticker import EngFormatter

    # Ensure output directory exists
    out_dir = Path(out_root)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Metadata extraction helper
    def _infer_meta(key):
        key_l = str(key).lower()
        if "%" in key_l or "percent" in key_l or "_pct" in key_l or key_l.endswith("_%"):
            unit = "%"
        elif key_l.endswith("_w") or "watt" in key_l or key_l.endswith("[w]"):
            unit = "W"
        else:
            unit = ""
        if "mismatch" in key_l and unit:
            label = "Total Mismatch"
            title = f"Trend Surfaces ({unit})"
        else:
            label = "Metric"
            title = "Trend Surfaces"
        return {"label": label, "unit": unit, "title": title}

    # Build a color map iterator if not provided per scenario
    # Use a set of distinct colormaps for multiple surfaces
    default_cmaps_cycle = [
        "viridis", "plasma", "inferno", "magma", "cividis",
        "turbo" if hasattr(plt.colormaps, "__call__") else "cubehelix",
        "YlGnBu", "PuRd", "YlOrRd"
    ]
    if cmaps is None:
        cmaps = {}
    cmaps_list = cmaps if isinstance(cmaps, (list, tuple)) else default_cmaps_cycle

    for metric_key, scenario_dict in surfaces_by_metric.items():
        if not scenario_dict:
            continue

        # Use formatted title from metric_meta if available
        meta = (_infer_meta(metric_key) if not metric_meta or metric_key not in metric_meta
                else metric_meta[metric_key])
        # Extract readable metadata (title, label, unit)
        unit = meta.get("unit", "")
        zlabel = meta.get("label", "Metric")
        title = meta.get("title", f"Trend Surfaces {metric_key}")

        # Create figure/axes
        fig = plt.figure(figsize=(11, 7))
        ax = fig.add_subplot(111, projection="3d")

        formatter = EngFormatter()
        ax.set_proj_type('ortho')
        ax.xaxis.set_major_formatter(formatter)
        ax.yaxis.set_major_formatter(formatter)
        ax.zaxis.set_major_formatter(formatter)

        # Collect global Z-limits to ensure shared Z axis scaling
        zmins, zmaxs = [], []

        # Plot each scenario surface
        legend_handles = []
        scenario_labels = list(scenario_dict.keys())
        if scenario_order:
            # Keep only those in dict
            scenario_labels = [s for s in scenario_order if s in scenario_dict]

        peaks = []  # list of (scenario, k_peak, n_peak, z_peak)
        for idx, scenario in enumerate(scenario_labels):
            Z = scenario_dict[scenario]
            if Z is None or not np.isfinite(Z).any():
                continue

            # Choose colormap
            if isinstance(cmaps, dict) and scenario in cmaps:
                cmap_name = cmaps[scenario]
            else:
                cmap_name = cmaps_list[idx % len(cmaps_list)]
            cmap = plt.get_cmap(cmap_name)

            surf = ax.plot_surface(k_mesh, set_mesh, Z,cmap=cmap, linewidth=0, antialiased=True, alpha=alpha, zorder=1)

            # Legend proxy using a colored patch from the colourmap middle value
            mid_color = cmap(0.6)
            legend_handles.append(mpl.patches.Patch(color=mid_color, label=scenario, alpha=alpha))

            # Track Z limits
            zfinite = Z[np.isfinite(Z)]
            if zfinite.size:
                zmins.append(np.nanmin(zfinite))
                zmaxs.append(np.nanmax(zfinite))

            # Peak per scenario
            flat_idx = np.nanargmax(Z)
            imax, jmax = np.unravel_index(flat_idx, Z.shape)
            k_peak = float(k_mesh[imax, jmax])
            n_peak = float(set_mesh[imax, jmax])
            z_peak = float(Z[imax, jmax])

            ax.scatter([k_peak], [n_peak], [z_peak], color=mid_color, s=55, depthshade=False, edgecolor="k",
                       linewidth=0.4, zorder=50)
            peaks.append((scenario, k_peak, n_peak, z_peak))

        # Set labels and colourbar (use last surface's unit as common)
        ax.set_xlabel("Degraded modules per string", fontweight="bold")
        ax.set_ylabel("Affected strings", fontweight="bold")
        ax.set_zlabel(f"{zlabel}" + (f" [{unit}]" if unit else ""), fontweight="bold")

        # Shared Z-axis scaling
        if zmins and zmaxs:
            zmin, zmax = min(zmins), max(zmaxs)
            if np.isfinite([zmin, zmax]).all():
                # Add a small margin
                span = zmax - zmin if zmax > zmin else (abs(zmax) if zmax != 0 else 1.0)
                ax.set_zlim(zmin - 0.05 * span, zmax + 0.1 * span)

        # Title
        fig_title = title
        ax.set_title(fig_title)

        # Connect peaks with a line (in the order they were drawn)
        if len(peaks) >= 2:
            # If scenario_order provided, re-order peaks accordingly
            if scenario_order:
                order_map = {name: i for i, name in enumerate(scenario_order)}
                peaks.sort(key=lambda p: order_map.get(p[0], 1e9))
            else:
                # Keep the plotting order as collected
                pass

            k_line = [p[1] for p in peaks]
            n_line = [p[2] for p in peaks]
            z_line = [p[3] for p in peaks]

            ax.plot(k_line, n_line, z_line, color="crimson", lw=2.0, label="Peak trend", zorder=1000)

            # Also annotate first and last peaks
            ax.text(k_line[0], n_line[0], z_line[0], " start", color="crimson", fontsize=8, zorder=1001)
            ax.text(k_line[-1], n_line[-1], z_line[-1], " end", color="crimson", fontsize=8, zorder=1001)

            # Add a legend entry for the peak trend line
            legend_handles.append(mpl.lines.Line2D([0], [0], color="crimson", lw=2.6, label="Peak trend"))

        # Legend
        if legend_handles:
            ax.legend(handles=legend_handles, loc="best", framealpha=0.9)

        plt.tight_layout()

        # --- Save figure ---
        fig_path = Path(out_dir) / f"{metric_key}_trend_surfaces.pdf"
        fig.savefig(fig_path, dpi=900)

        # --- Save peaks CSV ---
        csv_path = Path(out_dir) / f"{metric_key}_peaks.csv"
        with open(csv_path, "w", newline="") as fcsv:
            writer = csv.writer(fcsv)
            writer.writerow(["scenario", "k_peak", "affected_strings_peak", "z_peak" + (f" [{unit}]" if unit else "")])
            for scenario, k_peak, n_peak, z_peak in peaks:
                writer.writerow([scenario, f"{k_peak:.0f}", f"{n_peak:.0f}", f"{z_peak:.6g}"])

        if show:
            plt.show()
        else:
            plt.close(fig)


