/**
 * detail.js  —  珑饰商品详情页数据驱动层
 *
 * 职责：
 *   1. 从 URL 解析 id
 *   2. 拉取 jewelry.json，定位对应 SPU
 *   3. 渲染页面各区域（标题/价格/图片/属性/SKU）
 *   4. SKU 点击联动（价格、库存、AR 参数）
 *   5. 维护 window.currentAR 全局对象，供 AR 页读取
 *
 * 与 product.html 内联 <script> 的分工：
 *   内联脚本负责：changeQty / toggleWish / addToCart / switchTab / showToast
 *   本文件负责：所有数据渲染 + SKU 交互
 */

// ════════════════════════════════════════════════════
// 1. 配置
// ════════════════════════════════════════════════════

const JSON_URL = '../jewelry.json'

/** 颜色名 → 色值（用于 SKU 按钮的小圆点） */
const COLOR_DOT = {
  '银色':  '#C0C0C0',
  '金色':  '#D4AF37',
  '玫瑰金':'#E8A99A',
  '白色':  '#F5F5F0',
  '紫色':  '#9B7FBF',
  '白蓝':  '#A8C5DA',
  '黑色':  '#3A3A3A',
  '红色':  '#C0392B',
}

/** 挂载点中文名 */
const MOUNT_LABEL = {
  ear_lobe: '耳垂', ear_top: '耳上方',
  neck: '颈部', hair: '发部', wrist: '手腕',
}

/** 分类中文名 */
const CATEGORY_LABEL = {
  earring: '耳饰', necklace: '项链',
  bracelet: '手链', hairpin: '发饰', brooch: '胸针',
}

/** 各分类的占位图（无真实图时显示） */
const PLACEHOLDER_EMOJI = {
  earring: '💫', necklace: '✨', bracelet: '💎',
  hairpin: '🌸', brooch: '🔮',
}


// ════════════════════════════════════════════════════
// 2. 全局 AR 状态（供 ar.html 或后续 JS 读取）
// ════════════════════════════════════════════════════

/**
 * window.currentAR 结构：
 * {
 *   spu_id:            number,
 *   sku_name:          string,
 *   mount_type:        string,   // 'ear_lobe' | 'neck' | ...
 *   ar_asset_url:      string,
 *   ar_scale_base:     number,
 *   ar_offset_x:       number,
 *   ar_offset_y:       number,
 *   ar_rotation_offset:number,
 * }
 */
window.currentAR = null


// ════════════════════════════════════════════════════
// 3. 工具函数
// ════════════════════════════════════════════════════

/** 从 URL 读取 ?id=N，返回数字，解析失败返回 null */
function parseIdFromUrl() {
  const raw = new URLSearchParams(location.search).get('id')
  const n   = parseInt(raw, 10)
  return Number.isFinite(n) ? n : null
}

/** 根据当前选中 SKU 拼接 AR 页跳转 URL */
function buildARUrl(spu, sku) {
  const p = new URLSearchParams({
    spu_id:             spu.id,
    sku_name:           sku.sku_name,
    mount_type:         spu.mount_type,
    ar_asset_url:       sku.ar_asset_url ?? '',
    ar_scale_base:      sku.ar_scale_base,
    ar_offset_x:        sku.ar_offset_x,
    ar_offset_y:        sku.ar_offset_y,
    ar_rotation_offset: sku.ar_rotation_offset,
  })
  return `ar.html?${p.toString()}`
}

/** 格式化价格，保留整数位 */
function fmt(n) { return Number(n).toLocaleString('zh-CN', { maximumFractionDigits: 0 }) }


// ════════════════════════════════════════════════════
// 4. 页面渲染（静态内容区）
// ════════════════════════════════════════════════════

