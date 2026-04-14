#!/usr/bin/env python3

from __future__ import annotations

import argparse
import http.server
import json
import os
import subprocess
import threading
import time
from pathlib import Path
from urllib import error, parse, request


ROOT = Path(__file__).resolve().parent
SEC_USER_AGENT = os.environ.get("SEC_USER_AGENT", "SWFI-Demo research@example.com")
DASHBOARD_TTL_SECONDS = int(os.environ.get("DASHBOARD_TTL_SECONDS", "900"))
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
SPONSOR_TICKERS = ("BX", "KKR", "APO", "BN", "BLK")
SPONSOR_NAMES = {
    "BX": "Blackstone",
    "KKR": "KKR",
    "APO": "Apollo",
    "BN": "Brookfield",
    "BLK": "BlackRock",
}
COUNTRY_CODES = {
    "norway": "NO",
    "china": "CN",
    "united states": "US",
    "us": "US",
    "usa": "US",
    "saudi": "SA",
    "saudi arabia": "SA",
    "singapore": "SG",
    "uae": "AE",
    "united arab emirates": "AE",
}

_cache_lock = threading.Lock()
_dashboard_cache: dict[str, object] = {"timestamp": 0.0, "payload": None}
_company_tickers_cache: dict[str, object] = {"timestamp": 0.0, "payload": None}
_gdelt_backoff_until = 0.0
RESEARCH_SYSTEM_PROMPT = """
You are SWFI Research Copilot inside a demo institutional capital workspace.
You are only a research assistant.

Allowed scope:
- sovereign wealth funds
- public pensions
- reserve managers
- private capital platforms
- capital flows
- mandate and strategy movement
- decision-maker and profile research
- SEC filings, macro context, and public-source market intelligence

Rules:
- Use only the provided source packet.
- Do not invent facts or imply hidden access.
- If the evidence is thin, say that directly.
- Stay concise, analytical, and professional.
- Answer in 2 to 4 short paragraphs or bullets.
- Treat this as a read-only institutional research tool, not a trading or execution agent.
- Do not answer unrelated lifestyle, entertainment, coding, or creative requests.
- If asked to go beyond research, reply that this demo assistant is limited to institutional capital research.
""".strip()

NON_RESEARCH_HINTS = (
    "joke",
    "poem",
    "story",
    "recipe",
    "dinner",
    "movie",
    "music",
    "song",
    "lyrics",
    "travel",
    "vacation",
    "weather",
    "translate",
    "translation",
    "birthday",
    "relationship",
    "horoscope",
    "game",
    "fantasy",
    "code this",
    "debug this",
    "write javascript",
    "write python",
    "html",
    "css",
)

ACTION_REQUEST_HINTS = (
    "send email",
    "email this",
    "text this",
    "whatsapp",
    "book a",
    "schedule",
    "call them",
    "contact them",
    "place a trade",
    "buy this",
    "sell this",
    "make the trade",
    "execute",
    "submit",
    "log in",
    "login",
)


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


