"""Build the FTC Qatar static sites: dist/v1 (no 3D) and dist/v2 (three.js), each in EN + AR.

Usage: python3 tools/build.py [--site-url https://example.onrender.com]
Copy lives in src/i18n/<lang>.json; markup lives in the page functions below.
Stdlib only, so it builds anywhere Python 3.9+ runs.
"""
import json, shutil, sys, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, DIST = ROOT / "src", ROOT / "dist"
LANGS = ["en", "ar"]
# v2 fly-through: rendered frames live in src/film/{d,m}/fNNN.webp (tools/make_film.sh); k0..k4.jpg are the step posters.
FILM_FRAMES = len(list((SRC / "film/d").glob("f*.webp"))) if (SRC / "film/d").exists() else 0
FILM_CUTS = [0, 0.227, 0.487, 0.673, 0.859]  # where each journey step starts, as a share of the film (facility.py STEPS)
BRANDS = ["Kingspan", "Daikin", "Danfoss", "Promat", "STILL", "Sodeca", "Friga-Bohn", "Polidoor", "Boxcold",
          "Thermobreak", "Halcor", "Genebre", "Dantherm", "Mercor", "Stow", "Dinak", "Pyrotek"]
PHONE_HEAD, PHONE_MAINT, PHONE_WH = "+974 4144 1800", "+974 3370 8096", "+974 3122 5566"
WHATSAPP = "https://wa.me/97441441800"  # live site's wa.me/03035959 has no country code; confirm the real WhatsApp line with FTC
esc = html.escape


def tel(n): return "tel:" + n.replace(" ", "")
def num(s): return f'<bdi class="n">{esc(s)}</bdi>'
def ja(o): return esc(json.dumps(o, ensure_ascii=False), quote=True)


def icon_menu():
    return '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M2 5h14M2 9h14M2 13h14" stroke="currentColor" stroke-width="1.6"/></svg>'


def cutaway_svg(t):
    j = t["journey"]
    return f'''<svg viewBox="140 20 420 350" role="img" aria-label="{esc(j["fig_alt"])}">
<polygon points="300,140 525,270 390,348 165,218" fill="var(--bg-2)" stroke="var(--rule-2)"/>
<polygon points="300,140 525,270 525,166 300,36" fill="var(--bg-2)" stroke="var(--rule-2)" fill-opacity="0.7"/>
<polygon points="300,140 165,218 165,114 300,36" fill="var(--bg-2)" stroke="var(--rule-2)" fill-opacity="0.5"/>
<polygon points="480,244 514,263 514,211 480,192" fill="var(--acc)" fill-opacity="0.15" stroke="var(--acc)"/>
<polygon points="300,104 368,143 300,182 232,143" fill="var(--acc)" fill-opacity="0.22" stroke="var(--acc)"/>
<polygon points="368,143 300,182 300,244 368,205" fill="var(--acc)" fill-opacity="0.10" stroke="var(--acc)"/>
<polygon points="232,143 300,182 300,244 232,205" fill="var(--acc)" fill-opacity="0.06" stroke="var(--acc)"/>
<polygon points="390,156 458,195 390,234 323,195" fill="var(--fg)" fill-opacity="0.18" stroke="var(--fg)"/>
<polygon points="458,195 390,234 390,296 458,257" fill="var(--fg)" fill-opacity="0.08" stroke="var(--fg)"/>
<polygon points="323,195 390,234 390,296 323,257" fill="var(--fg)" fill-opacity="0.05" stroke="var(--fg)"/>
<line x1="300" y1="104" x2="300" y2="60" stroke="var(--acc)" stroke-dasharray="3 3"/>
<text x="304" y="56" fill="var(--acc)" font-family="JetBrains Mono, IBM Plex Sans Arabic, monospace" font-size="9">{esc(j["label_cold"])}</text>
<line x1="390" y1="156" x2="430" y2="100" stroke="var(--fg)" stroke-dasharray="3 3"/>
<text x="434" y="98" fill="var(--fg)" font-family="JetBrains Mono, IBM Plex Sans Arabic, monospace" font-size="9">{esc(j["label_freezer"])}</text>
<line x1="514" y1="237" x2="540" y2="300" stroke="var(--acc)" stroke-dasharray="3 3"/>
<text x="470" y="314" fill="var(--acc)" font-family="JetBrains Mono, IBM Plex Sans Arabic, monospace" font-size="9">{esc(j["label_dock"])}</text>
</svg>'''


def globe_svg(t):
    g = t["group"]
    arcs = "".join(f'<path d="M300 236 Q {q}" fill="none" stroke="var(--acc)" stroke-width="1.4"/>' for q in
                   ["250 150 186 168", "240 120 160 132", "200 300 92 318", "320 220 330 246", "285 215 268 222", "250 190 206 184"])
    pins = "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="var(--acc)"/>' for x, y in
                   [(330, 246), (268, 222), (186, 168), (206, 184), (160, 132), (92, 318)])
    rings = "".join(f'<ellipse cx="240" cy="240" rx="{a}" ry="{b}" fill="none" stroke="var(--rule)"/>' for a, b in
                    [(210, 70), (210, 140), (70, 210), (140, 210)])
    return f'''<svg viewBox="0 0 480 480" role="img" aria-label="{esc(g["fig_alt"])}">
<circle cx="240" cy="240" r="210" fill="var(--bg-2)" stroke="var(--rule)"/>{rings}
<line x1="30" y1="240" x2="450" y2="240" stroke="var(--rule)"/>{arcs}
<circle cx="300" cy="236" r="14" fill="none" stroke="var(--fg)" stroke-opacity="0.5"/>
<circle cx="300" cy="236" r="5" fill="var(--fg)"/>{pins}
<text x="312" y="226" fill="var(--fg)" font-family="JetBrains Mono, IBM Plex Sans Arabic, monospace" font-size="11">{esc(g["items"][0][5])} · {esc(g["hq"])}</text>
</svg>'''


def anatomy_svg(t):
    c = t["cold"]; L = c["fig_labels"]
    f = 'font-family="JetBrains Mono, IBM Plex Sans Arabic, monospace" font-size="10"'
    return f'''<svg viewBox="0 0 520 400" role="img" aria-label="{esc(c["fig_alt"])}">
<polygon points="260,40 400,110 260,180 120,110" fill="var(--acc)" fill-opacity="0.18" stroke="var(--acc)"/>
<polygon points="120,150 260,220 260,340 120,270" fill="var(--acc)" fill-opacity="0.07" stroke="var(--acc)"/>
<polygon points="260,220 400,150 400,270 260,340" fill="var(--acc)" fill-opacity="0.12" stroke="var(--acc)"/>
<polygon points="300,240 350,215 350,290 300,315" fill="var(--fg)" fill-opacity="0.12" stroke="var(--fg)"/>
<polygon points="160,96 230,131 230,151 160,116" fill="var(--bg-2)" stroke="var(--fg)"/>
<polygon points="420,60 480,90 480,130 420,100" fill="var(--bg-2)" stroke="var(--fg)"/>
<polygon points="420,60 450,45 510,75 480,90" fill="var(--bg-2)" stroke="var(--fg)"/>
<line x1="260" y1="40" x2="260" y2="16" stroke="var(--acc)" stroke-dasharray="3 3"/><text x="266" y="18" fill="var(--acc)" {f}>{esc(L[0])}</text>
<line x1="120" y1="210" x2="60" y2="210" stroke="var(--acc)" stroke-dasharray="3 3"/><text x="6" y="200" fill="var(--acc)" {f}>{esc(L[1])}</text>
<line x1="325" y1="315" x2="325" y2="372" stroke="var(--fg)" stroke-dasharray="3 3"/><text x="290" y="388" fill="var(--fg)" {f}>{esc(L[2])}</text>
<text x="150" y="80" fill="var(--fg)" {f}>{esc(L[3])}</text>
<text x="404" y="150" fill="var(--fg)" {f}>{esc(L[4])}</text>
</svg>'''


