#!/usr/bin/env python3
"""CAS-like non-force Git persistence. Fixed ref, no arbitrary shell or main writes."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess
import operations as ops
import monitor as m

REF = 'refs/heads/monitoring/state-phase2b'


def git(*args, data=None, env=None, check=True):
    environment = dict(os.environ if env is None else env)
    token = environment.get('GH_TOKEN')
    if token:
        environment['GIT_CONFIG_COUNT'] = '1'
        environment['GIT_CONFIG_KEY_0'] = 'http.https://github.com/.extraheader'
        environment['GIT_CONFIG_VALUE_0'] = 'AUTHORIZATION: basic ' + base64.b64encode(('x-access-token:' + token).encode()).decode()
    return subprocess.run(['git', *args], input=data, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=check, env=environment)


def remote_head():
    response = git('ls-remote', '--exit-code', 'origin', REF, check=False)
    if response.returncode == 2:
        return None
    if response.returncode:
        raise RuntimeError('State remote unavailable; refusing to reset')
    return response.stdout.decode().split()[0]


def remote_payload(head):
    size = int(git('cat-file', '-s', head + ':state.json').stdout)
    if not 0 < size <= ops.schema.MAX_BYTES:
        raise ValueError('Remote state exceeds size bound')
    return git('show', head + ':state.json').stdout


def restore(path):
    head = remote_head()
    if not head:
        if path.exists():
            raise ValueError('Local state exists but remote missing')
        return None
    git('fetch', '--no-tags', 'origin', REF)
    payload = remote_payload(head)
    state = ops.schema.decode(payload, *ops.state_inputs())
    ops.atomic_json(path, state)
    return head


def persist(path):
    state = ops.load_state(path)
    head = remote_head()
    if head:
        git('fetch', '--no-tags', 'origin', REF)
        old = ops.schema.decode(remote_payload(head), *ops.state_inputs())
        if not set(old['observations']).issubset(state['observations']):
            raise ValueError('Refusing ledger loss')
        for key, row in old['observations'].items():
            newer = state['observations'][key]
            if (row['first_seen'] != newer['first_seen'] or newer['last_seen'] < row['last_seen']
                or not set(row['source_ids']).issubset(newer['source_ids'])
                or row['identity_keys'] != newer['identity_keys']):
                raise ValueError('Refusing observation history regression')
        if not set(old['runs']).issubset(state['runs']):
            raise ValueError('Refusing run history loss')
        for sid, previous in old['sources'].items():
            if sid not in state['sources'] or state['sources'][sid].get('watermark', '') < previous.get('watermark', ''):
                raise ValueError('Refusing source watermark regression')
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
