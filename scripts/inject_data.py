#!/usr/bin/env python3
"""Inject Hammond data embed from Rfind_explorer_v1.html into index.html.

Extracts lines starting with `let RAW =`, `window.RFIND_VOCAB =`,
`window.RFIND_SIGS =`, `window.RFIND_ORTHO =` from the Explorer HTML, then
replaces the embed block in index.html (between RFIND_EMBED_BEGIN and END
markers).
"""
import re
import sys
from pathlib import Path

EXPLORER = Path(
    "/Users/tomoyukimurano/Miyakawa Lab Dropbox/Murano Tomoyuki/"
    "RFind-sc_260424/Rfind_explorer_v1.html"
)
INDEX = Path(__file__).resolve().parent.parent / "index.html"

PREFIXES = (
    "let RAW =",
    "window.RFIND_VOCAB =",
    "window.RFIND_SIGS ",   # note: has extra space before = in source
    "window.RFIND_ORTHO =",
)

BEGIN = "// === RFIND_EMBED_BEGIN ==="
END = "// === RFIND_EMBED_END ==="


def extract_lines():
    found = {}
    with EXPLORER.open("r", encoding="utf-8") as f:
        for line in f:
            for pre in PREFIXES:
                if line.startswith(pre) and pre not in found:
                    found[pre] = line.rstrip("\n")
    missing = [p for p in PREFIXES if p not in found]
    if missing:
        raise SystemExit(f"Missing in Explorer HTML: {missing}")
    return [found[p] for p in PREFIXES]


def main():
    print(f"Reading Explorer: {EXPLORER}")
    embed_lines = extract_lines()
    for ln in embed_lines:
        print(f"  extracted: {ln[:60]}...  ({len(ln):,} chars)")

    print(f"Reading index skeleton: {INDEX}")
    html = INDEX.read_text(encoding="utf-8")
    if BEGIN not in html or END not in html:
        raise SystemExit("Embed markers not found in index.html")

    new_block = (
        BEGIN + " (populated by inject_data.py from Rfind_explorer_v1.html)\n"
        + "\n".join(embed_lines)
        + "\n" + END
    )
    pattern = re.compile(
        re.escape(BEGIN) + r".*?" + re.escape(END),
        re.DOTALL,
    )
    new_html = pattern.sub(new_block, html, count=1)
    INDEX.write_text(new_html, encoding="utf-8")
    print(f"Wrote: {INDEX}  ({len(new_html):,} chars, "
          f"{len(new_html) / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
