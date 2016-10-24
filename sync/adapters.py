from pycountry import countries

import __init__


def company_name_to_org_id(company):
    ret = ""
    if company:
        res = __init__.create_or_update_organization_in_pipedrive(company)
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


def organization_name_to_external_id(organization):
    ret = ""
    if organization:
        res = __init__.create_or_update_company_in_marketo(organization)
        ret = res["externalId"] if res else ""
    return ret
