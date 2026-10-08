#!/usr/bin/env python3
"""Compile Tailwind to css/tailwind.css so pages are styled on first paint (no CDN script, no flash).

The theme (colours, fonts, spacing) is still defined once, in research/pages/partials/tailwind-config.html;
this script reads it, so edit the partial, then run:

    python research/scripts/build-pages.py     (regenerate the pages)
    python research/scripts/build-css.py       (recompile css/tailwind.css from the pages + js)

Needs Node.js. On first run it installs tailwindcss 3.4.17 + the forms and container-queries plugins into
research/.tools/ (git-ignored). Same versions the CDN build used.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "research" / ".tools"
PARTIAL = ROOT / "research" / "pages" / "partials" / "tailwind-config.html"
OUT = ROOT / "css" / "tailwind.css"


def run(cmd, cwd):
    npm = shutil.which("npm") or "npm"
    r = subprocess.run([npm if c == "npm" else c for c in cmd], cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout + r.stderr)
    return r.stdout + r.stderr


def main():
    TOOLS.mkdir(parents=True, exist_ok=True)
    if not (TOOLS / "node_modules" / "tailwindcss").exists():
        (TOOLS / "package.json").write_text('{"name":"gratovo-tools","private":true}', encoding="utf-8")
        run(["npm", "install", "tailwindcss@3.4.17", "@tailwindcss/forms@0.5.10",
             "@tailwindcss/container-queries@0.1.1", "--no-audit", "--no-fund"], TOOLS)

    src = PARTIAL.read_text(encoding="utf-8")
    m = re.search(r"tailwind\.config\s*=\s*(\{.*\})\s*</script>", src, re.S)
    if not m:
        sys.exit("could not find tailwind.config in the partial")
    content = [str(ROOT / n).replace("\\", "/") for n in ("index.html", "brands.html", "creators.html")]
    content.append(str(ROOT / "js" / "*.js").replace("\\", "/"))
    cfg = (f"const base = {m.group(1)};\n"
           f"module.exports = Object.assign(base, {{ content: {content!r},\n"
           "  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/container-queries')] });\n")
    (TOOLS / "tailwind.config.js").write_text(cfg, encoding="utf-8")
    (TOOLS / "input.css").write_text("@tailwind base;\n@tailwind components;\n@tailwind utilities;\n", encoding="utf-8")

    OUT.parent.mkdir(exist_ok=True)
    cli = TOOLS / "node_modules" / "tailwindcss" / "lib" / "cli.js"
    out = run(["node", str(cli), "-c", "tailwind.config.js", "-i", "input.css", "-o", str(OUT), "--minify"], TOOLS)
    print(out.strip().splitlines()[-1] if out.strip() else "built")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
