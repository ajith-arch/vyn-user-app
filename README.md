# VYN User — Web

Front-end build of **VYN User**, the student/staff side of VYN, an autonomous campus-delivery concept.
Screens are recreated from the VYN Figma design system in plain HTML, CSS and JavaScript — no framework, no build step.

> One autonomous system. Two radically different human experiences.
> The user tracks the delivery, not the robot.

## Screens

| # | Screen | Status |
|---|--------|--------|
| 01 | Home | ✅ Built |
| 04–14 | Send (person / department), Review, Robot assigned, Live tracking, Secure handoff, Delivery complete, exception states | Designed in Figma, coming next |

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
css/styles.css      Tokens, components, responsive layout
js/map.js           Pan/zoom engine, live robots, nearest-robot ETA
js/app.js           Navigation, sheets, campus switching, toasts
assets/             Campus map (WebP + JPEG fallback), favicon
```

## Scope note

VYN is a product-design concept. Robot positions and ETAs on this page are simulated for the prototype; no real fleet data is used.
