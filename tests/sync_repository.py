#!/usr/bin/env python3

import logging
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
                    data={'repository': repo, 'mirror': False})['task']


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
        logging.debug("Created repository %s" % repo)
        remote = create_remote(lib.get_random_string(), r)
        logging.debug("Created remote %s" % remote)
        repo_remote.append((repo, remote))

    tasks = []
    for repo, remote in repo_remote:
        task = start_sync(repo, remote)
        logging.debug("Created sync task %s" % task)
        tasks.append(task)

    results = lib.wait_for_tasks(tasks)
    print(lib.tasks_table(results))
    print("Sync tasks waiting time:", lib.tasks_waiting_time(results))
    print("Sync tasks service time:", lib.tasks_service_time(results))

    return 0


if __name__ == '__main__':
    sys.exit(main())
