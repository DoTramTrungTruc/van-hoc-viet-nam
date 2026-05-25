"""
Authentication Routes
API endpoints cho đăng ký, đăng nhập, đăng xuất
"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from services.neo4j_service import Neo4jService
from services.auth_service import AuthService
from config import Config

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Khởi tạo services
neo4j_service = Neo4jService(
    uri=Config.NEO4J_URI,
    user=Config.NEO4J_USER,
    password=Config.NEO4J_PASSWORD,
    database=Config.NEO4J_DATABASE
)
auth_service = AuthService(neo4j_service)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Đăng ký tài khoản mới
    POST /api/auth/register
    Body: {
        "username": "...",
        "email": "...",
        "password": "...",
        "full_name": "..."
    }
    """
    data = request.get_json()
    
    # Validate
    required = ['username', 'email', 'password']
    for field in required:
        if not data.get(field):
            return jsonify({
                'success': False,
                'error': f'Thiếu trường bắt buộc: {field}'
            }), 400
    
    # Validate password length
    if len(data['password']) < 6:
        return jsonify({
            'success': False,
            'error': 'Mật khẩu phải có ít nhất 6 ký tự'
        }), 400
    
    try:
        user = auth_service.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data.get('full_name', ''),
            role='user'  # Mặc định là user thường
        )
        
        if user:
            return jsonify({
                'success': True,
                'message': 'Đăng ký thành công! Vui lòng đăng nhập.',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Đăng ký thất bại'
            }), 400
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Lỗi server: {str(e)}'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Đăng nhập
    POST /api/auth/login
    Body: {
        "username": "...",  // hoặc email
        "password": "..."
    }
    """
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            'success': False,
            'error': 'Vui lòng nhập username và password'
        }), 400
    
    try:
        user = auth_service.login(username, password)
        
        if user:
            login_user(user)
            session['user_id'] = user.username
            session['is_admin'] = user.is_admin

            return jsonify({
                'success': True,
                'message': 'Đăng nhập thành công!',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role,
                    'is_admin': user.is_admin
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Username hoặc password không đúng'
            }), 401
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Lỗi server: {str(e)}'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Đăng xuất
    POST /api/auth/logout
    """
    logout_user()
    return jsonify({
        'success': True,
        'message': 'Đã đăng xuất'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """
    Lấy thông tin user hiện tại
    GET /api/auth/me
    """
    return jsonify({
        'success': True,
        'user': {
            'username': current_user.username,
            'email': current_user.email,
            'full_name': current_user.full_name,
            'role': current_user.role,
            'is_admin': current_user.is_admin
        }
    }), 200


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """
    Kiểm tra trạng thái đăng nhập
    GET /api/auth/check
    """
    if current_user.is_authenticated:
        return jsonify({
            'success': True,
            'authenticated': True,
            'user': {
                'username': current_user.username,
                'email': current_user.email,       
                'full_name': current_user.full_name,
                'role': current_user.role,
                'is_admin': current_user.is_admin
            }
        }), 200
    else:
        return jsonify({
            'success': True,
            'authenticated': False
        }), 200


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """
    Đổi mật khẩu
    POST /api/auth/change-password
    Body: {
        "old_password": "...",
        "new_password": "..."
    }
    """
    data = request.get_json()
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({
            'success': False,
            'error': 'Vui lòng nhập đầy đủ thông tin'
        }), 400
    
    if len(new_password) < 6:
        return jsonify({
            'success': False,
            'error': 'Mật khẩu mới phải có ít nhất 6 ký tự'
        }), 400
    
    try:
        success = auth_service.change_password(
            current_user.username,
            old_password,
            new_password
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Đổi mật khẩu thành công'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Đổi mật khẩu thất bại'
            }), 400
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Lỗi server: {str(e)}'
        }), 500


@auth_bp.route('/update-profile', methods=['PUT'])
@login_required
def update_profile():
    """
    Cập nhật thông tin profile
    PUT /api/auth/update-profile
    Body: {
        "email": "...",
        "full_name": "..."
    }
    """
    data = request.get_json()
    
    email = data.get('email')
    full_name = data.get('full_name', '')
    
    if not email:
        return jsonify({
            'success': False,
            'error': 'Email là bắt buộc'
        }), 400
    
    try:
        # Update user info in Neo4j
        query = """
        MATCH (u:User {username: $username})
        SET u.email = $email,
            u.full_name = $full_name
        RETURN u
        """
        
        params = {
            'username': current_user.username,
            'email': email,
            'full_name': full_name
        }
        
        result = neo4j_service.execute_write(query, params)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Cập nhật thông tin thành công',
                'user': {
                    'username': current_user.username,
                    'email': email,
                    'full_name': full_name
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Cập nhật thất bại'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Lỗi server: {str(e)}'
        }), 500


