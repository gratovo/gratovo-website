#!/usr/bin/env python3
"""Build the three public pages from shared pieces.

  index.html     both audiences (tabbed sections)
  brands.html    brands only
  creators.html  creators only

The contact section always keeps BOTH sides (brand / creator tabs); only its starting tab changes.
Shared blocks live in research/pages/partials/*.html (tailwind config, feature cards, vetting stats,
contact). Copy that differs per page (hero, process steps, FAQ) is defined below.

Edit the partials or the data in this file, then run:   python research/scripts/build-pages.py
Do not hand-edit the generated pages: the next run overwrites them.
"""
import re
import sys
import json
import hashlib
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PART = ROOT / "research" / "pages" / "partials"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import seo_content as SEO
from legal_content import LEGAL  # copy for the landing pages and guides
SITE = "https://gratovo.com"   # apex: www 301-redirects here, so canonicals must use it


def partial(name):
    return (PART / name).read_text(encoding="utf-8").rstrip() + "\n"


ARROW_ICON = '<span class="material-symbols-outlined" aria-hidden="true">arrow_forward</span>'


def cta(href, label, extra=""):
    """Primary call-to-action: a link styled as a button (css/theme.css .btn)."""
    return f'<a href="{href}"{extra} class="btn btn-primary">{label} {ARROW_ICON}</a>'

# ------------------------------------------------------------------ process steps
BRAND_STEPS = [
    ("mail", "Tell Us What You Sell",
     "A short message about your product and who it's for. We reply within 24 hours.",
     "brief", '{"topIcon":"mail","topText":"BRIEF RECEIVED","hubIcon":"schedule","hubText":"REPLY IN 24H","tags":["PRODUCT","AUDIENCE","GOAL"]}',
     "Animated diagram: your message arrives and we map your product, audience and goal."),
    ("groups", "Creator Matching",
     "You get 1 to 3 vetted creators with their views and audience details, never a list of 200.",
     "match", '{"foundText":"8 FOUND","vettedText":"3 VETTED"}',
     "Animated diagram: eight creators are found, then narrowed to three vetted matches."),
    ("handshake", "Introduction & Deal",
     "We introduce you and keep the conversation moving until you both agree.",
     "deal", '{"topIcon":"send","topText":"INTRO SENT","discs":["mail","description","chat"],"doneText":"DEAL AGREED"}',
     "Animated diagram: an introduction is sent and a deal is agreed."),
    ("visibility", "Review & Go Live",
     "We coordinate the contract, script and posting date. You approve the video before it posts.",
     "review", '{"topIcon":"visibility","topText":"VIDEO PREVIEW","approveText":"VIDEO APPROVED","finalIcon":"event_available","finalText":"READY TO POST"}',
     "Animated diagram: you preview the video, approve it, and it is ready to post."),
    ("trending_up", "Reporting & Scaling",
     "We track how each video performs, then help you scale with the creators who deliver.",
     "report", '{"finalText":"TOP PERFORMER"}',
     "Animated diagram: data is collected and analysed, and the top performing creator is picked to scale."),
]
CREATOR_STEPS = [
    ("smart_display", "Tell Us About Your Channel",
     "Your channel link and what you cover. It takes two minutes.",
     "brief", '{"topIcon":"smart_display","topText":"CHANNEL RECEIVED","hubIcon":"search","hubText":"WE REVIEW IT","tags":["NICHE","AUDIENCE","FORMAT"]}',
     "Animated diagram: your channel arrives and we map your niche, audience and format."),
    ("groups", "Brand Matching",
     "We match you with AI and SaaS brands that fit your audience.",
     "match", '{"brands":true,"foundText":"8 BRANDS","vettedText":"3 FIT"}',
     "Animated diagram: eight brands are found, then narrowed to three that fit your audience."),
    ("handshake", "A Deal That Fits",
     "When a brand fits, we bring you the details. You decide.",
     "deal", '{"topIcon":"mail","topText":"OFFER RECEIVED","discs":["rocket_launch","description","chat"],"doneText":"DEAL AGREED"}',
     "Animated diagram: an offer arrives and a deal is agreed."),
    ("rocket_launch", "Create & Go Live",
     "You make the video. We keep the brand conversation moving until it posts.",
     "review", '{"topIcon":"upload","topText":"DRAFT SENT","approveText":"BRAND APPROVED","finalIcon":"event_available","finalText":"READY TO POST"}',
     "Animated diagram: your draft is sent, the brand approves it, and it is ready to post."),
    ("trending_up", "Reporting & Repeat Deals",
     "We track how your video performs, then line up the next brand that fits.",
     "report", '{"brands":true,"finalText":"NEXT DEAL"}',
     "Animated diagram: results are collected and analysed, and the next brand deal is lined up."),
]

# Optional real creator photos for the brand-side matching and reporting cards.
# Put permitted photos in images/creators/creator-1.jpg ... creator-8.jpg (jpg/png/webp, roughly square, face near the top).
# Only files that exist are used; the neutral avatar shows for the rest.
def creator_photos():
    out = []
    for n in range(1, 9):
        for ext in ("jpg", "jpeg", "png", "webp"):
            f = ROOT / "images" / "creators" / f"creator-{n}.{ext}"
            if f.exists():
                out.append(f"images/creators/{f.name}")
                break
        else:
            out.append("")
    return out if any(out) else None


_ph = creator_photos()
if _ph:
    _js = json.dumps(_ph)
    BRAND_STEPS[1] = BRAND_STEPS[1][:4] + (BRAND_STEPS[1][4][:-1] + ',"photos":' + _js + "}",) + BRAND_STEPS[1][5:]
    BRAND_STEPS[4] = BRAND_STEPS[4][:4] + (BRAND_STEPS[4][4][:-1] + ',"photos":' + _js + "}",) + BRAND_STEPS[4][5:]

ARROW_L = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>'
ARROW_R = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18l6-6-6-6"/></svg>'


def esc(s):
    return s.replace("&", "&amp;")


def step_html(i, s):
    icon, title, desc, comp, opts, alt = s
    return (
        f'<div class="pc-step"><div class="pc-card">'
        f'<div class="pc-tag"><span class="material-symbols-outlined" aria-hidden="true">{icon}</span></div>'
        f'<div class="pc-frame"><div class="pc-card-head"><div class="pc-card-row"><h3>{esc(title)}</h3><span class="pc-num">{i}</span></div>'
        f'<p>{esc(desc)}</p></div>'
        f"<div class=\"pc-visual\" data-comp=\"{comp}\" data-opt='{opts}' role=\"img\" aria-label=\"{esc(alt)}\"></div>"
        f'</div></div></div>'
    )


def track(aud, steps, hidden):
    name = "brands" if aud == "brand" else "creators"
    cards = "\n                        ".join(step_html(i + 1, s) for i, s in enumerate(steps))
    return (f'<div data-pc-panel="{aud}" role="tabpanel" aria-label="How it works for {name}"{" hidden" if hidden else ""}>\n'
            f'                        <div class="pc-track" tabindex="0" aria-label="Steps for {name}, scroll sideways">\n'
            f'                        {cards}\n                        </div>\n                    </div>')


