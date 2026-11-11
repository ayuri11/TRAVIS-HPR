# Design and modelling history (what was tried and dropped)

- **15 MWth, 259 pipes of 15.9 mm diameter**: about 57.9 kW per pipe, vapor temperature near 2,644 C. Not feasible; the geometry supports about 2.69 MWth. Power revised to 2.5 MWth.
- **2.5 MWth, 259 pipes, 4.5 mm radius**: above the cladding limit. Radius increased to 12.7 mm in the thermal model; uniform sizing at peaking 1.2 asked for 289 pipes; the lattice fixed the count at 240.
- **Ring binning on a +/-45 cm mesh**: wrong extent for the run (the tally covers +/-60 cm). Ring loads from it were discarded.
- **Early per-ring thermal driver (50 s transient)**: not at steady state (energy-balance ratio about 0.35). The current driver runs to steady state and checks the energy balance.
- **Uniform-assumption IVTBC (259 pipes)**: replaced by the per-ring solution.
- **Rod slots**: B4C is defined but the reference run fills the slots with sodium.
- **Earlier OpenMC scripts** (`HPR_OpenMC.py`, `fix_fuel.py`): replaced by `Define_OpenMC.py`. The reference run used zone-1 U-235 = 12% and a 60 cm reflector radius, which the current scripts reproduce.
- **snappyHexMesh and Gmsh meshing attempts** (STL-based pipe and fuel-pin meshes, `.geo` files): replaced by the structured `blockMesh` unit cell in `system/blockMeshDict`, which is the source of the solver mesh (12.7 mm pipe radius).
Earlier files remain available in the git history of `ayuri11/openfoam-cases`.
