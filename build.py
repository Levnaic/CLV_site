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
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SITE_URL = "https://DOMAIN"  # the ONE place to set the domain (no trailing slash)
LANGS = ["de"]
DEFAULT_LANG = "de"

DATA = Path(os.environ.get("CLV_DATA_DIR", ROOT / "data"))  # override only for tests
OUT = Path(os.environ.get("CLV_OUT_DIR", ROOT))
SITE = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
DRINKS = json.loads((DATA / "drinks.json").read_text(encoding="utf-8"))
I18N = json.loads((DATA / "i18n.json").read_text(encoding="utf-8"))

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


def alternates(path):
    """hreflang alternates (filled in once more than one language exists)."""
    return []


def home_description(lang):
    t = I18N[lang]
    n = get("venue.screens", report=False)
    return t["description"].replace("{screens}", t["descScreens"].format(n=n) if n else "")


def meta_block(lang, path, title, desc, social=True):
    url = page_url(lang, path)
    if len(desc) > 160:
        print(f"WARNING: meta description >160 chars ({len(desc)}): {path or '/'}", file=sys.stderr)
    t = I18N[lang]
    lines = [f'<meta name="description" content="{attr(desc)}">', f'<link rel="canonical" href="{attr(url)}">']
    lines += alternates(path)
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


def hours_summary(lang):
    days = SITE["hours"]["days"]
    names = I18N[lang]["days"]
    en = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return "; ".join(f'{names[d]}: {days[en[d]]["open"]}–{days[en[d]]["close"]}' for d in [1, 2, 3, 4, 5, 6, 0] if en[d] in days)


def faq_items(lang):
    """[(question, answer)] built only from confirmed site.json data; entries without data are left out."""
    t = I18N[lang]
    items = []
    if get("venue.shows_all_eintracht_matches") is True:
        a = t["faqA1"] + (t["faqA1sound"] if get("venue.sound_on_for_eintracht") is True else "")
        items.append((t["faqQ1"], a))
    acc = get("venue.accepts_reservations")
    how = loc(get("venue.reservation_how"), lang)
    if acc is True and how and not missing(how):
        items.append((t["faqQ2"], t["faqA2yes"].format(how=how)))
    elif acc is False:
        items.append((t["faqQ2"], t["faqA2no"]))
    walk = loc(get("local.walk_from_stadium"), lang)
    if walk and not missing(walk):
        a = t["faqA3"].format(stadium=SITE["local"]["stadium_name"], walk=walk)
        pt = loc(get("local.public_transport"), lang)
        if pt and not missing(pt):
            a += t["faqA3pt"].format(pt=pt)
        items.append((t["faqQ3"], a))
    if get("address.street"):
        items.append((t["faqQ4"], t["faqA4"].format(addr=full_address_line())))
    if SITE["hours"].get("confirmed") is True:
        items.append((t["faqQ5"], hours_summary(lang) + "."))
    parts = []
    if get("venue.seats"):
        parts.append(t["faqA6seats"].format(n=get("venue.seats")))
    if get("venue.screens"):
        parts.append(t["faqA6screens"].format(n=get("venue.screens")))
    if parts:
        items.append((t["faqQ6"], ", ".join(parts) + "."))
    return items


