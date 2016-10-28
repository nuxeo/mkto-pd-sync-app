from datetime import datetime
from pycountry import countries
from sync import get_pipedrive_client

import pipedrive
import views


def company_name_to_org_id(company):
    ret = ""
    if company:
        res = views.create_or_update_organization_in_pipedrive(company)
        ret = res["id"] if res and "id" in res else ret
    return ret


def country_iso_to_name(country):
    ret = ""
    if country:
        try:
            ret = countries.get(alpha2=country).name
        except KeyError:
            pass
    return ret


def lead_name_to_user_id(lead):
    ret = "1628545"  # Not Big Bot yet, still my ID (Helene Jonin)!
    if lead.strip():
        user = pipedrive.User(get_pipedrive_client(), lead, "name")
        ret = user.id or ret
    return ret


def datetime_to_date(datetime_):
    ret = ""
    if datetime_:
        try:
            ret = datetime.strptime(datetime_, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
        except ValueError:
            pass
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


def big_bot_id(empty_str):
    return "1628545"  # Not Big Bot yet, still my ID (Helene Jonin)!


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
        ret = res["externalId"] if res and "externalId" in res else ret
    return ret


def user_to_email(user):
    ret = ""
    if user is not None:
        ret = user.email
    return ret


def user_to_first_name(user):
    ret = ""
    if user is not None:
        ret = split_name_get_first(user.name)
    return ret


def user_to_last_name(user):
    ret = ""
    if user is not None:
        ret = split_name_get_last(user.name)
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


def type_code_to_name(type):
    ret = ""
    types = {
        "4": "New Business",
        "5": "Upsell",
        "6": "Renewal",
        "129": "Consulting"
    }
    if type and type in types:
        ret = types[type]
    return ret


def is_closed(status):
    ret = ""
    if status == "lost" or status == "won":
        ret = True
    return ret


def is_won(status):
    ret = ""
    if status == "won":
        ret = True
    return ret


def number_to_float(number):
    ret = ""
    if number:
        ret = float(number)
    return ret or ""


def datetime_to_date2(datetime_):
    ret = ""
    if datetime_:
        try:
            ret = datetime.strptime(datetime_, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        except ValueError:
            try:
                ret = datetime.strptime(datetime_, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                pass
    return ret


def datetime_to_quarter(datetime_):
    ret = ""
    if datetime_:
        try:
            ret = datetime.strptime(datetime_, "%Y-%m-%d %H:%M:%S").year
        except ValueError:
            try:
                ret = datetime.strptime(datetime_, "%Y-%m-%d").year
            except ValueError:
                pass
    return ret


def datetime_to_year(datetime_):
    ret = ""
    if datetime_:
        try:
            ret = (datetime.strptime(datetime_, "%Y-%m-%d %H:%M:%S").month - 1) // 3 + 1
        except ValueError:
            try:
                ret = (datetime.strptime(datetime_, "%Y-%m-%d").month - 1) // 3 + 1
            except ValueError:
                pass
    return ret
