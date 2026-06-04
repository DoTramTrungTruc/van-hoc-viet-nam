/**
 * TAC-PHAM-DETAIL.JS - Chi tiết Tác Phẩm
 * Giữ nguyên logic, chỉ cập nhật DOM theo design mới
 */
let allTacPham = [];
let tacPhamData = null;
const tenTacPham = decodeURIComponent(window.location.pathname.split('/').pop());

document.addEventListener('DOMContentLoaded', function() {
    loadTacPhamDetail();
    loadCompareList();
});

async function loadTacPhamDetail() {
    try {

        const response = await fetch(`/api/tac-pham/${encodeURIComponent(tenTacPham)}`);
        const data = await response.json();

        if (!data.success) {

            showError(`Không tìm thấy tác phẩm: ${tenTacPham}`);
            return;
        }

        const tp = data.data;

        // ===== GÁN GLOBAL =====
        tacPhamData = tp;

        // Hiển thị thông tin
        displayTacPhamInfo(tp);

        // Vẽ đồ thị
        drawGraph(tp);
        initCompareCurrent(tp);
        // Show content, hide loading
        document.getElementById('loading').style.display = 'none';
        document.getElementById('content').style.display = 'block';

    } catch (error) {

        console.error('Lỗi:', error);
        showError(`Lỗi khi tải dữ liệu: ${error.message}`);
    }

    initQuiz();
    await loadFavoriteState();
}

function formatLiteraryText(text) {
    if (!text) return '';

    return text
        .split('\n')
        .filter(p => p.trim() !== '')
        .map(p => `<p>${escapeHtml(p)}</p>`)
        .join('');
}
function displayTacPhamInfo(tp) {
    
    currentTacPhamData = tp;
    // Breadcrumb & Title
    document.getElementById('breadcrumbTitle').textContent = tp.ten;
    document.getElementById('tacPhamTitle').textContent = tp.ten;
    document.title = `${tp.ten} - Văn Học Việt Nam`;
    const imgElement = document.getElementById('tacPhamImage');
    if (imgElement) {
        imgElement.src = tp.anh_dai_dien || '/static/images/default_cover.jpg';
        imgElement.alt = `Bìa ${tp.ten}`;
    }
    // Meta cards
    document.getElementById('tacGia').textContent = tp.tac_gia || 'N/A';
    document.getElementById('namSangTac').textContent = tp.nam_sang_tac || 'N/A';
    document.getElementById('theLoai').textContent = tp.the_loai ? tp.the_loai.join(', ') : 'N/A';
    document.getElementById('namXuatBan').textContent = tp.nam_xuat_ban || 'N/A';
    document.getElementById('giaiDoan').textContent =
    tp.giai_doan && tp.giai_doan.length > 0 ? tp.giai_doan.join(', ') : 'N/A';
    // Nội dung tóm tắt
    document.getElementById('noiDung').innerHTML =
    formatLiteraryText(tp.noi_dung_tom_tat || 'Chưa có thông tin');
    // Trích đoạn
    if (tp.trich_doan && tp.trich_doan.length > 0) {
        document.getElementById('trichDoanSection').style.display = 'block';
    
        const container = document.getElementById('trichDoanList');
    
        container.innerHTML = tp.trich_doan.map(td => {

            const isPoem =
                td.includes('\n') &&
                td.split('\n').length >= 3;
        
            return `
                <div class="${isPoem ? 'poem poem-center' : 'literary-quote'}">
                    ${td}
                </div>
            `;
        }).join('');
    }
    // Hoàn cảnh
    if (tp.hoan_canh) {
        document.getElementById('hoanCanhSection').style.display = 'block';
        document.getElementById('hoanCanh').textContent = tp.hoan_canh;
    }
    
    // Chủ đề (hiển thị dạng tags)
    if (tp.chu_de && tp.chu_de.length > 0) {
        document.getElementById('chuDeSection').style.display = 'block';
        const chuDeContainer = document.getElementById('chuDe');
        chuDeContainer.innerHTML = tp.chu_de
            .map(cd => `<span class="tag">${cd}</span>`)
            .join('');
    }
    
    // Ý nghĩa
    if (tp.y_nghia) {
        document.getElementById('yNghiaSection').style.display = 'block';
        document.getElementById('yNghia').textContent = tp.y_nghia;
    }
    
    // Giá trị nghệ thuật
    if (tp.gia_tri_nghe_thuat) {
        document.getElementById('giaTriSection').style.display = 'block';
        document.getElementById('giaTriNgheThuat').textContent = tp.gia_tri_nghe_thuat;
    }
    
    // Nhân vật
    displayCharacters(tp.nhan_vat);
}

function displayCharacters(nhanVat) {
    if (!nhanVat || nhanVat.length === 0) {
        document.getElementById('nhanVatSection').style.display = 'none';
        return;
    }
    
    const nhanVatGrid = document.getElementById('nhanVatGrid');
    const validCharacters = nhanVat.filter(nv => nv.ten);
    
    if (validCharacters.length === 0) {
        document.getElementById('nhanVatSection').style.display = 'none';
        return;
    }
    
    nhanVatGrid.innerHTML = validCharacters.map(nv => `
        <div class="character-card">
            <h4>${escapeHtml(nv.ten)}</h4>
            <div class="role">${escapeHtml(nv.vai_tro) || 'N/A'}</div>
            <p><strong>Tính cách:</strong> ${escapeHtml(nv.tinh_cach) || 'Chưa có thông tin'}</p>
        </div>
    `).join('');
}

