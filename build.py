#!/usr/bin/env python3
"""Static site generator for C'est la vie Sports Bar (Python 3 standard library only).

Reads  data/site.json, data/drinks.json, data/i18n.json
Writes index.html, impressum.html, datenschutz.html (and language/other pages)
Run:   python3 build.py
Never edit the generated HTML by hand: change the data files or this script.
"""
import html
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SITE_URL = "https://DOMAIN"  # the ONE place to set the domain (no trailing slash)
LANGS = ["de", "en"]
DEFAULT_LANG = "de"
# Colour palette (all colour tokens live in this one file, loaded before css/style.css).
# Default "pitch" = css/palette.css. Alternatives: css/themes/ember.css, volt.css, derby.css, gold.css
# Branch design-eintracht: black / red / white matchday theme.
PALETTE = "css/themes/eintracht.css"
THEME_COLOR = {"dark": "#0b0b0c", "light": "#0b0b0c"}  # static <meta theme-color> fallback (= the always-dark header)

# Self-hosted fonts (no CDN). css/fonts.css is linked only when every file below exists in
# assets/fonts/, so a checkout without the font files falls back to the local font stacks
# in css/style.css and never requests a missing file. Licence: SIL OFL 1.1 (assets/fonts/OFL.txt).
FONT_FILES = [
    "barlow-condensed-latin-700-normal.woff2",
    "barlow-condensed-latin-800-normal.woff2",
    "barlow-condensed-latin-800-italic.woff2",
    "barlow-latin-400-normal.woff2",
    "barlow-latin-600-normal.woff2",
    "barlow-latin-700-normal.woff2",
]
FONT_PRELOAD = "barlow-condensed-latin-800-italic.woff2"  # the hero / page headline face

DATA = Path(os.environ.get("CLV_DATA_DIR", ROOT / "data"))  # override only for tests
OUT = Path(os.environ.get("CLV_OUT_DIR", ROOT))
SITE = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
DRINKS = json.loads((DATA / "drinks.json").read_text(encoding="utf-8"))
I18N = json.loads((DATA / "i18n.json").read_text(encoding="utf-8"))
SCHEDULE = json.loads((DATA / "schedule.json").read_text(encoding="utf-8"))
NOW = datetime.now(timezone.utc)  # build time: past matches are hidden relative to this
TZ = ZoneInfo("Europe/Berlin")

TODOS = []  # collected while building


# ---------------------------------------------------------------- helpers
def missing(v):
    return v is None or (isinstance(v, str) and (not v.strip() or v.strip().startswith("TODO")))


def get(path, default=None, *, report=True):
    """Read a dotted path from site.json. Missing/TODO values return default and are reported."""
    cur = SITE
    for part in path.split("."):
        cur = cur.get(part) if isinstance(cur, dict) else None
    if missing(cur):
        if report and path not in TODOS:
            TODOS.append(path)
        return default
    return cur


def loc(v, lang):
    if isinstance(v, dict):
        return v.get(lang) or v.get(DEFAULT_LANG) or ""
    return v if v is not None else ""


def esc(s):
    return html.escape(str(s), quote=False)


def attr(s):
    return html.escape(str(s), quote=True)


def tr(lang, key):
    return I18N[lang][key]


def lang_prefix(lang):
    return "" if lang == DEFAULT_LANG else lang + "/"


def rel_root(lang, depth=0):
    """Relative path from a page back to the site root."""
    return "../" * (depth + (0 if lang == DEFAULT_LANG else 1))


def img_alt(text):
    """Descriptive alt only for real photos; the placeholder illustrations are decorative (alt="")."""
    if SITE.get("images", {}).get("photos_are_real"):
        return attr(text)
    if "images.photos_are_real" not in TODOS:
        TODOS.append("images.photos_are_real (real photos missing: placeholder images are marked decorative, alt=\"\")")
    return ""


def digits(s):
    return "".join(ch for ch in str(s) if ch.isdigit())


# ---------------------------------------------------------------- business facts
def full_address_line():
    street = get("address.street", report=False)
    parts = [street, f'{get("address.postal_code", "")} {get("address.locality", "")}'.strip()]
    return ", ".join(p for p in parts if p)


def route_url():
    maps = get("maps_url", report=False)
    if maps:
        return maps
    street = get("address.street", report=False)
    name = SITE["name"]
    if street:
        q = f'{name}, {street}, {get("address.postal_code", "")} {get("address.locality", "")}'
    else:
        q = f'{name} {SITE["area_label"]}'
    return "https://www.google.com/maps/search/?api=1&query=" + quote(q)


def hours_numeric():
    """List indexed by JS getDay() (0 = Sunday): [open, close] in hours; close > 24 means after midnight."""
    names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    days = SITE["hours"]["days"]
    out = []
    for n in names:
        d = days.get(n)
        if not d:
            out.append(None)
            continue

        def h(t):
            hh, mm = t.split(":")
            return int(hh) + int(mm) / 60

        o, c = h(d["open"]), h(d["close"])
        if c <= o:
            c += 24
        out.append([o, c])
    return out


def fmt_hour(x):
    x = x % 24
    return f"{int(x):02d}:{int(round((x % 1) * 60)):02d}"


# ---------------------------------------------------------------- meta, facts, FAQ
def page_url(lang, path=""):
    return f"{SITE_URL}/{lang_prefix(lang)}{path}"


# page key -> {lang: path relative to that language's root}. Every key exists in every language.
PAGES = {
    "home": {"de": "", "en": ""},
    "impressum": {"de": "impressum.html", "en": "impressum.html"},
    "datenschutz": {"de": "datenschutz.html", "en": "datenschutz.html"},
    "schedule": {"de": "spielplan/", "en": "schedule/"},
    "eintracht": {"de": "eintracht/", "en": "eintracht/"},
}


def page_key(lang, path):
    return next(k for k, v in PAGES.items() if v[lang] == path)


def alternates(lang, path):
    """hreflang alternates: every language + x-default (-> default language), absolute URLs."""
    key = page_key(lang, path)
    lines = [f'<link rel="alternate" hreflang="{l}" href="{attr(page_url(l, PAGES[key][l]))}">' for l in LANGS]
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{attr(page_url(DEFAULT_LANG, PAGES[key][DEFAULT_LANG]))}">')
    return lines


def switch_href(lang, path):
    """Relative link from this page to the same page in the other language."""
    other = [l for l in LANGS if l != lang][0]
    up = "../" * (path.count("/") + (0 if lang == DEFAULT_LANG else 1))
    return up + lang_prefix(other) + PAGES[page_key(lang, path)][other]


def home_description(lang):
    t = I18N[lang]
    n = get("venue.screens", report=False)
    stadium = nearby_place(SITE["local"]["stadium_name"])
    near = t["descNear"].format(dist=fmt_dist(lang, stadium["distance_km"]), stadium=stadium["name"]) if stadium else ""
    return (t["description"].replace("{screens}", t["descScreens"].format(n=n) if n else "")
            .replace("{near}", near))


def meta_block(lang, path, title, desc, social=True):
    url = page_url(lang, path)
    if len(desc) > 160:
        print(f"WARNING: meta description >160 chars ({len(desc)}): {path or '/'}", file=sys.stderr)
    t = I18N[lang]
    lines = [f'<meta name="description" content="{attr(desc)}">', f'<link rel="canonical" href="{attr(url)}">']
    lines += alternates(lang, path)
    if social:
        img = f"{SITE_URL}/assets/img/og-image.jpg"
        lines += [
            '<meta property="og:type" content="website">',
            f'<meta property="og:site_name" content="{attr(SITE["name"])}">',
            f'<meta property="og:locale" content="{t["ogLocale"]}">',
            f'<meta property="og:title" content="{attr(title)}">',
            f'<meta property="og:description" content="{attr(desc)}">',
            f'<meta property="og:url" content="{attr(url)}">',
            f'<meta property="og:image" content="{img}">',
            '<meta property="og:image:type" content="image/jpeg">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            f'<meta property="og:image:alt" content="{attr(t["ogImageAlt"])}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{attr(title)}">',
            f'<meta name="twitter:description" content="{attr(desc)}">',
            f'<meta name="twitter:image" content="{img}">',
            f'<meta name="twitter:image:alt" content="{attr(t["ogImageAlt"])}">',
        ]
    return "\n".join("    " + l for l in lines)


def venue_facts(lang):
    """Short quotable facts, only from confirmed data in site.json."""
    t = I18N[lang]
    out = []
    n = get("venue.screens")
    if n:
        out.append(t["factScreens"].format(n=n))
    n = get("venue.seats")
    if n:
        out.append(t["factSeats"].format(n=n))
    if get("venue.sound_on_for_eintracht") is True:
        out.append(t["factSound"])
    subs = get("venue.subscriptions")
    if subs:
        out.append(t["factSubs"].format(subs=", ".join(subs) if isinstance(subs, list) else subs))
    how = loc(get("venue.reservation_how"), lang) if get("venue.accepts_reservations") is True else ""
    if how and not missing(how):
        out.append(t["factReserve"].format(how=how))
    pr = get("venue.price_range")
    if pr:
        out.append(t["factPrice"].format(pr=pr))
    return out


def join_list(lang, items):
    """'A, B und C' / 'A, B and C'."""
    items = list(items)
    if len(items) < 2:
        return "".join(items)
    return ", ".join(items[:-1]) + (" und " if lang == "de" else " and ") + items[-1]


def cap(s):
    return s[:1].upper() + s[1:]


def fmt_km(lang, km):
    """2.0 -> '2', 2.5 -> '2,5' (de) / '2.5' (en)."""
    s = f"{float(km):g}"
    return s.replace(".", ",") if lang == "de" else s