def process_section(mode):
    """mode: both | brand | creator. Single-audience pages get no tabs."""
    both = mode == "both"
    tabs = ""
    if both:
        tabs = ('<div class="pc-tabs" role="tablist" aria-label="Choose your side">\n'
                '                        <button type="button" role="tab" class="pc-tabbtn pc-on" data-aud="brand" aria-selected="true">For <span>Brands</span></button>\n'
                '                        <button type="button" role="tab" class="pc-tabbtn" data-aud="creator" aria-selected="false">For <span>Creators</span></button>\n'
                '                        <span class="pc-ind" aria-hidden="true"></span>\n                    </div>')
    sub = {"both": "Pick your side to see the steps. Both start with one message.",
           "brand": "Five steps, from your first message to your next deal.",
           "creator": "Five steps, from your channel link to your next brand deal."}[mode]
    panels = []
    if mode in ("both", "brand"):
        panels.append(track("brand", BRAND_STEPS, False))
    if mode in ("both", "creator"):
        panels.append(track("creator", CREATOR_STEPS, mode == "both"))
    cta_links = []
    if mode in ("both", "brand"):
        cta_links.append(cta("#workwithus", "Find My Creators", ' data-pc-cta="brand"'))
    if mode in ("both", "creator"):
        cta_links.append(cta("#creators", "Get Brand Deals", ' data-pc-cta="creator"' + (" hidden" if both else "")))
    return f'''<!-- How it works (animated{", tabbed by audience" if both else ""}) -->
        <section id="how-it-works" class="pc-section" aria-label="How it works">
            <div class="pattern-tint" aria-hidden="true"></div>
            <div class="pc-wrap">
                <div class="pc-head">
                    <p class="pc-eyebrow font-display text-label uppercase">How it works</p>
                    <h2 class="font-display text-h2 mb-4 text-ink">Start With a Message. <span class="pc-grad">Scale What Works.</span></h2>
                    <p class="pc-sub font-body text-lead">{sub}</p>
                    {tabs}
                </div>
                <div class="pc-panels">
                    {chr(10).join("                    " + p if k else p for k, p in enumerate(panels))}
                </div>
                <div class="pc-controls">
                    <button type="button" class="pc-arrow pc-prev" aria-label="Previous steps" disabled>{ARROW_L}</button>
                    <div class="pc-meter" aria-hidden="true"><div class="pc-progress"><i></i></div><p class="pc-count"></p></div>
                    <button type="button" class="pc-arrow pc-next" aria-label="Next steps">{ARROW_R}</button>
                </div>
                <div class="pc-cta">
                    {chr(10).join("                    " + c if k else c for k, c in enumerate(cta_links))}
                </div>
            </div>
        </section>

        '''


# ------------------------------------------------------------------ FAQ
BRAND_FAQ = [
    ("What does Gratovo actually do?",
     "We connect AI and SaaS brands with vetted creators. We make the introduction, keep the conversation moving, and take care of the contract, script and posting date. We recommend 1 to 3 creators, not a list of 200."),
    ("How do you choose the creators?",
     "Before you see a name, we check real average views, engagement and audience location. Our standards are 30K+ average views, 3-8% engagement and 35%+ of the audience in your target country. No fake audiences, no bad-fit channels."),
    ("What kinds of brands do you work with?",
     "AI and SaaS products that people can try: tools, apps and platforms that are easy to show in a tutorial or a walkthrough."),
    ("Do I get to approve the video?",
     "Yes. You approve the video before it goes live."),
    ("How long until a video goes live?",
     "We reply within 24 hours. Most deals go live within about a month."),
    ("Why not contact creators myself?",
     "You can. It means searching, checking each channel, writing to them and chasing replies. We do all of that, and you only hear about the creators worth your time."),
    ("How do you report results?",
     "We track how each video performs. When one works, we help you scale with the creators who deliver."),
]
CREATOR_FAQ = [
    ("How does Gratovo find me brand deals?",
     "You tell us about your channel. We put you forward to AI and SaaS brands that fit your audience, so the deals come to you instead of you pitching cold."),
    ("What kind of channel do you work with?",
     "Creators making content about AI and software, on YouTube, LinkedIn, X or newsletters. We look at average views, engagement and where your audience is, so send your link and we will tell you if there is a fit."),
    ("Do I choose which brands I work with?",
     "Yes. When a brand fits, we bring you the details and you decide."),
    ("Who will I be talking to?",
     "One contact at Gratovo. No long media-kit requests and no endless email threads."),
    ("What happens after my video goes live?",
     "We track how it performs, then line up the next brand that fits."),
    ("How quickly will I hear back?",
     "We reply within 24 hours."),
]
CHEV = '<svg class="faq-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>'


def faq_items(prefix, data):
    out = []
    for i, (q, a) in enumerate(data):
        pid = f"faq-{prefix}-{i}"
        out.append(
            f'<div class="faq-item"><h3><button type="button" class="faq-q" aria-expanded="false" aria-controls="{pid}">'
            f'<span>{escape(q)}</span>{CHEV}</button></h3>'
            f'<div class="faq-a" id="{pid}" role="region"><div><p>{escape(a)}</p></div></div></div>')
    return "\n                        ".join(out)


def faq_section(mode):
    both = mode == "both"
    tabs = ""
    if both:
        tabs = ('<div class="faq-tabs" role="tablist" aria-label="Questions for">\n'
                '                        <button type="button" role="tab" class="faq-tabbtn faq-on" data-aud="brand" aria-selected="true">For <span>Brands</span></button>\n'
                '                        <button type="button" role="tab" class="faq-tabbtn" data-aud="creator" aria-selected="false">For <span>Creators</span></button>\n'
                '                        <span class="faq-ind" aria-hidden="true"></span>\n                    </div>')
    panels = []
    if mode in ("both", "brand"):
        panels.append(f'<div data-faq-panel="brand" role="tabpanel" aria-label="Questions for brands" class="faq-list">\n                        {faq_items("b", BRAND_FAQ)}\n                    </div>')
    if mode in ("both", "creator"):
        panels.append(f'<div data-faq-panel="creator" role="tabpanel" aria-label="Questions for creators" class="faq-list"{" hidden" if both else ""}>\n                        {faq_items("c", CREATOR_FAQ)}\n                    </div>')
    return f'''<!-- FAQ{" (tabbed by audience)" if both else ""} -->
        <section id="faq" class="bg-band border-y border-line py-section scroll-mt-24" aria-label="Frequently asked questions">
            <div class="max-w-container-max mx-auto px-grid-gutter grid grid-cols-1 md:grid-cols-[minmax(0,1fr)_minmax(0,2.3fr)] gap-10 md:gap-16 items-start">
                <div>
                    <p class="font-display text-label uppercase text-brand-deep mb-3">FAQs</p>
                    <h2 class="font-display text-h2 text-ink">Still Have Questions?</h2>
                </div>
                <div>
                    {tabs}
                    {chr(10).join("                    " + p if k else p for k, p in enumerate(panels))}
                </div>
            </div>
        </section>

        '''


# ------------------------------------------------------------------ hero (MindShare-style) + header
def ticker_html():
    """Hero strip: the same keywords as the loop beside the contact form. Two identical halves, so -50% is a seamless loop."""
    one = "".join(f'<span class="tk-item{" tk-em" if em else ""}">{escape(t)}</span>' for t, em in KEYWORDS)
    return f'<div class="marquee-track" style="animation-duration:{round(len(KEYWORDS) * 3.6)}s">{one * 2}</div>'

PILL_DARK = 'class="btn btn-light"'
PILL_LINE = 'class="btn btn-ghost"'

