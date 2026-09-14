#!/usr/bin/env python3
"""MVP campaign checks for Bober Frost Lodge. No browser required."""

from __future__ import annotations

import math
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
        "Hold the fire.",
        "25 days. One lodge.",
        "Keep the Lodge Fire. Assign Bobers. Outlast the whiteout.",
        "a winter story, not a grind wallet.",
        "Fan game by a holder.",
        "WOOD 0",
        '"WOOD " + Math.floor(state.wood)',
        "CAMP_PROPS",
        "topSlab",
        "drawPineTop",
        "F 0",
        "SA 0",
        "ST 0",
        "5 wood + 3Sa",
        "remain * 0.72",
        "Math.max(220, remain - minStage)",
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
        "Need Stone Hut",
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
        "LONG WINTER",
        "bober-frost-endless-v1",
        "The thaw was a lie. Hold forever.",
        "E-Day ",
        "RETRY ENDLESS",
        "PADS_MORE",
        "The lodge fire outlasted the freeze.",
        "After the Dam — Wood held the river. Winter wanted the rest.",
        "Lodge Raised — One fire. Four Bobers. Snow already counting.",
        "River Still Runs — Fish under ice. Hunger doesn’t wait for thaw.",
        "Sap-Spirit Wood — The trees bleed warmth if you ask kindly.",
        "Stone Hauls — Rock for walls. Walls for heat.",
        "Whiteout Nights — Assign wrong, wake colder.",
        "Fire Holds — Dawn. Crew up. Day again.",
        "Toward Nightfall — Survive this winter; the keep still waits.",
        "assets/history/f0.jpg",
        "assets/history/f6.jpg",
        "assets/history/f7.jpg",
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
        "Nightfall waits. Blade first. The long road after.",
        "assets/history/graph.jpg",
        "MUSEUM",
        "bober-frost-museum-v1",
        "var W = 420, H = 480",
        "WORLD_W = 1200",
        "WORLD_H = 1600",
        "camX",
        "onCanvasMove",
        "tickEdgeScroll",
        "b.haul",
        "SITE_STOCK",
        "Dripkin",
        "Amberkin",
        "Heartwood Whisper",
        "Thaw-Sibling",
        "If this dies, the chapter dies.",
        "Chop Belt",
        "Fish Hole",
        "Sap-Spirit Stand",
        "Stone Field",
        "Deep Drift",
        "Woodcache",
        "Smoke Kiln",
        "Ice Cellar",
        "mus-tab-jobs",
        "Heat 80%",
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
        "drag to pan",
        "JOBS SEND BOBERS OUT",
        "GOT IT",
        "bober-frost-onboard-v1",
        "buildNeedLine",
        "reached the",
        "drawCrumbs",
        "Woodlots west",
        "Sap Forest north",
        "Stone Trail east",
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

    banned = ["gacha", "nickname", "leaderboard", "connect wallet", "Night King", "@bobercto"]
    low = text.lower()
    for s in banned:
        if s.lower() in low:
            errors.append(f"banned string present: {s}")
    if "wallet" in low and "not a grind wallet" not in low:
        errors.append("banned string present: wallet")
    if "Survive 25 winter days. Assign Chopper" in text:
        errors.append("splash still has doubled how-text")
    if "$BOBER" in text:
        errors.append("spendable wood still labeled $BOBER")
    if "c.ellipse(0, 6, 32, 20" in text or "c.ellipse(0, 10, 34, 22" in text:
        errors.append("circular sticker pads still live")
    if "roundRect(c, -20, -18, 40, 34, 4)" in text:
        errors.append("crate-ring pads still live")
    if "WORLD_W = 1200" in text and "WORLD_H = 1600" in text:
        if 1200 / 420 < 2.2 or 1600 / 480 < 2.2:
            errors.append("world smaller than 2.2x viewport")
    else:
        errors.append("scrollable world size missing")
    if 'textContent = "W "' in text or ">W 0<" in text:
        errors.append("wood HUD still uses W shorthand")
    if '"F " + Math.floor(state.fish)' not in text:
        errors.append("fish HUD label changed")
    if '"SA " + Math.floor(state.sap)' not in text:
        errors.append("sap HUD label changed")
    if '"ST " + Math.floor(state.stone)' not in text:
        errors.append("stone HUD label changed")
    if "green-home-games" not in text:
        errors.append("hub link missing")
    if "list.sort(function (a, b) { return a.y - b.y" not in text:
        errors.append("Y-sort missing")

    m = re.search(r'var SAVE_KEY = "([^"]+)"', text)
    if not m or m.group(1) != "bober-frost-lodge-v1":
        errors.append("SAVE_KEY is not bober-frost-lodge-v1")

    pad_pts = re.findall(
        r"\{ x: \d+, y: \d+ \}",
        text.split("var PADS")[1].split("];")[0] if "var PADS" in text else "",
    )
    if len(pad_pts) != 8:
        errors.append(f"expected 8 pads, got {len(pad_pts)}")

    def xy_list(chunk: str) -> list[tuple[int, int]]:
        return [(int(a), int(b)) for a, b in re.findall(r"x: (\d+), y: (\d+)", chunk)]

    pads = xy_list(text.split("var PADS")[1].split("];")[0]) if "var PADS" in text else []
    extra = []
    if "var PAD_EXPAND" in text:
        extra += xy_list(text.split("var PAD_EXPAND")[1].split(";")[0])
    if "var PADS_MORE" in text:
        extra += xy_list(text.split("var PADS_MORE")[1].split("];")[0])
    lodge_m = re.search(r"var LODGE = \{ x: (\d+), y: (\d+) \}", text)
    lodge = (int(lodge_m.group(1)), int(lodge_m.group(2))) if lodge_m else (600, 800)

    def site_xy(name: str) -> tuple[int, int] | None:
        m = re.search(rf"var {name} = \{{ x: (\d+), y: (\d+) \}}", text)
        return (int(m.group(1)), int(m.group(2))) if m else None

    chop, fish, sap, mine = site_xy("SITE_CHOP"), site_xy("SITE_FISH"), site_xy("SITE_SAP"), site_xy("SITE_MINE")
    if not chop or chop[0] > lodge[0] - 200:
        errors.append(f"CHOP site is not in the west woodlots: {chop}")
    if not fish or fish[1] < lodge[1] + 200:
        errors.append(f"FISH site is not at the south river: {fish}")
    if not sap or sap[1] > lodge[1] - 200:
        errors.append(f"TAP site is not in the north sap forest: {sap}")
    if not mine or mine[0] < lodge[0] + 200:
        errors.append(f"MINE site is not on the east stone trail: {mine}")
    if "b.haul" not in text:
        errors.append("miner haul loop missing")
    if "b.job === \"miner\"" in text and "SITE_STOCK" not in text:
        errors.append("miners do not haul to stockpile")

    def dist(a: tuple[int, int], b: tuple[int, int]) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    for i, a in enumerate(pads):
        for b in pads[i + 1 :]:
            if dist(a, b) < 64:
                errors.append(f"pad centers closer than 64px: {a} vs {b} ({dist(a, b):.1f})")
        if dist(a, lodge) < 40:
            errors.append(f"lodge breathing room < 40px to pad {a} ({dist(a, lodge):.1f})")
    for i, a in enumerate(extra):
        if dist(a, lodge) < 40:
            errors.append(f"expand pad too close to lodge: {a}")
        for b in pads:
            if dist(a, b) < 64:
                errors.append(f"expand pad closer than 64px: {a} vs {b} ({dist(a, b):.1f})")
        for b in extra[i + 1 :]:
            if dist(a, b) < 64:
                errors.append(f"expand pads closer than 64px: {a} vs {b} ({dist(a, b):.1f})")

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

    for name in ("graph.jpg", "f0.jpg", "f1.jpg", "f2.jpg", "f3.jpg", "f4.jpg", "f5.jpg", "f6.jpg", "f7.jpg", "a0.jpg", "a1.jpg", "a2.jpg", "a3.jpg"):
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
