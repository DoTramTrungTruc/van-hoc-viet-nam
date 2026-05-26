"""
File cấu hình ứng dụng
Chứa các thông tin kết nối database và cấu hình hệ thống
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Cấu hình chung cho ứng dụng"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-van-hoc-kg-change-this-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Session Configuration
    SESSION_TYPE = os.getenv('SESSION_TYPE', 'filesystem')
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Neo4j Configuration
    NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j+s://ae54e57b.databases.neo4j.io')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')
    NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'ae54e57b')
    
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
    # Application Configuration
    ITEMS_PER_PAGE = 10
    MAX_SEARCH_RESULTS = 50
     # Email Configuration (Gmail SMTP)
    MAIL_SERVER   = os.getenv('MAIL_SERVER',   'smtp.gmail.com')
    MAIL_PORT     = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS  = os.getenv('MAIL_USE_TLS',  'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')   # Gmail của bạn
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')   # App Password Gmail
    MAIL_FROM     = os.getenv('MAIL_FROM',     '')   # Tên hiển thị + email
    APP_URL       = os.getenv('APP_URL', 'http://localhost:5000')
 
    # Reset token expire (phút)
    RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv('RESET_TOKEN_EXPIRE_MINUTES', '30'))
