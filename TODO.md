# TODO for the owner

Everything the website still needs from you, and what is left to do before it goes live.

How it works: all facts live in three data files. A value that starts with `TODO` is **left out of the
site** until you replace it. After every change run `python3 build.py`. It rebuilds the pages and
prints the list of data that is still missing (`TODO – missing data`).

| File | What is in it |
|---|---|
| `data/site.json` | the bar: name, address, contact, hours, venue facts, legal data, social links |
| `data/drinks.json` | the drinks menu: categories, drinks, sizes, prices, additives |
| `data/schedule.json` | the matches you show live |

Texts with languages are written as `{"de": "...", "en": "...", "it": "..."}`. Fill in all three. A
missing English or Italian text falls back to German.

Last updated: 2026-11-26.

---

## 1. Information the site needs from you

Tick each item once the value is in the file.

### 1.1 Required before launch

| Done | What | Where (`data/site.json` unless noted) | Example / note |
|---|---|---|---|
| [x] | **Domain** | `site.domain` **and** `SITE_URL` in `build.py` | set: `https://cestlavie-frankfurt.de` (without www; www will redirect to it, see `docs/deployment.md`) |
| [x] | **Owner or company name** (Impressum) | `legal.owner_name` | set: Antonio Petrilo (check the spelling) |
| [ ] | **Trade register entry**, if there is one | `legal.trade_register` | `Amtsgericht Frankfurt am Main, HRB 12345`; remove the line if there is none |
| [ ] | **VAT ID**, if there is one | `legal.vat_id` | `DE123456789`; remove the line if there is none |
| [x] | **Hosting provider** (privacy policy) | `legal.hosting_provider` | set: Hetzner Online GmbH |
| [ ] | **E-mail address** | `contact.email` | shown on the contact page and in the Impressum |
| [x] | **Check the phone number** | `contact.phone`, `contact.whatsapp` | confirmed, WhatsApp on the same number |
| [ ] | **Opening hours** | `hours.days`, then set `hours.confirmed` to `true` | provisional: 11:00–03:00 every day, open all week. Hours can change. Not confirmed yet |
| [x] | **Official name** | `name` | set: C'est la Vie Café & Sportsbar |
| [ ] | **Real matches** | `data/schedule.json` | delete the three `"example": true` entries, add the real matches (see 1.5) |

### 1.2 Photos

For the start the home page shows **only the big photo at the top**. The gallery and the "About us"
photo are switched off.

| Done | Photo | File | Size |
|---|---|---|---|
| [ ] | Big photo at the top of the home page (bar, screens, atmosphere) | `hero` | best: landscape, about 2400 × 1600, web file about 400 KB or less |
| [ ] | Preview image for WhatsApp, Facebook etc. (the current one is text with old lime-green colours) | `og-image.jpg` | exactly 1200 × 630 |

- Phones show only about the middle of a landscape photo, so keep the subject in the centre. The page
  darkens the photo and covers parts of it with text and red shapes. Do not use a photo with important
  text or faces near the edges. Use only photos you may publish, with the consent of people shown.
- A second, upright photo for phones (at least 1200 × 1600) is possible with a small code change.
  One photo or several is not decided yet.
- Put the file in `assets/img/` and tell the agent its name: the page still points to `hero.svg`.
  Then set `images.photos_are_real` to `true`. This turns on the descriptions of all shown photos, so
  check that the hero description matches your photo.

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
| [ ] | Check the **four events** (Match Day, Partyabende, Private Feiern, Quizabend): do they really happen? | `events.items`, then `events.confirmed` to `true` | all four now say "On request", without drink specials or prizes. Confirm this, then set `events.confirmed` to `true` |
| [ ] | Optional: **more details per event** (day, time, price, prizes) | `events.items[].more` | de/en/it; the event card then opens to show the text |

### 1.4 Drinks menu (`data/drinks.json`)

| Done | What | Note |
|---|---|---|
| [ ] | **Additive numbers 1–14**: what does each number on the printed menu mean? | Required by German law. Fill `additives_legend` as `{"1": {"de": "mit Farbstoff", "en": "with colouring", "it": "con colorante"}, ...}`. The numbers are hidden until then. |
| [ ] | Check **every price and size** against the printed menu | |
| [ ] | Check the **English and Italian drink names** and cocktail ingredients | |

### 1.5 Matches (`data/schedule.json`)

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
| [ ] | **Map position**: the site and the Google listing are about 230 m apart. Which point is the door of the bar? | `geo.lat`, `geo.lng` | site 50.085943, 8.651535; Google 50.0840, 8.6499 |
| [ ] | **Public transport**: nearest stops and lines | `local.public_transport` | de/en/it, e.g. "Tram 12 und 15, Haltestelle …" |
| [ ] | Check the **walking time from the stadium** | `local.walk_from_stadium` | "about 2 km, roughly a 25-minute walk" |
| [ ] | Check the **distances** to Deutsche Bank Park (2 km), Festhalle (3 km), Hauptbahnhof (2.5 km) | `local.nearby_places` | rounded straight-line estimates |
| [ ] | Optional: more places nearby | `local.nearby_places` | name, kind, distance |

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
- [ ] **Final check** of the finished site on a computer and a phone (no automated tests, by your choice). Checked in a headless browser on 2026-11-26; the layout and photo viewer with the photo switches on are still unchecked.
- [ ] **Deployment**: the server, HTTPS and the domain are ready. Do the one-time setup in `docs/deployment.md` (steps 1–5), then go live (step 6).
- [ ] **Search engines**: set `NOINDEX = False` in `build.py` (while it is `True`, every page tells search engines not to index it). Leave `robots.txt` as it is.
- [x] **Old Eintracht page** (`/eintracht/`, `/en/eintracht/`, `/it/eintracht/`) removed. If an older version with these pages was ever online, redirect the three addresses (301) to the schedule page.
- [ ] After launch: add the site to Google Search Console and keep the Google Business Profile in sync.

## 3. Repository clean-up

- [ ] Merge the finished branch (`drinks-menu-merge`) into `main`. Merging starts the Deploy workflow (it only builds until `DEPLOY_ENABLED` is `true`).
- [ ] Decide what happens with the other design branches (`design-pub`, `design-neon`, `design-modern`, `design-editorial`): keep, delete or reuse parts. The red, black and white matchday design on `main` is the chosen one.
- [ ] Branch `seo-music-beer-nearby`: merge into `main` or delete.

## 4. Tips

- Preview the site locally: `cd /home/l/projects/CLV_site && python3 -m http.server 8765 --bind 127.0.0.1`, then open http://127.0.0.1:8765.
- `python3 build.py` after every change in `data/`. Never edit the generated `.html` files by hand.
- Design branches and their status are described in the Claude project memory (`design-catalog.md`, `design-variations-plan.md`).
