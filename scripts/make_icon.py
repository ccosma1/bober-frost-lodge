#!/usr/bin/env python3
"""Bober Frost Lodge — original app-mark painter.

Snow-capped stick-lodge mound + hearth flame on a full-bleed night-purple
square. Winter colony: hold the fire.

Composition unique to this game: squat dome hut, cream snow hat with
overhang, chimney hole, tall flame, timber door, ear-bumps on the lintel.
Not a beaver-face portrait, not a sling-V, not stacked capsule logs, not
a rounded-square badge with an inner glow-circle.

Outputs under assets/icons/:
  bober-frost.ico, icon-192.png, icon-512.png, icon-maskable-512.png
"""

from __future__ import annotations

import math
import random
import struct
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / "assets" / "icons"

NIGHT = (0x3A, 0x2A, 0x6A)
LODGE = (0x8B, 0x5A, 0x2B)
FLAME_Y = (0xF5, 0xC4, 0x00)
SNOW = (0xF4, 0xE6, 0xC3)
TIMBER = (0x5C, 0x3A, 0x1A)
FLAME_O = (0xE8, 0x6A, 0x2A)
ICE = (0xA8, 0xC4, 0xE8)

INK = (0x24, 0x16, 0x10)
STICK = (0x6A, 0x42, 0x1E)
LODGE_WARM = (0xA3, 0x6C, 0x36)
SNOW_SHADE = (0xE0, 0xCC, 0xA4)
FLAME_CORE = (0xFF, 0xF0, 0xC4)
HEARTH = (0xF0, 0x9A, 0x3A)

MASTER = 1024
ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)


def _dome_arc(
    cx: float,
    top: float,
    base: float,
    half_w: float,
    power: float,
    n: int = 64,
) -> list[tuple[float, float]]:
    """Upper outline of a squat superellipse dome (left → right). Not a circle."""
    pts: list[tuple[float, float]] = []
    for i in range(n + 1):
        u = -1.0 + 2.0 * i / n
        rise = (1.0 - abs(u) ** power) ** (1.0 / power)
        pts.append((cx + half_w * u, base - (base - top) * rise))
    return pts


def _closed_dome(
    cx: float,
    top: float,
    base: float,
    half_w: float,
    power: float,
    n: int = 64,
) -> list[tuple[float, float]]:
    arc = _dome_arc(cx, top, base, half_w, power, n)
    return arc + [(cx + half_w, base), (cx - half_w, base)]


def _flame_tongue(
    cx: float,
    y_tip: float,
    y_base: float,
    half_w: float,
    lean: float,
    n: int = 30,
) -> list[tuple[float, float]]:
    """Tall pointed tongue. One flame, not stacked glow-orbs."""
    h = y_base - y_tip
    left: list[tuple[float, float]] = []
    right: list[tuple[float, float]] = []
    for i in range(n + 1):
        t = i / n
        bloom = math.sin(math.pi * t) ** 0.70
        side = half_w * bloom
        y = y_tip + h * t
        drift = lean * (1.0 - t) * (1.0 - t)
        left.append((cx + drift - side, y))
        right.append((cx + drift + side, y))
    return left + right[::-1]


