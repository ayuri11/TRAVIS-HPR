"""
pin_to_pipe.py - turn the fine wedge tally (pin_tally.npz) into per-pipe loads and per-pipe Tvap.

  python pin_to_pipe.py --npz pin_tally.npz --layout pin_layout.json --Tinf 750 --L 1.82
  python pin_to_pipe.py --selftest            # no OpenMC needed; checks the code on synthetic data

Method (all assumptions are printed in the output):
  1. Unfold the wedge to the full core with the 12-fold symmetry (6 rotations x mirror). Voxels cut by the
     30-degree plane are divided by their inside-wedge area fraction.
  2. Normalise to 2.5 MW and give every voxel to its nearest fuel pin (Voronoi) -> power per pin.
  3. Decide which pipe removes which heat. DEFAULT ('cond'): solve 2-D steady conduction through the graphite
     with the pipes as conductance sinks G = 2*pi*r_p*L/(r1+r2) (the Eq. 7 wall relation), so every pipe's
     load follows from the temperature field, i.e. a coupled multi-pipe solve for an axially uniform load.
     Cruder alternatives are printed beside it: 1/d^2 weights within a cut-off radius, and the whole cell's power
     split equally over its own pipes (the ring-mean-like baseline).
  4. Pipes that are images of each other under the symmetry are averaged (this also averages out noise).
  5. Tvap = Tinf + 124 K + r2*q'',  q'' = Q/(2*pi*r_p*L)   (Price et al. Eq. 7, isolated pipe, steady state).
"""
import argparse, json, math, os, sys
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'common'))
import travis_layout as TL

R1, R2, GAP, LIMIT_C = 0.00133, 0.00334, 124.0, 900.0
TABLE42 = [50376.0, 286324.0, 766044.0, 1397256.0]       # ring totals of Table 4.2 (coarse-mesh binning)
VARIANTS = {'r30': (3.0, 2.0), 'r25': (2.5, 2.0), 'r40': (4.0, 2.0)}   # (cut-off radius cm, exponent n)


def wedge_fraction(nx, ny, h, sub=8):
    s = (np.arange(sub) + 0.5) / sub
    x = (np.arange(nx)[None, :, None, None] + s[None, None, :, None]) * h
    y = (np.arange(ny)[:, None, None, None] + s[None, None, None, :]) * h
    return ((y >= 0) & (y <= x * math.tan(math.radians(30)))).mean(axis=(2, 3))


def unfold(mean, std, h, total_W=2.5e6):
    ny, nx = mean.shape
    frac = wedge_fraction(nx, ny, h)
    ok = frac > 0.25
    m = np.where(ok, mean / np.where(ok, frac, 1.0), 0.0)
    s = np.where(ok, std / np.where(ok, frac, 1.0), 0.0)
    n = 2 * nx
    c = -nx * h + (np.arange(n) + 0.5) * h
    X, Y = np.meshgrid(c, c)
    xf, yf = TL.fold_to_wedge(X, Y)
    ix = np.clip((xf / h).astype(int), 0, nx - 1)
    iy = np.clip((yf / h).astype(int), 0, ny - 1)
    P = m[iy, ix]
    S = s[iy, ix]
    return X.ravel(), Y.ravel(), P.ravel(), S.ravel()


def pin_powers(X, Y, P, S, pins, total_W=2.5e6, max_d=2.5):
    pxy = np.array([[p['x'], p['y']] for p in pins])
    d, idx = cKDTree(pxy).query(np.c_[X, Y])
    keep = d <= max_d
    dropped = P[~keep].sum() / P.sum()
    pin_P = np.bincount(idx[keep], weights=P[keep], minlength=len(pins))
    pin_V = np.bincount(idx[keep], weights=S[keep] ** 2, minlength=len(pins))
    scale = total_W / pin_P.sum()
    return pin_P * scale, np.sqrt(pin_V) * scale, dropped


def distribute(pin_xy, pin_P, pipe_xy, R, n):
    """Each pin gives its power to every pipe within R cm, weights 1/d^n (a distance cut-off, not 'K nearest',
    so equal-distance pipes are treated alike and the 12-fold symmetry is preserved)."""
    tree = cKDTree(pipe_xy)
    load = np.zeros(len(pipe_xy))
    for xy, P in zip(pin_xy, pin_P):
        ids = tree.query_ball_point(xy, R)
        if not ids:                                   # no pipe in reach: use the nearest one(s)
            d0, _ = tree.query(xy)
            ids = tree.query_ball_point(xy, d0 + 1e-6)
        d = np.linalg.norm(pipe_xy[ids] - xy, axis=1)
        w = 1.0 / np.maximum(d, 1e-6) ** n
        load[ids] += P * w / w.sum()
    return load


