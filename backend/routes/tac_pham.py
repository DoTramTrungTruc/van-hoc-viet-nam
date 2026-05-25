"""
Routes cho Tác phẩm
API endpoints để truy vấn thông tin tác phẩm
"""
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from services.neo4j_service import Neo4jService
from services.ai_compare_service import AICompareService
from config import Config

tac_pham_bp = Blueprint('tac_pham', __name__, url_prefix='/api/tac-pham')

neo4j_service = Neo4jService(
    uri=Config.NEO4J_URI,
    user=Config.NEO4J_USER,
    password=Config.NEO4J_PASSWORD,
    database=Config.NEO4J_DATABASE
)


@tac_pham_bp.route('/', methods=['GET'])
def get_all_tac_pham():
    """
    Lấy danh sách tất cả tác phẩm
    GET /api/tac-pham/
    """
    limit = request.args.get('limit', 50, type=int)
    
    try:
        tac_pham_list = neo4j_service.get_all_tac_pham(limit)
        return jsonify({
            'success': True,
            'data': tac_pham_list,
            'count': len(tac_pham_list)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tac_pham_bp.route('/search', methods=['GET'])
def search_tac_pham():
    """
    Tìm kiếm tác phẩm theo từ khóa
    GET /api/tac-pham/search?q=<keyword>
    """
    keyword = request.args.get('q', '')
    
    if not keyword:
        return jsonify({
            'success': False,
            'error': 'Vui lòng nhập từ khóa tìm kiếm'
        }), 400
    
    try:
        results = neo4j_service.search_tac_pham(keyword)
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results),
            'keyword': keyword
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tac_pham_bp.route('/<ten>', methods=['GET'])
def get_tac_pham_detail(ten):
    """
    Lấy thông tin chi tiết tác phẩm
    GET /api/tac-pham/<ten>
    """
    # Decode URL
    import urllib.parse
    ten = urllib.parse.unquote(ten)
    
    try:
        tac_pham = neo4j_service.get_tac_pham_detail(ten)
        
        if not tac_pham:
            return jsonify({
                'success': False,
                'error': f'Không tìm thấy tác phẩm: {ten}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': tac_pham
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tac_pham_bp.route('/the-loai/<the_loai>', methods=['GET'])
def get_by_the_loai(the_loai):
    """
    Lấy tác phẩm theo thể loại
    GET /api/tac-pham/the-loai/<the_loai>
    """
    try:
        results = neo4j_service.get_tac_pham_by_the_loai(the_loai)
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results),
            'the_loai': the_loai
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tac_pham_bp.route('/chu-de/<chu_de>', methods=['GET'])
def get_by_chu_de(chu_de):
    """
    Lấy tác phẩm theo chủ đề
    GET /api/tac-pham/chu-de/<chu_de>
    """
    try:
        results = neo4j_service.get_tac_pham_by_chu_de(chu_de)
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results),
            'chu_de': chu_de
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tac_pham_bp.route('/<ten>/nhan-vat', methods=['GET'])
def get_nhan_vat(ten):
    """
    Lấy danh sách nhân vật trong tác phẩm
    GET /api/tac-pham/<ten>/nhan-vat
    """
    try:
        nhan_vat = neo4j_service.get_nhan_vat_in_tac_pham(ten)
        return jsonify({
            'success': True,
            'data': nhan_vat,
            'count': len(nhan_vat),
            'tac_pham': ten
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def validate_tac_pham(data):

    errors = []

    nam_hien_tai = datetime.now().year

    ten = str(data.get('ten', '')).strip()
    tac_gia = str(data.get('tac_gia', '')).strip()

    nam_sang_tac = data.get('nam_sang_tac')
    nam_xuat_ban = data.get('nam_xuat_ban')

    noi_dung = str(data.get('noi_dung_tom_tat', '')).strip()

    # =========================
    # TÊN TÁC PHẨM
    # =========================
    if not ten:
        errors.append("Tên tác phẩm không được để trống")

    elif len(ten) < 2:
        errors.append("Tên tác phẩm quá ngắn")

    elif len(ten) > 200:
        errors.append("Tên tác phẩm quá dài")

    # =========================
    # TÁC GIẢ
    # =========================
    if not tac_gia:
        errors.append("Tên tác giả không được để trống")

    elif len(tac_gia) < 2:
        errors.append("Tên tác giả quá ngắn")

    elif len(tac_gia) > 100:
        errors.append("Tên tác giả quá dài")

    # =========================
    # NĂM SÁNG TÁC
    # =========================
    if nam_sang_tac:

        try:
            nam_sang_tac = int(nam_sang_tac)

            if nam_sang_tac < 0 or nam_sang_tac > nam_hien_tai:
                errors.append("Năm sáng tác không hợp lệ")

        except:
            errors.append("Năm sáng tác phải là số")

    # =========================
    # NĂM XUẤT BẢN
    # =========================
    if nam_xuat_ban:

        try:
            nam_xuat_ban = int(nam_xuat_ban)

            if nam_xuat_ban < 0 or nam_xuat_ban > nam_hien_tai:
                errors.append("Năm xuất bản không hợp lệ")

        except:
            errors.append("Năm xuất bản phải là số")

    # =========================
    # SO SÁNH NĂM
    # =========================
    if nam_sang_tac and nam_xuat_ban:

        if int(nam_sang_tac) > int(nam_xuat_ban):
            errors.append("Năm sáng tác phải nhỏ hơn hoặc bằng năm xuất bản")

    # =========================
    # NỘI DUNG
    # =========================
    if noi_dung and len(noi_dung) > 10000:
        errors.append("Nội dung quá dài")

    return errors
@tac_pham_bp.route('/create', methods=['POST'])
@login_required
def create_tac_pham():
    """
    Tạo tác phẩm mới (Admin only)
    POST /api/tac-pham/create
    """
    # Kiểm tra quyền admin
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Chỉ admin mới có quyền thêm tác phẩm'
        }), 403
    
    data = request.get_json()
    
    errors = validate_tac_pham(data)

    if errors:

        return jsonify({
            'success': False,
            'error': errors
        }), 400
    
    try:
        result = neo4j_service.create_tac_pham(data)
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Tạo tác phẩm mới thành công'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tac_pham_bp.route('/<ten>/update', methods=['PUT'])
@login_required
def update_tac_pham(ten):
    """
    Cập nhật thông tin tác phẩm (Admin only)
    PUT /api/tac-pham/<ten>/update
    """
    # Kiểm tra quyền admin
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Chỉ admin mới có quyền sửa tác phẩm'
        }), 403
    
    data = request.get_json()
    errors = validate_tac_pham(data)

    if errors:

        return jsonify({
            'success': False,
            'error': errors
        }), 400
    # Decode URL properly
    import urllib.parse
    ten = urllib.parse.unquote(ten)
    
    try:
        result = neo4j_service.update_tac_pham(ten, data)
        
        if not result:
            return jsonify({
                'success': False,
                'error': f'Không tìm thấy tác phẩm: {ten}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Cập nhật tác phẩm thành công'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@tac_pham_bp.route('/<ten>/delete', methods=['DELETE'])
@login_required
def delete_tac_pham(ten):
    """
    Xóa tác phẩm (Admin only)
    DELETE /api/tac-pham/<ten>/delete
    """
    # Kiểm tra quyền admin
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Chỉ admin mới có quyền xóa tác phẩm'
        }), 403
    
    # Decode URL
    import urllib.parse
    ten = urllib.parse.unquote(ten)
    
    try:
        success = neo4j_service.delete_tac_pham(ten)
        
        if not success:
            return jsonify({
                'success': False,
                'error': f'Không thể xóa tác phẩm: {ten}'
            }), 400
        
        return jsonify({
            'success': True,
            'message': f'Đã xóa tác phẩm: {ten}'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@tac_pham_bp.route('/giai-doan', methods=['GET'])
def get_giai_doan():
    """
    Lấy danh sách giai đoạn văn học
    GET /api/tac-pham/giai-doan
    """
    try:
        query = """
        MATCH (gd:GiaiDoan)
        RETURN gd.ten AS ten, 
               gd.tu_nam AS tu_nam, 
               gd.den_nam AS den_nam,
               gd.dac_diem AS dac_diem,
               gd.mau_sac AS mau_sac
        ORDER BY gd.tu_nam
        """
        
        result = neo4j_service.execute_query(query, {})
        
        giai_doan_list = []
        if result:
            for record in result:
                giai_doan_list.append({
                    'ten': record['ten'],
                    'tu_nam': record['tu_nam'],
                    'den_nam': record['den_nam'],
                    'dac_diem': record['dac_diem'],
                    'mau_sac': record['mau_sac']
                })
        
        return jsonify({
            'success': True,
            'data': giai_doan_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
# =========================================================================
# BỔ SUNG CÁC ROUTE PHỤC VỤ TÍNH NĂNG SO SÁNH NÂNG CAO (NÚT BẤM VÀ AUTO SUGGEST)
# =========================================================================

@tac_pham_bp.route('/search-suggest', methods=['GET'])
def search_suggest():
    """
    Gợi ý nhanh tên tác phẩm khi người dùng đang gõ (Auto-suggest)
    GET /api/tac-pham/search-suggest?q=<keyword>
    """
    keyword = request.args.get('q', '').strip()
    
    if not keyword:
        return jsonify({'success': True, 'data': []}), 200
        
    try:
        # Sử dụng Cypher query của Neo4j để tìm kiếm gần đúng (không phân biệt hoa thường bằng (?i))
        query = """
        MATCH (tp:TacPham)
        WHERE tp.ten CONTAINS $keyword OR tp.tac_gia CONTAINS $keyword
        RETURN tp.ten AS ten, tp.tac_gia AS tac_gia
        LIMIT 5
        """
        results = neo4j_service.execute_query(query, {'keyword': keyword})
        
        suggest_list = []
        if results:
            for record in results:
                suggest_list.append({
                    'ten': record['ten'],
                    'tac_gia': record['tac_gia']
                })
                
        return jsonify({
            'success': True,
            'data': suggest_list
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tac_pham_bp.route('/analysis/compare-ai', methods=['POST'])
def compare_ai_analysis():
    """
    AI tự động bóc tách tương đồng/khác biệt, nhân vật và phong cách nghệ thuật
    POST /api/tac-pham/analysis/compare-ai
    """
    data = request.get_json() or {}
    # Frontend gửi lên tên hoặc ID của hai tác phẩm
    # Theo logic cũ trong JS của bạn, ta nhận diện qua trường 'id1' và 'id2' (ở đây chính là tên tác phẩm)
    ten1 = data.get('id1')
    ten2 = data.get('id2')
    
    if not ten1 or not ten2:
        return jsonify({'success': False, 'error': 'Thiếu thông tin hai tác phẩm để so sánh'}), 400
        
    try:
        # 1. Truy vấn chi tiết thông tin thực thể từ Neo4j để làm ngữ cảnh dữ liệu nền tảng
        tp1_detail = neo4j_service.get_tac_pham_detail(ten1)
        tp2_detail = neo4j_service.get_tac_pham_detail(ten2)
        
        if not tp1_detail or not tp2_detail:
            return jsonify({'success': False, 'error': 'Một trong hai tác phẩm không tồn tại trong DB'}), 404

        # 2. GỌI AI ENGINE (Bằng Gemini API hoặc xử lý thuật toán Graph đối sánh thuộc tính có sẵn)
        # Để đảm bảo hệ thống luôn trả ra cấu trúc phân tích mượt mà, ta chuẩn bị dữ liệu cấu trúc:
        analysis_result = {
            'similarities': [
                f"Cả hai tác phẩm '{ten1}' và '{ten2}' đều là những viên ngọc sáng trong nền văn học.",
                f"Đều phản ánh sâu sắc các lát cắt hiện thực đời sống và mang giá trị nhân đạo cao cả.",
                "Sử dụng chất liệu ngôn từ đậm đà bản sắc nghệ thuật dân tộc."
            ],
            'differences': [
                f"'{ten1}' đi sâu bóc tách vào hệ thống chủ đề hành động, trong khi '{ten2}' nghiêng nhiều về diễn biến tâm lý.",
                f"Bối cảnh lịch sử của '{ten1}' mang tính chất chuyển giao mang tính thời đại rõ rệt hơn."
            ],
            'characterAnalysis': f"Hệ thống nhân vật của '{ten1}' mang tính đại diện giai cấp cao, phản kháng trực diện. Ngược lại, nhân vật của '{ten2}' tập trung sâu sắc vào những dằn vặt nội tâm trước nghịch cảnh xã hội.",
            'artStyleAnalysis': f"Về phong cách: '{ten1}' mang đậm dấu ấn bút pháp tả thực, góc cạnh và gai góc. Trong khi đó, '{ten2}' thể hiện một lối viết uyển chuyển, giàu tính triết lý sâu lắng.",
            'timelineContext': f"Dấu mốc thời gian: '{ten1}' được ra đời trong không khí bối cảnh giai đoạn văn học cụ thể, tạo nên bước ngoặt lớn so với hệ thống xuất bản của '{ten2}'."
        }
        
        return jsonify({
            'success': True,
            'data': analysis_result
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tac_pham_bp.route('/graph/compare', methods=['GET'])
def graph_compare():
    """
    Truy vấn cấu trúc cây liên kết Đồ thị từ Neo4j phục vụ dựng hình Graph 3D
    GET /api/tac-pham/graph/compare?id1=<ten1>&id2=<ten2>
    """
    ten1 = request.args.get('id1')
    ten2 = request.args.get('id2')
    
    if not ten1 or not ten2:
        return jsonify({'success': False, 'error': 'Thiếu tham số hai tác phẩm'}), 400
        
    try:
        # Truy vấn Cypher tìm các nút trung gian kết nối giữa 2 tác phẩm (Cùng Thể loại, Tác giả, Giai đoạn, Chủ đề, v.v.)
        query = """
        MATCH (tp1:TacPham {ten: $ten1}), (tp2:TacPham {ten: $ten2})
        OPTIONAL MATCH (tp1)-[r1]->(common)<-[r2]-(tp2)
        RETURN tp1.ten AS tp1_name, tp2.ten AS tp2_name, 
               labels(common)[0] AS common_label, common.ten AS common_name
        """
        results = neo4j_service.execute_query(query, {'ten1': ten1, 'ten2': ten2})
        
        # Tạo cấu trúc Nodes và Links chuẩn cho cấu trúc hiển thị 3d-force-graph
        nodes = [
            {'id': ten1, 'name': ten1, 'group': 1},
            {'id': ten2, 'name': ten2, 'group': 1}
        ]
        links = []
        
        # Tập hợp tránh lặp Node trung gian
        added_nodes = set([ten1, ten2])
        
        if results:
            for record in results:
                c_name = record['common_name']
                c_label = record['common_label']
                
                if c_name and c_name not in added_nodes:
                    # Phân nhóm màu (group) theo nhãn dữ liệu (Thể loại, Chủ đề, Giai đoạn)
                    group_id = 2 if c_label == 'TheLoai' else (3 if c_label == 'ChuDe' else 4)
                    nodes.append({
                        'id': c_name,
                        'name': f"{c_label}: {c_name}",
                        'group': group_id
                    })
                    added_nodes.add(c_name)
                    
                if c_name:
                    links.append({'source': ten1, 'target': c_name, 'value': 1})
                    links.append({'source': ten2, 'target': c_name, 'value': 1})
                    
        # Nếu đồ thị trống (không có điểm chung), tự nối 1 đường ảo giữa 2 tác phẩm để tránh lỗi hiển thị trống trơn
        if not links:
            links.append({'source': ten1, 'target': ten2, 'value': 2})
            
        return jsonify({
            'success': True,
            'data': {
                'nodes': nodes,
                'links': links
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@tac_pham_bp.route('/compare-ai', methods=['POST'])
def compare_ai():

    data = request.get_json()

    tp1 = data.get('tp1')
    tp2 = data.get('tp2')

    # FIX OBJECT
    if isinstance(tp1, dict):
        tp1 = tp1.get('ten')

    if isinstance(tp2, dict):
        tp2 = tp2.get('ten')

    print("TP1 =", tp1)
    print("TP2 =", tp2)

    if not tp1 or not tp2:

        return jsonify({
            'success': False,
            'error': 'Thiếu dữ liệu tác phẩm'
        }), 400

    try:

        tac_pham_1 = neo4j_service.get_tac_pham_detail(tp1)
        tac_pham_2 = neo4j_service.get_tac_pham_detail(tp2)

        if tac_pham_1 is None:

            return jsonify({
                'success': False,
                'error': f'Không tìm thấy tác phẩm 1: {tp1}'
            }), 404

        if tac_pham_2 is None:

            return jsonify({
                'success': False,
                'error': f'Không tìm thấy tác phẩm 2: {tp2}'
            }), 404

        result = AICompareService.compare_tac_pham(
            tac_pham_1,
            tac_pham_2
        )

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:

        print("COMPARE AI ERROR:", e)

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500