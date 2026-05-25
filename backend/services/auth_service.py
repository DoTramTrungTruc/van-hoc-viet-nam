"""
Authentication Service
Xử lý đăng ký, đăng nhập, và quản lý user
"""

import bcrypt
from datetime import datetime
from typing import Optional, Dict
from .neo4j_service import Neo4jService
from models.user import User


class AuthService:
    """Service xử lý authentication"""
    
    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j = neo4j_service
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password bằng bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def register_user(self, username: str, email: str, password: str, 
                     full_name: str = '', role: str = 'user') -> Optional[User]:
        """
        Đăng ký user mới
        
        Args:
            username: Tên đăng nhập (unique)
            email: Email (unique)
            password: Mật khẩu (sẽ được hash)
            full_name: Họ tên đầy đủ
            role: Vai trò (user/admin)
            
        Returns:
            User object nếu thành công, None nếu thất bại
        """
        # Kiểm tra username đã tồn tại
        existing = self.get_user_by_username(username)
        if existing:
            raise ValueError('Username đã tồn tại')
        
        # Kiểm tra email đã tồn tại
        existing_email = self.get_user_by_email(email)
        if existing_email:
            raise ValueError('Email đã tồn tại')
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Tạo user trong Neo4j với auto-increment ID
        query = """
        MATCH (u:User)
        WITH COALESCE(MAX(u.id), 0) AS max_id
        CREATE (new:User {
            id: max_id + 1,
            username: $username,
            email: $email,
            password_hash: $password_hash,
            full_name: $full_name,
            role: $role,
            is_admin: false,
            is_active: true,
            created_at: datetime(),
            last_login: null
        })
        RETURN new
        """
        
        params = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'full_name': full_name,
            'role': role
        }
        
        result = self.neo4j.execute_query(query, params)
        
        if result and len(result) > 0:
            return User.from_dict(dict(result[0]['new']))
        return None
    
    def login(self, username: str, password: str) -> Optional[User]:
        """
        Đăng nhập
        
        Args:
            username: Tên đăng nhập hoặc email
            password: Mật khẩu
            
        Returns:
            User object nếu đăng nhập thành công
        """
        # Tìm user (có thể dùng username hoặc email)
        query = """
        MATCH (u:User)
        WHERE u.username = $username OR u.email = $username
        RETURN u
        """
        
        results = self.neo4j.execute_query(query, {'username': username})
        
        if not results:
            return None
        
        user_data = dict(results[0]['u'])
        
        # Kiểm tra user có active không
        if not user_data.get('is_active', True):
            raise ValueError('Tài khoản đã bị khóa')
        
        # Verify password
        if not self.verify_password(password, user_data['password_hash']):
            return None
        
        # Cập nhật last_login
        self.update_last_login(user_data['username'])
        
        # Return User object
        return User.from_dict(user_data)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Lấy user theo username"""
        query = """
        MATCH (u:User {username: $username})
        RETURN u
        """
        
        results = self.neo4j.execute_query(query, {'username': username})
        
        if results:
            return User.from_dict(dict(results[0]['u']))
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Lấy user theo email"""
        query = """
        MATCH (u:User {email: $email})
        RETURN u
        """
        
        results = self.neo4j.execute_query(query, {'email': email})
        
        if results:
            return User.from_dict(dict(results[0]['u']))
        return None
    
    def update_last_login(self, username: str):
        """Cập nhật thời gian đăng nhập cuối"""
        query = """
        MATCH (u:User {username: $username})
        SET u.last_login = datetime()
        """
        
        self.neo4j.execute_write(query, {'username': username})
    
    def get_all_users(self) -> list:
        """Lấy danh sách tất cả users (admin only)"""
        query = """
        MATCH (u:User)
        RETURN u
        ORDER BY u.created_at DESC
        """
        
        results = self.neo4j.execute_query(query)
        return [User.from_dict(dict(r['u'])).to_dict() for r in results]
    
    def update_user_role(self, username: str, role: str) -> bool:
        """Cập nhật role của user (admin only)"""
        query = """
        MATCH (u:User {username: $username})
        SET u.role = $role
        RETURN u
        """
        
        result = self.neo4j.execute_write(query, {
            'username': username,
            'role': role
        })
        
        return result is not None
    
    def deactivate_user(self, username: str) -> bool:
        """Vô hiệu hóa user (admin only)"""
        query = """
        MATCH (u:User {username: $username})
        SET u.is_active = false
        RETURN u
        """
        
        result = self.neo4j.execute_write(query, {'username': username})
        return result is not None
    
    def activate_user(self, username: str) -> bool:
        """Kích hoạt user (admin only)"""
        query = """
        MATCH (u:User {username: $username})
        SET u.is_active = true
        RETURN u
        """
        
        result = self.neo4j.execute_write(query, {'username': username})
        return result is not None
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Đổi mật khẩu"""
        # Verify old password
        user_data = self.get_user_by_username(username)
        if not user_data:
            return False
        
        # Get password hash from database
        query = """
        MATCH (u:User {username: $username})
        RETURN u.password_hash as password_hash
        """
        results = self.neo4j.execute_query(query, {'username': username})
        
        if not results:
            return False
        
        if not self.verify_password(old_password, results[0]['password_hash']):
            raise ValueError('Mật khẩu cũ không đúng')
        
        # Update password
        new_hash = self.hash_password(new_password)
        
        query = """
        MATCH (u:User {username: $username})
        SET u.password_hash = $password_hash
        RETURN u
        """
        
        result = self.neo4j.execute_write(query, {
            'username': username,
            'password_hash': new_hash
        })
        
        return result is not None