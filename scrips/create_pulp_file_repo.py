#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
import argparse
import os
import errno
import csv
import hashlib


def main():
    rp_parser = argparse.ArgumentParser(
        description="Create Pulp file repo",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    rp_parser.add_argument('--files-count', default=10, type=int,
                           help='number of files in the repo')
    rp_parser.add_argument('--file-size', default=50, type=int,
                           help='size of files in repository in bytes')
    rp_parser.add_argument('--file-prefix', default='a',
                           help='file prefix used for both name and content so'
                                ' you have different files in similar repos')
    rp_parser.add_argument('--directory', default='/tmp/aaa',
                           help='repo directory path')
    rp_parser.add_argument('--debug', action='store_true',
                           help='show debug output')
    args = rp_parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.debug(args)

    pulp_manifest = []

    logging.info('Generating %s files with size %s into %s'
                 % (args.files_count, args.file_size, args.directory))
    for i in range(args.files_count):
        pulp_manifest.append(create_file(args.directory, i, args.file_prefix,
                                         args.file_size))

    logging.info('Saving PULP_MANIFEST into %s' % args.directory)
    dump_manifest(args.directory, pulp_manifest)

    logging.info('Finished creating repo in %s' % args.directory)


def create_file(directory, file_id, file_prefix, file_size,
                file_suffix='.iso'):
    """Create file with defined size and return info needed for
    PULP_MANIFEST"""

    file_name = file_prefix + str(file_id) + file_suffix
    file_path = os.path.join(directory, file_name)
    file_content = file_prefix + str(file_id).zfill(
        file_size - len(file_prefix))
    file_content = file_content.encode()

    assert len(file_content) == file_size

    try:
        os.makedirs(os.path.dirname(file_path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    logging.debug('Writing file %s' % file_path)
    with open(file_path, 'wb') as fp:
        fp.write(file_content)
    file_checksum = hashlib.sha256(file_content).hexdigest()

    return (file_name, file_checksum, file_size)


def dump_manifest(directory, content):
    """Dump PULP_MANIFEST file into specified directory"""

    manifest_path = os.path.join(directory, 'PULP_MANIFEST')

    logging.debug('Writing manifest with %s records to %s'
                  % (len(manifest_path), manifest_path))
    with open(manifest_path, mode='w') as fp:
        writer = csv.writer(fp, delimiter=',', quoting=csv.QUOTE_NONE)
        for row in content:
            writer.writerow(row)


if __name__ == '__main__':
    main()
