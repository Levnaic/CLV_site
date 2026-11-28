# TODO for the owner

Everything the website still needs from you, and what is left to do before it goes live.

How it works: all facts live in three data files. A value that starts with `TODO` is **left out of the
site** until you replace it. After every change run `python3 build.py`. It rebuilds the pages and
prints the list of data that is still missing (`TODO – missing data`).

| File | What is in it |
|---|---|
| `data/site.json` | the bar: name, address, contact, hours, venue facts, legal data, social links |
| `data/drinks.json` | the drinks menu: categories, drinks, sizes, prices |
| `data/schedule.json` | the matches you show live |

Texts with languages are written as `{"de": "...", "en": "...", "it": "..."}`. Fill in all three. A
missing English or Italian text falls back to German.

Last updated: 2026-11-28.

---

## 1. Information the site needs from you

A ready-to-send German message for Antonio is in `docs/nachricht-fehlende-daten.txt`. It asks only about the e-mail address, opening hours, spelling of the surname, trade register and VAT ID. Everything else in this file still has to be asked or checked separately.

Tick each item once the value is in the file.

### 1.1 Required before launch

| Done | What | Where (`data/site.json` unless noted) | Example / note |
|---|---|---|---|
| [x] | **Domain** | `site.domain` **and** `SITE_URL` in `build.py` | set: `https://cestlavie-frankfurt.de` (without www; www will redirect to it, see `docs/deployment.md`) |
| [x] | **Owner or company name** (Impressum) | `legal.owner_name` | set: Antonio Petrilo. Registered on him; ask whether it is spelled with one or two "l" (in the message) |
| [ ] | **Trade register entry**, if there is one | `legal.trade_register` | `Amtsgericht Frankfurt am Main, HRB 12345`; remove the line if there is none |
| [ ] | **VAT ID**, if there is one | `legal.vat_id` | `DE123456789`; remove the line if there is none |
| [x] | **Hosting provider** (privacy policy) | `legal.hosting_provider` | set: Hetzner Online GmbH |
| [ ] | **E-mail address** | `contact.email` | shown on the contact page and in the Impressum, which generally needs one (§ 5 DDG). First ask whether the bar has its own address; publishing a private one needs consent |
| [x] | **Check the phone number** | `contact.phone`, `contact.whatsapp` | confirmed, WhatsApp on the same number |
| [ ] | **Opening hours** | `hours.days`, then set `hours.confirmed` to `true` | provisional: 11:00–03:00 every day, open all week. Hours can change. Not confirmed yet, **but visitors already see these hours and the "open now" label**: confirm before launch |
| [x] | **Official name** | `name` | set: C'est la Vie Café & Sportsbar |

### 1.2 Photos

For the start the home page shows **only the big photo at the top**. The gallery and the "About us"
photo are switched off.

| Done | Photo | File | Size |
|---|---|---|---|
| [x] | Big photo at the top of the home page (bar with bartender and cocktails) | `hero-1600.webp`, `hero-960.webp` | in place, 1600 × 1200. Optional upgrade: a larger original, 2400 px wide or more |
| [ ] | Consent of the person in the big photo to publish it (get it before launch, best in writing) | | |
| [x] | `assets/shank.jpeg` (original of the big photo) is kept on this computer only: ignored by git, so it is not on GitHub or the server. Back it up yourself | | |
| [x] | Unused pictures `hero-portrait.webp` and `hero.svg` deleted | | |
| [x] | Preview image for WhatsApp, Facebook etc. (made from the big photo; it shows the same person, so the consent must cover it) | `og-image.jpg` | 1200 × 630 |

- The big photo is cropped by the page, differently on phones and wide screens, so keep the subject in
  the centre. Text never lies on top of it. A red colour filter is added in the browser (the `--hero-`
  lines in `css/themes/eintracht.css`); the image files are not tinted. Use only photos you may
  publish, with the consent of people shown.
- To replace it: put the new photo in `assets/img/` in two sizes (1600 and 960 px wide) and tell the
  agent. The crop may need adjusting.
- The big photo always has its description. `images.photos_are_real` stays `false` while
  the switched-off photos are placeholders. It turns on the descriptions of the
  "About us" and gallery photos.

