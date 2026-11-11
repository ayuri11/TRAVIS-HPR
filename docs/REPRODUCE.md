# Reproduce the thesis numbers

Run from the repository root with the `travis` environment active.

1. Neutronics (about the cost of one OpenMC run; commit only the XMLs and a small log):
   `cd 01_neutronics && python Define_OpenMC.py` (writes XMLs, runs OpenMC, writes `statepoint.100.h5`; the statepoint is git-ignored)
2. Power per ring: `cd ../02_power_distribution && python extract_power.py` then `python check_ring_binning_v4.py`
   (outputs go to `data/`; expects the +/-60 cm tally; the output must match `data/ring_binning_v4.json`; read KNOWN_ISSUES 3a first).
3. Thermal reference case (about 1 minute):
   `cp -r 03_thermal_hydraulics/openfoam_case ~/HPR_case` (the driver edits the case in place, so always work on a copy; recreate `0/solid/T`, see KNOWN_ISSUES 15), then
   `cd 03_thermal_hydraulics && python ivtbc_multi_ring_v10.py --case ~/HPR_case --counts 6 36 72 126 --L 1.82 --Tinf 750 --tag A182_750 --ringW 50376 286324 766044 1397256`
   Check: the printed EB ratio is between 0.98 and 1.02 for every ring.
4. Cross-checks: repeat with `--L 1.60`, `--Tinf` other, `--peak` as in `PROVENANCE.md`.
5. Per-pipe (needs a new OpenMC run): see `01_neutronics/Define_OpenMC_pin.py` and `02_power_distribution/pin_to_pipe.py`.

Fill in the exact argument lists next to each JSON in `results/` (record the command in a `.cmd` text file beside it).
