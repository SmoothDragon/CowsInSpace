#!/usr/bin/env python3
"""Laser/print SVGs for cow place markers and the active-cow indicator.

Place markers are flat top-down cow silhouettes (the 2D footprint the 3D cow
stands on). Each cow is white with **Holstein black patches**; cow identity is
**1–6 black pips** on a white patch on the back (not player colors).

Run: python3 CowPlaceMarker.svg.py
"""

import math
import drawsvg as draw

PX_PER_MM = 96 / 25.4

# Match spherical_cow-scad.rs body radius (mm).
COW_BODY_R = 16.0
MARKER_R = COW_BODY_R * 1.05
LEG_R = 3.2
HEAD_R = 7.0
HEAD_OFFSET = (-0.15 * COW_BODY_R, 0.55 * COW_BODY_R)
PIP_ZONE_R = 6.5

# Print the octahedron target die in a neutral tone — not white like cows.
DIE_COLOR = '#5C5C5C'
DIE_COLOR_NAME = 'slate gray'

HOLSTEIN_BLACK = '#212121'
HOLSTEIN_WHITE = '#FFFFFF'
ACTIVE_MARKER_COLOR = '#00ACC1'
BODY_FILL = HOLSTEIN_WHITE
BODY_STROKE = HOLSTEIN_BLACK
CUT_STROKE = 'black'
PIP_FILL = HOLSTEIN_BLACK

# Six cows: pip count is the only ID; each also gets a distinct Holstein patch layout.
# Patch ellipses: (dx, dy, rx, ry, rotation_deg) relative to body center (mm).
COW_MARKINGS = [
    {
        'id': 1, 'pips': 1,
        'patches': [(-5, 1, 7.5, 4.5, -25), (6, -2, 5, 8, 20)],
    },
    {
        'id': 2, 'pips': 2,
        'patches': [(4, 4, 6, 5, 10), (-6, -1, 8, 5, -15), (2, -6, 4, 6, 35)],
    },
    {
        'id': 3, 'pips': 3,
        'patches': [(-7, 3, 6, 7, 0), (5, 0, 7, 4, -30)],
    },
    {
        'id': 4, 'pips': 4,
        'patches': [(0, 5, 9, 4, 0), (-5, -4, 5, 6, 40), (7, -3, 4, 5, -10)],
    },
    {
        'id': 5, 'pips': 5,
        'patches': [(-4, -5, 7, 5, 15), (6, 4, 5, 7, -20)],
    },
    {
        'id': 6, 'pips': 6,
        'patches': [(-6, 0, 8, 6, -10), (4, -5, 6, 5, 25), (3, 6, 4, 4, 0)],
    },
]


def px(mm):
    return mm * PX_PER_MM


def pip_offsets(count, arm=PIP_ZONE_R * 0.38):
    """Standard die pip layout in marker-local mm coordinates."""
    c = (0.0, 0.0)
    if count == 1:
        return [c]
    if count == 2:
        return [(0.0, -arm), (0.0, arm)]
    if count == 3:
        return [(0.0, -arm), c, (0.0, arm)]
    if count == 4:
        return [(-arm, -arm), (arm, -arm), (-arm, arm), (arm, arm)]
    if count == 5:
        return [(-arm, -arm), (arm, -arm), c, (-arm, arm), (arm, arm)]
    if count == 6:
        return [(-arm, -arm), (0.0, -arm), (arm, -arm),
                (-arm, arm), (0.0, arm), (arm, arm)]
    raise ValueError(f'unsupported pip count {count}')


def add_circle(d, cx, cy, r_mm, **kwargs):
    d.append(draw.Circle(px(cx), px(cy), px(r_mm), **kwargs))


def add_ellipse(d, cx, cy, rx, ry, rot_deg, **kwargs):
    d.append(draw.Ellipse(px(cx), px(cy), px(rx), px(ry), rotate=rot_deg, **kwargs))


def add_leg_bumps(d, cx, cy):
    """Four stubby leg bumps — top-down view of spherical cow."""
    for angle in (135, 45, -135, -45):
        th = math.radians(angle)
        lx = cx + 0.72 * MARKER_R * math.cos(th)
        ly = cy + 0.72 * MARKER_R * math.sin(th)
        add_circle(d, lx, ly, LEG_R, fill=BODY_FILL, stroke=BODY_STROKE,
                   stroke_width=px(0.4))


def add_head_bump(d, cx, cy):
    hx = cx + HEAD_OFFSET[0]
    hy = cy + HEAD_OFFSET[1]
    add_circle(d, hx, hy, HEAD_R, fill=BODY_FILL, stroke=BODY_STROKE,
               stroke_width=px(0.4))
    # Helmet ring
    add_circle(d, hx, hy, HEAD_R * 0.55, fill='none', stroke=BODY_STROKE,
               stroke_width=px(0.35))
    # Small Holstein patch on head (visible from above)
    add_ellipse(d, hx + 1.5, hy - 0.5, 2.8, 2.0, 15, fill=HOLSTEIN_BLACK, stroke='none')


def add_holstein_patches(d, cx, cy, cow):
    """Irregular black Holstein patches on the body (top-down)."""
    for dx, dy, rx, ry, rot in cow['patches']:
        add_ellipse(d, cx + dx, cy + dy, rx, ry, rot,
                    fill=HOLSTEIN_BLACK, stroke='none')


