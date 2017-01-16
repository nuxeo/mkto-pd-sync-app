from functools import wraps

from flask import request
from google.appengine.ext import ndb

from .common import Error


class InvalidUsage(Error):
    """Exception raised for errors in the authentication.
    """
    status_code = 400  # "Bad Request" HTTP response code

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


def authenticate(authorized_keys):
    """
    Decorator function that blocks the route it is applied to access if it is not properly authenticated.
    :param authorized_keys: A list of authorized keys
    :return: The decorated method result in case of proper authentication, otherwise raise an error
    """

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if request.args.get('api_key') and request.args.get('api_key') in authorized_keys.values():
                return function(*args, **kwargs)
            else:
                raise InvalidUsage('Authentication required', 401)

        return wrapper

    return decorator


class EnqueuedTask(ndb.Model):
    """
    The task model in the datastore.
    """
    name = ndb.StringProperty()
    params = ndb.JsonProperty(indexed=True)
    ata = ndb.DateTimeProperty()