def design_panel(t):
    d = t["design"]
    def group(name, legend, opts, swatch=None):
        items = "".join(
            f'<label><input type="radio" name="{name}" value="{k}"><span>'
            + (f'<i class="sw" style="background:{swatch[k]}"></i>' if swatch else "") + f'{esc(v)}</span></label>'
            for k, v in opts.items())
        return f'<fieldset><legend class="m">{esc(legend)}</legend><div class="opts">{items}</div></fieldset>'
    sw = {"cyan": "#04AFF0", "ice": "#9FE3F5", "signal": "#FF8A2A", "navy": "#1D3F8F"}
    return f'''<button type="button" class="btn btn-p dz-open" aria-controls="dz" aria-expanded="false">{esc(d["open"])}</button>
<section class="dz" id="dz" role="dialog" aria-labelledby="dz-t" hidden>
<button type="button" class="x" aria-label="{esc(t["nav"]["close"])}">×</button>
<h2 id="dz-t">{esc(d["title"])}</h2><p class="note">{esc(d["note"])}</p>
<form>{group("theme", d["theme"], d["themes"])}{group("accent", d["accent"], d["accents"], sw)}{group("type", d["type"], d["types"])}{group("shape", d["shape"], d["shapes"])}</form>
<div class="row"><button type="button" class="btn btn-p" data-copy data-done="{esc(d["copied"])}">{esc(d["copy"])}</button><button type="button" class="btn btn-o" data-reset>{esc(d["reset"])}</button></div>
</section>'''


THEME_BOOT = """<script>(function(){var k=['theme','accent','type','shape'],d={theme:'ink',accent:'cyan',type:'expanded',shape:'soft'},q=new URLSearchParams(location.search),s={};try{s=JSON.parse(localStorage.getItem('ftc-design')||'{}')}catch(e){}k.forEach(function(n){document.documentElement.setAttribute('data-'+n,q.get(n)||s[n]||d[n])});var h=document.documentElement;if(!matchMedia('(prefers-reduced-motion: reduce)').matches){h.classList.add('mo');setTimeout(function(){if(!window.ftcMotion)h.classList.remove('mo')},3000)}})();</script>"""


def page(t, v, slug, title, desc, body, site_url):
    lang, other = t["lang"], ("ar" if t["lang"] == "en" else "en")
    path = f"/{lang}/" + (f"{slug}/" if slug else "")
    alt_path = f"/{other}/" + (f"{slug}/" if slug else "")
    fonts = "family=Archivo:wdth,wght@62..125,300..900&family=JetBrains+Mono:wght@400;500;600"
    # Arabic pages need the full family; English pages only render the "عربي" switch label
    # unicode-range subsetting means English pages only download Arabic glyphs for the switch label
    fonts += "&family=IBM+Plex+Sans+Arabic:wght@" + ("400;500;600;700" if lang == "ar" else "500")
    ld = {"@context": "https://schema.org", "@type": "LocalBusiness", "name": "FTC Qatar W.L.L.", "url": site_url + path,
          "logo": site_url + "/assets/img/logo-dark.png", "telephone": PHONE_HEAD, "email": "info@ftc-qatar.com",
          "parentOrganization": {"@type": "Organization", "name": "Farjallah Holding S.A.L."},
          "address": {"@type": "PostalAddress", "streetAddress": "Building 16, Street 653, Zone 57, West Industrial Area",
                      "addressLocality": "Doha", "addressCountry": "QA"},
          "sameAs": ["https://www.linkedin.com/company/ftc-qatar/"], "foundingDate": "2008"}
    nav = t["nav"]
    home = f"/{lang}/"
    contact = L(CAT["ui"]["contact"], lang)
    links = [("solutions", home + "solutions/", nav["solutions"]), ("projects", home + "projects/", nav["projects"]),
             ("services", home + "services/", nav["services"]), ("about", home + "about/", nav["about"]),
             ("group", home + "#group", nav["group"]), ("contact", home + "contact/", contact)]
    top = slug.split("/")[0]
    section = "solutions" if (top in PILLARS or top in LINES or top == "solutions") else top
    nav_html = "".join(f'<a href="{h}"' + (' aria-current="page"' if k == section else "") + f'>{esc(label)}</a>' for k, h, label in links)
    sitemap = "".join(f'<a href="{home}{p["slug"]}/">{esc(L(p["tag"], lang))}</a><br>' for p in CAT["pillars"])
    scripts = '<script src="/assets/js/site.js" defer></script><script src="/assets/js/motion.js" defer></script>'
    if v == "v2":
        scripts += ('<script type="importmap">{"imports":{"three":"/assets/vendor/three.module.min.js","three/addons/":"/assets/vendor/jsm/"}}</script>'
                    '<script type="module" src="/assets/js/film.js"></script>'
                    '<script type="module" src="/assets/js/cutaway.js"></script><script type="module" src="/assets/js/globe.js"></script>')
    f = t["footer"]
    return f'''<!doctype html>
<html lang="{lang}" dir="{t["dir"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{site_url}{path}">
<link rel="alternate" hreflang="{lang}" href="{site_url}{path}">
<link rel="alternate" hreflang="{other}" href="{site_url}{alt_path}">
<link rel="alternate" hreflang="x-default" href="{site_url}/en/{slug + "/" if slug else ""}">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{site_url}/assets/img/hero.jpg"><meta property="og:locale" content="{t["og_locale"]}">
<meta name="theme-color" content="#060A0F">
<link rel="icon" href="/assets/img/favicon.png">
{THEME_BOOT}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
<link rel="stylesheet" href="/assets/css/styles.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{scripts}
</head>
<body class="base {v}">
<a class="skip" href="#main">{esc(nav["skip"])}</a>
<header class="hdr base"><div class="wrap">
<a class="logo" href="{home}" aria-label="{esc(t["brand"])}"><img class="logo-w" src="/assets/img/logo-white.png" alt="{esc(t["brand"])}" width="77" height="38"><img class="logo-c" src="/assets/img/logo-dark.png" alt="{esc(t["brand"])}" width="77" height="38"></a>
<nav class="nav" id="nav" aria-label="{esc(nav["menu"])}">{nav_html}</nav>
<span class="spacer"></span>
<a class="tel m" href="{tel(PHONE_MAINT)}">{esc(nav["maintenance"])} · {num(PHONE_MAINT)}</a>
<a class="lang m" href="{alt_path}" hreflang="{other}" lang="{other}" aria-label="{esc(nav["switch_label"])}">{esc(nav["switch"])}</a>
<a class="btn btn-p q" href="{home}#rfq">{esc(nav["quote"])}</a>
<button type="button" class="menu-btn" aria-controls="nav" aria-expanded="false" aria-label="{esc(nav["menu"])}">{icon_menu()}</button>
</div></header>
<main id="main">{body}</main>
<footer class="ftr dark"><div class="wrap" style="padding-top:72px">
<div class="d big" aria-hidden="true">{esc(f["big"])}</div>
<div class="ftr-grid">
<div><img src="/assets/img/logo-white.png" alt="{esc(t["brand"])}" width="89" height="44"><div>{esc(f["entity"])}<br>{f["address"]}</div></div>
<div><span class="m">{esc(f["head"])}</span><a href="{tel(PHONE_HEAD)}">{num(PHONE_HEAD)}</a><br>{esc(f["hours"])}<br><a href="mailto:info@ftc-qatar.com">info@ftc-qatar.com</a></div>
<div><span class="m">{esc(f["maint"])}</span><a href="{tel(PHONE_MAINT)}">{num(PHONE_MAINT)}</a><br><br><span class="m">{esc(f["warehouse"])}</span><a href="{tel(PHONE_WH)}">{num(PHONE_WH)}</a></div>
<div><span class="m">{esc(nav["solutions"])}</span>{sitemap}</div>
<div><span class="m">FTC Qatar</span><a href="{home}projects/">{esc(nav["projects"])}</a><br><a href="{home}services/">{esc(nav["services"])}</a><br><a href="{home}about/">{esc(nav["about"])}</a><br><a href="{home}contact/">{esc(contact)}</a><br><a href="/assets/ftc-qatar-brochure.pdf">{esc(L(CAT["ui"]["brochure"], lang))}</a></div>
<div><span class="m">{esc(f["group"])}</span><a href="https://ftc-me.com/">FTC M.E.</a> · <a href="https://ftc-arabia.com/">FTC Arabia</a><br><a href="https://ftceurope.com/">FTC Europe</a> · <a href="https://afrigel.com/">Afrigel</a><br><a href="https://farjallah.com/leb">Farjallah Holding</a></div>
</div>
<div class="ftr-bot m"><span>{esc(f["copy"])}</span><span><a href="https://www.linkedin.com/company/ftc-qatar/">LinkedIn</a> · <a href="{home}contact/#jobs">{esc(f["careers"])}</a> · {esc(f["privacy"])}</span></div>
</div></footer>
<nav class="qbar m" aria-label="{esc(nav["maintenance"])}"><a href="{tel(PHONE_MAINT)}">{esc(t["quickbar"]["call"])}</a><a href="{WHATSAPP}">{esc(t["quickbar"]["whatsapp"])}</a><a href="{home}#rfq">{esc(t["quickbar"]["quote"])}</a></nav>
{design_panel(t)}
</body>
</html>
'''


