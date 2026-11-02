"""Generate VYN flow screens (04–14) + screen index as static HTML.
Run from the repo root: python3 tools/build_pages.py .
"""
import sys, os, html

OUT = sys.argv[1]
V = "4"

def ic(name, cls="g", extra=""):
    href = "#i-robot" if name == "robot" else f"#g-{name}"
    return f'<svg class="{cls}{(" " + extra) if extra else ""}" aria-hidden="true"><use href="{href}"/></svg>'

def page(fname, title, topbar, content, action, script="", body_attrs=""):
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="theme-color" content="#f2f5fa" />
  <title>VYN — {html.escape(title)}</title>
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="css/styles.css?v={V}" />
  <link rel="stylesheet" href="css/flow.css?v={V}" />
</head>
<body class="flow"{body_attrs}>
  <div class="screen screen--flow">
    <main class="flow-content" id="main">
{topbar}
{content}
    </main>
{action}
  </div>
  <div class="toast" data-toast-el role="status" aria-live="polite"></div>
  <script src="js/icons.js?v={V}"></script>
  <script src="js/routemap.js?v={V}"></script>
  <script src="js/flow.js?v={V}"></script>
{('  <script>' + script + '</script>') if script else ''}
</body>
</html>
"""
    with open(os.path.join(OUT, fname), "w") as f:
        f.write(doc)

def topbar(title, back="index.html", trail="Help", trail_toast="Help opens a chat with campus delivery support"):
    t = f'<a class="topbar__trail" href="#" data-toast="{trail_toast}">{trail}</a>' if trail else "<span></span>"
    return f"""      <header class="topbar">
        <a class="back-btn" href="{back}" data-back aria-label="Back">{ic('arrow-left')}</a>
        <h1 class="topbar__title">{title}</h1>
        {t}
      </header>"""

def sec(title, right=""):
    return f'<div class="sec-head"><h2 class="sec-title">{title}</h2>{right}</div>'

def detail(label, value, icon, action="", bind=""):
    b = f' data-bind="{bind}"' if bind else ""
    return f"""<div class="detail"><span class="detail__tile">{ic(icon)}</span><span class="detail__text"><span class="detail__label">{label}</span><span class="detail__value"{b}>{value}</span></span>{action}</div>"""

STATUS = {"open": ("check-circle", "c-success"), "closing": ("clock", "c-warning"), "likely": ("user-check", "c-brand"), "arriving": ("package", "c-brand")}

def row(title, status, kind, lead, value=None, selected=False, extra=""):
    si, sc = STATUS[kind]
    if lead in ("building", "book-open"):
        leadhtml = f'<span class="row__lead">{ic(lead)}</span>'
    else:
        leadhtml = f'<span class="row__lead row__lead--person">{lead}</span>'
    v = value or title
    return f"""<button type="button" class="row" role="radio" aria-checked="{'true' if selected else 'false'}" data-value="{html.escape(v)}" data-status="{kind}"{extra}>
          {leadhtml}
          <span class="row__text"><span class="row__title">{title}</span><span class="row__status">{ic(si, 'g14', sc)}<span>{status}</span></span></span>
          {ic('chevron-right', 'g row__chev')}{ic('check-circle', 'g22 row__check')}
        </button>"""

def notice(tone, title, body, icon):
    return f"""<div class="notice notice--{tone}" role="note">{ic(icon)}<div class="notice__text"><p class="notice__title">{title}</p><p class="notice__body">{body}</p></div></div>"""

def chip_status(tone, label, icon, attrs=""):
    return f'<span class="status-chip status-chip--{tone}"{attrs}>{ic(icon)}<span data-chip-label>{label}</span></span>'

def option(name, value, title, desc, checked=False, badge="", cta="", href="", icon="", toast=""):
    b = f'<span class="badge">{badge}</span>' if badge else ""
    attrs = f' data-cta="{html.escape(cta)}"' if cta else ""
    attrs += f' data-href="{href}"' if href else ""
    attrs += f' data-icon="{icon}"' if icon else ""
    attrs += f' data-toast-msg="{html.escape(toast)}"' if toast else ""
    return f"""<label class="option-card"><input type="radio" name="{name}" value="{value}"{' checked' if checked else ''}{attrs} /><span class="option-card__radio" aria-hidden="true"></span><span class="option-card__text"><span class="option-card__head"><span class="option-card__title">{title}</span>{b}</span><span class="option-card__desc">{desc}</span></span></label>"""

def btn(variant, label, icon=None, href="#", attrs=""):
    i = ic(icon) if icon else ""
    return f'<a class="btn btn--{variant}" href="{href}"{attrs}>{i}<span data-label>{label}</span></a>'

def action(*parts, note="", attrs=""):
    n = f'<p class="action-bar__note">{note}</p>' if note else ""
    return f'    <div class="action-bar"{attrs}>\n      ' + "\n      ".join(parts) + f"\n      {n}\n    </div>"

def chips(values, selected, attr=""):
    return '<div class="chips" data-chips' + attr + ">" + "".join(
        f'<button type="button" class="chip" aria-pressed="{"true" if v in selected else "false"}" data-value="{html.escape(v)}">{html.escape(v)}</button>' for v in values) + "</div>"

def code(digits, label):
    return '<div class="code" role="img" aria-label="' + label + ' ' + " ".join(digits) + '">' + "".join(f'<span class="code__digit" aria-hidden="true">{d}</span>' for d in digits) + "</div>"

def steps(items, attr=""):
    return f'<ol class="steps"{attr}>' + "".join(f'<li class="step">{t}</li>' for t in items) + "</ol>"

def card(inner, cls="", attrs=""):
    return f'<section class="card {cls}"{attrs}>{inner}</section>'

def when_seg(group):
    return f"""<div class="seg" role="group" aria-label="When" data-seg data-seg-panels="{group}">
          <button type="button" class="seg__btn" aria-pressed="true" data-value="now">{ic('clock', 'g18')}Pickup now</button>
          <button type="button" class="seg__btn" aria-pressed="false" data-value="schedule">{ic('calendar', 'g18')}Schedule</button>
        </div>"""

def schedule_field(group):
    return f"""<div data-panel="{group}:schedule" hidden>
          <label class="field">{ic('calendar', 'g', 'c-muted')}<select aria-label="Pickup time"><option>Today · 2:00 PM</option><option>Today · 3:30 PM</option><option>Tomorrow · 8:00 AM</option><option>Tomorrow · 10:00 AM</option></select>{ic('chevron-down', 'g18', 'c-muted')}</label>
        </div>"""

# =====================================================================
# 04 / 05 — Send item (Person | Department)
# =====================================================================
send_content = f"""
      <div class="seg" role="tablist" aria-label="Send to" data-seg data-seg-panels="send" data-seg-hash>
        <button type="button" class="seg__btn" role="tab" aria-selected="true" data-value="person">{ic('user', 'g18')}Person</button>
        <button type="button" class="seg__btn" role="tab" aria-selected="false" data-value="department">{ic('building', 'g18')}Department</button>
      </div>

      <!-- ===== Person ===== -->
      <div class="g12" data-panel="send:person" style="gap:16px">
        <label class="field">{ic('search', 'g', 'c-muted')}<input type="search" placeholder="Search name, UID or email" aria-label="Search people" data-filter="#recent-list" /></label>
        <section class="card card--selected" style="padding:14px 16px" aria-label="Selected recipient">
          <div class="person">
            <span class="avatar-soft" data-sel-initials>MC</span>
            <span class="person__text">
              <span class="person__name" data-sel-name>Maya Chen</span>
              <span class="person__meta" data-sel-meta>UID 2024-1187 · Biology</span>
              <span class="person__avail" data-sel-avail>{ic('user-check', 'g14')}<span>Likely available now</span></span>
            </span>
            {ic('check-circle', 'g22', 'c-brand')}
          </div>
        </section>
        {sec('Recent')}
        <div class="card card--list list" id="recent-list" role="radiogroup" aria-label="Recent people" data-select-group>
        {row('Maya Chen', 'Likely available now', 'likely', 'MC', selected=True, extra=' data-meta="UID 2024-1187 · Biology"')}
        {row('Arjun Patel', 'In class until 11:50 AM', 'closing', 'AP', extra=' data-meta="UID 2023-0442 · Engineering"')}
        {row('Priya Nair', 'Likely available now', 'likely', 'PN', extra=' data-meta="UID 2022-3318 · Chemistry"')}
        {row('Daniel Okafor', 'Usually free after 2:00 PM', 'closing', 'DO', extra=' data-meta="UID 2024-0916 · Business"')}
        </div>
        {sec('When')}
        <div class="g8">
        {when_seg('pwhen')}
          <p class="hint" data-panel="pwhen:now">{ic('robot', 'g16', 'c-muted')}A robot can be at your pickup point in about 4 min.</p>
        {schedule_field('pwhen')}
        </div>
        {sec('Item details', '<span class="sec-meta">Optional</span>')}
        <section class="card" style="gap:14px">
          <p class="card__label">Type</p>
          {chips(['Documents', 'Keys & ID', 'Electronics', 'Food', 'Other'], ['Electronics'])}
          <p class="card__label">Size</p>
          {chips(['Small', 'Medium', 'Large'], ['Small'], ' data-size')}
          <p class="code-caption" data-size-hint>Small fits a laptop charger or a stack of papers (30 × 25 × 10 cm).</p>
          <label class="field field--area"><textarea rows="2" placeholder="Add a note for Maya (optional)" aria-label="Note for recipient" data-note-person></textarea></label>
        </section>
        {sec('Pickup')}
        <section class="card card--rows">
          {detail('Pickup point · your location', 'Student Union · Lobby', 'map-pin', '<a class="detail__action" href="#" data-toast="Pickup point picker is coming next">Change</a>')}
        </section>
      </div>

      <!-- ===== Department ===== -->
      <div class="g12" data-panel="send:department" hidden style="gap:16px">
        {notice('success', 'No waiting for a reply', 'Department desks accept deliveries automatically during their posted hours.', 'shield-check')}
        <label class="field">{ic('search', 'g', 'c-muted')}<input type="search" placeholder="Search departments or buildings" aria-label="Search departments" data-filter="#dept-list" /></label>
        {sec('Popular departments', '<a class="link" href="#" data-toast="Showing 4 of 38 departments">See all</a>')}
        <div class="card card--list list" id="dept-list" role="radiogroup" aria-label="Departments" data-select-group>
        {row('Registrar Office', 'Open until 5:00 PM', 'open', 'building', selected=True)}
        {row('Library Front Desk', 'Closing in 20 min', 'closing', 'book-open')}
        {row('IT Help Desk', 'Open until 6:00 PM', 'open', 'building')}
        {row('Science Hall Front Desk', 'Open until 6:00 PM', 'open', 'building')}
        </div>
        {sec('Route')}
        <section class="card card--rows">
          {detail('Pickup', 'Student Union · Lobby', 'map-pin', '<a class="detail__action" href="#" data-toast="Pickup point picker is coming next">Change</a>')}
          {detail('Drop-off · auto-filled', 'Admin Building · Registrar front desk', 'building', bind='drop')}
          {detail('Posted hours', 'Mon–Fri · 8:00 AM – 5:00 PM', 'clock', bind='hours')}
        </section>
        {sec('When')}
        <div class="g8">
        {when_seg('dwhen')}
          <p class="hint" data-dept-hint>{ic('check-circle', 'g16', 'c-success')}<span>Arrives well before the desk closes (est. 10:42 AM).</span></p>
        {schedule_field('dwhen')}
        </div>
        {sec('Item details', '<span class="sec-meta">Optional</span>')}
        <section class="card" style="gap:14px">
          {chips(['Documents', 'Keys & ID', 'Electronics', 'Other'], ['Documents'], ' data-dept-type')}
          <label class="field field--area"><textarea rows="2" placeholder="Note for the desk, e.g. “Transcript request form”" aria-label="Note for the desk" data-note-dept></textarea></label>
        </section>
      </div>"""

send_action = (
    action(btn('primary', 'Continue', None, 'ai-decision.html', ' data-continue-person'), note="You’ll review everything before the robot is sent.", attrs=' data-panel="send:person"')
    + "\n" +
    action(btn('primary', 'Review &amp; send', None, 'review.html', ' data-continue-dept'), note="The desk accepts on arrival — you can walk away once it’s loaded.", attrs=' data-panel="send:department" hidden')
)

send_script = r"""
(function(){
  const {$, $$, store} = window.VYN;
  // Search filters the list it points at
  $$('[data-filter]').forEach(inp => inp.addEventListener('input', () => {
    const q = inp.value.trim().toLowerCase();
    $$('.row', $(inp.dataset.filter)).forEach(r => { r.hidden = q && !r.textContent.toLowerCase().includes(q); });
  }));
  // Person selection updates the recipient card
  const list = $('#recent-list');
  list.addEventListener('rowselect', e => {
    const r = e.detail, name = r.dataset.value;
    $('[data-sel-name]').textContent = name;
    $('[data-sel-initials]').textContent = name.split(' ').map(p => p[0]).join('');
    $('[data-sel-meta]').textContent = r.dataset.meta;
    const avail = $('[data-sel-avail]');
    const likely = r.dataset.status === 'likely';
    avail.classList.toggle('person__avail--warn', !likely);
    avail.querySelector('use').setAttribute('href', likely ? '#g-user-check' : '#g-clock');
    avail.querySelector('span').textContent = r.querySelector('.row__status span').textContent;
    $('[data-note-person]').placeholder = `Add a note for ${name.split(' ')[0]} (optional)`;
  });
  const sizes = {Small: 'Small fits a laptop charger or a stack of papers (30 × 25 × 10 cm).', Medium: 'Medium fits a textbook or a small box (40 × 30 × 20 cm).', Large: 'Large fits a backpack or a lab kit (55 × 40 × 30 cm).'};
  $('[data-size]').addEventListener('chipchange', e => { $('[data-size-hint]').textContent = sizes[e.detail]; });
  // Department selection updates route, hours and the next step
  const DEPTS = {
    'Registrar Office': {drop: 'Admin Building · Registrar front desk', hours: 'Mon–Fri · 8:00 AM – 5:00 PM'},
    'Library Front Desk': {drop: 'Marriott Library · Front desk', hours: 'Today · closes at 5:00 PM', closing: true},
    'IT Help Desk': {drop: 'Tech Commons · IT Help Desk', hours: 'Mon–Fri · 8:00 AM – 6:00 PM'},
    'Science Hall Front Desk': {drop: 'Science Hall · Front desk', hours: 'Mon–Sat · 7:30 AM – 6:00 PM'},
  };
  let dept = 'Registrar Office';
  const hint = $('[data-dept-hint]');
  $('#dept-list').addEventListener('rowselect', e => {
    dept = e.detail.dataset.value;
    const d = DEPTS[dept];
    $('[data-bind="drop"]').textContent = d.drop;
    $('[data-bind="hours"]').textContent = d.hours;
    hint.querySelector('use').setAttribute('href', d.closing ? '#g-alert-triangle' : '#g-check-circle');
    hint.querySelector('svg').setAttribute('class', 'g16 ' + (d.closing ? 'c-warning' : 'c-success'));
    hint.querySelector('span').textContent = d.closing ? 'This desk may close before the robot arrives.' : 'Arrives well before the desk closes (est. 10:42 AM).';
    $('[data-continue-dept]').setAttribute('href', d.closing ? 'department-closing.html' : 'review.html');
  });
  const typeOf = sel => ($(sel + ' .chip[aria-pressed="true"]') || {}).textContent || '';
  $('[data-continue-dept]').addEventListener('click', () => {
    store.set('dept', {name: dept, drop: DEPTS[dept].drop, item: typeOf('[data-dept-type]') || 'Documents', note: $('[data-note-dept]').value.trim()});
  });
  $('[data-continue-person]').addEventListener('click', () => {
    store.set('person', {name: $('[data-sel-name]').textContent, initials: $('[data-sel-initials]').textContent, item: typeOf('[data-chips]:not([data-size])') || 'Electronics', size: typeOf('[data-size]') || 'Small'});
  });
})();
"""
page("send.html", "Send item", topbar("Send item"), send_content, send_action, send_script)

# =====================================================================
# 06 — Review delivery
# =====================================================================
review_content = f"""
      <section class="card" aria-label="Delivery summary">
        {chip_status('success', 'Accepted automatically', 'check-circle')}
        <div class="headline"><p class="headline__title">Arrives by 10:42 AM</p><p class="headline__sub" data-bind="to">To Registrar Office · Admin Building front desk</p></div>
        <div class="route-map" style="--ar:329/148" data-route="A,B,C,D,E" data-dest-label="Registrar Office" role="img" aria-label="Route from Student Union to the Registrar Office"></div>
        <p class="conf-note">{ic('info', 'g16')}<span>High confidence · based on current campus paths. We’ll tell you if this changes.</span></p>
      </section>
      {sec('Details', '<a class="link" href="send.html#department">Edit</a>')}
      <section class="card card--rows">
        {detail('To', 'Registrar Office · front desk', 'building', bind='dest')}
        {detail('Pickup', 'Student Union · Lobby', 'map-pin')}
        {detail('Robot ready', 'Now · in about 4 min', 'clock')}
        {detail('Item', 'Documents · Small', 'file-text', bind='item')}
        {detail('Note', '“Transcript request form”', 'pencil', bind='note')}
        {detail('Handoff', 'Desk staff verify with a pickup code', 'shield-check')}
      </section>
      {notice('info', 'You’re done once it’s loaded', 'Place the item, close the lid and walk away. We’ll confirm when the desk receives it.', 'check-circle')}"""
review_action = action(btn('primary', 'Confirm &amp; send', 'send', 'assigned.html', ' data-loading="Sending…"'), btn('ghost', 'Edit details', 'pencil', 'send.html#department'))
review_script = r"""
(function(){
  const d = window.VYN.store.get('dept', null);
  if (!d) return;
  const set = (k, v) => { const el = document.querySelector(`[data-bind="${k}"]`); if (el && v) el.textContent = v; };
  set('to', `To ${d.name} · ${d.drop.split(' · ')[0]}`);
  set('dest', `${d.name} · front desk`);
  set('item', `${d.item} · Small`);
  set('note', d.note ? `“${d.note}”` : 'No note');
})();
"""
page("review.html", "Review delivery", topbar("Review delivery", "send.html#department", trail=""), review_content, review_action, review_script)

# =====================================================================
# 07 — Robot assigned
# =====================================================================
assigned_content = f"""
      <div class="confirm-hero">
        <span class="confirm-hero__icon pop-in">{ic('check')}</span>
        <p class="confirm-hero__title">Robot assigned</p>
        <p class="confirm-hero__sub">VYN-07 is on its way to your pickup point.</p>
      </div>
      <section class="card" aria-label="Robot arrival">
        {chip_status('brand', 'Heading to you', 'navigation', ' data-assigned-chip')}
        <div class="headline"><p class="confirm-hero__title" style="text-align:left" aria-live="polite" data-eta>Arrives in 4 min</p><p class="headline__sub">At Student Union · Lobby entrance</p></div>
        <div class="route-map" style="--ar:329/140" data-route="E,D,C,B,A" data-cur="1,0.45" data-cur-glyph="robot" data-cur-label="VYN-07" data-dest-glyph="map-pin" data-dest-label="Your pickup point" data-live="75" role="img" aria-label="VYN-07 heading to Student Union lobby"></div>
      </section>
      <section class="card card--center" aria-label="Loading code">
        <p class="card__label" style="font-size:14px;line-height:20px">Your loading code</p>
        {code('4821', 'Loading code')}
        <p class="code-caption">Enter it on the robot’s lid to open the compartment.</p>
      </section>
      {sec('Get ready')}
      <section class="card">
        {steps(['Have your documents ready — they fit the small compartment.', 'Meet the robot at the Student Union lobby entrance.', 'Enter code 4821, place the item inside and close the lid.', 'That’s it. You can walk away — we’ll track it from here.'])}
      </section>
      <section class="card card--rows">
        {detail('Pickup', 'Student Union · Lobby', 'map-pin')}
        {detail('Destination', 'Registrar Office · front desk', 'building', bind='dest')}
        {detail('Item', 'Documents · Small', 'file-text', bind='item')}
      </section>"""
assigned_action = action(btn('primary', 'Track mission', 'navigation', 'tracking.html'), btn('secondary', 'Edit request', 'pencil', 'send.html#department'))
assigned_script = r"""
(function(){
  const d = window.VYN.store.get('dept', null);
  if (d) { document.querySelector('[data-bind="dest"]').textContent = `${d.name} · front desk`; document.querySelector('[data-bind="item"]').textContent = `${d.item} · Small`; }
  const map = document.querySelector('.route-map'), eta = document.querySelector('[data-eta]'), chip = document.querySelector('[data-assigned-chip]');
  let start = null, last = '';
  map.addEventListener('routeprogress', e => {
    if (start === null) start = e.detail;
    const left = (1 - e.detail) / (1 - start);
    const text = e.detail >= 1 ? 'Robot is here' : `Arrives in ${Math.max(1, Math.ceil(left * 4))} min`;
    if (text !== last) { eta.textContent = text; last = text; }
    if (e.detail >= 1) { chip.className = 'status-chip status-chip--success'; chip.querySelector('use').setAttribute('href', '#g-check-circle'); chip.querySelector('[data-chip-label]').textContent = 'At your pickup point'; }
  });
})();
"""
page("assigned.html", "Robot assigned", topbar("Request sent", "index.html", trail=""), assigned_content, assigned_action, assigned_script)

# =====================================================================
# 08 — Live tracking
# =====================================================================
tracking_content = f"""
      <div class="route-map route-map--lg" data-route="A,B,C,D,E" data-cur="2,0.45" data-live="120" data-cur-label="Your package" data-dest-label="Registrar Office" role="img" aria-label="Live route from Student Union to the Registrar Office"></div>
      <section class="card" aria-label="Delivery status">
        <div class="status-row">{chip_status('brand', 'On the way', 'navigation', ' data-track-chip')}<span class="sec-meta">Documents · Small</span></div>
        <div class="headline"><p class="headline__title" aria-live="polite" data-eta>Arrives in 6 min</p><p class="headline__sub">To Registrar Office · Admin Building front desk</p></div>
        <div class="progress" data-progress>
          <div class="progress__step is-done"><span class="progress__bar"><i></i></span><span class="progress__label">{ic('check')}Picked up</span></div>
          <div class="progress__step is-current"><span class="progress__bar"><i></i></span><span class="progress__label">{ic('check')}On the way</span></div>
          <div class="progress__step"><span class="progress__bar"><i></i></span><span class="progress__label">{ic('check')}Arriving</span></div>
          <div class="progress__step"><span class="progress__bar"><i></i></span><span class="progress__label">{ic('check')}Delivered</span></div>
        </div>
      </section>
      {sec('Updates')}
      <section class="card" style="padding:16px 16px 4px">
        <ol class="timeline" aria-label="Delivery updates">
          <li class="tl is-done"><span class="tl__time">10:31 AM</span><span class="tl__rail"><span class="tl__dot"></span><span class="tl__line"></span></span><span class="tl__body"><span class="tl__title">Picked up</span><span class="tl__sub">Student Union · Lobby</span></span></li>
          <li class="tl is-current" data-tl-now><span class="tl__time">10:33 AM</span><span class="tl__rail"><span class="tl__dot"></span><span class="tl__line"></span></span><span class="tl__body"><span class="tl__title">On the way</span><span class="tl__sub">Crossing Central Quad</span></span></li>
          <li class="tl is-todo" data-tl-end><span class="tl__time">~10:42 AM</span><span class="tl__rail"><span class="tl__dot"></span></span><span class="tl__body"><span class="tl__title">Arrives at Registrar front desk</span><span class="tl__sub">Desk staff verify with a pickup code</span></span></li>
        </ol>
      </section>
      {notice('success', 'Your part is done', 'The Registrar desk will receive it. We’ll notify you the moment it’s delivered.', 'check-circle')}"""
tracking_action = action(btn('primary', 'View delivery summary', 'check-circle', 'complete.html', ' data-summary hidden'), '<button type="button" class="btn btn--secondary" data-copy-link>' + ic('share') + '<span>Share live ETA</span></button>')
tracking_script = r"""
(function(){
  const {$, $$, toast} = window.VYN;
  const map = $('.route-map'), eta = $('[data-eta]'), chip = $('[data-track-chip]'), steps = $$('.progress__step');
  let start = null, stage = 1, last = '';
  function setStage(n) {
    if (n === stage) return; stage = n;
    steps.forEach((s, i) => { s.classList.toggle('is-done', i < n); s.classList.toggle('is-current', i === n); });
  }
  map.addEventListener('routeprogress', e => {
    const f = e.detail; if (start === null) start = f;
    const left = (1 - f) / (1 - start);
    if (f >= 1) {
      setStage(3); steps[3].classList.add('is-done');
      eta.textContent = 'Delivered';
      chip.className = 'status-chip status-chip--success'; chip.querySelector('use').setAttribute('href', '#g-check-circle'); chip.querySelector('[data-chip-label]').textContent = 'Delivered';
      const end = $('[data-tl-end]'); end.className = 'tl is-done'; end.querySelector('.tl__time').textContent = '10:41 AM'; end.querySelector('.tl__title').textContent = 'Delivered to Registrar front desk'; end.querySelector('.tl__sub').textContent = 'Verified by desk staff with code';
      $('[data-tl-now]').className = 'tl is-done';
      const b = $('[data-summary]'); b.hidden = false;
      toast('Delivered to Registrar Office');
      return;
    }
    if (f > 0.82) setStage(2);
    const text = `Arrives in ${Math.max(1, Math.ceil(left * 6))} min`;
    if (text !== last) { eta.textContent = stage === 2 ? 'Arriving now' : text; last = text; }
  });
})();
"""
page("tracking.html", "Live tracking", topbar("Live tracking"), tracking_content, tracking_action, tracking_script)

# =====================================================================
# 09 — Secure handoff
# =====================================================================
handoff_content = f"""
      <section class="card" aria-label="Delivery arrived">
        {chip_status('success', 'Arrived', 'check-circle')}
        <div class="headline"><p class="headline__title">Your delivery is here</p><p class="headline__sub">Waiting at Science Hall · Main entrance</p></div>
        <div class="route-map" style="--ar:329/120" data-route="C,D,E" data-no-start data-dest-glyph="package" data-dest-label="Robot with your package" role="img" aria-label="Robot waiting at Science Hall main entrance"></div>
        <div class="hold" data-countdown-wrap>
          {ic('timer', 'g18')}
          <div class="hold__text"><p class="hold__title" data-expired-title="Moved to Science Hall front desk">Held for you for <span data-countdown="292">4:52</span> more</p><p class="hold__sub">After that it goes safely to the Science Hall front desk.</p></div>
        </div>
      </section>
      <section class="card card--center" aria-label="Verify pickup">
        <p class="card__label" style="font-size:14px;line-height:20px">Your pickup code</p>
        {code('7305', 'Pickup code')}
        <p class="code-caption">Enter it on the robot’s keypad, or scan the QR code on the lid.</p>
        {btn('tonal', 'Scan QR on robot', 'scan', '#', ' data-toast="Point your camera at the QR code on the robot’s lid"')}
      </section>
      <div data-opened hidden>{notice('success', 'Compartment open', 'Take your lab notebook and close the lid to finish the handoff.', 'lock-open')}</div>
      {sec('Package')}
      <section class="card card--rows">
        {detail('From', 'Maya Chen', 'user')}
        {detail('Item', 'Lab notebook · Small', 'package')}
        {detail('Handoff point', 'Science Hall · Main entrance', 'map-pin')}
      </section>
      {sec('How to collect')}
      <section class="card">
        {steps(['Find VYN-07 by the main entrance — its light ring glows blue.', 'Unlock with your code, the QR scan, or the button below.', 'Take your item and close the lid. That confirms the handoff.'], ' data-collect')}
      </section>"""
handoff_action = action(btn('primary', 'Unlock compartment', 'lock-open', '#', ' data-unlock'), btn('ghost', 'I can’t find the robot', 'help-circle', '#', ' data-toast="VYN-07 is flashing its lights and chiming now"'))
handoff_script = r"""
(function(){
  const {$, $$, toast} = window.VYN;
  const b = $('[data-unlock]'), label = $('[data-label]', b), use = $('use', b);
  let state = 'locked';
  b.addEventListener('click', e => {
    e.preventDefault();
    if (state === 'locked') {
      state = 'busy'; b.classList.add('is-loading'); use.setAttribute('href', '#g-loader'); label.textContent = 'Unlocking…';
      setTimeout(() => {
        state = 'open'; b.classList.remove('is-loading'); use.setAttribute('href', '#g-check'); label.textContent = 'I’ve taken my item';
        $('[data-opened]').hidden = false;
        const s = $$('[data-collect] .step'); s[0].classList.add('is-done'); s[1].classList.add('is-done');
        toast('Compartment unlocked');
      }, 1000);
    } else if (state === 'open') {
      state = 'done'; toast('Handoff confirmed · Maya has been notified');
      setTimeout(() => { location.href = 'index.html'; }, 1200);
    }
  });
})();
"""
page("handoff.html", "Pick up delivery", topbar("Pick up delivery"), handoff_content, handoff_action, handoff_script)

# =====================================================================
# 10 — Delivery complete
# =====================================================================
complete_content = f"""
      <div class="confirm-hero" style="padding-top:12px">
        <span class="confirm-hero__icon confirm-hero__icon--lg pop-in">{ic('check')}</span>
        <p class="confirm-hero__title">Delivered</p>
        <p class="confirm-hero__sub">Registrar Office received your documents at 10:41 AM.</p>
      </div>
      <section class="card card--rows" aria-label="Delivery summary">
        {detail('Item', 'Documents · Small', 'file-text')}
        {detail('Delivered to', 'Registrar Office · front desk', 'building')}
        {detail('Delivered at', '10:41 AM · 1 min earlier than estimated', 'clock')}
        {detail('Received by', 'Front desk staff · verified with code', 'shield-check')}
      </section>
      <section class="card" style="gap:14px" aria-label="Feedback">
        <div class="g8" style="gap:2px"><h2 class="sec-title">How did it go?</h2><p class="sec-meta">Optional · helps us improve campus delivery</p></div>
        <div class="stars" role="radiogroup" aria-label="Rating" data-stars="4">
          {''.join(f'<button type="button" class="star-btn" role="radio" aria-label="{n} star{"s" if n > 1 else ""}">{ic("star")}</button>' for n in range(1, 6))}
        </div>
        <p class="sec-meta" style="text-align:center" data-stars-out aria-live="polite"></p>
        <div class="chips" data-multi>
          {''.join(f'<button type="button" class="chip" aria-pressed="{"true" if s else "false"}">{t}</button>' for t, s in [('On time', True), ('Easy handoff', True), ('Clear updates', False), ('Something went wrong', False)])}
        </div>
      </section>"""
complete_action = action(btn('primary', 'Send another item', 'send', 'send.html#department'), btn('secondary', 'View delivery history', 'clock', '#', ' data-toast="Delivery history is coming next"'))
complete_script = r"""
document.querySelectorAll('[data-multi] .chip').forEach(c => c.addEventListener('click', () => c.setAttribute('aria-pressed', String(c.getAttribute('aria-pressed') !== 'true'))));
"""
page("complete.html", "Delivery complete", topbar("Delivery complete", "index.html", trail=""), complete_content, complete_action, complete_script)

# =====================================================================
# 11 — Receiver unavailable
# =====================================================================
unavail_content = f"""
      {notice('warning', 'Maya hasn’t responded yet', 'The robot has waited 5 min at Science Hall. Your laptop charger is still locked inside.', 'alert-triangle')}
      <section class="card card--rows" aria-label="Current state">
        {detail('Robot is at', 'Science Hall · Main entrance', 'map-pin')}
        {detail('Your item', 'Locked and secure in the compartment', 'shield-check')}
      </section>
      {sec('Recommended next step')}
      <div class="g8" role="radiogroup" aria-label="What should happen next">
        {option('next', 'desk', 'Leave it at Science Hall front desk', 'Approved desk in Maya’s building · open until 6:00 PM. Arrives in 3 min, and Maya gets a pickup code.', True, 'Recommended', 'Send to front desk', 'tracking.html', 'building', 'Sent to Science Hall front desk · Maya gets a pickup code')}
        <p class="why">{ic('info', 'g16')}<span>Why this? It’s the closest approved desk on the robot’s current route, so the item stays secure and Maya can collect it any time today.</span></p>
      </div>
      {sec('Other options')}
      <div class="g8">
        {option('next', 'retry', 'Try Maya again', 'We’ll notify her once more and wait up to 5 more minutes.', cta='Notify Maya again', href='#', icon='bell', toast='Maya notified · waiting up to 5 more min')}
        {option('next', 'later', 'Reschedule', 'Pick a new delivery window. The item is held at the nearest desk until then.', cta='Choose a new time', href='send.html#person', icon='calendar')}
        {option('next', 'return', 'Return it to me', 'Back to Student Union · Lobby in about 9 min.', cta='Return it to me', href='tracking.html', icon='undo', toast='Returning to Student Union · Lobby')}
      </div>"""
unavail_action = action(btn('primary', 'Send to front desk', 'building', 'tracking.html', ' data-cta-for="next" data-loading="Updating…"'), btn('ghost', 'Contact support', 'message', '#', ' data-toast="Support usually replies within 2 min"'))
page("receiver-unavailable.html", "Delivery update", topbar("Delivery update"), unavail_content, unavail_action)

# =====================================================================
# 12 — Department closing
# =====================================================================
closing_content = f"""
      <div class="card card--list list" aria-label="Selected department">
        <a class="row" href="send.html#department"><span class="row__lead">{ic('book-open')}</span><span class="row__text"><span class="row__title">Library Front Desk</span><span class="row__status">{ic('clock', 'g14', 'c-warning')}<span>Closes at 5:00 PM · in 12 min</span></span></span>{ic('chevron-right', 'g row__chev')}</a>
      </div>
      {notice('warning', 'This desk closes before the robot arrives', 'We’ve paused this request so your item isn’t left without anyone to receive it.', 'alert-triangle')}
      <section class="card card--rows" aria-label="Timing">
        <div class="timing">{ic('clock', 'g18', 'c-muted')}<span class="timing__label">Now</span><span class="timing__value">4:48 PM</span></div>
        <div class="timing">{ic('building', 'g18', 'c-warning')}<span class="timing__label">Desk closes</span><span class="timing__value c-warning">5:00 PM</span></div>
        <div class="timing">{ic('alert-triangle', 'g18', 'c-critical')}<span class="timing__label">Robot would arrive</span><span class="timing__value c-critical">5:06 PM</span></div>
      </section>
      {sec('Choose what to do')}
      <div class="g8" role="radiogroup" aria-label="Choose what to do">
        {option('plan', 'schedule', 'Schedule for the next open window', 'Tomorrow · 8:00 AM. A robot collects from you at 7:45 AM, and we’ll remind you the night before.', True, 'Recommended', 'Schedule for 8:00 AM', 'index.html', 'calendar', 'Scheduled for tomorrow · 8:00 AM')}
        {option('plan', 'library', 'Send to Main Library · Circulation', 'Open until 10:00 PM · same building · arrives 4:57 PM.', cta='Send to Main Library', href='review.html', icon='send')}
        {option('plan', 'person', 'Send to a person instead', 'Choose someone who can receive it right now.', cta='Choose a person', href='send.html#person', icon='user')}
      </div>
      <p class="why">{ic('info', 'g16')}<span>Why can’t I send now? Departments only accept during posted hours. Sending anyway would leave your item locked in a robot after closing.</span></p>"""
closing_action = action(btn('primary', 'Schedule for 8:00 AM', 'calendar', 'index.html', ' data-cta-for="plan" data-loading="Saving…"'), btn('secondary', 'Choose another department', 'building', 'send.html#department'))
page("department-closing.html", "Department closing", topbar("Send item", "send.html#department"), closing_content, closing_action)

# =====================================================================
# 13 — Robot delayed
# =====================================================================
delayed_content = f"""
      <section class="card" aria-label="Delivery status">
        <div class="status-row">{chip_status('warning', 'Delayed', 'clock')}<span class="sec-meta">Documents · Small</span></div>
        <div class="headline"><p class="headline__title">Now arriving in 14 min</p><p class="headline__sub">Was 6 min · new estimate 10:56 AM at Registrar front desk</p></div>
        <div class="route-map" style="--ar:329/170" data-route="A,N1,N2,N3,E" data-cur="1,0.3" data-blocked="B,C,D" data-cur-label="Your package" data-dest-label="Registrar Office" role="img" aria-label="New route around a closed path near Engineering Quad"></div>
        <div class="legend"><span><i></i>New route</span><span><i class="is-closed"></i>Path closed</span></div>
      </section>
      {notice('success', 'Your item is secure', 'The compartment stays locked. Only the desk’s pickup code can open it.', 'shield-check')}
      {sec('Why it happened')}
      <section class="card" style="gap:8px">
        <p style="font-size:14px;line-height:20px">A maintenance barrier is blocking the path near Engineering Quad, so the robot is taking a longer, safe route.</p>
        <p class="sec-meta">Detected at 10:36 AM · reroute approved by the operations team</p>
      </section>
      {sec('What you can do')}
      <div class="g8" role="radiogroup" aria-label="What you can do">
        {option('delay', 'keep', 'Keep this delivery', 'Still arrives well before the desk closes. No action needed from you.', True, 'Recommended', 'Keep this delivery', 'tracking.html', 'check')}
        {option('delay', 'reassign', 'Reassign handoff', 'Deliver to Engineering front desk instead · arrives in 5 min.', cta='Reassign handoff', href='review.html', icon='route')}
        {option('delay', 'return', 'Return package to me', 'Back to Student Union · Lobby in about 8 min.', cta='Return package to me', href='tracking.html', icon='undo', toast='Returning to Student Union · Lobby')}
      </div>"""
delayed_action = action(btn('primary', 'Keep this delivery', 'check', 'tracking.html', ' data-cta-for="delay" data-loading="Updating…"'), btn('ghost', 'Contact support', 'message', '#', ' data-toast="Support usually replies within 2 min"'))
page("delayed.html", "Delivery delayed", topbar("Delivery update"), delayed_content, delayed_action)

# =====================================================================
# 14 — AI-assisted delivery decision
# =====================================================================
ai_content = f"""
      <section class="card" style="padding:14px 16px" aria-label="Recipient">
        <div class="person">
          <span class="avatar-soft" data-bind="initials">MC</span>
          <span class="person__text"><span class="person__name" data-bind="to">To Maya Chen</span><span class="person__meta" data-bind="item">Laptop charger · Small · Pickup now</span></span>
          <a class="detail__action" href="send.html#person">Change</a>
        </div>
      </section>
      <section class="ai-card" aria-label="Availability suggestion">
        <div class="ai-card__head"><span class="ai-card__icon">{ic('sparkles', 'g18')}</span><p class="ai-card__title" data-bind="ai-title">Maya may not be free when it arrives</p></div>
        <p class="ai-card__body" data-bind="ai-body">She’s usually in class on Tuesdays until 11:50 AM. The robot would reach Science Hall at 10:42 AM.</p>
        <div class="ai-card__conf">{chip_status('onsoft', 'Medium confidence', 'info')}<span>From her shared class schedule + 6 past deliveries</span></div>
        <p class="ai-card__fine">Signals stay coarse and campus-only. We never show anyone’s exact location.</p>
      </section>
      {sec('Choose how to send')}
      <div class="g8" role="radiogroup" aria-label="Choose how to send">
        {option('dest', 'desk', 'Science Hall front desk', 'Maya’s building · open until 6:00 PM. She gets a pickup code and can collect any time today. Arrives 10:44 AM.', True, 'Suggested', 'Confirm & send to front desk', 'assigned.html', 'send')}
        {option('dest', 'office', 'Biology Department office', 'Floor 2, Science Hall · open until 5:00 PM · arrives 10:46 AM.', cta='Confirm & send to Biology office', href='assigned.html', icon='send')}
        {option('dest', 'anyway', 'Send to Maya anyway', 'The robot waits up to 5 min. If she doesn’t come, it goes to the front desk.', cta='Send to Maya anyway', href='assigned.html', icon='send')}
      </div>
      <p class="why">{ic('user', 'g16')}<span>You decide — VYN only suggests. Nothing is sent until you confirm.</span></p>"""
ai_action = action(btn('primary', 'Confirm &amp; send to front desk', 'send', 'assigned.html', ' data-cta-for="dest" data-loading="Sending…"'), btn('ghost', 'Choose a different recipient', 'user', 'send.html#person'))
ai_script = r"""
(function(){
  const p = window.VYN.store.get('person', null);
  if (!p || p.name === 'Maya Chen') return;
  const first = p.name.split(' ')[0];
  const set = (k, v) => { const el = document.querySelector(`[data-bind="${k}"]`); if (el) el.textContent = v; };
  set('initials', p.initials); set('to', `To ${p.name}`); set('item', `${p.item} · ${p.size} · Pickup now`);
  set('ai-title', `${first} may not be free when it arrives`);
  set('ai-body', `${first} is often away from their building at this time. The robot would arrive at 10:42 AM.`);
  document.querySelectorAll('.option-card__title, .option-card__desc').forEach(el => { el.textContent = el.textContent.replace(/Maya’s/g, `${first}’s`).replace(/Maya/g, first).replace(/She gets/g, 'They get').replace(/she doesn’t/g, 'they don’t'); });
  document.querySelector('[data-cta-for] [data-label]').textContent = document.querySelector('input[name="dest"]:checked').dataset.cta;
  document.querySelectorAll('input[name="dest"]').forEach(i => { if (i.dataset.cta) i.dataset.cta = i.dataset.cta.replace('Maya', first); });
})();
"""
page("ai-decision.html", "Review delivery", topbar("Review delivery", "send.html#person", trail=""), ai_content, ai_action, ai_script)

# =====================================================================
# Screen index (linked from the More tab)
# =====================================================================
def link(num, title, sub, href):
    return f'<a class="screen-link" href="{href}"><span class="screen-link__num">{num}</span><span class="row__text"><span class="row__title">{title}</span><span class="row__status"><span>{sub}</span></span></span>{ic("chevron-right", "g row__chev")}</a>'
groups = [
    ("Sending", [("01", "Home", "Live campus map and services", "index.html"), ("04", "Send item — Person", "Pick a recipient and item", "send.html#person"), ("05", "Send item — Department", "Desks accept automatically", "send.html#department"), ("06", "Review delivery", "Confirm before the robot is sent", "review.html"), ("07", "Robot assigned", "Loading code and get-ready steps", "assigned.html"), ("08", "Live tracking", "Watch the delivery arrive", "tracking.html"), ("10", "Delivery complete", "Summary and rating", "complete.html")]),
    ("Receiving", [("09", "Secure handoff", "Unlock with your pickup code", "handoff.html")]),
    ("When plans change", [("11", "Receiver unavailable", "Recommended desk fallback", "receiver-unavailable.html"), ("12", "Department closing", "Schedule the next open window", "department-closing.html"), ("13", "Robot delayed", "Detour around a closed path", "delayed.html"), ("14", "AI-assisted decision", "A suggestion you can override", "ai-decision.html")]),
]
gal = "".join(f'<section class="gallery-group"><h2>{g}</h2><div class="card card--list list">' + "".join(link(*s) for s in items) + "</div></section>" for g, items in groups)
page("screens.html", "All screens", topbar("All screens", "index.html", trail=""), "      " + gal, "")
print("ok")
