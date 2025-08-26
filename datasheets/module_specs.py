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

'''
# Jinko JKM 290PP 72 module parameters
CELL_PARAMS = {
    'Isc_ref': 9.2,
    'Voc_ref': 0.6,
    'Rs': 0.005,
    'Rsh': 1000
}


def create_jinko_module():
    Ns = 12  # cells in series per substring
    Np = 6  # parallel substrings

    # Create cells
    cells = [PVcell(**CELL_PARAMS) for _ in range(Ns * Np)]

    # Create module
    module = PVmodule(Ns=Ns, Np=Np, cells=cells, name='Jinko JKM 290PP 72')
    return module
'''
