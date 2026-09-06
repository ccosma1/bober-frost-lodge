#!/usr/bin/env python3
"""MVP campaign checks for Bober Frost Lodge. No browser required."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"
STORMS = {3, 6, 9, 12, 15}


def drain(day: int, tender: bool, watch: bool = False) -> float:
    d = 10 + day * 0.55
    if day == 15:
        d *= 2.0
    elif day in STORMS:
        d *= 1.6
    if tender:
        d *= 0.65
    if watch:
        d -= 2
    return max(4.0, d)


def main() -> int:
    errors: list[str] = []
    if not HTML.exists():
        print("FAIL: index.html missing")
        return 1
    text = HTML.read_text(encoding="utf-8")

    needed = [
        "BOBER FROST LODGE",
        "Fan game by a holder.",
        "HOLD THE FIRE",
        "bober-frost-lodge-v1",
        "THAW HOLDS",
        "Beacon Tower",
        "BOSS WHITEOUT — fire the Beacon or hold 40%",
        "Beacon ready",
        "Fire won’t last",
        "Heat after stoke",
        "PAD_R = 56",
        "Give every beaver a job.",
        "wood: 30",
        "CHOP_PER_DAY = 7",
        "day * 0.55",
        "THE FREEZE",
        "NEW WINTER",
        "HISTORY",
        "KEEP WARMING",
        "The lodge fire outlasted the freeze.",
        "After the dam, winter came looking for a hearth.",
        "HOLD THE FIRE.",
        "assets/history/f0.jpg",
        "bober-history-v1",
    ]
    for s in needed:
        if s not in text:
            errors.append(f"missing string: {s}")

    if "THAW HOLDS (slice)" in text:
        errors.append("win title still says slice")
    if "state.day * 0.8" in text:
        errors.append("old drain slope still live")
    if "d *= 2.2" in text:
        errors.append("old boss ×2.2 still live")
    if "d *= 1.75" in text:
        errors.append("old storm ×1.75 still live")
    if "d *= 0.6;" in text:
        errors.append("old tender ×0.6 still live")

    banned = ["wallet", "gacha", "nickname", "leaderboard", "connect wallet"]
    low = text.lower()
    for s in banned:
        if s.lower() in low:
            errors.append(f"banned string present: {s}")

    m = re.search(r'var SAVE_KEY = "([^"]+)"', text)
    if not m or m.group(1) != "bober-frost-lodge-v1":
        errors.append("SAVE_KEY is not bober-frost-lodge-v1")

    pad_pts = re.findall(
        r"\{ x: \d+, y: \d+ \}",
        text.split("var PADS")[1].split("];")[0] if "var PADS" in text else "",
    )
    if len(pad_pts) != 8:
        errors.append(f"expected 8 pads, got {len(pad_pts)}")

    fair3 = 10 + 3 * 0.55
    wo3 = fair3 * 1.6
    if abs(drain(3, False) - wo3) > 1e-9:
        errors.append(f"day 3 storm drain off: {drain(3, False)} vs {wo3}")
    boss = (10 + 15 * 0.55) * 2.0
    if abs(drain(15, False) - boss) > 1e-9:
        errors.append(f"day 15 boss drain off: {drain(15, False)} vs {boss}")
    if drain(15, True, True) >= drain(15, False):
        errors.append("tender+watch should cut boss drain")
    if boss > 40:
        errors.append(f"boss drain without tender too steep vs start 80: {boss}")

    # Imperfect-play Beacon: 1 miner from day 4–10 after spending 8 on quarry.
    start_st = 10
    quarry = 8
    mined = 4 * 7  # days 4..10
    if start_st - quarry + mined < 12:
        errors.append("beacon stone unreachable on a normal miner")

    for name in ("f0.jpg", "f1.jpg", "f2.jpg", "f3.jpg", "f4.jpg", "f5.jpg"):
        if not (ROOT / "assets" / "history" / name).exists():
            errors.append(f"missing history still {name}")

    if errors:
        print("PLAYTEST FAIL")
        for e in errors:
            print(" -", e)
        return 1

    print("PLAYTEST OK")
    print(f"  day 3 storm drain:  {drain(3, False):.1f} (fair {fair3:.1f})")
    print(f"  day 15 boss drain:  {drain(15, False):.1f}")
    print(f"  boss +tender+watch: {drain(15, True, True):.1f}")
    print(f"  tender-only boss:   {drain(15, True, False):.1f}  (Beacon +25 covers)")
    heat = 80.0
    for day in range(1, 16):
        heat -= drain(day, True, False)
    print(f"  tender no-stoke heat after 15n: {heat:.1f} (must stoke; not free)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
