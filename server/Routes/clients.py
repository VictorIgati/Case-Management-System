from flask import Blueprint, request, jsonify
from Models.clients import Client, db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/api/clients', methods=['GET'])
def get_all_clients():
    try:
        clients = Client.query.all()
        return jsonify([{
            'id': client.id,
            'name': client.name,
            'email': client.email,
            'phone': client.phone,
            'address': client.address
        } for client in clients])
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@clients_bp.route('/api/clients', methods=['POST'])
def create_client():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        new_client = Client(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address')
        )
        db.session.add(new_client)
        db.session.commit()
        return jsonify({'message': 'Client created successfully', 'id': new_client.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 409
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@clients_bp.route('/api/clients/<int:id>', methods=['GET'])
def get_client(id):
    try:
        client = Client.query.get(id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        return jsonify({
            'id': client.id,
            'name': client.name,
            'email': client.email,
            'phone': client.phone,
            'address': client.address
        })
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@clients_bp.route('/api/clients/<int:id>', methods=['PUT'])
def update_client(id):
    try:
        client = Client.query.get(id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        client.name = data.get('name', client.name)
        client.email = data.get('email', client.email)
        client.phone = data.get('phone', client.phone)
        client.address = data.get('address', client.address)
        
        db.session.commit()
        return jsonify({'message': 'Client updated successfully'})
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 409
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@clients_bp.route('/api/clients/<int:id>', methods=['DELETE'])
def delete_client(id):
    try:
        client = Client.query.get(id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        if client.cases:
            return jsonify({'error': 'Cannot delete client with active cases'}), 400
            
        db.session.delete(client)
        db.session.commit()
        return jsonify({'message': 'Client deleted successfully'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'message': str(e)}), 500