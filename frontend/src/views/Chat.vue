<template>
  <div class="chat-container">
    <!-- 会话列表 -->
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <el-button type="primary" class="new-chat-btn" @click="createNewSession">
          <el-icon><Plus /></el-icon>
          <span>新建对话</span>
        </el-button>
      </div>
      
      <div class="session-list">
        <div class="session-list-header">
          <span class="session-count">共 {{ sessions.length }} 个对话</span>
        </div>
        
        <div
          v-for="session in sessions" 
          :key="session.session_id"
          :class="['session-item', { active: currentSession === session.session_id }]"
          @click="selectSession(session.session_id)"
        >
          <div class="session-icon">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="session-info">
            <span class="session-name">{{ session.session_name }}</span>
            <span class="session-time">{{ formatSessionTime(session.last_time) }}</span>
          </div>
          <el-dropdown @command="(cmd) => handleSessionAction(cmd, session)" trigger="click">
            <el-icon class="more-icon" @click.stop><MoreFilled /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="rename">
                  <el-icon><Edit /></el-icon>
                  重命名
                </el-dropdown-item>
                <el-dropdown-item command="delete" divided>
                  <el-icon><Delete /></el-icon>
                  删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        
        <el-empty v-if="sessions.length === 0" description="暂无对话" :image-size="80" />
      </div>
    </div>
    
    <!-- 对话主区域 -->
    <div class="chat-main">
      <!-- 顶部工具栏 -->
      <div class="chat-header">
        <div class="model-selector">
          <span class="selector-label">模型</span>
          <el-select v-model="selectedModel" placeholder="选择模型" class="model-select" popper-class="model-select-dropdown">
            <el-option
              v-for="model in models"
              :key="model.code"
              :label="model.name"
              :value="model.code"
            >
              <div class="model-option">
                <span class="model-name">{{ model.name }}</span>
                <span class="model-desc">{{ model.description || '通用模型' }}</span>
              </div>
            </el-option>
          </el-select>
        </div>
        
        <div class="chat-options">
          <div 
            class="option-toggle"
            :class="{ active: isDeepThink, disabled: !currentModelSupportsDeepThink }"
            @click="toggleDeepThink"
          >
            <el-icon><Cpu /></el-icon>
            <span>深度思考</span>
            <el-switch 
              v-model="isDeepThink" 
              :disabled="!currentModelSupportsDeepThink"
              size="small"
            />
          </div>
          <div 
            class="option-toggle"
            :class="{ active: isWebSearch, disabled: !currentModelSupportsWebSearch }"
            @click="toggleWebSearch"
          >
            <el-icon><Search /></el-icon>
            <span>联网搜索</span>
            <el-switch 
              v-model="isWebSearch" 
              :disabled="!currentModelSupportsWebSearch"
              size="small"
            />
          </div>
        </div>
      </div>
      
      <!-- 消息区域 -->
      <div class="chat-messages" ref="messagesRef">
        <!-- 空状态 -->
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-icon">
            <el-icon :size="64"><ChatDotRound /></el-icon>
          </div>
          <h3 class="empty-title">开始新对话</h3>
          <p class="empty-desc">选择模型并输入您的问题，开始与 AI 助手对话</p>
          <div class="quick-actions">
            <div class="quick-action" @click="inputMessage = '请帮我写一篇关于人工智能的文章'">
              <el-icon><Document /></el-icon>
              <span>写一篇文章</span>
            </div>
            <div class="quick-action" @click="inputMessage = '请帮我分析这段代码的问题'">
              <el-icon><Code /></el-icon>
              <span>代码分析</span>
            </div>
            <div class="quick-action" @click="inputMessage = '请帮我翻译以下内容'">
              <el-icon><Translate /></el-icon>
              <span>翻译内容</span>
            </div>
          </div>
        </div>
        
        <!-- 消息列表 -->
        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="['message', msg.role]"
        >
          <div class="message-avatar">
            <el-avatar 
              v-if="msg.role === 'user'" 
              :size="40" 
              class="avatar-user"
            >
              {{ userStore.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <div v-else class="avatar-ai">
              <svg viewBox="0 0 32 32" width="32" height="32">
                <defs>
                  <linearGradient id="aiGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#4096ff" />
                    <stop offset="100%" style="stop-color:#1677ff" />
                  </linearGradient>
                </defs>
                <circle cx="16" cy="16" r="14" fill="url(#aiGradient)" />
                <path d="M10 16 L14 20 L22 12" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="message-author">{{ msg.role === 'user' ? '我' : 'AI 助手' }}</span>
              <span class="message-time">{{ formatTime(msg.created_at) }}</span>
            </div>
            <div class="message-text" v-html="renderMarkdown(msg.content)"></div>
          </div>
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div class="chat-input">
        <div class="input-container">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 6 }"
            placeholder="输入消息，按 Ctrl + Enter 发送..."
            class="message-input"
            @keyup.enter.ctrl="sendMessage"
          />
          <el-button 
            type="primary" 
            class="send-btn"
            :loading="sending"
            :disabled="!inputMessage.trim()"
            @click="sendMessage"
          >
            <el-icon v-if="!sending"><Promotion /></el-icon>
            <span>{{ sending ? '发送中' : '发送' }}</span>
          </el-button>
        </div>
        <div class="input-hint">
          <span>按 <kbd>Ctrl</kbd> + <kbd>Enter</kbd> 快速发送</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { User, ChatDotRound, Plus, MoreFilled, Edit, Delete, Cpu, Search, Document, Promotion } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import { useUserStore } from '@/stores/user'
import {
  getChatModels,
  getSessions,
  createSession,
  getMessages,
  sendMessageStream,
  renameSession,
  deleteSession
} from '@/api/chat'

// 图标组件
const Code = {
  template: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8.29 16.752a1 1 0 1 1-1.414-1.414l4.242-4.243-4.242-4.242a1 1 0 0 1 1.414-1.414l4.95 4.95a1 1 0 0 1 0 1.414l-4.95 4.95zm6.914-1.414a1 1 0 0 0 1.414 1.414l4.95-4.95a1 1 0 0 0 0-1.414l-4.95-4.95a1 1 0 0 0-1.414 1.414l4.242 4.242-4.242 4.243z"/></svg>'
}
const Translate = {
  template: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.87 15.07l-2.54-2.51.03-.03A17.52 17.52 0 0014.07 6H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z"/></svg>'
}

// 配置 marked
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true
})

