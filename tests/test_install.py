import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('reference_design_installer', ROOT / 'tools/install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def targets(self, agents=('claude-code',), scope='project'):
        return installer.destinations(agents, scope, self.root / 'project', self.root / 'home')

    def test_all_profiles_install_complete_bundle_without_private_data(self):
        source = self.root / 'source'
        shutil.copytree(installer.SOURCE, source, ignore=shutil.ignore_patterns('__pycache__'))
        (source / 'references/memory').mkdir(parents=True, exist_ok=True)
        (source / 'references/memory/store.json').write_text('{"personal": true}')
        (source / 'references/private-notes.md').write_text('Private unlisted notes')
        names = list(installer.profiles())
        targets = self.targets(names)
        self.assertLess(len(targets), len(names))  # Shared locations are written once.
        installer.install(targets, source=source)
        expected = installer.bundle(source)
        for item in targets:
            target = item['path']
            self.assertEqual(installer.read_json(target / installer.RECEIPT)['files'], expected)
            for name, sha in expected.items():
                self.assertEqual(installer.digest(target / name), sha)
            self.assertFalse((target / 'references/memory').exists())
            self.assertFalse((target / 'references/private-notes.md').exists())
            subprocess.run([sys.executable, str(target / 'scripts/reference_memory.py'), '--root',
                            str(self.root / 'private-memory'), 'list'], check=True, capture_output=True)
        self.assertTrue(all(i['matches_checkout'] for i in installer.doctor(targets)['installations']))

    def test_project_and_user_scope_are_distinct_and_paths_with_spaces_work(self):
        project = self.root / 'project with spaces'
        user = installer.destinations(['github-copilot', 'opencode', 'antigravity'], 'user', project, self.root / 'home')
        self.assertEqual(user[0]['path'], self.root / 'home/.copilot/skills/reference-design')
        self.assertEqual(user[1]['path'], self.root / 'home/.config/opencode/skills/reference-design')
        self.assertEqual(user[2]['path'], self.root / 'home/.gemini/config/skills/reference-design')
        targets = installer.destinations(['github-copilot'], 'project', project)
        installer.install(targets)
        self.assertTrue((project / '.github/skills/reference-design/SKILL.md').is_file())
        self.assertFalse((self.root / 'home').exists())

    def test_dry_run_writes_nothing_and_batch_conflict_prevents_installation(self):
        targets = self.targets(['codex', 'claude-code'])
        installer.install(targets, dry_run=True)
        self.assertFalse((self.root / 'project').exists())
        targets[1]['path'].mkdir(parents=True)
        (targets[1]['path'] / 'personal.txt').write_text('Keep me')
        with self.assertRaises(ValueError): installer.install(targets)
        self.assertFalse(targets[0]['path'].exists())
        with self.assertRaises(ValueError): installer.install(targets, update=True)

    def test_update_preserves_memory_and_custom_files_and_removes_old_managed_file(self):
        targets = self.targets()
        installer.install(targets)
        target = targets[0]['path']
        memory = target / 'references/memory'
        memory.mkdir()
        (memory / 'store.json').write_bytes(b'personal references\n')
        (memory / 'mechanisms.json').write_bytes(b'personal mechanisms\n')
        (target / 'custom.txt').write_text('local adaptation')
        legacy = target / 'scripts/retired.py'
        legacy.write_text('retired')
        receipt = installer.read_json(target / installer.RECEIPT)
        receipt['files']['scripts/retired.py'] = installer.digest(legacy)
        (target / installer.RECEIPT).write_text(json.dumps(receipt))
        installer.install(targets, update=True)
        self.assertEqual((memory / 'store.json').read_bytes(), b'personal references\n')
        self.assertEqual((memory / 'mechanisms.json').read_bytes(), b'personal mechanisms\n')
        self.assertEqual((target / 'custom.txt').read_text(), 'local adaptation')
        self.assertFalse(legacy.exists())

    def test_modified_managed_file_and_new_resource_collision_are_preserved(self):
        targets = self.targets()
        installer.install(targets)
        target = targets[0]['path']
        skill = target / 'SKILL.md'
        skill.write_text('local changes')
        with self.assertRaises(ValueError): installer.install(targets, update=True)
        self.assertEqual(skill.read_text(), 'local changes')
        self.assertFalse(installer.doctor(targets)['installations'][0]['matches_checkout'])
        shutil.copyfile(installer.SOURCE / 'SKILL.md', skill)
        receipt = installer.read_json(target / installer.RECEIPT)
        receipt['files'].pop('references/agent-portability.md')
        (target / installer.RECEIPT).write_text(json.dumps(receipt))
        with self.assertRaises(ValueError): installer.install(targets, update=True)

    def test_failed_replacement_restores_previous_installation(self):
        targets = self.targets()
        installer.install(targets)
        target = targets[0]['path']
        (target / 'custom.txt').write_text('preserve during rollback')
        original = Path.rename

        def fail_staged(path, destination):
            if path.name == 'staged': raise OSError('simulated replacement failure')
            return original(path, destination)

        with patch.object(Path, 'rename', fail_staged):
            with self.assertRaises(OSError): installer.install(targets, update=True)
        self.assertEqual((target / 'custom.txt').read_text(), 'preserve during rollback')
        self.assertTrue(installer.doctor(targets)['installations'][0]['matches_checkout'])
        self.assertFalse((target.parent / '.reference-design.install-lock').exists())

    def test_inventory_and_receipt_cannot_escape_or_publish_memory(self):
        for value in ['.', '../secret', '/tmp/secret', 'scripts/../../secret', 'scripts\\secret',
                      'references/memory/store.json', 'scripts/__pycache__/file.pyc', 'C:/secret', None]:
            with self.assertRaises(ValueError): installer.relative_path(value)
        targets = self.targets()
        installer.install(targets)
        receipt_path = targets[0]['path'] / installer.RECEIPT
        receipt = installer.read_json(receipt_path)
        receipt['files']['../secret'] = 'anything'
        receipt_path.write_text(json.dumps(receipt))
        with self.assertRaises(ValueError): installer.install(targets, update=True)

    def test_failed_rollback_keeps_recoverable_backup(self):
        targets = self.targets()
        installer.install(targets)
        target = targets[0]['path']
        (target / 'custom.txt').write_text('recoverable private data')
        original = Path.rename

        def fail_replacement_and_restore(path, destination):
            if path.name in {'staged', 'previous'}: raise OSError('simulated filesystem failure')
            return original(path, destination)

        with patch.object(Path, 'rename', fail_replacement_and_restore):
            with self.assertRaisesRegex(OSError, 'preserved installation'):
                installer.install(targets, update=True)
        backups = list(target.parent.glob('.reference-design-*/previous/custom.txt'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'recoverable private data')

    @unittest.skipIf(sys.platform == 'win32', 'Symlinks can require Windows developer privileges')
    def test_symlink_installations_are_not_replaced(self):
        target = self.targets()[0]['path']
        elsewhere = self.root / 'elsewhere'
        elsewhere.mkdir()
        target.parent.mkdir(parents=True)
        target.symlink_to(elsewhere, target_is_directory=True)
        with self.assertRaises(ValueError): installer.install(self.targets(), update=True)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_bundle_inventory_tracks_all_distribution_resources(self):
        expected = {str(p.relative_to(installer.SOURCE).as_posix()) for p in installer.SOURCE.rglob('*')
                    if p.is_file() and 'memory' not in p.relative_to(installer.SOURCE).parts
                    and '__pycache__' not in p.parts and p.suffix not in {'.pyc', '.pyo'}}
        self.assertEqual(set(installer.bundle()), expected)
        text = (ROOT / 'docs/agent-compatibility.md').read_text(encoding='utf-8')
        for key in installer.profiles(): self.assertIn('`' + key + '`', text)

    def test_cli_reports_missing_install_and_rejects_unknown_agent(self):
        cmd = [sys.executable, str(ROOT / 'tools/install.py')]
        missing = subprocess.run(cmd + ['doctor', '--agent', 'codex', '--project', str(self.root)], capture_output=True, text=True)
        self.assertEqual(missing.returncode, 1)
        self.assertFalse(json.loads(missing.stdout)['installations'][0]['complete'])
        unknown = subprocess.run(cmd + ['install', '--agent', 'unknown-agent'], capture_output=True)
        self.assertNotEqual(unknown.returncode, 0)


if __name__ == '__main__':
    unittest.main()
