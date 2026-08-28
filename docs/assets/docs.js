/* NAMper docs — shared top-bar behaviour: the theme switch and the
   language picker. Every localized copy of a page loads this file, so the
   seventeen-language menu lives in one place instead of in 153 top bars. */
(function () {
  var LOCALES = [
    { c: 'en',      d: '',        n: 'English' },
    { c: 'ru',      d: 'ru',      n: 'Русский' },
    { c: 'de',      d: 'de',      n: 'Deutsch' },
    { c: 'es',      d: 'es',      n: 'Español' },
    { c: 'fr',      d: 'fr',      n: 'Français' },
    { c: 'it',      d: 'it',      n: 'Italiano' },
    { c: 'pt',      d: 'pt',      n: 'Português' },
    { c: 'tr',      d: 'tr',      n: 'Türkçe' },
    { c: 'id',      d: 'id',      n: 'Indonesia' },
    { c: 'vi',      d: 'vi',      n: 'Tiếng Việt' },
    { c: 'th',      d: 'th',      n: 'ไทย' },
    { c: 'ja',      d: 'ja',      n: '日本語' },
    { c: 'ko',      d: 'ko',      n: '한국어' },
    { c: 'zh',      d: 'zh',      n: '简体中文' },
    { c: 'zh-hant', d: 'zh-hant', n: '繁體中文' },
    { c: 'hi',      d: 'hi',      n: 'हिन्दी' },
    { c: 'fil',     d: 'fil',     n: 'Filipino' }
  ];

  /* ---- where are we: /docs/[lang/]page.html ---- */
  function place() {
    var p = location.pathname.replace(/^\/+|\/+$/g, '').split('/'); // docs[,lang][,file]
    var rest = p.slice(1);                                          // after "docs"
    var lang = 'en', file = '';
    if (rest.length && rest[0].indexOf('.html') < 0) {
      for (var i = 0; i < LOCALES.length; i++)
        if (LOCALES[i].d === rest[0]) { lang = LOCALES[i].c; rest = rest.slice(1); break; }
    }
    if (rest.length) file = rest[rest.length - 1];
    return { lang: lang, file: file };
  }
  function href(loc, file) {
    return '/docs/' + (loc.d ? loc.d + '/' : '') + file;
  }

  var here = place();

  /* ---- language picker ---- */
  var nav = document.querySelector('.topbar .langs');
  if (nav) {
    var cur = LOCALES.filter(function (l) { return l.c === here.lang; })[0] || LOCALES[0];
    var det = document.createElement('details');
    det.className = 'langpick';
    var sum = document.createElement('summary');
    sum.textContent = cur.n + ' ▾';
    det.appendChild(sum);
    var menu = document.createElement('div');
    menu.className = 'langmenu';
    LOCALES.forEach(function (l) {
      var a = document.createElement('a');
      a.href = href(l, here.file);
      a.textContent = l.n;
      a.hreflang = l.c === 'zh' ? 'zh-Hans' : l.c === 'zh-hant' ? 'zh-Hant' : l.c;
      if (l.c === here.lang) { a.className = 'on'; a.setAttribute('aria-current', 'page'); }
      menu.appendChild(a);
    });
    det.appendChild(menu);
    nav.textContent = '';
    nav.appendChild(det);
    document.addEventListener('click', function (e) {
      if (det.open && !det.contains(e.target)) det.open = false;
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') det.open = false;
    });
  }

  /* ---- theme: system -> light -> dark -> system ---- */
  var ICO = { system: '◐', light: '☀', dark: '☾' };
  var btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'themebtn';
  btn.title = 'Theme: system / light / dark';
  btn.setAttribute('aria-label', 'Theme');

  function set(v) {
    try {
      if (v === 'system') {
        document.documentElement.removeAttribute('data-theme');
        localStorage.removeItem('theme');
      } else {
        document.documentElement.setAttribute('data-theme', v);
        localStorage.setItem('theme', v);
      }
    } catch (e) {}
    btn.textContent = ICO[v];
  }
  var cur = 'system';
  try { cur = localStorage.getItem('theme') || 'system'; } catch (e) {}
  set(cur);
  btn.addEventListener('click', function () {
    var c = 'system';
    try { c = localStorage.getItem('theme') || 'system'; } catch (e) {}
    set(c === 'system' ? 'light' : c === 'light' ? 'dark' : 'system');
  });
  var bar = document.querySelector('.topbar');
  if (bar) bar.insertBefore(btn, nav || null);
})();
