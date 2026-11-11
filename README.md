# TRAVIS-HPR

TRAVIS is a 2.5 MWth sodium heat-pipe microreactor with TRISO fuel in a graphite matrix, 240 heat pipes, and a supercritical CO2 Brayton
cycle, designed for off-grid use in the Philippines. This repository holds the models, scripts and data behind the thesis results.
It is meant as the starting point for the optimization work that follows.

## Design basis
| | |
|---|---|
| Thermal power | 2.5 MWth (about 0.9 MWe) |
| Core | 1/12-symmetric hexagonal lattice, 5.5 cm pitch, 37 fuel cells in rings 0-3, Be reflector |
| Cell | 12 TRISO fuel pins, 6 sodium heat pipes (7th pipe at the centre of ring-3 cells), graphite matrix |
| Enrichment | 12% (zone 1, rings 0-1), 15% (zone 2), 19.75% (zone 3) U-235 |
| Heat pipes | 240 in rings 0-3 as 6 / 36 / 72 / 126, Haynes 230 wall |
| Neutronics | keff = 0.9934, leakage 17.3% (OpenMC, rods out) |
| Thermal reference case | l = 1.82 m, T_inf = 750 K, limiting ring 3, vapor 855.8 C, +44.2 K to the 900 C cladding limit |
| Power cycle | simple recuperated sCO2, 34.6% to 37.2% before losses |

## Layout
| Folder | Contents |
|---|---|
| `01_neutronics/` | OpenMC model (`Define_OpenMC.py`), pin-tally variant (`Define_OpenMC_pin.py`), XML inputs of the reference run |
| `02_power_distribution/` | Statepoint to W/m3 (`extract_power.py`), ring binning, per-pipe loads (`pin_to_pipe.py`), plots; results in `data/` |
| `03_thermal_hydraulics/` | Per-ring IVTBC driver (`ivtbc_multi_ring_v10.py`), OpenFOAM unit-cell case, meshing files, result JSONs |
| `04_power_cycle/` | sCO2 Brayton results used for the sink temperature |
| `common/` | `travis_layout.py`, lattice geometry shared by the pin-tally scripts |
| `figures/` | Figures produced by the scripts |
| `docs/` | `REPRODUCE.md`, `RESULTS_MAP.md`, `NEXT_STEPS.md`, `DESIGN_HISTORY.md` |
| `tools/` | `audit_repo.py`, checks a working folder before committing |

## Quick start
```
conda env create -f environment.yml && conda activate travis
python 02_power_distribution/pin_to_pipe.py --selftest
```
OpenMC and OpenFOAM are required for the full chain; see `docs/REPRODUCE.md`. Statepoints, VTK files and OpenFOAM time directories are not tracked.

## Where to start optimizing
See `docs/NEXT_STEPS.md`.

## Attribution
The neutronics script is adapted from Xiao et al. (2019), https://github.com/bearsan/Heat-Pipe-Reactor; see `THIRD_PARTY.md`.
