/**
 * HOI-DAP.JS - Hỏi đáp tự nhiên
 * Giữ nguyên toàn bộ logic, chỉ cập nhật DOM
 */

let currentNetwork = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSuggestions();
});

/**
 * Load gợi ý câu hỏi
 */
async function loadSuggestions() {
    try {
        const res = await fetch('/api/qa/suggestions');
        const data = await res.json();
        
        if (data.success && data.data) {
            const container = document.getElementById('suggestionsList');
            container.innerHTML = data.data.map(q => 
                `<button class="suggestion-btn" onclick="fillQuestion(\`${escapeJs(q)}\`)">${escapeHtml(q)}</button>`
            ).join('');
        }
    } catch (error) {
        console.error('Error loading suggestions:', error);
    }
}

/**
 * Fill câu hỏi vào input
 */
function fillQuestion(question) {
    document.getElementById('questionInput').value = question;
    document.getElementById('questionInput').focus();
}

/**
 * Handle Enter key
 */
function handleEnter(event) {
    if (event.key === 'Enter') {
        askQuestion();
    }
}

/**
 * Hỏi câu hỏi
 */
async function askQuestion() {
    const question = document.getElementById('questionInput').value.trim();
    
    if (!question) {
        showError('Vui lòng nhập câu hỏi!', 'empty');
        return;
    }

    // Show loading
    document.getElementById('loadingBox').style.display = 'block';
    document.getElementById('resultsContainer').style.display = 'none';
    hideError();

    try {
        const res = await fetch('/api/qa/ask', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question})
        });

        const data = await res.json();

        if (data.success) {
            displayResults(data.data);
        } else {
            // Xử lý lỗi validation
            handleValidationError(data);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Lỗi kết nối! Vui lòng thử lại.', 'error');
    } finally {
        document.getElementById('loadingBox').style.display = 'none';
    }
}

/**
 * Xử lý validation error
 */
function handleValidationError(data) {
    const errorType = data.error_type || 'unknown';
    const errorMessage = data.error || 'Câu hỏi không hợp lệ';
    const suggestions = data.suggestions || [];

    // Hiển thị error message
    showError(errorMessage, errorType);

    // Nếu có suggestions, hiển thị
    if (suggestions.length > 0) {
        showSuggestions(suggestions, 'Thử các câu hỏi này:');
    }

    // Tự động clear error sau 5 giây
    setTimeout(hideError, 5000);
}

/**
 * Hiển thị error
 */
function showError(message, type = 'error') {
    let errorBox = document.getElementById('errorBox');
    
    if (!errorBox) {
        errorBox = document.createElement('div');
        errorBox.id = 'errorBox';
        errorBox.className = 'error-message';
        const searchBox = document.querySelector('.qa-search-box');
        searchBox.parentElement.insertBefore(errorBox, searchBox.nextSibling);
    }
    
    const icons = {
        'empty': '⚠️',
        'too_short': '📏',
        'too_long': '📏',
        'spam': '🚫',
        'invalid_chars': '❌',
        'irrelevant': '🤔',
        'wrong_language': '🌐',
        'no_question_word': '❓',
        'error': '⚠️'
    };

    errorBox.innerHTML = `<strong>${icons[type] || '⚠️'} ${message}</strong>`;
    errorBox.style.display = 'block';
    
    // Scroll to error
    errorBox.scrollIntoView({behavior: 'smooth', block: 'nearest'});
}

/**
 * Hide error
 */
function hideError() {
    const errorBox = document.getElementById('errorBox');
    if (errorBox) {
        errorBox.style.display = 'none';
    }
}

/**
 * Hiển thị gợi ý mới
 */
function showSuggestions(suggestions, title = '💡 Gợi ý:') {
    const container = document.getElementById('suggestionsList');
    container.innerHTML = suggestions.map(q => 
        `<button class="suggestion-btn" onclick="fillQuestion(\`${escapeJs(q)}\`)">${escapeHtml(q)}</button>`
    ).join('');
    
    // Update title
    const titleEl = document.querySelector('.suggestions-title');
    if (titleEl) {
        titleEl.textContent = title;
    }
}

/**
 * Hiển thị kết quả
 */
