from flask import Flask, jsonify, request
from util import logger
from services import company_service
from sqlalchemy.exc import IntegrityError
from util.errors import AmbiguousRecordError, NotFoundError, UniqueViolationError

log = logger.create_logger('routes')

def initialize_routes(app: Flask):
    log.info("Initializing Flask server")

    # Takes a potentially partial string and searches for companies with names matching it
    # Returns JSON payload including the matching names, language tag, and a UUID
    # of the company
    # Any empty array is considered successful
    @app.get("/companies/name/auto/<name>")
    def get_companies_by_name_auto(name):
        result = company_service.get_companies_by_name_match(name)
        return jsonify(searchString = name, matches = result), 200

    # Retrieves company record by UUID value
    @app.get("/companies/<id>")
    def get_company_by_id(id):
        result = company_service.get_company_by_id(id)
        if result != None:
            return jsonify(matches = result), 200
        else:
            return None, 404

    # Searches for exact matches using the provided company name
    # The result will contain a JSON payload with array data as the same company
    # name could be used in different regions
    @app.get("/companies/name/<name>")
    def get_companies_by_name_exact(name):
        result = company_service.get_companies_by_name_exact(name)
        return jsonify(matches = result)

    @app.get("/companies/tags/<tag>")
    def get_companies_by_tag(tag):
        result = company_service.get_companies_by_tag(tag)
        return jsonify(companies = result)


    # Add existing tags to a company
    # These tags must already exist before they can be added
    # A locale query parameter can be included to specify the exact
    # language to find the tag by - this is only necessary in cases where
    # tags between language happen to have the same name but reference different
    # information

    @app.post("/companies/<name>/tag/name/<tag>")
    def add_company_tag(name, tag):
        language = request.args.get('language', None)
        try:
            result = company_service.add_company_tag_record(name, tag, language=language)
            return '', 201
        except UniqueViolationError as ex:
            return ex.message, 409
        except AmbiguousRecordError as ex:
            return ex.message, 400
        except NotFoundError as ex:
            return ex.message, 404

    @app.delete("/companies/<name>/tag/name/<tag>")
    def delete_company_tag(name, tag):
        language = request.args.get('language', None)
        try:
            result = company_service.remove_tag_from_company(name, tag, language=language)
            return '', 204
        except UniqueViolationError as ex:
            return ex.message, 409
        except NonUniqueError as ex:
            return ex.message, 400

    # Insertion of completely new tags
    # Expects a JSON payload in body defining names in each language
    @app.post("/tags")
    def create_tag():
        data = request.get_json()
        result = company_service.create_tag(data)
