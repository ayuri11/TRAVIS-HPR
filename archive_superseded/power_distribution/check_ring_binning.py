# Run from the folder containing power_density_3d.npy (PHASE 2)
import numpy as np, math
q = np.load('power_density_3d.npy')            # (nx,ny,nz) W/m3, normalized to 2.5 MWth
nx, ny, nz = q.shape
R, P = 45.0, 5.5                               # assumed half-width of mesh (cm) and lattice pitch (cm)
dx = 2*R/nx; vol = dx*dx*(160.0/nz)*1e-6       # cell volume in m3 (assumes 160 cm tall)
x = np.linspace(-R+dx/2, R-dx/2, nx)
xx, yy = np.meshgrid(x, x, indexing='ij')

def old(r):
    if r == 0: return [(0.0, 0.0)]
    return [(P*r*math.cos(math.radians(i*60/r)), P*r*math.sin(math.radians(i*60/r))) for i in range(6*r)]
def true(r):
    if r == 0: return [(0.0, 0.0)]
    cs = [(r*P*math.cos(math.radians(60*k)), r*P*math.sin(math.radians(60*k))) for k in range(6)]
    return [(cs[k][0]+(cs[(k+1)%6][0]-cs[k][0])*i/r, cs[k][1]+(cs[(k+1)%6][1]-cs[k][1])*i/r)
            for k in range(6) for i in range(r)]

def bin_power(fn):
    cen, ring = [], []
    for r in range(4):
        for c in fn(r): cen.append(c); ring.append(r)
    cen = np.array(cen); ring = np.array(ring)
    d2 = (xx[...,None]-cen[:,0])**2 + (yy[...,None]-cen[:,1])**2
    owner = ring[d2.argmin(axis=2)]
    return [q[owner == r].sum()*vol for r in range(4)]

total = q.sum()*vol
print(f"mesh total = {total/1e6:.4f} MW (should be 2.5000)")
if abs(total-2.5e6) > 0.02*2.5e6:
    print("!! WARNING: total is not 2.5 MW -> the mesh extent assumed here (R=45 cm, 160 cm tall) is probably wrong.")
    print("   Send me: head -40 extract_power.py   and I will correct the extents.")
res = {}
for name, fn in [("current (circular rings 2-3)", old), ("true hex-ring layout", true)]:
    t = bin_power(fn); res[name] = t
    print(f"{name:30s}", [f"{v/1e3:,.1f} kW" for v in t], f"sum={sum(t)/1e6:.4f} MW")
a, b = res["current (circular rings 2-3)"], res["true hex-ring layout"]
print("\nchange per ring (true - current):", [f"{(y-x)/1e3:+,.1f} kW ({(y-x)/max(x,1)*100:+.1f}%)" for x, y in zip(a, b)])
