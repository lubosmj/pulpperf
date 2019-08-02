#!/usr/bin/env python3

import logging
import argparse
import sys

import lib


def list_units_in_repo_ver(repo_ver):
    """List the file content with all the fields""" 
    return lib.get('/pulp/api/v3/content/file/files/',
        params={'repository_version': repo_ver})


def inspect_content(href):
    """Inspect a file content using href"""
    return lib.get(href)


def main():
    parser = argparse.ArgumentParser(
        description="Create publication and distribution on repositories",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    with lib.status_data(parser) as (args, data):

        durations_list = []
        for r in data:
            duration, content = lib.measureit(list_units_in_repo_ver, r['repository_version_href'])
            logging.debug("Repo version %s have %d content units" % (r['repository_version_href'], len(content)))
            durations_list.append(duration)

            durations_content = []
            for c in content
                url = c.get("_href")
                duration, content = lib.measureit(inspect_content, url)
                durations_content.append(duration)
            print("Content inspection duration in %s: %s" % (r['repository_version_href'], lib.data_stats(durations_list)))

        print("Repo version content listing duration: %s" % lib.data_stats(durations_list))

    return 0


if __name__ == '__main__':
    sys.exit(main())
