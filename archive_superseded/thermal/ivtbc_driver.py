import os
import subprocess
import numpy as np

# =============================================================
# IVTBC DRIVER - Price et al. 2023
# =============================================================

r2        = 0.00334
T_inf     = 791.0
hp_radius = 0.00795
hp_length = 1.60
epsilon   = 0.1
omega     = 0.5
max_iter  = 50
case_dir  = os.path.dirname(os.path.abspath(__file__))
hp_area   = 2 * np.pi * hp_radius * hp_length

def read_latest_heat_flux(case_dir):
    flux_file = os.path.join(case_dir, 'postProcessing', 'solid', 'wallHeatFlux', '0', 'wallHeatFlux.dat')
    with open(flux_file) as f:
        lines = [l for l in f.readlines() if not l.startswith('#') and l.strip()]
    last = lines[-1].split()
    return abs(float(last[4]))

def compute_Tvap(Q_wall, Tvap_old):
    q_flux   = Q_wall / hp_area
    Tvap_raw = r2 * q_flux + T_inf
    Tvap_new = omega * Tvap_raw + (1 - omega) * Tvap_old
    return Tvap_new, Tvap_raw

def update_BC(case_dir, Tvap):
    T_file = os.path.join(case_dir, '0', 'solid', 'T')
    with open(T_file) as f:
        content = f.read()
    import re
    # Only replace Ta value inside heatpipe_wall block
    pattern = r'(heatpipe_wall.*?Ta\s+uniform\s+)[\d.]+;'
    replacement = r'\g<1>' + f'{Tvap:.4f};'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    with open(T_file, 'w') as f:
        f.write(new_content)
    print(f'  Updated heatpipe_wall Ta = {Tvap:.4f} K')

def run_openfoam(case_dir):
    result = subprocess.run(['foamMultiRun'], cwd=case_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print('OpenFOAM error:')
        print(result.stderr[-500:])
        return False
    return True

def clean_time_folders(case_dir):
    import shutil
    for entry in os.listdir(case_dir):
        try:
            t = float(entry)
            if t > 0:
                shutil.rmtree(os.path.join(case_dir, entry))
        except ValueError:
            continue

if __name__ == '__main__':
    print('=' * 60)
    print('IVTBC DRIVER')
    print('=' * 60)
    Tvap = 1145.62
    converged = False
    iteration = 0
    results = []
    print(f'Initial Tvap = {Tvap:.2f} K ({Tvap-273.15:.2f} C)')
    print()
    while not converged and iteration < max_iter:
        print(f'--- Iteration {iteration} ---')
        update_BC(case_dir, Tvap)
        clean_time_folders(case_dir)
        print('  Running foamMultiRun...')
        ok = run_openfoam(case_dir)
        if not ok:
            print('  OpenFOAM failed - stopping')
            break
        print('  foamMultiRun complete')
        Q_wall = read_latest_heat_flux(case_dir)
        print(f'  Q_wall = {Q_wall:.4f} W')
        Tvap_new, Tvap_raw = compute_Tvap(Q_wall, Tvap)
        diff = abs(Tvap_new - Tvap)
        print(f'  Tvap_raw     = {Tvap_raw:.4f} K ({Tvap_raw-273.15:.2f} C)')
        print(f'  Tvap_relaxed = {Tvap_new:.4f} K ({Tvap_new-273.15:.2f} C)')
        print(f'  |dTvap|      = {diff:.4f} K')
        results.append({'iter': iteration, 'Q': Q_wall, 'Tvap': Tvap_new, 'diff': diff})
        if diff < epsilon:
            converged = True
            print(f'  CONVERGED')
        Tvap = Tvap_new
        iteration += 1
        print()
    print('=' * 60)
    print('FINAL RESULTS')
    print('=' * 60)
    print(f'Converged : {converged}')
    print(f'Iterations: {iteration}')
    print(f'Final Tvap: {Tvap:.4f} K  ({Tvap-273.15:.2f} C)')
    print()
    print('Iter | Q_wall (W) | Tvap (K) | Tvap (C) | diff (K)')
    print('-' * 58)
    for r in results:
        print(f"{r['iter']:4d} | {r['Q']:10.3f} | {r['Tvap']:8.3f} | {r['Tvap']-273.15:8.3f} | {r['diff']:8.4f}")