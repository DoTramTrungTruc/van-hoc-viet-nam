// ===== DỮ LIỆU MẪU - VĂN HỌC VIỆT NAM =====

// ===== TẠO THỂ LOẠI =====
CREATE (tl1:TheLoai {ten: "Truyện thơ", dac_diem: "Tác phẩm kể chuyện bằng thơ, thường là thơ lục bát"})
CREATE (tl2:TheLoai {ten: "Tiểu thuyết", dac_diem: "Tác phẩm văn xuôi kể chuyện dài, có cốt truyện phức tạp"})
CREATE (tl3:TheLoai {ten: "Truyện ngắn", dac_diem: "Tác phẩm văn xuôi ngắn gọn, tập trung vào một sự kiện"})
CREATE (tl4:TheLoai {ten: "Thơ", dac_diem: "Thể loại văn học dùng ngôn ngữ có vần điệu, nhịp điệu"})

// ===== TẠO CHỦ ĐỀ =====
CREATE (cd1:ChuDe {ten: "Tình yêu", mo_ta: "Tình cảm nam nữ, tình yêu đôi lứa"})
CREATE (cd2:ChuDe {ten: "Số phận phụ nữ", mo_ta: "Những bất hạnh, đau khổ của phụ nữ trong xã hội phong kiến"})
CREATE (cd3:ChuDe {ten: "Cuộc sống nông thôn", mo_ta: "Đời sống, lao động của người dân làng quê"})
CREATE (cd4:ChuDe {ten: "Chống áp bức bóc lột", mo_ta: "Phê phán chế độ phong kiến, thực dân"})
CREATE (cd5:ChuDe {ten: "Nhân đạo", mo_ta: "Lòng thương người, tinh thần nhân văn"})

// ===== TẠO BÌ PHÁP =====
CREATE (bp1:BiPhap {ten: "So sánh", dinh_nghia: "Đặt sự vật này cạnh sự vật khác để tìm điểm tương đồng", vi_du: "Thúy Kiều như hoa gặp gió"})
CREATE (bp2:BiPhap {ten: "Ẩn dụ", dinh_nghia: "Chỉ vật này qua vật khác có điểm tương đồng", vi_du: "Thuyền quyên"})
CREATE (bp3:BiPhap {ten: "Nhân hóa", dinh_nghia: "Cho vật vô tri có tính cách, hành động của con người", vi_du: "Trăng tàn hoa rụng"})
CREATE (bp4:BiPhap {ten: "Điệp từ", dinh_nghia: "Lặp lại từ, cụm từ để nhấn mạnh", vi_du: "Tàu về, tàu về"})
CREATE (bp5:BiPhap {ten: "Phản nghĩa", dinh_nghia: "Dùng từ ngữ có nghĩa trái ngược để tạo hiệu quả", vi_du: "Sống mà như thác"})

// ===== TẠO THỜI KỲ =====
CREATE (tk1:ThoiKy {ten: "Phong kiến", tu_nam: 1000, den_nam: 1858, boi_canh: "Thời kỳ phong kiến độc lập, chế độ quân chủ chuyên chế"})
CREATE (tk2:ThoiKy {ten: "Pháp thuộc", tu_nam: 1858, den_nam: 1945, boi_canh: "Thời kỳ Pháp xâm lược, đô hộ Việt Nam"})
CREATE (tk3:ThoiKy {ten: "Kháng chiến chống Pháp", tu_nam: 1945, den_nam: 1954, boi_canh: "Cuộc kháng chiến chống thực dân Pháp"})
CREATE (tk4:ThoiKy {ten: "Hiện đại", tu_nam: 1945, den_nam: 2024, boi_canh: "Thời kỳ văn học hiện đại Việt Nam"})

// ===== TÁC GIẢ NGUYỄN DU =====
CREATE (tg1:TacGia {
  ten: "Nguyễn Du",
  nam_sinh: 1765,
  nam_mat: 1820,
  que_quan: "Tiên Điền, Nghi Xuân, Hà Tĩnh",
  truong_phai: "Văn học phong kiến",
  tieu_su: "Nguyễn Du (1765-1820) là nhà thơ lớn nhất Việt Nam, được UNESCO công nhận là danh nhân văn hóa thế giới. Sinh ra trong gia đình quan lại nhà Lê, ông chứng kiến sự sụp đổ của triều Lê và sự thay thế bởi triều Nguyễn. Tác phẩm Truyện Kiều là kiệt tác bất hủ của văn học Việt Nam."
})

