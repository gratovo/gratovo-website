# How the competitor sites look and behave (visual + animation research)

Captured 2026-10-08 by loading each site in headless Edge via Playwright (`scripts/capture-site.py`), scrolling it with the mouse wheel in 800px steps, and probing the live page for animations and libraries.
Screenshots: `competitor-screenshots/<site>/step-NN.jpg` (desktop 1440x900, one per scroll stop) and `probe.json` (scripts loaded, live CSS animations, libraries).

**Limits:** these are still screenshots at scroll stops, not video. Animation *names* and timings come from the code and the live-animation probe; I have not watched them move. Hover effects are known only where the code or a screenshot caught them. Do not refetch: read this file and the screenshots.
Earlier, `competitor-fetch-raw.md` could not cover scalepledge.com, smoothmedia.co or adhesivemedia.com. They are covered here.

## Quick comparison

| Site | Look | Hero effect | Scroll / hover effects | Built with |
|---|---|---|---|---|
| Attrakt | Near-black, grainy texture, dark red accent, outlined buttons | Loading-bar preloader, then textured hero, "scroll down" cue with a growing line | AOS fade-ups, Slick carousels, creator grid where hover blurs the tile and shows subscribers / channel views / average views, "services" panels animate in step by step, back-to-top button | AOS, Slick, jQuery |
| Creator Authority | Flat teal and navy, rounded pill buttons, very plain | None. Static hero with logo and one button | Infinite logo marquee only (CSS scroll-left / scroll-right) | Astro (Hostinger builder), no JS libraries |
| Scale Pledge | Off-white with one electric blue, big tight Inter headlines, white cards with blue top border | Blue line chart draws itself across the hero (CSS `growth-line-draw`), stage labels Discover, Vet, Negotiate, Activate sit along the line | Sections fade in on scroll ("reveal"), accordion rows (+ toggle) for services, tabbed carousel, step-by-step carousel with arrows and "1 of 6", FAQ accordion, blog cards, sticky blurred nav | Next.js, pure CSS and small custom JS, no animation library |
| Nsentive | Black then olive green, big plain sans, rounded outlined cards | Dictionary-style hero: "nsentivize /pronunciation/ verb" fading in line by line | Rounded outline cards with icons, thin-ruled rows with a diagonal arrow, a looping word list (`scrollUp`) beside the contact form, form on olive | WordPress, jQuery |
| Apollo | Deep navy "space", glassy cards, purple glow, serif display type | Starfield with shooting stars, big logo, two glass cards (creators / brands) with floating creator chips and orbiting brand logos | Floating chips (`apollo-float-a/b/c`), orbit rings (`orbit-spin/counter/pulse`), shimmering beams, marquees, scroll-driven animation, video panel with pause button, huge ghost number behind the stats, gradient headline text | Webflow, jQuery, custom CSS |
| Right Click | Pure black with yellow, ultra-condensed all-caps headline, monospaced body, purple accent | Giant headline with tilted photo cards floating around it, custom purple circle cursor | Scroll-progress counter down the left edge (0 to 100), pill buttons with arrows, rounded yellow-outlined panels | Webflow (interactions), jQuery |
| Smooth | Soft lilac and cream, big editorial serif headline, bold script logo | Full-bleed podcast video with a purple tint, a hand-drawn ellipse around the word "knowledge", bobbing down arrow | Pill-shaped category cloud ("Categories we cover"), phone-style video cards, 3D tilt and sticky sections, custom cursor | Framer |
| MindShare | Orange and charcoal in alternating bands, giant heavy condensed type | Huge black wordmark filling the screen, bracketed tagline, two pill buttons, logo ticker along the bottom edge | Sections fade up on scroll (`fadeUp`), logo ticker (`ticker`), small vertical side label ("FOR CREATORS"), orange pill tags, toasts | React single-page app, custom CSS |
| Adhesive Media | White, one royal blue accent, plain bold sans | Navy preloader that draws the logo as a thin line, then a light hero | Horizontal carousel of small animated diagrams (nodes joined by lines, "Deal accepted"), category tabs with icons, ticker, video, review widget | Webflow, React, custom CSS |

## What is worth borrowing for Gratovo (effects that need no proof)

1. **Hero line that draws itself with the steps on it (Scale Pledge).** Directly shows "how it works" in the hero. Pure CSS, tiny, fits a tech audience.
2. **Step-by-step stepper with arrows and "1 of N" (Scale Pledge).** Turns the process into something to click through instead of read.
3. **Accordion FAQ and `details` rows (Scale Pledge).** Answers cost and "can't we do this ourselves?" without length.
4. **Hover-to-reveal creator tile with stats (Attrakt).** An honest way to show what a shortlist looks like, using clearly labeled example data.
5. **Scroll fade-up on every section (Scale Pledge, MindShare, Attrakt).** Cheap, expected, makes the page feel finished.
6. **Giant headline and alternating colour bands (MindShare, Right Click).** Strong first impression, almost no content needed.
7. **Floating cards around the hero (Apollo, Right Click).** Can be built from Gratovo's own vetting numbers instead of photos.
8. **Logo/ticker strip (Creator Authority, MindShare, Apollo).** Only usable with something true to put in it: platforms (YouTube, LinkedIn, X, newsletters) rather than client logos.

## What not to copy

