const modules = [
  {
    id: "capital-flows",
    label: "Capital Flows",
    eyebrow: "Flow monitor",
    title: "Where capital is moving across sovereign and institutional accounts.",
    copy:
      "Focus on pool size, account changes, and fresh signals that move a coverage list.",
    metrics: ["Flow signals", "Account tiers", "Watchlist routing"],
    checklist: [
      "Keep allocators first.",
      "Route signals into accounts.",
      "Cut general-market noise.",
    ],
  },
  {
    id: "coverage-desk",
    label: "Coverage Desk",
    eyebrow: "Coverage monitor",
    title: "One book for institutions, people, signals, and profile state.",
    copy:
      "Use the desk to move from search to account view without leaving the workspace.",
    metrics: ["Account coverage", "People context", "Morning scan"],
    checklist: [
      "Keep the book live.",
      "Show the source trail.",
      "Stay account-centric.",
    ],
  },
  {
    id: "mandate-radar",
    label: "Mandate Radar",
    eyebrow: "Signal monitor",
    title: "Mandate movement, strategy shifts, and search signals.",
    copy:
      "Pull headlines, filings, and public-source movement into one read path.",
    metrics: ["Mandate shifts", "Search signals", "Strategy moves"],
    checklist: [
      "Turn noise into account signals.",
      "Keep signals short.",
      "Stay source-backed.",
    ],
  },
  {
    id: "profile-ops",
    label: "Profile Ops",
    eyebrow: "Queue monitor",
    title: "Claims, evidence, review, and publish state.",
    copy:
      "Keep profile change visible instead of burying it behind request forms.",
    metrics: ["Claim queue", "Evidence review", "Publish state"],
    checklist: [
      "Keep ownership visible.",
      "Review before publish.",
      "Feed changes back into the desk.",
    ],
  },
];

