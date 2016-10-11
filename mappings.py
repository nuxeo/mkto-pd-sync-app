import pipedrive
from pycountry import countries


def org_name_to_id(org_name, client):
    # Find company in Pipedrive
    organization = client.find_resource_by_name("organization", org_name)
    # Or add it if it does not exist yet
    if organization.id is None:
        organization = pipedrive.Organization(client)
        organization.name = org_name
        # FIXME for test purpose, set owner_id
        organization.owner_id = 1628545  # my (Helene Jonin) owner id
        organization.save()
    return organization.id


def country_iso_to_name(country, client):
    ret = country
    if country is not None:
        ret = countries.get(alpha2=country).name
    return ret

# To send from Marketo to Pipedrive
PIPEDRIVE_TO_MARKETO = {
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


def split_name_get_first(name, client):
    split = name.split()
    return " ".join(split[:-1]) if len(split) > 1 else ""


def split_name_get_last(name, client):
    split = name.split()
    return split[-1] if split else ""


def get_primary_email(emails, client):
    ret = ""
    for email in emails:
        if email["primary"]:
            ret = email["value"]
    return ret


def country_name_to_iso(country, client):
    ret = country
    if country is not None:
        ret = countries.get(name=country).alpha2
    return ret

# To send from Pipedrive to Marketo
MARKETO_TO_PIPEDRIVE = {
    "firstName": {
        "fields": ["name"],
        "adapter": split_name_get_first
    },
    "lastName": {
        "fields": ["name"],
        "adapter": split_name_get_last
    },
    "email": {
        "fields": ["email"],
        "adapter": get_primary_email
    },
    "country": {
        "fields": ["inferred_country"],
        "adapter": country_name_to_iso
    },
    "leadScore": {
        "fields": ["lead_score"]
    }
}
