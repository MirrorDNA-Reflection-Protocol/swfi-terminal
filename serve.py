#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import html
import http.server
import io
import json
import os
import re
import subprocess
import threading
import time
from collections import Counter
from pathlib import Path
from textwrap import shorten
from urllib import parse, request


ROOT = Path(__file__).resolve().parent
SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/1dVHsh2zmWrWsxSpMg3zEr7Je27XmAsnO/gviz/tq"
    "?tqx=out:csv&gid=251913671"
)
AUM_DOCS_URL = "https://api.swfi.com/collections/aum"
API_HOME_URL = "https://api.swfi.com/"
CACHE_TTL_SECONDS = int(os.environ.get("DASHBOARD_TTL_SECONDS", "900"))
HTTP_USER_AGENT = os.environ.get("SWFI_TERMINAL_USER_AGENT", "SWFI Terminal/0.3")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

PROPOSAL_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/1dVHsh2zmWrWsxSpMg3zEr7Je27XmAsnO/htmlview#gid=251913671"
)

PLATFORM_REFERENCE = {
    "observed_at": "Observed 17 Apr 2026",
    "counts": [
        {"label": "Profiles", "value": "595,040", "note": "Public SWFI homepage count"},
        {"label": "Transactions", "value": "172,518", "note": "Public SWFI homepage count"},
        {"label": "RFPs", "value": "4,844", "note": "Public SWFI homepage count"},
        {"label": "News articles", "value": "17,602", "note": "Public SWFI homepage count"},
        {"label": "People & contacts", "value": "123,217", "note": "Public SWFI homepage count"},
    ],
    "surfaces": [
        {
            "label": "Public site",
            "value": "swfi.com",
            "note": "Category framing, proofs, and buyer journeys",
        },
        {
            "label": "Private platform",
            "value": "Dashboard + entities + people + transactions + compass",
            "note": "Dense authenticated workspace inspected live",
        },
        {
            "label": "API docs",
            "value": "api.swfi.com",
            "note": "Public documentation for AUM and related collections",
        },
    ],
}

PROPOSAL = {
    "title": "SWFI Feed Modernization and Client Delivery System",
    "goal": (
        "Build a private working surface at swfi.activemirror.ai that modernizes feed delivery, "
        "normalizes outputs, and improves operational visibility."
    ),
    "fee": "USD 100,000 fixed fee",
    "timeline": "8 to 12 weeks",
    "payments": ["50% on kickoff", "50% on delivery and acceptance"],
    "deliverables": [
        "Working private deployment of swfi.activemirror.ai",
        "Modernized delivery interface for in-scope client feeds",
        "Normalized data and export layer for agreed fields",
        "MSCI people/account export capability",
        "Agreed field mappings and output structure",
        "Basic admin and refresh-state visibility",
        "Delivery walkthrough and handoff session",
    ],
    "maintenance": [
        "Monthly maintenance: USD 5,000",
        "Annual maintenance: USD 50,000 prepaid",
    ],
    "sources": [
        {"source": "Proposal", "label": "Feed modernization proposal", "url": PROPOSAL_SHEET_URL},
        {"source": "AUM docs", "label": "SWFI API docs", "url": AUM_DOCS_URL},
    ],
}

CLIENT_PRESETS = {
    "MSCI": {
        "status": "active",
        "cadence": "Rolling delivery + quarterly revisit cycle",
        "focus": "People/account mapping, allocation automation, and managed-assets splits",
        "deliverable": "CSV export and canonical mapping output",
    },
    "Bloomberg": {
        "status": "active",
        "cadence": "Quarterly delivery lane",
        "focus": "Financial institution AUM coverage, FX normalization, and allocation math",
        "deliverable": "Structured feed with currency-normalized outputs",
    },
    "IFC": {
        "status": "scaffolded",
        "cadence": "Pending detailed workflow pack",
        "focus": "Private delivery lane scaffold from proposal scope",
        "deliverable": "Controlled client output lane",
    },
}

