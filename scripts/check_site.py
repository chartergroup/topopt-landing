#!/usr/bin/env python3
"""Check the static landing page. Standard library only.

Usage:
    python3 scripts/check_site.py site

The site folder holds a single landing page at index.html.

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
- the landing page has the six client names;
- the landing page has no meta word (private, not tested, status, preview, ...) in its visible text,
  title, meta description, alt text, aria-label or title attribute (text inside code and pre is not checked);
- every font folder with .woff2 files has a licence file (OFL*, LICENSE*);
- search engines: a canonical link goes to SITE_ORIGIN only, and the root page has the canonical link
  SITE_ORIGIN; JSON-LD is valid JSON, and its URLs go to SITE_ORIGIN, https://github.com/chartergroup/
  or https://schema.org/ only; a variant page v<N>/index.html has <meta name="robots" content="noindex">,
  and the root page has none; robots.txt names SITE_ORIGIN sitemap.xml; sitemap.xml lists only pages
  of SITE_ORIGIN that exist in the site folder and are not noindex.
"""

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
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
ALLOWED_EXTERNAL_LINK = re.compile(r"^https://github\.com/chartergroup(?:[/?#]|$)")
# The address of the site. The canonical link, JSON-LD, robots.txt and the sitemap name it.
SITE_ORIGIN = "https://topopt.ai/"
JSON_LD_URL = re.compile(r"^(?:" + re.escape(SITE_ORIGIN) + r"|https://github\.com/chartergroup(?:[/?#]|$)|https://schema\.org(?:/|$))")
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
# the attributes that hold a URL, for every tag
URL_ATTRS = ("href", "src", "poster", "action", "srcset", "data")
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
CSS_IMPORT = re.compile(r"@import\s+(?:url\(\s*)?(['\"])(.*?)\1", re.IGNORECASE)
SCRIPT_URL = re.compile(r"(?:https?:)?//[A-Za-z0-9.-]+\.[A-Za-z]{2,}", re.IGNORECASE)
TEXT_SUFFIXES = (".html", ".css", ".js")
# The owner-requested Three.js viewer is bundled locally, with its MIT licence.
# Three.js contains shader references, the SVG namespace, and rendering identifiers
# such as pixelRatio. These are not outbound requests or tracking pixels. Exempt
# only this exact reviewed bundle, and reject any unrecorded replacement.
PINNED_VENDOR_JS = {
    "vendor/three/headlug-viewer.js": "b3b1eb9748257562ae32792d0eb0ae370dd50bc435fd58311c02c076a8dd26dd",
}


def pinned_vendor(site, path):
    expected = PINNED_VENDOR_JS.get(path.relative_to(site).as_posix())
    return bool(expected and hashlib.sha256(path.read_bytes()).hexdigest() == expected)


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
        self.json_ld = []  # (line, text)
        self.canonicals = []  # (line, href)
        self.robots = []  # the content of each <meta name="robots">
        self._in = []  # open title, style and script elements: (tag, line, parts, kind)
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
        if tag == "meta" and (a.get("name") or "").lower() == "robots":
            self.robots.append((a.get("content") or "").lower())
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
        canonical = tag == "link" and "canonical" in (a.get("rel") or "").lower().split()
        if canonical:
            # A canonical link names the address of this page. The browser loads nothing from it.
            self.canonicals.append((line, (a.get("href") or "").strip()))
        for attr in URL_ATTRS:
            if attr not in a or (canonical and attr == "href"):
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
            kind = tag
            if tag == "script" and (a.get("type") or "").strip().lower() == "application/ld+json":
                kind = "json-ld"
            self._in.append((tag, line, [], kind))

    def handle_endtag(self, tag):
        if tag in ("code", "pre") and self._code_depth > 0:
            self._code_depth -= 1
        if self._in and self._in[-1][0] == tag:
            name, line, parts, kind = self._in.pop()
            body = "".join(parts)
            if name == "title":
                self.title = body.strip()
                self.prose.append((line, "title", self.title))
            elif name == "style":
                self.inline_css.append((line, body))
            elif kind == "json-ld":
                self.json_ld.append((line, body))
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
        if pinned_vendor(site, path):
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


def check_content(name, page, problems):
    """The six clients and the meta-word guard."""
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


def check_fonts(site, problems):
    fonts = site / "fonts"
    if not fonts.is_dir():
        return
    for folder in sorted({p.parent for p in fonts.rglob("*.woff2")}):
        licences = [p for p in folder.iterdir() if p.is_file() and p.name.upper().startswith(("OFL", "LICENSE"))]
        if not licences:
            problems.append("{}: font folder has no licence file (OFL.txt)".format(name_of(site, folder)))