function renderStatic(spu) {
  const catLabel = CATEGORY_LABEL[spu.category] ?? spu.category
  const emoji    = PLACEHOLDER_EMOJI[spu.category] ?? '💎'

  // ── 页面标题 & 面包屑 ──
  document.title = `${spu.name} — 珑饰 LongShi`
  const cur = document.querySelector('.breadcrumb .cur')
  if (cur) cur.textContent = spu.name

  // ── 主标题 & 副标题 ──
  const titleEl = document.querySelector('.pd-title')
  if (titleEl) titleEl.textContent = spu.name

  const subEl = document.querySelector('.pd-subtitle')
  if (subEl) {
    subEl.textContent = `${catLabel} · ${spu.material}` +
      (spu.description ? ` · ${spu.description.slice(0, 40)}…` : '')
  }

  // ── 主图区（占位 emoji，有真实图时换 <img>） ──
  const imgBox = document.querySelector('.pd-main-img')
  if (imgBox) {
    const isRealUrl = spu.cover_url && !spu.cover_url.startsWith('/assets/')
    // 清除子节点，保留 .img-tag 和 .ar-cta-float
    const imgTag   = imgBox.querySelector('.img-tag')
    const arCta    = imgBox.querySelector('.ar-cta-float')
    imgBox.innerHTML = ''

    if (isRealUrl) {
      const img = document.createElement('img')
      img.src   = spu.cover_url
      img.alt   = spu.name
      img.style.cssText = 'width:100%;height:100%;object-fit:cover;'
      imgBox.appendChild(img)
    } else {
      const span = document.createElement('span')
      span.textContent = emoji
      span.style.cssText = 'font-size:120px;filter:drop-shadow(0 8px 24px rgba(196,144,106,.3));'
      imgBox.appendChild(span)
    }
    if (imgTag) imgBox.appendChild(imgTag)
    if (arCta)  imgBox.appendChild(arCta)
  }

  // ── AI 匹配说明 ──
  const matchReason = document.querySelector('.pd-match-reason')
  if (matchReason && spu.target_face_shapes?.length) {
    const faceNames = { oval:'椭圆形', round:'圆形', square:'方形', heart:'心形', oblong:'长形', diamond:'菱形' }
    const faces = spu.target_face_shapes.map(f => faceNames[f] ?? f).join('、')
    const occasions = (spu.occasion_tags ?? []).slice(0, 2).join('、')
    matchReason.textContent =
      `适合 ${faces} 脸型，风格标签：${spu.style_tags.slice(0,2).join('、')}` +
      (occasions ? `，适用场合：${occasions}` : '')
  }

  // ── 商品属性卡片（tab0 里的 pd-attrs） ──
  const attrsEl = document.querySelector('.pd-attrs')
  if (attrsEl) {
    attrsEl.innerHTML = `
      <div class="pd-attr"><span class="ic">🏷️</span><div>
        <div class="pd-attr-key">品类</div>
        <div class="pd-attr-val">${catLabel}</div>
      </div></div>
      <div class="pd-attr"><span class="ic">🔩</span><div>
        <div class="pd-attr-key">材质</div>
        <div class="pd-attr-val">${spu.material}</div>
      </div></div>
      <div class="pd-attr"><span class="ic">📍</span><div>
        <div class="pd-attr-key">佩戴位置</div>
        <div class="pd-attr-val">${MOUNT_LABEL[spu.mount_type] ?? spu.mount_type}</div>
      </div></div>
      <div class="pd-attr"><span class="ic">✨</span><div>
        <div class="pd-attr-key">风格标签</div>
        <div class="pd-attr-val">${spu.style_tags.join(' · ')}</div>
      </div></div>
      <div class="pd-attr"><span class="ic">🌸</span><div>
        <div class="pd-attr-key">适用场合</div>
        <div class="pd-attr-val">${(spu.occasion_tags ?? []).join(' · ') || '全场合'}</div>
      </div></div>
      <div class="pd-attr"><span class="ic">😊</span><div>
        <div class="pd-attr-key">推荐脸型</div>
        <div class="pd-attr-val">${spu.target_face_shapes?.map(f =>
          ({oval:'椭圆',round:'圆',square:'方',heart:'心形',oblong:'长',diamond:'菱'})[f] ?? f
        ).join('、') || '通用'}</div>
      </div></div>
    `
  }
}


// ════════════════════════════════════════════════════
// 5. SKU 渲染
// ════════════════════════════════════════════════════

function renderSkus(spu) {
  // 找到所有 pd-sku-section，全部替换为一个"颜色/规格"区块
  const existing = document.querySelectorAll('.pd-sku-section')
  if (!existing.length || !spu.skus?.length) return

  // 以第一个 sku-section 为锚点，在其前插入新块，然后删除所有旧块
  const anchor = existing[0]
  const parent = anchor.parentNode

  const section = document.createElement('div')
  section.className = 'pd-sku-section'
  section.id = 'js-sku-section'
  section.innerHTML = `
    <div class="pd-sku-label">
      颜色 / 规格
      <span class="selected-val" id="js-sku-selected">—</span>
    </div>
    <div class="pd-sku-options" id="js-sku-options"></div>
  `
  parent.insertBefore(section, anchor)
  existing.forEach(el => el.remove())

  // 生成按钮
  const optionsEl = document.getElementById('js-sku-options')
  spu.skus.forEach((sku, idx) => {
    const dotColor = COLOR_DOT[sku.color] ?? '#CCCCCC'
    const btn = document.createElement('button')
    btn.className   = 'pd-sku-btn' + (sku.stock === 0 ? ' disabled' : '')
    btn.dataset.idx = idx
    btn.innerHTML   = `
      <span class="pd-color-dot" style="background:${dotColor};border:1px solid rgba(0,0,0,.12);"></span>
      ${sku.color || sku.sku_name}
      ${sku.stock === 0 ? '<span style="font-size:10px;color:var(--t3);margin-left:4px;">缺货</span>' : ''}
    `
    if (sku.stock > 0) {
      btn.addEventListener('click', () => selectSku(spu, idx))
    }
    optionsEl.appendChild(btn)
  })

  // 默认选中第一个有货的 SKU
  const firstAvail = spu.skus.findIndex(s => s.stock > 0)
  selectSku(spu, firstAvail >= 0 ? firstAvail : 0)
}


