#!/usr/bin/env python3
"""Generate nine Gratovo test pages, one per competitor layout, into research/layouts/.

Gratovo brokers deals between AI/SaaS brands and creators, so every page speaks to both sides
(two hero paths, a For Creators section, a form for each). Each page borrows one competitor's section
order and signature effects (see research/competitor-effects.md) but uses Gratovo's copy and colours.
Shared copy lives in the constants below so every layout says the same things. Sections that depend on
proof Gratovo does not have (client logos, testimonials, real creator rosters) are left out or replaced
with clearly labelled examples. No pricing, rates, or payment handling is mentioned anywhere.

Usage:   python research/scripts/build-layout-tests.py
Output:  research/layouts/*.html and research/layouts/index.html (open in a browser)
"""
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "research" / "layouts"
SRC_INDEX = ROOT / "index.html"
ASSET = "../../"  # layouts live in research/layouts/

# ---------------------------------------------------------------- shared copy
CTA = "Find My Creators"          # brand button
CTA_C = "Get Brand Deals"         # creator button
EMAIL = "mustafa@gratovo.com"
HEAD_PARTS = ("Connecting AI Brands With the ", "Creators Their Customers Trust", ".")
HEADLINE = "".join(HEAD_PARTS)
SUB = "Brands get vetted AI creators. Creators get brand deals that fit."
BODY = "No cold emails. No chasing replies. We make the introduction and keep the conversation moving."
NOTE = "We reply within 24 hours."
CTA_SUB = "Brands, tell us what you're promoting. Creators, tell us about your channel. We reply within 24 hours."

BENEFITS = [
    ("schedule", "Zero Outreach",
     "No searching, no cold emails, no waiting on replies. We contact the creators, and you only hear about the ones worth your time."),
    ("verified", "Vetted, Not Guessed",
     "Before you see a name, we check real average views, engagement, and audience location. No fake audiences. No bad-fit channels."),
    ("visibility", "Nothing Goes Live Unseen",
     "We check the draft against your product first. Then you approve it before it posts."),
]
CREATOR_BENEFITS = [
    ("handshake", "Brand Deals Come to You",
     "No cold outreach to brands. We bring AI and SaaS sponsorship deals to creators who fit."),
    ("person", "One Contact, Less Back-and-Forth",
     "No long media-kit requests or endless email threads. One person to talk to."),
]
CREATOR_STEPS = [
    ("Tell us about your channel", "Your channel link and what you cover. It takes two minutes."),
    ("We put you forward", "We introduce you to AI and SaaS brands that fit your audience."),
    ("You hear from us", "When a brand deal fits, we reach out with the details."),
]
STATS = [
    ("30K+", "average views per video"),
    ("3-8%", "real engagement from active viewers"),
    ("35%+", "of the audience in your target country"),
    ("1-3", "creators recommended for your product, not 200"),
]
SERVICES = [
    ("Creator search", "We find AI creators who already cover tools like yours."),
    ("Vetting", "Real views, real engagement, and the right audience location."),
    ("Introductions", "We reach out to the creators and keep the conversation moving."),
    ("Contracts", "Deliverables, dates, and usage rights locked in before anything goes live."),
    ("Script and draft review", "You see and approve the video before it posts."),
    ("Go-live check", "We confirm it posts on schedule and send you the early performance numbers."),
]
STEPS5 = [
    ("Tell us what you sell", "A short message about your product and who it's for. We reply within 24 hours."),
    ("We recommend the best fit", "You get 1 to 3 vetted creators with their views, engagement, and audience details."),
    ("We agree the deal", "Deliverables and dates are agreed and put in writing."),
    ("You approve the video", "We review the script and draft, then send it to you for sign-off."),
    ("It goes live", "We confirm it posts and send you the early performance numbers."),
]
STEPS3 = [
    STEPS5[0], STEPS5[1],
    ("We take it from there",
     "Contracts, scripts, and posting dates. You approve the video, and it goes live. Most deals go live within about a month."),
]
STEPS4 = [
    ("Request", "Tell us what you sell and who it's for."),
    ("Match", "We recommend the 1 to 3 vetted AI creators that fit your product."),
    ("Agree", "We agree deliverables and dates and put everything in writing."),
    ("Launch", "You approve the video. We make sure it goes live."),
]
PLATFORMS = ["YouTube", "LinkedIn", "X", "Newsletters"]
FAQ = [
    ("What do you need from me?",
     "Brands: a short message about your product and who it's for. Creators: your channel link and what you cover. We take it from there."),
    ("How many creators do brands get to choose from?",
     "One to three. Each one has passed our checks on views, engagement, and audience location, so you're choosing between good options instead of sorting a spreadsheet."),
    ("I'm a creator. What happens after I apply?",
     "We look at your channel. When an AI or SaaS brand fits your audience, we reach out with the details."),
    ("Can't we just do this ourselves?",
     "You can. It means searching for creators, checking their numbers, writing to them, drafting contracts and reviewing scripts. We do all of that so your team doesn't have to."),
    ("How fast does it happen?",
     "We reply within 24 hours. Most deals go live within about a month of signing."),
]
EXAMPLES = [
    ("Creator A", "AI tutorials, YouTube", "42K", "5.1%", "46%"),
    ("Creator B", "Automation tips, LinkedIn", "31K", "4.2%", "41%"),
    ("Creator C", "AI news, newsletter and X", "58K", "3.6%", "52%"),
]
LAYOUTS = []  # (file, name, blurb) filled as pages are registered


# ---------------------------------------------------------------- shared head / css / js
def tailwind_config():
    src = SRC_INDEX.read_text(encoding="utf-8")
    m = re.search(r'<script id="tailwind-config">.*?</script>', src, re.S)
    return m.group(0)


BASE_CSS = """
html { scroll-behavior: smooth; }
body { -webkit-font-smoothing: antialiased; }
.material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
.icon-fill { font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
.reveal { opacity: 0; transform: translateY(26px); transition: opacity .7s ease, transform .7s ease; }
.reveal.in { opacity: 1; transform: none; }
.marquee { overflow: hidden; white-space: nowrap; }
.marquee-track { display: inline-flex; gap: 4rem; animation: marquee 26s linear infinite; padding-right: 4rem; }
@keyframes marquee { to { transform: translateX(-50%); } }
@keyframes floaty { 0%,100% { transform: translateY(0) rotate(var(--r,0deg)); } 50% { transform: translateY(-14px) rotate(var(--r,0deg)); } }
@keyframes drawline { to { stroke-dashoffset: 0; } }
@keyframes fadein { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
@keyframes scrollup { to { transform: translateY(-50%); } }
.layout-tag { position: fixed; left: 12px; bottom: 12px; z-index: 9999; font: 12px/1.3 system-ui, sans-serif; background: rgba(15,23,34,.88); color: #fff; padding: 6px 10px; border-radius: 999px; }
.layout-tag a { color: #9ad6f7; text-decoration: underline; margin-left: 6px; }
.step-panel[hidden] { display: none; }
@media (prefers-reduced-motion: reduce) {
  .reveal { opacity: 1; transform: none; transition: none; }
  *, *::before, *::after { animation: none !important; }
}
"""

BASE_JS = """
(function () {
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.12 }) : null;
  document.querySelectorAll('.reveal').forEach(function (el, i) {
    var d = el.getAttribute('data-delay'); if (d) el.style.transitionDelay = d + 'ms';
    if (io) io.observe(el); else el.classList.add('in');
  });
  document.querySelectorAll('[data-stepper]').forEach(function (root) {
    var panels = [].slice.call(root.querySelectorAll('.step-panel'));
    var tabs = [].slice.call(root.querySelectorAll('.step-tab'));
    var count = root.querySelector('[data-count]'); var i = 0;
    function show(n) {
      i = (n + panels.length) % panels.length;
      panels.forEach(function (p, k) { p.hidden = k !== i; });
      tabs.forEach(function (t, k) { t.setAttribute('aria-selected', k === i ? 'true' : 'false'); t.classList.toggle('is-active', k === i); });
      if (count) count.textContent = (i + 1) + ' of ' + panels.length;
    }
    tabs.forEach(function (t, k) { t.addEventListener('click', function () { show(k); }); });
    var p = root.querySelector('[data-prev]'), n = root.querySelector('[data-next]');
    if (p) p.addEventListener('click', function () { show(i - 1); });
    if (n) n.addEventListener('click', function () { show(i + 1); });
    show(0);
  });
  var prog = document.getElementById('scroll-progress');
  if (prog) {
    var num = document.getElementById('scroll-progress-num');
    var upd = function () {
      var h = document.documentElement.scrollHeight - innerHeight;
      var pct = h > 0 ? Math.min(100, Math.round(scrollY / h * 100)) : 0;
      prog.style.height = pct + '%'; if (num) num.textContent = pct;
    };
    addEventListener('scroll', upd, { passive: true }); upd();
  }
  var menuBtn = document.getElementById('menu-btn'), menu = document.getElementById('menu-overlay');
  if (menuBtn && menu) {
    var tgl = function () { var open = menu.classList.toggle('hidden'); menuBtn.setAttribute('aria-expanded', open ? 'false' : 'true'); };
    menuBtn.addEventListener('click', tgl);
    menu.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', tgl); });
  }
  var star = document.getElementById('stars');
  if (star) {
    for (var s = 0; s < 70; s++) {
      var d = document.createElement('i');
      d.style.cssText = 'position:absolute;border-radius:50%;background:#fff;left:' + Math.random() * 100 + '%;top:' + Math.random() * 100 +
        '%;width:' + (1 + Math.random() * 2) + 'px;height:' + (1 + Math.random() * 2) + 'px;opacity:' + (0.2 + Math.random() * 0.7) +
        ';animation:twinkle ' + (2 + Math.random() * 4) + 's ease-in-out ' + Math.random() * 3 + 's infinite';
      star.appendChild(d);
    }
  }
  var cp = document.getElementById('copy-email');
  if (cp) cp.addEventListener('click', function () {
    var st = document.getElementById('copy-email-status'), ic = document.getElementById('copy-email-icon');
    function done(ok) {
      st.textContent = ok ? 'Copied!' : 'Press Ctrl+C to copy';
      if (ok) ic.textContent = 'check';
      setTimeout(function () { st.textContent = ''; ic.textContent = 'content_copy'; }, 2500);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText('@@EMAIL@@').then(function () { done(true); }, function () { done(false); });
    else done(false);
  });
})();
""".replace("@@EMAIL@@", EMAIL)


def page(file, title, name, blurb, body_cls, css, body, extra_head=""):
    # Tailwind's text-size classes reset weight, so make big headings bold explicitly.
    for cls in ("font-headline-lg text-", "font-display-lg text-"):
        body = body.replace(cls, cls.replace(" text-", " font-bold text-"))
    head = f"""<!DOCTYPE html>
<html class="light" lang="en">
<head>
<meta charset="utf-8">
<meta content="width=device-width, initial-scale=1.0" name="viewport">
<meta name="robots" content="noindex, nofollow">
<title>{title}</title>
<link rel="icon" type="image/svg+xml" href="{ASSET}images/logo.svg">
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link rel="stylesheet" href="{ASSET}fonts/fonts.css">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="{ASSET}css/process-cards.css">
{extra_head}
{tailwind_config()}
<style>{BASE_CSS}{css}</style>
<noscript><style>.reveal{{opacity:1;transform:none}}</style></noscript>
</head>
<body class="{body_cls}">
{body}
<div class="layout-tag">Layout test: {name}<a href="index.html">all layouts</a></div>
<script>{BASE_JS}</script>
<script src="{ASSET}js/audience-tabs.js"></script>
<script src="{ASSET}js/process-cards.js"></script>
</body>
</html>
"""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / file).write_text(head, encoding="utf-8")
    LAYOUTS.append((file, name, blurb))
    print("wrote", file)


# ---------------------------------------------------------------- shared components
def wordmark(cls="text-2xl md:text-3xl"):
    return (f'<span class="wordmark {cls}" role="img" aria-label="Gratovo"><img src="{ASSET}images/logo-mark.svg" alt="">'
            '<span aria-hidden="true">ratovo</span></span>')


def mat(icon, cls="", fill=True):
    return f'<span class="material-symbols-outlined {"icon-fill " if fill else ""}{cls}">{icon}</span>'


FORM_STYLES = {
    "color": dict(
        inp="w-full py-3.5 px-5 rounded-full text-on-surface bg-white border-0 focus:ring-2 focus:ring-inverse-primary shadow-lg outline-none placeholder:text-secondary",
        area="w-full py-3.5 px-5 rounded-3xl text-on-surface bg-white border-0 focus:ring-2 focus:ring-inverse-primary shadow-lg outline-none placeholder:text-secondary",
        btn="bg-white text-primary-container hover:bg-surface-bright",
        pill="bg-white/20 hover:bg-white/30 text-white", txt="text-primary-fixed",
        card="bg-white/15 border border-white/30 rounded-3xl p-6 md:p-8", head="text-white", sub="text-white/85"),
    "light": dict(
        inp="w-full py-3.5 px-5 rounded-xl bg-white border border-outline-variant focus:ring-2 focus:ring-primary-container outline-none placeholder:text-secondary",
        area="w-full py-3.5 px-5 rounded-xl bg-white border border-outline-variant focus:ring-2 focus:ring-primary-container outline-none placeholder:text-secondary",
        btn="bg-primary-container text-on-primary hover:bg-primary",
        pill="bg-surface-container hover:bg-surface-container-high text-primary", txt="text-secondary",
        card="bg-white border border-outline-variant rounded-2xl p-6 md:p-8 shadow-sm", head="text-on-background", sub="text-secondary"),
    "dark": dict(
        inp="w-full py-3.5 px-5 rounded-full bg-white/10 border border-white/25 text-white focus:ring-2 focus:ring-primary-fixed-dim outline-none placeholder:text-white/60",
        area="w-full py-3.5 px-5 rounded-3xl bg-white/10 border border-white/25 text-white focus:ring-2 focus:ring-primary-fixed-dim outline-none placeholder:text-white/60",
        btn="bg-primary-container text-white hover:bg-primary",
        pill="bg-white/15 hover:bg-white/25 text-white", txt="text-white/80",
        card="bg-white/5 border border-white/15 rounded-3xl p-6 md:p-8", head="text-white", sub="text-white/70"),
}


GV_VARS = {
    "color": "",
    "light": "--gv-bg:#eaf4fc;--gv-bd:#c5d5e4;--gv-fg:#3e4c5e;--gv-on-fg:#fff;--gv-on-bg:#0072b8;--gv-ph:#4a5a6e;",
    "dark": "--gv-bg:rgba(255,255,255,.08);--gv-bd:rgba(255,255,255,.2);--gv-fg:rgba(255,255,255,.7);--gv-on-fg:#0b1c2e;--gv-on-bg:#fff;--gv-ph:rgba(255,255,255,.65);",
}
BRAND_OPTS = [("find-creators", "Find creators for my product", "What does your product do? One line is enough.", 0),
              ("specific-creator", "Work with a specific creator", "Which creator? A link works.", 1),
              ("scale", "Scale what's already working", "What's working so far? One line is enough.", 0),
              ("question", "I have a question first", "What would you like to know?", 1)]
CREATOR_OPTS = [("get-deals", "Get brand deals for my channel", "What do you cover? One line is enough.", 0),
                ("specific-brand", "Work with a specific brand", "Which brand? A link works.", 1),
                ("question", "I have a question first", "What would you like to know?", 1)]


def _options(opts):
    head = '<option value="" disabled selected>What&#39;s this about?</option>'
    return head + "".join(f'<option value="{v}" data-hint="{h}" data-need="{n}">{l}</option>' for v, l, h, n in opts)


def forms(style):
    """ONE tabbed card: I'm a brand (id=workwithus) / I'm a creator (id=creators), each with an inquiry dropdown, plus the copyable email."""
    s = FORM_STYLES[style]
    btn = f"self-center {s['btn']} py-3.5 px-8 rounded-full font-label-sm uppercase text-sm tracking-wider inline-flex items-center gap-2 shadow-lg transition hover:-translate-y-1 duration-200"
    hidden = '<input type="hidden" name="_captcha" value="false"><input type="hidden" name="_next" value="https://www.gratovo.com/">'
    sel = s["inp"]

    brand = f"""<div id="workwithus" role="tabpanel" data-gv-panel="brand" class="scroll-mt-28">
<p class="{s['sub']} mb-5">Tell us what you're promoting.</p>
<form action="https://formsubmit.co/{EMAIL}" method="POST" class="gv-form flex flex-col gap-3" data-who="brand request">{hidden}
<input type="hidden" name="_subject" value="New brand request from the website">
<input type="text" name="name" placeholder="Your name / company" required class="{s['inp']}">
<input type="email" name="email" placeholder="Your email" required class="{s['inp']}">
<select name="inquiry" required aria-label="What is this about?" class="{sel}" style="padding-right:3rem">{_options(BRAND_OPTS)}</select>
<textarea name="message" rows="2" placeholder="Anything we should know? (optional)" class="{s['area']}"></textarea>
<button type="submit" class="{btn}">{CTA} {mat('send', '', False)}</button></form></div>"""
    creator = f"""<div id="creators" role="tabpanel" data-gv-panel="creator" class="scroll-mt-28" hidden>
<p class="{s['sub']} mb-5">Tell us about your channel.</p>
<form action="https://formsubmit.co/{EMAIL}" method="POST" class="gv-form flex flex-col gap-3" data-who="creator application">{hidden}
<input type="hidden" name="_subject" value="New creator application from the website">
<input type="text" name="name" placeholder="Your name / channel name" required class="{s['inp']}">
<input type="email" name="email" placeholder="Your email" required class="{s['inp']}">
<input type="text" name="channel" placeholder="Your channel link" required class="{s['inp']}">
<select name="inquiry" required aria-label="What is this about?" class="{sel}" style="padding-right:3rem">{_options(CREATOR_OPTS)}</select>
<textarea name="message" rows="2" placeholder="Anything we should know? (optional)" class="{s['area']}"></textarea>
<button type="submit" class="{btn}">{CTA_C} {mat('send', '', False)}</button></form></div>"""
    return f"""<div class="max-w-xl mx-auto">
<div id="contact-card" class="scroll-mt-28 {s['card']} text-left" style="{GV_VARS[style]}">
<div class="gv-tabs" role="tablist" aria-label="I am a"><button type="button" role="tab" class="gv-tabbtn gv-on" data-aud="brand" aria-selected="true" aria-controls="workwithus">I'm a brand</button><button type="button" role="tab" class="gv-tabbtn" data-aud="creator" aria-selected="false" aria-controls="creators">I'm a creator</button><span class="gv-ind" aria-hidden="true"></span></div>
{brand}{creator}</div>
<div class="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3 {s['txt']}">
<span class="font-body-md">Prefer email?</span>
<button type="button" id="copy-email" aria-label="Copy email address {EMAIL}" class="inline-flex items-center gap-2 {s['pill']} rounded-full py-2 px-5 font-label-sm transition-colors">
<span>{EMAIL}</span><span id="copy-email-icon" class="material-symbols-outlined text-base">content_copy</span></button>
<span id="copy-email-status" class="font-label-sm" role="status"></span>
</div></div>"""


def hero_buttons(primary, secondary, wrap="mt-10 flex flex-wrap gap-4"):
    return (f'<div class="{wrap}"><a href="#workwithus" class="{primary}">{CTA}</a>'
            f'<a href="#creators" class="{secondary}">{CTA_C}</a></div>')


THEMES = {
    "dark": dict(wrap="", h="text-white", p="text-white/70", card="bg-white/5 border border-white/15 rounded-2xl",
                 eye="text-primary-fixed-dim", ico="bg-primary-container text-white", num="text-primary-fixed-dim",
                 btn="bg-primary-container text-white"),
    "light": dict(wrap="", h="text-on-background", p="text-secondary", card="bg-white border border-outline-variant rounded-2xl shadow-sm",
                  eye="text-primary-container", ico="bg-primary-container text-white", num="text-primary-container",
                  btn="bg-primary-container text-white"),
    "color": dict(wrap="", h="text-[#0b1623]", p="text-[#0b1623]/90", card="bg-white/25 border border-white/40 rounded-2xl",
                  eye="text-[#0b1623]", ico="bg-[#0b1623] text-white", num="text-[#0b1623]",
                  btn="bg-[#0b1623] text-white"),
}


def creator_section(theme, id_="for-creators", extra_cls="", head_cls=""):
    t = THEMES[theme]
    cards = "".join(
        f'<div class="reveal {t["card"]} p-7" data-delay="{i*100}"><div class="w-12 h-12 rounded-xl {t["ico"]} flex items-center justify-center mb-4">{mat(ic, "text-2xl")}</div>'
        f'<h3 class="font-headline-md {t["h"]} mb-2">{ti}</h3><p class="{t["p"]}">{d}</p></div>'
        for i, (ic, ti, d) in enumerate(CREATOR_BENEFITS))
    steps = "".join(
        f'<div class="reveal" data-delay="{i*100}"><p class="font-label-sm {t["num"]} mb-1">0{i+1}</p><h4 class="font-semibold {t["h"]}">{ti}</h4><p class="{t["p"]} text-sm">{d}</p></div>'
        for i, (ti, d) in enumerate(CREATOR_STEPS))
    return f"""<section id="{id_}" class="max-w-container-max mx-auto px-6 md:px-12 py-20 {extra_cls}">
<div class="text-center max-w-3xl mx-auto mb-10"><p class="font-label-sm uppercase tracking-widest {t['eye']} mb-3 reveal">For creators</p>
<h2 class="font-headline-lg text-3xl md:text-5xl {t['h']} {head_cls} reveal">Brand deals that fit your channel.</h2>
<p class="{t['p']} mt-4 reveal">Already making content about AI and software? We put you in front of the brands that fit your audience.</p></div>
<div class="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto mb-10">{cards}</div>
<div class="grid sm:grid-cols-3 gap-6 max-w-4xl mx-auto mb-10">{steps}</div>
<div class="text-center"><a href="#creators" class="inline-flex {t['btn']} rounded-full px-8 py-4 font-label-sm uppercase tracking-wider">{CTA_C}</a></div></section>"""


def footer(dark=False):
    cls = "bg-[#0b1623] border-white/10 text-white/70" if dark else "bg-surface border-outline-variant text-secondary"
    return f"""<footer class="{cls} border-t py-10"><div class="max-w-container-max mx-auto px-grid-gutter flex flex-col md:flex-row justify-between items-center gap-6">
<p class="font-label-sm uppercase text-center md:text-left">© 2026 Gratovo. Connecting AI brands with the right creators.</p>
<nav class="flex gap-6 font-label-sm uppercase"><a class="hover:opacity-100 opacity-80" href="{ASSET}privacy-policy.html">Privacy Policy</a><a class="hover:opacity-100 opacity-80" href="{ASSET}terms-of-service.html">Terms of Service</a></nav>
</div></footer>"""


def example_card(i):
    n, kind, views, eng, aud = EXAMPLES[i]
    return f"""<div class="group relative aspect-square rounded-2xl overflow-hidden bg-gradient-to-br from-[#16293d] to-[#0a5c9e] border border-white/10">
<div class="absolute inset-0 flex flex-col items-center justify-center text-center p-4 transition duration-300 group-hover:blur-sm group-hover:opacity-30">
{mat('account_circle', 'text-6xl text-white/70')}<p class="font-headline-md text-white mt-2">{n}</p><p class="text-white/70 text-sm">{kind}</p></div>
<div class="absolute inset-0 flex flex-col items-center justify-center text-center p-4 bg-black/55 opacity-0 group-hover:opacity-100 transition duration-300">
<p class="font-headline-md text-white">{n}</p><p class="text-white/80 text-sm mb-3">{kind}</p>
<div class="flex gap-5 text-white"><div><p class="text-xl font-bold">{views}</p><p class="text-[11px] uppercase text-white/70">avg views</p></div>
<div><p class="text-xl font-bold">{eng}</p><p class="text-[11px] uppercase text-white/70">engagement</p></div>
<div><p class="text-xl font-bold">{aud}</p><p class="text-[11px] uppercase text-white/70">US audience</p></div></div></div>
<span class="absolute top-3 left-3 text-[10px] uppercase tracking-wider bg-white/90 text-[#16293d] rounded-full px-2 py-0.5">Example format</span></div>"""


# ================================================================ 1. ATTRAKT
def build_attrakt():
    css = """
.grain { background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 .5 0'/></filter><rect width='100%' height='100%' filter='url(%23n)' opacity='.35'/></svg>"); }
.on-dark .wordmark { color: #5fb8ee; }
.scroll-cue::after { content: ''; display: block; width: 2px; height: 70px; margin: 8px auto 0; background: linear-gradient(#b8286e, transparent); animation: cue 1.8s ease-in-out infinite; transform-origin: top; }
@keyframes cue { 0% { transform: scaleY(0); } 60% { transform: scaleY(1); } 100% { transform: scaleY(1); opacity: 0; } }
.svc-row { border-top: 1px solid rgba(255,255,255,.15); }
"""
    lk = 'class="hover:text-primary-fixed-dim"'
    menu_links = (f'<a href="#top" {lk}>Home</a><a href="#services" {lk}>For brands</a><a href="#for-creators" {lk}>For creators</a>'
                  f'<a href="#process" {lk}>How it works</a><a href="#workwithus" {lk}>Contact</a>')
    stats = "".join(
        f'<div class="reveal border border-white/15 rounded-xl p-8 text-center bg-white/5" data-delay="{i*100}"><p class="font-display-lg text-5xl text-white">{v}</p><p class="text-white/70 mt-2">{l}</p></div>'
        for i, (v, l) in enumerate(STATS))
    svc = "".join(
        f'<div class="svc-row reveal flex gap-6 py-6" data-delay="{(i%2)*120}"><span class="font-label-sm text-accent-container w-8 shrink-0 pt-1">0{i+1}</span><div><h3 class="font-headline-md text-white">{t}</h3><p class="text-white/70 mt-1">{d}</p></div></div>'
        for i, (t, d) in enumerate(SERVICES))
    steps = "".join(
        f'<div class="reveal border-t-2 border-primary-container pt-5" data-delay="{i*120}"><p class="font-label-sm text-primary-fixed-dim mb-2">0{i+1}</p><h3 class="font-headline-md text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>'
        for i, (t, d) in enumerate(STEPS4))
    plats = "".join(f'<span class="font-headline-md text-white/60 uppercase tracking-widest">{p}</span><span class="text-accent">/</span>' for p in PLATFORMS * 2)
    hb = hero_buttons("px-8 py-4 border-2 border-accent bg-accent text-white font-label-sm uppercase tracking-widest hover:bg-transparent transition",
                      "px-8 py-4 border-2 border-accent text-white font-label-sm uppercase tracking-widest hover:bg-accent/20 transition")
    body = f"""
<div class="on-dark bg-[#0b1623] text-white" id="top">
<header class="fixed top-0 inset-x-0 z-50 flex justify-between items-center px-6 md:px-12 h-20 bg-gradient-to-b from-[#0b1623] to-transparent">
<a href="#top">{wordmark()}</a>
<button id="menu-btn" aria-expanded="false" class="flex items-center gap-3 font-label-sm uppercase tracking-[.3em] bg-black/40 px-4 py-2 rounded">Menu <span class="flex flex-col gap-1"><i class="block w-6 h-0.5 bg-accent"></i><i class="block w-6 h-0.5 bg-accent"></i><i class="block w-6 h-0.5 bg-accent"></i></span></button>
</header>
<div id="menu-overlay" class="hidden fixed inset-0 z-40 bg-[#0b1623]/97 flex flex-col items-center justify-center gap-8 text-3xl font-headline-md">{menu_links}</div>
<main>
<section class="grain relative min-h-screen flex items-center bg-gradient-to-br from-[#0b1623] via-[#101f33] to-[#1b0f1e]">
<div class="max-w-container-max mx-auto px-6 md:px-12 w-full pt-24">
<h1 class="font-display-lg text-4xl md:text-7xl text-white max-w-5xl leading-tight">{HEAD_PARTS[0]}<span class="text-accent">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-6 text-lg text-white/80 max-w-2xl">{SUB} {BODY}</p>
{hb}</div>
<div class="absolute bottom-8 right-8 text-center font-label-sm uppercase tracking-[.3em] text-white/80 scroll-cue">Scroll down</div>
</section>
<section class="py-24 text-center max-w-4xl mx-auto px-6 reveal">
<p class="font-label-sm uppercase tracking-widest text-accent-container mb-4">The short version</p>
<h2 class="font-headline-lg text-3xl md:text-5xl text-white">We find the creators for brands. We find the deals for creators.</h2>
<p class="mt-6 text-white/70 text-lg">People who watch AI tutorials are already looking for tools to try. We put brands in front of them through creators they trust, and we bring creators the brand deals that fit.</p></section>
<section class="border-y border-white/10 py-6 marquee"><div class="marquee-track">{plats}{plats}</div></section>
<section class="py-24 max-w-container-max mx-auto px-6 md:px-12">
<p class="font-label-sm uppercase tracking-widest text-accent-container text-center mb-3 reveal">For brands</p>
<h2 class="font-headline-lg text-3xl md:text-5xl text-white text-center mb-3 reveal">Every creator passes this check.</h2>
<p class="text-center text-white/70 mb-12 reveal">Before you see a name.</p>
<div class="grid grid-cols-2 md:grid-cols-4 gap-5">{stats}</div></section>
<section id="services" class="py-12 max-w-container-max mx-auto px-6 md:px-12">
<h2 class="font-headline-lg text-3xl md:text-5xl text-white text-center mb-12 reveal">Everything your brand needs to work with AI creators.</h2>
<div class="grid md:grid-cols-2 gap-x-14">{svc}</div></section>
<section id="shortlist" class="py-24 max-w-container-max mx-auto px-6 md:px-12">
<h2 class="font-headline-lg text-3xl md:text-5xl text-white text-center mb-3 reveal">What we send brands.</h2>
<p class="text-center text-white/70 mb-12 reveal">Hover a card. These are example formats, not real creators.</p>
<div class="grid sm:grid-cols-3 gap-5 reveal">{example_card(0)}{example_card(1)}{example_card(2)}</div></section>
{creator_section('dark')}
<section id="process" class="py-24 max-w-container-max mx-auto px-6 md:px-12">
<h2 class="font-headline-lg text-3xl md:text-5xl text-white text-center mb-12 reveal">For brands: from message to live video in four steps.</h2>
<div class="grid md:grid-cols-4 gap-8">{steps}</div></section>
<section class="py-24 px-6 bg-gradient-to-b from-transparent to-[#1b0f1e] text-center">
<h2 class="font-headline-lg text-3xl md:text-5xl text-white mb-4 reveal">Let's work together.</h2>
<p class="text-white/70 mb-10 reveal">{CTA_SUB}</p>
{forms('dark')}</section>
</main>
{footer(True)}
<a href="#top" aria-label="Back to top" class="fixed bottom-6 right-6 w-12 h-12 bg-black/70 text-white flex items-center justify-center rounded">{mat('arrow_upward', '', False)}</a>
</div>"""
    page("layout-attrakt.html", "Layout test: Attrakt-style | Gratovo", "Attrakt-style",
         "Dark, grainy and dramatic. Menu overlay, scroll-down cue, two hero buttons, number boxes, hover-reveal creator grid, For Creators section, four steps.",
         "bg-[#0b1623]", css, body)


# ================================================================ 2. CREATOR AUTHORITY
def build_creatorauthority():
    benefits = "".join(
        f'<div class="reveal bg-white rounded-2xl p-8 text-center shadow-md" data-delay="{i*100}"><div class="w-14 h-14 mx-auto rounded-xl bg-primary-container text-white flex items-center justify-center mb-4">{mat(ic, "text-3xl")}</div><h3 class="font-headline-md text-on-background mb-2">{t}</h3><p class="text-secondary">{d}</p></div>'
        for i, (ic, t, d) in enumerate(BENEFITS))
    svc = "".join(
        f'<div class="reveal bg-white border border-outline-variant rounded-xl p-6" data-delay="{(i%3)*100}"><h3 class="font-headline-md text-on-background mb-1">{t}</h3><p class="text-secondary">{d}</p></div>'
        for i, (t, d) in enumerate(SERVICES))
    plats = "".join(f'<span class="font-headline-md text-primary/70 uppercase tracking-widest">{p}</span>' for p in PLATFORMS * 3)
    hb = hero_buttons("bg-inverse-surface text-white rounded-full px-10 py-4 font-semibold hover:bg-primary transition",
                      "bg-white text-inverse-surface border border-inverse-surface rounded-full px-10 py-4 font-semibold hover:bg-surface-container transition",
                      "mt-10 flex flex-wrap justify-center gap-4")
    body = f"""
<div class="bg-surface-container text-on-background">
<header class="bg-inverse-surface"><div class="max-w-container-max mx-auto px-6 h-20 flex items-center justify-between">
<a href="#">{wordmark()}</a>
<nav class="flex items-center gap-6 text-white text-sm"><a href="#why" class="hidden sm:block hover:underline">For brands</a><a href="#for-creators" class="hidden sm:block hover:underline">For creators</a>
<a href="#workwithus" class="bg-primary-fixed-dim text-inverse-surface rounded-full px-6 py-2 font-semibold">Contact Us</a></nav></div></header>
<main>
<section class="bg-gradient-to-b from-primary-fixed to-surface-container text-center px-6 pt-20 pb-16">
<div class="mb-10">{wordmark("text-5xl md:text-7xl")}</div>
<h1 class="font-headline-lg text-3xl md:text-5xl font-bold text-inverse-surface max-w-4xl mx-auto">{HEADLINE}</h1>
<p class="mt-4 text-xl text-on-surface-variant">{SUB}</p>
{hb}</section>
<section class="py-10 text-center"><p class="font-headline-md text-primary mb-6">Where your content gets seen</p>
<div class="marquee"><div class="marquee-track">{plats}{plats}</div></div></section>
<section id="why" class="max-w-container-max mx-auto px-6 py-16"><h2 class="font-headline-lg text-3xl md:text-4xl text-center mb-10 reveal">Why brands use Gratovo</h2><div class="grid md:grid-cols-3 gap-6">{benefits}</div></section>
<section id="services" class="max-w-container-max mx-auto px-6 py-16"><h2 class="font-headline-lg text-3xl md:text-4xl text-center mb-10 reveal">What brands get</h2><div class="grid md:grid-cols-3 gap-5">{svc}</div></section>
{creator_section('light')}
<section class="max-w-container-max mx-auto px-6 py-16">
<h2 class="font-headline-lg text-3xl md:text-4xl text-center mb-2 reveal">Contact Us</h2><p class="text-center text-xl text-on-surface-variant mb-10">{CTA_SUB}</p>
{forms('light')}</section>
</main>{footer()}</div>"""
    page("layout-creatorauthority.html", "Layout test: Creator Authority-style | Gratovo", "Creator Authority-style",
         "Short and flat. Minimal hero with two buttons, scrolling platform strip, benefits, service grid, For Creators section, two contact cards.",
         "bg-surface-container", "", body)


# ================================================================ 3. SCALE PLEDGE
def build_scalepledge():
    css = """
.sp-card { background:#fff; border:1px solid #deded8; border-top:3px solid #0072b8; border-radius:16px; box-shadow:0 1.25rem 3rem rgba(18,18,18,.07); }
.sp-h { letter-spacing:-.045em; line-height:1; font-weight:800; }
.sp-eyebrow { font:600 12px/1 'JetBrains Mono', monospace; letter-spacing:.14em; text-transform:uppercase; color:#0072b8; }
.growth-path { fill:none; stroke:#0072b8; stroke-width:4; stroke-dasharray:1; stroke-dashoffset:1; animation: drawline 3.4s .4s ease-out forwards; }
.growth-area { fill:url(#ga); opacity:0; animation: fadein 1.2s 2.4s ease forwards; }
.stage { position:absolute; font:600 12px 'JetBrains Mono', monospace; letter-spacing:.12em; text-transform:uppercase; color:#0a5c9e; border-left:2px solid #0072b8; padding-left:8px; opacity:0; animation: fadein .8s ease forwards; }
details.row summary { list-style:none; cursor:pointer; display:grid; grid-template-columns:48px 1fr auto 24px; gap:12px; align-items:center; padding:22px 0; border-top:1px solid #deded8; }
details.row summary::-webkit-details-marker { display:none; }
details.row .tog { transition: transform .25s; font-size:22px; color:#0072b8; }
details.row[open] .tog { transform: rotate(45deg); }
details.row p { padding:0 0 22px 60px; color:#3f403e; }
.step-tab { padding:12px 16px; border-bottom:3px solid transparent; font-weight:600; color:#686867; white-space:nowrap; }
.step-tab.is-active { color:#121212; border-color:#0072b8; }
.nav-blur { backdrop-filter: blur(10px); background: rgba(246,249,255,.85); }
"""
    rows = "".join(
        f'<details class="row"><summary><span class="sp-eyebrow">0{i+1}</span><span class="font-headline-md text-2xl font-bold">{t}</span><span class="hidden md:block text-secondary text-sm">Included</span><span class="tog">+</span></summary><p>{d}</p></details>'
        for i, (t, d) in enumerate(SERVICES))
    cats = [("AI assistants", "Reach people already learning to get more from AI chat and writing tools."),
            ("Automation", "Show workflow builders how your tool saves them hours, on screen."),
            ("Developer tools", "Put your product in front of developers who watch tutorials before they buy."),
            ("Productivity", "Get walked through in real workflows by creators who use tools like yours daily.")]
    cat_tabs = "".join(f'<button class="step-tab" role="tab">{c}</button>' for c, _ in cats)
    cat_panels = "".join(f'<div class="step-panel" role="tabpanel"><h3 class="sp-h text-3xl mb-3">{c}</h3><p class="text-[#3f403e] max-w-xl">{d}</p></div>' for c, d in cats)
    step_panels = "".join(
        f'<div class="step-panel"><p class="sp-eyebrow mb-2">Step {i+1} of 5</p><h3 class="sp-h text-3xl mb-3">{t}</h3><p class="text-[#3f403e] max-w-xl">{d}</p></div>' for i, (t, d) in enumerate(STEPS5))
    faq = "".join(f'<details class="row"><summary style="grid-template-columns:1fr 24px"><span class="font-headline-md text-xl font-bold">{q}</span><span class="tog">+</span></summary><p style="padding-left:0">{a}</p></details>' for q, a in FAQ)
    body = f"""
<div class="bg-[#f6f9ff] text-[#121212]">
<header class="nav-blur sticky top-0 z-50 border-b border-[#deded8]"><div class="max-w-[80rem] mx-auto px-6 h-[72px] flex items-center justify-between">
<a href="#">{wordmark("text-2xl")}</a>
<nav class="hidden md:flex gap-8 text-sm font-medium"><a href="#services">For brands</a><a href="#for-creators">For creators</a><a href="#process">How it works</a><a href="#faq">Questions</a></nav>
<a href="#workwithus" class="bg-primary-container text-white rounded-2xl px-5 py-3 text-sm font-semibold">{CTA}</a></div></header>
<main>
<section class="relative overflow-hidden"><div class="absolute inset-x-0 bottom-0 h-[55%] pointer-events-none">
<svg viewBox="0 0 760 430" preserveAspectRatio="none" class="w-full h-full" aria-hidden="true"><defs><linearGradient id="ga" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#0072b8" stop-opacity=".25"/><stop offset="1" stop-color="#0072b8" stop-opacity=".02"/></linearGradient></defs>
<path class="growth-area" d="M0 400 L90 385 L170 392 L250 360 L330 366 L410 330 L490 335 L560 230 L640 215 L700 110 L760 40 L760 430 L0 430 Z"/>
<path class="growth-path" pathLength="1" d="M0 400 L90 385 L170 392 L250 360 L330 366 L410 330 L490 335 L560 230 L640 215 L700 110 L760 40"/></svg>
<span class="stage" style="left:24%;bottom:22%;animation-delay:1.2s">Request</span><span class="stage" style="left:42%;bottom:33%;animation-delay:1.8s">Match</span>
<span class="stage" style="left:62%;bottom:50%;animation-delay:2.4s">Agree</span><span class="stage" style="left:82%;bottom:72%;animation-delay:3s">Launch</span></div>
<div class="relative max-w-[80rem] mx-auto px-6 pt-20 pb-72 md:pb-80">
<p class="sp-eyebrow mb-6">AI influencer marketing</p>
<h1 class="sp-h text-5xl md:text-8xl max-w-5xl">{HEAD_PARTS[0]}<span class="text-primary-container">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-6 text-lg text-[#3f403e] max-w-2xl">{SUB} {BODY}</p>
{hero_buttons("bg-primary-container text-white rounded-2xl px-6 py-4 font-semibold", "bg-[#121212] text-white rounded-2xl px-6 py-4 font-semibold", "mt-8 flex flex-wrap gap-3")}</div></section>
<section class="max-w-[80rem] mx-auto px-6 pb-24 grid md:grid-cols-2 gap-5">
<article class="sp-card p-9 reveal"><p class="sp-eyebrow mb-3">The buying journey</p><h3 class="sp-h text-3xl mb-3">People watch before they buy.</h3><p class="text-[#3f403e]">Before trying a new AI tool, people watch tutorials, compare options, and listen to creators they already trust.</p></article>
<article class="sp-card p-9 reveal" data-delay="120"><p class="sp-eyebrow mb-3">Our role</p><h3 class="sp-h text-3xl mb-3">We connect both sides.</h3><p class="text-[#3f403e]">We find the right creator for the brand, and the right brand deal for the creator, and keep the conversation moving between them.</p></article></section>
<section id="services" class="max-w-[80rem] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">For brands</p><h2 class="sp-h text-4xl md:text-6xl">What brands get.</h2></div><div class="max-w-4xl mx-auto border-b border-[#deded8]">{rows}</div></section>
<section class="bg-white py-24"><div class="max-w-[80rem] mx-auto px-6"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">Built for AI</p><h2 class="sp-h text-4xl md:text-6xl">Creator marketing works when the product needs showing.</h2></div>
<div data-stepper class="max-w-4xl mx-auto"><div class="flex justify-center gap-2 overflow-x-auto border-b border-[#deded8]" role="tablist">{cat_tabs}</div>
<div class="sp-card p-10 mt-8 min-h-[190px] relative">{cat_panels}<div class="absolute right-6 top-6 flex flex-col items-center gap-2"><button data-prev aria-label="Previous" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">←</button><span data-count class="text-xs text-[#686867]"></span><button data-next aria-label="Next" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">→</button></div></div></div></div></section>
{creator_section('light')}
<section id="process" class="max-w-[80rem] mx-auto px-6 py-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">How it works for brands</p><h2 class="sp-h text-4xl md:text-6xl">From message to live video.</h2></div>
<div data-stepper class="max-w-4xl mx-auto"><div class="sp-card p-10 min-h-[190px] relative">{step_panels}<div class="absolute right-6 top-6 flex flex-col items-center gap-2"><button data-prev aria-label="Previous step" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">←</button><span data-count class="text-xs text-[#686867]"></span><button data-next aria-label="Next step" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">→</button></div></div></div></section>
<section class="max-w-[80rem] mx-auto px-6 pb-24"><div class="sp-card p-10 md:p-14 grid md:grid-cols-2 gap-8 items-center reveal" style="border-left:4px solid #0072b8;border-top:1px solid #deded8"><div><p class="sp-eyebrow mb-3">Our approach</p><h3 class="sp-h text-4xl">Brands bring the product. Creators bring the audience.</h3></div><p class="text-[#3f403e]">We don't hand brands a spreadsheet of 200 names. We check each creator's real numbers, send the one to three that fit, and keep it simple for creators too.</p></div></section>
<section id="faq" class="max-w-4xl mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">Common questions</p><h2 class="sp-h text-4xl md:text-5xl">What to know before we work together.</h2></div><div class="border-b border-[#deded8]">{faq}</div></section>
<section class="px-6 pb-24"><div class="max-w-5xl mx-auto text-center reveal"><p class="sp-eyebrow mb-3">Let's work together</p><h2 class="sp-h text-4xl md:text-5xl mb-4">Brands and creators, start here.</h2><p class="text-[#3f403e] mb-8">{CTA_SUB}</p>{forms('light')}</div></section>
</main>
<footer class="bg-[#121212] text-white/75 py-14"><div class="max-w-[80rem] mx-auto px-6 grid md:grid-cols-3 gap-8"><div>{wordmark("text-2xl")}<p class="mt-4 text-sm">Connecting AI and SaaS brands with vetted creators, and creators with brand deals that fit.</p></div>
<div><p class="font-label-sm uppercase mb-3 text-white">Explore</p><div class="space-y-2 text-sm"><a class="block" href="#services">For brands</a><a class="block" href="#for-creators">For creators</a><a class="block" href="#faq">Questions</a></div></div>
<div><p class="font-label-sm uppercase mb-3 text-white">Contact</p><p class="text-sm">{EMAIL}</p><p class="text-sm mt-4"><a href="{ASSET}privacy-policy.html">Privacy</a> · <a href="{ASSET}terms-of-service.html">Terms</a></p></div></div>
<p class="max-w-[80rem] mx-auto px-6 mt-10 text-xs text-white/50">© 2026 Gratovo.</p></footer></div>"""
    page("layout-scalepledge.html", "Layout test: Scale Pledge-style | Gratovo", "Scale Pledge-style",
         "Editorial and light. Hero line draws itself with the four stages, accordion services, tabbed carousel, For Creators section, step carousel, FAQ.",
         "bg-[#f6f9ff]", css, body)


# ================================================================ 4. NSENTIVE
def build_nsentive():
    css = """
.dict-line { opacity:0; animation: fadein .9s ease forwards; }
.n-card { border:1px solid rgba(255,255,255,.55); border-radius:28px; padding:26px 26px 40px; }
.n-row { border-top:1px solid #3a3a3a; display:grid; grid-template-columns: 1fr 1.4fr 60px; gap:24px; padding:34px 0; align-items:start; }
@media (max-width: 768px) { .n-row { grid-template-columns: 1fr; gap: 10px; padding: 24px 0; } .n-row > span { display: none; } }
.loop { height: 340px; overflow: hidden; -webkit-mask-image: linear-gradient(transparent, #000 25%, #000 75%, transparent); mask-image: linear-gradient(transparent, #000 25%, #000 75%, transparent); }
.loop-track { animation: scrollup 14s linear infinite; }
.loop-track span { display:block; text-align:center; font-size:1.7rem; line-height:3.1rem; color:#fff; }
.loop-track span:nth-child(3n+2) { font-family: Georgia, serif; font-style: italic; }
"""
    cards = "".join(
        f'<div class="n-card reveal" data-delay="{i*100}"><div class="mb-14 text-white">{mat(ic, "text-3xl", False)}</div><h3 class="text-2xl font-semibold text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>'
        for i, (ic, t, d) in enumerate(BENEFITS))
    w = [("WHO", "Brands and creators in AI and SaaS: marketing managers and founders who want creators promoting their product, and creators who want brand deals that fit."),
         ("WHAT", "Brands get 1 to 3 vetted AI creators picked for their product. Creators get put forward to brands that fit their audience."),
         ("WHY", "People watching AI tutorials are looking for tools to try. A trusted creator showing a product reaches them at that moment."),
         ("WHERE", "YouTube, LinkedIn, X, and newsletters, wherever the right creator's audience is."),
         ("HOW", "Tell us about your product or your channel. We make the introduction. We take care of contracts, scripts, and posting."),
         ("WHEN", "We reply within 24 hours. Most deals go live within about a month.")]
    rows = "".join(f'<div class="n-row reveal"><h3 class="text-5xl md:text-6xl font-semibold text-[#161616]">{a}</h3><p class="text-[#555] text-lg">{c}</p><span class="text-3xl text-[#161616]">↘</span></div>' for a, c in w)
    who = [("Marketing managers", "Hand off the searching, vetting, and chasing. Keep the final say."),
           ("Founders", "Get your product in front of the right audience without learning creator marketing first."),
           ("Creators", "Get brand deals that fit your channel, without cold outreach or endless email threads.")]
    whorows = "".join(f'<div class="n-row reveal"><h3 class="text-4xl md:text-5xl font-semibold text-[#161616]">{a}</h3><p class="text-[#555] text-lg">{b}</p><span class="text-3xl text-[#161616]">↘</span></div>' for a, b in who)
    flow = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="text-white/40 text-sm mb-3">0{i+1}</p><h3 class="text-4xl font-semibold text-white mb-3">{t}</h3><p class="text-white/70">{d}</p></div>' for i, (t, d) in enumerate(STEPS4))
    loop_items = "".join(f"<span>{x}</span>" for x in ["no cold emails", "no chasing replies", "no guessing who's legit", "no endless threads", "just the right match"] * 2)
    body = f"""
<div class="bg-black text-white">
<header class="max-w-[1280px] mx-auto px-6 h-24 flex items-center justify-between"><a href="#">{wordmark("text-4xl")}</a><a href="#workwithus" class="bg-primary-container text-white rounded-full px-8 py-3 font-medium">Let's Talk</a></header>
<main>
<section class="text-center px-6 pt-16 pb-24">
<h1 class="dict-line text-6xl md:text-8xl font-semibold tracking-tight" style="animation-delay:.2s">match</h1>
<p class="dict-line text-3xl md:text-4xl text-white/35 mt-3" style="animation-delay:.9s">/mætʃ/</p>
<p class="dict-line text-3xl md:text-4xl font-semibold mt-1" style="animation-delay:1.5s">noun</p>
<p class="dict-line text-xl md:text-2xl mt-8 max-w-2xl mx-auto text-white/90" style="animation-delay:2.1s">A creator whose audience fits your product. A brand deal that fits your channel. We find both.</p>
{hero_buttons("bg-white text-black rounded-full px-10 py-4 font-semibold", "border border-white text-white rounded-full px-10 py-4 font-semibold", "dict-line mt-10 flex flex-wrap justify-center gap-4\" style=\"animation-delay:2.7s")}</section>
<section class="max-w-[1280px] mx-auto px-6 pb-28 grid md:grid-cols-3 gap-6">{cards}</section>
<div class="bg-white text-[#161616]"><div class="max-w-[1280px] mx-auto px-6 py-24">
<h2 class="text-5xl md:text-7xl font-semibold tracking-tight mb-14 reveal">The short version.</h2><div class="border-b border-[#3a3a3a]">{rows}</div></div>
<div class="max-w-[1280px] mx-auto px-6 pb-24"><h2 class="text-5xl md:text-7xl font-semibold tracking-tight mb-14 reveal">Who it's for.</h2><div class="border-b border-[#3a3a3a]">{whorows}</div></div></div>
{creator_section('dark')}
<section class="max-w-[1280px] mx-auto px-6 py-28"><h2 class="text-5xl md:text-7xl font-semibold tracking-tight text-center mb-16 reveal">Four steps for brands.</h2><div class="grid md:grid-cols-4 gap-10">{flow}</div></section>
<section class="bg-primary-container px-6 py-24"><div class="max-w-[1200px] mx-auto grid md:grid-cols-[1fr_2.4fr] gap-10 items-center">
<div class="loop hidden md:block"><div class="loop-track">{loop_items}</div></div>
<div class="bg-black rounded-[28px] p-8 md:p-10"><h2 class="text-center text-3xl font-semibold mb-2">Let's Talk</h2><p class="text-center text-white/70 mb-6">{CTA_SUB}</p>{forms('dark')}</div></div></section>
</main>{footer(True)}</div>"""
    page("layout-nsentive.html", "Layout test: Nsentive-style | Gratovo", "Nsentive-style",
         "Black to white to brand blue. Dictionary-style hero that fades in line by line, outlined cards, ruled rows (brands, creators), scrolling word list beside the forms.",
         "bg-black", css, body)


# ================================================================ 5. APOLLO
def build_apollo():
    css = """
@keyframes twinkle { 0%,100% { opacity:.15; } 50% { opacity:.9; } }
@keyframes shoot { 0% { transform: translate(0,0) rotate(-35deg); opacity:0; } 8% { opacity:1; } 30% { transform: translate(-420px,300px) rotate(-35deg); opacity:0; } 100% { opacity:0; } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes counter { to { transform: rotate(-360deg); } }
.shoot { position:absolute; top:8%; right:12%; width:120px; height:2px; background:linear-gradient(90deg, rgba(255,255,255,0), #fff); animation: shoot 7s 2s infinite; }
.glass { background: linear-gradient(160deg, rgba(255,255,255,.08), rgba(255,255,255,.02)); border:1px solid rgba(255,255,255,.12); border-radius:28px; backdrop-filter: blur(10px); }
.grad-text { background: linear-gradient(90deg, #ffd9a8, #ff8fb3, #b88cff); -webkit-background-clip:text; background-clip:text; color:transparent; }
.chip { position:absolute; background: rgba(20,30,70,.9); border:1px solid rgba(255,255,255,.18); border-radius:16px; padding:10px 14px; font-size:13px; color:#fff; animation: floaty 6s ease-in-out infinite; box-shadow:0 10px 30px rgba(0,0,0,.4); }
.orbit { position:relative; width:260px; height:260px; margin:auto; }
.orbit .ring { position:absolute; inset:0; border:1px dashed rgba(255,255,255,.25); border-radius:50%; animation: spin 24s linear infinite; }
.orbit .ring i { position:absolute; width:52px; height:52px; margin:-26px; border-radius:16px; background:#fff; color:#16293d; display:flex; align-items:center; justify-content:center; animation: counter 24s linear infinite; }
.orbit .core { position:absolute; inset:88px; border-radius:24px; background: linear-gradient(135deg,#0a5c9e,#6a54e8); display:flex; align-items:center; justify-content:center; box-shadow:0 0 50px rgba(106,84,232,.6); }
.ghost { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size: clamp(120px, 24vw, 340px); font-weight:800; color: rgba(255,255,255,.05); pointer-events:none; letter-spacing:-.04em; }
.beam { height:1px; background: linear-gradient(90deg, transparent, rgba(150,130,255,.8), transparent); background-size:200% 100%; animation: shimmer 4s linear infinite; }
@keyframes shimmer { to { background-position: -200% 0; } }
"""
    blocks = [("It's that easy.", "Send us a short message. We do the searching, vetting, and chasing."),
              ("Peace of mind.", "Every creator is checked for real views, engagement, and audience location first."),
              ("Your product, shown properly.", "Creators demo your tool in a real workflow, for an audience that wants to try it."),
              ("Nothing goes live unseen.", "You approve the video before it posts.")]
    bl = "".join(f'<div class="glass p-8 reveal" data-delay="{i*100}"><h3 class="font-headline-md text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>' for i, (t, d) in enumerate(blocks))
    stats = "".join(f'<div class="text-center"><p class="text-5xl font-bold text-white">{v}</p><p class="text-white/65 mt-2 max-w-[200px] mx-auto">{l}</p></div>' for v, l in STATS[:3])
    steps = "".join(f'<div class="glass p-7 reveal" data-delay="{i*90}"><span class="grad-text text-4xl font-bold">0{i+1}</span><h3 class="font-headline-md text-white mt-3 mb-2">{t}</h3><p class="text-white/70 text-sm">{d}</p></div>' for i, (t, d) in enumerate(STEPS5))
    plat_icons = ["smart_display", "work", "tag", "mail"]
    orbit_items = "".join(
        f'<i style="left:{50 + 50*math.cos(a)}%;top:{50 + 50*math.sin(a)}%">{mat(ic, "text-2xl", True)}</i>'
        for ic, a in zip(plat_icons, [0, 1.5708, 3.1416, 4.7124]))
    pill = "inline-block border border-white/25 bg-white/10 rounded-full px-7 py-3 text-sm font-semibold"
    body = f"""
<div class="bg-[#050a1f] text-white relative overflow-hidden">
<div id="stars" class="absolute inset-0 pointer-events-none"></div><div class="shoot"></div>
<header class="relative z-20 max-w-[1280px] mx-auto px-6 h-20 flex items-center justify-between"><a href="#">{wordmark("text-3xl")}</a>
<nav class="hidden md:flex gap-1 border border-white/15 rounded-full px-2 py-2 text-sm bg-white/5"><a class="px-4 py-1.5 rounded-full bg-white/10" href="#">Home</a><a class="px-4 py-1.5" href="#brands">For brands</a><a class="px-4 py-1.5" href="#for-creators">For creators</a><a class="px-4 py-1.5" href="#process">How it works</a></nav>
<a href="#workwithus" class="border border-white/25 bg-white/5 rounded-lg px-5 py-2 text-sm">Contact</a></header>
<main class="relative z-10">
<section class="text-center px-6 pt-14 pb-12"><h1 class="font-display-lg text-4xl md:text-7xl max-w-5xl mx-auto leading-[1.05]">{HEAD_PARTS[0]}<span class="grad-text">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-5 text-white/70 text-lg max-w-2xl mx-auto">{SUB}</p></section>
<section class="max-w-[1280px] mx-auto px-6 grid md:grid-cols-2 gap-6 pb-24">
<div id="brands" class="glass p-8 md:p-10 text-center relative overflow-hidden min-h-[470px] reveal"><h2 class="font-display-lg text-4xl mb-3">for brands.</h2><p class="text-white/70 mb-6">1 to 3 vetted AI creators picked for your product.</p>
<a href="#workwithus" class="{pill}">{CTA}</a>
<div class="relative h-56 mt-6"><div class="chip" style="left:6%;top:6%;--r:-6deg">Creator A · 42K avg views</div><div class="chip" style="left:34%;top:38%;--r:4deg;animation-delay:1s">Creator B · 5.1% engagement</div><div class="chip" style="left:12%;top:70%;--r:-3deg;animation-delay:2s">Creator C · 46% US audience</div></div>
<p class="absolute bottom-3 inset-x-0 text-[11px] text-white/45 uppercase tracking-wider">Example format</p></div>
<div class="glass p-8 md:p-10 text-center min-h-[470px] reveal" data-delay="120"><h2 class="font-display-lg text-4xl mb-3">for creators.</h2><p class="text-white/70 mb-6">Brand deals that fit your channel. YouTube, LinkedIn, X, and newsletters.</p>
<a href="#creators" class="{pill}">{CTA_C}</a>
<div class="orbit mt-8"><div class="core">{mat('rocket_launch', 'text-4xl text-white')}</div><div class="ring">{orbit_items}</div></div></div></section>
<section class="max-w-[1280px] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><span class="inline-block border border-white/20 rounded-full px-4 py-1 text-sm mb-4">What brands get ✦</span><h2 class="font-display-lg text-4xl md:text-6xl">A simpler way to work with AI creators.</h2></div><div class="grid md:grid-cols-2 gap-5">{bl}</div></section>
<section class="relative max-w-[1100px] mx-auto px-6 py-24"><div class="ghost" aria-hidden="true">1-3</div><div class="relative"><div class="beam mb-12"></div><div class="grid md:grid-cols-3 gap-10">{stats}</div><div class="beam mt-12"></div></div><p class="relative text-center text-white/60 mt-8">Every creator we recommend passes these checks first.</p></section>
{creator_section('dark')}
<section id="process" class="max-w-[1280px] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><h2 class="font-display-lg text-4xl md:text-6xl">How a deal works with us.</h2></div><div class="grid md:grid-cols-5 gap-4">{steps}</div></section>
<section class="max-w-[1100px] mx-auto px-6 pb-24"><div class="glass p-8 md:p-14 text-center reveal"><h2 class="font-display-lg text-4xl md:text-6xl mb-3">Ready for <span class="grad-text">take-off?</span></h2><p class="text-white/70 mb-10">{CTA_SUB}</p>{forms('dark')}</div></section>
</main>{footer(True)}</div>"""
    page("layout-apollo.html", "Layout test: Apollo-style | Gratovo", "Apollo-style",
         "Dark space theme. Twinkling stars and a shooting star, a glass card for brands and one for creators, floating chips, orbiting platform icons, ghost number behind the stats.",
         "bg-[#050a1f]", css, body)


# ================================================================ 6. RIGHT CLICK
def build_rightclick():
    css = """
.display { font-family: 'Anton', 'Plus Jakarta Sans', sans-serif; text-transform: uppercase; letter-spacing: .01em; line-height: .95; }
.mono { font-family: 'JetBrains Mono', monospace; }
.rc-cap { color:#9ad6f7; }
.rc-btn { border:1px solid #9ad6f7; color:#9ad6f7; border-radius:999px; padding:18px 28px; font-size:1.6rem; display:flex; justify-content:space-between; align-items:center; transition:.25s; }
.rc-btn:hover { background:#9ad6f7; color:#050a14; }
.rc-btn:hover span { color:#050a14 !important; }
.fcard { position:absolute; width:150px; border-radius:18px; padding:14px; color:#fff; box-shadow:0 14px 40px rgba(0,0,0,.5); animation: floaty 7s ease-in-out infinite; }
#scroll-progress-wrap { position:fixed; left:10px; top:90px; bottom:40px; width:3px; z-index:50; }
#scroll-progress { width:3px; background:#9ad6f7; height:0; }
"""
    cards = [("30K+", "avg views", "left:2%;top:6%;--r:-8deg;background:linear-gradient(135deg,#6a54e8,#b8286e)", 0),
             ("3-8%", "engagement", "right:3%;top:2%;--r:6deg;background:linear-gradient(135deg,#0a5c9e,#0072b8)", 1.2),
             ("35%+", "target audience", "left:6%;top:48%;--r:5deg;background:linear-gradient(135deg,#b8286e,#ff7a59)", 2.2),
             ("1-3", "creators, not 200", "right:2%;top:42%;--r:-5deg;background:linear-gradient(135deg,#0072b8,#1fb6a6)", 3.2)]
    fc = "".join(f'<div class="fcard hidden md:block" style="{st};animation-delay:{d}s"><p class="display text-4xl">{v}</p><p class="text-xs uppercase tracking-wider opacity-90">{l}</p></div>' for v, l, st, d in cards)
    pills = [("BRANDS", "Vetted AI creators for your product.", "#workwithus"),
             ("CREATORS", "Brand deals that fit your channel.", "#creators"),
             ("HOW IT WORKS", "Four steps, from message to live video.", "#process")]
    pl = "".join(f'<a href="{h}" class="rc-btn reveal mono" data-delay="{i*100}"><span>{a}</span><span class="text-base text-white/70 max-w-md text-right hidden md:block">{b}</span><span>↗</span></a>' for i, (a, b, h) in enumerate(pills))
    ex = "".join(example_card(i) for i in range(3))
    steps = "".join(f'<div class="reveal border-l border-[#9ad6f7]/50 pl-5" data-delay="{i*100}"><p class="display text-4xl rc-cap">0{i+1}</p><h3 class="mono text-lg font-semibold mt-2">{t}</h3><p class="mono text-white/70 text-sm mt-1">{d}</p></div>' for i, (t, d) in enumerate(STEPS4))
    hb = hero_buttons("bg-[#9ad6f7] text-[#050a14] font-bold rounded-full px-8 py-4", "border border-[#9ad6f7] text-[#9ad6f7] font-bold rounded-full px-8 py-4", "mt-8 flex flex-wrap justify-center gap-4")
    body = f"""
<div class="bg-[#050a14] text-white mono">
<div id="scroll-progress-wrap" aria-hidden="true"><div id="scroll-progress"></div></div>
<header class="relative z-20 flex items-center justify-between px-6 md:px-12 h-24"><span class="mono text-xs rc-cap hidden md:block"><span id="scroll-progress-num">0</span> / 100</span>
<a href="#" class="md:absolute md:left-1/2 md:-translate-x-1/2">{wordmark("text-3xl")}</a><a href="#workwithus" class="ml-auto bg-white/10 rc-cap rounded-full px-5 py-2 text-xs tracking-widest">WORK WITH US</a></header>
<main>
<section class="relative min-h-[88vh] flex flex-col items-center justify-center text-center px-6 overflow-hidden">{fc}
<h1 class="display rc-cap text-[clamp(3rem,10vw,8.5rem)] max-w-6xl relative z-10">{HEADLINE}</h1>
<p class="relative z-10 mt-6 max-w-xl text-white/80">{SUB}</p><div class="relative z-10">{hb}</div></section>
<section class="max-w-5xl mx-auto px-6 pb-24"><div class="border border-[#9ad6f7] rounded-[32px] p-10 md:p-14 text-center reveal"><p class="text-xl leading-relaxed">We're <b class="rc-cap">Gratovo</b>. We connect AI brands with vetted creators, and creators with brand deals that fit. {BODY}</p></div></section>
<section class="max-w-5xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-10 reveal">Who we work with</h2><div class="space-y-5">{pl}</div></section>
<section class="max-w-6xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-3 reveal">What we send brands</h2><p class="text-white/70 mb-10 reveal">Hover a card. Example formats, not real creators.</p><div class="grid sm:grid-cols-3 gap-5 reveal">{ex}</div></section>
{creator_section('dark', head_cls='display')}
<section id="process" class="max-w-6xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-12 reveal">Four steps for brands</h2><div class="grid md:grid-cols-4 gap-8">{steps}</div></section>
<section class="max-w-5xl mx-auto px-6 pb-28 text-center"><h2 class="display rc-cap text-6xl md:text-8xl mb-6 reveal">Ready to get started?</h2><p class="text-white/70 mb-10">{CTA_SUB}</p>{forms('dark')}</section>
</main>{footer(True)}</div>"""
    page("layout-rightclick.html", "Layout test: Right Click-style | Gratovo", "Right Click-style",
         "Bold and edgy. Giant condensed headline with floating stat cards and two buttons, scroll progress counter on the left edge, outlined pill rows (brands, creators), big closing line.",
         "bg-[#050a14]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;display=swap" rel="stylesheet">')


# ================================================================ 7. MINDSHARE
def build_mindshare():
    css = """
.ms { font-family: 'Anton', 'Plus Jakarta Sans', sans-serif; text-transform: uppercase; letter-spacing: -.01em; line-height: .92; }
.pill { border-radius:999px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; font-size:.8rem; padding:18px 30px; display:inline-flex; gap:8px; align-items:center; }
.tag { border:1px solid currentColor; border-radius:999px; padding:6px 14px; font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.side { position:absolute; left:18px; top:40px; writing-mode:vertical-rl; transform:rotate(180deg); font-size:.7rem; letter-spacing:.25em; opacity:.6; text-transform:uppercase; }
@keyframes ticker { to { transform: translateX(-50%); } }
.ticker .marquee-track { animation: ticker 22s linear infinite; }
"""
    plats = "".join(f'<span class="ms text-4xl md:text-5xl text-[#16293d]/80">{p}</span>' for p in PLATFORMS * 3)
    svc = "".join(f'<div class="reveal border-t border-white/20 pt-6" data-delay="{i*90}"><p class="text-primary-fixed-dim text-xs font-bold tracking-widest mb-2">0{i+1}</p><h3 class="ms text-3xl mb-2">{t}</h3><p class="text-white/65">{d}</p></div>' for i, (t, d) in enumerate(SERVICES[:4]))
    props = [("Zero outreach", "We contact the creators. You only hear about the ones worth your time."),
             ("Real numbers", "Views, engagement, and audience location, checked before you see a name."),
             ("You approve it", "Nothing goes live until you've seen the video.")]
    pr = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="font-bold text-lg">{a}</p><p class="text-[#0b1623]/90">{b}</p></div>' for i, (a, b) in enumerate(props))
    cprops = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="font-bold text-lg">{t}</p><p class="text-[#0b1623]/90">{d}</p></div>' for i, (_ic, t, d) in enumerate(CREATOR_BENEFITS))
    body = f"""
<div class="bg-[#16293d] text-white">
<section class="relative bg-primary-container text-[#0b1623] min-h-screen flex flex-col">
<header class="flex items-center justify-between px-6 md:px-10 h-20"><a href="#" class="bg-white rounded-xl px-3 py-1">{wordmark("text-2xl")}</a>
<nav class="flex items-center gap-6 text-xs tracking-widest uppercase font-semibold"><a class="hidden sm:block" href="#brands">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="bg-[#0b1623] text-white rounded-full px-5 py-2">Contact</a></nav></header>
<div class="flex-1 flex flex-col items-center justify-center text-center px-6"><h1 class="ms text-[clamp(4.5rem,17vw,15rem)] text-[#0b1623]">Gratovo</h1>
<p class="mt-6 text-lg font-medium text-[#0b1623]">[ {HEADLINE} ]</p>
<div class="mt-8 flex flex-wrap justify-center gap-3"><a href="#workwithus" class="pill bg-[#0b1623] text-white">{CTA} →</a><a href="#creators" class="pill border border-[#0b1623]/60">{CTA_C}</a></div></div>
<div class="ticker marquee py-6 border-t border-[#0b1623]/20"><div class="marquee-track">{plats}{plats}</div></div></section>
<section id="why" class="px-6 md:px-16 py-24 max-w-[1200px] mx-auto"><p class="text-primary-fixed-dim font-bold tracking-widest text-xs uppercase mb-3 reveal">For brands</p><h2 class="ms text-5xl md:text-7xl mb-14 reveal">Everything between "hello" and "live".</h2><div class="grid md:grid-cols-4 gap-8">{svc}</div></section>
<section class="bg-[#101d2e] px-6 py-20 text-center"><h2 class="ms text-5xl md:text-7xl mb-10 reveal">Where it runs</h2><div class="flex flex-wrap justify-center gap-3 reveal">{"".join(f'<span class="tag text-primary-fixed-dim">{p}</span>' for p in PLATFORMS)}</div></section>
<section class="px-6 md:px-16 py-24 max-w-[1200px] mx-auto grid md:grid-cols-2 gap-14 items-center"><div><p class="text-primary-fixed-dim text-xs font-bold tracking-widest uppercase mb-4 reveal">Our approach</p>
<h2 class="ms text-6xl md:text-8xl reveal">We send 1 to 3 names. <span class="text-accent-container">Not 200.</span></h2><div class="h-1 w-14 bg-accent mt-6"></div></div>
<p class="text-white/65 text-lg reveal">Most creator lists are long spreadsheets that someone still has to check. We check first. Brands get the few creators whose real numbers fit their product, and creators get introduced to brands that fit theirs.</p></section>
<section id="brands" class="relative bg-primary-container text-[#0b1623] px-6 py-24 text-center"><span class="side">For brands</span>
<h2 class="ms text-6xl md:text-9xl max-w-5xl mx-auto reveal">No guessing. Just the right creators.</h2><div class="h-1 w-14 bg-[#0b1623] mx-auto my-6"></div>
<div class="max-w-3xl mx-auto grid md:grid-cols-3 gap-8 text-left my-10">{pr}</div>
<a href="#workwithus" class="pill bg-[#0b1623] text-white">{CTA} →</a></section>
<section id="for-creators" class="relative bg-[#16293d] text-white px-6 py-24 text-center"><span class="side">For creators</span>
<h2 class="ms text-6xl md:text-9xl max-w-5xl mx-auto reveal">Brand deals that <span class="text-accent-container">fit your channel.</span></h2><div class="h-1 w-14 bg-accent mx-auto my-6"></div>
<div class="max-w-3xl mx-auto grid md:grid-cols-2 gap-8 text-left my-10 text-white">{"".join(f'<div class="reveal"><p class="font-bold text-lg">{t}</p><p class="text-white/70">{d}</p></div>' for _ic, t, d in CREATOR_BENEFITS)}</div>
<a href="#creators" class="pill bg-primary-container text-[#0b1623]">{CTA_C} →</a></section>
<section class="px-6 py-24 bg-[#16293d]"><div class="max-w-5xl mx-auto bg-primary-container text-[#0b1623] rounded-[28px] p-8 md:p-14 text-center reveal"><h2 class="ms text-5xl md:text-7xl mb-4">Let's get you matched.</h2><p class="mb-8 opacity-90">{CTA_SUB}</p>{forms('color')}</div></section>
{footer(True)}</div>"""
    page("layout-mindshare.html", "Layout test: MindShare-style | Gratovo", "MindShare-style",
         "Giant type on alternating blue and navy bands. Full-screen wordmark hero with two buttons, platform ticker, For Brands and For Creators bands, rounded closing card.",
         "bg-[#16293d]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;display=swap" rel="stylesheet">')


# ================================================================ 8. SMOOTH
def build_smooth():
    css = """
.serif { font-family: 'Fraunces', Georgia, serif; }
.hero-bg { background: linear-gradient(120deg, #2b1a4d, #0a5c9e, #5b2a86, #16293d); background-size: 300% 300%; animation: drift 16s ease-in-out infinite; }
@keyframes drift { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
.ellipse { fill:none; stroke:#fff; stroke-width:2.5; stroke-dasharray:1; stroke-dashoffset:1; animation: drawline 1.6s 1s ease-out forwards; }
@keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(8px); } }
.phone { width:200px; border:6px solid #2a1745; border-radius:32px; background:#fff; box-shadow:0 20px 40px rgba(42,23,69,.25); overflow:hidden; }
.cloud span { background:#fcfaf6; border-radius:999px; padding:10px 20px; font-weight:700; font-size:.78rem; letter-spacing:.06em; text-transform:uppercase; color:#2a1745; }
"""
    tags = ["AI assistants", "Automation", "Developer tools", "Productivity", "SaaS", "No-code", "AI agents", "Analytics", "Writing tools", "Design tools", "Meeting tools", "Research tools"]
    cloud = "".join(f"<span>{t}</span>" for t in tags)
    phones = "".join(
        f"""<div class="phone reveal" data-delay="{i*120}" style="margin-top:{[0,36,0][i]}px"><div class="bg-gradient-to-br from-[#2a1745] to-[#0a5c9e] h-64 flex flex-col items-center justify-center text-white text-center p-4">{mat('account_circle','text-6xl text-white/80')}<p class="serif text-xl mt-2">{EXAMPLES[i][0]}</p><p class="text-xs text-white/70">{EXAMPLES[i][1]}</p></div>
<div class="p-4 text-[#2a1745]"><p class="text-[10px] uppercase tracking-widest text-[#2a1745]/60 mb-2">Example format</p><div class="flex justify-between text-center"><div><p class="font-bold">{EXAMPLES[i][2]}</p><p class="text-[10px] uppercase">avg views</p></div><div><p class="font-bold">{EXAMPLES[i][3]}</p><p class="text-[10px] uppercase">engage</p></div><div><p class="font-bold">{EXAMPLES[i][4]}</p><p class="text-[10px] uppercase">US</p></div></div></div></div>"""
        for i in range(3))
    steps = "".join(f'<div class="reveal text-center px-4" data-delay="{i*120}"><p class="serif text-6xl text-[#7a4fc0]">{i+1}</p><h3 class="serif text-2xl text-[#2a1745] mt-2 mb-2">{t}</h3><p class="text-[#2a1745]/75">{d}</p></div>' for i, (t, d) in enumerate(STEPS3))
    body = f"""
<div class="bg-[#fcfaf6] text-[#2a1745]">
<section class="hero-bg relative min-h-screen text-white flex flex-col">
<div class="absolute inset-0 bg-[#2a1745]/45"></div>
<header class="relative z-10 flex items-center justify-between px-6 md:px-10 h-24"><a href="#">{wordmark("text-3xl")}</a>
<nav class="flex items-center gap-7 text-sm font-medium"><a class="hidden sm:block" href="#who">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="border border-white rounded-full px-5 py-2">Contact</a></nav></header>
<div class="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 pb-10">
<p class="text-xs font-semibold tracking-[.2em] uppercase mb-6">AI brands and creators, introduced</p>
<h1 class="serif text-5xl md:text-8xl max-w-5xl leading-[1.02]">Connecting AI brands with the <span class="relative inline-block">creators<svg class="absolute -inset-x-3 -inset-y-3 w-[calc(100%+1.5rem)] h-[calc(100%+1.5rem)]" viewBox="0 0 300 100" preserveAspectRatio="none" aria-hidden="true"><ellipse class="ellipse" pathLength="1" cx="150" cy="50" rx="146" ry="44"/></svg></span> their customers trust.</h1>
<p class="mt-8 max-w-xl text-lg text-white/85">{SUB} {BODY}</p>
{hero_buttons("bg-white text-[#2a1745] rounded-full px-9 py-4 font-semibold", "border border-white text-white rounded-full px-9 py-4 font-semibold", "mt-8 flex flex-wrap justify-center gap-3")}
<a href="#who" aria-label="Scroll down" class="mt-10 text-2xl" style="animation: bob 1.8s ease-in-out infinite">↓</a></div></section>
<section id="who" class="bg-[#e6def2] px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">What we send brands.</h2><p class="mb-14 text-[#2a1745]/75 reveal">Each creator, with the numbers that matter. Example formats, not real creators.</p>
<div class="flex flex-wrap justify-center gap-8 mb-20">{phones}</div>
<p class="text-sm tracking-widest uppercase mb-6 reveal">We work with products like:</p><div class="cloud flex flex-wrap justify-center gap-3 max-w-3xl mx-auto reveal">{cloud}</div></section>
<section id="approach" class="px-6 py-24 max-w-5xl mx-auto text-center"><h2 class="serif text-4xl md:text-6xl mb-14 reveal">How it works for <em class="text-[#7a4fc0]">brands</em>.</h2><div class="grid md:grid-cols-3 gap-8">{steps}</div>
<div class="grid sm:grid-cols-3 gap-4 mt-16">{"".join(f'<div class="reveal bg-white rounded-2xl p-6 text-left"><p class="font-bold mb-1">{t}</p><p class="text-sm text-[#2a1745]/70">{d}</p></div>' for _i, t, d in BENEFITS)}</div></section>
<div class="bg-[#e6def2] text-[#2a1745]">{creator_section('light')}</div>
<section class="bg-[#2a1745] text-white px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">Let's get you matched.</h2><p class="text-white/75 mb-10 reveal">{CTA_SUB}</p>{forms('dark')}</section>
{footer(True)}</div>"""
    page("layout-smooth.html", "Layout test: Smooth-style | Gratovo", "Smooth-style",
         "Soft and editorial. Full-screen tinted hero with a hand-drawn ellipse and two buttons, phone-shaped example cards, category pill cloud, For Creators section, serif headings.",
         "bg-[#fcfaf6]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&amp;display=swap" rel="stylesheet">')


# ================================================================ 9. ADHESIVE
def build_adhesive():
    css = """
.hl { color:#0072b8; }
.step-tab { padding:12px 16px; border-bottom:3px solid transparent; font-weight:600; color:#686867; white-space:nowrap; }
.step-tab.is-active { color:#121212; border-color:#0072b8; }
.nav-blur { backdrop-filter: blur(10px); background: rgba(246,249,255,.85); }
"""
    rows = "".join(
        f'<details class="row"><summary><span class="sp-eyebrow">0{i+1}</span><span class="font-headline-md text-2xl font-bold">{t}</span><span class="hidden md:block text-secondary text-sm">Included</span><span class="tog">+</span></summary><p>{d}</p></details>'
        for i, (t, d) in enumerate(SERVICES))
    cats = [("AI assistants", "Reach people already learning to get more from AI chat and writing tools."),
            ("Automation", "Show workflow builders how your tool saves them hours, on screen."),
            ("Developer tools", "Put your product in front of developers who watch tutorials before they buy."),
            ("Productivity", "Get walked through in real workflows by creators who use tools like yours daily.")]
    cat_tabs = "".join(f'<button class="step-tab" role="tab">{c}</button>' for c, _ in cats)
    cat_panels = "".join(f'<div class="step-panel" role="tabpanel"><h3 class="sp-h text-3xl mb-3">{c}</h3><p class="text-[#3f403e] max-w-xl">{d}</p></div>' for c, d in cats)
    step_panels = "".join(
        f'<div class="step-panel"><p class="sp-eyebrow mb-2">Step {i+1} of 5</p><h3 class="sp-h text-3xl mb-3">{t}</h3><p class="text-[#3f403e] max-w-xl">{d}</p></div>' for i, (t, d) in enumerate(STEPS5))
    faq = "".join(f'<details class="row"><summary style="grid-template-columns:1fr 24px"><span class="font-headline-md text-xl font-bold">{q}</span><span class="tog">+</span></summary><p style="padding-left:0">{a}</p></details>' for q, a in FAQ)
    body = f"""
<div class="bg-[#f6f9ff] text-[#121212]">
<header class="nav-blur sticky top-0 z-50 border-b border-[#deded8]"><div class="max-w-[80rem] mx-auto px-6 h-[72px] flex items-center justify-between">
<a href="#">{wordmark("text-2xl")}</a>
<nav class="hidden md:flex gap-8 text-sm font-medium"><a href="#services">For brands</a><a href="#for-creators">For creators</a><a href="#process">How it works</a><a href="#faq">Questions</a></nav>
<a href="#workwithus" class="bg-primary-container text-white rounded-2xl px-5 py-3 text-sm font-semibold">{CTA}</a></div></header>
<main>
<section class="relative overflow-hidden"><div class="absolute inset-x-0 bottom-0 h-[55%] pointer-events-none">
<svg viewBox="0 0 760 430" preserveAspectRatio="none" class="w-full h-full" aria-hidden="true"><defs><linearGradient id="ga" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#0072b8" stop-opacity=".25"/><stop offset="1" stop-color="#0072b8" stop-opacity=".02"/></linearGradient></defs>
<path class="growth-area" d="M0 400 L90 385 L170 392 L250 360 L330 366 L410 330 L490 335 L560 230 L640 215 L700 110 L760 40 L760 430 L0 430 Z"/>
<path class="growth-path" pathLength="1" d="M0 400 L90 385 L170 392 L250 360 L330 366 L410 330 L490 335 L560 230 L640 215 L700 110 L760 40"/></svg>
<span class="stage" style="left:24%;bottom:22%;animation-delay:1.2s">Request</span><span class="stage" style="left:42%;bottom:33%;animation-delay:1.8s">Match</span>
<span class="stage" style="left:62%;bottom:50%;animation-delay:2.4s">Agree</span><span class="stage" style="left:82%;bottom:72%;animation-delay:3s">Launch</span></div>
<div class="relative max-w-[80rem] mx-auto px-6 pt-20 pb-72 md:pb-80">
<p class="sp-eyebrow mb-6">AI influencer marketing</p>
<h1 class="sp-h text-5xl md:text-8xl max-w-5xl">{HEAD_PARTS[0]}<span class="text-primary-container">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-6 text-lg text-[#3f403e] max-w-2xl">{SUB} {BODY}</p>
{hero_buttons("bg-primary-container text-white rounded-2xl px-6 py-4 font-semibold", "bg-[#121212] text-white rounded-2xl px-6 py-4 font-semibold", "mt-8 flex flex-wrap gap-3")}</div></section>
<section class="max-w-[80rem] mx-auto px-6 pb-24 grid md:grid-cols-2 gap-5">
<article class="sp-card p-9 reveal"><p class="sp-eyebrow mb-3">The buying journey</p><h3 class="sp-h text-3xl mb-3">People watch before they buy.</h3><p class="text-[#3f403e]">Before trying a new AI tool, people watch tutorials, compare options, and listen to creators they already trust.</p></article>
<article class="sp-card p-9 reveal" data-delay="120"><p class="sp-eyebrow mb-3">Our role</p><h3 class="sp-h text-3xl mb-3">We connect both sides.</h3><p class="text-[#3f403e]">We find the right creator for the brand, and the right brand deal for the creator, and keep the conversation moving between them.</p></article></section>
<section id="services" class="max-w-[80rem] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">For brands</p><h2 class="sp-h text-4xl md:text-6xl">What brands get.</h2></div><div class="max-w-4xl mx-auto border-b border-[#deded8]">{rows}</div></section>
<section class="bg-white py-24"><div class="max-w-[80rem] mx-auto px-6"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">Built for AI</p><h2 class="sp-h text-4xl md:text-6xl">Creator marketing works when the product needs showing.</h2></div>
<div data-stepper class="max-w-4xl mx-auto"><div class="flex justify-center gap-2 overflow-x-auto border-b border-[#deded8]" role="tablist">{cat_tabs}</div>
<div class="sp-card p-10 mt-8 min-h-[190px] relative">{cat_panels}<div class="absolute right-6 top-6 flex flex-col items-center gap-2"><button data-prev aria-label="Previous" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">←</button><span data-count class="text-xs text-[#686867]"></span><button data-next aria-label="Next" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">→</button></div></div></div></div></section>
{creator_section('light')}
<section id="process" class="max-w-[80rem] mx-auto px-6 py-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">How it works for brands</p><h2 class="sp-h text-4xl md:text-6xl">From message to live video.</h2></div>
<div data-stepper class="max-w-4xl mx-auto"><div class="sp-card p-10 min-h-[190px] relative">{step_panels}<div class="absolute right-6 top-6 flex flex-col items-center gap-2"><button data-prev aria-label="Previous step" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">←</button><span data-count class="text-xs text-[#686867]"></span><button data-next aria-label="Next step" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">→</button></div></div></div></section>
<section class="max-w-[80rem] mx-auto px-6 pb-24"><div class="sp-card p-10 md:p-14 grid md:grid-cols-2 gap-8 items-center reveal" style="border-left:4px solid #0072b8;border-top:1px solid #deded8"><div><p class="sp-eyebrow mb-3">Our approach</p><h3 class="sp-h text-4xl">Brands bring the product. Creators bring the audience.</h3></div><p class="text-[#3f403e]">We don't hand brands a spreadsheet of 200 names. We check each creator's real numbers, send the one to three that fit, and keep it simple for creators too.</p></div></section>
<section id="faq" class="max-w-4xl mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">Common questions</p><h2 class="sp-h text-4xl md:text-5xl">What to know before we work together.</h2></div><div class="border-b border-[#deded8]">{faq}</div></section>
<section class="px-6 pb-24"><div class="max-w-5xl mx-auto text-center reveal"><p class="sp-eyebrow mb-3">Let's work together</p><h2 class="sp-h text-4xl md:text-5xl mb-4">Brands and creators, start here.</h2><p class="text-[#3f403e] mb-8">{CTA_SUB}</p>{forms('light')}</div></section>
</main>
<footer class="bg-[#121212] text-white/75 py-14"><div class="max-w-[80rem] mx-auto px-6 grid md:grid-cols-3 gap-8"><div>{wordmark("text-2xl")}<p class="mt-4 text-sm">Connecting AI and SaaS brands with vetted creators, and creators with brand deals that fit.</p></div>
<div><p class="font-label-sm uppercase mb-3 text-white">Explore</p><div class="space-y-2 text-sm"><a class="block" href="#services">For brands</a><a class="block" href="#for-creators">For creators</a><a class="block" href="#faq">Questions</a></div></div>
<div><p class="font-label-sm uppercase mb-3 text-white">Contact</p><p class="text-sm">{EMAIL}</p><p class="text-sm mt-4"><a href="{ASSET}privacy-policy.html">Privacy</a> · <a href="{ASSET}terms-of-service.html">Terms</a></p></div></div>
<p class="max-w-[80rem] mx-auto px-6 mt-10 text-xs text-white/50">© 2026 Gratovo.</p></footer></div>"""
    page("layout-scalepledge.html", "Layout test: Scale Pledge-style | Gratovo", "Scale Pledge-style",
         "Editorial and light. Hero line draws itself with the four stages, accordion services, tabbed carousel, For Creators section, step carousel, FAQ.",
         "bg-[#f6f9ff]", css, body)


# ================================================================ 4. NSENTIVE
def build_nsentive():
    css = """
.dict-line { opacity:0; animation: fadein .9s ease forwards; }
.n-card { border:1px solid rgba(255,255,255,.55); border-radius:28px; padding:26px 26px 40px; }
.n-row { border-top:1px solid #3a3a3a; display:grid; grid-template-columns: 1fr 1.4fr 60px; gap:24px; padding:34px 0; align-items:start; }
@media (max-width: 768px) { .n-row { grid-template-columns: 1fr; gap: 10px; padding: 24px 0; } .n-row > span { display: none; } }
.loop { height: 340px; overflow: hidden; -webkit-mask-image: linear-gradient(transparent, #000 25%, #000 75%, transparent); mask-image: linear-gradient(transparent, #000 25%, #000 75%, transparent); }
.loop-track { animation: scrollup 14s linear infinite; }
.loop-track span { display:block; text-align:center; font-size:1.7rem; line-height:3.1rem; color:#fff; }
.loop-track span:nth-child(3n+2) { font-family: Georgia, serif; font-style: italic; }
"""
    cards = "".join(
        f'<div class="n-card reveal" data-delay="{i*100}"><div class="mb-14 text-white">{mat(ic, "text-3xl", False)}</div><h3 class="text-2xl font-semibold text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>'
        for i, (ic, t, d) in enumerate(BENEFITS))
    w = [("WHO", "Brands and creators in AI and SaaS: marketing managers and founders who want creators promoting their product, and creators who want brand deals that fit."),
         ("WHAT", "Brands get 1 to 3 vetted AI creators picked for their product. Creators get put forward to brands that fit their audience."),
         ("WHY", "People watching AI tutorials are looking for tools to try. A trusted creator showing a product reaches them at that moment."),
         ("WHERE", "YouTube, LinkedIn, X, and newsletters, wherever the right creator's audience is."),
         ("HOW", "Tell us about your product or your channel. We make the introduction. We take care of contracts, scripts, and posting."),
         ("WHEN", "We reply within 24 hours. Most deals go live within about a month.")]
    rows = "".join(f'<div class="n-row reveal"><h3 class="text-5xl md:text-6xl font-semibold text-[#161616]">{a}</h3><p class="text-[#555] text-lg">{c}</p><span class="text-3xl text-[#161616]">↘</span></div>' for a, c in w)
    who = [("Marketing managers", "Hand off the searching, vetting, and chasing. Keep the final say."),
           ("Founders", "Get your product in front of the right audience without learning creator marketing first."),
           ("Creators", "Get brand deals that fit your channel, without cold outreach or endless email threads.")]
    whorows = "".join(f'<div class="n-row reveal"><h3 class="text-4xl md:text-5xl font-semibold text-[#161616]">{a}</h3><p class="text-[#555] text-lg">{b}</p><span class="text-3xl text-[#161616]">↘</span></div>' for a, b in who)
    flow = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="text-white/40 text-sm mb-3">0{i+1}</p><h3 class="text-4xl font-semibold text-white mb-3">{t}</h3><p class="text-white/70">{d}</p></div>' for i, (t, d) in enumerate(STEPS4))
    loop_items = "".join(f"<span>{x}</span>" for x in ["no cold emails", "no chasing replies", "no guessing who's legit", "no endless threads", "just the right match"] * 2)
    body = f"""
<div class="bg-black text-white">
<header class="max-w-[1280px] mx-auto px-6 h-24 flex items-center justify-between"><a href="#">{wordmark("text-4xl")}</a><a href="#workwithus" class="bg-primary-container text-white rounded-full px-8 py-3 font-medium">Let's Talk</a></header>
<main>
<section class="text-center px-6 pt-16 pb-24">
<h1 class="dict-line text-6xl md:text-8xl font-semibold tracking-tight" style="animation-delay:.2s">match</h1>
<p class="dict-line text-3xl md:text-4xl text-white/35 mt-3" style="animation-delay:.9s">/mætʃ/</p>
<p class="dict-line text-3xl md:text-4xl font-semibold mt-1" style="animation-delay:1.5s">noun</p>
<p class="dict-line text-xl md:text-2xl mt-8 max-w-2xl mx-auto text-white/90" style="animation-delay:2.1s">A creator whose audience fits your product. A brand deal that fits your channel. We find both.</p>
{hero_buttons("bg-white text-black rounded-full px-10 py-4 font-semibold", "border border-white text-white rounded-full px-10 py-4 font-semibold", "dict-line mt-10 flex flex-wrap justify-center gap-4\" style=\"animation-delay:2.7s")}</section>
<section class="max-w-[1280px] mx-auto px-6 pb-28 grid md:grid-cols-3 gap-6">{cards}</section>
<div class="bg-white text-[#161616]"><div class="max-w-[1280px] mx-auto px-6 py-24">
<h2 class="text-5xl md:text-7xl font-semibold tracking-tight mb-14 reveal">The short version.</h2><div class="border-b border-[#3a3a3a]">{rows}</div></div>
<div class="max-w-[1280px] mx-auto px-6 pb-24"><h2 class="text-5xl md:text-7xl font-semibold tracking-tight mb-14 reveal">Who it's for.</h2><div class="border-b border-[#3a3a3a]">{whorows}</div></div></div>
{creator_section('dark')}
<section class="max-w-[1280px] mx-auto px-6 py-28"><h2 class="text-5xl md:text-7xl font-semibold tracking-tight text-center mb-16 reveal">Four steps for brands.</h2><div class="grid md:grid-cols-4 gap-10">{flow}</div></section>
<section class="bg-primary-container px-6 py-24"><div class="max-w-[1200px] mx-auto grid md:grid-cols-[1fr_2.4fr] gap-10 items-center">
<div class="loop hidden md:block"><div class="loop-track">{loop_items}</div></div>
<div class="bg-black rounded-[28px] p-8 md:p-10"><h2 class="text-center text-3xl font-semibold mb-2">Let's Talk</h2><p class="text-center text-white/70 mb-6">{CTA_SUB}</p>{forms('dark')}</div></div></section>
</main>{footer(True)}</div>"""
    page("layout-nsentive.html", "Layout test: Nsentive-style | Gratovo", "Nsentive-style",
         "Black to white to brand blue. Dictionary-style hero that fades in line by line, outlined cards, ruled rows (brands, creators), scrolling word list beside the forms.",
         "bg-black", css, body)


# ================================================================ 5. APOLLO
def build_apollo():
    css = """
@keyframes twinkle { 0%,100% { opacity:.15; } 50% { opacity:.9; } }
@keyframes shoot { 0% { transform: translate(0,0) rotate(-35deg); opacity:0; } 8% { opacity:1; } 30% { transform: translate(-420px,300px) rotate(-35deg); opacity:0; } 100% { opacity:0; } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes counter { to { transform: rotate(-360deg); } }
.shoot { position:absolute; top:8%; right:12%; width:120px; height:2px; background:linear-gradient(90deg, rgba(255,255,255,0), #fff); animation: shoot 7s 2s infinite; }
.glass { background: linear-gradient(160deg, rgba(255,255,255,.08), rgba(255,255,255,.02)); border:1px solid rgba(255,255,255,.12); border-radius:28px; backdrop-filter: blur(10px); }
.grad-text { background: linear-gradient(90deg, #ffd9a8, #ff8fb3, #b88cff); -webkit-background-clip:text; background-clip:text; color:transparent; }
.chip { position:absolute; background: rgba(20,30,70,.9); border:1px solid rgba(255,255,255,.18); border-radius:16px; padding:10px 14px; font-size:13px; color:#fff; animation: floaty 6s ease-in-out infinite; box-shadow:0 10px 30px rgba(0,0,0,.4); }
.orbit { position:relative; width:260px; height:260px; margin:auto; }
.orbit .ring { position:absolute; inset:0; border:1px dashed rgba(255,255,255,.25); border-radius:50%; animation: spin 24s linear infinite; }
.orbit .ring i { position:absolute; width:52px; height:52px; margin:-26px; border-radius:16px; background:#fff; color:#16293d; display:flex; align-items:center; justify-content:center; animation: counter 24s linear infinite; }
.orbit .core { position:absolute; inset:88px; border-radius:24px; background: linear-gradient(135deg,#0a5c9e,#6a54e8); display:flex; align-items:center; justify-content:center; box-shadow:0 0 50px rgba(106,84,232,.6); }
.ghost { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size: clamp(120px, 24vw, 340px); font-weight:800; color: rgba(255,255,255,.05); pointer-events:none; letter-spacing:-.04em; }
.beam { height:1px; background: linear-gradient(90deg, transparent, rgba(150,130,255,.8), transparent); background-size:200% 100%; animation: shimmer 4s linear infinite; }
@keyframes shimmer { to { background-position: -200% 0; } }
"""
    blocks = [("It's that easy.", "Send us a short message. We do the searching, vetting, and chasing."),
              ("Peace of mind.", "Every creator is checked for real views, engagement, and audience location first."),
              ("Your product, shown properly.", "Creators demo your tool in a real workflow, for an audience that wants to try it."),
              ("Nothing goes live unseen.", "You approve the video before it posts.")]
    bl = "".join(f'<div class="glass p-8 reveal" data-delay="{i*100}"><h3 class="font-headline-md text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>' for i, (t, d) in enumerate(blocks))
    stats = "".join(f'<div class="text-center"><p class="text-5xl font-bold text-white">{v}</p><p class="text-white/65 mt-2 max-w-[200px] mx-auto">{l}</p></div>' for v, l in STATS[:3])
    steps = "".join(f'<div class="glass p-7 reveal" data-delay="{i*90}"><span class="grad-text text-4xl font-bold">0{i+1}</span><h3 class="font-headline-md text-white mt-3 mb-2">{t}</h3><p class="text-white/70 text-sm">{d}</p></div>' for i, (t, d) in enumerate(STEPS5))
    plat_icons = ["smart_display", "work", "tag", "mail"]
    orbit_items = "".join(
        f'<i style="left:{50 + 50*math.cos(a)}%;top:{50 + 50*math.sin(a)}%">{mat(ic, "text-2xl", True)}</i>'
        for ic, a in zip(plat_icons, [0, 1.5708, 3.1416, 4.7124]))
    pill = "inline-block border border-white/25 bg-white/10 rounded-full px-7 py-3 text-sm font-semibold"
    body = f"""
<div class="bg-[#050a1f] text-white relative overflow-hidden">
<div id="stars" class="absolute inset-0 pointer-events-none"></div><div class="shoot"></div>
<header class="relative z-20 max-w-[1280px] mx-auto px-6 h-20 flex items-center justify-between"><a href="#">{wordmark("text-3xl")}</a>
<nav class="hidden md:flex gap-1 border border-white/15 rounded-full px-2 py-2 text-sm bg-white/5"><a class="px-4 py-1.5 rounded-full bg-white/10" href="#">Home</a><a class="px-4 py-1.5" href="#brands">For brands</a><a class="px-4 py-1.5" href="#for-creators">For creators</a><a class="px-4 py-1.5" href="#process">How it works</a></nav>
<a href="#workwithus" class="border border-white/25 bg-white/5 rounded-lg px-5 py-2 text-sm">Contact</a></header>
<main class="relative z-10">
<section class="text-center px-6 pt-14 pb-12"><h1 class="font-display-lg text-4xl md:text-7xl max-w-5xl mx-auto leading-[1.05]">{HEAD_PARTS[0]}<span class="grad-text">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-5 text-white/70 text-lg max-w-2xl mx-auto">{SUB}</p></section>
<section class="max-w-[1280px] mx-auto px-6 grid md:grid-cols-2 gap-6 pb-24">
<div id="brands" class="glass p-8 md:p-10 text-center relative overflow-hidden min-h-[470px] reveal"><h2 class="font-display-lg text-4xl mb-3">for brands.</h2><p class="text-white/70 mb-6">1 to 3 vetted AI creators picked for your product.</p>
<a href="#workwithus" class="{pill}">{CTA}</a>
<div class="relative h-56 mt-6"><div class="chip" style="left:6%;top:6%;--r:-6deg">Creator A · 42K avg views</div><div class="chip" style="left:34%;top:38%;--r:4deg;animation-delay:1s">Creator B · 5.1% engagement</div><div class="chip" style="left:12%;top:70%;--r:-3deg;animation-delay:2s">Creator C · 46% US audience</div></div>
<p class="absolute bottom-3 inset-x-0 text-[11px] text-white/45 uppercase tracking-wider">Example format</p></div>
<div class="glass p-8 md:p-10 text-center min-h-[470px] reveal" data-delay="120"><h2 class="font-display-lg text-4xl mb-3">for creators.</h2><p class="text-white/70 mb-6">Brand deals that fit your channel. YouTube, LinkedIn, X, and newsletters.</p>
<a href="#creators" class="{pill}">{CTA_C}</a>
<div class="orbit mt-8"><div class="core">{mat('rocket_launch', 'text-4xl text-white')}</div><div class="ring">{orbit_items}</div></div></div></section>
<section class="max-w-[1280px] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><span class="inline-block border border-white/20 rounded-full px-4 py-1 text-sm mb-4">What brands get ✦</span><h2 class="font-display-lg text-4xl md:text-6xl">A simpler way to work with AI creators.</h2></div><div class="grid md:grid-cols-2 gap-5">{bl}</div></section>
<section class="relative max-w-[1100px] mx-auto px-6 py-24"><div class="ghost" aria-hidden="true">1-3</div><div class="relative"><div class="beam mb-12"></div><div class="grid md:grid-cols-3 gap-10">{stats}</div><div class="beam mt-12"></div></div><p class="relative text-center text-white/60 mt-8">Every creator we recommend passes these checks first.</p></section>
{creator_section('dark')}
<section id="process" class="max-w-[1280px] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><h2 class="font-display-lg text-4xl md:text-6xl">How a deal works with us.</h2></div><div class="grid md:grid-cols-5 gap-4">{steps}</div></section>
<section class="max-w-[1100px] mx-auto px-6 pb-24"><div class="glass p-8 md:p-14 text-center reveal"><h2 class="font-display-lg text-4xl md:text-6xl mb-3">Ready for <span class="grad-text">take-off?</span></h2><p class="text-white/70 mb-10">{CTA_SUB}</p>{forms('dark')}</div></section>
</main>{footer(True)}</div>"""
    page("layout-apollo.html", "Layout test: Apollo-style | Gratovo", "Apollo-style",
         "Dark space theme. Twinkling stars and a shooting star, a glass card for brands and one for creators, floating chips, orbiting platform icons, ghost number behind the stats.",
         "bg-[#050a1f]", css, body)


# ================================================================ 6. RIGHT CLICK
def build_rightclick():
    css = """
.display { font-family: 'Anton', 'Plus Jakarta Sans', sans-serif; text-transform: uppercase; letter-spacing: .01em; line-height: .95; }
.mono { font-family: 'JetBrains Mono', monospace; }
.rc-cap { color:#9ad6f7; }
.rc-btn { border:1px solid #9ad6f7; color:#9ad6f7; border-radius:999px; padding:18px 28px; font-size:1.6rem; display:flex; justify-content:space-between; align-items:center; transition:.25s; }
.rc-btn:hover { background:#9ad6f7; color:#050a14; }
.rc-btn:hover span { color:#050a14 !important; }
.fcard { position:absolute; width:150px; border-radius:18px; padding:14px; color:#fff; box-shadow:0 14px 40px rgba(0,0,0,.5); animation: floaty 7s ease-in-out infinite; }
#scroll-progress-wrap { position:fixed; left:10px; top:90px; bottom:40px; width:3px; z-index:50; }
#scroll-progress { width:3px; background:#9ad6f7; height:0; }
"""
    cards = [("30K+", "avg views", "left:2%;top:6%;--r:-8deg;background:linear-gradient(135deg,#6a54e8,#b8286e)", 0),
             ("3-8%", "engagement", "right:3%;top:2%;--r:6deg;background:linear-gradient(135deg,#0a5c9e,#0072b8)", 1.2),
             ("35%+", "target audience", "left:6%;top:48%;--r:5deg;background:linear-gradient(135deg,#b8286e,#ff7a59)", 2.2),
             ("1-3", "creators, not 200", "right:2%;top:42%;--r:-5deg;background:linear-gradient(135deg,#0072b8,#1fb6a6)", 3.2)]
    fc = "".join(f'<div class="fcard hidden md:block" style="{st};animation-delay:{d}s"><p class="display text-4xl">{v}</p><p class="text-xs uppercase tracking-wider opacity-90">{l}</p></div>' for v, l, st, d in cards)
    pills = [("BRANDS", "Vetted AI creators for your product.", "#workwithus"),
             ("CREATORS", "Brand deals that fit your channel.", "#creators"),
             ("HOW IT WORKS", "Four steps, from message to live video.", "#process")]
    pl = "".join(f'<a href="{h}" class="rc-btn reveal mono" data-delay="{i*100}"><span>{a}</span><span class="text-base text-white/70 max-w-md text-right hidden md:block">{b}</span><span>↗</span></a>' for i, (a, b, h) in enumerate(pills))
    ex = "".join(example_card(i) for i in range(3))
    steps = "".join(f'<div class="reveal border-l border-[#9ad6f7]/50 pl-5" data-delay="{i*100}"><p class="display text-4xl rc-cap">0{i+1}</p><h3 class="mono text-lg font-semibold mt-2">{t}</h3><p class="mono text-white/70 text-sm mt-1">{d}</p></div>' for i, (t, d) in enumerate(STEPS4))
    hb = hero_buttons("bg-[#9ad6f7] text-[#050a14] font-bold rounded-full px-8 py-4", "border border-[#9ad6f7] text-[#9ad6f7] font-bold rounded-full px-8 py-4", "mt-8 flex flex-wrap justify-center gap-4")
    body = f"""
<div class="bg-[#050a14] text-white mono">
<div id="scroll-progress-wrap" aria-hidden="true"><div id="scroll-progress"></div></div>
<header class="relative z-20 flex items-center justify-between px-6 md:px-12 h-24"><span class="mono text-xs rc-cap hidden md:block"><span id="scroll-progress-num">0</span> / 100</span>
<a href="#" class="md:absolute md:left-1/2 md:-translate-x-1/2">{wordmark("text-3xl")}</a><a href="#workwithus" class="ml-auto bg-white/10 rc-cap rounded-full px-5 py-2 text-xs tracking-widest">WORK WITH US</a></header>
<main>
<section class="relative min-h-[88vh] flex flex-col items-center justify-center text-center px-6 overflow-hidden">{fc}
<h1 class="display rc-cap text-[clamp(3rem,10vw,8.5rem)] max-w-6xl relative z-10">{HEADLINE}</h1>
<p class="relative z-10 mt-6 max-w-xl text-white/80">{SUB}</p><div class="relative z-10">{hb}</div></section>
<section class="max-w-5xl mx-auto px-6 pb-24"><div class="border border-[#9ad6f7] rounded-[32px] p-10 md:p-14 text-center reveal"><p class="text-xl leading-relaxed">We're <b class="rc-cap">Gratovo</b>. We connect AI brands with vetted creators, and creators with brand deals that fit. {BODY}</p></div></section>
<section class="max-w-5xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-10 reveal">Who we work with</h2><div class="space-y-5">{pl}</div></section>
<section class="max-w-6xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-3 reveal">What we send brands</h2><p class="text-white/70 mb-10 reveal">Hover a card. Example formats, not real creators.</p><div class="grid sm:grid-cols-3 gap-5 reveal">{ex}</div></section>
{creator_section('dark', head_cls='display')}
<section id="process" class="max-w-6xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-12 reveal">Four steps for brands</h2><div class="grid md:grid-cols-4 gap-8">{steps}</div></section>
<section class="max-w-5xl mx-auto px-6 pb-28 text-center"><h2 class="display rc-cap text-6xl md:text-8xl mb-6 reveal">Ready to get started?</h2><p class="text-white/70 mb-10">{CTA_SUB}</p>{forms('dark')}</section>
</main>{footer(True)}</div>"""
    page("layout-rightclick.html", "Layout test: Right Click-style | Gratovo", "Right Click-style",
         "Bold and edgy. Giant condensed headline with floating stat cards and two buttons, scroll progress counter on the left edge, outlined pill rows (brands, creators), big closing line.",
         "bg-[#050a14]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;display=swap" rel="stylesheet">')


# ================================================================ 7. MINDSHARE
def build_mindshare():
    css = """
.ms { font-family: 'Anton', 'Plus Jakarta Sans', sans-serif; text-transform: uppercase; letter-spacing: -.01em; line-height: .92; }
.pill { border-radius:999px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; font-size:.8rem; padding:18px 30px; display:inline-flex; gap:8px; align-items:center; }
.tag { border:1px solid currentColor; border-radius:999px; padding:6px 14px; font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.side { position:absolute; left:18px; top:40px; writing-mode:vertical-rl; transform:rotate(180deg); font-size:.7rem; letter-spacing:.25em; opacity:.6; text-transform:uppercase; }
@keyframes ticker { to { transform: translateX(-50%); } }
.ticker .marquee-track { animation: ticker 22s linear infinite; }
"""
    plats = "".join(f'<span class="ms text-4xl md:text-5xl text-[#16293d]/80">{p}</span>' for p in PLATFORMS * 3)
    svc = "".join(f'<div class="reveal border-t border-white/20 pt-6" data-delay="{i*90}"><p class="text-primary-fixed-dim text-xs font-bold tracking-widest mb-2">0{i+1}</p><h3 class="ms text-3xl mb-2">{t}</h3><p class="text-white/65">{d}</p></div>' for i, (t, d) in enumerate(SERVICES[:4]))
    props = [("Zero outreach", "We contact the creators. You only hear about the ones worth your time."),
             ("Real numbers", "Views, engagement, and audience location, checked before you see a name."),
             ("You approve it", "Nothing goes live until you've seen the video.")]
    pr = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="font-bold text-lg">{a}</p><p class="text-[#0b1623]/90">{b}</p></div>' for i, (a, b) in enumerate(props))
    cprops = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="font-bold text-lg">{t}</p><p class="text-[#0b1623]/90">{d}</p></div>' for i, (_ic, t, d) in enumerate(CREATOR_BENEFITS))
    body = f"""
<div class="bg-[#16293d] text-white">
<section class="relative bg-primary-container text-[#0b1623] min-h-screen flex flex-col">
<header class="flex items-center justify-between px-6 md:px-10 h-20"><a href="#" class="bg-white rounded-xl px-3 py-1">{wordmark("text-2xl")}</a>
<nav class="flex items-center gap-6 text-xs tracking-widest uppercase font-semibold"><a class="hidden sm:block" href="#brands">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="bg-[#0b1623] text-white rounded-full px-5 py-2">Contact</a></nav></header>
<div class="flex-1 flex flex-col items-center justify-center text-center px-6"><h1 class="ms text-[clamp(4.5rem,17vw,15rem)] text-[#0b1623]">Gratovo</h1>
<p class="mt-6 text-lg font-medium text-[#0b1623]">[ {HEADLINE} ]</p>
<div class="mt-8 flex flex-wrap justify-center gap-3"><a href="#workwithus" class="pill bg-[#0b1623] text-white">{CTA} →</a><a href="#creators" class="pill border border-[#0b1623]/60">{CTA_C}</a></div></div>
<div class="ticker marquee py-6 border-t border-[#0b1623]/20"><div class="marquee-track">{plats}{plats}</div></div></section>
<section id="why" class="px-6 md:px-16 py-24 max-w-[1200px] mx-auto"><p class="text-primary-fixed-dim font-bold tracking-widest text-xs uppercase mb-3 reveal">For brands</p><h2 class="ms text-5xl md:text-7xl mb-14 reveal">Everything between "hello" and "live".</h2><div class="grid md:grid-cols-4 gap-8">{svc}</div></section>
<section class="bg-[#101d2e] px-6 py-20 text-center"><h2 class="ms text-5xl md:text-7xl mb-10 reveal">Where it runs</h2><div class="flex flex-wrap justify-center gap-3 reveal">{"".join(f'<span class="tag text-primary-fixed-dim">{p}</span>' for p in PLATFORMS)}</div></section>
<section class="px-6 md:px-16 py-24 max-w-[1200px] mx-auto grid md:grid-cols-2 gap-14 items-center"><div><p class="text-primary-fixed-dim text-xs font-bold tracking-widest uppercase mb-4 reveal">Our approach</p>
<h2 class="ms text-6xl md:text-8xl reveal">We send 1 to 3 names. <span class="text-accent-container">Not 200.</span></h2><div class="h-1 w-14 bg-accent mt-6"></div></div>
<p class="text-white/65 text-lg reveal">Most creator lists are long spreadsheets that someone still has to check. We check first. Brands get the few creators whose real numbers fit their product, and creators get introduced to brands that fit theirs.</p></section>
<section id="brands" class="relative bg-primary-container text-[#0b1623] px-6 py-24 text-center"><span class="side">For brands</span>
<h2 class="ms text-6xl md:text-9xl max-w-5xl mx-auto reveal">No guessing. Just the right creators.</h2><div class="h-1 w-14 bg-[#0b1623] mx-auto my-6"></div>
<div class="max-w-3xl mx-auto grid md:grid-cols-3 gap-8 text-left my-10">{pr}</div>
<a href="#workwithus" class="pill bg-[#0b1623] text-white">{CTA} →</a></section>
<section id="for-creators" class="relative bg-[#16293d] text-white px-6 py-24 text-center"><span class="side">For creators</span>
<h2 class="ms text-6xl md:text-9xl max-w-5xl mx-auto reveal">Brand deals that <span class="text-accent-container">fit your channel.</span></h2><div class="h-1 w-14 bg-accent mx-auto my-6"></div>
<div class="max-w-3xl mx-auto grid md:grid-cols-2 gap-8 text-left my-10 text-white">{"".join(f'<div class="reveal"><p class="font-bold text-lg">{t}</p><p class="text-white/70">{d}</p></div>' for _ic, t, d in CREATOR_BENEFITS)}</div>
<a href="#creators" class="pill bg-primary-container text-[#0b1623]">{CTA_C} →</a></section>
<section class="px-6 py-24 bg-[#16293d]"><div class="max-w-5xl mx-auto bg-primary-container text-[#0b1623] rounded-[28px] p-8 md:p-14 text-center reveal"><h2 class="ms text-5xl md:text-7xl mb-4">Let's get you matched.</h2><p class="mb-8 opacity-90">{CTA_SUB}</p>{forms('color')}</div></section>
{footer(True)}</div>"""
    page("layout-mindshare.html", "Layout test: MindShare-style | Gratovo", "MindShare-style",
         "Giant type on alternating blue and navy bands. Full-screen wordmark hero with two buttons, platform ticker, For Brands and For Creators bands, rounded closing card.",
         "bg-[#16293d]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;display=swap" rel="stylesheet">')


# ================================================================ 8. SMOOTH
def build_smooth():
    css = """
.serif { font-family: 'Fraunces', Georgia, serif; }
.hero-bg { background: linear-gradient(120deg, #2b1a4d, #0a5c9e, #5b2a86, #16293d); background-size: 300% 300%; animation: drift 16s ease-in-out infinite; }
@keyframes drift { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
.ellipse { fill:none; stroke:#fff; stroke-width:2.5; stroke-dasharray:1; stroke-dashoffset:1; animation: drawline 1.6s 1s ease-out forwards; }
@keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(8px); } }
.phone { width:200px; border:6px solid #2a1745; border-radius:32px; background:#fff; box-shadow:0 20px 40px rgba(42,23,69,.25); overflow:hidden; }
.cloud span { background:#fcfaf6; border-radius:999px; padding:10px 20px; font-weight:700; font-size:.78rem; letter-spacing:.06em; text-transform:uppercase; color:#2a1745; }
"""
    tags = ["AI assistants", "Automation", "Developer tools", "Productivity", "SaaS", "No-code", "AI agents", "Analytics", "Writing tools", "Design tools", "Meeting tools", "Research tools"]
    cloud = "".join(f"<span>{t}</span>" for t in tags)
    phones = "".join(
        f"""<div class="phone reveal" data-delay="{i*120}" style="margin-top:{[0,36,0][i]}px"><div class="bg-gradient-to-br from-[#2a1745] to-[#0a5c9e] h-64 flex flex-col items-center justify-center text-white text-center p-4">{mat('account_circle','text-6xl text-white/80')}<p class="serif text-xl mt-2">{EXAMPLES[i][0]}</p><p class="text-xs text-white/70">{EXAMPLES[i][1]}</p></div>
<div class="p-4 text-[#2a1745]"><p class="text-[10px] uppercase tracking-widest text-[#2a1745]/60 mb-2">Example format</p><div class="flex justify-between text-center"><div><p class="font-bold">{EXAMPLES[i][2]}</p><p class="text-[10px] uppercase">avg views</p></div><div><p class="font-bold">{EXAMPLES[i][3]}</p><p class="text-[10px] uppercase">engage</p></div><div><p class="font-bold">{EXAMPLES[i][4]}</p><p class="text-[10px] uppercase">US</p></div></div></div></div>"""
        for i in range(3))
    steps = "".join(f'<div class="reveal text-center px-4" data-delay="{i*120}"><p class="serif text-6xl text-[#7a4fc0]">{i+1}</p><h3 class="serif text-2xl text-[#2a1745] mt-2 mb-2">{t}</h3><p class="text-[#2a1745]/75">{d}</p></div>' for i, (t, d) in enumerate(STEPS3))
    body = f"""
<div class="bg-[#fcfaf6] text-[#2a1745]">
<section class="hero-bg relative min-h-screen text-white flex flex-col">
<div class="absolute inset-0 bg-[#2a1745]/45"></div>
<header class="relative z-10 flex items-center justify-between px-6 md:px-10 h-24"><a href="#">{wordmark("text-3xl")}</a>
<nav class="flex items-center gap-7 text-sm font-medium"><a class="hidden sm:block" href="#who">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="border border-white rounded-full px-5 py-2">Contact</a></nav></header>
<div class="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 pb-10">
<p class="text-xs font-semibold tracking-[.2em] uppercase mb-6">AI brands and creators, introduced</p>
<h1 class="serif text-5xl md:text-8xl max-w-5xl leading-[1.02]">Connecting AI brands with the <span class="relative inline-block">creators<svg class="absolute -inset-x-3 -inset-y-3 w-[calc(100%+1.5rem)] h-[calc(100%+1.5rem)]" viewBox="0 0 300 100" preserveAspectRatio="none" aria-hidden="true"><ellipse class="ellipse" pathLength="1" cx="150" cy="50" rx="146" ry="44"/></svg></span> their customers trust.</h1>
<p class="mt-8 max-w-xl text-lg text-white/85">{SUB} {BODY}</p>
{hero_buttons("bg-white text-[#2a1745] rounded-full px-9 py-4 font-semibold", "border border-white text-white rounded-full px-9 py-4 font-semibold", "mt-8 flex flex-wrap justify-center gap-3")}
<a href="#who" aria-label="Scroll down" class="mt-10 text-2xl" style="animation: bob 1.8s ease-in-out infinite">↓</a></div></section>
<section id="who" class="bg-[#e6def2] px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">What we send brands.</h2><p class="mb-14 text-[#2a1745]/75 reveal">Each creator, with the numbers that matter. Example formats, not real creators.</p>
<div class="flex flex-wrap justify-center gap-8 mb-20">{phones}</div>
<p class="text-sm tracking-widest uppercase mb-6 reveal">We work with products like:</p><div class="cloud flex flex-wrap justify-center gap-3 max-w-3xl mx-auto reveal">{cloud}</div></section>
<section id="approach" class="px-6 py-24 max-w-5xl mx-auto text-center"><h2 class="serif text-4xl md:text-6xl mb-14 reveal">How it works for <em class="text-[#7a4fc0]">brands</em>.</h2><div class="grid md:grid-cols-3 gap-8">{steps}</div>
<div class="grid sm:grid-cols-3 gap-4 mt-16">{"".join(f'<div class="reveal bg-white rounded-2xl p-6 text-left"><p class="font-bold mb-1">{t}</p><p class="text-sm text-[#2a1745]/70">{d}</p></div>' for _i, t, d in BENEFITS)}</div></section>
<div class="bg-[#e6def2] text-[#2a1745]">{creator_section('light')}</div>
<section class="bg-[#2a1745] text-white px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">Let's get you matched.</h2><p class="text-white/75 mb-10 reveal">{CTA_SUB}</p>{forms('dark')}</section>
{footer(True)}</div>"""
    page("layout-smooth.html", "Layout test: Smooth-style | Gratovo", "Smooth-style",
         "Soft and editorial. Full-screen tinted hero with a hand-drawn ellipse and two buttons, phone-shaped example cards, category pill cloud, For Creators section, serif headings.",
         "bg-[#fcfaf6]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&amp;display=swap" rel="stylesheet">')


# ================================================================ 9. ADHESIVE
def build_adhesive():
    css = """
.hl { color:#0072b8; }
.diagram { height:150px; position:relative; background:#f4f9fe; border-bottom:1px solid #d5e6f4; overflow:hidden; }
.node { position:absolute; background:#fff; border:1px solid #c5d5e4; border-radius:8px; padding:4px 10px; font:11px/1.2 'JetBrains Mono', monospace; text-transform:uppercase; color:#3e4c5e; }
@keyframes pulse2 { 0% { box-shadow:0 0 0 0 rgba(0,114,184,.45); } 100% { box-shadow:0 0 0 22px rgba(0,114,184,0); } }
.pulse { animation: pulse2 2s ease-out infinite; }
.carousel { display:flex; gap:20px; overflow-x:auto; scroll-snap-type:x mandatory; padding-bottom:8px; scrollbar-width:none; }
.carousel::-webkit-scrollbar { display:none; }
.carousel > article { flex:0 0 300px; scroll-snap-align:start; background:#fff; border:1px solid #d5e6f4; border-radius:14px; overflow:hidden; }
.step-tab { padding:10px 16px; border-radius:10px; font-weight:600; color:#3e4c5e; }
.step-tab.is-active { background:#fff; color:#0a5c9e; box-shadow:0 1px 4px rgba(0,0,0,.12); }
"""
    # the animated, tabbed process section is the one on the real homepage (single source of truth)
    idx = (Path(__file__).resolve().parent.parent.parent / "index.html").read_text(encoding="utf-8")
    proc = re.search(r'<section id="how-it-works".*?</section>', idx, re.S).group(0)
    cats = [("AI assistants", "Reach people already learning to get more from AI chat and writing tools."),
            ("Automation", "Show workflow builders how your tool saves them hours, on screen."),
            ("Developer tools", "Put your product in front of developers who watch tutorials before they buy."),
            ("Productivity", "Get walked through in real workflows by creators who use tools like yours daily.")]
    cat_tabs = "".join(f'<button class="step-tab" role="tab">{c}</button>' for c, _ in cats)
    cat_panels = "".join(f'<div class="step-panel" role="tabpanel"><h3 class="sp-h text-3xl mb-3">{c}</h3><p class="text-[#3f403e] max-w-xl">{d}</p></div>' for c, d in cats)
    step_panels = "".join(
        f'<div class="step-panel"><p class="sp-eyebrow mb-2">Step {i+1} of 5</p><h3 class="sp-h text-3xl mb-3">{t}</h3><p class="text-[#3f403e] max-w-xl">{d}</p></div>' for i, (t, d) in enumerate(STEPS5))
    faq = "".join(f'<details class="row"><summary style="grid-template-columns:1fr 24px"><span class="font-headline-md text-xl font-bold">{q}</span><span class="tog">+</span></summary><p style="padding-left:0">{a}</p></details>' for q, a in FAQ)
    body = f"""
<div class="bg-[#f6f9ff] text-[#121212]">
<header class="nav-blur sticky top-0 z-50 border-b border-[#deded8]"><div class="max-w-[80rem] mx-auto px-6 h-[72px] flex items-center justify-between">
<a href="#">{wordmark("text-2xl")}</a>
<nav class="hidden md:flex gap-8 text-sm font-medium"><a href="#services">For brands</a><a href="#for-creators">For creators</a><a href="#process">How it works</a><a href="#faq">Questions</a></nav>
<a href="#workwithus" class="bg-primary-container text-white rounded-2xl px-5 py-3 text-sm font-semibold">{CTA}</a></div></header>
<main>
<section class="relative overflow-hidden"><div class="absolute inset-x-0 bottom-0 h-[55%] pointer-events-none">
<svg viewBox="0 0 760 430" preserveAspectRatio="none" class="w-full h-full" aria-hidden="true"><defs><linearGradient id="ga" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#0072b8" stop-opacity=".25"/><stop offset="1" stop-color="#0072b8" stop-opacity=".02"/></linearGradient></defs>
<path class="growth-area" d="M0 400 L90 385 L170 392 L250 360 L330 366 L410 330 L490 335 L560 230 L640 215 L700 110 L760 40 L760 430 L0 430 Z"/>
<path class="growth-path" pathLength="1" d="M0 400 L90 385 L170 392 L250 360 L330 366 L410 330 L490 335 L560 230 L640 215 L700 110 L760 40"/></svg>
<span class="stage" style="left:24%;bottom:22%;animation-delay:1.2s">Request</span><span class="stage" style="left:42%;bottom:33%;animation-delay:1.8s">Match</span>
<span class="stage" style="left:62%;bottom:50%;animation-delay:2.4s">Agree</span><span class="stage" style="left:82%;bottom:72%;animation-delay:3s">Launch</span></div>
<div class="relative max-w-[80rem] mx-auto px-6 pt-20 pb-72 md:pb-80">
<p class="sp-eyebrow mb-6">AI influencer marketing</p>
<h1 class="sp-h text-5xl md:text-8xl max-w-5xl">{HEAD_PARTS[0]}<span class="text-primary-container">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-6 text-lg text-[#3f403e] max-w-2xl">{SUB} {BODY}</p>
{hero_buttons("bg-primary-container text-white rounded-2xl px-6 py-4 font-semibold", "bg-[#121212] text-white rounded-2xl px-6 py-4 font-semibold", "mt-8 flex flex-wrap gap-3")}</div></section>
<section class="max-w-[80rem] mx-auto px-6 pb-24 grid md:grid-cols-2 gap-5">
<article class="sp-card p-9 reveal"><p class="sp-eyebrow mb-3">The buying journey</p><h3 class="sp-h text-3xl mb-3">People watch before they buy.</h3><p class="text-[#3f403e]">Before trying a new AI tool, people watch tutorials, compare options, and listen to creators they already trust.</p></article>
<article class="sp-card p-9 reveal" data-delay="120"><p class="sp-eyebrow mb-3">Our role</p><h3 class="sp-h text-3xl mb-3">We connect both sides.</h3><p class="text-[#3f403e]">We find the right creator for the brand, and the right brand deal for the creator, and keep the conversation moving between them.</p></article></section>
<section id="services" class="max-w-[80rem] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">For brands</p><h2 class="sp-h text-4xl md:text-6xl">What brands get.</h2></div><div class="max-w-4xl mx-auto border-b border-[#deded8]">{rows}</div></section>
<section class="bg-white py-24"><div class="max-w-[80rem] mx-auto px-6"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">Built for AI</p><h2 class="sp-h text-4xl md:text-6xl">Creator marketing works when the product needs showing.</h2></div>
<div data-stepper class="max-w-4xl mx-auto"><div class="flex justify-center gap-2 overflow-x-auto border-b border-[#deded8]" role="tablist">{cat_tabs}</div>
<div class="sp-card p-10 mt-8 min-h-[190px] relative">{cat_panels}<div class="absolute right-6 top-6 flex flex-col items-center gap-2"><button data-prev aria-label="Previous" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">←</button><span data-count class="text-xs text-[#686867]"></span><button data-next aria-label="Next" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">→</button></div></div></div></div></section>
{creator_section('light')}
<section id="process" class="max-w-[80rem] mx-auto px-6 py-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">How it works for brands</p><h2 class="sp-h text-4xl md:text-6xl">From message to live video.</h2></div>
<div data-stepper class="max-w-4xl mx-auto"><div class="sp-card p-10 min-h-[190px] relative">{step_panels}<div class="absolute right-6 top-6 flex flex-col items-center gap-2"><button data-prev aria-label="Previous step" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">←</button><span data-count class="text-xs text-[#686867]"></span><button data-next aria-label="Next step" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">→</button></div></div></div></section>
<section class="max-w-[80rem] mx-auto px-6 pb-24"><div class="sp-card p-10 md:p-14 grid md:grid-cols-2 gap-8 items-center reveal" style="border-left:4px solid #0072b8;border-top:1px solid #deded8"><div><p class="sp-eyebrow mb-3">Our approach</p><h3 class="sp-h text-4xl">Brands bring the product. Creators bring the audience.</h3></div><p class="text-[#3f403e]">We don't hand brands a spreadsheet of 200 names. We check each creator's real numbers, send the one to three that fit, and keep it simple for creators too.</p></div></section>
<section id="faq" class="max-w-4xl mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">Common questions</p><h2 class="sp-h text-4xl md:text-5xl">What to know before we work together.</h2></div><div class="border-b border-[#deded8]">{faq}</div></section>
<section class="px-6 pb-24"><div class="max-w-5xl mx-auto text-center reveal"><p class="sp-eyebrow mb-3">Let's work together</p><h2 class="sp-h text-4xl md:text-5xl mb-4">Brands and creators, start here.</h2><p class="text-[#3f403e] mb-8">{CTA_SUB}</p>{forms('light')}</div></section>
</main>
<footer class="bg-[#121212] text-white/75 py-14"><div class="max-w-[80rem] mx-auto px-6 grid md:grid-cols-3 gap-8"><div>{wordmark("text-2xl")}<p class="mt-4 text-sm">Connecting AI and SaaS brands with vetted creators, and creators with brand deals that fit.</p></div>
<div><p class="font-label-sm uppercase mb-3 text-white">Explore</p><div class="space-y-2 text-sm"><a class="block" href="#services">For brands</a><a class="block" href="#for-creators">For creators</a><a class="block" href="#faq">Questions</a></div></div>
<div><p class="font-label-sm uppercase mb-3 text-white">Contact</p><p class="text-sm">{EMAIL}</p><p class="text-sm mt-4"><a href="{ASSET}privacy-policy.html">Privacy</a> · <a href="{ASSET}terms-of-service.html">Terms</a></p></div></div>
<p class="max-w-[80rem] mx-auto px-6 mt-10 text-xs text-white/50">© 2026 Gratovo.</p></footer></div>"""
    page("layout-scalepledge.html", "Layout test: Scale Pledge-style | Gratovo", "Scale Pledge-style",
         "Editorial and light. Hero line draws itself with the four stages, accordion services, tabbed carousel, For Creators section, step carousel, FAQ.",
         "bg-[#f6f9ff]", css, body)


# ================================================================ 4. NSENTIVE
def build_nsentive():
    css = """
.dict-line { opacity:0; animation: fadein .9s ease forwards; }
.n-card { border:1px solid rgba(255,255,255,.55); border-radius:28px; padding:26px 26px 40px; }
.n-row { border-top:1px solid #3a3a3a; display:grid; grid-template-columns: 1fr 1.4fr 60px; gap:24px; padding:34px 0; align-items:start; }
@media (max-width: 768px) { .n-row { grid-template-columns: 1fr; gap: 10px; padding: 24px 0; } .n-row > span { display: none; } }
.loop { height: 340px; overflow: hidden; -webkit-mask-image: linear-gradient(transparent, #000 25%, #000 75%, transparent); mask-image: linear-gradient(transparent, #000 25%, #000 75%, transparent); }
.loop-track { animation: scrollup 14s linear infinite; }
.loop-track span { display:block; text-align:center; font-size:1.7rem; line-height:3.1rem; color:#fff; }
.loop-track span:nth-child(3n+2) { font-family: Georgia, serif; font-style: italic; }
"""
    cards = "".join(
        f'<div class="n-card reveal" data-delay="{i*100}"><div class="mb-14 text-white">{mat(ic, "text-3xl", False)}</div><h3 class="text-2xl font-semibold text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>'
        for i, (ic, t, d) in enumerate(BENEFITS))
    w = [("WHO", "Brands and creators in AI and SaaS: marketing managers and founders who want creators promoting their product, and creators who want brand deals that fit."),
         ("WHAT", "Brands get 1 to 3 vetted AI creators picked for their product. Creators get put forward to brands that fit their audience."),
         ("WHY", "People watching AI tutorials are looking for tools to try. A trusted creator showing a product reaches them at that moment."),
         ("WHERE", "YouTube, LinkedIn, X, and newsletters, wherever the right creator's audience is."),
         ("HOW", "Tell us about your product or your channel. We make the introduction. We take care of contracts, scripts, and posting."),
         ("WHEN", "We reply within 24 hours. Most deals go live within about a month.")]
    rows = "".join(f'<div class="n-row reveal"><h3 class="text-5xl md:text-6xl font-semibold text-[#161616]">{a}</h3><p class="text-[#555] text-lg">{c}</p><span class="text-3xl text-[#161616]">↘</span></div>' for a, c in w)
    who = [("Marketing managers", "Hand off the searching, vetting, and chasing. Keep the final say."),
           ("Founders", "Get your product in front of the right audience without learning creator marketing first."),
           ("Creators", "Get brand deals that fit your channel, without cold outreach or endless email threads.")]
    whorows = "".join(f'<div class="n-row reveal"><h3 class="text-4xl md:text-5xl font-semibold text-[#161616]">{a}</h3><p class="text-[#555] text-lg">{b}</p><span class="text-3xl text-[#161616]">↘</span></div>' for a, b in who)
    flow = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="text-white/40 text-sm mb-3">0{i+1}</p><h3 class="text-4xl font-semibold text-white mb-3">{t}</h3><p class="text-white/70">{d}</p></div>' for i, (t, d) in enumerate(STEPS4))
    loop_items = "".join(f"<span>{x}</span>" for x in ["no cold emails", "no chasing replies", "no guessing who's legit", "no endless threads", "just the right match"] * 2)
    body = f"""
<div class="bg-black text-white">
<header class="max-w-[1280px] mx-auto px-6 h-24 flex items-center justify-between"><a href="#">{wordmark("text-4xl")}</a><a href="#workwithus" class="bg-primary-container text-white rounded-full px-8 py-3 font-medium">Let's Talk</a></header>
<main>
<section class="text-center px-6 pt-16 pb-24">
<h1 class="dict-line text-6xl md:text-8xl font-semibold tracking-tight" style="animation-delay:.2s">match</h1>
<p class="dict-line text-3xl md:text-4xl text-white/35 mt-3" style="animation-delay:.9s">/mætʃ/</p>
<p class="dict-line text-3xl md:text-4xl font-semibold mt-1" style="animation-delay:1.5s">noun</p>
<p class="dict-line text-xl md:text-2xl mt-8 max-w-2xl mx-auto text-white/90" style="animation-delay:2.1s">A creator whose audience fits your product. A brand deal that fits your channel. We find both.</p>
{hero_buttons("bg-white text-black rounded-full px-10 py-4 font-semibold", "border border-white text-white rounded-full px-10 py-4 font-semibold", "dict-line mt-10 flex flex-wrap justify-center gap-4\" style=\"animation-delay:2.7s")}</section>
<section class="max-w-[1280px] mx-auto px-6 pb-28 grid md:grid-cols-3 gap-6">{cards}</section>
<div class="bg-white text-[#161616]"><div class="max-w-[1280px] mx-auto px-6 py-24">
<h2 class="text-5xl md:text-7xl font-semibold tracking-tight mb-14 reveal">The short version.</h2><div class="border-b border-[#3a3a3a]">{rows}</div></div>
<div class="max-w-[1280px] mx-auto px-6 pb-24"><h2 class="text-5xl md:text-7xl font-semibold tracking-tight mb-14 reveal">Who it's for.</h2><div class="border-b border-[#3a3a3a]">{whorows}</div></div></div>
{creator_section('dark')}
<section class="max-w-[1280px] mx-auto px-6 py-28"><h2 class="text-5xl md:text-7xl font-semibold tracking-tight text-center mb-16 reveal">Four steps for brands.</h2><div class="grid md:grid-cols-4 gap-10">{flow}</div></section>
<section class="bg-primary-container px-6 py-24"><div class="max-w-[1200px] mx-auto grid md:grid-cols-[1fr_2.4fr] gap-10 items-center">
<div class="loop hidden md:block"><div class="loop-track">{loop_items}</div></div>
<div class="bg-black rounded-[28px] p-8 md:p-10"><h2 class="text-center text-3xl font-semibold mb-2">Let's Talk</h2><p class="text-center text-white/70 mb-6">{CTA_SUB}</p>{forms('dark')}</div></div></section>
</main>{footer(True)}</div>"""
    page("layout-nsentive.html", "Layout test: Nsentive-style | Gratovo", "Nsentive-style",
         "Black to white to brand blue. Dictionary-style hero that fades in line by line, outlined cards, ruled rows (brands, creators), scrolling word list beside the forms.",
         "bg-black", css, body)


# ================================================================ 5. APOLLO
def build_apollo():
    css = """
@keyframes twinkle { 0%,100% { opacity:.15; } 50% { opacity:.9; } }
@keyframes shoot { 0% { transform: translate(0,0) rotate(-35deg); opacity:0; } 8% { opacity:1; } 30% { transform: translate(-420px,300px) rotate(-35deg); opacity:0; } 100% { opacity:0; } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes counter { to { transform: rotate(-360deg); } }
.shoot { position:absolute; top:8%; right:12%; width:120px; height:2px; background:linear-gradient(90deg, rgba(255,255,255,0), #fff); animation: shoot 7s 2s infinite; }
.glass { background: linear-gradient(160deg, rgba(255,255,255,.08), rgba(255,255,255,.02)); border:1px solid rgba(255,255,255,.12); border-radius:28px; backdrop-filter: blur(10px); }
.grad-text { background: linear-gradient(90deg, #ffd9a8, #ff8fb3, #b88cff); -webkit-background-clip:text; background-clip:text; color:transparent; }
.chip { position:absolute; background: rgba(20,30,70,.9); border:1px solid rgba(255,255,255,.18); border-radius:16px; padding:10px 14px; font-size:13px; color:#fff; animation: floaty 6s ease-in-out infinite; box-shadow:0 10px 30px rgba(0,0,0,.4); }
.orbit { position:relative; width:260px; height:260px; margin:auto; }
.orbit .ring { position:absolute; inset:0; border:1px dashed rgba(255,255,255,.25); border-radius:50%; animation: spin 24s linear infinite; }
.orbit .ring i { position:absolute; width:52px; height:52px; margin:-26px; border-radius:16px; background:#fff; color:#16293d; display:flex; align-items:center; justify-content:center; animation: counter 24s linear infinite; }
.orbit .core { position:absolute; inset:88px; border-radius:24px; background: linear-gradient(135deg,#0a5c9e,#6a54e8); display:flex; align-items:center; justify-content:center; box-shadow:0 0 50px rgba(106,84,232,.6); }
.ghost { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size: clamp(120px, 24vw, 340px); font-weight:800; color: rgba(255,255,255,.05); pointer-events:none; letter-spacing:-.04em; }
.beam { height:1px; background: linear-gradient(90deg, transparent, rgba(150,130,255,.8), transparent); background-size:200% 100%; animation: shimmer 4s linear infinite; }
@keyframes shimmer { to { background-position: -200% 0; } }
"""
    blocks = [("It's that easy.", "Send us a short message. We do the searching, vetting, and chasing."),
              ("Peace of mind.", "Every creator is checked for real views, engagement, and audience location first."),
              ("Your product, shown properly.", "Creators demo your tool in a real workflow, for an audience that wants to try it."),
              ("Nothing goes live unseen.", "You approve the video before it posts.")]
    bl = "".join(f'<div class="glass p-8 reveal" data-delay="{i*100}"><h3 class="font-headline-md text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>' for i, (t, d) in enumerate(blocks))
    stats = "".join(f'<div class="text-center"><p class="text-5xl font-bold text-white">{v}</p><p class="text-white/65 mt-2 max-w-[200px] mx-auto">{l}</p></div>' for v, l in STATS[:3])
    steps = "".join(f'<div class="glass p-7 reveal" data-delay="{i*90}"><span class="grad-text text-4xl font-bold">0{i+1}</span><h3 class="font-headline-md text-white mt-3 mb-2">{t}</h3><p class="text-white/70 text-sm">{d}</p></div>' for i, (t, d) in enumerate(STEPS5))
    plat_icons = ["smart_display", "work", "tag", "mail"]
    orbit_items = "".join(
        f'<i style="left:{50 + 50*math.cos(a)}%;top:{50 + 50*math.sin(a)}%">{mat(ic, "text-2xl", True)}</i>'
        for ic, a in zip(plat_icons, [0, 1.5708, 3.1416, 4.7124]))
    pill = "inline-block border border-white/25 bg-white/10 rounded-full px-7 py-3 text-sm font-semibold"
    body = f"""
<div class="bg-[#050a1f] text-white relative overflow-hidden">
<div id="stars" class="absolute inset-0 pointer-events-none"></div><div class="shoot"></div>
<header class="relative z-20 max-w-[1280px] mx-auto px-6 h-20 flex items-center justify-between"><a href="#">{wordmark("text-3xl")}</a>
<nav class="hidden md:flex gap-1 border border-white/15 rounded-full px-2 py-2 text-sm bg-white/5"><a class="px-4 py-1.5 rounded-full bg-white/10" href="#">Home</a><a class="px-4 py-1.5" href="#brands">For brands</a><a class="px-4 py-1.5" href="#for-creators">For creators</a><a class="px-4 py-1.5" href="#process">How it works</a></nav>
<a href="#workwithus" class="border border-white/25 bg-white/5 rounded-lg px-5 py-2 text-sm">Contact</a></header>
<main class="relative z-10">
<section class="text-center px-6 pt-14 pb-12"><h1 class="font-display-lg text-4xl md:text-7xl max-w-5xl mx-auto leading-[1.05]">{HEAD_PARTS[0]}<span class="grad-text">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-5 text-white/70 text-lg max-w-2xl mx-auto">{SUB}</p></section>
<section class="max-w-[1280px] mx-auto px-6 grid md:grid-cols-2 gap-6 pb-24">
<div id="brands" class="glass p-8 md:p-10 text-center relative overflow-hidden min-h-[470px] reveal"><h2 class="font-display-lg text-4xl mb-3">for brands.</h2><p class="text-white/70 mb-6">1 to 3 vetted AI creators picked for your product.</p>
<a href="#workwithus" class="{pill}">{CTA}</a>
<div class="relative h-56 mt-6"><div class="chip" style="left:6%;top:6%;--r:-6deg">Creator A · 42K avg views</div><div class="chip" style="left:34%;top:38%;--r:4deg;animation-delay:1s">Creator B · 5.1% engagement</div><div class="chip" style="left:12%;top:70%;--r:-3deg;animation-delay:2s">Creator C · 46% US audience</div></div>
<p class="absolute bottom-3 inset-x-0 text-[11px] text-white/45 uppercase tracking-wider">Example format</p></div>
<div class="glass p-8 md:p-10 text-center min-h-[470px] reveal" data-delay="120"><h2 class="font-display-lg text-4xl mb-3">for creators.</h2><p class="text-white/70 mb-6">Brand deals that fit your channel. YouTube, LinkedIn, X, and newsletters.</p>
<a href="#creators" class="{pill}">{CTA_C}</a>
<div class="orbit mt-8"><div class="core">{mat('rocket_launch', 'text-4xl text-white')}</div><div class="ring">{orbit_items}</div></div></div></section>
<section class="max-w-[1280px] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><span class="inline-block border border-white/20 rounded-full px-4 py-1 text-sm mb-4">What brands get ✦</span><h2 class="font-display-lg text-4xl md:text-6xl">A simpler way to work with AI creators.</h2></div><div class="grid md:grid-cols-2 gap-5">{bl}</div></section>
<section class="relative max-w-[1100px] mx-auto px-6 py-24"><div class="ghost" aria-hidden="true">1-3</div><div class="relative"><div class="beam mb-12"></div><div class="grid md:grid-cols-3 gap-10">{stats}</div><div class="beam mt-12"></div></div><p class="relative text-center text-white/60 mt-8">Every creator we recommend passes these checks first.</p></section>
{creator_section('dark')}
<section id="process" class="max-w-[1280px] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><h2 class="font-display-lg text-4xl md:text-6xl">How a deal works with us.</h2></div><div class="grid md:grid-cols-5 gap-4">{steps}</div></section>
<section class="max-w-[1100px] mx-auto px-6 pb-24"><div class="glass p-8 md:p-14 text-center reveal"><h2 class="font-display-lg text-4xl md:text-6xl mb-3">Ready for <span class="grad-text">take-off?</span></h2><p class="text-white/70 mb-10">{CTA_SUB}</p>{forms('dark')}</div></section>
</main>{footer(True)}</div>"""
    page("layout-apollo.html", "Layout test: Apollo-style | Gratovo", "Apollo-style",
         "Dark space theme. Twinkling stars and a shooting star, a glass card for brands and one for creators, floating chips, orbiting platform icons, ghost number behind the stats.",
         "bg-[#050a1f]", css, body)


# ================================================================ 6. RIGHT CLICK
def build_rightclick():
    css = """
.display { font-family: 'Anton', 'Plus Jakarta Sans', sans-serif; text-transform: uppercase; letter-spacing: .01em; line-height: .95; }
.mono { font-family: 'JetBrains Mono', monospace; }
.rc-cap { color:#9ad6f7; }
.rc-btn { border:1px solid #9ad6f7; color:#9ad6f7; border-radius:999px; padding:18px 28px; font-size:1.6rem; display:flex; justify-content:space-between; align-items:center; transition:.25s; }
.rc-btn:hover { background:#9ad6f7; color:#050a14; }
.rc-btn:hover span { color:#050a14 !important; }
.fcard { position:absolute; width:150px; border-radius:18px; padding:14px; color:#fff; box-shadow:0 14px 40px rgba(0,0,0,.5); animation: floaty 7s ease-in-out infinite; }
#scroll-progress-wrap { position:fixed; left:10px; top:90px; bottom:40px; width:3px; z-index:50; }
#scroll-progress { width:3px; background:#9ad6f7; height:0; }
"""
    cards = [("30K+", "avg views", "left:2%;top:6%;--r:-8deg;background:linear-gradient(135deg,#6a54e8,#b8286e)", 0),
             ("3-8%", "engagement", "right:3%;top:2%;--r:6deg;background:linear-gradient(135deg,#0a5c9e,#0072b8)", 1.2),
             ("35%+", "target audience", "left:6%;top:48%;--r:5deg;background:linear-gradient(135deg,#b8286e,#ff7a59)", 2.2),
             ("1-3", "creators, not 200", "right:2%;top:42%;--r:-5deg;background:linear-gradient(135deg,#0072b8,#1fb6a6)", 3.2)]
    fc = "".join(f'<div class="fcard hidden md:block" style="{st};animation-delay:{d}s"><p class="display text-4xl">{v}</p><p class="text-xs uppercase tracking-wider opacity-90">{l}</p></div>' for v, l, st, d in cards)
    pills = [("BRANDS", "Vetted AI creators for your product.", "#workwithus"),
             ("CREATORS", "Brand deals that fit your channel.", "#creators"),
             ("HOW IT WORKS", "Four steps, from message to live video.", "#process")]
    pl = "".join(f'<a href="{h}" class="rc-btn reveal mono" data-delay="{i*100}"><span>{a}</span><span class="text-base text-white/70 max-w-md text-right hidden md:block">{b}</span><span>↗</span></a>' for i, (a, b, h) in enumerate(pills))
    ex = "".join(example_card(i) for i in range(3))
    steps = "".join(f'<div class="reveal border-l border-[#9ad6f7]/50 pl-5" data-delay="{i*100}"><p class="display text-4xl rc-cap">0{i+1}</p><h3 class="mono text-lg font-semibold mt-2">{t}</h3><p class="mono text-white/70 text-sm mt-1">{d}</p></div>' for i, (t, d) in enumerate(STEPS4))
    hb = hero_buttons("bg-[#9ad6f7] text-[#050a14] font-bold rounded-full px-8 py-4", "border border-[#9ad6f7] text-[#9ad6f7] font-bold rounded-full px-8 py-4", "mt-8 flex flex-wrap justify-center gap-4")
    body = f"""
<div class="bg-[#050a14] text-white mono">
<div id="scroll-progress-wrap" aria-hidden="true"><div id="scroll-progress"></div></div>
<header class="relative z-20 flex items-center justify-between px-6 md:px-12 h-24"><span class="mono text-xs rc-cap hidden md:block"><span id="scroll-progress-num">0</span> / 100</span>
<a href="#" class="md:absolute md:left-1/2 md:-translate-x-1/2">{wordmark("text-3xl")}</a><a href="#workwithus" class="ml-auto bg-white/10 rc-cap rounded-full px-5 py-2 text-xs tracking-widest">WORK WITH US</a></header>
<main>
<section class="relative min-h-[88vh] flex flex-col items-center justify-center text-center px-6 overflow-hidden">{fc}
<h1 class="display rc-cap text-[clamp(3rem,10vw,8.5rem)] max-w-6xl relative z-10">{HEADLINE}</h1>
<p class="relative z-10 mt-6 max-w-xl text-white/80">{SUB}</p><div class="relative z-10">{hb}</div></section>
<section class="max-w-5xl mx-auto px-6 pb-24"><div class="border border-[#9ad6f7] rounded-[32px] p-10 md:p-14 text-center reveal"><p class="text-xl leading-relaxed">We're <b class="rc-cap">Gratovo</b>. We connect AI brands with vetted creators, and creators with brand deals that fit. {BODY}</p></div></section>
<section class="max-w-5xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-10 reveal">Who we work with</h2><div class="space-y-5">{pl}</div></section>
<section class="max-w-6xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-3 reveal">What we send brands</h2><p class="text-white/70 mb-10 reveal">Hover a card. Example formats, not real creators.</p><div class="grid sm:grid-cols-3 gap-5 reveal">{ex}</div></section>
{creator_section('dark', head_cls='display')}
<section id="process" class="max-w-6xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-12 reveal">Four steps for brands</h2><div class="grid md:grid-cols-4 gap-8">{steps}</div></section>
<section class="max-w-5xl mx-auto px-6 pb-28 text-center"><h2 class="display rc-cap text-6xl md:text-8xl mb-6 reveal">Ready to get started?</h2><p class="text-white/70 mb-10">{CTA_SUB}</p>{forms('dark')}</section>
</main>{footer(True)}</div>"""
    page("layout-rightclick.html", "Layout test: Right Click-style | Gratovo", "Right Click-style",
         "Bold and edgy. Giant condensed headline with floating stat cards and two buttons, scroll progress counter on the left edge, outlined pill rows (brands, creators), big closing line.",
         "bg-[#050a14]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;display=swap" rel="stylesheet">')


# ================================================================ 7. MINDSHARE
def build_mindshare():
    css = """
.ms { font-family: 'Anton', 'Plus Jakarta Sans', sans-serif; text-transform: uppercase; letter-spacing: -.01em; line-height: .92; }
.pill { border-radius:999px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; font-size:.8rem; padding:18px 30px; display:inline-flex; gap:8px; align-items:center; }
.tag { border:1px solid currentColor; border-radius:999px; padding:6px 14px; font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.side { position:absolute; left:18px; top:40px; writing-mode:vertical-rl; transform:rotate(180deg); font-size:.7rem; letter-spacing:.25em; opacity:.6; text-transform:uppercase; }
@keyframes ticker { to { transform: translateX(-50%); } }
.ticker .marquee-track { animation: ticker 22s linear infinite; }
"""
    plats = "".join(f'<span class="ms text-4xl md:text-5xl text-[#16293d]/80">{p}</span>' for p in PLATFORMS * 3)
    svc = "".join(f'<div class="reveal border-t border-white/20 pt-6" data-delay="{i*90}"><p class="text-primary-fixed-dim text-xs font-bold tracking-widest mb-2">0{i+1}</p><h3 class="ms text-3xl mb-2">{t}</h3><p class="text-white/65">{d}</p></div>' for i, (t, d) in enumerate(SERVICES[:4]))
    props = [("Zero outreach", "We contact the creators. You only hear about the ones worth your time."),
             ("Real numbers", "Views, engagement, and audience location, checked before you see a name."),
             ("You approve it", "Nothing goes live until you've seen the video.")]
    pr = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="font-bold text-lg">{a}</p><p class="text-[#0b1623]/90">{b}</p></div>' for i, (a, b) in enumerate(props))
    cprops = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="font-bold text-lg">{t}</p><p class="text-[#0b1623]/90">{d}</p></div>' for i, (_ic, t, d) in enumerate(CREATOR_BENEFITS))
    body = f"""
<div class="bg-[#16293d] text-white">
<section class="relative bg-primary-container text-[#0b1623] min-h-screen flex flex-col">
<header class="flex items-center justify-between px-6 md:px-10 h-20"><a href="#" class="bg-white rounded-xl px-3 py-1">{wordmark("text-2xl")}</a>
<nav class="flex items-center gap-6 text-xs tracking-widest uppercase font-semibold"><a class="hidden sm:block" href="#brands">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="bg-[#0b1623] text-white rounded-full px-5 py-2">Contact</a></nav></header>
<div class="flex-1 flex flex-col items-center justify-center text-center px-6"><h1 class="ms text-[clamp(4.5rem,17vw,15rem)] text-[#0b1623]">Gratovo</h1>
<p class="mt-6 text-lg font-medium text-[#0b1623]">[ {HEADLINE} ]</p>
<div class="mt-8 flex flex-wrap justify-center gap-3"><a href="#workwithus" class="pill bg-[#0b1623] text-white">{CTA} →</a><a href="#creators" class="pill border border-[#0b1623]/60">{CTA_C}</a></div></div>
<div class="ticker marquee py-6 border-t border-[#0b1623]/20"><div class="marquee-track">{plats}{plats}</div></div></section>
<section id="why" class="px-6 md:px-16 py-24 max-w-[1200px] mx-auto"><p class="text-primary-fixed-dim font-bold tracking-widest text-xs uppercase mb-3 reveal">For brands</p><h2 class="ms text-5xl md:text-7xl mb-14 reveal">Everything between "hello" and "live".</h2><div class="grid md:grid-cols-4 gap-8">{svc}</div></section>
<section class="bg-[#101d2e] px-6 py-20 text-center"><h2 class="ms text-5xl md:text-7xl mb-10 reveal">Where it runs</h2><div class="flex flex-wrap justify-center gap-3 reveal">{"".join(f'<span class="tag text-primary-fixed-dim">{p}</span>' for p in PLATFORMS)}</div></section>
<section class="px-6 md:px-16 py-24 max-w-[1200px] mx-auto grid md:grid-cols-2 gap-14 items-center"><div><p class="text-primary-fixed-dim text-xs font-bold tracking-widest uppercase mb-4 reveal">Our approach</p>
<h2 class="ms text-6xl md:text-8xl reveal">We send 1 to 3 names. <span class="text-accent-container">Not 200.</span></h2><div class="h-1 w-14 bg-accent mt-6"></div></div>
<p class="text-white/65 text-lg reveal">Most creator lists are long spreadsheets that someone still has to check. We check first. Brands get the few creators whose real numbers fit their product, and creators get introduced to brands that fit theirs.</p></section>
<section id="brands" class="relative bg-primary-container text-[#0b1623] px-6 py-24 text-center"><span class="side">For brands</span>
<h2 class="ms text-6xl md:text-9xl max-w-5xl mx-auto reveal">No guessing. Just the right creators.</h2><div class="h-1 w-14 bg-[#0b1623] mx-auto my-6"></div>
<div class="max-w-3xl mx-auto grid md:grid-cols-3 gap-8 text-left my-10">{pr}</div>
<a href="#workwithus" class="pill bg-[#0b1623] text-white">{CTA} →</a></section>
<section id="for-creators" class="relative bg-[#16293d] text-white px-6 py-24 text-center"><span class="side">For creators</span>
<h2 class="ms text-6xl md:text-9xl max-w-5xl mx-auto reveal">Brand deals that <span class="text-accent-container">fit your channel.</span></h2><div class="h-1 w-14 bg-accent mx-auto my-6"></div>
<div class="max-w-3xl mx-auto grid md:grid-cols-2 gap-8 text-left my-10 text-white">{"".join(f'<div class="reveal"><p class="font-bold text-lg">{t}</p><p class="text-white/70">{d}</p></div>' for _ic, t, d in CREATOR_BENEFITS)}</div>
<a href="#creators" class="pill bg-primary-container text-[#0b1623]">{CTA_C} →</a></section>
<section class="px-6 py-24 bg-[#16293d]"><div class="max-w-5xl mx-auto bg-primary-container text-[#0b1623] rounded-[28px] p-8 md:p-14 text-center reveal"><h2 class="ms text-5xl md:text-7xl mb-4">Let's get you matched.</h2><p class="mb-8 opacity-90">{CTA_SUB}</p>{forms('color')}</div></section>
{footer(True)}</div>"""
    page("layout-mindshare.html", "Layout test: MindShare-style | Gratovo", "MindShare-style",
         "Giant type on alternating blue and navy bands. Full-screen wordmark hero with two buttons, platform ticker, For Brands and For Creators bands, rounded closing card.",
         "bg-[#16293d]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;display=swap" rel="stylesheet">')


# ================================================================ 8. SMOOTH
def build_smooth():
    css = """
.serif { font-family: 'Fraunces', Georgia, serif; }
.hero-bg { background: linear-gradient(120deg, #2b1a4d, #0a5c9e, #5b2a86, #16293d); background-size: 300% 300%; animation: drift 16s ease-in-out infinite; }
@keyframes drift { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
.ellipse { fill:none; stroke:#fff; stroke-width:2.5; stroke-dasharray:1; stroke-dashoffset:1; animation: drawline 1.6s 1s ease-out forwards; }
@keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(8px); } }
.phone { width:200px; border:6px solid #2a1745; border-radius:32px; background:#fff; box-shadow:0 20px 40px rgba(42,23,69,.25); overflow:hidden; }
.cloud span { background:#fcfaf6; border-radius:999px; padding:10px 20px; font-weight:700; font-size:.78rem; letter-spacing:.06em; text-transform:uppercase; color:#2a1745; }
"""
    tags = ["AI assistants", "Automation", "Developer tools", "Productivity", "SaaS", "No-code", "AI agents", "Analytics", "Writing tools", "Design tools", "Meeting tools", "Research tools"]
    cloud = "".join(f"<span>{t}</span>" for t in tags)
    phones = "".join(
        f"""<div class="phone reveal" data-delay="{i*120}" style="margin-top:{[0,36,0][i]}px"><div class="bg-gradient-to-br from-[#2a1745] to-[#0a5c9e] h-64 flex flex-col items-center justify-center text-white text-center p-4">{mat('account_circle','text-6xl text-white/80')}<p class="serif text-xl mt-2">{EXAMPLES[i][0]}</p><p class="text-xs text-white/70">{EXAMPLES[i][1]}</p></div>
<div class="p-4 text-[#2a1745]"><p class="text-[10px] uppercase tracking-widest text-[#2a1745]/60 mb-2">Example format</p><div class="flex justify-between text-center"><div><p class="font-bold">{EXAMPLES[i][2]}</p><p class="text-[10px] uppercase">avg views</p></div><div><p class="font-bold">{EXAMPLES[i][3]}</p><p class="text-[10px] uppercase">engage</p></div><div><p class="font-bold">{EXAMPLES[i][4]}</p><p class="text-[10px] uppercase">US</p></div></div></div></div>"""
        for i in range(3))
    steps = "".join(f'<div class="reveal text-center px-4" data-delay="{i*120}"><p class="serif text-6xl text-[#7a4fc0]">{i+1}</p><h3 class="serif text-2xl text-[#2a1745] mt-2 mb-2">{t}</h3><p class="text-[#2a1745]/75">{d}</p></div>' for i, (t, d) in enumerate(STEPS3))
    body = f"""
<div class="bg-[#fcfaf6] text-[#2a1745]">
<section class="hero-bg relative min-h-screen text-white flex flex-col">
<div class="absolute inset-0 bg-[#2a1745]/45"></div>
<header class="relative z-10 flex items-center justify-between px-6 md:px-10 h-24"><a href="#">{wordmark("text-3xl")}</a>
<nav class="flex items-center gap-7 text-sm font-medium"><a class="hidden sm:block" href="#who">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="border border-white rounded-full px-5 py-2">Contact</a></nav></header>
<div class="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 pb-10">
<p class="text-xs font-semibold tracking-[.2em] uppercase mb-6">AI brands and creators, introduced</p>
<h1 class="serif text-5xl md:text-8xl max-w-5xl leading-[1.02]">Connecting AI brands with the <span class="relative inline-block">creators<svg class="absolute -inset-x-3 -inset-y-3 w-[calc(100%+1.5rem)] h-[calc(100%+1.5rem)]" viewBox="0 0 300 100" preserveAspectRatio="none" aria-hidden="true"><ellipse class="ellipse" pathLength="1" cx="150" cy="50" rx="146" ry="44"/></svg></span> their customers trust.</h1>
<p class="mt-8 max-w-xl text-lg text-white/85">{SUB} {BODY}</p>
{hero_buttons("bg-white text-[#2a1745] rounded-full px-9 py-4 font-semibold", "border border-white text-white rounded-full px-9 py-4 font-semibold", "mt-8 flex flex-wrap justify-center gap-3")}
<a href="#who" aria-label="Scroll down" class="mt-10 text-2xl" style="animation: bob 1.8s ease-in-out infinite">↓</a></div></section>
<section id="who" class="bg-[#e6def2] px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">What we send brands.</h2><p class="mb-14 text-[#2a1745]/75 reveal">Each creator, with the numbers that matter. Example formats, not real creators.</p>
<div class="flex flex-wrap justify-center gap-8 mb-20">{phones}</div>
<p class="text-sm tracking-widest uppercase mb-6 reveal">We work with products like:</p><div class="cloud flex flex-wrap justify-center gap-3 max-w-3xl mx-auto reveal">{cloud}</div></section>
<section id="approach" class="px-6 py-24 max-w-5xl mx-auto text-center"><h2 class="serif text-4xl md:text-6xl mb-14 reveal">How it works for <em class="text-[#7a4fc0]">brands</em>.</h2><div class="grid md:grid-cols-3 gap-8">{steps}</div>
<div class="grid sm:grid-cols-3 gap-4 mt-16">{"".join(f'<div class="reveal bg-white rounded-2xl p-6 text-left"><p class="font-bold mb-1">{t}</p><p class="text-sm text-[#2a1745]/70">{d}</p></div>' for _i, t, d in BENEFITS)}</div></section>
<div class="bg-[#e6def2] text-[#2a1745]">{creator_section('light')}</div>
<section class="bg-[#2a1745] text-white px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">Let's get you matched.</h2><p class="text-white/75 mb-10 reveal">{CTA_SUB}</p>{forms('dark')}</section>
{footer(True)}</div>"""
    page("layout-smooth.html", "Layout test: Smooth-style | Gratovo", "Smooth-style",
         "Soft and editorial. Full-screen tinted hero with a hand-drawn ellipse and two buttons, phone-shaped example cards, category pill cloud, For Creators section, serif headings.",
         "bg-[#fcfaf6]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&amp;display=swap" rel="stylesheet">')


# ================================================================ 9. ADHESIVE
def build_adhesive():
    css = """
.hl { color:#0072b8; }
.step-tab { padding:12px 16px; border-bottom:3px solid transparent; font-weight:600; color:#686867; white-space:nowrap; }
.step-tab.is-active { color:#121212; border-color:#0072b8; }
.nav-blur { backdrop-filter: blur(10px); background: rgba(246,249,255,.85); }
"""
    rows = "".join(
        f'<details class="row"><summary><span class="sp-eyebrow">0{i+1}</span><span class="font-headline-md text-2xl font-bold">{t}</span><span class="hidden md:block text-secondary text-sm">Included</span><span class="tog">+</span></summary><p>{d}</p></details>'
        for i, (t, d) in enumerate(SERVICES))
    cats = [("AI assistants", "Reach people already learning to get more from AI chat and writing tools."),
            ("Automation", "Show workflow builders how your tool saves them hours, on screen."),
            ("Developer tools", "Put your product in front of developers who watch tutorials before they buy."),
            ("Productivity", "Get walked through in real workflows by creators who use tools like yours daily.")]
    cat_tabs = "".join(f'<button class="step-tab" role="tab">{c}</button>' for c, _ in cats)
    cat_panels = "".join(f'<div class="step-panel" role="tabpanel"><h3 class="sp-h text-3xl mb-3">{c}</h3><p class="text-[#3f403e] max-w-xl">{d}</p></div>' for c, d in cats)
    step_panels = "".join(
        f'<div class="step-panel"><p class="sp-eyebrow mb-2">Step {i+1} of 5</p><h3 class="sp-h text-3xl mb-3">{t}</h3><p class="text-[#3f403e] max-w-xl">{d}</p></div>' for i, (t, d) in enumerate(STEPS5))
    faq = "".join(f'<details class="row"><summary style="grid-template-columns:1fr 24px"><span class="font-headline-md text-xl font-bold">{q}</span><span class="tog">+</span></summary><p style="padding-left:0">{a}</p></details>' for q, a in FAQ)
    body = f"""
<div class="bg-[#f6f9ff] text-[#121212]">
<header class="nav-blur sticky top-0 z-50 border-b border-[#deded8]"><div class="max-w-[80rem] mx-auto px-6 h-[72px] flex items-center justify-between">
<a href="#">{wordmark("text-2xl")}</a>
<nav class="hidden md:flex gap-8 text-sm font-medium"><a href="#services">For brands</a><a href="#for-creators">For creators</a><a href="#process">How it works</a><a href="#faq">Questions</a></nav>
<a href="#workwithus" class="bg-primary-container text-white rounded-2xl px-5 py-3 text-sm font-semibold">{CTA}</a></div></header>
<main>
<section class="relative overflow-hidden"><div class="absolute inset-x-0 bottom-0 h-[55%] pointer-events-none">
<svg viewBox="0 0 760 430" preserveAspectRatio="none" class="w-full h-full" aria-hidden="true"><defs><linearGradient id="ga" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#0072b8" stop-opacity=".25"/><stop offset="1" stop-color="#0072b8" stop-opacity=".02"/></linearGradient></defs>
<path class="growth-area" d="M0 400 L90 385 L170 392 L250 360 L330 366 L410 330 L490 335 L560 230 L640 215 L700 110 L760 40 L760 430 L0 430 Z"/>
<path class="growth-path" pathLength="1" d="M0 400 L90 385 L170 392 L250 360 L330 366 L410 330 L490 335 L560 230 L640 215 L700 110 L760 40"/></svg>
<span class="stage" style="left:24%;bottom:22%;animation-delay:1.2s">Request</span><span class="stage" style="left:42%;bottom:33%;animation-delay:1.8s">Match</span>
<span class="stage" style="left:62%;bottom:50%;animation-delay:2.4s">Agree</span><span class="stage" style="left:82%;bottom:72%;animation-delay:3s">Launch</span></div>
<div class="relative max-w-[80rem] mx-auto px-6 pt-20 pb-72 md:pb-80">
<p class="sp-eyebrow mb-6">AI influencer marketing</p>
<h1 class="sp-h text-5xl md:text-8xl max-w-5xl">{HEAD_PARTS[0]}<span class="text-primary-container">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-6 text-lg text-[#3f403e] max-w-2xl">{SUB} {BODY}</p>
{hero_buttons("bg-primary-container text-white rounded-2xl px-6 py-4 font-semibold", "bg-[#121212] text-white rounded-2xl px-6 py-4 font-semibold", "mt-8 flex flex-wrap gap-3")}</div></section>
<section class="max-w-[80rem] mx-auto px-6 pb-24 grid md:grid-cols-2 gap-5">
<article class="sp-card p-9 reveal"><p class="sp-eyebrow mb-3">The buying journey</p><h3 class="sp-h text-3xl mb-3">People watch before they buy.</h3><p class="text-[#3f403e]">Before trying a new AI tool, people watch tutorials, compare options, and listen to creators they already trust.</p></article>
<article class="sp-card p-9 reveal" data-delay="120"><p class="sp-eyebrow mb-3">Our role</p><h3 class="sp-h text-3xl mb-3">We connect both sides.</h3><p class="text-[#3f403e]">We find the right creator for the brand, and the right brand deal for the creator, and keep the conversation moving between them.</p></article></section>
<section id="services" class="max-w-[80rem] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">For brands</p><h2 class="sp-h text-4xl md:text-6xl">What brands get.</h2></div><div class="max-w-4xl mx-auto border-b border-[#deded8]">{rows}</div></section>
<section class="bg-white py-24"><div class="max-w-[80rem] mx-auto px-6"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">Built for AI</p><h2 class="sp-h text-4xl md:text-6xl">Creator marketing works when the product needs showing.</h2></div>
<div data-stepper class="max-w-4xl mx-auto"><div class="flex justify-center gap-2 overflow-x-auto border-b border-[#deded8]" role="tablist">{cat_tabs}</div>
<div class="sp-card p-10 mt-8 min-h-[190px] relative">{cat_panels}<div class="absolute right-6 top-6 flex flex-col items-center gap-2"><button data-prev aria-label="Previous" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">←</button><span data-count class="text-xs text-[#686867]"></span><button data-next aria-label="Next" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">→</button></div></div></div></div></section>
{creator_section('light')}
<section id="process" class="max-w-[80rem] mx-auto px-6 py-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">How it works for brands</p><h2 class="sp-h text-4xl md:text-6xl">From message to live video.</h2></div>
<div data-stepper class="max-w-4xl mx-auto"><div class="sp-card p-10 min-h-[190px] relative">{step_panels}<div class="absolute right-6 top-6 flex flex-col items-center gap-2"><button data-prev aria-label="Previous step" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">←</button><span data-count class="text-xs text-[#686867]"></span><button data-next aria-label="Next step" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">→</button></div></div></div></section>
<section class="max-w-[80rem] mx-auto px-6 pb-24"><div class="sp-card p-10 md:p-14 grid md:grid-cols-2 gap-8 items-center reveal" style="border-left:4px solid #0072b8;border-top:1px solid #deded8"><div><p class="sp-eyebrow mb-3">Our approach</p><h3 class="sp-h text-4xl">Brands bring the product. Creators bring the audience.</h3></div><p class="text-[#3f403e]">We don't hand brands a spreadsheet of 200 names. We check each creator's real numbers, send the one to three that fit, and keep it simple for creators too.</p></div></section>
<section id="faq" class="max-w-4xl mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">Common questions</p><h2 class="sp-h text-4xl md:text-5xl">What to know before we work together.</h2></div><div class="border-b border-[#deded8]">{faq}</div></section>
<section class="px-6 pb-24"><div class="max-w-5xl mx-auto text-center reveal"><p class="sp-eyebrow mb-3">Let's work together</p><h2 class="sp-h text-4xl md:text-5xl mb-4">Brands and creators, start here.</h2><p class="text-[#3f403e] mb-8">{CTA_SUB}</p>{forms('light')}</div></section>
</main>
<footer class="bg-[#121212] text-white/75 py-14"><div class="max-w-[80rem] mx-auto px-6 grid md:grid-cols-3 gap-8"><div>{wordmark("text-2xl")}<p class="mt-4 text-sm">Connecting AI and SaaS brands with vetted creators, and creators with brand deals that fit.</p></div>
<div><p class="font-label-sm uppercase mb-3 text-white">Explore</p><div class="space-y-2 text-sm"><a class="block" href="#services">For brands</a><a class="block" href="#for-creators">For creators</a><a class="block" href="#faq">Questions</a></div></div>
<div><p class="font-label-sm uppercase mb-3 text-white">Contact</p><p class="text-sm">{EMAIL}</p><p class="text-sm mt-4"><a href="{ASSET}privacy-policy.html">Privacy</a> · <a href="{ASSET}terms-of-service.html">Terms</a></p></div></div>
<p class="max-w-[80rem] mx-auto px-6 mt-10 text-xs text-white/50">© 2026 Gratovo.</p></footer></div>"""
    page("layout-scalepledge.html", "Layout test: Scale Pledge-style | Gratovo", "Scale Pledge-style",
         "Editorial and light. Hero line draws itself with the four stages, accordion services, tabbed carousel, For Creators section, step carousel, FAQ.",
         "bg-[#f6f9ff]", css, body)


# ================================================================ 4. NSENTIVE
def build_nsentive():
    css = """
.dict-line { opacity:0; animation: fadein .9s ease forwards; }
.n-card { border:1px solid rgba(255,255,255,.55); border-radius:28px; padding:26px 26px 40px; }
.n-row { border-top:1px solid #3a3a3a; display:grid; grid-template-columns: 1fr 1.4fr 60px; gap:24px; padding:34px 0; align-items:start; }
@media (max-width: 768px) { .n-row { grid-template-columns: 1fr; gap: 10px; padding: 24px 0; } .n-row > span { display: none; } }
.loop { height: 340px; overflow: hidden; -webkit-mask-image: linear-gradient(transparent, #000 25%, #000 75%, transparent); mask-image: linear-gradient(transparent, #000 25%, #000 75%, transparent); }
.loop-track { animation: scrollup 14s linear infinite; }
.loop-track span { display:block; text-align:center; font-size:1.7rem; line-height:3.1rem; color:#fff; }
.loop-track span:nth-child(3n+2) { font-family: Georgia, serif; font-style: italic; }
"""
    cards = "".join(
        f'<div class="n-card reveal" data-delay="{i*100}"><div class="mb-14 text-white">{mat(ic, "text-3xl", False)}</div><h3 class="text-2xl font-semibold text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>'
        for i, (ic, t, d) in enumerate(BENEFITS))
    w = [("WHO", "Brands and creators in AI and SaaS: marketing managers and founders who want creators promoting their product, and creators who want brand deals that fit."),
         ("WHAT", "Brands get 1 to 3 vetted AI creators picked for their product. Creators get put forward to brands that fit their audience."),
         ("WHY", "People watching AI tutorials are looking for tools to try. A trusted creator showing a product reaches them at that moment."),
         ("WHERE", "YouTube, LinkedIn, X, and newsletters, wherever the right creator's audience is."),
         ("HOW", "Tell us about your product or your channel. We make the introduction. We take care of contracts, scripts, and posting."),
         ("WHEN", "We reply within 24 hours. Most deals go live within about a month.")]
    rows = "".join(f'<div class="n-row reveal"><h3 class="text-5xl md:text-6xl font-semibold text-[#161616]">{a}</h3><p class="text-[#555] text-lg">{c}</p><span class="text-3xl text-[#161616]">↘</span></div>' for a, c in w)
    who = [("Marketing managers", "Hand off the searching, vetting, and chasing. Keep the final say."),
           ("Founders", "Get your product in front of the right audience without learning creator marketing first."),
           ("Creators", "Get brand deals that fit your channel, without cold outreach or endless email threads.")]
    whorows = "".join(f'<div class="n-row reveal"><h3 class="text-4xl md:text-5xl font-semibold text-[#161616]">{a}</h3><p class="text-[#555] text-lg">{b}</p><span class="text-3xl text-[#161616]">↘</span></div>' for a, b in who)
    flow = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="text-white/40 text-sm mb-3">0{i+1}</p><h3 class="text-4xl font-semibold text-white mb-3">{t}</h3><p class="text-white/70">{d}</p></div>' for i, (t, d) in enumerate(STEPS4))
    loop_items = "".join(f"<span>{x}</span>" for x in ["no cold emails", "no chasing replies", "no guessing who's legit", "no endless threads", "just the right match"] * 2)
    body = f"""
<div class="bg-black text-white">
<header class="max-w-[1280px] mx-auto px-6 h-24 flex items-center justify-between"><a href="#">{wordmark("text-4xl")}</a><a href="#workwithus" class="bg-primary-container text-white rounded-full px-8 py-3 font-medium">Let's Talk</a></header>
<main>
<section class="text-center px-6 pt-16 pb-24">
<h1 class="dict-line text-6xl md:text-8xl font-semibold tracking-tight" style="animation-delay:.2s">match</h1>
<p class="dict-line text-3xl md:text-4xl text-white/35 mt-3" style="animation-delay:.9s">/mætʃ/</p>
<p class="dict-line text-3xl md:text-4xl font-semibold mt-1" style="animation-delay:1.5s">noun</p>
<p class="dict-line text-xl md:text-2xl mt-8 max-w-2xl mx-auto text-white/90" style="animation-delay:2.1s">A creator whose audience fits your product. A brand deal that fits your channel. We find both.</p>
{hero_buttons("bg-white text-black rounded-full px-10 py-4 font-semibold", "border border-white text-white rounded-full px-10 py-4 font-semibold", "dict-line mt-10 flex flex-wrap justify-center gap-4\" style=\"animation-delay:2.7s")}</section>
<section class="max-w-[1280px] mx-auto px-6 pb-28 grid md:grid-cols-3 gap-6">{cards}</section>
<div class="bg-white text-[#161616]"><div class="max-w-[1280px] mx-auto px-6 py-24">
<h2 class="text-5xl md:text-7xl font-semibold tracking-tight mb-14 reveal">The short version.</h2><div class="border-b border-[#3a3a3a]">{rows}</div></div>
<div class="max-w-[1280px] mx-auto px-6 pb-24"><h2 class="text-5xl md:text-7xl font-semibold tracking-tight mb-14 reveal">Who it's for.</h2><div class="border-b border-[#3a3a3a]">{whorows}</div></div></div>
{creator_section('dark')}
<section class="max-w-[1280px] mx-auto px-6 py-28"><h2 class="text-5xl md:text-7xl font-semibold tracking-tight text-center mb-16 reveal">Four steps for brands.</h2><div class="grid md:grid-cols-4 gap-10">{flow}</div></section>
<section class="bg-primary-container px-6 py-24"><div class="max-w-[1200px] mx-auto grid md:grid-cols-[1fr_2.4fr] gap-10 items-center">
<div class="loop hidden md:block"><div class="loop-track">{loop_items}</div></div>
<div class="bg-black rounded-[28px] p-8 md:p-10"><h2 class="text-center text-3xl font-semibold mb-2">Let's Talk</h2><p class="text-center text-white/70 mb-6">{CTA_SUB}</p>{forms('dark')}</div></div></section>
</main>{footer(True)}</div>"""
    page("layout-nsentive.html", "Layout test: Nsentive-style | Gratovo", "Nsentive-style",
         "Black to white to brand blue. Dictionary-style hero that fades in line by line, outlined cards, ruled rows (brands, creators), scrolling word list beside the forms.",
         "bg-black", css, body)


# ================================================================ 5. APOLLO
def build_apollo():
    css = """
@keyframes twinkle { 0%,100% { opacity:.15; } 50% { opacity:.9; } }
@keyframes shoot { 0% { transform: translate(0,0) rotate(-35deg); opacity:0; } 8% { opacity:1; } 30% { transform: translate(-420px,300px) rotate(-35deg); opacity:0; } 100% { opacity:0; } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes counter { to { transform: rotate(-360deg); } }
.shoot { position:absolute; top:8%; right:12%; width:120px; height:2px; background:linear-gradient(90deg, rgba(255,255,255,0), #fff); animation: shoot 7s 2s infinite; }
.glass { background: linear-gradient(160deg, rgba(255,255,255,.08), rgba(255,255,255,.02)); border:1px solid rgba(255,255,255,.12); border-radius:28px; backdrop-filter: blur(10px); }
.grad-text { background: linear-gradient(90deg, #ffd9a8, #ff8fb3, #b88cff); -webkit-background-clip:text; background-clip:text; color:transparent; }
.chip { position:absolute; background: rgba(20,30,70,.9); border:1px solid rgba(255,255,255,.18); border-radius:16px; padding:10px 14px; font-size:13px; color:#fff; animation: floaty 6s ease-in-out infinite; box-shadow:0 10px 30px rgba(0,0,0,.4); }
.orbit { position:relative; width:260px; height:260px; margin:auto; }
.orbit .ring { position:absolute; inset:0; border:1px dashed rgba(255,255,255,.25); border-radius:50%; animation: spin 24s linear infinite; }
.orbit .ring i { position:absolute; width:52px; height:52px; margin:-26px; border-radius:16px; background:#fff; color:#16293d; display:flex; align-items:center; justify-content:center; animation: counter 24s linear infinite; }
.orbit .core { position:absolute; inset:88px; border-radius:24px; background: linear-gradient(135deg,#0a5c9e,#6a54e8); display:flex; align-items:center; justify-content:center; box-shadow:0 0 50px rgba(106,84,232,.6); }
.ghost { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size: clamp(120px, 24vw, 340px); font-weight:800; color: rgba(255,255,255,.05); pointer-events:none; letter-spacing:-.04em; }
.beam { height:1px; background: linear-gradient(90deg, transparent, rgba(150,130,255,.8), transparent); background-size:200% 100%; animation: shimmer 4s linear infinite; }
@keyframes shimmer { to { background-position: -200% 0; } }
"""
    blocks = [("It's that easy.", "Send us a short message. We do the searching, vetting, and chasing."),
              ("Peace of mind.", "Every creator is checked for real views, engagement, and audience location first."),
              ("Your product, shown properly.", "Creators demo your tool in a real workflow, for an audience that wants to try it."),
              ("Nothing goes live unseen.", "You approve the video before it posts.")]
    bl = "".join(f'<div class="glass p-8 reveal" data-delay="{i*100}"><h3 class="font-headline-md text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>' for i, (t, d) in enumerate(blocks))
    stats = "".join(f'<div class="text-center"><p class="text-5xl font-bold text-white">{v}</p><p class="text-white/65 mt-2 max-w-[200px] mx-auto">{l}</p></div>' for v, l in STATS[:3])
    steps = "".join(f'<div class="glass p-7 reveal" data-delay="{i*90}"><span class="grad-text text-4xl font-bold">0{i+1}</span><h3 class="font-headline-md text-white mt-3 mb-2">{t}</h3><p class="text-white/70 text-sm">{d}</p></div>' for i, (t, d) in enumerate(STEPS5))
    plat_icons = ["smart_display", "work", "tag", "mail"]
    orbit_items = "".join(
        f'<i style="left:{50 + 50*math.cos(a)}%;top:{50 + 50*math.sin(a)}%">{mat(ic, "text-2xl", True)}</i>'
        for ic, a in zip(plat_icons, [0, 1.5708, 3.1416, 4.7124]))
    pill = "inline-block border border-white/25 bg-white/10 rounded-full px-7 py-3 text-sm font-semibold"
    body = f"""
<div class="bg-[#050a1f] text-white relative overflow-hidden">
<div id="stars" class="absolute inset-0 pointer-events-none"></div><div class="shoot"></div>
<header class="relative z-20 max-w-[1280px] mx-auto px-6 h-20 flex items-center justify-between"><a href="#">{wordmark("text-3xl")}</a>
<nav class="hidden md:flex gap-1 border border-white/15 rounded-full px-2 py-2 text-sm bg-white/5"><a class="px-4 py-1.5 rounded-full bg-white/10" href="#">Home</a><a class="px-4 py-1.5" href="#brands">For brands</a><a class="px-4 py-1.5" href="#for-creators">For creators</a><a class="px-4 py-1.5" href="#process">How it works</a></nav>
<a href="#workwithus" class="border border-white/25 bg-white/5 rounded-lg px-5 py-2 text-sm">Contact</a></header>
<main class="relative z-10">
<section class="text-center px-6 pt-14 pb-12"><h1 class="font-display-lg text-4xl md:text-7xl max-w-5xl mx-auto leading-[1.05]">{HEAD_PARTS[0]}<span class="grad-text">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-5 text-white/70 text-lg max-w-2xl mx-auto">{SUB}</p></section>
<section class="max-w-[1280px] mx-auto px-6 grid md:grid-cols-2 gap-6 pb-24">
<div id="brands" class="glass p-8 md:p-10 text-center relative overflow-hidden min-h-[470px] reveal"><h2 class="font-display-lg text-4xl mb-3">for brands.</h2><p class="text-white/70 mb-6">1 to 3 vetted AI creators picked for your product.</p>
<a href="#workwithus" class="{pill}">{CTA}</a>
<div class="relative h-56 mt-6"><div class="chip" style="left:6%;top:6%;--r:-6deg">Creator A · 42K avg views</div><div class="chip" style="left:34%;top:38%;--r:4deg;animation-delay:1s">Creator B · 5.1% engagement</div><div class="chip" style="left:12%;top:70%;--r:-3deg;animation-delay:2s">Creator C · 46% US audience</div></div>
<p class="absolute bottom-3 inset-x-0 text-[11px] text-white/45 uppercase tracking-wider">Example format</p></div>
<div class="glass p-8 md:p-10 text-center min-h-[470px] reveal" data-delay="120"><h2 class="font-display-lg text-4xl mb-3">for creators.</h2><p class="text-white/70 mb-6">Brand deals that fit your channel. YouTube, LinkedIn, X, and newsletters.</p>
<a href="#creators" class="{pill}">{CTA_C}</a>
<div class="orbit mt-8"><div class="core">{mat('rocket_launch', 'text-4xl text-white')}</div><div class="ring">{orbit_items}</div></div></div></section>
<section class="max-w-[1280px] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><span class="inline-block border border-white/20 rounded-full px-4 py-1 text-sm mb-4">What brands get ✦</span><h2 class="font-display-lg text-4xl md:text-6xl">A simpler way to work with AI creators.</h2></div><div class="grid md:grid-cols-2 gap-5">{bl}</div></section>
<section class="relative max-w-[1100px] mx-auto px-6 py-24"><div class="ghost" aria-hidden="true">1-3</div><div class="relative"><div class="beam mb-12"></div><div class="grid md:grid-cols-3 gap-10">{stats}</div><div class="beam mt-12"></div></div><p class="relative text-center text-white/60 mt-8">Every creator we recommend passes these checks first.</p></section>
{creator_section('dark')}
<section id="process" class="max-w-[1280px] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><h2 class="font-display-lg text-4xl md:text-6xl">How a deal works with us.</h2></div><div class="grid md:grid-cols-5 gap-4">{steps}</div></section>
<section class="max-w-[1100px] mx-auto px-6 pb-24"><div class="glass p-8 md:p-14 text-center reveal"><h2 class="font-display-lg text-4xl md:text-6xl mb-3">Ready for <span class="grad-text">take-off?</span></h2><p class="text-white/70 mb-10">{CTA_SUB}</p>{forms('dark')}</div></section>
</main>{footer(True)}</div>"""
    page("layout-apollo.html", "Layout test: Apollo-style | Gratovo", "Apollo-style",
         "Dark space theme. Twinkling stars and a shooting star, a glass card for brands and one for creators, floating chips, orbiting platform icons, ghost number behind the stats.",
         "bg-[#050a1f]", css, body)


# ================================================================ 6. RIGHT CLICK
def build_rightclick():
    css = """
.display { font-family: 'Anton', 'Plus Jakarta Sans', sans-serif; text-transform: uppercase; letter-spacing: .01em; line-height: .95; }
.mono { font-family: 'JetBrains Mono', monospace; }
.rc-cap { color:#9ad6f7; }
.rc-btn { border:1px solid #9ad6f7; color:#9ad6f7; border-radius:999px; padding:18px 28px; font-size:1.6rem; display:flex; justify-content:space-between; align-items:center; transition:.25s; }
.rc-btn:hover { background:#9ad6f7; color:#050a14; }
.rc-btn:hover span { color:#050a14 !important; }
.fcard { position:absolute; width:150px; border-radius:18px; padding:14px; color:#fff; box-shadow:0 14px 40px rgba(0,0,0,.5); animation: floaty 7s ease-in-out infinite; }
#scroll-progress-wrap { position:fixed; left:10px; top:90px; bottom:40px; width:3px; z-index:50; }
#scroll-progress { width:3px; background:#9ad6f7; height:0; }
"""
    cards = [("30K+", "avg views", "left:2%;top:6%;--r:-8deg;background:linear-gradient(135deg,#6a54e8,#b8286e)", 0),
             ("3-8%", "engagement", "right:3%;top:2%;--r:6deg;background:linear-gradient(135deg,#0a5c9e,#0072b8)", 1.2),
             ("35%+", "target audience", "left:6%;top:48%;--r:5deg;background:linear-gradient(135deg,#b8286e,#ff7a59)", 2.2),
             ("1-3", "creators, not 200", "right:2%;top:42%;--r:-5deg;background:linear-gradient(135deg,#0072b8,#1fb6a6)", 3.2)]
    fc = "".join(f'<div class="fcard hidden md:block" style="{st};animation-delay:{d}s"><p class="display text-4xl">{v}</p><p class="text-xs uppercase tracking-wider opacity-90">{l}</p></div>' for v, l, st, d in cards)
    pills = [("BRANDS", "Vetted AI creators for your product.", "#workwithus"),
             ("CREATORS", "Brand deals that fit your channel.", "#creators"),
             ("HOW IT WORKS", "Four steps, from message to live video.", "#process")]
    pl = "".join(f'<a href="{h}" class="rc-btn reveal mono" data-delay="{i*100}"><span>{a}</span><span class="text-base text-white/70 max-w-md text-right hidden md:block">{b}</span><span>↗</span></a>' for i, (a, b, h) in enumerate(pills))
    ex = "".join(example_card(i) for i in range(3))
    steps = "".join(f'<div class="reveal border-l border-[#9ad6f7]/50 pl-5" data-delay="{i*100}"><p class="display text-4xl rc-cap">0{i+1}</p><h3 class="mono text-lg font-semibold mt-2">{t}</h3><p class="mono text-white/70 text-sm mt-1">{d}</p></div>' for i, (t, d) in enumerate(STEPS4))
    hb = hero_buttons("bg-[#9ad6f7] text-[#050a14] font-bold rounded-full px-8 py-4", "border border-[#9ad6f7] text-[#9ad6f7] font-bold rounded-full px-8 py-4", "mt-8 flex flex-wrap justify-center gap-4")
    body = f"""
<div class="bg-[#050a14] text-white mono">
<div id="scroll-progress-wrap" aria-hidden="true"><div id="scroll-progress"></div></div>
<header class="relative z-20 flex items-center justify-between px-6 md:px-12 h-24"><span class="mono text-xs rc-cap hidden md:block"><span id="scroll-progress-num">0</span> / 100</span>
<a href="#" class="md:absolute md:left-1/2 md:-translate-x-1/2">{wordmark("text-3xl")}</a><a href="#workwithus" class="ml-auto bg-white/10 rc-cap rounded-full px-5 py-2 text-xs tracking-widest">WORK WITH US</a></header>
<main>
<section class="relative min-h-[88vh] flex flex-col items-center justify-center text-center px-6 overflow-hidden">{fc}
<h1 class="display rc-cap text-[clamp(3rem,10vw,8.5rem)] max-w-6xl relative z-10">{HEADLINE}</h1>
<p class="relative z-10 mt-6 max-w-xl text-white/80">{SUB}</p><div class="relative z-10">{hb}</div></section>
<section class="max-w-5xl mx-auto px-6 pb-24"><div class="border border-[#9ad6f7] rounded-[32px] p-10 md:p-14 text-center reveal"><p class="text-xl leading-relaxed">We're <b class="rc-cap">Gratovo</b>. We connect AI brands with vetted creators, and creators with brand deals that fit. {BODY}</p></div></section>
<section class="max-w-5xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-10 reveal">Who we work with</h2><div class="space-y-5">{pl}</div></section>
<section class="max-w-6xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-3 reveal">What we send brands</h2><p class="text-white/70 mb-10 reveal">Hover a card. Example formats, not real creators.</p><div class="grid sm:grid-cols-3 gap-5 reveal">{ex}</div></section>
{creator_section('dark', head_cls='display')}
<section id="process" class="max-w-6xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-12 reveal">Four steps for brands</h2><div class="grid md:grid-cols-4 gap-8">{steps}</div></section>
<section class="max-w-5xl mx-auto px-6 pb-28 text-center"><h2 class="display rc-cap text-6xl md:text-8xl mb-6 reveal">Ready to get started?</h2><p class="text-white/70 mb-10">{CTA_SUB}</p>{forms('dark')}</section>
</main>{footer(True)}</div>"""
    page("layout-rightclick.html", "Layout test: Right Click-style | Gratovo", "Right Click-style",
         "Bold and edgy. Giant condensed headline with floating stat cards and two buttons, scroll progress counter on the left edge, outlined pill rows (brands, creators), big closing line.",
         "bg-[#050a14]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;display=swap" rel="stylesheet">')


# ================================================================ 7. MINDSHARE
def build_mindshare():
    css = """
.ms { font-family: 'Anton', 'Plus Jakarta Sans', sans-serif; text-transform: uppercase; letter-spacing: -.01em; line-height: .92; }
.pill { border-radius:999px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; font-size:.8rem; padding:18px 30px; display:inline-flex; gap:8px; align-items:center; }
.tag { border:1px solid currentColor; border-radius:999px; padding:6px 14px; font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.side { position:absolute; left:18px; top:40px; writing-mode:vertical-rl; transform:rotate(180deg); font-size:.7rem; letter-spacing:.25em; opacity:.6; text-transform:uppercase; }
@keyframes ticker { to { transform: translateX(-50%); } }
.ticker .marquee-track { animation: ticker 22s linear infinite; }
"""
    plats = "".join(f'<span class="ms text-4xl md:text-5xl text-[#16293d]/80">{p}</span>' for p in PLATFORMS * 3)
    svc = "".join(f'<div class="reveal border-t border-white/20 pt-6" data-delay="{i*90}"><p class="text-primary-fixed-dim text-xs font-bold tracking-widest mb-2">0{i+1}</p><h3 class="ms text-3xl mb-2">{t}</h3><p class="text-white/65">{d}</p></div>' for i, (t, d) in enumerate(SERVICES[:4]))
    props = [("Zero outreach", "We contact the creators. You only hear about the ones worth your time."),
             ("Real numbers", "Views, engagement, and audience location, checked before you see a name."),
             ("You approve it", "Nothing goes live until you've seen the video.")]
    pr = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="font-bold text-lg">{a}</p><p class="text-[#0b1623]/90">{b}</p></div>' for i, (a, b) in enumerate(props))
    cprops = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="font-bold text-lg">{t}</p><p class="text-[#0b1623]/90">{d}</p></div>' for i, (_ic, t, d) in enumerate(CREATOR_BENEFITS))
    body = f"""
<div class="bg-[#16293d] text-white">
<section class="relative bg-primary-container text-[#0b1623] min-h-screen flex flex-col">
<header class="flex items-center justify-between px-6 md:px-10 h-20"><a href="#" class="bg-white rounded-xl px-3 py-1">{wordmark("text-2xl")}</a>
<nav class="flex items-center gap-6 text-xs tracking-widest uppercase font-semibold"><a class="hidden sm:block" href="#brands">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="bg-[#0b1623] text-white rounded-full px-5 py-2">Contact</a></nav></header>
<div class="flex-1 flex flex-col items-center justify-center text-center px-6"><h1 class="ms text-[clamp(4.5rem,17vw,15rem)] text-[#0b1623]">Gratovo</h1>
<p class="mt-6 text-lg font-medium text-[#0b1623]">[ {HEADLINE} ]</p>
<div class="mt-8 flex flex-wrap justify-center gap-3"><a href="#workwithus" class="pill bg-[#0b1623] text-white">{CTA} →</a><a href="#creators" class="pill border border-[#0b1623]/60">{CTA_C}</a></div></div>
<div class="ticker marquee py-6 border-t border-[#0b1623]/20"><div class="marquee-track">{plats}{plats}</div></div></section>
<section id="why" class="px-6 md:px-16 py-24 max-w-[1200px] mx-auto"><p class="text-primary-fixed-dim font-bold tracking-widest text-xs uppercase mb-3 reveal">For brands</p><h2 class="ms text-5xl md:text-7xl mb-14 reveal">Everything between "hello" and "live".</h2><div class="grid md:grid-cols-4 gap-8">{svc}</div></section>
<section class="bg-[#101d2e] px-6 py-20 text-center"><h2 class="ms text-5xl md:text-7xl mb-10 reveal">Where it runs</h2><div class="flex flex-wrap justify-center gap-3 reveal">{"".join(f'<span class="tag text-primary-fixed-dim">{p}</span>' for p in PLATFORMS)}</div></section>
<section class="px-6 md:px-16 py-24 max-w-[1200px] mx-auto grid md:grid-cols-2 gap-14 items-center"><div><p class="text-primary-fixed-dim text-xs font-bold tracking-widest uppercase mb-4 reveal">Our approach</p>
<h2 class="ms text-6xl md:text-8xl reveal">We send 1 to 3 names. <span class="text-accent-container">Not 200.</span></h2><div class="h-1 w-14 bg-accent mt-6"></div></div>
<p class="text-white/65 text-lg reveal">Most creator lists are long spreadsheets that someone still has to check. We check first. Brands get the few creators whose real numbers fit their product, and creators get introduced to brands that fit theirs.</p></section>
<section id="brands" class="relative bg-primary-container text-[#0b1623] px-6 py-24 text-center"><span class="side">For brands</span>
<h2 class="ms text-6xl md:text-9xl max-w-5xl mx-auto reveal">No guessing. Just the right creators.</h2><div class="h-1 w-14 bg-[#0b1623] mx-auto my-6"></div>
<div class="max-w-3xl mx-auto grid md:grid-cols-3 gap-8 text-left my-10">{pr}</div>
<a href="#workwithus" class="pill bg-[#0b1623] text-white">{CTA} →</a></section>
<section id="for-creators" class="relative bg-[#16293d] text-white px-6 py-24 text-center"><span class="side">For creators</span>
<h2 class="ms text-6xl md:text-9xl max-w-5xl mx-auto reveal">Brand deals that <span class="text-accent-container">fit your channel.</span></h2><div class="h-1 w-14 bg-accent mx-auto my-6"></div>
<div class="max-w-3xl mx-auto grid md:grid-cols-2 gap-8 text-left my-10 text-white">{"".join(f'<div class="reveal"><p class="font-bold text-lg">{t}</p><p class="text-white/70">{d}</p></div>' for _ic, t, d in CREATOR_BENEFITS)}</div>
<a href="#creators" class="pill bg-primary-container text-[#0b1623]">{CTA_C} →</a></section>
<section class="px-6 py-24 bg-[#16293d]"><div class="max-w-5xl mx-auto bg-primary-container text-[#0b1623] rounded-[28px] p-8 md:p-14 text-center reveal"><h2 class="ms text-5xl md:text-7xl mb-4">Let's get you matched.</h2><p class="mb-8 opacity-90">{CTA_SUB}</p>{forms('color')}</div></section>
{footer(True)}</div>"""
    page("layout-mindshare.html", "Layout test: MindShare-style | Gratovo", "MindShare-style",
         "Giant type on alternating blue and navy bands. Full-screen wordmark hero with two buttons, platform ticker, For Brands and For Creators bands, rounded closing card.",
         "bg-[#16293d]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;display=swap" rel="stylesheet">')


# ================================================================ 8. SMOOTH
def build_smooth():
    css = """
.serif { font-family: 'Fraunces', Georgia, serif; }
.hero-bg { background: linear-gradient(120deg, #2b1a4d, #0a5c9e, #5b2a86, #16293d); background-size: 300% 300%; animation: drift 16s ease-in-out infinite; }
@keyframes drift { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
.ellipse { fill:none; stroke:#fff; stroke-width:2.5; stroke-dasharray:1; stroke-dashoffset:1; animation: drawline 1.6s 1s ease-out forwards; }
@keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(8px); } }
.phone { width:200px; border:6px solid #2a1745; border-radius:32px; background:#fff; box-shadow:0 20px 40px rgba(42,23,69,.25); overflow:hidden; }
.cloud span { background:#fcfaf6; border-radius:999px; padding:10px 20px; font-weight:700; font-size:.78rem; letter-spacing:.06em; text-transform:uppercase; color:#2a1745; }
"""
    tags = ["AI assistants", "Automation", "Developer tools", "Productivity", "SaaS", "No-code", "AI agents", "Analytics", "Writing tools", "Design tools", "Meeting tools", "Research tools"]
    cloud = "".join(f"<span>{t}</span>" for t in tags)
    phones = "".join(
        f"""<div class="phone reveal" data-delay="{i*120}" style="margin-top:{[0,36,0][i]}px"><div class="bg-gradient-to-br from-[#2a1745] to-[#0a5c9e] h-64 flex flex-col items-center justify-center text-white text-center p-4">{mat('account_circle','text-6xl text-white/80')}<p class="serif text-xl mt-2">{EXAMPLES[i][0]}</p><p class="text-xs text-white/70">{EXAMPLES[i][1]}</p></div>
<div class="p-4 text-[#2a1745]"><p class="text-[10px] uppercase tracking-widest text-[#2a1745]/60 mb-2">Example format</p><div class="flex justify-between text-center"><div><p class="font-bold">{EXAMPLES[i][2]}</p><p class="text-[10px] uppercase">avg views</p></div><div><p class="font-bold">{EXAMPLES[i][3]}</p><p class="text-[10px] uppercase">engage</p></div><div><p class="font-bold">{EXAMPLES[i][4]}</p><p class="text-[10px] uppercase">US</p></div></div></div></div>"""
        for i in range(3))
    steps = "".join(f'<div class="reveal text-center px-4" data-delay="{i*120}"><p class="serif text-6xl text-[#7a4fc0]">{i+1}</p><h3 class="serif text-2xl text-[#2a1745] mt-2 mb-2">{t}</h3><p class="text-[#2a1745]/75">{d}</p></div>' for i, (t, d) in enumerate(STEPS3))
    body = f"""
<div class="bg-[#fcfaf6] text-[#2a1745]">
<section class="hero-bg relative min-h-screen text-white flex flex-col">
<div class="absolute inset-0 bg-[#2a1745]/45"></div>
<header class="relative z-10 flex items-center justify-between px-6 md:px-10 h-24"><a href="#">{wordmark("text-3xl")}</a>
<nav class="flex items-center gap-7 text-sm font-medium"><a class="hidden sm:block" href="#who">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="border border-white rounded-full px-5 py-2">Contact</a></nav></header>
<div class="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 pb-10">
<p class="text-xs font-semibold tracking-[.2em] uppercase mb-6">AI brands and creators, introduced</p>
<h1 class="serif text-5xl md:text-8xl max-w-5xl leading-[1.02]">Connecting AI brands with the <span class="relative inline-block">creators<svg class="absolute -inset-x-3 -inset-y-3 w-[calc(100%+1.5rem)] h-[calc(100%+1.5rem)]" viewBox="0 0 300 100" preserveAspectRatio="none" aria-hidden="true"><ellipse class="ellipse" pathLength="1" cx="150" cy="50" rx="146" ry="44"/></svg></span> their customers trust.</h1>
<p class="mt-8 max-w-xl text-lg text-white/85">{SUB} {BODY}</p>
{hero_buttons("bg-white text-[#2a1745] rounded-full px-9 py-4 font-semibold", "border border-white text-white rounded-full px-9 py-4 font-semibold", "mt-8 flex flex-wrap justify-center gap-3")}
<a href="#who" aria-label="Scroll down" class="mt-10 text-2xl" style="animation: bob 1.8s ease-in-out infinite">↓</a></div></section>
<section id="who" class="bg-[#e6def2] px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">What we send brands.</h2><p class="mb-14 text-[#2a1745]/75 reveal">Each creator, with the numbers that matter. Example formats, not real creators.</p>
<div class="flex flex-wrap justify-center gap-8 mb-20">{phones}</div>
<p class="text-sm tracking-widest uppercase mb-6 reveal">We work with products like:</p><div class="cloud flex flex-wrap justify-center gap-3 max-w-3xl mx-auto reveal">{cloud}</div></section>
<section id="approach" class="px-6 py-24 max-w-5xl mx-auto text-center"><h2 class="serif text-4xl md:text-6xl mb-14 reveal">How it works for <em class="text-[#7a4fc0]">brands</em>.</h2><div class="grid md:grid-cols-3 gap-8">{steps}</div>
<div class="grid sm:grid-cols-3 gap-4 mt-16">{"".join(f'<div class="reveal bg-white rounded-2xl p-6 text-left"><p class="font-bold mb-1">{t}</p><p class="text-sm text-[#2a1745]/70">{d}</p></div>' for _i, t, d in BENEFITS)}</div></section>
<div class="bg-[#e6def2] text-[#2a1745]">{creator_section('light')}</div>
<section class="bg-[#2a1745] text-white px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">Let's get you matched.</h2><p class="text-white/75 mb-10 reveal">{CTA_SUB}</p>{forms('dark')}</section>
{footer(True)}</div>"""
    page("layout-smooth.html", "Layout test: Smooth-style | Gratovo", "Smooth-style",
         "Soft and editorial. Full-screen tinted hero with a hand-drawn ellipse and two buttons, phone-shaped example cards, category pill cloud, For Creators section, serif headings.",
         "bg-[#fcfaf6]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&amp;display=swap" rel="stylesheet">')


# ================================================================ 9. ADHESIVE
def build_adhesive():
    css = """
.hl { color:#0072b8; }
.diagram { height:150px; position:relative; background:#f4f9fe; border-bottom:1px solid #d5e6f4; overflow:hidden; }
.node { position:absolute; background:#fff; border:1px solid #c5d5e4; border-radius:8px; padding:4px 10px; font:11px/1.2 'JetBrains Mono', monospace; text-transform:uppercase; color:#3e4c5e; }
@keyframes pulse2 { 0% { box-shadow:0 0 0 0 rgba(0,114,184,.45); } 100% { box-shadow:0 0 0 22px rgba(0,114,184,0); } }
.pulse { animation: pulse2 2s ease-out infinite; }
.carousel { display:flex; gap:20px; overflow-x:auto; scroll-snap-type:x mandatory; padding-bottom:8px; scrollbar-width:none; }
.carousel::-webkit-scrollbar { display:none; }
.carousel > article { flex:0 0 300px; scroll-snap-align:start; background:#fff; border:1px solid #d5e6f4; border-radius:14px; overflow:hidden; }
.step-tab { padding:10px 16px; border-radius:10px; font-weight:600; color:#3e4c5e; }
.step-tab.is-active { background:#fff; color:#0a5c9e; box-shadow:0 1px 4px rgba(0,0,0,.12); }
"""
    d1 = '<div class="node" style="left:34%;top:14%">Your product</div><div class="node" style="left:12%;top:68%">Audience</div><div class="node" style="left:60%;top:68%">Goals</div><svg class="absolute inset-0 w-full h-full" aria-hidden="true"><line x1="50%" y1="32%" x2="24%" y2="66%" stroke="#c5d5e4"/><line x1="50%" y1="32%" x2="72%" y2="66%" stroke="#c5d5e4"/></svg>'
    d2 = '<div class="node" style="left:10%;top:20%">Creator A</div><div class="node pulse" style="left:42%;top:52%;border-color:#0072b8;color:#0a5c9e">Creator B</div><div class="node" style="left:62%;top:16%">Creator C</div>'
    d3 = '<div class="node pulse" style="left:26%;top:38%;border-color:#0072b8;color:#0a5c9e">Deal agreed ✓</div><div class="node" style="left:8%;top:8%">Scripts</div><div class="node" style="left:64%;top:10%">Dates</div><div class="node" style="left:60%;top:76%">Contract</div>'
    d4 = '<div class="absolute inset-0 flex items-center justify-center"><span class="pulse w-16 h-16 rounded-full bg-primary-container text-white flex items-center justify-center">' + mat('play_arrow', 'text-4xl') + '</span></div>'
    diag = [d1, d2, d3, d4]
    cards = "".join(
        f'<article><div class="diagram">{diag[i]}</div><div class="p-6"><p class="font-label-sm text-primary-container mb-1">STEP {i+1}</p><h3 class="font-headline-md text-on-background mb-1">{t}</h3><p class="text-secondary text-sm">{d}</p></div></article>'
        for i, (t, d) in enumerate(STEPS4))
    cats = [("AI assistants", "Reach people already learning to get more from AI chat and writing tools."),
            ("Automation", "Show workflow builders how your tool saves them hours, on screen."),
            ("Developer tools", "Put your product in front of developers who watch tutorials before they buy."),
            ("Productivity", "Get walked through in real workflows by creators who use tools like yours daily.")]
    tabs = "".join(f'<button class="step-tab" role="tab">{c}</button>' for c, _ in cats)
    panels = "".join(f'<div class="step-panel"><p class="text-lg text-on-surface-variant">{d}</p></div>' for _, d in cats)
    plats = "".join(f'<span class="font-headline-md text-secondary/70 uppercase tracking-widest">{p}</span>' for p in PLATFORMS * 3)
    ben = "".join(f'<div class="reveal" data-delay="{i*100}"><div class="w-12 h-12 rounded-xl bg-primary-fixed text-primary-container flex items-center justify-center mb-4">{mat(ic, "text-2xl")}</div><h3 class="font-headline-md mb-1">{t}</h3><p class="text-secondary">{d}</p></div>' for i, (ic, t, d) in enumerate(BENEFITS))
    hb = hero_buttons("bg-primary-container text-white rounded-md px-7 py-4 font-semibold", "border border-outline-variant rounded-md px-7 py-4 font-semibold", "mt-8 flex flex-wrap gap-3")
    body = f"""
<div class="bg-white text-on-background">
<header class="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-outline-variant"><div class="max-w-container-max mx-auto px-6 h-20 flex items-center justify-between"><a href="#">{wordmark()}</a>
<nav class="flex items-center gap-7 text-sm font-medium"><a class="hidden sm:block border-t-2 border-on-background pt-1" href="#">Home</a><a class="hidden sm:block" href="#how-it-works">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="bg-primary-container text-white rounded-md px-5 py-2.5 font-semibold">Contact</a></nav></div></header>
<main>
<section class="max-w-container-max mx-auto px-6 pt-20 pb-16"><p class="font-label-sm text-primary-container mb-4 tracking-widest">AI INFLUENCER MARKETING</p>
<h1 class="font-headline-lg text-4xl md:text-7xl max-w-5xl leading-[1.05]">{HEAD_PARTS[0]}<span class="hl">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-6 text-xl text-secondary max-w-2xl">{SUB} {BODY}</p>{hb}</section>
<section class="border-y border-outline-variant py-5 marquee bg-surface-container-low"><div class="marquee-track">{plats}{plats}</div></section>
{proc}
<section id="who" class="bg-[#e6def2] px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">What we send brands.</h2><p class="mb-14 text-[#2a1745]/75 reveal">Each creator, with the numbers that matter. Example formats, not real creators.</p>
<div class="flex flex-wrap justify-center gap-8 mb-20">{phones}</div>
<p class="text-sm tracking-widest uppercase mb-6 reveal">We work with products like:</p><div class="cloud flex flex-wrap justify-center gap-3 max-w-3xl mx-auto reveal">{cloud}</div></section>
<section id="approach" class="px-6 py-24 max-w-5xl mx-auto text-center"><h2 class="serif text-4xl md:text-6xl mb-14 reveal">How it works for <em class="text-[#7a4fc0]">brands</em>.</h2><div class="grid md:grid-cols-3 gap-8">{steps}</div>
<div class="grid sm:grid-cols-3 gap-4 mt-16">{"".join(f'<div class="reveal bg-white rounded-2xl p-6 text-left"><p class="font-bold mb-1">{t}</p><p class="text-sm text-[#2a1745]/70">{d}</p></div>' for _i, t, d in BENEFITS)}</div></section>
<div class="bg-[#e6def2] text-[#2a1745]">{creator_section('light')}</div>
<section class="bg-[#2a1745] text-white px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">Let's get you matched.</h2><p class="text-white/75 mb-10 reveal">{CTA_SUB}</p>{forms('dark')}</section>
{footer(True)}</div>"""
    page("layout-smooth.html", "Layout test: Smooth-style | Gratovo", "Smooth-style",
         "Soft and editorial. Full-screen tinted hero with a hand-drawn ellipse and two buttons, phone-shaped example cards, category pill cloud, For Creators section, serif headings.",
         "bg-[#fcfaf6]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&amp;display=swap" rel="stylesheet">')


# ================================================================ 9. ADHESIVE
def build_adhesive():
    css = """
.hl { color:#0072b8; }
.step-tab { padding:12px 16px; border-bottom:3px solid transparent; font-weight:600; color:#686867; white-space:nowrap; }
.step-tab.is-active { color:#121212; border-color:#0072b8; }
.nav-blur { backdrop-filter: blur(10px); background: rgba(246,249,255,.85); }
"""
    rows = "".join(
        f'<details class="row"><summary><span class="sp-eyebrow">0{i+1}</span><span class="font-headline-md text-2xl font-bold">{t}</span><span class="hidden md:block text-secondary text-sm">Included</span><span class="tog">+</span></summary><p>{d}</p></details>'
        for i, (t, d) in enumerate(SERVICES))
    cats = [("AI assistants", "Reach people already learning to get more from AI chat and writing tools."),
            ("Automation", "Show workflow builders how your tool saves them hours, on screen."),
            ("Developer tools", "Put your product in front of developers who watch tutorials before they buy."),
            ("Productivity", "Get walked through in real workflows by creators who use tools like yours daily.")]
    cat_tabs = "".join(f'<button class="step-tab" role="tab">{c}</button>' for c, _ in cats)
    cat_panels = "".join(f'<div class="step-panel" role="tabpanel"><h3 class="sp-h text-3xl mb-3">{c}</h3><p class="text-[#3f403e] max-w-xl">{d}</p></div>' for c, d in cats)
    step_panels = "".join(
        f'<div class="step-panel"><p class="sp-eyebrow mb-2">Step {i+1} of 5</p><h3 class="sp-h text-3xl mb-3">{t}</h3><p class="text-[#3f403e] max-w-xl">{d}</p></div>' for i, (t, d) in enumerate(STEPS5))
    faq = "".join(f'<details class="row"><summary style="grid-template-columns:1fr 24px"><span class="font-headline-md text-xl font-bold">{q}</span><span class="tog">+</span></summary><p style="padding-left:0">{a}</p></details>' for q, a in FAQ)
    body = f"""
<div class="bg-[#f6f9ff] text-[#121212]">
<header class="nav-blur sticky top-0 z-50 border-b border-[#deded8]"><div class="max-w-[80rem] mx-auto px-6 h-[72px] flex items-center justify-between">
<a href="#">{wordmark("text-2xl")}</a>
<nav class="hidden md:flex gap-8 text-sm font-medium"><a href="#services">For brands</a><a href="#for-creators">For creators</a><a href="#process">How it works</a><a href="#faq">Questions</a></nav>
<a href="#workwithus" class="bg-primary-container text-white rounded-2xl px-5 py-3 text-sm font-semibold">{CTA}</a></div></header>
<main>
<section class="relative overflow-hidden"><div class="absolute inset-x-0 bottom-0 h-[55%] pointer-events-none">
<svg viewBox="0 0 760 430" preserveAspectRatio="none" class="w-full h-full" aria-hidden="true"><defs><linearGradient id="ga" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#0072b8" stop-opacity=".25"/><stop offset="1" stop-color="#0072b8" stop-opacity=".02"/></linearGradient></defs>
<path class="growth-area" d="M0 400 L90 385 L170 392 L250 360 L330 366 L410 330 L490 335 L560 230 L640 215 L700 110 L760 40 L760 430 L0 430 Z"/>
<path class="growth-path" pathLength="1" d="M0 400 L90 385 L170 392 L250 360 L330 366 L410 330 L490 335 L560 230 L640 215 L700 110 L760 40"/></svg>
<span class="stage" style="left:24%;bottom:22%;animation-delay:1.2s">Request</span><span class="stage" style="left:42%;bottom:33%;animation-delay:1.8s">Match</span>
<span class="stage" style="left:62%;bottom:50%;animation-delay:2.4s">Agree</span><span class="stage" style="left:82%;bottom:72%;animation-delay:3s">Launch</span></div>
<div class="relative max-w-[80rem] mx-auto px-6 pt-20 pb-72 md:pb-80">
<p class="sp-eyebrow mb-6">AI influencer marketing</p>
<h1 class="sp-h text-5xl md:text-8xl max-w-5xl">{HEAD_PARTS[0]}<span class="text-primary-container">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-6 text-lg text-[#3f403e] max-w-2xl">{SUB} {BODY}</p>
{hero_buttons("bg-primary-container text-white rounded-2xl px-6 py-4 font-semibold", "bg-[#121212] text-white rounded-2xl px-6 py-4 font-semibold", "mt-8 flex flex-wrap gap-3")}</div></section>
<section class="max-w-[80rem] mx-auto px-6 pb-24 grid md:grid-cols-2 gap-5">
<article class="sp-card p-9 reveal"><p class="sp-eyebrow mb-3">The buying journey</p><h3 class="sp-h text-3xl mb-3">People watch before they buy.</h3><p class="text-[#3f403e]">Before trying a new AI tool, people watch tutorials, compare options, and listen to creators they already trust.</p></article>
<article class="sp-card p-9 reveal" data-delay="120"><p class="sp-eyebrow mb-3">Our role</p><h3 class="sp-h text-3xl mb-3">We connect both sides.</h3><p class="text-[#3f403e]">We find the right creator for the brand, and the right brand deal for the creator, and keep the conversation moving between them.</p></article></section>
<section id="services" class="max-w-[80rem] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">For brands</p><h2 class="sp-h text-4xl md:text-6xl">What brands get.</h2></div><div class="max-w-4xl mx-auto border-b border-[#deded8]">{rows}</div></section>
<section class="bg-white py-24"><div class="max-w-[80rem] mx-auto px-6"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">Built for AI</p><h2 class="sp-h text-4xl md:text-6xl">Creator marketing works when the product needs showing.</h2></div>
<div data-stepper class="max-w-4xl mx-auto"><div class="flex justify-center gap-2 overflow-x-auto border-b border-[#deded8]" role="tablist">{cat_tabs}</div>
<div class="sp-card p-10 mt-8 min-h-[190px] relative">{cat_panels}<div class="absolute right-6 top-6 flex flex-col items-center gap-2"><button data-prev aria-label="Previous" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">←</button><span data-count class="text-xs text-[#686867]"></span><button data-next aria-label="Next" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">→</button></div></div></div></div></section>
{creator_section('light')}
<section id="process" class="max-w-[80rem] mx-auto px-6 py-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">How it works for brands</p><h2 class="sp-h text-4xl md:text-6xl">From message to live video.</h2></div>
<div data-stepper class="max-w-4xl mx-auto"><div class="sp-card p-10 min-h-[190px] relative">{step_panels}<div class="absolute right-6 top-6 flex flex-col items-center gap-2"><button data-prev aria-label="Previous step" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">←</button><span data-count class="text-xs text-[#686867]"></span><button data-next aria-label="Next step" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">→</button></div></div></div></section>
<section class="max-w-[80rem] mx-auto px-6 pb-24"><div class="sp-card p-10 md:p-14 grid md:grid-cols-2 gap-8 items-center reveal" style="border-left:4px solid #0072b8;border-top:1px solid #deded8"><div><p class="sp-eyebrow mb-3">Our approach</p><h3 class="sp-h text-4xl">Brands bring the product. Creators bring the audience.</h3></div><p class="text-[#3f403e]">We don't hand brands a spreadsheet of 200 names. We check each creator's real numbers, send the one to three that fit, and keep it simple for creators too.</p></div></section>
<section id="faq" class="max-w-4xl mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">Common questions</p><h2 class="sp-h text-4xl md:text-5xl">What to know before we work together.</h2></div><div class="border-b border-[#deded8]">{faq}</div></section>
<section class="px-6 pb-24"><div class="max-w-5xl mx-auto text-center reveal"><p class="sp-eyebrow mb-3">Let's work together</p><h2 class="sp-h text-4xl md:text-5xl mb-4">Brands and creators, start here.</h2><p class="text-[#3f403e] mb-8">{CTA_SUB}</p>{forms('light')}</div></section>
</main>
<footer class="bg-[#121212] text-white/75 py-14"><div class="max-w-[80rem] mx-auto px-6 grid md:grid-cols-3 gap-8"><div>{wordmark("text-2xl")}<p class="mt-4 text-sm">Connecting AI and SaaS brands with vetted creators, and creators with brand deals that fit.</p></div>
<div><p class="font-label-sm uppercase mb-3 text-white">Explore</p><div class="space-y-2 text-sm"><a class="block" href="#services">For brands</a><a class="block" href="#for-creators">For creators</a><a class="block" href="#faq">Questions</a></div></div>
<div><p class="font-label-sm uppercase mb-3 text-white">Contact</p><p class="text-sm">{EMAIL}</p><p class="text-sm mt-4"><a href="{ASSET}privacy-policy.html">Privacy</a> · <a href="{ASSET}terms-of-service.html">Terms</a></p></div></div>
<p class="max-w-[80rem] mx-auto px-6 mt-10 text-xs text-white/50">© 2026 Gratovo.</p></footer></div>"""
    page("layout-scalepledge.html", "Layout test: Scale Pledge-style | Gratovo", "Scale Pledge-style",
         "Editorial and light. Hero line draws itself with the four stages, accordion services, tabbed carousel, For Creators section, step carousel, FAQ.",
         "bg-[#f6f9ff]", css, body)


# ================================================================ 4. NSENTIVE
def build_nsentive():
    css = """
.dict-line { opacity:0; animation: fadein .9s ease forwards; }
.n-card { border:1px solid rgba(255,255,255,.55); border-radius:28px; padding:26px 26px 40px; }
.n-row { border-top:1px solid #3a3a3a; display:grid; grid-template-columns: 1fr 1.4fr 60px; gap:24px; padding:34px 0; align-items:start; }
@media (max-width: 768px) { .n-row { grid-template-columns: 1fr; gap: 10px; padding: 24px 0; } .n-row > span { display: none; } }
.loop { height: 340px; overflow: hidden; -webkit-mask-image: linear-gradient(transparent, #000 25%, #000 75%, transparent); mask-image: linear-gradient(transparent, #000 25%, #000 75%, transparent); }
.loop-track { animation: scrollup 14s linear infinite; }
.loop-track span { display:block; text-align:center; font-size:1.7rem; line-height:3.1rem; color:#fff; }
.loop-track span:nth-child(3n+2) { font-family: Georgia, serif; font-style: italic; }
"""
    cards = "".join(
        f'<div class="n-card reveal" data-delay="{i*100}"><div class="mb-14 text-white">{mat(ic, "text-3xl", False)}</div><h3 class="text-2xl font-semibold text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>'
        for i, (ic, t, d) in enumerate(BENEFITS))
    w = [("WHO", "Brands and creators in AI and SaaS: marketing managers and founders who want creators promoting their product, and creators who want brand deals that fit."),
         ("WHAT", "Brands get 1 to 3 vetted AI creators picked for their product. Creators get put forward to brands that fit their audience."),
         ("WHY", "People watching AI tutorials are looking for tools to try. A trusted creator showing a product reaches them at that moment."),
         ("WHERE", "YouTube, LinkedIn, X, and newsletters, wherever the right creator's audience is."),
         ("HOW", "Tell us about your product or your channel. We make the introduction. We take care of contracts, scripts, and posting."),
         ("WHEN", "We reply within 24 hours. Most deals go live within about a month.")]
    rows = "".join(f'<div class="n-row reveal"><h3 class="text-5xl md:text-6xl font-semibold text-[#161616]">{a}</h3><p class="text-[#555] text-lg">{c}</p><span class="text-3xl text-[#161616]">↘</span></div>' for a, c in w)
    who = [("Marketing managers", "Hand off the searching, vetting, and chasing. Keep the final say."),
           ("Founders", "Get your product in front of the right audience without learning creator marketing first."),
           ("Creators", "Get brand deals that fit your channel, without cold outreach or endless email threads.")]
    whorows = "".join(f'<div class="n-row reveal"><h3 class="text-4xl md:text-5xl font-semibold text-[#161616]">{a}</h3><p class="text-[#555] text-lg">{b}</p><span class="text-3xl text-[#161616]">↘</span></div>' for a, b in who)
    flow = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="text-white/40 text-sm mb-3">0{i+1}</p><h3 class="text-4xl font-semibold text-white mb-3">{t}</h3><p class="text-white/70">{d}</p></div>' for i, (t, d) in enumerate(STEPS4))
    loop_items = "".join(f"<span>{x}</span>" for x in ["no cold emails", "no chasing replies", "no guessing who's legit", "no endless threads", "just the right match"] * 2)
    body = f"""
<div class="bg-black text-white">
<header class="max-w-[1280px] mx-auto px-6 h-24 flex items-center justify-between"><a href="#">{wordmark("text-4xl")}</a><a href="#workwithus" class="bg-primary-container text-white rounded-full px-8 py-3 font-medium">Let's Talk</a></header>
<main>
<section class="text-center px-6 pt-16 pb-24">
<h1 class="dict-line text-6xl md:text-8xl font-semibold tracking-tight" style="animation-delay:.2s">match</h1>
<p class="dict-line text-3xl md:text-4xl text-white/35 mt-3" style="animation-delay:.9s">/mætʃ/</p>
<p class="dict-line text-3xl md:text-4xl font-semibold mt-1" style="animation-delay:1.5s">noun</p>
<p class="dict-line text-xl md:text-2xl mt-8 max-w-2xl mx-auto text-white/90" style="animation-delay:2.1s">A creator whose audience fits your product. A brand deal that fits your channel. We find both.</p>
{hero_buttons("bg-white text-black rounded-full px-10 py-4 font-semibold", "border border-white text-white rounded-full px-10 py-4 font-semibold", "dict-line mt-10 flex flex-wrap justify-center gap-4\" style=\"animation-delay:2.7s")}</section>
<section class="max-w-[1280px] mx-auto px-6 pb-28 grid md:grid-cols-3 gap-6">{cards}</section>
<div class="bg-white text-[#161616]"><div class="max-w-[1280px] mx-auto px-6 py-24">
<h2 class="text-5xl md:text-7xl font-semibold tracking-tight mb-14 reveal">The short version.</h2><div class="border-b border-[#3a3a3a]">{rows}</div></div>
<div class="max-w-[1280px] mx-auto px-6 pb-24"><h2 class="text-5xl md:text-7xl font-semibold tracking-tight mb-14 reveal">Who it's for.</h2><div class="border-b border-[#3a3a3a]">{whorows}</div></div></div>
{creator_section('dark')}
<section class="max-w-[1280px] mx-auto px-6 py-28"><h2 class="text-5xl md:text-7xl font-semibold tracking-tight text-center mb-16 reveal">Four steps for brands.</h2><div class="grid md:grid-cols-4 gap-10">{flow}</div></section>
<section class="bg-primary-container px-6 py-24"><div class="max-w-[1200px] mx-auto grid md:grid-cols-[1fr_2.4fr] gap-10 items-center">
<div class="loop hidden md:block"><div class="loop-track">{loop_items}</div></div>
<div class="bg-black rounded-[28px] p-8 md:p-10"><h2 class="text-center text-3xl font-semibold mb-2">Let's Talk</h2><p class="text-center text-white/70 mb-6">{CTA_SUB}</p>{forms('dark')}</div></div></section>
</main>{footer(True)}</div>"""
    page("layout-nsentive.html", "Layout test: Nsentive-style | Gratovo", "Nsentive-style",
         "Black to white to brand blue. Dictionary-style hero that fades in line by line, outlined cards, ruled rows (brands, creators), scrolling word list beside the forms.",
         "bg-black", css, body)


# ================================================================ 5. APOLLO
def build_apollo():
    css = """
@keyframes twinkle { 0%,100% { opacity:.15; } 50% { opacity:.9; } }
@keyframes shoot { 0% { transform: translate(0,0) rotate(-35deg); opacity:0; } 8% { opacity:1; } 30% { transform: translate(-420px,300px) rotate(-35deg); opacity:0; } 100% { opacity:0; } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes counter { to { transform: rotate(-360deg); } }
.shoot { position:absolute; top:8%; right:12%; width:120px; height:2px; background:linear-gradient(90deg, rgba(255,255,255,0), #fff); animation: shoot 7s 2s infinite; }
.glass { background: linear-gradient(160deg, rgba(255,255,255,.08), rgba(255,255,255,.02)); border:1px solid rgba(255,255,255,.12); border-radius:28px; backdrop-filter: blur(10px); }
.grad-text { background: linear-gradient(90deg, #ffd9a8, #ff8fb3, #b88cff); -webkit-background-clip:text; background-clip:text; color:transparent; }
.chip { position:absolute; background: rgba(20,30,70,.9); border:1px solid rgba(255,255,255,.18); border-radius:16px; padding:10px 14px; font-size:13px; color:#fff; animation: floaty 6s ease-in-out infinite; box-shadow:0 10px 30px rgba(0,0,0,.4); }
.orbit { position:relative; width:260px; height:260px; margin:auto; }
.orbit .ring { position:absolute; inset:0; border:1px dashed rgba(255,255,255,.25); border-radius:50%; animation: spin 24s linear infinite; }
.orbit .ring i { position:absolute; width:52px; height:52px; margin:-26px; border-radius:16px; background:#fff; color:#16293d; display:flex; align-items:center; justify-content:center; animation: counter 24s linear infinite; }
.orbit .core { position:absolute; inset:88px; border-radius:24px; background: linear-gradient(135deg,#0a5c9e,#6a54e8); display:flex; align-items:center; justify-content:center; box-shadow:0 0 50px rgba(106,84,232,.6); }
.ghost { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size: clamp(120px, 24vw, 340px); font-weight:800; color: rgba(255,255,255,.05); pointer-events:none; letter-spacing:-.04em; }
.beam { height:1px; background: linear-gradient(90deg, transparent, rgba(150,130,255,.8), transparent); background-size:200% 100%; animation: shimmer 4s linear infinite; }
@keyframes shimmer { to { background-position: -200% 0; } }
"""
    blocks = [("It's that easy.", "Send us a short message. We do the searching, vetting, and chasing."),
              ("Peace of mind.", "Every creator is checked for real views, engagement, and audience location first."),
              ("Your product, shown properly.", "Creators demo your tool in a real workflow, for an audience that wants to try it."),
              ("Nothing goes live unseen.", "You approve the video before it posts.")]
    bl = "".join(f'<div class="glass p-8 reveal" data-delay="{i*100}"><h3 class="font-headline-md text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>' for i, (t, d) in enumerate(blocks))
    stats = "".join(f'<div class="text-center"><p class="text-5xl font-bold text-white">{v}</p><p class="text-white/65 mt-2 max-w-[200px] mx-auto">{l}</p></div>' for v, l in STATS[:3])
    steps = "".join(f'<div class="glass p-7 reveal" data-delay="{i*90}"><span class="grad-text text-4xl font-bold">0{i+1}</span><h3 class="font-headline-md text-white mt-3 mb-2">{t}</h3><p class="text-white/70 text-sm">{d}</p></div>' for i, (t, d) in enumerate(STEPS5))
    plat_icons = ["smart_display", "work", "tag", "mail"]
    orbit_items = "".join(
        f'<i style="left:{50 + 50*math.cos(a)}%;top:{50 + 50*math.sin(a)}%">{mat(ic, "text-2xl", True)}</i>'
        for ic, a in zip(plat_icons, [0, 1.5708, 3.1416, 4.7124]))
    pill = "inline-block border border-white/25 bg-white/10 rounded-full px-7 py-3 text-sm font-semibold"
    body = f"""
<div class="bg-[#050a1f] text-white relative overflow-hidden">
<div id="stars" class="absolute inset-0 pointer-events-none"></div><div class="shoot"></div>
<header class="relative z-20 max-w-[1280px] mx-auto px-6 h-20 flex items-center justify-between"><a href="#">{wordmark("text-3xl")}</a>
<nav class="hidden md:flex gap-1 border border-white/15 rounded-full px-2 py-2 text-sm bg-white/5"><a class="px-4 py-1.5 rounded-full bg-white/10" href="#">Home</a><a class="px-4 py-1.5" href="#brands">For brands</a><a class="px-4 py-1.5" href="#for-creators">For creators</a><a class="px-4 py-1.5" href="#process">How it works</a></nav>
<a href="#workwithus" class="border border-white/25 bg-white/5 rounded-lg px-5 py-2 text-sm">Contact</a></header>
<main class="relative z-10">
<section class="text-center px-6 pt-14 pb-12"><h1 class="font-display-lg text-4xl md:text-7xl max-w-5xl mx-auto leading-[1.05]">{HEAD_PARTS[0]}<span class="grad-text">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-5 text-white/70 text-lg max-w-2xl mx-auto">{SUB}</p></section>
<section class="max-w-[1280px] mx-auto px-6 grid md:grid-cols-2 gap-6 pb-24">
<div id="brands" class="glass p-8 md:p-10 text-center relative overflow-hidden min-h-[470px] reveal"><h2 class="font-display-lg text-4xl mb-3">for brands.</h2><p class="text-white/70 mb-6">1 to 3 vetted AI creators picked for your product.</p>
<a href="#workwithus" class="{pill}">{CTA}</a>
<div class="relative h-56 mt-6"><div class="chip" style="left:6%;top:6%;--r:-6deg">Creator A · 42K avg views</div><div class="chip" style="left:34%;top:38%;--r:4deg;animation-delay:1s">Creator B · 5.1% engagement</div><div class="chip" style="left:12%;top:70%;--r:-3deg;animation-delay:2s">Creator C · 46% US audience</div></div>
<p class="absolute bottom-3 inset-x-0 text-[11px] text-white/45 uppercase tracking-wider">Example format</p></div>
<div class="glass p-8 md:p-10 text-center min-h-[470px] reveal" data-delay="120"><h2 class="font-display-lg text-4xl mb-3">for creators.</h2><p class="text-white/70 mb-6">Brand deals that fit your channel. YouTube, LinkedIn, X, and newsletters.</p>
<a href="#creators" class="{pill}">{CTA_C}</a>
<div class="orbit mt-8"><div class="core">{mat('rocket_launch', 'text-4xl text-white')}</div><div class="ring">{orbit_items}</div></div></div></section>
<section class="max-w-[1280px] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><span class="inline-block border border-white/20 rounded-full px-4 py-1 text-sm mb-4">What brands get ✦</span><h2 class="font-display-lg text-4xl md:text-6xl">A simpler way to work with AI creators.</h2></div><div class="grid md:grid-cols-2 gap-5">{bl}</div></section>
<section class="relative max-w-[1100px] mx-auto px-6 py-24"><div class="ghost" aria-hidden="true">1-3</div><div class="relative"><div class="beam mb-12"></div><div class="grid md:grid-cols-3 gap-10">{stats}</div><div class="beam mt-12"></div></div><p class="relative text-center text-white/60 mt-8">Every creator we recommend passes these checks first.</p></section>
{creator_section('dark')}
<section id="process" class="max-w-[1280px] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><h2 class="font-display-lg text-4xl md:text-6xl">How a deal works with us.</h2></div><div class="grid md:grid-cols-5 gap-4">{steps}</div></section>
<section class="max-w-[1100px] mx-auto px-6 pb-24"><div class="glass p-8 md:p-14 text-center reveal"><h2 class="font-display-lg text-4xl md:text-6xl mb-3">Ready for <span class="grad-text">take-off?</span></h2><p class="text-white/70 mb-10">{CTA_SUB}</p>{forms('dark')}</div></section>
</main>{footer(True)}</div>"""
    page("layout-apollo.html", "Layout test: Apollo-style | Gratovo", "Apollo-style",
         "Dark space theme. Twinkling stars and a shooting star, a glass card for brands and one for creators, floating chips, orbiting platform icons, ghost number behind the stats.",
         "bg-[#050a1f]", css, body)


# ================================================================ 6. RIGHT CLICK
def build_rightclick():
    css = """
.display { font-family: 'Anton', 'Plus Jakarta Sans', sans-serif; text-transform: uppercase; letter-spacing: .01em; line-height: .95; }
.mono { font-family: 'JetBrains Mono', monospace; }
.rc-cap { color:#9ad6f7; }
.rc-btn { border:1px solid #9ad6f7; color:#9ad6f7; border-radius:999px; padding:18px 28px; font-size:1.6rem; display:flex; justify-content:space-between; align-items:center; transition:.25s; }
.rc-btn:hover { background:#9ad6f7; color:#050a14; }
.rc-btn:hover span { color:#050a14 !important; }
.fcard { position:absolute; width:150px; border-radius:18px; padding:14px; color:#fff; box-shadow:0 14px 40px rgba(0,0,0,.5); animation: floaty 7s ease-in-out infinite; }
#scroll-progress-wrap { position:fixed; left:10px; top:90px; bottom:40px; width:3px; z-index:50; }
#scroll-progress { width:3px; background:#9ad6f7; height:0; }
"""
    cards = [("30K+", "avg views", "left:2%;top:6%;--r:-8deg;background:linear-gradient(135deg,#6a54e8,#b8286e)", 0),
             ("3-8%", "engagement", "right:3%;top:2%;--r:6deg;background:linear-gradient(135deg,#0a5c9e,#0072b8)", 1.2),
             ("35%+", "target audience", "left:6%;top:48%;--r:5deg;background:linear-gradient(135deg,#b8286e,#ff7a59)", 2.2),
             ("1-3", "creators, not 200", "right:2%;top:42%;--r:-5deg;background:linear-gradient(135deg,#0072b8,#1fb6a6)", 3.2)]
    fc = "".join(f'<div class="fcard hidden md:block" style="{st};animation-delay:{d}s"><p class="display text-4xl">{v}</p><p class="text-xs uppercase tracking-wider opacity-90">{l}</p></div>' for v, l, st, d in cards)
    pills = [("BRANDS", "Vetted AI creators for your product.", "#workwithus"),
             ("CREATORS", "Brand deals that fit your channel.", "#creators"),
             ("HOW IT WORKS", "Four steps, from message to live video.", "#process")]
    pl = "".join(f'<a href="{h}" class="rc-btn reveal mono" data-delay="{i*100}"><span>{a}</span><span class="text-base text-white/70 max-w-md text-right hidden md:block">{b}</span><span>↗</span></a>' for i, (a, b, h) in enumerate(pills))
    ex = "".join(example_card(i) for i in range(3))
    steps = "".join(f'<div class="reveal border-l border-[#9ad6f7]/50 pl-5" data-delay="{i*100}"><p class="display text-4xl rc-cap">0{i+1}</p><h3 class="mono text-lg font-semibold mt-2">{t}</h3><p class="mono text-white/70 text-sm mt-1">{d}</p></div>' for i, (t, d) in enumerate(STEPS4))
    hb = hero_buttons("bg-[#9ad6f7] text-[#050a14] font-bold rounded-full px-8 py-4", "border border-[#9ad6f7] text-[#9ad6f7] font-bold rounded-full px-8 py-4", "mt-8 flex flex-wrap justify-center gap-4")
    body = f"""
<div class="bg-[#050a14] text-white mono">
<div id="scroll-progress-wrap" aria-hidden="true"><div id="scroll-progress"></div></div>
<header class="relative z-20 flex items-center justify-between px-6 md:px-12 h-24"><span class="mono text-xs rc-cap hidden md:block"><span id="scroll-progress-num">0</span> / 100</span>
<a href="#" class="md:absolute md:left-1/2 md:-translate-x-1/2">{wordmark("text-3xl")}</a><a href="#workwithus" class="ml-auto bg-white/10 rc-cap rounded-full px-5 py-2 text-xs tracking-widest">WORK WITH US</a></header>
<main>
<section class="relative min-h-[88vh] flex flex-col items-center justify-center text-center px-6 overflow-hidden">{fc}
<h1 class="display rc-cap text-[clamp(3rem,10vw,8.5rem)] max-w-6xl relative z-10">{HEADLINE}</h1>
<p class="relative z-10 mt-6 max-w-xl text-white/80">{SUB}</p><div class="relative z-10">{hb}</div></section>
<section class="max-w-5xl mx-auto px-6 pb-24"><div class="border border-[#9ad6f7] rounded-[32px] p-10 md:p-14 text-center reveal"><p class="text-xl leading-relaxed">We're <b class="rc-cap">Gratovo</b>. We connect AI brands with vetted creators, and creators with brand deals that fit. {BODY}</p></div></section>
<section class="max-w-5xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-10 reveal">Who we work with</h2><div class="space-y-5">{pl}</div></section>
<section class="max-w-6xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-3 reveal">What we send brands</h2><p class="text-white/70 mb-10 reveal">Hover a card. Example formats, not real creators.</p><div class="grid sm:grid-cols-3 gap-5 reveal">{ex}</div></section>
{creator_section('dark', head_cls='display')}
<section id="process" class="max-w-6xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-12 reveal">Four steps for brands</h2><div class="grid md:grid-cols-4 gap-8">{steps}</div></section>
<section class="max-w-5xl mx-auto px-6 pb-28 text-center"><h2 class="display rc-cap text-6xl md:text-8xl mb-6 reveal">Ready to get started?</h2><p class="text-white/70 mb-10">{CTA_SUB}</p>{forms('dark')}</section>
</main>{footer(True)}</div>"""
    page("layout-rightclick.html", "Layout test: Right Click-style | Gratovo", "Right Click-style",
         "Bold and edgy. Giant condensed headline with floating stat cards and two buttons, scroll progress counter on the left edge, outlined pill rows (brands, creators), big closing line.",
         "bg-[#050a14]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;display=swap" rel="stylesheet">')


# ================================================================ 7. MINDSHARE
def build_mindshare():
    css = """
.ms { font-family: 'Anton', 'Plus Jakarta Sans', sans-serif; text-transform: uppercase; letter-spacing: -.01em; line-height: .92; }
.pill { border-radius:999px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; font-size:.8rem; padding:18px 30px; display:inline-flex; gap:8px; align-items:center; }
.tag { border:1px solid currentColor; border-radius:999px; padding:6px 14px; font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.side { position:absolute; left:18px; top:40px; writing-mode:vertical-rl; transform:rotate(180deg); font-size:.7rem; letter-spacing:.25em; opacity:.6; text-transform:uppercase; }
@keyframes ticker { to { transform: translateX(-50%); } }
.ticker .marquee-track { animation: ticker 22s linear infinite; }
"""
    plats = "".join(f'<span class="ms text-4xl md:text-5xl text-[#16293d]/80">{p}</span>' for p in PLATFORMS * 3)
    svc = "".join(f'<div class="reveal border-t border-white/20 pt-6" data-delay="{i*90}"><p class="text-primary-fixed-dim text-xs font-bold tracking-widest mb-2">0{i+1}</p><h3 class="ms text-3xl mb-2">{t}</h3><p class="text-white/65">{d}</p></div>' for i, (t, d) in enumerate(SERVICES[:4]))
    props = [("Zero outreach", "We contact the creators. You only hear about the ones worth your time."),
             ("Real numbers", "Views, engagement, and audience location, checked before you see a name."),
             ("You approve it", "Nothing goes live until you've seen the video.")]
    pr = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="font-bold text-lg">{a}</p><p class="text-[#0b1623]/90">{b}</p></div>' for i, (a, b) in enumerate(props))
    cprops = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="font-bold text-lg">{t}</p><p class="text-[#0b1623]/90">{d}</p></div>' for i, (_ic, t, d) in enumerate(CREATOR_BENEFITS))
    body = f"""
<div class="bg-[#16293d] text-white">
<section class="relative bg-primary-container text-[#0b1623] min-h-screen flex flex-col">
<header class="flex items-center justify-between px-6 md:px-10 h-20"><a href="#" class="bg-white rounded-xl px-3 py-1">{wordmark("text-2xl")}</a>
<nav class="flex items-center gap-6 text-xs tracking-widest uppercase font-semibold"><a class="hidden sm:block" href="#brands">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="bg-[#0b1623] text-white rounded-full px-5 py-2">Contact</a></nav></header>
<div class="flex-1 flex flex-col items-center justify-center text-center px-6"><h1 class="ms text-[clamp(4.5rem,17vw,15rem)] text-[#0b1623]">Gratovo</h1>
<p class="mt-6 text-lg font-medium text-[#0b1623]">[ {HEADLINE} ]</p>
<div class="mt-8 flex flex-wrap justify-center gap-3"><a href="#workwithus" class="pill bg-[#0b1623] text-white">{CTA} →</a><a href="#creators" class="pill border border-[#0b1623]/60">{CTA_C}</a></div></div>
<div class="ticker marquee py-6 border-t border-[#0b1623]/20"><div class="marquee-track">{plats}{plats}</div></div></section>
<section id="why" class="px-6 md:px-16 py-24 max-w-[1200px] mx-auto"><p class="text-primary-fixed-dim font-bold tracking-widest text-xs uppercase mb-3 reveal">For brands</p><h2 class="ms text-5xl md:text-7xl mb-14 reveal">Everything between "hello" and "live".</h2><div class="grid md:grid-cols-4 gap-8">{svc}</div></section>
<section class="bg-[#101d2e] px-6 py-20 text-center"><h2 class="ms text-5xl md:text-7xl mb-10 reveal">Where it runs</h2><div class="flex flex-wrap justify-center gap-3 reveal">{"".join(f'<span class="tag text-primary-fixed-dim">{p}</span>' for p in PLATFORMS)}</div></section>
<section class="px-6 md:px-16 py-24 max-w-[1200px] mx-auto grid md:grid-cols-2 gap-14 items-center"><div><p class="text-primary-fixed-dim text-xs font-bold tracking-widest uppercase mb-4 reveal">Our approach</p>
<h2 class="ms text-6xl md:text-8xl reveal">We send 1 to 3 names. <span class="text-accent-container">Not 200.</span></h2><div class="h-1 w-14 bg-accent mt-6"></div></div>
<p class="text-white/65 text-lg reveal">Most creator lists are long spreadsheets that someone still has to check. We check first. Brands get the few creators whose real numbers fit their product, and creators get introduced to brands that fit theirs.</p></section>
<section id="brands" class="relative bg-primary-container text-[#0b1623] px-6 py-24 text-center"><span class="side">For brands</span>
<h2 class="ms text-6xl md:text-9xl max-w-5xl mx-auto reveal">No guessing. Just the right creators.</h2><div class="h-1 w-14 bg-[#0b1623] mx-auto my-6"></div>
<div class="max-w-3xl mx-auto grid md:grid-cols-3 gap-8 text-left my-10">{pr}</div>
<a href="#workwithus" class="pill bg-[#0b1623] text-white">{CTA} →</a></section>
<section id="for-creators" class="relative bg-[#16293d] text-white px-6 py-24 text-center"><span class="side">For creators</span>
<h2 class="ms text-6xl md:text-9xl max-w-5xl mx-auto reveal">Brand deals that <span class="text-accent-container">fit your channel.</span></h2><div class="h-1 w-14 bg-accent mx-auto my-6"></div>
<div class="max-w-3xl mx-auto grid md:grid-cols-2 gap-8 text-left my-10 text-white">{"".join(f'<div class="reveal"><p class="font-bold text-lg">{t}</p><p class="text-white/70">{d}</p></div>' for _ic, t, d in CREATOR_BENEFITS)}</div>
<a href="#creators" class="pill bg-primary-container text-[#0b1623]">{CTA_C} →</a></section>
<section class="px-6 py-24 bg-[#16293d]"><div class="max-w-5xl mx-auto bg-primary-container text-[#0b1623] rounded-[28px] p-8 md:p-14 text-center reveal"><h2 class="ms text-5xl md:text-7xl mb-4">Let's get you matched.</h2><p class="mb-8 opacity-90">{CTA_SUB}</p>{forms('color')}</div></section>
{footer(True)}</div>"""
    page("layout-mindshare.html", "Layout test: MindShare-style | Gratovo", "MindShare-style",
         "Giant type on alternating blue and navy bands. Full-screen wordmark hero with two buttons, platform ticker, For Brands and For Creators bands, rounded closing card.",
         "bg-[#16293d]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;display=swap" rel="stylesheet">')


# ================================================================ 8. SMOOTH
def build_smooth():
    css = """
.serif { font-family: 'Fraunces', Georgia, serif; }
.hero-bg { background: linear-gradient(120deg, #2b1a4d, #0a5c9e, #5b2a86, #16293d); background-size: 300% 300%; animation: drift 16s ease-in-out infinite; }
@keyframes drift { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
.ellipse { fill:none; stroke:#fff; stroke-width:2.5; stroke-dasharray:1; stroke-dashoffset:1; animation: drawline 1.6s 1s ease-out forwards; }
@keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(8px); } }
.phone { width:200px; border:6px solid #2a1745; border-radius:32px; background:#fff; box-shadow:0 20px 40px rgba(42,23,69,.25); overflow:hidden; }
.cloud span { background:#fcfaf6; border-radius:999px; padding:10px 20px; font-weight:700; font-size:.78rem; letter-spacing:.06em; text-transform:uppercase; color:#2a1745; }
"""
    tags = ["AI assistants", "Automation", "Developer tools", "Productivity", "SaaS", "No-code", "AI agents", "Analytics", "Writing tools", "Design tools", "Meeting tools", "Research tools"]
    cloud = "".join(f"<span>{t}</span>" for t in tags)
    phones = "".join(
        f"""<div class="phone reveal" data-delay="{i*120}" style="margin-top:{[0,36,0][i]}px"><div class="bg-gradient-to-br from-[#2a1745] to-[#0a5c9e] h-64 flex flex-col items-center justify-center text-white text-center p-4">{mat('account_circle','text-6xl text-white/80')}<p class="serif text-xl mt-2">{EXAMPLES[i][0]}</p><p class="text-xs text-white/70">{EXAMPLES[i][1]}</p></div>
<div class="p-4 text-[#2a1745]"><p class="text-[10px] uppercase tracking-widest text-[#2a1745]/60 mb-2">Example format</p><div class="flex justify-between text-center"><div><p class="font-bold">{EXAMPLES[i][2]}</p><p class="text-[10px] uppercase">avg views</p></div><div><p class="font-bold">{EXAMPLES[i][3]}</p><p class="text-[10px] uppercase">engage</p></div><div><p class="font-bold">{EXAMPLES[i][4]}</p><p class="text-[10px] uppercase">US</p></div></div></div></div>"""
        for i in range(3))
    steps = "".join(f'<div class="reveal text-center px-4" data-delay="{i*120}"><p class="serif text-6xl text-[#7a4fc0]">{i+1}</p><h3 class="serif text-2xl text-[#2a1745] mt-2 mb-2">{t}</h3><p class="text-[#2a1745]/75">{d}</p></div>' for i, (t, d) in enumerate(STEPS3))
    body = f"""
<div class="bg-[#fcfaf6] text-[#2a1745]">
<section class="hero-bg relative min-h-screen text-white flex flex-col">
<div class="absolute inset-0 bg-[#2a1745]/45"></div>
<header class="relative z-10 flex items-center justify-between px-6 md:px-10 h-24"><a href="#">{wordmark("text-3xl")}</a>
<nav class="flex items-center gap-7 text-sm font-medium"><a class="hidden sm:block" href="#who">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="border border-white rounded-full px-5 py-2">Contact</a></nav></header>
<div class="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 pb-10">
<p class="text-xs font-semibold tracking-[.2em] uppercase mb-6">AI brands and creators, introduced</p>
<h1 class="serif text-5xl md:text-8xl max-w-5xl leading-[1.02]">Connecting AI brands with the <span class="relative inline-block">creators<svg class="absolute -inset-x-3 -inset-y-3 w-[calc(100%+1.5rem)] h-[calc(100%+1.5rem)]" viewBox="0 0 300 100" preserveAspectRatio="none" aria-hidden="true"><ellipse class="ellipse" pathLength="1" cx="150" cy="50" rx="146" ry="44"/></svg></span> their customers trust.</h1>
<p class="mt-8 max-w-xl text-lg text-white/85">{SUB} {BODY}</p>
{hero_buttons("bg-white text-[#2a1745] rounded-full px-9 py-4 font-semibold", "border border-white text-white rounded-full px-9 py-4 font-semibold", "mt-8 flex flex-wrap justify-center gap-3")}
<a href="#who" aria-label="Scroll down" class="mt-10 text-2xl" style="animation: bob 1.8s ease-in-out infinite">↓</a></div></section>
<section id="who" class="bg-[#e6def2] px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">What we send brands.</h2><p class="mb-14 text-[#2a1745]/75 reveal">Each creator, with the numbers that matter. Example formats, not real creators.</p>
<div class="flex flex-wrap justify-center gap-8 mb-20">{phones}</div>
<p class="text-sm tracking-widest uppercase mb-6 reveal">We work with products like:</p><div class="cloud flex flex-wrap justify-center gap-3 max-w-3xl mx-auto reveal">{cloud}</div></section>
<section id="approach" class="px-6 py-24 max-w-5xl mx-auto text-center"><h2 class="serif text-4xl md:text-6xl mb-14 reveal">How it works for <em class="text-[#7a4fc0]">brands</em>.</h2><div class="grid md:grid-cols-3 gap-8">{steps}</div>
<div class="grid sm:grid-cols-3 gap-4 mt-16">{"".join(f'<div class="reveal bg-white rounded-2xl p-6 text-left"><p class="font-bold mb-1">{t}</p><p class="text-sm text-[#2a1745]/70">{d}</p></div>' for _i, t, d in BENEFITS)}</div></section>
<div class="bg-[#e6def2] text-[#2a1745]">{creator_section('light')}</div>
<section class="bg-[#2a1745] text-white px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">Let's get you matched.</h2><p class="text-white/75 mb-10 reveal">{CTA_SUB}</p>{forms('dark')}</section>
{footer(True)}</div>"""
    page("layout-smooth.html", "Layout test: Smooth-style | Gratovo", "Smooth-style",
         "Soft and editorial. Full-screen tinted hero with a hand-drawn ellipse and two buttons, phone-shaped example cards, category pill cloud, For Creators section, serif headings.",
         "bg-[#fcfaf6]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&amp;display=swap" rel="stylesheet">')


# ================================================================ 9. ADHESIVE
def build_adhesive():
    css = """
.hl { color:#0072b8; }
.diagram { height:150px; position:relative; background:#f4f9fe; border-bottom:1px solid #d5e6f4; overflow:hidden; }
.node { position:absolute; background:#fff; border:1px solid #c5d5e4; border-radius:8px; padding:4px 10px; font:11px/1.2 'JetBrains Mono', monospace; text-transform:uppercase; color:#3e4c5e; }
@keyframes pulse2 { 0% { box-shadow:0 0 0 0 rgba(0,114,184,.45); } 100% { box-shadow:0 0 0 22px rgba(0,114,184,0); } }
.pulse { animation: pulse2 2s ease-out infinite; }
.carousel { display:flex; gap:20px; overflow-x:auto; scroll-snap-type:x mandatory; padding-bottom:8px; scrollbar-width:none; }
.carousel::-webkit-scrollbar { display:none; }
.carousel > article { flex:0 0 300px; scroll-snap-align:start; background:#fff; border:1px solid #d5e6f4; border-radius:14px; overflow:hidden; }
.step-tab { padding:10px 16px; border-radius:10px; font-weight:600; color:#3e4c5e; }
.step-tab.is-active { background:#fff; color:#0a5c9e; box-shadow:0 1px 4px rgba(0,0,0,.12); }
"""
    # the animated, tabbed process section is the one on the real homepage (single source of truth)
    idx = (Path(__file__).resolve().parent.parent.parent / "index.html").read_text(encoding="utf-8")
    proc = re.search(r'<section id="how-it-works".*?</section>', idx, re.S).group(0)
    cats = [("AI assistants", "Reach people already learning to get more from AI chat and writing tools."),
            ("Automation", "Show workflow builders how your tool saves them hours, on screen."),
            ("Developer tools", "Put your product in front of developers who watch tutorials before they buy."),
            ("Productivity", "Get walked through in real workflows by creators who use tools like yours daily.")]
    cat_tabs = "".join(f'<button class="step-tab" role="tab">{c}</button>' for c, _ in cats)
    cat_panels = "".join(f'<div class="step-panel" role="tabpanel"><h3 class="sp-h text-3xl mb-3">{c}</h3><p class="text-[#3f403e] max-w-xl">{d}</p></div>' for c, d in cats)
    step_panels = "".join(
        f'<div class="step-panel"><p class="sp-eyebrow mb-2">Step {i+1} of 5</p><h3 class="sp-h text-3xl mb-3">{t}</h3><p class="text-[#3f403e] max-w-xl">{d}</p></div>' for i, (t, d) in enumerate(STEPS5))
    faq = "".join(f'<details class="row"><summary style="grid-template-columns:1fr 24px"><span class="font-headline-md text-xl font-bold">{q}</span><span class="tog">+</span></summary><p style="padding-left:0">{a}</p></details>' for q, a in FAQ)
    body = f"""
<div class="bg-[#f6f9ff] text-[#121212]">
<header class="nav-blur sticky top-0 z-50 border-b border-[#deded8]"><div class="max-w-[80rem] mx-auto px-6 h-[72px] flex items-center justify-between">
<a href="#">{wordmark("text-2xl")}</a>
<nav class="hidden md:flex gap-8 text-sm font-medium"><a href="#services">For brands</a><a href="#for-creators">For creators</a><a href="#process">How it works</a><a href="#faq">Questions</a></nav>
<a href="#workwithus" class="bg-primary-container text-white rounded-2xl px-5 py-3 text-sm font-semibold">{CTA}</a></div></header>
<main>
<section class="relative overflow-hidden"><div class="absolute inset-x-0 bottom-0 h-[55%] pointer-events-none">
<svg viewBox="0 0 760 430" preserveAspectRatio="none" class="w-full h-full" aria-hidden="true"><defs><linearGradient id="ga" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#0072b8" stop-opacity=".25"/><stop offset="1" stop-color="#0072b8" stop-opacity=".02"/></linearGradient></defs>
<path class="growth-area" d="M0 400 L90 385 L170 392 L250 360 L330 366 L410 330 L490 335 L560 230 L640 215 L700 110 L760 40 L760 430 L0 430 Z"/>
<path class="growth-path" pathLength="1" d="M0 400 L90 385 L170 392 L250 360 L330 366 L410 330 L490 335 L560 230 L640 215 L700 110 L760 40"/></svg>
<span class="stage" style="left:24%;bottom:22%;animation-delay:1.2s">Request</span><span class="stage" style="left:42%;bottom:33%;animation-delay:1.8s">Match</span>
<span class="stage" style="left:62%;bottom:50%;animation-delay:2.4s">Agree</span><span class="stage" style="left:82%;bottom:72%;animation-delay:3s">Launch</span></div>
<div class="relative max-w-[80rem] mx-auto px-6 pt-20 pb-72 md:pb-80">
<p class="sp-eyebrow mb-6">AI influencer marketing</p>
<h1 class="sp-h text-5xl md:text-8xl max-w-5xl">{HEAD_PARTS[0]}<span class="text-primary-container">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-6 text-lg text-[#3f403e] max-w-2xl">{SUB} {BODY}</p>
{hero_buttons("bg-primary-container text-white rounded-2xl px-6 py-4 font-semibold", "bg-[#121212] text-white rounded-2xl px-6 py-4 font-semibold", "mt-8 flex flex-wrap gap-3")}</div></section>
<section class="max-w-[80rem] mx-auto px-6 pb-24 grid md:grid-cols-2 gap-5">
<article class="sp-card p-9 reveal"><p class="sp-eyebrow mb-3">The buying journey</p><h3 class="sp-h text-3xl mb-3">People watch before they buy.</h3><p class="text-[#3f403e]">Before trying a new AI tool, people watch tutorials, compare options, and listen to creators they already trust.</p></article>
<article class="sp-card p-9 reveal" data-delay="120"><p class="sp-eyebrow mb-3">Our role</p><h3 class="sp-h text-3xl mb-3">We connect both sides.</h3><p class="text-[#3f403e]">We find the right creator for the brand, and the right brand deal for the creator, and keep the conversation moving between them.</p></article></section>
<section id="services" class="max-w-[80rem] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">For brands</p><h2 class="sp-h text-4xl md:text-6xl">What brands get.</h2></div><div class="max-w-4xl mx-auto border-b border-[#deded8]">{rows}</div></section>
<section class="bg-white py-24"><div class="max-w-[80rem] mx-auto px-6"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">Built for AI</p><h2 class="sp-h text-4xl md:text-6xl">Creator marketing works when the product needs showing.</h2></div>
<div data-stepper class="max-w-4xl mx-auto"><div class="flex justify-center gap-2 overflow-x-auto border-b border-[#deded8]" role="tablist">{cat_tabs}</div>
<div class="sp-card p-10 mt-8 min-h-[190px] relative">{cat_panels}<div class="absolute right-6 top-6 flex flex-col items-center gap-2"><button data-prev aria-label="Previous" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">←</button><span data-count class="text-xs text-[#686867]"></span><button data-next aria-label="Next" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">→</button></div></div></div></div></section>
{creator_section('light')}
<section id="process" class="max-w-[80rem] mx-auto px-6 py-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">How it works for brands</p><h2 class="sp-h text-4xl md:text-6xl">From message to live video.</h2></div>
<div data-stepper class="max-w-4xl mx-auto"><div class="sp-card p-10 min-h-[190px] relative">{step_panels}<div class="absolute right-6 top-6 flex flex-col items-center gap-2"><button data-prev aria-label="Previous step" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">←</button><span data-count class="text-xs text-[#686867]"></span><button data-next aria-label="Next step" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">→</button></div></div></div></section>
<section class="max-w-[80rem] mx-auto px-6 pb-24"><div class="sp-card p-10 md:p-14 grid md:grid-cols-2 gap-8 items-center reveal" style="border-left:4px solid #0072b8;border-top:1px solid #deded8"><div><p class="sp-eyebrow mb-3">Our approach</p><h3 class="sp-h text-4xl">Brands bring the product. Creators bring the audience.</h3></div><p class="text-[#3f403e]">We don't hand brands a spreadsheet of 200 names. We check each creator's real numbers, send the one to three that fit, and keep it simple for creators too.</p></div></section>
<section id="faq" class="max-w-4xl mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">Common questions</p><h2 class="sp-h text-4xl md:text-5xl">What to know before we work together.</h2></div><div class="border-b border-[#deded8]">{faq}</div></section>
<section class="px-6 pb-24"><div class="max-w-5xl mx-auto text-center reveal"><p class="sp-eyebrow mb-3">Let's work together</p><h2 class="sp-h text-4xl md:text-5xl mb-4">Brands and creators, start here.</h2><p class="text-[#3f403e] mb-8">{CTA_SUB}</p>{forms('light')}</div></section>
</main>
<footer class="bg-[#121212] text-white/75 py-14"><div class="max-w-[80rem] mx-auto px-6 grid md:grid-cols-3 gap-8"><div>{wordmark("text-2xl")}<p class="mt-4 text-sm">Connecting AI and SaaS brands with vetted creators, and creators with brand deals that fit.</p></div>
<div><p class="font-label-sm uppercase mb-3 text-white">Explore</p><div class="space-y-2 text-sm"><a class="block" href="#services">For brands</a><a class="block" href="#for-creators">For creators</a><a class="block" href="#faq">Questions</a></div></div>
<div><p class="font-label-sm uppercase mb-3 text-white">Contact</p><p class="text-sm">{EMAIL}</p><p class="text-sm mt-4"><a href="{ASSET}privacy-policy.html">Privacy</a> · <a href="{ASSET}terms-of-service.html">Terms</a></p></div></div>
<p class="max-w-[80rem] mx-auto px-6 mt-10 text-xs text-white/50">© 2026 Gratovo.</p></footer></div>"""
    page("layout-scalepledge.html", "Layout test: Scale Pledge-style | Gratovo", "Scale Pledge-style",
         "Editorial and light. Hero line draws itself with the four stages, accordion services, tabbed carousel, For Creators section, step carousel, FAQ.",
         "bg-[#f6f9ff]", css, body)


# ================================================================ 4. NSENTIVE
def build_nsentive():
    css = """
.dict-line { opacity:0; animation: fadein .9s ease forwards; }
.n-card { border:1px solid rgba(255,255,255,.55); border-radius:28px; padding:26px 26px 40px; }
.n-row { border-top:1px solid #3a3a3a; display:grid; grid-template-columns: 1fr 1.4fr 60px; gap:24px; padding:34px 0; align-items:start; }
@media (max-width: 768px) { .n-row { grid-template-columns: 1fr; gap: 10px; padding: 24px 0; } .n-row > span { display: none; } }
.loop { height: 340px; overflow: hidden; -webkit-mask-image: linear-gradient(transparent, #000 25%, #000 75%, transparent); mask-image: linear-gradient(transparent, #000 25%, #000 75%, transparent); }
.loop-track { animation: scrollup 14s linear infinite; }
.loop-track span { display:block; text-align:center; font-size:1.7rem; line-height:3.1rem; color:#fff; }
.loop-track span:nth-child(3n+2) { font-family: Georgia, serif; font-style: italic; }
"""
    cards = "".join(
        f'<div class="n-card reveal" data-delay="{i*100}"><div class="mb-14 text-white">{mat(ic, "text-3xl", False)}</div><h3 class="text-2xl font-semibold text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>'
        for i, (ic, t, d) in enumerate(BENEFITS))
    w = [("WHO", "Brands and creators in AI and SaaS: marketing managers and founders who want creators promoting their product, and creators who want brand deals that fit."),
         ("WHAT", "Brands get 1 to 3 vetted AI creators picked for their product. Creators get put forward to brands that fit their audience."),
         ("WHY", "People watching AI tutorials are looking for tools to try. A trusted creator showing a product reaches them at that moment."),
         ("WHERE", "YouTube, LinkedIn, X, and newsletters, wherever the right creator's audience is."),
         ("HOW", "Tell us about your product or your channel. We make the introduction. We take care of contracts, scripts, and posting."),
         ("WHEN", "We reply within 24 hours. Most deals go live within about a month.")]
    rows = "".join(f'<div class="n-row reveal"><h3 class="text-5xl md:text-6xl font-semibold text-[#161616]">{a}</h3><p class="text-[#555] text-lg">{c}</p><span class="text-3xl text-[#161616]">↘</span></div>' for a, c in w)
    who = [("Marketing managers", "Hand off the searching, vetting, and chasing. Keep the final say."),
           ("Founders", "Get your product in front of the right audience without learning creator marketing first."),
           ("Creators", "Get brand deals that fit your channel, without cold outreach or endless email threads.")]
    whorows = "".join(f'<div class="n-row reveal"><h3 class="text-4xl md:text-5xl font-semibold text-[#161616]">{a}</h3><p class="text-[#555] text-lg">{b}</p><span class="text-3xl text-[#161616]">↘</span></div>' for a, b in who)
    flow = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="text-white/40 text-sm mb-3">0{i+1}</p><h3 class="text-4xl font-semibold text-white mb-3">{t}</h3><p class="text-white/70">{d}</p></div>' for i, (t, d) in enumerate(STEPS4))
    loop_items = "".join(f"<span>{x}</span>" for x in ["no cold emails", "no chasing replies", "no guessing who's legit", "no endless threads", "just the right match"] * 2)
    body = f"""
<div class="bg-black text-white">
<header class="max-w-[1280px] mx-auto px-6 h-24 flex items-center justify-between"><a href="#">{wordmark("text-4xl")}</a><a href="#workwithus" class="bg-primary-container text-white rounded-full px-8 py-3 font-medium">Let's Talk</a></header>
<main>
<section class="text-center px-6 pt-16 pb-24">
<h1 class="dict-line text-6xl md:text-8xl font-semibold tracking-tight" style="animation-delay:.2s">match</h1>
<p class="dict-line text-3xl md:text-4xl text-white/35 mt-3" style="animation-delay:.9s">/mætʃ/</p>
<p class="dict-line text-3xl md:text-4xl font-semibold mt-1" style="animation-delay:1.5s">noun</p>
<p class="dict-line text-xl md:text-2xl mt-8 max-w-2xl mx-auto text-white/90" style="animation-delay:2.1s">A creator whose audience fits your product. A brand deal that fits your channel. We find both.</p>
{hero_buttons("bg-white text-black rounded-full px-10 py-4 font-semibold", "border border-white text-white rounded-full px-10 py-4 font-semibold", "dict-line mt-10 flex flex-wrap justify-center gap-4\" style=\"animation-delay:2.7s")}</section>
<section class="max-w-[1280px] mx-auto px-6 pb-28 grid md:grid-cols-3 gap-6">{cards}</section>
<div class="bg-white text-[#161616]"><div class="max-w-[1280px] mx-auto px-6 py-24">
<h2 class="text-5xl md:text-7xl font-semibold tracking-tight mb-14 reveal">The short version.</h2><div class="border-b border-[#3a3a3a]">{rows}</div></div>
<div class="max-w-[1280px] mx-auto px-6 pb-24"><h2 class="text-5xl md:text-7xl font-semibold tracking-tight mb-14 reveal">Who it's for.</h2><div class="border-b border-[#3a3a3a]">{whorows}</div></div></div>
{creator_section('dark')}
<section class="max-w-[1280px] mx-auto px-6 py-28"><h2 class="text-5xl md:text-7xl font-semibold tracking-tight text-center mb-16 reveal">Four steps for brands.</h2><div class="grid md:grid-cols-4 gap-10">{flow}</div></section>
<section class="bg-primary-container px-6 py-24"><div class="max-w-[1200px] mx-auto grid md:grid-cols-[1fr_2.4fr] gap-10 items-center">
<div class="loop hidden md:block"><div class="loop-track">{loop_items}</div></div>
<div class="bg-black rounded-[28px] p-8 md:p-10"><h2 class="text-center text-3xl font-semibold mb-2">Let's Talk</h2><p class="text-center text-white/70 mb-6">{CTA_SUB}</p>{forms('dark')}</div></div></section>
</main>{footer(True)}</div>"""
    page("layout-nsentive.html", "Layout test: Nsentive-style | Gratovo", "Nsentive-style",
         "Black to white to brand blue. Dictionary-style hero that fades in line by line, outlined cards, ruled rows (brands, creators), scrolling word list beside the forms.",
         "bg-black", css, body)


# ================================================================ 5. APOLLO
def build_apollo():
    css = """
@keyframes twinkle { 0%,100% { opacity:.15; } 50% { opacity:.9; } }
@keyframes shoot { 0% { transform: translate(0,0) rotate(-35deg); opacity:0; } 8% { opacity:1; } 30% { transform: translate(-420px,300px) rotate(-35deg); opacity:0; } 100% { opacity:0; } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes counter { to { transform: rotate(-360deg); } }
.shoot { position:absolute; top:8%; right:12%; width:120px; height:2px; background:linear-gradient(90deg, rgba(255,255,255,0), #fff); animation: shoot 7s 2s infinite; }
.glass { background: linear-gradient(160deg, rgba(255,255,255,.08), rgba(255,255,255,.02)); border:1px solid rgba(255,255,255,.12); border-radius:28px; backdrop-filter: blur(10px); }
.grad-text { background: linear-gradient(90deg, #ffd9a8, #ff8fb3, #b88cff); -webkit-background-clip:text; background-clip:text; color:transparent; }
.chip { position:absolute; background: rgba(20,30,70,.9); border:1px solid rgba(255,255,255,.18); border-radius:16px; padding:10px 14px; font-size:13px; color:#fff; animation: floaty 6s ease-in-out infinite; box-shadow:0 10px 30px rgba(0,0,0,.4); }
.orbit { position:relative; width:260px; height:260px; margin:auto; }
.orbit .ring { position:absolute; inset:0; border:1px dashed rgba(255,255,255,.25); border-radius:50%; animation: spin 24s linear infinite; }
.orbit .ring i { position:absolute; width:52px; height:52px; margin:-26px; border-radius:16px; background:#fff; color:#16293d; display:flex; align-items:center; justify-content:center; animation: counter 24s linear infinite; }
.orbit .core { position:absolute; inset:88px; border-radius:24px; background: linear-gradient(135deg,#0a5c9e,#6a54e8); display:flex; align-items:center; justify-content:center; box-shadow:0 0 50px rgba(106,84,232,.6); }
.ghost { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size: clamp(120px, 24vw, 340px); font-weight:800; color: rgba(255,255,255,.05); pointer-events:none; letter-spacing:-.04em; }
.beam { height:1px; background: linear-gradient(90deg, transparent, rgba(150,130,255,.8), transparent); background-size:200% 100%; animation: shimmer 4s linear infinite; }
@keyframes shimmer { to { background-position: -200% 0; } }
"""
    blocks = [("It's that easy.", "Send us a short message. We do the searching, vetting, and chasing."),
              ("Peace of mind.", "Every creator is checked for real views, engagement, and audience location first."),
              ("Your product, shown properly.", "Creators demo your tool in a real workflow, for an audience that wants to try it."),
              ("Nothing goes live unseen.", "You approve the video before it posts.")]
    bl = "".join(f'<div class="glass p-8 reveal" data-delay="{i*100}"><h3 class="font-headline-md text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>' for i, (t, d) in enumerate(blocks))
    stats = "".join(f'<div class="text-center"><p class="text-5xl font-bold text-white">{v}</p><p class="text-white/65 mt-2 max-w-[200px] mx-auto">{l}</p></div>' for v, l in STATS[:3])
    steps = "".join(f'<div class="glass p-7 reveal" data-delay="{i*90}"><span class="grad-text text-4xl font-bold">0{i+1}</span><h3 class="font-headline-md text-white mt-3 mb-2">{t}</h3><p class="text-white/70 text-sm">{d}</p></div>' for i, (t, d) in enumerate(STEPS5))
    plat_icons = ["smart_display", "work", "tag", "mail"]
    orbit_items = "".join(
        f'<i style="left:{50 + 50*math.cos(a)}%;top:{50 + 50*math.sin(a)}%">{mat(ic, "text-2xl", True)}</i>'
        for ic, a in zip(plat_icons, [0, 1.5708, 3.1416, 4.7124]))
    pill = "inline-block border border-white/25 bg-white/10 rounded-full px-7 py-3 text-sm font-semibold"
    body = f"""
<div class="bg-[#050a1f] text-white relative overflow-hidden">
<div id="stars" class="absolute inset-0 pointer-events-none"></div><div class="shoot"></div>
<header class="relative z-20 max-w-[1280px] mx-auto px-6 h-20 flex items-center justify-between"><a href="#">{wordmark("text-3xl")}</a>
<nav class="hidden md:flex gap-1 border border-white/15 rounded-full px-2 py-2 text-sm bg-white/5"><a class="px-4 py-1.5 rounded-full bg-white/10" href="#">Home</a><a class="px-4 py-1.5" href="#brands">For brands</a><a class="px-4 py-1.5" href="#for-creators">For creators</a><a class="px-4 py-1.5" href="#process">How it works</a></nav>
<a href="#workwithus" class="border border-white/25 bg-white/5 rounded-lg px-5 py-2 text-sm">Contact</a></header>
<main class="relative z-10">
<section class="text-center px-6 pt-14 pb-12"><h1 class="font-display-lg text-4xl md:text-7xl max-w-5xl mx-auto leading-[1.05]">{HEAD_PARTS[0]}<span class="grad-text">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-5 text-white/70 text-lg max-w-2xl mx-auto">{SUB}</p></section>
<section class="max-w-[1280px] mx-auto px-6 grid md:grid-cols-2 gap-6 pb-24">
<div id="brands" class="glass p-8 md:p-10 text-center relative overflow-hidden min-h-[470px] reveal"><h2 class="font-display-lg text-4xl mb-3">for brands.</h2><p class="text-white/70 mb-6">1 to 3 vetted AI creators picked for your product.</p>
<a href="#workwithus" class="{pill}">{CTA}</a>
<div class="relative h-56 mt-6"><div class="chip" style="left:6%;top:6%;--r:-6deg">Creator A · 42K avg views</div><div class="chip" style="left:34%;top:38%;--r:4deg;animation-delay:1s">Creator B · 5.1% engagement</div><div class="chip" style="left:12%;top:70%;--r:-3deg;animation-delay:2s">Creator C · 46% US audience</div></div>
<p class="absolute bottom-3 inset-x-0 text-[11px] text-white/45 uppercase tracking-wider">Example format</p></div>
<div class="glass p-8 md:p-10 text-center min-h-[470px] reveal" data-delay="120"><h2 class="font-display-lg text-4xl mb-3">for creators.</h2><p class="text-white/70 mb-6">Brand deals that fit your channel. YouTube, LinkedIn, X, and newsletters.</p>
<a href="#creators" class="{pill}">{CTA_C}</a>
<div class="orbit mt-8"><div class="core">{mat('rocket_launch', 'text-4xl text-white')}</div><div class="ring">{orbit_items}</div></div></div></section>
<section class="max-w-[1280px] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><span class="inline-block border border-white/20 rounded-full px-4 py-1 text-sm mb-4">What brands get ✦</span><h2 class="font-display-lg text-4xl md:text-6xl">A simpler way to work with AI creators.</h2></div><div class="grid md:grid-cols-2 gap-5">{bl}</div></section>
<section class="relative max-w-[1100px] mx-auto px-6 py-24"><div class="ghost" aria-hidden="true">1-3</div><div class="relative"><div class="beam mb-12"></div><div class="grid md:grid-cols-3 gap-10">{stats}</div><div class="beam mt-12"></div></div><p class="relative text-center text-white/60 mt-8">Every creator we recommend passes these checks first.</p></section>
{creator_section('dark')}
<section id="process" class="max-w-[1280px] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><h2 class="font-display-lg text-4xl md:text-6xl">How a deal works with us.</h2></div><div class="grid md:grid-cols-5 gap-4">{steps}</div></section>
<section class="max-w-[1100px] mx-auto px-6 pb-24"><div class="glass p-8 md:p-14 text-center reveal"><h2 class="font-display-lg text-4xl md:text-6xl mb-3">Ready for <span class="grad-text">take-off?</span></h2><p class="text-white/70 mb-10">{CTA_SUB}</p>{forms('dark')}</div></section>
</main>{footer(True)}</div>"""
    page("layout-apollo.html", "Layout test: Apollo-style | Gratovo", "Apollo-style",
         "Dark space theme. Twinkling stars and a shooting star, a glass card for brands and one for creators, floating chips, orbiting platform icons, ghost number behind the stats.",
         "bg-[#050a1f]", css, body)


# ================================================================ 6. RIGHT CLICK
def build_rightclick():
    css = """
.display { font-family: 'Anton', 'Plus Jakarta Sans', sans-serif; text-transform: uppercase; letter-spacing: .01em; line-height: .95; }
.mono { font-family: 'JetBrains Mono', monospace; }
.rc-cap { color:#9ad6f7; }
.rc-btn { border:1px solid #9ad6f7; color:#9ad6f7; border-radius:999px; padding:18px 28px; font-size:1.6rem; display:flex; justify-content:space-between; align-items:center; transition:.25s; }
.rc-btn:hover { background:#9ad6f7; color:#050a14; }
.rc-btn:hover span { color:#050a14 !important; }
.fcard { position:absolute; width:150px; border-radius:18px; padding:14px; color:#fff; box-shadow:0 14px 40px rgba(0,0,0,.5); animation: floaty 7s ease-in-out infinite; }
#scroll-progress-wrap { position:fixed; left:10px; top:90px; bottom:40px; width:3px; z-index:50; }
#scroll-progress { width:3px; background:#9ad6f7; height:0; }
"""
    cards = [("30K+", "avg views", "left:2%;top:6%;--r:-8deg;background:linear-gradient(135deg,#6a54e8,#b8286e)", 0),
             ("3-8%", "engagement", "right:3%;top:2%;--r:6deg;background:linear-gradient(135deg,#0a5c9e,#0072b8)", 1.2),
             ("35%+", "target audience", "left:6%;top:48%;--r:5deg;background:linear-gradient(135deg,#b8286e,#ff7a59)", 2.2),
             ("1-3", "creators, not 200", "right:2%;top:42%;--r:-5deg;background:linear-gradient(135deg,#0072b8,#1fb6a6)", 3.2)]
    fc = "".join(f'<div class="fcard hidden md:block" style="{st};animation-delay:{d}s"><p class="display text-4xl">{v}</p><p class="text-xs uppercase tracking-wider opacity-90">{l}</p></div>' for v, l, st, d in cards)
    pills = [("BRANDS", "Vetted AI creators for your product.", "#workwithus"),
             ("CREATORS", "Brand deals that fit your channel.", "#creators"),
             ("HOW IT WORKS", "Four steps, from message to live video.", "#process")]
    pl = "".join(f'<a href="{h}" class="rc-btn reveal mono" data-delay="{i*100}"><span>{a}</span><span class="text-base text-white/70 max-w-md text-right hidden md:block">{b}</span><span>↗</span></a>' for i, (a, b, h) in enumerate(pills))
    ex = "".join(example_card(i) for i in range(3))
    steps = "".join(f'<div class="reveal border-l border-[#9ad6f7]/50 pl-5" data-delay="{i*100}"><p class="display text-4xl rc-cap">0{i+1}</p><h3 class="mono text-lg font-semibold mt-2">{t}</h3><p class="mono text-white/70 text-sm mt-1">{d}</p></div>' for i, (t, d) in enumerate(STEPS4))
    hb = hero_buttons("bg-[#9ad6f7] text-[#050a14] font-bold rounded-full px-8 py-4", "border border-[#9ad6f7] text-[#9ad6f7] font-bold rounded-full px-8 py-4", "mt-8 flex flex-wrap justify-center gap-4")
    body = f"""
<div class="bg-[#050a14] text-white mono">
<div id="scroll-progress-wrap" aria-hidden="true"><div id="scroll-progress"></div></div>
<header class="relative z-20 flex items-center justify-between px-6 md:px-12 h-24"><span class="mono text-xs rc-cap hidden md:block"><span id="scroll-progress-num">0</span> / 100</span>
<a href="#" class="md:absolute md:left-1/2 md:-translate-x-1/2">{wordmark("text-3xl")}</a><a href="#workwithus" class="ml-auto bg-white/10 rc-cap rounded-full px-5 py-2 text-xs tracking-widest">WORK WITH US</a></header>
<main>
<section class="relative min-h-[88vh] flex flex-col items-center justify-center text-center px-6 overflow-hidden">{fc}
<h1 class="display rc-cap text-[clamp(3rem,10vw,8.5rem)] max-w-6xl relative z-10">{HEADLINE}</h1>
<p class="relative z-10 mt-6 max-w-xl text-white/80">{SUB}</p><div class="relative z-10">{hb}</div></section>
<section class="max-w-5xl mx-auto px-6 pb-24"><div class="border border-[#9ad6f7] rounded-[32px] p-10 md:p-14 text-center reveal"><p class="text-xl leading-relaxed">We're <b class="rc-cap">Gratovo</b>. We connect AI brands with vetted creators, and creators with brand deals that fit. {BODY}</p></div></section>
<section class="max-w-5xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-10 reveal">Who we work with</h2><div class="space-y-5">{pl}</div></section>
<section class="max-w-6xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-3 reveal">What we send brands</h2><p class="text-white/70 mb-10 reveal">Hover a card. Example formats, not real creators.</p><div class="grid sm:grid-cols-3 gap-5 reveal">{ex}</div></section>
{creator_section('dark', head_cls='display')}
<section id="process" class="max-w-6xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-12 reveal">Four steps for brands</h2><div class="grid md:grid-cols-4 gap-8">{steps}</div></section>
<section class="max-w-5xl mx-auto px-6 pb-28 text-center"><h2 class="display rc-cap text-6xl md:text-8xl mb-6 reveal">Ready to get started?</h2><p class="text-white/70 mb-10">{CTA_SUB}</p>{forms('dark')}</section>
</main>{footer(True)}</div>"""
    page("layout-rightclick.html", "Layout test: Right Click-style | Gratovo", "Right Click-style",
         "Bold and edgy. Giant condensed headline with floating stat cards and two buttons, scroll progress counter on the left edge, outlined pill rows (brands, creators), big closing line.",
         "bg-[#050a14]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;display=swap" rel="stylesheet">')


# ================================================================ 7. MINDSHARE
def build_mindshare():
    css = """
.ms { font-family: 'Anton', 'Plus Jakarta Sans', sans-serif; text-transform: uppercase; letter-spacing: -.01em; line-height: .92; }
.pill { border-radius:999px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; font-size:.8rem; padding:18px 30px; display:inline-flex; gap:8px; align-items:center; }
.tag { border:1px solid currentColor; border-radius:999px; padding:6px 14px; font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.side { position:absolute; left:18px; top:40px; writing-mode:vertical-rl; transform:rotate(180deg); font-size:.7rem; letter-spacing:.25em; opacity:.6; text-transform:uppercase; }
@keyframes ticker { to { transform: translateX(-50%); } }
.ticker .marquee-track { animation: ticker 22s linear infinite; }
"""
    plats = "".join(f'<span class="ms text-4xl md:text-5xl text-[#16293d]/80">{p}</span>' for p in PLATFORMS * 3)
    svc = "".join(f'<div class="reveal border-t border-white/20 pt-6" data-delay="{i*90}"><p class="text-primary-fixed-dim text-xs font-bold tracking-widest mb-2">0{i+1}</p><h3 class="ms text-3xl mb-2">{t}</h3><p class="text-white/65">{d}</p></div>' for i, (t, d) in enumerate(SERVICES[:4]))
    props = [("Zero outreach", "We contact the creators. You only hear about the ones worth your time."),
             ("Real numbers", "Views, engagement, and audience location, checked before you see a name."),
             ("You approve it", "Nothing goes live until you've seen the video.")]
    pr = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="font-bold text-lg">{a}</p><p class="text-[#0b1623]/90">{b}</p></div>' for i, (a, b) in enumerate(props))
    cprops = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="font-bold text-lg">{t}</p><p class="text-[#0b1623]/90">{d}</p></div>' for i, (_ic, t, d) in enumerate(CREATOR_BENEFITS))
    body = f"""
<div class="bg-[#16293d] text-white">
<section class="relative bg-primary-container text-[#0b1623] min-h-screen flex flex-col">
<header class="flex items-center justify-between px-6 md:px-10 h-20"><a href="#" class="bg-white rounded-xl px-3 py-1">{wordmark("text-2xl")}</a>
<nav class="flex items-center gap-6 text-xs tracking-widest uppercase font-semibold"><a class="hidden sm:block" href="#brands">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="bg-[#0b1623] text-white rounded-full px-5 py-2">Contact</a></nav></header>
<div class="flex-1 flex flex-col items-center justify-center text-center px-6"><h1 class="ms text-[clamp(4.5rem,17vw,15rem)] text-[#0b1623]">Gratovo</h1>
<p class="mt-6 text-lg font-medium text-[#0b1623]">[ {HEADLINE} ]</p>
<div class="mt-8 flex flex-wrap justify-center gap-3"><a href="#workwithus" class="pill bg-[#0b1623] text-white">{CTA} →</a><a href="#creators" class="pill border border-[#0b1623]/60">{CTA_C}</a></div></div>
<div class="ticker marquee py-6 border-t border-[#0b1623]/20"><div class="marquee-track">{plats}{plats}</div></div></section>
<section id="why" class="px-6 md:px-16 py-24 max-w-[1200px] mx-auto"><p class="text-primary-fixed-dim font-bold tracking-widest text-xs uppercase mb-3 reveal">For brands</p><h2 class="ms text-5xl md:text-7xl mb-14 reveal">Everything between "hello" and "live".</h2><div class="grid md:grid-cols-4 gap-8">{svc}</div></section>
<section class="bg-[#101d2e] px-6 py-20 text-center"><h2 class="ms text-5xl md:text-7xl mb-10 reveal">Where it runs</h2><div class="flex flex-wrap justify-center gap-3 reveal">{"".join(f'<span class="tag text-primary-fixed-dim">{p}</span>' for p in PLATFORMS)}</div></section>
<section class="px-6 md:px-16 py-24 max-w-[1200px] mx-auto grid md:grid-cols-2 gap-14 items-center"><div><p class="text-primary-fixed-dim text-xs font-bold tracking-widest uppercase mb-4 reveal">Our approach</p>
<h2 class="ms text-6xl md:text-8xl reveal">We send 1 to 3 names. <span class="text-accent-container">Not 200.</span></h2><div class="h-1 w-14 bg-accent mt-6"></div></div>
<p class="text-white/65 text-lg reveal">Most creator lists are long spreadsheets that someone still has to check. We check first. Brands get the few creators whose real numbers fit their product, and creators get introduced to brands that fit theirs.</p></section>
<section id="brands" class="relative bg-primary-container text-[#0b1623] px-6 py-24 text-center"><span class="side">For brands</span>
<h2 class="ms text-6xl md:text-9xl max-w-5xl mx-auto reveal">No guessing. Just the right creators.</h2><div class="h-1 w-14 bg-[#0b1623] mx-auto my-6"></div>
<div class="max-w-3xl mx-auto grid md:grid-cols-3 gap-8 text-left my-10">{pr}</div>
<a href="#workwithus" class="pill bg-[#0b1623] text-white">{CTA} →</a></section>
<section id="for-creators" class="relative bg-[#16293d] text-white px-6 py-24 text-center"><span class="side">For creators</span>
<h2 class="ms text-6xl md:text-9xl max-w-5xl mx-auto reveal">Brand deals that <span class="text-accent-container">fit your channel.</span></h2><div class="h-1 w-14 bg-accent mx-auto my-6"></div>
<div class="max-w-3xl mx-auto grid md:grid-cols-2 gap-8 text-left my-10 text-white">{"".join(f'<div class="reveal"><p class="font-bold text-lg">{t}</p><p class="text-white/70">{d}</p></div>' for _ic, t, d in CREATOR_BENEFITS)}</div>
<a href="#creators" class="pill bg-primary-container text-[#0b1623]">{CTA_C} →</a></section>
<section class="px-6 py-24 bg-[#16293d]"><div class="max-w-5xl mx-auto bg-primary-container text-[#0b1623] rounded-[28px] p-8 md:p-14 text-center reveal"><h2 class="ms text-5xl md:text-7xl mb-4">Let's get you matched.</h2><p class="mb-8 opacity-90">{CTA_SUB}</p>{forms('color')}</div></section>
{footer(True)}</div>"""
    page("layout-mindshare.html", "Layout test: MindShare-style | Gratovo", "MindShare-style",
         "Giant type on alternating blue and navy bands. Full-screen wordmark hero with two buttons, platform ticker, For Brands and For Creators bands, rounded closing card.",
         "bg-[#16293d]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;display=swap" rel="stylesheet">')


# ================================================================ 8. SMOOTH
def build_smooth():
    css = """
.serif { font-family: 'Fraunces', Georgia, serif; }
.hero-bg { background: linear-gradient(120deg, #2b1a4d, #0a5c9e, #5b2a86, #16293d); background-size: 300% 300%; animation: drift 16s ease-in-out infinite; }
@keyframes drift { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
.ellipse { fill:none; stroke:#fff; stroke-width:2.5; stroke-dasharray:1; stroke-dashoffset:1; animation: drawline 1.6s 1s ease-out forwards; }
@keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(8px); } }
.phone { width:200px; border:6px solid #2a1745; border-radius:32px; background:#fff; box-shadow:0 20px 40px rgba(42,23,69,.25); overflow:hidden; }
.cloud span { background:#fcfaf6; border-radius:999px; padding:10px 20px; font-weight:700; font-size:.78rem; letter-spacing:.06em; text-transform:uppercase; color:#2a1745; }
"""
    tags = ["AI assistants", "Automation", "Developer tools", "Productivity", "SaaS", "No-code", "AI agents", "Analytics", "Writing tools", "Design tools", "Meeting tools", "Research tools"]
    cloud = "".join(f"<span>{t}</span>" for t in tags)
    phones = "".join(
        f"""<div class="phone reveal" data-delay="{i*120}" style="margin-top:{[0,36,0][i]}px"><div class="bg-gradient-to-br from-[#2a1745] to-[#0a5c9e] h-64 flex flex-col items-center justify-center text-white text-center p-4">{mat('account_circle','text-6xl text-white/80')}<p class="serif text-xl mt-2">{EXAMPLES[i][0]}</p><p class="text-xs text-white/70">{EXAMPLES[i][1]}</p></div>
<div class="p-4 text-[#2a1745]"><p class="text-[10px] uppercase tracking-widest text-[#2a1745]/60 mb-2">Example format</p><div class="flex justify-between text-center"><div><p class="font-bold">{EXAMPLES[i][2]}</p><p class="text-[10px] uppercase">avg views</p></div><div><p class="font-bold">{EXAMPLES[i][3]}</p><p class="text-[10px] uppercase">engage</p></div><div><p class="font-bold">{EXAMPLES[i][4]}</p><p class="text-[10px] uppercase">US</p></div></div></div></div>"""
        for i in range(3))
    steps = "".join(f'<div class="reveal text-center px-4" data-delay="{i*120}"><p class="serif text-6xl text-[#7a4fc0]">{i+1}</p><h3 class="serif text-2xl text-[#2a1745] mt-2 mb-2">{t}</h3><p class="text-[#2a1745]/75">{d}</p></div>' for i, (t, d) in enumerate(STEPS3))
    body = f"""
<div class="bg-[#fcfaf6] text-[#2a1745]">
<section class="hero-bg relative min-h-screen text-white flex flex-col">
<div class="absolute inset-0 bg-[#2a1745]/45"></div>
<header class="relative z-10 flex items-center justify-between px-6 md:px-10 h-24"><a href="#">{wordmark("text-3xl")}</a>
<nav class="flex items-center gap-7 text-sm font-medium"><a class="hidden sm:block" href="#who">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="border border-white rounded-full px-5 py-2">Contact</a></nav></header>
<div class="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 pb-10">
<p class="text-xs font-semibold tracking-[.2em] uppercase mb-6">AI brands and creators, introduced</p>
<h1 class="serif text-5xl md:text-8xl max-w-5xl leading-[1.02]">Connecting AI brands with the <span class="relative inline-block">creators<svg class="absolute -inset-x-3 -inset-y-3 w-[calc(100%+1.5rem)] h-[calc(100%+1.5rem)]" viewBox="0 0 300 100" preserveAspectRatio="none" aria-hidden="true"><ellipse class="ellipse" pathLength="1" cx="150" cy="50" rx="146" ry="44"/></svg></span> their customers trust.</h1>
<p class="mt-8 max-w-xl text-lg text-white/85">{SUB} {BODY}</p>
{hero_buttons("bg-white text-[#2a1745] rounded-full px-9 py-4 font-semibold", "border border-white text-white rounded-full px-9 py-4 font-semibold", "mt-8 flex flex-wrap justify-center gap-3")}
<a href="#who" aria-label="Scroll down" class="mt-10 text-2xl" style="animation: bob 1.8s ease-in-out infinite">↓</a></div></section>
<section id="who" class="bg-[#e6def2] px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">What we send brands.</h2><p class="mb-14 text-[#2a1745]/75 reveal">Each creator, with the numbers that matter. Example formats, not real creators.</p>
<div class="flex flex-wrap justify-center gap-8 mb-20">{phones}</div>
<p class="text-sm tracking-widest uppercase mb-6 reveal">We work with products like:</p><div class="cloud flex flex-wrap justify-center gap-3 max-w-3xl mx-auto reveal">{cloud}</div></section>
<section id="approach" class="px-6 py-24 max-w-5xl mx-auto text-center"><h2 class="serif text-4xl md:text-6xl mb-14 reveal">How it works for <em class="text-[#7a4fc0]">brands</em>.</h2><div class="grid md:grid-cols-3 gap-8">{steps}</div>
<div class="grid sm:grid-cols-3 gap-4 mt-16">{"".join(f'<div class="reveal bg-white rounded-2xl p-6 text-left"><p class="font-bold mb-1">{t}</p><p class="text-sm text-[#2a1745]/70">{d}</p></div>' for _i, t, d in BENEFITS)}</div></section>
<div class="bg-[#e6def2] text-[#2a1745]">{creator_section('light')}</div>
<section class="bg-[#2a1745] text-white px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">Let's get you matched.</h2><p class="text-white/75 mb-10 reveal">{CTA_SUB}</p>{forms('dark')}</section>
{footer(True)}</div>"""
    page("layout-smooth.html", "Layout test: Smooth-style | Gratovo", "Smooth-style",
         "Soft and editorial. Full-screen tinted hero with a hand-drawn ellipse and two buttons, phone-shaped example cards, category pill cloud, For Creators section, serif headings.",
         "bg-[#fcfaf6]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&amp;display=swap" rel="stylesheet">')


# ================================================================ 9. ADHESIVE
def build_adhesive():
    css = """
.hl { color:#0072b8; }
.step-tab { padding:12px 16px; border-bottom:3px solid transparent; font-weight:600; color:#686867; white-space:nowrap; }
.step-tab.is-active { color:#121212; border-color:#0072b8; }
.nav-blur { backdrop-filter: blur(10px); background: rgba(246,249,255,.85); }
"""
    rows = "".join(
        f'<details class="row"><summary><span class="sp-eyebrow">0{i+1}</span><span class="font-headline-md text-2xl font-bold">{t}</span><span class="hidden md:block text-secondary text-sm">Included</span><span class="tog">+</span></summary><p>{d}</p></details>'
        for i, (t, d) in enumerate(SERVICES))
    cats = [("AI assistants", "Reach people already learning to get more from AI chat and writing tools."),
            ("Automation", "Show workflow builders how your tool saves them hours, on screen."),
            ("Developer tools", "Put your product in front of developers who watch tutorials before they buy."),
            ("Productivity", "Get walked through in real workflows by creators who use tools like yours daily.")]
    cat_tabs = "".join(f'<button class="step-tab" role="tab">{c}</button>' for c, _ in cats)
    cat_panels = "".join(f'<div class="step-panel" role="tabpanel"><h3 class="sp-h text-3xl mb-3">{c}</h3><p class="text-[#3f403e] max-w-xl">{d}</p></div>' for c, d in cats)
    step_panels = "".join(
        f'<div class="step-panel"><p class="sp-eyebrow mb-2">Step {i+1} of 5</p><h3 class="sp-h text-3xl mb-3">{t}</h3><p class="text-[#3f403e] max-w-xl">{d}</p></div>' for i, (t, d) in enumerate(STEPS5))
    faq = "".join(f'<details class="row"><summary style="grid-template-columns:1fr 24px"><span class="font-headline-md text-xl font-bold">{q}</span><span class="tog">+</span></summary><p style="padding-left:0">{a}</p></details>' for q, a in FAQ)
    body = f"""
<div class="bg-[#f6f9ff] text-[#121212]">
<header class="nav-blur sticky top-0 z-50 border-b border-[#deded8]"><div class="max-w-[80rem] mx-auto px-6 h-[72px] flex items-center justify-between">
<a href="#">{wordmark("text-2xl")}</a>
<nav class="hidden md:flex gap-8 text-sm font-medium"><a href="#services">For brands</a><a href="#for-creators">For creators</a><a href="#process">How it works</a><a href="#faq">Questions</a></nav>
<a href="#workwithus" class="bg-primary-container text-white rounded-2xl px-5 py-3 text-sm font-semibold">{CTA}</a></div></header>
<main>
<section class="relative overflow-hidden"><div class="absolute inset-x-0 bottom-0 h-[55%] pointer-events-none">
<svg viewBox="0 0 760 430" preserveAspectRatio="none" class="w-full h-full" aria-hidden="true"><defs><linearGradient id="ga" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#0072b8" stop-opacity=".25"/><stop offset="1" stop-color="#0072b8" stop-opacity=".02"/></linearGradient></defs>
<path class="growth-area" d="M0 400 L90 385 L170 392 L250 360 L330 366 L410 330 L490 335 L560 230 L640 215 L700 110 L760 40 L760 430 L0 430 Z"/>
<path class="growth-path" pathLength="1" d="M0 400 L90 385 L170 392 L250 360 L330 366 L410 330 L490 335 L560 230 L640 215 L700 110 L760 40"/></svg>
<span class="stage" style="left:24%;bottom:22%;animation-delay:1.2s">Request</span><span class="stage" style="left:42%;bottom:33%;animation-delay:1.8s">Match</span>
<span class="stage" style="left:62%;bottom:50%;animation-delay:2.4s">Agree</span><span class="stage" style="left:82%;bottom:72%;animation-delay:3s">Launch</span></div>
<div class="relative max-w-[80rem] mx-auto px-6 pt-20 pb-72 md:pb-80">
<p class="sp-eyebrow mb-6">AI influencer marketing</p>
<h1 class="sp-h text-5xl md:text-8xl max-w-5xl">{HEAD_PARTS[0]}<span class="text-primary-container">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-6 text-lg text-[#3f403e] max-w-2xl">{SUB} {BODY}</p>
{hero_buttons("bg-primary-container text-white rounded-2xl px-6 py-4 font-semibold", "bg-[#121212] text-white rounded-2xl px-6 py-4 font-semibold", "mt-8 flex flex-wrap gap-3")}</div></section>
<section class="max-w-[80rem] mx-auto px-6 pb-24 grid md:grid-cols-2 gap-5">
<article class="sp-card p-9 reveal"><p class="sp-eyebrow mb-3">The buying journey</p><h3 class="sp-h text-3xl mb-3">People watch before they buy.</h3><p class="text-[#3f403e]">Before trying a new AI tool, people watch tutorials, compare options, and listen to creators they already trust.</p></article>
<article class="sp-card p-9 reveal" data-delay="120"><p class="sp-eyebrow mb-3">Our role</p><h3 class="sp-h text-3xl mb-3">We connect both sides.</h3><p class="text-[#3f403e]">We find the right creator for the brand, and the right brand deal for the creator, and keep the conversation moving between them.</p></article></section>
<section id="services" class="max-w-[80rem] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">For brands</p><h2 class="sp-h text-4xl md:text-6xl">What brands get.</h2></div><div class="max-w-4xl mx-auto border-b border-[#deded8]">{rows}</div></section>
<section class="bg-white py-24"><div class="max-w-[80rem] mx-auto px-6"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">Built for AI</p><h2 class="sp-h text-4xl md:text-6xl">Creator marketing works when the product needs showing.</h2></div>
<div data-stepper class="max-w-4xl mx-auto"><div class="flex justify-center gap-2 overflow-x-auto border-b border-[#deded8]" role="tablist">{cat_tabs}</div>
<div class="sp-card p-10 mt-8 min-h-[190px] relative">{cat_panels}<div class="absolute right-6 top-6 flex flex-col items-center gap-2"><button data-prev aria-label="Previous" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">←</button><span data-count class="text-xs text-[#686867]"></span><button data-next aria-label="Next" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">→</button></div></div></div></div></section>
{creator_section('light')}
<section id="process" class="max-w-[80rem] mx-auto px-6 py-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">How it works for brands</p><h2 class="sp-h text-4xl md:text-6xl">From message to live video.</h2></div>
<div data-stepper class="max-w-4xl mx-auto"><div class="sp-card p-10 min-h-[190px] relative">{step_panels}<div class="absolute right-6 top-6 flex flex-col items-center gap-2"><button data-prev aria-label="Previous step" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">←</button><span data-count class="text-xs text-[#686867]"></span><button data-next aria-label="Next step" class="w-10 h-10 rounded-full border border-primary-container text-primary-container">→</button></div></div></div></section>
<section class="max-w-[80rem] mx-auto px-6 pb-24"><div class="sp-card p-10 md:p-14 grid md:grid-cols-2 gap-8 items-center reveal" style="border-left:4px solid #0072b8;border-top:1px solid #deded8"><div><p class="sp-eyebrow mb-3">Our approach</p><h3 class="sp-h text-4xl">Brands bring the product. Creators bring the audience.</h3></div><p class="text-[#3f403e]">We don't hand brands a spreadsheet of 200 names. We check each creator's real numbers, send the one to three that fit, and keep it simple for creators too.</p></div></section>
<section id="faq" class="max-w-4xl mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><p class="sp-eyebrow mb-3">Common questions</p><h2 class="sp-h text-4xl md:text-5xl">What to know before we work together.</h2></div><div class="border-b border-[#deded8]">{faq}</div></section>
<section class="px-6 pb-24"><div class="max-w-5xl mx-auto text-center reveal"><p class="sp-eyebrow mb-3">Let's work together</p><h2 class="sp-h text-4xl md:text-5xl mb-4">Brands and creators, start here.</h2><p class="text-[#3f403e] mb-8">{CTA_SUB}</p>{forms('light')}</div></section>
</main>
<footer class="bg-[#121212] text-white/75 py-14"><div class="max-w-[80rem] mx-auto px-6 grid md:grid-cols-3 gap-8"><div>{wordmark("text-2xl")}<p class="mt-4 text-sm">Connecting AI and SaaS brands with vetted creators, and creators with brand deals that fit.</p></div>
<div><p class="font-label-sm uppercase mb-3 text-white">Explore</p><div class="space-y-2 text-sm"><a class="block" href="#services">For brands</a><a class="block" href="#for-creators">For creators</a><a class="block" href="#faq">Questions</a></div></div>
<div><p class="font-label-sm uppercase mb-3 text-white">Contact</p><p class="text-sm">{EMAIL}</p><p class="text-sm mt-4"><a href="{ASSET}privacy-policy.html">Privacy</a> · <a href="{ASSET}terms-of-service.html">Terms</a></p></div></div>
<p class="max-w-[80rem] mx-auto px-6 mt-10 text-xs text-white/50">© 2026 Gratovo.</p></footer></div>"""
    page("layout-scalepledge.html", "Layout test: Scale Pledge-style | Gratovo", "Scale Pledge-style",
         "Editorial and light. Hero line draws itself with the four stages, accordion services, tabbed carousel, For Creators section, step carousel, FAQ.",
         "bg-[#f6f9ff]", css, body)


# ================================================================ 4. NSENTIVE
def build_nsentive():
    css = """
.dict-line { opacity:0; animation: fadein .9s ease forwards; }
.n-card { border:1px solid rgba(255,255,255,.55); border-radius:28px; padding:26px 26px 40px; }
.n-row { border-top:1px solid #3a3a3a; display:grid; grid-template-columns: 1fr 1.4fr 60px; gap:24px; padding:34px 0; align-items:start; }
@media (max-width: 768px) { .n-row { grid-template-columns: 1fr; gap: 10px; padding: 24px 0; } .n-row > span { display: none; } }
.loop { height: 340px; overflow: hidden; -webkit-mask-image: linear-gradient(transparent, #000 25%, #000 75%, transparent); mask-image: linear-gradient(transparent, #000 25%, #000 75%, transparent); }
.loop-track { animation: scrollup 14s linear infinite; }
.loop-track span { display:block; text-align:center; font-size:1.7rem; line-height:3.1rem; color:#fff; }
.loop-track span:nth-child(3n+2) { font-family: Georgia, serif; font-style: italic; }
"""
    cards = "".join(
        f'<div class="n-card reveal" data-delay="{i*100}"><div class="mb-14 text-white">{mat(ic, "text-3xl", False)}</div><h3 class="text-2xl font-semibold text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>'
        for i, (ic, t, d) in enumerate(BENEFITS))
    w = [("WHO", "Brands and creators in AI and SaaS: marketing managers and founders who want creators promoting their product, and creators who want brand deals that fit."),
         ("WHAT", "Brands get 1 to 3 vetted AI creators picked for their product. Creators get put forward to brands that fit their audience."),
         ("WHY", "People watching AI tutorials are looking for tools to try. A trusted creator showing a product reaches them at that moment."),
         ("WHERE", "YouTube, LinkedIn, X, and newsletters, wherever the right creator's audience is."),
         ("HOW", "Tell us about your product or your channel. We make the introduction. We take care of contracts, scripts, and posting."),
         ("WHEN", "We reply within 24 hours. Most deals go live within about a month.")]
    rows = "".join(f'<div class="n-row reveal"><h3 class="text-5xl md:text-6xl font-semibold text-[#161616]">{a}</h3><p class="text-[#555] text-lg">{c}</p><span class="text-3xl text-[#161616]">↘</span></div>' for a, c in w)
    who = [("Marketing managers", "Hand off the searching, vetting, and chasing. Keep the final say."),
           ("Founders", "Get your product in front of the right audience without learning creator marketing first."),
           ("Creators", "Get brand deals that fit your channel, without cold outreach or endless email threads.")]
    whorows = "".join(f'<div class="n-row reveal"><h3 class="text-4xl md:text-5xl font-semibold text-[#161616]">{a}</h3><p class="text-[#555] text-lg">{b}</p><span class="text-3xl text-[#161616]">↘</span></div>' for a, b in who)
    flow = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="text-white/40 text-sm mb-3">0{i+1}</p><h3 class="text-4xl font-semibold text-white mb-3">{t}</h3><p class="text-white/70">{d}</p></div>' for i, (t, d) in enumerate(STEPS4))
    loop_items = "".join(f"<span>{x}</span>" for x in ["no cold emails", "no chasing replies", "no guessing who's legit", "no endless threads", "just the right match"] * 2)
    body = f"""
<div class="bg-black text-white">
<header class="max-w-[1280px] mx-auto px-6 h-24 flex items-center justify-between"><a href="#">{wordmark("text-4xl")}</a><a href="#workwithus" class="bg-primary-container text-white rounded-full px-8 py-3 font-medium">Let's Talk</a></header>
<main>
<section class="text-center px-6 pt-16 pb-24">
<h1 class="dict-line text-6xl md:text-8xl font-semibold tracking-tight" style="animation-delay:.2s">match</h1>
<p class="dict-line text-3xl md:text-4xl text-white/35 mt-3" style="animation-delay:.9s">/mætʃ/</p>
<p class="dict-line text-3xl md:text-4xl font-semibold mt-1" style="animation-delay:1.5s">noun</p>
<p class="dict-line text-xl md:text-2xl mt-8 max-w-2xl mx-auto text-white/90" style="animation-delay:2.1s">A creator whose audience fits your product. A brand deal that fits your channel. We find both.</p>
{hero_buttons("bg-white text-black rounded-full px-10 py-4 font-semibold", "border border-white text-white rounded-full px-10 py-4 font-semibold", "dict-line mt-10 flex flex-wrap justify-center gap-4\" style=\"animation-delay:2.7s")}</section>
<section class="max-w-[1280px] mx-auto px-6 pb-28 grid md:grid-cols-3 gap-6">{cards}</section>
<div class="bg-white text-[#161616]"><div class="max-w-[1280px] mx-auto px-6 py-24">
<h2 class="text-5xl md:text-7xl font-semibold tracking-tight mb-14 reveal">The short version.</h2><div class="border-b border-[#3a3a3a]">{rows}</div></div>
<div class="max-w-[1280px] mx-auto px-6 pb-24"><h2 class="text-5xl md:text-7xl font-semibold tracking-tight mb-14 reveal">Who it's for.</h2><div class="border-b border-[#3a3a3a]">{whorows}</div></div></div>
{creator_section('dark')}
<section class="max-w-[1280px] mx-auto px-6 py-28"><h2 class="text-5xl md:text-7xl font-semibold tracking-tight text-center mb-16 reveal">Four steps for brands.</h2><div class="grid md:grid-cols-4 gap-10">{flow}</div></section>
<section class="bg-primary-container px-6 py-24"><div class="max-w-[1200px] mx-auto grid md:grid-cols-[1fr_2.4fr] gap-10 items-center">
<div class="loop hidden md:block"><div class="loop-track">{loop_items}</div></div>
<div class="bg-black rounded-[28px] p-8 md:p-10"><h2 class="text-center text-3xl font-semibold mb-2">Let's Talk</h2><p class="text-center text-white/70 mb-6">{CTA_SUB}</p>{forms('dark')}</div></div></section>
</main>{footer(True)}</div>"""
    page("layout-nsentive.html", "Layout test: Nsentive-style | Gratovo", "Nsentive-style",
         "Black to white to brand blue. Dictionary-style hero that fades in line by line, outlined cards, ruled rows (brands, creators), scrolling word list beside the forms.",
         "bg-black", css, body)


# ================================================================ 5. APOLLO
def build_apollo():
    css = """
@keyframes twinkle { 0%,100% { opacity:.15; } 50% { opacity:.9; } }
@keyframes shoot { 0% { transform: translate(0,0) rotate(-35deg); opacity:0; } 8% { opacity:1; } 30% { transform: translate(-420px,300px) rotate(-35deg); opacity:0; } 100% { opacity:0; } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes counter { to { transform: rotate(-360deg); } }
.shoot { position:absolute; top:8%; right:12%; width:120px; height:2px; background:linear-gradient(90deg, rgba(255,255,255,0), #fff); animation: shoot 7s 2s infinite; }
.glass { background: linear-gradient(160deg, rgba(255,255,255,.08), rgba(255,255,255,.02)); border:1px solid rgba(255,255,255,.12); border-radius:28px; backdrop-filter: blur(10px); }
.grad-text { background: linear-gradient(90deg, #ffd9a8, #ff8fb3, #b88cff); -webkit-background-clip:text; background-clip:text; color:transparent; }
.chip { position:absolute; background: rgba(20,30,70,.9); border:1px solid rgba(255,255,255,.18); border-radius:16px; padding:10px 14px; font-size:13px; color:#fff; animation: floaty 6s ease-in-out infinite; box-shadow:0 10px 30px rgba(0,0,0,.4); }
.orbit { position:relative; width:260px; height:260px; margin:auto; }
.orbit .ring { position:absolute; inset:0; border:1px dashed rgba(255,255,255,.25); border-radius:50%; animation: spin 24s linear infinite; }
.orbit .ring i { position:absolute; width:52px; height:52px; margin:-26px; border-radius:16px; background:#fff; color:#16293d; display:flex; align-items:center; justify-content:center; animation: counter 24s linear infinite; }
.orbit .core { position:absolute; inset:88px; border-radius:24px; background: linear-gradient(135deg,#0a5c9e,#6a54e8); display:flex; align-items:center; justify-content:center; box-shadow:0 0 50px rgba(106,84,232,.6); }
.ghost { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size: clamp(120px, 24vw, 340px); font-weight:800; color: rgba(255,255,255,.05); pointer-events:none; letter-spacing:-.04em; }
.beam { height:1px; background: linear-gradient(90deg, transparent, rgba(150,130,255,.8), transparent); background-size:200% 100%; animation: shimmer 4s linear infinite; }
@keyframes shimmer { to { background-position: -200% 0; } }
"""
    blocks = [("It's that easy.", "Send us a short message. We do the searching, vetting, and chasing."),
              ("Peace of mind.", "Every creator is checked for real views, engagement, and audience location first."),
              ("Your product, shown properly.", "Creators demo your tool in a real workflow, for an audience that wants to try it."),
              ("Nothing goes live unseen.", "You approve the video before it posts.")]
    bl = "".join(f'<div class="glass p-8 reveal" data-delay="{i*100}"><h3 class="font-headline-md text-white mb-2">{t}</h3><p class="text-white/70">{d}</p></div>' for i, (t, d) in enumerate(blocks))
    stats = "".join(f'<div class="text-center"><p class="text-5xl font-bold text-white">{v}</p><p class="text-white/65 mt-2 max-w-[200px] mx-auto">{l}</p></div>' for v, l in STATS[:3])
    steps = "".join(f'<div class="glass p-7 reveal" data-delay="{i*90}"><span class="grad-text text-4xl font-bold">0{i+1}</span><h3 class="font-headline-md text-white mt-3 mb-2">{t}</h3><p class="text-white/70 text-sm">{d}</p></div>' for i, (t, d) in enumerate(STEPS5))
    plat_icons = ["smart_display", "work", "tag", "mail"]
    orbit_items = "".join(
        f'<i style="left:{50 + 50*math.cos(a)}%;top:{50 + 50*math.sin(a)}%">{mat(ic, "text-2xl", True)}</i>'
        for ic, a in zip(plat_icons, [0, 1.5708, 3.1416, 4.7124]))
    pill = "inline-block border border-white/25 bg-white/10 rounded-full px-7 py-3 text-sm font-semibold"
    body = f"""
<div class="bg-[#050a1f] text-white relative overflow-hidden">
<div id="stars" class="absolute inset-0 pointer-events-none"></div><div class="shoot"></div>
<header class="relative z-20 max-w-[1280px] mx-auto px-6 h-20 flex items-center justify-between"><a href="#">{wordmark("text-3xl")}</a>
<nav class="hidden md:flex gap-1 border border-white/15 rounded-full px-2 py-2 text-sm bg-white/5"><a class="px-4 py-1.5 rounded-full bg-white/10" href="#">Home</a><a class="px-4 py-1.5" href="#brands">For brands</a><a class="px-4 py-1.5" href="#for-creators">For creators</a><a class="px-4 py-1.5" href="#process">How it works</a></nav>
<a href="#workwithus" class="border border-white/25 bg-white/5 rounded-lg px-5 py-2 text-sm">Contact</a></header>
<main class="relative z-10">
<section class="text-center px-6 pt-14 pb-12"><h1 class="font-display-lg text-4xl md:text-7xl max-w-5xl mx-auto leading-[1.05]">{HEAD_PARTS[0]}<span class="grad-text">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-5 text-white/70 text-lg max-w-2xl mx-auto">{SUB}</p></section>
<section class="max-w-[1280px] mx-auto px-6 grid md:grid-cols-2 gap-6 pb-24">
<div id="brands" class="glass p-8 md:p-10 text-center relative overflow-hidden min-h-[470px] reveal"><h2 class="font-display-lg text-4xl mb-3">for brands.</h2><p class="text-white/70 mb-6">1 to 3 vetted AI creators picked for your product.</p>
<a href="#workwithus" class="{pill}">{CTA}</a>
<div class="relative h-56 mt-6"><div class="chip" style="left:6%;top:6%;--r:-6deg">Creator A · 42K avg views</div><div class="chip" style="left:34%;top:38%;--r:4deg;animation-delay:1s">Creator B · 5.1% engagement</div><div class="chip" style="left:12%;top:70%;--r:-3deg;animation-delay:2s">Creator C · 46% US audience</div></div>
<p class="absolute bottom-3 inset-x-0 text-[11px] text-white/45 uppercase tracking-wider">Example format</p></div>
<div class="glass p-8 md:p-10 text-center min-h-[470px] reveal" data-delay="120"><h2 class="font-display-lg text-4xl mb-3">for creators.</h2><p class="text-white/70 mb-6">Brand deals that fit your channel. YouTube, LinkedIn, X, and newsletters.</p>
<a href="#creators" class="{pill}">{CTA_C}</a>
<div class="orbit mt-8"><div class="core">{mat('rocket_launch', 'text-4xl text-white')}</div><div class="ring">{orbit_items}</div></div></div></section>
<section class="max-w-[1280px] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><span class="inline-block border border-white/20 rounded-full px-4 py-1 text-sm mb-4">What brands get ✦</span><h2 class="font-display-lg text-4xl md:text-6xl">A simpler way to work with AI creators.</h2></div><div class="grid md:grid-cols-2 gap-5">{bl}</div></section>
<section class="relative max-w-[1100px] mx-auto px-6 py-24"><div class="ghost" aria-hidden="true">1-3</div><div class="relative"><div class="beam mb-12"></div><div class="grid md:grid-cols-3 gap-10">{stats}</div><div class="beam mt-12"></div></div><p class="relative text-center text-white/60 mt-8">Every creator we recommend passes these checks first.</p></section>
{creator_section('dark')}
<section id="process" class="max-w-[1280px] mx-auto px-6 pb-24"><div class="text-center mb-10 reveal"><h2 class="font-display-lg text-4xl md:text-6xl">How a deal works with us.</h2></div><div class="grid md:grid-cols-5 gap-4">{steps}</div></section>
<section class="max-w-[1100px] mx-auto px-6 pb-24"><div class="glass p-8 md:p-14 text-center reveal"><h2 class="font-display-lg text-4xl md:text-6xl mb-3">Ready for <span class="grad-text">take-off?</span></h2><p class="text-white/70 mb-10">{CTA_SUB}</p>{forms('dark')}</div></section>
</main>{footer(True)}</div>"""
    page("layout-apollo.html", "Layout test: Apollo-style | Gratovo", "Apollo-style",
         "Dark space theme. Twinkling stars and a shooting star, a glass card for brands and one for creators, floating chips, orbiting platform icons, ghost number behind the stats.",
         "bg-[#050a1f]", css, body)


# ================================================================ 6. RIGHT CLICK
def build_rightclick():
    css = """
.display { font-family: 'Anton', 'Plus Jakarta Sans', sans-serif; text-transform: uppercase; letter-spacing: .01em; line-height: .95; }
.mono { font-family: 'JetBrains Mono', monospace; }
.rc-cap { color:#9ad6f7; }
.rc-btn { border:1px solid #9ad6f7; color:#9ad6f7; border-radius:999px; padding:18px 28px; font-size:1.6rem; display:flex; justify-content:space-between; align-items:center; transition:.25s; }
.rc-btn:hover { background:#9ad6f7; color:#050a14; }
.rc-btn:hover span { color:#050a14 !important; }
.fcard { position:absolute; width:150px; border-radius:18px; padding:14px; color:#fff; box-shadow:0 14px 40px rgba(0,0,0,.5); animation: floaty 7s ease-in-out infinite; }
#scroll-progress-wrap { position:fixed; left:10px; top:90px; bottom:40px; width:3px; z-index:50; }
#scroll-progress { width:3px; background:#9ad6f7; height:0; }
"""
    cards = [("30K+", "avg views", "left:2%;top:6%;--r:-8deg;background:linear-gradient(135deg,#6a54e8,#b8286e)", 0),
             ("3-8%", "engagement", "right:3%;top:2%;--r:6deg;background:linear-gradient(135deg,#0a5c9e,#0072b8)", 1.2),
             ("35%+", "target audience", "left:6%;top:48%;--r:5deg;background:linear-gradient(135deg,#b8286e,#ff7a59)", 2.2),
             ("1-3", "creators, not 200", "right:2%;top:42%;--r:-5deg;background:linear-gradient(135deg,#0072b8,#1fb6a6)", 3.2)]
    fc = "".join(f'<div class="fcard hidden md:block" style="{st};animation-delay:{d}s"><p class="display text-4xl">{v}</p><p class="text-xs uppercase tracking-wider opacity-90">{l}</p></div>' for v, l, st, d in cards)
    pills = [("BRANDS", "Vetted AI creators for your product.", "#workwithus"),
             ("CREATORS", "Brand deals that fit your channel.", "#creators"),
             ("HOW IT WORKS", "Four steps, from message to live video.", "#process")]
    pl = "".join(f'<a href="{h}" class="rc-btn reveal mono" data-delay="{i*100}"><span>{a}</span><span class="text-base text-white/70 max-w-md text-right hidden md:block">{b}</span><span>↗</span></a>' for i, (a, b, h) in enumerate(pills))
    ex = "".join(example_card(i) for i in range(3))
    steps = "".join(f'<div class="reveal border-l border-[#9ad6f7]/50 pl-5" data-delay="{i*100}"><p class="display text-4xl rc-cap">0{i+1}</p><h3 class="mono text-lg font-semibold mt-2">{t}</h3><p class="mono text-white/70 text-sm mt-1">{d}</p></div>' for i, (t, d) in enumerate(STEPS4))
    hb = hero_buttons("bg-[#9ad6f7] text-[#050a14] font-bold rounded-full px-8 py-4", "border border-[#9ad6f7] text-[#9ad6f7] font-bold rounded-full px-8 py-4", "mt-8 flex flex-wrap justify-center gap-4")
    body = f"""
<div class="bg-[#050a14] text-white mono">
<div id="scroll-progress-wrap" aria-hidden="true"><div id="scroll-progress"></div></div>
<header class="relative z-20 flex items-center justify-between px-6 md:px-12 h-24"><span class="mono text-xs rc-cap hidden md:block"><span id="scroll-progress-num">0</span> / 100</span>
<a href="#" class="md:absolute md:left-1/2 md:-translate-x-1/2">{wordmark("text-3xl")}</a><a href="#workwithus" class="ml-auto bg-white/10 rc-cap rounded-full px-5 py-2 text-xs tracking-widest">WORK WITH US</a></header>
<main>
<section class="relative min-h-[88vh] flex flex-col items-center justify-center text-center px-6 overflow-hidden">{fc}
<h1 class="display rc-cap text-[clamp(3rem,10vw,8.5rem)] max-w-6xl relative z-10">{HEADLINE}</h1>
<p class="relative z-10 mt-6 max-w-xl text-white/80">{SUB}</p><div class="relative z-10">{hb}</div></section>
<section class="max-w-5xl mx-auto px-6 pb-24"><div class="border border-[#9ad6f7] rounded-[32px] p-10 md:p-14 text-center reveal"><p class="text-xl leading-relaxed">We're <b class="rc-cap">Gratovo</b>. We connect AI brands with vetted creators, and creators with brand deals that fit. {BODY}</p></div></section>
<section class="max-w-5xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-10 reveal">Who we work with</h2><div class="space-y-5">{pl}</div></section>
<section class="max-w-6xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-3 reveal">What we send brands</h2><p class="text-white/70 mb-10 reveal">Hover a card. Example formats, not real creators.</p><div class="grid sm:grid-cols-3 gap-5 reveal">{ex}</div></section>
{creator_section('dark', head_cls='display')}
<section id="process" class="max-w-6xl mx-auto px-6 pb-24"><h2 class="display rc-cap text-5xl md:text-7xl mb-12 reveal">Four steps for brands</h2><div class="grid md:grid-cols-4 gap-8">{steps}</div></section>
<section class="max-w-5xl mx-auto px-6 pb-28 text-center"><h2 class="display rc-cap text-6xl md:text-8xl mb-6 reveal">Ready to get started?</h2><p class="text-white/70 mb-10">{CTA_SUB}</p>{forms('dark')}</section>
</main>{footer(True)}</div>"""
    page("layout-rightclick.html", "Layout test: Right Click-style | Gratovo", "Right Click-style",
         "Bold and edgy. Giant condensed headline with floating stat cards and two buttons, scroll progress counter on the left edge, outlined pill rows (brands, creators), big closing line.",
         "bg-[#050a14]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;display=swap" rel="stylesheet">')


# ================================================================ 7. MINDSHARE
def build_mindshare():
    css = """
.ms { font-family: 'Anton', 'Plus Jakarta Sans', sans-serif; text-transform: uppercase; letter-spacing: -.01em; line-height: .92; }
.pill { border-radius:999px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; font-size:.8rem; padding:18px 30px; display:inline-flex; gap:8px; align-items:center; }
.tag { border:1px solid currentColor; border-radius:999px; padding:6px 14px; font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.side { position:absolute; left:18px; top:40px; writing-mode:vertical-rl; transform:rotate(180deg); font-size:.7rem; letter-spacing:.25em; opacity:.6; text-transform:uppercase; }
@keyframes ticker { to { transform: translateX(-50%); } }
.ticker .marquee-track { animation: ticker 22s linear infinite; }
"""
    plats = "".join(f'<span class="ms text-4xl md:text-5xl text-[#16293d]/80">{p}</span>' for p in PLATFORMS * 3)
    svc = "".join(f'<div class="reveal border-t border-white/20 pt-6" data-delay="{i*90}"><p class="text-primary-fixed-dim text-xs font-bold tracking-widest mb-2">0{i+1}</p><h3 class="ms text-3xl mb-2">{t}</h3><p class="text-white/65">{d}</p></div>' for i, (t, d) in enumerate(SERVICES[:4]))
    props = [("Zero outreach", "We contact the creators. You only hear about the ones worth your time."),
             ("Real numbers", "Views, engagement, and audience location, checked before you see a name."),
             ("You approve it", "Nothing goes live until you've seen the video.")]
    pr = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="font-bold text-lg">{a}</p><p class="text-[#0b1623]/90">{b}</p></div>' for i, (a, b) in enumerate(props))
    cprops = "".join(f'<div class="reveal" data-delay="{i*100}"><p class="font-bold text-lg">{t}</p><p class="text-[#0b1623]/90">{d}</p></div>' for i, (_ic, t, d) in enumerate(CREATOR_BENEFITS))
    body = f"""
<div class="bg-[#16293d] text-white">
<section class="relative bg-primary-container text-[#0b1623] min-h-screen flex flex-col">
<header class="flex items-center justify-between px-6 md:px-10 h-20"><a href="#" class="bg-white rounded-xl px-3 py-1">{wordmark("text-2xl")}</a>
<nav class="flex items-center gap-6 text-xs tracking-widest uppercase font-semibold"><a class="hidden sm:block" href="#brands">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="bg-[#0b1623] text-white rounded-full px-5 py-2">Contact</a></nav></header>
<div class="flex-1 flex flex-col items-center justify-center text-center px-6"><h1 class="ms text-[clamp(4.5rem,17vw,15rem)] text-[#0b1623]">Gratovo</h1>
<p class="mt-6 text-lg font-medium text-[#0b1623]">[ {HEADLINE} ]</p>
<div class="mt-8 flex flex-wrap justify-center gap-3"><a href="#workwithus" class="pill bg-[#0b1623] text-white">{CTA} →</a><a href="#creators" class="pill border border-[#0b1623]/60">{CTA_C}</a></div></div>
<div class="ticker marquee py-6 border-t border-[#0b1623]/20"><div class="marquee-track">{plats}{plats}</div></div></section>
<section id="why" class="px-6 md:px-16 py-24 max-w-[1200px] mx-auto"><p class="text-primary-fixed-dim font-bold tracking-widest text-xs uppercase mb-3 reveal">For brands</p><h2 class="ms text-5xl md:text-7xl mb-14 reveal">Everything between "hello" and "live".</h2><div class="grid md:grid-cols-4 gap-8">{svc}</div></section>
<section class="bg-[#101d2e] px-6 py-20 text-center"><h2 class="ms text-5xl md:text-7xl mb-10 reveal">Where it runs</h2><div class="flex flex-wrap justify-center gap-3 reveal">{"".join(f'<span class="tag text-primary-fixed-dim">{p}</span>' for p in PLATFORMS)}</div></section>
<section class="px-6 md:px-16 py-24 max-w-[1200px] mx-auto grid md:grid-cols-2 gap-14 items-center"><div><p class="text-primary-fixed-dim text-xs font-bold tracking-widest uppercase mb-4 reveal">Our approach</p>
<h2 class="ms text-6xl md:text-8xl reveal">We send 1 to 3 names. <span class="text-accent-container">Not 200.</span></h2><div class="h-1 w-14 bg-accent mt-6"></div></div>
<p class="text-white/65 text-lg reveal">Most creator lists are long spreadsheets that someone still has to check. We check first. Brands get the few creators whose real numbers fit their product, and creators get introduced to brands that fit theirs.</p></section>
<section id="brands" class="relative bg-primary-container text-[#0b1623] px-6 py-24 text-center"><span class="side">For brands</span>
<h2 class="ms text-6xl md:text-9xl max-w-5xl mx-auto reveal">No guessing. Just the right creators.</h2><div class="h-1 w-14 bg-[#0b1623] mx-auto my-6"></div>
<div class="max-w-3xl mx-auto grid md:grid-cols-3 gap-8 text-left my-10">{pr}</div>
<a href="#workwithus" class="pill bg-[#0b1623] text-white">{CTA} →</a></section>
<section id="for-creators" class="relative bg-[#16293d] text-white px-6 py-24 text-center"><span class="side">For creators</span>
<h2 class="ms text-6xl md:text-9xl max-w-5xl mx-auto reveal">Brand deals that <span class="text-accent-container">fit your channel.</span></h2><div class="h-1 w-14 bg-accent mx-auto my-6"></div>
<div class="max-w-3xl mx-auto grid md:grid-cols-2 gap-8 text-left my-10 text-white">{"".join(f'<div class="reveal"><p class="font-bold text-lg">{t}</p><p class="text-white/70">{d}</p></div>' for _ic, t, d in CREATOR_BENEFITS)}</div>
<a href="#creators" class="pill bg-primary-container text-[#0b1623]">{CTA_C} →</a></section>
<section class="px-6 py-24 bg-[#16293d]"><div class="max-w-5xl mx-auto bg-primary-container text-[#0b1623] rounded-[28px] p-8 md:p-14 text-center reveal"><h2 class="ms text-5xl md:text-7xl mb-4">Let's get you matched.</h2><p class="mb-8 opacity-90">{CTA_SUB}</p>{forms('color')}</div></section>
{footer(True)}</div>"""
    page("layout-mindshare.html", "Layout test: MindShare-style | Gratovo", "MindShare-style",
         "Giant type on alternating blue and navy bands. Full-screen wordmark hero with two buttons, platform ticker, For Brands and For Creators bands, rounded closing card.",
         "bg-[#16293d]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Anton&amp;display=swap" rel="stylesheet">')


# ================================================================ 8. SMOOTH
def build_smooth():
    css = """
.serif { font-family: 'Fraunces', Georgia, serif; }
.hero-bg { background: linear-gradient(120deg, #2b1a4d, #0a5c9e, #5b2a86, #16293d); background-size: 300% 300%; animation: drift 16s ease-in-out infinite; }
@keyframes drift { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
.ellipse { fill:none; stroke:#fff; stroke-width:2.5; stroke-dasharray:1; stroke-dashoffset:1; animation: drawline 1.6s 1s ease-out forwards; }
@keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(8px); } }
.phone { width:200px; border:6px solid #2a1745; border-radius:32px; background:#fff; box-shadow:0 20px 40px rgba(42,23,69,.25); overflow:hidden; }
.cloud span { background:#fcfaf6; border-radius:999px; padding:10px 20px; font-weight:700; font-size:.78rem; letter-spacing:.06em; text-transform:uppercase; color:#2a1745; }
"""
    tags = ["AI assistants", "Automation", "Developer tools", "Productivity", "SaaS", "No-code", "AI agents", "Analytics", "Writing tools", "Design tools", "Meeting tools", "Research tools"]
    cloud = "".join(f"<span>{t}</span>" for t in tags)
    phones = "".join(
        f"""<div class="phone reveal" data-delay="{i*120}" style="margin-top:{[0,36,0][i]}px"><div class="bg-gradient-to-br from-[#2a1745] to-[#0a5c9e] h-64 flex flex-col items-center justify-center text-white text-center p-4">{mat('account_circle','text-6xl text-white/80')}<p class="serif text-xl mt-2">{EXAMPLES[i][0]}</p><p class="text-xs text-white/70">{EXAMPLES[i][1]}</p></div>
<div class="p-4 text-[#2a1745]"><p class="text-[10px] uppercase tracking-widest text-[#2a1745]/60 mb-2">Example format</p><div class="flex justify-between text-center"><div><p class="font-bold">{EXAMPLES[i][2]}</p><p class="text-[10px] uppercase">avg views</p></div><div><p class="font-bold">{EXAMPLES[i][3]}</p><p class="text-[10px] uppercase">engage</p></div><div><p class="font-bold">{EXAMPLES[i][4]}</p><p class="text-[10px] uppercase">US</p></div></div></div></div>"""
        for i in range(3))
    steps = "".join(f'<div class="reveal text-center px-4" data-delay="{i*120}"><p class="serif text-6xl text-[#7a4fc0]">{i+1}</p><h3 class="serif text-2xl text-[#2a1745] mt-2 mb-2">{t}</h3><p class="text-[#2a1745]/75">{d}</p></div>' for i, (t, d) in enumerate(STEPS3))
    body = f"""
<div class="bg-[#fcfaf6] text-[#2a1745]">
<section class="hero-bg relative min-h-screen text-white flex flex-col">
<div class="absolute inset-0 bg-[#2a1745]/45"></div>
<header class="relative z-10 flex items-center justify-between px-6 md:px-10 h-24"><a href="#">{wordmark("text-3xl")}</a>
<nav class="flex items-center gap-7 text-sm font-medium"><a class="hidden sm:block" href="#who">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="border border-white rounded-full px-5 py-2">Contact</a></nav></header>
<div class="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 pb-10">
<p class="text-xs font-semibold tracking-[.2em] uppercase mb-6">AI brands and creators, introduced</p>
<h1 class="serif text-5xl md:text-8xl max-w-5xl leading-[1.02]">Connecting AI brands with the <span class="relative inline-block">creators<svg class="absolute -inset-x-3 -inset-y-3 w-[calc(100%+1.5rem)] h-[calc(100%+1.5rem)]" viewBox="0 0 300 100" preserveAspectRatio="none" aria-hidden="true"><ellipse class="ellipse" pathLength="1" cx="150" cy="50" rx="146" ry="44"/></svg></span> their customers trust.</h1>
<p class="mt-8 max-w-xl text-lg text-white/85">{SUB} {BODY}</p>
{hero_buttons("bg-white text-[#2a1745] rounded-full px-9 py-4 font-semibold", "border border-white text-white rounded-full px-9 py-4 font-semibold", "mt-8 flex flex-wrap justify-center gap-3")}
<a href="#who" aria-label="Scroll down" class="mt-10 text-2xl" style="animation: bob 1.8s ease-in-out infinite">↓</a></div></section>
<section id="who" class="bg-[#e6def2] px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">What we send brands.</h2><p class="mb-14 text-[#2a1745]/75 reveal">Each creator, with the numbers that matter. Example formats, not real creators.</p>
<div class="flex flex-wrap justify-center gap-8 mb-20">{phones}</div>
<p class="text-sm tracking-widest uppercase mb-6 reveal">We work with products like:</p><div class="cloud flex flex-wrap justify-center gap-3 max-w-3xl mx-auto reveal">{cloud}</div></section>
<section id="approach" class="px-6 py-24 max-w-5xl mx-auto text-center"><h2 class="serif text-4xl md:text-6xl mb-14 reveal">How it works for <em class="text-[#7a4fc0]">brands</em>.</h2><div class="grid md:grid-cols-3 gap-8">{steps}</div>
<div class="grid sm:grid-cols-3 gap-4 mt-16">{"".join(f'<div class="reveal bg-white rounded-2xl p-6 text-left"><p class="font-bold mb-1">{t}</p><p class="text-sm text-[#2a1745]/70">{d}</p></div>' for _i, t, d in BENEFITS)}</div></section>
<div class="bg-[#e6def2] text-[#2a1745]">{creator_section('light')}</div>
<section class="bg-[#2a1745] text-white px-6 py-24 text-center"><h2 class="serif text-4xl md:text-6xl mb-4 reveal">Let's get you matched.</h2><p class="text-white/75 mb-10 reveal">{CTA_SUB}</p>{forms('dark')}</section>
{footer(True)}</div>"""
    page("layout-smooth.html", "Layout test: Smooth-style | Gratovo", "Smooth-style",
         "Soft and editorial. Full-screen tinted hero with a hand-drawn ellipse and two buttons, phone-shaped example cards, category pill cloud, For Creators section, serif headings.",
         "bg-[#fcfaf6]", css, body,
         extra_head='<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&amp;display=swap" rel="stylesheet">')


# ================================================================ 9. ADHESIVE
def build_adhesive():
    css = """
.hl { color:#0072b8; }
.diagram { height:150px; position:relative; background:#f4f9fe; border-bottom:1px solid #d5e6f4; overflow:hidden; }
.node { position:absolute; background:#fff; border:1px solid #c5d5e4; border-radius:8px; padding:4px 10px; font:11px/1.2 'JetBrains Mono', monospace; text-transform:uppercase; color:#3e4c5e; }
@keyframes pulse2 { 0% { box-shadow:0 0 0 0 rgba(0,114,184,.45); } 100% { box-shadow:0 0 0 22px rgba(0,114,184,0); } }
.pulse { animation: pulse2 2s ease-out infinite; }
.carousel { display:flex; gap:20px; overflow-x:auto; scroll-snap-type:x mandatory; padding-bottom:8px; scrollbar-width:none; }
.carousel::-webkit-scrollbar { display:none; }
.carousel > article { flex:0 0 300px; scroll-snap-align:start; background:#fff; border:1px solid #d5e6f4; border-radius:14px; overflow:hidden; }
.step-tab { padding:10px 16px; border-radius:10px; font-weight:600; color:#3e4c5e; }
.step-tab.is-active { background:#fff; color:#0a5c9e; box-shadow:0 1px 4px rgba(0,0,0,.12); }
"""
    d1 = '<div class="node" style="left:34%;top:14%">Your product</div><div class="node" style="left:12%;top:68%">Audience</div><div class="node" style="left:60%;top:68%">Goals</div><svg class="absolute inset-0 w-full h-full" aria-hidden="true"><line x1="50%" y1="32%" x2="24%" y2="66%" stroke="#c5d5e4"/><line x1="50%" y1="32%" x2="72%" y2="66%" stroke="#c5d5e4"/></svg>'
    d2 = '<div class="node" style="left:10%;top:20%">Creator A</div><div class="node pulse" style="left:42%;top:52%;border-color:#0072b8;color:#0a5c9e">Creator B</div><div class="node" style="left:62%;top:16%">Creator C</div>'
    d3 = '<div class="node pulse" style="left:26%;top:38%;border-color:#0072b8;color:#0a5c9e">Deal agreed ✓</div><div class="node" style="left:8%;top:8%">Scripts</div><div class="node" style="left:64%;top:10%">Dates</div><div class="node" style="left:60%;top:76%">Contract</div>'
    d4 = '<div class="absolute inset-0 flex items-center justify-center"><span class="pulse w-16 h-16 rounded-full bg-primary-container text-white flex items-center justify-center">' + mat('play_arrow', 'text-4xl') + '</span></div>'
    diag = [d1, d2, d3, d4]
    cards = "".join(
        f'<article><div class="diagram">{diag[i]}</div><div class="p-6"><p class="font-label-sm text-primary-container mb-1">STEP {i+1}</p><h3 class="font-headline-md text-on-background mb-1">{t}</h3><p class="text-secondary text-sm">{d}</p></div></article>'
        for i, (t, d) in enumerate(STEPS4))
    cats = [("AI assistants", "Reach people already learning to get more from AI chat and writing tools."),
            ("Automation", "Show workflow builders how your tool saves them hours, on screen."),
            ("Developer tools", "Put your product in front of developers who watch tutorials before they buy."),
            ("Productivity", "Get walked through in real workflows by creators who use tools like yours daily.")]
    tabs = "".join(f'<button class="step-tab" role="tab">{c}</button>' for c, _ in cats)
    panels = "".join(f'<div class="step-panel"><p class="text-lg text-on-surface-variant">{d}</p></div>' for _, d in cats)
    plats = "".join(f'<span class="font-headline-md text-secondary/70 uppercase tracking-widest">{p}</span>' for p in PLATFORMS * 3)
    ben = "".join(f'<div class="reveal" data-delay="{i*100}"><div class="w-12 h-12 rounded-xl bg-primary-fixed text-primary-container flex items-center justify-center mb-4">{mat(ic, "text-2xl")}</div><h3 class="font-headline-md mb-1">{t}</h3><p class="text-secondary">{d}</p></div>' for i, (ic, t, d) in enumerate(BENEFITS))
    hb = hero_buttons("bg-primary-container text-white rounded-md px-7 py-4 font-semibold", "border border-outline-variant rounded-md px-7 py-4 font-semibold", "mt-8 flex flex-wrap gap-3")
    body = f"""
<div class="bg-white text-on-background">
<header class="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-outline-variant"><div class="max-w-container-max mx-auto px-6 h-20 flex items-center justify-between"><a href="#">{wordmark()}</a>
<nav class="flex items-center gap-7 text-sm font-medium"><a class="hidden sm:block border-t-2 border-on-background pt-1" href="#">Home</a><a class="hidden sm:block" href="#how-it-works">For brands</a><a class="hidden sm:block" href="#for-creators">For creators</a><a href="#workwithus" class="bg-primary-container text-white rounded-md px-5 py-2.5 font-semibold">Contact</a></nav></div></header>
<main>
<section class="max-w-container-max mx-auto px-6 pt-20 pb-16"><p class="font-label-sm text-primary-container mb-4 tracking-widest">AI INFLUENCER MARKETING</p>
<h1 class="font-headline-lg text-4xl md:text-7xl max-w-5xl leading-[1.05]">{HEAD_PARTS[0]}<span class="hl">{HEAD_PARTS[1]}</span>{HEAD_PARTS[2]}</h1>
<p class="mt-6 text-xl text-secondary max-w-2xl">{SUB} {BODY}</p>{hb}</section>
<section class="border-y border-outline-variant py-5 marquee bg-surface-container-low"><div class="marquee-track">{plats}{plats}</div></section>
<section id="how" class="max-w-container-max mx-auto px-6 py-20"><div class="flex items-end justify-between mb-8"><div><p class="font-label-sm text-primary-container mb-2 tracking-widest">HOW IT WORKS FOR BRANDS</p><h2 class="font-headline-lg text-3xl md:text-5xl">Four steps, start to finish.</h2></div>
<div class="hidden md:flex gap-2"><button aria-label="Previous" onclick="document.getElementById('car').scrollBy({{left:-320,behavior:'smooth'}})" class="w-11 h-11 rounded-full border border-outline-variant">←</button><button aria-label="Next" onclick="document.getElementById('car').scrollBy({{left:320,behavior:'smooth'}})" class="w-11 h-11 rounded-full border border-outline-variant">→</button></div></div>
<div id="car" class="carousel">{cards}</div></section>
<section id="who" class="max-w-container-max mx-auto px-6 py-20"><p class="font-label-sm text-primary-container mb-2 tracking-widest">WHO IT'S FOR</p>
<h2 class="font-headline-lg text-3xl md:text-5xl max-w-4xl leading-tight reveal">We find AI creators for products that need showing, <span class="hl">and send brands the best fit, not a spreadsheet.</span></h2>
<div data-stepper class="mt-8"><div class="inline-flex flex-wrap gap-1 bg-surface-container-low border border-outline-variant rounded-xl p-1" role="tablist">{tabs}</div><div class="mt-6 min-h-[60px]">{panels}</div></div></section>
<section class="bg-surface-container-low"><div class="max-w-container-max mx-auto px-6 py-20 grid md:grid-cols-3 gap-10">{ben}</div></section>
{creator_section('light')}
<section class="max-w-container-max mx-auto px-6 py-24 text-center"><h2 class="font-headline-lg text-3xl md:text-5xl mb-3 reveal">Let's get you matched.</h2><p class="text-secondary mb-10 reveal">{CTA_SUB}</p>{forms('light')}</section>
</main>{footer()}</div>"""
    page("layout-adhesive.html", "Layout test: Adhesive-style | Gratovo", "Adhesive-style",
         "Clean and light. Big headline with blue highlight and two buttons, platform ticker, the real animated How It Works section (brand/creator tabs, matching and reporting cards), category tabs, For Creators section.",
         "bg-white", css, body)


# ================================================================ index
def build_index():
    items = "".join(
        f'<a href="{f}" class="block bg-white border border-outline-variant rounded-2xl p-6 hover:shadow-xl hover:-translate-y-1 transition"><h2 class="font-headline-md text-on-background mb-2">{n}</h2><p class="text-secondary">{b}</p><p class="mt-4 text-primary-container font-semibold">Open →</p></a>'
        for f, n, b in LAYOUTS)
    body = f"""<main class="max-w-4xl mx-auto px-6 py-16"><div class="mb-8">{wordmark("text-4xl")}</div>
<h1 class="font-headline-lg font-bold text-4xl mb-3 text-on-background">Layout tests</h1>
<p class="text-secondary text-lg mb-10">{len(LAYOUTS)} versions of the Gratovo homepage, each using a competitor's section order and effects with Gratovo's copy and colours. Every one speaks to both brands and creators. Open them one by one on desktop and phone. Sections that need proof Gratovo doesn't have yet (logos, testimonials, real creators) are left out or shown as clearly labelled examples.</p>
<div class="grid sm:grid-cols-2 gap-5">{items}</div>
<p class="mt-10 text-sm text-secondary">Compare with the current page: <a class="text-primary-container underline" href="{ASSET}index.html">index.html</a>. Research notes: <code>research/competitor-effects.md</code>. Regenerate with <code>python research/scripts/build-layout-tests.py</code>.</p></main>"""
    head = f"""<!DOCTYPE html><html class="light" lang="en"><head><meta charset="utf-8"><meta content="width=device-width, initial-scale=1.0" name="viewport"><meta name="robots" content="noindex, nofollow"><title>Layout tests | Gratovo</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script><link rel="stylesheet" href="{ASSET}fonts/fonts.css">{tailwind_config()}</head><body class="bg-background">{body}</body></html>"""
    (OUT / "index.html").write_text(head, encoding="utf-8")
    print("wrote index.html")


if __name__ == "__main__":
    build_attrakt()
    build_creatorauthority()
    build_scalepledge()
    build_nsentive()
    build_apollo()
    build_rightclick()
    build_mindshare()
    build_smooth()
    build_adhesive()
    build_index()
