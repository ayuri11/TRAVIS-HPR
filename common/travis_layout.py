"""
travis_layout.py - pure-Python description of the TRAVIS lattice (no OpenMC needed).

Positions are taken from Define_OpenMC.py:
  - HexLattice pitch (flat-to-flat) 5.5 cm, rings 0..3 fuel-bearing (1+6+12+18 = 37 cells)
  - per cell: 12 fuel pins (6 at r=0.95 cm, angles 0,60,..; 6 at r=1.85 cm, angles 30,90,..),
              6 heat pipes at r=2.65 cm, angles 0,60,..., plus a 7th pipe at the centre in ring 3
  - unit-cell coordinates are NOT rotated by the lattice, they are offsets in the global frame.

The only thing the script cannot know is which way the lattice vectors point. Two candidates:
  'A': neighbour directions at 30,90,150,... deg   (flat sides face +/-y, corners on the x axis)
  'B': neighbour directions at 0,60,120,... deg    (flat sides face +/-x)
Define_OpenMC_pin.py tests both against the real OpenMC geometry and writes the one that matches
into pin_layout.json. Nothing downstream guesses.
"""
import math, json
import numpy as np

PITCH = 5.5
PIN_R1, PIN_R2, HP_R = 0.95, 1.85, 2.65
N_RINGS_FUEL = 4          # rings 0..3
ZONE_OF_RING = {0: 1, 1: 1, 2: 2, 3: 3}
CENTER_PIPE_RINGS = {3}   # zone 3 cells carry a 7th pipe at the cell centre


def lattice_vectors(layout):
    off = {'A': 30.0, 'B': 0.0}[layout]
    a = PITCH * np.array([math.cos(math.radians(off)), math.sin(math.radians(off))])
    b = PITCH * np.array([math.cos(math.radians(off + 60)), math.sin(math.radians(off + 60))])
    return a, b


def cells(layout):
    """All fuel-bearing cells of the full (360 deg) lattice: list of dicts."""
    a, b = lattice_vectors(layout)
    out = []
    for i in range(-N_RINGS_FUEL + 1, N_RINGS_FUEL):
        for j in range(-N_RINGS_FUEL + 1, N_RINGS_FUEL):
            ring = max(abs(i), abs(j), abs(i + j))
            if ring >= N_RINGS_FUEL:
                continue
            c = i * a + j * b
            out.append({'ring': ring, 'zone': ZONE_OF_RING[ring], 'cx': float(c[0]), 'cy': float(c[1])})
    out.sort(key=lambda d: (d['ring'], math.atan2(d['cy'], d['cx']) % (2 * math.pi)))
    for k, d in enumerate(out):
        d['cell'] = k
    return out


def pins_and_pipes(layout):
    pins, pipes = [], []
    for c in cells(layout):
        for k in range(6):
            t = math.radians(60 * k)
            pins.append({**c, 'x': c['cx'] + PIN_R1 * math.cos(t), 'y': c['cy'] + PIN_R1 * math.sin(t)})
            t = math.radians(60 * k + 30)
            pins.append({**c, 'x': c['cx'] + PIN_R2 * math.cos(t), 'y': c['cy'] + PIN_R2 * math.sin(t)})
            t = math.radians(60 * k)
            pipes.append({**c, 'x': c['cx'] + HP_R * math.cos(t), 'y': c['cy'] + HP_R * math.sin(t)})
        if c['ring'] in CENTER_PIPE_RINGS:
            pipes.append({**c, 'x': c['cx'], 'y': c['cy']})
    return pins, pipes


def fold_to_wedge(x, y):
    """Map any point to the 0..30 deg wedge using the 12-fold symmetry (6 rotations x mirror)."""
    r = np.hypot(x, y)
    th = np.mod(np.arctan2(y, x), math.radians(60.0))
    th = np.where(th > math.radians(30.0), math.radians(60.0) - th, th)
    return r * np.cos(th), r * np.sin(th)


def in_wedge(x, y, margin_deg=1.0):
    th = math.degrees(math.atan2(y, x))
    return margin_deg < th < 30.0 - margin_deg


def save_layout(layout, path='pin_layout.json'):
    pins, pipes = pins_and_pipes(layout)
    with open(path, 'w') as f:
        json.dump({'layout': layout, 'pins': pins, 'pipes': pipes}, f)
    return path


if __name__ == '__main__':
    for L in ('A', 'B'):
        p, q = pins_and_pipes(L)
        n = {}
        for d in q:
            n[d['ring']] = n.get(d['ring'], 0) + 1
        print(L, 'cells', len(cells(L)), 'pins', len(p), 'pipes', len(q), 'pipes per ring', dict(sorted(n.items())))