const userStore = useUserStore()
const models = ref([])
const sessions = ref([])
const messages = ref([])
const currentSession = ref('')
const selectedModel = ref('qwen-turbo')
const isDeepThink = ref(false)
const isWebSearch = ref(false)

// 计算当前模型是否支持深度思考和联网搜索
const currentModelSupportsDeepThink = computed(() => {
  const model = models.value.find(m => m.code === selectedModel.value)
  return model?.supports_deep_think || false
})

const currentModelSupportsWebSearch = computed(() => {
  const model = models.value.find(m => m.code === selectedModel.value)
  return model?.supports_web_search || false
})
const inputMessage = ref('')
const sending = ref(false)
const messagesRef = ref(null)

onMounted(async () => {
  await loadModels()
  await loadSessions()
})

const loadModels = async () => {
  const res = await getChatModels()
  if (res.code === 200) {
    models.value = res.data
    if (models.value.length > 0 && !selectedModel.value) {
      selectedModel.value = models.value[0].code
    }
  }
}

const loadSessions = async () => {
  const res = await getSessions()
  if (res.code === 200) {
    sessions.value = res.data.list
  }
}

const createNewSession = async () => {
  const res = await createSession()
  if (res.code === 200) {
    currentSession.value = res.data.session_id
    messages.value = []
    await loadSessions()
  }
}

const selectSession = async (sessionId) => {
  currentSession.value = sessionId
  const res = await getMessages(sessionId)
  if (res.code === 200) {
    messages.value = res.data.list.reverse()
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  if (!currentSession.value) {
    await createNewSession()
  }

  const userMessage = inputMessage.value
  inputMessage.value = ''
  sending.value = true

  try {
    // 先添加用户消息到列表
    messages.value.push({
      id: Date.now(),
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    })
    scrollToBottom()

    // 创建 AI 回复占位
    const aiMessageId = Date.now() + 1
    messages.value.push({
      id: aiMessageId,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString()
    })

    // 调用流式接口
    const response = await sendMessageStream({
      session_id: currentSession.value,
      message: userMessage,
      model_code: selectedModel.value,
      is_deep_think: isDeepThink.value,
      is_web_search: isWebSearch.value
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let aiContent = ''
    let reasoningContent = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data:')) {
          try {
            const data = JSON.parse(line.slice(5).trim())
            // 处理推理内容
            if (data.reasoning_content) {
              reasoningContent += data.reasoning_content
            }
            // 处理正常内容
            if (data.content) {
              aiContent += data.content
            }
            
            // 更新 AI 消息内容（组合推理内容和正常内容）
            if (reasoningContent || aiContent) {
              const aiMsg = messages.value.find(m => m.id === aiMessageId)
              if (aiMsg) {
                let fullContent = ''
                if (reasoningContent) {
                  fullContent += `<think>
${reasoningContent}
</think>

`
                }
                if (aiContent) {
                  fullContent += aiContent
                }
                aiMsg.content = fullContent
              }
              scrollToBottom()
            }
            
            if (data.done) {
              sending.value = false
            }
          } catch (e) {
            console.error('解析 SSE 数据失败:', e)
          }
        }
      }
    }
  } catch (error) {
    ElMessage.error('发送消息失败')
    sending.value = false
  }
}

