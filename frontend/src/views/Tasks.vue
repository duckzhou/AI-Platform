<template>
  <div class="tasks-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">任务管理</h2>
        <p class="page-desc">查看和管理您的 AI 创作任务</p>
      </div>
      <div class="header-right">
        <el-select v-model="filterStatus" placeholder="全部状态" clearable class="status-select" @change="loadTasks">
          <el-option label="待执行" value="pending">
            <div class="status-option">
              <span class="status-dot pending"></span>
              <span>待执行</span>
            </div>
          </el-option>
          <el-option label="执行中" value="running">
            <div class="status-option">
              <span class="status-dot running"></span>
              <span>执行中</span>
            </div>
          </el-option>
          <el-option label="成功" value="success">
            <div class="status-option">
              <span class="status-dot success"></span>
              <span>成功</span>
            </div>
          </el-option>
          <el-option label="失败" value="failed">
            <div class="status-option">
              <span class="status-dot failed"></span>
              <span>失败</span>
            </div>
          </el-option>
        </el-select>
        <el-button type="primary" @click="loadTasks">
          <el-icon><Refresh /></el-icon>
          <span>刷新</span>
        </el-button>
      </div>
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon total">
          <el-icon><List /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ total }}</span>
          <span class="stat-label">总任务数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon running">
          <el-icon><Loading /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ runningCount }}</span>
          <span class="stat-label">执行中</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ successCount }}</span>
          <span class="stat-label">已完成</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon failed">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ failedCount }}</span>
          <span class="stat-label">失败</span>
        </div>
      </div>
    </div>
    
    <!-- 任务列表 -->
    <div class="tasks-list" v-loading="loading">
      <div v-if="tasks.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无任务">
          <el-button type="primary" @click="$router.push('/create')">创建任务</el-button>
        </el-empty>
      </div>
      
      <div v-else class="task-cards">
        <div 
          v-for="task in tasks" 
          :key="task.id" 
          class="task-card"
          @click="viewDetail(task)"
        >
          <div class="task-header">
            <div class="task-type">
              <el-icon><component :is="getTaskIcon(task.task_type)" /></el-icon>
              <span>{{ getTaskTypeLabel(task.task_type) }}</span>
            </div>
            <div :class="['task-status', task.status]">
              <span class="status-dot"></span>
              <span>{{ getStatusLabel(task.status) }}</span>
            </div>
          </div>
          
          <div class="task-body">
            <h4 class="task-name">{{ task.task_name }}</h4>
            <div class="task-meta">
              <span class="meta-item">
                <el-icon><Clock /></el-icon>
                {{ formatTime(task.created_at) }}
              </span>
              <span class="meta-item">
                <el-icon><Coin /></el-icon>
                消耗 {{ task.quota_cost || 0 }} 额度
              </span>
            </div>
          </div>
          
          <div class="task-footer">
            <div class="task-preview" v-if="task.output_urls && task.output_urls.length > 0">
              <img :src="task.output_urls[0]" alt="预览" v-if="isImageTask(task.task_type)" />
              <el-icon v-else :size="32"><VideoPlay /></el-icon>
            </div>
            <div class="task-actions" @click.stop>
              <el-button 
                v-if="task.status === 'pending' || task.status === 'running'"
                type="danger"
                size="small"
                text
                @click="cancelTask(task.id)"
              >
                <el-icon><Close /></el-icon>
                取消
              </el-button>
              <el-button 
                v-if="task.status === 'failed'"
                type="primary"
                size="small"
                text
                @click="retryTask(task.id)"
              >
                <el-icon><Refresh /></el-icon>
                重试
              </el-button>
              <el-button 
                v-if="task.status === 'success' && task.output_urls"
                type="success"
                size="small"
                text
                @click="downloadOutput(task)"
              >
                <el-icon><Download /></el-icon>
                下载
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="total > size">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="size"
        :total="total"
        layout="total, prev, pager, next"
        background
        @current-change="loadTasks"
      />
    </div>
    
    <!-- 任务详情弹窗 -->
    <el-dialog v-model="detailVisible" title="任务详情" width="600px" class="task-detail-dialog">
      <div v-if="currentTask" class="task-detail">
        <div class="detail-header">
          <div :class="['detail-status', currentTask.status]">
            <span class="status-dot"></span>
            <span>{{ getStatusLabel(currentTask.status) }}</span>
          </div>
          <span class="detail-id">#{{ currentTask.id }}</span>
        </div>
        
        <div class="detail-body">
          <div class="detail-item">
            <span class="detail-label">任务名称</span>
            <span class="detail-value">{{ currentTask.task_name }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">任务类型</span>
            <span class="detail-value">{{ getTaskTypeLabel(currentTask.task_type) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">消耗额度</span>
            <span class="detail-value highlight">{{ currentTask.quota_cost || 0 }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">创建时间</span>
            <span class="detail-value">{{ formatTime(currentTask.created_at) }}</span>
          </div>
        </div>
        
        <!-- 子任务进度 -->
        <div v-if="currentTask.items && currentTask.items.length > 0" class="detail-section">
          <h4>子任务进度</h4>
          <el-steps :active="getActiveStep(currentTask.items)" finish-status="success" simple>
            <el-step
              v-for="item in currentTask.items"
              :key="item.id"
              :title="item.step_name"
              :status="getStepStatus(item.status)"
            />
          </el-steps>
        </div>
        
        <!-- 输出文件 -->
        <div v-if="currentTask.output_urls && currentTask.output_urls.length > 0" class="detail-section">
          <h4>输出文件</h4>
          <div class="output-files">
            <div v-for="(url, index) in currentTask.output_urls" :key="index" class="output-file">
              <img v-if="isImageTask(currentTask.task_type)" :src="url" />
              <video v-else-if="isVideoTask(currentTask.task_type)" :src="url" controls />
              <el-link v-else :href="url" target="_blank">文件 {{ index + 1 }}</el-link>
            </div>
          </div>
        </div>
        
        <!-- 错误信息 -->
        <div v-if="currentTask.error_message" class="detail-section">
          <h4>错误信息</h4>
          <el-alert :title="currentTask.error_message" type="error" show-icon />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, List, Loading, CircleCheck, CircleClose, 
  Clock, Coin, Close, Download, Picture, VideoPlay, 
  Document, ChatDotRound, Connection
} from '@element-plus/icons-vue'
import { getTasks, getTaskDetail, cancelTask as cancelTaskApi, retryTask as retryTaskApi, pollTaskStatus } from '@/api/task'

const tasks = ref([])
const loading = ref(false)
const page = ref(1)
const size = ref(20)
const total = ref(0)
const filterStatus = ref('')
const detailVisible = ref(false)
const currentTask = ref(null)
let pollTimer = null

// 计算统计
const runningCount = computed(() => tasks.value.filter(t => t.status === 'running' || t.status === 'pending').length)
const successCount = computed(() => tasks.value.filter(t => t.status === 'success').length)
const failedCount = computed(() => tasks.value.filter(t => t.status === 'failed').length)

onMounted(() => {
  loadTasks()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})

const startPolling = () => {
  pollTimer = setInterval(async () => {
    const runningTasks = tasks.value.filter(t => t.status === 'pending' || t.status === 'running')
    
    if (runningTasks.length > 0) {
      for (const task of runningTasks) {
        try {
          const res = await pollTaskStatus(task.id)
          if (res.code === 200 && res.data.status === 'success') {
            loadTasks(true)
            break
          }
        } catch (e) {
          console.error('轮询任务失败:', e)
        }
      }
    }
  }, 10000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const loadTasks = async (silent = false) => {
  if (!silent) loading.value = true
  try {
    const res = await getTasks({
      page: page.value,
      size: size.value,
      status: filterStatus.value
    })
    if (res.code === 200) {
      tasks.value = res.data.list
      total.value = res.data.total || 0
    }
  } finally {
    loading.value = false
  }
}

const getTaskIcon = (type) => {
  const map = {
    'text_to_image': 'Picture',
    'image_to_image': 'Picture',
    'image_to_video': 'VideoPlay',
    'text_to_video': 'VideoPlay',
    'chat': 'ChatDotRound',
    'workflow': 'Connection'
  }
  return map[type] || 'Document'
}

const getTaskTypeLabel = (type) => {
  const map = {
    'text_to_image': '文生图',
    'image_to_image': '图生图',
    'image_to_video': '图生视频',
    'text_to_video': '文生视频',
    'chat': '对话',
    'workflow': '编排任务'
  }
  return map[type] || type
}

const isImageTask = (type) => {
  return ['text_to_image', 'image_to_image'].includes(type)
}

const isVideoTask = (type) => {
  return ['image_to_video', 'text_to_video'].includes(type)
}

const getStatusLabel = (status) => {
  const map = {
    'pending': '待执行',
    'running': '执行中',
    'success': '成功',
    'failed': '失败',
    'retry': '重试中',
    'cancelled': '已取消',
    'timeout': '超时'
  }
  return map[status] || status
}

const cancelTask = async (taskId) => {
  await ElMessageBox.confirm('确定取消该任务吗？', '提示', { type: 'warning' })
  const res = await cancelTaskApi(taskId)
  if (res.code === 200) {
    ElMessage.success('任务已取消')
    loadTasks()
  }
}

const retryTask = async (taskId) => {
  const res = await retryTaskApi(taskId)
  if (res.code === 200) {
    ElMessage.success('任务已重试')
    loadTasks()
  }
}

const viewDetail = async (row) => {
  const res = await getTaskDetail(row.id)
  if (res.code === 200) {
    currentTask.value = res.data
    detailVisible.value = true
  }
}

const downloadOutput = (row) => {
  if (row.output_urls && row.output_urls.length > 0) {
    window.open(row.output_urls[0], '_blank')
  }
}

const getActiveStep = (items) => {
  return items.filter(item => item.status === 'success').length
}

const getStepStatus = (status) => {
  const map = {
    'pending': 'wait',
    'running': 'process',
    'success': 'success',
    'failed': 'error',
    'skipped': 'finish'
  }
  return map[status] || 'wait'
}

const formatTime = (time) => {
  return new Date(time).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.tasks-container {
  background: #fff;
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.header-right {
  display: flex;
  gap: 12px;
}

.status-select {
  width: 140px;
}

.status-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.pending { background: var(--gray-400); }
.status-dot.running { background: var(--warning-500); animation: pulse 1.5s infinite; }
.status-dot.success { background: var(--success-500); }
.status-dot.failed { background: var(--error-500); }

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 24px;
  background: var(--gray-50);
  border-bottom: 1px solid var(--border-color);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fff;
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-color);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.total {
  background: var(--primary-50);
  color: var(--primary-500);
}

.stat-icon.running {
  background: var(--warning-500);
  color: #fff;
  background: linear-gradient(135deg, #faad14 0%, #ffc53d 100%);
}

.stat-icon.success {
  background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
  color: #fff;
}

.stat-icon.failed {
  background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
  color: #fff;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--gray-800);
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--gray-500);
  margin-top: 2px;
}

/* 任务列表 */
.tasks-list {
  min-height: 400px;
}

.empty-state {
  padding: 60px 0;
}

.task-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  padding: 24px;
}

.task-card {
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.task-card:hover {
  border-color: var(--primary-300);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--gray-50);
  border-bottom: 1px solid var(--border-color);
}

.task-type {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--gray-600);
}

.task-type .el-icon {
  color: var(--primary-500);
}

.task-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.task-status.pending {
  background: var(--gray-100);
  color: var(--gray-600);
}

.task-status.running {
  background: var(--warning-500);
  background: #fffbe6;
  color: #d48806;
}

.task-status.success {
  background: #f6ffed;
  color: #389e0d;
}

.task-status.failed {
  background: #fff2f0;
  color: #cf1322;
}

.task-status .status-dot {
  width: 6px;
  height: 6px;
}

.task-status.running .status-dot {
  animation: pulse 1.5s infinite;
}

.task-body {
  padding: 16px;
}

.task-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--gray-800);
  margin: 0 0 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--gray-500);
}

.meta-item .el-icon {
  font-size: 14px;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  background: var(--gray-50);
}

.task-preview {
  width: 48px;
  height: 48px;
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  background: var(--gray-100);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gray-400);
}

.task-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.task-actions {
  display: flex;
  gap: 8px;
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 24px;
  border-top: 1px solid var(--border-color);
}

/* 详情弹窗 */
.task-detail {
  padding: 8px 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.detail-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 500;
}

.detail-status.pending { background: var(--gray-100); color: var(--gray-600); }
.detail-status.running { background: #fffbe6; color: #d48806; }
.detail-status.success { background: #f6ffed; color: #389e0d; }
.detail-status.failed { background: #fff2f0; color: #cf1322; }

.detail-id {
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-400);
}

.detail-body {
  background: var(--gray-50);
  border-radius: var(--border-radius-md);
  padding: 16px;
  margin-bottom: 24px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.detail-item + .detail-item {
  border-top: 1px solid var(--border-color);
}

.detail-label {
  font-size: 13px;
  color: var(--gray-500);
}

.detail-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-800);
}

.detail-value.highlight {
  color: var(--primary-600);
}

.detail-section {
  margin-top: 24px;
}

.detail-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--gray-700);
  margin: 0 0 12px;
}

.output-files {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.output-file img,
.output-file video {
  max-width: 100%;
  max-height: 300px;
  border-radius: var(--border-radius-md);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