COMPETITOR_BENCHMARK = [
    {
        "name": "Preqin Pro",
        "status": "direct competitor",
        "headline": "Workflow depth across investors, funds, deals, benchmarking, and data delivery.",
        "signals": [
            "Preqin positions Pro around investors, fund managers, service providers, performance, and deal intelligence.",
            "Preqin publishes bulk data feeds, CRM/data lake/Excel delivery, and more than 100 schedulable feeds.",
            "Their July 2024 coverage sheet emphasizes dedicated alternatives coverage, researcher-led updates, and benchmark tooling.",
        ],
        "source": "Official product + data feed pages and July 2024 coverage update",
        "url": "https://www.preqin.com/our-products/preqin-pro",
    },
    {
        "name": "BlackRock Aladdin",
        "status": "platform benchmark",
        "headline": "API-first operating system with governed analytics and enterprise data distribution.",
        "signals": [
            "BlackRock publicly frames Aladdin as API-first, with read/write/modify operations across the ecosystem.",
            "Aladdin Data Cloud emphasizes Snowflake-powered data distribution and whole-portfolio analytics.",
            "This is the benchmark for integration depth, governance, and downstream system fit.",
        ],
        "source": "Official Aladdin and Aladdin Data Cloud pages",
        "url": "https://www.blackrock.com/aladdin/products/aladdin-platform",
    },
    {
        "name": "KKR",
        "status": "institutional credibility benchmark",
        "headline": "Important target/benchmark institution, but not a public developer-platform benchmark.",
        "signals": [
            "Public official KKR product or developer API surfaces comparable to Preqin/Aladdin were not found in this review.",
            "Treat KKR as a customer/data-subject benchmark for coverage quality, not as the primary API benchmark.",
        ],
        "source": "Inference from official-public review",
        "url": "https://www.kkr.com/",
    },
]

