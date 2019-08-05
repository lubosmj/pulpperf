#!/usr/bin/env python3

import logging
import argparse
import sys

import pulpperf.interact
import pulpperf.structure
import pulpperf.utils
import pulpperf.reporting


def create_repo_version(repo, ver):
    """Create repository version based on different existing version"""
    return pulpperf.interact.post(repo + 'versions/',
                                  data={'base_version': ver})['task']


def create_repo(name):
    """Create repository"""
    return pulpperf.interact.post('/pulp/api/v3/repositories/',
                                  data={'name': name})['_href']


def main():
    parser = argparse.ArgumentParser(
        description="Create repository version copy",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    with pulpperf.structure.status_data(parser) as (args, data):

        for r in data:
            r['repository_clone_name'] = pulpperf.utils.get_random_string()
            r['repository_clone_href'] = create_repo(r['repository_clone_name'])
            logging.debug("For repo %s created repository clone %s" % (r['repository_href'], r['repository_clone_href']))

        tasks = []
        for r in data:
            task = create_repo_version(r['repository_clone_href'], r['repository_version_href'])
            logging.debug("Created version clone task %s" % task)
            tasks.append(task)

        results = pulpperf.interact.wait_for_tasks(tasks)
        pulpperf.reporting.report_tasks_stats('Version clone tasks', results)


if __name__ == '__main__':
    sys.exit(main())
