/* ==========================================
   FORUM.JS - Diễn đàn văn học Việt Nam
   ========================================== */

// ===== STATE =====
let currentUser   = null;   // { user_id, username, is_admin, ... }
let currentPage   = 1;
let currentTab    = 'all';  // 'all' | 'tac_pham' | 'tac_gia'
let activeTagType = null;
let activeTagName = null;
let hasMore       = true;
let isLoading     = false;

const EMOJIS = [
    { e: '👍', label: 'Thích' },
    { e: '❤️', label: 'Yêu thích' },
    { e: '😮', label: 'Ngạc nhiên' },
    { e: '😢', label: 'Buồn' },
    { e: '🔥', label: 'Tuyệt vời' },
    { e: '📚', label: 'Hay lắm' },
];

// ===== INIT =====
document.addEventListener('DOMContentLoaded', async () => {
    await fetchCurrentUser();
    setupUI();
    await loadPosts(true);
    loadStats();
});

async function fetchCurrentUser() {
    try {
        const res  = await fetch('/api/auth/me', { credentials: 'include' });
        const data = await res.json();
        if (data.success && data.user) {
            currentUser = data.user;
        }
    } catch (_) {}
}

function setupUI() {
    const createBox  = document.getElementById('createPostBox');
    const loginHint  = document.getElementById('loginPrompt');
    const myAvatar   = document.getElementById('myAvatar');

    if (currentUser) {
        createBox.style.display  = 'block';
        loginHint.style.display  = 'none';
        myAvatar.textContent = avatarLetter(currentUser.username || currentUser.full_name);
    } else {
        createBox.style.display  = 'none';
        loginHint.style.display  = 'flex';
    }
}

// ===== LOAD POSTS =====
async function loadPosts(reset = false) {
    if (isLoading) return;
    isLoading = true;

    if (reset) {
        currentPage = 1;
        hasMore     = true;
        document.getElementById('postsFeed').innerHTML =
            '<div class="feed-loading"><div class="spinner"></div><span>Đang tải bài viết...</span></div>';
    }

    const params = new URLSearchParams({ page: currentPage, page_size: 10 });
    if (currentTab !== 'all') params.set('tag_type', currentTab);
    if (activeTagType) params.set('tag_type', activeTagType);
    if (activeTagName) params.set('tag_name', activeTagName);

    try {
        const res  = await fetch(`/api/forum/posts?${params}`, { credentials: 'include' });
        const data = await res.json();

        if (!data.success) throw new Error(data.error);

        const { posts, total_pages } = data.data;
        hasMore = currentPage < total_pages;

        if (reset) {
            if (posts.length === 0) {
                document.getElementById('postsFeed').innerHTML = `
                    <div class="empty-feed">
                        <div class="empty-icon">📭</div>
                        <p>Chưa có bài viết nào. Hãy là người đầu tiên chia sẻ!</p>
                    </div>`;
            } else {
                document.getElementById('postsFeed').innerHTML = '';
                posts.forEach(p => appendPostCard(p));
            }
        } else {
            posts.forEach(p => appendPostCard(p));
        }

        document.getElementById('loadMoreWrap').style.display = hasMore ? 'block' : 'none';

    } catch (err) {
        document.getElementById('postsFeed').innerHTML =
            `<div class="empty-feed"><p>❌ Lỗi tải bài viết: ${err.message}</p></div>`;
    } finally {
        isLoading = false;
    }
}

async function loadMorePosts() {
    currentPage++;
    await loadPosts(false);
}

