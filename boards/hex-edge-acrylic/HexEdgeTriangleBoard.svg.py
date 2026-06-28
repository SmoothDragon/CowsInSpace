#!/usr/bin/env python3
"""Hex-edge triangle laser panels for black acrylic 16"×12" sheets.

Like the snub birch board (pointy-top hex grid, walls, orange pip labels) but the
cut perimeter follows the outer edges of boundary hexagons only — no partial perimeter
hexes and no chamfered snub tips or corner cutouts.

Run: .venv/bin/python boards/hex-edge-acrylic/HexEdgeTriangleBoard.svg.py
"""

from collections import Counter
import importlib.util
import json
import random
from pathlib import Path

import drawsvg as draw
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

BOARD_DIR = Path(__file__).resolve().parent
SNUB_MODULE = BOARD_DIR.parent / 'snub-birch' / 'SnubTriangleBoard.svg.py'


def _load_snub():
    spec = importlib.util.spec_from_file_location('snub_board', SNUB_MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


snub = _load_snub()

PX_PER_MM = snub.PX_PER_MM
MM_PER_INCH = snub.MM_PER_INCH
WALL_SPACING_MM = snub.WALL_SPACING_MM
PIP_COLOR = snub.PIP_COLOR
# Interior depth of wall trapezoids, in multiples of WALL_SPACING_MM (was 2, now 4).
WALL_INTERIOR_DEPTH_SPACINGS = 4
WALL_FILL_COLOR = 'yellow'
PANEL_WALL_SEEDS = snub.PANEL_WALL_SEEDS
SHEETBACK_WALL_SEEDS = snub.SHEETBACK_WALL_SEEDS
PANEL_SHEET_GROUPS = [(1, 2), (3, 4), (5, 6)]
SHEET_VERTICAL_GAP_MM = 3.0
SHEET_HORIZONTAL_MARGIN_MM = 6.0
SHEET_PAIR_GAP_MM = 0.0
# Third hex row from the base (0-indexed j=2) on panel 1; panel 2 apex aligns here.
SECOND_PANEL_ALIGN_ROW_FROM_BASE = 3

SHEET_MATERIAL = 'black acrylic'
SHEET_THICKNESS_MM = 3.0
SHEET_WIDTH_IN = 16.0
SHEET_HEIGHT_IN = 12.0
SHEET_MARGIN_MM = 8.0  # legacy single-panel helper; production sheets use snub-style margins below

# Hexagons along each triangle edge (bottom, left, and right diagonal).
EDGE_HEX_COUNT = 7
GRID_N = EDGE_HEX_COUNT
# Reference circumradius (mm) at EDGE_HEX_COUNT; production R is solved from sheet fit.
HEX_R_MM = 19.0
VERTEX_HOLE_DIAMETER_MM = 8.0


def hex_polygon(i, j, R):
    return Polygon(snub.hexagon(R) + snub.hex_center(i, j, R))


def board_region(n, R):
    """Union of all full hex cells in the triangular packing."""
    polys = [hex_polygon(i, j, R) for j in range(n) for i in range(n - j)]
    return unary_union(polys).buffer(0)


def hex_edge_segment(i, j, R, edge_idx):
    verts = snub.hex_vertices_at(i, j, R)
    return verts[edge_idx], verts[(edge_idx + 1) % 6]


def segments_match(a0, a1, b0, b1, tol=1e-4):
    a0, a1, b0, b1 = map(np.asarray, (a0, a1, b0, b1))
    return (np.linalg.norm(a0 - b0) + np.linalg.norm(a1 - b1) < tol or
            np.linalg.norm(a0 - b1) + np.linalg.norm(a1 - b0) < tol)


def shared_edge(i, j, ni, nj, R):
    """Shared segment between two adjacent hex cells."""
    vi = snub.hex_vertices_at(i, j, R)
    vn = snub.hex_vertices_at(ni, nj, R)
    for ei in range(6):
        a0, a1 = vi[ei], vi[(ei + 1) % 6]
        for en in range(6):
            b0, b1 = vn[en], vn[(en + 1) % 6]
            if segments_match(a0, a1, b0, b1):
                return np.asarray(a0, float), np.asarray(a1, float)
    return None


def internal_etch_edges(n, R):
    """Hex edges shared by two cells (green etch). Boundary edges are cut-only."""
    segments = []
    seen = set()
    for j in range(n):
        for i in range(n - j):
            for ni, nj in snub.hex_neighbors(i, j, n):
                if (ni, nj) < (i, j):
                    continue
                seg = shared_edge(i, j, ni, nj, R)
                if seg is None:
                    continue
                key = snub.segment_dedup_key(seg[0], seg[1])
                if key in seen:
                    continue
                seen.add(key)
                segments.append(seg)
    return segments


def edge_key(p0, p1):
    return snub.segment_dedup_key(p0, p1, decimals=1)


def outer_boundary_edges(n, R):
    """Hex edges that belong to only one cell (true board outline)."""
    counts = Counter()
    canonical = {}
    for j in range(n):
        for i in range(n - j):
            for edge_idx in range(6):
                p0, p1 = hex_edge_segment(i, j, R, edge_idx)
                key = edge_key(p0, p1)
                counts[key] += 1
                canonical[key] = (np.asarray(p0, float), np.asarray(p1, float))
    return [canonical[k] for k, c in counts.items() if c == 1]


def chain_boundary_ring(edges, decimals=3):
    """Walk boundary segments into one closed ring."""
    adj = {}
    for a, b in edges:
        ka = tuple(np.round(a, decimals))
        kb = tuple(np.round(b, decimals))
        adj.setdefault(ka, []).append(kb)
        adj.setdefault(kb, []).append(ka)

    for pt, nbrs in adj.items():
        if len(nbrs) != 2:
            raise ValueError(f'boundary vertex degree {len(nbrs)} at {pt}')

    start = min(adj)
    ring = [np.asarray(start, float)]
    prev = None
    cur = start
    for _ in range(len(edges) + 1):
        nbrs = adj[cur]
        nxt = nbrs[0] if prev is None or nbrs[0] != prev else nbrs[1]
        if nxt == start:
            break
        ring.append(np.asarray(nxt, float))
        prev, cur = cur, nxt
    return ring


def boundary_perimeter(n, R):
    """Closed cut path along outer hex edges only."""
    edges = outer_boundary_edges(n, R)
    return chain_boundary_ring(edges)


def region_to_perimeter(region):
    """Exterior ring of the board region as an ordered CCW vertex list."""
    if region.geom_type == 'Polygon':
        poly = region
    elif region.geom_type == 'MultiPolygon':
        poly = max(region.geoms, key=lambda g: g.area)
    else:
        raise ValueError(f'unexpected geometry {region.geom_type}')
    return [np.asarray(p, float) for p in poly.exterior.coords[:-1]]


def hex_edge_triangle(n, R):
    """Perimeter polygon and internal etch for one full-hex triangle board."""
    perimeter = boundary_perimeter(n, R)
    etch = internal_etch_edges(n, R)
    return perimeter, etch


def geometry_params(n=GRID_N, sheet_w_in=SHEET_WIDTH_IN, sheet_h_in=SHEET_HEIGHT_IN,
                    vertical_gap_mm=SHEET_VERTICAL_GAP_MM,
                    horizontal_margin_mm=SHEET_HORIZONTAL_MARGIN_MM,
                    pair_gap_mm=SHEET_PAIR_GAP_MM):
    R = hex_r_for_sheet(
        n, sheet_w_in, sheet_h_in, vertical_gap_mm, horizontal_margin_mm, pair_gap_mm)
    return n, R


def second_panel_align_row_j(n, row_from_base=SECOND_PANEL_ALIGN_ROW_FROM_BASE):
    """Grid row j on panel 1 that panel 2's apex hex aligns to (1 = base row)."""
    if n < 3:
        raise ValueError(f'need at least 3 hexes per edge for tessellated pairs, got n={n}')
    if row_from_base < 1 or row_from_base > n:
        raise ValueError(f'align row {row_from_base} out of range for n={n}')
    return row_from_base - 1


def triangle_dims(n, R):
    side = (n - 1) * np.sqrt(3) * R
    height = (n - 1) * 1.5 * R
    return side, height


def placed_panel_polygons(base_poly, n, R, m, pair_gap_mm, second_drop):
    """Cut polygon for panel m in a tessellated pair (before sheet centering)."""
    side, height = triangle_dims(n, R)
    x0 = m * side / 2 + m * pair_gap_mm
    flip = (m % 2 == 1)
    poly = snub.transform(base_poly, x0, side, height, flip)
    if m == 1:
        poly = [p + np.array([0.0, second_drop]) for p in poly]
    return poly


def count_shared_cut_edges(poly_a, poly_b):
    """Boundary segments shared by two panel cut polygons."""
    pa = Polygon(poly_a)
    pb = Polygon(poly_b)
    keys_a = {
        snub.segment_dedup_key(pa.exterior.coords[i], pa.exterior.coords[i + 1], decimals=1)
        for i in range(len(pa.exterior.coords) - 1)
    }
    keys_b = {
        snub.segment_dedup_key(pb.exterior.coords[i], pb.exterior.coords[i + 1], decimals=1)
        for i in range(len(pb.exterior.coords) - 1)
    }
    return len(keys_a & keys_b)


def tessellated_pair_layout_metrics(base_poly, n, R, pair_gap_mm=SHEET_PAIR_GAP_MM):
    """Shared-edge tessellation quality for the current hex-edge sheet layout rules."""
    second_drop = second_panel_drop_mm(n, R, pair_gap_mm)
    p1 = Polygon(placed_panel_polygons(base_poly, n, R, 0, pair_gap_mm, second_drop))
    p2 = Polygon(placed_panel_polygons(base_poly, n, R, 1, pair_gap_mm, second_drop))
    return {
        'align_row_j': second_panel_align_row_j(n),
        'second_drop_mm': second_drop,
        'shared_cut_edges': count_shared_cut_edges(p1, p2),
        'overlap_area_mm2': float(p1.intersection(p2).area),
        'gap_mm': float(p1.distance(p2)),
    }


def second_panel_drop_mm(n, R, pair_gap_mm=SHEET_PAIR_GAP_MM, base_poly=None):
    """+y shift so the flipped panel apex hex shares a row with panel 1."""
    align_j = second_panel_align_row_j(n)
    return float(snub.hex_center(0, align_j, R)[1])


def tessellated_pair_bbox_estimate_mm(n, R, pair_gap_mm=SHEET_PAIR_GAP_MM):
    """Conservative bbox (mm) for sheet-fit checks (avoids fragile boundary at trial R)."""
    side, height = triangle_dims(n, R)
    drop = second_panel_drop_mm(n, R, pair_gap_mm)
    hex_x = np.sqrt(3) / 2 * R
    hex_y = R
    p1 = (-hex_x, -hex_y, side + hex_x, height + hex_y)
    x0 = side / 2 + pair_gap_mm
    p2 = (x0 - hex_x, drop - hex_y, x0 + side + hex_x, drop + height + hex_y)
    return min(p1[0], p2[0]), min(p1[1], p2[1]), max(p1[2], p2[2]), max(p1[3], p2[3])


def validate_tessellated_pair_layout(base_poly, n, R, pair_gap_mm=SHEET_PAIR_GAP_MM,
                                     min_shared_edges=1, max_overlap_mm2=0.1):
    metrics = tessellated_pair_layout_metrics(base_poly, n, R, pair_gap_mm)
    if metrics['shared_cut_edges'] < min_shared_edges:
        raise ValueError(
            f'n={n} R={R:.3f}: tessellated pair has no shared cut edge '
            f'(gap={metrics["gap_mm"]:.3f} mm)')
    if metrics['overlap_area_mm2'] > max_overlap_mm2:
        raise ValueError(
            f'n={n} R={R:.3f}: tessellated pair overlap '
            f'{metrics["overlap_area_mm2"]:.4f} mm²')
    return metrics


def tessellated_pair_bbox_mm(n, R, pair_gap_mm=SHEET_PAIR_GAP_MM):
    base_poly, base_etch = hex_edge_triangle(n, R)
    pair = build_tessellated_pair(
        base_poly, base_etch, n, R, [1, 2], WALL_SPACING_MM, PANEL_WALL_SEEDS,
        pair_gap_mm=pair_gap_mm)
    polys = [poly for _, poly, _, _, _, _, _ in pair]
    walls = [trap for _, _, _, traps, _, _, _ in pair for trap in traps]
    return geometry_bbox_mm(polys, walls)


def _pair_bbox_size_estimate(n, R, pair_gap_mm=SHEET_PAIR_GAP_MM):
    minx, miny, maxx, maxy = tessellated_pair_bbox_estimate_mm(n, R, pair_gap_mm)
    return maxx - minx, maxy - miny


def _actual_pair_bbox(n, R, pair_gap_mm=SHEET_PAIR_GAP_MM):
    try:
        return tessellated_pair_bbox_mm(n, R, pair_gap_mm)
    except ValueError:
        return None


def _solve_r_for_height(n, target_h, pair_gap_mm=SHEET_PAIR_GAP_MM, r_max=500.0):
    """R so the tessellated pair height matches ``target_h`` (3 mm top + bottom inset)."""
    lo, hi = 0.1, r_max
    for _ in range(50):
        mid = (lo + hi) / 2
        _, h = _pair_bbox_size_estimate(n, mid, pair_gap_mm)
        if h < target_h:
            lo = mid
        else:
            hi = mid
    R_est = lo
    best = None
    for R_try in np.arange(R_est + 0.5, R_est - 1.5, -0.05):
        R_try = round(float(R_try), 2)
        bbox = _actual_pair_bbox(n, R_try, pair_gap_mm)
        if bbox is None:
            continue
        h = bbox[3] - bbox[1]
        if h > target_h + 0.15:
            continue
        try:
            base_poly, _ = hex_edge_triangle(n, R_try)
            validate_tessellated_pair_layout(base_poly, n, R_try, pair_gap_mm)
        except ValueError:
            continue
        if best is None or h > best[1]:
            best = (R_try, h)
    if best is None:
        raise ValueError(f'no valid R for n={n} with height <= {target_h:.2f} mm')
    return best[0]


def _solve_r_for_width(n, target_w, pair_gap_mm=SHEET_PAIR_GAP_MM, r_max=500.0):
    lo, hi = 0.1, r_max
    for _ in range(50):
        mid = (lo + hi) / 2
        w, _ = _pair_bbox_size_estimate(n, mid, pair_gap_mm)
        if w < target_w:
            lo = mid
        else:
            hi = mid
    R_est = lo
    best = None
    for R_try in np.arange(R_est + 0.5, R_est - 1.5, -0.05):
        R_try = round(float(R_try), 2)
        bbox = _actual_pair_bbox(n, R_try, pair_gap_mm)
        if bbox is None:
            continue
        w = bbox[2] - bbox[0]
        if w > target_w + 0.15:
            continue
        try:
            base_poly, _ = hex_edge_triangle(n, R_try)
            validate_tessellated_pair_layout(base_poly, n, R_try, pair_gap_mm)
        except ValueError:
            continue
        if best is None or w > best[1]:
            best = (R_try, w)
    if best is None:
        raise ValueError(f'no valid R for n={n} with width <= {target_w:.2f} mm')
    return best[0]


def hex_r_for_sheet(n, sheet_w_in=SHEET_WIDTH_IN, sheet_h_in=SHEET_HEIGHT_IN,
                    vertical_gap_mm=SHEET_VERTICAL_GAP_MM,
                    horizontal_margin_mm=SHEET_HORIZONTAL_MARGIN_MM,
                    pair_gap_mm=SHEET_PAIR_GAP_MM):
    """R so a tessellated pair has ``vertical_gap_mm`` to top and bottom sheet edges."""
    sheet_w = sheet_w_in * MM_PER_INCH
    sheet_h = sheet_h_in * MM_PER_INCH
    target_h = sheet_h - 2 * vertical_gap_mm
    max_w = sheet_w - 2 * horizontal_margin_mm

    R = _solve_r_for_height(n, target_h, pair_gap_mm)
    bbox = _actual_pair_bbox(n, R, pair_gap_mm)
    if bbox is not None and (bbox[2] - bbox[0]) > max_w:
        R = _solve_r_for_width(n, max_w, pair_gap_mm)

    base_poly, _ = hex_edge_triangle(n, R)
    validate_tessellated_pair_layout(base_poly, n, R, pair_gap_mm)
    return R


def disallowed_wall_hex_indices(n):
    """Corner (vertex) hexes and the two grid neighbors of each corner."""
    disallowed = set()
    for corner in snub.corner_hex_indices(n):
        disallowed.add(corner)
        for nb in snub.hex_neighbors(*corner, n):
            disallowed.add(nb)
    return disallowed


def allowed_wall_hex_indices(n):
    """Hexes eligible for random wall targets."""
    bad = disallowed_wall_hex_indices(n)
    return [(i, j) for j in range(n) for i in range(n - j) if (i, j) not in bad]


def _interior_wall_line(v0, v1, tangent, inward, edge_mid, edge_len, spacing, k,
                        prev_wall, next_wall, verts, edge_idx, center):
    """Endpoints of one interior wall line at offset ``k`` (k=-2 is innermost/shortest)."""
    offset = -k * spacing
    base = v0 + offset * inward
    offset_perp = np.dot(base - edge_mid, inward)
    mid = base + np.dot(edge_mid - base, tangent) * tangent
    tan30 = np.tan(np.pi / 6)
    half_len = edge_len / 2 - offset_perp * tan30

    prev_edge = (edge_idx - 1) % 6
    next_edge = (edge_idx + 1) % 6
    _, _, t_prev, n_prev = snub.hex_edge_geometry(verts, prev_edge, center)
    _, _, t_next, n_next = snub.hex_edge_geometry(verts, next_edge, center)

    if prev_wall:
        a = snub.wall_miter_at_corner(base, tangent, v0 + offset * n_prev, t_prev)
    else:
        a = mid - half_len * tangent

    if next_wall:
        b = snub.wall_miter_at_corner(base, tangent, v1 + offset * n_next, t_next)
    else:
        b = mid + half_len * tangent

    if a is None or b is None or np.dot(b - a, tangent) < 1e-9:
        return None
    return a, b


def hex_wall_trapezoid(i, j, n, R, edge_idx, spacing, wall_edges):
    """Trapezoid wall on one hex edge: outer side on the hex edge, inner parallel inset."""
    center = snub.hex_center(i, j, R)
    verts = snub.hex_vertices_at(i, j, R)
    v0, v1, tangent, inward = snub.hex_edge_geometry(verts, edge_idx, center)
    edge_mid = (v0 + v1) / 2
    edge_len = np.linalg.norm(v1 - v0)
    prev_wall = (edge_idx - 1) % 6 in wall_edges
    next_wall = (edge_idx + 1) % 6 in wall_edges

    inner = _interior_wall_line(
        v0, v1, tangent, inward, edge_mid, edge_len, spacing,
        -WALL_INTERIOR_DEPTH_SPACINGS,
        prev_wall, next_wall, verts, edge_idx, center)
    if inner is None:
        return None
    a_inner, b_inner = inner
    return [np.asarray(v0, float), np.asarray(v1, float),
            np.asarray(b_inner, float), np.asarray(a_inner, float)]


def hex_walls_on_edges_interior(i, j, n, R, edge_indices, spacing):
    """Interior trapezoid walls for the given edges of one target hex."""
    wall_edges = set(edge_indices)
    trapezoids = []
    for edge_idx in edge_indices:
        trap = hex_wall_trapezoid(i, j, n, R, edge_idx, spacing, wall_edges)
        if trap is not None:
            trapezoids.append(trap)
    return trapezoids


def geometry_bbox_mm(polys, wall_trapezoids=()):
    """Axis-aligned bounding box of polygons and wall trapezoids, in mm."""
    xs = [p[0] for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    for trap in wall_trapezoids:
        for p in trap:
            xs.append(p[0])
            ys.append(p[1])
    return min(xs), min(ys), max(xs), max(ys)


def drawing_bbox(polys, wall_trapezoids, pip_marks=(), margin=20):
    """Pixel-space bounding box for perimeter polygons, walls, and pip marks."""
    xs = [p[0] * PX_PER_MM for poly in polys for p in poly]
    ys = [p[1] * PX_PER_MM for poly in polys for p in poly]
    for trap in wall_trapezoids:
        for p in trap:
            xs.append(p[0] * PX_PER_MM)
            ys.append(p[1] * PX_PER_MM)
    for center, radius in pip_marks:
        rpx = radius * PX_PER_MM
        xs.extend([center[0] * PX_PER_MM - rpx, center[0] * PX_PER_MM + rpx])
        ys.extend([center[1] * PX_PER_MM - rpx, center[1] * PX_PER_MM + rpx])
    minx, miny = min(xs) - margin, min(ys) - margin
    width = (max(xs) + margin) - minx
    height_px = (max(ys) + margin) - miny
    return minx, miny, width, height_px


def add_wall_trapezoids(d, trapezoids, color=WALL_FILL_COLOR):
    for trap in trapezoids:
        coords = []
        for p in trap:
            coords.extend([p[0] * PX_PER_MM, p[1] * PX_PER_MM])
        d.append(draw.Lines(*coords, close=True, fill=color, stroke='none'))


def random_wall_config(n, R, spacing, rng):
    """Walled hexes — same patterns as snub, with relaxed placement on small boards."""
    interior = allowed_wall_hex_indices(n)
    wall_hexes = None
    for wall_count in range(4, 0, -1):
        try:
            wall_hexes = snub.pick_non_adjacent_hexes(interior, wall_count, n, rng)
            break
        except RuntimeError:
            continue
    if wall_hexes is None:
        raise RuntimeError(f'no non-adjacent interior hexes for walls at n={n}')
    patterns = snub.THREE_EDGE_PATTERNS[:]
    rng.shuffle(patterns)
    trapezoids = []
    configs = []
    for hex_idx, pattern in zip(wall_hexes, patterns):
        rotation = rng.randrange(6)
        edges = snub.rotated_pattern_edges(pattern, rotation)
        trapezoids.extend(hex_walls_on_edges_interior(*hex_idx, n, R, edges, spacing))
        label = snub.pattern_pip_count(pattern)
        configs.append({
            'hex': list(hex_idx),
            'pattern': list(pattern),
            'rotation': rotation,
            'edges': edges,
            'label': label,
            'pip_count': label,
        })
    return trapezoids, configs


def vertex_hole_marks(n, R, diameter_mm=VERTEX_HOLE_DIAMETER_MM):
    """Round cut holes at the center of each corner (vertex) hexagon."""
    radius = diameter_mm / 2
    return [(np.asarray(snub.hex_center(i, j, R), float), radius)
            for i, j in snub.corner_hex_indices(n)]


def build_tessellated_pair(base_poly, base_etch, n, R, panel_ids, wall_spacing,
                           panel_seeds, pair_gap_mm=SHEET_PAIR_GAP_MM):
    """Two triangles on one sheet; distinct wall layout per panel (mirrors snub-birch)."""
    side, height = triangle_dims(n, R)
    second_drop = second_panel_drop_mm(n, R, pair_gap_mm)
    placed = []
    for m, panel_id in enumerate(panel_ids):
        seed = panel_seeds[panel_id]
        rng = random.Random(seed)
        wall_trapezoids, wall_configs = random_wall_config(n, R, wall_spacing, rng)
        x0 = m * side / 2 + m * pair_gap_mm
        flip = (m % 2 == 1)
        poly = snub.transform(base_poly, x0, side, height, flip)
        etch = [tuple(snub.transform(seg, x0, side, height, flip)) for seg in base_etch]
        walls = [
            [snub.transform([p], x0, side, height, flip)[0] for p in trap]
            for trap in wall_trapezoids
        ]
        pips = snub.transform_pip_marks(
            snub.wall_pip_marks(n, R, wall_configs), x0, side, height, flip)
        vertex_holes = [
            (snub.transform([snub.hex_center(i, j, R)], x0, side, height, flip)[0],
             VERTEX_HOLE_DIAMETER_MM / 2)
            for i, j in snub.corner_hex_indices(n)
        ]
        if m == 1:
            drop = np.array([0.0, second_drop])
            poly, etch, walls, pips, vertex_holes = apply_offset(
                poly, etch, walls, drop, pips, vertex_holes)
        placed.append((panel_id, poly, etch, walls, wall_configs, pips, vertex_holes))
    return placed


def apply_offset(poly, etch, walls, offset, pip_marks=(), vertex_holes=()):
    off = np.asarray(offset, float)
    poly = [p + off for p in poly]
    etch = [(a + off, b + off) for a, b in etch]
    walls = [[p + off for p in trap] for trap in walls]
    pip_marks = [(np.asarray(p, float) + off, r) for p, r in pip_marks]
    vertex_holes = [(np.asarray(p, float) + off, r) for p, r in vertex_holes]
    return poly, etch, walls, pip_marks, vertex_holes


def center_on_sheet(triangles, sheet_width_in, sheet_height_in,
                    vertical_gap_mm=SHEET_VERTICAL_GAP_MM,
                    horizontal_margin_mm=SHEET_HORIZONTAL_MARGIN_MM):
    """Place a tessellated pair on the sheet (same layout rules as snub-birch)."""
    polys = [poly for _, poly, _, _, _, _, _ in triangles]
    walls = [trap for _, _, _, traps, _, _, _ in triangles for trap in traps]
    minx, miny, maxx, maxy = geometry_bbox_mm(polys, walls)
    pair_w = maxx - minx
    sheet_w = sheet_width_in * MM_PER_INCH
    inset_x = min(horizontal_margin_mm, max(0.0, (sheet_w - pair_w) / 2))
    off_x = inset_x + max(0.0, (sheet_w - 2 * inset_x - pair_w) / 2) - minx
    off_y = vertical_gap_mm - miny
    offset = np.array([off_x, off_y])
    centered = []
    for panel_id, poly, etch, walls, configs, pip_marks, vertex_holes in triangles:
        poly, etch, walls, pip_marks, vertex_holes = apply_offset(
            poly, etch, walls, offset, pip_marks, vertex_holes)
        centered.append((panel_id, poly, etch, walls, configs, pip_marks, vertex_holes))
    return centered


def polygon_cut_segments(poly):
    pts = [np.asarray(p, float) for p in poly]
    return [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def add_cut_lines(d, segments, color='black', stroke_width=5):
    for q0, q1 in snub.dedupe_segments(segments):
        d.append(draw.Line(q0[0] * PX_PER_MM, q0[1] * PX_PER_MM,
                           q1[0] * PX_PER_MM, q1[1] * PX_PER_MM,
                           stroke=color, stroke_width=stroke_width, fill='none'))


def add_cut_holes(d, holes, fill='red', stroke='black', stroke_width=5):
    for center, radius in holes:
        cx = center[0] * PX_PER_MM
        cy = center[1] * PX_PER_MM
        r = radius * PX_PER_MM
        d.append(draw.Circle(cx, cy, r, fill=fill, stroke='none'))
        d.append(draw.Circle(cx, cy, r, stroke=stroke, stroke_width=stroke_width, fill='none'))


def add_sheet_bbox(d, sheet_width_in, sheet_height_in, color='blue', stroke_width=1):
    """Full sheet outline (registration guide; not a board cut line)."""
    w_mm = sheet_width_in * MM_PER_INCH
    h_mm = sheet_height_in * MM_PER_INCH
    coords = []
    for x, y in ((0, 0), (w_mm, 0), (w_mm, h_mm), (0, h_mm)):
        coords.extend([x * PX_PER_MM, y * PX_PER_MM])
    d.append(draw.Lines(*coords, close=True, stroke=color, stroke_width=stroke_width, fill='none'))


def save_laser_sheet(path, sheet_width_in, sheet_height_in, triangles, *, etch_only=False):
    sheet_w_px = sheet_width_in * MM_PER_INCH * PX_PER_MM
    sheet_h_px = sheet_height_in * MM_PER_INCH * PX_PER_MM
    d = draw.Drawing(sheet_w_px, sheet_h_px, origin=(0, 0))
    add_sheet_bbox(d, sheet_width_in, sheet_height_in)
    cut_segments = []
    etch_segments = []
    wall_trapezoids = []
    cut_holes = []
    pip_marks = []
    for _, poly, etch, walls, _, pips, holes in triangles:
        if not etch_only:
            cut_segments.extend(polygon_cut_segments(poly))
            cut_holes.extend(holes)
        etch_segments.extend(etch)
        wall_trapezoids.extend(walls)
        pip_marks.extend(pips)
    if not etch_only:
        add_cut_lines(d, cut_segments, 'black', stroke_width=5)
        add_cut_holes(d, cut_holes)
    snub.add_etch(d, etch_segments, 'green', stroke_width=3)
    add_wall_trapezoids(d, wall_trapezoids)
    snub.add_pip_marks(d, pip_marks)
    d.save_svg(path)


def save_panel_reference(path, poly, etch, walls, pip_marks, vertex_holes):
    """Single-triangle reference SVG (tight bbox, like snub panel-*.svg)."""
    minx, miny, width, height_px = drawing_bbox([poly], walls, pip_marks)
    d = draw.Drawing(width, height_px, origin=(minx, miny))
    snub.add_perimeter(d, poly, 'black', stroke_width=5)
    add_cut_holes(d, vertex_holes)
    snub.add_etch(d, etch, 'green', stroke_width=3)
    add_wall_trapezoids(d, walls)
    snub.add_pip_marks(d, pip_marks)
    d.save_svg(path)


def save_dev_pair(path, n, R, wall_spacing=WALL_SPACING_MM):
    """Two tessellated panels (preview, same layout as snub SnubTriangleBoard.svg)."""
    base_poly, base_etch = hex_edge_triangle(n, R)
    dev_seeds = {1: 42, 2: 43}
    pair = build_tessellated_pair(
        base_poly, base_etch, n, R, [1, 2], wall_spacing, dev_seeds)
    polys = [poly for _, poly, _, _, _, _, _ in pair]
    walls = [trap for _, _, _, traps, _, _, _ in pair for trap in traps]
    pips = [m for _, _, _, _, _, pm, _ in pair for m in pm]
    minx, miny, width, height_px = drawing_bbox(polys, walls, pips)
    d = draw.Drawing(width, height_px, origin=(minx, miny))
    cut_segments = []
    etch_segments = []
    wall_trapezoids = []
    cut_holes = []
    for _, poly, etch, wall_t, _, pips_t, holes in pair:
        cut_segments.extend(polygon_cut_segments(poly))
        etch_segments.extend(etch)
        wall_trapezoids.extend(wall_t)
        cut_holes.extend(holes)
        snub.add_pip_marks(d, pips_t)
    add_cut_lines(d, cut_segments, 'black', stroke_width=5)
    add_cut_holes(d, cut_holes)
    snub.add_etch(d, etch_segments, 'green', stroke_width=3)
    add_wall_trapezoids(d, wall_trapezoids)
    d.save_svg(path)


def generate_laser_sheets(output_dir=BOARD_DIR, n=GRID_N,
                          sheet_w_in=SHEET_WIDTH_IN, sheet_h_in=SHEET_HEIGHT_IN,
                          wall_spacing=WALL_SPACING_MM, panel_seeds=PANEL_WALL_SEEDS,
                          sheet_groups=PANEL_SHEET_GROUPS,
                          vertical_gap_mm=SHEET_VERTICAL_GAP_MM,
                          horizontal_margin_mm=SHEET_HORIZONTAL_MARGIN_MM,
                          pair_gap_mm=SHEET_PAIR_GAP_MM):
    """Three laser-cut SVG files (two tessellated panels per sheet, like snub-birch)."""
    output_dir = Path(output_dir)
    n, R = geometry_params(n, sheet_w_in, sheet_h_in, vertical_gap_mm,
                           horizontal_margin_mm, pair_gap_mm)
    base_poly, base_etch = hex_edge_triangle(n, R)

    manifest = {
        'board_style': 'hex-edge-acrylic',
        'material': SHEET_MATERIAL,
        'sheet_thickness_mm': SHEET_THICKNESS_MM,
        'sheet_size_in': [sheet_w_in, sheet_h_in],
        'grid_n': n,
        'edge_hex_count': n,
        'hex_R_mm': R,
        'vertex_hole_diameter_mm': VERTEX_HOLE_DIAMETER_MM,
        'second_panel_align_row_from_base': SECOND_PANEL_ALIGN_ROW_FROM_BASE,
        'pair_gap_mm': pair_gap_mm,
        'wall_spacing_mm': wall_spacing,
        'wall_fill_color': WALL_FILL_COLOR,
        'pip_color': PIP_COLOR,
        'perimeter': 'outer hex edges only (no partial perimeter hexes)',
        'vertical_gap_mm': vertical_gap_mm,
        'horizontal_margin_mm': horizontal_margin_mm,
        'panels': {},
        'sheets': {},
    }

    layout = validate_tessellated_pair_layout(base_poly, n, R, pair_gap_mm)
    manifest['sheet_layout'] = {
        'style': 'tessellated shared-edge pair',
        'second_panel_align_row_j': layout['align_row_j'],
        'second_panel_drop_mm': layout['second_drop_mm'],
        'shared_cut_edges_per_pair': layout['shared_cut_edges'],
    }

    for panel_id in sorted(panel_seeds):
        seed = panel_seeds[panel_id]
        rng = random.Random(seed)
        _, wall_configs = random_wall_config(n, R, wall_spacing, rng)
        manifest['panels'][str(panel_id)] = {
            'wall_seed': seed,
            'walls': wall_configs,
        }

    for sheet_idx, panel_ids in enumerate(sheet_groups, start=1):
        pair = build_tessellated_pair(
            base_poly, base_etch, n, R, list(panel_ids), wall_spacing, panel_seeds,
            pair_gap_mm=pair_gap_mm)
        centered = center_on_sheet(
            pair, sheet_w_in, sheet_h_in, vertical_gap_mm, horizontal_margin_mm)
        path = output_dir / f'HexEdgeTriangleBoard-sheet-{sheet_idx}.svg'
        save_laser_sheet(str(path), sheet_w_in, sheet_h_in, centered)
        svg_name = path.name
        manifest['sheets'][str(sheet_idx)] = {
            'svg': svg_name,
            'panels': list(panel_ids),
        }
        for panel_id, _, _, _, wall_configs, _, _ in centered:
            manifest['panels'][str(panel_id)]['sheet'] = sheet_idx
            manifest['panels'][str(panel_id)]['svg'] = svg_name
            manifest['panels'][str(panel_id)]['walls'] = wall_configs

    manifest_path = output_dir / 'HexEdgeTriangleBoard-panels.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
        f.write('\n')
    return manifest


def generate_production_panels(output_dir=BOARD_DIR, n=GRID_N, R=None,
                               wall_spacing=WALL_SPACING_MM,
                               panel_seeds=PANEL_WALL_SEEDS):
    """Six single-triangle reference SVGs (tight bbox, distinct wall layouts)."""
    output_dir = Path(output_dir)
    if R is None:
        n, R = geometry_params(n)
    base_poly, base_etch = hex_edge_triangle(n, R)

    for panel_id in sorted(panel_seeds):
        seed = panel_seeds[panel_id]
        rng = random.Random(seed)
        walls, wall_configs = random_wall_config(n, R, wall_spacing, rng)
        pips = snub.wall_pip_marks(n, R, wall_configs)
        vertex_holes = vertex_hole_marks(n, R)
        path = output_dir / f'HexEdgeTriangleBoard-panel-{panel_id}.svg'
        save_panel_reference(str(path), base_poly, base_etch, walls, pips, vertex_holes)

    return n, R


def generate_sheetback_sheets(output_dir=BOARD_DIR, n=GRID_N, R=None,
                              wall_spacing=WALL_SPACING_MM,
                              panel_seeds=SHEETBACK_WALL_SEEDS,
                              sheet_groups=PANEL_SHEET_GROUPS,
                              sheet_w_in=SHEET_WIDTH_IN, sheet_h_in=SHEET_HEIGHT_IN,
                              vertical_gap_mm=SHEET_VERTICAL_GAP_MM,
                              horizontal_margin_mm=SHEET_HORIZONTAL_MARGIN_MM,
                              pair_gap_mm=SHEET_PAIR_GAP_MM):
    """Three etch-only back-side sheets (flip after cut; no perimeter)."""
    output_dir = Path(output_dir)
    if R is None:
        n, R = geometry_params(n, sheet_w_in, sheet_h_in, vertical_gap_mm,
                               horizontal_margin_mm, pair_gap_mm)
    base_poly, base_etch = hex_edge_triangle(n, R)

    sheetbacks = {}
    sheetback_panels = {}

    for panel_id in sorted(panel_seeds):
        seed = panel_seeds[panel_id]
        rng = random.Random(seed)
        _, wall_configs = random_wall_config(n, R, wall_spacing, rng)
        sheetback_panels[str(panel_id)] = {
            'wall_seed': seed,
            'front_panel': panel_id,
            'walls': wall_configs,
        }

    for sheet_idx, panel_ids in enumerate(sheet_groups, start=1):
        pair = build_tessellated_pair(
            base_poly, base_etch, n, R, list(panel_ids), wall_spacing, panel_seeds,
            pair_gap_mm=pair_gap_mm)
        centered = center_on_sheet(
            pair, sheet_w_in, sheet_h_in, vertical_gap_mm, horizontal_margin_mm)
        path = output_dir / f'HexEdgeTriangleBoard-sheetback-{sheet_idx}.svg'
        save_laser_sheet(str(path), sheet_w_in, sheet_h_in, centered, etch_only=True)
        svg_name = path.name
        sheetbacks[str(sheet_idx)] = {
            'svg': svg_name,
            'panels': list(panel_ids),
            'pairs_with_front_sheet': sheet_idx,
        }
        for panel_id, _, _, _, wall_configs, _, _ in centered:
            sheetback_panels[str(panel_id)]['sheetback'] = sheet_idx
            sheetback_panels[str(panel_id)]['svg'] = svg_name
            sheetback_panels[str(panel_id)]['walls'] = wall_configs

    return {
        'sheetbacks': sheetbacks,
        'sheetback_panels': sheetback_panels,
        'sheetback_wall_seeds': dict(panel_seeds),
    }


def merge_sheetback_manifest(sheetback_info, manifest_path=None):
    if manifest_path is None:
        manifest_path = BOARD_DIR / 'HexEdgeTriangleBoard-panels.json'
    manifest_path = Path(manifest_path)
    with open(manifest_path, encoding='utf-8') as f:
        manifest = json.load(f)
    manifest.update(sheetback_info)
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
        f.write('\n')
    return manifest


if __name__ == '__main__':
    manifest = generate_laser_sheets()
    n, R = manifest['grid_n'], manifest['hex_R_mm']
    sheetback_info = generate_sheetback_sheets(n=n, R=R)
    merge_sheetback_manifest(sheetback_info)
    generate_production_panels(n=n, R=R)
    save_dev_pair(str(BOARD_DIR / 'HexEdgeTriangleBoard.svg'), n, R)
    print('Wrote HexEdgeTriangleBoard-sheet-1..3.svg, sheetback-1..3, panel-1..6, dev preview')
    layout = manifest.get('sheet_layout', {})
    print(f'  grid_n={n}  R={R:.3f} mm  shared_cut_edges={layout.get("shared_cut_edges_per_pair")}')
