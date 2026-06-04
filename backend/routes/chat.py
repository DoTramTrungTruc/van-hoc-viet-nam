from flask import Blueprint, request, jsonify
from groq import Groq 
import os
from services.neo4j_service import Neo4jService
from dotenv import load_dotenv
import os, json, re, random
# Load biến môi trường
load_dotenv()

chat_bp = Blueprint('chat', __name__)

# ===== KHỞI TẠO GROQ =====
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ===== KẾT NỐI NEO4J =====
neo4j = Neo4jService(
    uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    user=os.getenv("NEO4J_USER", "ae54e57b"),
    password=os.getenv("NEO4J_PASSWORD", "password")
)

 
# ===== MÀU SẮC NODE =====
NODE_COLORS = {
    "TacGia":   {"background": "#8B4513", "border": "#D4AF37", "font": "#FFFFFF"},
    "TacPham":  {"background": "#1565C0", "border": "#42A5F5", "font": "#FFFFFF"},
    "NhanVat":  {"background": "#2E7D32", "border": "#66BB6A", "font": "#FFFFFF"},
    "TheLoai":  {"background": "#6A1B9A", "border": "#CE93D8", "font": "#FFFFFF"},
    "GiaiDoan": {"background": "#E65100", "border": "#FFA726", "font": "#FFFFFF"},
}
 
