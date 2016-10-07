from abc import ABCMeta, abstractproperty
import logging
import helpers


class Resource:
    __metaclass__ = ABCMeta

    FIELD_TO_UPDATE = {  # Has to be keys for now TODO names?
        "name": False,
        "owner_id": True,  # Boolean that indicates if the field should be converted to a number (bc related resource)
        "org_id": True,
        "email": False,
        "phone": False,
        "visible_to": False
    }

    def __init__(self, client, id_=None):
        self._logger = logging.getLogger(__name__)
        self._client = client

        self._load_fields()

        self.id = id_  # Resource always has an id
        if id_ is not None:
            self._load_data()

    def __getattr__(self, name):
        if name in self._field_keys\
                and name != self._field_keys[name]:  # Prevent from overflowing when no attribute and name = key
            self._logger.debug("Looking for custom attribute %s in loaded fields", name)

            key = self._field_keys[name]

            attr = getattr(self, key)

            if key in self._field_types and self._field_types[key] in self.related_resources():
                class_ = self.related_resources()[self._field_types[key]]

                if type(class_) != type(attr):  # Related resource already loaded
                    related_name = class_.__name__.lower()
                    related_id = attr["value"]
                    self._logger.debug("Loading related resource %s with id %s", related_name, related_id)
                    attr = self._client.get_resource_by_id(related_name, related_id)
                    setattr(self, name, attr)

            return attr
        else:
            raise AttributeError("No attribute named %s" % name)

    @property
    def resource_name(self):
        return self.__class__.__name__.lower()

    @property
    def resource_data_to_update(self):
        data = {}
        for key in self.FIELD_TO_UPDATE:
            try:
                data[key] = getattr(self, key)
                if (self.FIELD_TO_UPDATE[key]  # Field has to be "flattened"
                        and type(data[key]) is dict and "value" in data[key]):
                    data[key] = data[key]["value"]
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
            self._field_keys[helpers.to_snake_case(field["name"])] = key
            self._field_types[key] = field["field_type"]

    def _load_data(self):
        self._logger.debug("Loading resource with id %d", self.id)
        data = self._client.get_resource_data(self.resource_name, self.id)
        if data:
            for key in data:
                setattr(self, key, data[key])
        else:
            self.id = None  # Reset id case given id not found

    def save(self):
        self._logger.debug("Saving resource")
        data = self._client.set_resource_data(self.resource_name, self.resource_data_to_update, self.id)
        for key in data:
            setattr(self, key, data[key])


class Person(Resource):

    def related_resources(self):
        return {
            "org": Organization
        }


class Organization(Resource):

    def related_resources(self):
        return {}
