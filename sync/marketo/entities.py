import logging
from abc import ABCMeta, abstractproperty
from datetime import datetime

from sync.common import InitializationError, SavingError


class Entity:
    """
    The base abstract class for a synchronizable object in Marketo.
    """
    __metaclass__ = ABCMeta  # Define Abstract Base Class

    def __init__(self, client, id_=None, id_field='id', load=True):
        self._logger = logging.getLogger(__name__)
        self._client = client  # The class corresponding client instance
        self.id = None  # Entities should always have an id

        self._load_fields()

        if id_:
            if load:
                if id_field == 'id' and self._id_field != 'id':
                    # Load entity by its id field if not id
                    self._load(id_, self._id_field)
                else:
                    # Load entity by the given id field or id
                    self._load(id_, id_field)
            else:
                # Store the given id for further loading
                if id_field and hasattr(self, id_field):
                    setattr(self, id_field, id_)

    @property
    def entity_name(self):
        return self.__class__.__name__.lower()

    @property
    def entity_data(self):
        """
        Return the entity data compliant with Marketo input format.
        :return: A dictionary of field keys mapped against their value for the entity
        """
        data = {}
        for field_key in self._fields:
            if field_key in self._entity_fields_to_update:
                attr = getattr(self, field_key)
                if attr is None:
                    attr = self._entity_fields_to_update[field_key]  # Set default value if any to avoid system errors
                data[field_key] = attr
        return data

    @abstractproperty
    def _entity_fields_to_update(self):
        """
        Return the entity fields available for update because Marketo won't let us update them all.
        :return: A dictionary of field keys mapped against their default value for the entity
        """
        pass

    def _load_fields(self):
        """
        Initialize the entity attributes.
        """
        data = self._client.get_entity_fields(self.entity_name)
        self._fields = []
        if data:
            self._id_field = data[0]['idField']
            for field in data[0]['fields']:
                self._fields.append(field['name'])
                setattr(self, field['name'], None)  # Initialize field
        else:
            raise InitializationError('Load fields', 'No data returned for entity={}', self.entity_name)

    def _load(self, id_, id_field):
        """
        Load and initialize entity data from Marketo.
        :param id_: The entity id
        :param id_field: The entity field to filter on
        """
        data = {}
        if id_ and id_field:
            data = self._client.get_entity_data(self.entity_name, id_, id_field, self._fields)
            if data:
                self.init(data)
            else:
                self._logger.warning('No data could be loaded for entity=%s with %s=%s',
                                     self.entity_name, id_field, id_)
        return data

    def init(self, data):
        """
        Initialize the entity with data.
        :param data: Data to initialize the entity with
        """
        for field_key in data:
            setattr(self, field_key, data[field_key])
        if self._id_field != 'id':
            self.id = getattr(self, self._id_field)  # Set id value with id field value

    def load(self):
        """
        Load entity.
        """
        self._load(getattr(self, self._id_field), self._id_field)

    def save(self):
        """
        Save (i.e. create or update) entity.
        """
        data = self._client.put_entity_data(self.entity_name, self.entity_data, self.id)
        if data:
            self.init(data)
        else:
            raise SavingError('Save entity', 'No data returned for entity={}{}', self.entity_name,
                              ' with id=%s' % self.id if self.id else '')

    def delete(self, id_field=None):
        """
        Delete entity.
        """
        if id_field and hasattr(self, id_field):
            self._client.delete_entity(self.entity_name, getattr(self, id_field), id_field)
        else:
            self._client.delete_entity(self.entity_name, self.id)
        return None


class Lead(Entity):
    # Override
    # Fields do not share the same schema for leads
    def _load_fields(self):
        fields = self._client.get_entity_fields(self.entity_name)
        self._fields = []
        if fields:
            for field in fields:
                name = field['rest']['name']
                self._fields.append(name)
                setattr(self, name, None)  # Initialize field
                self._id_field = 'id'  # Manually set id field
        else:
            raise InitializationError('Load fields', 'No data returned for entity={}', self.entity_name)

    def get_activities(self, activities, start_date=None):
        """
        Return the lead latest activities of specified types from start date or current date if not specified.
        :param activities: A list of activity type names
        :param start_date: The date to begin retrieving activities from of format 'YYYY-MM-DD'
        :return: A list of activities
        """
        activity_types = self._client.get_activity_types()

        activity_ids = [type_['id'] for type_ in activity_types if type_['name'] in activities]

        if not start_date:
            start_datetime = datetime.utcnow()
        else:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')

        return self._client.get_lead_activities(self.id, activity_ids, start_datetime.isoformat())

    @property
    def _entity_fields_to_update(self):
        field_defaults = {
            'id': None,  # id is mandatory for update
            'firstName': None,
            'lastName': None,
            'email': None,
            'title': None,
            'phone': None,
            'leadSource': None,
            'conversicaLeadOwnerEmail': None,
            'conversicaLeadOwnerFirstName': None,
            'conversicaLeadOwnerLastName': None,
            'pipedriveId': None,
            'leadStatus': None,
            'toDelete': False,
            'leadScore': None,
            'mKTODateSQL': None,
            'leadCountry': None,
            'pDMarketingSuspended': False
        }
        # Fields that cannot be updated at the same time
        if self.externalCompanyId:
            field_defaults['externalCompanyId'] = None
        else:
            field_defaults['website'] = None
            field_defaults['country'] = None
        return field_defaults

    def save(self):
        # Filter leads with no email to prevent from unexpected side effects (e.g. duplicate companies)
        if self.email:
            super(Lead, self).save()
        else:
            self._logger.warning('No data could be saved for entity=%s%s (no email)', self.entity_name,
                              ' with id=%s' % self.id if self.id else '')


class Opportunity(Entity):
    @property
    def _entity_fields_to_update(self):
        return {
            'externalOpportunityId': None,
            'name': 'Default opportunity name',
            'type': None,
            'description': None,
            'lastActivityDate': None,
            'isClosed': None,
            'isWon': None,
            'amount': None,
            'closeDate': None,
            'stage': None,
            'fiscalQuarter': None,
            'fiscalYear': None
        }


class Role(Entity):
    @property
    def entity_name(self):
        return 'opportunities/' + self.__class__.__name__.lower()

    @property
    def _entity_fields_to_update(self):
        return {
            'externalOpportunityId': None,
            'leadId': None,
            'role': None,
            'isPrimary': False  # Set a default value different from null when it is a boolean
        }


class Company(Entity):
    @property
    def _entity_fields_to_update(self):
        return {
            'externalCompanyId': None,
            'company': None,
            'billingStreet': None,
            'billingCity': None,
            'billingState': None,
            'billingCountry': None,
            'mainPhone': None,
            'industry': None,
            'annualRevenue': None,
            'numberOfEmployees': None
        }
