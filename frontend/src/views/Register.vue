<template>
  <div class="register-page">
    <!-- 左侧品牌区域 -->
    <div class="brand-section">
      <div class="brand-content">
        <div class="brand-logo">
          <svg viewBox="0 0 48 48" width="56" height="56">
            <defs>
              <linearGradient id="brandGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#4096ff" />
                <stop offset="100%" style="stop-color:#1677ff" />
              </linearGradient>
            </defs>
            <circle cx="24" cy="24" r="22" fill="url(#brandGradient)" />
            <path d="M14 24 L20 30 L34 16" stroke="white" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h1 class="brand-title">AI 创作平台</h1>
        <p class="brand-desc">智能创作，无限可能</p>
        
        <div class="benefits">
          <h3>注册即可享受</h3>
          <div class="benefit-list">
            <div class="benefit-item">
              <el-icon><CircleCheck /></el-icon>
              <span>免费体验额度</span>
            </div>
            <div class="benefit-item">
              <el-icon><CircleCheck /></el-icon>
              <span>多种 AI 模型选择</span>
            </div>
            <div class="benefit-item">
              <el-icon><CircleCheck /></el-icon>
              <span>素材云端存储</span>
            </div>
            <div class="benefit-item">
              <el-icon><CircleCheck /></el-icon>
              <span>任务历史记录</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="brand-decoration">
        <div class="decoration-circle c1"></div>
        <div class="decoration-circle c2"></div>
        <div class="decoration-circle c3"></div>
      </div>
    </div>
    
    <!-- 右侧注册区域 -->
    <div class="register-section">
      <div class="register-box">
        <div class="register-header">
          <h2>创建账户</h2>
          <p>开启您的 AI 创作之旅</p>
        </div>
        
        <el-form :model="form" :rules="rules" ref="formRef" class="register-form">
          <el-form-item prop="email">
            <label class="form-label">邮箱地址</label>
            <el-input
              v-model="form.email"
              placeholder="请输入邮箱"
              size="large"
              class="form-input"
            >
              <template #prefix>
                <el-icon><Message /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item prop="username">
            <label class="form-label">用户名 <span class="optional">(可选)</span></label>
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              size="large"
              class="form-input"
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item prop="password">
            <label class="form-label">密码</label>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码（至少6位）"
              size="large"
              class="form-input"
              show-password
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item prop="confirmPassword">
            <label class="form-label">确认密码</label>
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              size="large"
              class="form-input"
              show-password
              @keyup.enter="handleRegister"
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item>
            <el-checkbox v-model="agreeTerms">
              我已阅读并同意
              <el-button type="primary" text size="small">服务条款</el-button>
              和
              <el-button type="primary" text size="small">隐私政策</el-button>
            </el-checkbox>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="register-btn"
              :loading="loading"
              :disabled="!agreeTerms"
              @click="handleRegister"
            >
              <span v-if="!loading">立即注册</span>
              <span v-else>注册中...</span>
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="register-footer">
          <span>已有账号？</span>
          <el-button type="primary" @click="goLogin">立即登录</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Message, CircleCheck } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { register } from '@/api/auth'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const agreeTerms = ref(false)

const form = reactive({
  email: '',
  username: '',
  password: '',
  confirmPassword: ''
})

const validatePass2 = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await register({
      email: form.email,
      username: form.username,
      password: form.password
    })
    if (res.code === 200) {
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
}

const goLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
}

/* 左侧品牌区域 */
.brand-section {
  flex: 1;
  background: linear-gradient(135deg, #1a1f36 0%, #151929 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  padding: 60px;
}

.brand-content {
  text-align: center;
  position: relative;
  z-index: 1;
}

.brand-logo {
  margin-bottom: 24px;
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 12px;
  letter-spacing: -0.5px;
}

.brand-desc {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 48px;
}

.benefits {
  max-width: 280px;
  margin: 0 auto;
}

.benefits h3 {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.benefit-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.benefit-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.benefit-item .el-icon {
  color: var(--success-500);
  font-size: 18px;
}

/* 装饰圆圈 */
.brand-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  opacity: 0.1;
}

.c1 {
  width: 600px;
  height: 600px;
  top: -200px;
  right: -200px;
}

.c2 {
  width: 400px;
  height: 400px;
  bottom: -100px;
  left: -100px;
}

.c3 {
  width: 200px;
  height: 200px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 右侧注册区域 */
.register-section {
  width: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: #fff;
  overflow-y: auto;
}

.register-box {
  width: 100%;
  max-width: 380px;
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: var(--gray-800);
  margin: 0 0 8px;
}

.register-header p {
  font-size: 14px;
  color: var(--gray-500);
  margin: 0;
}

.register-form {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--gray-700);
  margin-bottom: 8px;
}

.form-label .optional {
  font-size: 12px;
  color: var(--gray-400);
  font-weight: 400;
}

.form-input :deep(.el-input__wrapper) {
  padding: 4px 16px;
  border-radius: var(--border-radius-md);
  border: 2px solid var(--border-color);
  box-shadow: none;
  transition: all var(--transition-fast);
}

.form-input :deep(.el-input__wrapper:hover) {
  border-color: var(--gray-300);
}

.form-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px var(--primary-100);
}

.register-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: var(--border-radius-md);
  margin-top: 8px;
}

.register-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.register-footer span {
  font-size: 14px;
  color: var(--gray-500);
}

.register-footer .el-button {
  font-weight: 500;
}

/* 响应式 */
@media (max-width: 1024px) {
  .brand-section {
    display: none;
  }
  
  .register-section {
    width: 100%;
  }
}
</style>
