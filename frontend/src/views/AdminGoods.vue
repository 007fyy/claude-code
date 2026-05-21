<template>
  <div class="admin-goods-page">
    <div class="page-header">
      <h1 class="page-title"><span>✦</span> 商品管理</h1>
    </div>

    <el-tabs v-model="activeTab" class="goods-tabs">
      <!-- ── Tab 1: 商品列表 ── -->
      <el-tab-pane label="商品列表" name="list">
        <div class="toolbar">
          <el-button type="primary" @click="openSpuDialog()">+ 新增商品</el-button>
          <el-select v-model="filterCat" placeholder="全部分类" clearable style="width:140px" @change="loadGoods">
            <el-option v-for="c in categories" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </div>

        <el-table :data="spus" v-loading="loading" border stripe class="goods-table">
          <el-table-column label="封面" width="72">
            <template #default="{ row }">
              <el-image :src="row.cover_url" fit="cover" style="width:48px;height:48px;border-radius:6px">
                <template #error><div class="img-err">📷</div></template>
              </el-image>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="商品名" min-width="180" show-overflow-tooltip />
          <el-table-column label="分类" width="90">
            <template #default="{ row }">{{ catLabel(row.category) }}</template>
          </el-table-column>
          <el-table-column label="挂载" width="90">
            <template #default="{ row }">{{ mountLabel(row.mount_type) }}</template>
          </el-table-column>
          <el-table-column label="SKU数" width="72" align="center">
            <template #default="{ row }">{{ row.skus.length }}</template>
          </el-table-column>
          <el-table-column label="状态" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
                {{ row.status === 1 ? '上架' : '下架' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" align="center">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="openSpuDialog(row)">编辑</el-button>
              <el-button link size="small" @click="openSkuDialog(row)">SKU</el-button>
              <el-button link :type="row.status === 1 ? 'danger' : 'success'" size="small"
                @click="toggleStatus(row)">
                {{ row.status === 1 ? '下架' : '上架' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- ── Tab 2: AR素材 ── -->
      <el-tab-pane label="AR素材配置" name="ar">
        <div class="ar-layout">
          <div class="spu-panel">
            <div class="panel-hd">选择商品</div>
            <div class="spu-list">
              <div v-for="spu in spus" :key="spu.spu_id"
                class="spu-item" :class="{ active: arSelected?.spu_id === spu.spu_id }"
                @click="arSelected = spu">
                <el-image :src="spu.cover_url" fit="cover" class="spu-thumb">
                  <template #error><div class="img-err">📷</div></template>
                </el-image>
                <div class="spu-info">
                  <div class="spu-name">{{ spu.name }}</div>
                  <div class="spu-meta">
                    <el-tag size="small" type="info">{{ catLabel(spu.category) }}</el-tag>
                    <el-tag v-if="spu.skus.some(s => s.ar_asset_url)" size="small" type="success">已配置</el-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="sku-panel">
            <el-empty v-if="!arSelected" description="请从左侧选择商品" style="margin-top:60px" />
            <template v-else>
              <div class="panel-hd">{{ arSelected.name }}</div>
              <div class="sku-cards">
                <div v-for="sku in arSelected.skus" :key="sku.sku_id" class="sku-card">
                  <div class="sku-card-hd">
                    <span class="sku-name">{{ sku.sku_name }}</span>
                    <el-tag :type="sku.ar_asset_url ? 'success' : 'info'" size="small">
                      {{ sku.ar_asset_url ? '已配置' : '未配置' }}
                    </el-tag>
                  </div>
                  <div class="sku-card-body">
                    <div class="ar-preview-col">
                      <div class="ar-preview-box">
                        <img v-if="sku.ar_asset_url" :src="sku.ar_asset_url" class="ar-preview-img" />
                        <div v-else class="ar-no-asset">暂无素材</div>
                      </div>
                      <el-button size="small" style="width:100%" :loading="uploading[sku.sku_id]" @click="triggerUpload(sku.sku_id)">
                        {{ sku.ar_asset_url ? '更换' : '上传PNG' }}
                      </el-button>
                      <el-button size="small" style="width:100%" @click="openPreset(sku)">预设库</el-button>
                    </div>
                    <div class="ar-params-col">
                      <div class="param-row"><label>X偏移</label><el-input-number v-model="sku.ar_offset_x" :step="1" size="small" controls-position="right" /></div>
                      <div class="param-row"><label>Y偏移</label><el-input-number v-model="sku.ar_offset_y" :step="1" size="small" controls-position="right" /></div>
                      <div class="param-row"><label>缩放</label><el-input-number v-model="sku.ar_scale_base" :step="0.05" :min="0.1" :max="5" :precision="2" size="small" controls-position="right" /></div>
                      <div class="param-row"><label>旋转°</label><el-input-number v-model="sku.ar_rotation_offset" :step="5" :min="-180" :max="180" size="small" controls-position="right" /></div>
                      <el-button type="primary" size="small" :loading="saving[sku.sku_id]" @click="saveParams(sku)">保存参数</el-button>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- SPU 新增/编辑 Dialog -->
    <el-dialog v-model="spuDialogVisible" :title="spuForm.spu_id ? '编辑商品' : '新增商品'" width="600px" destroy-on-close>
      <el-form :model="spuForm" label-width="80px" class="spu-form">
        <el-form-item label="商品名" required><el-input v-model="spuForm.name" /></el-form-item>
        <el-form-item label="分类" required>
          <el-select v-model="spuForm.category" style="width:100%">
            <el-option v-for="c in categories" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="挂载类型" required>
          <el-select v-model="spuForm.mount_type" style="width:100%">
            <el-option v-for="m in mountTypes" :key="m.value" :label="m.label" :value="m.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="材质"><el-input v-model="spuForm.material" /></el-form-item>
        <el-form-item label="封面URL"><el-input v-model="spuForm.cover_url" placeholder="https://..." /></el-form-item>
        <el-form-item label="描述"><el-input v-model="spuForm.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="风格标签"><el-input v-model="spuForm.style_tags_str" placeholder="逗号分隔，如：简约极简,优雅复古" /></el-form-item>
        <el-form-item label="场合标签"><el-input v-model="spuForm.occasion_tags_str" placeholder="逗号分隔" /></el-form-item>
        <el-form-item label="排序权重"><el-input-number v-model="spuForm.sort_weight" :min="0" /></el-form-item>

        <el-divider>SKU 列表</el-divider>
        <div v-for="(sku, i) in spuForm.skus" :key="i" class="sku-row">
          <el-input v-model="sku.sku_name" placeholder="规格名" style="flex:2" />
          <el-input-number v-model="sku.price" :min="0" :precision="2" placeholder="价格" style="flex:1" controls-position="right" />
          <el-input-number v-model="sku.stock" :min="0" placeholder="库存" style="flex:1" controls-position="right" />
          <el-button link type="danger" @click="spuForm.skus.splice(i,1)">删除</el-button>
        </div>
        <el-button link type="primary" @click="spuForm.skus.push({ sku_name:'', price:0, stock:0 })">+ 添加SKU</el-button>
      </el-form>
      <template #footer>
        <el-button @click="spuDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitSpu">保存</el-button>
      </template>
    </el-dialog>

    <!-- SKU 管理 Dialog -->
    <el-dialog v-model="skuDialogVisible" :title="`SKU管理 · ${skuDialogSpu?.name}`" width="560px" destroy-on-close>
      <el-table :data="skuDialogSpu?.skus" border size="small">
        <el-table-column prop="sku_name" label="规格名" />
        <el-table-column prop="price" label="价格" width="90" />
        <el-table-column prop="stock" label="库存" width="80" />
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEditSku(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDeleteSku(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-divider>添加新SKU</el-divider>
      <div class="sku-row">
        <el-input v-model="newSku.sku_name" placeholder="规格名" style="flex:2" />
        <el-input-number v-model="newSku.price" :min="0" :precision="2" placeholder="价格" style="flex:1" controls-position="right" />
        <el-input-number v-model="newSku.stock" :min="0" placeholder="库存" style="flex:1" controls-position="right" />
        <el-button type="primary" size="small" :loading="skuAdding" @click="handleAddSku">添加</el-button>
      </div>
    </el-dialog>

    <!-- 编辑单个SKU Dialog -->
    <el-dialog v-model="editSkuVisible" title="编辑SKU" width="400px" destroy-on-close>
      <el-form :model="editSkuForm" label-width="70px">
        <el-form-item label="规格名"><el-input v-model="editSkuForm.sku_name" /></el-form-item>
        <el-form-item label="价格"><el-input-number v-model="editSkuForm.price" :min="0" :precision="2" controls-position="right" /></el-form-item>
        <el-form-item label="库存"><el-input-number v-model="editSkuForm.stock" :min="0" controls-position="right" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editSkuVisible = false">取消</el-button>
        <el-button type="primary" :loading="skuSaving" @click="handleUpdateSku">保存</el-button>
      </template>
    </el-dialog>

    <!-- AR预设库 Dialog -->
    <el-dialog v-model="presetVisible" title="从预设库选择AR素材" width="680px">
      <div class="preset-grid">
        <div v-for="p in presets" :key="p.filename" class="preset-item" @click="applyPreset(p)">
          <img :src="p.ar_asset_url" class="preset-img" />
          <div class="preset-name">{{ p.name }}</div>
          <div class="preset-meta">{{ p.mount_type }}</div>
        </div>
      </div>
    </el-dialog>

    <input ref="fileRef" type="file" accept=".png,.webp" style="display:none" @change="onFile" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  adminListGoods, getArPresets, uploadArAsset, updateArParams,
  createSpu, updateSpu, toggleSpuStatus, createSku, updateSku, deleteSku,
} from '@/api/goods'

const loading = ref(false)
const submitting = ref(false)
const activeTab = ref('list')
const filterCat = ref('')
const spus = ref([])
const arSelected = ref(null)
const uploading = reactive({})
const saving = reactive({})
const fileRef = ref(null)
const currentSkuId = ref(null)
const presetVisible = ref(false)
const presets = ref([])
const presetTargetSku = ref(null)

const categories = [
  { value: 'earring', label: '耳饰' }, { value: 'necklace', label: '项链' },
  { value: 'bracelet', label: '手链' }, { value: 'ring', label: '戒指' },
]
const mountTypes = [
  { value: 'ear_lobe', label: '耳垂' }, { value: 'ear_top', label: '耳廓' },
  { value: 'neck', label: '颈部' }, { value: 'hair', label: '发饰' },
  { value: 'wrist', label: '手腕' }, { value: 'finger', label: '手指' },
]
const catLabel = (c) => categories.find(x => x.value === c)?.label || c
const mountLabel = (m) => mountTypes.find(x => x.value === m)?.label || m

async function loadGoods() {
  loading.value = true
  try {
    const res = await adminListGoods()
    spus.value = res.data
    if (arSelected.value)
      arSelected.value = spus.value.find(s => s.spu_id === arSelected.value.spu_id) || null
  } finally { loading.value = false }
}

// ── SPU Dialog ────────────────────────────────────────────────────────────────
const spuDialogVisible = ref(false)
const spuForm = reactive({
  spu_id: null, name: '', category: 'earring', mount_type: 'ear_lobe',
  material: '', cover_url: '', description: '',
  style_tags_str: '', occasion_tags_str: '', sort_weight: 0, skus: [],
})

function openSpuDialog(spu = null) {
  Object.assign(spuForm, {
    spu_id: spu?.spu_id || null, name: spu?.name || '',
    category: spu?.category || 'earring', mount_type: spu?.mount_type || 'ear_lobe',
    material: spu?.material || '', cover_url: spu?.cover_url || '',
    description: spu?.description || '',
    style_tags_str: (spu?.style_tags || []).join(','),
    occasion_tags_str: (spu?.occasion_tags || []).join(','),
    sort_weight: spu?.sort_weight || 0,
    skus: spu ? spu.skus.map(s => ({ sku_id: s.sku_id, sku_name: s.sku_name, price: s.price, stock: s.stock })) : [],
  })
  spuDialogVisible.value = true
}

async function submitSpu() {
  if (!spuForm.name || !spuForm.category) return ElMessage.warning('请填写商品名和分类')
  submitting.value = true
  try {
    const payload = {
      name: spuForm.name, category: spuForm.category, mount_type: spuForm.mount_type,
      material: spuForm.material, cover_url: spuForm.cover_url, description: spuForm.description,
      style_tags: spuForm.style_tags_str.split(',').map(s => s.trim()).filter(Boolean),
      occasion_tags: spuForm.occasion_tags_str.split(',').map(s => s.trim()).filter(Boolean),
      sort_weight: spuForm.sort_weight,
      skus: spuForm.skus.map(s => ({ sku_name: s.sku_name, price: s.price, stock: s.stock })),
    }
    if (spuForm.spu_id) { await updateSpu(spuForm.spu_id, payload); ElMessage.success('商品已更新') }
    else { await createSpu(payload); ElMessage.success('商品已创建') }
    spuDialogVisible.value = false
    loadGoods()
  } finally { submitting.value = false }
}

async function toggleStatus(spu) {
  const next = spu.status === 1 ? 0 : 1
  await ElMessageBox.confirm(`确认${next === 1 ? '上架' : '下架'}「${spu.name}」？`, '提示', { type: 'warning' })
  await toggleSpuStatus(spu.spu_id, next)
  ElMessage.success(next === 1 ? '已上架' : '已下架')
  loadGoods()
}

// ── SKU Dialog ────────────────────────────────────────────────────────────────
const skuDialogVisible = ref(false)
const skuDialogSpu = ref(null)
const newSku = reactive({ sku_name: '', price: 0, stock: 0 })
const skuAdding = ref(false)
const editSkuVisible = ref(false)
const editSkuForm = reactive({ sku_id: null, sku_name: '', price: 0, stock: 0 })
const skuSaving = ref(false)

function openSkuDialog(spu) {
  skuDialogSpu.value = spu
  Object.assign(newSku, { sku_name: '', price: 0, stock: 0 })
  skuDialogVisible.value = true
}

async function handleAddSku() {
  if (!newSku.sku_name) return ElMessage.warning('请填写规格名')
  skuAdding.value = true
  try {
    await createSku(skuDialogSpu.value.spu_id, { ...newSku })
    ElMessage.success('SKU已添加')
    Object.assign(newSku, { sku_name: '', price: 0, stock: 0 })
    await loadGoods()
    skuDialogSpu.value = spus.value.find(s => s.spu_id === skuDialogSpu.value.spu_id)
  } finally { skuAdding.value = false }
}

function openEditSku(sku) {
  Object.assign(editSkuForm, { sku_id: sku.sku_id, sku_name: sku.sku_name, price: sku.price, stock: sku.stock })
  editSkuVisible.value = true
}

async function handleUpdateSku() {
  skuSaving.value = true
  try {
    await updateSku(editSkuForm.sku_id, { sku_name: editSkuForm.sku_name, price: editSkuForm.price, stock: editSkuForm.stock })
    ElMessage.success('已更新')
    editSkuVisible.value = false
    await loadGoods()
    skuDialogSpu.value = spus.value.find(s => s.spu_id === skuDialogSpu.value.spu_id)
  } finally { skuSaving.value = false }
}

async function handleDeleteSku(sku) {
  await ElMessageBox.confirm(`确认删除SKU「${sku.sku_name}」？`, '提示', { type: 'warning' })
  await deleteSku(sku.sku_id)
  ElMessage.success('已删除')
  await loadGoods()
  skuDialogSpu.value = spus.value.find(s => s.spu_id === skuDialogSpu.value.spu_id)
}

// ── AR ────────────────────────────────────────────────────────────────────────
function triggerUpload(skuId) { currentSkuId.value = skuId; fileRef.value.value = ''; fileRef.value.click() }

async function onFile(e) {
  const file = e.target.files[0]; if (!file) return
  const skuId = currentSkuId.value; uploading[skuId] = true
  try {
    const res = await uploadArAsset(skuId, file)
    const sku = arSelected.value.skus.find(s => s.sku_id === skuId)
    if (sku) sku.ar_asset_url = res.data.ar_asset_url
    ElMessage.success('素材上传成功')
  } finally { uploading[skuId] = false }
}

async function saveParams(sku) {
  saving[sku.sku_id] = true
  try {
    await updateArParams(sku.sku_id, { ar_offset_x: sku.ar_offset_x, ar_offset_y: sku.ar_offset_y, ar_scale_base: sku.ar_scale_base, ar_rotation_offset: sku.ar_rotation_offset })
    ElMessage.success('参数已保存')
  } finally { saving[sku.sku_id] = false }
}

async function openPreset(sku) {
  presetTargetSku.value = sku
  if (!presets.value.length) { const res = await getArPresets(); presets.value = res.data }
  presetVisible.value = true
}

async function applyPreset(preset) {
  const sku = presetTargetSku.value; saving[sku.sku_id] = true
  try {
    await updateArParams(sku.sku_id, { ar_asset_url: preset.ar_asset_url, ar_offset_x: preset.ar_offset_x, ar_offset_y: preset.ar_offset_y, ar_scale_base: preset.ar_scale_base, ar_rotation_offset: preset.ar_rotation_offset })
    Object.assign(sku, { ar_asset_url: preset.ar_asset_url, ar_offset_x: preset.ar_offset_x, ar_offset_y: preset.ar_offset_y, ar_scale_base: preset.ar_scale_base, ar_rotation_offset: preset.ar_rotation_offset })
    ElMessage.success(`已应用「${preset.name}」`); presetVisible.value = false
  } finally { saving[sku.sku_id] = false }
}

onMounted(loadGoods)
</script>

<style scoped>
.admin-goods-page { padding: 28px 32px; }
.page-header { margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 800; color: #1A1714; }
.page-title span { color: #C4906A; margin-right: 8px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.goods-table { border-radius: 10px; overflow: hidden; }
.img-err { width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:#f5f3f0;font-size:18px; }
.sku-row { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
.ar-layout { display: grid; grid-template-columns: 260px 1fr; gap: 16px; }
.spu-panel, .sku-panel { background: #fff; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,.05); overflow: hidden; }
.panel-hd { padding: 14px 18px; font-size: 14px; font-weight: 700; color: #1A1714; border-bottom: 1px solid #f0ede8; }
.spu-list { max-height: 600px; overflow-y: auto; }
.spu-item { display: flex; gap: 10px; padding: 12px 14px; cursor: pointer; border-bottom: 1px solid #f5f3f0; transition: background .15s; }
.spu-item:hover { background: #fdf9f5; }
.spu-item.active { background: #fdf6f0; border-left: 3px solid #C4906A; }
.spu-thumb { width: 44px; height: 44px; border-radius: 6px; flex-shrink: 0; }
.spu-name { font-size: 12px; font-weight: 600; color: #1A1714; margin-bottom: 4px; }
.spu-meta { display: flex; gap: 4px; flex-wrap: wrap; }
.sku-cards { padding: 14px; display: flex; flex-direction: column; gap: 14px; max-height: 600px; overflow-y: auto; }
.sku-card { border: 1px solid #f0ede8; border-radius: 10px; overflow: hidden; }
.sku-card-hd { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: #faf9f7; border-bottom: 1px solid #f0ede8; }
.sku-name { font-size: 13px; font-weight: 700; color: #1A1714; flex: 1; }
.sku-card-body { display: flex; gap: 16px; padding: 14px; }
.ar-preview-col { display: flex; flex-direction: column; align-items: center; gap: 6px; width: 110px; flex-shrink: 0; }
.ar-preview-box { width: 90px; height: 110px; border: 2px dashed #e0dbd4; border-radius: 8px; display: flex; align-items: center; justify-content: center; background: #faf9f7; overflow: hidden; }
.ar-preview-img { max-width: 100%; max-height: 100%; object-fit: contain; }
.ar-no-asset { font-size: 11px; color: #bbb; text-align: center; }
.ar-params-col { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.param-row { display: flex; align-items: center; gap: 8px; }
.param-row label { width: 40px; font-size: 12px; color: #888; text-align: right; flex-shrink: 0; }
.preset-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.preset-item { border: 2px solid #f0ede8; border-radius: 8px; padding: 10px; cursor: pointer; text-align: center; transition: all .15s; }
.preset-item:hover { border-color: #C4906A; background: #fdf6f0; }
.preset-img { width: 56px; height: 72px; object-fit: contain; margin-bottom: 4px; }
.preset-name { font-size: 11px; font-weight: 600; color: #1A1714; }
.preset-meta { font-size: 10px; color: #999; }
</style>
