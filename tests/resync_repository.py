#!/usr/bin/env python3

import logging
import argparse
import sys

import pulpperf.interact
import pulpperf.structure
import pulpperf.utils
import pulpperf.reporting


def start_sync(repo, remote):
    """Start sync of the remote into the repository, return task"""
    return pulpperf.interact.post(remote+'sync/',
                                  data={'repository': repo, 'mirror': False})['task']


def main():
    parser = argparse.ArgumentParser(
        description="Resync file repositories",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    with pulpperf.structure.status_data(parser) as (args, data):

        tasks = []
        for r in data:
            task = start_sync(r['repository_href'], r['remote_href'])
            logging.debug("Created resync task %s" % task)
            tasks.append(task)

        results = pulpperf.interact.wait_for_tasks(tasks)
        print(pulpperf.reporting.tasks_table(results))
        print(pulpperf.reporting.tasks_min_max_table(results))
        print("Resync tasks waiting time:", pulpperf.reporting.tasks_waiting_time(results))
        print("Resync tasks service time:", pulpperf.reporting.tasks_service_time(results))

    return 0


if __name__ == '__main__':
    sys.exit(main())