**Later (not needed for launch):** the "About us" photo (`about`, landscape, at least 1200 × 900) and
six gallery photos (`gallery-1` … `gallery-6`, square, at least 800 × 800). Add the files first, then
set `images.show_about_photo` or `images.show_gallery` to `true` in `data/site.json`.

### 1.3 Facts about the bar (`venue`)

Until these are filled in, the site simply does not mention them.

| Done | Question | Where | Answer format |
|---|---|---|---|
| [x] | How many **screens**? | `venue.screens` | set: 2 |
| [x] | How many **seats**? | `venue.seats` | set: 30 |
| [x] | Which **TV subscriptions**? | `venue.subscriptions` | set: DAZN |
| [x] | Do you take **reservations**? | `venue.accepts_reservations` | set: yes |
| [x] | If yes: **how** do guests reserve? | `venue.reservation_how` | set: by phone |
| [x] | **How do guests choose the music?** | `venue.music_choice_how` | set: ask at the bar |
| [x] | **Price range** | `venue.price_range` | set: `€` (suggested by the AI from limited price data; change if wrong) |
| [x] | Check the **sports list** (`sports.items`) | `sports.items`, then `sports.confirmed` to `true` | confirmed: football, basketball, Champions League, Bundesliga, internationals and major tournaments. Check that DAZN covers what the site promises |
| [ ] | **Bundesliga promise** (before launch): the site says every matchday is shown live, but only DAZN is listed. From a web search summary (pages not opened), 2025–2029: DAZN has the Saturday conference and Sunday games, Sky has Friday and the single Saturday games. Does the bar have Sky? | `sports`, `sport1` in `data/i18n.json` | without Sky, reword in all three languages, e.g. "Saturday conference and Sunday matches live". Check the Champions League wording too |
| [ ] | **Public screening rights** (before launch): are the TV subscriptions allowed for showing in a bar? | with the provider | not checked |
| [x] | Check the **four events** | `events.items` | confirmed: all four happen occasionally, no drink specials or prizes |
| [ ] | Optional: **more details per event** (day, time, price, prizes) | `events.items[].more` | de/en/it; the event card then opens to show the text |

### 1.4 Drinks menu (`data/drinks.json`)

| Done | What | Note |
|---|---|---|
| [ ] | **Legal check: food additives.** The footnote numbers 1–14 from the printed menu were removed at the owner's request. Ask whether the website menu must still declare additives (German law) | old numbers are in git history |
| [x] | **Prices and sizes** | confirmed |
| [ ] | Check the **English and Italian drink names** and cocktail ingredients | |

### 1.5 Matches (`data/schedule.json`)

**The schedule is hidden for now** (`SHOW_SCHEDULE = False` in `build.py`). The code and data are kept. To bring it back: set it to `True`, and in `.github/workflows/deploy.yml` add `spielplan` to `GENERATED` and set `MIN_PAGES` to `15`. Not needed for launch while hidden.

One entry per match you show. Past matches are hidden 3 hours after kick-off, but only when the site is rebuilt. Once deployment is switched on, GitHub rebuilds the site every day and on every change to `main`.

```json
{
  "id": "bvb-fcb-2027-02-06",
  "competition": "Bundesliga",
  "home": "Borussia Dortmund",
  "away": "Bayern München",
  "start": "2027-02-06T15:30:00+01:00",
  "note": { "de": "", "en": "", "it": "" }
}
```

- [ ] Delete the three example matches.
- [ ] Add the upcoming matches.
- [ ] Keep the list up to date (for example once a week).

### 1.6 Location (`local`)

| Done | What | Where | Now |
|---|---|---|---|
| [x] | **Map position** | `geo.lat`, `geo.lng` | set from the OpenStreetMap entry for the bar |
| [ ] | **Public transport**: check the line numbers again **after the timetable change on 13.12.2026** (also whether tram 20 stops at DFB-Campus regularly) | `local.public_transport` | from OpenStreetMap: DFB-Campus 21/61, Triftstraße 12/19, Schwarzwaldstraße 15 |
| [x] | **Walking time from the stadium** | `local.walk_from_stadium` | about 2 km, 25-30 minutes (map route) |
| [x] | **Nearby places** | `local.nearby_places` | DFB-Campus 0.3 km, Uniklinik 1.2 km, Deutsche Bank Park 1.7 km (straight line) |