REQUIRED_API_STACK = [
    {
        "name": "Core SWFI domain APIs",
        "status": "have_base_need_productization",
        "why": "Entities, people, transactions, compass, reports, news, subsidiaries, and AUM are the product spine.",
        "gap": "Need private, authenticated product endpoints with stable contracts, saved views, and per-client output jobs.",
        "sources": [{"label": "SWFI API docs", "url": API_HOME_URL}],
    },
    {
        "name": "Document ingestion and extraction APIs",
        "status": "missing",
        "why": "IISM and the question bank imply a product layer for source discovery, document import, extraction runs, confidence scores, and review queues.",
        "gap": "Needed for primary-source fact extraction, monitoring, and human-in-the-loop validation.",
        "sources": [],
    },
    {
        "name": "Entity identity and legal reference APIs",
        "status": "missing",
        "why": "Canonical people/account mapping and field backfill require legal-entity identifiers and registry lookups.",
        "gap": "Need LEI and corporate registry resolution in the delivery system.",
        "sources": [
            {"label": "GLEIF API", "url": "https://www.gleif.org/en/lei-data/gleif-lei-look-up-api/access-the-api"},
            {"label": "Companies House API", "url": "https://developer.company-information.service.gov.uk/"},
        ],
    },
    {
        "name": "Regulatory and filings APIs",
        "status": "partial",
        "why": "Institutional-grade refreshes need primary-source filings, disclosures, and sanctions/compliance checks.",
        "gap": "Current prototype coverage is too narrow; needs first-party filing rails and watchlists.",
        "sources": [
            {"label": "SEC APIs", "url": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces"},
            {"label": "OFAC Sanctions List Service", "url": "https://ofac.treasury.gov/sanctions-list-service"},
        ],
    },
    {
        "name": "CRM, spreadsheet, and data-lake delivery APIs",
        "status": "missing",
        "why": "Preqin explicitly competes on CRM/data lake/Excel delivery; BlackRock competes on cloud distribution and APIs.",
        "gap": "Need outbound connectors and scheduled sync jobs, not just CSV downloads.",
        "sources": [
            {"label": "Salesforce APIs", "url": "https://developer.salesforce.com/docs/apis"},
            {"label": "Snowflake SQL API", "url": "https://docs.snowflake.com/en/developer-guide/sql-api/index"},
            {"label": "Microsoft Graph", "url": "https://learn.microsoft.com/en-us/graph/overview"},
        ],
    },
    {
        "name": "Research and news enrichment APIs",
        "status": "partial",
        "why": "A product on par with institutional platforms needs traceable news, alerts, and evidence packets.",
        "gap": "Current public-source stack is enough for a prototype, not enough for premium institutional monitoring.",
        "sources": [],
    },
]

RESEARCH_SYSTEM_PROMPT = """
You are SWFI Ops Copilot inside a private feed modernization terminal.
You are only a read-only analysis assistant.

Allowed scope:
- client feed workflows
- exports, mappings, and delivery blockers
- AUM/API schema readiness
- competitive product positioning
- document-ingestion and fact extraction design
- required integrations and API categories

Rules:
- Use only the provided source packet.
- Distinguish clearly between sourced facts and inference.
- Do not claim hidden access or unverified capabilities.
- Stay concise, operational, and product-focused.
- Do not execute actions, send messages, or promise implementation already exists.
""".strip()

NON_PRODUCT_HINTS = (
    "joke",
    "poem",
    "recipe",
    "movie",
    "music",
    "weather",
    "translate",
    "story",
)

ACTION_HINTS = (
    "send email",
    "email this",
    "text this",
    "whatsapp",
    "call them",
    "schedule",
    "log in",
    "login",
    "book a meeting",
)

_cache_lock = threading.Lock()
_dashboard_cache: dict[str, object] = {"timestamp": 0.0, "payload": None}


def load_gemini_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    if key:
        return key

    for secret_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-a", "mirrordna", "-s", secret_name, "-w"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            continue
    return ""


GEMINI_API_KEY = load_gemini_api_key()


def normalize_text(value: str) -> str:
    return " ".join(value.replace("\xa0", " ").split())


def strip_tags(value: str) -> str:
    return normalize_text(re.sub(r"<[^>]+>", " ", value))


def fetch_text(url: str, *, timeout: int = 20, headers: dict[str, str] | None = None) -> str:
    request_headers = {"User-Agent": HTTP_USER_AGENT, **(headers or {})}
    req = request.Request(url, headers=request_headers)
    with request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_json(url: str, *, payload: object | None = None, headers: dict[str, str] | None = None, timeout: int = 20):
    request_headers = {"User-Agent": HTTP_USER_AGENT, **(headers or {})}
    data = None
    if payload is not None:
        request_headers.setdefault("Content-Type", "application/json")
        data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, headers=request_headers, data=data)
    with request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def derive_tags(*parts: str) -> list[str]:
    text = normalize_text(" ".join(part for part in parts if part)).lower()
    tags: list[str] = []
    rules = [
        ("manual_ops", ("manual", "excel", "oanda")),
        ("missing_fields", ("missing", "lacks", "unavailable", "does not have", "currently lacks")),
        ("capacity", ("additional resources", "insufficient", "bandwidth", "30 working days", "time-intensive")),
        ("automation", ("automate", "automation", "backend", "implement", "system should")),
        ("classification", ("active and passive", "active/passive", "asset allocation", "strategy field")),
        ("mapping", ("people/account", "mapping", "identifiers")),
        ("currency", ("currency", "fx", "oanda")),
        ("exports", ("csv export", "export", "output")),
        ("subsidiaries", ("subsidiar",)),
        ("high_volume", ("600000", "600,000", "4952", "906", "573", "176")),
    ]
    for tag, keywords in rules:
        if any(keyword in text for keyword in keywords):
            tags.append(tag)
    return tags