EDGE_COLORS = {
    "SANG_TAC":        {"color": "#D4AF37", "label": "sáng tác"},
    "CO_NHAN_VAT":     {"color": "#66BB6A", "label": "có nhân vật"},
    "QUAN_HE":         {"color": "#90CAF9", "label": "quan hệ"},
    "THUOC_THE_LOAI":  {"color": "#CE93D8", "label": "thể loại"},
    "THUOC_GIAI_DOAN": {"color": "#FFA726", "label": "giai đoạn"},
}
 
 
# ===== HELPER: QUERY SUBGRAPH TỪ NEO4J =====
def get_subgraph_for_question(tac_pham: str,  question: str, entities_mentioned: list) -> dict:
    """
    Truy vấn Neo4j lấy subgraph liên quan đến tác phẩm và các thực thể
    được nhắc đến trong câu hỏi/câu trả lời.
    Trả về dict {nodes: [...], edges: [...]} cho Vis.js
    """
    
    nodes_map = {}   # id -> node
    edges_list = []
    edge_ids = set()
 
    def add_node(node_id: str, label: str, node_type: str, title: str = ""):
        if node_id not in nodes_map:
            color = NODE_COLORS.get(node_type, {"background": "#607D8B", "border": "#90A4AE", "font": "#FFFFFF"})
            nodes_map[node_id] = {
                "id":    node_id,
                "label": label[:25] + "…" if len(label) > 25 else label,
                "title": title or label,
                "group": node_type,
                "color": color,
                "font":  {"color": color["font"]},
                "shape": "ellipse",
                "size":  28 if node_type == "TacPham" else 22,
            }
 
    def add_edge(from_id: str, to_id: str, rel_type: str, extra_label: str = ""):
        eid = f"{from_id}__{rel_type}__{to_id}"
        if eid not in edge_ids:
            edge_ids.add(eid)
            ec = EDGE_COLORS.get(rel_type, {"color": "#90A4AE", "label": rel_type})
            display_label = ec["label"]
            if extra_label:
              display_label = extra_label if extra_label else ec["label"]
            edges_list.append({
                "from":   from_id,
                "to":     to_id,
                "label":  display_label,
                "color":  {"color": ec["color"], "highlight": ec["color"]},
                "arrows": "to",
                "font":   {"size": 10, "color": "#555555"},
            })
 
    # ── 1. TÁC PHẨM + TÁC GIẢ + THỂ LOẠI + GIAI ĐOẠN ──────────────────
    
    # ── 2. NHÂN VẬT ────────────────────────────────────────────────────
    # Nếu câu hỏi liên quan nhân vật → lấy tất cả nhân vật
    # Nếu không → chỉ lấy nhân vật được nhắc tên trong entities_mentioned
    entities_lower = [e.lower() for e in entities_mentioned]
     
    question_lower = question.lower()
    ask_about_chars = any(
        kw in question_lower
        for kw in [
            "nhân vật",
            "nhan vat",
            "tính cách",
            "vai trò",
            "số phận"
        ]
    )
    ask_author = any(k in question_lower for k in [
        "tác giả",
        "nhà văn",
        "nhà thơ",
        "ai sáng tác"
    ])

    ask_character = any(k in question_lower for k in [
        "nhân vật",
        "vai trò",
        "tính cách",
        "số phận",
        "ai là"
    ])

    ask_genre = any(k in question_lower for k in [
        "thể loại"
    ])

    ask_period = any(k in question_lower for k in [
        "giai đoạn"
    ])

    ask_year = any(k in question_lower for k in [
        "năm sáng tác",
        "sáng tác năm nào",
        "xuất bản năm nào"
    ])

    if ask_about_chars:
        # Lấy tất cả nhân vật
        cypher_nv = """
        MATCH (tp:TacPham {ten: $ten})-[r:CO_NHAN_VAT]->(nv:NhanVat)
        RETURN nv, r.vai_tro AS vai_tro
        """
    else:
        # Chỉ lấy nhân vật được nhắc đến
        cypher_nv = """
        MATCH (tp:TacPham {ten: $ten})-[r:CO_NHAN_VAT]->(nv:NhanVat)
        WHERE toLower(nv.ten) IN $entities
        RETURN nv, r.vai_tro AS vai_tro
        """
    if ask_author:

        cypher = """
        MATCH (tg:TacGia)-[:SANG_TAC]->(tp:TacPham {ten:$ten})
        RETURN tg,tp
        """

        rows = neo4j.execute_query(cypher, {"ten": tac_pham})

        for row in rows:

            tg = row["tg"]
            tp = row["tp"]

            tg_id = f"tg_{tg['ten']}"
            tp_id = f"tp_{tp['ten']}"

            add_node(
                tg_id,
                tg["ten"],
                "TacGia",
                f"Tác giả: {tg['ten']}"
            )

            add_node(
                tp_id,
                tp["ten"],
                "TacPham",
                f"Tác phẩm: {tp['ten']}"
            )

            add_edge(
                tg_id,
                tp_id,
                "SANG_TAC"
            )

        return {
            "nodes": list(nodes_map.values()),
            "edges": edges_list
        }
    if ask_genre:

        cypher = """
        MATCH (tp:TacPham {ten:$ten})
        -[:THUOC_THE_LOAI]->
        (tl:TheLoai)
        RETURN tp,tl
        """

        rows = neo4j.execute_query(cypher, {"ten": tac_pham})

        for row in rows:

            tp = row["tp"]
            tl = row["tl"]

            tp_id = f"tp_{tp['ten']}"
            tl_id = f"tl_{tl['ten']}"

            add_node(tp_id,tp["ten"],"TacPham")
            add_node(tl_id,tl["ten"],"TheLoai")

            add_edge(
                tp_id,
                tl_id,
                "THUOC_THE_LOAI"
            )

        return {
            "nodes": list(nodes_map.values()),
            "edges": edges_list
        }
    if ask_period:

        cypher = """
        MATCH (tp:TacPham {ten:$ten})
        -[:THUOC_GIAI_DOAN]->
        (gd:GiaiDoan)
        RETURN tp,gd
        """

        rows = neo4j.execute_query(cypher, {"ten": tac_pham})

        for row in rows:

            tp = row["tp"]
            gd = row["gd"]

            tp_id = f"tp_{tp['ten']}"
            gd_id = f"gd_{gd['ten']}"

            add_node(tp_id,tp["ten"],"TacPham")
            add_node(gd_id,gd["ten"],"GiaiDoan")

            add_edge(
                tp_id,
                gd_id,
                "THUOC_GIAI_DOAN"
            )

        return {
            "nodes": list(nodes_map.values()),
            "edges": edges_list
        }
    mentioned_characters = []

    for entity in entities_lower:

        cypher = """
        MATCH (nv:NhanVat)
        WHERE toLower(nv.ten)= $name
        RETURN nv
        """

        rows = neo4j.execute_query(
            cypher,
            {"name": entity}
        )

        if rows:
            mentioned_characters.append(entity)
    if mentioned_characters:

        cypher = """
        MATCH (tp:TacPham {ten:$ten})
        -[:CO_NHAN_VAT]->
        (nv:NhanVat)

        WHERE toLower(nv.ten) IN $chars

        RETURN nv
        """
        if len(mentioned_characters) >= 2:

            cypher_rel = """
            MATCH (a:NhanVat)-[r:QUAN_HE]->(b:NhanVat)
            WHERE toLower(a.ten) IN $chars
            AND toLower(b.ten) IN $chars
            RETURN a,b,r
            """

            rel_rows = neo4j.execute_query(
                cypher_rel,
                {"chars": mentioned_characters}
            )

            for row in rel_rows:

                a = row["a"]
                b = row["b"]
                r = row["r"]

                a_id = f"nv_{a['ten']}"
                b_id = f"nv_{b['ten']}"

                add_node(
                    a_id,
                    a["ten"],
                    "NhanVat",
                    f"Nhân vật: {a['ten']}"
                )

                add_node(
                    b_id,
                    b["ten"],
                    "NhanVat",
                    f"Nhân vật: {b['ten']}"
                )

                add_edge(
                    a_id,
                    b_id,
                    "QUAN_HE",
                    r.get("loai", "")
                )

            if rel_rows:
                return {
                    "nodes": list(nodes_map.values()),
                    "edges": edges_list
                }
        rows = neo4j.execute_query(
            cypher,
            {
                "ten": tac_pham,
                "chars": mentioned_characters
            }
        )

        tp_id = f"tp_{tac_pham}"

        add_node(
            tp_id,
            tac_pham,
            "TacPham"
        )

        for row in rows:

            nv = row["nv"]

            nv_id = f"nv_{nv['ten']}"

            add_node(
                nv_id,
                nv["ten"],
                "NhanVat"
            )

            add_edge(
                tp_id,
                nv_id,
                "CO_NHAN_VAT"
            )

        return {
            "nodes": list(nodes_map.values()),
            "edges": edges_list
        }
    if ask_character and mentioned_characters:

        cypher = """
        MATCH (tp:TacPham {ten:$ten})
        -[r:CO_NHAN_VAT]->
        (nv:NhanVat)

        RETURN nv,r.vai_tro as vai_tro
        """

        rows = neo4j.execute_query(cypher, {"ten": tac_pham})

        tp_id = f"tp_{tac_pham}"

        add_node(
            tp_id,
            tac_pham,
            "TacPham"
        )

        selected_chars = []

        for row in rows:

            nv = row["nv"]

            nv_id = f"nv_{nv['ten']}"

            add_node(
                nv_id,
                nv["ten"],
                "NhanVat"
            )

            add_edge(
                tp_id,
                nv_id,
                "CO_NHAN_VAT"
            )

            selected_chars.append(nv["ten"])

        return {
            "nodes": list(nodes_map.values()),
            "edges": edges_list
        }
    nv_results = neo4j.execute_query(
        cypher_nv,
        {"ten": tac_pham, "entities": entities_lower}
    )
 
    tp_id = f"tp_{tac_pham}"
    for row in nv_results:
        nv = row.get("nv", {})
        vai_tro = row.get("vai_tro", "")
        if nv.get("ten"):
            nv_id = f"nv_{nv.get('ten')}"
            title = f"Nhân vật: {nv.get('ten')}"
            if nv.get("tinh_cach"):
                title += f"\nTính cách: {nv.get('tinh_cach')[:60]}"
            if nv.get("so_phan"):
                title += f"\nSố phận: {nv.get('so_phan')[:60]}"
            add_node(nv_id, nv.get("ten"), "NhanVat", title)
            add_edge(tp_id, nv_id, "CO_NHAN_VAT", vai_tro)
 
    # ── 3. QUAN HỆ GIỮA CÁC NHÂN VẬT ───────────────────────────────────
    if len([k for k in nodes_map if k.startswith("nv_")]) >= 2:
        cypher_rel = """
        MATCH (tp:TacPham {ten: $ten})-[:CO_NHAN_VAT]->(a:NhanVat)
        MATCH (tp)-[:CO_NHAN_VAT]->(b:NhanVat)
        MATCH (a)-[r:QUAN_HE]->(b)
        RETURN a.ten AS a_ten, b.ten AS b_ten, r.loai AS loai
        """
        rel_results = neo4j.execute_query(cypher_rel, {"ten": tac_pham})
        for row in rel_results:
            a_id = f"nv_{row.get('a_ten')}"
            b_id = f"nv_{row.get('b_ten')}"
            if a_id in nodes_map and b_id in nodes_map:
                add_edge(a_id, b_id, "QUAN_HE", row.get("loai", ""))
 
    return {
        "nodes": list(nodes_map.values()),
        "edges": edges_list,
    }
 
 
