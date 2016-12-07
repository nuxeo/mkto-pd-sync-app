import os
import sys
sys.path.insert(0, os.path.abspath('.'))

activate_this = os.path.join(os.path.abspath('.'), 'venv/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

# Monkey-patch requests to make sure that Requests uses URLFetch.
from requests_toolbelt.adapters import appengine
appengine.monkeypatch()

from sync.gae_handler import gae_app as application