function displayResults(data) {
    // Show results container
    document.getElementById('resultsContainer').style.display = 'block';

    // Display answer text
    document.getElementById('answerText').innerHTML = `
        <p><strong>Câu hỏi:</strong> ${escapeHtml(data.question)}</p>
        <p><strong>Trả lời:</strong> ${escapeHtml(data.answer)}</p>
    `;

    // Display details if available
    if (data.results && data.results.length > 0) {
        const details = formatDetails(data.results[0], data.intent);
        document.getElementById('detailsBox').innerHTML = details;
    } else {
        document.getElementById('detailsBox').innerHTML = '';
    }

    // Display graph
    if (data.graph_data && data.graph_data.nodes && data.graph_data.nodes.length > 0) {
        drawGraph(data.graph_data);
    } else {
        document.getElementById('graphContainer').innerHTML = 
            '<p style="text-align:center;color:#999;padding:4rem">Không có dữ liệu đồ thị</p>';
    }

    // Scroll to results
    document.getElementById('resultsContainer').scrollIntoView({behavior: 'smooth'});
}

/**
 * Format chi tiết
 */
function formatDetails(result, intent) {
    let html = '<div class="detail-card">';
    html += '<h4>📊 Thông tin chi tiết</h4>';
    html += '<table class="detail-table">';

    for (let [key, value] of Object.entries(result)) {
        if (value && !['nhan_vat', 'tac_pham'].includes(key)) {
            const label = formatLabel(key);
            const displayValue = Array.isArray(value) ? value.join(', ') : value;
            html += `<tr><td><strong>${label}:</strong></td><td>${escapeHtml(String(displayValue))}</td></tr>`;
        }
    }

    // Special handling for arrays
    if (result.nhan_vat && Array.isArray(result.nhan_vat) && result.nhan_vat.length > 0) {
        const nvText = result.nhan_vat.map(nv => 
            typeof nv === 'string' ? nv : `${nv.ten} (${nv.vai_tro || 'nhân vật'})`
        ).join(', ');
        html += `<tr><td><strong>Nhân vật:</strong></td><td>${escapeHtml(nvText)}</td></tr>`;
    }

    if (result.tac_pham && Array.isArray(result.tac_pham) && result.tac_pham.length > 0) {
        const tpText = result.tac_pham.map(tp => 
            typeof tp === 'string' ? tp : tp.ten
        ).join(', ');
        html += `<tr><td><strong>Tác phẩm:</strong></td><td>${escapeHtml(tpText)}</td></tr>`;
    }

    html += '</table></div>';
    return html;
}

/**
 * Format label
 */
function formatLabel(key) {
    const labels = {
        'tac_gia': 'Tác giả',
        'tac_pham': 'Tác phẩm',
        'nam_sang_tac': 'Năm sáng tác',
        'nam_sinh': 'Năm sinh',
        'nam_mat': 'Năm mất',
        'que_quan': 'Quê quán',
        'the_loai': 'Thể loại',
        'noi_dung': 'Nội dung',
        'noi_dung_tom_tat': 'Nội dung',
        'y_nghia': 'Ý nghĩa',
        'vai_tro': 'Vai trò',
        'loai_quan_he': 'Loại quan hệ',
        'mo_ta': 'Mô tả',
        'ten': 'Tên'
    };
    return labels[key] || key;
}

/**
 * Vẽ đồ thị
 */
function drawGraph(graphData) {
    const container = document.getElementById('graphContainer');
    container.innerHTML = ''; // Clear

    if (!graphData.nodes || graphData.nodes.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:#999;padding:4rem">Không có dữ liệu đồ thị</p>';
        return;
    }

    // Create graph using graph-viz.js
    try {
        currentNetwork = createGraph(container, graphData);
    } catch (error) {
        console.error('Error drawing graph:', error);
        container.innerHTML = '<p style="text-align:center;color:#d32f2f;padding:4rem">Lỗi khi vẽ đồ thị</p>';
    }
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Escape JavaScript string
 */
function escapeJs(text) {
    if (!text) return '';
    return text.replace(/`/g, '\\`').replace(/\$/g, '\\$');
}