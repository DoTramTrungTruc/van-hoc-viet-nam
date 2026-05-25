/**
 * TAC-PHAM.JS
 */

let currentPage = 1;
const itemsPerPage = 6;

let originalTacPham = [];
let filteredTacPham = [];

document.addEventListener('DOMContentLoaded', () => {
    loadAllTacPham();
    loadTheLoaiFilter();

    const searchInput = document.getElementById('searchInput');

    if (searchInput) {
        searchInput.addEventListener('keypress', e => {
            if (e.key === 'Enter') {
                searchTacPham();
            }
        });
    }
});

/* =========================
   LOAD DATA
========================= */

async function loadAllTacPham() {

    const loading = document.getElementById('loading');

    try {

        const response = await fetch('/api/tac-pham');
        const data = await response.json();

        if (data.success && data.data) {

            originalTacPham = data.data;
            filteredTacPham = [...originalTacPham];

            loadGiaiDoanFilter(originalTacPham);

            displayPage(1);

            document.getElementById('totalCount').textContent =
                filteredTacPham.length;

            loading.style.display = 'none';

        } else {

            loading.innerHTML = `
                <div class="empty-state">
                    Không có dữ liệu
                </div>
            `;
        }

    } catch (error) {

        console.error(error);

        loading.innerHTML = `
            <div class="empty-state">
                Lỗi tải dữ liệu
            </div>
        `;
    }
}

/* =========================
   DISPLAY
========================= */

function displayPage(page = 1) {

    currentPage = page;

    const worksGrid = document.getElementById('worksGrid');

    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;

    const pageData = filteredTacPham.slice(start, end);

    const totalPages =
        Math.ceil(filteredTacPham.length / itemsPerPage);

    worksGrid.innerHTML = `
        <div class="works-grid-content">
            ${renderWorks(pageData)}
        </div>

        ${createPagination(page, totalPages)}
    `;

    document.getElementById('totalCount').textContent =
        filteredTacPham.length;
}

function renderWorks(works) {

    if (!works.length) {
        return `
            <div class="empty-state">
                Không tìm thấy tác phẩm
            </div>
        `;
    }

    return works.map(tp => {

        const theLoai = Array.isArray(tp.the_loai)
            ? tp.the_loai.join(', ')
            : (tp.the_loai || 'Chưa phân loại');

        const tacGia = Array.isArray(tp.tac_gia)
            ? tp.tac_gia.join(', ')
            : (tp.tac_gia || 'Chưa rõ');

        return `
            <div class="work-card">

                <div class="work-cover">
                    <img
                        src="${tp.anh_dai_dien || '/static/images/default_cover.jpg'}"
                        alt="${escapeHtml(tp.ten)}"
                    >
                </div>

                <div class="work-content">

                    <h3 class="work-title">
                        <a href="/tac-pham/${encodeURIComponent(tp.ten)}">
                            ${escapeHtml(tp.ten)}
                        </a>
                    </h3>

                    <div class="work-meta">

                        <div class="work-meta-item">
                            <strong>Tác giả:</strong>
                            ${escapeHtml(tacGia)}
                        </div>

                        ${tp.nam_sang_tac ? `
                            <div class="work-meta-item">
                                <strong>Năm:</strong>
                                ${tp.nam_sang_tac}
                            </div>
                        ` : ''}

                        ${tp.giai_doan ? `
                            <div class="work-meta-item">
                                <strong>Giai đoạn:</strong>
                                ${escapeHtml(tp.giai_doan)}
                            </div>
                        ` : ''}

                        <div class="work-genre">
                            ${escapeHtml(theLoai)}
                        </div>

                    </div>

                    ${tp.noi_dung_tom_tat ? `
                        <div class="work-summary">
                            ${escapeHtml(tp.noi_dung_tom_tat)}
                        </div>
                    ` : ''}

                    <a
                        href="/tac-pham/${encodeURIComponent(tp.ten)}"
                        class="work-btn"
                    >
                        Xem chi tiết →
                    </a>

                </div>

            </div>
        `;

    }).join('');
}

/* =========================
   PAGINATION
========================= */

