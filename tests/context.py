import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Make sure your test runner has the appropriate libraries on the Python load path
sys.path.insert(1, '/Users/helene/SDK/google-cloud-sdk/platform/google_appengine')
sys.path.insert(1, '/Users/helene/SDK/google-cloud-sdk/platform/google_appengine/lib/yaml/lib')

import sync
import sync.tasks
