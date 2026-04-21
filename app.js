/* SWFI Intelligence Terminal */

const TOP_FUNDS = [
  { rank: "01", name: "Government Pension Fund Global", code: "GPFG", country: "Norway", flag: "🇳🇴", aum: "$1.7T" },
  { rank: "02", name: "China Investment Corporation", code: "CIC", country: "China", flag: "🇨🇳", aum: "$1.35T" },
  { rank: "03", name: "Abu Dhabi Investment Authority", code: "ADIA", country: "UAE", flag: "🇦🇪", aum: "$993B" },
  { rank: "04", name: "Public Investment Fund", code: "PIF", country: "Saudi Arabia", flag: "🇸🇦", aum: "$930B" },
  { rank: "05", name: "Kuwait Investment Authority", code: "KIA", country: "Kuwait", flag: "🇰🇼", aum: "$923B" },
  { rank: "06", name: "GIC Private Limited", code: "GIC", country: "Singapore", flag: "🇸🇬", aum: "$770B" },
  { rank: "07", name: "Hong Kong Monetary Authority", code: "HKMA", country: "Hong Kong", flag: "🇭🇰", aum: "$587B" },
  { rank: "08", name: "Temasek Holdings", code: "TEM", country: "Singapore", flag: "🇸🇬", aum: "$381B" },
];

const TICKER_ITEMS = [
  { name: "GPFG", val: "$1,707B", change: "+2.4%" },
  { name: "CIC", val: "$1,350B", change: "+1.8%" },
  { name: "ADIA", val: "$993B", change: "+3.1%" },
  { name: "PIF", val: "$930B", change: "+5.7%" },
  { name: "KIA", val: "$923B", change: "+1.2%" },
  { name: "GIC", val: "$770B", change: "+2.9%" },
  { name: "QIA", val: "$526B", change: "+4.1%" },
  { name: "TEM", val: "$381B", change: "+3.4%" },
  { name: "NWF RU", val: "$210B", change: "-1.3%", neg: true },
  { name: "ADQ", val: "$198B", change: "+6.2%" },
  { name: "Mubadala", val: "$302B", change: "+4.5%" },
  { name: "NBIM", val: "$1,707B", change: "+2.4%" },
];

const HERO_VIEWS = {
  overview: {
    label: "Global SWF AUM",
    value: "$36.4T",
    change: "▲ 4.2%",
    changeTone: "positive",
    period: "Total AUM · 2026",
    source: "Estimate · SWFI homepage framing",
    series: [28.2, 29.1, 29.8, 30.5, 31.2, 31.8, 32.4, 33.1, 33.6, 34.2, 34.9, 35.6, 36.4],
    stats: [
      { value: "189", label: "Countries" },
      { value: "176", label: "Active Funds" },
      { value: "595K", label: "Profiles" },
      { value: "172K", label: "Transactions" },
    ],
    headers: { name: "Fund", country: "Country", aum: "AUM" },
    rows: TOP_FUNDS,
    ticker: TICKER_ITEMS,
  },
  "top-funds": {
    label: "Top Fund Profiles",
    value: "$7.6T",
    change: "▲ 8 visible",
    changeTone: "positive",
    period: "Largest profiles in terminal view",
    source: "Static sample · top 8 by headline AUM",
    series: [4.8, 5.2, 5.6, 6.0, 6.3, 6.7, 7.1, 7.6],
    stats: [
      { value: "8", label: "Profiles" },
      { value: "6", label: "Countries" },
      { value: "7", label: ">$500B" },
      { value: "3", label: "GCC Funds" },
    ],
    headers: { name: "Profile", country: "Country", aum: "AUM" },
    rows: TOP_FUNDS,
    ticker: TICKER_ITEMS.slice(0, 8),
  },
  allocation: {
    label: "Asset Allocation",
    value: "31% EQ",
    change: "▲ docs mapped",
    changeTone: "positive",
    period: "Terminal allocation view",
    source: "Illustrative mix · verify before export",
    series: [16, 18, 19, 21, 22, 24, 26, 27, 29, 30, 31],
    stats: [
      { value: "26%", label: "Fixed Income" },
      { value: "24%", label: "Private Equity" },
      { value: "9%", label: "Infrastructure" },
      { value: "7%", label: "Real Estate" },
    ],
    headers: { name: "Asset Class", country: "Focus", aum: "Exposure" },
    rows: [
      { rank: "01", code: "Equities", country: "Global", aum: "31%" },
      { rank: "02", code: "Fixed Income", country: "Global", aum: "26%" },
      { rank: "03", code: "Private Equity", country: "Alternatives", aum: "24%" },
      { rank: "04", code: "Infrastructure", country: "Real Assets", aum: "9%" },
      { rank: "05", code: "Real Estate", country: "Real Assets", aum: "7%" },
      { rank: "06", code: "Hedge Funds", country: "Alternatives", aum: "3%" },
      { rank: "07", code: "Cash", country: "Liquidity", aum: "0-2%" },
      { rank: "08", code: "Other", country: "Special Situations", aum: "Residual" },
    ],
    ticker: [
      { name: "EQ", val: "31%", change: "+1.2%" },
      { name: "FI", val: "26%", change: "+0.4%" },
      { name: "PE", val: "24%", change: "+1.8%" },
      { name: "INFRA", val: "9%", change: "+0.7%" },
      { name: "RE", val: "7%", change: "+0.3%" },
      { name: "HF", val: "3%", change: "-0.1%", neg: true },
    ],
  },
  deals: {
    label: "Transactions",
    value: "172K",
    change: "▲ live record base",
    changeTone: "positive",
    period: "Historical + current coverage",
    source: "SWFI homepage count · 17 Apr 2026",
    series: [88, 95, 101, 112, 124, 133, 145, 153, 161, 166, 172],
    stats: [
      { value: "RFP", label: "Mandates" },
      { value: "PE", label: "Top Strategy" },
      { value: "GCC", label: "Active Region" },
      { value: "Daily", label: "Alert Cadence" },
    ],
    headers: { name: "Profile", country: "Market", aum: "Focus" },
    rows: [
      { rank: "01", code: "PIF", country: "Saudi Arabia", aum: "Direct + strategic deals" },
      { rank: "02", code: "ADQ", country: "UAE", aum: "Growth + infrastructure" },
      { rank: "03", code: "Mubadala", country: "UAE", aum: "Private markets" },
      { rank: "04", code: "ADIA", country: "UAE", aum: "Fund commitments" },
      { rank: "05", code: "QIA", country: "Qatar", aum: "Global mandates" },
      { rank: "06", code: "GIC", country: "Singapore", aum: "Cross-market allocation" },
      { rank: "07", code: "CIC", country: "China", aum: "Strategic deployment" },
      { rank: "08", code: "TEM", country: "Singapore", aum: "Direct investments" },
    ],
    ticker: [
      { name: "PIF", val: "Deals", change: "+5.7%" },
      { name: "ADQ", val: "Mandates", change: "+6.2%" },
      { name: "QIA", val: "RFPs", change: "+4.1%" },
      { name: "GIC", val: "Themes", change: "+2.9%" },
      { name: "TEM", val: "Deployments", change: "+3.4%" },
      { name: "NWF RU", val: "Paused", change: "-1.3%", neg: true },
    ],
  },
};

const INTEL_TAB_PROMPTS = {
  "top-swfs": "Show the top 5 sovereign wealth fund profiles by assets and note any coverage cautions.",
  "pif-deals": "Summarize Public Investment Fund transactions and explain any current source limitations.",
  "gcc-trends": "Summarize GCC asset allocation, mandate, and transaction themes from the current packet.",
  "active-rfps": "Show active RFPs and mandate activity by strategy from the current packet.",
};

