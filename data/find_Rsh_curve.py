import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# function of dataset found initially via MS Excel as y = 487.05x^(-0.985)
# function refined via manual adjustment to best fit

def find_Rsh_curve():
    k = -2.085          # exponent values
    start_val = 285.79  # Rsh of standard module
    n = 30              # number of points to fit

    x = np.arange(0, n)
    y = start_val * (x+1) ** k  # x+1 to avoid singularity at x=0

    Rsh_curve = pd.Series(y, index=x)
    return Rsh_curve

# Rsh_curve = find_Rsh_curve()
# print(Rsh_curve)
