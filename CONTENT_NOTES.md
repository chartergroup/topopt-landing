# Landing page content and model provenance

The selected design is served at the site root. The gallery and earlier page variants have been removed; Git history retains them.

## Content and evidence

- Leads with ease of use, agent workflow, local compute and token-cost mechanics.
- The original illustrative selection was superseded after the owner identified it as an earlier version. The hero now renders the final supplier-upload mesh: `topopt/inset2/print_pass/print_final_upload/as_printed_S3_build_upload.stl`, derived from `print_final/as_printed_S3_build.stl`. The final package contains a build sheet, machining instructions and release record dated October 6, 2026. The owner states this is the part they had printed; no physical photograph is used.
- The source upload mesh has 193,498 faces and was already reduced for the printer's upload limit. Its original verification reports 0.042 mm maximum sampled deviation from the full print STL and -0.0095% volume change. No additional simplification or geometric smoothing was applied for the website.
- Converted that source into `assets/headlug-print-final.glb` (4.64 MB, 96,653 vertices), undoing its S3 build orientation and centering it for display. The GLB contains smooth lighting normals. Source and GLB SHA-256 values are in the adjacent provenance JSON.
- The fallback and case-study images now come from `print_final/acc/render_nominal_isometric.png` and `render_nominal_side.png`. These depict the final finished nominal model, while the interactive geometry includes print stock. Both are actual geometric renders, not photographs. No manufacturing certification, head-lug mass-reduction percentage, solve time or dollar cost was invented.
- Material is 17-4PH stainless steel, as documented in `print_final/BUILD_SHEET.md`.
- The original brief excerpt comes from `library_test_case/real_world_headlug_brief/brief.md` in the bicycle project. It is an input excerpt, not a fabricated transcript of a successful agent run.
- The original head-lug workflow's M1 / 16 GB hardware and numerical solve without model calls are documented in that project's `START_HERE.md`; the page attributes the hardware to the original workflow rather than to an independently repeated run of the new package.
- Existing hook media and figures are reused from v1–v6: 85.6 g to 26.5 g, 69% less mass, 80 iterations. The video shows a recorded optimization.
- Distinguishes local numerical compute from an AI client that may call a cloud model.
- Gives Claude Code, Codex, Cursor, and Other Agents equal installation sections. The Claude Code commands retain the release pin. Codex and Cursor use the repository checkout and launcher configuration.
- No change to the public product name: topopt. Naming can be considered separately.
- The owner explicitly requested Three.js, superseding the original no-JavaScript-library constraint for this page. It is pinned to 0.186.1, MIT licensed, and bundled locally with esbuild 0.28.2. The site requires no runtime build or CDN. Source and pinned build manifest are in `scripts/viewer/`; runtime and license are in `site/vendor/three/`.
- The site checker exempts only the recorded hash of the reviewed local bundle from its word-based URL/tracker heuristics. Three.js includes harmless SVG namespace URLs, paper references and shader identifiers containing “pixel”. Changed or unknown scripts still receive the original scans; an unrecorded bundle change fails explicitly.

## Review

Serve `site/` and open `/`. Run `python3 scripts/check_site.py site` for the site's structural/link/content checks. Check desktop and 390 px layouts, copy interaction, disclosures, model rotation/side/reset/zoom controls, and video playback. The model rotates automatically after loading, with a Stop button. Reduced-motion preferences disable automatic rotation. Rendering suspends offscreen and in hidden tabs.

## Page-comment revisions

- Applied the owner's headline and introductory wording, enlarged and renamed the hero eyebrow to “Agent First Generative Design”, and changed the model label to “001 / Bicycle Headtube”.
- Installation is the first section after the hero. The hero button is now explicitly labelled “Install topopt” and scrolls to that section; the repository link opens GitHub. The former model-caption/project link and the promise strip were removed.
- Replaced the sketch chip with the actual frame drawing attached by the owner on September 17, 2026, recovered from the original conversation's embedded image. It is copied unchanged to `assets/early-frame-sketch.png` and opens at full resolution when clicked. It is not a new illustration or the later reconstructed reference diagram.
- Rewrote body copy in complete sentences, removed the requested slogans, captions, provenance prose, and setup note, and revised the headtube case study and sample section.
- The sample-files link now explicitly says GitHub and opens the repository's `examples/` folder, which contains the hook, ladle, and interface examples.
- The hook clip has no native controls. A play/pause button sits under it; `page.js` keeps the button label in step with the real state of the clip, and the clip keeps its reduced-motion handling.
- The later readability review removed the separate local-computation section, repeated agent descriptions, the hero footnote, and the generic footer sentence. Body text and small labels were enlarged. The install section uses four equally styled cards with individual copy controls and appears directly after a more compact hero.
- The owner's edits of 2026-10-26 on the root page: new hero title and two buttons (Install, Examples), the 3D viewer as tall as the first section on desktop, platform and agent icons (files and licences in `site/icons/`), the same band background for the install section, the real-world example and the questions, all visuals in the right column, and the 2x hook clip with its play/pause button.