def classify_row(row: dict[str, str]) -> dict[str, str]:
    tags = row["tags"]
    lowered = normalize_text(" ".join((row["requirement"], row["challenge"], row["recommendation"]))).lower()

    if "mapping" in tags:
        title = "Canonicalize people-to-account mapping"
    elif "subsidiaries" in tags:
        title = "Add subsidiary-aware AUM coverage"
    elif "currency" in tags:
        title = "Automate currency normalization"
    elif "classification" in tags and "manual_ops" in tags:
        title = "Automate allocation percentage calculations"
    elif "missing_fields" in tags and "profile" in lowered:
        title = "Backfill missing profile fields"
    elif "missing_fields" in tags:
        title = "Add missing dashboard fields"
    elif "capacity" in tags:
        title = "Increase delivery bandwidth for priority feeds"
    else:
        title = shorten(row["requirement"] or row["challenge"], width=72, placeholder="...")

    if "manual_ops" in tags or "missing_fields" in tags:
        state = "blocked"
    elif "automation" in tags or "capacity" in tags:
        state = "partial"
    else:
        state = "watch"

    priority = "P1" if row["client"] in ("MSCI", "Bloomberg") else "P2"
    if "high_volume" in tags or "mapping" in tags:
        priority = "P1"

    return {"title": title, "state": state, "priority": priority}


def load_concern_rows() -> list[dict[str, object]]:
    csv_text = fetch_text(SHEET_CSV_URL)
    reader = csv.DictReader(io.StringIO(csv_text))

    client = ""
    use_case = ""
    rows: list[dict[str, object]] = []

    for raw in reader:
        client = (raw.get("Client Name") or client or "").strip()
        use_case = (raw.get("Use Case") or use_case or "").strip()
        requirement = normalize_text(raw.get("Data Requirement") or "")
        challenge = normalize_text(raw.get("Challenges") or "")
        recommendation = normalize_text(raw.get("Recommendations") or "")

        if not any((client, requirement, challenge, recommendation)):
            continue

        tags = derive_tags(requirement, challenge, recommendation)
        row = {
            "client": client or "General",
            "use_case": use_case or "Feed delivery",
            "requirement": requirement,
            "challenge": challenge,
            "recommendation": recommendation,
            "tags": tags,
        }
        row.update(classify_row(row))
        rows.append(row)

    return rows


def parse_aum_docs() -> dict[str, object]:
    aum_html = fetch_text(AUM_DOCS_URL)
    collections_html = fetch_text(API_HOME_URL)

    section = aum_html.split("Success Response", 1)[0]
    pattern = re.compile(
        r'bg-light rounded(?: text-break)?">([^<]+)</div><div class="font-monospace(?: ms-1)?">'
        r'<span class="text-muted me-1">TYPE</span><span>([^<]+)</span></div></div><div>(.*?)</div>',
        re.S,
    )

    params: list[dict[str, str]] = []
    seen_params: set[str] = set()
    for name, dtype, description in pattern.findall(section):
        clean_name = normalize_text(html.unescape(name))
        if clean_name in seen_params:
            continue
        seen_params.add(clean_name)
        params.append(
            {
                "name": clean_name,
                "type": normalize_text(html.unescape(dtype)),
                "description": strip_tags(html.unescape(description)),
            }
        )

    example_match = re.search(r"Example response</div><pre[^>]*>(.*?)</pre>", aum_html, re.S)
    example_fields: list[str] = []
    if example_match:
        pre_block = example_match.group(1)
        seen_fields: set[str] = set()
        for field in re.findall(r"&quot;([^&]+?)&quot;\s*:", pre_block):
            if field in seen_fields:
                continue
            seen_fields.add(field)
            example_fields.append(field)

    collections: list[dict[str, str]] = []
    seen_slugs: set[str] = set()
    for slug, label in re.findall(r'href="/collections/([^"]+)">([^<]+)</a>', collections_html):
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        collections.append({"slug": slug, "label": normalize_text(html.unescape(label))})

    return {
        "title": "AUM collection",
        "path": "GET /v1/aum",
        "summary": "Historical assets under management for entities, with filters for time, value ranges, entity_id, and sort controls.",
        "query_parameters": params,
        "example_fields": example_fields,
        "collections": collections,
        "source": {"label": "SWFI API docs", "url": AUM_DOCS_URL},
    }


