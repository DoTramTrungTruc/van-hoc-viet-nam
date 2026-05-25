# BÁO CÁO ĐỒ ÁN TỐT NGHIỆP

## XÂY DỰNG HỆ THỐNG HỎI ĐÁP VỀ CÁC TÁC PHẨM VĂN HỌC VIỆT NAM

---

## PHẦN I: TỔNG QUAN VÀ LÝ THUYẾT

### 1. ĐẶT VẤN ĐỀ

#### 1.1. Lý do chọn đề tài
Văn học Việt Nam là một kho tàng tri thức phong phú với hàng nghìn tác giả, tác phẩm qua nhiều thời kỳ lịch sử. Tuy nhiên, việc tra cứu, tìm hiểu thông tin về văn học hiện nay còn gặp nhiều khó khăn:
- Thông tin phân tán, không có hệ thống tổ chức rõ ràng
- Khó khăn trong việc tìm kiếm mối liên hệ giữa các tác giả, tác phẩm, nhân vật
- Thiếu công cụ trực quan để hiểu các mối quan hệ phức tạp

Từ đó, việc xây dựng một hệ thống tra cứu sử dụng Knowledge Graph là cần thiết.

#### 1.2. Mục tiêu đề tài
- Nghiên cứu và ứng dụng Knowledge Graph trong lĩnh vực nhân văn
- Xây dựng cơ sở dữ liệu đồ thị về văn học Việt Nam
- Phát triển ứng dụng web hỗ trợ tra cứu và visualization

#### 1.3. Phạm vi nghiên cứu
- **Về nội dung**: Tập trung vào các tác phẩm văn học tiêu biểu trong chương trình phổ thông và đại học
- **Về công nghệ**: Neo4j, Python Flask, JavaScript
- **Về chức năng**: Tra cứu, tìm kiếm, visualization, quản trị

### 2. CƠ SỞ LÝ THUYẾT

#### 2.1. Knowledge Graph (Đồ thị tri thức)

**Định nghĩa**: Knowledge Graph là một cấu trúc dữ liệu dạng đồ thị để biểu diễn tri thức, trong đó:
- **Node (nút)**: Đại diện cho các thực thể (entity)
- **Edge (cạnh)**: Đại diện cho mối quan hệ (relationship) giữa các thực thể
- **Properties (thuộc tính)**: Thông tin bổ sung về thực thể và quan hệ

**Ưu điểm**:
- Biểu diễn trực quan các mối quan hệ phức tạp
- Truy vấn linh hoạt và hiệu quả
- Dễ mở rộng và cập nhật
- Phù hợp với dữ liệu có nhiều liên kết

**Ứng dụng**:
- Google Knowledge Graph
- Facebook Social Graph
- LinkedIn Knowledge Graph
- Các hệ thống gợi ý và tìm kiếm

#### 2.2. Neo4j Graph Database

**Neo4j** là hệ quản trị cơ sở dữ liệu đồ thị phổ biến nhất hiện nay.

**Đặc điểm**:
- Native graph storage: Lưu trữ dữ liệu dưới dạng đồ thị nguyên bản
- ACID transactions: Đảm bảo tính toàn vẹn dữ liệu
- Cypher Query Language: Ngôn ngữ truy vấn trực quan
- Hiệu năng cao với dữ liệu có nhiều quan hệ

**Kiến trúc Neo4j**:
```
┌─────────────────────────────────────┐
│     Neo4j Browser / API             │
├─────────────────────────────────────┤
│     Cypher Query Engine             │
├─────────────────────────────────────┤
│     Transaction Management          │
├─────────────────────────────────────┤
│     Native Graph Storage            │
└─────────────────────────────────────┘
```

#### 2.3. Cypher Query Language

**Cypher** là ngôn ngữ truy vấn của Neo4j, được thiết kế để làm việc với đồ thị.

**Cú pháp cơ bản**:
```cypher
// Tìm node
MATCH (n:Label {property: value})
RETURN n

// Tạo node
CREATE (n:Label {property: value})

// Tạo relationship
MATCH (a:Label1), (b:Label2)
CREATE (a)-[:RELATIONSHIP]->(b)

// Truy vấn pattern
MATCH (a)-[r:RELATIONSHIP]->(b)
WHERE a.property = value
RETURN a, r, b
```

