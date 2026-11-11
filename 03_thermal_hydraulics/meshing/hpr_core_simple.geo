// HPR core - simple extrusion without layers
// Units: meters

core_height = 1.60;
hp_r        = 0.00450;
fp_r        = 0.00350;
hp_ring_r   = 0.0265;
fp1_ring_r  = 0.0095;
fp2_ring_r  = 0.0185;
wedge_r     = 0.0275;
lc_bg       = 0.004;
lc_hp       = 0.001;
lc_fp       = 0.0015;

// Wedge boundary points
Point(1) = {0, 0, 0, lc_bg};
Point(2) = {wedge_r, 0, 0, lc_bg};
Point(3) = {wedge_r*Cos(Pi/12), wedge_r*Sin(Pi/12), 0, lc_bg};
Point(4) = {wedge_r*Cos(Pi/6), wedge_r*Sin(Pi/6), 0, lc_bg};

Line(1)   = {1, 2};
Circle(2) = {2, 1, 3};
Circle(3) = {3, 1, 4};
Line(4)   = {4, 1};
Line Loop(1) = {1, 2, 3, 4};

// Heat pipe at 15 degrees
hp_x = hp_ring_r * Cos(Pi/12);
hp_y = hp_ring_r * Sin(Pi/12);
Point(10) = {hp_x,        hp_y,        0, lc_hp};
Point(11) = {hp_x+hp_r,   hp_y,        0, lc_hp};
Point(12) = {hp_x,        hp_y+hp_r,   0, lc_hp};
Point(13) = {hp_x-hp_r,   hp_y,        0, lc_hp};
Point(14) = {hp_x,        hp_y-hp_r,   0, lc_hp};
Circle(10) = {11, 10, 12};
Circle(11) = {12, 10, 13};
Circle(12) = {13, 10, 14};
Circle(13) = {14, 10, 11};
Line Loop(10) = {10, 11, 12, 13};

// Fuel pin inner ring at 15 degrees
fp1_x = fp1_ring_r * Cos(Pi/12);
fp1_y = fp1_ring_r * Sin(Pi/12);
Point(20) = {fp1_x,        fp1_y,        0, lc_fp};
Point(21) = {fp1_x+fp_r,   fp1_y,        0, lc_fp};
Point(22) = {fp1_x,        fp1_y+fp_r,   0, lc_fp};
Point(23) = {fp1_x-fp_r,   fp1_y,        0, lc_fp};
Point(24) = {fp1_x,        fp1_y-fp_r,   0, lc_fp};
Circle(20) = {21, 20, 22};
Circle(21) = {22, 20, 23};
Circle(22) = {23, 20, 24};
Circle(23) = {24, 20, 21};
Line Loop(20) = {20, 21, 22, 23};

// Fuel pin outer ring at 15 degrees
fp2_x = fp2_ring_r * Cos(Pi/12);
fp2_y = fp2_ring_r * Sin(Pi/12);
Point(30) = {fp2_x,        fp2_y,        0, lc_fp};
Point(31) = {fp2_x+fp_r,   fp2_y,        0, lc_fp};
Point(32) = {fp2_x,        fp2_y+fp_r,   0, lc_fp};
Point(33) = {fp2_x-fp_r,   fp2_y,        0, lc_fp};
Point(34) = {fp2_x,        fp2_y-fp_r,   0, lc_fp};
Circle(30) = {31, 30, 32};
Circle(31) = {32, 30, 33};
Circle(32) = {33, 30, 34};
Circle(33) = {34, 30, 31};
Line Loop(30) = {30, 31, 32, 33};

// Main graphite surface
Plane Surface(100) = {1, -10, -20, -30};

// Simple extrusion - NO layers, let gmsh mesh freely
out_g[]  = Extrude {0, 0, core_height} { Surface{100}; };
out_hp[] = Extrude {0, 0, core_height} { Surface{10}; };
out_f1[] = Extrude {0, 0, core_height} { Surface{20}; };
out_f2[] = Extrude {0, 0, core_height} { Surface{30}; };

// Physical volumes
Physical Volume("graphite") = {out_g[1]};
Physical Volume("heatPipe")  = {out_hp[1]};
Physical Volume("fuelPin1")  = {out_f1[1]};
Physical Volume("fuelPin2")  = {out_f2[1]};

// Physical surfaces for boundary conditions
Physical Surface("bottom")       = {100};
Physical Surface("top")          = {out_g[0]};
Physical Surface("sym1")         = {out_g[2]};
Physical Surface("outer")        = {out_g[3]};
Physical Surface("sym2")         = {out_g[4]};
Physical Surface("heatPipe_BC")  = {out_hp[2], out_hp[3], out_hp[4], out_hp[5]};
Physical Surface("fuelPin1_BC")  = {out_f1[2], out_f1[3], out_f1[4], out_f1[5]};
Physical Surface("fuelPin2_BC")  = {out_f2[2], out_f2[3], out_f2[4], out_f2[5]};

Mesh.Algorithm   = 6;
Mesh.Algorithm3D = 1;
Mesh.CharacteristicLengthMin = 0.0008;
Mesh.CharacteristicLengthMax = 0.005;
