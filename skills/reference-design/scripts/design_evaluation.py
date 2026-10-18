#!/usr/bin/env python3
"""Prepare blinded screenshot comparisons and summarize an independent judgment."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import random
import secrets
import shutil
import struct
import sys
import tempfile
import uuid

CRITERIA = [
    {"id": "brief", "instruction": "Which design follows the explicit brief and product content more closely?"},
    {"id": "hierarchy", "instruction": "Which design communicates the primary action and reading order more clearly?"},
    {"id": "readability", "instruction": "Which design has clearer typography, wrapping, and readable surfaces?"},
    {"id": "composition", "instruction": "Which design uses alignment, spacing, and content density more effectively?"},
    {"id": "consistency", "instruction": "Which design applies repeated visual decisions more consistently?"},
    {"id": "responsive", "instruction": "Which design adapts more effectively across the provided viewport sizes?"},
]
CHOICES = {"A", "B", "tie", "unassessed"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_path(report_path, relative):
    if not isinstance(relative, str):
        raise ValueError("Every compared snapshot needs a screenshot")
    parent = report_path.parent.resolve()
    target = (parent / relative).resolve()
    if Path(relative).is_absolute() or not target.is_relative_to(parent):
        raise ValueError("Screenshot paths must remain within their capture directory")
    with target.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise ValueError("Comparison assets must be PNG screenshots")
    width, height = struct.unpack('>II', header[16:24])
    if not width or not height:
        raise ValueError("Invalid screenshot dimensions")
    return target, {"width": width, "height": height}


def read_capture(path, all_states=False):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("capture_version") != 1 or not isinstance(data.get("snapshots"), list):
        raise ValueError("Expected a version 1 capture report")
    if data.get("errors"):
        raise ValueError("Fix capture errors before preparing a comparison")
    shots = {}
    for shot in data["snapshots"]:
        if not all_states and (shot.get("state") != "default" or shot.get("reduced_motion")):
            continue
        size = shot["viewport"]
        key = (size["width"], size["height"], shot["state"], bool(shot.get("reduced_motion")))
        if key in shots:
            raise ValueError("Duplicate viewport/state snapshot")
        asset, dimensions = image_path(path, shot.get("screenshot"))
        shots[key] = {"asset": asset, "dimensions": dimensions,
                      "issues": {severity: sum(i.get("severity") == severity for i in shot.get("issues", [])) for severity in ("error", "warning")}}
    if not shots:
        raise ValueError("No matching screenshots in capture")
    return data, shots


def check_criteria(criteria):
    if not isinstance(criteria, list) or not 1 <= len(criteria) <= 20:
        raise ValueError("Supply 1..20 review criteria")
    seen = set()
    for criterion in criteria:
        if not isinstance(criterion, dict) or not all(isinstance(criterion.get(k), str) and criterion[k].strip() for k in ("id", "instruction")):
            raise ValueError("Each criterion needs id and instruction")
        if criterion["id"] in seen:
            raise ValueError("Criterion IDs must be unique")
        seen.add(criterion["id"])


def render_review(package):
    criteria = ''.join('<li><strong>' + html.escape(c['id']) + '</strong>: ' + html.escape(c['instruction']) + '</li>' for c in package['criteria'])
    pairs = []
    for pair in package['pairs']:
        images = ''.join('<figure><figcaption>Design ' + label + ' · <a href="' + html.escape(pair['images'][label]['path'], quote=True) + '">Open full size</a></figcaption><img alt="Design ' + label + ' at the stated viewport" src="' + html.escape(pair['images'][label]['path'], quote=True) + '"></figure>' for label in ('A', 'B'))
        pairs.append('<section><h2>' + html.escape(pair['id']) + ' · ' + str(pair['viewport']['width']) + ' × ' + str(pair['viewport']['height']) + ' · ' + html.escape(pair['state']) + '</h2><div class="pair">' + images + '</div></section>')
    refs = ''.join('<figure><figcaption>Reference ' + str(index) + '</figcaption><img alt="Supplied reference" src="' + html.escape(image['path'], quote=True) + '"></figure>' for index, image in enumerate(package.get('reference_images', []), 1))
    references = '<section><h2>Supplied references</h2><div class="pair">' + refs + '</div></section>' if refs else ''
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Design comparison</title><style>body{margin:0;background:#f2f4f8;color:#172033;font:16px/1.5 system-ui}header,section{padding:24px;max-width:1600px;margin:auto}h1{font-size:32px}pre{white-space:pre-wrap;font:inherit}.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:start}figure{margin:0;min-width:0;background:white}figcaption{font-weight:700;padding:12px}img{display:block;width:100%;height:auto}@media(max-width:700px){.pair{grid-template-columns:1fr}}</style><header><h1>Design comparison</h1><p>Review A and B against the same brief. Labels do not disclose the production condition. Screenshots establish appearance, not complete behavior or accessibility.</p><h2>Brief</h2><pre>' + html.escape(package['brief']) + '</pre><h2>Criteria</h2><ol>' + criteria + '</ol><p>Record preferences and screenshot evidence in judgment-template.json. Use unassessed where evidence is insufficient.</p></header>' + references + ''.join(pairs) + '</html>\n'


def prepare(baseline, candidate, brief, output, key_file, criteria=None, seed=None, all_states=False, reference_images=()):
    default_criteria = criteria is None
    criteria = list(criteria if criteria is not None else CRITERIA)
    if reference_images and default_criteria:
        criteria.append({'id': 'reference-use', 'instruction': 'Which design adapts the requested reference principles more coherently while following the target brief?'})
    check_criteria(criteria)
    output, key_file = output.resolve(), key_file.resolve()
    if not isinstance(brief, str) or not brief.strip():
        raise ValueError("A nonempty brief is required")
    if output.exists() or key_file.exists():
        raise ValueError("Use new output and private key paths; existing evaluations are preserved")
    if key_file.is_relative_to(output):
        raise ValueError("Keep the private condition key outside the reviewer package")
    left_data, left = read_capture(baseline, all_states)
    right_data, right = read_capture(candidate, all_states)
    if set(left) != set(right):
        raise ValueError("Capture viewport/state sets must match; missing views cannot be silently excluded")
    if any(left_data.get(k) != right_data.get(k) for k in ('engine', 'browser_version')):
        raise ValueError("Use the same engine and browser version for both captures")
    flip = random.Random(seed).randrange(2) if seed is not None else secrets.randbelow(2)
    labels = {'A': 'candidate' if flip else 'baseline', 'B': 'baseline' if flip else 'candidate'}
    sources = {'baseline': left, 'candidate': right}
    comparison_id = str(uuid.uuid4())
    package = {'evaluation_version': 1, 'comparison_id': comparison_id, 'brief': brief, 'criteria': criteria,
               'environment': {k: left_data.get(k) for k in ('engine', 'browser_version')}, 'pairs': [],
               'reference_images': [],
               'limitations': ['A single comparison does not establish a general skill improvement.',
                              'Pixel similarity is not treated as design quality; assess brief and reference-role compliance.',
                              'Screenshots alone do not prove working interactions or complete accessibility.']}
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix='.evaluation-', dir=output.parent))
    key_written = False
    try:
        (temp / 'assets').mkdir()
        for index, reference in enumerate(reference_images, 1):
            path, dimensions = image_path(reference, reference.name)
            relative = 'assets/reference-%03d.png' % index
            shutil.copyfile(path, temp / relative)
            package['reference_images'].append({'path': relative, 'sha256': digest(temp / relative), 'dimensions': dimensions})
        for index, key in enumerate(sorted(left), 1):
            pair = {'id': 'pair-%03d' % index, 'viewport': {'width': key[0], 'height': key[1]},
                    'state': key[2], 'reduced_motion': key[3], 'images': {}}
            for label, condition in labels.items():
                shot = sources[condition][key]
                relative = 'assets/%s-%03d.png' % (label, index)
                shutil.copyfile(shot['asset'], temp / relative)
                pair['images'][label] = {'path': relative, 'sha256': digest(temp / relative), 'dimensions': shot['dimensions']}
            package['pairs'].append(pair)
        (temp / 'review.json').write_text(json.dumps(package, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (temp / 'index.html').write_text(render_review(package), encoding='utf-8')
        template = {'evaluation_version': 1, 'comparison_id': comparison_id, 'reviewer': '', 'overall_preference': 'unassessed',
                    'overall_reason': '', 'overall_evidence': [],
                    'evidence_format': {'allowed_pair_ids': [p['id'] for p in package['pairs']],
                                        'instruction': 'Use exact pair ID strings in evidence arrays, for example ["pair-001"]. Put descriptive observations in reason fields.'},
                    'criteria': [{'id': c['id'], 'preferred': 'unassessed', 'reason': '', 'evidence': []} for c in criteria], 'limitations': []}
        (temp / 'judgment-template.json').write_text(json.dumps(template, indent=2) + '\n', encoding='utf-8')
        private = {'evaluation_version': 1, 'comparison_id': comparison_id, 'labels': labels,
                   'review_sha256': digest(temp / 'review.json'),
                   'sources': {condition: {'report': str(path.resolve()), 'sha256': digest(path),
                       'observations': {str(key): shot['issues'] for key, shot in sources[condition].items()}}
                       for condition, path in [('baseline', baseline), ('candidate', candidate)]}}
        key_file.parent.mkdir(parents=True, exist_ok=True)
        with key_file.open('x', encoding='utf-8') as handle:
            json.dump(private, handle, indent=2)
            handle.write('\n')
        key_written = True
        temp.rename(output)
    except Exception:
        if key_written:
            key_file.unlink()
        raise
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return {'comparison_id': comparison_id, 'review_package': str(output), 'private_key': str(key_file), 'pairs': len(package['pairs'])}


def summarize(review_directory, judgment_path, key_file):
    review_path = review_directory / 'review.json'
    package = json.loads(review_path.read_text(encoding='utf-8'))
    private = json.loads(key_file.read_text(encoding='utf-8'))
    judgment = json.loads(judgment_path.read_text(encoding='utf-8'))
    if any(data.get('evaluation_version') != 1 for data in (package, private, judgment)):
        raise ValueError('Unsupported evaluation version')
    if any(data.get('comparison_id') != package.get('comparison_id') for data in (private, judgment)) or digest(review_path) != private.get('review_sha256'):
        raise ValueError('Judgment, key, and original review package must match')
    if set(private.get('labels', {})) != {'A', 'B'} or set(private['labels'].values()) != {'baseline', 'candidate'}:
        raise ValueError('Invalid private label mapping')
    for pair in package['pairs']:
        for image in pair['images'].values():
            path, _ = image_path(review_path, image['path'])
            if digest(path) != image['sha256']:
                raise ValueError('Review screenshots changed after preparation')
    for image in package.get('reference_images', []):
        path, _ = image_path(review_path, image['path'])
        if digest(path) != image['sha256']:
            raise ValueError('Review reference images changed after preparation')
    check_criteria(package['criteria'])
    criteria = judgment.get('criteria')
    if not isinstance(criteria, list) or len(criteria) != len(package['criteria']):
        raise ValueError('Judgment must account for every criterion')
    expected, seen = {c['id'] for c in package['criteria']}, set()
    pairs = {p['id'] for p in package['pairs']}
    votes, evaluated = {'baseline': 0, 'candidate': 0, 'tie': 0, 'unassessed': 0}, []
    for item in criteria:
        if not isinstance(item, dict) or item.get('id') not in expected or item['id'] in seen or item.get('preferred') not in CHOICES:
            raise ValueError('Invalid or duplicate criterion judgment')
        seen.add(item['id'])
        if not isinstance(item.get('reason'), str) or not item['reason'].strip():
            raise ValueError('Every criterion needs a reason, including unassessed criteria')
        evidence = item.get('evidence')
        if not isinstance(evidence, list) or any(not isinstance(p, str) or p not in pairs for p in evidence):
            raise ValueError('Evidence must name actual pair IDs')
        if item['preferred'] != 'unassessed' and not evidence:
            raise ValueError('Assessed preferences require screenshot pair evidence')
        preferred = private['labels'].get(item['preferred'], item['preferred'])
        votes[preferred] += 1
        evaluated.append({**item, 'preferred_condition': preferred})
    reviewer = judgment.get('reviewer')
    overall = judgment.get('overall_preference', 'unassessed')
    if not isinstance(reviewer, str) or not reviewer.strip() or overall not in CHOICES:
        raise ValueError('Judgment needs a reviewer and a valid overall preference')
    if overall != 'unassessed':
        if not isinstance(judgment.get('overall_reason'), str) or not judgment['overall_reason'].strip():
            raise ValueError('An overall preference needs its own rationale')
        evidence = judgment.get('overall_evidence')
        if not isinstance(evidence, list) or not evidence or any(p not in pairs for p in evidence):
            raise ValueError('An overall preference needs actual screenshot pair evidence')
        if not any(item['preferred'] != 'unassessed' for item in criteria):
            raise ValueError('An overall preference requires at least one assessed criterion')
    limitations = judgment.get('limitations', [])
    if not isinstance(limitations, list) or not all(isinstance(v, str) for v in limitations):
        raise ValueError('Judgment limitations must be strings')
    return {'evaluation_version': 1, 'comparison_id': package['comparison_id'], 'reviewer': reviewer,
            'criterion_votes': votes, 'overall_preference': private['labels'].get(overall, overall),
            'overall_reason': judgment.get('overall_reason', ''), 'overall_evidence': judgment.get('overall_evidence', []),
            'criteria': evaluated, 'automated_observations': {k: v['observations'] for k, v in private['sources'].items()},
            'judgment_sha256': digest(judgment_path), 'limitations': package['limitations'] + limitations}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    create = sub.add_parser('prepare')
    create.add_argument('--baseline', type=Path, required=True)
    create.add_argument('--candidate', type=Path, required=True)
    create.add_argument('--brief', type=Path, required=True)
    create.add_argument('--output', type=Path, required=True)
    create.add_argument('--key-file', type=Path, required=True)
    create.add_argument('--criteria', type=Path)
    create.add_argument('--seed', type=int)
    create.add_argument('--all-states', action='store_true')
    create.add_argument('--reference-image', type=Path, action='append', default=[])
    final = sub.add_parser('summarize')
    final.add_argument('--review', type=Path, required=True)
    final.add_argument('--judgment', type=Path, required=True)
    final.add_argument('--key-file', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        criteria = json.loads(args.criteria.read_text(encoding='utf-8')) if args.criteria else None
        result = prepare(args.baseline, args.candidate, args.brief.read_text(encoding='utf-8'), args.output,
                         args.key_file, criteria, args.seed, args.all_states, args.reference_image)
    else:
        result = summarize(args.review, args.judgment, args.key_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print('design-evaluation: ' + str(error), file=sys.stderr)
        sys.exit(1)
