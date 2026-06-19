import json
import numpy as np
import drawsvg as draw
import random

# 96 dpi => pixels per millimeter, matching the ~3.78 factor used by TriangleBoard.svg.py
PX_PER_MM = 96 / 25.4
MM_PER_INCH = 25.4

# Geometry of a single pointy-top hexagon (vertical left/right edges, points up/down).
# Vertices are placed on a circle of radius R (circumradius) going around the hexagon.
HEX_ANGLES = np.deg2rad([90, 150, 210, 270, 330, 30])


def hexagon(R):
    """Return the 6 vertices of a pointy-top hexagon of circumradius R, centered at origin."""
    return R * np.column_stack([np.cos(HEX_ANGLES), np.sin(HEX_ANGLES)])


def hex_centers(n, R):
    """Centers of a triangular packing with n hexagons along each side.

    Row j (counting from the base) holds n-j hexagons.  The three rows that lie
    on the triangle edges (j == 0, i == 0, and the i == n-1-j diagonal) provide
    the half hexagons; everything strictly inside provides the full hexagons.
    """
    dx = np.array([np.sqrt(3) * R, 0.0])            # neighbor to the right
    dy = np.array([np.sqrt(3) * R / 2, 1.5 * R])    # neighbor up and to the right
    centers = []
    for j in range(n):
        for i in range(n - j):
            centers.append(i * dx + j * dy)
    return centers


def hex_edges(n, R):
    """Every edge (as a (p0, p1) pair) of every hexagon in the triangular packing."""
    verts = hexagon(R)
    rolled = np.roll(verts, -1, axis=0)
    edges = []
    for c in hex_centers(n, R):
        for a, b in zip(verts, rolled):
            edges.append((a + c, b + c))
    return edges


def triangle_corners(n, R):
    """The three corners of the equilateral triangle (located at the corner hexagon centers)."""
    side = (n - 1) * np.sqrt(3) * R
    height = (n - 1) * 1.5 * R
    A = np.array([0.0, 0.0])           # bottom left
    B = np.array([side, 0.0])          # bottom right
    C = np.array([side / 2, height])   # apex
    return A, B, C


def corner_hex_indices(n):
    """Grid (i, j) indices of the three corner hexagons."""
    return [(0, 0), (n - 1, 0), (0, n - 1)]


def hex_center(i, j, R):
    dx = np.array([np.sqrt(3) * R, 0.0])
    dy = np.array([np.sqrt(3) * R / 2, 1.5 * R])
    return i * dx + j * dy


def chamfer_points_at_corner(corners, tip_clip, k):
    """Chamfer endpoints and snub-cut tangent at triangle corner k."""
    L = 2 * tip_clip / np.sqrt(3)
    cur = corners[k]
    prev = corners[(k - 1) % 3]
    nxt = corners[(k + 1) % 3]
    p1 = cur + L * (prev - cur) / np.linalg.norm(prev - cur)
    p2 = cur + L * (nxt - cur) / np.linalg.norm(nxt - cur)
    tangent = (p2 - p1) / np.linalg.norm(p2 - p1)
    return p1, p2, tangent


def segment_intersection(p0, p1, q0, q1, eps=1e-9):
    p0, p1, q0, q1 = map(np.asarray, (p0, p1, q0, q1))
    d = p1 - p0
    e = q1 - q0
    denom = d[0] * e[1] - d[1] * e[0]
    if abs(denom) < eps:
        return None
    t = ((q0[0] - p0[0]) * e[1] - (q0[1] - p0[1]) * e[0]) / denom
    u = ((q0[0] - p0[0]) * d[1] - (q0[1] - p0[1]) * d[0]) / denom
    if -eps <= t <= 1 + eps and -eps <= u <= 1 + eps:
        return p0 + t * d
    return None


def distance_point_to_segment(point, a, b):
    """Perpendicular distance from ``point`` to segment ``a``->``b``."""
    point = np.asarray(point, float)
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    ab = b - a
    length_sq = np.dot(ab, ab)
    if length_sq < 1e-12:
        return np.linalg.norm(point - a)
    t = np.clip(np.dot(point - a, ab) / length_sq, 0.0, 1.0)
    return np.linalg.norm(point - (a + t * ab))


def unique_points(points, tol=1e-4):
    out = []
    for p in points:
        p = np.asarray(p, float)
        if not any(np.linalg.norm(p - q) < tol for q in out):
            out.append(p)
    return out


def corner_piece_polygon(i, j, n, R, corners, tip_clip):
    """Partial corner hexagon inside the chamfered triangle."""
    chamfer = chamfer_polygon(corners, tip_clip)
    hex_poly = [np.asarray(v, float) for v in hexagon(R) + hex_center(i, j, R)]
    points = []
    for v in hex_poly:
        if point_in_polygon(v, chamfer):
            points.append(v)
    for k in range(len(hex_poly)):
        p0, p1 = hex_poly[k], hex_poly[(k + 1) % len(hex_poly)]
        for m in range(len(chamfer)):
            q0, q1 = chamfer[m], chamfer[(m + 1) % len(chamfer)]
            hit = segment_intersection(p0, p1, q0, q1)
            if hit is not None:
                points.append(hit)
    return order_polygon_ccw(unique_points(points))


def point_in_polygon(point, poly):
    x, y = point
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if abs((x1 - x0) * (y - y0) - (y1 - y0) * (x - x0)) < 1e-6:
            if min(x0, x1) - 1e-6 <= x <= max(x0, x1) + 1e-6 and min(y0, y1) - 1e-6 <= y <= max(y0, y1) + 1e-6:
                return True
    inside = False
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if ((y0 > y) != (y1 > y)) and (x < (x1 - x0) * (y - y0) / (y1 - y0 + 1e-15) + x0):
            inside = not inside
    return inside


