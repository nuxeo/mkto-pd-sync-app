import os
import sys

sys.path.insert(0, os.path.abspath('.'))

activate_this = os.path.join(os.path.abspath('.'), 'venv/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

from datadog import initialize, ThreadStats
import sync

config = sync.app.config

initialize(api_key=config['DATADOG_API_KEY'])

t_stats = ThreadStats()
t_stats.start(flush_in_thread=False)

from integration import app as application
