// ===== THƯ VIỆN TRUY VẤN CYPHER MẪU =====

// ===== 1. TRUY VẤN VỀ TÁC GIẢ =====

// 1.1. Tìm tất cả tác giả
MATCH (t:TacGia)
RETURN t.ten AS ten_tac_gia, t.nam_sinh, t.nam_mat, t.que_quan
ORDER BY t.nam_sinh;

// 1.2. Tìm tác giả theo tên (tìm kiếm không phân biệt hoa thường)
MATCH (t:TacGia)
WHERE toLower(t.ten) CONTAINS toLower($ten_tim_kiem)
RETURN t;

// 1.3. Tìm tác giả sinh vào khoảng thời gian
MATCH (t:TacGia)
WHERE t.nam_sinh >= $nam_bat_dau AND t.nam_sinh <= $nam_ket_thuc
RETURN t.ten, t.nam_sinh, t.que_quan;

// 1.4. Tìm tác giả và các tác phẩm của họ
MATCH (t:TacGia)-[:SANG_TAC]->(tp:TacPham)
WHERE t.ten = $ten_tac_gia
RETURN t.ten AS tac_gia, collect(tp.ten) AS cac_tac_pham;

// 1.5. Tìm tác giả có nhiều tác phẩm nhất
MATCH (t:TacGia)-[:SANG_TAC]->(tp:TacPham)
RETURN t.ten AS tac_gia, count(tp) AS so_tac_pham
ORDER BY so_tac_pham DESC
LIMIT 5;

// ===== 2. TRUY VẤN VỀ TÁC PHẨM =====

// 2.1. Tìm tất cả tác phẩm
MATCH (tp:TacPham)
RETURN tp.ten, tp.nam_sang_tac
ORDER BY tp.nam_sang_tac;

// 2.2. Tìm tác phẩm theo tên
MATCH (tp:TacPham)
WHERE toLower(tp.ten) CONTAINS toLower($ten_tac_pham)
RETURN tp;

// 2.3. Tìm chi tiết tác phẩm kèm tác giả
MATCH (t:TacGia)-[:SANG_TAC]->(tp:TacPham)
WHERE tp.ten = $ten_tac_pham
RETURN t.ten AS tac_gia, tp.ten AS tac_pham, 
       tp.nam_sang_tac, tp.noi_dung_tom_tat, tp.y_nghia;

// 2.4. Tìm tác phẩm theo thể loại
MATCH (tp:TacPham)-[:THUOC_THE_LOAI]->(tl:TheLoai)
WHERE tl.ten = $the_loai
RETURN tp.ten AS tac_pham, tp.nam_sang_tac;

// 2.5. Tìm tác phẩm theo chủ đề
MATCH (tp:TacPham)-[:NOI_VE]->(cd:ChuDe)
WHERE cd.ten = $chu_de
RETURN tp.ten AS tac_pham, cd.ten AS chu_de;

// 2.6. Tìm tác phẩm cùng thời kỳ
MATCH (tp:TacPham)-[:THUOC_THOI_KY]->(tk:ThoiKy)
WHERE tk.ten = $thoi_ky
RETURN tp.ten AS tac_pham, tp.nam_sang_tac;

// ===== 3. TRUY VẤN VỀ NHÂN VẬT =====

// 3.1. Tìm tất cả nhân vật trong một tác phẩm
MATCH (tp:TacPham)-[r:CO_NHAN_VAT]->(nv:NhanVat)
WHERE tp.ten = $ten_tac_pham
RETURN nv.ten AS nhan_vat, nv.vai_tro, nv.tinh_cach, nv.so_phan;

// 3.2. Tìm nhân vật theo tên
MATCH (nv:NhanVat)
WHERE toLower(nv.ten) CONTAINS toLower($ten_nhan_vat)
RETURN nv;

// 3.3. Tìm tác phẩm chứa nhân vật
MATCH (tp:TacPham)-[:CO_NHAN_VAT]->(nv:NhanVat)
WHERE nv.ten = $ten_nhan_vat
RETURN tp.ten AS tac_pham;

// 3.4. Tìm mối quan hệ giữa các nhân vật
MATCH (nv1:NhanVat)-[r:QUAN_HE]->(nv2:NhanVat)
WHERE nv1.ten = $ten_nhan_vat
RETURN nv1.ten AS tu_nhan_vat, type(r) AS quan_he, 
       r.loai AS loai_quan_he, nv2.ten AS den_nhan_vat, r.mo_ta;

