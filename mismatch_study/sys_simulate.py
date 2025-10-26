# Tide Langner
# Simulate all systems

import time
from datetime import timedelta

from case_study_data.module_specs import degraded_module
from sys_healthy import create_healthy, plot_healthy
from sys_degraded_fully import create_degraded, plot_degraded, plot_deg_vs_healthy_mods, plot_degradation_modes
from sys_mismatched import create_mismatched_pyramid, create_mismatched_parametric, print_system, create_mismatched_multimodal
from sys_mismatch_calculator import loss_calculator
from sys_plotter import (plot_system_comparisons, plot_healthy_vs_mismatch, plot_parametric_2d,
                         plot_parametric_3d, save_parametric_3d, plot_and_save_trend_surfaces)
from sys_save import save_parametric_discrete_modal, save_parametric_multi_modal

# ======== SET DEGRADATION MODE ========= #
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
    plot_healthy(Imod=Imod, Vmod=Vmod, Pmod=Pmod,
                 Istr=Istr, Vstr=Vstr, Pstr=Pstr,
                 Isys=Isys, Vsys=Vsys, Psys=Psys)

    # Fully-Degraded System
    plot_degraded(Imod_deg=Imod_deg, Vmod_deg=Vmod_deg, Pmod_deg=Pmod_deg,
                  Istr_deg=Istr_deg, Vstr_deg=Vstr_deg, Pstr_deg=Pstr_deg,
                  Isys_deg=Isys_deg, Vsys_deg=Vsys_deg, Psys_deg=Psys_deg,
                  deg_label=deg_label)
    plot_deg_vs_healthy_mods(Imod=Imod, Vmod=Vmod, Pmod=Pmod,
                             Imod_deg=Imod_deg, Vmod_deg=Vmod_deg, Pmod_deg=Pmod_deg,
                             deg_label=deg_label)

    # Loop through all degradation scenarios and plot on the same figure
    all_modes = []
    for i in range(1, 7):
        degraded_i = create_degraded(degradation_mode=i)
        all_modes.append({
            "Imod_deg": degraded_i["Imod_deg"],
            "Vmod_deg": degraded_i["Vmod_deg"],
            "Pmod_deg": degraded_i["Pmod_deg"],
            "deg_label": degraded_i["deg_label"]
        })
    plot_degradation_modes(Imod=Imod, Vmod=Vmod, Pmod=Pmod, all_modes=all_modes)

    report_degraded = loss_calculator(system_degraded, system_healthy)
    print("\n=== Degraded Baseline Report ===")
    for k, v in report_degraded.items():
        print(f"{k}: {v}")
    print((report_degraded["module_MPPs_sum_degraded"]/report_degraded["module_MPPs_sum_healthy"])*100, "%")

    # show time to simulate
    end = time.time()
    elapsed = end - start
    print(f"\nTotal time: {timedelta(seconds=elapsed)}")


