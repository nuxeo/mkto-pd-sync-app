import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load the appropriate libraries on the Python path
sys.path.insert(1, os.environ['GOOGLE_APP_ENGINE'])
sys.path.insert(1, os.environ['GOOGLE_APP_ENGINE'] + '/lib/yaml/lib')
sys.path.insert(1, os.path.abspath('lib'))

import sync
# Make necessary modules visible
import sync.mappings
import sync.tasks
