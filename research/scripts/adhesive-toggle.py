"""Record frames of adhesivemedia.com's audience toggles: hero split buttons, How-We-Work tabs, FAQ tabs.
Usage: python -I research/scripts/adhesive-toggle.py"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
OUT = Path(__file__).resolve().parent.parent / "adhesive-deep" / "toggle"
OUT.mkdir(parents=True, exist_ok=True)
SEC = 'section[class*="_section_79ol8"]'

def wheel_to(page, y):
    page.mouse.move(700, 450)
    while abs(page.evaluate("scrollY") - y) > 300:
        d = 300 if page.evaluate("scrollY") < y else -300
        page.mouse.wheel(0, d); page.wait_for_timeout(110)
    page.evaluate(f"window.scrollTo(0,{y})"); page.wait_for_timeout(1500)

def frames(page, name, n, gap, **kw):
    for i in range(n):
        page.screenshot(path=str(OUT / f"{name}-{i:02d}.jpg"), type="jpeg", quality=68, **kw)
        page.wait_for_timeout(gap)

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    page = b.new_context(viewport={"width":1440,"height":900}).new_page()
    page.goto("https://www.adhesivemedia.com/", wait_until="load", timeout=60000)
    page.wait_for_timeout(4000)
    # 1) How We Work tabs
    top = page.evaluate(f"document.querySelector('{SEC}').getBoundingClientRect().top + scrollY")
    wheel_to(page, int(top) - 40)
    page.wait_for_timeout(4000)
    frames(page, "tabs-before", 1, 0)
    # indicator + card state before click
    st0 = page.evaluate(f"""() => {{ const s=document.querySelector('{SEC}'); const ind=s.querySelector('[class*=_tabIndicator]'); return {{ind: ind.getAttribute('style'), steps:[...s.querySelectorAll('[class*=_step_]')].map(x=>x.getAttribute('style'))}}; }}""")
    print("before", json.dumps(st0)[:600])
    page.click(f"{SEC} button:has-text('For Creators')")
    frames(page, "tabs-click", 14, 120)
    st1 = page.evaluate(f"""() => {{ const s=document.querySelector('{SEC}'); const ind=s.querySelector('[class*=_tabIndicator]'); return {{ind: ind.getAttribute('style'), titles:[...s.querySelectorAll('h3')].map(h=>h.innerText), steps:[...s.querySelectorAll('[class*=_step_]')].map(x=>x.getAttribute('style'))}}; }}""")
    print("after", json.dumps(st1)[:900])
    # switch back
    page.click(f"{SEC} button:has-text('For Brands')")
    frames(page, "tabs-back", 8, 120)
    # 2) hero split buttons: click I'm a Brand
    page.evaluate("window.scrollTo(0,0)"); page.wait_for_timeout(1200)
    url0 = page.url
    page.hover("a[class*=_button_1whxr]:has-text(\"I'm a Brand\")"); 
    frames(page, "hero-hover", 2, 200)
    page.click("a[class*=_button_1whxr]:has-text(\"I'm a Brand\")")
    frames(page, "hero-click", 12, 100)
    print("url", url0, "->", page.url)
    page.wait_for_timeout(2500)
    frames(page, "brand-page", 1, 0)
    page.go_back(); page.wait_for_timeout(1500)
    page.click("a[class*=_button_1whxr]:has-text(\"I'm a Creator\")")
    frames(page, "hero-click-creator", 8, 100)
    page.wait_for_timeout(2500)
    frames(page, "creator-page", 1, 0)
    # 3) FAQ tabs on home
    page.goto("https://www.adhesivemedia.com/", wait_until="load"); page.wait_for_timeout(3000)
    top = page.evaluate("document.querySelector('section[class*=\"_section_ie7br\"]').getBoundingClientRect().top + scrollY")
    wheel_to(page, int(top) - 40); page.wait_for_timeout(1500)
    frames(page, "faq-before", 1, 0)
    page.click("section[class*=\"_section_ie7br\"] button:has-text('For Creators')")
    frames(page, "faq-click", 8, 120)
    page.click("section[class*=\"_section_ie7br\"] button[class*=accordionTrigger] >> nth=0")
    frames(page, "faq-open", 6, 120)
    b.close()
