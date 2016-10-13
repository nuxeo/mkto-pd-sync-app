from abc import ABCMeta, abstractproperty
import logging
import helpers


class Resource:
    __metaclass__ = ABCMeta

    def __init__(self, client, id_=None):
        self._logger = logging.getLogger(__name__)
        self._client = client

        self._load_fields()

        self.id = id_  # Resource always has an id
        if id_ is not None:
            self._load_data()

    def __getattr__(self, name):
        if name != "_field_keys":
            if name in self._field_keys\
                    and name != self._field_keys[name]:  # Prevent from overflowing when attribute not found and name = key
                self._logger.debug("Looking for custom attribute with name %s in loaded fields", name)

                key = self._field_keys[name]

                attr = getattr(self, key)

                # Check related resource
                if key in self._field_types and self._field_types[key] in self.related_resources():
                    resource_class = self.related_resources()[self._field_types[key]]

                    if attr is not None\
                            and not isinstance(attr, resource_class):  # Related resource already loaded
                        related_name = resource_class.__name__.lower()
                        related_id = attr
                        self._logger.debug("Loading related resource %s with id %s", related_name, related_id)
                        attr = self._client.get_resource_by_id(related_name, related_id)
                        setattr(self, key, attr)  # Cache attribute value for related object

                return attr
            else:
                raise AttributeError("No attribute found with name %s" % name)
        else:
            return {}  # _field_keys not initialized but return an empty dict to make the whole thing work

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
        data = {}
        for name in self._field_keys:
            try:
                key = self._field_keys[name]
                attr = getattr(self, key)
                value = attr
                if isinstance(attr, Resource):
                    value = getattr(attr, "id")  # Convert related resource to id as parameter
                elif type(attr) is dict and "id" in attr:
                    value = attr["id"]
                data[key] = value
            except AttributeError:
                data[key] = None
        return data

    @abstractproperty
    def related_resources(self):
        pass

    def _load_fields(self):
        fields = self._client.get_resource_fields(self.resource_name)
        self._field_keys = {}
        self._field_types = {}
        for field in fields:
            key = field["key"]
            name = helpers.to_snake_case(field["name"])
            self._field_keys[name] = key
            self._field_types[key] = field["field_type"]

    def _load_data(self):
        data = self._client.get_resource_data(self.resource_name, self.id)
        if data:
            for key in data:
                setattr(self, key, self._get_data_value(data[key]))
        else:
            self.id = None  # Reset id case given id not found

    def save(self):
        data = self._client.set_resource_data(self.resource_name, self.resource_data, self.id)
        for key in data:
            setattr(self, key, self._get_data_value(data[key]))

    def _get_data_value(self, value):
        new_value = value
        if type(value) is dict and "value" in value:  # Field has to be "flattened" as parameter
            new_value = value["value"]
        elif type(value) is list:  # In case of list/array keep only primary value
            for v in value:
                if v["primary"]:
                    new_value = v["value"]
        return new_value


class Person(Resource):

    def related_resources(self):
        return {
            "org": Organization
        }


class Organization(Resource):

    def related_resources(self):
        return {}
