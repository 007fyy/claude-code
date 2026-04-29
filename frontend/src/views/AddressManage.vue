<template>
  <div class="address-page">
    <div class="container">
      <div class="page-header">
        <div class="header-left">
          <el-button text @click="$router.back()">← 返回</el-button>
          <h1 class="page-title">收货地址管理</h1>
        </div>
        <el-button type="primary" @click="openAdd">+ 新增地址</el-button>
      </div>

      <div v-loading="loading" class="address-list">
        <div
          v-for="addr in addresses"
          :key="addr.id"
          class="address-card"
          :class="{ 'is-default': addr.is_default }"
        >
          <div class="card-left">
            <div class="addr-top">
              <span class="addr-name">{{ addr.name }}</span>
              <span class="addr-phone">{{ addr.phone }}</span>
              <span v-if="addr.tag" class="addr-tag">{{ addr.tag }}</span>
              <span v-if="addr.is_default" class="default-badge">默认</span>
            </div>
            <div class="addr-detail">
              {{ addr.province }}{{ addr.city }}{{ addr.district }} {{ addr.detail }}
            </div>
          </div>
          <div class="card-actions">
            <el-button
              v-if="!addr.is_default"
              size="small"
              @click="handleSetDefault(addr)"
            >设为默认</el-button>
            <el-button size="small" @click="openEdit(addr)">编辑</el-button>
            <el-button
              size="small"
              type="danger"
              plain
              @click="handleDelete(addr)"
            >删除</el-button>
          </div>
        </div>

        <el-empty v-if="!loading && addresses.length === 0" description="还没有收货地址">
          <el-button type="primary" @click="openAdd">添加第一个地址</el-button>
        </el-empty>
      </div>

      <div class="address-tip" v-if="addresses.length > 0">
        共 {{ addresses.length }} 个收货地址，最多可保存 20 个
      </div>
    </div>

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑地址' : '新增地址'"
      width="560px"
      :close-on-click-modal="false"
    >
      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-position="top"
        class="addr-form"
      >
        <div class="form-row">
          <el-form-item label="收货人" prop="name" class="form-half">
            <el-input v-model="form.name" placeholder="请输入姓名" size="large" />
          </el-form-item>
          <el-form-item label="手机号" prop="phone" class="form-half">
            <el-input v-model="form.phone" placeholder="请输入手机号" size="large" maxlength="11" />
          </el-form-item>
        </div>

        <div class="form-row">
          <el-form-item label="省份" prop="province" class="form-third">
            <el-select v-model="form.province" placeholder="省" size="large" style="width:100%">
              <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
            </el-select>
          </el-form-item>
          <el-form-item label="城市" prop="city" class="form-third">
            <el-input v-model="form.city" placeholder="市" size="large" />
          </el-form-item>
          <el-form-item label="区/县" prop="district" class="form-third">
            <el-input v-model="form.district" placeholder="区/县" size="large" />
          </el-form-item>
        </div>

        <el-form-item label="详细地址" prop="detail">
          <el-input
            v-model="form.detail"
            type="textarea"
            :rows="2"
            placeholder="街道、楼栋、门牌号等"
            size="large"
          />
        </el-form-item>

        <div class="form-row form-bottom">
          <el-form-item label="标签" class="form-half">
            <div class="tag-chips">
              <span
                v-for="t in tagOptions"
                :key="t"
                class="tag-chip"
                :class="{ active: form.tag === t }"
                @click="form.tag = form.tag === t ? '' : t"
              >{{ t }}</span>
            </div>
          </el-form-item>
          <el-form-item class="form-half default-check">
            <el-checkbox v-model="form.is_default">设为默认地址</el-checkbox>
          </el-form-item>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '保存修改' : '添加地址' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  listAddress,
  createAddress,
  updateAddress,
  deleteAddress,
  setDefaultAddress,
} from '@/api/user'

const loading = ref(false)
const addresses = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref(null)

const form = ref({
  name: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  detail: '',
  tag: '',
  is_default: false,
})

