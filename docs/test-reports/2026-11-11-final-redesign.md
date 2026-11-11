# QA report: branch `final-redesign` (commit 8ad0d89)

Date: 2026-11-11 · Agent: qa · Scope: Italian language, language dropdown, slanted nav indicator,
"Besuch & Kontakt" page and home visit strip (diff `main...final-redesign`, 27 files).

## Important: the browser pass was not run

The browser tool refuses `http://127.0.0.1:8765` (`net::ERR_BLOCKED_BY_CLIENT`). The qa agent may
only open the local dev and preview servers on ports **5173 and 4173**, and nothing was listening on
4173. So none of the runtime checks in the test plan ran: no screenshots, no viewport or overflow
measurements, no keyboard or mouse runs, no console logs, no rendered contrast.

What was done instead: a static review of the generated HTML, `css/style.css`, `js/main.js` and the
branch diff. Geometry, contrast and JS behaviour were checked by reading the code and calculating
the values. Every finding below says whether it is **confirmed in code** or **needs a browser
check**.

To unblock the browser pass, start the preview on an allowed port, for example
`python3 -m http.server 4173 --bind 127.0.0.1`, then run qa again. The other option is to add
port 8765 to the qa agent's browser allowlist, which is the user's decision. TODO.md §9 tells
people to use 8765, which does not match the qa allowlist.

## Summary

| Area | Result (static) | Browser check |
|---|---|---|
| 1. Italian pages (6) present, `lang="it"`, hreflang, og:locale | pass | not run |
| 2. Language dropdown: markup, links to the same page in each language, no-JS | pass (all 18 pages map correctly) | not run |
| 2. Language dropdown: keyboard/JS logic | pass, 1 minor (F1) | not run |
| 3. Nav slant: divider vs hover bar vs current plate, mobile bar | pass (angles identical by calculation) | not run |
| 4. Contact page content, FAQ JSON-LD = visible text, back links, footer link | pass | not run |
| 4. Home visit strip, section numbers `data-n` = heading counters | pass | not run |
| Overflow at 360/768/1200/1440, header fit at 1200 (DE/EN/IT) | cannot be judged statically, risk noted (F5) | **not run** |
| Console errors | no error path found in `main.js` on any page type | **not run** |
| Accessibility basics | 1 h1 per page, no new heading skips, 44px targets on new controls, contrast >= 4.5:1 | not run (no axe) |
| SEO of the new pages | pass, titles a bit long (F7) | n/a |

Findings: **0 blocker · 0 major · 7 minor · 4 cosmetic** (plus 3 older minors that were already on `main`).

## Findings

### F1 · minor · confirmed in code: Escape does not close the language menu unless focus is inside it
- Where: `js/main.js:105` (`langBox.addEventListener('keydown', …)`), all pages, all viewports.
- Steps: in Safari (and Firefox on macOS), open the menu with a **mouse click** on the summary,
  then press Escape.
- Expected: the menu closes. Actual: these browsers do not focus a `<summary>` on mouse click, so
  the keydown goes to `body`, the listener on `#langBox` never fires and the menu stays open.
  Chrome and Edge focus the summary, so they behave correctly. **Needs a check in Safari.**
- Fix (frontend): handle Escape on `document` while `langBox.open`, and keep the
  `preventDefault()` so the mobile overlay stays open on the first Escape.

### F2 · minor · confirmed in code: the language button's accessible name does not contain its visible label as a word
- Where: `build.py` `lang_switch`, summary `aria-label="Sprache: Deutsch"` / `"Language: English"` /
  `"Lingua: Italiano"`. The visible label is `DE` / `EN` / `IT`.
- Expected (WCAG 2.5.3 Label in Name): the visible text is part of the name, so a speech-input
  user can say "click DE". Actual: "DE" only appears inside "Deutsch".
- Fix (frontend): for example `aria-label="Sprache: Deutsch (DE)"`, or drop `aria-label` and add
  visually hidden text next to the code.