// ===== RENDER POST CARD =====
function appendPostCard(post) {
    const div = document.createElement('div');
    div.className = 'post-card';
    div.id        = `post-${post.id}`;

    const letter   = avatarLetter(post.full_name || post.username);
    const timeStr  = formatTime(post.created_at);
    const canDel   = currentUser &&
                     (currentUser.user_id === post.user_id || currentUser.is_admin);

    // Reaction summary
    const totalReacts = Object.values(post.reactions || {}).reduce((a, b) => a + b, 0);
    const topEmojis   = Object.entries(post.reactions || {})
        .sort((a, b) => b[1] - a[1]).slice(0, 3)
        .map(([e]) => e).join('');

    // Content collapse
    const isLong    = (post.content || '').length > 300;
    const contentId = `content-${post.id}`;

    div.innerHTML = `
        <!-- Header -->
        <div class="post-header">
            <div class="post-avatar">
                ${post.anh_dai_dien
                    ? `<img src="${esc(post.anh_dai_dien)}" onerror="this.parentElement.textContent='${letter}'">`
                    : letter}
            </div>
            <div class="post-meta">
                <div class="post-author">${esc(post.full_name || post.username)}</div>
                <div class="post-time">${timeStr}
                ${post.tag_name ? `
                    <span class="post-tag-badge"
                          onclick="${post.tag_type === 'tac_pham'
                            ? `goToTacPham('${esc(post.tag_name)}')`
                            : `goToTacGia('${esc(post.tag_name)}')`}">
                        ${post.tag_type === 'tac_pham' ? '📖' : '✍️'}
                        ${esc(post.tag_name)}
                    </span>` : ''}
                </div>
            </div>
            ${canDel ? `<button class="post-delete-btn" onclick="deletePost(${post.id})" title="Xóa bài">🗑️</button>` : ''}
        </div>

        <!-- Content -->
        ${post.title ? `<div class="post-title">${esc(post.title)}</div>` : ''}
        <div class="post-content ${isLong ? 'collapsed' : ''}" id="${contentId}">
            ${esc(post.content)}
        </div>
        ${isLong
            ? `<button class="read-more-btn" onclick="toggleExpand('${contentId}', this)">Xem thêm ▼</button>`
            : ''}

        <!-- Reactions bar -->
        <div class="reactions-bar">
            <div class="reaction-summary">
                ${topEmojis ? `<span>${topEmojis}</span>` : ''}
                ${totalReacts > 0 ? `<span>${totalReacts} lượt cảm xúc</span>` : ''}
            </div>
            <div class="emoji-reactions" id="reactions-${post.id}">
                ${renderEmojiButtons(post.id, post.reactions, post.user_reaction)}
            </div>
        </div>

        <!-- Actions -->
        <div style="display:flex;align-items:center;gap:.5rem;padding-top:.3rem">
            <button class="comment-toggle-btn"
                    onclick="toggleComments(${post.id})">
                💬 ${post.comment_count > 0 ? post.comment_count + ' bình luận' : 'Bình luận'}
            </button>
        </div>

        <!-- Comments -->
        <div class="comments-section" id="comments-section-${post.id}">
            <div id="comments-list-${post.id}"></div>
            ${currentUser
                ? `<div class="comment-input-row">
                        <div class="comment-avatar" style="margin-top:.2rem">
                            ${currentUser.anh_dai_dien
                                ? `<img src="${esc(currentUser.anh_dai_dien)}">`
                                : avatarLetter(currentUser.username)}
                        </div>
                        <textarea id="comment-input-${post.id}"
                                  placeholder="Viết bình luận..."
                                  rows="2"
                                  onkeydown="handleCommentKey(event,${post.id})"></textarea>
                        <button class="comment-submit-btn"
                                onclick="submitComment(${post.id})">Gửi</button>
                   </div>`
                : `<p style="color:#aaa;font-size:.88rem;padding:.5rem 0">
                       <a href="/login" style="color:var(--vn-brown)">Đăng nhập</a> để bình luận
                   </p>`}
        </div>
    `;

    document.getElementById('postsFeed').appendChild(div);
}

function renderEmojiButtons(postId, reactions, userReaction) {
    return EMOJIS.map(({ e, label }) => {
        const count   = (reactions || {})[e] || 0;
        const isActive = userReaction === e;
        return `
            <button class="emoji-btn ${isActive ? 'active' : ''}"
                    onclick="react(${postId}, '${e}')"
                    title="${label}">
                ${e}
                ${count > 0 ? `<span class="count">${count}</span>` : ''}
            </button>`;
    }).join('');
}

// ===== REACT =====
async function react(postId, emoji) {
    if (!currentUser) {
        alert('Vui lòng đăng nhập để thả cảm xúc!');
        return;
    }
    try {
        const res  = await fetch(`/api/forum/posts/${postId}/react`, {
            method: 'POST', credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emoji })
        });
        const data = await res.json();
        if (data.success) {
            document.getElementById(`reactions-${postId}`).innerHTML =
                renderEmojiButtons(postId, data.data.reactions, data.data.user_reaction);

            // update summary
            const bar = document.getElementById(`reactions-${postId}`).closest('.reactions-bar');
            const summary = bar.querySelector('.reaction-summary');
            const totalR  = Object.values(data.data.reactions).reduce((a, b) => a + b, 0);
            const topE    = Object.entries(data.data.reactions)
                .sort((a, b) => b[1] - a[1]).slice(0, 3).map(([e]) => e).join('');
            summary.innerHTML = `
                ${topE ? `<span>${topE}</span>` : ''}
                ${totalR > 0 ? `<span>${totalR} lượt cảm xúc</span>` : ''}`;
        }
    } catch (err) { console.error(err); }
}

