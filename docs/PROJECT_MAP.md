# Cows in Space — project map

Quick navigation for a repo that grew from several board prototypes into a production laser-cut game.

---

## Which board is which?

| What you want | Location | Output | Edge style |
|---------------|----------|--------|------------|
| **Production — 3 mm birch 1'×2'** | `boards/snub-birch/SnubTriangleBoard.svg.py` | `SnubTriangleBoard-sheet-*.svg`, `-panel-*.svg` | Chamfered tips; walls; orange pip labels |
| **Hex-edge acrylic 16"×12"** | `boards/hex-edge-acrylic/HexEdgeTriangleBoard.svg.py` | `HexEdgeTriangleBoard-panel-*.svg` | Full hexes; cut = boundary hex edges |
| **Smooth acrylic 12"×16"** | `boards/smooth-acrylic/SmoothTriangleBoard.svg.py` | `SmoothTriangleBoard-panel-*.svg` | Legacy scalloped `outer_edge`; 6 panels → 19-hex diagonal |
| **Smooth scalloped / circle edges** | `boards/legacy-3d-smooth/TriangleBoard.scad.py` | `TriangleBoard.scad`, `.stl` | Union of circles + `outer_edge()` |
| **Early laser triangle (2D)** | `boards/legacy-2d/TriangleBoard.svg.py` | `TriangleBoard.svg` | Sharp outline; red target circles |
| **Single-column hex boards** | `boards/legacy-2d/HexBoard*.svg.py` | `HexBoard*.svg` | Legacy |
| **6-panel hex hub (3D)** | `boards/legacy-3d-hub/HexBoardCenter.scad.py` | `HexBoardCenter.scad` | Legacy hub |

### Production board (snub birch)

```
boards/snub-birch/
  SnubTriangleBoard.svg.py      ← generator
  SnubTriangleBoard-panels.json ← wall seeds, sheet layout
  SnubTriangleBoard-sheet-*.svg  ← three 1'×2' cut files
  README.md                      ← material & regen notes
```

**Material:** 3 mm birch plywood, nominal **1'×2'** sheet (actual 23.875″×11.875″).

```bash
python3 boards/snub-birch/SnubTriangleBoard.svg.py
```

### Hex-edge acrylic board (16"×12")

```
boards/hex-edge-acrylic/
  HexEdgeTriangleBoard.svg.py     ← generator (6 panel SVGs + dev preview)
  HexEdgeTriangleBoard-panels.json
  README.md
```

**Material:** Black acrylic, **16"×12"** (landscape) per sheet. **Two tessellated panels per sheet** (panels 1+2, 3+4, 5+6) with sheetback etch files — same layout pattern as `boards/snub-birch/`. **8 full hexagons** per triangle edge.

```bash
.venv/bin/python boards/hex-edge-acrylic/HexEdgeTriangleBoard.svg.py
```

### Smooth acrylic board (12"×16")

```
boards/smooth-acrylic/
  SmoothTriangleBoard.svg.py      ← generator (6 panel SVGs + assembly)
  smooth_geometry.py              ← wedge clip, hub void, walls/pips
  smooth_board_2d.scad            ← OpenSCAD cut outline
  SmoothTriangleBoard-panels.json
  README.md
```

**Material:** Black acrylic, **12"×16"** per panel. Six panels → hex **19 units** on main diagonal.

```bash
.venv/bin/python boards/smooth-acrylic/SmoothTriangleBoard.svg.py
```

### Smooth circle-edge board (legacy 3D)

```
boards/legacy-3d-smooth/TriangleBoard.scad.py → TriangleBoard.scad / .stl
```

Requires `solid2`. Not the production birch laser board.

---

## Board lineage

```
boards/legacy-3d-smooth/TriangleBoard.scad.py  ──► circle-edge triangle (acrylic/print)
        │
        ├── boards/legacy-2d/TriangleBoard.svg.py  ──► flat SVG, sharp edges
        │
        └── boards/snub-birch/SnubTriangleBoard.svg.py  ──► 3 mm birch laser production
        │
        └── boards/smooth-acrylic/SmoothTriangleBoard.svg.py  ──► black acrylic, scalloped edges
        │
        └── boards/hex-edge-acrylic/HexEdgeTriangleBoard.svg.py  ──► black acrylic, hex-edge cut
```

---

## Directory layout

```
boards/
  snub-birch/           Production laser (3 mm birch 1'×2')
  smooth-acrylic/       Scalloped triangle panels (black acrylic 12"×16")
  hex-edge-acrylic/     Full-hex triangle panels (black acrylic 16"×12")
  legacy-2d/            Flat SVG prototypes
  legacy-3d-smooth/     Circle-edge OpenSCAD triangle
  legacy-3d-hub/        Hex center hub prototype

pieces/                 (at repo root today: cows, die, hub, markers)
cards/                  CowsInSpace.json, tex, pdf, graphics/
docs/                   This file, PUBLISHING_PLAN.md, PLAYTEST_COMPONENTS.md
```

---

## Other components

| Area | Key files |
|------|-----------|
| **Rules / cards** | `CowsInSpace.json`, `CowsInSpace.tex.py`, `make` |
| **Cows** | `spherical_cow-scad.rs` |
| **Place markers** | `CowPlaceMarker.svg.py` |
| **Active cow** | `active_cow_marker.scad` |
| **Target die** | `die_octahedron_cowsinspace.scad` |
| **Center hub** | `frictionless_center_big-scad.rs` |
| **Publishing** | `PUBLISHING_PLAN.md` |

---

## Entry points

| Task | Command |
|------|---------|
| Regenerate **production** birch sheets | `python3 boards/snub-birch/SnubTriangleBoard.svg.py` |
| Regenerate **smooth acrylic** panels | `.venv/bin/python boards/smooth-acrylic/SmoothTriangleBoard.svg.py` |
| Regenerate **hex-edge acrylic** panels | `.venv/bin/python boards/hex-edge-acrylic/HexEdgeTriangleBoard.svg.py` |
| Regenerate **place markers** | `python3 CowPlaceMarker.svg.py` |
| Regenerate **cards PDF** | `make` |
| Regenerate **smooth 3D triangle** | `python3 boards/legacy-3d-smooth/TriangleBoard.scad.py > boards/legacy-3d-smooth/TriangleBoard.scad` |
