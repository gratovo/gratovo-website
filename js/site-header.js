/*
 * Top bar behaviour.
 *  - Pages with a full-screen hero (data-hide-on-hero: home, brands, creators): the bar starts hidden because the hero carries
 *    the logo and pills. After a short scroll (about 20% of the hero) it slides in and stays while the hero is on screen.
 *  - Every page (data-autohide): once you are past the top (or past the hero), the bar tucks away while you scroll down to read and comes
 *    straight back when you scroll up, hover it, tab into it, or reach the top. Small wobbles never trigger it (a few pixels of travel are
 *    needed in one direction) and it never hides while the pointer or keyboard focus is on it.
 * While hidden at the top of a hero page it is `inert`, so keyboard focus skips it.
 */
(function () {
    'use strict';
    var bar = document.querySelector('.site-header[data-autohide]');
    if (!bar) return;
    var hero = document.querySelector('[data-hero]');
    var heroPage = bar.hasAttribute('data-hide-on-hero') && !!hero;

    var lastY = window.pageYOffset || 0;
    var run = 0;                       // pixels travelled in the current direction (down = +, up = -)
    var hidden = heroPage, queued = false, pointerOn = false;

    function setHidden(h, inert) {
        if (h === hidden && (!heroPage || h === bar.hasAttribute('inert'))) return;
        hidden = h;
        bar.classList.toggle('is-hidden', h);
        if (h && inert) bar.setAttribute('inert', ''); else bar.removeAttribute('inert');
    }

    function update() {
        queued = false;
        var y = Math.max(0, window.pageYOffset || document.documentElement.scrollTop || 0);
        var dy = y - lastY;
        lastY = y;

        if (heroPage) {
            var h = hero.offsetHeight || window.innerHeight;
            if (y < h * (hidden ? 0.2 : 0.12)) { run = 0; setHidden(true, true); return; }   // top of the hero: pills only
            if (y < h * 0.8) { run = 0; setHidden(false); return; }                            // short scroll into the hero: bar shown
        } else if (y < 80) { run = 0; setHidden(false); return; }                               // near the top of any other page

        if (pointerOn || bar.contains(document.activeElement)) { setHidden(false); run = 0; return; }
        if (dy === 0) return;
        run = (dy > 0) === (run > 0) ? run + dy : dy;                                           // restart the count when direction flips
        if (run > 14) setHidden(true);                                                          // reading down: tuck away
        else if (run < -6) setHidden(false);                                                    // any real move up: bring it back
    }
    function queue() {
        if (queued) return;
        queued = true;
        requestAnimationFrame(update);
    }

    window.addEventListener('scroll', queue, { passive: true });
    window.addEventListener('resize', queue);
    bar.addEventListener('pointerenter', function () { pointerOn = true; setHidden(false); });
    bar.addEventListener('pointerleave', function () { pointerOn = false; });
    document.addEventListener('pointermove', function (e) {                                     // mouse to the very top edge brings it back
        if (hidden && !bar.hasAttribute('inert') && e.pointerType === 'mouse' && e.clientY < 6) setHidden(false);
    }, { passive: true });
    bar.addEventListener('focusin', function () { setHidden(false); });
    update();
})();