const scrollToBottom = () => {
  setTimeout(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  }, 50)
}

const handleSessionAction = async (command, session) => {
  if (command === 'rename') {
    const { value } = await ElMessageBox.prompt('请输入新名称', '重命名', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: session.session_name
    })
    if (value) {
      await renameSession(session.session_id, { name: value })
      await loadSessions()
    }
  } else if (command === 'delete') {
    await ElMessageBox.confirm('确定删除该会话吗？', '提示', {
      type: 'warning'
    })
    await deleteSession(session.session_id)
    await loadSessions()
    if (currentSession.value === session.session_id) {
      currentSession.value = ''
      messages.value = []
    }
  }
}

const formatTime = (time) => {
  return new Date(time).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatSessionTime = (time) => {
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  
  if (diff < 86400000) { // 24小时内
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (diff < 604800000) { // 7天内
    return date.toLocaleDateString('zh-CN', { weekday: 'short' })
  }
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

const renderMarkdown = (content) => {
  if (!content) return ''
  
  // 处理 think 标签 - 转换为可折叠的 HTML
  content = content.replace(/<think>([\s\S]*?)<\/think>/g, (match, thinking) => {
    const trimmedThinking = thinking.trim()
    if (!trimmedThinking) return ''
    return `<details class="thinking-block" open>
      <summary>💭 思考过程（点击收起）</summary>
      <div class="thinking-content">${marked.parse(trimmedThinking)}</div>
    </details>`
  })
  
  return marked.parse(content)
}

const toggleDeepThink = () => {
  if (currentModelSupportsDeepThink.value) {
    isDeepThink.value = !isDeepThink.value
  }
}

const toggleWebSearch = () => {
  if (currentModelSupportsWebSearch.value) {
    isWebSearch.value = !isWebSearch.value
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  height: calc(100vh - 112px);
  background: var(--bg-layout);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

/* ========== 会话列表 ========== */
.chat-sidebar {
  width: 280px;
  background: #fff;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.new-chat-btn {
  width: 100%;
  height: 44px;
  font-size: 14px;
  font-weight: 500;
  border-radius: var(--border-radius-md);
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-list-header {
  padding: 8px 12px;
  font-size: 12px;
  color: var(--gray-500);
}

.session-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 4px;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
}

.session-item:hover {
  background: var(--gray-50);
}

.session-item.active {
  background: var(--primary-50);
  border: 1px solid var(--primary-100);
}

.session-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--border-radius-md);
  background: var(--gray-100);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gray-500);
  flex-shrink: 0;
}

.session-item.active .session-icon {
  background: var(--primary-100);
  color: var(--primary-500);
}

.session-info {
  flex: 1;
  margin-left: 10px;
  overflow: hidden;
}

.session-name {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-800);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-time {
  display: block;
  font-size: 12px;
  color: var(--gray-400);
  margin-top: 2px;
}

.more-icon {
  opacity: 0;
  padding: 6px;
  border-radius: var(--border-radius-sm);
  transition: all var(--transition-fast);
  color: var(--gray-400);
}

.session-item:hover .more-icon {
  opacity: 1;
}

.more-icon:hover {
  background: var(--gray-100);
  color: var(--gray-600);
}

/* ========== 对话主区域 ========== */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
}

/* 顶部工具栏 */
.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
}

.model-selector {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selector-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-600);
}

.model-select {
  width: 200px;
}

.model-option {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.model-name {
  font-size: 14px;
  font-weight: 500;
}

.model-desc {
  font-size: 12px;
  color: var(--gray-500);
}

.chat-options {
  display: flex;
  gap: 12px;
}

.option-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--gray-50);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  font-size: 13px;
  color: var(--gray-600);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.option-toggle:hover:not(.disabled) {
  background: var(--gray-100);
  border-color: var(--gray-300);
}

.option-toggle.active {
  background: var(--primary-50);
  border-color: var(--primary-200);
  color: var(--primary-600);
}

.option-toggle.active .el-icon {
  color: var(--primary-500);
}

.option-toggle.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: var(--gray-50);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 48px;
}

