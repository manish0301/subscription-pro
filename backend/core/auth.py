import jwt
import bcrypt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from backend.core.database import db

class AuthService:
    def __init__(self):
        self.secret_key = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.token_expiry = timedelta(hours=24)
    
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_token(self, user_id, role='customer'):
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.utcnow() + self.token_expiry,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def authenticate_user(self, email, password):
        with db.get_cursor() as (cursor, conn):
            cursor.execute("SELECT user_id, password_hash, user_role FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
            
            if user and self.verify_password(password, user['password_hash']):
                token = self.generate_token(user['user_id'], user['user_role'])
                return {
                    'token': token,
                    'user_id': user['user_id'],
                    'role': user['user_role']
                }
            return None
    
    def register_user(self, email, password, first_name, last_name, role='customer'):
        hashed_password = self.hash_password(password)
        
        with db.get_cursor() as (cursor, conn):
            try:
                cursor.execute("""
                    INSERT INTO users (email, password_hash, first_name, last_name, user_role)
                    VALUES (%s, %s, %s, %s, %s) RETURNING user_id
                """, (email, hashed_password, first_name, last_name, role))
                
                user_id = cursor.fetchone()['user_id']
                conn.commit()
                
                token = self.generate_token(user_id, role)
                return {
                    'token': token,
                    'user_id': user_id,
                    'role': role
                }
            except Exception as e:
                conn.rollback()
                return None

auth_service = AuthService()

def require_auth(allowed_roles=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'No token provided'}), 401
            
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = auth_service.verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            if allowed_roles and payload['role'] not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            request.current_user = payload
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator