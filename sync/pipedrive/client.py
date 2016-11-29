from ..common import memoize

from requests import HTTPError, Session

import logging


class PipedriveClient:
    API_ENDPOINT = "https://api.pipedrive.com/v1"

    def __init__(self, api_token):
        self._logger = logging.getLogger(__name__)
        self._memo = {}

        payload = {"api_token": api_token}
        self._session = Session()
        self._session.params = payload

    @memoize(function_name="get_resource_fields")
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

        if not r_id_or_action:  # Create
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

    def _push_data_json(self, r_name, r_data, r_id_or_action=None):
        self._logger.debug("Pushing resource %s%s", r_name,
                           " with id/action %s" % str(r_id_or_action) if r_id_or_action is not None else "")
        url = self._build_url(r_name, r_id_or_action)

        if not r_id_or_action:  # Create
            r = self._session.post(url, json=r_data)
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
        if r_id_or_action:
            url += "/" + str(r_id_or_action)
        return url

    # Play carefully with this method!
    def delete_resource(self, r_name, r_id):
        ret = {}

        if r_id:
            self._logger.warning("Deleting resource %s with id %s", r_name, str(r_id))

            url = self._build_url(r_name + "s", r_id)  # Takes an 's' at the end of the resource name

            r = self._session.delete(url)
            self._logger.info("Called %s", r.url)
            try:
                r.raise_for_status()
            except HTTPError as e:
                if e.response.status_code != 410:  # Pipedrive seems to raise a 410 error during deletion
                    raise e

            data = r.json()

            if "success" in data:
                if data["success"]:
                    ret = data["data"]
                else:
                    self._logger.error("Error: %s", data["error"])
        else:
            self._logger.warning("Null id given")

        return ret

    @memoize(function_name="get_filters")
    def _get_filters(self):
        return self._fetch_data("filters")

    def get_organization_email_domain_filter(self, filter_value):
        filters = self._get_filters()

        filter_name = "Real Time API filter"
        # Search for existing filter
        filter_id = next((filter_["id"] for filter_ in filters if filter_["name"] == filter_name), None)
        if filter_id:
            filter_ = self._fetch_data("filters", filter_id)  # Ensure filter still exists
            if not filter_:  # Case it does not
                filter_id = None
                self._memo["get_filters"] = {}  # Reset cache because the filter has probably been deleted

        r_data = {
            "name": filter_name,
            "conditions": {
                "glue": "and",
                "conditions": [
                    {
                        "glue": "and",
                        "conditions": [
                            {
                                "object": "organization",
                                "field_id": "4014",
                                "operator": "=",
                                "value": filter_value,
                                "extra_value": None
                            }
                        ]
                    },
                    {
                        "glue": "or",
                        "conditions": []
                    }
                ]
            },
            "type": "org"
        }

        ret = self._push_data_json("filters",  r_data, filter_id)  # Create or update filter

        if not filter_id and ret:
            self._memo["get_filters"] = {}  # Reset cache because a filter has been created

        return ret
