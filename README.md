# HỆ THỐNG HỎI ĐÁP & TRA CỨU VĂN HỌC VIỆT NAM

Đồ án tốt nghiệp K64 - Xây dựng hệ thống hỏi đáp về các tác phẩm văn học Việt Nam sử dụng Knowledge Graph và Neo4j.

## 📚 Giới thiệu

Hệ thống cung cấp nền tảng tra cứu thông tin về:
- Tác giả văn học Việt Nam
- Tác phẩm văn học tiêu biểu
- Nhân vật trong các tác phẩm
- Mối quan hệ giữa các thực thể văn học

Dữ liệu được tổ chức dưới dạng Knowledge Graph sử dụng Neo4j, cho phép truy vấn phức tạp và visualization trực quan.

## 🏗️ Kiến trúc hệ thống

### Technology Stack
- **Backend**: Python Flask
- **Database**: Neo4j Graph Database
- **Frontend**: HTML, CSS, JavaScript
- **Visualization**: Vis.js

### Cấu trúc thư mục
```
van-hoc-kg/
├── backend/
│   ├── app.py              # Flask application chính
│   ├── config.py           # Cấu hình
│   ├── routes/             # API endpoints
│   │   ├── tac_gia.py
│   │   ├── tac_pham.py
│   │   └── general.py
│   ├── services/           # Business logic
│   │   └── neo4j_service.py
│   └── utils/
├── database/
│   ├── schema.cypher       # Định nghĩa schema
│   ├── sample_data.cypher  # Dữ liệu mẫu
│   └── queries.cypher      # Thư viện truy vấn
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/          # HTML templates
├── docs/                   # Tài liệu
└── requirements.txt        # Dependencies
```

## 🚀 Cài đặt

### 1. Cài đặt Neo4j

#### Trên Windows/Mac/Linux:
1. Tải Neo4j Desktop từ: https://neo4j.com/download/
2. Cài đặt và khởi động Neo4j
3. Tạo database mới với tên `van-hoc`
4. Lưu username và password (mặc định: neo4j/password)

#### Hoặc dùng Docker:
```bash
docker run \
    --name neo4j-vanhoc \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    -v $HOME/neo4j/data:/data \
    neo4j:latest
```

### 2. Cài đặt Python Dependencies

```bash
# Tạo virtual environment (khuyến nghị)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt packages
pip install -r requirements.txt
```

### 3. Cấu hình

Tạo file `.env` trong thư mục gốc:

```env
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=van-hoc

# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 4. Import dữ liệu vào Neo4j

#### Cách 1: Dùng Neo4j Browser
1. Mở Neo4j Browser tại http://localhost:7474
2. Đăng nhập
3. Mở file `database/schema.cypher` và chạy các câu lệnh
4. Mở file `database/sample_data.cypher` và chạy để import dữ liệu mẫu

#### Cách 2: Dùng cypher-shell
```bash
# Chạy schema
cat database/schema.cypher | cypher-shell -u neo4j -p password

# Import dữ liệu
cat database/sample_data.cypher | cypher-shell -u neo4j -p password
```

### 5. Chạy ứng dụng

```bash
# Chuyển vào thư mục backend
cd backend

