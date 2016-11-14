from adapters import *


"""
Either "fields" or "transformer" should be provided.
Transformers and adapters are functions that are used for data computation.
The whole resource will be passed as the "transformer" parameter.
For "fields", the field raw value will be passed as the "pre-adapter" parameter
and the final string value will be passed as the "post-adapter" parameter.
"mode" ("join" or "choose") should be provided if several fields are.
"join" mode will join field string values using space before post-adapting.
"choose" mode will chose the first non empty field string value before post-adapting.
"""

# To send from Marketo to Pipedrive

PERSON_TO_LEAD = {
    "name": {
        "fields": ["firstName", "lastName"],
        "mode": "join"
    },
    "email": {
        "fields": ["email"]
    },
    "org_id": {
        "transformer": company_name_to_org_id
    },
    "title": {
        "fields": ["title"]
    },
    "phone": {
        "fields": ["phone"]
    },
    "inferred_country": {
        "fields": ["inferredCountry", "country"],
        "mode": "choose",
        "pre_adapter": country_iso_to_name
    },
    "lead_source": {
        "fields": ["leadSource"]
    },
    "owner_id": {
        "fields": ["conversicaLeadOwnerFirstName", "conversicaLeadOwnerLastName"],
        "mode": "join",
        "post_adapter": lead_name_to_user_id
    },
    "created_date": {
        "fields": ["createdAt"],
        "post_adapter": datetime_to_date
    },
    "marketoid": {
        "fields": ["id"]
    },
    "state": {
        "fields": ["inferredStateRegion", "state"],
        "mode": "choose"
    },
    "city": {
        "fields": ["inferredCity", "city"],
        "mode": "choose"
    },
    "lead_score": {
        "fields": ["leadScore"]
    },
    "date_sql": {
        "fields": ["mKTODateSQL"],
        "post_adapter": datetime_to_date
    },
    "lead_status": {
        "fields": ["leadStatus"],
        "post_adapter": lead_status_to_code
    }
}

ORGANIZATION_TO_COMPANY = {
    "name": {
        "fields": ["company"]
    },
    "address": {
        "fields": ["billingStreet"]
    },
    "city": {
        "fields": ["billingCity"]
    },
    "state": {
        "fields": ["billingState"]
    },
    "country": {
        "fields": ["billingCountry"],
        "pre_adapter": country_iso_to_name
    },
    "company_phone": {
        "fields": ["mainPhone"]
    },
    "industry": {
        "fields": ["industry"],
        "post_adapter": industry_name_to_code
    },
    "annual_revenue": {
        "fields": ["annualRevenue"],
        "post_adapter": number_to_float
    },
    "number_of_employees": {
        "fields": ["numberOfEmployees"]
    }
}

# To send from Pipedrive to Marketo

LEAD_TO_PERSON = {
    "firstName": {
        "fields": ["name"],
        "post_adapter": split_name_get_first
    },
    "lastName": {
        "fields": ["name"],
        "post_adapter": split_name_get_last
    },
    "email": {
        "fields": ["email"]
    },
    "externalCompanyId": {
        "fields": ["organization"],
        "pre_adapter": organization_to_external_id,
    },
    "title": {
        "fields": ["title"]
    },
    "phone": {
        "fields": ["phone"]
    },
    "leadSource": {
        "fields": ["lead_source"]
    },
    "conversicaLeadOwnerEmail": {
        "fields": ["owner"],
        "pre_adapter": user_to_email
    },
    "conversicaLeadOwnerFirstName": {
        "fields": ["owner"],
        "pre_adapter": user_to_first_name
    },
    "conversicaLeadOwnerLastName": {
        "fields": ["owner"],
        "pre_adapter": user_to_last_name
    },
    "pipedriveId": {
        "fields": ["id"]
    },
    "leadStatus": {
        "fields": ["lead_status"],
        "post_adapter": lead_code_to_status
    }
}

COMPANY_TO_ORGANIZATION = {
    "company": {
        "fields": ["name"]
    },
    "billingStreet": {
        "fields": ["address"]
    },
    "billingCity": {
        "fields": ["city"]
    },
    "billingState": {
        "fields": ["state"]
    },
    "billingCountry": {
        "fields": ["country"],
        "pre_adapter": country_iso_to_name
    },
    "mainPhone": {
        "fields": ["company_phone"]
    },
    "industry": {
        "fields": ["industry"],
        "post_adapter": industry_code_to_name
    },
    "annualRevenue": {
        "fields": ["annual_revenue"]
    },
    "numberOfEmployees": {
        "fields": ["number_of_employees"]
    }
}

DEAL_TO_OPPORTUNITY = {
    "name": {
        "fields": ["title"]
    },
    "type": {
        "fields": ["type"],
        "post_adapter": type_code_to_name
    },
    "description": {
        "fields": ["deal_description"]
    },
    "lastActivityDate": {
        "fields": ["last_activity_date"]
    },
    "isClosed": {
        "fields": ["status"],
        "post_adapter": is_closed
    },
    "isWon": {
        "fields": ["status"],
        "post_adapter": is_won
    },
    "amount": {
        "fields": ["value"],
        "post_adapter": number_to_float
    },
    "closeDate": {
        "fields": ["close_time", "expected_close_date"],
        "mode": "choose",
        "post_adapter": datetime_to_date2
    },
    "stage": {
        "fields": ["stage"],
        "pre_adapter": stage_to_name
    },
    "fiscalQuarter": {
        "fields": ["close_time", "expected_close_date"],
        "mode": "choose",
        "post_adapter": datetime_to_quarter
    },
    "fiscalYear": {
        "fields": ["close_time", "expected_close_date"],
        "mode": "choose",
        "post_adapter": datetime_to_year
    }
}
