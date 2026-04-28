/**
 * products.js  —  珑饰商品列表动态渲染
 *
 * 职责：fetch jewelry.json → 过滤/排序 → 生成卡片 HTML → 注入网格
 * 不依赖任何第三方库，纯原生 JS（ES2020）。
 */

// ════════════════════════════════════════════════════
// 1. 配置
// ════════════════════════════════════════════════════

const JSON_URL   = '../jewelry.json'   // 相对于 prototype-pc/
const DETAIL_URL = 'product.html'      // 详情页（?id=N 传参）

/** 各分类的占位背景色和 emoji（图片路径未就绪时显示） */
const PLACEHOLDER = {
  earring:  { bg: 'linear-gradient(135deg,#F5EDE3,#EDE0CE)', emoji: '💫' },
  necklace: { bg: 'linear-gradient(135deg,#F0ECF5,#E4DCF0)', emoji: '✨' },
  bracelet: { bg: 'linear-gradient(135deg,#EAF0F5,#D8E4F5)', emoji: '💎' },
  hairpin:  { bg: 'linear-gradient(135deg,#EAF5EA,#D8F0D8)', emoji: '🌸' },
  brooch:   { bg: 'linear-gradient(135deg,#F5F0E8,#EDE8DC)', emoji: '🔮' },
}

/** 风格标签的聚合映射（前端显示名 → JSON 里的 style_tags 值） */
const STYLE_MAP = {
  '简约精致': ['简约精致', '简约极简', '气质百搭'],
  '优雅复古': ['优雅复古', '法式轻奢', '气质通勤'],
  '甜美少女': ['甜美少女', '仙气飘飘', '浪漫春意'],
  '个性潮酷': ['个性先锋', 'ins风', '小众设计'],
}

/** 分类中文名映射 */
const CATEGORY_LABEL = {
  earring: '耳饰', necklace: '项链',
  bracelet: '手链', hairpin: '发饰', brooch: '胸针',
}


// ════════════════════════════════════════════════════
// 2. 纯函数：数据计算
// ════════════════════════════════════════════════════

/** 从 SKU 数组计算最低价和最高价 */
function calcPriceRange(skus) {
  const prices = skus.map(s => s.price)
  return { min: Math.min(...prices), max: Math.max(...prices) }
}

/** 格式化价格区间："89" 或 "89 – 198" */
function formatPrice(min, max) {
  return min === max ? String(min) : `${min} – ${max}`
}

/** 取 SKU 里最高的原价（用于划线价显示） */
function calcOriginalPrice(skus) {
  const origs = skus.map(s => s.original_price).filter(Boolean)
  return origs.length ? Math.max(...origs) : null
}

/** 检查商品是否落在价格区间内（区间格式 "lo-hi"，hi=Infinity 用 999999 表示） */
function inPriceRange(skus, rangeStr) {
  const [lo, hi] = rangeStr.split('-').map(Number)
  const { min, max } = calcPriceRange(skus)
  return min <= hi && max >= lo
}


// ════════════════════════════════════════════════════
// 3. 纯函数：过滤 & 排序
// ════════════════════════════════════════════════════

/**
 * 根据 state 过滤商品列表。
 * 多个筛选条件之间是 AND，同一条件内多选是 OR。
 */
function applyFilters(goods, state) {
  return goods.filter(item => {
    // 分类 OR
    if (state.categories.size > 0 && !state.categories.has(item.category)) return false

    // 价格 OR
    if (state.priceRanges.size > 0) {
      const ok = [...state.priceRanges].some(r => inPriceRange(item.skus, r))
      if (!ok) return false
    }

    // 风格 OR（通过 STYLE_MAP 将前端标签映射到 JSON tags）
    if (state.styles.size > 0) {
      const ok = [...state.styles].some(displayLabel => {
        const jsonTags = STYLE_MAP[displayLabel] || [displayLabel]
        return item.style_tags.some(t => jsonTags.includes(t))
      })
      if (!ok) return false
    }

    return true
  })
}