const OFFERING_CARDS = [
  {
    label: "Subscription",
    value: "Profiles · Transactions · RFPs",
    note: "Deals, key executives, strategy notes, mandates, asset allocation data, news, and profiles.",
  },
  {
    label: "Key People",
    value: "Contacts within Profiles",
    note: "Work history, education, phone numbers, emails, and related profile detail.",
  },
  {
    label: "Datafeeds/API",
    value: "JSON and CSV delivery",
    note: "Profiles, AUM, asset allocation, transactions, RFPs, and contacts for direct integration.",
  },
];

function buildPublicDiscoveryDashboard() {
  return {
    generated_at: new Date().toISOString(),
    statuses: [
      { source: "Controlled access", note: "Sign in for client workspaces, protected exports, and research responses.", status: "partial" },
      { source: "Profiles", note: "Sovereign wealth funds, public pensions, central banks, endowments, and family offices.", status: "ok" },
      { source: "Transactions", note: "Deals, mandates, RFPs, and institutional allocation activity.", status: "ok" },
      { source: "Datafeeds/API", note: "JSON and CSV delivery through SWFI REST API and custom feed workflows.", status: "ok" },
    ],
    metric_cards: [
      { label: "Profiles", value: "595,040", note: "Public SWFI homepage count" },
      { label: "Transactions", value: "172,518", note: "Public SWFI homepage count" },
      { label: "RFPs", value: "4,844", note: "Public SWFI homepage count" },
      { label: "People & contacts", value: "123,217", note: "Public SWFI homepage count" },
    ],
    lanes: [],
    concerns: [
      {
        client: "SWFI",
        use_case: "Datafeeds/API",
        title: "Controlled access",
        state: "partial",
        priority: "P1",
        requirement: "Sign in is required for MSCI workspaces, protected exports, research responses, and client delivery views.",
        challenge: "Public discovery focuses on Profiles, Transactions, RFPs, Key People, Asset Allocation, and Datafeeds/API.",
        recommendation: "Use the public site for discovery and sign in for client delivery workspaces.",
        tags: ["exports", "profile", "people"],
      },
    ],
    action_queue: [
      { title: "Profiles", lane: "Subscription", status: "ok", priority: "P1", impact: "Institution profiles across sovereign wealth funds, public pensions, central banks, endowments, and family offices." },
      { title: "Transactions", lane: "Subscription", status: "ok", priority: "P1", impact: "Direct investments, fund commitments, and historical transaction activity across institutional investors." },
      { title: "RFPs and Opportunities", lane: "Subscription", status: "ok", priority: "P1", impact: "Mandates and business leads by strategy, institution, and region." },
      { title: "Key People", lane: "Subscription", status: "ok", priority: "P1", impact: "Contacts, work history, education, phone numbers, emails, and related profile detail." },
    ],
    aum_docs: {
      title: "SWFI Data Feeds & REST API",
      path: "https://api.swfi.com/collections/aum",
      query_parameters: [
        { name: "entity_id", type: "string", description: "Filter AUM records to a specific profile or related entity." },
        { name: "year", type: "number", description: "Request historical AUM snapshots by period." },
        { name: "sort", type: "string", description: "Sort output for delivery or reporting views." },
        { name: "limit", type: "number", description: "Control the number of returned rows." },
      ],
      example_fields: ["assets", "managedAssets", "equities", "realAssets", "realEstate", "infrastructure", "entityId", "period"],
      collections: [
        { label: "Entities" },
        { label: "Financials" },
        { label: "People" },
        { label: "Transactions" },
        { label: "RFPs" },
        { label: "News" },
      ],
    },
    readiness: [
      { title: "Subscription", status: "ok", note: "Profiles, Transactions, RFPs, Key People, Asset Allocation, briefings, and news." },
      { title: "Datafeeds/API", status: "ok", note: "JSON and CSV delivery for direct integration and custom reporting." },
      { title: "Controlled client workspaces", status: "partial", note: "Protected views such as MSCI remain available after sign-in." },
    ],
    proposal: {
      deliverables: [
        "Profiles",
        "Transactions",
        "RFPs and Opportunities",
        "Key People",
        "Asset Allocation",
        "Datafeeds/API",
      ],
    },
    platform_reference: {
      observed_at: "Public SWFI categories",
      counts: [
        { label: "Profiles", value: "595,040", note: "Public SWFI homepage count" },
        { label: "Transactions", value: "172,518", note: "Public SWFI homepage count" },
        { label: "RFPs", value: "4,844", note: "Public SWFI homepage count" },
        { label: "People & contacts", value: "123,217", note: "Public SWFI homepage count" },
      ],
      surfaces: [
        { label: "Subscription", value: "swfi.com", note: "Profiles, Transactions, RFPs, Key People, Asset Allocation, and briefings." },
        { label: "Datafeeds/API", value: "api.swfi.com", note: "REST API, collections, and AUM documentation." },
        { label: "Public Fund Monitor", value: "Newsletter surface", note: "Public institutional investor news distribution." },
      ],
    },
    benchmark_matrix: [
      {
        name: "SWFI Subscription",
        tone: "ok",
        headline: "Profiles, Transactions, RFPs and Opportunities, Key People, Asset Allocation, and briefings.",
        signals: ["Public fund coverage", "Institutional investor intelligence", "Controlled-access client workspaces"],
        url: "https://www.swfinstitute.org/services/subscription",
        source: "Official source",
      },
      {
        name: "SWFI Datafeeds/API",
        tone: "ok",
        headline: "JSON and CSV delivery with REST API access and custom data structures.",
        signals: ["api.swfi.com", "Collections docs", "AUM docs"],
        url: "https://www.swfinstitute.org/services/datafeed-api",
        source: "Official source",
      },
    ],
    required_api_stack: [
      {
        name: "SWFI REST API",
        status: "ok",
        why: "Public REST documentation for collection access and data integration.",
        gap: "Private delivery routes and protected exports still require sign-in.",
        sources: [{ label: "API home", url: "https://api.swfi.com/" }],
      },
      {
        name: "AUM collection",
        status: "ok",
        why: "Historical assets under management and related financial fields.",
        gap: "Deeper account mapping and protected client exports remain controlled.",
        sources: [{ label: "AUM docs", url: "https://api.swfi.com/collections/aum" }],
      },
      {
        name: "Collections surface",
        status: "ok",
        why: "Public object-family discovery across the API surface.",
        gap: "Authenticated collections and deeper delivery lanes remain private.",
        sources: [{ label: "Collections", url: "https://api.swfi.com/collections" }],
      },
    ],
  };
}

const state = {
  dashboard: null,
  lane: "All",
  query: "",
  heroTab: "overview",
  intelTab: "top-swfs",
};

const $ = (id) => document.getElementById(id);
const statusStrip = $("status-strip");
const metricGrid = $("metric-grid");
const laneTabs = $("lane-tabs");
const proposalBrief = $("proposal-brief");
const referenceGrid = $("reference-grid");
const collectionList = $("collection-list");
const laneList = $("lane-list");
const actionList = $("action-list");
const clientFilters = $("client-filters");
const concernSearch = $("concern-search");
const concernList = $("concern-list");
const concernCount = $("concern-count");
const apiTitle = $("api-title");
const apiPath = $("api-path");
const apiSummaryGrid = $("api-summary-grid");
const apiParamList = $("api-param-list");
const apiFieldList = $("api-field-list");
const readinessList = $("readiness-list");
const deliverableList = $("deliverable-list");
const telemetryChart = $("telemetry-chart");
const lastRefresh = $("last-refresh");
const chatLog = $("chat-log");
const chatForm = $("chat-form");
const chatInput = $("chat-input");
const benchmarkList = $("benchmark-list");
const apiStackList = $("api-stack-list");

