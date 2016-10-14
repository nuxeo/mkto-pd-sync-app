from abc import ABCMeta, abstractproperty
import logging


class Resource:
    __metaclass__ = ABCMeta

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
        """
        Get resource data as a dictionary to pass as parameter for create/update request.
        :return: A dictionary of fields
        """
        data = {}
        for key in self._fields:
            try:
                data[key] = getattr(self, key)
            except AttributeError:
                data[key] = None
        return data

    @abstractproperty
    def related_resources(self):
        """
        Get related resources as a dictionary if any.
        :return: A dictionary of related resources
        """
        pass

    @abstractproperty
    def resource_fields(self):
        """
        Get resource fields we want to retrieve and be able to set.
        :return: A dictionary of fields
        """
        pass

    def _load_fields(self):
        fields = self._client.get_resource_fields(self.resource_name)
        self._fields = []
        if fields:
            if "idField" in fields[0]:
                self._id_field = fields[0]["idField"]
            if "fields" in fields[0]:
                fields = fields[0]["fields"]
        for field in fields:
            if field["name"] in self.resource_fields():
                self._fields.append(field["name"])

    def _load_data(self):
        data = self._client.get_resource_data(self.resource_name,
                                              {"filterType": self._id_field, "filterValues": self.id}, self._fields)
        if data:
            for key in data:
                setattr(self, key, data[key])
        else:
            self.id = None  # Reset id case given id is not found

    def save(self):
        """
        Save (i.e. create or update) resource.
        """
        data = self._client.set_resource_data(self.resource_name, self.resource_data, self.id)
        # Only id is returned
        if "id" in data:
            setattr(self, "id", data["id"])


class Lead(Resource):

    # Override
    def _load_fields(self):
        fields = self._client.get_resource_fields(self.resource_name)
        self._fields = []
        for field in fields:
            name = field["rest"]["name"]
            if name in self.resource_fields() and not field["rest"]["readOnly"]:
                self._fields.append(name)
        self._id_field = "id"

    def related_resources(self):
        return {}

    def resource_fields(self):
        return [
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


class Opportunity(Resource):

    def related_resources(self):
        return {}

    def resource_fields(self):
        return [
            "externalOpportunityId",
            "name"
        ]


class Role(Resource):

    @property
    def resource_name(self):
        return "opportunities/" + self.__class__.__name__.lower()

    def related_resources(self):
        return {}

    def resource_fields(self):
        return [
            "externalOpportunityId",
            "leadId",
            "role"
        ]