// 3.5. Tìm nhân vật chính trong các tác phẩm
MATCH (tp:TacPham)-[r:CO_NHAN_VAT]->(nv:NhanVat)
WHERE r.vai_tro = "chính" OR nv.vai_tro = "Nhân vật chính"
RETURN tp.ten AS tac_pham, collect(nv.ten) AS nhan_vat_chinh;

// ===== 4. TRUY VẤN PHỨC HOP =====

// 4.1. Tìm toàn bộ thông tin về một tác phẩm (tác giả, nhân vật, thể loại, chủ đề)
MATCH (t:TacGia)-[:SANG_TAC]->(tp:TacPham)
WHERE tp.ten = $ten_tac_pham
OPTIONAL MATCH (tp)-[:CO_NHAN_VAT]->(nv:NhanVat)
OPTIONAL MATCH (tp)-[:THUOC_THE_LOAI]->(tl:TheLoai)
OPTIONAL MATCH (tp)-[:NOI_VE]->(cd:ChuDe)
OPTIONAL MATCH (tp)-[:SU_DUNG]->(bp:BiPhap)
RETURN t.ten AS tac_gia,
       tp.ten AS tac_pham,
       tp.noi_dung_tom_tat,
       tp.y_nghia,
       collect(DISTINCT nv.ten) AS nhan_vat,
       collect(DISTINCT tl.ten) AS the_loai,
       collect(DISTINCT cd.ten) AS chu_de,
       collect(DISTINCT bp.ten) AS bi_phap;

// 4.2. Tìm các tác phẩm cùng chủ đề
MATCH (tp1:TacPham)-[:NOI_VE]->(cd:ChuDe)<-[:NOI_VE]-(tp2:TacPham)
WHERE tp1.ten = $ten_tac_pham AND tp1 <> tp2
RETURN DISTINCT tp2.ten AS tac_pham_cung_chu_de, 
       collect(DISTINCT cd.ten) AS chu_de_chung;

// 4.3. Tìm tác phẩm của cùng tác giả
MATCH (t:TacGia)-[:SANG_TAC]->(tp1:TacPham)
WHERE tp1.ten = $ten_tac_pham
MATCH (t)-[:SANG_TAC]->(tp2:TacPham)
WHERE tp1 <> tp2
RETURN t.ten AS tac_gia, collect(tp2.ten) AS tac_pham_khac;

// 4.4. So sánh hai tác phẩm
MATCH (tp1:TacPham), (tp2:TacPham)
WHERE tp1.ten = $tac_pham_1 AND tp2.ten = $tac_pham_2
OPTIONAL MATCH (tp1)-[:NOI_VE]->(cd1:ChuDe)
OPTIONAL MATCH (tp2)-[:NOI_VE]->(cd2:ChuDe)
OPTIONAL MATCH (tp1)-[:THUOC_THE_LOAI]->(tl1:TheLoai)
OPTIONAL MATCH (tp2)-[:THUOC_THE_LOAI]->(tl2:TheLoai)
RETURN tp1.ten AS tac_pham_1,
       tp2.ten AS tac_pham_2,
       collect(DISTINCT cd1.ten) AS chu_de_1,
       collect(DISTINCT cd2.ten) AS chu_de_2,
       collect(DISTINCT tl1.ten) AS the_loai_1,
       collect(DISTINCT tl2.ten) AS the_loai_2;

// 4.5. Thống kê số lượng tác phẩm theo thể loại
MATCH (tp:TacPham)-[:THUOC_THE_LOAI]->(tl:TheLoai)
RETURN tl.ten AS the_loai, count(tp) AS so_luong_tac_pham
ORDER BY so_luong_tac_pham DESC;

// 4.6. Thống kê số lượng tác phẩm theo thời kỳ
MATCH (tp:TacPham)-[:THUOC_THOI_KY]->(tk:ThoiKy)
RETURN tk.ten AS thoi_ky, count(tp) AS so_luong_tac_pham
ORDER BY tk.tu_nam;

// ===== 5. TRUY VẤN TÌM KIẾM NÂNG CAO =====