### F3 · minor · confirmed in code (old logic, new places): the open/closed chip uses the visitor's device time zone
- Where: `js/main.js:168` `isOpen(new Date())`. It now shows on the home visit strip and twice on
  each contact page.
- Steps: set the device to Europe/London and open `/en/` at 15:30 London time on a Monday
  (16:30 in Frankfurt).
- Expected: "Open now · until 01:00". Actual: "Closed right now".
- Fix (frontend): compute the weekday and hour in `Europe/Berlin`, using
  `Intl.DateTimeFormat(…, {timeZone:'Europe/Berlin'})`.

### F4 · minor · confirmed in content: German placeholder text on `/it/calendario/`
- What: the example matches show "Beispiel-Team A … F" and the competition "Beispiel" on the
  Italian page. The tag correctly says "Esempio – non è una data reale".
- This goes away when the owner deletes the example matches (TODO.md §1). If the examples stay
  until launch, the example labels need translating (frontend, `build.py`/`data/schedule.json`).
  Note: this contradicts the earlier "no German on /it/" check, which probably skipped data-driven
  fields.

### F5 · minor · needs a browser check: header fit at 1200px has less spare room than the CSS comment says
- Where: `css/style.css:895-906`. The comment says there is "about 10px to spare" in German and
  Italian at 1200px. That was measured in Playwright, and headless Chromium hides scrollbars.
- Risk: in desktop browsers with classic scrollbars (Windows about 17px, Linux about 15px), a
  1200px window still matches `min-width:1200px` but the layout is only about 1183px wide. That is
  about 7px short. Calculated effect: nothing overlaps. The header row spills about 7px into the
  container's 32px right padding, and the page should not get a horizontal scrollbar.
- A second risk is the first visit with `font-display: swap`. The nav uses Barlow Condensed 700
  normal, which is not preloaded (only 800 italic is). Until it loads, a wider fallback font can
  overflow the header and shift the layout.
- Check on jupiter or locally: `/` and `/it/` at window widths of 1200 and 1215 with
  `--hide-scrollbars` off and fonts throttled.

### F6 · minor · confirmed in CSS: the new footer link "Besuch & Kontakt" is about 24px tall
- Where: `.footer-inner a` on every page (inline text, 0.95rem × 1.6 line height).
- The project goal is 44px touch targets. WCAG 2.5.8 still passes through the "inline" exception.
  Optional fix (frontend): give the footer links `display:inline-block; padding-block` up to 44px.

### F7 · minor · confirmed in markup: the contact page titles are 69–71 characters
- DE "Anfahrt, Öffnungszeiten & Kontakt – C'est la vie Sports Bar Frankfurt" (69),
  EN (71), IT (69). Search results usually cut off around 60 characters, so "Frankfurt" or
  "Francoforte" at the end will likely be lost.
- Meta descriptions are fine: DE 151, EN 153, IT 150 characters.
- Optional (content/frontend): put the place name earlier or shorten the brand part.

### F8 · cosmetic: contact cards
- The phone number shows as `+491744800000` without grouping (contact card and Impressum).
  `+49 174 4800000` reads better; the `tel:` link stays as it is.
- `.grid-3` holds 2 cards, so from 900px the third column is empty. This fills itself once
  `contact.email` is supplied (TODO.md §1).

### F9 · cosmetic: "Route planen" opens the place page, not a route
- All "Route planen / Plan route / Calcola il percorso" buttons link to
  `maps.app.goo.gl/U6kGrxTTeQX3aGoNA`, which is the place card. The button text suggests
  directions. A link of the form `https://www.google.com/maps/dir/?api=1&destination=…`
  would open directions straight away. The link also opens a new tab without saying so.

### F10 · cosmetic: language links use `aria-current="true"`
- The link points to the current page in the current language, so `aria-current="page"` is the
  more precise value. Screen readers announce "current page" instead of just "current".

### F11 · cosmetic: copy details (already covered by the native-speaker review in TODO.md §7)
- IT: weekday names are capitalised ("da Lunedì a Giovedì", "Lunedì" in the hours table). Italian
  writes them in lower case.
