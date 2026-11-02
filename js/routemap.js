/* VYN — route maps for flow screens.
 * Draws the campus image (object-fit: cover) with a route that follows real walkways.
 * Usage: <div class="route-map" data-route="A,B,C,D,E" data-cur="2,0.45" data-cur-glyph="package"
 *          data-dest-glyph="building" data-blocked="B,C,D" data-no-start data-live="90"></div>
 */
(function () {
  "use strict";
  const IW = 1420, IH = 1058;
  const K = 1448 / 361;
  // Walkway points traced on the 361 × 271 design export, converted to full-res image px
  const RAW = { A: [121, 95], B: [121, 138], C: [150, 151], D: [228, 152], E: [227, 98], N1: [121, 84], N2: [176, 50], N3: [214, 66], MID: [189, 151.5] };
  const P = {};
  for (const k in RAW) P[k] = [RAW[k][0] * K - 14, RAW[k][1] * K - 14];
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const ns = "http://www.w3.org/2000/svg";

  function lengths(pts) {
    const seg = [];
    let total = 0;
    for (let i = 1; i < pts.length; i++) {
      const l = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
      seg.push(l);
      total += l;
    }
    return { seg, total };
  }
  // Split a polyline at fraction t (0–1 of its length)
  function splitAt(pts, t) {
    const { seg, total } = lengths(pts);
    let d = Math.max(0, Math.min(1, t)) * total;
    for (let i = 0; i < seg.length; i++) {
      if (d <= seg[i] || i === seg.length - 1) {
        const k = seg[i] ? Math.min(1, d / seg[i]) : 0;
        const a = pts[i], b = pts[i + 1];
        const cp = [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k];
        return { before: [...pts.slice(0, i + 1), cp], after: [cp, ...pts.slice(i + 1)], point: cp };
      }
      d -= seg[i];
    }
    return { before: pts, after: [pts[pts.length - 1]], point: pts[pts.length - 1] };
  }
  function fractionOf(pts, segIndex, t) {
    const { seg, total } = lengths(pts);
    let d = 0;
    for (let i = 0; i < segIndex; i++) d += seg[i];
    d += (seg[segIndex] || 0) * t;
    return total ? d / total : 0;
  }

  function pin(cls, glyph, label) {
    const el = document.createElement("span");
    el.className = "rm-pin " + cls;
    if (label) { el.setAttribute("role", "img"); el.setAttribute("aria-label", label); } else el.setAttribute("aria-hidden", "true");
    el.innerHTML = glyph ? `<svg aria-hidden="true"><use href="#${glyph === "robot" ? "i-robot" : "g-" + glyph}"/></svg>` : "";
    return el;
  }

  function mount(root) {
    const keys = (root.dataset.route || "").split(",").map((s) => s.trim()).filter(Boolean);
    const route = keys.map((k) => P[k]);
    const blocked = root.dataset.blocked ? root.dataset.blocked.split(",").map((k) => P[k.trim()]) : null;
    let frac = 0;
    if (root.dataset.cur) {
      const [si, t] = root.dataset.cur.split(",").map(Number);
      frac = fractionOf(route, si, t);
    }
    const hasCur = !!root.dataset.cur;

    root.insertAdjacentHTML("afterbegin",
      '<picture><source srcset="assets/campus-map.webp" type="image/webp"><img class="rm-img" src="assets/campus-map.jpg" width="1420" height="1058" alt="" draggable="false"></picture>');
    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("class", "rm-svg");
    svg.setAttribute("aria-hidden", "true");
    const mk = (cls) => { const p = document.createElementNS(ns, "path"); p.setAttribute("class", cls); svg.appendChild(p); return p; };
    const blockHalo = blocked && mk("rm-halo");
    const blockLine = blocked && mk("rm-blocked");
    const remHalo = mk("rm-halo rm-halo--thin");
    const remLine = mk("rm-remaining");
    const travHalo = mk("rm-halo");
    const travLine = mk("rm-travelled");
    root.appendChild(svg);

    const start = root.hasAttribute("data-no-start") ? null : pin("rm-start");
    const dest = pin("rm-dest", root.dataset.destGlyph || "building", root.dataset.destLabel || "Destination");
    const block = blocked ? pin("rm-block", "x", "Path closed") : null;
    const curGlyph = root.dataset.curGlyph || "package";
    const cur = hasCur ? pin(curGlyph === "robot" ? "rm-robot" : "rm-cur", curGlyph, root.dataset.curLabel || "Current position") : null;
    const pulse = hasCur ? pin("rm-pulse") : null;
    [start, dest, block, pulse, cur].forEach((n) => n && root.appendChild(n));

    let s = 1, ox = 0, oy = 0;
    const toPx = (p) => [p[0] * s + ox, p[1] * s + oy];
    const d = (pts) => pts.length < 2 ? "" : "M" + pts.map((p) => toPx(p).map((v) => v.toFixed(1)).join(" ")).join(" L");
    const place = (el, p) => { if (!el) return; const [x, y] = toPx(p); el.style.left = x + "px"; el.style.top = y + "px"; };

    function draw() {
      const w = root.clientWidth, h = root.clientHeight;
      if (!w || !h) return;
      s = Math.max(w / IW, h / IH);
      ox = (w - IW * s) / 2;
      oy = (h - IH * s) / 2;
      svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
      if (blocked) { blockHalo.setAttribute("d", d(blocked)); blockLine.setAttribute("d", d(blocked)); }
      const parts = hasCur ? splitAt(route, frac) : { before: [route[0]], after: route, point: null };
      remHalo.setAttribute("d", d(parts.after));
      remLine.setAttribute("d", d(parts.after));
      travHalo.setAttribute("d", d(parts.before));
      travLine.setAttribute("d", d(parts.before));
      place(start, route[0]);
      place(dest, route[route.length - 1]);
      if (blocked) place(block, P.MID);
      if (hasCur) { place(cur, parts.point); place(pulse, parts.point); }
    }

    const api = {
      el: root,
      get progress() { return frac; },
      setProgress(f) { frac = Math.max(0, Math.min(1, f)); draw(); root.dispatchEvent(new CustomEvent("routeprogress", { detail: frac })); },
      redraw: draw,
    };

    // Live mode: move the current marker along the route over N seconds
    const live = Number(root.dataset.live || 0);
    if (live && hasCur) {
      const from = frac;
      let t0 = null;
      const step = (now) => {
        if (t0 === null) t0 = now;
        const f = from + ((now - t0) / 1000 / live) * (1 - from);
        api.setProgress(f);
        if (f < 1) requestAnimationFrame(step);
      };
      if (!reduceMotion) requestAnimationFrame(step);
    }

    const img = root.querySelector("img");
    if (img.complete) draw(); else img.addEventListener("load", draw, { once: true });
    if ("ResizeObserver" in window) new ResizeObserver(draw).observe(root); else window.addEventListener("resize", draw);
    draw();
    root.vynMap = api;
    return api;
  }

  window.VYNRouteMap = { mount };
  document.querySelectorAll(".route-map").forEach(mount);
})();