function drawGraph(tacPham) {
    const nodes = [];
    const edges = [];
    const nodeCache = new Map();

    function addNode(node) {
        if (!nodeCache.has(node.id)) {
            nodeCache.set(node.id, true);
            nodes.push(node);
        }
    }

    function addEdge(edge) {
        edges.push(edge);
    }

    // ===== 1. TẠO NODES & EDGES PHÂN CẤP XỊN HƠN =====
    
    // TÁC PHẨM (Gốc trung tâm)
    addNode({
        id: 'tacpham',
        label: `📚 ${tacPham.ten}`,
        group: 'tacpham',
        size: 40,
        font: { size: 16, bold: true },
        title: (() => {
            const container = document.createElement('div');
            container.style.padding = '4px';
            container.innerHTML = `<b>📚 Tác phẩm Trung Tâm</b><br>${tacPham.ten}`;
            return container;
        })()
    });

    // TÁC GIẢ
    if (tacPham.tac_gia) {
        const tgId = 'tacgia_' + tacPham.tac_gia;
        addNode({
            id: tgId,
            label: `✍️ ${tacPham.tac_gia}`,
            group: 'tacgia',
            size: 30,
            font: { size: 14, bold: true }
        });

        addEdge({
            from: tgId,
            to: 'tacpham',
            label: 'sáng tác',
            arrows: 'to',
            width: 3,
            color: { color: '#607D8B', highlight: '#2196F3' }
        });
    }

    // NHÂN VẬT
    if (tacPham.nhan_vat) {
        tacPham.nhan_vat.forEach(nv => {
            if (!nv.ten) return;

            const id = 'nv_' + nv.ten;
            const isMain = nv.vai_tro && nv.vai_tro.toLowerCase().includes('chính');

            addNode({
                id,
                label: `👤 ${nv.ten}`,
                group: 'nhanvat',
                size: isMain ? 28 : 20,
                borderWidth: isMain ? 3 : 1,
                font: { size: isMain ? 13 : 11, color: isMain ? '#000' : '#555' },
                title: (() => {
                    const container = document.createElement('div');
                    container.style.padding = '4px';
                    container.innerHTML = `
                        <b style="color: #E74C3C;">👤 Nhân vật: ${nv.ten}</b><br>
                        <b>Vai trò:</b> ${nv.vai_tro || 'N/A'}<br>
                        <b>Tính cách:</b> ${nv.tinh_cach || 'Chưa rõ'}`
                    ;
                    return container; // Trả về DOM Element thay vì chuỗi thuần
                })()
             });

             const vaiTroText = nv.vai_tro || 'nhân vật';

             const shortRole =
                 vaiTroText.length > 28
                     ? vaiTroText.substring(0, 28) + '...'
                     : vaiTroText;
             
             addEdge({
                 from: 'tacpham',
                 to: id,
             
                 label: shortRole,
                 title: vaiTroText,
             
                 width: isMain ? 2.5 : 1.5,
             
                 color: {
                     color: isMain ? '#E74C3C' : '#95A5A6'
                 },
             
                 font: {
                     size: 10,
                     strokeWidth: 0,
                     multi: false,
                     align: 'middle'
                 },
             
                 smooth: {
                     type: 'curvedCW',
                     roundness: 0.2
                 },
             
                 length: isMain ? 160 : 180
             });
        });
    }

    // THỂ LOẠI
    if (tacPham.the_loai) {
        tacPham.the_loai.forEach(tl => {
            const ten = typeof tl === 'string' ? tl : tl.ten;
            const id = 'tl_' + ten;

            addNode({
                id,
                label: `🎭 ${ten}`,
                group: 'theloai',
                size: 20
            });

            addEdge({
                from: 'tacpham',
                to: id,
                label: 'thể loại',
                arrows: 'to',
                dashes: [4, 4],
                color: { color: '#27AE60' }
            });
        });
    }

    // CHỦ ĐỀ
    if (tacPham.chu_de) {
        tacPham.chu_de.forEach(cd => {
            const ten = typeof cd === 'string' ? cd : cd.ten;
            const id = 'cd_' + ten;

            addNode({
                id,
                label: `🏷️ ${ten}`,
                group: 'chude',
                size: 18
            });

            addEdge({
                from: 'tacpham',
                to: id,
                label: 'chủ đề',
                dashes: true,
                color: { color: '#F39C12' }
            });
        });
    }
    // NĂM SÁNG TÁC
    if (tacPham.nam_sang_tac) {
        const namId = 'nam_' + tacPham.nam_sang_tac;

        addNode({
            id: namId,
            label: `📅 ${tacPham.nam_sang_tac}`,
            group: 'namsangtac',
            size: 18,
            font: { size: 12, bold: true }
        });

        addEdge({
            from: 'tacpham',
            to: namId,
            label: 'năm sáng tác',
            arrows: 'to',
            color: { color: '#9B59B6' },
            dashes: [6, 3]
        });
    }

    // GIAI ĐOẠN
    if (tacPham.giai_doan) {
        const gdId = 'giaidoan_' + tacPham.giai_doan;

        addNode({
            id: gdId,
            label: `🏛️ ${tacPham.giai_doan}`,
            group: 'giaidoan',
            size: 20,
            font: { size: 12, bold: true }
        });

        addEdge({
            from: 'tacpham',
            to: gdId,
            label: 'giai đoạn',
            arrows: 'to',
            color: { color: '#8E44AD' },
            width: 2
        });
    }
    // ===== 2. ĐỊNH DẠNG CẤU HÌNH UI VIS.JS CHUYÊN NGHIỆP =====
    const nodeCount = nodes.length;
    const physicsStrength = nodeCount < 10 ? -3500 : nodeCount < 20 ? -2000 : -1200;

    const options = {
        nodes: {
            shape: 'box', // Chuyển sang dạng thẻ 'box' bo góc nhìn hiện đại và dễ đọc text hơn 'dot'
            margin: { top: 8, bottom: 8, left: 12, right: 12 },
            shapeProperties: { borderRadius: 6 },
            font: {
                face: 'Segoe UI, Roboto, Helvetica, Arial, sans-serif',
                align: 'center'
            },
            shadow: { enabled: true, color: 'rgba(0,0,0,0.1)', size: 4, x: 2, y: 2 }
        },
        edges: {
            font: {
                size: 10,
                align: 'middle',
                background: '#ffffff',
                color: '#666666'
            },
            smooth: {
                type: 'cubicBezier', // Đổi sang đường cong mượt mềm mại kiểu sơ đồ tư duy
                forceDirection: 'none',
                roundness: 0.5
            }
        },
        groups: {
            tacpham: { color: { background: '#FFF9E6', border: '#D4AC0D', highlight: { background: '#FFF1C5', border: '#B7950B' } } },
            tacgia: { color: { background: '#EBF5FB', border: '#2980B9', highlight: { background: '#D4E6F1', border: '#21618C' } } },
            nhanvat: { color: { background: '#FDEDEC', border: '#E74C3C', highlight: { background: '#FADBD8', border: '#C0392B' } } },
            theloai: { color: { background: '#E8F8F5', border: '#1ABC9C', highlight: { background: '#D1F2EB', border: '#16A085' } } },
            chude: { color: { background: '#FEF9E7', border: '#F39C12', highlight: { background: '#FCF3CF', border: '#D35400' } } },
            namsangtac: {
                color: {
                    background: '#F5EEF8',
                    border: '#9B59B6',
                    highlight: {
                        background: '#EBDEF0',
                        border: '#7D3C98'
                    }
                }
            },

            giaidoan: {
                color: {
                    background: '#E8DAEF',
                    border: '#8E44AD',
                    highlight: {
                        background: '#D2B4DE',
                        border: '#6C3483'
                    }
                }
            }
        },
        physics: {
            enabled: true,
            solver: 'barnesHut',
        
            barnesHut: {
                gravitationalConstant: -2500,
                centralGravity: 0.2,
                springLength: 140,
                springConstant: 0.03,
                damping: 0.35,
                avoidOverlap: 1
            },
        
            stabilization: {
                enabled: true,
                iterations: 200,
                updateInterval: 25
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            navigationButtons: true,
            keyboard: true
        }
    };

    const container = document.getElementById('network');
    // Khởi tạo DataSet để có thể cập nhật trạng thái động (cho tính năng highlight)
    const nodesDataSet = new vis.DataSet(nodes);
    const edgesDataSet = new vis.DataSet(edges);
    const network = new vis.Network(
        container,
        { nodes: nodesDataSet, edges: edgesDataSet },
        options
    );
    
    network.once("stabilizationIterationsDone", function () {
        network.setOptions({
            physics: false
        });
    });

    // ===== 3. HIỆU ỨNG TỰ ĐỘNG HIGHLIGHT KHI CLICK =====
    let allNodes = nodesDataSet.get({ returnType: "Object" });
    let allEdges = edgesDataSet.get({ returnType: "Object" });
    let isHighlighted = false;

    network.on("click", function (params) {
        if (params.nodes.length > 0) {
            isHighlighted = true;
            const selectedNode = params.nodes[0];

            // Tìm toàn bộ các node có kết nối trực tiếp với node được chọn
            const connectedNodes = network.getConnectedNodes(selectedNode);

            // Làm mờ toàn bộ các node không liên quan
            for (let nodeId in allNodes) {
                allNodes[nodeId].color = {
                    background: 'rgba(240, 240, 240, 0.4)',
                    border: 'rgba(200, 200, 200, 0.4)'
                };
                allNodes[nodeId].font = { color: 'rgba(150, 150, 150, 0.4)' };
            }

            // Khôi phục màu đậm rõ nét cho node gốc và các node liên kết trực tiếp
            connectedNodes.forEach(nodeId => {
                allNodes[nodeId].color = undefined; // reset về màu mặc định của group
                allNodes[nodeId].font = { color: '#000000' };
            });
            allNodes[selectedNode].color = undefined;
            allNodes[selectedNode].font = { color: '#000000', bold: true };

            // Cập nhật lại đồ thị
            const updateArray = [];
            for (let nodeId in allNodes) { updateArray.push(allNodes[nodeId]); }
            nodesDataSet.update(updateArray);

            // Điều hướng xử lý logic nếu click vào Tác giả hoặc mở Popup
            if (selectedNode.startsWith('tacgia_')) {
                const ten = selectedNode.replace('tacgia_', '');
                window.location.href = `/tac-gia/${encodeURIComponent(ten)}`;
                return;
            }
            showNodePopup(selectedNode, tacPham);

        } else if (isHighlighted) {
            // Nếu click ra khoảng trống: Reset đồ thị về trạng thái ban đầu
            isHighlighted = false;
            for (let nodeId in allNodes) {
                allNodes[nodeId].color = undefined;
                allNodes[nodeId].font = undefined;
            }
            const updateArray = [];
            for (let nodeId in allNodes) { updateArray.push(allNodes[nodeId]); }
            nodesDataSet.update(updateArray);
        }
    });

    // ===== 4. HIỆU ỨNG CON TRỎ CHUỘT =====
    network.on("hoverNode", function () {
        network.body.container.style.cursor = 'pointer';
    });

    network.on("blurNode", function () {
        network.body.container.style.cursor = 'default';
    });
}

function showError(message) {
    const loading = document.getElementById('loading');
    loading.innerHTML = `
        <div class="loading-content">
            <div style="font-size: 3rem; margin-bottom: 20px;">❌</div>
            <p style="color: #fff; font-size: 1.2rem;">${message}</p>
            <a href="/tac-pham" style="
                display: inline-block;
                margin-top: 20px;
                padding: 12px 30px;
                background: #fff;
                color: #8B4513;
                text-decoration: none;
                border-radius: 25px;
                font-weight: 600;
            ">← Quay lại danh sách</a>
        </div>
    `;
}
function showNodePopup(nodeId, tacPham) {
    const popup = document.getElementById('graphPopup');
    let html = '';

    // ===== NHÂN VẬT =====
    if (nodeId.startsWith('nv_')) {
    const ten = nodeId.replace('nv_', '');
    const nv = tacPham.nhan_vat.find(n => n.ten === ten);

    if (!nv) return;

    html = `
        <h3>${nv.ten}</h3>

        <p><b>Vai trò:</b> ${nv.vai_tro || 'N/A'}</p>
        <p><b>Tính cách:</b> ${nv.tinh_cach || 'Chưa có'}</p>

        ${nv.so_phan ? `<p><b>Số phận:</b> ${nv.so_phan}</p>` : ''}
        ${nv.y_nghia_dien_hinh ? `<p><b>Ý nghĩa:</b> ${nv.y_nghia_dien_hinh}</p>` : ''}

         
    `;
}
     
    // ===== TÁC GIẢ =====
    else if (nodeId.startsWith('tacgia_')) {
        const ten = nodeId.replace('tacgia_', '');
    
        popup.innerHTML = `<p>Đang tải...</p>`;
        popup.style.display = 'block';
    
        fetch(`/api/tac-gia/${encodeURIComponent(ten)}`)
            .then(res => res.json())
            .then(data => {
                if (!data.success) return;
    
                const tg = data.data;
    
                popup.innerHTML = `
                    <h3>👤 ${tg.ten}</h3>
    
                    <p><b>Năm sinh:</b> ${tg.nam_sinh || 'N/A'}</p>
                    <p><b>Năm mất:</b> ${tg.nam_mat || 'N/A'}</p>
                    <p><b>Quê quán:</b> ${tg.que_quan || 'N/A'}</p>
                    <p><b>Trường phái:</b> ${tg.truong_phai || 'N/A'}</p>
     
                `;
            });
    }
    
    // ===== TÁC PHẨM =====
    else if (nodeId === 'tacpham') {
        html = `
            <h3>${tacPham.ten}</h3>
            <p><b>Tác giả:</b> ${tacPham.tac_gia}</p>
            <button onclick="goToTacPham('${tacPham.ten}')">Xem chi tiết</button>
        `;
    }

    popup.innerHTML = html;
    popup.style.display = 'block';
}
function goToNhanVat(ten) {
    window.location.href = `/nhan-vat/${encodeURIComponent(ten)}`;
}

function goToTacGia(ten) {
    window.location.href = `/tac-gia/${encodeURIComponent(ten)}`;
}

function goToTacPham(ten) {
    window.location.href = `/tac-pham/${encodeURIComponent(ten)}`;
}
document.addEventListener('click', function(e) {
    const popup = document.getElementById('graphPopup');
    if (!e.target.closest('#network') && !e.target.closest('#graphPopup')) {
        popup.style.display = 'none';
    }
});
// ===== CHATBOT FUNCTIONALITY =====
let currentTacPhamData = null;

// Save tác phẩm data khi load
function saveTacPhamData(tp) {
    currentTacPhamData = tp;
}

// Handle chat input
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    
    if (chatSend) {
        chatSend.addEventListener('click', sendMessage);
    }
    
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});