def _stroke(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], fill, width: int) -> None:
    if width < 1 or len(pts) < 2:
        return
    draw.line(pts + [pts[0]], fill=fill, width=width, joint="curve")
    r = max(1, width // 2)
    for x, y in (pts[0], pts[-1]):
        draw.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def paint_lodge(size: int, *, pad: float = 0.0, simple: bool = False) -> Image.Image:
    """Paint the Frost Lodge mark onto a full-bleed night-purple square."""
    im = Image.new("RGB", (size, size), NIGHT)
    d = ImageDraw.Draw(im)

    margin = pad * size
    box = size - 2 * margin

    def X(nx: float) -> int:
        return int(round(margin + nx * box))

    def Y(ny: float) -> int:
        return int(round(margin + ny * box))

    def poly(pts: list[tuple[float, float]]) -> list[tuple[int, int]]:
        return [(X(x), Y(y)) for x, y in pts]

    def wpx(frac: float) -> int:
        return max(1, int(round(frac * box)))

    def oval(b: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
        return (X(b[0]), Y(b[1]), X(b[2]), Y(b[3]))

    cx = 0.50
    ink_w = wpx(0.036 if simple else 0.028)

    # Short snow pillow under the hut — a discrete drift, not a cream floor bar.
    bank = [
        (0.18, 0.92),
        (0.12, 0.86),
        (0.18, 0.80),
        (0.32, 0.77),
        (0.50, 0.75),
        (0.68, 0.77),
        (0.82, 0.80),
        (0.88, 0.86),
        (0.82, 0.92),
        (0.66, 0.96),
        (0.50, 0.97),
        (0.34, 0.96),
    ]
    d.polygon(poly(bank), fill=SNOW)
    d.ellipse((X(0.28), Y(0.84), X(0.72), Y(0.96)), fill=SNOW_SHADE)
    d.ellipse((X(0.32), Y(0.86), X(0.68), Y(0.96)), fill=SNOW)
    _stroke(d, poly(bank), INK, max(1, ink_w // 2))

    # Brown stick-lodge mound: squat dome, wider than tall.
    mound_pts = _closed_dome(cx=cx, top=0.36, base=0.85, half_w=0.335, power=1.55, n=72)
    mound = poly(mound_pts)
    d.polygon(mound, fill=LODGE)

    if not simple:
        hatch = Image.new("L", (size, size), 0)
        ImageDraw.Draw(hatch).polygon(mound, fill=255)
        sticks = Image.new("RGB", (size, size), LODGE)
        sd = ImageDraw.Draw(sticks)
        rng = random.Random(19)
        sw = max(2, wpx(0.010))
        for _ in range(55):
            x0 = rng.uniform(0.18, 0.82)
            y0 = rng.uniform(0.48, 0.84)
            ang = rng.choice((0.55, 0.70, 2.45, 2.60))
            length = rng.uniform(0.07, 0.16)
            x1 = x0 + length * math.cos(ang)
            y1 = y0 + length * math.sin(ang)
            sd.line((X(x0), Y(y0), X(x1), Y(y1)), fill=STICK, width=sw)
        im.paste(sticks, (0, 0), hatch)

    _stroke(d, mound, INK, ink_w)

    # Twigs poking from the shoulders — short radial nubs, never capsule logs.
    if not simple:
        for u, lift in ((-0.92, 0.02), (-0.70, 0.04), (0.70, 0.04), (0.92, 0.02)):
            nx = cx + 0.335 * u
            rise = (1.0 - abs(u) ** 1.55) ** (1.0 / 1.55)
            ny = 0.85 - (0.85 - 0.36) * rise
            s = 1.0 if u > 0 else -1.0
            nub = [
                (nx - s * 0.010, ny - 0.008),
                (nx + s * 0.058, ny - 0.018 - lift),
                (nx + s * 0.016, ny + 0.016),
            ]
            d.polygon(poly(nub), fill=TIMBER)
            _stroke(d, poly(nub), INK, max(1, ink_w // 3))

    # Cream snow hat with side overhang — the 32px white mound.
    hat_arc = _dome_arc(cx=cx, top=0.26, base=0.56, half_w=0.40, power=1.70, n=72)
    drape: list[tuple[float, float]] = []
    for i in range(22):
        t = i / 21
        x = cx + 0.40 - t * 0.80
        y = 0.53 + 0.030 * math.sin(t * math.pi * 3.0) + 0.010 * math.sin(t * math.pi * 6.5)
        drape.append((x, y))
    hat = poly(hat_arc + drape)
    d.polygon(hat, fill=SNOW)
    _stroke(d, hat, INK, ink_w)

    # Ice-blue sheen on the snow cap only (winter, not cyan-neon, not a moon).
    hi: list[tuple[float, float]] = []
    for i in range(20):
        t = 2.0 * math.pi * i / 20
        hi.append((0.39 + 0.105 * math.cos(t), 0.36 + 0.048 * math.sin(t)))
    d.polygon(poly(hi), fill=ICE)

    # Smoke-hole at the apex.
    d.ellipse((X(0.438), Y(0.288), X(0.562), Y(0.360)), fill=INK)
    d.ellipse((X(0.452), Y(0.300), X(0.548), Y(0.348)), fill=TIMBER)

    # Tall hearth flame — 32px hero together with the mound.
    outer = poly(_flame_tongue(0.50, 0.028, 0.345, 0.088, lean=-0.030))
    mid = poly(_flame_tongue(0.496, 0.072, 0.338, 0.054, lean=-0.018))
    inner = poly(_flame_tongue(0.494, 0.118, 0.330, 0.026, lean=-0.010))
    d.polygon(outer, fill=FLAME_O)
    _stroke(d, outer, INK, max(2, ink_w // 2))
    d.polygon(mid, fill=FLAME_Y)
    d.polygon(inner, fill=FLAME_CORE)
    if not simple:
        lick = poly(_flame_tongue(0.585, 0.145, 0.322, 0.032, lean=0.024))
        d.polygon(lick, fill=FLAME_O)
        _stroke(d, lick, INK, max(1, ink_w // 3))
        d.polygon(poly(_flame_tongue(0.580, 0.175, 0.318, 0.016, lean=0.012)), fill=FLAME_Y)

    # Dark timber doorway: a hole, not a face.
    door = [X(0.405), Y(0.58), X(0.595), Y(0.835)]
    rad = wpx(0.048)
    d.rounded_rectangle(door, radius=rad, fill=INK)
    d.rounded_rectangle(
        [X(0.422), Y(0.598), X(0.578), Y(0.820)],
        radius=max(2, rad - 3),
        fill=TIMBER,
    )
    # Hearth as a low floor-glow strip — not a centered "nose" blob.
    d.ellipse((X(0.435), Y(0.775), X(0.565), Y(0.828)), fill=HEARTH)
    d.ellipse((X(0.455), Y(0.798), X(0.545), Y(0.828)), fill=FLAME_Y)

    # Round beaver ear-bumps on the lintel. Ears only — no snout, teeth, or square head.
    if not simple:
        ear_w = max(1, wpx(0.010))
        for outer_e, inner_e in (
            ((0.432, 0.538, 0.478, 0.612), (0.440, 0.552, 0.470, 0.600)),
            ((0.522, 0.538, 0.568, 0.612), (0.530, 0.552, 0.560, 0.600)),
        ):
            d.ellipse(oval(outer_e), fill=LODGE)
            d.ellipse(oval(outer_e), outline=INK, width=ear_w)
            d.ellipse(oval(inner_e), fill=LODGE_WARM)

    # Snow drifted against the sill, tying hut to bank.
    drift = [
        (0.36, 0.85),
        (0.41, 0.80),
        (0.50, 0.82),
        (0.59, 0.80),
        (0.64, 0.85),
        (0.60, 0.90),
        (0.40, 0.90),
    ]
    d.polygon(poly(drift), fill=SNOW)

    return im


def render(size: int, *, pad: float = 0.0) -> Image.Image:
    """Paint at master resolution, then downsample for clean edges."""
    simple = size <= 24 and pad == 0.0
    master = paint_lodge(MASTER, pad=pad, simple=simple)
    if size == MASTER:
        return master
    return master.resize((size, size), Image.Resampling.LANCZOS)


def write_ico(path: Path, sizes: tuple[int, ...]) -> None:
    """Write a multi-size ICO with one PNG image per listed size."""
    blobs: list[bytes] = []
    for n in sizes:
        buf = BytesIO()
        render(n).save(buf, format="PNG")
        blobs.append(buf.getvalue())
    count = len(sizes)
    offset = 6 + 16 * count
    entries = bytearray()
    for n, data in zip(sizes, blobs):
        w = 0 if n >= 256 else n
        h = 0 if n >= 256 else n
        entries += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    header = struct.pack("<HHH", 0, 1, count)
    with path.open("wb") as fp:
        fp.write(header)
        fp.write(entries)
        for data in blobs:
            fp.write(data)


def main() -> None:
    ICON_DIR.mkdir(parents=True, exist_ok=True)

    render(192).save(ICON_DIR / "icon-192.png", format="PNG", optimize=True)
    render(512).save(ICON_DIR / "icon-512.png", format="PNG", optimize=True)
    render(512, pad=0.12).save(ICON_DIR / "icon-maskable-512.png", format="PNG", optimize=True)
    write_ico(ICON_DIR / "bober-frost.ico", ICO_SIZES)

    print(f"wrote {ICON_DIR / 'icon-192.png'}")
    print(f"wrote {ICON_DIR / 'icon-512.png'}")
    print(f"wrote {ICON_DIR / 'icon-maskable-512.png'}")
    print(f"wrote {ICON_DIR / 'bober-frost.ico'}")


if __name__ == "__main__":
    main()
