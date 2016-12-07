from ..common import InitializationError, SavingError
from .helpers import to_snake_case

from abc import ABCMeta, abstractproperty
from requests import HTTPError

import logging


class Resource:
    __metaclass__ = ABCMeta

    def __init__(self, client, id_=None, id_field='id'):
        self._logger = logging.getLogger(__name__)
        self._client = client

        self._load_fields()

        if id_:
            self._load_data(id_, id_field)

    def __getattr__(self, name):
        if name != '_field_keys':
            if name in self._field_keys\
                    and name != self._field_keys[name]:  # Prevent from infinite looping when name = key
                self._logger.debug('Looking for custom attribute with name %s in loaded fields', name)

                key = self._field_keys[name]

                attr = getattr(self, key)

                # Look for related resource
                if key in self._field_types and self._field_types[key] in self.related_resources:
                    resource_class = self.related_resources[self._field_types[key]]

                    if attr is not None\
                            and not isinstance(attr, resource_class):  # Related resource already loaded
                        related_name = resource_class.__name__.lower()
                        related_id = attr
                        self._logger.debug('Loading related resource %s with id %s', related_name, related_id)

                        attr = resource_class(self._client, related_id)
                        setattr(self, key, attr)  # Cache related resource to prevent from further reloading

                # Look for enum
                if key in self._field_options and attr:
                    try:
                        attr = self._field_options[key][int(attr)]
                    except ValueError:  # In case attribute is not an integer
                        pass

                return attr
            else:
                raise AttributeError('No attribute found with name %s' % name)
        else:
            # "_field_keys" not initialized yet but return an empty dict to make the whole thing work
            return {}

    def __setattr__(self, key_or_name, value):
        key = key_or_name
        # If trying to set value for name, set value for key instead
        if key_or_name in self._field_keys:
            key = self._field_keys[key_or_name]
        object.__setattr__(self, key, value)

    @property
    def resource_name(self):
        return self.__class__.__name__.lower()

    @property
    def resource_data(self):
        """
        Get resource data as a dictionary to pass as parameter for create/update request.
        :return: A dictionary of fields mapped against their value
        """
        data = {}
        for name in self._field_keys:
            key = self._field_keys[name]
            attr = getattr(self, key)
            if attr is None or attr == '':
                attr = self._field_defaults.get(key, attr)
            elif isinstance(attr, Resource):
                attr = getattr(attr, 'id')  # "Flatten" related resources - keep id only
            elif type(attr) is dict and 'id' in attr:  # In case of dict, keep id only as well
                attr = attr['id']
            data[key] = attr
        return data

    @property
    def _field_defaults(self):
        """
        Get mandatory resource fields for update as a dictionary.
        :return: A dictionary of fields mapped against their default value
        """
        return {}

    @abstractproperty
    def related_resources(self):
        """
        Get related resources as a dictionary, if any.
        :return: A dictionary of related resource types mapped against their class
        """
        pass

    def _load_fields(self):
        fields = self._client.get_resource_fields(self.resource_name)
        self._field_keys = {}
        self._field_types = {}
        self._field_options = {}
        if fields:
            for field in fields:
                key = field['key']
                name = to_snake_case(field['name'])
                self._field_keys[name] = key
                self._field_types[key] = field['field_type']

                if 'options' in field:
                    self._field_options[key] = {}
                    for option in field['options']:
                        self._field_options[key][option['id']] = option['label']

                setattr(self, key, None)  # Initialize field
        else:
            raise InitializationError('Load fields', 'No data returned')

    def _load_data(self, id_, id_field):
        id_to_look_for = id_

        # Find resource id first if id_field was provided
        if id_field == 'name':
            id_to_look_for = self._find_by_name(id_)
        elif id_field:
            id_to_look_for = self._find_by_filter(id_field, id_) or id_

        if id_to_look_for:
            try:
                data = self._client.get_resource_data(self.resource_name, id_to_look_for)
                if data and\
                        ('active_flag' in data and data['active_flag'] or 'active_flag' not in data):  # Prevent from loading deleted resource
                    for key in data:
                        setattr(self, key, self._get_data_value(data[key]))
                else:
                    self._logger.warning('No data could be loaded for resource %s with id %s',
                                         self.resource_name, id_to_look_for)
            except HTTPError as e:
                if e.response.status_code == 404:
                    self._logger.warning('No data could be loaded for resource %s with id %s',
                                         self.resource_name, id_to_look_for)
                else:
                    raise e

    def _find_by_name(self, name):
        id_ = None
        if name and name.strip():
            name = name.strip()
            data_array = self._client.get_resource_data(self.resource_name, 'find', {'term': name})
            if data_array:
                if len(data_array) == 1:
                    id_ = data_array[0]['id']
                else:
                    self._logger.warning('More than one resource %s found with name %s', self.resource_name, name)
            else:
                self._logger.warning('No resource %s found with name %s',
                                     self.resource_name, name)
        return id_

    def _find_by_filter(self, filter_name, filter_value):
        return None

    def save(self):
        """
        Save (i.e. create or update) resource.
        """
        data = self._client.set_resource_data(self.resource_name, self.resource_data, self.id)
        if data:
            for key in data:
                setattr(self, key, self._get_data_value(data[key]))
        else:
            raise SavingError('Save resource', 'No data returned')

    def _get_data_value(self, value):
        new_value = value
        if type(value) is dict and 'value' in value:  # "Flatten" complex field value such as org_id
            new_value = value['value']
        elif type(value) is list:  # In case of list, keep only primary value and "flatten" field value
            for v in value:
                if v['primary']:
                    new_value = v['value']
        return new_value


