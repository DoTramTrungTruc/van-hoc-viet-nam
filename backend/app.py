"""
Hệ thống Hỏi đáp & Tra cứu Văn học Việt Nam
Main Flask Application
"""

from flask import Flask, render_template, jsonify, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from config import Config
import logging
import os
from services.neo4j_service import Neo4jService

# Import routes
from routes.tac_gia import tac_gia_bp
from routes.tac_pham import tac_pham_bp
from routes.general import general_bp
from routes.auth import auth_bp
from routes.the_loai import the_loai_bp
from routes.nhan_vat import nhan_vat_bp
from routes.qa import qa_bp
from routes.admin import admin_bp
from routes.chat import chat_bp
from routes.forum import forum_bp
from routes.excel import excel_bp
# Import services
from services.neo4j_service import Neo4jService
from services.auth_service import AuthService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    app.config.from_object(config_class)
    app.neo4j_service = Neo4jService(
        uri=Config.NEO4J_URI,
        user=Config.NEO4J_USER,
        password=Config.NEO4J_PASSWORD,
        database=Config.NEO4J_DATABASE
)
    app.config['NEO4J_SERVICE'] = app.neo4j_service
    # Enable CORS
    CORS(app, supports_credentials=True)
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login_page'
    login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này'
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({
            'success': False,
            'error': 'Chưa đăng nhập'
        }), 401
    # User loader
    @login_manager.user_loader
    def load_user(username):
        neo4j_service = Neo4jService(
            uri=Config.NEO4J_URI,
            user=Config.NEO4J_USER,
            password=Config.NEO4J_PASSWORD,
            database=Config.NEO4J_DATABASE
        )
        
        auth_service = AuthService(neo4j_service)
        return auth_service.get_user_by_username(username)
    
    # Register blueprints
    app.register_blueprint(tac_gia_bp)
    app.register_blueprint(tac_pham_bp)
    app.register_blueprint(general_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(the_loai_bp)
    app.register_blueprint(nhan_vat_bp)
    app.register_blueprint(qa_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(forum_bp)
    app.register_blueprint(excel_bp)
    # Home route
    @app.route('/')
    def index():
        """Trang chủ"""
        return render_template('index.html')
    
    @app.route('/tac-gia/<ten>')
    def tac_gia_detail_page(ten):    
        return render_template('tac_gia_detail.html')
    # Auth pages
    @app.route('/login')
    def login_page():
        """Trang đăng nhập"""
        return render_template('login.html')
    
    @app.route('/register')
    def register_page():
        """Trang đăng ký"""
        return render_template('register.html')
    
    @app.route('/profile')
    @login_required
    def profile_page():
        """Trang thông tin user"""
        return render_template('profile.html')
    
    # Main pages
    @app.route('/tac-gia')
    def tac_gia_page():
        """Trang danh sách tác giả"""
        return render_template('tac_gia.html')
    
    @app.route('/tac-pham')
    def tac_pham_page():
        """Trang danh sách tác phẩm"""
        return render_template('tac_pham.html')
    
    @app.route('/tac-pham/<ten>')
    def tac_pham_detail_page(ten):
        """Trang chi tiết tác phẩm"""
        return render_template('tac_pham_detail.html', ten=ten)
    @app.route('/hoi-dap')
    def hoi_dap_page():
        return render_template('hoi_dap.html')
    @app.route('/dien-dan')
    def dien_dan_page():
        """Trang diễn đàn văn học"""
        return render_template('dien_dan.html')
    @app.route('/forgot-password')
    def forgot_password_page():
        return render_template('forgot_password.html')
 
    @app.route('/reset-password')
    def reset_password_page():
        return render_template('reset_password.html')
    # Admin pages (chỉ cho admin)
    @app.route('/admin')
    @login_required
    def admin_page():
        """Trang quản trị - chỉ admin"""
        if not current_user.is_admin:
            return redirect(url_for('index'))
        return render_template('admin.html')
    
    @app.route('/admin/users')
    @login_required
    def admin_users_page():
        """Trang quản lý users - chỉ admin"""
        if not current_user.is_admin:
            return redirect(url_for('index'))
        return render_template('admin_users.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Không tìm thấy trang'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Server Error: {error}')
        return jsonify({
            'success': False,
            'error': 'Lỗi máy chủ'
        }), 500
    
    logger.info("Flask app created successfully")
    return app


if __name__ == '__main__':
    app = create_app()
    logger.info("Starting Flask development server...")

    app.run(
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 5000))
    )