const entities = [
  {
    id: "gpfg",
    name: "Norway Government Pension Fund Global",
    family: "State capital",
    rawType: "Sovereign Wealth Fund",
    country: "Norway",
    region: "Europe",
    assets: "$2.117T",
    allocator: true,
    deskFit: "Flagship sovereign account",
    note: "Flagship sovereign account. Real assets, exclusions, and policy signals matter.",
    lastSeen: "Current SWFI entity profile",
    freshness: "Observed 14 Apr 2026",
    status: "Profile verified",
    facts: [
      ["Legal name", "Norges Bank Investment Management"],
      ["Desk label", "Flagship sovereign account"],
      ["Transparency", "10 / 10"],
      ["Alt assets", "Real Estate, Infrastructure, Hedge Funds"],
      ["Established", "01 Jan 1990"],
      ["Desk priority", "Coverage tier 1"],
    ],
    sources: ["SWFI profile page", "nbim.no", "Analyst-ready dossier"],
    signals: [
      "Watch policy changes and exclusions.",
      "Route real-asset activity into the live list.",
      "Treat freshness as part of coverage quality.",
    ],
    workflow: [
      "Anchor the sovereign book here.",
      "Push updates into review.",
      "Feed changes into watchlists.",
    ],
  },
  {
    id: "safe",
    name: "SAFE Investment Company",
    family: "State capital",
    rawType: "Sovereign Wealth Fund",
    country: "China",
    region: "Asia",
    assets: "$1.952T",
    allocator: true,
    deskFit: "Core Asia sovereign coverage",
    note: "Core Asia sovereign. Keep it in the top coverage lane.",
    lastSeen: "Current SWFI entity search",
    freshness: "Observed 14 Apr 2026",
    status: "Search verified",
    facts: [
      ["Country", "China"],
      ["Desk label", "Core Asia sovereign coverage"],
      ["Raw type", "Sovereign Wealth Fund"],
      ["Region", "Asia"],
      ["Visible assets", "$1.952T"],
      ["Desk priority", "Coverage tier 1"],
    ],
    sources: ["SWFI entity search", "Coverage explorer"],
    signals: [
      "Keep mandate context beside the profile.",
      "Route movement into Asia watchlists.",
      "Make the account fast to scan.",
    ],
    workflow: [
      "Keep it visible in allocator mode.",
      "Connect people and strategy changes.",
      "Review freshness continuously.",
    ],
  },
  {
    id: "cic",
    name: "China Investment Corporation",
    family: "State capital",
    rawType: "Sovereign Wealth Fund",
    country: "China",
    region: "Asia",
    assets: "$1.567T",
    allocator: true,
    deskFit: "Named-account priority",
    note: "Named account. Track strategy shifts and decision-maker movement.",
    lastSeen: "Current SWFI entity search",
    freshness: "Observed 14 Apr 2026",
    status: "Search verified",
    facts: [
      ["Country", "China"],
      ["Desk label", "Named-account priority"],
      ["Raw type", "Sovereign Wealth Fund"],
      ["Region", "Asia"],
      ["Visible assets", "$1.567T"],
      ["Desk priority", "Coverage tier 1"],
    ],
    sources: ["SWFI entity search", "Coverage workflow"],
    signals: [
      "Keep people moves with strategy shifts.",
      "Route signals into the live book.",
      "Make the account easy to revisit.",
    ],
    workflow: [
      "Keep the account live, not archival.",
      "Use the watchlist for morning scan.",
      "Keep opportunities in the same view.",
    ],
  },
  {
    id: "fed",
    name: "Federal Reserve System",
    family: "Reserve manager",
    rawType: "Central Bank",
    country: "United States",
    region: "North America",
    assets: "$7.113T",
    allocator: true,
    deskFit: "Reserve and macro desk",
    note: "Important context record. Keep it in the reserve lane, not the sovereign lane.",
    lastSeen: "Current SWFI entity search",
    freshness: "Observed 14 Apr 2026",
    status: "Search verified",
    facts: [
      ["Country", "United States"],
      ["Desk label", "Reserve and macro desk"],
      ["Raw type", "Central Bank"],
      ["Region", "North America"],
      ["Visible assets", "$7.113T"],
      ["Desk priority", "Context tier 1"],
    ],
    sources: ["SWFI entity search", "Capital-pool filter"],
    signals: [
      "Reserve signals matter.",
      "Keep macro context visible without clutter.",
      "Segmentation should stay obvious.",
    ],
    workflow: [
      "Keep the record in the right lane.",
      "Use the same dossier format.",
      "Let filters do the sorting.",
    ],
  },
  {
    id: "jpm",
    name: "JPMorgan Chase & Co",
    family: "Out of scope",
    rawType: "Financial Holding Company",
    country: "United States",
    region: "North America",
    assets: "$4.425T",
    allocator: false,
    deskFit: "Context only",
    note: "Useful context. Not a default allocator result.",
    lastSeen: "Current SWFI entity search",
    freshness: "Observed 14 Apr 2026",
    status: "Filtered by default",
    facts: [
      ["Country", "United States"],
      ["Desk label", "Context only"],
      ["Raw type", "Financial Holding Company"],
      ["Region", "North America"],
      ["Visible assets", "$4.425T"],
      ["Desk priority", "Background only"],
    ],
    sources: ["SWFI entity search", "Capital-pool mode"],
    signals: [
      "Keep it searchable.",
      "Hide it by default in allocator mode.",
      "Scope should feel obvious.",
    ],
    workflow: [
      "Preserve power-user access.",
      "Keep the main desk clean.",
      "Make scope control visible.",
    ],
  },
];

const opsSteps = [
  {
    step: "01",
    title: "Claim",
    body: "Assign ownership to the record.",
  },
  {
    step: "02",
    title: "Evidence",
    body: "Attach sources to each proposed change.",
  },
  {
    step: "03",
    title: "Review",
    body: "Review freshness and publish state.",
  },
  {
    step: "04",
    title: "Publish",
    body: "Push approved changes back into the desk.",
  },
];

const fallbackLiveData = {
  generated_at: null,
  statuses: [
    { source: "SEC", status: "loading", note: "Pulling filings" },
    { source: "World Bank", status: "loading", note: "Pulling macro context" },
    { source: "USAspending", status: "loading", note: "Pulling public-sector matches" },
    { source: "GDELT", status: "loading", note: "Pulling signal feed" },
  ],
  filings: [],
  macro: [],
  recipients: [],
  feed: [],
};

const fallbackFeedItems = [
  {
    state: "Seeded",
    title: "Coverage feed will populate from live public sources once the local API layer returns.",
    summary: "The desk prefers live SEC, World Bank, USAspending, and optional GDELT responses over static filler.",
    sources: ["Local source layer"],
  },
];

const state = {
  activeModule: "capital-flows",
  activeEntityId: "gpfg",
  query: "",
  allocatorOnly: true,
  family: "All",
  liveData: fallbackLiveData,
};

