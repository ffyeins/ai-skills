#!/usr/bin/env python3
"""Search and read the DevDocs references bundled with the doc-lookup skill.

  devdocs.py topics               list installed topics and their versions
  devdocs.py search TOPIC TERM    find entries whose name contains TERM
  devdocs.py show TOPIC PATH      print one entry as plain text

PATH comes from `search`, e.g. bourne-shell-builtins#index-getopts.
"""

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

DEVDOCS = Path(__file__).resolve().parent.parent / "devdocs"
SEARCH_LIMIT = 20  # enough to spot the right entry without flooding the context
MAX_LINES = 300  # one entry rarely needs more; --max-lines 0 prints everything
TINY_SECTION = 40  # characters; an anchor this short is only a marker


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def installed_topics():
    if not DEVDOCS.is_dir():
        return []
    return sorted(
        p.name
        for p in DEVDOCS.iterdir()
        if (p / "index.json").is_file() and (p / "db.json").is_file()
    )


def topic_dir(topic):
    path = DEVDOCS / topic
    if not ((path / "index.json").is_file() and (path / "db.json").is_file()):
        have = ", ".join(installed_topics()) or "none"
        fail(f"no DevDocs data for '{topic}'. Installed topics: {have}.")
    return path


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        fail(f"can't read {path} ({e}). The download may be incomplete.")


