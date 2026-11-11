# QA report: branch `final-redesign`

Date: 2026-11-11 · Agent: qa
Scope: Italian language, language dropdown, slanted nav indicator, "Besuch & Kontakt" page and
home visit strip (diff `main...final-redesign`).

| Round | Commit | Method |
|---|---|---|
| 1 | 8ad0d89 | Static review of the generated HTML, `css/style.css`, `js/main.js` and the diff. The browser was blocked because port 8765 is not allowed. |
| 2 | 69022ea (fixes F1–F3, F5–F7, F9) | Browser pass on `http://127.0.0.1:4173`: Playwright Chromium, headless, cache-busted with `?v=N` and `fetch(…, {cache:'reload'})`, `.reveal` set to `.visible` before full-page screenshots |
| 3 | fa9e42f (fixes N1, N2, N5, C1) | Short browser re-check plus a regression check, same setup |

Screenshots are in `docs/test-reports/img/`. Round 3 screenshots start with `r3-`.

## Verdict: READY to merge into main (after round 3, commit fa9e42f)

There are no blockers and no majors left. N1 (major), N2 and N5 are fixed and checked in the
browser, and the regression checks are clean. What is still open is minor or cosmetic and does not
block the merge:
- N4: desktop nav targets are 28–30px tall (WCAG 2.5.8 passes).
- C2: `aria-current="true"` on the language links.
- C3: phone number unformatted, 2 cards in a 3-column grid.
- C4: copy details for the native-speaker review.
- C5: hyphenated jump tile.
- C6: example-match placeholders (data).
- C7: the DE and EN home pages have the same title.

As before, every push still needs your approval.

## Round 3: re-check of fa9e42f

Setup: style sheets and script reloaded with `{cache:'reload'}` (the new CSS has
`scroll-margin-top` and the 1399px rule) and `localStorage.theme` cleared.

| Check | Result |
|---|---|
| **N1** at 360, 768 and 1100, starting at y = 3000: open the menu, press Escape, click the language button, press Escape | y stays at 3000 at every step. **Fixed** |
| **N1**: overlay current-section mark after jumping to drinks, events, gallery or sport via the overlay and reopening it | the right section is marked and y does not change (`img/r3-mobile-menu-360-current-drinks.png`) |
| **N1** at 1440, starting at y = 3000: click the language button, press Escape (focus returns to the button), click the theme button | y stays at 3000 |
| **N1** at 1440: one Shift+Tab from the first link in `main` into the header (from y = 1500), then 4 more | lands on the language button, y stays at 1500 |
| Focus not hidden under the header (WCAG 2.4.11), `/kontakt/` 1440: 31 Tab stops through `main` | 0 stops hidden under the sticky header. Tab from the header into `main` lands at top 122 (header bottom 72) |
| Anchor jumps, 21 cases × 360 and 1440: nav links (including the mobile overlay and `../#drinks` from a sub page), hero "Anfahrt" → `#visit` (DE and IT), beer link → `#drinks-menu`, jump tiles on `/kontakt/` and `/eintracht/`, schedule and Eintracht pages → contact `#visit`/`#local` in DE/EN/IT, FAQ "Alle Orte" → `#local` | every target lands exactly 12px under the header: top 72 with a 60px header, top 84 with a 72px header. The exception is `#visit` at 1440, which is the last section, so the page simply ends there |
| Scroll-spy at 360 and 1440 | about, sport, drinks, events and gallery are each marked correctly |
| **N2** sweep from 1200 to 1520px in 10px steps × with and without a 17px scrollbar × `/`, `/en/`, `/it/`, `/kontakt/`, `/en/contact/`, `/it/contatti/` (396 measurements) | 0 problems: the header buttons never go past the content box or the viewport, the nav-to-buttons gap is at least 12px, and the nav is one row with no inner overflow. **Fixed** |
| **N5** titles | `/` 63, `/en/` 63, `/it/` 65, `/kontakt/` 53, `/en/contact/` 56, `/it/contatti/` 59 characters. og:title and twitter:title match. **Fixed** |
| Language button name (C1) | `aria-label` and Chrome's accessible name are both "DE, Sprache: Deutsch", "EN, Language: English" and "IT, Lingua: Italiano". `expanded` is exposed. **Fixed** |
| Regression: 360/768/1200/1440, plus 1600/1920 for the header, × light/dark × `/`, `/it/`, `/kontakt/`, `/en/` (48 loads) | no horizontal overflow, no element outside the viewport, 1 h1, header within its container |
| Console errors and warnings, page errors, failed requests, HTTP ≥ 400 (all round 3 runs) | none |

