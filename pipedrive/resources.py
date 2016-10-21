from abc import ABCMeta, abstractproperty
from .errors import *
from helpers import *
from requests import HTTPError
import logging


class Resource:
    __metaclass__ = ABCMeta

    def __init__(self, client, id_=None, id_field="id"):
        self._logger = logging.getLogger(__name__)
        self._client = client

        self._load_fields()

        if id_:
            self._load_data(id_, id_field)

    def __getattr__(self, name):
        if name != "_field_keys":
            if name in self._field_keys\
                    and name != self._field_keys[name]:  # Prevent from infinite looping when name = key
                self._logger.debug("Looking for custom attribute with name %s in loaded fields", name)

                key = self._field_keys[name]

                attr = getattr(self, key)

                # Look for related resource
                if key in self._field_types and self._field_types[key] in self.related_resources:
                    resource_class = self.related_resources[self._field_types[key]]

                    if attr is not None\
                            and not isinstance(attr, resource_class):  # Related resource already loaded
                        related_name = resource_class.__name__.lower()
                        related_id = attr
                        self._logger.debug("Loading related resource %s with id %s", related_name, related_id)

                        attr = resource_class(self._client, related_id)

                        setattr(self, key, attr)  # Cache related resource to prevent from further reloading

                return attr
            else:
                raise AttributeError("No attribute found with name %s" % name)
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
            value = attr
            if isinstance(attr, Resource):
                value = getattr(attr, "id")  # "Flatten" related resources - keep id only
            elif type(attr) is dict and "id" in attr:  # In case of dict, keep id only as well
                value = attr["id"]
            data[key] = value
        return data

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
        if fields:
            for field in fields:
                key = field["key"]
                name = to_snake_case(field["name"])
                self._field_keys[name] = key
                self._field_types[key] = field["field_type"]
                setattr(self, key, None)  # Initialize field
        else:
            raise InitializationError("Load fields", "No data returned")

    def _load_data(self, id_, id_field):
        id_to_look_for = id_

        # Find resource id first if id_field was provided as "name"
        if id_field == "name":
            data_array = self._client.get_resource_data(self.resource_name, "find", {"term": id_})
            if data_array:
                id_to_look_for = data_array[0]["id"]  # Assume first result is the right one
            else:
                self._logger.warning("No resource %s found with name %s",
                                     self.resource_name, id_)
                return

        try:
            data = self._client.get_resource_data(self.resource_name, id_to_look_for)
            if data:
                for key in data:
                    setattr(self, key, self._get_data_value(data[key]))
            else:
                self._logger.warning("No data could be loaded for resource %s with id %s",
                                     self.resource_name, id_to_look_for)
        except HTTPError as e:
            if e.response.status_code == 404:
                self._logger.warning("No data could be loaded for resource %s with id %s",
                                     self.resource_name, id_to_look_for)
            else:
                raise e

    def save(self):
        """
        Save (i.e. create or update) resource.
        """
        data = self._client.set_resource_data(self.resource_name, self.resource_data, self.id)
        if data:
            for key in data:
                setattr(self, key, self._get_data_value(data[key]))
        else:
            raise SavingError("Save resource", "No data returned")

    def _get_data_value(self, value):
        new_value = value
        if type(value) is dict and "value" in value:  # "Flatten" complex field value such as org_id
            new_value = value["value"]
        elif type(value) is list:  # In case of list, keep only primary value and "flatten" field value
            for v in value:
                if v["primary"]:
                    new_value = v["value"]
        return new_value


class Person(Resource):

    @property
    def related_resources(self):
        return {
            "org": Organization
        }


class Organization(Resource):

    @property
    def related_resources(self):
        return {}


class Deal(Resource):

    @property
    def related_resources(self):
        return {
            "people": Person
        }