def home_body(t, v):
    h, j, s, p, pr, sv, g, ln, r = (t[k] for k in ["hero", "journey", "solutions", "paths", "projects", "services", "group", "lineage", "rfq"])
    lang = t["lang"]
    temps = "".join(f'<span>{esc(a)} <b>{num(b)}</b></span>' for a, b in h["temps"])
    stats = "".join(f'<div class="stat"><div class="d">{num(a)}</div><span class="m">{esc(b)}</span></div>' for a, b in t["stats"])
    marks = "".join(f"<span>{esc(x)}</span>" for x in t["landmarks"]["items"])
    steps = "".join(
        f'<li><button type="button" class="step" data-step="{i}"><span class="num m">0{i + 1}</span><span><span class="t">{esc(a)}</span><span class="s">{esc(b)}</span></span></button></li>'
        for i, (a, b) in enumerate(j["steps"]))
    if v == "v2":
        parts = {k: {"t": a, "s": b} for k, (a, b) in j["parts"].items()}
        fig = (f'<figure class="fig"><div class="stage" id="cutaway" data-parts="{ja(parts)}" data-fallback="{esc(j["fallback"])}">'
               f'<div class="poster">{cutaway_svg(t)}</div>'
               f'<div class="part-card" role="status" hidden></div></div>'
               f'<figcaption class="m"><span>{esc(j["fig_caption"])}</span><span class="acc">{esc(j["fig_v2"])}</span></figcaption></figure>')
    else:
        fig = f'<figure class="fig">{cutaway_svg(t)}<figcaption class="m"><span>{esc(j["fig_caption"])}</span><span class="acc">{esc(j["fig_v1"])}</span></figcaption></figure>'
    cells = ""
    for i, it in enumerate(s["items"]):
        it = dict(it, page=["refrigeration", "hvac", "building-materials", "warehousing", "valves-copper"][i])
        inner = (f'<div class="top m"><span>0{i + 1}</span><span>{esc(it["tag"])}</span></div><div class="d">{esc(it["title"])}</div>'
                 f'<div class="s">{esc(it["desc"])}</div><div class="brands m">{esc(it["brands"])}</div>')
        cells += f'<a class="cell" href="/{lang}/{it["page"]}/">{inner}</a>' if it.get("page") else f'<div class="cell">{inner}</div>'
    sc = s["service"]
    cells += (f'<div class="cell inv"><div class="top m"><span>06</span><span>{esc(sc["tag"])}</span></div><div class="d">{esc(sc["title"])}</div>'
              f'<div class="s">{esc(sc["desc"])}</div><a class="m" style="color:var(--fg)" href="/{lang}/after-sales/">{esc(L(CAT["pillars"][4]["title"], lang))} →</a>'
              f'<a class="brands m acc" style="color:var(--acc);margin-top:0" href="{tel(PHONE_MAINT)}">{esc(sc["call"])} · {num(PHONE_MAINT)} →</a></div>')
    hrefs = ["#rfq", "#rfq", "#group"]
    pcards = "".join(
        f'<div class="card{" hl" if i == 1 else ""}"><div class="m muted">{esc(a)}</div><div class="d">{esc(b)}</div><div class="s">{esc(c)}</div><a class="go m" href="{hrefs[i]}">{esc(d)} →</a></div>'
        for i, (a, b, c, d) in enumerate(p["items"]))
    chips = "".join(f'<span class="chip m">{esc(x)}</span>' for x in p["sectors"])
    projs = "".join(proj_card(x, lang) for x in CAT["home_projects"])
    svs = "".join(f'<div><div class="m acc">{esc(sv["step"])} {i + 1}</div><div class="d">{esc(a)}</div><p>{esc(b)}</p></div>' for i, (a, b) in enumerate(sv["items"]))
    offices = "".join(
        f'<li data-lat="{lat}" data-lon="{lon}" data-kind="{kind}" data-city="{esc(city)}"><span style="font-weight:600">{esc(c)}</span><span class="m">{esc(co)}</span></li>'
        for c, co, kind, lat, lon, city in g["items"])
    gfig = (f'<figure style="margin:0"><div class="globe" id="globe"><div class="poster">{globe_svg(t)}</div><div class="pin-card" hidden></div></div>'
            f'<figcaption class="m muted" style="margin-top:12px">{esc(g["fig_v2"])}</figcaption></figure>') if v == "v2" else \
           f'<figure style="margin:0"><div style="max-width:520px">{globe_svg(t)}</div><figcaption class="m muted" style="margin-top:12px">{esc(g["fig_v1"])}</figcaption></figure>'
    film = ""
    if v == "v2":
        fm = t["film"]
        fsteps = "".join(
            f'<li><img src="/assets/film/k{i}.jpg" alt="" loading="lazy" width="1280" height="720"><span class="num m">0{i + 1}</span>'
            f'<span class="t">{esc(a)}</span><span class="s">{esc(b)}</span></li>' for i, (a, b) in enumerate(j["steps"]))
        film = (f'<section class="film" id="film" aria-labelledby="film-h" data-frames="{FILM_FRAMES}" data-cuts="{ja(FILM_CUTS)}">'
                f'<div class="film-pin"><canvas class="film-canvas" aria-hidden="true"></canvas><div class="wrap film-ui">'
                f'<div><p class="m eyebrow">{esc(fm["eyebrow"])}</p><h2 class="d h2" id="film-h" style="max-width:16ch">{esc(fm["title"])}</h2>'
                f'<p class="m film-hint muted">{esc(fm["hint"])} ↓</p></div>'
                f'<div style="position:relative"><ol class="film-steps">{fsteps}</ol>'
                f'<div class="film-rail" aria-hidden="true"><span></span></div><p class="m film-note">{esc(fm["note"])}</p></div></div></div></section>')
    tl = "".join(f'<li><div class="d{" now" if a == "2008" else ""}">{num(a)}</div><p>{esc(b)}</p></li>' for a, b in ln["items"])
    brands = "".join(f"<span>{b}</span>" for b in BRANDS)
    opts = lambda xs: "".join(f"<option>{esc(x)}</option>" for x in xs)
    # v2 plays FTC's own warehouse footage behind the hero; site.js drops it for reduced motion / data saver
    video = ('<video class="bgimg" data-hero-video autoplay muted loop playsinline preload="metadata" poster="/assets/img/hero.jpg" aria-hidden="true">'
             '<source src="/assets/img/hero-loop.mp4" type="video/mp4"></video>') if v == "v2" else ""
    return f'''
<section class="hero dark" id="top"><img class="bgimg" src="/assets/img/hero.jpg" alt="" fetchpriority="high" width="1280" height="720">{video}<div class="wrap">
<p class="m eyebrow">{esc(h["eyebrow"])}</p><h1 class="d">{esc(h["title"])}</h1>
<div class="hero-row"><p class="lead">{esc(h["lead"])}</p><div class="btns"><a class="btn btn-p" href="#rfq">{esc(h["cta1"])}</a><a class="btn btn-o" href="#journey">{esc(h["cta2"])}</a></div></div>
<div class="temps m">{temps}</div></div></section>
<section class="base bt bb" aria-label="{esc(t["stats_label"])}"><div class="wrap stats">{stats}</div></section>
<section class="base" aria-label="{esc(t["landmarks"]["label"])}"><div class="wrap marks m"><span class="acc">{esc(t["landmarks"]["label"])} →</span>{marks}</div></section>
{film}
<section class="alt-soft base bt" id="journey" style="background:var(--bg-2)"><div class="wrap sec split">
<div><p class="m eyebrow">{esc(j["eyebrow"])}</p><h2 class="d h2">{esc(j["title"])}</h2><p class="lead" style="margin:24px 0 0">{esc(j["lead"])}</p><ol class="steps" id="steps">{steps}</ol></div>
{fig}</div></section>
<section class="alt" id="solutions"><div class="wrap sec">
<div class="sec-head"><div><p class="m eyebrow">{esc(s["eyebrow"])}</p><h2 class="d h2" style="max-width:14ch">{esc(s["title"])}</h2></div><p class="lead" style="margin:0;max-width:420px">{esc(s["lead"])}</p></div>
<div class="grid-cells">{cells}</div></div></section>
<section class="base" id="industries"><div class="wrap sec"><p class="m eyebrow">{esc(p["eyebrow"])}</p><h2 class="d h2" style="margin-bottom:52px">{esc(p["title"])}</h2>
<div class="cards3">{pcards}</div><div class="chips">{chips}</div></div></section>
<section class="base bt" id="projects"><div class="wrap sec"><div class="sec-head"><div><p class="m eyebrow">{esc(pr["eyebrow"])}</p><h2 class="d h2">{esc(pr["title"])}</h2></div><a class="m link" href="/{lang}/projects/">{esc(pr["all"])} →</a></div>
<div class="projects">{projs}</div></div></section>
<section class="base bt" id="services" style="background:var(--bg-2)"><div class="wrap sec"><p class="m eyebrow">{esc(sv["eyebrow"])}</p><h2 class="d h2" style="margin-bottom:52px;max-width:16ch">{esc(sv["title"])}</h2><div class="cols4">{svs}</div></div></section>
<section class="base bt" id="group"><div class="wrap sec split" style="align-items:center">{gfig}
<div><p class="m eyebrow">{esc(g["eyebrow"])}</p><h2 class="d h2" style="margin-bottom:24px">{esc(g["title"])}</h2><p class="lead" style="margin:0 0 32px">{esc(g["lead"])}</p><ul class="offices" id="offices">{offices}</ul></div></div></section>
<section class="alt" id="lineage"><div class="wrap sec"><p class="m eyebrow">{esc(ln["eyebrow"])}</p><h2 class="d h2" style="margin-bottom:52px;max-width:15ch">{esc(ln["title"])}</h2><ol class="timeline">{tl}</ol></div></section>
<section class="base bb" aria-label="{esc(t["brands_label"])}"><div class="wrap" style="padding-block:80px"><p class="m muted" style="margin:0 0 32px">{esc(t["brands_label"])}</p><div class="d brands-wall">{brands}</div></div></section>
<section class="base" id="rfq"><div class="wrap sec split">
<div><p class="m eyebrow">{esc(r["eyebrow"])}</p><h2 class="d" style="font-size:clamp(44px,6vw,96px);margin-bottom:24px">{esc(r["title"])}</h2><p class="lead">{esc(r["lead"])}</p></div>
<form class="rfq" id="rfq-form" data-subject="{esc(r["subject"])}" action="mailto:info@ftc-qatar.com" method="post" enctype="text/plain">
<label class="m">{esc(r["type"])}<select name="facility">{opts(r["types"])}</select></label>
<label class="m">{esc(r["temp"])}<select name="temperature">{opts(r["temps"])}</select></label>
<label class="m">{esc(r["area"])}<input name="area" type="number" min="1" inputmode="numeric" placeholder="{esc(r["area_ph"])}"></label>
<label class="m">{esc(r["start"])}<input name="start" type="month"></label>
<label class="m full">{esc(r["email"])}<input name="email" type="email" required autocomplete="email" placeholder="{esc(r["email_ph"])}" dir="ltr"></label>
<button type="submit" class="btn btn-p full">{esc(r["send"])}</button>
<a class="m full wa" href="{WHATSAPP}">{esc(r["whatsapp"])} →</a>
</form></div></section>'''


