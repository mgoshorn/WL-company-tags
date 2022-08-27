from models.models import CompanyName, Company, CompanyTags, Tag, TagLocalization
from util import logger

log = logger.create_logger('company_service')

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