"""
Routes cho Tác giả
API endpoints để truy vấn thông tin tác giả
"""
from datetime import datetime
import re
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from services.neo4j_service import Neo4jService
from config import Config

tac_gia_bp = Blueprint('tac_gia', __name__, url_prefix='/api/tac-gia')

# Khởi tạo Neo4j service
neo4j_service = Neo4jService(
    uri=Config.NEO4J_URI,
    user=Config.NEO4J_USER,
    password=Config.NEO4J_PASSWORD,
    database=Config.NEO4J_DATABASE
)


@tac_gia_bp.route('/', methods=['GET'])
def get_all_tac_gia():
    """
    Lấy danh sách tất cả tác giả
    GET /api/tac-gia/
    """
    try:
        tac_gia_list = neo4j_service.get_all_tac_gia()
        return jsonify({
            'success': True,
            'data': tac_gia_list,
            'count': len(tac_gia_list)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tac_gia_bp.route('/search', methods=['GET'])
def search_tac_gia():
    keyword = request.args.get('q', '').strip()
    
    if not keyword:
        return jsonify({
            'success': False,
            'error': 'Vui lòng nhập từ khóa tìm kiếm'
        }), 400
    
    try:
        query = """
        MATCH (tg:TacGia)
        WHERE toLower(tg.ten) CONTAINS toLower($keyword)
        OPTIONAL MATCH (tg)-[:SANG_TAC]->(tp:TacPham)
        RETURN tg, collect(tp.ten) AS tac_pham
        """
        
        results = neo4j_service.execute_query(query, {"keyword": keyword})
        
        data = []
        for record in results:
            tg = dict(record['tg'])
            tg['tac_pham'] = record['tac_pham']
            data.append(tg)
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@tac_gia_bp.route('/<ten>', methods=['GET'])
def get_tac_gia_detail(ten):
    try:
        query = """
        MATCH (tg:TacGia {ten: $ten})
        OPTIONAL MATCH (tg)-[:SANG_TAC]->(tp:TacPham)
        
        RETURN 
            tg,
            collect(DISTINCT tp.ten) AS tac_pham
        """

        result = neo4j_service.execute_query(query, {"ten": ten})

        if not result:
            return jsonify({
                'success': False,
                'error': f'Không tìm thấy tác giả: {ten}'
            }), 404

        record = result[0]

        tg = dict(record['tg'])
        tg['tac_pham'] = record['tac_pham']

        return jsonify({
            'success': True,
            'data': tg
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def validate_tac_gia(data):

    errors = []

    nam_hien_tai = datetime.now().year

    ten = str(data.get('ten', '')).strip()

    nam_sinh = data.get('nam_sinh')
    nam_mat = data.get('nam_mat')

    que_quan = str(data.get('que_quan', '')).strip()
    truong_phai = str(data.get('truong_phai', '')).strip()
    tieu_su = str(data.get('tieu_su', '')).strip()

    # =========================
    # TÊN
    # =========================
    if not ten:
        errors.append("Tên tác giả không được để trống")

    elif len(ten) < 2:
        errors.append("Tên tác giả quá ngắn")

    elif len(ten) > 100:
        errors.append("Tên tác giả quá dài")

    # Không cho ký tự lạ
    elif not re.match(r"^[\wÀ-ỹ\s\.\-]+$", ten):
        errors.append("Tên tác giả chứa ký tự không hợp lệ")

    # =========================
    # NĂM SINH
    # =========================
    if nam_sinh:

        try:

            nam_sinh = int(nam_sinh)

            if nam_sinh < 0 or nam_sinh > nam_hien_tai:
                errors.append("Năm sinh không hợp lệ")

        except:
            errors.append("Năm sinh phải là số")

    # =========================
    # NĂM MẤT
    # =========================
    if nam_mat:

        try:

            nam_mat = int(nam_mat)

            if nam_mat < 0 or nam_mat > nam_hien_tai:
                errors.append("Năm mất không hợp lệ")

        except:
            errors.append("Năm mất phải là số")

    # =========================
    # SO SÁNH NĂM
    # =========================
    if nam_sinh and nam_mat:

        if int(nam_sinh) >= int(nam_mat):
            errors.append("Năm sinh phải nhỏ hơn năm mất")

    # =========================
    # QUÊ QUÁN
    # =========================
    if que_quan and len(que_quan) > 1000:
        errors.append("Quê quán quá dài")

    # =========================
    # TRƯỜNG PHÁI
    # =========================
    if truong_phai and len(truong_phai) > 1000:
        errors.append("Trường phái quá dài")

    # =========================
    # TIỂU SỬ
    # =========================
    if tieu_su and len(tieu_su) > 5000:
        errors.append("Tiểu sử quá dài")

    return errors
@tac_gia_bp.route('/create', methods=['POST'])
@login_required
def create_tac_gia():

    # Kiểm tra quyền admin
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Chỉ admin mới có quyền thêm tác giả'
        }), 403

    # 👉 FIX QUAN TRỌNG: hỗ trợ cả JSON và form-data
    data_req = request.get_json(silent=True)
    if not data_req:
        data_req = request.form

    data = {
        'ten': data_req.get('ten'),
        'anh_dai_dien': data_req.get('anh_dai_dien'),
        'nam_sinh': data_req.get('nam_sinh'),
        'nam_mat': data_req.get('nam_mat'),
        'que_quan': data_req.get('que_quan'),
        'truong_phai': data_req.get('truong_phai'),
        'tieu_su': data_req.get('tieu_su'),
        'but_danh': data_req.get('but_danh'),
        'giai_thuong': data_req.get('giai_thuong'),
        'cau_noi_noi_tieng': data_req.get('cau_noi_noi_tieng')
        
    }

    # Normalize dữ liệu rỗng
    if data['ten']:
        data['ten'] = data['ten'].strip()

    # Validate
    errors = validate_tac_gia(data)

    if errors:

        return jsonify({
            'success': False,
            'error': errors
        }), 400
    # =========================
    # CHECK TRÙNG TÊN
    # =========================
    check_query = """
    MATCH (tg:TacGia)
    WHERE toLower(trim(tg.ten)) = toLower(trim($ten))
    RETURN tg
    LIMIT 1
    """

    existing = neo4j_service.execute_query(
        check_query,
        {"ten": data['ten']}
    )

    if existing:

        return jsonify({
            'success': False,
            'error': 'Tác giả đã tồn tại'
        }), 400
    try:
        result = neo4j_service.create_tac_gia(data)

        return jsonify({
            'success': True,
            'data': result,
            'message': 'Tạo tác giả mới thành công'
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tac_gia_bp.route('/<ten>/update', methods=['PUT'])
@login_required
def update_tac_gia(ten):
    """
    Cập nhật thông tin tác giả (Admin only)
    PUT /api/tac-gia/<ten>/update
    """
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Chỉ admin mới có quyền sửa tác giả'
        }), 403
    
    data = request.get_json()
    # =========================
    # VALIDATE
    # =========================
    errors = validate_tac_gia(data)

    if errors:

        return jsonify({
            'success': False,
            'error': errors
        }), 400
    try:
        # Update tác giả
        query = """
            MATCH (t:TacGia {ten: $ten})
            SET t.anh_dai_dien = COALESCE($anh_dai_dien, t.anh_dai_dien),
                t.nam_sinh = COALESCE($nam_sinh, t.nam_sinh),
                t.but_danh = COALESCE($but_danh, t.but_danh),
                t.giai_thuong = COALESCE($giai_thuong, t.giai_thuong),
                t.cau_noi_noi_tieng = COALESCE($cau_noi_noi_tieng, t.cau_noi_noi_tieng),
                t.nam_mat = COALESCE($nam_mat, t.nam_mat),
                t.que_quan = COALESCE($que_quan, t.que_quan),
                t.truong_phai = COALESCE($truong_phai, t.truong_phai),
                t.tieu_su = COALESCE($tieu_su, t.tieu_su)
            RETURN t
            """
        
        params = {"ten": ten, **data}
        result = neo4j_service.execute_write(query, params)
        
        if not result:
            return jsonify({
                'success': False,
                'error': f'Không tìm thấy tác giả: {ten}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': dict(result['t']),
            'message': 'Cập nhật tác giả thành công'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tac_gia_bp.route('/<ten>/delete', methods=['DELETE'])
@login_required
def delete_tac_gia(ten):
    """
    Xóa tác giả (Admin only)
    DELETE /api/tac-gia/<ten>/delete
    """
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Chỉ admin mới có quyền xóa tác giả'
        }), 403
    
    try:
        query = """
        MATCH (t:TacGia {ten: $ten})
        DETACH DELETE t
        """
        
        neo4j_service.execute_write(query, {"ten": ten})
        
        return jsonify({
            'success': True,
            'message': f'Đã xóa tác giả: {ten}'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