HERO = {
    "both": dict(chip="", tag="B2B Influencer Marketing Services",
                 sub="Delivering strategy, creators, and measurement for brand campaigns",
                 b1=('brands.html', "I'm a Brand &rarr;"), b2=('creators.html', "I'm a Creator &rarr;")),
    "brand": dict(chip="For brands", tag="Vetted AI Creators for Your Product",
                  sub="Delivering vetted creators, introductions, and contracts for AI and SaaS brands",
                  b1=('#workwithus', "Find My Creators &rarr;"), b2=('#how-it-works', "How It Works")),
    "creator": dict(chip="For creators", tag="Brand Deals for AI and Tech Creators",
                    sub="Delivering matched brands, introductions, and repeat deals for creators",
                    b1=('#creators', "Get Brand Deals &rarr;"), b2=('#how-it-works', "How It Works")),
}


def site_header(nav, hide=False):
    """Top bar. hide=True (home, brands, creators): fixed and hidden while the hero is on screen (js/site-header.js
    reveals it once the hero has scrolled away). Other pages: sticky and always visible.
    nav: which link is current: home | brands | creators | guides | "" """
    cur = " nav-on"
    c = {k: (cur if nav == k else "") for k in ("home", "brands", "creators", "guides")}
    pos = "fixed inset-x-0 is-hidden" if hide else "sticky"
    attrs = " data-autohide data-hide-on-hero inert" if hide else " data-autohide"
    return f'''<header class="site-header {pos} top-0 z-50 bg-white text-ink border-b border-line shadow-card"{attrs}>
        <div class="max-w-container-max mx-auto flex items-center justify-between gap-3 px-4 md:px-grid-gutter h-20">
            <a href="index.html" class="shrink-0 leading-none" aria-label="Gratovo home"><img src="images/logo-mark.svg" alt="Gratovo" width="56" height="44" class="h-8 sm:h-10 w-auto"></a>
            <nav class="flex items-center gap-4 sm:gap-8 font-display text-[12px] font-bold tracking-wider sm:text-small uppercase" aria-label="Main">
                <a class="nav-link inline-flex items-center{c["home"]}" href="index.html" aria-label="Home"><span class="material-symbols-outlined icon-fill text-xl sm:hidden" aria-hidden="true">home</span><span class="hidden sm:inline">Home</span></a>
                <a class="nav-link{c["brands"]}" href="brands.html"><span class="hidden sm:inline">For </span>brands</a>
                <a class="nav-link{c["creators"]}" href="creators.html"><span class="hidden sm:inline">For </span>creators</a>
                <a class="nav-link hidden md:inline-block{c["guides"]}" href="guides.html">Guides</a>
                <a href="#contact-card" aria-label="Contact us" title="Contact us" class="nav-call bg-tint border border-line rounded-full w-10 h-10 sm:w-11 sm:h-11 inline-flex items-center justify-center text-lg sm:text-xl leading-none"><span aria-hidden="true">&#128222;</span></a>
            </nav>
        </div>
    </header>
    '''


WORDMARK_HERO = ('<span class="wordmark wordmark-grad wordmark-caps text-logo" role="img" aria-label="Gratovo">'
                 '<span class="wm-mark" aria-hidden="true"></span><span class="wm-text" aria-hidden="true">ratovo</span></span>')


def hero(mode):
    h = HERO[mode]
    chip = ""
    if h["chip"]:
        chip = (f'<div class="hero-chip flex items-center justify-center gap-3 mb-8 portrait:order-2 portrait:mb-0 portrait:mt-6"><a href="index.html" class="tag tag-link inline-flex items-center gap-1.5">'
                f'<span class="material-symbols-outlined icon-fill text-base" aria-hidden="true">home</span>Back to Home</a><p class="tag">{h["chip"]}</p></div>')
    # Landscape: everything centred. Portrait (phones, tall windows): the logo sits at the top, the copy is centred in the space below.
    # .hero-layer holds everything that moves with the layout; js/hero-spotlight.js clones it into the light "lens" version.
    return f'''<!-- Hero: the full logo is the centrepiece; the nav bar stays hidden until the visitor scrolls a little -->
        <section id="hero" data-hero class="hero-bg relative text-white min-h-[100svh] flex flex-col">
            <div class="pattern-cubes" aria-hidden="true"></div>
            <div class="hero-layer">
                <div class="relative flex-1 flex flex-col items-center justify-center portrait:justify-start portrait:pt-[9svh] text-center px-6 py-10 w-full">
                    {chip}
                    <a href="index.html" class="leading-none portrait:order-1" aria-label="Gratovo home">{WORDMARK_HERO}</a>
                    <div class="hero-copy portrait:order-3 portrait:my-auto portrait:pt-10">
                        <h1 class="hero-title font-display text-h2 text-white max-w-3xl mx-auto mt-8 portrait:mt-0">{h["tag"]}</h1>
                        <p class="hero-sub font-body text-lead text-white/90 mt-4 max-w-2xl mx-auto">{h["sub"]}</p>
                        <div class="hero-actions mt-10 flex flex-wrap justify-center gap-3"><a href="{h["b1"][0]}" {PILL_DARK}>{h["b1"][1]}</a><a href="{h["b2"][0]}" {PILL_LINE}>{h["b2"][1]}</a></div>
                    </div>
                </div>
                <div class="scroll-cue" aria-hidden="true"><span>Scroll</span><i></i></div>
                <div class="ticker marquee relative py-6 border-t border-white/20" aria-hidden="true">{ticker_html()}</div>
            </div>
        </section>

        '''


# ------------------------------------------------------------------ creator benefit cards (image cards, same design as the brand cards)
UNS = "https://images.unsplash.com/photo-{}?auto=format&fit=crop&q=80&w=800"
CREATOR_CARDS = [
    ("handshake", "Brand Deals Come to You", "No cold outreach to brands. We bring AI and SaaS sponsorship deals to creators who fit.",
     UNS.format("1598550476439-6847785fcea6"), "A creator's recording desk with a camera on a tripod, a microphone and two monitors."),
    ("person", "One Contact, Less Back-and-Forth", "No long media-kit requests or endless email threads. One person to talk to.",
     UNS.format("1579389083046-e3df9c2b3325"), "Hands working on a laptop next to a phone, representing a single clear point of contact."),
    ("trending_up", "Repeat Deals", "We track how your video performs, then line up the next brand that fits.",
     UNS.format("1460925895917-afdab827c52f"), "A laptop showing a performance analytics dashboard."),
]
CARD = ('<div class="bg-card border border-line rounded-card overflow-hidden flex flex-col group hover:-translate-y-1 hover:shadow-lift shadow-card transition-all duration-300">'
        '<img src="{img}" alt="{alt}" width="800" height="533" loading="lazy" decoding="async" class="h-48 w-full object-cover">'
        '<div class="p-8 flex flex-col items-start flex-grow relative"><div class="w-12 h-12 rounded-full bg-brand flex items-center justify-center text-white absolute -top-6 right-8 shadow-card">'
        '<span class="material-symbols-outlined icon-fill text-2xl">{ic}</span></div>'
        '<h3 class="font-display text-h3 text-ink mb-4">{t}</h3><p class="font-body text-body text-muted">{d}</p></div></div>')


