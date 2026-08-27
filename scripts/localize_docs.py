#!/usr/bin/env python3
"""Docs localization plumbing.

    python3 scripts/localize_docs.py skeleton   # copy EN -> docs/<lang>/, fix links
    python3 scripts/localize_docs.py alternates # rewrite hreflang blocks everywhere
    python3 scripts/localize_docs.py check      # compare tag skeletons against EN

The English pages under docs/ are the source of truth for structure: a
localized page is the same markup with the prose swapped, so `check`
diffing the tag sequence catches a translator that dropped a table row.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

# code -> (directory, html lang attribute)
LOCALES = [
    ("en", "",        "en"),
    ("ru", "ru",      "ru"),
    ("de", "de",      "de"),
    ("es", "es",      "es"),
    ("fr", "fr",      "fr"),
    ("it", "it",      "it"),
    ("pt", "pt",      "pt-BR"),
    ("tr", "tr",      "tr"),
    ("id", "id",      "id"),
    ("vi", "vi",      "vi"),
    ("th", "th",      "th"),
    ("ja", "ja",      "ja"),
    ("ko", "ko",      "ko"),
    ("zh", "zh",      "zh-Hans"),
    ("zh-hant", "zh-hant", "zh-Hant"),
]

PAGES = ["index.html", "setup.html", "rig.html", "plugins.html", "looper.html",
         "sampler.html", "perform.html", "control.html", "settings.html"]


def page_path(d, page):
    return os.path.join(DOCS, d, page) if d else os.path.join(DOCS, page)


def alternates(page):
    """The <link rel=alternate> block for one page, all locales."""
    out = []
    for code, d, lang in LOCALES:
        url = "https://namper.org/docs/" + (d + "/" if d else "")
        url += "" if page == "index.html" else page
        out.append('<link rel="alternate" hreflang="%s" href="%s">' % (lang, url))
    out.append('<link rel="alternate" hreflang="x-default" href="https://namper.org/docs/'
               + ("" if page == "index.html" else page) + '">')
    return "\n".join(out)


def retarget(html, d, lang, page):
    """Point a copied English page at its own locale directory."""
    # page links: /docs/foo.html -> /docs/<d>/foo.html ; /docs/ -> /docs/<d>/
    def fix(m):
        tail = m.group(1)
        if tail.startswith("assets/"):
            return m.group(0)
        return 'href="/docs/%s%s"' % (d + "/" if d else "", tail)
    html = re.sub(r'href="/docs/([^"]*)"', fix, html)
    html = re.sub(r'<html lang="[^"]*"', '<html lang="%s"' % lang, html, count=1)
    url = "https://namper.org/docs/" + (d + "/" if d else "")
    url += "" if page == "index.html" else page
    html = re.sub(r'(<meta property="og:url" content=")[^"]*(">)',
                  lambda m: m.group(1) + url + m.group(2), html)
    html = re.sub(r'(?:<link rel="alternate"[^>]*>\n?)+', alternates(page) + "\n", html,
                  count=1)
    return html


def cmd_skeleton():
    made = 0
    for code, d, lang in LOCALES:
        if not d or code == "ru":
            continue                        # en is the source, ru is written
        os.makedirs(os.path.join(DOCS, d), exist_ok=True)
        for page in PAGES:
            dst = page_path(d, page)
            if os.path.exists(dst):
                continue
            html = open(page_path("", page), encoding="utf-8").read()
            open(dst, "w", encoding="utf-8").write(retarget(html, d, lang, page))
            made += 1
    print("skeleton pages written:", made)


def cmd_alternates():
    n = 0
    for code, d, lang in LOCALES:
        for page in PAGES:
            p = page_path(d, page)
            if not os.path.exists(p):
                continue
            s = open(p, encoding="utf-8").read()
            new = re.sub(r'(?:<link rel="alternate"[^>]*>\n?)+', alternates(page) + "\n",
                         s, count=1)
            if new != s:
                open(p, "w", encoding="utf-8").write(new)
                n += 1
    print("alternate blocks refreshed:", n)


TAG = re.compile(r"<(/?)([a-zA-Z0-9]+)")


def skeleton_of(html):
    body = html.split("<body", 1)[-1]
    return [m.group(1) + m.group(2).lower() for m in TAG.finditer(body)]


def cmd_check():
    bad = 0
    for code, d, lang in LOCALES:
        if not d:
            continue
        for page in PAGES:
            p = page_path(d, page)
            if not os.path.exists(p):
                print("MISSING", p[len(ROOT) + 1:])
                bad += 1
                continue
            a = skeleton_of(open(page_path("", page), encoding="utf-8").read())
            b = skeleton_of(open(p, encoding="utf-8").read())
            if a != b:
                i = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
                print("STRUCTURE %s/%s: %d vs %d tags, first diff at %d (%s vs %s)"
                      % (d, page, len(a), len(b), i,
                         a[i] if i < len(a) else "-", b[i] if i < len(b) else "-"))
                bad += 1
    print("pages with problems:", bad)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    {"skeleton": cmd_skeleton, "alternates": cmd_alternates, "check": cmd_check}[cmd]()
