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
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PART = ROOT / "research" / "pages" / "partials"
SITE = "https://www.gratovo.com"


def partial(name):
    return (PART / name).read_text(encoding="utf-8").rstrip() + "\n"


BTN = ('class="bg-primary-container text-on-primary py-4 px-10 rounded-full font-label-sm uppercase text-base md:text-lg '
       'tracking-wider hover:bg-primary transition-colors shadow-lg hover:shadow-xl transform hover:-translate-y-1 duration-200 '
       'inline-flex items-center gap-2"')

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
    cta = []
    if mode in ("both", "brand"):
        cta.append(f'<a href="#workwithus" data-pc-cta="brand"><button type="button" {BTN}>Find My Creators <span class="material-symbols-outlined">arrow_forward</span></button></a>')
    if mode in ("both", "creator"):
        cta.append(f'<a href="#creators" data-pc-cta="creator"{" hidden" if both else ""}><button type="button" {BTN}>Get Brand Deals <span class="material-symbols-outlined">arrow_forward</span></button></a>')
    return f'''<!-- How it works (animated{", tabbed by audience" if both else ""}) -->
        <section id="how-it-works" class="pc-section scroll-mt-20" aria-label="How it works">
            <div class="pc-dots" aria-hidden="true"></div>
            <div class="pc-wrap">
                <div class="pc-head">
                    <p class="pc-eyebrow font-label-sm text-label-sm">How it works</p>
                    <h2 class="font-headline-lg text-headline-md md:text-headline-lg mb-4 leading-tight text-white">Start With a Message. <span class="pc-grad">Scale What Works.</span></h2>
                    <p class="pc-sub font-body-lg text-body-lg">{sub}</p>
                    {tabs}
                </div>
                <div class="pc-panels">
                    {chr(10).join("                    " + p if k else p for k, p in enumerate(panels))}
                </div>
                <div class="pc-controls">
                    <button type="button" class="pc-arrow pc-prev" aria-label="Previous steps" disabled>{ARROW_L}</button>
                    <button type="button" class="pc-arrow pc-next" aria-label="Next steps">{ARROW_R}</button>
                </div>
                <div class="pc-cta">
                    {chr(10).join("                    " + c if k else c for k, c in enumerate(cta))}
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
        <section id="faq" class="bg-surface-container-low border-y border-outline-variant py-20 md:py-24 scroll-mt-20" aria-label="Frequently asked questions">
            <div class="max-w-container-max mx-auto px-grid-gutter grid grid-cols-1 md:grid-cols-[minmax(0,1fr)_minmax(0,2.3fr)] gap-10 md:gap-16 items-start">
                <div>
                    <p class="font-label-sm text-label-sm uppercase tracking-widest text-primary mb-3">FAQs</p>
                    <h2 class="font-headline-lg text-headline-md md:text-headline-lg text-on-background leading-tight">Still Have Questions?</h2>
                </div>
                <div>
                    {tabs}
                    {chr(10).join("                    " + p if k else p for k, p in enumerate(panels))}
                </div>
            </div>
        </section>

        '''


def faq_ld(mode):
    data = (BRAND_FAQ if mode in ("both", "brand") else []) + (CREATOR_FAQ if mode in ("both", "creator") else [])
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in data]}
    return '<script type="application/ld+json" id="faq-ld">\n    ' + json.dumps(ld, indent=2, ensure_ascii=False).replace("\n", "\n    ") + "\n    </script>"


# ------------------------------------------------------------------ hero (MindShare-style) + header
TICKER = "".join(f'<span class="ms text-4xl md:text-5xl text-white/85">{p}</span>'
                 for _ in range(6) for p in ("YouTube", "LinkedIn", "X", "Newsletters"))

PILL_DARK = 'class="pill bg-white text-primary shadow-lg hover:bg-primary-fixed"'
PILL_LINE = 'class="pill border-2 border-white text-white hover:bg-white/15"'

HERO = {
    "both": dict(eyebrow="", tag="[ Connecting AI Brands With the Creators Their Customers Trust. ]",
                 b1=('brands.html', "I'm a Brand &rarr;"), b2=('creators.html', "I'm a Creator")),
    "brand": dict(eyebrow="For brands", tag="[ Vetted AI creators for your product. No cold outreach. ]",
                  b1=('#workwithus', "Find My Creators &rarr;"), b2=('#how-it-works', "How It Works")),
    "creator": dict(eyebrow="For creators", tag="[ Brand deals that fit your channel. Brought to you. ]",
                    b1=('#creators', "Get Brand Deals &rarr;"), b2=('#how-it-works', "How It Works")),
}


