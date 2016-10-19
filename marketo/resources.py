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
        :return: A dictionary of fields mapped against their value
        """
        data = {}
        for key in self._fields:
            if not self._resource_fields[key]["readOnly"]:  # Some attributes cannot be updated while other are
                try:
                    data[key] = getattr(self, key)
                except AttributeError:
                    data[key] = self._resource_fields[key]["default"]  # Set default value to avoid system errors
        return data

    @abstractproperty
    def _resource_fields(self):
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
            if field["name"] in self._resource_fields.keys():
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
        # Only id is returned so update id only in resource
        if self._id_field in data:
            setattr(self, "id", data[self._id_field])
            if self._id_field != "id":
                setattr(self, self._id_field, data[self._id_field])


class Lead(Resource):

    # Override bc fields do not share the same schema for leads
    def _load_fields(self):
        fields = self._client.get_resource_fields(self.resource_name)
        self._fields = []
        for field in fields:
            name = field["rest"]["name"]
            if name in self._resource_fields.keys() and not field["rest"]["readOnly"]:
                self._fields.append(name)
        self._id_field = "id"  # idField is not specified in return data so manually set it

    @property
    def _resource_fields(self):
        return {
            "id": {  # id is mandatory for updating
                "default": None,
                "readOnly": False
            },
            "firstName": {
                "default": None,
                "readOnly": False
            },
            "lastName": {
                "default": None,
                "readOnly": False
            },
            "email": {
                "default": None,
                "readOnly": False
            },
            "title": {
                "default": None,
                "readOnly": False
            },
            "phone": {
                "default": None,
                "readOnly": False
            },
            "country": {
                "default": None,
                "readOnly": True
            },  # read only bc of "externalCompanyId"
            "leadSource": {
                "default": None,
                "readOnly": False
            },
            "leadStatus": {
                "default": None,
                "readOnly": False
            },
            "conversicaLeadOwnerEmail": {
                "default": None,
                "readOnly": False
            },
            "conversicaLeadOwnerFirstName": {
                "default": None,
                "readOnly": False
            },
            "conversicaLeadOwnerLastName": {
                "default": None,
                "readOnly": False
            },
            "pipedriveId": {
                "default": None,
                "readOnly": False
            },
            "state":  {
                "default": None,
                "readOnly": True
            },  # read only bc of "externalCompanyId"
            "city":  {
                "default": None,
                "readOnly": True
            },  # read only bc of "externalCompanyId"
            "noofEmployeesRange": {
                "default": None,
                "readOnly": False
            },
            "company":  {
                "default": None,
                "readOnly": True
            },  # read only bc of "externalCompanyId"
            "leadScore": {
                "default": None,
                "readOnly": False
            },
            "externalCompanyId": {
                "default": None,
                "readOnly": False
            },
        }


class Opportunity(Resource):

    @property
    def _resource_fields(self):
        return {
            "externalOpportunityId": {
                "default": None,
                "readOnly": False
            },
            "name": {
                "default": None,
                "readOnly": False
            },
        }


class Role(Resource):

    @property
    def resource_name(self):
        return "opportunities/" + self.__class__.__name__.lower()

    @property
    def _resource_fields(self):
        return {
            "externalOpportunityId": {
                "default": None,
                "readOnly": False
            },
            "leadId": {
                "default": None,
                "readOnly": False
            },
            "role": {
                "default": None,
                "readOnly": False
            },
            "isPrimary": {
                "default": False,
                "readOnly": False
            },
        }


class Company(Resource):

    @property
    def _resource_fields(self):
        return {
            "externalCompanyId": {
                "default": None,
                "readOnly": False
            },
            "company": {
                "default": None,
                "readOnly": False
            },
            "annualRevenue": {
                "default": None,
                "readOnly": False
            },
            "numberOfEmployees": {
                "default": None,
                "readOnly": False
            },
        }
