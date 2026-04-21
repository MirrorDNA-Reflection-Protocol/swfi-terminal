#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
SERVE_PATH = ROOT / "serve.py"


def load_serve_module():
    spec = importlib.util.spec_from_file_location("swfi_serve", SERVE_PATH)
    if not spec or not spec.loader:
        raise RuntimeError(f"Unable to load {SERVE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the SWFI governed research eval pack.")
    parser.add_argument("--live-models", action="store_true", help="Allow model calls instead of deterministic-only evaluation.")
    parser.add_argument("--json", action="store_true", help="Print the full summary JSON instead of a compact report.")
    args = parser.parse_args()

    serve = load_serve_module()
    pack = serve.build_research_eval_pack()
    results = []
    passed = 0

    for case in pack.get("cases", []):
        query = str(case.get("query", ""))
        payload = serve.build_research_payload(query, allow_models=args.live_models)
        expectations = case.get("expectations", {})
        checks = []
        if "status" in expectations:
            checks.append(payload.get("status") == expectations["status"])
        if "guardrail" in expectations:
            checks.append(payload.get("guardrail") == expectations["guardrail"])
        if "prompt_version" in expectations:
            checks.append(payload.get("prompt_version") == expectations["prompt_version"])
        if "min_sources" in expectations:
            checks.append(len(payload.get("source_refs", [])) >= int(expectations["min_sources"]))
        ok = all(checks) if checks else True
        if ok:
            passed += 1
        results.append(
            {
                "id": case.get("id"),
                "query": query,
                "ok": ok,
                "status": payload.get("status"),
                "guardrail": payload.get("guardrail"),
                "prompt_version": payload.get("prompt_version"),
                "source_refs": len(payload.get("source_refs", [])),
                "provider_label": payload.get("provider_label"),
            }
        )

    summary = {
        "pack_version": pack.get("pack_version", "swfi.eval_pack.v1"),
        "allow_models": bool(args.live_models),
        "passed_cases": passed,
        "total_cases": len(results),
        "failed_cases": len(results) - passed,
        "results": results,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"{summary['pack_version']}: {summary['passed_cases']}/{summary['total_cases']} passed")
        for row in results:
            mark = "PASS" if row["ok"] else "FAIL"
            print(f"{mark}  {row['id']}  status={row['status']}  prompt={row['prompt_version']}  refs={row['source_refs']}  provider={row['provider_label']}")

    return 0 if summary["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
