from . import get_config

from flask import request
from functools import wraps


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
