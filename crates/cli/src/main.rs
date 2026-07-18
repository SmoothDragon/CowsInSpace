//! `cowsinspace` — regenerate CAD and laser assets.

use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use std::path::PathBuf;

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
}

fn repo_root(cli: &Cli) -> Result<PathBuf> {
    if let Some(r) = &cli.root {
        return Ok(r.clone());
    }
    let cwd = std::env::current_dir()?;
    // Walk up looking for Cargo.toml workspace + markers/
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

fn main() -> Result<()> {
    let cli = Cli::parse();
    let root = repo_root(&cli)?;

    match cli.command {
        Commands::Cows { radius, out } => {
            let out = out.unwrap_or_else(|| root.join("cows/spherical_cow.scad"));
            if let Some(parent) = out.parent() {
                std::fs::create_dir_all(parent)?;
            }
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
            if let Some(parent) = out.parent() {
                std::fs::create_dir_all(parent)?;
            }
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
    }
    Ok(())
}
