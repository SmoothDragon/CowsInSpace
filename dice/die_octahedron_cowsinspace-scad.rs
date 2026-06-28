//! Target die source — see `die_octahedron_cowsinspace.scad` (OpenSCAD).
//!
//! The playtest die is an octahedron with 1–4 pip faces. Print in slate gray,
//! not white and not player splotch colors.

use anyhow::Result;

fn main() -> Result<()> {
    eprintln!("Use die_octahedron_cowsinspace.scad — openscad -o die_octahedron_cowsinspace.stl die_octahedron_cowsinspace.scad");
    Ok(())
}
