from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import db, User
from . import auth_bp

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists!'}), 400
    
    # Create a new user
    user = User(
        username=data['username'],
        full_name=data.get('full_name', ''),
        qualification=data.get('qualification', ''),
        is_admin=False
    )
    
    # Simple password setting
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully!'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing username or password"}), 400
    
    print(f"Login attempt: {data.get('username')} / {data.get('password')}")
    
    user = User.query.filter_by(username=data.get('username')).first()
    
    if not user or not user.check_password(data.get('password')):
        return jsonify({"error": "Invalid username or password"}), 401
    
    # Create access token with user ID as identity
    # Set a longer expiration period for development
    access_token = create_access_token(
        identity=str(user.id),
        fresh=True
    )
    
    print(f"Login successful for: {user.username} (ID: {user.id}), admin: {user.is_admin}")
    print(f"Token created (first 15 chars): {access_token[:15]}...")
    
    return jsonify({
        'token': access_token,
        'isAdmin': user.is_admin,
        'userId': user.id,
        'username': user.username
    }), 200 