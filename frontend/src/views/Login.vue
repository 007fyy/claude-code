<template>
  <div class="login-page">
    <!-- Left Visual -->
    <div class="login-visual">
      <div class="login-ring ring-1"></div>
      <div class="login-ring ring-2"></div>
      <div class="login-ring ring-3"></div>
      <div class="login-ring ring-4"></div>

      <div class="login-brand-title">&#128142; 珑饰</div>
      <div class="login-brand-sub">智能珠宝 · 虚拟试戴 · AI 精准推荐</div>

      <div class="login-features">
        <div class="login-feature">
          <div class="login-feature-icon">&#10024;</div>
          <div class="login-feature-text">
            <div class="login-feature-title">AI 智能导购</div>
            <div class="login-feature-desc">4 步问答，精准匹配 96% 满意度的个性化推荐</div>
          </div>
        </div>
        <div class="login-feature">
          <div class="login-feature-icon">&#128247;</div>
          <div class="login-feature-text">
            <div class="login-feature-title">AR 虚拟试戴</div>
            <div class="login-feature-desc">实时摄像头叠加，买前先试，降低 40% 退货率</div>
          </div>
        </div>
        <div class="login-feature">
          <div class="login-feature-icon">&#128100;</div>
          <div class="login-feature-text">
            <div class="login-feature-title">脸型精准匹配</div>
            <div class="login-feature-desc">AI 分析您的脸型轮廓，推荐最适合的饰品款式</div>
          </div>
        </div>
      </div>

      <div class="login-testimonial">
        <div class="login-testimonial-text">
          "用了 AI 导购推荐的耳环，朋友都说太适合我了！AR 试戴功能真的太好用，再也不怕买错了。"
        </div>
        <div class="login-testimonial-user">
          <div class="login-testimonial-avatar">李</div>
          <div>
            <div class="login-testimonial-name">李小明</div>
            <div class="login-testimonial-since">珑饰会员 · 2024 年加入</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Form -->
    <div class="login-form-wrap">
      <div v-if="!showOnboarding" class="login-card">
        <!-- Tabs -->
        <div class="login-tabs">
          <div class="login-tab" :class="{ active: mode === 'login' }" @click="mode = 'login'">登录账号</div>
          <div class="login-tab" :class="{ active: mode === 'register' }" @click="mode = 'register'">新用户注册</div>
        </div>

        <!-- Login: email + password -->
        <div v-if="mode === 'login'" class="step-wrap">
          <el-form :model="form" ref="loginRef" :rules="loginRules" class="auth-form">
            <el-form-item prop="email">
              <el-input v-model="form.email" placeholder="请输入 QQ 邮箱" size="large" @keyup.enter="$refs.loginPwInput?.focus()">
                <template #suffix>@qq.com</template>
              </el-input>
            </el-form-item>
            <el-form-item prop="password">
              <el-input ref="loginPwInput" v-model="form.password" placeholder="请输入密码" size="large" type="password" show-password @keyup.enter="handleLogin" />
            </el-form-item>
            <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="handleLogin">
              登录
            </el-button>
          </el-form>
        </div>

        <!-- Register: email + code + password -->
        <div v-if="mode === 'register'" class="step-wrap">
          <div v-if="regStep === 1">
            <el-form :model="form" ref="emailRef" :rules="emailRules" class="auth-form">
              <el-form-item prop="email">
                <el-input v-model="form.email" placeholder="请输入 QQ 邮箱" size="large" @keyup.enter="handleSendCode">
                  <template #suffix>@qq.com</template>
                </el-input>
              </el-form-item>
              <el-button type="primary" size="large" class="submit-btn" :loading="sending" @click="handleSendCode">
                获取验证码
              </el-button>
            </el-form>
          </div>

          <div v-if="regStep === 2">
            <div class="step-hint hint-register">新用户注册，请设置密码</div>
            <div class="step-email">{{ fullEmail }}</div>

            <el-form :model="form" ref="verifyRef" :rules="verifyRules" class="auth-form">
              <el-form-item prop="code">
                <el-input v-model="form.code" placeholder="请输入 6 位验证码" maxlength="6" size="large">
                  <template #append>
                    <el-button :disabled="countdown > 0" @click="resendCode" link>
                      {{ countdown > 0 ? `${countdown}s` : '重新发送' }}
                    </el-button>
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item prop="password">
                <el-input v-model="form.password" placeholder="设置密码（8位以上含字母+数字）" size="large" type="password" show-password />
              </el-form-item>
              <div class="pw-strength">
                <div class="pw-bar" :class="pwLevel >= 1 ? pwClass : ''" />
                <div class="pw-bar" :class="pwLevel >= 2 ? pwClass : ''" />
                <div class="pw-bar" :class="pwLevel >= 3 ? pwClass : ''" />
              </div>
              <el-form-item prop="confirmPwd">
                <el-input v-model="form.confirmPwd" placeholder="确认密码" size="large" type="password" show-password />
              </el-form-item>
              <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="handleVerify">
                注册
              </el-button>
            </el-form>
            <el-button link class="back-btn" @click="regStep = 1">&#8592; 换一个邮箱</el-button>
          </div>
        </div>

        <div class="agreement">
          继续即同意
          <el-link type="primary" :underline="false">《用户协议》</el-link>
          <el-link type="primary" :underline="false">《隐私政策》</el-link>
        </div>
        <el-button link class="skip-btn" @click="skipLogin">跳过，先看看 &#8594;</el-button>
      </div>

      <!-- Onboarding -->
      <div v-else class="onboarding">
        <div class="ob-progress">
          <span v-for="i in 3" :key="i" class="ob-dot" :class="{ active: i === obStep }" />
        </div>
        <transition name="slide-left" mode="out-in">
          <div :key="obStep" class="ob-card">
            <div class="ob-question">{{ obQuestions[obStep - 1].q }}</div>
            <div class="ob-options">
              <div v-for="opt in obQuestions[obStep - 1].options" :key="opt"
                class="ob-opt" :class="{ selected: obAnswers[obStep - 1] === opt }"
                @click="selectOb(opt)">{{ opt }}</div>
            </div>
          </div>
        </transition>
        <el-button v-if="obStep === 3 && obAnswers[2]" type="primary" size="large" class="submit-btn" @click="finishOnboarding">
          完成，去看看适合你的款式 &#8594;
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { sendCode as apiSendCode, login as apiLogin, verify as apiVerify, updatePrefs } from '@/api/user'

