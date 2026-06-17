/**
 * AUTH-FORM.JS - Login & Register Form Handler
 */

/**
 * Show alert message
 */
function showAlert(message, type = 'success') {
    const container = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `<strong>${message}</strong>`;
    
    container.innerHTML = '';
    container.appendChild(alert);
    
    // Auto remove success alerts
    if (type === 'success') {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 3000);
    }
    
    // Scroll to alert
    alert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Handle login form submission
 */
async function handleLogin(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = {
        username: formData.get('username'),
        password: formData.get('password')
    };
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const originalText = btnText.textContent;
    
    // Disable button
    submitBtn.disabled = true;
    btnText.textContent = 'Đang xử lý...';
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
     if (result.success) {

            showAlert(
                '✓ Đăng nhập thành công! Đang chuyển hướng...',
                'success'
            );
        
            setTimeout(() => {
        
                const redirectUrl =
                    localStorage.getItem(
                        'redirect_after_login'
                    );
        
                const favoriteAfterLogin =
                    localStorage.getItem(
                        'favorite_after_login'
                    );
        
                if (redirectUrl) {
        
                    localStorage.removeItem(
                        'redirect_after_login'
                    );
        
                    localStorage.removeItem(
                        'favorite_after_login'
                    );
        
                    window.location.href =
                        redirectUrl;
        
                } else {
        
                    if (result.user &&
                        result.user.is_admin) {
        
                        window.location.href =
                            '/admin';
        
                    } else {
        
                        window.location.href =
                            '/';
                    }
                }
        
            }, 1000);
        
        } else {
            showAlert('✗ ' + (result.error || 'Đăng nhập thất bại'), 'error');
            submitBtn.disabled = false;
            btnText.textContent = originalText;
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('✗ Lỗi kết nối: ' + error.message, 'error');
        submitBtn.disabled = false;
        btnText.textContent = originalText;
    }
}

/**
 * Handle register form submission
 */
async function handleRegister(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    
    // Validate password match
    const password = formData.get('password');
    const confirmPassword = formData.get('confirm_password');
    
    if (password !== confirmPassword) {
        showAlert('✗ Mật khẩu xác nhận không khớp!', 'error');
        return;
    }
    
    const data = {
        username: formData.get('username'),
        email: formData.get('email'),
        full_name: formData.get('full_name'),
        password: password
    };
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const originalText = btnText.textContent;
    
    // Disable button
    submitBtn.disabled = true;
    btnText.textContent = 'Đang xử lý...';
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('✓ Đăng ký thành công! Đang chuyển hướng...', 'success');
            
            // Redirect to login after 1.5 seconds
            setTimeout(() => {
                window.location.href = '/login';
            }, 1500);
        } else {
            showAlert('✗ ' + (result.error || 'Đăng ký thất bại'), 'error');
            submitBtn.disabled = false;
            btnText.textContent = originalText;
        }
    } catch (error) {
        console.error('Register error:', error);
        showAlert('✗ Lỗi kết nối: ' + error.message, 'error');
        submitBtn.disabled = false;
        btnText.textContent = originalText;
    }
}

/**
 * Password strength indicator (for register page)
 */
function checkPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]/)) strength++;
    if (password.match(/[A-Z]/)) strength++;
    if (password.match(/[0-9]/)) strength++;
    if (password.match(/[^a-zA-Z0-9]/)) strength++;
    
    const labels = ['Rất yếu', 'Yếu', 'Trung bình', 'Mạnh', 'Rất mạnh'];
    const colors = ['#d32f2f', '#f57c00', '#fbc02d', '#689f38', '#388e3c'];
    
    return {
        score: strength,
        label: labels[strength - 1] || 'Rất yếu',
        color: colors[strength - 1] || '#d32f2f'
    };
}

/**
 * Update password strength indicator
 */
function updatePasswordStrength(inputElement, indicatorElement) {
    const password = inputElement.value;
    
    if (!password) {
        indicatorElement.style.display = 'none';
        return;
    }
    
    const strength = checkPasswordStrength(password);
    indicatorElement.style.display = 'block';
    indicatorElement.textContent = `Độ mạnh: ${strength.label}`;
    indicatorElement.style.color = strength.color;
}
