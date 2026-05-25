"""
User Model
Quản lý thông tin user và authentication
"""

from flask_login import UserMixin
from datetime import datetime


class User(UserMixin):
    """User model cho Flask-Login"""
    
    def __init__(self, username, email, full_name='', role='user', is_active=True):
        self._username = username
        self._email = email
        self._full_name = full_name
        self._role = role
        self._is_active = is_active
        self._created_at = None
        self._last_login = None
    
    @property
    def username(self):
        return self._username
    
    @username.setter
    def username(self, value):
        self._username = value
    
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, value):
        self._email = value
    
    @property
    def full_name(self):
        return self._full_name
    
    @full_name.setter
    def full_name(self, value):
        self._full_name = value
    
    @property
    def role(self):
        return self._role
    
    @role.setter
    def role(self, value):
        self._role = value
    
    @property
    def is_active(self):
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        self._is_active = value
    
    @property
    def created_at(self):
        return self._created_at
    
    @created_at.setter
    def created_at(self, value):
        self._created_at = value
    
    @property
    def last_login(self):
        return self._last_login
    
    @last_login.setter
    def last_login(self, value):
        self._last_login = value
    
    def get_id(self):
        """Override method cho Flask-Login"""
        return self.username
    
    @property
    def is_admin(self):
        """Kiểm tra user có phải admin không"""
        return self.role == 'admin'
    
    @property
    def is_authenticated(self):
        """Override Flask-Login property"""
        return True
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': str(self.created_at) if self.created_at else None,
            'last_login': str(self.last_login) if self.last_login else None
        }
    
    @staticmethod
    def from_dict(data):
        """Create User from dictionary"""
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            full_name=data.get('full_name', ''),
            role=data.get('role', 'user'),
            is_active=data.get('is_active', True)
        )
        user.created_at = data.get('created_at')
        user.last_login = data.get('last_login')
        return user
