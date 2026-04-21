const $ = (id) => document.getElementById(id);

const summaryGrid = $("msci-summary-grid");
const answerEl = $("msci-answer");
const coverageGrid = $("msci-coverage-grid");
const fieldsEl = $("msci-requested-fields");
const previewTable = $("msci-preview-table");
const readyList = $("msci-ready-list");
const blockedList = $("msci-blocked-list");
const downloadsEl = $("msci-downloads");
const reportDownloadsEl = $("msci-report-downloads");
const targetsEl = $("msci-targets");
const breakdownList = $("msci-breakdown-list");
const statusStrip = $("msci-status-strip");

function resetInitialViewport() {
  if ("scrollRestoration" in window.history) {
    window.history.scrollRestoration = "manual";
  }
  window.requestAnimationFrame(() => {
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  });
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
  return ({
    ok: "ok",
    active: "ok",
    verified: "ok",
    partial: "partial",
    derived: "partial",
    watch: "watch",
    blocked: "blocked",
    missing: "blocked",
  })[status] || "watch";
}

function renderTicker() {
  const track = $("ticker-tape");
  if (!track) return;
  const items = [
    { label: "MSCI", value: "Key People", delta: "1000 accessible" },
    { label: "Email", value: "640", delta: "present" },
    { label: "Phone", value: "138", delta: "present" },
    { label: "LinkedIn", value: "146", delta: "linked" },
    { label: "Sample rows", value: "10", delta: "shown" },
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

function renderStatusStrip(workbench) {
  const exportInfo = workbench.people_export || {};
  const summary = exportInfo.coverage_summary || {};
  const items = [
    { label: "Subscriber access", note: "Session-backed access", status: "ok" },
    { label: "People export", note: `${summary.people_total || 0} accessible records`, status: "ok" },
    { label: "Email coverage", note: `${summary.with_email || 0} records`, status: summary.with_email ? "partial" : "blocked" },
    { label: "Phone coverage", note: `${summary.with_phone || 0} records`, status: summary.with_phone ? "partial" : "blocked" },
  ];
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

function renderSummary(workbench) {
  const cards = workbench.summary_cards || [];
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

function renderCoverage(workbench) {
  const summary = workbench.people_export?.coverage_summary || {};
  const cards = [
    { label: "Accessible people", value: String(summary.people_total || 0), note: "Authenticated people surface" },
    { label: "With email", value: String(summary.with_email || 0), note: "Export-ready contact rows" },
    { label: "With phone", value: String(summary.with_phone || 0), note: "Direct dial coverage" },
    { label: "With LinkedIn", value: String(summary.with_linkedin || 0), note: "Reference-only enrichment" },
  ];
  coverageGrid.innerHTML = cards
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

function renderFields(workbench) {
  const fields = workbench.people_export?.requested_fields || [];
  fieldsEl.innerHTML = fields
    .map(
      (field) => `
        <article class="stack-card tone-${tone(field.status)}">
          <div class="readiness-head">
            <strong>${esc(field.field)}</strong>
            <span class="status-chip tone-${tone(field.status)}">${esc(field.status)}</span>
          </div>
          <p>${esc(field.availability || "")}</p>
          <div class="detail-line"><span>${esc(field.note || "")}</span></div>
        </article>
      `,
    )
    .join("");
}

function renderPreviewRows(workbench) {
  const rows = workbench.people_export?.preview_rows || [];
  if (!rows.length) {
    previewTable.innerHTML = '<p class="panel-note">No sample rows are currently available.</p>';
    return;
  }
  const rowStatus = (row) => {
    if (row.email && row.has_entity_reference) return "Verified";
    if (row.has_entity_reference) return "Derived";
    return "Missing";
  };
  previewTable.innerHTML = `
    <div class="msci-table-row msci-table-head">
      <span>Name</span>
      <span>Title</span>
      <span>Email</span>
      <span>Phone</span>
      <span>Status</span>
      <span>Account ref</span>
    </div>
    ${rows
      .map(
        (row) => `
          <div class="msci-table-row">
            <span>${esc(row.name)}</span>
            <span>${esc(row.title || "—")}</span>
            <span>${esc(row.email || "—")}</span>
            <span>${esc(row.phone || "—")}</span>
            <span><span class="status-chip tone-${tone(rowStatus(row).toLowerCase())}">${esc(rowStatus(row))}</span></span>
            <span>${row.has_entity_reference ? "Yes" : "No"}</span>
          </div>
        `,
      )
      .join("")}
  `;
}

function renderLists(workbench) {
  const exportInfo = workbench.people_export || {};
  readyList.innerHTML = (exportInfo.export_ready_now || [])
    .map((item) => `<article class="mini-item"><span class="list-mark">✓</span><p>${esc(item)}</p></article>`)
    .join("");
  blockedList.innerHTML = (exportInfo.blocked_until_private_access || [])
    .map((item) => `<article class="mini-item"><span class="list-mark">!</span><p>${esc(item)}</p></article>`)
    .join("");
}

function renderDownloads(workbench) {
  const downloads = workbench.people_export?.downloads || {};
  const analyticsDownloads = workbench.analytics?.downloads || {};
  const items = [
    { label: "Accounts CSV", href: downloads.accounts_csv },
    { label: "People CSV", href: downloads.people_csv },
    { label: "Follow-up CSV", href: downloads.people_review_csv },
    { label: "Template CSV", href: downloads.people_template_csv },
  ].filter((item) => item.href);
  downloadsEl.innerHTML = items
    .map((item) => `<a class="nav-cta mini-cta" href="${esc(item.href)}">${esc(item.label)}</a>`)
    .join("");
  const reportItems = [
    { label: "Analytics CSV", href: analyticsDownloads.msci_analytics_csv },
    { label: "API Matrix CSV", href: analyticsDownloads.external_api_matrix_csv },
    { label: "History CSV", href: analyticsDownloads.export_history_csv },
    { label: "Phase 1 Summary", href: analyticsDownloads.phase1_summary_md },
  ].filter((item) => item.href);
  reportDownloadsEl.innerHTML = reportItems
    .map((item) => `<a class="nav-cta mini-cta" href="${esc(item.href)}">${esc(item.label)}</a>`)
    .join("");
}

function renderTargets(workbench) {
  const targets = workbench.top_targets || [];
  if (!targets.length) {
    targetsEl.innerHTML = '<p class="panel-note">Target account workbook is not currently materialized in this runtime.</p>';
    return;
  }
  targetsEl.innerHTML = `
    <div class="msci-table-row msci-table-head compact">
      <span>Account</span>
      <span>Type</span>
      <span>Tier</span>
    </div>
    ${targets
      .slice(0, 12)
      .map(
        (row) => `
          <div class="msci-table-row compact">
            <span>${esc(row.account_name)}</span>
            <span>${esc(row.account_type)}</span>
            <span>${esc(row.priority_tier)}</span>
          </div>
        `,
      )
      .join("")}
  `;
}

function renderBreakdown(workbench) {
  const items = [
    ...(workbench.type_breakdown || []).map((item) => `${item.name}: ${item.count}`),
    ...(workbench.state_breakdown || []).map((item) => `${item.name}: ${item.count}`),
  ];
  if (!items.length) {
    breakdownList.innerHTML = '<article class="stack-card"><p>Type and state breakdowns are not yet populated from the target account workbook.</p></article>';
    return;
  }
  breakdownList.innerHTML = items
    .map((item) => `<article class="mini-item"><span class="list-mark">▸</span><p>${esc(item)}</p></article>`)
    .join("");
}

async function loadWorkbench() {
  const response = await fetch("/api/msci/workbench/v1", { credentials: "same-origin" });
  if (response.status === 401) {
    window.location.href = `/login?next=${encodeURIComponent("/msci")}`;
    return;
  }
  if (!response.ok) {
    throw new Error(`msci workbench ${response.status}`);
  }
  const workbench = await response.json();
  answerEl.textContent = workbench.people_export?.answer || "MSCI export status is not available.";
  renderTicker();
  renderStatusStrip(workbench);
  renderSummary(workbench);
  renderCoverage(workbench);
  renderFields(workbench);
  renderPreviewRows(workbench);
  renderLists(workbench);
  renderDownloads(workbench);
  renderTargets(workbench);
  renderBreakdown(workbench);
  resetInitialViewport();
}

resetInitialViewport();
window.addEventListener("pageshow", resetInitialViewport);

loadWorkbench().catch((error) => {
  console.error(error);
  answerEl.textContent = "MSCI workspace failed to load.";
});
