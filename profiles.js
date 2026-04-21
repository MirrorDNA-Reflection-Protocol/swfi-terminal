const $ = (id) => document.getElementById(id);

const summaryGrid = $("profile-summary-grid");
const statusStrip = $("profile-status-strip");
const downloadsEl = $("profile-downloads");
const sourceStatusEl = $("profile-source-status");
const countEl = $("profile-count");
const searchInput = $("profile-search");
const typeFiltersEl = $("profile-type-filters");
const regionFiltersEl = $("profile-region-filters");
const profileListEl = $("profile-list");
const detailEyebrowEl = $("profile-detail-eyebrow");
const detailNameEl = $("profile-detail-name");
const detailStatusEl = $("profile-detail-status");
const detailConfidenceEl = $("profile-detail-confidence");
const detailMetaEl = $("profile-detail-meta");
const detailSummaryEl = $("profile-detail-summary");
const factGridEl = $("profile-fact-grid");
const signalListEl = $("profile-signal-list");
const sourceListEl = $("profile-source-list");
const keyPeopleCountEl = $("profile-key-people-count");
const keyPeopleEl = $("profile-key-people");

const state = {
  payload: null,
  selectedSlug: null,
  selectedProfile: null,
  search: "",
  type: "All",
  region: "All",
};

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
    authenticated: "partial",
    pending_ratification: "partial",
    ok: "ok",
    partial: "partial",
    blocked: "blocked",
    watch: "watch",
    public: "ok",
    sourced: "ok",
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
    authenticated: "Authenticated",
    pending_ratification: "Authenticated",
  })[key] || String(status || "Under review");
}

function relDate(value) {
  if (!value) return "No date";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toISOString().slice(0, 10);
}

function currentSlugFromLocation() {
  const match = window.location.pathname.match(/^\/profiles\/([^/]+)$/);
  if (match) return decodeURIComponent(match[1]);
  const params = new URLSearchParams(window.location.search);
  return params.get("id") || "";
}

function updateLocation(slug) {
  const target = slug ? `/profiles/${encodeURIComponent(slug)}` : "/profiles";
  if (window.location.pathname !== target) {
    window.history.replaceState({}, "", target);
  }
}