const aumLabel = $("aum-label");
const aumDisplay = $("aum-display");
const aumChange = $("aum-change");
const aumPeriod = $("aum-period");
const aumSource = $("aum-source");
const statCountries = $("stat-countries");
const statCountriesLabel = $("stat-countries-label");
const statFunds = $("stat-funds");
const statFundsLabel = $("stat-funds-label");
const statProfiles = $("stat-profiles");
const statProfilesLabel = $("stat-profiles-label");
const statTransactions = $("stat-transactions");
const statTransactionsLabel = $("stat-transactions-label");
const fundNameHeader = $("fund-name-header");
const fundCountryHeader = $("fund-country-header");
const fundAumHeader = $("fund-aum-header");

const coverageSummaryGrid = $("coverage-summary-grid");
const signalSummaryNote = $("signal-summary-note");
const signalList = $("signal-list");
const briefingList = $("briefing-list");
const reportLinkList = $("report-link-list");
const coverageList = $("coverage-list");
const sourceFamilyList = $("source-family-list");
const sandboxMapList = $("sandbox-map-list");
const maturityGroupList = $("maturity-group-list");
const confidenceSummaryGrid = $("confidence-summary-grid");
const schemaList = $("schema-list");
const sourceTrailList = $("source-trail-list");
const launchChecklistList = $("launch-checklist-list");
const gapList = $("gap-list");
const securityControlsList = $("security-controls-list");
const riskRegisterList = $("risk-register-list");
const emailStreamList = $("email-stream-list");

const heroTabButtons = [...document.querySelectorAll("[data-hero-tab]")];
const intelTabButtons = [...document.querySelectorAll("[data-intel-tab]")];

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function relDate(iso) {
  if (!iso) return "—";
  const deltaMinutes = Math.max(1, Math.round((Date.now() - new Date(iso).getTime()) / 60000));
  return deltaMinutes < 60 ? `${deltaMinutes}m ago` : `${Math.round(deltaMinutes / 60)}h ago`;
}

function tone(status) {
  return ({
    ok: "ok",
    sourced: "ok",
    active: "ok",
    materialized: "ok",
    verified: "ok",
    partial: "partial",
    derived: "partial",
    watch: "watch",
    needsreview: "watch",
    needs_review: "watch",
    conflicted: "watch",
    scaffolded: "watch",
    missing_env: "watch",
    missing_driver: "watch",
    preview_branch_only: "watch",
    blocked: "blocked",
    rejected: "blocked",
    fallback: "blocked",
    connection_failed: "blocked",
    private_source_required: "blocked",
    direct_competitor: "partial",
    platform_benchmark: "partial",
    have_base_need_productization: "partial",
  })[status] || status || "watch";
}

const STATUS_LABELS = {
  ok: "Available",
  active: "Live",
  partial: "Partial",
  blocked: "Needed",
  watch: "Tracked",
  scaffolded: "Defined",
};

const PRIORITY_LABELS = {
  P1: "Immediate",
  P2: "Next",
};

const TAG_LABELS = {
  automation: "Automation",
  capacity: "Refresh scale",
  classification: "Asset Allocation",
  exports: "Datafeeds/API",
  high_volume: "High-volume coverage",
  manual_ops: "Manual handling",
  mapping: "Key People mapping",
  missing_fields: "Profile fields",
  alt_assets: "Alternatives",
  people: "Key People",
  profile: "Profiles",
  subsidiaries: "Subsidiaries",
};

const CONCERN_CONTENT = {
  "Complete Asset Allocation fields": {
    summary: "Complete Asset Allocation fields used in MSCI and client delivery.",
    build: "Move allocation percentages, managed assets, and classification fields into repeatable export-ready records.",
    impact: "This improves Asset Allocation tables, AUM views, and Datafeeds/API delivery.",
  },
  "Expand AUM coverage for subsidiaries": {
    summary: "Expand AUM and managed-assets coverage across subsidiaries and child funds.",
    build: "Add the profile fields and joins required to connect parent entities, subsidiaries, and related funds.",
    impact: "This improves profile completeness and makes AUM exports more reliable.",
  },
  "Increase Datafeeds/API refresh": {
    summary: "Increase refresh capacity for the largest institutional datafeeds.",
    build: "Improve update throughput across ingestion, review, and publishing for high-volume profiles and transactions.",
    impact: "This keeps recurring deliveries on schedule and reduces stale records.",
  },
  "Complete Profile fields": {
    summary: "Complete the core profile fields used across subscriptions, exports, and direct integrations.",
    build: "Backfill institution identity, location, and reference fields where profiles are still thin.",
    impact: "This improves trust in profiles and raises the completeness of feeds and exports.",
  },
  "Complete Datafeeds/API fields": {
    summary: "Complete the fields needed by downstream Datafeeds/API consumers.",
    build: "Close the remaining gaps between tracked internal fields and the records surfaced directly in exports.",
    impact: "This reduces one-off handling and makes delivery easier to automate.",
  },
  "Align Key People with Profiles": {
    summary: "Align Key People, contacts, and institution profiles with stable account references.",
    build: "Use consistent identifiers and joins so people-to-profile mapping stays stable across exports and APIs.",
    impact: "This is the foundation for trustworthy MSCI Key People files and review workflows.",
  },
  "Normalize AUM currency fields": {
    summary: "Normalize currency handling across AUM, managed assets, and account-level outputs.",
    build: "Apply shared FX conversion and currency metadata rules across feeds and exports.",
    impact: "This keeps profile and AUM outputs consistent for downstream consumers.",
  },
  "Extend Alternatives coverage": {
    summary: "Extend Alternatives and Real Assets coverage for institutions where that data is still thin.",
    build: "Add the fields and profile types required to surface alternatives directly in the product.",
    impact: "This closes a visible coverage gap and reduces manual side handling.",
  },
  "Expand Key People coverage": {
    summary: "Improve the depth and consistency of Key People records used in delivery work.",
    build: "Enrich contact coverage, refresh cadence, and supporting joins so people records are usable downstream.",
    impact: "This raises confidence in contact-level outputs and reduces manual follow-up.",
  },
};

function displayStatus(status) {
  return STATUS_LABELS[status] || String(status || "Tracked");
}

function displayPriority(priority) {
  return PRIORITY_LABELS[priority] || String(priority || "Next");
}

function displayTags(tags) {
  return (tags || []).map((tag) => TAG_LABELS[tag] || String(tag || "").replaceAll("_", " "));
}

function displayTitle(title) {
  return ({
    "Automate allocation percentage calculations": "Complete Asset Allocation fields",
    "Add subsidiary-aware AUM coverage": "Expand AUM coverage for subsidiaries",
    "Increase delivery bandwidth for priority feeds": "Increase Datafeeds/API refresh",
    "Backfill missing profile fields": "Complete Profile fields",
    "Add missing dashboard fields": "Complete Datafeeds/API fields",
    "Canonicalize people-to-account mapping": "Align Key People with Profiles",
    "Automate currency normalization": "Normalize AUM currency fields",
    "Add alternative asset coverage": "Extend Alternatives coverage",
    "Expand people profile coverage": "Expand Key People coverage",
    "Fix top-500 entity data quality": "Improve top 500 Profiles",
    "Publish sourced canonical schema": "Add source and timestamp detail",
    "Build MSCI people export lane": "MSCI Key People export",
    "Stabilize search and demo performance": "Platform speed and search",
    "Add AI search and saved alerts": "Search and alerts",
    "Wire CRM and warehouse connectors": "CRM and Datafeeds/API delivery",
    "Add entitlements, monitoring, and unified data model controls": "Access controls and monitoring",
  })[title] || title || "Coverage update";
}