def fmt_dist(lang, km):
    """Rounded straight-line distance as words: 'ca. 2,5 km' / 'about 2.5 km'."""
    return f'{I18N[lang]["nearAbout"]} {fmt_km(lang, km)} km'


# Beer detection in data/drinks.json (names are matched in German, lower case). drinks.json has no
# "is beer" flag, so this list decides; anything else (e.g. Apfelwein on tap) is never called a beer.
BEER_WORDS = ("pils", "weizen", "weißbier", "radler", "bier", "helles", "export", "lager", "kölsch", "bock")


def beer_groups(lang):
    """[(category id, category label, [(menu name, name inside a sentence)])] from data/drinks.json,
    in menu order, one entry per beer (sizes merged). Only drinks that are really on the menu."""
    out = []
    for c in DRINKS.get("categories", []):
        names = []
        for it in c.get("items", []):
            if not any(w in loc(it["name"], "de").lower() for w in BEER_WORDS):
                continue
            n = loc(it["name"], lang)
            # English translations are common nouns ("wheat beer"); German nouns and names ("Pils") keep their capital
            inline = n[:1].lower() + n[1:] if lang != "de" and isinstance(it["name"], dict) else n
            if n not in [x for x, _ in names]:
                names.append((n, inline))
        if names:
            out.append((c["id"], loc(c["name"], lang), names))
    return out


def show_beers():
    return get("venue.beer_variety") is True and sum(len(g[2]) for g in beer_groups(DEFAULT_LANG)) >= 2


def music_how(lang):
    """How guests choose the music, once the owner has said so (site.json venue.music_choice_how)."""
    how = loc(get("venue.music_choice_how", report=False), lang)
    if how and not missing(how):
        return how
    msg = ("venue.music_choice_how (ask the owner HOW guests choose the music: jukebox, request at the bar, "
           "app/playlist …; until then the site only says that guests choose the music)")
    if msg not in TODOS:
        TODOS.append(msg)
    return ""


def show_music():
    return get("venue.music_choice") is True


# Per-place copy in data/i18n.json ("near<suffix>" blurb). Places without an entry show name, kind and distance only.
NEAR_COPY = {"Deutsche Bank Park": "Stadium", "Festhalle Frankfurt": "Festhalle", "Frankfurt Hauptbahnhof": "Hbf"}


def nearby_places():
    """Confirmed nearby places from site.json local.nearby_places, nearest first (straight-line km, rounded)."""
    L = SITE["local"]
    if L.get("nearby_confirmed") is not True:
        return []
    out = [p for p in L.get("nearby_places") or [] if p.get("name") and isinstance(p.get("distance_km"), (int, float))]
    return sorted(out, key=lambda p: p["distance_km"])


def nearby_place(name):
    return next((p for p in nearby_places() if p["name"] == name), None)


def hours_summary(lang):
    days = SITE["hours"]["days"]
    names = I18N[lang]["days"]
    en = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return "; ".join(f'{names[d]}: {days[en[d]]["open"]}–{days[en[d]]["close"]}' for d in [1, 2, 3, 4, 5, 6, 0] if en[d] in days)


def faq_items(lang):
    """[(question, answer, more)] built only from confirmed site.json / drinks.json data; entries without
    data are left out. more = None or (href on the home page, label): a visible follow-up link only
    (the FAQPage schema carries question and answer text, exactly as shown)."""
    t = I18N[lang]
    items = []
    if get("venue.shows_all_eintracht_matches") is True:
        a = t["faqA1"] + (t["faqA1sound"] if get("venue.sound_on_for_eintracht") is True else "")
        items.append((t["faqQ1"], a, None))
    acc = get("venue.accepts_reservations")
    how = loc(get("venue.reservation_how"), lang)
    if acc is True and how and not missing(how):
        items.append((t["faqQ2"], t["faqA2yes"].format(how=how), None))
    elif acc is False:
        items.append((t["faqQ2"], t["faqA2no"], None))
    stadium = SITE["local"]["stadium_name"]
    walk = loc(get("local.walk_from_stadium"), lang)
    if walk and not missing(walk):
        a = t["faqA3"].format(stadium=stadium, walk=walk)
        pt = loc(get("local.public_transport"), lang)
        if pt and not missing(pt):
            a += t["faqA3pt"].format(pt=pt)
        items.append((t["faqQ3"].format(stadium=stadium), a, (PAGES["eintracht"][lang], t["faqMoreEintracht"])))
    # Places near the bar (rounded straight-line distances, always worded as "about")
    for name, key in (("Festhalle Frankfurt", "Festhalle"), ("Frankfurt Hauptbahnhof", "Hbf")):
        p = nearby_place(name)
        if p:
            items.append((t[f"faqQnear{key}"], cap(t[f"faqAnear{key}"].format(dist=fmt_dist(lang, p["distance_km"]))),
                          ("#local", t["faqMoreLocal"])))
    if get("address.street"):
        items.append((t["faqQ4"], t["faqA4"].format(addr=full_address_line()), None))
    if SITE["hours"].get("confirmed") is True:
        items.append((t["faqQ5"], hours_summary(lang) + ".", None))
    parts = []
    if get("venue.seats"):
        parts.append(t["faqA6seats"].format(n=get("venue.seats")))
    if get("venue.screens"):
        parts.append(t["faqA6screens"].format(n=get("venue.screens")))
    if parts:
        items.append((t["faqQ6"], ", ".join(parts) + ".", None))
    if show_beers():
        groups = beer_groups(lang)
        a = t["faqAbeerFirst"].format(cat=groups[0][1], list=join_list(lang, [i for _, i in groups[0][2]]))
        rest = [i for g in groups[1:] for _, i in g[2]]
        if rest:
            a += t["faqAbeerAlso"].format(list=join_list(lang, rest))
        items.append((t["faqQbeer"], a + t["faqAbeerEnd"], ("#drinks", t["faqMoreDrinks"])))
    if show_music():
        how = music_how(lang)
        items.append((t["faqQmusic"], t["faqAmusic"] + (t["faqAmusicHow"].format(how=how) if how else ""), None))
    return items


def faq_section(lang):
    items = faq_items(lang)
    if not items:
        return ""

    def more(m):
        return (f'<p class="more-link faq-more"><a href="{attr(m[0])}">{esc(m[1])}<span aria-hidden="true">&nbsp;→</span></a></p>'
                if m else "")
    body = "\n                    ".join(
        f'<div class="faq-item reveal"><h3>{esc(q)}</h3><p>{esc(a)}</p>{more(m)}</div>' for q, a, m in items)
    return f'''
        <section class="section" id="faq">
            <div class="container">
                <h2>{esc(I18N[lang]["faqTitle"])}</h2>
                <div class="faq">
                    {body}
                </div>
            </div>
        </section>
'''


# ---------------------------------------------------------------- structured data (JSON-LD)
BAR_ID = SITE_URL + "/#bar"  # one stable entity id for all languages
SCHEMA_DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
AMENITY = {
    "de": {"screens": "Bildschirme", "seats": "Sitzplätze", "sound": "Ton bei Spielen von Eintracht Frankfurt",
           "music": "Gäste bestimmen die Musik"},
    "en": {"screens": "Screens", "seats": "Seats", "sound": "Sound on for Eintracht Frankfurt matches",
           "music": "Guests choose the music"},
}
BAD_VALUES = ("TODO", "Muster", "example.com", "000000", "Platzhalter")


def bar_schema(lang):
    d = {
        "@context": "https://schema.org",
        "@type": "BarOrPub",
        "@id": BAR_ID,
        "name": SITE["name"],
        "url": page_url(DEFAULT_LANG),
        "description": home_description(lang),
        "image": f"{SITE_URL}/assets/img/og-image.jpg",
    }
    phone, mail = get("contact.phone", report=False), get("contact.email", report=False)
    if phone:
        d["telephone"] = phone
    if mail:
        d["email"] = mail
    addr = {"@type": "PostalAddress"}
    street = get("address.street", report=False)
    if street:
        addr["streetAddress"] = street
    addr.update({
        "postalCode": SITE["address"]["postal_code"],
        "addressLocality": SITE["address"]["locality"],
        "addressRegion": SITE["address"]["region"],
        "addressCountry": SITE["address"]["country"],
    })
    d["address"] = addr
    try:
        d["geo"] = {"@type": "GeoCoordinates", "latitude": float(get("geo.lat", report=False)),
                    "longitude": float(get("geo.lng", report=False))}
    except (TypeError, ValueError):
        pass
    if SITE["hours"].get("confirmed") is True:
        groups = {}
        for name in SCHEMA_DAYS:
            e = SITE["hours"]["days"].get(name)
            if e:
                groups.setdefault((e["open"], e["close"]), []).append(name)
        d["openingHoursSpecification"] = [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": days, "opens": o, "closes": c}
            for (o, c), days in groups.items()]
    pr = get("venue.price_range", report=False)
    if pr:
        d["priceRange"] = pr
    acc = get("venue.accepts_reservations", report=False)
    if isinstance(acc, bool):
        d["acceptsReservations"] = acc
    am = AMENITY[lang]
    feats = []
    n = get("venue.screens", report=False)
    if n:
        feats.append({"@type": "LocationFeatureSpecification", "name": am["screens"], "value": n})
    n = get("venue.seats", report=False)
    if n:
        feats.append({"@type": "LocationFeatureSpecification", "name": am["seats"], "value": n})
    if get("venue.sound_on_for_eintracht", report=False) is True:
        feats.append({"@type": "LocationFeatureSpecification", "name": am["sound"], "value": True})
    if get("venue.music_choice", report=False) is True:  # visible: drinks section tile + FAQ
        feats.append({"@type": "LocationFeatureSpecification", "name": am["music"], "value": True})
    if feats:
        d["amenityFeature"] = feats
    if DRINKS.get("categories"):  # the drinks menu with prices is visible on the home page (#drinks)
        d["hasMenu"] = page_url(lang) + "#drinks"
    same = [get(f"social.{k}.url", report=False) for k in ("instagram", "facebook", "tiktok")]
    same.append(get("social.google_business_profile", report=False))
    same = [u for u in same if u]
    if same:
        d["sameAs"] = same
    if get("maps_url", report=False):
        d["hasMap"] = get("maps_url", report=False)
    return d