// ════════════════════════════════════════════════════
// 6. SKU 选中联动（核心）
// ════════════════════════════════════════════════════

function selectSku(spu, idx) {
  const sku = spu.skus[idx]
  if (!sku) return

  // ── 更新按钮激活态 ──
  document.querySelectorAll('#js-sku-options .pd-sku-btn').forEach((btn, i) => {
    btn.classList.toggle('active', i === idx)
  })

  // ── 更新已选显示 ──
  const selectedEl = document.getElementById('js-sku-selected')
  if (selectedEl) selectedEl.textContent = sku.sku_name

  // ── 更新价格区域 ──
  const priceNow  = document.querySelector('.pd-price-now')
  const priceOld  = document.querySelector('.pd-price-old')
  const priceSave = document.querySelector('.pd-price-save')

  if (priceNow) priceNow.innerHTML = `<span>¥</span>${fmt(sku.price)}`

  if (priceOld) {
    if (sku.original_price && sku.original_price > sku.price) {
      priceOld.textContent = `¥${fmt(sku.original_price)}`
      priceOld.style.display = ''
    } else {
      priceOld.style.display = 'none'
    }
  }

  if (priceSave) {
    if (sku.original_price && sku.original_price > sku.price) {
      const saved = Math.round(sku.original_price - sku.price)
      priceSave.textContent = `省 ¥${fmt(saved)}`
      priceSave.style.display = ''
    } else {
      priceSave.style.display = 'none'
    }
  }

  // ── 更新库存提示 ──
  const stockHint = document.querySelector('.pd-stock-hint')
  if (stockHint) {
    if (sku.stock === 0) {
      stockHint.innerHTML = '<strong style="color:var(--red);">暂时缺货</strong>'
    } else if (sku.stock <= 10) {
      stockHint.innerHTML = `库存 <strong>仅剩 ${sku.stock} 件</strong>`
    } else {
      stockHint.innerHTML = `库存充足 (${sku.stock} 件)`
    }
    // 同步 qty 输入框的 max
    const qtyInput = document.getElementById('qty')
    if (qtyInput) qtyInput.max = Math.min(sku.stock, 99)
  }

  // ── 存入全局 AR 状态 ──
  window.currentAR = {
    spu_id:             spu.id,
    sku_name:           sku.sku_name,
    mount_type:         spu.mount_type,
    ar_asset_url:       sku.ar_asset_url ?? '',
    ar_scale_base:      sku.ar_scale_base ?? 1,
    ar_offset_x:        sku.ar_offset_x  ?? 0,
    ar_offset_y:        sku.ar_offset_y  ?? 0,
    ar_rotation_offset: sku.ar_rotation_offset ?? 0,
  }

  // ── 更新 AR 试戴按钮的跳转链接 ──
  const arCta = document.querySelector('.ar-cta-float')
  if (arCta) arCta.href = buildARUrl(spu, sku)

  // ── 控制"AR 可试戴"标签显示 ──
  const imgTag = document.querySelector('.pd-main-img .img-tag')
  if (imgTag) imgTag.style.display = sku.ar_asset_url ? '' : 'none'
}


// ════════════════════════════════════════════════════
// 7. 错误页渲染
// ════════════════════════════════════════════════════

function renderNotFound(reason) {
  const wrap = document.querySelector('.pd-wrap')
  if (wrap) {
    wrap.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;padding:80px 20px;color:var(--t3);">
        <div style="font-size:64px;margin-bottom:20px;">🔍</div>
        <h2 style="font-size:20px;font-weight:700;color:var(--dark);margin-bottom:10px;">
          找不到该商品
        </h2>
        <p style="font-size:14px;margin-bottom:24px;">${reason}</p>
        <a href="products.html" class="btn btn-dark">← 返回商品列表</a>
      </div>`
  }
}


// ════════════════════════════════════════════════════
// 8. 入口
// ════════════════════════════════════════════════════

async function init() {
  // 1. 解析 ID
  const id = parseIdFromUrl()
  if (!id) {
    renderNotFound('URL 中缺少商品 ID（?id=1）')
    return
  }

  // 2. 拉取数据
  let spu
  try {
    const res  = await fetch(JSON_URL)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    spu = data.goods.find(g => g.id === id)
  } catch (err) {
    console.error('[detail.js] 数据加载失败:', err)
    renderNotFound('数据加载失败，请确认服务器已启动（fetch 需要 HTTP 服务器）')
    return
  }

  if (!spu) {
    renderNotFound(`未找到 ID=${id} 的商品，请检查 jewelry.json`)
    return
  }

  // 3. 渲染
  renderStatic(spu)   // 标题、图片、描述、属性
  renderSkus(spu)     // SKU 选择按钮 + 初始选中
}

document.addEventListener('DOMContentLoaded', init)
