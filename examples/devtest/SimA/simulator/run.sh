#!/bin/bash

echo "Start Simulation"

ln -s /data/sim-a/out/ /simulator/result
python sim.py

echo "End Simulation"
