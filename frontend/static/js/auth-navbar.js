<!-- Navigation Component với Authentication -->
<script>
// Global auth state
let currentUser = null;
let isAuthenticated = false;

// Check auth khi page load
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/check', {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.authenticated) {
            isAuthenticated = true;
            currentUser = data.user;
            updateNavbar();
        } else {
            isAuthenticated = false;
            currentUser = null;
            updateNavbar();
        }
    } catch (error) {
        console.error('Error checking auth:', error);
    }
}

// Update navbar based on auth status
function updateNavbar() {
    const authLinks = document.getElementById('authLinks');
    if (!authLinks) return;
    
    if (isAuthenticated && currentUser) {
        // Logged in - show user menu
        authLinks.innerHTML = `
            <li class="user-menu">
                <span class="user-greeting">👋 ${currentUser.username}</span>
                <div class="dropdown">
                    <button class="dropdown-btn">▼</button>
                    <div class="dropdown-content">
                        <a href="/profile">👤 Hồ sơ</a>
                        ${currentUser.is_admin ? '<a href="/admin">⚙️ Quản trị</a>' : ''}
                        <a href="#" onclick="logout(event)" style="color: #e74c3c;">🚪 Đăng xuất</a>
                    </div>
                </div>
            </li>
        `;
    } else {
        // Not logged in - show login/register
        authLinks.innerHTML = `
            <li><a href="/login">Đăng nhập</a></li>
            <li><a href="/register">Đăng ký</a></li>
        `;
    }
}

// Logout function
async function logout(event) {
    if (event) event.preventDefault();
    
    if (!confirm('Bạn có chắc muốn đăng xuất?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show success message
            showNotification('Đã đăng xuất thành công!', 'success');
            
            // Redirect after a short delay
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        }
    } catch (error) {
        console.error('Logout error:', error);
        showNotification('Lỗi khi đăng xuất', 'error');
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notif = document.createElement('div');
    notif.className = `notification notification-${type}`;
    notif.textContent = message;
    notif.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 1rem 2rem;
        background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notif);
    
    setTimeout(() => {
        notif.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notif.remove(), 300);
    }, 3000);
}

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
    
    .user-menu {
        position: relative;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .user-greeting {
        color: white;
        font-weight: 500;
    }
    
    .dropdown {
        position: relative;
    }
    
    .dropdown-btn {
        background: rgba(255,255,255,0.1);
        border: none;
        color: white;
        padding: 0.5rem 0.8rem;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.9rem;
    }
    
    .dropdown-btn:hover {
        background: rgba(255,255,255,0.2);
    }
    
    .dropdown-content {
        display: none;
        position: absolute;
        right: 0;
        top: 100%;
        margin-top: 0.5rem;
        background: white;
        min-width: 200px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-radius: 4px;
        overflow: hidden;
        z-index: 1000;
    }
    
    .dropdown:hover .dropdown-content {
        display: block;
    }
    
    .dropdown-content a {
        display: block;
        padding: 0.8rem 1.2rem;
        color: #333;
        text-decoration: none;
        transition: background 0.2s;
    }
    
    .dropdown-content a:hover {
        background: #f5f7fa;
    }
`;
document.head.appendChild(style);

// Check auth on page load
document.addEventListener('DOMContentLoaded', checkAuthStatus);
</script>
