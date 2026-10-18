"""Observe explicit UI actions, DOM/style changes, and optional Chromium JS coverage."""
import json
from pathlib import Path
import re

PROBE = Path(__file__).with_name("interaction_probe.js")
ACTIONS = {"click", "hover", "focus", "press", "scroll"}
KEYS = {"Enter", "Space", "Tab", "Escape", "ArrowDown", "ArrowUp", "ArrowLeft", "ArrowRight", "Home", "End"}


def validate_plan(plan):
    if not isinstance(plan, dict) or plan.get("version") != 1 or set(plan) - {"version", "scenarios"}:
        raise ValueError("Interaction plan needs version 1 and scenarios")
    scenarios = plan.get("scenarios")
    if not isinstance(scenarios, list) or not 1 <= len(scenarios) <= 10:
        raise ValueError("Supply 1..10 interaction scenarios")
    names, total = set(), 0
    for scenario in scenarios:
        if not isinstance(scenario, dict) or set(scenario) - {"name", "steps", "observe", "expect", "settle_ms"}:
            raise ValueError("Unknown interaction scenario fields")
        name = scenario.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", name) or name in names:
            raise ValueError("Scenario names must be unique lowercase slugs")
        names.add(name)
        steps = scenario.get("steps")
        if not isinstance(steps, list) or not 1 <= len(steps) <= 15:
            raise ValueError("Each scenario needs 1..15 steps")
        total += len(steps)
        observed = scenario.get("observe", [])
        if not isinstance(observed, list) or len(observed) > 30 or not all(isinstance(v, str) and v.strip() for v in observed):
            raise ValueError("observe must contain at most 30 CSS selectors")
        settle = scenario.get("settle_ms", 150)
        if type(settle) is not int or not 0 <= settle <= 3000:
            raise ValueError("settle_ms must be 0..3000")
        for step in steps:
            if not isinstance(step, dict) or set(step) - {"action", "selector", "key", "x", "y"}:
                raise ValueError("Unknown interaction step fields")
            if step.get("action") not in ACTIONS:
                raise ValueError("Allowed actions: click, hover, focus, press, scroll")
            allowed = {"action", "x", "y"} if step["action"] == "scroll" else {"action", "selector", "key"} if step["action"] == "press" else {"action", "selector"}
            if set(step) - allowed:
                raise ValueError("Action contains unsupported or ignored parameters")
            if step["action"] != "scroll" and (not isinstance(step.get("selector"), str) or not step["selector"].strip()):
                raise ValueError("Interaction action requires a CSS selector")
            if step["action"] == "press" and step.get("key") not in KEYS:
                raise ValueError("press requires a supported navigation/activation key")
            if step["action"] == "scroll" and any(type(step.get(k, 0)) is not int or abs(step.get(k, 0)) > 100000 for k in ("x", "y")):
                raise ValueError("Scroll coordinates must be bounded integers")
        expectations = scenario.get("expect", [])
        if not isinstance(expectations, list) or len(expectations) > 30:
            raise ValueError("expect must be a list with at most 30 assertions")
        for expectation in expectations:
            if not isinstance(expectation, dict) or set(expectation) - {"selector", "visible", "attribute", "equals"}:
                raise ValueError("Unknown expectation fields")
            if not isinstance(expectation.get("selector"), str) or not expectation["selector"].strip():
                raise ValueError("Expectation requires a selector")
            if "visible" in expectation:
                if type(expectation["visible"]) is not bool or set(expectation) != {"selector", "visible"}:
                    raise ValueError("Visible expectations accept a selector and boolean visible")
            elif not isinstance(expectation.get("attribute"), str) or not isinstance(expectation.get("equals"), str):
                raise ValueError("Attribute expectation needs attribute and string equals")
    if total > 50:
        raise ValueError("Interaction plan exceeds 50 actions")
    return scenarios


def state_changes(before, after):
    old = {(e["selector"], e["index"]): e for e in before["elements"]}
    new = {(e["selector"], e["index"]): e for e in after["elements"]}
    changes = []
    for key in sorted(set(old) | set(new)):
        a, b = old.get(key, {"exists": False}), new.get(key, {"exists": False})
        fields = {}
        for field in ("exists", "visible", "focused", "text", "bounds", "attributes", "styles", "before", "after"):
            av, bv = a.get(field), b.get(field)
            if av == bv:
                continue
            if isinstance(av, dict) and isinstance(bv, dict):
                fields[field] = {prop: {"before": av.get(prop), "after": bv.get(prop)}
                                 for prop in sorted(set(av) | set(bv)) if av.get(prop) != bv.get(prop)}
            else:
                fields[field] = {"before": av, "after": bv}
        if fields:
            changes.append({"selector": key[0], "index": key[1], "changes": fields})
    return changes


