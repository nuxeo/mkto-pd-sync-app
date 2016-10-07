from abc import ABCMeta, abstractproperty
import logging


class Resource:
    __metaclass__ = ABCMeta

    # FIELD_TO_UPDATE = {  # Has to be keys for now TODO names?
    #     "name": False,
    #     "owner_id": True,  # Boolean that indicates if the field should be converted to a number (bc related resource)
    #     "org_id": True,
    #     "email": False,
    #     "phone": False,
    #     "visible_to": False
    # }

    def __init__(self, client, id_=None):
        self._logger = logging.getLogger(__name__)
        self._client = client

        self._load_fields()

        self.id = id_  # Resource always has an id
        if id_ is not None:
            self._load_data()

    @property
    def resource_name(self):
        return self.__class__.__name__.lower()

    @property
    def resource_data_to_update(self):
        data = {}
        # for key in self.FIELD_TO_UPDATE:
        #     try:
        #         data[key] = getattr(self, key)
        #         if (self.FIELD_TO_UPDATE[key]  # Field has to be "flattened"
        #                 and type(data[key]) is dict and "value" in data[key]):
        #             data[key] = data[key]["value"]
        #     except AttributeError:
        #         data[key] = None
        return data

    @abstractproperty
    def related_resources(self):
        pass

    def _load_fields(self):
        fields = self._client.get_resource_fields(self.resource_name)
        self._fields = []
        for field in fields:
            self._fields.append(field["rest"]["name"])

    def _load_data(self):
        self._logger.debug("Loading resource with id %d", self.id)
        data = self._client.get_resource_data(self.resource_name, self.id, self._fields)
        if data:
            for key in data:
                setattr(self, key, data[key])
        else:
            self.id = None  # Reset id case given id not found

    def save(self):
        self._logger.debug("Saving resource")
        # data = self._client.set_resource_data(self.resource_name, self.resource_data_to_update, self.id)
        # for key in data:
        #     setattr(self, key, data[key])


class Lead(Resource):

    def related_resources(self):
        return {}
