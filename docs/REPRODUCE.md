# Reproducing the results

Run from the repository root with the `travis` environment active (OpenMC and OpenFOAM installed).

1. **Neutronics.** `cd 01_neutronics && python Define_OpenMC.py` writes the XML inputs, runs OpenMC (100 batches, 20 inactive, 50,000 particles)
   and writes `statepoint.100.h5` and a VTK file. The reference inputs are stored in `01_neutronics/inputs/`.
2. **Power distribution.** `cd 02_power_distribution && python extract_power.py ../01_neutronics/statepoint.100.h5`, then
   `python check_ring_binning_v4.py 60`. Outputs go to `data/`; the ring totals should match `data/ring_binning_v4.json`
   (50,376 / 286,324 / 766,044 / 1,397,256 W).
3. **Thermal reference case** (about 1 minute). The solver mesh in `openfoam_case/constant/` was generated from `system/blockMeshDict` (12.7 mm pipe radius); the driver checks the mesh against `hp_radius` before running. The driver edits the OpenFOAM case in place, so work on a copy:
   ```
   cp -r 03_thermal_hydraulics/openfoam_case ~/HPR_case
   cd 03_thermal_hydraulics
   python ivtbc_multi_ring_v10.py --case ~/HPR_case --counts 6 36 72 126 --L 1.82 --Tinf 750 --tag A182_750 \
          --ringW 50376 286324 766044 1397256
   ```
   The energy-balance ratio printed for each ring should lie between 0.98 and 1.02. The cross-check cases use `--L 1.60` and `--Tinf 791`;
   the peaking case adds `--peak`.
4. **Per-pipe loads.** `python 01_neutronics/Define_OpenMC_pin.py --check`, then the full run, then
   `python 02_power_distribution/pin_to_pipe.py --Tinf 750 --L 1.82`. `--selftest` checks the post-processing without OpenMC.
5. **Plots.** `python 02_power_distribution/plot_axial_power.py` and `plot_radial_power.py` write to `figures/power_distribution/`.

## Large files
Statepoints, VTK files and OpenFOAM time directories are not in git. They are in the shared Drive folder:
https://drive.google.com/drive/folders/192V2o4moqz5ajfOQsA7exomapnlnYKfs

It holds the OpenMC statepoint and VTK export of the reference run, the converged OpenFOAM fields, the ParaView state files behind the
figures, and backups of the working folders. Put downloaded files where the scripts expect them: `statepoint.100.h5` in `01_neutronics/`.
Record the OpenMC version and cross-section library next to the statepoint.
