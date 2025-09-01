# Tide Langner
# 25 August 2025
# Runs simulations of PV system

import numpy as np
import matplotlib.pyplot as plt
from pv_system import create_system, create_Rsh_degraded_system, create_Rs_degraded_system, plot_pv_system
from mismatch_models import shade_modules, remove_modules
from pvmismatch import pvsystem

"""
# ---------- Example 1: Basic system ----------
pvsys = create_system()
print("Pmp:", pvsys.Pmp, " Vmp:", pvsys.Vmp, " Imp:", pvsys.Imp)
ex1 = pvsys.plotSys()

# ---------- Example 2: Single module shading ----------
pvsys = create_system()
shade_modules(pvsys, {0: {0: 0.01}})
print("Pmp after shading:", pvsys.Pmp)
print("Imp after shading:", pvsys.Imp)
print("Vmp after shading:", pvsys.Vmp)
ex2 = pvsys.plotSys()

# ---------- Example 3: Partial shading & heating ----------
pvsys = create_system()
shade_modules(pvsys, {0: {0: [(0.2,)*8, (0,1,2,3,4,5,6,7)]}})
pvsys.setTemps({0:{0:[(100.0+273.15,)*8, (0,1,2,3,4,5,6,7)]}})
print("Pmp after partial shading & heating:", pvsys.Pmp)
print("Imp after partial shading & heating:", pvsys.Imp)
print("Vmp after partial shading & heating:", pvsys.Vmp)
ex3 = pvsys.plotSys()

# ---------- Example 4: Module removal ----------
pvsys = create_system()
pvsys_degraded = remove_modules(pvsys, n_missing=3, strings_with_missing=8)
module_eq_diff = (pvsys.Pmp - pvsys_degraded.Pmp) / (pvsys.Pmp/len(pvsys.numberMods))
print("Module equivalent loss:", module_eq_diff)
print("Pmp after module removal:", pvsys_degraded.Pmp)
print("Imp after module removal:", pvsys_degraded.Imp)
print("Vmp after module removal:", pvsys_degraded.Vmp)
ex4 = pvsys_degraded.plotSys()

# ---------- Example 5: Loop over number of strings ----------
num_strings_list = np.unique(np.logspace(0, np.log10(50), num=10, dtype=int))
module_eq_diff_list = []

for num_strings in num_strings_list:
    sys = create_system(num_strings=num_strings)
    # shade module 0 in string 0 to 90% irradiance
    shade_modules(sys, {0:{0:0.9}})
    diff = (sys.Pmp - create_system(num_strings=num_strings).Pmp)/(sys.Pmp/len(sys.numberMods))
    module_eq_diff_list.append(diff)

plt.figure()
plt.plot(num_strings_list, module_eq_diff_list)
plt.xlabel("Number of Strings")
plt.ylabel("Module Equivalent Loss")
plt.grid()
# plt.show()
"""

# ---------- Example 6: Healthy vs Exponentially Degraded System ----------

# Healthy system
pvsys_healthy = create_system()

# Exponentially degraded Rsh or Rs system
pvsys_degraded = create_Rsh_degraded_system()   # --> change to create_Rsh_degraded_system()/create_Rs_degraded_system()
plot_pv_system(pvsys_degraded, title="Rsh")      # --> update title to match Rsh/Rs
plt.show()

# Prepare legend labels with Pmp info
label_healthy = (f"Healthy: Vmp={pvsys_healthy.Vmp:.1f}V, "
                 f"Imp={pvsys_healthy.Imp:.2f}A, Pmp={pvsys_healthy.Pmp:.1f}W")
label_degraded = (f"Degraded: Vmp={pvsys_degraded.Vmp:.1f}V, "
                  f"Imp={pvsys_degraded.Imp:.2f}A, Pmp={pvsys_degraded.Pmp:.1f}W")

# Plot IV curves
plt.figure(figsize=(10,6))
plt.plot(pvsys_healthy.Vsys, pvsys_healthy.Isys, label="Healthy System", lw=2)
plt.plot(pvsys_degraded.Vsys, pvsys_degraded.Isys, label="Degraded System", lw=2, ls="--")

# Highlight Pmp points
plt.plot(pvsys_healthy.Vmp, pvsys_healthy.Imp, 'o', color='blue', label=label_healthy)
plt.plot(pvsys_degraded.Vmp, pvsys_degraded.Imp, 'o', color='red', label=label_degraded)

plt.xlabel("Voltage [V]")
plt.ylabel("Current [A]")
plt.title("IV Curve: Healthy vs Exponentially Degraded System")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Optional: print Pmp values
print("Healthy Pmp:", pvsys_healthy.Pmp)
print("Degraded Pmp:", pvsys_degraded.Pmp)