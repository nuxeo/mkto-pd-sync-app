import logging
from abc import ABCMeta

from requests import HTTPError

from .helpers import to_snake_case
from sync.common import InitializationError, SavingError


class Entity:
    """
    The base abstract class for a synchronizable object in Pipedrive.
    """
    __metaclass__ = ABCMeta  # Define Abstract Base Class

    def __init__(self, client, id_=None, id_field='id', load=True):
        self._logger = logging.getLogger(__name__)
        self._client = client  # The class corresponding client instance
        self.id = None  # Entities should always have an id

        self._load_fields()

        if id_:
            if load:
                self._load(id_, id_field)
            else:
                # Store the given id for further loading
                if id_field and hasattr(self, id_field):
                    setattr(self, id_field, id_)

    def __getattr__(self, field_name):
        if field_name != '_field_keys':
            if field_name in self._field_keys and field_name != self._field_keys[field_name]:
                # Prevent from infinite looping when field name = field key

                field_key = self._field_keys[field_name]

                self._logger.debug('Looking for custom attribute with name=%s (key=%s)', field_name, field_key)
                attr = getattr(self, field_key)

                # Search for a related entity
                if field_key in self._field_types and self._field_types[field_key] in self._related_entities:
                    entity_class = self._related_entities[self._field_types[field_key]]

                    if attr is not None and not isinstance(attr, entity_class):
                        # Related entity has already been loaded
                        related_name = entity_class.__name__.lower()
                        related_id = attr
                        self._logger.debug('Loading related entity=%s with id=%s', related_name, related_id)

                        attr = entity_class(self._client, related_id)
                        setattr(self, field_key, attr)  # Cache related entity to prevent from further reloading

                # Search for an enum
                if field_key in self._field_options and attr:
                    try:
                        attr = self._field_options[field_key][int(attr)]
                    except ValueError:  # In case the attribute is not an integer
                        pass

                return attr

            else:
                raise AttributeError('No attribute found with name=%s' % field_name)

        else:
            # "_field_keys" is not initialized yet but return an empty dict for the magic to happen
            return {}

    def __setattr__(self, key_or_name, value):
        key = key_or_name
        # If trying to set a value for a field name, set the value for the field key instead
        if key_or_name in self._field_keys:
            key = self._field_keys[key_or_name]
        object.__setattr__(self, key, self._get_data_value(value))

    def _get_data_value(self, value):
        data_value = value
        if type(value) is dict and 'value' in value:  # "Flatten" complex field value such as org_id: get value only
            data_value = value['value']
        elif type(value) is list:  # In case of a list, keep only primary value and "flatten" field value
            for v in value:
                if v['primary']:
                    data_value = v['value']
        return data_value

    @property
    def entity_name(self):
        return self.__class__.__name__.lower()

    @property
    def entity_data(self):
        """
        Return the entity data compliant with Pipedrive input format.
        :return: A dictionary of field keys mapped against their value for the entity
        """
        data = {}
        for field_name in self._field_keys:
            field_key = self._field_keys[field_name]
            attr = getattr(self, field_key)
            if attr is None or attr == '':
                attr = self._field_defaults.get(field_key, attr)
            elif isinstance(attr, Entity):
                attr = getattr(attr, 'id')  # "Flatten" related entities: get id only
            elif type(attr) is dict and 'id' in attr:  # Same in case of a dict
                attr = attr['id']
            data[field_key] = attr
        return data

    @property
    def _field_defaults(self):
        """
        Return the mandatory entity field default values.
        :return: A dictionary of fields mapped against their default value for the entity
        """
        return {}

    @property
    def _related_entities(self):
        """
        Return the entity related entities.
        :return: A dictionary of related entity types mapped against their class
        """
        return {}

    def _load_fields(self):
        """
        Initialize the entity attributes.
        """
        fields = self._client.get_entity_fields(self.entity_name)
        self._field_keys = {}
        self._field_types = {}
        self._field_options = {}
        if fields:
            for field in fields:
                field_key = field['key']
                field_name = to_snake_case(field['name'])
                # If multiple fields share the same name use key to access them all
                count_name = len([f for f in fields if to_snake_case(f['name']) == field_name])
                if count_name < 2:
                    self._field_keys[field_name] = field_key
                else:
                    self._field_keys[field_key] = field_key
                self._field_types[field_key] = field['field_type']

                if 'options' in field:
                    self._field_options[field_key] = {}
                    for option in field['options']:
                        self._field_options[field_key][option['id']] = option['label']

                setattr(self, field_key, None)  # Initialize field
        else:
            raise InitializationError('Load fields', 'No data returned for entity={}', self.entity_name)

    def _load(self, id_, id_field):
        """
        Load and initialize entity data from Pipedrive.
        :param id_: The entity id
        :param id_field: The entity field to filter on
        """
        # Find entity id first
        if id_field == 'name':
            id_to_look_for = self._find_by_name(id_)
        elif id_field:
            id_to_look_for = self._find_by_filter(id_field, id_)
        else:
            id_to_look_for = id_

        if id_to_look_for:
            try:
                data = self._client.get_entity_data(self.entity_name, id_to_look_for)
                if data and ('active_flag' not in data or ('active_flag' in data and data['active_flag'])):
                    # Prevent from loading deleted entity
                    self.init(data)
                else:
                    self._logger.warning('No data could be loaded for entity=%s for %s=%s',
                                         self.entity_name, id_field, id_to_look_for)
            except HTTPError as e:
                if e.response.status_code == 404:
                    self._logger.warning('No data could be loaded for entity=%s for %s=%s',
                                         self.entity_name, id_field, id_to_look_for)
                else:
                    raise e

    def init(self, data):
        """
        Initialize the entity with data.
        :param data: Data to initialize the entity with
        """
        for key in data:
            setattr(self, key, data[key])

    def _find_by_name(self, name):
        """
        Return the entity id given its name.
        :param name: The entity name
        :return: The entity id
        """
        id_ = None
        if name and name.strip() and len(name.strip()) >= 2:  # Search term must be at least 2 characters long
            name = name.strip()
            data_array = self._client.get_entity_data(self.entity_name, 'find', {'term': name})
            if data_array:
                if len(data_array) == 1:
                    id_ = data_array[0]['id']
                else:
                    match = False
                    for data in data_array:
                        if data['name'] == name:
                            id_ = data['id']
                            match = True
                            break
                    if match:
                        self._logger.debug('More than one entity=%s found with name=%s and found one exact match',
                                           self.entity_name, name)
                    else:
                        self._logger.warning('More than one entity=%s found with name=%s', self.entity_name, name)
            else:
                self._logger.warning('No entity=%s found with name=%s',
                                     self.entity_name, name)

        return id_

    def _find_by_filter(self, filter_name, filter_value):
        """
        Return the entity id given a filter.
        :param filter_name: The filter name
        :param filter_value: The filter value
        :return: The entity id
        """
        if filter_name == 'id':
            return filter_value
        return None

    def load(self):
        """
        Load entity.
        """
        self._load(self.id, 'id')

    def save(self):
        """
        Save (i.e. create or update) entity.
        """
        try:
            data = self._client.put_entity_data(self.entity_name, self.entity_data, self.id)
            if data:
                self.init(data)
            else:
                raise SavingError('Save entity', 'No data returned for entity={}{}', self.entity_name,
                                  ' with id=%s' % self.id if self.id else '')
        except HTTPError as e:
            if e.response.status_code == 400:
                raise SavingError('Save entity', 'No data returned for entity={}{}', self.entity_name,
                                  ' with id=%s' % self.id if self.id else '')
            else:
                raise e

    def delete(self):
        """
        Delete entity.
        """
        data = self._client.delete_entity(self.entity_name, self.id)
        if data:
            return data['id']
        else:
            raise SavingError('Delete entity', 'No data returned for entity={}{}', self.entity_name,
                              ' with id=%s' % self.id if self.id else '')
        return None