// ===== CHATGPT VERSION =====
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    addMessage(message, 'user');
    input.value = '';

    showTyping();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: message,
                tac_pham: currentTacPhamData?.ten
            })
        });

        const data = await response.json();

        hideTyping();

        if (data.success) {
            addMessage(data.answer, 'bot', data.graph_data || null);
        } else {
            addMessage(data.answer || "Không tìm được câu trả lời.", 'bot');
        }

    } catch (err) {
        console.error('Chat error:', err);
        hideTyping();
        
        // Fallback to local processing
        const response = processQuestion(message);
        addMessage(response, 'bot');
    }
}
function renderMiniGraph(containerId, graphData) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Dùng lại groups/màu từ drawGraph gốc
    const options = {
        nodes: {
            shape:  'box',
            margin: { top: 6, bottom: 6, left: 10, right: 10 },
            shapeProperties: { borderRadius: 5 },
            font:   { size: 11, face: 'Segoe UI', color: '#333' },
            shadow: { enabled: true, color: 'rgba(0,0,0,0.08)', size: 3, x: 1, y: 1 },
        },
        edges: {
            font:   { size: 9, align: 'middle', background: '#fff', color: '#666' },
            smooth: { type: 'curvedCW', roundness: 0.2 },
            width:  1.2,
            arrows: { to: { enabled: true, scaleFactor: 0.6 } },
        },
        groups: {
            TacGia:   { color: { background: '#EBF5FB', border: '#2980B9' } },
            TacPham:  { color: { background: '#FFF9E6', border: '#D4AC0D' } },
            NhanVat:  { color: { background: '#FDEDEC', border: '#E74C3C' } },
            TheLoai:  { color: { background: '#E8F8F5', border: '#1ABC9C' } },
            GiaiDoan: { color: { background: '#E8DAEF', border: '#8E44AD' } },
        },
        physics: {
            enabled: true,
            solver:  'barnesHut',
            barnesHut: {
                gravitationalConstant: -1500,
                centralGravity:        0.3,
                springLength:          100,
                springConstant:        0.04,
                damping:               0.4,
                avoidOverlap:          1,
            },
            stabilization: { enabled: true, iterations: 100 },
        },
        interaction: {
            hover:             true,
            tooltipDelay:      150,
            navigationButtons: false,   // ← không cần nút điều hướng ở mini
            keyboard:          false,
            zoomView:          true,
            dragNodes:         true,
        },
    };

    // Map group từ server sang group của Vis.js
    const nodes = new vis.DataSet(
        graphData.nodes.map(n => ({
            id:    n.id,
            label: n.label,
            group: n.group,   // TacGia / TacPham / NhanVat / TheLoai / GiaiDoan
            title: n.title,
            // Highlight node liên quan
            borderWidth: n.highlighted ? 3 : 1,
            shadow: n.highlighted
                ? { enabled: true, color: '#D4AC0D', size: 8 }
                : { enabled: false },
        }))
    );

    const edges = new vis.DataSet(graphData.edges);

    let miniNetwork = null;
    try {
        miniNetwork = new vis.Network(
            container,
            { nodes, edges },
            options
        );

        miniNetwork.once('stabilizationIterationsDone', () => {
            miniNetwork.setOptions({ physics: false });
            miniNetwork.fit({ animation: { duration: 400 } });
        });

        // Click vào node trong mini graph → hiện tooltip nhỏ
        miniNetwork.on('click', params => {
            if (params.nodes.length > 0) {
                const node = nodes.get(params.nodes[0]);
                if (node?.title) {
                    // Hiện title ngay tại vị trí click
                    const tip = document.createElement('div');
                    tip.className   = 'mini-graph-tip';
                    tip.innerHTML   = typeof node.title === 'string'
                        ? node.title.replace(/\n/g, '<br>')
                        : node.label;
                    container.appendChild(tip);
                    setTimeout(() => tip.remove(), 3000);
                }
            }
        });
    } catch (err) {
        console.warn('Mini graph render error:', err);
    }
}
function formatAIResponse(text) {

    return text
        // xuống dòng
        .replace(/\n/g, "<br>")

        // tiêu đề ##
        .replace(/## (.*?)(<br>|$)/g,
            '<h3 class="ai-title">$1</h3>')

        // tiêu đề #
        .replace(/# (.*?)(<br>|$)/g,
            '<h2 class="ai-big-title">$1</h2>')

        // in đậm
        .replace(/\*\*(.*?)\*\*/g,
            '<strong>$1</strong>')

        // bullet
        .replace(/- (.*?)(<br>|$)/g,
            '<li>$1</li>');
}