const router = useRouter()
const route = useRoute()

const mode = ref('login')
const regStep = ref(1)
const sending = ref(false)
const loading = ref(false)
const countdown = ref(0)
const showOnboarding = ref(false)
const obStep = ref(1)
const obAnswers = reactive(['', '', ''])

const loginRef = ref(null)
const emailRef = ref(null)
const verifyRef = ref(null)

const form = reactive({
  email: '',
  code: '',
  password: '',
  confirmPwd: '',
})

const fullEmail = computed(() => {
  const e = form.email.trim()
  return e.includes('@') ? e : `${e}@qq.com`
})

const pwLevel = computed(() => {
  const pw = form.password
  if (!pw) return 0
  let s = 0
  if (pw.length >= 8) s++
  if (/[a-zA-Z]/.test(pw) && /[0-9]/.test(pw)) s++
  if (/[!@#$%^&*]/.test(pw)) s++
  return s
})
const pwClass = computed(() => ['', 'weak', 'medium', 'strong'][pwLevel.value] || '')

const loginRules = {
  email: [{ required: true, message: '请输入 QQ 邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const emailRules = {
  email: [{ required: true, message: '请输入 QQ 邮箱', trigger: 'blur' }],
}

const confirmPwdValidator = (_r, v, cb) => {
  if (v !== form.password) cb(new Error('两次密码不一致'))
  else cb()
}

const verifyRules = {
  code: [{ required: true, len: 6, message: '请输入6位验证码', trigger: 'blur' }],
  password: [{ required: true, min: 8, message: '密码至少8位', trigger: 'blur' }],
  confirmPwd: [{ required: true, validator: confirmPwdValidator, trigger: 'blur' }],
}

const obQuestions = [
  { q: '你的常见饰品佩戴场合？', options: ['日常通勤', '约会出行', '职场正式', '派对聚会'] },
  { q: '你偏好的饰品风格？', options: ['简约极简', '优雅复古', '甜美少女', '个性先锋'] },
  { q: '你通常对哪类饰品感兴趣？', options: ['耳饰', '项链', '手链', '戒指'] },
]

function startCountdown() {
  countdown.value = 60
  const t = setInterval(() => {
    if (--countdown.value <= 0) clearInterval(t)
  }, 1000)
}

async function handleLogin() {
  await loginRef.value.validate()
  loading.value = true
  try {
    const res = await apiLogin({ email: fullEmail.value, password: form.password })
    if (res && res.code === 0) {
      const { token, user } = res.data
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      ElMessage.success('登录成功，欢迎回来')
      router.push(route.query.redirect || '/home')
    }
  } catch (e) {
    console.error('[登录失败]', e?.message || e)
  } finally { loading.value = false }
}

async function handleSendCode() {
  await emailRef.value.validate()
  sending.value = true
  try {
    const res = await apiSendCode(fullEmail.value)
    if (res.data.is_registered) {
      ElMessage.info('该邮箱已注册，请切换到登录')
      mode.value = 'login'
      return
    }
    ElMessage.success('验证码已发送到您的邮箱，请查收')
    startCountdown()
    regStep.value = 2
  } catch { /* interceptor */ }
  finally { sending.value = false }
}

async function resendCode() {
  try {
    await apiSendCode(fullEmail.value)
    ElMessage.success('验证码已重新发送')
    startCountdown()
  } catch { /* interceptor */ }
}

async function handleVerify() {
  await verifyRef.value.validate()
  loading.value = true
  try {
    const payload = { email: fullEmail.value, code: form.code, password: form.password }
    const res = await apiVerify(payload)
    if (res && res.code === 0) {
      ElMessage.success('注册成功，请登录')
      form.code = ''
      form.password = ''
      form.confirmPwd = ''
      regStep.value = 1
      mode.value = 'login'
    }
  } catch (e) {
    console.error('[注册失败]', e?.message || e)
  } finally { loading.value = false }
}

function skipLogin() { router.push(route.query.redirect || '/home') }

function selectOb(opt) {
  obAnswers[obStep.value - 1] = opt
  if (obStep.value < 3) setTimeout(() => { obStep.value++ }, 300)
}

async function finishOnboarding() {
  const [occasion, style] = obAnswers
  try { await updatePrefs({ occasion_prefs: [occasion], style_prefs: [style] }) } catch {}
  router.push(route.query.redirect || '/home')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 480px;
}

/* ── Left Visual Panel ── */
.login-visual {
  background: linear-gradient(135deg, #1A1714 0%, #2D1810 40%, #4A3020 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  position: relative;
  overflow: hidden;
}

.login-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(196,144,106,.12);
}
.ring-1 { width: 300px; height: 300px; top: -80px; left: -80px; }
.ring-2 { width: 500px; height: 500px; top: -150px; left: -150px; }
.ring-3 { width: 400px; height: 400px; bottom: -120px; right: -120px; }
.ring-4 { width: 200px; height: 200px; bottom: -40px; right: -40px; border-color: rgba(196,144,106,.25); }

.login-brand-title {
  font-size: 36px;
  font-weight: 900;
  color: #fff;
  letter-spacing: 1px;
  margin-bottom: 12px;
  z-index: 1;
}
.login-brand-sub {
  font-size: 14px;
  color: rgba(255,255,255,.5);
  z-index: 1;
  margin-bottom: 48px;
  letter-spacing: .5px;
}

.login-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
  z-index: 1;
  width: 100%;
  max-width: 340px;
}
.login-feature {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 18px;
  background: rgba(255,255,255,.05);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,.08);
  transition: background .2s;
}
.login-feature:hover { background: rgba(255,255,255,.09); }
.login-feature-icon {
  width: 44px; height: 44px;
  background: rgba(196,144,106,.2);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}
.login-feature-title {
  font-size: 14px; font-weight: 700; color: #fff; margin-bottom: 3px;
}
.login-feature-desc {
  font-size: 12px; color: rgba(255,255,255,.5); line-height: 1.5;
}

.login-testimonial {
  margin-top: 40px;
  padding: 20px;
  background: rgba(196,144,106,.1);
  border: 1px solid rgba(196,144,106,.25);
  border-radius: 12px;
  z-index: 1;
  width: 100%;
  max-width: 340px;
}
.login-testimonial-text {
  font-size: 13px;
  color: rgba(255,255,255,.75);
  line-height: 1.7;
  font-style: italic;
  margin-bottom: 12px;
}
.login-testimonial-user {
  display: flex; align-items: center; gap: 10px;
}
.login-testimonial-avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: #C4906A;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; color: #fff;
  flex-shrink: 0;
}
.login-testimonial-name {
  font-size: 12px; font-weight: 700; color: rgba(255,255,255,.7);
}
.login-testimonial-since {
  font-size: 11px; color: rgba(255,255,255,.35);
}

/* ── Right Form Panel ── */
.login-form-wrap {
  background: #FAF9F7;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.login-card {
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,.08);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-tabs {
  display: flex;
  background: #FAF9F7;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 32px;
}
.login-tab {
  flex: 1; text-align: center; padding: 10px;
  font-size: 14px; font-weight: 700;
  color: #999; border-radius: 9px;
  cursor: pointer; transition: all .18s;
}
.login-tab.active {
  background: #fff; color: #1A1714;
  box-shadow: 0 2px 8px rgba(0,0,0,.08);
}

.step-wrap { margin-bottom: 16px; }
.step-hint {
  text-align: center; font-size: 14px; font-weight: 600;
  padding: 10px 16px; border-radius: 10px; margin-bottom: 12px;
}
.hint-register { background: #fff3e0; color: #e65100; }
.step-email { text-align: center; font-size: 13px; color: #999; margin-bottom: 20px; }

.auth-form { margin-bottom: 8px; }
.submit-btn {
  width: 100%; margin-top: 8px;
  border-radius: 12px; font-size: 16px; font-weight: 800;
  background: linear-gradient(135deg, #1A1714, #4A3020);
  border-color: transparent;
}
.submit-btn:hover {
  background: linear-gradient(135deg, #2D231A, #6B4226);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(26,23,20,.25);
}
.back-btn {
  display: block; width: 100%; text-align: center;
  margin-top: 12px; color: #999; font-size: 13px;
}

.pw-strength { display: flex; gap: 4px; margin: -8px 0 12px; padding: 0 2px; }
.pw-bar { flex: 1; height: 4px; background: #eee; border-radius: 2px; transition: background .3s; }
.pw-bar.weak { background: #f44336; }
.pw-bar.medium { background: #ff9800; }
.pw-bar.strong { background: #4caf50; }

.agreement {
  text-align: center; font-size: 12px; color: #bbb; margin-top: 20px; line-height: 1.6;
}
.skip-btn {
  display: block; width: 100%; text-align: center;
  margin-top: 16px; color: #C4906A; font-size: 13px; font-weight: 600;
}
.skip-btn:hover { color: #a87456; }

/* ── Onboarding ── */
.onboarding { width: 100%; max-width: 400px; }
.ob-progress { display: flex; justify-content: center; gap: 8px; margin-bottom: 32px; }
.ob-dot { width: 8px; height: 8px; border-radius: 50%; background: #ddd; transition: background .3s; }
.ob-dot.active { background: #C4906A; }
.ob-card {
  background: #fff; border-radius: 20px; padding: 32px 24px;
  box-shadow: 0 8px 32px rgba(0,0,0,.08); margin-bottom: 24px;
}
.ob-question { font-size: 18px; font-weight: 600; color: #1A1714; margin-bottom: 24px; text-align: center; }
.ob-options { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.ob-opt {
  padding: 16px 12px; border: 2px solid #eee; border-radius: 12px;
  text-align: center; font-size: 14px; cursor: pointer; transition: all .2s;
}
.ob-opt:hover { border-color: #C4906A; color: #C4906A; }
.ob-opt.selected { border-color: #C4906A; background: #fdf6f0; color: #C4906A; font-weight: 600; }

/* ── Transitions ── */
.slide-left-enter-active, .slide-left-leave-active { transition: all .3s ease; }
.slide-left-enter-from { opacity: 0; transform: translateX(40px); }
.slide-left-leave-to { opacity: 0; transform: translateX(-40px); }
</style>
