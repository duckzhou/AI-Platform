<template>
  <div class="profile-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">个人中心</h2>
      <p class="page-desc">管理您的账户信息和安全设置</p>
    </div>
    
    <div class="profile-content">
      <!-- 个人信息卡片 -->
      <div class="profile-card">
        <div class="card-header">
          <h3>个人信息</h3>
        </div>
        <div class="card-body">
          <div class="avatar-section">
            <div class="avatar-wrapper">
              <el-avatar :size="80" class="user-avatar">
                {{ profileForm.username?.charAt(0)?.toUpperCase() || 'U' }}
              </el-avatar>
              <div class="avatar-upload">
                <el-button size="small" text>
                  <el-icon><Camera /></el-icon>
                  更换头像
                </el-button>
              </div>
            </div>
            <div class="user-basic">
              <h4 class="user-name">{{ profileForm.username || '用户' }}</h4>
              <p class="user-email">{{ profileForm.email }}</p>
              <div class="user-badge">
                <el-tag type="success" effect="light">
                  <el-icon><CircleCheck /></el-icon>
                  <span>正常</span>
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 基本信息表单 -->
      <div class="form-card">
        <div class="card-header">
          <h3>基本信息</h3>
          <span class="card-desc">修改您的个人资料</span>
        </div>
        <div class="card-body">
          <el-form :model="profileForm" label-position="top" class="profile-form">
            <div class="form-row">
              <div class="form-item">
                <label class="form-label">用户名</label>
                <el-input v-model="profileForm.username" placeholder="请输入用户名" />
              </div>
              <div class="form-item">
                <label class="form-label">邮箱</label>
                <el-input v-model="profileForm.email" disabled>
                  <template #suffix>
                    <el-tag size="small" type="success">已验证</el-tag>
                  </template>
                </el-input>
              </div>
            </div>
            
            <div class="form-actions">
              <el-button type="primary" @click="updateProfile">
                <el-icon><Check /></el-icon>
                保存修改
              </el-button>
            </div>
          </el-form>
        </div>
      </div>
      
      <!-- 安全设置 -->
      <div class="form-card">
        <div class="card-header">
          <h3>安全设置</h3>
          <span class="card-desc">修改您的登录密码</span>
        </div>
        <div class="card-body">
          <el-form :model="passwordForm" label-position="top" class="password-form">
            <div class="form-item full">
              <label class="form-label">当前密码</label>
              <el-input 
                v-model="passwordForm.old_password" 
                type="password" 
                placeholder="请输入当前密码"
                show-password
              />
            </div>
            <div class="form-row">
              <div class="form-item">
                <label class="form-label">新密码</label>
                <el-input 
                  v-model="passwordForm.new_password" 
                  type="password" 
                  placeholder="请输入新密码"
                  show-password
                />
              </div>
              <div class="form-item">
                <label class="form-label">确认新密码</label>
                <el-input 
                  v-model="passwordForm.confirm_password" 
                  type="password" 
                  placeholder="请再次输入新密码"
                  show-password
                />
              </div>
            </div>
            
            <div class="form-actions">
              <el-button type="primary" @click="handleChangePassword">
                <el-icon><Lock /></el-icon>
                修改密码
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
import { User, Camera, CircleCheck, Check, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getProfile, updateProfile as updateProfileApi, changePassword as changePasswordApi } from '@/api/auth'

const userStore = useUserStore()

const profileForm = ref({
  username: '',
  email: ''
})

const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

onMounted(async () => {
  await loadProfile()
})

const loadProfile = async () => {
  const res = await getProfile()
  if (res.code === 200) {
    profileForm.value = {
      username: res.data.username,
      email: res.data.email
    }
    userStore.userInfo = res.data
  }
}

const updateProfile = async () => {
  const res = await updateProfileApi({ username: profileForm.value.username })
  if (res.code === 200) {
    ElMessage.success('修改成功')
    await loadProfile()
  }
}

const handleChangePassword = async () => {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  
  const res = await changePasswordApi({
    old_password: passwordForm.value.old_password,
    new_password: passwordForm.value.new_password
  })
  
  if (res.code === 200) {
    ElMessage.success('密码修改成功')
    passwordForm.value = {
      old_password: '',
      new_password: '',
      confirm_password: ''
    }
  }
}
</script>

<style scoped>
.profile-container {
  background: #fff;
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

/* 页面头部 */
.page-header {
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--gray-800);
  margin: 0 0 4px;
}

.page-desc {
  font-size: 14px;
  color: var(--gray-500);
  margin: 0;
}

.profile-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 卡片样式 */
.profile-card,
.form-card {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
}

.card-header {
  padding: 16px 20px;
  background: var(--gray-50);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--gray-800);
  margin: 0;
}

.card-desc {
  font-size: 13px;
  color: var(--gray-500);
}

.card-body {
  padding: 24px;
}

/* 头像区域 */
.avatar-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  background: linear-gradient(135deg, var(--primary-400) 0%, var(--primary-600) 100%);
  color: #fff;
  font-size: 28px;
  font-weight: 600;
}

.avatar-upload .el-button {
  font-size: 12px;
  color: var(--gray-500);
}

.user-basic {
  flex: 1;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  color: var(--gray-800);
  margin: 0 0 4px;
}

.user-email {
  font-size: 14px;
  color: var(--gray-500);
  margin: 0 0 12px;
}

.user-badge .el-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* 表单样式 */
.profile-form,
.password-form {
  max-width: 600px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item.full {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--gray-700);
}

.form-actions {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}
</style>
