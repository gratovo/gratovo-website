#!/usr/bin/env python3
"""Deep interaction study of adhesivemedia.com (tabs, brand/creator pages, matching card, footer form).

Saves into research/adhesive-deep/. Usage:
  python -I research/scripts/adhesive-deep.py <step> [url-path]
  step = outline | frames <selector-text> | dom <css selector> | shot <path>
Most steps are driven by small functions below; edit STEP table at the bottom.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "adhesive-deep"
OUT.mkdir(exist_ok=True)
BASE = "https://www.adhesivemedia.com"


def open_page(p, path="/", w=1440, h=900):
    b = p.chromium.launch(channel="msedge", headless=True)
    ctx = b.new_context(viewport={"width": w, "height": h})
    page = ctx.new_page()
    page.goto(BASE + "/" + path.lstrip("/"), wait_until="load", timeout=60000)
    page.wait_for_timeout(5000)
    return b, page


def scroll_to(page, y):
    page.mouse.move(700, 450)
    cur = page.evaluate("scrollY")
    step = 400 if y > cur else -400
    while abs(page.evaluate("scrollY") - y) > 400:
        page.mouse.wheel(0, step)
        page.wait_for_timeout(120)
    page.evaluate(f"window.scrollTo(0,{y})")
    page.wait_for_timeout(600)


def frames(page, name, n=10, gap=350, clip=None):
    for i in range(n):
        page.screenshot(path=str(OUT / f"{name}-f{i:02d}.jpg"), type="jpeg", quality=70, clip=clip)
        page.wait_for_timeout(gap)


def section_top(page, head_text):
    return page.evaluate("""(t) => { const s=[...document.querySelectorAll('section')].find(x=>x.innerText.includes(t)); if(!s) return null; const r=s.getBoundingClientRect(); return {top:Math.round(r.top+scrollY),h:Math.round(r.height)}; }""", head_text)


def outline(page):
    return page.evaluate("""() => [...document.querySelectorAll('section, footer')].filter(s=>s.getBoundingClientRect().height>120).map(s=>{const r=s.getBoundingClientRect();const h=s.querySelector('h1,h2,h3');return {top:Math.round(r.top+scrollY),h:Math.round(r.height),cls:(s.className||'').toString().slice(0,40),head:h?h.innerText.slice(0,70):''}})""")


def run():
    step = sys.argv[1]
    path = sys.argv[2] if len(sys.argv) > 2 else ""
    with sync_playwright() as p:
        b, page = open_page(p, path)
        if step == "outline":
            for d in outline(page):
                print(d)
            print("height", page.evaluate("document.documentElement.scrollHeight"))
        elif step == "fullshots":
            # screenshot each section at its natural top, wait for reveal
            tag = path.strip("/") or "home"
            for i, d in enumerate(outline(page)):
                scroll_to(page, max(0, d["top"] - 40))
                page.wait_for_timeout(1200)
                page.screenshot(path=str(OUT / f"{tag}-sec{i:02d}.jpg"), type="jpeg", quality=72)
                print(i, d["head"][:50])
        b.close()


if __name__ == "__main__":
    run()
