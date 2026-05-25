/**
 * TAC-GIA.JS - JavaScript cho trang Tác Giả với phân trang
 */

let allTacGia = [];
let currentPage = 1;
const itemsPerPage = 6;

// Load khi DOM ready
document.addEventListener('DOMContentLoaded', function() {
    loadAllTacGia();
    
    // Search on Enter
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchTacGia();
            }
        });
    }
});

/**
 * Load tất cả tác giả từ API
 */
async function loadAllTacGia() {
    const loading = document.getElementById('loading');
    const authorsGrid = document.getElementById('authorsGrid');
    
    try {
        const response = await fetch('/api/tac-gia');
        const data = await response.json();
        
        console.log('Tác giả data:', data);
        
        if (data.success && data.data && data.data.length > 0) {
            allTacGia = data.data;
            
            // Update count
            document.getElementById('totalCount').textContent = allTacGia.length;
            
            // Display first page
            displayPage(1);
            
            // Show grid, hide loading
            loading.style.display = 'none';
            authorsGrid.style.display = 'block';
        } else {
            loading.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📚</div>
                    <div class="empty-state-text">Chưa có tác giả nào</div>
                    <div class="empty-state-hint">Hệ thống chưa có dữ liệu tác giả</div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Lỗi khi load tác giả:', error);
        loading.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">❌</div>
                <div class="empty-state-text">Không thể tải dữ liệu</div>
                <div class="empty-state-hint">Lỗi: ${error.message}</div>
            </div>
        `;
    }
}

/**
 * Hiển thị trang cụ thể
 */
function displayPage(pageNumber) {
    currentPage = pageNumber;
    const start = (pageNumber - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageData = allTacGia.slice(start, end);
    
    const authorsGrid = document.getElementById('authorsGrid');
    const container = document.createElement('div');
    
    // Display authors
    displayAuthors(pageData, container);
    
    // Create pagination
    const totalPages = Math.ceil(allTacGia.length / itemsPerPage);
    const pagination = createPagination(pageNumber, totalPages);
    
    // Update authorsGrid
    authorsGrid.innerHTML = '';
    authorsGrid.appendChild(container);
    authorsGrid.appendChild(pagination);
}

/**
 * Tạo pagination controls
 */
function createPagination(currentPage, totalPages) {
    const paginationDiv = document.createElement('div');
    paginationDiv.className = 'pagination';
    
    if (totalPages <= 1) {
        return paginationDiv;
    }
    
    let html = '';
    
    // Previous button
    if (currentPage > 1) {
        html += `<button class="page-btn" onclick="displayPage(${currentPage - 1})">‹ Trước</button>`;
    }
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        // Show first page, last page, current page, and pages around current
        if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
            html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="displayPage(${i})">${i}</button>`;
        } else if (i === currentPage - 2 || i === currentPage + 2) {
            html += `<span class="page-dots">...</span>`;
        }
    }
    
    // Next button
    if (currentPage < totalPages) {
        html += `<button class="page-btn" onclick="displayPage(${currentPage + 1})">Tiếp ›</button>`;
    }
    
    paginationDiv.innerHTML = html;
    return paginationDiv;
}

/**
 * Hiển thị danh sách tác giả
 */
function displayAuthors(authors, container) {
    const gridDiv = document.createElement('div');
    gridDiv.className = 'authors-grid-content';
    
    gridDiv.innerHTML = authors.map(tg => {
        // Tạo avatar initial
        const initial = tg.ten
            .split(' ')
            .map(word => word[0])
            .join('')
            .toUpperCase()
            .substring(0, 3);
        
        // Format năm
        const years = tg.nam_mat 
            ? `${tg.nam_sinh} - ${tg.nam_mat}`
            : `${tg.nam_sinh} - `;
        
        // Count tác phẩm
        const worksCount = tg.tac_pham ? 
            (Array.isArray(tg.tac_pham) ? tg.tac_pham.filter(tp => tp).length : 0) : 0;
        
        return `
            <div class="author-card" onclick="goToAuthorDetail('${escapeHtml(tg.ten)}')">
                <div class="author-avatar">${initial}</div>
                <div class="author-name">${escapeHtml(tg.ten)}</div>
                <div class="author-years">${years}</div>
                ${tg.que_quan ? `<div class="author-location">📍 ${escapeHtml(tg.que_quan)}</div>` : ''}
                ${tg.truong_phai ? `<div class="author-style">${escapeHtml(tg.truong_phai)}</div>` : ''}
                ${tg.tieu_su ? `<div class="author-bio">${escapeHtml(tg.tieu_su.substring(0, 100))}${tg.tieu_su.length > 100 ? '...' : ''}</div>` : ''}
                ${worksCount > 0 ? `<div class="author-works-count">📚 ${worksCount} tác phẩm</div>` : ''}
            </div>
        `;
    }).join('');
    
    container.appendChild(gridDiv);
}
function goToAuthorDetail(tenTacGia) {
    window.location.href = `/tac-gia/${encodeURIComponent(tenTacGia)}`;
}
/**
 * Tìm kiếm tác giả
 */
