#!/usr/bin/env python3
"""Bober Willow Cut checks. Static rules, then a Chrome play of the first morning."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"
URL = HTML.as_uri()


def static_checks(text: str) -> list[str]:
    errors = []
    must = [
        "BOBER WILLOW CUT",
        "A farm simulator. Four seasons on the bank.",
        "Nightfall is still downriver.",
        "Fan game by a holder.",
        "SPRING · DAY 1",
        "Reedbean",
        "Pond beet",
        "Lanternpod",
        "reedswan",
        "plodder",
        "creek stones",
        "bober-willow-cut-v1",
        "No egg. The trough was empty.",
        "The mill made meal",
        "withered",
    ]
    banned = [
        "HOLD THE FIRE",
        "THAW HOLDS",
        "Hold the fire",
        "bober-frost-lodge-v1",
        "Heat ",
        "WHITEOUT",
        "Beacon",
    ]
    for needle in must:
        if needle not in text:
            errors.append("missing " + needle)
    for needle in banned:
        if needle in text:
            errors.append("still has " + needle)
    return errors


def play_checks() -> list[str]:
    from playwright.sync_api import sync_playwright

    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_context(viewport={"width": 390, "height": 844}).new_page()
        page.goto(URL, wait_until="domcontentloaded")
        page.evaluate("localStorage.removeItem('bober-willow-cut-v1')")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_selector("#btn-start")
        title = page.locator("h1").inner_text()
        if title != "BOBER WILLOW CUT":
            errors.append("splash title " + title)
        if page.locator("text=HOLD THE FIRE").count():
            errors.append("old splash button")
        page.locator("#btn-start").click()
        page.wait_for_timeout(400)
        when = page.locator("#when").inner_text()
        if when != "SPRING · DAY 1":
            errors.append("open when " + when)
        shot = ROOT / "scripts" / "_willow_day1.png"
        page.screenshot(path=str(shot))
        info = page.evaluate(
            """() => {
              const s = WC.state;
              const camX = s.player.x - 210;
              const camY = s.player.y - 240;
              const inside = (x, y) => x > camX + 4 && x < camX + 416 && y > camY + 4 && y < camY + 476;
              const lodgeBottom = 1184;
              return {
                beds: s.beds.slice(0, 4).map(b => b.state + ':' + (b.crop || '') + ':' + b.days),
                willow: s.willows[0].days,
                stones: s.stones,
                seeds: s.items.seedReed,
                meal: WC.price('meal'),
                grain: WC.price('reedbean'),
                shoots: inside(s.beds[0].x, s.beds[0].y) && inside(s.beds[1].x, s.beds[1].y),
                tilled: inside(s.beds[2].x, s.beds[2].y) && inside(s.beds[3].x, s.beds[3].y),
                swan: inside(1092, 1172),
                barnCut: 1368 < camX + 420 && 1528 > camX + 420,
                willowOff: s.willows[0].x < camX,
                crewOut: s.crew.every(c => c.y > lodgeBottom)
              };
            }"""
        )
        if info["beds"][0] != "growing:reedbean:1" or info["beds"][2] != "tilled::0":
            errors.append("beds " + str(info["beds"]))
        if info["willow"] != 0:
            errors.append("willow started ready")
        if not (info["meal"] > info["grain"]):
            errors.append("meal does not pay more")
        if not info["shoots"] or not info["tilled"]:
            errors.append("first screen beds off view " + str(info))
        if not info["swan"] or not info["barnCut"] or not info["willowOff"] or not info["crewOut"]:
            errors.append("first screen frame " + str(info))
        page.evaluate("WC.sleep()")
        page.wait_for_timeout(200)
        body = page.locator("#dawn-body").inner_text()
        title2 = page.locator("#dawn-title").inner_text()
        if "DAY 2" not in title2:
            errors.append("dawn title " + title2)
        if "No egg. The trough was empty." not in body:
            errors.append("unfed swan laid or copy changed: " + body)
        if "waited" not in body:
            errors.append("dry bed grew: " + body)
        fed = page.evaluate(
            """() => {
              WC.boot();
              WC.cutGrass(0);
              WC.water(0);
              WC.water(1);
              WC.sleep();
              const s = WC.state;
              return { egg: s.items.egg, fodder: s.fodder, d0: s.beds[0].days, d1: s.beds[1].days, body: document.getElementById('dawn-body').innerText };
            }"""
        )
        if fed["egg"] != 1 or fed["d0"] != 2:
            errors.append("fed morning " + str(fed))
        milled = page.evaluate(
            """() => {
              WC.boot();
              WC.state.items.reedbean = 1;
              const err = WC.loadMill();
              WC.state.mill.t = 72;
              WC.sleep();
              const s = WC.state;
              return { err: err, meal: s.items.meal, chaff: s.chaff, sack: s.mill.sack, grain: s.items.reedbean };
            }"""
        )
        if milled["meal"] != 1 or milled["chaff"] != 1 or milled["sack"] != 0:
            errors.append("mill " + str(milled))
        wither = page.evaluate(
            """() => {
              WC.boot();
              WC.setDay(7);
              WC.water(0);
              WC.sleep();
              const s = WC.state;
              return { season: s.season, day: s.day, bed: s.beds[0].state, crop: s.beds[0].crop };
            }"""
        )
        if wither["season"] != 1 or wither["bed"] != "stubble" or wither["crop"]:
            errors.append("wither " + str(wither))
        winter = page.evaluate(
            """() => {
              WC.boot();
              WC.state.season = 2;
              WC.setDay(7);
              const before = WC.state.willows[0].days;
              WC.sleep();
              return { season: WC.state.season, days: WC.state.willows[0].days, before: before };
            }"""
        )
        if winter["season"] != 3 or winter["days"] != 0:
            errors.append("willow grew in winter " + str(winter))

        def world_click(x, y):
            pt = page.evaluate(
                """([x, y]) => {
                  const c = WC.cam();
                  const el = document.getElementById('view').getBoundingClientRect();
                  return { x: el.left + c.ox + (x - c.x) * c.scale, y: el.top + c.oy + (y - c.y) * c.scale };
                }""",
                [x, y],
            )
            page.mouse.click(pt["x"], pt["y"])

        page.evaluate("WC.boot()")
        world_click(1280, 1450)
        try:
            page.wait_for_function("() => WC.state.player.y > 1380", timeout=8000)
        except Exception as exc:
            errors.append("walk failed " + repr(exc))
        page.evaluate("WC.boot()")
        world_click(1105, 1365)
        try:
            page.wait_for_function(
                "() => !document.getElementById('sheet').classList.contains('hidden')",
                timeout=8000,
            )
            page.locator("#sheet-body button", has_text="Plant Reedbean").click()
            planted = page.evaluate(
                "() => ({ st: WC.state.beds[2].state, crop: WC.state.beds[2].crop, seed: WC.state.items.seedReed })"
            )
            if planted["st"] != "seeded" or planted["crop"] != "reedbean" or planted["seed"] != 1:
                errors.append("plant " + str(planted))
        except Exception as exc:
            errors.append("plant click " + repr(exc))
        try:
            world_click(1105, 1275)
            page.wait_for_function("() => WC.state.beds[0].wet === true", timeout=8000)
        except Exception as exc:
            errors.append("water click " + repr(exc))

        page.evaluate("WC.boot()")
        page.locator("#btn-chores").click()
        page.locator("#sheet-body .row").first.locator("button", has_text="BARN").click()
        page.locator("#btn-sheet-close").click()
        try:
            page.wait_for_function("() => WC.state.fodder >= 1", timeout=10000)
        except Exception as exc:
            errors.append("barn chore " + repr(exc))

        page.evaluate(
            """() => {
              WC.boot();
              WC.state.items.reedbean = 1;
            }"""
        )
        page.locator("#btn-chores").click()
        page.locator("#sheet-body .row").first.locator("button", has_text="MILL").click()
        page.locator("#btn-sheet-close").click()
        try:
            page.wait_for_function("() => WC.state.mill.sack === 1", timeout=12000)
        except Exception as exc:
            errors.append("mill chore " + repr(exc))

        page.evaluate(
            """() => {
              WC.boot();
              WC.state.items.egg = 1;
              WC.state.player.x = 2260;
              WC.state.player.y = 1320;
              WC.state.player.tx = null;
            }"""
        )
        page.wait_for_function(
            "() => Math.abs(WC.cam().x - (WC.state.player.x - 210)) < 40",
            timeout=4000,
        )
        world_click(2280, 1288)
        try:
            page.wait_for_function(
                "() => document.getElementById('sheet-title').textContent.indexOf('Moss') >= 0",
                timeout=8000,
            )
            page.locator("#sheet-body .row", has_text="Egg").locator("button").click()
            sold = page.evaluate("() => ({ stones: WC.state.stones, egg: WC.state.items.egg })")
            if sold["stones"] != 11 or sold["egg"] != 0:
                errors.append("sell " + str(sold))
        except Exception as exc:
            errors.append("shop " + repr(exc))

        page.evaluate("localStorage.removeItem('bober-willow-cut-v1')")
        page.reload(wait_until="domcontentloaded")
        page.locator("#btn-notes").click()
        notes = page.evaluate(
            """() => ({
              mode: WC.mode(),
              splash: document.getElementById('splash').classList.contains('hidden'),
              clock: WC.state.clock
            })"""
        )
        if notes["mode"] != "sheet" or not notes["splash"] or notes["clock"] > 0.05:
            errors.append("notes opened the day " + str(notes))
        page.locator("#btn-sheet-close").click()
        back = page.evaluate(
            """() => ({
              mode: WC.mode(),
              splash: document.getElementById('splash').classList.contains('hidden')
            })"""
        )
        if back["mode"] != "splash" or back["splash"]:
            errors.append("notes did not return " + str(back))

        page.locator("#btn-start").click()
        page.wait_for_timeout(200)
        before = page.evaluate("() => ({ x: WC.state.player.x, y: WC.state.player.y, cam: WC.cam().x })")
        box = page.locator("#view").bounding_box()
        page.mouse.move(box["x"] + 30, box["y"] + box["height"] * 0.55)
        page.mouse.down()
        page.mouse.move(box["x"] + 90, box["y"] + box["height"] * 0.55, steps=8)
        page.mouse.up()
        dragged = page.evaluate("() => ({ x: WC.state.player.x, y: WC.state.player.y, cam: WC.cam().x })")
        if dragged["x"] != before["x"] or dragged["y"] != before["y"] or abs(dragged["cam"] - before["cam"]) < 5:
            errors.append("drag look " + str(before) + " -> " + str(dragged))

        page.locator("#btn-sleep").click()
        try:
            page.wait_for_function(
                "() => !document.getElementById('dawn').classList.contains('hidden')",
                timeout=3000,
            )
        except Exception as exc:
            errors.append("sleep button " + repr(exc))
        if "No egg. The trough was empty." not in page.locator("#dawn-body").inner_text():
            errors.append("sleep copy " + page.locator("#dawn-body").inner_text())
        page.locator("#btn-work").click()
        if page.evaluate("() => WC.mode()") != "play":
            errors.append("work did not resume")

        wide = browser.new_context(viewport={"width": 1280, "height": 800}).new_page()
        wide.goto(URL, wait_until="domcontentloaded")
        wide.evaluate("localStorage.removeItem('bober-willow-cut-v1')")
        wide.reload(wait_until="domcontentloaded")
        wide.locator("#btn-start").click()
        wide.wait_for_timeout(300)
        wide.screenshot(path=str(ROOT / "scripts" / "_willow_desktop.png"))
        col = wide.evaluate("() => document.getElementById('app').getBoundingClientRect().width")
        if col > 481:
            errors.append("desktop column " + str(col))
        wide.close()
        browser.close()
    return errors


def main() -> int:
    if not HTML.exists():
        print("FAIL missing index")
        return 1
    text = HTML.read_text(encoding="utf-8")
    errors = static_checks(text)
    try:
        errors.extend(play_checks())
    except Exception as exc:
        errors.append("play crashed " + repr(exc))
    if errors:
        print("FAIL")
        for err in errors:
            print(" -", err)
        return 1
    print("OK willow cut")
    return 0


if __name__ == "__main__":
    sys.exit(main())
