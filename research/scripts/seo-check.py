#!/usr/bin/env python3
"""SEO lint for the generated site. Run after build-pages.py:  python research/scripts/seo-check.py

Checks every indexable page for: title and description length, exactly one H1, canonical on the apex domain,
Open Graph / Twitter tags and image files, JSON-LD that parses, images with alt text and dimensions,
internal links and #anchors that resolve, duplicate titles/descriptions, and sitemap coverage.
Exit code 1 if anything is wrong (warnings do not fail).
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = "https://gratovo.com"
LEGACY = {"index-b.html"}  # old experiment, kept out of the deploy


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.meta = {}
        self.links = []          # (rel, href)
        self.h1 = []
        self._h1 = False
        self.ld = []
        self._ld = False
        self.imgs = []
        self.hrefs = []
        self.ids = set()
        self.text = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            k = a.get("name") or a.get("property")
            if k:
                self.meta[k] = a.get("content", "")
        elif tag == "link":
            self.links.append((a.get("rel"), a.get("href")))
        elif tag == "h1":
            self._h1 = True
            self.h1.append("")
        elif tag == "script":
            if a.get("type") == "application/ld+json":
                self._ld = True
                self.ld.append("")
            else:
                self._skip += 1
        elif tag == "style":
            self._skip += 1
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self._h1 = False
        elif tag == "script":
            if self._ld:
                self._ld = False
            elif self._skip:
                self._skip -= 1
        elif tag == "style" and self._skip:
            self._skip -= 1

    def handle_data(self, d):
        if self.in_title:
            self.title += d
        if self._h1 and self.h1:
            self.h1[-1] += d
        if self._ld and self.ld:
            self.ld[-1] += d
        if not self._skip and not self._ld:
            self.text.append(d)


def main():
    errors, warns = [], []
    pages = {}
    for f in sorted(ROOT.glob("*.html")):
        if f.name in LEGACY:
            continue
        p = Page()
        p.feed(f.read_text(encoding="utf-8"))
        pages[f.name] = p

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    sm_urls = set(re.findall(r"<loc>([^<]+)</loc>", sitemap))
    titles, descs = {}, {}

    for name, p in pages.items():
        robots = p.meta.get("robots", "")
        indexable = "noindex" not in robots
        e = lambda m: errors.append(f"{name}: {m}")
        w = lambda m: warns.append(f"{name}: {m}")
        if indexable:
            t, d = p.title.strip(), p.meta.get("description", "")
            if not t: e("missing <title>")
            elif len(t) > 70: w(f"title is {len(t)} chars (aim for <= 65): {t}")
            elif len(t) < 25: w(f"title is short ({len(t)})")
            if not d: e("missing meta description")
            elif not 70 <= len(d) <= 165: w(f"description is {len(d)} chars (aim for 110-160)")
            titles.setdefault(t, []).append(name)
            descs.setdefault(d, []).append(name)
            canon = [h for r, h in p.links if r == "canonical"]
            expect = f"{SITE}/" if name == "index.html" else f"{SITE}/{name}"
            if canon != [expect]: e(f"canonical {canon} != {expect}")
            if expect not in sm_urls: e("not in sitemap.xml")
            for k in ("og:title", "og:description", "og:url", "og:image", "twitter:card", "twitter:image"):
                if not p.meta.get(k): e(f"missing {k}")
            if p.meta.get("og:url") != expect: e(f"og:url {p.meta.get('og:url')} != {expect}")
            og = p.meta.get("og:image", "").replace(SITE + "/", "")
            if og and not (ROOT / og).exists(): e(f"og image file missing: {og}")
            if "www.gratovo" in (ROOT / name).read_text(encoding="utf-8"): e("contains a www.gratovo.com URL")
            if not p.ld: e("no JSON-LD")
        elif name in sm_urls or f"{SITE}/{name}" in sm_urls:
            e("noindex page is listed in the sitemap")
        if len(p.h1) != 1: e(f"{len(p.h1)} <h1> elements (need exactly 1)")
        for i, raw in enumerate(p.ld):
            try:
                json.loads(raw)
            except Exception as ex:
                e(f"JSON-LD block {i} does not parse: {ex}")
        for im in p.imgs:
            if "alt" not in im: e(f"<img> without alt: {im.get('src')}")
            if not im.get("width") or not im.get("height"): w(f"<img> without width/height: {str(im.get('src'))[:60]}")
            src = im.get("src", "")
            if not src.startswith("http") and not src.startswith("data:") and not (ROOT / src).exists(): e(f"image file missing: {src}")
        for h in p.hrefs:
            if h.startswith(("http", "mailto:", "tel:", "javascript:")):
                if h.startswith("http://"): w(f"insecure link {h}")
                continue
            path, _, frag = h.partition("#")
            target = pages.get(path) if path else p
            if path and path not in pages and not (ROOT / path).exists(): e(f"broken link {h}")
            elif frag and target is not None and frag not in target.ids: e(f"anchor #{frag} not found in {path or name}")
        words = len(" ".join(p.text).split())
        if indexable and words < 250: w(f"thin page: {words} words")

    for k, v in titles.items():
        if len(v) > 1: errors.append(f"duplicate title in {v}")
    for k, v in descs.items():
        if len(v) > 1: errors.append(f"duplicate description in {v}")
    for u in sm_urls:
        n = "index.html" if u == f"{SITE}/" else u.replace(SITE + "/", "")
        if n not in pages: errors.append(f"sitemap URL has no file: {u}")

    robots_txt = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {SITE}/sitemap.xml" not in robots_txt: errors.append("robots.txt sitemap line missing or not on the apex domain")
    if "http://www.sitemaps.org/schemas/sitemap/0.9" not in sitemap: errors.append("sitemap.xml namespace is wrong")

    print(f"{len(pages)} pages checked, {sum(1 for p in pages.values() if 'noindex' not in p.meta.get('robots', ''))} indexable")
    for m in warns: print("  warn :", m)
    for m in errors: print("  ERROR:", m)
    print("OK" if not errors else f"{len(errors)} error(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
