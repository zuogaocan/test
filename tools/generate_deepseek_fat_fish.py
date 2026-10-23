#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render a chubby "DeepSeek 大肥鱼" mascot illustration.

The picture is drawn procedurally with Pillow at 2x resolution and then
downsampled, which keeps every curve smooth without needing a vector
renderer.  Run:

    python3 tools/generate_deepseek_fat_fish.py [output.png]
"""

import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

S = 2                      # supersampling factor
W, H = 1400, 1000          # final canvas size
WS, HS = W * S, H * S      # render size

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_BOLD = os.path.join(HERE, "assets", "fonts",
                         "NotoSansSC-Bold-subset.otf")
DEFAULT_OUT = os.path.join(HERE, "output", "deepseek_fat_fish.png")

TRANSPARENT = (0, 0, 0, 0)
INK = (13, 22, 62)


# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #
def sc(*values):
    """Scale canvas coordinates to the supersampled render resolution."""
    return [v * S for v in values]


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


def vertical_gradient(width, height, stops):
    """stops: [(position 0..1, rgb), ...] sorted by position."""
    column = Image.new("RGB", (1, height))
    px = column.load()
    for y in range(height):
        t = y / max(1, height - 1)
        lo, hi = stops[0], stops[-1]
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                lo, hi = stops[i], stops[i + 1]
                break
        span = max(1e-6, hi[0] - lo[0])
        local = min(1.0, max(0.0, (t - lo[0]) / span))
        px[0, y] = lerp(lo[1], hi[1], local)
    return column.resize((width, height), Image.BILINEAR).convert("RGBA")


def new_layer():
    return Image.new("RGBA", (WS, HS), TRANSPARENT)


def merge(base, layer):
    base.alpha_composite(layer)


def mask_layer(draw_fn):
    """Create an 'L' mask by running draw_fn on a drawn layer."""
    mask = Image.new("L", (WS, HS), 0)
    draw_fn(ImageDraw.Draw(mask))
    return mask


def outline(mask, color=INK, width=6.0, threshold=24):
    """Colored stroke that follows the silhouette of a mask."""
    edges = mask.filter(ImageFilter.FIND_EDGES)
    edges = edges.point(lambda v: 255 if v > threshold else 0)
    if width:
        edges = edges.filter(ImageFilter.MaxFilter(int(width) * 2 + 1))
        edges = edges.filter(ImageFilter.GaussianBlur(1.6 * S))
    shade = Image.new("RGBA", (WS, HS), color)
    shade.putalpha(edges)
    return shade


def add_shadow(layer_mask, offset=(12, 30), blur=22, opacity=70):
    shadow = Image.new("RGBA", (WS, HS), (3, 10, 30, opacity))
    shadow.putalpha(layer_mask.filter(ImageFilter.GaussianBlur(blur * S)))
    shifted = Image.new("RGBA", (WS, HS), TRANSPARENT)
    shifted.paste(shadow, (int(offset[0] * S), int(offset[1] * S)), shadow)
    return shifted


def radial_glow(center, radius, color, peak_alpha=110, steps=48):
    layer = new_layer()
    d = ImageDraw.Draw(layer)
    for i in range(steps, 0, -1):
        t = i / steps
        r = radius * t
        a = int(peak_alpha * (1 - t) ** 1.7)
        if a <= 0:
            continue
        d.ellipse(sc(center[0] - r, center[1] - r, center[0] + r, center[1] + r),
                  fill=color + (a,))
    return layer.filter(ImageFilter.GaussianBlur(24 * S))


def bezier(p0, p1, p2, steps=48):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x * S, y * S))
    return pts


def draw_text(layer, xy, text, size, fill, font_path=FONT_BOLD,
              spacing=0.0, anchor="mm", stroke=0, stroke_fill=None):
    if not os.path.exists(font_path):
        return
    font = ImageFont.truetype(font_path, int(size * S))
    x, y = xy[0] * S, xy[1] * S
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + spacing * S * (len(text) - 1)
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    d = ImageDraw.Draw(layer)
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill, anchor="lm",
               stroke_width=int(stroke * S), stroke_fill=stroke_fill)
        x += w + spacing * S



# --------------------------------------------------------------------------- #
# background
# --------------------------------------------------------------------------- #
def build_background(img):
    img.paste(vertical_gradient(WS, HS, [
        (0.00, (4, 14, 38)),
        (0.32, (9, 44, 92)),
        (0.66, (15, 84, 138)),
        (1.00, (26, 138, 168)),
    ]), (0, 0))

    # soft light pool behind the fish
    merge(img, radial_glow((790, 545), 640, (77, 107, 254), peak_alpha=95))

    # light shafts falling from the surface
    rays = new_layer()
    d = ImageDraw.Draw(rays)
    for cx, spread, alpha in ((330, 170, 16), (760, 250, 22), (1100, 190, 14)):
        d.polygon([(cx - 30, -20), (cx + 40, -20),
                   (cx + spread, 760), (cx - spread * 0.9, 760)],
                  fill=(170, 220, 255, alpha))
    rays = rays.filter(ImageFilter.GaussianBlur(30 * S))
    merge(img, rays)

    # plankton dots
    rnd = random.Random(20261023)
    dots = new_layer()
    d = ImageDraw.Draw(dots)
    for _ in range(120):
        x = rnd.uniform(0, W)
        y = rnd.uniform(0, 900)
        r = rnd.uniform(1.0, 3.2)
        a = rnd.randint(25, 90)
        d.ellipse(sc(x - r, y - r, x + r, y + r), fill=(190, 235, 255, a))
    merge(img, dots)

    # sea floor
    floor = new_layer()
    d = ImageDraw.Draw(floor)
    top = [(x, 928 + 16 * math.sin(x / 105.0) + 7 * math.sin(x / 41.0))
           for x in range(-20, W + 30, 10)]
    d.polygon([(p[0] * S, p[1] * S) for p in top] + [(WS, HS), (0, HS)],
              fill=(12, 48, 74, 255))
    d.polygon([(p[0] * S, (p[1] - 14) * S) for p in top] + [(WS, HS), (0, HS)],
              fill=(22, 74, 96, 255))
    merge(img, floor.filter(ImageFilter.GaussianBlur(1.2 * S)))

    # pebbles
    rocks = new_layer()
    d = ImageDraw.Draw(rocks)
    for x, y, r, c in ((205, 946, 26, (18, 62, 84)),
                       (1180, 952, 34, (17, 58, 80)),
                       (1055, 962, 18, (24, 78, 98)),
                       (450, 968, 14, (20, 66, 88))):
        d.ellipse(sc(x - r * 1.4, y - r * 0.75, x + r * 1.4, y + r * 0.8),
                  fill=c + (255,))
    merge(img, rocks)


def seaweed(img, x, base_y, height, lean, width, color, alpha=235):
    layer = new_layer()
    d = ImageDraw.Draw(layer)
    steps = 90
    for i in range(steps + 1):
        t = i / steps
        yy = base_y - t * height
        xx = x + lean * math.sin(t * 2.9) + 10 * math.sin(t * 6.3)
        r = width * (1 - t * 0.72)
        d.ellipse(sc(xx - r, yy - r, xx + r, yy + r), fill=color + (alpha,))
    merge(img, layer.filter(ImageFilter.GaussianBlur(0.7 * S)))


def build_flora(img):
    for x, h, lean, w, c in ((95, 330, 34, 13, (20, 122, 116)),
                             (140, 250, -26, 10, (28, 142, 118)),
                             (1275, 360, -30, 14, (18, 116, 122)),
                             (1325, 260, 24, 10, (30, 146, 124)),
                             (1205, 190, 18, 8, (26, 134, 120))):
        seaweed(img, x, 950, h, lean, w, c)

    # little coral fan
    coral = new_layer()
    d = ImageDraw.Draw(coral)
    d.arc(sc(1010, 830, 1150, 960), 200, 340, fill=(255, 138, 150, 210),
          width=int(9 * S))
    d.arc(sc(1045, 840, 1145, 950), 205, 335, fill=(255, 158, 170, 190),
          width=int(6 * S))


# --------------------------------------------------------------------------- #
# the fish
# --------------------------------------------------------------------------- #
BODY_BOX = (462, 252, 1138, 892)


def fish_body_mask():
    return mask_layer(lambda d: d.ellipse(sc(*BODY_BOX), fill=255))


def fish_tail_mask():
    """Forked fluke made of two tilted, rounded lobes."""
    upper = Image.new("L", (WS, HS), 0)
    ImageDraw.Draw(upper).ellipse(sc(200, 430, 530, 575), fill=255)
    upper = upper.rotate(-35, center=(365 * S, 502 * S),
                         resample=Image.BICUBIC)

    lower = Image.new("L", (WS, HS), 0)
    ImageDraw.Draw(lower).ellipse(sc(200, 555, 530, 700), fill=255)
    lower = lower.rotate(35, center=(365 * S, 627 * S),
                         resample=Image.BICUBIC)

    mask = ImageChops.lighter(upper, lower)
    ImageDraw.Draw(mask).ellipse(sc(450, 505, 550, 640), fill=255)
    return mask


def fish_dorsal_mask():
    left = bezier((620, 386), (700, 190), (790, 170), 36)
    right = bezier((790, 170), (900, 225), (960, 368), 36)
    pts = left + right + [(966 * S, 392 * S), (632 * S, 392 * S)]
    return mask_layer(lambda d: d.polygon(pts, fill=255))


def paste_gradient(img, mask, stops, offset=0):
    grad = vertical_gradient(WS, HS, stops)
    if offset:
        grad = ImageChops.offset(grad, 0, int(offset * S))
    img.paste(grad, (0, 0), mask)



def draw_fish(img):
    body = fish_body_mask()
    tail = fish_tail_mask()
    dorsal = fish_dorsal_mask()

    silhouette = ImageChops.lighter(body, ImageChops.lighter(tail, dorsal))
    merge(img, add_shadow(silhouette))

    # ---- tail -----------------------------------------------------------
    paste_gradient(img, tail, [(0.00, (140, 175, 255)),
                               (0.55, (92, 126, 245)),
                               (1.00, (62, 86, 216))])
    merge(img, outline(tail, width=3))

    ribs = new_layer()
    d = ImageDraw.Draw(ribs)
    for k in range(-2, 3):
        ang = math.radians(-18 + k * 18)
        d.line([(500 * S, 572 * S),
                ((500 + 265 * math.cos(ang)) * S,
                 (572 + 265 * math.sin(ang)) * S)],
               fill=(255, 255, 255, 55), width=int(5 * S))
    ribs.putalpha(ImageChops.multiply(
        ribs.getchannel("A"),
        tail.filter(ImageFilter.GaussianBlur(1.5 * S))))
    merge(img, ribs)

    # ---- dorsal fin ----------------------------------------------------
    paste_gradient(img, dorsal, [(0.10, (132, 170, 255)),
                                 (0.70, (80, 112, 240)),
                                 (1.00, (62, 88, 220))])
    merge(img, outline(dorsal, width=5))

    # ---- body -----------------------------------------------------------
    paste_gradient(img, body, [(0.00, (150, 182, 255)),
                               (0.35, (104, 138, 252)),
                               (0.72, (72, 102, 244)),
                               (1.00, (48, 66, 205))])
    merge(img, outline(body, width=7))

    # belly light
    belly = new_layer()
    d = ImageDraw.Draw(belly)
    d.ellipse(sc(600, 640, 1120, 940), fill=(206, 228, 255, 45))
    belly = belly.filter(ImageFilter.GaussianBlur(26 * S))
    belly.putalpha(ImageChops.multiply(
        belly.getchannel("A"), body.filter(ImageFilter.GaussianBlur(9 * S))))
    merge(img, belly)

    # top shine
    shine = new_layer()
    d = ImageDraw.Draw(shine)
    d.ellipse(sc(700, 306, 880, 356), fill=(255, 255, 255, 40))
    shine = shine.filter(ImageFilter.GaussianBlur(14 * S))
    shine.putalpha(ImageChops.multiply(
        shine.getchannel("A"), body.filter(ImageFilter.GaussianBlur(9 * S))))
    merge(img, shine)

    # ---- scales ---------------------------------------------------------
    scales = new_layer()
    d = ImageDraw.Draw(scales)
    for row in range(6):
        cy = 430 + row * 58
        for col in range(12):
            cx = 470 + col * 56 + (row % 2) * 28
            r = 30
            d.arc(sc(cx - r, cy - r, cx + r, cy + r), 200, 340,
                  fill=(226, 238, 255, 32), width=int(3 * S))
    scales.putalpha(ImageChops.multiply(
        scales.getchannel("A"), body.filter(ImageFilter.GaussianBlur(2 * S))))
    merge(img, scales)

    draw_face(img)



def draw_face(img):
    for cx, cy, r in ((916, 458, 55), (1042, 484, 58)):
        white = new_layer()
        d = ImageDraw.Draw(white)
        d.ellipse(sc(cx - r, cy - r, cx + r, cy + r),
                  fill=(255, 255, 255, 255))
        merge(img, white)

        ring = new_layer()
        d = ImageDraw.Draw(ring)
        d.ellipse(sc(cx - r, cy - r, cx + r, cy + r),
                  outline=INK + (255,), width=int(4 * S))
        merge(img, ring)

        px, py = cx + 9, cy + 4
        pupil = new_layer()
        d = ImageDraw.Draw(pupil)
        d.ellipse(sc(px - 33, py - 33, px + 33, py + 33),
                  fill=(24, 34, 78, 255))
        d.ellipse(sc(px - 21, py - 21, px + 21, py + 21),
                  fill=(8, 12, 30, 255))
        merge(img, pupil)

        glint = new_layer()
        d = ImageDraw.Draw(glint)
        d.ellipse(sc(px - 24, py - 26, px - 4, py - 6),
                  fill=(255, 255, 255, 240))
        d.ellipse(sc(px + 8, py + 10, px + 18, py + 20),
                  fill=(255, 255, 255, 170))
        merge(img, glint)

    # smile
    smile = new_layer()
    d = ImageDraw.Draw(smile)
    d.arc(sc(946, 542, 1084, 646), 20, 130, fill=INK + (255,),
          width=int(10 * S))
    merge(img, smile)


def fish_sparkles(img):
    layer = new_layer()
    d = ImageDraw.Draw(layer)
    for x, y, r in ((300, 240, 13), (1200, 250, 10), (245, 700, 8),
                    (1250, 820, 12), (330, 640, 9)):
        pts = []
        for i in range(8):
            a = math.pi / 4 * i
            rad = r if i % 2 == 0 else r * 0.32
            pts.append(((x + rad * math.cos(a)) * S,
                        (y + rad * math.sin(a)) * S))
        d.polygon(pts, fill=(214, 240, 255, 190))
    merge(img, layer)


def bubbles(img):
    rnd = random.Random(5150)
    layer = new_layer()
    d = ImageDraw.Draw(layer)
    for _ in range(18):
        cx = rnd.uniform(1190, 1340)
        cy = rnd.uniform(260, 600)
        r = rnd.uniform(4, 15)
        d.ellipse(sc(cx - r, cy - r, cx + r, cy + r),
                  outline=(206, 238, 255, 120),
                  width=max(2, int(1.6 * S)))
        d.ellipse(sc(cx - r * 0.45, cy - r * 0.55,
                     cx - r * 0.05, cy - r * 0.15),
                  fill=(255, 255, 255, 170))
    merge(img, layer)



def title(img):
    glow = new_layer()
    draw_text(glow, (76, 96), "DeepSeek", 112, (120, 170, 255, 210),
              spacing=2, anchor="lm")
    glow = glow.filter(ImageFilter.GaussianBlur(16 * S))
    merge(img, glow)

    wordmark = new_layer()
    draw_text(wordmark, (76, 96), "DeepSeek", 112, (255, 255, 255, 255),
              spacing=2, anchor="lm")
    merge(img, wordmark)

    sub = new_layer()
    draw_text(sub, (80, 172), "大肥鱼  ·  BIG FAT FISH", 46,
              (168, 228, 255, 245), spacing=1, anchor="lm")
    merge(img, sub)


def vignette(img):
    mask = Image.new("L", (WS, HS), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse(sc(-180, -200, W + 180, H + 220), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(120 * S))
    dark = Image.new("RGBA", (WS, HS), (2, 8, 24, 255))
    dark.putalpha(ImageChops.invert(mask).point(lambda v: int(v * 0.55)))
    merge(img, dark)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    img = Image.new("RGBA", (WS, HS), (6, 20, 46, 255))
    build_background(img)
    build_flora(img)
    fish_sparkles(img)
    draw_fish(img)
    bubbles(img)
    vignette(img)
    title(img)

    final = img.convert("RGB").resize((W, H), Image.LANCZOS)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    final.save(out, "PNG", optimize=True)
    print("saved", out, final.size)


if __name__ == "__main__":
    main()
