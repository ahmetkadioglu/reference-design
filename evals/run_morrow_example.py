#!/usr/bin/env python3
"""Re-render the frozen Morrow examples and prepare a new private blinded review."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
from threading import Thread

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/reference-design/scripts'))
from capture_reference import capture
from design_evaluation import prepare


def run(output, browser_path=None):
    from playwright.sync_api import sync_playwright
    if output.exists():
        raise ValueError('Use a new output directory to preserve earlier evaluation runs')
    output.mkdir(parents=True)

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    reports = {}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**({'executable_path': browser_path} if browser_path else {}))
            try:
                for name, path in [('reference', 'tests/fixtures/reference.html'),
                                   ('baseline', 'evals/examples/morrow/output-one/index.html'),
                                   ('candidate', 'evals/examples/morrow/output-two/index.html')]:
                    report = capture(browser, f'http://127.0.0.1:{server.server_port}/{path}', output / 'captures',
                        [{'width': 1440, 'height': 900}, {'width': 390, 'height': 844}], keyboard_steps=0)
                    if report['errors']:
                        raise ValueError('Resolve capture errors before comparing: ' + report['report_path'])
                    reports[name] = report
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
    reference = reports['reference']
    images = [Path(reference['report_path']).parent / s['screenshot'] for s in reference['snapshots']
              if s['state'] == 'default' and not s['reduced_motion']]
    result = prepare(Path(reports['baseline']['report_path']), Path(reports['candidate']['report_path']),
        (ROOT / 'evals/examples/morrow/brief.md').read_text(encoding='utf-8'),
        output / 'review', output / 'private-unblinding/key.json', reference_images=images)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--browser-path', default=os.environ.get('REFERENCE_DESIGN_BROWSER_PATH'))
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.output.resolve(), args.browser_path), indent=2))
    except Exception as error:
        print('morrow-example: ' + str(error), file=sys.stderr)
        sys.exit(1)
