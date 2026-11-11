# Third-party material

The neutronics script `01_neutronics/Define_OpenMC.py` descends from the KRUSTY OpenMC/Nektar++ coupling model of
Xiao et al. (2019), distributed at https://github.com/bearsan/Heat-Pipe-Reactor. In this repository the materials, geometry,
tallies and settings were rewritten for TRAVIS; no verbatim third-party files are included. Files of the upstream project
that were deliberately left out: its README, `Image/`, `Define_Nektar.py` and `Coupling_3D_4.ipynb`.

The upstream repository states no license that we could verify. Until the authors confirm this, treat the attribution above as
required and check with the upstream authors before reusing or redistributing the adapted script outside the thesis context.

The heat-pipe wall model is from Price et al. (2023) (Eq. 7); KRUSTY data are from the KRUSTY paper provided with the thesis sources.
OpenFOAM and OpenMC are used as external tools and are not redistributed.
