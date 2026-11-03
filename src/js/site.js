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
})();
