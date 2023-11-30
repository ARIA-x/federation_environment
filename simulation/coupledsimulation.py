import os
from anytree import Node, RenderTree, search, AsciiStyle, PostOrderIter

## Own libraries
from simulation.configparse import SimulationConfig
from simulation.simulation import Simulation

class CoupledSimulation:
    def __init__(self):
        self.config = SimulationConfig()
        self.sims :list(Simulation)   = []
        self.root   = None


    def add(self, sim: tuple[Simulation, str]):
        self.sims.append(sim)


    def _search(self, name):
        for sim, _ in self.sims:
            if sim.config.getName() == name:
                return sim
        return None

    def relation(self, parent: str = None, child: str = None):
        if self.root is None:
            self.root = Node(parent)
            Node(child, parent=self.root)
        else:
            f = search.find(self.root, lambda node: node.name == parent)
            if f is None:
                print("Could not find the parent for %s" % parent)
            else:
                Node(child, parent=f)
        
        sim = self._search(parent)
        if sim:
            sim.takeOver()
        else:
            print("WARNING: there are no registered simulator: " + parent)

    
    def printRelation(self):
        print("=================================")
        print(RenderTree(self.root, style=AsciiStyle()).by_attr())
        for sim, _ in self.sims:
            print("---------------")
            print(sim.config.getName())
            print(sim.take_over)
        print("=================================")


    def run(self):
            for node in PostOrderIter(self.root):
                for sim, path in self.sims:
                    if sim.config.getName() == node.name:
                        print("RUN : %s " % sim.config.getName())
                        os.chdir(os.path.dirname(path))
                        if node.parent:
                            print("sim.run(%s)" % node.parent.name)
                            print("take over: " + str(sim.take_over))
                            sim.run(node.parent.name)
                        else:
                            print("sim.run()")
                            print("take over: " + str(sim.take_over))
                            sim.run()