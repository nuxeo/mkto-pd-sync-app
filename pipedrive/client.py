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
        instance = class_(self)
        data = self.get_resource_data(resource_name, resource_id)
        for key in data:
            setattr(instance, key, data[key])
        return instance

    def get_resource_data(self, resource_name, resource_id):
        return self._fetch_data(resource_name.lower() + "s", resource_id)  # takes an 's' at the end of the resource name

    def _fetch_data(self, r_name, r_id=None):
        self._logger.debug("Fetching resource %s with id %s", r_name, str(r_id) or "None")

        url = self._build_url(r_name, r_id)

        r = self._session.get(url)
        data = r.json()

        self._logger.info("URL=%s", r.url)

        if r.status_code == requests.codes.ok:
            if "success" in data and data["success"]:
                if "data" in data:
                    return data["data"]

        return None  # TODO: Exception handling

    def _build_url(self, r_name, r_id=None):
        url = self.API_ENDPOINT + "/" + r_name
        if r_id is not None:
            url += "/" + str(r_id)
        return url

    def get_resource_fields(self, resource_name):
        return self._fetch_data(resource_name.lower() + "Fields")