def creator_block():
    cards = "".join(CARD.format(ic=ic, t=t, d=d, img=img.replace("&", "&amp;"), alt=alt) for ic, t, d, img, alt in CREATOR_CARDS)
    return f'''<div class="text-center max-w-3xl mx-auto mb-12">
                    <h2 class="font-display text-h2 text-ink mb-4">Brand Deals That Fit Your Channel.</h2>
                    <p class="font-body text-lead text-muted">Already making content about AI and software? We put you in front of the brands that fit your audience.</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">{cards}</div>
                <div class="text-center">{cta("#creators", "Get Brand Deals")}</div>'''


def creator_section():
    """creators.html: the creator cards sit where the brand cards sit on brands.html."""
    return f'''<!-- Creator benefits -->
        <section id="for-creators" class="w-full pt-section pb-section scroll-mt-24">
            <div class="max-w-container-max mx-auto px-grid-gutter">
                {creator_block()}
            </div>
        </section>

        '''


def benefits_tabbed(features_html):
    """index.html: brand cards and creator block in one section with I'm a brand / I'm a creator tabs."""
    m = re.search(r'(<div class="grid grid-cols-1 md:grid-cols-3 gap-8">.*</div>)\s*</div>\s*</section>', features_html, re.S)
    brand_grid = m.group(1)
    return f'''<!-- Benefits (tabbed by audience) -->
        <section id="benefits" class="w-full pt-section scroll-mt-24" aria-label="Why Gratovo">
            <div class="max-w-container-max mx-auto px-grid-gutter">
                <div class="flex justify-center mb-10">
                    <div class="faq-tabs !mb-0" role="tablist" aria-label="I am a">
                        <button type="button" role="tab" class="faq-tabbtn faq-on" data-aud="brand" aria-selected="true">I'm a <span>Brand</span></button>
                        <button type="button" role="tab" class="faq-tabbtn" data-aud="creator" aria-selected="false">I'm a <span>Creator</span></button>
                        <span class="faq-ind" aria-hidden="true"></span>
                    </div>
                </div>
                <div data-bn-panel="brand" role="tabpanel" aria-label="For brands">
                    {brand_grid}
                </div>
                <div data-bn-panel="creator" role="tabpanel" aria-label="For creators" hidden>
                    {creator_block()}
                </div>
            </div>
        </section>

        '''


# ------------------------------------------------------------------ footer / head
def footer():
    a = 'class="font-display text-small font-semibold text-muted hover:text-brand-deep transition-colors"'
    h = 'class="font-display text-label uppercase text-ink mb-4"'
    res = "".join(f'<li><a {a} href="{s}.html">{escape(CARD_COPY[s][1])}</a></li>' for s in FOOTER_RES)
    return f"""<!-- Footer -->
    <footer class="bg-canvas py-12 border-t border-line">
        <div class="max-w-container-max mx-auto px-grid-gutter grid gap-10 md:grid-cols-[1.4fr_1fr_1.6fr_1fr]">
            <div>
                <a href="index.html" class="inline-block leading-none mb-4" aria-label="Gratovo home"><span class="wordmark wordmark-caps wordmark-grad wordmark-color" style="--wm-size:2.5rem" role="img" aria-label="Gratovo"><img src="images/logo-mark.svg" alt="" width="40" height="32"><span class="wm-text" aria-hidden="true">ratovo</span></span></a>
                <p class="font-body text-small text-muted max-w-xs">Connecting AI brands with the right creators.</p>
                <p class="font-body text-small text-muted mt-4">&copy; 2026 Gratovo</p>
            </div>
            <nav aria-label="Explore"><p {h}>Explore</p><ul class="flex flex-col gap-2.5">
                <li><a {a} href="index.html">Home</a></li><li><a {a} href="brands.html">For Brands</a></li><li><a {a} href="creators.html">For Creators</a></li><li><a {a} href="guides.html">Guides</a></li></ul></nav>
            <nav aria-label="Resources"><p {h}>Resources</p><ul class="flex flex-col gap-2.5">{res}</ul></nav>
            <nav aria-label="Legal"><p {h}>Legal</p><ul class="flex flex-col gap-2.5">
                <li><a {a} href="privacy-policy.html">Privacy Policy</a></li><li><a {a} href="terms-of-service.html">Terms of Service</a></li></ul></nav>
        </div>
    </footer>
"""


# ------------------------------------------------------------------ resource cards (internal links)
CARD_COPY = {
    "saas-influencer-marketing": ("smart_display", "SaaS Influencer Marketing", "How creators show your product to the people who need it, and how we find them."),
    "ai-youtube-sponsorships": ("search", "AI YouTube Sponsorships", "Dedicated video, integration or mention: how sponsorships work and what to check first."),
    "ai-youtuber-brand-deals": ("handshake", "Brand Deals for AI YouTubers", "How we bring AI and SaaS sponsorship deals to creators who fit."),
    "ai-influencer-marketing-guide": ("description", "AI Influencer Marketing Guide", "What it is, why it suits software, and how to run it without wasting a month."),
    "how-to-find-ai-youtubers-to-sponsor": ("search", "How to Find AI YouTubers to Sponsor", "Search like your buyer, shortlist ten, cut to three."),
    "how-to-vet-ai-creators-before-sponsoring": ("verified", "How to Vet an AI Creator", "Six checks and the red flags, in the order we run them."),
    "how-ai-creators-get-brand-sponsorships": ("trending_up", "How Creators Get Brand Sponsorships", "What brands look at, what to send them, and how to get repeat deals."),
}
FOOTER_RES = ["ai-influencer-marketing-guide", "saas-influencer-marketing", "ai-youtube-sponsorships", "ai-youtuber-brand-deals",
              "how-to-find-ai-youtubers-to-sponsor", "how-to-vet-ai-creators-before-sponsoring", "how-ai-creators-get-brand-sponsorships"]
RESOURCES = {"both": ["ai-influencer-marketing-guide", "how-to-find-ai-youtubers-to-sponsor", "how-ai-creators-get-brand-sponsorships"],
             "brand": ["saas-influencer-marketing", "ai-youtube-sponsorships", "how-to-vet-ai-creators-before-sponsoring"],
             "creator": ["ai-youtuber-brand-deals", "how-ai-creators-get-brand-sponsorships", "ai-influencer-marketing-guide"]}


def link_card(slug):
    ic, t, d = CARD_COPY[slug]
    return (f'<a href="{slug}.html" class="group block bg-card border border-line rounded-card p-8 shadow-card hover:-translate-y-1 hover:shadow-lift transition-all duration-300">'
            f'<span class="w-12 h-12 rounded-full bg-brand flex items-center justify-center text-white shadow-card mb-6"><span class="material-symbols-outlined icon-fill text-2xl" aria-hidden="true">{ic}</span></span>'
            f'<h3 class="font-display text-h3 text-ink mb-3">{escape(t)}</h3><p class="font-body text-body text-muted mb-5">{escape(d)}</p>'
            f'<span class="font-display text-label uppercase text-brand-deep inline-flex items-center gap-1">Read more <span class="material-symbols-outlined text-lg" aria-hidden="true">arrow_forward</span></span></a>')


def resources_section(slugs, heading="Learn More Before You Reach Out.", all_link=False):
    cards = "".join(link_card(s) for s in slugs)
    more = f'<div class="text-center mt-10"><a href="guides.html" class="btn btn-light">All guides {ARROW_ICON}</a></div>' if all_link else ""
    return f"""<!-- Guides and resources (internal links) -->
        <section class="bg-canvas py-section" aria-label="Guides and resources">
            <div class="max-w-container-max mx-auto px-grid-gutter">
                <div class="text-center max-w-3xl mx-auto mb-12">
                    <p class="font-display text-label uppercase text-brand-deep mb-3">Guides</p>
                    <h2 class="font-display text-h2 text-ink">{heading}</h2>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8">{cards}</div>
                {more}
            </div>
        </section>

        """


