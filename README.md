# CowsInSpace

A path-finding board game on a modular hexagonal grid, with rule-modifier cards and spherical cow pieces.

**Project navigation:** see [`docs/PROJECT_MAP.md`](docs/PROJECT_MAP.md) — board variants, file locations, and how pieces fit together.

| Board | Location | Notes |
|-------|----------|--------|
| **Production (laser)** | `boards/snub-birch/SnubTriangleBoard.svg.py` | 3 mm birch 1'×2' sheets, six panels |
| **Smooth circle edges (3D)** | `boards/legacy-3d-smooth/TriangleBoard.scad.py` | Union-of-circles triangle |
| **Legacy laser SVG** | `boards/legacy-2d/TriangleBoard.svg.py` | Sharp outline, red target holes |

See [`boards/README.md`](boards/README.md) and [`docs/PROJECT_MAP.md`](docs/PROJECT_MAP.md).

# How to make
Print out PDF file to make cards.

# How to play
Deal one or two cards to modify the rules.
The cards are designed to be a mapping from rules to rules, so the card order matters!
Have fun playing!

# Example card rule page
![CowsInSpace](https://github.com/SmoothDragon/CowsInSpace/blob/main/CowsInSpace.png)


# Rule modifers
-Non-target may edge jump
-transparent center
-Move to antipodal point