def faq_schema(lang):
    items = faq_items(lang)
    if not items:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "@id": page_url(lang) + "#faq",
        "url": page_url(lang),
        "inLanguage": lang,
        "about": {"@id": BAR_ID},
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a, _ in items],
    }


def check_schema(obj, where):
    for v in (obj.values() if isinstance(obj, dict) else obj):
        if isinstance(v, (dict, list)):
            check_schema(v, where)
        elif isinstance(v, str) and any(b in v for b in BAD_VALUES):
            raise SystemExit(f"ERROR: placeholder value in JSON-LD ({where}): {v!r}")


def jsonld_scripts(lang, blocks=None):
    out = []
    for block in (blocks if blocks is not None else (bar_schema(lang), faq_schema(lang))):
        if block:
            check_schema(block, lang)
            txt = json.dumps(block, ensure_ascii=False, indent=4).replace("</", "<\\/")
            out.append('    <script type="application/ld+json">\n' + "\n".join("    " + l for l in txt.splitlines()) + "\n    </script>")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- page fragments
def fonts_ready():
    return all((ROOT / "assets" / "fonts" / f).is_file() for f in FONT_FILES)


def head_common(lang, depth, extra=""):
    r = rel_root(lang, depth)
    fonts = ""
    if fonts_ready():
        fonts = (f'    <link rel="preload" href="{r}assets/fonts/{FONT_PRELOAD}" as="font" type="font/woff2" crossorigin>\n'
                 f'    <link rel="stylesheet" href="{r}css/fonts.css">\n')
    elif "assets/fonts" not in " ".join(TODOS):
        TODOS.append("assets/fonts: self-hosted Barlow / Barlow Condensed files missing (local font fallbacks in use), see FONT_FILES in build.py")
    # theme-color: static fallback for the active palette; js/main.js replaces it with the live background
    return f'''    <meta name="theme-color" content="{THEME_COLOR["dark"]}" media="(prefers-color-scheme: dark)">
    <meta name="theme-color" content="{THEME_COLOR["light"]}" media="(prefers-color-scheme: light)">
    <link rel="icon" href="{r}assets/icons/favicon.svg" type="image/svg+xml">
    <script>try{{var t=localStorage.getItem("theme");if(t==="light"||t==="dark")document.documentElement.dataset.theme=t}}catch(e){{}}</script>
{fonts}    <link rel="stylesheet" href="{r}{PALETTE}">
    <link rel="stylesheet" href="{r}css/style.css">
{extra}'''


def logo_svg():
    return ('<svg class="logo-mark" viewBox="0 0 48 48" aria-hidden="true" focusable="false">'
            '<path class="lm-c" pathLength="1" d="M38.14 9.86A20 20 0 1 0 38.14 38.14"/>'
            '<path class="lm-l" pathLength="1" d="M15 13V33H27"/>'
            '<path class="lm-v" pathLength="1" d="M20 13L27 33L40 6"/></svg>')


def lang_switch(lang, other_href):
    """Language switch: a real link to the other language version (omitted if there is only one language)."""
    if len(LANGS) < 2 or other_href is None:
        return ""
    other = [l for l in LANGS if l != lang][0]
    label = ('<span class="{a}" data-l="en">en</span> / <span class="{b}" data-l="de">de</span>'
             .format(a="is-active" if lang == "en" else "", b="is-active" if lang == "de" else ""))
    aria = "Auf Deutsch wechseln" if other == "de" else "Switch to English"
    return (f'<a class="lang-btn" href="{attr(other_href)}" hreflang="{other}" lang="{other}" '
            f'aria-label="{aria}">{label}</a>')


def home_href(path):
    """Relative link from a page (path relative to its language root) to that language's home page."""
    return "../" * path.count("/") or "./"


def wing_svg(cls):
    """Decorative, generic abstract wing: six slanted 'feather' bars. Not a club crest or logo."""
    bars = []
    for i, (xl, xr) in enumerate([(20, 390), (56, 376), (100, 362), (148, 348), (194, 334), (236, 320)]):
        y = 10 + i * 50
        bars.append(f'<polygon class="wing-f{i}" points="{xl + 26},{y} {xr},{y} {xr - 26},{y + 34} {xl},{y + 34}"/>')
    return (f'<svg class="{cls}" viewBox="0 0 400 304" aria-hidden="true" focusable="false">'
            + "".join(bars) + "</svg>")


def ticker_html(items, extra_cls=""):
    """Decorative marquee band. The same words are on the page already, so the track is hidden
    from screen readers. Four identical groups let the CSS loop scroll by exactly one group (-25%).
    js/main.js adds the pause button outside the hidden track."""
    group = "".join(f"<li>{esc(x)}</li>" for x in items)
    cls = "ticker" + (f" {extra_cls}" if extra_cls else "")
    return (f'<div class="{cls}"><div class="ticker-track" aria-hidden="true">'
            f'<ul>{group}</ul>' + f'<ul class="ticker-dup">{group}</ul>' * 3 + '</div></div>')


def kickoff_html(lang, start, with_time=True):
    """Scoreboard date block: day / date (+ year) / kick-off time. Reads as one date for screen readers."""
    t = I18N[lang]
    d = start.astimezone(TZ)
    wd = t["dayShort"][(d.weekday() + 1) % 7]
    if lang == "de":
        day, date, year = f"{wd}.", f"{d.day:02d}.{d.month:02d}.", f"{d.year}"
    else:
        day, date, year = wd, f"{d.day} {t['months'][d.month - 1]}", f" {d.year}"
    when = (f' <span class="ko-time">{d:%H:%M}<span class="ko-suffix">{esc(t["timeSuffix"])}</span></span>'
            if with_time else "")
    iso = start.isoformat() if with_time else d.date().isoformat()
    return (f'<time class="kickoff" datetime="{attr(iso)}"><span class="ko-day">{esc(day)}</span> '
            f'<span class="ko-date">{esc(date)}<span class="ko-year">{esc(year)}</span></span>{when}</time>')


def kickoff_tbd(lang, with_time=True):
    """Scoreboard block for a date that is not known yet."""
    t = I18N[lang]
    clock = '<span class="ko-time" aria-hidden="true">--:--</span>' if with_time else ""
    return (f'<p class="kickoff kickoff-tbd"><span class="ko-day" aria-hidden="true">–</span> '
            f'<span class="ko-date">{esc(t["efDateTbd"])}</span>{clock}</p>')


# Decorative nav icons (24x24, drawn in currentColor; the text label is always next to them).
# "eintracht" is the site's own generic wing motif (three slanted feather bars), not a club crest.
NAV_ICONS = {
    "home": '<path d="M3 11.5 12 4l9 7.5M5.5 9.5V20h5v-6h3v6h5V9.5"/>',
    "schedule": '<path d="M3.5 6h17v14.5h-17zM3.5 10.5h17M8 3v5M16 3v5"/><path class="nif" d="M12.5 13.5H17V18h-4.5z"/>',
    "eintracht": ('<path class="nif" d="M4 2.5h19l-3 5H1z"/><path class="nif" d="M8 9.5h13.5l-3 5H5z"/>'
                  '<path class="nif" d="M12 16.5h8l-3 5H9z"/>'),
}
# "Opens another page" cue (arrow out of the corner), shown after every standalone page link
GO_ICON = ('<svg class="nav-go" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
           '<path d="M6 18 17.5 6.5M8.5 6H18v9.5"/></svg>')
NAV_PAGE_KEYS = {"home": "navHome", "schedule": "navSchedule", "eintracht": "navEintracht"}
NAV_SECTION_KEYS = {"about": "navAbout", "sport": "navSport", "drinks": "navDrinks", "events": "navEvents",
                    "gallery": "navGallery", "visit": "navVisit", "contact": "navContact"}


def nav_icon(key):
    return f'<svg class="nav-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{NAV_ICONS[key]}</svg>'


def home_sections(lang):
    """Ids of the home page's .section blocks in page order (CSS numbers them 01, 02, … in this order)."""
    ids = ["about", "sport", "drinks", "events", "gallery", "visit", "local"]
    if faq_items(lang):
        ids.append("faq")
    if contact_cards(lang):
        ids.append("contact")
    return ids


