from abc import ABCMeta, abstractproperty
import logging
import helpers


class Resource:
    __metaclass__ = ABCMeta

    def __init__(self, client, id_=None):
        self._logger = logging.getLogger(__name__)
        self._client = client

        fields = self._client.get_resource_fields(self.resource_name)
        self._field_keys = {}
        self._field_types = {}
        for field in fields:
            key = field["key"]
            self._field_keys[helpers.to_snake_case(field["name"])] = key
            self._field_types[key] = field["field_type"]

        if id_ is not None:
            self._logger.debug("Load resource with id %d", id_)
            data = self._client.get_resource_data(self.resource_name, id_)
            for key in data:
                setattr(self, key, data[key])

    def __getattr__(self, name):
        if name in self._field_keys\
                and name != self._field_keys[name]:  # Prevent from overflowing when no attribute and name = key
            self._logger.debug("Look for custom attribute %s in loaded fields", name)

            key = self._field_keys[name]

            attr = getattr(self, key)

            if key in self._field_types and self._field_types[key] in self.related_resources():
                class_ = self.related_resources()[self._field_types[key]]

                if type(class_) != type(attr):  # Related resource already loaded
                    self._logger.debug("Load related resource %s", name)
                    attr = self._client.get_resource_by_id(class_.__name__.lower(), attr["value"])
                    setattr(self, name, attr)

            return attr
        else:
            raise AttributeError("No attribute named %s" % name)

    @property
    def resource_name(self):
        return self.__class__.__name__.lower()

    @property
    def resource_data(self):
        data = {}
        for name in self._field_keys:
            key = self._field_keys[name]
            try:
                data[key] = getattr(self, key)
            except AttributeError:
                data[key] = ""
        return data

    @abstractproperty
    def related_resources(self):
        pass

    def save(self):
        self._client.add_resource(self)


class Person(Resource):

    def related_resources(self):
        return {
            "org": Organization
        }


class Organization(Resource):

    def related_resources(self):
        return {}
