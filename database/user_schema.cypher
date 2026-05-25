// ===== USER AUTHENTICATION SCHEMA =====

// Tạo constraints cho User
CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT user_username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE;

// Tạo index
CREATE INDEX user_role IF NOT EXISTS FOR (u:User) ON (u.role);
CREATE INDEX user_created_at IF NOT EXISTS FOR (u:User) ON (u.created_at);

// ===== NODE STRUCTURE =====

// Node: User
// Properties:
//   - username: String (unique, required)
//   - email: String (unique, required)
//   - password_hash: String (required) - Mật khẩu đã hash
//   - full_name: String
//   - role: String (user, admin) - default: user
//   - is_active: Boolean - default: true
//   - created_at: DateTime
//   - last_login: DateTime

// ===== SAMPLE DATA - ADMIN VÀ USER MẪU =====

// Xóa users cũ nếu có (để tránh duplicate)
MATCH (u:User) WHERE u.username IN ['admin', 'user1'] 
DETACH DELETE u;

// Tạo admin mặc định
// Password: admin123
// Hash được tạo bằng bcrypt với rounds=12
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

// Tạo user thường mẫu
// Password: user123
// Hash được tạo bằng bcrypt với rounds=12
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

// ===== RELATIONSHIPS =====

// User có thể thích tác phẩm
// (User)-[:THICH]->(TacPham)
// Properties: created_at

// User có thể đánh giá tác phẩm
// (User)-[:DANH_GIA]->(TacPham)
// Properties: rating (1-5), comment, created_at

// User tạo/chỉnh sửa nội dung (cho audit trail)
// (User)-[:TAO_NOI_DUNG {created_at}]->(TacGia|TacPham)
// (User)-[:CHINH_SUA {updated_at, changes}]->(TacGia|TacPham)

RETURN "User schema created successfully!";
