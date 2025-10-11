# Simulate all systems

import time
from datetime import timedelta
from sys_healthy import create_healthy, plot_healthy
from sys_degraded_fully import create_degraded, plot_degraded, plot_deg_vs_healthy_mods, plot_degradation_modes
from sys_mismatched import create_mismatched, create_mismatched_parametric, print_system
from sys_mismatch_calculator import loss_calculator
from sys_plotter import (plot_system_comparisons, plot_healthy_vs_mismatch, plot_mismatch_sweeps,
                         plot_mismatch_3d, save_mismatch_3d, plot_and_save_trend_surfaces)

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
degradation_mode = 3
# ======================================= #

# Start simulation timer
start = time.time()

# GLOBAL VARIABLES
# Healthy System
healthy = create_healthy()
cell_healthy = healthy["cell_healthy"]
Icell, Vcell, Pcell = healthy["Icell"], healthy["Vcell"], healthy["Pcell"]
mod_healthy = healthy["module_healthy"]
Imod, Vmod, Pmod = healthy["Imod"], healthy["Vmod"], healthy["Pmod"]
string_healthy = healthy["string_healthy"]
Istr, Vstr, Pstr = healthy["Istr"], healthy["Vstr"], healthy["Pstr"]
system_healthy = healthy["system_healthy"]
Isys, Vsys, Psys = healthy["Isys"], healthy["Vsys"], healthy["Psys"]

# Fully-Degraded System
degraded = create_degraded(degradation_mode)
cell_deg = degraded["cell_degraded"]
Icell_deg, Vcell_deg, Pcell_deg = degraded["Icell_deg"], degraded["Vcell_deg"], degraded["Pcell_deg"]
mod_deg = degraded["module_degraded"]
Imod_deg, Vmod_deg, Pmod_deg = degraded["Imod_deg"], degraded["Vmod_deg"], degraded["Pmod_deg"]
string_deg = degraded["string_degraded"]
Istr_deg, Vstr_deg, Pstr_deg = degraded["Istr_deg"], degraded["Vstr_deg"], degraded["Pstr_deg"]
system_degraded = degraded["system_degraded"]
Isys_deg, Vsys_deg, Psys_deg = degraded["Isys_deg"], degraded["Vsys_deg"], degraded["Psys_deg"]
deg_label = degraded["deg_label"]


def run_baselines():
    """Plot constant baseline systems"""

    # Healthy System
    plot_healthy(Icell=Icell, Vcell=Vcell, Pcell=Pcell)
    # plot_healthy(Imod=Imod, Vmod=Vmod, Pmod=Pmod,
    #              Istr=Istr, Vstr=Vstr, Pstr=Pstr,
    #              Isys=Isys, Vsys=Vsys, Psys=Psys)

    # # Fully-Degraded System
    # plot_degraded(Imod_deg=Imod_deg, Vmod_deg=Vmod_deg, Pmod_deg=Pmod_deg,
    #               Istr_deg=Istr_deg, Vstr_deg=Vstr_deg, Pstr_deg=Pstr_deg,
    #               Isys_deg=Isys_deg, Vsys_deg=Vsys_deg, Psys_deg=Psys_deg,
    #               deg_label=deg_label)
    # plot_deg_vs_healthy_mods(Imod=Imod, Vmod=Vmod, Pmod=Pmod,
    #                          Imod_deg=Imod_deg, Vmod_deg=Vmod_deg, Pmod_deg=Pmod_deg,
    #                          deg_label=deg_label)
    #
    # # Loop through all degradation scenarios and plot on the same figure
    # all_modes = []
    # for i in range(1, 7):
    #     degraded_i = create_degraded(degradation_mode=i)
    #     all_modes.append({
    #         "Imod_deg": degraded_i["Imod_deg"],
    #         "Vmod_deg": degraded_i["Vmod_deg"],
    #         "Pmod_deg": degraded_i["Pmod_deg"],
    #         "deg_label": degraded_i["deg_label"]
    #     })
    # plot_degradation_modes(Imod=Imod, Vmod=Vmod, Pmod=Pmod, all_modes=all_modes)

    # report_degraded = loss_calculator(system_degraded, system_healthy)
    # print("\n=== Degraded Baseline Report ===")
    # for k, v in report_degraded.items():
    #     print(f"{k}: {v}")
    # print((report_degraded["module_MPPs_sum_degraded"]/report_degraded["module_MPPs_sum_healthy"])*100, "%")


