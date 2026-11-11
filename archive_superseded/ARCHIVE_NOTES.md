# Archive of superseded files (not used for the final results; kept for history; do not build on them)

Files are unmodified copies from the original working folder.

| Folder / file | Status |
|---|---|
| neutronics/HPR_OpenMC.py, fix_fuel.py | Early versions of the OpenMC model, replaced by 01_neutronics/Define_OpenMC.py |
| power_distribution/check_ring_binning.py, _v2.py, per_ring_power_hexlattice.json | Assumed a +/-45 cm tally mesh; wrong ring loads |
| thermal/superseded_ring_binning_R45 | Ring binning at 45 cm half-width (wrong for the run) |
| power_distribution/plot_axial_temperature.py, plot_ring_temperatures.py | Plot the old uniform-assumption IVTBC result (phase3_ivtbc_results.json, 259 pipes, "AYURI" title); figures kept in figures/power_distribution/ for reference only |
| thermal/ivtbc_multi_ring.py (v5) and JSONs | Invalid: 50 s transient, not steady (energy-balance ratio about 0.35) |
| thermal/ivtbc_coupled.py, ivtbc_driver.py, ivtbc_simplified.py | Earlier drivers, replaced by 03_thermal_hydraulics/ivtbc_multi_ring_v10.py |
| thermal/ivtbc_fullwedge_perring.json, _v3_superseded.json, _v6.json, ivtbc_fullwedge_results.json, ivtbc_final_results.json, ivtbc_per_ring_results.json, ivtbc_perpipe_*.json, per_ring_power.json, design_revision_v2.json, phase3_ivtbc_results.json | Results from superseded loads or models (see docs/PROVENANCE.md) |
| thermal/r1_r2_sensitivity*.json / .png | Unverified: produced with an earlier driver; re-run before quoting |
| thermal/update_BC.py | Contains a syntax error (broken string); its function now lives inside ivtbc_multi_ring_v10.py |
