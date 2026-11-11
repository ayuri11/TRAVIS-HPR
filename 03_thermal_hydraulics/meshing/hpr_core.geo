// =============================================================================
// hpr_core.geo — HPR core geometry for OpenFOAM IVTBC thermal analysis
// PHASE 3B: simplified solid graphite wedge with heat pipe boundary surfaces
// Approach: solid wedge extrusion with HP holes as embedded circles
// Units: meters
// =============================================================================

// =============================================================================
// PARAMETERS
// =============================================================================
core_height = 1.60;      // m — active fuel height
n_axial     = 28;        // axial layers (NA=28)

// heat pipe geometry
hp_r   = 0.00450;        // m — HP outer radius (4.5mm)

// pin geometry  
fp_r   = 0.00350;        // m — fuel pin radius (3.5mm)

// ring positions (from Phase 3A build_unit_cell)
hp_ring_r  = 0.0265;     // m — HP at hex corners
fp1_ring_r = 0.0095;     // m — inner fuel pins
fp2_ring_r = 0.0185;     // m — outer fuel pins

// wedge outer radius (graphite block inscribed circle)
wedge_r = 0.0275;        // m — apothem of hex cell (cell_flat/2 = 5.5/2 cm)

// mesh sizes
lc_bg  = 0.003;          // background mesh
lc_hp  = 0.0008;         // near heat pipes (fine for IVTBC BC)
lc_fp  = 0.001;          // near fuel pins

// =============================================================================
// WEDGE BOUNDARY POINTS (30 degree slice, 1/12 symmetry)
// =============================================================================
// origin
Point(1) = {0, 0, 0, lc_bg};

// symmetry plane 1: along x-axis (0 degrees)
Point(2) = {wedge_r, 0, 0, lc_bg};

// arc midpoint for meshing
Point(3) = {wedge_r*Cos(Pi/12), wedge_r*Sin(Pi/12), 0, lc_bg};

// symmetry plane 2: at 30 degrees
Point(4) = {wedge_r*Cos(Pi/6), wedge_r*Sin(Pi/6), 0, lc_bg};

// arc center (at origin)
Point(5) = {0, 0, 0, lc_bg};

// =============================================================================
// WEDGE BOUNDARY LINES
// =============================================================================
// symmetry plane 1 (along x-axis)
Line(1) = {1, 2};

// outer arc (30 degrees)
Circle(2) = {2, 5, 3};
Circle(3) = {3, 5, 4};

// symmetry plane 2 (at 30 degrees, back to origin)
Line(4) = {4, 1};

// wedge outline
Line Loop(1) = {1, 2, 3, 4};

// =============================================================================
// HEAT PIPE HOLES
// HP at 0 degrees (on symmetry plane 1) — half circle in wedge
// HP at 30 degrees (on symmetry plane 2) — half circle in wedge
// HP at 15 degrees (inside wedge) — full circle
// =============================================================================

// --- HP at 15 degrees (fully inside wedge) ---
hp_mid_x = hp_ring_r * Cos(Pi/12);   // 15 degrees
hp_mid_y = hp_ring_r * Sin(Pi/12);

Point(10) = {hp_mid_x,          hp_mid_y,          0, lc_hp};  // center
Point(11) = {hp_mid_x + hp_r,   hp_mid_y,          0, lc_hp};  // right
Point(12) = {hp_mid_x,          hp_mid_y + hp_r,   0, lc_hp};  // top
Point(13) = {hp_mid_x - hp_r,   hp_mid_y,          0, lc_hp};  // left
Point(14) = {hp_mid_x,          hp_mid_y - hp_r,   0, lc_hp};  // bottom

Circle(10) = {11, 10, 12};
Circle(11) = {12, 10, 13};
Circle(12) = {13, 10, 14};
Circle(13) = {14, 10, 11};

Line Loop(10) = {10, 11, 12, 13};
Plane Surface(10) = {10};   // HP disk surface

// =============================================================================
// FUEL PIN HOLES
// Representative fuel pins within the 30-degree wedge
// Pin at 0 degrees (on sym plane 1, half pin)
// Pin at 30 degrees (on sym plane 2, half pin)  
// Pin at 15 degrees (fully inside)
// =============================================================================

// --- Fuel pin at 15 degrees (inner ring, fully inside wedge) ---
fp1_x = fp1_ring_r * Cos(Pi/12);
fp1_y = fp1_ring_r * Sin(Pi/12);

Point(20) = {fp1_x,          fp1_y,          0, lc_fp};
Point(21) = {fp1_x + fp_r,   fp1_y,          0, lc_fp};
Point(22) = {fp1_x,          fp1_y + fp_r,   0, lc_fp};
Point(23) = {fp1_x - fp_r,   fp1_y,          0, lc_fp};
Point(24) = {fp1_x,          fp1_y - fp_r,   0, lc_fp};