# ------------------------------------------------------------------ pages registry
TODAY = date.today().isoformat()
ROBOTS_INDEX = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
ORG_ID = f"{SITE}/#organization"

PAGES = {
    "index.html": dict(
        mode="both", slug="home", kind="core", nav="home", url=f"{SITE}/", unsplash=True,
        title="AI Influencer Marketing for AI and SaaS Brands | Gratovo",
        desc="We connect AI and SaaS brands with vetted creators, and creators with brand deals that fit. We make the introductions and take care of contracts and posting."),
    "brands.html": dict(
        mode="brand", slug="brands", kind="core", nav="brands", url=f"{SITE}/brands.html", unsplash=True,
        title="Find Vetted AI Creators for Your Product | Gratovo",
        desc="Get 1 to 3 vetted AI creators picked for your product. We make the introduction and handle contracts and posting. You approve the video before it goes live."),
    "creators.html": dict(
        mode="creator", slug="creators", kind="core", nav="creators", url=f"{SITE}/creators.html", unsplash=True,
        title="Brand Deals for AI and Tech Creators | Gratovo",
        desc="Already making content about AI and software? Gratovo puts you in front of AI and SaaS brands that fit your audience. One contact, no cold outreach."),
}
for _sp in SEO.PAGES:
    PAGES[f"{_sp['slug']}.html"] = dict(
        mode=_sp["aud"], slug=_sp["slug"], kind=_sp["kind"], data=_sp, url=f"{SITE}/{_sp['slug']}.html",
        nav=("brands" if _sp["aud"] == "brand" else "creators") if _sp["kind"] == "landing" else "guides",
        title=_sp["title"], desc=_sp["desc"])
for _slug, _d in LEGAL.items():
    PAGES[f"{_slug}.html"] = dict(mode="both", slug=_slug, kind="legal", data=_d, url=f"{SITE}/{_slug}.html", nav="", noindex=True,
                                  robots="noindex, follow", title=f"{_d['title']} | Gratovo", desc=f"{_d['title']} of Gratovo.")
PAGES["guides.html"] = dict(mode="both", slug="guides", kind="hub", data=SEO.HUB, url=f"{SITE}/guides.html", nav="guides",
                            title=SEO.HUB["title"], desc=SEO.HUB["desc"])


# ------------------------------------------------------------------ structured data
def ld_script(obj, ident=""):
    idattr = f' id="{ident}"' if ident else ""
    return f'<script type="application/ld+json"{idattr}>' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"


def org_ld():
    return {"@context": "https://schema.org", "@type": "Organization", "@id": ORG_ID, "name": "Gratovo", "url": f"{SITE}/",
            "logo": {"@type": "ImageObject", "url": f"{SITE}/images/icon-512.png", "width": 512, "height": 512},
            "image": f"{SITE}/images/og/home.png",
            "description": "Gratovo is an influencer marketing broker for AI and SaaS. We connect brands with vetted creators, and creators with brand deals that fit.",
            "email": "mustafa@gratovo.com", "areaServed": "Worldwide",
            "knowsAbout": ["Influencer marketing", "AI influencer marketing", "SaaS influencer marketing", "YouTube sponsorships", "Creator brand deals"],
            "contactPoint": {"@type": "ContactPoint", "contactType": "customer support", "email": "mustafa@gratovo.com", "availableLanguage": "English"}}


def website_ld():
    return {"@context": "https://schema.org", "@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": "Gratovo",
            "description": "AI influencer marketing for AI and SaaS brands and creators.", "inLanguage": "en", "publisher": {"@id": ORG_ID}}


def breadcrumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


def service_ld(p, audience):
    return {"@context": "https://schema.org", "@type": "Service", "name": p["title"].split(" | ")[0], "serviceType": "Influencer marketing brokerage",
            "description": p["desc"], "url": p["url"], "provider": {"@id": ORG_ID}, "areaServed": "Worldwide",
            "audience": {"@type": "Audience", "audienceType": audience}}


def article_ld(p):
    d = p["data"]
    return {"@context": "https://schema.org", "@type": "Article", "headline": d["h1"][:110], "description": d["desc"],
            "datePublished": SEO.DATE, "dateModified": SEO.DATE, "inLanguage": "en", "mainEntityOfPage": {"@type": "WebPage", "@id": p["url"]},
            "image": f"{SITE}/images/og/{p['slug']}.png", "author": {"@type": "Organization", "name": "Gratovo", "@id": ORG_ID},
            "publisher": {"@id": ORG_ID}}


def faq_obj(items):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}


def page_ld(p):
    kind, mode = p["kind"], p["mode"]
    home = ("Home", f"{SITE}/")
    if kind == "core" and mode == "both":
        return [org_ld(), website_ld(), faq_obj(BRAND_FAQ + CREATOR_FAQ)]
    if kind == "core":
        brand = mode == "brand"
        return [org_ld(), breadcrumb_ld([home, ("For brands" if brand else "For creators", p["url"])]),
                service_ld(p, "AI and SaaS brands" if brand else "AI and software creators"),
                faq_obj(BRAND_FAQ if brand else CREATOR_FAQ)]
    d = p["data"]
    if kind == "landing":
        brand = d["aud"] == "brand"
        parent = ("For brands", f"{SITE}/brands.html") if brand else ("For creators", f"{SITE}/creators.html")
        return [org_ld(), breadcrumb_ld([home, parent, (d["crumb"], p["url"])]),
                service_ld(p, "AI and SaaS brands" if brand else "AI and software creators"), faq_obj(d["faq"])]
    if kind == "article":
        return [org_ld(), breadcrumb_ld([home, ("Guides", f"{SITE}/guides.html"), (d["crumb"], p["url"])]), article_ld(p), faq_obj(d["faq"])]
    return [org_ld(), breadcrumb_ld([home, ("Guides", p["url"])])]


