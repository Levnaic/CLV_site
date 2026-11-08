# C'est la vie Sports Bar – Website

Static site (HTML/CSS/vanilla JS). All HTML pages are **generated** by `build.py`
(Python 3, standard library only). Do not edit the generated HTML by hand.

## Files

| Path | Purpose |
|---|---|
| `data/site.json` | All business facts (address, phone, hours, venue facts, social links, legal data). Values starting with `TODO` are missing and are left out of the output. |
| `data/drinks.json` | Drinks menu (DE/EN names, sizes, prices). |
| `data/i18n.json` | All page texts in German and English. |
| `data/schedule.json` | Match schedule (see below). |
| `build.py` | Generates `index.html`, `impressum.html`, `datenschutz.html`, `spielplan/`, and the same under `en/` (`en/schedule/`). |
| `css/`, `js/`, `assets/` | Design, small progressive-enhancement script, images. |

## Build

```sh
python3 build.py                 # regenerate all pages
python3 -m http.server 8000      # preview at http://localhost:8000
```

`build.py` prints a TODO report: every fact still missing in `data/site.json`.
The domain is set in one place: `SITE_URL` at the top of `build.py`.

## Updating the match schedule

1. Open `data/schedule.json` and add one object per match the bar shows:

   ```json
   {
     "id": "sge-bvb-2027-03-06",
     "competition": "Bundesliga",
     "home": "Eintracht Frankfurt",
     "away": "Borussia Dortmund",
     "start": "2027-03-06T15:30:00+01:00",
     "note": { "de": "Ton an, Reservierung empfohlen", "en": "Sound on, booking recommended" }
   }
   ```

   `start` needs the time zone offset (`+01:00` winter, `+02:00` summer). `id` must be unique and
   URL-safe. `note` is optional.
2. Delete the entries with `"example": true` (they are clearly marked examples and get no
   `SportsEvent` schema).
3. Run `python3 build.py`, check the result, then commit and deploy.

Past matches disappear automatically **at build time** (3 hours after kick-off), so rebuild at
least once per matchday – or after every schedule change.

## Before launch

- Fill the `TODO` values in `data/site.json` (see the build report) and confirm opening hours
  (`hours.confirmed: true`), sports and events.
- Replace the placeholder images in `assets/img/` with real photos and set
  `images.photos_are_real` to `true` (this switches on the descriptive alt texts).
- Set the real domain in `SITE_URL` in `build.py`.
