const token = new URLSearchParams(window.location.search).get('token');

// ===== VERIFY TOKEN ON LOAD =====
window.addEventListener('DOMContentLoaded', async () => {
    if (!token) {
        showExpired();
        return;
    }

    try {
        const res  = await fetch(`/api/auth/verify-reset-token?token=${encodeURIComponent(token)}`);
        const data = await res.json();

        document.getElementById('checkingState').style.display = 'none';

        if (data.success) {
            document.getElementById('formSection').style.display = 'block';
        } else {
            showExpired();
        }
    } catch (e) {
        showExpired();
    }
});

function showExpired() {
    document.getElementById('checkingState').style.display = 'none';
    document.getElementById('expiredState').classList.add('show');
}

// ===== STRENGTH CHECK =====
function checkStrength(val) {
    const fill  = document.getElementById('strengthFill');
    const label = document.getElementById('strengthLabel');

    if (!val) { fill.style.width='0'; label.textContent=''; return; }

    let score = 0;
    if (val.length >= 6)  score++;
    if (val.length >= 10) score++;
    if (/[A-Z]/.test(val)) score++;
    if (/[0-9]/.test(val)) score++;
    if (/[^A-Za-z0-9]/.test(val)) score++;

    const levels = [
        { pct:'20%', color:'#e74c3c', text:'⚠️ Rất yếu' },
        { pct:'40%', color:'#e67e22', text:'🔶 Yếu' },
        { pct:'60%', color:'#f1c40f', text:'🔷 Trung bình' },
        { pct:'80%', color:'#2ecc71', text:'✅ Mạnh' },
        { pct:'100%',color:'#27ae60', text:'🔐 Rất mạnh' },
    ];
    const lvl  = levels[Math.min(score - 1, 4)] || levels[0];
    fill.style.width       = lvl.pct;
    fill.style.background  = lvl.color;
    label.textContent      = lvl.text;
    label.style.color      = lvl.color;
}

// ===== TOGGLE PASSWORD VISIBILITY =====
function togglePwd(id, btn) {
    const input = document.getElementById(id);
    if (input.type === 'password') {
        input.type   = 'text';
        btn.textContent = '🙈';
    } else {
        input.type   = 'password';
        btn.textContent = '👁';
    }
}

// ===== SUBMIT =====
async function submitReset() {
    const pwd     = document.getElementById('newPassword').value;
    const confirm = document.getElementById('confirmPassword').value;
    const errEl   = document.getElementById('alertError');
    const btn     = document.getElementById('submitBtn');

    errEl.classList.remove('show');

    if (!pwd || pwd.length < 6) {
        errEl.textContent = '⚠️ Mật khẩu phải có ít nhất 6 ký tự';
        errEl.classList.add('show');
        return;
    }
    if (pwd !== confirm) {
        errEl.textContent = '⚠️ Mật khẩu xác nhận không khớp';
        errEl.classList.add('show');
        return;
    }

    btn.disabled    = true;
    btn.innerHTML   = '<span class="spinner-inline"></span> Đang xử lý...';

    try {
        const res  = await fetch('/api/auth/reset-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token,
                password:         pwd,
                confirm_password: confirm
            })
        });
        const data = await res.json();

        if (data.success) {
            document.getElementById('formSection').style.display = 'none';
            document.getElementById('successState').classList.add('show');
            // Progress bar → redirect
            setTimeout(() => {
                document.getElementById('progressBar').style.width = '100%';
            }, 100);
            setTimeout(() => { window.location.href = '/login'; }, 3200);
        } else {
            errEl.textContent = '❌ ' + data.error;
            errEl.classList.add('show');
            btn.disabled    = false;
            btn.textContent = '✅ Đặt lại mật khẩu';
        }
    } catch (e) {
        errEl.textContent = '❌ Lỗi kết nối';
        errEl.classList.add('show');
        btn.disabled    = false;
        btn.textContent = '✅ Đặt lại mật khẩu';
    }
}