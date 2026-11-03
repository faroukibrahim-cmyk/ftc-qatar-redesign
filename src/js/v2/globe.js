// v2 — dot-matrix globe for the Farjallah group. Office data comes from the HTML list (#offices li[data-lat]);
// the canvas only draws. Auto-rotates, pauses off screen, mouse-drag rotates, hover a pin (or list row) for its card.
import * as THREE from 'three';

const host = document.getElementById('globe');
const rows = [...document.querySelectorAll('#offices li[data-lat]')];
if (host && rows.length && hasWebGL()) init();

function hasWebGL() {
  try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch (e) { return false; }
}
function xyz(lat, lon, r = 1) {
  const phi = (90 - lat) * Math.PI / 180, th = (lon + 180) * Math.PI / 180;
  return new THREE.Vector3(-r * Math.sin(phi) * Math.cos(th), r * Math.cos(phi), r * Math.sin(phi) * Math.sin(th));
}

async function init() {
  const dots = await fetch('/assets/data/land-dots.json').then(r => r.json()).catch(() => null);
  if (!dots) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const card = host.querySelector('.pin-card');
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  host.prepend(renderer.domElement);
  renderer.domElement.setAttribute('aria-hidden', 'true');

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 20);
  camera.position.set(0, 0.35, 3.6); camera.lookAt(0, 0, 0);
  const world = new THREE.Group(); scene.add(world);

  const occluder = new THREE.Mesh(new THREE.SphereGeometry(0.985, 64, 48), new THREE.MeshBasicMaterial());
  world.add(occluder);
  const pos = new Float32Array(dots.length / 2 * 3);
  for (let i = 0; i < dots.length; i += 2) xyz(dots[i], dots[i + 1]).toArray(pos, i / 2 * 3);
  const landGeo = new THREE.BufferGeometry(); landGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const landMat = new THREE.PointsMaterial({ size: 0.022, sizeAttenuation: true });
  world.add(new THREE.Points(landGeo, landMat));

  const offices = rows.map(li => ({ li, lat: +li.dataset.lat, lon: +li.dataset.lon, hq: li.dataset.kind === 'hq',
    city: li.dataset.city, name: li.querySelector('span').textContent, co: li.querySelector('.m').textContent }));
  const hq = offices.find(o => o.hq) || offices[0];
  const pinMat = new THREE.MeshBasicMaterial(), hqMat = new THREE.MeshBasicMaterial(), arcMat = new THREE.LineBasicMaterial({ transparent: true, opacity: 0.9 });
  const pulseMat = new THREE.MeshBasicMaterial();
  const curves = [], pulses = [];
  offices.forEach(o => {
    o.v = xyz(o.lat, o.lon, 1.005);
    const pin = new THREE.Mesh(new THREE.SphereGeometry(o.hq ? 0.022 : 0.014, 16, 12), o.hq ? hqMat : pinMat);
    pin.position.copy(o.v); world.add(pin); o.pin = pin;
    if (o === hq) {
      const ring = new THREE.Mesh(new THREE.RingGeometry(0.04, 0.048, 40), new THREE.MeshBasicMaterial({ transparent: true, side: THREE.DoubleSide }));
      ring.position.copy(o.v); ring.lookAt(o.v.clone().multiplyScalar(2)); world.add(ring); o.ring = ring;
      return;
    }
    const mid = hq.v.clone().add(o.v).multiplyScalar(0.5);
    mid.setLength(1 + hq.v.distanceTo(o.v) * 0.45);
    const curve = new THREE.QuadraticBezierCurve3(hq.v, mid, o.v);
    world.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(curve.getPoints(48)), arcMat));
    curves.push(curve);
    [0, 0.5].forEach(off => { const p = new THREE.Mesh(new THREE.SphereGeometry(0.008, 8, 6), pulseMat); world.add(p); pulses.push({ p, curve, off }); });
  });

  function paint() {
    const cs = getComputedStyle(host), c = v => new THREE.Color(cs.getPropertyValue(v).trim() || '#888');
    occluder.material.color.copy(c('--bg-2')); landMat.color.copy(c('--mist'));
    pinMat.color.copy(c('--acc')); arcMat.color.copy(c('--acc')); pulseMat.color.copy(c('--fg')); hqMat.color.copy(c('--fg'));
    if (hq.ring) hq.ring.material.color.copy(c('--fg'));
  }
  addEventListener('ftc:design', paint);

  // Start facing the Gulf / Mediterranean
  // Yaw that turns the HQ to face the camera (+z), nudged east so Europe and Africa stay in view
  let rotY = Math.atan2(-hq.v.x, hq.v.z) + 0.45, rotX = 0.32, drag = null, hoverRow = null;
  host.addEventListener('pointerdown', e => { if (e.pointerType === 'mouse') drag = { x: e.clientX, y: e.clientY }; });
  addEventListener('pointerup', () => { drag = null; });
  host.addEventListener('pointermove', e => {
    if (drag) { rotY += (e.clientX - drag.x) * 0.006; rotX = Math.max(-0.6, Math.min(0.9, rotX + (e.clientY - drag.y) * 0.004)); drag.x = e.clientX; drag.y = e.clientY; }
    pick(e.clientX, e.clientY);
  });
  host.addEventListener('pointerleave', () => { card.hidden = true; });
  host.addEventListener('click', e => pick(e.clientX, e.clientY));
  rows.forEach((o, i) => { o.addEventListener('mouseenter', () => { hoverRow = offices[i]; }); o.addEventListener('mouseleave', () => { hoverRow = null; card.hidden = true; }); });

  const tmp = new THREE.Vector3(), camDir = new THREE.Vector3();
  function screen(o) {
    o.pin.getWorldPosition(tmp);
    camDir.copy(camera.position).sub(tmp);
    const front = tmp.dot(camDir) > 0;
    tmp.project(camera);
    const r = host.getBoundingClientRect();
    return { x: (tmp.x + 1) / 2 * r.width, y: (1 - tmp.y) / 2 * r.height, front };
  }
  function show(o, s) {
    card.textContent = `${o.city} · ${o.name} — ${o.co}`;
    card.style.left = s.x + 'px'; card.style.top = s.y + 'px'; card.hidden = false;
  }
  function pick(cx, cy) {
    const r = host.getBoundingClientRect(); let best = null, bd = 18 * 18;
    for (const o of offices) { const s = screen(o); const d = (s.x - (cx - r.left)) ** 2 + (s.y - (cy - r.top)) ** 2; if (s.front && d < bd) { bd = d; best = [o, s]; } }
    if (best) show(...best); else if (!hoverRow) card.hidden = true;
  }

  function resize() { const { width } = host.getBoundingClientRect(); renderer.setSize(width, width, false); }
  new ResizeObserver(resize).observe(host);
  let visible = false, raf = 0;
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; if (visible && !raf) raf = requestAnimationFrame(loop); }).observe(host);
  renderer.domElement.addEventListener('webglcontextlost', e => { e.preventDefault(); host.classList.remove('live'); renderer.domElement.remove(); });

  const t0 = performance.now();
  function loop(now) {
    raf = 0;
    if (!visible) return;
    if (!drag && !reduce) rotY += 0.0012;
    world.rotation.set(rotX, rotY, 0);
    const t = ((now - t0) / 2600) % 1;
    pulses.forEach(({ p, curve, off }) => { const u = (t + off) % 1; curve.getPoint(u < 0.5 ? u * 2 : 2 - u * 2, p.position); });
    if (hq.ring) hq.ring.scale.setScalar(1 + ((now - t0) / 1400 % 1) * 0.8);
    if (hoverRow) { const s = screen(hoverRow); if (s.front) show(hoverRow, s); else card.hidden = true; }
    renderer.render(scene, camera);
    raf = requestAnimationFrame(loop);
  }

  paint(); resize(); host.classList.add('live');
}
