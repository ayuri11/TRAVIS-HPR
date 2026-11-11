# For the next researchers: what to optimize

Fixed by the thesis: 2.5 MWth, 240 heat pipes, TRISO fuel, sodium heat pipes, graphite matrix, Philippine off-grid use.

Free to change: enrichment by zone (U-235 <= 19.75%), reflector thickness, fuel-pin radius and count, pipe radius, active height,
evaporator length L, sink temperature (Brayton parameters), pipe layout.

Objectives and constraints
- keff >= about 1.02 to 1.05 with rods out (excess reactivity) and sufficient shutdown margin with B4C in
- leakage as low as possible
- heat-pipe vapour temperature + wall rise below the 900 C cladding limit with margin, heat-pipe operating limits < 50% utilization
- TRISO fuel temperature below 1600 C (verify the interior hot spot first: KNOWN_ISSUES C9)

Suggested order: fix inputs (KNOWN_ISSUES A), get keff above 1, then per-pipe loads, then optimize the thermal side.
The thermal solve takes about a minute per case and the neutronics run takes as long as the original OpenMC run.