**So sánh với SQL**:
| SQL | Cypher |
|-----|--------|
| Table | Label |
| Row | Node |
| Join | Relationship |
| SELECT | MATCH + RETURN |

#### 2.4. Property Graph Model

Mô hình Property Graph trong Neo4j:
- **Nodes**: Chứa labels và properties
- **Relationships**: Có type, direction và properties
- **Properties**: Key-value pairs

Ví dụ trong đề tài:
```
(TacGia {ten: "Nguyễn Du"})-[:SANG_TAC {nam: 1820}]->(TacPham {ten: "Truyện Kiều"})
```

### 3. PHÂN TÍCH YÊU CẦU HỆ THỐNG

#### 3.1. Yêu cầu chức năng

**Người dùng thông thường**:
1. Tìm kiếm tác giả, tác phẩm, nhân vật
2. Xem thông tin chi tiết tác phẩm
3. Duyệt theo thể loại, chủ đề
4. Xem visualization Knowledge Graph
5. Khám phá mối liên hệ giữa các thực thể

**Quản trị viên**:
1. Thêm/sửa/xóa tác giả
2. Thêm/sửa/xóa tác phẩm
3. Quản lý nhân vật và quan hệ
4. Xem thống kê hệ thống

#### 3.2. Yêu cầu phi chức năng

1. **Hiệu năng**: 
   - Thời gian phản hồi < 2s
   - Hỗ trợ ít nhất 100 users đồng thời

2. **Khả năng mở rộng**:
   - Dễ dàng thêm dữ liệu mới
   - Có thể tích hợp thêm chức năng

3. **Giao diện**:
   - Thân thiện, dễ sử dụng
   - Responsive design
   - Visualization trực quan

4. **Bảo mật**:
   - Xác thực cho chức năng quản trị
   - Validate input để tránh injection

---

## PHẦN II: THIẾT KẾ HỆ THỐNG

### 1. KIẾN TRÚC TỔNG THỂ

```
┌──────────────────────────────────────────────────┐
│                 CLIENT BROWSER                    │
│  (HTML, CSS, JavaScript, Vis.js)                 │
└───────────────────┬──────────────────────────────┘
                    │ HTTP/REST API
┌───────────────────▼──────────────────────────────┐
│              FLASK WEB SERVER                     │
│  ┌──────────────────────────────────────────┐   │
│  │  Routes (API Endpoints)                   │   │
│  │  - /api/tac-gia                          │   │
│  │  - /api/tac-pham                         │   │
│  │  - /api/statistics                       │   │
│  └──────────────┬───────────────────────────┘   │
│                 │                                 │
│  ┌──────────────▼───────────────────────────┐   │
│  │  Service Layer                            │   │
│  │  - Neo4jService (Business Logic)         │   │
│  └──────────────┬───────────────────────────┘   │
└─────────────────┼───────────────────────────────┘
                  │ Bolt Protocol
┌─────────────────▼───────────────────────────────┐
│              NEO4J DATABASE                      │
│  ┌────────────────────────────────────────┐     │
│  │   Knowledge Graph                       │     │
│  │   - Nodes: TacGia, TacPham, NhanVat    │     │
│  │   - Relationships: SANG_TAC, CO_NV     │     │
│  └────────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
```

### 2. THIẾT KẾ KNOWLEDGE GRAPH

#### 2.1. Sơ đồ thực thể - quan hệ (ER Diagram)

```
┌─────────────┐         ┌──────────────┐
│   TacGia    │────────▶│   TacPham    │
└─────────────┘ SANG_TAC└──────────────┘
      │                        │
      │                        │ CO_NHAN_VAT
      │                        ▼
      │                  ┌──────────────┐
      │                  │   NhanVat    │
      │                  └──────────────┘
      │                        │ QUAN_HE
      │                        ▼
      │                  ┌──────────────┐
      │                  │   NhanVat    │
      │                  └──────────────┘
      │
      │ ANH_HUONG
      ▼
┌─────────────┐
│   TacGia    │
└─────────────┘

┌──────────────┐         ┌──────────────┐
│   TacPham    │────────▶│   TheLoai    │
└──────────────┘ THUOC   └──────────────┘

┌──────────────┐         ┌──────────────┐
│   TacPham    │────────▶│    ChuDe     │
└──────────────┘ NOI_VE  └──────────────┘
```

