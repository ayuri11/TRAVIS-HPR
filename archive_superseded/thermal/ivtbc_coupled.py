import subprocess
import re
import math
import os

# 1. INITIALIZATION (From your simplified script)
T_inf = 791.0
D = 0.0159
lc = 1.82
r2 = 0.00334
w = 0.5
eps = 0.1

patches = ["ring_0_hp", "ring_1_hp", "ring_2_hp", "ring_3_hp"]
Tvap = {patch: 1145.62 for patch in patches} # Start with your converged guess

def update_0_T_file(Tvap_dict):
    """Finds the Ta value for each patch in 0/T and replaces it"""
    with open("0/T", "r") as f:
        content = f.read()
    
    for patch, temp in Tvap_dict.items():
        # Regex to find the Ta line specific to this patch and update it
        pattern = rf"({patch}\s*{{[^}}]*Ta\s+constant\s+)\d+\.?\d*;"
        replacement = f"\\g<1>{temp:.2f};"
        content = re.sub(pattern, replacement, content)
        
    with open("0/T", "w") as f:
        f.write(content)

# 2. IVTBC ITERATION LOOP
iteration = 0
converged = False

while not converged and iteration < 50:
    print(f"\n--- Iteration {iteration} ---")
    
    # A. Update OpenFOAM boundaries
    update_0_T_file(Tvap)
    
    # B. Run OpenFOAM (laplacianFoam)
    print("Running laplacianFoam...")
    subprocess.run(["laplacianFoam"], stdout=subprocess.DEVNULL)
    
    # C. Read extracted heat fluxes
    # wallHeatFlux.dat creates a table: Time | Patch1 | Patch2 ...
    flux_file = "postProcessing/wallHeatFlux1/0/wallHeatFlux.dat"
    with open(flux_file, "r") as f:
        lines = f.readlines()
        last_line = lines[-1].split()
        # Note: You'll need to map the column indices to your patch names based on the file header
        
    Tvap_new = {}
    max_diff = 0.0
    
    # D. Calculate new Tvap
    for idx, patch in enumerate(patches):
        # get extracted Q (Watts) for this patch from the last line of dat file
        q_extracted = abs(float(last_line[idx + 1])) 
        
        # Apply Price et al. Eq 4
        T_calc = (r2 / (math.pi * D * lc)) * q_extracted + T_inf
        Tvap_new[patch] = w * T_calc + (1 - w) * Tvap[patch]
        
        diff = abs(Tvap_new[patch] - Tvap[patch])
        if diff > max_diff:
            max_diff = diff

    print(f"Max Tvap change: {max_diff:.4f} K")
    Tvap = Tvap_new
    
    if max_diff < eps:
        converged = True
        print("IVTBC Converged!")
        
    # Optional: Clear old time directories to save space
    subprocess.run("rm -rf [1-9]*", shell=True) 
    iteration += 1
