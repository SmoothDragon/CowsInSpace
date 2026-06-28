# Playtest component updates

Notes from table playtesting (2026) and the physical changes they drove.

---

## 1. Target die ≠ cow color

**Problem:** The octahedron target die (1–4 pips) was hard to distinguish from cow pieces when both were printed in similar white/light filament.

**Decision:**

| Component | Body color | Notes |
|-----------|------------|--------|
| **Target die** | Slate gray `#5C5C5C` | `die_octahedron_cowsinspace.scad` — 8 faces, values 1–4 (each twice) |
| **Cow bodies** | White | All six cows |
| **Cow markings** | Black Holstein patches + black pips | See §3 |
| **Active marker** | Cyan `#00ACC1` | `active_cow_marker.scad` |

Do **not** print the die in white.

---

## 2. Cow place markers (2D bases)

**Problem:** Cows were hard to track on the hex grid; needed a fixed “home” footprint per cow.

**Solution:** Flat **top-down cow silhouette** markers the 3D cow stands on.

- Generator: `CowPlaceMarker.svg.py` → `CowPlaceMarker-sheet.svg`
- Same silhouette as the spherical cow from above: round body, helmet bump, four leg bumps
- Each marker shows **Holstein black patches** and a **white pip zone with 1–6 black pips** matching its 3D cow
- Can be laser-etched on birch, printed as cardstock, or sticker-cut

**Manufacturing options (pick one for boxed game):**

1. Second laser pass on birch (etch black patches and pips)
2. Black-and-white sticker sheet (print `CowPlaceMarker-sheet.svg` at 100% scale)
3. Thin 3D-printed disks with embossed silhouette

---

## 3. White Holstein cows + pip ID (1–6)

**Problem:** Colored splotches did not match the Holstein brand; cows should read as cows first.

**Decision:**

- **Body:** white PLA/PETG for all cows
- **Patches:** **black Holstein splotches** (organic blobs on body/head; each sculpt slightly different)
- **ID:** **black pips on white** on the back — die-style layouts with **1–6 pips** (no player colors)
- **3D source:** `spherical_cow-scad.rs` — `holstein_patches()` + `pip_marking()`; print white + black (AMS or paint mask)

| Cow | Pips (ID) |
|-----|-----------|
| 1 | 1 |
| 2 | 2 |
| 3 | 3 |
| 4 | 4 |
| 5 | 5 |
| 6 | 6 |

Count alone disambiguates all six cows; Holstein patches add character at table scale.

---

## 4. Active cow marker

**Problem:** No clear indication of which cow is moving on a given turn.

**Solution:** One shared **C-ring with arrow tab** (`active_cow_marker.scad` / `ActiveCowMarker.svg`).

- Print in **cyan** — distinct from black-and-white cows and the gray die
- Place around the active cow’s place marker (or adjacent) at start of movement
- Rules should define when designation clears (end of turn, end of round, etc.)

2D reference for sticker/etch: `ActiveCowMarker.svg` from `CowPlaceMarker.svg.py`.

---

## File index

| File | Purpose |
|------|---------|
| `CowPlaceMarker.svg.py` | 2D place markers + active marker + color chart |
| `CowPlaceMarker-sheet.svg` | Six place markers (generated) |
| `ActiveCowMarker.svg` | Active-cow ring graphic (generated) |
| `ComponentColors.svg` | Print color reference (generated) |
| `spherical_cow-scad.rs` | White cow + Holstein patches + pip markings |
| `die_octahedron_cowsinspace.scad` | Gray target die |
| `active_cow_marker.scad` | Cyan active-cow ring |

Regenerate 2D assets:

```bash
python3 CowPlaceMarker.svg.py
```

Regenerate 3D STLs (requires OpenSCAD):

```bash
openscad -o die_octahedron_cowsinspace.stl die_octahedron_cowsinspace.scad
openscad -o active_cow_marker.stl active_cow_marker.scad
```
