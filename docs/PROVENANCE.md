# Provenance: which files back which thesis numbers

## Valid (used in Chapter 4)
| File | What it is |
|---|---|
| `01_neutronics/inputs/{materials,geometry,settings,tallies}.xml` | Authoritative inputs of the OpenMC run (dated 2026-08-11): U-235 zone 1 = 12%, zone 2 = 15%, zone 3 = 19.75%; reflector radius 60 cm; tally mesh 50x50x28 over +/-60 cm; B4C defined but unused (sodium in rod slots) |
| `02_power_distribution/ring_binning_v4.json` (`check_ring_binning_v4.py`) | Ring totals with +/-60 cm mesh; lattice layouts B and C compared |
| `03_thermal_hydraulics/results/ivtbc_fullwedge_perring_v10_A182_750.json` | **Reference design** (L = 1.82 m, T_inf = 750 K) |
| `..._v10_A160.json`, `..._v10_A182.json`, `..._v10_A182_750_pk.json` | Cross-check cases (shorter L, other T_inf, peaking) |

Per-ring loads (W, +/-60 cm binning, layout B): 50,376 / 286,324 / 766,044 / 1,397,256. Per pipe: 8,396 / 7,953 / 10,640 / 11,089.

## Superseded (do not use; kept in `archive_superseded/`)
| File | Why |
|---|---|
| `ivtbc_multi_ring.py` (v5) and its results | Invalid: a 50 s transient, not steady state (energy-balance ratio about 0.35) |
| `ivtbc_multi_ring_v6/v7/v9` scripts and JSONs | Used ring loads from a wrong mesh extent (+/-45 cm) and/or wrong lattice orientation |
| `per_ring_power_hexlattice.json`, `check_ring_binning_v1/v2/v3` | Assumed +/-45 cm mesh; v3 extent auto-detect was unreliable |

## Energy-balance check
Every thermal result must have EB ratio (wall heat out / heat injected) between 0.98 and 1.02. Valid runs: 0.999 to 1.000.
