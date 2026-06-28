// Target die — regular octahedron, 1–4 pip faces (each value on a pair of opposites).
//
// Print SLATE GRAY (#5C5C5C) — not white, not player splotch colors.
// openscad -o die_octahedron_cowsinspace.stl die_octahedron_cowsinspace.scad

$fn = 48;

edge = 18;
r = edge / (2 * sqrt(2));
pip_r = 1.35;
spread = edge * 0.18;
emboss = 0.9;
outset = 0.15;

pts = [
    [ r, 0, 0], [-r, 0, 0],
    [0,  r, 0], [0, -r, 0],
    [0, 0,  r], [0, 0, -r]
];

faces = [
    [0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4],
    [0, 3, 5], [3, 1, 5], [1, 2, 5], [2, 0, 5]
];

face_values = [1, 2, 3, 4, 1, 2, 3, 4];

function vadd(a, b) = [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
function vscale(s, v) = [s * v[0], s * v[1], s * v[2]];
function vnorm(v) = sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
function face_center(idx) =
    vscale(1 / 3, vadd(vadd(pts[faces[idx][0]], pts[faces[idx][1]]), pts[faces[idx][2]]));

module align_z(u) {
    rotate([0, 0, -atan2(u[0], u[1])])
        rotate([atan2(sqrt(u[0] * u[0] + u[1] * u[1]), u[2]), 0, 0])
            children();
}

module octahedron() {
    polyhedron(points = pts, faces = faces, convexity = 1);
}

module pip() {
    scale([1, 1, emboss / (2 * pip_r)])
        sphere(r = pip_r);
}

module face_pips(count) {
    if (count == 1) {
        pip();
    } else if (count == 2) {
        translate([0, -spread, 0]) pip();
        translate([0,  spread, 0]) pip();
    } else if (count == 3) {
        translate([0, -spread, 0]) pip();
        pip();
        translate([0,  spread, 0]) pip();
    } else if (count == 4) {
        translate([-spread, -spread, 0]) pip();
        translate([ spread, -spread, 0]) pip();
        translate([-spread,  spread, 0]) pip();
        translate([ spread,  spread, 0]) pip();
    }
}

module face_mark(idx) {
    c = face_center(idx);
    n = vscale(1 / vnorm(c), c);
    translate(vscale(outset, n))
        align_z(n)
            face_pips(face_values[idx]);
}

union() {
    octahedron();
    for (i = [0 : len(faces) - 1])
        face_mark(i);
}
