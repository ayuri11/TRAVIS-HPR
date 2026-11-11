import os, subprocess, shutil, json, re
import numpy as np

r2        = 0.00334
T_inf     = 791.0
hp_radius = 0.00795
hp_length = 1.60
hp_area   = 2 * np.pi * hp_radius * hp_length
epsilon   = 0.1
omega     = 0.5
max_iter  = 50
case_dir  = os.path.expanduser('~/HPR_case')

ring_data = {
    'ring_0': {'r_cm': 2.65,  'count': 1,  'q_hp_W': 17830.0},
    'ring_1': {'r_cm': 8.15,  'count': 6,  'q_hp_W': 22200.0},
    'ring_2': {'r_cm': 13.65, 'count': 12, 'q_hp_W': 10440.0},
    'ring_3': {'r_cm': 19.15, 'count': 18, 'q_hp_W': 260.0},
}

def update_heat_source(case_dir, q_vol):
    fvmodels = os.path.join(case_dir, 'constant', 'solid', 'fvModels')
    with open(fvmodels) as f:
        content = f.read()
    content = re.sub(r'q\s+[\d.e+]+;', 'q               ' + f'{q_vol:.4e};', content)
    with open(fvmodels, 'w') as f:
        f.write(content)

def update_BC(case_dir, Tvap):
    T_file = os.path.join(case_dir, '0', 'solid', 'T')
    lines = [
        'FoamFile { format ascii; class volScalarField; object T; }',
        'dimensions [0 0 0 1 0 0 0];',
        f'internalField uniform {Tvap:.4f};',
        'boundaryField',
        '{',
        '    heatpipe_wall',
        '    {',
        '        type            externalWallHeatFluxTemperature;',
        '        mode            coefficient;',
        '        h               uniform 751.88;',
        f'        Ta              uniform {Tvap:.4f};',
        f'        value           uniform {Tvap:.4f};',
        '    }',
        '    outer_symmetry { type symmetry; }',
        '    front { type empty; }',
        '    back  { type empty; }',
        '}',
    ]
    with open(T_file, 'w') as f:
        f.write('\n'.join(lines))

def read_Q(case_dir):
    flux_file = os.path.join(case_dir, 'postProcessing', 'solid',
                             'wallHeatFlux', '0', 'wallHeatFlux.dat')
    with open(flux_file) as f:
        lines = [l for l in f.readlines() if not l.startswith('#') and l.strip()]
    return abs(float(lines[-1].split()[4]))

def run_openfoam(case_dir):
    result = subprocess.run(['foamMultiRun'], cwd=case_dir,
                            capture_output=True, text=True)
    return result.returncode == 0

def clean_times(case_dir):
    for entry in os.listdir(case_dir):
        try:
            t = float(entry)
            if t > 0:
                shutil.rmtree(os.path.join(case_dir, entry))
        except ValueError:
            continue

if __name__ == '__main__':
    print('=' * 65)
    print('MULTI-RING IVTBC DRIVER')
    print('=' * 65)

    all_results = {}

    for ring_name, ring in ring_data.items():
        q_hp_W = ring['q_hp_W']
        r_cm   = ring['r_cm']
        count  = ring['count']
        cell_vol_m3 = (0.055**2) * 1.60
        q_vol = q_hp_W * 6 / cell_vol_m3

        print(f'--- {ring_name} | r={r_cm}cm | {count} pipes | q_HP={q_hp_W:.0f} W ---')
        print(f'    q_vol = {q_vol:.3e} W/m3')

        Tvap = 1145.62
        converged = False
        iteration = 0

        while not converged and iteration < max_iter:
            update_BC(case_dir, Tvap)
            update_heat_source(case_dir, q_vol)
            clean_times(case_dir)
            ok = run_openfoam(case_dir)
            if not ok:
                print(f'  OpenFOAM failed at iteration {iteration}')
                break
            Q_wall   = read_Q(case_dir)
            q_flux   = Q_wall / hp_area
            Tvap_raw = r2 * q_flux + T_inf
            Tvap_new = omega * Tvap_raw + (1 - omega) * Tvap
            diff     = abs(Tvap_new - Tvap)
            print(f'  iter {iteration}: Q={Q_wall:.2f}W Tvap={Tvap_new:.2f}K ({Tvap_new-273.15:.2f}C) diff={diff:.4f}K')
            if diff < epsilon:
                converged = True
            Tvap = Tvap_new
            iteration += 1

        all_results[ring_name] = {
            'r_cm': r_cm, 'count': count, 'q_hp_W': q_hp_W,
            'Tvap_K': Tvap, 'Tvap_C': Tvap - 273.15,
            'converged': converged, 'iterations': iteration
        }
        print(f'  RESULT: Tvap = {Tvap:.4f} K  ({Tvap-273.15:.4f} C)')
        print()

    print('=' * 65)
    print('FINAL PER-RING TVAP RESULTS')
    print('=' * 65)
    print(f"{'Ring':<8} {'r(cm)':<8} {'pipes':<8} {'q_HP(W)':<12} {'Tvap(K)':<12} {'Tvap(C)':<12}")
    print('-' * 65)
    for rname, r in all_results.items():
        print(f"{rname:<8} {r['r_cm']:<8} {r['count']:<8} {r['q_hp_W']:<12.0f} {r['Tvap_K']:<12.4f} {r['Tvap_C']:<12.4f}")

    out = os.path.expanduser('~/openfoam-cases/Heat-Pipe-Reactor/PHASE 3/ivtbc_per_ring_results.json')
    with open(out, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f'Saved: {out}')
