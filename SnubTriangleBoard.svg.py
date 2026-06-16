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


def snub_triangle(n, R, tip_clip):
    """Build one snub triangle, returning (perimeter_polygon, etch_segments) in mm."""
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
    return poly, etch


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


if __name__ == '__main__':
    cut = 'black'
    mark = 'green'

    interior_side = 8          # full (interior) hexagons along each side
    tip_clip = 9.0             # mm trimmed off each sharp tip
    height_in = 11.825         # height of the clipped triangle, in inches
    num_triangles = 2          # one rightside up and one upside down triangle, sharing an edge

    # The edge rows are half hexagons; the full interior triangle is 3 smaller per
    # side (one half-hexagon row plus the two shared corners), so add 3.
    n = interior_side + 3
    # height_in sets the height of the clipped piece; clipping removes tip_clip from
    # the apex, so the nominal (through-center) triangle is that much taller.
    height_mm = height_in * MM_PER_INCH + tip_clip
    R = height_mm / ((n - 1) * 1.5)        # hexagon circumradius (mm) chosen to hit the height
    side = (n - 1) * np.sqrt(3) * R
    height = (n - 1) * 1.5 * R

    base_poly, base_etch = snub_triangle(n, R, tip_clip)

    # Down-pointing (flip=False) side triangles slide down ALONG their shared long
    # edge (keeping it collinear, so the edge stays mostly shared) until the snub
    # nose reaches the same ground plane as the up-pointing triangles' base.  The
    # slide distance along the edge equals the chamfer length L = 2*tip_clip/sqrt(3),
    # which drops the nose by exactly tip_clip.
    center = (num_triangles - 1) / 2
    slide = 2 * tip_clip / np.sqrt(3)

    placed = []  # (perimeter_polygon, etch_segments) per triangle, in mm
    for m in range(num_triangles):
        x0 = m * side / 2
        flip = (m % 2 == 1)
        poly = transform(base_poly, x0, side, height, flip)
        etch = [tuple(transform(seg, x0, side, height, flip)) for seg in base_etch]
        if not flip:
            sx = -1.0 if m < center else 1.0  # slide along the center-facing edge
            off = np.array([sx * slide * 0.5, slide * np.sqrt(3) / 2])
            poly = [p + off for p in poly]
            etch = [(a + off, b + off) for a, b in etch]
        placed.append((poly, etch))

    xs = [p[0] * PX_PER_MM for poly, _ in placed for p in poly]
    ys = [p[1] * PX_PER_MM for poly, _ in placed for p in poly]
    margin = 20
    minx, miny = min(xs) - margin, min(ys) - margin
    width = (max(xs) + margin) - minx
    height_px = (max(ys) + margin) - miny

    d = draw.Drawing(width, height_px, origin=(minx, miny))
    for poly, etch in placed:
        add_perimeter(d, poly, cut, stroke_width=5)
        add_etch(d, etch, mark, stroke_width=3)
    d.save_svg('SnubTriangleBoard.svg')