- DE: the hidden text "Freitag bis Samstag" would read better as "Freitag und Samstag", and the same
  applies to EN "Friday to Saturday".

### Already on `main` (not caused by this branch, for the record)
- P1 · minor: on `/spielplan/`, `/en/schedule/` and `/it/calendario/` the headings go from h1 to h3
  (match titles) before the first h2.
- P2 · minor: `.mobile-bar` is a `<div aria-label=…>` without a role. `aria-label` is not supported
  on generic elements, and axe reports it for review.
- P3 · minor: without JS, the mobile nav below 1200px cannot be opened. The new language dropdown
  does work without JS.

## What passed in the static review (details)

- **Language mapping (item 2):** read the language menu of `/`, `/kontakt/`, `/spielplan/`,
  `/eintracht/`, `/impressum.html`, `/en/`, `/en/contact/`, `/en/schedule/`, `/en/eintracht/`,
  `/en/datenschutz.html`, `/it/`, `/it/contatti/`, `/it/calendario/`, `/it/eintracht/` and
  `/it/impressum.html`. Each one offers DE, EN and IT versions of the **same** page type. The
  current language has `aria-current` and the visible check mark (`.lang-check` shows only when
  `aria-current` is set). Every link has `hreflang` and `lang`. The globe, caret and check icons
  are `aria-hidden`.
- **Dropdown logic (item 2):** native `<details>` toggles on click, Enter and Space without JS.
  ArrowDown/ArrowUp on the summary open the menu and focus the first/last link. In the menu they
  wrap (`(i+step+n)%n`), and Home/End jump to the ends. Escape closes, `preventDefault()` keeps
  the overlay open, and focus returns to the summary. An outside click closes the menu, and so does
  focus leaving it (`focusout` with `relatedTarget` outside). In the mobile overlay the Tab loop now
  includes `summary`, and the menu links only while it is open (closed `<details>` content has no
  boxes). The first Escape closes the language menu and the second closes the overlay. The menu
  (`z-index:2`, positioned) paints above the fixed overlay (`z-index:auto`).
- **Nav slant (item 3), calculated:** the divider uses `skewX(-12deg)` on 3px × 1.7rem. The hover
  bar uses the same size with `skewX(-12deg) scaleY(s)`. Scale is applied before skew, so the
  edge is x' = x − tan12°·(s·y) and y' = s·y. The slope stays tan 12° throughout the animation,
  and at the end the matrix is identical to the divider's, `matrix(1,0,-0.2126,1,0,0)`. The
  current plate uses `skewX(-12deg) scaleX(s)` with origin left. Its edges are x' = s·x − tan12°·y,
  so they stay at 12° during the whole wipe. The mobile overlay's current indicator is a 5px red bar
  with `skewX(-12deg)`, no longer the old vertical inset shadow. Hover is suppressed on the current
  link. At 1200–1339 the bar's top corner (about 5.9px) sits just right of the 5.6px padding, but
  at cap height it is only about 4.2px, so it does not touch the glyphs.
- **Section numbers (item 4):** the home nav has `data-n` 01–05 for about, sport, drinks, events and
  gallery. These match `counter(sec)` on the five `.section` elements. The visit strip is not a
  `.section`, so it is not counted. On sub pages, Drinks and Events are 03 and 04. On the contact
  page, `.section` 01–04 match the jump-board tiles 01–04.
- **Contact page (item 4):** hours table, map (loads only after a click), address, Route and Call,
  directions with 3 nearby places, 6 FAQs, 2 contact cards, back links at the top and bottom, and
  a footer link on every page that was read. The JSON-LD has `BarOrPub` (`@id …/#bar`) and a
  `FAQPage` with `url` set to the page itself and `inLanguage` de/en/it. All 6 × 3 questions and
  answers match the visible text word for word. Canonical, hreflang de/en/it/x-default (x-default
  points to DE) and og:locale with 2 alternates are present.