class Person(Resource):

    @property
    def _field_defaults(self):
        return {
            'name': 'Unknown Unknown'
        }

    @property
    def related_resources(self):
        return {
            'org': Organization,
            'user': User
        }


class Organization(Resource):

    @property
    def _field_defaults(self):
        return {
            'name': 'Default organization name'
        }

    @property
    def related_resources(self):
        return {}

    def _find_by_filter(self, filter_name, filter_value):
        id_ = None
        if filter_name == 'email_domain' and filter_value:
            filter_value = filter_value.strip()
            if filter_value:
                filter_data = self._client.get_organization_email_domain_filter(filter_value)
                filtered_data_array = self._client.get_resource_data('organization', None, {'filter_id': filter_data['id']})
                if filtered_data_array:
                    if len(filtered_data_array) == 1:
                        id_ = filtered_data_array[0]['id']
                    else:
                        self._logger.warning('More than one resource %s found with %s %s',
                                             self.resource_name, filter_name, filter_value)
                else:
                    self._logger.warning('No resource %s found with %s %s',
                                         self.resource_name, filter_name, filter_value)
        return id_


class Deal(Resource):

    @property
    def _field_defaults(self):
        return {
            'title': 'Default deal title'
        }

    @property
    def related_resources(self):
        return {
            'people': Person,
            'stage': Stage
        }


class User(Resource):

    @property
    def related_resources(self):
        return {}


class Stage(Resource):

    @property
    def related_resources(self):
        return {}

    def _load_fields(self):
        # Cannot automatically load fields bc "stageFields" endpoint not implemented
        fields = [
            'id',
            'order_nr',
            'name',
            'active_flag',
            'deal_probability',
            'pipeline_id',
            'rotten_flag',
            'rotten_days',
            'add_time',
            'update_time',
            'deals_summary'
        ]
        self._field_keys = {}
        self._field_types = {}
        for field in fields:
            self._field_keys[field] = field
            setattr(self, field, None)  # Initialize field


class Pipeline(Resource):

    @property
    def related_resources(self):
        return {}

    def _load_fields(self):
        # Cannot automatically load fields bc "pipelineFields" endpoint not implemented
        fields = [
            'id',
            'name',
            'url_title',
            'order_nr',
            'active',
            'add_time',
            'update_time',
            'selected'
        ]
        self._field_keys = {}
        self._field_types = {}
        for field in fields:
            self._field_keys[field] = field
            setattr(self, field, None)  # Initialize field
