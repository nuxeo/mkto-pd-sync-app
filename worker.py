# Monkey-patch requests to make sure that Requests uses URLFetch.
from requests_toolbelt.adapters import appengine

appengine.monkeypatch()

from sync.gae_handler import gae_app as application
