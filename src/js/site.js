// Shared behaviour for v1 and v2: mobile menu, design-options panel, quote form.
(function () {
  var root = document.documentElement;
  var KEYS = ['theme', 'accent', 'type', 'shape'];
  var DEFAULTS = { theme: 'ink', accent: 'cyan', type: 'expanded', shape: 'soft' };

  // v2 hero footage: skip it when the visitor asks for less motion or less data
  var vid = document.querySelector('[data-hero-video]');
  var saveData = navigator.connection && navigator.connection.saveData;
  if (vid && (matchMedia('(prefers-reduced-motion: reduce)').matches || saveData)) vid.remove();

  // Section footage (brochure band): loads only when near the viewport, pauses off screen, never with reduced motion or data saver
  [].forEach.call(document.querySelectorAll('[data-lazy-video]'), function (v) {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches || saveData || !('IntersectionObserver' in window)) { v.remove(); return; }
    new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          var s = v.querySelector('source[data-src]');
          if (s) { s.src = s.getAttribute('data-src'); s.removeAttribute('data-src'); v.load(); }
          v.play().catch(function () {});
        } else v.pause();
      });
    }, { rootMargin: '200px 0px' }).observe(v);
  });

  // Mobile menu
  var menuBtn = document.querySelector('.menu-btn'), nav = document.getElementById('nav');
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', String(open));
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) { nav.classList.remove('open'); menuBtn.setAttribute('aria-expanded', 'false'); }
    });
  }

  // Design options: attributes on <html>, remembered per browser, shareable by URL
  var panel = document.getElementById('dz'), opener = document.querySelector('.dz-open');
  function current() {
    var o = {};
    KEYS.forEach(function (k) { o[k] = root.getAttribute('data-' + k) || DEFAULTS[k]; });
    return o;
  }
  function save(o) { try { localStorage.setItem('ftc-design', JSON.stringify(o)); } catch (e) {} }
  function sync() {
    var o = current();
    KEYS.forEach(function (k) {
      var r = panel && panel.querySelector('input[name="' + k + '"][value="' + o[k] + '"]');
      if (r) r.checked = true;
    });
    window.dispatchEvent(new CustomEvent('ftc:design', { detail: o }));
  }
  if (panel && opener) {
    function show(open) {
      panel.hidden = !open; opener.hidden = open;
      opener.setAttribute('aria-expanded', String(open));
      if (open) panel.querySelector('input:checked, input').focus(); else opener.focus();
    }
    opener.addEventListener('click', function () { show(true); });
    panel.querySelector('.x').addEventListener('click', function () { show(false); });
    panel.addEventListener('keydown', function (e) { if (e.key === 'Escape') show(false); });
    panel.addEventListener('change', function (e) {
      if (!e.target.name) return;
      root.setAttribute('data-' + e.target.name, e.target.value);
      save(current()); sync();
    });
    panel.querySelector('[data-reset]').addEventListener('click', function () {
      KEYS.forEach(function (k) { root.setAttribute('data-' + k, DEFAULTS[k]); });
      save(DEFAULTS); sync();
    });
    var copyBtn = panel.querySelector('[data-copy]');
    copyBtn.addEventListener('click', function () {
      var u = new URL(location.href), o = current();
      KEYS.forEach(function (k) { u.searchParams.set(k, o[k]); });
      var label = copyBtn.textContent;
      function done() { copyBtn.textContent = copyBtn.getAttribute('data-done'); setTimeout(function () { copyBtn.textContent = label; }, 1800); }
      if (navigator.clipboard) navigator.clipboard.writeText(u.toString()).then(done, function () { prompt('', u.toString()); });
      else prompt('', u.toString());
    });
    sync();
  }

  // Quote, contact and job forms: no backend yet, so each composes an email to FTC with the answers
  [].forEach.call(document.querySelectorAll('form[data-subject]'), function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var lines = [];
      form.querySelectorAll('label').forEach(function (l) {
        var f = l.querySelector('input, select, textarea');
        if (f && f.value) lines.push(l.firstChild.textContent.trim() + ': ' + f.value);
      });
      location.href = 'mailto:info@ftc-qatar.com?subject=' + encodeURIComponent(form.getAttribute('data-subject')) +
        '&body=' + encodeURIComponent(lines.join('\n'));
    });
  });

  // Projects index: sector filter
  [].forEach.call(document.querySelectorAll('.pfilter'), function (bar) {
    bar.addEventListener('click', function (e) {
      var b = e.target.closest('[data-f]'); if (!b) return;
      var f = b.getAttribute('data-f');
      [].forEach.call(bar.children, function (c) { c.classList.toggle('on', c === b); });
      [].forEach.call(document.querySelectorAll('.pf'), function (p) { p.hidden = f !== '*' && p.getAttribute('data-s') !== f; });
    });
  });

  // Virtual office: the invite code goes into FTC's OfficeVerse join link, opened in a new tab so this site stays open
  [].forEach.call(document.querySelectorAll('form[data-ov]'), function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!f.reportValidity()) return;
      var code = f.querySelector('input').value.trim().toUpperCase();
      window.open(f.getAttribute('data-ov').replace('{code}', encodeURIComponent(code)), '_blank', 'noopener');
    });
  });

  // Service cards open their full write-up in a native dialog (Esc, the × button or a backdrop click closes it)
  [].forEach.call(document.querySelectorAll('[data-dlg]'), function (b) {
    var d = document.getElementById(b.getAttribute('data-dlg'));
    if (!d || !d.showModal) return;
    b.addEventListener('click', function () { d.showModal(); });
    d.addEventListener('click', function (e) {
      var r = d.getBoundingClientRect(), out = e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
      if (out || e.target.closest('[data-close]')) d.close();
    });
    d.addEventListener('close', function () { b.focus(); });
  });

  // Interactive history: tabs on a rail, arrow keys, swipe, and an autoplay that stops for good once the visitor takes over
  [].forEach.call(document.querySelectorAll('[data-hx-root]'), function (root) {
    var tabs = [].slice.call(root.querySelectorAll('.hx-tab')), panels = [].slice.call(root.querySelectorAll('.hx-p'));
    var rail = root.querySelector('.hx-rail'), fill = root.querySelector('.hx-fill'), playBtn = root.querySelector('[data-hx="play"]');
    var rtl = document.documentElement.dir === 'rtl', reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    var cur = 0, timer = 0, playing = !reduce, inView = false, DUR = 7000;
    root.classList.add('js');
    function go(i, focus) {
      cur = (i + tabs.length) % tabs.length;
      tabs.forEach(function (b, k) {
        b.setAttribute('aria-selected', String(k === cur)); b.tabIndex = k === cur ? 0 : -1; b.classList.toggle('past', k < cur);
      });
      panels.forEach(function (p, k) { p.classList.toggle('cur', k === cur); });
      // fill runs from the first dot to the centre of the active one (dots sit 12px in from the tab's inline start)
      var tb = tabs[cur], track = tb.parentNode, first = tabs[0];
      var at = rtl ? track.offsetWidth - tb.offsetLeft - tb.offsetWidth : tb.offsetLeft;
      var start = rtl ? track.offsetWidth - first.offsetLeft - first.offsetWidth : first.offsetLeft;
      fill.style.width = (at - start) + 'px';
      var left = tb.offsetLeft - (rail.clientWidth - tb.offsetWidth) / 2;
      rail.scrollTo({ left: left, behavior: reduce ? 'auto' : 'smooth' });
      if (focus) tb.focus({ preventScroll: true });
      schedule();
    }
    function schedule() {
      clearTimeout(timer);
      root.classList.remove('playing'); void root.offsetWidth;
      if (playing && inView) { root.classList.add('playing'); timer = setTimeout(function () { go(cur + 1); }, DUR); }
    }
    function stop() { playing = false; schedule(); if (playBtn) playBtn.textContent = playBtn.getAttribute('data-play'); }
    tabs.forEach(function (b, k) { b.addEventListener('click', function () { stop(); go(k); }); });
    rail.addEventListener('keydown', function (e) {
      var k = e.key, f = rtl ? -1 : 1, n = null;
      if (k === 'ArrowRight') n = cur + f; else if (k === 'ArrowLeft') n = cur - f; else if (k === 'Home') n = 0; else if (k === 'End') n = tabs.length - 1;
      if (n === null) return;
      e.preventDefault(); stop(); go(Math.max(0, Math.min(tabs.length - 1, n)), true);
    });
    root.addEventListener('click', function (e) {
      var b = e.target.closest('[data-hx]'); if (!b) return;
      var a = b.getAttribute('data-hx');
      if (a === 'play') { if (playing) stop(); else { playing = true; b.textContent = b.getAttribute('data-pause'); go(cur + 1); } return; }
      stop(); go(cur + (a === 'next' ? 1 : -1));
    });
    // swipe on the story
    var sx = null, stage = root.querySelector('.hx-stage');
    stage.addEventListener('pointerdown', function (e) { sx = e.clientX; });
    stage.addEventListener('pointerup', function (e) {
      if (sx === null) return; var dx = e.clientX - sx; sx = null;
      if (Math.abs(dx) > 50) { stop(); go(cur + ((dx < 0) !== rtl ? 1 : -1)); }
    });
    root.addEventListener('mouseenter', function () { clearTimeout(timer); root.classList.remove('playing'); });
    root.addEventListener('mouseleave', schedule);
    if (reduce && playBtn) playBtn.hidden = true;
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { inView = es[0].isIntersecting; schedule(); }, { threshold: 0.4 }).observe(root);
    addEventListener('resize', function () { go(cur); });
    go(0);
  });
})();
