//! Spherical Holstein cow — flowscad geometry emitting OpenSCAD.
//!
//! Port of the former repo-root `spherical_cow-scad.rs`.

use anyhow::Result;
use flowscad::*;

/// Default body radius (mm) sized for the current board hexes.
pub const DEFAULT_COW_R: i32 = 16;

/// Black pip dots (1–6) on the cow's back — print black on white; count is the ID.
pub fn pip_marking(count: i32, r: i32) -> D3 {
    let rf = r as f32;
    let pip = D3::sphere_r(rf * 0.11);
    let spread = rf * 0.34;
    let z = rf * 1.48;
    let mut coords: Vec<(f32, f32)> = Vec::new();
    match count {
        1 => coords.push((0.0, 0.0)),
        2 => {
            coords.push((0.0, -spread));
            coords.push((0.0, spread));
        }
        3 => {
            coords.push((0.0, -spread));
            coords.push((0.0, 0.0));
            coords.push((0.0, spread));
        }
        4 => {
            coords.extend([
                (-spread, -spread),
                (spread, -spread),
                (-spread, spread),
                (spread, spread),
            ]);
        }
        5 => {
            coords.extend([
                (-spread, -spread),
                (spread, -spread),
                (0.0, 0.0),
                (-spread, spread),
                (spread, spread),
            ]);
        }
        6 => {
            coords.extend([
                (-spread, -spread),
                (0.0, -spread),
                (spread, -spread),
                (-spread, spread),
                (0.0, spread),
                (spread, spread),
            ]);
        }
        _ => {}
    }
    coords
        .into_iter()
        .map(|(x, y)| pip.clone().translate((x, y, z)))
        .union()
}

/// Organic Holstein patch blobs — print black on white body; layout varies per cow.
pub fn holstein_patches(cow_id: i32, r: i32) -> D3 {
    let rf = r as f32;
    let blob = |sx: f32, sy: f32, sz: f32, br: f32| {
        D3::sphere_r(br).translate((sx * rf, sy * rf, sz * rf))
    };
    let layouts: &[&[(f32, f32, f32, f32)]] = &[
        &[(-0.35, 0.15, 1.05, 0.22), (0.40, -0.10, 0.95, 0.18)],
        &[
            (0.30, 0.35, 1.00, 0.20),
            (-0.45, -0.05, 0.90, 0.24),
            (0.15, -0.40, 0.85, 0.16),
        ],
        &[(-0.50, 0.20, 0.95, 0.21), (0.35, 0.0, 1.02, 0.19)],
        &[
            (0.0, 0.45, 1.08, 0.23),
            (-0.35, -0.35, 0.88, 0.17),
            (0.45, -0.20, 0.92, 0.15),
        ],
        &[(-0.30, -0.45, 0.87, 0.20), (0.42, 0.38, 1.00, 0.18)],
        &[
            (-0.48, 0.0, 0.93, 0.22),
            (0.28, -0.38, 0.86, 0.19),
            (0.22, 0.42, 1.04, 0.14),
        ],
    ];
    let idx = (cow_id.clamp(1, 6) - 1) as usize;
    layouts[idx]
        .iter()
        .map(|&(sx, sy, sz, br)| blob(sx, sy, sz, br))
        .union()
}

pub fn spherical_cow(radius: i32) -> D3 {
    let r = X(radius as f32);
    let body = D3::sphere_r(r)
        .translate_z(r * (2.0_f64.powf(-0.5)))
        .intersection(
            D3::cuboid([4.0 * radius as f64, 4.0 * radius as f64, 2.0 * radius as f64])
                .center()
                .translate_z(2 * r),
        );
    let leg = D3::sphere_r(r / 4)
        .translate(0.85 * r * v3(0.5, 0.5 * 3.0_f64.powf(0.5), 2.0_f64.powf(-0.5)))
        .add_map(|x| x.translate_z(-r))
        .hull()
        .add_map(|x| x.mirror((1, 0, 0)))
        .add_map(|x| x.mirror((0, 1, 0)))
        .intersection(D3::cube(4 * r).center().translate_z(2 * r));
    let head = D3::sphere_r(r / 2)
        .add(
            D3::sphere_r(r / 8)
                .intersection(D3::cube(4 * r).center().translate_z(2 * r))
                .rotate_y(100)
                .translate(r / 4 * v3(1, 1, 1.8))
                .add_map(|x| x.mirror((1, 0, 0))),
        )
        .translate(r * v3(0, 0.8, 0.75));
    body + leg + head
}

/// One cow with Holstein patches and pip ID `id` (1–6).
pub fn cow_with_id(id: i32, r: i32) -> D3 {
    spherical_cow(r)
        .add(holstein_patches(id, r))
        .add(pip_marking(id, r))
}

/// Six cows laid out in a 3×2 grid (same arrangement as the old script).
pub fn six_cows_sheet(r: i32) -> D3 {
    let cow = spherical_cow(r);
    (1..=6)
        .map(|id| {
            cow.clone()
                .add(holstein_patches(id, r))
                .add(pip_marking(id, r))
                .translate(((id % 3 - 1) * 40, ((id + 1) % 2) * 30, 0))
        })
        .union()
}

/// OpenSCAD source for the six-cow sheet (`$fn=64` preamble included).
pub fn six_cows_scad(r: i32) -> String {
    format!("$fn=64;\n{}", &six_cows_sheet(r))
}

/// Write OpenSCAD to `path`.
pub fn write_six_cows_scad(path: impl AsRef<std::path::Path>, r: i32) -> Result<()> {
    std::fs::write(path, six_cows_scad(r))?;
    Ok(())
}
