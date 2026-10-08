#!/usr/bin/env python3
"""Tell IndexNow-enabled search engines (Bing, Yandex, Naver, Seznam; not Google) about new or changed pages.

One-time:  python research/scripts/indexnow.py --init     creates <key>.txt in the site root. Commit and deploy it.
After every deploy that changed pages:
           python research/scripts/indexnow.py --submit   sends every URL in sitemap.xml to api.indexnow.org

Nothing is sent unless you pass --submit. The key file is public by design (it only proves you own the site).
"""
import json
import re
import secrets
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOST = "gratovo.com"
KEYFILE = ROOT / "research" / ".cache" / "indexnow-key.txt"


def key():
    if not KEYFILE.exists():
        sys.exit("No key yet. Run with --init first.")
    return KEYFILE.read_text(encoding="utf-8").strip()


def init():
    KEYFILE.parent.mkdir(parents=True, exist_ok=True)
    k = KEYFILE.read_text(encoding="utf-8").strip() if KEYFILE.exists() else secrets.token_hex(16)
    KEYFILE.write_text(k, encoding="utf-8")
    (ROOT / f"{k}.txt").write_text(k, encoding="utf-8")
    print(f"wrote {k}.txt in the site root. Commit and deploy it, then run --submit.")


def submit():
    k = key()
    urls = re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    body = json.dumps({"host": HOST, "key": k, "keyLocation": f"https://{HOST}/{k}.txt", "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow response:", r.status, "for", len(urls), "URLs")


if __name__ == "__main__":
    if "--init" in sys.argv:
        init()
    elif "--submit" in sys.argv:
        submit()
    else:
        print(__doc__)
