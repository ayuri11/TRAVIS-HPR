# Run from the PHASE 2 folder (needs power_density_3d.npy)
import numpy as np, math, json
q = np.load('power_density_3d.npy'); nx, ny, nz = q.shape
R, P = 45.0, 5.5
dx = 2*R/nx; vol = dx*dx*(160.0/nz)*1e-6
x = np.linspace(-R+dx/2, R-dx/2, nx); xx, yy = np.meshgrid(x, x, indexing='ij')
q2 = q.sum(axis=2)*(160.0/nz)*1e-2*dx*dx*1e-4   # W per (x,y) pixel column

def circ(r):
    if r == 0: return [(0.0, 0.0)]
    return [(P*r*math.cos(math.radians(i*60/r)), P*r*math.sin(math.radians(i*60/r))) for i in range(6*r)]
def hexring(r, rot=0.0):
    if r == 0: return [(0.0, 0.0)]
    cs = [(r*P*math.cos(math.radians(60*k+rot)), r*P*math.sin(math.radians(60*k+rot))) for k in range(6)]
    return [(cs[k][0]+(cs[(k+1)%6][0]-cs[k][0])*i/r, cs[k][1]+(cs[(k+1)%6][1]-cs[k][1])*i/r) for k in range(6) for i in range(r)]

layouts = {"A: circular rings 2-3 (current)": circ,
           "B: hex lattice, neighbors at 0,60,..": lambda r: hexring(r, 0.0),
           "C: hex lattice, neighbors at 30,90,..": lambda r: hexring(r, 30.0)}

def analyse(fn):
    cen, ring = [], []
    for r in range(4):
        for c in fn(r): cen.append(c); ring.append(r)
    cen = np.array(cen); ring = np.array(ring)
    d2 = (xx[...,None]-cen[:,0])**2 + (yy[...,None]-cen[:,1])**2
    idx = d2.argmin(axis=2); owner = ring[idx]
    ring_W = [float(q2[owner == r].sum()) for r in range(4)]
    dmin = np.sqrt(d2.min(axis=2))
    fit = float((q2*dmin).sum()/q2.sum())          # power-weighted distance to nearest cell centre
    return ring_W, fit

total = q2.sum()
print(f"mesh total = {total/1e6:.4f} MW (should be 2.5000)\n")
out = {}
for name, fn in layouts.items():
    w, fit = analyse(fn); out[name] = (w, fit)
    print(name); print("   ring totals (W):", [f"{v:,.1f}" for v in w], f" sum={sum(w)/1e6:.4f} MW")
    print(f"   lattice-fit metric (lower = power sits closer to cell centres): {fit:.3f} cm\n")
best = min(out, key=lambda k: out[k][1]); print("BEST FIT:", best)
counts = [6, 36, 72, 126]; cells = [1, 6, 12, 18]
w = out[best][0]
print("\nper-pipe load (W) using best layout:", [f"{w[i]/counts[i]:,.1f}" for i in range(4)])
json.dump({"layout": best, "ring_W": w, "pipes": counts, "per_pipe_W": [w[i]/counts[i] for i in range(4)],
           "all_layouts": {k: {"ring_W": v[0], "fit_cm": v[1]} for k, v in out.items()}},
          open('per_ring_power_hexlattice.json', 'w'), indent=2)
print("saved per_ring_power_hexlattice.json")
