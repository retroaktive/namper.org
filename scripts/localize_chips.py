#!/usr/bin/env python3
"""Localize the exact-UI-label chips in the docs from the app's catalog.

The docs quote app labels inside <b class="ui">…</b>. Translators leave
those in English on purpose: the app itself ships fifteen locales, so the
right label for the German page is whatever Localizable.xcstrings says,
not a translator's guess. This pass swaps them in — and only when the
chip still holds the exact English source string, so it is idempotent.

    python3 scripts/localize_chips.py [--dry]
"""
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.expanduser("~/NAMper/ios/App/Localizable.xcstrings")

# docs directory -> catalog language
LOCALES = {
    "ru": "ru", "de": "de", "es": "es", "fr": "fr", "it": "it", "pt": "pt-BR",
    "tr": "tr", "id": "id", "vi": "vi", "th": "th", "ja": "ja", "ko": "ko",
    "zh": "zh-Hans", "zh-hant": "zh-Hant", "hi": "hi", "fil": "fil",
}

CHIP = re.compile(r'(<(b|span) class="ui[^"]*">)(.*?)(</\2>)', re.S)


def catalog():
    with open(CATALOG, encoding="utf-8") as f:
        d = json.load(f)
    out = {}
    for key, entry in d["strings"].items():
        loc = entry.get("localizations", {})
        vals = {}
        for lang, unit in loc.items():
            v = unit.get("stringUnit", {}).get("value")
            if v:
                vals[lang] = v
        out[norm(key)] = (key, vals)
    return out


def norm(s):
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def main(dry=False):
    cat = catalog()
    swapped = missed = 0
    misses = {}
    for d, lang in LOCALES.items():
        for path in glob.glob(os.path.join(ROOT, "docs", d, "*.html")):
            src = open(path, encoding="utf-8").read()

            def sub(m):
                nonlocal swapped, missed
                text = m.group(3)
                key = norm(text)
                hit = cat.get(key)
                if not hit:
                    missed += 1
                    misses[key] = misses.get(key, 0) + 1
                    return m.group(0)
                _, vals = hit
                v = vals.get(lang)
                if not v or v == vals.get("en", key):
                    return m.group(0)          # same in both languages
                swapped += 1
                return m.group(1) + html.escape(v, quote=False) + m.group(4)

            out = CHIP.sub(sub, src)
            if out != src and not dry:
                open(path, "w", encoding="utf-8").write(out)
    print("chips localized:", swapped, "| unmatched chip texts:", missed)
    top = sorted(misses.items(), key=lambda kv: -kv[1])[:15]
    for k, n in top:
        print("   no catalog entry (%dx): %s" % (n, k[:70]))


if __name__ == "__main__":
    main("--dry" in sys.argv)