def order_polygon_ccw(points):
    points = [np.asarray(p, float) for p in points]
    if len(points) < 3:
        return points
    center = np.mean(points, axis=0)
    return sorted(points, key=lambda p: np.arctan2(p[1] - center[1], p[0] - center[0]))


def clip_segment_to_polygon(p0, p1, poly):
    """Clip segment p0->p1 to convex polygon. Returns (q0, q1) or None."""
    return clip_segment(np.asarray(p0, float), np.asarray(p1, float), poly)


def hex_edge_midpoints_in_region(center, R, region):
    """Midpoints of hex edges clipped to the partial corner hex, grouped by orientation."""
    verts = hexagon(R) + np.asarray(center, float)
    vertical_mids = []
    slant_mids = []
    for i in range(6):
        a, b = verts[i], verts[(i + 1) % 6]
        clipped = clip_segment_to_polygon(a, b, region)
        if clipped is None:
            continue
        q0, q1 = clipped
        if np.linalg.norm(q1 - q0) < 1e-6:
            continue
        mid = (q0 + q1) / 2
        direction = (b - a) / np.linalg.norm(b - a)
        if abs(abs(direction[1]) - 1.0) < 0.01:
            vertical_mids.append(mid)
        else:
            slant_mids.append(mid)
    return vertical_mids, slant_mids


def snub_normal_into_corner(p1, p2, point):
    """Unit normal to the snub cut, pointing from ``point`` toward the snub line."""
    tangent = (p2 - p1) / np.linalg.norm(p2 - p1)
    normal = np.array([-tangent[1], tangent[0]])
    point = np.asarray(point, float)
    if np.dot(p1 - point, normal) < 0 and np.dot(p2 - point, normal) < 0:
        normal = -normal
    return normal


def triangle_to_pentagon(apex, m1, m2, p1, p2, wall_height):
    """Extend a corner triangle into a house pentagon.

    The triangle base (spanning the two edge midpoints) is moved ``wall_height``
  along the snub-cut normal to form the bottom edge, which stays parallel to the
    snub cut.  The two side edges from the midpoints to the bottom are length
    ``wall_height``.
    """
    apex = np.asarray(apex, float)
    m1 = np.asarray(m1, float)
    m2 = np.asarray(m2, float)
    tangent = (p2 - p1) / np.linalg.norm(p2 - p1)
    normal = snub_normal_into_corner(p1, p2, (m1 + m2) / 2)

    b1 = m1 + wall_height * normal
    b2 = b1 + np.dot(m2 - m1, tangent) * tangent

    return [apex, m2, b2, b1, m1]


def corner_cutout_pentagon(i, j, n, R, corners, tip_clip, k, wall_height):
    """Pentagon cutout in one corner of the partial corner hexagon."""
    p1, p2, _ = chamfer_points_at_corner(corners, tip_clip, k)
    region = corner_piece_polygon(i, j, n, R, corners, tip_clip)
    c_corner = hex_center(i, j, R)

    hex_verts = hexagon(R) + c_corner
    apex = min(hex_verts, key=lambda v: distance_point_to_segment(v, p1, p2))

    vertical_mids, slant_mids = hex_edge_midpoints_in_region(c_corner, R, region)
    if len(vertical_mids) >= 2:
        midpoints = vertical_mids[:2]
    elif len(vertical_mids) == 1 and slant_mids:
        midpoints = [vertical_mids[0], slant_mids[0]]
    elif len(slant_mids) >= 2:
        midpoints = slant_mids[:2]
    else:
        return None

    return triangle_to_pentagon(apex, midpoints[0], midpoints[1], p1, p2, wall_height)


def corner_cutouts(n, R, tip_clip, wall_height):
    """Pentagon cutouts at the three corners of one snub triangle."""
    corners = list(triangle_corners(n, R))
    pentagons = []
    for k, (i, j) in enumerate(corner_hex_indices(n)):
        pent = corner_cutout_pentagon(i, j, n, R, corners, tip_clip, k, wall_height)
        if pent is not None:
            pentagons.append(pent)
    return pentagons


def interior_hex_indices(n):
    """Grid (i, j) indices of full interior hexagons (not on the triangle edge)."""
    indices = []
    for j in range(n):
        for i in range(n - j):
            if j == 0 or i == 0 or i == n - 1 - j:
                continue
            indices.append((i, j))
    return indices


def hex_vertices_at(i, j, R):
    """Vertices of the hexagon at grid position (i, j)."""
    return hexagon(R) + hex_center(i, j, R)


def inward_edge_direction(vertex, neighbor, center):
    """Unit direction along a hex edge, from ``vertex`` toward ``center``."""
    d = np.asarray(neighbor, float) - np.asarray(vertex, float)
    if np.dot(d, np.asarray(center, float) - vertex) < 0:
        d = -d
    return d / np.linalg.norm(d)


def line_line_intersection(p, d, q, e, eps=1e-12):
    """Intersection of lines ``p`` + t*``d`` and ``q`` + u*``e``."""
    p, d, q, e = map(lambda x: np.asarray(x, float), (p, d, q, e))
    denom = d[0] * e[1] - d[1] * e[0]
    if abs(denom) < eps:
        return None
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / denom
    return p + t * d


# Distinct ways to choose three hex edges, up to rotation (one representative each).
THREE_EDGE_PATTERNS = [(0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 4)]


