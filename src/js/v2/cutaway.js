// v2 — explorable facility cutaway. Procedural stand-in for the Blender GLB kit (see research/03-v2-3d-plan.md).
// Scroll or click a journey step to move the camera; click a part for its card; drag (mouse) to orbit.
// Falls back to the SVG poster when WebGL is missing or the context is lost.
import * as THREE from 'three';

const stage = document.getElementById('cutaway');
const steps = [...document.querySelectorAll('#steps .step')];
if (stage && hasWebGL()) init();

function hasWebGL() {
  try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch (e) { return false; }
}

function init() {
  const PARTS = JSON.parse(stage.dataset.parts);
  const card = stage.querySelector('.part-card');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  stage.prepend(renderer.domElement);
  renderer.domElement.setAttribute('aria-hidden', 'true');

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1.2, 0.5, 200);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x223344, 1.6));
  const sun = new THREE.DirectionalLight(0xffffff, 1.6); sun.position.set(12, 20, 14); scene.add(sun);

  const palette = {};
  const mats = [];   // { mat, role } so a theme change can recolour everything
  const edges = [];  // { line, part }
  const groups = {}; // part key -> Group

  function mat(role, opacity = 1) {
    const m = new THREE.MeshStandardMaterial({ roughness: 0.85, metalness: 0.05, transparent: opacity < 1, opacity });
    mats.push({ mat: m, role }); return m;
  }
  function box(part, w, h, d, x, y, z, role = 'body', opacity = 1) {
    const g = new THREE.BoxGeometry(w, h, d);
    const mesh = new THREE.Mesh(g, mat(role, opacity));
    mesh.position.set(x, y + h / 2, z);
    const line = new THREE.LineSegments(new THREE.EdgesGeometry(g), new THREE.LineBasicMaterial({ transparent: true }));
    mesh.add(line); edges.push({ line, part });
    mesh.userData.part = part;
    (groups[part] ||= new THREE.Group()).add(mesh);
    return mesh;
  }

  // Shell: slab and two back walls (front walls cut away)
  box(null, 20, 0.3, 12, 0, -0.3, 0, 'floor');
  box(null, 20, 5, 0.25, 0, 0, -6, 'wall', 0.55);
  box(null, 0.25, 5, 12, -10, 0, 0, 'wall', 0.4);
  // Cold room and freezer
  box('cold', 6, 3, 5, -6, 0, -2.5, 'cold', 0.9);
  box('freezer', 5, 3, 5, 0.5, 0, -2.5, 'freezer', 0.9);
  // Dock: frame, door, leveller
  box('dock', 0.4, 4, 0.4, 10, 0, -2.2); box('dock', 0.4, 4, 0.4, 10, 0, 1.2);
  box('dock', 0.4, 0.4, 3.8, 10, 3.6, -0.5); box('dock', 0.15, 3.4, 3.2, 10, 0.2, -0.5, 'door', 0.7);
  box('dock', 2.4, 0.15, 3, 8.6, 0, -0.5, 'accent');
  // Plant skid: compressor rack and two condensers
  box('plant', 3.2, 1.6, 1.4, 7, 0, -4.6);
  box('plant', 1.6, 1.4, 1.6, 5.2, 0, -4.4, 'body'); box('plant', 1.6, 1.4, 1.6, 5.2, 1.4, -4.4, 'body');
  // AHU and duct run on the back wall
  box('ahu', 5, 1.4, 1.4, -5, 4.2, -5.2); box('ahu', 9, 0.6, 0.6, 2, 4.6, -5.2, 'duct');
  // Racking rows with pallets
  for (let r = 0; r < 3; r++) {
    const z = 2.2 + r * 1.5;
    box('racks', 12, 0.08, 0.9, -3, 1.4, z); box('racks', 12, 0.08, 0.9, -3, 2.8, z);
    for (let x = -8.5; x <= 2.5; x += 1.4) { box('racks', 0.08, 3.6, 0.9, x, 0, z); box('racks', 1, 0.9, 0.8, x + 0.7, 1.48, z, 'pallet'); }
  }
  // Service van outside the dock
  box('van', 4.2, 2.4, 2, 14, 0.3, 4, 'body'); box('van', 1.4, 1.6, 2, 16.8, 0.3, 4, 'body');
  Object.values(groups).forEach(g => scene.add(g));

  // Each shot frames its parts with the rest of the building still in view
  const SHOTS = [
    { parts: ['dock'], pos: [30, 14, 18], at: [7, 1.2, -0.5] },
    { parts: ['cold', 'freezer'], pos: [10, 18, 26], at: [-3, 1.2, -2] },
    { parts: ['plant'], pos: [26, 15, 14], at: [5, 1.4, -3.5] },
    { parts: ['ahu', 'racks'], pos: [14, 22, 30], at: [-1.5, 2.2, 0] },
    { parts: ['van'], pos: [32, 13, 26], at: [10, 1.2, 2] },
  ];
  const OVERVIEW = { parts: [], pos: [28, 22, 32], at: [2, 0.5, 0] };
  let shot = OVERVIEW, active = new Set();
  const camPos = new THREE.Vector3(...OVERVIEW.pos), camAt = new THREE.Vector3(...OVERVIEW.at);
  const goalPos = camPos.clone(), goalAt = camAt.clone();
  let yaw = 0;

  function readPalette() {
    const cs = getComputedStyle(stage);
    const c = v => new THREE.Color(cs.getPropertyValue(v).trim() || '#888');
    Object.assign(palette, { acc: c('--acc'), fg: c('--fg'), bg2: c('--bg-2'), rule: c('--rule-2'), mist: c('--mist') });
  }
  function paint() {
    const ROLE = { floor: palette.bg2, wall: palette.bg2, body: palette.rule, door: palette.mist, duct: palette.mist, pallet: palette.mist, cold: palette.acc, freezer: palette.fg, accent: palette.acc };
    for (const { mat: m, role } of mats) { m.color.copy(ROLE[role] || palette.rule); m.emissive.setRGB(0, 0, 0); }
    for (const { line, part } of edges) {
      const on = active.has(part);
      line.material.color.copy(on ? palette.acc : palette.rule);
      line.material.opacity = on || !active.size ? 1 : 0.35;
    }
    for (const [k, g] of Object.entries(groups)) g.children.forEach(mesh => {
      if (active.has(k)) mesh.material.emissive.copy(palette.acc).multiplyScalar(0.25);
    });
    dirty = true;
  }
  function setShot(i) {
    shot = i == null ? OVERVIEW : SHOTS[i];
    active = new Set(shot.parts);
    goalPos.set(...shot.pos); goalAt.set(...shot.at); yaw = 0;
    if (reduce) { camPos.copy(goalPos); camAt.copy(goalAt); }
    steps.forEach((s, j) => j === i ? s.setAttribute('aria-current', 'step') : s.removeAttribute('aria-current'));
    paint();
  }

  // Steps: scroll position picks the step, clicks pick it too
  const io = new IntersectionObserver(es => es.forEach(e => e.isIntersecting && setShot(+e.target.dataset.step)), { rootMargin: '-45% 0px -45% 0px' });
  steps.forEach(s => { io.observe(s); s.addEventListener('click', () => setShot(+s.dataset.step)); });

  // Picking and orbit
  const ray = new THREE.Raycaster(), ptr = new THREE.Vector2();
  let drag = null;
  const el = renderer.domElement;
  el.addEventListener('pointerdown', e => { if (e.pointerType === 'mouse') drag = { x: e.clientX, moved: false }; });
  addEventListener('pointerup', () => { drag = null; });
  el.addEventListener('pointermove', e => {
    if (!drag) return;
    const dx = e.clientX - drag.x; drag.x = e.clientX;
    if (Math.abs(dx) > 1) drag.moved = true;
    yaw += dx * 0.006; dirty = true;
  });
  el.addEventListener('click', e => {
    if (drag && drag.moved) return;
    const r = el.getBoundingClientRect();
    ptr.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ptr, camera);
    const hit = ray.intersectObjects(Object.entries(groups).filter(([k]) => k !== 'null').map(([, g]) => g), true)
      .find(h => h.object.userData.part);
    if (!hit) { card.hidden = true; return; }
    const key = hit.object.userData.part, info = PARTS[key];
    active = new Set([key]); paint();
    card.innerHTML = '';
    const b = document.createElement('strong'); b.textContent = info.t;
    card.append(b, document.createTextNode(info.s)); card.hidden = false;
  });

  // Size, visibility, context loss
  function resize() {
    const { width, height } = stage.getBoundingClientRect();
    renderer.setSize(width, height, false); camera.aspect = width / height; camera.updateProjectionMatrix(); dirty = true;
  }
  new ResizeObserver(resize).observe(stage);
  let visible = false, dirty = true, raf = 0;
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; if (visible && !raf) raf = requestAnimationFrame(loop); }).observe(stage);
  el.addEventListener('webglcontextlost', e => {
    e.preventDefault(); stage.classList.remove('live'); el.remove();
    card.textContent = stage.dataset.fallback; card.hidden = false;
  });
  addEventListener('ftc:design', () => { readPalette(); paint(); });

  const tmp = new THREE.Vector3();
  function loop() {
    raf = 0;
    if (!visible) return;
    const k = reduce ? 1 : 0.06;
    camPos.lerp(goalPos, k); camAt.lerp(goalAt, k);
    tmp.copy(camPos).sub(camAt).applyAxisAngle(THREE.Object3D.DEFAULT_UP, yaw).add(camAt);
    camera.position.copy(tmp); camera.lookAt(camAt);
    const moving = camPos.distanceToSquared(goalPos) > 1e-4;
    if (moving || dirty) { renderer.render(scene, camera); dirty = false; }
    raf = requestAnimationFrame(loop);
  }

  readPalette(); resize(); setShot(null);
  stage.classList.add('live');
}
