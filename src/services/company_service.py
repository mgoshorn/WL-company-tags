from models.models import CompanyName, Company, CompanyTags, Tag, TagLocalization
from sqlalchemy import func
from models.models import db
from sqlalchemy.exc import IntegrityError
from util import logger
from util.errors import AmbiguousRecordError, NotFoundError, UniqueViolationError
from util.iso639_1 import languages as iso639_1

"""
    Contains internal service logic relating to companies and tags
"""

log = logger.create_logger('company_service')
language_set = set(map(lambda lang:lang[0], iso639_1))

""" 
    Used to search for companies using incomplete company names
    Will return a list of companies which includes companies with names that match the input
    string in any stored language
"""
def get_companies_by_name_match(name: str):
    search_string = '%{}%'.format(name).lower()
    query = CompanyName.query.filter(func.lower(CompanyName.name).ilike("%{}%".format(name)))
    result = query.all()
    log.debug("Searching for companies with name contains {}, {} records returned".format(search_string, len(result)))
    return format_company_list_output(map(lambda c:c.company, result))

""" Get company by UUID value """
def get_company_by_id(id: str):
    result = Company.query.filter_by(id=id).first()
    return format_company_output(result)

""" 
    Get companies which exactly match the input company name
    Returned as a list, as it is possible that the same name could be used between different
    locations
"""
def get_companies_by_name_exact(name: str):
    result = CompanyName.query.filter_by(name=name).all()
    return format_company_list_output(map(lambda c:c.company, result))
"""

"""
def get_companies_by_tag(tag_name: str):
    tag_localization = TagLocalization.query.filter_by(name=tag_name).all()
    tag_uuids = map(lambda tl:tl.tag_id, tag_localization)
    if tag_localization != None:
        company_tags = CompanyTags.query.filter(CompanyTags.tag_id.in_(tag_uuids)).all()
        log.info(company_tags)
        return format_company_list_output(map(lambda t:t.company, company_tags))
    else:
        return None

""" Maps list of CompanyName records to Company records, removing duplicate Company entries """
def format_company_list_output(company_records: list):
    uuids = set()
    companies = []

    for company_record in company_records:
        if company_record.id in uuids:
            continue
        else:
            uuids.add(company_record.id)
            company = format_company_output(company_record)
            companies.append(company)
    return companies

""" Utility function to map entity storage objects to service output format """
def format_company_output(company_record):
    company = { 
        "id": company_record.id,
        "names": { },
        "tags": [ ]
    }
    for name in company_record.names:
        company["names"][name.language] = name.name
    for company_tag in company_record.tags:
        tag = {
            "id": company_tag.tag_id,
            "localizations": { }
        }
        for localization in company_tag.tag.localizations:
            tag["localizations"][localization.language] = localization.name
        company["tags"].append(tag)
    return company

""" Maps list of CompanyName records to Company records, removing duplicate Company entries """
def map_company_names_to_companies(company_names: list):
    uuids = set()
    companies = []

    for company_name in company_names:
        if company_name.company_id in uuids:
            continue
        else:
            uuids.add(company_name.company_id)
            company = { 
                "id": company_name.company_id,
                "names": { },
                "tags": [ ]
            }
            for name in company_name.company.names:
                company["names"][name.language] = name.name
            for company_tag in company_name.company.tags:
                tag = {
                    "id": company_tag.tag_id,
                    "localizations": { }
                }
                for localization in company_tag.tag.localizations:
                    tag["localizations"][localization.language] = localization.name
                company["tags"].append(tag)

            companies.append(company)
    return companies

""" Create a company tag record between existing company and tag """
def add_company_tag_record(company_name: str, tag_name: str, language=None):
    ids = get_tag_ids_by_name(tag_name, language=language)
    if len(ids) == 0:
        raise NotFoundError("No tag found with provided name.")
    if len(ids) > 1:
        raise AmbiguousRecordError("Multiple tags matching tag name %."%tag_name)
    companies = get_companies_by_name_exact(company_name)
    if len(companies) == 0:
        raise NotFoundError("No companies found with provided name.")
    if len(companies) > 1:
        raise AmbiguousRecordError("Multiple companies matching company name %."%company_name)
    tag_record = CompanyTags(company_id=companies[0]["id"], tag_id=ids[0])
    db.session.add(tag_record)
    try:
        db.session.commit()
    except IntegrityError:
        raise UniqueViolationError("Tag already present on company")


""" Remove a company tag record """
def remove_tag_from_company(company_name: str, tag_name: str, language=None):
    ids = get_tag_ids_by_name(tag_name, language=language)
    if len(ids) == 0:
        raise NotFoundError("No tag found with provided name.")
    if len(ids) > 1:
        raise AmbiguousRecordError("Multiple tags matching tag name %."%tag_name)
    companies = get_companies_by_name_exact(company_name)
    if len(companies) == 0:
        raise NotFoundError("No companies found with provided name.")
    if len(companies) > 1:
        raise AmbiguousRecordError("Multiple companies matching company name %."%company_name)

    tag_record = CompanyTags.query.filter_by(company_id=companies[0]["id"], tag_id=ids[0]).first()
    db.session.delete(tag_record)
    db.session.commit()

