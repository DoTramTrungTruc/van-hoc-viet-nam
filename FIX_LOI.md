# 🔧 HƯỚNG DẪN SỬA LỖI ĐĂNG NHẬP/ĐĂNG KÝ

## ❌ CÁC LỖI THƯỜNG GẶP

### Lỗi 1: "property 'is_active' of 'User' object has no setter"

**Nguyên nhân**: User model thiếu setter cho properties

**Giải pháp**: ✅ ĐÃ SỬA trong `backend/models/user.py`

File đã được cập nhật với đầy đủ getters/setters cho tất cả properties.

---

### Lỗi 2: Không đăng nhập được với tài khoản admin/user1

**Nguyên nhân**: Password hash trong database không đúng

**Giải pháp**:

#### Bước 1: Xóa users cũ trong Neo4j

Mở Neo4j Browser và chạy:

```cypher
// Xóa tất cả users cũ
MATCH (u:User) DETACH DELETE u;
```

#### Bước 2: Tạo lại users với hash đúng

Chạy lại file `database/user_schema.cypher` trong Neo4j Browser, HOẶC chạy trực tiếp:

```cypher
// Tạo admin - password: admin123
CREATE (admin:User {
  username: 'admin',
  email: 'admin@vanhoc.vn',
  password_hash: '$2b$12$6vKGgoQ7K6X3PqL5iP8xqO5jJ.XFzMZQkN8r8YvP7nGCZJCXKF5Zy',
  full_name: 'Quản trị viên',
  role: 'admin',
  is_active: true,
  created_at: datetime()
});

// Tạo user1 - password: user123
CREATE (user1:User {
  username: 'user1',
  email: 'user1@example.com',
  password_hash: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeWY5eRZ7K.6MI.K2',
  full_name: 'Nguyễn Văn A',
  role: 'user',
  is_active: true,
  created_at: datetime()
});
```

#### Bước 3: Verify users đã tạo

```cypher
MATCH (u:User) RETURN u;
```

Kết quả phải có 2 users: admin và user1

---

### Lỗi 3: "Lỗi server" khi đăng ký

**Checklist**:

1. ✅ Đã cài bcrypt chưa?
   ```bash
   pip install bcrypt==4.1.2
   ```

2. ✅ Đã import user_schema.cypher chưa?
   - Phải có constraints: `user_email`, `user_username`

3. ✅ Neo4j đang chạy?
   - Kiểm tra kết nối tại http://localhost:7474

4. ✅ File .env có SECRET_KEY chưa?
   ```env
   SECRET_KEY=your-secret-key-here
   SESSION_TYPE=filesystem
   ```

---

## 🧪 TESTING ĐĂNG NHẬP

### Cách ĐÚNG để tạo users trong Neo4j:

**QUAN TRỌNG**: Phải chạy TỪNG câu lệnh một, KHÔNG chạy cả file!

#### Bước 1: Mở Neo4j Browser
- Truy cập: http://localhost:7474
- Đăng nhập Neo4j

#### Bước 2: Xóa users cũ
Copy và chạy câu lệnh này:
```cypher
MATCH (u:User) DETACH DELETE u;
```

#### Bước 3: Tạo admin
Copy và chạy câu lệnh này:
```cypher
CREATE (admin:User {
  username: 'admin',
  email: 'admin@vanhoc.vn',
  password_hash: '$2b$12$6vKGgoQ7K6X3PqL5iP8xqO5jJ.XFzMZQkN8r8YvP7nGCZJCXKF5Zy',
  full_name: 'Quản trị viên',
  role: 'admin',
  is_active: true,
  created_at: datetime()
})
RETURN admin;
```

Phải thấy kết quả: 1 node User được tạo

#### Bước 4: Tạo user thường
Copy và chạy câu lệnh này:
```cypher
CREATE (user1:User {
  username: 'user1',
  email: 'user1@example.com',
  password_hash: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeWY5eRZ7K.6MI.K2',
  full_name: 'Nguyễn Văn A',
  role: 'user',
  is_active: true,
  created_at: datetime()
})
RETURN user1;
```

Phải thấy kết quả: 1 node User được tạo

#### Bước 5: Kiểm tra
Copy và chạy:
```cypher
MATCH (u:User) RETURN u;
```

