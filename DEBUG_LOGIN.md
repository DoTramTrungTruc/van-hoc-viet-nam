# 🔍 HƯỚNG DẪN DEBUG LỖI ĐĂNG NHẬP

## ❌ Lỗi: "Username hoặc password không đúng"

Có 3 nguyên nhân chính:
1. Password hash trong database không đúng
2. Username không tồn tại trong database
3. Code verify password có vấn đề

---

## 🛠️ BƯỚC 1: CHẠY SCRIPT DEBUG

### A. Test password hash:

```bash
cd backend
python test_password.py
```

Script này sẽ:
- ✅ Test hash hiện tại có đúng không
- ✅ Tạo hash MỚI 100% đúng
- ✅ In ra Cypher query để cập nhật

**Kết quả mong đợi:**
```
Admin verify: True ✓ OK
User verify: True ✓ OK
```

**Nếu thấy False:** Hash trong database sai!

---

### B. Test toàn bộ login flow:

```bash
cd backend
python debug_login.py
```

Script này sẽ:
- ✅ Kiểm tra kết nối Neo4j
- ✅ Liệt kê users trong database
- ✅ Test verify password từng user
- ✅ Test AuthService.login()
- ✅ Đưa ra khuyến nghị

**Quan sát output để tìm nguyên nhân!**

---

## 🔧 BƯỚC 2: SỬA LỖI

### Trường hợp 1: Hash sai

**Triệu chứng:** Script debug_login.py báo "✗ SAI" khi verify

**Giải pháp:**

1. Chạy `python test_password.py`
2. Copy Cypher query từ output (phần cuối)
3. Mở Neo4j Browser
4. Paste và chạy từng đoạn:

```cypher
// Đoạn 1: Xóa users cũ
MATCH (u:User) DETACH DELETE u;

// Đoạn 2: Tạo admin (copy hash từ output)
CREATE (admin:User {
  username: 'admin',
  email: 'admin@vanhoc.vn',
  password_hash: 'HASH_TỪ_OUTPUT_test_password.py',
  full_name: 'Quản trị viên',
  role: 'admin',
  is_active: true,
  created_at: datetime()
})
RETURN admin;

// Đoạn 3: Tạo user1 (copy hash từ output)
CREATE (user1:User {
  username: 'user1',
  email: 'user1@example.com',
  password_hash: 'HASH_TỪ_OUTPUT_test_password.py',
  full_name: 'Nguyễn Văn A',
  role: 'user',
  is_active: true,
  created_at: datetime()
})
RETURN user1;
```

4. Restart Flask app
5. Test lại login

---

### Trường hợp 2: User không tồn tại

**Triệu chứng:** debug_login.py báo "Tìm thấy 0 users"

**Giải pháp:**

Chưa import user_schema.cypher! Làm lại từ đầu:

```bash
# Terminal 1: Chạy test_password.py
cd backend
python test_password.py

# Terminal 2: Neo4j Browser
# Copy query từ terminal 1 và chạy
```

---

### Trường hợp 3: Code có vấn đề

**Triệu chứng:** Hash đúng, user tồn tại, nhưng vẫn không login được

**Checklist:**

- [ ] File .env có SECRET_KEY?
- [ ] Flask app đã restart?
- [ ] Browser cookies đã clear?
- [ ] Endpoint /api/auth/login có chạy không?

**Test endpoint:**

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -v
```

Phải trả về: `"success": true`

---

## 📋 CHECKLIST ĐẦY ĐỦ

### 1. Chuẩn bị:
- [ ] Neo4j đang chạy (http://localhost:7474)
- [ ] Flask app đang chạy (http://localhost:5000)
- [ ] Đã cài bcrypt: `pip install bcrypt`

### 2. Kiểm tra Database:
```cypher
// Trong Neo4j Browser
MATCH (u:User) RETURN u;
```
- [ ] Có ít nhất 1 user
- [ ] User có trường `password_hash`

### 3. Chạy Debug:
```bash
cd backend
python test_password.py
python debug_login.py
```
- [ ] Không có lỗi Exception
- [ ] Verify password trả về True

### 4. Cập nhật Hash (nếu cần):
- [ ] Copy Cypher query từ test_password.py
- [ ] Chạy trong Neo4j Browser
- [ ] Verify có 2 users (admin và user1)

### 5. Restart & Test:
- [ ] Restart Flask app (Ctrl+C, python app.py)
- [ ] Clear browser cookies
- [ ] Test login tại http://localhost:5000/login

---

## 🎯 QUICK FIX (Nếu vội)

**Làm theo đúng 5 bước này:**

```bash
# 1. Vào backend folder
cd backend

# 2. Tạo hash mới
python test_password.py

# 3. Copy output, mở Neo4j Browser

# 4. Xóa users cũ
MATCH (u:User) DETACH DELETE u;

# 5. Paste và chạy 2 câu CREATE từ output test_password.py

# 6. Restart Flask
# Ctrl+C
python app.py

# 7. Test login
```

---

## 🆘 NẾU VẪN KHÔNG ĐƯỢC

**Gửi cho tôi:**

1. Output của `python debug_login.py`
2. Output của `python test_password.py`
3. Screenshot Neo4j Browser: `MATCH (u:User) RETURN u`
4. Error log từ Flask terminal

---

## ✅ DẤU HIỆU THÀNH CÔNG

Khi chạy `debug_login.py`, phải thấy:

```
✓ Kết nối thành công!
✓ Tìm thấy 2 users
✓ ĐÚNG (cho admin/admin123)
✓ ĐÚNG (cho user1/user123)
✓ THÀNH CÔNG! User: admin (admin)
✓ Password hash ĐÚNG!
```

Khi đó login sẽ hoạt động!

---

**Hãy chạy debug_login.py và cho tôi biết kết quả!** 🔍
