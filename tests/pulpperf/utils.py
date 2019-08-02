import logging
import random
import time
import string
import requests

from interact import get


def get_random_string():
    """Return random string"""
    return ''.join(random.choice(string.ascii_lowercase) for i in range(5))


def urljoin(*args):
    # This sucks, but works. Better ways welcome.
    return '/'.join([i.lstrip('/').rstrip('/') for i in args])


def measureit(func, *args, **kwargs):
    logging.debug("Measuring duration of %s %s %s" % (func.__name__, args, kwargs))
    before = time.clock()
    out = func(*args, **kwargs)
    after = time.clock()
    return after - before, out


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
