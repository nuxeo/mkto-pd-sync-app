from adapters import *


# To send from Marketo to Pipedrive

PERSON_TO_LEAD = {
    "marketoid": {
        "fields": ["id"]
    },
    "name": {
        "fields": ["firstName", "lastName"]
    },
    "email": {
        "fields": ["email"]
    },
    "inferred_country": {
        "fields": ["country"],
        "post_adapter": country_iso_to_name
    },
    "org_id": {
        "fields": ["company"],
        "post_adapter": company_name_to_org_id
    },
    "lead_score": {
        "fields": ["leadScore"]
    }
}

ORGANIZATION_TO_COMPANY = {
    "name": {
        "fields": ["company"]
    },
    "people_count": {
        "fields": ["numberOfEmployees"]
    }
}

# To send from Pipedrive to Marketo

LEAD_TO_PERSON = {
    "pipedriveId": {
        "fields": ["id"]
    },
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
    "country": {
        "fields": ["inferred_country"],
        "post_adapter": country_name_to_iso
    },
    "externalCompanyId": {
        "fields": ["organization"],
        "pre_adapter": organization_to_name,
        "post_adapter": organization_name_to_external_id
    },
    "leadScore": {
        "fields": ["lead_score"]
    }
}

COMPANY_TO_ORGANIZATION = {
    "company": {
        "fields": ["name"]
    },
    "numberOfEmployees": {
        "fields": ["people_count"]
    }
}

DEAL_TO_OPPORTUNITY = {
    "name": {
        "fields": ["title"]
    }
}