class Person(Entity):
    @property
    def _field_defaults(self):
        return {
            'name': 'Unknown Unknown'
        }

    @property
    def _related_entities(self):
        return {
            'org': Organization,
            'user': User
        }


class Organization(Entity):
    @property
    def _field_defaults(self):
        return {
            'name': 'Default organization name'
        }

    def _find_by_filter(self, filter_name, filter_value):
        id_ = Entity._find_by_filter(self, filter_name, filter_value)
        if filter_value and (filter_name == 'email_domain' or filter_name == 'marketoid'):
            if filter_name == 'email_domain':
                filter_data = self._client.get_organization_email_domain_filter(filter_value.strip())
            elif filter_name == 'marketoid':
                filter_data = self._client.get_organization_marketoid_filter(filter_value)
            filtered_data_array = self._client.get_entity_data('organization', None, {'filter_id': filter_data['id']})
            if filtered_data_array:
                if len(filtered_data_array) == 1:
                    id_ = filtered_data_array[0]['id']
                else:
                    self._logger.warning('More than one entity=%s found for %s=%s', self.entity_name,
                                         filter_name, filter_value)
            else:
                self._logger.warning('No entity=%s found with %s=%s', self.entity_name, filter_name, filter_value)
        return id_


class Deal(Entity):
    @property
    def _field_defaults(self):
        return {
            'title': 'Default deal title'
        }

    @property
    def _related_entities(self):
        return {
            'people': Person,
            'stage': Stage,
            'user': User,
            'org': Organization
        }


class User(Entity):
    pass


class Activity(Entity):
    pass


class Stage(Entity):
    def _load_fields(self):
        # Fields cannot be automatically loaded ("stageFields" endpoint not implemented)
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


class Pipeline(Entity):
    def _load_fields(self):
        # Fields cannot be automatically loaded ("pipelineFields" endpoint not implemented)
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


class Note(Entity):
    def _load(self, id_, id_field):
        if id_ and id_field in ('user_id', 'deal_id', 'person_id', 'org_id'):
            try:
                data = self._client.get_entity_data(self.entity_name, None, {id_field: id_})
                if data:
                    # Always load last note
                    self.init(data[len(data) - 1])
                else:
                    self._logger.warning('No data could be loaded for entity=%s for %s=%s',
                                         self.entity_name, id_field, id_)
            except HTTPError as e:
                if e.response.status_code == 404:
                    self._logger.warning('No data could be loaded for entity=%s for %s=%s',
                                         self.entity_name, id_field, id_)
                else:
                    raise e
