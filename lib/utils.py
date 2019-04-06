import re
import logging
from copy import deepcopy
from urllib.parse import urlencode

from tornado import gen
from tornado.web import HTTPError
from tornado.httpclient import HTTPRequest, AsyncHTTPClient


def filter_keys(data, keys=None):
    ret = deepcopy(data)
    if keys is None:
        return ret
    elif isinstance(data, dict):
        ret = {k: v for k, v in data.items() if k in keys}

    return ret
