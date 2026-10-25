#!/usr/bin/env python3
"""Check the static landing page. Standard library only.

Usage:
    python3 scripts/check_site.py site [--checklist <install-test-checklist.md>]

Exit code 0: all checks pass. Exit code 1: one line for each problem. Exit code 2: bad usage.

Checks:
- every local href, src and poster resolves to a file under the site folder;
  every #anchor resolves to an id on the target page;
- no script, stylesheet, image, video, audio, iframe or font URL from another host;
  an external <a href> goes to https://github.com/chartergroup/ only;
- no known tracker word in the HTML, CSS or JavaScript;
- every img has a non-empty alt; the page has lang, title, a meta description,
  one h1 and no skipped heading level;
- the six client names are on the page, each in a block with data-client
  and a status word (data-role="status");
- with --checklist: the status word of each client equals the table
  "Readiness at a glance" of the checklist.
"""

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

CLIENTS = ("Claude Code", "Claude Desktop", "Cursor", "Codex CLI", "VS Code", "Gemini CLI")
STATUS_WORDS = ("ready", "ready with gaps", "not ready")
TRACKER_WORDS = ("gtag", "analytics", "googletagmanager", "plausible", "matomo", "pixel")
ALLOWED_EXTERNAL_LINK = re.compile(r"^https://github\.com/chartergroup(?:[/?#]|$)")
# (attribute) that holds a URL, for every tag
URL_ATTRS = ("href", "src", "poster", "action", "srcset")
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
CSS_IMPORT = re.compile(r"@import\s+(?:url\(\s*)?(['\"])(.*?)\1", re.IGNORECASE)
TEXT_SUFFIXES = (".html", ".css", ".js")


class Page(HTMLParser):
    """Collect the facts of one HTML file."""

    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.refs = []  # (line, tag, attr, value)
        self.ids = set()
        self.imgs = []  # (line, alt or None)
        self.lang = None
        self.title = ""
        self.description = None
        self.headings = []  # (line, level)
        self.clients = []  # dicts: name, line, status
        self.text = []
        self.inline_css = []  # (line, text)
        self.inline_js = []
        self._in = []  # open tag names that we watch: title, style, script
        self._status_tag = None
        self._status_text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        line = self.getpos()[0]
        if tag == "html":
            self.lang = a.get("lang")
        if "id" in a and a["id"]:
            self.ids.add(a["id"])
        if tag == "meta" and (a.get("name") or "").lower() == "description":
            self.description = (a.get("content") or "").strip()
        if tag == "img":
            self.imgs.append((line, a.get("alt")))
        if len(tag) == 2 and tag[0] == "h" and tag[1] in "123456":
            self.headings.append((line, int(tag[1])))
        for attr in URL_ATTRS:
            if attr not in a:
                continue
            value = a[attr] if a[attr] is not None else ""
            if attr == "srcset":
                for part in value.split(","):
                    url = part.strip().split()[0] if part.strip() else ""
                    self.refs.append((line, tag, attr, url))
            else:
                self.refs.append((line, tag, attr, value))
        if "style" in a and a["style"]:
            self.inline_css.append((line, a["style"]))
        if "data-client" in a:
            self.clients.append({"name": a["data-client"], "line": line, "status": None})
        if a.get("data-role") == "status" and self.clients:
            self._status_tag = tag
            self._status_text = []
        if tag in ("title", "style", "script"):
            self._in.append((tag, line, []))

    def handle_endtag(self, tag):
        if self._status_tag == tag:
            self.clients[-1]["status"] = " ".join("".join(self._status_text).split())
            self._status_tag = None
        if self._in and self._in[-1][0] == tag:
            name, line, parts = self._in.pop()
            body = "".join(parts)
            if name == "title":
                self.title = body.strip()
            elif name == "style":
                self.inline_css.append((line, body))
            else:
                self.inline_js.append((line, body))

    def handle_data(self, data):
        if self._in:
            self._in[-1][2].append(data)
        else:
            self.text.append(data)
        if self._status_tag is not None:
            self._status_text.append(data)


def parse_page(path):
    page = Page(path)
    page.feed(path.read_text(encoding="utf-8"))
    page.close()
    return page