const metricStrip = document.getElementById("metric-strip");
const sourceHealthList = document.getElementById("source-health-list");
const moduleList = document.getElementById("module-list");
const signalGrid = document.getElementById("signal-grid");
const coverageList = document.getElementById("coverage-list");
const commandSearch = document.getElementById("command-search");
const entitySearch = document.getElementById("entity-search");
const allocatorToggle = document.getElementById("allocator-toggle");
const familyFilters = document.getElementById("family-filters");
const entityList = document.getElementById("entity-list");
const dossierTop = document.getElementById("dossier-top");
const factGrid = document.getElementById("fact-grid");
const signalList = document.getElementById("signal-list");
const workflowList = document.getElementById("workflow-list");
const sourceStrip = document.getElementById("source-strip");
const moduleMeta = document.getElementById("module-meta");
const moduleTitle = document.getElementById("module-title");
const moduleCopy = document.getElementById("module-copy");
const moduleMetrics = document.getElementById("module-metrics");
const moduleChecklist = document.getElementById("module-checklist");
const feedList = document.getElementById("feed-list");
const filingsList = document.getElementById("filings-list");
const macroList = document.getElementById("macro-list");
const opsStepsEl = document.getElementById("ops-steps");
const lastRefresh = document.getElementById("last-refresh");
const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");

const familyOptions = ["All", ...new Set(entities.map((entity) => entity.family))];

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatRelativeDate(isoString) {
  if (!isoString) return "Not refreshed";
  const deltaMs = Date.now() - new Date(isoString).getTime();
  const minutes = Math.max(1, Math.round(deltaMs / 60000));
  if (minutes < 60) return `Refreshed ${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  return `Refreshed ${hours}h ago`;
}

function renderMetricStrip() {
  const statuses = state.liveData.statuses || [];
  const okCount = statuses.filter((item) => item.status === "ok").length;
  const gdeltState = statuses.find((item) => item.source === "GDELT")?.status ?? "unknown";

  const metricCards = [
    {
      label: "Live sources",
      value: `${okCount}/${statuses.length || 4}`,
      note: "Public APIs currently responding to the desk",
    },
    {
      label: "Street filings",
      value: String((state.liveData.filings || []).length || 0),
      note: "Latest SEC filing pulse for key public managers",
    },
    {
      label: "Macro countries",
      value: String((state.liveData.macro || []).length || 0),
      note: "World Bank GDP context for core sovereign markets",
    },
    {
      label: "Signal feed",
      value: gdeltState === "ok" ? "Live" : gdeltState === "rate_limited" ? "Fallback" : "Seeded",
      note: "Public-source feed with graceful fallback when rate-limited",
    },
  ];

  metricStrip.innerHTML = metricCards
    .map(
      (card) => `
        <article class="metric-card">
          <span class="metric-label">${card.label}</span>
          <strong>${card.value}</strong>
          <p>${card.note}</p>
        </article>
      `,
    )
    .join("");
}

function renderSourceHealth() {
  if (!sourceHealthList) return;
  const statuses = state.liveData.statuses || [];
  sourceHealthList.innerHTML = statuses
    .map(
      (item) => `
        <article class="source-health-card tone-${item.status}">
          <div class="source-health-head">
            <strong>${item.source}</strong>
            <span>${item.status}</span>
          </div>
          <p>${item.note}</p>
        </article>
      `,
    )
    .join("");
}

function appendChatMessage(role, text, evidence = [], meta = "") {
  if (!chatLog) return;

  const wrapper = document.createElement("article");
  wrapper.className = `chat-message ${role}`;
  wrapper.innerHTML = `
    <div class="chat-message-head">
      <strong>${role === "user" ? "You" : "Research Desk"}</strong>
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
  if (!chatLog || chatLog.childElementCount) return;
  appendChatMessage(
    "assistant",
    "Ask about Blackstone, KKR, Apollo, Brookfield, sovereign accounts, macro context, or mandate movement. The desk stays read-only and answers from the live source stack.",
    [],
    "Research only",
  );
}

