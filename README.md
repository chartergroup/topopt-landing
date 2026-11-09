# topopt-landing

This repository contains the website for topopt: the landing page and a contact page. The product code is in [chartergroup/topopt](https://github.com/chartergroup/topopt).

## Layout

- `site/index.html`, `site/style.css`, and `site/page.js` contain the landing page.
- `site/contact/index.html` is the contact page. Its form posts to a Google Apps Script web app, `scripts/contact-form/Code.gs`, which emails each message to the team (see "Contact form").
- `site/assets/` contains the bicycle model, renders, original frame drawing, and mesh provenance, and the topopt icon: `topopt-icon.svg` (the header and footer mark), `favicon.svg` (the same shape, light in dark mode), `favicon-light.svg` and `favicon-dark.svg` (`page.js` swaps them when the browser switches between light and dark mode, because a browser draws an SVG favicon only once), `favicon-32.png` and `apple-touch-icon.png`. Each `site/vN/assets/` has its own copy of the icon files.
- `site/media/` contains the recorded wall-hook optimization and its poster.
- `site/fonts/manrope/` contains the self-hosted font and its SIL OFL license.
- `site/icons/` contains the GitHub mark of the root page (Simple Icons, CC0) and `LICENSES.md` with its source.
- `site/vendor/three/` contains the bundled Three.js viewer and MIT license.
- `scripts/viewer/` contains the editable viewer source and pinned build dependencies.
- `scripts/check_site.py` checks links, resources, accessibility markup, and content.
- `CONTENT_NOTES.md` records the sources for the page's content and model.

The selected design is served directly at `/`. The gallery and previous page variants are retained only in Git history.

## Preview and check

```sh
python3 -m http.server 8080 --bind 127.0.0.1 --directory site
```

Open `http://127.0.0.1:8080/`.

```sh
python3 scripts/check_site.py site
```

The check allows two HTML pages, `index.html` and `contact/index.html`. It verifies local files and anchors, self-hosted resources, permitted GitHub links, the address the contact form posts to, image alt text, heading order, the installation client names, font licenses, and the absence of tracking scripts and editorial placeholders.

## Social preview

`site/assets/social-preview-optimized.jpg` is the 1200 × 630 sharing image. Open Graph and large-image card metadata in `site/index.html` point to its absolute published URL.

The artwork source is `scripts/social-preview.html`. To regenerate it, temporarily copy it to `site/social-preview-artwork.html`, serve the site, and capture a 1200 × 630 browser screenshot after the Manrope font and model image finish loading. Save the screenshot as JPEG to the asset path and remove the temporary page before running the site check.

## Search engines

The site address is `https://topopt.ai/` (`SITE_ORIGIN` in `scripts/check_site.py`). The root page has the canonical link to it,
Open Graph and Twitter URLs on it, and JSON-LD (`WebSite` and `SoftwareApplication`). Each `site/vN/` variant has
`<meta name="robots" content="noindex">`. `site/robots.txt` names `https://topopt.ai/sitemap.xml`, and `site/sitemap.xml` lists the root page and the contact page.
Search engines read `robots.txt` and the sitemap only at the root of the host, so they work once the site is served at `https://topopt.ai/`.
The check guards all of this. If the address changes, change `SITE_ORIGIN`, the root page, `robots.txt` and `sitemap.xml` together.

## Contact form

The form on `site/contact/index.html` posts to a Google Apps Script web app that runs as a team member's Google account.
The script, `scripts/contact-form/Code.gs`, checks the fields and emails the message to the team with the visitor's
address as Reply-To. The team addresses are the script property `RECIPIENTS`, not part of this repository.
A hidden field named `website` catches bots: when it is filled, the script answers "ok" and sends nothing.
`page.js` sends the form in the background and shows the result on the page; without JavaScript the browser posts the form
and the script shows a short page with a link back.

The same web app also receives the contact form of the charter site (a post with `form=charter`). It emails that message,
with all its fields, to the script property `CHARTER_RECIPIENTS`; the optional `CHARTER_SITE_URL` is the link back on the
no-JavaScript page. The deployment URL stays the same (Manage deployments, Edit, New version).

To change the script, paste the new `Code.gs` into the Apps Script project and use Deploy, Manage deployments, Edit,
Version: New version. That keeps the `/exec` address. A new deployment gets a new address, which then has to go into the
form's `action` (the site check accepts only a `https://script.google.com/macros/s/<id>/exec` address).
Google limits a personal account to 100 email recipients per day, so about 25 messages a day for four recipients.

## Viewer

The viewer uses Three.js 0.186.1 and is bundled with esbuild 0.28.2. All runtime assets are checked in; serving the website requires no build step or CDN. The model rotates automatically with a Stop button. Reduced-motion preferences disable automatic rotation, and rendering pauses offscreen and in hidden tabs.

To rebuild after editing the viewer:

```sh
cd scripts/viewer
npm ci
npm run build
```

Review the rebuilt bundle and update its SHA-256 in `scripts/check_site.py`. This pins the exception for Three.js shader identifiers and reference URLs that would otherwise match the checker's simple tracking and URL scans. See `site/vendor/three/README.md` for details.

## Publish

The `pages` workflow in `.github/workflows/pages.yml` runs manually. It checks the site and deploys `site/` to GitHub Pages. No push or pull request automatically runs the workflow. The repository's Pages source must be set to GitHub Actions.

```sh
gh workflow run pages.yml --ref main
```

## Licenses

The font and Three.js licenses are included alongside those assets. Links on the page refer to the MIT license and third-party notices in the topopt product repository.
