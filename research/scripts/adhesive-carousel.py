"""Scroll adhesivemedia.com's 'How it works' carousel and record frames + card text.
Usage: python -I research/scripts/adhesive-carousel.py <page-path> <tag>"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
OUT = Path(__file__).resolve().parent.parent / "adhesive-deep"
path = sys.argv[1] if len(sys.argv) > 1 else ""
tag = sys.argv[2] if len(sys.argv) > 2 else (path or "home")
SEC = 'section[class*="_section_79ol8"]'
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    page = b.new_context(viewport={"width":1440,"height":900}).new_page()
    page.goto("https://www.adhesivemedia.com/" + path, wait_until="load", timeout=60000)
    page.wait_for_timeout(3000)
    top = page.evaluate(f"document.querySelector('{SEC}').getBoundingClientRect().top + scrollY")
    page.mouse.move(700, 450)
    y = 0
    while y < top - 50:
        y += 250; page.mouse.wheel(0, 250); page.wait_for_timeout(120)
    # frames while entering (reveal animation)
    for i in range(8):
        page.screenshot(path=str(OUT / f"car-{tag}-enter{i}.jpg"), type="jpeg", quality=70)
        page.wait_for_timeout(250)
    page.wait_for_timeout(3000)
    # find next arrow, click until end, screenshot each
    arrows = page.evaluate(f"""() => [...document.querySelector('{SEC}').querySelectorAll('button')].map(b => ({{label: b.getAttribute('aria-label'), cls: b.className.toString().slice(0,60), disabled: b.disabled}}))""")
    print("buttons", arrows)
    for k in range(4):
        page.evaluate(f"""() => {{ const z = document.querySelector('{SEC} [class*="_zigzag"]'); z.scrollBy({{left: 400, behavior: 'smooth'}}); }}""")
        page.wait_for_timeout(1500)
        for i in range(4):
            page.screenshot(path=str(OUT / f"car-{tag}-scroll{k}-{i}.jpg"), type="jpeg", quality=70)
            page.wait_for_timeout(500)
    info = page.evaluate(f"""() => {{ const s = document.querySelector('{SEC}'); return [...s.querySelectorAll('[class*="_step_"]')].map(st => st.innerText.split(String.fromCharCode(10)).filter(x=>x.trim()).join(' | ')); }}""")
    print(json.dumps(info, indent=1))
    html = page.evaluate(f"document.querySelector('{SEC}').outerHTML")
    (OUT / f"dom-{tag}-full.html").write_text(html, encoding="utf-8")
    b.close()
