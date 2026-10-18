"""Blinding, pairing, evidence requirements, and immutable evaluation inputs."""
import base64
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/reference-design/scripts'))
import design_evaluation as evaluation

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aXioAAAAASUVORK5CYII=')


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.paths = {}
        for condition in ('baseline', 'candidate'):
            directory = self.root / condition
            directory.mkdir()
            (directory / 'shot.png').write_bytes(PNG)
            report = {'capture_version': 1, 'url': 'https://' + condition + '.private.test/',
                      'engine': 'chromium', 'browser_version': 'same-version', 'errors': [],
                      'snapshots': [{'state': 'default', 'viewport': {'width': 390, 'height': 844},
                                     'screenshot': 'shot.png', 'reduced_motion': False, 'issues': []}]}
            path = directory / 'report.json'
            path.write_text(json.dumps(report))
            self.paths[condition] = path
        self.review, self.key = self.root / 'review', self.root / 'private/key.json'

    def prepare(self):
        return evaluation.prepare(self.paths['baseline'], self.paths['candidate'], 'Make a clear booking interface.',
                                  self.review, self.key, seed=3)

    def judgment(self):
        result = json.loads((self.review / 'judgment-template.json').read_text())
        result.update({'reviewer': 'Independent reviewer', 'overall_preference': 'A',
                       'overall_reason': 'A has a clearer hierarchy in the compared view.', 'overall_evidence': ['pair-001']})
        for criterion in result['criteria']:
            criterion.update({'preferred': 'A', 'reason': 'Visible comparison evidence for this criterion.', 'evidence': ['pair-001']})
        path = self.root / 'judgment.json'
        path.write_text(json.dumps(result))
        return path, result

    def test_review_is_blind_and_judgment_unblinds_with_evidence(self):
        self.prepare()
        public = (self.review / 'review.json').read_text() + (self.review / 'index.html').read_text()
        self.assertNotIn('.private.test', public)
        self.assertNotIn('"labels"', public)
        judgment, _ = self.judgment()
        result = evaluation.summarize(self.review, judgment, self.key)
        mapping = json.loads(self.key.read_text())['labels']
        self.assertEqual(result['criterion_votes'][mapping['A']], len(evaluation.CRITERIA))
        self.assertEqual(result['overall_preference'], mapping['A'])

    def test_missing_or_unsupported_judgment_is_rejected(self):
        self.prepare()
        path, judgment = self.judgment()
        variants = []
        incomplete = copy.deepcopy(judgment)
        incomplete['criteria'].pop()
        variants.append(incomplete)
        unsupported = copy.deepcopy(judgment)
        unsupported['criteria'][0]['evidence'] = []
        variants.append(unsupported)
        wrong = copy.deepcopy(judgment)
        wrong['comparison_id'] = 'another-comparison'
        variants.append(wrong)
        for variant in variants:
            path.write_text(json.dumps(variant))
            with self.assertRaises(ValueError):
                evaluation.summarize(self.review, path, self.key)

    def test_modified_screenshot_and_key_placement_are_rejected(self):
        with self.assertRaises(ValueError):
            evaluation.prepare(self.paths['baseline'], self.paths['candidate'], 'Brief', self.review, self.review / 'key.json')
        self.prepare()
        judgment, _ = self.judgment()
        asset = self.review / 'assets/A-001.png'
        asset.write_bytes(asset.read_bytes() + b'changed')
        with self.assertRaises(ValueError):
            evaluation.summarize(self.review, judgment, self.key)

    def test_missing_views_and_capture_errors_cannot_be_hidden(self):
        path = self.paths['candidate']
        data = json.loads(path.read_text())
        for mutate in ('viewport', 'errors'):
            broken = copy.deepcopy(data)
            if mutate == 'viewport':
                broken['snapshots'][0]['viewport']['width'] = 1440
            else:
                broken['errors'] = ['Capture failed']
            path.write_text(json.dumps(broken))
            with self.assertRaises(ValueError):
                self.prepare()

    def test_screenshot_paths_cannot_escape_the_capture(self):
        path = self.paths['baseline']
        data = json.loads(path.read_text())
        data['snapshots'][0]['screenshot'] = '../candidate/shot.png'
        path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            self.prepare()

    def test_shared_references_are_included_and_checked(self):
        reference = self.root / 'reference.png'
        reference.write_bytes(PNG)
        evaluation.prepare(self.paths['baseline'], self.paths['candidate'], 'Use the shared surface reference.',
                           self.review, self.key, reference_images=[reference])
        package = json.loads((self.review / 'review.json').read_text())
        self.assertIn('reference-use', [c['id'] for c in package['criteria']])
        self.assertEqual(len(package['reference_images']), 1)
        judgment, _ = self.judgment()
        evaluation.summarize(self.review, judgment, self.key)
        (self.review / package['reference_images'][0]['path']).write_bytes(PNG + b'changed')
        with self.assertRaises(ValueError):
            evaluation.summarize(self.review, judgment, self.key)


if __name__ == '__main__':
    unittest.main()
