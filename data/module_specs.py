# Tide Langner
# 25 August 2025
# Jinko JKM 290PP 72 module parameters - 6 columns x 12 rows

from pvmismatch import pvcell, pvmodule
from data.find_curves import find_Rsh_curve, find_Rs_curve

# Jinko JKM290PP-72 module with standard parameters from CEC module database
def std_module():
    cell = pvcell.PVcell(Rs=0.00641575, Rsh=285.79,
                         Isc0_T0=8.69, alpha_Isc=0.00060, Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5)
    return pvmodule.PVmodule(cell_pos=pvmodule.STD72, pvcells=[cell]*72)

# Degraded module with low shunt resistance
def degraded_module(Rsh=0.25):
    cell = pvcell.PVcell(Rs=0.00641575, Rsh=Rsh,
                         Isc0_T0=8.69, alpha_Isc=0.00060, Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5)
    return pvmodule.PVmodule(cell_pos=pvmodule.STD72, pvcells=[cell]*72)

def Rsh_degraded_module(p):
    Rsh_curve = find_Rsh_curve()
    Rsh = Rsh_curve[p]
    cell = pvcell.PVcell(Rs=0.00641575, Rsh=Rsh,
                         Isc0_T0=8.69, alpha_Isc=0.00060, Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5)
    return pvmodule.PVmodule(cell_pos=pvmodule.STD72, pvcells=[cell]*72)

def Rs_degraded_module(p):
    Rs_curve = find_Rs_curve()
    Rs = Rs_curve[p]
    cell = pvcell.PVcell(Rs=Rs, Rsh=285.79,
                         Isc0_T0=8.69, alpha_Isc=0.00060, Isat1_T0=1.79556E-10, Isat2_T0=1.2696E-5)
    return pvmodule.PVmodule(cell_pos=pvmodule.STD72, pvcells=[cell]*72)
