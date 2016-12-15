from datetime import datetime

from pycountry import countries

import marketo
import pipedrive
import sync

BIG_BOT_ID = 208823


def company_name_to_org_id(lead):
    ret = None
    if lead.company:
        import tasks
        res = tasks.create_or_update_organization_in_pipedrive(lead.externalCompanyId)
        if res and 'id' in res:  # Case Company object
            ret = res['id']
        else:  # Case company form fields
            company = marketo.Company(sync.get_marketo_client())
            company.externalCompanyId = marketo.compute_external_id('lead-company', lead.id, 'mkto')
            company.company = lead.company
            company.billingStreet = lead.street
            company.billingCity = lead.city
            company.billingState = lead.state
            company.billingPostalCode = lead.postalCode
            company.billingCountry = lead.country
            company.mainPhone = lead.mainPhone
            company.industry = lead.industry
            company.annualRevenue = lead.annualRevenue
            company.numberOfEmployees = lead.numberOfEmployees
            company.save()
            lead.externalCompanyId = company.externalCompanyId
            lead.save()
            res = tasks.create_or_update_organization_in_pipedrive(company.externalCompanyId)
            ret = res['id'] if res and 'id' in res else ret
    return ret


def country_iso_to_name(country_iso_or_name):
    ret = country_iso_or_name
    if country_iso_or_name:
        try:
            ret = countries.get(alpha2=country_iso_or_name).name
        except KeyError:
            try:
                ret = countries.get(name=country_iso_or_name).name
            except KeyError:
                pass
    return ret


def user_name_to_user_id(lead_name):
    ret = BIG_BOT_ID
    if lead_name and lead_name.strip():
        user = pipedrive.User(sync.get_pipedrive_client(), lead_name, 'name')  # TODO: use existing value if not found
        ret = user.id or ret
    return ret


def datetime_to_date(datetime_):
    ret = None
    if datetime_:
        try:
            ret = datetime.strptime(datetime_, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
        except ValueError:
            pass
    return ret


def number_to_string(number):
    ret = None
    if number:
        ret = str(number)
    return ret


def split_name_get_first(name):
    ret = name
    if name:
        split = name.split()
        ret = ' '.join(split[:-1]) if len(split) > 1 else ret
    return ret


def split_name_get_last(name):
    ret = name
    if name:
        split = name.split()
        ret = split[-1] if split else ret
    return ret


def organization_to_external_id(organization):
    ret = None
    if organization is not None:
        import tasks
        res = tasks.create_or_update_company_in_marketo(organization.id)
        ret = res['externalId'] if res and 'externalId' in res else ret
    return ret


def user_to_email(user):
    ret = None
    if user is not None and BIG_BOT_ID != user.id:
        ret = user.email
    return ret


def user_to_first_name(user):
    ret = None
    if user is not None and BIG_BOT_ID != user.id:
        ret = split_name_get_first(user.name)
    return ret


def user_to_last_name(user):
    ret = None
    if user is not None and BIG_BOT_ID != user.id:
        ret = split_name_get_last(user.name)
    return ret


def toggle_boolean(boolean):
    return not boolean


def is_closed(status):
    ret = False
    if status == 'lost' or status == 'won':
        ret = True
    return ret


def is_won(status):
    ret = False
    if status == 'won':
        ret = True
    return ret


def number_to_float(number):
    ret = None
    if number:
        ret = float(number)
    return ret


def datetime_to_date2(datetime_):
    ret = None
    if datetime_:
        try:
            ret = datetime.strptime(datetime_, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        except ValueError:
            try:
                ret = datetime.strptime(datetime_, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                pass
    return ret


def stage_to_name(stage):
    ret = None
    if stage is not None:
        ret = stage.name
    return ret


def datetime_to_quarter(datetime_):
    ret = None
    if datetime_:
        try:
            ret = (datetime.strptime(datetime_, '%Y-%m-%d %H:%M:%S').month - 1) // 3 + 1
        except ValueError:
            try:
                ret = (datetime.strptime(datetime_, '%Y-%m-%d').month - 1) // 3 + 1
            except ValueError:
                pass
    return ret


def datetime_to_year(datetime_):
    ret = None
    if datetime_:
        try:
            ret = datetime.strptime(datetime_, '%Y-%m-%d %H:%M:%S').year
        except ValueError:
            try:
                ret = datetime.strptime(datetime_, '%Y-%m-%d').year
            except ValueError:
                pass
    return ret
