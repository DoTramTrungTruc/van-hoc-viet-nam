# 🎉 TÍNH NĂNG MỚI: USER PROFILE & AVATAR

## ✨ CÁC TÍNH NĂNG ĐÃ THÊM

### 1. 👤 TRANG HỒ SƠ CÁ NHÂN (`/profile`)

**Tính năng:**
- ✅ Hiển thị avatar với chữ cái đầu của tên
- ✅ Thông tin cá nhân đầy đủ (username, email, role)
- ✅ Đổi mật khẩu ngay trên trang profile
- ✅ Thống kê hoạt động (sẵn sàng mở rộng)
- ✅ Nút đăng xuất

**Truy cập:**
- URL: http://localhost:5000/profile
- Cần đăng nhập mới vào được
- Tự động redirect về /login nếu chưa đăng nhập

---

### 2. 🔘 AVATAR TRÊN NAVBAR

**Vị trí:** Góc phải navbar trên tất cả các trang

**Khi CHƯA đăng nhập:**
- Hiển thị nút "Đăng nhập" và "Đăng ký"

**Khi ĐÃ đăng nhập:**
- Hiển thị avatar tròn với chữ cái đầu của tên
- Click vào avatar → hiện dropdown menu:
  - 👤 Hồ sơ cá nhân
  - ⚙️ Quản trị (chỉ admin)
  - 🚪 Đăng xuất

---

### 3. 🚪 ĐĂNG XUẤT

**Cách 1:** Click avatar → Chọn "Đăng xuất"
**Cách 2:** Vào /profile → Click nút "Đăng xuất"

**Flow:**
1. Click đăng xuất
2. Confirm "Bạn có chắc muốn đăng xuất?"
3. Gọi API /api/auth/logout
4. Redirect về trang /login

---

## 📁 CÁC FILE MỚI/SỬA ĐỔI

### Frontend

**Mới:**
- `frontend/templates/profile.html` - Trang hồ sơ cá nhân
- `frontend/static/js/auth.js` - Xử lý UI authentication

**Đã sửa:**
- `frontend/templates/index.html` - Thêm auth.js
- `frontend/templates/tac_gia.html` - Thêm auth.js
- `frontend/templates/tac_pham.html` - Thêm auth.js
- `frontend/templates/admin.html` - Thêm auth.js

### Backend

**Không thay đổi** - Các API đã có sẵn:
- GET `/api/auth/me` - Lấy thông tin user hiện tại
- GET `/api/auth/check` - Kiểm tra đăng nhập
- POST `/api/auth/logout` - Đăng xuất
- POST `/api/auth/change-password` - Đổi mật khẩu

---

## 🎨 GIAO DIỆN

### Avatar
```
┌─────┐
│  A  │  ← Chữ cái đầu tên (hoặc username)
└─────┘
```

**Màu sắc:**
- Background: Trắng
- Text: Xanh dương (var(--secondary-color))
- Border: Viền mờ trắng

**Hiệu ứng:**
- Hover: Scale 1.1 + shadow
- Click: Toggle dropdown

### Dropdown Menu

```
┌────────────────────────────┐
│  [A]  Nguyễn Văn A         │ ← Header (gradient)
│       admin@vanhoc.vn      │
├────────────────────────────┤
│  👤  Hồ sơ cá nhân        │
│  ⚙️  Quản trị (admin)      │
├────────────────────────────┤
│  🚪  Đăng xuất            │ ← Màu đỏ
└────────────────────────────┘
```

---

## 🚀 HƯỚNG DẪN SỬ DỤNG

### User thường:

1. **Đăng nhập** tại /login
2. Thấy **avatar** góc phải navbar
3. **Click avatar** → Dropdown hiện ra
4. Chọn **"Hồ sơ cá nhân"** → Vào /profile
5. Trong profile có thể:
   - Xem thông tin
   - Đổi mật khẩu
   - Đăng xuất

### Admin:

1. Đăng nhập với tài khoản admin
2. Avatar góc phải + menu "⚙️ Quản trị"
3. Click avatar → Dropdown có:
   - Hồ sơ cá nhân
   - **Quản trị** (thêm so với user)
   - Đăng xuất

