from abc import ABCMeta, abstractproperty
import logging


class Resource:
    __metaclass__ = ABCMeta

    def __init__(self, client, id_=None, id_field=None):
        self._logger = logging.getLogger(__name__)
        self._client = client

        self._load_fields()

        self.id = id_  # Resource always has an id
        if id_ is not None:
            self._load_data(id_field)

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
                data[key] = self.resource_fields()[key]  # Get default value from resource fields
        return data

    @abstractproperty
    def related_resources(self):
        """
        Get related resources as a dictionary if any.
        :return: A dictionary of related resources mapped against their class
        """
        pass

    @abstractproperty
    def resource_fields(self):
        """
        Get resource fields we want to retrieve and be able to set.
        :return: A dictionary of fields mapped against their default value
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
            if field["name"] in self.resource_fields().keys():
                self._fields.append(field["name"])

    def _load_data(self, id_field):
        id_field_to_look_for = self._id_field if id_field is None else id_field
        data = self._client.get_resource_data(self.resource_name, self.id, self._fields, id_field_to_look_for)
        if data:
            for key in data:
                setattr(self, key, data[key])
            self.id = data[self._id_field]
        else:
            self.id = None  # Reset id case given id is not found

    def save(self):
        """
        Save (i.e. create or update) resource.
        """
        data = self._client.set_resource_data(self.resource_name, self.resource_data, self.id)
        # Only id is returned
        if self._id_field in data:
            setattr(self, "id", data[self._id_field])
            if self._id_field != "id":
                setattr(self, self._id_field, data[self._id_field])


class Lead(Resource):

    # Override
    def _load_fields(self):
        fields = self._client.get_resource_fields(self.resource_name)
        self._fields = []
        for field in fields:
            name = field["rest"]["name"]
            if name in self.resource_fields().keys() and not field["rest"]["readOnly"]:
                self._fields.append(name)
        self._id_field = "id"

    def related_resources(self):
        return {}

    def resource_fields(self):
        return {
            "id": None,
            "firstName": None,
            "lastName": None,
            "email": None,
            "title": None,
            "phone": None,
            "country": None,
            "leadSource": None,
            "leadStatus": None,
            "conversicaLeadOwnerEmail": None,
            "conversicaLeadOwnerFirstName": None,
            "conversicaLeadOwnerLastName": None,
            "pipedriveId": None,
            "state": None,
            "city": None,
            "noofEmployeesRange": None,
            "company": None,
            "leadScore": None
        }


class Opportunity(Resource):

    def related_resources(self):
        return {}

    def resource_fields(self):
        return {
            "externalOpportunityId": None,
            "name": None
        }


class Role(Resource):

    @property
    def resource_name(self):
        return "opportunities/" + self.__class__.__name__.lower()

    def related_resources(self):
        return {}

    def resource_fields(self):
        return {
            "externalOpportunityId": None,
            "leadId": None,
            "role": None,
            "isPrimary": False
        }