def classify(value):
    """Return 'empty', 'anchor', 'external', 'other-scheme' or 'local'."""
    value = value.strip()
    if not value:
        return "empty"
    if value.startswith("#"):
        return "anchor"
    if value.startswith("//"):
        return "external"
    scheme = urlsplit(value).scheme.lower()
    if scheme in ("http", "https"):
        return "external"
    if scheme:
        return "other-scheme"
    return "local"


def resolve_local(site, base_file, value):
    """Return (target path, fragment, error text)."""
    parts = urlsplit(value.strip())
    raw = unquote(parts.path)
    base = site if raw.startswith("/") else base_file.parent
    target = (base / raw.lstrip("/")).resolve() if raw else base_file.resolve()
    root = site.resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return None, parts.fragment, "points outside the site folder"
    if target.is_dir():
        target = target / "index.html"
    if not target.is_file():
        return None, parts.fragment, "file not found"
    return target, parts.fragment, None


def check_reference(site, base_file, line, tag, attr, value, pages, problems):
    where = "{}:{}".format(base_file.relative_to(site.parent), line)
    kind = classify(value)
    label = "<{} {}=\"{}\">".format(tag, attr, value)
    if kind == "empty":
        problems.append("{}: empty URL in {}".format(where, label))
    elif kind == "other-scheme":
        problems.append("{}: URL scheme is not allowed in {}".format(where, label))
    elif kind == "external":
        if tag == "a" and attr == "href":
            if not ALLOWED_EXTERNAL_LINK.match(value.strip()):
                problems.append("{}: external link is not to https://github.com/chartergroup/ in {}".format(where, label))
        else:
            problems.append("{}: resource from another host in {}".format(where, label))
    else:
        if kind == "anchor":
            target, fragment, error = base_file, value.strip()[1:], None
        else:
            target, fragment, error = resolve_local(site, base_file, value)
        if error:
            problems.append("{}: {} in {}".format(where, error, label))
        elif fragment:
            ids = ids_of(target, pages)
            if ids is not None and unquote(fragment) not in ids:
                problems.append("{}: no id \"{}\" on the page in {}".format(where, fragment, label))


def ids_of(target, pages):
    if target.suffix.lower() != ".html":
        return None
    if target not in pages:
        pages[target] = parse_page(target)
    return pages[target].ids


def check_css_text(site, css_file, line_offset, text, problems, label):
    refs = [m.group(2) for m in CSS_URL.finditer(text)] + [m.group(2) for m in CSS_IMPORT.finditer(text)]
    for value in refs:
        kind = classify(value)
        where = "{}:{}".format(label, line_offset)
        if kind == "external":
            problems.append("{}: resource from another host in CSS \"{}\"".format(where, value))
        elif kind == "other-scheme":
            if not value.strip().lower().startswith("data:"):
                problems.append("{}: URL scheme is not allowed in CSS \"{}\"".format(where, value))
        elif kind == "empty":
            problems.append("{}: empty URL in CSS".format(where))
        elif kind == "local":
            target, _, error = resolve_local(site, css_file, value)
            if error:
                problems.append("{}: {} in CSS \"{}\"".format(where, error, value))


