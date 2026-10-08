# Adhesive Media (adhesivemedia.com): how its interactions actually work

Studied 2026-10-08 with Playwright (Edge): scroll captures, frame-by-frame recordings of every click, the live DOM and CSS, and the site's own JavaScript bundles (read for logic only; nothing was copied). Raw captures are in `adhesive-deep/` (section screenshots of all three pages, entrance frames, and `toggle/` click-by-click frames). Scripts: `scripts/adhesive-deep.py`, `adhesive-dom.py`, `adhesive-carousel.py`, `adhesive-toggle.py`. Their JavaScript bundles were read to learn the logic but are deliberately **not** saved in the repo (third-party source, and this repo is public); everything needed from them is written down in section 4. **Do not refetch; read this file and `adhesive-deep/`.**

Note: the site changed since the first capture in `competitor-effects.md`. It now has separate `/brands` and `/creators` pages, a tabbed "How We Work" section and a multi-step contact form.

## 1. Site structure (the audience split)

| Where | What the visitor sees |
|---|---|
| Home hero | Looping video, headline, two **split buttons**: `I'm a Creator` (solid blue) and `I'm a Brand` (white). Logo marquee under the hero. Nav also has `For Brands`, `For Creators`, `Contact`. |
| `/brands` | Own dark hero ("Engagement That Converts Starts Here."), floating "tape" stat tags ($30M+ deployed, 250+ creators, 0% brand churn), results carousel, **dark "Launch in Days. Scale in Weeks." step section**, curated-roster section, FAQ for brands. |
| `/creators` | Own hero ("Got a YouTube Channel? Let's Get You a Deal!"), "We Land the Deal. You Focus on Creating." step section (creator version), services list, example sponsorships, FAQ for creators. |
| Home "How We Work" | **One section, two tabs** (`For Brands` / `For Creators`) that swap the whole row of step cards in place. |
| Home FAQ | Same tab pattern: `For Brands` / `For Creators` swap the question list. |
| Footer "Let's Talk" | One shared multi-step form (button says `Next`). |

So the audience split is done three ways: separate pages (hero buttons), in-place tabs (sections), and one shared conversion form.

## 2. What happens on each click (recorded frame by frame)

### Hero split buttons (`I'm a Brand` / `I'm a Creator`)
- Plain links to `/brands` and `/creators` (client-side route change, no full reload).
- The new page's hero **builds in a staggered sequence**, about 0.1s apart: headline fades in line by line (last line in the blue accent), then the paragraph, then the two buttons, then the three stat "tapes" pop in one at a time, logo marquee already running.
- The nav underline moves to the active audience (`For Brands` / `For Creators`) and the nav turns from white to dark on the dark hero.
- Colour/tone changes per audience (brand page dark navy, creator page lighter), so the visitor feels they are in "their" part of the site.

### "How We Work" tabs (`For Brands` / `For Creators`)
1. **Sliding indicator.** One white pill sits behind the tab labels. On click it animates `left` and `width` to the new tab: **0.3s, `power2.inOut`** (GSAP). Width differs per tab (158px -> 169px), so it resizes while it slides. The active label turns dark; the inactive one stays grey. The word "Brands"/"Creators" inside each label is the accent blue.
2. **Cards swap in place.** The step row is re-rendered with the other audience's cards and `scrollLeft` is reset to 0.
3. **The reveal replays.** Every card starts at `opacity 0, y 50, scale .95` and animates to `1, 0, 1` in **0.7s, `power3.out`, stagger 0.08s**. The label "tape" on each card starts at `scaleX 0, rotate -6deg` (origin left centre) and draws on to `scaleX 1, rotate -2deg` in **0.5s, `back.out(1.7)`, stagger 0.08s, delay 0.25s**.
4. **Each card's diagram restarts from frame 0** (each is a fresh animated player).
5. First entry uses a ScrollTrigger (`start: top 75%`, once). After the first run, every tab change plays the same reveal immediately.
- Total felt time: roughly 0.8 to 1.2s from click to everything settled. It never feels like a page change, only like the content "re-dealing".

### FAQ tabs
Same sliding-pill indicator. The question list swaps, the first item resets closed. Accordion rows: a left blue rule appears on the open row, a chevron rotates, the answer height animates.

