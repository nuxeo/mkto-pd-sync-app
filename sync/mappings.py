from adapters import *


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
    "no__of_employees__range_": {
        "fields": ["noofEmployeesRange"]
    }
}

ORGANIZATION_TO_COMPANY = {
    "industry": {
        "fields": ["industry"],
        "post_adapter": industry_name_to_code
    },
    "name": {
        "fields": ["company"]
    },
    "people_count": {
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
    "pipedriveId": {
        "fields": ["id"]
    },
    "noofEmployeesRange": {
        "fields": ["no__of_employees__range_"]
    }
}

COMPANY_TO_ORGANIZATION = {
    "industry": {
        "fields": ["industry"],
        "post_adapter": industry_code_to_name
    },
    "company": {
        "fields": ["name"]
    },
    "numberOfEmployees": {
        "fields": ["people_count"]
    }
}

DEAL_TO_OPPORTUNITY = {
    "amount": {
        "fields": ["value"],
        "post_adapter": number_to_float
    },
    "closeDate": {
        "fields": ["close_time"],
        "post_adapter": datetime_to_date2
    },
    "name": {
        "fields": ["title"]
    },
    "stage": {
        "fields": ["stage"]
    },
    "type": {
        "fields": ["type"]
    }
}