def check_trackers(site, problems):
    for path in sorted(site.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            low = line.lower()
            for word in TRACKER_WORDS:
                if word in low:
                    problems.append("{}:{}: tracker word \"{}\"".format(path.relative_to(site.parent), number, word))


def read_checklist(path):
    """Return {client cell: status word} from the table 'Readiness at a glance'."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = None
    for number, line in enumerate(lines):
        if re.match(r"^##\s+Readiness at a glance\s*$", line):
            start = number
            break
    if start is None:
        raise ValueError("no section 'Readiness at a glance' in {}".format(path))
    rows = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        if line.lstrip().startswith("|"):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
        elif rows:
            break
    if len(rows) < 3:
        raise ValueError("no table in the section 'Readiness at a glance'")
    header = [cell.lower() for cell in rows[0]]
    if "client" not in header or "status" not in header:
        raise ValueError("the table has no columns Client and Status")
    c_col, s_col = header.index("client"), header.index("status")
    table = {}
    for row in rows[2:]:
        if len(row) > max(c_col, s_col):
            table[row[c_col]] = row[s_col].strip("` ").lower()
    return table


def check_page(site, index, pages, checklist, problems):
    page = pages[index]
    name = index.relative_to(site.parent)
    if not page.lang:
        problems.append("{}: the html element has no lang".format(name))
    if not page.title:
        problems.append("{}: no title".format(name))
    if not page.description:
        problems.append("{}: no meta description".format(name))
    h1 = [h for h in page.headings if h[1] == 1]
    if len(h1) != 1:
        problems.append("{}: expected one h1, found {}".format(name, len(h1)))
    previous = 0
    for line, level in page.headings:
        if level > previous + 1:
            problems.append("{}:{}: heading level jumps from {} to {}".format(name, line, previous, level))
        previous = level
    for line, alt in page.imgs:
        if alt is None or not alt.strip():
            problems.append("{}:{}: img has no alt text".format(name, line))
    text = " ".join(page.text)
    for client in CLIENTS:
        if client not in text:
            problems.append("{}: client name \"{}\" is not on the page".format(name, client))
    seen = {}
    for block in page.clients:
        seen[block["name"]] = block
        status = block["status"]
        if status is None:
            problems.append("{}:{}: client \"{}\" has no status (data-role=\"status\")".format(name, block["line"], block["name"]))
        elif status not in STATUS_WORDS:
            problems.append("{}:{}: client \"{}\" has an unknown status \"{}\"".format(name, block["line"], block["name"], status))
    for client in CLIENTS:
        if client not in seen:
            problems.append("{}: no block with data-client=\"{}\"".format(name, client))
    if checklist is not None:
        matched = set()
        for cell, word in checklist.items():
            owners = [n for n in seen if cell.lower().startswith(n.lower())]
            if not owners:
                problems.append("{}: the checklist client \"{}\" has no block on the page".format(name, cell))
                continue
            block = seen[owners[0]]
            matched.add(owners[0])
            if block["status"] is not None and block["status"] != word:
                problems.append("{}:{}: status of \"{}\" is \"{}\", the checklist says \"{}\"".format(
                    name, block["line"], owners[0], block["status"], word))
        for client in seen:
            if client not in matched:
                problems.append("{}: client \"{}\" is not in the checklist table".format(name, client))


def run(site, checklist_path):
    problems = []
    index = site / "index.html"
    if not index.is_file():
        return ["{}: the page is missing".format(index)]
    checklist = None
    if checklist_path is not None:
        try:
            checklist = read_checklist(checklist_path)
        except (OSError, ValueError) as error:
            problems.append("checklist: {}".format(error))
    site = site.resolve()
    index = index.resolve()
    pages = {}
    for path in sorted(site.rglob("*.html")):
        pages[path] = parse_page(path)
    for path, page in sorted(pages.items()):
        for line, tag, attr, value in page.refs:
            check_reference(site, path, line, tag, attr, value, pages, problems)
        label = str(path.relative_to(site.parent))
        for line, text in page.inline_css:
            check_css_text(site, path, line, text, problems, label)
    for css in sorted(site.rglob("*.css")):
        check_css_text(site, css, 1, css.read_text(encoding="utf-8"), problems, str(css.relative_to(site.parent)))
    check_trackers(site, problems)
    check_page(site, index, pages, checklist, problems)
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check the static landing page.")
    parser.add_argument("site", help="the site folder (it holds index.html)")
    parser.add_argument("--checklist", help="install-test-checklist.md of topopt-demo")
    args = parser.parse_args(argv)
    site = Path(args.site)
    if not site.is_dir():
        print("check_site: not a folder: {}".format(site), file=sys.stderr)
        return 2
    checklist = Path(args.checklist) if args.checklist else None
    if checklist is not None and not checklist.is_file():
        print("check_site: not a file: {}".format(checklist), file=sys.stderr)
        return 2
    problems = run(site, checklist)
    if problems:
        for line in problems:
            print(line, file=sys.stderr)
        print("check_site: {} problem(s)".format(len(problems)), file=sys.stderr)
        return 1
    print("check_site: all checks pass ({}, checklist: {})".format(site, "yes" if checklist else "no"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
