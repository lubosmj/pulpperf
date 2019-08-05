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
        pulpperf.reporting.report_tasks_stats('Resync tasks', results)

    return 0


if __name__ == '__main__':
    sys.exit(main())
