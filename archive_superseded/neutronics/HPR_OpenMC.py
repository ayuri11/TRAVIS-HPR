import numpy as np #imports NumPy as np (NumPy is the standard Python math library for arrays)
import openmc #imports OpenMC Monte Carlo neutronics library

# =============================================================================
# DEFINING MATERIALS SELECTED (line 5 -77)
# =============================================================================
# REFERENCE CODE USED: U-10Mo fuel (HEU 93%), single enrichment
# OUR HPR USES: UO2 fuel, three HALEU enrichment zones
# CHANGE: entire fuel material definition

# KEEP - same cladding material as reference (Haynes 230)
haynes = openmc.Material(name='Haynes230') # creates a new material object; name= is used to label 
haynes.set_density('g/cm3', 8.97) # sets the mass density; openmc alw is CSG units
haynes.add_element('Ni', 0.57, 'wo')  # add_element: adds a natural element; wo: weight fraction
haynes.add_element('Cr', 0.22, 'wo')
haynes.add_element('W',  0.14, 'wo')
haynes.add_element('Mo', 0.02, 'wo')
haynes.add_element('Fe', 0.01875, 'wo')
haynes.add_element('Co', 0.03125, 'wo')
# weight fraction must sum to 1; Haynes230 is made up of the stated elements in %

# KEEP - same B4C control rod as reference
# CHANGE - add B-10 enrichment 
b4c = openmc.Material(name='B4C')
b4c.set_density('g/cm3', 2.52)
b4c.add_nuclide('B10', 3.84, 'ao')  # B10 is the neutron-absorbing isotope in boron; 3.84/4 boron atoms are B10 (96%)
b4c.add_nuclide('B11', 0.16, 'ao')  # 0.16/4 of boron atoms are B11 (4%)
b4c.add_element('C',   1.0,  'ao')  # 1 carbon atom
#add_nucleotide: adds a specific isotope; ao: atomic fraction

# BeO material for axial reflector
beo = openmc.Material(name='BeO')
beo.set_density('g/cm3', 3.025)
beo.add_element('Be', 1.0, 'ao') #BeO stoich 1:1
beo.add_element('O',  1.0, 'ao')

# Be material for radial
be = openmc.Material(name='Be')
be.set_density('g/cm3', 1.85)
be.add_element('Be', 1.0, 'ao')

# KEEP - same sodium coolant as reference
sodium = openmc.Material(name='Na')
sodium.set_density('g/cm3', 0.76)
sodium.add_element('Na', 1.0, 'ao')

# CHANGE: remove U-10Mo, replace with UO2 three-zone HALEU
# CHANGE: new material - graphite moderator monolith 
graphite = openmc.Material(name='Graphite')
graphite.set_density('g/cm3', 1.7)
graphite.add_element('C', 1.0, 'ao')
graphite.add_s_alpha_beta('c_Graphite')  # Thermal scattering law: The S(α,β) table captures the crystal lattice vibration physics 

# CHANGE: Zone 1 - central region, 12% enrichment (replaces U-10Mo entirely)
fuel_zone1 = openmc.Material(name='UO2_12pct')
fuel_zone1.set_density('g/cm3', 10.4)
fuel_zone1.add_nuclide('U235', 0.12, 'ao') # 12% of uranium atoms are U235
fuel_zone1.add_nuclide('U238', 0.88, 'ao') # remaining 88% are U238
fuel_zone1.add_nuclide('O16',  2.0,  'ao') # O at ratio 2:1

# CHANGE: Zone 2 - middle region, 15% enrichment
fuel_zone2 = openmc.Material(name='UO2_15pct')
fuel_zone2.set_density('g/cm3', 10.4)
fuel_zone2.add_nuclide('U235', 0.15, 'ao') 
fuel_zone2.add_nuclide('U238', 0.85, 'ao')
fuel_zone2.add_nuclide('O16',  2.0,  'ao') #UO2 stoich 

# CHANGE: Zone 3 - outer region, 19.75% HALEU enrichment
fuel_zone3 = openmc.Material(name='UO2_1975pct')
fuel_zone3.set_density('g/cm3', 10.4)
fuel_zone3.add_nuclide('U235', 0.1975, 'ao')
fuel_zone3.add_nuclide('U238', 0.8025, 'ao')
fuel_zone3.add_nuclide('O16',  2.0,   'ao')

# 3 ZONES: The three fuel zones use increasing enrichment outward to compensate for neutron leakage at the core edge.

# create collection object of the materials
materials = openmc.Materials([
    haynes, b4c, beo, be, sodium,
    graphite, fuel_zone1, fuel_zone2, fuel_zone3
])
materials.export_to_xml() # OpenMC can't read python directly; can read xml files