def cold_body(t, v):
    c, nav, lang = t["cold"], t["nav"], t["lang"]
    spec = "".join(f'<div><dt class="m">{esc(a)}</dt><dd class="m{" acc" if i == 4 else ""}">{num(b) if any(ch.isdigit() for ch in b) else esc(b)}</dd></div>' for i, (a, b) in enumerate(c["spec"]))
    parts = "".join(f'<li><div class="step"><span class="num m">0{i + 1}</span><span><span class="t" style="font-size:18px">{esc(a)}</span><span class="s" style="font-size:14px">{esc(b)}</span></span></div></li>' for i, (a, b) in enumerate(c["parts"]))
    head = "".join(f'<th scope="col" class="m">{esc(x)}</th>' for x in c["cols"])
    rows = "".join(f'<tr><th scope="row">{esc(a)}</th><td>{esc(b)}</td><td>{esc(cc)}</td><td class="m">{esc(d)}</td></tr>' for a, b, cc, d in c["rows"])
    proc = "".join(f'<li><div class="m acc">0{i + 1}</div><div style="font-size:19px;font-weight:700;margin:10px 0 8px">{esc(a)}</div><p>{esc(b)}</p></li>' for i, (a, b) in enumerate(c["process"]))
    rel = "".join(proj_card(x, lang, True) for x in ["al-raed", "al-asmakh", "gwc-ras-laffan"])
    faq = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in c["faq"])
    ds = "".join(f'<a class="chip m" href="/assets/ftc-qatar-brochure.pdf">{esc(x)}</a>' for x in c["datasheets"])
    return f'''
<section class="base"><div class="wrap" style="padding-block:56px 96px">
<nav aria-label="Breadcrumb" class="crumb m"><a href="/{lang}/">{esc(nav["home"])}</a><span aria-hidden="true">/</span><a href="/{lang}/solutions/">{esc(nav["solutions"])}</a><span aria-hidden="true">/</span><a href="/{lang}/refrigeration/">{esc(nav["refrigeration"])}</a><span aria-hidden="true">/</span><span aria-current="page">{esc(nav["cold_rooms"])}</span></nav>
<div class="split" style="margin-top:56px;align-items:flex-end;gap:56px">
<div style="flex:1 1 620px"><p class="m eyebrow" style="margin-bottom:24px">{esc(c["eyebrow"])}</p><h1 class="d" style="font-size:clamp(48px,8vw,128px);line-height:.88">{esc(c["title"])}</h1><p class="lead" style="margin:32px 0 0;font-size:19px;max-width:600px">{esc(c["lead"])}</p></div>
<dl class="specs">{spec}</dl></div></div></section>
<section class="base bt bb" style="background:var(--bg-2)"><div class="wrap sec split" style="align-items:center">
<figure class="fig" style="position:static">{anatomy_svg(t)}<figcaption class="m"><span>{esc(c["fig_caption"])}</span></figcaption></figure>
<div><p class="m eyebrow">{esc(c["anatomy_eyebrow"])}</p><h2 class="d h2" style="font-size:clamp(34px,4.4vw,64px)">{esc(c["anatomy_title"])}</h2><ol class="steps">{parts}</ol></div></div></section>
<section class="base"><div class="wrap sec"><p class="m eyebrow">{esc(c["choose_eyebrow"])}</p><h2 class="d h2" style="font-size:clamp(34px,4.4vw,64px);margin-bottom:48px">{esc(c["choose_title"])}</h2>
<div class="tbl-box"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div></div></section>
<section class="base bt" style="background:var(--bg-2)"><div class="wrap sec"><h2 class="d h2" style="font-size:clamp(30px,3.6vw,52px);margin-bottom:40px">{esc(L(CAT["ui"]["range"], lang))}</h2>{products_grid(LINES["cold-rooms"], lang)}</div></section>
<section class="alt"><div class="wrap sec"><p class="m eyebrow">{esc(c["process_eyebrow"])}</p><h2 class="d h2" style="font-size:clamp(34px,4.4vw,64px);margin-bottom:48px">{esc(c["process_title"])}</h2><ol class="timeline">{proc}</ol></div></section>
<section class="base"><div class="wrap sec"><div class="sec-head" style="margin-bottom:40px"><h2 class="d" style="font-size:clamp(30px,3.6vw,52px)">{esc(c["related_title"])}</h2><div class="chips" style="margin:0">{ds}</div></div><div class="projects">{rel}</div></div></section>
<section class="base bt"><div class="wrap sec split" style="gap:56px"><h2 class="d" style="flex:1 1 300px;font-size:clamp(30px,3.6vw,52px)">{esc(c["faq_title"])}</h2><div style="flex:2 1 540px">{faq}</div></div></section>
<section class="band"><div class="wrap" style="padding-block:88px;display:flex;flex-wrap:wrap;gap:32px;align-items:center;justify-content:space-between">
<h2 class="d" style="font-size:clamp(40px,5.4vw,84px);max-width:13ch">{esc(c["cta_title"])}</h2>
<div class="btns"><a class="btn btn-dark" href="/{lang}/#rfq">{esc(c["cta"])}</a><a class="btn btn-line" style="border:1px solid" href="{tel(PHONE_HEAD)}">{num(PHONE_HEAD)}</a></div></div></section>'''