def site_nav(lang, pages, sections, home="", current=None):
    """Main nav in two labelled groups, the same structure on every page:
    1. standalone pages (icon + label + 'opens a page' arrow, drawn as plates),
    2. section jumps on the home page (numbered like the section headings, so '03' = section 03).
    home: relative link to this language's home page ('' on the home page itself)."""
    t = I18N[lang]
    num = {sid: n for n, sid in enumerate(home_sections(lang), 1)}
    ind = "\n                        "

    def page_href(k):
        return (home or "./") if k == "home" else home + PAGES[k][lang]

    cur = ' aria-current="page"'
    page_items = ind.join(
        f'<li><a class="nav-page" href="{attr(page_href(k))}"{cur if k == current else ""}>'
        f'{nav_icon(k)}<span class="nav-label">{esc(t[NAV_PAGE_KEYS[k]])}</span>{GO_ICON}</a></li>'
        for k in pages)
    section_items = ind.join(
        f'<li><a href="{attr(home)}#{sid}" data-n="{num.get(sid, 0):02d}">{esc(t[NAV_SECTION_KEYS[sid]])}</a></li>'
        for sid in sections)
    here = t["navOnPage"] if not home else t["navOnHome"]
    # The visible group headings are aria-hidden: each group is already named by them via aria-labelledby.
    return f'''<nav id="nav" class="nav" aria-label="{attr(t["navLabel"])}">
                <div class="nav-group nav-pages" role="group" aria-labelledby="nav-pages-h">
                    <p class="nav-heading" id="nav-pages-h" aria-hidden="true">{esc(t["navPages"])}</p>
                    <ul>
                        {page_items}
                    </ul>
                </div>
                <div class="nav-group nav-sections" role="group" aria-labelledby="nav-sections-h">
                    <p class="nav-heading" id="nav-sections-h" aria-hidden="true">{esc(here)}</p>
                    <ul>
                        {section_items}
                    </ul>
                </div>
            </nav>'''


def menu_button(t):
    return (f'<button class="menu-btn" id="menuBtn" type="button" aria-expanded="false" aria-controls="nav" aria-label="{attr(t["menuOpen"])}">\n'
            '                    <span></span><span></span><span></span>\n'
            '                </button>')


def subpage_header(lang, path, current, other_href):
    """Header for every page except home: logo -> home, a nav with a clear Home item, theme, language, menu."""
    t = I18N[lang]
    home = home_href(path)
    nav = site_nav(lang, ["home", "schedule", "eintracht"], ["events", "visit"], home=home, current=current)
    return f'''    <header class="site-header">
        <div class="container header-inner">
            <a class="brand" href="{home}" aria-label="{attr(t["brandHome"].format(name=SITE["name"]))}">{logo_svg()}<span class="brand-title">C'est la <span>vie</span></span></a>
            {nav}
            <div class="header-actions">
                <button class="theme-btn" id="themeBtn" type="button" aria-label="{attr(t["themeBtn"])}"></button>
                {lang_switch(lang, other_href)}
                {menu_button(t)}
            </div>
        </div>
    </header>'''


def back_link(lang, path, end=False):
    """'Back to home' link, shown at the top and the bottom of every sub page."""
    t = I18N[lang]
    cls = "back-row back-row-end" if end else "back-row"
    return (f'<p class="{cls}"><a class="back-link" href="{home_href(path)}">'
            f'<span class="back-arrow" aria-hidden="true">←</span>{esc(t["backHome"])}</a></p>')


def site_footer(lang, home=""):
    t = I18N[lang]
    return f'''    <footer class="site-footer">
        <div class="container footer-inner">
            <p>© <span id="year">2026</span> {esc(SITE["name"])} · {esc(SITE["area_label"])}</p>
            <p><a href="{home}impressum.html">{esc(t["imprint"])}</a> · <a href="{home}datenschutz.html">{esc(t["privacy"])}</a></p>
        </div>
    </footer>'''


def drinks_html(lang):
    cats = DRINKS.get("categories", [])
    cur = DRINKS.get("currency", "€")

    def price(n):
        s = f"{n:.2f}"
        if lang == "de":
            s = s.replace(".", ",")
        return f"{s} {cur}"

    tabs, panels = [], []
    for i, c in enumerate(cats):
        cid = c["id"]
        tabs.append(
            f'<button class="drink-tab" type="button" role="tab" id="tab-{cid}" aria-selected="{"true" if i == 0 else "false"}" '
            f'aria-controls="panel-{cid}" tabindex="{0 if i == 0 else -1}">{esc(loc(c["name"], lang))}</button>')
        items = []
        for j, it in enumerate(c.get("items", [])):
            size = f'<span class="drink-size">{esc(it["size"])}</span>' if it.get("size") else ""
            extra = loc(it.get("ingredients"), lang) or loc(it.get("description"), lang)
            desc = f'<p class="drink-desc">{esc(extra)}</p>' if extra else ""
            items.append(
                f'<div class="drink-item" style="--i:{j}"><div class="drink-head">'
                f'<span class="drink-name">{esc(loc(it["name"], lang))}{size}</span><span class="drink-dots"></span>'
                f'<span class="drink-price">{price(it["price"])}</span></div>{desc}</div>')
        panels.append(
            f'<div class="drink-panel" id="panel-{cid}" aria-labelledby="tab-{cid}" tabindex="0">'
            f'<h3 class="drink-cat-title">{esc(loc(c["name"], lang))}</h3>' + "".join(items) + "</div>")
    return ('<div class="drink-tabs" role="tablist" id="drinkTabs" hidden>' + "".join(tabs) + "</div>\n                    "
            + "\n                    ".join(panels))


# Decorative tile icons (currentColor, aria-hidden; the heading next to them carries the meaning)
BEER_ICON = ('<svg class="perk-icon" viewBox="0 0 48 48" aria-hidden="true" focusable="false">'
             '<path d="M9 13h22v29H9z"/><path d="M31 18h5.5v15H31"/><path d="M15 20v15M21 20v15M27 20v15"/>'
             '<path class="nif" d="M7 6h26l-2 7H9z"/></svg>')
MUSIC_ICON = ('<svg class="perk-icon" viewBox="0 0 48 48" aria-hidden="true" focusable="false">'
              '<path d="M17 36V9l22-5v27"/><path class="nif" d="M5 37a6 5 0 1 0 12 0a6 5 0 1 0-12 0zM27 32a6 5 0 1 0 12 0a6 5 0 1 0-12 0z"/>'
              '<path class="nif" d="M17 9l22-5v6l-22 5z"/></svg>')


def perks_html(lang):
    """Feature strip at the top of the drinks section: beer types (only real ones from drinks.json,
    linked to the menu below) and 'you pick the music' (no mechanism named until the owner says how)."""
    t = I18N[lang]
    tiles = []
    if show_beers():
        groups = beer_groups(lang)
        chip_groups = "".join(
            f'<div class="chip-group{" chip-group-main" if i == 0 else ""}">'
            f'<p class="chip-label" id="beer-{cid}">{esc(label)}</p>'
            f'<ul class="chips" aria-labelledby="beer-{cid}">' + "".join(f"<li>{esc(n)}</li>" for n, _ in names) + "</ul></div>"
            for i, (cid, label, names) in enumerate(groups))
        tiles.append(
            f'<li class="card perk perk-beer reveal">{BEER_ICON}<h3>{esc(t["beerTitle"])}</h3>'
            f'<p>{esc(t["beerText"])}</p>{chip_groups}'
            f'<p class="more-link"><a href="#drinks-menu" data-drink-tab="{attr(groups[0][0])}">{esc(t["beerLink"])}'
            f'<span aria-hidden="true">&nbsp;→</span></a></p></li>')
    if show_music():
        how = music_how(lang)
        how_html = f'<p>{esc(t["musicHow"].format(how=how))}</p>' if how else ""
        eq = '<span class="eq" aria-hidden="true">' + "<span></span>" * 5 + "</span>"
        tiles.append(
            f'<li class="card perk perk-music reveal">{MUSIC_ICON}<h3>{esc(t["musicTitle"])}</h3>'
            f'<p class="perk-claim">{esc(t["musicText"])}</p>{how_html}{eq}</li>')
    if not tiles:
        return ""
    return f'<ul class="perks" aria-label="{attr(t["perksLabel"])}">' + "".join(tiles) + "</ul>"


def hours_html(lang):
    days = SITE["hours"]["days"]
    names = I18N[lang]["days"]  # index 0 = Sunday
    en_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    rows = []
    for d in [1, 2, 3, 4, 5, 6, 0]:
        e = days.get(en_names[d])
        if not e:
            continue
        o, c = e["open"], e["close"]
        rows.append(f'<tr data-d="{d}"><th scope="row">{esc(names[d])}</th><td>{o} – {c}</td></tr>')
    return "\n                            ".join(rows)


def events_html(lang):
    out = []
    for ev in SITE["events"]["items"]:
        tag, title, short = loc(ev["tag"], lang), loc(ev["title"], lang), loc(ev["short"], lang)
        more = loc(ev.get("more"), lang) if ev.get("more") else ""
        head = f'<span class="tag">{esc(tag)}</span><h3>{esc(title)}</h3><p>{esc(short)}</p>'
        if more and not missing(more):
            out.append(f'<details class="card event reveal"><summary>{head}</summary>'
                       f'<div class="event-more"><p>{esc(more)}</p></div></details>')
        else:
            out.append(f'<article class="card event event-plain reveal"><div class="event-plain-body">{head}</div></article>')
    return "\n                    ".join(out)


def contact_cards(lang):
    t = I18N[lang]
    cards = []
    phone = get("contact.phone")
    if phone:
        cards.append(f'<a class="card contact-card reveal" href="tel:+{digits(phone)}"><h3>{esc(t["phone"])}</h3><p>{esc(phone)}</p></a>')
    wa = get("contact.whatsapp")
    if wa:
        cards.append(f'<a class="card contact-card reveal" href="https://wa.me/{digits(wa)}" target="_blank" rel="noopener"><h3>{t["whatsapp"]}</h3><p>{esc(t["waText"])}</p></a>')
    mail = get("contact.email")
    if mail:
        cards.append(f'<a class="card contact-card reveal" href="mailto:{attr(mail)}"><h3>{esc(t["email"])}</h3><p>{esc(mail)}</p></a>')
    for key, label in (("instagram", "Instagram"), ("facebook", "Facebook"), ("tiktok", "TikTok")):
        url = get(f"social.{key}.url")
        if url:
            handle = get(f"social.{key}.handle", SITE["name"])
            cards.append(f'<a class="card contact-card reveal" href="{attr(url)}" target="_blank" rel="noopener"><h3>{label}</h3><p>{esc(handle)}</p></a>')
    return "\n                    ".join(cards)


