/* VYN — interactive campus map
 * Pan / pinch / wheel / keyboard zoom over the illustrated campus map,
 * with live robots moving along real walkways and a nearest-robot callout.
 */
(function () {
  "use strict";

  const IMG_W = 1420;
  const IMG_H = 1058;

  // Paths were traced on the 361 × 271 design export; convert to full-res image px.
  // (Full-res export is 1448 px wide, trimmed 14 px each side to drop rounded corners.)
  const K = 1448 / 361;
  const pt = (x, y) => [x * K - 14, y * K - 14];

  const USER = pt(110, 148);

  const ROBOTS = [
    { id: "VYN-107", path: [pt(150, 151), pt(189, 151.5), pt(228, 152)], speed: 15, t: 0.15 },
    { id: "VYN-112", path: [pt(121, 84), pt(176, 50), pt(240, 12)], speed: 18, t: 0.35 },
    { id: "VYN-104", path: [pt(118, 84), pt(129, 112), pt(140, 140)], speed: 12, t: 0.8 },
    { id: "VYN-118", path: [pt(212, 250), pt(270, 216), pt(330, 182)], speed: 22, t: 0.5, busy: true },
    { id: "VYN-109", path: [pt(228, 152), pt(227.5, 125), pt(227, 98)], speed: 11, t: 0.6 },
    { id: "VYN-121", path: [pt(36, 108), pt(44, 134), pt(52, 160)], speed: 10, t: 0.2 },
  ];

  const PX_PER_MIN = 190;          // walking-pace robots, in image px per minute
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const root = document.querySelector("[data-map]");
  if (!root) return;
  const layer = root.querySelector("[data-map-layer]");
  const markersEl = root.querySelector("[data-markers]");
  const card = root.closest(".map-card");
  const calloutEl = card.querySelector("[data-callout]");
  const calloutName = card.querySelector("[data-callout-name]");
  const calloutEta = card.querySelector("[data-callout-eta]");
  const avgEtaEl = card.querySelector("[data-avg-eta]");
  const locateBtn = card.querySelector("[data-locate]");
  const zoomInBtn = card.querySelector('[data-zoom="in"]');
  const zoomOutBtn = card.querySelector('[data-zoom="out"]');

  /* ---------------- View state ---------------- */
  const view = { s: 1, x: 0, y: 0, min: 1, max: 4, vw: 0, vh: 0 };

  // Returns false until the map has a real size (hidden tab, not laid out yet)
  function measure() {
    const r = root.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return false;
    view.vw = r.width;
    view.vh = r.height;
    view.min = Math.max(view.vw / IMG_W, view.vh / IMG_H);
    view.max = view.min * 3;
    return true;
  }

  function clamp() {
    if (!Number.isFinite(view.s) || view.s <= 0) view.s = view.min;
    if (!Number.isFinite(view.x)) view.x = 0;
    if (!Number.isFinite(view.y)) view.y = 0;
    view.s = Math.min(view.max, Math.max(view.min, view.s));
    const minX = view.vw - IMG_W * view.s;
    const minY = view.vh - IMG_H * view.s;
    view.x = Math.min(0, Math.max(minX, view.x));
    view.y = Math.min(0, Math.max(minY, view.y));
  }

  function apply(animate) {
    clamp();
    layer.classList.toggle("is-animating", !!animate && !reduceMotion);
    layer.style.transform = `translate3d(${view.x}px, ${view.y}px, 0) scale(${view.s})`;
    markersEl.style.setProperty("--inv", (1 / view.s).toFixed(5));
    zoomInBtn.disabled = view.s >= view.max - 1e-4;
    zoomOutBtn.disabled = view.s <= view.min + 1e-4;
    if (animate) setTimeout(() => layer.classList.remove("is-animating"), 460);
  }

  function zoomAt(px, py, nextScale, animate) {
    const s = Math.min(view.max, Math.max(view.min, nextScale));
    view.x = px - (px - view.x) * (s / view.s);
    view.y = py - (py - view.y) * (s / view.s);
    view.s = s;
    apply(animate);
  }

  function centerOn(ix, iy, scale, animate) {
    if (scale) view.s = Math.min(view.max, Math.max(view.min, scale));
    view.x = view.vw / 2 - ix * view.s;
    view.y = view.vh / 2 - iy * view.s;
    apply(animate);
  }

  function isCenteredOnUser() {
    const cx = (view.vw / 2 - view.x) / view.s;
    const cy = (view.vh / 2 - view.y) / view.s;
    return Math.hypot(cx - USER[0], cy - USER[1]) < 40 / view.s;
  }

  /* ---------------- Markers ---------------- */
  function makeMarker(cls, html, label) {
    const m = document.createElement("div");
    m.className = "marker " + cls;
    m.innerHTML = `<div class="marker__body">${html}</div>`;
    if (label) {
      m.setAttribute("role", "button");
      m.setAttribute("tabindex", "-1");
      m.setAttribute("aria-label", label);
    }
    markersEl.appendChild(m);
    return m;
  }
  function place(m, x, y) {
    m.style.setProperty("--x", x.toFixed(1) + "px");
    m.style.setProperty("--y", y.toFixed(1) + "px");
  }

  const userMarker = makeMarker(
    "marker--user",
    `<div class="user-pin"><span class="user-pin__halo"></span><span class="user-pin__pulse"></span><span class="user-pin__dot"></span></div>`
  );
  place(userMarker, USER[0], USER[1]);

  const robotSvg = `<svg viewBox="6 4 24 28" aria-hidden="true"><use href="#i-robot"/></svg>`;
  ROBOTS.forEach((r) => {
    r.segLens = [];
    r.len = 0;
    for (let i = 1; i < r.path.length; i++) {
      const l = Math.hypot(r.path[i][0] - r.path[i - 1][0], r.path[i][1] - r.path[i - 1][1]);
      r.segLens.push(l);
      r.len += l;
    }
    r.dir = 1;
    r.el = makeMarker("marker--robot" + (r.busy ? " is-busy" : ""), `<div class="robot-pin">${robotSvg}</div>`, `${r.id}${r.busy ? ", on a delivery" : ""}`);
    r.el.dataset.robot = r.id;
    position(r);
  });

  function position(r) {
    let d = r.t * r.len;
    for (let i = 0; i < r.segLens.length; i++) {
      if (d <= r.segLens[i] || i === r.segLens.length - 1) {
        const k = r.segLens[i] ? Math.min(1, d / r.segLens[i]) : 0;
        const a = r.path[i], b = r.path[i + 1];
        r.x = a[0] + (b[0] - a[0]) * k;
        r.y = a[1] + (b[1] - a[1]) * k;
        break;
      }
      d -= r.segLens[i];
    }
    place(r.el, r.x, r.y);
  }

  /* ---------------- Nearest robot + ETA ---------------- */
  let pinned = null;      // robot id chosen by tap
  let pinnedUntil = 0;
  let shownId = null;

  const etaMin = (r) => Math.max(1, Math.round(Math.hypot(r.x - USER[0], r.y - USER[1]) / PX_PER_MIN));

  function updateCallout() {
    const available = ROBOTS.filter((r) => !r.busy);
    const sorted = available.slice().sort((a, b) => etaMin(a) - etaMin(b) || a.id.localeCompare(b.id));
    const nearest = sorted[0];
    let target = nearest;
    if (pinned && performance.now() < pinnedUntil) target = ROBOTS.find((r) => r.id === pinned) || nearest;
    else pinned = null;

    ROBOTS.forEach((r) => r.el.classList.toggle("is-nearest", r === target));
    const eta = target.busy ? "On a delivery" : `${etaMin(target)} min away`;
    if (shownId !== target.id) {
      calloutEl.classList.add("is-updating");
      setTimeout(() => calloutEl.classList.remove("is-updating"), 180);
      shownId = target.id;
    }
    calloutName.textContent = target.id;
    calloutEta.textContent = eta;

    // Average pickup window across the three closest available robots (+ handoff time)
    const etas = sorted.slice(0, 3).map(etaMin);
    const lo = etas[0] + 3;
    const hi = Math.max(lo + 2, etas[etas.length - 1] + 5);
    avgEtaEl.textContent = `${lo}–${hi} min`;
  }

  /* ---------------- Animation loop ---------------- */
  let last = performance.now();
  let acc = 0;
  function tick(now) {
    const dt = Math.min(0.1, (now - last) / 1000);
    last = now;
    ROBOTS.forEach((r) => {
      r.t += (r.dir * r.speed * dt) / r.len;
      if (r.t >= 1) { r.t = 1; r.dir = -1; }
      if (r.t <= 0) { r.t = 0; r.dir = 1; }
      position(r);
    });
    acc += dt;
    if (acc > 1) { acc = 0; updateCallout(); }
    requestAnimationFrame(tick);
  }

  /* ---------------- Gestures ---------------- */
  const pointers = new Map();
  let drag = null;
  let pinch = null;
  let moved = false;

  root.addEventListener("pointerdown", (e) => {
    if (e.pointerType === "mouse" && e.button !== 0) return;
    root.setPointerCapture(e.pointerId);
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    moved = false;
    if (pointers.size === 1) {
      drag = { x: e.clientX, y: e.clientY, vx: view.x, vy: view.y };
    } else if (pointers.size === 2) {
      const [a, b] = [...pointers.values()];
      const rect = root.getBoundingClientRect();
      pinch = {
        d: Math.hypot(a.x - b.x, a.y - b.y),
        s: view.s,
        cx: (a.x + b.x) / 2 - rect.left,
        cy: (a.y + b.y) / 2 - rect.top,
        vx: view.x, vy: view.y,
      };
      drag = null;
    }
  });

  root.addEventListener("pointermove", (e) => {
    if (!pointers.has(e.pointerId)) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pinch && pointers.size >= 2) {
      const [a, b] = [...pointers.values()];
      const d = Math.hypot(a.x - b.x, a.y - b.y);
      const s = Math.min(view.max, Math.max(view.min, pinch.s * (d / pinch.d)));
      const rect = root.getBoundingClientRect();
      const cx = (a.x + b.x) / 2 - rect.left;
      const cy = (a.y + b.y) / 2 - rect.top;
      view.x = cx - (pinch.cx - pinch.vx) * (s / pinch.s);
      view.y = cy - (pinch.cy - pinch.vy) * (s / pinch.s);
      view.s = s;
      moved = true;
      apply(false);
    } else if (drag) {
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
      if (!moved && Math.hypot(dx, dy) < 4) return;
      moved = true;
      root.classList.add("is-dragging");
      view.x = drag.vx + dx;
      view.y = drag.vy + dy;
      apply(false);
    }
  });

  function endPointer(e) {
    pointers.delete(e.pointerId);
    if (pointers.size < 2) pinch = null;
    if (pointers.size === 1) {
      const p = [...pointers.values()][0];
      drag = { x: p.x, y: p.y, vx: view.x, vy: view.y };
    }
    if (pointers.size === 0) {
      drag = null;
      root.classList.remove("is-dragging");
      if (!moved) handleTap(e);
      syncLocate();
    }
  }
  root.addEventListener("pointerup", endPointer);
  root.addEventListener("pointercancel", endPointer);

  function handleTap(e) {
    const el = document.elementFromPoint(e.clientX, e.clientY);
    const robotEl = el && el.closest("[data-robot]");
    if (robotEl) selectRobot(robotEl.dataset.robot);
  }

  function selectRobot(id) {
    pinned = id;
    pinnedUntil = performance.now() + 8000;
    updateCallout();
  }

  // Plain scrolling keeps scrolling the page; trackpad pinch (ctrlKey) or ctrl/cmd + wheel zooms the map
  root.addEventListener("wheel", (e) => {
    if (!e.ctrlKey && !e.metaKey) return;
    e.preventDefault();
    const rect = root.getBoundingClientRect();
    const factor = Math.exp(-e.deltaY * 0.01);
    zoomAt(e.clientX - rect.left, e.clientY - rect.top, view.s * factor, false);
    syncLocate();
  }, { passive: false });

  root.addEventListener("dblclick", (e) => {
    const rect = root.getBoundingClientRect();
    zoomAt(e.clientX - rect.left, e.clientY - rect.top, view.s * 1.8, true);
    syncLocate();
  });

  root.addEventListener("keydown", (e) => {
    const step = 60;
    const map = { ArrowLeft: [step, 0], ArrowRight: [-step, 0], ArrowUp: [0, step], ArrowDown: [0, -step] };
    if (map[e.key]) {
      e.preventDefault();
      view.x += map[e.key][0];
      view.y += map[e.key][1];
      apply(true);
    } else if (e.key === "+" || e.key === "=") {
      zoomAt(view.vw / 2, view.vh / 2, view.s * 1.4, true);
    } else if (e.key === "-" || e.key === "_") {
      zoomAt(view.vw / 2, view.vh / 2, view.s / 1.4, true);
    } else return;
    syncLocate();
  });

  zoomInBtn.addEventListener("click", () => { zoomAt(view.vw / 2, view.vh / 2, view.s * 1.5, true); syncLocate(); });
  zoomOutBtn.addEventListener("click", () => { zoomAt(view.vw / 2, view.vh / 2, view.s / 1.5, true); syncLocate(); });
  locateBtn.addEventListener("click", () => {
    centerOn(USER[0], USER[1], Math.max(view.s, view.min * 1.6), true);
    setTimeout(syncLocate, 480);
  });

  function syncLocate() {
    const on = isCenteredOnUser();
    locateBtn.classList.toggle("is-active", on);
    locateBtn.setAttribute("aria-pressed", String(on));
  }

  /* ---------------- Init ---------------- */
  let ready = false;
  function init() {
    if (ready || !measure()) return;
    ready = true;
    centerOn(USER[0] + 120, USER[1] - 40, view.min * 1.35, false);
    syncLocate();
    updateCallout();
    if (!reduceMotion) requestAnimationFrame((t) => { last = t; tick(t); });
  }

  // Keep the same map centre when the card resizes (rotation, desktop resize)
  let ro;
  if ("ResizeObserver" in window) {
    ro = new ResizeObserver(() => {
      if (!ready) { init(); return; }
      const cx = (view.vw / 2 - view.x) / view.s;
      const cy = (view.vh / 2 - view.y) / view.s;
      const rel = view.s / view.min;
      if (!measure()) return;
      centerOn(cx, cy, view.min * rel, false);
      syncLocate();
    });
  }

  const img = layer.querySelector("img");
  const start = () => { init(); if (ro) ro.observe(root); };
  if (img.complete) start(); else { img.addEventListener("load", start, { once: true }); img.addEventListener("error", start, { once: true }); }

  window.VYNMap = { centerOnUser: () => locateBtn.click(), selectRobot };
})();
