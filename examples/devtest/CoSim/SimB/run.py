import sys, os

## モジュール探索ディレクトリの追加
## インストールパッケージができれば本来はいらない
dir = os.path.dirname(__file__)
if os.name == 'posix':
    sys.path.append(os.path.join(dir, '../../../'))
else:
    sys.path.append(os.path.join(dir, '..\\..\\..\\..\\'))
## モジュール探索ディレクトリの追加（ここまで）

## Simulation libraries
from simulation.simulation import Simulation
import sim_utils

def sim():
    # コンフィグの設定と実行
    configfile = os.path.dirname(__file__) + sim_utils.DirSep() + "config.ini"
    sim = Simulation()
    if configfile:
        sim.setconfig(configfile)
    else:
        ## コンフィグファイルがない場合、以下のように個別設定も可能
        sim.path(path=None)
        sim.cmdline(cmdline=None)
    return sim, __file__


if __name__ == "__main__":
    sim, _ = sim()
    sim.run()
