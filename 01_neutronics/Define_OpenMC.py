"""
TRAVIS-HPR neutronics model (OpenMC).

1/12 wedge (0-30 deg, reflective sides) of a hexagonal-lattice, three-zone UO2 core with sodium heat pipes,
graphite matrix and a Be/BeO reflector. Writes the XML inputs, runs OpenMC, and exports a VTK file for ParaView.

Adapted from the KRUSTY OpenMC/Nektar++ model of Xiao et al. (2019), https://github.com/bearsan/Heat-Pipe-Reactor.
Materials, geometry and tallies were rewritten for TRAVIS.

Units: cm. Run from this folder:  python Define_OpenMC.py
"""
import numpy as np
import openmc
import math

# =============================================================================
# MATERIALS
# =============================================================================
haynes = openmc.Material(name='Haynes230')
haynes.set_density('g/cm3', 8.97)
haynes.add_element('Ni', 0.57, 'wo')
haynes.add_element('Cr', 0.22, 'wo')
haynes.add_element('W',  0.14, 'wo')
haynes.add_element('Mo', 0.02, 'wo')
haynes.add_element('Fe', 0.01875, 'wo')
haynes.add_element('Co', 0.03125, 'wo')

# B4C is defined but not used in the current model: the control-rod slots are filled with sodium (see build_unit_cell calls)
b4c = openmc.Material(name='B4C')
b4c.set_density('g/cm3', 2.52)
b4c.add_nuclide('B10', 0.80, 'ao')   # 20% of B atoms are B10
b4c.add_nuclide('B11', 3.20, 'ao')
b4c.add_element('C',   1.0,  'ao')

beo = openmc.Material(name='BeO')    # axial reflector
beo.set_density('g/cm3', 3.025)
beo.add_element('Be', 1.0, 'ao')
beo.add_element('O',  1.0, 'ao')

be = openmc.Material(name='Be')      # radial reflector
be.set_density('g/cm3', 1.85)
be.add_element('Be', 1.0, 'ao')

sodium = openmc.Material(name='Na')
sodium.set_density('g/cm3', 0.76)
sodium.add_element('Na', 1.0, 'ao')

graphite = openmc.Material(name='Graphite')
graphite.set_density('g/cm3', 1.7)
graphite.add_element('C', 1.0, 'ao')
graphite.add_s_alpha_beta('c_Graphite')

# Three UO2 zones, enrichment increasing outward to offset leakage
fuel_zone1 = openmc.Material(name='UO2_12pct')
fuel_zone1.set_density('g/cm3', 10.4)
fuel_zone1.add_nuclide('U235', 0.12, 'ao')
fuel_zone1.add_nuclide('U238', 0.88, 'ao')
fuel_zone1.add_nuclide('O16',  2.0,  'ao')

fuel_zone2 = openmc.Material(name='UO2_15pct')
fuel_zone2.set_density('g/cm3', 10.4)
fuel_zone2.add_nuclide('U235', 0.15, 'ao')
fuel_zone2.add_nuclide('U238', 0.85, 'ao')
fuel_zone2.add_nuclide('O16',  2.0,  'ao')

fuel_zone3 = openmc.Material(name='UO2_1975pct')
fuel_zone3.set_density('g/cm3', 10.4)
fuel_zone3.add_nuclide('U235', 0.1975, 'ao')
fuel_zone3.add_nuclide('U238', 0.8025, 'ao')
fuel_zone3.add_nuclide('O16',  2.0,   'ao')

materials = openmc.Materials([
    haynes, b4c, beo, be, sodium,
    graphite, fuel_zone1, fuel_zone2, fuel_zone3
])
materials.export_to_xml()


# =============================================================================
# GEOMETRY PARAMETERS (cm)
# =============================================================================
core_height    = 160.0   # active fuel height
hp_radius      = 0.450   # neutronics heat-pipe radius (reduced to fit the 5.5 cm cell; the thermal model uses 12.7 mm)
hp_wall_thick  = 0.089
fuel_pin_r     = 0.350
ctrl_rod_r     = 0.450

cell_flat      = 5.5     # unit-cell flat-to-flat pitch

axial_ref_top    = 12.5
axial_ref_bottom = 12.5
total_height = core_height + axial_ref_top + axial_ref_bottom

core_radius      = 45.0
reflector_radius = 60.0  # outer radius of the radial reflector; also sets the tally-mesh extent


# =============================================================================
# SURFACES
# =============================================================================
top_boundary    = openmc.ZPlane(z0=+total_height/2, boundary_type='vacuum')
bottom_boundary = openmc.ZPlane(z0=-total_height/2, boundary_type='vacuum')
fuel_top        = openmc.ZPlane(z0=+core_height/2)
fuel_bottom     = openmc.ZPlane(z0=-core_height/2)
top_ref_plane   = openmc.ZPlane(z0=+core_height/2)
bot_ref_plane   = openmc.ZPlane(z0=-core_height/2)

