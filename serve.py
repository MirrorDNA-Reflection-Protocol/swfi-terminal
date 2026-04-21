#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import html
from http import cookies
import http.server
import io
import json
import os
import re
import secrets
import subprocess
import threading
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from textwrap import shorten
from urllib import error as urlerror, parse, request
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent
INPUTS_ROOT = ROOT / "data" / "inputs"
DOCS_ROOT = ROOT / "docs"
AI_DOCS_ROOT = DOCS_ROOT / "ai"

SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/1dVHsh2zmWrWsxSpMg3zEr7Je27XmAsnO/gviz/tq"
    "?tqx=out:csv&gid=251913671"
)
AUM_DOCS_URL = "https://api.swfi.com/collections/aum"
COLLECTIONS_URL = "https://api.swfi.com/collections"
API_HOME_URL = "https://api.swfi.com/"
PROPOSAL_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/1dVHsh2zmWrWsxSpMg3zEr7Je27XmAsnO/htmlview#gid=251913671"
)

TARGET_LIST_XLSX = Path(
    os.environ.get(
        "SWFI_TARGET_LIST_XLSX",
        str(INPUTS_ROOT / "target_list_top250_list_toClose(1).xlsx"),
    )
)
SWF_GLOBAL_CSV = Path(
    os.environ.get(
        "SWFI_SWF_GLOBAL_CSV",
        str(INPUTS_ROOT / "SWFs Global - Sheet4.csv"),
    )
)
PLATFORM_IMPROVEMENTS_CSV = Path(
    os.environ.get(
        "SWFI_PLATFORM_IMPROVEMENTS_CSV",
        str(INPUTS_ROOT / "Platform Improvements - Sheet1.csv"),
    )
)

CACHE_TTL_SECONDS = int(os.environ.get("DASHBOARD_TTL_SECONDS", "900"))
HTTP_USER_AGENT = os.environ.get("SWFI_TERMINAL_USER_AGENT", "SWFI Terminal/0.4")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5-mini").strip() or "gpt-5-mini"
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514").strip() or "claude-sonnet-4-20250514"
MSCI_EXPORT_TTL_SECONDS = int(os.environ.get("MSCI_EXPORT_TTL_SECONDS", "3600"))
SWFI_SANDBOX_API_ROOT = os.environ.get("SWFI_SANDBOX_API_ROOT", "https://sandbox-api.swfi.com/v1").rstrip("/")
SWFI_PUBLIC_SITE_ORIGIN = os.environ.get("SWFI_PUBLIC_SITE_ORIGIN", "https://swfi.com").rstrip("/")
_SECURITY_CONTACT_ENV = os.environ.get("SWFI_SECURITY_CONTACT_URI", "").strip()
SWFI_SECURITY_CONTACT_URI = _SECURITY_CONTACT_ENV or "mailto:security@swfi.com"
SWFI_SECURITY_CONTACT_CONFIGURED = bool(_SECURITY_CONTACT_ENV)
SWFI_SECURITY_POLICY_URL = os.environ.get("SWFI_SECURITY_POLICY_URL", "").strip()
SWFI_EXPORT_AUDIT_LOG = Path(
    os.environ.get(
        "SWFI_EXPORT_AUDIT_LOG",
        str(Path.home() / "Library/Logs/swfi-terminal/export_audit.jsonl"),
    )
)
RESEARCH_RATE_LIMIT_PER_MINUTE = int(os.environ.get("SWFI_RESEARCH_RATE_LIMIT_PER_MINUTE", "24"))
EXPORT_RATE_LIMIT_PER_MINUTE = int(os.environ.get("SWFI_EXPORT_RATE_LIMIT_PER_MINUTE", "10"))
LOGIN_RATE_LIMIT_PER_15_MIN = int(os.environ.get("SWFI_LOGIN_RATE_LIMIT_PER_15_MIN", "12"))
PREVIEW_SESSION_TTL_SECONDS = int(os.environ.get("SWFI_PREVIEW_SESSION_TTL_SECONDS", "43200"))
CONNECTOR_PROBE_TTL_SECONDS = int(os.environ.get("SWFI_CONNECTOR_PROBE_TTL_SECONDS", "21600"))

ATLAS_URI = os.environ.get("SWFI_ATLAS_URI", "").strip()
ATLAS_DB = os.environ.get("SWFI_ATLAS_DB", "swfi_terminal_preview").strip() or "swfi_terminal_preview"
ATLAS_COLLECTION = (
    os.environ.get("SWFI_ATLAS_COLLECTION", "materialized_packets").strip() or "materialized_packets"
)

DASHBOARD_SCHEMA_VERSION = "swfi.dashboard.v1"
RESEARCH_SCHEMA_VERSION = "swfi.research.v1"
MSCI_SCHEMA_VERSION = "swfi.msci_workbench.v1"
ADMIN_SCHEMA_VERSION = "swfi.admin.v1"
PREVIEW_ROUTE = "/preview"
AI_POLICY_VERSION = "swfi.policy.ai_governance.v0_1"
PROMPT_REGISTRY_VERSION = "swfi.prompt_registry.v1"
GROUNDED_RESEARCH_PROMPT_ID = "swfi.prompt.answer.grounded_v1"
REFUSAL_PROMPT_ID = "swfi.prompt.refuse.unsupported_v1"
NUGGET_SCHEMA_VERSION = "swfi.nugget.v1"
ANTHROPIC_API_VERSION = "2023-06-01"

XLSX_NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}

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
            "note": "Authenticated IA review informed alignment; no private data persisted",
        },
        {
            "label": "Collections surface",
            "value": "api.swfi.com/collections",
            "note": "Collection names are masked publicly, but the object families are visible",
        },
    ],
}