# ------------------------------------------------------------------ <head>
def head(p, base=False):
    t, d, u = escape(p["title"]), escape(p["desc"]), p["url"]
    og = f"{SITE}/images/og/{p['slug']}.png"
    robots = p.get("robots", ROBOTS_INDEX)
    article = p["kind"] == "article"
    extra = ""
    if article:
        extra = (f'\n    <meta property="article:published_time" content="{SEO.DATE}">\n    <meta property="article:modified_time" content="{SEO.DATE}">'
                 f'\n    <meta property="article:author" content="Gratovo">')
    canon = "" if p.get("noindex") else f'\n    <link rel="canonical" href="{u}">'
    logo_font = '\n    <link rel="preload" href="fonts/outfit-logo.woff2" as="font" type="font/woff2" crossorigin>' if p["kind"] == "core" and not p.get("noindex") else ""
    script = "site.min.js" if p["kind"] == "core" and not p.get("noindex") else "lite.min.js"   # only the hero pages need the hero and "How it works" code
    lds = "\n    ".join(ld_script(o) for o in p.get("ld", page_ld(p))) if not p.get("noindex") else ""
    return f"""<!DOCTYPE html>
<html class="light" lang="en">

<head>
    <meta charset="utf-8">
    <meta content="width=device-width, initial-scale=1.0" name="viewport">{'<base href="/">' if base else ''}
    <title>{t}</title>
    <meta name="description" content="{d}">
    <meta name="robots" content="{robots}">
    <meta name="theme-color" content="#0072b8">
    <meta name="author" content="Gratovo">{canon}
    <link rel="icon" type="image/svg+xml" href="images/logo.svg">
    <link rel="icon" type="image/png" sizes="192x192" href="images/icon-192.png">
    <link rel="apple-touch-icon" href="images/apple-touch-icon.png">
    <link rel="manifest" href="manifest.webmanifest">

    <meta property="og:type" content="{'article' if article else 'website'}">
    <meta property="og:site_name" content="Gratovo">
    <meta property="og:locale" content="en_US">
    <meta property="og:url" content="{u}">
    <meta property="og:title" content="{t}">
    <meta property="og:description" content="{d}">
    <meta property="og:image" content="{og}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="{t}">{extra}

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="{u}">
    <meta name="twitter:title" content="{t}">
    <meta name="twitter:description" content="{d}">
    <meta name="twitter:image" content="{og}">
    <meta name="twitter:image:alt" content="{t}">

    <!-- Speed: fonts and the one stylesheet are requested first; the site script is deferred -->
    <link rel="preload" href="fonts/plus-jakarta-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="fonts/source-sans-3-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="fonts/material-symbols-subset.woff2" as="font" type="font/woff2" crossorigin>{logo_font}
    <link rel="stylesheet" href="css/site.min.css">
    <script src="js/{script}" defer></script>
    <!-- Structured data -->
    {lds}
    <noscript><style>.site-header.is-hidden{{transform:none!important}}</style></noscript>
</head>
"""


# Vertical keyword loop beside the contact form: (text, emphasised). One copy is repeated 3x so the loop never jumps.
KEYWORDS = [
    ("no cold emails", 0), ("no chasing replies", 0), ("no guessing who's legit", 0), ("no endless threads", 0),
    ("just the right match", 1),
    ("no media-kit requests", 0), ("no fake audiences", 0), ("no bad-fit channels", 0),
    ("1 to 3 vetted creators", 1),
    ("no pitching cold", 0), ("no spreadsheets", 0), ("no scheduling ping-pong", 0),
    ("one contact at Gratovo", 1),
    ("no contract headaches", 0),
    ("deals that fit", 1),
    ("no 200-name lists", 0),
    ("you approve every video", 1),
    ("no ghosted emails", 0),
    ("reply within 24 hours", 1),
]
SECONDS_PER_KEYWORD = 2.4


def keyword_loop():
    one = "".join(f'<span class="em">{escape(t)}</span>' if em else f"<span>{escape(t)}</span>" for t, em in KEYWORDS)
    dur = round(len(KEYWORDS) * SECONDS_PER_KEYWORD)
    return f'<div class="gv-loop-track" style="--gv-dur:{dur}s">{one * 3}</div>'


def contact_for(mode):
    c = partial("contact.html")
    c = re.sub(r'<div class="gv-loop-track">.*?</div>', lambda m: keyword_loop(), c, flags=re.S)
    if mode == "creator":
        c = c.replace('class="gv-tabbtn gv-on" data-aud="brand" aria-selected="true"', 'class="gv-tabbtn" data-aud="brand" aria-selected="false"')
        c = c.replace('class="gv-tabbtn" data-aud="creator" aria-selected="false"', 'class="gv-tabbtn gv-on" data-aud="creator" aria-selected="true"')
        c = c.replace('data-gv-panel="brand" class="scroll-mt-28">', 'data-gv-panel="brand" class="scroll-mt-28" hidden>')
        c = c.replace('data-gv-panel="creator" class="scroll-mt-28" hidden>', 'data-gv-panel="creator" class="scroll-mt-28">')
    return c


COPY_SCRIPT = '''    <script>
        document.getElementById('copy-email').addEventListener('click', function () {
            var email = 'mustafa@gratovo.com';
            var status = document.getElementById('copy-email-status');
            var icon = document.getElementById('copy-email-icon');
            function done(ok) {
                status.textContent = ok ? 'Copied!' : 'Press Ctrl+C to copy';
                if (ok) icon.textContent = 'check';
                setTimeout(function () { status.textContent = ''; icon.textContent = 'content_copy'; }, 2500);
            }
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(email).then(function () { done(true); }, function () { done(false); });
            } else {
                done(false);
            }
        });
    </script>
'''


# ------------------------------------------------------------------ SEO page templates (landing pages, guides, hub)
def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def render_blocks(blocks):
    out, toc = [], []
    for b in blocks:
        k = b[0]
        if k == "h2":
            i = slugify(b[1])
            toc.append((i, b[1]))
            out.append(f'<h2 id="{i}">{b[1]}</h2>')
        elif k == "h3":
            out.append(f"<h3>{b[1]}</h3>")
        elif k == "p":
            out.append(f"<p>{b[1]}</p>")
        elif k in ("ul", "ol"):
            out.append(f"<{k}>" + "".join(f"<li>{x}</li>" for x in b[1]) + f"</{k}>")
        elif k == "note":
            out.append(f'<div class="note">{b[1]}</div>')
    return "\n                ".join(out), toc


def crumbs_html(items, dark=False):
    lis = "".join((f'<li><a href="{h}">{escape(n)}</a></li>' if h else f'<li aria-current="page">{escape(n)}</li>') for n, h in items)
    return f'<nav class="crumbs{" crumbs-dark" if dark else ""}" aria-label="Breadcrumb"><ol>{lis}</ol></nav>'


def faq_band(items, aud):
    return f"""<!-- FAQ -->
        <section id="faq" class="bg-band border-y border-line py-section scroll-mt-24" aria-label="Frequently asked questions">
            <div class="max-w-container-max mx-auto px-grid-gutter grid grid-cols-1 md:grid-cols-[minmax(0,1fr)_minmax(0,2.3fr)] gap-10 md:gap-16 items-start">
                <div>
                    <p class="font-display text-label uppercase text-brand-deep mb-3">FAQs</p>
                    <h2 class="font-display text-h2 text-ink">Still Have Questions?</h2>
                </div>
                <div data-faq-panel="{aud}" role="region" aria-label="Frequently asked questions" class="faq-list">
                    {faq_items(aud[0], items)}
                </div>
            </div>
        </section>

        """


