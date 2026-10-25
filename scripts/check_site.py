#!/usr/bin/env python3
"""Check the static landing site: the gallery and every variant. Standard library only.

Usage:
    python3 scripts/check_site.py site

The site folder holds the gallery (index.html) and one folder for each variant
(v1/, v2/, ... each with an index.html). The check finds the variants by their
folder name, so a new variant needs no change here.

Exit code 0: all checks pass. Exit code 1: one line for each problem. Exit code 2: bad usage.

Checks:
- every local href, src, poster and CSS url() resolves to a file under the site folder;
  every #anchor resolves to an id on the target page;
- no script, stylesheet, image, video, audio, iframe, font or other resource from another host
  (also not in a CSS url(), an @import or an @font-face source);
  an external <a href> goes to https://github.com/chartergroup/ only;
- no known tracker word in the HTML, CSS or JavaScript;
- every img has a non-empty alt; each page has lang, title, a meta description, one h1
  and no skipped heading level;
- every variant page has the six client names;
- every variant page has no meta word (private, not tested, status, preview, ...) in its visible text,
  title, meta description, alt text, aria-label or title attribute (text inside code and pre is not checked);
- the gallery (the root page with class "gallery" on its body) links to every variant folder; after the launch
  the root page is the chosen variant: it has no class "gallery", and then it gets the variant checks instead;
- every font folder with .woff2 files has a licence file (OFL*, LICENSE*).
"""

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

CLIENTS = ("Claude Code", "Claude Desktop", "Cursor", "Codex CLI", "VS Code", "Gemini CLI")
# A word that is a note about the page, not content. Matched case-insensitive, at the start of a word.
META_WORDS = (
    "private", "not tested", "untested", "not checked", "not verified", "status", "ready with gaps",
    "not ready", "research preview", "preview", "beta", "for now", "coming soon", "draft", "todo",
    "lorem", "placeholder",
)
TRACKER_WORDS = (
    "gtag", "analytics", "googletagmanager", "plausible", "matomo", "pixel",
    "doubleclick", "hotjar", "mixpanel", "fbq(",
)
VARIANT_DIR = re.compile(r"^v\d+$")
ALLOWED_EXTERNAL_LINK = re.compile(r"^https://github\.com/chartergroup(?:[/?#]|$)")
# the attributes that hold a URL, for every tag
URL_ATTRS = ("href", "src", "poster", "action", "srcset", "data")
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
CSS_IMPORT = re.compile(r"@import\s+(?:url\(\s*)?(['\"])(.*?)\1", re.IGNORECASE)
SCRIPT_URL = re.compile(r"(?:https?:)?//[A-Za-z0-9.-]+\.[A-Za-z]{2,}", re.IGNORECASE)
TEXT_SUFFIXES = (".html", ".css", ".js")
META_RE = re.compile(
    "|".join(r"(?<![A-Za-z0-9])" + r"\s+".join(re.escape(w) for w in word.split()) for word in META_WORDS),
    re.IGNORECASE,
)


