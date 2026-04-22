const $ = (id) => document.getElementById(id);

const summaryGrid = $("research-summary-grid");
const statusStrip = $("research-status-strip");
const downloadsEl = $("research-downloads");
const sourceGroupsEl = $("research-source-groups");
const readCountEl = $("research-read-count");
const searchInput = $("research-search");
const familyFiltersEl = $("research-family-filters");
const readListEl = $("research-read-list");
const detailEyebrowEl = $("research-detail-eyebrow");
const detailTitleEl = $("research-detail-title");
const detailStatusEl = $("research-detail-status");
const detailConfidenceEl = $("research-detail-confidence");
const detailMetaEl = $("research-detail-meta");
const detailSummaryEl = $("research-detail-summary");
const detailImplicationEl = $("research-detail-implication");
const factGridEl = $("research-fact-grid");
const evidenceListEl = $("research-evidence-list");
const mandateListEl = $("research-mandate-list");
const briefingListEl = $("research-briefing-list");
const profileFocusEl = $("research-profile-focus");
const reviewQueueEl = $("research-review-queue");

const state = {
  payload: null,
  selectedId: null,
  search: "",
  family: "All",
};

function currentSearchFromLocation() {
  const params = new URLSearchParams(window.location.search);
  return params.get("q") || "";
}

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function tone(status) {
  const key = String(status || "").toLowerCase().replaceAll(" ", "_");
  return ({
    verified: "ok",
    derived: "partial",
    conflicted: "watch",
    missing: "blocked",
    needsreview: "watch",
    needs_review: "watch",
    pending: "watch",
    ok: "ok",
    watch: "watch",
    high: "ok",
    medium: "partial",
    low: "watch",
  })[key] || "watch";
}

function statusLabel(status) {
  const key = String(status || "").toLowerCase().replaceAll(" ", "_");
  return ({
    needsreview: "Needs review",
    needs_review: "Needs review",
    verified: "Verified",
    derived: "Derived",
    conflicted: "Conflicted",
    missing: "Missing",
    pending: "Pending review",
  })[key] || String(status || "Review");
}

function relDate(value) {
  if (!value) return "No date";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toISOString().slice(0, 10);
}

function renderTicker(payload) {
  const track = $("ticker-tape");
  if (!track) return;
  const summary = payload.summary || {};
  const items = [
    { label: "VIP briefings", value: summary.current_reads || 0, delta: "ready" },
    { label: "Official sources", value: summary.official_sources || 0, delta: "watched" },
    { label: "Mandates", value: summary.mandate_sources || 0, delta: "official" },
    { label: "Profiles in focus", value: summary.profiles_in_focus || 0, delta: "loaded" },
  ];
  const markup = items
    .map(
      (item) => `
        <span class="ticker-item">
          <span class="t-name">${esc(item.label)}</span>
          <span class="t-val">${esc(String(item.value))}</span>
          <span class="t-val">${esc(item.delta)}</span>
          <span class="t-sep">│</span>
        </span>
      `,
    )
    .join("");
  track.innerHTML = markup + markup;
}

function renderSummary(payload) {
  const cards = payload.metric_cards || [];
  summaryGrid.innerHTML = cards
    .map(
      (card) => `
        <article class="metric-card">
          <span class="metric-label">${esc(card.label)}</span>
          <strong>${esc(String(card.value))}</strong>
          <p>${esc(card.note || "")}</p>
        </article>
      `,
    )
    .join("");

  statusStrip.innerHTML = (payload.status_strip || [])
    .map(
      (item) => `
        <article class="status-pill tone-${tone(item.status)}">
          <strong>${esc(item.label)}</strong>
          <span>${esc(item.note || "")}</span>
        </article>
      `,
    )
    .join("");

  downloadsEl.innerHTML = (payload.downloads || [])
    .map((item) => `<a class="nav-cta mini-cta" href="${esc(item.url || "#")}">${esc(item.label || "Download")}</a>`)
    .join("");

  sourceGroupsEl.innerHTML = (payload.source_groups || [])
    .map(
      (group) => `
        <article class="stack-card tone-${group.high_priority ? "ok" : "watch"}">
          <div class="readiness-head">
            <strong>${esc(group.family || "Official sources")}</strong>
            <span class="status-chip tone-${group.high_priority ? "ok" : "watch"}">${esc(`${group.high_priority || 0} high`)}</span>
          </div>
          <p>${esc(`${group.count || 0} official sources currently in scope.`)}</p>
        </article>
      `,
    )
    .join("");
}

function currentFamilies() {
  const values = new Set(["All"]);
  (state.payload?.current_reads || []).forEach((item) => {
    if (item.family) values.add(item.family);
  });
  return [...values];
}

function filteredReads() {
  const query = state.search.trim().toLowerCase();
  return (state.payload?.current_reads || []).filter((item) => {
    if (state.family !== "All" && item.family !== state.family) return false;
    if (!query) return true;
    const haystack = [item.title, item.family, item.entity_type, item.summary, item.implication, ...(item.tags || [])]
      .join(" ")
      .toLowerCase();
    return haystack.includes(query);
  });
}

