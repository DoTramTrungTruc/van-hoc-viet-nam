/**
 * TAC-GIA-DETAIL.JS
 * Trang chi tiết tác giả + graph tác phẩm
 */

const tenTacGia = decodeURIComponent(window.location.pathname.split('/').pop());

document.addEventListener('DOMContentLoaded', function () {
    loadTacGiaDetail();

    // Chat events
    const input = document.getElementById('chatInput');
    const btn = document.getElementById('chatSend');

    if (btn) btn.addEventListener('click', sendMessageTacGia);

    if (input) {
        input.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') sendMessageTacGia();
        });
    }
});
function escapeHtml(text) {
    if (!text) return '';

    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
async function loadTacGiaDetail() {
    try {
        const res = await fetch(`/api/tac-gia/${encodeURIComponent(tenTacGia)}`);
        const data = await res.json();

        if (!data.success) {
            showError("Không tìm thấy tác giả");
            return;
        }

        const tg = data.data;
        currentTacGiaData = tg;
        displayTacGiaInfo(tg);
        drawGraphTacGia(tg);

        document.getElementById('loading').style.display = 'none';
        document.getElementById('content').style.display = 'block';

    } catch (err) {
        console.error(err);
        showError(err.message);
    }
}
function formatLiteraryText(text) {
    if (!text) return '';

    return text
        .split('\n')
        .filter(p => p.trim() !== '')
        .map(p => {

            const line = escapeHtml(p.trim());

            // Nếu là câu quote
            if (
                line.startsWith('"') ||
                line.startsWith('“') ||
                line.length < 80
            ) {
                return `
                    <blockquote class="literary-quote">
                        ${line}
                    </blockquote>
                `;
            }

            // Paragraph thường
            return `
                <p class="literary-paragraph">
                    ${line}
                </p>
            `;
        })
        .join('');
}
/* ================= HIỂN THỊ INFO ================= */
function displayTacGiaInfo(tg) {
    document.getElementById('tacGiaTitle').textContent = tg.ten;
    document.getElementById('breadcrumbTitle').textContent = tg.ten;
    document.title = tg.ten + " - Tác giả";

    document.getElementById('namSinh').textContent = tg.nam_sinh || 'N/A';
    document.getElementById('namMat').textContent = tg.nam_mat || 'N/A';
    document.getElementById('queQuan').textContent = tg.que_quan || 'N/A';
    document.getElementById('truongPhai').textContent = tg.truong_phai || 'N/A';
     
    document.getElementById('butDanhDetail').textContent =
        tg.but_danh || 'Chưa có dữ liệu';

    document.getElementById('giaiThuongDetail').textContent =
        tg.giai_thuong || 'Chưa có dữ liệu';

    document.getElementById('cauNoiDetail').innerHTML =
        formatLiteraryText(tg.cau_noi_noi_tieng);
    const img = document.getElementById('tacGiaImage');

    if (img) {
        img.src = tg.anh_dai_dien || '/static/images/default_cover.jpg';
    
        // fallback nếu lỗi ảnh
        img.onerror = function () {
            this.src = '/static/images/default_cover.jpg';
        };
    }
    if (tg.tieu_su) {
        document.getElementById('tieuSu').innerHTML =
        formatLiteraryText(tg.tieu_su);
    }
}

/* ================= GRAPH TÁC GIẢ MỞ RỘNG (KNOWLEDGE GRAPH) ================= */
function drawGraphTacGia(tg) {
    const nodes = [];
    const edges = [];
    const nodeCache = new Map();

    function addNode(node) {
        if (!nodeCache.has(node.id)) {
            nodeCache.set(node.id, true);
            nodes.push(node);
        }
    }

    console.log("DỮ LIỆU ĐẦU VÀO NEO4J TÁC GIẢ:", tg);

    // ==========================================
    // 1. TẠO NODE TRUNG TÂM: TÁC GIẢ & TOOLTIP CHI TIẾT
    // ==========================================
    const tgTooltip = document.createElement('div');
    tgTooltip.style.maxWidth = '300px';
    tgTooltip.style.whiteSpace = 'normal';
    tgTooltip.style.wordBreak = 'break-word';
    tgTooltip.style.fontFamily = 'Segoe UI, Roboto, sans-serif';
    tgTooltip.style.fontSize = '13px';
    tgTooltip.style.lineHeight = '1.6';

    const cuocDoi = (tg.nam_sinh || tg.nam_mat) 
        ? `<br><b>📅 Thời gian sống:</b> ${tg.nam_sinh || '?' } - ${tg.nam_mat || '?'}` 
        : '';

    tgTooltip.innerHTML = `
        <b style="color: #2980B9; font-size: 14px;">👤 Tác giả: ${tg.ten}</b>
        ${tg.but_danh ? `<br><b>🖊️ Bút danh khác:</b> ${tg.but_danh}` : ''}
        ${cuocDoi}
        ${tg.que_quan ? `<br><b>📍 Quê quán:</b> ${tg.que_quan}` : ''}
        ${tg.truong_phai ? `<br><b>🏫 Trường phái:</b> ${tg.truong_phai}` : ''}
        ${tg.tieu_su ? `<br><hr style="border-top:1px dashed #ddd; margin:5px 0;"><b>📖 Tiểu sử tóm tắt:</b> <span style="color:#555;">${tg.tieu_su}</span>` : ''}
        <br><span style="color: #7f8c8d; font-size: 11px; display:block; margin-top:5px;">💡 Click vào khoảng trống để hủy highlight cụm.</span>
    `;

    addNode({
        id: 'tacgia',
        label: `✍️ ${tg.ten}`,
        group: 'tacgia',
        size: 45,
        font: { size: 16, bold: true },
        title: tgTooltip
    });

    // ==========================================
    // 2. MỞ RỘNG: NODE TRƯỜNG PHÁI VĂN HỌC
    // ==========================================
    if (tg.truong_phai) {
        const tpId = 'truongphai_' + tg.truong_phai;
        const tpTooltip = document.createElement('div');
        tpTooltip.style.maxWidth = '220px';
        tpTooltip.style.whiteSpace = 'normal';
        tpTooltip.innerHTML = `<b>🏫 Trường phái văn học</b><br>${tg.truong_phai}`;

        addNode({
            id: tpId,
            label: `🏫 ${tg.truong_phai}`,
            group: 'chude', 
            size: 25,
            font: { size: 12, bold: true },
            title: tpTooltip
        });

        edges.push({
            from: 'tacgia',
            to: tpId,
            label: 'thuộc trường phái',
            arrows: 'to',
            width: 2,
            color: { color: '#F39C12' },
            length: 200
        });
    }
 

    // ==========================================
    // EXTRA: NODE NĂM SINH
    // ==========================================
    if (tg.nam_sinh) {
        const nsId = 'namsinh_' + tg.nam_sinh;
        addNode({
            id: nsId,
            label: `🐣 Sinh: ${tg.nam_sinh}`,
            group: 'thoiky', 
            size: 22,
            font: { size: 11 },
            title: (() => {
                const container = document.createElement('div');
                container.style.padding = '4px';
                container.innerHTML = `<b>📅 Năm sinh của tác giả:</b> ${tg.nam_sinh}`;
                return container;
            })()
        });
        edges.push({
            from: 'tacgia',
            to: nsId,
            label: 'sinh năm',
            arrows: 'to',
            width: 1.5,
            color: { color: '#2ECC71' },
            length: 180
        });
    }

    // ==========================================
    // EXTRA: NODE NĂM MẤT
    // ==========================================
    if (tg.nam_mat) {
        const nmId = 'nammat_' + tg.nam_mat;
        addNode({
            id: nmId,
            label: `🍂 Mất: ${tg.nam_mat}`,
            group: 'thoiky',
            size: 22,
            font: { size: 11 },
            title: (() => {
                const container = document.createElement('div');
                container.style.padding = '4px';
                container.innerHTML = `<b>📅 Năm mất của tác giả:</b> ${tg.nam_mat}`;
                return container;
            })()
           
        });
        edges.push({
            from: 'tacgia',
            to: nmId,
            label: 'mất năm',
            arrows: 'to',
            width: 1.5,
            color: { color: '#27AE60' },
            length: 180
        });
    }

    // ==========================================
    // EXTRA: NODE QUÊ QUÁN
    // ==========================================
    if (tg.que_quan) {
        const qqId = 'quequan_' + tg.que_quan;
        addNode({
            id: qqId,
            label: `📍 ${tg.que_quan}`,
            group: 'theloai', 
            size: 24,
            font: { size: 11, italic: true },
            title: (() => {
                const container = document.createElement('div');
                container.style.padding = '4px';
                container.innerHTML = `<b>📍 Quê quán gốc:</b> ${tg.que_quan}`;
                return container;
            })()

        });
        edges.push({
            from: 'tacgia',
            to: qqId,
            label: 'quê quán',
            arrows: 'to',
            width: 1.5,
            color: { color: '#1ABC9C' },
            length: 180
        });
    }

    // ==========================================
    // 4. DANH SÁCH NODE TÁC PHẨM SÁNG TÁC
    // ==========================================
    if (!tg.tac_pham || tg.tac_pham.length === 0) {
        console.warn("Không có tác phẩm!");
    } else {
        tg.tac_pham.forEach((tp, index) => {
            if (!tp || tp.trim() === '') return;
            if (tp === tg.ten) return;

            const id = 'tp_' + index;
            const tpTooltip = document.createElement('div');
            tpTooltip.style.maxWidth = '250px';
            tpTooltip.style.whiteSpace = 'normal';
            tpTooltip.style.wordBreak = 'break-word';
            tpTooltip.style.fontFamily = 'Merriweather, serif';
            tpTooltip.style.fontSize = '13px';
            tpTooltip.innerHTML = `<b>📚 Tác phẩm: ${tp}</b><br><span style="color: #2980B9;">Click để chuyển hướng sang trang chi tiết nội dung.</span>`;

            addNode({
                id,
                label: `📖 ${tp}`,
                group: 'tacpham',
                size: 23,
                font: { size: 12 },
                title: tpTooltip
            });

            edges.push({
                from: 'tacgia',
                to: id,
                label: 'sáng tác',
                arrows: 'to',
                width: 2,
                color: { color: '#8B4513', highlight: '#D4AC0D' },
                length: 180
            });
        });
    }

    // ==========================================
    // 5. CẤU HÌNH UI VIS.JS CHỐNG XOAY & ỔN ĐỊNH ĐỒ THỊ
    // ==========================================
    const options = {
        nodes: {
            shape: 'box',
            margin: { top: 8, bottom: 8, left: 12, right: 12 },
            shapeProperties: { borderRadius: 6 },
            font: { face: 'Segoe UI, Roboto, Helvetica, Arial, sans-serif', align: 'center' },
            shadow: { enabled: true, color: 'rgba(0,0,0,0.1)', size: 4, x: 2, y: 2 }
        },
        edges: {
            font: { size: 10, align: 'middle', background: '#ffffff', color: '#666666' },
            smooth: { type: 'cubicBezier', roundness: 0.4 }
        },
        groups: {
            tacgia: { color: { background: '#EBF5FB', border: '#2980B9', highlight: { background: '#D4E6F1', border: '#21618C' } } },
            tacpham: { color: { background: '#FFF9E6', border: '#D4AC0D', highlight: { background: '#FFF1C5', border: '#B7950B' } } },
            chude: { color: { background: '#FFF3E0', border: '#F39C12', highlight: { background: '#FCF3CF', border: '#D35400' } } }, 
            theloai: { color: { background: '#E0F2F1', border: '#1ABC9C', highlight: { background: '#B2DFDB', border: '#16A085' } } }, 
            thoiky: { color: { background: '#E8F5E9', border: '#2ECC71', highlight: { background: '#C8E6C9', border: '#27AE60' } } },  
            nhanvat: { color: { background: '#FDEDEC', border: '#E74C3C', highlight: { background: '#FADBD8', border: '#C0392B' } } }  
        },
        // ĐÃ SỬA: Tinh chỉnh lại các thông số chống xoay vô hạn
        physics: {
            enabled: true,
            solver: 'barnesHut',
            barnesHut: {
                gravitationalConstant: -2000,  // Giảm lực đẩy vừa phải để không bị giật bắn ra ngoài
                centralGravity: 0.4,          // Tăng trọng lực trung tâm để hút các node gom cụm lại ổn định hơn
                springLength: 130,            // Giảm độ dài lò xo tránh việc co giãn liên tục
                springConstant: 0.05,
                damping: 0.3,                 // Tăng hệ số giảm chấn (damping) giúp dập tắt dao động xoay nhanh chóng
                avoidOverlap: 1               // Chống đè chữ
            },
            stabilization: {
                enabled: true,                // Bật tính năng tính toán ngầm
                iterations: 150,              // Thực hiện 150 bước tính toán trước khi vẽ lên màn hình
                updateInterval: 25
            }
        },
        interaction: { hover: true, tooltipDelay: 120, navigationButtons: true, keyboard: true }
    };

    const container = document.getElementById('network');
    const nodesDataSet = new vis.DataSet(nodes);
    const edgesDataSet = new vis.DataSet(edges);
    const network = new vis.Network(container, { nodes: nodesDataSet, edges: edgesDataSet }, options);

    // ĐÃ SỬA: Tắt hẳn chế độ physics ngay sau khi đồ thị đã ổn định cấu trúc ổn thỏa
    network.on("stabilizationIterationsDone", function () {
        network.setOptions({ physics: { enabled: false } });
    });

    // ==========================================
    // 6. HIỆU ỨNG HIGHLIGHT TIÊU ĐIỂM KHI CLICK
    // ==========================================
    let allNodes = nodesDataSet.get({ returnType: "Object" });
    let isHighlighted = false;

    network.on("click", function (params) {
        if (params.nodes.length > 0) {
            isHighlighted = true;
            const selectedNode = params.nodes[0];
            const connectedNodes = network.getConnectedNodes(selectedNode);

            for (let nodeId in allNodes) {
                allNodes[nodeId].color = { background: 'rgba(240, 240, 240, 0.4)', border: 'rgba(200, 200, 200, 0.4)' };
                allNodes[nodeId].font = { color: 'rgba(150, 150, 150, 0.4)' };
            }

            connectedNodes.forEach(nodeId => {
                allNodes[nodeId].color = undefined;
                allNodes[nodeId].font = { color: '#000000' };
            });
            allNodes[selectedNode].color = undefined;
            allNodes[selectedNode].font = { color: '#000000', bold: true };

            const updateArray = [];
            for (let nodeId in allNodes) { updateArray.push(allNodes[nodeId]); }
            nodesDataSet.update(updateArray);

            if (selectedNode.startsWith('tp_')) {
                const index = parseInt(selectedNode.replace('tp_', ''));
                const ten = tg.tac_pham[index];
                if (!ten || ten === tg.ten) return;
                window.location.href = `/tac-pham/${encodeURIComponent(ten)}`;
            }
        } else if (isHighlighted) {
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

    network.on("hoverNode", function () { network.body.container.style.cursor = 'pointer'; });
    network.on("blurNode", function () { network.body.container.style.cursor = 'default'; });
}
async function sendMessageTacGia() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    addMessage(message, 'user');
    input.value = '';
    showTyping();

    try {
        const res = await fetch('/api/chat-tac-gia', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: message,
                tac_gia: currentTacGiaData?.ten
            })
        });

        const data = await res.json();
        hideTyping();

        if (data.success) {
            addMessage(data.answer, 'bot');
        } else {
            addMessage(data.answer || "Không có câu trả lời.", 'bot');
        }

    } catch (err) {
        console.error(err);
        hideTyping();
        addMessage(processTacGiaQuestion(message), 'bot');
    }
}

