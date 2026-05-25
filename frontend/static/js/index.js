/**
 * INDEX.JS - JavaScript cho trang chủ
 * Load data và xử lý interactions
 */

// Load khi DOM ready
document.addEventListener('DOMContentLoaded', function() {
    loadStatistics();
    loadFeaturedTacPham();
    loadFeaturedAuthors(); // Thêm này
    loadTheLoai();
    
    // Search on Enter
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                search();
            }
        });
    }
});

/**
 * Load thống kê
 */
async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const data = await response.json();
        
        if (data.success) {
            const stats = data.data.tong_quan;
            
            // Animate numbers
            animateNumber('statTacGia', stats.tac_gia);
            animateNumber('statTacPham', stats.tac_pham);
            animateNumber('statNhanVat', stats.nhan_vat);
            animateNumber('statTheLoai', stats.the_loai);
        }
    } catch (error) {
        console.error('Lỗi khi load thống kê:', error);
        // Fallback values
        document.getElementById('statTacGia').textContent = '15';
        document.getElementById('statTacPham').textContent = '30';
        document.getElementById('statNhanVat').textContent = '19';
        document.getElementById('statTheLoai').textContent = '6';
    }
}

/**
 * Animate number counting
 */
function animateNumber(elementId, targetNumber) {
    const element = document.getElementById(elementId);
    const duration = 1500; // 1.5 seconds
    const steps = 60;
    const increment = targetNumber / steps;
    let current = 0;
    let step = 0;
    
    const timer = setInterval(() => {
        step++;
        current += increment;
        
        if (step >= steps) {
            element.textContent = targetNumber;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, duration / steps);
}

/**
 * Load tác giả nổi bật từ Neo4j
 */
async function loadFeaturedAuthors() {
    const carousel = document.querySelector('.authors-carousel');
    if (!carousel) return;
    
    try {
        const response = await fetch('/api/tac-gia');
        const data = await response.json();
        
        console.log('Tác giả data:', data); // Debug
        
        if (data.success && data.data && data.data.length > 0) {
            // Lấy 4 tác giả đầu tiên hoặc random
            const tacGias = data.data.slice(0, 4);
            
            carousel.innerHTML = tacGias.map(tg => {
                // Tạo initial từ tên
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
                
                return `
                    <div class="author-card">
                        <div class="author-initial">${initial}</div>
                        <h3>${tg.ten}</h3>
                        <p class="author-years">${years}</p>
                        <p class="author-style">${tg.truong_phai || 'Văn học Việt Nam'}</p>
                        <a href="/tac-gia" class="author-link">Xem chi tiết →</a>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Lỗi khi load tác giả:', error);
    }
}

/**
 * Load tác phẩm tiêu biểu từ Neo4j
 */
async function loadFeaturedTacPham() {
    const grid = document.getElementById('tacPhamGrid');
    
    try {
        // Gọi API lấy tác phẩm
        const response = await fetch('/api/tac-pham');
        const data = await response.json();
        
        console.log('Tác phẩm data:', data); // Debug
        
        if (data.success && data.data && data.data.length > 0) {
            // Lấy 6 tác phẩm đầu tiên
            const tacPhams = data.data.slice(0, 6);
            
            grid.innerHTML = tacPhams.map(tp => {
                // Lấy tác giả - có thể là string hoặc array
                let tacGia = 'Chưa rõ';
                if (tp.tac_gia) {
                    if (Array.isArray(tp.tac_gia)) {
                        tacGia = tp.tac_gia.join(', ');
                    } else {
                        tacGia = tp.tac_gia;
                    }
                }
                
                // Lấy thể loại
                let theLoai = 'Chưa phân loại';
                if (tp.the_loai) {
                    if (Array.isArray(tp.the_loai)) {
                        theLoai = tp.the_loai.join(', ');
                    } else {
                        theLoai = tp.the_loai;
                    }
                }
                return `
                    <div class="work-card">

                        <div class="work-cover">
                            <img src="${tp.anh_dai_dien || '/static/images/default_cover.jpg'}">
                        </div>

                        <div class="work-content">

                            <h3>
                                <a href="/tac-pham/${encodeURIComponent(tp.ten)}">
                                    ${tp.ten}
                                </a>
                            </h3>

                            <p class="meta">
                                ✍️ ${tacGia}
                            </p>

                            <p class="meta">
                                📚 ${theLoai}
                            </p>

                            ${tp.noi_dung_tom_tat ? `
                            <p class="summary">
                                ${tp.noi_dung_tom_tat.substring(0,100)}...
                            </p>
                            ` : ''}

                            <a href="/tac-pham/${encodeURIComponent(tp.ten)}"
                            class="work-read-btn">
                            Xem chi tiết →
                            </a>

                        </div>

                    </div>
                    `;
                
            }).join('');
        } else {
            grid.innerHTML = `
                <div class="work-card">
                    <p>Chưa có tác phẩm nào trong hệ thống</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Lỗi khi load tác phẩm:', error);
        grid.innerHTML = `
            <div class="work-card">
                <p style="color: #d9534f;">❌ Không thể tải tác phẩm. Vui lòng kiểm tra kết nối Neo4j.</p>
            </div>
        `;
    }
}

/**
 * Load thể loại từ Neo4j
 */
async function loadTheLoai() {
    const grid = document.getElementById('theLoaiGrid');
    
    try {
        const response = await fetch('/api/the-loai/');
        const data = await response.json();
        
        console.log('Thể loại data:', data); // Debug
        
        if (data.success && data.data && data.data.length > 0) {
            grid.innerHTML = data.data.map(tl => {
                // Icon theo thể loại
                const icons = {
                    'Trường ca': '📜',
                    'Truyện ngắn': '📖',
                    'Tiểu thuyết': '📚',
                    'Thơ': '🎭',
                    'Thơ ca': '🎭',
                    'Tản văn': '✍️',
                    'Truyện dài': '📕'
                };
                
                const icon = icons[tl.ten] || '📄';
                
                // Lấy số lượng tác phẩm
                let soLuong = 0;
                if (tl.so_luong_tac_pham !== undefined && tl.so_luong_tac_pham !== null) {
                    soLuong = tl.so_luong_tac_pham;
                } else if (tl.so_luong !== undefined && tl.so_luong !== null) {
                    soLuong = tl.so_luong;
                }
                
                return `
                    <div class="genre-card">
                        <div style="font-size: 2.5rem; margin-bottom: 10px;">${icon}</div>
                        <h4>${tl.ten}</h4>
                        <p class="count">${soLuong} tác phẩm</p>
                        ${tl.mo_ta ? `<p style="font-size: 0.85rem; color: #666; margin-top: 8px;">${tl.mo_ta}</p>` : ''}
                    </div>
                `;
            }).join('');
        } else {
            grid.innerHTML = `
                <div class="genre-card">
                    <p>Chưa có thể loại nào trong hệ thống</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Lỗi khi load thể loại:', error);
        grid.innerHTML = `
            <div class="genre-card">
                <p style="color: #d9534f;">❌ Không thể tải thể loại. Vui lòng kiểm tra kết nối.</p>
            </div>
        `;
    }
}

/**
 * Search function
 */
function search() {
    const keyword = document.getElementById('searchInput').value.trim();
    
    if (keyword) {
        // Redirect to search page
        window.location.href = `/tac-pham?search=${encodeURIComponent(keyword)}`;
    } else {
        // Shake animation if empty
        const input = document.getElementById('searchInput');
        input.classList.add('shake');
        setTimeout(() => input.classList.remove('shake'), 500);
    }
}

// Add shake animation to CSS dynamically if not exists
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    
    .shake {
        animation: shake 0.5s;
    }
`;
document.head.appendChild(style);
const observer = new IntersectionObserver(entries => {

    entries.forEach(entry => {

        if(entry.isIntersecting){
            entry.target.classList.add('show');
        }

    });

});

document.querySelectorAll(
    '.work-card, .stat-card, .genre-card, .author-card'
).forEach(el => {

    el.classList.add('hidden-scroll');
    observer.observe(el);

});