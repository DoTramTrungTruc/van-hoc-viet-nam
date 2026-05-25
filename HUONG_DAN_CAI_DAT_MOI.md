# HƯỚNG DẪN CÀI ĐẶT HỆ THỐNG MỚI
## Với tính năng Authentication & Phân quyền User/Admin

---

## 🎯 CÁC TÍNH NĂNG MỚI

### 1. HỆ THỐNG ĐĂNG NHẬP/ĐĂNG KÝ
- ✅ Đăng ký tài khoản user mới
- ✅ Đăng nhập với username hoặc email
- ✅ Đăng xuất
- ✅ Phân quyền User/Admin
- ✅ Bảo mật mật khẩu với bcrypt

### 2. TÍNH NĂNG USER
- ✅ Xem thông tin cá nhân
- ✅ Đổi mật khẩu
- ✅ Tra cứu tác phẩm, tác giả

### 3. TÍNH NĂNG ADMIN
- ✅ Tất cả tính năng của User
- ✅ Thêm/Sửa/Xóa Tác giả
- ✅ Thêm/Sửa/Xóa Tác phẩm
- ✅ Quản lý Users (xem danh sách, phân quyền, khóa tài khoản)
- ✅ Xem thống kê hệ thống

---

## 📦 CÀI ĐẶT

### Bước 1: Cài đặt thư viện mới

```bash
pip install -r requirements.txt
```

Các thư viện mới:
- `Flask-Login==0.6.3` - Quản lý session đăng nhập
- `Flask-Session==0.5.0` - Session management
- `bcrypt==4.1.2` - Hash mật khẩu
- `PyJWT==2.8.0` - JSON Web Tokens

### Bước 2: Import User Schema vào Neo4j

Mở Neo4j Browser và chạy file `database/user_schema.cypher`:

```cypher
// Tạo constraints
CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT user_username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE;

// Tạo admin mặc định
CREATE (admin:User {
  username: 'admin',
  email: 'admin@vanhoc.vn',
  password_hash: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5eRZ7K.6MI.K2',
  full_name: 'Quản trị viên',
  role: 'admin',
  is_active: true,
  created_at: datetime()
})
```

### Bước 3: Cập nhật file .env

Thêm SECRET_KEY cho Flask session:

```env
# Flask Configuration  
SECRET_KEY=your-very-secret-key-here-change-this
SESSION_TYPE=filesystem

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j
```

### Bước 4: Chạy ứng dụng

```bash
cd backend
python app.py
```

---

## 👤 TÀI KHOẢN MẶC ĐỊNH

### Admin:
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: admin@vanhoc.vn

### User thường:
- **Username**: `user1`
- **Password**: `user123`
- **Email**: user1@example.com

---

## 🔐 CẤU TRÚC AUTHENTICATION

### Database Schema

```
User Node:
├── username (unique)
├── email (unique)
├── password_hash (bcrypt)
├── full_name
├── role (user/admin)
├── is_active (boolean)
├── created_at (datetime)
└── last_login (datetime)
```

### API Endpoints Mới

#### Authentication
```
POST   /api/auth/register          - Đăng ký
POST   /api/auth/login             - Đăng nhập
POST   /api/auth/logout            - Đăng xuất
GET    /api/auth/me                - Thông tin user hiện tại
GET    /api/auth/check             - Kiểm tra trạng thái đăng nhập
POST   /api/auth/change-password   - Đổi mật khẩu
```

#### Admin Only
```
GET    /api/auth/users                     - Danh sách users
PUT    /api/auth/users/<username>/role     - Cập nhật role
POST   /api/auth/users/<username>/deactivate - Khóa user
```

#### Tác giả (Admin only cho CUD)
```
GET    /api/tac-gia/               - Xem (Public)
POST   /api/tac-gia/create         - Tạo (Admin)
PUT    /api/tac-gia/<ten>/update   - Sửa (Admin)
DELETE /api/tac-gia/<ten>/delete   - Xóa (Admin)
```

#### Tác phẩm (Admin only cho CUD)
```
GET    /api/tac-pham/              - Xem (Public)
POST   /api/tac-pham/create        - Tạo (Admin)
PUT    /api/tac-pham/<ten>/update  - Sửa (Admin)
DELETE /api/tac-pham/<ten>/delete  - Xóa (Admin)
```

---

## 🎨 CÁC TRANG WEB

