"""
Routes cho Thể loại
API endpoints để quản lý thể loại văn học
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from services.neo4j_service import Neo4jService
from config import Config

the_loai_bp = Blueprint('the_loai', __name__, url_prefix='/api/the-loai')

# Khởi tạo Neo4j service
neo4j_service = Neo4jService(
    uri=Config.NEO4J_URI,
    user=Config.NEO4J_USER,
    password=Config.NEO4J_PASSWORD,
    database=Config.NEO4J_DATABASE
)


@the_loai_bp.route('/', methods=['GET'])
def get_all_the_loai():
    """
    Lấy danh sách tất cả thể loại
    GET /api/the-loai/
    """
    try:
        query = """
        MATCH (tl:TheLoai)
        OPTIONAL MATCH (tp:TacPham)-[:THUOC_THE_LOAI]->(tl)
        RETURN 
            tl.ten AS ten,
            tl.mo_ta AS mo_ta,
            COUNT(tp) AS so_luong_tac_pham
        ORDER BY so_luong_tac_pham DESC
        """
        
        results = neo4j_service.execute_query(query)
        
        the_loai_list = []
        for record in results:
            the_loai_list.append({
                'ten': record['ten'],
                'mo_ta': record['mo_ta'],
                'so_luong_tac_pham': record['so_luong_tac_pham']
            })
        
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


@the_loai_bp.route('/create', methods=['POST'])
@login_required
def create_the_loai():
    """
    Tạo thể loại mới (Admin only)
    POST /api/the-loai/create
    Body: {
        "ten": "...",
        "mo_ta": "..."
    }
    """
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Chỉ admin mới có quyền thêm thể loại'
        }), 403
    
    data = request.get_json()
    
    if not data.get('ten'):
        return jsonify({
            'success': False,
            'error': 'Tên thể loại là bắt buộc'
        }), 400
    
    try:
        # Kiểm tra đã tồn tại chưa
        check_query = """
        MATCH (tl:TheLoai {ten: $ten})
        RETURN tl
        """
        existing = neo4j_service.execute_query(check_query, {'ten': data['ten']})
        
        if existing:
            return jsonify({
                'success': False,
                'error': f'Thể loại "{data["ten"]}" đã tồn tại'
            }), 400
        
        # Tạo mới
        query = """
        CREATE (tl:TheLoai {
            ten: $ten,
            mo_ta: $mo_ta,
            so_luong_tac_pham: 0
        })
        RETURN tl
        """
        
        params = {
            'ten': data['ten'],
            'mo_ta': data.get('mo_ta', '')
        }
        
        result = neo4j_service.execute_write(query, params)
        
        if result:
            return jsonify({
                'success': True,
                'data': dict(result['tl']),
                'message': 'Tạo thể loại thành công'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Tạo thể loại thất bại'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@the_loai_bp.route('/<ten>/update', methods=['PUT'])
@login_required
def update_the_loai(ten):
    """
    Cập nhật thể loại (Admin only)
    PUT /api/the-loai/<ten>/update
    Body: {
        "mo_ta": "..."
    }
    """
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Chỉ admin mới có quyền sửa thể loại'
        }), 403
    
    data = request.get_json()
    
    try:
        query = """
        MATCH (tl:TheLoai {ten: $ten})
        SET tl.mo_ta = COALESCE($mo_ta, tl.mo_ta)
        RETURN tl
        """
        
        params = {
            'ten': ten,
            'mo_ta': data.get('mo_ta')
        }
        
        result = neo4j_service.execute_write(query, params)
        
        if not result:
            return jsonify({
                'success': False,
                'error': f'Không tìm thấy thể loại: {ten}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': dict(result['tl']),
            'message': 'Cập nhật thể loại thành công'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@the_loai_bp.route('/<ten>/delete', methods=['DELETE'])
@login_required
def delete_the_loai(ten):
    """
    Xóa thể loại (Admin only)
    DELETE /api/the-loai/<ten>/delete
    """
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Chỉ admin mới có quyền xóa thể loại'
        }), 403
    
    try:
        # Kiểm tra có tác phẩm nào đang dùng không
        check_query = """
        MATCH (tp:TacPham)-[:THUOC_THE_LOAI]->(tl:TheLoai {ten: $ten})
        RETURN count(tp) as count
        """
        
        result = neo4j_service.execute_query(check_query, {'ten': ten})
        
        if result and result[0]['count'] > 0:
            return jsonify({
                'success': False,
                'error': f'Không thể xóa! Có {result[0]["count"]} tác phẩm đang thuộc thể loại này'
            }), 400
        
        # Xóa thể loại
        query = """
        MATCH (tl:TheLoai {ten: $ten})
        DETACH DELETE tl
        """
        
        neo4j_service.execute_write(query, {'ten': ten})
        
        return jsonify({
            'success': True,
            'message': f'Đã xóa thể loại: {ten}'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@the_loai_bp.route('/<ten>', methods=['GET'])
def get_the_loai_detail(ten):
    """
    Lấy chi tiết thể loại
    GET /api/the-loai/<ten>
    """
    try:
        query = """
        MATCH (tl:TheLoai {ten: $ten})
        OPTIONAL MATCH (tp:TacPham)-[:THUOC_THE_LOAI]->(tl)
        WITH tl, collect(tp.ten) as tac_pham
        RETURN tl, tac_pham
        """
        
        results = neo4j_service.execute_query(query, {'ten': ten})
        
        if not results:
            return jsonify({
                'success': False,
                'error': f'Không tìm thấy thể loại: {ten}'
            }), 404
        
        tl_data = dict(results[0]['tl'])
        tl_data['tac_pham'] = results[0]['tac_pham']
        
        return jsonify({
            'success': True,
            'data': tl_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500