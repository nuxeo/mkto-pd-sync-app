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
        self._logger.debug("Fetching access token")
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

    def get_resource_fields(self, resource_name):
        return self._fetch_data(resource_name, "describe")

    def get_resource_by_id(self, resource_name, resource_id, resource_fields=None):
        resource_class = getattr(importlib.import_module("marketo.resources"), resource_name.capitalize())
        resource = resource_class(self)
        data = self.get_resource_data(resource_name, resource_id, resource_fields)
        for key in data:
            setattr(resource, key, data[key])
        return resource

    def get_resource_data(self, resource_name, resource_id, resource_fields):
        data_array = self._fetch_data(resource_name, resource_id, resource_fields)
        ret = {}
        if data_array:
            ret = data_array[0]
        return ret

    def add_resource(self, resource_name, resource_data):
        resource_class = getattr(importlib.import_module("marketo.resources"), resource_name.capitalize())
        resource = resource_class(self)
        data = self.set_resource_data(resource_name, resource_data)
        # Only id is returned
        if "id" in data:
            setattr(resource, "id", data["id"])
        for key in resource_data:
            setattr(resource, key, resource_data[key])
        return resource

    def set_resource_data(self, resource_name, resource_data, resource_id=None):
        r_data = {
            "action": "createOrUpdate",
            "input": [resource_data]
        }
        if resource_id is not None:
            resource_data["id"] = resource_id
            r_data["lookupField"] = "id"
        data_array = self._push_data(resource_name, r_data)
        ret = {}
        if data_array:
            ret = data_array[0]
        if ret["status"] == "skipped":
            reason = ret["reasons"][0]
            self._logger.warning(reason["message"])
        else:
            self._logger.info("Resource has been %s", ret["status"])
        return ret

    def _fetch_data(self, r_name, r_id_or_action=None, r_fields=None):
        self._logger.debug("Fetching resource %s%s", r_name, " with id/action %s" % str(r_id_or_action) or "")

        url = self._build_url(r_name, r_id_or_action)

        # Fields to retrieve have to be specified because not all loaded by default
        payload = {}
        if r_fields is not None:
            payload["fields"] = r_fields

        headers = {"Authorization": "Bearer %s" % self._auth_token}
        r = self._session.get(url, headers=headers, params=payload)
        self._logger.info("Called %s", r.url)
        r.raise_for_status()

        data = r.json()

        ret = {}
        if "success" in data:
            if data["success"]:
                ret = data["result"]
            else:
                error = data["errors"][0]
                if error["code"] == "602":
                    self._logger.debug("Token expired, fetching new token to replay request")
                    self._auth_token = self._get_auth_token()
                    ret = self._fetch_data(r_name, r_id_or_action, r_fields)
                else:
                    self._logger.error(error["message"])

        return ret

    def _push_data(self, r_name, r_data, r_id_or_action=None):
        self._logger.debug("Pushing resource %s%s", r_name, " with id/action %s" % str(r_id_or_action) or "")

        url = self._build_url(r_name, r_id_or_action)

        headers = {"Authorization": "Bearer %s" % self._auth_token}
        r = self._session.post(url, headers=headers, json=r_data)  # POST to add and update
        self._logger.info("Called %s", r.url)
        r.raise_for_status()

        data = r.json()

        ret = {}
        if "success" in data:
            if data["success"]:
                ret = data["result"]
            else:
                error = data["errors"][0]
                if error["code"] == "602":
                    self._logger.debug("Token expired, fetching new token to replay request")
                    self._auth_token = self._get_auth_token()
                    ret = self._push_data(r_name, r_data, r_id_or_action)
                else:
                    self._logger.error(error["message"])

        return ret

    def _build_url(self, r_name, r_id_or_action=None):
        url = "%s/%s/%s" % (self._api_endpoint, self.API_VERSION, r_name + "s")  # Takes an 's' at the end of the resource name
        if r_id_or_action is not None:
            url += "/" + str(r_id_or_action)
        url += ".json"
        return url

    # Play carefully with this method!
    def delete_resource(self, r_name, r_id):
        self._logger.warning("Deleting resource %s with id %s", r_name, str(r_id))

        r_data = {
            "input": [{"id": r_id}]
        }
        data_array = self._push_data(r_name, r_data, "delete")
        ret = {}
        if data_array:
            ret = data_array[0]
        return ret