def landing_main(p):
    d = p["data"]
    aud = d["aud"]
    parent = ("For brands", "brands.html") if aud == "brand" else ("For creators", "creators.html")
    crumbs = [("Home", "index.html"), parent, (d["crumb"], None)]
    hero_html = f"""<!-- Hero -->
        <section class="relative bg-gradient-to-b from-brand-deep to-brand text-white">
            <div class="max-w-container-max mx-auto px-grid-gutter pt-8 pb-section">
                {crumbs_html(crumbs, True)}
                <div class="text-center max-w-4xl mx-auto mt-10">
                    <p class="tag mb-6">{escape(d["eyebrow"])}</p>
                    <h1 class="font-display text-h1 text-white">{escape(d["h1"])}</h1>
                    <p class="font-body text-lead text-white/90 mt-6 max-w-3xl mx-auto">{escape(d["lead"])}</p>
                    <div class="mt-10 flex flex-wrap justify-center gap-3"><a href="{d["cta_href"]}" class="btn btn-light">{escape(d["cta"])} {ARROW_ICON}</a></div>
                </div>
            </div>
        </section>

        """
    cards = "".join(
        f'<div class="bg-card border border-line rounded-card p-8 shadow-card relative"><div class="w-12 h-12 rounded-full bg-brand flex items-center justify-center text-white shadow-card mb-6">'
        f'<span class="material-symbols-outlined icon-fill text-2xl" aria-hidden="true">{ic}</span></div>'
        f'<h2 class="font-display text-h3 text-ink mb-3">{escape(t)}</h2><p class="font-body text-body text-muted">{escape(x)}</p></div>'
        for ic, t, x in d["cards"])
    cards_html = f"""<section class="pt-section"><div class="max-w-container-max mx-auto px-grid-gutter grid grid-cols-1 md:grid-cols-3 gap-8">{cards}</div></section>

        """
    body, _ = render_blocks(d["blocks"])
    prose = f"""<section class="pt-section"><div class="max-w-3xl mx-auto px-grid-gutter prose-gv">
                {body}
            </div></section>

        """
    stats = partial("vetting.html") if d.get("stats") else f'<div class="pb-section"></div>'
    res = resources_section(d["related"], "Keep Reading.")
    return (hero_html + cards_html + prose + stats + "\n        " + faq_band(d["faq"], aud) + res + contact_for(aud))


def date_label(iso):
    y, m, dd = (int(x) for x in iso.split("-"))
    return f"{date(y, m, dd).strftime('%B')} {dd}, {y}"


def article_main(p):
    d = p["data"]
    aud = d["aud"]
    body, toc = render_blocks(d["blocks"])
    words = len(re.sub(r"<[^>]+>", " ", body + " ".join(q + " " + a for q, a in d["faq"])).split())
    minutes = max(1, round(words / 210))
    crumbs = [("Home", "index.html"), ("Guides", "guides.html"), (d["crumb"], None)]
    take = "".join(f"<li>{escape(t)}</li>" for t in d["takeaways"])
    toc_html = "".join(f'<li><a href="#{i}">{escape(re.sub(r"<[^>]+>", "", t))}</a></li>' for i, t in toc)
    cta_text = ("Tell us what you sell. We find and check the creators, recommend one to three, and make the introduction. We reply within 24 hours."
                if aud == "brand" else "Send us your channel link and what you cover. We match you with AI and SaaS brands that fit, and you decide. We reply within 24 hours.")
    cta_label, cta_href = ("Find My Creators", "#workwithus") if aud == "brand" else ("Get Brand Deals", "#creators")
    rel = "".join(link_card(s) for s in d["related"])
    return f"""<!-- Guide -->
        <article>
            <header class="pt-8 pb-10">
                <div class="max-w-3xl mx-auto px-grid-gutter">
                    {crumbs_html(crumbs)}
                    <p class="font-display text-label uppercase text-brand-deep mt-10 mb-4">Guide</p>
                    <h1 class="font-display text-h1 text-ink">{escape(d["h1"])}</h1>
                    <p class="font-body text-lead text-muted mt-5">{escape(d["lead"])}</p>
                    <p class="font-body text-small text-muted mt-6">By the Gratovo team &middot; <time datetime="{SEO.DATE}">Updated {date_label(SEO.DATE)}</time> &middot; {minutes} min read</p>
                </div>
            </header>
            <div class="max-w-3xl mx-auto px-grid-gutter pb-section">
                <div class="takeaways"><p class="font-display text-label uppercase text-brand-deep mb-3">Key takeaways</p><ul>{take}</ul></div>
                <nav class="toc" aria-label="In this guide"><p class="font-display text-label uppercase text-ink mb-3">In this guide</p><ol>{toc_html}</ol></nav>
                <div class="prose-gv">
                {body}
                </div>
                <section id="faq" class="mt-14 scroll-mt-24" aria-label="Frequently asked questions">
                    <h2 class="font-display text-h2 text-ink mb-6">Frequently Asked Questions</h2>
                    <div data-faq-panel="{aud}" role="region" aria-label="Frequently asked questions" class="faq-list">
                        {faq_items(aud[0], d["faq"])}
                    </div>
                </section>
                <div class="cta-box mt-14"><h2 class="font-display text-h3 text-ink mb-2">Want us to do this for you?</h2><p class="font-body text-body text-muted mb-6">{cta_text}</p>
                    <a href="{cta_href}" class="btn btn-primary">{cta_label} {ARROW_ICON}</a></div>
            </div>
        </article>

        <section class="bg-band border-y border-line py-section" aria-label="Related guides">
            <div class="max-w-container-max mx-auto px-grid-gutter">
                <h2 class="font-display text-h2 text-ink text-center mb-12">Keep Reading.</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8">{rel}</div>
            </div>
        </section>

        {contact_for(aud)}"""


def hub_main(p):
    d = p["data"]
    crumbs = [("Home", "index.html"), ("Guides", None)]
    brand = ["ai-influencer-marketing-guide", "how-to-find-ai-youtubers-to-sponsor", "how-to-vet-ai-creators-before-sponsoring", "saas-influencer-marketing", "ai-youtube-sponsorships"]
    creator = ["how-ai-creators-get-brand-sponsorships", "ai-youtuber-brand-deals"]
    g = lambda ss: "".join(link_card(s) for s in ss)
    return f"""<header class="pt-8 pb-12">
            <div class="max-w-container-max mx-auto px-grid-gutter">
                {crumbs_html(crumbs)}
                <div class="text-center max-w-3xl mx-auto mt-10">
                    <p class="font-display text-label uppercase text-brand-deep mb-4">Guides</p>
                    <h1 class="font-display text-h1 text-ink">{escape(d["h1"])}</h1>
                    <p class="font-body text-lead text-muted mt-5">{escape(d["lead"])}</p>
                </div>
            </div>
        </header>
        <section class="pb-section"><div class="max-w-container-max mx-auto px-grid-gutter">
            <h2 class="font-display text-h2 text-ink mb-8">For Brands</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">{g(brand)}</div>
            <h2 class="font-display text-h2 text-ink mt-16 mb-8">For Creators</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">{g(creator)}</div>
        </div></section>

        {contact_for("brand")}"""


# ------------------------------------------------------------------ assemble + write
def assemble(p, main, with_contact=True, base=False):
    aud = "creator" if p["mode"] == "creator" else "brand"
    scripts = COPY_SCRIPT if with_contact else ""   # the site's own scripts are one deferred bundle, linked in <head>
    return (head(p, base) +
            f'\n<body class="bg-canvas text-ink font-body text-body min-h-screen flex flex-col" data-audience="{aud}" data-page="{p["mode"]}">\n'
            f'    {site_header(p["nav"], hide=(p["kind"] == "core" and not p.get("noindex")))}\n    <main class="flex-grow">\n        {main}\n    </main>\n    {footer()}\n'
            f'{scripts}</body>\n\n</html>\n')


def legal_main(p):
    d = p["data"]
    secs = "".join(f'<section><h2>{escape(h)}</h2>' + "".join(f"<p>{escape(t)}</p>" for t in body) + "</section>" for h, body in d["sections"])
    return f"""<section class="max-w-3xl mx-auto px-grid-gutter py-section">
            <h1 class="font-display text-h1 text-ink mb-10 pb-6 border-b border-line">{escape(d["title"])}</h1>
            <div class="prose-gv">{secs}</div>
        </section>"""


