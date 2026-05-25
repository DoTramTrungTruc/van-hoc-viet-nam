import requests
from config import Config


class AICompareService:

    @staticmethod
    def compare_tac_pham(tp1, tp2):

        prompt = f"""
Bạn là chuyên gia nghiên cứu văn học Việt Nam.

Hãy phân tích chuyên sâu và so sánh 2 tác phẩm văn học sau.

=====================
TÁC PHẨM 1
=====================

Tên:
{tp1.get('ten')}

Tác giả:
{tp1.get('tac_gia')}

Nội dung:
{tp1.get('noi_dung')}

Chủ đề:
{tp1.get('chu_de')}

Giá trị nghệ thuật:
{tp1.get('gia_tri_nghe_thuat')}

Nhân vật:
{tp1.get('nhan_vat')}

=====================
TÁC PHẨM 2
=====================

Tên:
{tp2.get('ten')}

Tác giả:
{tp2.get('tac_gia')}

Nội dung:
{tp2.get('noi_dung')}

Chủ đề:
{tp2.get('chu_de')}

Giá trị nghệ thuật:
{tp2.get('gia_tri_nghe_thuat')}

Nhân vật:
{tp2.get('nhan_vat')}

=====================
YÊU CẦU
=====================

1. Điểm giống nhau
2. Điểm khác nhau
3. So sánh phong cách nghệ thuật
4. So sánh nhân vật
5. So sánh giá trị hiện thực
6. So sánh giá trị nhân đạo
7. Timeline văn học
8. Nhận xét chuyên sâu
9. Kết luận

Viết:
- đẹp
- có emoji nhẹ
- markdown rõ ràng
- chuyên sâu như bài phân tích văn học
"""

        headers = {
            "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "Bạn là chuyên gia phân tích văn học Việt Nam."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2500
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )

        result = response.json()

        print("OPENROUTER RESULT:", result)

        if "error" in result:
            raise Exception(result["error"]["message"])

        return result["choices"][0]["message"]["content"]