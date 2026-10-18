"""Source linkage, review gates, retrieval, and atomic mechanism revisions."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/reference-design/scripts'))
import mechanism_memory as mechanisms
import reference_memory as references


class MechanismTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.reference = references.write_patches(self.root, [{'url': 'https://paper.test/', 'title': 'Paper'}])[0]
        self.patch = {'slug': 'layered-card', 'title': 'Layered card', 'summary': 'Decorative grain behind card content',
            'kind': 'surface', 'components': ['card'], 'tags': ['grain'],
            'mechanism': {'description': 'A pseudo-element holds the decorative background.'},
            'recipe': {'steps': ['Place decoration behind the content.', 'Preserve contrast and pointer access.']},
            'sources': [{'url': self.reference['url'], 'selector': '.card::before'}],
            'evidence': [{'kind': 'code-declaration', 'source': 'https://paper.test/style.css',
                          'locator': '.card::before', 'finding': 'A background image is placed on the pseudo-element.'}]}

    def test_drafts_require_deliberate_review_and_retrieval_preserves_history(self):
        mechanisms.upsert(self.root, [self.patch])
        self.assertEqual(mechanisms.search(mechanisms.load(self.root)['mechanisms'], 'gren kart'), [])
        mechanisms.upsert(self.root, [{'slug': 'layered-card', 'status': 'reviewed'}])
        records = mechanisms.load(self.root)['mechanisms']
        found = mechanisms.search(records, 'pütürlü kart', filters={'components': ['card']})
        self.assertEqual(found[0]['id'], 'mech-layered-card')
        self.assertEqual(records[0]['sources'][0]['reference_id'], self.reference['id'])
        self.assertEqual(len(records[0]['history']), 1)
        mechanisms.upsert(self.root, [{'slug': 'layered-card', 'status': 'deprecated'}])
        self.assertEqual(mechanisms.search(mechanisms.load(self.root)['mechanisms'], 'card', include_drafts=True), [])

    def test_reviewed_mechanism_requires_technical_evidence(self):
        patch = copy.deepcopy(self.patch)
        patch['status'] = 'reviewed'
        patch['evidence'][0]['kind'] = 'visual-estimate'
        with self.assertRaises(ValueError):
            mechanisms.upsert(self.root, [patch])
        self.assertFalse((self.root / 'mechanisms.json').exists())

    def test_failed_batch_unknown_sources_and_corrupt_store_are_preserved(self):
        mechanisms.upsert(self.root, [self.patch])
        path = self.root / 'mechanisms.json'
        before = path.read_bytes()
        unknown = copy.deepcopy(self.patch)
        unknown['slug'] = 'unknown-source'
        unknown['sources'][0]['url'] = 'https://missing.test/'
        with self.assertRaises(ValueError):
            mechanisms.upsert(self.root, [{'slug': 'layered-card', 'title': 'Changed'}, unknown])
        self.assertEqual(path.read_bytes(), before)
        (self.root / '.mechanisms-lock').mkdir()
        with self.assertRaises(ValueError):
            mechanisms.upsert(self.root, [self.patch])
        (self.root / '.mechanisms-lock').rmdir()
        path.write_text('{broken')
        with self.assertRaises(ValueError):
            mechanisms.upsert(self.root, [self.patch])
        self.assertEqual(path.read_text(), '{broken')

    def test_source_id_cannot_be_assigned_to_another_reference(self):
        self.patch['sources'][0]['reference_id'] = 'ref-another-source'
        with self.assertRaises(ValueError):
            mechanisms.upsert(self.root, [self.patch])

    def test_extractor_labels_surface_evidence_without_inventing_the_asset_mechanism(self):
        report = {'capture_version': 1, 'url': 'https://paper.test/', 'snapshots': [{
            'state': 'default', 'viewport': {'width': 1440, 'height': 900},
            'elements': [{'selector': '.card', 'styles': {'display': 'block'},
                          'before': {'content': '""', 'background-image': 'url(noise.svg)', 'opacity': '.04'}}]}]}
        drafts = mechanisms.extract(report)
        self.assertEqual(len(drafts), 1)
        self.assertEqual(drafts[0]['status'], 'draft')
        self.assertNotIn('turbulence', drafts[0]['mechanism']['description'].lower())
        self.assertEqual(drafts[0]['sources'][0]['selector'], '.card::before')


if __name__ == '__main__':
    unittest.main()