def build_lane_summaries(concerns: list[dict[str, object]]) -> list[dict[str, object]]:
    lanes: list[dict[str, object]] = []
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in concerns:
        grouped.setdefault(str(row["client"]), []).append(row)

    for client in ("MSCI", "Bloomberg"):
        preset = CLIENT_PRESETS[client]
        rows = grouped.get(client, [])
        tag_counter = Counter(tag for row in rows for tag in row["tags"])
        lanes.append(
            {
                "name": client,
                "status": preset["status"],
                "cadence": preset["cadence"],
                "focus": preset["focus"],
                "deliverable": preset["deliverable"],
                "issue_count": len(rows),
                "manual_count": tag_counter.get("manual_ops", 0),
                "field_gap_count": tag_counter.get("missing_fields", 0),
                "automation_count": tag_counter.get("automation", 0),
                "source_note": rows[0]["title"] if rows else "No tracked concern rows",
            }
        )

    preset = CLIENT_PRESETS["IFC"]
    lanes.append(
        {
            "name": "IFC",
            "status": preset["status"],
            "cadence": preset["cadence"],
            "focus": preset["focus"],
            "deliverable": preset["deliverable"],
            "issue_count": 0,
            "manual_count": 0,
            "field_gap_count": 0,
            "automation_count": 1,
            "source_note": "Proposal includes IFC as an in-scope workflow, but the concern sheet does not yet define the lane.",
        }
    )
    return lanes


def build_action_queue(concerns: list[dict[str, object]]) -> list[dict[str, object]]:
    actions: list[dict[str, object]] = []
    seen_titles: set[str] = set()

    for row in concerns:
        title = str(row["title"])
        if title in seen_titles:
            continue
        seen_titles.add(title)
        actions.append(
            {
                "title": title,
                "lane": row["client"],
                "status": row["state"],
                "priority": row["priority"],
                "impact": shorten(
                    str(row["recommendation"] or row["challenge"] or row["requirement"]),
                    width=132,
                    placeholder="...",
                ),
            }
        )

    actions.append(
        {
            "title": "Stand up IFC delivery scaffolding",
            "lane": "IFC",
            "status": "watch",
            "priority": "P2",
            "impact": "Proposal scope includes IFC; build the lane, outputs, and refresh telemetry before final acceptance.",
        }
    )
    return actions[:7]


def build_readiness(aum_docs: dict[str, object], concerns: list[dict[str, object]]) -> list[dict[str, str]]:
    tag_counter = Counter(tag for row in concerns for tag in row["tags"])
    params = aum_docs["query_parameters"]
    fields = aum_docs["example_fields"]

    return [
        {
            "title": "People/account mapping",
            "status": "partial",
            "note": "MSCI explicitly requires canonical people-to-account mapping inside the main project scope.",
        },
        {
            "title": "Export automation",
            "status": "blocked" if tag_counter.get("manual_ops") else "ok",
            "note": f"{tag_counter.get('manual_ops', 0)} tracked concern(s) still reference manual calculations or external tools.",
        },
        {
            "title": "AUM schema exposure",
            "status": "partial",
            "note": f"Public docs expose {len(params)} query parameters and {len(fields)} example response fields, but the concern sheet still calls out subsidiary and strategy gaps.",
        },
        {
            "title": "Profile field completeness",
            "status": "blocked" if tag_counter.get("missing_fields") else "ok",
            "note": "The concern sheet calls out missing entity name, legal name, DBA, LEI, address, country, region, phone, state, city, and website fields.",
        },
        {
            "title": "Ops telemetry",
            "status": "partial",
            "note": "Proposal requires feed generation and refresh-state visibility in the private working surface.",
        },
    ]


