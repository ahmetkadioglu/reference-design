"""Interaction-plan and source-location invariants independent of a browser."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/reference-design/scripts"))
import interaction_trace as trace


class InteractionTests(unittest.TestCase):
    def test_explicit_plan_validation_and_budget(self):
        plan = {"version": 1, "scenarios": [{"name": "menu", "observe": ["#menu"],
                "steps": [{"action": "click", "selector": "#trigger"}],
                "expect": [{"selector": "#menu", "visible": True}]}]}
        self.assertEqual(len(trace.validate_plan(plan)), 1)
        for step in [{"action": "evaluate", "selector": "body"}, {"action": "click"},
                     {"action": "press", "selector": "body", "key": "Control+L"}]:
            broken = copy.deepcopy(plan)
            broken["scenarios"][0]["steps"] = [step]
            with self.assertRaises(ValueError):
                trace.validate_plan(broken)
        plan["scenarios"] *= 2
        with self.assertRaises(ValueError):
            trace.validate_plan(plan)

    def test_state_diff_keeps_attribute_and_layer_changes(self):
        before = {"elements": [{"selector": "#menu", "index": 0, "exists": True, "visible": False,
                  "attributes": {"hidden": ""}, "styles": {"display": "none"}}]}
        after = {"elements": [{"selector": "#menu", "index": 0, "exists": True, "visible": True,
                 "attributes": {}, "styles": {"display": "grid"}}]}
        result = trace.state_changes(before, after)[0]
        self.assertEqual(result["changes"]["visible"], {"before": False, "after": True})
        self.assertEqual(result["changes"]["styles"]["display"]["after"], "grid")

    def test_utf16_offsets_map_back_to_source(self):
        source = '// 🌿\nfunction openMenu() { return true; }'
        prefix = source[:source.index('function')]
        start = len(prefix.encode('utf-16-le')) // 2
        line, column, snippet = trace.source_slice(source, start, len(source.encode('utf-16-le')) // 2)
        self.assertEqual((line, column), (2, 1))
        self.assertTrue(snippet.startswith('function openMenu'))
        source = '/* 🌿 */ function run() {}'
        start = len(source[:source.index('function')].encode('utf-16-le')) // 2
        self.assertEqual(trace.source_slice(source, start, start + 20)[:2], (1, start + 1))


if __name__ == '__main__':
    unittest.main()
