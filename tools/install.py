#!/usr/bin/env python3
"""Install the same Reference Design bundle into documented agent skill locations."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'skills/reference-design'
RECEIPT = '.reference-design-install.json'
SKILL = 'reference-design'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_path(value):
    if not isinstance(value, str):
        raise ValueError('Bundle paths must be strings')
    path = PurePosixPath(value)
    if not value or not path.parts or path.is_absolute() or '..' in path.parts or '\\' in value or ':' in value or str(path) != value:
        raise ValueError('Bundle paths must be normalized relative paths')
    if path.parts[0] not in {'SKILL.md', 'requirements-browser.txt', 'agents', 'assets', 'references', 'scripts'}:
        raise ValueError('Unexpected bundle path: ' + value)
    if 'memory' in path.parts or '__pycache__' in path.parts or path.suffix in {'.pyc', '.pyo'}:
        raise ValueError('Private memory and caches cannot be bundled')
    return Path(*path.parts)


def regular_file(root, relative):
    path = root / relative
    if any(p.is_symlink() for p in [path, *path.parents] if p != root and p.is_relative_to(root)):
        raise ValueError('Managed resource paths cannot be symbolic links: ' + str(path))
    if not path.is_file():
        raise ValueError('Missing bundle resource: ' + str(path))
    return path


def bundle(source=SOURCE):
    names = read_json(ROOT / 'tools/bundle.json')['files']
    if not names or len(names) != len(set(names)) or 'SKILL.md' not in names:
        raise ValueError('Invalid bundle inventory')
    return {name: digest(regular_file(source, relative_path(name))) for name in names}


def profiles():
    return read_json(ROOT / 'tools/agents.json')['agents']


def destinations(agents, scope, project, home=None):
    home = Path.home() if home is None else Path(home)
    records, targets = profiles(), {}
    for agent in agents:
        if agent not in records:
            raise ValueError('Unknown agent: ' + agent)
        record = records[agent]
        base = home if scope == 'user' else Path(project)
        # Preserve the final path until preflight so a symlink is never silently followed.
        target = base.expanduser().resolve() / record[scope] / SKILL
        targets.setdefault(target, []).append(agent)
    return [{'path': path, 'agents': sorted(set(names))} for path, names in targets.items()]


def preflight(target, files, update):
    if target.is_symlink():
        raise ValueError('Destination is a symlink; update it with its original installer: ' + str(target))
    if target == SOURCE.resolve() or target.is_relative_to(SOURCE.resolve()) or SOURCE.resolve().is_relative_to(target):
        raise ValueError('Do not install over the source bundle')
    if not target.exists():
        return {}
    if not target.is_dir() or not update:
        raise ValueError('Destination exists; use --update for an installation managed by this installer: ' + str(target))
    receipt = target / RECEIPT
    if receipt.is_symlink() or not receipt.is_file():
        raise ValueError('Existing directory is not managed by this installer; preserve it and use its original installation method')
    data = read_json(receipt)
    if data.get('installer_version') != 1 or data.get('skill') != SKILL or not isinstance(data.get('files'), dict) or not data['files'] or 'SKILL.md' not in data['files']:
        raise ValueError('Invalid installation receipt; existing files are preserved')
    old = data['files']
    for name, expected in old.items():
        relative = relative_path(name)
        path = target / relative
        if path.exists() or path.is_symlink():
            if digest(regular_file(target, relative)) != expected:
                raise ValueError('Managed file has local changes; preserve or move them before updating: ' + str(path))
    for name in files:
        relative = relative_path(name)
        path = target / relative
        # Detect directory or parent symlink collisions even when the leaf is missing.
        for parent in relative.parents:
            if parent == Path('.'): continue
            existing = target / parent
            if existing.is_symlink() or (existing.exists() and not existing.is_dir()):
                raise ValueError('Managed resource parent conflicts with a local path: ' + str(existing))
        if name not in old and (path.exists() or path.is_symlink()):
            raise ValueError('New bundle resource conflicts with a local file: ' + str(path))
    return old


def install_one(target, agents, files, old, source=SOURCE):
    target.parent.mkdir(parents=True, exist_ok=True)
    lock = target.parent / ('.' + SKILL + '.install-lock')
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError('Another installation holds the destination lock: ' + str(lock))
    temp, keep_temp = None, False
    try:
        # Recheck under the lock before making any changes.
        checked = preflight(target, files, bool(old))
        if checked != old:
            raise ValueError('Installation changed during preparation; retry after inspecting it')
        temp = Path(tempfile.mkdtemp(prefix='.' + SKILL + '-', dir=target.parent))
        staged, backup = temp / 'staged', temp / 'previous'
        if target.exists():
            shutil.copytree(target, staged, symlinks=True)
        else:
            staged.mkdir()
        for name in old.keys() - files.keys():
            (staged / relative_path(name)).unlink(missing_ok=True)
        for name in files:
            destination = staged / relative_path(name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(regular_file(source, relative_path(name)), destination)
            if digest(destination) != files[name]:
                raise ValueError('Source bundle changed during installation; rerun from a stable checkout')
        (staged / RECEIPT).write_text(json.dumps({'installer_version': 1, 'skill': SKILL,
            'agents': agents, 'installed_at': datetime.now(timezone.utc).isoformat(), 'files': files}, indent=2) + '\n', encoding='utf-8')
        if target.exists(): target.rename(backup)
        try:
            staged.rename(target)
        except Exception:
            if backup.exists():
                try:
                    backup.rename(target)
                except OSError:
                    keep_temp = True
                    raise OSError('Restore the preserved installation from ' + str(backup))
            raise
    finally:
        if temp and temp.exists() and not keep_temp: shutil.rmtree(temp)
        lock.rmdir()


def install(targets, update=False, dry_run=False, source=SOURCE):
    files = bundle(source)
    plans = [(item, preflight(item['path'], files, update)) for item in targets]
    results = []
    for item, old in plans:
        if not dry_run: install_one(item['path'], item['agents'], files, old, source)
        results.append({'agents': item['agents'], 'path': str(item['path']),
                        'action': ('update' if old else 'install'), 'dry_run': dry_run, 'resources': len(files)})
    return {'installations': results, 'note': 'Restart or reload the agent and confirm skill discovery. Browser access and permissions are configured by the host.'}


def doctor(targets):
    expected, results = bundle(), []
    for item in targets:
        target, missing, changed = item['path'], [], []
        for name, value in expected.items():
            try:
                actual = digest(regular_file(target, relative_path(name)))
                if actual != value: changed.append(name)
            except ValueError:
                missing.append(name)
        memory = Path(os.environ.get('REFERENCE_DESIGN_MEMORY_ROOT') or target / 'references/memory').expanduser()
        results.append({'agents': item['agents'], 'path': str(target), 'complete': not missing,
            'matches_checkout': not missing and not changed, 'missing': missing, 'different': changed,
            'managed': (target / RECEIPT).is_file(), 'memory_root': str(memory), 'memory_exists': (memory / 'store.json').is_file()})
    return {'installations': results, 'python': sys.version.split()[0],
        'playwright_module_available': importlib.util.find_spec('playwright') is not None,
        'host_discovery': 'not tested; confirm in the actual agent',
        'browser_access': 'not tested; use the host-approved browser workflow'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list', help='Show agent profiles and documented paths')
    for name in ('install', 'doctor'):
        command = commands.add_parser(name)
        command.add_argument('--agent', nargs='+', required=True, choices=sorted(profiles()))
        command.add_argument('--scope', choices=['project', 'user'], default='project')
        command.add_argument('--project', type=Path, default=Path.cwd())
        if name == 'install':
            command.add_argument('--update', action='store_true')
            command.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        raise ValueError('Python 3.10 or newer is required')
    if args.command == 'list':
        result = {'checked_on': read_json(ROOT / 'tools/agents.json')['checked_on'], 'agents': profiles()}
    else:
        targets = destinations(args.agent, args.scope, args.project)
        result = install(targets, args.update, args.dry_run) if args.command == 'install' else doctor(targets)
    print(json.dumps(result, indent=2))
    if args.command == 'doctor' and not all(i['matches_checkout'] for i in result['installations']):
        return 1
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError) as error:
        print('reference-design installer: ' + str(error), file=sys.stderr)
        sys.exit(1)