def site_header(mode):
    """Sticky top bar (direct child of <body>, so it stays visible on every section and over the footer)."""
    cur = " border-b-2 border-white"
    cur_h = cur if mode == "both" else ""
    cur_b = cur if mode == "brand" else ""
    cur_c = cur if mode == "creator" else ""
    return f'''<header class="sticky top-0 z-50 bg-primary text-white border-b border-white/20 shadow-md">
        <div class="flex items-center justify-between gap-2 px-4 md:px-10 h-20">
            <a href="index.html" class="bg-white rounded-xl px-2.5 sm:px-3 py-1 shrink-0" aria-label="Gratovo home"><span class="wordmark text-xl sm:text-2xl" role="img" aria-label="Gratovo"><img src="images/logo-mark.svg" alt=""><span aria-hidden="true">ratovo</span></span></a>
            <nav class="flex items-center gap-3 sm:gap-6 text-[10px] sm:text-xs tracking-wider sm:tracking-widest uppercase font-semibold" aria-label="Main">
                <a class="inline-flex items-center gap-1 py-1{cur_h}" href="index.html" aria-label="Home"><span class="material-symbols-outlined icon-fill text-lg sm:text-base" aria-hidden="true">home</span><span class="hidden sm:inline">Home</span></a>
                <a class="py-1{cur_b}" href="brands.html"><span class="hidden sm:inline">For </span>brands</a>
                <a class="py-1{cur_c}" href="creators.html"><span class="hidden sm:inline">For </span>creators</a>
                <a href="#contact-card" aria-label="Contact us" title="Contact us" class="bg-white text-primary rounded-full w-10 h-10 sm:w-11 sm:h-11 inline-flex items-center justify-center text-lg sm:text-xl leading-none hover:bg-primary-fixed transition-colors"><span aria-hidden="true">&#128222;</span></a>
            </nav>
        </div>
    </header>
    '''


def hero(mode):
    h = HERO[mode]
    eyebrow = f'<p class="tag mb-6">{h["eyebrow"]}</p>' if h["eyebrow"] else ""
    return f'''<!-- Hero (MindShare-style, white on brand blue for contrast) -->
        <section class="relative bg-gradient-to-br from-primary-container to-primary text-white min-h-[calc(100vh-5rem)] flex flex-col">
            <div class="flex-1 flex flex-col items-center justify-center text-center px-6 py-10">
                {eyebrow}
                <h1><span class="ms block text-[clamp(4.5rem,17vw,15rem)] text-white">Gratovo</span>
                    <span class="mt-6 block text-lg font-medium text-white/95">{h["tag"]}</span></h1>
                <div class="mt-8 flex flex-wrap justify-center gap-3"><a href="{h["b1"][0]}" {PILL_DARK}>{h["b1"][1]}</a><a href="{h["b2"][0]}" {PILL_LINE}>{h["b2"][1]}</a></div>
            </div>
            <div class="ticker marquee py-6 border-t border-white/25" aria-hidden="true"><div class="marquee-track">{TICKER}</div></div>
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
CARD = ('<div class="bg-surface-container-lowest border border-outline-variant rounded-2xl overflow-hidden flex flex-col group hover:-translate-y-2 hover:shadow-xl shadow-md transition-all duration-300">'
        '<div class="h-48 bg-cover bg-center" style="background-image:url({img})" role="img" aria-label="{alt}"></div>'
        '<div class="p-8 flex flex-col items-start flex-grow relative"><div class="w-12 h-12 rounded-full bg-primary-container flex items-center justify-center text-on-primary absolute -top-6 right-8 shadow-lg">'
        '<span class="material-symbols-outlined icon-fill text-2xl">{ic}</span></div>'
        '<h3 class="font-headline-md text-headline-md text-on-background mb-4">{t}</h3><p class="font-body-md text-body-md text-secondary">{d}</p></div></div>')


def creator_block():
    cards = "".join(CARD.format(ic=ic, t=t, d=d, img=img.replace("&", "&amp;"), alt=alt) for ic, t, d, img, alt in CREATOR_CARDS)
    return f'''<div class="text-center max-w-3xl mx-auto mb-12">
                    <h2 class="font-headline-lg text-headline-md md:text-headline-lg text-on-background mb-4 leading-tight">Brand Deals That Fit Your Channel.</h2>
                    <p class="font-body-lg text-body-lg text-secondary">Already making content about AI and software? We put you in front of the brands that fit your audience.</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">{cards}</div>
                <div class="text-center"><a href="#creators"><button {BTN}>Get Brand Deals <span class="material-symbols-outlined">arrow_forward</span></button></a></div>'''


def creator_section():
    """creators.html: the creator cards sit where the brand cards sit on brands.html."""
    return f'''<!-- Creator benefits -->
        <section id="for-creators" class="w-full mt-20 mb-24 relative z-20 scroll-mt-24">
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
        <section id="benefits" class="w-full mt-20 mb-24 relative z-20 scroll-mt-24" aria-label="Why Gratovo">
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
    link = 'class="font-label-sm text-label-sm uppercase text-secondary hover:text-primary transition-colors opacity-80 hover:opacity-100"'
    return f'''<!-- Footer -->
    <footer class="bg-surface py-12 border-t border-outline-variant">
        <div
            class="max-w-container-max mx-auto px-grid-gutter flex flex-col md:flex-row justify-between items-center gap-8">
            <div class="flex flex-col items-center md:items-start gap-4">
                <p class="font-label-sm text-label-sm uppercase text-secondary">&copy; 2026 Gratovo. Connecting AI brands
                    with the right creators.</p>
            </div>
            <nav class="flex flex-wrap justify-center gap-6" aria-label="Footer">
                <a {link} href="index.html">Home</a>
                <a {link} href="brands.html">For Brands</a>
                <a {link} href="creators.html">For Creators</a>
                <a {link} href="privacy-policy.html">Privacy Policy</a>
                <a {link} href="terms-of-service.html">Terms of Service</a>
            </nav>
        </div>
    </footer>
'''