### Process carousel controls
- Cards are `350px` wide, `36px` gap, `scroll-snap-type: x mandatory`, horizontal scroll with hidden scrollbar.
- A **gradient mask fades the right edge** (`mask-image: linear-gradient(90deg, #000 calc(100% - 5.5rem), transparent)`); when scrolled to the end a class removes the mask.
- Round arrow buttons below (`3.25rem`) call `scrollBy({left: ±420, behavior: smooth})`. Previous is disabled (opacity .3) at the start; next is disabled at the end. Both update from the scroll event.
- A **dotted connector** (`2px dotted`, brand colour at 45%) sits between consecutive cards (`::after`, 1.5rem wide, vertically centred).
- On dark theme the section has a faint dot grid (`radial-gradient` dots every 40px at 4% white, masked to fade at the edges), the heading's last words use a blue gradient text, and card frames get a thin white 14% border.
- On phones: one card fills the width (`min(350px, 100vw - 2*padding)`), gap 1.5rem, tape shrinks (64x36).

## 3. The card layout

Each card: a "tape" label sticking out of the top-left corner (80x44, blue gradient, 3px white border, perforated side edges, icon inside, rotated -2deg) and a white framed card (1px grey border, 4px radius, 350px wide, aspect about 350/446). Inside: a light grey (`#f8f8f8`) header with the **title** (20px, weight 500), a **numbered blue circle** (28px) on the right, and a one or two line description (16px, grey), then the **animated diagram area** (520x480 stage, scaled to fit).

## 4. The animated diagrams ("the part that feels professional")

**They are not CSS animations.** Each diagram is a **Remotion Player** composition (the React video library): a fixed `520 x 480` stage, **30 fps**, `loop`, `autoPlay`, scaled down with a CSS transform (about 0.6). Every element's position/opacity/scale is computed from the **current frame number** with a few helpers, so the whole thing is deterministic and perfectly synchronised. This is why it looks tight: all timing is authored on one timeline, not scattered CSS delays.

Loaded lazily: the card shows a small blue spinner until the composition module arrives, then the card plays. The SFX `<audio>` tags are present but silent.

### The toolkit (these helpers are the "logic")
- `interp(frame, [start, end], easing)` = clamp((frame - start) / (end - start)) through an easing. The default easing is `inOut(quad)`.
- `lerp(a, b, t)`.
- Easings used: `out(cubic)` for almost everything that arrives; `inOut(cubic)` for fades and long moves; `out(back(1.05..1.3))` for pops that overshoot a hair; `linear` for spinners; `bezier(.32,0,.68,1)` for the scanning sweep.
- **Spring** (`damping 9, stiffness 118 to 130, mass .85 to .95`, `durationInFrames 12 to 20`): used for chips and icons popping in, `scale .6 -> 1` with opacity ramping 0 -> 1 over the first 20% of the spring. "Done" states (check marks) pop `1.1 -> 1`.
- **Sweep**: a vertical `linearGradient` band (stops at 24% / 54% / 76%, opacity 0 -> .95 -> 0, brand blue) whose `y1`/`y2` move down the stage over time. It is shown **through an SVG mask built from the lines and chip outlines** (white strokes on black). Result: a bright pulse that "runs along" the connection lines and around chip borders, not across the whole page. A second copy with `feGaussianBlur(stdDeviation 2.2)` at 35% opacity gives the glow.
- **Draw-on lines**: a line's end point is lerped from its start to its target (`out(cubic)`, 9 to 40 frames), so lines grow out of nodes. Lines are either solid 2px grey (`rgba(0,0,0,.1)`), dashed `5 6`, or dotted `1 7` with round caps.
- **Spinner to check**: a 22px gradient arc rotates `0 -> 720deg` linearly over about 40 to 90 frames, then at the moment it finishes it hides and a check mark springs in at `1.1 -> 1`. Used for "Collecting Data" and "Analyzing Results".
- **Text scramble reveal**: status text resolves left to right from deterministic random characters (`hash(frame, index)` picks from A-Z0-9), e.g. `MATCHING...` -> `MATCHED`. Same effect in reverse when the loop resets.
- **Idle breathing**: `1 + 0.025 * sin(frame / loopLength * 2pi)` scales pulse rings so nothing is ever perfectly still.
- **Loop with a fade-out**: in the last ~17 frames of every loop everything fades (`inOut(cubic)` 1 -> 0) so the restart is invisible.
- Style tokens: chip text is **uppercase, weight 400, letter-spacing .7 to 1.1px, colour `#3f3f46`**; chip borders `1.5px`, radius 10 to 18; avatar rings `2px rgba(0,0,0,.12)`; accent `#0066FF`; card background pure white.

