import logging

logging.basicConfig()
logging.getLogger("marketo").setLevel(logging.DEBUG)
logging.getLogger("pipedrive").setLevel(logging.DEBUG)