Correction to round 2: the case "Shift+Tab into the header scrolls to the very top" was a flaw in
my test, not part of N1. The script walked back through every link in `main`, which scrolls the
page up naturally. The one-step check above is the correct test. The rest of N1 (menu button,
language button, theme button, Escape refocus) was real and is fixed.

New cosmetic finding: **C7**, the DE and EN home pages have the same title, "C'est la vie Sports Bar
Frankfurt | Eintracht & Bundesliga live". hreflang already separates the two versions; an EN wording
such as "Watch Eintracht & Bundesliga live" is optional.

## Summary (after round 2, for the record)

| Area | Result |
|---|---|
| 1. Italian pages: `lang`, hreflang, og:locale, canonical | pass (18 pages) |
| 2. Language dropdown: mouse, keyboard, no-JS, links to the matching page | pass (54 links on 18 pages; 18 click-throughs land on the right page and language) |
| 2. Language dropdown inside the mobile overlay (Tab loop, Escape order) | pass |
| 3. Nav slant: divider = hover bar = current plate = page plates = mobile bar | pass, 12.00° in every case, also mid-animation |
| 4. Contact page, home strip, FAQ JSON-LD, anchors from other pages, footer link | pass |
| Scroll-spy | pass while scrolling. **Fails after the mobile menu is opened** (N1) |
| Horizontal overflow at 360/768/1200/1440, light and dark | pass (92 page loads). One edge case at 1340–1349px with a classic scrollbar (N2) |
| Header fit at 1200 (DE/EN/IT, with or without a 17px scrollbar) | pass, everything on one row, 12px between nav and buttons |
| Console errors and warnings, failed requests, HTTP ≥ 400 | none (92 loads plus all interaction runs) |
| Accessibility basics | pass: 1 h1 and no heading skips on the 6 key pages, visible focus on all new controls, contrast ≥ 4.99:1 (scan), reduced motion honoured. Desktop nav targets 28–30px (N4) |
| SEO spot-check of the new pages | pass. Contact titles are 53–59 chars; home titles are still 73–82 (N5) |
| Re-check of the round-1 fixes F1, F2, F3, F5, F6, F7, F9 | all fixed |

Open findings: **0 blocker · 1 major (N1) · 3 minor (N2, N4, N5) · 6 cosmetic**.

## Round 2: browser results

### Open findings

#### N1 · major · Focusing anything in the sticky header scrolls the page up (mobile menu, language and theme buttons)
- Pages and viewports: all pages, all viewports. Reproduced in Chromium. Firefox and Safari not checked.
- Steps (360×780, `/`):
  1. Scroll to y = 3000.
  2. Tap the menu button.
  3. Press Escape.
- Expected: the page stays at y = 3000. While the overlay is open, the slanted current-section bar
  marks the section you were reading.
- Actual: opening scrolls to y = 2602 and Escape scrolls again to y = 2204. Every focus of a header
  control moves the page up by about half a screen.
- Same jump in other cases:
  - At 768px it is 520px.
  - At 1440px, one mouse click on the **language button** or the theme button goes from 3000 to 2542.
  - Escape in the language menu refocuses the button, which triggers the same jump.
  - Shift+Tab from the contact page content back into the header scrolls to the very top (y = 0).
