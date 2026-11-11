# Which file backs which result

| Result | File |
|---|---|
| keff, leakage, simulation parameters | `01_neutronics/inputs/*.xml`, OpenMC statepoint |
| Ring power (W): 50,376 / 286,324 / 766,044 / 1,397,256 | `02_power_distribution/data/ring_binning_v4.json` (lattice orientation "x", +/-60 cm tally mesh) |
| Per-pipe load: 8,396 / 7,953 / 10,640 / 11,089 W | ring power divided by 6 / 36 / 72 / 126 pipes |
| Axial power profile | `02_power_distribution/data/axial_power_profile.csv` |
| Reference thermal case (240 pipes, l = 1.82 m, T_inf = 750 K) | `03_thermal_hydraulics/results/ivtbc_fullwedge_perring_v10_A182_750.json` |
| Cross-checks (T_inf = 791 K; l = 1.60 m) | `..._v10_A182.json`, `..._v10_A160.json` |
| Peaking sensitivity | `..._v10_A182_750_pk.json` |
| Cycle results and sink temperatures | `04_power_cycle/scO2_results.json`, `figures/power_cycle/` |

Every thermal result should have an energy-balance ratio (wall heat out / heat injected) between 0.98 and 1.02; the reference runs give 0.999 to 1.000.
