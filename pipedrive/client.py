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

    def get_resource_fields(self, resource_name):
        return self._fetch_data(resource_name + "Fields")

    def get_resource_by_id(self, resource_name, resource_id, resource_fields=None):
        resource_class = getattr(importlib.import_module("pipedrive.resources"), resource_name.capitalize())
        resource = resource_class(self)
        data = self.get_resource_data(resource_name, resource_id, resource_fields)
        # Fill object
        for key in data:
            setattr(resource, key, self._get_data_value(data[key]))
        return resource

    def get_resource_data(self, resource_name, resource_id, resource_fields=None):
        """
        Load resource data as a dictionary from request to Pipedrive result.
        :param resource_name: The resource name (should be the same as class name)
        :param resource_id: The resource id
        :param resource_fields: The resource fields to consider retrieving
        :return: A dictionary of fields
        """
        return self._fetch_data(resource_name + "s", resource_id, resource_fields)  # Takes an 's' at the end of the resource name

    def add_resource(self, resource_name, resource_data):
        resources_class = getattr(importlib.import_module("pipedrive.resources"), resource_name.capitalize())
        resource = resources_class(self)
        data = self.set_resource_data(resource_name, resource_data)
        for key in data:
            setattr(resource, key, self._get_data_value(data[key]))
        return resource

    def _get_data_value(self, value):
        new_value = value
        if type(value) is dict and "value" in value:  # "Flatten" complex field value such as org_id
            new_value = value["value"]
        elif type(value) is list:  # In case of list, keep only primary value and "flatten" field value
            for v in value:
                if v["primary"]:
                    new_value = v["value"]
        return new_value

    def set_resource_data(self, resource_name, resource_data, resource_id=None):
        """
        Dump resource data to Pipedrive.
        :param resource_name: The resource name (should be the same as class name)
        :param resource_data: The resource data
        :param resource_id: The resource id
        :return: The dumped data as a dictionary of field
        """
        return self._push_data(resource_name + "s", resource_data, resource_id)  # Takes an 's' at the end of the resource name

    def find_resource_by_name(self, resource_name, resource_term):
        resource_class = getattr(importlib.import_module("pipedrive.resources"), resource_name.capitalize())
        resource = resource_class(self)
        data_array = self.get_resource_data(resource_name, "find", {"term": resource_term})
        if data_array:
            data = data_array[0]  # Assume first result is the right one
            for key in data:
                setattr(resource, key, data[key])
        return resource

    def _fetch_data(self, r_name, r_id_or_action=None, r_fields=None):
        self._logger.debug("Fetching resource %s%s", r_name, " with id/action %s" % str(r_id_or_action) or "")

        url = self._build_url(r_name, r_id_or_action)

        payload = r_fields or {}
        r = self._session.get(url, params=payload)
        self._logger.info("Called %s", r.url)
        r.raise_for_status()

        data = r.json()

        ret = {}
        if "success" in data:
            if data["success"]:
                ret = data["data"]
            else:
                self._logger.error("Error: %s", data["error"])

        return ret

    def _push_data(self, r_name, r_data, r_id_or_action=None):
        self._logger.debug("Pushing resource %s%s", r_name, " with id/action %s" % str(r_id_or_action) or "")

        url = self._build_url(r_name, r_id_or_action)

        if r_id_or_action is None:  # Create
            r = self._session.post(url, data=r_data)
        else:  # Update
            r = self._session.put(url, json=r_data)
        self._logger.info("Called %s", r.url)
        r.raise_for_status()

        data = r.json()

        ret = {}
        if "success" in data:
            if data["success"]:
                ret = data["data"]
            else:
                self._logger.error("Error: %s", data["error"])

        return ret

    def _build_url(self, r_name, r_id_or_action=None):
        url = self.API_ENDPOINT + "/" + r_name
        if r_id_or_action is not None:
            url += "/" + str(r_id_or_action)
        return url

    # Play carefully with this method!
    def delete_resource(self, r_name, r_id):
        self._logger.warning("Deleting resource %s with id %s", r_name, str(r_id))

        url = self._build_url(r_name + "s", r_id)  # Takes an 's' at the end of the resource name

        r = self._session.delete(url)
        self._logger.info("Called %s", r.url)
        r.raise_for_status()

        data = r.json()

        ret = {}
        if "success" in data:
            if data["success"]:
                ret = data["data"]
            else:
                self._logger.error("Error: %s", data["error"])

        return ret