### The "Creator Matching" card (270 frames = 9s loop), step by step
Centre chip at (260, 220), width 172, height 48. Eight avatar circles sit on an ellipse (centre 260,240; radius 178 x 162) starting at 12 o'clock every 45deg.
1. **0 to 78: scanning.** The chip reads `MATCHING...`. Three times (26 frames each, alternating direction) a blue gradient band sweeps up/down, **visible only through the chip's border** (mask of the chip outline, stroke 5). It looks like light running around the chip.
2. **78 to 96: lock-on.** The chip narrows `172 -> 136`, its border colour lerps grey -> blue.
3. **79 to 110: resolve.** Text scrambles into `MATCHED`.
4. **96 to ~150: fan-out.** For each avatar `i` (start `s = 96 + 6i`): a dashed line grows from the chip centre to the avatar's spot over 9 frames (`out(cubic)`); the avatar ring pops from 0 to 82px over 10 frames from `s+1` with **`out(back(1.3))`** (overshoot); the photo inside scales `.6 -> 1` and fades in over 10 frames from `s+2`. Stagger of 6 frames makes a clockwise "dealing" motion.
5. **150 to 240: hold.** Everything stays; only rings breathe.
6. **240 to 270: reset.** All lines/avatars fade out; chip widens back to 172 and scrambles back to `MATCHING...`. Loop.

### "Reporting & Scaling" (300 frames = 10s)
1. Chip 1 `COLLECTING DATA` pops in (back(1.05), 16 frames); a spinner rotates 0 -> 720deg until frame 40, then a check springs in.
2. A dotted line draws down from chip 1 while the blue sweep runs along it.
3. From frame 50, chip 2 `ANALYZING RESULTS` pops and spins until 138, then its check.
4. Three avatars appear in sequence (frames 72, 94, 116, 20 frames each) under chip 2.
5. At frame ~204 the **middle** avatar's ring turns blue and a springing blue pill `WINNING PARTNERSHIP` appears below (spring damping 10, stiffness 115); the side avatars dim to 30%.
6. Frames 282 to 299 fade everything, loop.

### The other diagrams (same toolkit)
- **Strategy call** (150): chip wobble at start (`6 sin(1.9f)` decaying over 60 frames), network of grey lines (chip -> hub -> three tags), the sweep travels the whole network from frame 60 to 145.
- **Outreach** (150): top chip, three concentric faint pulse rings (breathing), three icon discs spring in staggered around the ring, sweep runs down, bottom chip `DEAL ACCEPTED` with a check springs in.
- **Samples** (150): hub with three tags and an avatar, sweep to avatar.
- **Review & Launch** (197): chip `PREVIEW REVIEWAL` -> dotted line grows -> video thumbnail scales in -> `VIDEO APPROVED` chip pops over it -> line continues -> `SCHEDULED FOR TOMORROW`.
- **Creator side**: Onboarding Call, Sponsorship Pitches (avatar + pitch chip + brand circles), Offers & Negotiations (20/18 frame springs), Samples, Review & Launch (247), Reporting (300). Same grammar, different labels.

## 5. Other things worth noting
- Section order on the home page: hero + logo marquee, How We Work (tabs), category tabs with creator cards, "Why our YouTubers convert", numbers (accordion with counters), comparison table, testimonials, video wall, partner strip, team cards (hover/tap flips to a bio), FAQ (tabs), footer form.
- Number counters count up on enter. Team cards reveal a bio on hover with a blur on the photo.
- Contact: sticky `Contact` button top right, always visible.
- The footer form is a multi-step wizard (`Next`), which keeps each screen to one question.

## 6. What we copy for Gratovo (and what we deliberately do not)

Copy: the structure (one section, two audience tabs, swap in place), the sliding indicator, the staggered reveal and tape/tag draw-on, the horizontal card carousel with fade mask, arrows and dotted connectors, and the **frame-driven composition engine** with springs, sweeps through masked lines, spinner-to-check and text scramble. Build with our own colours, own icons and our own copy.

Do not copy: their tape artwork (it is their brand), their photos, their wording, their audio, their stat claims. Gratovo has no client results to show, so the diagrams show the **process**, never fake clients, fake creators or fake numbers.

## 7. Implementation in this repo
- Engine and compositions: `js/process-cards.js`; styles: `css/process-cards.css`. Used by `index.html` and `index-b.html`.
- Rule for future edits: add or change a diagram by editing/adding a composition (a function of the frame number), never by hand-tuning CSS delays. Keep everything on the 30 fps / 520x480 stage so cards stay consistent.
