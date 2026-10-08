#!/usr/bin/env python3
"""Rebuild images/logo-mark.svg and images/full-logo.png from images/logo.svg.

The full logo is the G mark from images/logo.svg followed by "ratovo" in
Plus Jakarta Sans (fonts/fonts.css), laid out with the same .wordmark CSS the
website uses, so the PNG always matches the site.

Usage:   python research/scripts/build-full-logo.py [--height 400] [--pad 0]
Needs:   Python 3, Pillow (pip install pillow), and Chrome, Edge or Chromium.
         Set BROWSER=/path/to/browser if it is not found automatically.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent.parent
LOGO_SVG = ROOT / "images" / "logo.svg"
MARK_SVG = ROOT / "images" / "logo-mark.svg"
FULL_PNG = ROOT / "images" / "full-logo.png"


def find_browser():
    candidates = [os.environ.get("BROWSER")]
    candidates += [shutil.which(n) for n in ("msedge", "chrome", "google-chrome", "chromium", "chromium-browser")]
    for base in filter(None, (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"), os.environ.get("LOCALAPPDATA"))):
        candidates += [
            Path(base) / "Microsoft/Edge/Application/msedge.exe",
            Path(base) / "Google/Chrome/Application/chrome.exe",
        ]
    candidates += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                   "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    for c in candidates:
        if c and Path(c).exists():
            return str(c)
    sys.exit("No Chrome/Edge/Chromium found. Set the BROWSER environment variable to its path.")


def render(browser, html_path, out_png, width, height, scale):
    """Screenshot an HTML file with a transparent background."""
    cmd = [browser, "--headless", "--disable-gpu", "--hide-scrollbars",
           f"--screenshot={out_png}", f"--window-size={width},{height}",
           f"--force-device-scale-factor={scale}", "--default-background-color=00000000",
           "--virtual-time-budget=10000", html_path.as_uri()]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not Path(out_png).exists():
        sys.exit("Browser did not produce a screenshot.")


def crop_viewbox(browser, tmp):
    """Write images/logo-mark.svg: logo.svg with its viewBox trimmed to the artwork."""
    svg = LOGO_SVG.read_text(encoding="utf8")
    m = re.search(r'viewBox="([\d.\-]+) ([\d.\-]+) ([\d.\-]+) ([\d.\-]+)"', svg)
    if not m:
        sys.exit("logo.svg needs a viewBox attribute.")
    vx, vy, vw, vh = map(float, m.groups())
    size = 1024
    html = tmp / "probe.html"
    html.write_text(f'<body style="margin:0"><img src="{LOGO_SVG.as_uri()}" width="{size}" height="{size}" style="display:block">', encoding="utf8")
    png = tmp / "probe.png"
    render(browser, html, png, size, size, 1)
    box = Image.open(png).convert("RGBA").getchannel("A").getbbox()
    if not box:
        sys.exit("logo.svg rendered empty.")
    # logo.svg is drawn into a square (preserveAspectRatio meet), so map pixels back to user units
    k = min(size / vw, size / vh)
    ox, oy = (size - vw * k) / 2, (size - vh * k) / 2
    x0, y0 = vx + (box[0] - ox) / k, vy + (box[1] - oy) / k
    x1, y1 = vx + (box[2] - ox) / k, vy + (box[3] - oy) / k
    w, h = x1 - x0, y1 - y0
    new_vb = f'viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}"'
    out = svg.replace(m.group(0), new_vb)
    out = re.sub(r'<svg([^>]*?) width="[^"]*" height="[^"]*"', rf'<svg\1 width="{w:.0f}" height="{h:.0f}"', out, count=1)
    MARK_SVG.write_text(out, encoding="utf8")
    print(f"logo-mark.svg  {new_vb}")


def build_png(browser, tmp, height, pad):
    css = (ROOT / "fonts" / "fonts.css").as_uri()
    # font-size so the full logo ends up about `height` px tall; trimmed afterwards
    fs = height / 1.0
    html = tmp / "wordmark.html"
    html.write_text(f'''<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="{css}">
<style>html,body{{margin:0;background:transparent}}body{{padding:{int(fs*0.5)}px}}
.wordmark{{font-size:{fs}px}}</style>
<span class="wordmark"><img src="{MARK_SVG.as_uri()}" alt="">ratovo</span>
<script>document.fonts.load("800 100px 'Plus Jakarta Sans'","ratovo");</script>''', encoding="utf8")
    png = tmp / "wordmark.png"
    render(browser, html, png, int(fs * 5), int(fs * 2.2), 1)
    im = Image.open(png).convert("RGBA")
    box = im.getchannel("A").getbbox()
    if not box:
        sys.exit("Wordmark rendered empty.")
    im = im.crop(box)
    if pad:
        canvas = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
        canvas.paste(im, (pad, pad))
        im = canvas
    im.save(FULL_PNG, optimize=True)
    print(f"full-logo.png  {im.width}x{im.height}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--height", type=int, default=300, help="approximate wordmark font size in px (default 300)")
    ap.add_argument("--pad", type=int, default=0, help="transparent padding around the logo in px (default 0)")
    a = ap.parse_args()
    browser = find_browser()
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        crop_viewbox(browser, tmp)
        build_png(browser, tmp, a.height, a.pad)


if __name__ == "__main__":
    main()