def address_html():
    street = get("address.street")
    if street:
        line2 = f'{esc(get("address.postal_code", ""))} {esc(get("address.locality", ""))}'.strip()
        body = f'<strong>{esc(SITE["name"])}</strong><br>\n                            {esc(street)}<br>\n                            {line2}'
    else:
        body = f'<strong>{esc(SITE["name"])}</strong><br>\n                            {esc(SITE["area_label"])}'
    return f"<address>\n                            {body}\n                        </address>"


def ui_data(lang):
    t = I18N[lang]
    keys = ["themeLight", "themeDark", "menuOpen", "menuClose", "open", "closed", "until", "lbClose", "lbPrev", "lbNext", "mapTitle", "tickerPause", "tickerPlay"]
    lat, lng = get("geo.lat", report=False), get("geo.lng", report=False)
    try:
        lat, lng = float(lat), float(lng)
        map_url = (f"https://www.openstreetmap.org/export/embed.html?bbox={lng-0.022}%2C{lat-0.0115}%2C{lng+0.022}%2C{lat+0.0115}"
                   f"&layer=mapnik&marker={lat}%2C{lng}")
    except (TypeError, ValueError):
        # no confirmed coordinates: show the Niederrad area without a marker
        map_url = "https://www.openstreetmap.org/export/embed.html?bbox=8.6150%2C50.0720%2C8.6600%2C50.0950&layer=mapnik"
    data = {"strings": {k: t[k] for k in keys}, "hours": hours_numeric(), "mapUrl": map_url}
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


# ---------------------------------------------------------------- pages
def render_home(lang, other_href=None):
    t = I18N[lang]
    r = rel_root(lang)
    phone = get("contact.phone", report=False)
    route = route_url()
    mobile_cls = "mobile-bar" + ("" if phone else " single")
    call = f'<a href="tel:+{digits(phone)}">{esc(t["call"])}</a>' if phone else ""
    gallery = "\n                    ".join(
        f'<button type="button" class="gallery-item" aria-label="{attr(t["zoom"])}"><img src="{r}assets/img/gallery-{n}.svg" width="800" height="800" loading="lazy" decoding="async" alt="{img_alt(t["galleryItemAlt"].format(n=n))}"></button>'
        for n in range(1, 7))
    contact = contact_cards(lang)
    contact_section = f'''
        <section class="section" id="contact">
            <div class="container">
                <h2>{esc(t["contactTitle"])}</h2>
                <div class="grid grid-3">
                    {contact}
                </div>
            </div>
        </section>
''' if contact else ""
    nav = site_nav(lang, ["schedule", "eintracht"],
                   ["about", "sport", "drinks", "events", "gallery", "visit"] + (["contact"] if contact else []),
                   current="home")
    has_hours = bool(SITE["hours"]["days"])
    status = '<p class="status" id="status" data-status aria-live="polite"></p>\n                        ' if has_hours else ""
    hero_chip = '<p class="status hero-status" data-status></p>\n                ' if has_hours else ""
    ticker_items = [p.strip() for p in t["tagline"].split("·") if p.strip()] + ["Bundesliga", "Eintracht Frankfurt", "Champions League"]
    # Decorative: the same words are in the hero and the sport section
    ticker = ticker_html(ticker_items)
    head = head_common(lang, 0, jsonld_scripts(lang))
    facts = venue_facts(lang)
    facts_html = ('<ul class="facts">' + "".join(f"<li>{esc(f)}</li>" for f in facts) + "</ul>") if facts else ""
    n_screens = get("venue.screens", report=False)
    sport5 = t["sport5Screens"].format(n=n_screens) if n_screens else t["sport5"]
    faq = faq_section(lang)
    sched_href = PAGES["schedule"][lang]
    local = local_section(lang)
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(t["title"])}</title>
{meta_block(lang, "", t["title"], home_description(lang))}
{head}</head>
<body>
    <a class="skip-link" href="#main">{esc(t["skip"])}</a>

    <header class="site-header">
        <div class="container header-inner">
            <a class="brand" href="#top" aria-label="{attr(SITE["name"])}">{logo_svg()}<span class="brand-title">C'est la <span>vie</span></span></a>
            {nav}
            <div class="header-actions">
                <button class="theme-btn" id="themeBtn" type="button" aria-label="{attr(t["themeBtn"])}"></button>
                {lang_switch(lang, other_href)}
                {menu_button(t)}
            </div>
        </div>
    </header>

    <main id="main">
        <section class="hero" id="top">
            <img class="hero-img" src="{r}assets/img/hero.svg" width="1200" height="1600" fetchpriority="high" alt="{img_alt(t["heroAlt"])}">
            <div class="hero-overlay"></div>
            <div class="hero-slab" aria-hidden="true"></div>
            {wing_svg("wing hero-wing")}
            <div class="container hero-content">
                {hero_chip}<p class="eyebrow">Frankfurt · Niederrad</p>
                <h1><span class="h1-line">C'est la vie</span> <span class="h1-line h1-flag">Sports Bar</span></h1>
                <p class="tagline">{esc(t["tagline"])}</p>
                <div class="hero-buttons">
                    <a class="btn btn-primary" href="{sched_href}">{esc(t["btnLive"])}</a>
                    <a class="btn btn-ghost" href="#visit">{esc(t["btnRoute"])}</a>
                </div>
            </div>
        </section>
        {ticker}

        <section class="section" id="about">
            <div class="container split">
                <div class="reveal">
                    <h2>{esc(t["aboutTitle"])}</h2>
                    <p>{esc(t["aboutP1"])}</p>
                    <p>{esc(t["aboutP2"])}</p>
                </div>
                <img class="reveal media" src="{r}assets/img/about.svg" width="1200" height="900" loading="lazy" decoding="async" alt="{img_alt(t["aboutAlt"])}">
            </div>
        </section>

        <section class="section section-alt" id="sport">
            <div class="container">
                <h2>{esc(t["sportTitle"])}</h2>
                <p class="lead">{esc(t["sportLead"])}</p>
                {facts_html}
                <div class="bento">
                    <article class="card bento-card bento-a reveal"><span class="bento-n" aria-hidden="true">01</span><h3>Bundesliga</h3><p>{esc(t["sport1"])}</p></article>
                    <article class="card bento-card bento-b reveal"><span class="bento-n" aria-hidden="true">02</span><h3>Eintracht Frankfurt</h3><p>{esc(t["sport2"])}</p></article>
                    <article class="card bento-card bento-c reveal"><span class="bento-n" aria-hidden="true">03</span><h3>Champions League</h3><p>{esc(t["sport3"])}</p></article>
                    <article class="card bento-card bento-d reveal"><span class="bento-n" aria-hidden="true">04</span><h3>{esc(t["sport4Title"])}</h3><p>{esc(t["sport4"])}</p></article>
                    <article class="card bento-card bento-e reveal"><span class="bento-n" aria-hidden="true">05</span><h3>{esc(t["sport5Title"])}</h3><p>{esc(sport5)}</p></article>
                </div>
            </div>
        </section>

        <section class="section" id="drinks">
            <div class="container">
                <h2>{esc(t["drinksTitle"])}</h2>
                {perks_html(lang)}
                <p class="lead">{esc(t["drinksLead"])}</p>
                <div class="drinks" id="drinks-menu">
                    {drinks_html(lang)}
                </div>
            </div>
        </section>

        <section class="section section-alt" id="events">
            <div class="container">
                <h2>{esc(t["eventsTitle"])}</h2>
                <div class="grid grid-3">
                    {events_html(lang)}
                </div>
            </div>
        </section>

        <section class="section" id="gallery">
            <div class="container">
                <h2>{esc(t["galleryTitle"])}</h2>
                <div class="gallery" id="gallery-grid">
                    {gallery}
                </div>
            </div>
        </section>

        <section class="section section-alt" id="visit">
            <div class="container">
                <h2>{esc(t["visitTitle"])}</h2>
                <div class="split">
                    <div>
                        {status}<table class="hours"><tbody id="hours">
                            {hours_html(lang)}
                        </tbody></table>
                        {address_html()}
                        <a class="btn btn-primary" href="{attr(route)}" target="_blank" rel="noopener">{esc(t["btnRoute2"])}</a>
                    </div>
                    <div class="map" id="map">
                        <p>{esc(t["mapText"])}</p>
                        <button type="button" class="btn btn-ghost" id="mapBtn">{esc(t["mapBtn"])}</button>
                    </div>
                </div>
            </div>
        </section>
{local}{faq}{contact_section}    </main>

{site_footer(lang)}

    <div class="{mobile_cls}" aria-label="{attr(t["quick"])}">
        {call}
        <a href="{attr(route)}" target="_blank" rel="noopener">{esc(t["route"])}</a>
    </div>

    <dialog class="lightbox" id="lightbox" aria-label="{attr(t["lbLabel"])}">
        <button type="button" class="lb-close" id="lbClose" aria-label="{attr(t["lbClose"])}">×</button>
        <button type="button" class="lb-nav lb-prev" id="lbPrev" aria-label="{attr(t["lbPrev"])}">‹</button>
        <img id="lbImg" src="" alt="">
        <button type="button" class="lb-nav lb-next" id="lbNext" aria-label="{attr(t["lbNext"])}">›</button>
    </dialog>

    <script type="application/json" id="ui-data">{ui_data(lang)}</script>
    <script src="{r}js/main.js"></script>
