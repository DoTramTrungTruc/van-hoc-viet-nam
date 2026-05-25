/**
 * Graph Visualization với Vis.js Network
 * Vẽ đồ thị mối liên kết giữa các thực thể văn học
 */

function createGraph(container, graphData) {
    // Prepare nodes với màu sắc theo nhóm
    const nodes = graphData.nodes.map(node => ({
        id: node.id,
        label: node.label,
        color: getNodeColor(node.group),
        shape: 'dot',
        size: 20,
        font: {
            size: 14,
            color: '#333'
        },
        group: node.group
    }));

    // Prepare edges
    const edges = graphData.edges.map((edge, index) => ({
        id: index,
        from: edge.from,
        to: edge.to,
        label: formatEdgeLabel(edge.label),
        arrows: 'to',
        font: {
            size: 10,
            align: 'middle'
        },
        color: {
            color: '#999',
            highlight: '#3498db'
        }
    }));

    // Create network
    const data = { nodes, edges };

    const options = {
        nodes: {
            borderWidth: 2,
            borderWidthSelected: 3,
            shadow: true
        },
        edges: {
            width: 2,
            shadow: true,
            smooth: {
                type: 'cubicBezier',
                forceDirection: 'horizontal',
                roundness: 0.4
            }
        },
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -8000,
                centralGravity: 0.3,
                springLength: 150,
                springConstant: 0.04,
                damping: 0.09,
                avoidOverlap: 0.5
            },
            stabilization: {
                iterations: 200
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            navigationButtons: true,
            keyboard: true
        },
        layout: {
            improvedLayout: true,
            hierarchical: false
        }
    };

    const network = new vis.Network(container, data, options);

    // Event handlers
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            console.log('Clicked node:', nodeId);
            // Could open detail modal here
        }
    });

    network.on('stabilized', function() {
        network.fit();
    });

    // Stabilize after 2 seconds
    setTimeout(() => {
        network.stopSimulation();
    }, 2000);

    return network;
}

function getNodeColor(group) {
    const colors = {
        'author': '#607D8B',      // Gray - Tác giả
        'tacgia': '#607D8B',      // Gray - Tác giả (alias)
        'work': '#8B4513',        // Brown - Tác phẩm
        'tacpham': '#8B4513',     // Brown - Tác phẩm (alias)
        'character': '#E74C3C',   // Red - Nhân vật
        'nhanvat': '#E74C3C',     // Red - Nhân vật (alias)
        'genre': '#27AE60',       // Green - Thể loại
        'theloai': '#27AE60',     // Green - Thể loại (alias)
        'period': '#9C27B0',      // Purple - Thời kỳ
        'thoiky': '#9C27B0',      // Purple - Thời kỳ (alias)
        'theme': '#FF9800',       // Orange - Chủ đề
        'chude': '#FF9800',       // Orange - Chủ đề (alias)
        'other': '#999999'        // Gray - Khác
    };
    
    return colors[group] || colors['other'];
}

function formatEdgeLabel(label) {
    const labelMap = {
        'SANG_TAC': 'Sáng tác',
        'CO_NHAN_VAT': 'Có nhân vật',
        'THUOC_THE_LOAI': 'Thuộc thể loại',
        'QUAN_HE': 'Quan hệ',
        'NOI_VE': 'Nói về',
        'THUOC_THOI_KY': 'Thuộc thời kỳ',
        'SU_DUNG': 'Sử dụng'
    };
    
    return labelMap[label] || label;
}

/**
 * Tạo đồ thị từ entity name (load từ API)
 */
async function loadAndDrawGraph(entityName, containerId) {
    try {
        const response = await fetch(`/api/qa/graph/${encodeURIComponent(entityName)}`);
        const data = await response.json();
        
        if (data.success && data.data.nodes.length > 0) {
            const container = document.getElementById(containerId);
            return createGraph(container, data.data);
        } else {
            console.error('No graph data found');
            return null;
        }
    } catch (error) {
        console.error('Error loading graph:', error);
        return null;
    }
}

/**
 * Export graph as image
 */
function exportGraphAsImage(network, filename = 'graph.png') {
    const canvas = network.canvas.frame.canvas;
    const dataURL = canvas.toDataURL('image/png');
    
    const link = document.createElement('a');
    link.download = filename;
    link.href = dataURL;
    link.click();
}

/**
 * Reset graph view
 */
function resetGraphView(network) {
    network.fit();
    network.startSimulation();
}

/**
 * Highlight connected nodes
 */
function highlightConnectedNodes(network, nodeId) {
    const connectedNodes = network.getConnectedNodes(nodeId);
    const allNodes = network.body.data.nodes.get();
    
    allNodes.forEach(node => {
        if (node.id === nodeId || connectedNodes.includes(node.id)) {
            network.body.data.nodes.update({
                id: node.id,
                opacity: 1
            });
        } else {
            network.body.data.nodes.update({
                id: node.id,
                opacity: 0.2
            });
        }
    });
}