#### 2.2. Định nghĩa Nodes

**Node: TacGia**
```cypher
Properties:
- ten: String (unique, required)
- nam_sinh: Integer
- nam_mat: Integer  
- que_quan: String
- truong_phai: String
- tieu_su: Text
```

**Node: TacPham**
```cypher
Properties:
- ten: String (unique, required)
- nam_sang_tac: Integer
- noi_dung_tom_tat: Text
- chu_de_chinh: String
- y_nghia: Text
- gia_tri_nghe_thuat: Text
- hoang_canh: String
- cau_truc: String
```

**Node: NhanVat**
```cypher
Properties:
- ten: String (required)
- vai_tro: String
- tinh_cach: Text
- so_phan: Text
- y_nghia_dien_hinh: Text
```

#### 2.3. Định nghĩa Relationships

**SANG_TAC**: (TacGia)-[:SANG_TAC]->(TacPham)
```
Properties:
- nam_sang_tac: Integer
```

**CO_NHAN_VAT**: (TacPham)-[:CO_NHAN_VAT]->(NhanVat)
```
Properties:
- vai_tro: String (chính, phụ, phản diện)
```

**QUAN_HE**: (NhanVat)-[:QUAN_HE]->(NhanVat)
```
Properties:
- loai: String (tình yêu, gia đình, thù địch...)
- mo_ta: Text
```

### 3. THIẾT KẾ API

#### 3.1. RESTful API Endpoints

**Tác giả**:
- `GET /api/tac-gia/` - Lấy danh sách tác giả
- `GET /api/tac-gia/search?q=keyword` - Tìm kiếm
- `GET /api/tac-gia/<ten>` - Chi tiết tác giả
- `POST /api/tac-gia/create` - Tạo mới (Admin)

**Tác phẩm**:
- `GET /api/tac-pham/` - Danh sách tác phẩm
- `GET /api/tac-pham/<ten>` - Chi tiết
- `GET /api/tac-pham/the-loai/<name>` - Lọc theo thể loại
- `POST /api/tac-pham/create` - Tạo mới (Admin)
- `PUT /api/tac-pham/<ten>/update` - Cập nhật (Admin)
- `DELETE /api/tac-pham/<ten>/delete` - Xóa (Admin)

#### 3.2. Response Format

Success:
```json
{
  "success": true,
  "data": {...},
  "count": 10
}
```

Error:
```json
{
  "success": false,
  "error": "Error message"
}
```

### 4. THIẾT KẾ GIAO DIỆN

#### 4.1. Wireframes

**Trang chủ**:
- Header với navigation
- Search box nổi bật
- Thống kê dạng cards
- Grid hiển thị tác phẩm tiêu biểu

**Chi tiết tác phẩm**:
- Thông tin tổng quan
- Các section: nội dung, ý nghĩa, giá trị nghệ thuật
- Danh sách nhân vật dạng cards
- Đồ thị Knowledge Graph interactive

#### 4.2. Color Scheme
```
Primary:   #2c3e50 (Dark blue)
Secondary: #3498db (Blue)
Accent:    #e74c3c (Red)
Success:   #27ae60 (Green)
Background: #f5f7fa (Light gray)
```

---

## PHẦN III: CÀI ĐẶT VÀ TRIỂN KHAI

### 1. CÀI ĐẶT DATABASE

#### 1.1. Setup Neo4j
[Chi tiết trong README.md]

#### 1.2. Import Schema và Data
[Chi tiết các câu lệnh Cypher trong files database/]

### 2. PHÁT TRIỂN BACKEND

#### 2.1. Flask Application Structure
```
backend/
├── app.py              # Main application
├── config.py           # Configuration
├── services/
│   └── neo4j_service.py
└── routes/
    ├── tac_gia.py
    ├── tac_pham.py
    └── general.py
```

