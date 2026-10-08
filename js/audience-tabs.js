/*
 * Audience state shared across the page: "brand" or "creator".
 * - hero buttons and any link to #workwithus / #creators pick a side and scroll to the form
 * - the "How it works" tabs and the contact form tabs stay in step with each other
 * - the inquiry dropdown sets the placeholder, whether the message is required, and the email subject
 * Pattern learned from adhesivemedia.com (see research/adhesive-interactions.md).
 */
(function () {
    'use strict';

    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var aud = (document.body && document.body.getAttribute('data-audience')) === 'creator' ? 'creator' : 'brand';
    var subs = [];

    function anchorAtCentre() {
        var el = document.elementFromPoint(window.innerWidth / 2, window.innerHeight / 2), main = document.querySelector('main');
        while (el && el.parentElement && el.parentElement !== main) el = el.parentElement;
        return el && el.parentElement === main ? el : null;
    }

    window.GV = {
        get: function () { return aud; },
        on: function (fn) { subs.push(fn); },
        set: function (a, opts) {
            if (a !== 'brand' && a !== 'creator') return;
            if (a === aud) return;
            aud = a;
            /* whatever is in the middle of the screen stays there: switching sides changes the height of sections above it, and Safari
               (unlike Chrome and Firefox) does not compensate for that by itself. If the browser already did, the correction is zero. */
            var anchor = anchorAtCentre(), was = anchor ? anchor.getBoundingClientRect().top : 0;
            subs.forEach(function (fn) { fn(a, opts || {}); });
            if (anchor) { var d = anchor.getBoundingClientRect().top - was; if (Math.abs(d) > 1) window.scrollBy({ top: d, behavior: 'instant' }); }
        }
    };

    function init() {
        var card = document.getElementById('contact-card');
        if (!card) return;
        var tabs = [].slice.call(card.querySelectorAll('.gv-tabbtn'));
        var ind = card.querySelector('.gv-ind');
        var panels = [].slice.call(card.querySelectorAll('[data-gv-panel]'));

        function moveInd() {
            if (!window.GV_PAINTED) return;   /* measuring forces a layout: wait until the first paint has happened */
            var b = tabs.filter(function (t) { return t.getAttribute('data-aud') === aud; })[0];
            if (!b || !ind) return;
            ind.style.left = b.offsetLeft + 'px';
            ind.style.width = b.offsetWidth + 'px';
        }
        function show(a, animate) {
            tabs.forEach(function (t) {
                var on = t.getAttribute('data-aud') === a;
                t.classList.toggle('gv-on', on);
                t.setAttribute('aria-selected', on ? 'true' : 'false');
            });
            panels.forEach(function (p) {
                var on = p.getAttribute('data-gv-panel') === a;
                var was = !p.hidden;
                p.hidden = !on;
                if (on && !was && animate && !reduce && p.animate) {
                    p.animate([{ opacity: 0, transform: 'translateY(12px)' }, { opacity: 1, transform: 'none' }],
                        { duration: 320, easing: 'cubic-bezier(0.22,1,0.36,1)' });
                }
            });
            moveInd();
        }
        tabs.forEach(function (t) {
            t.addEventListener('click', function () { window.GV.set(t.getAttribute('data-aud')); });
        });
        window.GV.on(function (a) { show(a, true); });
        window.addEventListener('resize', moveInd);
        if (document.fonts && document.fonts.ready) document.fonts.ready.then(moveInd);
        show(aud, false);
        document.addEventListener('gv-painted', moveInd);

        /* inquiry dropdown: shorter message, same inbox, easier sorting */
        [].forEach.call(card.querySelectorAll('form'), function (form) {
            var sel = form.querySelector('select[name="inquiry"]');
            var msg = form.querySelector('textarea[name="message"]');
            var subj = form.querySelector('input[name="_subject"]');
            var who = form.getAttribute('data-who') || 'request';
            if (!sel) return;
            var base = msg ? msg.getAttribute('placeholder') : '';
            sel.addEventListener('change', function () {
                var opt = sel.options[sel.selectedIndex];
                if (msg) {
                    msg.setAttribute('placeholder', opt.getAttribute('data-hint') || base);
                    var need = opt.getAttribute('data-need') === '1';
                    msg.required = need;
                    var label = form.querySelector('[data-msg-note]');
                    if (label) label.textContent = need ? 'Required' : 'Optional';
                }
                if (subj) subj.value = 'New ' + who + ': ' + opt.textContent.trim();
                sel.classList.add('gv-chosen');
            });
        });

        /* links to the forms choose the matching side first */
        function go(a) {
            window.GV.set(a);
            /* land on the whole "Let's work together" section (heading + form), not just the card; the top bar hides on the way down */
            var sec = card.closest('section') || card;
            var y = sec.getBoundingClientRect().top + window.pageYOffset;
            window.scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
        }
        [].forEach.call(document.querySelectorAll('a[href="#workwithus"], a[href="#creators"]'), function (a) {
            a.addEventListener('click', function (ev) {
                ev.preventDefault();
                go(a.getAttribute('href') === '#creators' ? 'creator' : 'brand');
                if (history.replaceState) history.replaceState(null, '', a.getAttribute('href'));
            });
        });
        if (location.hash === '#creators') { window.GV.set('creator'); }
    }

    /* FAQ: audience tabs with a sliding pill, one answer open at a time */
    function initFaq() {
        var sec = document.getElementById('faq');
        if (!sec) return;
        var tabs = [].slice.call(sec.querySelectorAll('.faq-tabbtn'));
        var ind = sec.querySelector('.faq-ind');
        var panels = [].slice.call(sec.querySelectorAll('[data-faq-panel]'));
        /* single-audience pages have no tabs: the list stays on that side whatever the contact form shows */
        var locked = tabs.length === 0;
        var fixed = panels[0] ? panels[0].getAttribute('data-faq-panel') : aud;

        function moveInd() {
            if (!window.GV_PAINTED) return;   /* measuring forces a layout: wait until the first paint has happened */
            var b = tabs.filter(function (t) { return t.getAttribute('data-aud') === aud; })[0];
            if (!b || !ind) return;
            ind.style.left = b.offsetLeft + 'px';
            ind.style.width = b.offsetWidth + 'px';
        }
        function closeAll(scope) {
            [].forEach.call(scope.querySelectorAll('.faq-item.faq-open'), function (it) {
                it.classList.remove('faq-open');
                it.querySelector('.faq-q').setAttribute('aria-expanded', 'false');
            });
        }
        function show(a, animate) {
            tabs.forEach(function (t) {
                var on = t.getAttribute('data-aud') === a;
                t.classList.toggle('faq-on', on);
                t.setAttribute('aria-selected', on ? 'true' : 'false');
            });
            panels.forEach(function (p) {
                var on = p.getAttribute('data-faq-panel') === a;
                var was = !p.hidden;
                if (!on) closeAll(p);
                p.hidden = !on;
                if (on && !was && animate && !reduce && p.animate) {
                    p.animate([{ opacity: 0, transform: 'translateY(10px)' }, { opacity: 1, transform: 'none' }],
                        { duration: 300, easing: 'cubic-bezier(0.22,1,0.36,1)' });
                }
            });
            moveInd();
        }
        tabs.forEach(function (t) {
            t.addEventListener('click', function () { window.GV.set(t.getAttribute('data-aud')); });
        });
        [].forEach.call(sec.querySelectorAll('.faq-q'), function (q) {
            q.addEventListener('click', function () {
                var item = q.parentNode.parentNode;
                var open = !item.classList.contains('faq-open');
                closeAll(item.parentNode);
                if (open) {
                    item.classList.add('faq-open');
                    q.setAttribute('aria-expanded', 'true');
                }
            });
        });
        if (!locked) window.GV.on(function (a) { show(a, true); });
        window.addEventListener('resize', moveInd);
        if (document.fonts && document.fonts.ready) document.fonts.ready.then(moveInd);
        show(locked ? fixed : aud, false);
        document.addEventListener('gv-painted', moveInd);
    }

    /* Benefits (home page): brand cards / creator cards behind "I'm a brand" / "I'm a creator" tabs */
    function initBenefits() {
        var sec = document.getElementById('benefits');
        if (!sec) return;
        var tabs = [].slice.call(sec.querySelectorAll('.faq-tabbtn'));
        var ind = sec.querySelector('.faq-ind');
        var panels = [].slice.call(sec.querySelectorAll('[data-bn-panel]'));

        function moveInd() {
            if (!window.GV_PAINTED) return;   /* measuring forces a layout: wait until the first paint has happened */
            var b = tabs.filter(function (t) { return t.getAttribute('data-aud') === aud; })[0];
            if (!b || !ind) return;
            ind.style.left = b.offsetLeft + 'px';
            ind.style.width = b.offsetWidth + 'px';
        }
        function show(a, animate) {
            tabs.forEach(function (t) {
                var on = t.getAttribute('data-aud') === a;
                t.classList.toggle('faq-on', on);
                t.setAttribute('aria-selected', on ? 'true' : 'false');
            });
            panels.forEach(function (p) {
                var on = p.getAttribute('data-bn-panel') === a;
                var was = !p.hidden;
                p.hidden = !on;
                if (on && !was && animate && !reduce && p.animate) {
                    p.animate([{ opacity: 0, transform: 'translateY(14px)' }, { opacity: 1, transform: 'none' }],
                        { duration: 350, easing: 'cubic-bezier(0.22,1,0.36,1)' });
                }
            });
            moveInd();
        }
        tabs.forEach(function (t) {
            t.addEventListener('click', function () { window.GV.set(t.getAttribute('data-aud')); });
        });
        window.GV.on(function (a) { show(a, true); });
        window.addEventListener('resize', moveInd);
        if (document.fonts && document.fonts.ready) document.fonts.ready.then(moveInd);
        show(aud, false);
        document.addEventListener('gv-painted', moveInd);
    }

    /* sections for one side only ([data-aud-only="brand"], e.g. the creator vetting standards): hidden while the other side is chosen.
       The scroll position is kept steady by GV.set above. */
    function initOnly() {
        var els = [].slice.call(document.querySelectorAll('[data-aud-only]'));
        if (!els.length) return;
        function apply(a, animate) {
            els.forEach(function (el) {
                var show = el.getAttribute('data-aud-only') === a;
                if (show === !el.hidden) return;
                el.hidden = !show;
                if (show && animate && !reduce && el.animate) el.animate([{ opacity: 0, transform: 'translateY(14px)' }, { opacity: 1, transform: 'none' }], { duration: 350, easing: 'cubic-bezier(0.22,1,0.36,1)' });
            });
        }
        window.GV.on(function (a) { apply(a, true); });
        apply(aud, false);
    }

    function boot() { init(); initFaq(); initBenefits(); initOnly(); }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
    else boot();
    /* after the first paint: let the tab pills measure themselves (doing it earlier forces a full layout inside the script) */
    requestAnimationFrame(function () { requestAnimationFrame(function () { window.GV_PAINTED = true; document.dispatchEvent(new Event('gv-painted')); }); });
})();
