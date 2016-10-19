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
        "adapter": country_iso_to_name
    },
    "org_id": {
        "fields": ["company"]
    },
    "lead_score": {
        "fields": ["leadScore"]
    }
}

# To send from Marketo to Pipedrive
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
        "adapter": split_name_get_first
    },
    "lastName": {
        "fields": ["name"],
        "adapter": split_name_get_last
    },
    "email": {
        "fields": ["email"]
    },
    "country": {
        "fields": ["inferred_country"],
        "adapter": country_name_to_iso
    },
    "company": {
        "fields": ["organization"],
        "adapter": organization_to_name
    },
    "leadScore": {
        "fields": ["lead_score"]
    }
}

# To send from Pipedrive to Marketo
DEAL_TO_OPPORTUNITY = {
    "name": {
        "fields": ["title"]
    }
}