# ===== HELPER: TRÍCH XUẤT THỰC THỂ TỪ CÂU HỎI =====
def extract_entities_from_text(text: str, tp_data: dict) -> list:
    """
    Tìm tên nhân vật, tác giả, thể loại được nhắc trong text.
    """
    entities = []
    text_lower = text.lower()
 
    # Tên nhân vật
    for nv in tp_data.get("nhan_vat", []):
        if nv.get("ten") and nv["ten"].lower() in text_lower:
            entities.append(nv["ten"])
 
    # Tác giả
    if tp_data.get("tac_gia") and tp_data["tac_gia"].lower() in text_lower:
        entities.append(tp_data["tac_gia"])
 
    # Từ khoá về nhân vật
    if any(kw in text_lower for kw in ["nhân vật", "tính cách", "vai trò", "số phận", "nhan vat"]):
        entities.append("nhân vật")
 
    return list(set(entities))
 
 
# ===== HELPER: FORMAT NHÂN VẬT =====
def format_nhan_vat(nv_list: list) -> str:
    parts = []
    for nv in nv_list:
        lines = [f"- Tên: {nv.get('ten')}"]
        for field, label in [
            ("vai_tro",         "Vai trò"),
            ("tinh_cach",       "Tính cách"),
            ("so_phan",         "Số phận"),
            ("y_nghia_dien_hinh","Ý nghĩa"),
        ]:
            if nv.get(field):
                lines.append(f"  {label}: {nv.get(field)}")
        parts.append("\n".join(lines))
    return "\n\n".join(parts) if parts else "Chưa có thông tin"
 
 
