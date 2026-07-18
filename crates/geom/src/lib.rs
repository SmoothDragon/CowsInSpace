//! Shared geometry helpers for Cows in Space (units: millimetres).

/// Marker / cow body circle diameter used for place markers (mm).
pub const MARKER_DIAMETER_MM: f64 = 16.0;

/// Marker circle radius (mm).
pub const MARKER_RADIUS_MM: f64 = MARKER_DIAMETER_MM / 2.0;

/// Production hex-edge acrylic circumradius R (mm). Edge length equals R for a regular hex.
pub const HEX_EDGE_ACRYLIC_R_MM: f64 = 21.29;

/// Hexagons along each triangle edge for hex-edge acrylic boards.
pub const HEX_EDGE_COUNT: u32 = 7;

/// Axial hex neighbor offsets (pointy-top style used by board generators).
pub const HEX_NEIGHBORS: [(i32, i32); 6] = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)];

/// Standard die pip centers as offsets from origin, scaled by `arm`.
pub fn pip_offsets(count: u32, arm: f64) -> Vec<(f64, f64)> {
    let c = (0.0, 0.0);
    match count {
        1 => vec![c],
        2 => vec![(0.0, -arm), (0.0, arm)],
        3 => vec![(0.0, -arm), c, (0.0, arm)],
        4 => vec![(-arm, -arm), (arm, -arm), (-arm, arm), (arm, arm)],
        5 => vec![(-arm, -arm), (arm, -arm), c, (-arm, arm), (arm, arm)],
        6 => vec![
            (-arm, -arm),
            (0.0, -arm),
            (arm, -arm),
            (-arm, arm),
            (0.0, arm),
            (arm, arm),
        ],
        _ => Vec::new(),
    }
}

/// Diagonal pip layout matching Spherical Cows / CIS markers (2 and 3 on TL–BR diagonal).
pub fn pip_offsets_diagonal(count: u32, arm: f64) -> Vec<(f64, f64)> {
    let c = (0.0, 0.0);
    match count {
        1 => vec![c],
        2 => vec![(-arm, -arm), (arm, arm)],
        3 => vec![(-arm, -arm), c, (arm, arm)],
        4 => vec![(-arm, -arm), (arm, -arm), (-arm, arm), (arm, arm)],
        5 => vec![(-arm, -arm), (arm, -arm), c, (-arm, arm), (arm, arm)],
        6 => vec![
            (-arm, -arm),
            (-arm, 0.0),
            (-arm, arm),
            (arm, -arm),
            (arm, 0.0),
            (arm, arm),
        ],
        _ => Vec::new(),
    }
}

/// Flat-to-flat width of a regular hex with circumradius `r`.
pub fn hex_flat_to_flat(r: f64) -> f64 {
    r * 3.0_f64.sqrt()
}

/// Center-to-center spacing along a row of pointy-top hexes with circumradius `r`.
pub fn hex_row_pitch(r: f64) -> f64 {
    r * 3.0_f64.sqrt()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn six_pips() {
        assert_eq!(pip_offsets(6, 1.0).len(), 6);
        assert_eq!(pip_offsets_diagonal(2, 1.0).len(), 2);
    }

    #[test]
    fn hex_edge_equals_r_note() {
        // For a regular hexagon, edge length == circumradius.
        assert!((HEX_EDGE_ACRYLIC_R_MM - 21.29).abs() < 1e-9);
    }
}