- Knock-on effect: in the mobile menu, tap "Getränke", wait, then open the menu again. The
  overlay now marks "02 Live Sport" instead of "03 Getränke", because the page has moved
  (`img/mobile-menu-360-current-drinks.png`). The new mobile indicator therefore shows the wrong
  section. Reproduced in 4 of 4 runs.
- Root cause (verified):
  - `html { scroll-padding-top: calc(var(--header-h) + 12px) }` (`css/style.css:54`). Header
    controls sit inside that padding area, so focusing them makes the browser "scroll them into
    view" and the sticky header comes along.
  - With `scroll-padding-top: 0` there is no jump. `focus({preventScroll:true})` also avoids it, but
    only for focus set from JS.
- Suggested fix (frontend): move the offset from `html` to the scroll targets, for example
  `main [id], main :is(a,button,summary,[tabindex]) { scroll-margin-top: calc(var(--header-h) + 12px) }`.
  I tested this in the browser: a theme click no longer scrolls, and `#events` still lands at
  84px under the 72px header.
- Note: this line and the menu focus code are unchanged since `main`, so the theme and menu buttons
  on `main` jump too. This branch adds two more triggers (the language button and the Escape
  refocus), and the problem directly breaks requirement 3 (the current-section indicator).

#### N2 · minor · From 1340px, the DE and IT home header is wider than its container
- The denser 1200–1339 rules stop at 1340. From there the home header row (3 plates and 5 sections)
  needs 23–36px more than the 1276px content box. The header buttons spill into the container's
  32px right padding. Measured at 1340–1520 on `/` and `/it/`; `/en/` and the sub pages fit.
- With a classic 17px scrollbar (simulated with `html { padding-right:17px }`), at window widths of
  about 1340–1349 the language button ends 6–8px past the visible area, which causes horizontal
  scrolling of the page.
- Without a scrollbar, nothing overlaps: the gap between nav and buttons is 20px. The right margin
  is about 30px narrower than the left one (`img/f12-home-de-1440-header.png`).
- Fix (frontend): let the dense rules run to about 1380px (scrollbar included), or give the header
  row more room above 1340.

#### N4 · minor · Desktop nav links are 28–30px tall
- Page plates and section links at 1200px and wider. WCAG 2.5.8 (24px) passes. The project goal of
  44px is missed on touch screens that get the desktop nav, such as iPad Pro landscape (1366px)
  and touch laptops. The brand link is 169×40. The sizes did not change in this branch.

#### N5 · minor · Home titles are still long
- DE 73, EN 79 and **IT 82 (new)** characters. Search results will likely cut them off. The contact
  titles were fixed (53/56/59).

#### Cosmetic
- C1: the language button's accessible name is "DE , Sprache: Deutsch" in Chromium. The visually
  hidden span is positioned absolutely, which inserts a space before the comma. Screen readers read
  it correctly; dropping the comma would avoid it.
- C2 (round-1 F10): language links still use `aria-current="true"`; `"page"` would be more precise.
- C3 (round-1 F8): the phone number shows unformatted (`+491744800000`), and there are 2 contact
  cards in a 3-column grid.
- C4 (round-1 F11): IT weekday names are capitalised; DE "Freitag bis Samstag" (native review,
  TODO.md §7).
- C5: the jump tile "ÖFFNUNGSZEI-TEN" is hyphenated at 1440px because the page head keeps 34%
  free on the right. Readable.
- C6 (round-1 F4, data): "Beispiel-Team …" on `/it/calendario/`. The coordinator asked to leave
  this placeholder data alone.

### Re-check of the round-1 fixes

