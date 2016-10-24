import sys
sys.path.insert(0, '/var/www/sync_app')

activate_this = '/var/www/sync_app/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from sync import app as application
