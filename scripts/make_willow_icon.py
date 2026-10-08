#!/usr/bin/env python3
"""Paint the Bober Willow Cut app mark.

Daylight coppice stool: low wide stump, upright willow wands, one yellow
cut face, soil bank, creek band. Not a lodge, not a face, not a flame.

Outputs under assets/icons/:
  bober-willow.ico, willow-192.png, willow-512.png, willow-maskable-512.png
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "icons"

WILLOW = (0x2F, 0x8A, 0x45)
CREEK = (0x2B, 0x86, 0xA8)
SOIL = (0x6E, 0x46, 0x32)
CUT = (0xF6, 0xD3, 0x6B)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


MEADOW = mix(WILLOW, WHITE, 0.78)
MEADOW_DEEP = mix(WILLOW, WHITE, 0.55)
BARK = mix(SOIL, BLACK, 0.22)
BARK_LIT = mix(SOIL, CUT, 0.28)
SAP = mix(CUT, WHITE, 0.28)
RING = mix(SOIL, CUT, 0.42)
WATER_LIT = mix(CREEK, WHITE, 0.35)
WATER_DEEP = mix(CREEK, BLACK, 0.18)
WAND = mix(WILLOW, BLACK, 0.08)
WAND_LIT = mix(WILLOW, WHITE, 0.22)
WAND_DEEP = mix(WILLOW, BLACK, 0.28)
BUD = mix(WILLOW, WHITE, 0.40)


def wave(px: int, y_mid: float, amp: float, turns: float, y_floor: float) -> list[tuple[float, float]]:
    steps = 64
    pts: list[tuple[float, float]] = []
    for i in range(steps + 1):
        x = px * i / steps
        y = y_mid + math.sin(turns * math.tau * i / steps) * amp
        pts.append((x, y))
    pts.append((px, y_floor))
    pts.append((0, y_floor))
    return pts


def lance(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    angle: float,
    length: float,
    width: float,
    color: tuple[int, int, int],
) -> None:
    """Narrow willow leaf. The base sits on (x, y); the tip points along angle."""
    ca, sa = math.cos(angle), math.sin(angle)
    px, py = -sa, ca
    pts = [(x, y)]
    n = 8
    for i in range(1, n):
        t = i / n
        w = width * math.sin(t * math.pi) * (1.0 - 0.35 * t)
        along = length * t
        pts.append((x + ca * along + px * w, y + sa * along + py * w))
    pts.append((x + ca * length, y + sa * length))
    for i in range(n - 1, 0, -1):
        t = i / n
        w = width * math.sin(t * math.pi) * (1.0 - 0.35 * t)
        along = length * t
        pts.append((x + ca * along - px * w, y + sa * along - py * w))
    draw.polygon(pts, fill=color)


def wand(
    draw: ImageDraw.ImageDraw,
    x: float,
    y_base: float,
    height: float,
    lean: float,
    width: float,
    color: tuple[int, int, int],
    leaf_color: tuple[int, int, int],
) -> None:
    y_tip = y_base - height
    x_tip = x + lean
    half_b = width * 0.46
    half_t = width * 0.20
    draw.polygon(
        [
            (x - half_b, y_base),
            (x + half_b, y_base),
            (x_tip + half_t, y_tip + width * 0.35),
            (x_tip, y_tip),
            (x_tip - half_t, y_tip + width * 0.35),
        ],
        fill=color,
    )
    # Alternate leaves on the upper wand only, so the tip stays a point.
    stem = math.atan2(y_tip - y_base, x_tip - x)
    for along, side, leng in ((0.42, -1.0, 0.20), (0.62, 1.0, 0.17), (0.80, -1.0, 0.14)):
        bx = x + (x_tip - x) * along
        by = y_base + (y_tip - y_base) * along
        lance(
            draw,
            bx,
            by,
            stem + side * 1.15,
            height * leng,
            width * 0.55,
            leaf_color if side < 0 else mix(leaf_color, WHITE, 0.2),
        )


def paint(px: int, stool_scale: float) -> Image.Image:
    im = Image.new("RGB", (px, px), MEADOW)
    d = ImageDraw.Draw(im)

    # Far meadow band. Flat color, no glow, no sky disc.
    d.rectangle((0, int(px * 0.46), px, px), fill=MEADOW_DEEP)

    d.polygon(wave(px, px * 0.80, px * 0.012, 1.5, px), fill=WATER_DEEP)
    d.polygon(wave(px, px * 0.785, px * 0.014, 1.5, px), fill=CREEK)
    # One ripple, a stroke, not a moon.
    ripple = []
    for i in range(48):
        x = px * (0.12 + 0.76 * i / 47)
        y = px * 0.88 + math.sin(i / 47 * math.tau * 2.0) * px * 0.008
        ripple.append((x, y))
    d.line(ripple, fill=WATER_LIT, width=max(2, px // 128))

    d.polygon(wave(px, px * 0.74, px * 0.016, 1.2, px * 0.86), fill=mix(SOIL, BLACK, 0.12))
    d.polygon(wave(px, px * 0.715, px * 0.012, 1.2, px * 0.82), fill=SOIL)

    cx = px * 0.50
    top_y = px * (0.56 + (1.0 - stool_scale) * 0.06)
    body_h = px * 0.16 * stool_scale
    top_rx = px * 0.30 * stool_scale
    top_ry = top_rx * 0.34
    bot_rx = top_rx * 1.18
    base_y = top_y + body_h

    # Wands behind the cut face. Uneven heights so it cannot read as a roof.
    shoots = (
        (-0.78, 0.92, -0.10, 0.10, WAND_DEEP, WAND),
        (-0.46, 1.18, -0.05, 0.115, WAND, WAND_LIT),
        (-0.14, 1.42, 0.02, 0.12, WAND_LIT, BUD),
        (0.22, 1.05, 0.06, 0.10, WAND, WAND_LIT),
        (0.52, 1.28, 0.09, 0.11, WAND_DEEP, WAND),
        (0.78, 0.78, 0.12, 0.09, WAND, BUD),
    )
    for ux, uh, lean, uw, col, leaf_col in shoots:
        wand(
            d,
            cx + top_rx * ux,
            top_y + top_ry * 0.15,
            px * 0.30 * stool_scale * uh,
            px * lean * stool_scale,
            px * uw * stool_scale,
            col,
            leaf_col,
        )

    # Low stump. Wider than it is tall. Vertical grain only.
    d.polygon(
        [
            (cx - top_rx, top_y),
            (cx + top_rx, top_y),
            (cx + bot_rx, base_y),
            (cx - bot_rx * 0.92, base_y),
        ],
        fill=BARK_LIT,
    )
    d.polygon(
        [
            (cx - top_rx * 0.15, top_y),
            (cx + top_rx, top_y),
            (cx + bot_rx, base_y),
            (cx + top_rx * 0.05, base_y),
        ],
        fill=BARK,
    )
    grain = max(2, px // 160)
    for gx, gy0, gy1 in (
        (-0.55, 0.08, 0.92),
        (-0.28, 0.02, 0.84),
        (0.02, 0.1, 0.78),
        (0.30, 0.04, 0.7),
    ):
        x0 = cx + top_rx * gx
        x1 = cx + bot_rx * gx * 0.9
        d.line(
            [(x0, top_y + body_h * gy0), (x1, top_y + body_h * gy1)],
            fill=mix(BARK, BLACK, 0.25),
            width=grain,
        )

    # Elliptical cut face — fresh willow, not a badge circle.
    box = (cx - top_rx, top_y - top_ry, cx + top_rx, top_y + top_ry)
    d.ellipse(box, fill=CUT)
    ring = (
        cx - top_rx * 0.62,
        top_y - top_ry * 0.52,
        cx + top_rx * 0.62,
        top_y + top_ry * 0.52,
    )
    d.ellipse(ring, outline=RING, width=max(3, px // 72))
    d.ellipse(
        (
            cx - top_rx * 0.07,
            top_y - top_ry * 0.07,
            cx + top_rx * 0.09,
            top_y + top_ry * 0.09,
        ),
        fill=SAP,
    )

    # A short new wand in front of the cut: the stool is already growing back.
    wand(
        d,
        cx + top_rx * 0.34,
        top_y + top_ry * 0.55,
        px * 0.16 * stool_scale,
        px * 0.03 * stool_scale,
        px * 0.055 * stool_scale,
        BUD,
        WAND_LIT,
    )

    # Root flare tucked into the bank, not a doorway.
    d.polygon(
        [
            (cx - bot_rx * 0.55, base_y - px * 0.01),
            (cx - bot_rx * 1.05, base_y + px * 0.035 * stool_scale),
            (cx - bot_rx * 0.35, base_y + px * 0.02),
        ],
        fill=BARK,
    )
    d.polygon(
        [
            (cx + bot_rx * 0.45, base_y - px * 0.008),
            (cx + bot_rx * 1.02, base_y + px * 0.03 * stool_scale),
            (cx + bot_rx * 0.2, base_y + px * 0.018),
        ],
        fill=mix(BARK, BLACK, 0.15),
    )
    return im


def save_ico(path: Path, master: Image.Image) -> None:
    sizes = (16, 24, 32, 48, 64, 128, 256)
    frames = [master.resize((s, s), Image.Resampling.LANCZOS) for s in sizes]
    frames[-1].save(
        path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=frames[:-1],
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    master = paint(1024, stool_scale=1.0)
    maskable = paint(1024, stool_scale=0.70)
    master.resize((512, 512), Image.Resampling.LANCZOS).save(OUT / "willow-512.png", optimize=True)
    master.resize((192, 192), Image.Resampling.LANCZOS).save(OUT / "willow-192.png", optimize=True)
    maskable.resize((512, 512), Image.Resampling.LANCZOS).save(OUT / "willow-maskable-512.png", optimize=True)
    save_ico(OUT / "bober-willow.ico", master)
    print(f"wrote {OUT / 'bober-willow.ico'}")
    print(f"wrote {OUT / 'willow-192.png'}")
    print(f"wrote {OUT / 'willow-512.png'}")
    print(f"wrote {OUT / 'willow-maskable-512.png'}")


if __name__ == "__main__":
    main()