// ===== COMMENTS =====
async function toggleComments(postId) {
    const section = document.getElementById(`comments-section-${postId}`);
    if (section.classList.contains('open')) {
        section.classList.remove('open');
        return;
    }
    section.classList.add('open');
    await loadComments(postId);
}

async function loadComments(postId) {
    const listEl = document.getElementById(`comments-list-${postId}`);
    listEl.innerHTML = '<div style="color:#aaa;font-size:.88rem;padding:.5rem">Đang tải...</div>';

    try {
        const res  = await fetch(`/api/forum/posts/${postId}`, { credentials: 'include' });
        const data = await res.json();
        if (data.success) {
            renderComments(postId, data.data.comments || []);
        }
    } catch (err) { listEl.innerHTML = ''; }
}

function renderComments(postId, comments) {
    const listEl = document.getElementById(`comments-list-${postId}`);
    if (comments.length === 0) {
        listEl.innerHTML = '<p style="color:#bbb;font-size:.88rem;padding:.5rem 0">Chưa có bình luận nào.</p>';
        return;
    }
    listEl.innerHTML = comments.map(c => {
        const letter = avatarLetter(c.full_name || c.username);
        const canDel = currentUser &&
                       (currentUser.username === c.username || currentUser.is_admin);
        return `
            <div class="comment-item" id="comment-${c.id}">
                <div class="comment-avatar">
                    ${c.anh_dai_dien
                        ? `<img src="${esc(c.anh_dai_dien)}" onerror="this.parentElement.textContent='${letter}'">`
                        : letter}
                </div>
                <div class="comment-bubble">
                    ${canDel
                        ? `<button class="comment-del-btn"
                                   onclick="deleteComment(${c.id},${postId})">✕</button>`
                        : ''}
                    <div class="comment-author">${esc(c.full_name || c.username)}</div>
                    <div class="comment-text">${esc(c.content)}</div>
                    <div class="comment-time">${formatTime(c.created_at)}</div>
                </div>
            </div>`;
    }).join('');
}

async function submitComment(postId) {
    const input   = document.getElementById(`comment-input-${postId}`);
    const content = (input.value || '').trim();
    if (!content) return;

    const btn = input.nextElementSibling;
    btn.disabled = true;

    try {
        const res  = await fetch(`/api/forum/posts/${postId}/comments`, {
            method: 'POST', credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
        const data = await res.json();
        if (data.success) {
            input.value = '';
            await loadComments(postId);
            // update comment count display
            const toggleBtn = document.querySelector(`#post-${postId} .comment-toggle-btn`);
            if (toggleBtn) {
                const countRes  = await fetch(`/api/forum/posts/${postId}`, { credentials: 'include' });
                const countData = await countRes.json();
                if (countData.success) {
                    const cnt = countData.data.comment_count || 0;
                    toggleBtn.textContent = `💬 ${cnt > 0 ? cnt + ' bình luận' : 'Bình luận'}`;
                }
            }
        } else {
            alert(data.error);
        }
    } catch (err) { alert('Lỗi kết nối'); }
    finally { btn.disabled = false; }
}

function handleCommentKey(e, postId) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submitComment(postId);
    }
}

async function deleteComment(commentId, postId) {
    if (!confirm('Xóa bình luận này?')) return;
    try {
        await fetch(`/api/forum/comments/${commentId}`, {
            method: 'DELETE', credentials: 'include'
        });
        await loadComments(postId);
    } catch (err) { alert('Lỗi khi xóa'); }
}

// ===== DELETE POST =====
async function deletePost(postId) {
    if (!confirm('Bạn có chắc muốn xóa bài viết này?')) return;
    try {
        const res  = await fetch(`/api/forum/posts/${postId}`, {
            method: 'DELETE', credentials: 'include'
        });
        const data = await res.json();
        if (data.success) {
            const el = document.getElementById(`post-${postId}`);
            if (el) { el.style.animation = 'fadeUp .3s reverse'; setTimeout(() => el.remove(), 280); }
        } else {
            alert(data.error);
        }
    } catch (err) { alert('Lỗi khi xóa'); }
}

// ===== CREATE POST MODAL =====
function openPostModal(presetTagType = '') {
    if (!currentUser) { window.location.href = '/login'; return; }
    const modal = document.getElementById('postModal');
    modal.style.display = 'flex';

    document.getElementById('postTitle').value   = '';
    document.getElementById('postContent').value = '';
    document.getElementById('tagType').value     = presetTagType;
    document.getElementById('tagName').value     = '';
    document.getElementById('modalError').textContent = '';
    document.getElementById('charCount').textContent  = '0';
    onTagTypeChange();

    document.getElementById('postContent').focus();
}

