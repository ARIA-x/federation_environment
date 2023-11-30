import sys, os

## モジュール探索ディレクトリの追加
## インストールパッケージができれば本来はいらない
dir = os.path.dirname(__file__)
if os.name == 'posix':
    sys.path.append(os.path.join(dir, '../../../'))
else:
    sys.path.append(os.path.join(dir, '..\\..\\..\\'))
## モジュール探索ディレクトリの追加（ここまで）

## Simulation libraries
from simulation.coupledsimulation import CoupledSimulation

import SimB.run
import SimC.run

if __name__ == "__main__":
    cosim = CoupledSimulation()
    b = SimB.run.sim()
    c = SimC.run.sim()
    cosim.add(b)
    cosim.add(c)
    cosim.relation(parent="sim-b", child="sim-c")
    cosim.printRelation()
    cosim.run()