function processTacGiaQuestion(question) {
    if (!currentTacGiaData) return "Chưa có dữ liệu tác giả.";

    const q = question.toLowerCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '');

    const tg = currentTacGiaData;

    // ===== TIỂU SỬ =====
    if (q.match(/tieu su|gioi thieu|la ai|who/)) {
        return tg.tieu_su || "Chưa có tiểu sử.";
    }

    // ===== NĂM SINH =====
    if (q.match(/nam sinh|sinh nam nao/)) {
        return tg.nam_sinh
            ? `Tác giả sinh năm ${tg.nam_sinh}.`
            : "Chưa có thông tin năm sinh.";
    }

    // ===== NĂM MẤT =====
    if (q.match(/nam mat|mat nam nao/)) {
        return tg.nam_mat
            ? `Tác giả mất năm ${tg.nam_mat}.`
            : "Chưa có thông tin năm mất.";
    }

    // ===== QUÊ =====
    if (q.match(/que|que quan|o dau/)) {
        return tg.que_quan
            ? `Quê quán: ${tg.que_quan}.`
            : "Chưa có thông tin quê quán.";
    }

    // ===== TRƯỜNG PHÁI =====
    if (q.match(/truong phai|phong cach|style/)) {
        return tg.truong_phai || "Chưa có thông tin.";
    }

    // ===== TÁC PHẨM =====
    if (q.match(/tac pham|viet gi|sang tac/)) {
        if (tg.tac_pham && tg.tac_pham.length > 0) {
            return `Các tác phẩm: ${tg.tac_pham.join(', ')}`;
        }
        return "Chưa có danh sách tác phẩm.";
    }

    return "Bạn có thể hỏi về tiểu sử, năm sinh, quê quán, tác phẩm...";
}

// ================= UI CHAT =================
function addMessage(text, sender) {
    const box = document.getElementById('chatMessages');
    const div = document.createElement('div');

    div.className = `chat-message ${sender}-message`;

    div.innerHTML = `
        <div class="message-icon">${sender === 'bot' ? '🤖' : '👤'}</div>
        <div class="message-content"><p>${text}</p></div>
    `;

    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

function showTyping() {
    const box = document.getElementById('chatMessages');
    const div = document.createElement('div');

    div.id = 'typingIndicator';
    div.className = 'chat-message bot-message';
    div.innerHTML = `🤖 Đang trả lời...`;

    box.appendChild(div);
}

function hideTyping() {
    document.getElementById('typingIndicator')?.remove();
}

/* ================= ERROR ================= */
function showError(msg) {
    document.getElementById('loading').innerHTML = `
        <h2 style="color:white">${msg}</h2>
    `;
}