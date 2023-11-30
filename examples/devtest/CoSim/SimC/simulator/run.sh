#!/bin/bash

echo "Start Simulation"

ln -s /data/sim-c/out/ /simulator/result
python sim.py

echo "End Simulation"
