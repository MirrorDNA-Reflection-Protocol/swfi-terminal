const state = {
  dashboard: null,
  lane: "All",
  query: "",
};

const statusStrip = document.getElementById("status-strip");
const metricGrid = document.getElementById("metric-grid");
const laneTabs = document.getElementById("lane-tabs");
const proposalBrief = document.getElementById("proposal-brief");
const referenceGrid = document.getElementById("reference-grid");
const collectionList = document.getElementById("collection-list");
const laneList = document.getElementById("lane-list");
const actionList = document.getElementById("action-list");
const clientFilters = document.getElementById("client-filters");
const concernSearch = document.getElementById("concern-search");
const concernList = document.getElementById("concern-list");
const concernCount = document.getElementById("concern-count");
const apiTitle = document.getElementById("api-title");
const apiPath = document.getElementById("api-path");
const apiSummaryGrid = document.getElementById("api-summary-grid");
const apiParamList = document.getElementById("api-param-list");
const apiFieldList = document.getElementById("api-field-list");
const readinessList = document.getElementById("readiness-list");
const deliverableList = document.getElementById("deliverable-list");
const telemetryChart = document.getElementById("telemetry-chart");
const lastRefresh = document.getElementById("last-refresh");
const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const benchmarkList = document.getElementById("benchmark-list");
const apiStackList = document.getElementById("api-stack-list");

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatRelativeDate(isoString) {
  if (!isoString) return "No refresh time";
  const deltaMs = Date.now() - new Date(isoString).getTime();
  const minutes = Math.max(1, Math.round(deltaMs / 60000));
  if (minutes < 60) return `Refreshed ${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  return `Refreshed ${hours}h ago`;
}

function statusTone(status) {
  return {
    ok: "ok",
    partial: "partial",
    active: "ok",
    scaffolded: "watch",
    blocked: "blocked",
    watch: "watch",
    direct_competitor: "partial",
    platform_benchmark: "partial",
    missing: "blocked",
    partial_have: "partial",
    have_base_need_productization: "partial",
  }[status] || status;
}

function renderStatusStrip() {
  statusStrip.innerHTML = state.dashboard.statuses
    .map(
      (item) => `
        <article class="status-pill tone-${statusTone(item.status)}">
          <strong>${escapeHtml(item.source)}</strong>
          <span>${escapeHtml(item.note)}</span>
        </article>
      `,
    )
    .join("");
}

function renderMetricGrid() {
  metricGrid.innerHTML = state.dashboard.metric_cards
    .map(
      (card) => `
        <article class="metric-card">
          <span class="metric-label">${escapeHtml(card.label)}</span>
          <strong>${escapeHtml(card.value)}</strong>
          <p>${escapeHtml(card.note)}</p>
        </article>
      `,
    )
    .join("");
}

function renderLaneSelectors() {
  const lanes = [{ name: "All", focus: "All client lanes" }, ...state.dashboard.lanes];

  const buttonMarkup = lanes
    .map(
      (lane) => `
        <button
          class="lane-tab ${lane.name === state.lane ? "active" : ""}"
          type="button"
          data-lane="${escapeHtml(lane.name)}"
        >
          <span>${escapeHtml(lane.name)}</span>
          <strong>${escapeHtml(lane.name === "All" ? "Full desk" : lane.focus)}</strong>
        </button>
      `,
    )
    .join("");

  laneTabs.innerHTML = buttonMarkup;
  clientFilters.innerHTML = buttonMarkup;

  document.querySelectorAll("[data-lane]").forEach((button) => {
    button.addEventListener("click", () => {
      state.lane = button.dataset.lane || "All";
      renderLaneSelectors();
      renderLaneList();
      renderConcernList();
      renderTelemetryChart();
    });
  });
}

function renderProposalBrief() {
  const proposal = state.dashboard.proposal;
  proposalBrief.innerHTML = `
    <div class="brief-grid">
      <article class="brief-card">
        <span class="metric-label">Project fee</span>
        <strong>${escapeHtml(proposal.fee)}</strong>
        <p>${escapeHtml(proposal.goal)}</p>
      </article>
      <article class="brief-card">
        <span class="metric-label">Timeline</span>
        <strong>${escapeHtml(proposal.timeline)}</strong>
        <p>${proposal.payments.map(escapeHtml).join(" · ")}</p>
      </article>
    </div>
  `;
}

function renderReferenceGrid() {
  const reference = state.dashboard.platform_reference;
  const cards = reference.counts
    .map(
      (item) => `
        <article class="reference-card">
          <span class="metric-label">${escapeHtml(item.label)}</span>
          <strong>${escapeHtml(item.value)}</strong>
          <p>${escapeHtml(item.note)}</p>
        </article>
      `,
    )
    .join("");

  const surfaces = reference.surfaces
    .map(
      (item) => `
        <article class="surface-card">
          <span class="metric-label">${escapeHtml(item.label)}</span>
          <strong>${escapeHtml(item.value)}</strong>
          <p>${escapeHtml(item.note)}</p>
        </article>
      `,
    )
    .join("");

  referenceGrid.innerHTML = `
    <p class="panel-note">${escapeHtml(reference.observed_at)}</p>
    <div class="reference-cards">${cards}</div>
    <div class="surface-list">${surfaces}</div>
  `;
}

function renderCollections() {
  collectionList.innerHTML = state.dashboard.aum_docs.collections
    .slice(0, 14)
    .map((item) => `<span class="data-pill">${escapeHtml(item.label)}</span>`)
    .join("");
}

function renderLaneList() {
  laneList.innerHTML = state.dashboard.lanes
    .map(
      (lane) => `
        <button
          class="lane-card ${lane.name === state.lane ? "active" : ""}"
          type="button"
          data-lane="${escapeHtml(lane.name)}"
        >
          <div class="lane-head">
            <div>
              <span class="metric-label">${escapeHtml(lane.cadence)}</span>
              <strong>${escapeHtml(lane.name)}</strong>
            </div>
            <span class="status-chip tone-${statusTone(lane.status)}">${escapeHtml(lane.status)}</span>
          </div>
          <p>${escapeHtml(lane.focus)}</p>
          <div class="lane-metrics">
            <span><strong>${lane.issue_count}</strong><em>Issues</em></span>
            <span><strong>${lane.manual_count}</strong><em>Manual</em></span>
            <span><strong>${lane.field_gap_count}</strong><em>Field gaps</em></span>
          </div>
          <div class="lane-footer">
            <span>${escapeHtml(lane.deliverable)}</span>
            <span>${escapeHtml(lane.source_note)}</span>
          </div>
        </button>
      `,
    )
    .join("");

  laneList.querySelectorAll("[data-lane]").forEach((button) => {
    button.addEventListener("click", () => {
      state.lane = button.dataset.lane || "All";
      renderLaneSelectors();
      renderLaneList();
      renderConcernList();
      renderTelemetryChart();
    });
  });
}

function renderActionList() {
  actionList.innerHTML = state.dashboard.action_queue
    .map(
      (item) => `
        <article class="action-card tone-${statusTone(item.status)}">
          <div class="action-head">
            <strong>${escapeHtml(item.title)}</strong>
            <span>${escapeHtml(item.priority)}</span>
          </div>
          <p>${escapeHtml(item.impact)}</p>
          <div class="action-meta">
            <span>${escapeHtml(item.lane)}</span>
            <span>${escapeHtml(item.status)}</span>
          </div>
        </article>
      `,
    )
    .join("");
}

function filteredConcerns() {
  const query = state.query.trim().toLowerCase();
  return state.dashboard.concerns.filter((row) => {
    const matchesLane = state.lane === "All" ? true : row.client === state.lane;
    const haystack = [row.client, row.use_case, row.requirement, row.challenge, row.recommendation, row.title]
      .join(" ")
      .toLowerCase();
    const matchesQuery = query ? haystack.includes(query) : true;
    return matchesLane && matchesQuery;
  });
}

function renderConcernList() {
  const rows = filteredConcerns();
  concernCount.textContent = `${rows.length} issue${rows.length === 1 ? "" : "s"}`;

  if (!rows.length) {
    concernList.innerHTML = `
      <article class="empty-state">
        <strong>No concern rows match the current lane filter.</strong>
        <p>Widen the desk filter or clear the search box.</p>
      </article>
    `;
    return;
  }

  concernList.innerHTML = rows
    .map(
      (row) => `
        <article class="concern-card tone-${statusTone(row.state)}">
          <div class="concern-head-row">
            <div>
              <p class="eyebrow">${escapeHtml(row.client)} · ${escapeHtml(row.use_case)}</p>
              <h4>${escapeHtml(row.title)}</h4>
            </div>
            <div class="tag-column">
              <span class="status-chip tone-${statusTone(row.state)}">${escapeHtml(row.state)}</span>
              <span class="priority-chip">${escapeHtml(row.priority)}</span>
            </div>
          </div>

          ${
            row.requirement
              ? `<div class="concern-block"><span>Requirement</span><p>${escapeHtml(row.requirement)}</p></div>`
              : ""
          }
          ${
            row.challenge
              ? `<div class="concern-block"><span>Challenge</span><p>${escapeHtml(row.challenge)}</p></div>`
              : ""
          }
          ${
            row.recommendation
              ? `<div class="concern-block"><span>Recommendation</span><p>${escapeHtml(row.recommendation)}</p></div>`
              : ""
          }
          <div class="tag-row">
            ${row.tags.map((tag) => `<span class="data-pill">${escapeHtml(tag.replaceAll("_", " "))}</span>`).join("")}
          </div>
        </article>
      `,
    )
    .join("");
}

function renderApiSurface() {
  const docs = state.dashboard.aum_docs;
  apiTitle.textContent = docs.title;
  apiPath.textContent = docs.path;

  const summaryCards = [
    {
      label: "Query params",
      value: String(docs.query_parameters.length),
      note: "Time windows, value ranges, entity_id, pagination, sort",
    },
    {
      label: "Example fields",
      value: String(docs.example_fields.length),
      note: "Assets, net assets, investments, liabilities, allocation splits",
    },
    {
      label: "Docs collections",
      value: String(docs.collections.length),
      note: "AUM plus adjacent object collections in the public docs",
    },
    {
      label: "Delivery modes",
      value: "API + CSV + UI",
      note: "Product must support machine delivery and operator workflows",
    },
  ];

  apiSummaryGrid.innerHTML = summaryCards
    .map(
      (card) => `
        <article class="summary-card">
          <span class="metric-label">${escapeHtml(card.label)}</span>
          <strong>${escapeHtml(card.value)}</strong>
          <p>${escapeHtml(card.note)}</p>
        </article>
      `,
    )
    .join("");

  apiParamList.innerHTML = docs.query_parameters
    .slice(0, 18)
    .map(
      (param) => `
        <article class="api-item">
          <div class="api-item-head">
            <strong>${escapeHtml(param.name)}</strong>
            <span>${escapeHtml(param.type)}</span>
          </div>
          <p>${escapeHtml(param.description)}</p>
        </article>
      `,
    )
    .join("");

  apiFieldList.innerHTML = docs.example_fields
    .slice(0, 24)
    .map((field) => `<span class="data-pill">${escapeHtml(field)}</span>`)
    .join("");
}

function renderReadiness() {
  readinessList.innerHTML = state.dashboard.readiness
    .map(
      (item) => `
        <article class="readiness-card tone-${statusTone(item.status)}">
          <div class="readiness-head">
            <strong>${escapeHtml(item.title)}</strong>
            <span class="status-chip tone-${statusTone(item.status)}">${escapeHtml(item.status)}</span>
          </div>
          <p>${escapeHtml(item.note)}</p>
        </article>
      `,
    )
    .join("");

  deliverableList.innerHTML = state.dashboard.proposal.deliverables
    .map((item) => `<article class="deliverable-item"><span class="list-mark">OK</span><p>${escapeHtml(item)}</p></article>`)
    .join("");
}

function renderBenchmarkPanel() {
  benchmarkList.innerHTML = state.dashboard.competitor_benchmark
    .map(
      (item) => `
        <article class="benchmark-card">
          <div class="benchmark-head">
            <div>
              <p class="eyebrow">${escapeHtml(item.status.replaceAll("_", " "))}</p>
              <strong>${escapeHtml(item.name)}</strong>
            </div>
          </div>
          <p>${escapeHtml(item.headline)}</p>
          <div class="mini-list">
            ${item.signals.map((signal) => `<article class="mini-item"><span class="list-mark">01</span><p>${escapeHtml(signal)}</p></article>`).join("")}
          </div>
          <a class="source-link" href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">${escapeHtml(item.source)}</a>
        </article>
      `,
    )
    .join("");

  apiStackList.innerHTML = state.dashboard.required_api_stack
    .map(
      (item) => `
        <article class="stack-card tone-${statusTone(item.status)}">
          <div class="readiness-head">
            <strong>${escapeHtml(item.name)}</strong>
            <span class="status-chip tone-${statusTone(item.status)}">${escapeHtml(item.status.replaceAll("_", " "))}</span>
          </div>
          <p>${escapeHtml(item.why)}</p>
          <div class="concern-block compact">
            <span>Gap</span>
            <p>${escapeHtml(item.gap)}</p>
          </div>
          <div class="tag-row">
            ${(item.sources || [])
              .map(
                (source) => `
                  <a class="data-pill pill-link" href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">
                    ${escapeHtml(source.label)}
                  </a>
                `,
              )
              .join("")}
          </div>
        </article>
      `,
    )
    .join("");
}

function renderTelemetryChart() {
  const selected = state.lane === "All" ? state.dashboard.lanes : state.dashboard.lanes.filter((lane) => lane.name === state.lane);
  const values = selected.map((lane) => Math.max(1, lane.issue_count + lane.manual_count + lane.field_gap_count));
  const maxValue = Math.max(...values, 1);
  const width = 320;
  const height = 120;
  const step = values.length > 1 ? width / (values.length - 1) : width;
  const points = values
    .map((value, index) => {
      const x = values.length === 1 ? width / 2 : index * step;
      const y = height - (value / maxValue) * 90 - 12;
      return `${x},${y}`;
    })
    .join(" ");

  const labels = selected
    .map(
      (lane, index) => `
        <div class="telemetry-legend-item">
          <span>${escapeHtml(lane.name)}</span>
          <strong>${values[index]}</strong>
        </div>
      `,
    )
    .join("");

  telemetryChart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" class="sparkline" role="img" aria-label="Lane blocker pressure">
      <defs>
        <linearGradient id="spark" x1="0%" x2="100%" y1="0%" y2="0%">
          <stop offset="0%" stop-color="#4dff9a" />
          <stop offset="100%" stop-color="#d5ff52" />
        </linearGradient>
      </defs>
      <polyline points="${points}" fill="none" stroke="url(#spark)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></polyline>
      ${values
        .map((value, index) => {
          const x = values.length === 1 ? width / 2 : index * step;
          const y = height - (value / maxValue) * 90 - 12;
          return `<circle cx="${x}" cy="${y}" r="4.5" fill="#08110d" stroke="#4dff9a" stroke-width="2"></circle>`;
        })
        .join("")}
    </svg>
    <div class="telemetry-legend">${labels}</div>
  `;
}

