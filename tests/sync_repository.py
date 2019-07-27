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


def create_publication(repo):
    """Start publication of the repository, return task"""
    return lib.post('/pulp/api/v3/publications/file/file/',
                    data={'repository': repo})['task']


def create_distribution(name, base_path, pub):
    """Start distribution of the repository version, return task"""
    return lib.post('/pulp/api/v3/distributions/file/file/',
                    data={'name': name, 'base_path': base_path, 'publication': pub})['task']


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
    print(lib.tasks_min_max_table(results))
    print("Sync tasks waiting time:", lib.tasks_waiting_time(results))
    print("Sync tasks service time:", lib.tasks_service_time(results))

    tasks = []
    for repo, remote in repo_remote:
        task = create_publication(repo)
        logging.debug("Created publication task %s" % task)
        tasks.append(task)

    results = lib.wait_for_tasks(tasks)
    print(lib.tasks_table(results))
    print(lib.tasks_min_max_table(results))
    print("Publication tasks waiting time:", lib.tasks_waiting_time(results))
    print("Publication tasks service time:", lib.tasks_service_time(results))

    publications = []
    for result in results:
        pub = result['created_resources'][0]
        publications.append(pub)

    tasks = []
    for pub in publications:
        task = create_distribution(lib.get_random_string(), lib.get_random_string(), pub)
        logging.debug("Created distribution task %s" % task)
        tasks.append(task)

    results = lib.wait_for_tasks(tasks)
    print(lib.tasks_table(results))
    print(lib.tasks_min_max_table(results))
    print("Distribution tasks waiting time:", lib.tasks_waiting_time(results))
    print("Distribution tasks service time:", lib.tasks_service_time(results))

    distributions = []
    dist_base_urls = []
    for result in results:
        distribution = result['created_resources'][0]
        distributions.append(distribution)
        dist_base_urls.append(lib.get(distribution)['base_url'])

    return 0

if __name__ == '__main__':
    sys.exit(main())
