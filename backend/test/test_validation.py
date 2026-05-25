"""
Test cases cho validation câu hỏi
Chạy: python -m pytest tests/test_validation.py
"""

from services.nlp_service import nlp_service


def test_valid_questions():
    """Test các câu hỏi hợp lệ"""
    
    valid_questions = [
        "Truyện Kiều do ai sáng tác?",
        "Các nhân vật trong Chí Phèo?",
        "Nam Cao viết tác phẩm nào?",
        "Mối quan hệ giữa Thúy Kiều và Kim Trọng?",
        "Tác phẩm nào thuộc thể loại truyện ngắn?"
    ]
    
    for question in valid_questions:
        result = nlp_service.validate_question(question)
        assert result['is_valid'] == True, f"Failed: {question}"
        print(f"✓ PASS: {question}")


def test_empty_question():
    """Test câu hỏi rỗng"""
    
    result = nlp_service.validate_question("")
    assert result['is_valid'] == False
    assert result['error_type'] == 'empty'
    print(f"✓ PASS: Empty question detected")


def test_too_short():
    """Test câu hỏi quá ngắn"""
    
    short_questions = ["ai?", "gì", "ok"]
    
    for question in short_questions:
        result = nlp_service.validate_question(question)
        assert result['is_valid'] == False
        assert result['error_type'] == 'too_short'
        print(f"✓ PASS: Too short - '{question}'")


def test_spam_detection():
    """Test phát hiện spam"""
    
    spam_questions = [
        "Click here to buy viagra",
        "Casino online http://spam.com",
        "Free loan www.scam.net"
    ]
    
    for question in spam_questions:
        result = nlp_service.validate_question(question)
        assert result['is_valid'] == False
        assert result['error_type'] == 'spam'
        print(f"✓ PASS: Spam detected - '{question}'")


def test_irrelevant_questions():
    """Test câu hỏi không liên quan văn học"""
    
    irrelevant = [
        "Cách nấu phở ngon?",
        "Thời tiết hôm nay thế nào?",
        "Giá vàng bao nhiêu?",
        "Tôi muốn mua nhà"
    ]
    
    for question in irrelevant:
        result = nlp_service.validate_question(question)
        assert result['is_valid'] == False
        assert result['error_type'] == 'irrelevant'
        print(f"✓ PASS: Irrelevant - '{question}'")


def test_no_question_word():
    """Test câu không có từ hỏi"""
    
    result = nlp_service.validate_question("Nguyễn Du sáng tác Truyện Kiều")
    assert result['is_valid'] == False
    assert result['error_type'] == 'no_question_word'
    print(f"✓ PASS: No question word detected")


def test_wrong_language():
    """Test câu hỏi bằng tiếng Anh"""
    
    english_questions = [
        "Who wrote Truyen Kieu?",
        "What is the story about?",
        "Who is the author?"
    ]
    
    for question in english_questions:
        result = nlp_service.validate_question(question)
        assert result['is_valid'] == False
        assert result['error_type'] == 'wrong_language'
        print(f"✓ PASS: Wrong language - '{question}'")


def test_special_characters():
    """Test quá nhiều ký tự đặc biệt"""
    
    result = nlp_service.validate_question("@#$%^&*()!!!!????")
    assert result['is_valid'] == False
    assert result['error_type'] == 'invalid_chars'
    print(f"✓ PASS: Invalid chars detected")


def test_edge_cases():
    """Test các trường hợp biên"""
    
    # Câu hỏi dài nhưng hợp lệ
    long_valid = "Bạn có thể cho tôi biết thông tin chi tiết về tác phẩm Truyện Kiều của Nguyễn Du không?"
    result = nlp_service.validate_question(long_valid)
    assert result['is_valid'] == True
    print(f"✓ PASS: Long valid question")
    
    # Câu hỏi với dấu hỏi nhưng không có từ hỏi
    result = nlp_service.validate_question("Nguyễn Du?")
    assert result['is_valid'] == False
    print(f"✓ PASS: Question mark without question word")
    
    # Câu hỏi với entity nhưng không liên quan
    result = nlp_service.validate_question("Kiều ăn gì?")
    # Vẫn hợp lệ vì có "Kiều" (entity văn học)
    assert result['is_valid'] == True
    print(f"✓ PASS: Edge case with entity")


if __name__ == '__main__':
    print("🧪 RUNNING VALIDATION TESTS...\n")
    
    print("=" * 50)
    print("TEST 1: Valid Questions")
    print("=" * 50)
    test_valid_questions()
    
    print("\n" + "=" * 50)
    print("TEST 2: Empty Question")
    print("=" * 50)
    test_empty_question()
    
    print("\n" + "=" * 50)
    print("TEST 3: Too Short")
    print("=" * 50)
    test_too_short()
    
    print("\n" + "=" * 50)
    print("TEST 4: Spam Detection")
    print("=" * 50)
    test_spam_detection()
    
    print("\n" + "=" * 50)
    print("TEST 5: Irrelevant Questions")
    print("=" * 50)
    test_irrelevant_questions()
    
    print("\n" + "=" * 50)
    print("TEST 6: No Question Word")
    print("=" * 50)
    test_no_question_word()
    
    print("\n" + "=" * 50)
    print("TEST 7: Wrong Language")
    print("=" * 50)
    test_wrong_language()
    
    print("\n" + "=" * 50)
    print("TEST 8: Special Characters")
    print("=" * 50)
    test_special_characters()
    
    print("\n" + "=" * 50)
    print("TEST 9: Edge Cases")
    print("=" * 50)
    test_edge_cases()
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("=" * 50)