function appendChatMessage(role, text, evidence = [], meta = "") {
  const wrapper = document.createElement("article");
  wrapper.className = `chat-message ${role}`;
  wrapper.innerHTML = `
    <div class="chat-message-head">
      <strong>${role === "user" ? "You" : "Ops Copilot"}</strong>
      ${meta ? `<span>${escapeHtml(meta)}</span>` : ""}
    </div>
    <p>${escapeHtml(text)}</p>
    ${
      evidence.length
        ? `<div class="chat-evidence">${evidence
            .map(
              (item) => `
                <a href="${escapeHtml(item.url || "#")}" ${item.url ? 'target="_blank" rel="noreferrer"' : ""}>
                  <span>${escapeHtml(item.source)}</span>
                  <strong>${escapeHtml(item.label)}</strong>
                </a>
              `,
            )
            .join("")}</div>`
        : ""
    }
  `;
  chatLog.appendChild(wrapper);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function seedChat() {
  if (chatLog.childElementCount) return;
  appendChatMessage(
    "assistant",
    "Ask about client blockers, competitive gaps, AUM schema readiness, or which APIs are still missing to make SWFI a full delivery product.",
    [],
    "Read-only analysis",
  );
}

async function runCopilot(query) {
  if (!query.trim()) return;

  appendChatMessage("user", query);
  appendChatMessage("assistant", "Pulling proposal, concern-sheet, benchmark, and API context...", [], "Source packet");

  try {
    const response = await fetch(`/api/research?q=${encodeURIComponent(query)}`);
    const payload = await response.json();
    const placeholder = chatLog.lastElementChild;
    if (placeholder?.classList.contains("assistant")) {
      placeholder.remove();
    }
    appendChatMessage(
      "assistant",
      payload.answer,
      payload.evidence || [],
      payload.model ? `${payload.model} · source-grounded` : "Deterministic fallback",
    );
  } catch (error) {
    const placeholder = chatLog.lastElementChild;
    if (placeholder?.classList.contains("assistant")) {
      placeholder.remove();
    }
    appendChatMessage(
      "assistant",
      "The ops copilot did not return cleanly. The dashboard data is still loaded, but the synthesis step failed.",
      [],
      "Fallback",
    );
    console.error(error);
  }
}

function renderAll() {
  if (!state.dashboard) return;
  renderStatusStrip();
  renderMetricGrid();
  renderLaneSelectors();
  renderProposalBrief();
  renderReferenceGrid();
  renderCollections();
  renderLaneList();
  renderActionList();
  renderConcernList();
  renderApiSurface();
  renderReadiness();
  renderBenchmarkPanel();
  renderTelemetryChart();
  lastRefresh.textContent = formatRelativeDate(state.dashboard.generated_at);
  seedChat();
}

async function loadDashboard() {
  const response = await fetch("/api/dashboard");
  if (!response.ok) {
    throw new Error(`dashboard ${response.status}`);
  }
  state.dashboard = await response.json();
  renderAll();
}

concernSearch?.addEventListener("input", (event) => {
  state.query = event.target.value || "";
  renderConcernList();
});

chatForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  const query = chatInput.value || "";
  if (!query.trim()) return;
  chatInput.value = "";
  runCopilot(query);
});

document.querySelectorAll("[data-chat-suggestion]").forEach((button) => {
  button.addEventListener("click", () => runCopilot(button.dataset.chatSuggestion || ""));
});

loadDashboard().catch((error) => {
  console.error(error);
  statusStrip.innerHTML = `
    <article class="status-pill tone-blocked">
      <strong>Dashboard</strong>
      <span>Failed to load the SWFI packet</span>
    </article>
  `;
});
