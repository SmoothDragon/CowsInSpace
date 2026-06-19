#!/usr/bin/env python3
"""Compose hex constellation and hex crater overlays onto box cover base art."""

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def hex_points(cx, cy, radius, *, pointy_top=True, angle_jitter=0.12, radius_jitter=0.18, seed=0):
    """Exactly six vertices; slightly irregular but clearly hexagonal."""
    rng = random.Random(seed)
    start = math.pi / 6 if pointy_top else 0.0
    start += rng.uniform(-angle_jitter, angle_jitter)
    pts = []
    for i in range(6):
        a = start + i * math.pi / 3
        r = radius * (1 + rng.uniform(-radius_jitter, radius_jitter))
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def inset_polygon(pts, scale):
    cx = sum(p[0] for p in pts) / 6
    cy = sum(p[1] for p in pts) / 6
    return [(cx + (p[0] - cx) * scale, cy + (p[1] - cy) * scale) for p in pts]


def add_hex_constellation(img, *, seed=7):
    """Faint blue hex grid connecting star-like nodes across the sky."""
    w, h = img.size
    overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    r = int(w * 0.042)
    dx = math.sqrt(3) * r
    dy = 1.5 * r
    line_w = max(2, w // 512)
    line_color = (90, 170, 255, 130)
    star_color = (210, 235, 255, 200)

    rows = int(h / dy) + 3
    cols = int(w / dx) + 3
    idx = 0
    for row in range(rows):
        for col in range(cols):
            cx = col * dx + (row % 2) * dx / 2 - dx * 0.3
            cy = row * dy - dy * 0.2
            if cx < -r or cx > w + r or cy < -r or cy > h * 0.94:
                continue
            if cy < h * 0.18:
                continue
            # Keep constellation in sky, not over cow/moon focal areas.
            if w * 0.30 < cx < w * 0.72 and h * 0.28 < cy < h * 0.78:
                continue
            pts = hex_points(cx, cy, r * 0.92, seed=seed + idx)
            idx += 1
            draw.line(pts + [pts[0]], fill=line_color, width=line_w)
            for px, py in pts:
                sr = max(2, w // 340)
                draw.ellipse([px - sr, py - sr, px + sr, py + sr], fill=star_color)

    glow = overlay.filter(ImageFilter.GaussianBlur(radius=max(1, w // 700)))
    return Image.alpha_composite(img.convert('RGBA'), glow)


def sample_moon_color(img, x0, y0, x1, y1):
    arr = np.asarray(img.crop((x0, y0, x1, y1)).convert('RGB'), float)
    return tuple(arr.mean(axis=(0, 1)).astype(int))


def add_hex_craters(img, *, seed=19):
    """Six-sided hex craters on the moon in the bottom-right."""
    w, h = img.size
    work = img.convert('RGBA')
    overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    moon_x0 = int(w * 0.52)
    moon_y0 = int(h * 0.58)
    moon_x1 = w
    moon_y1 = h
    base = sample_moon_color(work, moon_x0, moon_y0, moon_x1, moon_y1)
    rim = tuple(min(255, c + 42) for c in base)
    shadow = tuple(max(0, c - 40) for c in base)
    deep = tuple(max(0, c - 85) for c in base)

    wash = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    wash_draw = ImageDraw.Draw(wash)
    wash_draw.rectangle([moon_x0, moon_y0, moon_x1, moon_y1], fill=(*base, 100))
    wash = wash.filter(ImageFilter.GaussianBlur(radius=max(8, w // 180)))
    work = Image.alpha_composite(work, wash)

    placements = [
        (0.78, 0.82, 0.12),
        (0.68, 0.74, 0.09),
        (0.88, 0.70, 0.10),
        (0.62, 0.88, 0.08),
        (0.82, 0.64, 0.075),
        (0.72, 0.92, 0.07),
        (0.92, 0.86, 0.065),
        (0.58, 0.68, 0.06),
        (0.95, 0.74, 0.055),
    ]
    for i, (fx, fy, fr) in enumerate(placements):
        cx = fx * w
        cy = fy * h
        radius = fr * w
        pts = hex_points(
            cx, cy, radius,
            pointy_top=(i % 2 == 0),
            angle_jitter=0.06,
            radius_jitter=0.12,
            seed=seed + i * 17,
        )
        draw.polygon(pts, fill=(*shadow, 255), outline=(*rim, 255))
        inner = inset_polygon(pts, 0.74)
        draw.polygon(inner, fill=(*deep, 240))
        core = inset_polygon(pts, 0.42)
        draw.polygon(core, fill=(*deep, 210))

    return Image.alpha_composite(work, overlay)


def crop_cover_art(img):
    """Square crop; for 3D box mockups, take the front cover panel not the spine."""
    w, h = img.size
    side = min(w, h)
    if w > side * 1.25:
        left = int(w * 0.14)
        return img.crop((left, 0, left + side, side))
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def compose_cover(base_path, out_path, *, out_size=2048):
    img = Image.open(base_path).convert('RGB')
    img = crop_cover_art(img)
    if out_size and img.width != out_size:
        img = img.resize((out_size, out_size), Image.LANCZOS)
    img = add_hex_constellation(img)
    img = add_hex_craters(img)
    img.convert('RGB').save(out_path, quality=95)
    return out_path


def compose_from_original(original_path, out_path, *, out_size=2048):
    """Use the first approved cover for the cow; overlay precise hex geometry."""
    return compose_cover(original_path, out_path, out_size=out_size)


if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    assets = Path('/home/tom/.cursor/projects/home-tom-my-github-CowsInSpace/assets')
    original = assets / 'CowsInSpace-box-cover.png'
    base = root / 'CowsInSpace-box-cover-base.png'
    if original.exists():
        src = original
    elif base.exists():
        src = base
    elif (assets / 'CowsInSpace-box-cover-base.png').exists():
        src = assets / 'CowsInSpace-box-cover-base.png'
    else:
        raise SystemExit('No cover base image found')
    out = root / 'CowsInSpace-box-cover.png'
    compose_cover(src, out)
    print(f'Wrote {out} from {src}')
