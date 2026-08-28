#!/usr/bin/env python3
"""Collect the publishable files into _site/ for a Cloudflare deploy.

GitHub Pages serves the repository root directly; Cloudflare uploads a
directory, so we copy just the parts that belong on the web and leave the
tooling (scripts/, .github/, .git/) behind.
"""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_site")
ITEMS = ["index.html", "privacy.html", "docs", "assets", "robots.txt",
         "sitemap.xml"]


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    for name in ITEMS:
        src = os.path.join(ROOT, name)
        dst = os.path.join(OUT, name)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        elif os.path.exists(src):
            shutil.copy2(src, dst)
    n = sum(len(f) for _, _, f in os.walk(OUT))
    size = sum(os.path.getsize(os.path.join(d, f))
               for d, _, fs in os.walk(OUT) for f in fs)
    print("_site: %d files, %.1f MB" % (n, size / 1e6))


if __name__ == "__main__":
    main()
