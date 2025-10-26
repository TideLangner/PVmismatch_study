# Tide Langner
# Parametric surface results saver

from __future__ import annotations

import time
from datetime import timedelta
from pathlib import Path
import json
import numpy as np

from pvmismatch.pvmismatch_lib import pvstring
from sys_mismatched import create_mismatched_parametric, create_mismatched_multimodal
from sys_mismatch_calculator import loss_calculator


def save_parametric_discrete_modal(*, resolution: int = 30, degradation_mode: int, deg_label: str,
                                   system_healthy, mod_healthy, mod_deg):
    """Compute and save parametric mismatch data for later plotting.

    Parameters:
      resolution: 1, 5, 10, or 30 (step for affected strings axis)
      degradation_mode: scenario identifier used for output folder naming
      deg_label: formatted label stored in metadata
      system_healthy: pre-built healthy system object (from sys_simulate)
      mod_healthy: healthy module object
      mod_deg: degraded module object for this degradation_mode

    Saves:
      results/mode_{degradation_mode}/surface_res{resolution}.npz
      results/mode_{degradation_mode}/surface_res{resolution}.metadata.json
    """

    if resolution not in (1, 5, 10, 30):
        raise ValueError("Invalid resolution value. Must be 1, 5, 10 or 30.")

    start = time.time()

    # Grid setup
    k_grid_vals = np.arange(0, 31, 1)              # degraded modules per affected string
    str_grid_vals = np.arange(0, 151, resolution)  # number of affected strings
    K, N = np.meshgrid(k_grid_vals, str_grid_vals)

    # Allocate result arrays
    Z_W = np.zeros_like(K, dtype=float)
    Z_pct = np.zeros_like(K, dtype=float)

    # Cubes for system I-V-P curves
    num_rows, num_cols = N.shape
    num_points = len(system_healthy.Vsys)
    Vsys_cube = np.zeros((num_rows, num_cols, num_points), dtype=float)
    Isys_cube = np.zeros((num_rows, num_cols, num_points), dtype=float)
    Psys_cube = np.zeros((num_rows, num_cols, num_points), dtype=float)

    # Discover metrics and establish healthy baselines
    _probe_sys = create_mismatched_parametric(min_degraded_modules=0, num_degraded_strings=0,
                                              module_healthy=mod_healthy, module_degraded=mod_deg)
    _probe_rep = loss_calculator(_probe_sys, system_healthy)
    metric_keys = list(_probe_rep.keys())
    metric_surfaces = {k: np.zeros((num_rows, num_cols), dtype=float) for k in metric_keys}

    Pmods_healthy = float(_probe_rep["module_MPPs_sum_healthy"])
    Pstrs_healthy = float(_probe_rep["string_MPPs_sum_healthy"])
    Psys_healthy = float(_probe_rep["system_MPP_healthy"])

    # Precompute string prototypes for k = 0..30
    proto = {}
    for k_local in range(0, 31):
        mods = [mod_deg] * k_local + [mod_healthy] * (30 - k_local)
        s = pvstring.PVstring(pvmods=mods)
        Istr_k, Vstr_k, Pstr_k = s.Istring, s.Vstring, s.Pstring
        idx_s = int(np.argmax(Pstr_k))
        Pmp_str_k = float(Pstr_k[idx_s])
        sum_mods_mpp_k = 0.0
        for m in s.pvmods:
            idx_m = int(np.argmax(m.Pmod))
            sum_mods_mpp_k += float(m.Pmod[idx_m])
        proto[k_local] = {"V": Vstr_k, "I": Istr_k, "P": Pstr_k,
                          "Pmp_str": Pmp_str_k, "sum_mods_mpp": sum_mods_mpp_k}

    # Ensure common voltage grid
    V_ref = proto[0]["V"]
    for k_local in range(1, 31):
        if len(proto[k_local]["V"]) != len(V_ref) or not np.allclose(proto[k_local]["V"], V_ref, rtol=1e-10, atol=1e-10):
            proto[k_local]["I"] = np.interp(V_ref, proto[k_local]["V"], proto[k_local]["I"])
            proto[k_local]["P"] = V_ref * proto[k_local]["I"]
            proto[k_local]["V"] = V_ref

    # Build cubes/surfaces analytically (no full system construction)
    total_strings = 150
    for i in range(N.shape[0]):  # over affected strings
        n = int(N[i, 0])
        for j in range(K.shape[1]):  # over degraded modules per string
            k = int(K[i, j])

            Ik = proto[k]["I"]
            I0 = proto[0]["I"]
            V = V_ref

            Isys_ij = n * Ik + (total_strings - n) * I0
            Vsys_ij = V
            Psys_ij = Vsys_ij * Isys_ij

            idx_sys = int(np.argmax(Psys_ij))
            Psys_actual = float(Psys_ij[idx_sys])

            Pmods_actual = n * proto[k]["sum_mods_mpp"] + (total_strings - n) * proto[0]["sum_mods_mpp"]
            Pstrs_actual = n * proto[k]["Pmp_str"] + (total_strings - n) * proto[0]["Pmp_str"]

            mismatch_mods_to_strs = Pmods_actual - Pstrs_actual
            mismatch_strs_to_sys = Pstrs_actual - Psys_actual
            mismatch_total = mismatch_mods_to_strs + mismatch_strs_to_sys

            loss_mods = Pmods_healthy - Pmods_actual
            loss_strs = Pstrs_healthy - Pstrs_actual
            loss_sys = Psys_healthy - Psys_actual

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
                denom_strs = (Pstrs_healthy / num_strs_affected)
                denom_loss_strs = (loss_strs / num_strs_affected) if num_strs_affected != 0 else 0.0
                if denom_strs != 0:
                    percent_mismatch_strs_norm = 100.0 * mismatch_mods_to_strs / denom_strs
                if denom_loss_strs != 0:
                    percent_mismatch_strs_norm_vs_loss = 100.0 * (mismatch_mods_to_strs / denom_loss_strs)
            else:
                loss_degradation = (loss_sys - mismatch_total)

            Z_W[i, j] = mismatch_total
            Z_pct[i, j] = percent_mismatch_total

            Vsys_cube[i, j, :] = Vsys_ij
            Isys_cube[i, j, :] = Isys_ij
            Psys_cube[i, j, :] = Psys_ij

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

    elapsed = time.time() - start
    print(f"\nParametric generation time: {timedelta(seconds=elapsed)}")

    # Save artifacts for this degradation mode
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