// ===== TÁC PHẨM TRUYỆN KIỀU =====
CREATE (tp1:TacPham {
  ten: "Truyện Kiều",
  ten_khac: ["Đoạn Trường Tân Thanh", "Kim Vân Kiều truyện"],
  nam_sang_tac: 1820,
  noi_dung_tom_tat: "Tác phẩm kể về số phận bi thảm của Thúy Kiều - một cô gái tài sắc vẹn toàn nhưng phải chịu nhiều thăng trầm, bị đẩy vào con đường ô trọc để chuộc thân cho cha anh. Sau 15 năm lưu lạc, cuối cùng Kiều được đoàn tụ với Kim Trọng nhưng không thể trở thành vợ chánh mà chỉ là bạn tri âm.",
  chu_de_chinh: "Số phận phụ nữ, tài hoa gặp bạc mệnh",
  y_nghia: "Tác phẩm phản ánh sâu sắc số phận người phụ nữ trong xã hội phong kiến, đồng thời thể hiện tư tưởng nhân văn sâu sắc của Nguyễn Du. Truyện Kiều là tuyệt tác văn học Việt Nam, được xem như 'quốc bảo' của dân tộc.",
  gia_tri_nghe_thuat: "3254 câu thơ lục bát trường thiên với ngôn ngữ xuôi oai, giàu chất thơ. Kỹ thuật miêu tả tâm lý nhân vật tinh tế. Sử dụng nhiều bì pháp tu từ cao. Cấu trúc hoàn chỉnh, chặt chẽ.",
  hoang_canh: "Đầu thế kỷ 19, thời phong kiến Việt Nam",
  cau_truc: "Gồm 3 phần: Khởi - Thúy Kiều gặp Kim Trọng; Thân - 15 năm lưu lạc của Kiều; Kết - Kiều đoàn tụ với Kim Trọng"
})

// ===== NHÂN VẬT TRUYỆN KIỀU =====
CREATE (nv1:NhanVat {
  ten: "Thúy Kiều",
  vai_tro: "Nhân vật chính",
  tinh_cach: "Tài sắc vẹn toàn, hiếu thảo, trung với tình yêu, có ý thức về danh dự",
  so_phan: "Sinh ra trong gia đình khá giả nhưng gặp hoạn nạn, phải hy sinh hạnh phúc cá nhân để cứu cha anh. Trải qua 15 năm lưu lạc đầy đau khổ.",
  y_nghia_dien_hinh: "Điển hình cho số phận bi kịch của người phụ nữ tài hoa trong xã hội phong kiến. Thể hiện sự mâu thuẫn giữa tài năng, khát vọng với hoàn cảnh xã hội.",
  chi_tiet_ngoai_hinh: "Sắc đẹp tuyệt trần, tài năng xuất chúng, biết làm thơ, đàn ca",
  chi_tiet_noi_tam: "Tâm hồn trong sáng, có ý thức tự trọng cao, luôn khao khát hạnh phúc nhưng đầy bi quan về số phận"
})

CREATE (nv2:NhanVat {
  ten: "Kim Trọng",
  vai_tro: "Nhân vật chính",
  tinh_cach: "Đa tình, yêu thương Kiều chân thành, có chút yếu đuối",
  so_phan: "Người yêu của Kiều, đợi chờ 15 năm và cuối cùng đoàn tụ với nàng",
  y_nghia_dien_hinh: "Điển hình người trai tài yêu gái sắc, trung thành nhưng cũng bộc lộ sự yếu đuối của người đàn ông trong xã hội phong kiến"
})

CREATE (nv3:NhanVat {
  ten: "Thúy Vân",
  vai_tro: "Nhân vật phụ",
  tinh_cach: "Hiền lành, hiểu chuyện, biết nhường nhịn",
  so_phan: "Em gái Kiều, sau này trở thành vợ chánh của Kim Trọng",
  y_nghia_dien_hinh: "Tương phản với Kiều - người phụ nữ bình thường nhưng có được hạnh phúc"
})

