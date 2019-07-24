import logging
import requests
import random
import string
import time
import datetime
import statistics


BASE_ADDR = "http://localhost:24817"
CONTENT_ADDR = "http://localhost:24816"

DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"


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


def get(url):
    """Wrapper around requests.get with some simplification in our case"""
    url = BASE_ADDR + url

    r = requests.get(url=url)
    r.raise_for_status()
    return r.json()


def post(url, data):
    """Wrapper around requests.post with some simplification in our case"""
    url = BASE_ADDR + url

    r = requests.post(url=url, data=data)
    r.raise_for_status()
    return r.json()


def wait_for_tasks(tasks):
    """Wait for tasks to finish, returning task info. If we time out,
    list of None is returned."""
    start = time.time()
    out = []
    timeout = 60
    step = 3
    for t in tasks:
        while True:
            now = time.time()
            if now >= start + timeout:
                out.append(None)
                break
            response = get(t)
            if response['state'] in ('failed', 'cancelled', 'completed'):
                out.append(response)
                break
            else:
                time.sleep(step)
    return out


def tasks_table(tasks):
    """Return overview of tasks in the table"""
    out = ""
    for t in tasks:
        out += "%s\t%s\t%s\t%s\t%s\n" \
            % (t['_href'], t['_created'], t['started_at'], t['finished_at'],
               t['state'])
    return out


def data_stats(data):
    return {
        'min': min(data),
        'max': max(data),
        'mean': statistics.mean(data),
        'stdev': statistics.stdev(data),
    }


def tasks_waiting_time(tasks):
    """Analyse tasks waiting time (i.e. started_at - _created)"""
    durations = []
    for t in tasks:
        diff = datetime.datetime.strptime(t['started_at'], DATETIME_FMT) \
            - datetime.datetime.strptime(t['_created'], DATETIME_FMT)
        durations.append(diff.total_seconds())
    return data_stats(durations)


def tasks_service_time(tasks):
    """Analyse tasks service time (i.e. finished_at - started_at)"""
    durations = []
    for t in tasks:
        diff = datetime.datetime.strptime(t['finished_at'], DATETIME_FMT) \
            - datetime.datetime.strptime(t['started_at'], DATETIME_FMT)
        durations.append(diff.total_seconds())
    return data_stats(durations)
