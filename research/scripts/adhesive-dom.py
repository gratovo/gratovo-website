"""Dump the rendered 'How it works' carousel of adhesivemedia.com after scrolling it into view.
Usage: python -I research/scripts/adhesive-dom.py <page-path> <tag>   -> research/adhesive-deep/dom-<tag>.*"""
import json, sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright
OUT = Path(__file__).resolve().parent.parent / "adhesive-deep"
path = sys.argv[1] if len(sys.argv) > 1 else ""
tag = sys.argv[2] if len(sys.argv) > 2 else (path or "home")
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    page = b.new_context(viewport={"width":1440,"height":900}).new_page()
    page.goto("https://www.adhesivemedia.com/" + path, wait_until="load", timeout=60000)
    page.wait_for_timeout(3000)
    top = page.evaluate("document.querySelector('section[class*=\"_section_79ol8\"]').getBoundingClientRect().top + scrollY")
    page.mouse.move(700, 450)
    y = 0
    while y < top - 50:
        y += 300
        page.mouse.wheel(0, 300); page.wait_for_timeout(150)
    page.wait_for_timeout(5000)
    page.screenshot(path=str(OUT / f"dom-{tag}-view.jpg"), type="jpeg", quality=75)
    info = page.evaluate("""() => {
      const s = document.querySelector('section[class*="_section_79ol8"]');
      const steps = [...s.querySelectorAll('[class*="_step_"]')];
      return {
        html: s.outerHTML,
        text: s.innerText,
        steps: steps.map(st => ({title: (st.querySelector('h3,h4,[class*=Title],[class*=title]')||{}).innerText, text: st.innerText.split(String.fromCharCode(10)).join(' | ').slice(0,300), w: Math.round(st.getBoundingClientRect().width)})),
        zig: (() => { const z = s.querySelector('[class*="_zigzag"]'); const cs = getComputedStyle(z); return {display: cs.display, overflow: cs.overflow, gap: cs.gap, scrollW: z.scrollWidth, clientW: z.clientWidth, parentOverflow: getComputedStyle(z.parentElement).overflow}; })()
      };
    }""")
    (OUT / f"dom-{tag}.html").write_text(info["html"], encoding="utf-8")
    (OUT / f"dom-{tag}.txt").write_text(info["text"], encoding="utf-8")
    print(json.dumps({k: v for k, v in info.items() if k not in ("html", "text")}, indent=1))
    print(info["text"])
    # CSS rules of the module + keyframes
    css = page.evaluate("""() => {
      const out = [];
      for (const ss of document.styleSheets) {
        let rules; try { rules = ss.cssRules; } catch (e) { continue; }
        for (const r of rules) {
          const t = r.cssText;
          if (/79ol8|adhesive-|keyframes/.test(t)) out.push(t);
        }
      }
      return out;
    }""")
    (OUT / f"dom-{tag}.css").write_text("\n".join(css), encoding="utf-8")
    print("css rules", len(css))
    b.close()
