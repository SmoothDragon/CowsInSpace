# Cows in Space — Publication Readiness Plan

A path-finding board game on a modular hexagonal field, with rule-modifier cards and spherical cow pieces. This document tracks what exists, what must be built, and open decisions needed to move from prototype to a publishable product.

---

## 1. Product vision

**Core experience:** Real-time path-finding on a modular hex board. Players simultaneously search for the shortest path; when someone finds one, a **one-minute timer** starts, and at time-up the fastest correct path wins the round. Optional modifier cards change movement rules between games. The board is **modular** (six snub-triangle panels), so orientation and layout create many distinct playing fields.

**Manufacturing split (current intent):**

| Component | Process | Status |
|-----------|---------|--------|
| 6× snub triangle boards | Laser cut (SVG) | `SnubTriangleBoard.svg` / `.svg.py` — in progress |
| 1× center hub (“moon”) | 3D print | Not started |
| Cow pieces (×6+ sets?) | 3D print | Prototype: `spherical_cow.stl` via `spherical_cow-scad.rs` |
| Target / marker pieces | 3D print or cut | Prototypes: `frictionless_shira_target.*`, hex targets in older boards |
| Rule modifier cards | Print-on-demand or boxed deck | `CowsInSpace.pdf` from `CowsInSpace.json` + `CowsInSpace.tex.py` |

---

## 2. Playing field — six snub triangles

### 2.1 What we have

- **`SnubTriangleBoard.svg.py`** generates laser-cut/etch artwork:
  - Pointy-top hex grid clipped to an equilateral snub triangle
  - **Cut:** black perimeter, red corner house cutouts
  - **Etch:** green interior hex edges
  - **Walls:** blue interior wall lines (4 lines per walled edge; center line omitted so green shows through)
  - Parameters: `interior_side = 8`, `height_in ≈ 11.825"`, `tip_clip`, wall randomization via `wall_seed`
- Current output packs **two** snub triangles per SVG (one up, one down, sharing a long edge).
- **Six panels** form the full field; each panel is the same snub-triangle **shape and size**, but **wall placement differs** per panel (see §2.3). Rotations and hub slot assignment multiply layout variety.

### 2.2 Work needed

- [ ] **Laser sheet SVGs** — three 24″×12″ cut files, two tessellated panels per 1′×2′×⅛″ birch ply sheet (see §2.3).
- [x] **Wall manifest** — six documented `wall_seed` values; record hex, pattern, and rotation per panel (`SnubTriangleBoard-panels.json`).
- [ ] **Panel labeling:** subtle etched ID (1–6) on non-play face or edge, aligned with hub numbering.
- [ ] **Assembly diagram:** how six triangles meet at the hub (clockwise numbering, which corner points inward).
- [ ] **Layout catalog:** document recommended configurations (symmetric, asymmetric, “space curvature” wrap-friendly layouts).
- [ ] **Playtest** wall patterns for fairness (dead ends, choke points, target accessibility).

### 2.3 Decisions

**Panel geometry and walls (decided):** Six laser-cut panels from `SnubTriangleBoard.svg.py` with **identical geometry** (same `interior_side`, `height_in`, `tip_clip`, perimeter, corner cutouts, and hex grid). The only intentional cut/etch variation between panels is the **placement of the four walled interior hexes** — each panel gets a **different random** assignment (four non-adjacent allowed-interior hexes, one of each 3-wall pattern, random rotation), frozen at production time via a distinct `wall_seed` per panel 1–6.

**Production implication:** Generate **three laser-cut SVG files** (`SnubTriangleBoard-sheet-1.svg` … `-3.svg`), each sized for **24″×12″** (1′×2′ plywood laid with the long edge horizontal). Two snub triangles tessellate on each sheet (~21″×11.8″ footprint, 6 mm margin). Panel pairs: **1+2**, **3+4**, **5+6**. Identical board geometry; distinct `wall_seed` per panel. Manifest: `SnubTriangleBoard-panels.json`.

**Material (decided):** ⅛″ birch plywood; kerf compensation TBD at cut time.

### 2.4 Open questions

- Should outer perimeter walls be **identical** across panels for consistent “wrap” when using the Space Curvature card?
- Target hexes: cut circles (like `TriangleBoard.svg`), 3D printed inserts, or printed markers?

---

## 3. Center hub — “moon” connector (3D print)

### 3.1 Design intent

- Sits at the **center** where six snub triangles meet.
- Visual: **moon** (thematic; may double as “low gravity” flavor).
- **Six numbers** (1–6) around the perimeter — one per triangle slot.
- Mechanically: registers and holds panels (clips, slots, magnets, or screw bosses — TBD).

### 3.2 Work needed

