# Tide Langner
# 25 August 2025
# Jinko JKM 290PP 72 module parameters - 6 columns x 12 rows

from pvmismatch import *
from pvmismatch.pvmismatch_lib.pvcell import PVcell
from pvmismatch.pvmismatch_lib.pvmodule import PVmodule

from pvmismatch import pvcell, pvmodule

# Standard 72-cell module
def std_module():
    cell = pvcell.PVcell()
    return pvmodule.PVmodule(cell_pos=pvmodule.STD72, pvcells=[cell]*72)

# Degraded module with low shunt resistance
def degraded_module(Rsh=0.25):
    cell = pvcell.PVcell(Rsh=Rsh)
    return pvmodule.PVmodule(cell_pos=pvmodule.STD72, pvcells=[cell]*72)

"""
# create custom module (Jinko JKM 290PP 72) --> needs attention
Jinko_module = PVmodule(
    cell_pos=pvmodule.STD72,
    pvcells=[PVcell(Rs=0.00641575, Rsh=285.79) for _ in range(72)]  # Rs and Rsh found in CEC module database
)
"""