function addMessage(text, sender,graphData = null ) {

    const messagesDiv = document.getElementById('chatMessages');

    const messageDiv = document.createElement('div');

    messageDiv.className = `chat-message ${sender}-message`;

    const icon = sender === 'bot'
        ? '🤖'
        : '👤';

    // format AI
    const formattedText =
        sender === 'bot'
            ? formatAIResponse(text)
            : text;
            const graphId = 'mini-graph-' + Date.now();

            // ✅ Nếu là bot và có graph_data → thêm khung mini graph
            const graphHTML = (sender === 'bot' && graphData && graphData.nodes?.length > 0)
                ? `<div class="mini-graph-wrapper">
                       <div class="mini-graph-label">🔗 Knowledge Graph liên quan</div>
                       <div id="${graphId}" class="mini-graph-container"></div>
                   </div>`
                : '';
    messageDiv.innerHTML = `
        <div class="message-icon">${icon}</div>

        <div class="message-content">
            ${formattedText}
            ${graphHTML}
        </div>
    `;

    messagesDiv.appendChild(messageDiv);

    messagesDiv.scrollTop =
        messagesDiv.scrollHeight;
    if (sender === 'bot' && graphData && graphData.nodes?.length > 0) {
            setTimeout(() => renderMiniGraph(graphId, graphData), 100);
    }
}

