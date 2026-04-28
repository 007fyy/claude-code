<template>
  <div class="login-page">
    <div v-if="!showOnboarding" class="login-card">
      <div class="brand">
        <div class="brand-logo">✦</div>
        <div class="brand-name">珑饰</div>
        <div class="brand-slogan">发现最适合你的那一件</div>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef" class="login-form">
        <el-form-item prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" maxlength="11" size="large">
            <template #prepend>+86</template>
          </el-input>
        </el-form-item>
        <el-form-item prop="code">
          <el-input v-model="form.code" placeholder="请输入验证码" maxlength="6" size="large">
            <template #append>
              <el-button :disabled="countdown > 0" @click="sendCode" link>
                {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>

        <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="doLogin">
          登录 / 注册
        </el-button>
      </el-form>

      <div class="divider"><span>或者</span></div>
      <el-button class="wechat-btn" size="large" @click="mockWechat">
        <span class="wechat-icon">💬</span> 微信一键登录
      </el-button>

      <div class="agreement">
        继续即同意
        <el-link type="primary" :underline="false">《用户协议》</el-link>
        <el-link type="primary" :underline="false">《隐私政策》</el-link>
      </div>

      <el-button link class="skip-btn" @click="skipLogin">跳过，先看看 →</el-button>
    </div>

    <!-- 冷启动问卷 -->
    <div v-else class="onboarding">
      <div class="ob-progress">
        <span
          v-for="i in 3" :key="i"
          class="ob-dot"
          :class="{ active: i === obStep }"
        />
      </div>

      <transition name="slide-left" mode="out-in">
        <div :key="obStep" class="ob-card">
          <div class="ob-question">{{ obQuestions[obStep - 1].q }}</div>
          <div class="ob-options">
            <div
              v-for="opt in obQuestions[obStep - 1].options"
              :key="opt"
              class="ob-opt"
              :class="{ selected: obAnswers[obStep - 1] === opt }"
              @click="selectOb(opt)"
            >{{ opt }}</div>
          </div>
        </div>
      </transition>

      <el-button v-if="obStep === 3 && obAnswers[2]" type="primary" size="large" class="submit-btn" @click="finishOnboarding">
        完成，去看看适合你的款式 →
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { sendCode as apiSendCode, login as apiLogin, updatePrefs } from '@/api/user'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const countdown = ref(0)
const showOnboarding = ref(false)
const obStep = ref(1)
const obAnswers = reactive(['', '', ''])

const form = reactive({ phone: '', code: '' })
const rules = {
  phone: [{ required: true, pattern: /^1[3-9]\d{9}$/, message: '请输入正确手机号', trigger: 'blur' }],
  code:  [{ required: true, len: 6, message: '请输入6位验证码', trigger: 'blur' }],
}

const obQuestions = [
  { q: '你的常见饰品佩戴场合？', options: ['日常通勤', '约会出行', '职场正式', '派对聚会'] },
  { q: '你偏好的饰品风格？',     options: ['简约极简', '优雅复古', '甜美少女', '个性先锋'] },
  { q: '你通常对哪类饰品感兴趣？', options: ['耳饰', '项链', '手链', '戒指'] },
]

async function sendCode() {
  if (!/^1[3-9]\d{9}$/.test(form.phone)) {
    ElMessage.warning('请先输入正确手机号')
    return
  }
  try {
    await apiSendCode(form.phone)
    ElMessage.success('验证码已发送，请查看后端控制台')
    countdown.value = 60
    const t = setInterval(() => {
      if (--countdown.value <= 0) clearInterval(t)
    }, 1000)
  } catch {
    // error already shown by http interceptor
  }
}

async function doLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await apiLogin(form.phone, form.code)
    const { token, user_info } = res.data
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user_info))
    showOnboarding.value = true
  } catch {
    // error already shown by http interceptor
  } finally {
    loading.value = false
  }
}

function mockWechat() {
  ElMessage.info('微信登录暂未接入，请使用手机号登录')
}

function skipLogin() {
  router.push('/home')
}

function selectOb(opt) {
  obAnswers[obStep.value - 1] = opt
  if (obStep.value < 3) {
    setTimeout(() => { obStep.value++ }, 300)
  }
}

async function finishOnboarding() {
  const [occasion, style] = obAnswers
  try {
    await updatePrefs({ occasion_prefs: [occasion], style_prefs: [style] })
  } catch {
    // non-blocking — proceed even if prefs save fails
  }
  router.push('/home')
}
</script>

<style scoped>
.login-page {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fdf6f0 0%, #f5e9f7 100%);
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 380px;
  background: #fff;
  border-radius: 20px;
  padding: 40px 32px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.1);
}

.brand {
  text-align: center;
  margin-bottom: 36px;
}

.brand-logo {
  font-size: 48px;
  color: #c0876a;
  line-height: 1;
}

.brand-name {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  letter-spacing: 4px;
  margin-top: 8px;
}

.brand-slogan {
  font-size: 13px;
  color: #999;
  margin-top: 6px;
}

.login-form { margin-bottom: 16px; }

.submit-btn {
  width: 100%;
  margin-top: 8px;
  border-radius: 24px;
  font-size: 16px;
}

.divider {
  text-align: center;
  color: #ccc;
  font-size: 13px;
  margin: 16px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}
.divider::before, .divider::after {
  content: '';
  flex: 1;
  border-top: 1px solid #eee;
}

.wechat-btn {
  width: 100%;
  border-radius: 24px;
  background: #07c160;
  color: #fff;
  border: none;
  font-size: 15px;
}

.wechat-icon { margin-right: 6px; }

.agreement {
  text-align: center;
  font-size: 12px;
  color: #bbb;
  margin-top: 20px;
}

.skip-btn {
  display: block;
  width: 100%;
  text-align: center;
  margin-top: 16px;
  color: #aaa;
  font-size: 13px;
}

/* Onboarding */
.onboarding {
  width: 100%;
  max-width: 380px;
}

.ob-progress {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 32px;
}

.ob-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ddd;
  transition: background 0.3s;
}

.ob-dot.active { background: #c0876a; }

.ob-card {
  background: #fff;
  border-radius: 20px;
  padding: 32px 24px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.1);
  margin-bottom: 24px;
}

.ob-question {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 24px;
  text-align: center;
}

.ob-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.ob-opt {
  padding: 16px 12px;
  border: 2px solid #eee;
  border-radius: 12px;
  text-align: center;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.ob-opt:hover { border-color: #c0876a; color: #c0876a; }
.ob-opt.selected { border-color: #c0876a; background: #fdf6f0; color: #c0876a; font-weight: 600; }

.slide-left-enter-active, .slide-left-leave-active { transition: all 0.3s ease; }
.slide-left-enter-from { opacity: 0; transform: translateX(40px); }
.slide-left-leave-to   { opacity: 0; transform: translateX(-40px); }
</style>
