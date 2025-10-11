# Tide Langner
# 9 September 2025
# Parametric study of system losses as a function of the number of degraded strings

import numpy as np
import matplotlib.pyplot as plt
from pvmismatch import pvsystem
from mismatch_report import mismatch_report  # import your existing mismatch_report

def run_parametric_study(n_strings,
                         m_modules_per_string,
                         degrade_values,
                         create_degraded_system,
                         healthy_template):
    """
    Run a parametric study varying degradation severity (Rsh etc.)
    and number of degraded strings.
    Returns a list of dicts: [{'Rsh':..., 'n_degraded':..., 'report':...}, ...]
    """
    results = []

    for val in degrade_values:
        for n_degraded in range(0, n_strings + 1):

            try:
                # build mixed system
                if n_degraded == 0:
                    mixed_sys = healthy_template   # baseline system
                else:
                    degraded_sys = create_degraded_system(
                        num_strings=n_degraded,
                        num_modules=m_modules_per_string,
                        Rsh=val)

                    healthy_strings = healthy_template.pvstrs[:(n_strings - n_degraded)]
                    mixed_sys = pvsystem.PVsystem(
                        pvstrs=degraded_sys.pvstrs + healthy_strings)

                # (3) skip invalid IV curves
                if (np.any(np.isnan(mixed_sys.Iarray)) or
                    np.any(np.isnan(mixed_sys.Parray))):
                    print(f"Skipping invalid scenario: Rsh={val}, n_degraded={n_degraded}")
                    continue

                # compute mismatch report
                rep = mismatch_report(mixed_sys, pvsys_healthy=healthy_template)

                results.append({
                    "Rsh": val,
                    "n_degraded": n_degraded,
                    "report": rep
                })

            except Exception as e:
                print(f"Error building scenario Rsh={val}, n_degraded={n_degraded}: {e}")
                continue

    return results


def plot_parametric_results(results, x_axis='Rsh', y_metric='loss_total'):
    """
    Plot parametric study results.

    Parameters
    ----------
    results : list of dicts from run_parametric_study()
    x_axis : str
        Which key to use on x-axis: 'Rsh' or 'n_degraded'
    y_metric : str
        Which mismatch_report metric to plot, e.g. 'loss_total', 'percent_mismatch'
    """
    # Convert list of dicts to arrays for plotting
    x_vals = [r[x_axis] for r in results]
    y_vals = [r["report"][y_metric] for r in results]

    plt.figure(figsize=(8, 5))
    plt.scatter(x_vals, y_vals, c='dodgerblue')
    plt.xlabel(x_axis)
    plt.ylabel(y_metric)
    plt.title(f"{y_metric} vs {x_axis}")
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.show()