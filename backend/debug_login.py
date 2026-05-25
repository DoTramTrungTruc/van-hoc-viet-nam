"""
Script debug login
Test toàn bộ flow đăng nhập
"""

import sys
sys.path.append('.')

from services.neo4j_service import Neo4jService
from services.auth_service import AuthService
from config import Config
import bcrypt

print("=== DEBUG LOGIN FLOW ===\n")

# 1. Kết nối Neo4j
print("1. Kết nối Neo4j...")
try:
    neo4j_service = Neo4jService(
        uri=Config.NEO4J_URI,
        user=Config.NEO4J_USER,
        password=Config.NEO4J_PASSWORD,
        database=Config.NEO4J_DATABASE
    )
    print("   ✓ Kết nối thành công!\n")
except Exception as e:
    print(f"   ✗ Lỗi kết nối: {e}\n")
    sys.exit(1)

# 2. Khởi tạo AuthService
print("2. Khởi tạo AuthService...")
auth_service = AuthService(neo4j_service)
print("   ✓ OK\n")

# 3. Kiểm tra users trong database
print("3. Kiểm tra users trong database...")
query = "MATCH (u:User) RETURN u.username, u.email, u.role, u.password_hash"
try:
    users = neo4j_service.execute_query(query)
    print(f"   Tìm thấy {len(users)} users:")
    for user in users:
        print(f"   - {user['u.username']} ({user['u.role']}) - {user['u.email']}")
        print(f"     Hash: {user['u.password_hash'][:50]}...")
    print()
except Exception as e:
    print(f"   ✗ Lỗi: {e}\n")

# 4. Test verify password thủ công
print("4. Test verify password thủ công...")
test_cases = [
    ("admin", "admin123"),
    ("admin", "wrong_password"),
    ("user1", "user123"),
]

for username, password in test_cases:
    print(f"\n   Test: {username} / {password}")
    
    # Lấy password hash từ database
    query = "MATCH (u:User {username: $username}) RETURN u.password_hash as hash"
    result = neo4j_service.execute_query(query, {"username": username})
    
    if not result:
        print(f"   ✗ User {username} không tồn tại!")
        continue
    
    stored_hash = result[0]['hash']
    print(f"   Hash: {stored_hash[:50]}...")
    
    # Verify
    try:
        is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        print(f"   {'✓ ĐÚNG' if is_valid else '✗ SAI'}")
    except Exception as e:
        print(f"   ✗ Lỗi verify: {e}")

# 5. Test AuthService.login()
print("\n" + "="*50)
print("5. Test AuthService.login()...")
print("="*50)

test_logins = [
    ("admin", "admin123", True),
    ("admin", "wrong", False),
    ("user1", "user123", True),
]

for username, password, should_success in test_logins:
    print(f"\n   Login: {username} / {password}")
    try:
        user = auth_service.login(username, password)
        if user:
            print(f"   ✓ THÀNH CÔNG!")
            print(f"   User: {user.username} ({user.role})")
        else:
            print(f"   ✗ THẤT BẠI (trả về None)")
            if should_success:
                print(f"   ⚠️ LỖI: Lẽ ra phải thành công!")
    except Exception as e:
        print(f"   ✗ Exception: {e}")

# 6. Recommendations
print("\n" + "="*50)
print("6. KẾT LUẬN & KHUYẾN NGHỊ")
print("="*50 + "\n")

# Kiểm tra lại database
query = "MATCH (u:User {username: 'admin'}) RETURN u"
admin_in_db = neo4j_service.execute_query(query)

if not admin_in_db:
    print("⚠️ NGUYÊN NHÂN: Không tìm thấy user 'admin' trong database!")
    print("\nGIẢI PHÁP:")
    print("1. Chạy: python backend/test_password.py")
    print("2. Copy Cypher query từ output")
    print("3. Chạy trong Neo4j Browser")
    print("4. Test lại đăng nhập")
else:
    print("✓ User admin tồn tại trong database")
    
    # Kiểm tra hash
    admin_data = dict(admin_in_db[0]['u'])
    stored_hash = admin_data.get('password_hash', '')
    
    print(f"\nKiểm tra password hash của admin:")
    print(f"Hash: {stored_hash}")
    
    try:
        is_valid = bcrypt.checkpw(b"admin123", stored_hash.encode('utf-8'))
        if is_valid:
            print("✓ Password hash ĐÚNG!")
            print("\n⚠️ Nếu vẫn không login được, kiểm tra:")
            print("  1. File .env có SECRET_KEY chưa?")
            print("  2. Flask app đã restart chưa?")
            print("  3. Browser cookies đã clear chưa?")
            print("  4. Endpoint /api/auth/login có hoạt động không?")
        else:
            print("✗ Password hash SAI!")
            print("\nGIẢI PHÁP: Chạy lại test_password.py và cập nhật hash")
    except Exception as e:
        print(f"✗ Lỗi khi verify: {e}")

print("\n" + "="*50)
print("DEBUG HOÀN TẤT!")
print("="*50)
