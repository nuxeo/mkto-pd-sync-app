import adapters

"""
Either "fields" or "transformer" should be provided.
Transformers and adapters are functions that are used for data computation.
The whole entity will be passed as the "transformer" parameter.
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
    'lead_country': {
        'fields': ['leadCountry'],
        'post_adapter': adapters.country_iso_to_name
    },
    'lead_source': {
        'fields': ['leadSource']
    },
    'lead_state': {
        'fields': ['leadState']
    },
    'owner_id': {
        'fields': ['conversicaLeadOwnerFirstName', 'conversicaLeadOwnerLastName'],
        'mode': 'join',
        'post_adapter': adapters.user_name_to_user_id_or_big_bot
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
    },
    'marketing_suspended': {
        'fields': ['pDMarketingSuspended'],
        'post_adapter': adapters.boolean_to_boolean_string
    },
    'demographic_score': {
        'fields': ['demographicScore']
    },
    'behavioral_score': {
        'fields': ['behavioralScore']
    },
    'acquisition_program': {
        'fields': ['acquisitionProgramId'],
        'post_adapter': adapters.program_id_to_name
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
    'b97ac2f12d2071c4c5efbf3a89c812c970f04af1': {  # Use key to differentiate country from address_country fields
        'fields': ['billingCountry'],
        'post_adapter': adapters.country_iso_to_name
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
    },
    'marketoid': {
        'fields': ['id'],
        'post_adapter': adapters.number_to_string
    }
}

ACTIVITY_TO_LEAD = {
    'user_id': {
        'fields': ['conversicaLeadOwnerFirstName', 'conversicaLeadOwnerLastName'],
        'mode': 'join',
        'post_adapter': adapters.user_name_to_user_id_or_big_bot
    },
    'person_id': {
        'fields': ['pipedriveId']
    },
    'type': {
        'transformer': adapters.activity_type
    },
    'subject': {
        'fields': ['firstName', 'lastName'],
        'mode': 'join',
        'post_adapter': adapters.custom_subject
    },
    'note': {
        'fields': ['lastInterestingMoment']
    },
    'due_date': {
        'fields': [],
        'post_adapter': adapters.today_date
    }
}

ACTIVITY_TO_EMAIL_SENT = {
    'user_id': {
        'transformer': adapters.big_bot_id
    },
    'person_id': {
        'fields': ['pipedriveId']
    },
    'type': {
        'transformer': adapters.activity_type_email
    },
    'due_date': {
        'fields': [],
        'post_adapter': adapters.today_date
    },
    'done': {
        'transformer': adapters.activity_done
    },
}

# To send from Pipedrive to Marketo
# /!\ If you add a field here don't forget to add it in marketo.Entity._entity_fields_to_update() too

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
        'post_adapter': adapters.organization_to_external_id
    },
    'title': {
        'fields': ['title']
    },
    'phone': {
        'fields': ['phone']
    },
    'leadSource': {
        'fields': ['lead_source'],
        'post_adapter': adapters.lead_source_pipedrive_default
    },
    'conversicaLeadOwnerEmail': {
        'fields': ['owner'],
        'post_adapter': adapters.user_to_email
    },
    'conversicaLeadOwnerFirstName': {
        'fields': ['owner'],
        'post_adapter': adapters.user_to_first_name
    },
    'conversicaLeadOwnerLastName': {
        'fields': ['owner'],
        'post_adapter': adapters.user_to_last_name
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
    },
    'leadCountry': {
        'fields': ['lead_country']
    },
    'pDMarketingSuspended': {
        'fields': ['marketing_suspended'],
        'post_adapter': adapters.boolean_string_to_boolean
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
        'fields': ['b97ac2f12d2071c4c5efbf3a89c812c970f04af1'],  # Use key to differentiate country from address_country fields
        'post_adapter': adapters.country_iso_to_name
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

PIPELINE_FILTER_NAMES = ['Subscriptions (New and Upsell)', 'Renewals', 'Professional Services']

OPPORTUNITY_TO_DEAL = {
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
        'post_adapter': adapters.stage_to_name
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

COUNTRY_TO_REGION = {
    'Antigua and Barbuda': 'NAM',
    'Bahamas': 'NAM',
    'Barbados': 'NAM',
    'Belize': 'NAM',
    'Bermuda': 'NAM',
    'Canada': 'NAM',
    'Cayman Islands': 'NAM',
    'Costa Rica': 'NAM',
    'Dominica': 'NAM',
    'Dominican Republic': 'NAM',
    'El Salvador': 'NAM',
    'Grenada': 'NAM',
    'Guatemala': 'NAM',
    'Haiti': 'NAM',
    'Honduras': 'NAM',
    'Jamaica': 'NAM',
    'Mexico': 'NAM',
    'Nicaragua': 'NAM',
    'Panama': 'NAM',
    'Puerto Rico': 'NAM',
    'Saint Lucia': 'NAM',
    'Saint Martin': 'NAM',
    'Saint Vincent and the Grenadines': 'NAM',
    'Trinidad and Tobago': 'NAM',
    'Turks and Caicos Islands': 'NAM',
    'Anguilla': 'NAM',
    'Aruba': 'NAM',
    'Guadeloupe': 'NAM',
    'Martinique': 'NAM',
    'Saint Kitts and Nevis': 'NAM',
    'Sint Maarten (Dutch part)': 'NAM',
    'United States': 'NAM',
    'Virgin Islands, British': 'NAM',
    'Virgin Islands, US': 'NAM',
    'Brunei': 'APAC',
    'Cambodia': 'APAC',
    'East Timor': 'APAC',
    'Indonesia': 'APAC',
    'Laos': 'APAC',
    'Malaysia': 'APAC',
    'Myanmar': 'APAC',
    'Philippines': 'APAC',
    'Singapore': 'APAC',
    'Thailand': 'APAC',
    'Vietnam': 'APAC',
    'China': 'APAC',
    'Hong Kong': 'APAC',
    'Macau': 'APAC',
    'Japan': 'APAC',
    'Mongolia': 'APAC',
    'Korea, Republic of': 'APAC',
    'Taiwan': 'APAC',
    'American Samoa': 'APAC',
    'French Polynesia': 'APAC',
    'Pitcairn Islands': 'APAC',
    'Samoa': 'APAC',
    'Tonga': 'APAC',
    'Tuvalu': 'APAC',
    'Wallis and Futuna': 'APAC',
    'Australia': 'APAC',
    'Christmas Island': 'APAC',
    'Cocos (Keeling) Islands': 'APAC',
    'Norfolk Island': 'APAC',
    'New Zealand': 'APAC',
    'Cook Islands': 'APAC',
    'Niue': 'APAC',
    'Tokelau': 'APAC',
    'Fiji': 'APAC',
    'New Caledonia': 'APAC',
    'Papua New Guinea': 'APAC',
    'Solomon Islands': 'APAC',
    'Vanuatu': 'APAC',
    'Federated States of Micronesia': 'APAC',
    'Guam': 'APAC',
    'Kiribati': 'APAC',
    'Marshall Islands': 'APAC',
    'Nauru': 'APAC',
    'Northern Mariana Islands': 'APAC',
    'Palau': 'APAC',
    'Wake Island': 'APAC',
    'Bangladesh': 'APAC',
    'Bhutan': 'APAC',
    'British Indian Ocean Territory': 'APAC',
    'India': 'APAC',
    'Maldives': 'APAC',
    'Nepal': 'APAC',
    'Pakistan': 'APAC',
    'Sri Lanka': 'APAC',
    'France': 'EMEA',
    'Monaco': 'EMEA',
    'Martinique': 'EMEA',
    'Reunion': 'EMEA',
    'United Kingdom': 'EMEA',
    'Ireland': 'EMEA',
    'Belgium': 'EMEA',
    'Netherlands': 'EMEA',
    'Luxembourg': 'EMEA',
    'Germany': 'EMEA',
    'Austria': 'EMEA',
    'Switzerland': 'EMEA',
    'Denmark': 'EMEA',
    'Finland': 'EMEA',
    'Iceland': 'EMEA',
    'Norway': 'EMEA',
    'Sweden': 'EMEA',
    'Greenland': 'EMEA',
    'Faroe Islands': 'EMEA',
    'Aland Islands': 'EMEA',
    'Spain': 'EMEA',
    'Portugal': 'EMEA',
    'Andorra': 'EMEA',
    'Gibraltar': 'EMEA',
    'Italy': 'EMEA',
    'Israel': 'EMEA',
    'Russian Federation': 'EMEA',
    'Czech Republic': 'EMEA',
    'Poland': 'EMEA',
    'Croatia': 'EMEA',
    'Slovakia': 'EMEA',
    'Hungary': 'EMEA',
    'Romania': 'EMEA',
    'Moldova, Republic of': 'EMEA',
    'Serbia': 'EMEA',
    'Lithuania': 'EMEA',
    'Latvia': 'EMEA',
    'Estonia': 'EMEA',
    'Slovenia': 'EMEA',
    'Bulgaria': 'EMEA',
    'Ukraine': 'EMEA',
    'Belarus': 'EMEA',
    'Montenegro': 'EMEA',
    'Bosnia and Herzegovina': 'EMEA',
    'Albania': 'EMEA',
    'Kosovo': 'EMEA',
    'Macedonia': 'EMEA',
    'Bahrain': 'EMEA',
    'Egypt': 'EMEA',
    'Iraq': 'EMEA',
    'Jordan': 'EMEA',
    'Kuwait': 'EMEA',
    'Lebanon': 'EMEA',
    'Oman': 'EMEA',
    'Palestinian Territory': 'EMEA',
    'Qatar': 'EMEA',
    'Saudi Arabia': 'EMEA',
    'Turkey': 'EMEA',
    'United Arab Emirates': 'EMEA',
    'Yemen': 'EMEA',
    'Algeria': 'EMEA',
    'Angola': 'EMEA',
    'Benin': 'EMEA',
    'Botswana': 'EMEA',
    'Burkina Faso': 'EMEA',
    'Burundi': 'EMEA',
    'Cameroon': 'EMEA',
    'Cape Verde': 'EMEA',
    'Central African Republic': 'EMEA',
    'Chad': 'EMEA',
    'Comoros': 'EMEA',
    'Congo': 'EMEA',
    'Congo, The Democratic Republic of the': 'EMEA',
    'Cote D\'Ivoire': 'EMEA',
    'Djibouti': 'EMEA',
    'Eritrea': 'EMEA',
    'Ethiopia': 'EMEA',
    'Gabon': 'EMEA',
    'Gambia': 'EMEA',
    'Ghana': 'EMEA',
    'Guinea': 'EMEA',
    'Guinea-Bissau': 'EMEA',
    'Ivory Coast': 'EMEA',
    'Kenya': 'EMEA',
    'Lesotho': 'EMEA',
    'Liberia': 'EMEA',
    'Libya': 'EMEA',
    'Madagascar': 'EMEA',
    'Malawi': 'EMEA',
    'Mali': 'EMEA',
    'Mauritania': 'EMEA',
    'Mauritius': 'EMEA',
    'Morocco': 'EMEA',
    'Mozambique': 'EMEA',
    'Namibia': 'EMEA',
    'Niger': 'EMEA',
    'Rwanda': 'EMEA',
    'Sao Tome and Principe': 'EMEA',
    'Senegal': 'EMEA',
    'Seychelles': 'EMEA',
    'Somalia': 'EMEA',
    'South Africa': 'EMEA',
    'Swaziland': 'EMEA',
    'Tanzania, United Republic of': 'EMEA',
    'Togo': 'EMEA',
    'Tunisia': 'EMEA',
    'Uganda': 'EMEA',
    'Zambia': 'EMEA',
    'Zimbabwe': 'EMEA',
    'Nigeria': 'EMEA',
    'Argentina': 'SAM',
    'Bolivia': 'SAM',
    'Chile': 'SAM',
    'Colombia': 'SAM',
    'Ecuador': 'SAM',
    'Falkland Islands': 'SAM',
    'French Guiana': 'SAM',
    'Guyana': 'SAM',
    'Paraguay': 'SAM',
    'Peru': 'SAM',
    'Suriname': 'SAM',
    'Uruguay': 'SAM',
    'Venezuela': 'SAM',
    'Brazil': 'SAM'
}