function renderSignalBoard() {
  const recipientCount = (state.liveData.recipients || []).reduce((total, item) => total + (item.count || 0), 0);
  const filingPulse = state.liveData.filings?.[0]?.form ?? "n/a";

  const signalTiles = [
    {
      label: "Coverage mode",
      value: "Capital pools",
      note: "Sovereign and institutional capital ranked above generic finance noise",
      tone: "teal",
    },
    {
      label: "Street pulse",
      value: filingPulse,
      note: "Latest live SEC form across the tracked public managers",
      tone: "amber",
    },
    {
      label: "Public-source matches",
      value: recipientCount ? String(recipientCount) : "Warm",
      note: "USAspending and public-source coverage",
      tone: "cyan",
    },
    {
      label: "Ops path",
      value: "Claimed",
      note: "Claim, review, publish",
      tone: "rose",
    },
  ];

  const coverageRows = [
    { label: "State capital", width: 95, note: "Core target universe", tone: "teal" },
    { label: "Reserve managers", width: 72, note: "Segmented but visible", tone: "cyan" },
    { label: "Mandate radar", width: 84, note: "Origination-first signal flow", tone: "amber" },
    { label: "Street coverage", width: 88, note: "Blackstone, KKR, Apollo, Brookfield, BlackRock", tone: "amber" },
    { label: "Commercial finance noise", width: 34, note: "Hidden unless widened intentionally", tone: "rose" },
  ];

  signalGrid.innerHTML = signalTiles
    .map(
      (tile) => `
        <article class="signal-tile tone-${tile.tone}">
          <span class="signal-label">${tile.label}</span>
          <strong>${tile.value}</strong>
          <p>${tile.note}</p>
        </article>
      `,
    )
    .join("");

  coverageList.innerHTML = coverageRows
    .map(
      (row) => `
        <article class="coverage-row">
          <div class="coverage-head">
            <strong>${row.label}</strong>
            <span>${row.note}</span>
          </div>
          <div class="coverage-bar tone-${row.tone}">
            <span style="width:${row.width}%"></span>
          </div>
        </article>
      `,
    )
    .join("");
}

function syncModuleButtons() {
  document.querySelectorAll("[data-module-target]").forEach((button) => {
    button.classList.toggle("active", button.dataset.moduleTarget === state.activeModule);
  });
}

function setModule(moduleId) {
  state.activeModule = moduleId;
  renderModules();
  renderModuleSpotlight();
  syncModuleButtons();
}

function renderModules() {
  if (!moduleList) return;
  moduleList.innerHTML = modules
    .map(
      (module) => `
        <button
          class="module-card ${module.id === state.activeModule ? "active" : ""}"
          type="button"
          data-module-id="${module.id}"
        >
          <span class="module-eyebrow">${module.eyebrow}</span>
          <strong>${module.label}</strong>
          <p>${module.title}</p>
        </button>
      `,
    )
    .join("");

  moduleList.querySelectorAll("[data-module-id]").forEach((button) => {
    button.addEventListener("click", () => setModule(button.dataset.moduleId));
  });
}

function renderModuleSpotlight() {
  if (!moduleMeta || !moduleTitle || !moduleCopy || !moduleMetrics || !moduleChecklist) return;
  const module = modules.find((item) => item.id === state.activeModule);
  if (!module) return;

  moduleMeta.innerHTML = `<span class="spotlight-chip">${module.eyebrow}</span><span class="spotlight-chip">${module.label}</span>`;
  moduleTitle.textContent = module.title;
  moduleCopy.textContent = module.copy;
  moduleMetrics.innerHTML = module.metrics.map((item) => `<span class="metric-pill">${item}</span>`).join("");
  moduleChecklist.innerHTML = module.checklist
    .map(
      (item) => `
        <article class="check-item">
          <span class="check-mark">OK</span>
          <p>${item}</p>
        </article>
      `,
    )
    .join("");
}

function getFilteredEntities() {
  const query = state.query.trim().toLowerCase();

  return entities.filter((entity) => {
    const matchesAllocator = state.allocatorOnly ? entity.allocator : true;
    const matchesFamily = state.family === "All" ? true : entity.family === state.family;
    const haystack = [
      entity.name,
      entity.country,
      entity.region,
      entity.rawType,
      entity.family,
      entity.deskFit,
    ]
      .join(" ")
      .toLowerCase();
    const matchesQuery = query ? haystack.includes(query) : true;

    return matchesAllocator && matchesFamily && matchesQuery;
  });
}

function ensureActiveEntity(filtered) {
  if (!filtered.length) {
    state.activeEntityId = "";
    return;
  }

  if (!filtered.some((entity) => entity.id === state.activeEntityId)) {
    state.activeEntityId = filtered[0].id;
  }
}

