import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


R_s = 0.004267236774264931
R_sh = 10.01226369025448
E_e = 1.0
I_d1_sat_T0 = 2.286188161253440e-11
I_d2_sat_T0 = 1.117455042372326e-10
I_sc0_T0 = 6.3056
T_cell = 298.15
a_RBD = 1.036748445065697e-4
b_RBD = 0.
# V_RBD = -5.527260068445654
n_RBD = 3.284628553041425
E_g = 1.1
alpha_I_sc = 0.0003551
k = 1.380649e-23
q = 1.602176634e-19
T_0 = 289.15

# derived quantities
T_star = (T_cell/T_0)**3
delta_inv_T = 1/T_0 - 1/T_cell
I_d1_sat = I_d1_sat_T0*T_star*np.exp(E_g*q/k*delta_inv_T)
I_d2_sat = I_d2_sat_T0*T_star*np.exp(E_g*q/(2*k)*delta_inv_T)
I_sc0 = I_sc0_T0*(1+alpha_I_sc*(T_cell-T_0))
I_sc = E_e*I_sc0
V_d_sc = I_sc*R_s
V_t = k*T_cell/q
I_d1_sc = I_d1_sat*(np.exp(V_d_sc/V_t) - 1)
I_d2_sc = I_d2_sat*(np.exp(V_d_sc/(2*V_t)) - 1)
I_sh_sc = V_d_sc/R_sh
A_ph = 1 + (I_d1_sc + I_d2_sc+I_sh_sc)/I_sc
I_gen = A_ph*I_sc

def residual(I_c, V_c):
    residual_raw = (I_gen 
            - I_d1_sat*(np.exp((V_c+R_s*I_c)/V_t) - 1)
            - I_d2_sat*(np.exp((V_c+R_s*I_c)/(2*V_t)) - 1)
            - (V_c + R_s*I_c)/R_sh 
            - I_c)
    return residual_raw#(residual_raw<0)*residual_raw*10 + (residual_raw>0)*residual_raw

I_vec = np.linspace(0,7.,1000)
V_vec = np.linspace(0.,0.7,1000)
VV, II = np.meshgrid(V_vec, I_vec)

RR = residual(II, VV)

fig = plt.figure(figsize=(8, 4), dpi=80)
ax = fig.add_subplot(111, projection="3d")

# Residual surface
surf = ax.plot_surface(VV, II, RR, cmap="viridis", alpha=0.6) # use np.log10(np.abs(RR)) for log plot

# Residual=0 contour (projected to z=0 plane)
cs = ax.contour(VV, II, RR, levels=[0], colors="red", linewidths=2, offset=0)

# ax_c = fig.add_subplot(122)
# ax_c.contourf(VV,II,RR)
# ax_c.contour(VV,II,RR,levels=[0])
plt.show()