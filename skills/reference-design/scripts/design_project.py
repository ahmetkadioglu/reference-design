#!/usr/bin/env python3
"""Persist project design decisions, resolve page overrides, and export CSS tokens."""
import argparse
import copy
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile

from reference_memory import canonical_url, merge_dict, now


def token_items(tokens, prefix=()):
    if not isinstance(tokens, dict):
        raise ValueError("tokens must be an object")
    for key, value in tokens.items():
        if not isinstance(key, str) or not re.fullmatch(r"[a-z][a-z0-9_-]*", key):
            raise ValueError("Token names must be lowercase CSS-safe identifiers")
        path = prefix + (key,)
        if isinstance(value, dict):
            yield from token_items(value, path)
        else:
            if isinstance(value, bool) or not isinstance(value, (str, int, float)):
                raise ValueError("Token values must be CSS strings or finite numbers")
            if isinstance(value, (int, float)) and not math.isfinite(value):
                raise ValueError("Token values must be finite")
            if isinstance(value, str) and (not value.strip() or re.search(r"[;{}<>\r\n]|/\*|\*/", value)):
                raise ValueError("Token values must be single CSS values, not declarations")
            yield "--" + "-".join(path), value


def check_layer(layer):
    if not isinstance(layer, dict) or set(layer) - {"tokens", "rules", "references"}:
        raise ValueError("Design layers accept tokens, rules, and references only")
    tokens = list(token_items(layer.get("tokens", {})))
    if len({name for name, _ in tokens}) != len(tokens):
        raise ValueError("Token paths collide when flattened to CSS")
    if not isinstance(layer.get("rules", {}), dict):
        raise ValueError("rules must be an object")
    references = layer.get("references", [])
    if not isinstance(references, list):
        raise ValueError("references must be an array")
    for ref in references:
        if not isinstance(ref, dict) or not isinstance(ref.get("role"), str) or not ref["role"].strip():
            raise ValueError("Each selected reference needs a URL and an explicit role")
        canonical_url(ref.get("url"))


def check(data):
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Invalid design document; preserve it rather than resetting")
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        raise ValueError("Project needs a name")
    check_layer(data.get("master"))
    if not isinstance(data.get("pages"), dict):
        raise ValueError("pages must be an object")
    for page, layer in data["pages"].items():
        check_page(page)
        check_layer(layer)
        check_layer(merge_dict(data["master"], layer))


def check_page(page):
    if not isinstance(page, str) or not re.fullmatch(r"[a-z0-9][a-z0-9/_-]*", page):
        raise ValueError("Page names must be lowercase slugs, optionally separated by /")


def load(project):
    data = json.loads((project / ".reference-design" / "design.json").read_text(encoding="utf-8"))
    check(data)
    return data


def write(project, patch=None, name=None, page=None):
    directory = project / ".reference-design"
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / ".design-lock"
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError("Design document is locked by another writer")
    temp = None
    try:
        path = directory / "design.json"
        if name is not None:
            if path.exists():
                raise ValueError("Project design already exists; use update")
            data = {"schema_version": 1, "name": name, "updated_at": now(),
                    "master": {"tokens": {}, "rules": {}, "references": []}, "pages": {}}
        else:
            data = load(project)
            check_layer(patch)
            if page is not None:
                check_page(page)
                data["pages"][page] = merge_dict(data["pages"].get(page, {}), patch)
            else:
                data["master"] = merge_dict(data["master"], patch)
            data["updated_at"] = now()
        check(data)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory,
                                         prefix=".design-", delete=False) as handle:
            temp = Path(handle.name)
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
        return data
    finally:
        if temp is not None and temp.exists():
            temp.unlink()
        lock.rmdir()


def resolve(data, page=None):
    if page is not None:
        if page not in data["pages"]:
            raise ValueError("Page override not found: " + page)
        return merge_dict(data["master"], data["pages"][page])
    return copy.deepcopy(data["master"])


def css(layer):
    items = sorted(token_items(layer.get("tokens", {})))
    return ":root {\n" + "".join("  %s: %s;\n" % item for item in items) + "}\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--name", required=True)
    update = sub.add_parser("update")
    update.add_argument("--file", required=True, help="JSON layer patch, or '-' for stdin")
    update.add_argument("--page")
    for command in ("show", "export-css"):
        child = sub.add_parser(command)
        child.add_argument("--page")
    sub.add_parser("validate")
    args = parser.parse_args()
    if args.command == "init":
        result = write(args.project, name=args.name)
    elif args.command == "update":
        raw = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
        result = write(args.project, json.loads(raw), page=args.page)
    else:
        data = load(args.project)
        if args.command == "validate":
            result = {"valid": True, "pages": len(data["pages"])}
        else:
            result = resolve(data, args.page)
            if args.command == "export-css":
                print(css(result), end="")
                return
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("design-project: " + str(error), file=sys.stderr)
        sys.exit(1)