</body>
</html>
'''


def legal_lines(lang):
    """(imprint_html, privacy_html) body sections built only from confirmed data."""
    t = I18N[lang]
    owner = get("legal.owner_name")
    name_addr = ", ".join(p for p in [SITE["name"], owner, get("address.street"),
                                      f'{get("address.postal_code", "")} {get("address.locality", "")}'.strip()] if p)
    phone, mail = get("contact.phone"), get("contact.email")
    reg, vat = get("legal.trade_register"), get("legal.vat_id")
    imp = [f'<h2>{esc(t["l1h"])}</h2>\n        <p>{esc(name_addr)}</p>']
    contact = [f'{t["l2phone"]}: {phone}' if phone else "", f'{t["l2mail"]}: {mail}' if mail else ""]
    contact = [c for c in contact if c]
    if contact:
        imp.append(f'<h2>{esc(t["l2h"])}</h2>\n        <p>{esc(" · ".join(contact))}</p>')
    regs = [f'{t["l3reg"]}: {reg}' if reg else "", f'{t["l3vat"]}: {vat}' if vat else ""]
    regs = [x for x in regs if x]
    if regs:
        imp.append(f'<h2>{esc(t["l3h"])}</h2>\n        <p>{esc(" · ".join(regs))}</p>')
    provider = get("legal.hosting_provider")
    p2 = t["p2p"] + (f' {t["p2provider"]} {provider}' if provider else "")
    controller = ", ".join(x for x in [name_addr, mail] if x)
    priv = [
        (t["p1h"], controller), (t["p2h"], p2), (t["p3h"], t["p3p"]),
        (t["p4h"], t["p4p"]), (t["p5h"], t["p5p"]),
    ]
    return "\n        ".join(imp), "\n        ".join(f"<h2>{esc(h)}</h2>\n        <p>{esc(p)}</p>" for h, p in priv)


def render_legal(lang, kind, other_href=None):
    t = I18N[lang]
    r = rel_root(lang)
    imp, priv = legal_lines(lang)
    title = t["legalTitle"] if kind == "impressum" else t["pTitle"]
    body = imp if kind == "impressum" else priv
    path = kind + ".html"
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)} – {esc(SITE["name"])}</title>
{meta_block(lang, kind + ".html", title + " – " + SITE["name"], t["legalDescription"] if kind == "impressum" else t["privacyDescription"], social=False)}
    <meta name="robots" content="noindex">
{head_common(lang, 0)}</head>
<body>
    <a class="skip-link" href="#main">{esc(t["skip"])}</a>
{subpage_header(lang, path, kind, other_href)}
    <main class="container legal" id="main">
        {back_link(lang, path)}
        <h1>{esc(title)}</h1>
        {body}
        {back_link(lang, path, end=True)}
    </main>
{site_footer(lang, home_href(path))}
    <script type="application/json" id="ui-data">{ui_data(lang)}</script>
    <script src="{r}js/main.js"></script>
</body>
</html>
'''


# ---------------------------------------------------------------- schedule + local angle
def upcoming_matches():
    """Matches that have not finished yet (start + 3 h > build time), sorted by start."""
    out = []
    for m in SCHEDULE.get("matches", []):
        start = datetime.fromisoformat(m["start"])
        if start + timedelta(hours=3) > NOW:
            out.append((start, m))
    return sorted(out, key=lambda x: x[0])


def fmt_match_time(lang, start):
    t = I18N[lang]
    d = start.astimezone(TZ)
    wd = t["dayShort"][(d.weekday() + 1) % 7]  # dayShort index 0 = Sunday
    if lang == "de":
        day = f"{wd}., {d.day:02d}.{d.month:02d}.{d.year}"
    else:
        day = f"{wd} {d.day} {t['months'][d.month - 1]} {d.year}"
    return f"{day}, {d:%H:%M}{t['timeSuffix']}"


def sports_event_schema(lang, start, m):
    teams = f'{m["home"]} – {m["away"]}'
    name = f'{teams} ({m["competition"]})' if m.get("competition") else teams
    d = {
        "@context": "https://schema.org",
        "@type": "SportsEvent",
        "@id": f'{page_url(lang, PAGES["schedule"][lang])}#{m["id"]}',
        "name": name,
        "startDate": start.isoformat(),
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "homeTeam": {"@type": "SportsTeam", "name": m["home"]},
        "awayTeam": {"@type": "SportsTeam", "name": m["away"]},
        "url": page_url(lang, PAGES["schedule"][lang]),
        "location": {"@id": BAR_ID},
    }
    return d


def local_paragraphs(lang):
    """Local-angle sentences, only from confirmed facts in site.json. The stadium walk is shown in the
    nearby list when the stadium is in it, so it is only repeated here as a fallback."""
    t = I18N[lang]
    L = SITE["local"]
    parts = [t["localLead"]]
    walk = loc(get("local.walk_from_stadium"), lang)
    if walk and not missing(walk) and not nearby_place(L["stadium_name"]):
        parts.append(t["localStadium"].format(stadium=L["stadium_name"], walk=walk))
    if L.get("nearby_confirmed") is True and L.get("nearby"):
        parts.append(t["localNearby"].format(places=join_list(lang, L["nearby"])))
    elif "local.nearby_confirmed" not in TODOS:
        TODOS.append("local.nearby_confirmed (set true once the bar is confirmed to be near DFB-Campus / Bürostadt)")
    pt = loc(get("local.public_transport"), lang)
    if pt and not missing(pt):
        parts.append(t["localPt"].format(pt=pt))
    return parts


# Pin icon for the "Nearby" heading (decorative, currentColor)
PIN_ICON = ('<svg class="near-pin" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            '<path d="M12 22s7-7.2 7-12.5A7 7 0 0 0 5 9.5C5 14.8 12 22 12 22z"/><path class="nif" d="M9.5 7.5h5l-1 4h-5z"/></svg>')


def near_item(lang, p, home="", link_eintracht=True, hl=4):
    """One nearby place as a ticket: name, kind, a sentence for people, and a scoreboard distance chip.
    hl: heading level of the place name (4 under the 'Nearby' h3, 3 directly under a page h2)."""
    t = I18N[lang]
    km = p["distance_km"]
    key = NEAR_COPY.get(p["name"])
    text = ""
    if key == "Stadium":
        walk = loc(get("local.walk_from_stadium", report=False), lang)
        if walk and not missing(walk):
            text = t["nearStadium"].format(walk=walk)
    elif key:
        text = t[f"near{key}"]
    kind = loc(p.get("kind"), lang)
    link = ""
    if key == "Stadium" and link_eintracht:
        link = (f'<p class="near-link"><a href="{attr(home + PAGES["eintracht"][lang])}">{esc(t["nearLinkEintracht"])}'
                f'<span aria-hidden="true">&nbsp;→</span></a></p>')
    return (f'<li class="near"><div class="near-body"><h{hl} class="near-name">{esc(p["name"])}</h{hl}>'
            + (f'<p class="near-kind">{esc(kind)}</p>' if kind else "")
            + (f'<p class="near-text">{esc(text)}</p>' if text else "") + link
            + f'</div><p class="near-dist"><span class="near-ca">{esc(t["nearAbout"])}</span> '
            f'<span class="near-km">{fmt_km(lang, km)}<span class="near-unit"> km</span></span> '
            f'<span class="near-line">{esc(t["nearLine"])}</span></p></li>')


def nearby_html(lang, home="", uid="near"):
    """'Nearby' block: heading, intro, ticket list (nearest first), distance note. '' without confirmed places."""
    t = I18N[lang]
    places = nearby_places()
    if not places:
        return ""
    items = "".join(near_item(lang, p, home) for p in places)
    return (f'<div class="nearby" role="group" aria-labelledby="{uid}-h">'
            f'<h3 class="nearby-title" id="{uid}-h">{PIN_ICON}{esc(t["nearTitle"])}</h3>'
            f'<p class="near-intro">{esc(t["nearIntro"])}</p>'
            f'<ul class="near-list">{items}</ul>'
            f'<p class="near-note">{esc(t["nearNote"])}</p></div>')


def link_list(lang, home, keys):
    """Internal follow-up links (other pages, home sections), drawn as underlined plate links."""
    t = I18N[lang]
    target = {
        "schedule": (home + PAGES["schedule"][lang], "localLinkSchedule"),
        "eintracht": (home + PAGES["eintracht"][lang], "localLinkEintracht"),
        "drinks": (home + "#drinks", "localLinkDrinks"),
        "visit": (home + "#visit", "localLinkVisit"),
        "local": (home + "#local", "localLinkArea"),
    }
    lis = "".join(f'<li class="more-link"><a href="{attr(target[k][0])}">{esc(t[target[k][1]])}'
                  f'<span aria-hidden="true">&nbsp;→</span></a></li>' for k in keys)
    return f'<ul class="link-list">{lis}</ul>'


def local_block(lang, home="", links=("visit", "schedule", "eintracht")):
    """Body of 'Directions & area' (home page and schedule page): text column + nearby list."""
    paras = "".join(f"<p>{esc(x)}</p>" for x in local_paragraphs(lang))
    near = nearby_html(lang, home)
    return (f'<div class="local-grid"><div class="local">{paras}{link_list(lang, home, links)}</div>'
            f'{near}</div>')


def local_section(lang):
    t = I18N[lang]
    return f'''
        <section class="section" id="local">
            <div class="container">
                <h2>{esc(t["localTitle"])}</h2>
                {local_block(lang)}
            </div>
        </section>
'''


def match_title(home, away, score=None):
    """'Home – Away' (or 'Home 2:1 Away') as three parts the CSS can lay out like a scoreboard."""
    mid = f'<span class="score">{score}</span>' if score is not None else '<span class="vs">–</span>'
    return (f'<h3 class="match-title"><span class="team team-home">{esc(home)}</span> {mid} '
            f'<span class="team team-away">{esc(away)}</span></h3>')


def page_head(lang, path, h1, intro, kicker, extra="", art=False, cls=""):
    """Dark matchday band at the top of the schedule and Eintracht pages."""
    parts = h1.split(" ", 1)
    title = (f'<span class="h1-line">{esc(parts[0])}</span> <span class="h1-line h1-flag">{esc(parts[1])}</span>'
             if len(parts) == 2 else esc(h1))
    wing = wing_svg("wing page-wing") if art else ""
    return f'''        <section class="page-head{" " + cls if cls else ""}" aria-labelledby="page-h1">
            <div class="page-head-stripes" aria-hidden="true"></div>
            {wing}
            <div class="container page-head-inner">
                {back_link(lang, path)}
                <p class="kicker">{esc(kicker)}</p>
                <h1 id="page-h1">{title}</h1>
                <p class="lead">{esc(intro)}</p>
                {extra}
            </div>
        </section>'''


def render_schedule(lang, other_href):
    t = I18N[lang]
    path = PAGES["schedule"][lang]
    r = "../" * (path.count("/") + (0 if lang == DEFAULT_LANG else 1))
    matches = upcoming_matches()
    items, blocks, any_example = [], [bar_schema(lang)], False
    for start, m in matches:
        ex = bool(m.get("example"))
        any_example |= ex
        badge = f'<span class="tag">{esc(t["exampleBadge"])}</span>' if ex else ""
        comp = f'<span class="match-comp">{esc(m["competition"])}</span>' if m.get("competition") else ""
        note = loc(m.get("note"), lang)
        note_html = f'<p class="match-note">{esc(note)}</p>' if note else ""
        meta = f'<p class="match-meta">{comp}{badge}</p>' if comp or badge else ""
        items.append(
            f'<li class="match" id="{attr(m["id"])}">{kickoff_html(lang, start)}<div class="match-body">'
            f'{match_title(m["home"], m["away"])}{meta}{note_html}</div></li>')
        if not ex:
            blocks.append(sports_event_schema(lang, start, m))
    body = ('<ul class="match-list">' + "".join(items) + "</ul>") if items else f'<p>{esc(t["schedEmpty"])}</p>'
    example_note = f'<p class="match-note">{esc(t["exampleNote"])}</p>' if any_example else ""
    local = local_block(lang, home_href(path), links=("eintracht", "drinks", "visit"))
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(t["schedTitle"])}</title>
{meta_block(lang, path, t["schedTitle"], t["schedDesc"])}
{head_common(lang, path.count("/"), jsonld_scripts(lang, blocks))}</head>
<body>
    <a class="skip-link" href="#main">{esc(t["skip"])}</a>
{subpage_header(lang, path, "schedule", other_href)}
    <main id="main">
{page_head(lang, path, t["schedH1"], t["schedIntro"], t["schedKicker"])}
        <div class="container page-body schedule">
            {body}
            {example_note}
            <section class="page-sec" aria-labelledby="sched-local">
                <h2 class="sec-head" id="sched-local">{esc(t["localTitle"])}</h2>
                {local}
            </section>
            {back_link(lang, path, end=True)}
        </div>
    </main>
{site_footer(lang, home_href(path))}
    <script type="application/json" id="ui-data">{ui_data(lang)}</script>
    <script src="{r}js/main.js"></script>
