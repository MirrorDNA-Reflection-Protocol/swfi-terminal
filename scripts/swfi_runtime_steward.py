#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import sys
from urllib import error as urlerror, request


DEFAULT_ORIGIN = os.environ.get("SWFI_RUNTIME_ORIGIN", "http://127.0.0.1:8344").rstrip("/")
DEFAULT_SESSION_COOKIE = os.environ.get("SWFI_SESSION_COOKIE", "").strip()


def fetch_json(url: str, *, session_cookie: str = "") -> dict[str, object]:
    req = request.Request(url, headers={"Accept": "application/json"})
    if session_cookie:
        req.add_header("Cookie", session_cookie)
    with request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def render_markdown(payload: dict[str, object]) -> str:
    runtime = payload.get("label") or "SWFI Runtime Steward"
    purpose = payload.get("purpose") or ""
    research_loop = payload.get("research_loop") or {}
    summary = research_loop.get("summary") or {}
    observe = payload.get("observe") or []
    decide = payload.get("decide") or []
    writeback = payload.get("writeback") or []
    gold = research_loop.get("gold_candidates") or []

    lines = [
        f"# {runtime}",
        "",
        purpose,
        "",
        "## Summary",
        f"- Tracked sources: {summary.get('tracked_sources', 0)}",
        f"- High-priority sources: {summary.get('high_priority_sources', 0)}",
        f"- Gold candidates: {summary.get('gold_candidates', 0)}",
        f"- Publishable nuggets: {summary.get('publishable_nuggets', 0)}",
        f"- Pending nuggets: {summary.get('pending_nuggets', 0)}",
        "",
        "## Observe",
    ]
    for item in observe:
        lines.append(f"- {item}")
    lines.extend(["", "## Decide"])
    for item in decide:
        lines.append(f"- {item}")
    lines.extend(["", "## Write Back"])
    for item in writeback:
        lines.append(f"- {item}")
    lines.extend(["", "## Gold Queue"])
    for item in gold[:5]:
        lines.append(f"- **{item.get('title', 'Untitled')}** · {item.get('status', 'NeedsReview')} · {item.get('priority', 'medium')}")
        lines.append(f"  - {item.get('why_it_matters', '')}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Read the SWFI Runtime Steward snapshot.")
    parser.add_argument("--origin", default=DEFAULT_ORIGIN, help="SWFI runtime origin")
    parser.add_argument("--session-cookie", default=DEFAULT_SESSION_COOKIE, help="Authenticated session cookie")
    parser.add_argument("--json", action="store_true", help="Print raw JSON")
    args = parser.parse_args()

    url = f"{args.origin.rstrip('/')}/api/swfi/steward/v1"
    try:
        payload = fetch_json(url, session_cookie=args.session_cookie)
    except urlerror.HTTPError as exc:
        sys.stderr.write(f"HTTP {exc.code} from {url}\n")
        return 1
    except Exception as exc:
        sys.stderr.write(f"Failed to read {url}: {exc}\n")
        return 1

    if args.json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        sys.stdout.write(render_markdown(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
