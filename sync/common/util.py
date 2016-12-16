import logging
from functools import wraps


def simple_pluralize(word):
    """
    Simply pluralize word by adding an extra 's' at the end
    taking into account some exceptions.
    >>> simple_pluralize('lead')
    'leads'
    >>> simple_pluralize('opportunity')
    'opportunities'
    """
    plural = word
    if word.endswith('y'):
        plural = plural[:-1] + 'ie'
    plural += 's'
    return plural


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