#### 2.2. Neo4jService Class
Class này encapsulate toàn bộ logic tương tác với Neo4j:
- Connection management
- Query execution
- CRUD operations
- Data transformation

### 3. PHÁT TRIỂN FRONTEND

#### 3.1. HTML Templates
Sử dụng Flask templates với Jinja2:
- Base template với navigation
- Các trang: index, tac_gia, tac_pham, detail, admin

#### 3.2. Styling với CSS
- Responsive design
- Card-based layout
- Modern UI components

#### 3.3. JavaScript
- Fetch API để gọi backend
- DOM manipulation
- Vis.js cho visualization

### 4. INTEGRATION & TESTING

#### 4.1. Unit Testing
Test các service functions:
```python
def test_get_tac_pham():
    service = Neo4jService(...)
    result = service.get_tac_pham_detail("Truyện Kiều")
    assert result is not None
    assert result['ten'] == "Truyện Kiều"
```

#### 4.2. Integration Testing
Test API endpoints:
```bash
curl http://localhost:5000/api/tac-pham/Truyện%20Kiều
```

---

## PHẦN IV: KẾT QUẢ VÀ ĐÁNH GIÁ

### 1. KẾT QUẢ ĐẠT ĐƯỢC

#### 1.1. Dữ liệu
- 6 tác giả tiêu biểu
- 6 tác phẩm văn học nổi tiếng
- 10+ nhân vật chi tiết
- 4 thể loại, nhiều chủ đề
- Hệ thống mối quan hệ phong phú

#### 1.2. Chức năng
✅ Tìm kiếm full-text
✅ Tra cứu theo nhiều tiêu chí
✅ Visualization đồ thị
✅ CRUD operations cho admin
✅ API RESTful đầy đủ
✅ Giao diện responsive

### 2. ĐÁNH GIÁ

#### 2.1. Ưu điểm
- Biểu diễn trực quan mối quan hệ phức tạp
- Truy vấn linh hoạt và hiệu quả
- Dễ mở rộng dữ liệu
- Giao diện thân thiện

#### 2.2. Hạn chế
- Dữ liệu mẫu còn hạn chế
- Chưa có tính năng đề xuất thông minh
- Chưa hỗ trợ xử lý ngôn ngữ tự nhiên
- Chưa có authentication đầy đủ

### 3. HƯỚNG PHÁT TRIỂN

#### 3.1. Ngắn hạn
- Bổ sung thêm dữ liệu văn học
- Cải thiện giao diện admin
- Thêm tính năng bookmark
- Export dữ liệu

#### 3.2. Dài hạn
- Tích hợp NLP để xử lý câu hỏi tự nhiên
- Hệ thống gợi ý dựa trên sở thích
- Mobile app
- Collaborative editing
- Machine Learning để phân tích văn bản

---

## KẾT LUẬN

Đồ án đã thành công xây dựng một hệ thống tra cứu văn học Việt Nam sử dụng Knowledge Graph và Neo4j. Hệ thống cho phép:
- Tổ chức dữ liệu văn học có cấu trúc
- Tra cứu và tìm kiếm linh hoạt
- Visualization trực quan các mối quan hệ
- Quản lý dữ liệu dễ dàng

Dự án là minh chứng cho ứng dụng thực tế của Knowledge Graph trong lĩnh vực nhân văn, mở ra hướng nghiên cứu mới cho Digital Humanities tại Việt Nam.

---

## TÀI LIỆU THAM KHẢO

[1] Neo4j, Inc. (2024). Neo4j Graph Database Documentation. https://neo4j.com/docs/

[2] Robinson, I., Webber, J., & Eifrem, E. (2015). Graph Databases: New Opportunities for Connected Data. O'Reilly Media.

[3] Grinberg, M. (2018). Flask Web Development. O'Reilly Media.

[4] Bộ Giáo dục và Đào tạo. Chương trình giáo dục phổ thông môn Ngữ văn.

[5] Lê Bá Hán et al. Từ điển thuật ngữ văn học. NXB Giáo dục.

[6] Angles, R., & Gutierrez, C. (2008). Survey of graph database models. ACM Computing Surveys.

[7] Hogan, A., et al. (2021). Knowledge Graphs. ACM Computing Surveys.
