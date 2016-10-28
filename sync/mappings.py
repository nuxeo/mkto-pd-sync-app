from adapters import *


"""
"fields" is mandatory
"mode" ("join" or "choose") should be provided if several fields are
"pre-adapter" is run for each raw field
"post-adapter" is run on final string value
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
        "fields": ["company"],
        "post_adapter": company_name_to_org_id
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
    }
}

ORGANIZATION_TO_COMPANY = {
    "name": {
        "fields": ["company"]
    },
    "industry": {
        "fields": ["industry"],
        "post_adapter": industry_name_to_code
    },
    "people_count": {
        "fields": ["numberOfEmployees"]
    },
    "owner_id": {
        "fields": [],
        "post_adapter": big_bot_id
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
        "pre_adapter": organization_to_name,
        "post_adapter": organization_name_to_external_id
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
    }
}

COMPANY_TO_ORGANIZATION = {
    "company": {
        "fields": ["name"]
    },
    "industry": {
        "fields": ["industry"],
        "post_adapter": industry_code_to_name
    },
    "numberOfEmployees": {
        "fields": ["people_count"]
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
        "fields": ["stage"]
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
