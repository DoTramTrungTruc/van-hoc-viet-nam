"""
Script debug để test password hash
Chạy để kiểm tra password có đúng không
"""

import bcrypt

print("=== TEST PASSWORD HASH ===\n")

# Password thực tế
admin_password = "admin123"
user_password = "user123"

# Hash hiện tại trong database
admin_hash_current = "$2b$12$6vKGgoQ7K6X3PqL5iP8xqO5jJ.XFzMZQkN8r8YvP7nGCZJCXKF5Zy"
user_hash_current = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeWY5eRZ7K.6MI.K2"

# Test verify
print("1. Test Admin Password:")
print(f"   Password: {admin_password}")
print(f"   Hash: {admin_hash_current}")
try:
    result = bcrypt.checkpw(admin_password.encode('utf-8'), admin_hash_current.encode('utf-8'))
    print(f"   ✓ Verify Result: {result}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n2. Test User Password:")
print(f"   Password: {user_password}")
print(f"   Hash: {user_hash_current}")
try:
    result = bcrypt.checkpw(user_password.encode('utf-8'), user_hash_current.encode('utf-8'))
    print(f"   ✓ Verify Result: {result}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Tạo hash mới ĐÚNG
print("\n" + "="*50)
print("3. TẠO HASH MỚI (100% ĐÚNG):")
print("="*50 + "\n")

admin_new_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt(rounds=12))
user_new_hash = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt(rounds=12))

print(f"Admin (password: {admin_password}):")
print(f"Hash mới: {admin_new_hash.decode('utf-8')}\n")

print(f"User (password: {user_password}):")
print(f"Hash mới: {user_new_hash.decode('utf-8')}\n")

# Verify hash mới
print("="*50)
print("4. VERIFY HASH MỚI:")
print("="*50 + "\n")

admin_verify = bcrypt.checkpw(admin_password.encode('utf-8'), admin_new_hash)
user_verify = bcrypt.checkpw(user_password.encode('utf-8'), user_new_hash)

print(f"Admin verify: {admin_verify} {'✓ OK' if admin_verify else '✗ FAIL'}")
print(f"User verify: {user_verify} {'✓ OK' if user_verify else '✗ FAIL'}")

# Tạo Cypher query
print("\n" + "="*50)
print("5. CYPHER QUERY ĐỂ CẬP NHẬT:")
print("="*50 + "\n")

print(f"""// Xóa users cũ
MATCH (u:User) DETACH DELETE u;

// Tạo admin với hash MỚI
CREATE (admin:User {{
  username: 'admin',
  email: 'admin@vanhoc.vn',
  password_hash: '{admin_new_hash.decode('utf-8')}',
  full_name: 'Quản trị viên',
  role: 'admin',
  is_active: true,
  created_at: datetime()
}})
RETURN admin;

// Tạo user với hash MỚI
CREATE (user1:User {{
  username: 'user1',
  email: 'user1@example.com',
  password_hash: '{user_new_hash.decode('utf-8')}',
  full_name: 'Nguyễn Văn A',
  role: 'user',
  is_active: true,
  created_at: datetime()
}})
RETURN user1;
""")

print("\n" + "="*50)
print("COPY CYPHER QUERY Ở TRÊN VÀ CHẠY TRONG NEO4J!")
print("="*50)