const rules = {
  name: [{ required: true, message: '请输入收货人姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  province: [{ required: true, message: '请选择省份', trigger: 'change' }],
  city: [{ required: true, message: '请输入城市', trigger: 'blur' }],
  district: [{ required: true, message: '请输入区/县', trigger: 'blur' }],
  detail: [{ required: true, message: '请输入详细地址', trigger: 'blur' }],
}

const tagOptions = ['家', '公司', '学校', '父母家']

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

function resetForm() {
  form.value = {
    name: '', phone: '', province: '', city: '',
    district: '', detail: '', tag: '', is_default: false,
  }
}

function openAdd() {
  isEdit.value = false
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(addr) {
  isEdit.value = true
  editingId.value = addr.id
  form.value = {
    name: addr.name,
    phone: addr.phone,
    province: addr.province,
    city: addr.city,
    district: addr.district,
    detail: addr.detail,
    tag: addr.tag || '',
    is_default: addr.is_default,
  }
  dialogVisible.value = true
}

async function loadAddresses() {
  loading.value = true
  try {
    const res = await listAddress()
    addresses.value = res.data || []
  } catch {
    addresses.value = []
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateAddress(editingId.value, { ...form.value })
      ElMessage.success('地址已更新')
    } else {
      await createAddress({ ...form.value })
      ElMessage.success('地址已添加')
    }
    dialogVisible.value = false
    await loadAddresses()
  } catch {
    ElMessage.error('操作失败，请重试')
  } finally {
    submitting.value = false
  }
}

async function handleSetDefault(addr) {
  try {
    await setDefaultAddress(addr.id)
    ElMessage.success('已设为默认地址')
    await loadAddresses()
  } catch {
    ElMessage.error('设置失败')
  }
}

async function handleDelete(addr) {
  try {
    await ElMessageBox.confirm(
      `确认删除「${addr.name}」的地址吗？`,
      '删除地址',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  try {
    await deleteAddress(addr.id)
    ElMessage.success('地址已删除')
    await loadAddresses()
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(loadAddresses)
</script>

<style scoped>
.address-page { flex: 1; }
.container { max-width: 900px; margin: 0 auto; padding: 0 32px 60px; }

.page-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 24px 0 20px;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.page-title { font-size: 22px; font-weight: 800; color: #1A1714; }

.address-list { display: flex; flex-direction: column; gap: 12px; }

.address-card {
  background: #fff; border-radius: 16px; padding: 20px 24px;
  display: flex; align-items: center; justify-content: space-between;
  gap: 24px; box-shadow: 0 2px 12px rgba(0,0,0,.07);
  border-left: 4px solid transparent;
  transition: all .2s;
}
.address-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,.1); }
.address-card.is-default { border-left-color: #C4906A; }

.card-left { flex: 1; min-width: 0; }

.addr-top {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 8px; flex-wrap: wrap;
}
.addr-name { font-size: 16px; font-weight: 700; color: #1A1714; }
.addr-phone { font-size: 14px; color: #6B6B6B; }
.addr-tag {
  font-size: 12px; font-weight: 600; color: #C4906A;
  background: #F5EDE3; padding: 2px 10px; border-radius: 10px;
}
.default-badge {
  font-size: 12px; font-weight: 600; color: #fff;
  background: #C4906A; padding: 2px 10px; border-radius: 10px;
}

.addr-detail {
  font-size: 14px; color: #6B6B6B; line-height: 1.6;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.card-actions { display: flex; gap: 8px; flex-shrink: 0; }

.address-tip {
  text-align: center; font-size: 13px; color: #B0B0B0;
  margin-top: 20px;
}

/* 弹窗表单 */
.addr-form { padding: 0 4px; }
.form-row { display: flex; gap: 16px; }
.form-half { flex: 1; }
.form-third { flex: 1; }
.form-bottom { align-items: center; }
.default-check { display: flex; align-items: flex-end; padding-bottom: 4px; }

.tag-chips { display: flex; gap: 8px; }
.tag-chip {
  padding: 6px 16px; border-radius: 20px;
  font-size: 13px; font-weight: 500;
  border: 1.5px solid #EBEBEB; background: #fff; color: #6B6B6B;
  cursor: pointer; transition: all .15s;
}
.tag-chip:hover { border-color: #C4906A; color: #9E7050; }
.tag-chip.active { background: #1A1714; color: #fff; border-color: #1A1714; }
</style>