# =============================================================================
# DEFINING GEOMETRY - PARAMETERS (line 86 - 110)
# =============================================================================
# REFERENCE: annular cylindrical geometry, 1/8 symmetry
# AYURI HPR: hexagonal lattice of unit cells, 1/12 symmetry

# KEEP concept: define dimensions as variables first, not hardcoded
# CHANGE: all values updated to AYURI HPR specs (units: cm)

core_height    = 160.0   # cm - active fuel
hp_radius      = 0.795   # 7.95mm OD/2 = 0.795cm
hp_wall_thick  = 0.089   # Haynes 230 wall thickness 
fuel_pin_r     = 0.635   # fuel pin radius 
ctrl_rod_r     = 0.795   # same OD as heat pipe 
cell_flat      = 5.5     # unit cell flat-to-flat 55mm 

# Axial reflector thickness 
axial_ref_top    = 12.5  # cm top BeO reflector
axial_ref_bottom = 12.5  # cm bottom BeO reflector

# Total height including reflectors: 
total_height = core_height + axial_ref_top + axial_ref_bottom 

# Radial reflector (~45cm active core radius)
core_radius      = 45.0  # defines where the graphite core ends and the BeO radial reflector begins
reflector_radius = 65.0  # outer reflector boundary


# =============================================================================
# GEOMETRY - SURFACES (line 114-150)
# in OpenMC, geometry is built by defining mathematical surfaces (planes, cylinders, spheres) 
# and then combining them with boolean operators to create regions (cells)
# =============================================================================
# REFERENCE: ZCylinder rings + ZPlanes for annular geometry
# AYURI HPR: hexagonal prism surfaces for unit cells
# CHANGE: replace ZCylinder rings with hexagonal surfaces

# ZPlanes for axial boundaries 
top_boundary    = openmc.ZPlane(z0=+total_height/2, boundary_type='vacuum')
bottom_boundary = openmc.ZPlane(z0=-total_height/2, boundary_type='vacuum')
fuel_top        = openmc.ZPlane(z0=+core_height/2)
fuel_bottom     = openmc.ZPlane(z0=-core_height/2)
top_ref_plane   = openmc.ZPlane(z0=+core_height/2)   # BeO axial reflector start
bot_ref_plane   = openmc.ZPlane(z0=-core_height/2)   # BeO axial reflector start
# openmc.ZPlane(z0=value): flat horizontal plane at height z0; defines the top & bot of reactor
# vaccuum: neutrons that reach this surface escapes; used on the outermost boundaries
# reflective: neutrons hitting this surface bounce back; for symmetry planes to simulate a full core with only 1/12 of it

# outer boundary cylinder (same concept as reference reflector_OD)
outer_boundary  = openmc.ZCylinder(r=reflector_radius, boundary_type='vacuum')

# CHANGE: symmetry planes for 1/12 hex (reference used 1/8 with 2 planes)
# 1/12 symmetry: a regular hexagon has 12-fold symmetry (6 rotational × 2 mirror)
# by modeling only a 30 deg wedge with reflective boundaries on both sides, openmc simulates the full core
# this reduces computation time by 12×
import math
angle1 = 0.0                  # 0 degrees
angle2 = math.radians(30.0)   # 30 degrees = 1/12 of 360; converts degrees to radians
sym_plane_1 = openmc.Plane(
    a=math.sin(angle1), b=-math.cos(angle1), c=0, d=0,
    boundary_type='reflective'
)
sym_plane_2 = openmc.Plane(
    a=math.sin(angle2), b=-math.cos(angle2), c=0, d=0,
    boundary_type='reflective'
)

# openmc plane abcd: general plane equation: ax + by + cz = d
# for a plane at angle θ from x-axis: a = sin(θ), b = -cos(θ), c = 0, d = 0
# the two planes are at 0° and 30° 

# =============================================================================
# GEOMETRY - UNIT CELL UNIVERSE (line 157-276)
# a Universe in OpenMC is a reusable geometry template; defined once, then places copies of it anywhere in the lattice 
# each universe contains cells (regions + materials); 
# used to build 37 identical-structure unit cells efficiently
# =============================================================================
# REFERENCE: pin_cell_universe with annular fuel rings
# AYURI HPR: hexagonal unit cell with 12 fuel pins + 6 HPs + 1 central rod
# CHANGE: completely new unit cell definition for each zone