def build_metric_cards(lanes: list[dict[str, object]], concerns: list[dict[str, object]], aum_docs: dict[str, object]) -> list[dict[str, str]]:
    tag_counter = Counter(tag for row in concerns for tag in row["tags"])
    return [
        {"label": "Client lanes", "value": str(len(lanes)), "note": "MSCI, Bloomberg, and IFC"},
        {
            "label": "Tracked blockers",
            "value": str(len(concerns)),
            "note": "Rows pulled from the live concern sheet",
        },
        {
            "label": "Automation targets",
            "value": str(tag_counter.get("automation", 0)),
            "note": "Rows explicitly pointing to backend automation",
        },
        {
            "label": "AUM filters",
            "value": str(len(aum_docs["query_parameters"])),
            "note": "Publicly documented query parameters",
        },
    ]


def build_statuses(concerns: list[dict[str, object]], aum_docs: dict[str, object]) -> list[dict[str, str]]:
    return [
        {"source": "Proposal", "status": "ok", "note": "Scope, deliverables, commercials, and timeline loaded"},
        {
            "source": "Client concerns",
            "status": "ok" if concerns else "fallback",
            "note": f"{len(concerns)} concern rows parsed from the live sheet",
        },
        {
            "source": "AUM docs",
            "status": "ok" if aum_docs["query_parameters"] else "fallback",
            "note": f"{len(aum_docs['query_parameters'])} parameters and {len(aum_docs['example_fields'])} example fields parsed",
        },
        {
            "source": "Competitive audit",
            "status": "ok",
            "note": "Preqin and BlackRock benchmark surfaces reviewed online",
        },
    ]


def build_dashboard_payload() -> dict[str, object]:
    concerns = load_concern_rows()
    aum_docs = parse_aum_docs()
    lanes = build_lane_summaries(concerns)

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "statuses": build_statuses(concerns, aum_docs),
        "proposal": PROPOSAL,
        "platform_reference": PLATFORM_REFERENCE,
        "metric_cards": build_metric_cards(lanes, concerns, aum_docs),
        "lanes": lanes,
        "concerns": concerns,
        "action_queue": build_action_queue(concerns),
        "aum_docs": aum_docs,
        "readiness": build_readiness(aum_docs, concerns),
        "competitor_benchmark": COMPETITOR_BENCHMARK,
        "required_api_stack": REQUIRED_API_STACK,
        "source_links": [
            {"label": "SWFI API docs", "url": API_HOME_URL},
            {"label": "Concern sheet", "url": PROPOSAL_SHEET_URL},
            {"label": "Preqin Pro", "url": "https://www.preqin.com/our-products/preqin-pro"},
            {"label": "Preqin data feeds", "url": "https://www.preqin.com/our-products/data-feeds"},
            {"label": "BlackRock Aladdin", "url": "https://www.blackrock.com/aladdin/products/aladdin-platform"},
        ],
    }


def get_dashboard_payload() -> dict[str, object]:
    now = time.time()
    with _cache_lock:
        cached = _dashboard_cache.get("payload")
        timestamp = float(_dashboard_cache.get("timestamp", 0.0))
        if cached and now - timestamp < CACHE_TTL_SECONDS:
            return cached

    payload = build_dashboard_payload()

    with _cache_lock:
        _dashboard_cache["timestamp"] = now
        _dashboard_cache["payload"] = payload
    return payload


def get_cached_dashboard_payload():
    with _cache_lock:
        return _dashboard_cache.get("payload")


def get_guardrail(query_text: str) -> str | None:
    lowered = query_text.lower().strip()
    if not lowered:
        return "Ask about client blockers, AUM schema, competitor gaps, or the required API stack."
    if any(token in lowered for token in ACTION_HINTS):
        return (
            "This copilot is read-only. It can analyze the product and API stack, but it will not log in, "
            "send messages, or execute workflow actions."
        )
    if any(token in lowered for token in NON_PRODUCT_HINTS):
        return (
            "This copilot is limited to SWFI product, workflow, competitor, and API-stack analysis."
        )
    return None


