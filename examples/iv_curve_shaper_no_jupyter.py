import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.optimize import newton

# ---- Constants ----
I_d1_sat_T0 = 2.286188161253440e-11
I_d2_sat_T0 = 1.117455042372326e-10
I_sc0_T0 = 6.3056
T_cell = 298.15
alpha_I_sc = 0.0003551
E_g = 1.1
k = 1.380649e-23
q = 1.602176634e-19
T_0 = 289.15

# ---- Derived quantities ----
T_star = (T_cell / T_0) ** 3
delta_inv_T = 1 / T_0 - 1 / T_cell
I_d1_sat = I_d1_sat_T0 * T_star * np.exp(E_g * q / k * delta_inv_T)
I_d2_sat = I_d2_sat_T0 * T_star * np.exp(E_g * q / (2 * k) * delta_inv_T)
V_t = k * T_cell / q

def make_IV_curve(R_s, R_sh, E_e):
    """Compute IV curve for given R_s, R_sh, E_e."""
    I_sc0 = I_sc0_T0 * (1 + alpha_I_sc * (T_cell - T_0))
    I_sc = E_e * I_sc0

    V_d_sc = I_sc * R_s
    I_d1_sc = I_d1_sat * (np.exp(V_d_sc / V_t) - 1)
    I_d2_sc = I_d2_sat * (np.exp(V_d_sc / (2 * V_t)) - 1)
    I_sh_sc = V_d_sc / R_sh
    A_ph = 1 + (I_d1_sc + I_d2_sc + I_sh_sc) / I_sc
    I_gen = A_ph * I_sc

    def residual(I, V):
        return (I_gen
                - I_d1_sat * (np.exp((V + R_s * I) / V_t) - 1)
                - I_d2_sat * (np.exp((V + R_s * I) / (2 * V_t)) - 1)
                - (V + R_s * I) / R_sh
                - I)

    V_vec = np.linspace(0, 0.8, 200)
    I_vec = []
    for V in V_vec:
        try:
            guess = I_vec[-1] if I_vec else I_sc
            I_sol = newton(residual, guess, args=(V,), maxiter=100, tol=1e-8)
            I_vec.append(max(I_sol, 0))
        except RuntimeError:
            I_vec.append(np.nan)
    return V_vec, np.array(I_vec)

# ---- Initial parameters ----
R_s0, R_sh0, E_e0 = 0.0043, 10.0, 1.0
V, I = make_IV_curve(R_s0, R_sh0, E_e0)

# ---- Set up figure ----
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.35)
(line,) = ax.plot(V, I, lw=2, color="red")
ax.set_xlabel("Voltage [V]")
ax.set_ylabel("Current [A]")
ax.set_ylim(0, 7)
ax.set_xlim(0, 0.8)
ax.grid(True)

# ---- Sliders ----
axcolor = "lightgoldenrodyellow"
ax_rs = plt.axes([0.25, 0.25, 0.65, 0.03], facecolor=axcolor)
ax_rsh = plt.axes([0.25, 0.18, 0.65, 0.03], facecolor=axcolor)
ax_ee = plt.axes([0.25, 0.11, 0.65, 0.03], facecolor=axcolor)

s_rs = Slider(ax_rs, "R_s [Ω]", 1e-4, 0.05, valinit=R_s0, valstep=1e-4)
s_rsh = Slider(ax_rsh, "R_sh [Ω]", 1, 15, valinit=R_sh0, valstep=0.5)
s_ee = Slider(ax_ee, "E_e [suns]", 0.1, 1.2, valinit=E_e0, valstep=0.05)

# ---- Update function ----
def update(val):
    R_s = s_rs.val
    R_sh = s_rsh.val
    E_e = s_ee.val
    V, I = make_IV_curve(R_s, R_sh, E_e)
    line.set_ydata(I)
    line.set_xdata(V)
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw_idle()

s_rs.on_changed(update)
s_rsh.on_changed(update)
s_ee.on_changed(update)

plt.show()