PROPOSAL = {
    "title": "SWFI Feed Modernization and Client Delivery System",
    "goal": (
        "Build a private working surface at swfi.activemirror.ai that modernizes feed delivery, "
        "normalizes outputs, and gives operators a refresh-state and audit surface."
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
}

CLIENT_PRESETS = {
    "MSCI": {
        "status": "active",
        "cadence": "Rolling delivery + quarterly revisit cycle",
        "focus": "Key People, Asset Allocation, and managed-assets splits",
        "deliverable": "Key People export and account mapping",
    },
    "Bloomberg": {
        "status": "active",
        "cadence": "Quarterly delivery lane",
        "focus": "Financial institution coverage, currency-normalized AUM, and Asset Allocation fields",
        "deliverable": "Datafeed with normalized AUM outputs",
    },
    "IFC": {
        "status": "scaffolded",
        "cadence": "Pending detailed workflow pack",
        "focus": "Alternatives coverage, profiles, and controlled delivery",
        "deliverable": "Controlled client output",
    },
}

PRIVATE_IA_NOTE = (
    "Authenticated review informed IA alignment; no private data persisted in the repo or preview packet."
)

COLLECTION_MODEL = [
    {
        "name": "Entities",
        "status": "partial",
        "summary": "Institution profiles with child entities such as subsidiaries and funds.",
        "sample_fields": ["name", "LegalName", "State", "City", "Address", "Summary", "associatedNews", "type"],
    },
    {
        "name": "Financials",
        "status": "partial",
        "summary": "AUM and managedAUM histories with total-assets and asset-class breakout ambiguity.",
        "sample_fields": ["assets", "equities", "realAssets", "realEstate", "infrastructure", "managedAssets"],
    },
    {
        "name": "People",
        "status": "blocked",
        "summary": "People, peopleHistory, and peopleEducation drive the MSCI export ask, but require private access and cleanup.",
        "sample_fields": ["name", "title", "email", "phone", "personHistory", "education", "entityId"],
    },
    {
        "name": "Transactions",
        "status": "partial",
        "summary": "Fund commitments and deals with sector/industry context and sometimes missing disclosed values.",
        "sample_fields": ["sector", "industries", "amount", "entity", "announcementDate", "investmentType"],
    },
    {
        "name": "Compass / RFP",
        "status": "partial",
        "summary": "Institutional procurement and opportunity records associated with entities and investment strategies.",
        "sample_fields": ["opportunityId", "entityId", "investmentStrategy", "deadline", "region"],
    },
    {
        "name": "News",
        "status": "partial",
        "summary": "Relevant stories and associatedNews links used to enrich profiles and alerts.",
        "sample_fields": ["headline", "publishedAt", "entityIds", "storyType", "sourceUrl"],
    },
]

SOURCE_TAXONOMY = [
    {
        "family": "Transactions",
        "sources": [
            "BusinessWire and other release wires",
            "News sites and email newsletters such as Axios",
            "Company websites",
            "Exchange disclosures",
        ],
    },
    {
        "family": "People",
        "sources": [
            "Company websites",
            "LinkedIn with stale-data caution",
            "Guessed email formats tested externally and Apollo enrichment",
            "Interviews and surveys (lower recent usage)",
            "Conference and association websites",
        ],
    },
    {
        "family": "Entities",
        "sources": [
            "Company websites",
            "Board minutes and agendas",
            "Structured and unstructured filings, including PDF/PPT assets",
            "Interviews and surveys (lower recent usage)",
            "News sites with credibility screening",
        ],
    },
    {
        "family": "Enhancers",
        "sources": [
            "Google Alerts",
            "RSS feeds",
            "Internal long-running standardization process",
            "PDF/image extraction for scattered asset-allocation disclosures",
        ],
    },
]

CANONICAL_SCHEMA = [
    {
        "name": "institution",
        "primary_key": "institution_id",
        "joins": ["fund", "person_contact", "document", "opportunity_rfp", "compliance_event", "research_item"],
        "fields": [
            "institution_id",
            "source_refs",
            "display_name",
            "legal_name",
            "institution_type",
            "country",
            "region",
            "address",
            "website",
            "profile_status",
        ],
    },
    {
        "name": "fund",
        "primary_key": "fund_id",
        "joins": ["institution", "asset_aum_series", "document", "research_item"],
        "fields": [
            "fund_id",
            "institution_id",
            "fund_name",
            "strategy",
            "vintage_year",
            "status",
            "country",
            "currency",
            "source_refs",
        ],
    },
    {
        "name": "asset_aum_series",
        "primary_key": "aum_series_id",
        "joins": ["institution", "fund", "document"],
        "fields": [
            "aum_series_id",
            "owner_type",
            "owner_id",
            "as_of_date",
            "total_assets",
            "managed_assets",
            "asset_class_breakout",
            "currency",
            "method_notes",
        ],
    },
    {
        "name": "person_contact",
        "primary_key": "person_id",
        "joins": ["institution", "document", "research_item"],
        "fields": [
            "person_id",
            "institution_id",
            "full_name",
            "title",
            "department",
            "seniority",
            "email",
            "phone",
            "employment_status",
            "verified_at",
        ],
    },
    {
        "name": "document",
        "primary_key": "document_id",
        "joins": ["institution", "fund", "asset_aum_series", "person_contact", "compliance_event"],
        "fields": [
            "document_id",
            "document_type",
            "title",
            "entity_refs",
            "published_at",
            "source_url",
            "file_pointer",
            "extraction_status",
            "raw_hash",
        ],
    },
    {
        "name": "opportunity_rfp",
        "primary_key": "opportunity_id",
        "joins": ["institution", "document", "research_item"],
        "fields": [
            "opportunity_id",
            "institution_id",
            "title",
            "investment_strategy",
            "region",
            "deadline",
            "status",
            "source_refs",
            "last_seen_at",
        ],
    },
    {
        "name": "compliance_event",
        "primary_key": "compliance_event_id",
        "joins": ["institution", "fund", "document"],
        "fields": [
            "compliance_event_id",
            "institution_id",
            "event_type",
            "jurisdiction",
            "event_date",
            "filing_reference",
            "status",
            "evidence_ref",
            "watchlist_hit",
        ],
    },
    {
        "name": "research_item",
        "primary_key": "research_item_id",
        "joins": ["institution", "fund", "person_contact", "document"],
        "fields": [
            "research_item_id",
            "headline",
            "item_type",
            "published_at",
            "entity_refs",
            "importance",
            "summary",
            "source_url",
            "confidence",
        ],
    },
]

PROVENANCE_CONTRACT = {
    "required_fields": [
        "source_system",
        "retrieval_time",
        "extraction_method",
        "confidence",
        "status",
        "evidence_url_or_pointer",
    ],
    "example": {
        "source_system": "swfi_public_api",
        "retrieval_time": "2026-04-17T09:30:00Z",
        "extraction_method": "html_parse",
        "confidence": "high",
        "status": "sourced",
        "evidence_url_or_pointer": "https://api.swfi.com/collections/aum",
    },
}

PLATFORM_FEEDBACK = {
    "overall_score": "5/10",
    "top_challenges": [
        "Data inaccuracy and insufficient depth across contacts, AUM, transactions, and entity profiles",
        "Persistent slowness and instability that undermine demo credibility",
        "No AI or intelligent search capability",
        "Lack of social proof and visible case studies",
        "Weak marketing presence and awareness before demos",
    ],
    "top_recommendations": [
        "Audit and fix top-500 entity data quality for contacts, AUM, and transactions",
        "Implement the sales tech stack and one-click export infrastructure",
        "Publish case studies, testimonials, and logos",
        "Ship AI assistant / chatbot and tiered pricing",
        "Rebuild marketing and research publication cadence",
    ],
    "integration_gaps": [
        "CRM sync for HubSpot and Salesforce",
        "LinkedIn Sales Navigator and outreach-platform exports",
        "API access for enterprise clients",
        "Zapier / Make automation hooks",
        "Role / department / seniority segmentation for contact lists",
    ],
    "sales_risk": "Approximately 60% of demos involve data skepticism.",
}

EMAIL_AUTOMATION_STREAMS = {
    "streams": [
        {
            "name": "Asset Owner Platform Alerts",
            "audience": "Paid SWFI subscribers",
            "cadence": "Daily",
            "transport": "Mandrill",
            "collections": ["Transactions", "Compass", "People"],
            "status": "private_source_required",
        },
        {
            "name": "Public Fund Monitor",
            "audience": "~200,000 public list",
            "cadence": "Every 3 days",
            "transport": "SendGrid",
            "collections": ["Transactions", "Compass", "People"],
            "status": "private_source_required",
        },
    ]
}

BENCHMARK_MATRIX = [
    {
        "name": "SWFI",
        "tone": "watch",
        "product_benchmark": "Strong sovereign/institutional niche, but trust and depth issues still dominate buyer feedback.",
        "api_benchmark": "Public AUM docs exist, but delivery jobs, canonical exports, and private people/account APIs are missing.",
        "ux_benchmark": "Dense authenticated IA exists, but feedback still scores the platform 5/10 on speed and usability.",
    },
    {
        "name": "Preqin",
        "tone": "partial",
        "product_benchmark": "Direct coverage and workflow benchmark for investors, deals, performance, mandates, and delivery.",
        "api_benchmark": "Data feeds, API delivery, CRM workflows, and ongoing contact / RFP product updates are all visible publicly.",
        "ux_benchmark": "Institutional operator benchmark for research, saved searches, target lists, and data-backed workflows.",
    },
    {
        "name": "PitchBook",
        "tone": "partial",
        "product_benchmark": "Major private-capital benchmark across companies, investors, funds, deals, and people.",
        "api_benchmark": "Direct Data exposes feeds, API, sandboxing, and CRM plugins for Salesforce, HubSpot, and Dynamics.",
        "ux_benchmark": "Strong workflow benchmark across Excel, PowerPoint, Chrome, and conversational AI partnerships.",
    },
    {
        "name": "Bloomberg",
        "tone": "partial",
        "product_benchmark": "Enterprise benchmark on breadth, real-time data, documents, analytics, and collaboration.",
        "api_benchmark": "Server API, unified data-model delivery, entitlements management, and warehouse delivery are all public.",
        "ux_benchmark": "AI-powered research, mobile continuity, and integrated collaboration make this the enterprise UX benchmark.",
    },
    {
        "name": "BlackRock Aladdin",
        "tone": "partial",
        "product_benchmark": "Platform benchmark rather than direct data competitor.",
        "api_benchmark": "API-first and data-cloud benchmark with read/write APIs, data dictionary, and expanding API surface.",
        "ux_benchmark": "Institutional system-of-record benchmark with Copilot and private-markets integration depth.",
    },
    {
        "name": "KKR",
        "tone": "watch",
        "product_benchmark": "Institutional credibility and target-account benchmark.",
        "api_benchmark": "No comparable public developer surface found in this review.",
        "ux_benchmark": "Brand and institutional trust benchmark, not a direct API model.",
    },
]

REQUIRED_API_STACK = [
    {
        "name": "Core SWFI domain APIs",
        "status": "partial",
        "why": "Entities, people, transactions, Compass, news, and AUM are the product spine.",
        "gap": "Need stable authenticated contracts, per-client jobs, saved views, and entitlement-aware exports.",
        "sources": [{"label": "SWFI collections", "url": COLLECTIONS_URL}],
    },
    {
        "name": "Document ingestion and extraction",
        "status": "blocked",
        "why": "Board minutes, filings, PDFs, PPTs, and image-heavy disclosures drive hard-to-structure facts.",
        "gap": "Need document import, OCR/extraction, review queues, and evidence pointers.",
        "sources": [],
    },
    {
        "name": "Identity and registry resolution",
        "status": "blocked",
        "why": "Canonical institution / fund / people mapping needs legal-entity and registry joins.",
        "gap": "Need LEI and corporate registry lookups for standardization.",
        "sources": [
            {"label": "GLEIF API", "url": "https://www.gleif.org/en/lei-data/gleif-lei-look-up-api/access-the-api"},
            {"label": "Companies House API", "url": "https://developer.company-information.service.gov.uk/"},
        ],
    },
    {
        "name": "Regulatory / filings rails",
        "status": "partial",
        "why": "Asset-allocation and compliance facts are often scattered in filings, board packs, and sanctions rails.",
        "gap": "Need first-party filing connectors and watchlist ingestion.",
        "sources": [
            {"label": "SEC APIs", "url": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces"},
            {"label": "OFAC Sanctions List Service", "url": "https://ofac.treasury.gov/sanctions-list-service"},
        ],
    },
    {
        "name": "CRM / warehouse delivery",
        "status": "blocked",
        "why": "Sales feedback explicitly calls out missing CRM sync and one-click list delivery.",
        "gap": "Need Salesforce, Snowflake, and Graph connectors plus outbound export jobs.",
        "sources": [
            {"label": "Salesforce APIs", "url": "https://developer.salesforce.com/docs/apis"},
            {"label": "Snowflake SQL API", "url": "https://docs.snowflake.com/en/developer-guide/sql-api/index"},
            {"label": "Microsoft Graph", "url": "https://learn.microsoft.com/en-us/graph/overview"},
        ],
    },
    {
        "name": "Entitlements / monitoring / unified data model",
        "status": "blocked",
        "why": "Bloomberg exposes entitlements control, activity monitoring, and unified data delivery as standard enterprise capabilities.",
        "gap": "Need permission-aware exports, usage telemetry, monitoring, and a consistent cross-collection field model.",
        "sources": [
            {"label": "Bloomberg SAPI", "url": "https://professional.bloomberg.com/products/data/data-connectivity/server-api/"},
            {"label": "Bloomberg Data License Plus", "url": "https://professional.bloomberg.com/products/data/data-management/dms/"},
        ],
    },
    {
        "name": "Email / alert delivery APIs",
        "status": "partial",
        "why": "Daily subscriber alerts and the public newsletter already exist as automated streams.",
        "gap": "Need observable job state, transport telemetry, and evidence-backed send logs in the terminal.",
        "sources": [
            {"label": "Mandrill", "url": "https://mailchimp.com/developer/transactional/"},
            {"label": "SendGrid", "url": "https://www.twilio.com/docs/sendgrid/api-reference"},
        ],
    },
    {
        "name": "AI search and operator copilots",
        "status": "blocked",
        "why": "Feedback repeatedly flags the lack of natural-language search and smart recommendations.",
        "gap": "Need source-grounded query, saved alerts, explainable retrieval, and operator copilots comparable to current market leaders.",
        "sources": [
            {"label": "PitchBook AI partnerships", "url": "https://pitchbook.com/media/press-releases/pitchbook-announces-new-essential-mcp-integration-with-perplexity-expanding-access-to-ai-powered-verifiable-market-intelligence"},
            {"label": "Bloomberg AI", "url": "https://professional.bloomberg.com/solutions/ai"},
            {"label": "Aladdin Copilot", "url": "https://www.blackrock.com/aladdin/solutions/aladdin-copilot"},
        ],
    },
]

EXTERNAL_API_MATRIX = [
    {
        "name": "GLEIF LEI API",
        "access": "free_public",
        "status": "ok",
        "use_case": "Legal-entity normalization, parent-child resolution, fuzzy matching, LEI backfill.",
        "note": "Official production API. Supports ownership data, fuzzy matching, and mapped identifiers such as BIC or ISIN.",
        "url": "https://www.gleif.org/en/lei-data/gleif-lei-look-up-api/access-the-api",
    },
    {
        "name": "SEC EDGAR / data.sec.gov",
        "access": "free_public",
        "status": "ok",
        "use_case": "Filings, XBRL company facts, submissions, and RSS-based filing monitoring.",
        "note": "Official public JSON APIs, HTTPS filing access, and RSS feeds. Follow SEC fair-access guidance and user-agent rules.",
        "url": "https://www.sec.gov/about/developer-resources",
    },
    {
        "name": "Companies House API",
        "access": "free_public_with_key",
        "status": "ok",
        "use_case": "UK entity registry lookups, officers, filings history, and sandbox testing.",
        "note": "Official API is public but requires registration and an API key. Default rate limit is 600 requests per 5 minutes.",
        "url": "https://developer.company-information.service.gov.uk/get-started",
    },
    {
        "name": "OFAC Sanctions List Service",
        "access": "free_public",
        "status": "ok",
        "use_case": "Compliance-event enrichment, sanctions watch checks, and downloadable screening data.",
        "note": "Official public sanctions data service and search interface.",
        "url": "https://ofac.treasury.gov/ofac-sanctions-lists",
    },
    {
        "name": "OpenFIGI API",
        "access": "free_public",
        "status": "partial",
        "use_case": "Instrument identifier normalization for securities-linked transaction and holdings rails.",
        "note": "Free public API with lower unauthenticated rate limits. Use v3; OpenFIGI documents v2 sunset on July 1, 2026.",
        "url": "https://www.openfigi.com/api/documentation",
    },
    {
        "name": "OpenCorporates API",
        "access": "hybrid_open_or_paid",
        "status": "watch",
        "use_case": "Cross-jurisdiction company backfill and reconciliation.",
        "note": "Free for open-data projects under share-alike terms; commercial use and broader rights move into paid API accounts.",
        "url": "https://api.opencorporates.com/",
    },
    {
        "name": "NewsAPI",
        "access": "paid_for_production",
        "status": "blocked",
        "use_case": "Headline/news enrichment.",
        "note": "Developer tier is free only for development and testing, not production use.",
        "url": "https://newsapi.org/pricing",
    },
]

MSCI_REQUESTED_FIELDS = [
    {
        "field": "SWFI Contact ID",
        "status": "ok",
        "availability": "Available from authenticated sandbox and production people sources",
        "note": "The people endpoint exposes a stable contact identifier that can be exported directly.",
    },
    {
        "field": "SWFI Account (Company) ID",
        "status": "ok",
        "availability": "Available from people history.entity_id and entity joins",
        "note": "The account identifier can be resolved from active or latest history rows and exported directly.",
    },
    {
        "field": "Name",
        "status": "ok",
        "availability": "Available now",
        "note": "Available directly from the people endpoint.",
    },
    {
        "field": "Email",
        "status": "partial",
        "availability": "Available where populated; verification still recommended",
        "note": "The authenticated people source exposes email, but quality still needs downstream verification before high-trust outreach.",
    },
    {
        "field": "Title",
        "status": "ok",
        "availability": "Available now",
        "note": "Resolved from the active or latest people history row.",
    },
    {
        "field": "Account Name",
        "status": "ok",
        "availability": "Available now",
        "note": "Resolved from the joined entity record when an entity_id is present.",
    },
    {
        "field": "Phone",
        "status": "partial",
        "availability": "Available where populated; validation still recommended",
        "note": "The people source exposes phone where present, but completeness remains uneven.",
    },
    {
        "field": "Relevant metadata",
        "status": "ok",
        "availability": "Available now",
        "note": "Recommended metadata includes institution type, city, state, country, region, LinkedIn, source confidence, and evidence pointers.",
    },
]

SANDBOX_COLLECTIONS = [
    {"name": "aum", "family": "core"},
    {"name": "aum-managed", "family": "core"},
    {"name": "compass", "family": "core"},
    {"name": "entities", "family": "core"},
    {"name": "news", "family": "core"},
    {"name": "people", "family": "core"},
    {"name": "reports", "family": "core"},
    {"name": "subsidiaries", "family": "core"},
    {"name": "transactions", "family": "core"},
    {"name": "advisors", "family": "referential"},
    {"name": "countries", "family": "referential"},
    {"name": "currencies", "family": "referential"},
    {"name": "entities-types", "family": "referential"},
    {"name": "industries", "family": "referential"},
    {"name": "investment-types", "family": "referential"},
    {"name": "news-tags", "family": "referential"},
    {"name": "regions", "family": "referential"},
    {"name": "sectors", "family": "referential"},
    {"name": "security-types", "family": "referential"},
]

COMPANY_SUFFIXES = {
    "inc",
    "inc.",
    "corp",
    "corp.",
    "corporation",
    "company",
    "companies",
    "co",
    "co.",
    "group",
    "holdings",
    "holding",
    "llc",
    "ltd",
    "ltd.",
    "limited",
    "plc",
    "sa",
    "ag",
    "lp",
    "llp",
    "partners",
}

RESEARCH_SYSTEM_PROMPT = """
You are SWFI Ops Copilot inside a private feed modernization terminal.
You are a read-only analysis assistant.

Allowed scope:
- canonical schema and provenance
- client feed workflows and exports
- data coverage, blockers, and gaps
- AUM/API readiness
- competitive benchmarking
- Atlas preview posture and launch readiness

Rules:
- Use only the provided source packet.
- Distinguish sourced facts from inference.
- Do not claim hidden access or stored private data.
- Stay concise, operational, and product-focused.
""".strip()

RESEARCH_GOVERNED_SYSTEM_PROMPT = """
You are SWFI governed research inside a controlled-access intelligence terminal.
You are not allowed to invent or expand beyond the approved answer seed and evidence catalog.

Rules:
- Use only the supplied approved_context.
- Rewrite or tighten the answer_seed; do not introduce new facts, numbers, dates, institutions, or claims.
- Distinguish direct support from interpretation.
- If the support is weak or partial, reduce confidence and use status NeedsReview.
- If the evidence does not support a reliable answer, refuse using the approved refusal language.
- Return JSON only with keys: answer, status, confidence, source_labels, inference_note.
- status must be one of Verified, Derived, Conflicted, Missing, NeedsReview, Rejected.
- confidence must be one of High, Medium, Low, None.
- source_labels must refer only to labels present in the evidence catalog.
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
_sandbox_request_lock = threading.Lock()
_dashboard_build_lock = threading.Lock()
_request_rate_lock = threading.Lock()
_audit_log_lock = threading.Lock()
_session_lock = threading.Lock()
_dashboard_cache: dict[str, object] = {"timestamp": 0.0, "payload": None}
_sandbox_cache: dict[str, object] = {"timestamp": 0.0, "payload": None}
_msci_people_summary_cache: dict[str, object] = {"timestamp": 0.0, "payload": None}
_msci_people_export_cache: dict[str, object] = {"timestamp": 0.0, "payload": None}
_external_probe_cache: dict[str, object] = {"timestamp": 0.0, "payload": None}
_request_rate_cache: dict[tuple[str, str], list[float]] = defaultdict(list)
_session_store: dict[str, dict[str, object]] = {}
_sandbox_last_request = 0.0


def load_secret_from_env_or_keychain(*secret_names: str) -> str:
    for secret_name in secret_names:
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

    for secret_name in secret_names:
        key = os.environ.get(secret_name, "").strip()
        if key:
            return key
    return ""


OPENAI_API_KEY = load_secret_from_env_or_keychain("OPENAI_API_KEY")
GEMINI_API_KEY = load_secret_from_env_or_keychain("GEMINI_API_KEY", "GOOGLE_API_KEY")
ANTHROPIC_API_KEY = load_secret_from_env_or_keychain("ANTHROPIC_API_KEY", "CLAUDE_API_KEY")
SWFI_SANDBOX_API_KEY = load_secret_from_env_or_keychain("SWFI_SANDBOX_API_KEY")
SWFI_PRIVATE_EXPORT_TOKEN = load_secret_from_env_or_keychain("SWFI_PRIVATE_EXPORT_TOKEN")
COMPANIES_HOUSE_API_KEY = load_secret_from_env_or_keychain("COMPANIES_HOUSE_API_KEY")
OPENCORPORATES_API_TOKEN = load_secret_from_env_or_keychain("OPENCORPORATES_API_TOKEN")
NEWSAPI_KEY = load_secret_from_env_or_keychain("NEWSAPI_KEY")
_PREVIEW_AUTH_USERNAME_SECRET = load_secret_from_env_or_keychain("SWFI_PREVIEW_AUTH_USERNAME")
_PREVIEW_AUTH_PASSWORD_SECRET = load_secret_from_env_or_keychain("SWFI_PREVIEW_AUTH_PASSWORD")
SWFI_PREVIEW_AUTH_USERNAME = _PREVIEW_AUTH_USERNAME_SECRET or "swfi-preview"
SWFI_PREVIEW_AUTH_PASSWORD = _PREVIEW_AUTH_PASSWORD_SECRET or secrets.token_urlsafe(24)
SWFI_SESSION_SECRET = load_secret_from_env_or_keychain("SWFI_SESSION_SECRET") or secrets.token_urlsafe(32)
SESSION_COOKIE_NAME = "swfi_preview_session"

# --- demo surface state -------------------------------------------------------
_demo_cache_lock = threading.Lock()
_demo_entity_cache: dict = {}
_demo_cache_loaded_at: float = 0.0
_DEMO_CACHE_TTL_SECONDS = 6 * 3600  # refresh entity packet every 6h
DEMO_ASK_LOG = Path(os.path.expanduser("~/Library/Logs/swfi-terminal/demo-ask.log"))
# --- end demo surface state ---------------------------------------------------


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def normalize_text(value: str) -> str:
    return " ".join(value.replace("\xa0", " ").split())


def strip_tags(value: str) -> str:
    return normalize_text(re.sub(r"<[^>]+>", " ", value))


def human_number(value: float) -> str:
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.1f}T"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def to_number(value: object) -> float:
    text = str(value or "").strip().replace(",", "").replace("$", "")
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def make_provenance(
    source_system: str,
    retrieval_time: str,
    extraction_method: str,
    confidence: str,
    status: str,
    *,
    evidence_url: str | None = None,
    document_pointer: str | None = None,
) -> dict[str, str | None]:
    return {
        "source_system": source_system,
        "retrieval_time": retrieval_time,
        "extraction_method": extraction_method,
        "confidence": confidence,
        "status": status,
        "evidence_url_or_pointer": evidence_url or document_pointer,
    }


def make_source_entry(
    source_id: str,
    label: str,
    classification: str,
    source_system: str,
    retrieval_time: str,
    extraction_method: str,
    confidence: str,
    status: str,
    *,
    evidence_url: str | None = None,
    document_pointer: str | None = None,
    note: str | None = None,
) -> dict[str, str | None]:
    entry = {
        "id": source_id,
        "label": label,
        "classification": classification,
        "source_system": source_system,
        "retrieval_time": retrieval_time,
        "extraction_method": extraction_method,
        "confidence": confidence,
        "status": status,
        "evidence_url": evidence_url,
        "document_pointer": document_pointer,
        "note": note,
    }
    return entry


def merge_sources(*groups: list[dict[str, str | None]]) -> list[dict[str, str | None]]:
    merged: dict[str, dict[str, str | None]] = {}
    for group in groups:
        for item in group:
            merged[str(item["id"])] = item
    return list(merged.values())


def build_confidence_summary(sources: list[dict[str, str | None]]) -> dict[str, object]:
    confidence_counts = Counter(str(item.get("confidence", "unknown")) for item in sources)
    status_counts = Counter(str(item.get("status", "unknown")) for item in sources)
    return {
        "high": confidence_counts.get("high", 0),
        "medium": confidence_counts.get("medium", 0),
        "low": confidence_counts.get("low", 0),
        "private_sources": sum(1 for item in sources if item.get("classification") == "authenticated_private_source"),
        "blocked_sources": status_counts.get("blocked", 0) + status_counts.get("fallback", 0),
        "summary": "High-confidence public, local, and authenticated sandbox packets are present, but production still needs export protection, audit logging, and contact-quality controls.",
    }


def fetch_text(url: str, *, timeout: int = 20, headers: dict[str, str] | None = None) -> str:
    request_headers = {"User-Agent": HTTP_USER_AGENT, **(headers or {})}
    req = request.Request(url, headers=request_headers)
    with request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_json(
    url: str,
    *,
    payload: object | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 20,
):
    request_headers = {"User-Agent": HTTP_USER_AGENT, **(headers or {})}
    data = None
    if payload is not None:
        request_headers.setdefault("Content-Type", "application/json")
        data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, headers=request_headers, data=data)
    with request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def local_pointer(path: Path) -> str:
    return str(path)


def display_collection_name(name: str) -> str:
    return name.replace("-", " ").title()


def normalize_company_key(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9 ]+", " ", (value or "").lower().replace("&", " and "))
    parts = [part for part in cleaned.split() if part and part not in COMPANY_SUFFIXES]
    return " ".join(parts)


def pick_person_history_row(person: dict[str, object]) -> dict[str, object]:
    history = [item for item in (person.get("history") or []) if isinstance(item, dict)]
    if not history:
        return {}

    active_rows = [item for item in history if item.get("active")]
    rows = active_rows or history

    def sort_key(item: dict[str, object]) -> tuple[str, str, str]:
        return (
            str(item.get("ended_at") or ""),
            str(item.get("started_at") or ""),
            str(item.get("created_at") or ""),
        )

    return sorted(rows, key=sort_key, reverse=True)[0]


def derive_row_confidence(*values: object) -> str:
    present = sum(1 for value in values if str(value or "").strip())
    if present >= 6:
        return "high"
    if present >= 4:
        return "medium"
    return "low"


def fetch_sandbox_json(path: str, *, params: dict[str, object] | None = None, timeout: int = 20):
    global _sandbox_last_request
    if not SWFI_SANDBOX_API_KEY:
        raise RuntimeError("missing sandbox credentials")

    url = f"{SWFI_SANDBOX_API_ROOT}/{path.lstrip('/')}"
    if params:
        pairs = [(key, value) for key, value in params.items() if value not in ("", None)]
        if pairs:
            url = f"{url}?{parse.urlencode(pairs, doseq=True)}"

    with _sandbox_request_lock:
        now = time.time()
        wait_seconds = 0.12 - (now - _sandbox_last_request)
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        _sandbox_last_request = time.time()

    return fetch_json(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": SWFI_SANDBOX_API_KEY,
        },
        timeout=timeout,
    )


def fetch_sandbox_entity_for_export(entity_id: str) -> tuple[str, dict[str, object]]:
    try:
        payload = fetch_json(
            f"{SWFI_SANDBOX_API_ROOT}/entities/{entity_id}",
            headers={
                "Accept": "application/json",
                "Authorization": SWFI_SANDBOX_API_KEY,
            },
            timeout=20,
        )
        return entity_id, (payload.get("data") or {})
    except Exception:
        return entity_id, {}


def build_sandbox_api_map() -> dict[str, object]:
    retrieved_at = iso_now()
    source = make_source_entry(
        "swfi_sandbox_api",
        "SWFI sandbox API",
        "authenticated_private_source",
        "swfi_sandbox_api",
        retrieved_at,
        "rest_api_probe",
        "high" if SWFI_SANDBOX_API_KEY else "low",
        "ok" if SWFI_SANDBOX_API_KEY else "blocked",
        evidence_url=SWFI_SANDBOX_API_ROOT,
        note="Sandbox API surface used for MSCI export validation and field mapping.",
    )
    if not SWFI_SANDBOX_API_KEY:
        source["note"] = "Sandbox API key not configured."
        return {
            "status": "blocked",
            "tone": "blocked",
            "api_root": SWFI_SANDBOX_API_ROOT,
            "auth_mode": "Authorization header",
            "rate_limit": "10 requests per second (public docs)",
            "collections": [],
            "summary": {"core": 0, "referential": 0, "accessible_collections": 0},
            "source": source,
        }

    failures = 0
    people_total = ""
    try:
        people_probe = fetch_sandbox_json("people", params={"limit": 1})
        people_total = int(people_probe.get("total_items", 0))
    except Exception as exc:
        failures = 1
        source["status"] = "blocked"
        source["confidence"] = "low"
        source["note"] = f"Sandbox probe failed: {exc.__class__.__name__}"
        return {
            "status": "blocked",
            "tone": "blocked",
            "api_root": SWFI_SANDBOX_API_ROOT,
            "auth_mode": "Authorization header",
            "rate_limit": "10 requests per second (public docs)",
            "collections": [],
            "summary": {"core": 0, "referential": 0, "accessible_collections": 0},
            "source": source,
        }

    collections = [
        {
            "name": spec["name"],
            "label": display_collection_name(spec["name"]),
            "family": spec["family"],
            "status": "ok",
            "total_items": people_total if spec["name"] == "people" else "",
            "sample_fields": [],
            "note": "Authenticated core collection documented and available via sandbox."
            if spec["family"] == "core"
            else "Documented referential collection available via the SWFI sandbox contract.",
        }
        for spec in SANDBOX_COLLECTIONS
    ]

    source["status"] = "ok"
    source["confidence"] = "high"
    source["note"] = "Sandbox contract verified via authenticated probe; documented collections are mapped into the terminal."
    return {
        "status": "ok",
        "tone": "ok",
        "api_root": SWFI_SANDBOX_API_ROOT,
        "auth_mode": "Authorization header",
        "rate_limit": "10 requests per second (public docs)",
        "collections": collections,
        "summary": {
            "core": sum(1 for item in collections if item["family"] == "core"),
            "referential": sum(1 for item in collections if item["family"] == "referential"),
            "accessible_collections": sum(1 for item in collections if item["status"] == "ok"),
        },
        "source": source,
    }


def get_sandbox_api_map() -> dict[str, object]:
    now = time.time()
    with _cache_lock:
        cached = _sandbox_cache.get("payload")
        timestamp = float(_sandbox_cache.get("timestamp", 0.0))
        if cached and now - timestamp < CACHE_TTL_SECONDS:
            return cached

    payload = build_sandbox_api_map()
    with _cache_lock:
        _sandbox_cache["timestamp"] = now
        _sandbox_cache["payload"] = payload
    return payload


def build_target_account_index(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    index: dict[str, dict[str, object]] = {}
    for row in rows:
        key = normalize_company_key(str(row.get("account_name", "")))
        if key and key not in index:
            index[key] = row
    return index


def build_msci_people_summary(target_bundle: dict[str, object]) -> dict[str, object]:
    retrieved_at = iso_now()
    source = make_source_entry(
        "msci_people_access",
        "MSCI people access export",
        "authenticated_private_source",
        "swfi_sandbox_api",
        retrieved_at,
        "rest_api_summary_probe",
        "high" if SWFI_SANDBOX_API_KEY else "low",
        "ok" if SWFI_SANDBOX_API_KEY else "blocked",
        evidence_url=f"{SWFI_SANDBOX_API_ROOT}/people",
        note="Summary probe across people and entity endpoints for MSCI export coverage.",
    )
    if not SWFI_SANDBOX_API_KEY:
        source["note"] = "Sandbox API key not configured."
        return {
            "status": "blocked",
            "tone": "blocked",
            "summary": {},
            "preview_rows": [],
            "source": source,
        }

    try:
        totals = {
            "people_total": int(fetch_sandbox_json("people", params={"limit": 1}).get("total_items", 0)),
            "with_email": int(fetch_sandbox_json("people", params={"limit": 1, "email": 1}).get("total_items", 0)),
            "with_phone": int(fetch_sandbox_json("people", params={"limit": 1, "phone": 1}).get("total_items", 0)),
            "with_linkedin": int(fetch_sandbox_json("people", params={"limit": 1, "linkedin": 1}).get("total_items", 0)),
        }
        preview_payload = fetch_sandbox_json("people", params={"limit": 10, "sort_field": "name", "sort_dir": "ASC"})
    except Exception as exc:
        source["status"] = "blocked"
        source["confidence"] = "low"
        source["note"] = f"Summary probe failed: {exc.__class__.__name__}"
        return {
            "status": "blocked",
            "tone": "blocked",
            "summary": {},
            "preview_rows": [],
            "source": source,
        }

    preview_rows: list[dict[str, object]] = []
    for person in preview_payload.get("data") or []:
        history = pick_person_history_row(person)
        preview_rows.append(
            {
                "name": person.get("name", ""),
                "title": history.get("title", ""),
                "email": person.get("email", ""),
                "phone": person.get("phone", ""),
                "has_entity_reference": bool(history.get("entity_id")),
            }
        )

    summary = {
        **totals,
        "preview_rows": len(preview_rows),
        "preview_with_entity_reference": sum(1 for row in preview_rows if row["has_entity_reference"]),
    }
    source["note"] = "Summary probe succeeded against the authenticated people surface."
    return {
        "status": "ok",
        "tone": "ok",
        "summary": summary,
        "preview_rows": preview_rows,
        "source": source,
    }


def get_msci_people_summary(target_bundle: dict[str, object]) -> dict[str, object]:
    now = time.time()
    with _cache_lock:
        cached = _msci_people_summary_cache.get("payload")
        timestamp = float(_msci_people_summary_cache.get("timestamp", 0.0))
        if cached and now - timestamp < CACHE_TTL_SECONDS:
            return cached

    payload = build_msci_people_summary(target_bundle)
    with _cache_lock:
        _msci_people_summary_cache["timestamp"] = now
        _msci_people_summary_cache["payload"] = payload
    return payload


def build_msci_people_export_payload(target_bundle: dict[str, object]) -> dict[str, object]:
    retrieved_at = iso_now()
    summary_bundle = get_msci_people_summary(target_bundle)
    if not SWFI_SANDBOX_API_KEY:
        return {
            "status": "blocked",
            "tone": "blocked",
            "generated_at": retrieved_at,
            "rows": [],
            "summary": {},
            "review_queue": [],
            "downloads": {
                "people_csv": "/api/msci/export/people.csv",
                "people_template_csv": "/api/msci/export/people-template.csv",
            },
            "source": summary_bundle["source"],
        }

    target_index = build_target_account_index(list(target_bundle.get("rows", [])))
    entity_cache: dict[str, dict[str, object]] = {}
    all_people: list[dict[str, object]] = []
    rows: list[dict[str, object]] = []
    review_queue: list[dict[str, object]] = []
    total_items = 0
    offset = 0
    limit = 100
    while True:
        payload = fetch_sandbox_json("people", params={"limit": limit, "offset": offset, "sort_field": "name", "sort_dir": "ASC"})
        people = payload.get("data") or []
        total_items = int(payload.get("total_items", total_items))
        if not people:
            break
        all_people.extend(person for person in people if isinstance(person, dict))
        offset += len(people)
        if offset >= total_items:
            break

    unique_entity_ids = sorted(
        {
            str(pick_person_history_row(person).get("entity_id", "")).strip()
            for person in all_people
            if str(pick_person_history_row(person).get("entity_id", "")).strip()
        }
    )
    if unique_entity_ids:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(fetch_sandbox_entity_for_export, entity_id) for entity_id in unique_entity_ids]
            for future in as_completed(futures):
                entity_id, entity = future.result()
                entity_cache[entity_id] = entity

    for person in all_people:
        history = pick_person_history_row(person)
        entity_id = str(history.get("entity_id", "")).strip()
        entity = entity_cache.get(entity_id, {})

        account_name = str(entity.get("name") or entity.get("legal_name") or "")
        institution_type = str(entity.get("type") or "")
        city = str(entity.get("city") or person.get("city") or "")
        state = str(entity.get("state") or "")
        country = str(entity.get("country") or person.get("country") or "")
        region = str(entity.get("region") or person.get("region") or "")
        title = str(history.get("title") or "")
        overlap = bool(target_index.get(normalize_company_key(account_name)))
        confidence = derive_row_confidence(
            person.get("_id"),
            entity_id,
            person.get("name"),
            person.get("email"),
            title,
            account_name,
            person.get("phone"),
        )
        person_url = f"{SWFI_SANDBOX_API_ROOT}/people/{person.get('_id', '')}"
        entity_url = f"{SWFI_SANDBOX_API_ROOT}/entities/{entity_id}" if entity_id else None
        person_provenance = make_provenance(
            "swfi_sandbox_api",
            retrieved_at,
            "rest_api_people",
            confidence,
            "sourced",
            evidence_url=person_url,
        )
        entity_provenance = make_provenance(
            "swfi_sandbox_api",
            retrieved_at,
            "rest_api_entity_join",
            confidence,
            "sourced" if entity_url else "partial",
            evidence_url=entity_url or person_url,
        )
        combined_pointer = " | ".join(pointer for pointer in (person_url, entity_url) if pointer)
        row = {
            "swfi_contact_id": str(person.get("_id", "")),
            "swfi_account_id": entity_id,
            "name": str(person.get("name") or ""),
            "email": str(person.get("email") or ""),
            "title": title,
            "account_name": account_name,
            "phone": str(person.get("phone") or ""),
            "institution_type": institution_type,
            "city": city,
            "state": state,
            "country": country,
            "region": region,
            "linkedin": str(person.get("linkedin") or ""),
            "role": str(history.get("role") or ""),
            "history_active": bool(history.get("active")),
            "target_account_overlap": "yes" if overlap else "no",
            "last_updated": str(person.get("updated_at") or ""),
            "provenance": {
                "source_system": "swfi_sandbox_api",
                "retrieval_time": retrieved_at,
                "extraction_method": "rest_api_people_plus_entity_join",
                "confidence": confidence,
                "status": "sourced" if account_name else "partial",
                "evidence_url_or_pointer": combined_pointer,
            },
            "field_provenance": {
                "swfi_contact_id": person_provenance,
                "swfi_account_id": entity_provenance,
                "name": person_provenance,
                "email": person_provenance,
                "title": person_provenance,
                "account_name": entity_provenance,
                "phone": person_provenance,
                "institution_type": entity_provenance,
                "city": entity_provenance,
                "state": entity_provenance,
                "country": entity_provenance,
                "region": entity_provenance,
                "linkedin": person_provenance,
            },
        }
        rows.append(row)
        if not entity_id or not account_name:
            review_queue.append(
                {
                    "name": row["name"],
                    "swfi_contact_id": row["swfi_contact_id"],
                    "swfi_account_id": row["swfi_account_id"],
                    "title": row["title"],
                    "reason": "missing_entity_join" if entity_id else "missing_entity_reference",
                    "evidence_pointer": combined_pointer or person_url,
                }
            )

    summary_counts = Counter(row["provenance"]["confidence"] for row in rows)
    export_summary = {
        "people_total": total_items,
        "rows_exported": len(rows),
        "resolved_accounts": sum(1 for row in rows if row["account_name"]),
        "rows_with_email": sum(1 for row in rows if row["email"]),
        "rows_with_phone": sum(1 for row in rows if row["phone"]),
        "rows_with_linkedin": sum(1 for row in rows if row["linkedin"]),
        "target_account_overlap": sum(1 for row in rows if row["target_account_overlap"] == "yes"),
        "review_queue": len(review_queue),
        "high_confidence": summary_counts.get("high", 0),
        "medium_confidence": summary_counts.get("medium", 0),
        "low_confidence": summary_counts.get("low", 0),
    }
    return {
        "status": "partial" if review_queue else "ok",
        "tone": "partial" if review_queue else "ok",
        "generated_at": retrieved_at,
        "rows": rows,
        "summary": export_summary,
        "review_queue": review_queue,
        "downloads": {
            "people_csv": "/api/msci/export/people.csv",
            "people_review_csv": "/api/msci/export/people-review.csv",
            "people_template_csv": "/api/msci/export/people-template.csv",
        },
        "source": summary_bundle["source"],
    }


def get_msci_people_export_payload(target_bundle: dict[str, object]) -> dict[str, object]:
    now = time.time()
    with _cache_lock:
        cached = _msci_people_export_cache.get("payload")
        timestamp = float(_msci_people_export_cache.get("timestamp", 0.0))
        if cached and now - timestamp < MSCI_EXPORT_TTL_SECONDS:
            return cached

    try:
        payload = build_msci_people_export_payload(target_bundle)
    except Exception as exc:
        payload = {
            "status": "blocked",
            "tone": "blocked",
            "generated_at": iso_now(),
            "rows": [],
            "summary": {},
            "review_queue": [],
            "downloads": {
                "people_csv": "/api/msci/export/people.csv",
                "people_review_csv": "/api/msci/export/people-review.csv",
                "people_template_csv": "/api/msci/export/people-template.csv",
            },
            "source": {
                "id": "msci_people_access",
                "label": "MSCI people access export",
                "classification": "authenticated_private_source",
                "source_system": "swfi_sandbox_api",
                "retrieval_time": iso_now(),
                "extraction_method": "rest_api_people_plus_entity_join",
                "confidence": "low",
                "status": "blocked",
                "evidence_url": f"{SWFI_SANDBOX_API_ROOT}/people",
                "document_pointer": None,
                "note": f"Export generation failed: {exc.__class__.__name__}",
            },
        }
    with _cache_lock:
        _msci_people_export_cache["timestamp"] = now
        _msci_people_export_cache["payload"] = payload
    return payload


def derive_tags(*parts: str) -> list[str]:
    text = normalize_text(" ".join(part for part in parts if part)).lower()
    tags: list[str] = []
    rules = [
        ("manual_ops", ("manual", "excel", "oanda")),
        (
            "missing_fields",
            (
                "missing",
                "lacks",
                "unavailable",
                "does not have",
                "currently lacks",
                "not currently available",
                "not available",
                "gap in the availability",
            ),
        ),
        ("capacity", ("additional resources", "insufficient", "bandwidth", "30 working days", "time-intensive")),
        ("automation", ("automate", "automation", "backend", "implement", "system should")),
        ("classification", ("active and passive", "active/passive", "asset allocation", "strategy field")),
        ("mapping", ("people/account", "mapping", "identifiers")),
        ("currency", ("currency", "fx", "oanda")),
        ("exports", ("csv export", "export", "output")),
        ("subsidiaries", ("subsidiar",)),
        ("alt_assets", ("alternative asset", "alternative assets", "private equity")),
        ("people", ("people data", "people-related", "people profiles", "people profile", "contacts")),
        ("high_volume", ("600000", "600,000", "4952", "906", "573", "176")),
    ]
    for tag, keywords in rules:
        if any(keyword in text for keyword in keywords):
            tags.append(tag)
    return tags


def classify_row(row: dict[str, object]) -> dict[str, str]:
    tags = list(row["tags"])
    lowered = normalize_text(
        " ".join((str(row["requirement"]), str(row["challenge"]), str(row["recommendation"])))
    ).lower()

    if "mapping" in tags:
        title = "Align Key People with Profiles"
    elif "subsidiaries" in tags:
        title = "Expand AUM coverage for subsidiaries"
    elif "currency" in tags:
        title = "Normalize AUM currency fields"
    elif "manual_ops" in tags and "allocation" in lowered:
        title = "Complete Asset Allocation fields"
    elif "alt_assets" in tags:
        title = "Extend Alternatives coverage"
    elif "people" in tags and ("gap in the availability" in lowered or "comprehensive" in lowered):
        title = "Expand Key People coverage"
    elif "missing_fields" in tags and "profile" in lowered:
        title = "Complete Profile fields"
    elif "missing_fields" in tags:
        title = "Complete Datafeeds/API fields"
    elif "capacity" in tags:
        title = "Increase Datafeeds/API refresh"
    else:
        title = shorten(str(row["requirement"] or row["challenge"]), width=72, placeholder="...")

    if "manual_ops" in tags or "missing_fields" in tags:
        state = "blocked"
    elif "automation" in tags or "capacity" in tags:
        state = "partial"
    else:
        state = "watch"

    priority = "P1" if str(row["client"]) in ("MSCI", "Bloomberg") else "P2"
    if "high_volume" in tags or "mapping" in tags:
        priority = "P1"

    return {"title": title, "state": state, "priority": priority}


CONCERN_BRIEFS = {
    "Complete Asset Allocation fields": {
        "requirement": "Complete Asset Allocation fields used in MSCI and client delivery.",
        "challenge": "Move allocation percentages, managed assets, and classification fields into repeatable export-ready records.",
        "recommendation": "This improves Asset Allocation tables, AUM views, and Datafeeds/API delivery.",
    },
    "Expand AUM coverage for subsidiaries": {
        "requirement": "Expand AUM and managed-assets coverage across subsidiaries and child funds.",
        "challenge": "Add the profile fields and joins required to connect parent entities, subsidiaries, and related funds.",
        "recommendation": "This improves profile completeness and makes AUM exports more reliable.",
    },
    "Increase Datafeeds/API refresh": {
        "requirement": "Increase refresh capacity for the largest institutional datafeeds.",
        "challenge": "Improve update throughput across ingestion, review, and publishing for high-volume profiles and transactions.",
        "recommendation": "This keeps recurring deliveries on schedule and reduces stale records.",
    },
    "Complete Profile fields": {
        "requirement": "Complete the core profile fields used across subscriptions, exports, and direct integrations.",
        "challenge": "Backfill institution identity, location, and reference fields where profiles are still thin.",
        "recommendation": "This improves trust in profiles and raises the completeness of feeds and exports.",
    },
    "Complete Datafeeds/API fields": {
        "requirement": "Complete the fields needed by downstream Datafeeds/API consumers.",
        "challenge": "Close the remaining gaps between tracked internal fields and the records surfaced directly in exports.",
        "recommendation": "This reduces one-off handling and makes delivery easier to automate.",
    },
    "Align Key People with Profiles": {
        "requirement": "Align Key People, contacts, and institution profiles with stable account references.",
        "challenge": "Use consistent identifiers and joins so people-to-profile mapping stays stable across exports and APIs.",
        "recommendation": "This is the foundation for trustworthy MSCI Key People files and review workflows.",
    },
    "Normalize AUM currency fields": {
        "requirement": "Normalize currency handling across AUM, managed assets, and account-level outputs.",
        "challenge": "Apply shared FX conversion and currency metadata rules across feeds and exports.",
        "recommendation": "This keeps profile and AUM outputs consistent for downstream consumers.",
    },
    "Extend Alternatives coverage": {
        "requirement": "Extend Alternatives and Real Assets coverage for institutions where that data is still thin.",
        "challenge": "Add the fields and profile types required to surface alternatives directly in the product.",
        "recommendation": "This closes a visible coverage gap and reduces manual side handling.",
    },
    "Expand Key People coverage": {
        "requirement": "Improve the depth and consistency of Key People records used in delivery work.",
        "challenge": "Enrich contact coverage, refresh cadence, and supporting joins so people records are usable downstream.",
        "recommendation": "This raises confidence in contact-level outputs and reduces manual follow-up.",
    },
}


def sanitize_concern_copy(row: dict[str, object]) -> dict[str, str]:
    title = str(row.get("title") or "")
    mapped = CONCERN_BRIEFS.get(title)
    if mapped:
        return mapped
    client = str(row.get("client") or "delivery")
    return {
        "requirement": f"{title} sits inside the {client} lane and still needs fuller coverage before it can be treated as routine.",
        "challenge": "Focus areas span profiles, key people, asset allocation, and delivery controls.",
        "recommendation": "This affects export completeness, Datafeeds/API reliability, and operator confidence across the lane.",
    }


def normalize_use_case(value: str) -> str:
    text = (value or "").strip()
    lowered = text.lower()
    if not text:
        return "Datafeeds/API"
    if "api" in lowered:
        return "Datafeeds/API"
    if "rfp" in lowered or "mandate" in lowered:
        return "RFPs and Opportunities"
    if "people" in lowered or "contact" in lowered:
        return "Key People"
    if "allocation" in lowered or "aum" in lowered:
        return "Asset Allocation"
    if "deal" in lowered or "transaction" in lowered:
        return "Transactions"
    if "profile" in lowered:
        return "Profiles"
    return text


def load_concern_rows() -> dict[str, object]:
    retrieved_at = iso_now()
    source = make_source_entry(
        "concern_sheet",
        "Client concern sheet",
        "public_api_available_now",
        "google_sheets_export",
        retrieved_at,
        "csv_export_parse",
        "high",
        "ok",
        evidence_url=PROPOSAL_SHEET_URL,
    )
    rows: list[dict[str, object]] = []

    try:
        csv_text = fetch_text(SHEET_CSV_URL)
        reader = csv.DictReader(io.StringIO(csv_text))
        client = ""
        use_case = ""
        for raw in reader:
            client = (raw.get("Client Name") or client or "").strip()
            use_case = (raw.get("Use Case") or use_case or "").strip()
            requirement = normalize_text(raw.get("Data Requirement") or "")
            challenge = normalize_text(raw.get("Challenges") or "")
            recommendation = normalize_text(raw.get("Recommendations") or "")
            if not any((client, requirement, challenge, recommendation)):
                continue

            tags = derive_tags(requirement, challenge, recommendation)
            row: dict[str, object] = {
                "client": client or "General",
                "use_case": normalize_use_case(use_case or "Datafeeds/API"),
                "requirement": requirement,
                "challenge": challenge,
                "recommendation": recommendation,
                "tags": tags,
                "provenance": make_provenance(
                    "google_sheets_export",
                    retrieved_at,
                    "csv_export_parse",
                    "high",
                    "sourced",
                    evidence_url=PROPOSAL_SHEET_URL,
                ),
            }
            row.update(classify_row(row))
            row.update(sanitize_concern_copy(row))
            rows.append(row)
    except Exception as exc:
        source["status"] = "fallback"
        source["confidence"] = "low"
        source["note"] = f"Concern sheet fetch failed: {exc.__class__.__name__}"

    # Dedupe: classify_row() can collapse distinct sheet rows to the same title
    # (e.g. several "missing_fields" rows for MSCI both resolve to
    # "Add missing dashboard fields"). Key on (client, title, requirement) and
    # keep the first occurrence so the dashboard feed does not expose duplicates.
    seen_concern_keys: set[tuple[str, str, str]] = set()
    deduped_rows: list[dict[str, object]] = []
    for row in rows:
        key = (
            str(row.get("client") or ""),
            str(row.get("title") or ""),
            str(row.get("requirement") or ""),
        )
        if key in seen_concern_keys:
            continue
        seen_concern_keys.add(key)
        deduped_rows.append(row)
    rows = deduped_rows

    return {"rows": rows, "source": source}


def parse_aum_docs() -> dict[str, object]:
    retrieved_at = iso_now()
    source = make_source_entry(
        "swfi_aum_docs",
        "SWFI AUM docs",
        "public_api_available_now",
        "swfi_public_api",
        retrieved_at,
        "html_parse",
        "high",
        "ok",
        evidence_url=AUM_DOCS_URL,
    )
    docs = {
        "title": "AUM collection",
        "path": "GET /v1/aum",
        "summary": "Historical assets under management for entities with filters for time, ranges, entity ids, and sort controls.",
        "query_parameters": [],
        "example_fields": [],
        "collections": [],
        "provenance": make_provenance(
            "swfi_public_api",
            retrieved_at,
            "html_parse",
            "high",
            "sourced",
            evidence_url=AUM_DOCS_URL,
        ),
    }

    try:
        aum_html = fetch_text(AUM_DOCS_URL)
        collections_html = fetch_text(COLLECTIONS_URL)
        section = aum_html.split("Success Response", 1)[0]
        pattern = re.compile(
            r'bg-light rounded(?: text-break)?">([^<]+)</div><div class="font-monospace(?: ms-1)?">'
            r'<span class="text-muted me-1">TYPE</span><span>([^<]+)</span></div></div><div>(.*?)</div>',
            re.S,
        )

        seen_params: set[str] = set()
        for name, dtype, description in pattern.findall(section):
            clean_name = normalize_text(html.unescape(name))
            if clean_name in seen_params:
                continue
            seen_params.add(clean_name)
            docs["query_parameters"].append(
                {
                    "name": clean_name,
                    "type": normalize_text(html.unescape(dtype)),
                    "description": strip_tags(html.unescape(description)),
                    "provenance": make_provenance(
                        "swfi_public_api",
                        retrieved_at,
                        "html_parse",
                        "high",
                        "sourced",
                        evidence_url=AUM_DOCS_URL,
                    ),
                }
            )

        example_match = re.search(r"Example response</div><pre[^>]*>(.*?)</pre>", aum_html, re.S)
        seen_fields: set[str] = set()
        if example_match:
            pre_block = example_match.group(1)
            for field in re.findall(r"&quot;([^&]+?)&quot;\s*:", pre_block):
                if field in seen_fields:
                    continue
                seen_fields.add(field)
                docs["example_fields"].append(
                    {
                        "name": field,
                        "provenance": make_provenance(
                            "swfi_public_api",
                            retrieved_at,
                            "html_parse",
                            "high",
                            "sourced",
                            evidence_url=AUM_DOCS_URL,
                        ),
                    }
                )

        seen_slugs: set[str] = set()
        for slug, label in re.findall(r'href="/collections/([^"]+)">([^<]+)</a>', collections_html):
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            docs["collections"].append(
                {
                    "slug": slug,
                    "label": normalize_text(html.unescape(label)),
                    "provenance": make_provenance(
                        "swfi_public_api",
                        retrieved_at,
                        "html_parse",
                        "high",
                        "sourced",
                        evidence_url=COLLECTIONS_URL,
                    ),
                }
            )
    except Exception as exc:
        source["status"] = "fallback"
        source["confidence"] = "low"
        source["note"] = f"AUM docs fetch failed: {exc.__class__.__name__}"
        docs["summary"] = "Public AUM docs were not available during this fetch."

    return {"docs": docs, "source": source}


def column_index(cell_ref: str) -> int:
    letters = "".join(char for char in cell_ref if char.isalpha()).upper()
    index = 0
    for char in letters:
        index = index * 26 + (ord(char) - 64)
    return max(index - 1, 0)


def sheet_rows_from_xlsx(path: Path, desired_sheet: str | None = None) -> list[list[str]]:
    with ZipFile(path) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in shared_root.findall("a:si", XLSX_NS):
                shared_strings.append("".join(text.text or "" for text in item.findall(".//a:t", XLSX_NS)))

        sheet_path = "xl/worksheets/sheet1.xml"
        if desired_sheet:
            workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
            rels_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
            rel_map = {
                rel.get("Id", ""): f"xl/{rel.get('Target', '').lstrip('/')}"
                for rel in rels_root.findall("pr:Relationship", XLSX_NS)
            }
            for sheet in workbook_root.findall("a:sheets/a:sheet", XLSX_NS):
                if normalize_text(sheet.get("name", "")).lower() == desired_sheet.lower():
                    relation_id = sheet.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", "")
                    sheet_path = rel_map.get(relation_id, sheet_path)
                    break

        sheet_root = ET.fromstring(archive.read(sheet_path))
        rows: list[list[str]] = []
        for row_elem in sheet_root.findall(".//a:row", XLSX_NS):
            values: list[str] = []
            for cell in row_elem.findall("a:c", XLSX_NS):
                index = column_index(cell.get("r", "A1"))
                while len(values) <= index:
                    values.append("")
                cell_type = cell.get("t")
                cell_value = ""
                if cell_type == "s":
                    value_elem = cell.find("a:v", XLSX_NS)
                    if value_elem is not None and value_elem.text is not None:
                        cell_value = shared_strings[int(value_elem.text)]
                elif cell_type == "inlineStr":
                    cell_value = "".join(text.text or "" for text in cell.findall(".//a:t", XLSX_NS))
                else:
                    value_elem = cell.find("a:v", XLSX_NS)
                    if value_elem is not None and value_elem.text is not None:
                        cell_value = value_elem.text
                values[index] = normalize_text(cell_value)
            while values and not values[-1]:
                values.pop()
            rows.append(values)
        return rows


def derive_mapping_focus(account_type: str) -> str:
    lowered = account_type.lower()
    if "asset manager" in lowered:
        return "allocator coverage + decision-maker mapping"
    if "bank" in lowered or "holding" in lowered:
        return "parent / subsidiary normalization"
    if "insurance" in lowered:
        return "balance-sheet owner + portfolio mapping"
    return "entity profile + people enrichment"


def derive_priority_tier(assets_managed: float, api_potential: float) -> str:
    if api_potential >= 80_000 or assets_managed >= 1_000_000_000_000:
        return "Tier 1"
    if assets_managed >= 300_000_000_000:
        return "Tier 2"
    return "Tier 3"


def load_target_accounts() -> dict[str, object]:
    retrieved_at = iso_now()
    source = make_source_entry(
        "msci_target_accounts",
        "MSCI target account workbook",
        "document_extraction_required",
        "local_xlsx",
        retrieved_at,
        "xlsx_xml_parse",
        "high",
        "ok",
        document_pointer=local_pointer(TARGET_LIST_XLSX),
    )

    if not TARGET_LIST_XLSX.exists():
        source["status"] = "fallback"
        source["confidence"] = "low"
        source["note"] = "Workbook not found"
        return {"rows": [], "summary": {}, "source": source}

    try:
        rows = sheet_rows_from_xlsx(TARGET_LIST_XLSX)
    except Exception as exc:
        source["status"] = "fallback"
        source["confidence"] = "low"
        source["note"] = f"Workbook parse failed: {exc.__class__.__name__}"
        return {"rows": [], "summary": {}, "source": source}

    header_index = 0
    for index, row in enumerate(rows):
        lowered = [cell.lower() for cell in row]
        if lowered[:4] == ["name", "type", "city", "state"]:
            header_index = index
            break

    headers = rows[header_index]
    revenue_row = rows[0] if rows else []
    records: list[dict[str, object]] = []
    for raw in rows[header_index + 1 :]:
        if not raw or not raw[0]:
            continue
        item = {headers[index]: raw[index] if index < len(raw) else "" for index in range(len(headers))}
        assets = to_number(item.get("assets"))
        assets_managed = to_number(item.get("assetsManaged"))
        api_potential = to_number(item.get("API Potential"))
        team_subscription = to_number(item.get("Team Subscription"))
        single_subscription = to_number(item.get("Single Subscription"))
        income_potential = to_number(item.get("Income Potential"))
        priority_tier = derive_priority_tier(assets_managed, api_potential)
        mapping_focus = derive_mapping_focus(str(item.get("type", "")))
        provenance = make_provenance(
            "local_xlsx",
            retrieved_at,
            "xlsx_xml_parse",
            "high",
            "sourced",
            document_pointer=local_pointer(TARGET_LIST_XLSX),
        )
        records.append(
            {
                "account_name": item.get("name", ""),
                "account_type": item.get("type", ""),
                "city": item.get("city", ""),
                "state": item.get("state", ""),
                "assets": assets,
                "assets_managed": assets_managed,
                "api_potential": api_potential,
                "team_subscription": team_subscription,
                "single_subscription": single_subscription,
                "income_potential": income_potential,
                "priority_tier": priority_tier,
                "mapping_focus": mapping_focus,
                "field_provenance": {
                    "account_name": provenance,
                    "account_type": provenance,
                    "city": provenance,
                    "state": provenance,
                    "assets": provenance,
                    "assets_managed": provenance,
                    "api_potential": provenance,
                    "priority_tier": provenance,
                    "mapping_focus": provenance,
                },
                "provenance": provenance,
            }
        )

    total_api_potential = sum(float(row["api_potential"]) for row in records)
    total_assets_managed = sum(float(row["assets_managed"]) for row in records)
    type_breakdown = Counter(str(row["account_type"]) for row in records)
    state_breakdown = Counter(str(row["state"]) for row in records if row["state"])
    top_targets = sorted(records, key=lambda item: float(item["assets_managed"]), reverse=True)[:8]

    summary = {
        "total_targets": len(records),
        "total_api_potential": total_api_potential,
        "total_assets_managed": total_assets_managed,
        "revenue_cap": to_number(revenue_row[1]) if len(revenue_row) > 1 else 0.0,
        "top_targets": top_targets,
        "type_breakdown": [{"name": name, "count": count} for name, count in type_breakdown.most_common(6)],
        "state_breakdown": [{"name": name, "count": count} for name, count in state_breakdown.most_common(6)],
    }
    return {"rows": records, "summary": summary, "source": source}


def load_swf_seeds() -> dict[str, object]:
    retrieved_at = iso_now()
    source = make_source_entry(
        "swf_global_seed",
        "SWFs Global seed CSV",
        "document_extraction_required",
        "local_csv",
        retrieved_at,
        "csv_parse",
        "high",
        "ok",
        document_pointer=local_pointer(SWF_GLOBAL_CSV),
    )
    if not SWF_GLOBAL_CSV.exists():
        source["status"] = "fallback"
        source["confidence"] = "low"
        source["note"] = "CSV not found"
        return {"rows": [], "summary": {}, "source": source}

    rows: list[dict[str, str]] = []
    try:
        with SWF_GLOBAL_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for raw in reader:
                rows.append(
                    {
                        "name": raw.get("name", ""),
                        "type": raw.get("type", ""),
                        "region": raw.get("region", ""),
                        "country": raw.get("country", ""),
                        "website": raw.get("website", ""),
                        "verified": raw.get("Verified (Yes/No)", ""),
                        "summary": strip_tags(raw.get("summary", "")),
                        "provenance": make_provenance(
                            "local_csv",
                            retrieved_at,
                            "csv_parse",
                            "high",
                            "sourced",
                            document_pointer=local_pointer(SWF_GLOBAL_CSV),
                        ),
                    }
                )
    except Exception as exc:
        source["status"] = "fallback"
        source["confidence"] = "low"
        source["note"] = f"CSV parse failed: {exc.__class__.__name__}"
        return {"rows": [], "summary": {}, "source": source}

    regions = Counter(row["region"] for row in rows if row["region"])
    verified = sum(1 for row in rows if row["verified"].lower() == "yes")
    summary = {
        "total": len(rows),
        "verified": verified,
        "regions": [{"name": name, "count": count} for name, count in regions.most_common(6)],
        "sample": rows[:5],
    }
    return {"rows": rows, "summary": summary, "source": source}


def load_platform_improvements() -> dict[str, object]:
    retrieved_at = iso_now()
    source = make_source_entry(
        "platform_improvements",
        "Platform improvements roadmap",
        "document_extraction_required",
        "local_csv",
        retrieved_at,
        "csv_parse",
        "high",
        "ok",
        document_pointer=local_pointer(PLATFORM_IMPROVEMENTS_CSV),
    )
    if not PLATFORM_IMPROVEMENTS_CSV.exists():
        source["status"] = "fallback"
        source["confidence"] = "low"
        source["note"] = "CSV not found"
        return {"roadmap": {}, "source": source}

    rows: list[list[str]] = []
    try:
        with PLATFORM_IMPROVEMENTS_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
    except Exception as exc:
        source["status"] = "fallback"
        source["confidence"] = "low"
        source["note"] = f"CSV parse failed: {exc.__class__.__name__}"
        return {"roadmap": {}, "source": source}

    summary = [
        "Immediate focus on data quality and platform usability",
        "Short-term search improvements and coverage expansion",
        "Mid-term analytics and intelligence capabilities",
        "Long-term platform and data-architecture modernization",
    ]
    timeline_headers: list[str] = []
    timeline_values: list[list[str]] = []
    initiatives: dict[str, list[str]] = defaultdict(list)
    kpis: list[str] = []

    for index, row in enumerate(rows):
        cleaned = [normalize_text(cell) for cell in row]
        if any(cell in ("0–3 Months", "0-3 Months") for cell in cleaned):
            timeline_headers = [cell for cell in cleaned if cell]
            if index + 1 < len(rows):
                timeline_values = [
                    [normalize_text(item) for item in cell.splitlines() if normalize_text(item)]
                    for cell in rows[index + 1][: len(timeline_headers)]
                ]
        if any("High Impact | High Priority" in cell for cell in cleaned):
            headers = [cell for cell in cleaned if cell]
            cursor = index + 1
            while cursor < len(rows):
                candidate = [normalize_text(cell) for cell in rows[cursor]]
                if not any(candidate):
                    break
                if any("Product Success Metrics" in cell for cell in candidate):
                    break
                for header, value in zip(headers, candidate):
                    if value:
                        initiatives[header].append(value)
                cursor += 1
        if any("Product Success Metrics" in cell for cell in cleaned):
            cursor = index + 1
            while cursor < len(rows):
                candidate = [normalize_text(cell) for cell in rows[cursor] if normalize_text(cell)]
                if candidate:
                    kpis.extend(candidate)
                cursor += 1

    roadmap = {
        "summary": summary,
        "timeline": [
            {"window": header, "items": timeline_values[pos] if pos < len(timeline_values) else []}
            for pos, header in enumerate(timeline_headers)
        ],
        "initiatives": [{"bucket": bucket, "items": values} for bucket, values in initiatives.items()],
        "kpis": kpis,
    }
    return {"roadmap": roadmap, "source": source}


def build_lane_summaries(concerns: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in concerns:
        grouped[str(row["client"])].append(row)

    lanes: list[dict[str, object]] = []
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
            "source_note": "Proposal includes IFC, but no live concern rows define the lane.",
        }
    )
    return lanes


def build_action_queue(concerns: list[dict[str, object]]) -> list[dict[str, object]]:
    actions: list[dict[str, object]] = []
    seen_titles: set[str] = set()

    curated = [
        {
            "title": "Improve top 500 Profiles",
            "lane": "All",
            "status": "blocked",
            "priority": "P1",
            "impact": "Profiles, Key People, AUM, and Transactions remain the highest-leverage trust fix.",
        },
        {
            "title": "Add source and timestamp detail",
            "lane": "All",
            "status": "partial",
            "priority": "P1",
            "impact": "Every important field should show source, retrieval time, method, confidence, and evidence.",
        },
        {
            "title": "MSCI Key People export",
            "lane": "MSCI",
            "status": "partial",
            "priority": "P1",
            "impact": "The export path exists; the next step is stronger contact verification, authorization, and audit history.",
        },
        {
            "title": "Platform speed and search",
            "lane": "All",
            "status": "blocked",
            "priority": "P1",
            "impact": "Speed and search quality are recurring blockers in live demos and client evaluation.",
        },
        {
            "title": "Search and alerts",
            "lane": "All",
            "status": "blocked",
            "priority": "P1",
            "impact": "Clients expect natural-language search, saved searches, and alerts across profiles and transactions.",
        },
        {
            "title": "CRM and Datafeeds/API delivery",
            "lane": "All",
            "status": "blocked",
            "priority": "P1",
            "impact": "CSV alone is not enough; enterprise clients expect CRM delivery, warehouse sync, and scheduled exports.",
        },
        {
            "title": "Access controls and monitoring",
            "lane": "All",
            "status": "blocked",
            "priority": "P1",
            "impact": "Enterprise delivery expects controlled access, usage monitoring, and consistent fields across every delivery channel.",
        },
    ]

    for item in curated:
        actions.append(item)
        seen_titles.add(item["title"])

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

    return actions[:8]


def build_readiness(
    concerns: list[dict[str, object]],
    aum_docs: dict[str, object],
    atlas_status: dict[str, object],
    people_summary: dict[str, object],
) -> list[dict[str, str]]:
    tag_counter = Counter(tag for row in concerns for tag in row["tags"])
    people_counts = people_summary.get("summary", {})
    return [
        {
            "title": "Canonical schema",
            "status": "partial",
            "note": "The normalized object model is now explicit, but live population still depends on more than public AUM docs.",
        },
        {
            "title": "Provenance envelope",
            "status": "partial",
            "note": "The preview build is provenance-aware; the production build still needs evidence pointers on authenticated fields.",
        },
        {
            "title": "People export completeness",
            "status": str(people_summary.get("tone", "blocked")),
            "note": (
                f"Authenticated people access now exposes {people_counts.get('people_total', 0)} accessible records, "
                f"with {people_counts.get('with_email', 0)} emails and {people_counts.get('with_phone', 0)} phones available for export."
            )
            if people_summary.get("status") == "ok"
            else "MSCI requested Contact ID, Account ID, Email, Title, Account Name, and Phone; the export path is blocked until authenticated people access is configured.",
        },
        {
            "title": "Export automation",
            "status": "blocked" if tag_counter.get("manual_ops") else "partial",
            "note": f"{tag_counter.get('manual_ops', 0)} tracked concern(s) still reference manual calculations or external tools.",
        },
        {
            "title": "AUM schema exposure",
            "status": "partial",
            "note": f"Public docs expose {len(aum_docs['query_parameters'])} query parameters and {len(aum_docs['example_fields'])} example fields.",
        },
        {
            "title": "Atlas preview persistence",
            "status": str(atlas_status.get("tone", "watch")),
            "note": str(atlas_status.get("note", "Atlas not configured for preview materialization.")),
        },
    ]


def build_metric_cards(
    concerns: list[dict[str, object]],
    target_summary: dict[str, object],
    confidence_summary: dict[str, object],
    people_summary: dict[str, object],
) -> list[dict[str, str]]:
    people_counts = people_summary.get("summary", {})
    return [
        {"label": "Coverage models", "value": str(len(CANONICAL_SCHEMA)), "note": "Institution, fund, AUM, people, document, RFP, filing, news"},
        {"label": "Coverage items", "value": str(len(concerns)), "note": "Current items surfaced from the live delivery sheet"},
        {
            "label": "Target accounts",
            "value": str(target_summary.get("total_targets", 0)),
            "note": "MSCI account workbook rows normalized into the workbench",
        },
        {
            "label": "Accessible key people",
            "value": str(people_counts.get("people_total", 0) or "0"),
            "note": "Authenticated Key People list available for MSCI export",
        },
    ]


def build_maturity_groups() -> list[dict[str, object]]:
    return [
        {
            "bucket": "public_api_available_now",
            "title": "Public API available now",
            "items": [
                {"name": "SWFI public collections / AUM docs", "status": "ok", "note": "Public collection docs and AUM filters are available today."},
                {"name": "GLEIF and Companies House", "status": "ok", "note": "Suitable for legal-entity normalization and registry backfill."},
                {"name": "SEC and OFAC", "status": "ok", "note": "Useful for filings, sanctions, and compliance-event enrichment."},
            ],
        },
        {
            "bucket": "authenticated_private_source",
            "title": "Authenticated / private source",
            "items": [
                {"name": "SWFI sandbox people / entities", "status": "ok" if SWFI_SANDBOX_API_KEY else "blocked", "note": "Authenticated sandbox source now supports MSCI people-access export validation and entity joins." if SWFI_SANDBOX_API_KEY else "Configure the sandbox or equivalent authenticated source to enable the people export."},
                {"name": "SWFI private people / entities / transactions / compass", "status": "watch", "note": "Still needed for full production entitlements and parity beyond sandbox-access scope."},
                {"name": "Mandrill alert delivery", "status": "watch", "note": "Existing private automation stream; observability still needs to be exposed."},
                {"name": "SendGrid newsletter delivery", "status": "watch", "note": "Existing private automation stream for the public list."},
                {"name": "MongoDB Atlas preview storage", "status": "watch", "note": "Driver-based materialization target for canonical packets and job state."},
            ],
        },
        {
            "bucket": "document_extraction_required",
            "title": "Document extraction required",
            "items": [
                {"name": "Target account workbook", "status": "partial", "note": "Now parsed into the MSCI workbench via XLSX XML extraction."},
                {"name": "Board minutes / agendas / PDF filings", "status": "blocked", "note": "Critical for scattered asset-allocation facts and unstructured disclosures."},
                {"name": "Platform improvements roadmap and local briefing docs", "status": "partial", "note": "Roadmap items are now surfaced, but not yet tied to execution telemetry."},
            ],
        },
        {
            "bucket": "manual_enrichment_only",
            "title": "Manual enrichment only",
            "items": [
                {"name": "LinkedIn / guessed email / Apollo workflows", "status": "blocked", "note": "Useful but risky without freshness and verification controls."},
                {"name": "Clay / outreach / Sales Navigator playbooks", "status": "blocked", "note": "Sales efficiency asks exist, but are not yet integrated into the product."},
                {"name": "Case studies and social proof", "status": "watch", "note": "Not an API, but a major sales objection surfaced in feedback."},
            ],
        },
        {
            "bucket": "benchmark_only_not_integration_target",
            "title": "Benchmark only, not integration target",
            "items": [
                {"name": "Preqin", "status": "watch", "note": "Direct product benchmark on coverage, feeds, and workflow depth."},
                {"name": "PitchBook", "status": "watch", "note": "Direct data, CRM plugins, Excel/PowerPoint/Chrome integrations, and AI partnership benchmark."},
                {"name": "Bloomberg", "status": "watch", "note": "Enterprise data, entitlements, unified delivery, and AI-assisted research benchmark."},
                {"name": "BlackRock Aladdin", "status": "watch", "note": "API-first enterprise benchmark for governed platform depth."},
                {"name": "KKR", "status": "watch", "note": "Institutional credibility benchmark rather than a target integration."},
            ],
        },
    ]


def build_data_coverage(people_summary: dict[str, object]) -> list[dict[str, object]]:
    people_counts = people_summary.get("summary", {})
    return [
        {
            "lane": "MSCI",
            "available_today_api": [
                "Public AUM docs and masked collections map",
                "Account-target workbook ingestion and normalized account export",
                "Sandbox-backed people export with entity joins",
                f"Accessible people list summary: {people_counts.get('people_total', 0)} records",
            ],
            "public_docs_extraction": [
                "Target account workbook",
                "Proposal-defined MSCI mapping scope",
                "Platform improvements roadmap and feedback packet",
            ],
            "third_party_connectors": [
                "GLEIF / Companies House for identity resolution",
                "Salesforce / Snowflake / Graph for downstream delivery",
            ],
            "unavailable_without_private_access": [
                "Production-grade entitlements beyond sandbox scope",
                "Email and phone verification workflow",
                "Private-source parity across every profile and account lane",
            ],
        },
        {
            "lane": "Bloomberg",
            "available_today_api": [
                "AUM field surface and current blocker sheet",
                "Transactions / Compass domain framing",
            ],
            "public_docs_extraction": [
                "Roadmap items for search, filters, and data coverage",
                "Local notes around active/passive and real-assets ambiguity",
            ],
            "third_party_connectors": [
                "Registry / filing connectors for entity normalization",
                "Warehouse and CRM delivery connectors",
            ],
            "unavailable_without_private_access": [
                "Full managed-assets splits and validated classifications",
                "Latest RFP and Compass completeness",
                "Internal search / filter telemetry and true production performance signals",
            ],
        },
        {
            "lane": "IFC",
            "available_today_api": [
                "Proposal scope only",
            ],
            "public_docs_extraction": [
                "Roadmap and product-gap framing",
            ],
            "third_party_connectors": [
                "Reusable delivery connectors from other lanes once the workflow pack exists",
            ],
            "unavailable_without_private_access": [
                "Detailed IFC workflow definition",
                "Entitlement rules and output schema",
                "Live authenticated data source wiring",
            ],
        },
    ]


def build_gap_list(atlas_status: dict[str, object], people_summary: dict[str, object]) -> list[dict[str, str]]:
    people_counts = people_summary.get("summary", {})
    return [
        {
            "title": "MSCI export still needs quality controls",
            "severity": "partial" if people_summary.get("status") == "ok" else "blocked",
            "detail": (
                f"The authenticated export path is now populated, but only {people_counts.get('with_phone', 0)} phone values and {people_counts.get('with_email', 0)} email values are currently present in the accessible people surface."
            )
            if people_summary.get("status") == "ok"
            else "The contract exists, but the populated people export path is blocked until authenticated sandbox or production credentials are configured.",
        },
        {
            "title": "Contact quality remains a trust blocker",
            "severity": "blocked",
            "detail": "Feedback explicitly calls out sparse and inaccurate contact data, especially email and role accuracy.",
        },
        {
            "title": "Per-customer export authorization is still missing",
            "severity": "partial",
            "detail": "Private export routes are now guarded and durably logged, but production still needs customer identity binding, reviewer-visible history, and session-aware entitlements.",
        },
        {
            "title": "Production performance has not been cleared",
            "severity": "partial",
            "detail": "The architecture is now production-shaped, but rollout should still stay controlled until live performance and auth posture are cleared.",
        },
        {
            "title": "AI search and smart alerts are still missing",
            "severity": "blocked",
            "detail": "Natural-language query and explainable alerting are now baseline buyer expectations.",
        },
        {
            "title": "Entitlements and unified data delivery are not yet built",
            "severity": "blocked",
            "detail": "Current enterprise leaders expose permission-aware APIs, monitoring, and a unified data model across delivery channels.",
        },
        {
            "title": "Atlas preview materialization is not ready",
            "severity": str(atlas_status.get("tone", "watch")),
            "detail": str(atlas_status.get("note", "Atlas preview storage is not configured.")),
        },
    ]


def build_security_controls() -> list[dict[str, str]]:
    return [
        {
            "title": "Response hardening",
            "status": "ok",
            "note": "HTML now ships with CSP nonce enforcement, frame blocking, MIME sniff protection, strict referrer handling, permission lockdown, and same-origin isolation headers.",
            "source": "OWASP headers",
            "url": "https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html",
        },
        {
            "title": "Controlled exports + durable audit log",
            "status": "partial",
            "note": f"Private CSV exports are session, token, or local gated, rate limited, and appended to a durable audit log at {SWFI_EXPORT_AUDIT_LOG}. Customer identity binding is the remaining gap.",
            "source": "SWFI runtime",
            "url": None,
        },
        {
            "title": "Preview crawl isolation",
            "status": "ok",
            "note": "Preview hosts remain noindex/disallow, while the canonical host exposes sitemap, robots, llms guidance, and structured data for discovery.",
            "source": "OpenAI crawler docs",
            "url": "https://platform.openai.com/docs/bots",
        },
        {
            "title": "Vulnerability disclosure surface",
            "status": "ok" if SWFI_SECURITY_CONTACT_CONFIGURED else "partial",
            "note": "security.txt is now published on the well-known path. Set SWFI_SECURITY_CONTACT_URI to the monitored disclosure inbox if it differs from the default security@swfi.com path.",
            "source": "RFC 9116",
            "url": "https://www.rfc-editor.org/rfc/rfc9116",
        },
        {
            "title": "Read-only research lane",
            "status": "ok",
            "note": "The chat surface remains read-only, bounded to the current packet, and rate limited to reduce leakage and model-spend abuse.",
            "source": "SWFI runtime",
            "url": None,
        },
        {
            "title": "Email sender posture",
            "status": "partial",
            "note": "Mandrill and SendGrid streams are modeled, but production still depends on SPF, DKIM, DMARC, suppression handling, and mailbox health operations.",
            "source": "FTC email authentication",
            "url": "https://www.ftc.gov/business-guidance/small-businesses/cybersecurity/email-authentication",
        },
    ]


def build_legal_risk_register() -> list[dict[str, str]]:
    return [
        {
            "title": "Commercial email compliance",
            "status": "partial",
            "note": "B2B email still falls under CAN-SPAM. Automated sends need sender identity, postal address, unsubscribe handling, and suppression honoring within the required window.",
            "action": "Keep Mandrill and SendGrid sends tied to list hygiene, suppression syncing, and template review.",
            "source": "FTC CAN-SPAM",
            "url": "https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business",
        },
        {
            "title": "Business-contact personal data",
            "status": "partial",
            "note": "People, email, phone, and role data require documented lawful-basis handling, retention rules, and region-aware use constraints before broader outreach automation.",
            "action": "Treat exported people/contact data as controlled-access data with retention, access, and suppression policy.",
            "source": "ICO legitimate interests",
            "url": "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/legitimate-interests/when-can-we-rely-on-legitimate-interests/",
        },
        {
            "title": "LinkedIn and manual enrichment sources",
            "status": "blocked",
            "note": "LinkedIn scraping is a legal and terms risk. Keep LinkedIn, guessed-email, and Apollo-style enrichment off the automated production path unless policy and counsel explicitly clear the workflow.",
            "action": "Use company websites, filings, registries, exchanges, and approved connectors as the automated source base.",
            "source": "LinkedIn crawling terms",
            "url": "https://www.linkedin.com/legal/crawling-terms",
        },
        {
            "title": "Client entitlement and export misuse",
            "status": "partial",
            "note": "The MSCI problem is not just fields. Production must prove who had access to which export, when, and under which client entitlement.",
            "action": "Bind exports to authenticated users or service principals and keep durable audit history.",
            "source": "SWFI runtime",
            "url": None,
        },
        {
            "title": "AI crawler and preview-host leakage",
            "status": "ok",
            "note": "The public host is discoverable, but preview hosts remain blocked. llms.txt is treated as supplemental only; robots and noindex remain authoritative controls.",
            "action": "Keep public discovery limited to swfi.com and never expose private export routes on crawlable preview hosts.",
            "source": "Google AI Search guidance",
            "url": "https://developers.google.com/search/blog/2025/05/succeeding-in-ai-search",
        },
    ]


def build_msci_people_export(people_summary: dict[str, object]) -> dict[str, object]:
    counts = people_summary.get("summary", {})
    status = people_summary.get("status", "blocked")
    return {
        "answer": (
            f"Yes. The authenticated people-export path is live and currently summarizes {counts.get('people_total', 0)} accessible records. "
            "Use the export for delivery; contact-quality review is a separate step."
            if status == "ok"
            else "The export contract is defined, but delivery is blocked until authenticated SWFI sandbox or production credentials are configured."
        ),
        "requested_fields": MSCI_REQUESTED_FIELDS,
        "export_ready_now": [
            "Authenticated people export with SWFI Contact ID and Account ID",
            "Entity-joined account names and institution metadata",
            "Relevant metadata fields such as city, state, country, region, provenance, and target-account overlap",
            "CSV template and protected populated CSV export routes",
            "Durable export audit logging",
        ],
        "blocked_until_private_access": [
            "Production entitlements beyond the sandbox scope",
            "Contact verification and consent-sensitive outreach controls",
            "Reviewer-visible audit history and customer-specific export authorization",
        ],
        "coverage_summary": counts,
        "preview_rows": people_summary.get("preview_rows", []),
        "downloads": {
            "accounts_csv": "/api/msci/export/accounts.csv",
            "people_csv": "/api/msci/export/people.csv",
            "people_review_csv": "/api/msci/export/people-review.csv",
            "people_template_csv": "/api/msci/export/people-template.csv",
            "workbench_json": "/api/msci/workbench/v1",
        },
    }


def build_msci_workbench(
    target_bundle: dict[str, object],
    swf_bundle: dict[str, object],
    people_summary: dict[str, object],
) -> dict[str, object]:
    summary = target_bundle.get("summary", {})
    swf_summary = swf_bundle.get("summary", {})
    people_export = build_msci_people_export(people_summary)
    return {
        "schema_version": MSCI_SCHEMA_VERSION,
        "generated_at": iso_now(),
        "summary_cards": [
            {"label": "Target accounts", "value": str(summary.get("total_targets", 0)), "note": "Rows in the normalized account workbook"},
            {"label": "API potential", "value": human_number(float(summary.get("total_api_potential", 0.0))), "note": "Modeled account-level potential from the workbook"},
            {"label": "Managed assets", "value": human_number(float(summary.get("total_assets_managed", 0.0))), "note": "Aggregate managed-assets figure across target accounts"},
            {"label": "Accessible people", "value": str(people_summary.get("summary", {}).get("people_total", 0)), "note": "Authenticated people records available for export"},
        ],
        "top_targets": summary.get("top_targets", []),
        "type_breakdown": summary.get("type_breakdown", []),
        "state_breakdown": summary.get("state_breakdown", []),
        "people_export": people_export,
        "analytics": build_msci_analytics(target_bundle, people_summary),
        "sovereign_seed_summary": swf_summary,
    }


def atlas_materialize_payload(payload: dict[str, object]) -> dict[str, object]:
    if not ATLAS_URI:
        return {
            "status": "missing_env",
            "tone": "watch",
            "backend": "local_runtime_only",
            "note": "Set SWFI_ATLAS_URI to materialize preview packets into Atlas. Atlas Data API is not used.",
        }

    try:
        from pymongo import MongoClient
        from pymongo.server_api import ServerApi
    except Exception:
        return {
            "status": "missing_driver",
            "tone": "watch",
            "backend": "local_runtime_only",
            "note": "SWFI_ATLAS_URI is set, but pymongo is not installed in this runtime.",
        }

    client = None
    try:
        client = MongoClient(ATLAS_URI, server_api=ServerApi("1"), serverSelectionTimeoutMS=2500)
        client.admin.command("ping")
        collection = client[ATLAS_DB][ATLAS_COLLECTION]
        collection.replace_one(
            {"packet_name": DASHBOARD_SCHEMA_VERSION},
            {
                "packet_name": DASHBOARD_SCHEMA_VERSION,
                "schema_version": payload["schema_version"],
                "generated_at": payload["generated_at"],
                "payload": payload,
            },
            upsert=True,
        )
        return {
            "status": "materialized",
            "tone": "ok",
            "backend": f"atlas:{ATLAS_DB}.{ATLAS_COLLECTION}",
            "note": "Preview payload materialized into Atlas using a driver-based connection.",
        }
    except Exception as exc:
        return {
            "status": "connection_failed",
            "tone": "blocked",
            "backend": "local_runtime_only",
            "note": f"Atlas connection failed: {exc.__class__.__name__}",
        }
    finally:
        if client is not None:
            client.close()


def build_launch_checklist(atlas_status: dict[str, object]) -> list[dict[str, str]]:
    return [
        {
            "title": "Environment variables",
            "status": "partial",
            "note": "Need explicit env management for GEMINI_API_KEY, SWFI_SANDBOX_API_KEY, SWFI_PRIVATE_EXPORT_TOKEN, SWFI_SECURITY_CONTACT_URI, DASHBOARD_TTL_SECONDS, local file paths, and optional SWFI_ATLAS_* settings.",
        },
        {
            "title": "Auth / session assumptions",
            "status": "partial",
            "note": "A controlled-access preview login now gates the terminal and protected APIs. Production still needs customer-specific auth, user lifecycle, and entitlement binding.",
        },
        {
            "title": "Protected exports and audit trail",
            "status": "partial",
            "note": f"Private export routes are now session, token, or local gated, rate limited, and appended to {SWFI_EXPORT_AUDIT_LOG}, but production still needs customer-specific authorization and reviewer-visible audit history.",
        },
        {
            "title": "Legal and source-policy posture",
            "status": "partial",
            "note": "Manual-only enrichment sources such as LinkedIn and guessed-email workflows should remain off the automated production path unless counsel and policy controls explicitly clear them.",
        },
        {
            "title": "Rate limits and timeout budget",
            "status": "partial",
            "note": f"Research and private-export routes now have basic runtime throttles ({RESEARCH_RATE_LIMIT_PER_MINUTE}/min research, {EXPORT_RATE_LIMIT_PER_MINUTE}/min exports). Production still needs source-specific retry and rate-limit policy.",
        },
        {
            "title": "Error states and no-data fallback",
            "status": "partial",
            "note": "Preview has safe empty-state fallbacks, but production needs clear operator-visible failure and retry states.",
        },
        {
            "title": "Cache strategy",
            "status": "partial",
            "note": "Current preview uses 15-minute in-memory cache plus no-store responses. Production needs warm-cache and rollback behavior.",
        },
        {
            "title": "Static build and rollback path",
            "status": "partial",
            "note": "Host-aware HTML, crawler controls, and a rollbackable static runtime now exist, but the public production default still needs an explicit auth and deployment decision.",
        },
        {
            "title": "Security headers and disclosure path",
            "status": "ok" if SWFI_SECURITY_CONTACT_CONFIGURED else "partial",
            "note": "security.txt is now published and the HTML surface is header hardened. Final public launch should confirm the monitored security disclosure contact.",
        },
        {
            "title": "Crawl and agent discovery",
            "status": "ok",
            "note": "robots.txt, sitemap.xml, llms.txt, and host-aware metadata are now part of the runtime surface. llms.txt is treated as supplemental rather than authoritative.",
        },
        {
            "title": "Entitlements and usage monitoring",
            "status": "blocked",
            "note": "The market standard now includes entitlements-aware delivery, usage monitoring, and a unified field model across channels.",
        },
        {
            "title": "Atlas preview storage",
            "status": str(atlas_status.get("tone", "watch")),
            "note": str(atlas_status.get("note", "")),
        },
    ]


def build_statuses(
    concern_source: dict[str, str | None],
    aum_source: dict[str, str | None],
    atlas_status: dict[str, object],
    sandbox_status: dict[str, object],
    people_summary: dict[str, object],
) -> list[dict[str, str]]:
    return [
        {
            "source": "Profiles + Key People",
            "status": str(people_summary.get("tone", "watch")),
            "note": (
                f"Authenticated people access summary is live with {people_summary.get('summary', {}).get('people_total', 0)} accessible records."
                if people_summary.get("status") == "ok"
                else str(people_summary.get("source", {}).get("note", "People-access export is not configured."))
            ),
        },
        {
            "source": "Datafeeds",
            "status": "ok" if concern_source.get("status") == "ok" else "blocked",
            "note": "Client blocker rows loaded from the live sheet." if concern_source.get("status") == "ok" else str(concern_source.get("note", "")),
        },
        {
            "source": "API Access",
            "status": str(sandbox_status.get("tone", "watch")) if SWFI_SANDBOX_API_KEY else ("ok" if aum_source.get("status") == "ok" else "blocked"),
            "note": (
                f"Public docs plus {sandbox_status.get('summary', {}).get('accessible_collections', 0)} authenticated sandbox collections are reachable."
                if SWFI_SANDBOX_API_KEY
                else "Public collection docs parsed from api.swfi.com."
            ),
        },
        {
            "source": "Security posture",
            "status": "ok",
            "note": "Session-backed preview login, hardened headers, controlled export gates, audit logging, and preview-host crawl blocking are now in the runtime surface.",
        },
        {
            "source": "Storage + cache",
            "status": str(atlas_status.get("tone", "watch")),
            "note": str(atlas_status.get("note", "")),
        },
    ]


def build_sources(
    concern_source: dict[str, str | None],
    aum_source: dict[str, str | None],
    target_source: dict[str, str | None],
    swf_source: dict[str, str | None],
    roadmap_source: dict[str, str | None],
    sandbox_source: dict[str, str | None],
    people_source: dict[str, str | None],
) -> list[dict[str, str | None]]:
    retrieved_at = iso_now()
    return merge_sources(
        [concern_source, aum_source, target_source, swf_source, roadmap_source, sandbox_source, people_source],
        [
            make_source_entry(
                "proposal_scope",
                "Feed modernization proposal",
                "document_extraction_required",
                "google_docs_shared_view",
                retrieved_at,
                "manual_summary",
                "high",
                "ok",
                evidence_url=PROPOSAL_SHEET_URL,
            ),
            make_source_entry(
                "platform_feedback",
                "Platform feedback memo",
                "manual_enrichment_only",
                "user_supplied_feedback",
                retrieved_at,
                "manual_capture",
                "high",
                "ok",
            ),
            make_source_entry(
                "email_automation",
                "Automated email streams note",
                "authenticated_private_source",
                "user_supplied_ops_note",
                retrieved_at,
                "manual_capture",
                "medium",
                "ok",
            ),
            make_source_entry(
                "authenticated_review",
                "Authenticated IA review",
                "authenticated_private_source",
                "private_swfi_workspace",
                retrieved_at,
                "manual_alignment_review",
                "medium",
                "ok",
                note=PRIVATE_IA_NOTE,
            ),
            make_source_entry(
                "msci_email_thread",
                "MSCI API requirement thread",
                "document_extraction_required",
                "user_supplied_email_thread",
                retrieved_at,
                "manual_capture",
                "high",
                "ok",
                document_pointer="/Users/mirror-admin/Downloads/swfi/Fwd_ MSCI API.eml",
                note="Confirms the People Search versus internal extract mismatch and the required MSCI export fields.",
            ),
            make_source_entry(
                "production_handover_thread",
                "Production support dependency and handover thread",
                "document_extraction_required",
                "user_supplied_email_thread",
                retrieved_at,
                "manual_capture",
                "high",
                "ok",
                document_pointer="/Users/mirror-admin/Downloads/swfi/Fwd_ SWFI- Production support dependency & handover.eml",
                note="Confirms live production sensitivity, handover dependencies, and the need for controlled deployment.",
            ),
            make_source_entry(
                "security_txt_standard",
                "RFC 9116 security.txt standard",
                "official_policy_source",
                "rfc_editor",
                retrieved_at,
                "web_research",
                "high",
                "ok",
                evidence_url="https://www.rfc-editor.org/rfc/rfc9116",
            ),
            make_source_entry(
                "owasp_headers",
                "OWASP secure headers guidance",
                "official_policy_source",
                "owasp",
                retrieved_at,
                "web_research",
                "high",
                "ok",
                evidence_url="https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html",
            ),
            make_source_entry(
                "ftc_can_spam",
                "FTC CAN-SPAM compliance guidance",
                "official_policy_source",
                "ftc",
                retrieved_at,
                "web_research",
                "high",
                "ok",
                evidence_url="https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business",
            ),
            make_source_entry(
                "ico_legitimate_interests",
                "ICO legitimate interests guidance",
                "official_policy_source",
                "ico",
                retrieved_at,
                "web_research",
                "high",
                "ok",
                evidence_url="https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/legitimate-interests/when-can-we-rely-on-legitimate-interests/",
            ),
            make_source_entry(
                "linkedin_crawling_terms",
                "LinkedIn crawling terms",
                "official_policy_source",
                "linkedin",
                retrieved_at,
                "web_research",
                "high",
                "ok",
                evidence_url="https://www.linkedin.com/legal/crawling-terms",
            ),
            make_source_entry(
                "openai_crawlers",
                "OpenAI crawler controls",
                "official_policy_source",
                "openai",
                retrieved_at,
                "web_research",
                "high",
                "ok",
                evidence_url="https://platform.openai.com/docs/bots",
            ),
            make_source_entry(
                "google_ai_search",
                "Google AI search guidance",
                "official_policy_source",
                "google_search_central",
                retrieved_at,
                "web_research",
                "high",
                "ok",
                evidence_url="https://developers.google.com/search/blog/2025/05/succeeding-in-ai-search",
            ),
            make_source_entry(
                "preqin_benchmark",
                "Preqin benchmark",
                "benchmark_only_not_integration_target",
                "official_public_site",
                retrieved_at,
                "web_research",
                "high",
                "ok",
                evidence_url="https://www.preqin.com/our-products/preqin-pro",
            ),
            make_source_entry(
                "pitchbook_benchmark",
                "PitchBook benchmark",
                "benchmark_only_not_integration_target",
                "official_public_site",
                retrieved_at,
                "web_research",
                "high",
                "ok",
                evidence_url="https://pitchbook.com/help/data-feed-api-crm-direct-data-solutions-q3-2025",
            ),
            make_source_entry(
                "bloomberg_benchmark",
                "Bloomberg benchmark",
                "benchmark_only_not_integration_target",
                "official_public_site",
                retrieved_at,
                "web_research",
                "high",
                "ok",
                evidence_url="https://professional.bloomberg.com/products/data/data-connectivity/server-api/",
            ),
            make_source_entry(
                "aladdin_benchmark",
                "BlackRock Aladdin benchmark",
                "benchmark_only_not_integration_target",
                "official_public_site",
                retrieved_at,
                "web_research",
                "high",
                "ok",
                evidence_url="https://www.blackrock.com/aladdin/products/aladdin-platform",
            ),
            make_source_entry(
                "kkr_benchmark",
                "KKR institutional benchmark",
                "benchmark_only_not_integration_target",
                "official_public_site",
                retrieved_at,
                "web_research",
                "medium",
                "ok",
                evidence_url="https://www.kkr.com/",
            ),
        ],
    )


def build_dashboard_payload() -> dict[str, object]:
    concern_bundle = load_concern_rows()
    aum_bundle = parse_aum_docs()
    target_bundle = load_target_accounts()
    swf_bundle = load_swf_seeds()
    roadmap_bundle = load_platform_improvements()
    sandbox_bundle = get_sandbox_api_map()
    people_summary = get_msci_people_summary(target_bundle)

    concerns = concern_bundle["rows"]
    aum_docs = aum_bundle["docs"]
    lanes = build_lane_summaries(concerns)
    sources = build_sources(
        concern_bundle["source"],
        aum_bundle["source"],
        target_bundle["source"],
        swf_bundle["source"],
        roadmap_bundle["source"],
        sandbox_bundle["source"],
        people_summary["source"],
    )
    confidence_summary = build_confidence_summary(sources)
    msci_workbench = build_msci_workbench(target_bundle, swf_bundle, people_summary)

    payload = {
        "schema_version": DASHBOARD_SCHEMA_VERSION,
        "generated_at": iso_now(),
        "preview_posture": {
            "mode": "controlled_access",
            "note": "Use as a controlled-access production surface with protected export routes and explicit rollout checks.",
        },
        "proposal": PROPOSAL,
        "platform_reference": PLATFORM_REFERENCE,
        "collection_model": COLLECTION_MODEL,
        "source_taxonomy": SOURCE_TAXONOMY,
        "sources": sources,
        "confidence_summary": confidence_summary,
        "metric_cards": build_metric_cards(concerns, target_bundle.get("summary", {}), confidence_summary, people_summary),
        "lanes": lanes,
        "concerns": concerns,
        "action_queue": build_action_queue(concerns),
        "aum_docs": aum_docs,
        "data_coverage": build_data_coverage(people_summary),
        "canonical_schema": {
            "models": CANONICAL_SCHEMA,
            "provenance_contract": PROVENANCE_CONTRACT,
        },
        "benchmark_matrix": BENCHMARK_MATRIX,
        "required_api_stack": REQUIRED_API_STACK,
        "external_api_matrix": EXTERNAL_API_MATRIX,
        "connector_maturity": build_maturity_groups(),
        "platform_feedback": PLATFORM_FEEDBACK,
        "email_streams": EMAIL_AUTOMATION_STREAMS,
        "security_controls": build_security_controls(),
        "legal_risk_register": build_legal_risk_register(),
        # Only surface roadmap when the upstream CSV actually produced content;
        # an empty dict leaked to the client as `roadmap: {}` which reads as a
        # broken section in the dashboard.
        **({"roadmap": roadmap_bundle["roadmap"]} if roadmap_bundle.get("roadmap") else {}),
        "msci_workbench": msci_workbench,
        "sandbox_api": sandbox_bundle,
    }

    atlas_status = atlas_materialize_payload(payload)
    payload["atlas"] = atlas_status
    payload["statuses"] = build_statuses(concern_bundle["source"], aum_bundle["source"], atlas_status, sandbox_bundle, people_summary)
    payload["readiness"] = build_readiness(concerns, aum_docs, atlas_status, people_summary)
    payload["gaps"] = build_gap_list(atlas_status, people_summary)
    payload["production_launch_checklist"] = build_launch_checklist(atlas_status)
    payload["notes"] = [PRIVATE_IA_NOTE]
    return payload


def get_dashboard_payload() -> dict[str, object]:
    now = time.time()
    with _cache_lock:
        cached = _dashboard_cache.get("payload")
        timestamp = float(_dashboard_cache.get("timestamp", 0.0))
        if cached and now - timestamp < CACHE_TTL_SECONDS:
            return cached

    with _dashboard_build_lock:
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


def get_guardrail(query_text: str) -> str | None:
    lowered = query_text.lower().strip()
    if not lowered:
        return "Ask about canonical schema, provenance, MSCI export readiness, coverage gaps, or launch readiness."
    if any(token in lowered for token in ACTION_HINTS):
        return "This copilot is read-only. It analyzes product and delivery readiness; it does not execute workflows."
    if any(token in lowered for token in NON_PRODUCT_HINTS):
        return "This copilot is limited to SWFI product, workflow, schema, and launch-readiness analysis."
    return None


def make_evidence(label: str, source: str, url: str | None = None) -> dict[str, str | None]:
    return {"label": label, "source": source, "url": url}


def build_fallback_answer(query_text: str, payload: dict[str, object]) -> tuple[str, list[dict[str, str | None]]]:
    lowered = query_text.lower()
    evidence: list[dict[str, str | None]] = []
    parts: list[str] = []

    if "msci" in lowered and any(token in lowered for token in ("people", "export", "contact")):
        export_info = payload["msci_workbench"]["people_export"]
        parts.append(str(export_info["answer"]))
        evidence.append(make_evidence("MSCI export contract", "Preview packet"))
        if export_info.get("downloads", {}).get("people_csv"):
            evidence.append(make_evidence("Protected people export", "SWFI terminal", export_info["downloads"]["people_csv"]))

    if any(token in lowered for token in ("provenance", "confidence", "evidence")):
        parts.append(
            "The preview now treats provenance as a first-class contract: every surfaced packet includes source system, retrieval time, extraction method, confidence/status, and an evidence URL or file pointer."
        )
        evidence.append(make_evidence("AUM docs", "SWFI API docs", AUM_DOCS_URL))

    if any(token in lowered for token in ("security", "legal", "risk", "privacy", "audit")):
        parts.append(
            "Security and legal posture are now explicit: preview hosts stay out of indexing, HTML responses ship with hardened browser headers, private export routes are gated and durably logged, and the remaining production blockers are auth, entitlement binding, and policy review of manual-only enrichment sources."
        )
        evidence.append(make_evidence("Launch checklist", "Preview packet"))
        evidence.append(make_evidence("RFC 9116", "Official source", "https://www.rfc-editor.org/rfc/rfc9116"))
        evidence.append(make_evidence("FTC CAN-SPAM", "Official source", "https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business"))

    if any(token in lowered for token in ("canonical", "schema", "object model")):
        parts.append(
            f"The canonical layer covers {len(payload['canonical_schema']['models'])} normalized objects: institution, fund, asset/AUM series, person/contact, document, opportunity/RFP, compliance event, and research/news item."
        )
        evidence.append(make_evidence("Canonical schema", "Preview packet"))

    if any(token in lowered for token in ("atlas", "mongodb")):
        parts.append(
            f"Atlas is handled as an optional driver-based preview storage layer. Current status: {payload['atlas']['note']}"
        )
        evidence.append(
            make_evidence(
                "PyMongo Atlas connection guide",
                "MongoDB docs",
                "https://www.mongodb.com/docs/languages/python/pymongo-driver/connect/connection-targets/",
            )
        )

    if any(token in lowered for token in ("email", "mandrill", "sendgrid", "newsletter", "alerts")):
        parts.append(
            "Two automated communication streams are modeled: daily subscriber alerts via Mandrill and the Public Fund Monitor every three days via SendGrid. The product gap is observability and evidence-backed job state inside the terminal."
        )

    if any(token in lowered for token in ("coverage", "gap", "benchmark", "preqin", "pitchbook", "bloomberg", "aladdin", "kkr")):
        parts.append(
            "The current public benchmark set is bigger than Preqin alone. SWFI still trails Preqin and PitchBook on direct data + CRM delivery, Bloomberg on entitlements and enterprise data operations, and Aladdin on API-first workflow depth and copilots. KKR remains a credibility benchmark rather than an integration target."
        )
        evidence.append(make_evidence("Preqin Pro", "Official source", "https://www.preqin.com/our-products/preqin-pro"))
        evidence.append(make_evidence("PitchBook Direct Data", "Official source", "https://pitchbook.com/help/data-feed-api-crm-direct-data-solutions-q3-2025"))
        evidence.append(make_evidence("Bloomberg SAPI", "Official source", "https://professional.bloomberg.com/products/data/data-connectivity/server-api/"))
        evidence.append(
            make_evidence(
                "BlackRock Aladdin",
                "Official source",
                "https://www.blackrock.com/aladdin/products/aladdin-platform",
            )
        )

    if not parts:
        parts.append(
            "The current build is no longer just a dashboard mock. It now defines the canonical object model, provenance contract, connector maturity map, sandbox-backed MSCI workbench, and the launch checklist for a controlled-access production rollout."
        )
        evidence.append(make_evidence("Preview packet", "SWFI terminal"))

    return " ".join(parts), evidence[:6]


def json_digest(value: object) -> str:
    packed = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(packed).hexdigest()[:16]


def build_research_context(
    query_text: str,
    payload: dict[str, object],
    fallback_answer: str,
    evidence: list[dict[str, str | None]],
) -> dict[str, object]:
    return {
        "user_query": query_text,
        "answer_seed": fallback_answer,
        "evidence_catalog": evidence,
        "approved_context": {
            "preview_posture": payload.get("preview_posture", {}),
            "canonical_schema_summary": {
                "model_count": len((payload.get("canonical_schema") or {}).get("models", [])),
                "model_names": [item.get("id") for item in (payload.get("canonical_schema") or {}).get("models", [])[:8]],
            },
            "coverage_highlights": (payload.get("data_coverage") or [])[:4],
            "msci_summary": {
                "target_accounts": ((payload.get("msci_workbench") or {}).get("summary") or {}).get("target_accounts", 0),
                "accessible_people": ((payload.get("msci_workbench") or {}).get("summary") or {}).get("people_total", 0),
                "people_with_email": ((payload.get("msci_workbench") or {}).get("summary") or {}).get("with_email", 0),
                "people_with_phone": ((payload.get("msci_workbench") or {}).get("summary") or {}).get("with_phone", 0),
            },
            "gaps": (payload.get("gaps") or [])[:5],
            "security_controls": (payload.get("security_controls") or [])[:4],
            "legal_risks": (payload.get("legal_risk_register") or [])[:4],
        },
    }


def build_research_governance(answer_mode: str, source_bundle_id: str, *, provider: str | None = None) -> dict[str, object]:
    return {
        "policy_version": AI_POLICY_VERSION,
        "prompt_version": REFUSAL_PROMPT_ID if answer_mode in {"guardrail", "policy_refusal"} else GROUNDED_RESEARCH_PROMPT_ID,
        "registry_version": PROMPT_REGISTRY_VERSION,
        "nugget_contract": NUGGET_SCHEMA_VERSION,
        "source_bundle_id": source_bundle_id,
        "answer_mode": answer_mode,
        "provider": provider,
    }


def normalize_research_status(value: object) -> str:
    text = str(value or "").strip()
    normalized = {
        "verified": "Verified",
        "derived": "Derived",
        "conflicted": "Conflicted",
        "missing": "Missing",
        "needsreview": "NeedsReview",
        "needs_review": "NeedsReview",
        "rejected": "Rejected",
    }.get(re.sub(r"[^a-z]", "", text.lower()), "")
    return normalized or "NeedsReview"


def normalize_research_confidence(value: object) -> str:
    text = str(value or "").strip().lower()
    normalized = {
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "none": "None",
    }.get(text, "")
    return normalized or "Low"


def parse_json_text(text: str) -> dict[str, object] | None:
    cleaned = str(text or "").strip()
    if not cleaned:
        return None
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        pass
    match = re.search(r"\{.*\}", cleaned, flags=re.S)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None


def validate_governed_research_result(
    candidate: dict[str, object] | None,
    evidence_catalog: list[dict[str, str | None]],
) -> dict[str, object] | None:
    if not isinstance(candidate, dict):
        return None
    answer = normalize_text(str(candidate.get("answer") or ""))
    if not answer:
        return None
    status = normalize_research_status(candidate.get("status"))
    confidence = normalize_research_confidence(candidate.get("confidence"))
    allowed_by_label = {str(item.get("label")): item for item in evidence_catalog if str(item.get("label") or "").strip()}
    selected_labels: list[str] = []
    raw_labels = candidate.get("source_labels") or []
    if isinstance(raw_labels, list):
        for label in raw_labels:
            key = str(label or "").strip()
            if key and key in allowed_by_label and key not in selected_labels:
                selected_labels.append(key)
    selected_refs = [allowed_by_label[label] for label in selected_labels]
    inference_note = normalize_text(str(candidate.get("inference_note") or ""))

    if status == "Verified" and not selected_refs:
        return None
    if not selected_refs and status in {"Derived", "Conflicted"}:
        return None
    if not selected_refs:
        status = "NeedsReview"
        confidence = "None"

    return {
        "answer": answer,
        "status": status,
        "confidence": confidence,
        "evidence": selected_refs,
        "inference_note": inference_note,
    }


def build_policy_refusal_payload(
    answer: str,
    source_bundle_id: str,
    *,
    guardrail: str,
    evidence: list[dict[str, str | None]] | None = None,
) -> dict[str, object]:
    evidence = evidence or []
    return {
        "schema_version": RESEARCH_SCHEMA_VERSION,
        "generated_at": iso_now(),
        "answer": answer,
        "evidence": evidence,
        "source_refs": evidence,
        "guardrail": guardrail,
        "model": None,
        "provider": None,
        "provider_label": "Policy refusal",
        "status": "Rejected" if guardrail == "scope_limited" else "NeedsReview",
        "confidence": "None",
        "inference_note": "No supported answer was published beyond the approved refusal language.",
        "sources": [],
        "confidence_summary": {},
        "gaps": [],
        "governance": build_research_governance("policy_refusal" if guardrail != "scope_limited" else "guardrail", source_bundle_id),
        "policy_version": AI_POLICY_VERSION,
        "prompt_version": REFUSAL_PROMPT_ID,
        "registry_version": PROMPT_REGISTRY_VERSION,
        "source_bundle_id": source_bundle_id,
    }


def extract_openai_output_text(response: dict[str, object]) -> str | None:
    direct_text = str(response.get("output_text") or "").strip()
    if direct_text:
        return direct_text

    output = response.get("output", [])
    if not isinstance(output, list):
        return None

    chunks: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            text = str(content.get("text") or content.get("output_text") or "").strip()
            if text:
                chunks.append(text)
    return "\n".join(chunks).strip() or None


def call_openai_governed_research(query_text: str, research_context: dict[str, object]) -> dict[str, str] | None:
    if not OPENAI_API_KEY:
        return None

    payload = {
        "model": OPENAI_MODEL,
        "instructions": RESEARCH_GOVERNED_SYSTEM_PROMPT,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": json.dumps(research_context),
                    }
                ],
            }
        ],
        "temperature": 0,
        "max_output_tokens": 420,
        "store": False,
    }

    model_candidates = [OPENAI_MODEL]
    if OPENAI_MODEL != "gpt-4.1-mini":
        model_candidates.append("gpt-4.1-mini")

    for model_name in model_candidates:
        payload["model"] = model_name
        try:
            response = fetch_json(
                "https://api.openai.com/v1/responses",
                payload=payload,
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                timeout=25,
            )
        except urlerror.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace").lower()
            if exc.code in (400, 404) and "model" in body:
                continue
            return None
        except Exception:
            return None

        text = extract_openai_output_text(response)
        if text:
            return {
                "answer": text,
                "model": model_name,
                "provider": "OpenAI Responses",
                "provider_label": f"OpenAI · {model_name}",
            }
    return None


def extract_anthropic_output_text(response: dict[str, object]) -> str | None:
    chunks: list[str] = []
    for item in response.get("content", []):
        if not isinstance(item, dict):
            continue
        if item.get("type") == "text":
            text = str(item.get("text") or "").strip()
            if text:
                chunks.append(text)
    return "\n".join(chunks).strip() or None


def call_anthropic_governed_research(query_text: str, research_context: dict[str, object]) -> dict[str, str] | None:
    if not ANTHROPIC_API_KEY:
        return None

    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 420,
        "temperature": 0,
        "system": RESEARCH_GOVERNED_SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": json.dumps(research_context),
            }
        ],
    }
    try:
        response = fetch_json(
            "https://api.anthropic.com/v1/messages",
            payload=payload,
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": ANTHROPIC_API_VERSION,
            },
            timeout=25,
        )
    except Exception:
        return None

    text = extract_anthropic_output_text(response)
    if not text:
        return None
    return {
        "answer": text,
        "model": str(response.get("model") or ANTHROPIC_MODEL),
        "provider": "Anthropic Messages",
        "provider_label": f"Anthropic · {response.get('model') or ANTHROPIC_MODEL}",
    }


def call_gemini_governed_research(query_text: str, research_context: dict[str, object]) -> dict[str, str] | None:
    if not GEMINI_API_KEY:
        return None

    payload = {
        "system_instruction": {"parts": [{"text": RESEARCH_GOVERNED_SYSTEM_PROMPT}]},
        "contents": [
            {
                "parts": [
                    {
                        "text": json.dumps(research_context)
                    }
                ]
            }
        ],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 420},
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
    if not text:
        return None
    return {
        "answer": text,
        "model": GEMINI_MODEL,
        "provider": "Google Gemini",
        "provider_label": f"Google Gemini · {GEMINI_MODEL}",
    }


def call_governed_research_model(query_text: str, research_context: dict[str, object]) -> dict[str, str] | None:
    openai_result = call_openai_governed_research(query_text, research_context)
    if openai_result:
        return openai_result
    anthropic_result = call_anthropic_governed_research(query_text, research_context)
    if anthropic_result:
        return anthropic_result
    return call_gemini_governed_research(query_text, research_context)


def build_research_payload(query_text: str) -> dict[str, object]:
    guardrail = get_guardrail(query_text)
    source_bundle_id = json_digest({"query": query_text.strip(), "guardrail": bool(guardrail)})
    if guardrail:
        return build_policy_refusal_payload(guardrail, source_bundle_id, guardrail="scope_limited")

    payload = get_dashboard_payload()
    fallback_answer, evidence = build_fallback_answer(query_text, payload)
    research_context = build_research_context(query_text, payload, fallback_answer, evidence)
    source_bundle_id = json_digest(research_context)
    model_result = call_governed_research_model(query_text, research_context)
    validated_result = validate_governed_research_result(
        parse_json_text(model_result["answer"]) if model_result else None,
        evidence,
    )
    answer_mode = "deterministic_fallback"
    answer = fallback_answer
    selected_evidence = evidence
    status = "Derived" if evidence else "NeedsReview"
    confidence = "Medium" if len(evidence) >= 2 else "Low" if evidence else "None"
    inference_note = "Rendered from the deterministic source-backed answer seed."
    provider = None
    provider_label = "Governed deterministic fallback"
    model_name = None

    if validated_result:
        answer_mode = "governed_model"
        answer = str(validated_result["answer"])
        selected_evidence = list(validated_result["evidence"])
        status = str(validated_result["status"])
        confidence = str(validated_result["confidence"])
        inference_note = str(validated_result.get("inference_note") or "") or inference_note
        provider = model_result["provider"] if model_result else None
        provider_label = model_result["provider_label"] if model_result else provider_label
        model_name = model_result["model"] if model_result else None

    return {
        "schema_version": RESEARCH_SCHEMA_VERSION,
        "generated_at": iso_now(),
        "answer": answer,
        "evidence": selected_evidence,
        "source_refs": selected_evidence,
        "guardrail": "source_grounded",
        "model": model_name,
        "provider": provider,
        "provider_label": provider_label,
        "status": status,
        "confidence": confidence,
        "inference_note": inference_note,
        "sources": payload["sources"],
        "confidence_summary": payload["confidence_summary"],
        "gaps": payload["gaps"],
        "governance": build_research_governance(answer_mode, source_bundle_id, provider=provider),
        "policy_version": AI_POLICY_VERSION,
        "prompt_version": GROUNDED_RESEARCH_PROMPT_ID,
        "registry_version": PROMPT_REGISTRY_VERSION,
        "source_bundle_id": source_bundle_id,
    }


def build_accounts_csv() -> str:
    payload = get_dashboard_payload()
    rows = payload["msci_workbench"]["top_targets"]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Account Name",
            "Account Type",
            "City",
            "State",
            "Assets",
            "Assets Managed",
            "API Potential",
            "Priority Tier",
            "Mapping Focus",
            "Source System",
            "Retrieval Time",
            "Extraction Method",
            "Confidence",
            "Evidence Pointer",
        ]
    )
    for row in rows:
        provenance = row["provenance"]
        writer.writerow(
            [
                row["account_name"],
                row["account_type"],
                row["city"],
                row["state"],
                int(row["assets"]),
                int(row["assets_managed"]),
                int(row["api_potential"]),
                row["priority_tier"],
                row["mapping_focus"],
                provenance["source_system"],
                provenance["retrieval_time"],
                provenance["extraction_method"],
                provenance["confidence"],
                provenance["evidence_url_or_pointer"],
            ]
        )
    return output.getvalue()


def build_people_csv() -> str:
    export_payload = get_msci_people_export_payload(load_target_accounts())
    rows = export_payload.get("rows", [])
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "SWFI Contact ID",
            "SWFI Account (Company) ID",
            "Name",
            "Email",
            "Title",
            "Account Name",
            "Phone",
            "Institution Type",
            "City",
            "State",
            "Country",
            "Region",
            "LinkedIn",
            "Role",
            "Target Account Overlap",
            "Source System",
            "Retrieval Time",
            "Extraction Method",
            "Confidence",
            "Evidence Pointer",
        ]
    )
    for row in rows:
        provenance = row["provenance"]
        writer.writerow(
            [
                row["swfi_contact_id"],
                row["swfi_account_id"],
                row["name"],
                row["email"],
                row["title"],
                row["account_name"],
                row["phone"],
                row["institution_type"],
                row["city"],
                row["state"],
                row["country"],
                row["region"],
                row["linkedin"],
                row["role"],
                row["target_account_overlap"],
                provenance["source_system"],
                provenance["retrieval_time"],
                provenance["extraction_method"],
                provenance["confidence"],
                provenance["evidence_url_or_pointer"],
            ]
        )
    return output.getvalue()


def build_people_review_csv() -> str:
    export_payload = get_msci_people_export_payload(load_target_accounts())
    rows = export_payload.get("review_queue", [])
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Name",
            "SWFI Contact ID",
            "SWFI Account (Company) ID",
            "Title",
            "Review Reason",
            "Evidence Pointer",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row["name"],
                row["swfi_contact_id"],
                row["swfi_account_id"],
                row["title"],
                row["reason"],
                row["evidence_pointer"],
            ]
        )
    return output.getvalue()


def build_people_template_csv() -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "SWFI Contact ID",
            "SWFI Account (Company) ID",
            "Name",
            "Email",
            "Title",
            "Account Name",
            "Phone",
            "Institution Type",
            "City",
            "State",
            "Country",
            "Source Confidence",
            "Retrieval Time",
            "Evidence Pointer",
        ]
    )
    return output.getvalue()


def clear_runtime_caches() -> None:
    with _cache_lock:
        _dashboard_cache["timestamp"] = 0.0
        _dashboard_cache["payload"] = None
        _sandbox_cache["timestamp"] = 0.0
        _sandbox_cache["payload"] = None
        _msci_people_summary_cache["timestamp"] = 0.0
        _msci_people_summary_cache["payload"] = None
        _msci_people_export_cache["timestamp"] = 0.0
        _msci_people_export_cache["payload"] = None
        _external_probe_cache["timestamp"] = 0.0
        _external_probe_cache["payload"] = None


def probe_gleif_live() -> dict[str, object]:
    url = "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=State%20Street%20Corporation&page%5Bsize%5D=1"
    payload = fetch_json(url, timeout=10)
    record = (payload.get("data") or [{}])[0]
    attributes = record.get("attributes") or {}
    legal_name = (
        (attributes.get("entity") or {}).get("legalName", {}) or {}
    ).get("name") or "State Street Corporation"
    lei = record.get("id") or attributes.get("lei") or "unknown"
    return {
        "live_status": "ok",
        "probe_tone": "ok",
        "probe_note": f"Matched {legal_name} to LEI {lei}.",
        "probe_url": url,
        "checked_at": iso_now(),
    }


def probe_sec_live() -> dict[str, object]:
    url = "https://data.sec.gov/submissions/CIK0000093751.json"
    payload = fetch_json(url, timeout=10, headers={"User-Agent": "SWFI Terminal/0.4 admin@swfi.com"})
    recent = (payload.get("filings") or {}).get("recent") or {}
    forms = recent.get("form") or []
    filing_dates = recent.get("filingDate") or []
    latest_form = forms[0] if forms else "unknown"
    latest_date = filing_dates[0] if filing_dates else "unknown"
    company_name = payload.get("name") or "State Street Corp"
    return {
        "live_status": "ok",
        "probe_tone": "ok",
        "probe_note": f"Fetched SEC submissions for {company_name}; latest filing {latest_form} on {latest_date}.",
        "probe_url": url,
        "checked_at": iso_now(),
    }


def probe_ofac_live() -> dict[str, object]:
    url = "https://ofac.treasury.gov/ofac-sanctions-lists"
    html_text = fetch_text(url, timeout=10)
    if "Sanctions List Service" not in html_text:
        raise RuntimeError("unexpected_ofac_response")
    return {
        "live_status": "ok",
        "probe_tone": "ok",
        "probe_note": "Sanctions List Service page responded and exposed the current OFAC download/search surface.",
        "probe_url": url,
        "checked_at": iso_now(),
    }


def probe_openfigi_live() -> dict[str, object]:
    url = "https://api.openfigi.com/v3/mapping"
    payload = fetch_json(
        url,
        payload=[{"idType": "TICKER", "idValue": "STT", "exchCode": "US"}],
        timeout=10,
        headers={"Content-Type": "application/json"},
    )
    rows = payload[0].get("data") if isinstance(payload, list) and payload else []
    first = rows[0] if rows else {}
    figi = first.get("figi", "unknown")
    security = first.get("securityDescription") or first.get("name") or "State Street Corp"
    return {
        "live_status": "ok",
        "probe_tone": "ok",
        "probe_note": f"Mapped STT (US) to FIGI {figi} for {security}.",
        "probe_url": url,
        "checked_at": iso_now(),
    }


def probe_companies_house_live() -> dict[str, object]:
    if not COMPANIES_HOUSE_API_KEY:
        return {
            "live_status": "blocked",
            "probe_tone": "blocked",
            "probe_note": "API key not configured on this runtime. Public docs are mapped, but live registry lookups are not enabled.",
            "probe_url": "https://developer.company-information.service.gov.uk/get-started",
            "checked_at": iso_now(),
        }
    auth = base64.b64encode(f"{COMPANIES_HOUSE_API_KEY}:".encode("utf-8")).decode("ascii")
    url = "https://api.company-information.service.gov.uk/search/companies?q=state%20street"
    payload = fetch_json(url, timeout=10, headers={"Authorization": f"Basic {auth}"})
    first = (payload.get("items") or [{}])[0]
    title = first.get("title") or "State Street candidate"
    company_number = first.get("company_number") or "unknown"
    return {
        "live_status": "ok",
        "probe_tone": "ok",
        "probe_note": f"Registry search returned {title} ({company_number}).",
        "probe_url": url,
        "checked_at": iso_now(),
    }


def probe_opencorporates_live() -> dict[str, object]:
    if not OPENCORPORATES_API_TOKEN:
        return {
            "live_status": "watch",
            "probe_tone": "watch",
            "probe_note": "API token not configured. This rail stays mapped as hybrid open-or-paid until commercial rights are confirmed.",
            "probe_url": "https://api.opencorporates.com/documentation/API-Reference",
            "checked_at": iso_now(),
        }
    url = f"https://api.opencorporates.com/v0.4/companies/search?q=state%20street&api_token={parse.quote(OPENCORPORATES_API_TOKEN)}"
    payload = fetch_json(url, timeout=10)
    companies = (((payload.get("results") or {}).get("companies")) or [])
    first = companies[0].get("company", {}) if companies else {}
    name = first.get("name") or "State Street candidate"
    jurisdiction = first.get("jurisdiction_code") or "unknown"
    return {
        "live_status": "ok",
        "probe_tone": "ok",
        "probe_note": f"Company search returned {name} in jurisdiction {jurisdiction}.",
        "probe_url": url,
        "checked_at": iso_now(),
    }


def probe_newsapi_live() -> dict[str, object]:
    if not NEWSAPI_KEY:
        return {
            "live_status": "blocked",
            "probe_tone": "blocked",
            "probe_note": "API key not configured. NewsAPI remains a paid production rail, not a live dependency in this runtime.",
            "probe_url": "https://newsapi.org/pricing",
            "checked_at": iso_now(),
        }
    url = f"https://newsapi.org/v2/everything?q=sovereign%20wealth%20fund&pageSize=1&apiKey={parse.quote(NEWSAPI_KEY)}"
    payload = fetch_json(url, timeout=10)
    total = int(payload.get("totalResults", 0))
    return {
        "live_status": "ok",
        "probe_tone": "ok",
        "probe_note": f"Search returned {total} matching articles for the sample sovereign-wealth query.",
        "probe_url": "https://newsapi.org/v2/everything",
        "checked_at": iso_now(),
    }


def build_live_external_api_matrix() -> list[dict[str, object]]:
    probes = {
        "GLEIF LEI API": probe_gleif_live,
        "SEC EDGAR / data.sec.gov": probe_sec_live,
        "Companies House API": probe_companies_house_live,
        "OFAC Sanctions List Service": probe_ofac_live,
        "OpenFIGI API": probe_openfigi_live,
        "OpenCorporates API": probe_opencorporates_live,
        "NewsAPI": probe_newsapi_live,
    }
    results: list[dict[str, object]] = []
    for item in EXTERNAL_API_MATRIX:
        enriched = dict(item)
        probe_fn = probes.get(str(item.get("name", "")))
        try:
            probe_payload = probe_fn() if probe_fn else {
                "live_status": "watch",
                "probe_tone": "watch",
                "probe_note": "No runtime probe implemented for this connector.",
                "probe_url": item.get("url"),
                "checked_at": iso_now(),
            }
        except Exception as exc:
            probe_payload = {
                "live_status": "blocked",
                "probe_tone": "blocked",
                "probe_note": f"Live probe failed: {exc.__class__.__name__}",
                "probe_url": item.get("url"),
                "checked_at": iso_now(),
            }
        enriched.update(probe_payload)
        results.append(enriched)
    return results


def get_live_external_api_matrix() -> list[dict[str, object]]:
    now = time.time()
    with _cache_lock:
        cached = _external_probe_cache.get("payload")
        timestamp = float(_external_probe_cache.get("timestamp", 0.0))
        if cached and now - timestamp < CONNECTOR_PROBE_TTL_SECONDS:
            return cached

    payload = build_live_external_api_matrix()
    with _cache_lock:
        _external_probe_cache["timestamp"] = now
        _external_probe_cache["payload"] = payload
    return payload


def read_export_audit_events(limit: int = 50) -> list[dict[str, object]]:
    if not SWFI_EXPORT_AUDIT_LOG.exists():
        return []
    try:
        lines = SWFI_EXPORT_AUDIT_LOG.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    events: list[dict[str, object]] = []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            continue
        if len(events) >= limit:
            break
    return events


def build_msci_analytics(target_bundle: dict[str, object], people_summary: dict[str, object]) -> dict[str, object]:
    summary = target_bundle.get("summary", {})
    people_counts = people_summary.get("summary", {})
    total_people = max(int(people_counts.get("people_total", 0)), 1)
    analytics_cards = [
        {
            "label": "Target accounts",
            "value": str(summary.get("total_targets", 0)),
            "note": "High-confidence target rows loaded from the workbook",
        },
        {
            "label": "People with email",
            "value": f"{round((int(people_counts.get('with_email', 0)) / total_people) * 100)}%",
            "note": f"{people_counts.get('with_email', 0)} of {people_counts.get('people_total', 0)} accessible people",
        },
        {
            "label": "People with phone",
            "value": f"{round((int(people_counts.get('with_phone', 0)) / total_people) * 100)}%",
            "note": f"{people_counts.get('with_phone', 0)} phone values currently available",
        },
        {
            "label": "Entity-linked preview rows",
            "value": f"{round((int(people_counts.get('preview_with_entity_reference', 0)) / max(int(people_counts.get('preview_rows', 0)), 1)) * 100)}%",
            "note": f"{people_counts.get('preview_with_entity_reference', 0)} of {people_counts.get('preview_rows', 0)} preview rows carry an entity reference",
        },
    ]
    return {
        "cards": analytics_cards,
        "downloads": {
            "msci_analytics_csv": "/api/reports/msci-analytics.csv",
            "external_api_matrix_csv": "/api/reports/external-api-matrix.csv",
            "export_history_csv": "/api/reports/export-history.csv",
            "phase1_summary_md": "/api/reports/phase1-summary.md",
        },
    }


def build_msci_analytics_csv() -> str:
    target_bundle = load_target_accounts()
    people_summary = get_msci_people_summary(target_bundle)
    analytics = build_msci_analytics(target_bundle, people_summary)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Metric", "Value", "Note"])
    for card in analytics["cards"]:
        writer.writerow([card["label"], card["value"], card["note"]])
    return output.getvalue()


def build_external_api_matrix_csv() -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["API", "Access", "Status", "Live Status", "Checked At", "Use Case", "Note", "Live Note", "URL", "Probe URL"])
    for item in get_live_external_api_matrix():
        writer.writerow(
            [
                item["name"],
                item["access"],
                item["status"],
                item.get("live_status", ""),
                item.get("checked_at", ""),
                item["use_case"],
                item["note"],
                item.get("probe_note", ""),
                item["url"],
                item.get("probe_url", ""),
            ]
        )
    return output.getvalue()


def build_export_history_csv(limit: int = 200) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Route", "Outcome", "Auth Mode", "Host", "Client IP", "User Agent"])
    for item in read_export_audit_events(limit):
        writer.writerow(
            [
                item.get("timestamp", ""),
                item.get("route", ""),
                item.get("outcome", ""),
                item.get("auth_mode", ""),
                item.get("host", ""),
                item.get("client_ip", ""),
                item.get("user_agent", ""),
            ]
        )
    return output.getvalue()


def build_phase1_summary_md() -> str:
    target_bundle = load_target_accounts()
    people_summary = get_msci_people_summary(target_bundle)
    export_payload = get_cached_msci_people_export_payload(include_stale=True) or {
        "summary": {
            "rows_exported": int(people_summary.get("summary", {}).get("people_total", 0)),
            "review_queue": 0,
        }
    }
    dashboard = get_cached_dashboard_payload(include_stale=True) or {}
    lines = [
        "# SWFI Beta - Capital Intelligence Layer v0.1",
        "",
        f"Generated: {iso_now()}",
        "",
        "## Phase 1 wedge",
        "- Controlled-access landing and login",
        "- MSCI Key People workspace",
        "- Clean CSV export path with audit logging",
        "- Trust layer with source, status, timestamp, and confidence",
        "",
        "## MSCI numbers",
        f"- Target accounts: {target_bundle.get('summary', {}).get('total_targets', 0)}",
        f"- Accessible people: {people_summary.get('summary', {}).get('people_total', 0)}",
        f"- People with email: {people_summary.get('summary', {}).get('with_email', 0)}",
        f"- People with phone: {people_summary.get('summary', {}).get('with_phone', 0)}",
        f"- Export rows: {export_payload.get('summary', {}).get('rows_exported', 0)}",
        f"- Review queue: {export_payload.get('summary', {}).get('review_queue', 0)}",
        "",
        "## Free/public external rails identified",
    ]
    for item in EXTERNAL_API_MATRIX:
        lines.append(f"- {item['name']}: {item['access']} - {item['use_case']}")
    gaps = dashboard.get("gaps", []) if isinstance(dashboard, dict) else []
    if gaps:
        lines.extend(
            [
                "",
                "## Current blockers",
            ]
        )
        for gap in gaps[:6]:
            lines.append(f"- {gap['title']}: {gap['detail']}")
        lines.append("")
    return "\n".join(lines)


def read_ai_doc(filename: str) -> str:
    path = AI_DOCS_ROOT / filename
    return path.read_text(encoding="utf-8")


def build_ai_governance_md() -> str:
    return read_ai_doc("SWFI_AI_GOVERNANCE.md")


def build_nugget_schema_json() -> str:
    raw = read_ai_doc("nugget_schema_v1.json")
    return json.dumps(json.loads(raw), indent=2) + "\n"


def build_prompt_registry_yaml() -> str:
    return read_ai_doc("prompt_registry.yaml")


def get_cached_dashboard_payload(*, include_stale: bool = True) -> dict[str, object] | None:
    now = time.time()
    with _cache_lock:
        cached = _dashboard_cache.get("payload")
        timestamp = float(_dashboard_cache.get("timestamp", 0.0))
        if not cached:
            return None
        if include_stale or now - timestamp < CACHE_TTL_SECONDS:
            return cached
    return None


def get_cached_msci_people_export_payload(*, include_stale: bool = True) -> dict[str, object] | None:
    now = time.time()
    with _cache_lock:
        cached = _msci_people_export_cache.get("payload")
        timestamp = float(_msci_people_export_cache.get("timestamp", 0.0))
        if not cached:
            return None
        if include_stale or now - timestamp < MSCI_EXPORT_TTL_SECONDS:
            return cached
    return None


def build_admin_payload() -> dict[str, object]:
    dashboard = get_cached_dashboard_payload(include_stale=True) or {}
    target_bundle = load_target_accounts()
    people_summary = get_msci_people_summary(target_bundle)
    live_external_matrix = get_live_external_api_matrix()
    export_payload = get_cached_msci_people_export_payload(include_stale=True) or {
        "tone": "ok" if people_summary.get("status") == "ok" else "watch",
        "summary": {
            "rows_exported": int(people_summary.get("summary", {}).get("people_total", 0)),
        },
    }
    audit_events = read_export_audit_events(100)
    atlas_status = dashboard.get("atlas", {}) if isinstance(dashboard, dict) else {}
    sandbox_status = dashboard.get("sandbox_api", {}) if isinstance(dashboard, dict) else {}
    if not atlas_status:
        atlas_status = {
            "status": "not_warmed",
            "tone": "watch",
            "note": "Dashboard packet has not been warmed yet on this runtime.",
        }
    if not sandbox_status:
        sandbox_status = {
            "tone": "ok" if SWFI_SANDBOX_API_KEY else "blocked",
            "source": {
                "note": (
                    "Sandbox credentials are configured on this runtime."
                    if SWFI_SANDBOX_API_KEY
                    else "Sandbox credentials are not configured on this runtime."
                )
            },
        }
    errors: list[dict[str, str]] = []
    if atlas_status.get("status") != "materialized":
        errors.append({"title": "Atlas preview storage", "detail": str(atlas_status.get("note", "")), "status": str(atlas_status.get("tone", "watch"))})
    if people_summary.get("summary", {}).get("with_phone", 0) < 250:
        errors.append({"title": "Phone coverage remains thin", "detail": "MSCI export is populated, but phone coverage is still low for high-confidence outreach use.", "status": "partial"})
    statuses = [
        {"label": "Dashboard packet", "status": "ok" if dashboard else "watch", "note": f"Last built {dashboard.get('generated_at', 'not warmed yet') if isinstance(dashboard, dict) else 'not warmed yet'}"},
        {"label": "MSCI target workbook", "status": "ok" if target_bundle.get('summary', {}).get('total_targets', 0) else "blocked", "note": f"{target_bundle.get('summary', {}).get('total_targets', 0)} target accounts parsed"},
        {"label": "People export", "status": str(export_payload.get("tone", "watch")), "note": f"{export_payload.get('summary', {}).get('rows_exported', 0)} rows exported"},
        {"label": "Export audit log", "status": "ok" if SWFI_EXPORT_AUDIT_LOG.exists() else "watch", "note": f"{len(audit_events)} recent events loaded"},
        {"label": "Sandbox API", "status": str(sandbox_status.get('tone', 'watch')), "note": str(sandbox_status.get('source', {}).get('note', ''))},
        {"label": "Public connector probes", "status": "ok" if sum(1 for item in live_external_matrix if item.get("live_status") == "ok") >= 4 else "partial", "note": f"{sum(1 for item in live_external_matrix if item.get('live_status') == 'ok')} connectors responded on the latest probe"},
    ]
    return {
        "schema_version": ADMIN_SCHEMA_VERSION,
        "generated_at": iso_now(),
        "summary_cards": [
            {"label": "Target accounts", "value": str(target_bundle.get("summary", {}).get("total_targets", 0)), "note": "Rows parsed into the MSCI workspace"},
            {"label": "Accessible people", "value": str(people_summary.get("summary", {}).get("people_total", 0)), "note": "Authenticated people records"},
            {"label": "Exports logged", "value": str(len(audit_events)), "note": "Recent export audit events"},
            {"label": "Live public probes", "value": str(sum(1 for item in live_external_matrix if item.get("live_status") == "ok")), "note": "Public/free connector probes responding on the latest check"},
        ],
        "statuses": statuses,
        "errors": errors,
        "export_history": audit_events,
        "analytics": build_msci_analytics(target_bundle, people_summary),
        "external_api_matrix": live_external_matrix,
        "reports": [
            {"label": "MSCI analytics CSV", "url": "/api/reports/msci-analytics.csv"},
            {"label": "External API matrix CSV", "url": "/api/reports/external-api-matrix.csv"},
            {"label": "Connector status JSON", "url": "/api/connectors/v1"},
            {"label": "Export history CSV", "url": "/api/reports/export-history.csv"},
            {"label": "Phase 1 summary", "url": "/api/reports/phase1-summary.md"},
            {"label": "AI governance spec", "url": "/api/reports/ai-governance.md"},
            {"label": "Nugget schema JSON", "url": "/api/reports/nugget-schema.json"},
            {"label": "Prompt registry YAML", "url": "/api/reports/prompt-registry.yaml"},
        ],
        "rebuild": {"url": "/api/admin/rebuild", "method": "POST"},
    }


def parse_request_host(headers) -> str:
    forwarded = headers.get("X-Forwarded-Host", "").split(",")[0].strip()
    host = forwarded or headers.get("Host", "")
    return host.split(":")[0].strip().lower()


def parse_request_proto(headers) -> str:
    return headers.get("X-Forwarded-Proto", "").split(",")[0].strip().lower()


def get_request_client_ip(handler: "SiteHandler") -> str:
    forwarded = handler.headers.get("CF-Connecting-IP", "").strip() or handler.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    return forwarded or str(handler.client_address[0])


def login_configured() -> bool:
    return bool(SWFI_PREVIEW_AUTH_PASSWORD)


def is_local_request(handler: "SiteHandler") -> bool:
    return is_local_host(parse_request_host(handler.headers))


def parse_cookies(headers) -> dict[str, str]:
    raw = headers.get("Cookie", "")
    if not raw:
        return {}
    jar = cookies.SimpleCookie()
    try:
        jar.load(raw)
    except Exception:
        return {}
    return {key: morsel.value for key, morsel in jar.items()}


def prune_expired_sessions(now: float | None = None) -> None:
    current = now or time.time()
    expired = [token for token, data in _session_store.items() if float(data.get("expires_at", 0.0)) <= current]
    for token in expired:
        _session_store.pop(token, None)


def create_session(username: str) -> str:
    token = secrets.token_urlsafe(32)
    now = time.time()
    with _session_lock:
        prune_expired_sessions(now)
        _session_store[token] = {
            "username": username,
            "issued_at": now,
            "expires_at": now + PREVIEW_SESSION_TTL_SECONDS,
        }
    return token


def get_session(handler: "SiteHandler") -> dict[str, object] | None:
    token = parse_cookies(handler.headers).get(SESSION_COOKIE_NAME, "")
    if not token:
        return None
    now = time.time()
    with _session_lock:
        prune_expired_sessions(now)
        session = _session_store.get(token)
        if not session:
            return None
        session["expires_at"] = now + PREVIEW_SESSION_TTL_SECONDS
        return dict(session)


def clear_session(handler: "SiteHandler") -> None:
    token = parse_cookies(handler.headers).get(SESSION_COOKIE_NAME, "")
    if not token:
        return
    with _session_lock:
        _session_store.pop(token, None)


def request_is_authenticated(handler: "SiteHandler") -> bool:
    return authenticated_request_mode(handler) is not None


def authenticated_request_mode(handler: "SiteHandler") -> str | None:
    if is_local_request(handler):
        return "localhost"
    if get_session(handler) is not None:
        return "session"
    return None


def sanitize_next_path(value: str | None) -> str:
    text = str(value or "/").strip()
    if not text.startswith("/") or text.startswith("//"):
        return "/"
    return text or "/"


def is_public_host(host: str) -> bool:
    return host in {"swfi.com", "www.swfi.com"}


def is_local_host(host: str) -> bool:
    return host in {"127.0.0.1", "localhost"}


def request_origin(host: str, proto: str) -> str:
    clean_host = host.strip().lower()
    if not clean_host:
        return SWFI_PUBLIC_SITE_ORIGIN
    if is_public_host(clean_host):
        return SWFI_PUBLIC_SITE_ORIGIN
    scheme = proto or ("http" if is_local_host(clean_host) else "https")
    return f"{scheme}://{clean_host}"


def check_rate_limit(bucket: str, key: str, limit: int, *, window_seconds: int = 60) -> tuple[bool, int]:
    now = time.time()
    cache_key = (bucket, key)
    with _request_rate_lock:
        timestamps = [timestamp for timestamp in _request_rate_cache.get(cache_key, []) if now - timestamp < window_seconds]
        if len(timestamps) >= limit:
            retry_after = max(1, int(window_seconds - (now - timestamps[0])))
            _request_rate_cache[cache_key] = timestamps
            return False, retry_after
        timestamps.append(now)
        _request_rate_cache[cache_key] = timestamps
    return True, 0


# ---------------------------------------------------------------------------
# Demo surface helpers — /demo/api/ask, /demo/health, /demo/api/coverage
# ---------------------------------------------------------------------------

def _load_demo_entity_cache() -> dict:
    """Read entities.json from disk. Returns parsed dict (may have count=0)."""
    seed_path = ROOT / "demo" / "seed" / "entities.json"
    try:
        return json.loads(seed_path.read_text(encoding="utf-8"))
    except Exception:
        return {"count": 0, "entities": [], "generated_at": None}


def get_demo_entities() -> dict:
    """Return the in-process entity cache, refreshing from disk if older than 6h."""
    global _demo_entity_cache, _demo_cache_loaded_at
    with _demo_cache_lock:
        now = time.time()
        if not _demo_entity_cache or (now - _demo_cache_loaded_at) > _DEMO_CACHE_TTL_SECONDS:
            _demo_entity_cache = _load_demo_entity_cache()
            _demo_cache_loaded_at = now
        return _demo_entity_cache


def _compact_entity(e: dict) -> dict:
    """Return a stripped-down entity record for the system prompt.
    Drops enrichment arrays (_aum_series, contacts detail, etc.) to keep
    prompt size small. Keeps the fields needed for grounded answers.
    """
    latest = e.get("_aum_latest") or {}
    aum = (
        e.get("assets") or e.get("managed_assets") or e.get("aum")
        or latest.get("assets") or ""
    )
    contacts = e.get("contacts") or []
    first_contact = ""
    if contacts and isinstance(contacts, list):
        c = contacts[0]
        first_contact = " ".join(filter(None, [c.get("name"), c.get("title")])).strip()
    prov = e.get("provenance") or {}
    return {k: v for k, v in {
        "id": e.get("_id") or e.get("id"),
        "name": e.get("name"),
        "type": e.get("type"),
        "country": e.get("country"),
        "region": e.get("region"),
        "aum_usd": aum,
        "aum_period": latest.get("period"),
        "summary": (e.get("summary") or e.get("background") or "")[:300],
        "contact": first_contact or None,
        "source": prov.get("evidence_url_or_pointer"),
    }.items() if v not in (None, "", 0)}


def build_demo_system_prompt(entities: dict) -> str:
    entity_list = entities.get("entities", [])
    count = entities.get("count", len(entity_list))
    return (
        "You are the SWFI verified-intelligence assistant. "
        f"You have access ONLY to the following curated packet of {count} verified "
        "sovereign wealth and institutional investor entities.\n"
        "Rules you MUST follow:\n"
        "1. Answer ONLY from facts present in the entity packet below.\n"
        "2. If the packet does not contain the fund, investor, or number the user asked about, "
        "say so clearly — do not guess or fabricate.\n"
        "3. Every numeric claim in your answer (AUM, allocation %, date, etc.) MUST correspond "
        "to an entry in your sources list with a URL or document pointer from the packet. "
        "If you cannot cite it, do not claim it.\n"
        "4. 'I don't know' or 'Not in the verified data' are acceptable answers.\n"
        "5. Return your answer as a JSON object only — no text outside it:\n"
        '   {"text": "...", "sources": [{"label": "...", "url": "...", "field": "..."}], "status": "ok"}\n\n'
        "ENTITY PACKET:\n"
        + json.dumps([_compact_entity(e) for e in entity_list], ensure_ascii=False)
    )


def build_demo_stream_prompt(entities: dict) -> str:
    """System prompt for streaming mode — plain prose + SOURCES_JSON trailer line."""
    entity_list = entities.get("entities", [])
    count = entities.get("count", len(entity_list))
    return (
        "You are the SWFI verified-intelligence assistant. "
        f"You have access ONLY to the following curated packet of {count} verified "
        "sovereign wealth and institutional investor entities.\n"
        "Rules you MUST follow:\n"
        "1. Answer ONLY from facts present in the entity packet below.\n"
        "2. If the data does not contain what the user asked about, say so — do not fabricate.\n"
        "3. Every numeric claim (AUM, allocation %, date) MUST trace to a source in the packet.\n"
        "4. Write your answer in fluent, specific, data-rich prose. No JSON wrapper.\n"
        "5. After a blank line at the very end of your response, output EXACTLY one line:\n"
        "   SOURCES_JSON: [{\"label\":\"...\",\"url\":\"...\",\"field\":\"...\"},...]\n"
        "   This must be valid compact JSON. Nothing after this line.\n\n"
        "ENTITY PACKET:\n"
        + json.dumps([_compact_entity(e) for e in entity_list], ensure_ascii=False)
    )


def call_gemini_for_demo(query: str, entities: dict) -> dict:
    """Call Gemini 2.5 Pro (fallback: 2.5 Flash). Returns parsed response dict."""
    if not GEMINI_API_KEY:
        return {
            "text": "AI search is not available: API key not configured on this runtime.",
            "sources": [],
            "status": "error",
        }
    system_prompt = build_demo_system_prompt(entities)
    models = ["gemini-2.5-pro", "gemini-2.5-flash"]
    last_err = ""
    for model in models:
        try:
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
                f":generateContent?key={GEMINI_API_KEY}"
            )
            body = json.dumps({
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"role": "user", "parts": [{"text": query}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            }).encode("utf-8")
            req = request.Request(
                url, data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with request.urlopen(req, timeout=12) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
            text = raw["candidates"][0]["content"]["parts"][0]["text"].strip()
            parsed = json.loads(text)
            parsed["_model"] = model
            return parsed
        except Exception as exc:
            last_err = str(exc)
            continue
    return {
        "text": f"AI search temporarily unavailable. Please try again shortly.",
        "sources": [],
        "status": "error",
        "_last_err": last_err,
    }


def stream_gemini_demo(query: str, entities: dict, history: list | None = None):
    """Generator: yields SSE-formatted bytes token by token from Gemini streaming API.

    Event shapes:
      data: {"type":"token","text":"..."}\\n\\n   — incremental text chunk
      data: {"type":"done","sources":[...],"model":"..."}\\n\\n  — terminal event
      data: {"type":"error","text":"..."}\\n\\n   — on failure

    history: list of {role: "user"|"model", text: "..."} for multi-turn context.
    """
    if not GEMINI_API_KEY:
        yield b'data: {"type":"error","text":"AI search not configured on this runtime."}\n\n'
        return

    system_prompt = build_demo_stream_prompt(entities)
    # flash first for lower TTFT; fall back to pro
    models = ["gemini-2.5-flash", "gemini-2.5-pro"]

    # Build multi-turn contents from history + current query
    contents: list[dict] = []
    for turn in (history or [])[-6:]:  # cap at last 3 exchanges (6 turns)
        role = turn.get("role", "user")
        text = str(turn.get("text", "")).strip()
        if role in ("user", "model") and text:
            contents.append({"role": role, "parts": [{"text": text}]})
    contents.append({"role": "user", "parts": [{"text": query}]})

    for model in models:
        full_text_parts: list[str] = []
        try:
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
                f":streamGenerateContent?alt=sse&key={GEMINI_API_KEY}"
            )
            body = json.dumps({
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": contents,
                "generationConfig": {"temperature": 0.3},
            }).encode("utf-8")
            req = request.Request(
                url, data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with request.urlopen(req, timeout=60) as resp:
                for raw_line in resp:
                    line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
                    if not line.startswith("data:"):
                        continue
                    data_str = line[5:].strip()
                    if not data_str or data_str == "[DONE]":
                        continue
                    try:
                        chunk = json.loads(data_str)
                        text_piece = (
                            chunk.get("candidates", [{}])[0]
                            .get("content", {})
                            .get("parts", [{}])[0]
                            .get("text", "")
                        )
                    except (json.JSONDecodeError, IndexError):
                        continue
                    if not text_piece:
                        continue
                    full_text_parts.append(text_piece)
                    evt = json.dumps({"type": "token", "text": text_piece}, ensure_ascii=False)
                    yield f"data: {evt}\n\n".encode("utf-8")

            # Parse SOURCES_JSON trailer from accumulated text
            full_text = "".join(full_text_parts)
            sources: list[dict] = []
            for ln in reversed(full_text.splitlines()):
                ln = ln.strip()
                if ln.startswith("SOURCES_JSON:"):
                    try:
                        sources = json.loads(ln[len("SOURCES_JSON:"):].strip())
                    except Exception:
                        pass
                    break

            done_evt = json.dumps(
                {"type": "done", "sources": sources, "model": model},
                ensure_ascii=False,
            )
            yield f"data: {done_evt}\n\n".encode("utf-8")
            return

        except Exception:
            continue  # try next model

    err_evt = json.dumps({"type": "error", "text": "AI search temporarily unavailable."})
    yield f"data: {err_evt}\n\n".encode("utf-8")


def log_demo_ask(ip_raw: str, query: str, model: str, latency_ms: int) -> None:
    """Append one structured line to the demo-ask log.
    IP is hashed (sha256 prefix), response text is NOT logged per spec."""
    try:
        DEMO_ASK_LOG.parent.mkdir(parents=True, exist_ok=True)
        ip_hash = hashlib.sha256(ip_raw.encode("utf-8")).hexdigest()[:16]
        line = json.dumps({
            "ts": iso_now(),
            "ip_hash": ip_hash,
            "query": query[:500],
            "model": model,
            "latency_ms": latency_ms,
        }, ensure_ascii=False)
        with DEMO_ASK_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass  # log failures must never crash a request


# ---------------------------------------------------------------------------

def redact_path_tokens(path: str) -> str:
    parsed = parse.urlsplit(path)
    if not parsed.query:
        return path
    query = parse.parse_qs(parsed.query, keep_blank_values=True)
    changed = False
    for key in ("token", "access_token", "api_key"):
        if key in query:
            query[key] = ["REDACTED"]
            changed = True
    if not changed:
        return path
    sanitized_query = parse.urlencode(query, doseq=True)
    return parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, sanitized_query, parsed.fragment))


def redact_requestline_tokens(requestline: str) -> str:
    parts = requestline.split(" ")
    if len(parts) < 2:
        return requestline
    parts[1] = redact_path_tokens(parts[1])
    return " ".join(parts)


def build_site_meta(host: str, proto: str) -> dict[str, object]:
    public = is_public_host(host)
    title = "SWFI | Institutional Investor Profiles, Transactions, RFPs, Key People, Asset Allocation, Datafeeds, API Access"
    description = (
        "Institutional investor data across sovereign wealth funds, public pensions, central banks, "
        "endowments, family offices, Profiles, Transactions, Mandates, RFPs, Key People, Asset Allocation, "
        "Datafeeds, and API Access."
    )
    keywords = [
        "sovereign wealth fund data",
        "institutional investor profiles",
        "public pension data",
        "central bank profiles",
        "family office profiles",
        "transactions",
        "mandates",
        "RFPs",
        "key people",
        "asset allocation",
        "datafeeds",
        "API access",
    ]
    canonical = f"{request_origin(host, proto)}/"
    robots = "index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1" if public else "noindex,nofollow,noarchive"
    # Attribute the Organization and WebSite entities to the current origin.
    # On public hosts this is swfi.com; on preview/controlled hosts (e.g.
    # swfi.activemirror.ai) it points to the preview canonical so JSON-LD does
    # not misattribute the preview surface to the public site.
    entity_url = SWFI_PUBLIC_SITE_ORIGIN if public else canonical.rstrip("/")
    json_ld = [
        {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "SWFI",
            "url": entity_url,
            "keywords": keywords,
        },
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "SWFI",
            "url": entity_url,
            "description": description,
            "keywords": keywords,
        },
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": title,
            "url": canonical,
            "description": description,
            "keywords": keywords,
            "about": [
                "Sovereign Wealth Funds",
                "Public Pensions",
                "Central Banks",
                "Endowments",
                "Family Offices",
                "Profiles",
                "Transactions",
                "Mandates",
                "RFPs",
                "Key People",
                "Asset Allocation",
                "Datafeeds",
                "API Access",
            ],
        },
    ]
    return {
        "title": title,
        "description": description,
        "canonical": canonical,
        "robots": robots,
        "keywords": keywords,
        "json_ld": json_ld,
        "public": public,
    }


def build_page_meta(
    host: str,
    proto: str,
    *,
    path: str,
    title: str,
    description: str,
    about: list[str],
    force_private: bool = False,
) -> dict[str, object]:
    public = is_public_host(host) and not force_private
    canonical = f"{request_origin(host, proto)}{path}"
    robots = "index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1" if public else "noindex,nofollow,noarchive"
    keywords = about + ["SWFI", "institutional investor data", "datafeeds", "API access"]
    # Attribute the Organization entity to the current origin on preview hosts
    # (see build_site_meta for rationale).
    entity_url = SWFI_PUBLIC_SITE_ORIGIN if public else f"{request_origin(host, proto)}/"
    json_ld = [
        {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "SWFI",
            "url": entity_url.rstrip("/") if entity_url != SWFI_PUBLIC_SITE_ORIGIN else SWFI_PUBLIC_SITE_ORIGIN,
            "keywords": keywords,
        },
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": title,
            "url": canonical,
            "description": description,
            "keywords": keywords,
            "about": about,
        },
    ]
    return {
        "title": title,
        "description": description,
        "canonical": canonical,
        "robots": robots,
        "keywords": keywords,
        "json_ld": json_ld,
        "public": public,
    }


def render_template_html(template_name: str, meta: dict[str, object], csp_nonce: str) -> str:
    html_text = (ROOT / template_name).read_text(encoding="utf-8")
    json_ld = json.dumps(meta["json_ld"]).replace("</", "<\\/")
    html_text = re.sub(r"<title>.*?</title>", f"<title>{html.escape(str(meta['title']))}</title>", html_text, count=1, flags=re.S)
    html_text = re.sub(
        r'<meta name="description" content="[^"]*"\s*/?>',
        f'<meta name="description" content="{html.escape(str(meta["description"]))}" />',
        html_text,
        count=1,
    )
    injection = f"""
    <meta name="robots" content="{html.escape(str(meta["robots"]))}" />
    <meta name="googlebot" content="{html.escape(str(meta["robots"]))}" />
    <meta name="keywords" content="{html.escape(', '.join(meta.get("keywords", [])))}" />
    <meta name="application-name" content="SWFI" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="{html.escape(str(meta["title"]))}" />
    <meta property="og:description" content="{html.escape(str(meta["description"]))}" />
    <meta property="og:url" content="{html.escape(str(meta["canonical"]))}" />
    <meta property="og:site_name" content="SWFI" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{html.escape(str(meta["title"]))}" />
    <meta name="twitter:description" content="{html.escape(str(meta["description"]))}" />
    <link rel="canonical" href="{html.escape(str(meta["canonical"]))}" />
    <script type="application/ld+json" nonce="{html.escape(csp_nonce)}">{json_ld}</script>
    """.strip()
    return html_text.replace("</head>", f"{injection}\n  </head>", 1)


def render_index_html(host: str, proto: str, csp_nonce: str) -> str:
    return render_template_html("index.html", build_site_meta(host, proto), csp_nonce)


def render_landing_html(host: str, proto: str, csp_nonce: str) -> str:
    meta = build_page_meta(
        host,
        proto,
        path="/",
        title="SWFI | Institutional Investor Profiles, Transactions, RFPs, Key People, Asset Allocation, Datafeeds, API Access",
        description=(
            "Institutional investor data across sovereign wealth funds, public pensions, central banks, "
            "endowments, family offices, Profiles, Transactions, RFPs, Key People, Asset Allocation, Datafeeds, and API Access."
        ),
        about=[
            "Sovereign Wealth Funds",
            "Public Pensions",
            "Central Banks",
            "Endowments",
            "Family Offices",
            "Profiles",
            "Transactions",
            "RFPs",
            "Key People",
            "Asset Allocation",
            "Datafeeds",
            "API Access",
        ],
    )
    return render_template_html("landing.html", meta, csp_nonce)


def render_msci_html(host: str, proto: str, csp_nonce: str) -> str:
    meta = build_page_meta(
        host,
        proto,
        path="/msci",
        title="SWFI | MSCI Key People Export Workspace",
        description="Controlled-access SWFI workspace for MSCI Key People exports, account mapping, and delivery review.",
        about=["MSCI", "Key People", "Profiles", "Datafeeds", "API Access", "Asset Allocation"],
    )
    return render_template_html("msci.html", meta, csp_nonce)


def render_admin_html(host: str, proto: str, csp_nonce: str) -> str:
    meta = build_page_meta(
        host,
        proto,
        path="/admin",
        title="SWFI | Admin Console",
        description="Hidden SWFI admin console for feed status, export history, audit logs, analytics, and controlled rebuild actions.",
        about=["Admin Console", "Datafeeds", "API Access", "Profiles", "Key People"],
        force_private=True,
    )
    return render_template_html("admin.html", meta, csp_nonce)


def render_login_html(host: str, proto: str, csp_nonce: str, *, error: str | None = None, next_path: str = "/") -> str:
    meta = build_page_meta(
        host,
        proto,
        path="/login",
        title="SWFI | Controlled Access",
        description="Controlled-access login for the SWFI intelligence terminal.",
        about=["Controlled access", "Profiles", "Datafeeds", "API Access"],
        force_private=True,
    )
    error_block = f'<p class="auth-error">{html.escape(error)}</p>' if error else ""
    next_value = html.escape(next_path or "/")
    html_text = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>SWFI | Controlled Access</title>
    <meta name="description" content="Controlled-access login for the SWFI intelligence terminal." />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>
    <div class="page-shell auth-shell">
      <div class="auth-panel panel">
        <p class="sys-label">Controlled access</p>
        <h1>SWFI Intelligence Terminal</h1>
        <p class="auth-copy">This preview requires sign-in before Profiles, Transactions, Mandates, RFPs, Key People, Asset Allocation, Datafeeds, API Access, and the MSCI workspace are loaded.</p>
        {error_block}
        <form class="auth-form" method="post" action="/auth/login">
          <input type="hidden" name="next" value="{next_value}" />
          <label>
            <span>Username</span>
            <input type="text" name="username" autocomplete="username" required />
          </label>
          <label>
            <span>Password</span>
            <input type="password" name="password" autocomplete="current-password" required />
          </label>
          <button type="submit" class="nav-cta auth-submit">Sign in</button>
        </form>
        <p class="auth-note">Controlled-access preview. Sensitive exports remain separately protected.</p>
      </div>
    </div>
  </body>
</html>"""
    return render_template_html_text(html_text, meta, csp_nonce)


def render_template_html_text(html_text: str, meta: dict[str, object], csp_nonce: str) -> str:
    json_ld = json.dumps(meta["json_ld"]).replace("</", "<\\/")
    html_text = re.sub(r"<title>.*?</title>", f"<title>{html.escape(str(meta['title']))}</title>", html_text, count=1, flags=re.S)
    html_text = re.sub(
        r'<meta name="description" content="[^"]*"\s*/?>',
        f'<meta name="description" content="{html.escape(str(meta["description"]))}" />',
        html_text,
        count=1,
    )
    injection = f"""
    <meta name="robots" content="{html.escape(str(meta["robots"]))}" />
    <meta name="googlebot" content="{html.escape(str(meta["robots"]))}" />
    <meta name="keywords" content="{html.escape(', '.join(meta.get("keywords", [])))}" />
    <meta name="application-name" content="SWFI" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="{html.escape(str(meta["title"]))}" />
    <meta property="og:description" content="{html.escape(str(meta["description"]))}" />
    <meta property="og:url" content="{html.escape(str(meta["canonical"]))}" />
    <meta property="og:site_name" content="SWFI" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{html.escape(str(meta["title"]))}" />
    <meta name="twitter:description" content="{html.escape(str(meta["description"]))}" />
    <link rel="canonical" href="{html.escape(str(meta["canonical"]))}" />
    <script type="application/ld+json" nonce="{html.escape(csp_nonce)}">{json_ld}</script>
    """.strip()
    return html_text.replace("</head>", f"{injection}\n  </head>", 1)

def build_robots_txt(host: str) -> str:
    if is_public_host(host):
        return "\n".join(
            [
                "User-agent: *",
                "Allow: /",
                "",
                "User-agent: OAI-SearchBot",
                "Allow: /",
                "",
                "User-agent: Google-Extended",
                "Allow: /",
                "",
                "User-agent: OAI-AdsBot",
                "Allow: /",
                "",
                "User-agent: GPTBot",
                "Allow: /",
                "",
                "User-agent: Claude-SearchBot",
                "Allow: /",
                "",
                "User-agent: Claude-User",
                "Allow: /",
                "",
                "User-agent: ClaudeBot",
                "Allow: /",
                "",
                f"Sitemap: {SWFI_PUBLIC_SITE_ORIGIN}/sitemap.xml",
                "",
            ]
        )
    return "User-agent: *\nDisallow: /\n"


def build_llms_txt(host: str) -> str:
    if not is_public_host(host):
        return "Preview host only. Public AI discovery should target the canonical swfi.com host.\n"
    return "\n".join(
        [
            "# SWFI",
            "",
            "> Institutional investor data across Profiles, Transactions, Mandates, RFPs, Key People, Asset Allocation, Datafeeds, and API Access.",
            "",
            "Canonical: https://swfi.com/",
            "Primary path: /",
            "",
            "Machine-readable surfaces:",
            "- /sitemap.xml",
            "- /robots.txt",
            "- https://api.swfi.com/",
            "- https://api.swfi.com/collections",
            "- https://api.swfi.com/collections/aum",
            "",
            "Notes:",
            "- Public discovery should target swfi.com rather than preview hosts.",
            "- Sensitive export routes remain controlled-access surfaces.",
            "- llms.txt is supplemental and non-standard; robots and meta directives remain authoritative.",
            "- Visible page content and structured data should stay aligned.",
            "",
        ]
    )


def build_security_txt(host: str) -> str:
    # On preview/controlled hosts the disclosure surface is owned by the
    # Active Mirror operator, not the public SWFI property. Point the Canonical
    # URL at the current host's well-known path so reports land with the
    # infrastructure operator responsible for this preview.
    if is_public_host(host):
        canonical = f"{SWFI_PUBLIC_SITE_ORIGIN}/.well-known/security.txt"
    else:
        canonical = f"https://{host}/.well-known/security.txt"
    lines = [
        "# SWFI vulnerability disclosure",
        f"Contact: {SWFI_SECURITY_CONTACT_URI}",
        f"Canonical: {canonical}",
        f"Expires: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() + 15552000))}",
        "Preferred-Languages: en",
    ]
    if SWFI_SECURITY_POLICY_URL:
        lines.append(f"Policy: {SWFI_SECURITY_POLICY_URL}")
    if not is_public_host(host):
        lines.append("# Preview host operated by Active Mirror for SWFI. Reports about this host and its protected export routes should be sent to the Contact above.")
    return "\n".join(lines) + "\n"


def build_sitemap_xml(host: str, proto: str) -> str:
    root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    url = ET.SubElement(root, "url")
    ET.SubElement(url, "loc").text = f"{request_origin(host, proto)}/"
    ET.SubElement(url, "lastmod").text = time.strftime("%Y-%m-%d", time.gmtime())
    ET.SubElement(url, "changefreq").text = "daily"
    ET.SubElement(url, "priority").text = "1.0"
    return ET.tostring(root, encoding="unicode")


def build_content_security_policy(host: str, nonce: str) -> str:
    directives = [
        "default-src 'self'",
        f"script-src 'self' 'nonce-{nonce}'",
        f"script-src-elem 'self' 'nonce-{nonce}'",
        "style-src 'self' https://fonts.googleapis.com",
        "font-src 'self' https://fonts.gstatic.com",
        "img-src 'self' data:",
        "connect-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'",
        "manifest-src 'self'",
    ]
    if is_public_host(host):
        directives.append("upgrade-insecure-requests")
    return "; ".join(directives)


def private_export_auth_mode(handler: "SiteHandler", parsed: parse.ParseResult) -> str | None:
    if is_local_request(handler):
        return "localhost"
    if get_session(handler):
        return "session"
    if SWFI_PRIVATE_EXPORT_TOKEN:
        query_token = parse.parse_qs(parsed.query).get("token", [""])[0].strip()
        header_token = handler.headers.get("X-SWFI-Export-Token", "").strip()
        if header_token == SWFI_PRIVATE_EXPORT_TOKEN:
            return "header_token"
        if query_token == SWFI_PRIVATE_EXPORT_TOKEN:
            return "query_token"
    return None


def private_export_allowed(handler: "SiteHandler", parsed: parse.ParseResult) -> bool:
    return private_export_auth_mode(handler, parsed) is not None


def append_export_audit_event(handler: "SiteHandler", route: str, outcome: str, auth_mode: str | None) -> None:
    event = {
        "timestamp": iso_now(),
        "route": route,
        "outcome": outcome,
        "auth_mode": auth_mode or "denied",
        "host": parse_request_host(handler.headers),
        "client_ip": get_request_client_ip(handler),
        "user_agent": handler.headers.get("User-Agent", "")[:240],
    }
    try:
        SWFI_EXPORT_AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with _audit_log_lock:
            with SWFI_EXPORT_AUDIT_LOG.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event) + "\n")
    except Exception:
        return