### 1.7 Social media

| Done | What | Where | Note |
|---|---|---|---|
| [ ] | Instagram link | `social.instagram.url` | the handle is now `01744800000`, which looks like a phone number. Correct it too. |
| [ ] | Facebook link and page name | `social.facebook.url`, `.handle` | |
| [ ] | TikTok link and handle | `social.tiktok.url`, `.handle` | |
| [ ] | Google Business Profile: same name, address, hours and phone as the site | on Google | |

---

## 2. Before going live

- [ ] **Legal check**: have the Impressum and Datenschutz (and their English and Italian versions) checked by someone qualified. The German texts are the binding ones.
- [ ] **Italian review**: a native speaker should read every Italian text. They were written by the AI and not checked by a person: the `"it"` blocks in `data/i18n.json`, `data/site.json` and `data/drinks.json`.
- [ ] **Final check** (again after the changes of 2026-11-28) of the finished site on a computer and a phone (no automated tests, by your choice). Checked in a headless browser on 2026-11-26; the layout and photo viewer with the photo switches on are still unchecked.
- [ ] **Deployment**: the server, HTTPS and the domain are ready. Do the one-time setup in `docs/deployment.md` (steps 1–5), then go live (step 6).
- [ ] **Search engines**: set `NOINDEX = False` in `build.py` (while it is `True`, every page tells search engines not to index it). Leave `robots.txt` as it is.
- [x] **Old Eintracht page** (`/eintracht/`, `/en/eintracht/`, `/it/eintracht/`) removed. If an older version with these pages was ever online, redirect the three addresses (301) to the schedule page.
- [ ] After launch: add the site to Google Search Console and keep the Google Business Profile in sync.

## 3. Open technical work (from the audit of 2026-11-28)

Set up later:

- [ ] **Browser caching:** add `Cache-Control "no-cache"` to the `header` block of the Caddy config in `docs/deployment.md` (and on the server), so returning visitors get updates. Do it at go-live (step 6).
- [ ] **Run the site check before upload:** add a step to `.github/workflows/deploy.yml` that serves the build and runs `check_site.py`. Fix the "todo" false alarm below first.

Nice to have:

- [ ] `check_site.py` rejects any page containing "todo", which also matches the Italian word "metodo". Match whole words only.
- [ ] Delete the unused colour themes (`css/palette.css` and every file in `css/themes/` except `eintracht.css`) and update the comments that mention them. They are uploaded to the server.
- [ ] Update `README.md`: it calls the images placeholders and lists the hidden schedule page as generated. Delete the outdated AI prompt.
- [ ] Delete the unused texts `ogDescription`, `navVisit`, `navContact`, `faqNav` in `data/i18n.json` (all three languages).
- [ ] Add a "page not found" page and point the web server to it.

## 4. Repository clean-up

- [ ] Merge branch `hero` (owner data, hidden schedule, new hero photo) into `main` and push. A push to `main` starts the Deploy workflow (it only builds until `DEPLOY_ENABLED` is `true`).
- [x] `drinks-menu-merge` merged into `main`.
- [ ] Delete the old branches on GitHub that are already in `main`: `design-eintracht`, `drinks-menu-merge`, `final-redesign`, `light-tema-jaka-akcenat`, `nav-page-links`, `seo-music-beer-nearby`.
- [ ] Decide what happens with the branches that are not in `main` (`design-pub`, `design-neon`, `design-modern`, `design-editorial`, `redesign`, `theme-italy`, `theme-neon`, `theme-ocean`, `theme-sunset`): keep, delete or reuse parts. The red, black and white matchday design on `main` is the chosen one.

## 5. Tips

- Preview the site locally: `cd /home/l/projects/CLV_site && python3 -m http.server 8765 --bind 127.0.0.1`, then open http://127.0.0.1:8765.
- `python3 build.py` after every change in `data/`. Never edit the generated `.html` files by hand.
- Design branches and their status are described in the Claude project memory (`design-catalog.md`, `design-variations-plan.md`).
