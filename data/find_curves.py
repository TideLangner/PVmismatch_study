import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

num_modules = 30
x = np.arange(0, num_modules)

def find_Rsh_curve():
    """function of dataset found initially via MS Excel as y = 2429.2x^(-1.535)
    function refined via manual adjustment to best fit of y = 285.79x^(-2.085) for custom cell data extrapolation"""
    k = -1.535          # exponent value
    start_val = 258.79  # Rsh of standard cell
    n = num_modules     # number of points to fit

    y = start_val * (x+1) ** k  # x+1 to avoid singularity at x=0

    Rsh_curve = pd.Series(y, index=x)
    return Rsh_curve

def find_Rs_curve():
    """function of dataset found initially via MS Excel as y = 1.5716x^(-0.254)
    function refined via manual adjustment to best fit of y = 0.00641575x^(0.254) for custom cell data extrapolation"""
    k = 0.254                 # exponent value
    start_val = 0.00641575    # Rs of standard cell
    n = num_modules           # number of points to fit

    y = start_val * (x+1) ** k    # x+1 to avoid singularity at x=0

    Rs_curve = pd.Series(y, index=x)
    return Rs_curve

def plot_curves():
    script_dir = Path(__file__).parent
    Rsh_csv = script_dir / 'Rsh_curve.csv'
    Rs_csv = script_dir / 'Rs_curve.csv'

    Rsh_data = pd.read_csv(Rsh_csv, usecols=[1])
    Rsh_curve = find_Rsh_curve()

    Rs_data = pd.read_csv(Rs_csv, usecols=[1])
    Rs_curve = find_Rs_curve()

    fig, (Rsh, Rs) = plt.subplots(2, 1, figsize=(10, 7))

    #Rsh.plot(x, Rsh_data, 'o-', label='Data')
    Rsh.plot(x, Rsh_curve, label='Curve Fit')
    Rsh.set_title("Rsh Curve Fit")
    Rsh.set_xlabel("Module Number")
    Rsh.set_ylabel("Rsh")
    Rsh.legend()
    Rsh.grid()

    #Rs.plot(x, Rs_data, 'o-', label='Data')
    Rs.plot(x, Rs_curve, label='Curve Fit')
    Rs.set_title("Rs Curve Fit")
    Rs.set_xlabel("Module Number")
    Rs.set_ylabel("Rs")
    Rs.legend()
    Rs.grid()

    plt.tight_layout()
    plt.show()
