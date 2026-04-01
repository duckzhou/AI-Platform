<template>
  <router-view />
</template>

<script setup>
</script>

<style>
/* ========== 企业级设计系统 ========== */

/* CSS 变量 - 设计令牌 */
:root {
  /* 主色调 - 科技蓝 */
  --primary-50: #e6f4ff;
  --primary-100: #bae0ff;
  --primary-200: #91caff;
  --primary-300: #69b1ff;
  --primary-400: #4096ff;
  --primary-500: #1677ff;
  --primary-600: #0958d9;
  --primary-700: #003eb3;
  --primary-800: #002c8c;
  --primary-900: #001d66;
  
  /* 成功色 */
  --success-500: #52c41a;
  --success-600: #389e0d;
  
  /* 警告色 */
  --warning-500: #faad14;
  --warning-600: #d48806;
  
  /* 错误色 */
  --error-500: #ff4d4f;
  --error-600: #cf1322;
  
  /* 中性色 */
  --gray-50: #fafafa;
  --gray-100: #f5f5f5;
  --gray-200: #e8e8e8;
  --gray-300: #d9d9d9;
  --gray-400: #bfbfbf;
  --gray-500: #8c8c8c;
  --gray-600: #595959;
  --gray-700: #434343;
  --gray-800: #262626;
  --gray-900: #1f1f1f;
  
  /* 背景色 */
  --bg-layout: #f0f2f5;
  --bg-container: #ffffff;
  --bg-elevated: #ffffff;
  
  /* 边框 */
  --border-color: #e8e8e8;
  --border-radius-sm: 6px;
  --border-radius-md: 8px;
  --border-radius-lg: 12px;
  --border-radius-xl: 16px;
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px 0 rgba(0, 0, 0, 0.02);
  --shadow-md: 0 6px 16px 0 rgba(0, 0, 0, 0.08), 0 3px 6px -4px rgba(0, 0, 0, 0.12), 0 9px 28px 8px rgba(0, 0, 0, 0.05);
  --shadow-lg: 0 6px 16px 0 rgba(0, 0, 0, 0.08), 0 3px 6px -4px rgba(0, 0, 0, 0.12), 0 9px 28px 8px rgba(0, 0, 0, 0.05);
  
  /* 间距 */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-xxl: 48px;
  
  /* 过渡 */
  --transition-fast: 0.15s ease;
  --transition-normal: 0.3s ease;
  --transition-slow: 0.5s ease;
  
  /* 字体 */
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans SC', sans-serif;
  --font-family-mono: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Mono', 'Droid Sans Mono', 'Source Code Pro', monospace;
  
  /* 字号 */
  --font-size-xs: 12px;
  --font-size-sm: 13px;
  --font-size-md: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 18px;
  --font-size-2xl: 20px;
  --font-size-3xl: 24px;
  --font-size-4xl: 30px;
}

/* ========== 全局重置 ========== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: var(--font-family);
  font-size: var(--font-size-md);
  line-height: 1.5714285714285714;
  color: var(--gray-800);
  background-color: var(--bg-layout);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

#app {
  height: 100%;
}

/* ========== 滚动条美化 ========== */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--gray-300);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--gray-400);
}

/* ========== Element Plus 主题覆盖 ========== */

/* 按钮 */
.el-button {
  font-weight: 500;
  border-radius: var(--border-radius-md);
  transition: all var(--transition-fast);
}

.el-button--primary {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  border: none;
  box-shadow: 0 2px 4px rgba(22, 119, 255, 0.2);
}

.el-button--primary:hover {
  background: linear-gradient(135deg, var(--primary-400) 0%, var(--primary-500) 100%);
  box-shadow: 0 4px 8px rgba(22, 119, 255, 0.3);
  transform: translateY(-1px);
}

.el-button--primary:active {
  transform: translateY(0);
}

