#!/usr/bin/env python3
"""Scroll through websites like a visitor and record screenshots plus animation signals.

For each URL it saves, into <outdir>/<site-name>/:
  step-00.jpg, step-01.jpg, ...  one screenshot per scroll stop (mouse-wheel, so smooth-scroll
                                 libraries and scroll-triggered effects behave as they do for a visitor)
  probe.json                     scripts loaded, JS globals found, live CSS animations, video/canvas counts

Usage:   python -I research/scripts/capture-site.py <outdir> <url> [<url> ...]
Needs:   pip install playwright, and Microsoft Edge installed (uses channel "msedge").
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

MAX_SHOTS = 10
SCROLL_STEP = 800
SETTLE_MS = 1600

# Substrings that identify animation / layout libraries in script URLs.
LIB_URL_HINTS = {
    "gsap": "GSAP", "scrolltrigger": "GSAP ScrollTrigger", "lenis": "Lenis smooth scroll",
    "locomotive": "Locomotive Scroll", "swiper": "Swiper", "slick": "Slick carousel",
    "splide": "Splide", "lottie": "Lottie", "three": "Three.js", "framer": "Framer",
    "aos": "AOS (animate on scroll)", "webflow": "Webflow", "rive": "Rive", "spline": "Spline",
    "embla": "Embla carousel", "particles": "particles", "anime": "anime.js", "barba": "Barba.js",
}

# JS globals that identify libraries once the page has loaded.
JS_PROBE = """() => {
  const g = {};
  const has = (k, v) => { try { if (v) g[k] = true; } catch (e) {} };
  has('gsap', window.gsap); has('ScrollTrigger', window.ScrollTrigger); has('Lenis', window.Lenis);
  has('LocomotiveScroll', window.LocomotiveScroll); has('Webflow', window.Webflow);
  has('AOS', window.AOS); has('Swiper', window.Swiper); has('lottie', window.lottie);
  has('THREE', window.THREE); has('jQuery', window.jQuery);
  has('slick', window.jQuery && window.jQuery.fn && window.jQuery.fn.slick);
  has('framer', document.querySelector('[data-framer-name],[data-framer-component-type]'));
  has('next', window.__NEXT_DATA__ || document.getElementById('__next'));
  has('react', document.querySelector('[data-reactroot]') || document.getElementById('root'));
  const anims = document.getAnimations ? document.getAnimations() : [];
  const names = {};
  anims.forEach(a => {
    const n = a.animationName || (a.transitionProperty ? 'transition:' + a.transitionProperty : 'js-animation');
    names[n] = (names[n] || 0) + 1;
  });
  const html = document.documentElement;
  return {
    globals: g,
    liveAnimations: names,
    videos: [...document.querySelectorAll('video')].map(v => ({autoplay: v.autoplay, loop: v.loop, muted: v.muted, src: (v.currentSrc || '').slice(0, 120)})),
    canvases: document.querySelectorAll('canvas').length,
    svgs: document.querySelectorAll('svg').length,
    htmlClass: html.className.slice(0, 200),
    customCursor: !!document.querySelector('[class*="cursor"]'),
    stickyElements: [...document.querySelectorAll('*')].filter(e => getComputedStyle(e).position === 'sticky').length,
    pageHeight: html.scrollHeight,
  };
}"""


def site_name(url):
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if not host:  # file:// URL: name it after the file
        return Path(parsed.path).stem
    return re.sub(r"^www\.", "", host).split(".")[0]


def capture(pw, url, outroot):
    name = site_name(url)
    out = Path(outroot) / name
    out.mkdir(parents=True, exist_ok=True)
    browser = pw.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    scripts = set()
    page.on("response", lambda r: scripts.add(r.url) if r.request.resource_type == "script" else None)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
    except Exception as e:  # keep going with whatever loaded
        print(f"{name}: goto warning: {e}")
    page.wait_for_timeout(9000)  # let preloaders and intro animations finish
    page.mouse.move(720, 450)

    last_y, shots = -1, 0
    for i in range(MAX_SHOTS):
        page.screenshot(path=str(out / f"step-{i:02d}.jpg"), type="jpeg", quality=62)
        shots += 1
        y = page.evaluate("window.scrollY")
        if y == last_y:
            break
        last_y = y
        page.mouse.wheel(0, SCROLL_STEP)
        page.wait_for_timeout(SETTLE_MS)

    probe = page.evaluate(JS_PROBE)
    probe["url"] = url
    probe["screenshots"] = shots
    hints = sorted({label for s in scripts for key, label in LIB_URL_HINTS.items() if key in s.lower()})
    probe["libraryHintsFromScriptUrls"] = hints
    probe["scriptHosts"] = sorted({urlparse(s).netloc for s in scripts})
    (out / "probe.json").write_text(json.dumps(probe, indent=2), encoding="utf-8")
    browser.close()
    print(f"{name}: {shots} shots, height {probe['pageHeight']}, libs {hints}, globals {list(probe['globals'])}")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    outroot, urls = sys.argv[1], sys.argv[2:]
    with sync_playwright() as pw:
        for url in urls:
            try:
                capture(pw, url, outroot)
            except Exception as e:
                print(f"{url}: FAILED {e}")


if __name__ == "__main__":
    main()
