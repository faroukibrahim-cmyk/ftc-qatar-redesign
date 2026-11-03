// Motion layer, shared by v1 and v2. Only runs when the boot script set html.mo (no reduced-motion preference);
// without it every element is simply visible. Kept to restrained moves: fade-and-rise reveals with a stagger,
// a word-by-word headline, count-up figures, a landmarks marquee, and a header that steps aside on scroll.
(function () {
  var root = document.documentElement;
  if (!root.classList.contains('mo')) return;
  window.ftcMotion = true;

  // Everything that rises into view. Siblings in the same parent are staggered.
  var SEL = ['section .eyebrow', 'section h2.d', 'section .lead', '.hero .btns', '.temps > span', '.stat', '.cell', '.card',
    '.chip', '.proj', '.cols4 > div', '.timeline > li', '.offices > li', '.rfq', '.fig', '.steps > li', '.brands-wall > span',
    '.specs', '.tbl-box', 'details', '.crumb', '.globe', '.film-steps > li', '.ftr-grid > div', '.band .btns'].join(',');
  var els = [].slice.call(document.querySelectorAll(SEL)).filter(function (el) {
    return !el.closest('.film') && !el.closest('.dz');
  });
  var set = new Set(els);
  els.forEach(function (el) {
    var i = 0, c = el.previousElementSibling;
    while (c) { if (set.has(c)) i++; c = c.previousElementSibling; }
    el.style.setProperty('--dl', Math.min(i, 8) * 0.07 + 's');
    el.classList.add('rv');
  });

  // Headlines (h1) come in word by word
  [].forEach.call(document.querySelectorAll('h1.d'), function (h) {
    var words = h.textContent.trim().split(/\s+/);
    h.textContent = '';
    words.forEach(function (w, i) {
      var o = document.createElement('span'), n = document.createElement('span');
      o.className = 'w'; n.textContent = w; n.style.setProperty('--dl', 0.15 + i * 0.08 + 's');
      o.appendChild(n); h.appendChild(o);
      if (i < words.length - 1) h.appendChild(document.createTextNode(' '));
    });
    h.classList.add('words');
    els.push(h);
  });

  // Count-up figures (1946 counts from 1900; "5K+" keeps its suffix)
  function countUp(el) {
    var m = el.textContent.trim().match(/^(\d+)(.*)$/);
    if (!m) return;
    var to = +m[1], from = to > 1000 ? to - 46 : 0, t0 = performance.now(), dur = 1400;
    (function tick(now) {
      var p = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(from + (to - from) * e) + m[2];
      if (p < 1) requestAnimationFrame(tick);
    })(t0);
  }

  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      var el = e.target;
      el.classList.add('in'); io.unobserve(el);
      if (el.classList.contains('stat')) { var n = el.querySelector('.n'); if (n) countUp(n); }
      // once revealed, drop the stagger so hover moves respond at once
      setTimeout(function () { el.style.removeProperty('--dl'); el.classList.add('done'); }, 1600);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  els.forEach(function (el) { io.observe(el); });

  // Landmarks: a slow marquee (label stays put, names scroll; pauses on hover)
  var marks = document.querySelector('.marks');
  if (marks && marks.children.length > 2) {
    var label = marks.firstElementChild, track = document.createElement('div'), run = document.createElement('div');
    track.className = 'mq'; run.className = 'mq-run';
    [].slice.call(marks.children, 1).forEach(function (s) { run.appendChild(s); });
    var copy = run.cloneNode(true); copy.setAttribute('aria-hidden', 'true');
    track.appendChild(run); track.appendChild(copy);
    marks.appendChild(track); marks.classList.add('marquee');
    label.classList.add('mq-label');
  }

  // Header: solid on scroll, steps aside going down, returns going up; a thin progress line underneath
  var hdr = document.querySelector('.hdr'), nav = document.getElementById('nav'), last = scrollY, ticking = false;
  function onScroll() {
    ticking = false;
    var y = scrollY, max = document.documentElement.scrollHeight - innerHeight;
    if (hdr) {
      hdr.classList.toggle('scrolled', y > 8);
      var open = nav && nav.classList.contains('open');
      hdr.classList.toggle('away', !open && y > 400 && y > last + 4);
      if (y < last - 4) hdr.classList.remove('away');
      hdr.style.setProperty('--sp', max > 0 ? (y / max).toFixed(4) : 0);
    }
    last = y;
  }
  addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();
})();