Phải thấy 2 users: admin và user1

---

### HOẶC dùng file có sẵn:

Mở file `database/user_setup_step_by_step.cypher` và làm theo hướng dẫn trong đó.

---

### Test bằng cURL:

```bash
# Test đăng ký
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@test.com",
    "password": "test123",
    "full_name": "Test User"
  }'

# Test đăng nhập admin
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Check session
curl http://localhost:5000/api/auth/check -b cookies.txt
```

---

## 🔐 TẠO PASSWORD HASH MỚI

### Cách 1: Dùng script có sẵn

```bash
cd backend
python utils/hash_password.py
```

Script sẽ in ra password hash cho admin và user.

### Cách 2: Dùng Python interactive

```python
import bcrypt

password = "your-password-here"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
print(hashed.decode('utf-8'))
```

### Cách 3: Thay đổi password trong code

Sửa trong `database/user_schema.cypher`:

```cypher
CREATE (admin:User {
  username: 'admin',
  email: 'admin@vanhoc.vn',
  password_hash: 'PASTE-YOUR-HASH-HERE',
  ...
});
```

---

## 📋 CHECKLIST HOÀN CHỈNH

Trước khi test, đảm bảo:

- [ ] Neo4j đang chạy (http://localhost:7474)
- [ ] Đã cài đặt bcrypt: `pip install bcrypt`
- [ ] Đã cài đặt Flask-Login: `pip install Flask-Login`
- [ ] Đã import `user_schema.cypher` vào Neo4j
- [ ] File `.env` có SECRET_KEY
- [ ] File `config.py` đã có SESSION_TYPE
- [ ] User model đã có setters (file mới)
- [ ] Flask app đã restart

---

## 🐛 DEBUG MODE

### Bật debug logging:

Thêm vào đầu `app.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Kiểm tra session:

Thêm vào route:

```python
from flask import session

@app.route('/debug/session')
def debug_session():
    return {
        'session': dict(session),
        'user_authenticated': current_user.is_authenticated if current_user else False
    }
```

### Kiểm tra database:

```cypher
// Xem tất cả users
MATCH (u:User) RETURN u;

// Xem user cụ thể
MATCH (u:User {username: 'admin'}) RETURN u;

// Xem constraints
CALL db.constraints();

// Xem indexes
CALL db.indexes();
```

---

## ✅ FLOW ĐÚNG

### Đăng ký:
1. User nhập thông tin → POST /api/auth/register
2. Backend hash password bằng bcrypt
3. Lưu vào Neo4j với password_hash
4. Return success

### Đăng nhập:
1. User nhập username/password → POST /api/auth/login
2. Backend tìm user trong Neo4j
3. Verify password bằng bcrypt.checkpw()
4. Nếu đúng → Tạo session với Flask-Login
5. Return user info

### Kiểm tra auth:
1. Browser gửi request với cookie
2. Flask-Login load user từ session
3. Check current_user.is_authenticated
4. Return auth status

---

## 🆘 NẾU VẪN LỖI

1. **Xóa tất cả và làm lại**:
   ```cypher
   // Xóa hết users
   MATCH (u:User) DETACH DELETE u;
   
   // Xóa constraints
   DROP CONSTRAINT user_email IF EXISTS;
   DROP CONSTRAINT user_username IF EXISTS;
   ```

2. **Chạy lại từ đầu**:
   - Import `user_schema.cypher`
   - Restart Flask app
   - Clear browser cookies
   - Test lại

3. **Kiểm tra logs**:
   ```bash
   # Terminal chạy Flask sẽ show errors
   # Xem kỹ stack trace
   ```

4. **Test bcrypt riêng**:
   ```python
   import bcrypt
   
   # Test basic
   pw = b"admin123"
   hashed = bcrypt.hashpw(pw, bcrypt.gensalt())
   print(bcrypt.checkpw(pw, hashed))  # Must be True
   ```

---

## 📞 LIÊN HỆ

Nếu vẫn gặp lỗi, gửi:
1. Full error message
2. Screenshot Neo4j (MATCH (u:User) RETURN u)
3. File .env (che SECRET_KEY)
4. Version Python, bcrypt, Flask-Login

---

**Good luck! 🍀**
