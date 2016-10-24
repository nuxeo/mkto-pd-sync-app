from requests import Session

import logging


class PipedriveClient:
    API_ENDPOINT = "https://api.pipedrive.com/v1"

    def __init__(self, api_token):
        self._logger = logging.getLogger(__name__)

        payload = {"api_token": api_token}
        self._session = Session()
        self._session.params = payload

    def get_resource_fields(self, resource_name):
        return self._fetch_data(resource_name + "Fields")

    def get_resource_data(self, resource_name, resource_id, resource_fields=None):
        """
        Load resource data as a dictionary from a request to Pipedrive result.
        :param resource_name: The resource name (should be the same as the class name)
        :param resource_id: The resource id
        :param resource_fields: The resource fields to consider retrieving, default are all fields
        :return: The loaded dara as a dictionary of fields mapped against their value
        """
        return self._fetch_data(resource_name + "s",  # Takes an 's' at the end of the resource name
                                resource_id, resource_fields)

    def set_resource_data(self, resource_name, resource_data, resource_id=None):
        """
        Dump resource data to Pipedrive.
        :param resource_name: The resource name (should be the same as the class name)
        :param resource_data: The resource data
        :param resource_id: The resource id (update only)
        :return: The dumped data as a dictionary of field mapped against their value
        """
        return self._push_data(resource_name + "s",  # Takes an 's' at the end of the resource name
                               resource_data, resource_id)

    def _fetch_data(self, r_name, r_id_or_action=None, r_fields=None):
        self._logger.debug("Fetching resource %s%s", r_name,
                           " with id/action %s" % str(r_id_or_action) if r_id_or_action is not None else "")
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
        self._logger.debug("Pushing resource %s%s", r_name,
                           " with id/action %s" % str(r_id_or_action) if r_id_or_action is not None else "")
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