- [ ] **Measure interface geometry** from snub triangle inner corner / shared-edge dimensions (export reference points from `SnubTriangleBoard.svg.py` or CAD).
- [ ] **Hub CAD model** (OpenSCAD, FreeCAD, or Fusion) with:
  - 6-fold symmetry
  - Labeled positions 1–6 (embossed or engraved)
  - Panel retention (draft angles, tolerance for FDM/SLA)
- [ ] **Prototype print** and fit test with one laser-cut panel.
- [ ] **STL + source** checked into repo (mirror pattern: `moon_hub.scad`, `moon_hub-scad.rs`, or similar).

### 3.3 Open questions

- Hub height profile: flush with board surface or raised lip?
- Magnets vs. friction fit vs. thumb screws for panel swap?
- Should numbers imply **fixed** wall orientation rules, or only **slot identity**?

---

## 4. Spherical cows (3D print)

### 4.1 What we have

- **`spherical_cow-scad.rs`** (Rust + flowscad) → OpenSCAD → **`spherical_cow.stl`**
- Stylized spherical body, legs, head; prototype subtracts **numeric text** 1–6 on the surface (not yet cow-like splotches).

### 4.2 Design intent

- Cows should read as **spherical cows**, not generic balls.
- **Six distinguishable backs** with **splotch patterns** roughly resembling **die pips** (1–6), for:
  - Player identity
  - Possibly matching hub numbers or movement values

### 4.3 Work needed

- [ ] **Replace/enhance** text cutouts with **organic splotch** geometry (SCAD modules or texture via bump map / separate overlay mesh).
- [ ] **Six STL variants** (or one parametric file with `pip_count` / `cow_id`).
- [ ] **Scale** relative to hex size (hex circumradius ~20.6 mm at current board params → cow base ~12 mm radius in prototype; verify on real board).
- [ ] **Print profile:** material (PLA/PETG), support strategy under legs, `$fn` vs. print time.
- [ ] **Color:** single material + paint vs. multi-color AMS vs. dyed splotches.
- [ ] **Quantity per box:** cows per player × player count (4? 6?).

### 4.4 Open questions

- Do pip patterns encode **player color** only, or **gameplay** (e.g. movement die)?
- Standing stability: widen foot / flatten bottom vs. accept tipping?
- Herd size and distinguishability for color-blind players (shape + pip count)?

---

## 5. Other physical components

| Item | Notes |
|------|--------|
| **Targets** | `frictionless_shira_target` / hex board cutouts — define final target count and whether they’re printed, cut, or stickers |
| **Cards** | 15+ text modifiers in `CowsInSpace.json`; PDF via `make` / `CowsInSpace.tex.py` |
| **Box** | Dimensions from nested triangles + hub + cows + cards |
| **Rulebook** | Not in repo; README is minimal |

---

## 6. Rules, balance, and playtesting

### 6.1 What we have

- README: deal 1–2 modifier cards; order matters; example modifiers listed informally.
- `CowsInSpace.json`: 15 modifier cards with names/descriptions (physics puns).
- Partial rule ideas in README (edge jump, transparent center, antipodal move).

### 6.2 Work needed

- [ ] **Complete base rules** (setup, turn structure, win condition, cow movement default, targets, collisions).
- [ ] **Modifier glossary** — how each card interacts with walls, wrap, hub layout.
- [ ] **Player count** (2–4? 2–6?) and components scaling.
- [ ] **Structured playtest log** (layout × modifiers × player count).
- [ ] **Playtime, age, complexity** targets for box back.
- [ ] **Accessibility:** color-independent cow IDs, readable card text size.

### 6.3 Decisions

| Topic | Decision |
|-------|----------|
| **Core loop** | **Real-time path-finding.** All players search the board simultaneously for the shortest path. When a path is found, a **one-minute timer** starts; at time-up, whoever found the shortest path first demonstrates it and **wins the round**. |
| **Walls** | **Blocking.** Cows may not pass through walls (base rule). |
| **Board layout × modifiers** | Interactions with modifier cards (e.g. Space Curvature wrap) **TBD** during card glossary work. |

### 6.4 Open questions

- **Player count** and session length targets?
- Win condition across rounds (first to N points, best of M rounds, etc.)?

---

## 7. Art, graphic design, and identity

- [x] Game logo and box art (“Cows in Space”) — `CowsInSpace-box-cover.png` (square lid art, 2048×2048)
- [x] Mascot character bible — `CHARACTER.md` (flying cow from box art)
- [ ] Card frame/template polish (`CowsInSpace.tex`, `graphics/`)
- [ ] Rulebook layout and illustrations (hub assembly, example layouts)
- [ ] Icon set consistency (cow symbol `\COW`, existing `graphics/` assets)
- [ ] Style guide for splotch patterns matching card/pack art

---

## 8. Manufacturing and BOM

### 8.1 Draft bill of materials (retail SKU TBD)

