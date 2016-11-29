from . import get_config, get_redis

from flask import request
from functools import wraps
from pickle import dumps, loads
from uuid import uuid4


class InvalidUsage(Exception):
    """Exception raised for errors in the authentication.
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.args.get('api_key') and request.args.get('api_key') in get_config('FLASK_AUTHORIZED_KEYS'):
            return f(*args, **kwargs)
        else:
            raise InvalidUsage('Authentication required', 401)
    return decorated_function


class DelayedResult(object):
    def __init__(self, key):
        self.key = key
        self._rv = None

    @property
    def return_value(self):
        if self._rv is None:
            rv = get_redis().get(self.key)
            if rv is not None:
                self._rv = loads(rv)
        return self._rv


def queuefunc(f):
    def delay(*args, **kwargs):
        qkey = get_config("REDIS_QUEUE_KEY")
        key = '%s:result:%s' % (qkey, str(uuid4()))
        s = dumps((f, key, args, kwargs))
        get_redis().rpush(get_config("REDIS_QUEUE_KEY"), s)
        return DelayedResult(key)
    f.delay = delay
    return f
