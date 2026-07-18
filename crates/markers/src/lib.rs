//! Place markers: 16 mm white circles with 1–6 Holstein spots (CIS layout).
//!
//! Spot path data lives in `markers/cow-marker-N.svg`. This crate rewrites SVG
//! and emits DXF (CUT = circle, ENGRAVE = spots) for laser workflows.

use anyhow::{bail, Context, Result};
use cowsinspace_geom::{MARKER_DIAMETER_MM, MARKER_RADIUS_MM};
use regex::Regex;
use std::fs;
use std::path::{Path, PathBuf};

const MARGIN_MM: f64 = 0.5;
const VIEW_MM: f64 = MARKER_DIAMETER_MM + 2.0 * MARGIN_MM;
const CX: f64 = VIEW_MM / 2.0;
const CY: f64 = VIEW_MM / 2.0;

#[derive(Debug, Clone)]
pub struct Marker {
    pub id: u32,
    pub spot_paths: Vec<String>,
}

/// Load marker `id` (1–6) from `markers_dir/cow-marker-{id}.svg`.
pub fn load_marker(markers_dir: impl AsRef<Path>, id: u32) -> Result<Marker> {
    if !(1..=6).contains(&id) {
        bail!("marker id must be 1..=6, got {id}");
    }
    let path = markers_dir.as_ref().join(format!("cow-marker-{id}.svg"));
    let text = fs::read_to_string(&path).with_context(|| format!("read {}", path.display()))?;
    let re = Regex::new(r#"<path[^>]*\sd="([^"]+)""#).unwrap();
    let spot_paths: Vec<String> = re
        .captures_iter(&text)
        .map(|c| c[1].to_string())
        .collect();
    if spot_paths.len() != id as usize {
        bail!(
            "{}: expected {id} spot paths, found {}",
            path.display(),
            spot_paths.len()
        );
    }
    Ok(Marker { id, spot_paths })
}

pub fn load_all(markers_dir: impl AsRef<Path>) -> Result<Vec<Marker>> {
    (1..=6).map(|id| load_marker(&markers_dir, id)).collect()
}

/// Emit SVG for one marker (canonical 17×17 mm viewBox, 16 mm circle).
pub fn marker_svg(marker: &Marker) -> String {
    let mut out = String::new();
    out.push_str("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
    out.push_str(&format!(
        "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{VIEW_MM}mm\" height=\"{VIEW_MM}mm\" viewBox=\"0 0 {VIEW_MM} {VIEW_MM}\">\n"
    ));
    out.push_str(&format!(
        "  <circle cx=\"{CX}\" cy=\"{CY}\" r=\"{MARKER_RADIUS_MM}\" fill=\"#FFFFFF\" stroke=\"#000000\" stroke-width=\"0.25\"/>\n"
    ));
    for d in &marker.spot_paths {
        out.push_str(&format!("  <path fill=\"#000000\" d=\"{d}\"/>\n"));
    }
    out.push_str("</svg>\n");
    out
}

pub fn write_svg(marker: &Marker, path: impl AsRef<Path>) -> Result<()> {
    fs::write(path, marker_svg(marker))?;
    Ok(())
}

/// Sample SVG path `d` (M/C/Z) into polylines of (x, y) in SVG coords.
fn parse_path_d(d: &str) -> Vec<Vec<(f64, f64)>> {
    let token_re = Regex::new(r#"[MCZmcZ]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"#).unwrap();
    let tokens: Vec<&str> = token_re.find_iter(d).map(|m| m.as_str()).collect();
    let mut i = 0;
    let mut x = 0.0;
    let mut y = 0.0;
    let mut start = (0.0, 0.0);
    let mut pts: Vec<(f64, f64)> = Vec::new();
    let mut polys: Vec<Vec<(f64, f64)>> = Vec::new();

    let flush = |pts: &mut Vec<(f64, f64)>, polys: &mut Vec<Vec<(f64, f64)>>| {
        if pts.len() >= 2 {
            polys.push(std::mem::take(pts));
        } else {
            pts.clear();
        }
    };

    while i < tokens.len() {
        let t = tokens[i];
        match t {
            "M" | "m" => {
                flush(&mut pts, &mut polys);
                let abs = t == "M";
                i += 1;
                let nx: f64 = tokens[i].parse().unwrap();
                let ny: f64 = tokens[i + 1].parse().unwrap();
                i += 2;
                if abs {
                    x = nx;
                    y = ny;
                } else {
                    x += nx;
                    y += ny;
                }
                start = (x, y);
                pts.push((x, y));
                while i < tokens.len() && !matches!(tokens[i], "M" | "m" | "C" | "c" | "Z" | "z") {
                    let nx: f64 = tokens[i].parse().unwrap();
                    let ny: f64 = tokens[i + 1].parse().unwrap();
                    i += 2;
                    if abs {
                        x = nx;
                        y = ny;
                    } else {
                        x += nx;
                        y += ny;
                    }
                    pts.push((x, y));
                }
            }
            "C" | "c" => {
                let abs = t == "C";
                i += 1;
                while i < tokens.len() && !matches!(tokens[i], "M" | "m" | "C" | "c" | "Z" | "z") {
                    let mut x1: f64 = tokens[i].parse().unwrap();
                    let mut y1: f64 = tokens[i + 1].parse().unwrap();
                    let mut x2: f64 = tokens[i + 2].parse().unwrap();
                    let mut y2: f64 = tokens[i + 3].parse().unwrap();
                    let mut x3: f64 = tokens[i + 4].parse().unwrap();
                    let mut y3: f64 = tokens[i + 5].parse().unwrap();
                    i += 6;
                    if !abs {
                        x1 += x;
                        y1 += y;
                        x2 += x;
                        y2 += y;
                        x3 += x;
                        y3 += y;
                    }
                    let x0 = x;
                    let y0 = y;
                    for s in 1..=16 {
                        let u = s as f64 / 16.0;
                        let bx = (1.0 - u).powi(3) * x0
                            + 3.0 * (1.0 - u).powi(2) * u * x1
                            + 3.0 * (1.0 - u) * u.powi(2) * x2
                            + u.powi(3) * x3;
                        let by = (1.0 - u).powi(3) * y0
                            + 3.0 * (1.0 - u).powi(2) * u * y1
                            + 3.0 * (1.0 - u) * u.powi(2) * y2
                            + u.powi(3) * y3;
                        pts.push((bx, by));
                    }
                    x = x3;
                    y = y3;
                }
            }
            "Z" | "z" => {
                if pts.last() != Some(&start) {
                    pts.push(start);
                }
                flush(&mut pts, &mut polys);
                i += 1;
            }
            _ => i += 1,
        }
    }
    flush(&mut pts, &mut polys);
    polys
}

fn fmt_f(v: f64) -> String {
    format!("{v:.6}")
}

/// Write a minimal ASCII DXF (mm): CUT circle + ENGRAVE closed polylines.
pub fn write_dxf(marker: &Marker, path: impl AsRef<Path>) -> Result<()> {
    let mut entities = String::new();

    // CIRCLE on CUT (Y flipped for CAD)
    let cad_cy = VIEW_MM - CY;
    entities.push_str("  0\nCIRCLE\n  8\nCUT\n 10\n");
    entities.push_str(&fmt_f(CX));
    entities.push_str("\n 20\n");
    entities.push_str(&fmt_f(cad_cy));
    entities.push_str("\n 30\n0.0\n 40\n");
    entities.push_str(&fmt_f(MARKER_RADIUS_MM));
    entities.push('\n');

    for d in &marker.spot_paths {
        for poly in parse_path_d(d) {
            if poly.len() < 2 {
                continue;
            }
            entities.push_str("  0\nLWPOLYLINE\n  8\nENGRAVE\n 90\n");
            entities.push_str(&poly.len().to_string());
            entities.push_str("\n 70\n1\n"); // closed
            for (px, py) in &poly {
                entities.push_str(" 10\n");
                entities.push_str(&fmt_f(*px));
                entities.push_str("\n 20\n");
                entities.push_str(&fmt_f(VIEW_MM - py));
                entities.push('\n');
            }
        }
    }

    let dxf = format!(
        "  0\nSECTION\n  2\nHEADER\n  9\n$INSUNITS\n 70\n4\n  0\nENDSEC\n  0\nSECTION\n  2\nTABLES\n  0\nTABLE\n  2\nLAYER\n  0\nLAYER\n  2\nCUT\n 70\n0\n 62\n7\n  0\nLAYER\n  2\nENGRAVE\n 70\n0\n 62\n1\n  0\nENDTAB\n  0\nENDSEC\n  0\nSECTION\n  2\nENTITIES\n{entities}  0\nENDSEC\n  0\nEOF\n"
    );
    fs::write(path, dxf)?;
    Ok(())
}

/// Regenerate SVG + DXF for markers 1–6 under `markers_dir`.
pub fn emit_all(markers_dir: impl AsRef<Path>) -> Result<Vec<PathBuf>> {
    let dir = markers_dir.as_ref();
    let mut written = Vec::new();
    for id in 1..=6 {
        let marker = load_marker(dir, id)?;
        let svg_path = dir.join(format!("cow-marker-{id}.svg"));
        let dxf_path = dir.join(format!("cow-marker-{id}.dxf"));
        write_svg(&marker, &svg_path)?;
        write_dxf(&marker, &dxf_path)?;
        written.push(svg_path);
        written.push(dxf_path);
    }
    Ok(written)
}