class Page(HTMLParser):
    """Collect the facts of one HTML file."""

    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.refs = []  # (line, tag, attr, value)
        self.ids = set()
        self.imgs = []  # (line, alt or None)
        self.lang = None
        self.body_classes = ()
        self.title = ""
        self.description = None
        self.headings = []  # (line, level)
        self.text = []  # visible text, all of it: (line, text)
        self.prose = []  # visible text outside code and pre, and the text attributes: (line, kind, text)
        self.inline_css = []  # (line, text)
        self.inline_js = []  # (line, text)
        self._in = []  # open title, style and script elements: (tag, line, parts)
        self._code_depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        line = self.getpos()[0]
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "body":
            self.body_classes = tuple((a.get("class") or "").split())
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "meta" and (a.get("name") or "").lower() == "description":
            self.description = (a.get("content") or "").strip()
            self.prose.append((line, "meta description", self.description))
        if tag == "img":
            self.imgs.append((line, a.get("alt")))
            if a.get("alt"):
                self.prose.append((line, "alt text", a["alt"]))
        for name in ("aria-label", "title"):
            if a.get(name) and tag != "meta":
                self.prose.append((line, name + " attribute", a[name]))
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
        if a.get("style"):
            self.inline_css.append((line, a["style"]))
        if tag in ("code", "pre"):
            self._code_depth += 1
        if tag in ("title", "style", "script"):
            self._in.append((tag, line, []))

    def handle_endtag(self, tag):
        if tag in ("code", "pre") and self._code_depth > 0:
            self._code_depth -= 1
        if self._in and self._in[-1][0] == tag:
            name, line, parts = self._in.pop()
            body = "".join(parts)
            if name == "title":
                self.title = body.strip()
                self.prose.append((line, "title", self.title))
            elif name == "style":
                self.inline_css.append((line, body))
            else:
                self.inline_js.append((line, body))

    def handle_data(self, data):
        if self._in:
            self._in[-1][2].append(data)
            return
        line = self.getpos()[0]
        self.text.append((line, data))
        if self._code_depth == 0 and data.strip():
            self.prose.append((line, "text", data))


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
    try:
        target.relative_to(site)
    except ValueError:
        return None, parts.fragment, "points outside the site folder"
    if target.is_dir():
        target = target / "index.html"
    if not target.is_file():
        return None, parts.fragment, "file not found"
    return target, parts.fragment, None


def name_of(site, path):
    return "{}/{}".format(site.name, path.relative_to(site).as_posix())


def check_reference(site, base_file, line, tag, attr, value, pages, problems):
    where = "{}:{}".format(name_of(site, base_file), line)
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


def check_css_text(site, css_file, label, line_offset, text, problems):
    """A stylesheet or a style element: url(), @import and @font-face sources."""
    seen = set()
    for match in list(CSS_URL.finditer(text)) + list(CSS_IMPORT.finditer(text)):
        value = match.group(2)
        kind = classify(value)
        line = line_offset + text.count("\n", 0, match.start())
        if (line, value) in seen:  # @import url("...") matches both patterns
            continue
        seen.add((line, value))
        where = "{}:{}".format(label, line)
        if kind == "external":
            problems.append("{}: resource from another host in CSS \"{}\"".format(where, value))
        elif kind == "other-scheme":
            if not value.strip().lower().startswith("data:"):
                problems.append("{}: URL scheme is not allowed in CSS \"{}\"".format(where, value))
        elif kind == "empty":
            problems.append("{}: empty URL in CSS".format(where))
        elif kind == "local":
            _, _, error = resolve_local(site, css_file, value)
            if error:
                problems.append("{}: {} in CSS \"{}\"".format(where, error, value))


def check_scripts(site, path, page, problems):
    for line, body in page.inline_js:
        for match in SCRIPT_URL.finditer(body):
            problems.append("{}:{}: URL of another host in a script: \"{}\"".format(name_of(site, path), line, match.group(0)))