.empty-icon {
  color: var(--primary-200);
  margin-bottom: 24px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--gray-800);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: var(--gray-500);
  margin-bottom: 32px;
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.quick-action {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  font-size: 14px;
  color: var(--gray-700);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.quick-action:hover {
  background: var(--primary-50);
  border-color: var(--primary-200);
  color: var(--primary-600);
}

.quick-action .el-icon {
  color: var(--primary-500);
}

/* 消息 */
.message {
  display: flex;
  margin-bottom: 24px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar-user {
  background: linear-gradient(135deg, var(--primary-400) 0%, var(--primary-600) 100%);
  color: #fff;
  font-weight: 600;
}

.avatar-ai {
  width: 40px;
  height: 40px;
}

.message-content {
  max-width: 70%;
  margin: 0 16px;
}

.message.user .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.message.user .message-header {
  flex-direction: row-reverse;
}

.message-author {
  font-size: 13px;
  font-weight: 600;
  color: var(--gray-700);
}

.message-time {
  font-size: 12px;
  color: var(--gray-400);
}

.message-text {
  padding: 16px 20px;
  border-radius: var(--border-radius-lg);
  background: #fff;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  line-height: 1.7;
  font-size: 14px;
  color: var(--gray-800);
}

.message.user .message-text {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  color: #fff;
  border: none;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.25);
}

/* Markdown 样式 */
.message-text :deep(h1),
.message-text :deep(h2),
.message-text :deep(h3),
.message-text :deep(h4) {
  margin: 16px 0 12px;
  font-weight: 600;
  line-height: 1.4;
  color: inherit;
}

.message-text :deep(h1) { font-size: 20px; }
.message-text :deep(h2) { font-size: 18px; }
.message-text :deep(h3) { font-size: 16px; }

.message-text :deep(p) {
  margin: 8px 0;
}

.message-text :deep(ul),
.message-text :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.message-text :deep(li) {
  margin: 4px 0;
}

.message-text :deep(code) {
  background: rgba(0, 0, 0, 0.06);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--font-family-mono);
  font-size: 13px;
}

.message.user .message-text :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}

.message-text :deep(pre) {
  background: #f6f8fa;
  padding: 16px;
  border-radius: var(--border-radius-md);
  overflow-x: auto;
  margin: 12px 0;
}

.message-text :deep(pre code) {
  background: none;
  padding: 0;
  color: var(--gray-800);
}

.message-text :deep(blockquote) {
  border-left: 3px solid var(--primary-400);
  margin: 12px 0;
  padding: 8px 16px;
  background: var(--primary-50);
  border-radius: 0 var(--border-radius-md) var(--border-radius-md) 0;
  color: var(--gray-700);
}

.message-text :deep(hr) {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 16px 0;
}

.message-text :deep(strong) {
  font-weight: 600;
}

.message-text :deep(a) {
  color: var(--primary-500);
  text-decoration: none;
}

.message-text :deep(a:hover) {
  text-decoration: underline;
}

/* 思考过程 */
.message-text :deep(.thinking-block) {
  margin: 12px 0;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background: var(--gray-50);
  overflow: hidden;
}

.message-text :deep(.thinking-block summary) {
  padding: 12px 16px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: var(--gray-600);
  background: var(--gray-100);
  border-bottom: 1px solid transparent;
  transition: all var(--transition-fast);
  user-select: none;
}

.message-text :deep(.thinking-block summary:hover) {
  background: var(--gray-200);
}

.message-text :deep(.thinking-block[open] summary) {
  border-bottom-color: var(--border-color);
}

.message-text :deep(.thinking-content) {
  padding: 16px;
  font-size: 13px;
  color: var(--gray-600);
  line-height: 1.7;
}

.message.user .message-text :deep(.thinking-block) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.message.user .message-text :deep(.thinking-block summary) {
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.9);
}

/* 输入区域 */
.chat-input {
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: #fff;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
}

.message-input :deep(.el-textarea__inner) {
  padding: 14px 16px;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  border-radius: var(--border-radius-lg);
  border: 2px solid var(--border-color);
  transition: all var(--transition-fast);
}

.message-input :deep(.el-textarea__inner:focus) {
  border-color: var(--primary-400);
  box-shadow: 0 0 0 3px var(--primary-100);
}

.send-btn {
  height: 48px;
  padding: 0 24px;
  font-size: 14px;
  font-weight: 500;
  border-radius: var(--border-radius-lg);
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-hint {
  margin-top: 8px;
  text-align: right;
}

.input-hint span {
  font-size: 12px;
  color: var(--gray-400);
}

.input-hint kbd {
  display: inline-block;
  padding: 2px 6px;
  font-size: 11px;
  font-family: var(--font-family-mono);
  background: var(--gray-100);
  border: 1px solid var(--gray-300);
  border-radius: 4px;
  box-shadow: 0 1px 1px rgba(0,0,0,0.1);
  margin: 0 2px;
}
</style>