/** 排序，不修改原数组 */
function applySort(goods, sortKey) {
  const list = [...goods]
  if (sortKey === 'price_asc')  return list.sort((a, b) => calcPriceRange(a.skus).min - calcPriceRange(b.skus).min)
  if (sortKey === 'price_desc') return list.sort((a, b) => calcPriceRange(b.skus).min - calcPriceRange(a.skus).min)
  // 默认：按 sort_weight 降序（综合推荐）
  return list.sort((a, b) => (b.sort_weight ?? 0) - (a.sort_weight ?? 0))
}


// ════════════════════════════════════════════════════
// 4. 渲染：HTML 字符串生成
// ════════════════════════════════════════════════════

/**
 * 生成单张商品卡片的 HTML。
 * 完全复用 shared.css 里的 .product-card* 类，不引入新 CSS 规则。
 */
function renderCard(item) {
  const { min, max } = calcPriceRange(item.skus)
  const origPrice    = calcOriginalPrice(item.skus)
  const ph           = PLACEHOLDER[item.category] ?? PLACEHOLDER.earring
  const hasAR        = item.skus.some(s => s.ar_asset_url)

  // 图片区：有真实 URL 时用 <img>，否则用占位 emoji
  const isRealUrl  = item.cover_url && !item.cover_url.startsWith('/assets/')
  const imgContent = isRealUrl
    ? `<img src="${item.cover_url}" alt="${item.name}" style="width:100%;height:100%;object-fit:cover;">`
    : `<span style="font-size:52px;line-height:1;">${ph.emoji}</span>`

  // 试戴徽章（有 AR 素材才显示）
  const tryBadge = hasAR ? `<div class="try-badge">📷 试戴</div>` : ''

  // 划线价
  const origHTML = origPrice
    ? `<span class="price-old">¥${origPrice}</span>`
    : ''

  // 风格标签（最多 2 个，避免卡片撑高）
  const tagChips = item.style_tags.slice(0, 2)
    .map(t => `<span class="js-tag-chip">${t}</span>`)
    .join('')

  return `
<div class="product-card" onclick="goToDetail(${item.id})">
  <div class="product-card-img" style="background:${ph.bg};">
    ${imgContent}
    ${tryBadge}
  </div>
  <div class="product-card-body">
    <div class="product-card-name">${item.name}</div>
    <div class="product-card-sub">${CATEGORY_LABEL[item.category] ?? item.category} · ${item.material}</div>
    <div class="product-card-price">
      <span class="price-unit">¥</span>
      <span class="price-main">${formatPrice(min, max)}</span>
      ${origHTML}
    </div>
    <div class="product-card-meta" style="gap:4px;flex-wrap:wrap;margin-bottom:10px;">
      ${tagChips}
    </div>
    <div class="product-card-actions">
      <a href="ar.html?id=${item.id}"
         class="btn btn-out btn-sm"
         onclick="event.stopPropagation()">📷 试戴</a>
      <button class="btn btn-dark btn-sm"
              style="flex:1;"
              onclick="event.stopPropagation();addToCart(${item.id})">加购</button>
    </div>
  </div>
</div>`
}