# ---- Catalogue pages (src/i18n/catalog.json: [en, ar] pairs) ----
CAT = json.loads((SRC / "i18n" / "catalog.json").read_text("utf-8"))
PILLARS = {x["slug"]: x for x in CAT["pillars"]}
LINES = {x["slug"]: x for x in CAT["lines"]}
PROJECTS = {x["slug"]: x for x in CAT["projects"]}


def L(x, lang):
    """Pick the language from an [en, ar] pair; plain strings pass through."""
    return x[0 if lang == "en" else 1] if isinstance(x, list) else x


def crumbs(t, *trail):
    lang, nav = t["lang"], t["nav"]
    parts = [f'<a href="/{lang}/">{esc(nav["home"])}</a>']
    for i, (label, href) in enumerate(trail):
        last = i == len(trail) - 1
        parts.append(f'<span aria-current="page">{esc(label)}</span>' if last or not href else f'<a href="{href}">{esc(label)}</a>')
    return '<nav aria-label="Breadcrumb" class="crumb m">' + '<span aria-hidden="true">/</span>'.join(parts) + '</nav>'


def phero(t, trail, eyebrow, title, lead, side=""):
    return (f'<section class="base phero"><div class="wrap" style="padding-block:56px 88px">{crumbs(t, *trail)}'
            f'<div class="split" style="margin-top:56px;align-items:flex-end;gap:56px"><div style="flex:1 1 620px">'
            f'<p class="m eyebrow" style="margin-bottom:24px">{esc(eyebrow)}</p><h1 class="d">{esc(title)}</h1>'
            + (f'<p class="lead" style="margin:32px 0 0;font-size:19px;max-width:620px">{esc(lead)}</p>' if lead else "")
            + f'</div>{side}</div></div></section>')


def cta_band(t, title=None):
    u, lang = CAT["ui"], t["lang"]
    return (f'<section class="band"><div class="wrap" style="padding-block:80px;display:flex;flex-wrap:wrap;gap:32px;align-items:center;justify-content:space-between">'
            f'<h2 class="d" style="font-size:clamp(36px,5vw,76px);max-width:14ch">{esc(title or L(u["cta_title"], lang))}</h2>'
            f'<div class="btns"><a class="btn btn-dark" href="/{lang}/#rfq">{esc(L(u["cta"], lang))}</a>'
            f'<a class="btn btn-line" style="border:1px solid" href="{tel(PHONE_HEAD)}">{num(PHONE_HEAD)}</a></div></div></section>')


def pimg(name, alt, cls="plate"):
    if not name:
        return f'<div class="{cls} none" aria-hidden="true"><span class="m">FTC</span></div>'
    return f'<div class="{cls}"><img src="/assets/img/p/{name}.webp" alt="{esc(alt)}" loading="lazy" width="800" height="600"></div>'


def line_card(slug, lang, i=None):
    ln = LINES[slug]
    img = next((it["img"] for it in ln["items"] if it["img"]), None)
    top = f'<span>{i + 1:02d}</span>' if i is not None else ""
    return (f'<a class="lcard" href="/{lang}/{slug}/">{pimg(img, L(ln["title"], lang))}<div class="lc-b">'
            f'<div class="top m">{top}<span>{len(ln["items"])} {esc(L(CAT["ui"]["items"], lang))}</span></div>'
            f'<h3>{esc(L(ln["title"], lang))}</h3><p>{esc(L(ln["lead"], lang))}</p></div></a>')


