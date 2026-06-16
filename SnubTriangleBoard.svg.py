import numpy as np
import drawsvg as draw

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


if __name__ == '__main__':
    cut = 'black'
    mark = 'green'

    interior_side = 8          # full (interior) hexagons along each side
    tip_clip = 12.0             # mm trimmed off each sharp tip
    height_in = 11.825         # height of the clipped triangle, in inches
    num_triangles = 2          # one rightside up and one upside down triangle, sharing an edge
    cutout_wall_height = 0.8   # mm height of house cutout side walls / snub offset

    # The edge rows are half hexagons; the full interior triangle is 3 smaller per
    # side (one half-hexagon row plus the two shared corners), so add 3.
    n = interior_side + 3
    # height_in sets the height of the clipped piece; clipping removes tip_clip from
    # the apex, so the nominal (through-center) triangle is that much taller.
    height_mm = height_in * MM_PER_INCH + tip_clip
    R = height_mm / ((n - 1) * 1.5)        # hexagon circumradius (mm) chosen to hit the height
    side = (n - 1) * np.sqrt(3) * R
    height = (n - 1) * 1.5 * R

    base_poly, base_etch, base_cutouts = snub_triangle(n, R, tip_clip, cutout_wall_height)

    # Down-pointing (flip=False) side triangles slide down ALONG their shared long
    # edge (keeping it collinear, so the edge stays mostly shared) until the snub
    # nose reaches the same ground plane as the up-pointing triangles' base.  The
    # slide distance along the edge equals the chamfer length L = 2*tip_clip/sqrt(3),
    # which drops the nose by exactly tip_clip.
    center = (num_triangles - 1) / 2
    slide = 2 * tip_clip / np.sqrt(3)

    placed = []  # (perimeter_polygon, etch_segments, cutouts) per triangle, in mm
    for m in range(num_triangles):
        x0 = m * side / 2
        flip = (m % 2 == 1)
        poly = transform(base_poly, x0, side, height, flip)
        etch = [tuple(transform(seg, x0, side, height, flip)) for seg in base_etch]
        cutouts = [transform(p, x0, side, height, flip) for p in base_cutouts]
        if not flip:
            sx = -1.0 if m < center else 1.0  # slide along the center-facing edge
            off = np.array([sx * slide * 0.5, slide * np.sqrt(3) / 2])
            poly = [p + off for p in poly]
            etch = [(a + off, b + off) for a, b in etch]
            cutouts = [[p + off for p in pent] for pent in cutouts]
        placed.append((poly, etch, cutouts))

    xs = [p[0] * PX_PER_MM for poly, _, _ in placed for p in poly]
    ys = [p[1] * PX_PER_MM for poly, _, _ in placed for p in poly]
    margin = 20
    minx, miny = min(xs) - margin, min(ys) - margin
    width = (max(xs) + margin) - minx
    height_px = (max(ys) + margin) - miny

    d = draw.Drawing(width, height_px, origin=(minx, miny))
    for poly, etch, cutouts in placed:
        add_perimeter(d, poly, cut, stroke_width=5)
        add_etch(d, etch, mark, stroke_width=3)
        add_cutouts(d, cutouts, cut, stroke_width=2)
    d.save_svg('SnubTriangleBoard.svg')