</body>
</html>
'''


# ---------------------------------------------------------------- Eintracht Frankfurt page
EINTRACHT = "Eintracht Frankfurt"  # team name exactly as written in data/schedule.json

# TODO(owner): PLACEHOLDER data. There is no data source yet for Eintracht results or the league table,
# and data/schedule.json has no Eintracht match yet. Until real data is entered here, the page shows each
# entry below in a visible "to be filled in" state. Never put invented results or standings here.
#
# Upcoming fixtures: add them to data/schedule.json with "Eintracht Frankfurt" as "home" or "away".
#   They then appear on /spielplan/ AND here, and the "fixtures" list below is ignored.
#   (Entries in "fixtures" below use: {"start": "2027-02-06T15:30:00+01:00", "opponent": "…",
#    "competition": "Bundesliga", "home": true}; finished matches are hidden 3 h after kick-off.)
# Past results, newest first:
#   {"date": "2026-11-01", "opponent": "…", "competition": "Bundesliga", "home": true,
#    "goals_for": 2, "goals_against": 1}
# Table standing (one entry):
#   {"competition": "Bundesliga", "season": "2026/27", "position": 4, "played": 10,
#    "points": 19, "goal_diff": 6, "as_of": "2026-11-08"}
# Replace a {"placeholder": True} entry with a real one; an empty list hides the rows of that section.
EINTRACHT_DATA = {
    "fixtures": [{"placeholder": True}, {"placeholder": True}, {"placeholder": True}],
    "results": [{"placeholder": True}, {"placeholder": True}, {"placeholder": True}],
    "standing": {"placeholder": True},
}


def fmt_date(lang, d):
    """Date without time, e.g. 'Sa., 01.11.2026' / 'Sat 1 Nov 2026'."""
    t = I18N[lang]
    wd = t["dayShort"][(d.weekday() + 1) % 7]
    if lang == "de":
        return f"{wd}., {d.day:02d}.{d.month:02d}.{d.year}"
    return f"{wd} {d.day} {t['months'][d.month - 1]} {d.year}"


def tbd_html(lang):
    """A visible dash for a value that is not filled in yet; screen readers hear 'to be filled in'."""
    return f'<span aria-hidden="true">–</span><span class="sr-only">{esc(I18N[lang]["efTbd"])}</span>'


def pending_note(lang, text_key):
    t = I18N[lang]
    return f'<p class="pending-note"><span class="tag tag-pending">{esc(t["efPending"])}</span>{esc(t[text_key])}</p>'


def teams(e, opponent):
    """(home team, away team) for an Eintracht match."""
    return (EINTRACHT, opponent) if e.get("home", True) else (opponent, EINTRACHT)


def eintracht_fixtures():
    """[(start | None, entry)]: upcoming Eintracht matches from schedule.json, else the EINTRACHT_DATA list."""
    out = []
    for start, m in upcoming_matches():
        if EINTRACHT in (m.get("home"), m.get("away")):
            home = m["home"] == EINTRACHT
            out.append((start, {"opponent": m["away"] if home else m["home"], "home": home,
                                "competition": m.get("competition"), "example": bool(m.get("example")), "id": m["id"]}))
    if out:
        return out
    for e in EINTRACHT_DATA["fixtures"]:
        if e.get("placeholder"):
            out.append((None, e))
            continue
        start = datetime.fromisoformat(e["start"])
        if start + timedelta(hours=3) > NOW:
            out.append((start, e))
    return out


def venue_tag(lang, e):
    t = I18N[lang]
    return f'<span class="match-venue">{esc(t["efHome"] if e.get("home", True) else t["efAway"])}</span>'


def match_flag(lang, key):
    """Small label above the first card of a list ('Next match' / 'Last match')."""
    return f'<p class="match-flag">{esc(I18N[lang][key])}</p>'


def fixture_item(lang, start, e, first=False):
    t = I18N[lang]
    flag = match_flag(lang, "efNext") if first else ""
    cls = "match fixture" + (" is-next" if first else "")
    if e.get("placeholder"):
        return (f'<li class="{cls} is-pending">{kickoff_tbd(lang)}<div class="match-body">{flag}'
                f'{match_title(EINTRACHT, t["efOpponentTbd"])}'
                f'<p class="match-meta"><span class="match-comp">{esc(t["efCompTbd"])}</span></p></div></li>')
    home, away = teams(e, e["opponent"])
    comp = f'<span class="match-comp">{esc(e["competition"])}</span>' if e.get("competition") else ""
    badge = f'<span class="tag">{esc(t["exampleBadge"])}</span>' if e.get("example") else ""
    return (f'<li class="{cls}">{kickoff_html(lang, start)}<div class="match-body">{flag}'
            f'{match_title(home, away)}<p class="match-meta">{comp}{venue_tag(lang, e)}{badge}</p></div></li>')


def result_item(lang, e, first=False):
    t = I18N[lang]
    flag = match_flag(lang, "efLast") if first else ""
    if e.get("placeholder"):
        return (f'<li class="match result is-pending">{kickoff_tbd(lang, with_time=False)}<div class="match-body">{flag}'
                f'{match_title(EINTRACHT, t["efOpponentTbd"], tbd_html(lang))}'
                f'<p class="match-meta"><span class="match-comp">{esc(t["efCompTbd"])}</span></p></div></li>')
    home, away = teams(e, e["opponent"])
    gf, ga = int(e["goals_for"]), int(e["goals_against"])
    hg, ag = (gf, ga) if e.get("home", True) else (ga, gf)
    outcome, ocls = (t["efWin"], "win") if gf > ga else (t["efDraw"], "draw") if gf == ga else (t["efLoss"], "loss")
    d = datetime.fromisoformat(e["date"])
    comp = f'<span class="match-comp">{esc(e["competition"])}</span>' if e.get("competition") else ""
    return (f'<li class="match result">{kickoff_html(lang, d.replace(tzinfo=d.tzinfo or TZ), with_time=False)}'
            f'<div class="match-body">{flag}{match_title(home, away, f"{hg}:{ag}")}'
            f'<p class="match-meta">{comp}{venue_tag(lang, e)}<span class="tag outcome outcome-{ocls}">{esc(outcome)}</span></p></div></li>')


def standing_html(lang):
    t = I18N[lang]
    s = EINTRACHT_DATA.get("standing")
    if not s:
        return f'<p>{esc(t["efTableEmpty"])}</p>'
    pend = bool(s.get("placeholder"))

    def val(k, fmt=str):
        return tbd_html(lang) if pend or s.get(k) is None else esc(fmt(s[k]))

    league = " ".join(str(s[k]) for k in ("competition", "season") if s.get(k))
    label = esc(t["efPosition"]) + (f' · {esc(league)}' if league else "")
    pos = tbd_html(lang) if pend or s.get("position") is None else f'{int(s["position"])}.'
    as_of = ""
    if not pend and s.get("as_of"):
        d = datetime.fromisoformat(s["as_of"]).date()
        as_of = f'<p class="match-note">{esc(t["efAsOf"].format(date=fmt_date(lang, d)))}</p>'
    stats = "".join(f'<div><dt>{esc(t[label_key])}</dt><dd>{val(k, fmt)}</dd></div>' for label_key, k, fmt in (
        ("efPlayed", "played", str), ("efPoints", "points", str), ("efGoalDiff", "goal_diff", lambda n: f"{int(n):+d}")))
    return (f'<div class="standing{" is-pending" if pend else ""}">'
            f'<p class="standing-pos"><span class="standing-n">{pos}</span><span class="standing-label">{label}</span></p>'
            f'<dl class="standing-stats">{stats}</dl>{as_of}</div>')


def reserve_buttons(lang):
    """'Reserve a table' reuses the existing contact links (phone, else WhatsApp). Hidden if the bar takes no reservations."""
    t = I18N[lang]
    if get("venue.accepts_reservations", report=False) is False:
        return ""
    phone, wa = get("contact.phone", report=False), get("contact.whatsapp", report=False)
    out = []
    if phone:
        out.append(f'<a class="btn btn-primary" href="tel:+{digits(phone)}">{esc(t["efReserve"])}</a>')
    if wa:
        cls = "btn btn-ghost" if out else "btn btn-primary"
        label = t["efReserveWa"] if out else t["efReserve"]
        out.append(f'<a class="{cls}" href="https://wa.me/{digits(wa)}" target="_blank" rel="noopener">{esc(label)}</a>')
    return f'<div class="cta-row">{"".join(out)}</div>' if out else ""


def render_eintracht(lang, other_href):
    t = I18N[lang]
    path = PAGES["eintracht"][lang]
    r = "../" * (path.count("/") + (0 if lang == DEFAULT_LANG else 1))
    fixtures = eintracht_fixtures()
    results = EINTRACHT_DATA.get("results", [])
    for key, pend in (("fixtures", any(e.get("placeholder") for _, e in fixtures)),
                      ("results", any(e.get("placeholder") for e in results)),
                      ("standing", bool((EINTRACHT_DATA.get("standing") or {}).get("placeholder")))):
        msg = f"EINTRACHT_DATA['{key}'] in build.py (placeholder shown on /{path})"
        if pend and msg not in TODOS:
            TODOS.append(msg)
    fx = ("".join(fixture_item(lang, s, e, first=(i == 0)) for i, (s, e) in enumerate(fixtures)))
    fx_html = (f'<ol class="match-list fixtures">{fx}</ol>' if fx else f'<p>{esc(t["efFixturesEmpty"])}</p>')
    fx_note = pending_note(lang, "efPendingFixtures") if any(e.get("placeholder") for _, e in fixtures) else ""
    rs = "".join(result_item(lang, e, first=(i == 0)) for i, e in enumerate(results))
    rs_html = (f'<ol class="match-list results">{rs}</ol>' if rs else f'<p>{esc(t["efResultsEmpty"])}</p>')
    rs_note = pending_note(lang, "efPendingResults") if any(e.get("placeholder") for e in results) else ""
    tb_note = pending_note(lang, "efPendingTable") if (EINTRACHT_DATA.get("standing") or {}).get("placeholder") else ""
    cta = reserve_buttons(lang)
    cta_band = f'''
                <section class="cta-band ticket" aria-labelledby="ef-reserve">
                    <p class="ticket-stub" aria-hidden="true"><span>{esc(t["efTicketStub"])}</span></p>
                    <div class="ticket-main">
                        <h2 id="ef-reserve">{esc(t["efCtaTitle"])}</h2>
                        <p>{esc(t["efCtaText"])}</p>
                        {cta}
                    </div>
                </section>''' if cta else ""
    sched = home_href(path) + PAGES["schedule"][lang]
    # 04: from the stadium to the bar (only with a confirmed stadium entry in local.nearby_places)
    stadium = nearby_place(SITE["local"]["stadium_name"])
    way = f'''
                <section class="page-sec ef-way" aria-labelledby="ef-way">
                    <h2 class="sec-head" id="ef-way"><span class="sec-n" aria-hidden="true">04</span>{esc(t["efWay"])}</h2>
                    <ul class="near-list">{near_item(lang, stadium, link_eintracht=False, hl=3)}</ul>
                    <p class="near-note">{esc(t["nearNote"])}</p>
                    {link_list(lang, home_href(path), ("local", "drinks"))}
                </section>''' if stadium else ""
    jump_items = [("ef-fixtures", "efFixtures"), ("ef-results", "efResults"), ("ef-table", "efTable")]
    if way:
        jump_items.append(("ef-way", "efWay"))
    jump = "".join(
        f'<li><a href="#{hid}"><span class="jump-n" aria-hidden="true">{n:02d}</span>{esc(t[key])}</a></li>'
        for n, (hid, key) in enumerate(jump_items, 1))
    jump_nav = f'<nav class="ef-jump" aria-label="{attr(t["efJumpLabel"])}"><ol>{jump}</ol></nav>'
    head = page_head(lang, path, t["efH1"], t["efIntro"], t["efKicker"], extra=cta + jump_nav, art=True, cls="ef-head")
    ticker = ticker_html([EINTRACHT, t["efKicker"], t["efFixtures"], t["efResults"], t["efTable"]], "ticker-alt")
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(t["efTitle"])}</title>
{meta_block(lang, path, t["efTitle"], t["efDesc"])}
{head_common(lang, path.count("/"), jsonld_scripts(lang, [bar_schema(lang)]))}</head>
<body>
    <a class="skip-link" href="#main">{esc(t["skip"])}</a>
{subpage_header(lang, path, "eintracht", other_href)}
    <main id="main" class="eintracht">
{head}
        {ticker}
        <div class="container page-body ef-body">
            <div class="ef-grid">
                <div class="ef-main">
                <section class="page-sec ef-fixtures" aria-labelledby="ef-fixtures">
                    <h2 class="sec-head" id="ef-fixtures"><span class="sec-n" aria-hidden="true">01</span>{esc(t["efFixtures"])}</h2>
                    {fx_note}
                    {fx_html}
                    <p class="more-link"><a href="{sched}">{esc(t["efAllMatches"])}<span aria-hidden="true">&nbsp;→</span></a></p>
                </section>
                <section class="page-sec ef-results" aria-labelledby="ef-results">
                    <h2 class="sec-head" id="ef-results"><span class="sec-n" aria-hidden="true">02</span>{esc(t["efResults"])}</h2>
                    {rs_note}
                    {rs_html}
                </section>
                </div>
                <div class="ef-side">
                <section class="page-sec ef-table" aria-labelledby="ef-table">
                    <h2 class="sec-head" id="ef-table"><span class="sec-n" aria-hidden="true">03</span>{esc(t["efTable"])}</h2>
                    {tb_note}
                    {standing_html(lang)}
                </section>{cta_band}{way}
                </div>
            </div>
            {back_link(lang, path, end=True)}
        </div>
    </main>
{site_footer(lang, home_href(path))}
    <script type="application/json" id="ui-data">{ui_data(lang)}</script>
    <script src="{r}js/main.js"></script>
</body>
</html>
'''