def source_slice(source, start, end):
    """CDP offsets count UTF-16 code units, not Python Unicode code points."""
    encoded = source.encode("utf-16-le", errors="surrogatepass")
    prefix = encoded[:start * 2].decode("utf-16-le", errors="replace")
    snippet = encoded[start * 2:min(end, start + 1200) * 2].decode("utf-16-le", errors="replace")
    return prefix.count("\n") + 1, len(prefix.rsplit("\n", 1)[-1].encode("utf-16-le")) // 2 + 1, snippet


class JavaScriptEvidence:
    def __init__(self, page):
        self.client = page.context.new_cdp_session(page)
        self.scripts, self.sources, self.limitations = {}, {}, []
        self.client.on("Debugger.scriptParsed", lambda event: self.scripts.update({event["scriptId"]: event}))
        try:
            self.client.send("Debugger.enable")
            self.client.send("Debugger.setSkipAllPauses", {"skip": True})
            self.client.send("Profiler.enable")
            self.client.send("Profiler.startPreciseCoverage", {"callCount": True, "detailed": True})
        except Exception:
            self.client.detach()
            raise

    def listeners(self, selector):
        expression = "(() => { const nodes=[]; let el=" + ("document.querySelector(" + json.dumps(selector) + ")" if selector else "document.documentElement") + "; while(el && nodes.length<10){nodes.push(el);el=el.parentElement;} return [...nodes,document,window]; })()"
        group = "reference-design-listeners"
        result = self.client.send("Runtime.evaluate", {"expression": expression, "objectGroup": group})
        listeners = []
        try:
            object_id = result.get("result", {}).get("objectId")
            if not object_id:
                return listeners
            properties = self.client.send("Runtime.getProperties", {"objectId": object_id, "ownProperties": True})["result"]
            for prop in properties:
                node_id = prop.get("value", {}).get("objectId")
                if not prop["name"].isdigit() or not node_id:
                    continue
                for item in self.client.send("DOMDebugger.getEventListeners", {"objectId": node_id})["listeners"]:
                    if len(listeners) >= 30:
                        self.limitations.append("Event-listener evidence reached its 30-entry budget.")
                        return listeners
                    metadata = self.scripts.get(item["scriptId"], {})
                    listeners.append({"type": item["type"], "source": metadata.get("url", ""),
                        "line": item["lineNumber"] + 1, "column": item["columnNumber"] + 1,
                        "capture": item["useCapture"], "passive": item["passive"],
                        "evidence_kind": "listener-location", "execution_confirmed": False})
            return listeners
        finally:
            self.client.send("Runtime.releaseObjectGroup", {"objectGroup": group})

    def reset(self):
        self.client.send("Profiler.takePreciseCoverage")

    def executed(self):
        items = []
        for script in self.client.send("Profiler.takePreciseCoverage")["result"]:
            metadata = self.scripts.get(script["scriptId"], {})
            url = script.get("url") or metadata.get("url", "")
            if not url.startswith(("http://", "https://")):
                continue
            functions = [fn for fn in script["functions"] if fn["ranges"] and fn["ranges"][0]["count"] > 0]
            if not functions:
                continue
            source = self.sources.get(script["scriptId"])
            if source is None and len(self.sources) < 6 and metadata.get("length", 0) <= 500000:
                source = self.client.send("Debugger.getScriptSource", {"scriptId": script["scriptId"]}).get("scriptSource", "")
                self.sources[script["scriptId"]] = source
            if source is None:
                self.limitations.append("Some script excerpts were omitted by the source budget; coverage locations remain available.")
            for fn in functions:
                if len(items) >= 20:
                    self.limitations.append("Executed-function evidence reached its 20-entry budget.")
                    return items
                covered = fn["ranges"][0]
                item = {"source": url, "function": fn["functionName"], "start_offset_utf16": covered["startOffset"],
                    "end_offset_utf16": covered["endOffset"], "count": covered["count"], "evidence_kind": "executed-range"}
                if source is not None:
                    line, column, snippet = source_slice(source, covered["startOffset"], covered["endOffset"])
                    item.update({"line": line + metadata.get("startLine", 0),
                                 "column": column + (metadata.get("startColumn", 0) if line == 1 else 0), "snippet": snippet})
                items.append(item)
        return items

    def close(self):
        for method in ("Profiler.stopPreciseCoverage", "Profiler.disable", "Debugger.disable"):
            try:
                self.client.send(method)
            except Exception:
                pass  # A failed action may have navigated or destroyed its execution context.
        try:
            self.client.detach()
        except Exception:
            pass


