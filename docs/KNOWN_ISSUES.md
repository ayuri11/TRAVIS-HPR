# Known issues and open items (read before optimizing)

## A. Inconsistent or unsourced inputs
1. **Pipe radius.** Thermal model: 12.7 mm radius. Neutronics: 4.5 mm (scaled down in the code to fit). Six pipes of 12.7 mm radius
   need 30.4 cm2, the cell has 26.2 cm2, so the thermal pipe does not physically fit the lattice. The "1/2 inch" origin of
   12.7 mm is not traceable to the KRUSTY paper, and 1/2 inch is a diameter (6.35 mm radius). Source it or change it.
   Sensitivity: the temperature rise above the sink scales as 1/r_p (at 7.95 mm, ring 3 is about 1008 C).
2. **Sink temperature T_inf = 750 K is provisional.** It should come from the Brayton cycle (PHX cold-side inlet); a CoolProp
   snippet for this was prepared but not run.
3. **Define_OpenMC.py vs the run.** The script in the old repository had zone-1 U-235 = 0.15 and reflector radius 75 cm; the run that
   produced the results used 0.12 and 60 cm (see `01_neutronics/inputs/*.xml`). Both `Define_OpenMC.py` and `Define_OpenMC_pin.py` here
   use 0.12 / 60 (zone-1 U-235 0.12 / U-238 0.88, reflector radius 60 cm); no other code line changed. Change them deliberately if you
   want the old values.
3a. **extract_power.py scaling error (affects absolute W/m3, not ring fractions).** It assumes a 45 cm tally half-width (the run used 60 cm,
   so the voxel volume is too small and W/m3 too high by 1.78x) and normalises the 1/12-wedge sum to 2.5 MW as if it were the full core
   (12x too high). Net: saved W/m3 values are about 21.3x too high (q_max 7.82e8 in `phase1_summary.json`; corrected about 3.67e7 W/m3;
   multiply stored values by 0.046875). The script is left unchanged here so that the stored data stay reproducible; fix it before
   using `power_density_3d.npy`, `fvModels_heatSource.txt` or `phase1_summary.json` in absolute terms. Ring power fractions and the
   thermal results driven by them (`--ringW`) are not affected, because they are normalised to 2.5 MW afterwards. Thesis Section 4.1
   and Fig. 4.2 quote the affected absolute values.
3b. **B4C comment contradiction in the original model**: a comment states 96% B-10 whereas the material actually defined is 20% B-10;
   B4C is defined but unused in the run (sodium in the rod slots).

## B. Neutronics
4. **keff = 0.9934 with rods out and no B4C in the model.** The design is subcritical as modelled; no excess reactivity.
   Levers: zone 1 and 2 enrichment (zone 3 is at the 19.75% cap), fuel loading, reflector thickness.
5. **Leakage 17.3%.** Thicker Be reflector lowers it.
6. **Lattice orientation** (flat sides facing +/-y or +/-x) changes ring loads (ring 1 +10%, ring 2 -13%, ring 3 +5%) and the
   worst thermal margin (+44 K vs +31 K). `Define_OpenMC_pin.py --check` determines it from the real geometry.
7. Tally mesh extent (+/-60 cm) was confirmed from tallies.xml, not from the statepoint.

## C. Thermal-hydraulics
8. **Results are per ring, not per pipe**: ring-mean pipe, isolated adiabatic unit cell, heat uniform axially. Per-pipe loads need
   `Define_OpenMC_pin.py` + `02_power_distribution/pin_to_pipe.py` (written, tested on synthetic data only).
9. **Interior hot spot not captured.** Fuel sits in the cell centre and the pipes at its edge; a quick 2-D conduction check on
   synthetic data suggests the in-cell temperature rise is much larger than the unit-cell CFD (Table 4.5 Tmax). Verify.
10. **Operating limits are screening-level** (entrainment governs, about 41% utilization; assumed wick/annulus geometry).
11. Axial power shape not used; heat is uniform over L.
12. Ring-3 centre pipes (7th pipe) are likely the most loaded pipes. Check once per-pipe loads exist.

## D. Missing from this repository
15. `03_thermal_hydraulics/openfoam_case/0/solid/T` is not in the old repository (the driver edits it in place). Recreate it from the
    boundary-condition description in `ivtbc_multi_ring_v10.py` (`update_BC`: internalField, `Ta`, wall `value`) or copy it from the machine that ran the cases.
16. The Brayton cycle code that produced `04_power_cycle/scO2_results.json` is not in the repository, only its result and figure.
17. Exact command lines of each result JSON are not recorded (add a `.cmd` file beside each).
18. The Heat-Pipe-Reactor folder this work grew out of is derived from the Xiao et al. (2019) KRUSTY model; see `THIRD_PARTY.md`.

## E. Housekeeping
13. Figures 4.2b, 4.2c and 4.3c in the thesis are old renders; regenerate from the corrected loads.
14. Cite or remove every `[confirm ...]` tag in the manuscript.