def core_main(p):
    mode = p["mode"]
    features = partial("features.html")
    parts = [hero(mode)]
    if mode == "creator":
        parts.append(creator_section())
    elif mode == "both":
        # brand-only: the vetting standards hide when "I'm a creator" is picked (js/audience-tabs.js)
        parts += [benefits_tabbed(features), '<div data-aud-only="brand">' + partial("vetting.html") + '</div>']
    else:
        parts += [features, partial("vetting.html")]
    parts.append(process_section(mode))
    parts.append(faq_section(mode))
    parts.append(resources_section(RESOURCES[mode], all_link=(mode == "both")))
    parts.append(contact_for(mode))
    return "\n        ".join(s.strip("\n") + "\n" for s in parts)


LOCAL_PHOTO = re.compile(r"https://images\.unsplash\.com/photo-(\d+-[0-9a-f]+)\?[^\"'\s]*")
KEEP = re.compile(r"(<script\b.*?</script>|<style\b.*?</style>|<pre\b.*?</pre>|<textarea\b.*?</textarea>)", re.S | re.I)


def optimise(html):
    """Smaller HTML: card photos come from our own server (images/cards/*.webp), no comments, no indentation."""
    html = LOCAL_PHOTO.sub(lambda m: f"images/cards/{m.group(1)}.webp", html)
    out = []
    for i, seg in enumerate(KEEP.split(html)):
        if i % 2 == 0:                                   # not inside <script>, <style>, <pre>, <textarea>
            seg = re.sub(r"<!--(?!\[if).*?-->", "", seg, flags=re.S)
            seg = re.sub(r"\n[ \t]+", "\n", seg)
            seg = re.sub(r"[ \t]+\n", "\n", seg)
            seg = re.sub(r"\n{2,}", "\n", seg)
        out.append(seg)
    return "".join(out)


def build(name, p):
    kind = p["kind"]
    main = {"core": core_main, "landing": landing_main, "article": article_main, "hub": hub_main, "legal": legal_main}[kind](p)
    html = assemble(p, main, with_contact=(kind != "legal"))
    if kind == "legal":                      # no contact form on these pages: the header's phone button goes to the home page's
        html = html.replace('href="#contact-card"', 'href="index.html#contact-card"')
    html = optimise(html)
    (ROOT / name).write_text(html, encoding="utf-8")
    print("wrote", name, len(html))
    return html


# ------------------------------------------------------------------ generated support files
def lastmod_for(name, html, cache):
    h = hashlib.sha1(html.encode("utf-8")).hexdigest()
    e = cache.get(name)
    if not e or e["hash"] != h:
        e = {"hash": h, "date": TODAY}
        cache[name] = e
    return e["date"]


def write_support(pages_html):
    cache_f = ROOT / "research" / ".cache" / "lastmod.json"
    cache_f.parent.mkdir(parents=True, exist_ok=True)
    cache = json.loads(cache_f.read_text(encoding="utf-8")) if cache_f.exists() else {}
    urls = []
    for name, html in pages_html.items():
        p = PAGES[name]
        if p.get("noindex"):
            continue
        urls.append((p["url"], lastmod_for(name, html, cache), p))
    cache_f.write_text(json.dumps(cache, indent=1), encoding="utf-8")
    pr = {"core": 0.9, "landing": 0.8, "hub": 0.7, "article": 0.7}
    rows = []
    for u, lm, p in urls:
        pri = 1.0 if p["slug"] == "home" else pr[p["kind"]]
        rows.append(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{lm}</lastmod>\n    <priority>{pri}</priority>\n  </url>")
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /research/\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    manifest = {"name": "Gratovo", "short_name": "Gratovo", "description": "AI influencer marketing for AI and SaaS brands and creators.",
                "start_url": "/", "display": "browser", "background_color": "#ffffff", "theme_color": "#0072b8",
                "icons": [{"src": "/images/icon-192.png", "sizes": "192x192", "type": "image/png"},
                          {"src": "/images/icon-512.png", "sizes": "512x512", "type": "image/png"}]}
    (ROOT / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    # plain-language summary for AI assistants and answer engines (llms.txt convention)
    lines = ["# Gratovo", "",
             "> Gratovo is an influencer marketing broker for AI and SaaS. We connect AI and SaaS brands with vetted creators, and creators with brand deals that fit. We recommend one to three creators per product, make the introduction, and take care of the contract, script and posting date. Brands approve the video before it goes live. We reply within 24 hours.", "",
             "Gratovo works with real creators on YouTube, LinkedIn, X and newsletters. This is not about AI-generated influencers.", "",
             "## Main pages", f"- [Home]({SITE}/): what Gratovo does for brands and creators",
             f"- [For brands]({SITE}/brands.html): vetted AI creators for your product", f"- [For creators]({SITE}/creators.html): brand deals that fit your channel", "",
             "## Guides and service pages"]
    for s in FOOTER_RES:
        lines.append(f"- [{CARD_COPY[s][1]}]({SITE}/{s}.html): {CARD_COPY[s][2]}")
    lines += ["", "## Vetting standards", "- 30K+ average views per video", "- 3-8% real engagement from active viewers", "- 35%+ of the audience in the brand's target country", "",
              "## Contact", "- Email: mustafa@gratovo.com", ""]
    (ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")
    # 404 (GitHub Pages serves it for any unknown URL; <base href="/"> keeps the assets working at any depth)
    p404 = dict(mode="both", slug="404", kind="core", nav="", url=f"{SITE}/404.html", noindex=True, robots="noindex, follow",
                title="Page not found | Gratovo", desc="This page does not exist. Head back to the Gratovo home page.")
    main404 = """<section class="py-section"><div class="max-w-3xl mx-auto px-grid-gutter text-center">
            <p class="font-display text-label uppercase text-brand-deep mb-4">404</p>
            <h1 class="font-display text-h1 text-ink">That Page Does Not Exist.</h1>
            <p class="font-body text-lead text-muted mt-5">The link may be old or mistyped. Try one of these instead.</p>
            <div class="mt-10 flex flex-wrap justify-center gap-3"><a href="index.html" class="btn btn-primary">Home</a><a href="brands.html" class="btn btn-light">For Brands</a><a href="creators.html" class="btn btn-light">For Creators</a><a href="guides.html" class="btn btn-light">Guides</a></div>
        </div></section>"""
    (ROOT / "404.html").write_text(optimise(assemble(p404, main404, with_contact=False, base=True).replace('href="#contact-card"', 'href="index.html#contact-card"')), encoding="utf-8")
    # og image jobs for research/scripts/build-og.py
    jobs = [dict(slug=p["slug"], title=(HERO[p["mode"]]["tag"] if p["kind"] == "core" else p["data"]["h1"]),
                 kicker=("AI influencer marketing" if p["slug"] == "home" else {"core": "Gratovo", "landing": "Gratovo", "article": "Guide", "hub": "Guides"}[p["kind"]]))
            for p in PAGES.values() if not p.get("noindex")]
    (ROOT / "research" / ".cache" / "og-pages.json").write_text(json.dumps(jobs, indent=1), encoding="utf-8")
    print("wrote sitemap.xml robots.txt manifest.webmanifest llms.txt 404.html", len(urls), "urls")


if __name__ == "__main__":
    out = {n: build(n, p) for n, p in PAGES.items()}
    write_support(out)