def run_mismatched_system(degraded_sets=3, min_degraded_modules=1, max_degraded_modules=30, clamp_after_max=False):
    """Create, calculate and plot mismatch report for a mismatched system"""

    # Create mismatched system
    system_mismatched = create_mismatched(degraded_sets=degraded_sets,
                                          min_degraded_modules=min_degraded_modules,
                                          max_degraded_modules=max_degraded_modules,
                                          clamp_after_max=clamp_after_max,
                                          module_healthy=mod_healthy, module_degraded=mod_deg)

    # Print system visual (binary matrix)
    print_system(system_mismatched, mod_deg)

    # Run loss calculation
    report_mismatch = loss_calculator(system_mismatched, system_healthy)

    # Print loss report
    print("\n=== Mismatch Breakdown ===")
    if min_degraded_modules == max_degraded_modules:
        for k, v in report_mismatch.items():
            if k.startswith("percent"):
                print(f"{k}: {v:.2f} %")
            else:
                print(f"{k}: {v:.2f} W")
    else:
        for k, v in report_mismatch.items():
            if k.startswith("percent_mismatch_strs_norm"):
                continue
            elif k.startswith("percent"):
                print(f"{k}: {v:.2f} %")
            else:
                print(f"{k}: {v:.2f} W")

    # Plot
    plot_system_comparisons(healthy=healthy, degraded=degraded, mismatched=system_mismatched)
    plot_healthy_vs_mismatch(healthy=system_healthy, mismatched=system_mismatched)


def run_sweep(mismatch_vs="total"):
    """Sweeps for mismatch plots"""

    # Sweep A:
    # - (y-axis) (string-normalised) module->string mismatch, (x-axis) degraded modules per string.
    # - Normalised to show mismatch for one string, not the entire system.
    k_values = list(range(0, 31))   # range of degraded modules
    mod2str_values = []
    mod2str_percents = []
    mod2str_percents_vs_loss = []
    for k in k_values:
        sys_k = create_mismatched(degraded_sets=1,
                                  min_degraded_modules=k, max_degraded_modules=k,
                                  clamp_after_max=True,
                                  module_healthy=mod_healthy, module_degraded=mod_deg)
        rep_k = loss_calculator(sys_k, system_healthy, num_strs_affected=30)
        mod2str_values.append(float(rep_k["mismatch_modules_to_strings"]))
        mod2str_percents.append(float(rep_k["percent_mismatch_strs_norm"]))
        mod2str_percents_vs_loss.append(float(rep_k["percent_mismatch_strs_norm_vs_loss"]))

    # Sweep B:
    # - (y-axis) strings->system mismatch, (x-axis) number of affected sets.
    # - Fixed number of degraded modules per string.
    n_min, n_max = 0, 150
    fixed_k_for_string_sweep = 30
    n_values = list(range(n_min, n_max + 1))
    str2sys_values = []
    str2sys_percents = []
    str2sys_percents_vs_loss = []
    for n in n_values:
        sys_n = create_mismatched_parametric(
            min_degraded_modules=fixed_k_for_string_sweep,
            num_degraded_strings=n,
            module_healthy=mod_healthy,
            module_degraded=mod_deg)
        rep_n = loss_calculator(sys_n, system_healthy, num_strs_affected=n)
        str2sys_values.append(float(rep_n["mismatch_strings_to_system"]))
        str2sys_percents.append(float(rep_n["percent_mismatch_total"]))
        str2sys_percents_vs_loss.append(float(rep_n["percent_mismatch_to_loss"]))

    # show time to simulate
    end = time.time()
    elapsed = end - start
    print(f"\nTotal time: {timedelta(seconds=elapsed)}")

    # Plot sweeps on one figure with two subplots
    if mismatch_vs == "total":
        plot_mismatch_sweeps(k_values, mod2str_values, n_values, str2sys_values, mod2str_percents, str2sys_percents)
    elif mismatch_vs == "loss":
        plot_mismatch_sweeps(k_values, mod2str_values, n_values, str2sys_values, mod2str_percents_vs_loss, str2sys_percents_vs_loss)
    else:
        raise ValueError("Invalid mismatch_vs value")


