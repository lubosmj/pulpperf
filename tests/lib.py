import logging
import requests
import random
import string
import time
import datetime
import statistics
import json
import tempfile
from contextlib import contextmanager


BASE_ADDR = "http://localhost:24817"
CONTENT_ADDR = "http://localhost:24816"

DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"


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


def get_random_string():
    """Return random string"""
    return ''.join(random.choice(string.ascii_lowercase) for i in range(5))


def get(url, params={}):
    """Wrapper around requests.get with some simplification in our case"""
    # TODO: pagination and results
    url = BASE_ADDR + url

    r = requests.get(url=url, params=params)
    r.raise_for_status()
    return r.json()


def post(url, data):
    """Wrapper around requests.post with some simplification in our case"""
    url = BASE_ADDR + url

    r = requests.post(url=url, data=data)
    r.raise_for_status()
    return r.json()


def _urljoin(*args):
    # This sucks, but works. Better ways welcome.
    return '/'.join([i.lstrip('/').rstrip('/') for i in args])


def measureit(func, *args, **kwargs):
    logging.debug("Measuring duration of %s %s %s" % (func.__name__, args, kwargs))
    before = time.clock()
    out = func(*args, **kwargs)
    after = time.clock()
    return after - before, out


def download(base_url, file_name, file_size):
    """Downlad file with expected size and drop it"""
    with tempfile.TemporaryFile() as downloaded_file:
        full_url = _urljoin(CONTENT_ADDR, base_url, file_name)
        duration, response = measureit(requests.get, full_url)
        response.raise_for_status()
        downloaded_file.write(response.content)
        assert downloaded_file.tell() == file_size
        return duration


def wait_for_tasks(tasks):
    """Wait for tasks to finish, returning task info. If we time out,
    list of None is returned."""
    start = time.time()
    out = []
    timeout = 7200
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


def parse_pulp_manifest(url):
    response = requests.get(url)
    response.text.split("\n")
    data = [i.strip().split(',') for i in response.text.split("\n")]
    return [(i[0], i[1], int(i[2])) for i in data if i != ['']]


def tasks_table(tasks):
    """Return overview of tasks in the table"""
    out = "%56s\t%27s\t%27s\t%27s\t%s\n" \
        % ('task', 'created', 'started', 'finished', 'state')
    for t in tasks:
        out += "%s\t%s\t%s\t%s\t%s\n" \
            % (t['_href'], t['_created'], t['started_at'], t['finished_at'],
               t['state'])
    return out


def tasks_min_max_table(tasks):
    """Return overview of tasks dates min and max in a table"""
    out = "\n%11s\t%27s\t%27s\n" % ('field', 'min', 'max')
    for f in ('_created', 'started_at', 'finished_at'):
        sample = [datetime.datetime.strptime(t[f], DATETIME_FMT)
                  for t in tasks]
        out += "%s\t%s\t%s\n" \
            % (f,
               min(sample).strftime(DATETIME_FMT),
               max(sample).strftime(DATETIME_FMT))
    return out


def data_stats(data):
    return {
        'samples': len(data),
        'min': min(data),
        'max': max(data),
        'mean': statistics.mean(data),
        'stdev': statistics.stdev(data) if len(data) > 1 else 0.0,
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