function displayUseCase(value) {
  const text = String(value || "").trim();
  const lowered = text.toLowerCase();
  if (!text) return "Datafeeds/API";
  if (lowered.includes("api")) return "Datafeeds/API";
  if (lowered.includes("rfp") || lowered.includes("mandate")) return "RFPs and Opportunities";
  if (lowered.includes("people") || lowered.includes("contact")) return "Key People";
  if (lowered.includes("allocation") || lowered.includes("aum")) return "Asset Allocation";
  if (lowered.includes("deal") || lowered.includes("transaction")) return "Transactions";
  if (lowered.includes("profile")) return "Profiles";
  return text;
}

function concernNarrative(row) {
  if (row.requirement && row.challenge && row.recommendation) {
    return {
      summary: row.requirement,
      build: row.challenge,
      impact: row.recommendation,
    };
  }
  const mapped = CONCERN_CONTENT[row.title];
  if (mapped) return mapped;
  const focusAreas = displayTags(row.tags).slice(0, 3);
  return {
    summary: `${displayTitle(row.title)} sits inside the ${row.client} lane and still needs fuller coverage before it can be treated as routine.`,
    build: focusAreas.length
      ? `Focus areas: ${focusAreas.join(", ")}.`
      : "Focus areas span profiles, key people, asset allocation, and delivery controls.",
    impact: "This affects export completeness, Datafeeds/API reliability, and operator confidence across the lane.",
  };
}

function resetInitialViewport() {
  if ("scrollRestoration" in window.history) {
    window.history.scrollRestoration = "manual";
  }
  window.requestAnimationFrame(() => {
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  });
}

function isPublicDiscoveryHost() {
  const host = String(window.location.hostname || "").toLowerCase();
  return host === "swfi.com" || host === "www.swfi.com";
}

function getHeroView() {
  return HERO_VIEWS[state.heroTab] || HERO_VIEWS.overview;
}

function fieldLabel(field) {
  if (typeof field === "string") return field;
  if (!field || typeof field !== "object") return "";
  return field.name || field.field || field.label || JSON.stringify(field);
}

function renderMiniList(items) {
  if (!Array.isArray(items) || !items.length) {
    return '<article class="mini-item"><span class="list-mark">·</span><p>No tracked items.</p></article>';
  }
  return items
    .map((item) => `<article class="mini-item"><span class="list-mark">▸</span><p>${esc(item)}</p></article>`)
    .join("");
}

function renderKeyBlocks(blocks) {
  return blocks
    .map((block) => `
      <div class="concern-block compact">
        <span>${esc(block.label)}</span>
        <div class="mini-list">${renderMiniList(block.items)}</div>
      </div>
    `)
    .join("");
}

function renderTicker() {
  const track = $("ticker-tape");
  if (!track) return;
  const items = (getHeroView().ticker || TICKER_ITEMS)
    .map(
      (ticker) => `
        <span class="ticker-item">
          <span class="t-name">${esc(ticker.name)}</span>
          <span class="${ticker.neg ? "t-neg" : "t-val"}">${esc(ticker.val)}</span>
          <span class="${ticker.neg ? "t-neg" : "t-val"}">${esc(ticker.change)}</span>
          <span class="t-sep">│</span>
        </span>
      `,
    )
    .join("");
  track.innerHTML = items + items;
}

