from datetime import datetime
from pycountry import countries

import marketo
import pipedrive
import sync


BIG_BOT_ID = 208823


def default_name_if_empty(name):
    ret = name
    if not ret.strip():
        ret = "Unknown Unknown"
    return ret


def company_name_to_org_id(lead):
    ret = ""
    if lead.company:  # Case Company object
        res = sync.create_or_update_organization_in_pipedrive(lead.company)
        if res and "id" in res:
            ret = res["id"]
        else:  # Case company form fields
            company = marketo.Company(sync.get_marketo_client())
            company.externalCompanyId = marketo.compute_external_id("lead-company", lead.id, "mkto")
            company.company = lead.company
            company.billingStreet = lead.street
            company.billingCity = lead.city
            company.billingState = lead.state
            company.billingCountry = lead.country
            company.mainPhone = lead.mainPhone
            company.industry = lead.industry
            company.annualRevenue = lead.annualRevenue
            company.numberOfEmployees = lead.numberOfEmployees
            company.save()
            lead.externalCompanyId = company.externalCompanyId
            lead.save()
            res = sync.create_or_update_organization_in_pipedrive(company.company)
            ret = res["id"] if res and "id" in res else ret
    return ret


def country_iso_to_name(country_iso_or_name):
    ret = ""
    if country_iso_or_name:
        try:
            ret = countries.get(alpha2=country_iso_or_name).name
        except KeyError:
            try:
                ret = countries.get(name=country_iso_or_name).name
            except KeyError:
                pass
    return ret


def lead_name_to_user_id(lead_name):
    ret = BIG_BOT_ID
    if lead_name.strip():
        user = pipedrive.User(sync.get_pipedrive_client(), lead_name, "name")
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


def lead_status_to_code(lead_status):
    ret = ""
    statuses = {
        "New": "187",
        "Prospect": "188",
        "MQL": "189",
        "SQL": "190",
        "Qualified Deal": "191",
        "Customer": "192",
        "Former Customer": "193",
        "Partner": "194",
        "Recycled": "195",
        "Disqualified": "196"
        }
    if lead_status and lead_status in statuses:
        ret = statuses[lead_status]
    return ret


def industry_name_to_code(industry_name):
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
    if industry_name and industry_name in industries:
        ret = industries[industry_name]
    return ret


def split_name_get_first(name):
    split = name.split()
    return " ".join(split[:-1]) if len(split) > 1 else ""


def split_name_get_last(name):
    split = name.split()
    return split[-1] if split else ""


def country_name_to_iso(country_name):
    ret = ""
    if country_name:
        try:
            ret = countries.get(name=country_name).alpha2
        except KeyError:
            pass
    return ret


def organization_to_external_id(organization):
    ret = ""
    if organization is not None:
        res = sync.create_or_update_company_in_marketo(organization.name)
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


def lead_code_to_status(lead_code):
    ret = ""
    statuses = {
        "187": "New",
        "188": "Prospect",
        "189": "MQL",
        "190": "SQL",
        "191": "Qualified Deal",
        "192": "Customer",
        "193": "Former Customer",
        "194": "Partner",
        "195": "Recycled",
        "196": "Disqualified"
        }
    if lead_code and lead_code in statuses:
        ret = statuses[lead_code]
    return ret


def organization_to_country(organization):
    ret = ""
    if organization is not None:
        ret = organization.country
    return ret


def industry_code_to_name(industry_code):
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
    if industry_code and industry_code in industries:
        ret = industries[industry_code]
    return ret


def type_code_to_name(type_code):
    ret = ""
    types = {
        "4": "New Business",
        "5": "Upsell",
        "6": "Renewal",
        "129": "Consulting"
    }
    if type_code and type_code in types:
        ret = types[type_code]
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


def stage_to_name(stage):
    ret = ""
    if stage is not None:
        ret = stage.name
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
