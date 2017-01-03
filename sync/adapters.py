from datetime import datetime

from pycountry import countries

import marketo
import pipedrive
import sync

BIG_BOT_ID = 208823


def company_name_to_org_id(lead):
    org_id = None
    if lead.company:
        import tasks
        rv = tasks.create_or_update_organization_in_pipedrive(lead.externalCompanyId)
        if rv and 'id' in rv:  # Case Company object
            org_id = rv['id']
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
            rv = tasks.create_or_update_organization_in_pipedrive(company.externalCompanyId)
            org_id = rv['id'] if rv and 'id' in rv else org_id
    return org_id


def country_iso_to_name(country_iso_or_name):
    country_name = country_iso_or_name
    if country_iso_or_name:
        try:
            country_name = countries.get(alpha2=country_iso_or_name).name
        except KeyError:
            try:
                country_name = countries.get(name=country_iso_or_name).name
            except KeyError:
                pass
    return country_name


def user_name_to_user_id_or_big_bot(user_name):
    user_id = BIG_BOT_ID
    if user_name and user_name.strip():
        user = pipedrive.User(sync.get_pipedrive_client(), user_name, 'name')  # TODO use existing value if not found?
        user_id = user.id or user_id
    return user_id


def user_name_to_user_id(user_name):
    user_id = None
    if user_name and user_name.strip():
        user = pipedrive.User(sync.get_pipedrive_client(), user_name, 'name')
        user_id = user.id
    return user_id


def datetime_to_date(datetime_):
    date = None
    if datetime_:
        try:
            date = datetime.strptime(datetime_, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
        except ValueError:
            pass
    return date


def number_to_string(number):
    number_str = None
    if number:
        number_str = str(number)
    return number_str


def call_type(nothing):
    return 'call'


def custom_subject(name):
    return 'Follow up with %s' % name


def today_date(nothing):
    return datetime.now().strftime('%Y-%m-%d')


def split_name_get_first(name):
    first_name = name
    if name:
        split = name.split()
        first_name = ' '.join(split[:-1]) if len(split) > 1 else first_name
    return first_name


def split_name_get_last(name):
    last_name = name
    if name:
        split = name.split()
        last_name = split[-1] if split else last_name
    return last_name


def organization_to_external_id(organization):
    org_external_id = None
    if organization is not None:
        import tasks
        res = tasks.create_or_update_company_in_marketo(organization.id)
        org_external_id = res['externalId'] if res and 'externalId' in res else org_external_id
    return org_external_id


def user_to_email(user):
    user_email = None
    if user is not None and BIG_BOT_ID != user.id:
        user_email = user.email
    return user_email


def user_to_first_name(user):
    user_first_name = None
    if user is not None and BIG_BOT_ID != user.id:
        user_first_name = split_name_get_first(user.name)
    return user_first_name


def user_to_last_name(user):
    user_last_name = None
    if user is not None and BIG_BOT_ID != user.id:
        user_last_name = split_name_get_last(user.name)
    return user_last_name


def toggle_boolean(boolean):
    return not boolean


def is_closed(status):
    closed = False
    if status == 'lost' or status == 'won':
        closed = True
    return closed


def is_won(status):
    won = False
    if status == 'won':
        won = True
    return won


def number_to_float(number):
    number_float = None
    if number:
        number_float = float(number)
    return number_float


def datetime_to_date2(datetime_):
    date = None
    if datetime_:
        try:
            date = datetime.strptime(datetime_, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        except ValueError:
            try:
                date = datetime.strptime(datetime_, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                pass
    return date


def stage_to_name(stage):
    stage_name = None
    if stage is not None:
        stage_name = stage.name
    return stage_name


def datetime_to_quarter(datetime_):
    quarter = None
    if datetime_:
        try:
            quarter = (datetime.strptime(datetime_, '%Y-%m-%d %H:%M:%S').month - 1) // 3 + 1
        except ValueError:
            try:
                quarter = (datetime.strptime(datetime_, '%Y-%m-%d').month - 1) // 3 + 1
            except ValueError:
                pass
    return quarter


def datetime_to_year(datetime_):
    year = None
    if datetime_:
        try:
            year = datetime.strptime(datetime_, '%Y-%m-%d %H:%M:%S').year
        except ValueError:
            try:
                year = datetime.strptime(datetime_, '%Y-%m-%d').year
            except ValueError:
                pass
    return year
