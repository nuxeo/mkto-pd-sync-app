from pycountry import countries
import pipedrive


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
