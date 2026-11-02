# VYN User — Web

Front-end build of **VYN User**, the student/staff side of VYN, an autonomous campus-delivery concept.
Screens are recreated from the VYN Figma design system in plain HTML, CSS and JavaScript — no framework, no build step.

> One autonomous system. Two radically different human experiences.
> The user tracks the delivery, not the robot.

## Screens

All screens from the Figma file are built and linked into a working prototype. Open **More** in the tab bar for the full list.

| # | Screen | File |
|---|--------|------|
| 01 | Home | `index.html` |
| 04 | Send item — Person | `send.html#person` |
| 05 | Send item — Department | `send.html#department` |
| 06 | Review delivery | `review.html` |
| 07 | Robot assigned | `assigned.html` |
| 08 | Live tracking | `tracking.html` |
| 09 | Secure handoff | `handoff.html` |
| 10 | Delivery complete | `complete.html` |
| 11 | Receiver unavailable | `receiver-unavailable.html` |
| 12 | Department closing | `department-closing.html` |
| 13 | Robot delayed | `delayed.html` |
| 14 | AI-assisted delivery decision | `ai-decision.html` |
| — | Screen index | `screens.html` |

**Main journey:** Home → Start delivery → Department → Review → Robot assigned → Live tracking (the package moves live and arrives) → Delivery complete.
**Person journey:** Send item → Person → AI-assisted decision → Robot assigned.
**Exceptions:** picking *Library Front Desk* opens Department closing; every option card updates the main button so the user always sees what will happen before confirming.

## Home — what's included

- **Live campus map** — the illustrated campus map with drag-to-pan, pinch / ctrl-scroll / double-tap zoom, `+` / `−` controls and keyboard panning (arrow keys, `+`, `−`).
- **Robots moving on real walkways**, your location pulse, a **nearest-robot callout** with a live ETA (tap any robot to inspect it), an **Avg ETA** pill and **Locate me**.
- **Campus selector** bottom sheet (remembers your choice), **notifications** sheet, campus status strip with weather.
- **All services** grid, **Start delivery** / **Receive a request** actions and the tip card.
- **Mobile-first, mobile-only**: the layout matches the 393 px Figma frame and stays a phone-width column (max 430 px) on every screen, centred on larger displays.
- **Accessible**: semantic landmarks, skip link, labelled controls, focus-visible rings, focus-trapped sheets with `Esc` to close, `prefers-reduced-motion` support, and status never shown by colour alone.

## Design tokens

Colours, spacing, radii and type mirror the `VYN Tokens` collection in Figma (`css/styles.css` → `:root`).
Font: [Inter](https://rsms.me/inter/). Icons are the exact SVGs exported from the Figma file.

## Run locally

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Any static server works — or just enable **GitHub Pages** (Settings → Pages → Deploy from branch → `main` / root).

## Project structure

```
index.html          Home screen markup + SVG icon sprite
*.html              Flow screens 04–14 and the screen index
css/styles.css      Tokens, components, responsive layout
js/map.js           Pan/zoom engine, live robots, nearest-robot ETA
js/app.js           Home navigation, sheets, campus switching, toasts
css/flow.css        Flow components (top bar, option cards, notices, timeline, route maps…)
js/flow.js          Shared flow behaviour (tabs, chips, option → button, countdowns, rating)
js/routemap.js      Route maps on the campus image, with live progress
js/icons.js         Shared glyph sprite for flow screens
tools/build_pages.py  Generates the flow pages from one template
assets/             Campus map (WebP + JPEG fallback), favicon
```

## Scope note

VYN is a product-design concept. Robot positions and ETAs on this page are simulated for the prototype; no real fleet data is used.
