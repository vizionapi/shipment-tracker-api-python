import os
from app import *
import dateutil.parser as dt
from flask import jsonify
import json
from vizion import create_subscription
from marshmallow import pprint
from models import *

@app.route('/shipments/<shipment_id>', methods=['GET'])
def show_shipment(shipment_id):
    '''
    Show a single shipment record.
    '''
    schema = ShipmentSchema()
    shipment = Shipment.query.get_or_404(shipment_id, 'Container not found.')
    res = schema.dump(shipment)
    return res

@app.route('/containers/<container_id>', methods=['GET'])
def show_container(container_id):
    '''
    Show a single container record.
    '''
    schema = ContainerSchema()
    container = Container.query.get_or_404(container_id, 'Container not found.')
    res = schema.dump(container)
    return res

@app.route('/containers/<container_id>/updates', methods=['GET'])
def list_container_updates(container_id):
    '''
    Show a list of updates for a given container.
    '''
    schema = ContainerSchema()
    update_schema = ContainerUpdateSchema()
    container = Container.query.get_or_404(container_id, 'Container not found.')
    container_updates = ContainerUpdate.query.filter_by(container_id=container_id).all()
    res = update_schema.dump(container_updates, many=True)
    return jsonify(res)

@app.route('/shipments', methods=['GET'])
def list_shipments():
    '''
    List all shipments.
    '''
    schema = ShipmentSchema()
    shipments = Shipment.query.all()
    res = schema.dump(shipments, many=True)
    return jsonify(res)

@app.route('/shipments', methods=['POST'])
def add_shipment():
    '''
    Add a new shipment to DB.\n
    Creates a new Vizion subscription reference for tracking.
    '''
    schema = ShipmentSchema()
    data = request.get_json()
    scac = data.get('scac')
    bol_number = data.get('bill_of_lading')
    container_id = data.get('container_id')

    # Determine whether this shipment is a BL or container
    # Identifier for subscription creation is set based on this value
    is_bol = bol_number != None
    identifier = bol_number if is_bol else container_id

    # Create Vizion reference subscription and return ref ID
    vizion_ref_id = create_subscription(identifier, scac, is_bol)

    # Create shipment record and return
    shipment = Shipment(
        carrier_scac = scac,
        bill_of_lading = bol_number,
        container_id = container_id,
        vizion_reference_id = vizion_ref_id
    )
    db.session.add(shipment)
    db.session.commit()
    res = schema.dump(shipment)
    print('Created new shipment.')
    pprint(res)
    return res, 201

@app.route('/webhook', methods=['POST'])
def webhook():
    '''
    Handle webhook push from Vizion API.\n
    If update is for container not yet identified, creates container record
    then creates a ContainerUpdate record w/ the payload milestones.
    '''
    shipment_schema = ShipmentSchema()
    container_schema = ContainerSchema()
    container_update_schema = ContainerUpdateSchema()
    data = request.get_json()
    if not data:
        print('No data received')
        return { 'message': 'No data received for reference.' }, 422
    payload = data.get('payload')
    # Raise error if no payload received
    if not payload:
        print('No payload received for update')
        return { 'error': 'No payload received' }, 422
        raise
    # Find shipment matching Vizion ref id
    vizion_shipment_id = data.get('parent_reference_id')
    vizion_ref_id = data.get('reference_id')
    shipment = Shipment.query.filter_by(vizion_reference_id=vizion_shipment_id).first()
    if shipment:
        container = Container.query.filter_by(vizion_reference_id=vizion_ref_id).first()
        if not container:
            container = Container(
                shipment_id = shipment.id,
                container_id = payload.get('container_id'),
                vizion_reference_id = vizion_ref_id,
                last_updated_at = dt.isoparse(data.get('updated_at'))
            )
            db.session.add(container)
            db.session.commit()
            print('Added new container.')
            pprint(container_schema.dump(container))
        milestones = []
        for milestone_data in payload.get('milestones'):
            milestone = Milestone(
                description = milestone_data.get('description'),
                location = milestone_data['location'].get('name'),
                unlocode = milestone_data['location'].get('unlocode'),
                country = milestone_data['location'].get('country'),
                vessel = milestone_data.get('vessel'),
                voyage = milestone_data.get('voyage'),
                timestamp = dt.isoparse(milestone_data.get('timestamp')),
                planned = milestone_data.get('planned')
            )
            milestones.append(milestone)
        container_update = ContainerUpdate(
            container_id = container.id,
            milestones = milestones
        )
        db.session.add(container_update)
        db.session.commit()
        print('Created container update for container %r' % container.container_id)
        container_update_data = container_update_schema.dump(container_update)
        pprint(container_update_data)
    else:
        print('No shipment found matching Vizion ID: %r' % vizion_id)
        return { 'message': 'Shipment not found' }, 404
    return { 'message': 'Update received' }, 200

if __name__ == "__main__":
    app.run(debug=True)