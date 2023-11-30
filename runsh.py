from xmlrpc.client import Boolean
from simulation.configparse import SimulationConfig


script_header = """\
#!/bin/bash

"""

script_prefix = """\
echo "Start Simulation"

"""

script_postfix = """
echo "End Simulation"
"""


def mkscript(conf: SimulationConfig, take_over: Boolean):

    _out = "ln -s /data/" + conf.getName() + '/out/ ' + conf.getOutdir() + '\n'
    _cmd = conf.getCmdline() + '\n'

    if take_over and conf.getIndir() != None:
        _in = "ln -s /data/" + conf.getName() + "/in/ " + conf.getIndir() + '\n'
        script = script_header + script_prefix + _in + _out + _cmd + script_postfix

    else:
        script = script_header + script_prefix + _out + _cmd + script_postfix
        ## TODO: consider the input directory outside the simulator directory
        ## prev_sim == None and conf.getIndir() == "indicate a directory"

    if take_over == False and conf.getIndir() == None:        
        print("WARNING: simulator(%s) should take over the previous result, but an input directory is not offered." % conf.getName())

    return script.replace('\r', '')


## for test
if __name__ == "__main__":
    import tempfile, os
    import subprocess
    import simulation.configparse

    conf = SimulationConfig()
    conf.setName("test-sim")
    conf.setOutdir("outdir/")
    conf.setCmd("python")
    conf.setArgs(["sim.py"])
    conf.setIndir("indir/")

    script = mkscript(conf, False)
    print (script)
    script = mkscript(conf, True)
    print (script)
    
    #with open("test.bat", "w") as f:
    #    f.write(script)
    #subprocess.run([f.name], shell=True)