| Qty | Part | Process |
|-----|------|---------|
| 6 | Snub triangle panel | Laser cut |
| 1 | Moon hub | 3D print |
| N | Spherical cow (6 pip designs × copies) | 3D print |
| M | Target marker | Print or cut |
| 1 | Modifier deck (~15–30 cards) | Poker deck print |
| 1 | Rulebook | Booklet |
| 1 | Box | Custom or standard size |

### 8.2 Work needed

- [ ] Vendor quotes (laser, print farm, card printer, box).
- [ ] **Cost model** → MSRP band.
- [ ] **QC checklist** (panel flatness, hub fit, leg breakage rate).
- [ ] **Assembly instructions** (insert sheet or QR to video).

---

## 9. Legal, licensing, and publishing path

### 9.1 Current licenses (see `LICENSE`)

- **Code:** GPLv3
- **Card content:** CC-BY-NC-SA 4.0 (non-commercial)

### 9.2 Implications

- **Commercial publication** likely requires **license adjustment** for card text/art (or dual licensing decision).
- **GPL** on code may affect bundled digital rulebook apps or print pipelines — clarify what “conveying” means for your distribution model.
- **Third-party assets** in `graphics/` — verify provenance and compatibility.

### 9.3 Work needed

- [ ] Choose publishing route: self-publish (Kickstarter, Print-on-demand), small publisher, or print-and-play only.
- [ ] **Trademark** search / registration for “Cows in Space”.
- [ ] **Final license** for retail (often CC-BY-SA or all-rights-reserved for art + open STL for hub/cows optional).
- [ ] Safety/age labeling (small parts, choking hazard for cows).

---

## 10. Digital and repository hygiene

- [ ] **Release tagging** for cut files (`SnubTriangleBoard-v1.0.svg`) and STLs.
- [ ] **README** update: build instructions for board, hub, cows, cards.
- [ ] **CI or script** to regenerate SVG/STL/PDF from pinned parameters.
- [ ] Remove or gitignore bulky binaries if not needed in repo (`*.stl`, `*.3mf`) — or use Git LFS.
- [ ] **Contributing** / **CHANGELOG** if opening to collaborators.

---

## 11. Suggested phased roadmap

### Phase A — Playable prototype (4–8 weeks)

1. Finalize **six single-panel SVGs** with distinct wall seeds; laser cut six panels.
2. Draft hub v0.1; fit test.
3. Six cow STLs with pip splotches; scale on board.
4. Write base rules v0.1; playtest with fixed layout.

### Phase B — Production-ready files (4–8 weeks)

1. Freeze geometry and wall seeds; layout catalog.
2. Hub v1.0 + assembly doc.
3. Rulebook + card proof with graphic designer.
4. BOM and quote sheet.

### Phase C — Publish (8+ weeks)

1. Resolve licensing for commercial deck.
2. Kickstarter / publisher outreach OR print-and-play launch.
3. Fulfillment, QC, community feedback loop.

---

## 12. Master checklist (summary)

**Board**

- [ ] Three production laser sheet SVGs (panels 1+2, 3+4, 5+6 on 24″×12″)
- [ ] Material + kerf spec
- [ ] Panel numbering / alignment with hub

**Hub**

- [ ] Moon hub CAD + STL
- [ ] Six labeled slots; mechanical retention
- [ ] Fit validated on real panels

**Cows**

- [ ] Six pip-splotch designs on spherical cow mesh
- [ ] Print settings + quantity per box

**Cards & rules**

- [ ] Complete rulebook
- [ ] Final modifier deck content and editing pass
- [ ] Box contents list

**Business**

- [ ] License strategy for retail
- [ ] Trademark
- [ ] Pricing and fulfillment

---

## 13. Open questions (consolidated)

**Answered** (see §2.3, §6.3):

- ~~Panel uniqueness~~ → Identical geometry; six different wall placements (`wall_seed` per panel).
- ~~Core loop~~ → Real-time shortest-path rounds with one-minute timer.
- ~~Wall rules~~ → Blocking in base game.

**Still open:**

1. **Commercial license:** Keep NC on cards or relicense for retail?
2. **Cow count and pip meaning:** Cosmetic ID vs. mechanical role?
3. **Targets:** Physical form factor and count?
4. **Player count and game length** targets?
5. **Box size** constraint driving triangle `height_in` / `interior_side`?
6. **Publisher vs. self-publish** — affects component quality bar and MOQ.
7. **Digital edition** (Tabletop Simulator / print-and-play PDF only)?
8. **Hub attachment** (magnets, friction fit, flush vs. lip) and whether numbers 1–6 fix orientation or slot identity only.
9. **Perimeter wrap** consistency across panels for Space Curvature card.

---

*Last updated: decisions on panels, core loop, and walls integrated.*
