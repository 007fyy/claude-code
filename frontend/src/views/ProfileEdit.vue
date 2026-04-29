<template>
  <div class="edit-page">
    <div class="container">
      <div class="page-header">
        <el-button text @click="$router.back()">← 返回</el-button>
        <h1 class="page-title">编辑资料</h1>
      </div>

      <div class="edit-layout">
        <!-- 左侧：头像 + 基本信息 -->
        <div class="edit-sidebar">
          <div class="avatar-section">
            <div class="avatar-wrap">
              <img v-if="form.avatar_url" :src="form.avatar_url" class="avatar-img" />
              <span v-else class="avatar-placeholder">{{ form.nickname?.charAt(0) || '👤' }}</span>
              <div class="avatar-overlay" @click="triggerAvatarUpload">
                <span>📷</span>
              </div>
            </div>
            <input ref="avatarInput" type="file" accept="image/*" style="display:none" @change="onAvatarSelect" />
            <div class="avatar-hint">点击更换头像</div>
          </div>

          <div class="sidebar-card">
            <div class="sidebar-label">账号信息</div>
            <div class="sidebar-row">
              <span class="sidebar-key">QQ邮箱</span>
              <span class="sidebar-val">{{ form.email || '未绑定' }}</span>
            </div>
            <div class="sidebar-row">
              <span class="sidebar-key">手机号</span>
              <span class="sidebar-val">{{ form.phone || '未绑定' }}</span>
            </div>
            <div class="sidebar-row">
              <span class="sidebar-key">注册时间</span>
              <span class="sidebar-val">{{ joinDate }}</span>
            </div>
          </div>
        </div>

        <!-- 右侧：表单 -->
        <div class="edit-main">
          <el-form :model="form" :rules="rules" ref="formRef" label-position="top" class="edit-form">

            <!-- 基本信息 -->
            <div class="form-card">
              <div class="card-title">基本信息</div>
              <div class="form-grid">
                <el-form-item label="QQ邮箱">
                  <div class="email-display">
                    <span class="input-icon">📧</span>
                    <span>{{ form.email }}</span>
                  </div>
                  <div class="field-hint">邮箱为账号唯一标识，不可修改</div>
                </el-form-item>
                <el-form-item label="昵称" prop="nickname">
                  <el-input v-model="form.nickname" placeholder="给自己取个名字吧" size="large" maxlength="20" show-word-limit>
                    <template #prefix><span class="input-icon">✏️</span></template>
                  </el-input>
                </el-form-item>
              </div>

              <div class="form-grid">
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="form.phone" placeholder="请输入手机号" size="large" maxlength="11">
                    <template #prefix><span class="input-icon">📱</span></template>
                  </el-input>
                </el-form-item>
                <el-form-item label="性别">
                  <div class="gender-cards">
                    <div
                      v-for="g in genderOptions"
                      :key="g.value"
                      class="gender-card"
                      :class="{ active: form.gender === g.value }"
                      @click="form.gender = g.value"
                    >
                      <span class="gender-icon">{{ g.icon }}</span>
                      <span class="gender-label">{{ g.label }}</span>
                    </div>
                  </div>
                </el-form-item>
                <el-form-item label="生日">
                  <el-date-picker
                    v-model="form.birthday"
                    type="date"
                    placeholder="选择生日"
                    size="large"
                    style="width: 100%"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    :disabled-date="disableFutureDate"
                  />
                </el-form-item>
              </div>
            </div>

            <!-- 个性展示 -->
            <div class="form-card">
              <div class="card-title">个性展示</div>
              <el-form-item label="个性签名">
                <el-input
                  v-model="form.signature"
                  placeholder="一句话介绍自己的风格态度"
                  size="large"
                  maxlength="50"
                  show-word-limit
                >
                  <template #prefix><span class="input-icon">💬</span></template>
                </el-input>
              </el-form-item>
              <el-form-item label="自我介绍">
                <el-input
                  v-model="form.bio"
                  type="textarea"
                  :rows="4"
                  placeholder="分享你的穿搭理念、饰品偏好，或者任何你想说的..."
                  maxlength="200"
                  show-word-limit
                  resize="none"
                />
              </el-form-item>
            </div>

            <!-- 偏好设置 -->
            <div class="form-card">
              <div class="card-title">偏好设置</div>
              <el-form-item label="偏好风格">
                <div class="pref-chips">
                  <span
                    v-for="s in styleOptions"
                    :key="s"
                    class="chip"
                    :class="{ active: form.style_prefs.includes(s) }"
                    @click="togglePref('style_prefs', s)"
                  >{{ s }}</span>
                </div>
              </el-form-item>
              <el-form-item label="佩戴场合">
                <div class="pref-chips">
                  <span
                    v-for="o in occasionOptions"
                    :key="o"
                    class="chip"
                    :class="{ active: form.occasion_prefs.includes(o) }"
                    @click="togglePref('occasion_prefs', o)"
                  >{{ o }}</span>
                </div>
              </el-form-item>
            </div>

            <!-- 脸型档案 -->
            <div class="form-card">
              <div class="card-title">脸型档案</div>
              <div class="face-info">
                <div class="face-left">
                  <span class="face-icon">👤</span>
                  <div>
                    <div class="face-label">{{ faceType || '未检测' }}</div>
                    <div class="face-sub">脸型信息用于精准推荐饰品</div>
                  </div>
                </div>
                <el-button size="small" @click="$router.push('/face-detect')">
                  {{ faceType ? '重新检测' : '去检测' }}
                </el-button>
              </div>
            </div>

            <div class="form-footer">
              <el-button size="large" @click="$router.back()">取消</el-button>
              <el-button type="primary" size="large" class="save-btn" :loading="saving" @click="save">
                保存修改
              </el-button>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getMe, updateMe, updatePrefs, uploadAvatar } from '@/api/user'

