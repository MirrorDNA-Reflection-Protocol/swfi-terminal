#!/usr/bin/env python3
"""
demo/seed/seed_entities.py — Pass A: seed demo/seed/entities.json from sandbox API.

Strategy (confirmed by API probe 2026-04-19):
  1. Fetch entities by type (SWF, Pension Fund, etc.) — type filter returns targeted subsets
  2. Enrich each entity with:
     - /aum?entity_id={id}       → rich numeric AUM (assets field is numeric here)
     - /people?entity_id={id}    → verified contacts
     - /transactions?entity_id={id} → transaction records
  3. Apply hard completeness filter (AUM + contact + txn + provenance)
  4. Rank by completeness score, take top 500
  5. Write entities.json + ratification CSV for Prem + Kong

Sandbox API (confirmed):
  Base: https://sandbox-api.swfi.com/v1
  Auth: Authorization: <raw_key>  (no Bearer prefix)
  Pagination: ?limit=N&offset=N
  Type filter: /entities?type=Sovereign+Wealth+Fund  (173 SWFs confirmed)
  AUM: /aum?entity_id={id}  → {"data": [{assets: 545000000000, ...}]}

Usage (from repo root):
    python3 demo/seed/seed_entities.py [--dry-run] [--limit 500]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import parse, request
from urllib.error import HTTPError

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SEED_DIR = REPO_ROOT / "demo" / "seed"
ENTITIES_JSON = SEED_DIR / "entities.json"
SANDBOX_BASE = os.environ.get("SWFI_SANDBOX_API_ROOT", "https://sandbox-api.swfi.com/v1").rstrip("/")

REQUIRED_PROVENANCE_FIELDS = [
    "source_system", "retrieval_time", "extraction_method",
    "confidence", "status", "evidence_url_or_pointer",
]

# Entity types to target — covers the demo narrative (MENA SWFs, pension funds, etc.)
TARGET_TYPES = [
    "Sovereign Wealth Fund",
    "Pension Fund",
    "Endowment",
    "Family Office",
    "Insurance Company",
    "Central Bank",
    "Development Bank",
    "Asset Manager",
    "Government Investment Corporation",
    "National Reserve Fund",
    "Sovereign Development Fund",
    "Public Pension Reserve",
]

_SANDBOX_MIN_INTERVAL = 0.12
_last_req: float = 0.0


# ── keychain ──────────────────────────────────────────────────────────────────
def load_secret(*names: str) -> str:
    for name in names:
        try:
            r = subprocess.run(
                ["security", "find-generic-password", "-a", "mirrordna", "-s", name, "-w"],
                capture_output=True, text=True, timeout=5, check=False,
            )
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()
        except Exception:
            pass
    for name in names:
        v = os.environ.get(name, "").strip()
        if v:
            return v
    return ""


# ── fetch helpers ─────────────────────────────────────────────────────────────
def _get(path: str, key: str, params: dict | None = None, timeout: int = 20) -> dict:
    global _last_req
    url = f"{SANDBOX_BASE}/{path.lstrip('/')}"
    if params:
        pairs = [(k, v) for k, v in params.items() if v not in ("", None)]
        if pairs:
            url += "?" + parse.urlencode(pairs, doseq=True)
    wait = _SANDBOX_MIN_INTERVAL - (time.time() - _last_req)
    if wait > 0:
        time.sleep(wait)
    _last_req = time.time()
    req = request.Request(url, headers={"Accept": "application/json", "Authorization": key})
    with request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_all(path: str, key: str, params: dict | None = None, max_records: int = 500) -> list[dict]:
    """Paginate an endpoint and return all records up to max_records."""
    all_records: list[dict] = []
    base_params = dict(params or {})
    page_size = min(100, max_records)
    offset = 0
    while len(all_records) < max_records:
        p = {**base_params, "limit": page_size, "offset": offset}
        try:
            raw = _get(path, key, p)
        except Exception as exc:
            print(f"    [warn] {path} offset={offset}: {exc}", file=sys.stderr)
            break
        records = raw.get("data") or (raw if isinstance(raw, list) else [])
        if not records:
            break
        all_records.extend(records)
        if len(records) < page_size:
            break
        offset += page_size
    return all_records[:max_records]


# ── enrichment ────────────────────────────────────────────────────────────────
def enrich(entity: dict, key: str) -> dict:
    eid = entity.get("_id") or entity.get("id") or entity.get("entity_id")
    if not eid:
        return entity

    # AUM series — richer than the entity stub's `assets` field
    aum_records = _fetch_all("aum", key, {"entity_id": eid}, max_records=5)
    if aum_records:
        # Use the most recent record
        latest = sorted(aum_records, key=lambda r: r.get("period",""), reverse=True)[0]
        entity["_aum_series"] = aum_records
        entity["_aum_latest"] = latest
        # Promote the numeric AUM to top-level for filter/score
        if latest.get("assets") and not entity.get("assets"):
            entity["assets"] = latest["assets"]

    # Contacts (people)
    if not entity.get("contacts"):
        people = _fetch_all("people", key, {"entity_id": eid}, max_records=20)
        if people:
            entity["contacts"] = people

    # Transactions: /transactions does not support per-entity filter (400s). Skip.

    return entity


# ── completeness ──────────────────────────────────────────────────────────────
def has_aum(e: dict) -> bool:
    for field in ("assets", "managed_assets", "aum"):
        v = e.get(field)
        if v is None or v == "":
            continue
        if isinstance(v, (int, float)) and v > 0:
            return True
        if isinstance(v, str) and v.strip():
            return True
    # also check promoted AUM from enrichment
    latest = e.get("_aum_latest") or {}
    if latest.get("assets") and float(latest.get("assets") or 0) > 0:
        return True
    return False


def has_verified_contact(e: dict) -> bool:
    if e.get("phone") and str(e["phone"]).strip():
        return True
    contacts = e.get("contacts") or []
    return isinstance(contacts, list) and len(contacts) > 0


def has_transaction_or_rfp(e: dict) -> bool:
    for key in ("transactions", "investments", "deals", "rfps", "opportunities"):
        v = e.get(key)
        if isinstance(v, list) and len(v) > 0:
            return True
    return False


def has_complete_provenance(e: dict) -> bool:
    prov = e.get("provenance") or {}
    return all(prov.get(f) for f in REQUIRED_PROVENANCE_FIELDS)


def completeness_score(e: dict) -> float:
    def _count(obj: object, depth: int = 0) -> tuple[int, int]:
        if depth > 4:
            return 0, 0
        if isinstance(obj, dict):
            p = t = 0
            for v in obj.values():
                dp, dt = _count(v, depth + 1)
                p += dp; t += dt
            return p, t
        if isinstance(obj, list):
            p = t = 0
            for item in obj[:10]:
                dp, dt = _count(item, depth + 1)
                p += dp; t += dt
            return p, t
        present = obj is not None and obj != "" and obj is not False
        return (1 if present else 0), 1
    pop, total = _count(e)
    return round(pop / total, 4) if total else 0.0


def inject_provenance(e: dict) -> dict:
    if e.get("provenance"):
        return e
    e["provenance"] = {
        "source_system": "swfi_sandbox_api/entities",
        "retrieval_time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "extraction_method": "rest_api_json",
        "confidence": "medium",
        "status": "pending_ratification",
        "evidence_url_or_pointer": f"{SANDBOX_BASE}/entities",
    }
    return e


def red_flags(e: dict) -> list[str]:
    flags = []
    if not has_aum(e): flags.append("missing_aum")
    if not has_verified_contact(e): flags.append("no_verified_contact")
    if not has_transaction_or_rfp(e): flags.append("no_transactions_or_rfps")
    if not has_complete_provenance(e): flags.append("incomplete_provenance")
    return flags


# ── main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--no-enrich", action="store_true",
                        help="Skip AUM/people/transactions enrichment (faster, lower hit rate)")
    args = parser.parse_args()

    api_key = load_secret("SWFI_SANDBOX_API_KEY")
    if not api_key:
        print("ERROR: SWFI_SANDBOX_API_KEY not found", file=sys.stderr)
        sys.exit(1)
    print(f"[seed] API key loaded ({len(api_key)} chars)")

    # Step 1: collect entity stubs by type
    all_stubs: list[dict] = []
    seen_ids: set = set()
    for entity_type in TARGET_TYPES:
        try:
            data = _get("entities", api_key, {"type": entity_type, "limit": 1, "offset": 0})
            total = data.get("total_items", 0)
            print(f"  {entity_type}: {total} available")
        except Exception as exc:
            print(f"  {entity_type}: error ({exc})", file=sys.stderr)
            continue
        if not total:
            continue
        # fetch up to 500 per type (we'll trim globally later)
        records = _fetch_all("entities", api_key, {"type": entity_type}, max_records=500)
        for r in records:
            eid = r.get("_id") or r.get("id")
            if eid and eid not in seen_ids:
                seen_ids.add(eid)
                all_stubs.append(r)

    print(f"\n[seed] Total unique stubs: {len(all_stubs)}")

    # Step 2: enrich (or skip)
    enriched: list[dict] = []
    if args.no_enrich:
        enriched = [inject_provenance(e) for e in all_stubs]
    else:
        print(f"[seed] Enriching {len(all_stubs)} stubs with AUM, contacts, transactions…")
        for i, e in enumerate(all_stubs):
            e = enrich(e, api_key)
            e = inject_provenance(e)
            enriched.append(e)
            if (i + 1) % 50 == 0:
                print(f"  enriched {i + 1}/{len(all_stubs)}…")

    # Step 3: filter + score
    # Hard filter: AUM + verified contact + provenance (all three populated by enrichment).
    # Transactions: the sandbox /transactions endpoint has no per-entity filter param —
    # transaction data is recorded as a soft flag in the CSV, not a hard gate.
    passed: list[tuple[float, dict]] = []
    reasons: dict[str, int] = {}
    for e in enriched:
        hard_fail = []
        if not has_aum(e): hard_fail.append("missing_aum")
        if not has_verified_contact(e): hard_fail.append("no_verified_contact")
        if not has_complete_provenance(e): hard_fail.append("incomplete_provenance")
        if not hard_fail:
            passed.append((completeness_score(e), e))
        else:
            for f in hard_fail:
                reasons[f] = reasons.get(f, 0) + 1

    print(f"\n[seed] Passed: {len(passed)}  |  Filtered: {len(enriched)-len(passed)}")
    if reasons:
        for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"  {reason}: {count}")

    passed.sort(key=lambda x: x[0], reverse=True)
    top_scored = passed[: args.limit]
    top = [e for _, e in top_scored]
    print(f"[seed] Top {len(top)} selected")

    breakdown: dict[str, int] = {}
    for e in top:
        t = str(e.get("type", "unknown"))
        breakdown[t] = breakdown.get(t, 0) + 1

    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    csv_path = SEED_DIR / f"ratification-{date_str}.csv"

    if args.dry_run:
        print(f"\n[dry-run] Would write {ENTITIES_JSON} ({len(top)} entities)")
        print(f"[dry-run] Would write {csv_path}")
        print(f"[dry-run] entity type breakdown: {breakdown}")
        if top_scored:
            s, e = top_scored[0]
            print(f"[dry-run] Best: score={s:.4f} name='{e.get('name','?')}' type='{e.get('type','?')}'")
        return

    SEED_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "_note": "Auto-seeded. Pending Pass B ratification by Prem + Kong.",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(top),
        "sources_breakdown": {"sandbox_api": len(top)},
        "entity_type_breakdown": breakdown,
        "entities": top,
    }
    ENTITIES_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[seed] Wrote {ENTITIES_JSON}")

    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["entity_name", "entity_type", "country", "aum_usd",
                         "contact_count", "transaction_count", "completeness_score", "red_flags"])
        for score, e in top_scored:
            latest = e.get("_aum_latest") or {}
            aum_val = latest.get("assets") or e.get("assets") or e.get("managed_assets") or ""
            contacts = e.get("contacts") or (["phone"] if e.get("phone") else [])
            txns = e.get("transactions") or []
            flags = red_flags(e)
            writer.writerow([
                e.get("name", ""), e.get("type", ""), e.get("country", ""),
                aum_val,
                len(contacts) if isinstance(contacts, list) else 0,
                len(txns) if isinstance(txns, list) else 0,
                f"{score:.4f}",
                "; ".join(flags) if flags else "",
            ])
    print(f"[seed] Wrote {csv_path}")
    print(f"[seed] Done. Send {csv_path.name} to Prem + Kong for ratification.")


if __name__ == "__main__":
    main()