# ---------------------------------------------------------------- robots.txt + sitemap.xml
INDEXABLE = ["home", "schedule", "eintracht"]  # legal pages are noindex and stay out of the sitemap


def robots_txt():
    return (
        "# Everything may be crawled, including AI search/assistant crawlers (no per-bot rules on purpose).\n"
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )


def sitemap_xml():
    rows = []
    for key in INDEXABLE:
        for lang in LANGS:
            path = PAGES[key][lang]
            alts = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{page_url(l, PAGES[key][l])}"/>' for l in LANGS)
            alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{page_url(DEFAULT_LANG, PAGES[key][DEFAULT_LANG])}"/>'
            rows.append(f"  <url>\n    <loc>{page_url(lang, path)}</loc>{alts}\n  </url>")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<!-- Generated by build.py. lastmod is omitted on purpose: no reliable per-page change date. -->\n"
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(rows) + "\n</urlset>\n"
    )


# ---------------------------------------------------------------- build
def write(rel, content):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


def main():
    for lang in LANGS:
        pre = lang_prefix(lang)
        write(pre + "index.html", render_home(lang, switch_href(lang, "")))
        write(pre + "impressum.html", render_legal(lang, "impressum", switch_href(lang, "impressum.html")))
        write(pre + "datenschutz.html", render_legal(lang, "datenschutz", switch_href(lang, "datenschutz.html")))
        write(pre + PAGES["schedule"][lang] + "index.html", render_schedule(lang, switch_href(lang, PAGES["schedule"][lang])))
        write(pre + PAGES["eintracht"][lang] + "index.html", render_eintracht(lang, switch_href(lang, PAGES["eintracht"][lang])))
    write("robots.txt", robots_txt())
    write("sitemap.xml", sitemap_xml())
    if TODOS:
        print("\nTODO – missing data (left out of the output, or shown as a 'to be filled in' placeholder):")
        for k in sorted(set(TODOS)):
            print("  -", k)
    return 0


if __name__ == "__main__":
    sys.exit(main())