# single heat pipe universe 
hp_inner = openmc.ZCylinder(r=hp_radius - hp_wall_thick)  # sodium vapor core
hp_outer = openmc.ZCylinder(r=hp_radius)                  # Haynes 230 wall
# outer radius - wall thickness = inner surface of HP wall 
# outer surface = outer radius

sodium_cell = openmc.Cell(fill=sodium,  region=-hp_inner) # everything inside the hp_inner (r < 0.706)
wall_cell   = openmc.Cell(fill=haynes,  region=+hp_inner & -hp_outer) # everything outside hp_inner & inside hp_outer
# -cylinder: INSIDE ( r < radius); +cylinder: OUTSIDE (r > radius)
# -plane: below the plane; +plane: above

hp_universe = openmc.Universe(cells=[sodium_cell, wall_cell])
# bundles into a universe; represents 1 complete heat pipe cross-section; 
# placed at the center of each unit cell in the hex lattice

# single fuel pin universe (CHANGE: UO2 replaces U-10Mo) 
fuel_pin_surf = openmc.ZCylinder(r=fuel_pin_r)

# Zone 1 pin (central region)
fp1_fuel = openmc.Cell(fill=fuel_zone1, region=-fuel_pin_surf)
fp1_mod  = openmc.Cell(fill=graphite,   region=+fuel_pin_surf)
fp1_universe = openmc.Universe(cells=[fp1_fuel, fp1_mod])
# +fuel_pin_surf = outside the fuel cylinder = the graphite moderator that surrounds each fuel pin
# the graphite fills everything outside the fuel pins and heat pipe in our unit cell

# Zone 2 pin (middle region)
fp2_fuel = openmc.Cell(fill=fuel_zone2, region=-fuel_pin_surf)
fp2_mod  = openmc.Cell(fill=graphite,   region=+fuel_pin_surf)
fp2_universe = openmc.Universe(cells=[fp2_fuel, fp2_mod])

# Zone 3 pin (outer region)
fp3_fuel = openmc.Cell(fill=fuel_zone3, region=-fuel_pin_surf)
fp3_mod  = openmc.Cell(fill=graphite,   region=+fuel_pin_surf)
fp3_universe = openmc.Universe(cells=[fp3_fuel, fp3_mod])

# Control rod universe = B4C adsorber + graphite mix
cr_surf = openmc.ZCylinder(r=ctrl_rod_r)
cr_cell = openmc.Cell(fill=b4c,      region=-cr_surf)
cr_mod  = openmc.Cell(fill=graphite, region=+cr_surf)
cr_universe = openmc.Universe(cells=[cr_cell, cr_mod])

# ADDED: full unit cell universe builder; places 12 fuel pins + 6 heat pipes + 1 central rod
# inside a hexagonal graphite block; replaces the solid fuel placeholders below
# pin positions: 12 pins arranged in two rings of 6 inside the hex cell
# inner ring radius ~1.5cm, outer ring radius ~2.8cm (to be confirmed from refs)
# hp positions: 6 heat pipes at corners of the hex, radius ~2.5cm from center
# EDITED: replaced placeholder zone universes with real unit cell geometry
def build_unit_cell(fp_universe, cr_universe, hp_universe, graphite):
    # fuel pin positions: 2 rings of 6 pins around the central rod
    # inner ring at r=1.4cm, outer ring at r=2.6cm — from Aldebie et al. P/D 1.15-1.25
    pin_ring1_r = 1.4   # cm — inner ring of 6 pins
    pin_ring2_r = 2.6   # cm — outer ring of 6 pins
    hp_ring_r   = 3.2   # cm — 6 heat pipes at hex corners

    cells = []

    # 6 fuel pins: inner ring
    for i in range(6):
        ang = math.radians(i * 60)
        x = pin_ring1_r * math.cos(ang)
        y = pin_ring1_r * math.sin(ang)
        pin_s = openmc.ZCylinder(x0=x, y0=y, r=fuel_pin_r)
        cells.append(openmc.Cell(fill=fp_universe, region=-pin_s))

    # 6 fuel pins: outer ring (offset 30 deg from inner)
    for i in range(6):
        ang = math.radians(i * 60 + 30)
        x = pin_ring2_r * math.cos(ang)
        y = pin_ring2_r * math.sin(ang)
        pin_s = openmc.ZCylinder(x0=x, y0=y, r=fuel_pin_r)
        cells.append(openmc.Cell(fill=fp_universe, region=-pin_s))

    # 6 heat pipes: at hex corners
    for i in range(6):
        ang = math.radians(i * 60)
        x = hp_ring_r * math.cos(ang)
        y = hp_ring_r * math.sin(ang)
        hp_s = openmc.ZCylinder(x0=x, y0=y, r=hp_radius)
        cells.append(openmc.Cell(fill=hp_universe, region=-hp_s))

    # 1 central rod (control rod for zone1, extra HP for zone3)
    cr_s = openmc.ZCylinder(x0=0, y0=0, r=ctrl_rod_r)
    cells.append(openmc.Cell(fill=cr_universe, region=-cr_s))

    # hexagonal boundary: graphite fills everything else inside the hex
    hex_prism = openmc.model.HexagonalPrism(
        edge_length=cell_flat / math.sqrt(3),
        orientation='x'
    )
    # graphite cell: inside hex AND outside all pins/HPs/central rod
    # build the exclusion region from all cylinders already added
    all_pin_surfs  = [openmc.ZCylinder(x0=pin_ring1_r*math.cos(math.radians(i*60)),
                                        y0=pin_ring1_r*math.sin(math.radians(i*60)),
                                        r=fuel_pin_r) for i in range(6)]
    all_pin_surfs += [openmc.ZCylinder(x0=pin_ring2_r*math.cos(math.radians(i*60+30)),
                                        y0=pin_ring2_r*math.sin(math.radians(i*60+30)),
                                        r=fuel_pin_r) for i in range(6)]
    all_hp_surfs   = [openmc.ZCylinder(x0=hp_ring_r*math.cos(math.radians(i*60)),
                                        y0=hp_ring_r*math.sin(math.radians(i*60)),
                                        r=hp_radius) for i in range(6)]
    cr_s2 = openmc.ZCylinder(x0=0, y0=0, r=ctrl_rod_r)

    # graphite region = inside hex, outside every pin and HP
    graphite_region = -hex_prism
    for s in all_pin_surfs + all_hp_surfs:
        graphite_region = graphite_region & +s
    graphite_region = graphite_region & +cr_s2

    cells.append(openmc.Cell(fill=graphite, region=graphite_region))

    return openmc.Universe(cells=cells)