def json_ld_urls(value):
    """Yield every string in a JSON value that is a URL with a host."""
    if isinstance(value, dict):
        for item in value.values():
            yield from json_ld_urls(item)
    elif isinstance(value, list):
        for item in value:
            yield from json_ld_urls(item)
    elif isinstance(value, str) and re.match(r"^(?:[A-Za-z][A-Za-z0-9+.-]*:)?//", value.strip()):
        yield value.strip()


def is_noindex(page):
    return any("noindex" in content.replace(" ", "").split(",") for content in page.robots)


def check_search(site, pages, problems):
    """The tags and files for search engines (see the module docstring)."""
    root = (site / "index.html").resolve()
    for path, page in sorted(pages.items()):
        name = name_of(site, path)
        for line, href in page.canonicals:
            if not href.startswith(SITE_ORIGIN):
                problems.append("{}:{}: canonical link is not to {}: \"{}\"".format(name, line, SITE_ORIGIN, href))
        for line, body in page.json_ld:
            try:
                data = json.loads(body)
            except ValueError as exc:
                problems.append("{}:{}: JSON-LD is not valid JSON: {}".format(name, line, exc))
                continue
            for url in json_ld_urls(data):
                if not JSON_LD_URL.match(url):
                    problems.append("{}:{}: JSON-LD URL is not to {}, https://github.com/chartergroup/ or "
                                    "https://schema.org/: \"{}\"".format(name, line, SITE_ORIGIN, url))
        if path == root:
            if [href for _, href in page.canonicals] != [SITE_ORIGIN]:
                problems.append("{}: the root page needs one canonical link to {}".format(name, SITE_ORIGIN))
            if is_noindex(page):
                problems.append("{}: the root page has noindex".format(name))
        elif not is_noindex(page):
            problems.append("{}: a variant page needs <meta name=\"robots\" content=\"noindex\">".format(name))
    sitemap_url = SITE_ORIGIN + "sitemap.xml"
    robots = site / "robots.txt"
    if not robots.is_file():
        problems.append("{}: robots.txt is missing".format(name_of(site, robots)))
    else:
        named = [line.split(":", 1)[1].strip() for line in robots.read_text(encoding="utf-8").splitlines()
                 if line.split(":", 1)[0].strip().lower() == "sitemap" and ":" in line]
        if sitemap_url not in named:
            problems.append("{}: no line \"Sitemap: {}\"".format(name_of(site, robots), sitemap_url))
    sitemap = site / "sitemap.xml"
    if not sitemap.is_file():
        problems.append("{}: sitemap.xml is missing".format(name_of(site, sitemap)))
        return
    try:
        tree = ET.parse(sitemap)
    except ET.ParseError as exc:
        problems.append("{}: sitemap.xml is not valid XML: {}".format(name_of(site, sitemap), exc))
        return
    locs = [(loc.text or "").strip() for loc in tree.getroot().iter(SITEMAP_NS + "loc")]
    if not locs:
        problems.append("{}: sitemap.xml lists no page".format(name_of(site, sitemap)))
    for loc in locs:
        if not loc.startswith(SITE_ORIGIN):
            problems.append("{}: sitemap URL is not on {}: \"{}\"".format(name_of(site, sitemap), SITE_ORIGIN, loc))
            continue
        target = (site / unquote(urlsplit(loc).path).lstrip("/")).resolve()
        if target.is_dir():
            target = target / "index.html"
        page = pages.get(target)
        if page is None:
            problems.append("{}: sitemap URL has no page in the site folder: \"{}\"".format(name_of(site, sitemap), loc))
        elif is_noindex(page):
            problems.append("{}: sitemap URL is a noindex page: \"{}\"".format(name_of(site, sitemap), loc))


def run(site):
    problems = []
    index = site / "index.html"
    if not index.is_file():
        return ["{}: index.html is missing".format(name_of(site, index))]
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
        if pinned_vendor(site, js):
            continue
        if js.relative_to(site).as_posix() in PINNED_VENDOR_JS:
            problems.append("{}: vendored viewer hash does not match the recorded bundle".format(name_of(site, js)))
        for match in SCRIPT_URL.finditer(js.read_text(encoding="utf-8")):
            problems.append("{}: URL of another host in a script: \"{}\"".format(name_of(site, js), match.group(0)))
    check_trackers(site, problems)
    check_fonts(site, problems)
    check_search(site, pages, problems)
    for path, page in pages.items():
        check_basics(name_of(site, path), page, problems)
        check_content(name_of(site, path), page, problems)
    # The landing page is index.html. A variant to compare with it is one page at v<N>/index.html.
    for path in pages:
        if not re.fullmatch(r"index\.html|v[0-9]+/index\.html", name_of(site, path).split("/", 1)[1]):
            problems.append("{}: an HTML page must be index.html or v<N>/index.html".format(name_of(site, path)))
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check the static landing page.")
    parser.add_argument("site", help="the site folder containing index.html")
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
    print("check_site: all checks pass ({})".format(site.name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