CREATE (nv4:NhanVat {
  ten: "Sở Khanh",
  vai_tro: "Phản diện",
  tinh_cach: "Gian ác, xảo quyệt, lừa đảo",
  so_phan: "Kẻ lừa bán Kiều vào lầu xanh, cuối cùng bị trừng phạt",
  y_nghia_dien_hinh: "Điển hình cho sự xảo trá, phi nghĩa của kẻ tiểu nhân"
})

CREATE (nv5:NhanVat {
  ten: "Hoạn Thư",
  vai_tro: "Phản diện",
  tinh_cach: "Độc ác, ghen tuông, tàn nhẫn",
  so_phan: "Vợ cả của Thúc Khanh, hành hạ Kiều dã man",
  y_nghia_dien_hinh: "Điển hình cho sự ác độc, ghen ghét của phụ nữ phong kiến"
})

CREATE (nv6:NhanVat {
  ten: "Từ Hải",
  vai_tro: "Nhân vật chính",
  tinh_cach: "Anh hùng hào khí, nghĩa hiệp, yêu Kiều thương thật",
  so_phan: "Thủ lĩnh nghĩa quân, yêu Kiều và muốn giúp nàng báo thù, cuối cùng bị chết do nghe lời Kiều",
  y_nghia_dien_hinh: "Điển hình anh hùng lỗi thời, người có tài nhưng không gặp thời"
})

// ===== TẠO MỐI QUAN HỆ TRUYỆN KIỀU =====
CREATE (tg1)-[:SANG_TAC {nam_sang_tac: 1820}]->(tp1)
CREATE (tp1)-[:THUOC_THE_LOAI]->(tl1)
CREATE (tp1)-[:THUOC_THOI_KY]->(tk1)
CREATE (tp1)-[:NOI_VE {muc_do: "chính"}]->(cd1)
CREATE (tp1)-[:NOI_VE {muc_do: "chính"}]->(cd2)
CREATE (tp1)-[:SU_DUNG {vi_du_cu_the: "Vừa hay vừa dở đoạn trường thiên"}]->(bp1)
CREATE (tp1)-[:SU_DUNG {vi_du_cu_the: "Thuyền quyên bể khổ trần ai"}]->(bp2)

CREATE (tp1)-[:CO_NHAN_VAT {vai_tro: "chính"}]->(nv1)
CREATE (tp1)-[:CO_NHAN_VAT {vai_tro: "chính"}]->(nv2)
CREATE (tp1)-[:CO_NHAN_VAT {vai_tro: "phụ"}]->(nv3)
CREATE (tp1)-[:CO_NHAN_VAT {vai_tro: "phản diện"}]->(nv4)
CREATE (tp1)-[:CO_NHAN_VAT {vai_tro: "phản diện"}]->(nv5)
CREATE (tp1)-[:CO_NHAN_VAT {vai_tro: "chính"}]->(nv6)

CREATE (nv1)-[:QUAN_HE {loai: "tình yêu", mo_ta: "Người yêu đầu tiên"}]->(nv2)
CREATE (nv1)-[:QUAN_HE {loai: "chị em", mo_ta: "Em gái ruột"}]->(nv3)
CREATE (nv1)-[:QUAN_HE {loai: "thù địch", mo_ta: "Kẻ lừa đảo"}]->(nv4)
CREATE (nv1)-[:QUAN_HE {loai: "thù địch", mo_ta: "Người hành hạ"}]->(nv5)
CREATE (nv1)-[:QUAN_HE {loai: "vợ chồng", mo_ta: "Chồng thứ hai, anh hùng nghĩa hiệp"}]->(nv6)

// ===== NAM CAO =====
CREATE (tg2:TacGia {
  ten: "Nam Cao",
  nam_sinh: 1915,
  nam_mat: 1951,
  que_quan: "Hà Nam",
  truong_phai: "Văn học hiện thực",
  tieu_su: "Nam Cao là nhà văn hiện thực xuất sắc, tên thật là Trần Hữu Tri. Ông nổi tiếng với các tác phẩm phê phán xã hội, phản ánh cuộc sống người lao động nghèo khổ. Tác phẩm tiêu biểu: Chí Phèo, Lão Hạc, Sống mòn..."
})