def trace_scenario(page, scenario, directory, prefix, trace_js=False):
    observe = list(dict.fromkeys(scenario.get("observe", []) + [s["selector"] for s in scenario["steps"] if s.get("selector")]))
    if not observe:
        observe = ["body"]
    api = page.evaluate_handle(PROBE.read_text(encoding="utf-8"), observe)
    trace = {"name": scenario["name"], "settle_ms": scenario.get("settle_ms", 150), "steps": [], "expectations": [], "limitations": [
        "Observed changes and executed code share an action window; background work can appear and causality requires review.",
        "DOM attributes and computed styles do not expose a framework's internal state or original component boundaries.",
        "Source excerpts describe delivered JavaScript; precise coverage changes optimization and is not a performance measurement."]}
    javascript = None
    try:
        if trace_js:
            try:
                javascript = JavaScriptEvidence(page)
            except Exception as error:
                trace["limitations"].append("JavaScript tracing unavailable: " + str(error)[:400])
        for index, step in enumerate(scenario["steps"]):
            before = api.evaluate("api => api.snapshot()")
            before_image, after_image = f"{prefix}-step-{index}-before.png", f"{prefix}-step-{index}-after.png"
            page.screenshot(path=str(directory / before_image))
            entry = {"trigger": step, "before": before, "before_screenshot": before_image, "listener_candidates": [], "executed_functions": []}
            if javascript:
                try:
                    entry["listener_candidates"] = javascript.listeners(step.get("selector"))
                except Exception as error:
                    trace["limitations"].append("Listener inspection unavailable: " + str(error)[:300])
            api.evaluate("api => api.start()")
            coverage_ready = False
            if javascript:
                try:
                    javascript.reset()
                    coverage_ready = True
                except Exception as error:
                    trace["limitations"].append("Coverage reset unavailable: " + str(error)[:300])
            try:
                action = step["action"]
                if action == "scroll":
                    page.evaluate("p => window.scrollTo(p.x, p.y)", {"x": step.get("x", 0), "y": step.get("y", 0)})
                elif action == "press":
                    page.locator(step["selector"]).first.press(step["key"])
                else:
                    getattr(page.locator(step["selector"]).first, action)()
                page.wait_for_timeout(scenario.get("settle_ms", 150))
                if javascript and coverage_ready:
                    try:
                        entry["executed_functions"] = javascript.executed()
                    except Exception as error:
                        trace["limitations"].append("Coverage collection unavailable: " + str(error)[:300])
                entry["observations"] = api.evaluate("api => api.finish()")
                entry["after"] = api.evaluate("api => api.snapshot()")
                entry["changes"] = state_changes(before, entry["after"])
                page.screenshot(path=str(directory / after_image))
                entry["after_screenshot"] = after_image
            except Exception as error:
                entry["error"] = str(error)[:800]
                trace["steps"].append(entry)
                break
            trace["steps"].append(entry)
        for expectation in scenario.get("expect", []):
            locator = page.locator(expectation["selector"]).first
            try:
                if "visible" in expectation:
                    actual = locator.is_visible()
                    expected = expectation["visible"]
                else:
                    actual = locator.get_attribute(expectation["attribute"])
                    expected = expectation["equals"]
                trace["expectations"].append({**expectation, "actual": actual, "passed": actual == expected})
            except Exception as error:
                trace["expectations"].append({**expectation, "passed": False, "error": str(error)[:400]})
        trace["passed"] = not any("error" in step for step in trace["steps"]) and all(e["passed"] for e in trace["expectations"])
        if javascript:
            trace["limitations"] += list(dict.fromkeys(javascript.limitations))
        return trace
    finally:
        try:
            try:
                api.evaluate("api => api.dispose()")
                api.dispose()
            except Exception:
                trace["limitations"].append("The page execution context ended before observer cleanup; inspect action failures.")
        finally:
            if javascript:
                javascript.close()