def label(topic):
    """Human-readable name and version of a topic, from meta.json if present."""
    try:
        meta = json.loads((DEVDOCS / topic / "meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return f"{topic} (version not recorded)"
    name = " ".join(str(v) for v in (meta.get("name"), meta.get("release")) if v)
    downloaded = meta.get("downloaded")
    return f"{name or topic}" + (f" (downloaded {downloaded})" if downloaded else "")


# --- HTML to text -----------------------------------------------------------

HEADINGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}
PARAGRAPH_TAGS = {
    "p", "pre", "div", "section", "article", "blockquote", "table", "dl", "ul",
    "ol", "figure", "header", "footer", "hr", *HEADINGS,
}
LINE_TAGS = {"li", "tr", "dt", "dd", "caption", "figcaption"}
SKIP_TAGS = {"script", "style"}


class TextExtractor(HTMLParser):
    """Turns a DevDocs HTML fragment into readable plain text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)  # decodes &lt; &amp; and friends
        self.chunks = []
        self.in_pre = 0
        self.skipping = 0
        self.cells = 0

    def _tail(self):
        return "".join(self.chunks[-3:])[-2:]

    def _break(self, blank_line):
        tail = self._tail()
        if not self.chunks:
            return
        if blank_line:
            self.chunks.append("\n\n" if not tail.endswith("\n") else ("\n" if tail != "\n\n" else ""))
        elif not tail.endswith("\n"):
            self.chunks.append("\n")

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skipping += 1
        elif tag == "br":
            self.chunks.append("\n")
        elif tag in PARAGRAPH_TAGS or tag in LINE_TAGS:
            self._break(tag in PARAGRAPH_TAGS)
            if tag in HEADINGS:
                self.chunks.append("#" * HEADINGS[tag] + " ")
            elif tag == "li":
                self.chunks.append("- ")
            elif tag == "pre":
                self.in_pre += 1
            elif tag == "tr":
                self.cells = 0
        elif tag in ("td", "th"):
            if self.cells:
                self.chunks.append(" | ")
            self.cells += 1

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self.skipping = max(0, self.skipping - 1)
        elif tag in PARAGRAPH_TAGS or tag in LINE_TAGS:
            if tag == "pre":
                self.in_pre = max(0, self.in_pre - 1)
            self._break(tag in PARAGRAPH_TAGS)

    def handle_data(self, data):
        if self.skipping:
            return
        if self.in_pre:
            self.chunks.append(data)
            return
        text = re.sub(r"\s+", " ", data)
        if not self.chunks or self._tail().endswith("\n") or self._tail().endswith("- "):
            text = text.lstrip()
        if text:
            self.chunks.append(text)

    def text(self):
        lines = [line.rstrip() for line in "".join(self.chunks).split("\n")]
        return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def to_text(html_fragment):
    parser = TextExtractor()
    parser.feed(html_fragment)
    parser.close()
    return parser.text()


# --- Finding one entry in a page --------------------------------------------

def matching_close(page, tag, start):
    """Index just past the tag that closes the element opened at `start`."""
    depth = 0
    pattern = re.compile(r"<(/?)%s\b[^>]*>" % re.escape(tag), re.I)
    for m in pattern.finditer(page, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return m.end()
    return len(page)


def heading_end(page, level, start):
    """Index of the next heading at `level` or above, after `start`."""
    for m in re.finditer(r"<h([1-6])\b", page[start + 1:], re.I):
        if int(m.group(1)) <= level:
            return start + 1 + m.start()
    return len(page)


def section_at(page, tag, start, tag_end):
    """The HTML of the entry whose anchor tag starts at `start`."""
    tag = tag.lower()
    if tag in HEADINGS:
        return page[start:heading_end(page, HEADINGS[tag], start)]
    if tag == "dt":
        # A term, any terms that share its definition, then the <dd> itself.
        end = matching_close(page, "dt", start)
        while True:
            nxt = re.match(r"\s*<(dt|dd)\b", page[end:], re.I)
            if not nxt:
                break
            end = matching_close(page, nxt.group(1), end + nxt.start(1) - 1)
            if nxt.group(1).lower() == "dd":
                break
        return page[start:end]
    section = page[start:matching_close(page, tag, start)]
    if len(to_text(section)) < TINY_SECTION:
        # An empty marker like <a name="x"></a>: read on to the next heading.
        return page[start:heading_end(page, 6, tag_end)]
    return section


def find_sections(page, fragment):
    """Return (sections, note) for `fragment`, falling back to heading names."""
    for candidate in dict.fromkeys((fragment, unquote(fragment))):
        anchor = re.search(
            r'<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*\s(?:id|name)="%s"[^>]*>' % re.escape(candidate),
            page,
        )
        if anchor:
            return [section_at(page, anchor.group(1), anchor.start(), anchor.end())], None

    # Some indexes (Java generics) use fragments that differ from the page's
    # anchors, e.g. #add-E- vs id="add-java.lang.Object-". Match the name instead.
    name = fragment.split("-")[0]
    sections = []
    if name:
        for m in re.finditer(r"<(h[1-6])\b[^>]*>(.*?)</\1>", page, re.I | re.S):
            if to_text(m.group(2)) == name:
                sections.append(section_at(page, m.group(1), m.start(), m.end()))
    if sections:
        return sections, f"no anchor #{fragment}; showing {len(sections)} section(s) titled '{name}'"
    return [page], f"no section #{fragment} on this page; showing the whole page"


# --- Commands -----------------------------------------------------------------

def cmd_topics(_args):
    topics = installed_topics()
    if not topics:
        print("No DevDocs topics are installed.")
    for topic in topics:
        print(f"{topic}\t{label(topic)}")


def cmd_search(args):
    entries = load_json(topic_dir(args.topic) / "index.json").get("entries", [])
    term = args.term.casefold()
    matches = []
    for entry in entries:
        name = entry.get("name", "")
        folded = name.casefold()
        if term in folded:
            rank = 0 if folded == term else 1 if folded.startswith(term) else 2
            matches.append((rank, len(name), name, entry))
    if not matches:
        print(f"No entries in {args.topic} contain '{args.term}'. Try a shorter or different term.")
        return
    matches.sort(key=lambda m: m[:3])
    shown = matches if args.limit == 0 else matches[:args.limit]
    for _, _, name, entry in shown:
        print(f"{name}\t{entry.get('path', '')}\t{entry.get('type', '')}")
    if len(shown) < len(matches):
        print(f"[{len(matches) - len(shown)} more; use a longer term, or --limit 0 for all]")


def cmd_show(args):
    db = load_json(topic_dir(args.topic) / "db.json")
    page_key, _, fragment = args.path.partition("#")
    page = db.get(page_key)
    if page is None:
        fail(f"no page '{page_key}' in {args.topic}. "
             f"Find entries with: devdocs.py search {args.topic} <term>")
    sections, note = find_sections(page, fragment) if fragment else ([page], None)
    text = "\n\n---\n\n".join(to_text(s) for s in sections)
    lines = text.split("\n")
    print(f"[{label(args.topic)}] {args.path}")
    if note:
        print(f"[{note}]")
    print()
    if args.max_lines and len(lines) > args.max_lines:
        print("\n".join(lines[:args.max_lines]))
        print(f"\n[{len(lines) - args.max_lines} more lines; add --max-lines 0 to see all]")
    else:
        print(text)


def main():
    parser = argparse.ArgumentParser(
        description="Search and read the DevDocs references bundled with doc-lookup."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("topics", help="list installed topics and their versions")

    search = sub.add_parser("search", help="find entries whose name contains TERM")
    search.add_argument("topic", help="topic folder, e.g. bash or openjdk-8")
    search.add_argument("term", help="case-insensitive part of the entry name")
    search.add_argument("--limit", type=int, default=SEARCH_LIMIT,
                        help=f"results to show (default {SEARCH_LIMIT}, 0 for all)")

    show = sub.add_parser("show", help="print one entry as plain text")
    show.add_argument("topic", help="topic folder, e.g. bash or openjdk-8")
    show.add_argument("path", help="entry path from search, e.g. page#section")
    show.add_argument("--max-lines", type=int, default=MAX_LINES,
                      help=f"stop after this many lines (default {MAX_LINES}, 0 for all)")

    args = parser.parse_args()
    {"topics": cmd_topics, "search": cmd_search, "show": cmd_show}[args.command](args)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # The reader stopped early (e.g. piped into head); that's not an error.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
