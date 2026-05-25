"""
Script để generate bcrypt password hash
Dùng để tạo password hash cho admin và users
"""

import bcrypt
import sys

def hash_password(password):
    """Hash password bằng bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed):
    """Verify password với hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

if __name__ == '__main__':
    print("=== Bcrypt Password Hash Generator ===\n")
    
    # Generate hashes cho passwords mặc định
    admin_password = "admin123"
    user_password = "user123"
    
    admin_hash = hash_password(admin_password)
    user_hash = hash_password(user_password)
    
    print(f"Admin password: {admin_password}")
    print(f"Admin hash: {admin_hash}\n")
    
    print(f"User password: {user_password}")
    print(f"User hash: {user_hash}\n")
    
    # Verify
    print("=== Verification ===")
    print(f"Admin verify: {verify_password(admin_password, admin_hash)}")
    print(f"User verify: {verify_password(user_password, user_hash)}")
    
    print("\n=== Cypher Query ===")
    print(f"""
// Tạo admin
CREATE (admin:User {{
  username: 'admin',
  email: 'admin@vanhoc.vn',
  password_hash: '{admin_hash}',
  full_name: 'Quản trị viên',
  role: 'admin',
  is_active: true,
  created_at: datetime()
}});

// Tạo user
CREATE (user1:User {{
  username: 'user1',
  email: 'user1@example.com',
  password_hash: '{user_hash}',
  full_name: 'Nguyễn Văn A',
  role: 'user',
  is_active: true,
  created_at: datetime()
}});
""")
    
    # Cho phép user nhập password tùy ý
    if len(sys.argv) > 1:
        custom_password = sys.argv[1]
        custom_hash = hash_password(custom_password)
        print(f"\n=== Custom Password ===")
        print(f"Password: {custom_password}")
        print(f"Hash: {custom_hash}")
