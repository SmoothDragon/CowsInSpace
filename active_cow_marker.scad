// Active-cow indicator — C-ring with arrow tab. Print cyan/teal (#00ACC1).
// openscad -o active_cow_marker.stl active_cow_marker.scad

$fn = 64;

outer_r = 22;
inner_r = 17.5;
h = 2.0;
gap_deg = 32;
tab_len = 8;
tab_w = 6;

module ring_sector(a0, a1) {
    difference() {
        cylinder(h = h, r = outer_r, center = false);
        translate([0, 0, -0.1])
            cylinder(h = h + 0.2, r = inner_r, center = false);
        // Gap opening toward +X
        rotate([0, 0, -gap_deg / 2])
            translate([0, -outer_r - 1, -0.1])
                cube([outer_r + tab_len + 2, outer_r + 2, h + 0.2]);
        rotate([0, 0, gap_deg / 2])
            translate([0, -outer_r - 1, -0.1])
                cube([outer_r + tab_len + 2, outer_r + 2, h + 0.2]);
    }
}

union() {
    ring_sector(0, 360);
    translate([outer_r + tab_len / 2, 0, 0])
        cube([tab_len, tab_w, h], center = true);
}
