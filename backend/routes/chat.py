from flask import Blueprint, request, jsonify
from groq import Groq
import os
from services.neo4j_service import Neo4jService
from dotenv import load_dotenv
import random

# Load biến môi trường
load_dotenv()

chat_bp = Blueprint('chat', __name__)

# ===== KHỞI TẠO GROQ =====
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ===== KẾT NỐI NEO4J =====
neo4j = Neo4jService(
    uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    user=os.getenv("NEO4J_USER", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "password")
)


@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        question = data.get('question', '').strip()
        tac_pham = data.get('tac_pham')

        # ===== VALIDATE =====
        if not question:
            return jsonify({
                "success": False,
                "answer": "Bạn chưa nhập câu hỏi."
            })

        if not tac_pham:
            return jsonify({
                "success": False,
                "answer": "Thiếu tên tác phẩm."
            })

        # ===== LẤY DỮ LIỆU NEO4J =====
        tp = neo4j.get_tac_pham_detail(tac_pham)

        if not tp:
            return jsonify({
                "success": False,
                "answer": f"Không tìm thấy tác phẩm '{tac_pham}'."
            })

        # ===== FORMAT NHÂN VẬT =====
        nhan_vat_list = []
        for nv in tp.get("nhan_vat", []):
            nv_info = f"- Tên: {nv.get('ten')}"
            if nv.get('vai_tro'):
                nv_info += f"\n  Vai trò: {nv.get('vai_tro')}"
            if nv.get('tinh_cach'):
                nv_info += f"\n  Tính cách: {nv.get('tinh_cach')}"
            if nv.get('so_phan'):
                nv_info += f"\n  Số phận: {nv.get('so_phan')}"
            if nv.get('y_nghia_dien_hinh'):
                nv_info += f"\n  Ý nghĩa: {nv.get('y_nghia_dien_hinh')}"
            
            nhan_vat_list.append(nv_info)

        nhan_vat_text = "\n\n".join(nhan_vat_list) if nhan_vat_list else "Chưa có thông tin"

        # ===== BUILD CONTEXT =====
        context_parts = []

        context_parts.append(f"TÁC PHẨM: {tp.get('ten')}")

        if tp.get('tac_gia'):
            context_parts.append(f"TÁC GIẢ: {tp.get('tac_gia')}")

        if tp.get('nam_sang_tac'):
            context_parts.append(f"NĂM SÁNG TÁC: {tp.get('nam_sang_tac')}")

        if tp.get('nam_xuat_ban'):
            context_parts.append(f"NĂM XUẤT BẢN: {tp.get('nam_xuat_ban')}")

        if tp.get('the_loai'):
            the_loai = tp.get('the_loai')
            if isinstance(the_loai, list):
                context_parts.append(f"THỂ LOẠI: {', '.join(the_loai)}")
            else:
                context_parts.append(f"THỂ LOẠI: {the_loai}")

        if tp.get('giai_doan'):
            giai_doan = tp.get('giai_doan')
            if isinstance(giai_doan, list):
                context_parts.append(f"GIAI ĐOẠN: {', '.join(giai_doan)}")
            else:
                context_parts.append(f"GIAI ĐOẠN: {giai_doan}")

        if tp.get('noi_dung_tom_tat'):
            context_parts.append(f"\nNỘI DUNG TÓM TẮT:\n{tp.get('noi_dung_tom_tat')}")

        if tp.get('chu_de_chinh'):
            context_parts.append(f"\nCHỦ ĐỀ CHÍNH:\n{tp.get('chu_de_chinh')}")

        if tp.get('y_nghia'):
            context_parts.append(f"\nÝ NGHĨA:\n{tp.get('y_nghia')}")

        if tp.get('gia_tri_nghe_thuat'):
            context_parts.append(f"\nGIÁ TRỊ NGHỆ THUẬT:\n{tp.get('gia_tri_nghe_thuat')}")

        if tp.get('hoan_canh'):
            context_parts.append(f"\nHOÀN CẢNH SÁNG TÁC:\n{tp.get('hoan_canh')}")

        if tp.get('cau_truc'):
            context_parts.append(f"\nCẤU TRÚC:\n{tp.get('cau_truc')}")
        if tp.get('trich_doan'):
            context_parts.append(f"\nTRÍCH ĐOẠN:\n{tp.get('trich_doan')}")

        context_parts.append(f"\nNHÂN VẬT:\n{nhan_vat_text}")

        context = "\n".join(context_parts)

        # ===== SYSTEM PROMPT =====
        system_prompt = """
Bạn là trợ lý ảo chuyên về văn học Việt Nam.

QUY TẮC:

* Chỉ trả lời dựa trên dữ liệu được cung cấp
* Không được bịa
* Không có thông tin → trả lời: "Chưa có thông tin về vấn đề này"

CÁCH TRÌNH BÀY:

* Chia đoạn rõ ràng
* Không viết 1 đoạn quá dài
* Mỗi đoạn tối đa 2-3 dòng
* Dùng emoji phù hợp 📖 🎯 👥 ✨
* Nếu phân tích thì chia:
  📖 Nội dung
  🎯 Ý nghĩa
  ✨ Nghệ thuật
  👥 Nhân vật
* Khi liệt kê thì dùng dấu "-"
* Luôn xuống dòng giữa các ý
  """


        # ===== USER PROMPT =====
        user_prompt = f"""DỮ LIỆU:
{context}

CÂU HỎI:
{question}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # ===== GỌI GROQ =====
        response = client.chat.completions.create(
           model="llama-3.3-70b-versatile",  # 🔥 free + nhanh
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        answer = response.choices[0].message.content.strip()

        return jsonify({
            "success": True,
            "answer": answer
        })

    except Exception as e:
        print("Chat error:", str(e))
        return jsonify({
            "success": False,
            "answer": f"Lỗi server: {str(e)}"
        }), 500
@chat_bp.route('/api/chat-tac-gia', methods=['POST'])
def chat_tac_gia():  
    try:
        data = request.json
        question = data.get('question', '').strip()

        tac_gia = data.get('tac_gia')
        tac_pham = data.get('tac_pham')

        if not question:
            return jsonify({"success": False, "answer": "Thiếu câu hỏi."})

        context = ""

        # ===== CONTEXT TÁC PHẨM =====
        if tac_pham:
            tp = neo4j.get_tac_pham_detail(tac_pham)

            if not tp:
                return jsonify({"success": False, "answer": "Không tìm thấy tác phẩm."})

            context = f"""
