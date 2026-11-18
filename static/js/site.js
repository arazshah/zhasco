(function () {
  var burger = document.querySelector('.burger');
  var nav = document.getElementById('nav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  var header = document.querySelector('.site-header');
  function onScroll() { header && header.classList.toggle('scrolled', window.scrollY > 8); }
  onScroll(); window.addEventListener('scroll', onScroll, { passive: true });

  // count-up for hero stats
  var FA = '۰۱۲۳۴۵۶۷۸۹';
  function fa(n) { return String(n).replace(/\d/g, function (d) { return FA[d]; }); }
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('[data-count]').forEach(function (el) {
    var end = parseInt(el.getAttribute('data-count'), 10);
    if (isNaN(end) || reduce) return;
    var t0 = null;
    function step(t) {
      if (!t0) t0 = t;
      var p = Math.min((t - t0) / 900, 1);
      var v = Math.round(end * (1 - Math.pow(1 - p, 3)));
      el.textContent = end >= 1000 ? v.toLocaleString('fa-IR') : fa(v);
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  });

  // image lightbox (certificates, galleries)
  document.querySelectorAll('[data-lightbox]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var o = document.createElement('div');
      o.className = 'lightbox';
      o.innerHTML = '<img alt=""><button aria-label="بستن">×</button>';
      o.querySelector('img').src = a.href;
      o.querySelector('img').alt = a.getAttribute('data-alt') || '';
      function close() { o.remove(); document.removeEventListener('keydown', key); }
      function key(ev) { if (ev.key === 'Escape') close(); }
      o.addEventListener('click', close); document.addEventListener('keydown', key);
      document.body.appendChild(o);
    });
  });
})();