function renderFamilyFilters() {
  familyFilters.innerHTML = familyOptions
    .map(
      (family) => `
        <button
          class="filter-btn ${family === state.family ? "active" : ""}"
          type="button"
          data-family="${family}"
        >
          ${family}
        </button>
      `,
    )
    .join("");

  familyFilters.querySelectorAll("[data-family]").forEach((button) => {
    button.addEventListener("click", () => {
      state.family = button.dataset.family;
      renderEntitiesAndDossier();
      renderFamilyFilters();
    });
  });
}

function renderEntitiesAndDossier() {
  const filtered = getFilteredEntities();
  ensureActiveEntity(filtered);

  if (!filtered.length) {
    entityList.innerHTML = `
      <article class="empty-state">
        <strong>No entities match the current desk filters.</strong>
        <p>Widen the family filter or turn capital-pool-only mode off.</p>
      </article>
    `;
    dossierTop.innerHTML = "";
    factGrid.innerHTML = "";
    signalList.innerHTML = "";
    workflowList.innerHTML = "";
    sourceStrip.innerHTML = "";
    return;
  }

  entityList.innerHTML = filtered
    .map(
      (entity) => `
        <button
          class="entity-card ${entity.id === state.activeEntityId ? "active" : ""}"
          type="button"
          data-entity-id="${entity.id}"
        >
          <div class="entity-head">
            <div>
              <strong>${entity.name}</strong>
              <p>${entity.country} · ${entity.region}</p>
            </div>
            <span class="family-badge">${entity.family}</span>
          </div>
          <div class="entity-metrics">
            <span><strong>Raw type</strong><em>${entity.rawType}</em></span>
            <span><strong>Assets</strong><em>${entity.assets}</em></span>
            <span><strong>Desk fit</strong><em>${entity.deskFit}</em></span>
          </div>
          <p class="entity-note">${entity.note}</p>
        </button>
      `,
    )
    .join("");

  entityList.querySelectorAll("[data-entity-id]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeEntityId = button.dataset.entityId;
      renderEntitiesAndDossier();
    });
  });

  const entity = entities.find((item) => item.id === state.activeEntityId);
  if (!entity) return;

  dossierTop.innerHTML = `
    <div class="dossier-heading">
      <p class="eyebrow">Selected account</p>
      <h3>${entity.name}</h3>
      <p class="dossier-copy">${entity.note}</p>
    </div>
    <div class="dossier-badges">
      <span class="metric-pill">${entity.family}</span>
      <span class="metric-pill">${entity.rawType}</span>
      <span class="metric-pill">${entity.status}</span>
      <span class="metric-pill">${entity.freshness}</span>
    </div>
  `;

  factGrid.innerHTML = entity.facts
    .map(
      ([label, value]) => `
        <article class="fact-card">
          <span>${label}</span>
          <strong>${value}</strong>
        </article>
      `,
    )
    .join("");

  signalList.innerHTML = entity.signals
    .map(
      (item, index) => `
        <article class="list-item">
          <span class="list-mark">${String(index + 1).padStart(2, "0")}</span>
          <p>${item}</p>
        </article>
      `,
    )
    .join("");

  workflowList.innerHTML = entity.workflow
    .map(
      (item, index) => `
        <article class="list-item">
          <span class="list-mark">${String(index + 1).padStart(2, "0")}</span>
          <p>${item}</p>
        </article>
      `,
    )
    .join("");

  sourceStrip.innerHTML = `
    <div class="source-head">
      <div>
        <p class="eyebrow">Source trail</p>
        <strong>${entity.lastSeen}</strong>
      </div>
      <span class="status-pill">${entity.freshness}</span>
    </div>
    <div class="source-pills">
      ${entity.sources.map((source) => `<span class="source-pill">${source}</span>`).join("")}
    </div>
  `;
}

function renderFeed() {
  const items = (state.liveData.feed && state.liveData.feed.length ? state.liveData.feed : fallbackFeedItems).slice(0, 6);
  feedList.innerHTML = items
    .map(
      (item) => `
        <article class="feed-card">
          <div class="feed-head">
            <span class="state-pill">${item.state}</span>
            <span class="feed-date">${item.date || "Observed live"}</span>
          </div>
          <strong>${item.title}</strong>
          <p>${item.summary}</p>
          <div class="source-pills">
            ${(item.sources || []).map((source) => `<span class="source-pill">${source}</span>`).join("")}
          </div>
        </article>
      `,
    )
    .join("");
}

