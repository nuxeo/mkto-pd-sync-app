import requests
import logging
import importlib


class PipedriveClient:
    API_ENDPOINT = "https://api.pipedrive.com/v1"

    def __init__(self, api_token):
        self._logger = logging.getLogger(__name__)

        payload = {"api_token": api_token}
        self._session = requests.Session()
        self._session.params = payload

    def get_resource_by_id(self, resource_name, resource_id):
        class_ = getattr(importlib.import_module("pipedrive.resources"), resource_name.capitalize())
        resource = class_(self)
        data = self.get_resource_data(resource_name, resource_id)
        for key in data:
            setattr(resource, key, data[key])
        return resource

    def get_resource_data(self, resource_name, resource_id):
        return self._fetch_data(resource_name + "s", resource_id)  # takes an 's' at the end of the resource name

    def add_resource(self, resource_name, resource_data):
        class_ = getattr(importlib.import_module("pipedrive.resources"), resource_name.capitalize())
        resource = class_(self)
        data = self.set_resource_data(resource_name, resource_data)
        for key in data:
            setattr(resource, key, data[key])
        return resource

    def set_resource_data(self, resource_name, resource_data, resource_id=None):
        return self._push_data(resource_name + "s", resource_data, resource_id)

    def _fetch_data(self, r_name, r_id=None):
        self._logger.debug("Fetching resource %s%s", r_name, " with id %s" % str(r_id) or "")

        url = self._build_url(r_name, r_id)

        r = self._session.get(url)
        data = r.json()

        self._logger.info("URL=%s", r.url)

        if r.status_code == requests.codes.ok:
            if "success" in data and data["success"]:
                if "data" in data:
                    return data["data"]
        else:
            if "error" in data and data["error"]:
                logging.error(data["error"])

        return {}  # TODO: Better exception handling

    def _push_data(self, r_name, r_data, r_id=None):
        self._logger.debug("Pushing resource %s%s", r_name, " with id %s" % str(r_id) or "")

        url = self._build_url(r_name, r_id)

        if r_id is None:  # Add
            r = self._session.post(url, data=r_data)
        else:             # Update
            r = self._session.put(url, json=r_data)

        data = r.json()

        self._logger.info("URL=%s", r.url)

        if r.status_code == 201:
            if "success" in data and data["success"]:
                if "data" in data:
                    return data["data"]
        else:
            if "error" in data and data["error"]:
                logging.error(data["error"])

        return {}  # TODO: Better exception handling

    def _build_url(self, r_name, r_id=None):
        url = self.API_ENDPOINT + "/" + r_name
        if r_id is not None:
            url += "/" + str(r_id)
        return url

    def get_resource_fields(self, resource_name):
        return self._fetch_data(resource_name + "Fields")