def hex_neighbors(i, j, n):
    """Grid neighbors of hex (i, j) in the triangular packing."""
    candidates = [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1),
                  (i - 1, j + 1), (i + 1, j - 1)]
    return [p for p in candidates if 0 <= p[1] < n and 0 <= p[0] < n - p[1]]


def hexes_adjacent(a, b, n):
    return b in hex_neighbors(*a, n)


def interior_triangle_vertex_indices(n):
    """Three corner hexes of the triangle of full interior hexagons."""
    return [(1, 1), (n - 3, 1), (1, n - 3)]


def disallowed_wall_hex_indices(n):
    """Interior triangle corners and the six interior hexes adjacent to them."""
    interior = set(interior_hex_indices(n))
    disallowed = set(interior_triangle_vertex_indices(n))
    for v in interior_triangle_vertex_indices(n):
        for nb in hex_neighbors(*v, n):
            if nb in interior:
                disallowed.add(nb)
    return sorted(disallowed)


def allowed_interior_hex_indices(n):
    """Interior hexes eligible for random wall placement."""
    disallowed = set(disallowed_wall_hex_indices(n))
    return [h for h in interior_hex_indices(n) if h not in disallowed]


def pick_non_adjacent_hexes(candidates, count, n, rng, attempts=500):
    """Pick ``count`` mutually non-adjacent hexes from ``candidates``."""
    for _ in range(attempts):
        shuffled = candidates[:]
        rng.shuffle(shuffled)
        chosen = []
        for h in shuffled:
            if all(not hexes_adjacent(h, c, n) for c in chosen):
                chosen.append(h)
            if len(chosen) == count:
                return chosen
    raise RuntimeError(f"could not pick {count} non-adjacent interior hexagons")


def rotated_pattern_edges(pattern, rotation):
    """Apply a 6-fold rotation to a three-edge wall pattern."""
    return [(e + rotation) % 6 for e in pattern]


def hex_walls_on_edges(i, j, n, R, edge_indices, spacing):
    """Wall line segments for multiple edges of one interior hexagon."""
    wall_edges = set(edge_indices)
    segments = []
    for edge_idx in edge_indices:
        segments.extend(hex_wall_lines(i, j, n, R, edge_idx, spacing, wall_edges))
    return segments


def random_wall_config(n, R, spacing, rng):
    """Four non-adjacent interior hexes, one of each 3-edge pattern, random rotations."""
    interior = allowed_interior_hex_indices(n)
    wall_hexes = pick_non_adjacent_hexes(interior, 4, n, rng)
    patterns = THREE_EDGE_PATTERNS[:]
    rng.shuffle(patterns)
    segments = []
    configs = []
    for hex_idx, pattern in zip(wall_hexes, patterns):
        rotation = rng.randrange(6)
        edges = rotated_pattern_edges(pattern, rotation)
        segments.extend(hex_walls_on_edges(*hex_idx, n, R, edges, spacing))
        configs.append({
            'hex': list(hex_idx),
            'pattern': list(pattern),
            'rotation': rotation,
            'edges': edges,
        })
    return segments, configs


def _board_hex_rotation_maps(n, R):
    """Map allowed interior hex (i, j) under 0°/120°/240° rotation about triangle centroid."""
    allowed = set(allowed_interior_hex_indices(n))
    centroid = np.mean(triangle_corners(n, R), axis=0)
    centers = {
        (i, j): hex_center(i, j, R)
        for j in range(n)
        for i in range(n - j)
        if (i, j) in allowed
    }

    def rotate_pt(p, deg):
        th = np.deg2rad(deg)
        c, s = np.cos(th), np.sin(th)
        v = np.asarray(p, float) - centroid
        return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]]) + centroid

    def nearest_hex(pt):
        best, best_d = None, float('inf')
        for h in allowed:
            d = np.linalg.norm(centers[h] - pt)
            if d < best_d:
                best_d, best = d, h
        return best

    maps = []
    for deg in (0, 120, 240):
        maps.append({h: nearest_hex(rotate_pt(centers[h], deg)) for h in allowed})
    return maps


def canonical_wall_form(wall_configs, n, R):
    """Lexicographically smallest wall layout over 120° board rotations."""
    tuples = [(tuple(w['hex']), tuple(sorted(w['edges']))) for w in wall_configs]
    forms = []
    for steps, hmap in enumerate(_board_hex_rotation_maps(n, R)):
        items = []
        for h, edges in tuples:
            e2 = tuple(sorted((e + 2 * steps) % 6 for e in edges))
            items.append((hmap[h], e2))
        forms.append(tuple(sorted(items)))
    return min(forms)


def find_distinct_wall_seeds(existing_seeds, n, R, spacing, count=6, start=701):
    """Pick ``count`` seeds whose layouts are unique vs ``existing_seeds`` up to rotation."""
    existing = set()
    for seed in existing_seeds.values():
        rng = random.Random(seed)
        _, cfg = random_wall_config(n, R, spacing, rng)
        existing.add(canonical_wall_form(cfg, n, R))

    found = {}
    seed = start
    while len(found) < count:
        rng = random.Random(seed)
        _, cfg = random_wall_config(n, R, spacing, rng)
        canon = canonical_wall_form(cfg, n, R)
        if canon not in existing:
            existing.add(canon)
            found[len(found) + 1] = seed
        seed += 1
    return found


def random_wall_segments(n, R, spacing, rng):
    """Wall line segments only (see ``random_wall_config`` for placement metadata)."""
    segments, _ = random_wall_config(n, R, spacing, rng)
    return segments


