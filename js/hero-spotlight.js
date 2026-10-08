/* Hero spotlight: a circle follows the mouse and shows a light version of the hero (white gradient, coloured text,
   the G in its own colours). The light version is a clone of .hero-layer, so it always matches the real layout.
   Wide screens with a mouse or pen: the circle follows the pointer. Phones (under 640px wide): a light shape with a curved lower edge hangs from the top edge
   behind the logo and grows in once, so the logo shows in its light version. Tablets without a mouse and keyboard users just see the normal hero. */
(function () {
  var hero = document.querySelector('[data-hero]');
  var layer = hero && hero.querySelector('.hero-layer');
  if (!layer) return;
  var narrow = window.matchMedia('(max-width: 639px)');
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)');
  if (!narrow.matches && !fine.matches) return;

  // light copy: same markup, not focusable, not announced, only one <h1> on the page
  var alt = document.createElement('div');
  alt.className = 'hero-alt';
  alt.setAttribute('aria-hidden', 'true');
  alt.setAttribute('inert', '');
  var copy = layer.cloneNode(true);
  copy.querySelectorAll('[id]').forEach(function (n) {
    n.removeAttribute('id');
  });
  copy.querySelectorAll('a').forEach(function (a) {
    a.setAttribute('tabindex', '-1');
  });
  copy.querySelectorAll('h1').forEach(function (h) {
    var d = document.createElement('div');
    d.className = h.className;
    d.innerHTML = h.innerHTML;
    h.replaceWith(d);
  });
  alt.appendChild(copy);
  var ring = document.createElement('div');
  ring.className = 'hero-lens-ring';
  ring.setAttribute('aria-hidden', 'true');
  var wrap = document.createElement('div'); // carries the drop shadow (a shadow on the clipped element itself would be clipped too)
  wrap.className = 'hero-alt-wrap';
  wrap.appendChild(alt);
  hero.appendChild(wrap);
  hero.appendChild(ring);

  var logo = layer.querySelector('.wordmark');
  var fixedMode = false;

  /* phones: a fixed light shape from the top edge: a rectangle whose lower edge is a gentle curve (a parabola with a sag of SAG px).
       The flat part is as tall as it needs to be to keep CLEAR px of air under the logo (and the pills), measured from the real
       elements, so it follows font loading and rotation. The curve itself always has the same shape. */
  var SAG = 35,
    CLEAR = 40;
  function domePath(W, E) {
    return (
      "path('M0 0H" +
      W.toFixed(1) +
      'V' +
      E.toFixed(1) +
      'Q' +
      (W / 2).toFixed(1) +
      ' ' +
      (E + 2 * SAG * (E > 0 ? 1 : 0)).toFixed(1) +
      ' 0 ' +
      E.toFixed(1) +
      "Z')"
    );
  }
  function placeFixed() {
    var hb = hero.getBoundingClientRect(),
      mid = hb.width / 2,
      E = 0;
    [logo, layer.querySelector('.hero-chip')]
      .filter(Boolean)
      .forEach(function (n) {
        var b = n.getBoundingClientRect();
        var u = Math.min(
          1,
          Math.max(
            Math.abs(b.left - hb.left - mid),
            Math.abs(b.right - hb.left - mid),
          ) / mid,
        ); // how far out the item reaches
        E = Math.max(E, b.bottom - hb.top + CLEAR - SAG * (1 - u * u)); // curve height at that spot = E + SAG(1-u^2)
      });
    alt.style.clipPath = domePath(hb.width, E);
    ring.classList.remove('is-on');
  }
  function mode() {
    var f = narrow.matches;
    hero.classList.toggle('hero-fixed', f);
    alt.hidden = wrap.hidden = ring.hidden = !(f || fine.matches);
    if (f) {
      rt = 0;
      r = 0;
      if (!fixedMode) {
        // grow in once: start at 0, then set the real size on the next frame
        alt.style.clipPath = domePath(hero.clientWidth, 0);
        requestAnimationFrame(function () {
          requestAnimationFrame(placeFixed);
        });
      } else placeFixed();
    } else {
      rt = 0;
      r = 0;
      seen = false;
      alt.style.clipPath = '';
      ring.classList.remove('is-on');
    }
    fixedMode = f;
  }

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cx = 0,
    cy = 0; // pointer, in viewport coordinates
  var x = 0,
    y = 0,
    r = 0; // what is drawn (hero coordinates, radius)
  var rt = 0,
    seen = false,
    raf = 0;

  var RING = 210; // the ring is drawn at its largest size (radius() never exceeds this) and scaled down
  function radius() {
    return Math.max(
      120,
      Math.min(210, Math.min(hero.clientWidth, hero.clientHeight) * 0.24),
    );
  }

  function frame() {
    raf = 0;
    if (fixedMode) return;
    var b = hero.getBoundingClientRect();
    var tx = cx - b.left,
      ty = cy - b.top;
    var k = reduce ? 1 : 0.2;
    x += (tx - x) * k;
    y += (ty - y) * k;
    r += (rt - r) * (reduce ? 1 : 0.16);
    if (Math.abs(rt - r) < 0.5) r = rt;
    // set straight on the two elements (not as inherited CSS variables on the hero, which would restyle the whole hero every frame)
    alt.style.clipPath =
      'circle(' +
      r.toFixed(1) +
      'px at ' +
      x.toFixed(1) +
      'px ' +
      y.toFixed(1) +
      'px)';
    ring.style.transform =
      'translate3d(' +
      (x - RING).toFixed(1) +
      'px,' +
      (y - RING).toFixed(1) +
      'px,0) scale(' +
      (r / RING).toFixed(3) +
      ')';
    ring.classList.toggle('is-on', r > 1);
    if (r !== rt || Math.abs(tx - x) > 0.3 || Math.abs(ty - y) > 0.3)
      raf = requestAnimationFrame(frame);
  }
  function kick() {
    if (!raf) raf = requestAnimationFrame(frame);
  }

  hero.addEventListener('pointermove', function (e) {
    if (fixedMode || e.pointerType === 'touch') return;
    cx = e.clientX;
    cy = e.clientY;
    if (!seen) {
      // first entry: start at the pointer, not at the corner
      var b = hero.getBoundingClientRect();
      x = cx - b.left;
      y = cy - b.top;
      seen = true;
    }
    rt = radius();
    kick();
  });
  hero.addEventListener('pointerleave', function () {
    if (fixedMode) return;
    rt = 0;
    kick();
  });
  window.addEventListener(
    'scroll',
    function () {
      if (rt && !fixedMode) kick();
    },
    { passive: true },
  );
  window.addEventListener('resize', function () {
    if (fixedMode && narrow.matches) placeFixed();
  });
  if (narrow.addEventListener) {
    narrow.addEventListener('change', mode);
    fine.addEventListener('change', mode);
  }
  if (document.fonts && document.fonts.ready)
    document.fonts.ready.then(function () {
      if (fixedMode) placeFixed();
    });
  mode();
})();
