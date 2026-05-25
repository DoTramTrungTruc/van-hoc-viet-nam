  // Load user info
  async function loadUserInfo() {
    try {
        const res = await fetch('/api/auth/me', {credentials: 'include'});
        if (!res.ok) { 
            window.location.href = '/login'; 
            return; 
        }
        
        const data = await res.json();
        if (data.success) {
            const user = data.user;
            document.getElementById('username').value = user.username;
            document.getElementById('email').value = user.email;
            document.getElementById('full_name').value = user.full_name || '';
            
            // Update hero display
            document.getElementById('displayName').textContent = user.full_name || user.username;
            document.getElementById('displayUsername').textContent = '@' + user.username;
            document.getElementById('displayEmail').textContent = user.email;
        }
    } catch (error) {
        console.error('Error loading user info:', error);
        showAlert('Lỗi khi tải thông tin người dùng', 'error');
    }
}

// Update user info
async function updateUserInfo(e) {
    e.preventDefault();
    
    const data = {
        email: e.target.email.value,
        full_name: e.target.full_name.value
    };
    
    try {
        const res = await fetch('/api/auth/update-profile', {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        const result = await res.json();
        
        if (result.success) {
            showAlert('✓ Cập nhật thông tin thành công!', 'success');
            // Reload to update hero display
            setTimeout(() => loadUserInfo(), 1000);
        } else {
            showAlert('✗ ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error updating info:', error);
        showAlert('✗ Lỗi kết nối', 'error');
    }
}

// Change password
async function changePassword(e) {
    e.preventDefault();
    
    const fd = new FormData(e.target);
    const newPassword = fd.get('new_password');
    const confirmPassword = fd.get('confirm_password');
    
    if (newPassword !== confirmPassword) {
        showAlert('✗ Mật khẩu xác nhận không khớp!', 'error');
        return;
    }
    
    try {
        const res = await fetch('/api/auth/change-password', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify({
                old_password: fd.get('old_password'),
                new_password: newPassword
            })
        });
        
        const result = await res.json();
        
        if (result.success) {
            showAlert('✓ Đổi mật khẩu thành công!', 'success');
            e.target.reset();
        } else {
            showAlert('✗ ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error changing password:', error);
        showAlert('✗ Lỗi kết nối', 'error');
    }
}

// Show alert
function showAlert(message, type = 'success') {
    const container = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `<strong>${message}</strong>`;
    
    container.innerHTML = '';
    container.appendChild(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
    
    // Scroll to alert
    alert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
async function loadFavorites() {
    try {
        const res = await fetch('/api/auth/favorites', {
            credentials: 'include'
        });
        const data = await res.json();
        if (!data.success) return;

        const container = document.getElementById('favoriteList');
        if (!container) return; // Phòng hờ nếu không tìm thấy element trên HTML

        if (data.favorites.length === 0) {
            container.innerHTML = '<p class="empty-favorite">Chưa có tác phẩm yêu thích</p>';
            return;
        }

        container.innerHTML = data.favorites.map(tp => {
            // Nếu tác phẩm không có ảnh_dai_dien, sử dụng một ảnh mặc định để giao diện không bị vỡ
            const imgUrl = tp.anh_dai_dien ? tp.anh_dai_dien : '/static/images/default-book.png';

            return `
                <div class="favorite-item">
                    <a href="/tac-pham/${encodeURIComponent(tp.ten)}" class="favorite-link">
                        <img src="${imgUrl}" alt="${esc(tp.ten)}" class="favorite-cover" 
                             onerror="this.src='/static/images/default-book.png'">
                        <p class="favorite-title">${esc(tp.ten)}</p>
                    </a>
                    <button class="remove-favorite-btn" onclick="removeFavorite('${esc(tp.ten)}')" title="Xóa khỏi yêu thích">❌</button>
                </div>
            `;
        }).join('');
    } catch (err) {
        console.error("Lỗi khi tải danh sách yêu thích:", err);
    }
}

// Hàm hỗ trợ escape HTML tránh lỗi bảo mật XSS (giống bên forum.js của bạn)
function esc(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
async function removeFavorite(ten) {

    try {

        await fetch('/api/auth/favorites/remove', {

            method: 'POST',

            headers: {
                'Content-Type': 'application/json'
            },

            credentials: 'include',

            body: JSON.stringify({
                ten_tac_pham: ten
            })
        });

        loadFavorites();

    } catch(err) {

        console.error(err);

    }
}
// Load on page load
document.addEventListener('DOMContentLoaded', () => {

    loadUserInfo();
    loadFavorites();

});