---

## 🔧 CUSTOMIZATION

### Thay đổi màu avatar:

File: `frontend/static/js/auth.js`

```javascript
// Tìm phần này và thay đổi style
.user-avatar {
    background: white;           // ← Đổi màu background
    color: var(--secondary-color); // ← Đổi màu chữ
}
```

### Thay đổi avatar thành hình ảnh:

File: `frontend/templates/profile.html`

```javascript
// Thay vì chữ cái, dùng <img>
document.getElementById('userAvatar').innerHTML = 
    `<img src="${user.avatar_url}" alt="Avatar">`;
```

### Thêm trường avatar_url vào User:

1. Cập nhật user_schema.cypher:
```cypher
CREATE (u:User {
    ...
    avatar_url: 'https://...'
})
```

2. Cập nhật auth.js để hiển thị ảnh thay vì chữ

---

## 🎯 TESTING

### Test Flow đăng nhập → Profile:

```bash
# 1. Đăng nhập
Open: http://localhost:5000/login
Login: admin / admin123

# 2. Kiểm tra navbar
- Phải thấy avatar "A" góc phải
- Click vào → dropdown hiện ra

# 3. Vào profile
Click "Hồ sơ cá nhân"
URL: http://localhost:5000/profile

# 4. Test đổi mật khẩu
Nhập:
- Mật khẩu cũ: admin123
- Mật khẩu mới: newpass123
- Xác nhận: newpass123
Submit → Thành công

# 5. Test đăng xuất
Click "Đăng xuất" → Confirm → Redirect về /login
```

### Test bằng cURL:

```bash
# 1. Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"admin","password":"admin123"}'

# 2. Get user info
curl http://localhost:5000/api/auth/me -b cookies.txt

# 3. Logout
curl -X POST http://localhost:5000/api/auth/logout -b cookies.txt
```

---

## 📊 LUỒNG HOẠT ĐỘNG

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ 1. Load page
       ▼
┌─────────────────┐
│   auth.js       │
│  - checkAuth()  │
└──────┬──────────┘
       │
       │ 2. GET /api/auth/check
       ▼
┌─────────────────┐
│   Flask API     │
│  - current_user │
└──────┬──────────┘
       │
       │ 3. Return user data
       ▼
┌─────────────────┐
│   auth.js       │
│ - updateNavbar()│
└──────┬──────────┘
       │
       │ 4. Render avatar/menu
       ▼
┌─────────────────┐
│   Navbar UI     │
│  [Avatar] [▼]   │
└─────────────────┘
```

---

## ⚠️ LƯU Ý

1. **auth.js tự động load** trên mọi trang có include nó
2. **Không cần code gì thêm** - chỉ thêm `<script src="/static/js/auth.js"></script>`
3. **Avatar tự động hiện** khi user đăng nhập
4. **Dropdown tự đóng** khi click ra ngoài
5. **Responsive** - hoạt động tốt trên mobile

---

## 🐛 TROUBLESHOOTING

### Avatar không hiện:

**Nguyên nhân:** Chưa thêm auth.js vào trang

**Giải pháp:**
```html
<script src="/static/js/auth.js"></script>
```

### Dropdown không mở:

**Nguyên nhân:** JavaScript error

**Giải pháp:** Mở Console (F12) và xem lỗi

### Profile redirect về login:

**Nguyên nhân:** Chưa đăng nhập hoặc session hết hạn

**Giải pháp:** Đăng nhập lại

### Đăng xuất không hoạt động:

**Nguyên nhân:** API endpoint lỗi

**Giải pháp:**
```bash
# Check endpoint
curl -X POST http://localhost:5000/api/auth/logout \
  -b cookies.txt -v
```

---

## 🎓 KẾT LUẬN

Hệ thống giờ có:
- ✅ Avatar user trên navbar
- ✅ Dropdown menu với profile & logout
- ✅ Trang profile đầy đủ chức năng
- ✅ Đổi mật khẩu trong profile
- ✅ Phân quyền User/Admin rõ ràng
- ✅ UX mượt mà, chuyên nghiệp

**Hãy test và enjoy! 🎉**
