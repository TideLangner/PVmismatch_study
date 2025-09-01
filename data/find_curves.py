import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

num_modules = 30
x = np.arange(0, num_modules)

def find_Rsh_curve():
    """function of dataset found initially via MS Excel as y = 2429.2x^(-1.535)
    function refined via manual adjustment to best fit of y = 285.79x^(-2.085) for custom cell data extrapolation"""
    k = -2.085          # exponent values
    start_val = 285.79  # Rsh of standard module
    n = num_modules     # number of points to fit

    y = start_val * (x+1) ** k  # x+1 to avoid singularity at x=0

    Rsh_curve = pd.Series(y, index=x)
    return Rsh_curve

# Rsh_curve = find_Rsh_curve()
# print(Rsh_curve)

def find_Rs_curve():
    """function of dataset found initially via MS Excel as y = 1.5716x^(-0.254)
    function refined via manual adjustment to best fit of y = 0.00641575x^(0.254) for custom cell data extrapolation"""
    k = 0.254
    start_val = 0.00641575    # Rs of standard cell
    n = num_modules           # number of points to fit

    y = start_val * (x+1) ** k    # x+1 to avoid singularity at x=0

    Rs_curve = pd.Series(y, index=x)
    return Rs_curve

"""
y = pd.read_csv('Rs_curve.csv', usecols=[1])
Rs_curve = find_Rs_curve()
#print(y)
print(Rs_curve)

plt.figure(figsize=(10, 5))
#plt.plot(x, y, 'o-', label='Data')
plt.plot(x, Rs_curve, label='Curve Fit')
plt.xlabel("Rsh")
plt.ylabel("Module Number")
plt.legend()
plt.grid()
plt.show()
"""
