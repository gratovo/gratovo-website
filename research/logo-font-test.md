# Hero logo: font test (2026-10-08)

Problem: with the G mark as the base, the capitals (Plus Jakarta Sans 800) looked thinner than the mark and did not sit right against it.

## Measurements (Edge, canvas measureText; fonts subset from Google Fonts, letters R A T O V only)
- Mark `images/logo-mark.svg`: tight crop, aspect 1.27, stroke thickness of the G ring = **0.212 of the mark's height**.
  With the mark sized to the cap height plus 6% overshoot, the matching letter stem is about **0.225 of cap height**.
- Stem / cap height by font and weight (cap height in em in brackets):

| Font | 700 | 800 | 900 | Notes |
|---|---|---|---|---|
| Outfit (0.719) | 0.239 | 0.261 | 0.304 | 650 -> 0.222. Round O echoes the round G. 650 matches the mark's stroke exactly; **chosen: 800** (stronger, the owner's pick) |
| Figtree (0.703) | 0.222 | 0.244 | 0.289 | close second, narrower |
| Plus Jakarta Sans (0.750) | 0.208 | 0.229 | n/a | the previous font; the numbers match, the letterforms felt off |
| Nunito (0.719) | n/a | 0.239 | 0.261 | rounded terminals, slightly childish next to the sharp arrow |
| Poppins (0.703) | 0.244 | 0.311 | 0.326 | a little wide |
| Sora (0.734) | 0.234 | 0.277 | n/a | too wide (RATOVO 4.5em) |
| Montserrat | 0.244 | 0.311 | 0.356 | too wide (4.5em+) |
| Urbanist / Manrope | 0.200 / 0.174 | 0.222 / 0.196 | 0.244 | too light unless 900 |
| Lexend | - | - | - | its I glyph has serifs, stem measure meaningless |

## Alignment rules (css/theme.css `.wordmark-caps`)
- Mark height = cap height x 1.06 (overshoot above and below, like the round letters).
- Mark bottom sits 3% of cap height under the baseline; gap to the R = 0.12 x cap height (0.22 looked too loose, 0.02 touched the arrow); letter-spacing 0.045em.
- Everything is in em, so it scales with `--wm-size` (default: the big hero size from `--fs-logo`).
- The hero logo (`.wordmark-grad`) paints the mark through a CSS mask and the letters through `background-clip: text`, both with the same horizontal white -> pale sky gradient (`--wg`, total width `--wg-w`, letters start at `--wg-x`).

## Decision
Outfit 800 everywhere: hero, footer, `images/full-logo.png` (rebuild: see `build-full-logo.py`, `build_png`) and the share-image plate (`build-og.py`). The comparison page and candidate subsets were deleted; the measured subsets stay in `research/.cache/logo-fonts/`.
- Site font: `fonts/outfit-logo.woff2` (3.4 KB, variable weight).
