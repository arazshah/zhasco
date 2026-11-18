(function () {
  var svg = document.querySelector('[data-map]');
  if (!svg) return;
  var tip = document.querySelector('[data-tip]');
  var panel = document.querySelector('[data-panel]');
  var intro = document.querySelector('[data-intro]');
  var FA = '۰۱۲۳۴۵۶۷۸۹';
  function fa(n) { return String(n).replace(/\d/g, function (d) { return FA[d]; }); }
  var cache = {};
  var current = null;

  function esc(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

  function showTip(el, ev) {
    var r = svg.parentElement.getBoundingClientRect();
    tip.hidden = false;
    tip.innerHTML = '<strong>' + esc(el.dataset.name) + '</strong><span>' + fa(el.dataset.n) + ' پروژه</span>';
    tip.style.left = (ev.clientX - r.left) + 'px';
    tip.style.top = (ev.clientY - r.top - 14) + 'px';
  }

  function select(slug) {
    document.querySelectorAll('.prov.is-selected').forEach(function (n) { n.classList.remove('is-selected'); });
    document.querySelectorAll('.chip.on').forEach(function (n) { n.classList.remove('on'); });
    var el = svg.querySelector('[data-slug="' + slug + '"]');
    if (!el) return;
    el.classList.add('is-selected');
    svg.querySelector('.provinces').appendChild(el); // bring to front
    var chip = document.querySelector('[data-chip="' + slug + '"]');
    if (chip) chip.classList.add('on');
    current = slug;
    panel.hidden = false; intro.hidden = true;
    panel.classList.add('loading');
    panel.querySelector('[data-p-name]').textContent = el.dataset.name;
    panel.querySelector('[data-p-sum]').textContent = '';
    panel.querySelector('[data-p-list]').innerHTML = '';
    panel.querySelector('[data-p-all]').href = el.getAttribute('href');
    if (window.innerWidth < 900) panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    load(slug).then(function (d) { if (current === slug) render(d); })
      .catch(function () { window.location = el.getAttribute('href'); });
  }

  function load(slug) {
    if (cache[slug]) return Promise.resolve(cache[slug]);
    return fetch('/api/provinces/' + slug + '/').then(function (r) {
      if (!r.ok) throw new Error(r.status); return r.json();
    }).then(function (d) { cache[slug] = d; return d; });
  }

  function render(d) {
    panel.classList.remove('loading');
    panel.querySelector('[data-p-name]').textContent = d.name;
    panel.querySelector('[data-p-sum]').textContent =
      fa(d.count) + ' پروژه' + (d.ongoing ? ' · ' + fa(d.ongoing) + ' در حال اجرا' : '');
    panel.querySelector('[data-p-all]').href = d.list_url;
    var ul = panel.querySelector('[data-p-list]');
    ul.innerHTML = d.projects.map(function (p) {
      return '<li><a href="' + p.url + '"><span class="pl-title">' + esc(fa(p.title)) + '</span>' +
        '<span class="pl-meta"><i class="dotc tag-' + p.service_slug + '"></i>' + esc(p.service) +
        (p.end ? ' · ' + esc(p.end) : '') + '</span></a></li>';
    }).join('');
    ul.scrollTop = 0;
  }

  function close() {
    current = null; panel.hidden = true; intro.hidden = false;
    document.querySelectorAll('.prov.is-selected').forEach(function (n) { n.classList.remove('is-selected'); });
    document.querySelectorAll('.chip.on').forEach(function (n) { n.classList.remove('on'); });
  }

  svg.querySelectorAll('.prov.is-active').forEach(function (el) {
    el.addEventListener('click', function (e) { e.preventDefault(); select(el.dataset.slug); });
    el.addEventListener('mousemove', function (e) { showTip(el, e); });
    el.addEventListener('mouseleave', function () { tip.hidden = true; });
    el.addEventListener('focus', function () {
      var b = el.getBoundingClientRect(), r = svg.parentElement.getBoundingClientRect();
      showTip(el, { clientX: b.left + b.width / 2, clientY: b.top + b.height / 2 });
    });
    el.addEventListener('blur', function () { tip.hidden = true; });
  });
  document.querySelectorAll('[data-chip]').forEach(function (c) {
    c.addEventListener('click', function (e) { e.preventDefault(); select(c.dataset.chip); });
  });
  panel.querySelector('[data-close]').addEventListener('click', close);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && current) close(); });
})();
