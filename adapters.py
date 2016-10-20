import marketo_pipedrive_sync
from pycountry import countries


def company_name_to_org_id(company):
    ret = ""
    if company:
        res = marketo_pipedrive_sync.create_or_update_organization_in_pipedrive(company)
        ret = res["id"] if res else ""
    return ret


def country_iso_to_name(country):
    ret = ""
    if country:
        ret = countries.get(alpha2=country).name
    return ret


def split_name_get_first(name):
    split = name.split()
    return " ".join(split[:-1]) if len(split) > 1 else ""


def split_name_get_last(name):
    split = name.split()
    return split[-1] if split else ""


def country_name_to_iso(country):
    ret = ""
    if country:
        ret = countries.get(name=country).alpha2
    return ret


def organization_to_name(organization):
    ret = ""
    if organization is not None:
        ret = organization.name
    return ret