function renderTicker(payload) {
  const track = $("ticker-tape");
  if (!track) return;
  const items = [
    { label: "Profiles", value: payload.summary?.total_profiles || 0, delta: "current" },
    { label: "Verified", value: payload.summary?.verified_profiles || 0, delta: "current" },
    { label: "Under review", value: payload.summary?.review_profiles || 0, delta: "current" },
    { label: "Key People", value: payload.summary?.key_people || 0, delta: "attached" },
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
  const summary = payload.summary || {};
  const cards = [
    { label: "Profiles", value: summary.total_profiles || 0, note: "Curated sovereign and public profiles in current coverage" },
    { label: "Verified", value: summary.verified_profiles || 0, note: "Profiles aligned to SWFI reference coverage" },
    { label: "Needs review", value: summary.review_profiles || 0, note: "Profiles with review still required" },
    { label: "Key People", value: summary.key_people || 0, note: "Current Key People attached across coverage" },
  ];
  summaryGrid.innerHTML = cards
    .map(
      (card) => `
        <article class="metric-card">
          <span class="metric-label">${esc(card.label)}</span>
          <strong>${esc(String(card.value))}</strong>
          <p>${esc(card.note)}</p>
        </article>
      `,
    )
    .join("");

  statusStrip.innerHTML = [
    { label: "Profiles", note: summary.generated_from || "Curated profile coverage", status: "ok" },
    { label: "Regions", note: `${(summary.regions || []).length} regions represented`, status: "ok" },
    { label: "Types", note: `${(summary.types || []).length} profile types represented`, status: "ok" },
  ]
    .map(
      (item) => `
        <article class="status-pill tone-${tone(item.status)}">
          <strong>${esc(item.label)}</strong>
          <span>${esc(item.note)}</span>
        </article>
      `,
    )
    .join("");

  downloadsEl.innerHTML = `
    <a class="nav-cta mini-cta" href="/api/profiles/v1">Profiles JSON</a>
    ${
      state.selectedSlug
        ? `<a class="nav-cta mini-cta" href="/api/profiles/${encodeURIComponent(state.selectedSlug)}/v1">Current profile JSON</a>`
        : ""
    }
  `;

  sourceStatusEl.innerHTML = (payload.sources || [])
    .map(
      (source) => `
        <article class="stack-card tone-${tone(source.status)}">
          <div class="readiness-head">
            <strong>${esc(source.label || source.id || "Source")}</strong>
            <span class="status-chip tone-${tone(source.status)}">${esc(source.status || "watch")}</span>
          </div>
          <p>${esc(source.note || source.document_pointer || source.evidence_url || "")}</p>
        </article>
      `,
    )
    .join("");
}

function uniqueValues(key) {
  const values = new Set(["All"]);
  (state.payload?.profiles || []).forEach((item) => {
    if (item[key]) values.add(item[key]);
  });
  return [...values];
}

function renderFilters() {
  const renderButtons = (container, values, active, onClick) => {
    container.innerHTML = values
      .map(
        (value) => `
          <button class="lane-tab ${value === active ? "active" : ""}" type="button" data-value="${esc(value)}">
            ${esc(value)}
          </button>
        `,
      )
      .join("");
    container.querySelectorAll("button").forEach((button) => {
      button.addEventListener("click", () => onClick(button.dataset.value || "All"));
    });
  };

  renderButtons(typeFiltersEl, uniqueValues("type"), state.type, (value) => {
    state.type = value;
    ensureSelection();
    renderProfileList();
  });
  renderButtons(regionFiltersEl, uniqueValues("region"), state.region, (value) => {
    state.region = value;
    ensureSelection();
    renderProfileList();
  });
}

function filteredProfiles() {
  const query = state.search.trim().toLowerCase();
  return (state.payload?.profiles || []).filter((item) => {
    if (state.type !== "All" && item.type !== state.type) return false;
    if (state.region !== "All" && item.region !== state.region) return false;
    if (!query) return true;
    const haystack = [
      item.name,
      item.type,
      item.country,
      item.region,
      item.summary,
      ...(item.key_people || []).map((person) => `${person.name} ${person.title}`),
    ]
      .join(" ")
      .toLowerCase();
    return haystack.includes(query);
  });
}

function ensureSelection() {
  const profiles = filteredProfiles();
  const exists = profiles.some((item) => item.slug === state.selectedSlug);
  if (!exists) {
    state.selectedSlug = profiles[0]?.slug || null;
  }
}

function renderProfileList() {
  const profiles = filteredProfiles();
  countEl.textContent = `${profiles.length} profiles`;
  if (!profiles.length) {
    profileListEl.innerHTML = '<article class="empty-state"><p>No profiles match the current filters.</p></article>';
    return;
  }
  profileListEl.innerHTML = profiles
    .map(
      (item) => `
        <button class="lane-card profile-list-item ${item.slug === state.selectedSlug ? "active" : ""}" type="button" data-slug="${esc(item.slug)}">
          <div class="lane-head">
            <strong>${esc(item.name)}</strong>
            <span class="status-chip tone-${tone(item.trust?.status)}">${esc(statusLabel(item.trust?.status || "Review"))}</span>
          </div>
          <p>${esc(item.type)} · ${esc(item.country || item.region || "Country not disclosed")}</p>
          <div class="lane-metrics">
            <span><strong>${esc(item.aum_display || "Not disclosed")}</strong><em>Assets</em></span>
            <span><strong>${esc(String(item.coverage?.key_people || 0))}</strong><em>Key People</em></span>
            <span><strong>${esc(String(item.coverage?.with_email || 0))}</strong><em>Email</em></span>
          </div>
        </button>
      `,
    )
    .join("");

  profileListEl.querySelectorAll("[data-slug]").forEach((button) => {
    button.addEventListener("click", async () => {
      const slug = button.getAttribute("data-slug");
      if (!slug || slug === state.selectedSlug) return;
      state.selectedSlug = slug;
      updateLocation(slug);
      renderSummary(state.payload);
      renderProfileList();
      await loadProfile(slug);
    });
  });
}

function renderDetail(profile) {
  if (!profile) {
    detailEyebrowEl.textContent = "Profile";
    detailNameEl.textContent = "Profile not found";
    detailStatusEl.textContent = "Missing";
    detailStatusEl.className = "status-chip tone-blocked";
    detailConfidenceEl.textContent = "None";
    detailConfidenceEl.className = "status-chip tone-blocked";
    detailMetaEl.textContent = "";
    detailSummaryEl.textContent = "The requested profile is not available.";
    factGridEl.innerHTML = "";
    signalListEl.innerHTML = '<article class="empty-state"><p>No governed profile signals are available.</p></article>';
    sourceListEl.innerHTML = '<article class="empty-state"><p>No source references are available.</p></article>';
    keyPeopleCountEl.textContent = "0 people";
    keyPeopleEl.innerHTML = '<article class="empty-state"><p>No Key People are attached to this profile.</p></article>';
    return;
  }

  detailEyebrowEl.textContent = profile.type || "Profile";
  detailNameEl.textContent = profile.name || "Unnamed profile";
  detailStatusEl.textContent = statusLabel(profile.trust?.status || "Review");
  detailStatusEl.className = `status-chip tone-${tone(profile.trust?.status)}`;
  detailConfidenceEl.textContent = profile.trust?.confidence || "Low";
  detailConfidenceEl.className = `status-chip tone-${tone(profile.trust?.status)}`;
  detailMetaEl.innerHTML = [
    profile.country,
    profile.region,
    profile.established_at ? `Established ${profile.established_at.slice(0, 4)}` : "",
    profile.updated_at ? `Updated ${profile.updated_at}` : "",
  ]
    .filter(Boolean)
    .map((value) => `<span>${esc(value)}</span>`)
    .join("");
  detailSummaryEl.textContent = profile.summary || profile.background || profile.trust?.note || "No summary is available.";

  const facts = [
    { label: "Assets", value: profile.aum_display || "Not disclosed", note: "Current value" },
    { label: "Country", value: profile.country || "Not disclosed", note: "Profile geography" },
    { label: "Region", value: profile.region || "Not disclosed", note: "SWFI region" },
    { label: "Established", value: profile.established_at || "Not disclosed", note: "Institution start date" },
    { label: "Key People", value: String(profile.coverage?.key_people || 0), note: "Current people attached" },
    { label: "With email", value: String(profile.coverage?.with_email || 0), note: "Key People with email" },
    { label: "With phone", value: String(profile.coverage?.with_phone || 0), note: "Key People with phone" },
    { label: "Website", value: profile.website ? "Available" : "Missing", note: profile.website || "No website in current coverage" },
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

  signalListEl.innerHTML = (profile.signals || [])
    .map(
      (item) => `
        <article class="stack-card tone-${tone(item.status)}">
          <div class="readiness-head">
            <strong>${esc(item.title)}</strong>
            <span class="status-chip tone-${tone(item.status)}">${esc(statusLabel(item.status))}</span>
          </div>
          <p>${esc(item.summary || "")}</p>
          <div class="detail-line">
            <span>${esc(item.confidence || "")}</span>
            <span>${esc(relDate(item.observed_at))}</span>
          </div>
          ${
            (item.source_refs || []).length
              ? `<div class="tag-row">${item.source_refs
                  .map((ref) =>
                    ref.url
                      ? `<a class="data-pill pill-link" href="${esc(ref.url)}" target="_blank" rel="noreferrer">${esc(ref.label || ref.source || "Source")}</a>`
                      : `<span class="data-pill">${esc(ref.label || ref.source || "Source")}</span>`,
                  )
                  .join("")}</div>`
              : ""
          }
        </article>
      `,
    )
    .join("");

  sourceListEl.innerHTML = (profile.source_refs || [])
    .map(
      (item) => `
        <article class="stack-card tone-${tone(item.status)}">
          <div class="readiness-head">
            <strong>${esc(item.label || "Source")}</strong>
            <span class="status-chip tone-${tone(item.status)}">${esc(statusLabel(item.status || "watch"))}</span>
          </div>
          <p>${esc(item.source || "")}</p>
          <div class="detail-line">
            ${item.retrieved_at ? `<span>${esc(relDate(item.retrieved_at))}</span>` : ""}
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

  const people = profile.key_people || [];
  keyPeopleCountEl.textContent = `${people.length} people`;
  if (!people.length) {
    keyPeopleEl.innerHTML = '<article class="empty-state"><p>No Key People are attached to this profile.</p></article>';
  } else {
    keyPeopleEl.innerHTML = `
      <div class="msci-table-row profile-people-row msci-table-head">
        <span>Name</span>
        <span>Title</span>
        <span>Email</span>
        <span>Phone</span>
        <span>LinkedIn</span>
      </div>
      ${people
        .map(
          (person) => `
            <div class="msci-table-row profile-people-row">
              <span>${esc(person.name || "Unknown")}</span>
              <span>${esc(person.title || "Role not specified")}</span>
              <span>${person.email ? `<a class="nav-link" href="mailto:${esc(person.email)}">${esc(person.email)}</a>` : "—"}</span>
              <span>${esc(person.phone || "—")}</span>
              <span>${person.linkedin ? `<a class="nav-link" href="${esc(person.linkedin)}" target="_blank" rel="noreferrer">Open</a>` : "—"}</span>
            </div>
          `,
        )
        .join("")}
    `;
  }

  downloadsEl.innerHTML = `
    <a class="nav-cta mini-cta" href="/api/profiles/v1">Profiles JSON</a>
    <a class="nav-cta mini-cta" href="${esc(profile.download_url || `/api/profiles/${profile.slug}/v1`)}">Current profile JSON</a>
    ${profile.website ? `<a class="nav-cta mini-cta" href="${esc(profile.website)}" target="_blank" rel="noreferrer">Institution website</a>` : ""}
  `;
}

async function loadProfile(slug) {
  if (!slug) {
    renderDetail(null);
    return;
  }
  const response = await fetch(`/api/profiles/${encodeURIComponent(slug)}/v1`, { credentials: "same-origin" });
  if (response.status === 401) {
    window.location.href = `/login?next=${encodeURIComponent(`/profiles/${slug}`)}`;
    return;
  }
  if (!response.ok) {
    renderDetail(null);
    return;
  }
  const payload = await response.json();
  state.selectedProfile = payload.profile || null;
  renderDetail(state.selectedProfile);
}

async function loadProfiles() {
  const response = await fetch("/api/profiles/v1", { credentials: "same-origin" });
  if (response.status === 401) {
    window.location.href = `/login?next=${encodeURIComponent(window.location.pathname || "/profiles")}`;
    return;
  }
  if (!response.ok) {
    throw new Error(`profiles fetch failed: ${response.status}`);
  }
  state.payload = await response.json();
  const currentSlug = currentSlugFromLocation();
  if (!currentSlug && (state.payload?.profiles || []).some((item) => item.type === "Sovereign Wealth Fund")) {
    state.type = "Sovereign Wealth Fund";
  }
  state.selectedSlug = currentSlug || state.payload?.profiles?.find((item) => item.type === state.type)?.slug || state.payload?.profiles?.[0]?.slug || null;
  ensureSelection();
  updateLocation(state.selectedSlug);
  renderTicker(state.payload);
  renderSummary(state.payload);
  renderFilters();
  renderProfileList();
  await loadProfile(state.selectedSlug);
}

searchInput?.addEventListener("input", async (event) => {
  state.search = event.target.value || "";
  ensureSelection();
  renderProfileList();
  updateLocation(state.selectedSlug);
  await loadProfile(state.selectedSlug);
});

window.addEventListener("popstate", async () => {
  state.selectedSlug = currentSlugFromLocation() || state.payload?.profiles?.[0]?.slug || null;
  ensureSelection();
  renderProfileList();
  await loadProfile(state.selectedSlug);
});

loadProfiles().catch((error) => {
  console.error(error);
  detailNameEl.textContent = "Profiles unavailable";
  detailSummaryEl.textContent = "The profiles workspace could not load the current data.";
});