# =============================================================================
# GEOMETRY - HEX LATTICE (line 280-326)
# places 37 unit cell universes in a regular hexagonal grid
# this is the 37-cell core arrangement with 3 enrichment zones
# =============================================================================
# REFERENCE: no lattice - single pin with angular symmetry
# AYURI HPR: HexLattice of 37 unit cells

# ADD: define the hex lattice for the full core
# 37 cells = 3 rings (R=3: 1 + 6 + 12 + 18 = 37)
# Ring 0 (center, 1 cell): Zone 1 - control rod center, 12% fuel
# Ring 1 (6 cells): Zone 1 - control rod center, 12% fuel
# Ring 2 (12 cells): Zone 2 - extra HP center, 15% fuel
# Ring 3 (18 cells): Zone 3 - extra HP center, 19.75% fuel

# EDITED: replaced solid fuel placeholders with real unit cell universes built above
# zone 1 and 2 use cr_universe as central rod; zone 3 uses hp_universe as extra central HP
zone1_univ = build_unit_cell(fp1_universe, cr_universe, hp_universe, graphite)
zone2_univ = build_unit_cell(fp2_universe, cr_universe, hp_universe, graphite)
zone3_univ = build_unit_cell(fp3_universe, hp_universe, hp_universe, graphite)
# zone3 central rod replaced with extra heat pipe (outer zone unit cells)

# ADD: HexLattice definition
lattice = openmc.HexLattice()
lattice.center = (0.0, 0.0)
lattice.pitch  = (cell_flat,)           # flat-to-flat pitch in cm
lattice.orientation = 'x'              # flat side faces x-axis

# ADD: outer universe catches particles that leave lattice boundary
outer_fill_cell = openmc.Cell(fill=be) # radial reflector
outer_univ      = openmc.Universe(cells=[outer_fill_cell])
lattice.outer   = outer_univ
# outer universe: any neutron that drifts outside the lattice boundary enters this universe (filled with BeO reflector)
# without this, OpenMC throws an error when a neutron leaves the lattice

# Ring arrangement:  OpenMC reads rings outermost first 
# Ring 3 (18 cells) = zone3, Ring 2 (12 cells) = zone2,
# Ring 1 (6 cells) = zone1, Ring 0 (1 cell) = zone1
lattice.universes = [
    [zone3_univ] * 18,   # outer ring - 19.75% HALEU; 18 copies of zone 3
    [zone2_univ] * 12,   # middle ring - 15%
    [zone1_univ] * 6,    # inner ring - 12%
    [zone1_univ],        # center cell - 12%
]

# ADD: fill the lattice into a containing cell
lattice_cell = openmc.Cell(fill=lattice)
core_universe = openmc.Universe(cells=[lattice_cell])