def hex_edge_geometry(verts, edge_idx, center):
    """Vertices, tangent, and inward normal for one hex edge."""
    v0 = verts[edge_idx]
    v1 = verts[(edge_idx + 1) % 6]
    tangent = (v1 - v0) / np.linalg.norm(v1 - v0)
    inward = np.array([-tangent[1], tangent[0]])
    if np.dot(inward, center - (v0 + v1) / 2) < 0:
        inward = -inward
    return v0, v1, tangent, inward


def wall_miter_at_corner(base_a, tangent_a, base_b, tangent_b):
    """Where mirrored offset wall lines on two edges meeting at a vertex cross."""
    return line_line_intersection(base_a, tangent_a, base_b, tangent_b)


def hex_wall_lines(i, j, n, R, edge_idx, spacing, wall_edges):
    """Four parallel wall lines on one edge of an interior hexagon.

    The hex edge itself (green etch) is the center line and is not drawn.  Lines
    closer to the hex center are shorter; lines farther from the center are longer.
    Four flanking lines are spaced by ``spacing`` on each side of the edge.  Where
    two wall edges meet, matching offsets join (``k`` meets ``k``) at a miter.
    """
    center = hex_center(i, j, R)
    verts = hex_vertices_at(i, j, R)
    v0, v1, tangent, inward = hex_edge_geometry(verts, edge_idx, center)

    prev_edge = (edge_idx - 1) % 6
    next_edge = (edge_idx + 1) % 6
    prev_wall = prev_edge in wall_edges
    next_wall = next_edge in wall_edges

    _, _, t_prev, n_prev = hex_edge_geometry(verts, prev_edge, center)
    _, _, t_next, n_next = hex_edge_geometry(verts, next_edge, center)

    edge_mid = (v0 + v1) / 2
    edge_len = np.linalg.norm(v1 - v0)
    tan30 = np.tan(np.pi / 6)

    segments = []
    for k in (2, 1, -1, -2):
        offset = -k * spacing
        base = v0 + offset * inward
        offset_perp = np.dot(base - edge_mid, inward)
        mid = base + np.dot(edge_mid - base, tangent) * tangent
        half_len = edge_len / 2 - offset_perp * tan30

        if prev_wall:
            a = wall_miter_at_corner(base, tangent, v0 + offset * n_prev, t_prev)
        else:
            a = mid - half_len * tangent

        if next_wall:
            b = wall_miter_at_corner(base, tangent, v1 + offset * n_next, t_next)
        else:
            b = mid + half_len * tangent

        if a is None or b is None:
            continue
        if np.dot(b - a, tangent) < 1e-9:
            continue
        segments.append((a, b))
    return segments


def add_wall_lines(d, segments, color, stroke_width):
    for q0, q1 in segments:
        d.append(draw.Line(q0[0] * PX_PER_MM, q0[1] * PX_PER_MM,
                           q1[0] * PX_PER_MM, q1[1] * PX_PER_MM,
                           stroke=color, stroke_width=stroke_width, fill='none'))


def chamfer_polygon(corners, tip_clip):
    """Clip each sharp tip of the triangle, returning a CCW convex polygon.

    ``tip_clip`` is the perpendicular distance (mm) removed from each tip; for a
    60 degree corner that means trimming 2*tip_clip/sqrt(3) along each edge.
    """
    L = 2 * tip_clip / np.sqrt(3)
    poly = []
    m = len(corners)
    for k in range(m):
        prev = corners[(k - 1) % m]
        cur = corners[k]
        nxt = corners[(k + 1) % m]
        to_prev = (prev - cur) / np.linalg.norm(prev - cur)
        to_next = (nxt - cur) / np.linalg.norm(nxt - cur)
        poly.append(cur + L * to_prev)
        poly.append(cur + L * to_next)
    return poly


def clip_segment(p0, p1, poly):
    """Clip segment p0->p1 to the CCW convex polygon. Returns (q0, q1) or None."""
    p0 = np.asarray(p0, float)
    p1 = np.asarray(p1, float)
    d = p1 - p0
    tmin, tmax = 0.0, 1.0
    m = len(poly)
    for i in range(m):
        a = poly[i]
        b = poly[(i + 1) % m]
        e = b - a
        normal = np.array([-e[1], e[0]])  # inward normal for CCW winding
        num = np.dot(normal, p0 - a)
        den = np.dot(normal, d)
        if abs(den) < 1e-12:
            if num < -1e-9:
                return None
        else:
            t = -num / den
            if den > 0:
                tmin = max(tmin, t)
            else:
                tmax = min(tmax, t)
            if tmin > tmax + 1e-12:
                return None
    if tmin > tmax:
        return None
    q0 = p0 + tmin * d
    q1 = p0 + tmax * d
    if np.hypot(*(q1 - q0)) < 1e-7:
        return None
    return q0, q1


def snub_triangle(n, R, tip_clip, cutout_wall_height):
    """Build one snub triangle, returning (perimeter_polygon, etch_segments, cutouts) in mm."""
    poly = chamfer_polygon(triangle_corners(n, R), tip_clip)

    etch = []
    seen = set()
    for p0, p1 in hex_edges(n, R):
        clipped = clip_segment(p0, p1, poly)
        if clipped is None:
            continue
        q0, q1 = clipped
        key = tuple(sorted((tuple(np.round(q0, 4)), tuple(np.round(q1, 4)))))
        if key in seen:
            continue
        seen.add(key)
        etch.append((q0, q1))
    cutouts = corner_cutouts(n, R, tip_clip, cutout_wall_height)
    return poly, etch, cutouts


