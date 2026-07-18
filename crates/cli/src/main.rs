//! `cowsinspace` — regenerate CAD and laser assets.

use anyhow::{bail, Context, Result};
use clap::{Parser, Subcommand};
use std::path::{Path, PathBuf};
use std::process::Command;

#[derive(Parser)]
#[command(name = "cowsinspace", about = "Cows in Space generators (CAD + laser)")]
struct Cli {
    /// Repository root (defaults to cwd).
    #[arg(long, global = true)]
    root: Option<PathBuf>,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Emit spherical cow OpenSCAD (six cows with Holstein + pips).
    Cows {
        /// Body radius in mm.
        #[arg(long, default_value_t = cowsinspace_cows::DEFAULT_COW_R)]
        radius: i32,
        /// Output .scad path (default: `<root>/cows/spherical_cow.scad`).
        #[arg(long)]
        out: Option<PathBuf>,
    },
    /// Point at / copy the target die OpenSCAD source.
    Dice {
        /// Copy die .scad to this path (default: leave in place, print openscad hint).
        #[arg(long)]
        out: Option<PathBuf>,
    },
    /// Emit center hub OpenSCAD.
    Centers {
        /// Output .scad path (default: `<root>/centers/frictionless_center_big.scad`).
        #[arg(long)]
        out: Option<PathBuf>,
    },
    /// Regenerate marker SVG + DXF from CIS spot paths in markers/.
    Markers {
        /// Markers directory (default: `<root>/markers`).
        #[arg(long)]
        dir: Option<PathBuf>,
    },
    /// Board info / Python regen hints (SVG not yet ported to Rust).
    Boards {
        /// snub-birch | hex-edge-acrylic | smooth-acrylic
        kind: String,
    },
    /// One-shot: write .scad sources, then mesh cows / die / hub to .stl via OpenSCAD.
    Stl {
        /// Body radius in mm for the cow sheet.
        #[arg(long, default_value_t = cowsinspace_cows::DEFAULT_COW_R)]
        radius: i32,
        /// OpenSCAD binary (default: `openscad` on PATH).
        #[arg(long, default_value = "openscad")]
        openscad: String,
    },
}

fn repo_root(cli: &Cli) -> Result<PathBuf> {
    if let Some(r) = &cli.root {
        return Ok(r.clone());
    }
    let cwd = std::env::current_dir()?;
    let mut dir = cwd.clone();
    loop {
        if dir.join("Cargo.toml").is_file() && dir.join("markers").is_dir() {
            return Ok(dir);
        }
        if !dir.pop() {
            break;
        }
    }
    Ok(cwd)
}

fn ensure_parent(path: &Path) -> Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    Ok(())
}

fn run_openscad(openscad: &str, scad: &Path, stl: &Path) -> Result<()> {
    ensure_parent(stl)?;
    println!("OpenSCAD {} → {}", scad.display(), stl.display());
    let status = Command::new(openscad)
        .arg("-o")
        .arg(stl)
        .arg(scad)
        .status()
        .with_context(|| format!("failed to run `{openscad}` (is OpenSCAD installed?)"))?;
    if !status.success() {
        bail!(
            "`{openscad}` failed for {} (exit {:?})",
            scad.display(),
            status.code()
        );
    }
    Ok(())
}

fn build_all_stl(root: &Path, radius: i32, openscad: &str) -> Result<()> {
    let cow_scad = root.join("cows/spherical_cow.scad");
    let cow_stl = root.join("cows/spherical_cow.stl");
    let die_scad = cowsinspace_dice::scad_path(root);
    let die_stl = root.join(cowsinspace_dice::DIE_STL_REL);
    let hub_scad = root.join("centers/frictionless_center_big.scad");
    let hub_stl = root.join("centers/frictionless_center_big.stl");

    ensure_parent(&cow_scad)?;
    cowsinspace_cows::write_six_cows_scad(&cow_scad, radius)?;
    println!("Wrote {}", cow_scad.display());

    cowsinspace_dice::emit_scad(root, &die_scad)?;
    println!("Die OpenSCAD: {}", die_scad.display());

    ensure_parent(&hub_scad)?;
    cowsinspace_centers::write_hub_scad(&hub_scad)?;
    println!("Wrote {}", hub_scad.display());

    run_openscad(openscad, &cow_scad, &cow_stl)?;
    run_openscad(openscad, &die_scad, &die_stl)?;
    run_openscad(openscad, &hub_scad, &hub_stl)?;

    println!();
    println!("STL outputs:");
    println!("  {}", cow_stl.display());
    println!("  {}", die_stl.display());
    println!("  {}", hub_stl.display());
    Ok(())
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let root = repo_root(&cli)?;

    match cli.command {
        Commands::Cows { radius, out } => {
            let out = out.unwrap_or_else(|| root.join("cows/spherical_cow.scad"));
            ensure_parent(&out)?;
            cowsinspace_cows::write_six_cows_scad(&out, radius)
                .with_context(|| format!("write {}", out.display()))?;
            println!("Wrote {}", out.display());
        }
        Commands::Dice { out } => {
            let dest = out.unwrap_or_else(|| cowsinspace_dice::scad_path(&root));
            cowsinspace_dice::emit_scad(&root, &dest)?;
            println!("Die OpenSCAD: {}", dest.display());
            println!("{}", cowsinspace_dice::openscad_stl_command(&root));
        }
        Commands::Centers { out } => {
            let out = out.unwrap_or_else(|| root.join("centers/frictionless_center_big.scad"));
            ensure_parent(&out)?;
            cowsinspace_centers::write_hub_scad(&out)?;
            println!("Wrote {}", out.display());
        }
        Commands::Markers { dir } => {
            let dir = dir.unwrap_or_else(|| root.join("markers"));
            let written = cowsinspace_markers::emit_all(&dir)?;
            for p in written {
                println!("Wrote {}", p.display());
            }
        }
        Commands::Boards { kind } => {
            let kind = cowsinspace_boards::BoardKind::parse(&kind)?;
            println!("{}", cowsinspace_boards::describe(kind));
        }
        Commands::Stl { radius, openscad } => {
            build_all_stl(&root, radius, &openscad)?;
        }
    }
    Ok(())
}
