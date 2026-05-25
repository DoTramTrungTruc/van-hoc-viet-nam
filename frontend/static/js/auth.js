/**
 * Authentication UI Handler
 * Xử lý hiển thị user info, avatar và logout trên navbar
 */

class AuthUI {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    async init() {
        await this.checkAuth();
        this.updateNavbar();
    }

    async checkAuth() {
        try {
            const response = await fetch('/api/auth/check', {
                credentials: 'include'
            });
            const data = await response.json();
            
            if (data.success && data.authenticated) {
                this.currentUser = data.user;
            } else {
                this.currentUser = null;
            }
        } catch (error) {
            console.error('Auth check error:', error);
            this.currentUser = null;
        }
    }

    updateNavbar() {
        const navbar = document.querySelector('.nav-menu');
        if (!navbar) return;

        // Xóa các items auth cũ (nếu có)
        const existingAuth = navbar.querySelector('.nav-auth-items');
        if (existingAuth) {
            existingAuth.remove();
        }

        // Tạo auth menu items
        const authItems = document.createElement('div');
        authItems.className = 'nav-auth-items';
        authItems.style.cssText = 'display: flex; align-items: center; gap: 1rem; margin-left: auto;';

        if (this.currentUser) {
            // User đã đăng nhập
            authItems.innerHTML = `
                ${this.currentUser.is_admin ? '<li><a href="/admin">⚙️ Quản trị</a></li>' : ''}
                <li class="user-menu">
                    <div class="user-avatar" onclick="window.authUI.toggleUserMenu()">
                        ${this.getAvatar()}
                    </div>
                    <div class="user-dropdown" id="userDropdown" style="display: none;">
                        <div class="dropdown-header">
                            <div class="dropdown-avatar">${this.getAvatar()}</div>
                            <div class="dropdown-info">
                                <div class="dropdown-name">${this.currentUser.full_name || this.currentUser.username}</div>
                                <div class="dropdown-email">${this.currentUser.email}</div>
                            </div>
                        </div>
                        <div class="dropdown-divider"></div>
                        <a href="/profile" class="dropdown-item" style="color:black;">
                            <span>👤</span> Hồ sơ cá nhân
                        </a>
                        ${this.currentUser.is_admin ? '<a href="/admin" class="dropdown-item" style="color:black;"><span>⚙️</span> Quản trị</a>' : ''}
                        <div class="dropdown-divider"></div>
                        <a href="#" onclick="window.authUI.logout(); return false;" class="dropdown-item logout">
                            <span>🚪</span> Đăng xuất
                        </a>
                    </div>
                </li>
            `;
        } else {
            // Chưa đăng nhập
            authItems.innerHTML = `
                <li><a href="/login" class="btn-login">Đăng nhập</a></li>
                <li><a href="/register" class="btn-register">Đăng ký</a></li>
            `;
        }

        navbar.appendChild(authItems);
        this.addStyles();
    }

    getAvatar() {
        if (!this.currentUser) return 'U';
        const name = this.currentUser.full_name || this.currentUser.username || 'User';
        return name.charAt(0).toUpperCase();
    }

    toggleUserMenu() {
        const dropdown = document.getElementById('userDropdown');
        if (dropdown) {
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        }
    }

    async logout() {
        if (!confirm('Bạn có chắc muốn đăng xuất?')) {
            return;
        }

        try {
            const response = await fetch('/api/auth/logout', {
                method: 'POST',
                credentials: 'include'
            });

            if (response.ok) {
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Logout error:', error);
            window.location.href = '/login';
        }
    }

    addStyles() {
        // Kiểm tra xem đã có styles chưa
        if (document.getElementById('auth-ui-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'auth-ui-styles';
        styles.textContent = `
            .nav-auth-items {
                display: flex;
                align-items: center;
                gap: 1rem;
                list-style: none;
            }

            .nav-auth-items li {
                list-style: none;
            }

            .btn-login, .btn-register {
                padding: 0.5rem 1.5rem;
                border-radius: 4px;
                font-weight: 500;
                transition: all 0.3s;
            }

            .btn-login {
                  color: var(--primary-color);
            }

            
            .btn-login {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }

            .btn-register {
                color: var(--primary-color);
            }

            .btn-register {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }

            .user-menu {
                position: relative;
            }

            .user-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: white;
                color: var(--secondary-color);
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 1.1rem;
                cursor: pointer;
                transition: all 0.3s;
                border: 2px solid rgba(255,255,255,0.3);
            }

            .user-avatar:hover {
                transform: scale(1.1);
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }

            .user-dropdown {
                position: absolute;
                top: calc(100% + 10px);
                right: 0;
                background: white;
                border-radius: 8px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.15);
                min-width: 280px;
                z-index: 1000;
                overflow: hidden;
            }

            .dropdown-header {
                padding: 1.5rem;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                display: flex;
                align-items: center;
                gap: 1rem;
            }

            .dropdown-avatar {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: white;
                color: var(--secondary-color);
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 1.5rem;
                border: 3px solid rgba(255,255,255,0.3);
            }

            .dropdown-info {
                flex: 1;
            }

            .dropdown-name {
                font-weight: 600;
                font-size: 1.1rem;
                margin-bottom: 0.3rem;
            }

            .dropdown-email {
                font-size: 0.85rem;
                opacity: 0.9;
            }

            .dropdown-divider {
                height: 1px;
                background: #e0e0e0;
                margin: 0.5rem 0;
            }

            .dropdown-item {
                display: flex;
                align-items: center;
                gap: 0.8rem;
                padding: 0.8rem 1.5rem;
                color: #333;
                text-decoration: none;
                transition: background 0.2s;
            }

            .dropdown-item:hover {
                background: #f5f5f5;
            }

            .dropdown-item.logout {
                color: #e74c3c;
            }

            .dropdown-item.logout:hover {
                background: #ffebee;
            }

            .dropdown-item span {
                font-size: 1.2rem;
            }

            /* Click outside to close */
            @media (max-width: 768px) {
                .user-dropdown {
                    right: -10px;
                    min-width: 260px;
                }
            }
        `;

        document.head.appendChild(styles);

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            const userMenu = document.querySelector('.user-menu');
            const dropdown = document.getElementById('userDropdown');
            
            if (dropdown && userMenu && !userMenu.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
    }

    // Utility: Check if user is logged in
    isAuthenticated() {
        return this.currentUser !== null;
    }

    // Utility: Check if user is admin
    isAdmin() {
        return this.currentUser && this.currentUser.is_admin;
    }

    // Utility: Get current user
    getCurrentUser() {
        return this.currentUser;
    }
}

// Initialize globally
window.authUI = new AuthUI();

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthUI;
}