function renderAumChart() {
  const el = $("aum-chart");
  if (!el) return;
  const points = getHeroView().series || [];
  if (!points.length) {
    el.innerHTML = "";
    return;
  }
  const width = 400;
  const height = 70;
  const max = Math.max(...points);
  const min = Math.min(...points);
  const range = Math.max(max - min, 1);
  const step = points.length > 1 ? width / (points.length - 1) : width;
  const coords = points.map((value, index) => {
    const x = points.length === 1 ? width / 2 : index * step;
    const y = height - ((value - min) / range) * (height - 10) - 5;
    return `${x},${y}`;
  });
  const line = coords.join(" ");
  const area = `0,${height} ${line} ${width},${height}`;
  el.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
      <defs>
        <linearGradient id="aumGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="rgba(77,255,154,0.25)" />
          <stop offset="100%" stop-color="rgba(77,255,154,0)" />
        </linearGradient>
        <linearGradient id="aumLine" x1="0%" x2="100%" y1="0%" y2="0%">
          <stop offset="0%" stop-color="#4dff9a" />
          <stop offset="100%" stop-color="#d5ff52" />
        </linearGradient>
      </defs>
      <polygon points="${area}" fill="url(#aumGrad)" />
      <polyline points="${line}" fill="none" stroke="url(#aumLine)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
  `;
}

function renderHeroStats() {
  const view = getHeroView();
  const stats = view.stats || [];
  const first = stats[0] || { value: "—", label: "Countries" };
  const second = stats[1] || { value: "—", label: "Active Funds" };
  const third = stats[2] || { value: "—", label: "Profiles" };
  const fourth = stats[3] || { value: "—", label: "Transactions" };

  if (aumLabel) aumLabel.textContent = view.label || "Global SWF AUM";
  if (aumDisplay) aumDisplay.textContent = view.value || "—";
  if (aumChange) {
    aumChange.textContent = view.change || "—";
    aumChange.className = `aum-change ${view.changeTone === "negative" ? "negative" : "positive"}`;
  }
  if (aumPeriod) aumPeriod.textContent = view.period || "";
  if (aumSource) aumSource.textContent = view.source || "";

  if (statCountries) statCountries.textContent = first.value;
  if (statCountriesLabel) statCountriesLabel.textContent = first.label;
  if (statFunds) statFunds.textContent = second.value;
  if (statFundsLabel) statFundsLabel.textContent = second.label;
  if (statProfiles) statProfiles.textContent = third.value;
  if (statProfilesLabel) statProfilesLabel.textContent = third.label;
  if (statTransactions) statTransactions.textContent = fourth.value;
  if (statTransactionsLabel) statTransactionsLabel.textContent = fourth.label;

  if (fundNameHeader) fundNameHeader.textContent = view.headers?.name || "Fund";
  if (fundCountryHeader) fundCountryHeader.textContent = view.headers?.country || "Country";
  if (fundAumHeader) fundAumHeader.textContent = view.headers?.aum || "AUM";
}

function renderFundTable() {
  const el = $("fund-list");
  if (!el) return;
  const rows = getHeroView().rows || [];
  el.innerHTML = rows
    .map((row) => `
      <div class="fund-row">
        <span class="fund-rank">${esc(row.rank)}</span>
        <span class="fund-name">${row.flag ? `<span class="fund-flag">${esc(row.flag)}</span>` : ""}${esc(row.code)}</span>
        <span class="fund-country">${esc(row.country)}</span>
        <span class="fund-aum">${esc(row.aum)}</span>
      </div>
    `)
    .join("");
}

function renderHero() {
  heroTabButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.heroTab === state.heroTab);
  });
  renderHeroStats();
  renderTicker();
  renderAumChart();
  renderFundTable();
}

function renderStatusStrip() {
  const items = state.dashboard?.statuses || [];
  statusStrip.innerHTML = items
    .map(
      (item) => `
        <article class="status-pill tone-${tone(item.status)}">
          <strong>${esc(item.source)}</strong>
          <span>${esc(item.note)}</span>
        </article>
      `,
    )
    .join("");
}

function renderMetricGrid() {
  const items = state.dashboard?.metric_cards || [];
  metricGrid.innerHTML = items
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

function renderLaneSelectors() {
  const lanes = [{ name: "All" }, ...(state.dashboard?.lanes || [])];
  const markup = lanes
    .map(
      (lane) => `
        <button class="lane-tab ${lane.name === state.lane ? "active" : ""}" data-lane="${esc(lane.name)}">${esc(lane.name)}</button>
      `,
    )
    .join("");
  laneTabs.innerHTML = markup;
  clientFilters.innerHTML = markup;
  document.querySelectorAll("[data-lane]").forEach((button) =>
    button.addEventListener("click", () => {
      state.lane = button.dataset.lane || "All";
      renderLaneSelectors();
      renderLaneList();
      renderConcernList();
      renderTelemetryChart();
    }),
  );
}

function renderProposalBrief() {
  proposalBrief.innerHTML = `
    <div class="brief-grid">
      ${OFFERING_CARDS.map(
        (card) => `
          <article class="brief-card">
            <span class="metric-label">${esc(card.label)}</span>
            <strong>${esc(card.value)}</strong>
            <p>${esc(card.note)}</p>
          </article>
        `,
      ).join("")}
    </div>
  `;
}

function renderReferenceGrid() {
  const reference = state.dashboard?.platform_reference;
  if (!reference) {
    referenceGrid.innerHTML = "";
    return;
  }
  const cards = (reference.counts || [])
    .map(
      (item) => `
        <article class="reference-card">
          <span class="metric-label">${esc(item.label)}</span>
          <strong>${esc(item.value)}</strong>
          <p>${esc(item.note)}</p>
        </article>
      `,
    )
    .join("");
  const surfaces = (reference.surfaces || [])
    .map(
      (item) => `
        <article class="surface-card">
          <span class="metric-label">${esc(item.label)}</span>
          <strong>${esc(item.value)}</strong>
          <p>${esc(item.note)}</p>
        </article>
      `,
    )
    .join("");
  referenceGrid.innerHTML = `
    <p class="panel-note">${esc(reference.observed_at)}</p>
    <div class="reference-cards">${cards}</div>
    <div class="surface-list">${surfaces}</div>
  `;
}

function renderCollections() {
  const docs = state.dashboard?.aum_docs;
  if (!docs?.collections) {
    collectionList.innerHTML = "";
    return;
  }
  collectionList.innerHTML = docs.collections
    .slice(0, 16)
    .map((item) => `<span class="data-pill">${esc(item.label)}</span>`)
    .join("");
}

function renderLaneList() {
  const lanes = state.dashboard?.lanes || [];
  laneList.innerHTML = lanes
    .map(
      (lane) => `
        <button class="lane-card ${lane.name === state.lane ? "active" : ""}" data-lane="${esc(lane.name)}">
          <div class="lane-head">
            <div>
              <p class="sys-label">${esc(lane.cadence)}</p>
              <strong>${esc(lane.name)}</strong>
            </div>
            <span class="status-chip tone-${tone(lane.status)}">${esc(displayStatus(lane.status))}</span>
          </div>
          <p>${esc(lane.focus)}</p>
          <div class="lane-metrics">
            <span><strong>${lane.issue_count ?? 0}</strong><em>Priorities</em></span>
            <span><strong>${lane.manual_count ?? 0}</strong><em>Automation</em></span>
            <span><strong>${lane.field_gap_count ?? 0}</strong><em>Data gaps</em></span>
          </div>
          <div class="lane-footer"><span>${esc(lane.deliverable)}</span></div>
        </button>
      `,
    )
    .join("");

  laneList.querySelectorAll("[data-lane]").forEach((button) =>
    button.addEventListener("click", () => {
      state.lane = button.dataset.lane || "All";
      renderLaneSelectors();
      renderLaneList();
      renderConcernList();
      renderTelemetryChart();
    }),
  );
}

function renderActionList() {
  const items = state.dashboard?.action_queue || [];
  actionList.innerHTML = items
    .map(
      (item) => `
        <article class="action-card tone-${tone(item.status)}">
          <div class="action-head">
            <strong>${esc(displayTitle(item.title))}</strong>
            <span>${esc(displayPriority(item.priority))}</span>
          </div>
          <p>${esc(item.impact)}</p>
          <div class="action-meta">
            <span>${esc(item.lane)}</span>
            <span>${esc(displayStatus(item.status))}</span>
          </div>
        </article>
      `,
    )
    .join("");
}

function filteredConcerns() {
  const loweredQuery = state.query.trim().toLowerCase();
  const concerns = state.dashboard?.concerns || [];
  return concerns.filter((row) => {
    const laneMatch = state.lane === "All" || row.client === state.lane;
    const haystack = [row.client, row.use_case, row.requirement, row.challenge, row.recommendation, row.title]
      .join(" ")
      .toLowerCase();
    return laneMatch && (!loweredQuery || haystack.includes(loweredQuery));
  });
}

function renderConcernList() {
  const concerns = filteredConcerns();
  concernCount.textContent = concerns.length
    ? `${concerns.length} item${concerns.length === 1 ? "" : "s"}`
    : "No items";
  if (!concerns.length) {
    concernList.innerHTML = `
      <article class="empty-state">
        <strong>No matches.</strong>
        <p>Widen the lane filter or clear the search.</p>
      </article>
    `;
    return;
  }

  concernList.innerHTML = concerns
    .map((row) => {
      const narrative = concernNarrative(row);
      const tags = displayTags(row.tags);
      return `
        <article class="concern-card tone-${tone(row.state)}">
          <div class="concern-head-row">
            <div>
              <p class="eyebrow">${esc(row.client)} · ${esc(displayUseCase(row.use_case))}</p>
              <h4>${esc(displayTitle(row.title))}</h4>
            </div>
            <div class="tag-column">
              <span class="status-chip tone-${tone(row.state)}">${esc(displayStatus(row.state))}</span>
              <span class="priority-chip">${esc(displayPriority(row.priority))}</span>
            </div>
          </div>
          <div class="concern-block"><span>Coverage need</span><p>${esc(narrative.summary)}</p></div>
          <div class="concern-block"><span>Current gap</span><p>${esc(narrative.build)}</p></div>
          <div class="concern-block"><span>Delivery impact</span><p>${esc(narrative.impact)}</p></div>
          <div class="tag-row">${tags.map((tag) => `<span class="data-pill">${esc(tag)}</span>`).join("")}</div>
        </article>
      `;
    })
    .join("");
}

function renderApiSurface() {
  const docs = state.dashboard?.aum_docs;
  if (!docs) {
    apiTitle.textContent = "Unavailable";
    apiPath.textContent = "";
    apiSummaryGrid.innerHTML = "";
    apiParamList.innerHTML = "";
    apiFieldList.innerHTML = "";
    return;
  }
  const params = docs.query_parameters || [];
  const fields = (docs.example_fields || []).map(fieldLabel).filter(Boolean);
  const collections = docs.collections || [];
  const cards = [
    { label: "Query params", value: String(params.length), note: "Time, value, entity_id, sort" },
    { label: "Response fields", value: String(fields.length), note: "Assets, investments, allocations" },
    { label: "Collections", value: String(collections.length), note: "Public collection object types" },
    { label: "Delivery modes", value: "API+CSV+UI", note: "Machine + operator workflows" },
  ];
  apiTitle.textContent = docs.title || "AUM collection";
  apiPath.textContent = docs.path || "";
  apiSummaryGrid.innerHTML = cards
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
  apiParamList.innerHTML = params
    .slice(0, 16)
    .map(
      (param) => `
        <article class="api-item">
          <div class="api-item-head">
            <strong>${esc(param.name)}</strong>
            <span>${esc(param.type)}</span>
          </div>
          <p>${esc(param.description)}</p>
        </article>
      `,
    )
    .join("");
  apiFieldList.innerHTML = fields.slice(0, 24).map((field) => `<span class="data-pill">${esc(field)}</span>`).join("");
}

function renderReadiness() {
  const items = state.dashboard?.readiness || [];
  readinessList.innerHTML = items
    .map(
      (item) => `
        <article class="readiness-card tone-${tone(item.status)}">
          <div class="readiness-head">
            <strong>${esc(item.title)}</strong>
            <span class="status-chip tone-${tone(item.status)}">${esc(displayStatus(item.status))}</span>
          </div>
          <p>${esc(item.note)}</p>
        </article>
      `,
    )
    .join("");

  const deliverables = state.dashboard?.proposal?.deliverables || [];
  deliverableList.innerHTML = deliverables
    .map(
      (item) => `
        <article class="deliverable-item">
          <span class="list-mark">✓</span>
          <p>${esc(item)}</p>
        </article>
      `,
    )
    .join("");
}

function renderBenchmarkPanel() {
  const benchmarks = state.dashboard?.benchmark_matrix || state.dashboard?.competitor_benchmark || [];
  benchmarkList.innerHTML = benchmarks
    .map((benchmark) => {
      const level = benchmark.tone || benchmark.status || "watch";
      const headline = benchmark.headline || benchmark.product_benchmark || "";
      const signals = Array.isArray(benchmark.signals)
        ? benchmark.signals
        : [benchmark.api_benchmark, benchmark.ux_benchmark].filter(Boolean);
      return `
        <article class="benchmark-card tone-${tone(level)}">
          <div class="benchmark-head">
            <div>
              <p class="eyebrow">${esc(String(level).replaceAll("_", " "))}</p>
              <strong>${esc(benchmark.name)}</strong>
            </div>
          </div>
          <p>${esc(headline)}</p>
          ${signals.length ? `<div class="mini-list">${renderMiniList(signals)}</div>` : ""}
          ${benchmark.url ? `<a class="source-link" href="${esc(benchmark.url)}" target="_blank" rel="noreferrer">${esc(benchmark.source || "Official source")}</a>` : ""}
        </article>
      `;
    })
    .join("");

  const stack = state.dashboard?.required_api_stack || [];
  apiStackList.innerHTML = stack
    .map(
      (item) => `
        <article class="stack-card tone-${tone(item.status)}">
          <div class="readiness-head">
            <strong>${esc(item.name)}</strong>
            <span class="status-chip tone-${tone(item.status)}">${esc(displayStatus(item.status))}</span>
          </div>
          <p>${esc(item.why)}</p>
          <div class="concern-block compact">
            <span>Gap</span>
            <p>${esc(item.gap)}</p>
          </div>
          <div class="tag-row">
            ${(item.sources || [])
              .map(
                (source) => `
                  <a class="data-pill pill-link" href="${esc(source.url)}" target="_blank" rel="noreferrer">${esc(source.label)}</a>
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
  const allLanes = state.dashboard?.lanes || [];
  const lanes = state.lane === "All" ? allLanes : allLanes.filter((lane) => lane.name === state.lane);
  if (!lanes.length) {
    telemetryChart.innerHTML = "";
    return;
  }
  const values = lanes.map((lane) => Math.max(1, (lane.issue_count || 0) + (lane.manual_count || 0) + (lane.field_gap_count || 0)));
  const max = Math.max(...values, 1);
  const width = 320;
  const height = 110;
  const step = values.length > 1 ? width / (values.length - 1) : width;
  const points = values
    .map((value, index) => {
      const x = values.length === 1 ? width / 2 : index * step;
      const y = height - (value / max) * 80 - 10;
      return `${x},${y}`;
    })
    .join(" ");
  const legend = lanes
    .map(
      (lane, index) => `
        <div class="telemetry-legend-item">
          <span>${esc(lane.name)}</span>
          <strong>${values[index]}</strong>
        </div>
      `,
    )
    .join("");
  telemetryChart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" class="sparkline">
      <defs>
        <linearGradient id="spark" x1="0%" x2="100%">
          <stop offset="0%" stop-color="#4dff9a"/>
          <stop offset="100%" stop-color="#d5ff52"/>
        </linearGradient>
      </defs>
      <polyline points="${points}" fill="none" stroke="url(#spark)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      ${values
        .map((value, index) => {
          const x = values.length === 1 ? width / 2 : index * step;
          const y = height - (value / max) * 80 - 10;
          return `<circle cx="${x}" cy="${y}" r="4" fill="#040708" stroke="#4dff9a" stroke-width="2"/>`;
        })
        .join("")}
    </svg>
    <div class="telemetry-legend">${legend}</div>
  `;
}

function renderCoveragePanel() {
  const coverage = state.dashboard?.data_coverage || [];
  const families = state.dashboard?.source_taxonomy || [];
  const confidence = state.dashboard?.confidence_summary || {};
  const maturityGroups = state.dashboard?.connector_maturity || [];
  const sandbox = state.dashboard?.sandbox_api || {};
  const publicGroup = maturityGroups.find((group) => group.bucket === "public_api_available_now");
  const cards = [
    { label: "Coverage lanes", value: String(coverage.length), note: "MSCI, Bloomberg, IFC" },
    { label: "Source families", value: String(families.length), note: "Transactions, People, Entities, Enhancers" },
    { label: "Public APIs now", value: String((publicGroup?.items || []).length), note: "Current public rails ready for wiring" },
    { label: "Sandbox collections", value: String(sandbox.summary?.accessible_collections || 0), note: "Authenticated collections reachable now" },
    { label: "Private gaps", value: String(confidence.private_sources || 0), note: "Authenticated sources still required" },
  ];
  coverageSummaryGrid.innerHTML = cards
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

  coverageList.innerHTML = coverage
    .map(
      (lane) => `
        <article class="stack-card">
          <div class="readiness-head">
            <strong>${esc(lane.lane)} lane</strong>
            <span class="panel-note">Coverage</span>
          </div>
          ${renderKeyBlocks([
            { label: "API available today", items: lane.available_today_api || [] },
            { label: "Public docs extraction", items: lane.public_docs_extraction || [] },
            { label: "Third-party connectors", items: lane.third_party_connectors || [] },
            { label: "Unavailable without private access", items: lane.unavailable_without_private_access || [] },
          ])}
        </article>
      `,
    )
    .join("");

  sourceFamilyList.innerHTML = families
    .map(
      (family) => `
        <article class="stack-card">
          <div class="readiness-head">
            <strong>${esc(family.family)}</strong>
            <span class="panel-note">${(family.sources || []).length} inputs</span>
          </div>
          <div class="mini-list">${renderMiniList(family.sources || [])}</div>
        </article>
      `,
    )
    .join("");
}

function renderSandboxMap() {
  const sandbox = state.dashboard?.sandbox_api || {};
  const collections = sandbox.collections || [];
  if (!sandboxMapList) return;
  if (!collections.length) {
    sandboxMapList.innerHTML = `
      <article class="stack-card tone-${tone(sandbox.status)}">
        <div class="readiness-head">
          <strong>Sandbox API</strong>
          <span class="status-chip tone-${tone(sandbox.status)}">${esc(sandbox.status || "blocked")}</span>
        </div>
        <p>${esc(sandbox.source?.note || "Sandbox API map is not available.")}</p>
      </article>
    `;
    return;
  }

  sandboxMapList.innerHTML = collections
    .map(
      (collection) => `
        <article class="stack-card tone-${tone(collection.status)}">
          <div class="readiness-head">
            <strong>${esc(collection.label)}</strong>
            <span class="panel-note">${esc(collection.family)}</span>
          </div>
          <p>${collection.total_items ? `${esc(String(collection.total_items))} records surfaced in the authenticated sandbox.` : esc(collection.note || "Documented in the authenticated sandbox contract.")}</p>
          <div class="tag-row">${(collection.sample_fields || []).slice(0, 8).map((field) => `<span class="data-pill">${esc(field)}</span>`).join("")}</div>
        </article>
      `,
    )
    .join("");
}

function renderMaturityPanel() {
  const groups = state.dashboard?.connector_maturity || [];
  maturityGroupList.innerHTML = groups
    .map(
      (group) => `
        <article class="stack-card">
          <div class="readiness-head">
            <strong>${esc(group.title)}</strong>
            <span class="panel-note">${(group.items || []).length} items</span>
          </div>
          <div class="mini-list">
            ${(group.items || [])
              .map(
                (item) => `
                  <article class="mini-item">
                    <span class="list-mark">${tone(item.status) === "blocked" ? "!" : tone(item.status) === "ok" ? "✓" : "▸"}</span>
                    <p><strong>${esc(item.name)}</strong> · ${esc(item.note)}</p>
                  </article>
                `,
              )
              .join("")}
          </div>
        </article>
      `,
    )
    .join("");
}

function renderSignalPanel() {
  const signalStream = state.dashboard?.profile_signals || {};
  const items = signalStream.items || [];
  const summary = signalStream.summary || {};
  signalSummaryNote.textContent = `${summary.publishable || 0} publishable · ${summary.review_required || 0} review`;
  signalList.innerHTML = items
    .map(
      (item) => `
        <article class="stack-card tone-${tone(String(item.status || "").toLowerCase())}">
          <div class="readiness-head">
            <strong>${esc(item.title)}</strong>
            <span class="status-chip tone-${tone(String(item.status || "").toLowerCase())}">${esc(item.status)}</span>
          </div>
          <p>${esc(item.why_it_matters || item.summary || "")}</p>
          <div class="detail-line">
            <span>${esc(item.confidence || "")}</span>
            <span>${esc(item.priority || "")}</span>
            <span>${esc(relDate(item.generated_at))}</span>
          </div>
          ${
            (item.source_refs || []).length
              ? `<div class="tag-row">${(item.source_refs || [])
                  .map((ref) =>
                    ref.url
                      ? `<a class="data-pill pill-link" href="${esc(ref.url)}" target="_blank" rel="noreferrer">${esc(ref.label)}</a>`
                      : `<span class="data-pill">${esc(ref.label)}</span>`,
                  )
                  .join("")}</div>`
              : ""
          }
        </article>
      `,
    )
    .join("");
}

function renderBriefingPanel() {
  const briefings = state.dashboard?.alerts_briefings || {};
  const items = briefings.items || [];
  const reports = briefings.reports || [];
  briefingList.innerHTML = items
    .map(
      (item) => `
        <article class="stack-card tone-${tone(String(item.status || "").toLowerCase())}">
          <div class="readiness-head">
            <strong>${esc(item.title)}</strong>
            <span class="panel-note">${esc(item.cadence || "")}</span>
          </div>
          <p>${esc(item.summary || "")}</p>
          <div class="detail-line">
            <span>${esc(item.detail || "")}</span>
          </div>
        </article>
      `,
    )
    .join("");
  reportLinkList.innerHTML = reports
    .map((item) => `<a class="nav-cta mini-cta" href="${esc(item.url)}">${esc(item.label)}</a>`)
    .join("");
}

function renderCanonicalPanel() {
  const canonical = state.dashboard?.canonical_schema || {};
  const models = canonical.models || [];
  const provenance = canonical.provenance_contract || {};
  const confidence = state.dashboard?.confidence_summary || {};
  const sources = state.dashboard?.sources || [];
  const cards = [
    { label: "High confidence", value: String(confidence.high || 0), note: "Public APIs, local packets, and vetted docs" },
    { label: "Medium confidence", value: String(confidence.medium || 0), note: "Useful inputs that still need review" },
    { label: "Blocked sources", value: String(confidence.blocked_sources || 0), note: "Fallback or private-source dependencies" },
    { label: "Canonical models", value: String(models.length), note: "Institution through research item" },
  ];
  confidenceSummaryGrid.innerHTML = cards
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

  const provenanceCard = `
    <article class="stack-card">
      <div class="readiness-head">
        <strong>Provenance envelope</strong>
        <span class="panel-note">${(provenance.required_fields || []).length} required fields</span>
      </div>
      <div class="tag-row">${(provenance.required_fields || []).map((field) => `<span class="data-pill">${esc(field.replaceAll("_", " "))}</span>`).join("")}</div>
      <div class="detail-line">
        <span>${esc(provenance.example?.source_system || "")}</span>
        <span>${esc(provenance.example?.extraction_method || "")}</span>
        <span>${esc(provenance.example?.confidence || "")}</span>
      </div>
    </article>
  `;

  schemaList.innerHTML =
    provenanceCard +
    models
      .map(
        (model) => `
          <article class="stack-card">
            <div class="readiness-head">
              <strong>${esc(model.name)}</strong>
              <span class="panel-note">${esc(model.primary_key)}</span>
            </div>
            <p>${esc((model.joins || []).length)} joins across the canonical layer.</p>
            <div class="tag-row">${(model.fields || []).slice(0, 10).map((field) => `<span class="data-pill">${esc(field)}</span>`).join("")}</div>
          </article>
        `,
      )
      .join("");

  sourceTrailList.innerHTML = sources
    .slice(0, 14)
    .map(
      (source) => `
        <article class="stack-card tone-${tone(source.status)}">
          <div class="readiness-head">
            <strong>${esc(source.label)}</strong>
            <span class="status-chip tone-${tone(source.status)}">${esc(source.status || "ok")}</span>
          </div>
          <p>${esc(source.note || source.source_system || "")}</p>
          <div class="detail-line">
            <span>${esc(String(source.classification || "").replaceAll("_", " "))}</span>
            <span>${esc(source.extraction_method || "")}</span>
            <span>${esc(source.confidence || "")}</span>
          </div>
          ${
            source.evidence_url
              ? `<a class="source-link" href="${esc(source.evidence_url)}" target="_blank" rel="noreferrer">Evidence</a>`
              : source.document_pointer
                ? `<div class="detail-line"><span>${esc(source.document_pointer)}</span></div>`
                : ""
          }
        </article>
      `,
    )
    .join("");
}

function renderLaunchPanel() {
  const checklist = state.dashboard?.production_launch_checklist || [];
  const gaps = state.dashboard?.gaps || [];
  const securityControls = state.dashboard?.security_controls || [];
  const riskRegister = state.dashboard?.legal_risk_register || [];
  const streams = state.dashboard?.email_streams?.streams || [];

  launchChecklistList.innerHTML = checklist
    .map(
      (item) => `
        <article class="stack-card tone-${tone(item.status)}">
          <div class="readiness-head">
            <strong>${esc(item.title)}</strong>
            <span class="status-chip tone-${tone(item.status)}">${esc(item.status)}</span>
          </div>
          <p>${esc(item.note)}</p>
        </article>
      `,
    )
    .join("");

  gapList.innerHTML = gaps
    .map(
      (gap) => `
        <article class="stack-card tone-${tone(gap.severity)}">
          <div class="readiness-head">
            <strong>${esc(gap.title)}</strong>
            <span class="status-chip tone-${tone(gap.severity)}">${esc(gap.severity)}</span>
          </div>
          <p>${esc(gap.detail)}</p>
        </article>
      `,
    )
    .join("");

  securityControlsList.innerHTML = securityControls
    .map(
      (item) => `
        <article class="stack-card tone-${tone(item.status)}">
          <div class="readiness-head">
            <strong>${esc(item.title)}</strong>
            <span class="status-chip tone-${tone(item.status)}">${esc(item.status)}</span>
          </div>
          <p>${esc(item.note)}</p>
          ${item.url ? `<a class="source-link" href="${esc(item.url)}" target="_blank" rel="noreferrer">${esc(item.source || "Source")}</a>` : ""}
        </article>
      `,
    )
    .join("");

  riskRegisterList.innerHTML = riskRegister
    .map(
      (item) => `
        <article class="stack-card tone-${tone(item.status || item.severity)}">
          <div class="readiness-head">
            <strong>${esc(item.title)}</strong>
            <span class="status-chip tone-${tone(item.status || item.severity)}">${esc(item.status || item.severity || "watch")}</span>
          </div>
          <p>${esc(item.note || item.detail || "")}</p>
          ${item.action ? `<div class="detail-line"><span>${esc(item.action)}</span></div>` : ""}
          ${item.url ? `<a class="source-link" href="${esc(item.url)}" target="_blank" rel="noreferrer">${esc(item.source || "Source")}</a>` : ""}
        </article>
      `,
    )
    .join("");

  emailStreamList.innerHTML = streams
    .map(
      (stream) => `
        <article class="stack-card tone-${tone(stream.status)}">
          <div class="readiness-head">
            <strong>${esc(stream.name)}</strong>
            <span class="panel-note">${esc(stream.transport)}</span>
          </div>
          <p>${esc(stream.audience)} · ${esc(stream.cadence)}</p>
          <div class="tag-row">${(stream.collections || []).map((collection) => `<span class="data-pill">${esc(collection)}</span>`).join("")}</div>
        </article>
      `,
    )
    .join("");
}

function appendChat(role, text, evidence = [], meta = "") {
  const el = document.createElement("article");
  el.className = `chat-message ${role}`;
  el.innerHTML = `
    <div class="chat-message-head">
      <strong>${role === "user" ? "You" : "SWFI Research"}</strong>
      ${meta ? `<span>${esc(meta)}</span>` : ""}
    </div>
    <p>${esc(text)}</p>
    ${
      evidence.length
        ? `<div class="chat-evidence">${evidence
            .map(
              (item) => `
                <a href="${esc(item.url || "#")}" ${item.url ? 'target="_blank" rel="noreferrer"' : ""}>
                  <span>${esc(item.source)}</span>
                  <strong>${esc(item.label)}</strong>
                </a>
              `,
            )
            .join("")}</div>`
        : ""
    }
  `;
  chatLog.appendChild(el);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function seedChat() {
  if (chatLog.childElementCount) return;
  appendChat(
    "assistant",
    "Ask about Profiles, Transactions, RFPs, Key People, Asset Allocation, or Datafeeds. Answers stay tied to the current packet and linked evidence.",
    [],
    "Source-backed",
  );
}

async function runCopilot(query) {
  const trimmed = (query || "").trim();
  if (!trimmed) return;
  appendChat("user", trimmed);
  appendChat("assistant", "Checking the current packet and linked evidence...", [], "Sourcing");
  try {
    const response = await fetch(`/api/research/v1?q=${encodeURIComponent(trimmed)}`);
    if (response.status === 401) {
      window.location.href = `/login?next=${encodeURIComponent(window.location.pathname || "/")}`;
      return;
    }
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || `research ${response.status}`);
    }
    const placeholder = chatLog.lastElementChild;
    if (placeholder?.classList.contains("assistant")) placeholder.remove();
    const metaParts = [
      payload.provider_label || "Governed fallback",
      payload.status || "",
      payload.confidence || "",
    ].filter(Boolean);
    appendChat("assistant", payload.answer, payload.evidence || [], metaParts.join(" · "));
  } catch (error) {
    const placeholder = chatLog.lastElementChild;
    if (placeholder?.classList.contains("assistant")) placeholder.remove();
    appendChat("assistant", error.message || "Research lookup failed. The dashboard packet is still loaded.", [], "Fallback");
    console.error(error);
  }
}

function activateIntelTab(tabKey, fireQuery = false) {
  state.intelTab = tabKey;
  intelTabButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.intelTab === tabKey);
  });
  if (fireQuery && INTEL_TAB_PROMPTS[tabKey]) {
    runCopilot(INTEL_TAB_PROMPTS[tabKey]);
  }
}

