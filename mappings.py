import pipedrive
from pycountry import countries


def org_name_to_id(**kwargs):
    org_name = kwargs["value"]
    client = kwargs["client"]
    ret = ""
    if org_name:
        # Find company in Pipedrive
        organization = client.find_resource_by_name("organization", org_name)
        # Or add it if it does not exist yet
        if organization.id is None:
            organization = pipedrive.Organization(client)
            organization.name = org_name
            # FIXME for test purpose, set owner_id
            organization.owner_id = 1628545  # my (Helene Jonin) owner id
            organization.save()
        ret = organization.id
    return ret


def country_iso_to_name(**kwargs):
    country = kwargs["value"]
    ret = country
    if country is not None:
        ret = countries.get(alpha2=country).name
    return ret

# To send from Marketo to Pipedrive
PERSON_TO_LEAD = {
    "marketoid": {
        "fields": ["id"]
    },
    "name": {
        "fields": ["firstName", "lastName"]
    },
    "email": {
        "fields": ["email"]
    },
    "inferred_country": {
        "fields": ["country"],
        "adapter": country_iso_to_name
    },
    "org_id": {
        "fields": ["company"],
        "adapter": org_name_to_id
    },
    "lead_score": {
        "fields": ["leadScore"]
    }
}


def split_name_get_first(**kwargs):
    name = kwargs["value"]
    split = name.split()
    return " ".join(split[:-1]) if len(split) > 1 else ""


def split_name_get_last(**kwargs):
    name = kwargs["value"]
    split = name.split()
    return split[-1] if split else ""


def country_name_to_iso(**kwargs):
    country = kwargs["value"]
    ret = country
    if country is not None:
        ret = countries.get(name=country).alpha2
    return ret


def organization_to_name(**kwargs):
    organization = kwargs["value"]
    ret = ""
    if organization is not None:
        ret = organization.name
    return ret

# To send from Pipedrive to Marketo
LEAD_TO_PERSON = {
    "pipedriveId": {
        "fields": ["id"]
    },
    "firstName": {
        "fields": ["name"],
        "adapter": split_name_get_first
    },
    "lastName": {
        "fields": ["name"],
        "adapter": split_name_get_last
    },
    "email": {
        "fields": ["email"]
    },
    "country": {
        "fields": ["inferred_country"],
        "adapter": country_name_to_iso
    },
    "company": {
        "fields": ["organization"],
        "adapter": organization_to_name
    },
    "leadScore": {
        "fields": ["lead_score"]
    }
}


def compute_id(**kwargs):
    id_ = kwargs["value"]
    ret = id_  # TODO
    return ret

DEAL_TO_OPPORTUNITY = {
    "externalOpportunityId": {
        "fields": ["id"],
        "adapter": compute_id
    },
    "name": {
        "fields": ["title"]
    }
}


def person_to_id(**kwargs):
    contact_person = kwargs["value"]
    ret = ""
    if contact_person is not None:
        ret = contact_person.marketoid
    return ret


def get_fake_role(**kwargs):
    return "Fake role"

DEAL_TO_ROLE = {
    "externalOpportunityId": {
        "fields": ["id"],
        "adapter": compute_id
    },
    "leadId": {
        "fields": ["contact_person"],
        "adapter": person_to_id
    },
    "role": {
        "fields": ["contact_person"],
        "adapter": get_fake_role
    }
}