# Chạy Flask server
python app.py
```

Truy cập: http://localhost:5000

## 📖 Sử dụng

### 1. Trang chủ
- Xem thống kê tổng quan
- Tìm kiếm nhanh tác phẩm, tác giả
- Duyệt theo thể loại

### 2. Danh sách Tác giả
- Xem danh sách tác giả
- Tìm kiếm tác giả
- Xem chi tiết tác giả và tác phẩm của họ

### 3. Danh sách Tác phẩm
- Xem tất cả tác phẩm
- Lọc theo thể loại, chủ đề
- Tìm kiếm tác phẩm

### 4. Chi tiết Tác phẩm
- Thông tin đầy đủ về tác phẩm
- Danh sách nhân vật
- Visualization Knowledge Graph

### 5. Trang Quản trị
- Thêm/sửa/xóa tác giả
- Thêm/sửa/xóa tác phẩm
- Quản lý nhân vật

## 🔍 API Endpoints

### Tác giả
```
GET  /api/tac-gia/                    # Lấy danh sách tác giả
GET  /api/tac-gia/search?q=keyword    # Tìm kiếm tác giả
GET  /api/tac-gia/<ten>                # Chi tiết tác giả
POST /api/tac-gia/create               # Tạo tác giả mới (Admin)
```

### Tác phẩm
```
GET    /api/tac-pham/                      # Lấy danh sách tác phẩm
GET    /api/tac-pham/search?q=keyword      # Tìm kiếm tác phẩm
GET    /api/tac-pham/<ten>                 # Chi tiết tác phẩm
GET    /api/tac-pham/the-loai/<the_loai>   # Lọc theo thể loại
GET    /api/tac-pham/chu-de/<chu_de>       # Lọc theo chủ đề
POST   /api/tac-pham/create                # Tạo tác phẩm (Admin)
PUT    /api/tac-pham/<ten>/update          # Cập nhật (Admin)
DELETE /api/tac-pham/<ten>/delete          # Xóa (Admin)
```

### Thống kê & Danh mục
```
GET /api/the-loai         # Danh sách thể loại
GET /api/chu-de           # Danh sách chủ đề
GET /api/statistics       # Thống kê hệ thống
```

## 💡 Cypher Query Examples

### Tìm tác phẩm của tác giả
```cypher
MATCH (t:TacGia {ten: "Nguyễn Du"})-[:SANG_TAC]->(tp:TacPham)
RETURN tp.ten AS tac_pham
```

### Tìm nhân vật trong tác phẩm
```cypher
MATCH (tp:TacPham {ten: "Truyện Kiều"})-[:CO_NHAN_VAT]->(nv:NhanVat)
RETURN nv.ten, nv.vai_tro, nv.tinh_cach
```

### Tìm tác phẩm cùng chủ đề
```cypher
MATCH (tp1:TacPham {ten: "Truyện Kiều"})-[:NOI_VE]->(cd:ChuDe)<-[:NOI_VE]-(tp2:TacPham)
WHERE tp1 <> tp2
RETURN DISTINCT tp2.ten AS tac_pham_lien_quan
```

### Tìm mối quan hệ giữa nhân vật
```cypher
MATCH (nv1:NhanVat)-[r:QUAN_HE]->(nv2:NhanVat)
WHERE nv1.ten = "Thúy Kiều"
RETURN nv1.ten, r.loai, nv2.ten
```

## 📊 Knowledge Graph Schema

### Nodes (Nút)
- **TacGia**: Tác giả
- **TacPham**: Tác phẩm
- **NhanVat**: Nhân vật
- **TheLoai**: Thể loại
- **ChuDe**: Chủ đề
- **BiPhap**: Bì pháp nghệ thuật
- **ThoiKy**: Thời kỳ lịch sử

### Relationships (Quan hệ)
- (TacGia)-[:SANG_TAC]->(TacPham)
- (TacPham)-[:CO_NHAN_VAT]->(NhanVat)
- (TacPham)-[:THUOC_THE_LOAI]->(TheLoai)
- (TacPham)-[:NOI_VE]->(ChuDe)
- (TacPham)-[:SU_DUNG]->(BiPhap)
- (NhanVat)-[:QUAN_HE]->(NhanVat)

## 🔧 Development

### Thêm dữ liệu mới

1. **Thêm tác giả**:
```cypher
CREATE (t:TacGia {
  ten: "Xuân Diệu",
  nam_sinh: 1916,
  nam_mat: 1985,
  que_quan: "Nam Định",
  truong_phai: "Thơ mới",
  tieu_su: "..."
})
```

2. **Thêm tác phẩm**:
```cypher
MATCH (t:TacGia {ten: "Xuân Diệu"})
CREATE (tp:TacPham {
  ten: "Vội vàng",
  nam_sang_tac: 1936,
  noi_dung_tom_tat: "...",
  y_nghia: "..."
})
CREATE (t)-[:SANG_TAC]->(tp)
```

### Testing

```bash
# Test API endpoints
curl http://localhost:5000/api/health
curl http://localhost:5000/api/statistics
curl http://localhost:5000/api/tac-pham/Truyện%20Kiều
```

### Backup Database

```bash
# Backup
neo4j-admin dump --database=van-hoc --to=/backup/van-hoc.dump

# Restore
neo4j-admin load --from=/backup/van-hoc.dump --database=van-hoc --force
```

## 📝 Tài liệu tham khảo

1. Neo4j Documentation: https://neo4j.com/docs/
2. Flask Documentation: https://flask.palletsprojects.com/
3. Vis.js Network: https://visjs.github.io/vis-network/docs/network/
4. Cypher Query Language: https://neo4j.com/docs/cypher-manual/

## 👨‍💻 Tác giả

Đồ án tốt nghiệp K64
- Sinh viên: [Tên của bạn]
- MSSV: [Mã số sinh viên]
- Giảng viên hướng dẫn: [Tên giảng viên]

## 📄 License

Dự án này được phát triển cho mục đích học tập và nghiên cứu.

## 🤝 Đóng góp

Mọi đóng góp, ý kiến đều được hoan nghênh. Vui lòng tạo issue hoặc pull request.

## 📮 Liên hệ

- Email: [your-email]
- GitHub: [your-github]
