const $ = (id) => document.getElementById(id);

const summaryGrid = $("admin-summary-grid");
const statusStrip = $("admin-status-strip");
const reportDownloadsEl = $("admin-report-downloads");
const rebuildButton = $("admin-rebuild-button");
const statusList = $("admin-status-list");
const analyticsGrid = $("admin-analytics-grid");
const nuggetList = $("admin-nugget-list");
const exportHistoryEl = $("admin-export-history");
const errorList = $("admin-error-list");
const apiMatrixEl = $("admin-api-matrix");
const reviewQueueEl = $("admin-review-queue");
const reviewHistoryEl = $("admin-review-history");
const researchEvalEl = $("admin-research-eval");
let adminPayload = null;

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
    ok: "ok",
    active: "ok",
    verified: "ok",
    partial: "partial",
    derived: "partial",
    needsreview: "watch",
    needs_review: "watch",
    rejected: "blocked",
    conflicted: "watch",
    watch: "watch",
    blocked: "blocked",
    missing: "blocked",
    free_public: "ok",
    free_public_with_key: "ok",
    hybrid_open_or_paid: "partial",
    paid_for_production: "watch",
  })[key] || "watch";
}

function renderTicker(payload) {
  const track = $("ticker-tape");
  if (!track) return;
  const analyticsCards = payload.analytics?.cards || [];
  const items = [
    { label: "Targets", value: payload.summary_cards?.[0]?.value || "0", delta: "accounts" },
    { label: "People", value: payload.summary_cards?.[1]?.value || "0", delta: "accessible" },
    { label: "Exports", value: payload.summary_cards?.[2]?.value || "0", delta: "logged" },
    ...analyticsCards.slice(0, 2).map((card) => ({ label: card.label, value: card.value, delta: card.note })),
  ];
  const markup = items
    .map(
      (item) => `
        <span class="ticker-item">
          <span class="t-name">${esc(item.label)}</span>
          <span class="t-val">${esc(item.value)}</span>
          <span class="t-val">${esc(item.delta)}</span>
          <span class="t-sep">│</span>
        </span>
      `,
    )
    .join("");
  track.innerHTML = markup + markup;
}

function renderSummaryCards(payload) {
  const cards = payload.summary_cards || [];
  summaryGrid.innerHTML = cards
    .map(
      (card) => `
        <article class="metric-card">
          <span class="metric-label">${esc(card.label)}</span>
          <strong>${esc(card.value)}</strong>
          <p>${esc(card.note)}</p>
        </article>
      `,
    )
    .join("");
}

function renderStatusStrip(payload) {
  const items = (payload.statuses || []).slice(0, 4);
  statusStrip.innerHTML = items
    .map(
      (item) => `
        <article class="status-pill tone-${tone(item.status)}">
          <strong>${esc(item.label)}</strong>
          <span>${esc(item.note)}</span>
        </article>
      `,
    )
    .join("");
}

function renderReports(payload) {
  const reports = payload.reports || [];
  reportDownloadsEl.innerHTML = reports
    .map((item) => `<a class="nav-cta mini-cta" href="${esc(item.url)}">${esc(item.label)}</a>`)
    .join("");
}

function statusLabel(value) {
  const key = String(value || "").toLowerCase().replaceAll(" ", "_");
  return ({
    needsreview: "Needs review",
    needs_review: "Needs review",
    verified: "Verified",
    derived: "Derived",
    rejected: "Rejected",
    conflicted: "Conflicted",
    approved: "Approved",
    promoted: "Promoted",
    pending: "Pending review",
    publishable: "Publishable",
  })[key] || String(value || "watch");
}

function renderStatusList(payload) {
  const statuses = payload.statuses || [];
  statusList.innerHTML = statuses
    .map(
      (item) => `
        <article class="stack-card tone-${tone(item.status)}">
          <div class="readiness-head">
            <strong>${esc(item.label)}</strong>
            <span class="status-chip tone-${tone(item.status)}">${esc(item.status)}</span>
          </div>
          <p>${esc(item.note)}</p>
        </article>
      `,
    )
    .join("");
}