// ===== CHÍ PHÈO =====
CREATE (tp2:TacPham {
  ten: "Chí Phèo",
  nam_sang_tac: 1941,
  noi_dung_tom_tat: "Tác phẩm kể về Chí Phèo - một người nông dân nghèo khổ bị xã hội đẩy xuống con đường sa đọa, trở thành kẻ lưu manh. Chí Phèo yêu Thị Nở nhưng không được đáp lại, cuối cùng chết trong cô đơn và uất hận.",
  chu_de_chinh: "Số phận người nông dân nghèo, sự bất công xã hội",
  y_nghia: "Tác phẩm phê phán sâu sắc chế độ thực dân phong kiến, đồng thời thể hiện lòng thương cảm với những con người bị xã hội làm méo mó nhân cách.",
  gia_tri_nghe_thuat: "Nghệ thuật miêu tả tâm lý tinh tế, ngôn ngữ giàu chất dân gian. Kết cấu chặt chẽ, kỹ thuật hồi tưởng khéo léo.",
  hoang_canh: "Nông thôn Bắc Bộ thời Pháp thuộc, những năm 1930-1940",
  cau_truc: "Kết cấu 2 mạch: hiện tại và quá khứ đan xen"
})

CREATE (nv7:NhanVat {
  ten: "Chí Phèo",
  vai_tro: "Nhân vật chính",
  tinh_cach: "Hung dữ, cộc cằn nhưng có lúc tử tế, mặc cảm tự ti sâu sắc",
  so_phan: "Từ người nông dân lương thiện trở thành kẻ lưu manh do bị xã hội đẩy đi, cuối cùng chết trong cô đơn",
  y_nghia_dien_hinh: "Điển hình cho những người nông dân nghèo bị xã hội phong kiến đẩy vào con đường sa đọa"
})

CREATE (nv8:NhanVat {
  ten: "Thị Nở",
  vai_tro: "Nhân vật chính",
  tinh_cach: "Thực dụng, tự ti nhưng cũng đáng thương",
  so_phan: "Bị gia đình ép làm vợ lẽ của lý trưởng, sống trong cảnh bị coi thường",
  y_nghia_dien_hinh: "Số phận người phụ nữ nghèo bị mua bán trong xã hội cũ"
})

CREATE (tg2)-[:SANG_TAC {nam_sang_tac: 1941}]->(tp2)
CREATE (tp2)-[:THUOC_THE_LOAI]->(tl3)
CREATE (tp2)-[:THUOC_THOI_KY]->(tk2)
CREATE (tp2)-[:NOI_VE {muc_do: "chính"}]->(cd3)
CREATE (tp2)-[:NOI_VE {muc_do: "chính"}]->(cd4)
CREATE (tp2)-[:CO_NHAN_VAT]->(nv7)
CREATE (tp2)-[:CO_NHAN_VAT]->(nv8)
CREATE (nv7)-[:QUAN_HE {loai: "tình yêu đơn phương", mo_ta: "Yêu nhưng không được đáp lại"}]->(nv8)

// ===== NGÔ TẤT TỐ =====
CREATE (tg3:TacGia {
  ten: "Ngô Tất Tố",
  nam_sinh: 1894,
  nam_mat: 1954,
  que_quan: "Hà Tĩnh",
  truong_phai: "Văn học hiện thực",
  tieu_su: "Ngô Tất Tố là nhà văn tiêu biểu của văn học hiện thực Việt Nam. Tác phẩm nổi tiếng nhất là Tắt đèn - tiểu thuyết phản ánh cuộc sống nông dân Việt Nam đầu thế kỷ 20."
})