# ===== HELPER: BUILD CONTEXT =====
def build_context(tp: dict) -> str:
    fields = [
        ("ten",                "TÁC PHẨM"),
        ("tac_gia",            "TÁC GIẢ"),
        ("nam_sang_tac",       "NĂM SÁNG TÁC"),
        ("nam_xuat_ban",       "NĂM XUẤT BẢN"),
        ("noi_dung_tom_tat",   "\nNỘI DUNG TÓM TẮT"),
        ("chu_de_chinh",       "\nCHỦ ĐỀ CHÍNH"),
        ("y_nghia",            "\nÝ NGHĨA"),
        ("gia_tri_nghe_thuat", "\nGIÁ TRỊ NGHỆ THUẬT"),
        ("hoan_canh",          "\nHOÀN CẢNH SÁNG TÁC"),
        ("cau_truc",           "\nCẤU TRÚC"),
        ("trich_doan",         "\nTRÍCH ĐOẠN"),
    ]
    parts = []
    for key, label in fields:
        val = tp.get(key)
        if not val:
            continue
        if isinstance(val, list):
            val = ", ".join(val)
        parts.append(f"{label}: {val}")
 
    # Thể loại & giai đoạn
    for key, label in [("the_loai", "THỂ LOẠI"), ("giai_doan", "GIAI ĐOẠN")]:
        val = tp.get(key)
        if val:
            parts.append(f"{label}: {', '.join(val) if isinstance(val, list) else val}")
 
    parts.append(f"\nNHÂN VẬT:\n{format_nhan_vat(tp.get('nhan_vat', []))}")
    return "\n".join(parts)
 
 
