"""
Admin routes - User management
Quản lý người dùng: thêm, sửa, xóa, phân quyền
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
from services.neo4j_service import Neo4jService
from services.auth_service import AuthService
from config import Config
import re

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

neo4j_service = Neo4jService(
    uri=Config.NEO4J_URI,
    user=Config.NEO4J_USER,
    password=Config.NEO4J_PASSWORD,
    database=Config.NEO4J_DATABASE
)

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Check if user is admin
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users"""
    try:
        users = neo4j_service.get_all_users()
        return jsonify({'success': True, 'data': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get user by ID"""
    try:
        user = neo4j_service.get_user_by_id(user_id)
        if user:
            # Don't send password hash
            user.pop('password_hash', None)
            return jsonify({'success': True, 'data': user})
        else:
            return jsonify({'success': False, 'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
def validate_user_data(data, is_update=False):

    errors = []

    username = str(data.get('username', '')).strip().lower()
    email = str(data.get('email', '')).strip().lower()
    full_name = str(data.get('full_name', '')).strip()
    password = str(data.get('password', '')).strip()

    blocked_usernames = [
        'admin',
        'root',
        'system',
        'support',
        'administrator'
    ]

    fake_domains = [
        'mailinator.com',
        'tempmail.com',
        '10minutemail.com',
        'guerrillamail.com'
    ]

    # =========================
    # BLOCK USERNAME
    # =========================
    if username in blocked_usernames:
        errors.append(
            'Username không được phép sử dụng'
        )

    # =========================
    # USERNAME
    # =========================
    if not is_update or username:

        if not username:
            errors.append("Username không được để trống")

        elif not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            errors.append(
                "Username phải từ 3-20 ký tự, chỉ chứa chữ, số và dấu gạch dưới"
            )

    # =========================
    # EMAIL
    # =========================
    if not is_update or email:

        if not email:
            errors.append("Email không được để trống")

        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            errors.append("Email không hợp lệ")

        else:

            try:

                domain = email.split('@')[1].strip().lower()

                if domain in fake_domains:
                    errors.append("Email không được hỗ trợ")

            except:
                errors.append("Email không hợp lệ")

    # =========================
    # FULL NAME
    # =========================
    if not is_update or full_name:

        if not full_name:
            errors.append("Họ tên không được để trống")

        elif len(full_name) < 2:
            errors.append("Họ tên quá ngắn")

        elif len(full_name) > 100:
            errors.append("Họ tên quá dài")

    # =========================
    # PASSWORD
    # =========================
    if not is_update or password:

        if not password:
            errors.append("Mật khẩu không được để trống")

        elif len(password) < 6:
            errors.append("Mật khẩu phải tối thiểu 6 ký tự")

        elif len(password) > 100:
            errors.append("Mật khẩu quá dài")

    return errors
@admin_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """Create new user"""
    try:
        data = request.get_json(silent=True)
        errors = validate_user_data(data)

        if errors:

            return jsonify({
                'success': False,
                'error': errors
            }), 400
        
        # Check if username exists
        existing = neo4j_service.get_user_by_username(data['username'])
        if existing:
            return jsonify({'success': False, 'error': 'Username đã tồn tại'}), 400
        
        # Check if email exists
        existing = neo4j_service.get_user_by_email(data['email'])
        if existing:
            return jsonify({'success': False, 'error': 'Email đã tồn tại'}), 400
        
        # Hash password
        password_hash = AuthService.hash_password(data['password'])
        
        # Create user
        user_data = {
            'username': data['username'],
            'email': data['email'],
            'full_name': data['full_name'],
            'password_hash': password_hash,
            'is_admin': data.get('is_admin', False),
            'is_active': data.get('is_active', True)
        }
        
        user = neo4j_service.create_user(user_data)
        
        if user:
            user.pop('password_hash', None)
            return jsonify({'success': True, 'data': user}), 201
        else:
            return jsonify({'success': False, 'error': 'Failed to create user'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user"""
    try:
        data = request.get_json()
        # =========================
        # VALIDATE UPDATE
        # =========================
        errors = validate_user_data(
            data,
            is_update=True
        )

        if errors:

            return jsonify({
                'success': False,
                'error': errors
            }), 400
        # Convert current_user.id to int for comparison
        current_user_id = int(current_user.id) if hasattr(current_user, 'id') else None
        
        # Không cho tự khóa tài khoản của mình
        if (
            current_user_id
            and user_id == current_user_id
            and 'is_active' in data
            and not bool(data['is_active'])
        ):

            return jsonify({
                'success': False,
                'error': 'Không thể tự khóa tài khoản của chính mình'
            }), 400
        
        # Build update data
        update_data = {}
        
        if 'username' in data:
            # Validate username
            if not re.match(r'^[a-zA-Z0-9_]{3,20}$', data['username']):
                return jsonify({
                    'success': False, 
                    'error': 'Username không hợp lệ'
                }), 400
            
            # Check if username exists (not current user)
            existing = neo4j_service.get_user_by_username(data['username'])
            if existing and existing['id'] != user_id:
                return jsonify({'success': False, 'error': 'Username đã tồn tại'}), 400
            
            update_data['username'] = data['username']
        
        if 'email' in data:
            # Validate email
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['email']):
                return jsonify({'success': False, 'error': 'Email không hợp lệ'}), 400
            
            # Check if email exists (not current user)
            existing = neo4j_service.get_user_by_email(data['email'])
            if existing and existing['id'] != user_id:
                return jsonify({'success': False, 'error': 'Email đã tồn tại'}), 400
            
            update_data['email'] = data['email']
        
        if 'full_name' in data:
            update_data['full_name'] = data['full_name']
        
        if 'password' in data and data['password']:
            update_data['password_hash'] = AuthService.hash_password(data['password'])
        
        if 'is_admin' in data:
            update_data['is_admin'] = bool(data['is_admin'])
        
        if 'is_active' in data:
            update_data['is_active'] = bool(data['is_active'])
        
        # Update user
        updated = neo4j_service.update_user(user_id, update_data)
        
        if updated:
            updated.pop('password_hash', None)
            return jsonify({'success': True, 'data': updated})
        else:
            return jsonify({'success': False, 'error': 'Failed to update user'}), 500
            logger.error(f"Exception in update_user: {e}", exc_info=True)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    try:
        # Convert current_user.id to int for comparison
        current_user_id = int(current_user.id) if hasattr(current_user, 'id') else None
        
        # Don't allow deleting self
        if current_user_id and user_id == current_user_id:
            return jsonify({
                'success': False, 
                'error': 'Không thể xóa tài khoản của chính mình'
            }), 400
        # =========================
        # CHECK SUPER ADMIN
        # =========================
        target_user = neo4j_service.get_user_by_id(user_id)

        if target_user and target_user.get('username') == 'admin':

            return jsonify({
                'success': False,
                'error': 'Không thể xóa tài khoản admin gốc'
            }), 400
        # Delete user
        success = neo4j_service.delete_user(user_id)
        
        if success:
            return jsonify({'success': True, 'message': 'User deleted'})
        else:
            return jsonify({'success': False, 'error': 'Failed to delete user'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['PUT'])
@admin_required
def toggle_admin(user_id):
    """Toggle admin role"""
    try:
        data = request.get_json()
        
        # Convert current_user.id to int for comparison
        current_user_id = int(current_user.id) if hasattr(current_user, 'id') else None
        
        # Don't allow changing own admin status
        if current_user_id and user_id == current_user_id:
            return jsonify({
                'success': False, 
                'error': 'Không thể thay đổi quyền Admin của chính mình'
            }), 400
        
        is_admin = bool(data.get('is_admin', False))
        role = 'admin' if is_admin else 'user'
        # =========================
        # CHECK ADMIN CUỐI CÙNG
        # =========================
        if not is_admin:

            query = """
            MATCH (u:User)
            WHERE u.is_admin = true
            RETURN count(u) AS total
            """

            result = neo4j_service.execute_query(query, {})

            total_admin = result[0]['total']

            if total_admin <= 1:

                return jsonify({
                    'success': False,
                    'error': 'Hệ thống phải có ít nhất 1 admin'
                }), 400
        # Update admin status
        updated = neo4j_service.update_user(user_id, {
            'is_admin': is_admin,
            'role': role
        })
        
        if updated:
            return jsonify({'success': True, 'data': {'is_admin': is_admin}})
        else:
            return jsonify({'success': False, 'error': 'Failed to update admin status'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500