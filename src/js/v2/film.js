// v2 — scroll-scrubbed fly-through. Frames are Blender renders (tools/blender/facility.py), drawn to a canvas;
// scroll only moves time. Captions are the real journey copy in the page. Without JS, or with reduced motion,
// the section stays a static list of five key frames.
const sec = document.getElementById('film');
if (sec && !matchMedia('(prefers-reduced-motion: reduce)').matches) init();

function init() {
  const N = +sec.dataset.frames, cuts = JSON.parse(sec.dataset.cuts);
  const small = innerWidth < 760 || (navigator.connection && navigator.connection.saveData);
  const src = i => `/assets/film/${small ? 'm' : 'd'}/f${String(i + 1).padStart(3, '0')}.webp`;
  const canvas = sec.querySelector('canvas'), ctx = canvas.getContext('2d');
  const items = [...sec.querySelectorAll('.film-steps li')];
  const rail = sec.querySelector('.film-rail span');
  const imgs = new Array(N);
  sec.classList.add('scrub');

  // Coarse-to-fine load order (every 8th frame first) so scrubbing works before everything has arrived
  const order = [], seen = new Set();
  for (const s of [8, 4, 2, 1]) for (let i = 0; i < N; i += s) if (!seen.has(i)) { seen.add(i); order.push(i); }
  let started = false;
  function load() {
    if (started) return; started = true;
    let next = 0;
    const pump = () => {
      if (next >= order.length) return;
      const i = order[next++], im = new Image();
      im.decoding = 'async';
      im.onload = () => { imgs[i] = im; if (Math.abs(i - cur) < 6) dirty = true; pump(); };
      im.onerror = pump;
      im.src = src(i);
    };
    for (let k = 0; k < 6; k++) pump();
  }

  function nearest(i) {
    for (let d = 0; d < N; d++) { if (imgs[i - d]) return imgs[i - d]; if (imgs[i + d]) return imgs[i + d]; }
    return null;
  }
  function draw(i) {
    const im = nearest(i);
    if (!im) return;
    const cw = canvas.width, ch = canvas.height, s = Math.max(cw / im.width, ch / im.height);
    const w = im.width * s, h = im.height * s;
    ctx.drawImage(im, (cw - w) / 2, (ch - h) / 2, w, h);
  }
  function resize() {
    const r = Math.min(devicePixelRatio || 1, 1.5);
    canvas.width = canvas.clientWidth * r; canvas.height = canvas.clientHeight * r; dirty = true;
  }
  new ResizeObserver(resize).observe(canvas);

  let cur = 0, goal = 0, step = -1, dirty = true, visible = false, raf = 0;
  function progress() {
    const r = sec.getBoundingClientRect();
    return Math.min(1, Math.max(0, -r.top / (r.height - innerHeight)));
  }
  function frame() {
    raf = 0;
    if (!visible) return;
    const p = progress();
    goal = p * (N - 1);
    cur += (goal - cur) * 0.18;
    if (Math.abs(goal - cur) < 0.05) cur = goal;
    const i = Math.round(cur);
    if (i !== frame.last || dirty) { draw(i); frame.last = i; dirty = false; }
    let s = 0; cuts.forEach((c, k) => { if (p >= c) s = k; });
    if (s !== step) { items.forEach((li, k) => li.classList.toggle('on', k === s)); step = s; }
    rail.style.inlineSize = (p * 100).toFixed(2) + '%';
    raf = requestAnimationFrame(frame);
  }
  new IntersectionObserver(([e]) => {
    visible = e.isIntersecting;
    if (visible) { load(); if (!raf) raf = requestAnimationFrame(frame); }
  }, { rootMargin: '100% 0px' }).observe(sec);
}