function closePostModal() {
    document.getElementById('postModal').style.display = 'none';
}

function closePostModalOutside(e) {
    if (e.target === document.getElementById('postModal')) closePostModal();
}

function onTagTypeChange() {
    const val  = document.getElementById('tagType').value;
    const inp  = document.getElementById('tagName');
    inp.style.display = val ? 'block' : 'none';
    inp.placeholder   = val === 'tac_pham' ? 'Tên tác phẩm...' : 'Tên tác giả...';
}

function updateCharCount() {
    const len = (document.getElementById('postContent').value || '').length;
    const el  = document.getElementById('charCount');
    el.textContent = len;
    el.style.color = len > 1900 ? '#e74c3c' : '#aaa';
}

async function submitPost() {
    const content = (document.getElementById('postContent').value || '').trim();
    const title   = (document.getElementById('postTitle').value  || '').trim();
    const tagType = document.getElementById('tagType').value;
    const tagName = (document.getElementById('tagName').value || '').trim();
    const errEl   = document.getElementById('modalError');
    const btn     = document.getElementById('submitBtn');

    errEl.textContent = '';
    if (!content) { errEl.textContent = '⚠️ Nội dung không được để trống'; return; }
    if (content.length > 2000) { errEl.textContent = '⚠️ Tối đa 2000 ký tự'; return; }

    btn.disabled    = true;
    btn.textContent = '⏳ Đang đăng...';

    try {
        const res  = await fetch('/api/forum/posts', {
            method: 'POST', credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content, title, tag_type: tagType, tag_name: tagName })
        });
        const data = await res.json();

        if (data.success) {
            closePostModal();
            // Xóa empty placeholder nếu có
            const feed    = document.getElementById('postsFeed');
            const emptyEl = feed.querySelector('.empty-feed');
            if (emptyEl) emptyEl.remove();
            // Prepend: tạm thêm vào cuối rồi move lên đầu
            appendPostCard(data.data);
            const newCard = document.getElementById(`post-${data.data.id}`);
            if (newCard) feed.insertBefore(newCard, feed.firstChild);
        } else {
            errEl.textContent = '❌ ' + data.error;
        }
    } catch (err) {
        errEl.textContent = '❌ Lỗi kết nối';
    } finally {
        btn.disabled    = false;
        btn.textContent = '🚀 Đăng bài';
    }
}

// ===== TABS & FILTERS =====
function switchTab(btn, tab) {
    document.querySelectorAll('.feed-tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentTab   = tab;
    activeTagType = null;
    activeTagName = null;
    loadPosts(true);
}

function filterByTag(tagType, tagName) {
    activeTagType = tagType;
    activeTagName = tagName;
    // reset tabs
    document.querySelectorAll('.feed-tab').forEach(b => b.classList.remove('active'));
    loadPosts(true);
    window.scrollTo({ top: document.querySelector('.forum-main').offsetTop - 80, behavior: 'smooth' });
}

// ===== EXPAND / COLLAPSE =====
function toggleExpand(contentId, btn) {
    const el = document.getElementById(contentId);
    if (el.classList.contains('collapsed')) {
        el.classList.remove('collapsed');
        btn.textContent = 'Thu gọn ▲';
    } else {
        el.classList.add('collapsed');
        btn.textContent = 'Xem thêm ▼';
    }
}

// ===== STATS =====
async function loadStats() {
    try {
        const res = await fetch('/api/forum/stats');
        const data = await res.json();

        if (data.success) {
            document.getElementById('statPosts').textContent =
                data.data.posts;

            document.getElementById('statComments').textContent =
                data.data.comments;
        }

    } catch (err) {
        console.error(err);
    }
}
// ===== HELPERS =====
function avatarLetter(name) {
    if (!name) return '?';
    return name.trim()[0].toUpperCase();
}

function esc(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
function goToTacPham(ten) {
    window.location.href =
        '/tac-pham/' + encodeURIComponent(ten);
}

function goToTacGia(ten) {
    window.location.href =
        '/tac-gia/' + encodeURIComponent(ten);
}
function formatTime(ms) {
    if (!ms) return '';
    const now  = Date.now();
    const diff = now - ms;
    if (diff < 60000)    return 'Vừa xong';
    if (diff < 3600000)  return Math.floor(diff / 60000) + ' phút trước';
    if (diff < 86400000) return Math.floor(diff / 3600000) + ' giờ trước';
    if (diff < 604800000)return Math.floor(diff / 86400000) + ' ngày trước';
    return new Date(ms).toLocaleDateString('vi-VN');
}