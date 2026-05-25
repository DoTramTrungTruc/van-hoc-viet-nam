// ===== SCHEMA CHO HỆ THỐNG VĂN HỌC VIỆT NAM =====

// Tạo constraints để đảm bảo tính duy nhất
CREATE CONSTRAINT tac_gia_ten IF NOT EXISTS FOR (t:TacGia) REQUIRE t.ten IS UNIQUE;
CREATE CONSTRAINT tac_pham_ten IF NOT EXISTS FOR (tp:TacPham) REQUIRE tp.ten IS UNIQUE;
CREATE CONSTRAINT the_loai_ten IF NOT EXISTS FOR (tl:TheLoai) REQUIRE tl.ten IS UNIQUE;
CREATE CONSTRAINT chu_de_ten IF NOT EXISTS FOR (cd:ChuDe) REQUIRE cd.ten IS UNIQUE;
CREATE CONSTRAINT bi_phap_ten IF NOT EXISTS FOR (bp:BiPhap) REQUIRE bp.ten IS UNIQUE;

// Tạo indexes để tối ưu tìm kiếm
CREATE INDEX tac_gia_nam_sinh IF NOT EXISTS FOR (t:TacGia) ON (t.nam_sinh);
CREATE INDEX tac_pham_nam_sang_tac IF NOT EXISTS FOR (tp:TacPham) ON (tp.nam_sang_tac);
CREATE INDEX nhan_vat_ten IF NOT EXISTS FOR (nv:NhanVat) ON (nv.ten);

// ===== MÔ TÁ CẤU TRÚC CÁC NODE =====

// Node: TacGia
// Properties: 
//   - ten: String (bắt buộc)
//   - nam_sinh: Integer
//   - nam_mat: Integer
//   - que_quan: String
//   - truong_phai: String
//   - tieu_su: String (Text dài)
//   - hinh_anh: String (URL)

// Node: TacPham
// Properties:
//   - ten: String (bắt buộc)
//   - ten_khac: List<String> (tên gọi khác)
//   - nam_sang_tac: Integer
//   - noi_dung_tom_tat: String (Text)
//   - chu_de_chinh: String
//   - y_nghia: String (Text)
//   - gia_tri_nghe_thuat: String (Text)
//   - hoang_canh: String
//   - cau_truc: String

// Node: NhanVat
// Properties:
//   - ten: String (bắt buộc)
//   - vai_tro: String (nhân vật chính, phụ, phản diện...)
//   - tinh_cach: String
//   - so_phan: String
//   - y_nghia_dien_hinh: String
//   - chi_tiet_ngoai_hinh: String
//   - chi_tiet_noi_tam: String

// Node: TheLoai
// Properties:
//   - ten: String (truyện thơ, truyện Nôm, tiểu thuyết, thơ...)
//   - dac_diem: String

// Node: ChuDe
// Properties:
//   - ten: String (lòng yêu nước, tình yêu, nhân đạo...)
//   - mo_ta: String

// Node: BiPhap
// Properties:
//   - ten: String (so sánh, ẩn dụ, nhân hóa, điệp...)
//   - dinh_nghia: String
//   - vi_du: String

// Node: ThoiKy
// Properties:
//   - ten: String (Phong kiến, Pháp thuộc, Kháng chiến...)
//   - tu_nam: Integer
//   - den_nam: Integer
//   - boi_canh: String

// ===== RELATIONSHIPS =====
// [:SANG_TAC] - TacGia -> TacPham
//   Properties: nam_sang_tac
//
// [:CO_NHAN_VAT] - TacPham -> NhanVat
//   Properties: vai_tro
//
// [:THUOC_THE_LOAI] - TacPham -> TheLoai
//
// [:NOI_VE] - TacPham -> ChuDe
//   Properties: muc_do (chính, phụ)
//
// [:SU_DUNG] - TacPham -> BiPhap
//   Properties: vi_du_cu_the
//
// [:THUOC_THOI_KY] - TacPham -> ThoiKy
//
// [:QUAN_HE] - NhanVat -> NhanVat
//   Properties: loai (tình yêu, gia đình, thù địch...)
//
// [:ANH_HUONG] - TacGia -> TacGia
//   Properties: mo_ta
