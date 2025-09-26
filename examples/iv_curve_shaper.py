import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import newton
import ipywidgets as widgets
from ipywidgets import interact

# ---- Constants ----
I_d1_sat_T0 = 2.286188161253440e-11
I_d2_sat_T0 = 1.117455042372326e-10
I_sc0_T0 = 6.3056
T_cell = 298.15
a_RBD = 1.036748445065697e-4
b_RBD = 0.
n_RBD = 3.284628553041425
E_g = 1.1
alpha_I_sc = 0.0003551
k = 1.380649e-23
q = 1.602176634e-19
T_0 = 289.15

# ---- Derived quantities independent of R_s, R_sh, E_e ----
T_star = (T_cell / T_0) ** 3
delta_inv_T = 1 / T_0 - 1 / T_cell

I_d1_sat = I_d1_sat_T0 * T_star * np.exp(E_g * q / k * delta_inv_T)
I_d2_sat = I_d2_sat_T0 * T_star * np.exp(E_g * q / (2 * k) * delta_inv_T)
V_t = k * T_cell / q


def make_IV_curve(R_s=0.0043, R_sh=10.0, E_e=1.0):
    """Compute IV curve for given R_s, R_sh, E_e."""

    # Short-circuit current at this irradiance
    I_sc0 = I_sc0_T0 * (1 + alpha_I_sc * (T_cell - T_0))
    I_sc = E_e * I_sc0

    # Short-circuit condition to compute A_ph
    V_d_sc = I_sc * R_s
    I_d1_sc = I_d1_sat * (np.exp(V_d_sc / V_t) - 1)
    I_d2_sc = I_d2_sat * (np.exp(V_d_sc / (2 * V_t)) - 1)
    I_sh_sc = V_d_sc / R_sh
    A_ph = 1 + (I_d1_sc + I_d2_sc + I_sh_sc) / I_sc
    I_gen = A_ph * I_sc

    # Residual function
    def residual(I, V):
        return (I_gen
                - I_d1_sat * (np.exp((V + R_s * I) / V_t) - 1)
                - I_d2_sat * (np.exp((V + R_s * I) / (2 * V_t)) - 1)
                - (V + R_s * I) / R_sh
                - I)

    # Voltage sweep
    V_vec = np.linspace(0, 0.8, 200)
    I_vec = []

    for V in V_vec:
        try:
            # Use I_sc as initial guess for low V, then previous solution for stability
            guess = I_vec[-1] if I_vec else I_sc
            I_sol = newton(residual, guess, args=(V,), maxiter=100, tol=1e-8)
            I_vec.append(max(I_sol, 0))  # enforce non-negative
        except RuntimeError:
            I_vec.append(np.nan)

    return V_vec, np.array(I_vec)


# ---- Interactive plot ----
def plot_IV(R_s=0.0043, R_sh=10.0, E_e=1.0):
    V, I = make_IV_curve(R_s, R_sh, E_e)

    plt.figure(figsize=(6, 4))
    plt.plot(V, I, "r-", lw=2)
    plt.xlabel("Voltage [V]")
    plt.ylabel("Current [A]")
    plt.title(f"IV Curve (Rs={R_s:.4f} Ω, Rsh={R_sh:.2f} Ω, Ee={E_e:.2f})")
    plt.ylim(0, 1.1 * np.nanmax(I))
    plt.xlim(0, max(V))
    plt.grid(True)
    plt.show()


interact(plot_IV,
         R_s=widgets.FloatLogSlider(value=0.0043, base=10, min=-3, max=-1, step=0.01, description="R_s [Ω]"),
         R_sh=widgets.FloatLogSlider(value=10.0, base=10, min=0, max=3, step=0.01, description="R_sh [Ω]"),
         E_e=widgets.FloatSlider(value=1.0, min=0.1, max=1.2, step=0.05, description="Irradiance [suns]"));
