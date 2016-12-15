import logging

from requests import Session

from .helpers import is_marketo_guid, simple_pluralize
from ..common import memoize


class MarketoClient:
    API_VERSION = 'v1'

    def __init__(self, identity_endpoint, client_id, client_secret, api_endpoint):
        self._logger = logging.getLogger(__name__)
        self._memo = {}

        self._identity_endpoint = identity_endpoint
        self._client_id = client_id
        self._client_secret = client_secret
        self._api_endpoint = api_endpoint

        self._session = Session()

        self._auth_token = self._get_auth_token()

    def _get_auth_token(self):
        auth_url = self._identity_endpoint + '/oauth/token'

        payload = {
            'grant_type': 'client_credentials',
            'client_id': self._client_id,
            'client_secret': self._client_secret
        }

        r = self._session.get(auth_url, params=payload)
        self._logger.info('Called %s', r.url)
        r.raise_for_status()

        auth_data = r.json()

        self._logger.info('access_token=%s acquired expiring in %ss' %
                          (auth_data['access_token'], auth_data['expires_in']))
        return auth_data['access_token']

    @memoize(function_name='get_resource_fields')
    def get_resource_fields(self, resource_name):
        return self._fetch_data(resource_name, 'describe')

    def get_resource_data(self, resource_name, resource_id, filter_type='id', resource_fields=None):
        """
        Load resource data as a dictionary from a request to Marketo result.
        :param resource_name: The resource name (should be the same as the class name)
        :param resource_id: The resource id
        :param resource_fields: The resource fields to consider retrieving
        :param filter_type: The resource field to filter on, default is "id"
        :return: The loaded dara as a dictionary of fields mapped against their value
        """
        data_array = self._fetch_data(resource_name, resource_id, filter_type, resource_fields)
        ret = {}
        if data_array:
            if len(data_array) > 1:
                self._logger.warning('More than one resource=%s found for %s=%s',
                                     resource_name, filter_type, resource_id)
            ret = data_array[0]  # Only one resource handled at a time for now
        return ret

    def set_resource_data(self, resource_name, resource_data, resource_id=None):
        """
        Dump resource data to Marketo.
        :param resource_name: The resource name (should be the same as the class name)
        :param resource_data: The resource data
        :param resource_id: The resource id (update only)
        :return: The dumped data as a dictionary with the id field mapped against its value
        """
        r_data = {
            'action': 'createOrUpdate',
            'input': [resource_data]
        }
        if resource_id:  # Update
            if not is_marketo_guid(resource_id):
                r_data['lookupField'] = 'id'  # Otherwise default would have been "email" for a lead

        data_array = self._push_data(resource_name, r_data)

        ret = {}
        if data_array:
            ret = data_array[0]  # Only one resource handled at a time for now
            if ret['status'] == 'skipped':
                reason = ret['reasons'][0]  # Only one resource handled at a time for now
                self._logger.warning('resource=%s%s has been skipped for reason=%s', resource_name,
                                     ' with id=%s' % resource_id if resource_id is not None else '', reason['message'])
            else:
                self._logger.info('resource=%s%s has been %s', resource_name,
                                  ' with id=%s' % resource_id if resource_id is not None else '', ret['status'])

        return ret

    def _fetch_data(self, r_name, r_id_or_action, r_filter_type=None, r_fields=None):
        self._logger.debug('Fetching resource=%s%s%s%s', r_name,
                           ' (fields=%s)' % r_fields if r_fields is not None else '',
                           ' with id/action=%s' % r_id_or_action.encode('utf-8') if isinstance(r_id_or_action, unicode)
                           else str(r_id_or_action) if r_id_or_action is not None else '',
                           ' with filter_type=%s' % r_filter_type if r_filter_type is not None else '')
        payload = {}

        if r_filter_type:  # Case id
            url = self._build_url(r_name)
            payload['filterValues'] = r_id_or_action
            payload['filterType'] = r_filter_type
        else:  # Case action
            url = self._build_url(r_name, r_id_or_action)

        # Fields to be retrieved should be specified otherwise not all will be by default
        if r_fields:
            payload['fields'] = r_fields

        headers = {'Authorization': 'Bearer %s' % self._auth_token}
        r = self._session.get(url, headers=headers, params=payload)
        self._logger.info('Called url=%s with headers=%s and parameters=%s', r.url, headers, payload)
        r.raise_for_status()

        data = r.json()

        ret = {}
        if 'success' in data:
            if data['success']:
                ret = data['result']
            else:
                error = data['errors'][0]  # Only one resource handled at a time for now
                if error['code'] == '602':
                    self._logger.debug('Token expired, fetching new token to replay request')
                    self._auth_token = self._get_auth_token()
                    ret = self._fetch_data(r_name, r_id_or_action, r_filter_type, r_fields)
                else:
                    self._logger.error('Error=%s', error['message'])

        return ret

    def _push_data(self, r_name, r_data, r_action=None):
        self._logger.debug('Pushing resource=%s with data=%s%s', r_name, r_data,
                           ' with action=%s' % str(r_action) if r_action is not None else '')
        url = self._build_url(r_name, r_action)

        headers = {'Authorization': 'Bearer %s' % self._auth_token}
        r = self._session.post(url, headers=headers, json=r_data)  # POST request for creating and updating
        self._logger.info('Called url=%s with headers=%s and body=%s', r.url, headers, r_data)
        r.raise_for_status()

        data = r.json()

        ret = {}
        if 'success' in data:
            if data['success']:
                ret = data['result']
            else:
                error = data['errors'][0]  # Only one resource handled at a time for now
                if error['code'] == '602':
                    self._logger.debug('Token expired, fetching new token to replay request')
                    self._auth_token = self._get_auth_token()
                    ret = self._push_data(r_name, r_data, r_action)
                else:
                    self._logger.error('Error=%s', error['message'])

        return ret

    def _build_url(self, r_name, r_action=None):
        url = '%s/%s/%s' % (self._api_endpoint, self.API_VERSION,
                            simple_pluralize(r_name))  # Resource name should be plural form
        if r_action:
            url += '/' + r_action
        url += '.json'
        return url

    # Play carefully with this method!
    def delete_resource(self, r_name, r_id, r_id_dedupe_field=None):
        ret = {}

        if r_id:
            self._logger.warning('Deleting resource=%s with id=%s', r_name, str(r_id))

            r_data = {}
            if r_id_dedupe_field:
                r_id_field = r_id_dedupe_field
                r_data['deleteBy'] = 'dedupeFields'
            else:
                if is_marketo_guid(r_id):
                    r_id_field = 'marketoGUID'
                    r_data['deleteBy'] = 'idField'
                else:
                    r_id_field = 'id'
            r_data['input'] = [{r_id_field: r_id}]

            data_array = self._push_data(r_name, r_data, 'delete')

            if data_array:
                ret = data_array[0]  # Only one resource handled at a time for now
                if ret['status'] == 'skipped':
                    reason = ret['reasons'][0]  # Only one resource handled at a time for now
                    self._logger.warning('resource=%s with id=%s has been skipped for reason=%s', r_name, r_id,
                                         reason['message'])
                else:
                    self._logger.info('resource=%s with id=%s has been %s', r_name, r_id, ret['status'])
        else:
            self._logger.warning('Cannot delete resource=%s: invalid id (null or empty)', r_name)

        return ret