def check_trackers(site, problems):
    for path in sorted(site.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            low = line.lower()
            for word in TRACKER_WORDS:
                if word in low:
                    problems.append("{}:{}: tracker word \"{}\"".format(name_of(site, path), number, word))


def check_basics(name, page, problems):
    """Every page: lang, title, description, one h1, heading order, alt text."""
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


def check_variant(name, page, problems):
    """A variant page: the six clients and the meta-word guard."""
    text = " ".join(data for _, data in page.text)
    for client in CLIENTS:
        if client not in text:
            problems.append("{}: client name \"{}\" is not on the page".format(name, client))
    # The visible text is joined, so that a phrase over an element border ("not <b>tested</b>") is found too.
    joined, owners = "", []
    for line, kind, data in page.prose:
        if kind == "text":
            joined += data + " "
            owners.extend([line] * (len(data) + 1))
            continue
        for match in META_RE.finditer(data):
            problems.append("{}:{}: meta word \"{}\" in {}".format(name, line, " ".join(match.group(0).lower().split()), kind))
    for match in META_RE.finditer(joined):
        start = max(0, match.start() - 25)
        context = " ".join(joined[start:match.end() + 25].split())
        problems.append("{}:{}: meta word \"{}\" in text: \"...{}...\"".format(
            name, owners[match.start()], " ".join(match.group(0).lower().split()), context))


def variant_dirs(site):
    return sorted((p for p in site.iterdir() if p.is_dir() and VARIANT_DIR.match(p.name)),
                  key=lambda p: int(p.name[1:]))


def check_fonts(site, problems):
    fonts = site / "fonts"
    if not fonts.is_dir():
        return
    for folder in sorted({p.parent for p in fonts.rglob("*.woff2")}):
        licences = [p for p in folder.iterdir() if p.is_file() and p.name.upper().startswith(("OFL", "LICENSE"))]
        if not licences:
            problems.append("{}: font folder has no licence file (OFL.txt)".format(name_of(site, folder)))


def run(site):
    problems = []
    gallery = site / "index.html"
    if not gallery.is_file():
        return ["{}: the gallery is missing".format(name_of(site, gallery))]
    variants = variant_dirs(site)
    pages = {}
    for path in sorted(site.rglob("*.html")):
        pages[path.resolve()] = parse_page(path)
    for path, page in sorted(pages.items()):
        for line, tag, attr, value in page.refs:
            check_reference(site, path, line, tag, attr, value, pages, problems)
        label = name_of(site, path)
        for line, text in page.inline_css:
            check_css_text(site, path, label, line, text, problems)
        check_scripts(site, path, page, problems)
    for css in sorted(site.rglob("*.css")):
        check_css_text(site, css.resolve(), name_of(site, css), 1, css.read_text(encoding="utf-8"), problems)
    for js in sorted(site.rglob("*.js")):
        for match in SCRIPT_URL.finditer(js.read_text(encoding="utf-8")):
            problems.append("{}: URL of another host in a script: \"{}\"".format(name_of(site, js), match.group(0)))
    check_trackers(site, problems)
    check_fonts(site, problems)
    root = pages[gallery.resolve()]
    check_basics(name_of(site, gallery), root, problems)
    root_is_gallery = "gallery" in root.body_classes
    if not root_is_gallery:
        # after the launch: the root page is the chosen variant (no class "gallery" on its body)
        check_variant(name_of(site, gallery), root, problems)
    gallery_targets = set()
    for line, tag, attr, value in root.refs:
        if tag == "a" and attr == "href" and classify(value) == "local":
            target, _, error = resolve_local(site, gallery.resolve(), value)
            if not error:
                gallery_targets.add(target)
    for folder in variants:
        index = (folder / "index.html").resolve()
        if index not in pages:
            problems.append("{}: the variant has no index.html".format(name_of(site, folder)))
            continue
        check_basics(name_of(site, index), pages[index], problems)
        check_variant(name_of(site, index), pages[index], problems)
        if root_is_gallery and index not in gallery_targets:
            problems.append("{}: the gallery has no link to the variant {}".format(name_of(site, gallery), folder.name))
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check the static landing site: the gallery and every variant.")
    parser.add_argument("site", help="the site folder (the gallery index.html and the folders v1/, v2/, ...)")
    args = parser.parse_args(argv)
    site = Path(args.site)
    if not site.is_dir():
        print("check_site: not a folder: {}".format(site), file=sys.stderr)
        return 2
    site = site.resolve()
    problems = run(site)
    if problems:
        for line in problems:
            print(line, file=sys.stderr)
        print("check_site: {} problem(s)".format(len(problems)), file=sys.stderr)
        return 1
    count = len(variant_dirs(site))
    root = "the gallery" if "gallery" in parse_page(site / "index.html").body_classes else "the root page (a variant)"
    print("check_site: all checks pass ({}, {} and {} variant folder(s))".format(site.name, root, count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