def run_parametric(resolution=30, metric_key="mismatch_total_W"):
    """Load a saved parametric surface and plot it in 3D.

    Parameters:
      resolution: 1, 5, 10, 30 (must match saved surface)
      metric_key: key inside the saved NPZ to plot. Examples:
        - "mismatch_total_W"
        - "percent_mismatch_total"
        - "metric_percent_mismatch_to_loss"
        - "metric_total_system_loss"
      The function will also try with a "metric_" prefix if not provided.
    """

    if resolution not in (1, 5, 10, 30):
        raise ValueError("Invalid resolution value. Must be 1, 5, 10 or 30.")

    from pathlib import Path
    import json
    import numpy as np
    import time
    from datetime import timedelta

    # Start timing for load/display only
    start_load = time.time()

    # Paths to saved artifacts
    out_dir = Path("results") / f"mode_{degradation_mode}"
    npz_path = out_dir / f"surface_res{resolution}.npz"
    meta_path = out_dir / f"surface_res{resolution}.metadata.json"

    # Validate presence
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing metadata file: {meta_path}. Generate and save the parametric data first.")
    if not npz_path.exists():
        raise FileNotFoundError(f"Missing data file: {npz_path}. Generate and save the parametric data first.")

    # Load metadata
    with open(meta_path, "r") as f:
        metadata = json.load(f)

    # Load arrays
    with np.load(npz_path) as data:
        try:
            K = data["K"]
            N = data["N"]
        except KeyError as e:
            raise KeyError(f"Saved data is missing required mesh array: {e}")

        # Resolve the requested key; allow missing 'metric_' prefix
        selected_key = None
        if metric_key in data.files:
            selected_key = metric_key
        else:
            alt = f"metric_{metric_key}" if not metric_key.startswith("metric_") else metric_key[len("metric_") :]
            if alt in data.files:
                selected_key = alt
            elif metric_key.startswith("metric_") and metric_key[len("metric_") :] in data.files:
                selected_key = metric_key[len("metric_") :]
        if selected_key is None:
            available = ", ".join(sorted(data.files))
            raise KeyError(f"Requested surface '{metric_key}' not found in saved data. Available keys: {available}")

        Z = data[selected_key]

    # Determine label/unit for plotting
    units_map = metadata.get("units", {})
    unit = units_map.get(selected_key)
    # Fallback unit inference
    if unit is None:
        unit = "%" if "percent" in selected_key.lower() else "W"

    # Human-readable label from key
    def humanize(key: str) -> str:
        # strip optional 'metric_' for display
        base = key[7:] if key.startswith("metric_") else key
        return base.replace("_", " ").title()

    z_label = humanize(selected_key)
    title = f"{z_label} Surface [{unit}]"

    # Report basic info from metadata to confirm load
    deg_label_loaded = metadata.get("deg_label", f"mode_{degradation_mode}")
    num_rows = metadata.get("num_rows")
    num_cols = metadata.get("num_cols")
    print(f"Loaded surface '{selected_key}' for {deg_label_loaded} at resolution={metadata.get('resolution')}, "
          f"shape={Z.shape} (rows={num_rows}, cols={num_cols}), unit={unit}")

    # show time to load
    end_load = time.time()
    elapsed = end_load - start_load
    print(f"\nLoad+plot prep time: {timedelta(seconds=elapsed)}")

    # Plot 3D surface (generic)
    plot_mismatch_3d(K, N, Z, z_mode=None, title=title, mode=degradation_mode, z_label=z_label, z_unit=unit)


