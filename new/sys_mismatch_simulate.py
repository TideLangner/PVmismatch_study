# Simulate all systems
from os import system

import time
import numpy as np
from datetime import timedelta
from sys_healthy import create_healthy, plot_healthy
from sys_degraded_fully import create_degraded, plot_degraded, plot_deg_vs_healthy_mods, plot_degradation_modes
from sys_mismatched import create_mismatched, create_mismatched_parametric, print_system
from sys_mismatch_calculator import loss_calculator
from sys_mismatch_plotter import plot_system_comparisons, plot_healthy_vs_mismatch, plot_mismatch_sweeps, plot_mismatch_3d

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

    start = time.time()

    degradation_mode = iteration
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


    def plot_3d(resolution=10, output="W"):
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

        for i in range(N.shape[0]):      # over affected strings
            for j in range(K.shape[1]):  # over degraded modules per string
                n = int(N[i, j])
                k = int(K[i, j])
                sys_ij = create_mismatched_parametric(min_degraded_modules=k, num_degraded_strings=n,
                                                      module_healthy=mod_healthy, module_degraded=mod_deg)
                rep_ij = loss_calculator(sys_ij, system_healthy)
                Z_W[i, j] = float(rep_ij["mismatch_total"])
                Z_pct[i, j] = float(rep_ij["percent_mismatch_total"])

        # show time to simulate
        end = time.time()
        elapsed = end - start
        print(f"\nTotal time: {timedelta(seconds=elapsed)}")

        # Plot 3D surfaces
        if output == "W":
            plot_mismatch_3d(K, N, Z_W, z_mode="W", title="Total Mismatch Surface [W]", mode=iteration)
        else:
            plot_mismatch_3d(K, N, Z_pct, z_mode="%", title="Total Mismatch Surface [%]", mode=iteration)


    # ----- RUN -----
    # run_baselines()
    # run_mismatched_system(degraded_sets=3, min_degraded_modules=1, max_degraded_modules=15, clamp_after_max=True)
    # sweep(mismatch_vs="loss")
    plot_3d(resolution=30, output="%")
    plot_3d(resolution=30, output="W")

