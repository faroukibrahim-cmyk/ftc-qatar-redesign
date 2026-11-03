# Reference sites: what to take from each (studied 2026-11-03)

## officeverse.es: a scroll-driven 3D story (the template for v2)
- A sticky three.js stage on a ~7,200px scroll track, split into 10 steps. Each step is a camera pose with a numbered text panel ("04 / 09 · FOR STAFF"). A right-edge dot rail with `aria-current` navigates between steps.
- Posters come first: each step has a pre-rendered JPG (80–280KB) and a `-m.jpg` mobile version. The ~1MB gz 3D chunk loads only after you scroll. A WebGL context-loss message falls back to the posters.
- three.js r186, Vite, ~34 modular GLBs (~9MB, **no Draco/KTX2**; FTC must compress), baked-lightmap WebP textures.
- **For FTC:** a pinned cutaway of a cold-store facility. Steps: loading bay → cold room → blast freezer → plant room → AHU → racking → 24/7 maintenance.

## sandruci.com/ventures: worldwide presence (the template for the "Group" section)
- A dot-matrix 3D globe. The land is a 53KB dot list with no model file. Arcs carry pulses both ways, and pins have an expanding ring and are colour-coded by kind. It auto-rotates and pauses off screen.
- The data lives in an HTML list (`li data-lat data-lon data-kind`) and the canvas is `aria-hidden`, which keeps it SEO- and a11y-safe. On touch, scroll wins and tapping opens a pin.
- three.js 0.170 ES module with custom GLSL point shaders; ~70KB plus three.
- **For FTC:** Doha as HQ, with arcs to Dubai, Riyadh, Beirut, Athens, Abidjan and Amman. Colours: HQ / group company / partner brand origin.

## terminal-industries.com: art direction
- Teal-black `#052424` with one acid-lime accent `#ABFF02`. SuisseIntl headings (H1 70px/400, −3.6px tracking). Geist Mono eyebrows (11px/600, uppercase, 18% tracking).
- A scroll-scrubbed **pre-rendered video** hero, which is not live WebGL. The story is told as a physical journey (At the Gate → In the Yard → At the Dock). Entry paths split by customer size. An efficiency calculator acts as the lead magnet. Logo wall early, FAQs late.
- Nuxt, GSAP + Lenis, Storyblok.
- **For FTC:** "At the dock → In the cold room → In the plant room → Across the network". Entry paths: "One cold room / A facility / A regional network". A cold-room sizing and energy calculator.

## wearebrand.io: agency polish
- A full-bleed WebGL canvas, big uppercase statements ("LET'S BUILD SOMETHING EXCEPTIONAL"), minimal chrome, and offices listed in the footer as a trust signal.
- **For FTC:** confident oversized type, very little UI, and one bold statement per screen.

## landing.love: research gallery
- A catalogue of ~2,256 full-page recordings. Useful categories: **3D Websites (582), Technology (163), Dark Mode (652), SaaS (93), Business**. Use it to collect 5–10 recorded references for each project before designing.

## Awwwards: industrial and engineering sites that won awards (verified 2026-11-03)
| Site | Award | What to take |
|---|---|---|
| hustonengineering.com | HM 2023 | The closest peer (MEP firm). Full-bleed plant-room photos under one brand overlay, plain H1 |
| hajster.com/en | HM 2024 | Calm, clear HVAC product-line pages |
| caeli-energie.com | SOTD 2025 | Scroll-driven AC product walkthrough plus a "project simulation" form, a model for the RFQ |
| beintech.fr | HM 2025 | Dark UI with 3 disciplines (structure, building services, fire safety), Blender renders |
| q-industrial.com | SOTD + Dev 2024 | Black with one rendered brand object, "Industries & Surfaces" sector pages |
| terminal-industries.com | SOTD/SOTM 2025 | Scroll image sequence, Suisse + Geist Mono, story told as operations |
| efla-engineers.com | HM 2024 | Restrained multi-country consultancy tone |
| ose-engineering.fr | HM 2026 | "Complexity into clarity": expertise grid and project index |
| manuport-logistics.com | HM 2024 | Storytelling for an office network across countries (small WebGL) |
| vistaenergy.com | HM 2025 | A credibility layer pitched at investors |

**Common traits:** a dark neutral or off-white base with one accent and no gradients; neo-grotesk type with mono only for specs; real plant/site photos; restrained motion. Most 3D on these sites is **pre-rendered** and only 1 of 10 runs live WebGL. **Avoid:** WebGL as decoration, playful agency tricks, and stock hard-hat photos.
