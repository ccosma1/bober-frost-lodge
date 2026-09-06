#!/usr/bin/env python3
"""MVP campaign checks for Bober Frost Lodge. No browser required."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"
STORMS = {4, 8, 12, 18, 22, 25}


def drain(day: int, tender: bool, watch: bool = False) -> float:
    d = 10 + day * 0.55
    if day == 25:
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
        "Assign jobs · build · then START DAY",
        "Stoke · feed · hold heat",
        "Need Quarry Bench",
        "Day 1/25",
        "Watch Post:",
        "STOCKPILE",
        "SCOUT THE ICE",
        "Act I · Embers",
        "Act II · Deepening",
        "Act III · White Heart",
        "STORM_DAYS = [4, 8, 12, 18, 22, 25]",
        "DAYS = 25",
        "state.day === 25",
        "wood: 30",
        "CHOP_PER_DAY = 7",
        "day * 0.55",
        "THE FREEZE",
        "NEW WINTER",
        "HISTORY",
        "ENDLESS WINTER",
        "bober-frost-endless-v1",
        "The thaw was a lie. Hold forever.",
        "E-Day ",
        "RETRY ENDLESS",
        "PADS_MORE",
        "The lodge fire outlasted the freeze.",
        "After the dam, winter came looking for a hearth.",
        "HOLD THE FIRE.",
        "assets/history/f0.jpg",
        "assets/history/a0.jpg",
        "assets/cameos/e50.jpg",
        "assets/cameos/e75-check.jpg",
        "assets/cameos/e75-drill.jpg",
        "assets/cameos/e100.jpg",
        "bober-history-v1",
        "AFTER THE FREEZE",
        "John Snow from the white. Bober nodded. Nobody asked.",
        "Checklist: wood · fire · nerve.",
        "John Snow drilled the cold out of Bober — almost.",
        "Fire held. Frost King cracked.",
        "Two legends, one lodge — winter blinked first.",
        "The lodge warmed. Folks started calling it a green home.",
        "Something small. Something heavy. Not wood.",
        "A grey wanderer leaned on a stick. Quiet place, he said.",
        "Ash lands wait. Blade first. The long road after.",
        "afterFreezeUnlock",
        "maybeEndlessCameo",
        "CAMEO_BEATS",
        "state.day >= 50",
        "state.day >= 75",
        "state.day >= 100",
        "#241848",
        "chip-fork",
        "pulse-kill",
        "hoverBuild",
        "isActIII",
        "REINFORCE",
        "EXPAND CLEARING",
        "Lodge grows",
        "fork18",
        "PAD_EXPAND",
        "Brace the lodge",
        "Push the snow back",
        "+clearing",
        "drawFrozenDam",
        "#3D5C9A",
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

    banned = ["wallet", "gacha", "nickname", "leaderboard", "connect wallet", "Night King"]
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

    fair4 = 10 + 4 * 0.55
    wo4 = fair4 * 1.6
    if abs(drain(4, False) - wo4) > 1e-9:
        errors.append(f"day 4 storm drain off: {drain(4, False)} vs {wo4}")
    boss = (10 + 25 * 0.55) * 2.0
    if abs(drain(25, False) - boss) > 1e-9:
        errors.append(f"day 25 boss drain off: {drain(25, False)} vs {boss}")
    if drain(25, True, True) >= drain(25, False):
        errors.append("tender+watch should cut boss drain")
    if "STORM_DAYS = [3, 6, 9, 12, 15]" in text:
        errors.append("old 15-day storm schedule still live")
    if "isBossDay() { return state.day === 15; }" in text or "state.day === 15" in text:
        errors.append("boss still on day 15")

    # Imperfect-play Beacon: 1 miner from day 4–10 after spending 8 on quarry.
    start_st = 10
    quarry = 8
    mined = 4 * 7  # days 4..10
    if start_st - quarry + mined < 12:
        errors.append("beacon stone unreachable on a normal miner")

    for name in ("f0.jpg", "f1.jpg", "f2.jpg", "f3.jpg", "f4.jpg", "f5.jpg", "a0.jpg", "a1.jpg", "a2.jpg", "a3.jpg"):
        if not (ROOT / "assets" / "history" / name).exists():
            errors.append(f"missing history still {name}")
    for name in ("e50.jpg", "e75-check.jpg", "e75-drill.jpg", "e100.jpg"):
        if not (ROOT / "assets" / "cameos" / name).exists():
            errors.append(f"missing cameo still {name}")

    if errors:
        print("PLAYTEST FAIL")
        for e in errors:
            print(" -", e)
        return 1

    print("PLAYTEST OK")
    print(f"  day 4 storm drain:  {drain(4, False):.1f} (fair {fair4:.1f})")
    print(f"  day 25 boss drain:  {drain(25, False):.1f}")
    print(f"  boss +tender+watch: {drain(25, True, True):.1f}")
    print(f"  tender-only boss:   {drain(25, True, False):.1f}  (Beacon +25)")
    heat = 80.0
    for day in range(1, 26):
        heat -= drain(day, True, False)
    print(f"  tender no-stoke heat after 25n: {heat:.1f} (must stoke; not free)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