async function searchTacGia() {
    const keyword = document.getElementById('searchInput').value.trim();
    const authorsGrid = document.getElementById('authorsGrid');
    const searchResults = document.getElementById('searchResults');
    const searchResultsGrid = document.getElementById('searchResultsGrid');
    
    if (!keyword) {
        showAllTacGia();
        return;
    }
    
    try {
        const response = await fetch(`/api/tac-gia/search?q=${encodeURIComponent(keyword)}`);
        const data = await response.json();
        
        console.log('Search results:', data);
        
        if (data.success) {
            if (data.data && data.data.length > 0) {
                // Hide main grid, show search results
                authorsGrid.style.display = 'none';
                searchResults.style.display = 'block';
                
                // Display search results (no pagination for search)
                searchResultsGrid.innerHTML = '';
                const container = document.createElement('div');
                container.className = 'authors-grid-content';
                displayAuthors(data.data, searchResultsGrid);
            } else {
                // No results
                authorsGrid.style.display = 'none';
                searchResults.style.display = 'block';
                searchResultsGrid.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">🔍</div>
                        <div class="empty-state-text">Không tìm thấy tác giả</div>
                        <div class="empty-state-hint">Thử từ khóa khác: "${keyword}"</div>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Lỗi khi tìm kiếm:', error);
        alert('Có lỗi khi tìm kiếm: ' + error.message);
    }
}

/**
 * Hiển thị tất cả tác giả (clear search)
 */
function showAllTacGia() {
    document.getElementById('searchInput').value = '';
    document.getElementById('searchResults').style.display = 'none';
    document.getElementById('authorsGrid').style.display = 'block';
    displayPage(currentPage);
}

/**
 * Xem chi tiết tác giả
 */
async function viewAuthorDetail(tenTacGia) {
    const modal = document.getElementById('detailModal');
    const modalBody = document.getElementById('modalBody');
    
    // Show modal with loading
    modal.style.display = 'flex';
    modalBody.innerHTML = `
        <div class="loading-state">
            <div class="loading-spinner"></div>
            <p>Đang tải thông tin...</p>
        </div>
    `;
    
    try {
        const response = await fetch(`/api/tac-gia/${encodeURIComponent(tenTacGia)}`);
        const data = await response.json();
        
        console.log('Author detail:', data);
        
        if (data.success && data.data) {
            const tg = data.data;
            
            // Format years
            const years = tg.nam_mat 
                ? `${tg.nam_sinh} - ${tg.nam_mat}`
                : `${tg.nam_sinh} - `;
            
            // Build modal content
            let html = `
                <div class="modal-header">
                    <h2 class="modal-title">${escapeHtml(tg.ten)}</h2>
                </div>
                
                <div class="modal-meta">
                    <div class="meta-item">
                        <div class="meta-label">Năm sinh - mất</div>
                        <div class="meta-value">${years}</div>
                    </div>
                    ${tg.que_quan ? `
                    <div class="meta-item">
                        <div class="meta-label">Quê quán</div>
                        <div class="meta-value">${escapeHtml(tg.que_quan)}</div>
                    </div>
                    ` : ''}
                    ${tg.truong_phai ? `
                    <div class="meta-item">
                        <div class="meta-label">Trường phái</div>
                        <div class="meta-value">${escapeHtml(tg.truong_phai)}</div>
                    </div>
                    ` : ''}
                </div>
            `;
            
            // Tiểu sử
            if (tg.tieu_su) {
                html += `
                    <div class="modal-section">
                        <h3 class="section-title">📖 Tiểu sử</h3>
                        <div class="modal-bio">${escapeHtml(tg.tieu_su)}</div>
                    </div>
                `;
            }
            
            // Tác phẩm
            if (tg.tac_pham && tg.tac_pham.length > 0) {
                const works = tg.tac_pham.filter(tp => tp);
                if (works.length > 0) {
                    html += `
                        <div class="modal-section">
                            <h3 class="section-title">📚 Tác phẩm (${works.length})</h3>
                            <ul class="works-list">
                                ${works.map(tp => `
                                    <li>
                                        <a href="/tac-pham/${encodeURIComponent(tp)}">
                                            ${escapeHtml(tp)}
                                        </a>
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    `;
                }
            }
            
            modalBody.innerHTML = html;
        } else {
            modalBody.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">❌</div>
                    <div class="empty-state-text">Không tìm thấy thông tin</div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Lỗi khi load chi tiết:', error);
        modalBody.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">❌</div>
                <div class="empty-state-text">Lỗi khi tải dữ liệu</div>
                <div class="empty-state-hint">${error.message}</div>
            </div>
        `;
    }
}

/**
 * Đóng modal
 */
function closeModal() {
    document.getElementById('detailModal').style.display = 'none';
}

/**
 * Escape HTML để tránh XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal khi click overlay
document.addEventListener('click', function(e) {
    const modal = document.getElementById('detailModal');
    if (e.target.classList.contains('modal-overlay')) {
        closeModal();
    }
});

// Close modal khi nhấn ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});