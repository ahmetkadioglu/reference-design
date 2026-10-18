#!/usr/bin/env python3
"""Store and retrieve reference-design findings using the Python standard library."""
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from datetime import datetime, timezone
from urllib.parse import unquote, urlsplit, urlunsplit

STATUSES = {"queued", "partial", "analyzed", "unavailable"}
FACETS = ("domains", "components", "techniques")
FIELDS = {"url", "title", "tags", "roles", "summary", "status", "visual", "technical",
          "evidence", "preferences", "limitations", "inspected_at", *FACETS}
TRACKERS = {"fbclid", "gclid", "msclkid"}
ALIASES = ["card cards kart kartlar", "grain grainy gren grenli putur puturlu noise", "shadow shadows golge",
           "booking bookings appointment appointments rezervasyon randevu", "glass cam glassmorphism",
           "light acik", "dark koyu", "dashboard dashboards panel", "gradient gradients degrade",
           "typography tipografi", "navigation navbar navigasyon", "form forms formlar"]


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def canonical_url(value):
    if not isinstance(value, str):
        raise ValueError("url must be a string")
    parsed = urlsplit(value.strip())
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("url must be an absolute http(s) URL")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Do not store credentials in reference URLs")
    host = parsed.hostname.lower().encode("idna").decode("ascii")
    if ":" in host:
        host = "[" + host + "]"
    port = parsed.port
    if port and (parsed.scheme.lower(), port) not in {("http", 80), ("https", 443)}:
        host += ":" + str(port)
    query = []
    for part in parsed.query.split("&") if parsed.query else []:
        key = unquote(part.split("=", 1)[0]).casefold()
        if not key.startswith("utm_") and key not in TRACKERS:
            query.append(part)
    return urlunsplit((parsed.scheme.lower(), host, parsed.path or "/", "&".join(query), parsed.fragment))


def unique(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def check_record(record):
    if record.get("status") not in STATUSES:
        raise ValueError("Unknown reference status")
    for key in ("title", "summary"):
        if not isinstance(record.get(key), str):
            raise ValueError(key + " must be a string")
    for key in ("tags", "roles", "limitations", *FACETS):
        values = record.get(key, []) if key in FACETS else record.get(key)
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            raise ValueError(key + " must be a list of strings")
    for key in ("visual", "technical", "preferences"):
        if not isinstance(record.get(key), dict):
            raise ValueError(key + " must be an object")
    if not isinstance(record.get("evidence"), list):
        raise ValueError("evidence must be an array")
    for evidence in record["evidence"]:
        if not isinstance(evidence, dict) or not all(isinstance(evidence.get(k), str) and evidence[k].strip()
                                                    for k in ("kind", "source", "finding")):
            raise ValueError("Each evidence needs string kind, source and finding")
    inspected = record.get("inspected_at")
    if inspected is not None:
        if not isinstance(inspected, str):
            raise ValueError("inspected_at must be an ISO timestamp or null")
        datetime.fromisoformat(inspected.replace("Z", "+00:00"))
    if record["status"] == "analyzed" and not (record["summary"].strip() and record["evidence"]
                                                and (record["visual"] or record["technical"])):
        raise ValueError("analyzed requires summary, findings and evidence")


def load(root):
    path = root / "store.json"
    if not path.exists():
        return {"schema_version": 1, "references": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("references"), list):
        raise ValueError("Invalid memory store; preserve it and repair instead of resetting")
    seen = set()
    for record in data["references"]:
        check_record(record)
        canonical = canonical_url(record["url"])
        expected_id = "ref-" + hashlib.sha256(canonical.encode()).hexdigest()[:16]
        if record.get("canonical_url") != canonical or record.get("id") != expected_id or canonical in seen:
            raise ValueError("Inconsistent or duplicate reference identity")
        if not isinstance(record.get("history"), list):
            raise ValueError("history must be an array")
        seen.add(canonical)
    return data


def merge_dict(old, patch):
    result = copy.deepcopy(old)
    for key, value in patch.items():
        result[key] = merge_dict(result[key], value) if isinstance(value, dict) and isinstance(result.get(key), dict) else copy.deepcopy(value)
    return result


def apply_patch(data, patch):
    if not isinstance(patch, dict) or "url" not in patch or set(patch) - FIELDS:
        raise ValueError("Each patch needs url and only documented fields")
    canonical = canonical_url(patch["url"])
    identity = "ref-" + hashlib.sha256(canonical.encode()).hexdigest()[:16]
    previous = next((r for r in data["references"] if r["canonical_url"] == canonical), None)
    if previous is None and any(r["id"] == identity for r in data["references"]):
        raise ValueError("Reference ID collision")
    timestamp = now()
    record = copy.deepcopy(previous) if previous else {
        "id": identity, "url": canonical, "canonical_url": canonical, "source_urls": [],
        "title": "", "tags": [], "roles": [], "summary": "", "status": "queued",
        "domains": [], "components": [], "techniques": [],
        "visual": {}, "technical": {}, "preferences": {}, "evidence": [], "limitations": [],
        "inspected_at": None, "created_at": timestamp, "updated_at": timestamp, "history": []}
    record["source_urls"] = unique(record["source_urls"] + [patch["url"].strip()])
    for key, value in patch.items():
        if key == "url":
            continue
        if key in {"tags", "roles", *FACETS} and isinstance(value, list):
            record[key] = unique(record.get(key, []) + value)
        elif isinstance(value, dict) and isinstance(record.get(key), dict):
            record[key] = merge_dict(record[key], value)
        else:
            record[key] = copy.deepcopy(value)
    check_record(record)
    if previous == record:
        return previous
    if previous:
        record["history"].append({k: copy.deepcopy(v) for k, v in previous.items() if k != "history"})
        record["updated_at"] = timestamp
        data["references"][data["references"].index(previous)] = record
    else:
        data["references"].append(record)
    return record


def write_patches(root, patches, capture=None):
    root.mkdir(parents=True, exist_ok=True)
    lock = root / ".write-lock"
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError("Memory is locked by another writer; retry after it finishes")
    temp = None
    try:
        data = load(root)
        if capture is not None:
            patches = [capture_patch(data, capture)]
        records = [apply_patch(data, patch) for patch in patches]
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=root, prefix=".store-", delete=False) as handle:
            temp = Path(handle.name)
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, root / "store.json")
        return records
    finally:
        if temp and temp.exists():
            temp.unlink()
        lock.rmdir()


