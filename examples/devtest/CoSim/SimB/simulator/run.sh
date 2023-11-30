#!/bin/bash

echo "Start Simulation"

ln -s /data/sim-b/in/ /simulator/input
ln -s /data/sim-b/out/ /simulator/result
python sim.py

echo "End Simulation"
