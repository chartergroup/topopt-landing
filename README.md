# topopt-landing

This repository contains the single-page website for topopt. The product code is in [chartergroup/topopt](https://github.com/chartergroup/topopt).

## Layout

- `site/index.html`, `site/style.css`, and `site/page.js` contain the landing page.
- `site/assets/` contains the bicycle model, renders, original frame drawing, and mesh provenance, and the topopt icon: `topopt-icon.svg` (the header and footer mark), `favicon.svg` (the same shape, light in dark mode), `favicon-32.png` and `apple-touch-icon.png`. Each `site/vN/assets/` has its own copy of the icon files.
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

The check requires exactly one HTML page. It verifies local files and anchors, self-hosted resources, permitted GitHub links, image alt text, heading order, the installation client names, font licenses, and the absence of tracking scripts and editorial placeholders.

## Social preview

`site/assets/social-preview-optimized.jpg` is the 1200 × 630 sharing image. Open Graph and large-image card metadata in `site/index.html` point to its absolute published URL.

The artwork source is `scripts/social-preview.html`. To regenerate it, temporarily copy it to `site/social-preview-artwork.html`, serve the site, and capture a 1200 × 630 browser screenshot after the Manrope font and model image finish loading. Save the screenshot as JPEG to the asset path and remove the temporary page before running the site check. Keep the published site to one HTML page.

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
