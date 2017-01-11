import importlib
import logging

from requests import Session

from .helpers import is_marketo_guid
from ..common import memoize, simple_pluralize


class MarketoClient:
    """
    Simple client that make calls to Marketo REST API.
    """

    API_VERSION = 'v1'

    def __init__(self, identity_endpoint, client_id, client_secret, api_endpoint):
        self._logger = logging.getLogger(__name__)  # The class logger
        self._memo = {}  # The class cache

        self._identity_endpoint = identity_endpoint
        self._client_id = client_id
        self._client_secret = client_secret
        self._api_endpoint = api_endpoint

        self._session = Session()  # Reuse session for better performance within a single instance of the client

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

    @memoize(method_name='get_entity_fields')
    def get_entity_fields(self, entity_name):
        """
        Return an entity schema loaded from Marketo.
        :param entity_name: The entity name (should be the same as the class name)
        :return: A list of available fields for interaction via the API.
        """
        return self._fetch_data(entity_name, 'describe')

    def get_entity_data(self, entity_name, entity_id, entity_id_field, entity_fields=None):
        """
        Return an entity data loaded from Marketo.
        :param entity_name: The entity name (should be the same as the class name)
        :param entity_id: The entity id
        :param entity_id_field: The entity field to filter on, default is "id"
        :param entity_fields: The entity fields to return, default if not specified
        :return: A dictionary of field keys mapped against their value for the entity
        """
        data_array = self._fetch_data(entity_name, entity_id, entity_id_field, entity_fields)
        data = {}
        if data_array:
            # Should only be one entity
            if len(data_array) > 1:
                self._logger.warning('More than one entity=%s found for %s=%s', entity_name, entity_id_field, entity_id)
            data = data_array[0]
        return data

    def get_entities(self, entity_name, entity_ids, entity_id_field, entity_fields=None):
        """
        Load multiple entities from Marketo.
        :param entity_name: The entity name (should be the same as the class name)
        :param entity_ids: A list of entity ids to load
        :param entity_id_field: The entity field to filter on, default is "id"
        :param entity_fields: The entity fields to return, default if not specified
        :return: The loaded entities
        """
        data_array = self._fetch_data(entity_name, entity_ids, entity_id_field, entity_fields)
        entities = []
        if data_array:
            entities_module = importlib.import_module('.entities', __package__)
            entity_class = getattr(entities_module, entity_name.capitalize())
            for data in data_array:
                entity = entity_class(self)
                entity.init(data)
                entities.append(entity)
        return entities

    def put_entity_data(self, entity_name, entity_data, entity_id=None):
        """
        Dump an entity data to Marketo.
        :param entity_name: The entity name (should be the same as the class name)
        :param entity_data: The entity data
        :param entity_id: The entity id (update only)
        :return: A dictionary of field keys mapped against their value for the entity (id field only)
        """
        payload = {
            'action': 'createOrUpdate',
            'input': [entity_data]
        }

        if entity_name == 'lead' and entity_id:  # If lead update
            payload['lookupField'] = 'id'  # Set lookup field from default "email" to "id"

        data_array = self._push_data(entity_name, payload)

        return_data = {}
        if data_array:
            return_data = data_array[0]  # Should only be one entity
            if return_data['status'] == 'skipped':
                for reason in return_data['reasons']:
                    self._logger.warning('entity=%s%s has been skipped for reason=%s', entity_name,
                                         ' with id=%s' % entity_id if entity_id is not None else '', reason['message'])
            else:
                self._logger.info('entity=%s%s has been %s', entity_name,
                                  ' with id=%s' % entity_id if entity_id is not None else '', return_data['status'])

        return return_data

    def put_entities(self, entity_name, entities):
        """
        Dump multiple entities to Marketo.
        :param entity_name: The entity name (should be the same as the class name)
        :param entities: A list of entities to dump
        :return: The dumped entities
        """
        data = []
        for entity in entities:
            data.append(entity.entity_data)
        payload = {
            'action': 'createOrUpdate',
            'input': data
        }

        if entity_name == 'lead' and all(entity.id for entity in entities):  # If lead update
            payload['lookupField'] = 'id'  # Set lookup field from default "email" to "id"

        data_array = self._push_data(entity_name, payload)

        return_entities = entities
        if data_array:
            i = 0
            for data in data_array:
                if i < len(return_entities):
                    return_entities[i].init(data)
                    if data['status'] == 'skipped':
                        for reason in data['reasons']:
                            self._logger.warning('entity=%s%s has been skipped for reason=%s', entity_name,
                                                 ' with id=%s' % return_entities[i].id if return_entities[i].id is not None
                                                 else '', reason['message'])
                    else:
                        self._logger.info('entity=%s%s has been %s', entity_name,
                                          ' with id=%s' % return_entities[i].id if return_entities[i].id is not None
                                          else '', data['status'])
                i += 1

        return return_entities

    def delete_entity(self, entity_name, id_, id_field=None):
        """
        Delete an entity from Marketo.
        :param entity_name: The entity name (should be the same as the class name)
        :param id_: The entity id
        :param id_field: The entity field to filter on for deletion, default is "id"
        :return: A dictionary of field keys mapped against their value for the entity
        """
        data = {}
        if id_:
            self._logger.warning('Deleting entity=%s with id=%s', entity_name, str(id_))

            payload = {}
            if id_field:
                id_field_for_deletion = id_field
                payload['deleteBy'] = 'dedupeFields'
            else:
                if is_marketo_guid(id_):
                    id_field_for_deletion = 'marketoGUID'
                    payload['deleteBy'] = 'idField'
                else:
                    id_field_for_deletion = 'id'
            payload['input'] = [{id_field_for_deletion: id_}]

            data_array = self._push_data(entity_name, payload, 'delete')
            if data_array:
                data = data_array[0]  # Only one entity deleted at a time
                if data['status'] == 'skipped':
                    for reason in data['reasons']:
                        self._logger.warning('entity=%s with id=%s has been skipped for reason=%s', entity_name, id_,
                                             reason['message'])
                else:
                    self._logger.info('entity=%s with id=%s has been %s', entity_name, id_, data['status'])
        else:
            self._logger.warning('Cannot delete entity=%s: invalid id (null or empty)', entity_name)

        return data

    def _fetch_data(self, entity_name, id_or_action, filter_type=None, fields=None):
        self._logger.debug('Fetching entity=%s%s%s%s', entity_name,
                           ' (fields=%s)' % fields if fields is not None else '',
                           ' with id/action=%s' % id_or_action.encode('utf-8') if isinstance(id_or_action, unicode)
                           else str(id_or_action) if id_or_action is not None else '',
                           ' with filter_type=%s' % filter_type if filter_type is not None else '')

        payload = {}
        if filter_type:  # Case id
            url = self._build_url(entity_name)
            payload['filterValues'] = id_or_action
            payload['filterType'] = filter_type
        else:  # Case action
            url = self._build_url(entity_name, id_or_action)

        headers = {'Authorization': 'Bearer %s' % self._auth_token}

        if fields:
            payload['fields'] = fields
            # Use POST method to handle long URLs such as when fields are provided
            params = {'_method': 'GET'}
            r = self._session.post(url, headers=headers, params=params, data=payload)
        else:
            r = self._session.get(url, headers=headers, params=payload)

        self._logger.info('Called url=%s with headers=%s and parameters=%s', r.url, headers, payload)
        r.raise_for_status()
        data = r.json()

        result_data = {}
        if 'success' in data:
            if data['success']:
                result_data = data['result']
            else:
                for error in data['errors']:
                    if error['code'] == '602':
                        self._logger.debug('Token expired, fetching new token to replay request')
                        self._auth_token = self._get_auth_token()
                        result_data = self._fetch_data(entity_name, id_or_action, filter_type, fields)
                    else:
                        self._logger.error('Error=%s', error['message'])

        return result_data

    def _push_data(self, entity_name, payload, action=None):
        self._logger.debug('Pushing entity=%s with data=%s%s', entity_name, payload,
                           ' with action=%s' % str(action) if action is not None else '')

        url = self._build_url(entity_name, action)
        headers = {'Authorization': 'Bearer %s' % self._auth_token}
        r = self._session.post(url, headers=headers, json=payload)  # POST method for creation and update
        self._logger.info('Called url=%s with headers=%s and body=%s', r.url, headers, payload)
        r.raise_for_status()
        data = r.json()

        result_data = {}
        if 'success' in data:
            if data['success']:
                result_data = data['result']
            else:
                for error in data['errors']:
                    if error['code'] == '602':
                        self._logger.debug('Token expired, fetching new token to replay request')
                        self._auth_token = self._get_auth_token()
                        result_data = self._push_data(entity_name, data, action)
                    else:
                        self._logger.error('Error=%s', error['message'])

        return result_data

    def _build_url(self, entity_name, action=None):
        url = '%s/%s/%s' % (self._api_endpoint, self.API_VERSION,
                            simple_pluralize(entity_name))  # Entity name should be of plural form
        if action:
            url += '/' + action
        url += '.json'
        return url
