<template>
  <div class="cart-page">
    <div class="topbar">
      <el-page-header @back="$router.push('/goods')" title="返回商城" content="购物车" />
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

    <!-- 结算弹窗 -->
    <el-dialog v-model="checkoutVisible" title="填写收货信息" width="440px">
      <el-form :model="form" label-width="80px" :rules="rules" ref="formRef">
        <el-form-item label="收货人" prop="receiver_name">
          <el-input v-model="form.receiver_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="手机号" prop="receiver_phone">
          <el-input v-model="form.receiver_phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="收货地址" prop="receiver_address">
          <el-input
            v-model="form.receiver_address"
            type="textarea"
            :rows="2"
            placeholder="省/市/区/详细地址"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" placeholder="可选" />
        </el-form-item>
      </el-form>
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

const router = useRouter()

const items = ref([])
const loading = ref(false)
const selectedRows = ref([])
const checkoutVisible = ref(false)
const submitting = ref(false)
const formRef = ref(null)

const form = ref({
  receiver_name: '',
  receiver_phone: '',
  receiver_address: '',
  remark: '',
})

const rules = {
  receiver_name: [{ required: true, message: '请填写收货人', trigger: 'blur' }],
  receiver_phone: [{ required: true, message: '请填写手机号', trigger: 'blur' }],
  receiver_address: [{ required: true, message: '请填写地址', trigger: 'blur' }],
}

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

function openCheckout() {
  if (selectedRows.value.length === 0) return
  checkoutVisible.value = true
}

async function submitOrder() {
  await formRef.value.validate()
  submitting.value = true
  try {
    const cartItemIds = selectedRows.value.map((r) => r.cart_item_id)
    const res = await createOrder({
      cart_item_ids: cartItemIds,
      ...form.value,
    })
    const { order_id, order_no } = res.data

    // 模拟支付
    await payOrder({ order_id })

    checkoutVisible.value = false
    const amount = selectedRows.value.reduce((s, r) => s + r.price * r.quantity, 0).toFixed(2)
    router.push({ path: '/payment-result', query: { order_id, order_no, amount } })
    await loadCart()
  } finally {
    submitting.value = false
  }
}

onMounted(loadCart)
</script>

<style scoped>
.cart-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 16px 60px;
}

.topbar {
  padding: 16px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
}

.item-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-img {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  flex-shrink: 0;
}

.item-spu {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.price {
  color: #e6564e;
  font-weight: 600;
}

.subtotal {
  color: #e6564e;
  font-weight: 700;
}

.checkout-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 24px;
  padding: 16px 0;
  border-top: 1px solid #eee;
  margin-top: 12px;
}

.summary {
  font-size: 14px;
  color: #666;
}

.total-price {
  font-size: 20px;
  font-weight: 700;
  color: #e6564e;
}
</style>
