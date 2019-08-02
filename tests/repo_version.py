#!/usr/bin/env python3

import logging
import argparse

import pulpperf.interact
import pulpperf.structure
import pulpperf.utils
import pulpperf.reporting


def create_repo_version(repo, ver):
    """Create repository version based on different existing version"""
    return pulpperf.interact.post(repo + 'versions/',
                                  data={'base_version': ver})['_href']


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
            r['repository_clone_href'] = create_repo(r['repository_name'])
            logging.debug("For repo %s created repository clone %s" % (r['repository_href'], r['repository_clone_href']))

        tasks = []
        for r in data:
            task = create_repo_version(r['repository_clone_href'], r['repository_version_href'])
            logging.debug("Created version clone task %s" % task)
            tasks.append(task)

        results = pulpperf.interact.wait_for_tasks(tasks)
        print(pulpperf.reporting.tasks_table(results))
        print(pulpperf.reporting.tasks_min_max_table(results))
        print("Version clone tasks waiting time:", pulpperf.reporting.tasks_waiting_time(results))
        print("Version clone tasks service time:", pulpperf.reporting.tasks_service_time(results))
