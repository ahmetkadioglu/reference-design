#!/usr/bin/env python3
"""Capture reference evidence and basic UI checks with optional Playwright Chromium."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

from reference_memory import canonical_url, now, write_patches
from interaction_trace import trace_scenario, validate_plan

PROBE = Path(__file__).with_name("browser_probe.js")
LIMITATIONS = [
    "Captured screenshots require agent visual review; capture alone is not a completed design analysis.",
    "Checks use representative DOM samples and basic name/contrast heuristics, not a complete accessibility audit.",
    "JavaScript coverage and event-listener evidence require opt-in tracing; original source architecture requires repository inspection.",
    "Cross-origin frames, closed shadow roots, canvas internals, and unvisited routes are not inspected.",
    "Fresh isolated browser contexts do not reuse account sessions; mobile widths are desktop-engine viewport emulation.",
    "Keyboard sampling does not establish complete navigation, focus-trap, or screen-reader coverage.",
    "UI actions run only when explicitly configured; no automatic form filling or submission workflow is provided.",
]


def viewport(value):
    match = re.fullmatch(r"(\d+)x(\d+)", value)
    if not match or any(not 200 <= int(v) <= 4096 for v in match.groups()):
        raise argparse.ArgumentTypeError("Use WIDTHxHEIGHT, with each dimension from 200 to 4096")
    return dict(zip(("width", "height"), map(int, match.groups())))


def keyboard_sample(page, count):
    samples = []
    for _ in range(count):
        page.keyboard.press("Tab")
        samples.append(page.evaluate("""() => {
          const el = document.activeElement, s = getComputedStyle(el);
          return {tag: el.localName, id: el.id || null, role: el.getAttribute('role'),
            outline: s.outline, box_shadow: s.boxShadow, focus_visible: el.matches(':focus-visible')};
        }"""))
    return samples


def capture(browser, url, output, viewports, selectors=(), hover=(), focus=(), timeout=15000,
            wait_for=None, keyboard_steps=8, interaction_plan=None, trace_js=False):
    canonical_url(url)
    scenarios = validate_plan(interaction_plan) if interaction_plan is not None else []
    if trace_js and not scenarios:
        raise ValueError("JavaScript tracing requires an explicit interaction plan")
    stamp = now()
    slug = re.sub(r"[^a-zA-Z0-9.-]", "-", urlsplit(url).hostname or "reference")
    run = output / (slug + "-" + hashlib.sha256(url.encode()).hexdigest()[:8] + "-" + re.sub(r"\D", "", stamp))
    run.mkdir(parents=True, exist_ok=False)
    report = {"capture_version": 1, "url": url, "captured_at": stamp, "title": "",
              "report_path": str((run / "report.json").resolve()), "snapshots": [],
              "errors": [], "limitations": list(LIMITATIONS), "engine": "chromium",
              "browser_version": browser.version}
    states = [("default", None, None)] + [("hover", s, "hover") for s in hover] + [("focus", s, "focus") for s in focus]
    states += [("scenario:" + scenario["name"], None, scenario) for scenario in scenarios]
    probe = PROBE.read_text(encoding="utf-8")
    for size in viewports:
        for motion in ("no-preference", "reduce"):
            context = browser.new_context(viewport=size, reduced_motion=motion, service_workers="block")
            try:
                page = context.new_page()
                page.set_default_timeout(timeout)
                for index, (state, selector, action) in enumerate(states):
                    if isinstance(action, dict):
                        context.close()
                        context = browser.new_context(viewport=size, reduced_motion=motion, service_workers="block")
                        page = context.new_page()
                        page.set_default_timeout(timeout)
                    console_errors, resources = [], []
                    on_error = lambda error: console_errors.append(str(error)[:600]) if len(console_errors) < 100 else None
                    on_console = lambda msg: on_error(msg.text) if msg.type == "error" else None
                    on_response = lambda response: resources.append({"url": response.url, "status": response.status,
                        "type": response.request.resource_type}) if len(resources) < 250 else None
                    page.on("pageerror", on_error)
                    page.on("console", on_console)
                    page.on("response", on_response)
                    try:
                        response = page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                        if response is not None and response.status >= 400:
                            raise ValueError("HTTP " + str(response.status) + "; response is not treated as the reference design")
                        if wait_for:
                            page.locator(wait_for).first.wait_for(state="visible")
                        try:
                            page.wait_for_load_state("load", timeout=min(timeout, 5000))
                        except Exception:
                            report["limitations"].append("Some resources did not finish loading within the bounded wait.")
                        page.evaluate("""() => Promise.race([document.fonts.ready, new Promise(resolve => setTimeout(resolve, 1200))])
                          .then(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))))""")
                        interaction = None
                        if isinstance(action, dict):
                            interaction = trace_scenario(page, action, run, "%dx%d-%s-%d" % (size["width"], size["height"], motion, index), trace_js)
                        elif action:
                            getattr(page.locator(selector).first, action)()
                        shot = page.evaluate(probe, {"selectors": list(selectors), "limit": 100})
                        shot["state"] = state + (":" + selector if selector else "")
                        if interaction is not None:
                            shot["interaction_trace"] = interaction
                            if not interaction["passed"]:
                                report["errors"].append({"viewport": size, "motion": motion, "state": state, "error": "Interaction action or expectation failed; inspect interaction_trace."})
                        shot["console_errors"] = console_errors
                        shot["resources"] = resources
                        image = "%dx%d-%s-%d.png" % (size["width"], size["height"], motion, index)
                        full_page = page.evaluate("document.documentElement.scrollHeight <= 16000")
                        try:
                            page.screenshot(path=str(run / image), full_page=full_page)
                            shot["screenshot"] = image
                            shot["screenshot_full_page"] = full_page
                        except Exception as error:
                            shot["screenshot"] = None
                            report["limitations"].append("Screenshot failed: " + str(error)[:400])
                        if not full_page:
                            report["limitations"].append("Pages taller than 16000 px receive viewport screenshots only.")
                        if state == "default" and motion == "no-preference":
                            shot["keyboard_sample"] = keyboard_sample(page, keyboard_steps)
                        for message in console_errors:
                            shot["issues"].append({"rule": "console-error", "severity": "warning", "selector": "document", "message": message})
                        if shot["inaccessible_stylesheets"]:
                            report["limitations"].append("Some stylesheet rules were inaccessible through CSSOM; inspect their permitted source URLs separately.")
                        if shot["selector_errors"]:
                            report["errors"].extend(shot["selector_errors"])
                        if shot["coverage"]["dom_scan_truncated"] or shot["coverage"]["rule_limit_reached"]:
                            report["limitations"].append("A DOM/rule scan budget was reached; coverage is partial.")
                        report["title"] = shot["title"]
                        report["snapshots"].append(shot)
                    except Exception as error:
                        report["errors"].append({"viewport": size, "motion": motion, "state": state,
                                                 "selector": selector, "error": str(error)[:1000]})
                    finally:
                        page.remove_listener("pageerror", on_error)
                        page.remove_listener("console", on_console)
                        page.remove_listener("response", on_response)
            finally:
                context.close()
    report["limitations"] = list(dict.fromkeys(report["limitations"]))
    report["quality_counts"] = dict(Counter(issue["severity"] for s in report["snapshots"] for issue in s["issues"]))
    report["status"] = "partial" if report["snapshots"] else "unavailable"
    Path(report["report_path"]).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="+")
    parser.add_argument("--output", type=Path, required=True, help="Private directory for unique capture runs")
    parser.add_argument("--viewport", type=viewport, action="append")
    parser.add_argument("--selector", action="append", default=[], help="Representative CSS selector; repeat as needed")
    parser.add_argument("--hover", action="append", default=[])
    parser.add_argument("--focus", action="append", default=[])
    parser.add_argument("--interactions", type=Path, help="Explicit version 1 interaction plan JSON")
    parser.add_argument("--trace-js", action="store_true", help="Collect bounded executed JS ranges and listener locations during planned actions")
    parser.add_argument("--wait-for", help="Wait for a visible CSS selector after navigation")
    parser.add_argument("--timeout", type=int, default=15000, help="Navigation/action timeout in milliseconds")
    parser.add_argument("--keyboard-steps", type=int, default=8)
    parser.add_argument("--memory-root", type=Path, help="Also import runtime facts into this memory store")
    parser.add_argument("--browser-path", default=os.environ.get("REFERENCE_DESIGN_BROWSER_PATH"), help="Optional local Chromium executable")
    parser.add_argument("--fail-on", choices=["never", "warning", "error"], default="never")
    args = parser.parse_args()
    if not 1 <= args.timeout <= 60000 or not 0 <= args.keyboard_steps <= 30:
        parser.error("timeout must be 1..60000 and keyboard-steps must be 0..30")
    for url in args.urls:
        canonical_url(url)
    plan = json.loads(args.interactions.read_text(encoding="utf-8")) if args.interactions else None
    if plan is not None:
        validate_plan(plan)
    if args.trace_js and plan is None:
        parser.error("--trace-js requires --interactions")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ValueError("Optional browser dependency missing. Install requirements-browser.txt, then run: python -m playwright install chromium")
    summaries = []
    failed, quality_failed = False, False
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**({"executable_path": args.browser_path} if args.browser_path else {}))
        try:
            for url in args.urls:
                report = capture(browser, url, args.output,
                                 args.viewport or [{"width": 1440, "height": 900}, {"width": 390, "height": 844}],
                                 args.selector, args.hover, args.focus, args.timeout, args.wait_for, args.keyboard_steps, plan, args.trace_js)
                summary = {"url": url, "status": report["status"], "report": report["report_path"],
                           "snapshots": len(report["snapshots"]), "quality_counts": report["quality_counts"],
                           "memory_saved": False, "capture_errors": len(report["errors"])}
                if args.memory_root:
                    try:
                        write_patches(args.memory_root, [], capture=report)
                        summary["memory_saved"] = True
                    except (ValueError, OSError, KeyError, TypeError) as error:
                        summary["memory_error"] = str(error)
                        failed = True
                summaries.append(summary)
                failed |= bool(report["errors"])
                counts = report["quality_counts"]
                quality_failed |= args.fail_on != "never" and (counts.get("error", 0) > 0 or (args.fail_on == "warning" and counts.get("warning", 0) > 0))
        finally:
            browser.close()
    print(json.dumps(summaries, ensure_ascii=False, indent=2))
    return 1 if failed else 2 if quality_failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print("capture-reference: " + str(error), file=sys.stderr)
        sys.exit(1)