def save_parametric_multi_modal(*, resolution: int = 30, degradation_mode: int, deg_label: str,
                                system_healthy, mod_healthy, modules_degraded_levels):
    """
    Compute and save parametric mismatch data for the multimodal equal-spread pattern.

    Pattern (must match the system builder):
      - Within a string: first K modules degraded, cycling 1..L (wrap).
      - Across strings: per-string starting level offset advances by +1 per string (r = s_idx % L).
    """
    if resolution not in (1, 5, 10, 30):
        raise ValueError("Invalid resolution value. Must be 1, 5, 10 or 30.")
    if not modules_degraded_levels:
        raise ValueError("modules_degraded_levels must be a non-empty sequence of degraded PVmodule variants.")

    start = time.time()

    # Grid
    k_grid_vals = np.arange(0, 31, 1)              # degraded modules per affected string
    str_grid_vals = np.arange(0, 151, resolution)  # number of affected strings
    K, N = np.meshgrid(k_grid_vals, str_grid_vals)

    num_rows, num_cols = N.shape

    # Allocate arrays
    Z_W = np.zeros_like(K, dtype=float)
    Z_pct = np.zeros_like(K, dtype=float)

    # Discover metric keys by probing one configuration (schema compatibility)
    from sys_mismatched import create_mismatched_parametric as _probe_param
    probe_sys = _probe_param(min_degraded_modules=0, num_degraded_strings=0,
                             module_healthy=mod_healthy, module_degraded=modules_degraded_levels[0])
    probe_rep = loss_calculator(probe_sys, system_healthy)
    metric_surfaces = {k: np.zeros((num_rows, num_cols), dtype=float) for k in probe_rep.keys()}

    # System curve length
    num_points = len(system_healthy.Vsys)
    Vsys_cube = np.zeros((num_rows, num_cols, num_points), dtype=float)
    Isys_cube = np.zeros((num_rows, num_cols, num_points), dtype=float)
    Psys_cube = np.zeros((num_rows, num_cols, num_points), dtype=float)

    # -- Precompute single-string prototypes for k=0..30 and offsets r=0..L-1 --
    total_strings = 150
    mods_per_string = 30
    levels = modules_degraded_levels
    L = len(levels)

    def build_string_for(k_local: int, r_offset: int) -> pvstring.PVstring:
        # Match builder: first K degraded with cycling from r_offset; rest healthy
        pvmods = []
        for idx in range(k_local):
            lvl_idx = (r_offset + idx) % L
            pvmods.append(levels[lvl_idx])
        pvmods.extend([mod_healthy] * (mods_per_string - k_local))
        return pvstring.PVstring(pvmods=pvmods)

    # Healthy prototype (k=0)
    s0 = build_string_for(0, 0)
    V_ref = s0.Vstring
    I0 = s0.Istring
    P0 = s0.Pstring
    Pmp_str_0 = float(P0[int(np.argmax(P0))])
    sum_mods_mpp_0 = 0.0
    for m in s0.pvmods:
        pm = m.Pmod
        sum_mods_mpp_0 += float(pm[int(np.argmax(pm))])

    # Cache (k,r) on V_ref: string I/P curves and aggregates
    proto_str = {}
    for k_local in range(0, 31):
        for r in range(L if k_local > 0 else 1):  # for k=0, only r=0 needed
            s = build_string_for(k_local, r)
            V = s.Vstring
            I = s.Istring
            P = s.Pstring
            if len(V) != len(V_ref) or not np.allclose(V, V_ref, rtol=1e-10, atol=1e-10):
                I = np.interp(V_ref, V, I)
                P = V_ref * I
            idx_s = int(np.argmax(P))
            Pmp_str = float(P[idx_s])
            sum_mods_mpp = 0.0
            for m in s.pvmods:
                pm = m.Pmod
                sum_mods_mpp += float(pm[int(np.argmax(pm))])
            proto_str[(k_local, r)] = {"I": I, "P": P, "Pmp_str": Pmp_str, "sum_mods_mpp": sum_mods_mpp}

    # Count per-offset strings among the first n strings (r advances +1 each string)
    def offset_counts(n: int, L: int) -> np.ndarray:
        q, rem = divmod(n, L)
        c = np.full(L, q, dtype=int)
        if rem > 0:
            c[:rem] += 1
        return c

    # Healthy baselines
    Pmods_healthy = float(probe_rep["module_MPPs_sum_healthy"])
    Pstrs_healthy = float(probe_rep["string_MPPs_sum_healthy"])
    Psys_healthy = float(probe_rep["system_MPP_healthy"])

    # -- Aggregate across grid without constructing full systems --
    for i in range(num_rows):             # over affected strings
        n = int(N[i, 0])
        off_counts = offset_counts(n, L)
        for j in range(num_cols):         # over degraded modules per string
            k = int(K[i, j])

            Isys = np.zeros_like(V_ref, dtype=float)

            if k == 0:
                Isys = total_strings * I0
                Pmods_actual = total_strings * sum_mods_mpp_0
                Pstrs_actual = total_strings * Pmp_str_0
            else:
                Pmods_actual = 0.0
                Pstrs_actual = 0.0
                # Affected strings distributed by offsets r=0..L-1 (r = s_idx % L)
                for r, cnt in enumerate(off_counts):
                    if cnt == 0:
                        continue
                    ps = proto_str[(k, r)]
                    Isys += cnt * ps["I"]
                    Pmods_actual += cnt * ps["sum_mods_mpp"]
                    Pstrs_actual += cnt * ps["Pmp_str"]
                # Healthy strings
                healthy_cnt = total_strings - n
                if healthy_cnt > 0:
                    Isys += healthy_cnt * I0
                    Pmods_actual += healthy_cnt * sum_mods_mpp_0
                    Pstrs_actual += healthy_cnt * Pmp_str_0

            V = V_ref
            P = V * Isys

            idx_sys = int(np.argmax(P))
            Psys_actual = float(P[idx_sys])

            # Mismatch metrics:
            mismatch_mods_to_strs = Pmods_actual - Pstrs_actual
            mismatch_strs_to_sys = Pstrs_actual - Psys_actual
            mismatch_total = mismatch_mods_to_strs + mismatch_strs_to_sys

            loss_mods = Pmods_healthy - Pmods_actual
            loss_strs = Pstrs_healthy - Pstrs_actual
            loss_sys = Psys_healthy - Psys_actual
            loss_degradation = (loss_sys - mismatch_total)

            percent_loss = percent_mismatch_total = percent_degradation = 0.0
            percent_mismatch_to_loss = percent_degradation_to_loss = 0.0
            percent_mismatch_strs_to_sys = percent_mismatch_mods_to_strs = 0.0
            percent_mismatch_strs_norm = percent_mismatch_strs_norm_vs_loss = 0.0
            if Psys_healthy != 0:
                percent_loss = 100.0 * (1 - Psys_actual / Psys_healthy)
                percent_mismatch_total = 100.0 * mismatch_total / Psys_healthy
                percent_degradation = 100.0 * loss_degradation / Psys_healthy
                percent_mismatch_strs_to_sys = 100.0 * mismatch_strs_to_sys / Psys_healthy
                percent_mismatch_mods_to_strs = 100.0 * mismatch_mods_to_strs / Psys_healthy
            if loss_sys != 0:
                percent_mismatch_to_loss = 100.0 * mismatch_total / loss_sys
                percent_degradation_to_loss = 100.0 * loss_degradation / loss_sys

            # String-normalised percents (use healthy strings baseline per 150 strings)
            num_strs_affected_norm = 150
            denom_strs = (Pstrs_healthy / num_strs_affected_norm)
            denom_loss_strs = (loss_strs / num_strs_affected_norm) if num_strs_affected_norm != 0 else 0.0
            if denom_strs != 0:
                percent_mismatch_strs_norm = 100.0 * mismatch_mods_to_strs / denom_strs
            if denom_loss_strs != 0:
                percent_mismatch_strs_norm_vs_loss = 100.0 * (mismatch_mods_to_strs / denom_loss_strs)

            Z_W[i, j] = mismatch_total
            Z_pct[i, j] = percent_mismatch_total

            Vsys_cube[i, j, :] = V
            Isys_cube[i, j, :] = Isys
            Psys_cube[i, j, :] = P

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

    elapsed = time.time() - start
    print(f"\n[save_parametric_multimodal_equal_spread] Generation time: {timedelta(seconds=elapsed)}")

    # Save artifacts
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
        "notes": (
            f"Multimodal equal-spread with L={len(modules_degraded_levels)} degraded levels. "
            "Pattern: within-string cycles 1..L; across strings offset +1 per row. "
            "Arrays are float32 except K/N (int16). Shapes: curves (N x K x num_points), metrics (N x K)."
        ),
    }
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

