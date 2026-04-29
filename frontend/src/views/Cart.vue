<template>
  <div class="cart-page">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title"><span>✦</span> 购物车</h1>
        <el-button text @click="$router.push('/goods')">← 继续购物</el-button>
      </div>

    <div v-loading="loading" class="cart-body">
      <el-empty v-if="!loading && items.length === 0" description="购物车空空如也">
        <el-button type="primary" @click="$router.push('/goods')">去逛逛</el-button>
      </el-empty>

      <template v-else>
        <el-table :data="items" style="width: 100%" @selection-change="onSelect">
          <el-table-column type="selection" width="50" />

          <el-table-column label="商品" min-width="240">
            <template #default="{ row }">
              <div class="item-info">
                <el-image
                  :src="row.cover_url"
                  fit="cover"
                  class="item-img"
                />
                <div>
                  <div class="item-spu">{{ row.spu_name }}</div>
                  <el-tag size="small" type="info">{{ row.sku_name }}</el-tag>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="单价" width="100" align="right">
            <template #default="{ row }">
              <span class="price">¥{{ row.price.toFixed(2) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="数量" width="140" align="center">
            <template #default="{ row }">
              <el-input-number
                v-model="row.quantity"
                :min="1"
                :max="99"
                size="small"
                @change="(val) => changeQty(row, val)"
              />
            </template>
          </el-table-column>

          <el-table-column label="小计" width="110" align="right">
            <template #default="{ row }">
              <span class="subtotal">¥{{ (row.price * row.quantity).toFixed(2) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="AR 试戴" width="100" align="center">
            <template #default="{ row }">
              <el-button
                size="small"
                type="primary"
                link
                @click="tryOn(row)"
                :disabled="!row.ar_asset_url"
              >
                试戴
              </el-button>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="80" align="center">
            <template #default="{ row }">
              <el-button size="small" type="danger" link @click="removeItem(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 结算栏 -->
        <div class="checkout-bar">
          <div class="summary">
            已选 <b>{{ selectedRows.length }}</b> 件，合计：
            <span class="total-price">¥{{ totalSelected.toFixed(2) }}</span>
          </div>
          <el-button
            type="primary"
            size="large"
            :disabled="selectedRows.length === 0"
            @click="openCheckout"
          >
            去结算
          </el-button>
        </div>
      </template>
    </div>
    </div>

    <!-- 结算弹窗 -->
    <el-dialog v-model="checkoutVisible" title="确认订单" width="600px" :close-on-click-modal="false">
      <div v-loading="addrLoading" class="checkout-content">

        <!-- 视图 A：选择已有地址 -->
        <template v-if="addressMode === 'select'">
          <div class="section-label">选择收货地址</div>
          <div class="addr-list">
            <div
              v-for="addr in addressList"
              :key="addr.id"
              class="addr-card"
              :class="{ selected: selectedAddrId === addr.id }"
              @click="selectedAddrId = addr.id"
            >
              <div class="addr-radio">
                <span class="radio-dot" :class="{ active: selectedAddrId === addr.id }" />
              </div>
              <div class="addr-body">
                <div class="addr-top">
                  <span class="addr-name">{{ addr.name }}</span>
                  <span class="addr-phone">{{ addr.phone }}</span>
                  <span v-if="addr.is_default" class="addr-default-tag">默认</span>
                </div>
                <div class="addr-detail">{{ addr.province }}{{ addr.city }}{{ addr.district }} {{ addr.detail }}</div>
              </div>
              <el-button
                v-if="!addr.is_default"
                size="small"
                link
                class="set-default-btn"
                @click.stop="handleSetDefault(addr)"
              >设为默认</el-button>
            </div>
          </div>
          <div class="new-addr-link" @click="switchToNew">+ 使用新地址</div>
        </template>

        <!-- 视图 B：新增地址 -->
        <template v-if="addressMode === 'new'">
          <div class="section-label">
            填写收货地址
            <span v-if="addressList.length" class="back-link" @click="switchToSelect">← 选择已有地址</span>
          </div>
          <el-form :model="newAddr" :rules="addrRules" ref="addrFormRef" label-position="top" class="new-addr-form">
            <div class="form-row">
              <el-form-item label="收货人" prop="name" class="form-half">
                <el-input v-model="newAddr.name" placeholder="请输入姓名" />
              </el-form-item>
              <el-form-item label="手机号" prop="phone" class="form-half">
                <el-input v-model="newAddr.phone" placeholder="请输入手机号" maxlength="11" />
              </el-form-item>
            </div>
            <div class="form-row">
              <el-form-item label="省份" prop="province" class="form-third">
                <el-select v-model="newAddr.province" placeholder="省" style="width:100%">
                  <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
                </el-select>
              </el-form-item>
              <el-form-item label="城市" prop="city" class="form-third">
                <el-input v-model="newAddr.city" placeholder="市" />
              </el-form-item>
              <el-form-item label="区/县" prop="district" class="form-third">
                <el-input v-model="newAddr.district" placeholder="区/县" />
              </el-form-item>
            </div>
            <el-form-item label="详细地址" prop="detail">
              <el-input v-model="newAddr.detail" type="textarea" :rows="2" placeholder="街道、楼栋、门牌号等" />
            </el-form-item>
            <div class="form-checks">
              <el-checkbox v-model="newAddr.saveToBook">保存到地址簿</el-checkbox>
              <el-checkbox v-model="newAddr.is_default">设为默认地址</el-checkbox>
            </div>
          </el-form>
        </template>

        <!-- 备注（两个视图共用） -->
        <div class="remark-section">
          <div class="section-label">订单备注</div>
          <el-input v-model="remark" placeholder="选填，如有特殊要求请备注" />
        </div>
      </div>

      <template #footer>
        <el-button @click="checkoutVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitOrder">
          确认下单（模拟支付）
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCartList, updateCart, removeCart } from '../api/cart'
import { createOrder, payOrder } from '../api/order'
import { listAddress, createAddress, setDefaultAddress } from '../api/user'

const router = useRouter()

const items = ref([])
const loading = ref(false)
const selectedRows = ref([])
const checkoutVisible = ref(false)
const submitting = ref(false)

const addressMode = ref('select')
const addressList = ref([])
const selectedAddrId = ref(null)
const addrLoading = ref(false)
const addrFormRef = ref(null)
const remark = ref('')

const newAddr = ref({
  name: '', phone: '', province: '', city: '',
  district: '', detail: '', is_default: false, saveToBook: true,
})

const addrRules = {
  name: [{ required: true, message: '请输入收货人', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  province: [{ required: true, message: '请选择省份', trigger: 'change' }],
  city: [{ required: true, message: '请输入城市', trigger: 'blur' }],
  district: [{ required: true, message: '请输入区/县', trigger: 'blur' }],
  detail: [{ required: true, message: '请输入详细地址', trigger: 'blur' }],
}

const provinces = [
  '北京市', '天津市', '上海市', '重庆市',
  '河北省', '山西省', '辽宁省', '吉林省', '黑龙江省',
  '江苏省', '浙江省', '安徽省', '福建省', '江西省', '山东省',
  '河南省', '湖北省', '湖南省', '广东省', '海南省',
  '四川省', '贵州省', '云南省', '陕西省', '甘肃省',
  '青海省', '台湾省',
  '内蒙古自治区', '广西壮族自治区', '西藏自治区',
  '宁夏回族自治区', '新疆维吾尔自治区',
  '香港特别行政区', '澳门特别行政区',
]

const totalSelected = computed(() =>
  selectedRows.value.reduce((s, r) => s + r.price * r.quantity, 0)
)

async function loadCart() {
  loading.value = true
  try {
    const res = await getCartList()
    items.value = res.items
  } finally {
    loading.value = false
  }
}

function onSelect(rows) {
  selectedRows.value = rows
}

async function changeQty(row, val) {
  await updateCart({ cart_item_id: row.cart_item_id, quantity: val })
  row.quantity = val
}

async function removeItem(row) {
  await ElMessageBox.confirm('确认删除该商品？', '提示', { type: 'warning' })
  await removeCart(row.cart_item_id)
  items.value = items.value.filter((i) => i.cart_item_id !== row.cart_item_id)
  window.dispatchEvent(new Event('cart-updated'))
  ElMessage.success('已删除')
}

function tryOn(row) {
  router.push({
    name: 'FaceARView',
    query: {
      sku_id: row.sku_id,
      sku_name: row.spu_name,
      ar_asset_url: row.ar_asset_url || '',
      mount_type: row.mount_type,
    },
  })
}

async function openCheckout() {
  if (selectedRows.value.length === 0) return
  remark.value = ''
  selectedAddrId.value = null
  addrLoading.value = true
  checkoutVisible.value = true

  try {
    const res = await listAddress()
    addressList.value = res.data || []
  } catch {
    addressList.value = []
  } finally {
    addrLoading.value = false
  }

  if (addressList.value.length === 0) {
    addressMode.value = 'new'
    resetNewAddr()
  } else {
    addressMode.value = 'select'
    const def = addressList.value.find(a => a.is_default)
    selectedAddrId.value = def ? def.id : null
  }
}

function resetNewAddr() {
  newAddr.value = {
    name: '', phone: '', province: '', city: '',
    district: '', detail: '', is_default: false, saveToBook: true,
  }
}

function switchToNew() {
  resetNewAddr()
  addressMode.value = 'new'
}

function switchToSelect() {
  addressMode.value = 'select'
}

async function handleSetDefault(addr) {
  try {
    await setDefaultAddress(addr.id)
    addressList.value.forEach(a => { a.is_default = a.id === addr.id })
    selectedAddrId.value = addr.id
    ElMessage.success('已设为默认地址')
  } catch {
    ElMessage.error('设置失败')
  }
}

async function submitOrder() {
  let receiverName, receiverPhone, receiverAddress

  if (addressMode.value === 'select') {
    if (!selectedAddrId.value) {
      ElMessage.warning('请选择一个收货地址')
      return
    }
    const addr = addressList.value.find(a => a.id === selectedAddrId.value)
    receiverName = addr.name
    receiverPhone = addr.phone
    receiverAddress = `${addr.province}${addr.city}${addr.district} ${addr.detail}`
  } else {
    try {
      await addrFormRef.value.validate()
    } catch {
      return
    }
    const a = newAddr.value
    receiverName = a.name
    receiverPhone = a.phone
    receiverAddress = `${a.province}${a.city}${a.district} ${a.detail}`

    if (a.saveToBook) {
      try {
        await createAddress({
          name: a.name, phone: a.phone,
          province: a.province, city: a.city,
          district: a.district, detail: a.detail,
          is_default: a.is_default,
        })
      } catch {}
    }
  }

  submitting.value = true
  try {
    const cartItemIds = selectedRows.value.map((r) => r.cart_item_id)
    const res = await createOrder({
      cart_item_ids: cartItemIds,
      receiver_name: receiverName,
      receiver_phone: receiverPhone,
      receiver_address: receiverAddress,
      remark: remark.value,
    })
    const { order_id, order_no } = res.data

    await payOrder({ order_id })

    checkoutVisible.value = false
    const amount = selectedRows.value.reduce((s, r) => s + r.price * r.quantity, 0).toFixed(2)
    window.dispatchEvent(new Event('cart-updated'))
    router.push({ path: '/payment-result', query: { order_id, order_no, amount } })
    await loadCart()
  } finally {
    submitting.value = false
  }
}

onMounted(loadCart)
</script>

<style scoped>
.cart-page { flex: 1; }
.container { max-width: 1100px; margin: 0 auto; padding: 0 32px 60px; }

.page-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 24px 0 20px;
}
.page-title { font-size: 24px; font-weight: 800; color: #1A1714; }
.page-title span { color: #C4906A; }

.item-info { display: flex; align-items: center; gap: 12px; }
.item-img { width: 64px; height: 64px; border-radius: 8px; flex-shrink: 0; }
.item-spu { font-size: 14px; font-weight: 600; margin-bottom: 4px; }
.price { color: #1A1714; font-weight: 700; }
.subtotal { color: #1A1714; font-weight: 800; font-size: 16px; }

.checkout-bar {
  display: flex; align-items: center; justify-content: flex-end;
  gap: 24px; padding: 20px 0; border-top: 1px solid #F0F0F0; margin-top: 12px;
}
.summary { font-size: 14px; color: #6B6B6B; }
.total-price { font-size: 22px; font-weight: 800; color: #1A1714; }

/* 结算弹窗 */
.checkout-content { min-height: 120px; }

.section-label {
  font-size: 14px; font-weight: 700; color: #1A1714;
  margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;
}
.back-link {
  font-size: 13px; font-weight: 400; color: #C4906A;
  cursor: pointer; transition: color .15s;
}
.back-link:hover { color: #9E7050; }

.addr-list { display: flex; flex-direction: column; gap: 10px; max-height: 260px; overflow-y: auto; }

.addr-card {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 16px; border: 1.5px solid #EBEBEB; border-radius: 12px;
  cursor: pointer; transition: all .15s;
}
.addr-card:hover { border-color: #C4906A; }
.addr-card.selected { border-color: #C4906A; background: #FDF8F4; }

.addr-radio { flex-shrink: 0; }
.radio-dot {
  display: block; width: 18px; height: 18px; border-radius: 50%;
  border: 2px solid #EBEBEB; transition: all .15s;
  position: relative;
}
.radio-dot.active {
  border-color: #C4906A;
}
.radio-dot.active::after {
  content: ''; position: absolute;
  top: 3px; left: 3px; width: 8px; height: 8px;
  border-radius: 50%; background: #C4906A;
}

.addr-body { flex: 1; min-width: 0; }
.addr-top { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.addr-name { font-size: 14px; font-weight: 600; color: #1A1714; }
.addr-phone { font-size: 13px; color: #6B6B6B; }
.addr-default-tag {
  font-size: 11px; font-weight: 600; color: #fff;
  background: #C4906A; padding: 1px 8px; border-radius: 8px;
}
.addr-detail {
  font-size: 13px; color: #6B6B6B; line-height: 1.5;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.set-default-btn { font-size: 12px; color: #C4906A; flex-shrink: 0; }

.new-addr-link {
  margin-top: 12px; font-size: 13px; color: #C4906A;
  cursor: pointer; transition: color .15s; text-align: center;
}
.new-addr-link:hover { color: #9E7050; }

.new-addr-form { margin-top: 4px; }
.form-row { display: flex; gap: 12px; }
.form-half { flex: 1; }
.form-third { flex: 1; }
.form-checks {
  display: flex; gap: 24px; margin-top: 4px;
}

.remark-section { margin-top: 16px; padding-top: 16px; border-top: 1px solid #F0F0F0; }
</style>
