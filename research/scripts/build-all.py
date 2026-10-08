#!/usr/bin/env python3
"""Run the whole build in the right order: pages -> Tailwind CSS -> minified bundles -> SEO lint.

    python research/scripts/build-all.py

(Share images are separate because they need a browser: python research/scripts/build-og.py)
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for step in ("build-pages.py", "build-css.py", "build-assets.py", "seo-check.py"):
    print(f"\n== {step}")
    if subprocess.run([sys.executable, str(HERE / step)]).returncode:
        sys.exit(f"{step} failed")