def transform(points, x0, side, height, flip):
    """Place a base triangle into the strip: translate (flip=False) or 180 deg rotate (flip=True).

    Adjacent triangles share their full long (slanted) edge, tessellating cleanly.
    """
    out = []
    for p in points:
        if flip:
            out.append(np.array([side - p[0] + x0, height - p[1]]))
        else:
            out.append(np.array([p[0] + x0, p[1]]))
    return out


def add_perimeter(d, poly, color, stroke_width):
    coords = []
    for p in poly:
        coords.extend([p[0] * PX_PER_MM, p[1] * PX_PER_MM])
    d.append(draw.Lines(*coords, close=True, stroke=color, stroke_width=stroke_width, fill='none'))


def add_etch(d, segments, color, stroke_width):
    for q0, q1 in segments:
        d.append(draw.Line(q0[0] * PX_PER_MM, q0[1] * PX_PER_MM,
                           q1[0] * PX_PER_MM, q1[1] * PX_PER_MM,
                           stroke=color, stroke_width=stroke_width, fill='none'))


def add_cutouts(d, pentagons, color, stroke_width):
    for pent in pentagons:
        coords = []
        for p in pent:
            coords.extend([p[0] * PX_PER_MM, p[1] * PX_PER_MM])
        d.append(draw.Lines(*coords, close=True, stroke=color, stroke_width=stroke_width, fill='red'))


def drawing_bbox(polys, wall_segments, margin=20):
    """Pixel-space bounding box for perimeter polygons and wall segments."""
    xs = [p[0] * PX_PER_MM for poly in polys for p in poly]
    ys = [p[1] * PX_PER_MM for poly in polys for p in poly]
    for a, b in wall_segments:
        xs.extend([a[0] * PX_PER_MM, b[0] * PX_PER_MM])
        ys.extend([a[1] * PX_PER_MM, b[1] * PX_PER_MM])
    minx, miny = min(xs) - margin, min(ys) - margin
    width = (max(xs) + margin) - minx
    height_px = (max(ys) + margin) - miny
    return minx, miny, width, height_px


def save_triangle_svg(path, poly, etch, cutouts, wall_segments,
                      cut='black', mark='green', wall='green'):
    """Write one snub triangle (perimeter, etch, cutouts, walls) to ``path``."""
    minx, miny, width, height_px = drawing_bbox([poly], wall_segments)
    d = draw.Drawing(width, height_px, origin=(minx, miny))
    add_perimeter(d, poly, cut, stroke_width=5)
    add_etch(d, etch, mark, stroke_width=3)
    add_cutouts(d, cutouts, cut, stroke_width=2)
    add_wall_lines(d, wall_segments, wall, stroke_width=2)
    d.save_svg(path)


# Production wall seeds — frozen at cut time; one distinct layout per panel 1–6.
PANEL_WALL_SEEDS = {
    1: 101,
    2: 202,
    3: 303,
    4: 404,
    5: 505,
    6: 606,
}

# Back-side etch layouts: distinct from front panels up to 120° board rotation.
SHEETBACK_WALL_SEEDS = {
    1: 701,
    2: 702,
    3: 703,
    4: 704,
    5: 705,
    6: 706,
}

# Birch ply: nominal 1'×2' (24"×12") stock, but actual size is 1/8" less per dimension.
SHEET_NOMINAL_WIDTH_IN = 24.0
SHEET_NOMINAL_HEIGHT_IN = 12.0
SHEET_TRIM_IN = 0.125
SHEET_WIDTH_IN = SHEET_NOMINAL_WIDTH_IN - SHEET_TRIM_IN   # 23.875"
SHEET_HEIGHT_IN = SHEET_NOMINAL_HEIGHT_IN - SHEET_TRIM_IN  # 11.875"
PANEL_SHEET_GROUPS = [(1, 2), (3, 4), (5, 6)]
SHEET_VERTICAL_GAP_MM = 5.0    # top and bottom: triangle to sheet edge
SHEET_HORIZONTAL_MARGIN_MM = 6.0
SHEET_PAIR_GAP_MM = 10.0       # horizontal gap between the two panels on a sheet (1 cm)
WALL_SPACING_MM = 0.5