def run_batch_plot_metrics(resolution=1, modes=range(1, 7)):
    """
    Iterate through degradation modes and save plots and summaries for selected metrics.

    Metrics:
      1 - metric_system_MPP_degraded          (Blues)
      2 - metric_total_system_loss            (Reds)
      3 - metric_mismatch_total               (Magma)
      4 - metric_percent_mismatch_total       (Magma)  # same as 3
      5 - metric_percent_mismatch_to_loss     (Cividis)

    Saved under: results_plotted/mode_{mode}/
    """
    from pathlib import Path
    import json
    import numpy as np
    import time

    base_plot_dir = Path("results_plotted")
    base_plot_dir.mkdir(parents=True, exist_ok=True)

    # colormap per metric (3 and 4 share 'magma')
    metric_specs = [
        ("metric_system_MPP_degraded",        "viridis"),
        ("metric_total_system_loss",          "cividis"),
        ("metric_mismatch_total",             "inferno"),
        ("metric_percent_mismatch_total",     "inferno"),
        ("metric_percent_mismatch_to_loss",   "plasma"),
    ]

    def humanize(key: str) -> str:
        base = key[7:] if key.startswith("metric_") else key
        return base.replace("_", " ").title()

    for mode_val in modes:
        out_dir = Path("results") / f"mode_{mode_val}"
        npz_path = out_dir / f"surface_res{resolution}.npz"
        meta_path = out_dir / f"surface_res{resolution}.metadata.json"

        if not meta_path.exists() or not npz_path.exists():
            print(f"[run_batch_plot_metrics] Skipping mode {mode_val}: missing saved data at resolution={resolution}")
            continue

        with open(meta_path, "r") as f:
            metadata = json.load(f)

        with np.load(npz_path) as data:
            # required meshes
            if "K" not in data.files or "N" not in data.files:
                print(f"[run_batch_plot_metrics] Skipping mode {mode_val}: missing K/N meshes")
                continue
            K = data["K"]
            N = data["N"]

            # prep output folder and summary file
            mode_plot_dir = base_plot_dir / f"mode_{mode_val}"
            mode_plot_dir.mkdir(parents=True, exist_ok=True)
            summary_lines = []
            summary_lines.append(f"Mode {mode_val} - {metadata.get('deg_label', '')} (resolution={metadata.get('resolution')})")
            summary_lines.append("")

            for metric_key, cmap in metric_specs:
                selected_key = None
                if metric_key in data.files:
                    selected_key = metric_key
                else:
                    alt = metric_key[len("metric_"):] if metric_key.startswith("metric_") else f"metric_{metric_key}"
                    if alt in data.files:
                        selected_key = alt

                if selected_key is None:
                    summary_lines.append(f"- {metric_key}: NOT FOUND")
                    continue

                Z = data[selected_key]
                units_map = metadata.get("units", {})
                unit = units_map.get(selected_key) or ("%" if "percent" in selected_key.lower() else "W")

                z_label = humanize(selected_key)
                title = f"{z_label} Surface [{unit}] — {metadata.get('deg_label', f'Mode {mode_val}')}"
                plot_path = mode_plot_dir / f"{selected_key}_res{resolution}.png"

                # Use the new saver (no window by default)
                save_mismatch_3d(
                    K, N, Z,
                    title=title,
                    z_label=z_label,
                    z_unit=unit,
                    cmap=cmap,
                    save_path=plot_path,
                    show=False
                )

                # Statistics and maxima to summary
                z_flat = Z.astype(float).ravel()
                finite_mask = np.isfinite(z_flat)
                if finite_mask.any():
                    z_max = float(np.nanmax(Z))
                    z_min = float(np.nanmin(Z))
                    z_mean = float(np.nanmean(Z))
                    flat_idx = int(np.nanargmax(Z))
                    imax, jmax = np.unravel_index(flat_idx, Z.shape)
                    k_max = int(K[imax, jmax])
                    n_max = int(N[imax, jmax])
                    summary_lines.append(
                        f"- {selected_key}: saved -> {plot_path.name} | unit={unit} | "
                        f"min={z_min:.3f}, mean={z_mean:.3f}, max={z_max:.3f} @ (K={k_max}, N={n_max})"
                    )
                else:
                    summary_lines.append(f"- {selected_key}: all values non-finite; plot saved as {plot_path.name}")

            summary_path = mode_plot_dir / f"summary_res{resolution}.txt"
            summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
            print(f"[run_batch_plot_metrics] Wrote {summary_path}")


