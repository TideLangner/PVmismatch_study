# Save I-V-P and Mismatch Calculator Metadata

import time
import numpy as np
from datetime import timedelta
from sys_healthy import create_healthy, plot_healthy
from sys_degraded_fully import create_degraded, plot_degraded, plot_deg_vs_healthy_mods, plot_degradation_modes
from sys_mismatched import create_mismatched, create_mismatched_parametric, print_system
from sys_mismatch_calculator import loss_calculator
from sys_plotter import plot_system_comparisons, plot_healthy_vs_mismatch, plot_mismatch_sweeps, plot_mismatch_3d
from pvmismatch.pvmismatch_lib import pvstring

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
# degradation_mode = 1
# ======================================= #

for iteration in range(1, 7):
    degradation_mode = iteration

    # Start simulation timer
    start = time.time()

    # GLOBAL VARIABLES
    # Healthy System
    healthy = create_healthy()
    mod_healthy = healthy["module_healthy"]
    Imod, Vmod, Pmod = healthy["Imod"], healthy["Vmod"], healthy["Pmod"]
    string_healthy = healthy["string_healthy"]
    Istr, Vstr, Pstr = healthy["Istr"], healthy["Vstr"], healthy["Pstr"]
    system_healthy = healthy["system_healthy"]
    Isys, Vsys, Psys = healthy["Isys"], healthy["Vsys"], healthy["Psys"]

    # Fully-Degraded System
    degraded = create_degraded(degradation_mode)
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
                "Isys_deg": degraded_i["Isys_deg"],
                "Vsys_deg": degraded_i["Vsys_deg"],
                "Psys_deg": degraded_i["Psys_deg"],
                "deg_label": degraded_i["deg_label"]
            })
        plot_degradation_modes(all_modes)

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


    def sweep(mismatch_vs="total"):
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


    def save_parametric(resolution=30, output="W"):
        """Run parametric study and plot 3D surfaces.
        - sets_strings == "sets": sweep K (degraded modules per string) and S (affected sets).
        - sets_strings == "strings": sweep K (degraded modules per string) and N (affected strings).
        """

        if output not in ("W", "%"):
            raise ValueError("Invalid output type. Must be 'W' or '%'.")
        if resolution not in (1, 5, 10, 30):
            raise ValueError("Invalid resolution value. Must be 1, 5, 10 or 30.")

        # K: degraded modules per (affected) string [0..30]
        k_grid_vals = np.arange(0, 31, 1)

        # N: number of affected (degraded) strings [0..150]
        str_grid_vals = np.arange(0, 151, resolution)
        K, N = np.meshgrid(k_grid_vals, str_grid_vals)

        # Compute Z surfaces:
        # - Z_W: total mismatch in Watts
        # - Z_pct: total mismatch in percent (relative to healthy)
        Z_W = np.zeros_like(K, dtype=float)
        Z_pct = np.zeros_like(K, dtype=float)

        # ===== Save I-V-P info =====

        # Allocate cubes for system curves: (rows N) x (cols K) x (num_points)
        num_rows, num_cols = N.shape
        num_points = len(system_healthy.Vsys)
        Vsys_cube = np.zeros((num_rows, num_cols, num_points), dtype=float)
        Isys_cube = np.zeros((num_rows, num_cols, num_points), dtype=float)
        Psys_cube = np.zeros((num_rows, num_cols, num_points), dtype=float)

        # Prepare containers for all loss_calculator metrics (2D arrays per metric)
        # Probe one run to discover keys and get healthy baselines
        _probe_sys = create_mismatched_parametric(min_degraded_modules=0, num_degraded_strings=0,
                                                  module_healthy=mod_healthy, module_degraded=mod_deg)
        _probe_rep = loss_calculator(_probe_sys, system_healthy)
        metric_keys = list(_probe_rep.keys())
        metric_surfaces = {k: np.zeros((num_rows, num_cols), dtype=float) for k in metric_keys}

        # Healthy baselines from probe (constants)
        Pmods_healthy = float(_probe_rep["module_MPPs_sum_healthy"])
        Pstrs_healthy = float(_probe_rep["string_MPPs_sum_healthy"])
        Psys_healthy = float(_probe_rep["system_MPP_healthy"])

        # --------- FAST PATH: precompute string prototypes for k=0..30 ----------
        # For each k, build a PVstring once, record its I,V,P, its string MPP, and the sum of module MPPs in that string.
        proto = {}
        for k_local in range(0, 31):
            mods = [mod_deg] * k_local + [mod_healthy] * (30 - k_local)
            s = pvstring.PVstring(pvmods=mods)
            Istr_k, Vstr_k, Pstr_k = s.Istring, s.Vstring, s.Pstring
            # string MPP
            idx_s = int(np.argmax(Pstr_k))
            Pmp_str_k = float(Pstr_k[idx_s])
            # sum of module MPPs in this string
            sum_mods_mpp_k = 0.0
            for m in s.pvmods:
                idx_m = int(np.argmax(m.Pmod))
                sum_mods_mpp_k += float(m.Pmod[idx_m])
            proto[k_local] = {
                "V": Vstr_k, "I": Istr_k, "P": Pstr_k,
                "Pmp_str": Pmp_str_k,
                "sum_mods_mpp": sum_mods_mpp_k
            }

        # Ensure all prototypes share the same V grid; if not, we can interpolate.
        V_ref = proto[0]["V"]
        for k_local in range(1, 31):
            if len(proto[k_local]["V"]) != len(V_ref) or not np.allclose(proto[k_local]["V"], V_ref, rtol=1e-10,
                                                                         atol=1e-10):
                # Interpolate I onto reference voltage grid (rare, but safe)
                proto[k_local]["I"] = np.interp(V_ref, proto[k_local]["V"], proto[k_local]["I"])
                proto[k_local]["P"] = V_ref * proto[k_local]["I"]
                proto[k_local]["V"] = V_ref

        # ----------------- Fill cubes/surfaces without building systems -----------------
        total_strings = 150
        for i in range(N.shape[0]):  # over affected strings
            n = int(N[i, 0])
            for j in range(K.shape[1]):  # over degraded modules per string
                k = int(K[i, j])

                Ik = proto[k]["I"]
                I0 = proto[0]["I"]
                V = V_ref

                # System curve from parallel sum of strings
                Isys_ij = n * Ik + (total_strings - n) * I0
                Vsys_ij = V
                Psys_ij = Vsys_ij * Isys_ij

                # System MPP
                idx_sys = int(np.argmax(Psys_ij))
                Psys_actual = float(Psys_ij[idx_sys])

                # Module and string sums (linear combinations)
                Pmods_actual = n * proto[k]["sum_mods_mpp"] + (total_strings - n) * proto[0]["sum_mods_mpp"]
                Pstrs_actual = n * proto[k]["Pmp_str"] + (total_strings - n) * proto[0]["Pmp_str"]

                # Mismatch components
                mismatch_mods_to_strs = Pmods_actual - Pstrs_actual
                mismatch_strs_to_sys = Pstrs_actual - Psys_actual
                mismatch_total = mismatch_mods_to_strs + mismatch_strs_to_sys

                # Losses vs healthy
                loss_mods = Pmods_healthy - Pmods_actual
                loss_strs = Pstrs_healthy - Pstrs_actual
                loss_sys = Psys_healthy - Psys_actual

                # Percentages (mirror loss_calculator logic; default normalisation uses 150)
                num_strs_affected = 150
                percent_loss = percent_mismatch_total = percent_degradation = 0.0
                percent_mismatch_to_loss = percent_degradation_to_loss = 0.0
                percent_mismatch_strs_to_sys = percent_mismatch_mods_to_strs = 0.0
                percent_mismatch_strs_norm = percent_mismatch_strs_norm_vs_loss = 0.0
                if loss_sys != 0 and Psys_healthy != 0:
                    loss_degradation = (loss_sys - mismatch_total)
                    percent_loss = 100.0 * (1 - Psys_actual / Psys_healthy)
                    percent_mismatch_total = 100.0 * mismatch_total / Psys_healthy
                    percent_degradation = 100.0 * loss_degradation / Psys_healthy
                    percent_mismatch_to_loss = 100.0 * mismatch_total / loss_sys
                    percent_degradation_to_loss = 100.0 * loss_degradation / loss_sys
                    percent_mismatch_strs_to_sys = 100.0 * mismatch_strs_to_sys / Psys_healthy
                    percent_mismatch_mods_to_strs = 100.0 * mismatch_mods_to_strs / Psys_healthy
                    # normalised per-string basis (using healthy strings sum / 150)
                    denom_strs = (Pstrs_healthy / num_strs_affected)
                    denom_loss_strs = (loss_strs / num_strs_affected) if num_strs_affected != 0 else 0.0
                    if denom_strs != 0:
                        percent_mismatch_strs_norm = 100.0 * mismatch_mods_to_strs / denom_strs
                    if denom_loss_strs != 0:
                        percent_mismatch_strs_norm_vs_loss = 100.0 * (mismatch_mods_to_strs / denom_loss_strs)
                    # expose loss_degradation for storing below
                else:
                    loss_degradation = (loss_sys - mismatch_total)

                # Save basic surfaces for plotting
                Z_W[i, j] = mismatch_total
                Z_pct[i, j] = percent_mismatch_total

                # Save system curves
                Vsys_cube[i, j, :] = Vsys_ij
                Isys_cube[i, j, :] = Isys_ij
                Psys_cube[i, j, :] = Psys_ij

                # Save all metrics to match loss_calculator keys
                metric_surfaces["module_MPPs_sum_degraded"][i, j] = Pmods_actual
                metric_surfaces["module_MPPs_sum_healthy"][i, j] = Pmods_healthy
                metric_surfaces["string_MPPs_sum_degraded"][i, j] = Pstrs_actual
                metric_surfaces["string_MPPs_sum_healthy"][i, j] = Pstrs_healthy
                metric_surfaces["system_MPP_degraded"][i, j] = Psys_actual
                metric_surfaces["system_MPP_healthy"][i, j] = Psys_healthy
                metric_surfaces["total_module_loss"][i, j] = loss_mods
                metric_surfaces["total_string_loss"][i, j] = loss_strs
                metric_surfaces["total_system_loss"][i, j] = loss_sys
                metric_surfaces["mismatch_modules_to_strings"][i, j] = mismatch_mods_to_strs
                metric_surfaces["mismatch_strings_to_system"][i, j] = mismatch_strs_to_sys
                metric_surfaces["mismatch_total"][i, j] = mismatch_total
                metric_surfaces["degradation_only"][i, j] = loss_degradation
                metric_surfaces["percent_loss"][i, j] = percent_loss
                metric_surfaces["percent_degradation_to_loss"][i, j] = percent_degradation_to_loss
                metric_surfaces["percent_mismatch_to_loss"][i, j] = percent_mismatch_to_loss
                metric_surfaces["percent_degradation"][i, j] = percent_degradation
                metric_surfaces["percent_mismatch_total"][i, j] = percent_mismatch_total
                metric_surfaces["percent_mismatch_strs_to_sys"][i, j] = percent_mismatch_strs_to_sys
                metric_surfaces["percent_mismatch_mods_to_strs"][i, j] = percent_mismatch_mods_to_strs
                metric_surfaces["percent_mismatch_strs_norm"][i, j] = percent_mismatch_strs_norm
                metric_surfaces["percent_mismatch_strs_norm_vs_loss"][i, j] = percent_mismatch_strs_norm_vs_loss

        # show time to simulate
        end = time.time()
        elapsed = end - start
        print(f"\nTotal time: {timedelta(seconds=elapsed)}")

        # Plot 3D surfaces
        if output == "W":
            plot_mismatch_3d(K, N, Z_W, z_mode="W", title="Total Mismatch Surface [W]", mode=degradation_mode)
        else:
            plot_mismatch_3d(K, N, Z_pct, z_mode="%", title="Total Mismatch Surface [%]", mode=degradation_mode)

        # ===== SAVE ALL DATA FOR THIS MODE =====
        from pathlib import Path
        import json

        out_dir = Path("results") / f"mode_{degradation_mode}"
        out_dir.mkdir(parents=True, exist_ok=True)
        npz_path = out_dir / f"surface_res{resolution}.npz"
        meta_path = out_dir / f"surface_res{resolution}.metadata.json"

        savez_payload = {
            "K": K.astype(np.int16),
            "N": N.astype(np.int16),
            "Vsys_cube": Vsys_cube.astype(np.float32),
            "Isys_cube": Isys_cube.astype(np.float32),
            "Psys_cube": Psys_cube.astype(np.float32),
            "mismatch_total_W": Z_W.astype(np.float32),
            "percent_mismatch_total": Z_pct.astype(np.float32),
        }
        for kname, arr in metric_surfaces.items():
            savez_payload[f"metric_{kname}"] = arr.astype(np.float32)

        np.savez_compressed(npz_path, **savez_payload)

        metadata = {
            "degradation_mode": degradation_mode,
            "deg_label": deg_label,
            "resolution": resolution,
            "num_rows": int(num_rows),
            "num_cols": int(num_cols),
            "num_points": int(num_points),
            "arrays": sorted(list(savez_payload.keys())),
            "units": {
                "Vsys_cube": "V",
                "Isys_cube": "A",
                "Psys_cube": "W",
                "mismatch_total_W": "W",
                "percent_mismatch_total": "%",
            },
            "notes": "All arrays are float32 except K/N (int16). Shapes: curves (N x K x num_points), metrics (N x K).",
        }
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)


    # ----- RUN -----
    # run_baselines()
    # run_mismatched_system(degraded_sets=3, min_degraded_modules=1, max_degraded_modules=15, clamp_after_max=True)
    # sweep(mismatch_vs="total")
    save_parametric(resolution=1, output="%")
    # plot_3d(resolution=1, output="W")

