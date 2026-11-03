// v2 — explorable facility cutaway. The model is the Blender kit (tools/blender/facility.py -> facility.glb):
// geometry only, one mesh per (part, role). Colours come from the design tokens, so the theme panel recolours it.
// It follows the eight build phases (site.js sends 'ftc:phase'): the facility is drawn, then built up layer by layer —
// floor, envelope, refrigeration — pressure-tested, pulled down to temperature and handed over.
// Click a part for its card; drag (mouse) to orbit.
// Falls back to the SVG poster when WebGL is missing, the model fails to load, or the context is lost.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const stage = document.getElementById('cutaway');
if (stage && hasWebGL()) new GLTFLoader().load('/assets/models/facility.glb', g => init(g.scene), undefined, () => {});

function hasWebGL() {
  try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch (e) { return false; }
}
// Blender is Z-up; the GLB is Y-up. Shots are written in Blender metres so they match facility.py.
const b = (x, y, z) => new THREE.Vector3(x, z, -y);

// Which build phase each part of the model appears in (0 survey … 7 handover)
function phaseOf(part, role) {
  if (role === 'yard') return 0;
  if (role === 'floor' || role === 'slab' || role === 'panelfloor') return 2;
  if (!part) return role === 'steel' ? 2 : 3;                       // building frame, then cladding and roof
  if (part === 'racks' || part === 'van') return 7;
  if (['stock', 'stock2', 'pallet', 'upright', 'machine', 'tyre', 'body', 'logo', 'beam'].includes(role)) return 7;
  if (['unit', 'fan', 'tank', 'pipe', 'duct', 'fabric'].includes(role)) return 4;
  if (part === 'ahu' || part === 'plant') return role === 'block' || role === 'panel' ? 3 : 4;
  return 3;                                                          // panels, doors, curtains, dock equipment
}

