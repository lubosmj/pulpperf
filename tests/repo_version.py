#!/usr/bin/env python3

import logging
import argparse
import sys

import pulpperf.interact
import pulpperf.structure
import pulpperf.utils
import pulpperf.reporting


def create_repo_version_base_version(repo, ver):
    """Create repository version based on different existing version"""
    return pulpperf.interact.post(repo + 'versions/',
                                  data={'base_version': ver})['task']


def create_repo_version_add_content_units(repo, hrefs):
    """Create repository version based on list of hrefs"""
    return pulpperf.interact.post(repo + 'versions/',
                                  data={'add_content_units': hrefs})['task']


def create_repo(name):
    """Create repository"""
    return pulpperf.interact.post('/pulp/api/v3/repositories/',
                                  data={'name': name})['_href']


def list_units_in_repo_ver(repo_ver):
    """List the file content with all the fields"""
    return pulpperf.interact.get_results('/pulp/api/v3/content/file/files/',
                                 params={'repository_version': repo_ver})


def main():
    parser = argparse.ArgumentParser(
        description="Create repository version copy",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    with pulpperf.structure.status_data(parser) as (args, data):

        for r in data:
            r['repository_clone1_name'] = pulpperf.utils.get_random_string()
            r['repository_clone1_href'] = create_repo(r['repository_clone1_name'])
            logging.debug("For repo %s created repository clone1 %s" % (r['repository_href'], r['repository_clone1_href']))
            r['repository_clone2_name'] = pulpperf.utils.get_random_string()
            r['repository_clone2_href'] = create_repo(r['repository_clone2_name'])
            logging.debug("For repo %s created repository clone2 %s" % (r['repository_href'], r['repository_clone2_href']))

        tasks = []
        for r in data:
            task = create_repo_version_base_version(r['repository_clone1_href'], r['repository_version_href'])
            logging.debug("Created version clone1 task %s" % task)
            tasks.append(task)

        results = pulpperf.interact.wait_for_tasks(tasks)
        pulpperf.reporting.report_tasks_stats('Version clone with base_version tasks', results)
        add_content_units

        hrefs = [i['_href'] for i in list_units_in_repo_ver(r['repository_version_href'])]
        logging.debug("Repo version %s have %s units" % (r['repository_version_href'], len(hrefs)))

        tasks = []
        for r in data:
            task = create_repo_version_add_content_units(r['repository_clone2_href'], hrefs)
            logging.debug("Created version clone2 task %s" % task)
            tasks.append(task)

        results = pulpperf.interact.wait_for_tasks(tasks)
        pulpperf.reporting.report_tasks_stats('Version clone with add_content_units tasks', results)

if __name__ == '__main__':
    sys.exit(main())