def run_mismatch_pyramid(degraded_sets=3, min_degraded_modules=1, max_degraded_modules=30, clamp_after_max=False):
    """Create, calculate and plot mismatch report for a mismatched system

    Parameters:
    - degraded_sets (int): number of sets of degraded modules to include in the system [0-5]
    - min_degraded_modules (int): minimum number of degraded modules per set [1-30]
    - max_degraded_modules (int): maximum number of degraded modules per set [<=30]
    - clamp_after_max (bool): if True, remaining strings in the set will clamp at the same number of
      degraded modules to the maximum value, else healthy.
    """

    # Create pyramid-like mismatched system
    system_mismatched = create_mismatched_pyramid(degraded_sets=degraded_sets,
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

    # show time to simulate
    end = time.time()
    elapsed = end - start
    print(f"\nTotal time: {timedelta(seconds=elapsed)}")


def run_mismatch_parametric_2d(mismatch_vs="total"):
    """Sweeps for mismatch plots

    Parameter:
    - mismatch_vs (string): "total" or "loss"
    """

    # Plot A:
    # - (y-axis): (string-normalised) module->string mismatch.
    # - (x-axis): degraded modules per string.
    # - Normalised to show mismatch for one string, not the entire system.
    k_values = list(range(0, 31))   # range of degraded modules
    mod2str_values = []
    mod2str_percents = []
    mod2str_percents_vs_loss = []
    for k in k_values:
        sys_k = create_mismatched_pyramid(degraded_sets=1,
                                          min_degraded_modules=k, max_degraded_modules=k,
                                          clamp_after_max=True,
                                          module_healthy=mod_healthy, module_degraded=mod_deg)
        rep_k = loss_calculator(sys_k, system_healthy, num_strs_affected=30)
        mod2str_values.append(float(rep_k["mismatch_modules_to_strings"]))
        mod2str_percents.append(float(rep_k["percent_mismatch_strs_norm"]))
        mod2str_percents_vs_loss.append(float(rep_k["percent_mismatch_strs_norm_vs_loss"]))

    # Plot B:
    # - (y-axis): strings->system mismatch.
    # - (x-axis): number of affected sets.
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

    # Plot metrics on one figure with two subplots
    if mismatch_vs == "total":
        plot_parametric_2d(k_values, mod2str_values, n_values, str2sys_values, mod2str_percents, str2sys_percents)
    elif mismatch_vs == "loss":
        plot_parametric_2d(k_values, mod2str_values, n_values, str2sys_values, mod2str_percents_vs_loss, str2sys_percents_vs_loss)
    else:
        raise ValueError("Invalid mismatch_vs value")

    # show time to simulate
    end = time.time()
    elapsed = end - start
    print(f"\nTotal time: {timedelta(seconds=elapsed)}")


def run_mismatch_parametric_3d(resolution=30, metric_key="mismatch_total_W", deg_mode=1):
    """Load a saved parametric surface and plot it in 3D.

    Parameters:
    - resolution: 1, 5, 10, 30 (must match saved surface)
    - metric_key: key inside the saved NPZ to plot. Examples:
        > "mismatch_total_W"
        > "percent_mismatch_total"
        > "metric_percent_mismatch_to_loss"
        > "metric_total_system_loss"
    - The function will also try with a "metric_" prefix if not provided.
    - deg_mode: degradation mode
    """

    if resolution not in (1, 5, 10, 30):
        raise ValueError("Invalid resolution value. Must be 1, 5, 10 or 30.")

    from pathlib import Path
    import json
    import numpy as np
    import time
    from datetime import timedelta

    start = time.time()

    # Paths to saved artifacts
    out_dir = Path("results") / f"mode_{deg_mode}"
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
            alt = f"metric_{metric_key}" if not metric_key.startswith("metric_") else metric_key[len("metric_"):]
            if alt in data.files:
                selected_key = alt
            elif metric_key.startswith("metric_") and metric_key[len("metric_"):] in data.files:
                selected_key = metric_key[len("metric_"):]
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

    # Format label from key
    def format_label(key: str) -> str:
        # strip optional 'metric_' for display
        base = key[7:] if key.startswith("metric_") else key
        return base.replace("_", " ").title()

    z_label = format_label(selected_key)
    deg_label_loaded = metadata.get("deg_label", f"mode_{deg_mode}")
    title = f"{z_label} Surface [{unit}] — {deg_label_loaded}"

    # Report basic info from metadata to confirm load
    num_rows = metadata.get("num_rows")
    num_cols = metadata.get("num_cols")
    print(f"Loaded surface '{selected_key}' for {deg_label_loaded} at resolution={metadata.get('resolution')}, "
          f"shape={Z.shape} (rows={num_rows}, cols={num_cols}), unit={unit}")

    # show time to load
    end = time.time()
    elapsed = end - start
    print(f"\nLoad+plot prep time: {timedelta(seconds=elapsed)}")

    # Plot 3D surface (generic)
    plot_parametric_3d(K, N, Z, z_mode=None, title=title, mode=deg_mode, z_label=z_label, z_unit=unit,
                       deg_label=deg_label_loaded)


def save_parametric_results(resolution=30, mode_id=None):
    """
    Save the discrete-modal parametric surfaces for the current degraded mode.
    (Can iterate through all 1-6 modes)

    Parameters:
      resolution: 1, 5, 10, 30 (step along affected-strings axis)
      mode_id: folder id for results/mode_{mode_id}; defaults to global degradation_mode
    """
    mid = degradation_mode if mode_id is None else int(mode_id)
    save_parametric_discrete_modal(
        resolution=resolution,
        degradation_mode=mid,
        deg_label=deg_label,
        system_healthy=system_healthy,
        mod_healthy=mod_healthy,
        mod_deg=mod_deg,
    )


def save_parametric_surfaces(resolution=1, modes=range(1, 7), view=None):
    """
    Iterate through degradation modes and save plots and summaries for selected metrics.

    Parameters:
    - resolution (int): 1, 5, 10, 30 (must match saved surface)
    - view (string): "top" or "ortho"

    Metrics:
      1 - metric_system_MPP_degraded          (Viridis)
      2 - metric_total_system_loss            (Cividis)
      3 - metric_mismatch_total               (Inferno)
      4 - metric_percent_mismatch_total       (Inferno)  # same as 3
      5 - metric_percent_mismatch_to_loss     (Plasma)

    Saved under: results_plotted/mode_{mode}/
    """
    from pathlib import Path
    import json
    import numpy as np
    import time

    base_plot_dir = Path("results_plotted")
    base_plot_dir.mkdir(parents=True, exist_ok=True)

    # colormap per metric (3 and 4 share 'inferno')
    metric_specs = [
        ("metric_system_MPP_degraded",        "viridis"),
        ("metric_total_system_loss",          "cividis"),
        ("metric_mismatch_total",             "inferno"),
        ("metric_percent_mismatch_total",     "inferno"),
        ("metric_percent_mismatch_to_loss",   "plasma"),
    ]

    # Format label from key
    def format_label(key: str) -> str:
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

                z_label = format_label(selected_key)
                title = f"{z_label} Surface [{unit}] — {metadata.get('deg_label', f'Mode {mode_val}')}"

                if view == "top":
                    plot_path = mode_plot_dir / f"{selected_key}_res{resolution}_top.pdf"
                else:
                    plot_path = mode_plot_dir / f"{selected_key}_res{resolution}.pdf"

                # Plot and save
                save_parametric_3d(K, N, Z, title=title, z_label=z_label, z_unit=unit,
                                   cmap=cmap, save_path=plot_path, show=False, view=view)

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

    # show time to load
    end = time.time()
    elapsed = end - start
    print(f"\nLoad+plot prep time: {timedelta(seconds=elapsed)}")


def save_trend_surfaces(resolution=1, modes=range(1, 7), show=False,
                        metrics=("metric_mismatch_total", "metric_percent_mismatch_total",
                                "metric_total_system_loss", "metric_percent_mismatch_to_loss"),
                        out_root="results_plotted/trends"):
    """
    Load saved 3D surfaces for several degradation scenarios (modes) and, for each metric,
    plot all scenarios on a shared Z axis and connect their peaks.

    Parameters:
    - resolution (int): 1, 5, 10, 30 (must match saved surface)
    - show (bool): if True, show the plot after saving it
    - metrics (iterable): iterable of metric keys to plot
    - out_root (str): output folder path (default: results_plotted/trends)

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

    # Format label from key
    def format_label(key: str) -> str:
        base = key[7:] if key.startswith("metric_") else key
        return base.replace("_", " ").title()

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
                if K.shape != K_ref.shape or N.shape != N_ref.shape or not np.allclose(K, K_ref) or not np.allclose(N,
                                                                                                                    N_ref):
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

                if metric_key not in metric_meta:
                    metric_meta[metric_key] = {
                        "label": format_label(selected_key),
                        "unit": unit,
                        "title": f"{format_label(selected_key)} Trend Surfaces ({unit})"
                    }

    # Nothing to plot?
    any_data = any(bool(surfaces_by_metric[m]) for m in metrics)
    if not any_data or K_ref is None or N_ref is None:
        print("[run_trend_surfaces] No valid surfaces collected. Nothing to plot.")
        return

    # Call plot to save
    plot_and_save_trend_surfaces(k_mesh=K_ref, set_mesh=N_ref, surfaces_by_metric=surfaces_by_metric,
                                 scenario_order=scenario_order, metric_meta=metric_meta,
                                 out_root=out_root, show=show, alpha=0.4)

    # show time to load
    end = time.time()
    elapsed = end - start
    print(f"\nLoad+plot prep time: {timedelta(seconds=elapsed)}")


def save_multimodal_results(resolution=30, levels=(1, 2, 3, 4, 5, 6), mode_id=999):
    """
    Build L degraded module variants, save the multimodal equal-spread parametric surfaces,
    and then plot them using the existing helpers.

    Parameters:
      resolution: 1, 5, 10, 30 (step along affected-strings axis)
      levels: iterable of degradation_mode integers to instantiate degraded module variants
      mode_id: integer used as folder id under results/mode_{mode_id}
    """
    # Prepare degraded module variants in the requested order
    modules_degraded_levels = []
    for lv in levels:
        d = create_degraded(degradation_mode=int(lv))
        modules_degraded_levels.append(d["module_degraded"])

    # Label to embed in metadata/plots
    L = len(modules_degraded_levels)
    deg_lbl = f"Multimodal Spread (L={L})"

    # Save full surfaces
    save_parametric_multi_modal(
        resolution=resolution,
        degradation_mode=mode_id,
        deg_label=deg_lbl,
        system_healthy=system_healthy,
        mod_healthy=mod_healthy,
        modules_degraded_levels=modules_degraded_levels,
    )


def save_multimodal_surfaces(*, mode_id=999, resolution=1, view=None,
                             out_root="results_plotted/multimodal",
                             metrics=None, overwrite=False):
    """
    Load the saved multimodal parametric NPZ for a given mode_id (e.g., 999),
    and save 3D metric surfaces to a separate folder hierarchy.

    Outputs: <out_root>/mode_{mode_id}/
      - <metric_key>_res{resolution}.pdf (or *_top.pdf if view='top')
      - summary_res{resolution}.txt
    """
    from pathlib import Path
    import json
    import numpy as np

    # Metric keys to plot and their colormaps
    # If 'metrics' is provided, it overrides this default list
    metric_specs = metrics or [
        ("metric_system_MPP_degraded",        "viridis"),
        ("metric_total_system_loss",          "cividis"),
        ("metric_mismatch_total",             "inferno"),
        ("metric_percent_mismatch_total",     "inferno"),
        ("metric_percent_mismatch_to_loss",   "plasma"),
    ]

    def format_label(key: str) -> str:
        base = key[7:] if key.startswith("metric_") else key
        return base.replace("_", " ").title()

    # If a file already exists and overwrite=False, generate a unique variant name
    def unique_path(p: Path) -> Path:
        if not p.exists():
            return p
        idx = 2
        while True:
            cand = p.with_name(f"{p.stem}_v{idx}{p.suffix}")
            if not cand.exists():
                return cand
            idx += 1

    # Locate saved NPZ/metadata produced by the multimodal saver for the given mode_id/resolution
    src_dir = Path("results") / f"mode_{mode_id}"
    npz_path = src_dir / f"surface_res{resolution}.npz"
    meta_path = src_dir / f"surface_res{resolution}.metadata.json"

    if not meta_path.exists() or not npz_path.exists():
        print(f"[save_multimodal_metric_surfaces] Missing saved data for mode {mode_id} at resolution={resolution}")
        return

    mode_plot_dir = Path(out_root) / f"mode_{mode_id}"
    mode_plot_dir.mkdir(parents=True, exist_ok=True)

    with open(meta_path, "r") as f:
        metadata = json.load(f)

    with np.load(npz_path) as data:
        if "K" not in data.files or "N" not in data.files:
            print(f"[save_multimodal_metric_surfaces] Missing K/N meshes for mode {mode_id}")
            return

        K = data["K"]
        N = data["N"]

        # Per-metric stats
        summary_lines = [f"Mode {mode_id} - {metadata.get('deg_label', '')} (resolution={metadata.get('resolution')})", ""]

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

            z_label = format_label(selected_key)
            title = f"{z_label} Surface [{unit}] — {metadata.get('deg_label', f'Mode {mode_id}')}"

            # Choose output filename (top-down view or ortho)
            plot_name = f"{selected_key}_res{resolution}_top.svg" if view == "top" \
                        else f"{selected_key}_res{resolution}.svg"
            plot_path = mode_plot_dir / plot_name
            if not overwrite:
                plot_path = unique_path(plot_path)

            # Plot and save the surface
            save_parametric_3d(K, N, Z, title=title, z_label=z_label, z_unit=unit,
                               cmap=cmap, save_path=str(plot_path), show=False, view=view)

            # Simple stats for quick inspection
            z_flat = Z.astype(float).ravel()
            if np.isfinite(z_flat).any():
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

    # Write short summary file next to plots
    summary_path = mode_plot_dir / f"summary_res{resolution}.txt"
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    print(f"[save_multimodal_metric_surfaces] Wrote {summary_path}")


# ----- RUN -----
# run_baselines()
# run_mismatch_pyramid(degraded_sets=3, min_degraded_modules=1, max_degraded_modules=15, clamp_after_max=True)
# run_mismatch_parametric_2d(mismatch_vs="total") # Note: long run time (~3min)

# save_parametric_results(resolution=1, mode_id=1) # Data already stored - not necessary to run
# run_mismatch_parametric_3d(resolution=1, metric_key="metric_percent_mismatch_to_loss", deg_mode=1)
# run_mismatch_parametric_3d(resolution=1, metric_key="metric_mismatch_total", deg_mode=5)
# save_parametric_surfaces(resolution=1, view='ortho') # Plots already stored - not necessary to run
# save_parametric_surfaces(resolution=1, view='top') # Plots already stored - not necessary to run

# save_trend_surfaces(resolution=1, modes=range(1, 7), show=False) # Plots already stored - not necessary to run

# save_multimodal_results(resolution=1, levels=(1, 2, 3, 4, 5, 6), mode_id=999) # Data already stored - not necessary to run
# save_multimodal_surfaces(mode_id=999, resolution=1, view='ortho') # Plots already stored - not necessary to run
# save_multimodal_surfaces(mode_id=999, resolution=1, view='top') # Plots already stored - not necessary to run
