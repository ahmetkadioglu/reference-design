"""Project inheritance, exports, and preservation regressions."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/reference-design/scripts"))
import design_project as project


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        project.write(self.root, name="Booking")

    def test_inheritance_role_and_css_export(self):
        project.write(self.root, {"tokens": {"color": {"accent": "#2563eb", "text": "#14213d"}, "space": {"card": "24px"}},
                                  "rules": {"theme": "light"},
                                  "references": [{"url": "https://paper.test/", "role": "card texture"}]})
        project.write(self.root, {"tokens": {"space": {"card": "32px"}}}, page="booking/details")
        data = project.load(self.root)
        page = project.resolve(data, "booking/details")
        self.assertEqual(page["tokens"]["space"]["card"], "32px")
        self.assertEqual(data["master"]["tokens"]["space"]["card"], "24px")
        self.assertEqual(page["references"][0]["role"], "card texture")
        self.assertIn("--color-accent: #2563eb;", project.css(page))
        self.assertIn("--space-card: 32px;", project.css(page))
        with self.assertRaises(ValueError):
            project.resolve(data, "missing")

    def test_invalid_update_preserves_existing_file(self):
        path = self.root / ".reference-design/design.json"
        before = path.read_bytes()
        for patch in [{"tokens": {"color": "red; } body { color:black"}},
                      {"tokens": {"x-y": "1px", "x": {"y": "2px"}}},
                      {"references": [{"url": "https://paper.test/"}]}]:
            with self.assertRaises(ValueError):
                project.write(self.root, patch)
            self.assertEqual(path.read_bytes(), before)
        with self.assertRaises(ValueError):
            project.write(self.root, name="Overwrite")
        path.write_text("{broken")
        with self.assertRaises(ValueError):
            project.write(self.root, {"rules": {"theme": "dark"}})
        self.assertEqual(path.read_text(), "{broken")


if __name__ == "__main__":
    unittest.main()