function renderAll() {
  if (!state.dashboard) return;
  try { renderHero(); } catch (error) { console.error("hero", error); }
  try { renderStatusStrip(); } catch (error) { console.error("status", error); }
  try { renderMetricGrid(); } catch (error) { console.error("metric", error); }
  try { renderLaneSelectors(); } catch (error) { console.error("lanes", error); }
  try { renderProposalBrief(); } catch (error) { console.error("proposal", error); }
  try { renderReferenceGrid(); } catch (error) { console.error("reference", error); }
  try { renderCollections(); } catch (error) { console.error("collections", error); }
  try { renderLaneList(); } catch (error) { console.error("lane-list", error); }
  try { renderActionList(); } catch (error) { console.error("action", error); }
  try { renderConcernList(); } catch (error) { console.error("concern", error); }
  try { renderApiSurface(); } catch (error) { console.error("api", error); }
  try { renderReadiness(); } catch (error) { console.error("readiness", error); }
  try { renderBenchmarkPanel(); } catch (error) { console.error("benchmark", error); }
  try { renderTelemetryChart(); } catch (error) { console.error("telemetry", error); }
  try { renderCoveragePanel(); } catch (error) { console.error("coverage", error); }
  try { renderSignalPanel(); } catch (error) { console.error("signals", error); }
  try { renderBriefingPanel(); } catch (error) { console.error("briefings", error); }
  try { renderSandboxMap(); } catch (error) { console.error("sandbox", error); }
  try { renderMaturityPanel(); } catch (error) { console.error("maturity", error); }
  try { renderCanonicalPanel(); } catch (error) { console.error("canonical", error); }
  try { renderLaunchPanel(); } catch (error) { console.error("launch", error); }
  lastRefresh.textContent = relDate(state.dashboard.generated_at);
  seedChat();
}