TÁC PHẨM: {tp.get('ten')}
TÁC GIẢ: {tp.get('tac_gia')}
NĂM SÁNG TÁC: {tp.get('nam_sang_tac')}
THỂ LOẠI: {tp.get('the_loai')}

NỘI DUNG:
{tp.get('noi_dung_tom_tat')}

NHÂN VẬT:
{', '.join([nv['ten'] for nv in tp.get('nhan_vat', [])])}
"""

        # ===== CONTEXT TÁC GIẢ =====
        elif tac_gia:
            tg = neo4j.get_tac_gia_detail(tac_gia)

            if not tg:
                return jsonify({"success": False, "answer": "Không tìm thấy tác giả."})

            context = f"""
TÁC GIẢ: {tg.get('ten')}
NĂM SINH: {tg.get('nam_sinh')}
NĂM MẤT: {tg.get('nam_mat')}
QUÊ QUÁN: {tg.get('que_quan')}
TRƯỜNG PHÁI: {tg.get('truong_phai')}

✍️ BÚT DANH:
{tg.get('but_danh', 'Chưa có thông tin')}

🏆 GIẢI THƯỞNG:
{tg.get('giai_thuong', 'Chưa có thông tin')}

💬 CÂU NÓI NỔI TIẾNG:
{tg.get('cau_noi_noi_tieng', 'Chưa có thông tin')}

TIỂU SỬ:
{tg.get('tieu_su')}

