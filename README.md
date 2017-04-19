# MKTO-PD Sync App

MKTO-PD Sync App is a Flask application running on a Google App Engine that synchronizes data between marketing software Marketo and CRM Pipedrive.


## Features

The application handles user requests **asynchronously** using **task (push) queues**.

```bazaar
                     app.yaml      Application       queue.yaml                       worker.yaml
                        +          enqueues task         +                                 +
                        |                +               |                                 |
             +----------+----------+     |     +---------+----------+           +----------+----------+
             |                     |     |     |                    |           |                     |
             |     Application     |     |     | Task Queue Service |           |       Worker        |
  HTTP POST  |                     |     |     |                    | HTTP POST |                     |
 +----+----->+ +-----------------+ +-----+---->+ +----------------+ +---------->+ +-----------------+ |
      |      | |Flask Application| |           | |   Push Queue   | |           | |Flask Application| |
      |      | +-----------------+ +<----+-----+ +----------------+ +<----+-----+ +-----------------+ |
      |      +---------------------+     |     +--------------------+     |     +---------------------+
      |                                  |                                |                |
      +                                  +                                +                +
User calls API                     Returns task                        Returns   Worker executes task
                                   name and ETA                        sync
                                                                       status

```

### Marketo module

Simple Python client for the Marketo REST API.

#### Features

**Lead**, **opportunities**, **roles** and **companies** are **classes** that can be instantiated given a Marketo **client** instance.

All **fields** are **loaded** and available for **reading** and a defined **subset** for each entity is available for **updating**.

An entity also has an "**id field**" that will be used to match an existing entity.

An **existing** entity can be **loaded** given an identifier to the constructor and an eventual id field to look for different from its actual one
which can be any exiting field for leads but should be a "**searchable field**" for opportunities, roles and companies.

An entity can be **saved**: it is then **created** or **updated** depending on if it matches an existing one.

An entity can be **deleted**.

#### Usage

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

### Pipedrive module

Simple Python client for the Pipedrive REST API.

#### Features

**People**, **organizations**, **deals** and **activities** are classes that can be instantiated given a Pipedrive **client** instance.

All **fields** are **loaded** and available for reading and updating.

An **existing** entity can be **loaded** given an **identifier** or a **name** if the "id field" parameter is given as "name". A lead can also be loaded given a **custom filter** a the "id field". Currently supported filters are "email domain" and "marketo id".

**Custom fields** can be read using the snake case display name rather than their hash key.

Some entities are **related** to other and can be loaded as well if so.

An entity can be **saved**: it is then **created** or **updated** depending on if it matches an existing one.

For related entities, only the association can be updated (**no cascade update**).

An entity can be **deleted**.

#### Usage

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

### API reference

All requests to the API must be made over SSL (https not http) and validated against the `prod` key (see configuration).

#### List of endpoints

- **POST**: `/marketo/lead/<int:lead_id>`: to send lead data from Marketo to Pipedrive

Actually synchronizes data if and only if it is new or it has changed.

- **POST**: `/pipedrive/person/<int:person_id>` (or `/pipedrive/person` for Pipedrive notification usage): to send person data from Pipedrive to Marketo

Actually synchronizes data if and only if it is new or it has changed.

- **POST**: `/pipedrive/organization/<int:organization_id>` (or `/pipedrive/organization` for Pipedrive notification usage): to send organization data from Pipedrive to Marketo

Actually synchronizes data if and only if it is new or it has changed.

- **POST**: `/pipedrive/deal/<int:deal_id>` (or `/pipedrive/deal` for Pipedrive notification usage): to send deal data from Pipedrive to Marketo

Actually synchronizes data if and only if it is new or it has changed.

- **POST**: `/marketo/lead/<int:lead_pipedrive_id>/delete`: to delete a person in Pipedrive (using lead pipedrive id)

- **POST**: `/pipedrive/person/<int:pipedrive_marketo_id>/delete` (or `/pipedrive/person/delete` for Pipedrive notification usage): to delete a lead in Marketo (using person marketo id)

- **POST**: `/marketo/lead/<int:lead_id>/activity` : to send an activity to Pipedrive from Marketo lead data

- **POST**: `/pipedrive/organization/<int:organization_id>/compute` (or `/pipedrive/organization/compute` for Pipedrive notification usage): to compute organization data in Pipedrive

- **POST**: `/pipedrive/deal/notify` (for Pipedrive notification usage only): to notify about a deal (status change and note added) in Slack

### Mapping

A mapping file describes how Marketo and Pipedrive entity fields should be matched.

#### Schema
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

## Installation

Assuming you already have [Python 2.7](https://www.python.org/download/releases/2.7/) installed, you first need to set up a virtual environment containing all the dependencies.
- Install virtualenv if you have not already:
```
pip install virtualenv
```
- Create and activate the virtual environment.
```
cd mkto-pd-sync-app
virtualenv venv
source venv/bin/activate
```
- Install the required packages.
```
pip install -r requirements.txt
```

Then you need to create a new Cloud Platform Console project and install and initialize the [Google Cloud SDK](https://cloud.google.com/sdk/docs/).

For development, you'll also need [Eclipse](http://www.eclipse.org/downloads/packages/eclipse-ide-javascript-and-web-developers/neonr) and a [linked resource](http://help.eclipse.org/luna/index.jsp?topic=%2Forg.eclipse.platform.doc.user%2Fconcepts%2Fcpathvars.htm) `HOME` that targets the folder where you extracted the SDK.

## Configuration

* Create an `instance` folder in the root folder of the project
* Copy the `config.py` file to this folder and set `IDENTITY_ENDPOINT`, `CLIENT_ID`, `CLIENT_SECRET`, `API_ENDPOINT` from your Marketo credentials, `PD_API_TOKEN` from your Pipedrive API token and `FLASK_AUTHORIZED_KEYS` with any keys (one for unit testing and the other for production).

## Running

```
source venv/bin/activate  # Activate the virtual environment to start using it
dev_appserver.py -A sync-app app.yaml worker.yaml  # Start the local development server
deactivate  # Deactivate the virtual environment when you are done working with it
```

## Testing

Marketo and Pipedrive clients are tested in the `tests` module but should not be continuously run as they actually call Marketo and Pipedrive APIs. 

The application is also tested in this module where calls to the APIs have been mocked (see files in the `resources` folder under `tests`).

Run a test case:
```
source venv/bin/activate  # Activate the virtual environment to start using it
python -m tests.test_sync  # Launch test
deactivate  # Deactivate the virtual environment when you are done working with it
```

To run only a single unit test in Eclipse you can use the keybinding **CTRL + F9** while the file open.

## Deployment

You can [upload](https://cloud.google.com/appengine/docs/python/tools/uploadinganapp) the application running the following command from within the root directory of the project:
```
gcloud app deploy app.yaml worker.yaml queue.yaml [--project [YOUR_PROJECT_ID]]
```
