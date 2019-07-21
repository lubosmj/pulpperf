#!/usr/bin/env python3

import argparse
import sys

import lib


def create_repo(name):
    """Create repository"""
    return lib.post('/pulp/api/v3/repositories/',
                    data={'name': name})['_href']


def create_remote(name, url):
    """Create remote"""
    return lib.post('/pulp/api/v3/remotes/file/file/',
                    data={'name': name, 'url': url+'PULP_MANIFEST'})['_href']


def start_sync(repo, remote):
    """Start sync of the remote into the repository, return task"""
    return lib.post(remote+'sync/',
                    data={'repository': repo, 'mirror': False})


def main():
    parser = argparse.ArgumentParser(
        description="Sync file repositories in parallel",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('repositories', nargs='+',
                        help='file repository(ies) to sync')
    args = lib.add_common_params_and_parse(parser)

    repo_remote = []
    for r in args.repositories:
        repo = create_repo(lib.get_random_string())
        remote = create_remote(lib.get_random_string(), r)
        repo_remote.append((repo, remote))

    tasks = []
    for repo, remote in repo_remote:
        task = start_sync(repo, remote)
        tasks.append(task)

    return 0


if __name__ == '__main__':
    sys.exit(main())
