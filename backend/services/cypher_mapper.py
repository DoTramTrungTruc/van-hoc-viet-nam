"""
Cypher Mapper - Ánh xạ ý định sang Cypher Query
Map intent từ NLP service sang Neo4j Cypher query
"""

from typing import Dict, List, Optional


class CypherMapper:
    """Ánh xạ intent sang Cypher query"""
    
    def __init__(self):
        pass
    
    def map_to_query(self, analysis: Dict) -> Dict:
        """
        Ánh xạ kết quả phân tích sang Cypher query
        
        Args:
            analysis: Kết quả từ NLPService
            
        Returns:
            Dict {query: str, params: dict, response_template: str}
        """
        intent = analysis['intent']
        entities = analysis['entities']
        keywords = analysis['keywords']
        
        # Route theo intent
        if intent == 'tim_tac_gia':
            return self._query_find_author(entities, keywords)
        elif intent == 'tim_nhan_vat':
            return self._query_find_characters(entities, keywords)
        elif intent == 'tim_tac_pham':
            return self._query_find_works(entities, keywords)
        elif intent == 'tim_the_loai':
            return self._query_find_genre(entities, keywords)
        elif intent == 'tim_quan_he':
            return self._query_find_relationship(entities, keywords)
        elif intent == 'tim_theo_thoi_ky':
            return self._query_find_by_period(entities, keywords)
        else:  # chi_tiet
            return self._query_get_details(entities, keywords)
    
    def _query_find_author(self, entities: List[str], keywords: List[str]) -> Dict:
        """Tìm tác giả của tác phẩm"""
        
        # Tìm tên tác phẩm trong entities
        tac_pham = self._find_work_name(entities)
        
        if tac_pham:
            query = """
            MATCH (tg:TacGia)-[:SANG_TAC]->(tp:TacPham {ten: $tac_pham})
            RETURN tg.ten as tac_gia, 
                   tp.ten as tac_pham,
                   tp.nam_sang_tac as nam_sang_tac,
                   tg.nam_sinh as nam_sinh,
                   tg.que_quan as que_quan
            """
            params = {'tac_pham': tac_pham}
            template = "Tác phẩm '{tac_pham}' do {tac_gia} sáng tác năm {nam_sang_tac}. {tac_gia} sinh năm {nam_sinh}, quê quán {que_quan}."
        else:
            # Không tìm thấy tác phẩm cụ thể
            query = """
            MATCH (tg:TacGia)-[:SANG_TAC]->(tp:TacPham)
            RETURN tg.ten as tac_gia, collect(tp.ten) as tac_pham
            LIMIT 5
            """
            params = {}
            template = "Các tác giả và tác phẩm: {results}"
        
        return {
            'query': query,
            'params': params,
            'template': template,
            'intent': 'tim_tac_gia'
        }
    
    def _query_find_characters(self, entities: List[str], keywords: List[str]) -> Dict:
        """Tìm nhân vật trong tác phẩm"""
        
        tac_pham = self._find_work_name(entities)
        
        if tac_pham:
            query = """
            MATCH (tp:TacPham {ten: $tac_pham})-[r:CO_NHAN_VAT]->(nv:NhanVat)
            RETURN tp.ten as tac_pham,
                   collect({ten: nv.ten, vai_tro: r.vai_tro}) as nhan_vat
            """
            params = {'tac_pham': tac_pham}
            template = "Các nhân vật trong '{tac_pham}': {nhan_vat}"
        else:
            query = """
            MATCH (nv:NhanVat)
            RETURN nv.ten as ten, nv.vai_tro as vai_tro
            LIMIT 10
            """
            params = {}
            template = "Các nhân vật: {results}"
        
        return {
            'query': query,
            'params': params,
            'template': template,
            'intent': 'tim_nhan_vat'
        }
    
    def _query_find_works(self, entities: List[str], keywords: List[str]) -> Dict:
        """Tìm tác phẩm của tác giả"""
        
        tac_gia = self._find_author_name(entities)
        
        if tac_gia:
            query = """
            MATCH (tg:TacGia {ten: $tac_gia})-[:SANG_TAC]->(tp:TacPham)
            OPTIONAL MATCH (tp)-[:THUOC_THE_LOAI]->(tl:TheLoai)
            RETURN tg.ten as tac_gia,
                   collect({ten: tp.ten, nam: tp.nam_sang_tac, the_loai: tl.ten}) as tac_pham
            """
            params = {'tac_gia': tac_gia}
            template = "Tác phẩm của {tac_gia}: {tac_pham}"
        else:
            query = """
            MATCH (tp:TacPham)
            RETURN tp.ten as ten, tp.nam_sang_tac as nam
            LIMIT 10
            """
            params = {}
            template = "Các tác phẩm: {results}"
        
        return {
            'query': query,
            'params': params,
            'template': template,
            'intent': 'tim_tac_pham'
        }
    
    def _query_find_genre(self, entities: List[str], keywords: List[str]) -> Dict:
        """Tìm tác phẩm theo thể loại"""
        
        tac_pham = self._find_work_name(entities)
        
        if tac_pham:
            # Tìm thể loại của tác phẩm
            query = """
            MATCH (tp:TacPham {ten: $tac_pham})-[:THUOC_THE_LOAI]->(tl:TheLoai)
            RETURN tp.ten as tac_pham, tl.ten as the_loai, tl.mo_ta as mo_ta
            """
            params = {'tac_pham': tac_pham}
            template = "'{tac_pham}' thuộc thể loại {the_loai}. {mo_ta}"
        else:
            # Tìm thể loại trong keywords
            the_loai = None
            for kw in keywords:
                if kw in ['thơ', 'tho', 'ca']:
                    the_loai = 'Thơ ca'
                elif kw in ['tiểu', 'tieu', 'thuyết', 'thuyet']:
                    the_loai = 'Tiểu thuyết'
                elif kw in ['truyện', 'truyen', 'ngắn', 'ngan']:
                    the_loai = 'Truyện ngắn'
            
            if the_loai:
                query = """
                MATCH (tp:TacPham)-[:THUOC_THE_LOAI]->(tl:TheLoai {ten: $the_loai})
                OPTIONAL MATCH (tg:TacGia)-[:SANG_TAC]->(tp)
                RETURN tp.ten as tac_pham, tg.ten as tac_gia, tp.nam_sang_tac as nam
                LIMIT 10
                """
                params = {'the_loai': the_loai}
                template = "Các tác phẩm thuộc thể loại {the_loai}: {results}"
            else:
                query = """
                MATCH (tl:TheLoai)
                RETURN tl.ten as ten, tl.mo_ta as mo_ta
                """
                params = {}
                template = "Các thể loại: {results}"
        
        return {
            'query': query,
            'params': params,
            'template': template,
            'intent': 'tim_the_loai'
        }
    
    def _query_find_relationship(self, entities: List[str], keywords: List[str]) -> Dict:
        """Tìm mối quan hệ giữa 2 nhân vật"""
        
        # Tìm 2 nhân vật
        nhan_vat = [e for e in entities if self._is_character(e)]
        
        if len(nhan_vat) >= 2:
            query = """
            MATCH (nv1:NhanVat {ten: $nv1})-[r:QUAN_HE]-(nv2:NhanVat {ten: $nv2})
            RETURN nv1.ten as nhan_vat_1, 
                   nv2.ten as nhan_vat_2,
                   r.loai as loai_quan_he,
                   r.mo_ta as mo_ta
            """
            params = {'nv1': nhan_vat[0], 'nv2': nhan_vat[1]}
            template = "Mối quan hệ giữa {nhan_vat_1} và {nhan_vat_2}: {loai_quan_he}. {mo_ta}"
        else:
            # Tìm tất cả quan hệ
            query = """
            MATCH (nv1:NhanVat)-[r:QUAN_HE]->(nv2:NhanVat)
            RETURN nv1.ten as nv1, nv2.ten as nv2, r.loai as loai
            LIMIT 10
            """
            params = {}
            template = "Các mối quan hệ: {results}"
        
        return {
            'query': query,
            'params': params,
            'template': template,
            'intent': 'tim_quan_he'
        }
    
    def _query_find_by_period(self, entities: List[str], keywords: List[str]) -> Dict:
        """Tìm tác phẩm theo thời kỳ/giai đoạn"""
        
        # Trích xuất năm từ keywords
        years = [int(k) for k in keywords if k.isdigit() and len(k) == 4]
        
        if len(years) >= 2:
            start_year = min(years)
            end_year = max(years)
            query = """
            MATCH (tp:TacPham)
            WHERE tp.nam_sang_tac >= $start_year AND tp.nam_sang_tac <= $end_year
            OPTIONAL MATCH (tg:TacGia)-[:SANG_TAC]->(tp)
            RETURN tp.ten as tac_pham, tg.ten as tac_gia, tp.nam_sang_tac as nam
            ORDER BY tp.nam_sang_tac
            """
            params = {'start_year': start_year, 'end_year': end_year}
            template = "Tác phẩm văn học giai đoạn {start_year}-{end_year}: {results}"
        else:
            query = """
            MATCH (tp:TacPham)
            WHERE tp.nam_sang_tac IS NOT NULL
            RETURN tp.ten as tac_pham, tp.nam_sang_tac as nam
            ORDER BY tp.nam_sang_tac
            LIMIT 20
            """
            params = {}
            template = "Các tác phẩm theo thời gian: {results}"
        
        return {
            'query': query,
            'params': params,
            'template': template,
            'intent': 'tim_theo_thoi_ky'
        }
    
    def _query_get_details(self, entities: List[str], keywords: List[str]) -> Dict:
        """Lấy thông tin chi tiết"""
        
        # Ưu tiên tác phẩm
        tac_pham = self._find_work_name(entities)
        if tac_pham:
            query = """
            MATCH (tg:TacGia)-[:SANG_TAC]->(tp:TacPham {ten: $ten})
            OPTIONAL MATCH (tp)-[:CO_NHAN_VAT]->(nv:NhanVat)
            OPTIONAL MATCH (tp)-[:THUOC_THE_LOAI]->(tl:TheLoai)
            RETURN tp.ten as ten,
                   tg.ten as tac_gia,
                   tp.nam_sang_tac as nam_sang_tac,
                   tp.noi_dung_tom_tat as noi_dung,
                   tp.y_nghia as y_nghia,
                   tl.ten as the_loai,
                   collect(DISTINCT nv.ten) as nhan_vat
            """
            params = {'ten': tac_pham}
            template = "Chi tiết tác phẩm '{ten}'"
            return {
                'query': query,
                'params': params,
                'template': template,
                'intent': 'chi_tiet'
            }
        
        # Tác giả
        tac_gia = self._find_author_name(entities)
        if tac_gia:
            query = """
            MATCH (tg:TacGia {ten: $ten})-[:SANG_TAC]->(tp:TacPham)
            RETURN tg.ten as ten,
                   tg.nam_sinh as nam_sinh,
                   tg.nam_mat as nam_mat,
                   tg.que_quan as que_quan,
                   tg.tieu_su as tieu_su,
                   collect(tp.ten) as tac_pham
            """
            params = {'ten': tac_gia}
            template = "Chi tiết tác giả '{ten}'"
            return {
                'query': query,
                'params': params,
                'template': template,
                'intent': 'chi_tiet'
            }
        
        # Default: search
        return {
            'query': "MATCH (n) RETURN n LIMIT 5",
            'params': {},
            'template': "Kết quả tìm kiếm: {results}",
            'intent': 'search'
        }
    
    # Helper methods
    
    def _find_work_name(self, entities: List[str]) -> Optional[str]:
        """Tìm tên tác phẩm trong entities"""
        work_names = [
            # 30 tác phẩm đầy đủ
            'Truyện Kiều', 'Văn tế nghĩa sĩ Cần Giuộc',
            'Chí Phèo', 'Lão Hạc', 'Sống mòn',
            'Tắt đèn', 'Số đỏ', 'Dumb Luck',
            'Vang bóng một thời', 'Chữ người tử tù',
            'Dế Mèn phiêu lưu ký', 'Cô bé bán diêm',
            'Bánh trôi nước', 'Quán Mị',
            'Vĩnh biệt', 'Gửi hương cho gió',
            'Việt Bắc', 'Từ ấy',
            'Tràng Giang', 'Hoàng hôn',
            'Nhà mẹ Lê', 'Nắng trong vườn',
            'Vợ nhặt', 'Làng',
            'Chiếc lược ngà', 'Cá trong nước, nước trong cá',
            'Tướng về hưu', 'Không có vua',
            'Mắt biếc', 'Tôi thấy hoa vàng trên cỏ xanh'
        ]
        
        # Ensure entities is a list
        if not isinstance(entities, list):
            return None
            
        for entity in entities:
            # Make sure entity is string
            if isinstance(entity, str) and entity in work_names:
                return entity
        return None
    
    def _find_author_name(self, entities: List[str]) -> Optional[str]:
        """Tìm tên tác giả trong entities"""
        author_names = [
            'Nguyễn Du', 'Nam Cao', 'Ngô Tất Tố', 'Vũ Trọng Phụng',
            'Nguyễn Tuân', 'Tô Hoài', 'Hồ Xuân Hương', 'Xuân Diệu',
            'Tố Hữu', 'Huy Cận', 'Thạch Lam', 'Kim Lân',
            'Nguyễn Minh Châu', 'Nguyễn Huy Thiệp', 'Nguyễn Nhật Ánh'
        ]
        
        # Ensure entities is a list
        if not isinstance(entities, list):
            return None
            
        for entity in entities:
            # Make sure entity is string
            if isinstance(entity, str) and entity in author_names:
                return entity
        return None
    
    def _is_character(self, entity: str) -> bool:
        """Kiểm tra có phải tên nhân vật không"""
        # Ensure entity is string
        if not isinstance(entity, str):
            return False
            
        character_names = [
            # Truyện Kiều
            'Thúy Kiều', 'Kim Trọng', 'Thúy Vân', 'Sở Khanh', 'Hoạn Thư',
            # Chí Phèo
            'Chí Phèo', 'Thị Nở',
            # Lão Hạc
            'Lão Hạc', 'Cậu Vàng',
            # Tắt đèn
            'Dũng', 'Hắc',
            # Số đỏ
            'Xuân Tóc Đỏ',
            # Dế Mèn
            'Dế Mèn',
            # Vợ nhặt
            'Tràng', 'Thị',
            # Mắt biếc
            'Ngạn', 'Hà Lan',
            # Tôi thấy hoa vàng trên cỏ xanh
            'Thiều', 'Tường'
        ]
        return entity in character_names


# Singleton instance
cypher_mapper = CypherMapper()