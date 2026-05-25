Test 1: Câu hỏi rỗng
Input: [để trống]
Expected: ⚠️ Vui lòng nhập câu hỏi!
Test 2: Quá ngắn
Input: "ai?"
Expected: 📏 Câu hỏi quá ngắn! + Suggestions
Test 3: Spam
Input: "Click here casino"
Expected: 🚫 Câu hỏi chứa nội dung không phù hợp!
Test 4: Không liên quan
Input: "Cách nấu phở?"
Expected: 🤔 Không liên quan văn học + Suggestions
Test 5: Tiếng Anh
Input: "Who wrote Kieu?"
Expected: 🌐 Vui lòng đặt câu bằng tiếng Việt!
Test 6: Thiếu từ hỏi
Input: "Nguyễn Du sáng tác Truyện Kiều"
Expected: ❓ Thiếu từ hỏi + Suggestions
Test 7: Hợp lệ
Input: "Truyện Kiều do ai sáng tác?"
Expected: ✅ Hiển thị kết quả bình thường