def geometry_bbox_mm(polys, wall_segments=()):
    """Axis-aligned bounding box of polygons and wall segments, in mm."""
    xs = [p[0] for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    for a, b in wall_segments:
        xs.extend([a[0], b[0]])
        ys.extend([a[1], b[1]])
    return min(xs), min(ys), max(xs), max(ys)


def apply_offset(poly, etch, cutouts, wall_segments, offset):
    """Translate one triangle's geometry by ``offset`` (mm)."""
    off = np.asarray(offset, float)
    poly = [p + off for p in poly]
    etch = [(a + off, b + off) for a, b in etch]
    cutouts = [[p + off for p in pent] for pent in cutouts]
    wall_segments = [(a + off, b + off) for a, b in wall_segments]
    return poly, etch, cutouts, wall_segments


def build_tessellated_pair(base_poly, base_etch, base_cutouts, n, R, side, height, tip_clip,
                           panel_ids, wall_spacing, panel_seeds, pair_gap_mm=0.0):
    """Two snub triangles on one sheet; distinct wall layout per panel id.

    The second triangle is shifted ``pair_gap_mm`` further in +x (horizontal) from
    the usual tessellated placement to leave a gap between the pair.
    """
    center = 0.5
    slide = 2 * tip_clip / np.sqrt(3)
    placed = []
    for m, panel_id in enumerate(panel_ids):
        seed = panel_seeds[panel_id]
        rng = random.Random(seed)
        wall_segments, wall_configs = random_wall_config(n, R, wall_spacing, rng)

        x0 = m * side / 2 + m * pair_gap_mm
        flip = (m % 2 == 1)
        poly = transform(base_poly, x0, side, height, flip)
        etch = [tuple(transform(seg, x0, side, height, flip)) for seg in base_etch]
        cutouts = [transform(p, x0, side, height, flip) for p in base_cutouts]
        walls = []
        off = None
        if not flip:
            sx = -1.0 if m < center else 1.0
            off = np.array([sx * slide * 0.5, slide * np.sqrt(3) / 2])
            poly = [p + off for p in poly]
            etch = [(a + off, b + off) for a, b in etch]
            cutouts = [[p + off for p in pent] for pent in cutouts]
        for a, b in wall_segments:
            ta = transform([a], x0, side, height, flip)[0]
            tb = transform([b], x0, side, height, flip)[0]
            if off is not None:
                ta = ta + off
                tb = tb + off
            walls.append((ta, tb))
        placed.append((panel_id, poly, etch, cutouts, walls, wall_configs))
    return placed


def tessellated_pair_bbox_mm(height_in, interior_side=8, tip_clip=12.0, cutout_wall_height=0.8,
                             pair_gap_mm=SHEET_PAIR_GAP_MM):
    """Bounding box (mm) of two panels tessellated with ``pair_gap_mm`` horizontal offset."""
    n, R, tip_clip, cutout_wall_height = geometry_params(
        interior_side, tip_clip, height_in, cutout_wall_height)
    side = (n - 1) * np.sqrt(3) * R
    height = (n - 1) * 1.5 * R
    base_poly, base_etch, base_cutouts = snub_triangle(n, R, tip_clip, cutout_wall_height)
    pair = build_tessellated_pair(
        base_poly, base_etch, base_cutouts, n, R, side, height, tip_clip,
        [1, 2], 1.0, PANEL_WALL_SEEDS, pair_gap_mm=pair_gap_mm)
    polys = [poly for _, poly, _, _, _, _ in pair]
    walls = [seg for _, _, _, _, segs, _ in pair for seg in segs]
    return geometry_bbox_mm(polys, walls)


def height_in_for_vertical_gap(sheet_height_in, vertical_gap_mm, interior_side=8, tip_clip=12.0,
                               cutout_wall_height=0.8, pair_gap_mm=SHEET_PAIR_GAP_MM):
    """``height_in`` so a tessellated pair has ``vertical_gap_mm`` to top and bottom sheet edges."""
    target_h = sheet_height_in * MM_PER_INCH - 2 * vertical_gap_mm
    lo, hi = 8.0, 14.0
    for _ in range(50):
        mid = (lo + hi) / 2
        minx, miny, maxx, maxy = tessellated_pair_bbox_mm(
            mid, interior_side, tip_clip, cutout_wall_height, pair_gap_mm)
        if maxy - miny > target_h:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def center_on_sheet(triangles, sheet_width_in, sheet_height_in,
                    vertical_gap_mm=SHEET_VERTICAL_GAP_MM,
                    horizontal_margin_mm=SHEET_HORIZONTAL_MARGIN_MM):
    """Place a triangle group on the sheet with fixed vertical inset and centered horizontally."""
    polys = [poly for _, poly, _, _, _, _ in triangles]
    walls = [seg for _, _, _, _, segs, _ in triangles for seg in segs]
    minx, miny, maxx, maxy = geometry_bbox_mm(polys, walls)
    pair_w = maxx - minx
    sheet_w = sheet_width_in * MM_PER_INCH
    inset_x = min(horizontal_margin_mm, max(0.0, (sheet_w - pair_w) / 2))
    off_x = inset_x + max(0.0, (sheet_w - 2 * inset_x - pair_w) / 2) - minx
    off_y = vertical_gap_mm - miny
    offset = np.array([off_x, off_y])
    centered = []
    for panel_id, poly, etch, cutouts, walls, configs in triangles:
        poly, etch, cutouts, walls = apply_offset(poly, etch, cutouts, walls, offset)
        centered.append((panel_id, poly, etch, cutouts, walls, configs))
    return centered


def save_laser_sheet(path, sheet_width_in, sheet_height_in, triangles,
                     cut='black', mark='green', wall='green', *, etch_only=False):
    """Write a fixed-size cut sheet with one or more placed triangles."""
    sheet_w_px = sheet_width_in * MM_PER_INCH * PX_PER_MM
    sheet_h_px = sheet_height_in * MM_PER_INCH * PX_PER_MM
    d = draw.Drawing(sheet_w_px, sheet_h_px, origin=(0, 0))
    for _, poly, etch, cutouts, wall_segments, _ in triangles:
        if not etch_only:
            add_perimeter(d, poly, cut, stroke_width=5)
            add_cutouts(d, cutouts, cut, stroke_width=2)
        add_etch(d, etch, mark, stroke_width=3)
        add_wall_lines(d, wall_segments, wall, stroke_width=2)
    d.save_svg(path)


def geometry_params(interior_side=8, tip_clip=12.0, height_in=None, cutout_wall_height=0.8):
    """Shared snub-triangle geometry for all production panels."""
    if height_in is None:
        height_in = height_in_for_vertical_gap(
            SHEET_HEIGHT_IN, SHEET_VERTICAL_GAP_MM, interior_side, tip_clip, cutout_wall_height)
    n = interior_side + 3
    height_mm = height_in * MM_PER_INCH + tip_clip
    R = height_mm / ((n - 1) * 1.5)
    return n, R, tip_clip, cutout_wall_height


def generate_laser_sheets(output_dir='.', interior_side=8, tip_clip=12.0,
                          height_in=None, cutout_wall_height=0.8,
                          wall_spacing=WALL_SPACING_MM, panel_seeds=PANEL_WALL_SEEDS,
                          sheet_groups=PANEL_SHEET_GROUPS,
                          sheet_width_in=SHEET_WIDTH_IN, sheet_height_in=SHEET_HEIGHT_IN,
                          vertical_gap_mm=SHEET_VERTICAL_GAP_MM,
                          horizontal_margin_mm=SHEET_HORIZONTAL_MARGIN_MM,
                          pair_gap_mm=SHEET_PAIR_GAP_MM):
    """Three laser-cut SVG files sized to actual birch sheet, two panels per file."""
    if height_in is None:
        height_in = height_in_for_vertical_gap(
            sheet_height_in, vertical_gap_mm, interior_side, tip_clip, cutout_wall_height,
            pair_gap_mm)
    n, R, tip_clip, cutout_wall_height = geometry_params(
        interior_side, tip_clip, height_in, cutout_wall_height)
    side = (n - 1) * np.sqrt(3) * R
    height = (n - 1) * 1.5 * R
    base_poly, base_etch, base_cutouts = snub_triangle(n, R, tip_clip, cutout_wall_height)

    manifest = {
        'interior_side': interior_side,
        'height_in': height_in,
        'tip_clip_mm': tip_clip,
        'cutout_wall_height_mm': cutout_wall_height,
        'wall_spacing_mm': wall_spacing,
        'material': '1/8" birch plywood',
        'sheet_nominal_size_in': [SHEET_NOMINAL_WIDTH_IN, SHEET_NOMINAL_HEIGHT_IN],
        'sheet_trim_in': SHEET_TRIM_IN,
        'sheet_size_in': [sheet_width_in, sheet_height_in],
        'vertical_gap_mm': vertical_gap_mm,
        'horizontal_margin_mm': horizontal_margin_mm,
        'pair_gap_mm': pair_gap_mm,
        'panels': {},
        'sheets': {},
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
            base_poly, base_etch, base_cutouts, n, R, side, height, tip_clip,
            panel_ids, wall_spacing, panel_seeds, pair_gap_mm=pair_gap_mm)
        centered = center_on_sheet(
            pair, sheet_width_in, sheet_height_in, vertical_gap_mm, horizontal_margin_mm)
        path = f'{output_dir}/SnubTriangleBoard-sheet-{sheet_idx}.svg'
        save_laser_sheet(path, sheet_width_in, sheet_height_in, centered)
        svg_name = path.split('/')[-1]
        manifest['sheets'][str(sheet_idx)] = {
            'svg': svg_name,
            'panels': list(panel_ids),
        }
        for panel_id, _, _, _, _, wall_configs in centered:
            manifest['panels'][str(panel_id)]['sheet'] = sheet_idx
            manifest['panels'][str(panel_id)]['svg'] = svg_name
            manifest['panels'][str(panel_id)]['walls'] = wall_configs

    manifest_path = f'{output_dir}/SnubTriangleBoard-panels.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
        f.write('\n')
    return manifest


def generate_sheetback_sheets(output_dir='.', interior_side=8, tip_clip=12.0,
                                height_in=None, cutout_wall_height=0.8,
                                wall_spacing=WALL_SPACING_MM,
                                panel_seeds=SHEETBACK_WALL_SEEDS,
                                front_seeds=PANEL_WALL_SEEDS,
                                sheet_groups=PANEL_SHEET_GROUPS,
                                sheet_width_in=SHEET_WIDTH_IN, sheet_height_in=SHEET_HEIGHT_IN,
                                vertical_gap_mm=SHEET_VERTICAL_GAP_MM,
                                horizontal_margin_mm=SHEET_HORIZONTAL_MARGIN_MM,
                                pair_gap_mm=SHEET_PAIR_GAP_MM):
    """Three etch-only back-side sheets (flip board after cut; no perimeter or cutouts)."""
    if height_in is None:
        height_in = height_in_for_vertical_gap(
            sheet_height_in, vertical_gap_mm, interior_side, tip_clip, cutout_wall_height,
            pair_gap_mm)
    n, R, tip_clip, cutout_wall_height = geometry_params(
        interior_side, tip_clip, height_in, cutout_wall_height)
    side = (n - 1) * np.sqrt(3) * R
    height = (n - 1) * 1.5 * R
    base_poly, base_etch, base_cutouts = snub_triangle(n, R, tip_clip, cutout_wall_height)

    # Validate back layouts are distinct from fronts (up to board rotation).
    front_canonical = set()
    for seed in front_seeds.values():
        rng = random.Random(seed)
        _, cfg = random_wall_config(n, R, wall_spacing, rng)
        front_canonical.add(canonical_wall_form(cfg, n, R))
    for panel_id, seed in panel_seeds.items():
        rng = random.Random(seed)
        _, cfg = random_wall_config(n, R, wall_spacing, rng)
        canon = canonical_wall_form(cfg, n, R)
        if canon in front_canonical:
            raise ValueError(
                f'sheetback panel {panel_id} seed {seed} matches a front panel up to rotation')
        front_canonical.add(canon)

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
            base_poly, base_etch, base_cutouts, n, R, side, height, tip_clip,
            panel_ids, wall_spacing, panel_seeds, pair_gap_mm=pair_gap_mm)
        centered = center_on_sheet(
            pair, sheet_width_in, sheet_height_in, vertical_gap_mm, horizontal_margin_mm)
        path = f'{output_dir}/SnubTriangleBoard-sheetback-{sheet_idx}.svg'
        save_laser_sheet(path, sheet_width_in, sheet_height_in, centered, etch_only=True)
        svg_name = path.split('/')[-1]
        sheetbacks[str(sheet_idx)] = {
            'svg': svg_name,
            'panels': list(panel_ids),
            'pairs_with_front_sheet': sheet_idx,
        }
        for panel_id, _, _, _, _, wall_configs in centered:
            sheetback_panels[str(panel_id)]['sheetback'] = sheet_idx
            sheetback_panels[str(panel_id)]['svg'] = svg_name
            sheetback_panels[str(panel_id)]['walls'] = wall_configs

    return {
        'sheetbacks': sheetbacks,
        'sheetback_panels': sheetback_panels,
        'sheetback_wall_seeds': dict(panel_seeds),
    }