""" Add company tag record utilizing UUIDs for Company, Tag - avoids ambiguity in names """
def add_company_tag_record_by_uuid(company_uuid: str, tag_uuid: str):
    company = Company.query.filter_by(id=company_uuid).first()
    tag = Tag.query.filter_by(id=tag_uuid).first()
    if company == None:
        raise NotFoundError("No company found with provided UUID")
    if tag == None:
        raise NotFoundError("No tag found with provided UUID")
    db.session.add(CompanyTags(company=company, tag=tag))
    db.session.commit()

""" Removes company tag record utilizing UUIDs for Company, Tag - avoids ambiguity in names """
def remove_tag_from_company_by_uuid(company_uuid: str, tag_uuid: str):
    tag = CompanyTags.query.filter_by(company_id=company_uuid, tag_id=tag_uuid).first()
    db.session.delete(tag)
    db.session.commit()

"""
    Will accept localization keys for any language matching iso 639-1 specification
    as enumerated in src/util/iso639_1.py
"""
def create_tag(data):
    keys = [p for p in data.keys() if p in language_set]
    tag = Tag()
    for key in keys:
        tag.localizations.append(TagLocalization(language=key, name=data[key]))
    db.session.add(tag)
    db.session.commit()
    payload = { "id": tag.id, "localizations": { }}
    for localization in tag.localizations:
        payload["localizations"][localization.language] = localization.name
    return payload

"""
    Utility function to retrieve ID value of tags by a given name
"""
def get_tag_ids_by_name(tag_name: str, language=None):
    if language == None:
        result = TagLocalization.query.filter_by(name=tag_name).all()
        log.info('y')
        log.info(result)
        return list(map(lambda tl:tl.tag_id, result))
    else:
        result = TagLocalization.query.filter_by(name=tag_name, language=language).first()
        log.info(result)
        return [result.tag_id]

"""
    Utility function to insert CSV record data
"""
def insert_company_from_csv(db, items: list):
    company_ko = items[0].strip(" ")
    company_en = items[1].strip(" ")
    company_ja = items[2].strip(" ")
    tags_ko = items[3].strip(" ").split("|")
    tags_en = items[4].strip(" ").split("|")
    tags_ja = items[5].strip(" ").split("|")

    present = False
    missing = False
    present_record = None

    session = db.session()

    names = []

    # Check if existing company names exist already
    if len(company_ko) > 0:
        result = CompanyName.query.filter_by(name=company_ko, language="ko").first()
        if result != None:
            present = True
            present_record = result
        else:
            missing = True
            names.append(CompanyName(language="ko", name=company_ko))

    if len(company_en) > 0:
        result = CompanyName.query.filter_by(name=company_en, language="en").first()
        if result != None:
            present = True
            present_record = result
        else:
            missing = True
            names.append(CompanyName(language="en", name=company_en))

    
    if len(company_ja) > 0:
        result = CompanyName.query.filter_by(name=company_ja, language="ja").first()
        if result != None:
            present = True
            present_record = result
        else:
            missing = True
            names.append(CompanyName(language="ja", name=company_ja))

    company = None

    # Return early if data for company is already detected
    if present:
        log.debug("Up to date, continuing")
        return

    company = Company()
    company.names.extend(names)
    log.debug("Adding company with names: [%s, %s, %s]"%(company_ko, company_en, company_ja))

    # Validating the tags for equivalency between languages, just a sanity check
    if len(tags_ko) != len(tags_en) or len(tags_ko) != len(tags_ja):
        log.warn("Tag numbers not equivalent between languages.") 

    for x in range(0, len(tags_ko)):
        # Check if tag exists already
        result = TagLocalization.query.filter_by(name=tags_ko[x], language="ko").first()
        if result != None:
            # If tag exists, just add a new CompanyTag record for it
            log.debug("Tag for %s exists already, adding to company"%tags_en[x])
            company.tags.append(CompanyTags(company=company, tag=result.tag))
        else:
            # If the tag does not already exist, create it and and a CompanyTag record
            log.debug("Tag for %s not found. Creating."%tags_en[x])
            tag = Tag()
            tag.localizations.append(TagLocalization(language="ko", name=tags_ko[x]))
            tag.localizations.append(TagLocalization(language="en", name=tags_en[x]))
            tag.localizations.append(TagLocalization(language="ja", name=tags_ja[x]))
            company_tag = CompanyTags(company=company, tag=tag)
            company.tags.append(company_tag)

    if not present:
        db.session.add(company)
    
    db.session.commit()