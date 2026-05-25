let lastEmail = '';

async function sendReset() {
    const email   = document.getElementById('emailInput').value.trim();
    const errEl   = document.getElementById('alertError');
    const btn     = document.getElementById('submitBtn');

    // Validate
    errEl.className = 'alert alert-error';
    if (!email) {
        errEl.textContent = '⚠️ Vui lòng nhập địa chỉ email';
        errEl.classList.add('show');
        return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        errEl.textContent = '⚠️ Email không đúng định dạng';
        errEl.classList.add('show');
        return;
    }

    errEl.classList.remove('show');
    btn.disabled    = true;
    btn.innerHTML   = '<span class="spinner-inline"></span> Đang gửi...';

    try {
        const res  = await fetch('/api/auth/forgot-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await res.json();

        if (data.success) {
            lastEmail = email;
            // Update step indicator
            document.getElementById('step1').className = 'step done';
            document.getElementById('step1').textContent = '✓';
            document.getElementById('line1').className  = 'step-line done';
            document.getElementById('step2').className  = 'step active';
            // Show success
            document.getElementById('formSection').style.display = 'none';
            document.getElementById('sentEmail').textContent      = email;
            document.getElementById('successState').classList.add('show');
        } else {
            errEl.textContent = '❌ ' + data.error;
            errEl.classList.add('show');
            btn.disabled    = false;
            btn.textContent = '🔑 Gửi link đặt lại mật khẩu';
        }
    } catch (e) {
        errEl.textContent = '❌ Lỗi kết nối. Vui lòng thử lại.';
        errEl.classList.add('show');
        btn.disabled    = false;
        btn.textContent = '🔑 Gửi link đặt lại mật khẩu';
    }
}

async function resendEmail() {
    const btn = document.getElementById('resendBtn');
    btn.disabled    = true;
    btn.textContent = '⏳ Đang gửi lại...';

    try {
        await fetch('/api/auth/forgot-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: lastEmail })
        });
        btn.textContent = '✅ Đã gửi lại!';
        setTimeout(() => {
            btn.disabled    = false;
            btn.textContent = '🔄 Gửi lại email';
        }, 5000);
    } catch (e) {
        btn.disabled    = false;
        btn.textContent = '🔄 Gửi lại email';
    }
}