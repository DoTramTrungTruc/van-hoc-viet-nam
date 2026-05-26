"""
Neo4j Service
Lớp service để tương tác với cơ sở dữ liệu Neo4j
"""

from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Neo4jService:
    """Service class để tương tác với Neo4j database"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "ae54e57b"):
        """
        Khởi tạo kết nối Neo4j
        
        Args:
            uri: URI kết nối Neo4j (ví dụ: bolt://localhost:7687)
            user: Tên đăng nhập
            password: Mật khẩu
            database: Tên database (mặc định: neo4j)
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        logger.info(f"Đã kết nối đến Neo4j tại {uri}")
    
    def close(self):
        """Đóng kết nối"""
        if self.driver:
            self.driver.close()
            logger.info("Đã đóng kết nối Neo4j")
    
    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        """
        Thực thi một truy vấn Cypher
        
        Args:
            query: Câu truy vấn Cypher
            parameters: Tham số cho truy vấn
            
        Returns:
            Danh sách kết quả dạng dictionary
        """
        if parameters is None:
            parameters = {}
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters)
            return [dict(record) for record in result]
    
    def execute_write(self, query: str, parameters: Dict[str, Any] = None) -> Dict:
        """
        Thực thi truy vấn ghi (CREATE, UPDATE, DELETE)
        
        Args:
            query: Câu truy vấn Cypher
            parameters: Tham số cho truy vấn
            
        Returns:
            Kết quả của truy vấn
        """
        if parameters is None:
            parameters = {}
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters)
            record = result.single()
            return record if record else None

    
     
    def search_tac_gia(self, keyword: str) -> List[Dict]:
        query = """
        MATCH (t:TacGia)
        WHERE toLower(t.ten) CONTAINS toLower($keyword)
        OR toLower(t.que_quan) CONTAINS toLower($keyword)
        OR toLower(t.truong_phai) CONTAINS toLower($keyword)
        OR toLower(t.tieu_su) CONTAINS toLower($keyword)

        OPTIONAL MATCH (t)-[:SANG_TAC]->(tp:TacPham)

        RETURN 
            t.ten AS ten,
            t.nam_sinh AS nam_sinh,
            t.nam_mat AS nam_mat,
            t.que_quan AS que_quan,
            t.truong_phai AS truong_phai,
            collect(DISTINCT tp.ten) AS tac_pham
        LIMIT 20
        """
        return self.execute_query(query, {"keyword": keyword})

    
    
    # ===== TÁC PHẨM  tp.anh_dai_dien AS anh_dai_dien,=====
    
    def get_all_tac_pham(self, limit: int = 50) -> List[Dict]:
        """Lấy danh sách tất cả tác phẩm"""

        query = """
        MATCH (t:TacGia)-[:SANG_TAC]->(tp:TacPham)

        OPTIONAL MATCH (tp)-[:THUOC_THE_LOAI]->(tl:TheLoai)
        OPTIONAL MATCH (tp)-[:THUOC_GIAI_DOAN]->(gd:GiaiDoan)

        RETURN 
            tp.ten AS ten, 
            tp.anh_dai_dien AS anh_dai_dien,

            tp.nam_sang_tac AS nam_sang_tac,
            tp.nam_xuat_ban AS nam_xuat_ban,

            tp.noi_dung_tom_tat AS noi_dung_tom_tat,
            tp.chu_de_chinh AS chu_de_chinh,
            tp.y_nghia AS y_nghia,
            tp.gia_tri_nghe_thuat AS gia_tri_nghe_thuat,
            tp.hoan_canh AS hoan_canh,
            tp.cau_truc AS cau_truc,
            tp.trich_doan AS trich_doan,
            t.ten AS tac_gia,

            collect(DISTINCT tl.ten) AS the_loai,

            gd.ten AS giai_doan

        ORDER BY tp.nam_sang_tac
        LIMIT $limit
        """

        return self.execute_query(query, {"limit": limit})
    
    def search_tac_pham(self, keyword: str) -> List[Dict]:
        """Tìm kiếm tác phẩm theo tên hoặc nội dung"""
        query = """
        MATCH (tp:TacPham)
        WHERE toLower(tp.ten) CONTAINS toLower($keyword)
           OR toLower(tp.noi_dung_tom_tat) CONTAINS toLower($keyword)
        OPTIONAL MATCH (t:TacGia)-[:SANG_TAC]->(tp)
        RETURN tp.ten AS ten, tp.nam_sang_tac AS nam_sang_tac, 
               t.ten AS tac_gia, tp.noi_dung_tom_tat AS tom_tat
        LIMIT 20
        """
        return self.execute_query(query, {"keyword": keyword})
        #   # tp.anh_dai_dien AS anh_dai_dien, so_phan: nv.so_phan,
        #         y_nghia_dien_hinh: nv.y_nghia_dien_hinh,
        #         chi_tiet_ngoai_hinh: nv.chi_tiet_ngoai_hinh,
        #         chi_tiet_noi_tam: nv.chi_tiet_noi_tam
    def get_tac_pham_detail(self, ten_tac_pham: str) -> Optional[Dict]:
        """Lấy thông tin chi tiết tác phẩm"""
        # FIX chống None/map/object
        if not isinstance(ten_tac_pham, str):
            return None

        ten_tac_pham = ten_tac_pham.strip()

        query = """
        MATCH (t:TacGia)-[:SANG_TAC]->(tp:TacPham)
        WHERE toLower(trim(tp.ten)) = toLower(trim($ten))

        // ===== NHÂN VẬT =====
        OPTIONAL MATCH (tp)-[:CO_NHAN_VAT]->(nv:NhanVat)

        // ===== QUAN HỆ (chỉ trong tác phẩm này) =====
        OPTIONAL MATCH (tp)-[:CO_NHAN_VAT]->(nv1:NhanVat)
        OPTIONAL MATCH (tp)-[:CO_NHAN_VAT]->(nv2:NhanVat)
        OPTIONAL MATCH (nv1)-[r:QUAN_HE]->(nv2)

        // ===== THỂ LOẠI + KHÁC =====
        OPTIONAL MATCH (tp)-[:THUOC_THE_LOAI]->(tl:TheLoai)
        OPTIONAL MATCH (tp)-[:NOI_VE]->(cd:ChuDe)
        OPTIONAL MATCH (tp)-[:SU_DUNG]->(bp:BiPhap)
        OPTIONAL MATCH (tp)-[:THUOC_GIAI_DOAN]->(gd:GiaiDoan)

        WITH t, tp,

            // ===== NHÂN VẬT =====
            collect(DISTINCT {
                ten: nv.ten,
                vai_tro: nv.vai_tro,
                tinh_cach: nv.tinh_cach
            }) AS nhan_vat_raw,

            // ===== QUAN HỆ =====
            collect(DISTINCT {
                from: nv1.ten,
                to: nv2.ten,
                loai: r.loai
            }) AS quan_he_raw,

            collect(DISTINCT tl.ten) AS the_loai,
            collect(DISTINCT cd.ten) AS chu_de,
            collect(DISTINCT bp.ten) AS bi_phap,
            collect(DISTINCT gd.ten) AS giai_doan

        RETURN 
            tp.id AS id,
            t.ten AS tac_gia,
            tp.ten AS ten,
            tp.anh_dai_dien AS anh_dai_dien,
            tp.nam_sang_tac AS nam_sang_tac,
            tp.nam_xuat_ban AS nam_xuat_ban,   
            tp.noi_dung_tom_tat AS noi_dung_tom_tat,
            tp.chu_de_chinh AS chu_de_chinh,
            tp.y_nghia AS y_nghia,
            tp.gia_tri_nghe_thuat AS gia_tri_nghe_thuat,
            tp.hoan_canh AS hoan_canh,
            tp.cau_truc AS cau_truc,
            tp.trich_doan AS trich_doan,

            // ===== LỌC NULL =====
            [nv IN nhan_vat_raw WHERE nv.ten IS NOT NULL] AS nhan_vat,

            [qh IN quan_he_raw 
                WHERE qh.from IS NOT NULL 
                AND qh.to IS NOT NULL 
                AND qh.loai IS NOT NULL] AS quan_he,

            [tl IN the_loai WHERE tl IS NOT NULL] AS the_loai,
            [cd IN chu_de WHERE cd IS NOT NULL] AS chu_de,
            [bp IN bi_phap WHERE bp IS NOT NULL] AS bi_phap,
            [gd IN giai_doan WHERE gd IS NOT NULL] AS giai_doan
        """

        results = self.execute_query(query, {"ten": ten_tac_pham})
        return results[0] if results else None
    def get_tac_pham_by_the_loai(self, the_loai: str) -> List[Dict]:
        """Tìm tác phẩm theo thể loại"""
        query = """
        MATCH (tp:TacPham)-[:THUOC_THE_LOAI]->(tl:TheLoai {ten: $the_loai})
        OPTIONAL MATCH (t:TacGia)-[:SANG_TAC]->(tp)
        RETURN tp.ten AS ten, 
               tp.nam_sang_tac AS nam_sang_tac, 
               tp.noi_dung_tom_tat AS noi_dung_tom_tat,
               t.ten AS tac_gia,
               collect(DISTINCT tl.ten) AS the_loai
        """
        return self.execute_query(query, {"the_loai": the_loai})
    
    def get_tac_pham_by_chu_de(self, chu_de: str) -> List[Dict]:
        """Tìm tác phẩm theo chủ đề"""
        query = """
        MATCH (tp:TacPham)-[:NOI_VE]->(cd:ChuDe {ten: $chu_de})
        OPTIONAL MATCH (t:TacGia)-[:SANG_TAC]->(tp)
        RETURN tp.ten AS ten, tp.nam_sang_tac AS nam_sang_tac, t.ten AS tac_gia
        """
        return self.execute_query(query, {"chu_de": chu_de})
    
    # ===== NHÂN VẬT =====
    
    def get_nhan_vat_in_tac_pham(self, ten_tac_pham: str) -> List[Dict]:
        """Lấy danh sách nhân vật trong tác phẩm"""
        query = """
        MATCH (tp:TacPham {ten: $ten})-[:CO_NHAN_VAT]->(nv:NhanVat)
        RETURN nv.ten AS ten, nv.vai_tro AS vai_tro, 
               nv.tinh_cach AS tinh_cach, nv.so_phan AS so_phan,
               nv.y_nghia_dien_hinh AS y_nghia
        """
        return self.execute_query(query, {"ten": ten_tac_pham})
    
    def get_nhan_vat_relationships(self, ten_nhan_vat: str) -> List[Dict]:
        """Lấy mối quan hệ của nhân vật"""
        query = """
        MATCH (nv1:NhanVat {ten: $ten})-[r:QUAN_HE]->(nv2:NhanVat)
        RETURN nv1.ten AS tu_nhan_vat, r.loai AS loai_quan_he, 
               r.mo_ta AS mo_ta, nv2.ten AS den_nhan_vat
        """
        return self.execute_query(query, {"ten": ten_nhan_vat})
    
    # ===== THỂ LOẠI & CHỦ ĐỀ =====
    
    def get_all_the_loai(self) -> List[Dict]:
        """Lấy danh sách thể loại"""
        query = """
        MATCH (tl:TheLoai)
        RETURN tl.ten AS ten, tl.dac_diem AS dac_diem
        """
        return self.execute_query(query)
    
    def get_all_chu_de(self) -> List[Dict]:
        """Lấy danh sách chủ đề"""
        query = """
        MATCH (cd:ChuDe)
        RETURN cd.ten AS ten, cd.mo_ta AS mo_ta
        """
        return self.execute_query(query)
    
    # ===== THỐNG KÊ =====
   
    def get_tac_pham_by_the_loai_stats(self) -> List[Dict]:
        """Thống kê số tác phẩm theo thể loại"""
        query = """
        MATCH (tp:TacPham)-[:THUOC_THE_LOAI]->(tl:TheLoai)
        RETURN tl.ten AS the_loai, count(tp) AS so_luong
        ORDER BY so_luong DESC
        """
        return self.execute_query(query)
    
    # ===== ĐỒ THỊ VISUALIZATION =====
    
    def get_graph_data(self, ten_tac_pham: str) -> Dict:
        """Lấy dữ liệu đồ thị cho visualization"""
        query = """
        MATCH path = (t:TacGia)-[:SANG_TAC]->(tp:TacPham {ten: $ten})-[r]-(n)
        RETURN path
        LIMIT 50
        """
        
        results = self.execute_query(query, {"ten": ten_tac_pham})
        
        nodes = []
        edges = []
        node_ids = set()
        
        for record in results:
            path = record['path']
            # Process nodes and relationships from path
            # This will be handled in the frontend with vis.js
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    # ===== ADMIN - CRUD OPERATIONS    # anh_dai_dien: $anh_dai_dien,=====
    
    
    def create_tac_pham(self, data: Dict) -> Dict:
        try:
            # Tạo tác phẩm
            query = """
            MERGE (tg:TacGia {ten: $tac_gia})
            CREATE (tp:TacPham {
                ten: $ten,
                anh_dai_dien: $anh_dai_dien,
                nam_sang_tac: $nam_sang_tac,
                nam_xuat_ban: $nam_xuat_ban,
                giai_doan: $giai_doan,
                noi_dung_tom_tat: $noi_dung_tom_tat,
                chu_de_chinh: $chu_de_chinh,
                y_nghia: $y_nghia,
                gia_tri_nghe_thuat: $gia_tri_nghe_thuat,
                hoan_canh: $hoan_canh,
                cau_truc: $cau_truc,
                trich_doan: $trich_doan
            })
            CREATE (tg)-[:SANG_TAC]->(tp)
            RETURN tp
            """
            
            params = {
                'ten': data.get('ten'),
                'tac_gia': data.get('tac_gia'),
                'anh_dai_dien': data.get('anh_dai_dien', 'https://example.com/image.jpg'),
                'nam_sang_tac': data.get('nam_sang_tac'),
                'nam_xuat_ban': data.get('nam_xuat_ban'),
                'giai_doan': data.get('giai_doan', ''),
                'noi_dung_tom_tat': data.get('noi_dung_tom_tat', ''),
                'chu_de_chinh': data.get('chu_de_chinh', ''),
                'y_nghia': data.get('y_nghia', ''),
                'gia_tri_nghe_thuat': data.get('gia_tri_nghe_thuat', ''),
                'hoan_canh': data.get('hoan_canh', ''),
                'cau_truc': data.get('cau_truc', ''),
                'trich_doan': data.get('trich_doan', ''),
                'nhan_vat': data.get('nhan_vat', [])
            }
            
            result = self.execute_write(query, params)
            
            if not result:
                return None
            if data.get('the_loai'):
                    rel_query = """
                    MATCH (tp:TacPham {ten: $ten})
                    MERGE (tl:TheLoai {ten: $the_loai})
                    MERGE (tp)-[:THUOC_THE_LOAI]->(tl)
                    """
                    self.execute_write(rel_query, {
                        'ten': data.get('ten'),
                        'the_loai': data.get('the_loai')
                    })
            # ===== GIAI ĐOẠN =====
            if result and data.get('giai_doan'):
                giai_doan_query = """
                MATCH (tp:TacPham {ten: $tac_pham})
                MATCH (gd:GiaiDoan {ten: $giai_doan})
                MERGE (tp)-[:THUOC_GIAI_DOAN]->(gd)
                """
                
                self.execute_write(giai_doan_query, {
                    'tac_pham': data.get('ten'),
                    'giai_doan': data.get('giai_doan')
                })
            if result and data.get('nhan_vat'):
                nhan_vat_list = data.get('nhan_vat')
                if isinstance(nhan_vat_list, list):
                    for nv in nhan_vat_list:
                        if isinstance(nv, dict) and nv.get('ten'):
                            nhan_vat_query = """
                            MATCH (tp:TacPham {ten: $tac_pham})
                            MERGE (nv:NhanVat {ten: $ten_nhan_vat, tac_pham: $tac_pham})
                            ON CREATE SET 
                                nv.vai_tro = $vai_tro,
                                nv.tinh_cach = $tinh_cach
                            MERGE (tp)-[:CO_NHAN_VAT {vai_tro: $vai_tro}]->(nv)
                            """
                            
                            self.execute_write(nhan_vat_query, {
                            'tac_pham': data.get('ten'),
                            'ten_nhan_vat': nv.get('ten'),
                            'vai_tro': nv.get('vai_tro', 'Nhân vật chính'),
                            'tinh_cach': nv.get('tinh_cach', '')
                        })
            # ===== TẠO QUAN HỆ GIỮA NHÂN VẬT =====
            if result and data.get('nhan_vat'):
                nhan_vat_list = data.get('nhan_vat')
                
                for nv in nhan_vat_list:
                    if isinstance(nv.get('quan_he'), list):
                        for qh in nv.get('quan_he'):
                            if qh.get('voi'):
                                relation_query = """
                                MATCH (nv1:NhanVat {ten: $nv1, tac_pham: $tac_pham})
                                MERGE (nv2:NhanVat {ten: $nv2, tac_pham: $tac_pham})
                                MERGE (nv1)-[r:QUAN_HE {loai: $loai}]->(nv2)
                                SET r.mo_ta = $mo_ta
                                """
                                
                                self.execute_write(relation_query, {
                                    'nv1': nv.get('ten'),
                                    'nv2': qh.get('voi'),
                                    'loai': qh.get('loai', 'Liên quan'),
                                    'mo_ta': qh.get('mo_ta', ''),
                                    'tac_pham': data.get('ten')
                                })
            return dict(result['tp']) if result else None
        except Exception as e:
            logger.error(f"Lỗi tạo tác phẩm: {e}", exc_info=True)
            return None
                # tp.anh_dai_dien = COALESCE($anh_dai_dien, tp.anh_dai_dien),
    def update_tac_pham(self, ten: str, data: Dict) -> Dict:
        """Cập nhật thông tin tác phẩm"""
        query = """
        MATCH (tp:TacPham {ten: $ten})
        SET tp.nam_sang_tac = COALESCE($nam_sang_tac, tp.nam_sang_tac),
            tp.nam_xuat_ban = COALESCE($nam_xuat_ban, tp.nam_xuat_ban), 
            tp.anh_dai_dien = COALESCE($anh_dai_dien, tp.anh_dai_dien),
            tp.noi_dung_tom_tat = COALESCE($noi_dung_tom_tat, tp.noi_dung_tom_tat),
            tp.chu_de_chinh = COALESCE($chu_de_chinh, tp.chu_de_chinh),
            tp.y_nghia = COALESCE($y_nghia, tp.y_nghia),
            tp.gia_tri_nghe_thuat = COALESCE($gia_tri_nghe_thuat, tp.gia_tri_nghe_thuat),
            tp.hoan_canh = COALESCE($hoan_canh, tp.hoan_canh),
            tp.cau_truc = COALESCE($cau_truc, tp.cau_truc),
            tp.trich_doan = COALESCE($trich_doan, tp.trich_doan)
        RETURN tp
        """
        
        params = {"ten": ten, **data}
        result = self.execute_write(query, params)
        # Nếu có thể loại mới, update relationship
        if result and 'the_loai' in data and data['the_loai']:
            # Xóa relationship cũ
            delete_old = """
            MATCH (tp:TacPham {ten: $ten})-[r:THUOC_THE_LOAI]->()
            DELETE r
            """
            self.execute_write(delete_old, {'ten': ten})
            
            # Tạo relationship mới
            create_new = """
            MATCH (tp:TacPham {ten: $ten})
            MERGE (tl:TheLoai {ten: $the_loai})
            MERGE (tp)-[:THUOC_THE_LOAI]->(tl)
            WITH tl
            MATCH (tp2:TacPham)-[:THUOC_THE_LOAI]->(tl)
            WITH tl, count(tp2) AS total
            SET tl.so_luong_tac_pham = total
            """
            self.execute_write(create_new, {
                'ten': ten,
                'the_loai': data['the_loai']
            })
        # ===== UPDATE GIAI ĐOẠN =====
        if result and 'giai_doan' in data and data['giai_doan']:
            
            # Xóa cũ
            delete_old = """
            MATCH (tp:TacPham {ten: $ten})-[r:THUOC_GIAI_DOAN]->()
            DELETE r
            """
            self.execute_write(delete_old, {'ten': ten})
            
            # Tạo mới
            create_new = """
            MATCH (tp:TacPham {ten: $ten})
            MATCH (gd:GiaiDoan {ten: $giai_doan})
            MERGE (tp)-[:THUOC_GIAI_DOAN]->(gd)
            """
            self.execute_write(create_new, {
                'ten': ten,
                'giai_doan': data['giai_doan']
            })
        if result and 'tac_gia' in data and data['tac_gia']:
                change_author = """
                MATCH (tp:TacPham {ten: $ten})
                OPTIONAL MATCH (old:TacGia)-[r:SANG_TAC]->(tp)
                DELETE r
                WITH tp
                MATCH (new:TacGia {ten: $tac_gia})
                MERGE (new)-[:SANG_TAC]->(tp)
                """
                self.execute_write(change_author, {
                    "ten": ten,
                    "tac_gia": data['tac_gia']
                })
                
        if result and 'nhan_vat' in data and data['nhan_vat']:
        # Xóa relationship cũ với nhân vật
            delete_old_nv = """
            MATCH (tp:TacPham {ten: $ten})-[r:CO_NHAN_VAT]->()
            DELETE r
            """
            self.execute_write(delete_old_nv, {'ten': ten})
            
            # Tạo lại với nhân vật mới
            nhan_vat_list = data.get('nhan_vat')
            if isinstance(nhan_vat_list, list):
                for nv in nhan_vat_list:
                    if isinstance(nv, dict) and nv.get('ten'):
                        nhan_vat_query = """
                        MATCH (tp:TacPham {ten: $tac_pham})
                        MERGE (nv:NhanVat {ten: $ten_nhan_vat, tac_pham: $tac_pham})
                        SET 
                            nv.vai_tro = $vai_tro,
                            nv.tinh_cach = $tinh_cach
                        MERGE (tp)-[:CO_NHAN_VAT {vai_tro: $vai_tro}]->(nv)
                        """
                        
                        self.execute_write(nhan_vat_query, {
                        'tac_pham': data.get('ten'),
                        'ten_nhan_vat': nv.get('ten'),
                        'vai_tro': nv.get('vai_tro', 'Nhân vật chính'),
                        'tinh_cach': nv.get('tinh_cach', '')
                    })
            for nv in nhan_vat_list:
                if nv.get('quan_he'):
                    for qh in nv.get('quan_he'):
                        if qh.get('voi'):

                            self.execute_write("""
                            MATCH (nv1:NhanVat {ten: $nv1, tac_pham: $tac_pham})
                            MATCH (nv2:NhanVat {ten: $nv2, tac_pham: $tac_pham})
                            MERGE (nv1)-[r:QUAN_HE {loai: $loai}]->(nv2)
                            SET r.mo_ta = $mo_ta
                            """, {
                                'nv1': nv.get('ten'),
                                'nv2': qh.get('voi'),
                                'loai': qh.get('loai', 'Liên quan'),
                                'mo_ta': qh.get('mo_ta', ''),
                                'tac_pham': ten
                            })
        return dict(result['tp']) if result else None
    
    
    # ===== TÁC GIẢ =====
    
    def get_all_tac_gia(self) -> List[Dict]:
        """Lấy danh sách tất cả tác giả"""
        query = """
        MATCH (t:TacGia)
        RETURN t.ten AS ten, 
            t.anh_dai_dien AS anh_dai_dien, 
            t.nam_sinh AS nam_sinh, 
            t.nam_mat AS nam_mat, 
            t.que_quan AS que_quan, 
            t.truong_phai AS truong_phai,
            t.tieu_su AS tieu_su,
            t.but_danh AS but_danh,
            t.giai_thuong AS giai_thuong,
            t.cau_noi_noi_tieng AS cau_noi_noi_tieng
        ORDER BY t.nam_sinh
        """
        return self.execute_query(query)
    
     
    def get_tac_gia_detail(self, ten_tac_gia: str) -> Optional[Dict]:
        """Lấy thông tin chi tiết tác giả kèm tác phẩm"""
        query = """
        MATCH (t:TacGia {ten: $ten})
        OPTIONAL MATCH (t)-[:SANG_TAC]->(tp:TacPham)
        RETURN t.ten AS ten,
            t.anh_dai_dien AS anh_dai_dien,
            t.nam_sinh AS nam_sinh,
            t.nam_mat AS nam_mat,
            t.que_quan AS que_quan,
            t.truong_phai AS truong_phai,
            t.tieu_su AS tieu_su,
            t.but_danh AS but_danh,
            t.giai_thuong AS giai_thuong,
            t.cau_noi_noi_tieng AS cau_noi_noi_tieng,
               collect(DISTINCT tp.ten) AS tac_pham
        """
        results = self.execute_query(query, {"ten": ten_tac_gia})
        return results[0] if results else None
    
   
    # ===== THỐNG KÊ =====
    
    def get_statistics(self) -> Dict:
        """Lấy thống kê tổng quan"""
        queries = {
            "users": "MATCH (u:User) RETURN count(u) AS count",
            "tac_gia": "MATCH (t:TacGia) RETURN count(t) AS count",
            "tac_pham": "MATCH (tp:TacPham) RETURN count(tp) AS count",
            "nhan_vat": "MATCH (nv:NhanVat) RETURN count(nv) AS count",
            "the_loai": "MATCH (tl:TheLoai) RETURN count(tl) AS count"
        }
        
        stats = {}
        for key, query in queries.items():
            result = self.execute_query(query)
            stats[key] = result[0]['count'] if result else 0
        
        # Alias for admin.js compatibility
        stats['total_users'] = stats.get('users', 0)
        stats['total_tac_gia'] = stats.get('tac_gia', 0)
        stats['total_tac_pham'] = stats.get('tac_pham', 0)
        stats['total_nhan_vat'] = stats.get('nhan_vat', 0)
        
        return stats
    
    
    # ===== ADMIN - CRUD OPERATIONS anh_dai_dien: $anh_dai_dien, =====
    
    def create_tac_gia(self, data: Dict) -> Dict:
        """Tạo tác giả mới"""
        query = """
        CREATE (t:TacGia {
            ten: $ten,
            anh_dai_dien: $anh_dai_dien,
            nam_sinh: $nam_sinh,
            nam_mat: $nam_mat,
            que_quan: $que_quan,
            truong_phai: $truong_phai,
            tieu_su: $tieu_su,
            but_danh: $but_danh,
            giai_thuong: $giai_thuong,
            cau_noi_noi_tieng: $cau_noi_noi_tieng
        })
        RETURN t
        """
        result = self.execute_write(query, data)
        return dict(result['t']) if result else None

    def delete_tac_pham(self, ten: str) -> bool:
        try:
            # Check tồn tại + lấy thể loại
            check_query = """
            MATCH (tp:TacPham {ten: $ten})
            OPTIONAL MATCH (tp)-[:THUOC_THE_LOAI]->(tl:TheLoai)
            RETURN tp, tl.ten AS the_loai
            LIMIT 1
            """

            result = self.execute_query(check_query, {"ten": ten})

            if not result:
                return False

            the_loai_ten = result[0]["the_loai"]

            # Xóa tác phẩm
            delete_query = """
            MATCH (tp:TacPham {ten: $ten})
            WITH tp
            DETACH DELETE tp
            RETURN count(tp) AS deleted
            """

            delete_result = self.execute_write(delete_query, {"ten": ten})

            if not delete_result or delete_result["deleted"] == 0:
                return False

            # Update lại số lượng thể loại
            if the_loai_ten:
                update_query = """
                MATCH (tl:TheLoai {ten: $the_loai})
                OPTIONAL MATCH (tp:TacPham)-[:THUOC_THE_LOAI]->(tl)
                WITH tl, count(tp) AS total
                SET tl.so_luong_tac_pham = total
                """
                self.execute_write(update_query, {"the_loai": the_loai_ten})

            return True

        except Exception as e:
            logger.error(f"Lỗi khi xóa tác phẩm: {e}")
            return False
    # ===== USER MANAGEMENT METHODS =====
    
    def _convert_datetime(self, dt):
        """Convert Neo4j DateTime to timestamp or string"""
        if dt is None:
            return None
        # If it's a Neo4j DateTime, convert to ISO string
        if hasattr(dt, 'to_native'):
            return dt.to_native().isoformat()
        # If it's already a number (timestamp), return as is
        if isinstance(dt, (int, float)):
            return dt
        # If it's a datetime object
        if hasattr(dt, 'isoformat'):
            return dt.isoformat()
        return str(dt)
    
    def get_all_users(self):
        """Get all users (admin only)"""
        query = """
        MATCH (u:User)
        RETURN u.id AS id, u.username AS username, u.email AS email,
               u.full_name AS full_name, u.is_admin AS is_admin,
               u.is_active AS is_active, u.created_at AS created_at
        ORDER BY u.created_at DESC
        """
        
        result = self.execute_query(query)
        users = []
        for record in result:
            users.append({
                'id': record['id'],
                'username': record['username'],
                'email': record['email'],
                'full_name': record['full_name'],
                'is_admin': record['is_admin'],
                'is_active': record['is_active'],
                'created_at': self._convert_datetime(record['created_at'])
            })
        return users

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        query = """
        MATCH (u:User {id: $id})
        RETURN u.id AS id, u.username AS username, u.email AS email,
               u.full_name AS full_name, u.is_admin AS is_admin,
               u.is_active AS is_active, u.created_at AS created_at,
               u.password_hash AS password_hash
        """
        
        result = self.execute_query(query, {"id": user_id})
        if result:
            record = result[0]
            return {
                'id': record['id'],
                'username': record['username'],
                'email': record['email'],
                'full_name': record['full_name'],
                'is_admin': record['is_admin'],
                'is_active': record['is_active'],
                'created_at': self._convert_datetime(record['created_at']),
                'password_hash': record['password_hash']
            }
        return None

    def get_user_by_username(self, username):
        """Get user by username"""
        query = """
        MATCH (u:User {username: $username})
        RETURN u.id AS id, u.username AS username, u.email AS email,
               u.full_name AS full_name, u.is_admin AS is_admin,
               u.is_active AS is_active, u.password_hash AS password_hash
        """
        
        result = self.execute_query(query, {"username": username})
        if result:
            record = result[0]
            return {
                'id': record['id'],
                'username': record['username'],
                'email': record['email'],
                'full_name': record['full_name'],
                'is_admin': record['is_admin'],
                'is_active': record['is_active'],
                'password_hash': record['password_hash']
            }
        return None

    def get_user_by_email(self, email):
        """Get user by email"""
        query = """
        MATCH (u:User {email: $email})
        RETURN u.id AS id, u.username AS username, u.email AS email,
               u.full_name AS full_name, u.is_admin AS is_admin,
               u.is_active AS is_active
        """
        
        result = self.execute_query(query, {"email": email})
        if result:
            record = result[0]
            return {
                'id': record['id'],
                'username': record['username'],
                'email': record['email'],
                'full_name': record['full_name'],
                'is_admin': record['is_admin'],
                'is_active': record['is_active']
            }
        return None

    def create_user(self, user_data):
        """Create new user"""
        import time
        
        query = """
        MATCH (u:User)
        WITH COALESCE(MAX(u.id), 0) AS max_id
        CREATE (new:User {
            id: max_id + 1,
            username: $username,
            email: $email,
            full_name: $full_name,
            password_hash: $password_hash,
            role: $role,
            is_admin: $is_admin,
            is_active: $is_active,
            created_at: $created_at,
            last_login: null
        })
        RETURN new.id AS id, new.username AS username, new.email AS email,
               new.full_name AS full_name,new.role AS role, new.is_admin AS is_admin,
               new.is_active AS is_active, new.created_at AS created_at
        """
        
        params = {
            'username': user_data['username'],
            'email': user_data['email'],
            'full_name': user_data['full_name'],
            'password_hash': user_data['password_hash'],
            'role': 'admin' if user_data.get('is_admin', False) else 'user',
            'is_admin': user_data.get('is_admin', False),
            'is_active': user_data.get('is_active', True),
            'created_at': int(time.time() * 1000)
        }
        
        result = self.execute_query(query, params)
        if result and len(result) > 0:
            record = result[0]
            return {
                'id': record['id'],
                'username': record['username'],
                'email': record['email'],
                'full_name': record['full_name'],
                'role': record['role'],
                'is_admin': record['is_admin'],
                'is_active': record['is_active'],
                'created_at': self._convert_datetime(record['created_at'])
            }
        return None

    def update_user(self, user_id, update_data):
        """Update user"""
        try:
            # Build SET clause dynamically
            set_clauses = []
            params = {'id': user_id}
            
            for key, value in update_data.items():
                set_clauses.append(f"u.{key} = ${key}")
                params[key] = value
            
            if not set_clauses:
                logger.warning(f"update_user called with empty update_data for user {user_id}")
                return None
            
            query = f"""
            MATCH (u:User {{id: $id}})
            SET {', '.join(set_clauses)}
            RETURN u.id AS id, u.username AS username, u.email AS email,
                   u.full_name AS full_name, u.is_admin AS is_admin,
                   u.is_active AS is_active, u.created_at AS created_at
            """
            
            result = self.execute_query(query, params)
            if result and len(result) > 0:
                record = result[0]
                return {
                    'id': record['id'],
                    'username': record['username'],
                    'email': record['email'],
                    'full_name': record['full_name'],
                    'is_admin': record['is_admin'],
                    'is_active': record['is_active'],
                    'created_at': self._convert_datetime(record['created_at'])
                }
            else:
                logger.error(f"User {user_id} not found in database")
                return None
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}", exc_info=True)
            return None
        
    def delete_user(self, user_id):
        """Delete user"""
        try:
            # Check user exists first
            check_query = "MATCH (u:User {id: $id}) RETURN u"
            check_result = self.execute_query(check_query, {"id": user_id})
            
            if not check_result:
                logger.warning(f"User {user_id} not found for deletion")
                return False
            
            # Delete user
            delete_query = """
            MATCH (u:User {id: $id})
            DETACH DELETE u
            """
            
            self.execute_query(delete_query, {"id": user_id})
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}", exc_info=True)
            return False
   # ===== RESET PASSWORD TOKEN =====

    def save_reset_token(self, email: str, token: str, expire_ms: int) -> bool:
        """Lưu reset token vào node User"""
        query = """
        MATCH (u:User {email: $email})
        SET u.reset_token        = $token,
            u.reset_token_expire = $expire_ms
        RETURN u.email AS email
        """
        result = self.execute_query(query, {
            "email":     email,
            "token":     token,
            "expire_ms": expire_ms
        })
        return bool(result)

    def get_user_by_reset_token(self, token: str) -> Optional[Dict]:
        """Tìm user theo reset token (chưa hết hạn)"""
        import time
        now = int(time.time() * 1000)
        query = """
        MATCH (u:User {reset_token: $token})
        WHERE u.reset_token_expire >= $now
        RETURN u.id         AS id,
               u.email      AS email,
               u.username   AS username,
               u.full_name  AS full_name
        """
        result = self.execute_query(query, {"token": token, "now": now})
        return result[0] if result else None

    def clear_reset_token(self, token: str) -> bool:
        """Xóa reset token sau khi dùng"""
        query = """
        MATCH (u:User {reset_token: $token})
        REMOVE u.reset_token, u.reset_token_expire
        RETURN u.email AS email
        """
        result = self.execute_query(query, {"token": token})
        return bool(result)

    def update_password(self, user_id: int, password_hash: str) -> bool:
        """Cập nhật mật khẩu mới"""
        query = """
        MATCH (u:User {id: $id})
        SET u.password_hash = $hash
        RETURN u.id AS id
        """
        result = self.execute_query(query, {"id": user_id, "hash": password_hash})
        return bool(result)
    def execute_read(self, query, params=None):

        with self.driver.session(database=self.database) as session:

            result = session.run(query, params or {})

            return [record.data() for record in result]

 
