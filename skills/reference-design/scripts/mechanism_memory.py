#!/usr/bin/env python3
"""Store reusable, source-linked design mechanisms beside private reference memory."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

import reference_memory as references

STATUSES = {"draft", "reviewed", "deprecated"}
FIELDS = {"slug", "title", "summary", "kind", "status", "domains", "components", "techniques", "tags",
          "mechanism", "recipe", "use_when", "avoid_when", "accessibility", "limitations", "sources", "evidence"}
LISTS = ("domains", "components", "techniques", "tags", "use_when", "avoid_when", "accessibility", "limitations")


def check(record):
    if not isinstance(record.get("slug"), str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", record["slug"]):
        raise ValueError("Mechanism slug must be a lowercase identifier, at most 80 characters")
    if record.get("status") not in STATUSES:
        raise ValueError("Mechanism status must be draft, reviewed, or deprecated")
    for field in ("title", "summary", "kind"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(field + " must be a nonempty string")
    for field in LISTS:
        if not isinstance(record.get(field), list) or not all(isinstance(v, str) for v in record[field]):
            raise ValueError(field + " must be a list of strings")
    for field in ("mechanism", "recipe"):
        if not isinstance(record.get(field), dict):
            raise ValueError(field + " must be an object")
    sources = record.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("A mechanism needs at least one reference source")
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("selector"), str) or not source["selector"].strip():
            raise ValueError("Each source needs a URL and a selector/context locator")
        references.canonical_url(source.get("url"))
    evidence = record.get("evidence")
    if not isinstance(evidence, list):
        raise ValueError("evidence must be an array")
    for item in evidence:
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and item[k].strip() for k in ("kind", "source", "locator", "finding")):
            raise ValueError("Each evidence item needs kind, source, locator, and finding")
    if record["status"] == "reviewed":
        if not isinstance(record["mechanism"].get("description"), str) or not record["mechanism"]["description"].strip():
            raise ValueError("Reviewed mechanism needs a concrete description")
        steps = record["recipe"].get("steps")
        if not isinstance(steps, list) or not steps or not all(isinstance(s, str) and s.strip() for s in steps):
            raise ValueError("Reviewed mechanism needs actionable recipe.steps")
        if not any(e["kind"] in {"runtime", "code-declaration", "source-code"} for e in evidence):
            raise ValueError("Reviewed mechanism needs technical evidence; visual-only guesses remain drafts")


def load(root):
    path = root / "mechanisms.json"
    if not path.exists():
        return {"schema_version": 1, "mechanisms": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("mechanisms"), list):
        raise ValueError("Invalid mechanism store; preserve it rather than resetting")
    seen = set()
    for record in data["mechanisms"]:
        check(record)
        if record.get("id") != "mech-" + record["slug"] or record["slug"] in seen or not isinstance(record.get("history"), list):
            raise ValueError("Inconsistent mechanism identity/history")
        seen.add(record["slug"])
    return data


def upsert(root, patches):
    root.mkdir(parents=True, exist_ok=True)
    lock, temp = root / ".mechanisms-lock", None
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError("Mechanism store is locked by another writer")
    try:
        data = load(root)
        catalog = {r["canonical_url"]: r for r in references.load(root)["references"]}
        changed = []
        for patch in patches:
            if not isinstance(patch, dict) or "slug" not in patch or set(patch) - FIELDS:
                raise ValueError("Mechanism patch needs slug and only documented fields")
            previous = next((r for r in data["mechanisms"] if r["slug"] == patch["slug"]), None)
            record = copy.deepcopy(previous) if previous else {
                "id": "mech-" + str(patch["slug"]), "slug": patch["slug"], "title": "", "summary": "", "kind": "",
                "status": "draft", "mechanism": {}, "recipe": {}, "sources": [], "evidence": [],
                "created_at": references.now(), "updated_at": references.now(), "history": [],
                **{field: [] for field in LISTS}}
            for field, value in patch.items():
                if field in {"domains", "components", "techniques", "tags"} and isinstance(value, list):
                    record[field] = references.unique(record[field] + value)
                elif isinstance(value, dict) and isinstance(record.get(field), dict):
                    record[field] = references.merge_dict(record[field], value)
                else:
                    record[field] = copy.deepcopy(value)
            check(record)
            for source in record["sources"]:
                known = catalog.get(references.canonical_url(source["url"]))
                if known is None:
                    raise ValueError("Register each source in reference memory before storing its mechanisms")
                if "reference_id" in source and source["reference_id"] != known["id"]:
                    raise ValueError("Mechanism source reference_id does not match its URL")
                source["reference_id"] = known["id"]
            if record != previous:
                if previous:
                    record["history"].append({k: copy.deepcopy(v) for k, v in previous.items() if k != "history"})
                    record["updated_at"] = references.now()
                    data["mechanisms"][data["mechanisms"].index(previous)] = record
                else:
                    data["mechanisms"].append(record)
            changed.append(record)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=root, prefix=".mechanisms-", delete=False) as handle:
            temp = Path(handle.name)
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, root / "mechanisms.json")
        return changed
    finally:
        if temp and temp.exists():
            temp.unlink()
        lock.rmdir()


def brief(record):
    return {key: record[key] for key in ("id", "slug", "title", "summary", "kind", "status", "domains", "components", "techniques", "updated_at")}


def search(records, query, limit=8, include_drafts=False, filters=None):
    # Reuse the reference BM25 engine through transient search fields, never persisted proxy records.
    selected = [r for r in records if r["status"] == "reviewed" or (include_drafts and r["status"] == "draft")]
    indexed = [{**{field: r[field] for field in ("id", "title", "summary", "tags", "domains", "components", "techniques", "updated_at")},
        "url": r["sources"][0]["url"], "roles": r["use_when"], "status": "partial", "inspected_at": None,
        "visual": {}, "technical": {"mechanism": r["mechanism"], "recipe": r["recipe"]},
        "preferences": {"avoid_when": r["avoid_when"], "limitations": r["limitations"]}} for r in selected]
    by_id = {r["id"]: r for r in selected}
    return [dict(brief(by_id[result["id"]]), score=result["score"], matches=result["matches"])
            for result in references.search(indexed, query, limit, filters=filters, explain=True)]


def extract(report):
    if report.get("capture_version") != 1 or not isinstance(report.get("snapshots"), list):
        raise ValueError("Expected a version 1 capture report")
    url = references.canonical_url(report["url"])
    candidates = {}
    grids = {}

    def candidate(kind, selector, title, description, evidence, details, techniques):
        slug = kind + "-" + hashlib.sha256((url + selector).encode()).hexdigest()[:10]
        if slug not in candidates:
            candidates[slug] = {"slug": slug, "title": title, "summary": description, "kind": kind,
                "status": "draft", "components": ["card"] if "card" in selector else [], "techniques": techniques,
                "mechanism": {"description": description, "observations": details},
                "recipe": {"steps": ["Review the source evidence and missing states.", "Adapt this mechanism to the target stack and brief, then verify its rendered behavior."]},
                "sources": [{"url": url, "selector": selector}], "evidence": evidence,
                "limitations": ["Automatically extracted draft; source interpretation and target recipe require review."]}

    for shot in report["snapshots"]:
        for element in shot.get("elements", []):
            selector, styles = element["selector"], element.get("styles", {})
            if not shot.get("reduced_motion") and shot.get("state") == "default" and styles.get("display") == "grid":
                grids.setdefault(selector, []).append({"viewport": shot["viewport"], "columns": styles.get("grid-template-columns"), "gap": styles.get("gap")})
            for pseudo in ("before", "after"):
                surface = element.get(pseudo, {})
                if surface.get("content") not in (None, "none", "normal") and surface.get("background-image") not in (None, "none"):
                    candidate("surface", selector + "::" + pseudo, "Layered decorative surface",
                        "A separate pseudo-element supplies a background image behind or over the component.",
                        [{"kind": "runtime", "source": shot.get("url", url), "locator": selector + "::" + pseudo,
                          "finding": json.dumps({k: surface.get(k) for k in ("background-image", "opacity", "position", "z-index", "mix-blend-mode")})}],
                        {"pseudo_styles": surface, "component_styles": styles}, ["pseudo-element", "layered surface"])
        for rule in shot.get("rules", []):
            if re.search(r"font-size\s*:[^;]*clamp\(", rule.get("declaration", "")):
                candidate("typography", rule["selector"], "Fluid type scale", "A CSS clamp declaration constrains fluid font sizing.",
                    [{"kind": "code-declaration", "source": rule["source"], "locator": rule["locator"], "finding": rule["declaration"]}],
                    {"declaration": rule["declaration"], "conditions": rule.get("conditions", [])}, ["clamp", "fluid typography"])
        trace = shot.get("interaction_trace")
        if trace and trace.get("passed"):
            steps = [s for s in trace["steps"] if s.get("changes")]
            if steps:
                selector = "scenario:" + trace["name"]
                candidate("interaction", selector, "Observed " + trace["name"] + " state transition",
                    "Explicit UI actions coincide with recorded DOM/style changes; source causality still requires review.",
                    [{"kind": "runtime", "source": shot.get("url", url), "locator": selector,
                      "finding": "Observed %d action steps with DOM or style changes." % len(steps)}],
                    {"steps": [{"trigger": s["trigger"], "changes": s["changes"],
                                "executed_sources": [{k: fn[k] for k in ("source", "line", "function") if k in fn} for fn in s.get("executed_functions", [])]}
                               for s in steps]}, ["UI state transition"])
    for selector, views in grids.items():
        if len({v["columns"] for v in views}) > 1:
            candidate("layout", selector, "Responsive grid", "The same grid resolves to different columns across captured viewport sizes.",
                [{"kind": "runtime", "source": url, "locator": selector, "finding": json.dumps(views)}],
                {"viewports": views}, ["CSS grid", "responsive layout"])
    return list(candidates.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("REFERENCE_DESIGN_MEMORY_ROOT") or Path(__file__).resolve().parents[1] / "references/memory"))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    sub.add_parser("validate")
    write = sub.add_parser("upsert")
    write.add_argument("--file", default="-")
    get = sub.add_parser("get")
    get.add_argument("mechanism")
    get.add_argument("--history", action="store_true")
    find = sub.add_parser("search")
    find.add_argument("query")
    find.add_argument("--limit", type=int, default=8)
    find.add_argument("--include-drafts", action="store_true")
    for facet in references.FACETS:
        find.add_argument("--" + facet[:-1], action="append", default=[])
    derive = sub.add_parser("extract")
    derive.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "extract":
        result = extract(json.loads(args.capture.read_text(encoding="utf-8")))
    elif args.command == "upsert":
        patches = json.loads(sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8"))
        patches = patches if isinstance(patches, list) else [patches]
        if not patches:
            raise ValueError("Supply at least one mechanism")
        result = [brief(r) for r in upsert(args.root, patches)]
    else:
        records = load(args.root)["mechanisms"]
        if args.command == "list":
            result = [brief(r) for r in records]
        elif args.command == "validate":
            result = {"valid": True, "mechanisms": len(records)}
        elif args.command == "search":
            if args.limit < 1:
                raise ValueError("limit must be positive")
            result = search(records, args.query, args.limit, args.include_drafts,
                            {key: getattr(args, key[:-1]) for key in references.FACETS})
        else:
            record = next((r for r in records if args.mechanism in {r["id"], r["slug"]}), None)
            if record is None:
                raise ValueError("Mechanism not found")
            result = {k: v for k, v in record.items() if k != "history" or args.history}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("mechanism-memory: " + str(error), file=sys.stderr)
        sys.exit(1)