function renderAnalytics(payload) {
  const cards = payload.analytics?.cards || [];
  analyticsGrid.innerHTML = cards
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
}

function renderNuggets(payload) {
  const items = payload.nugget_pipeline?.items || [];
  if (!items.length) {
    nuggetList.innerHTML = '<article class="stack-card tone-watch"><strong>No governed nuggets yet.</strong><p>The pipeline is defined but no packet-derived items were produced.</p></article>';
    return;
  }
  nuggetList.innerHTML = items
    .map(
      (item) => `
        <article class="stack-card tone-${tone(item.status)}">
          <div class="readiness-head">
            <strong>${esc(item.claim)}</strong>
            <span class="status-chip tone-${tone(item.status)}">${esc(statusLabel(item.status))}</span>
          </div>
          <p>${esc(item.why_it_matters || item.observed_fact || "")}</p>
          <div class="detail-line">
            <span>${esc(item.confidence || "")}</span>
            <span>${esc(item.priority || "")}</span>
            <span>${esc((item.tags || []).join(" · "))}</span>
            <span>${esc(statusLabel(item.review?.label || item.review?.state || ""))}</span>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderExportHistory(payload) {
  const rows = payload.export_history || [];
  if (!rows.length) {
    exportHistoryEl.innerHTML = '<p class="panel-note">No export events have been logged yet.</p>';
    return;
  }
  exportHistoryEl.innerHTML = `
    <div class="msci-table-row msci-table-head admin-table-row">
      <span>Timestamp</span>
      <span>Route</span>
      <span>Outcome</span>
      <span>Auth</span>
      <span>Host</span>
      <span>Client IP</span>
      <span>User agent</span>
    </div>
    ${rows
      .map(
        (row) => `
          <div class="msci-table-row admin-table-row">
            <span>${esc(row.timestamp || "—")}</span>
            <span>${esc(row.route || "—")}</span>
            <span><span class="status-chip tone-${tone(row.outcome === "ok" ? "ok" : row.outcome === "denied" ? "blocked" : "watch")}">${esc(row.outcome || "—")}</span></span>
            <span>${esc(row.auth_mode || "—")}</span>
            <span>${esc(row.host || "—")}</span>
            <span>${esc(row.client_ip || "—")}</span>
            <span>${esc(row.user_agent || "—")}</span>
          </div>
        `,
      )
      .join("")}
  `;
}

function renderErrors(payload) {
  const items = payload.errors || [];
  if (!items.length) {
    errorList.innerHTML = '<article class="stack-card tone-ok"><strong>No blocking issues currently surfaced.</strong><p>The current wedge is operating inside the expected preview constraints.</p></article>';
    return;
  }
  errorList.innerHTML = items
    .map(
      (item) => `
        <article class="stack-card tone-${tone(item.status)}">
          <strong>${esc(item.title)}</strong>
          <p>${esc(item.detail)}</p>
        </article>
      `,
    )
    .join("");
}

function renderApiMatrix(payload) {
  const items = payload.external_api_matrix || [];
  apiMatrixEl.innerHTML = items
    .map(
      (item) => `
        <article class="stack-card tone-${tone(item.probe_tone || item.live_status || item.access)}">
          <div class="readiness-head">
            <strong>${esc(item.name)}</strong>
            <span class="status-chip tone-${tone(item.probe_tone || item.live_status || item.access)}">${esc(item.live_status || item.access)}</span>
          </div>
          <p>${esc(item.use_case)}</p>
          <div class="detail-line">
            <span>${esc(item.probe_note || item.note)}</span>
            <a class="nav-link" href="${esc(item.url)}" target="_blank" rel="noreferrer">Source</a>
            ${item.probe_url ? `<a class="nav-link" href="${esc(item.probe_url)}" target="_blank" rel="noreferrer">Probe</a>` : ""}
            ${item.checked_at ? `<span>${esc(item.checked_at)}</span>` : ""}
          </div>
        </article>
      `,
    )
    .join("");
}

function renderReviewQueue(payload) {
  const items = payload.nugget_pipeline?.review_queue || [];
  if (!items.length) {
    reviewQueueEl.innerHTML = '<article class="stack-card tone-ok"><strong>No nuggets require review.</strong><p>The current packet can publish all derived items without analyst gating.</p></article>';
    return;
  }
  reviewQueueEl.innerHTML = items
    .map(
      (item) => `
        <article class="stack-card tone-${tone(item.status)}">
          <div class="readiness-head">
            <strong>${esc(item.claim)}</strong>
            <span class="status-chip tone-${tone(item.status)}">${esc(statusLabel(item.status))}</span>
          </div>
          <p>${esc(item.derived_implication || item.observed_fact || "")}</p>
          <div class="detail-line">
            <span>${esc(item.confidence || "")}</span>
            <span>${esc(item.priority || "")}</span>
            <span>${esc((item.source_refs || []).map((ref) => ref.label || "").filter(Boolean).join(" · "))}</span>
          </div>
          <div class="detail-line">
            <span>${esc(statusLabel(item.review?.label || item.review?.state || "Pending review"))}</span>
          </div>
          <div class="download-row review-action-row">
            <button type="button" class="nav-cta mini-cta" data-review-action="approve" data-review-id="${esc(item.entity_id)}">Approve</button>
            <button type="button" class="nav-cta mini-cta" data-review-action="promote" data-review-id="${esc(item.entity_id)}">Promote</button>
            <button type="button" class="nav-cta mini-cta" data-review-action="reject" data-review-id="${esc(item.entity_id)}">Reject</button>
            <button type="button" class="lane-tab" data-review-action="reset" data-review-id="${esc(item.entity_id)}">Reset</button>
          </div>
        </article>
      `,
    )
    .join("");
  reviewQueueEl.querySelectorAll("[data-review-action]").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.getAttribute("data-review-id");
      const action = button.getAttribute("data-review-action");
      if (!id || !action) return;
      submitReviewAction(id, action, button).catch((error) => console.error(error));
    });
  });
}

function renderReviewHistory(payload) {
  const items = payload.nugget_pipeline?.review_history || [];
  if (!items.length) {
    reviewHistoryEl.innerHTML = '<article class="stack-card tone-watch"><strong>No review actions recorded yet.</strong><p>Approve, reject, or promote governed nuggets here to create the first analyst history.</p></article>';
    return;
  }
  reviewHistoryEl.innerHTML = items
    .map(
      (item) => `
        <article class="stack-card tone-${tone(item.action === "reject" ? "rejected" : item.action === "promote" ? "verified" : "derived")}">
          <div class="readiness-head">
            <strong>${esc(item.nugget_id || "nugget")}</strong>
            <span class="status-chip tone-${tone(item.action === "reject" ? "rejected" : item.action === "promote" ? "verified" : "derived")}">${esc(statusLabel(item.action))}</span>
          </div>
          <p>${esc(item.note || "No analyst note attached.")}</p>
          <div class="detail-line">
            <span>${esc(item.reviewer || "reviewer")}</span>
            <span>${esc(item.auth_mode || "")}</span>
            <span>${esc(item.timestamp || "")}</span>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderResearchEval(payload) {
  const summary = payload.research_eval || {};
  const rows = summary.results || [];
  const head = `
    <article class="stack-card tone-${summary.failed_cases ? "watch" : "ok"}">
      <div class="readiness-head">
        <strong>${esc(summary.pack_version || "swfi.eval_pack.v1")}</strong>
        <span class="status-chip tone-${summary.failed_cases ? "watch" : "ok"}">${esc(`${summary.passed_cases || 0}/${summary.total_cases || 0} passed`)}</span>
      </div>
      <p>${esc(summary.failed_cases ? "One or more regression cases need attention." : "Current deterministic regression cases are passing.")}</p>
    </article>
  `;
  const body = rows
    .map(
      (row) => `
        <article class="stack-card tone-${row.ok ? "ok" : "blocked"}">
          <div class="readiness-head">
            <strong>${esc(row.id || row.query || "case")}</strong>
            <span class="status-chip tone-${row.ok ? "ok" : "blocked"}">${esc(row.ok ? "pass" : "fail")}</span>
          </div>
          <p>${esc(row.note || row.query || "")}</p>
          <div class="detail-line">
            <span>${esc(row.status || "")}</span>
            <span>${esc(row.prompt_version || "")}</span>
            <span>${esc(`${row.source_refs || 0} refs`)}</span>
          </div>
        </article>
      `,
    )
    .join("");
  researchEvalEl.innerHTML = head + body;
}

function renderPayload(payload) {
  adminPayload = payload;
  renderTicker(payload);
  renderSummaryCards(payload);
  renderStatusStrip(payload);
  renderReports(payload);
  renderStatusList(payload);
  renderAnalytics(payload);
  renderNuggets(payload);
  renderExportHistory(payload);
  renderErrors(payload);
  renderApiMatrix(payload);
  renderReviewQueue(payload);
  renderReviewHistory(payload);
  renderResearchEval(payload);
}

async function loadAdmin() {
  const response = await fetch("/api/admin/v1", { credentials: "same-origin" });
  if (response.status === 401) {
    window.location.href = `/login?next=${encodeURIComponent("/admin")}`;
    return null;
  }
  if (!response.ok) {
    throw new Error(`admin payload ${response.status}`);
  }
  const payload = await response.json();
  renderPayload(payload);
  return payload;
}

async function rebuildRuntime() {
  rebuildButton.disabled = true;
  const originalLabel = rebuildButton.textContent;
  rebuildButton.textContent = "Rebuilding...";
  try {
    const response = await fetch("/api/admin/rebuild", {
      method: "POST",
      credentials: "same-origin",
    });
    if (response.status === 401) {
      window.location.href = `/login?next=${encodeURIComponent("/admin")}`;
      return;
    }
    if (!response.ok) {
      throw new Error(`admin rebuild ${response.status}`);
    }
    await loadAdmin();
    rebuildButton.textContent = "Rebuilt";
    window.setTimeout(() => {
      rebuildButton.textContent = originalLabel;
    }, 1500);
  } catch (error) {
    console.error(error);
    rebuildButton.textContent = "Rebuild failed";
    window.setTimeout(() => {
      rebuildButton.textContent = originalLabel;
    }, 1800);
  } finally {
    rebuildButton.disabled = false;
  }
}

async function submitReviewAction(id, action, button) {
  const originalText = button.textContent;
  button.disabled = true;
  button.textContent = "Saving...";
  try {
    const note = action === "reject" || action === "promote" ? window.prompt("Optional analyst note", "") || "" : "";
    const response = await fetch("/api/admin/nuggets/review", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, action, note }),
    });
    if (response.status === 401) {
      window.location.href = `/login?next=${encodeURIComponent("/admin")}`;
      return;
    }
    if (!response.ok) {
      throw new Error(`review action ${response.status}`);
    }
    const payload = await response.json();
    if (payload.admin) {
      renderPayload(payload.admin);
      return;
    }
    await loadAdmin();
  } finally {
    button.disabled = false;
    button.textContent = originalText;
  }
}

rebuildButton?.addEventListener("click", () => {
  rebuildRuntime().catch((error) => console.error(error));
});

loadAdmin().catch((error) => {
  console.error(error);
  errorList.innerHTML = '<article class="stack-card tone-blocked"><strong>Admin console failed to load.</strong><p>Refresh the page or rebuild the runtime from localhost.</p></article>';
});
