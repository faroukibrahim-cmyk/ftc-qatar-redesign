// v2 — optional sound design, all synthesised with Web Audio (no audio files). Off until the visitor turns it on;
// the choice is remembered. A low plant-room hum sits under the hero footage, the fly-through and the 3D model;
// the fly-through adds airflow that follows scroll speed; each build phase in the model has a short cue.
const btn = document.querySelector('[data-sound]');
if (btn && window.AudioContext) init();

function init() {
  let ctx = null, master, bed, air, airGain, on = false;
  const label = btn.querySelector('.snd-l');
  const KEY = 'ftc-sound';

  function noise(seconds, brown) {
    const n = ctx.sampleRate * seconds, buf = ctx.createBuffer(1, n, ctx.sampleRate), d = buf.getChannelData(0);
    let last = 0;
    for (let i = 0; i < n; i++) {
      const w = Math.random() * 2 - 1;
      d[i] = brown ? (last = (last + 0.02 * w) / 1.02) * 3.5 : w;
    }
    return buf;
  }
  function src(buf, loop) { const s = ctx.createBufferSource(); s.buffer = buf; s.loop = loop; return s; }
  function env(g, t, peak, attack, decay) {
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(peak, t + attack); g.gain.exponentialRampToValueAtTime(0.0001, t + attack + decay);
  }

  function build() {
    ctx = new AudioContext();
    master = ctx.createGain(); master.gain.value = 0;
    const comp = ctx.createDynamicsCompressor(); master.connect(comp); comp.connect(ctx.destination);
    // plant-room bed: brown noise through a low-pass, plus a 50 Hz mains hum with a slow compressor throb
    bed = ctx.createGain(); bed.gain.value = 0; bed.connect(master);
    const rumble = src(noise(4, true), true), lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 300;
    const rg = ctx.createGain(); rg.gain.value = 0.55; rumble.connect(lp); lp.connect(rg); rg.connect(bed); rumble.start();
    const hum = ctx.createGain(); hum.gain.value = 0.05; hum.connect(bed);
    [50, 100, 150].forEach((f, k) => { const o = ctx.createOscillator(); o.frequency.value = f; const g = ctx.createGain(); g.gain.value = [1, 0.5, 0.2][k]; o.connect(g); g.connect(hum); o.start(); });
    const lfo = ctx.createOscillator(), lg = ctx.createGain(); lfo.frequency.value = 0.35; lg.gain.value = 0.02; lfo.connect(lg); lg.connect(hum.gain); lfo.start();
    // airflow for the fly-through: band-passed white noise, level driven by scroll speed
    air = src(noise(3, false), true); const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 700; bp.Q.value = 0.7;
    airGain = ctx.createGain(); airGain.gain.value = 0; air.connect(bp); bp.connect(airGain); airGain.connect(master); air.start();
  }

  // Where we are on the page decides the bed level
  const zones = [['.hero', 0.35], ['#film', 0.5], ['#journey', 0.4]].map(([s, lv]) => ({ el: document.querySelector(s), lv, vis: false })).filter(z => z.el);
  const io = new IntersectionObserver(es => es.forEach(e => { const z = zones.find(z => z.el === e.target); if (z) z.vis = e.isIntersecting; }), { threshold: 0.25 });
  zones.forEach(z => io.observe(z.el));
  let lastY = scrollY, speed = 0;
  function tick() {
    if (!on) return;
    const t = ctx.currentTime, target = Math.max(0, ...zones.filter(z => z.vis).map(z => z.lv));
    bed.gain.setTargetAtTime(target, t, 0.6);
    const film = zones.find(z => z.el.id === 'film');
    speed = speed * 0.9 + Math.abs(scrollY - lastY) * 0.1; lastY = scrollY;
    airGain.gain.setTargetAtTime(film && film.vis ? Math.min(0.5, speed / 60) : 0, t, 0.15);
    requestAnimationFrame(tick);
  }

  // One short cue per build phase (see site.js 'ftc:phase')
  const CUES = [
    () => blip(1180, 0.05, 0.08),                                    // survey: a marker tick
    () => { blip(880, 0.05, 0.06); blip(1320, 0.05, 0.06, 0.09); },   // design: two-note
    () => thud(55, 0.7, 0.5),                                          // floor & slab: concrete
    () => { thud(150, 0.25, 0.35); thud(130, 0.25, 0.3, 0.18); },     // envelope: cam-locks closing
    () => sweep(300, 1100, 1.6, 0.22),                                 // refrigeration: fans spinning up
    () => hiss(1.8, 0.18),                                             // pressure test: nitrogen
    () => motor(1.8, 0.3),                                             // pull-down: compressor start
    () => { blip(523, 0.5, 0.09); blip(784, 0.6, 0.08, 0.14); },      // handover: a soft chime
  ];
  function out(level, delay = 0) { const g = ctx.createGain(); g.connect(master); return [g, ctx.currentTime + delay]; }
  function blip(f, dur, lv, delay) { const [g, t] = out(lv, delay); const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.value = f; o.connect(g); env(g, t, lv, 0.008, dur); o.start(t); o.stop(t + dur + 0.05); }
  function thud(f, dur, lv, delay) {
    const [g, t] = out(lv, delay); const o = ctx.createOscillator(); o.frequency.setValueAtTime(f * 1.6, t); o.frequency.exponentialRampToValueAtTime(f, t + 0.08);
    o.connect(g); env(g, t, lv, 0.005, dur); o.start(t); o.stop(t + dur + 0.05);
    const n = src(noise(0.2, false), false), lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 900; const ng = ctx.createGain();
    n.connect(lp); lp.connect(ng); ng.connect(master); env(ng, t, lv * 0.5, 0.002, 0.08); n.start(t);
  }
  function sweep(a, b, dur, lv) {
    const [g, t] = out(lv); const n = src(noise(dur + 0.2, false), false), f = ctx.createBiquadFilter(); f.type = 'bandpass'; f.Q.value = 1.4;
    f.frequency.setValueAtTime(a, t); f.frequency.exponentialRampToValueAtTime(b, t + dur); n.connect(f); f.connect(g); env(g, t, lv, dur * 0.6, dur * 0.4); n.start(t);
  }
  function hiss(dur, lv) {
    const [g, t] = out(lv); const n = src(noise(dur + 0.2, false), false), f = ctx.createBiquadFilter(); f.type = 'highpass'; f.frequency.value = 3200;
    n.connect(f); f.connect(g); env(g, t, lv, 0.05, dur); n.start(t);
  }
  function motor(dur, lv) {
    const [g, t] = out(lv); const o = ctx.createOscillator(), f = ctx.createBiquadFilter(); o.type = 'sawtooth'; f.type = 'lowpass'; f.frequency.value = 220;
    o.frequency.setValueAtTime(18, t); o.frequency.exponentialRampToValueAtTime(50, t + dur * 0.7);
    o.connect(f); f.connect(g); g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(lv, t + dur * 0.6); g.gain.exponentialRampToValueAtTime(0.0001, t + dur * 1.6);
    o.start(t); o.stop(t + dur * 1.7);
  }
  addEventListener('ftc:phase', e => { if (on && zones.some(z => z.el.id === 'journey' && z.vis)) CUES[e.detail] && CUES[e.detail](); });

  function set(v) {
    on = v;
    btn.setAttribute('aria-pressed', String(on));
    label.textContent = btn.getAttribute(on ? 'data-off' : 'data-on');
    try { localStorage.setItem(KEY, on ? '1' : '0'); } catch (e) {}
    if (on) {
      if (!ctx) build();
      ctx.resume(); master.gain.setTargetAtTime(0.9, ctx.currentTime, 0.4); requestAnimationFrame(tick);
    } else if (ctx) master.gain.setTargetAtTime(0, ctx.currentTime, 0.2);
  }
  btn.addEventListener('click', () => set(!on));
  document.addEventListener('visibilitychange', () => { if (ctx) document.hidden ? ctx.suspend() : on && ctx.resume(); });
  // A remembered "on" still needs a gesture before audio may start, so it waits for the first interaction
  let saved = false; try { saved = localStorage.getItem(KEY) === '1'; } catch (e) {}
  if (saved) {
    btn.setAttribute('aria-pressed', 'false');
    const go = e => {
      removeEventListener('pointerdown', go); removeEventListener('keydown', go);
      if (!(e.target.closest && e.target.closest('[data-sound]'))) set(true);   // a click on the button itself toggles it anyway
    };
    addEventListener('pointerdown', go); addEventListener('keydown', go);
  }
}
