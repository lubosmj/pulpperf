#!/usr/bin/env python3

import logging
import argparse
import sys
import datetime
import multiprocessing

import pulpperf.interact
import pulpperf.structure
import pulpperf.utils
import pulpperf.reporting


def list_units_in_repo_ver(repo_ver):
    """List the file content with all the fields"""
    return pulpperf.interact.get('/pulp/api/v3/content/file/files/',
                                 params={'repository_version': repo_ver})


def inspect_content(href):
    """Inspect a file content using href"""
    return pulpperf.interact.get(href)


def main():
    parser = argparse.ArgumentParser(
        description="List content of repo version and inspect individual units",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--limit', type=int, default=100,
                        help='limit number of inspected units (per repository)')
    parser.add_argument('--processes', type=int, default=1,
                        help='how many parallel processes to use when inspecting')
    with pulpperf.structure.status_data(parser) as (args, data):

        before = datetime.datetime.utcnow()

        durations_list = []
        for r in data:
            duration, content = pulpperf.utils.measureit(list_units_in_repo_ver, r['repository_version_href'])
            logging.debug("Repo version %s have %d content units" % (r['repository_version_href'], len(content)))
            durations_list.append(duration)

            params = []
            for c in content[:args.limit]:
                url = c.get("_href")
                params.append((inspect_content, url))
            with multiprocessing.Pool(processes=args.processes) as pool:
                output = pool.starmap(pulpperf.utils.measureit, params)
            durations_content = [i[0] for i in output]
            print("Content inspection duration in %s: %s" % (r['repository_version_href'], pulpperf.reporting.data_stats(durations_content)))

        after = datetime.datetime.utcnow()
        print("Repo version content listing duration: %s" % pulpperf.reporting.data_stats(durations_list))
        print(pulpperf.reporting.fmt_start_end_date("Experiment start - end time", before, after))

    return 0


if __name__ == '__main__':
    sys.exit(main())