// 5.1. Tìm kiếm full-text (tìm theo nhiều trường)
MATCH (tp:TacPham)
WHERE toLower(tp.ten) CONTAINS toLower($keyword)
   OR toLower(tp.noi_dung_tom_tat) CONTAINS toLower($keyword)
   OR toLower(tp.y_nghia) CONTAINS toLower($keyword)
RETURN tp.ten, tp.noi_dung_tom_tat;

// 5.2. Tìm đường đi ngắn nhất giữa hai nhân vật
MATCH path = shortestPath(
  (nv1:NhanVat {ten: $nhan_vat_1})-[*]-(nv2:NhanVat {ten: $nhan_vat_2})
)
RETURN path;

// 5.3. Tìm tác giả có ảnh hưởng (được nhiều tác giả khác tham khảo)
MATCH (t1:TacGia)<-[:ANH_HUONG]-(t2:TacGia)
RETURN t1.ten AS tac_gia, count(t2) AS so_nguoi_chiu_anh_huong
ORDER BY so_nguoi_chiu_anh_huong DESC;

// ===== 6. TRUY VẤN VỀ BÌ PHÁP NGHỆ THUẬT =====

// 6.1. Tìm tác phẩm sử dụng bì pháp cụ thể
MATCH (tp:TacPham)-[r:SU_DUNG]->(bp:BiPhap)
WHERE bp.ten = $bi_phap
RETURN tp.ten AS tac_pham, r.vi_du_cu_the AS vi_du;

// 6.2. Liệt kê các bì pháp sử dụng trong tác phẩm
MATCH (tp:TacPham)-[r:SU_DUNG]->(bp:BiPhap)
WHERE tp.ten = $ten_tac_pham
RETURN bp.ten AS bi_phap, bp.dinh_nghia, r.vi_du_cu_the;

// ===== 7. TRUY VẤN ĐỒ THỊ VISUALIZATION =====

// 7.1. Lấy đồ thị của một tác phẩm (để hiển thị bằng vis.js)
MATCH path = (t:TacGia)-[:SANG_TAC]->(tp:TacPham)-[r]-(n)
WHERE tp.ten = $ten_tac_pham
RETURN path;

// 7.2. Lấy đồ thị quan hệ giữa các nhân vật
MATCH path = (tp:TacPham)-[:CO_NHAN_VAT]->(nv1:NhanVat)-[r:QUAN_HE]->(nv2:NhanVat)
WHERE tp.ten = $ten_tac_pham
RETURN path;

// ===== 8. TRUY VẤN QUẢN TRỊ =====

// 8.1. Thêm tác giả mới
CREATE (t:TacGia {
  ten: $ten,
  nam_sinh: $nam_sinh,
  nam_mat: $nam_mat,
  que_quan: $que_quan,
  truong_phai: $truong_phai,
  tieu_su: $tieu_su
})
RETURN t;

// 8.2. Thêm tác phẩm mới
MATCH (t:TacGia {ten: $ten_tac_gia})
CREATE (tp:TacPham {
  ten: $ten_tac_pham,
  nam_sang_tac: $nam_sang_tac,
  noi_dung_tom_tat: $noi_dung,
  y_nghia: $y_nghia
})
CREATE (t)-[:SANG_TAC]->(tp)
RETURN tp;

// 8.3. Cập nhật thông tin tác phẩm
MATCH (tp:TacPham {ten: $ten_tac_pham})
SET tp.noi_dung_tom_tat = $noi_dung_moi,
    tp.y_nghia = $y_nghia_moi
RETURN tp;

// 8.4. Xóa tác phẩm
MATCH (tp:TacPham {ten: $ten_tac_pham})
DETACH DELETE tp;

// 8.5. Thêm nhân vật vào tác phẩm
MATCH (tp:TacPham {ten: $ten_tac_pham})
CREATE (nv:NhanVat {
  ten: $ten_nhan_vat,
  vai_tro: $vai_tro,
  tinh_cach: $tinh_cach,
  so_phan: $so_phan
})
CREATE (tp)-[:CO_NHAN_VAT {vai_tro: $vai_tro}]->(nv)
RETURN nv;

// 8.6. Tạo quan hệ giữa hai nhân vật
MATCH (nv1:NhanVat {ten: $nhan_vat_1})
MATCH (nv2:NhanVat {ten: $nhan_vat_2})
CREATE (nv1)-[:QUAN_HE {loai: $loai_quan_he, mo_ta: $mo_ta}]->(nv2)
RETURN nv1, nv2;