function ensureSelection() {
  const reads = filteredReads();
  if (!reads.some((item) => item.id === state.selectedId)) {
    state.selectedId = reads[0]?.id || null;
  }
}

function renderFilters() {
  familyFiltersEl.innerHTML = currentFamilies()
    .map(
      (value) => `
        <button class="lane-tab ${value === state.family ? "active" : ""}" type="button" data-value="${esc(value)}">
          ${esc(value)}
        </button>
      `,
    )
    .join("");
  familyFiltersEl.querySelectorAll("[data-value]").forEach((button) => {
    button.addEventListener("click", () => {
      state.family = button.getAttribute("data-value") || "All";
      ensureSelection();
      renderFilters();
      renderReadList();
      renderDetail();
    });
  });
}

function renderReadList() {
  const reads = filteredReads();
  readCountEl.textContent = `${reads.length} briefings`;
  if (!reads.length) {
    readListEl.innerHTML = '<article class="empty-state"><p>No reads match the current filters.</p></article>';
    return;
  }
  readListEl.innerHTML = reads
    .map(
      (item) => `
        <button class="lane-card profile-list-item ${item.id === state.selectedId ? "active" : ""}" type="button" data-id="${esc(item.id)}">
          <div class="lane-head">
            <strong>${esc(item.title || "Briefing note")}</strong>
            <span class="status-chip tone-${tone(item.status)}">${esc(statusLabel(item.status))}</span>
          </div>
          <p>${esc(item.family || "VIP Briefing")} · ${esc(item.entity_type || "Read")}</p>
          <div class="detail-line">
            <span>${esc(`${(item.source_refs || []).length} sources`)}</span>
            <span>${esc(relDate(item.generated_at))}</span>
            <span>${esc(item.confidence || "Low")}</span>
          </div>
          <div class="lane-footer">
            <span>${esc(item.why_it_matters || item.summary || "")}</span>
          </div>
        </button>
      `,
    )
    .join("");
  readListEl.querySelectorAll("[data-id]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedId = button.getAttribute("data-id");
      renderReadList();
      renderDetail();
    });
  });
}

function selectedRead() {
  return (state.payload?.current_reads || []).find((item) => item.id === state.selectedId) || null;
}

function renderDetail() {
  const read = selectedRead();
  if (!read) {
    detailEyebrowEl.textContent = "Briefing";
    detailTitleEl.textContent = "No briefing selected";
    detailStatusEl.textContent = "Missing";
    detailStatusEl.className = "status-chip tone-blocked";
    detailConfidenceEl.textContent = "None";
    detailConfidenceEl.className = "status-chip tone-blocked";
    detailMetaEl.textContent = "";
    detailSummaryEl.textContent = "No briefing is available for the current filter set.";
    detailImplicationEl.textContent = "";
    factGridEl.innerHTML = "";
    evidenceListEl.innerHTML = '<article class="empty-state"><p>No evidence is attached.</p></article>';
    return;
  }

  detailEyebrowEl.textContent = read.family || "VIP Briefing";
  detailTitleEl.textContent = read.title || "Briefing note";
  detailStatusEl.textContent = statusLabel(read.status || "Review");
  detailStatusEl.className = `status-chip tone-${tone(read.status)}`;
  detailConfidenceEl.textContent = read.confidence || "Low";
  detailConfidenceEl.className = `status-chip tone-${tone(read.status)}`;
  detailMetaEl.innerHTML = [read.entity_type, read.priority, read.review_label, relDate(read.generated_at)]
    .filter(Boolean)
    .map((value) => `<span>${esc(value)}</span>`)
    .join("");
  detailSummaryEl.textContent = read.summary || "No summary is available.";
  detailImplicationEl.textContent = read.implication || read.why_it_matters || "";

  const facts = [
    { label: "Family", value: read.family || "VIP Briefing", note: "Read family" },
    { label: "Status", value: statusLabel(read.status || "Review"), note: "Trust state" },
    { label: "Confidence", value: read.confidence || "Low", note: "Current confidence" },
    { label: "Sources", value: String((read.source_refs || []).length), note: "Evidence references attached" },
  ];
  factGridEl.innerHTML = facts
    .map(
      (card) => `
        <article class="summary-card">
          <span class="metric-label">${esc(card.label)}</span>
          <strong>${esc(card.value)}</strong>
          <p>${esc(card.note)}</p>
        </article>
      `,
    )
    .join("");

  evidenceListEl.innerHTML = (read.source_refs || [])
    .map(
      (item) => `
        <article class="stack-card tone-ok">
          <div class="readiness-head">
            <strong>${esc(item.label || "Source")}</strong>
            <span class="status-chip tone-ok">${esc(item.source || "SWFI")}</span>
          </div>
          <p>${esc(relDate(item.retrieved_at))}</p>
          <div class="detail-line">
            ${
              item.url
                ? `<a class="nav-link" href="${esc(item.url)}" target="_blank" rel="noreferrer">Open source</a>`
                : `<span>${esc("Internal pointer")}</span>`
            }
          </div>
        </article>
      `,
    )
    .join("");
}