def fetch_json(url: str, *, headers: dict[str, str] | None = None, payload: object | None = None, timeout: int = 20):
    data = None
    final_headers = {"User-Agent": SEC_USER_AGENT, **(headers or {})}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        final_headers.setdefault("Content-Type", "application/json")

    req = request.Request(url, data=data, headers=final_headers)
    with request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def fetch_world_bank_json(url: str):
    result = subprocess.run(
        ["curl", "-4", "-m", "15", "-s", url],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError("world bank request failed")
    return json.loads(result.stdout)


def compact_money(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    absolute = abs(float(value))
    if absolute >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.1f}T"
    if absolute >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if absolute >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${value:,.0f}"


def get_company_tickers():
    now = time.time()
    with _cache_lock:
        if _company_tickers_cache["payload"] and now - float(_company_tickers_cache["timestamp"]) < 86400:
            return _company_tickers_cache["payload"]

    data = fetch_json(
        "https://www.sec.gov/files/company_tickers.json",
        headers={"User-Agent": SEC_USER_AGENT},
    )

    with _cache_lock:
        _company_tickers_cache["timestamp"] = now
        _company_tickers_cache["payload"] = data
    return data


def fetch_sec_filings(tickers: tuple[str, ...] = SPONSOR_TICKERS):
    try:
        company_index = get_company_tickers()
        lookup = {entry["ticker"].upper(): entry for entry in company_index.values()}
        filings = []

        for ticker in tickers:
            company = lookup.get(ticker.upper())
            if not company:
                continue
            cik = str(company["cik_str"]).zfill(10)
            payload = fetch_json(
                f"https://data.sec.gov/submissions/CIK{cik}.json",
                headers={"User-Agent": SEC_USER_AGENT},
            )
            recent = payload.get("filings", {}).get("recent", {})
            if not recent or not recent.get("form"):
                continue

            accession = recent["accessionNumber"][0].replace("-", "")
            filing_url = (
                f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{recent['primaryDocument'][0]}"
            )
            filings.append(
                {
                    "ticker": ticker,
                    "name": payload.get("name", company["title"]),
                    "form": recent["form"][0],
                    "date": recent["filingDate"][0],
                    "url": filing_url,
                }
            )

        return {
            "status": "ok",
            "note": f"{len(filings)} live SEC filing snapshots",
            "items": filings,
        }
    except Exception as exc:  # pragma: no cover - demo fallback path
        return {"status": "fallback", "note": f"SEC unavailable: {exc}", "items": []}


def fetch_world_bank_macro(codes: tuple[str, ...] = ("NO", "CN", "US", "SA", "SG", "AE")):
    try:
        joined_codes = ";".join(codes)
        url = (
            f"https://api.worldbank.org/v2/country/{joined_codes}/indicator/NY.GDP.MKTP.CD"
            "?format=json&per_page=20&mrv=1"
        )
        payload = fetch_world_bank_json(url)
        rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        items = [
            {
                "country": row["country"]["value"],
                "country_code": row["countryiso3code"],
                "label": "GDP (current US$)",
                "date": row["date"],
                "value": row["value"],
                "display_value": compact_money(row["value"]),
            }
            for row in rows
            if row.get("value") is not None
        ]
        return {
            "status": "ok",
            "note": f"{len(items)} World Bank country snapshots",
            "items": items,
        }
    except Exception as exc:  # pragma: no cover - demo fallback path
        return {"status": "fallback", "note": f"World Bank unavailable: {exc}", "items": []}


def fetch_usaspending_matches(queries: tuple[str, ...] = ("Blackstone", "KKR", "Apollo", "Brookfield", "BlackRock")):
    items = []
    errors = 0

    for term in queries:
        try:
            payload = fetch_json(
                "https://api.usaspending.gov/api/v2/autocomplete/recipient/",
                payload={"search_text": term},
            )
            results = payload.get("results", [])
            items.append(
                {
                    "query": term,
                    "count": payload.get("count", 0),
                    "top_result": results[0]["recipient_name"] if results else "No close match",
                }
            )
        except Exception:
            errors += 1

    status = "ok" if errors == 0 else "fallback"
    note = f"{len(items)} USAspending recipient lookups"
    if errors:
        note = f"{note}, {errors} missed"
    return {"status": status, "note": note, "items": items}


def fetch_gdelt_feed(query_text: str, max_records: int = 6):
    global _gdelt_backoff_until

    if time.time() < _gdelt_backoff_until:
        return {"status": "rate_limited", "note": "GDELT backoff active", "items": []}

    params = {
        "query": query_text,
        "mode": "ArtList",
        "maxrecords": str(max_records),
        "sort": "DateDesc",
        "format": "json",
    }
    url = f"https://api.gdeltproject.org/api/v2/doc/doc?{parse.urlencode(params)}"

    try:
        payload = fetch_json(url, headers={"User-Agent": "SWFI-Demo/0.1"}, timeout=6)
        articles = payload.get("articles", [])
        items = []
        for article in articles:
            items.append(
                {
                    "state": "Live",
                    "title": article.get("title", "Untitled signal"),
                    "summary": article.get("seendate", "Fresh public-source signal"),
                    "date": article.get("seendate", "Live"),
                    "url": article.get("url"),
                    "sources": [article.get("domain", "GDELT"), "GDELT"],
                }
            )
        return {"status": "ok", "note": f"{len(items)} live GDELT signals", "items": items}
    except error.HTTPError as exc:
        if exc.code == 429:
            _gdelt_backoff_until = time.time() + 900
            return {"status": "rate_limited", "note": "GDELT rate limited", "items": []}
        return {"status": "fallback", "note": f"GDELT HTTP {exc.code}", "items": []}
    except Exception as exc:  # pragma: no cover - demo fallback path
        return {"status": "fallback", "note": f"GDELT unavailable: {exc}", "items": []}


def call_gemini_research(query_text: str, source_packet: dict[str, object]) -> str | None:
    if not GEMINI_API_KEY:
        return None

    payload = {
        "system_instruction": {
            "parts": [
                {
                    "text": RESEARCH_SYSTEM_PROMPT,
                }
            ]
        },
        "contents": [
            {
                "parts": [
                    {
                        "text": json.dumps(
                            {
                                "user_query": query_text,
                                "source_packet": source_packet,
                                "task": "Answer the query as a research assistant using only this evidence packet.",
                            }
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 320,
        },
    }

    try:
        response = fetch_json(
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
            headers={"x-goog-api-key": GEMINI_API_KEY},
            payload=payload,
            timeout=20,
        )
        candidates = response.get("candidates", [])
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        text_parts = [part.get("text", "") for part in parts if part.get("text")]
        final_text = "\n".join(text_parts).strip()
        return final_text or None
    except Exception:
        return None


def get_research_guardrail_message(query_text: str) -> str | None:
    lowered = query_text.lower().strip()
    if not lowered:
        return "Ask about an allocator, manager, filing, macro context, or mandate signal."

    if any(phrase in lowered for phrase in ACTION_REQUEST_HINTS):
        return (
            "This demo assistant is read-only. It can research institutional capital questions, "
            "but it will not log in, send messages, schedule meetings, or execute transactions."
        )

    if any(phrase in lowered for phrase in NON_RESEARCH_HINTS):
        return (
            "This demo assistant is limited to institutional capital research. "
            "Ask about allocators, managers, filings, macro context, or mandate movement."
        )

    return None


def build_fallback_feed(sec_items, macro_items, recipient_items):
    items = []

    for filing in sec_items[:3]:
        items.append(
            {
                "state": "Live",
                "title": f"{filing['ticker']} filed {filing['form']} on {filing['date']}",
                "summary": filing["name"],
                "date": filing["date"],
                "url": filing["url"],
                "sources": ["SEC", filing["ticker"]],
            }
        )

    for macro in macro_items[:2]:
        items.append(
            {
                "state": "Macro",
                "title": f"{macro['country']} GDP (current US$) at {macro['display_value']}",
                "summary": f"World Bank snapshot for {macro['date']}",
                "date": macro["date"],
                "url": None,
                "sources": ["World Bank", macro["country"]],
            }
        )

    for recipient in recipient_items[:2]:
        items.append(
            {
                "state": "Public",
                "title": f"{recipient['query']} returned {recipient['count']} USAspending recipient matches",
                "summary": f"Top match: {recipient['top_result']}",
                "date": "Live",
                "url": None,
                "sources": ["USAspending", recipient["query"]],
            }
        )

    return items[:6]


def build_dashboard_payload():
    sec_result = fetch_sec_filings()
    world_result = fetch_world_bank_macro()
    usa_result = fetch_usaspending_matches()
    gdelt_result = fetch_gdelt_feed(
        '"sovereign wealth fund" OR "public pension" OR Blackstone OR KKR OR Apollo OR Brookfield'
    )

    feed_items = gdelt_result["items"] if gdelt_result["items"] else build_fallback_feed(
        sec_result["items"],
        world_result["items"],
        usa_result["items"],
    )

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "statuses": [
            {"source": "SEC", "status": sec_result["status"], "note": sec_result["note"]},
            {"source": "World Bank", "status": world_result["status"], "note": world_result["note"]},
            {"source": "USAspending", "status": usa_result["status"], "note": usa_result["note"]},
            {"source": "GDELT", "status": gdelt_result["status"], "note": gdelt_result["note"]},
        ],
        "filings": sec_result["items"],
        "macro": world_result["items"],
        "recipients": usa_result["items"],
        "feed": feed_items,
    }


def get_dashboard_payload():
    now = time.time()
    with _cache_lock:
        cached = _dashboard_cache.get("payload")
        timestamp = float(_dashboard_cache.get("timestamp", 0.0))
        if cached and now - timestamp < DASHBOARD_TTL_SECONDS:
            return cached

    payload = build_dashboard_payload()

    with _cache_lock:
        _dashboard_cache["timestamp"] = now
        _dashboard_cache["payload"] = payload
    return payload


def get_cached_dashboard_payload():
    with _cache_lock:
        return _dashboard_cache.get("payload")


def mentioned_sponsors(query_text: str):
    lowered = query_text.lower()
    mapping = {
        "blackstone": "BX",
        "kkr": "KKR",
        "apollo": "APO",
        "brookfield": "BN",
        "blackrock": "BLK",
    }
    return tuple(ticker for name, ticker in mapping.items() if name in lowered)


def mentioned_countries(query_text: str):
    lowered = query_text.lower()
    seen = []
    for name, code in COUNTRY_CODES.items():
        if name in lowered and code not in seen:
            seen.append(code)
    return tuple(seen)


def build_research_payload(query_text: str):
    guardrail_message = get_research_guardrail_message(query_text)
    if guardrail_message:
        return {
            "query": query_text,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "answer": guardrail_message,
            "evidence": [],
            "assistant_mode": "research_only",
            "guardrail": "scope_limited",
            "model": None,
        }

    dashboard = get_cached_dashboard_payload() or {"filings": [], "macro": [], "recipients": []}
    sponsor_tickers = mentioned_sponsors(query_text)
    country_codes = mentioned_countries(query_text)
    lowered = query_text.lower()
    wants_filings = bool(sponsor_tickers) or "filing" in lowered or "sec" in lowered
    wants_macro = bool(country_codes) or any(keyword in lowered for keyword in ("macro", "gdp", "country", "sovereign"))
    wants_public = any(keyword in lowered for keyword in ("public", "government", "contract", "usaspending"))
    wants_gdelt = any(keyword in lowered for keyword in ("mandate", "strategy", "opportunity", "signal", "news", "headline"))

    sec_result = fetch_sec_filings(sponsor_tickers) if wants_filings and sponsor_tickers else {"items": dashboard["filings"][:3]}
    world_result = (
        fetch_world_bank_macro(country_codes) if wants_macro and country_codes else {"items": dashboard["macro"][:3] if wants_macro else []}
    )
    usa_result = (
        fetch_usaspending_matches(tuple(SPONSOR_NAMES[ticker] for ticker in sponsor_tickers))
        if wants_public and sponsor_tickers
        else {"items": dashboard["recipients"][:3] if wants_public else []}
    )
    gdelt_result = fetch_gdelt_feed(query_text, max_records=3) if wants_gdelt else {"status": "skipped", "items": []}

    summary_parts = []
    evidence = []

    if sec_result["items"]:
        filing_bits = []
        for filing in sec_result["items"][:3]:
            filing_bits.append(f"{filing['ticker']} filed {filing['form']} on {filing['date']}")
            evidence.append(
                {
                    "source": "SEC",
                    "label": f"{filing['ticker']} {filing['form']} {filing['date']}",
                    "url": filing["url"],
                }
            )
        summary_parts.append("SEC filing pulse: " + "; ".join(filing_bits) + ".")

    if world_result["items"]:
        macro_bits = []
        for macro in world_result["items"][:3]:
            macro_bits.append(f"{macro['country']} GDP ({macro['date']}) at {macro['display_value']}")
            evidence.append(
                {
                    "source": "World Bank",
                    "label": f"{macro['country']} GDP {macro['display_value']}",
                    "url": None,
                }
            )
        summary_parts.append("Macro context: " + "; ".join(macro_bits) + ".")

    if usa_result["items"]:
        public_bits = []
        for item in usa_result["items"][:2]:
            public_bits.append(f"{item['query']} returned {item['count']} recipient matches")
            evidence.append(
                {
                    "source": "USAspending",
                    "label": f"{item['query']} matches: {item['count']}",
                    "url": None,
                }
            )
        summary_parts.append("Public-sector footprint: " + "; ".join(public_bits) + ".")

    if gdelt_result["items"]:
        feed_bits = []
        for item in gdelt_result["items"][:2]:
            feed_bits.append(item["title"])
            evidence.append(
                {
                    "source": "GDELT",
                    "label": item["title"],
                    "url": item.get("url"),
                }
            )
        summary_parts.append("Public-source signal flow: " + "; ".join(feed_bits) + ".")
    elif gdelt_result["status"] != "skipped":
        summary_parts.append(
            "Public-source signal flow is currently using fallback mode because GDELT is rate-limited or unavailable."
        )

    if not summary_parts:
        summary_parts.append(
            "Ask about an allocator, a manager, filings, macro context, or mandate movement and the desk will pull the relevant source packet."
        )

    answer = " ".join(summary_parts)
    gemini_answer = call_gemini_research(
        query_text,
        {
            "summaries": summary_parts,
            "evidence": evidence,
            "sponsor_tickers": sponsor_tickers,
            "country_codes": country_codes,
            "live_status": get_cached_dashboard_payload().get("statuses", []) if get_cached_dashboard_payload() else [],
        },
    )
    if gemini_answer:
        answer = gemini_answer
    return {
        "query": query_text,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "answer": answer,
        "evidence": evidence[:8],
        "assistant_mode": "research_only",
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
            self._write_json({"status": "ok"})
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
    parser = argparse.ArgumentParser(description="Serve the SWFI intelligence workspace demo.")
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8344")))
    args = parser.parse_args()

    server = http.server.ThreadingHTTPServer((args.host, args.port), SiteHandler)
    print(f"serving {ROOT} on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
