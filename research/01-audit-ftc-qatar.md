# FTC Qatar website audit: ftc-qatar.com

Crawled 2026-11-03: 21 pages (home, 17 product/category pages, references, contact, /ar).
Full verbatim copy is in [ftc-content-inventory.md](ftc-content-inventory.md); the current brochure is [ftc-brochure-current.pdf](ftc-brochure-current.pdf).

## 1. Who FTC Qatar is (from their own material)

- **FTC Qatar W.L.L.** is part of **Farjallah Holding S.A.L.** (Lebanon). The roots go back to 1946, when Antoine Farjallah founded Iceberg, a factory for refrigerated showcases. Farjallah Trading Company followed in 1975 (refrigeration, electro-mechanical).
- FTC Qatar was set up in **2008 in partnership with Abu Issa Holding**. In 2023 it opened its own GCC headquarters in Doha and marked 15 years in Qatar.
- **HQ:** Building 16, Street 653, Zone 57, West Industrial Area, Doha. Tel +974 4144 1800 (Sun–Thu 8:00–17:30). Warehouse +974 3122 5566. Maintenance +974 3370 8096 (24/7). info@ftc-qatar.com
- **Group network (brochure):** Qatar (FTC Qatar, BES Qatar), UAE (FTC M.E., Dubai), KSA (FTC Arabia, 2024), Lebanon (FTC, Iceberg, Ammonia Cooling Systems, Optimised Logistic Solutions), Greece (FTC Europe, 2019), Ivory Coast (Afrigel Ouest, 2013), Jordan (Loreen Cooling Equipment), plus off-shore trading.
- **Their own counters:** 500+ employees, 10K+ clients, 5K+ projects, 20+ companies.
- **References:** GWC Warehouses Ras Laffan, Al Asmakh Warehouse, Al Raed Food & Fish Factory, Al Bayt Stadium, Al Rayyan Stadium, Al Udeid Air Base, Doha Metro Red Line, IKEA Qatar, Khalifa Stadium, Hamad Medical City, Sidra Hospital, Mall of Qatar.

### Scope of work: 6 pillars and their products

| Pillar | Lines | Brands |
|---|---|---|
| Refrigeration | Commercial (evaporators, compressors, monoblocks, air/water-cooled & silent condensing units), Industrial (central power racks, air-cooled condensers, ice banks), Ammonia chillers, Cold room assembly (modular rooms, cold storage doors) | Iceberg, Daikin, Friga-Bohn/HeatCraft, Kingspan, Boxcold, Polidoor, Prihoda |
| HVAC | Commercial & industrial A/C, exhaust & ventilation (smoke ventilators, ecology units, fans), air handling (soft/fabric ducts), thermal & acoustic insulation | Daikin, Sodeca, Dantherm, Mercor, Prihoda, Thermobreak, Pyrotek |
| Building envelope | Fire-rated materials, insulated panels, hygiene systems, geocellular tanks, chimneys | Promat, FSI, Kingspan, Hygibreak, Crane Composites, Cross-Wave, Dinak, BSK |
| Warehousing | Static & automated racking, industrial/rapid doors & docks, material handling | Stow, Loading Systems, STILL |
| Valves & copper | Control valves, copper tubes & fittings | Danfoss, Genebre, Halcor |
| After-sales | Spare parts (refrigerants, fans, Uniweld tools), maintenance 24/7 | Uniweld |

**Services:** Engineering, Contracting, Supply chain consultancy, Maintenance.

## 2. What's broken on the live site (fix these before anything visual)

| # | Issue | Where | Severity |
|---|---|---|---|
| 1 | Home footer shows **Lebanon** phone/fax/address and info@farjallah.com, not Qatar | `/` footer | High |
| 2 | Arabic site says **"Welcome to Farjallah Arabia"** in the hero, and the body copy names **FTC ME** and **FTC Arabia**. The `<title>` is Farjallah Holding | `/ar` | High |
| 3 | Arabic page has no `dir="rtl"` and `lang="en"` | `/ar` | High (a11y/SEO) |
| 4 | Mission statement says "The mission of **FTC Arabia**…" on the Qatar site | `/#about` | High |
| 5 | Commercial refrigeration copy: "the most reliable condensing units product line **in Lebanon**" | `/products?…10100` | Medium |
| 6 | WhatsApp link `wa.me/03035959` has no country code, so it doesn't open a chat | sitewide | Medium |
| 7 | "Been serving you for **77 years**" is stale (1946 → 2026 = 80) | `/#history` | Low |
| 8 | Counters render empty until JS runs ("+ Employees K+") | `/` | Medium |
| 9 | Every page has the same `<title>` and there is no `<h1>` | sitewide | High (SEO) |
| 10 | No `sitemap.xml` (404) and no canonical/OG tags. Meta description has typos ("middle easter", "it's") | sitewide | High (SEO) |
| 11 | 67 of 70 images have no alt text | `/` | Medium (a11y) |
| 12 | About 12.4 MB / 123 requests on home. Next.js wraps jQuery 3.2, Bootstrap 4.0, Revolution Slider and 8 jQuery plugins | `/` | High (perf) |
| 13 | Product pages hold names and one-line blurbs only: no specs, temperature ranges, datasheets per item or project links | `/products` | High (conversion) |
| 14 | References are 12 photos with "Project Description" placeholders and no case study content | `/references` | High (trust) |
| 15 | No quote/RFQ flow. The only conversion is a generic contact form with a math captcha | `/contact` | High (conversion) |
| 16 | Typos: "Air Conditionning", "Controlled Envronment panels are desgned…", "Yememi", "Mahmoul Sreet" | various | Low |
| 17 | Our Companies list is duplicated twice on /contact | `/contact` | Low |

## 3. What the new site has to do

1. **Show the problem FTC solves, not just a catalogue.** Most buyers are developers, MEP consultants, food/pharma/logistics operators and facility managers. They look for a contractor who can design, supply, install and maintain a temperature-controlled facility. Today the site reads like a brand distributor list.
2. **Organise by solution and by industry** as well as by product: Cold stores & cold chain, Food processing, Pharma & healthcare, Stadiums & venues, Logistics & warehousing, Hospitality & retail.
3. **Proof up front:** named Qatar landmark projects, an 80-year lineage, a group of 20 companies in 7 countries, and partner brands.
4. **Make conversion easy:** an RFQ wizard (facility type, temperature range, size, timeline), the 24/7 maintenance line visible on every page, and WhatsApp that works.
5. **Proper bilingual EN/AR,** with real RTL and the correct entity name.
6. **Technical SEO:** a unique title and H1 per page, a sitemap, schema.org `Organization`/`LocalBusiness`/`Product`, and hreflang en/ar.
7. **Performance:** under 1.5 MB on first view without 3D, and the 3D scene (v2) loaded progressively.
