# SEO research and audit (2026-10-08)

Saved so it is not refetched. Sources: live-site checks with curl, and web searches run on 2026-10-08.

## Audit of the site before the SEO pass
- Canonical, og:url, sitemap and robots all used `https://www.gratovo.com/`, but `www` 301-redirects to `https://gratovo.com/` (CNAME file says `gratovo.com`). Canonicals pointed at a redirecting URL. **Fixed: apex `https://gratovo.com` everywhere.**
- `sitemap.xml` used an invalid namespace (`https://www.sitemaps.org/...`; it must be `http://www.sitemaps.org/schemas/sitemap/0.9`) and listed two noindex pages (privacy, terms).
- `og:image` was `images/full-logo.png` at 1275x240 (not the 1200x630 social-card shape).
- `/brands` (no `.html`) also returns 200, so canonical tags matter.
- No custom 404, no manifest, no touch icons, no Article/WebSite/Breadcrumb schema, only 3 indexable pages (almost no keyword surface).
- `index-b.html` (an old experiment) was live and indexable (duplicate content risk).
- Card photos were CSS backgrounds (no real `<img>`, so nothing for image search and no lazy-loading hints).

## SERP landscape (what ranks for our terms)
- "AI influencer marketing" is ambiguous: many results are about AI-generated (virtual) influencers. Our pages must say plainly that this is about promoting AI/SaaS products through real creators.
- Who ranks for sponsor/agency queries: specialist agencies (Dothamina Agency, Riznex Media), YouTube sponsorship agencies (ThoughtLeaders), creator-side sponsor databases (GetSponsored, SponsorStream, SponsorRadar, YTSponsorDB), and platforms (IMAI, Upfluence). Almost all of them lead with pricing tiers, tool databases or "400M creators". A deal broker with a short vetted shortlist (1-3 creators) and creator-side deal sourcing is a different angle.
- "SaaS influencer marketing" informational results (hypefy, favikon, flippa, getreditus, pipedrive, 2checkout): B2B buyers do not buy on impulse, creators explain a workflow/problem, relevance and engagement beat follower count, micro creators often outperform, track with unique links.
- "How to get sponsored on YouTube / how YouTubers get brand deals" (lickd, podcastle, async, subscribr, toptal): brands check professionalism, audience relevance, consistent views and natural fit; AI channels are described as one of the fastest-moving sponsorship markets; YouTube Creator Partnerships (formerly BrandConnect) is a platform route.
- "How to vet influencers" (iqfluence, stack, contentgrip, yoloco, bird): average vs follower count, engagement quality and consistency, audience geography verified against analytics (not one screenshot), follower-growth spikes, comment quality, 30-post scroll.

## Keyword map (one primary phrase per page, no cannibalisation)
| Page | Primary phrase | Intent |
|---|---|---|
| index.html | AI influencer marketing (AI and SaaS brands, creators) | brand + creator, broad |
| brands.html | find AI creators for your product / AI creator sponsorships | brand, commercial |
| creators.html | brand deals for AI creators | creator, commercial |
| saas-influencer-marketing.html | SaaS influencer marketing | brand, commercial + info |
| ai-youtube-sponsorships.html | AI YouTube sponsorships / sponsor AI YouTubers | brand, commercial |
| ai-youtuber-brand-deals.html | brand deals for AI YouTubers | creator, commercial |
| ai-influencer-marketing-guide.html | AI influencer marketing guide | info pillar |
| how-to-find-ai-youtubers-to-sponsor.html | how to find AI YouTubers to sponsor | info |
| how-to-vet-ai-creators-before-sponsoring.html | how to vet an influencer / AI creator | info |
| how-ai-creators-get-brand-sponsorships.html | how AI YouTubers get sponsored | info (creator) |
| guides.html | influencer marketing guides for AI and SaaS | hub |

Copy rules kept: no pricing, no margins/transparency talk, no invented statistics (only Gratovo's own standards: 30K+ average views, 3-8% engagement, 35%+ audience in the target country).