/** 将渲染好的卡片列表注入网格，并同步结果数量 */
function renderGrid(items) {
  const grid     = document.getElementById('product-grid')
  const countEl  = document.getElementById('result-count')
  if (!grid) return

  if (items.length === 0) {
    grid.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;padding:60px 20px;color:var(--t3);">
        <div style="font-size:48px;margin-bottom:14px;">🔍</div>
        <div style="font-size:15px;font-weight:600;">没有找到符合条件的商品</div>
        <div style="font-size:13px;margin-top:8px;">
          调整筛选条件，或让 <a href="guide.html" style="color:var(--gold);font-weight:600;">AI 帮你选 →</a>
        </div>
      </div>`
  } else {
    grid.innerHTML = items.map(renderCard).join('')
  }

  if (countEl) {
    countEl.textContent = `共 ${items.length} 件商品`
  }
}

/** 点击卡片跳转详情页，携带商品 ID */
function goToDetail(id) {
  window.location.href = `${DETAIL_URL}?id=${id}`
}

/** 加购占位（后续对接购物车接口时替换） */
function addToCart(id) {
  // TODO: 调用 /api/v1/cart/add  { sku_id: defaultSkuId }
  const item = allGoods.find(g => g.id === id)
  if (!item) return
  const btn = event.currentTarget
  btn.textContent = '✓ 已加购'
  btn.disabled = true
  setTimeout(() => { btn.textContent = '加购'; btn.disabled = false }, 1500)
}


// ════════════════════════════════════════════════════
// 5. 状态管理 & 事件绑定
// ════════════════════════════════════════════════════

let allGoods = []   // 原始数据，fetch 后不再修改

const state = {
  categories:  new Set(),   // 选中的分类值（'earring' / 'necklace' …）
  priceRanges: new Set(),   // 选中的价格区间字符串（'0-50' / '50-200' …）
  styles:      new Set(),   // 选中的风格显示名（'优雅复古' …）
  sortKey:     'default',
}

/** 重新过滤、排序并渲染 */
function refresh() {
  const filtered = applyFilters(allGoods, state)
  const sorted   = applySort(filtered, state.sortKey)
  renderGrid(sorted)
}

function bindFilters() {
  // ── 分类复选框 ──
  document.querySelectorAll('[data-filter="category"]').forEach(cb => {
    if (cb.checked) state.categories.add(cb.dataset.value)
    cb.addEventListener('change', () => {
      cb.checked
        ? state.categories.add(cb.dataset.value)
        : state.categories.delete(cb.dataset.value)
      refresh()
    })
  })

  // ── 价格复选框 ──
  document.querySelectorAll('[data-filter="price"]').forEach(cb => {
    if (cb.checked) state.priceRanges.add(cb.dataset.value)
    cb.addEventListener('change', () => {
      cb.checked
        ? state.priceRanges.add(cb.dataset.value)
        : state.priceRanges.delete(cb.dataset.value)
      refresh()
    })
  })

  // ── 风格复选框 ──
  document.querySelectorAll('[data-filter="style"]').forEach(cb => {
    if (cb.checked) state.styles.add(cb.dataset.value)
    cb.addEventListener('change', () => {
      cb.checked
        ? state.styles.add(cb.dataset.value)
        : state.styles.delete(cb.dataset.value)
      refresh()
    })
  })

  // ── 排序按钮 ──
  document.querySelectorAll('[data-sort]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-sort]').forEach(b => b.classList.remove('active'))
      btn.classList.add('active')
      state.sortKey = btn.dataset.sort
      refresh()
    })
  })

  // ── 清除全部筛选 ──
  document.querySelector('.filter-clear')?.addEventListener('click', () => {
    state.categories.clear()
    state.priceRanges.clear()
    state.styles.clear()
    document.querySelectorAll('[data-filter]').forEach(cb => { cb.checked = false })
    refresh()
  })
}


// ════════════════════════════════════════════════════
// 6. 入口：DOMContentLoaded
// ════════════════════════════════════════════════════

async function init() {
  // 显示加载占位
  const grid = document.getElementById('product-grid')
  if (grid) {
    grid.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--t3);">
        <div style="font-size:36px;margin-bottom:12px;">⏳</div>加载中...
      </div>`
  }

  // 拉取数据
  try {
    const res  = await fetch(JSON_URL)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    allGoods   = data.goods ?? []
  } catch (err) {
    console.error('[products.js] 数据加载失败:', err)
    if (grid) {
      grid.innerHTML = `
        <div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--red);">
          ⚠️ 数据加载失败，请确认 jewelry.json 路径正确<br>
          <small style="color:var(--t3);margin-top:8px;display:block;">
            (fetch 需要 HTTP 服务器，不能直接双击打开 HTML 文件)
          </small>
        </div>`
    }
    return
  }

  bindFilters()
  refresh()   // 首次渲染，应用初始选中状态
}

document.addEventListener('DOMContentLoaded', init)
