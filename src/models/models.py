import uuid
import os
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from util.logger import create_logger

log = create_logger("models")

db = SQLAlchemy()

# CompanyTags = db.Table("CompanyTags",
#     db.Column("company_id", UUID(as_uuid=True), db.ForeignKey("company.id"), primary_key=True),
#     db.Column("tag_id", UUID(as_uuid=True), db.ForeignKey("tag.id"), primary_key=True)
# )

class Company(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    names = db.relationship('CompanyName', backref="company")
    tags = db.relationship('CompanyTags')

class CompanyName(db.Model):
    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('company.id'), primary_key=True)
    language = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)

# On Tags
# Given that the tag concept is that there is a shared meaning that is localized into a variety of languages
# I've created a Tag model which represents the singular meaning and has associated localizations for a variety
# of languages
# This would allow for easily switching localization without relying on assumptions from parsing the tagname
# and allows for the model to easily expand to additional localizations simply by adding a new row to TagLocalization 
# with the new language

class CompanyTags(db.Model):
    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('company.id'), primary_key=True)
    tag_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tag.id'), primary_key=True)
    tag = db.relationship("Tag", foreign_keys="CompanyTags.tag_id")
    company = db.relationship("Company", foreign_keys="CompanyTags.company_id")

class Tag(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    localizations = db.relationship("TagLocalization", backref="tag")

class TagLocalization(db.Model):
    tag_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tag.id'), primary_key=True)
    language = db.Column(db.String(16), primary_key=True)
    name = db.Column(db.String(32), nullable=False)

def initialize_sql(db, app: Flask):
    db_url = os.environ.get('DB_URL')

    if db_url == None:
        log.error("No database URL provided. Shutting down.")
        quit(1)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    log.info("Initializing SQLAlchemy")
    db.app = app
    db.init_app(app)