// ===== TẮT ĐÈN =====
CREATE (tp3:TacPham {
  ten: "Tắt đèn",
  nam_sang_tac: 1939,
  noi_dung_tom_tat: "Tiểu thuyết kể về cuộc đời vợ chồng Chị Dậu - Dậu trong xã hội nông thôn Bắc Bộ. Họ phải sống trong cảnh nghèo đói, vất vả nhưng luôn lao động cần cù. Chị Dậu là người phụ nữ xinh đẹp, hiền lành nhưng cuộc sống khổ cực đã làm chị già đi trước tuổi.",
  chu_de_chinh: "Cuộc sống cơ cực của người nông dân",
  y_nghia: "Tác phẩm phản ánh chân thực cuộc sống khốn khó của người nông dân Việt Nam dưới ách đô hộ của thực dân Pháp, đồng thời ca ngợi sức sống mãnh liệt của họ.",
  gia_tri_nghe_thuat: "Nghệ thuật miêu tả tỉ mỉ, chân thực, ngôn ngữ giản dị mang đậm chất dân gian",
  hoang_canh: "Nông thôn Bắc Bộ đầu thế kỷ 20",
  cau_truc: "Kết cấu theo dòng thời gian tuyến tính"
})

CREATE (nv9:NhanVat {
  ten: "Chị Dậu",
  vai_tro: "Nhân vật chính",
  tinh_cach: "Hiền lành, cần cù, chịu đựng",
  so_phan: "Người phụ nữ nông dân xinh đẹp nhưng cuộc sống nghèo khổ làm già nua trước tuổi",
  y_nghia_dien_hinh: "Điển hình cho người phụ nữ nông dân Việt Nam cần cù, chịu thương chịu khó"
})

CREATE (tg3)-[:SANG_TAC {nam_sang_tac: 1939}]->(tp3)
CREATE (tp3)-[:THUOC_THE_LOAI]->(tl2)
CREATE (tp3)-[:THUOC_THOI_KY]->(tk2)
CREATE (tp3)-[:NOI_VE {muc_do: "chính"}]->(cd3)
CREATE (tp3)-[:CO_NHAN_VAT]->(nv9)

// ===== KIM LÂN =====
CREATE (tg4:TacGia {
  ten: "Kim Lân",
  nam_sinh: 1920,
  nam_mat: 2007,
  que_quan: "Hà Nội",
  truong_phai: "Văn học hiện thực",
  tieu_su: "Kim Lân là nhà văn nổi tiếng với các truyện ngắn về đời sống nông thôn, đặc biệt là tác phẩm Vợ nhặt - một trong những truyện ngắn hay nhất văn học Việt Nam."
})

// ===== VỢ NHẶT =====
CREATE (tp4:TacPham {
  ten: "Vợ nhặt",
  nam_sang_tac: 1962,
  noi_dung_tom_tat: "Tác phẩm kể về Tràng trong hoàn cảnh nạn đói 1945 đã 'nhặt' được một cô gái bị bỏ rơi và cưới làm vợ. Câu chuyện thể hiện tình người trong hoàn cảnh khốn cùng.",
  chu_de_chinh: "Tình người trong hoàn cảnh khốn khó",
  y_nghia: "Tác phẩm ca ngợi tình người cao đẹp, lòng nhân ái trong hoàn cảnh khốn cùng nhất.",
  gia_tri_nghe_thuat: "Ngôn ngữ giản dị, chân thực. Kết thúc bất ngờ gây ấn tượng mạnh.",
  hoang_canh: "Nông thôn Bắc Bộ năm 1945 - thời kỳ nạn đói",
  cau_truc: "Kết cấu đơn giản, tập trung vào một sự kiện"
})

CREATE (nv10:NhanVat {
  ten: "Tràng",
  vai_tro: "Nhân vật chính",
  tinh_cach: "Chất phác, tốt bụng, nhân hậu",
  so_phan: "Người nông dân nghèo nhặt được vợ trong nạn đói",
  y_nghia_dien_hinh: "Điển hình cho lòng nhân ái của người nông dân Việt Nam"
})

CREATE (tg4)-[:SANG_TAC {nam_sang_tac: 1962}]->(tp4)
CREATE (tp4)-[:THUOC_THE_LOAI]->(tl3)
CREATE (tp4)-[:NOI_VE {muc_do: "chính"}]->(cd5)
CREATE (tp4)-[:NOI_VE {muc_do: "phụ"}]->(cd3)
CREATE (tp4)-[:CO_NHAN_VAT]->(nv10)

