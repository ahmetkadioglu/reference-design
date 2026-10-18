"""Real browser integration checks against local, deterministic fixtures."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Thread
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/reference-design/scripts"))
import capture_reference as collector
import reference_memory as memory
import mechanism_memory as mechanisms


@unittest.skipUnless(os.environ.get("REFERENCE_DESIGN_BROWSER_TESTS") == "1", "Set REFERENCE_DESIGN_BROWSER_TESTS=1 with Playwright Chromium installed")
class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        class Handler(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(ROOT / "tests/fixtures")))
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:%d/" % cls.server.server_port
        cls.playwright = sync_playwright().start()
        path = os.environ.get("REFERENCE_DESIGN_BROWSER_PATH")
        cls.browser = cls.playwright.chromium.launch(**({"executable_path": path} if path else {}))

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def test_capture_styles_pseudo_layers_responsive_and_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = collector.capture(self.browser, self.base + "reference.html", root,
                [{"width": 1440, "height": 900}, {"width": 390, "height": 844}],
                selectors=[".cards", ".card", "h1", "button", ".animation"], hover=["#choose"], keyboard_steps=3)
            self.assertFalse(report["errors"], report["errors"])
            self.assertEqual(len(report["snapshots"]), 8)
            defaults = [s for s in report["snapshots"] if s["state"] == "default" and not s["reduced_motion"]]
            columns = [next(e for e in s["elements"] if e["selector"] == "#booking")["styles"]["grid-template-columns"] for s in defaults]
            self.assertEqual(len(columns[0].split()), 2)
            self.assertEqual(len(columns[1].split()), 1)
            self.assertTrue(any("noise.svg" in e["before"]["background-image"] for e in defaults[0]["elements"]))
            self.assertTrue(any(r["conditions"] for s in report["snapshots"] for r in s["rules"]))
            self.assertTrue(any(s["scripts"][0]["url"].endswith("reference.js") for s in defaults))
            hovered = [s for s in report["snapshots"] if s["state"] == "hover:#choose"]
            self.assertTrue(all(next(e for e in s["elements"] if e["selector"] == "#choose")["styles"]["transform"] != "none" for s in hovered))
            self.assertTrue(all((Path(report["report_path"]).parent / s["screenshot"]).exists() for s in report["snapshots"]))
            self.assertFalse(any(i["rule"] == "reduced-motion-review" for s in report["snapshots"] for i in s["issues"]))
            memory.write_patches(root / "memory", [], capture=report)
            record = memory.load(root / "memory")["references"][0]
            self.assertEqual(record["status"], "partial")
            self.assertEqual(record["visual"], {})
            self.assertTrue(memory.search([record], "Booking", 1))

    def test_quality_failures_and_cli_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(ROOT / "skills/reference-design/scripts/capture_reference.py"),
                self.base + "broken.html", "--output", directory, "--viewport", "390x844", "--fail-on", "error", "--keyboard-steps", "0"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
            report = json.loads(Path(json.loads(result.stdout)[0]["report"]).read_text())
            rules = {issue["rule"] for s in report["snapshots"] for issue in s["issues"]}
            self.assertTrue({"page-overflow", "control-label", "interactive-name", "image-alt", "text-contrast", "reduced-motion-review", "console-error"} <= rules, rules)

    def test_failed_reference_and_invalid_selector_are_not_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            report = collector.capture(self.browser, self.base + "missing.html", Path(directory), [{"width":390,"height":844}], keyboard_steps=0)
            self.assertEqual(report["snapshots"], [])
            self.assertTrue(report["errors"])
            self.assertEqual(report["status"], "unavailable")
            report = collector.capture(self.browser, self.base + "reference.html", Path(directory), [{"width":390,"height":844}], selectors=["#"], keyboard_steps=0)
            self.assertTrue(report["errors"])

    def test_batch_continues_and_saves_each_reference_after_http_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = subprocess.run([sys.executable, str(ROOT / "skills/reference-design/scripts/capture_reference.py"),
                self.base + "missing.html", self.base + "reference.html", "--output", str(root / "captures"),
                "--memory-root", str(root / "memory"), "--viewport", "390x844", "--keyboard-steps", "0"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            summaries = json.loads(result.stdout)
            self.assertEqual([s["status"] for s in summaries], ["unavailable", "partial"])
            self.assertTrue(all(s["memory_saved"] for s in summaries))
            records = memory.load(root / "memory")["references"]
            self.assertEqual(len(records), 2)
            self.assertTrue(any("HTTP 404" in item for r in records for item in r["limitations"]))

    def test_interaction_chain_and_extracted_mechanisms(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = json.loads((ROOT / 'tests/fixtures/interactions.json').read_text())
            report = collector.capture(self.browser, self.base + 'interactive.html', root,
                [{"width": 390, "height": 844}], keyboard_steps=0, interaction_plan=plan, trace_js=True)
            self.assertFalse(report['errors'], report['errors'])
            traces = [s['interaction_trace'] for s in report['snapshots'] if 'interaction_trace' in s]
            self.assertEqual(len(traces), 8)
            self.assertTrue(all(t['passed'] for t in traces))
            menu = next(t for t in traces if t['name'] == 'menu-open')['steps'][0]
            self.assertTrue(any(c['selector'] == '#menu-toggle' and 'aria-expanded' in c['changes'].get('attributes', {}) for c in menu['changes']))
            self.assertTrue(any(c['selector'] == '#menu' and c['changes'].get('visible', {}).get('after') is True for c in menu['changes']))
            self.assertTrue(any(e['type'] == 'click' for e in menu['observations']['events']))
            self.assertTrue(any(m['attribute'] == 'hidden' for m in menu['observations']['mutations']))
            function = next(f for f in menu['executed_functions'] if f['function'] == 'toggleMenu')
            self.assertEqual(function['line'], 2)
            self.assertTrue(function['source'].endswith('/interactive.js'))
            self.assertIn("trigger.setAttribute", function['snippet'])
            self.assertTrue(any(l['source'].endswith('/interactive.js') for l in menu['listener_candidates']))
            drafts = mechanisms.extract(report)
            self.assertTrue({'surface', 'typography', 'interaction'} <= {d['kind'] for d in drafts})
            self.assertTrue(all(d['status'] == 'draft' for d in drafts))
            memory.write_patches(root / 'memory', [], capture=report)
            mechanisms.upsert(root / 'memory', drafts)
            self.assertFalse(mechanisms.search(mechanisms.load(root / 'memory')['mechanisms'], 'surface'))
            self.assertTrue(mechanisms.search(mechanisms.load(root / 'memory')['mechanisms'], 'surface', include_drafts=True))

    def test_failed_expectation_is_preserved_and_cannot_be_a_learned_transition(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = {'version': 1, 'scenarios': [{'name': 'wrong-menu-expectation', 'observe': ['#menu'],
                'steps': [{'action': 'click', 'selector': '#menu-toggle'}],
                'expect': [{'selector': '#menu', 'visible': False}]}]}
            report = collector.capture(self.browser, self.base + 'interactive.html', root,
                [{'width': 390, 'height': 844}], keyboard_steps=0, interaction_plan=plan)
            self.assertTrue(report['errors'])
            traces = [s['interaction_trace'] for s in report['snapshots'] if 'interaction_trace' in s]
            self.assertTrue(all(not t['passed'] for t in traces))
            self.assertTrue(all(t['steps'][0]['changes'] for t in traces))
            self.assertFalse(any(d['kind'] == 'interaction' for d in mechanisms.extract(report)))
            with self.assertRaises(ValueError):
                collector.capture(self.browser, self.base + 'interactive.html', root,
                    [{'width': 390, 'height': 844}], keyboard_steps=0, trace_js=True)


if __name__ == "__main__":
    unittest.main()
