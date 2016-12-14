import logging
from functools import wraps


def memoize(function_name):
    def decorator(function):
        @wraps(function)
        def wrapper(self, *args):
            if function_name in self._memo and args in self._memo[function_name]:
                logging.getLogger(__name__).debug('Retrieving function=%s return value from memo', function_name)
                rv = self._memo[function_name][args]
            else:
                if function_name not in self._memo:
                    self._memo[function_name] = {}
                rv = function(self, *args)
                self._memo[function_name][args] = rv
            return rv

        return wrapper

    return decorator
