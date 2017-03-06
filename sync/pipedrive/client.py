import logging

from requests import HTTPError, Session

from sync.common import memoize, simple_pluralize


class PipedriveClient:
    """
    Simple client that make calls to Pipedrive API.
    """

    API_ENDPOINT = 'https://api.pipedrive.com/v1'

    def __init__(self, api_token):
        self._logger = logging.getLogger(__name__)
        self._memo = {}  # The class cache

        self._session = Session()  # Reuse session for better performance within a single instance of the client
        self._session.params = {'api_token': api_token}

    @memoize(method_name='get_entity_fields')
    def get_entity_fields(self, entity_name):
        """
        Return an entity schema loaded from Pipedrive.
        :param entity_name: The entity name (should be the same as the class name)
        :return: A list of available fields for interaction via the API.
        """
        return self._fetch_data(entity_name + 'Fields')

    def get_entity_flow(self, entity_name, entity_id):
        """
        Return the entity list of updates loaded from Pipedrive.
        :param entity_name: The entity name (should be the same as the class name)
        :param entity_id: The entity id
        :return: A list of updates.
        """
        return self._fetch_data(simple_pluralize(entity_name), '%s/flow' % entity_id)

    def get_entity_data(self, entity_name, entity_id, entity_fields=None):
        """
        Return an entity data loaded from Pipedrive.
        :param entity_name: The entity name (should be the same as the class name)
        :param entity_id: The entity id
        :param entity_fields: The entity fields to return, default if not specified
        :return: A dictionary of field keys mapped against their value for the entity
        """
        return self._fetch_data(simple_pluralize(entity_name), entity_id, entity_fields)

    def put_entity_data(self, entity_name, entity_data, entity_id=None):
        """
        Dump an entity data to Pipedrive.
        :param entity_name: The entity name (should be the same as the class name)
        :param entity_data: The entity data
        :param entity_id: The entity id (update only)
        :return: A dictionary of field keys mapped against their value for the entity
        """
        return self._push_data(simple_pluralize(entity_name), entity_data, entity_id)

    def delete_entity(self, entity_name, id_):
        """
        Delete an entity from Pipedrive.
        :param entity_name: The entity name (should be the same as the class name)
        :param id_: The entity id
        :return: A dictionary of field keys mapped against their value for the entity
        """
        return_data = {}

        if id_:
            self._logger.warning('Deleting entity=%s with id=%s', entity_name, str(id_))

            url = self._build_url(simple_pluralize(entity_name), id_)

            r = self._session.delete(url)
            self._logger.info('Called url=%s', r.url)
            try:
                r.raise_for_status()
            except HTTPError as e:
                if e.response.status_code != 410:  # Pipedrive seems to raise a 410 error during deletion
                    raise e

            data = r.json()

            if 'success' in data:
                if data['success']:
                    return_data = data['data']
                else:
                    self._logger.error('Error=%s', data['error'])
        else:
            self._logger.warning('Cannot delete entity=%s: invalid id (null or empty)', entity_name)

        return return_data

    def _fetch_data(self, entity_name, id_or_action=None, fields=None):
        self._logger.debug('Fetching entity=%s%s%s', entity_name,
                           ' (fields=%s)' % fields if fields is not None else '',
                           ' with id/action=%s' % id_or_action.encode('utf-8') if isinstance(id_or_action, unicode)
                           else str(id_or_action) if id_or_action is not None else '')

        url = self._build_url(entity_name, id_or_action)
        payload = fields or {}
        r = self._session.get(url, params=payload)
        self._logger.info('Called url=%s with parameters=%s', r.url, payload)
        r.raise_for_status()
        data = r.json()

        result_data = {}
        if 'success' in data:
            if data['success']:
                result_data = data['data']
            else:
                self._logger.error('Error=%s', data['error'])

        return result_data

    def _push_data(self, entity_name, data, id_or_action=None):
        self._logger.debug('Pushing entity=%s with data=%s%s', entity_name, data,
                           ' with id/action=%s' % str(id_or_action) if id_or_action is not None else '')
        url = self._build_url(entity_name, id_or_action)

        if not id_or_action:  # Create
            r = self._session.post(url, data=data)
        else:  # Update
            r = self._session.put(url, json=data)

        self._logger.info('Called url=%s with body=%s', r.url, data)
        r.raise_for_status()
        data = r.json()

        result_data = {}
        if 'success' in data:
            if data['success']:
                result_data = data['data']
            else:
                self._logger.error('Error=%s', data['error'])

        return result_data

    def _push_data_json(self, entity_name, data, id_or_action=None):
        self._logger.debug('Pushing entity=%s with data=%s%s', entity_name, data,
                           ' with id/action=%s' % str(id_or_action) if id_or_action is not None else '')
        url = self._build_url(entity_name, id_or_action)

        if not id_or_action:  # Create
            r = self._session.post(url, json=data)
        else:  # Update
            r = self._session.put(url, json=data)
        self._logger.info('Called url=%s with body=%s', r.url, data)
        r.raise_for_status()
        data = r.json()

        result_data = {}
        if 'success' in data:
            if data['success']:
                result_data = data['data']
            else:
                self._logger.error('Error=%s', data['error'])

        return result_data

    def _build_url(self, entity_name, id_or_action=None):
        url = self.API_ENDPOINT + '/' + entity_name
        if id_or_action:
            url += '/' + str(id_or_action)
        return url

    @memoize(method_name='get_filters')
    def _get_filters(self):
        return self._fetch_data('filters')

    def _get_filter(self, filter_value, object_, field_id, type_):
        filters = self._get_filters()

        filter_name = 'Real Time API filter'
        # Search for existing filter
        filter_id = next((filter_['id'] for filter_ in filters if filter_['name'] == filter_name), None)
        if filter_id:
            filter_ = self._fetch_data('filters', filter_id)  # Ensure the filter still exists
            if not filter_:
                filter_id = None
                self._memo['get_filters'] = {}  # Reset cache because the filter has probably been deleted

        filter_data = {
            'name': filter_name,
            'conditions': {
                'glue': 'and',
                'conditions': [
                    {
                        'glue': 'and',
                        'conditions': [
                            {
                                'object': object_,
                                'field_id': field_id,
                                'operator': '=',
                                'value': filter_value,
                                'extra_value': None
                            }
                        ]
                    },
                    {
                        'glue': 'or',
                        'conditions': []
                    }
                ]
            },
            'type': type_
        }

        return_filter = self._push_data_json('filters', filter_data, filter_id)  # Create or update filter

        if not filter_id and return_filter:
            self._memo['get_filters'] = {}  # Reset cache because a filter has been created

        return return_filter

    def get_organization_email_domain_filter(self, filter_value):
        """
        Get the filter for organizations on email domain.
        :param filter_value: The filter email domain value
        :return: The filter
        """
        return self._get_filter(filter_value, 'organization', '4014', 'org')

    def get_organization_marketoid_filter(self, filter_value):
        """
        Get the filter for organizations on marketo id.
        :param filter_value: The filter marketo id value
        :return: The filter
        """
        return self._get_filter(filter_value, 'organization', '3999', 'org')
