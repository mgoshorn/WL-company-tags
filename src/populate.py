# Utility file used to populate database from the wanted_temp_data.csv document
from util.logger import create_logger
from models.models import db
from services import company_service
import csv

log = create_logger('populate')

def purge_db(db):
    log.info("Dropping tables")
    db.drop_all()

def populate_db(db):
    log.info("Running population script")

    db.drop_all()
    db.create_all()

    with open('./wanted-temp-data.csv') as csv_file:
        record_count = sum(1 for row in csv_file) - 1
        log.info("Parsing %s csv records"%record_count)
        
    added_records = 0

    with open('./wanted-temp-data.csv') as csv_file:
        reader = csv.reader(csv_file)

        # Skip header row
        next(reader, None)

        for row in reader:
            company_service.insert_company_from_csv(db, row)
        csv_file.close()

        log.info("Data sync successful")
