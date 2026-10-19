import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/reference-design/scripts"
sys.path.insert(0, str(SCRIPTS))
import intake_inventory as inventory
import reference_memory as memory


def finding(feature="Card geometry"):
    return {"feature": feature, "observation": "The source declares 24px card padding.",
            "mechanism": "The card's padding property separates content from the border.",
            "reuse": "Adapt internal spacing to the target product's content density.",
            "evidence": [{"kind": "code-declaration", "source": "supplied.css",
                          "locator": ".card", "finding": "padding:24px"}]}


def complete_patch(url="https://example.test/light"):
    patch = inventory.template(url, "source-only")
    for name, item in patch["technical"]["intake"]["categories"].items():
        item.update(status="not_observed", checks=["Read the supplied source and scoped selectors for " + name],
                    reason="No " + name + " feature was present in the supplied source snapshot.")
    patch["technical"]["intake"]["categories"]["cards"].update(
        status="inspected", findings=[finding()], reason="")
    patch.update(summary="A source-inspected card layout.", evidence=finding()["evidence"])
    return patch


class IntakeTests(unittest.TestCase):
    def test_theme_only_and_legacy_records_need_component_inventory(self):
        record = {"url": "https://example.test/light", "summary": "Light and minimal",
                  "visual": {"theme": "light"}, "technical": {}}
        self.assertFalse(inventory.review(record)["ready"])
        record["technical"]["intake"] = {"version": 1, "scope": "site",
            "categories": {"surfaces": {"status": "inspected", "checks": ["Looked at the page"],
                                      "findings": [{"feature": "Dark glowing style"}]}}}
        result = inventory.review(record)
        self.assertFalse(result["ready"])
        self.assertTrue(any("icons: missing" in error for error in result["errors"]))
        self.assertTrue(any("typography: missing" in error for error in result["errors"]))

    def test_template_is_pending_and_has_every_category(self):
        patch = inventory.template("https://EXAMPLE.test/?utm_source=test")
        self.assertEqual(set(patch["technical"]["intake"]["categories"]), set(inventory.CATEGORIES))
        self.assertEqual(patch["url"], "https://example.test/")
        self.assertFalse(inventory.review(patch)["ready"])

    def test_structured_source_findings_are_valid_without_runtime_claims(self):
        patch = complete_patch()
        result = inventory.review(patch)
        self.assertTrue(result["ready"], result)
        self.assertFalse(result["partial"])
        self.assertIn("not the truth", result["limitation"])

    def test_unknown_mechanisms_and_unavailable_layers_stay_partial(self):
        patch = complete_patch()
        card = patch["technical"]["intake"]["categories"]["cards"]["findings"][0]
        card["mechanism"] = None
        card["evidence"][0]["kind"] = "visual-estimate"
        patch["technical"]["intake"]["categories"]["motion"].update(
            status="unavailable", reason="No permitted rendered browser was available.",
            checks=["Checked available host tools for scroll and runtime inspection."])
        result = inventory.review(patch)
        self.assertTrue(result["ready"], result)
        self.assertTrue(result["partial"])
        self.assertIn("cards", result["limited_categories"])
        self.assertIn("motion", result["limited_categories"])

    def test_inspected_empty_or_unlinked_findings_are_rejected(self):
        for field, value in [("findings", []), ("checks", [])]:
            patch = complete_patch()
            patch["technical"]["intake"]["categories"]["cards"][field] = value
            self.assertFalse(inventory.review(patch)["ready"])
        patch = complete_patch()
        patch["technical"]["intake"]["categories"]["cards"]["findings"][0]["evidence"][0].pop("locator")
        self.assertFalse(inventory.review(patch)["ready"])

    def test_visual_estimates_cannot_establish_implementation(self):
        patch = complete_patch()
        patch["technical"]["intake"]["categories"]["cards"]["findings"][0]["evidence"][0]["kind"] = "visual-estimate"
        self.assertFalse(inventory.review(patch)["ready"])

    def test_general_site_cannot_skip_categories_or_invent_absence(self):
        patch = complete_patch()
        patch["technical"]["intake"]["scope"] = "site"
        category = patch["technical"]["intake"]["categories"]["icons"]
        category.update(status="out_of_scope", reason="Not highlighted by the user")
        self.assertFalse(inventory.review(patch)["ready"])
        category.update(status="not_observed", reason="", checks=[])
        self.assertFalse(inventory.review(patch)["ready"])

    def test_inventory_upsert_and_component_search_preserve_preferences_and_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory.write_patches(root, [{"url": "https://example.test/light",
                "summary": "Light minimalist", "preferences": {"liked": ["card spacing"]}}])
            patch = complete_patch()
            patch["components"] = ["card"]
            memory.write_patches(root, [patch])
            record = memory.load(root)["references"][0]
            self.assertEqual(record["preferences"]["liked"], ["card spacing"])
            self.assertEqual(len(record["history"]), 1)
            self.assertTrue(inventory.review(record)["ready"])
            self.assertEqual(memory.search([record], "card padding", 5)[0]["id"], record["id"])

    def test_cli_checks_each_saved_reference_and_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            records = memory.write_patches(root, [complete_patch(), {"url": "https://example.test/dark",
                "summary": "Dark glowing", "technical": {}}])
            before = (root / "store.json").read_bytes()
            command = [sys.executable, str(SCRIPTS / "intake_inventory.py"), "--root", str(root), "review"]
            valid = subprocess.run(command + [records[0]["id"]], capture_output=True, text=True)
            self.assertEqual(valid.returncode, 0, valid.stderr)
            batch = subprocess.run(command + [r["id"] for r in records], capture_output=True, text=True)
            self.assertEqual(batch.returncode, 1, batch.stderr)
            self.assertEqual([r["ready"] for r in json.loads(batch.stdout)], [True, False])
            self.assertEqual((root / "store.json").read_bytes(), before)

    def test_contrasting_themes_remain_retrievable_by_component_and_mechanism(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            light = complete_patch("https://example.test/light")
            light["visual"] = {"theme": "light minimal"}
            dark = complete_patch("https://example.test/dark")
            dark["visual"] = {"theme": "dark glowing"}
            motion = finding("Scroll reveal")
            motion.update(observation="The supplied script declares an IntersectionObserver with threshold .2.",
                          mechanism="IntersectionObserver sets data-visible once the section intersects.",
                          reuse="Adapt the reveal trigger to the target product, respecting reduced motion.")
            motion["evidence"] = [{"kind": "source-code", "source": "intake-dark.html",
                "locator": "new IntersectionObserver", "finding": "Sets data-visible=true at threshold .2."}]
            dark["technical"]["intake"]["categories"]["motion"].update(
                status="inspected", checks=["Read the supplied observer and .reveal CSS rules"],
                findings=[motion], reason="")
            dark["components"] = ["card", "icon"]
            dark["techniques"] = ["scroll reveal"]
            memory.write_patches(root, [light, dark])
            records = memory.load(root)["references"]
            self.assertTrue(all(inventory.review(r)["ready"] for r in records))
            self.assertEqual(memory.search(records, "scroll reveal", 5)[0]["url"], dark["url"])
            self.assertEqual(len(memory.search(records, "card padding", 5)), 2)


if __name__ == "__main__":
    unittest.main()