def make_evidence(label: str, source: str, url: str | None = None) -> dict[str, str | None]:
    return {"label": label, "source": source, "url": url}


def build_fallback_answer(query_text: str, payload: dict[str, object]) -> tuple[str, list[dict[str, str | None]]]:
    lowered = query_text.lower()
    concerns = payload["concerns"]
    lanes = {lane["name"].lower(): lane for lane in payload["lanes"]}
    evidence: list[dict[str, str | None]] = []
    parts: list[str] = []

    if "msci" in lowered and "msci" in lanes:
        lane = lanes["msci"]
        parts.append(
            f"MSCI is the heaviest active lane in the current sheet, with {lane['issue_count']} tracked blocker(s). "
            f"The dominant themes are {lane['focus'].lower()}."
        )
        evidence.append(make_evidence("MSCI concern rows", "Concern sheet", PROPOSAL_SHEET_URL))

    if "bloomberg" in lowered and "bloomberg" in lanes:
        lane = lanes["bloomberg"]
        parts.append(
            f"Bloomberg is a quarterly delivery lane with {lane['issue_count']} tracked blocker(s). "
            "The sheet emphasizes AUM coverage, allocation math, and currency normalization."
        )
        evidence.append(make_evidence("Bloomberg concern rows", "Concern sheet", PROPOSAL_SHEET_URL))

    if "ifc" in lowered and "ifc" in lanes:
        lane = lanes["ifc"]
        parts.append(
            f"IFC is in proposal scope but not yet represented in the live concern sheet. "
            f"Treat it as a scaffolded lane: {lane['deliverable']}."
        )
        evidence.append(make_evidence("Proposal scope", "Proposal", PROPOSAL_SHEET_URL))

    if any(token in lowered for token in ("aum", "api", "field", "schema")):
        docs = payload["aum_docs"]
        parts.append(
            f"The public AUM docs currently expose {len(docs['query_parameters'])} query parameter(s) and "
            f"{len(docs['example_fields'])} example response field(s). The biggest product gap is not basic AUM retrieval; "
            "it is client-specific coverage such as subsidiaries, active/passive strategy splits, and export-ready mappings."
        )
        evidence.append(make_evidence("AUM collection docs", "SWFI API docs", AUM_DOCS_URL))

    if any(token in lowered for token in ("manual", "excel", "automation", "currency")):
        manual_rows = [row for row in concerns if "manual_ops" in row["tags"] or "currency" in row["tags"]]
        parts.append(
            f"Manual operations remain a core blocker. The sheet explicitly calls out Excel-based allocation calculations "
            f"and manual currency conversion, and there are {len(manual_rows)} row(s) tied to those issues."
        )
        evidence.append(make_evidence("Manual workflow rows", "Concern sheet", PROPOSAL_SHEET_URL))

    if any(token in lowered for token in ("preqin", "competitor", "blackrock", "aladdin", "kkr")):
        parts.append(
            "Preqin is the direct product competitor on coverage plus delivery surfaces, while BlackRock Aladdin is the benchmark "
            "for API-first integration and enterprise data distribution. KKR is a credibility and customer benchmark, but not a "
            "public developer-platform benchmark in the same way."
        )
        evidence.append(make_evidence("Preqin Pro", "Official source", "https://www.preqin.com/our-products/preqin-pro"))
        evidence.append(make_evidence("Aladdin platform", "Official source", "https://www.blackrock.com/aladdin/products/aladdin-platform"))

    if any(token in lowered for token in ("what apis", "api stack", "integrations", "need to build")):
        parts.append(
            "To be competitive, SWFI needs more than domain objects. The missing categories are document-ingestion/extraction APIs, "
            "identity-resolution APIs, regulatory filings rails, CRM/data-lake delivery connectors, and stronger research/news enrichment."
        )
        evidence.append(make_evidence("Required API stack", "Competitive audit", "https://www.preqin.com/our-products/data-feeds"))

    if not parts:
        parts.append(
            "The current material points to three priorities: automate manual feed math and exports, close the missing-field and mapping gaps, "
            "and expand the API surface from raw collections into a true delivery platform with ingestion, review, and downstream sync."
        )
        evidence.append(make_evidence("Proposal + concern sheet", "Working packet", PROPOSAL_SHEET_URL))

    return " ".join(parts), evidence[:6]