function renderMandateSources() {
  const items = state.payload?.mandate_sources || [];
  if (!items.length) {
    mandateListEl.innerHTML = '<article class="empty-state"><p>No official mandate sources are loaded.</p></article>';
    return;
  }
  mandateListEl.innerHTML = items
    .map(
      (item) => `
        <article class="stack-card tone-${item.priority === "High" ? "ok" : "watch"}">
          <div class="readiness-head">
            <strong>${esc(item.source_name || "Official source")}</strong>
            <span class="status-chip tone-${item.priority === "High" ? "ok" : "watch"}">${esc(item.priority || "Watch")}</span>
          </div>
          <p>${esc(item.focus || "")}</p>
          <div class="detail-line">
            <span>${esc(item.collection || "Mandates")}</span>
            <span>${esc(item.cadence || "Ongoing")}</span>
          </div>
          <a class="source-link" href="${esc(item.url || "#")}" target="_blank" rel="noreferrer">Open source</a>
        </article>
      `,
    )
    .join("");
}

function renderBriefings() {
  const items = state.payload?.briefings || [];
  if (!items.length) {
    briefingListEl.innerHTML = '<article class="empty-state"><p>No briefing items are available.</p></article>';
    return;
  }
  briefingListEl.innerHTML = items
    .map(
      (item) => `
        <article class="stack-card tone-${tone(item.status)}">
          <div class="readiness-head">
            <strong>${esc(item.title || "Briefing")}</strong>
            <span class="status-chip tone-${tone(item.status)}">${esc(item.cadence || "Current")}</span>
          </div>
          <p>${esc(item.summary || "")}</p>
          <div class="detail-line">
            <span>${esc(item.detail || "")}</span>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderProfilesInFocus() {
  const items = state.payload?.profiles_in_focus || [];
  if (!items.length) {
    profileFocusEl.innerHTML = '<article class="empty-state"><p>No profiles are currently in focus.</p></article>';
    return;
  }
  profileFocusEl.innerHTML = items
    .map(
      (item) => `
        <article class="stack-card tone-${tone(item.trust_status)}">
          <div class="readiness-head">
            <strong>${esc(item.name || "Profile")}</strong>
            <span class="status-chip tone-${tone(item.trust_status)}">${esc(statusLabel(item.trust_status || "Review"))}</span>
          </div>
          <p>${esc(item.type || "")} · ${esc(item.country || "Country not disclosed")}</p>
          <div class="lane-metrics">
            <span><strong>${esc(item.aum_display || "Not disclosed")}</strong><em>Assets</em></span>
            <span><strong>${esc(String(item.key_people || 0))}</strong><em>Key People</em></span>
            <span><strong>${esc(String(item.with_email || 0))}</strong><em>Email</em></span>
          </div>
          <div class="lane-footer">
            <span>${esc(item.focus_note || "")}</span>
          </div>
          <a class="source-link" href="${esc(item.profile_url || "#")}">Open profile</a>
        </article>
      `,
    )
    .join("");
}

function renderReviewQueue() {
  const items = state.payload?.review_queue || [];
  if (!items.length) {
    reviewQueueEl.innerHTML = '<article class="empty-state"><p>No reads are currently waiting on review.</p></article>';
    return;
  }
  reviewQueueEl.innerHTML = items
    .map(
      (item) => `
        <article class="stack-card tone-watch">
          <div class="readiness-head">
            <strong>${esc(item.title || "Pending read")}</strong>
            <span class="status-chip tone-watch">${esc(item.review_label || "Pending review")}</span>
          </div>
          <p>${esc(item.why_it_matters || item.summary || "")}</p>
          <div class="detail-line">
            <span>${esc(item.family || "VIP Briefing")}</span>
            <span>${esc(item.confidence || "Low")}</span>
          </div>
        </article>
      `,
    )
    .join("");
}

async function loadWorkspace() {
  const response = await fetch("/api/research-workspace/v1", { credentials: "same-origin" });
  if (response.status === 401) {
    window.location.href = `/login?next=${encodeURIComponent("/research")}`;
    return;
  }
  if (!response.ok) {
    throw new Error(`research workspace fetch failed: ${response.status}`);
  }
  state.payload = await response.json();
  state.search = currentSearchFromLocation();
  if (searchInput) searchInput.value = state.search;
  state.selectedId = state.payload?.current_reads?.[0]?.id || null;
  ensureSelection();
  renderTicker(state.payload);
  renderSummary(state.payload);
  renderFilters();
  renderReadList();
  renderDetail();
  renderMandateSources();
  renderBriefings();
  renderProfilesInFocus();
  renderReviewQueue();
}

searchInput?.addEventListener("input", (event) => {
  state.search = event.target.value || "";
  ensureSelection();
  renderReadList();
  renderDetail();
});

loadWorkspace().catch((error) => {
  console.error(error);
  detailTitleEl.textContent = "Briefings unavailable";
  detailSummaryEl.textContent = "The briefings workspace could not load the current data.";
});
