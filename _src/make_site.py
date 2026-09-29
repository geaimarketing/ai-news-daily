#!/usr/bin/env python3
"""
Build the published GitHub Pages document from the daily brief fragment.

_src/brief.current.html holds only <title> + <style> + <div class="wrap"> —
the artifact host used to supply the outer shell. GitHub Pages needs the full
<!doctype html> document, so everything up to and including the LAST </style>
becomes <head> and the remainder becomes <body>.

Run from the repository root:  python3 _src/make_site.py
Exits non-zero if the self-check fails, so the caller must not commit.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_src", "brief.current.html")
OUT = os.path.join(ROOT, "index.html")

BASE_TITLE = "全球 AI 三大主題新聞日報"
DESCRIPTION = "每平日更新的全球 FinTech 與 AI 新聞彙整"


def fail(msg):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(1)


if not os.path.exists(SRC):
    fail("source not found: " + SRC)

with open(SRC, encoding="utf-8") as fh:
    html = fh.read()

idx = html.rfind("</style>")
if idx < 0:
    fail("no </style> found in source; unexpected format")

head = html[: idx + len("</style>")].strip()
body = html[idx + len("</style>") :].strip()

if '<div class="wrap">' not in body:
    fail("body has no .wrap container; unexpected format")

# Pull the report date out of the masthead so it can go in <title>.
m = re.search(r"<b>(20\d\d-\d\d-\d\d[^<]*)</b>", html)
date_label = m.group(1).strip() if m else ""
page_title = BASE_TITLE + " " + date_label if date_label else BASE_TITLE

head = re.sub(r"<title>.*?</title>", "<title>" + page_title + "</title>", head, flags=re.S)

doc = "\n".join(
    [
        "<!doctype html>",
        '<html lang="zh-Hant">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<meta name="description" content="' + DESCRIPTION + '">',
        '<meta property="og:title" content="' + page_title + '">',
        '<meta property="og:type" content="website">',
        head,
        "</head>",
        "<body>",
        body,
        "</body>",
        "</html>",
        "",
    ]
)

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(doc)

# Self-check: every story card must carry exactly one source link.
check = open(OUT, encoding="utf-8").read()
cards = len(re.findall(r'<article class="story', check))
links = len(re.findall(r'class="src" href=', check))
has_doctype = check.startswith("<!doctype html>")
has_body = "<body>" in check
has_style = "--stripe-3" in check

print("source  : " + SRC)
print("output  : " + OUT)
print("title   : " + page_title)
print(
    "doctype : %s   body: %s   css: %s"
    % (
        "OK" if has_doctype else "MISSING",
        "OK" if has_body else "MISSING",
        "OK" if has_style else "MISSING",
    )
)
print("cards   : %d    links: %d" % (cards, links))

if not cards or not links or cards != links or not (has_doctype and has_body and has_style):
    fail("self-check FAILED - do not commit")

print("self-check passed")
