"""
Forum Service - Dịch vụ diễn đàn văn học
Xử lý bài viết, bình luận, cảm xúc
"""

import time
import logging
from typing import List, Dict, Optional, Any
from neo4j import GraphDatabase
logger = logging.getLogger(__name__)


class ForumService:
    def __init__(self, neo4j_service):
        self.db = neo4j_service

    # ========== HELPER ==========

    def _now_ms(self):
        return int(time.time() * 1000)

    def _next_id(self, label: str) -> int:
        result = self.db.execute_query(
            f"MATCH (n:{label}) RETURN COALESCE(MAX(n.id), 0) AS max_id"
        )
        return (result[0]["max_id"] if result else 0) + 1

    # ========== POSTS ==========

    def create_post(self, user_id: int, data: Dict) -> Optional[Dict]:
        """Tạo bài viết mới"""
        try:
            post_id = self._next_id("BaiViet")
            now = self._now_ms()

            query = """
            MATCH (u:User {username: $user_id})
            CREATE (p:BaiViet{
                id:         $id,
                title:      $title,
                content:    $content,
                tag_type:   $tag_type,
                tag_name:   $tag_name,
                created_at: $now,
                updated_at: $now
            })
            CREATE (u)-[:DA_DANG]->(p)
            RETURN p, u.username AS username, u.full_name AS full_name,
                   u.anh_dai_dien AS anh_dai_dien
            """
            result = self.db.execute_query(query, {
                "user_id":  user_id,
                "id":       post_id,
                "title":    data.get("title", ""),
                "content":  data.get("content", ""),
                "tag_type": data.get("tag_type", ""),   # "tac_pham" | "tac_gia" | ""
                "tag_name": data.get("tag_name", ""),
                "now":      now,
            })

            if not result:
                return None

            row = result[0]
            p = dict(row["p"])
            p["username"]     = row["username"]
            p["full_name"]    = row["full_name"]
            p["anh_dai_dien"] = row["anh_dai_dien"]
            p["reactions"]    = {}
            p["comment_count"]= 0
            p["user_reaction"]= None
            return p

        except Exception as e:
            logger.error(f"create_post error: {e}", exc_info=True)
            return None

    def get_posts(self, page: int = 1, page_size: int = 10,
                  user_id: int = None, tag_type: str = None,
                  tag_name: str = None) -> Dict:
        """Lấy danh sách bài viết (có phân trang)"""
        skip = (page - 1) * page_size

        filters = []
        params: Dict[str, Any] = {"skip": skip, "limit": page_size}

        if tag_type:
            filters.append("p.tag_type = $tag_type")
            params["tag_type"] = tag_type
        if tag_name:
            filters.append("p.tag_name = $tag_name")
            params["tag_name"] = tag_name

        where = ("WHERE " + " AND ".join(filters)) if filters else ""

        count_q = f"MATCH (p:BaiViet) {where} RETURN count(p) AS total"
        total = (self.db.execute_query(count_q, params) or [{}])[0].get("total", 0)

        query = f"""
        MATCH (u:User)-[:DA_DANG]->(p:BaiViet)
        {where}

        // reactions
        OPTIONAL MATCH (p)<-[rc:THA_CAM_XUC]->()
        WITH p, u,
             collect(DISTINCT rc) AS all_rc

        // comments count
        OPTIONAL MATCH (p)<-[:BINH_LUAN]-(c:BinhLuan)
        WITH p, u, all_rc, count(DISTINCT c) AS comment_count

        RETURN p,
               u.username     AS username,
               u.full_name    AS full_name,
               u.anh_dai_dien AS anh_dai_dien,
               all_rc, comment_count

        ORDER BY p.created_at DESC
        SKIP $skip LIMIT $limit
        """

        rows = self.db.execute_query(query, params) or []
        posts = []

        for row in rows:
            p = dict(row["p"])
            p["username"]      = row["username"]
            p["full_name"]     = row["full_name"]
            p["anh_dai_dien"]  = row["anh_dai_dien"]
            p["comment_count"] = row["comment_count"]

            # aggregate reactions
            reactions: Dict[str, int] = {}
            for rc in (row["all_rc"] or []):
                emoji = dict(rc).get("emoji", "👍")
                reactions[emoji] = reactions.get(emoji, 0) + 1
            p["reactions"] = reactions

            # current user reaction
            # current user reaction
            p["user_reaction"] = None

            if user_id:
                ur = self.db.execute_query(
                    """
                    MATCH (u:User {username:$uid})-[r:THA_CAM_XUC]->(p:BaiViet{id:$pid})
                    RETURN r.emoji AS e
                    """,
                    {
                        "uid": user_id,
                        "pid": p["id"]
                    }
                )

                if ur:
                    p["user_reaction"] = ur[0]["e"]

            posts.append(p)

        return {"posts": posts, "total": total,
                "page": page, "page_size": page_size,
                "total_pages": -(-total // page_size)}

    def get_post_detail(self, post_id: int, user_id: int = None) -> Optional[Dict]:
        """Chi tiết 1 bài viết kèm bình luận"""
        query = """
        MATCH (u:User)-[:DA_DANG]->(p:BaiViet{id: $id})
        OPTIONAL MATCH (p)<-[rc:THA_CAM_XUC]-(:User)
        OPTIONAL MATCH (c:BinhLuan)-[:BINH_LUAN]->(p)
        OPTIONAL MATCH (cu:User)-[:DA_DANG]->(c)
        WITH p, u,
             collect(DISTINCT rc) AS all_rc,
             collect(DISTINCT {
                 id:         c.id,
                 content:    c.content,
                 created_at: c.created_at,
                 username:   cu.username,
                 full_name:  cu.full_name,
                 anh_dai_dien: cu.anh_dai_dien
             }) AS comments
        RETURN p,
               u.username     AS username,
               u.full_name    AS full_name,
               u.anh_dai_dien AS anh_dai_dien,
               all_rc, comments
        """
        rows = self.db.execute_query(query, {"id": post_id})
        if not rows:
            return None

        row = rows[0]
        p = dict(row["p"])
        p["username"]     = row["username"]
        p["full_name"]    = row["full_name"]
        p["anh_dai_dien"] = row["anh_dai_dien"]

        reactions: Dict[str, int] = {}
        for rc in (row["all_rc"] or []):
            emoji = dict(rc).get("emoji", "👍")
            reactions[emoji] = reactions.get(emoji, 0) + 1
        p["reactions"] = reactions

        p["user_reaction"] = None
        if user_id:
            ur = self.db.execute_query(
                "MATCH (u:User {username:$uid})-[r:THA_CAM_XUC]->(p:BaiViet{id:$pid}) RETURN r.emoji AS e",
                {"uid": user_id, "pid": post_id}
            )
            if ur:
                p["user_reaction"] = ur[0]["e"]

        # clean comments
        comments = [c for c in (row["comments"] or []) if c.get("id")]
        comments.sort(key=lambda x: x.get("created_at", 0))
        p["comments"] = comments
        p["comment_count"] = len(comments)
        return p

    def delete_post(self, post_id: int, user_id: str, is_admin: bool = False) -> bool:
        """Xóa bài viết + comments + reactions"""
        
        check = self.db.execute_query(
            """
            MATCH (u:User)-[:DA_DANG]->(p:BaiViet{id:$id})
            RETURN u.username AS username
            """,
            {"id": post_id}
        )

        if not check:
            return False

        # Chỉ chủ bài viết hoặc admin được xóa
        if not is_admin and check[0]["username"] != user_id:
            return False

        # Xóa comments + reactions + post
        self.db.execute_query(
            """
            MATCH (p:BaiViet{id:$id})

            // comments
            OPTIONAL MATCH (c:BinhLuan)-[:BINH_LUAN]->(p)

            // reactions
            OPTIONAL MATCH ()-[r:THA_CAM_XUC]->(p)

            DETACH DELETE c, r, p
            """,
            {"id": post_id}
        )

        return True

    # ========== REACTIONS ==========

    def react_post(self, post_id: int, user_id: str, emoji: str) -> Dict:
        """Thả / đổi / bỏ cảm xúc"""

        # Kiểm tra user đã react chưa
        existing = self.db.execute_query(
            """
            MATCH (u:User {username:$uid})-[r:THA_CAM_XUC]->(p:BaiViet{id:$pid})
            RETURN r.emoji AS e
            """,
            {
                "uid": user_id,
                "pid": post_id
            }
        )

        # ===== Đã có react =====
        if existing:
            old = existing[0]["e"]

            # Bấm lại emoji cũ => bỏ react
            if old == emoji:
                self.db.execute_query(
                    """
                    MATCH (u:User {username:$uid})-[r:THA_CAM_XUC]->(p:BaiViet{id:$pid})
                    DELETE r
                    """,
                    {
                        "uid": user_id,
                        "pid": post_id
                    }
                )

                action = "removed"

            # Đổi emoji khác
            else:
                self.db.execute_query(
                    """
                    MATCH (u:User {username:$uid})-[r:THA_CAM_XUC]->(p:BaiViet{id:$pid})
                    SET r.emoji = $e
                    """,
                    {
                        "uid": user_id,
                        "pid": post_id,
                        "e": emoji
                    }
                )

                action = "changed"

        # ===== Chưa có react =====
        else:
            self.db.execute_query(
                """
                MATCH (u:User {username:$uid}), (p:BaiViet{id:$pid})

                CREATE (u)-[:THA_CAM_XUC {
                    emoji: $e,
                    created_at: $now
                }]->(p)
                """,
                {
                    "uid": user_id,
                    "pid": post_id,
                    "e": emoji,
                    "now": self._now_ms()
                }
            )

            action = "added"

        # ===== Tổng hợp reactions =====
        rows = self.db.execute_query(
            """
            MATCH ()-[r:THA_CAM_XUC]->(p:BaiViet{id:$pid})
            RETURN r.emoji AS e
            """,
            {
                "pid": post_id
            }
        )

        totals = {}

        for r in rows:
            e = r["e"]
            totals[e] = totals.get(e, 0) + 1

        # ===== User reaction hiện tại =====
        ur = self.db.execute_query(
            """
            MATCH (u:User {username:$uid})-[r:THA_CAM_XUC]->(p:BaiViet{id:$pid})
            RETURN r.emoji AS e
            """,
            {
                "uid": user_id,
                "pid": post_id
            }
        )

        user_reaction = ur[0]["e"] if ur else None

        return {
            "action": action,
            "reactions": totals,
            "user_reaction": user_reaction
        }

    # ========== COMMENTS ==========

    def add_comment(self, post_id: int, user_id: str, content: str) -> Optional[Dict]:
        """Thêm bình luận"""

        try:
            cid = self._next_id("BinhLuan")
            now = self._now_ms()

            query = """
            MATCH (u:User {username:$uid}), (p:BaiViet{id:$pid})

            CREATE (c:BinhLuan {
                id:$id,
                content:$content,
                created_at:$now
            })

            CREATE (u)-[:DA_DANG]->(c)
            CREATE (c)-[:BINH_LUAN]->(p)

            RETURN c,
                u.username AS username,
                u.full_name AS full_name,
                u.anh_dai_dien AS anh_dai_dien
            """

            rows = self.db.execute_query(query, {
                "uid": user_id,
                "pid": post_id,
                "id": cid,
                "content": content,
                "now": now
            })

            if not rows:
                return None

            row = rows[0]

            c = dict(row["c"])

            c["username"] = row["username"]
            c["full_name"] = row["full_name"]
            c["anh_dai_dien"] = row["anh_dai_dien"]

            return c

        except Exception as e:
            logger.error(f"add_comment error: {e}", exc_info=True)
            return None

    def delete_comment(self, comment_id: int, user_id: str, is_admin: bool = False) -> bool:
        try:
            # Lấy chủ comment
            check = self.db.execute_query(
                """
                MATCH (u:User)-[:DA_DANG]->(c:BinhLuan {id:$id})
                RETURN u.username AS username
                """,
                {"id": comment_id}
            )

            if not check:
                return False

            # Chỉ chủ comment hoặc admin được xóa
            if not is_admin and check[0]["username"] != user_id:
                return False

            # Xóa comment
            self.db.execute_query(
                """
                MATCH (c:BinhLuan {id:$id})
                DETACH DELETE c
                """,
                {"id": comment_id}
            )

            return True

        except Exception as e:
            logger.error(f"delete_comment error: {e}", exc_info=True)
            return False