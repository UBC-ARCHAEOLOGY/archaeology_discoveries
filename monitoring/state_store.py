#!/usr/bin/env python3
"""CAS-like non-force Git persistence. Fixed ref, no arbitrary shell or main writes."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import operations as ops
import monitor as m

REF = 'refs/heads/monitoring/state-phase2b'


def git(*args, data=None, env=None, check=True):
    return subprocess.run(['git', *args], input=data, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=check, env=env)


def remote_head():
    response = git('ls-remote', '--exit-code', 'origin', REF, check=False)
    if response.returncode == 2:
        return None
    if response.returncode:
        raise RuntimeError('State remote unavailable; refusing to reset')
    return response.stdout.decode().split()[0]


def restore(path):
    head = remote_head()
    if not head:
        if path.exists():
            raise ValueError('Local state exists but remote missing')
        return None
    git('fetch', '--no-tags', 'origin', REF)
    payload = git('show', head + ':state.json').stdout
    state = json.loads(payload)
    ops.atomic_json(path, state)
    ops.load_state(path)
    return head


def persist(path):
    state = ops.load_state(path)
    head = remote_head()
    if head:
        git('fetch', '--no-tags', 'origin', REF)
        old = json.loads(git('show', head + ':state.json').stdout)
        if not set(old['observations']).issubset(state['observations']):
            raise ValueError('Refusing ledger loss')
        # Exact parent read by collector is bound in the state, preventing stale writes.
    expected = state.pop('_parent', None)
    if expected != head:
        raise ValueError('Concurrent state update: rerun against remote state')
    payload = (json.dumps(state, sort_keys=True, ensure_ascii=False, indent=2)+'\n').encode()
    blob = git('hash-object', '-w', '--stdin', data=payload).stdout.decode().strip()
    tree = git('mktree', data=f'100644 blob {blob}\tstate.json\n'.encode()).stdout.decode().strip()
    args = ['commit-tree', tree]
    if head:
        args += ['-p', head]
    env = {**os.environ, 'GIT_AUTHOR_NAME': 'Archaeology monitoring',
           'GIT_AUTHOR_EMAIL': 'monitoring@users.noreply.github.com',
           'GIT_COMMITTER_NAME': 'Archaeology monitoring',
           'GIT_COMMITTER_EMAIL': 'monitoring@users.noreply.github.com'}
    commit = git(*args, data=b'Persist Phase 2B source windows and safe ledger\n', env=env).stdout.decode().strip()
    # Non-force push rejects a race even if concurrency configuration is bypassed.
    git('push', 'origin', commit + ':' + REF)
    print('Durable state committed to ' + REF)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['restore', 'persist'])
    parser.add_argument('--path', type=Path, default=m.ROOT/'runs/durable/state.json')
    args = parser.parse_args()
    path = m.safe_output(args.path)
    if args.action == 'restore':
        head = restore(path)
        state = ops.load_state(path)
        state['_parent'] = head
        ops.atomic_json(path, state)
    else:
        persist(path)


if __name__ == '__main__':
    main()
