#!/usr/bin/env python3

import logging
import argparse
import sys
import multiprocessing

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
    with lib.status_data(parser) as (args, data):

        for r in args.repositories:
            data.append({'remote_url': r})

        repo_remote = []
        for r in data:
            r['repository_name'] = lib.get_random_string()
            r['repository_href'] = create_repo(r['repository_name'])
            logging.debug("Created repository %s" % r['repository_href'])
            r['remote_name'] = lib.get_random_string()
            r['remote_href'] = create_remote(r['remote_name'], r['remote_url'])
            logging.debug("Created remote %s" % r['remote_href'])

        tasks = []
        for r in data:
            task = start_sync(r['repository_href'], r['remote_href'])
            logging.debug("Created sync task %s" % task)
            tasks.append(task)

        results = lib.wait_for_tasks(tasks)
        print(lib.tasks_table(results))
        print(lib.tasks_min_max_table(results))
        print("Sync tasks waiting time:", lib.tasks_waiting_time(results))
        print("Sync tasks service time:", lib.tasks_service_time(results))

        tasks = []
        for r in data:
            task = create_publication(r['repository_href'])
            logging.debug("Created publication task %s" % task)
            tasks.append(task)

        results = lib.wait_for_tasks(tasks)
        print(lib.tasks_table(results))
        print(lib.tasks_min_max_table(results))
        print("Publication tasks waiting time:", lib.tasks_waiting_time(results))
        print("Publication tasks service time:", lib.tasks_service_time(results))

        for i in range(len(results)):
            data[i]['publication_href'] = results[i]['created_resources'][0]

        tasks = []
        for r in data:
            r['distribution_name'] = lib.get_random_string()
            r['distribution_base_path'] = lib.get_random_string()
            task = create_distribution(r['distribution_name'], r['distribution_base_path'], r['publication_href'])
            logging.debug("Created distribution task %s" % task)
            tasks.append(task)

        results = lib.wait_for_tasks(tasks)
        print(lib.tasks_table(results))
        print(lib.tasks_min_max_table(results))
        print("Distribution tasks waiting time:", lib.tasks_waiting_time(results))
        print("Distribution tasks service time:", lib.tasks_service_time(results))

        distributions = []
        dist_base_urls = []
        for i in range(len(results)):
            data[i]['distribution_href'] = results[i]['created_resources'][0]
            data[i]['download_base_url'] = lib.get(data[i]['distribution_href'])['base_url']

        for r in data:
            params = []
            for f, _, s in lib.parse_pulp_manifest(r['remote_url'] + 'PULP_MANIFEST'):
                params.append((r['download_base_url'], f, s))
            with multiprocessing.Pool(processes=4) as pool:
                durations = pool.starmap(lib.download, params)
            print("Download times for %s: %s" % (r['remote_url'], lib.data_stats(durations)))


    return 0

if __name__ == '__main__':
    sys.exit(main())
