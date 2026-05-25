// ===== TẠO CÁC THỂ LOẠI PHỔ BIẾN =====

// Thơ ca
CREATE (tl1:TheLoai {
  ten: 'Thơ ca',
  mo_ta: 'Thể loại văn học sử dụng vần điệu, nhịp điệu để diễn tả tình cảm, tư tưởng',
  so_luong_tac_pham: 0
});

// Tiểu thuyết
CREATE (tl2:TheLoai {
  ten: 'Tiểu thuyết',
  mo_ta: 'Tác phẩm văn xuôi dài, có cốt truyện phức tạp, nhiều nhân vật',
  so_luong_tac_pham: 0
});

// Truyện ngắn
CREATE (tl3:TheLoai {
  ten: 'Truyện ngắn',
  mo_ta: 'Tác phẩm văn xuôi ngắn, tập trung vào một sự kiện hoặc nhân vật chính',
  so_luong_tac_pham: 0
});

// Kịch
CREATE (tl4:TheLoai {
  ten: 'Kịch',
  mo_ta: 'Văn học viết để diễn xuất trên sân khấu, có đối thoại và hành động',
  so_luong_tac_pham: 0
});

// Tản văn
CREATE (tl5:TheLoai {
  ten: 'Tản văn',
  mo_ta: 'Văn xuôi tự do, thường miêu tả tâm trạng, suy nghĩ của tác giả',
  so_luong_tac_pham: 0
});

// Trường ca
CREATE (tl6:TheLoai {
  ten: 'Trường ca',
  mo_ta: 'Thơ dài kể chuyện, có cốt truyện hoàn chỉnh',
  so_luong_tac_pham: 0
});

RETURN tl1, tl2, tl3, tl4, tl5, tl6;


// ===== GẮN THỂ LOẠI CHO TÁC PHẨM CÓ SẴN =====

// Truyện Kiều -> Trường ca
MATCH (tp:TacPham {ten: 'Truyện Kiều'})
MATCH (tl:TheLoai {ten: 'Trường ca'})
MERGE (tp)-[:THUOC_THE_LOAI]->(tl);

// Chí Phèo -> Truyện ngắn
MATCH (tp:TacPham {ten: 'Chí Phèo'})
MATCH (tl:TheLoai {ten: 'Truyện ngắn'})
MERGE (tp)-[:THUOC_THE_LOAI]->(tl);

// Tắt đèn -> Tiểu thuyết
MATCH (tp:TacPham {ten: 'Tắt đèn'})
MATCH (tl:TheLoai {ten: 'Tiểu thuyết'})
MERGE (tp)-[:THUOC_THE_LOAI]->(tl);

// Vợ nhặt -> Truyện ngắn
MATCH (tp:TacPham {ten: 'Vợ nhặt'})
MATCH (tl:TheLoai {ten: 'Truyện ngắn'})
MERGE (tp)-[:THUOC_THE_LOAI]->(tl);

// Việt Bắc -> Thơ ca
MATCH (tp:TacPham {ten: 'Việt Bắc'})
MATCH (tl:TheLoai {ten: 'Thơ ca'})
MERGE (tp)-[:THUOC_THE_LOAI]->(tl);

// Bánh trôi nước -> Thơ ca
MATCH (tp:TacPham {ten: 'Bánh trôi nước'})
MATCH (tl:TheLoai {ten: 'Thơ ca'})
MERGE (tp)-[:THUOC_THE_LOAI]->(tl);


// ===== CẬP NHẬT SỐ LƯỢNG TÁC PHẨM =====

MATCH (tl:TheLoai)
OPTIONAL MATCH (tp:TacPham)-[:THUOC_THE_LOAI]->(tl)
WITH tl, count(tp) as count
SET tl.so_luong_tac_pham = count
RETURN tl.ten, tl.so_luong_tac_pham;