// ===== TỐ HỮU =====
CREATE (tg5:TacGia {
  ten: "Tố Hữu",
  nam_sinh: 1920,
  nam_mat: 2002,
  que_quan: "Thừa Thiên Huế",
  truong_phai: "Thơ cách mạng",
  tieu_su: "Tố Hữu, tên thật là Nguyễn Kim Thành, là nhà thơ lớn của cách mạng Việt Nam. Thơ ông gắn liền với lịch sử dân tộc, ca ngợi Đảng, Bác Hồ và con người Việt Nam."
})

CREATE (tp5:TacPham {
  ten: "Việt Bắc",
  nam_sang_tac: 1954,
  noi_dung_tom_tat: "Bài thơ ca ngợi vẻ đẹp thiên nhiên và con người Việt Bắc - vùng căn cứ địa kháng chiến. Thể hiện tình cảm sâu sắc của tác giả với mảnh đất và con người nơi đây.",
  chu_de_chinh: "Tình yêu quê hương, đất nước",
  y_nghia: "Ca ngợi vẻ đẹp thiên nhiên và con người Việt Bắc, đồng thời thể hiện tinh thần cách mạng lạc quan, yêu đời.",
  gia_tri_nghe_thuat: "Thơ giàu hình ảnh, ngôn ngữ trong sáng, nhịp điệu du dương",
  hoang_canh: "Việt Bắc thời kỳ kháng chiến chống Pháp",
  cau_truc: "Gồm nhiều đoạn thơ ca ngợi các cảnh vật, con người"
})

CREATE (tg5)-[:SANG_TAC {nam_sang_tac: 1954}]->(tp5)
CREATE (tp5)-[:THUOC_THE_LOAI]->(tl4)
CREATE (tp5)-[:THUOC_THOI_KY]->(tk3)

// ===== HỒ XUÂN HƯƠNG =====
CREATE (tg6:TacGia {
  ten: "Hồ Xuân Hương",
  nam_sinh: 1772,
  nam_mat: 1822,
  que_quan: "Nghệ An (hoặc Hà Tĩnh)",
  truong_phai: "Thơ Nôm phong kiến",
  tieu_su: "Hồ Xuân Hương là nữ thi sĩ tài hoa bậc nhất thời phong kiến. Bà nổi tiếng với những bài thơ Nôm táo bạo, phê phán xã hội và bộc lộ khát vọng tự do của người phụ nữ."
})

CREATE (cd6:ChuDe {ten: "Phê phán xã hội", mo_ta: "Châm biếm, phê phán các tệ nạn xã hội phong kiến"})
CREATE (cd7:ChuDe {ten: "Khát vọng tự do", mo_ta: "Mong muốn được tự do, bình đẳng"})

CREATE (tp6:TacPham {
  ten: "Bánh trôi nước",
  noi_dung_tom_tat: "Bài thơ dùng hình ảnh bánh trôi nước để nói về thân phận người phụ nữ tài hoa nhưng không được trọng dụng trong xã hội phong kiến.",
  chu_de_chinh: "Số phận phụ nữ tài hoa",
  y_nghia: "Bài thơ phản ánh nỗi buồn, khát vọng của người phụ nữ tài năng không được trọng dụng, thể hiện tinh thần nữ quyền tiến bộ.",
  gia_tri_nghe_thuat: "Sử dụng nghệ thuật ẩn dụ tinh tế, ngôn ngữ giản dị nhưng hàm súc sâu sắc",
  hoang_canh: "Xã hội phong kiến Việt Nam cuối thế kỷ 18",
  cau_truc: "Bài thơ 4 câu"
})

CREATE (tg6)-[:SANG_TAC]->(tp6)
CREATE (tp6)-[:THUOC_THE_LOAI]->(tl4)
CREATE (tp6)-[:THUOC_THOI_KY]->(tk1)
CREATE (tp6)-[:NOI_VE {muc_do: "chính"}]->(cd2)
CREATE (tp6)-[:NOI_VE {muc_do: "phụ"}]->(cd7)
CREATE (tp6)-[:SU_DUNG {vi_du_cu_the: "Bánh trôi là ẩn dụ cho thân phận phụ nữ"}]->(bp2)

RETURN "Dữ liệu mẫu đã được tạo thành công!"