- **Home visit strip:** `#visit` with an `h2`, a `data-status` chip (hidden while empty without
  JS), address, three lines of hours that match the `hours` data (Mon–Thu 16–01, Fri–Sat 16–03,
  Sun 14–00), Route (Google Maps, `rel=noopener`), Call (`tel:+491744800000`) and a link to the
  contact page. Links from other pages: the schedule page links to `../kontakt/#visit` (IT:
  `../contatti/#visit`), and the Eintracht page links to `../kontakt/#local` (IT:
  `../contatti/#local`).
- **Contrast (calculated from the theme tokens):** white on `#e1000f` is 4.99:1 (visit strip,
  current plate, open menu button). The language button outline is 48% white on `#0b0b0c`, about
  5.0:1 (needs 3:1). The menu text is white on `#19181a`. The codes use `#aaa29e` on `#19181a`
  (about 7.1:1) and the check mark `#ff4d55` (about 5.4:1). Focus rings: `#ff4d55` on the night
  header is 6.0:1, and white on the red strip is 5.0:1. One gap: if the mouse hovers the
  keyboard-focused language link, the `#ff4d55` ring sits on red (low contrast). This is an edge
  case and not filed as a finding.
- **Touch targets:** the language summary is at least 44×44px, menu links are at least 44px tall,
  `.more-link` and `.near-link` are at least 44px, buttons are 50px, jump tiles 5rem, and the back
  link 44px.
- **Reduced motion:** turns off all transitions and animations (dropdown drop-in, nav wipe and bar,
  ticker), shows `.reveal` content, sets `scroll-behavior: auto` and hides the ticker toggle.
- **Console errors (static):** every DOM lookup in `main.js` is guarded (`?.`, `if (lb)`,
  `if (!spyLinks.length)`, `#mapBtn` only on the contact pages). Scroll-spy only collects `href^="#"`
  links, so it is empty on sub and legal pages. No unguarded call was found.

## Results
| Level | Command | Passed | Failed | Skipped |
|---|---|---|---|---|
| Static review (HTML/CSS/JS) | Read + `git diff main...final-redesign` | 9 plan areas | 0 | 0 |
| Browser / exploratory | Playwright MCP on `http://127.0.0.1:8765` | 0 | 0 | all (blocked: port not allowed) |
| Automated tests | none in this repo (no `tests/` or `e2e/`) | – | – | – |

## Coverage
No backend business logic and no test suite. Requirement coverage: items 1–4 were checked by
static review only. Their runtime behaviour has not been tested.

## Tests not run (and why)
All of these need the browser on an allowed port (4173 or 5173), or the jupiter e2e workflow,
which does not exist yet:
- Viewports 360/768/1200/1440 × the 9 pages × light/dark: horizontal overflow, header fit at 1200
  in DE/EN/IT (see F5), screenshots.
- Running the language dropdown with mouse and keyboard; no-JS run; outside tap on iOS Safari (a
  document `click` listener can miss taps on non-clickable elements there, so worth one device
  check); Safari Escape (F1).
- Mobile menu: Tab loop, the Escape sequence, links closing the overlay.
- Scroll-spy on home at the bottom of the page (visit strip in view, so gallery should not be marked).
- Console errors on every page; axe-core scan (WCAG 2.2 AA); rendered contrast; visible focus.
- `prefers-reduced-motion` emulation.

## Verdict: NOT READY to merge into main (verification incomplete, no defect blocks it)

- The static review found **no blocker and no major**. F1–F11 are minor or cosmetic and can be
  fixed after merging.
- The plan's runtime checks (overflow, header fit, keyboard and mouse behaviour, console, axe)
  **did not run**, so this report cannot confirm them.
- What it takes to reach READY: run the browser pass (preview on port 4173 or 5173, then rerun qa).
  If that pass finds no blocker or major, the verdict becomes READY. It is worth fixing F1 and F3
  before then, because both are small JS changes (frontend agent).
