#!/usr/bin/env python3
"""Render the social-share images (images/og/<slug>.png, 1200x630) and the app icons.

Run after build-pages.py (it writes research/.cache/og-pages.json):

    python research/scripts/build-pages.py
    python research/scripts/build-og.py

Uses the site's own theme.css and fonts, so cards follow the palette. Needs Playwright + Edge or Chromium
(pip install playwright). Output is committed because the live site serves these files directly.
"""
import json
import html
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
JOBS = json.loads((ROOT / "research" / ".cache" / "og-pages.json").read_text(encoding="utf-8"))
OUT = ROOT / "images" / "og"
OUT.mkdir(parents=True, exist_ok=True)
FILE = ROOT.as_uri()

CARD = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{f}/fonts/fonts.css"><link rel="stylesheet" href="{f}/css/theme.css">
<style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
body{{background:linear-gradient(135deg,var(--brand-deep),var(--brand));color:#fff;font-family:var(--font-display);position:relative}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(circle,rgba(255,255,255,.09) 1.5px,transparent 1.5px);background-size:44px 44px;
  -webkit-mask-image:radial-gradient(70% 80% at 80% 20%,#000 10%,transparent 75%)}}
.wrap{{position:absolute;inset:0;padding:64px 72px;display:flex;flex-direction:column;justify-content:space-between}}
.plate{{align-self:flex-start;background:#fff;border-radius:16px;padding:12px 22px;line-height:1}}
.kicker{{font-weight:700;font-size:22px;letter-spacing:.14em;text-transform:uppercase;color:var(--sky);margin-bottom:22px}}
h1{{margin:0;font-weight:800;letter-spacing:-.03em;line-height:1.06;max-width:1000px;font-size:{size}px}}
.url{{font-weight:700;font-size:26px;letter-spacing:.04em;color:rgba(255,255,255,.85)}}
</style></head><body><div class="dots"></div><div class="wrap">
<div class="plate"><span class="wordmark wordmark-caps wordmark-grad wordmark-color" style="--wm-size:44px"><img src="{f}/images/logo-mark.svg" alt=""><span class="wm-text">ratovo</span></span></div>
<div><div class="kicker">{kicker}</div><h1>{title}</h1></div>
<div class="url">gratovo.com</div></div></body></html>"""

ICON = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:{s}px;height:{s}px;background:#fff;display:flex;align-items:center;justify-content:center}}
img{{width:{w}px;height:auto}}</style></head><body><img src="{f}/images/logo-mark.svg" alt=""></body></html>"""


def size_for(title):
    n = len(title)
    return 78 if n <= 40 else 68 if n <= 62 else 58


def main():
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="msedge")
        except Exception:
            b = p.chromium.launch()
        tmp = ROOT / "research" / ".cache" / "_render.html"
        pg = b.new_page(viewport={"width": 1200, "height": 630})
        for j in JOBS:
            tmp.write_text(CARD.format(f=FILE, size=size_for(j["title"]), title=html.escape(j["title"]), kicker=html.escape(j["kicker"])), encoding="utf-8")
            pg.goto(tmp.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(250)
            pg.screenshot(path=str(OUT / f"{j['slug']}.png"))
        print("og images:", len(JOBS))
        for name, s in (("icon-192.png", 192), ("icon-512.png", 512), ("apple-touch-icon.png", 180)):
            ip = b.new_page(viewport={"width": s, "height": s})
            tmp.write_text(ICON.format(s=s, w=int(s * 0.7), f=FILE), encoding="utf-8")
            ip.goto(tmp.as_uri())
            ip.wait_for_timeout(200)
            ip.screenshot(path=str(ROOT / "images" / name))
            ip.close()
        print("icons written")
        b.close()


if __name__ == "__main__":
    main()