| Finding | Check in the browser | Result |
|---|---|---|
| F1 Escape in Safari | Open with the mouse, `blur()` the button (Safari behaviour), press Escape: the menu closes and focus returns to the button. In the mobile overlay the first Escape closes only the language menu and the second closes the overlay, both for keyboard and for mouse with blur | fixed |
| F2 label in name | Chromium AX tree: role `DisclosureTriangle`, name "EN , LANGUAGE: ENGLISH", `expanded` and `controls=langMenu` exposed, no `aria-label` | fixed (C1 cosmetic) |
| F3 time zone | Fixed clock with `timezoneId` set to London, New York, Berlin and Tokyo. Mon 16:30 Berlin shows "open until 01:00". Mon 15:30 shows "closed". Sat 02:30 Berlin shows "open until 03:00" (Friday hours). Mon 00:30 Berlin (still Sunday in London) shows "closed", and the "today" row is Monday | fixed |
| F5 header at 1200 | 1200, 1215 and 1339 windows, each with and without a 17px scrollbar, on DE/EN/IT home and sub pages: one row, nav-to-buttons gap 12px, no overflow, no wrapped labels | fixed (new edge at 1340, see N2) |
| F6 footer targets | All footer links are 44px tall | fixed |
| F7 contact titles | 53 / 56 / 59 characters | fixed (home titles: N5) |
| F9 (coordinator's "F10") route | Every Route button and the mobile bar link to `google.com/maps/dir/?api=1&destination=…` with `target=_blank` | fixed |

### What passed (details)

- **Overflow:**
  - Dark theme: 18 pages × 4 viewports.
  - Light theme: home and contact pages in all 3 languages × 4 viewports (92 loads).
  - Result: `scrollWidth == clientWidth` everywhere, no element outside the viewport, exactly one
    h1.
  - The mobile overlay (360/768, DE/EN/IT, home and contact) has no horizontal overflow.
  - The language menu at 360 sits at x 80–288 with no overflow.
- **Language dropdown, mouse:** click opens, a second click closes, an outside click closes.
- **Language dropdown, keyboard:**
  - Enter and Space toggle; Escape closes and returns focus to the button.
  - ArrowDown/ArrowUp on the closed button open the menu on the first/last link; in the menu they
    wrap; Home/End jump to the ends.
  - Tab from the last link moves on and closes the menu; Shift+Tab from the button closes it too.
  - Enter on English goes to `/en/contact/`.
  - Focus ring: 3px `#ff4d55` on the button and an inset ring on the links.
  - Screenshot: `img/lang-menu-1440-open-kbd.png`.
- **No-JS** (separate context with `javaScriptEnabled:false`):
  - The `<details>` opens, links are 44px tall, and clicking or Enter on English from
    `/it/calendario/` lands on `/en/schedule/` (3 of 3).
  - FAQ content is visible and the status chips are hidden.
  - Screenshot: `img/lang-menu-360-nojs.png`.
  - Harness note: the first no-JS click timed out once (a `waitForNavigation` race in the test
    script). Rerun 3 of 3 passed. This is not a product issue.
- **Language mapping:** every page offers DE, EN and IT versions of the same page type, matching
  its `hreflang` links. The current language is marked, and the code in the button matches
  `<html lang>`. One click per page lands on the correct canonical and language.
- **Mobile menu (360):**
  - Opening focuses the first link; `aria-expanded` and the label update; `main` becomes inert;
    body overflow is hidden.
  - The Tab loop runs Spielplan … Galerie, theme, language button, menu button, logo and back to
    the start. Shift+Tab works in reverse.
  - With the language menu open, the loop includes its 3 links.
  - Section links close the overlay and land at 72px (under the 60px header).
  - Resizing to 1300px closes the overlay.
  - Screenshot: `img/mobile-menu-360-de.png`.
- **Nav slant** (computed transforms, 1200 and 1440):
  - The divider, the hover bar at the end of its animation, the current plate at the end of its
    animation and the page plates are all `matrix(1,0,-0.212557,1,0,0)`, which is 12.00°.
  - Mid-animation the hover bar is `matrix(1,0,-0.1065,0.501)` and the current plate is
    `matrix(0.0054,0,-0.2126,1)`. Both still have 12.00° edges.
  - The divider and hover bar are both 3×27.19px, colour `#e1000f`.
  - The mobile current bar is a 5px red `skewX(-12deg)` bar.
  - Screenshots: `img/nav-hover-1440.png`, `img/nav-current-drinks-1440.png`.
- **Scroll-spy** (no menu involved), 360 and 1440: about, sport, drinks, events and gallery are each
  marked when scrolled into view. On the visit strip nothing is marked at 360; at 1440 gallery stays
  marked while it is still on screen, which is the intended code behaviour.
- **Home strip:**
  - Chip filled ("Jetzt geöffnet · bis 01:00").
  - Address and hours (Mo–Do 16–01, Fr–Sa 16–03, So 14–00).
  - Route opens Google Maps directions, Call is `tel:+491744800000`, and the link goes to the
    contact page.
  - Buttons are 50px tall and the more-link is at least 44px.
  - Layout at 360, 768 and 1200: `img/visit-strip-360.png`, `img/visit-strip-768.png`,
    `img/visit-strip-1200.png`.
  - Focus ring is white on red (`img/visit-strip-focus-1440.png`).
- **Contact page:**
  - Hours table with today's row (Wednesday) highlighted.
  - Map loads only after a click; I did not click it, to avoid an external request.
  - The 6 FAQs equal the JSON-LD in all 3 languages (0 mismatches); the FAQPage `url` is the page
    itself.
  - Jump tiles go to `#visit`, `#local`, `#faq` and `#contact`.
  - Back links at the top and bottom.
  - Full page: `img/kontakt-1440-light-full.png`, `img/it-contatti-360-dark-full.png`.
- **Anchors from other pages:** `/spielplan/`, `/eintracht/`, `/en/schedule/`, `/en/eintracht/`,
  `/it/calendario/` and `/it/eintracht/` link to the contact page's `#visit` / `#local`. The target
  lands 12px under the header at 360 and at 1440.
- **Theme:** the button switches light/dark, the label and icon update, the choice survives a
  reload, and the system preference is the default.
- **Contrast scan** (every visible text node, background resolved from colours and skewed
  pseudo-element plates):
  - Dark theme, 7 pages: minimum 4.99:1, no failures.
  - Light theme: the only failures were footer texts, a false positive. The footer background is a
    gradient that the script cannot read, and it is night `#0b0b0c` (checked in
    `img/footer-light-kontakt.png`).
  - axe-core was not run (see "Tests not run").
- **Reduced motion:** no dropdown animation, nav transitions 0s, no ticker animation and no ticker
  toggle, `.reveal` visible, `scroll-behavior: auto`, no status pulse.
- **Visible focus** (keyboard): contact head buttons, jump tiles, map button, FAQ links, contact
  cards, back link, footer links and strip buttons all show a 3px outline with `:focus-visible`.

## Round 1: static code review (commit 8ad0d89, kept for the record)

Round 1 findings and their status after 69022ea:

| ID | Severity | Finding | Status |
|---|---|---|---|
| F1 | minor | Escape did not reach `#langBox` when the summary was not focused (Safari/Firefox macOS mouse open) | fixed |
| F2 | minor | Summary `aria-label` "Sprache: Deutsch" did not contain the visible "DE" (WCAG 2.5.3) | fixed |
| F3 | minor | Open/closed chip used the device time zone | fixed |
| F4 | minor | German "Beispiel…" placeholders on `/it/calendario/` | open, data (C6) |
| F5 | minor | Header fit at 1200 measured without scrollbar | fixed (new edge N2) |
| F6 | minor | Footer link about 24px tall | fixed |
| F7 | minor | Contact titles 69–71 chars | fixed |
| F8 | cosmetic | Phone unformatted, 2 cards in a 3-column grid | open (C3) |
| F9 | cosmetic | "Route planen" opened the place page, not directions | fixed |
| F10 | cosmetic | `aria-current="true"` instead of `"page"` | open (C2) |
| F11 | cosmetic | Copy details (IT weekday capitals, DE "bis") | open (C4) |
| P1–P3 | minor | Already on `main`: h1 → h3 skip on schedule pages, `aria-label` on the `.mobile-bar` div, no-JS mobile nav | open, not part of this branch |

Static checks that passed in round 1 and were confirmed in round 2:
- language link mapping
- dropdown key logic
- slant geometry: hover bar `skewX scaleY`, plate `skewX scaleX`, both keep 12° at every animation
  step
- section numbers: `data-n` 01–05 match the `counter(sec)` headings, the visit strip is not counted,
  and the contact sections 01–04 match the jump tiles
- FAQ JSON-LD text equals the visible text
- hreflang de/en/it/x-default and og:locale
- meta descriptions 150–153 characters
- token contrast: white on `#e1000f` 4.99:1; language button outline about 5:1
- 44px targets on the new controls
- reduced motion
- no unguarded DOM calls in `main.js`

## Results
| Level | Command | Passed | Failed | Skipped |
|---|---|---|---|---|
| Static review (round 1) | file reads + `git diff main...final-redesign` | 9 areas | 0 | 0 |
| Browser: overflow, header, h1, console | Playwright, 18 pages × 4 viewports × theme (92 loads), plus header sweep 1200–1520 with/without a 17px scrollbar | 92 | 0 | 0 (edge N2 noted) |
| Browser: language dropdown (mouse, keyboard, no-JS, mapping) | Playwright, 54 links, 18 click-throughs, 3 no-JS runs | all | 0 | 0 |
| Browser: mobile menu (focus loop, Escape order, links, resize) | Playwright 360 | all | 1 (N1, page jumps / wrong current section, 4 of 4 runs) | 0 |
| Browser: nav slant, scroll-spy, strip, contact page, anchors, F3 time zones, theme, reduced motion, focus, contrast scan | Playwright | all | 0 | 0 |
| Automated test suite | none in this repo | – | – | – |

## Coverage
No backend business logic and no test suite. Requirements 1–4 are covered by this browser pass;
everything except N1 passes.

## Tests not run (and why)
- **axe-core (WCAG 2.2 AA scan):** `@axe-core/playwright` is not installed, and loading axe from a
  CDN would mean opening another site. A custom contrast and heading scan was used instead. Adding
  `@axe-core/playwright` as a test dependency needs your approval.
- **Real browsers other than Chromium:** Safari (F1 behaviour, iOS outside tap) and Firefox (N1).
  Only Chromium is available here.
- **Real classic scrollbars:** headless Chromium hides them, so they were simulated with
  `html { padding-right: 17px }`.
- **Map iframe loading** (OpenStreetMap, external request) was not clicked.
- **Automated end-to-end suite on jupiter:** the workflow does not exist yet.

## Round 2 verdict (replaced by round 3: READY, see the top): NOT READY to merge into main

The only finding that had to be fixed for READY (fixed in fa9e42f):

- **N1 (major):** focusing a header control (menu button, language button, theme button, or Escape
  refocus) scrolls the page up about half a screen. Opening and closing the mobile menu loses about
  800px of scroll position, and the new current-section indicator then marks the wrong section.
  It is a one-rule CSS fix that I tested in the browser (`scroll-margin-top` on the targets instead
  of `scroll-padding-top` on `html`). Agent: frontend.

Recommended in the same pass, but not blocking: N2 (1340px header edge, frontend) and N5 (home
titles). Everything else passed in the browser: all 3 languages, the dropdown with mouse, keyboard
and no JS, the 12° slant, the contact page, the strip, no overflow at 360/768/1200/1440 in either
theme, and no console errors. After N1 is fixed, a short re-check of the mobile menu and the header
buttons is enough to move to READY.