# =============================================================================
# GEOMETRY - ROOT CELL AND GEOMETRY EXPORT (line 330-366)
# root universe: the top-level container that holds everything else; defines the physical boundaries 
# =============================================================================
# KEEP: root cell with boundary conditions
# CHANGE: use 1/12 symmetry planes instead of 1/8

root_cell = openmc.Cell(name='root cell')
root_cell.fill   = core_universe
root_cell.region = (
    -outer_boundary      # inside the outer cylinder (r < 65cm)
    & +bottom_boundary   # above bottom plane 
    & -top_boundary      # below top plane 
    
    & +sym_plane_1       # on the correct side of plane 1; plane 1 at 0°, wedge is above
    & -sym_plane_2       # on the correct side of plane 2; at 30°, wedge is below
    # inside the 30° wedge defined by the two symmetry planes; activates the 1/12 symmetry
)

root_universe = openmc.Universe(universe_id=0, name='root universe')
root_universe.add_cell(root_cell)

# ADDED: explicit BeO axial reflector cells above and below the active core
# fills the 12.5cm gap between fuel_top/fuel_bottom and the vacuum boundary with real BeO material
# without these cells, that space is geometric void — neutrons stream through instead of reflecting
top_beo_cell = openmc.Cell(
    fill=beo,
    region=+fuel_top & -top_boundary & -outer_boundary & +sym_plane_1 & -sym_plane_2
)
bot_beo_cell = openmc.Cell(
    fill=beo,
    region=+bottom_boundary & -fuel_bottom & -outer_boundary & +sym_plane_1 & -sym_plane_2
)
root_universe.add_cell(top_beo_cell)
root_universe.add_cell(bot_beo_cell)

geometry = openmc.Geometry(root_universe)
geometry.export_to_xml()


# =============================================================================
# SETTINGS (line 370-394)
# settings that dictate how the Monte Carlo neutron simulation runs; how many neutrons, batches, where they start, physics
# =============================================================================
# KEEP: same settings structure
# CHANGE: source point moved to center of hex core

settings = openmc.Settings()
# EDITED: increased batches, inactive, and particles to production-run values 
settings.batches   = 200    # total no. of batch to simulate; increased from 100 for production run
settings.inactive  = 50     # increased from 20; more inactive batches = better fission source convergence
settings.particles = 10000  # increased from 1000; more particles = smaller uncertainty on keff and power tallies
settings.temperature['multipole'] = True # uses the multipole representation of nuclear cross-sections; 
# allows accurate Doppler broadening at any temperature, not just pre-tabulated values
settings.temperature['method']    = 'interpolation'

# CHANGE: source point at center of hex core (was at fuel_r offset in reference)
settings.source = openmc.IndependentSource(
    space=openmc.stats.Box(
        [-core_radius, -core_radius, -core_height/2],
        [ core_radius,  core_radius,  core_height/2]
# Source distribution: starting neutrons are born uniformly throughout the core box 
        # to be changed: use a point source at the center or a mesh-based source from a previous run for faster convergence
    )
)
settings.export_to_xml()


# =============================================================================
# TALLIES (line 398-422)
# defining key outputs; what is measured during the run;
# gets the power distribution that feeds into OpenFOAM's fvModels heat source
# =============================================================================
# REFERENCE: DistribcellFilter per fuel cell
# AYURI HPR: mesh tally for spatial power distribution
# CHANGE: replace per-cell tallies with regular mesh tally

# ADD: cylindrical mesh tally covering active core
# NA >= 14 axial slices
mesh = openmc.RegularMesh()    # a 3D rectangular grid overlaid on the geometry; gives a spatial map of power and flux
# 20x20 radial gives enough resolution to distinguish the 3 enrichment zones for OpenFOAM coupling
mesh.dimension = [20, 20, 14]  # 20 bins X, 20 bins Y, 14 bins Z (NA >= 14 axial slices)
mesh.lower_left  = [-core_radius, -core_radius, -core_height/2]
mesh.upper_right = [ core_radius,  core_radius,  core_height/2]
# mesh boundaries match exactly the active fuel region (not including reflectors)
mesh_filter = openmc.MeshFilter(mesh)

# KEEP concept: heating and flux tallies (same scores as reference)
tally = openmc.Tally(name='power_distribution')
tally.filters = [mesh_filter]
tally.scores  = ['heating', 'flux']   # KEEP: same as reference

tallies = openmc.Tallies([tally])
tallies.export_to_xml()

print("All XML files exported. Run: openmc") #feed into openfoam as fvModels