### Public (Không cần đăng nhập)
- `/` - Trang chủ
- `/login` - Đăng nhập
- `/register` - Đăng ký
- `/tac-gia` - Danh sách tác giả
- `/tac-pham` - Danh sách tác phẩm
- `/tac-pham/<ten>` - Chi tiết tác phẩm

### User (Cần đăng nhập)
- `/profile` - Thông tin cá nhân

### Admin Only
- `/admin` - Trang quản trị chính
- `/admin/users` - Quản lý users

---

## 💻 CODE EXAMPLES

### Frontend: Kiểm tra đăng nhập

```javascript
async function checkAuth() {
    const response = await fetch('/api/auth/check', {
        credentials: 'include'
    });
    const data = await response.json();
    
    if (data.authenticated) {
        console.log('User:', data.user);
        // Update UI
        if (data.user.is_admin) {
            // Show admin menu
        }
    }
}
```

### Frontend: Đăng nhập

```javascript
async function login(username, password) {
    const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({username, password})
    });
    
    const result = await response.json();
    if (result.success) {
        window.location.href = '/';
    }
}
```

### Backend: Protect route (chỉ admin)

```python
from flask_login import login_required, current_user

@app.route('/api/admin/action', methods=['POST'])
@login_required
def admin_action():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Admin logic here
    return jsonify({'success': True})
```

---

## 🔒 BẢO MẬT

### Password Hashing
Sử dụng bcrypt với salt rounds = 12:
```python
import bcrypt

password_hash = bcrypt.hashpw(
    password.encode('utf-8'), 
    bcrypt.gensalt()
).decode('utf-8')
```

### Session Management
- Flask-Login quản lý sessions
- Secure cookies
- CSRF protection (nên thêm Flask-WTF)

### Best Practices
- ✅ Validate input
- ✅ Hash passwords
- ✅ HTTPS in production
- ✅ Rate limiting (nên thêm)
- ✅ SQL Injection protection (Cypher parameterized queries)

---

## 📝 TESTING

### Test Authentication

```bash
# Đăng ký user mới
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123"}'

# Đăng nhập
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"admin","password":"admin123"}'

# Kiểm tra auth
curl http://localhost:5000/api/auth/check -b cookies.txt

# Tạo tác giả (cần admin)
curl -X POST http://localhost:5000/api/tac-gia/create \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"ten":"Test Author","nam_sinh":1990}'
```

---

## 🚀 DEPLOYMENT

### Production Checklist

1. **Đổi SECRET_KEY**
   ```env
   SECRET_KEY=<random-256-bit-key>
   ```

2. **Enable HTTPS**
   ```python
   app.config['SESSION_COOKIE_SECURE'] = True
   app.config['SESSION_COOKIE_HTTPONLY'] = True
   ```

3. **Disable Debug**
   ```env
   DEBUG=False
   ```

4. **Rate Limiting**
   - Cài Flask-Limiter
   - Giới hạn login attempts

5. **Logging**
   - Log failed login attempts
   - Monitor suspicious activity

---

## 🐛 TROUBLESHOOTING

### Lỗi: "User not found"
→ Chưa import user_schema.cypher vào Neo4j

### Lỗi: "Unauthorized"
→ Kiểm tra cookie/session, đảm bảo `credentials: 'include'`

### Lỗi: "bcrypt not found"
→ `pip install bcrypt==4.1.2`

### Admin không đăng nhập được
→ Kiểm tra password hash đã tạo đúng chưa

---

## 📚 TÀI LIỆU THAM KHẢO

- Flask-Login: https://flask-login.readthedocs.io/
- bcrypt: https://github.com/pyca/bcrypt/
- Neo4j Security: https://neo4j.com/docs/operations-manual/current/security/

---

## 🎯 ROADMAP

### Phase 1 (Hiện tại) ✅
- Authentication basic
- User/Admin roles
- CRUD operations

### Phase 2 (Tương lai)
- [ ] Social login (Google, Facebook)
- [ ] Email verification
- [ ] Password reset
- [ ] User activity logs
- [ ] 2FA (Two-factor authentication)

### Phase 3 (Advanced)
- [ ] User comments/reviews
- [ ] Favorites/Bookmarks
- [ ] Reading history
- [ ] Recommendations

---

## 💡 TIPS

1. **Đổi mật khẩu admin ngay** sau khi deploy production
2. **Backup database** thường xuyên
3. **Monitor logs** để phát hiện tấn công
4. **Update dependencies** định kỳ
5. **Test thoroughly** trước khi deploy

---

**Chúc bạn thành công! 🎉**

Có thắc mắc? Tạo issue hoặc liên hệ support.