def brief(record):
    result = {key: record[key] for key in ("id", "url", "title", "tags", "roles", "summary", "status", "inspected_at", "updated_at")}
    result.update({key: record.get(key, []) for key in FACETS})
    return result


def tokenize(value):
    text = unicodedata.normalize("NFKD", value.casefold().replace("ı", "i"))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", text)


def words(value):
    return set(tokenize(value))


def terms(value):
    aliases = {term: tokenize(group)[0] for group in ALIASES for term in tokenize(group)}
    return [aliases.get(term, term) for term in tokenize(value)]


def search(records, query, limit, all_statuses=False, filters=None, explain=False):
    """Field-weighted BM25, with document frequency over eligible records."""
    from collections import Counter
    weights = {"title": 3, "url": 1, "tags": 5, "roles": 5, "summary": 3,
               "visual": 2, "technical": 2, "preferences": 2,
               "domains": 5, "components": 5, "techniques": 5}
    eligible = [r for r in records if all_statuses or r["status"] in {"analyzed", "partial"}]
    query_terms = set(terms(query))
    documents = [{key: Counter(terms(json.dumps(r.get(key, []), ensure_ascii=False)))
                  for key in weights} for r in eligible]
    averages = {key: sum(sum(doc[key].values()) for doc in documents) / max(1, len(documents))
                for key in weights}
    frequencies = {term: sum(any(term in field for field in doc.values()) for doc in documents)
                   for term in query_terms}
    found = []
    for record, doc in zip(eligible, documents):
        if any(not any(set(terms(value)) == set(terms(candidate))
                       for candidate in record.get(key, []) + record.get("tags", []))
               for key, values in (filters or {}).items() for value in values):
            continue
        score, matches = 0.0, {}
        for term in query_terms:
            tf = sum(weights[key] * field[term] / (0.25 + 0.75 * sum(field.values()) / (averages[key] or 1))
                     for key, field in doc.items())
            if tf:
                idf = math.log(1 + (len(eligible) - frequencies[term] + 0.5) / (frequencies[term] + 0.5))
                score += idf * tf * 2.2 / (tf + 1.2)
                matches[term] = [key for key, field in doc.items() if field[term]]
        if score:
            result = dict(brief(record), score=round(score, 6))
            if explain:
                result["matches"] = matches
            found.append((score, record["updated_at"], record["id"], result))
    found.sort(key=lambda item: item[:3], reverse=True)
    return [item[3] for item in found[:limit]]