outer_boundary = openmc.ZCylinder(r=reflector_radius, boundary_type='vacuum')

# A hexagonal lattice has 12-fold symmetry, so only a 30-degree wedge with reflective sides is modelled
angle1 = 0.0
angle2 = math.radians(30.0)
sym_plane_1 = openmc.Plane(
    a=math.sin(angle1), b=-math.cos(angle1), c=0, d=0,
    boundary_type='reflective'
)
sym_plane_2 = openmc.Plane(
    a=math.sin(angle2), b=-math.cos(angle2), c=0, d=0,
    boundary_type='reflective'
)


# =============================================================================
# UNIT CELL: 12 fuel pins, 6 heat pipes at the hex corners, 1 central slot
# =============================================================================
def build_unit_cell(fuel_material, center_type, graphite_material, sodium_mat, haynes_mat, b4c_mat):
    pin_ring1_r = 0.95  # inner ring of 6 fuel pins
    pin_ring2_r = 1.85  # outer ring of 6 fuel pins (offset 30 deg)
    hp_ring_r   = 2.65  # 6 heat pipes

    cells = []
    all_cylinders = []  # outer sides of every cylinder, used to carve out the graphite background

    for i in range(6):
        ang = math.radians(i * 60)
        x0_pos = pin_ring1_r * math.cos(ang)
        y0_pos = pin_ring1_r * math.sin(ang)
        pin_s = openmc.ZCylinder(x0=x0_pos, y0=y0_pos, r=fuel_pin_r)

        cells.append(openmc.Cell(fill=fuel_material, region=-pin_s))
        all_cylinders.append(+pin_s)

    for i in range(6):
        ang = math.radians(i * 60 + 30)
        x0_pos = pin_ring2_r * math.cos(ang)
        y0_pos = pin_ring2_r * math.sin(ang)
        pin_s = openmc.ZCylinder(x0=x0_pos, y0=y0_pos, r=fuel_pin_r)

        cells.append(openmc.Cell(fill=fuel_material, region=-pin_s))
        all_cylinders.append(+pin_s)

    for i in range(6):
        ang = math.radians(i * 60)
        x0_pos = hp_ring_r * math.cos(ang)
        y0_pos = hp_ring_r * math.sin(ang)
        hp_inner_s = openmc.ZCylinder(x0=x0_pos, y0=y0_pos, r=hp_radius - hp_wall_thick)
        hp_outer_s = openmc.ZCylinder(x0=x0_pos, y0=y0_pos, r=hp_radius)

        cells.append(openmc.Cell(fill=sodium_mat, region=-hp_inner_s))
        cells.append(openmc.Cell(fill=haynes_mat, region=+hp_inner_s & -hp_outer_s))
        all_cylinders.append(+hp_outer_s)

    # Central slot: control-rod slot (zones 1, 2) or a 7th heat pipe (zone 3)
    cr_s = openmc.ZCylinder(x0=0, y0=0, r=ctrl_rod_r)
    if center_type == 'control_rod':
        cells.append(openmc.Cell(fill=b4c_mat, region=-cr_s))
    elif center_type == 'heat_pipe':
        hp_inner_c = openmc.ZCylinder(x0=0, y0=0, r=hp_radius - hp_wall_thick)
        cells.append(openmc.Cell(fill=sodium_mat, region=-hp_inner_c))
        cells.append(openmc.Cell(fill=haynes_mat, region=+hp_inner_c & -cr_s))

    all_cylinders.append(+cr_s)

    # Graphite fills the rest; the HexLattice clips it to the cell
    graphite_region = all_cylinders[0]
    for cyl in all_cylinders[1:]:
        graphite_region &= cyl

    cells.append(openmc.Cell(fill=graphite_material, region=graphite_region))

    return openmc.Universe(cells=cells)


# =============================================================================
# HEX LATTICE (rings listed outermost first)
# =============================================================================
# The b4c_mat argument receives sodium, so the control-rod slots are sodium-filled
zone1_univ = build_unit_cell(fuel_zone1, 'control_rod', graphite, sodium, haynes, sodium)
zone2_univ = build_unit_cell(fuel_zone2, 'control_rod', graphite, sodium, haynes, sodium)
zone3_univ = build_unit_cell(fuel_zone3, 'heat_pipe',   graphite, sodium, haynes, sodium)

reflector_block_univ = openmc.Universe()
reflector_block_univ.add_cell(openmc.Cell(fill=be))

lattice = openmc.HexLattice()
lattice.center = (0.0, 0.0)
lattice.pitch = (cell_flat,)
lattice.orientation = 'x'   # actual cell orientation is verified by Define_OpenMC_pin.py --check

# Anything outside the lattice is radial reflector
outer_universe = openmc.Universe()
outer_cell = openmc.Cell(fill=be)
outer_universe.add_cell(outer_cell)

lattice.outer = outer_universe