def proj_card(slug, lang, small=False):
    pj = PROJECTS[slug]
    tag = f'{L(pj["sector"], lang)} · {L(pj["place"], lang)}'
    scope = " · ".join(L(x, lang) for x in pj["scope"][:2])
    return (f'<a class="proj" href="/{lang}/projects/{slug}/"><div class="ph"><img src="/assets/img/ref/{pj["imgs"][0]}.webp" alt="{esc(L(pj["title"], lang))}" loading="lazy" width="1200" height="900"></div>'
            f'<div class="m acc">{esc(tag)}</div><h3{" style=\"font-size:20px\"" if small else ""}>{esc(L(pj["title"], lang))}</h3><p>{esc(scope)}</p></a>')


def solutions_body(t, v):
    lang, u = t["lang"], CAT["ui"]
    blocks = ""
    for k, pl in enumerate(CAT["pillars"]):
        cards = "".join(line_card(s, lang) for s in pl["lines"])
        blocks += (f'<section class="base bt"><div class="wrap sec"><div class="sec-head"><div><p class="m eyebrow">0{k + 1} · {esc(L(pl["tag"], lang))}</p>'
                   f'<h2 class="d h2" style="font-size:clamp(34px,4.4vw,64px)"><a href="/{lang}/{pl["slug"]}/">{esc(L(pl["title"], lang))}</a></h2></div>'
                   f'<p class="lead" style="margin:0;max-width:420px">{esc(L(pl["lead"], lang))}</p></div><div class="lgrid">{cards}</div></div></section>')
    return phero(t, [(t["nav"]["solutions"], None)], L(u["solutions_title"], lang), t["solutions"]["title"], L(u["solutions_lead"], lang)) + blocks + cta_band(t)


def pillar_body(t, v, pl):
    lang, u = t["lang"], CAT["ui"]
    cards = "".join(line_card(s, lang, i) for i, s in enumerate(pl["lines"]))
    projs = []
    for s in pl["lines"]:
        projs += [p for p in LINES[s]["projects"] if p not in projs]
    side = f'<dl class="specs"><div><dt class="m">{esc(L(u["brands"], lang))}</dt><dd class="m">{esc(pl["brands"])}</dd></div></dl>'
    body = phero(t, [(t["nav"]["solutions"], f"/{lang}/solutions/"), (L(pl["tag"], lang), None)], L(pl["tag"], lang), L(pl["title"], lang), L(pl["lead"], lang), side)
    body += f'<section class="alt"><div class="wrap sec"><p class="m eyebrow">{esc(L(u["lines_in"], lang))}</p><div class="lgrid" style="margin-top:32px">{cards}</div></div></section>'
    if projs:
        body += (f'<section class="base"><div class="wrap sec"><div class="sec-head"><h2 class="d h2" style="font-size:clamp(30px,3.6vw,52px)">{esc(L(u["related_projects"], lang))}</h2>'
                 f'<a class="m link" href="/{lang}/projects/">{esc(L(u["all_projects"], lang))} →</a></div><div class="projects">{"".join(proj_card(p, lang) for p in projs[:6])}</div></div></section>')
    return body + cta_band(t)


def products_grid(ln, lang):
    u = CAT["ui"]
    out = ""
    for i, it in enumerate(ln["items"]):
        name = L(it["name"], lang)
        out += (f'<article class="prod">{pimg(it["img"], name)}<div class="pb"><div class="m acc">{i + 1:02d}</div><h3>{esc(name)}</h3>'
                f'<p>{esc(L(it["desc"], lang))}</p><a class="m go" href="/{lang}/#rfq">{esc(L(u["enquire"], lang))} →</a></div></article>')
    return f'<div class="pgrid">{out}</div>'


def line_body(t, v, ln):
    lang, u = t["lang"], CAT["ui"]
    pl = PILLARS[ln["pillar"]]
    side = (f'<dl class="specs"><div><dt class="m">{esc(L(u["products"], lang))}</dt><dd class="m">{num(str(len(ln["items"])))}</dd></div>'
            f'<div><dt class="m">{esc(L(u["brands"], lang))}</dt><dd class="m acc">{esc(ln["brands"])}</dd></div></dl>')
    body = phero(t, [(t["nav"]["solutions"], f"/{lang}/solutions/"), (L(pl["tag"], lang), f"/{lang}/{pl['slug']}/"), (L(ln["title"], lang), None)],
                 L(pl["title"], lang), L(ln["title"], lang), L(ln["lead"], lang), side)
    body += (f'<section class="alt-soft base bt" style="background:var(--bg-2)"><div class="wrap sec"><div class="sec-head"><h2 class="d h2" style="font-size:clamp(30px,3.6vw,52px)">{esc(L(u["range"], lang))}</h2>'
             f'<a class="chip m" href="/assets/ftc-qatar-brochure.pdf">{esc(L(u["brochure"], lang))}</a></div>{products_grid(ln, lang)}</div></section>')
    if ln["projects"]:
        body += (f'<section class="base"><div class="wrap sec"><h2 class="d" style="font-size:clamp(30px,3.6vw,52px);margin-bottom:40px">{esc(L(u["related_projects"], lang))}</h2>'
                 f'<div class="projects">{"".join(proj_card(p, lang, True) for p in ln["projects"])}</div></div></section>')
    others = [s for s in pl["lines"] if s != ln["slug"]]
    if others:
        body += (f'<section class="base bt"><div class="wrap sec"><p class="m eyebrow">{esc(L(u["other_lines"], lang))} {esc(L(pl["title"], lang))}</p>'
                 f'<div class="lgrid" style="margin-top:32px">{"".join(line_card(s, lang) for s in others)}</div></div></section>')
    return body + cta_band(t)


def projects_body(t, v):
    lang, pp, u = t["lang"], CAT["projects_page"], CAT["ui"]
    sectors = []
    for pj in CAT["projects"]:
        if pj["sector"][0] not in [s[0] for s in sectors]: sectors.append(pj["sector"])
    chips = f'<button type="button" class="chip m on" data-f="*">{esc(L(u["filter_all"], lang))}</button>' + "".join(
        f'<button type="button" class="chip m" data-f="{esc(s[0])}">{esc(L(s, lang))}</button>' for s in sectors)
    cards = "".join(f'<div class="pf" data-s="{esc(pj["sector"][0])}">{proj_card(pj["slug"], lang)}</div>' for pj in CAT["projects"])
    return (phero(t, [(L(pp["title"], lang), None)], L(pp["eyebrow"], lang), L(pp["title"], lang), L(pp["lead"], lang))
            + f'<section class="base bt"><div class="wrap sec"><div class="chips pfilter" style="margin:0 0 40px">{chips}</div><div class="projects">{cards}</div></div></section>' + cta_band(t))


