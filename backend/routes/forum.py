"""
Forum Routes - API endpoints cho diễn đàn văn học
"""

from flask import Blueprint, request, jsonify, session, current_app
from services.forum_service import ForumService
from neo4j import GraphDatabase
forum_bp = Blueprint('forum', __name__, url_prefix='/api/forum')

def get_forum():
    from flask import current_app
    return ForumService(current_app.neo4j_service)

from flask_login import current_user


def get_current_user():
    if current_user.is_authenticated:
        return current_user.username, current_user.is_admin
    return None, False


def require_login():
    if not current_user.is_authenticated:
        return jsonify({
            "success": False,
            "error": "Chưa đăng nhập"
        }), 401
    return None
# ========== POSTS ==========

@forum_bp.route('/posts', methods=['GET'])
def get_posts():
    uid, _ = get_current_user()
    page      = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    tag_type  = request.args.get('tag_type', '') or None
    tag_name  = request.args.get('tag_name', '') or None

    data = get_forum().get_posts(
        page=page, page_size=page_size,
        user_id=uid, tag_type=tag_type, tag_name=tag_name
    )
    return jsonify({"success": True, "data": data})


@forum_bp.route('/posts', methods=['POST'])
def create_post():
    err = require_login()
    if err: return err

    uid, _ = get_current_user()
    body   = request.get_json() or {}

    if not body.get('content', '').strip():
        return jsonify({"success": False, "error": "Nội dung không được để trống"}), 400

    post = get_forum().create_post(uid, body)
    if not post:
        return jsonify({"success": False, "error": "Không thể tạo bài viết"}), 500

    return jsonify({"success": True, "data": post}), 201


@forum_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    uid, _ = get_current_user()
    post   = get_forum().get_post_detail(post_id, user_id=uid)
    if not post:
        return jsonify({"success": False, "error": "Không tìm thấy bài viết"}), 404
    return jsonify({"success": True, "data": post})


@forum_bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    err = require_login()
    if err: return err

    uid, is_admin = get_current_user()
    ok = get_forum().delete_post(post_id, uid, is_admin)
    if not ok:
        return jsonify({"success": False, "error": "Không có quyền xóa"}), 403
    return jsonify({"success": True})


# ========== REACTIONS ==========

@forum_bp.route('/posts/<int:post_id>/react', methods=['POST'])
def react_post(post_id):
    err = require_login()
    if err: return err

    uid, _ = get_current_user()
    emoji  = (request.get_json() or {}).get('emoji', '👍')

    result = get_forum().react_post(post_id, uid, emoji)
    return jsonify({"success": True, "data": result})


# ========== COMMENTS ==========

@forum_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    err = require_login()
    if err: return err

    uid, _ = get_current_user()
    content = (request.get_json() or {}).get('content', '').strip()

    if not content:
        return jsonify({"success": False, "error": "Bình luận không được trống"}), 400

    comment = get_forum().add_comment(post_id, uid, content)
    if not comment:
        return jsonify({"success": False, "error": "Không thể thêm bình luận"}), 500

    return jsonify({"success": True, "data": comment}), 201


@forum_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    err = require_login()
    if err: return err

    uid, is_admin = get_current_user()
    ok = get_forum().delete_comment(comment_id, uid, is_admin)
    if not ok:
        return jsonify({"success": False, "error": "Không có quyền xóa"}), 403
    return jsonify({"success": True})

@forum_bp.route('/stats', methods=['GET'])
def forum_stats():
    forum = get_forum()

    post_count = forum.db.execute_query("""
        MATCH (p:BaiViet)
        RETURN count(p) AS total
    """)[0]["total"]

    comment_count = forum.db.execute_query("""
        MATCH (c:BinhLuan)
        RETURN count(c) AS total
    """)[0]["total"]

    return jsonify({
        "success": True,
        "data": {
            "posts": post_count,
            "comments": comment_count
        }
    })