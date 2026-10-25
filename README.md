# topopt-landing

This repo holds the landing site of topopt: a gallery of landing page variants.
Each variant is a full one-page site in its own folder. All variants stand side by side.

The code of topopt is in another repo: [chartergroup/topopt-demo](https://github.com/chartergroup/topopt-demo).

## Layout

| Path | What it is |
|---|---|
| `site/index.html` | The gallery: one card for each variant. It is the root page until launch. |
| `site/style.css` | The CSS of the gallery. |
| `site/gallery/vN.jpg` | The thumbnail of variant `vN` (720 px wide, JPEG, at most about 120 KB). |
| `site/v1/`, `site/v2/`, ... | One folder for each variant. Each has `index.html` and `style.css`. |
| `site/media/` | The shared media: the clip `hero.mp4`, its poster `hero-poster.jpg` (the last frame of the clip), and the pictures `before-after-front.png` and `before-after.png`. The sources are in `docs/media/` of topopt-demo. |
| `site/fonts/<family>/` | The shared self-hosted fonts: the `.woff2` files and the licence file `OFL.txt` of the family. |
| `scripts/check_site.py` | The check of the whole site (Python standard library only). |
| `.github/workflows/pages.yml` | Publishes the folder `site/` to GitHub Pages. It starts by hand only. |

A variant uses the shared files with relative paths: `../media/hero.mp4`, `../fonts/<family>/<file>.woff2`.
A new deploy never covers an old variant, because each variant has its own folder.

## Rules for every variant page

Write each page as it reads on the day of the launch.

- The code repo `https://github.com/chartergroup/topopt-demo` is public and the install works.
- No meta text. A page has no note about who can see the repo, no note that something is not tested or not checked,
  no status word or badge, no label such as "preview", "beta", "draft", "for now" or "coming soon", and no note about
  checks, screenshots or how the page was made. The list of words is `META_WORDS` in `scripts/check_site.py`.
  The check fails when one of them is in the text of a variant page.
- Do not claim more than the sources say. List the clients and their steps. Do not write "tested" or
  "works in X" or "supports X" unless a source says it. No number that is not in a source.
  No star count, no "trusted by".
- Keep the text short: one line for each idea. In the install part, give each client one short command or
  config line and a link to the full steps in topopt-demo (`README.md` or `docs/clients.md`).
- The six clients are on every variant page: Claude Code, Claude Desktop, Cursor, Codex CLI, VS Code, Gemini CLI.
  The hero links go to the install block of each client (the ids `install-claude-code`, `install-claude-desktop`,
  `install-cursor`, `install-codex-cli`, `install-vs-code`, `install-gemini-cli`).
- Name no other product or company: no CAD, CAE or topology product, and no site that gave an idea for a style.
  The agent clients above, MCP and the open-source libraries that topopt uses are fine as text. No logos.
  No personal names.
- Static HTML and CSS only. No build step, no framework, no JavaScript library, no CDN, nothing from another host
  (no font, script, image, analytics or cookie). A few lines of plain JavaScript are allowed for the play control of the clip.
  A font is allowed only when it is self-hosted with an open licence (SIL OFL): put the files and the licence file
  in `site/fonts/<family>/` (at most 4 font files for each variant).
- Accessibility: `lang="en"`, a title, a meta description, headings in order, alt text on every image,
  links that say where they go, a page that reads well on a phone (390 px wide), clear colour contrast.
- The clip: `<video muted loop playsinline poster=...>` with autoplay. With `prefers-reduced-motion: reduce`
  it does not start by itself: show the poster and a play control. No other moving element, no animated text,
  no scrolling effect.
- An external link goes only to `https://github.com/chartergroup/...`.

## Add a variant

1. Make the folder `site/vN/` (the next free number) with `index.html` and `style.css`.
   Read the shared files with `../media/...` and `../fonts/...`.
2. Add the card to the gallery. Open `site/index.html`, copy the whole block `<li class="card" id="card-v1"> ... </li>`
   and paste it after the last card. Change the id (`card-vN`), the two links (`vN/index.html`), the picture
   (`gallery/vN.jpg`) and its alt text, the name, the date and the one line. The cards need no other change.
3. Make the thumbnail `site/gallery/vN.jpg`: a screenshot of the first screen of the page (1440 x 900,
   with `prefers-reduced-motion: reduce`, so that the clip shows its poster), scaled to 720 px wide,
   saved as JPEG, at most about 120 KB.
4. Run the check (below). It fails when the gallery has no link to the folder.

## Preview on your computer

Start a local web server in the folder `site/`. Use a free port.

```
cd site
python3 -m http.server 8080 --bind 127.0.0.1
```

Open `http://127.0.0.1:8080/` in a browser. The gallery opens first; each card has an Open link.
Press Ctrl+C in the terminal to stop the server.
You can also open `site/index.html` from the file system.

## Check the site

```
python3 scripts/check_site.py site
```

The command exits with 0 when all checks pass. Else it prints one line for each problem and exits with 1.
It checks the gallery and every folder `site/v*/`:

- every local link, source and `#anchor` resolves, also in the CSS (`url(...)`, `@import`, `@font-face`);
- no resource comes from another host, and an external link goes only to `https://github.com/chartergroup/`;
- no tracker word is in the files;
- every image has an alt text; each page has `lang`, a title, a meta description, one `h1` and no skipped heading level;
- every variant page has the six client names;
- no meta word (the rule above) is in the visible text, the title, the description or the alt text of a variant page.
  Text inside `<code>` and `<pre>` is not checked;
- the gallery has a link to every variant folder;
- every font folder with `.woff2` files has a licence file.

## Publish

The workflow `pages.yml` starts by hand: Actions, `pages`, Run workflow. It runs the check, then it uploads
the whole folder `site/` and deploys it to the environment `github-pages`.
The settings of this repo need the Pages source "GitHub Actions".
Until launch, the gallery is the root page and each variant has its own address (`/v1/`, `/v2/`, ...).

## Launch: the chosen variant becomes the root

At launch, copy every file of the chosen variant folder `site/vN/` (the page, its stylesheet, and its script and icon if
it has them) to `site/`, over `site/index.html` and `site/style.css`. In the copies, change `../media/` to `media/` and
`../fonts/` to `fonts/`. The root page then has no class `gallery` on its body,
so the check treats it as a variant page (it must pass all the rules above) and does not look for gallery cards.
The folders `site/v*/` stay, so the address of each variant does not change.

## License

This repo has no license file. The pages say that topopt has the MIT License and link to the license files of
topopt-demo. Each font folder in `site/fonts/` has the license of its font (`OFL.txt`).