def call_gemini_copilot(query_text: str, source_packet: dict[str, object]) -> str | None:
    if not GEMINI_API_KEY:
        return None

    payload = {
        "system_instruction": {"parts": [{"text": RESEARCH_SYSTEM_PROMPT}]},
        "contents": [
            {
                "parts": [
                    {
                        "text": json.dumps(
                            {
                                "user_query": query_text,
                                "source_packet": source_packet,
                                "task": "Answer with sourced operational analysis. Call out inference explicitly.",
                            }
                        )
                    }
                ]
            }
        ],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 360},
    }

    try:
        response = fetch_json(
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
            payload=payload,
            headers={"x-goog-api-key": GEMINI_API_KEY},
            timeout=20,
        )
    except Exception:
        return None

    candidates = response.get("candidates", [])
    if not candidates:
        return None
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "\n".join(part.get("text", "") for part in parts if part.get("text", "")).strip()
    return text or None


def build_research_payload(query_text: str) -> dict[str, object]:
    guardrail = get_guardrail(query_text)
    if guardrail:
        return {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "answer": guardrail,
            "evidence": [],
            "guardrail": "scope_limited",
            "model": None,
        }

    payload = get_cached_dashboard_payload() or get_dashboard_payload()
    fallback_answer, evidence = build_fallback_answer(query_text, payload)

    source_packet = {
        "proposal": {
            "goal": payload["proposal"]["goal"],
            "timeline": payload["proposal"]["timeline"],
            "deliverables": payload["proposal"]["deliverables"][:4],
        },
        "lanes": payload["lanes"],
        "top_concerns": payload["concerns"][:8],
        "aum_docs": {
            "path": payload["aum_docs"]["path"],
            "parameter_count": len(payload["aum_docs"]["query_parameters"]),
            "example_field_count": len(payload["aum_docs"]["example_fields"]),
            "collections": payload["aum_docs"]["collections"][:8],
        },
        "competitor_benchmark": payload["competitor_benchmark"],
        "required_api_stack": payload["required_api_stack"],
    }

    gemini_answer = call_gemini_copilot(query_text, source_packet)
    answer = gemini_answer or fallback_answer

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "answer": answer,
        "evidence": evidence,
        "guardrail": "source_grounded",
        "model": GEMINI_MODEL if gemini_answer else None,
    }


class SiteHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory or str(ROOT), **kwargs)

    def _write_json(self, payload: object, status: int = 200) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        parsed = parse.urlparse(self.path)

        if parsed.path == "/health":
            dashboard = get_cached_dashboard_payload()
            concern_count = len(dashboard.get("concerns", [])) if isinstance(dashboard, dict) else 0
            self._write_json({"status": "ok", "concerns": concern_count})
            return

        if parsed.path == "/api/dashboard":
            self._write_json(get_dashboard_payload())
            return

        if parsed.path == "/api/research":
            query_text = parse.parse_qs(parsed.query).get("q", [""])[0].strip()
            if not query_text:
                self._write_json({"error": "missing query"}, status=400)
                return
            self._write_json(build_research_payload(query_text))
            return

        super().do_GET()

    def send_head(self):
        path = self.translate_path(self.path)
        if self.path != "/" and not Path(path).exists() and not self.path.startswith("/api/"):
            self.path = "/index.html"
        return super().send_head()


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the SWFI terminal prototype")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8344)
    args = parser.parse_args()

    server = http.server.ThreadingHTTPServer((args.host, args.port), SiteHandler)
    print(f"SWFI terminal listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