/* 输入框 */
.el-input__wrapper,
.el-textarea__inner {
  border-radius: var(--border-radius-md) !important;
  transition: all var(--transition-fast) !important;
}

.el-input__wrapper:hover,
.el-textarea__inner:hover {
  box-shadow: 0 0 0 1px var(--primary-400) !important;
}

.el-input__wrapper.is-focus,
.el-textarea__inner:focus {
  box-shadow: 0 0 0 2px var(--primary-100), 0 0 0 3px var(--primary-500) !important;
}

/* 选择器 */
.el-select .el-input__wrapper {
  border-radius: var(--border-radius-md) !important;
}

/* 卡片 */
.el-card {
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

.el-card:hover {
  box-shadow: var(--shadow-md);
}

/* 表格 */
.el-table {
  border-radius: var(--border-radius-lg);
  overflow: hidden;
}

.el-table th.el-table__cell {
  background: var(--gray-50);
  font-weight: 600;
  color: var(--gray-700);
}

.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell {
  background: var(--gray-50);
}

/* 标签页 */
.el-tabs__item {
  font-weight: 500;
  font-size: var(--font-size-md);
}

.el-tabs__item.is-active {
  color: var(--primary-500);
  font-weight: 600;
}

.el-tabs__active-bar {
  height: 3px;
  border-radius: 2px;
}

/* 菜单 */
.el-menu {
  border-right: none !important;
}

.el-menu-item {
  margin: 4px 8px;
  border-radius: var(--border-radius-md);
  transition: all var(--transition-fast);
}

.el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.08) !important;
}

.el-menu-item.is-active {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%) !important;
  color: #fff !important;
}

/* 对话框 */
.el-dialog {
  border-radius: var(--border-radius-xl);
  overflow: hidden;
}

.el-dialog__header {
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--border-color);
  margin-right: 0;
}

.el-dialog__title {
  font-weight: 600;
  font-size: var(--font-size-lg);
}

.el-dialog__body {
  padding: var(--spacing-xl);
}

.el-dialog__footer {
  padding: var(--spacing-lg) var(--spacing-xl);
  border-top: 1px solid var(--border-color);
}

/* 下拉菜单 */
.el-dropdown-menu {
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-xs);
}

.el-dropdown-menu__item {
  border-radius: var(--border-radius-sm);
  padding: 8px 16px;
  margin: 2px 0;
}

.el-dropdown-menu__item:hover {
  background-color: var(--primary-50);
  color: var(--primary-600);
}

/* 消息提示 */
.el-message {
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-lg);
}

/* 复选框 */
.el-checkbox__input.is-checked .el-checkbox__inner {
  background-color: var(--primary-500);
  border-color: var(--primary-500);
}

/* 单选框 */
.el-radio-button__inner {
  border-radius: var(--border-radius-md) !important;
}

.el-radio-button:first-child .el-radio-button__inner {
  border-radius: var(--border-radius-md) 0 0 var(--border-radius-md) !important;
}

.el-radio-button:last-child .el-radio-button__inner {
  border-radius: 0 var(--border-radius-md) var(--border-radius-md) 0 !important;
}

/* 分页 */
.el-pagination.is-background .el-pager li:not(.is-disabled).is-active {
  background-color: var(--primary-500);
}

/* 空状态 */
.el-empty__description p {
  color: var(--gray-500);
}

/* ========== 动画 ========== */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes shimmer {
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
}

/* ========== 工具类 ========== */
.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}

.animate-slideIn {
  animation: slideIn 0.3s ease-out;
}

.text-gradient {
  background: linear-gradient(135deg, var(--primary-400) 0%, var(--primary-600) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.glass-effect {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

/* 骨架屏加载效果 */
.skeleton {
  background: linear-gradient(90deg, var(--gray-100) 25%, var(--gray-200) 50%, var(--gray-100) 75%);
  background-size: 200px 100%;
  animation: shimmer 1.5s infinite;
}
</style>
