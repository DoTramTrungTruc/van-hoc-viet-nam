"""
Routes cho Thống kê và Danh mục
API endpoints cho thống kê, thể loại, chủ đề
"""

from flask import Blueprint, jsonify
from services.neo4j_service import Neo4jService
from config import Config

general_bp = Blueprint('general', __name__, url_prefix='/api')

neo4j_service = Neo4jService(
    uri=Config.NEO4J_URI,
    user=Config.NEO4J_USER,
    password=Config.NEO4J_PASSWORD,
    database=Config.NEO4J_DATABASE
)


@general_bp.route('/the-loai', methods=['GET'])
def get_all_the_loai():
    """
    Lấy danh sách thể loại
    GET /api/the-loai
    """
    try:
        the_loai_list = neo4j_service.get_all_the_loai()
        return jsonify({
            'success': True,
            'data': the_loai_list,
            'count': len(the_loai_list)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@general_bp.route('/chu-de', methods=['GET'])
def get_all_chu_de():
    """
    Lấy danh sách chủ đề
    GET /api/chu-de
    """
    try:
        chu_de_list = neo4j_service.get_all_chu_de()
        return jsonify({
            'success': True,
            'data': chu_de_list,
            'count': len(chu_de_list)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@general_bp.route('/statistics', methods=['GET'])
def get_statistics():
    try:
        stats          = neo4j_service.get_statistics()
        the_loai_stats = neo4j_service.get_tac_pham_by_the_loai_stats()

        # ── Giai đoạn ──────────────────────────────────────────────────────
        giai_doan_stats = neo4j_service.execute_query("""
            MATCH (tp:TacPham)-[:THUOC_GIAI_DOAN]->(gd:GiaiDoan)
            RETURN gd.ten AS giai_doan, count(tp) AS so_luong
            ORDER BY so_luong DESC
        """)

        # Fallback: nếu không có relationship THUOC_GIAI_DOAN,
        # dùng property giai_doan lưu trực tiếp trên TacPham
        if not giai_doan_stats:
            giai_doan_stats = neo4j_service.execute_query("""
                MATCH (tp:TacPham)
                WHERE tp.giai_doan IS NOT NULL AND tp.giai_doan <> ''
                RETURN tp.giai_doan AS giai_doan, count(tp) AS so_luong
                ORDER BY so_luong DESC
            """)

        # ── Top tác giả ────────────────────────────────────────────────────
        tac_gia_nhieu_tp = neo4j_service.execute_query("""
            MATCH (tg:TacGia)-[:SANG_TAC]->(tp:TacPham)
            RETURN tg.ten AS ten, count(tp) AS so_luong
            ORDER BY so_luong DESC
            LIMIT 8
        """)

        # ── Tác phẩm theo năm ──────────────────────────────────────────────
        # nam_sang_tac có thể là số nguyên HOẶC chuỗi → dùng toString()
        tp_by_year = neo4j_service.execute_query("""
            MATCH (tp:TacPham)
            WHERE tp.nam_sang_tac IS NOT NULL
            WITH toString(tp.nam_sang_tac) AS nam, tp
            WHERE nam <> '' AND nam <> 'null'
            RETURN nam, count(tp) AS so_luong
            ORDER BY nam
        """)

        # ── Nhân vật theo tác phẩm ─────────────────────────────────────────
        # Thử qua relationship CO_NHAN_VAT trước
        nhan_vat_by_tp = neo4j_service.execute_query("""
            MATCH (tp:TacPham)-[:CO_NHAN_VAT]->(nv:NhanVat)
            RETURN tp.ten AS ten, count(nv) AS so_nhan_vat
            ORDER BY so_nhan_vat DESC
            LIMIT 8
        """)

        # Fallback: nhan_vat lưu dạng property array trên TacPham
        if not nhan_vat_by_tp:
            nhan_vat_by_tp = neo4j_service.execute_query("""
                MATCH (tp:TacPham)
                WHERE tp.nhan_vat IS NOT NULL
                AND size(tp.nhan_vat) > 0
                RETURN tp.ten AS ten, size(tp.nhan_vat) AS so_nhan_vat
                ORDER BY so_nhan_vat DESC
                LIMIT 8
            """)

        return jsonify({
            'success': True,
            'data': {
                'tong_quan':        stats,
                'theo_the_loai':    the_loai_stats,
                'theo_giai_doan':   giai_doan_stats,
                'tac_gia_nhieu_tp': tac_gia_nhieu_tp,
                'tp_by_year':       tp_by_year,
                'nhan_vat_by_tp':   nhan_vat_by_tp,
            }
        }), 200

    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@general_bp.route('/health', methods=['GET'])
def health_check():
    """
    Kiểm tra tình trạng server
    GET /api/health
    """
    return jsonify({
        'success': True,
        'message': 'Server đang hoạt động',
        'version': '1.0.0'
    }), 200