class SiteHandler(http.server.SimpleHTTPRequestHandler):
    server_version = "SWFI/1.0"
    sys_version = ""

    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory or str(ROOT), **kwargs)

    def _cookie_secure(self) -> bool:
        return not is_local_request(self)

    def _session_cookie_value(self, value: str, *, max_age: int | None = None) -> str:
        parts = [f"{SESSION_COOKIE_NAME}={value}", "Path=/", "HttpOnly", "SameSite=Lax"]
        if max_age is not None:
            parts.append(f"Max-Age={max_age}")
        if self._cookie_secure():
            parts.append("Secure")
        return "; ".join(parts)

    def _send_common_headers(
        self,
        content_type: str,
        content_length: int,
        cache_control: str,
        *,
        csp_nonce: str | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        host = parse_request_host(self.headers)
        proto = parse_request_proto(self.headers)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(content_length))
        self.send_header("Cache-Control", cache_control)
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header(
            "Permissions-Policy",
            "accelerometer=(), autoplay=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()",
        )
        self.send_header("X-Frame-Options", "DENY")
        if csp_nonce:
            self.send_header("Content-Security-Policy", build_content_security_policy(host, csp_nonce))
        if proto == "https":
            self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")
        for header, value in (extra_headers or {}).items():
            self.send_header(header, value)

    def _write_json(
        self,
        payload: object,
        status: int = 200,
        *,
        head_only: bool = False,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self._send_common_headers("application/json", len(encoded), "no-store", extra_headers=extra_headers)
        self.end_headers()
        if not head_only:
            self.wfile.write(encoded)

    def _write_csv(self, payload: str, filename: str, *, head_only: bool = False) -> None:
        encoded = payload.encode("utf-8")
        self.send_response(200)
        self._send_common_headers(
            "text/csv; charset=utf-8",
            len(encoded),
            "no-store",
            extra_headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
        self.end_headers()
        if not head_only:
            self.wfile.write(encoded)

    def _write_text(
        self,
        payload: str,
        content_type: str,
        status: int = 200,
        *,
        cache_control: str = "public, max-age=300",
        head_only: bool = False,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        encoded = payload.encode("utf-8")
        self.send_response(status)
        self._send_common_headers(content_type, len(encoded), cache_control, extra_headers=extra_headers)
        self.end_headers()
        if not head_only:
            self.wfile.write(encoded)

    def _write_html(
        self,
        payload: str,
        status: int = 200,
        *,
        csp_nonce: str,
        robots_tag: str | None = None,
        head_only: bool = False,
    ) -> None:
        host = parse_request_host(self.headers)
        proto = parse_request_proto(self.headers)
        meta = build_site_meta(host, proto)
        encoded = payload.encode("utf-8")
        self.send_response(status)
        self._send_common_headers(
            "text/html; charset=utf-8",
            len(encoded),
            "no-store",
            csp_nonce=csp_nonce,
            extra_headers={"X-Robots-Tag": robots_tag or str(meta["robots"])},
        )
        self.end_headers()
        if not head_only:
            self.wfile.write(encoded)

    def _write_empty(self, status: int = 204, *, extra_headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self._send_common_headers("text/plain; charset=utf-8", 0, "no-store", extra_headers=extra_headers)
        self.end_headers()

    def _write_redirect(self, location: str, *, set_cookie: str | None = None) -> None:
        self.send_response(302)
        self.send_header("Location", location)
        if set_cookie:
            self.send_header("Set-Cookie", set_cookie)
        self._send_common_headers("text/plain; charset=utf-8", 0, "no-store")
        self.end_headers()

    def _write_method_not_allowed(self, path: str, *, head_only: bool = False) -> None:
        allow = "GET, HEAD, OPTIONS"
        if path in {"/auth/login", "/api/admin/rebuild"}:
            allow = "POST, OPTIONS"
        if path.startswith("/api/") or path.startswith("/auth/"):
            self._write_json({"error": "method not allowed"}, status=405, head_only=head_only, extra_headers={"Allow": allow})
            return
        self._write_empty(status=405, extra_headers={"Allow": allow})

    def log_message(self, format: str, *args) -> None:
        safe_args = list(args)
        if safe_args and isinstance(safe_args[0], str):
            safe_args[0] = redact_requestline_tokens(safe_args[0])
        super().log_message(format, *safe_args)

    def _handle_get_like(self, *, head_only: bool) -> bool:
        parsed = parse.urlparse(self.path)
        host = parse_request_host(self.headers)
        proto = parse_request_proto(self.headers)
        client_ip = get_request_client_ip(self)
        query_params = parse.parse_qs(parsed.query)

        if parsed.path == "/health":
            # Minimal public health payload. Internal telemetry (concern counts,
            # atlas_status, schema_version, cache timestamps) is not exposed on
            # the unauthenticated /health route to avoid leaking deployment state.
            self._write_json({"status": "ok"}, head_only=head_only)
            return True

        if parsed.path == "/robots.txt":
            self._write_text(build_robots_txt(host), "text/plain; charset=utf-8", head_only=head_only)
            return True

        if parsed.path == "/llms.txt":
            self._write_text(build_llms_txt(host), "text/plain; charset=utf-8", head_only=head_only)
            return True

        if parsed.path in ("/.well-known/security.txt", "/security.txt"):
            self._write_text(build_security_txt(host), "text/plain; charset=utf-8", head_only=head_only)
            return True

        if parsed.path == "/sitemap.xml":
            self._write_text(build_sitemap_xml(host, proto), "application/xml; charset=utf-8", head_only=head_only)
            return True

        # --- /demo — public client-facing surface (summer launch) -----------
        # No auth. Everything under /demo/* and /demo/api/* is explicitly
        # public. Keep internal telemetry out of this tree.
        if parsed.path in ("/demo", "/demo/"):
            self._write_text(
                (ROOT / "demo" / "index.html").read_text(encoding="utf-8"),
                "text/html; charset=utf-8",
                cache_control="no-store",
                head_only=head_only,
            )
            return True
        if parsed.path == "/demo/demo.css":
            self._write_text(
                (ROOT / "demo" / "demo.css").read_text(encoding="utf-8"),
                "text/css; charset=utf-8",
                cache_control="no-store",
                head_only=head_only,
            )
            return True
        if parsed.path == "/demo/demo.js":
            self._write_text(
                (ROOT / "demo" / "demo.js").read_text(encoding="utf-8"),
                "application/javascript; charset=utf-8",
                cache_control="no-store",
                head_only=head_only,
            )
            return True
        if parsed.path == "/demo/api/coverage":
            data = get_demo_entities()
            count = int(data.get("count", len(data.get("entities", []))))
            self._write_json(
                {
                    "count": count,
                    "generated_at": data.get("generated_at"),
                    "sources_breakdown": data.get("sources_breakdown", {}),
                    "note": (
                        "Verified entities. Completeness-gated: AUM + verified contact "
                        "+ transaction history + provenance envelope. Ratified by Prem + Kong."
                    ),
                },
                head_only=head_only,
            )
            return True

        if parsed.path == "/demo/health":
            data = get_demo_entities()
            count = int(data.get("count", len(data.get("entities", []))))
            self._write_json(
                {
                    "status": "ok",
                    "entities": count,
                    "last_refresh": iso_now() if not data.get("generated_at") else data["generated_at"],
                },
                head_only=head_only,
            )
            return True

        if parsed.path == "/demo/api/presets":
            try:
                presets_path = ROOT / "demo" / "seed" / "queries.json"
                presets_data = json.loads(presets_path.read_text(encoding="utf-8"))
            except Exception:
                presets_data = {"presets": []}
            self._write_json(presets_data, head_only=head_only)
            return True

        if parsed.path == "/demo/api/ask/stream":
            if head_only:
                self._write_json({}, head_only=True)
                return True
            q_param = query_params.get("q", [""])[0].strip()[:1000]
            if not q_param:
                self._write_json({"error": "missing q"}, status=400)
                return True
            allowed, retry_after = check_rate_limit("demo_ask", client_ip, 30, window_seconds=60)
            if not allowed:
                self._write_json({"error": "rate limit", "retry_after": retry_after}, status=429)
                return True
            allowed_hourly, _ = check_rate_limit("demo_ask_hourly", client_ip, 200, window_seconds=3600)
            if not allowed_hourly:
                self._write_json({"error": "hourly limit reached", "retry_after": 3600}, status=429)
                return True
            # parse optional conversation history (last N turns for follow-up context)
            history: list[dict] = []
            history_raw = query_params.get("history", [""])[0].strip()
            if history_raw:
                try:
                    parsed_h = json.loads(history_raw)
                    if isinstance(parsed_h, list):
                        history = parsed_h
                except Exception:
                    pass
            entities = get_demo_entities()
            # SSE: write headers directly — no Content-Length
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store")
            self.send_header("X-Accel-Buffering", "no")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            t0 = time.monotonic()
            try:
                for chunk in stream_gemini_demo(q_param, entities, history=history):
                    self.wfile.write(chunk)
                    self.wfile.flush()
            except Exception:
                pass
            log_demo_ask(client_ip, q_param, "stream", int((time.monotonic() - t0) * 1000))
            return True

        # --- end /demo -------------------------------------------------------

        if parsed.path == "/app.js":
            self._write_text(
                (ROOT / "app.js").read_text(encoding="utf-8"),
                "application/javascript; charset=utf-8",
                cache_control="no-store",
                head_only=head_only,
            )
            return True

        if parsed.path == "/styles.css":
            self._write_text(
                (ROOT / "styles.css").read_text(encoding="utf-8"),
                "text/css; charset=utf-8",
                cache_control="no-store",
                head_only=head_only,
            )
            return True

        if parsed.path in ("/landing", "/landing.html"):
            csp_nonce = secrets.token_urlsafe(18)
            self._write_html(render_landing_html(host, proto, csp_nonce), csp_nonce=csp_nonce, head_only=head_only)
            return True

        if parsed.path == "/msci.js":
            self._write_text(
                (ROOT / "msci.js").read_text(encoding="utf-8"),
                "application/javascript; charset=utf-8",
                cache_control="no-store",
                head_only=head_only,
            )
            return True

        if parsed.path == "/admin.js":
            self._write_text(
                (ROOT / "admin.js").read_text(encoding="utf-8"),
                "application/javascript; charset=utf-8",
                cache_control="no-store",
                head_only=head_only,
            )
            return True

        if parsed.path == "/auth/logout":
            clear_session(self)
            self._write_redirect("/login", set_cookie=self._session_cookie_value("", max_age=0))
            return True

        if parsed.path == "/login":
            if request_is_authenticated(self):
                self._write_redirect(sanitize_next_path(query_params.get("next", ["/"])[0]))
                return True
            csp_nonce = secrets.token_urlsafe(18)
            error = None if login_configured() else "Preview auth is not configured on this runtime."
            self._write_html(
                render_login_html(host, proto, csp_nonce, error=error, next_path=sanitize_next_path(query_params.get("next", ["/"])[0])),
                status=200 if login_configured() else 503,
                csp_nonce=csp_nonce,
                robots_tag="noindex,nofollow,noarchive",
                head_only=head_only,
            )
            return True

        if parsed.path in ("/api/dashboard", "/api/dashboard/v1"):
            if not request_is_authenticated(self):
                self._write_json({"error": "authentication required"}, status=401, head_only=head_only)
                return True
            self._write_json(get_dashboard_payload(), head_only=head_only)
            return True

        if parsed.path in ("/api/research", "/api/research/v1"):
            if not request_is_authenticated(self):
                self._write_json({"error": "authentication required"}, status=401, head_only=head_only)
                return True
            allowed, retry_after = check_rate_limit("research", client_ip, RESEARCH_RATE_LIMIT_PER_MINUTE)
            if not allowed:
                self._write_json(
                    {"error": "research rate limit exceeded", "retry_after": retry_after},
                    status=429,
                    head_only=head_only,
                    extra_headers={"Retry-After": str(retry_after)},
                )
                return True
            query_text = parse.parse_qs(parsed.query).get("q", [""])[0].strip()
            if not query_text:
                self._write_json({"error": "missing query"}, status=400, head_only=head_only)
                return True
            self._write_json(build_research_payload(query_text), head_only=head_only)
            return True

        if parsed.path in ("/api/msci/workbench", "/api/msci/workbench/v1"):
            if not request_is_authenticated(self):
                self._write_json({"error": "authentication required"}, status=401, head_only=head_only)
                return True
            self._write_json(get_dashboard_payload()["msci_workbench"], head_only=head_only)
            return True

        if parsed.path in ("/api/admin", "/api/admin/v1"):
            if not request_is_authenticated(self):
                self._write_json({"error": "authentication required"}, status=401, head_only=head_only)
                return True
            self._write_json(build_admin_payload(), head_only=head_only)
            return True

        if parsed.path in ("/api/connectors", "/api/connectors/v1"):
            if not request_is_authenticated(self):
                self._write_json({"error": "authentication required"}, status=401, head_only=head_only)
                return True
            self._write_json(
                {
                    "schema_version": "swfi.connectors.v1",
                    "generated_at": iso_now(),
                    "connectors": get_live_external_api_matrix(),
                },
                head_only=head_only,
            )
            return True

        if parsed.path == "/api/msci/export/accounts.csv":
            auth_mode = private_export_auth_mode(self, parsed)
            if not auth_mode:
                append_export_audit_event(self, parsed.path, "denied", None)
                self._write_json({"error": "access denied"}, status=403, head_only=head_only)
                return True
            allowed, retry_after = check_rate_limit("private_export", client_ip, EXPORT_RATE_LIMIT_PER_MINUTE)
            if not allowed:
                append_export_audit_event(self, parsed.path, "rate_limited", auth_mode)
                self._write_json(
                    {"error": "export rate limit exceeded", "retry_after": retry_after},
                    status=429,
                    head_only=head_only,
                    extra_headers={"Retry-After": str(retry_after)},
                )
                return True
            append_export_audit_event(self, parsed.path, "ok", auth_mode)
            self._write_csv(build_accounts_csv(), "swfi-msci-accounts.csv", head_only=head_only)
            return True

        if parsed.path == "/api/msci/export/people.csv":
            auth_mode = private_export_auth_mode(self, parsed)
            if not auth_mode:
                append_export_audit_event(self, parsed.path, "denied", None)
                self._write_json({"error": "access denied"}, status=403, head_only=head_only)
                return True
            allowed, retry_after = check_rate_limit("private_export", client_ip, EXPORT_RATE_LIMIT_PER_MINUTE)
            if not allowed:
                append_export_audit_event(self, parsed.path, "rate_limited", auth_mode)
                self._write_json(
                    {"error": "export rate limit exceeded", "retry_after": retry_after},
                    status=429,
                    head_only=head_only,
                    extra_headers={"Retry-After": str(retry_after)},
                )
                return True
            append_export_audit_event(self, parsed.path, "ok", auth_mode)
            self._write_csv(build_people_csv(), "swfi-msci-people.csv", head_only=head_only)
            return True

        if parsed.path == "/api/msci/export/people-review.csv":
            auth_mode = private_export_auth_mode(self, parsed)
            if not auth_mode:
                append_export_audit_event(self, parsed.path, "denied", None)
                self._write_json({"error": "access denied"}, status=403, head_only=head_only)
                return True
            allowed, retry_after = check_rate_limit("private_export", client_ip, EXPORT_RATE_LIMIT_PER_MINUTE)
            if not allowed:
                append_export_audit_event(self, parsed.path, "rate_limited", auth_mode)
                self._write_json(
                    {"error": "export rate limit exceeded", "retry_after": retry_after},
                    status=429,
                    head_only=head_only,
                    extra_headers={"Retry-After": str(retry_after)},
                )
                return True
            append_export_audit_event(self, parsed.path, "ok", auth_mode)
            self._write_csv(build_people_review_csv(), "swfi-msci-people-review.csv", head_only=head_only)
            return True

        if parsed.path == "/api/msci/export/people-template.csv":
            self._write_csv(build_people_template_csv(), "swfi-msci-people-template.csv", head_only=head_only)
            return True

        if parsed.path == "/api/reports/msci-analytics.csv":
            auth_mode = authenticated_request_mode(self)
            if not auth_mode:
                append_export_audit_event(self, parsed.path, "denied", None)
                self._write_json({"error": "authentication required"}, status=401, head_only=head_only)
                return True
            allowed, retry_after = check_rate_limit("report_export", client_ip, EXPORT_RATE_LIMIT_PER_MINUTE)
            if not allowed:
                append_export_audit_event(self, parsed.path, "rate_limited", auth_mode)
                self._write_json(
                    {"error": "report export rate limit exceeded", "retry_after": retry_after},
                    status=429,
                    head_only=head_only,
                    extra_headers={"Retry-After": str(retry_after)},
                )
                return True
            append_export_audit_event(self, parsed.path, "ok", auth_mode)
            self._write_csv(build_msci_analytics_csv(), "swfi-msci-analytics.csv", head_only=head_only)
            return True

        if parsed.path == "/api/reports/external-api-matrix.csv":
            auth_mode = authenticated_request_mode(self)
            if not auth_mode:
                append_export_audit_event(self, parsed.path, "denied", None)
                self._write_json({"error": "authentication required"}, status=401, head_only=head_only)
                return True
            allowed, retry_after = check_rate_limit("report_export", client_ip, EXPORT_RATE_LIMIT_PER_MINUTE)
            if not allowed:
                append_export_audit_event(self, parsed.path, "rate_limited", auth_mode)
                self._write_json(
                    {"error": "report export rate limit exceeded", "retry_after": retry_after},
                    status=429,
                    head_only=head_only,
                    extra_headers={"Retry-After": str(retry_after)},
                )
                return True
            append_export_audit_event(self, parsed.path, "ok", auth_mode)
            self._write_csv(build_external_api_matrix_csv(), "swfi-external-api-matrix.csv", head_only=head_only)
            return True

        if parsed.path == "/api/reports/export-history.csv":
            auth_mode = authenticated_request_mode(self)
            if not auth_mode:
                append_export_audit_event(self, parsed.path, "denied", None)
                self._write_json({"error": "authentication required"}, status=401, head_only=head_only)
                return True
            allowed, retry_after = check_rate_limit("report_export", client_ip, EXPORT_RATE_LIMIT_PER_MINUTE)
            if not allowed:
                append_export_audit_event(self, parsed.path, "rate_limited", auth_mode)
                self._write_json(
                    {"error": "report export rate limit exceeded", "retry_after": retry_after},
                    status=429,
                    head_only=head_only,
                    extra_headers={"Retry-After": str(retry_after)},
                )
                return True
            append_export_audit_event(self, parsed.path, "ok", auth_mode)
            self._write_csv(build_export_history_csv(), "swfi-export-history.csv", head_only=head_only)
            return True

        if parsed.path == "/api/reports/phase1-summary.md":
            auth_mode = authenticated_request_mode(self)
            if not auth_mode:
                append_export_audit_event(self, parsed.path, "denied", None)
                self._write_json({"error": "authentication required"}, status=401, head_only=head_only)
                return True
            allowed, retry_after = check_rate_limit("report_export", client_ip, EXPORT_RATE_LIMIT_PER_MINUTE)
            if not allowed:
                append_export_audit_event(self, parsed.path, "rate_limited", auth_mode)
                self._write_json(
                    {"error": "report export rate limit exceeded", "retry_after": retry_after},
                    status=429,
                    head_only=head_only,
                    extra_headers={"Retry-After": str(retry_after)},
                )
                return True
            append_export_audit_event(self, parsed.path, "ok", auth_mode)
            self._write_text(
                build_phase1_summary_md(),
                "text/markdown; charset=utf-8",
                cache_control="no-store",
                head_only=head_only,
                extra_headers={"Content-Disposition": 'attachment; filename="swfi-phase1-summary.md"'},
            )
            return True

        if parsed.path == "/api/reports/ai-governance.md":
            auth_mode = authenticated_request_mode(self)
            if not auth_mode:
                append_export_audit_event(self, parsed.path, "denied", None)
                self._write_json({"error": "authentication required"}, status=401, head_only=head_only)
                return True
            allowed, retry_after = check_rate_limit("report_export", client_ip, EXPORT_RATE_LIMIT_PER_MINUTE)
            if not allowed:
                append_export_audit_event(self, parsed.path, "rate_limited", auth_mode)
                self._write_json(
                    {"error": "report export rate limit exceeded", "retry_after": retry_after},
                    status=429,
                    head_only=head_only,
                    extra_headers={"Retry-After": str(retry_after)},
                )
                return True
            append_export_audit_event(self, parsed.path, "ok", auth_mode)
            self._write_text(
                build_ai_governance_md(),
                "text/markdown; charset=utf-8",
                cache_control="no-store",
                head_only=head_only,
                extra_headers={"Content-Disposition": 'attachment; filename="swfi-ai-governance.md"'},
            )
            return True

        if parsed.path == "/api/reports/nugget-schema.json":
            auth_mode = authenticated_request_mode(self)
            if not auth_mode:
                append_export_audit_event(self, parsed.path, "denied", None)
                self._write_json({"error": "authentication required"}, status=401, head_only=head_only)
                return True
            allowed, retry_after = check_rate_limit("report_export", client_ip, EXPORT_RATE_LIMIT_PER_MINUTE)
            if not allowed:
                append_export_audit_event(self, parsed.path, "rate_limited", auth_mode)
                self._write_json(
                    {"error": "report export rate limit exceeded", "retry_after": retry_after},
                    status=429,
                    head_only=head_only,
                    extra_headers={"Retry-After": str(retry_after)},
                )
                return True
            append_export_audit_event(self, parsed.path, "ok", auth_mode)
            self._write_text(
                build_nugget_schema_json(),
                "application/schema+json; charset=utf-8",
                cache_control="no-store",
                head_only=head_only,
                extra_headers={"Content-Disposition": 'attachment; filename="swfi-nugget-schema-v1.json"'},
            )
            return True

        if parsed.path == "/api/reports/prompt-registry.yaml":
            auth_mode = authenticated_request_mode(self)
            if not auth_mode:
                append_export_audit_event(self, parsed.path, "denied", None)
                self._write_json({"error": "authentication required"}, status=401, head_only=head_only)
                return True
            allowed, retry_after = check_rate_limit("report_export", client_ip, EXPORT_RATE_LIMIT_PER_MINUTE)
            if not allowed:
                append_export_audit_event(self, parsed.path, "rate_limited", auth_mode)
                self._write_json(
                    {"error": "report export rate limit exceeded", "retry_after": retry_after},
                    status=429,
                    head_only=head_only,
                    extra_headers={"Retry-After": str(retry_after)},
                )
                return True
            append_export_audit_event(self, parsed.path, "ok", auth_mode)
            self._write_text(
                build_prompt_registry_yaml(),
                "application/yaml; charset=utf-8",
                cache_control="no-store",
                head_only=head_only,
                extra_headers={"Content-Disposition": 'attachment; filename="swfi-prompt-registry.yaml"'},
            )
            return True

        path = self.translate_path(parsed.path)
        if parsed.path in ("/msci", "/msci.html"):
            if not request_is_authenticated(self):
                self._write_redirect(f"/login?next={parse.quote('/msci', safe='/')}")
                return True
            csp_nonce = secrets.token_urlsafe(18)
            self._write_html(render_msci_html(host, proto, csp_nonce), csp_nonce=csp_nonce, head_only=head_only)
            return True

        if parsed.path in ("/admin", "/admin.html"):
            if not request_is_authenticated(self):
                self._write_redirect(f"/login?next={parse.quote('/admin', safe='/')}")
                return True
            csp_nonce = secrets.token_urlsafe(18)
            self._write_html(render_admin_html(host, proto, csp_nonce), csp_nonce=csp_nonce, head_only=head_only)
            return True

        if parsed.path in ("/dashboard", "/dashboard/", PREVIEW_ROUTE, f"{PREVIEW_ROUTE}/"):
            if not request_is_authenticated(self):
                next_path = sanitize_next_path(parsed.path or "/")
                self._write_redirect(f"/login?next={parse.quote(next_path, safe='/')}")
                return True
            csp_nonce = secrets.token_urlsafe(18)
            self._write_html(render_index_html(host, proto, csp_nonce), csp_nonce=csp_nonce, head_only=head_only)
            return True

        if parsed.path in ("/", "/index.html"):
            csp_nonce = secrets.token_urlsafe(18)
            if is_public_host(host):
                self._write_html(render_landing_html(host, proto, csp_nonce), csp_nonce=csp_nonce, head_only=head_only)
                return True
            if not request_is_authenticated(self):
                next_path = sanitize_next_path(parsed.path or "/")
                self._write_redirect(f"/login?next={parse.quote(next_path, safe='/')}")
                return True
            self._write_html(render_index_html(host, proto, csp_nonce), csp_nonce=csp_nonce, head_only=head_only)
            return True

        if parsed.path != "/" and not Path(path).exists() and not parsed.path.startswith("/api/"):
            if not request_is_authenticated(self):
                self._write_redirect(f"/login?next={parse.quote(sanitize_next_path(parsed.path), safe='/')}")
                return True
            csp_nonce = secrets.token_urlsafe(18)
            self._write_html(render_index_html(host, proto, csp_nonce), csp_nonce=csp_nonce, head_only=head_only)
            return True

        if parsed.path.startswith("/api/"):
            self._write_json({"error": "not found"}, status=404, head_only=head_only)
            return True

        return False

    def do_GET(self) -> None:
        if self._handle_get_like(head_only=False):
            return
        super().do_GET()

    def do_HEAD(self) -> None:
        if self._handle_get_like(head_only=True):
            return
        super().do_HEAD()

    def do_OPTIONS(self) -> None:
        parsed = parse.urlparse(self.path)
        allow = "GET, HEAD, OPTIONS"
        if parsed.path in {"/auth/login", "/api/admin/rebuild"}:
            allow = "POST, OPTIONS"
        self._write_empty(status=204, extra_headers={"Allow": allow})

    def do_POST(self) -> None:
        parsed = parse.urlparse(self.path)
        client_ip = get_request_client_ip(self)
        host = parse_request_host(self.headers)
        proto = parse_request_proto(self.headers)

        # --- /demo/api/ask — public AI search endpoint ----------------------
        # Scaffold only. CC: wire this to Gemini 2.5 Pro (GOOGLE_API_KEY in
        # keychain). Inline the curated 500-entity packet from demo/seed/
        # into the system prompt. Rate-limit per client_ip. Return shape:
        #   { "text": "...", "sources": [ { "label": "...", "url": "..." } ] }
        if parsed.path == "/demo/api/ask":
            allowed, retry_after = check_rate_limit("demo_ask", client_ip, 30, window_seconds=60)
            if not allowed:
                self.send_response(429)
                payload = json.dumps({"error": "rate limit", "retry_after": retry_after}).encode("utf-8")
                self._send_common_headers("application/json", len(payload), "no-store", extra_headers={"Retry-After": str(retry_after)})
                self.end_headers()
                self.wfile.write(payload)
                return
            # soft hourly cap: 200 requests/hour per IP (on top of 30/min)
            allowed_hourly, _ = check_rate_limit("demo_ask_hourly", client_ip, 200, window_seconds=3600)
            if not allowed_hourly:
                self._write_json({"error": "hourly limit reached", "retry_after": 3600}, status=429)
                return
            # parse JSON body
            try:
                length = int(self.headers.get("Content-Length", "0") or "0")
                raw_body = self.rfile.read(length) if length else b"{}"
                body_data = json.loads(raw_body.decode("utf-8", errors="replace"))
                query = str(body_data.get("q", "")).strip()[:1000]
            except Exception:
                self._write_json({"error": "invalid request body"}, status=400)
                return
            if not query:
                self._write_json({"error": "missing q"}, status=400)
                return
            entities = get_demo_entities()
            t0 = time.monotonic()
            result = call_gemini_for_demo(query, entities)
            latency_ms = int((time.monotonic() - t0) * 1000)
            model_used = result.pop("_model", "unknown")
            result.pop("_last_err", None)  # never leak internal error details to client
            log_demo_ask(client_ip, query, model_used, latency_ms)
            if "status" not in result:
                result["status"] = "ok"
            self._write_json(result, status=200)
            return
        # --- end /demo/api/ask ----------------------------------------------

        if parsed.path == "/api/admin/rebuild":
            auth_mode = authenticated_request_mode(self)
            if not auth_mode:
                append_export_audit_event(self, parsed.path, "denied", None)
                self._write_json({"error": "authentication required"}, status=401)
                return
            allowed, retry_after = check_rate_limit("admin_rebuild", client_ip, 6)
            if not allowed:
                append_export_audit_event(self, parsed.path, "rate_limited", auth_mode)
                self._write_json(
                    {"error": "rebuild rate limit exceeded", "retry_after": retry_after},
                    status=429,
                    extra_headers={"Retry-After": str(retry_after)},
                )
                return
            clear_runtime_caches()

            def warm_runtime_packets() -> None:
                try:
                    get_dashboard_payload()
                    build_admin_payload()
                    get_live_external_api_matrix()
                except Exception:
                    return

            threading.Thread(target=warm_runtime_packets, daemon=True).start()
            append_export_audit_event(self, parsed.path, "ok", auth_mode)
            self._write_json(
                {
                    "status": "ok",
                    "message": "Runtime caches cleared. Packet warm-up has started in the background.",
                    "dashboard_generated_at": iso_now(),
                    "admin_generated_at": iso_now(),
                },
                status=200,
            )
            return

        if parsed.path != "/auth/login":
            self._write_json({"error": "method not allowed"}, status=405)
            return

        allowed, retry_after = check_rate_limit("login", client_ip, LOGIN_RATE_LIMIT_PER_15_MIN, window_seconds=900)
        if not allowed:
            self.send_response(429)
            payload = json.dumps({"error": "login rate limit exceeded", "retry_after": retry_after}).encode("utf-8")
            self._send_common_headers("application/json", len(payload), "no-store", extra_headers={"Retry-After": str(retry_after)})
            self.end_headers()
            self.wfile.write(payload)
            return

        length = int(self.headers.get("Content-Length", "0") or "0")
        raw_body = self.rfile.read(length).decode("utf-8", errors="replace")
        form = parse.parse_qs(raw_body, keep_blank_values=True)
        username = str(form.get("username", [""])[0]).strip()
        password = str(form.get("password", [""])[0])
        next_path = sanitize_next_path(form.get("next", ["/"])[0])

        if not login_configured():
            csp_nonce = secrets.token_urlsafe(18)
            self._write_html(
                render_login_html(host, proto, csp_nonce, error="Preview auth is not configured on this runtime.", next_path=next_path),
                status=503,
                csp_nonce=csp_nonce,
                robots_tag="noindex,nofollow,noarchive",
            )
            return

        username_ok = secrets.compare_digest(username, SWFI_PREVIEW_AUTH_USERNAME)
        password_ok = secrets.compare_digest(password, SWFI_PREVIEW_AUTH_PASSWORD)
        if not (username_ok and password_ok):
            csp_nonce = secrets.token_urlsafe(18)
            self._write_html(
                render_login_html(host, proto, csp_nonce, error="Incorrect username or password.", next_path=next_path),
                status=401,
                csp_nonce=csp_nonce,
                robots_tag="noindex,nofollow,noarchive",
            )
            return

        token = create_session(username)
        self._write_redirect(next_path, set_cookie=self._session_cookie_value(token, max_age=PREVIEW_SESSION_TTL_SECONDS))

    def do_PUT(self) -> None:
        self._write_method_not_allowed(parse.urlparse(self.path).path)

    def do_DELETE(self) -> None:
        self._write_method_not_allowed(parse.urlparse(self.path).path)

    def do_PATCH(self) -> None:
        self._write_method_not_allowed(parse.urlparse(self.path).path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the SWFI terminal preview")
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
