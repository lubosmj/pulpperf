import logging
import requests
import random
import string


BASE_ADDR = "http://localhost:24817"
CONTENT_ADDR = "http://localhost:24816"


def add_common_params_and_parse(parser):
    """Add common options to argparse parser"""
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


def get_random_string():
    """Return random string"""
    return ''.join(random.choice(string.ascii_lowercase) for i in range(5))


def get():
    """Wrapper around requests.get with some simplification in our case"""
    pass


def post(url, data):
    """Wrapper around requests.post with some simplification in our case"""
    return requests.post(url=BASE_ADDR+url, data=data).json()
