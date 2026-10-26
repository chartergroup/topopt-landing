# Local 3D viewer

Three.js 0.186.1, including OrbitControls, GLTFLoader, and RoomEnvironment.
Bundled with esbuild 0.28.2 from `scripts/viewer/headlug-viewer.js`.
Three.js is MIT licensed; see LICENSE.txt. The runtime makes no CDN requests.

The checked-in bundle is ready to serve. Rebuild only when changing the viewer:
run `npm install` then `npm run build` in `scripts/viewer/` and update the
recorded SHA-256 in `scripts/check_site.py` after reviewing the output.

The viewer loads the final head-lug printer-upload mesh, converted to indexed
GLB with normals, a rigid orientation change, and centering. Geometry was not
further simplified. See `site/assets/headlug-print-final.provenance.json`.

The model rotates after loading unless reduced motion is preferred. The Stop button pauses rotation.
Rendering pauses offscreen or in a hidden tab, and rotation stops if reduced motion is enabled.
The canvas has keyboard rotation/zoom/reset, and the page retains a still-image
fallback for browsers without WebGL. Touch users can rotate with one finger
and pinch with two; desktop users can use the zoom buttons without trapping
the page's mouse-wheel scrolling.
