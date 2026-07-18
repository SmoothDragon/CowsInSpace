//! Center hub CAD — port of `centers/old/frictionless_center_big-scad.rs`.

use anyhow::Result;
use flowscad::*;

pub fn version1() -> D3 {
    let id_hex = X(26.);
    let or_hex = id_hex / 3.0_f32.sqrt();
    let d_peg = or_hex / 3;
    let gap = X(0.4);
    let h_base = X(3.0);
    let h_peg = X(3.0);
    let inner_spread = X(44.1);
    let base = D3::chamfer_regular_polygon_prism(6, h_base, or_hex, 1)
        .rotate_z(30)
        .add(D3::cylinder_d(h_base, d_peg))
        .translate_x((inner_spread + d_peg) / 2)
        .iter_rotate((0, 0, 60), 6)
        .union()
        .add(D3::chamfer_regular_polygon_prism(6, h_base, or_hex, 1).rotate_z(30));
    let leg = D3::chamfer_regular_polygon_prism(6, h_base + h_peg, d_peg - 2 * gap, 1.2)
        .rotate_z(30)
        .translate_x((inner_spread + d_peg) / 2)
        .iter_rotate((0, 0, 60), 6)
        .union();
    let counts = (1..=6)
        .map(|x| {
            D2::text(x.to_string())
                .rotate(30)
                .translate_y(-inner_spread / 1.8)
                .rotate(30 + x * 60)
        })
        .union()
        .linear_extrude(10)
        .translate_z(-h_peg / 2)
        .rotate_y(180);
    base + leg - counts
}

pub fn version2() -> D3 {
    let id_hex = X(26.);
    let or_hex = id_hex / 3.0_f32.sqrt();
    let d_peg = or_hex / 3;
    let gap = X(0.4);
    let h_base = X(3.0);
    let h_peg = X(3.0);
    let inner_spread = X(47.);
    let base = D3::chamfer_regular_polygon_prism(6, h_base, or_hex, 1)
        .rotate_z(30)
        .add(D3::cylinder_d(h_base, d_peg))
        .translate_x((inner_spread + d_peg) / 2)
        .iter_rotate((0, 0, 60), 6)
        .union()
        .add(D3::chamfer_regular_polygon_prism(6, h_base, or_hex, 1).rotate_z(30));
    let leg = D3::chamfer_regular_polygon_prism(6, h_base + h_peg, d_peg - 2 * gap, 1.2)
        .rotate_z(30)
        .translate_x((inner_spread + d_peg) / 2)
        .iter_rotate((0, 0, 60), 6)
        .union();
    let counts = (1..=6)
        .map(|x| {
            D2::text(x.to_string())
                .rotate(30)
                .translate_y(-inner_spread / 1.8)
                .rotate(30 + x * 60)
        })
        .union()
        .linear_extrude(10)
        .translate_z(-h_peg / 2)
        .rotate_y(180);
    base + leg - counts
}

/// Default production hub geometry (version2).
pub fn hub() -> D3 {
    version2()
}

pub fn hub_scad() -> String {
    format!("$fn=64;\n{}", &hub())
}

pub fn write_hub_scad(path: impl AsRef<std::path::Path>) -> Result<()> {
    std::fs::write(path, hub_scad())?;
    Ok(())
}