PAGES = {
    "index.html": dict(
        mode="both", url=f"{SITE}/",
        title="AI Influencer Marketing for SaaS & AI Brands | Gratovo",
        desc="We connect AI and SaaS brands with vetted creators, and creators with brand deals that fit. We make the introductions and take care of contracts and posting."),
    "brands.html": dict(
        mode="brand", url=f"{SITE}/brands.html",
        title="Find Vetted AI Creators for Your Product | Gratovo",
        desc="Get 1 to 3 vetted AI creators picked for your product. We make the introduction and take care of contracts and posting, and you approve the video before it goes live."),
    "creators.html": dict(
        mode="creator", url=f"{SITE}/creators.html",
        title="Brand Deals for AI and Tech Creators | Gratovo",
        desc="Already making content about AI and software? Gratovo puts you in front of AI and SaaS brands that fit your audience. One contact, no cold outreach."),
}


def head(p):
    t, d, u = escape(p["title"], quote=True).replace("&amp;", "&"), p["desc"], p["url"]
    org = json.dumps({"@context": "https://schema.org", "@type": "Organization", "name": "Gratovo", "url": f"{SITE}/",
                      "logo": f"{SITE}/images/full-logo.png",
                      "description": "Gratovo connects AI and SaaS brands with vetted creators, and creators with brand deals that fit."},
                     indent=2)
    org = "\n    ".join(org.split("\n"))
    return f'''<!DOCTYPE html>
<html class="light" lang="en">

<head>
    <meta charset="utf-8">
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <link rel="icon" type="image/svg+xml" href="images/logo.svg">
    <title>{t}</title>
    <meta name="description" content="{d}">
    <meta name="keywords"
        content="AI influencer marketing, AI creator sponsorships, SaaS influencer marketing, AI YouTube sponsorships, find AI influencers, tech creator partnerships">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{u}">

    <meta property="og:type" content="website">
    <meta property="og:url" content="{u}">
    <meta property="og:title" content="{t}">
    <meta property="og:description" content="{d}">
    <meta property="og:image" content="{SITE}/images/full-logo.png">

    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="{u}">
    <meta property="twitter:title" content="{t}">
    <meta property="twitter:description" content="{d}">
    <meta property="twitter:image" content="{SITE}/images/full-logo.png">

    <!-- Structured Data for SEO -->
    <script type="application/ld+json">
    {org}
    </script>
    {faq_ld(p["mode"])}
    <link rel="preload" href="fonts/plus-jakarta-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="fonts/source-sans-3-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="fonts/jetbrains-mono-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="fonts/anton-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="fonts/material-symbols-subset.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="fonts/fonts.css">
    <link rel="stylesheet" href="css/tailwind.css">
    <link rel="stylesheet" href="css/hero.css">
    <link rel="stylesheet" href="css/process-cards.css">
</head>
'''


def contact_for(mode):
    c = partial("contact.html")
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


def build(name, p):
    mode = p["mode"]
    features = partial("features.html").replace("mt-8 md:-mt-16 mb-24", "mt-20 mb-24")
    parts = [hero(mode)]
    if mode == "creator":
        parts.append(creator_section())
    elif mode == "both":
        parts += [benefits_tabbed(features), partial("vetting.html")]
    else:
        parts += [features, partial("vetting.html")]
    parts.append(process_section(mode))
    parts.append(faq_section(mode))
    parts.append(contact_for(mode))
    aud = "creator" if mode == "creator" else "brand"
    main = "\n        ".join(s.strip("\n") + "\n" for s in parts)
    html = (head(p) +
            f'\n<body class="bg-background text-on-background font-body-md min-h-screen flex flex-col" data-audience="{aud}" data-page="{mode}">\n'
            f'    {site_header(mode)}\n    <main class="flex-grow">\n        {main}\n    </main>\n    {footer()}\n'
            f'{COPY_SCRIPT}    <script src="js/audience-tabs.js"></script>\n    <script src="js/process-cards.js"></script>\n</body>\n\n</html>\n')
    (ROOT / name).write_text(html, encoding="utf-8")
    print("wrote", name, len(html))


if __name__ == "__main__":
    for n, p in PAGES.items():
        build(n, p)
