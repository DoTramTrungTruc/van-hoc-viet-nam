"""
Routes cho Nhân vật
API endpoints để quản lý nhân vật
"""

from flask import Blueprint, jsonify, request
from services.neo4j_service import Neo4jService
from config import Config

nhan_vat_bp = Blueprint('nhan_vat', __name__, url_prefix='/api/nhan-vat')

# Khởi tạo Neo4j service
neo4j_service = Neo4jService(
    uri=Config.NEO4J_URI,
    user=Config.NEO4J_USER,
    password=Config.NEO4J_PASSWORD,
    database=Config.NEO4J_DATABASE
)


@nhan_vat_bp.route('/', methods=['GET'])
def get_all_nhan_vat():
    """
    Lấy danh sách tất cả nhân vật
    GET /api/nhan-vat/
    """
    try:
        query = """
        MATCH (nv:NhanVat)
        OPTIONAL MATCH (tp:TacPham)-[r:CO_NHAN_VAT]->(nv)
        RETURN DISTINCT nv.ten as ten, 
               collect(DISTINCT tp.ten) as tac_pham,
               count(DISTINCT tp) as so_tac_pham
        ORDER BY nv.ten
        """
        
        results = neo4j_service.execute_query(query)
        
        nhan_vat_list = []
        for record in results:
            nhan_vat_list.append({
                'ten': record['ten'],
                'tac_pham': record['tac_pham'],
                'so_tac_pham': record['so_tac_pham']
            })
        
        return jsonify({
            'success': True,
            'data': nhan_vat_list,
            'count': len(nhan_vat_list)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@nhan_vat_bp.route('/<ten>', methods=['GET'])
def get_nhan_vat_detail(ten):
    """
    Lấy chi tiết nhân vật
    GET /api/nhan-vat/<ten>
    """
    try:
        query = """
        MATCH (nv:NhanVat {ten: $ten})
        OPTIONAL MATCH (tp:TacPham)-[r:CO_NHAN_VAT]->(nv)
        RETURN nv.ten as ten,
               nv.vai_tro as vai_tro,
               nv.tinh_cach as tinh_cach,
               nv.so_phan as so_phan,
               collect({tac_pham: tp.ten, vai_tro: r.vai_tro}) as tac_pham
        """
        
        results = neo4j_service.execute_query(query, {'ten': ten})
        
        if not results:
            return jsonify({
                'success': False,
                'error': f'Không tìm thấy nhân vật: {ten}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': results[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500