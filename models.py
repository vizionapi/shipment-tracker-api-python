from app import *
from sqlalchemy.sql import func
import dateutil.parser as dt
import json
from marshmallow import Schema, fields, pprint

class MilestoneSchema(Schema):
    id = fields.Int()
    container_id = fields.Str()
    description = fields.Str()
    location = fields.Str()
    unlocode = fields.Str()
    country = fields.Str()
    vessel = fields.Str()
    voyage = fields.Str()
    timestamp = fields.DateTime()
    planned = fields.Bool()
    created_at = fields.DateTime()

class ContainerSchema(Schema):
    id = fields.Int()
    container_id = fields.Str()
    shipment_id = fields.Str()
    created_at = fields.DateTime()
    last_updated_at = fields.DateTime()

class ContainerUpdateSchema(Schema):
    id: fields.Int()
    container_id: fields.Str()
    milestones = fields.Nested(MilestoneSchema, many=True)
    created_at = fields.DateTime()

class ShipmentSchema(Schema):
    id = fields.Int()
    container_id = fields.Str()
    bill_of_lading = fields.Str()
    carrier_scac = fields.Str()
    vizion_reference_id = fields.Str()
    containers = fields.Nested(ContainerSchema, many=True)
    created_at = fields.DateTime()
    last_updated_at = fields.DateTime()

class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carrier_scac = db.Column(db.String(4), nullable=False)
    vizion_reference_id = db.Column(db.String(80), nullable=False, unique=True)
    bill_of_lading = db.Column(db.String(80), nullable=True)
    container_id = db.Column(db.String(80), nullable=True)
    containers = db.relationship('Container', backref='shipment', lazy=True)
    created_at = db.Column(db.DateTime, default=func.now())
    last_updated_at = db.Column(db.DateTime, onupdate=func.now())

    def __repr__(self):
        return '<Shipment %r>' % (self.bill_of_lading or self.container_id)

class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipment.id'), nullable=False)
    vizion_reference_id = db.Column(db.String(80), nullable=False, unique=True)
    container_id = db.Column(db.String(80), nullable=False)
    container_updates = db.relationship('ContainerUpdate', backref='container', lazy=True)
    created_at = db.Column(db.DateTime, default=func.now())
    last_updated_at = db.Column(db.DateTime, nullable=True, onupdate=func.now())

    def __repr__(self):
        return '<Container %r>' % self.container_id

class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    container_update_id = db.Column(db.Integer, db.ForeignKey('container_update.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    unlocode = db.Column(db.String(5), nullable=True)
    country = db.Column(db.String(80), nullable=True)
    vessel = db.Column(db.String(255), nullable=True)
    voyage = db.Column(db.String(80), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=True)
    planned = db.Column(db.Boolean, nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())

class ContainerUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    container_id = db.Column(db.Integer, db.ForeignKey('container.id'), nullable=False)
    milestones = db.relationship('Milestone', backref='container_update', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())