# ===== ADMIN ROUTES =====

@auth_bp.route('/users', methods=['GET'])
@login_required
def get_all_users():
    """
    Lấy danh sách users (Admin only)
    GET /api/auth/users
    """
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Không có quyền truy cập'
        }), 403
    
    try:
        users = auth_service.get_all_users()
        return jsonify({
            'success': True,
            'data': users,
            'count': len(users)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/users/<username>/role', methods=['PUT'])
@login_required
def update_user_role(username):
    """
    Cập nhật role của user (Admin only)
    PUT /api/auth/users/<username>/role
    Body: {"role": "admin" | "user"}
    """
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Không có quyền truy cập'
        }), 403
    
    data = request.get_json()
    role = data.get('role')
    
    if role not in ['user', 'admin']:
        return jsonify({
            'success': False,
            'error': 'Role không hợp lệ'
        }), 400
    
    try:
        success = auth_service.update_user_role(username, role)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Đã cập nhật role cho {username}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Cập nhật thất bại'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/users/<username>/deactivate', methods=['POST'])
@login_required
def deactivate_user(username):
    """
    Vô hiệu hóa user (Admin only)
    POST /api/auth/users/<username>/deactivate
    """
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Không có quyền truy cập'
        }), 403
    
    if username == current_user.username:
        return jsonify({
            'success': False,
            'error': 'Không thể vô hiệu hóa chính mình'
        }), 400
    
    try:
        success = auth_service.deactivate_user(username)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Đã vô hiệu hóa user {username}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Thao tác thất bại'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
# ===== QUÊN MẬT KHẨU =====

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    POST /api/auth/forgot-password
    Body: { "email": "..." }
    """
    import secrets
    import time
    from services.email_service import EmailService
    from config import Config

    data  = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()

    if not email:
        return jsonify({"success": False, "error": "Vui lòng nhập email"}), 400

    # Luôn trả về thành công để tránh lộ email tồn tại
    generic_ok = jsonify({
        "success": True,
        "message": "Nếu email tồn tại, chúng tôi đã gửi link đặt lại mật khẩu."
    })

    user = neo4j_service.get_user_by_email(email)
    if not user:
        return generic_ok   # không lộ thông tin
    # if not user:
    # return jsonify({
    #     "success": False,
    #     "error": "Email không tồn tại trong hệ thống"
    # }), 404 
    # Tạo token an toàn
    token      = secrets.token_urlsafe(48)
    expire_ms  = int(time.time() * 1000) + Config.RESET_TOKEN_EXPIRE_MINUTES * 60 * 1000

    saved = neo4j_service.save_reset_token(email, token, expire_ms)
    if not saved:
        return jsonify({"success": False, "error": "Lỗi hệ thống, thử lại sau"}), 500

    # Gửi email
    full_name = user.get('full_name') or user.get('username') or 'bạn'
    sent      = EmailService.send_reset_password(email, full_name, token)

    if not sent:
        return jsonify({
            "success": False,
            "error": "Không thể gửi email. Kiểm tra lại cấu hình SMTP."
        }), 500

    return generic_ok


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    POST /api/auth/reset-password
    Body: { "token": "...", "password": "...", "confirm_password": "..." }
    """
    import bcrypt
    data     = request.get_json() or {}
    token    = (data.get('token') or '').strip()
    password = data.get('password', '')
    confirm  = data.get('confirm_password', '')

    if not token:
        return jsonify({"success": False, "error": "Token không hợp lệ"}), 400

    if not password or len(password) < 6:
        return jsonify({"success": False,
                        "error": "Mật khẩu phải có ít nhất 6 ký tự"}), 400

    if password != confirm:
        return jsonify({"success": False,
                        "error": "Mật khẩu xác nhận không khớp"}), 400

    # Tìm user theo token
    user = neo4j_service.get_user_by_reset_token(token)
    if not user:
        return jsonify({
            "success": False,
            "error": "Link đặt lại mật khẩu không hợp lệ hoặc đã hết hạn"
        }), 400

    # Hash mật khẩu mới
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    # Cập nhật mật khẩu
    updated = neo4j_service.update_password(user['id'], password_hash)
    if not updated:
        return jsonify({"success": False, "error": "Lỗi cập nhật mật khẩu"}), 500

    # Xóa token đã dùng
    neo4j_service.clear_reset_token(token)

    return jsonify({
        "success": True,
        "message": "Đặt lại mật khẩu thành công! Vui lòng đăng nhập."
    })


@auth_bp.route('/verify-reset-token', methods=['GET'])
def verify_reset_token():
    """
    GET /api/auth/verify-reset-token?token=...
    Kiểm tra token còn hợp lệ không (dùng khi load trang reset)
    """
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({"success": False, "error": "Thiếu token"}), 400

    user = neo4j_service.get_user_by_reset_token(token)
    if not user:
        return jsonify({
            "success": False,
            "error": "Link không hợp lệ hoặc đã hết hạn"
        }), 400

    return jsonify({"success": True, "email": user['email']})
