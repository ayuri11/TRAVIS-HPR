#!/bin/bash
source /opt/openfoam11/etc/bashrc
cd ~/HPR_snappy

echo "=== Cleaning old mesh ==="
rm -rf constant/polyMesh 0.* 1 2 3 4 5

echo "=== Running blockMesh ==="
blockMesh 2>&1 | tail -3

echo "=== Extracting surface features ==="
surfaceFeatures 2>&1 | tail -3

echo "=== Running snappyHexMesh ==="
snappyHexMesh -overwrite 2>&1 | grep -E "heatPipe|fuelPin|patches|illegal|Mesh OK|wall"

echo "=== Checking mesh ==="
checkMesh 2>&1 | grep -E "cells|patches|illegal|Mesh OK|non-ortho"

echo "=== Boundary patches ==="
cat constant/polyMesh/boundary
