"""
Routes cho Hỏi đáp (Q&A)
API endpoints cho tính năng hỏi đáp tự nhiên
"""

from flask import Blueprint, jsonify, request
from services.neo4j_service import Neo4jService
from services.nlp_service import nlp_service
from services.cypher_mapper import cypher_mapper
from config import Config
import logging

logger = logging.getLogger(__name__)

qa_bp = Blueprint('qa', __name__, url_prefix='/api/qa')

# Khởi tạo Neo4j service
neo4j_service = Neo4jService(
    uri=Config.NEO4J_URI,
    user=Config.NEO4J_USER,
    password=Config.NEO4J_PASSWORD,
    database=Config.NEO4J_DATABASE
)


@qa_bp.route('/ask', methods=['POST'])
def ask_question():
    """
    Hỏi câu hỏi tự nhiên
    POST /api/qa/ask
    Body: {
        "question": "Truyện Kiều do ai sáng tác?"
    }
    """
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Vui lòng nhập câu hỏi',
                'error_type': 'empty'
            }), 400
        
        # Bước 1: Phân tích câu hỏi bằng NLP (bao gồm validation)
        analysis = nlp_service.analyze_question(question)
        
        # ✅ KIỂM TRA VALIDATION
        if not analysis.get('is_valid', True):
            return jsonify({
                'success': False,
                'error': analysis.get('error_message', 'Câu hỏi không hợp lệ'),
                'error_type': analysis.get('error_type', 'invalid'),
                'suggestions': analysis.get('suggestions', [])
            }), 400
        
        # Bước 2: Ánh xạ sang Cypher query
        query_map = cypher_mapper.map_to_query(analysis)
        
        # Bước 3: Thực thi query
        results = neo4j_service.execute_query(
            query_map['query'], 
            query_map['params']
        )
        
        # Bước 4: Format kết quả
        if results:
            # Tạo câu trả lời văn bản
            answer_text = format_answer(results, query_map, analysis)
            
            # Tạo dữ liệu đồ thị
            graph_data = generate_graph_data(results, query_map['intent'])
            
            return jsonify({
                'success': True,
                'data': {
                    'question': question,
                    'answer': answer_text,
                    'results': results,
                    'graph_data': graph_data,
                    'intent': analysis['intent'],
                    'entities': analysis['entities']
                }
            }), 200
        else:
            return jsonify({
                'success': True,
                'data': {
                    'question': question,
                    'answer': 'Xin lỗi, tôi không tìm thấy thông tin phù hợp. Vui lòng thử câu hỏi khác.',
                    'results': [],
                    'graph_data': {'nodes': [], 'edges': []},
                    'intent': analysis['intent']
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Error in ask_question: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Lỗi xử lý câu hỏi: {str(e)}',
            'error_type': 'server_error'
        }), 500


@qa_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    """
    Lấy gợi ý câu hỏi
    GET /api/qa/suggestions
    """
    try:
        suggestions = nlp_service.suggest_questions()
        
        return jsonify({
            'success': True,
            'data': suggestions
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_suggestions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@qa_bp.route('/graph/<entity_name>', methods=['GET'])
def get_entity_graph(entity_name):
    """
    Lấy đồ thị cho một entity cụ thể
    GET /api/qa/graph/<entity_name>
    """
    try:
        # Query lấy toàn bộ relationships của entity
        query = """
        MATCH path = (start)-[r]-(end)
        WHERE start.ten = $name OR end.ten = $name
        RETURN start, r, end
        LIMIT 50
        """
        
        results = neo4j_service.execute_query(query, {'name': entity_name})
        
        # Generate graph data
        graph_data = {
            'nodes': [],
            'edges': []
        }
        
        node_ids = set()
        
        for record in results:
            # Start node
            if 'start' in record:
                start = record['start']
                node_id = f"{start.get('ten', 'unknown')}"
                if node_id not in node_ids:
                    graph_data['nodes'].append({
                        'id': node_id,
                        'label': start.get('ten', 'Unknown'),
                        'group': get_node_type(start)
                    })
                    node_ids.add(node_id)
            
            # End node
            if 'end' in record:
                end = record['end']
                node_id = f"{end.get('ten', 'unknown')}"
                if node_id not in node_ids:
                    graph_data['nodes'].append({
                        'id': node_id,
                        'label': end.get('ten', 'Unknown'),
                        'group': get_node_type(end)
                    })
                    node_ids.add(node_id)
            
            # Edge
            if 'r' in record:
                rel = record['r']
                graph_data['edges'].append({
                    'from': record['start'].get('ten'),
                    'to': record['end'].get('ten'),
                    'label': rel.type if hasattr(rel, 'type') else 'RELATES_TO'
                })
        
        return jsonify({
            'success': True,
            'data': graph_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_entity_graph: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Helper functions

def format_answer(results: list, query_map: dict, analysis: dict) -> str:
    """Format kết quả thành câu trả lời tự nhiên"""
    
    if not results:
        return "Không tìm thấy kết quả phù hợp."
    
    intent = query_map['intent']
    result = results[0]
    
    # Format theo intent
    if intent == 'tim_tac_gia':
        if 'tac_gia' in result:
            return f"Tác phẩm '{result.get('tac_pham')}' do {result.get('tac_gia')} sáng tác năm {result.get('nam_sang_tac', 'không rõ')}."
    
    elif intent == 'tim_nhan_vat':
        if 'nhan_vat' in result:
            nhan_vat_list = result['nhan_vat']
            if nhan_vat_list:
                nv_text = ', '.join([f"{nv['ten']} ({nv.get('vai_tro', 'nhân vật')})" for nv in nhan_vat_list])
                return f"Các nhân vật trong '{result.get('tac_pham')}': {nv_text}."
    
    elif intent == 'tim_tac_pham':
        if 'tac_pham' in result:
            works = result['tac_pham']
            if works:
                works_text = ', '.join([w['ten'] for w in works])
                return f"{result.get('tac_gia')} có các tác phẩm: {works_text}."
    
    elif intent == 'tim_the_loai':
        if 'the_loai' in result:
            return f"'{result.get('tac_pham')}' thuộc thể loại {result.get('the_loai')}."
    
    elif intent == 'tim_quan_he':
        if 'loai_quan_he' in result:
            return f"Mối quan hệ giữa {result.get('nhan_vat_1')} và {result.get('nhan_vat_2')}: {result.get('loai_quan_he')}. {result.get('mo_ta', '')}".strip()
    
    elif intent == 'chi_tiet':
        if 'ten' in result:
            parts = [f"Thông tin về '{result['ten']}':"]
            if 'tac_gia' in result:
                parts.append(f"Tác giả: {result['tac_gia']}")
            if 'nam_sang_tac' in result:
                parts.append(f"Năm sáng tác: {result['nam_sang_tac']}")
            if 'the_loai' in result:
                parts.append(f"Thể loại: {result['the_loai']}")
            if 'noi_dung' in result and result['noi_dung']:
                parts.append(f"Nội dung: {result['noi_dung'][:200]}...")
            return ' | '.join(parts)
    
    # Default: trả về result đầu tiên dạng text
    return f"Kết quả: {str(result)}"


def generate_graph_data(results: list, intent: str) -> dict:
    """Tạo dữ liệu đồ thị từ kết quả"""
    
    graph_data = {
        'nodes': [],
        'edges': []
    }
    
    node_ids = set()
    
    for result in results:
        # Tùy intent mà tạo nodes/edges khác nhau
        
        if intent == 'tim_tac_gia':
            # Node: Tác giả
            if 'tac_gia' in result:
                tg_id = result['tac_gia']
                if tg_id not in node_ids:
                    graph_data['nodes'].append({
                        'id': tg_id,
                        'label': tg_id,
                        'group': 'author'
                    })
                    node_ids.add(tg_id)
            
            # Node: Tác phẩm
            if 'tac_pham' in result:
                tp_id = result['tac_pham']
                if tp_id not in node_ids:
                    graph_data['nodes'].append({
                        'id': tp_id,
                        'label': tp_id,
                        'group': 'work'
                    })
                    node_ids.add(tp_id)
                
                # Edge: Tác giả -> Tác phẩm
                graph_data['edges'].append({
                    'from': result['tac_gia'],
                    'to': tp_id,
                    'label': 'SANG_TAC'
                })
        
        elif intent == 'tim_nhan_vat':
            # Node: Tác phẩm
            if 'tac_pham' in result:
                tp_id = result['tac_pham']
                if tp_id not in node_ids:
                    graph_data['nodes'].append({
                        'id': tp_id,
                        'label': tp_id,
                        'group': 'work'
                    })
                    node_ids.add(tp_id)
                
                # Nodes: Nhân vật
                if 'nhan_vat' in result:
                    for nv in result['nhan_vat']:
                        nv_id = nv['ten']
                        if nv_id not in node_ids:
                            graph_data['nodes'].append({
                                'id': nv_id,
                                'label': nv_id,
                                'group': 'character'
                            })
                            node_ids.add(nv_id)
                        
                        # Edge: Tác phẩm -> Nhân vật
                        graph_data['edges'].append({
                            'from': tp_id,
                            'to': nv_id,
                            'label': nv.get('vai_tro', 'CO_NHAN_VAT')
                        })
    
    return graph_data


def get_node_type(node: dict) -> str:
    """Xác định loại node"""
    # Simple heuristic based on properties
    if 'nam_sinh' in node or 'que_quan' in node:
        return 'author'
    elif 'vai_tro' in node or 'tinh_cach' in node:
        return 'character'
    elif 'nam_sang_tac' in node or 'noi_dung_tom_tat' in node:
        return 'work'
    elif 'mo_ta' in node:
        return 'genre'
    else:
        return 'other'