function createPagination(current, total) {

    if (total <= 1) return '';

    let html = `<div class="pagination">`;

    if (current > 1) {
        html += `
            <button class="page-btn"
                onclick="displayPage(${current - 1})">
                ‹
            </button>
        `;
    }

    for (let i = 1; i <= total; i++) {

        html += `
            <button
                class="page-btn ${i === current ? 'active' : ''}"
                onclick="displayPage(${i})"
            >
                ${i}
            </button>
        `;
    }

    if (current < total) {
        html += `
            <button class="page-btn"
                onclick="displayPage(${current + 1})">
                ›
            </button>
        `;
    }

    html += `</div>`;

    return html;
}

/* =========================
   FILTER
========================= */

function applyFilters() {

    const theLoai =
        document.getElementById('theLoaiFilter').value;

    const giaiDoan =
        document.getElementById('giaiDoanFilter').value;

    filteredTacPham = originalTacPham.filter(tp => {

        let ok = true;

        if (theLoai) {

            if (Array.isArray(tp.the_loai)) {
                ok = tp.the_loai.includes(theLoai);
            } else {
                ok = tp.the_loai === theLoai;
            }
        }

        if (ok && giaiDoan) {
            ok = tp.giai_doan === giaiDoan;
        }

        return ok;
    });

    sortWorks(false);

    displayPage(1);
}

function filterByTheLoai() {
    applyFilters();
}

function filterByGiaiDoan() {
    applyFilters();
}

/* =========================
   SORT
========================= */

function sortWorks(render = true) {

    const sort =
        document.getElementById('sortFilter').value;

    filteredTacPham.sort((a, b) => {

        switch (sort) {

            case 'name-desc':
                return b.ten.localeCompare(a.ten, 'vi');

            case 'year-asc':
                return (a.nam_sang_tac || 0)
                    - (b.nam_sang_tac || 0);

            case 'year-desc':
                return (b.nam_sang_tac || 0)
                    - (a.nam_sang_tac || 0);

            default:
                return a.ten.localeCompare(b.ten, 'vi');
        }
    });

    if (render) {
        displayPage(1);
    }
}

/* =========================
   SEARCH
========================= */

function searchTacPham() {

    const keyword =
        document.getElementById('searchInput')
        .value
        .trim()
        .toLowerCase();

    if (!keyword) {

        filteredTacPham = [...originalTacPham];
        displayPage(1);

        return;
    }

    filteredTacPham = originalTacPham.filter(tp => {

        return (
            tp.ten?.toLowerCase().includes(keyword) ||
            tp.tac_gia?.toString().toLowerCase().includes(keyword)
        );
    });

    displayPage(1);
}

/* =========================
   RESET
========================= */

function showAllTacPham() {

    document.getElementById('searchInput').value = '';
    document.getElementById('theLoaiFilter').value = '';
    document.getElementById('giaiDoanFilter').value = '';
    document.getElementById('sortFilter').value = 'name-asc';

    filteredTacPham = [...originalTacPham];

    displayPage(1);
}

/* =========================
   LOAD FILTERS
========================= */

async function loadTheLoaiFilter() {

    try {

        const response = await fetch('/api/the-loai');
        const data = await response.json();

        if (data.success && data.data) {

            const select =
                document.getElementById('theLoaiFilter');

            data.data.forEach(tl => {

                const option =
                    document.createElement('option');

                option.value = tl.ten;
                option.textContent = tl.ten;

                select.appendChild(option);
            });
        }

    } catch (error) {
        console.error(error);
    }
}

function loadGiaiDoanFilter(data) {

    const select =
        document.getElementById('giaiDoanFilter');

    const set = new Set();

    data.forEach(tp => {
        if (tp.giai_doan) {
            set.add(tp.giai_doan);
        }
    });

    [...set].sort().forEach(gd => {

        const option =
            document.createElement('option');

        option.value = gd;
        option.textContent = gd;

        select.appendChild(option);
    });
}

/* =========================
   ESCAPE HTML
========================= */

function escapeHtml(text) {

    if (!text) return '';

    const div = document.createElement('div');

    div.textContent = text;

    return div.innerHTML;
}