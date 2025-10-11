# Calculate mismatch components

import numpy as np
# from sys_mismatched import *

def mpp_from_curve(I, V, P):
    """Return (Pmp, Imp, Vmp) from sampled I-V-P arrays"""
    k = np.argmax(P)
    return float(P[k]), float(I[k]), float(V[k])

# --- Cached MPP helpers (avoid recomputing argmax on immutable curves) ---
def _mpp_cached(obj, I_attr: str, V_attr: str, P_attr: str, cache_attr: str):
    """
    Compute and cache MPP on 'obj' the first time; reuse afterwards.
    Assumes the curve arrays are immutable for the lifetime of 'obj'.
    """
    if hasattr(obj, cache_attr):
        return getattr(obj, cache_attr)

    I = getattr(obj, I_attr)
    V = getattr(obj, V_attr)
    P = getattr(obj, P_attr)
    Pmp, Imp, Vmp = mpp_from_curve(I, V, P)
    setattr(obj, cache_attr, Pmp)  # cache only what we need for sums
    return Pmp

def sum_module_mpps(pvsys):
    total = 0.0
    for s in pvsys.pvstrs:
        for m in s.pvmods:
            # Cache per-module MPP as _Pmp_mod
            Pmp = _mpp_cached(m, "Imod", "Vmod", "Pmod", "_Pmp_mod")
            total += Pmp
    return total

def sum_string_mpps(pvsys):
    total = 0.0
    for s in pvsys.pvstrs:
        # Cache per-string MPP as _Pmp_str
        Pmp = _mpp_cached(s, "Istring", "Vstring", "Pstring", "_Pmp_str")
        total += Pmp
    return total

def system_mpp(pvsys):
    # Cache system MPP as _Pmp_sys
    return _mpp_cached(pvsys, "Isys", "Vsys", "Psys", "_Pmp_sys")


def loss_calculator(pvsys, pvsys_healthy=None, num_strs_affected=150):
    """
    Calculates:
      - total losses (vs healthy)
      - degradation-only losses
      - mismatch losses (modules->strings, strings->system, total mismatch)
      - module/string/system outputs (degraded and healthy)
    """

    # Healthy system
    Pmods_healthy = None
    Pstrs_healthy = None
    Psys_healthy = None
    if pvsys_healthy is not None:
        # Cache healthy sums at the system level to reuse across many calls
        if hasattr(pvsys_healthy, "_sum_Pmods_mpp"):
            Pmods_healthy = pvsys_healthy._sum_Pmods_mpp
        else:
            Pmods_healthy = sum_module_mpps(pvsys_healthy)
            setattr(pvsys_healthy, "_sum_Pmods_mpp", Pmods_healthy)

        if hasattr(pvsys_healthy, "_sum_Pstrs_mpp"):
            Pstrs_healthy = pvsys_healthy._sum_Pstrs_mpp
        else:
            Pstrs_healthy = sum_string_mpps(pvsys_healthy)
            setattr(pvsys_healthy, "_sum_Pstrs_mpp", Pstrs_healthy)

        if hasattr(pvsys_healthy, "_Pmp_sys"):
            Psys_healthy = pvsys_healthy._Pmp_sys
        else:
            Psys_healthy = system_mpp(pvsys_healthy)
            # system_mpp will cache as _Pmp_sys

    # Mismatched system
    Pmods_actual = sum_module_mpps(pvsys)
    Pstrs_actual = sum_string_mpps(pvsys)
    Psys_actual = system_mpp(pvsys)

    # Mismatch losses for mismatched system
    mismatch_mods_to_strs = Pmods_actual - Pstrs_actual
    mismatch_strs_to_sys = Pstrs_actual - Psys_actual
    mismatch_total = mismatch_mods_to_strs + mismatch_strs_to_sys

    # Losses healthy vs mismatched systems
    loss_mods, loss_strs, loss_sys = 0.0, 0.0, 0.0
    loss_degradation = 0.0
    percent_loss, percent_mismatch_to_loss, percent_degradation_to_loss = 0.0, 0.0, 0.0
    percent_mismatch_total, percent_mismatch_strs_to_sys, percent_mismatch_mods_to_strs = 0.0, 0.0, 0.0
    percent_mismatch_strs_norm, percent_mismatch_strs_norm_vs_loss = 0.0, 0.0
    percent_degradation = 0.0
    if pvsys_healthy is not None:
        # (degradation + mismatch) losses
        loss_mods = Pmods_healthy - Pmods_actual
        loss_strs = Pstrs_healthy - Pstrs_actual
        loss_sys = Psys_healthy - Psys_actual

        if loss_sys != 0:
            # (degradation-only) loss (constant for all levels)
            loss_degradation = (loss_sys - mismatch_total)

            # percentages
            percent_loss = 100.0 * (1 - Psys_actual / Psys_healthy)
            percent_mismatch_total = 100.0 * mismatch_total / Psys_healthy
            percent_degradation = 100.0 * loss_degradation / Psys_healthy
            #      #
            percent_mismatch_to_loss = 100.0 * mismatch_total / loss_sys
            percent_degradation_to_loss = 100.0 * loss_degradation / loss_sys
            #      #
            percent_mismatch_strs_to_sys = 100.0 * mismatch_strs_to_sys / Psys_healthy
            percent_mismatch_mods_to_strs = 100.0 * mismatch_mods_to_strs / Psys_healthy
            # normalise mod->str mismatch loss
            percent_mismatch_strs_norm = 100.0 * mismatch_mods_to_strs / (Pstrs_healthy/num_strs_affected)
            percent_mismatch_strs_norm_vs_loss = 100.0 * (mismatch_mods_to_strs / (loss_strs/num_strs_affected))

    return {
        # Outputs
        "module_MPPs_sum_degraded": Pmods_actual,
        "module_MPPs_sum_healthy": Pmods_healthy,
        "string_MPPs_sum_degraded": Pstrs_actual,
        "string_MPPs_sum_healthy": Pstrs_healthy,
        "system_MPP_degraded": Psys_actual,
        "system_MPP_healthy": Psys_healthy,
        # Total losses
        "total_module_loss": loss_mods,
        "total_string_loss": loss_strs,
        "total_system_loss": loss_sys,
        # Mismatch components
        "mismatch_modules_to_strings": mismatch_mods_to_strs,
        "mismatch_strings_to_system": mismatch_strs_to_sys,
        "mismatch_total": mismatch_total,
        # Degradation-only loss
        "degradation_only": loss_degradation,
        # Percentages:
        "percent_loss": percent_loss,
        "percent_degradation_to_loss": percent_degradation_to_loss,
        "percent_mismatch_to_loss": percent_mismatch_to_loss,
        "percent_degradation": percent_degradation,
        "percent_mismatch_total": percent_mismatch_total,
        "percent_mismatch_strs_to_sys": percent_mismatch_strs_to_sys,
        "percent_mismatch_mods_to_strs": percent_mismatch_mods_to_strs,
        "percent_mismatch_strs_norm": percent_mismatch_strs_norm,
        "percent_mismatch_strs_norm_vs_loss": percent_mismatch_strs_norm_vs_loss,
    }

