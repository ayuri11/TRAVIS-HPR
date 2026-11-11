# TRAVIS-HPR

Design study of **TRAVIS**, a 2.5 MWth TRISO-fuelled, sodium heat-pipe microreactor (240 heat pipes) for off-grid use in the Philippines.
This repository holds the code and data behind the thesis results so that later researchers can reproduce and optimise them.

## Layout
| Folder | Contents |
|---|---|
| `01_neutronics/` | OpenMC model (`Define_OpenMC.py`), pin-tally variant (`Define_OpenMC_pin.py`), and the XML inputs of the run behind the thesis numbers |
| `02_power_distribution/` | Statepoint to W/m3 (`extract_power.py`), ring binning, per-pipe loads (`pin_to_pipe.py`), power plots; results in `data/` |
| `03_thermal_hydraulics/` | Per-ring IVTBC driver (`ivtbc_multi_ring_v10.py`), OpenFOAM unit-cell case, meshing files, result JSONs |
| `04_power_cycle/` | Brayton (sCO2) results used for the sink temperature |
| `common/` | `travis_layout.py`: lattice geometry shared by the pin-tally scripts |
| `figures/` | Thesis figures |
| `docs/` | **Start here:** `KNOWN_ISSUES.md`, `OPTIMIZATION_HANDOFF.md`, `PROVENANCE.md`, `REPRODUCE.md` |
| `archive_superseded/` | Old versions, kept for history only (see `ARCHIVE_NOTES.md`) |
| `tools/` | `audit_repo.py` for checking a working folder before committing |

## Quick start
```
conda env create -f environment.yml && conda activate travis
python 02_power_distribution/pin_to_pipe.py --selftest      # no OpenMC needed
```
Full reproduction steps: `docs/REPRODUCE.md`. Requires OpenMC (neutronics) and OpenFOAM (thermal case).

## Read before using the numbers
`docs/KNOWN_ISSUES.md` lists inconsistent inputs (pipe radius 12.7 mm thermal vs 4.5 mm neutronics), the provisional sink temperature,
keff = 0.9934 as modelled, and a scaling error in `extract_power.py` that makes absolute W/m3 values about 21x too high.

## Not in git
Statepoints, VTK files, OpenFOAM time directories and other large outputs are git-ignored; see `docs/REPRODUCE.md` for where to put them.

## Attribution
The neutronics script is adapted from Xiao et al. (2019), https://github.com/bearsan/Heat-Pipe-Reactor. See `THIRD_PARTY.md`. No license has been chosen yet.