def merge_sheetback_manifest(sheetback_info, manifest_path='SnubTriangleBoard-panels.json'):
    """Add sheetback section to an existing production manifest."""
    with open(manifest_path, encoding='utf-8') as f:
        manifest = json.load(f)
    manifest.update(sheetback_info)
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
        f.write('\n')
    return manifest


def generate_production_panels(output_dir='.', interior_side=8, tip_clip=12.0,
                               height_in=None, cutout_wall_height=0.8,
                               wall_spacing=WALL_SPACING_MM, panel_seeds=PANEL_WALL_SEEDS,
                               write_manifest=True):
    """Six single-triangle SVGs with identical geometry and distinct wall layouts."""
    n, R, tip_clip, cutout_wall_height = geometry_params(
        interior_side, tip_clip, height_in, cutout_wall_height)
    base_poly, base_etch, base_cutouts = snub_triangle(n, R, tip_clip, cutout_wall_height)

    manifest = {
        'interior_side': interior_side,
        'height_in': height_in,
        'tip_clip_mm': tip_clip,
        'cutout_wall_height_mm': cutout_wall_height,
        'wall_spacing_mm': wall_spacing,
        'panels': {},
    }

    for panel_id in sorted(panel_seeds):
        seed = panel_seeds[panel_id]
        rng = random.Random(seed)
        wall_segments, wall_configs = random_wall_config(n, R, wall_spacing, rng)
        path = f'{output_dir}/SnubTriangleBoard-panel-{panel_id}.svg'
        save_triangle_svg(path, base_poly, base_etch, base_cutouts, wall_segments)
        manifest['panels'][str(panel_id)] = {
            'wall_seed': seed,
            'svg': path.split('/')[-1],
            'walls': wall_configs,
        }

    manifest_path = f'{output_dir}/SnubTriangleBoard-panels.json'
    if write_manifest:
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
            f.write('\n')
    return manifest


