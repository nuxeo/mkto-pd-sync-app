# Sync App

Synchronize data between Marketo and Pipedrive.

## sync module

Parent module containing client submodules and synchronization application.

## marketo module

Simple Python client for the Marketo REST API.

### Main features

Lead, opportunities, roles and companies are classes that can be instantiated given a Marketo client instance.

All fields are loaded and available for reading and a defined subset for each entity is available for updating.

An entity also has an "id field" that will be used to match an existing entity.

An existing entity can be loaded given an identifier to the constructor and an eventual id field to look for different from its actual one
which can be any exiting field for leads but should be a "searchable field" for opportunities, roles and companies.

An entity can be saved: it is then created or updated depending on if it matches an existing one.

An entity can be deleted.

### Usage

```python
import sync.marketo as marketo

mkto = marketo.MarketoClient(IDENTITY_ENDPOINT, CLIENT_ID, CLIENT_SECRET, API_ENDPOINT)

# Get a lead by id
lead = marketo.Lead(mkto, "12345")

# Get a lead by email
lead = marketo.Lead(mkto, "lead@mail.com", "email")

# Update lead data
lead.firstName = "New Name"
lead.save()

# Delete lead
lead.delete()
```

## pipedrive module

Simple Python client for the Pipedrive REST API.

### Main features

People, organizations deals and activities are classes that can be instantiated given a Pipedrive client instance.

All fields are loaded and available for reading and updating.

An existing entity can be loaded given an identifier or a name if the "id field" parameter is given as "name". A lead can also be loaded given a custom filter a the "id field". Currently supported filters are "email domain" and "marketo id".

Custom fields can be read using the snake case display name rather than their hash key.

Some entities are related to other and can be loaded as well if so.

An entity can be saved: it is then created or updated depending on if it matches an existing one.

For related entities, only the association can be updated (no cascade update).

An entity can be deleted.

### Usage

```python
import sync.pipedrive as pipedrive

pd = pipedrive.PipedriveClient(PD_API_TOKEN)

# Get a person by id
person = pipedrive.Person(pd, "12345")

# Get an organization by name
organization = pipedrive.Organization(pd, "MyCompany", "name")

# Get a person custom field with its nicer name
person.lead_score  # or getattr(person, {HASH KEY})

# Get a person related organization
organization = person.organization

# Update person data
person.name = "New Name"
person.save()

# Delete person
person.delete()
```

## sync module

Simple Flask app to synchronize data between Marketo and Pipedrive.

### Main features

#### Endpoints

List of endpoints accessible through a POST request:
- `/marketo/lead/<int:lead_id>`: to send lead data from Marketo to Pipedrive

Actually synchronizes data if and only if it is new or it has changed.

- `/pipedrive/person/<int:person_id>` (or `/pipedrive/person` for Pipedrive notification usage): to send person data from Pipedrive to Marketo

Actually synchronizes data if and only if it is new or it has changed.

- `/pipedrive/organization/<int:organization_id>` (or `/pipedrive/organization` for Pipedrive notification usage): to send organization data from Pipedrive to Marketo

Actually synchronizes data if and only if it is new or it has changed.

- `/pipedrive/deal/<int:deal_id>` (or `/pipedrive/deal` for Pipedrive notification usage): to send deal data from Pipedrive to Marketo

Actually synchronizes data if and only if it is new or it has changed.

- `/marketo/lead/<int:lead_pipedrive_id>/delete`: to delete a person in Pipedrive (using lead pipedrive id)

- `/pipedrive/person/<int:pipedrive_marketo_id>/delete` (or `/pipedrive/person/delete` for Pipedrive notification usage): to delete a lead in Marketo (using person marketo id)

- `/marketo/lead/<int:lead_id>/activity` : to send an activity to Pipedrive from Marketo lead data

#### Authentication

All routes require authentication using an API key as GET parameter.

#### Mapping

A mapping file describes how Marketo and Pipedrive entity fields should be matched.

##### Schema
```
MAPPING_NAME = {
    to_field_key_1: {
        "fields": [from_field_key_1, [from_field_key_2...]],
        ["mode": "join"/"choose",]
        ["pre_adapter": function,]
        ["post_adapter": function]
    },
    to_field_key_2: {
        "transformer": function
    }
}
```

## Processing

Any call to one of the endpoint enqueue a task to a Google Push task queue that is handling the processing asynchronously but sequentially.

It returns the name and the task ETA while tasks return the synchronisation status ("created", "updated" or "skipped") as well as the id of the created/updated entity in JSON.

## Testing

Marketo and Pipedrive clients are tested in the tests module, as well as the sync app.
