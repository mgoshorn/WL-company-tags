# Project Description

Supports API operations for searching companies by partial name match (for autocompletion), exact name match, and by tags. Both companies and tags flexibly support multiple localizations for names.

# Project start-up
Recommend using Docker for ease and compatibility, but it may be run directly as well.

## Docker
1. Build image from root directory: `docker build . -t wantedlabs`
2. Run with included docker-compose (will launch database as well): `docker-compose --env-file ./.env-example up`

## Python
1. Create or initialize a PostgreSQL database or other compatible psycopg2 driven database.
2. Install dependencies from requirements.txt.
3. Run application: `python ./src/app.py`. Tested in python 3.9.
4. (Recommended) Set the following environment variables to 'true':
   1. DROP_TABLES_AT_START: drops associated tables at app startup, useful for testing
   2. POPULATE_DATABASE: populates database with data from provided CSV document


# API
Basic documentation relating to API endpoints. In the future I would like to refactor this into Swagger docs, but was a bit short on time.

## Company

### Search for company with partial string

`GET /companies/name/auto/<name>`
Will return data relating to all companies with a name that partially matches the provided string.

Sample: `GET /companies/name/auto/want`
Output:
```
{
    "matches": [
        {
            "id": "a6f6b7db-fc6c-48ac-bfe9-dea37d9b109a",
            "names": {
                "en": "Wantedlab",
                "ko": "원티드랩"
            },
            "tags": [
                {
                    "id": "d7470f70-ed2b-42ef-9c92-b7c3d977c13f",
                    "localizations": {
                        "en": "tag_4",
                        "ja": "タグ_4",
                        "ko": "태그_4"
                    }
                },
                {
                    "id": "f14c8b2d-2175-4d2b-977f-140efeb80fdc",
                    "localizations": {
                        "en": "tag_20",
                        "ja": "タグ_20",
                        "ko": "태그_20"
                    }
                },
                {
                    "id": "2f56389c-3e12-4b5b-9e8c-5c4eed6b8412",
                    "localizations": {
                        "en": "tag_16",
                        "ja": "タグ_16",
                        "ko": "태그_16"
                    }
                }
            ]
        }
    ],
    "searchString": "want"
}
```


`GET /companies/name/<name>`
Returns data relating to all companies with an exact match on the name. Does not assume a single value is present due to the possibility of the same name being utilized between localities.

`GET /companies/<id>`
Returns company data with the matching UUID value.

`GET /companies/tags/<tag>`
Returns all companies with the provided tag name.  Will search between any tag language.

`POST /companies/name/<name>/tag/name/<name>`
Adds a tag to a company given a company name and tag name. Both the company and the tag must already exist. May fail if either the company name or tag name are ambiguous.

`DELETE /companies/name/<name>/tag/name/<name>`
Removes a tag from a company given a company and tag name. Does not remove the tag from the database, only removes the relationship between the company and the tag.  May fail if either the company name or tag name are ambiguous.

`POST /companies/<company_uuid>/tag/<tag_uuid>`
Adds a tag to a company given company and tag UUID.

`DELETE /companies/<company_uuid>/tag/<tag_uuid>`
Adds a tag to a company given company and tag UUID.

`POST /tags`
Creates a new tag with provided localization. Expect a JSON body with keynames matching ISO 639-1 two character language codes.  The value is interpreted as the tag name for the locality.  Will accept any valid language code and will ignore any other keys.

Sample body:
```
{
    "en": "tag_99",
    "ja": "タグ_99",
    "ko": "태그_99",
    "es": "etiqueta_99
}
```

# Data Model
The data as shown in the task description has a few traits that require some additional structure with consideration to the data model.
1. If tags are stored just as they are shown, then we end up breaking column atomicity standards.
2. For both tags and companies, there is no canonical name or ID so there is no explicitly unique reference point exposed. This is particularly problematic for company names, as these are real world entities and if we are tempted to make them unique in the data model to create unique identifiers we would likely discover that the real world rules of company names do not align with our business rules.
3. There are clear relationships between tag names in each locality, but those relationships are not displayed referentially.

To resolve this and ensure that the data solution is both robust and flexible, I applied the following solution:
1. Companies and tags are provided canonical UUID values.
2. Names of both tags and companies are not a part of the company or tag tables, but are instead in referenced tables providing localizations for these objects given a language. This should allow for localizations to arbitrary languages to be added without needing API level changes. The API is equally flexible and will provide more structured data to allow consumers to provide data in a localization applicable to the user.

# Todo
* Create OpenAPI documentation
* Add more comprehensive validation logic
  * Currently, most endpoints will fail without valid data, but will not give the consumer clear information regarding the failure so that they can fix the associated query - some have a bit more support here. This was primarily limited by time and could use some improvement.