def capture_patch(data, report):
    """Import capture facts without claiming human visual or source review."""
    if report.get("capture_version") != 1 or not isinstance(report.get("snapshots"), list):
        raise ValueError("Expected a version 1 capture report")
    url = canonical_url(report["url"])
    if not isinstance(report.get("captured_at"), str):
        raise ValueError("Capture report needs an ISO captured_at timestamp")
    datetime.fromisoformat(report["captured_at"].replace("Z", "+00:00"))
    previous = next((r for r in data["references"] if r["canonical_url"] == url), {})
    snapshots = report["snapshots"]
    limitations = report.get("limitations", [])
    if not isinstance(limitations, list) or not all(isinstance(v, str) for v in limitations):
        raise ValueError("Capture limitations must be strings")
    evidence = []
    interactions = []
    for shot in snapshots:
        if not isinstance(shot, dict) or not isinstance(shot.get("elements"), list):
            raise ValueError("Capture snapshot needs sampled elements")
        evidence.append({"kind": "runtime", "source": shot.get("url", url),
                         "locator": str(shot.get("viewport")) + "/" + str(shot.get("state")) + "/reduced-motion=" + str(bool(shot.get("reduced_motion"))),
                         "finding": "Captured %d representative elements and computed styles; screenshot capture is not a visual review." % len(shot["elements"])})
        trace = shot.get("interaction_trace")
        if trace and len(interactions) < 30:
            interactions.append({"name": trace["name"], "viewport": shot.get("viewport"),
                "reduced_motion": shot.get("reduced_motion", False), "passed": trace.get("passed"),
                "changed_selectors": unique(c["selector"] for step in trace.get("steps", []) for c in step.get("changes", [])),
                "executed_sources": unique(fn["source"] for step in trace.get("steps", []) for fn in step.get("executed_functions", []))})
            evidence.append({"kind": "runtime", "source": shot.get("url", url), "locator": "scenario:" + trace["name"],
                "finding": "Observed explicit actions, DOM/style deltas, and any available executed-code ranges. Passed configured expectations: " + str(trace.get("passed")) + ". Causal interpretation requires review."})
    patch = {"url": url, "status": "partial" if snapshots or previous.get("evidence") else "unavailable",
             "technical": {"capture": {"captured_at": report.get("captured_at"),
                                       "report": report.get("report_path"),
                                       "viewports": [s.get("viewport") for s in snapshots],
                                       "interactions": interactions,
                                       "quality_counts": report.get("quality_counts", {})}},
             "evidence": unique(previous.get("evidence", []) + evidence),
             "limitations": unique(previous.get("limitations", []) + limitations +
                ["Capture attempt: " + json.dumps(error, ensure_ascii=False)[:1200] for error in report.get("errors", [])])}
    if not previous.get("title"):
        patch["title"] = report.get("title", "")
    if snapshots:
        patch["inspected_at"] = report["captured_at"]
    return patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = os.environ.get("REFERENCE_DESIGN_MEMORY_ROOT") or str(Path(__file__).resolve().parents[1] / "references" / "memory")
    parser.add_argument("--root", type=Path, default=Path(default_root))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    sub.add_parser("validate")
    capture = sub.add_parser("import-capture")
    capture.add_argument("--file", required=True, help="capture_reference.py report.json")
    upsert = sub.add_parser("upsert")
    upsert.add_argument("--file", default="-", help="JSON object/array; '-' reads stdin")
    get = sub.add_parser("get")
    get.add_argument("reference", help="Stored ID or exact URL")
    get.add_argument("--history", action="store_true")
    find = sub.add_parser("search")
    find.add_argument("query")
    find.add_argument("--limit", type=int, default=8)
    find.add_argument("--all-statuses", action="store_true")
    find.add_argument("--explain", action="store_true")
    for facet in FACETS:
        find.add_argument("--" + facet[:-1], action="append", default=[])
    args = parser.parse_args()
    if args.command == "import-capture":
        report = json.loads(Path(args.file).read_text(encoding="utf-8"))
        output = [brief(record) for record in write_patches(args.root, [], capture=report)]
    elif args.command == "upsert":
        raw = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
        patches = json.loads(raw)
        patches = patches if isinstance(patches, list) else [patches]
        if not patches:
            raise ValueError("Supply at least one reference")
        output = [brief(record) for record in write_patches(args.root, patches)]
    else:
        data = load(args.root)
        records = data["references"]
        if args.command == "validate":
            output = {"valid": True, "references": len(records), "store": str(args.root / "store.json")}
        elif args.command == "list":
            output = [brief(record) for record in sorted(records, key=lambda r: r["updated_at"], reverse=True)]
        elif args.command == "search":
            if args.limit < 1:
                raise ValueError("limit must be positive")
            output = search(records, args.query, args.limit, args.all_statuses,
                            {key: getattr(args, key[:-1]) for key in FACETS}, args.explain)
        else:
            candidate = canonical_url(args.reference) if args.reference.startswith(("http://", "https://")) else args.reference
            match = next((r for r in records if candidate in {r["id"], r["canonical_url"]}), None)
            if match is None:
                raise ValueError("Reference not found")
            output = {k: v for k, v in match.items() if k != "history" or args.history}
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("reference-memory: " + str(error), file=sys.stderr)
        sys.exit(1)