def conduction_loads(X, Y, P, pipes, args, coarsen=1):
    """Where does each pin's heat really go?  Solve 2-D steady conduction in the radial plane of the whole core:
         k * lap(T) + q(x,y) = sum_i G_i * (T - T_ref) at the pipe positions   (T_ref = 0 here, it cancels)
       q  : fission-tally power field, W per metre of core height (reflector/outer edge adiabatic)
       G_i: wall conductance of each pipe = 2*pi*r_p*L / (r1 + r2) per metre of core height (Eq. 7: the pipe wall
            sees T_ref + (r1+r2)*q'' on the graphite side, so a hotter neighbourhood pushes more heat into the pipe)
       This is the coupled multi-pipe problem for an axially uniform load.  Returns the share of the total that
       each pipe removes (sums to 1) and the graphite temperature field relative to T_ref."""
    import scipy.sparse as sp
    from scipy.sparse.linalg import spsolve
    n0 = int(round(math.sqrt(len(P))))
    h0 = float(X[1] - X[0]) if n0 > 1 else 0.1
    Pm = P.reshape(n0, n0)
    c = coarsen
    Pm = Pm.reshape(n0 // c, c, n0 // c, c).sum(axis=(1, 3))         # W per coarse voxel
    n = n0 // c; h = h0 * c
    Pm = Pm * (args.total_W / Pm.sum())
    q = Pm.ravel() / args.Lcore                                       # W/m per node
    k = args.k
    idx = np.arange(n * n).reshape(n, n)
    rows, cols, vals = [], [], []
    diag = np.zeros(n * n)
    for a, b in ((idx[:, :-1], idx[:, 1:]), (idx[:-1, :], idx[1:, :])):
        a = a.ravel(); b = b.ravel()
        rows += [a, b]; cols += [b, a]; vals += [-k * np.ones(len(a))] * 2
        np.add.at(diag, a, k); np.add.at(diag, b, k)
    c0 = X[0] - 0.0 + (h0 * (c - 1)) / 2.0                           # centre of the first coarse node
    G = 2 * math.pi * args.rp * args.L / (R1 + R2) / args.Lcore        # W/m/K per pipe
    wts = []
    for q_ in pipes:
        fx = (q_['x'] - c0) / h; fy = (q_['y'] - c0) / h
        i0 = int(math.floor(fx)); j0 = int(math.floor(fy)); tx = fx - i0; ty = fy - j0
        for di, dj, w in ((0, 0, (1 - tx) * (1 - ty)), (1, 0, tx * (1 - ty)), (0, 1, (1 - tx) * ty), (1, 1, tx * ty)):
            wts.append((len(wts) // 4, (j0 + dj) * n + (i0 + di), w))
    wts = np.array(wts)
    for pid, node, w in wts:
        diag[int(node)] += G * w
    A = sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n * n, n * n)).tocsr() \
        + sp.diags(diag)
    T = spsolve(A.tocsc(), q)
    Qi = np.zeros(len(pipes))
    for pid, node, w in wts:
        Qi[int(pid)] += G * w * T[int(node)]
    return Qi / Qi.sum(), T


def distribute_by_cell(pins, pin_P, pipes):
    load = np.zeros(len(pipes))
    cell_P = {}
    for p, P in zip(pins, pin_P):
        cell_P[p['cell']] = cell_P.get(p['cell'], 0.0) + P
    n_in = {}
    for q in pipes:
        n_in[q['cell']] = n_in.get(q['cell'], 0) + 1
    for k, q in enumerate(pipes):
        load[k] = cell_P[q['cell']] / n_in[q['cell']]
    return load


def orbit_average(load, pipes):
    xf, yf = TL.fold_to_wedge(np.array([q['x'] for q in pipes]), np.array([q['y'] for q in pipes]))
    keys = [(round(float(a), 1), round(float(b), 1)) for a, b in zip(xf, yf)]
    groups = {}
    for i, k in enumerate(keys):
        groups.setdefault(k, []).append(i)
    out = np.zeros_like(load)
    spread = {}
    for k, ids in groups.items():
        out[ids] = load[ids].mean()
        spread[k] = (load[ids].max() - load[ids].min()) / max(load[ids].mean(), 1e-9)
    return out, groups, spread


def thermal(Q, Tinf, L, rp):
    q = Q / (2 * math.pi * rp * L)
    tv = Tinf + GAP + R2 * q - 273.15
    return tv, tv + R1 * q


def analyse(pins, pipes, pin_P, args, field=None):
    pin_xy = np.array([[p['x'], p['y']] for p in pins])
    pipe_xy = np.array([[q['x'], q['y']] for q in pipes])
    rings = np.array([q['ring'] for q in pipes])
    res = {}
    loads = {k: distribute(pin_xy, pin_P, pipe_xy, K, n) for k, (K, n) in VARIANTS.items()}
    loads['cell'] = distribute_by_cell(pins, pin_P, pipes)
    if field is not None:
        share, T = conduction_loads(*field, pipes, args)
        loads['cond'] = share * args.total_W
        res['_Tgmax_rel_K'] = float(T.max())
    for k, ld in loads.items():
        avg, groups, spread = orbit_average(ld, pipes)
        tv = np.array([thermal(Q, args.Tinf, args.L, args.rp)[0] for Q in avg])
        tm = np.array([thermal(Q, args.Tinf, args.L, args.rp)[1] for Q in avg])
        ring_rows = []
        for r in range(4):
            m = rings == r
            ring_rows.append({'ring': r, 'n': int(m.sum()), 'total_W': float(avg[m].sum()),
                              'Q_min': float(avg[m].min()), 'Q_mean': float(avg[m].mean()), 'Q_max': float(avg[m].max()),
                              'Tvap_min': float(tv[m].min()), 'Tvap_mean': float(tv[m].mean()), 'Tvap_max': float(tv[m].max()),
                              'Tm_max': float(tm[m].max()),
                              'margin_K': float(LIMIT_C - tv[m].max()),
                              'n_over_limit': int((tv[m] > LIMIT_C).sum()),
                              'hot_xy': [float(x) for x in pipe_xy[m][np.argmax(avg[m])]]})
        res[k] = {'rings': ring_rows, 'orbit_spread_max': float(max(spread.values())),
                  'orbit_spread_mean': float(np.mean(list(spread.values()))), 'n_orbits': len(groups),
                  'pipe_load_W': [float(v) for v in avg]}
    return res


def report(res, Tinf, L, rp):
    print(f"\nPer-pipe results   Tinf={Tinf} K   L={L} m   r_p={rp*1000:.2f} mm   limit {LIMIT_C:.0f} C")
    for k in [x for x in ('cond', 'r30', 'r25', 'r40', 'cell') if x in res]:
        r = res[k]
        tag = {'cond': 'DEFAULT: 2-D conduction through the graphite, pipes as conductance sinks (coupled)', 'r30': 'crude: pipes within 3.0 cm, weight 1/d^2', 'r25': 'pipes within 2.5 cm, weight 1/d^2', 'r40': 'pipes within 4.0 cm, weight 1/d^2',
               'cell': 'whole cell split equally over its own pipes'}[k]
        print(f"\n[{k}] {tag}   (orbits {r['n_orbits']}, max image-to-image spread {100*r['orbit_spread_max']:.1f}%)")
        print("ring  N    ringW(W)   Q_min  Q_mean  Q_max (W)   Tvap_min Tvap_mean Tvap_max   Tm_max   margin(K)  #over")
        for x in r['rings']:
            print(f"{x['ring']:>3} {x['n']:>4} {x['total_W']:>10.0f} {x['Q_min']:>7.0f} {x['Q_mean']:>7.0f} {x['Q_max']:>7.0f}"
                  f"   {x['Tvap_min']:>8.1f} {x['Tvap_mean']:>8.1f} {x['Tvap_max']:>8.1f}  {x['Tm_max']:>7.1f}  {x['margin_K']:>8.1f}  {x['n_over_limit']:>4}")


def synthetic(layout):
    """Build a fake wedge tally from known pin powers, to test the code path end to end."""
    pins, pipes = TL.pins_and_pipes(layout)
    cell_kW = {0: 50.4, 1: 47.7, 2: 63.8, 3: 77.6}
    rng = np.random.default_rng(1)
    truth = np.array([cell_kW[p['ring']] * 1e3 / 12 * (1 + 0.04 * math.cos(math.atan2(p["y"], p["x"]) * 6)) for p in pins])
    h, nx, ny, sig = 0.1, 230, 133, 0.35
    xs = (np.arange(nx) + 0.5) * h; ys = (np.arange(ny) + 0.5) * h
    Xc, Yc = np.meshgrid(xs, ys)
    field = np.zeros_like(Xc)
    for p, P in zip(pins, truth):
        field += P / (2 * math.pi * sig ** 2) * np.exp(-((Xc - p['x']) ** 2 + (Yc - p['y']) ** 2) / (2 * sig ** 2))
    # reflective-wedge tally: value at p in wedge = full-core field at p; cut voxels hold only the inside part
    mean = field * h * h * wedge_fraction(nx, ny, h)
    std = 0.02 * np.sqrt(mean * mean.max()) + 1e-12
    mean = mean * (1 + 0.02 * rng.standard_normal(mean.shape))
    return mean, std, h, pins, pipes, truth


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--npz', default='pin_tally.npz'); ap.add_argument('--layout', default='pin_layout.json')
    ap.add_argument('--Tinf', type=float, default=750.0); ap.add_argument('--L', type=float, default=1.82)
    ap.add_argument('--rp', type=float, default=0.0127); ap.add_argument('--out', default='pipe_loads.json')
    ap.add_argument('--k', type=float, default=9.92, help='graphite conductivity W/mK (as in the CFD)')
    ap.add_argument('--Lcore', type=float, default=1.6, help='active core height m')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(); a.total_W = 2.5e6

    if a.selftest:
        bad = False
        for lay in ('A', 'B'):
            mean, std, h, pins, pipes, truth = synthetic(lay)
            X, Y, P, S = unfold(mean, std, h)
            pin_P, pin_S, dropped = pin_powers(X, Y, P, S, pins)
            truth_n = truth / truth.sum() * 2.5e6
            err = np.abs(pin_P / truth_n - 1)
            ring_tot = [sum(p for p, q in zip(pin_P, pins) if q['ring'] == r) for r in range(4)]
            ring_true = [sum(p for p, q in zip(truth_n, pins) if q['ring'] == r) for r in range(4)]
            print(f"selftest layout {lay}: pin power error median {100*np.median(err):.2f}%  max {100*err.max():.2f}%  "
                  f"dropped {100*dropped:.2f}%  ring totals vs truth: " +
                  ', '.join(f"{100*(a_/b_-1):+.2f}%" for a_, b_ in zip(ring_tot, ring_true)))
            import argparse as _ap
            fa = _ap.Namespace(total_W=2.5e6, Lcore=1.6, k=9.92, rp=0.0127, L=1.82)
            share, _T = conduction_loads(X, Y, P, pipes, fa)
            _avg, _g, _sp = orbit_average(share * 2.5e6, pipes)
            print(f"   conduction split: shares sum {share.sum():.6f}, max image-to-image spread {100*max(_sp.values()):.1f}%")
            if abs(share.sum() - 1) > 1e-9 or max(_sp.values()) > 0.2:
                bad = True
            if np.median(err) > 0.03 or max(abs(a_ / b_ - 1) for a_, b_ in zip(ring_tot, ring_true)) > 0.02:
                bad = True
        print('SELFTEST', 'FAILED' if bad else 'PASSED')
        sys.exit(1 if bad else 0)

    d = np.load(a.npz); lay = json.load(open(a.layout))
    pins, pipes = lay['pins'], lay['pipes']
    print(f"layout {lay['layout']}; tally {d['mean'].shape}, {int(d['batches'])} batches ({int(d['inactive'])} inactive) x {int(d['particles'])} particles")
    X, Y, P, S = unfold(d['mean'], d['std'], float(d['voxel']))
    pin_P, pin_S, dropped = pin_powers(X, Y, P, S, pins)
    rel = pin_S / np.maximum(pin_P, 1e-9)
    print(f"pins {len(pins)}: power {pin_P.min():.0f}..{pin_P.max():.0f} W (mean {pin_P.mean():.0f}); power outside any pin's reach {100*dropped:.2f}%")
    print(f"statistical error per pin (1 sigma, voxel errors added in quadrature): median {100*np.median(rel):.2f}%, max {100*rel.max():.2f}%")
    print("ring totals from this tally vs Table 4.2 (coarse-mesh binning):")
    for r in range(4):
        t = sum(p for p, q in zip(pin_P, pins) if q['ring'] == r)
        print(f"  ring {r}: {t:>10.0f} W   Table 4.2 {TABLE42[r]:>10.0f} W   difference {100*(t/TABLE42[r]-1):+6.1f}%")
    res = analyse(pins, pipes, pin_P, a, field=(X, Y, P))
    if '_Tgmax_rel_K' in res:
        print(f"\nIndicative only (point-like hot spots make this grid-dependent, do not quote): hottest graphite point in the 2-D model is T_ref + {res['_Tgmax_rel_K']:.0f} K = {a.Tinf + GAP + res['_Tgmax_rel_K'] - 273.15:.0f} C; Table 4.5 Tmax (ring-mean CFD) is lower. Compare once real data is in.")
    report(res, a.Tinf, a.L, a.rp)
    hot = [x for x in res['cond' if 'cond' in res else 'r30']['rings']]
    print("\nCFD of the hottest pipe in each ring (default 'cond' assignment): run from 03_thermal_hydraulics")
    print("  python ivtbc_multi_ring_v10.py --counts 1 1 1 1 --L %.2f --Tinf %g --tag hotpipe --ringW %s"
          % (a.L, a.Tinf, ' '.join(f"{x['Q_max']:.1f}" for x in hot)))
    json.dump({'layout': lay['layout'], 'args': vars(a), 'pin_P': [float(v) for v in pin_P],
               'pin_rel_err': [float(v) for v in rel], 'results': res, 'pipes': pipes}, open(a.out, 'w'))
    print(f"\nwrote {a.out}")


if __name__ == '__main__':
    main()