const router = useRouter()
const saving = ref(false)
const faceType = ref('')
const formRef = ref(null)
const avatarInput = ref(null)
const avatarFile = ref(null)
const joinDate = ref('2026.04')

const form = ref({
  email: '',
  nickname: '',
  phone: '',
  gender: 'secret',
  birthday: '',
  signature: '',
  bio: '',
  avatar_url: '',
  style_prefs: [],
  occasion_prefs: [],
})

const phoneValidator = (_r, v, cb) => {
  if (v && !/^1[3-9]\d{9}$/.test(v)) cb(new Error('请输入正确的11位手机号'))
  else cb()
}

const rules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '昵称长度 2-20 个字符', trigger: 'blur' },
  ],
  phone: [
    { validator: phoneValidator, trigger: 'blur' },
  ],
}

const genderOptions = [
  { value: 'female', icon: '♀', label: '女' },
  { value: 'male', icon: '♂', label: '男' },
  { value: 'secret', icon: '✦', label: '保密' },
]

const styleOptions = ['简约极简', '优雅复古', '甜美少女', '个性先锋', '轻奢高级']
const occasionOptions = ['日常通勤', '约会出行', '职场正式', '派对聚会', '运动休闲']

function togglePref(key, val) {
  const arr = form.value[key]
  const idx = arr.indexOf(val)
  if (idx >= 0) arr.splice(idx, 1)
  else arr.push(val)
}

function disableFutureDate(date) {
  return date > new Date()
}

function triggerAvatarUpload() {
  avatarInput.value?.click()
}

function onAvatarSelect(e) {
  const file = e.target.files?.[0]
  if (!file) return
  avatarFile.value = file
  const reader = new FileReader()
  reader.onload = (ev) => {
    form.value.avatar_url = ev.target.result
  }
  reader.readAsDataURL(file)
}

onMounted(async () => {
  try {
    const res = await getMe()
    const u = res.data
    form.value.email = u.email || ''
    form.value.nickname = u.nickname || ''
    form.value.phone = u.phone || ''
    form.value.gender = u.gender || 'secret'
    form.value.birthday = u.birthday || ''
    form.value.signature = u.signature || ''
    form.value.bio = u.bio || ''
    form.value.avatar_url = u.avatar_url || ''
    form.value.style_prefs = u.style_prefs || []
    form.value.occasion_prefs = u.occasion_prefs || []
    if (u.face_shape) faceType.value = u.face_shape
    if (u.created_at) joinDate.value = u.created_at.slice(0, 7).replace('-', '.')
  } catch {}
})

