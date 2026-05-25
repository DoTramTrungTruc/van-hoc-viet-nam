// ========================================
// HƯỚNG DẪN TẠO USERS TRONG NEO4J
// Copy từng đoạn và chạy lần lượt
// ========================================

// ===== BƯỚC 1: XÓA USERS CŨ (nếu có) =====
// Copy và chạy đoạn này trước
MATCH (u:User) 
DETACH DELETE u;

// Kết quả: Deleted X nodes


// ===== BƯỚC 2: TẠO ADMIN =====
// Copy và chạy đoạn này
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

// Kết quả: Phải thấy 1 node User với username='admin'


// ===== BƯỚC 3: TẠO USER THƯỜNG =====
// Copy và chạy đoạn này
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

// Kết quả: Phải thấy 1 node User với username='user1'


// ===== BƯỚC 4: KIỂM TRA =====
// Copy và chạy để xem tất cả users
MATCH (u:User) 
RETURN u.username, u.email, u.role, u.is_active
ORDER BY u.role DESC;

// Kết quả phải có:
// admin     | admin@vanhoc.vn      | admin | true
// user1     | user1@example.com    | user  | true


// ===== BƯỚC 5 (TÙY CHỌN): TEST PASSWORD =====
// Kiểm tra password hash có đúng không
MATCH (u:User {username: 'admin'}) 
RETURN u.username, u.password_hash;

// Password hash của admin phải là:
// $2b$12$6vKGgoQ7K6X3PqL5iP8xqO5jJ.XFzMZQkN8r8YvP7nGCZJCXKF5Zy


// ========================================
// THÔNG TIN ĐĂNG NHẬP
// ========================================

/*
Admin:
  - Username: admin
  - Password: admin123
  - Email: admin@vanhoc.vn

User:
  - Username: user1
  - Password: user123
  - Email: user1@example.com
*/


// ========================================
// NẾU CẦN TẠO USER MỚI
// ========================================

// Template để tạo user mới:
// Thay đổi các giá trị trong {...}

CREATE (newuser:User {
  username: '{USERNAME}',
  email: '{EMAIL}',
  password_hash: '{HASH_FROM_SCRIPT}',
  full_name: '{HO_TEN}',
  role: 'user',
  is_active: true,
  created_at: datetime()
})
RETURN newuser;

// Để tạo password hash, chạy trong terminal:
// cd backend
// python utils/hash_password.py


// ========================================
// XÓA USER CỤ THỂ
// ========================================

// Xóa user theo username
MATCH (u:User {username: 'user_can_xoa'}) 
DETACH DELETE u;


// ========================================
// CẬP NHẬT THÔNG TIN USER
// ========================================

// Đổi role user thành admin
MATCH (u:User {username: 'user1'}) 
SET u.role = 'admin'
RETURN u;

// Đổi email
MATCH (u:User {username: 'admin'}) 
SET u.email = 'newemail@example.com'
RETURN u;

// Khóa user (deactivate)
MATCH (u:User {username: 'user1'}) 
SET u.is_active = false
RETURN u;

// Mở khóa user
MATCH (u:User {username: 'user1'}) 
SET u.is_active = true
RETURN u;
