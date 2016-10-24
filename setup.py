from setuptools import setup

setup(name='Sync App',
      version='1.0',
      description='Marketo-Pipedrive Synchronization Application',
      author='Helene Jonin',
      packages=['marketo', 'pipedrive', 'sync'],
      install_requires=['flask', 'pycountry']
     )
