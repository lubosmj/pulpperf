import logging
import json
from contextlib import contextmanager


def add_common_params_and_parse(parser):
    """Add common options to argparse parser"""
    parser.add_argument('--status', default='./status-data.json',
                        help='file from where to load and to which to dump status data')
    parser.add_argument('--debug', action='store_true',
                        help='show debug output')
    args = parser.parse_args()

    # By default, set logging to INFO
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Show args
    logging.debug(args)

    return args


@contextmanager
def status_data(parser):
    # Process params
    args = add_common_params_and_parse(parser)

    # Load status data if any
    try:
        with open(args.status, 'r') as fp:
            data = json.load(fp)
    except FileNotFoundError:
        data = []

    try:
        yield args, data
    finally:
        # Save final status data
        with open(args.status, 'w+') as fp:
            json.dump(data, fp, sort_keys=True, indent=4)
