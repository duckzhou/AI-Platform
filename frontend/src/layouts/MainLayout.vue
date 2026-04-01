<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapsed ? '64px' : '220px'" class="sidebar">
      <!-- Logo -->
      <div class="logo" @click="toggleCollapse">
        <div class="logo-icon">
          <svg viewBox="0 0 32 32" width="32" height="32">
            <defs>
              <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#4096ff" />
                <stop offset="100%" style="stop-color:#1677ff" />
              </linearGradient>
            </defs>
            <circle cx="16" cy="16" r="14" fill="url(#logoGradient)" />
            <path d="M10 16 L14 20 L22 12" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <transition name="fade">
          <span v-if="!isCollapsed" class="logo-text">AI 创作平台</span>
        </transition>
      </div>
      
      <!-- 导航菜单 -->
      <nav class="nav-menu">
        <div class="nav-section">
          <transition name="fade">
            <div v-if="!isCollapsed" class="nav-section-title">核心功能</div>
          </transition>
          
          <router-link 
            v-for="item in mainMenuItems" 
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: $route.path === item.path }"
            @click.native="console.log('导航到:', item.path, item.label)"
          >
            <el-icon :size="20"><component :is="item.icon" /></el-icon>
            <transition name="fade">
              <span v-if="!isCollapsed" class="nav-text">{{ item.label }}</span>
            </transition>
          </router-link>
        </div>
        
        <div class="nav-section">
          <transition name="fade">
            <div v-if="!isCollapsed" class="nav-section-title">资源管理</div>
          </transition>
          
          <router-link 
            v-for="item in resourceMenuItems" 
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: $route.path === item.path }"
          >
            <el-icon :size="20"><component :is="item.icon" /></el-icon>
            <transition name="fade">
              <span v-if="!isCollapsed" class="nav-text">{{ item.label }}</span>
            </transition>
          </router-link>
        </div>
      </nav>
      
      <!-- 折叠按钮 -->
      <div class="collapse-btn" @click="toggleCollapse">
        <el-icon :size="18">
          <component :is="isCollapsed ? Expand : Fold" />
        </el-icon>
      </div>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部栏 -->
      <el-header class="header">
        <div class="header-left">
          <h1 class="page-title">{{ currentPageTitle }}</h1>
        </div>
        
        <div class="header-right">
          <!-- 额度显示 -->
          <div class="quota-badge">
            <el-icon><Coin /></el-icon>
            <span class="quota-label">剩余额度</span>
            <span class="quota-value">{{ userStore.quota.remaining_quota }}</span>
          </div>
          
          <!-- 用户下拉 -->
          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-dropdown">
              <el-avatar :size="36" class="user-avatar">
                {{ userStore.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <div class="user-info">
                <span class="user-name">{{ userStore.username }}</span>
                <span class="user-role">普通用户</span>
              </div>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="quota">
                  <el-icon><Coin /></el-icon>
                  额度充值
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 主内容 -->
      <el-main class="main-content">
        <transition name="page" mode="out-in">
          <router-view />
        </transition>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getQuotaInfo } from '@/api/quota'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ChatDotRound, MagicStick, List, Picture, Coin, User, 
  ArrowDown, SwitchButton, Expand, Fold
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const isCollapsed = ref(false)

// 主菜单项
const mainMenuItems = [
  { path: '/chat', label: 'AI 对话', icon: 'ChatDotRound' },
  { path: '/create', label: 'AI 创作', icon: 'MagicStick' },
  { path: '/tasks', label: '任务管理', icon: 'List' },
]

// 资源菜单项
const resourceMenuItems = [
  { path: '/materials', label: '素材管理', icon: 'Picture' },
  { path: '/quota', label: '额度中心', icon: 'Coin' },
  { path: '/profile', label: '个人中心', icon: 'User' },
]

// 页面标题映射
const pageTitleMap = {
  '/chat': 'AI 对话',
  '/create': 'AI 创作',
  '/tasks': '任务管理',
  '/materials': '素材管理',
  '/quota': '额度中心',
  '/profile': '个人中心',
}

const currentPageTitle = computed(() => {
  return pageTitleMap[route.path] || 'AI 创作平台'
})

onMounted(async () => {
  const res = await getQuotaInfo()
  if (res.code === 200) {
    userStore.setQuota(res.data)
  }
})

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'quota':
      router.push('/quota')
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        userStore.logout()
        router.push('/login')
        ElMessage.success('已退出登录')
      })
      break
  }
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
  overflow: hidden;
}

/* ========== 侧边栏 ========== */
.sidebar {
  background: linear-gradient(180deg, #1a1f36 0%, #151929 100%);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  position: relative;
  z-index: 100;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-text {
  margin-left: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
  letter-spacing: 0.5px;
}

/* 导航菜单 */
.nav-menu {
  flex: 1;
  padding: 16px 12px;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-section {
  margin-bottom: 24px;
}

.nav-section-title {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.35);
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 0 12px;
  margin-bottom: 8px;
  white-space: nowrap;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin: 4px 0;
  border-radius: var(--border-radius-md);
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
  transition: all var(--transition-fast);
  position: relative;
  overflow: hidden;
}

.nav-item:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

.nav-item.active {
  color: #fff;
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.3);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background: #fff;
  border-radius: 0 2px 2px 0;
}

.nav-text {
  margin-left: 12px;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}

/* 折叠按钮 */
.collapse-btn {
  position: absolute;
  right: -12px;
  top: 80px;
  width: 24px;
  height: 24px;
  background: var(--primary-500);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all var(--transition-fast);
  z-index: 101;
}

.collapse-btn:hover {
  background: var(--primary-400);
  transform: scale(1.1);
}

/* ========== 主容器 ========== */
.main-container {
  background: var(--bg-layout);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ========== 顶部栏 ========== */
.header {
  height: 64px;
  background: #fff;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--gray-800);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* 额度徽章 */
.quota-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--primary-100) 100%);
  border-radius: 24px;
  border: 1px solid var(--primary-200);
}

.quota-badge .el-icon {
  color: var(--primary-500);
}

.quota-label {
  font-size: 13px;
  color: var(--gray-600);
}

.quota-value {
  font-size: 15px;
  font-weight: 600;
  color: var(--primary-600);
}

/* 用户下拉 */
.user-dropdown {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px 6px 6px;
  border-radius: 24px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.user-dropdown:hover {
  background: var(--gray-100);
}

.user-avatar {
  background: linear-gradient(135deg, var(--primary-400) 0%, var(--primary-600) 100%);
  color: #fff;
  font-weight: 600;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-800);
}

.user-role {
  font-size: 12px;
  color: var(--gray-500);
}

.dropdown-arrow {
  color: var(--gray-400);
  transition: transform var(--transition-fast);
}

.user-dropdown:hover .dropdown-arrow {
  transform: rotate(180deg);
}

/* ========== 主内容 ========== */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* ========== 动画 ========== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.page-enter-active,
.page-leave-active {
  transition: all 0.3s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