def project_body(t, v, pj):
    lang, u, pp = t["lang"], CAT["ui"], CAT["projects_page"]
    title = L(pj["title"], lang)
    side = (f'<dl class="specs"><div><dt class="m">{esc(t["nav"]["industries"])}</dt><dd class="m">{esc(L(pj["sector"], lang))}</dd></div>'
            f'<div><dt class="m">{"الموقع" if lang == "ar" else "Location"}</dt><dd class="m acc">{esc(L(pj["place"], lang))}</dd></div></dl>')
    body = phero(t, [(L(pp["title"], lang), f"/{lang}/projects/"), (title, None)], f'{L(pj["sector"], lang)} · {L(pj["place"], lang)}', title, "", side)
    imgs = pj["imgs"]
    gal = "".join(f'<div class="ph"><img src="/assets/img/ref/{im}.webp" alt="{esc(title)}" loading="{"eager" if i == 0 else "lazy"}" width="1200" height="800"></div>' for i, im in enumerate(imgs))
    body += f'<section class="base"><div class="wrap"><div class="gal n{min(len(imgs), 3)}">{gal}</div></div></section>'
    scope = "".join(f'<li><span class="m acc">{i + 1:02d}</span><span>{esc(L(x, lang))}</span></li>' for i, x in enumerate(pj["scope"]))
    lines = "".join(f'<a class="chip m" href="/{lang}/{s}/">{esc(L(LINES[s]["title"], lang))}</a>' for s in pj["lines"])
    body += (f'<section class="base"><div class="wrap sec split" style="gap:56px"><div><p class="m eyebrow">{esc(L(u["project_info"], lang))}</p>'
             f'<p class="lead" style="font-size:20px;max-width:none;color:var(--fg)">{esc(L(pj["info"], lang))}</p>'
             f'<p class="m eyebrow" style="margin-top:40px">{esc(L(u["solutions_used"], lang))}</p><div class="chips" style="margin:0">{lines}</div></div>'
             f'<div><p class="m eyebrow">{esc(L(u["our_scope"], lang))}</p><ol class="scope">{scope}</ol></div></div></section>')
    order = [p["slug"] for p in CAT["projects"]]
    nxt = PROJECTS[order[(order.index(pj["slug"]) + 1) % len(order)]]
    body += (f'<section class="base bt"><div class="wrap" style="padding-block:56px"><a class="next" href="/{lang}/projects/{nxt["slug"]}/">'
             f'<span class="m muted">{esc(L(u["next_project"], lang))} →</span><span class="d">{esc(L(nxt["title"], lang))}</span></a></div></section>')
    return body + cta_band(t)


def about_body(t, v):
    lang, a = t["lang"], CAT["about"]
    caps = "".join(f'<li><span class="m acc">{i + 1:02d}</span><span>{esc(L(x, lang))}</span></li>' for i, x in enumerate(a["caps"]))
    vals = "".join(f'<div><div class="m acc">{i + 1:02d}</div><div class="d">{esc(L(n, lang))}</div><p>{esc(L(d, lang))}</p></div>' for i, (n, d) in enumerate(a["values"]))
    tl = "".join(f'<li><div class="d{" now" if y == "2008" else ""}">{num(y)}</div><p>{esc(L(d, lang))}</p></li>' for y, d in a["history"])
    stats = "".join(f'<div class="stat"><div class="d">{num(x)}</div><span class="m">{esc(y)}</span></div>' for x, y in t["stats"])
    g = t["group"]
    offices = "".join(f'<li><span style="font-weight:600">{esc(c)}</span><span class="m">{esc(co)}</span></li>' for c, co, *_ in g["items"])
    return (phero(t, [(t["nav"]["about"], None)], L(a["eyebrow"], lang), L(a["title"], lang), L(a["intro"], lang))
            + f'<section class="base bt bb" aria-label="{esc(t["stats_label"])}"><div class="wrap stats">{stats}</div></section>'
            + f'<section class="base"><div class="wrap sec split" style="gap:56px"><ol class="scope">{caps}</ol><p class="lead" style="font-size:20px;color:var(--fg);max-width:none">{esc(L(a["people"], lang))}</p></div></section>'
            + f'<section class="alt"><div class="wrap sec"><div class="cards3">'
              f'<div class="card"><div class="m acc">{esc(L(a["vision_t"], lang))}</div><div class="s" style="font-size:19px;color:inherit">{esc(L(a["vision"], lang))}</div></div>'
              f'<div class="card hl"><div class="m acc">{esc(L(a["mission_t"], lang))}</div><div class="s" style="font-size:19px;color:inherit">{esc(L(a["mission"], lang))}</div></div></div></div></section>'
            + f'<section class="base"><div class="wrap sec"><p class="m eyebrow">{esc(L(a["values_t"], lang))}</p><h2 class="d h2" style="margin-bottom:52px">{esc(L(a["values_t"], lang))}</h2><div class="cols4 vals">{vals}</div></div></section>'
            + f'<section class="base bt" style="background:var(--bg-2)"><div class="wrap sec"><p class="m eyebrow">{esc(t["lineage"]["eyebrow"].split("·")[-1].strip())}</p><h2 class="d h2" style="margin-bottom:52px">{esc(L(a["history_t"], lang))}</h2><ol class="timeline">{tl}</ol></div></section>'
            + f'<section class="base bt"><div class="wrap sec split" style="align-items:center"><div><p class="m eyebrow">{esc(g["eyebrow"])}</p><h2 class="d h2" style="margin-bottom:24px">{esc(g["title"])}</h2><p class="lead">{esc(g["lead"])}</p>'
              f'<a class="btn btn-o" style="margin-top:24px" href="/{lang}/contact/#companies">{esc(L(a["group_cta"], lang))}</a></div><ul class="offices">{offices}</ul></div></section>'
            + cta_band(t))


def services_body(t, v):
    lang, sp = t["lang"], CAT["services_page"]
    out = ""
    for i, it in enumerate(sp["items"]):
        paras = "".join(f"<p>{esc(L(p, lang))}</p>" for p in it["p"])
        extra = f'<a class="btn btn-p" href="{tel(PHONE_MAINT)}">{esc(t["nav"]["maintenance"])} · {num(PHONE_MAINT)}</a>' if it["slug"] == "maintenance" else ""
        out += (f'<section class="base bt svc" id="{it["slug"]}"><div class="wrap sec split" style="gap:56px"><div style="flex:1 1 340px"><div class="m acc">{esc(t["services"]["step"])} {i + 1}</div>'
                f'<h2 class="d h2" style="font-size:clamp(34px,4.4vw,64px);margin-top:14px">{esc(L(it["t"], lang))}</h2></div><div class="svc-t" style="flex:2 1 520px">{paras}{extra}</div></div></section>')
    return phero(t, [(t["nav"]["services"], None)], L(sp["eyebrow"], lang), L(sp["title"], lang), L(sp["lead"], lang)) + out + cta_band(t)


