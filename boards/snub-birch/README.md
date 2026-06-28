# Snub triangle boards — 3 mm birch plywood 1'×2'

Production laser-cut panels for **Cows in Space**.

| | |
|---|---|
| **Material** | 3 mm birch plywood |
| **Sheet** | Nominal **1'×2'** (12" × 24"; **24" long edge horizontal**) |
| **Actual cut size** | 23.875″ × 11.875″ (⅛″ trim per dimension from nominal) |
| **Generator** | `SnubTriangleBoard.svg.py` |
| **Manifest** | `SnubTriangleBoard-panels.json` |

## Outputs

| File | Purpose |
|------|---------|
| `SnubTriangleBoard-sheet-1.svg` … `-3.svg` | Front cut sheets (panels 1+2, 3+4, 5+6) |
| `SnubTriangleBoard-sheetback-1.svg` … `-3.svg` | Back etch-only sheets |
| `SnubTriangleBoard-panel-1.svg` … `-6.svg` | Individual panel references |
| `SnubTriangleBoard.svg` | Dev preview (two tessellated panels) |

## Regenerate

```bash
python3 boards/snub-birch/SnubTriangleBoard.svg.py
```
