#!/usr/bin/env python3
"""Bundle and minify the site's CSS and JS (the last step of the build, after build-pages.py and build-css.py).

  css/site.min.css  <- fonts/fonts.css + css/tailwind.css + css/theme.css + css/hero.css + css/process-cards.css
  js/site.min.js    <- js/audience-tabs.js + js/process-cards.js + js/site-header.js + js/hero-spotlight.js   (home, brands, creators)
  js/lite.min.js    <- js/audience-tabs.js + js/site-header.js   (all other pages)

One stylesheet and one deferred script mean two requests instead of ten. The stylesheet is then inlined into every page (GitHub Pages only
caches for 10 minutes, so a separate file saves almost nothing, while inlining removes a whole network round trip before the first paint).
Pages without a hero or a "How it works" section (articles, landing pages, guides, 404) get a lighter copy without the two embedded mask images.
The source files stay the place to edit; the pages only link the two bundles. Uses esbuild (installed into research/.tools/ on first run).
Run everything in the right order with:  python research/scripts/build-all.py
"""
import gzip
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "research" / ".tools"
CSS = ["fonts/fonts.css", "css/tailwind.css", "css/theme.css", "css/hero.css", "css/process-cards.css"]
JS = ["js/audience-tabs.js", "js/process-cards.js", "js/site-header.js", "js/hero-spotlight.js"]       # home, brands, creators
JS_LITE = ["js/audience-tabs.js", "js/site-header.js"]                                                   # every other page (no hero, no "How it works")


def esbuild():
    exe = TOOLS / "node_modules" / ".bin" / ("esbuild.cmd" if sys.platform == "win32" else "esbuild")
    if not exe.exists():
        TOOLS.mkdir(parents=True, exist_ok=True)
        if not (TOOLS / "package.json").exists():
            (TOOLS / "package.json").write_text('{"name":"gratovo-tools","private":true}', encoding="utf-8")
        subprocess.run(["npm", "install", "esbuild", "--no-audit", "--no-fund"], cwd=TOOLS, check=True, shell=(sys.platform == "win32"))
    return str(exe)


def run(exe, src, out, loader):
    subprocess.run([exe, str(src), "--minify", f"--loader:.tmp={loader}", f"--outfile={out}", "--log-level=warning", "--legal-comments=none"],
                   check=True, shell=(sys.platform == "win32"))


LINK = '<link rel="stylesheet" href="css/site.min.css">'
LEGACY = {"index-b.html"}
CORE = {"index.html", "brands.html", "creators.html"}      # the pages with the hero and the "How it works" section (they use the masks)
MASKS = re.compile(r':root\{--wm-mask:\s*url\([^)]*\);--cubes-mask:\s*url\([^)]*\)\}')


def inline_css():
    full = (ROOT / "css" / "site.min.css").read_text(encoding="utf-8")
    full = full.replace("url(../", "url(")                  # the css/ folder is gone once the CSS lives in the page
    full = full.replace('url("../', 'url("')
    lite = MASKS.sub("", full)
    if lite == full:
        sys.exit("could not find the embedded mask block in the minified CSS")
    done = 0
    for f in sorted(ROOT.glob("*.html")):
        if f.name in LEGACY:
            continue
        html = f.read_text(encoding="utf-8")
        if LINK not in html:
            continue
        css = full if f.name in CORE else lite
        f.write_text(html.replace(LINK, "<style>" + css + "</style>"), encoding="utf-8")
        done += 1
    print(f"inlined the stylesheet into {done} pages")


def main():
    exe = esbuild()
    tmp = ROOT / "research" / ".cache"
    tmp.mkdir(exist_ok=True)

    parts = []
    for f in CSS:
        text = (ROOT / f).read_text(encoding="utf-8")
        if f == "fonts/fonts.css":                                     # the bundle lives in css/, the fonts one level up
            text = re.sub(r"url\((?!['\"]?(?:data:|https?:|\.\./|/))(['\"]?)([^)'\"]+)\1\)", r"url(../fonts/\2)", text)
        parts.append(text)
    (tmp / "bundle.tmp").write_text("\n".join(parts), encoding="utf-8")
    run(exe, tmp / "bundle.tmp", ROOT / "css" / "site.min.css", "css")

    for files, out in ((JS, "site.min.js"), (JS_LITE, "lite.min.js")):
        text = ";\n".join((ROOT / f).read_text(encoding="utf-8") for f in files) + ";\n"
        (tmp / "bundle-js.tmp").write_text(text, encoding="utf-8")
        run(exe, tmp / "bundle-js.tmp", ROOT / "js" / out, "js")

    inline_css()
    for f in ("css/site.min.css", "js/site.min.js", "js/lite.min.js"):
        b = (ROOT / f).read_bytes()
        print(f"wrote {f}: {len(b):,} bytes ({len(gzip.compress(b, 9)):,} gzipped)")
    (tmp / "bundle.tmp").unlink(missing_ok=True)
    (tmp / "bundle-js.tmp").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