def generate_dev_pair(output_path='SnubTriangleBoard.svg', interior_side=8, tip_clip=12.0,
                      height_in=None, cutout_wall_height=0.8, wall_spacing=WALL_SPACING_MM,
                      wall_seed=42):
    """Two tessellated snub triangles (up/down) for layout preview."""
    cut = 'black'
    mark = 'green'
    wall = 'green'

    n, R, tip_clip, cutout_wall_height = geometry_params(
        interior_side, tip_clip, height_in, cutout_wall_height)
    side = (n - 1) * np.sqrt(3) * R
    height = (n - 1) * 1.5 * R
    base_poly, base_etch, base_cutouts = snub_triangle(n, R, tip_clip, cutout_wall_height)

    # Sequential seeds from one base for quick visual comparison.
    dev_seeds = {1: wall_seed, 2: wall_seed + 1}
    pair = build_tessellated_pair(
        base_poly, base_etch, base_cutouts, n, R, side, height, tip_clip,
        [1, 2], wall_spacing, dev_seeds)

    polys = [poly for _, poly, _, _, _, _ in pair]
    walls = [seg for _, _, _, _, segs, _ in pair for seg in segs]
    minx, miny, width, height_px = drawing_bbox(polys, walls)
    d = draw.Drawing(width, height_px, origin=(minx, miny))
    for _, poly, etch, cutouts, wall_segments, _ in pair:
        add_perimeter(d, poly, cut, stroke_width=5)
        add_etch(d, etch, mark, stroke_width=3)
        add_cutouts(d, cutouts, cut, stroke_width=2)
        add_wall_lines(d, wall_segments, wall, stroke_width=2)
    d.save_svg(output_path)


if __name__ == '__main__':
    interior_side = 8
    tip_clip = 12.0
    cutout_wall_height = 0.8
    wall_spacing = WALL_SPACING_MM

    manifest = generate_laser_sheets(
        interior_side=interior_side,
        tip_clip=tip_clip,
        cutout_wall_height=cutout_wall_height,
        wall_spacing=wall_spacing,
    )
    sheetback_info = generate_sheetback_sheets(
        interior_side=interior_side,
        tip_clip=tip_clip,
        cutout_wall_height=cutout_wall_height,
        wall_spacing=wall_spacing,
    )
    merge_sheetback_manifest(sheetback_info)
    generate_production_panels(
        interior_side=interior_side,
        tip_clip=tip_clip,
        cutout_wall_height=cutout_wall_height,
        wall_spacing=wall_spacing,
        write_manifest=False,
    )
    generate_dev_pair(
        interior_side=interior_side,
        tip_clip=tip_clip,
        cutout_wall_height=cutout_wall_height,
        wall_spacing=wall_spacing,
    )
