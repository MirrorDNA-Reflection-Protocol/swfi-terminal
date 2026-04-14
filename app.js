const modules = [
  {
    id: "capital-flows",
    label: "Capital Flows",
    eyebrow: "Capital markets desk",
    title: "Track sovereign and institutional capital with a fund-raising lens.",
    copy:
      "This module is for teams that care about where large pools of capital are moving, how mandates are shifting, and which institutions belong on the active coverage list.",
    metrics: ["Flow signals", "Coverage-ready dossiers", "Named-account routing"],
    checklist: [
      "Keep capital pools at the center of the experience.",
      "Route signal flow into named accounts and target institutions.",
      "Make the interface feel premium enough to justify a paid product.",
    ],
  },
  {
    id: "coverage-desk",
    label: "Coverage Desk",
    eyebrow: "Wall Street workflow",
    title: "Give relationship, strategy, and placement teams one shared coverage workspace.",
    copy:
      "The best SWFI wedge is not a generic dashboard. It is a live coverage desk with institution profiles, decision context, public-source signals, and fast scanning for who matters this week.",
    metrics: ["Account coverage", "Decision context", "Fast morning scan"],
    checklist: [
      "Pull profiles, market signals, and mandate context into one view.",
      "Preserve source trails so the desk is trusted, not decorative.",
      "Optimize for relationship and origination teams, not just researchers.",
    ],
  },
  {
    id: "mandate-radar",
    label: "Mandate Radar",
    eyebrow: "Origination desk",
    title: "Surface mandate, strategy, and account movement faster than a static research portal.",
    copy:
      "This is the origination angle: where strategy changes, manager searches, capital formation, and opportunity signals should become visible before they get lost in a generic news flow.",
    metrics: ["Mandate shifts", "Opportunity signals", "Strategy movement"],
    checklist: [
      "Translate raw activity into actionable coverage signals.",
      "Make the desk useful to IR, placement, and product strategy teams.",
      "Use source-backed signals instead of fake terminal noise.",
    ],
  },
  {
    id: "profile-ops",
    label: "Profile Ops",
    eyebrow: "Operating desk",
    title: "Turn profile maintenance into a visible workflow instead of a manual request queue.",
    copy:
      "The live SWFI product already has the core records. The weak spot is operational: freshness, review, and ownership. This module shows how to make that a real queue without waiting for a total rebuild.",
    metrics: ["Claim queue", "Evidence review", "Publish control"],
    checklist: [
      "Open a structured write path only where it improves trust.",
      "Keep analyst review visible and auditable.",
      "Let profile operations feed the product instead of sitting behind it.",
    ],
  },
];

const audienceCards = [
  {
    title: "Private capital platforms",
    body: "Need a premium desk for sovereign coverage, capital formation, and strategic relationship mapping.",
  },
  {
    title: "Wall Street coverage teams",
    body: "Need an institutional market-data workspace, not a generic research site or slow vendor portal.",
  },
  {
    title: "Strategy and placement desks",
    body: "Need faster visibility into mandates, manager searches, and account movement across large pools of capital.",
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
    note: "The strongest live SWFI profile to anchor a premium institutional-capital dossier.",
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
      "Policy changes and exclusions are high-value coverage signals.",
      "Real-asset activity should route into capital-formation desks immediately.",
      "Freshness improvements on this profile create obvious subscriber value.",
    ],
    workflow: [
      "Use the profile as the anchor for relationship, mandate, and opportunity context.",
      "Attach updates to a structured claim and review queue.",
      "Push approved changes into named-account watchlists.",
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
    note: "A high-value sovereign account that belongs in a premium institutional-capital desk, not a mixed institutional dump.",
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
      "Coverage desks need mandate and relationship context beside the profile.",
      "Any capital movement should feed named Asia sovereign watchlists.",
      "The premium value is in making these accounts easy to monitor quickly.",
    ],
    workflow: [
      "Keep the account visible in sovereign-first mode.",
      "Connect people, opportunities, and strategy changes to the same desk.",
      "Treat freshness as part of the commercial product, not just operations.",
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
    note: "A natural fit for target-account coverage, mandate tracking, and strategy team workflows.",
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
      "Decision-maker movement and strategy change belong in one account view.",
      "Signal routing should prioritize relationship and origination teams.",
      "This is where SWFI can outperform a generic research portal quickly.",
    ],
    workflow: [
      "Keep account coverage active, not archival.",
      "Use named-account watchlists to power the morning scan.",
      "Surface opportunities and account movement in the same workspace.",
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
    note: "An important institutional record, but it belongs in a reserve-manager lane rather than mixed blindly into sovereign coverage.",
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
      "Reserve signals matter, but the desk needs family-aware segmentation.",
      "Macro-relevant entities should be visible without cluttering sovereign coverage.",
      "This is a good proof point for why the filtering layer matters commercially.",
    ],
    workflow: [
      "Preserve the record but place it in the right desk by default.",
      "Use a consistent dossier format across families.",
      "Make segmentation a user-facing advantage.",
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
    note: "A useful record for context, but exactly the kind of result that should not dominate a sovereign and institutional capital workspace by default.",
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
      "This is useful context, not a default capital-pool result.",
      "Keeping it searchable but hidden by default is a strong demo moment.",
      "Commercial users should feel that the desk understands scope immediately.",
    ],
    workflow: [
      "Keep power-user access without cluttering the main desk.",
      "Use design and defaults to reinforce the right workflow.",
      "Make scope control visible and deliberate.",
    ],
  },
];

