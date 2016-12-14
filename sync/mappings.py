import adapters


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
    'name': {
        'fields': ['firstName', 'lastName'],
        'mode': 'join'
    },
    'email': {
        'fields': ['email']
    },
    'org_id': {
        'transformer': adapters.company_name_to_org_id
    },
    'title': {
        'fields': ['title']
    },
    'phone': {
        'fields': ['phone']
    },
    'inferred_country': {
        'fields': ['inferredCountry', 'leadCountry'],
        'mode': 'choose',
        'pre_adapter': adapters.country_iso_to_name
    },
    'lead_source': {
        'fields': ['leadSource']
    },
    'owner_id': {
        'fields': ['conversicaLeadOwnerFirstName', 'conversicaLeadOwnerLastName'],
        'mode': 'join',
        'post_adapter': adapters.user_name_to_user_id
    },
    'created_date': {
        'fields': ['createdAt'],
        'post_adapter': adapters.datetime_to_date
    },
    'marketoid': {
        'fields': ['id'],
        'post_adapter': adapters.number_to_string
    },
    'state': {
        'fields': ['inferredStateRegion', 'state'],
        'mode': 'choose'
    },
    'city': {
        'fields': ['inferredCity', 'city'],
        'mode': 'choose'
    },
    'lead_score': {
        'fields': ['leadScore']
    },
    'date_sql': {
        'fields': ['mKTODateSQL'],
        'post_adapter': adapters.datetime_to_date
    },
    'lead_status': {
        'fields': ['leadStatus']
    }
}

ORGANIZATION_TO_COMPANY = {
    'name': {
        'fields': ['company']
    },
    'address': {
        'fields': ['billingStreet']
    },
    'city': {
        'fields': ['billingCity']
    },
    'state': {
        'fields': ['billingState']
    },
    'country': {
        'fields': ['billingCountry'],
        'pre_adapter': adapters.country_iso_to_name
    },
    'company_phone': {
        'fields': ['mainPhone']
    },
    'industry': {
        'fields': ['industry']
    },
    'annual_revenue': {
        'fields': ['annualRevenue'],
        'post_adapter': adapters.number_to_float
    },
    'number_of_employees': {
        'fields': ['numberOfEmployees']
    }
}

# To send from Pipedrive to Marketo

LEAD_TO_PERSON = {
    'firstName': {
        'fields': ['name'],
        'post_adapter': adapters.split_name_get_first
    },
    'lastName': {
        'fields': ['name'],
        'post_adapter': adapters.split_name_get_last
    },
    'email': {
        'fields': ['email']
    },
    'externalCompanyId': {
        'fields': ['organization'],
        'pre_adapter': adapters.organization_to_external_id,
    },
    'title': {
        'fields': ['title']
    },
    'phone': {
        'fields': ['phone']
    },
    'leadSource': {
        'fields': ['lead_source']
    },
    'conversicaLeadOwnerEmail': {
        'fields': ['owner'],
        'pre_adapter': adapters.user_to_email
    },
    'conversicaLeadOwnerFirstName': {
        'fields': ['owner'],
        'pre_adapter': adapters.user_to_first_name
    },
    'conversicaLeadOwnerLastName': {
        'fields': ['owner'],
        'pre_adapter': adapters.user_to_last_name
    },
    'pipedriveId': {
        'fields': ['id']
    },
    'leadStatus': {
        'fields': ['lead_status']
    },
    'toDelete': {
        'fields': ['active_flag'],
        'post_adapter': adapters.toggle_boolean
    }
}

COMPANY_TO_ORGANIZATION = {
    'company': {
        'fields': ['name']
    },
    'billingStreet': {
        'fields': ['address']
    },
    'billingCity': {
        'fields': ['city']
    },
    'billingState': {
        'fields': ['state']
    },
    'billingCountry': {
        'fields': ['country'],
        'pre_adapter': adapters.country_iso_to_name
    },
    'mainPhone': {
        'fields': ['company_phone']
    },
    'industry': {
        'fields': ['industry']
    },
    'annualRevenue': {
        'fields': ['annual_revenue']
    },
    'numberOfEmployees': {
        'fields': ['number_of_employees']
    }
}

DEAL_TO_OPPORTUNITY = {
    'name': {
        'fields': ['title']
    },
    'type': {
        'fields': ['type']
    },
    'description': {
        'fields': ['deal_description']
    },
    'lastActivityDate': {
        'fields': ['last_activity_date']
    },
    'isClosed': {
        'fields': ['status'],
        'post_adapter': adapters.is_closed
    },
    'isWon': {
        'fields': ['status'],
        'post_adapter': adapters.is_won
    },
    'amount': {
        'fields': ['value'],
        'post_adapter': adapters.number_to_float
    },
    'closeDate': {
        'fields': ['close_time', 'expected_close_date'],
        'mode': 'choose',
        'post_adapter': adapters.datetime_to_date2
    },
    'stage': {
        'fields': ['stage'],
        'pre_adapter': adapters.stage_to_name
    },
    'fiscalQuarter': {
        'fields': ['close_time', 'expected_close_date'],
        'mode': 'choose',
        'post_adapter': adapters.datetime_to_quarter
    },
    'fiscalYear': {
        'fields': ['close_time', 'expected_close_date'],
        'mode': 'choose',
        'post_adapter': adapters.datetime_to_year
    }
}
