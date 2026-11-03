# v2: the 3D interactive site (three.js + Blender)

v1 (the Claude Design canvas) is the content and layout baseline. v2 keeps every v1 section as real HTML and adds three 3D moments on top. With 3D off (low-end phone, no WebGL, reduced motion) the site is still the complete v1.

## The three 3D moments

| # | Moment | Where | Technique | Reference |
|---|---|---|---|---|
| A | **Facility fly-through**: the camera starts outside FTC's Doha HQ / a model cold store, then flies in through the dock door, the cold room, the freezer, the plant room, the roof AHUs and the racking, ending on the 24/7 service van | Home §02 "From the dock to the plant room" | A scroll-scrubbed **pre-rendered film** (Blender Cycles → H.264/AV1 clips with frame-locked seams), driven by a scrub engine. Posters come first, then the film is lazy-loaded | terminal-industries hero; scroll-world engine |
| B | **Explorable cutaway**: a pinned three.js stage with 7 numbered steps and a dot rail. Clicking a hotspot (panel, door, evaporator, condensing unit, rack) opens its product card with brands and datasheet | Home §02 on desktop, plus each Solution page "anatomy" figure | Live **three.js** (r170+). Modular GLBs exported from Blender with Draco and KTX2 and baked lightmaps. Context-loss fallback to posters | officeverse.es |
| C | **Group globe**: a dot-matrix earth. Doha HQ pulses arcs to Dubai, Riyadh, Beirut, Amman, Athens and Abidjan; hovering a pin shows a card with that company and its headline projects | Home §07, Group page | three.js points shader with a ~50KB land-dot list and no model file. The office data stays in an HTML list; the canvas is `aria-hidden` | sandruci.com/ventures |

## Why A is pre-rendered and B is live
- **A is a film.** It has to look photoreal and correct on every phone, and live WebGL can't guarantee that. Scroll only scrubs time.
- **B is interactive.** People need to click a part and get the product, so it has to be real geometry. It stays stylised (clean materials, FTC cyan highlights) to stay light.
- **Accuracy matters for this client.** Equipment has to look like what FTC actually installs. That favours **Blender renders from our own models** over AI-generated video. AI dioramas tend to invent compressors, doors and racking that don't exist.

### Option for A: the scroll-world skill (oso95/scroll-world, MIT)
- It generates isometric diorama stills with GPT Image and camera flights with Seedance or Kling image-to-video, frame-locks the seams, and ships a portable vanilla-JS scrub engine.
- Cost is pay-per-clip on Monid: about **$27 for a 6-scene 1080p chain**, doubled for the mobile 9:16 chain. It needs Monid or Higgsfield accounts, ffmpeg and Pillow.
- **Recommended use:** reuse its **scrub engine and seam-crossfade method** on our **Blender-rendered clips**. Use its AI pipeline only for a fast mood film to show the client before modelling.

## Blender production plan
1. **Kit of parts:** insulated panel wall/roof (with parametric length/thickness via geometry nodes), hinged and sliding cold door, rapid door, dock leveller and shelter, evaporator, condensing unit, monoblock, central rack, ammonia chiller, AHU, fabric duct, pallet racking, STILL forklift, pallets and stock, and the FTC service van.
2. **Scenes:** (1) HQ exterior at golden hour, Doha; (2) loading dock; (3) cold room; (4) freezer (frost FX); (5) plant room; (6) roof (AHUs, condensers); (7) warehouse racking; (8) service van exit.
3. **Look:** neutral concrete and steel with FTC cyan only on the "active" part of each step. Soft daylight. No neon or fantasy.
4. **Exports:**
   - Film: 1920×1080 and 1080×1920 (mobile) per step, AV1 with an H.264 fallback, plus a poster JPG and `-m.jpg` per step.
   - Interactive: GLB with Draco and KTX2 textures, under **4 MB total**, loaded on demand.
5. **Budgets:**
   - First view without 3D: under 1.5 MB, LCP under 2.0 s on 4G.
   - Film: under 2 MB per step at 1080p.
   - three.js chunk: under 250 KB gzip, lazy-loaded.

## Build stack
- Next.js (or Astro) static site, EN/AR with real RTL and hreflang.
- GSAP ScrollTrigger + Lenis for scroll.
- three.js lazy-loaded via dynamic import, and only on the sections that use it.
- A headless CMS (Sanity / Storyblok) so FTC can edit projects, products and brands.
- schema.org `Organization`, `LocalBusiness` and `Product`, plus a sitemap.

## Phases
| Phase | Deliverable | Size |
|---|---|---|
| 0 | Client sign-off on v1 canvas + content gaps filled (project scopes, FAQs, photos) | S |
| 1 | v1 built as a real site (no 3D), EN + AR, CMS, SEO fixes from the audit | L |
| 2 | Globe (C) | S |
| 3 | Blender kit + film (A) with posters | L |
| 4 | Interactive cutaway (B) + solution-page anatomy viewers | M |
| 5 | Perf/a11y pass, go-live | M |

## Content we need from FTC
- Scope delivered on each of the 12 references, plus 3–5 more recent projects with photos.
- High-res site photography (the current images are 768 px).
- Confirmation of temperature ranges, lead times and FAQ answers.
- Datasheets per product line.
- The 24/7 number and a WhatsApp number in international format.
- Correct Arabic company name and copy reviewed by a native speaker.
