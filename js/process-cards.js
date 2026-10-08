/*
 * Gratovo "How it works" animated process cards.
 *
 * Approach (learned from research/adhesive-interactions.md): every diagram is a small
 * composition that is a pure function of the CURRENT FRAME NUMBER on a fixed 520x480 stage
 * at 30 fps. All timing lives on one timeline (springs, eased interpolation, masked light
 * sweeps, spinner-to-check, text scramble), so nothing drifts out of sync. A stage is scaled
 * to fit its card with a CSS transform.
 *
 * To add or change a diagram: edit/add a composition in `C` and point a card at it with
 * data-comp="name" (+ data-opt for its labels). Do not tune CSS delays.
 */
(function () {
    'use strict';

    var FPS = 30, SW = 520, SH = 480;
    var ACC = '#0072b8';
    var LINE = 'rgba(11,28,46,0.12)';
    var DOT = 'rgba(11,28,46,0.22)';
    var RING = 'rgba(11,28,46,0.13)';
    var INK = '#3e4c5e';
    var CHIP = '#eef6fc';
    var NS = 'http://www.w3.org/2000/svg';

    /* ---------- math + easing ---------- */
    function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
    function lerp(a, b, t) { return a + (b - a) * t; }
    function bezier(x1, y1, x2, y2) {
        function cx(t) { return 3 * (1 - t) * (1 - t) * t * x1 + 3 * (1 - t) * t * t * x2 + t * t * t; }
        function cy(t) { return 3 * (1 - t) * (1 - t) * t * y1 + 3 * (1 - t) * t * t * y2 + t * t * t; }
        return function (x) {
            if (x <= 0) return 0;
            if (x >= 1) return 1;
            var lo = 0, hi = 1, t = x;
            for (var i = 0; i < 24; i++) {
                var v = cx(t);
                if (Math.abs(v - x) < 1e-5) break;
                if (v < x) lo = t; else hi = t;
                t = (lo + hi) / 2;
            }
            return cy(t);
        };
    }
    var E = {
        linear: function (t) { return t; },
        quad: function (t) { return t * t; },
        cubic: function (t) { return t * t * t; },
        out: function (f) { return function (t) { return 1 - f(1 - t); }; },
        inOut: function (f) { return function (t) { return t < 0.5 ? f(t * 2) / 2 : 1 - f((1 - t) * 2) / 2; }; },
        back: function (s) { return function (t) { return t * t * ((s + 1) * t - s); }; }
    };
    var outCubic = E.out(E.cubic), inOutCubic = E.inOut(E.cubic), inOutQuad = E.inOut(E.quad);
    var outQuad = E.out(E.quad), linear = E.linear, sweepEase = bezier(0.32, 0, 0.68, 1);
    function outBack(s) { return E.out(E.back(s)); }

    /* progress 0..1 of frame f between a and b, through an easing (default in-out quad) */
    function ip(f, a, b, e) { return (e || inOutQuad)(clamp((f - a) / (b - a), 0, 1)); }
    /* piecewise-linear keyframes, clamped */
    function kf(v, xs, ys) {
        if (v <= xs[0]) return ys[0];
        for (var i = 1; i < xs.length; i++) {
            if (v <= xs[i]) return lerp(ys[i - 1], ys[i], (v - xs[i - 1]) / (xs[i] - xs[i - 1]));
        }
        return ys[ys.length - 1];
    }

    /* damped spring 0 -> 1, time-stretched to settle at cfg.duration frames (like Remotion's spring) */
    var springNat = {};
    function springPos(t, c) {
        var w0 = Math.sqrt(c.stiffness / c.mass), z = c.damping / (2 * Math.sqrt(c.stiffness * c.mass));
        if (z < 1) {
            var wd = w0 * Math.sqrt(1 - z * z);
            return 1 - Math.exp(-z * w0 * t) * (Math.cos(wd * t) + (z * w0 / wd) * Math.sin(wd * t));
        }
        return 1 - Math.exp(-w0 * t) * (1 + w0 * t);
    }
    function spring(frame, c) {
        if (frame <= 0) return 0;
        var key = c.damping + '|' + c.stiffness + '|' + c.mass;
        var nat = springNat[key];
        if (!nat) {
            var last = 0;
            for (var f = 0; f < 300; f++) if (Math.abs(1 - springPos(f / FPS, c)) > 0.005) last = f;
            nat = springNat[key] = last + 1;
        }
        var ff = c.duration ? frame * nat / c.duration : frame;
        return springPos(ff / FPS, c);
    }
    var SPR = { damping: 9, stiffness: 125, mass: 0.9, duration: 20 };
    function sprCfg(duration, damping, stiffness, mass) {
        return { damping: damping || 9, stiffness: stiffness || 125, mass: mass || 0.9, duration: duration };
    }
    /* chip/icon pop-in: scale .6 -> 1, opacity ramps over the first 20% of the spring */
    function pop(f, start, cfg) {
        var s = spring(f - start, cfg || SPR);
        return { s: lerp(0.6, 1, s), o: clamp(kf(s, [0, 0.2, 1], [0, 1, 1]), 0, 1) };
    }

    /* text that resolves left to right out of deterministic random characters */
    var CH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    function hashChar(f, i) {
        var o = 43758.5453 * Math.sin(12.9898 * (17 * f + 23 * i));
        o = o - Math.floor(o);
        return CH.charAt(Math.floor(36 * o));
    }
    function scramble(f, t, a, b) {
        t = clamp(t, 0, 1);
        if (t <= 0) return a;
        if (t >= 1) return b;
        var n = Math.max(a.length, b.length), s = 1 / n, out = '';
        for (var c = 0; c < n; c++) {
            var p = b.charAt(c);
            out += t >= s * (c + 1) ? p : (p ? hashChar(f, c) : '');
        }
        return out;
    }

    function mixColor(a, b, t) {
        var pa = a.match(/[\d.]+/g).map(Number), pb = b.match(/[\d.]+/g).map(Number);
        function g(arr, i, d) { return arr.length > i ? arr[i] : d; }
        var r = Math.round(lerp(pa[0], pb[0], t)), gg = Math.round(lerp(pa[1], pb[1], t)), bb = Math.round(lerp(pa[2], pb[2], t));
        var al = lerp(g(pa, 3, 1), g(pb, 3, 1), t);
        return 'rgba(' + r + ',' + gg + ',' + bb + ',' + al.toFixed(3) + ')';
    }
    var RING_RGB = 'rgba(11,28,46,0.13)', ACC_RGB = 'rgba(0,114,184,1)';

    /* ---------- DOM helpers ---------- */
    function svgEl(name, attrs) {
        var e = document.createElementNS(NS, name);
        if (attrs) for (var k in attrs) e.setAttribute(k, attrs[k]);
        return e;
    }
    var uidc = 0;
    function Stage(host) {
        var S = { uid: 'pc' + (++uidc), host: host };
        S.root = document.createElement('div');
        S.root.className = 'pc-stage';
        S.svg = svgEl('svg', { width: SW, height: SH, viewBox: '0 0 ' + SW + ' ' + SH });
        S.svg.setAttribute('class', 'pc-svg');
        S.defs = svgEl('defs');
        S.svg.appendChild(S.defs);
        S.root.appendChild(S.svg);
        host.appendChild(S.root);
        return S;
    }
    function node(S, css, html) {
        var d = document.createElement('div');
        d.className = 'pc-n';
        for (var k in css) d.style[k] = css[k];
        if (html) d.innerHTML = html;
        S.root.appendChild(d);
        return d;
    }
    /* write style props only when they changed */
    function put(el, props) {
        var c = el._c || (el._c = {});
        for (var k in props) {
            var v = props[k];
            if (c[k] !== v) { c[k] = v; el.style[k] = v; }
        }
    }
    function ico(name, size, color) {
        return '<span class="pc-ico material-symbols-outlined" style="font-size:' + size + 'px;color:' + (color || INK) + '">' + name + '</span>';
    }
    var CHECK_SVG = '<svg viewBox="0 0 24 24" width="100%" height="100%"><circle cx="12" cy="12" r="10.5" fill="' + ACC + '"/><path d="M7.2 12.4l3.1 3.1L16.9 9" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    function spinnerSVG(id) {
        var c = 2 * Math.PI * 8.5;
        return '<svg viewBox="0 0 24 24" width="100%" height="100%"><defs><linearGradient id="' + id + '" x1="12" y1="2" x2="12" y2="22" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="' + ACC + '"/><stop offset=".5" stop-color="' + ACC + '" stop-opacity="0"/><stop offset="1" stop-color="' + ACC + '" stop-opacity="0"/></linearGradient></defs><circle cx="12" cy="12" r="8.5" fill="none" stroke="url(#' + id + ')" stroke-width="3" stroke-linecap="round" stroke-dasharray="' + (0.96 * c) + ' ' + c + '" transform="rotate(-90 12 12)"/></svg>';
    }

    /* rounded label chip, positioned by its top-left in stage units */
    function Chip(S, o) {
        var el = node(S, {
            left: o.x + 'px', top: o.y + 'px', width: o.w + 'px', height: o.h + 'px',
            borderRadius: (o.r || 10) + 'px', border: '1.5px solid ' + (o.border || RING),
            background: o.bg || '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
            gap: (o.gap || 10) + 'px', overflow: 'hidden', transformOrigin: '50% 50%', opacity: '0',
            boxSizing: 'border-box'
        });
        var iconEl = null;
        if (o.icon) {
            var w = document.createElement('span');
            w.className = 'pc-iconwrap';
            w.innerHTML = ico(o.icon, o.is || 22, o.iconColor || INK);
            el.appendChild(w);
            iconEl = w.firstChild;
        }
        var tx = document.createElement('span');
        tx.className = 'pc-txt';
        tx.style.fontSize = (o.fs || 17) + 'px';
        tx.style.letterSpacing = (o.ls != null ? o.ls : 0.6) + 'px';
        tx.textContent = o.text || '';
        el.appendChild(tx);
        return {
            el: el, icon: iconEl, tx: tx,
            set: function (p) {
                var css = {};
                if (p.scale != null) css.transform = 'translate(' + (p.dx || 0).toFixed(2) + 'px,' + (p.dy || 0).toFixed(2) + 'px) scale(' + p.scale.toFixed(4) + ')';
                if (p.opacity != null) css.opacity = clamp(p.opacity, 0, 1).toFixed(3);
                if (p.border) css.borderColor = p.border;
                if (p.left != null) css.left = p.left.toFixed(2) + 'px';
                if (p.width != null) css.width = p.width.toFixed(2) + 'px';
                put(el, css);
                if (p.text != null && tx._t !== p.text) { tx._t = p.text; tx.textContent = p.text; }
                if (p.iconColor && iconEl) put(iconEl, { color: p.iconColor });
            }
        };
    }

    /* circular node centred at (x,y), fixed size, animated by transform */
    function Disc(S, o) {
        var el = node(S, {
            left: (o.x - o.d / 2) + 'px', top: (o.y - o.d / 2) + 'px', width: o.d + 'px', height: o.d + 'px',
            borderRadius: '50%', border: (o.bw || 2) + 'px solid ' + RING, background: o.bg || '#fff',
            display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden',
            transformOrigin: '50% 50%', opacity: '0', boxSizing: 'border-box'
        }, o.html);
        return {
            el: el,
            inner: el.firstChild,
            set: function (p) {
                var css = {};
                if (p.scale != null) css.transform = 'scale(' + Math.max(0, p.scale).toFixed(4) + ')';
                if (p.opacity != null) css.opacity = clamp(p.opacity, 0, 1).toFixed(3);
                if (p.border) css.borderColor = p.border;
                put(el, css);
            }
        };
    }

    /* creator avatar: soft gradient disc with a neutral head-and-shoulders mark (no real people) */
    var HUES = [['#7cc4ee', '#3b8fcb'], ['#b9a8f0', '#7a63d6'], ['#f3b3c8', '#d9648e'], ['#9fe0c6', '#3fae8a'],
        ['#f7d58e', '#e0a43a'], ['#9ec9f5', '#4f86d6'], ['#f5b9a1', '#df7a55'], ['#a8d8e8', '#4f9fb8']];
    /* photos (optional): paths to real, permitted creator photos. The neutral avatar always sits underneath,
       so a missing or broken file just shows the avatar. */
    function personHTML(i, size, photos) {
        var h = HUES[i % HUES.length];
        var img = photos && photos[i]
            ? '<img src="' + String(photos[i]).replace(/"/g, '') + '" alt="" draggable="false" loading="lazy" onerror="this.remove()" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center top">'
            : '';
        return '<div style="position:relative;width:100%;height:100%;background:linear-gradient(160deg,' + h[0] + ',' + h[1] + ');display:flex;align-items:flex-end;justify-content:center">' +
            '<svg viewBox="0 0 40 40" style="width:86%;height:86%;display:block"><circle cx="20" cy="14.5" r="7.2" fill="rgba(255,255,255,.92)"/><path d="M5.5 40c0-8.6 6.5-14 14.5-14s14.5 5.4 14.5 14z" fill="rgba(255,255,255,.92)"/></svg>' + img + '</div>';
    }
    var BRAND_ICONS = ['smart_toy', 'bolt', 'cloud', 'terminal', 'database', 'hub', 'memory', 'code'];
    function brandHTML(i, size) {
        return '<div style="width:100%;height:100%;background:#eef6fc;display:flex;align-items:center;justify-content:center">' +
            ico(BRAND_ICONS[i % BRAND_ICONS.length], size, ACC) + '</div>';
    }

    /* straight svg line that can grow */
    function Line(S, x1, y1, x2, y2, o) {
        o = o || {};
        var el = svgEl('line', {
            x1: x1, y1: y1, x2: x2, y2: y2, stroke: o.stroke || LINE, 'stroke-width': o.width || 2, 'stroke-linecap': 'round'
        });
        if (o.dash) el.setAttribute('stroke-dasharray', o.dash);
        el.setAttribute('opacity', '0');
        S.svg.appendChild(el);
        return {
            el: el,
            set: function (ax, ay, bx, by, op) {
                el.setAttribute('x1', ax); el.setAttribute('y1', ay);
                el.setAttribute('x2', bx); el.setAttribute('y2', by);
                var v = clamp(op, 0, 1).toFixed(3);
                if (el._o !== v) { el._o = v; el.setAttribute('opacity', v); }
            }
        };
    }

    /*
     * A bright band that travels down the stage, visible only through a mask built from
     * lines and outlines. This is what makes the light "run along" the connections.
     * stops: [[offset, opacity], ...]; half = half band height.
     */
    function Sweep(S, key, stops, half, blur) {
        var id = S.uid + key;
        var g = svgEl('linearGradient', { id: id + 'g', gradientUnits: 'userSpaceOnUse', x1: SW / 2, x2: SW / 2, y1: 0, y2: 1 });
        stops.forEach(function (s) {
            g.appendChild(svgEl('stop', { offset: (s[0] * 100) + '%', 'stop-color': ACC, 'stop-opacity': s[1] }));
        });
        S.defs.appendChild(g);
        var fl = svgEl('filter', { id: id + 'f', x: '-20%', y: '-20%', width: '140%', height: '140%' });
        fl.appendChild(svgEl('feGaussianBlur', { stdDeviation: blur || 2.2 }));
        S.defs.appendChild(fl);
        var m = svgEl('mask', { id: id + 'm' });
        m.appendChild(svgEl('rect', { width: SW, height: SH, fill: 'black' }));
        S.defs.appendChild(m);
        function rect(glow) {
            var r = svgEl('rect', { x: 0, y: 0, width: SW, height: SH, fill: 'url(#' + id + 'g)', mask: 'url(#' + id + 'm)', opacity: 0 });
            if (glow) r.setAttribute('filter', 'url(#' + id + 'f)');
            S.svg.appendChild(r);
            return r;
        }
        var glowR = rect(true), sharpR = rect(false);
        return {
            line: function (x1, y1, x2, y2, w) {
                var l = svgEl('line', { x1: x1, y1: y1, x2: x2, y2: y2, stroke: 'white', 'stroke-width': w || 2, 'stroke-linecap': 'round' });
                m.appendChild(l);
                return l;
            },
            rect: function (x, y, w, h, rx, sw) {
                var r = svgEl('rect', { x: x, y: y, width: w, height: h, rx: rx, ry: rx, fill: 'none', stroke: 'white', 'stroke-width': sw || 2 });
                m.appendChild(r);
                return r;
            },
            update: function (center, opacity, glowOpacity) {
                g.setAttribute('y1', (center - half).toFixed(2));
                g.setAttribute('y2', (center + half).toFixed(2));
                glowR.setAttribute('opacity', clamp(glowOpacity != null ? glowOpacity : opacity * 0.35, 0, 1).toFixed(3));
                sharpR.setAttribute('opacity', clamp(opacity, 0, 1).toFixed(3));
            }
        };
    }
    function setLine(el, x1, y1, x2, y2) {
        el.setAttribute('x1', x1); el.setAttribute('y1', y1); el.setAttribute('x2', x2); el.setAttribute('y2', y2);
    }

    /* everything fades in at the start and out at the end so the loop restart is invisible */
    function fadeIO(f, loop, inEnd, outStart) {
        return ip(f, 0, inEnd, outQuad) * (1 - ip(f, outStart, loop - 1, inOutCubic));
    }

    /* ======================================================================
     * Compositions. Each returns { loop, hold, render(frame) }.
     * `hold` is the frame shown when motion is reduced.
     * ====================================================================== */
    var C = {};

    /* A. Brief / channel received: chip -> hub -> three tags, with a light sweep */
    C.brief = function (S, o) {
        var loop = 150;
        var L1 = Line(S, 260, 74, 260, 152);
        var tg = [{ x: 58, y: 362, w: 80, h: 40 }, { x: 196, y: 322, w: 128, h: 40 }, { x: 382, y: 362, w: 80, h: 40 }];
        var tl = tg.map(function (t) { return Line(S, 260, 210, t.x + t.w / 2, t.y); });
        var sw = Sweep(S, 'bs', [[0.28, 0], [0.52, 0.95], [0.6, 0]], 110, 2.3);
        sw.line(260, 74, 260, 152);
        sw.rect(156, 153, 208, 56, 28, 4);
        tg.forEach(function (t) { sw.line(260, 210, t.x + t.w / 2, t.y); });
        var top = Chip(S, { x: 150, y: 22, w: 220, h: 52, r: 10, icon: o.topIcon, text: o.topText, fs: 15, ls: 0.6, iconColor: ACC });
        var hub = Chip(S, { x: 156, y: 153, w: 208, h: 56, r: 28, icon: o.hubIcon, text: o.hubText, fs: 15, ls: 0.6, bg: CHIP });
        var tags = tg.map(function (t, i) { return Chip(S, { x: t.x, y: t.y, w: t.w, h: t.h, r: 8, text: o.tags[i], fs: 13, ls: 0.4 }); });
        return {
            loop: loop, hold: 120,
            render: function (f) {
                var g = fadeIO(f, loop, 8, 138);
                var shake = 1 - ip(f, 0, 60, outQuad);
                var p = pop(f, 0, sprCfg(16));
                top.set({ scale: p.s, opacity: p.o * g, dx: 3 * Math.sin(1.9 * f) * shake, dy: 1.2 * Math.sin(2.2 * f) * shake });
                var d1 = ip(f, 6, 22, outCubic);
                L1.set(260, 74, 260, lerp(74, 152, d1), d1 > 0 ? g : 0);
                var ph = pop(f, 18, sprCfg(16));
                hub.set({ scale: ph.s, opacity: ph.o * g });
                tl.forEach(function (l, i) {
                    var t = ip(f, 28 + i * 3, 44 + i * 3, outCubic);
                    var tx = tg[i].x + tg[i].w / 2, ty = tg[i].y;
                    l.set(260, 210, lerp(260, tx, t), lerp(210, ty, t), t > 0 ? g : 0);
                    var pt = pop(f, 38 + i * 4, sprCfg(14));
                    tags[i].set({ scale: pt.s, opacity: pt.o * g });
                });
                var c = lerp(-180, 660, ip(f, 56, 130, sweepEase));
                sw.update(c, f >= 56 && f <= 138 ? g : 0);
            }
        };
    };

    /* B. Matching: scanning chip, eight candidates fan out, then the field narrows to three */
    C.match = function (S, o) {
        var loop = 270, N = 8, KEEP = o.keep || [0, 3, 5], size = 82;
        var pts = [];
        for (var i = 0; i < N; i++) {
            var a = -Math.PI / 2 + i * Math.PI / 4;
            pts.push({ x: 260 + 178 * Math.cos(a), y: 240 + 162 * Math.sin(a) });
        }
        var lines = pts.map(function () { return Line(S, 260, 240, 260, 240, { dash: '5 6', stroke: LINE }); });
        var sw = Sweep(S, 'ms', [[0.1, 0], [0.5, 0.75], [0.9, 0]], 72, 2);
        var mr = sw.rect(192, 221, 136, 46, 10, 5);
        var chip = Chip(S, { x: 174, y: 220, w: 172, h: 48, r: 10, fs: 19, ls: 0.7, text: 'MATCHING...', bg: CHIP, gap: 0 });
        chip.tx.style.paddingInline = '12px';
        var discs = pts.map(function (p, i) {
            return Disc(S, { x: p.x, y: p.y, d: size, html: o.brands ? brandHTML(i, 34) : personHTML(i, 34, o.photos) });
        });
        return {
            loop: loop, hold: 205,
            render: function (f) {
                var e = f % loop;
                var rr = ip(e, 79, 110, outCubic);
                var oo = ip(e, 240, 270, inOutCubic);
                var ii = clamp(kf(oo, [0.4, 1], [0, 1]), 0, 1);
                var vet = ip(e, 150, 175, outCubic);
                var text;
                if (e < 110) text = scramble(e, rr, 'MATCHING...', o.foundText);
                else if (e < 150) text = o.foundText;
                else if (e < 240) text = scramble(e, vet, o.foundText, o.vettedText);
                else text = scramble(e, ii, o.vettedText, 'MATCHING...');
                var aa = ip(e, 78, 96, outCubic);
                var cc = e < 240 ? aa : 1 - oo;
                var width = e < 240 ? lerp(172, 136, aa) : lerp(136, 172, oo);
                var left = 260 - width / 2;
                var m = e < 240 ? 1 : 1 - oo;
                chip.set({ opacity: ip(e, 0, 6, outQuad) * (e < 240 ? 1 : 1), left: left, width: width, border: mixColor(RING_RGB, ACC_RGB, cc), text: text, scale: 1 });
                /* border sweep while scanning */
                var h = Math.floor(e / 26), y = e - 26 * h;
                var scanning = e < 78 && h >= 0 && h < 3;
                var g = scanning ? ip(y, 0, 26, sweepEase) : 0;
                var b = h % 2 === 0 ? lerp(196, 292, g) : lerp(292, 196, g);
                mr.setAttribute('x', left + 1); mr.setAttribute('width', width - 2);
                sw.update(b, scanning ? 0.95 : 0, scanning ? 0.3 : 0);
                var dim = ip(e, 152, 172, inOutCubic);
                pts.forEach(function (p, i) {
                    var s = 96 + 6 * i;
                    var t = ip(e, s, s + 9, outCubic);
                    var keep = KEEP.indexOf(i) >= 0;
                    var lop = m * (keep ? 1 : lerp(1, 0.25, dim));
                    lines[i].set(260, 240, lerp(260, p.x, t), lerp(240, p.y, t), t > 0 ? lop : 0);
                    var sc = ip(e, s + 1, s + 11, outBack(1.3));
                    var op = ip(e, s + 2, s + 12, outCubic);
                    var inner = discs[i].inner;
                    var innerScale = lerp(0.6, 1, op);
                    put(inner, { opacity: op.toFixed(3), transform: 'scale(' + innerScale.toFixed(3) + ')' });
                    var fadeOthers = keep ? 1 : lerp(1, 0.3, dim);
                    discs[i].set({
                        scale: sc, opacity: m * fadeOthers * (sc > 0.01 ? 1 : 0),
                        border: keep ? mixColor(RING_RGB, ACC_RGB, dim) : RING
                    });
                    put(discs[i].el, { filter: keep ? 'none' : 'grayscale(' + (dim).toFixed(2) + ')' });
                });
            }
        };
    };

    /* C. Introduction / offer: top chip, ring of icons, light runs down, deal chip lands */
    C.deal = function (S, o) {
        var loop = 150;
        var cx = 260, ringY = 255;
        var rings = [68, 148, 228].map(function (r) {
            var c = svgEl('circle', { cx: cx, cy: ringY, r: r, fill: 'none', stroke: 'rgba(11,28,46,0.05)', 'stroke-width': 2 });
            S.svg.appendChild(c);
            return c;
        });
        var disc = [{ x: 260, y: 190 }, { x: 142, y: 300 }, { x: 378, y: 300 }];
        var L0 = Line(S, 260, 84, 260, 190 - 48, { stroke: 'rgba(0,114,184,0.28)', width: 1.5 });
        var d1 = Line(S, 260, 190, 142, 300);
        var d2 = Line(S, 260, 190, 378, 300);
        var u1 = Line(S, 142, 348, 196, 392);
        var u2 = Line(S, 378, 348, 324, 392);
        var sw = Sweep(S, 'ds', [[0.24, 0], [0.54, 0.95], [0.76, 0]], 110, 2.2);
        sw.rect(161, 35, 198, 52, 12, 2);
        sw.line(260, 84, 260, 142);
        sw.line(260, 190, 142, 300);
        sw.line(260, 190, 378, 300);
        sw.line(142, 348, 196, 392);
        sw.line(378, 348, 324, 392);
        var top = Chip(S, { x: 160, y: 34, w: 200, h: 54, r: 12, icon: o.topIcon, text: o.topText, fs: 17, ls: 0.8, iconColor: ACC, is: 22 });
        var ds = disc.map(function (p, i) {
            return Disc(S, { x: p.x, y: p.y, d: 96, bw: 2, bg: '#fff', html: '<div class="pc-discin">' + ico(o.discs[i], 32, ACC) + '</div>' });
        });
        var done = Chip(S, { x: 135, y: 392, w: 250, h: 60, r: 16, text: o.doneText, fs: 18, ls: 0.9, bg: CHIP, border: 'rgba(0,114,184,0.27)', gap: 14 });
        var chk = document.createElement('span');
        chk.className = 'pc-chk';
        chk.innerHTML = CHECK_SVG;
        done.el.insertBefore(chk, done.tx);
        return {
            loop: loop, hold: 128,
            render: function (f) {
                var g = fadeIO(f, loop, 6, 136);
                var breath = 1 + 0.025 * Math.sin(f / loop * Math.PI * 2);
                rings.forEach(function (c, i) {
                    c.setAttribute('r', ([68, 148, 228][i] * (breath + 0.01 * Math.sin(0.03 * f + i))).toFixed(2));
                    c.setAttribute('opacity', g.toFixed(3));
                });
                var tp = pop(f, 0, sprCfg(16, 9, 125, 0.9));
                top.set({ scale: tp.s, opacity: tp.o * g });
                var t0 = ip(f, 10, 40, outCubic);
                L0.set(260, 84, 260, lerp(84, 142, t0), t0 > 0 ? g : 0);
                var dp = [pop(f, 30, sprCfg(16, 8.5, 130, 0.85)), pop(f, 44, sprCfg(16, 8.5, 130, 0.85)), pop(f, 50, sprCfg(16, 8.5, 130, 0.85))];
                ds.forEach(function (d, i) { d.set({ scale: dp[i].s, opacity: dp[i].o * g }); });
                var t1 = ip(f, 46, 68, outCubic);
                d1.set(260, 190, lerp(260, 142, t1), lerp(190, 300, t1), t1 > 0 ? g : 0);
                d2.set(260, 190, lerp(260, 378, t1), lerp(190, 300, t1), t1 > 0 ? g : 0);
                var t2 = ip(f, 78, 94, outCubic);
                u1.set(142, 348, lerp(142, 196, t2), lerp(348, 392, t2), t2 > 0 ? g : 0);
                u2.set(378, 348, lerp(378, 324, t2), lerp(348, 392, t2), t2 > 0 ? g : 0);
                sw.update(lerp(34, 470, ip(f, 0, 100, inOutQuad)), f < 106 ? g : 0);
                var np = pop(f, 96, sprCfg(18, 9, 120, 0.9));
                done.set({ scale: np.s, opacity: np.o * g });
                put(chk, { opacity: np.o.toFixed(3) });
            }
        };
    };

    /* D. Review: preview chip -> video -> approved -> ready */
    C.review = function (S, o) {
        var loop = 197;
        var L1 = Line(S, 260, 72, 260, 72, { dash: '1 7', stroke: DOT });
        var L2 = Line(S, 260, 220, 260, 220, { dash: '1 7', stroke: DOT });
        var top = Chip(S, { x: 152, y: 24, w: 216, h: 48, r: 10, icon: o.topIcon, text: o.topText, fs: 16, ls: 0.9, is: 21 });
        var vid = node(S, {
            left: '74px', top: '116px', width: '372px', height: '208px', borderRadius: '12px', overflow: 'hidden',
            background: 'linear-gradient(135deg,#0b1c2e 0%,#0a4a7a 60%,#0072b8 100%)', opacity: '0', transformOrigin: '50% 50%',
            boxShadow: '0 8px 24px rgba(11,28,46,0.18)'
        },
            '<div class="pc-vbar" style="top:16px;left:18px;width:120px"></div><div class="pc-vbar" style="top:32px;left:18px;width:70px;opacity:.5"></div>' +
            '<div class="pc-play"><svg viewBox="0 0 24 24" width="26" height="26"><path d="M8.5 5.5v13l10-6.5z" fill="#fff"/></svg></div>' +
            '<div class="pc-vprog"><i></i></div>');
        var prog = vid.querySelector('.pc-vprog i');
        var play = vid.querySelector('.pc-play');
        var appr = Chip(S, { x: 141, y: 176, w: 238, h: 56, r: 18, icon: 'check_circle', text: o.approveText, fs: 16, ls: 0.9, bg: '#eaf4fc', iconColor: RING, is: 22 });
        var fin = Chip(S, { x: 117, y: 390, w: 286, h: 48, r: 10, icon: o.finalIcon, text: o.finalText, fs: 16, ls: 0.9, iconColor: RING, is: 21 });
        return {
            loop: loop, hold: 160,
            render: function (f) {
                var e = f % loop;
                var i = 1 - ip(e, 184, 196, inOutCubic);
                var tp = pop(e, 0, sprCfg(15, 9, 125, 0.9));
                top.set({ scale: tp.s, opacity: tp.o * i, iconColor: mixColor(RING_RGB, ACC_RGB, ip(e, 30, 42, inOutCubic)) });
                var l1 = ip(e, 30, 50, outCubic);
                L1.set(260, 72, 260, lerp(72, 220, l1), l1 > 0 ? i : 0);
                var vp = pop(e, 50, sprCfg(20, 9, 118, 0.9));
                var showV = e >= 50 && e <= 196;
                put(vid, { opacity: showV ? (vp.o * i).toFixed(3) : '0', transform: 'scale(' + vp.s.toFixed(3) + ')' });
                put(prog, { width: (ip(e, 55, 150, linear) * 100).toFixed(1) + '%' });
                put(play, { opacity: (1 - ip(e, 60, 70)).toFixed(3) });
                var ap = pop(e, 65, sprCfg(12, 9, 125, 0.9));
                appr.set({ scale: ap.s, opacity: (e >= 65 && e <= 196) ? ap.o * i : 0, iconColor: mixColor(RING_RGB, ACC_RGB, ip(e, 92, 102, inOutCubic)) });
                var l2 = ip(e, 92, 112, outCubic);
                L2.set(260, 220, 260, lerp(220, 390, l2), l2 > 0 ? i : 0);
                var fp = pop(e, 112, sprCfg(12, 9, 125, 0.9));
                fin.set({ scale: fp.s, opacity: fp.o * i, iconColor: mixColor(RING_RGB, ACC_RGB, ip(e, 184, 193, inOutCubic)) });
            }
        };
    };

    /* E. Reporting: collecting -> analysing (spinner to check) -> three results, one wins */
    C.report = function (S, o) {
        var loop = 300, hMid = 122;
        var av = [{ x: 168, y: 322, d: 76 }, { x: 260, y: 304, d: 84 }, { x: 352, y: 322, d: 76 }];
        var L1 = Line(S, 260, 76, 260, 76, { dash: '1 7', stroke: DOT });
        var L2 = Line(S, 260, hMid, 260, hMid, { dash: '1 7', stroke: DOT });
        var s1 = Sweep(S, 'r1', [[0.24, 0], [0.54, 0.95], [0.76, 0]], 110, 2.2);
        var s2 = Sweep(S, 'r2', [[0.24, 0], [0.54, 0.95], [0.76, 0]], 110, 2.2);
        var m1 = s1.line(260, 76, 260, 76);
        var m2 = s2.line(260, hMid, 260, hMid);
        function statusChip(x, y, w, text, idKey) {
            var c = Chip(S, { x: x, y: y, w: w, h: 52, r: 10, text: text, fs: 16, ls: 0.9, gap: 12 });
            var box = document.createElement('span');
            box.className = 'pc-spinbox';
            box.innerHTML = '<span class="pc-spin">' + spinnerSVG(S.uid + idKey) + '</span><span class="pc-done">' + CHECK_SVG + '</span>';
            c.el.insertBefore(box, c.tx);
            c.spin = box.firstChild; c.done = box.lastChild;
            return c;
        }
        var c1 = statusChip(147, 24, 226, 'COLLECTING DATA', 'sa');
        var c2 = statusChip(138, 122, 244, 'ANALYZING RESULTS', 'sb');
        var ds = av.map(function (a, i) {
            return Disc(S, { x: a.x, y: a.y, d: a.d, bw: 2, html: '<div class="pc-avin">' + (o.brands ? brandHTML(i + 2, 34) : personHTML(i + 1, 34, o.photos)) + '</div>' });
        });
        var win = Chip(S, { x: 149, y: 360, w: 232, h: 46, r: 10, text: o.finalText, fs: 16, ls: 1.1, bg: ACC, border: ACC, gap: 0 });
        win.tx.style.color = '#fff';
        return {
            loop: loop, hold: 250,
            render: function (f) {
                var oo = f % loop;
                var i = 1 - ip(oo, 282, 299, inOutCubic);
                /* chip 1 */
                var n = ip(oo, 0, 16, outBack(1.05));
                var p1 = oo >= 40;
                var sc1 = p1 ? lerp(1.1, 1, spring(oo - 40, sprCfg(20, 9, 125, 0.9))) : lerp(0.6, 1, n);
                c1.set({ scale: sc1, opacity: n * i });
                put(c1.spin, { opacity: p1 ? '0' : '1', transform: 'rotate(' + lerp(0, 720, ip(oo, 0, 40, linear)).toFixed(1) + 'deg)' });
                put(c1.done, { opacity: p1 ? '1' : '0' });
                /* line 1 + sweep 1 */
                var j = ip(oo, 40, 80, outCubic);
                var v = lerp(76, hMid, j);
                setLine(m1, 260, 76, 260, v);
                L1.set(260, 76, 260, v, j > 0 ? i : 0);
                var T = clamp(kf(oo, [40, 50, 146], [0, 1, 1]), 0, 1);
                s1.update(lerp(-34, v + 110, j), T * i, T * i * 0.35);
                /* chip 2 */
                var S2 = ip(oo, 50, 66, outBack(1.05));
                var p2 = oo >= 138;
                var sc2 = p2 ? lerp(1.1, 1, spring(oo - 138, sprCfg(20, 9, 125, 0.9))) : lerp(0.6, 1, S2);
                c2.set({ scale: sc2, opacity: S2 * i });
                put(c2.spin, { opacity: p2 ? '0' : '1', transform: 'rotate(' + lerp(0, 720, ip(oo, 50, 138, linear)).toFixed(1) + 'deg)' });
                put(c2.done, { opacity: p2 ? '1' : '0' });
                /* line 2 + sweep 2 */
                var M = ip(oo, 146, 202, outCubic);
                var ve = lerp(hMid, av[1].y, M);
                setLine(m2, 260, hMid, 260, ve);
                L2.set(260, hMid, 260, ve, M > 0 ? i : 0);
                var A = clamp(kf(oo, [146, 156, 202, 210], [0, 1, 1, 0]), 0, 1);
                s2.update(lerp(12, ve + 110, M), M > 0 ? A * i : 0, M > 0 ? A * i * 0.35 : 0);
                /* three results */
                var B = ip(oo, 202, 210, inOutCubic);
                [0, 1, 2].forEach(function (k) {
                    var rv = ip(oo, 72 + 22 * k, 72 + 22 * k + 20, outCubic);
                    var mid = k === 1;
                    var op = rv * i * (mid ? 1 : lerp(1, 0.3, B));
                    ds[k].set({ scale: lerp(0.8, 1, rv), opacity: op, border: mid ? mixColor(RING_RGB, ACC_RGB, B) : RING });
                });
                /* winner tag */
                var N = spring(oo - 204, sprCfg(18, 10, 115, 0.95));
                win.set({ scale: lerp(0.6, 1, N), opacity: clamp(kf(N, [0, 0.35, 1], [0, 1, 1]), 0, 1) * i });
            }
        };
    };

    /* ======================================================================
     * Player: runs one composition at 30 fps, only while visible
     * ====================================================================== */
    var players = [], raf = 0;
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function Player(host) {
        this.host = host;
        this.name = host.getAttribute('data-comp');
        this.opt = {};
        try { this.opt = JSON.parse(host.getAttribute('data-opt') || '{}'); } catch (e) { /* keep defaults */ }
        this.built = false;
        this.playing = false;
        this.t0 = 0;
        this.f = -1;
        this.paused = 0;
    }
    Player.prototype.build = function () {
        if (this.built) return;
        this.built = true;
        this.host.innerHTML = '';
        this.S = Stage(this.host);
        var comp = C[this.name];
        this.comp = comp(this.S, this.opt);
        this.fit();
        this.draw(reduce ? this.comp.hold : this.comp.hold);
        this.host.classList.add('pc-ready');
    };
    Player.prototype.fit = function () {
        var w = this.host.clientWidth;
        if (w > 0 && this.S) this.S.root.style.transform = 'scale(' + (w / SW).toFixed(5) + ')';
    };
    Player.prototype.draw = function (f) {
        if (!this.comp) return;
        this.f = f;
        this.comp.render(f);
    };
    Player.prototype.play = function () {
        if (reduce) { this.build(); return; }
        this.build();
        if (this.playing) return;
        this.playing = true;
        this.t0 = performance.now() - this.paused * 1000 / FPS;
        wake();
    };
    Player.prototype.pause = function () {
        if (!this.playing) return;
        this.playing = false;
        this.paused = this.f < 0 ? 0 : this.f;
    };
    Player.prototype.restart = function () {
        this.paused = 0;
        this.t0 = performance.now();
        this.f = -1;
        if (this.built && !this.playing && this.visible) this.play();
    };
    Player.prototype.tick = function (now) {
        var f = Math.floor((now - this.t0) * FPS / 1000) % this.comp.loop;
        if (f !== this.f) this.draw(f);
    };
    function tick(now) {
        raf = 0;
        var any = false;
        for (var i = 0; i < players.length; i++) {
            if (players[i].playing) { any = true; players[i].tick(now); }
        }
        if (any) raf = requestAnimationFrame(tick);
    }
    function wake() { if (!raf) raf = requestAnimationFrame(tick); }

    var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
            var p = en.target._player;
            p.visible = en.isIntersecting;
            if (en.isIntersecting) p.play(); else p.pause();
        });
    }, { rootMargin: '120px 0px' }) : null;
    var ro = 'ResizeObserver' in window ? new ResizeObserver(function (entries) {
        entries.forEach(function (en) { if (en.target._player) en.target._player.fit(); });
    }) : null;

    /* ======================================================================
     * Section: audience tabs, staggered reveal, carousel controls
     * ====================================================================== */
    function initSection(sec) {
        sec.classList.add('pc-js');
        var tabs = [].slice.call(sec.querySelectorAll('.pc-tabbtn'));
        var ind = sec.querySelector('.pc-ind');
        var panels = [].slice.call(sec.querySelectorAll('[data-pc-panel]'));
        var prev = sec.querySelector('.pc-prev'), next = sec.querySelector('.pc-next');
        var ctas = [].slice.call(sec.querySelectorAll('[data-pc-cta]'));
        var aud = 'brand';
        var revealed = false;
        /* single-audience pages have no tabs: the section stays on its own side */
        var locked = tabs.length === 0;
        var lockAud = panels[0] ? panels[0].getAttribute('data-pc-panel') : 'brand';

        panels.forEach(function (pn) {
            [].forEach.call(pn.querySelectorAll('.pc-visual'), function (h) {
                var p = new Player(h);
                h._player = p;
                players.push(p);
                if (io) io.observe(h);
                if (ro) ro.observe(h);
                if (!io) p.play();
            });
        });
        panels.forEach(function (pn) { pn.classList.add('pc-pending'); });

        function track() { return sec.querySelector('[data-pc-panel="' + aud + '"] .pc-track'); }
        function moveInd() {
            var b = tabs.filter(function (t) { return t.getAttribute('data-aud') === aud; })[0];
            if (!b || !ind) return;
            ind.style.left = b.offsetLeft + 'px';
            ind.style.width = b.offsetWidth + 'px';
        }
        function arrows() {
            var t = track();
            if (!t) return;
            var start = t.scrollLeft <= 1, end = t.scrollLeft + t.clientWidth >= t.scrollWidth - 1;
            if (prev) prev.disabled = start;
            if (next) next.disabled = end;
            t.classList.toggle('pc-atend', end);
        }
        function reveal(panel) {
            panel.classList.remove('pc-pending');
            if (reduce || !panel.animate) return;
            var steps = panel.querySelectorAll('.pc-step'), tapes = panel.querySelectorAll('.pc-tag');
            [].forEach.call(steps, function (s, i) {
                s.animate([{ opacity: 0, transform: 'translateY(50px) scale(0.95)' }, { opacity: 1, transform: 'none' }],
                    { duration: 700, delay: i * 80, easing: 'cubic-bezier(0.215,0.61,0.355,1)', fill: 'backwards' });
            });
            [].forEach.call(tapes, function (t, i) {
                t.animate([{ transform: 'rotate(-6deg) scaleX(0)' }, { transform: 'rotate(-2deg) scaleX(1)' }],
                    { duration: 500, delay: 250 + i * 80, easing: 'cubic-bezier(0.34,1.56,0.64,1)', fill: 'backwards' });
            });
        }
        function setAud(a, fromUser) {
            if (a === aud && revealed === true && !fromUser) return;
            var changed = a !== aud;
            aud = a;
            tabs.forEach(function (t) {
                var on = t.getAttribute('data-aud') === a;
                t.classList.toggle('pc-on', on);
                t.setAttribute('aria-selected', on ? 'true' : 'false');
            });
            moveInd();
            panels.forEach(function (pn) {
                var on = pn.getAttribute('data-pc-panel') === a;
                pn.hidden = !on;
            });
            ctas.forEach(function (c) { c.hidden = c.getAttribute('data-pc-cta') !== a; });
            var t = track();
            if (t) t.scrollLeft = 0;
            if (changed && revealed) {
                var pn = sec.querySelector('[data-pc-panel="' + a + '"]');
                pn.classList.add('pc-pending');
                void pn.offsetWidth;
                reveal(pn);
                [].forEach.call(pn.querySelectorAll('.pc-visual'), function (h) { h._player.restart(); });
            }
            arrows();
        }

        tabs.forEach(function (t) {
            t.addEventListener('click', function () {
                var a = t.getAttribute('data-aud');
                if (window.GV) window.GV.set(a, { source: 'process' }); else setAud(a, true);
            });
        });
        if (prev) prev.addEventListener('click', function () { track().scrollBy({ left: -420, behavior: reduce ? 'auto' : 'smooth' }); });
        if (next) next.addEventListener('click', function () { track().scrollBy({ left: 420, behavior: reduce ? 'auto' : 'smooth' }); });
        panels.forEach(function (pn) { pn.querySelector('.pc-track').addEventListener('scroll', arrows, { passive: true }); });
        window.addEventListener('resize', function () { moveInd(); arrows(); });

        /* reveal once when the cards come into view (about 75% down the viewport) */
        if ('IntersectionObserver' in window) {
            var rv = new IntersectionObserver(function (en) {
                if (en[0].isIntersecting && !revealed) {
                    revealed = true;
                    reveal(sec.querySelector('[data-pc-panel="' + aud + '"]'));
                    rv.disconnect();
                }
            }, { rootMargin: '0px 0px -25% 0px' });
            rv.observe(sec.querySelector('.pc-panels'));
        } else {
            revealed = true;
            panels.forEach(function (pn) { pn.classList.remove('pc-pending'); });
        }

        sec._setAud = setAud;
        if (window.GV && !locked) window.GV.on(function (a) { setAud(a); });
        if (document.fonts && document.fonts.load) {
            document.fonts.load('24px "Material Symbols Outlined"').then(function () { sec.classList.add('pc-fonts'); moveInd(); });
            setTimeout(function () { sec.classList.add('pc-fonts'); }, 2500);
        } else sec.classList.add('pc-fonts');
        setAud(locked ? lockAud : (window.GV ? window.GV.get() : 'brand'), true);
        setTimeout(moveInd, 60);
    }

    window.GVProcess = {
        init: function () { [].forEach.call(document.querySelectorAll('.pc-section'), initSection); },
        players: players,
        compositions: C
    };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', window.GVProcess.init);
    else window.GVProcess.init();
})();
