"""Launching a binder via API

The binder build API yields a sequence of messages via event-stream.
This example demonstrates how to consume events from the stream
and redirect to the URL when it is ready.

When the image is ready, your browser will open at the desired URL.
"""

import argparse
import json
import sys
import requests
import shutil

def build_binder(repo,
                 ref='master',
                 filepath=None,
                 *,
                 binder_url='https://mybinder.org'):
    """Launch a binder

    Yields Binder's event-stream events (dicts)
    """
    print("Building binder for {repo}@{ref}".format(repo=repo, ref=ref), file=sys.stderr)
    print("Note your terminal may be weird after this, try running `stty sane` which should fix it", file=sys.stderr)
    url = binder_url + '/build/gh/{repo}/{ref}'.format(repo=repo, ref=ref)
    r = requests.get(url, stream=True)
    r.raise_for_status()
    for line in r.iter_lines():
        line = line.decode('utf8', 'replace')
        if line.startswith('data:'):
            yield json.loads(line.split(':', 1)[1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo', type=str, help="The GitHub repo to build")
    parser.add_argument(
        '--ref', default='master', help="The ref of the repo to build")
    parser.add_argument(
        '--filepath', type=str, help="The file to open, if any.")
    parser.add_argument(
        '--binder',
        default='https://mybinder.org',
        help="""
        The URL of the binder instance to use.
        Use `http://localhost:8585` if you are doing local testing.
    """)
    opts = parser.parse_args()

    assert shutil.which('gotty-client')
    for evt in build_binder(
            opts.repo,
            ref=opts.ref,
            filepath=opts.filepath,
            binder_url=opts.binder):
        if 'message' in evt:
            print("[{phase}] {message}".format(
                phase=evt.get('phase', ''),
                message=evt['message'].rstrip(),
            ), file=sys.stderr)
        if evt.get('phase') == 'ready':
            url = "{url}proxy/8080/?token={token}".format(**evt)
            print("/Users/lukasheinrich/Code/go/bin/gotty-client -v2 %s" % url)
            break
    else:
        sys.exit("binder never became ready")
