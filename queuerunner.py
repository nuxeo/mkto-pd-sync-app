from pickle import dumps, loads
from sync import app, get_redis


def queue_daemon(app, rv_ttl=500):
    while 1:
        msg = get_redis().blpop(app.config['REDIS_QUEUE_KEY'])
        func, key, args, kwargs = loads(msg[1])
        try:
            rv = func(*args, **kwargs)
        except Exception, e:
            rv = e
        if rv is not None:
            get_redis().set(key, dumps(rv))
            get_redis().expire(key, rv_ttl)

ctx = app.test_request_context()
ctx.push()
queue_daemon(app)
