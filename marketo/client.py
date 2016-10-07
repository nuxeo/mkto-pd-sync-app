import requests
import logging
import importlib


class MarketoClient:
    API_VERSION = "v1"

    def __init__(self, identity_endpoint, client_id, client_secret, api_endpoint):
        self._logger = logging.getLogger(__name__)

        self._identity_endpoint = identity_endpoint
        self._client_id = client_id
        self._client_secret = client_secret
        self._api_endpoint = api_endpoint

        self._session = requests.Session()

        self._auth_token = self._get_auth_token()

    def _get_auth_token(self):
        auth_url = self._identity_endpoint + "/oauth/token"

        payload = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret
        }

        r = self._session.get(auth_url, params=payload)
        self._logger.info("Called %s", r.url)
        r.raise_for_status()

        auth_data = r.json()

        self._logger.info("Access token acquired: %s expiring in %ss" %
            (auth_data['access_token'], auth_data['expires_in']))
        return auth_data['access_token']

    def get_resource_by_id(self, resource_name, resource_id, resource_fields=None):
        class_ = getattr(importlib.import_module("marketo.resources"), resource_name.capitalize())
        resource = class_(self)
        data = self.get_resource_data(resource_name, resource_id, resource_fields)
        for key in data:
            setattr(resource, key, data[key])
        return resource

    def get_resource_data(self, resource_name, resource_id, resource_fields):
        data_array = self._fetch_data(resource_name, resource_id, resource_fields)
        if data_array:
            return data_array[0]
        return {}

    # def add_resource(self, resource_name, resource_data):
    #     class_ = getattr(importlib.import_module("pipedrive.resources"), resource_name.capitalize())
    #     resource = class_(self)
    #     data = self.set_resource_data(resource_name, resource_data)
    #     for key in data:
    #         setattr(resource, key, data[key])
    #     return resource
    #
    # def set_resource_data(self, resource_name, resource_data, resource_id=None):
    #     return self._push_data(resource_name + "s", resource_data, resource_id)

    def _fetch_data(self, r_name, r_id=None, r_fields=None):
        self._logger.debug("Fetching resource %s%s", r_name, " with id %s" % str(r_id) or "")

        url = self._build_url(r_name, r_id)

        payload = {}
        if r_fields is not None:
            payload["fields"] = r_fields

        headers = {"Authorization": "Bearer %s" % self._auth_token}
        r = self._session.get(url, headers=headers, params=payload)
        self._logger.info("Called %s", r.url)
        r.raise_for_status()

        data = r.json()

        if "success" in data and data["success"]:
            if "result" in data:
                return data["result"]
        else:
            if "errors" in data and data["errors"]:
                error = data["errors"][0]
                if error["code"] in ("601", "602"):
                    self._logger.debug("Token expired or invalid, fetching new token to replay request")
                    self._auth_token = self._get_auth_token()
                else:
                    logging.error(error["message"])

        return {}  # TODO: Better exception handling

    # def _push_data(self, r_name, r_data, r_id=None):
    #     self._logger.debug("Pushing resource %s%s", r_name, " with id %s" % str(r_id) or "")
    #
    #     url = self._build_url(r_name, r_id)
    #
    #     if r_id is None:  # Add
    #         r = self._session.post(url, data=r_data)
    #     else:             # Update
    #         r = self._session.put(url, json=r_data)
    #
    #     data = r.json()
    #
    #     self._logger.info("URL=%s", r.url)
    #
    #     if r.status_code == 201:
    #         if "success" in data and data["success"]:
    #             if "data" in data:
    #                 return data["data"]
    #     else:
    #         if "error" in data and data["error"]:
    #             logging.error(data["error"])
    #
    #     return {}  # TODO: Better exception handling

    def _build_url(self, r_name, r_id=None):
        url = "%s/%s/%s" % (self._api_endpoint, self.API_VERSION, r_name)
        if r_id is not None:
            url += "/" + str(r_id)
        else:
            url += "s"
        url += ".json"
        return url

    def get_resource_fields(self, resource_name):
        return self._fetch_data(resource_name + "s", "describe")  # takes an 's' at the end of the resource name
