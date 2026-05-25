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
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
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
            return dict(record) if record else None
    
    # ===== TÁC GIẢ =====
    
    def get_all_tac_gia(self) -> List[Dict]:
        """Lấy danh sách tất cả tác giả"""
        query = """
        MATCH (t:TacGia)
        RETURN t.ten AS ten, t.nam_sinh AS nam_sinh, t.nam_mat AS nam_mat, 
               t.que_quan AS que_quan, t.truong_phai AS truong_phai
        ORDER BY t.nam_sinh
        """
        return self.execute_query(query)
    
    def search_tac_gia(self, keyword: str) -> List[Dict]:
        """Tìm kiếm tác giả theo tên"""
        query = """
        MATCH (t:TacGia)
        WHERE toLower(t.ten) CONTAINS toLower($keyword)
        RETURN t
        """
        results = self.execute_query(query, {"keyword": keyword})
        return [record['t'] for record in results]
    
    def get_tac_gia_detail(self, ten_tac_gia: str) -> Optional[Dict]:
        """Lấy thông tin chi tiết tác giả kèm tác phẩm"""
        query = """
        MATCH (t:TacGia {ten: $ten})
        OPTIONAL MATCH (t)-[:SANG_TAC]->(tp:TacPham)
        RETURN t.ten AS ten, t.nam_sinh AS nam_sinh, t.nam_mat AS nam_mat,
               t.que_quan AS que_quan, t.truong_phai AS truong_phai,
               t.tieu_su AS tieu_su,
               collect(DISTINCT tp.ten) AS tac_pham
        """
        results = self.execute_query(query, {"ten": ten_tac_gia})
        return results[0] if results else None
    
    # ===== TÁC PHẨM =====
    
    def get_all_tac_pham(self, limit: int = 50) -> List[Dict]:
        """Lấy danh sách tất cả tác phẩm"""
        query = """
        MATCH (t:TacGia)-[:SANG_TAC]->(tp:TacPham)
        OPTIONAL MATCH (tp)-[:THUOC_THE_LOAI]->(tl:TheLoai)
        RETURN tp.ten AS ten, 
               tp.anh_dai_dien AS anh_dai_dien,
               tp.nam_sang_tac AS nam_sang_tac, 
               tp.noi_dung_tom_tat AS noi_dung_tom_tat,
               t.ten AS tac_gia,
               collect(DISTINCT tl.ten) AS the_loai
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
    
    def get_tac_pham_detail(self, ten_tac_pham: str) -> Optional[Dict]:
        """Lấy thông tin chi tiết tác phẩm"""
        query = """
        MATCH (t:TacGia)-[:SANG_TAC]->(tp:TacPham {ten: $ten})
        OPTIONAL MATCH (tp)-[:CO_NHAN_VAT]->(nv:NhanVat)
        OPTIONAL MATCH (tp)-[:THUOC_THE_LOAI]->(tl:TheLoai)
        OPTIONAL MATCH (tp)-[:NOI_VE]->(cd:ChuDe)
        OPTIONAL MATCH (tp)-[:SU_DUNG]->(bp:BiPhap)
        OPTIONAL MATCH (tp)-[:THUOC_GIAI_DOAN]->(gd:GiaiDoan)
        RETURN t.ten AS tac_gia,
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
               collect(DISTINCT {ten: nv.ten, vai_tro: nv.vai_tro, tinh_cach: nv.tinh_cach}) AS nhan_vat,
               collect(DISTINCT tl.ten) AS the_loai,
               collect(DISTINCT cd.ten) AS chu_de,
               collect(DISTINCT bp.ten) AS bi_phap,
               collect(DISTINCT gd.ten) AS giai_doan
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
    
    # ===== ADMIN - CRUD OPERATIONS =====
    
    def create_tac_gia(self, data: Dict) -> Dict:
        """Tạo tác giả mới"""
        try:
            query = """
            CREATE (t:TacGia {
                ten: $ten,
                anh_dai_dien: $anh_dai_dien,
                nam_sinh: $nam_sinh,
                nam_mat: $nam_mat,
                que_quan: $que_quan,
                truong_phai: $truong_phai,
                tieu_su: $tieu_su
            })
            RETURN t
            """
            
            params = dict(data)
            params['anh_dai_dien'] = data.get('anh_dai_dien', 'https://via.placeholder.com/300x300/D2691E/ffffff?text=Tac+Gia')
            
            result = self.execute_query(query, params)
            if result and len(result) > 0:
                return dict(result[0]['t'])
            return None
        except Exception as e:
            logger.error(f"Lỗi tạo tác giả: {e}", exc_info=True)
            return None
    
    def create_tac_pham(self, data: Dict) -> Dict:
        """Tạo tác phẩm mới"""
        try:
            # Tạo tác phẩm
            query = """
            MATCH (tg:TacGia {ten: $tac_gia})
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
                nhan_vat: $nhan_vat
            })
            CREATE (tg)-[:SANG_TAC]->(tp)
            RETURN tp
            """
            
            params = {
                'ten': data.get('ten'),
                'tac_gia': data.get('tac_gia'),
                'anh_dai_dien': data.get('anh_dai_dien', 'https://via.placeholder.com/300x400/8B4513/ffffff?text=Tac+Pham'),
                'nam_sang_tac': data.get('nam_sang_tac'),
                'nam_xuat_ban': data.get('nam_xuat_ban'),
                'giai_doan': data.get('giai_doan', ''),
                'noi_dung_tom_tat': data.get('noi_dung_tom_tat', ''),
                'chu_de_chinh': data.get('chu_de_chinh', ''),
                'y_nghia': data.get('y_nghia', ''),
                'gia_tri_nghe_thuat': data.get('gia_tri_nghe_thuat', ''),
                'hoan_canh': data.get('hoan_canh', ''),
                'cau_truc': data.get('cau_truc', ''),
                'nhan_vat': data.get('nhan_vat', [])
            }
            
            result = self.execute_write(query, params)
            
            if not result:
                return None
            
            # Tạo relationship với thể loại nếu có
            if data.get('the_loai'):
                rel_query = """
                MATCH (tp:TacPham {ten: $ten})
                MATCH (tl:TheLoai {ten: $the_loai})
                MERGE (tp)-[:THUOC_THE_LOAI]->(tl)
                """
                self.execute_write(rel_query, {
                    'ten': data.get('ten'),
                    'the_loai': data.get('the_loai')
                })
            
            # Tạo relationship với giai đoạn nếu có
            if data.get('giai_doan'):
                gd_query = """
                MATCH (tp:TacPham {ten: $ten})
                MATCH (gd:GiaiDoan {ten: $giai_doan})
                MERGE (tp)-[:THUOC_GIAI_DOAN]->(gd)
                """
                self.execute_write(gd_query, {
                    'ten': data.get('ten'),
                    'giai_doan': data.get('giai_doan')
                })
            
            return dict(result['tp']) if result else None
            
        except Exception as e:
            logger.error(f"Lỗi tạo tác phẩm: {e}", exc_info=True)
            return None
    
    def update_tac_pham(self, ten: str, data: Dict) -> Dict:
        """Cập nhật thông tin tác phẩm"""
        try:
            # UPDATE query chính
            update_query = """
            MATCH (tp:TacPham {ten: $ten})
            SET tp.nam_sang_tac = COALESCE($nam_sang_tac, tp.nam_sang_tac),
                tp.nam_xuat_ban = COALESCE($nam_xuat_ban, tp.nam_xuat_ban),
                tp.anh_dai_dien = COALESCE($anh_dai_dien, tp.anh_dai_dien),
                tp.noi_dung_tom_tat = COALESCE($noi_dung_tom_tat, tp.noi_dung_tom_tat),
                tp.chu_de_chinh = COALESCE($chu_de_chinh, tp.chu_de_chinh),
                tp.y_nghia = COALESCE($y_nghia, tp.y_nghia),
                tp.gia_tri_nghe_thuat = COALESCE($gia_tri_nghe_thuat, tp.gia_tri_nghe_thuat),
                tp.hoan_canh = COALESCE($hoan_canh, tp.hoan_canh),
                tp.cau_truc = COALESCE($cau_truc, tp.cau_truc)
            RETURN tp
            """
            
            params = {"ten": ten, **data}
            result = self.execute_write(update_query, params)
            
            # Update tác giả nếu có
            if result and 'tac_gia' in data and data['tac_gia']:
                # Xóa relationship cũ
                self.execute_write("""
                    MATCH (tp:TacPham {ten: $ten})
                    OPTIONAL MATCH (old:TacGia)-[r:SANG_TAC]->(tp)
                    DELETE r
                """, {"ten": ten})
                
                # Tạo relationship mới
                self.execute_write("""
                    MATCH (tp:TacPham {ten: $ten})
                    MATCH (new:TacGia {ten: $tac_gia})
                    MERGE (new)-[:SANG_TAC]->(tp)
                """, {
                    "ten": ten,
                    "tac_gia": data['tac_gia']
                })
            
            # Update thể loại nếu có
            if result and 'the_loai' in data and data['the_loai']:
                # Xóa relationship cũ
                self.execute_write("""
                    MATCH (tp:TacPham {ten: $ten})-[r:THUOC_THE_LOAI]->()
                    DELETE r
                """, {'ten': ten})
                
                # Tạo relationship mới
                self.execute_write("""
                    MATCH (tp:TacPham {ten: $ten})
                    MERGE (tl:TheLoai {ten: $the_loai})
                    MERGE (tp)-[:THUOC_THE_LOAI]->(tl)
                    WITH tl
                    MATCH (tp2:TacPham)-[:THUOC_THE_LOAI]->(tl)
                    WITH tl, count(tp2) AS total
                    SET tl.so_luong_tac_pham = total
                """, {
                    'ten': ten,
                    'the_loai': data['the_loai']
                })
            
            # Update giai đoạn nếu có
            if result and 'giai_doan' in data and data['giai_doan']:
                # Xóa relationship cũ
                self.execute_write("""
                    MATCH (tp:TacPham {ten: $ten})-[r:THUOC_GIAI_DOAN]->()
                    DELETE r
                """, {'ten': ten})
                
                # Tạo relationship mới
                self.execute_write("""
                    MATCH (tp:TacPham {ten: $ten})
                    MATCH (gd:GiaiDoan {ten: $giai_doan})
                    MERGE (tp)-[:THUOC_GIAI_DOAN]->(gd)
                """, {
                    'ten': ten,
                    'giai_doan': data['giai_doan']
                })
            
            # Update nhân vật nếu có
            if result and 'nhan_vat' in data and data['nhan_vat']:
                # Xóa relationship cũ
                self.execute_write("""
                    MATCH (tp:TacPham {ten: $ten})-[r:CO_NHAN_VAT]->()
                    DELETE r
                """, {'ten': ten})
                
                # Tạo lại với nhân vật mới
                nhan_vat_list = data.get('nhan_vat')
                if isinstance(nhan_vat_list, list):
                    for nv in nhan_vat_list:
                        if isinstance(nv, dict) and nv.get('ten'):
                            self.execute_write("""
                                MATCH (tp:TacPham {ten: $tac_pham})
                                MERGE (nv:NhanVat {ten: $ten_nhan_vat})
                                SET 
                                    nv.vai_tro = $vai_tro,
                                    nv.tinh_cach = $tinh_cach
                                MERGE (tp)-[:CO_NHAN_VAT {vai_tro: $vai_tro}]->(nv)
                            """, {
                                'tac_pham': ten,
                                'ten_nhan_vat': nv.get('ten'),
                                'vai_tro': nv.get('vai_tro', 'Nhân vật chính'),
                                'tinh_cach': nv.get('tinh_cach', '')
                            })
            
            return dict(result['tp']) if result else None
            
        except Exception as e:
            logger.error(f"Lỗi update tác phẩm {ten}: {e}", exc_info=True)
            return None
    
    def delete_tac_pham(self, ten: str) -> bool:
        """Xóa tác phẩm"""
        query = """
        MATCH (tp:TacPham {ten: $ten})
        DETACH DELETE tp
        """
        try:
            self.execute_query(query, {"ten": ten})
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
               new.full_name AS full_name, new.role AS role, new.is_admin AS is_admin,
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
        if result:
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