function showTyping() {
    const messagesDiv = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'chat-message bot-message';
    typingDiv.innerHTML = `
        <div class="message-icon">🤖</div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    messagesDiv.appendChild(typingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function hideTyping() {
    const typing = document.getElementById('typingIndicator');
    if (typing) typing.remove();
}

function processQuestion(question) {
    if (!currentTacPhamData) return "Chưa load được thông tin tác phẩm.";
    
    const q = question.toLowerCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '') // Bỏ dấu
        .trim();
    const tp = currentTacPhamData;
    
    // ===== NHÂN VẬT =====
    if (q.match(/nhan vat|nguoi|ai|characters?/)) {
        // Nhân vật chính
        if (q.match(/chinh|main|chu chot/)) {
            const mainChars = tp.nhan_vat?.filter(nv => 
                nv.vai_tro && nv.vai_tro.toLowerCase().includes('chính')
            ) || [];
            if (mainChars.length > 0) {
                return `Nhân vật chính: ${mainChars.map(nv => nv.ten).join(', ')}`;
            }
        }
        
        // Số lượng nhân vật
        if (q.match(/bao nhieu|may|so luong|count/)) {
            return tp.nhan_vat 
                ? `Tác phẩm có ${tp.nhan_vat.length} nhân vật.`
                : "Chưa có thông tin về nhân vật.";
        }
        
        // Tính cách nhân vật cụ thể
        const nameMatch = q.match(/tinh cach|tinh chat|the nao|nhu the nao/);
        if (nameMatch && tp.nhan_vat) {
            for (let nv of tp.nhan_vat) {
                if (q.includes(nv.ten.toLowerCase())) {
                    return `${nv.ten} có tính cách: ${nv.tinh_cach || 'chưa rõ'}`;
                }
            }
        }
        
        // Vai trò
        if (q.match(/vai tro|vai|role/)) {
            if (tp.nhan_vat && tp.nhan_vat.length > 0) {
                const roles = tp.nhan_vat.map(nv => 
                    `${nv.ten}: ${nv.vai_tro || 'N/A'}`
                ).join('\n- ');
                return `Vai trò các nhân vật:\n- ${roles}`;
            }
        }
        
        // Số phận
        if (q.match(/so phan|ket cuc|ending|cuoi cung/)) {
            if (tp.nhan_vat && tp.nhan_vat.length > 0) {
                const withFate = tp.nhan_vat.filter(nv => nv.so_phan);
                if (withFate.length > 0) {
                    return withFate.map(nv => 
                        `${nv.ten}: ${nv.so_phan}`
                    ).join('\n\n');
                }
            }
        }
        
        // Danh sách tất cả
        if (tp.nhan_vat && tp.nhan_vat.length > 0) {
            const names = tp.nhan_vat.map(nv => nv.ten).join(', ');
            return `Các nhân vật trong tác phẩm: ${names}`;
        }
        return "Chưa có thông tin về nhân vật.";
    }
    
    // ===== TÁC GIẢ =====
    if (q.match(/tac gia|author|nguoi viet|ai viet|ai sang tac/)) {
        let response = `Tác giả của "${tp.ten}" là ${tp.tac_gia || 'chưa rõ'}.`;
        
        // Nếu hỏi thêm về tác giả
        if (q.match(/la ai|gioi thieu|thong tin/)) {
            // Có thể fetch thêm info tác giả ở đây
            response += ` Bạn có thể xem thêm thông tin tác giả ở trang Tác giả.`;
        }
        
        return response;
    }
    
    // ===== NĂM THÁNG =====
    if (q.match(/nam|year|thoi gian|khi nao|when/)) {
        // Năm xuất bản
        if (q.match(/xuat ban|phat hanh|publish|ra mat/)) {
            return tp.nam_xuat_ban 
                ? `Tác phẩm xuất bản năm ${tp.nam_xuat_ban}.`
                : "Chưa có thông tin năm xuất bản.";
        }
        
        // Năm sáng tác
        if (q.match(/sang tac|viet|write|written/)) {
            return tp.nam_sang_tac 
                ? `Tác phẩm được sáng tác năm ${tp.nam_sang_tac}.`
                : "Chưa có thông tin năm sáng tác.";
        }
        
        // Thời gian cách đây
        if (tp.nam_sang_tac) {
            const yearsAgo = new Date().getFullYear() - tp.nam_sang_tac;
            return `Tác phẩm được sáng tác năm ${tp.nam_sang_tac} (cách đây ${yearsAgo} năm)${tp.nam_xuat_ban ? `, xuất bản năm ${tp.nam_xuat_ban}` : ''}.`;
        }
        
        return "Chưa có thông tin về năm tháng.";
    }
    
    // ===== THỂ LOẠI =====
    if (q.match(/the loai|genre|loai|kieu|dang thuc/)) {
        if (tp.the_loai && tp.the_loai.length > 0) {
            const genres = Array.isArray(tp.the_loai) ? tp.the_loai : [tp.the_loai];
            return `"${tp.ten}" thuộc thể loại: ${genres.join(', ')}.`;
        }
        return "Chưa có thông tin thể loại.";
    }
    
    // ===== NỘI DUNG =====
    if (q.match(/noi dung|tom tat|ve gi|ke gi|cau chuyen|plot|story|content/)) {
        if (tp.noi_dung_tom_tat) {
            return `📖 Nội dung tóm tắt:\n\n${tp.noi_dung_tom_tat}`;
        }
        return "Chưa có thông tin tóm tắt nội dung.";
    }
    
    // ===== Ý NGHĨA =====
    if (q.match(/y nghia|thong diep|bai hoc|gia tri|meaning|message|giao duc/)) {
        // Ý nghĩa tác phẩm
        if (q.match(/tac pham|truyen|chuyen/)) {
            if (tp.y_nghia) {
                return `🎯 Ý nghĩa tác phẩm:\n\n${tp.y_nghia}`;
            }
        }
        
        // Ý nghĩa nhân vật
        if (tp.nhan_vat) {
            for (let nv of tp.nhan_vat) {
                if (q.includes(nv.ten.toLowerCase())) {
                    if (nv.y_nghia_dien_hinh) {
                        return `💡 Ý nghĩa của ${nv.ten}:\n\n${nv.y_nghia_dien_hinh}`;
                    }
                }
            }
        }
        
        // Mặc định
        if (tp.y_nghia) {
            return `🎯 Ý nghĩa:\n\n${tp.y_nghia}`;
        }
        
        return "Chưa có thông tin về ý nghĩa.";
    }
    
    // ===== GIÁ TRỊ NGHỆ THUẬT =====
    if (q.match(/gia tri nghe thuat|nghe thuat|artistic|phong cach|style|ky thuat|bieu cam/)) {
        if (tp.gia_tri_nghe_thuat) {
            return `🎨 Giá trị nghệ thuật:\n\n${tp.gia_tri_nghe_thuat}`;
        }
        return "Chưa có thông tin về giá trị nghệ thuật.";
    }
    
    // ===== HOÀN CẢNH SÁNG TÁC =====
    if (q.match(/hoan canh|boi canh|context|background|ly do|tai sao viet/)) {
        if (tp.hoan_canh) {
            return `🌍 Hoàn cảnh sáng tác:\n\n${tp.hoan_canh}`;
        }
        return "Chưa có thông tin về hoàn cảnh sáng tác.";
    }
    
    // ===== CẤU TRÚC =====
    if (q.match(/cau truc|bo cuc|structure|chia|phan|chuong/)) {
        if (tp.cau_truc) {
            return `📐 Cấu trúc tác phẩm:\n\n${tp.cau_truc}`;
        }
        return "Chưa có thông tin về cấu trúc.";
    }
    
    // ===== CHỦ ĐỀ =====
    if (q.match(/chu de|theme|topic|de tai|van de/)) {
        // Chủ đề chính
        if (tp.chu_de_chinh) {
            let response = `💡 Chủ đề chính:\n\n${tp.chu_de_chinh}`;
            
            // Nếu có danh sách chủ đề
            if (tp.chu_de && tp.chu_de.length > 0) {
                const themes = Array.isArray(tp.chu_de) ? tp.chu_de : [tp.chu_de];
                response += `\n\nCác chủ đề: ${themes.join(', ')}`;
            }
            
            return response;
        }
        
        return "Chưa có thông tin về chủ đề.";
    }
    
    // ===== GIAI ĐOẠN =====
    if (q.match(/giai doan|thoi ky|period|epoch/)) {
        if (tp.giai_doan && tp.giai_doan.length > 0) {
            const periods = Array.isArray(tp.giai_doan) ? tp.giai_doan : [tp.giai_doan];
            return `⏳ Tác phẩm thuộc giai đoạn: ${periods.join(', ')}.`;
        }
        return "Chưa có thông tin về giai đoạn văn học.";
    }
    
    // ===== ẢNH BÌA =====
    if (q.match(/anh|bia|cover|hinh/)) {
        if (tp.anh_dai_dien) {
            return `Ảnh bìa tác phẩm được hiển thị ở phần trên. URL: ${tp.anh_dai_dien}`;
        }
        return "Chưa có ảnh bìa.";
    }
    
    // ===== SO SÁNH - TÌM KIẾM PATTERN =====
    if (q.match(/khac nhau|giong nhau|so sanh|compare/)) {
        return "Để so sánh tác phẩm này với tác phẩm khác, hãy truy cập trang danh sách tác phẩm.";
    }
    
    // ===== TÌM KIẾM TÊN NHÂN VẬT CỤ THỂ =====
    if (tp.nhan_vat && tp.nhan_vat.length > 0) {
        for (let nv of tp.nhan_vat) {
            if (q.includes(nv.ten.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''))) {
                let info = `👤 **${nv.ten}**\n\n`;
                
                if (nv.vai_tro) info += `📌 Vai trò: ${nv.vai_tro}\n\n`;
                if (nv.tinh_cach) info += `🎭 Tính cách: ${nv.tinh_cach}\n\n`;
                if (nv.so_phan) info += `📖 Số phận: ${nv.so_phan}\n\n`;
                if (nv.y_nghia_dien_hinh) info += `💭 Ý nghĩa: ${nv.y_nghia_dien_hinh}\n\n`;
                if (nv.chi_tiet_ngoai_hinh) info += `👁️ Ngoại hình: ${nv.chi_tiet_ngoai_hinh}\n\n`;
                if (nv.chi_tiet_noi_tam) info += `❤️ Nội tâm: ${nv.chi_tiet_noi_tam}`;
                
                return info;
            }
        }
    }
    
    // ===== TỔNG QUAN =====
    if (q.match(/tong quan|gioi thieu|la gi|overview|summary|intro/)) {
        let overview = `📚 **${tp.ten}**\n\n`;
        
        if (tp.tac_gia) overview += `✍️ Tác giả: ${tp.tac_gia}\n`;
        if (tp.nam_sang_tac) overview += `📅 Năm sáng tác: ${tp.nam_sang_tac}\n`;
        if (tp.the_loai) {
            const genres = Array.isArray(tp.the_loai) ? tp.the_loai : [tp.the_loai];
            overview += `📖 Thể loại: ${genres.join(', ')}\n`;
        }
        if (tp.nhan_vat) overview += `👥 Số nhân vật: ${tp.nhan_vat.length}\n`;
        
        if (tp.chu_de_chinh) overview += `\n💡 ${tp.chu_de_chinh}`;
        
        return overview;
    }
    
    // ===== XIN CHÀO / HI =====
    if (q.match(/^(xin chao|chao|hello|hi|hey)$/)) {
        return `Xin chào! Tôi là trợ lý ảo về tác phẩm "${tp.ten}". Bạn có thể hỏi tôi về:\n\n` +
               `📖 Nội dung, cốt truyện\n` +
               `👥 Nhân vật (tính cách, vai trò, số phận)\n` +
               `✍️ Tác giả\n` +
               `🎯 Ý nghĩa, thông điệp\n` +
               `🎨 Giá trị nghệ thuật\n` +
               `📅 Năm sáng tác, xuất bản\n` +
               `⏳ Giai đoạn văn học\n` +
               `🌍 Hoàn cảnh sáng tác`;
    }
    
    // ===== CẢM ƠN =====
    if (q.match(/cam on|thank|thanks|merci/)) {
        return "Không có gì! Tôi luôn sẵn sàng giúp bạn khám phá văn học Việt Nam. 😊";
    }
    
    // ===== DEFAULT - GỢI Ý =====
    return `🤔 Xin lỗi, tôi chưa hiểu câu hỏi của bạn.\n\n` +
           `Bạn có thể hỏi:\n\n` +
           `• "Nội dung tác phẩm về gì?"\n` +
           `• "Nhân vật chính là ai?"\n` +
           `• "Ý nghĩa tác phẩm?"\n` +
           `• "Tác giả là ai?"\n` +
           `• "Tác phẩm sáng tác năm nao?"\n` +
           `• "Hoàn cảnh sáng tác?"\n` +
           `• "Giá trị nghệ thuật?"\n` +
           `• "Cấu trúc tác phẩm?"\n` +
           `• "Chủ đề chính?"\n` +
           `• "[Tên nhân vật] có tính cách thế nào?"\n` +
           `• "Số phận của [tên nhân vật]?"`;
}
// ===== QUIZ GLOBAL =====
let quizData = [];
let questionIndex = 0;
let score = 0;
let answered = false;
function showLoadingQuiz() {
    const q = document.getElementById('quizQuestion');
    if (q) q.innerHTML = "⏳ AI đang tạo câu hỏi...";
}

function hideLoadingQuiz() {}
// ===== INIT QUIZ =====
async function initQuiz() {
    if (!currentTacPhamData) return;

    quizData = [];
    questionIndex = 0;
    score = 0;

    showLoadingQuiz();

    try {
        const usedQuestions = new Set();

        const promises = Array.from({ length: 5 }, () =>
            fetch('/api/quiz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tac_pham: currentTacPhamData.ten
                })
            }).then(res => res.json())
        );

        const results = await Promise.all(promises);

        for (const data of results) {
            if (data.success && !usedQuestions.has(data.quiz.question)) {
                quizData.push(data.quiz);
                usedQuestions.add(data.quiz.question);
            }

            if (quizData.length >= 5) break;
        }

        if (quizData.length === 0) {
            throw new Error("Không tạo được câu hỏi");
        }

    } catch (err) {
        console.error("Quiz AI lỗi → fallback", err);
        generateQuizFromData();
    }

    hideLoadingQuiz();
    showQuiz();
}
function generateQuizFromData() {
    if (!currentTacPhamData) return;

    const tp = currentTacPhamData;

    // ❗ KHÔNG reset nếu đã có câu AI
    const localQuiz = [];

    // ===== TÁC GIẢ =====
    if (tp.tac_gia) {
        const options = shuffle([tp.tac_gia, "Nguyễn Du", "Nam Cao", "Tố Hữu"]);

        localQuiz.push({
            question: `Ai là tác giả của "${tp.ten}"?`,
            options: options,
            correct: options.indexOf(tp.tac_gia)
        });
    }

    // ===== NĂM =====
    if (tp.nam_sang_tac) {
        const options = shuffle([
            tp.nam_sang_tac,
            tp.nam_sang_tac - 5,
            tp.nam_sang_tac + 3,
            tp.nam_sang_tac + 10
        ]);

        localQuiz.push({
            question: `"${tp.ten}" sáng tác năm nào?`,
            options: options,
            correct: options.indexOf(tp.nam_sang_tac)
        });
    }

    // ===== NHÂN VẬT =====
    if (tp.nhan_vat?.length > 0) {
        const nv = randomItem(tp.nhan_vat);

        const options = shuffle([
            nv.ten,
            "Chí Phèo",
            "Lão Hạc",
            "Thị Nở"
        ]);

        localQuiz.push({
            question: `Ai là nhân vật trong "${tp.ten}"?`,
            options: options,
            correct: options.indexOf(nv.ten)
        });

        if (nv.tinh_cach) {
            const tcOptions = shuffle([
                nv.tinh_cach,
                "Hiền lành",
                "Hung dữ",
                "Lạnh lùng"
            ]);

            localQuiz.push({
                question: `Tính cách của ${nv.ten}?`,
                options: tcOptions,
                correct: tcOptions.indexOf(nv.tinh_cach)
            });
        }
    }

    // ===== THỂ LOẠI =====
    if (tp.the_loai?.length > 0) {
        const tl = randomItem(tp.the_loai);

        const options = shuffle([
            tl,
            "Thơ",
            "Tiểu thuyết",
            "Kịch"
        ]);

        localQuiz.push({
            question: `"${tp.ten}" thuộc thể loại nào?`,
            options: options,
            correct: options.indexOf(tl)
        });
    }

    // 👉 GHÉP vào quizData hiện có
    quizData = [...quizData, ...shuffle(localQuiz)];
}

// ===== SHOW QUIZ =====
function showQuiz() {
    if (!quizData.length) return;

    answered = false;

    const q = quizData[questionIndex];

    const questionEl = document.getElementById('quizQuestion');
    const answersEl = document.getElementById('quizAnswers');
    const progressEl = document.getElementById('quizProgress');
    const scoreEl = document.getElementById('quizScore');

    if (!questionEl || !answersEl) return;

    questionEl.textContent = q.question;

    answersEl.innerHTML = q.options.map((opt, i) => `
    <button onclick="checkAnswer(${i})">
        ${String.fromCharCode(65 + i)}. ${opt}
    </button>
`).join('');

    progressEl.textContent = `Câu ${questionIndex + 1}/${quizData.length}`;
    scoreEl.textContent = `Điểm: ${score}`;
}

// ===== CHECK ANSWER =====
function checkAnswer(index) {
    if (answered) return;

    answered = true;

    const buttons = document.querySelectorAll('#quizAnswers button');
    const q = quizData[questionIndex];

    buttons.forEach((btn, i) => {
        if (i === q.correct) {
            btn.classList.add('correct');
        } else if (i === index) {
            btn.classList.add('wrong');
        }
    });

    if (index === q.correct) {
        score += 20;
    }

    document.getElementById('quizScore').textContent = `Điểm: ${score}`;
}

// ===== NEXT =====
function nextQuiz() {
    if (!quizData.length) return;

    questionIndex++;

    if (questionIndex >= quizData.length) {
        alert(`🎉 Hoàn thành!\nĐiểm: ${score}`);
        questionIndex = 0;
        score = 0;
    }

    showQuiz();
}

// ===== UTILS =====
function shuffle(arr) {
    return arr.sort(() => Math.random() - 0.5);
}

function randomItem(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
async function toggleFavorite() {

    if (!tacPhamData || !tacPhamData.ten) {
        showToast("Không tìm thấy dữ liệu tác phẩm!", "error");
        return;
    }

    try {

        const res = await fetch('/api/auth/favorite', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                ten_tac_pham: tacPhamData.ten
            })
        });

        if (res.status === 401) {

            showToast("⚠️ Vui lòng đăng nhập để yêu thích tác phẩm!", "error");

            setTimeout(() => {
                window.location.href = "/login";
            }, 1500);

            return;
        }

        const result = await res.json();

        if (result.success) {

            const btn = document.querySelector('.favorite-btn');

            if (result.is_favorite) {

                btn.classList.add('favorited');
                document.getElementById('favoriteText').innerText = "Đã yêu thích";

                showToast("❤️ Đã thêm vào yêu thích!");

            } else {

                btn.classList.remove('favorited');
                document.getElementById('favoriteText').innerText = "Yêu thích";

                showToast("💔 Đã bỏ khỏi yêu thích!");
            }

        } else {

            showToast(result.error || "Có lỗi xảy ra!", "error");
        }

    } catch (err) {

        console.error(err);
        showToast("Lỗi kết nối server!", "error");
    }
}
function showToast(message, type = "success") {
    const toast = document.createElement("div");
    toast.className = `favorite-toast ${type}`;
    toast.innerHTML = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(120px)";

        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 2500);
}
async function loadFavoriteState() {
    if (!tacPhamData || !tacPhamData.ten) return;

    try {
        const res = await fetch(`/api/auth/favorites/check?ten_tac_pham=${encodeURIComponent(tacPhamData.ten)}`, {
            method: 'GET',
            credentials: 'include'
        });

        const result = await res.json();

        if (result.success) {
            const btn = document.querySelector('.favorite-btn');

            if (result.is_favorite) {
                btn.classList.add('favorited');
                document.getElementById('favoriteText').innerText = "Đã yêu thích";
            } else {
                btn.classList.remove('favorited');
                document.getElementById('favoriteText').innerText = "Yêu thích";
            }
        }
    } catch (err) {
        console.error("Check favorite error:", err);
    }
}
// =========================
// READING MODE
// =========================

let currentFontSize = 24;

function openReadingMode(){

    const title =
        document.getElementById('tacPhamTitle').innerText;

    const author =
        document.getElementById('tacGia').innerText;

    const content =
        document.getElementById('noiDung').innerText;

    document.getElementById('readingTitle').innerText =
        title;

    document.getElementById('readingAuthor').innerText =
        author;

    document.getElementById('readingText').innerText =
        content;

    // reading time
    const words = content.split(/\s+/).length;

    const mins = Math.ceil(words / 200);

    document.getElementById('readingTime').innerText =
        `⏱ ${mins} phút đọc`;

    document.getElementById('readingMode').style.display =
        'block';

    document.body.style.overflow = 'hidden';
}

function closeReadingMode(){

    document.getElementById('readingMode').style.display =
        'none';

    document.body.style.overflow = 'auto';

    speechSynthesis.cancel();

    isSpeaking = false;
}

function changeFontSize(delta){

    currentFontSize += delta;

    if(currentFontSize < 16)
        currentFontSize = 16;

    if(currentFontSize > 42)
        currentFontSize = 42;

    document.querySelector('.reading-content')
        .style.fontSize =
            currentFontSize + 'px';
}

function toggleDarkReading(){

    document.getElementById('readingMode')
        .classList.toggle('dark');
}
document.addEventListener('DOMContentLoaded', ()=>{

    const rm =
        document.getElementById('readingMode');

    rm.addEventListener('scroll', ()=>{

        const scrollTop = rm.scrollTop;

        const maxScroll =
            rm.scrollHeight - rm.clientHeight;

        const percent =
            (scrollTop / maxScroll) * 100;

        document.getElementById('readingBar')
            .style.width = percent + '%';

        document.getElementById('readingPercent')
            .innerText =
                Math.floor(percent) + '%';
    });

});
let speechUtterance = null;

let isSpeaking = false;

function toggleSpeech(){

    if(isSpeaking){

        speechSynthesis.cancel();

        isSpeaking = false;

        document.getElementById('speechBtn')
            .innerText = '🔊 Đọc truyện';

        return;
    }

    const text =
        document.getElementById('readingText').innerText;

    speechUtterance =
        new SpeechSynthesisUtterance(text);

    speechUtterance.lang = 'vi-VN';

    speechUtterance.rate =
        parseFloat(
            document.getElementById('speechRate').value
        );

    const voices =
        speechSynthesis.getVoices();

    const viVoice =
        voices.find(v => v.lang.includes('vi'));

    if(viVoice){
        speechUtterance.voice = viVoice;
    }

    speechUtterance.onend = ()=>{

        isSpeaking = false;

        document.getElementById('speechBtn')
            .innerText = '🔊 Đọc truyện';
    };

    speechUtterance.onboundary = function(event){

        const progress =
            event.charIndex / text.length;

        const rm =
            document.getElementById('readingMode');

        const maxScroll =
            rm.scrollHeight - rm.clientHeight;

        rm.scrollTop = maxScroll * progress;
    };

    speechSynthesis.speak(speechUtterance);

    isSpeaking = true;

    document.getElementById('speechBtn')
        .innerText = '⏹ Dừng đọc';
}

window.speechSynthesis.onvoiceschanged = ()=>{
    speechSynthesis.getVoices();
};
async function loadCompareList(){

    const res =
        await fetch('/api/tac-pham/');

    const data = await res.json();

    if(!data.success) return;

    allTacPham = data.data;

    const select =
        document.getElementById(
            'compareSelect'
        );

    data.data.forEach(tp=>{

        const option =
            document.createElement('option');

        option.value = tp.ten;

        option.innerText = tp.ten;

        select.appendChild(option);

    });

}
async function startCompare(){

    const selected =
        document.getElementById(
            'compareSelect'
        ).value;
    
    if(!selected){
    
        alert('Chọn tác phẩm');
    
        return;
    }
    
    // loading
    document.getElementById(
        'compareResult'
    ).innerHTML = `
        <div class="ai-loading">
            🤖 AI đang phân tích chuyên sâu...
        </div>
    `;
    
    try{
    
        // lấy tác phẩm target
        const res =
            await fetch(
                '/api/tac-pham/' +
                encodeURIComponent(selected)
            );
    
        const data = await res.json();
    
        if(!data.success){
    
            throw new Error('Không tải được tác phẩm');
        }
    
        const target = data.data;
    
        // gọi AI compare
        const aiRes =
            await fetch(
                '/api/tac-pham/compare-ai',
                {
    
                    method:'POST',
    
                    headers:{
                        'Content-Type':'application/json'
                    },
    
                    body:JSON.stringify({
    
                        tp1: currentTacPhamData.ten,
                        tp2: target.ten
    
                    })
    
                }
            );
        const aiData =
            await aiRes.json();
        console.log("AI RESULT:", aiData);
        // check lỗi AI
        if(!aiData.success){
            document.getElementById(
                'compareResult'
            ).innerHTML = `
                <div class="ai-error">
                    ❌ ${aiData.error}
                </div>
            `;
            return;
        }
        // render AI
        document.getElementById(
            'compareResult'
        ).innerHTML = `
            <div class="ai-analysis">
                ${
                    formatAIText(aiData.data)
                }
            </div>
        `;
    }catch(err){
        console.error(err);
        document.getElementById(
            'compareResult'
        ).innerHTML = `
            <div class="ai-error">
                ❌ ${err.message}
            </div>
        `;
    }
}
function formatAIText(text) {

    if (!text) {
        return `
            <div class="ai-error">
                ❌ Không có dữ liệu AI trả về
            </div>
        `;
    }
    
    // nếu object
    if (typeof text === 'object') {
    
        text = JSON.stringify(text, null, 2);
    }
    
    return text
    
        .replace(/\n/g, "<br>")
    
        .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>")
    
        .replace(/### (.*?)(<br>|$)/g, "<h3>$1</h3>")
    
        .replace(/## (.*?)(<br>|$)/g, "<h2>$1</h2>")
    
        .replace(/# (.*?)(<br>|$)/g, "<h1>$1</h1>");
    
    }
async function initCompareCurrent(){

    try{

        const res =
        await fetch('/api/tac-pham/');

        const data = await res.json();

        const list = data.data || [];

        const s1 =
        document.getElementById('compareSelect1');

        const s2 =
        document.getElementById('compareSelect2');

        s1.innerHTML = '';
        s2.innerHTML = '';

        list.forEach(tp=>{

            const option1 =
            document.createElement('option');

            option1.value = tp.ten;
            option1.textContent = tp.ten;

            const option2 =
            option1.cloneNode(true);

            s1.appendChild(option1);
            s2.appendChild(option2);

        });

    }catch(err){

        console.log(err);

    }

}
async function compareTacPhamAI(){

    const tp1 =
    document.getElementById('compareSelect1').value;

    const tp2 =
    document.getElementById('compareSelect2').value;

    const resultBox =
    document.getElementById('compareResult');

    const loading =
    document.getElementById('compareLoading');

    loading.style.display = 'block';

    resultBox.innerHTML = '';

    try{

        const res = await fetch(
            '/api/tac-pham/compare-ai',
            {
                method:'POST',

                headers:{
                    'Content-Type':'application/json'
                },

                body:JSON.stringify({
                    tp1,
                    tp2
                })
            }
        );

        const data = await res.json();

        loading.style.display = 'none';

        if(data.success){

            resultBox.innerHTML =
            marked.parse(data.data);

        }else{

            resultBox.innerHTML =
            '❌ ' + data.error;

        }

    }catch(err){

        loading.style.display = 'none';

        resultBox.innerHTML =
        '❌ Lỗi AI';

        console.log(err);

    }

}
async function compareAI(tp1, tp2){

    try{

        const res = await fetch(
            '/api/tac-pham/compare-ai',
            {
                method:'POST',

                headers:{
                    'Content-Type':'application/json'
                },

                body:JSON.stringify({
                    tp1,
                    tp2
                })
            }
        );

        const data = await res.json();

        if(data.success){

            document.getElementById(
                'aiCompareResult'
            ).innerHTML = `
                <div class="ai-result">
                    ${marked.parse(data.analysis)}
                </div>
            `;

        }else{

            console.error(data.error);

        }

    }catch(err){

        console.error(err);

    }
}
