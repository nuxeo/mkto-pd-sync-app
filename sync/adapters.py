from datetime import datetime
from pycountry import countries

import views


def company_name_to_org_id(company):
    ret = ""
    if company:
        res = views.create_or_update_organization_in_pipedrive(company)
        ret = res["id"] if res and "id" in res else ""
    return ret


def country_iso_to_name(country):
    ret = ""
    if country:
        try:
            ret = countries.get(alpha2=country).name
        except KeyError:
            pass
    return ret


def datetime_to_date(datetime_):
    ret = ""
    if datetime_:
        ret = datetime.strptime(datetime_, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
    return ret


def industry_name_to_code(industry):
    ret = ""
    industries = {
        "Agriculture": "151",
        "Banking": "152",
        "Biotechnology": "153",
        "Chemicals": "154",
        "Communications": "155",
        "Construction": "156",
        "Consulting": "157",
        "Defense": "158",
        "Education": "159",
        "Electronics": "160",
        "Energy": "161",
        "Engineering": "162",
        "Entertainment": "163",
        "Environmental": "164",
        "Finance": "165",
        "Food & Beverage": "166",
        "Government": "167",
        "Healthcare": "168",
        "Hospitality": "169",
        "Insurance": "170",
        "Machinery": "171",
        "Manufacturing": "172",
        "Media": "173",
        "Not For Profit": "174",
        "Other": "175",
        "Recreation": "176",
        "Retail": "177",
        "Shipping": "178",
        "Technology": "179",
        "Telecommunications": "180",
        "Transportation": "181",
        "Utilities": "182"
        }
    if industry and industry in industries:
        ret = industries[industry]
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
        try:
            ret = countries.get(name=country).alpha2
        except KeyError:
            pass
    return ret


def organization_to_name(organization):
    ret = ""
    if organization is not None:
        ret = organization.name
    return ret


def organization_name_to_external_id(organization):
    ret = ""
    if organization:
        res = views.create_or_update_company_in_marketo(organization)
        ret = res["externalId"] if res and "externalId" in res else ""
    return ret


def industry_code_to_name(industry):
    ret = ""
    industries = {
        "151": "Agriculture",
        "152": "Banking",
        "153": "Biotechnology",
        "154": "Chemicals",
        "155": "Communications",
        "156": "Construction",
        "157": "Consulting",
        "158": "Defense",
        "159": "Education",
        "160": "Electronics",
        "161": "Energy",
        "162": "Engineering",
        "163": "Entertainment",
        "164": "Environmental",
        "165": "Finance",
        "166": "Food & Beverage",
        "167": "Government",
        "168": "Healthcare",
        "169": "Hospitality",
        "170": "Insurance",
        "171": "Machinery",
        "172": "Manufacturing",
        "173": "Media",
        "174": "Not For Profit",
        "175": "Other",
        "176": "Recreation",
        "177": "Retail",
        "178": "Shipping",
        "179": "Technology",
        "180": "Telecommunications",
        "181": "Transportation",
        "182": "Utilities"
        }
    if industry and industry in industries:
        ret = industries[industry]
    return ret


def number_to_float(number):
    ret = ""
    if number:
        ret = float(number)
    return ret


def datetime_to_date2(datetime_):
    ret = ""
    if datetime_:
        ret = datetime.strptime(datetime_, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
    return ret
