# topopt-landing

This repo holds the landing page of topopt: one static page for first-time visitors.

The code of topopt is in another repo: [chartergroup/topopt-demo](https://github.com/chartergroup/topopt-demo).
That repo is private for now.

## What is in this repo

| Path | What it is |
|---|---|
| `site/index.html` | The page. |
| `site/style.css` | The one CSS file. It uses system fonts only. |
| `site/media/` | Copies of the media that the page uses: the clip `hero.mp4`, its poster `hero-poster.jpg` (the last frame of the clip), and two before-and-after pictures. The sources are in `docs/media/` of topopt-demo. |
| `scripts/check_site.py` | The check of the page (Python standard library only). |
| `.github/workflows/pages.yml` | Publishes the folder `site/` to GitHub Pages. It starts by hand only. |

The page has no build step, no framework, no CDN, no web font from another host and no tracker.
A few lines of plain JavaScript start and pause the clip. The page works without them.

## Preview on your computer

Start a local web server in the folder `site/`. Use a free port.

```
cd site
python3 -m http.server 8080 --bind 127.0.0.1
```

Open `http://127.0.0.1:8080/` in a browser. Press Ctrl+C in the terminal to stop the server.
You can also open `site/index.html` from the file system.

## Check the page

```
python3 scripts/check_site.py site
```

The command exits with 0 when all checks pass. Else it prints one line for each problem and exits with 1.
It checks that every local link and every `#anchor` resolves, that no resource comes from another host
(an external link goes only to `https://github.com/chartergroup/`), that no tracker word is in the files,
that every image has an alt text, and that the six client names are on the page.

With a copy of `docs/install-test-checklist.md` of topopt-demo, the check also compares the status word of each client
on the page with the table "Readiness at a glance":

```
python3 scripts/check_site.py site --checklist <path to install-test-checklist.md>
```

## Publish

The workflow `pages.yml` starts by hand: Actions, `pages`, Run workflow. It runs the check, then it uploads
the folder `site/` and deploys it to the environment `github-pages`.
The settings of this repo need the Pages source "GitHub Actions".

## License

This repo has no license file yet. The owner decides it.
The text of the page says that topopt has the MIT License and links to the license files of topopt-demo.
