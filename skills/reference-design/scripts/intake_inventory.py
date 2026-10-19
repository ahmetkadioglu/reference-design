#!/usr/bin/env python3
"""Review structured component coverage without treating style labels as an intake."""
import argparse
import json
import os
from pathlib import Path
import sys

import reference_memory as memory

CATEGORIES = ("cards", "icons", "typography", "layout", "navigation", "motion", "surfaces", "ux")
SCOPES = {"site", "component", "visual-only", "source-only"}
STATES = {"inspected", "not_observed", "unavailable", "out_of_scope"}
TECHNICAL = {"code-declaration", "runtime", "source-code"}
KINDS = TECHNICAL | {"visual-estimate"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def template(url, scope="site"):
    if scope not in SCOPES:
        raise ValueError("Unknown inspection scope")
    return {"url": memory.canonical_url(url), "status": "partial",
            "technical": {"intake": {"version": 1, "scope": scope,
                "categories": {name: {"status": "pending", "checks": [], "findings": [], "reason": ""}
                               for name in CATEGORIES}}}}


def review(record):
    errors, coverage, limited = [], {}, []
    intake = record.get("technical", {}).get("intake")
    if not isinstance(intake, dict) or intake.get("version") != 1:
        return {"url": record.get("url"), "ready": False, "partial": True,
                "errors": ["Missing technical.intake version 1 component inventory"],
                "coverage": {}, "limitation": "Checks structure and evidence linkage, not the truth or quality of an inspection."}
    scope = intake.get("scope")
    if scope not in SCOPES:
        errors.append("Inventory scope must be site, component, visual-only, or source-only")
    categories = intake.get("categories")
    if not isinstance(categories, dict):
        categories = {}
        errors.append("Inventory categories must be an object")
    if set(categories) - set(CATEGORIES):
        errors.append("Unknown inventory categories")
    for name in CATEGORIES:
        item = categories.get(name)
        if not isinstance(item, dict):
            errors.append(name + ": missing category")
            continue
        state = item.get("status")
        findings, checks = item.get("findings"), item.get("checks")
        coverage[name] = {"status": state, "findings": len(findings) if isinstance(findings, list) else 0}
        if state not in STATES:
            errors.append(name + ": inspection is pending or status is invalid")
        if not isinstance(checks, list) or not checks or not all(nonempty(c) for c in checks):
            errors.append(name + ": record actual inspection steps or the attempted access route in checks")
        if not isinstance(findings, list):
            errors.append(name + ": findings must be an array")
            continue
        if state == "inspected" and not findings:
            errors.append(name + ": inspected requires concrete findings")
        if state != "inspected":
            if findings:
                errors.append(name + ": positive findings require inspected status")
            if not nonempty(item.get("reason")):
                errors.append(name + ": explain missing, absent, or excluded coverage")
            if state in {"unavailable", "out_of_scope"}:
                limited.append(name)
            if state == "out_of_scope" and scope == "site":
                errors.append(name + ": a general site intake cannot silently exclude this category")
        for index, finding in enumerate(findings):
            prefix = name + " finding " + str(index + 1) + ": "
            if not isinstance(finding, dict):
                errors.append(prefix + "must be an object")
                continue
            for field in ("feature", "observation", "reuse"):
                if not nonempty(finding.get(field)):
                    errors.append(prefix + field + " must be concrete and nonempty")
            evidence = finding.get("evidence")
            valid_evidence = isinstance(evidence, list) and bool(evidence) and all(
                isinstance(e, dict) and e.get("kind") in KINDS and
                all(nonempty(e.get(k)) for k in ("source", "locator", "finding")) for e in evidence)
            if not valid_evidence:
                errors.append(prefix + "needs supported evidence with source, locator, and finding")
            mechanism = finding.get("mechanism")
            if mechanism is None:
                if name not in limited: limited.append(name)
                if valid_evidence and any(e["kind"] in TECHNICAL for e in evidence):
                    errors.append(prefix + "explain the mechanism supported by the technical evidence")
            elif not nonempty(mechanism) or not valid_evidence or not any(e["kind"] in TECHNICAL for e in evidence):
                errors.append(prefix + "a mechanism claim requires technical evidence; use null when unknown")
    return {"url": record.get("url"), "ready": not errors, "partial": bool(errors or limited),
            "limited_categories": limited, "errors": errors, "coverage": coverage,
            "limitation": "Checks structure and evidence linkage, not the truth or quality of an inspection."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("REFERENCE_DESIGN_MEMORY_ROOT")
                        or Path(__file__).resolve().parents[1] / "references/memory"))
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("template")
    create.add_argument("url")
    create.add_argument("--scope", choices=sorted(SCOPES), default="site")
    check = commands.add_parser("review")
    check.add_argument("references", nargs="+", help="Saved reference IDs or exact URLs")
    args = parser.parse_args()
    if args.command == "template":
        result = template(args.url, args.scope)
        success = True
    else:
        records = memory.load(args.root)["references"]
        result = []
        for value in args.references:
            identity = memory.canonical_url(value) if value.startswith(("http://", "https://")) else value
            record = next((r for r in records if identity in {r["id"], r["canonical_url"]}), None)
            if record is None:
                raise ValueError("Reference not found: " + value)
            result.append(review(record))
        success = all(item["ready"] for item in result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("intake-inventory: " + str(error), file=sys.stderr)
        sys.exit(1)
