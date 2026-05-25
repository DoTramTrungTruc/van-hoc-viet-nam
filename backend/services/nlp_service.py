"""
NLP Service - Xử lý ngôn ngữ tự nhiên tiếng Việt
Phân tích câu hỏi, trích xuất từ khóa, nhận diện ý định
Phiên bản: 2.0 - Cập nhật đầy đủ 30 tác phẩm văn học Việt Nam
"""

from underthesea import word_tokenize, pos_tag
import re
from typing import Dict, List, Optional


class NLPService:
    """Service xử lý câu hỏi tiếng Việt - Database: 30 tác phẩm, 15 tác giả"""
    
    def __init__(self):
        # Từ khóa văn học (whitelist) - 15 tác giả, 30 tác phẩm
        self.literature_keywords = [
            # Từ khóa chung
            'tác giả', 'tác phẩm', 'sáng tác', 'viết', 'nhân vật',
            'thể loại', 'truyện', 'thơ', 'văn', 'sách', 'tiểu thuyết',
            'văn học', 'văn xuôi', 'ca dao', 'tục ngữ', 'quan hệ',
            'ý nghĩa', 'nội dung', 'giai đoạn', 'thời kỳ', 'năm',
            
            # 15 Tác giả
            'nguyễn du', 'nam cao', 'ngô tất tố', 'vũ trọng phụng',
            'nguyễn tuân', 'tô hoài', 'hồ xuân hương', 'xuân diệu',
            'tố hữu', 'huy cận', 'thạch lam', 'kim lân',
            'nguyễn minh châu', 'nguyễn huy thiệp', 'nguyễn nhật ánh',
            
            # 30 Tác phẩm (từ khóa ngắn để dễ nhận diện)
            'kiều', 'truyện kiều', 'văn tế', 'cần giuộc', 'văn tế nghĩa sĩ',
            'chí phèo', 'phèo', 'lão hạc', 'hạc', 'sống mòn',
            'tắt đèn', 'số đỏ', 'dumb luck',
            'vang bóng', 'chữ người tử tù',
            'dế mèn', 'mèn', 'cô bé bán diêm',
            'bánh trôi', 'quán mị',
            'vĩnh biệt', 'gửi hương',
            'việt bắc', 'từ ấy',
            'tràng giang', 'hoàng hôn',
            'nhà mẹ lê', 'nắng trong vườn',
            'vợ nhặt', 'làng',
            'chiếc lược', 'lược ngà',
            'cá trong nước', 'nước trong cá',
            'tướng về hưu', 'không có vua',
            'mắt biếc', 'hoa vàng', 'cỏ xanh'
        ]
        
        # Từ khóa spam/không hợp lệ (blacklist)
        self.spam_keywords = [
            'casino', 'viagra', 'porn', 'sex', 'xxx',
            'click here', 'buy now', 'loan', 'credit',
            'http://', 'https://', 'www.', '.com', '.net'
        ]
        
        # Từ khóa nhận diện ý định
        self.intent_keywords = {
            'tim_tac_gia': ['ai', 'tác giả', 'người viết', 'sáng tác', 'do ai'],
            'tim_nhan_vat': ['nhân vật', 'người', 'ai xuất hiện', 'các nhân vật'],
            'tim_tac_pham': ['tác phẩm', 'sách', 'truyện', 'thơ', 'viết gì', 'có tác phẩm nào'],
            'tim_the_loai': ['thể loại', 'thuộc loại', 'là gì'],
            'tim_quan_he': ['mối quan hệ', 'quan hệ', 'liên quan', 'giữa'],
            'tim_theo_thoi_ky': ['thời kỳ', 'giai đoạn', 'năm', 'thế kỷ'],
            'chi_tiet': ['chi tiết', 'thông tin', 'giới thiệu', 'về']
        }
        
        # Stopwords tiếng Việt đơn giản
        self.stopwords = set([
            'là', 'của', 'và', 'có', 'trong', 'được', 'với', 'cho', 
            'từ', 'theo', 'về', 'các', 'những', 'này', 'đó', 'nào',
            'gì', 'như', 'thế', 'hay', 'hoặc', '?', '.'
        ])
    
    def analyze_question(self, question: str) -> Dict:
        """
        Phân tích câu hỏi
        
        Args:
            question: Câu hỏi của người dùng
            
        Returns:
            Dict chứa: intent, entities, keywords, is_valid, error_message
        """
        # BƯỚC 1: VALIDATE câu hỏi
        validation = self.validate_question(question)
        
        if not validation['is_valid']:
            return {
                'is_valid': False,
                'error_message': validation['error_message'],
                'error_type': validation['error_type'],
                'suggestions': validation.get('suggestions', [])
            }
        
        # BƯỚC 2: Chuẩn hóa
        question = question.strip().lower()
        
        # BƯỚC 3: Nhận diện ý định
        intent = self._detect_intent(question)
        
        # BƯỚC 4: Trích xuất entities (tên riêng)
        entities = self._extract_entities(question)
        
        # BƯỚC 5: Trích xuất keywords
        keywords = self._extract_keywords(question)
        
        return {
            'is_valid': True,
            'intent': intent,
            'entities': entities,
            'keywords': keywords,
            'original_question': question
        }
    
    def validate_question(self, question: str) -> Dict:
        """
        Validate câu hỏi trước khi xử lý
        
        Returns:
            Dict {is_valid: bool, error_message: str, error_type: str}
        """
        # 1. Kiểm tra rỗng
        if not question or not question.strip():
            return {
                'is_valid': False,
                'error_message': 'Vui lòng nhập câu hỏi!',
                'error_type': 'empty'
            }
        
        question = question.strip()
        
        # 2. Kiểm tra độ dài tối thiểu
        if len(question) < 5:
            return {
                'is_valid': False,
                'error_message': 'Câu hỏi quá ngắn! Vui lòng nhập câu hỏi đầy đủ hơn.',
                'error_type': 'too_short',
                'suggestions': [
                    'Truyện Kiều do ai sáng tác?',
                    'Nhân vật nào trong Chí Phèo?'
                ]
            }
        
        # 3. Kiểm tra độ dài tối đa
        if len(question) > 500:
            return {
                'is_valid': False,
                'error_message': 'Câu hỏi quá dài! Vui lòng rút gọn câu hỏi.',
                'error_type': 'too_long'
            }
        
        # 4. Kiểm tra spam keywords
        question_lower = question.lower()
        for spam_word in self.spam_keywords:
            if spam_word in question_lower:
                return {
                    'is_valid': False,
                    'error_message': 'Câu hỏi chứa nội dung không phù hợp!',
                    'error_type': 'spam'
                }
        
        # 5. Kiểm tra ký tự đặc biệt quá nhiều
        special_chars = sum(1 for c in question if not c.isalnum() and c not in ' ?,.-')
        if special_chars > len(question) * 0.3:  # >30% ký tự đặc biệt
            return {
                'is_valid': False,
                'error_message': 'Câu hỏi chứa quá nhiều ký tự đặc biệt!',
                'error_type': 'invalid_chars'
            }
        
        # 6. Kiểm tra có liên quan đến văn học không
        if not self._is_literature_related(question_lower):
            return {
                'is_valid': False,
                'error_message': 'Câu hỏi không liên quan đến văn học Việt Nam. Vui lòng hỏi về tác giả, tác phẩm, nhân vật văn học.',
                'error_type': 'irrelevant',
                'suggestions': [
                    'Nguyễn Du có tác phẩm nào?',
                    'Truyện Kiều nói về điều gì?',
                    'Các nhân vật trong Chí Phèo?'
                ]
            }
        
        # 7. Kiểm tra có phải tiếng Việt không (đơn giản)
        vietnamese_chars = 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
        has_vietnamese = any(c in question_lower for c in vietnamese_chars)
        has_alphabet = any(c.isalpha() for c in question_lower)
        
        if has_alphabet and not has_vietnamese:
            # Kiểm tra xem có phải câu tiếng Anh về văn học không
            english_literature_keywords = ['who', 'author', 'write', 'character', 'story', 'novel']
            if any(kw in question_lower for kw in english_literature_keywords):
                return {
                    'is_valid': False,
                    'error_message': 'Vui lòng đặt câu hỏi bằng tiếng Việt!',
                    'error_type': 'wrong_language',
                    'suggestions': ['Truyện Kiều do ai sáng tác?']
                }
        
        # 8. Kiểm tra có động từ hỏi không
        question_words = ['ai', 'gì', 'nào', 'đâu', 'bao nhiêu', 'khi nào', 'như thế nào', 'tại sao', 'vì sao']
        has_question_word = any(qw in question_lower for qw in question_words)
        
        if not has_question_word and '?' not in question:
            return {
                'is_valid': False,
                'error_message': 'Câu hỏi không rõ ràng. Vui lòng sử dụng từ hỏi: ai, gì, nào, đâu, khi nào...',
                'error_type': 'no_question_word',
                'suggestions': [
                    'Truyện Kiều do AI sáng tác?',
                    'Nhân vật NÀO trong Chí Phèo?',
                    'Nam Cao viết tác phẩm GÌ?'
                ]
            }
        
        # ✅ Hợp lệ
        return {
            'is_valid': True,
            'error_message': None,
            'error_type': None
        }
    
    def _is_literature_related(self, question: str) -> bool:
        """Kiểm tra câu hỏi có liên quan đến văn học không"""
        
        # Check whitelist keywords
        for keyword in self.literature_keywords:
            if keyword in question:
                return True
        
        # Nếu không có keyword nào, kiểm tra context
        # Ví dụ: "Kiều yêu ai?" → không có keyword nhưng vẫn hợp lệ
        # vì "Kiều" là entity văn học
        
        # Danh sách entities văn học (lowercase để so sánh)
        literature_entities = [
            # === NHÂN VẬT ===
            'kiều', 'thúy kiều', 'kim trọng', 'thúy vân', 'sở khanh', 'hoạn thư',
            'chí phèo', 'phèo', 'thị nở',
            'lão hạc', 'hạc', 'cậu vàng',
            'dũng', 'hắc',
            'xuân tóc đỏ', 'tóc đỏ',
            'dế mèn', 'mèn',
            'tràng', 'thị',
            'ngạn', 'hà lan',
            'thiều', 'tường',
            
            # === TÁC GIẢ ===
            'nguyễn du', 'nam cao', 'ngô tất tố', 'vũ trọng phụng',
            'nguyễn tuân', 'tô hoài', 'hồ xuân hương', 'xuân diệu',
            'tố hữu', 'huy cận', 'thạch lam', 'kim lân',
            'nguyễn minh châu', 'nguyễn huy thiệp', 'nguyễn nhật ánh',
            
            # === TÁC PHẨM (từ khóa ngắn) ===
            'tắt đèn', 'số đỏ', 'vợ nhặt', 'làng', 'mắt biếc',
            'dế mèn', 'tràng giang', 'quán mị', 'vĩnh biệt',
            'việt bắc', 'từ ấy', 'lão hạc', 'chí phèo',
            'bánh trôi', 'hoàng hôn', 'chiếc lược', 'cá trong nước',
            'tướng về hưu', 'không có vua', 'vang bóng', 'nắng trong vườn',
            'nhà mẹ lê', 'gửi hương', 'dumb luck', 'sống mòn',
            'chữ người tử tù', 'cô bé bán diêm', 'hoa vàng', 'cỏ xanh',
            'văn tế', 'cần giuộc', 'nghĩa sĩ'
        ]
        
        for entity in literature_entities:
            if entity in question:
                return True
        
        return False
    
    
    def _detect_intent(self, question: str) -> str:
        """Nhận diện ý định câu hỏi"""
        
        # Ưu tiên: tìm quan hệ (có từ "giữa")
        if 'giữa' in question or 'và' in question and any(w in question for w in ['quan hệ', 'liên quan']):
            return 'tim_quan_he'
        
        # Kiểm tra từng intent
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in question:
                    return intent
        
        # Mặc định: tìm chi tiết
        return 'chi_tiet'
    
    def _extract_entities(self, question: str) -> List[str]:
        """
        Trích xuất tên riêng (entities)
        Ví dụ: "Truyện Kiều", "Nguyễn Du", "Chí Phèo"
        """
        entities = []
        
        # Danh sách tên riêng văn học Việt Nam
        
        # === 15 TÁC GIẢ ===
        tac_gia_entities = [
            'Nguyễn Du', 'Nam Cao', 'Ngô Tất Tố', 'Vũ Trọng Phụng',
            'Nguyễn Tuân', 'Tô Hoài', 'Hồ Xuân Hương', 'Xuân Diệu',
            'Tố Hữu', 'Huy Cận', 'Thạch Lam', 'Kim Lân',
            'Nguyễn Minh Châu', 'Nguyễn Huy Thiệp', 'Nguyễn Nhật Ánh'
        ]
        
        # === 30 TÁC PHẨM (theo đúng database) ===
        tac_pham_entities = [
            # Nguyễn Du (2)
            'Truyện Kiều', 'Văn tế nghĩa sĩ Cần Giuộc',
            # Nam Cao (3)
            'Chí Phèo', 'Lão Hạc', 'Sống mòn',
            # Ngô Tất Tố (1)
            'Tắt đèn',
            # Vũ Trọng Phụng (2)
            'Số đỏ', 'Dumb Luck',
            # Nguyễn Tuân (2)
            'Vang bóng một thời', 'Chữ người tử tù',
            # Tô Hoài (2)
            'Dế Mèn phiêu lưu ký', 'Cô bé bán diêm',
            # Hồ Xuân Hương (2)
            'Bánh trôi nước', 'Quán Mị',
            # Xuân Diệu (2)
            'Vĩnh biệt', 'Gửi hương cho gió',
            # Tố Hữu (2)
            'Việt Bắc', 'Từ ấy',
            # Huy Cận (2)
            'Tràng Giang', 'Hoàng hôn',
            # Thạch Lam (2)
            'Nhà mẹ Lê', 'Nắng trong vườn',
            # Kim Lân (2)
            'Vợ nhặt', 'Làng',
            # Nguyễn Minh Châu (2)
            'Chiếc lược ngà', 'Cá trong nước, nước trong cá',
            # Nguyễn Huy Thiệp (2)
            'Tướng về hưu', 'Không có vua',
            # Nguyễn Nhật Ánh (2)
            'Mắt biếc', 'Tôi thấy hoa vàng trên cỏ xanh'
        ]
        
        # === NHÂN VẬT (19 nhân vật) ===
        nhan_vat_entities = [
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
        
        # Gộp tất cả
        known_entities = tac_gia_entities + tac_pham_entities + nhan_vat_entities
        
        # Tìm entities trong câu hỏi (case-insensitive)
        question_lower = question.lower()
        for entity in known_entities:
            if entity.lower() in question_lower:
                entities.append(entity)
        
        # Loại bỏ trùng lặp và convert thành list
        entities = list(set(entities))
        
        return entities
    
    def _extract_keywords(self, question: str) -> List[str]:
        """Trích xuất từ khóa quan trọng"""
        
        # Tokenize
        try:
            words = word_tokenize(question)
        except:
            # Fallback: split đơn giản
            words = question.split()
        
        # Lọc stopwords
        keywords = [w for w in words if w not in self.stopwords and len(w) > 1]
        
        return keywords
    
    def suggest_questions(self) -> List[str]:
        """Gợi ý câu hỏi mẫu"""
        return [
            "Truyện Kiều do ai sáng tác?",
            "Các nhân vật trong truyện Chí Phèo?",
            "Nguyễn Du có tác phẩm nào?",
            "Mối quan hệ giữa Thúy Kiều và Kim Trọng?",
            "Nam Cao viết những tác phẩm gì?",
            "Ai là tác giả của Dế Mèn phiêu lưu ký?",
            "Nhân vật nào xuất hiện trong Vợ nhặt?",
            "Nguyễn Nhật Ánh viết tác phẩm gì?",
            "Tố Hữu có những bài thơ nào nổi tiếng?"
        ]


# Singleton instance
nlp_service = NLPService()