# ================================================================
#  ROUTE 1: /api/chat  — Hỏi đáp tác phẩm + trả về KG subgraph
# ================================================================
@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    try:
        data      = request.json or {}
        question  = data.get('question', '').strip()
        tac_pham  = data.get('tac_pham', '').strip()
 
        if not question:
            return jsonify({"success": False, "answer": "Bạn chưa nhập câu hỏi."})
        if not tac_pham:
            return jsonify({"success": False, "answer": "Thiếu tên tác phẩm."})
 
        # ── Lấy dữ liệu tác phẩm ──────────────────────────────────────
        tp = neo4j.get_tac_pham_detail(tac_pham)
        if not tp:
            return jsonify({"success": False, "answer": f"Không tìm thấy tác phẩm '{tac_pham}'."})
 
        context = build_context(tp)
 
        # ── Gọi LLaMA qua Groq ────────────────────────────────────────
        system_prompt = """Bạn là trợ lý ảo chuyên về văn học Việt Nam.
 
QUY TẮC:
* Chỉ trả lời dựa trên dữ liệu được cung cấp.
* Không bịa đặt thông tin.
* Nếu không có thông tin → trả lời: "Chưa có thông tin về vấn đề này".
 
CÁCH TRÌNH BÀY:
* Chia đoạn rõ ràng, mỗi đoạn tối đa 2–3 dòng.
* Dùng emoji phù hợp: 📖 🎯 👥 ✨
* Khi phân tích chia: 📖 Nội dung / 🎯 Ý nghĩa / ✨ Nghệ thuật / 👥 Nhân vật
* Khi liệt kê dùng dấu "-", xuống dòng giữa các ý."""
 
        user_prompt = f"DỮ LIỆU:\n{context}\n\nCÂU HỎI:\n{question}"
 
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=600,
        )
        answer = response.choices[0].message.content.strip()
 
        # ── Trích xuất thực thể để highlight trên KG ─────────────────
        entities = extract_entities_from_text(question + " " + answer, tp)
 
        # ── Lấy subgraph từ Neo4j ─────────────────────────────────────
        graph_data = get_subgraph_for_question( tac_pham, question ,entities)
 
        # ── Highlight node liên quan ──────────────────────────────────
        for node in graph_data["nodes"]:
            node_label_lower = node["label"].lower()
            node["highlighted"] = any(
                e.lower() in node_label_lower or node_label_lower in e.lower()
                for e in entities
            )
            if node["highlighted"]:
                node["borderWidth"] = 3
                node["size"] = 32
 
        return jsonify({
            "success":    True,
            "answer":     answer,
            "graph_data": graph_data,        # <-- Vis.js sẽ dùng phần này
            "entities":   entities,          # <-- debug / tooltip
            "highlight":  True,
        })
 
    except Exception as e:
        print("Chat error:", str(e))
        return jsonify({"success": False, "answer": f"Lỗi server: {str(e)}"}), 500
 
 
