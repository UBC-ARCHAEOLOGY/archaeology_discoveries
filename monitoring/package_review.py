#!/usr/bin/env python3
"""Package the committed review snapshot; no untracked files, runner secrets or raw intake."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

REVIEW_BASE = '2def086a9f9796fe483be415e653ccc1ffaf4f30'
ROUND2_HEAD = 'd07dc52262ebb9d6604cc11127686924bf289369'
MAIN_BASE = '3d518218d4825a325cef60269c6d3cea4bc2cf93'


def git(*args):
    return subprocess.check_output(['git', *args])


def package(destination):
    head = git('rev-parse', 'HEAD').decode().strip()
    # git archive reads only committed tracked bytes; generated site/work/state never enter.
    snapshot = git('archive', '--format=zip', head)
    with zipfile.ZipFile(io.BytesIO(snapshot)) as source, zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as out:
        hashes = {}
        for entry in source.infolist():
            if entry.is_dir():
                continue
            body = source.read(entry)
            out.writestr('source/'+entry.filename, body)
            hashes[entry.filename] = hashlib.sha256(body).hexdigest()
        out.writestr('round2.diff', git('diff', '--binary', REVIEW_BASE, head))
        out.writestr('round3.diff', git('diff', '--binary', ROUND2_HEAD, head))
        out.writestr('complete-pr.diff', git('diff', '--binary', MAIN_BASE, head))
        out.writestr('manifest.json', json.dumps({
            'head':head, 'reviewed_round1_head':REVIEW_BASE,'reviewed_round2_head':ROUND2_HEAD,'main_base':MAIN_BASE,
            'source_sha256':hashes,
            'note':'Committed source only. Verification reports distinguish local tests from hosted CI; no production activation.'},indent=2)+'\n')
    print('Review package: ' + str(destination))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    package(args.output)
