#!/usr/bin/env python3
"""
demo/seed/seed_entities.py — Pass A: auto-seed demo/seed/entities.json from sandbox API.

Usage:
    python3 demo/seed/seed_entities.py [--dry-run] [--limit N]

Pass A produces entities.json + a ratification CSV for Prem + Kong (Pass B).
Run from the repo root:
    cd ~/repos/swfi-terminal-live
    python3 demo/seed/seed_entities.py

Requirements:
  - SWFI_SANDBOX_API_KEY in macOS Keychain (account: mirrordna, service: SWFI_SANDBOX_API_KEY)
    or SWFI_SANDBOX_API_KEY in environment.
  - Python 3.11+, no third-party deps.
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

# ── paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SEED_DIR = REPO_ROOT / "demo" / "seed"
ENTITIES_JSON = SEED_DIR / "entities.json"

SANDBOX_BASE = "https://sandbox-api.swfi.com/v1"

# The six provenance fields required by PROVENANCE_CONTRACT in serve.py
REQUIRED_PROVENANCE_FIELDS = [
    "source_system",
    "retrieval_time",
    "extraction_method",
    "confidence",
    "status",
    "evidence_url_or_pointer",
]


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


# ── sandbox API helpers ───────────────────────────────────────────────────────
def sandbox_get(path: str, api_key: str, params: dict | None = None, timeout: int = 20) -> dict | list:
    url = f"{SANDBOX_BASE}/{path.lstrip('/')}"
    if params:
        url += "?" + parse.urlencode(params)
    req = request.Request(url, headers={
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    })
    with request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def discover_collections(api_key: str) -> list[str]:
    """Return list of collection endpoint slugs from the API root."""
    try:
        root = sandbox_get("", api_key)
        # Typical shape: {"collections": ["sovereign_wealth_funds", "pension_funds", ...]}
        if isinstance(root, dict) and "collections" in root:
            return [str(c) for c in root["collections"]]
    except Exception as exc:
        print(f"  [warn] root discovery failed: {exc}", file=sys.stderr)
    # Fallback: known collection slugs from the dashboard audit (19 collections)
    return [
        "sovereign_wealth_funds", "pension_funds", "endowments", "foundations",
        "family_offices", "insurance_companies", "central_banks", "development_banks",
        "asset_managers", "private_equity_funds", "hedge_funds", "real_estate_funds",
        "infrastructure_funds", "venture_capital", "sovereign_development_funds",
        "government_investment_corporations", "national_reserve_funds",
        "public_pension_reserves", "sovereign_investment_authorities",
    ]


def fetch_collection_entities(collection: str, api_key: str) -> list[dict]:
    """Paginate through a collection and return all entity records."""
    entities: list[dict] = []
    page = 1
    while True:
        try:
            data = sandbox_get(f"collections/{collection}", api_key, params={"page": page, "per_page": 100})
        except HTTPError as exc:
            if exc.code == 404:
                print(f"  [skip] {collection}: 404", file=sys.stderr)
            else:
                print(f"  [warn] {collection} page {page}: HTTP {exc.code}", file=sys.stderr)
            break
        except Exception as exc:
            print(f"  [warn] {collection} page {page}: {exc}", file=sys.stderr)
            break

        if isinstance(data, list):
            batch = data
        elif isinstance(data, dict):
            batch = data.get("data") or data.get("results") or data.get("entities") or []
        else:
            break

        if not batch:
            break
        entities.extend(batch)

        # Stop if we got a partial page (last page)
        if len(batch) < 100:
            break
        page += 1
        time.sleep(0.1)  # be a good citizen

    return entities


# ── completeness scoring ──────────────────────────────────────────────────────
def has_aum(entity: dict) -> bool:
    aum = entity.get("aum") or entity.get("assets_under_management")
    if isinstance(aum, dict):
        v = aum.get("value") or aum.get("amount")
        return v is not None and float(v or 0) > 0
    if isinstance(aum, (int, float)):
        return aum > 0
    return False


def has_verified_contact(entity: dict) -> bool:
    contacts = entity.get("contacts") or entity.get("people") or []
    if isinstance(contacts, list):
        for c in contacts:
            if isinstance(c, dict):
                has_email = bool(c.get("email") or c.get("email_address"))
                has_phone = bool(c.get("phone") or c.get("phone_number"))
                has_linkedin = bool(c.get("linkedin") or c.get("linkedin_url"))
                if has_email or has_phone or has_linkedin:
                    return True
    return False


def has_transaction_or_rfp(entity: dict) -> bool:
    txns = entity.get("transactions") or entity.get("investments") or []
    rfps = entity.get("rfps") or entity.get("opportunities") or []
    return len(txns) > 0 or len(rfps) > 0


def has_complete_provenance(entity: dict) -> bool:
    prov = entity.get("provenance") or entity.get("_provenance") or {}
    if not isinstance(prov, dict):
        return False
    return all(prov.get(f) for f in REQUIRED_PROVENANCE_FIELDS)


def count_populated_fields(obj: object, depth: int = 0) -> tuple[int, int]:
    """Recursively count (populated, total) leaf fields."""
    if depth > 4:
        return 0, 0
    if isinstance(obj, dict):
        populated = total = 0
        for v in obj.values():
            p, t = count_populated_fields(v, depth + 1)
            populated += p
            total += t
        return populated, total
    if isinstance(obj, list):
        populated = total = 0
        for item in obj[:10]:  # cap list depth
            p, t = count_populated_fields(item, depth + 1)
            populated += p
            total += t
        return populated, total
    # leaf
    is_present = obj is not None and obj != "" and obj != 0 and obj is not False
    return (1 if is_present else 0), 1


def completeness_score(entity: dict) -> float:
    p, t = count_populated_fields(entity)
    if t == 0:
        return 0.0
    return round(p / t, 4)


def red_flags(entity: dict) -> list[str]:
    flags = []
    if not has_aum(entity):
        flags.append("missing_aum")
    if not has_verified_contact(entity):
        flags.append("no_verified_contact")
    if not has_transaction_or_rfp(entity):
        flags.append("no_transactions_or_rfps")
    if not has_complete_provenance(entity):
        flags.append("incomplete_provenance")
    return flags


# ── provenance injection ──────────────────────────────────────────────────────
def inject_provenance_if_missing(entity: dict, collection: str) -> dict:
    """If entity lacks a provenance envelope, attach one at entity level."""
    if entity.get("provenance") or entity.get("_provenance"):
        return entity
    entity["provenance"] = {
        "source_system": f"swfi_sandbox_api/{collection}",
        "retrieval_time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "extraction_method": "api_json",
        "confidence": "medium",  # human review in Pass B will upgrade to 'high'
        "status": "pending_ratification",
        "evidence_url_or_pointer": f"{SANDBOX_BASE}/collections/{collection}",
    }
    return entity


# ── main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo/seed/entities.json from sandbox API")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and score but don't write files")
    parser.add_argument("--limit", type=int, default=500, help="Max entities to include (default 500)")
    args = parser.parse_args()

    api_key = load_secret("SWFI_SANDBOX_API_KEY")
    if not api_key:
        print("ERROR: SWFI_SANDBOX_API_KEY not found in keychain or environment.", file=sys.stderr)
        sys.exit(1)
    print(f"[seed] API key loaded ({len(api_key)} chars)")

    # Step 1: discover collections
    print("[seed] Discovering collections…")
    collections = discover_collections(api_key)
    print(f"[seed] {len(collections)} collections: {', '.join(collections)}")

    # Step 2: fetch all entities
    all_raw: list[tuple[str, dict]] = []  # (collection, entity)
    for col in collections:
        print(f"  fetching {col}…", end=" ", flush=True)
        batch = fetch_collection_entities(col, api_key)
        print(f"{len(batch)} records")
        for e in batch:
            all_raw.append((col, e))
    print(f"[seed] Total raw records: {len(all_raw)}")

    # Step 3: inject provenance, apply hard filter, score
    passed: list[tuple[float, dict]] = []
    filtered_out = 0
    for col, entity in all_raw:
        entity = inject_provenance_if_missing(entity, col)
        if not (has_aum(entity) and has_verified_contact(entity)
                and has_transaction_or_rfp(entity) and has_complete_provenance(entity)):
            filtered_out += 1
            continue
        score = completeness_score(entity)
        passed.append((score, entity))

    print(f"[seed] Passed filter: {len(passed)}  |  Filtered out: {filtered_out}")

    # Step 4: rank and take top N
    passed.sort(key=lambda x: x[0], reverse=True)
    top = [e for _, e in passed[: args.limit]]
    print(f"[seed] Top {len(top)} selected")

    # Step 5: sources_breakdown
    breakdown: dict[str, int] = {}
    for e in top:
        prov = e.get("provenance") or e.get("_provenance") or {}
        sys_name = str(prov.get("source_system", "unknown")).split("/")[0]
        breakdown[sys_name] = breakdown.get(sys_name, 0) + 1

    # Step 6: write entities.json
    output = {
        "_note": "Auto-seeded by seed_entities.py. Pending Pass B ratification by Prem + Kong.",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(top),
        "sources_breakdown": breakdown,
        "entities": top,
    }

    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    csv_path = SEED_DIR / f"ratification-{date_str}.csv"

    if args.dry_run:
        print(f"[dry-run] Would write {ENTITIES_JSON} ({len(top)} entities)")
        print(f"[dry-run] Would write {csv_path}")
        print(f"[dry-run] sources_breakdown: {breakdown}")
        return

    SEED_DIR.mkdir(parents=True, exist_ok=True)
    ENTITIES_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[seed] Wrote {ENTITIES_JSON}")

    # Step 7: ratification CSV for Prem + Kong
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "entity_name", "country", "aum_raw", "contact_count",
            "transaction_count", "rfp_count", "completeness_score", "red_flags",
        ])
        for score, entity in passed[: args.limit]:
            name = entity.get("name") or entity.get("entity_name") or entity.get("institution_name") or ""
            country = entity.get("country") or entity.get("country_code") or entity.get("headquarters_country") or ""
            aum = entity.get("aum") or entity.get("assets_under_management") or ""
            if isinstance(aum, dict):
                aum = f"{aum.get('value', '')} {aum.get('currency', '')}".strip()
            contacts = entity.get("contacts") or entity.get("people") or []
            txns = entity.get("transactions") or entity.get("investments") or []
            rfps = entity.get("rfps") or entity.get("opportunities") or []
            flags = red_flags(entity)
            writer.writerow([
                name, country, aum,
                len(contacts), len(txns), len(rfps),
                f"{score:.4f}",
                "; ".join(flags) if flags else "",
            ])

    print(f"[seed] Wrote {csv_path} ({len(top)} rows)")
    print(f"[seed] Done. Send {csv_path.name} to Prem + Kong for Pass B ratification.")
    print(f"[seed] sources_breakdown: {breakdown}")


if __name__ == "__main__":
    main()