# ================================================================
#  ROUTE 2: /api/chat-tac-gia — Hỏi đáp tác giả + KG
# ================================================================
@chat_bp.route('/api/chat-tac-gia', methods=['POST'])
def chat_tac_gia():
    try:
        data     = request.json or {}
        question = data.get('question', '').strip()
        tac_gia  = data.get('tac_gia',  '').strip()
        tac_pham = data.get('tac_pham', '').strip()
 
        if not question:
            return jsonify({"success": False, "answer": "Thiếu câu hỏi."})
 
        context    = ""
        graph_data = {"nodes": [], "edges": []}
 
        if tac_pham:
            tp = neo4j.get_tac_pham_detail(tac_pham)
            if not tp:
                return jsonify({"success": False, "answer": "Không tìm thấy tác phẩm."})
            context    = build_context(tp)
            entities   = extract_entities_from_text(question, tp)
            graph_data = get_subgraph_for_question(tac_pham, question, entities)
 
        elif tac_gia:
            tg = neo4j.get_tac_gia_detail(tac_gia)
            if not tg:
                return jsonify({"success": False, "answer": "Không tìm thấy tác giả."})
 
            context = f"""TÁC GIẢ: {tg.get('ten')}
NĂM SINH: {tg.get('nam_sinh')}  |  NĂM MẤT: {tg.get('nam_mat')}
QUÊ QUÁN: {tg.get('que_quan')}
TRƯỜNG PHÁI: {tg.get('truong_phai')}
BÚT DANH: {tg.get('but_danh', 'Chưa có')}
TIỂU SỬ:\n{tg.get('tieu_su')}
TÁC PHẨM: {', '.join(tg.get('tac_pham', []))}"""
 
            # Build KG mini cho tác giả
            nodes_map, edges_list, edge_ids = {}, [], set()
            tg_id = f"tg_{tg.get('ten')}"
            nodes_map[tg_id] = {
                "id": tg_id, "label": tg.get("ten"), "group": "TacGia",
                "color": NODE_COLORS["TacGia"], "shape": "ellipse", "size": 28,
                "title": f"Tác giả: {tg.get('ten')}\n({tg.get('nam_sinh')}–{tg.get('nam_mat')})",
            }
            for tp_name in tg.get("tac_pham", []):
                tp_id = f"tp_{tp_name}"
                nodes_map[tp_id] = {
                    "id": tp_id, "label": tp_name[:22] + "…" if len(tp_name) > 22 else tp_name,
                    "group": "TacPham", "color": NODE_COLORS["TacPham"],
                    "shape": "ellipse", "size": 22, "title": f"Tác phẩm: {tp_name}",
                }
                eid = f"{tg_id}__SANG_TAC__{tp_id}"
                if eid not in edge_ids:
                    edge_ids.add(eid)
                    edges_list.append({
                        "from": tg_id, "to": tp_id, "label": "sáng tác",
                        "color": {"color": "#D4AF37"}, "arrows": "to",
                    })
            graph_data = {"nodes": list(nodes_map.values()), "edges": edges_list}
 
        else:
            return jsonify({"success": False, "answer": "Thiếu context."})
 
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Chỉ trả lời dựa trên context. Không bịa. Dùng emoji phù hợp."},
                {"role": "user",   "content": f"{context}\n\nCâu hỏi: {question}"},
            ],
            temperature=0.7,
            max_tokens=500,
        )
 
        return jsonify({
            "success":    True,
            "answer":     response.choices[0].message.content.strip(),
            "graph_data": graph_data,
        })
 
    except Exception as e:
        return jsonify({"success": False, "answer": str(e)})
 
 
# ================================================================
#  ROUTE 3: /api/quiz — Tạo câu hỏi trắc nghiệm
# ================================================================
QUESTION_TYPES = [
    "nhân vật chính", "tác giả", "nội dung", "ý nghĩa", "chủ đề",
    "vai trò nhân vật", "tính cách nhân vật", "năm sáng tác", "thể loại",
    "số phận nhân vật", "giá trị nghệ thuật", "so sánh nhân vật",
    "chi tiết đặc sắc", "hình ảnh biểu tượng", "phong cách nghệ thuật",
    "biện pháp tu từ", "bối cảnh tác phẩm", "tâm trạng nhân vật",
    "thông điệp tác giả", "tình huống truyện", "diễn biến chính",
]
 