- Client logo walls, testimonials, creator rosters with real names, stat counters of campaigns or views. Gratovo has no results to show yet.
- Preloaders (Attrakt, Adhesive). They delay the first screen. A visitor deciding fast does not benefit.
- Custom cursors (Right Click, Smooth, MindShare). They look distinctive but add friction on touch devices and for accessibility.
- (Correction) Do NOT treat speaking to both brands and creators as a weakness. Gratovo brokers both sides, and 8 of the 9 competitors address both (two hero buttons, For Brands / For Creators sections, a form for each). Copy that dual structure.

## Per-site notes

### Attrakt (attraktmedia.com)
Preloader is a thin red progress bar on black. Hero: dark grainy texture, left-aligned dark-red headline, two outlined buttons. Hamburger "MENU" top right opens a full menu. Fixed LinkedIn icon on the right edge. Page height about 10,500px. Creator roster is a 3-column grid of square avatars with a dark hover overlay. Libraries found: AOS (`data-aos` on many elements), Slick, jQuery; `servicesPanelIn` and `servicesStepIn` animations run as the services block enters. Autoplay video present.

### Creator Authority (creatorauthority.com)
Shortest page, about 3,350px. Teal hero with big logo, headline and one dark pill button. "Trusted By Amazing Brands" logo strip scrolls continuously. Contact section is two white cards with hard offset shadows and tick-bullets (For Brands / For Creators), each with a dark pill button. Footer shows a LinkedIn Marketing Partner badge.

### Scale Pledge (scalepledge.com) - the closest match to Gratovo's idea
Describes itself as a "tech influencer marketing agency" for tech brands, and its hero line chart carries the process stages. Section order (about 8,100px): sticky nav with blue "Plan a Campaign" button; hero (eyebrow, huge headline, short paragraph, blue primary + black "See how it works" buttons, drawing line chart); two cards ("The buying journey" / "Our role"); "What we do" accordion of six numbered rows; "Built for tech" tabbed carousel (4 categories); "The principle" with research accordions linking to studies; "How it works" six-step carousel; "Why Scale Pledge" pledge card; three blog cards; FAQ accordion (four questions); closing card with one button; dark footer. Cookie banner bottom right. CTA is a `mailto:` link, not a form. Page root has `data-motion="full"` and sections carry a `reveal` class for scroll fade-in. Design tokens seen in the code: blue `#1446e5`, ink `#121212`, background `#f6f9ff`, 16px radius, heading letter-spacing -0.07em.

### Nsentive (nsentive.com)
Black hero with a large olive "n." logo, a dictionary-style definition, and an olive "Let's Talk" pill. Three outlined rounded cards with icons sit directly under the hero. Lower sections are white with thin horizontal rules and large left-aligned words (Creators, Brands, Business) with a diagonal arrow on the right. Contact area is an olive full-bleed block with a black rounded form card centered, flanked by a looping word list (negotiation, networking, nurturing...) and Instagram / LinkedIn icons. Form reassurance line: "We respect your privacy... No funny business."

### Apollo (apollomgmt.co)
Space theme throughout. Pill-shaped floating nav with a count badge on "Careers". Hero is a giant logo over drifting stars and shooting stars, then a split of two big glass cards. A looping video panel has a pause button. "Who We Are" has a glowing app-icon logo over a faint grid. Stats show three numbers over a huge faint "140M". Brands section is a glowing panel with gradient headline and a 2x3 grid of brand tiles. Page height about 12,600px. Webflow, jQuery, many `apollo-*` CSS animations, `animation-timeline` (scroll-driven), `backdrop-filter` glass.

### Right Click (rightclick.gg)
Black with yellow. Centered tiny spaced logo, yellow "WORK WITH US" pill and a menu button top right. Hero headline in a very tall condensed typeface, with tilted rounded photo cards drifting around it. A thin yellow line down the left edge fills as you scroll, with "0" at the top and "100" at the bottom. Purple circle custom cursor. Panels are rounded with yellow outlines. Buttons are full-width yellow-outlined pills with arrows ("CREATORS ↗"). Webflow interactions. Page height about 5,000px.

### Smooth (smoothmedia.co)
"The knowledge creator company". Full-bleed looping video hero under a purple tint with a hand-drawn ellipse around "knowledge". Lilac and cream bands. Phone-shaped video cards with creator handles. A pill cloud "Categories we cover" (Tech, AI, Business, Design...). Section "The smooth approach" uses mixed serif and script type. Framer-built: heavy GPU transforms, 3D perspective, sticky sections, hidden system cursor.

### MindShare (mindsharemedia.live)
Orange hero with a wordmark sized to fill the width, bracketed tagline, black pill "I'M A BRAND →" and outlined "I'M A CREATOR", and a logo ticker at the bottom edge. Then charcoal bands alternating with orange: "BRANDS THAT TRUST US" (four logos), "WE DON'T CHASE CLICKS" (white and orange condensed type, orange pill tags), "YOUR VOICE. YOUR VALUE.", and a final orange rounded card "LET'S BUILD SOMETHING REAL." Sections fade up as they enter. A vertical side label marks each audience section.

### Adhesive Media (adhesivemedia.com)
**Superseded by `adhesive-interactions.md`** (the site now has /brands and /creators pages, tabbed sections and Remotion-driven diagrams).
Logo-draw preloader on dark navy. Page height about 10,300px. White layout with a blue accent. "How it works" is a horizontal carousel of small animated diagrams (goal / audience / style nodes, "Deal accepted" with a check). "Categories" headline with blue highlighted phrase ("drive measurable results"), then icon tabs (Most popular, Automotive, Farming, Homesteading...). Contact button top right in solid blue.