Circle(20) = {21, 20, 22};
Circle(21) = {22, 20, 23};
Circle(22) = {23, 20, 24};
Circle(23) = {24, 20, 21};

Line Loop(20) = {20, 21, 22, 23};
Plane Surface(20) = {20};   // fuel pin 1 disk

// --- Fuel pin at 15 degrees (outer ring, fully inside wedge) ---
fp2_x = fp2_ring_r * Cos(Pi/12);
fp2_y = fp2_ring_r * Sin(Pi/12);

Point(30) = {fp2_x,          fp2_y,          0, lc_fp};
Point(31) = {fp2_x + fp_r,   fp2_y,          0, lc_fp};
Point(32) = {fp2_x,          fp2_y + fp_r,   0, lc_fp};
Point(33) = {fp2_x - fp_r,   fp2_y,          0, lc_fp};
Point(34) = {fp2_x,          fp2_y - fp_r,   0, lc_fp};

Circle(30) = {31, 30, 32};
Circle(31) = {32, 30, 33};
Circle(32) = {33, 30, 34};
Circle(33) = {34, 30, 31};

Line Loop(30) = {30, 31, 32, 33};
Plane Surface(30) = {30};   // fuel pin 2 disk

// =============================================================================
// MAIN GRAPHITE SURFACE
// Wedge minus heat pipe holes minus fuel pin holes
// =============================================================================
Plane Surface(100) = {1, -10, -20, -30};

// =============================================================================
// EXTRUDE TO 3D
// Simple extrusion — no recombine to avoid vertex tracking errors
// =============================================================================

// extrude graphite surface
ext_graphite[] = Extrude {0, 0, core_height} {
    Surface{100};
    Layers{n_axial};
};

// extrude HP hole (creates cylindrical surface for IVTBC BC)
ext_hp[] = Extrude {0, 0, core_height} {
    Surface{10};
    Layers{n_axial};
};

// extrude fuel pin 1
ext_fp1[] = Extrude {0, 0, core_height} {
    Surface{20};
    Layers{n_axial};
};

// extrude fuel pin 2
ext_fp2[] = Extrude {0, 0, core_height} {
    Surface{30};
    Layers{n_axial};
};

// =============================================================================
// PHYSICAL GROUPS — boundary condition labels for OpenFOAM
// =============================================================================

// solid volumes
Physical Volume("graphite") = {ext_graphite[1]};
Physical Volume("heatPipe") = {ext_hp[1]};
Physical Volume("fuelPin1") = {ext_fp1[1]};
Physical Volume("fuelPin2") = {ext_fp2[1]};

// boundary surfaces
// symmetry planes (faces 2 and 4 of wedge after extrusion)
Physical Surface("sym1") = {ext_graphite[2]};   // bottom face sym plane 1
Physical Surface("sym2") = {ext_graphite[4]};   // bottom face sym plane 2
Physical Surface("outer") = {ext_graphite[3]};  // outer arc surface

// axial faces
Physical Surface("bottom") = {100};                // z=0 face
Physical Surface("top")    = {ext_graphite[0]};    // z=core_height face

// heat pipe cylindrical surface — gets IVTBC boundary condition
Physical Surface("heatPipe_BC") = {
    ext_hp[2], ext_hp[3], ext_hp[4], ext_hp[5]
};

// fuel pin surfaces — heat generation zones
Physical Surface("fuelPin1_BC") = {
    ext_fp1[2], ext_fp1[3], ext_fp1[4], ext_fp1[5]
};
Physical Surface("fuelPin2_BC") = {
    ext_fp2[2], ext_fp2[3], ext_fp2[4], ext_fp2[5]
};

// =============================================================================
// MESH OPTIONS
// =============================================================================
Mesh.Algorithm   = 5;    // Delaunay 2D
Mesh.Algorithm3D = 1;    // Delaunay 3D (most stable)
Mesh.CharacteristicLengthMin = 0.0005;
Mesh.CharacteristicLengthMax = 0.005;

// refinement near heat pipe surfaces
Field[1] = Distance;
Field[1].NNodesByEdge = 30;
Field[1].EdgesList = {10, 11, 12, 13};   // HP circle edges

Field[2] = Threshold;
Field[2].InField    = 1;
Field[2].SizeMin    = lc_hp;
Field[2].SizeMax    = lc_bg;
Field[2].DistMin    = 0.001;
Field[2].DistMax    = 0.010;

Background Field = 2;