async function loadDashboard() {
  const response = await fetch("/api/dashboard/v1");
  if (response.status === 401) {
    if (isPublicDiscoveryHost()) {
      state.dashboard = buildPublicDiscoveryDashboard();
      renderAll();
      resetInitialViewport();
      return;
    }
    window.location.href = `/login?next=${encodeURIComponent(window.location.pathname || "/")}`;
    return;
  }
  if (!response.ok) throw new Error(`dashboard ${response.status}`);
  state.dashboard = await response.json();
  renderAll();
  resetInitialViewport();
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

document.querySelectorAll("[data-chat-suggestion]").forEach((button) =>
  button.addEventListener("click", () => runCopilot(button.dataset.chatSuggestion || "")),
);

heroTabButtons.forEach((button) =>
  button.addEventListener("click", () => {
    state.heroTab = button.dataset.heroTab || "overview";
    renderHero();
  }),
);

intelTabButtons.forEach((button) =>
  button.addEventListener("click", () => {
    activateIntelTab(button.dataset.intelTab || "top-swfs", true);
  }),
);

resetInitialViewport();
window.addEventListener("pageshow", resetInitialViewport);

renderHero();

loadDashboard().catch((error) => {
  console.error(error);
  statusStrip.innerHTML = `
    <article class="status-pill tone-blocked">
      <strong>Dashboard</strong>
      <span>Failed to load the SWFI packet</span>
    </article>
  `;
});