const watchlists = [
  {
    name: "Asia Sovereign Coverage",
    cadence: "Daily open",
    logic: "State capital + Asia + profile change + strategy movement + verified signals",
  },
  {
    name: "Mandate Radar",
    cadence: "Morning sweep",
    logic: "Signals that suggest manager search, allocation shift, or relationship opportunity",
  },
  {
    name: "Street Coverage",
    cadence: "Intraday",
    logic: "Blackstone, KKR, Apollo, Brookfield, BlackRock filing pulse and public-source signal flow",
  },
];

const opsSteps = [
  {
    step: "01",
    title: "Claim",
    body: "Profile owners or internal operators claim the record instead of sending blind update requests.",
  },
  {
    step: "02",
    title: "Evidence",
    body: "Every proposed change carries a source, document, or verified decision-maker context.",
  },
  {
    step: "03",
    title: "Review",
    body: "An analyst queue assigns freshness, confidence, and publish state before the change goes live.",
  },
  {
    step: "04",
    title: "Publish",
    body: "Approved changes flow back into account desks, signal feeds, and watchlists automatically.",
  },
];

const wins = [
  {
    title: "The desk feels expensive in the right way.",
    body: "It reads like a premium market-data product instead of a generic portal or internal tool.",
  },
  {
    title: "It uses live public sources immediately.",
    body: "SEC, World Bank, USAspending, and optional GDELT enrichment make the pilot feel connected without a big procurement cycle.",
  },
  {
    title: "It sells to Wall Street workflows.",
    body: "Coverage, mandate intelligence, capital flows, and named-account tracking are visible on the page.",
  },
  {
    title: "It stays believable.",
    body: "The pilot is honest about where data is seeded from SWFI and where it is pulled live from free public APIs.",
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
    sources: ["Local pilot server"],
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
const audienceList = document.getElementById("audience-list");
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
const watchlistList = document.getElementById("watchlist-list");
const opsStepsEl = document.getElementById("ops-steps");
const winList = document.getElementById("win-list");
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

function renderAudience() {
  audienceList.innerHTML = audienceCards
    .map(
      (card) => `
        <article class="audience-card">
          <strong>${card.title}</strong>
          <p>${card.body}</p>
        </article>
      `,
    )
    .join("");
}

function renderSourceHealth() {
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
      <strong>${role === "user" ? "You" : "Research Copilot"}</strong>
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
    "Ask about Blackstone, KKR, Apollo, Brookfield, sovereign accounts, macro context, or mandate movement. This desk stays read-only and answers from the live SEC, World Bank, USAspending, and public-source feed layer wired into the pilot.",
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
      note: "USAspending and public-source enrichment feeding the pilot",
      tone: "cyan",
    },
    {
      label: "Ops path",
      value: "Claimed",
      note: "Claim, evidence, review, publish",
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

function renderWatchlists() {
  watchlistList.innerHTML = watchlists
    .map(
      (item) => `
        <article class="watch-card">
          <div class="watch-head">
            <strong>${item.name}</strong>
            <span>${item.cadence}</span>
          </div>
          <p>${item.logic}</p>
        </article>
      `,
    )
    .join("");
}

function renderOps() {
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

function renderWins() {
  winList.innerHTML = wins
    .map(
      (item) => `
        <article class="win-card">
          <strong>${item.title}</strong>
          <p>${item.body}</p>
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

renderAudience();
renderModules();
renderFamilyFilters();
renderEntitiesAndDossier();
renderModuleSpotlight();
renderWatchlists();
renderOps();
renderWins();
syncModuleButtons();
renderMetricStrip();
renderSourceHealth();
renderSignalBoard();
renderFeed();
renderFilings();
renderMacro();
seedChat();
loadLiveData();
