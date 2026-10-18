"""Memory persistence and retrieval regressions; every test uses temporary storage."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/reference-design/scripts"
sys.path.insert(0, str(SCRIPTS))
import reference_memory as memory


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def put(self, **values):
        return memory.write_patches(self.root, [values])[0]

    def test_duplicate_history_and_separate_process(self):
        first = self.put(url="https://PAPER.test:443/?utm_source=test", title="Paper")
        self.put(url="https://paper.test/?fbclid=test", tags=["card"], preferences={"liked": ["Texture"]})
        self.put(url="https://paper.test/", tags=["card", "grain"], technical={"surface": "SVG noise"})
        result = subprocess.run([sys.executable, str(SCRIPTS / "reference_memory.py"), "--root", str(self.root), "get", first["id"], "--history"], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        self.assertEqual(len(data["history"]), 2)
        self.assertEqual(data["tags"], ["card", "grain"])
        self.assertEqual(data["preferences"]["liked"], ["Texture"])
        self.assertEqual(len(memory.load(self.root)["references"]), 1)

    def test_routes_and_credentials(self):
        self.assertEqual(memory.canonical_url("https://example.test/?view=compact&utm_a=x#/cards"), "https://example.test/?view=compact#/cards")
        with self.assertRaises(ValueError):
            memory.canonical_url("https://user:password@example.test/")

    def test_atomic_failures_lock_and_corruption(self):
        self.put(url="https://valid.test/")
        before = (self.root / "store.json").read_bytes()
        for patches in [[{"url": "https://another.test/"}, {"url": "ftp://bad.test/"}],
                        [{"url": "https://unverified.test/", "status": "analyzed"}]]:
            with self.assertRaises(ValueError):
                memory.write_patches(self.root, patches)
            self.assertEqual((self.root / "store.json").read_bytes(), before)
        (self.root / ".write-lock").mkdir()
        with self.assertRaises(ValueError):
            self.put(url="https://locked.test/")
        (self.root / ".write-lock").rmdir()
        (self.root / "store.json").write_text("{broken")
        with self.assertRaises(ValueError):
            self.put(url="https://repair.test/")
        self.assertEqual((self.root / "store.json").read_text(), "{broken")

    def test_bm25_relevance_aliases_facets_and_statuses(self):
        self.put(url="https://focused.test/", title="Appointment cards", status="partial",
                 summary="Textured appointment booking", tags=["grain"], domains=["booking"], components=["card"])
        self.put(url="https://verbose.test/", status="partial", summary="card " * 600 + " unrelated " * 800)
        self.put(url="https://blocked.test/", status="unavailable", title="Appointment cards")
        records = memory.load(self.root)["references"]
        results = memory.search(records, "randevu pütürlü kart", 8, explain=True)
        self.assertEqual(results[0]["url"], "https://focused.test/")
        self.assertIn("grain", results[0]["matches"])
        self.assertFalse(any(r["status"] == "unavailable" for r in results))
        filtered = memory.search(records, "kart", 8, filters={"domains": ["randevu"], "components": ["card"]})
        self.assertEqual([r["url"] for r in filtered], ["https://focused.test/"])
        self.assertEqual(memory.search(records, "", 8), [])

    def test_legacy_store_without_facets_remains_readable(self):
        self.put(url="https://legacy.test/", status="partial", tags=["card"])
        data = memory.load(self.root)
        for field in memory.FACETS:
            del data["references"][0][field]
        (self.root / "store.json").write_text(json.dumps(data))
        loaded = memory.load(self.root)
        self.assertEqual(memory.search(loaded["references"], "kart", 1)[0]["components"], [])
        self.put(url="https://legacy.test/", components=["card"])

    def test_capture_import_preserves_preferences_and_evidence(self):
        original = self.put(url="https://paper.test/", title="My preferred name", status="analyzed", summary="Previously reviewed",
                            technical={"surface": "SVG"}, visual={"cards": "Warm"},
                            evidence=[{"kind": "source-code", "source": "styles.css", "finding": "SVG layer"}],
                            preferences={"liked": ["Cards"]})
        report = {"capture_version": 1, "url": original["url"], "captured_at": memory.now(), "title": "Live title",
                  "snapshots": [{"elements": [], "viewport": {"width": 390}, "state": "default"}],
                  "limitations": ["Visual review still needed"]}
        memory.write_patches(self.root, [], capture=report)
        current = memory.load(self.root)["references"][0]
        self.assertEqual(current["status"], "partial")
        self.assertEqual(current["title"], "My preferred name")
        self.assertEqual(current["preferences"], original["preferences"])
        self.assertEqual(current["technical"]["surface"], "SVG")
        self.assertEqual(len(current["evidence"]), 2)
        report["snapshots"] = []
        memory.write_patches(self.root, [], capture=report)
        self.assertEqual(memory.load(self.root)["references"][0]["status"], "partial")


if __name__ == "__main__":
    unittest.main()
