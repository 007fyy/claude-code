// ── 登录状态管理 ──────────────────────────────────────────
// 用 localStorage key: "ls_user" = { name, phone, avatar? }
// 供所有页面 initNav() 调用

const LS_KEY = 'ls_user';

function lsGetUser()  { try { return JSON.parse(localStorage.getItem(LS_KEY)); } catch { return null; } }
function lsSetUser(u) { localStorage.setItem(LS_KEY, JSON.stringify(u)); }
function lsLogout()   { localStorage.removeItem(LS_KEY); location.href = 'index.html'; }

// ── 导航栏动态渲染 ─────────────────────────────────────────
function initNav() {
  const user = lsGetUser();

  // 找到所有指向 login.html 的导航按钮（各页面可能是 nav-user-btn 或 nav-icon-btn）
  const loginLinks = document.querySelectorAll('.nav a[href="login.html"]');

  loginLinks.forEach(el => {
    if (!user) return; // 未登录保持原样

    el.href = 'profile.html';
    const initial = (user.name || '我').charAt(0);
    const avatarHtml = `<span style="width:26px;height:26px;border-radius:50%;background:var(--gold,#C4906A);display:inline-flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:11px;flex-shrink:0;">${initial}</span>`;

    if (el.classList.contains('nav-user-btn')) {
      el.innerHTML = `${avatarHtml} <span>${user.name}</span>`;
    } else {
      // icon-only 样式（profile、orders 等页面的右上角圆形按钮）
      el.innerHTML = avatarHtml;
      el.style.width  = 'auto';
      el.style.padding = '4px';
    }
  });
}

// ── 当前页导航高亮 ─────────────────────────────────────────
function initNavActive() {
  const page = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(a => {
    a.classList.remove('active');
    const href = a.getAttribute('href') || '';
    // 精确匹配文件名（忽略 query string）
    const hPage = href.split('?')[0].split('/').pop();
    if (hPage === page) a.classList.add('active');
  });
  // 首页特殊处理：产品列表页也高亮"商品"下拉
  if (page === 'products.html') {
    const dropTrigger = document.querySelector('.has-drop > a');
    if (dropTrigger) dropTrigger.classList.add('active');
  }
}

// ── 退出登录（供 profile 等页面调用）─────────────────────────
function logout() {
  lsLogout();
}

// ── 自动执行 ──────────────────────────────────────────────
function _sharedInit() {
  initNav();
  initNavActive();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', _sharedInit);
} else {
  _sharedInit();
}
