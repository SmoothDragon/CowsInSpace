# Hex-edge triangle boards — black acrylic 16"×12"

Laser-cut panels with a **full-hex** triangular grid: every cell is a complete hexagon and the **cut line** follows the outer edges of boundary hexes only. No chamfered snub tips, no partial perimeter hexes, no corner cutouts.

Interior etch, walls, and orange pip labels use the same rules as `boards/snub-birch/`.

| | |
|---|---|
| **Material** | Black acrylic |
| **Sheet** | **16"×12"** (landscape) |
| **Layout** | Two tessellated panels per sheet (same pairing as snub-birch) |
| **Edge length** | **8 hexagons** per triangle side |
| **Generator** | `HexEdgeTriangleBoard.svg.py` |
| **Manifest** | `HexEdgeTriangleBoard-panels.json` |

## Outputs

| File | Purpose |
|------|---------|
| `HexEdgeTriangleBoard-sheet-1.svg` … `-3.svg` | Front cut sheets (panels 1+2, 3+4, 5+6); **blue** 16"×12" sheet outline |
| `HexEdgeTriangleBoard-sheetback-1.svg` … `-3.svg` | Back etch-only sheets; blue sheet outline |
| `HexEdgeTriangleBoard-panel-1.svg` … `-6.svg` | Individual panel references |
| `HexEdgeTriangleBoard.svg` | Dev preview (two tessellated panels) |

## Regenerate

```bash
.venv/bin/python boards/hex-edge-acrylic/HexEdgeTriangleBoard.svg.py
```
