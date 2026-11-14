"""Update a bot-owned operational issue with controlled output; no human decisions."""
import json
import os
import subprocess
from pathlib import Path


def gh(*args):
    return subprocess.check_output(['gh', *args], text=True)


def main():
    title = 'Phase 2B — human editorial review queue' if os.environ['MODE'] == 'review' else 'Phase 2B — source outage / incomplete coverage'
    issues = json.loads(gh('issue', 'list', '--state', 'open', '--limit', '100', '--json', 'number,title,author'))
    matches = [i for i in issues if i['title'] == title and i['author']['login'] == 'github-actions[bot]']
    body = Path('monitoring/runs/phase2b/summary.md')
    with body.open('a') as stream:
        stream.write(f"\nRun: https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}\n")
        stream.write('\nReview safe report.json artifact for hash queue and balance details. This issue records no PROMOTE/HOLD/REJECT decision.\n')
    if matches:
        gh('issue', 'edit', str(matches[0]['number']), '--body-file', str(body))
    else:
        gh('issue', 'create', '--title', title, '--body-file', str(body))


if __name__ == '__main__':
    main()
