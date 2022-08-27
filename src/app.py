import os
from util import logger
from models.models import db, initialize_sql
from flask import Flask
from populate import purge_db, populate_db

log = logger.create_logger('app')
log.info("Application initializing")

app = Flask(__name__)

initialize_sql(db, app)

if os.environ.get('DROP_TABLES_AT_START').upper() == "TRUE":
    purge_db(db)

if os.environ.get('POPULATE_DATABASE').upper() == "TRUE":
    populate_db(db)

log.info("Configuring routing")