last_questions: list[str] = []
 
 
def is_duplicate(q: str) -> bool:
    return any(
        q.lower() in old.lower() or old.lower() in q.lower()
        for old in last_questions
    )
 
 
@chat_bp.route('/api/quiz', methods=['POST'])
def generate_quiz():
    try:
        data     = request.json or {}
        tac_pham = data.get('tac_pham', '').strip()
 
        if not tac_pham:
            return jsonify({"success": False, "message": "Thiếu tác phẩm."})
 
        tp = neo4j.get_tac_pham_detail(tac_pham)
        if not tp:
            return jsonify({"success": False, "message": "Không tìm thấy tác phẩm."})
 
        q_type     = random.choice(QUESTION_TYPES)
        difficulty = random.choice(["dễ", "trung bình", "khó"])
 
        context = f"""TÁC PHẨM: {tp.get('ten')}
TÁC GIẢ: {tp.get('tac_gia')}
NỘI DUNG: {tp.get('noi_dung_tom_tat')}
NHÂN VẬT: {', '.join([nv['ten'] for nv in tp.get('nhan_vat', [])])}
CHỦ ĐỀ: {tp.get('chu_de_chinh')}
Ý NGHĨA: {tp.get('y_nghia')}"""
 
        avoid_text = "\n".join(last_questions[-5:])
 
        prompt = f"""Bạn là AI tạo câu hỏi trắc nghiệm văn học Việt Nam.
 
⚠️ BẮT BUỘC:
- Không trùng câu hỏi đã dùng
- Mỗi câu phải KHÁC HOÀN TOÀN
 
🎯 Chủ đề: {q_type}  |  🔥 Độ khó: {difficulty}
 
🚫 CÂU HỎI ĐÃ DÙNG:
{avoid_text}
 
YÊU CẦU:
- 4 đáp án không trùng nhau
- Chỉ 1 đáp án đúng
- Đáp án sai phải hợp lý
- KHÔNG thêm A. B. C. D. trong nội dung đáp án
 
FORMAT JSON (chỉ JSON, không thêm gì):
{{
  "question": "...",
  "options": ["...", "...", "...", "..."],
  "correct": 0
}}
 
DỮ LIỆU:
{context}"""
 
        quiz = None
        for _ in range(5):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=1.1,
                top_p=0.95,
                frequency_penalty=0.5,
                presence_penalty=0.6,
                max_tokens=400,
            )
            raw  = response.choices[0].message.content.strip()
            raw  = re.sub(r"```json|```", "", raw).strip()
 
            # Trích JSON nếu có text thừa
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                raw = match.group(0)
 
            quiz = json.loads(raw)
            if not is_duplicate(quiz["question"]):
                break
 
        last_questions.append(quiz["question"])
        if len(last_questions) > 10:
            last_questions.pop(0)
 
        return jsonify({"success": True, "quiz": quiz})
 
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        })  
 
 
# ================================================================
#  ROUTE 4: /api/graph — Lấy KG thuần (cho trang chi tiết)
# ================================================================
@chat_bp.route('/api/graph', methods=['GET'])
def get_graph():
    """
    Endpoint riêng để frontend load KG đầy đủ khi mở trang tác phẩm,
    không cần hỏi chatbot.
    """
    tac_pham = request.args.get('tac_pham', '').strip()
    if not tac_pham:
        return jsonify({"success": False, "message": "Thiếu tên tác phẩm."})
 
    try:
        graph_data = get_subgraph_for_question(tac_pham, "hiển thị tất cả nhân vật",["nhân vật"])
        return jsonify({"success": True, "graph_data": graph_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