async function save() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  saving.value = true
  try {
    if (avatarFile.value) {
      const avatarRes = await uploadAvatar(avatarFile.value)
      form.value.avatar_url = avatarRes.data.avatar_url
      avatarFile.value = null
    }

    await updateMe({
      nickname: form.value.nickname,
      avatar_url: form.value.avatar_url,
      phone: form.value.phone,
      gender: form.value.gender,
      birthday: form.value.birthday,
      signature: form.value.signature,
      bio: form.value.bio,
    })

    await updatePrefs({
      style_prefs: form.value.style_prefs,
      occasion_prefs: form.value.occasion_prefs,
    })

    const stored = JSON.parse(localStorage.getItem('user') || '{}')
    stored.nickname = form.value.nickname
    stored.avatar_url = form.value.avatar_url
    localStorage.setItem('user', JSON.stringify(stored))

    ElMessage.success('保存成功')
    router.back()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.edit-page { flex: 1; }
.container { max-width: 1100px; margin: 0 auto; padding: 0 32px 60px; }

.page-header {
  display: flex; align-items: center; gap: 12px; padding: 24px 0 20px;
}
.page-title { font-size: 22px; font-weight: 800; color: #1A1714; }

.edit-layout {
  display: grid; grid-template-columns: 280px 1fr; gap: 24px; align-items: start;
}

.edit-sidebar { display: flex; flex-direction: column; gap: 16px; }

.avatar-section {
  background: linear-gradient(135deg, #C4906A, #e8b49a);
  border-radius: 20px; padding: 32px 24px;
  display: flex; flex-direction: column; align-items: center; gap: 12px;
}
.avatar-wrap {
  position: relative; width: 100px; height: 100px;
  border-radius: 50%; overflow: hidden;
  border: 3px solid rgba(255,255,255,.4);
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-placeholder {
  width: 100%; height: 100%; display: flex; align-items: center;
  justify-content: center; font-size: 40px;
  background: rgba(255,255,255,.2); color: #fff;
}
.avatar-overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,.35); display: flex;
  align-items: center; justify-content: center;
  font-size: 24px; cursor: pointer;
  opacity: 0; transition: opacity .2s;
}
.avatar-wrap:hover .avatar-overlay { opacity: 1; }
.avatar-hint { font-size: 13px; color: rgba(255,255,255,.8); }

.sidebar-card {
  background: #fff; border-radius: 16px; padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,.07);
}
.sidebar-label {
  font-size: 13px; font-weight: 600; color: #B0B0B0;
  text-transform: uppercase; letter-spacing: 1px; margin-bottom: 14px;
}
.sidebar-row {
  display: flex; justify-content: space-between;
  font-size: 14px; padding: 8px 0;
  border-bottom: 1px solid #F0F0F0;
}
.sidebar-row:last-child { border-bottom: none; }
.sidebar-key { color: #6B6B6B; }
.sidebar-val { color: #1A1714; font-weight: 500; }

.edit-main { display: flex; flex-direction: column; gap: 0; }

.form-card {
  background: #fff; border-radius: 16px; padding: 24px 28px;
  margin-bottom: 16px; box-shadow: 0 2px 12px rgba(0,0,0,.07);
}
.card-title {
  font-size: 16px; font-weight: 700; color: #1A1714;
  margin-bottom: 20px; padding-bottom: 12px;
  border-bottom: 1px solid #F0F0F0;
}

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 24px; }

.input-icon { font-size: 16px; }
.field-hint { font-size: 12px; color: #B0B0B0; margin-top: 4px; }

.email-display {
  display: flex; align-items: center; gap: 8px;
  height: 40px; padding: 0 12px;
  background: #FAF9F7; border-radius: 8px;
  font-size: 14px; color: #1A1714; width: 100%;
}

.gender-cards { display: flex; gap: 12px; }
.gender-card {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  gap: 6px; padding: 16px 12px; border: 2px solid #EBEBEB;
  border-radius: 14px; cursor: pointer; transition: all .2s;
  background: #fff;
}
.gender-card:hover { border-color: #C4906A; }
.gender-card.active { border-color: #C4906A; background: #F5EDE3; }
.gender-icon { font-size: 22px; }
.gender-label { font-size: 13px; font-weight: 600; color: #1A1714; }

.pref-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  display: inline-flex; align-items: center;
  padding: 8px 18px; border-radius: 20px;
  font-size: 13px; font-weight: 500;
  border: 1.5px solid #EBEBEB; background: #fff; color: #6B6B6B;
  cursor: pointer; transition: all .15s;
}
.chip:hover { border-color: #C4906A; color: #9E7050; }
.chip.active { background: #1A1714; color: white; border-color: #1A1714; }

.face-info {
  display: flex; align-items: center; justify-content: space-between;
  background: #FAF9F7; border-radius: 12px; padding: 18px;
}
.face-left { display: flex; align-items: center; gap: 14px; }
.face-icon { font-size: 32px; }
.face-label { font-size: 15px; font-weight: 600; color: #1A1714; }
.face-sub { font-size: 13px; color: #B0B0B0; margin-top: 2px; }

.form-footer {
  display: flex; justify-content: flex-end; gap: 12px;
  padding-top: 8px;
}
.save-btn {
  min-width: 160px; border-radius: 12px; font-size: 16px; font-weight: 700;
  background: linear-gradient(135deg, #1A1714, #4A3020); border-color: transparent;
}
.save-btn:hover { background: linear-gradient(135deg, #2D231A, #6B4226); }
</style>
