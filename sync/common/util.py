from functools import wraps


def memoize(function_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(self, *args):
            if function_name in self._memo and args in self._memo[function_name]:
                rv = self._memo[function_name][args]
            else:
                if function_name not in self._memo:
                    self._memo[function_name] = {}
                rv = f(self, *args)
                self._memo[function_name][args] = rv
            return rv
        return decorated_function
    return decorator
