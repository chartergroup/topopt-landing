import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const root = document.querySelector('#headlug-viewer');
if (root) mountViewer(root);

function mountViewer(root) {
  const message = root.querySelector('.viewer-message');
  const buttons = [...root.querySelectorAll('[data-view]')];
  const rotateButton = root.querySelector('[data-view="rotate"]');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  buttons.forEach(button => { button.disabled = true; });
  let renderer, controls, environment, meshRoot;
  let frame = 0, automatic = false, visible = true, loaded = false, destroyed = false;
  let size = 250, lastTime = 0;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#e5e8e6');
  const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 4000);
  const setAutomatic = value => {
    automatic = value;
    rotateButton.setAttribute('aria-pressed', String(value));
    rotateButton.textContent = value ? 'Stop' : 'Rotate';
    rotateButton.setAttribute('aria-label', value ? 'Stop model rotation' : 'Start model rotation');
    if (value) requestRender();
  };
  const fail = () => {
    root.classList.remove('is-ready');
    message.textContent = '3D view unavailable. The final design is shown above.';
    buttons.forEach(button => { button.disabled = true; });
    setAutomatic(false);
    loaded = false;
  };
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, powerPreference: 'low-power' });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 0.95;
    const canvas = renderer.domElement;
    canvas.tabIndex = 0;
    canvas.setAttribute('role', 'img');
    canvas.setAttribute('aria-label', 'Final 17-4PH head-lug model. Drag or use arrow keys to rotate. Plus and minus zoom. Home resets the view.');
    root.prepend(canvas);
    controls = new OrbitControls(camera, canvas);
    controls.enableDamping = false;
    controls.enablePan = false;
    // Wheel scrolling belongs to the page; explicit buttons/pinch control zoom.
    controls.enableZoom = false;
    controls.rotateSpeed = 0.7;
    controls.minPolarAngle = 0.08;
    controls.maxPolarAngle = Math.PI - 0.08;
    controls.addEventListener('change', requestRender);
    controls.addEventListener('start', () => setAutomatic(false));
    canvas.addEventListener('webglcontextlost', event => { event.preventDefault(); fail(); });
    const pmrem = new THREE.PMREMGenerator(renderer);
    const room = new RoomEnvironment();
    environment = pmrem.fromScene(room, 0.04);
    scene.environment = environment.texture;
    room.dispose();
    pmrem.dispose();
    scene.add(new THREE.HemisphereLight(0xf4f5ee, 0x555f53, 1.2));
    const key = new THREE.DirectionalLight(0xffffff, 2);
    key.position.set(-200, 350, 250);
    scene.add(key);
    const rim = new THREE.DirectionalLight(0xe8edff, 1.5);
    rim.position.set(180, 160, -180);
    scene.add(rim);

    new GLTFLoader().load(
      new URL('assets/headlug-print-final.glb', document.baseURI).href,
      gltf => {
        if (destroyed) return;
        meshRoot = gltf.scene;
        meshRoot.traverse(object => {
          if (!object.isMesh) return;
          object.material.dispose();
          object.material = new THREE.MeshStandardMaterial({
            color: 0x69736e, metalness: 0.72, roughness: 0.38,
            envMapIntensity: 0.85, side: THREE.DoubleSide
          });
        });
        const box = new THREE.Box3().setFromObject(meshRoot);
        meshRoot.position.sub(box.getCenter(new THREE.Vector3()));
        const extent = box.getSize(new THREE.Vector3());
        size = Math.max(extent.x, extent.y, extent.z);
        scene.add(meshRoot);
        loaded = true;
        buttons.forEach(button => { button.disabled = false; });
        root.classList.add('is-ready');
        root.dataset.modelSource = 'print_final_upload/as_printed_S3_build_upload.stl';
        message.textContent = 'Final print model loaded. Drag to rotate.';
        resize();
        resetView();
        setAutomatic(!reducedMotion.matches);
      },
      progress => {
        if (progress.total) message.textContent = `Loading final print model · ${Math.round(progress.loaded / progress.total * 100)}%`;
      },
      fail
    );

    function resetView(side = false) {
      setAutomatic(false);
      controls.target.set(0, 0, 0);
      const distance = size * (camera.aspect < 1 ? 2.1 : 1.9);
      camera.position.copy(new THREE.Vector3(side ? 0 : -0.85, side ? 0 : 0.32, side ? 1 : 1.7).normalize().multiplyScalar(distance));
      camera.near = size / 1000;
      camera.far = size * 50;
      camera.updateProjectionMatrix();
      controls.update();
      requestRender();
    }
    function zoom(factor) {
      const offset = camera.position.clone().sub(controls.target);
      const distance = THREE.MathUtils.clamp(offset.length() * factor, size * 0.55, size * 5);
      camera.position.copy(controls.target).add(offset.normalize().multiplyScalar(distance));
      controls.update();
      requestRender();
    }
    function orbit(horizontal, vertical) {
      const offset = camera.position.clone().sub(controls.target);
      const spherical = new THREE.Spherical().setFromVector3(offset);
      spherical.theta += horizontal;
      spherical.phi = THREE.MathUtils.clamp(spherical.phi + vertical, 0.08, Math.PI - 0.08);
      camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical));
      controls.update();
      requestRender();
    }
    buttons.forEach(button => button.addEventListener('click', () => {
      if (!loaded) return;
      switch (button.dataset.view) {
        case 'reset': resetView(); break;
        case 'side': resetView(true); break;
        case 'zoom-in': zoom(0.82); break;
        case 'zoom-out': zoom(1.22); break;
        case 'rotate': setAutomatic(!automatic); break;
      }
    }));
    canvas.addEventListener('keydown', event => {
      if (!loaded) return;
      const actions = {
        ArrowLeft: () => orbit(-0.14, 0), ArrowRight: () => orbit(0.14, 0),
        ArrowUp: () => orbit(0, -0.14), ArrowDown: () => orbit(0, 0.14),
        '+': () => zoom(0.82), '=': () => zoom(0.82), '-': () => zoom(1.22),
        Home: () => resetView()
      };
      if (actions[event.key]) { event.preventDefault(); setAutomatic(false); actions[event.key](); }
    });
    // Pinch zoom leaves single-finger drag to OrbitControls and normal scrolling outside the canvas.
    let pinchDistance = 0;
    canvas.addEventListener('touchstart', event => {
      if (event.touches.length === 2) pinchDistance = Math.hypot(event.touches[0].clientX - event.touches[1].clientX, event.touches[0].clientY - event.touches[1].clientY);
    }, { passive: true });
    canvas.addEventListener('touchmove', event => {
      if (event.touches.length !== 2 || !pinchDistance || !loaded) return;
      const next = Math.hypot(event.touches[0].clientX - event.touches[1].clientX, event.touches[0].clientY - event.touches[1].clientY);
      zoom(pinchDistance / next);
      pinchDistance = next;
    }, { passive: true });
    canvas.addEventListener('touchend', () => { pinchDistance = 0; }, { passive: true });
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(root);
    const intersection = new IntersectionObserver(entries => {
      visible = entries[0].isIntersecting;
      if (visible) requestRender();
    });
    intersection.observe(root);
    document.addEventListener('visibilitychange', () => { if (!document.hidden) requestRender(); });
    reducedMotion.addEventListener('change', () => { if (reducedMotion.matches) setAutomatic(false); });
    window.addEventListener('pagehide', event => {
      if (event.persisted) return;
      destroyed = true;
      cancelAnimationFrame(frame);
      resizeObserver.disconnect(); intersection.disconnect(); controls.dispose();
      scene.traverse(object => { if (object.isMesh) { object.geometry.dispose(); object.material.dispose(); } });
      environment.dispose(); renderer.dispose();
    });
    function resize() {
      const width = root.clientWidth, height = root.clientHeight;
      if (!width || !height) return;
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      requestRender();
    }
  } catch { fail(); }

  function requestRender() {
    if (frame || destroyed || !loaded || !visible || document.hidden) return;
    frame = requestAnimationFrame(render);
  }
  function render(time) {
    frame = 0;
    if (!loaded || !visible || document.hidden || destroyed) return;
    if (automatic) {
      const delta = Math.min((time - lastTime) / 1000 || 0, 0.05);
      const offset = camera.position.clone().sub(controls.target);
      offset.applyAxisAngle(new THREE.Vector3(0, 1, 0), delta * 0.22);
      camera.position.copy(controls.target).add(offset);
      controls.update();
    }
    lastTime = time;
    renderer.render(scene, camera);
    if (automatic) requestRender();
  }
}
