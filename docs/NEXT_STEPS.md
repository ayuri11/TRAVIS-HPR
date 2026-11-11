# Gaps and recommendations for the next work

## Inputs to settle first
- **Heat-pipe size.** The thermal model uses a 12.7 mm radius, the neutronics model 4.5 mm, and the specification 7.95 mm (15.9 mm diameter).
  Six 12.7 mm pipes do not fit the 5.5 cm cell. Fix one size and use it in both models; vapor temperature rises as 1/r_p
  (about 1,008 C in ring 3 at 7.95 mm).
- **Sink temperature.** T_inf = 750 K is provisional. Take it from the cycle (`04_power_cycle`): the PHX cold-inlet definition gives 672-739 K,
  the mean bulk sCO2 definition 773-856 K. The condenser arrangement and r2 should come from the PCHE design.
- **Operating limits.** The screening limits (entrainment governs, about 41% utilization) assume a wick and annulus geometry that is not yet specified.

## Neutronics
- keff is 0.9934 with rods out and no B4C in the model (sodium fills the rod slots). Aim for keff of about 1.02 to 1.05 with rods out and
  adequate shutdown margin with B4C inserted. Levers: zone 1 and 2 enrichment (zone 3 is at the 19.75% cap), pin radius and count,
  reflector thickness (leakage is 17.3%).
- Define B4C with the intended B-10 enrichment before using it; the material in `Define_OpenMC.py` is natural boron (20% B-10).
- The 2.4 cm tally mesh cannot resolve pins, and ring loads change by +10% / -13% / +5% (rings 1-3) with the lattice orientation.
  Run `Define_OpenMC_pin.py` and `pin_to_pipe.py` to get per-pin and per-pipe loads; ring 3 centre pipes are probably the most loaded.

## Power data
- `extract_power.py` uses a 45 cm tally half-width (the run used 60 cm) and normalizes the 1/12-wedge sum as a full core, so the absolute
  W/m3 in `data/` are 21.3x too high (multiply by 0.046875). Ring fractions and the thermal results are not affected. Correct the script
  before using the absolute values, e.g. for an OpenFOAM heat source.

## Thermal-hydraulics
- Results are per ring: a ring-mean pipe in an adiabatic unit cell with axially uniform heat. Next: per-pipe loads, a coupled multi-pipe
  model with inter-pipe heat redistribution, the axial power shape (peaking 1.32), and the in-cell graphite hot spot (fuel sits at the cell
  centre, pipes at its edge).
- `openfoam_case/0/solid/T` is needed by the driver and is not stored; create it with the entries the driver rewrites (`internalField`, `Ta`, wall `value`).
- Record the exact command line beside each result JSON in `results/`.

## Suggested objectives
Fixed: 2.5 MWth, TRISO fuel, sodium heat pipes, graphite matrix. Free: enrichment by zone, reflector, fuel pin radius and count, pipe radius
and count, active height, evaporator length, cycle parameters. Constraints: keff and shutdown margin above, leakage low, vapor temperature
below 900 C with margin, utilization of the governing limit below 50%, TRISO below 1,600 C.
