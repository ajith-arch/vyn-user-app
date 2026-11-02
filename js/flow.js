/* VYN — shared behaviour for flow screens (04–14) */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  /* ---------------- Session state (carries choices between screens) ---------------- */
  const store = {
    get(k, d) { try { const v = sessionStorage.getItem("vyn." + k); return v === null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { sessionStorage.setItem("vyn." + k, JSON.stringify(v)); } catch (_) {} },
  };

  /* ---------------- Toast ---------------- */
  let toastEl = $("[data-toast-el]");
  if (!toastEl) {
    toastEl = document.createElement("div");
    toastEl.className = "toast";
    toastEl.setAttribute("role", "status");
    toastEl.setAttribute("aria-live", "polite");
    toastEl.dataset.toastEl = "";
    document.body.appendChild(toastEl);
  }
  let toastTimer;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("is-visible"), 2400);
  }
  $$("[data-toast]").forEach((el) => el.addEventListener("click", (e) => { e.preventDefault(); toast(el.dataset.toast); }));

  /* ---------------- Back: return to the previous VYN screen when there is one ---------------- */
  $$("[data-back]").forEach((el) => el.addEventListener("click", (e) => {
    const sameOrigin = document.referrer && new URL(document.referrer).origin === location.origin;
    if (sameOrigin && history.length > 1) { e.preventDefault(); history.back(); }
  }));

  /* ---------------- Segmented controls (optionally switching panels) ---------------- */
  $$("[data-seg]").forEach((seg) => {
    const btns = $$("[data-value]", seg);
    const panelsFor = seg.dataset.segPanels;
    function select(value, fromHash) {
      btns.forEach((b) => b.setAttribute(seg.getAttribute("role") === "tablist" ? "aria-selected" : "aria-pressed", String(b.dataset.value === value)));
      if (panelsFor) {
        $$(`[data-panel^="${panelsFor}:"]`).forEach((p) => { p.hidden = p.dataset.panel !== `${panelsFor}:${value}`; });
        if (!fromHash && seg.hasAttribute("data-seg-hash")) history.replaceState(null, "", "#" + value);
      }
      seg.dispatchEvent(new CustomEvent("segchange", { detail: value, bubbles: true }));
    }
    btns.forEach((b) => b.addEventListener("click", () => select(b.dataset.value)));
    if (seg.hasAttribute("data-seg-hash")) {
      const h = location.hash.slice(1);
      if (btns.some((b) => b.dataset.value === h)) select(h, true);
      window.addEventListener("hashchange", () => { const v = location.hash.slice(1); if (btns.some((b) => b.dataset.value === v)) select(v, true); });
    }
    seg.vynSelect = select;
  });

  /* ---------------- Chips: single choice per group ---------------- */
  $$("[data-chips]").forEach((group) => {
    $$(".chip", group).forEach((chip) => chip.addEventListener("click", () => {
      $$(".chip", group).forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
      group.dispatchEvent(new CustomEvent("chipchange", { detail: chip.dataset.value || chip.textContent.trim(), bubbles: true }));
    }));
  });

  /* ---------------- Selectable list rows ---------------- */
  $$("[data-select-group]").forEach((group) => {
    $$(".row", group).forEach((row) => row.addEventListener("click", () => {
      $$(".row", group).forEach((r) => r.setAttribute("aria-checked", String(r === row)));
      group.dispatchEvent(new CustomEvent("rowselect", { detail: row, bubbles: true }));
    }));
  });

  /* ---------------- Option cards drive the primary button ---------------- */
  $$("[data-cta-for]").forEach((cta) => {
    const name = cta.dataset.ctaFor;
    const label = $("[data-label]", cta) || cta;
    function sync() {
      const checked = $(`input[name="${name}"]:checked`);
      if (!checked) return;
      if (checked.dataset.cta) label.textContent = checked.dataset.cta;
      if (checked.dataset.href) cta.setAttribute("href", checked.dataset.href);
      if (checked.dataset.icon) { const u = $("use", cta); if (u) u.setAttribute("href", "#g-" + checked.dataset.icon); }
      if (checked.dataset.toastMsg) cta.dataset.doneToast = checked.dataset.toastMsg; else delete cta.dataset.doneToast;
    }
    $$(`input[name="${name}"]`).forEach((i) => i.addEventListener("change", sync));
    sync();
  });

  /* ---------------- Buttons that show progress, then continue ---------------- */
  $$("[data-loading]").forEach((btn) => btn.addEventListener("click", (e) => {
    if (btn.classList.contains("is-loading")) return;
    e.preventDefault();
    const href = btn.getAttribute("href");
    const label = $("[data-label]", btn) || btn;
    const use = $("use", btn);
    const prevIcon = use && use.getAttribute("href");
    const prevText = label.textContent;
    btn.classList.add("is-loading");
    btn.setAttribute("aria-busy", "true");
    if (use) use.setAttribute("href", "#g-loader");
    label.textContent = btn.dataset.loading;
    setTimeout(() => {
      if (btn.dataset.doneToast) {
        toast(btn.dataset.doneToast);
        btn.classList.remove("is-loading");
        btn.removeAttribute("aria-busy");
        if (use) use.setAttribute("href", prevIcon);
        label.textContent = prevText;
        if (!href || href === "#") return;
        setTimeout(() => { location.href = href; }, 900);
        return;
      }
      if (href && href !== "#") location.href = href;
    }, Number(btn.dataset.loadingMs || 900));
  }));

  /* ---------------- Countdown (m:ss) ---------------- */
  $$("[data-countdown]").forEach((el) => {
    let left = Number(el.dataset.countdown);
    const wrap = el.closest("[data-countdown-wrap]");
    const fmt = (n) => `${Math.floor(n / 60)}:${String(n % 60).padStart(2, "0")}`;
    el.textContent = fmt(left);
    const t = setInterval(() => {
      left -= 1;
      if (left <= 0) {
        clearInterval(t);
        if (wrap) {
          wrap.classList.add("is-expired");
          const title = $("[data-expired-title]", wrap);
          if (title) title.textContent = title.dataset.expiredTitle;
        }
        return;
      }
      el.textContent = fmt(left);
    }, 1000);
  });

  /* ---------------- Star rating ---------------- */
  $$("[data-stars]").forEach((group) => {
    const stars = $$(".star-btn", group);
    const out = $("[data-stars-out]");
    const words = ["", "Poor", "Fair", "Good", "Great", "Excellent"];
    function set(n) {
      stars.forEach((s, i) => { s.classList.toggle("is-on", i < n); s.setAttribute("aria-checked", String(i === n - 1)); });
      if (out) out.textContent = n ? `${words[n]} · thanks for rating` : "Tap a star to rate";
    }
    stars.forEach((s, i) => s.addEventListener("click", () => set(i + 1)));
    set(Number(group.dataset.stars || 0));
  });

  /* ---------------- Copy current tracking link ---------------- */
  $$("[data-copy-link]").forEach((btn) => btn.addEventListener("click", async () => {
    const url = location.href.split("#")[0];
    try { await navigator.clipboard.writeText(url); toast("Tracking link copied"); }
    catch (_) { toast("Copy this link: " + url); }
  }));

  window.VYN = { toast, store, $, $$ };
})();