def add_pip_marking(d, cx, cy, cow):
    """White pip zone on the back with black pips (1–6) — cow ID."""
    sx = cx - HEAD_OFFSET[0] * 1.1
    sy = cy - HEAD_OFFSET[1] * 0.35
    add_circle(d, sx, sy, PIP_ZONE_R, fill=HOLSTEIN_WHITE, stroke=HOLSTEIN_BLACK,
               stroke_width=px(0.35))
    pip_r = PIP_ZONE_R * 0.17
    for ox, oy in pip_offsets(cow['pips']):
        add_circle(d, sx + ox, sy + oy, pip_r, fill=PIP_FILL, stroke='none')


def draw_place_marker(d, cx, cy, cow, *, cut_line=True):
    """One 2D place marker centered at (cx, cy) mm."""
    add_circle(d, cx, cy, MARKER_R, fill=BODY_FILL, stroke=CUT_STROKE if cut_line else BODY_STROKE,
               stroke_width=px(0.6 if cut_line else 0.4))
    add_holstein_patches(d, cx, cy, cow)
    add_leg_bumps(d, cx, cy)
    add_head_bump(d, cx, cy)
    add_pip_marking(d, cx, cy, cow)
    label_y = cy - MARKER_R - 4
    d.append(draw.Text(f"{cow['id']} ({cow['pips']} pip)",
                       font_size=px(3), x=px(cx), y=px(label_y),
                       text_anchor='middle', fill=BODY_STROKE))


def draw_active_marker(d, cx, cy):
    """Ring + arrow tab — slips beside the active cow's place marker."""
    outer = MARKER_R + 5.5
    path = []
    steps = 72
    for i in range(steps + 1):
        t = i / steps
        angle = math.radians(200 + t * 280)
        path.extend([px(cx + outer * math.cos(angle)), px(cy + outer * math.sin(angle))])
    d.append(draw.Lines(*path, stroke=ACTIVE_MARKER_COLOR, stroke_width=px(2.2),
                        fill='none'))
    ax = cx + outer + 2
    d.append(draw.Lines(
        px(cx + outer), px(cy),
        px(ax + 5), px(cy),
        px(ax), px(cy - 4),
        px(ax), px(cy + 4),
        px(ax + 5), px(cy),
        stroke=ACTIVE_MARKER_COLOR, stroke_width=px(2.2), fill=ACTIVE_MARKER_COLOR))
    d.append(draw.Text('ACTIVE', font_size=px(3), x=px(cx), y=px(cy + outer + 7),
                       text_anchor='middle', fill=ACTIVE_MARKER_COLOR))


def save_place_marker_sheet(path='CowPlaceMarker-sheet.svg'):
    pitch = MARKER_R * 2 + 14
    cols, rows = 3, 2
    margin = 10
    width = margin * 2 + pitch * (cols - 1) + MARKER_R * 2
    height = margin * 2 + pitch * (rows - 1) + MARKER_R * 2 + 12
    d = draw.Drawing(px(width), px(height), origin=(0, 0))

    d.append(draw.Text(
        'Cow place markers — Holstein patches; 1–6 black pips identify each cow',
        font_size=px(3.2), x=px(width / 2 / PX_PER_MM), y=px(5),
        text_anchor='middle', fill=BODY_STROKE))

    for idx, cow in enumerate(COW_MARKINGS):
        col = idx % cols
        row = idx // cols
        cx = margin + MARKER_R + col * pitch
        cy = margin + MARKER_R + 8 + row * pitch
        draw_place_marker(d, cx, cy, cow)

    d.save_svg(path)
    return path


def save_active_marker_sheet(path='ActiveCowMarker.svg'):
    size = (MARKER_R + 14) * 2 + 10
    cx = cy = size / 2
    d = draw.Drawing(px(size), px(size), origin=(0, 0))
    d.append(draw.Text(
        'Active cow — place ring around the cow that is moving this turn',
        font_size=px(3.2), x=px(cx), y=px(6), text_anchor='middle', fill=BODY_STROKE))
    draw_active_marker(d, cx, cy + 4)
    d.save_svg(path)
    return path


def save_color_reference(path='ComponentColors.svg'):
    """Quick reference for print colors: cows vs die vs active marker."""
    row_h = 14
    width = 120
    margin = 10
    height = margin + row_h * (len(COW_MARKINGS) + 5) + 10
    d = draw.Drawing(px(width), px(height), origin=(0, 0))
    y = margin + 6

    def swatch(color, label, note=''):
        nonlocal y
        d.append(draw.Rectangle(px(10), px(y - 4), px(8), px(8),
                                fill=color, stroke=BODY_STROKE, stroke_width=px(0.3)))
        d.append(draw.Text(label, font_size=px(3.2), x=px(22), y=px(y + 2), fill=BODY_STROKE))
        if note:
            d.append(draw.Text(note, font_size=px(2.6), x=px(62), y=px(y + 2), fill='#666'))
        y += row_h

    d.append(draw.Text('Component colors', font_size=px(4),
                       x=px(width / 2 / PX_PER_MM), y=px(margin + 2),
                       text_anchor='middle', fill=BODY_STROKE))
    y += 8
    swatch(HOLSTEIN_WHITE, 'Cow body', 'white')
    swatch(HOLSTEIN_BLACK, 'Holstein patches + pips', 'black')
    for cow in COW_MARKINGS:
        swatch(HOLSTEIN_WHITE, f"Cow {cow['id']}", f"{cow['pips']} black pip(s)")
    swatch(DIE_COLOR, f'Target die ({DIE_COLOR_NAME})', 'not white')
    swatch(ACTIVE_MARKER_COLOR, 'Active cow marker', 'cyan ring')
    d.save_svg(path)
    return path


if __name__ == '__main__':
    save_place_marker_sheet()
    save_active_marker_sheet()
    save_color_reference()
    print('Wrote CowPlaceMarker-sheet.svg, ActiveCowMarker.svg, ComponentColors.svg')