def faq_section(lang):
    items = faq_items(lang)
    if not items:
        return ""
    body = "\n                    ".join(
        f'<div class="faq-item reveal"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q, a in items)
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


# ---------------------------------------------------------------- page fragments
def head_common(lang, depth, extra=""):
    r = rel_root(lang, depth)
    return f'''    <meta name="theme-color" content="#111214" media="(prefers-color-scheme: dark)">
    <meta name="theme-color" content="#e4e9c4" media="(prefers-color-scheme: light)">
    <link rel="icon" href="{r}assets/icons/favicon.svg" type="image/svg+xml">
    <script>try{{var t=localStorage.getItem("theme");if(t==="light"||t==="dark")document.documentElement.dataset.theme=t}}catch(e){{}}</script>
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
    keys = ["themeLight", "themeDark", "menuOpen", "menuClose", "open", "closed", "until", "lbClose", "lbPrev", "lbNext", "mapTitle"]
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
    nav_contact = f'\n                    <li><a href="#contact">{esc(t["navContact"])}</a></li>' if contact else ""
    status = '<p class="status" id="status" aria-live="polite"></p>\n                        ' if SITE["hours"]["days"] else ""
    head = head_common(lang, 0, "")
    facts = venue_facts(lang)
    facts_html = ('<ul class="facts">' + "".join(f"<li>{esc(f)}</li>" for f in facts) + "</ul>") if facts else ""
    n_screens = get("venue.screens", report=False)
    sport5 = t["sport5Screens"].format(n=n_screens) if n_screens else t["sport5"]
    faq = faq_section(lang)
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
            <nav id="nav" class="nav" aria-label="{attr(t["navLabel"])}">
                <ul>
                    <li><a href="#about">{esc(t["navAbout"])}</a></li>
                    <li><a href="#sport">{esc(t["navSport"])}</a></li>
                    <li><a href="#drinks">{esc(t["navDrinks"])}</a></li>
                    <li><a href="#events">{esc(t["navEvents"])}</a></li>
                    <li><a href="#gallery">{esc(t["navGallery"])}</a></li>
                    <li><a href="#visit">{esc(t["navVisit"])}</a></li>{nav_contact}
                </ul>
            </nav>
            <div class="header-actions">
                <button class="theme-btn" id="themeBtn" type="button" aria-label="{attr(t["themeBtn"])}"></button>
                {lang_switch(lang, other_href)}
                <button class="menu-btn" id="menuBtn" type="button" aria-expanded="false" aria-controls="nav" aria-label="{attr(t["menuOpen"])}">
                    <span></span><span></span><span></span>
                </button>
            </div>
        </div>
    </header>

    <main id="main">
        <section class="hero" id="top">
            <img class="hero-img" src="{r}assets/img/hero.svg" width="1200" height="1600" fetchpriority="high" alt="{img_alt(t["heroAlt"])}">
            <div class="hero-overlay"></div>
            <div class="container hero-content">
                <p class="eyebrow">Frankfurt · Niederrad</p>
                <h1>C'est la vie<br><span>Sports Bar</span></h1>
                <p class="tagline">{esc(t["tagline"])}</p>
                <div class="hero-buttons">
                    <a class="btn btn-primary" href="#sport">{esc(t["btnLive"])}</a>
                    <a class="btn btn-ghost" href="#visit">{esc(t["btnRoute"])}</a>
                </div>
            </div>
        </section>

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
                <div class="grid grid-3">
                    <article class="card reveal"><h3>Bundesliga</h3><p>{esc(t["sport1"])}</p></article>
                    <article class="card reveal"><h3>Eintracht Frankfurt</h3><p>{esc(t["sport2"])}</p></article>
                    <article class="card reveal"><h3>Champions League</h3><p>{esc(t["sport3"])}</p></article>
                    <article class="card reveal"><h3>{esc(t["sport4Title"])}</h3><p>{esc(t["sport4"])}</p></article>
                    <article class="card reveal"><h3>{esc(t["sport5Title"])}</h3><p>{esc(sport5)}</p></article>
                </div>
            </div>
        </section>

        <section class="section" id="drinks">
            <div class="container">
                <h2>{esc(t["drinksTitle"])}</h2>
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
{faq}{contact_section}    </main>

    <footer class="site-footer">
        <div class="container footer-inner">
            <p>© <span id="year">2026</span> {esc(SITE["name"])} · {esc(SITE["area_label"])}</p>
            <p><a href="impressum.html">{esc(t["imprint"])}</a> · <a href="datenschutz.html">{esc(t["privacy"])}</a></p>
        </div>
    </footer>

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
    home = "index.html"
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
    <header class="site-header">
        <div class="container header-inner">
            <a class="brand" href="{home}" aria-label="{attr(SITE["name"])}">{logo_svg()}<span class="brand-title">C'est la <span>vie</span></span></a>
            <div class="header-actions">
                <button class="theme-btn" id="themeBtn" type="button" aria-label="{attr(t["themeBtn"])}"></button>
                {lang_switch(lang, other_href)}
            </div>
        </div>
    </header>
    <main class="container legal">
        <p><a href="{home}">{esc(t["legalBack"])}</a></p>
        <h1>{esc(title)}</h1>
        {body}
    </main>
    <script type="application/json" id="ui-data">{ui_data(lang)}</script>
    <script src="{r}js/main.js"></script>
</body>
</html>
'''


# ---------------------------------------------------------------- build
def write(rel, content):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel)


def main():
    for lang in LANGS:
        pre = lang_prefix(lang)
        write(pre + "index.html", render_home(lang))
        write(pre + "impressum.html", render_legal(lang, "impressum"))
        write(pre + "datenschutz.html", render_legal(lang, "datenschutz"))
    if TODOS:
        print("\nTODO – missing data in data/site.json (left out of the output):")
        for k in sorted(set(TODOS)):
            print("  -", k)
    return 0


if __name__ == "__main__":
    sys.exit(main())
