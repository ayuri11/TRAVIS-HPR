# Run this to verify the correct way to define UO2 in OpenMC
import openmc

# Correct way: use add_nuclide all in ao
fuel_test = openmc.Material(name='test')
fuel_test.set_density('g/cm3', 10.4)
fuel_test.add_nuclide('U235', 0.12,  'ao')
fuel_test.add_nuclide('U238', 0.88,  'ao')
fuel_test.add_nuclide('O16',  2.0,   'ao')  # specify isotope directly
materials = openmc.Materials([fuel_test])
materials.export_to_xml()
print("done")