def contact_body(t, v):
    lang, c = t["lang"], CAT["contact_page"]
    blocks = "".join(f'<div><span class="m acc">{esc(L(a, lang))}</span><a class="d" href="{tel(n)}">{num(n)}</a><span class="m muted">{esc(L(h, lang))}</span></div>' for a, n, h in c["lines"])
    blocks += f'<div><span class="m acc">{esc(L(c["email_t"], lang))}</span><a class="d" href="mailto:info@ftc-qatar.com" dir="ltr">info@ftc-qatar.com</a></div>'
    maps = "https://www.google.com/maps/search/?api=1&query=" + "FTC+Qatar+West+Industrial+Area+Doha"
    f = lambda k: esc(L(c[k], lang))
    form = (f'<form class="rfq" data-subject="{f("subject")}" action="mailto:info@ftc-qatar.com" method="post" enctype="text/plain">'
            f'<label class="m">{f("f_name")}<input name="name" required autocomplete="name"></label>'
            f'<label class="m">{f("f_company")}<input name="company" autocomplete="organization"></label>'
            f'<label class="m">{f("f_phone")}<input name="phone" type="tel" autocomplete="tel" dir="ltr"></label>'
            f'<label class="m">{f("f_email")}<input name="email" type="email" required autocomplete="email" dir="ltr"></label>'
            f'<label class="m full">{f("f_msg")}<textarea name="message" rows="5" required></textarea></label>'
            f'<button type="submit" class="btn btn-p full">{f("f_send")}</button></form>')
    jobs = (f'<form class="rfq" data-subject="{f("jobs_subject")}" action="mailto:info@ftc-qatar.com" method="post" enctype="text/plain">'
            f'<label class="m">{f("f_name")}<input name="name" required autocomplete="name"></label>'
            f'<label class="m">{f("f_email")}<input name="email" type="email" required autocomplete="email" dir="ltr"></label>'
            f'<label class="m full">{f("f_role")}<input name="position"></label>'
            f'<label class="m full">{f("f_msg")}<textarea name="cover" rows="4"></textarea></label>'
            f'<button type="submit" class="btn btn-o full">{f("f_apply")}</button></form>')
    cos = "".join(
        f'<li><div><span style="font-weight:600">{esc(n)}</span><span class="m muted">{esc(L(co, lang))}</span></div><p>{esc(L(ad, lang))}</p>'
        + (f'<a class="m" href="{w}" rel="noopener">{f("website")} →</a>' if w else "") + '</li>' for n, co, ad, w in c["companies"])
    return (phero(t, [(L(c["eyebrow"], lang), None)], L(c["eyebrow"], lang), L(c["title"], lang), "")
            + f'<section class="base bt bb"><div class="wrap cblocks">{blocks}</div></section>'
            + f'<section class="base"><div class="wrap sec split" style="gap:56px"><div><p class="m eyebrow">{f("visit_t")}</p><p class="lead" style="color:var(--fg)">{t["footer"]["address"]}</p>'
              f'<a class="m link" href="{maps}" rel="noopener">{f("map")} →</a></div><div><h2 class="d" style="font-size:clamp(30px,3.6vw,52px);margin-bottom:28px">{f("form_t")}</h2>{form}</div></div></section>'
            + f'<section class="base bt" id="companies" style="background:var(--bg-2)"><div class="wrap sec"><h2 class="d h2" style="margin-bottom:48px">{f("companies_t")}</h2><ul class="co">{cos}</ul></div></section>'
            + f'<section class="base bt" id="jobs"><div class="wrap sec split" style="gap:56px"><div><h2 class="d" style="font-size:clamp(30px,3.6vw,52px)">{f("jobs_t")}</h2><p class="lead">{f("jobs_lead")}</p></div>{jobs}</div></section>')


def build(site_urls):
    loc = {l: json.loads((SRC / "i18n" / f"{l}.json").read_text("utf-8")) for l in LANGS}
    for v in ["v1", "v2"]:
        site_url = site_urls[v].rstrip("/")
        out = DIST / v
        if out.exists(): shutil.rmtree(out)
        (out / "assets").mkdir(parents=True)
        shutil.copytree(SRC / "css", out / "assets/css")
        shutil.copytree(SRC / "img", out / "assets/img")
        if v == "v1": (out / "assets/img/hero-loop.mp4").unlink()
        (out / "assets/js").mkdir()
        for f in ["site.js", "motion.js"]: shutil.copy(SRC / "js" / f, out / "assets/js" / f)
        if (ROOT / "research/ftc-brochure-current.pdf").exists():
            shutil.copy(ROOT / "research/ftc-brochure-current.pdf", out / "assets/ftc-qatar-brochure.pdf")
        if v == "v2":
            for f in ["cutaway.js", "globe.js", "film.js"]: shutil.copy(SRC / "js/v2" / f, out / "assets/js" / f)
            shutil.copytree(SRC / "vendor/jsm", out / "assets/vendor/jsm")
            shutil.copytree(SRC / "models", out / "assets/models")
            if (SRC / "film").exists(): shutil.copytree(SRC / "film", out / "assets/film")
            shutil.copy(SRC / "vendor/three.module.min.js", out / "assets/vendor/three.module.min.js")
            (out / "assets/data").mkdir()
            shutil.copy(SRC / "data/land-dots.json", out / "assets/data/land-dots.json")
        urls = []
        for l, t in loc.items():
            sfx = " | " + t["brand"]
            pages = {"": (t["meta"]["home_title"], t["meta"]["home_desc"], home_body(t, v)),
                     "cold-rooms": (t["meta"]["cold_title"], t["meta"]["cold_desc"], cold_body(t, v)),
                     "solutions": (t["nav"]["solutions"] + sfx, L(CAT["ui"]["solutions_lead"], l), solutions_body(t, v))}
            for pl in CAT["pillars"]:
                pages[pl["slug"]] = (L(pl["title"], l) + sfx, L(pl["lead"], l), pillar_body(t, v, pl))
            for ln in CAT["lines"]:
                if ln["slug"] != "cold-rooms":
                    pages[ln["slug"]] = (L(ln["title"], l) + sfx, L(ln["lead"], l), line_body(t, v, ln))
            pp = CAT["projects_page"]
            pages["projects"] = (L(pp["meta"], l), L(pp["lead"], l), projects_body(t, v))
            for pj in CAT["projects"]:
                pages["projects/" + pj["slug"]] = (L(pj["title"], l) + sfx, L(pj["info"], l)[:155], project_body(t, v, pj))
            pages["about"] = (L(CAT["about"]["meta"], l), L(CAT["about"]["intro"], l), about_body(t, v))
            pages["services"] = (L(CAT["services_page"]["meta"], l), L(CAT["services_page"]["lead"], l), services_body(t, v))
            pages["contact"] = (L(CAT["contact_page"]["meta"], l), t["footer"]["entity"] + " · " + PHONE_HEAD, contact_body(t, v))
            for slug, (title, desc, body) in pages.items():
                d = out / l / slug if slug else out / l
                d.mkdir(parents=True, exist_ok=True)
                (d / "index.html").write_text(page(t, v, slug, title, desc, body, site_url), "utf-8")
                urls.append(f"{site_url}/{l}/" + (f"{slug}/" if slug else ""))
        (out / "index.html").write_text(
            '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>FTC Qatar</title>'
            '<meta name="viewport" content="width=device-width, initial-scale=1"><link rel="canonical" href="' + site_url + '/en/">'
            '<script>location.replace((navigator.language||"").toLowerCase().startsWith("ar")?"/ar/":"/en/")</script>'
            '<meta http-equiv="refresh" content="1; url=/en/"></head><body style="font-family:sans-serif;background:#060A0F;color:#EAF2F7;padding:40px">'
            '<a href="/en/" style="color:#04AFF0">FTC Qatar — English</a> · <a href="/ar/" lang="ar" style="color:#04AFF0">إف تي سي قطر — العربية</a></body></html>', "utf-8")
        (out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                         + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>\n", "utf-8")
        (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n", "utf-8")
        print(v, "->", out, len(urls), "pages")


if __name__ == "__main__":
    a = sys.argv[1:]
    urls = {"v1": "https://ftc-qatar-v1.onrender.com", "v2": "https://ftc-qatar-v2.onrender.com"}
    for i, x in enumerate(a):
        if x in ("--v1-url", "--v2-url"): urls[x[2:4]] = a[i + 1]
    build(urls)