TÁC PHẨM:
{', '.join(tg.get('tac_pham', []))}
"""

        else:
            return jsonify({"success": False, "answer": "Thiếu context."})

        # ===== CALL AI =====
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Chỉ trả lời dựa trên context. Không bịa."
                },
                {
                    "role": "user",
                    "content": f"{context}\n\nCâu hỏi: {question}"
                }
            ]
        )

        return jsonify({
            "success": True,
            "answer": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "answer": str(e)
        })

QUESTION_TYPES = [
    "nhân vật chính",
    "tác giả",
    "nội dung",
    "ý nghĩa",
    "chủ đề",
    "vai trò nhân vật",
    "tính cách nhân vật",
    "năm sáng tác",
    "thể loại",
    "chi tiết cốt truyện",
    "số phận nhân vật",
    "giá trị nghệ thuật",

    # 🔥 thêm mạnh
    "so sánh nhân vật",
    "chi tiết đặc sắc",
    "hình ảnh biểu tượng",
    "phong cách nghệ thuật",
    "biện pháp tu từ",
    "bối cảnh tác phẩm",
    "tâm trạng nhân vật",
    "thông điệp tác giả",
    "tình huống truyện",
    "diễn biến chính"
]
last_questions = []
def is_duplicate(q):
    for old in last_questions:
        if q.lower() in old.lower() or old.lower() in q.lower():
            return True
    return False

@chat_bp.route('/api/quiz', methods=['POST'])
def generate_quiz():
    try:
        data = request.json
        tac_pham = data.get('tac_pham')

        if not tac_pham:
            return jsonify({"success": False, "message": "Thiếu tác phẩm"})

        tp = neo4j.get_tac_pham_detail(tac_pham)

        if not tp:
            return jsonify({"success": False, "message": "Không tìm thấy tác phẩm"})

        # ===== RANDOM TYPE =====
        question_type = random.choice(QUESTION_TYPES)
        difficulty = random.choice(["dễ", "trung bình", "khó"])

        # ===== CONTEXT =====
        context = f"""
TÁC PHẨM: {tp.get('ten')}
TÁC GIẢ: {tp.get('tac_gia')}
NỘI DUNG: {tp.get('noi_dung_tom_tat')}
NHÂN VẬT: {', '.join([nv['ten'] for nv in tp.get('nhan_vat', [])])}
CHỦ ĐỀ: {tp.get('chu_de')}
Ý NGHĨA: {tp.get('y_nghia')}
"""

        avoid_text = "\n".join(last_questions[-5:])

        # ===== PROMPT XỊN =====
        prompt = f"""
Bạn là AI tạo câu hỏi trắc nghiệm văn học Việt Nam.

⚠️ BẮT BUỘC:
- Không được trùng nội dung câu hỏi trước
- Không được hỏi lại cùng ý (dù khác chữ)
- Mỗi câu phải KHÁC HOÀN TOÀN

🎯 Chủ đề: {question_type}
🔥 Độ khó: {difficulty}

🚫 CÂU HỎI ĐÃ DÙNG:
{avoid_text}

YÊU CẦU:
- 4 đáp án KHÔNG trùng nhau
- Chỉ 1 đáp án đúng
- Đáp án sai phải hợp lý (không quá vô lý)
- KHÔNG thêm A. B. C. D. trong nội dung

FORMAT JSON:
{{
  "question": "...",
  "options": ["...", "...", "...", "..."],
  "correct": 0
}}

DỮ LIỆU:
{context}
"""
        import json

        quiz = None

        # ===== TRY 5 LẦN TRÁNH LẶP =====
        for _ in range(5):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=1.2,
                top_p=0.95,
                frequency_penalty=0.5,
                presence_penalty=0.6
            )

            raw = response.choices[0].message.content.strip()

            # 🔥 FIX JSON bị ```json
            raw = raw.replace("```json", "").replace("```", "").strip()

            quiz = json.loads(raw)

            if not is_duplicate(quiz["question"]):
                break
       

        # ===== SAVE MEMORY =====
        last_questions.append(quiz["question"])
        if len(last_questions) > 10:
            last_questions.pop(0)

        return jsonify({
            "success": True,
            "quiz": quiz
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        })  
 