import requests
import tempfile

from utils import measureit
from utils import urljoin

BASE_ADDR = "http://localhost:24817"
CONTENT_ADDR = "http://localhost:24816"


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


def download(base_url, file_name, file_size):
    """Downlad file with expected size and drop it"""
    with tempfile.TemporaryFile() as downloaded_file:
        full_url = urljoin(CONTENT_ADDR, base_url, file_name)
        duration, response = measureit(requests.get, full_url)
        response.raise_for_status()
        downloaded_file.write(response.content)
        assert downloaded_file.tell() == file_size
        return duration
