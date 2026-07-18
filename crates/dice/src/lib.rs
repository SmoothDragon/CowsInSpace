//! Target die (octahedron, 1–4 pip faces). Print slate gray — not white / cow colors.
//!
//! Geometry currently lives in OpenSCAD; this crate points at that source of truth.

use anyhow::{bail, Context, Result};
use std::path::{Path, PathBuf};

/// Relative path from the repo root to the OpenSCAD die source.
pub const DIE_SCAD_REL: &str = "dice/die_octahedron_cowsinspace.scad";

/// Relative path for the exported STL.
pub const DIE_STL_REL: &str = "dice/die_octahedron_cowsinspace.stl";

/// Resolve `DIE_SCAD_REL` under `repo_root`.
pub fn scad_path(repo_root: impl AsRef<Path>) -> PathBuf {
    repo_root.as_ref().join(DIE_SCAD_REL)
}

/// Copy the checked-in OpenSCAD die to `out` (or verify it exists when `out` is the same).
pub fn emit_scad(repo_root: impl AsRef<Path>, out: impl AsRef<Path>) -> Result<()> {
    let src = scad_path(&repo_root);
    if !src.is_file() {
        bail!("missing die OpenSCAD source: {}", src.display());
    }
    let out = out.as_ref();
    if out != src.as_path() {
        if let Some(parent) = out.parent() {
            std::fs::create_dir_all(parent)?;
        }
        std::fs::copy(&src, out)
            .with_context(|| format!("copy {} → {}", src.display(), out.display()))?;
    }
    Ok(())
}

/// Shell command hint to rebuild the STL with OpenSCAD.
pub fn openscad_stl_command(repo_root: impl AsRef<Path>) -> String {
    let root = repo_root.as_ref().display();
    format!(
        "openscad -o {root}/{DIE_STL_REL} {root}/{DIE_SCAD_REL}"
    )
}
