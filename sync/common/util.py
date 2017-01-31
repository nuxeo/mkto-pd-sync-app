import logging
from functools import wraps


def simple_pluralize(word):
    """
    Simply pluralize word by adding an extra 's' at the end taking into account some exceptions.
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


def memoize(method_name):
    """
    Decorator function that store or retrieve the result of the method it is applied to
    into/from the enclosing class cache.
    :param method_name: The method name that will be used as a key for the cache
    :return: The decorated method result
    """

    def decorator(function):
        @wraps(function)
        def wrapper(self, *args):
            if method_name in self._memo and args in self._memo[method_name]:
                logging.getLogger(__name__).debug('Retrieving function=%s return value from memo', method_name)
                rv = self._memo[method_name][args]
            else:
                if method_name not in self._memo:
                    self._memo[method_name] = {}
                rv = function(self, *args)
                self._memo[method_name][args] = rv
            return rv

        return wrapper

    return decorator


if __name__ == '__main__':
    import doctest

    doctest.testmod()