function init(model) {
  const PARTS = JSON.parse(stage.dataset.parts);
  const card = stage.querySelector('.part-card');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  stage.prepend(renderer.domElement);
  renderer.domElement.setAttribute('aria-hidden', 'true');

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1.2, 1, 400);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x334455, 1.7));
  const sun = new THREE.DirectionalLight(0xffffff, 1.5); sun.position.set(30, 50, 25); scene.add(sun);
  scene.add(model);

  const meshes = [];
  model.traverse(o => {
    if (!o.isMesh) return;
    const role = o.userData.role || 'body';
    o.material = new THREE.MeshStandardMaterial({ flatShading: true, roughness: 0.85, metalness: 0.05 });
    const line = new THREE.LineSegments(new THREE.EdgesGeometry(o.geometry, 25), new THREE.LineBasicMaterial({ transparent: true }));
    o.add(line);
    meshes.push({ o, role, part: o.userData.part || null, line, phase: phaseOf(o.userData.part || null, role), g: 0 });
  });

  // One camera per build phase: [camera, look-at] in Blender metres
  const SHOTS = [
    { pos: b(52, -56, 40), at: b(8, -3, 0) },     // survey: the whole site, drawn
    { pos: b(14, -26, 58), at: b(6, 0, 0) },      // design: from above, like a plan
    { pos: b(30, -34, 16), at: b(-4, 2, 0) },     // floor & slab
    { pos: b(-6, -28, 22), at: b(-5, 5, 1) },     // envelope: cold room and freezer
    { pos: b(32, -20, 13), at: b(12.5, 7.5, 2) }, // refrigeration: plant room
    { pos: b(24, -6, 8), at: b(12.5, 7.5, 2) },   // pressure test: close on the plant
    { pos: b(-18, -26, 16), at: b(-5, 5, 2) },    // pull-down: both rooms cooling
    { pos: b(58, -50, 24), at: b(12, -6, 0) },    // handover: operating, van on site
  ];
  const OVERVIEW = SHOTS[0];
  let phase = 0;
  let active = new Set();   // parts picked by a click
  const camPos = OVERVIEW.pos.clone(), camAt = OVERVIEW.at.clone();
  const goalPos = camPos.clone(), goalAt = camAt.clone();
  let yaw = 0;

  const P = {};
  function readPalette() {
    const cs = getComputedStyle(stage);
    const c = v => new THREE.Color(cs.getPropertyValue(v).trim() || '#888');
    Object.assign(P, { acc: c('--acc'), fg: c('--fg'), bg2: c('--bg-2'), rule: c('--rule-2'), mist: c('--mist') });
  }
  const mix = (a, c, t) => a.clone().lerp(c, t);
  function roleColour(role) {
    switch (role) {
      case 'floor': case 'panelfloor': return [P.bg2];
      case 'yard': case 'slab': return [mix(P.bg2, P.rule, 0.35)];
      case 'clad': return [mix(P.bg2, P.rule, 0.3), 0.35];   // see-through walls and roof keep the inside readable
      case 'roof': return [P.rule, 0.25];
      case 'block': return [mix(P.bg2, P.rule, 0.5)];
      case 'panel': case 'door': return [mix(P.bg2, P.fg, 0.12)];
      case 'unit': case 'duct': case 'tank': case 'plate': case 'body': case 'fabric': return [mix(P.bg2, P.mist, 0.45)];
      case 'pallet': case 'stock': return [mix(P.bg2, P.mist, 0.7)];
      case 'stock2': return [mix(P.bg2, P.fg, 0.22)];
      case 'beam': return [mix(P.rule, P.mist, 0.4)];
      case 'accent': case 'logo': return [P.acc];
      case 'curtain': return [P.acc, 0.2];
      default: return [P.rule];
    }
  }
  function paint() {
    const t = performance.now() / 1000;
    for (const m of meshes) {
      const { o, role, part, line } = m;
      const [col, base = 1] = roleColour(role), on = active.has(part);
      const built = m.phase <= phase;
      // eased build progress: parts rise out of the ground and fade in
      m.g += ((built ? 1 : 0) - m.g) * (reduce ? 1 : 0.08);
      if (Math.abs(m.g - (built ? 1 : 0)) < 0.002) m.g = built ? 1 : 0;
      const op = (active.size && part && !on ? Math.min(base, 0.22) : base) * m.g;
      o.scale.y = 0.02 + 0.98 * m.g;
      o.material.color.copy(col); o.material.transparent = op < 1; o.material.opacity = op; o.material.depthWrite = op > 0.98;
      // phase effects: pressure test pulses the plant; pull-down cools the rooms
      let glow = on ? 0.16 : 0;
      if (phase === 5 && (role === 'pipe' || role === 'unit' || role === 'tank')) glow = 0.12 + 0.12 * Math.sin(t * 4);
      if (phase === 6 && (part === 'cold' || part === 'freezer') && (role === 'panel' || role === 'door' || role === 'panelfloor')) glow = 0.22 * coolT;
      o.material.emissive.copy(glow ? P.acc : BLACK).multiplyScalar(glow);
      // unbuilt parts stay as drawing lines; the design phase lights the drawing up
      line.material.color.copy(on || (!built && phase === 1) ? P.acc : P.rule);
      line.material.opacity = built ? (on ? 1 : active.size ? 0.25 : 0.55) * Math.max(m.g, 0.2) : phase <= 1 ? 0.7 : 0.14;
    }
  }
  const BLACK = new THREE.Color(0);
  let coolT = 0;
  function settled() { return meshes.every(m => m.g === 0 || m.g === 1); }
  function setPhase(i) {
    phase = i; active = new Set(); card.hidden = true; coolT = 0;
    const shot = SHOTS[i] || OVERVIEW;
    goalPos.copy(shot.pos); goalAt.copy(shot.at); yaw = 0;
    if (reduce) { camPos.copy(goalPos); camAt.copy(goalAt); }
    phaseTag.textContent = (i + 1).toString().padStart(2, '0') + ' / 08 · ' + (stepTitles[i] || '');
    dirty = true;
  }
  addEventListener('ftc:phase', e => setPhase(e.detail));

  // Picking and orbit
  const ray = new THREE.Raycaster(), ptr = new THREE.Vector2();
  const pickable = meshes.filter(m => m.part && PARTS[m.part]).map(m => m.o);
  let drag = null;
  const el = renderer.domElement;
  el.addEventListener('pointerdown', e => { if (e.pointerType === 'mouse') drag = { x: e.clientX, moved: false }; });
  addEventListener('pointerup', () => { setTimeout(() => { drag = null; }); });
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
    const hit = ray.intersectObjects(pickable, false)[0];
    if (!hit) { card.hidden = true; return; }
    const key = hit.object.userData.part, info = PARTS[key];
    active = new Set([key]); dirty = true;
    card.innerHTML = '';
    const t = document.createElement('strong'); t.textContent = info.t;
    card.append(t, document.createTextNode(info.s)); card.hidden = false;
  });

  // Size, visibility, context loss
  let visible = false, dirty = true, raf = 0;
  function resize() {
    const { width, height } = stage.getBoundingClientRect();
    renderer.setSize(width, height, false); camera.aspect = width / height; camera.updateProjectionMatrix(); dirty = true;
  }
  new ResizeObserver(resize).observe(stage);
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; if (visible && !raf) raf = requestAnimationFrame(loop); }).observe(stage);
  el.addEventListener('webglcontextlost', e => {
    e.preventDefault(); stage.classList.remove('live'); el.remove();
    card.textContent = stage.dataset.fallback; card.hidden = false;
  });
  addEventListener('ftc:design', () => { readPalette(); dirty = true; });

  const tmp = new THREE.Vector3();
  function loop() {
    raf = 0;
    if (!visible) return;
    const k = reduce ? 1 : 0.06;
    camPos.lerp(goalPos, k); camAt.lerp(goalAt, k);
    tmp.copy(camPos).sub(camAt).applyAxisAngle(THREE.Object3D.DEFAULT_UP, yaw).add(camAt);
    camera.position.copy(tmp); camera.lookAt(camAt);
    if (phase === 6 && coolT < 1) coolT = Math.min(1, coolT + (reduce ? 1 : 0.004));
    const animating = !settled() || phase === 5 || (phase === 6 && coolT < 1);
    if (camPos.distanceToSquared(goalPos) > 1e-4 || dirty || animating) { paint(); renderer.render(scene, camera); dirty = false; }
    raf = requestAnimationFrame(loop);
  }

  const phaseTag = stage.querySelector('.stage-phase');
  const stepTitles = [...document.querySelectorAll('#steps .step .t')].map(e => e.textContent);
  readPalette(); resize(); setPhase(window.ftcPhase || 0);
  stage.classList.add('live');
}
