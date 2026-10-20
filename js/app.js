/* VYN — Home screen interactions: navigation, sheets, campus switching, toasts */
(function () {
  "use strict";

  /* ---------------- Toast ---------------- */
  const toastEl = document.querySelector("[data-toast-el]");
  let toastTimer;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("is-visible"), 2200);
  }

  // Screens other than Home are designed but not built yet — acknowledge the tap.
  document.querySelectorAll("[data-toast]").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      toast(el.dataset.toast);
    });
  });

  /* ---------------- Bottom navigation ---------------- */
  const TAB_LABELS = { deliveries: "Deliveries", campus: "Campus map", more: "More" };
  document.querySelectorAll("[data-nav] .nav-item").forEach((item) => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const tab = item.dataset.tab;
      if (tab === "campus" && window.VYNMap) {
        window.VYNMap.centerOnUser();
        document.querySelector(".map-card").scrollIntoView({ behavior: "smooth", block: "center" });
      }
      if (tab !== "home" && tab !== "campus") {
        toast(`${TAB_LABELS[tab]} is coming next`);
        return;
      }
      document.querySelectorAll(".nav-item").forEach((n) => {
        const on = n.dataset.tab === tab;
        n.classList.toggle("is-active", on);
        if (on) n.setAttribute("aria-current", "page"); else n.removeAttribute("aria-current");
      });
      if (tab === "home") window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });

  /* ---------------- Sheets ---------------- */
  const backdrop = document.querySelector("[data-sheet-backdrop]");
  let openSheet = null;
  let lastFocus = null;

  function focusables(el) {
    return [...el.querySelectorAll('button, [href], [tabindex]:not([tabindex="-1"])')].filter((n) => !n.disabled);
  }

  function open(name) {
    const sheet = document.querySelector(`[data-sheet="${name}"]`);
    if (!sheet) return;
    lastFocus = document.activeElement;
    openSheet = sheet;
    backdrop.hidden = false;
    sheet.hidden = false;
    requestAnimationFrame(() => {
      backdrop.classList.add("is-open");
      sheet.classList.add("is-open");
    });
    const first = sheet.querySelector('[aria-checked="true"]') || focusables(sheet)[0];
    setTimeout(() => first && first.focus(), 60);
    document.body.style.overflow = "hidden";
  }

  function close() {
    if (!openSheet) return;
    const sheet = openSheet;
    openSheet = null;
    sheet.classList.remove("is-open");
    backdrop.classList.remove("is-open");
    setTimeout(() => { sheet.hidden = true; backdrop.hidden = true; }, 320);
    document.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }

  document.querySelectorAll("[data-open-sheet]").forEach((btn) =>
    btn.addEventListener("click", () => open(btn.dataset.openSheet))
  );
  document.querySelectorAll("[data-close-sheet]").forEach((btn) => btn.addEventListener("click", close));
  backdrop.addEventListener("click", close);

  document.addEventListener("keydown", (e) => {
    if (!openSheet) return;
    if (e.key === "Escape") { e.preventDefault(); close(); return; }
    if (e.key === "Tab") {
      const f = focusables(openSheet);
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  /* ---------------- Campus selector ---------------- */
  const nameEl = document.querySelector("[data-campus-name]");
  const countEl = document.querySelector("[data-available-count]");
  const selectBtn = document.querySelector(".campus-select");
  const options = document.querySelectorAll("[data-campus]");

  options.forEach((opt) => {
    opt.addEventListener("click", () => {
      options.forEach((o) => o.setAttribute("aria-checked", String(o === opt)));
      nameEl.textContent = opt.dataset.campus;
      countEl.textContent = opt.dataset.robots;
      selectBtn.setAttribute("aria-label", `Change campus. Current campus: ${opt.dataset.campus}`);
      try { localStorage.setItem("vyn.campus", opt.dataset.campus); } catch (_) {}
      close();
      toast(`Switched to ${opt.dataset.campus}`);
    });
  });

  // Arrow-key navigation inside the radio group
  const group = document.querySelector("[data-campus-list]");
  group.addEventListener("keydown", (e) => {
    if (e.key !== "ArrowDown" && e.key !== "ArrowUp") return;
    e.preventDefault();
    const list = [...options];
    const i = list.indexOf(document.activeElement);
    const next = list[(i + (e.key === "ArrowDown" ? 1 : -1) + list.length) % list.length];
    next.focus();
  });

  try {
    const saved = localStorage.getItem("vyn.campus");
    const match = saved && [...options].find((o) => o.dataset.campus === saved);
    if (match) {
      options.forEach((o) => o.setAttribute("aria-checked", String(o === match)));
      nameEl.textContent = match.dataset.campus;
      countEl.textContent = match.dataset.robots;
    }
  } catch (_) {}

  /* ---------------- Notifications ---------------- */
  const avatar = document.querySelector(".avatar");
  avatar.addEventListener("click", () => {
    avatar.classList.add("is-read");
    avatar.setAttribute("aria-label", "Account and notifications");
  });
})();
