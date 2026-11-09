# TODO for the owner

Things only you can supply or confirm. After each change run `python3 build.py`. It prints the same
list of missing data (`TODO – missing data`). Business facts live in `data/site.json`; a value that
starts with `TODO` is left out of the site until you replace it.

Last updated: 2026-11-09.

## 1. Before going live (most important)

- [ ] **Domain**: choose the domain in `data/site.json` (`site.domain`) and set `SITE_URL` in `build.py`.
- [ ] **Real photos**: replace the placeholder images in `assets/img/` (hero, about, gallery-1 to gallery-6) with real photos, then set `images.photos_are_real` to `true`.
- [ ] **Social preview image**: add a real 1200×630 photo as `assets/img/og-image.jpg` (`images.og_image`).
- [ ] **Legal data** for Impressum and Datenschutz (`data/site.json`, section `legal`):
  - [ ] `owner_name` (owner or operating company)
  - [ ] `trade_register` (if there is one)
  - [ ] `vat_id` (if there is one)
  - [ ] `hosting_provider` (needed for the privacy policy)
  - [ ] Have the Impressum and Datenschutz texts checked by someone qualified before launch.
- [ ] **Opening hours**: check them and set `hours.confirmed` to `true`. Until then they are not in the page markup (schema).
- [ ] **Contact**: `contact.email`.
- [ ] **Delete the example matches** in `data/schedule.json` (`"example": true`) and enter real matches.

## 2. Facts about the bar (`data/site.json`, section `venue`)

- [ ] `music_choice_how`: **how do guests choose the music?** (jukebox, request at the bar, playlist or app). Until then the site only says that guests choose the music.
- [ ] `screens`: number of screens
- [ ] `seats`: number of seats
- [ ] `subscriptions`: for example `["Sky", "DAZN"]`
- [ ] `shows_all_eintracht_matches`: `true` or `false` (home and away)
- [ ] `sound_on_for_eintracht`: `true` or `false`
- [ ] `accepts_reservations`: `true` or `false`, and `reservation_how` (phone, WhatsApp or e-mail)
- [ ] `price_range`: `€`, `€€` or `€€€`
- [ ] `sports.confirmed`: check the sports list and set it to `true`
- [ ] `events.confirmed`: check the event texts and set it to `true` (the detail texts are still missing)

## 3. Eintracht page (`/eintracht/`, `/en/eintracht/`)

The page shows "to be filled in" boxes until real data is in.

- [ ] **Upcoming matches**: add Eintracht games to `data/schedule.json` (team name `Eintracht Frankfurt`).
- [ ] **Recent results**: `EINTRACHT_DATA["results"]` in `build.py` (date, opponent, competition, home or away, goals).
- [ ] **League table**: `EINTRACHT_DATA["standing"]` in `build.py` (competition, season, position, played, points, goal difference, date).
- [ ] Consider moving results and table into a data file such as `data/eintracht.json` (the frontend agent may not edit data files, so ask for it).

## 4. Location and nearby places (`data/site.json`, section `local`)

- [ ] **Check the distances** in `nearby_places`. They are rounded straight-line estimates (Deutsche Bank Park about 2 km, Festhalle about 3 km, Hauptbahnhof about 2.5 km), taken from travel sites, not from an official source.
- [ ] **Check the walking time** in `walk_from_stadium` ("about 25 minutes on foot") with a map.
- [ ] **Check the map position**: `geo` (50.085943, 8.651535) differs by about 230 m from the position in the Google Maps link (`google_business_profile`: 50.0840, 8.6499). Use the correct point.
- [ ] `public_transport`: stops and lines (tram and S-Bahn) near the bar.
- [ ] Optional: more nearby places (add entries to `nearby_places`).

## 5. Social media and profiles

- [ ] `social.instagram.url`
- [ ] `social.facebook.url` and handle
- [ ] `social.tiktok.url` and handle
- [ ] Keep the Google Business Profile in line with the site (name, address, hours, phone).

## 6. Naming

- [ ] **Which name is official?** The data says "C'est la Vie Café & Sportsbar", the page titles say "C'est la vie Sports Bar". Pick one and use it everywhere.

## 7. Repository and design decisions

- [ ] Decide what happens with the other design branches on GitHub (`design-pub`, `design-neon`, `design-modern`, `design-editorial`): keep, delete or reuse parts. Only `design-eintracht` / `main` is the main design.
- [ ] The new navigation (pages vs. sections) is only in `main`. The other designs do not have it yet. Ask if you want it in one of them.
- [ ] Branch `seo-music-beer-nearby` (music, beer, nearby places): merge into `main` when you are happy.
- [ ] Run a QA pass and a code review before going live (not done on any branch yet).
- [ ] Optional: set the upstream for the nav branch with `git branch --set-upstream-to=origin/nav-page-links nav-page-links`.

## 8. Tips for working with the agents

- Start the preview server in your own terminal before a browser check: `cd /home/l/projects/CLV_site && python3 -m http.server 8765 --bind 127.0.0.1`.
- Design branches and the status of each design are described in the Claude project memory (`design-catalog.md`, `design-variations-plan.md`).