function renderFilings() {
  const filings = state.liveData.filings || [];
  filingsList.innerHTML = filings
    .map(
      (item) => `
        <article class="filing-card">
          <div class="filing-head">
            <strong>${item.ticker}</strong>
            <span>${item.date}</span>
          </div>
          <p>${item.name}</p>
          <div class="filing-meta">
            <span class="metric-pill">${item.form}</span>
            <a href="${item.url}" target="_blank" rel="noreferrer">Open filing</a>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderMacro() {
  const macro = state.liveData.macro || [];
  macroList.innerHTML = macro
    .map(
      (item) => `
        <article class="macro-card">
          <div class="macro-head">
            <strong>${item.country}</strong>
            <span>${item.date}</span>
          </div>
          <p>${item.label}</p>
          <strong class="macro-value">${item.display_value}</strong>
        </article>
      `,
    )
    .join("");
}

function renderOps() {
  if (!opsStepsEl) return;
  opsStepsEl.innerHTML = opsSteps
    .map(
      (item) => `
        <article class="ops-card">
          <span class="ops-step">${item.step}</span>
          <div>
            <strong>${item.title}</strong>
            <p>${item.body}</p>
          </div>
        </article>
      `,
    )
    .join("");
}

function setQuery(value) {
  state.query = value;
  if (commandSearch && commandSearch.value !== value) {
    commandSearch.value = value;
  }
  if (entitySearch && entitySearch.value !== value) {
    entitySearch.value = value;
  }
  renderEntitiesAndDossier();
}

async function loadLiveData() {
  try {
    const response = await fetch("/api/dashboard");
    if (!response.ok) {
      throw new Error(`dashboard ${response.status}`);
    }
    state.liveData = await response.json();
  } catch (error) {
    console.error("live data unavailable", error);
    state.liveData = {
      ...fallbackLiveData,
      statuses: fallbackLiveData.statuses.map((item) => ({
        ...item,
        status: "fallback",
        note: "Using local fallback because live fetch failed",
      })),
    };
  }

  renderMetricStrip();
  renderSourceHealth();
  renderSignalBoard();
  renderFeed();
  renderFilings();
  renderMacro();
  if (lastRefresh) {
    lastRefresh.textContent = formatRelativeDate(state.liveData.generated_at);
  }
}

async function runResearch(query) {
  if (!query.trim()) return;

  appendChatMessage("user", query);
  appendChatMessage("assistant", "Running source-backed research...", [], "Live pull");

  try {
    const response = await fetch(`/api/research?q=${encodeURIComponent(query)}`);
    const payload = await response.json();
    const placeholder = chatLog?.lastElementChild;
    if (placeholder?.classList.contains("assistant")) {
      placeholder.remove();
    }
    const assistantMeta = payload.guardrail === "scope_limited"
      ? "Research only"
      : payload.model
        ? `${payload.model} · source-backed`
        : "Source packet";
    appendChatMessage("assistant", payload.answer, payload.evidence || [], assistantMeta);
  } catch (error) {
    const placeholder = chatLog?.lastElementChild;
    if (placeholder?.classList.contains("assistant")) {
      placeholder.remove();
    }
    appendChatMessage(
      "assistant",
      "The research layer did not return cleanly. SEC and macro endpoints are wired, but this answer fell back before synthesis completed.",
      [],
      "Fallback",
    );
    console.error("research failed", error);
  }
}

document.querySelectorAll("[data-module-target]").forEach((button) => {
  button.addEventListener("click", () => setModule(button.dataset.moduleTarget));
});

commandSearch?.addEventListener("input", (event) => {
  setQuery(event.target.value);
});

entitySearch?.addEventListener("input", (event) => {
  setQuery(event.target.value);
});

allocatorToggle?.addEventListener("change", (event) => {
  state.allocatorOnly = event.target.checked;
  renderEntitiesAndDossier();
});

chatForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  const query = chatInput?.value || "";
  if (!query.trim()) return;
  chatInput.value = "";
  runResearch(query);
});

document.querySelectorAll("[data-chat-suggestion]").forEach((button) => {
  button.addEventListener("click", () => {
    const query = button.dataset.chatSuggestion || "";
    if (chatInput) {
      chatInput.value = "";
    }
    runResearch(query);
  });
});

renderModules();
renderFamilyFilters();
renderEntitiesAndDossier();
renderModuleSpotlight();
renderOps();
syncModuleButtons();
renderMetricStrip();
renderSourceHealth();
renderSignalBoard();
renderFeed();
renderFilings();
renderMacro();
seedChat();
loadLiveData();