lattice.universes = [
    [reflector_block_univ] * 36, # ring 6: reflector
    [reflector_block_univ] * 30, # ring 5: reflector
    [reflector_block_univ] * 24, # ring 4: reflector
    [zone3_univ] * 18,           # ring 3: fuel zone 3 (19.75%)
    [zone2_univ] * 12,           # ring 2: fuel zone 2 (15%)
    [zone1_univ] * 6,            # ring 1: fuel zone 1 (12%)
    [zone1_univ],                # ring 0: centre cell (12%)
]

# The prism must enclose all lattice cells (corner at about 41 cm) or particles are lost
core_hex_boundary = openmc.model.HexagonalPrism(edge_length=cell_flat * 10.0, orientation='x')
core_hex = -core_hex_boundary

lattice_cell = openmc.Cell(
    fill=lattice,
    region=core_hex
)

core_universe = openmc.Universe()
core_universe.add_cell(lattice_cell)

# Wedge clipping is done only in root_cell below; clipping here as well leaves gaps and lost particles
radial_reflector_cell = openmc.Cell(
    fill=be,
    region=(
        ~core_hex
        & -outer_boundary
        & +fuel_bottom
        & -fuel_top
    )
)

core_universe.add_cell(radial_reflector_cell)


# =============================================================================
# ROOT CELL AND GEOMETRY EXPORT
# =============================================================================
root_cell = openmc.Cell(name='root cell')
root_cell.fill   = core_universe
root_cell.region = (
    -outer_boundary
    & +fuel_bottom
    & -fuel_top
    & -sym_plane_1       # y > 0
    & +sym_plane_2       # y < tan(30 deg) * x
)

root_universe = openmc.Universe(universe_id=0, name='root universe')
root_universe.add_cell(root_cell)

# Axial BeO reflectors above and below the active core
top_beo_cell = openmc.Cell(
    fill=beo,
    region=+fuel_top & -top_boundary & -outer_boundary & -sym_plane_1 & +sym_plane_2
)

bot_beo_cell = openmc.Cell(
    fill=beo,
    region=+bottom_boundary & -fuel_bottom & -outer_boundary & -sym_plane_1 & +sym_plane_2
)
root_universe.add_cell(top_beo_cell)
root_universe.add_cell(bot_beo_cell)

geometry = openmc.Geometry(root_universe)
geometry.export_to_xml()


# =============================================================================
# SETTINGS
# =============================================================================
settings = openmc.Settings()
settings.batches   = 100
settings.inactive  = 20
settings.particles = 50000

settings.temperature['multipole'] = True
settings.temperature['method']    = 'interpolation'

# Source box covers the wedge; only fissionable material is sampled
lower_left  = [0.0, 0.0, -core_height/2]
upper_right = [22.5, 13.0, core_height/2]
spatial_dist = openmc.stats.Box(lower_left, upper_right)

settings.source = openmc.IndependentSource(
    space=spatial_dist,
    constraints={'fissionable': True}
)

settings.export_to_xml()


# =============================================================================
# TALLIES: heating and flux on a 50 x 50 x 28 mesh over +/- reflector_radius (power map for the thermal model)
# =============================================================================
mesh = openmc.RegularMesh()
mesh.dimension = [50, 50, 28]
mesh.lower_left  = [-reflector_radius, -reflector_radius, -core_height/2]
mesh.upper_right = [ reflector_radius,  reflector_radius,  core_height/2]
mesh_filter = openmc.MeshFilter(mesh)

tally = openmc.Tally(name='power_distribution')
tally.filters = [mesh_filter]
tally.scores  = ['heating', 'flux']

tallies = openmc.Tallies([tally])
tallies.export_to_xml()

print("All XML files exported. Starting OpenMC simulation execution block...")

# geometry plot for visual inspection
plot = openmc.Plot()
plot.basis = 'xy'
plot.origin = (11.0, 6.0, 0.0)
plot.width = (44.0, 26.0)
plot.pixels = (1000, 500)
plot.color_by = 'material'
plots = openmc.Plots([plot])
plots.export_to_xml()
openmc.plot_geometry()

openmc.run()


# =============================================================================
# PARAVIEW VTK EXPORT
# =============================================================================
print("\nSimulation finished! Extracting 3D mesh datasets for ParaView...")

statepoint_filename = f'statepoint.{settings.batches}.h5'

with openmc.StatePoint(statepoint_filename) as sp:
    tally_output = sp.get_tally(name='power_distribution')

    flux_data = tally_output.get_values(scores=['flux']).flatten()
    heating_data = tally_output.get_values(scores=['heating']).flatten()

    mesh_geometry = tally_output.find_filter(openmc.MeshFilter).mesh

    mesh_geometry.write_data_to_vtk(
        'reactor_3d_results.vtk',
        datasets={
            'Neutron_Flux': flux_data,
            'Nuclear_Heating': heating_data
        }
    )

print("Success! 'reactor_3d_results.vtk' has been saved to working directory.")
print("Open ParaView, import this file, and look for 'Neutron_Flux' and 'Nuclear_Heating' arrays.")
