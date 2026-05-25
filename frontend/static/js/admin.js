let currentPageUsers = 1;
let currentPageTacGia = 1;
let currentPageTacPham = 1;

const pageSize = 5;

let allUsers = [];
let allTacGia = [];
let allTacPham = [];
function showTab(tab) {
    // Ẩn tất cả content
    document.querySelectorAll('.tab-content').forEach(content => {
    content.style.display = 'none';
    content.classList.remove('active');
    });

    
    // Reset tất cả tab button
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.style.borderBottom = 'none';
    });
    
    // Hiển thị tab được chọn
    const content = document.getElementById(`content-${tab}`);
    const button = document.getElementById(`tab-${tab}`);
    
    if (content) {
        content.style.display = 'block';
        content.classList.add('active');
    }
    
    if (button) {
        button.classList.add('active');
        button.style.borderBottom = '3px solid #3498db';
    }
    
    // Load dữ liệu theo tab
    switch (tab) {
        case 'users':
            loadUsers();
            break;
    
        case 'thong-ke':
            loadStatistics();
            break;
    
        case 'tac-gia':
            loadTacGiaList();
            break;
    
        case 'tac-pham':
            loadTacPhamList();
            loadTheLoaiDropdown();
            loadGiaiDoanDropdown();
            loadTacGiaDropdown();
            break;
    
        case 'the-loai':
            loadTheLoaiList();
            break;
    
        case 'excel':
            console.log("Tab Excel opened");
            break;
    }
}
function showAlert(msg, type='success') {
    const div = document.createElement('div');
    div.className = `alert alert-${type}`;
    div.textContent = msg;
    document.getElementById('alertContainer').innerHTML = '';
    document.getElementById('alertContainer').appendChild(div);
    setTimeout(() => div.remove(), 5000);
}
async function loadUsers() {
    try {
        const response = await fetch('/api/admin/users', {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.success) {
            displayUsers(data.data);
            allUsers = data.data;
   
        } else {
            showAlert('Lỗi tải danh sách người dùng: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Load users error:', error);
        showAlert('Lỗi kết nối khi tải người dùng', 'error');
    }
}
function displayUsers(users) {
    const tbody = document.getElementById('usersTableBody');
    
    if (!users || users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">Chưa có người dùng</td></tr>';
        return;
    }
    
    tbody.innerHTML = users
    .sort((a, b) => a.id - b.id)
    .map(user => `
        <tr>
            <td>${user.id || '-'}</td>
            <td><strong>${escapeHtml(user.username)}</strong></td>
            <td>${escapeHtml(user.email)}</td>
            <td>${escapeHtml(user.full_name)}</td>
            <td>
                <span class="badge ${user.is_admin ? 'badge-admin' : 'badge-user'}">
                    ${user.is_admin ? 'Admin' : 'User'}
                </span>
            </td>
            <td>
                <span class="badge ${user.is_active ? 'badge-active' : 'badge-inactive'}">
                    ${user.is_active ? 'Hoạt động' : 'Khóa'}
                </span>
            </td>
            <td>${formatDate(user.created_at)}</td>
            <td>
                <button class="btn-toggle-admin" onclick="toggleAdmin(${user.id}, ${!user.is_admin})">
                    ${user.is_admin ? '↓ Gỡ Admin' : '↑ Set Admin'}
                </button>
                <button class="btn-edit" onclick="editUser(${user.id})">Sửa</button>
                <button class="btn-delete" onclick="deleteUser(${user.id}, '${escapeHtml(user.username)}')">Xóa</button>
            </td>
        </tr>
    `).join('');
}
 
/**
 * Open user modal (add/edit)
 */
function openUserModal(userId = null) {
    const modal = document.getElementById('userModal');
    const form = document.getElementById('userForm');
    const title = document.getElementById('userModalTitle');
    
    // Reset form
    form.reset();
    document.getElementById('userEditMode').value = userId ? 'true' : 'false';
    document.getElementById('userId').value = userId || '';
    
    if (userId) {
        title.textContent = 'Sửa người dùng';
        loadUserData(userId);
    } else {
        title.textContent = 'Thêm người dùng';
        document.getElementById('userPassword').required = true;
    }
    
    modal.classList.add('active');
}
 
/**
 * Close user modal
 */
function closeUserModal() {
    document.getElementById('userModal').classList.remove('active');
}
 
/**
 * Load user data for editing
 */
async function loadUserData(userId) {
    try {
        const response = await fetch(`/api/admin/users/${userId}`, {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.success) {
            const user = data.data;
            document.getElementById('userUsername').value = user.username;
            document.getElementById('userEmail').value = user.email;
            document.getElementById('userFullName').value = user.full_name;
            document.getElementById('userIsAdmin').checked = user.is_admin;
            document.getElementById('userIsActive').checked = user.is_active;
            document.getElementById('userPassword').required = false;
        } else {
            showAlert('Lỗi tải thông tin người dùng: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Load user error:', error);
        showAlert('Lỗi kết nối khi tải người dùng', 'error');
    }
}
 
/**
 * Save user (add/edit)
 */
async function saveUser(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const editMode = document.getElementById('userEditMode').value === 'true';
    const userId = document.getElementById('userId').value;
    
    const data = {
        username: formData.get('username'),
        email: formData.get('email'),
        full_name: formData.get('full_name'),
        is_admin: formData.get('is_admin') === 'on',
        is_active: formData.get('is_active') === 'on'
    };
    
    // Add password if provided (or required for new user)
    const password = formData.get('password');
    if (password) {
        data.password = password;
    }
    
    try {
        const url = editMode ? `/api/admin/users/${userId}` : '/api/admin/users';
        const method = editMode ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            credentials: 'include',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        console.log('Save user response:', result);

        if (result.success) {
            showAlert(editMode ? '✓ Cập nhật người dùng thành công!' : '✓ Thêm người dùng thành công!', 'success');
            closeUserModal();
            loadUsers();
        } else {
            showAlert('✗ Lỗi: ' + (result.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Save user error:', error);
        showAlert('✗ Lỗi kết nối khi lưu người dùng', 'error');
    }
}
 
/**
 * Edit user
 */
function editUser(userId) {
    openUserModal(userId);
}
 
/**
 * Delete user
 */
async function deleteUser(userId, username) {
    if (!confirm(`Bạn có chắc muốn xóa người dùng "${username}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/users/${userId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const result = await response.json();
        console.log('Delete user response:', result); 

        if (result.success) {
            showAlert('✓ Xóa người dùng thành công!', 'success');
            loadUsers();
        } else {
            showAlert('✗ Lỗi xóa người dùng: ' + (result.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Delete user error:', error);
        showAlert('✗ Lỗi kết nối khi xóa người dùng', 'error');
    }
}
 
/**
 * Toggle admin role
 */
async function toggleAdmin(userId, makeAdmin) {
    const action = makeAdmin ? 'cấp quyền Admin' : 'gỡ quyền Admin';
    
    if (!confirm(`Bạn có chắc muốn ${action} cho người dùng này?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/users/${userId}/toggle-admin`, {
            method: 'PUT',
            credentials: 'include',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ is_admin: makeAdmin })
        });
        
        const result = await response.json();
        console.log('Toggle admin response:', result); 
    

        if (result.success) {
            showAlert(`✓ ${makeAdmin ? 'Đã cấp' : 'Đã gỡ'} quyền Admin!`, 'success');
            loadUsers();
        } else {
            showAlert('✗ Lỗi: ' + (result.error|| 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Toggle admin error:', error);
        showAlert('✗ Lỗi kết nối', 'error');
    }
}
 
/* ========================================
   STATISTICS
   ======================================== */
 
/**
 * Load statistics
 */
async function loadStats() {
    try {
        const response = await fetch('/api/statistics', {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.success) {
            displayStats(data.data);
        }
    } catch (error) {
        console.error('Load stats error:', error);
    }
}
 
/**
 * Display statistics
 */
function displayStats(data) {
    // Handle nested structure: data.data.tong_quan or data directly
    const stats = data.tong_quan || data;
    
    document.getElementById('statUsers').textContent = stats.total_users || stats.users || 0;
    document.getElementById('statTacGia').textContent = stats.total_tac_gia || stats.tac_gia || 0;
    document.getElementById('statTacPham').textContent = stats.total_tac_pham || stats.tac_pham || 0;
    document.getElementById('statNhanVat').textContent = stats.total_nhan_vat || stats.nhan_vat || 0;
}
 
/* ========================================
   UTILITIES
   ======================================== */
 
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
 * Format date
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}
 
/**
 * Close modal on outside click
 */
window.onclick = function(event) {
    const modal = document.getElementById('userModal');
    if (event.target === modal) {
        closeUserModal();
    }
}
// TÁC GIẢ
async function saveTacGia(e) {
    e.preventDefault();
    const isEdit = document.getElementById('tacGiaEditMode').value === 'true';
    const oldName = document.getElementById('tacGiaOldName').value;
    const fd = new FormData(e.target);
    const data = Object.fromEntries(fd.entries());
    
    const url = isEdit ? `/api/tac-gia/${encodeURIComponent(oldName)}/update` : '/api/tac-gia/create';
    const method = isEdit ? 'PUT' : 'POST';
    
    const res = await fetch(url, {
        method,
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify(data)
    });
    
    const result = await res.json();
    if (result.success) {
        showAlert(isEdit ? '✓ Cập nhật thành công!' : '✓ Thêm thành công!', 'success');
        e.target.reset();
        cancelEditTacGia();
        loadTacGiaList();
    } else {
        showAlert('✗ ' + result.error, 'error');
    }
}

async function loadTacGiaList() {
    const container = document.getElementById('tacGiaList');
    container.innerHTML = '<div class="loading">Đang tải...</div>';
    
    const res = await fetch('/api/tac-gia/');
    const data = await res.json();
    
    if (data.success && data.data.length > 0) {
        // container.innerHTML = `
        //     <table>
        //         <thead><tr><th>Ảnh</th><th>Tên</th><th>Năm sinh</th><th>Quê quán</th><th>Thao tác</th></tr></thead>
        //         <tbody>
        //             ${data.data.map(tg => `
        //                 <tr>
        //                     <td>
        //                         <img src="${tg.anh_dai_dien}" 
        //                             style="width:50px;height:50px;border-radius:50%">
        //                         <!-- Fallback: Icon 👤 -->
        //                     </td>
        //                     <td><strong>${tg.ten}</strong></td>
        //                     <td>${tg.nam_sinh || 'N/A'}</td>
        //                     <td>${tg.que_quan || 'N/A'}</td>
        //                     <td>
        //                         <button onclick="editTacGia('${tg.ten}')" class="btn btn-primary" style="padding:0.3rem 0.8rem;font-size:0.85rem">✏️ Sửa</button>
        //                         <button onclick="deleteTacGia('${tg.ten}')" class="btn btn-danger" style="padding:0.3rem 0.8rem;font-size:0.85rem">🗑️ Xóa</button>
        //                     </td>
        //                 </tr>
        //             `).join('')}
        //         </tbody>
        //     </table>
        // `;
        allTacGia = data.data;
        renderTacGia();
    } else {
        container.innerHTML = '<p>Chưa có tác giả nào</p>';
    }
}

async function editTacGia(ten) {
    const res = await fetch(`/api/tac-gia/${encodeURIComponent(ten)}`);
    const data = await res.json();
    if (!data.success) return;
    
    const tg = data.data;
    document.getElementById('tacGiaFormTitle').textContent = '✏️ Sửa Tác giả: ' + ten;
    document.getElementById('tacGiaEditMode').value = 'true';
    document.getElementById('tacGiaOldName').value = ten;
    document.getElementById('tacGiaTen').value = tg.ten;
    document.querySelector('[name="nam_sinh"]').value = tg.nam_sinh || '';
    document.querySelector('[name="nam_mat"]').value = tg.nam_mat || '';
    document.querySelector('[name="que_quan"]').value = tg.que_quan || '';
    document.querySelector('[name="truong_phai"]').value = tg.truong_phai || '';
    document.querySelector('[name="tieu_su"]').value = tg.tieu_su || '';
    document.querySelector('[name="but_danh"]').value = tg.but_danh || '';
    document.querySelector('[name="giai_thuong"]').value = tg.giai_thuong || '';
    document.querySelector('[name="cau_noi_noi_tieng"]').value = tg.cau_noi_noi_tieng || '';
    if (tg.anh_dai_dien) {
        document.getElementById('tacGiaAnhDaiDien').value = tg.anh_dai_dien || '';
        previewTacGiaImage(tg.anh_dai_dien);
    }
    window.scrollTo({top: 0, behavior: 'smooth'});
}

function cancelEditTacGia() {
    document.getElementById('tacGiaFormTitle').textContent = '➕ Thêm Tác giả mới';
    document.getElementById('tacGiaEditMode').value = 'false';
    document.getElementById('tacGiaOldName').value = '';
    document.getElementById('formTacGia').reset();
    clearTacGiaImage();
}

async function deleteTacGia(ten) {
    if (!confirm(`Xóa tác giả "${ten}"?`)) return;
    const res = await fetch(`/api/tac-gia/${encodeURIComponent(ten)}/delete`, {
        method: 'DELETE',
        credentials: 'include'
    });
    const result = await res.json();
    showAlert(result.success ? '✓ Đã xóa!' : '✗ ' + result.error, result.success ? 'success' : 'error');
    if (result.success) loadTacGiaList();
}
// ===== QUẢN LÝ NHÂN VẬT =====

function addNhanVat() {
    const container = document.getElementById('nhanVatContainer');
    const newItem = document.createElement('div');
    newItem.className = 'nhan-vat-item';
    newItem.style.cssText = 'display:flex;gap:0.5rem;margin-bottom:0.5rem;align-items:flex-start';
    newItem.innerHTML = `
    <input type="text" class="nhan-vat-ten" placeholder="Tên nhân vật" style="flex:1">
    <input type="text" class="nhan-vat-vai-tro" placeholder="Vai trò" style="flex:1">
    <input type="text" class="nhan-vat-tinh-cach" placeholder="Tính cách" style="flex:1">
    
    <select class="nhan-vat-target" style="flex:1">
        <option value="">-- Liên kết với ai --</option>
    </select>

    <input type="text" class="nhan-vat-quan-he" placeholder="Quan hệ" style="flex:1">

    <button type="button" onclick="removeNhanVat(this)" class="btn btn-danger">✕</button>
`;
    container.appendChild(newItem);
    updateAllTargetOptions();
}
function updateAllTargetOptions() {
    const allNames = [];

    document.querySelectorAll(".nhan-vat-ten").forEach(input => {
        if (input.value.trim() !== "") {
            allNames.push(input.value.trim());
        }
    });

    document.querySelectorAll(".nhan-vat-item").forEach(item => {
        const currentName = item.querySelector(".nhan-vat-ten").value;
        const select = item.querySelector(".nhan-vat-target");

        const oldValue = select.value;

        select.innerHTML = `<option value="">-- Liên kết với ai --</option>`;

        allNames.forEach(name => {
            if (name !== currentName) {  
                const option = document.createElement("option");
                option.value = name;
                option.textContent = name;

                if (name === oldValue) option.selected = true;

                select.appendChild(option);
            }
        });
    });
}
function removeNhanVat(button) {
    const container = document.getElementById('nhanVatContainer');
    const items = container.getElementsByClassName('nhan-vat-item');
    
    // Không cho xóa nếu chỉ còn 1 item
    if (items.length > 1) {
        button.closest('.nhan-vat-item').remove();
    } else {
        // Clear thay vì xóa
        container.querySelector('.nhan-vat-ten').value = '';
        container.querySelector('.nhan-vat-vai-tro').value = '';
    }
    updateAllTargetOptions(); 
}

function getNhanVatData() {
    const nhanVatList = [];

    document.querySelectorAll(".nhan-vat-item").forEach(item => {
        const ten = item.querySelector(".nhan-vat-ten").value.trim();
        const vaiTro = item.querySelector(".nhan-vat-vai-tro").value;
        const tinhCach = item.querySelector(".nhan-vat-tinh-cach").value;

        const target = item.querySelector(".nhan-vat-target").value;
        const quanHe = item.querySelector(".nhan-vat-quan-he").value;

        if (ten) {
            let nv = {
                ten,
                vai_tro: vaiTro || "Nhân vật chính",
                tinh_cach: tinhCach || "",
                quan_he: []
            };

            if (target && quanHe) {
                nv.quan_he.push({
                    voi: target,
                    loai: quanHe
                });
            }

            nhanVatList.push(nv);
        }
    });

    return nhanVatList;
}
function setNhanVatData(nhanVatList, quanHeList = []) {
    const container = document.getElementById('nhanVatContainer');
    container.innerHTML = '';

    if (!nhanVatList || nhanVatList.length === 0) {
        addNhanVat();
        return;
    }

    nhanVatList.forEach(nv => {
        const item = document.createElement('div');
        item.className = 'nhan-vat-item';
        item.style.cssText = 'display:flex;gap:0.5rem;margin-bottom:0.5rem;align-items:flex-start';

        item.innerHTML = `
            <input class="nhan-vat-ten" value="${escapeHtml(nv.ten || '')}" style="flex:1">
            <input class="nhan-vat-vai-tro" value="${escapeHtml(nv.vai_tro || '')}" style="flex:1">
            <input class="nhan-vat-tinh-cach" value="${escapeHtml(nv.tinh_cach || '')}" style="flex:1">

            <select class="nhan-vat-target" style="flex:1">
                <option value="">-- Liên kết với ai --</option>
            </select>

            <input class="nhan-vat-quan-he" placeholder="Quan hệ" style="flex:1">

            <button onclick="removeNhanVat(this)">✕</button>
        `;

        container.appendChild(item);
    });

    updateAllTargetOptions();
    setTimeout(() => {
        quanHeList.forEach(qh => {
            document.querySelectorAll(".nhan-vat-item").forEach(item => {
                const ten = item.querySelector(".nhan-vat-ten").value;

                if (ten === qh.from) {
                    const select = item.querySelector(".nhan-vat-target");
                    const input = item.querySelector(".nhan-vat-quan-he");

                    select.value = qh.to;
                    input.value = qh.loai;
                }
            });
        });
    }, 0);
}
function addQuanHe(button) {
    const container = button.parentElement.querySelector('.quan-he-container');

    const div = document.createElement('div');
    div.className = 'quan-he-item';

    div.innerHTML = `
        <input class="qh-voi" placeholder="Với ai">
        <input class="qh-loai" placeholder="Quan hệ">
        <button onclick="this.parentElement.remove()">✕</button>
    `;

    container.appendChild(div);
}
// TÁC PHẨM
async function saveTacPham(e) {
    e.preventDefault();
    const isEdit = document.getElementById('tacPhamEditMode').value === 'true';
    const oldName = document.getElementById('tacPhamOldName').value;
    const fd = new FormData(e.target);
    const data = Object.fromEntries(fd.entries());
    data.nhan_vat = getNhanVatData();
    const trichDoanInputs = document.querySelectorAll('.trich-doan-input');

    const trichDoan = Array.from(trichDoanInputs)
        .map(i => i.value.trim())
        .filter(v => v !== '');

    data.trich_doan = trichDoan; 
    const url = isEdit ? `/api/tac-pham/${encodeURIComponent(oldName)}/update` : '/api/tac-pham/create';
    const method = isEdit ? 'PUT' : 'POST';
    
    const res = await fetch(url, {
        method,
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify(data)
    });
    const nhanVatList = [];
    const quanHeList = [];
    
    document.querySelectorAll(".nhan-vat-item").forEach(item => {
        const ten = item.querySelector(".nhan-vat-ten").value.trim();
        const vaiTro = item.querySelector(".nhan-vat-vai-tro").value;
        const tinhCach = item.querySelector(".nhan-vat-tinh-cach").value;
    
        const target = item.querySelector(".nhan-vat-target").value;
        const quanHe = item.querySelector(".nhan-vat-quan-he").value;
    
        if (ten !== "") {
            nhanVatList.push({
                ten,
                vai_tro: vaiTro,
                tinh_cach: tinhCach
            });
    
            if (target && quanHe) {
                quanHeList.push({
                    from: ten,
                    to: target,
                    loai: quanHe
                });
            }
        }
    });
   
    const result = await res.json();
    if (result.success) {
        showAlert(isEdit ? '✓ Cập nhật thành công!' : '✓ Thêm thành công!', 'success');
        e.target.reset();
        setNhanVatData([]);
        cancelEditTacPham();
        loadTacPhamList();
    } else {
        showAlert('✗ ' + result.error, 'error');
    }
}

async function loadTacPhamList() {
    const container = document.getElementById('tacPhamList');
    container.innerHTML = '<div class="loading">Đang tải...</div>';
    
    const res = await fetch('/api/tac-pham/');
    const data = await res.json();
    
    if (data.success && data.data.length > 0) {
        // container.innerHTML = `
        //     <table>
        //         <thead><tr><th>Ảnh</th><th>Tên</th><th>Tác giả</th><th>Năm</th><th>Thao tác</th></tr></thead>
        //         <tbody>
        //             ${data.data.map(tp => `
        //                 <tr>
        //                    <td>
        //                                 ${tp.anh_dai_dien ? 
        //                                     `<img src="${tp.anh_dai_dien}" 
        //                                           alt="${tp.ten}" 
        //                                           style="width:50px;height:70px;object-fit:cover;border-radius:4px;box-shadow:0 2px 6px rgba(0,0,0,0.15)"
        //                                           onerror="this.src='/static/images/default_cover.jpg';">` 
        //                                     : 
        //                                     `<div style="width:50px;height:70px;background:#e0e0e0;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:1.5rem">📖</div>`
        //                                 }
        //                     </td>
        //                     <td><strong>${tp.ten}</strong></td>
        //                     <td>${tp.tac_gia || 'N/A'}</td>
        //                     <td>${tp.nam_sang_tac || 'N/A'}</td>
        //                     <td>
        //                         <button onclick="editTacPham('${tp.ten}')" class="btn btn-primary" style="padding:0.3rem 0.8rem;font-size:0.85rem">✏️ Sửa</button>
        //                         <button onclick="deleteTacPham('${tp.ten}')" class="btn btn-danger" style="padding:0.3rem 0.8rem;font-size:0.85rem">🗑️ Xóa</button>
        //                     </td>
        //                 </tr>
        //             `).join('')}
        //         </tbody>
        //     </table>
        // `;
        allTacPham = data.data;
        renderTacPham();
    } else {
        container.innerHTML = '<p>Chưa có tác phẩm nào</p>';
    }
}
function previewTacPhamImage(url) {
    const preview = document.getElementById('tacPhamImagePreview');
    const img = document.getElementById('tacPhamPreviewImg');
    
    if (url && url.trim()) {
        img.src = url;
        preview.style.display = 'block';
    } else {
        preview.style.display = 'none';
    }
}
function previewTacGiaImage(url) {
    const preview = document.getElementById('tacGiaImagePreview');
    const img = document.getElementById('tacGiaPreviewImg');
    
    if (url && url.trim()) {
        img.src = url;
        preview.style.display = 'block';
    } else {
        preview.style.display = 'none';
    }
}
function clearTacGiaImage() {
    document.getElementById('tacGiaAnhDaiDien').value = '';
    document.getElementById('tacGiaImagePreview').style.display = 'none';
}

function clearTacPhamImage() {
    document.getElementById('tacPhamAnhDaiDien').value = '';
    document.getElementById('tacPhamImagePreview').style.display = 'none';
}
async function editTacPham(ten) {
    const res = await fetch(`/api/tac-pham/${encodeURIComponent(ten)}`);
    const data = await res.json();
    if (!data.success) return;
    
    const tp = data.data;
    document.getElementById('tacPhamFormTitle').textContent = '✏️ Sửa Tác phẩm: ' + ten;
    document.getElementById('tacPhamEditMode').value = 'true';
    document.getElementById('tacPhamOldName').value = ten;
    document.querySelector('#formTacPham [name="ten"]').value = tp.ten;
    document.querySelector('#formTacPham [name="anh_dai_dien"]').value = tp.anh_dai_dien || '';
            
    // Preview ảnh nếu có
    if (tp.anh_dai_dien) {
        previewTacPhamImage(tp.anh_dai_dien);
    }
    const tacGiaSelect = document.getElementById('tacPhamTacGia');
    if (tacGiaSelect && tp.tac_gia) {
        tacGiaSelect.value = tp.tac_gia;
    }
    document.querySelector('#formTacPham [name="nam_sang_tac"]').value = tp.nam_sang_tac || '';
    document.querySelector('#formTacPham [name="nam_xuat_ban"]').value = tp.nam_xuat_ban || '';
    document.querySelector('#formTacPham [name="noi_dung_tom_tat"]').value = tp.noi_dung_tom_tat || '';
    document.querySelector('#formTacPham [name="chu_de_chinh"]').value = tp.chu_de_chinh || '';
    document.querySelector('#formTacPham [name="y_nghia"]').value = tp.y_nghia || '';
    document.querySelector('#formTacPham [name="gia_tri_nghe_thuat"]').value = tp.gia_tri_nghe_thuat || '';
    document.querySelector('#formTacPham [name="hoan_canh"]').value = tp.hoan_canh || '';
    document.querySelector('#formTacPham [name="cau_truc"]').value = tp.cau_truc || '';

    // Load giai đoạn
    const giaiDoanSelect = document.getElementById('tacPhamGiaiDoan');
    if (giaiDoanSelect && tp.giai_doan) {
        giaiDoanSelect.value = tp.giai_doan;
    }

    const theLoaiSelect = document.getElementById('tacPhamTheLoai');
    if (theLoaiSelect && tp.the_loai) {
        theLoaiSelect.value = tp.the_loai;
    }
   

    // Load nhân vật - Lọc bỏ null
    if (tp.nhan_vat && tp.nhan_vat.length > 0) {
        const validNhanVat = tp.nhan_vat.filter(nv => nv && nv.ten);
        if (validNhanVat.length > 0) {
            setNhanVatData(validNhanVat, tp.quan_he || []);
        } else {
            setNhanVatData([], []);
        }
    } else {
        setNhanVatData([], []);
    }

    setTrichDoanData(tp.trich_doan);
    window.scrollTo({top: 0, behavior: 'smooth'});
}

function cancelEditTacPham() {
    document.getElementById('tacPhamFormTitle').textContent = '➕ Thêm Tác phẩm mới';
    document.getElementById('tacPhamEditMode').value = 'false';
    document.getElementById('tacPhamOldName').value = '';
    document.getElementById('formTacPham').reset();
    clearTacPhamImage();
}
async function loadTacGiaDropdown() {
    try {
        const res = await fetch('/api/tac-gia/');
        const data = await res.json();

        if (data.success) {
            const select = document.getElementById('tacPhamTacGia');

            select.innerHTML = '<option value="">-- Chọn tác giả --</option>';

            data.data.forEach(tg => {
                const option = document.createElement('option');
                option.value = tg.ten;
                option.textContent = tg.ten;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Lỗi load tác giả:', error);
    }
}
async function deleteTacPham(ten) {
    if (!confirm(`Xóa tác phẩm "${ten}"?`)) return;
    const res = await fetch(`/api/tac-pham/${encodeURIComponent(ten)}/delete`, {
        method: 'DELETE',
        credentials: 'include'
    });
    const result = await res.json();
    showAlert(result.success ? '✓ Đã xóa!' : '✗ ' + result.error, result.success ? 'success' : 'error');
    if (result.success) loadTacPhamList();
}

async function saveTheLoai(e) {
    e.preventDefault();
    const isEdit = document.getElementById('theLoaiEditMode').value === 'true';
    const oldName = document.getElementById('theLoaiOldName').value;
    const fd = new FormData(e.target);
    const data = Object.fromEntries(fd.entries());
    
    const url = isEdit ? `/api/the-loai/${encodeURIComponent(oldName)}/update` : '/api/the-loai/create';
    const method = isEdit ? 'PUT' : 'POST';
    
    try {
        const res = await fetch(url, {
            method,
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        const result = await res.json();
        
        if (result.success) {
            showAlert(isEdit ? '✓ Cập nhật thành công!' : '✓ Thêm thành công!', 'success');
            e.target.reset();
            cancelEditTheLoai();
            loadTheLoaiList();
        } else {
            showAlert('✗ ' + result.error, 'error');
        }
    } catch (error) {
        showAlert('✗ Lỗi: ' + error.message, 'error');
    }
}

async function loadTheLoaiList() {
    const container = document.getElementById('theLoaiList');
    container.innerHTML = '<div class="loading">Đang tải...</div>';
    
    try {
        const res = await fetch('/api/the-loai/');
        const data = await res.json();
        
        if (data.success && data.data.length > 0) {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Tên thể loại</th>
                            <th>Mô tả</th>
                            <th>Số tác phẩm</th>
                            <th>Thao tác</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.data.map(tl => `
                            <tr>
                                <td><strong>${tl.ten}</strong></td>
                                <td>${tl.mo_ta || 'N/A'}</td>
                                <td>${tl.so_luong_tac_pham || 0}</td>
                                <td>
                                    <button onclick="editTheLoai('${escapeHtml(tl.ten)}')" 
                                            class="btn btn-primary" 
                                            style="padding:0.3rem 0.8rem;font-size:0.85rem">
                                        ✏️ Sửa
                                    </button>
                                    <button onclick="deleteTheLoai('${escapeHtml(tl.ten)}')" 
                                            class="btn btn-danger" 
                                            style="padding:0.3rem 0.8rem;font-size:0.85rem">
                                        🗑️ Xóa
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<p>Chưa có thể loại nào</p>';
        }
    } catch (error) {
        container.innerHTML = `<div class="alert alert-error">Lỗi: ${error.message}</div>`;
    }
}

async function editTheLoai(ten) {
    try {
        const res = await fetch(`/api/the-loai/${encodeURIComponent(ten)}`);
        const data = await res.json();
        
        if (!data.success) {
            showAlert('✗ Không tìm thấy thể loại', 'error');
            return;
        }
        
        const tl = data.data;
        document.getElementById('theLoaiFormTitle').textContent = '✏️ Sửa Thể loại: ' + ten;
        document.getElementById('theLoaiEditMode').value = 'true';
        document.getElementById('theLoaiOldName').value = ten;
        document.getElementById('theLoaiTen').value = tl.ten;
        document.getElementById('theLoaiTen').disabled = true; // Không cho đổi tên
        document.querySelector('#formTheLoai [name="mo_ta"]').value = tl.mo_ta || '';
        
        window.scrollTo({top: 0, behavior: 'smooth'});
    } catch (error) {
        showAlert('✗ Lỗi: ' + error.message, 'error');
    }
}

function cancelEditTheLoai() {
    document.getElementById('theLoaiFormTitle').textContent = '➕ Thêm Thể loại mới';
    document.getElementById('theLoaiEditMode').value = 'false';
    document.getElementById('theLoaiOldName').value = '';
    document.getElementById('theLoaiTen').disabled = false;
    document.getElementById('formTheLoai').reset();
}

async function deleteTheLoai(ten) {
    if (!confirm(`Xóa thể loại "${ten}"?\n\nLưu ý: Chỉ xóa được nếu không có tác phẩm nào thuộc thể loại này.`)) {
        return;
    }
    
    try {
        const res = await fetch(`/api/the-loai/${encodeURIComponent(ten)}/delete`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const result = await res.json();
        
        if (result.success) {
            showAlert('✓ Đã xóa thể loại!', 'success');
            loadTheLoaiList();
        } else {
            showAlert('✗ ' + result.error, 'error');
        }
    } catch (error) {
        showAlert('✗ Lỗi: ' + error.message, 'error');
    }
}

 
 
// Load danh sách thể loại vào dropdown
async function loadTheLoaiDropdown() {
    try {
        const res = await fetch('/api/the-loai/');
        const data = await res.json();
        
        if (data.success) {
            const select = document.getElementById('tacPhamTheLoai');
            
            // Xóa các option cũ (trừ option đầu tiên)
            select.innerHTML = '<option value="">-- Chọn thể loại --</option>';
            
            // Thêm các option mới
            data.data.forEach(tl => {
                const option = document.createElement('option');
                option.value = tl.ten;
                option.textContent = tl.ten;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Lỗi khi load thể loại:', error);
    }
}
// Load danh sách giai đoạn vào dropdown
async function loadGiaiDoanDropdown() {
    try {
        const res = await fetch('/api/tac-pham/giai-doan');
        const data = await res.json();
        
        if (data.success) {
            const select = document.getElementById('tacPhamGiaiDoan');
            
            // Xóa các option cũ (trừ option đầu tiên)
            select.innerHTML = '<option value="">-- Chọn giai đoạn --</option>';
            
            // Thêm các option mới
            data.data.forEach(gd => {
                const option = document.createElement('option');
                option.value = gd.ten;
                option.textContent = `${gd.ten}`;
                option.title = gd.dac_diem; // Tooltip
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Lỗi khi load giai đoạn:', error);
    }
}
function paginate(data, page) {
    const start = (page - 1) * pageSize;
    return data.slice(start, start + pageSize);
}

function renderPagination(totalItems, currentPage, onPageChange, containerId) {
    const totalPages = Math.ceil(totalItems / pageSize);
    const container = document.getElementById(containerId);

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';

    for (let i = 1; i <= totalPages; i++) {
        html += `
            <button 
                onclick="${onPageChange}(${i})" 
                style="margin:2px; padding:5px 10px; 
                ${i === currentPage ? 'background:#3498db;color:white' : ''}">
                ${i}
            </button>
        `;
    }

    container.innerHTML = html;
}
function renderUsers() {
    const keyword = document.getElementById('searchUsers')?.value?.toLowerCase() || '';

    let filtered = allUsers.filter(u =>
        u.username.toLowerCase().includes(keyword) ||
        u.email.toLowerCase().includes(keyword)
    );

    const pageData = paginate(filtered, currentPageUsers);

    displayUsers(pageData);

    renderPagination(filtered.length, currentPageUsers, 'changePageUsers', 'paginationUsers');
}

function changePageUsers(page) {
    currentPageUsers = page;
    renderUsers();
}
function renderTacGia() {
    const keyword = document.getElementById('searchTacGia')?.value?.toLowerCase() || '';

    let filtered = allTacGia.filter(tg =>
        tg.ten.toLowerCase().includes(keyword)
    );

    const pageData = paginate(filtered, currentPageTacGia);

    const container = document.getElementById('tacGiaList');
    container.innerHTML = `
    <table>
        <thead><tr><th>Ảnh</th><th>Tên</th><th>Năm sinh</th><th>Quê quán</th><th>Thao tác</th></tr></thead>
        <tbody>
        ${pageData.map(tg => `
                <tr>
                    <td>
                        <img src="${tg.anh_dai_dien}" 
                            style="width:50px;height:50px;border-radius:50%">
                        <!-- Fallback: Icon 👤 -->
                    </td>
                    <td><strong>${tg.ten}</strong></td>
                    <td>${tg.nam_sinh || 'N/A'}</td>
                    <td>${tg.que_quan || 'N/A'}</td>
                    <td>
                        <button onclick="editTacGia('${tg.ten}')" class="btn btn-primary" style="padding:0.3rem 0.8rem;font-size:0.85rem">✏️ Sửa</button>
                        <button onclick="deleteTacGia('${tg.ten}')" class="btn btn-danger" style="padding:0.3rem 0.8rem;font-size:0.85rem">🗑️ Xóa</button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    </table>
      <div id="paginationTacGia"></div>
`;
    renderPagination(filtered.length, currentPageTacGia, 'changePageTacGia', 'paginationTacGia');
}

function changePageTacGia(page) {
    currentPageTacGia = page;
    renderTacGia();
}
function renderTacPham(list = allTacPham, page = 1) {
    const keyword = document.getElementById('searchTacPham')?.value?.toLowerCase() || '';

    let filtered = allTacPham.filter(tp =>
        tp.ten.toLowerCase().includes(keyword) ||
        (tp.tac_gia || '').toLowerCase().includes(keyword)
    );
    const pageData = paginate(filtered, currentPageTacPham);

    const container = document.getElementById('tacPhamList');

     
    container.innerHTML = `
    <table>
        <thead><tr><th>Ảnh</th><th>Tên</th><th>Tác giả</th><th>Năm</th><th>Thao tác</th></tr></thead>
        <tbody>
        ${pageData.map(tp => `
                <tr>
                   <td>
                                ${tp.anh_dai_dien ? 
                                    `<img src="${tp.anh_dai_dien}" 
                                          alt="${tp.ten}" 
                                          style="width:50px;height:70px;object-fit:cover;border-radius:4px;box-shadow:0 2px 6px rgba(0,0,0,0.15)"
                                          onerror="this.src='/static/images/default_cover.jpg';">` 
                                    : 
                                    `<div style="width:50px;height:70px;background:#e0e0e0;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:1.5rem">📖</div>`
                                }
                    </td>
                    <td><strong>${tp.ten}</strong></td>
                    <td>${tp.tac_gia || 'N/A'}</td>
                    <td>${tp.nam_sang_tac || 'N/A'}</td>
                    <td>
                        <button onclick="editTacPham('${tp.ten}')" class="btn btn-primary" style="padding:0.3rem 0.8rem;font-size:0.85rem">✏️ Sửa</button>
                        <button onclick="deleteTacPham('${tp.ten}')" class="btn btn-danger" style="padding:0.3rem 0.8rem;font-size:0.85rem">🗑️ Xóa</button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    </table>
        <div id="paginationTacPham"></div>
`;                
    renderPagination(list.length, currentPageTacPham, 'changePageTacPham', 'paginationTacPham');
}

function changePageTacPham(page) {
    currentPageTacPham = page;
    renderTacPham();
}
function searchTacGia() {
    const keyword = document.getElementById("searchTacGia").value.toLowerCase();

    const filtered = allTacGia.filter(tg =>
        tg.ten.toLowerCase().includes(keyword)
    );

    renderTacGia(filtered, 1);
}
function searchUsers(keyword) {
    keyword = keyword.toLowerCase();

    const filtered = allUsers.filter(u =>
        (u.username && u.username.toLowerCase().includes(keyword)) ||
        (u.email && u.email.toLowerCase().includes(keyword)) ||
        (u.full_name && u.full_name.toLowerCase().includes(keyword))
    );

    displayUsers(filtered);
}
function searchTacPham() {
    const keyword = document
        .getElementById("searchTacPham")
        .value
        .toLowerCase();

    const filtered = allTacPham.filter(tp =>
        (tp.ten && tp.ten.toLowerCase().includes(keyword)) ||
        (tp.tac_gia && tp.tac_gia.toLowerCase().includes(keyword))
    );

    renderTacPham(filtered, 1);
}
function addTrichDoan(value = "") {
    const container = document.getElementById("trichDoanContainer");

    const index = container.children.length + 1;  

    const div = document.createElement("div");
    div.style.display = "flex";
    div.style.flexDirection = "column";
    div.style.marginBottom = "0.5rem";

    div.innerHTML = `
        <label style="font-weight:bold">Trích đoạn ${index}</label>
        <div style="display:flex;gap:0.5rem">
            <textarea class="trich-doan-input" 
                      placeholder="Nhập trích đoạn..." 
                      style="flex:1;min-height:60px">${value}</textarea>
            <button type="button" onclick="removeTrichDoan(this)" 
                    class="btn btn-danger">✕</button>
        </div>
    `;

    container.appendChild(div);
}
function removeTrichDoan(btn) {
    btn.closest("div").parentElement.remove();
    updateTrichDoanIndex();
}

function updateTrichDoanIndex() {
    const container = document.getElementById("trichDoanContainer");
    const items = container.children;

    for (let i = 0; i < items.length; i++) {
        const label = items[i].querySelector("label");
        label.textContent = `Trích đoạn ${i + 1}`;
    }
}
document.addEventListener("DOMContentLoaded", () => {
    addTrichDoan();
});
function setTrichDoanData(list) {
    const container = document.getElementById("trichDoanContainer");
    container.innerHTML = "";

    if (!list || list.length === 0) {
        addTrichDoan();
        return;
    }

    list.forEach(td => addTrichDoan(td));
}
 // ===== CHART INSTANCES (để destroy khi reload) =====
 const charts = {};
 
 // ===== PALETTE =====
 const COLORS = [
     '#8B4513','#1565C0','#2E7D32','#6A1B9A','#C62828',
     '#F57F17','#00838F','#AD1457','#37474F','#4E342E',
 ];
 const COLORS_ALPHA = (opacity=0.85) =>
     COLORS.map(c => c + Math.round(opacity*255).toString(16).padStart(2,'0'));

 // ===== LOAD STATISTICS =====
 async function loadStatistics() {
     try {
         const res  = await fetch('/api/statistics');
         const data = await res.json();
         if (!data.success) return;

         const d = data.data;
         const q = d.tong_quan;

         // KPI
         animateNumber('statTacGia',  q.tac_gia  || 0);
         animateNumber('statTacPham', q.tac_pham || 0);
         animateNumber('statNhanVat', q.nhan_vat || 0);
         animateNumber('statTheLoai', q.the_loai || 0);
         animateNumber('statUsers',   q.users    || 0);

         // Charts
         renderDonutTheLoai(d.theo_the_loai   || []);
         renderBarGiaiDoan (d.theo_giai_doan  || []);
         renderBarTacGia   (d.tac_gia_nhieu_tp|| []);
         renderLineNam     (d.tp_by_year      || []);
         renderBarNhanVat  (d.nhan_vat_by_tp  || []);

     } catch(e) {
         console.error('Lỗi load thống kê:', e);
     }
 }

 // ===== ANIMATE NUMBER =====
 function animateNumber(id, target) {
     const el  = document.getElementById(id);
     if (!el) return;
     const dur = 1000;
     const step= 16;
     const inc = target / (dur / step);
     let cur   = 0;
     const t   = setInterval(() => {
         cur = Math.min(cur + inc, target);
         el.textContent = Math.round(cur).toLocaleString('vi-VN');
         if (cur >= target) clearInterval(t);
     }, step);
 }

 // ===== DESTROY OLD CHART =====
 function destroyChart(id) {
     if (charts[id]) { charts[id].destroy(); delete charts[id]; }
 }

 // ===== 1. DONUT: THỂ LOẠI =====
 function renderDonutTheLoai(data) {
     destroyChart('theLoai');
     if (!data.length) return;
     const labels = data.map(d => d.the_loai || d.ten || '?');
     const values = data.map(d => d.so_luong);
     const ctx    = document.getElementById('chartTheLoai').getContext('2d');
     charts.theLoai = new Chart(ctx, {
         type: 'doughnut',
         data: {
             labels,
             datasets:[{
                 data: values,
                 backgroundColor: COLORS,
                 borderWidth: 3,
                 borderColor: '#fff',
                 hoverOffset: 12,
             }]
         },
         options: {
             responsive: true,
             maintainAspectRatio: false,
             cutout: '62%',
             plugins: {
                 legend: {
                     position: 'right',
                     labels: {
                         boxWidth: 14, padding: 12,
                         font: { size: 12 },
                         color: '#444',
                     }
                 },
                 tooltip: {
                     callbacks: {
                         label: ctx =>
                             ` ${ctx.label}: ${ctx.parsed} tác phẩm`
                     }
                 }
             }
         }
     });
 }

 // ===== 2. BAR NGANG: GIAI ĐOẠN =====
 function renderBarGiaiDoan(data) {
     destroyChart('giaiDoan');
     if (!data.length) return;
     // Rút gọn tên giai đoạn
     const shortName = n => n ? n.replace('Văn học ', '').replace(/\(.*\)/,'').trim() : '?';
     const labels = data.map(d => shortName(d.giai_doan));
     const values = data.map(d => d.so_luong);
     const ctx    = document.getElementById('chartGiaiDoan').getContext('2d');
     charts.giaiDoan = new Chart(ctx, {
         type: 'bar',
         data: {
             labels,
             datasets:[{
                 label: 'Số tác phẩm',
                 data: values,
                 backgroundColor: COLORS.slice(0, data.length),
                 borderRadius: 8,
                 borderSkipped: false,
             }]
         },
         options: {
             indexAxis: 'y',
             responsive: true,
             maintainAspectRatio: false,
             plugins: {
                 legend: { display: false },
                 tooltip: {
                     callbacks: {
                         label: ctx => ` ${ctx.parsed.x} tác phẩm`
                     }
                 }
             },
             scales: {
                 x: {
                     grid: { color: 'rgba(0,0,0,.05)' },
                     ticks: { precision: 0, color:'#666' },
                     border: { display: false }
                 },
                 y: {
                     grid: { display: false },
                     ticks: { color:'#444', font:{ size:11 } }
                 }
             }
         }
     });
 }

 // ===== 3. BAR DỌC: TÁC GIẢ =====
 function renderBarTacGia(data) {
     destroyChart('tacGia');
     if (!data.length) return;
     const labels = data.map(d => d.ten);
     const values = data.map(d => d.so_luong);
     const ctx    = document.getElementById('chartTacGia').getContext('2d');

     // Gradient
     const grad = ctx.createLinearGradient(0, 0, 0, 300);
     grad.addColorStop(0,   'rgba(139,69,19,.9)');
     grad.addColorStop(1,   'rgba(210,105,30,.4)');

     charts.tacGia = new Chart(ctx, {
         type: 'bar',
         data: {
             labels,
             datasets:[{
                 label: 'Số tác phẩm',
                 data: values,
                 backgroundColor: grad,
                 borderRadius: 8,
                 borderSkipped: false,
             }]
         },
         options: {
             responsive: true,
             maintainAspectRatio: false,
             plugins: {
                 legend: { display: false },
                 tooltip: {
                     callbacks: {
                         label: ctx => ` ${ctx.parsed.y} tác phẩm`
                     }
                 }
             },
             scales: {
                 x: {
                     grid: { display: false },
                     ticks: {
                         maxRotation: 30,
                         font: { size: 11 }, color: '#444',
                         callback: (v, i) => {
                             const l = labels[i];
                             return l.length > 12 ? l.slice(0,12)+'…' : l;
                         }
                     }
                 },
                 y: {
                     grid: { color:'rgba(0,0,0,.05)' },
                     ticks: { precision:0, color:'#666' },
                     border: { display:false }
                 }
             }
         }
     });
 }

 // ===== 4. LINE: NĂM SÁNG TÁC =====
 function renderLineNam(data) {
     destroyChart('namSangTac');
     if (!data.length) return;
     const labels = data.map(d => d.nam);
     const values = data.map(d => d.so_luong);
     const ctx    = document.getElementById('chartNamSangTac').getContext('2d');

     const grad = ctx.createLinearGradient(0, 0, 0, 280);
     grad.addColorStop(0,   'rgba(21,101,192,.35)');
     grad.addColorStop(1,   'rgba(21,101,192,.02)');

     charts.namSangTac = new Chart(ctx, {
         type: 'line',
         data: {
             labels,
             datasets:[{
                 label: 'Số tác phẩm',
                 data: values,
                 borderColor: '#1565C0',
                 backgroundColor: grad,
                 borderWidth: 2.5,
                 pointBackgroundColor: '#1565C0',
                 pointRadius: 5,
                 pointHoverRadius: 8,
                 tension: 0.4,
                 fill: true,
             }]
         },
         options: {
             responsive: true,
             maintainAspectRatio: false,
             plugins: {
                 legend: { display: false },
                 tooltip: {
                     callbacks: {
                         label: ctx => ` ${ctx.parsed.y} tác phẩm`
                     }
                 }
             },
             scales: {
                 x: {
                     grid: { color:'rgba(0,0,0,.05)' },
                     ticks: { maxRotation:45, color:'#666', font:{size:11} }
                 },
                 y: {
                     grid: { color:'rgba(0,0,0,.05)' },
                     ticks: { precision:0, color:'#666' },
                     border:{ display:false }
                 }
             }
         }
     });
 }

 // ===== 5. BAR: NHÂN VẬT =====
 function renderBarNhanVat(data) {
     destroyChart('nhanVat');
     if (!data.length) return;
     const labels = data.map(d => d.ten);
     const values = data.map(d => d.so_nhan_vat);
     const ctx    = document.getElementById('chartNhanVat').getContext('2d');

     const grad = ctx.createLinearGradient(0, 0, 0, 250);
     grad.addColorStop(0, 'rgba(46,125,50,.9)');
     grad.addColorStop(1, 'rgba(56,142,60,.4)');

     charts.nhanVat = new Chart(ctx, {
         type: 'bar',
         data: {
             labels,
             datasets:[{
                 label: 'Số nhân vật',
                 data: values,
                 backgroundColor: grad,
                 borderRadius: 8,
                 borderSkipped: false,
             }]
         },
         options: {
             responsive: true,
             maintainAspectRatio: false,
             plugins: {
                 legend: { display: false },
                 tooltip: {
                     callbacks: {
                         label: ctx => ` ${ctx.parsed.y} nhân vật`
                     }
                 }
             },
             scales: {
                 x: {
                     grid: { display: false },
                     ticks: {
                         maxRotation: 25,
                         font:{size:11}, color:'#444',
                         callback: (v, i) => {
                             const l = labels[i];
                             return l.length > 14 ? l.slice(0,14)+'…' : l;
                         }
                     }
                 },
                 y: {
                     grid: { color:'rgba(0,0,0,.05)' },
                     ticks: { precision:0, color:'#666' },
                     border: { display:false }
                 }
             }
         }
     });
 }
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    loadStats();
    document.addEventListener("input", function(e) {
        if (e.target.classList.contains("nhan-vat-ten")) {
            updateAllTargetOptions();
        }
    });
     // ===== SEARCH =====

    // Tác giả
    const searchTG = document.getElementById("searchTacGia");
    if (searchTG) {
        searchTG.addEventListener("input", () => {
            if (typeof searchTacGia === "function") {
                searchTacGia();
            }
        });
    }

    // Người dùng
    const searchUser = document.getElementById("searchUser");
    if (searchUser) {
        searchUser.addEventListener("input", () => {
            if (typeof searchUsers === "function") {
                searchUsers();
            }
        });
    }

    const searchTP = document.getElementById("searchTacPham");

    if (searchTP) {
        searchTP.addEventListener("input", searchTacPham);
    }
});
// ===============================
// TOAST
// ===============================
function showToast(message, type = 'success') {

    const toast = document.createElement('div');

    toast.innerText = message;

    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.padding = '12px 18px';
    toast.style.borderRadius = '10px';
    toast.style.color = '#fff';
    toast.style.fontWeight = 'bold';
    toast.style.boxShadow = '0 4px 10px rgba(0,0,0,0.2)';
    toast.style.transition = '0.3s';

    toast.style.background =
        type === 'error' ? '#e53935' :
        type === 'warning' ? '#fb8c00' :
        '#43a047';

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
    }, 2500);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}


// ===============================
// EXCEL IMPORT / EXPORT
// ===============================

let selectedExcelFile = null;


// ===============================
// EXPORT EXCEL
// ===============================
async function exportExcel(type) {

    try {

        const loading = document.getElementById('exportLoading');

        if (loading) {
            loading.style.display = 'block';
        }

        let url = '/api/excel/export';

        if (type === 'tac-gia') {
            url = '/api/excel/export/tac-gia';
        }
        else if (type === 'tac-pham') {
            url = '/api/excel/export/tac-pham';
        }
        else if (type === 'template') {
            url = '/api/excel/template';
        }

        const response = await fetch(url, {
            method: 'GET',
            credentials: 'include'
        });

        // Nếu lỗi
        if (!response.ok) {

            let errorMessage = 'Lỗi export Excel';

            const contentType = response.headers.get('content-type');

            // Nếu backend trả JSON
            if (contentType && contentType.includes('application/json')) {

                const err = await response.json();

                errorMessage = err.error || errorMessage;
            }
            else {

                // Flask trả HTML lỗi 500
                const text = await response.text();

                console.error(text);
            }

            throw new Error(errorMessage);
        }

        // =========================
        // DOWNLOAD FILE
        // =========================

        const blob = await response.blob();

        const downloadUrl = window.URL.createObjectURL(blob);

        const a = document.createElement('a');

        a.href = downloadUrl;

        // lấy filename từ header
        const disposition = response.headers.get('Content-Disposition');

        let filename = 'export.xlsx';

        if (disposition && disposition.includes('filename=')) {

            filename = disposition
                .split('filename=')[1]
                .replace(/"/g, '');
        }

        a.download = filename;

        document.body.appendChild(a);

        a.click();

        a.remove();

        window.URL.revokeObjectURL(downloadUrl);

        showToast('✅ Xuất Excel thành công!');

    }
    catch (err) {

        console.error('EXPORT ERROR:', err);

        showToast(err.message || 'Lỗi export Excel!', 'error');
    }
    finally {

        const loading = document.getElementById('exportLoading');

        if (loading) {
            loading.style.display = 'none';
        }
    }
}


// ===============================
// FILE SELECT
// ===============================
function handleFileSelect(input) {

    if (!input.files || !input.files[0]) return;

    const file = input.files[0];

    processSelectedFile(file);
}


// ===============================
// DRAG DROP
// ===============================
function handleDragOver(event) {

    event.preventDefault();

    const zone = document.getElementById('dropZone');

    zone.style.background = '#e3f2fd';

    zone.style.borderColor = '#0d47a1';
}

function handleDragLeave(event) {

    event.preventDefault();

    resetDropZone();
}

function handleDrop(event) {

    event.preventDefault();

    resetDropZone();

    const files = event.dataTransfer.files;

    if (files.length > 0) {

        processSelectedFile(files[0]);
    }
}

function resetDropZone() {

    const zone = document.getElementById('dropZone');

    zone.style.background = '#f8fbff';

    zone.style.borderColor = '#1565C0';
}


// ===============================
// PROCESS FILE
// ===============================
function processSelectedFile(file) {

    if (!file.name.endsWith('.xlsx')) {

        showToast('❌ Chỉ hỗ trợ file .xlsx', 'error');

        return;
    }

    selectedExcelFile = file;

    document.getElementById('filePreview').style.display = 'block';

    document.getElementById('fileName').innerText = file.name;

    document.getElementById('fileSize').innerText =
        (file.size / 1024).toFixed(2) + ' KB';

    const btn = document.getElementById('importBtn');

    btn.disabled = false;

    btn.style.opacity = '1';

    btn.style.cursor = 'pointer';
}


// ===============================
// CLEAR FILE
// ===============================
function clearFile() {

    selectedExcelFile = null;

    document.getElementById('filePreview').style.display = 'none';

    document.getElementById('excelFileInput').value = '';

    const btn = document.getElementById('importBtn');

    btn.disabled = true;

    btn.style.opacity = '0.5';

    btn.style.cursor = 'not-allowed';

    document.getElementById('importResult').style.display = 'none';
}


// ===============================
// IMPORT EXCEL
// ===============================
async function importExcel() {

    if (!selectedExcelFile) {

        showToast('⚠️ Vui lòng chọn file!', 'error');

        return;
    }

    try {

        document.getElementById('importLoading').style.display = 'block';

        const formData = new FormData();

        formData.append('file', selectedExcelFile);

        const response = await fetch('/api/excel/import', {

            method: 'POST',

            credentials: 'include',

            body: formData
        });

        const result = await response.json();

        if (!result.success) {

            throw new Error(result.error || 'Import thất bại');
        }

        showImportResult(result);

        showToast('✅ Import Excel thành công!');

    }
    catch (err) {

        console.error(err);

        showToast(err.message || 'Lỗi import Excel!', 'error');
    }
    finally {

        document.getElementById('importLoading').style.display = 'none';
    }
}

// ===============================
// SHOW IMPORT RESULT
// ===============================

function showImportResult(result) {

    const div = document.getElementById('importResult');

    div.style.display = 'block';

    const details = result.details || {};

    let html = `
        <div style="
            background:#f0fff4;
            border:1px solid #4CAF50;
            border-radius:12px;
            padding:1.5rem;
        ">
            <h3 style="color:#2E7D32;margin-bottom:1rem">
                ✅ Import hoàn tất
            </h3>

            <p style="margin-bottom:1rem">
                ${result.message}
            </p>
    `;

    Object.keys(details).forEach(key => {

        const item = details[key];

        html += `
            <div style="
                background:#fff;
                border-radius:8px;
                padding:1rem;
                margin-bottom:1rem;
                border:1px solid #ddd;
            ">
                <h4 style="margin-bottom:.5rem;color:#1565C0">
                    ${key.toUpperCase()}
                </h4>

                <p>✅ Thành công: <strong>${item.success || 0}</strong></p>

                <p>❌ Lỗi: <strong>${item.errors || 0}</strong></p>
        `;

        if (item.error_list && item.error_list.length > 0) {

            html += `<ul style="margin-top:.5rem;color:#c62828">`;

            item.error_list.forEach(err => {

                html += `<li>${err}</li>`;
            });

            html += `</ul>`;
        }

        html += `</div>`;
    });

    html += `</div>`;

    div.innerHTML = html;
}