# ===== FAVORITE TAC PHAM =====

@auth_bp.route('/favorites/add', methods=['POST'])
@login_required
def add_favorite():
    try:
        data = request.get_json()
        ten_tac_pham = data.get('ten_tac_pham')

        if not ten_tac_pham:
            return jsonify({
                'success': False,
                'error': 'Thiếu tên tác phẩm'
            }), 400

        query = """
        MATCH (u:User {username: $username})
        MATCH (tp:TacPham {ten: $ten_tac_pham})
        MERGE (u)-[:YEU_THICH]->(tp)
        RETURN tp
        """

        params = {
            'username': current_user.username,
            'ten_tac_pham': ten_tac_pham
        }

        neo4j_service.execute_write(query, params)

        return jsonify({
            'success': True,
            'message': 'Đã thêm vào yêu thích'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/favorites', methods=['GET'])
@login_required
def get_favorites():
    try:
        query = """
        MATCH (u:User {username: $username})-[r:YEU_THICH]->(tp:TacPham)
        RETURN
            tp.ten AS ten,
            tp.anh_dai_dien AS anh_dai_dien
        """

        params = {
            'username': current_user.username
        }

        result = neo4j_service.execute_read(query, params)
        favorites = []

        for item in result:
            favorites.append({
                'ten': item['ten'],
                'anh_dai_dien': item['anh_dai_dien']  # Sửa từ 'anh' thành 'anh_dai_dien' để khớp JS
            })

        return jsonify({
            'success': True,
            'favorites': favorites
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/favorites/remove', methods=['POST'])
@login_required
def remove_favorite():
    try:
        data = request.get_json()
        ten_tac_pham = data.get('ten_tac_pham')

        query = """
        MATCH (u:User {username: $username})-[r:YEU_THICH]->(tp:TacPham {ten: $ten_tac_pham})
        DELETE r
        """

        params = {
            'username': current_user.username,
            'ten_tac_pham': ten_tac_pham
        }

        neo4j_service.execute_write(query, params)

        return jsonify({
            'success': True,
            'message': 'Đã xóa khỏi yêu thích'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/favorite', methods=['POST'])
@login_required
def toggle_favorite():
    try:
        data = request.get_json()
        ten_tac_pham = data.get('ten_tac_pham')

        if not ten_tac_pham:
            return jsonify({
                'success': False,
                'error': 'Thiếu ten_tac_pham'
            }), 400

        # CHECK ĐÃ THÍCH CHƯA
        check_query = """
        MATCH (u:User {username: $username})
        MATCH (tp:TacPham {ten: $ten_tac_pham})
        OPTIONAL MATCH (u)-[r:YEU_THICH]->(tp)
        RETURN r
        """

        result = neo4j_service.execute_read(check_query, {
            'username': current_user.username,
            'ten_tac_pham': ten_tac_pham
        })

        # ĐÃ THÍCH → XÓA
        if result and result[0]['r']:
            delete_query = """
            MATCH (u:User {username: $username})-[r:YEU_THICH]->(tp:TacPham {ten: $ten_tac_pham})
            DELETE r
            """

            neo4j_service.execute_write(delete_query, {
                'username': current_user.username,
                'ten_tac_pham': ten_tac_pham
            })

            return jsonify({
                'success': True,
                'is_favorite': False
            })

        # CHƯA THÍCH → THÊM
        else:
            create_query = """
            MATCH (u:User {username: $username})
            MATCH (tp:TacPham {ten: $ten_tac_pham})
            MERGE (u)-[:YEU_THICH]->(tp)
            """

            neo4j_service.execute_write(create_query, {
                'username': current_user.username,
                'ten_tac_pham': ten_tac_pham
            })

            return jsonify({
                'success': True,
                'is_favorite': True
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@auth_bp.route('/favorites/check', methods=['GET'])
@login_required
def check_favorite():
    try:
        ten_tac_pham = request.args.get('ten_tac_pham')

        if not ten_tac_pham:
            return jsonify({
                'success': False,
                'error': 'Thiếu tên tác phẩm'
            }), 400

        query = """
        MATCH (u:User {username: $username})-[r:YEU_THICH]->(tp:TacPham {ten: $ten_tac_pham})
        RETURN r
        """

        result = neo4j_service.execute_read(query, {
            'username': current_user.username,
            'ten_tac_pham': ten_tac_pham
        })

        is_favorite = len(result) > 0 and result[0]['r'] is not None

        return jsonify({
            'success': True,
            'is_favorite': is_favorite
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500