def run_trend_surfaces(resolution=1, modes=range(1, 7),
                       metrics=("metric_mismatch_total", "metric_percent_mismatch_total",
                                "metric_total_system_loss", "metric_percent_mismatch_to_loss"),
                       out_root="results_plotted/trends",
                       show=False):
    """
    Load saved 3D surfaces for several degradation scenarios (modes) and, for each metric,
    plot all scenarios on a shared Z axis and connect their peaks.

    Saves outputs into: results_plotted/trends
    """
    from pathlib import Path
    import json
    import numpy as np

    # Prepare containers
    surfaces_by_metric = {m: {} for m in metrics}
    metric_meta = {}
    scenario_order = []
    K_ref = None
    N_ref = None

    for mode_val in modes:
        out_dir = Path("results") / f"mode_{mode_val}"
        npz_path = out_dir / f"surface_res{resolution}.npz"
        meta_path = out_dir / f"surface_res{resolution}.metadata.json"

        if not meta_path.exists() or not npz_path.exists():
            print(f"[run_trend_surfaces] Skipping mode {mode_val}: missing saved data at resolution={resolution}")
            continue

        with open(meta_path, "r") as f:
            metadata = json.load(f)

        scenario_label = metadata.get("deg_label", f"Mode {mode_val}")
        scenario_order.append(scenario_label)

        with np.load(npz_path) as data:
            if "K" not in data.files or "N" not in data.files:
                print(f"[run_trend_surfaces] Skipping mode {mode_val}: missing K/N meshes")
                continue

            K = data["K"]
            N = data["N"]

            # Ensure meshes are consistent across modes
            if K_ref is None and N_ref is None:
                K_ref, N_ref = K, N
            else:
                if K.shape != K_ref.shape or N.shape != N_ref.shape or not np.allclose(K, K_ref) or not np.allclose(N, N_ref):
                    print(f"[run_trend_surfaces] Skipping mode {mode_val}: K/N mesh mismatch vs reference")
                    continue

            # Load each requested metric if present
            for metric_key in metrics:
                selected_key = None
                if metric_key in data.files:
                    selected_key = metric_key
                else:
                    # allow missing/extra 'metric_' prefix
                    if metric_key.startswith("metric_"):
                        alt = metric_key[len("metric_"):]
                    else:
                        alt = f"metric_{metric_key}"
                    if alt in data.files:
                        selected_key = alt

                if selected_key is None:
                    print(f"[run_trend_surfaces] Mode {mode_val}: metric '{metric_key}' not found, skipping.")
                    continue

                Z = data[selected_key]
                surfaces_by_metric[metric_key][scenario_label] = Z

                # Collect meta (unit/label) once per metric
                units_map = metadata.get("units", {})
                unit = units_map.get(selected_key) or ("%" if "percent" in selected_key.lower() else "W")

                def humanize(key: str) -> str:
                    base = key[7:] if key.startswith("metric_") else key
                    return base.replace("_", " ").title()

                if metric_key not in metric_meta:
                    metric_meta[metric_key] = {
                        "label": humanize(selected_key),
                        "unit": unit,
                        "title": f"Trend Surfaces ({unit})"
                    }

    # Nothing to plot?
    any_data = any(bool(surfaces_by_metric[m]) for m in metrics)
    if not any_data or K_ref is None or N_ref is None:
        print("[run_trend_surfaces] No valid surfaces collected. Nothing to plot.")
        return

    # Call the new plotting helper; it will save PNGs and CSVs per metric
    plot_and_save_trend_surfaces(
        k_mesh=K_ref,
        set_mesh=N_ref,
        surfaces_by_metric=surfaces_by_metric,
        scenario_order=scenario_order,
        metric_meta=metric_meta,
        out_root=out_root,
        show=show,
        alpha=0.4,
    )


# ----- RUN -----
run_baselines()
# run_mismatched_system(degraded_sets=3, min_degraded_modules=1, max_degraded_modules=15, clamp_after_max=True)
# run_sweep(mismatch_vs="total")
# run_parametric(resolution=1, metric_key="metric_percent_mismatch_to_loss")
# run_batch_plot_metrics(resolution=1)
# run_trend_surfaces(resolution=1, modes=range(1, 7), show=False)
