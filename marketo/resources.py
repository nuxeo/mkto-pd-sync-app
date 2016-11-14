from .errors import *

from abc import ABCMeta, abstractproperty

import logging


class Resource:
    __metaclass__ = ABCMeta

    def __init__(self, client, id_=None, id_field=None):
        self._logger = logging.getLogger(__name__)
        self._client = client

        self._load_fields()

        if id_:
            self._load_data(id_, id_field)

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
            if key in self._resource_fields_to_update:
                data[key] = getattr(self, key)\
                            or self._resource_fields_to_update[key]  # Set default value if any to avoid system errors
        return data

    @abstractproperty
    def _resource_fields_to_update(self):
        """
        Get resource fields we want to be able to set.
        :return: A dictionary of fields mapped against their default value
        """
        pass

    def _load_fields(self):
        data = self._client.get_resource_fields(self.resource_name)
        self._fields = []
        if data:
            self._id_field = data[0]["idField"]
            if self._id_field != "id":
                self.id = None  # Resource should always have an id
            for field in data[0]["fields"]:
                self._fields.append(field["name"])
                setattr(self, field["name"], None)  # Initialize field

        else:
            raise InitializationError("Load fields", "No data returned")

    def _load_data(self, id_, id_field):
        id_field_to_look_for = id_field or self._id_field
        data = self._client.get_resource_data(self.resource_name, id_, id_field_to_look_for, self._fields)
        if data:
            for key in data:
                setattr(self, key, data[key])
            if self._id_field != "id":
                self.id = getattr(self, self._id_field)  # Set id value with id field value
        else:
            self._logger.warning("No data could be loaded for resource %s with id %s (looking for id field \"%s\")",
                                 self.resource_name, id_, id_field_to_look_for)

    def save(self):
        """
        Save (i.e. create or update) resource.
        """
        data = self._client.set_resource_data(self.resource_name, self.resource_data, self.id)
        # Only id field is returned so update id and id field only
        if data and self._id_field in data:
            setattr(self, self._id_field, data[self._id_field])
            if self._id_field != "id":
                setattr(self, "id", data[self._id_field])  # Set id value with id field value
        else:
            raise SavingError("Save resource", "No data returned")


class Lead(Resource):

    # Override bc fields do not share the same schema for leads
    def _load_fields(self):
        fields = self._client.get_resource_fields(self.resource_name)
        self._fields = []
        if fields:
            for field in fields:
                name = field["rest"]["name"]
                self._fields.append(name)
                setattr(self, name, None)  # Initialize field
                self._id_field = "id"  # id field is not specified in return data for lead so manually set it
        else:
            raise InitializationError("Load fields", "No data returned")

    @property
    def _resource_fields_to_update(self):
        # Marketo won't let us update all fields
        # Especially some that cannot be updated while other are
        return {
            "id": None,  # id is mandatory for updating
            "firstName": None,
            "lastName": None,
            "email": None,
            "externalCompanyId": None,
            "title": None,
            "phone": None,
            "leadSource": None,
            "conversicaLeadOwnerEmail": None,
            "conversicaLeadOwnerFirstName": None,
            "conversicaLeadOwnerLastName": None,
            "pipedriveId": None,
            "leadStatus": None,
            "toDelete": False
        }


class Opportunity(Resource):

    @property
    def _resource_fields_to_update(self):
        return {
            "externalOpportunityId": None,
            "name": None,
            "type": None,
            "description": None,
            "lastActivityDate": None,
            "isClosed": None,
            "isWon": None,
            "amount": None,
            "closeDate": None,
            "stage": None,
            "fiscalQuarter": None,
            "fiscalYear": None
        }


class Role(Resource):

    @property
    def resource_name(self):
        return "opportunities/" + self.__class__.__name__.lower()

    @property
    def _resource_fields_to_update(self):
        return {
            "externalOpportunityId": None,
            "leadId": None,
            "role": None,
            "isPrimary": False  # Marketo also requires a default value (no null) for certain fields (boolean fields?)
        }


class Company(Resource):

    @property
    def _resource_fields_to_update(self):
        return {
            "externalCompanyId": None,
            "company": None,
            "billingStreet": None,
            "billingCity": None,
            "billingState": None,
            "billingCountry": None,
            "mainPhone": None,
            "industry": None,
            "annualRevenue": None,
            "numberOfEmployees": None
        }
