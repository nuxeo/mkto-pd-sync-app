from abc import ABCMeta, abstractproperty
import logging


class Resource:
    __metaclass__ = ABCMeta

    # Marketo won't let us update all fields so pick the one we want in a list
    FIELD_TO_UPDATE = [
        "firstName",
        "lastName",
        "email",
        "title",
        "phone",
        "country",
        "leadSource",
        "leadStatus",
        "conversicaLeadOwnerEmail",
        "conversicaLeadOwnerFirstName",
        "conversicaLeadOwnerLastName",
        "pipedriveId",
        "state",
        "city",
        "noofEmployeesRange",
        "company",
        "leadScore"
    ]

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
    def resource_data(self):
        data = {}
        for key in self._fields:
            try:
                data[key] = getattr(self, key)
            except AttributeError:
                data[key] = None
        return data

    @abstractproperty
    def related_resources(self):
        pass

    def _load_fields(self):
        fields = self._client.get_resource_fields(self.resource_name)
        self._fields = []
        for field in fields:
            name = field["rest"]["name"]
            if name in self.FIELD_TO_UPDATE and not field["rest"]["readOnly"]:
                self._fields.append(name)

    def _load_data(self):
        data = self._client.get_resource_data(self.resource_name, self.id, self._fields)
        if data:
            for key in data:
                setattr(self, key, data[key])
        else:
            self.id = None  # Reset id case given id not found

    def save(self):
        data = self._client.set_resource_data(self.resource_name, self.resource_data, self.id)
        # Only id is returned
        if "id" in data:
            setattr(self, "id", data["id"])


class Lead(Resource):

    def related_resources(self):
        return {}
