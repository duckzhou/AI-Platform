<template>
  <div class="create-container">
    <!-- 标签页导航 -->
    <div class="tabs-header">
      <div 
        v-for="tab in tabs" 
        :key="tab.key"
        :class="['tab-item', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        <el-icon :size="20"><component :is="tab.icon" /></el-icon>
        <span>{{ tab.label }}</span>
      </div>
    </div>
    
    <div class="tabs-content">
      <!-- 文生图 -->
      <div v-show="activeTab === 'text2image'" class="tab-panel">
        <div class="panel-header">
          <h2 class="panel-title">文生图</h2>
          <p class="panel-desc">输入文字描述，AI 将为您生成精美图片</p>
        </div>
        
        <div class="create-form">
          <div class="form-section">
            <label class="form-label required">提示词</label>
            <el-input
              v-model="text2imageForm.prompt"
              type="textarea"
              :rows="4"
              placeholder="描述您想要生成的图片，例如：一只可爱的橘猫在阳光下睡觉，油画风格..."
              class="prompt-input"
            />
            <div class="form-hint">
              <span>详细的描述能获得更好的效果</span>
            </div>
          </div>
          
          <div class="form-section">
            <label class="form-label">图片尺寸</label>
            <div class="size-options">
              <div 
                v-for="size in sizeOptions" 
                :key="size.value"
                :class="['size-item', { active: text2imageForm.size === size.value }]"
                @click="text2imageForm.size = size.value"
              >
                <div class="size-icon" :style="{ aspectRatio: size.ratio }">
                  <span>{{ size.label }}</span>
                </div>
                <span class="size-label">{{ size.name }}</span>
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <el-button 
              type="primary" 
              size="large" 
              class="create-btn"
              @click="createTextToImage" 
              :loading="creating"
            >
              <el-icon v-if="!creating"><MagicStick /></el-icon>
              <span>{{ creating ? 'AI 正在生成...' : '生成图片' }}</span>
              <span class="cost-badge">5 额度</span>
            </el-button>
          </div>
          
          <!-- 生成结果 -->
          <div v-if="text2imageResult.length" class="result-section">
            <div class="result-header">
              <h3>生成结果</h3>
              <span class="result-count">{{ text2imageResult.length }} 张图片</span>
            </div>
            <div class="result-images">
              <div v-for="(url, idx) in text2imageResult" :key="idx" class="result-image-wrapper">
                <el-image
                  :src="url"
                  :preview-src-list="text2imageResult"
                  fit="cover"
                  class="result-image"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 图生图 -->
      <div v-show="activeTab === 'image2image'" class="tab-panel">
        <div class="panel-header">
          <h2 class="panel-title">图生图</h2>
          <p class="panel-desc">上传参考图片，AI 将根据描述生成风格相似的新图片</p>
        </div>
        
        <div class="create-form">
          <div class="form-section">
            <label class="form-label required">参考图片</label>
            <div class="source-tabs">
              <div 
                :class="['source-tab', { active: image2imageForm.sourceType === 'upload' }]"
                @click="image2imageForm.sourceType = 'upload'"
              >
                <el-icon><Upload /></el-icon>
                <span>上传图片</span>
              </div>
              <div 
                :class="['source-tab', { active: image2imageForm.sourceType === 'material' }]"
                @click="image2imageForm.sourceType = 'material'"
              >
                <el-icon><Picture /></el-icon>
                <span>素材库</span>
              </div>
            </div>
            
            <!-- 上传区域 -->
            <div v-if="image2imageForm.sourceType === 'upload'" class="upload-area">
              <el-upload
                class="upload-dragger"
                drag
                action="#"
                :auto-upload="false"
                :on-change="handleImageChange"
                :show-file-list="false"
                accept="image/*"
              >
                <div v-if="!image2imageForm.previewUrl" class="upload-placeholder">
                  <el-icon class="upload-icon"><Upload /></el-icon>
                  <div class="upload-text">
                    <span>拖拽图片到此处或</span>
                    <em>点击上传</em>
                  </div>
                  <div class="upload-hint">支持 JPG、PNG 格式，最大 10MB</div>
                </div>
                <div v-else class="upload-preview">
                  <img :src="image2imageForm.previewUrl" />
                  <div class="preview-overlay">
                    <el-icon><Refresh /></el-icon>
                    <span>更换图片</span>
                  </div>
                </div>
              </el-upload>
            </div>
            
            <!-- 素材库选择 -->
            <div v-else class="material-select-area">
              <el-button class="select-material-btn" @click="openMaterialDialog">
                <el-icon><Picture /></el-icon>
                <span>从素材库选择</span>
              </el-button>
              <div v-if="image2imageForm.selectedMaterial" class="selected-material-card">
                <img :src="image2imageForm.selectedMaterial.file_url" />
                <div class="material-info">
                  <span class="material-name">{{ image2imageForm.selectedMaterial.name }}</span>
                  <el-button type="danger" text size="small" @click="clearSelectedMaterial">
                    <el-icon><Delete /></el-icon>
                    移除
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-section">
            <label class="form-label">提示词</label>
            <el-input
              v-model="image2imageForm.prompt"
              type="textarea"
              :rows="3"
              placeholder="描述您想要的效果，例如：将这张照片转换为水彩画风格..."
              class="prompt-input"
            />
          </div>
          
          <div class="form-section">
            <label class="form-label">图片尺寸</label>
            <div class="size-options">
              <div 
                v-for="size in sizeOptions" 
                :key="size.value"
                :class="['size-item', { active: image2imageForm.size === size.value }]"
                @click="image2imageForm.size = size.value"
              >
                <div class="size-icon" :style="{ aspectRatio: size.ratio }">
                  <span>{{ size.label }}</span>
                </div>
                <span class="size-label">{{ size.name }}</span>
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <el-button 
              type="primary" 
              size="large" 
              class="create-btn"
              @click="createImageToImage" 
              :loading="creating"
            >
              <el-icon v-if="!creating"><MagicStick /></el-icon>
              <span>{{ creating ? 'AI 正在生成...' : '生成图片' }}</span>
              <span class="cost-badge">5 额度</span>
            </el-button>
          </div>
          
          <!-- 生成结果 -->
          <div v-if="image2imageResult.length" class="result-section">
            <div class="result-header">
              <h3>生成结果</h3>
              <span class="result-count">{{ image2imageResult.length }} 张图片</span>
            </div>
            <div class="result-images">
              <div v-for="(url, idx) in image2imageResult" :key="idx" class="result-image-wrapper">
                <el-image
                  :src="url"
                  :preview-src-list="image2imageResult"
                  fit="cover"
                  class="result-image"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 图生视频 -->
      <div v-show="activeTab === 'image2video'" class="tab-panel">
        <div class="panel-header">
          <h2 class="panel-title">图生视频</h2>
          <p class="panel-desc">上传静态图片，AI 将为您生成动态视频</p>
        </div>
        
        <div class="create-form">
          <div class="form-section">
            <label class="form-label required">首帧图片</label>
            <el-button class="select-material-btn" @click="openVideoMaterialDialog">
              <el-icon><Picture /></el-icon>
              <span>从素材库选择</span>
            </el-button>
            <div v-if="image2videoForm.selectedMaterial" class="selected-material-card">
              <img :src="image2videoForm.selectedMaterial.file_url" />
              <div class="material-info">
                <span class="material-name">{{ image2videoForm.selectedMaterial.name }}</span>
                <el-button type="danger" text size="small" @click="image2videoForm.selectedMaterial = null">
                  <el-icon><Delete /></el-icon>
                  移除
                </el-button>
              </div>
            </div>
          </div>
          
          <div class="form-section">
            <label class="form-label">描述（可选）</label>
            <el-input
              v-model="image2videoForm.prompt"
              type="textarea"
              :rows="2"
              placeholder="描述视频中想要发生的动作..."
              class="prompt-input"
            />
          </div>
          
          <div class="form-section">
            <label class="form-label">视频时长</label>
            <div class="duration-selector">
              <div 
                v-for="duration in durationOptions" 
                :key="duration"
                :class="['duration-item', { active: image2videoForm.duration === duration }]"
                @click="image2videoForm.duration = duration"
              >
                {{ duration }}秒
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <el-button 
              type="primary" 
              size="large" 
              class="create-btn"
              @click="createImageToVideo" 
              :loading="creating"
            >
              <el-icon v-if="!creating"><VideoPlay /></el-icon>
              <span>{{ creating ? '提交中...' : '生成视频' }}</span>
              <span class="cost-badge">20 额度</span>
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 任务编排 -->
      <div v-show="activeTab === 'workflow'" class="tab-panel">
        <div class="panel-header">
          <h2 class="panel-title">任务编排</h2>
          <p class="panel-desc">选择预设工作流，一键完成复杂创作任务</p>
        </div>
        
        <div class="workflow-grid">
          <div 
            v-for="flow in taskFlows" 
            :key="flow.id"
            class="workflow-card"
            @click="selectFlow(flow)"
          >
            <div class="workflow-thumbnail">
              <img :src="flow.thumbnail_url || '/placeholder.png'" />
              <div class="workflow-overlay">
                <el-icon :size="32"><VideoCamera /></el-icon>
              </div>
            </div>
            <div class="workflow-info">
              <h4>{{ flow.name }}</h4>
              <p>{{ flow.description }}</p>
              <el-tag size="small" effect="light">{{ flow.category }}</el-tag>
            </div>
          </div>
          
          <el-empty v-if="taskFlows.length === 0" description="暂无可用工作流" />
        </div>
      </div>
    </div>
    
    <!-- 素材库选择弹窗 -->
    <el-dialog v-model="materialDialogVisible" title="选择素材" width="800px" class="material-dialog">
      <div class="dialog-material-grid">
        <div
          v-for="material in materialList"
          :key="material.id"
          :class="['dialog-material-item', { selected: tempSelectedMaterial?.id === material.id }]"
          @click="tempSelectedMaterial = material"
        >
          <img :src="material.file_url" />
          <div class="material-check" v-if="tempSelectedMaterial?.id === material.id">
            <el-icon><Check /></el-icon>
          </div>
          <div class="material-name">{{ material.name }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="materialDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmMaterialSelect">确定选择</el-button>
      </template>
    </el-dialog>
    
    <!-- 视频素材选择弹窗 -->
    <el-dialog v-model="videoMaterialDialogVisible" title="选择首帧图片" width="800px" class="material-dialog">
      <div class="dialog-material-grid">
        <div
          v-for="material in videoMaterialList"
          :key="material.id"
          :class="['dialog-material-item', { selected: tempVideoMaterial?.id === material.id }]"
          @click="tempVideoMaterial = material"
        >
          <img :src="material.file_url" />
          <div class="material-check" v-if="tempVideoMaterial?.id === material.id">
            <el-icon><Check /></el-icon>
          </div>
          <div class="material-name">{{ material.name }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="videoMaterialDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmVideoMaterialSelect">确定选择</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { MagicStick, UploadFilled, VideoPlay, Picture, Upload, Delete, Check, Refresh, VideoCamera } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  createTextToImage as createTextToImageApi,
  createImageToImage as createImageToImageApi,
  createImageToVideo as createImageToVideoApi,
  createWorkflow as createWorkflowApi,
  getTaskFlows
} from '@/api/task'
import { getMaterials } from '@/api/material'

const router = useRouter()
const activeTab = ref('text2image')
const creating = ref(false)
const taskFlows = ref([])

// 标签页配置
const tabs = [
  { key: 'text2image', label: '文生图', icon: 'MagicStick' },
  { key: 'image2image', label: '图生图', icon: 'Picture' },
  { key: 'image2video', label: '图生视频', icon: 'VideoPlay' },
  { key: 'workflow', label: '任务编排', icon: 'List' },
]

// 尺寸选项
const sizeOptions = [
  { value: '1024x1024', label: '1:1', name: '正方形', ratio: '1' },
  { value: '720x1280', label: '9:16', name: '竖屏', ratio: '0.5625' },
  { value: '1280x720', label: '16:9', name: '横屏', ratio: '1.7778' },
  { value: '768x1152', label: '2:3', name: '海报', ratio: '0.6667' },
]

// 时长选项
const durationOptions = [4, 5, 6, 7, 8, 9, 10]

// 文生图
const text2imageForm = ref({
  prompt: '',
  size: '1024x1024'
})
const text2imageResult = ref([])

// 图生图
const image2imageForm = ref({
  prompt: '',
  sourceType: 'upload',
  image: null,
  previewUrl: '',
  selectedMaterial: null,
  size: '1024x1024'
})
const image2imageResult = ref([])

// 素材库选择
const materialDialogVisible = ref(false)
const materialList = ref([])
const tempSelectedMaterial = ref(null)

// 图生视频
const image2videoForm = ref({
  prompt: '',
  duration: 5,
  selectedMaterial: null
})

// 视频素材选择
const videoMaterialDialogVisible = ref(false)
const videoMaterialList = ref([])
const tempVideoMaterial = ref(null)

onMounted(async () => {
  await loadTaskFlows()
})

const loadTaskFlows = async () => {
  const res = await getTaskFlows()
  if (res.code === 200) {
    taskFlows.value = res.data.list
  }
}

const loadMaterials = async () => {
  const res = await getMaterials({ material_type: 'image', size: 50 })
  if (res.code === 200) {
    materialList.value = res.data.list
  }
}

const handleImageChange = (file) => {
  image2imageForm.value.image = file.raw
  image2imageForm.value.previewUrl = URL.createObjectURL(file.raw)
  image2imageForm.value.selectedMaterial = null
}

const openVideoMaterialDialog = async () => {
  const res = await getMaterials({ material_type: 'image', size: 50 })
  if (res.code === 200) {
    videoMaterialList.value = res.data.list
  }
  tempVideoMaterial.value = image2videoForm.value.selectedMaterial
  videoMaterialDialogVisible.value = true
}

const confirmVideoMaterialSelect = () => {
  if (tempVideoMaterial.value) {
    image2videoForm.value.selectedMaterial = tempVideoMaterial.value
  }
  videoMaterialDialogVisible.value = false
}

const openMaterialDialog = async () => {
  await loadMaterials()
  tempSelectedMaterial.value = image2imageForm.value.selectedMaterial
  materialDialogVisible.value = true
}

const confirmMaterialSelect = () => {
  if (tempSelectedMaterial.value) {
    image2imageForm.value.selectedMaterial = tempSelectedMaterial.value
    image2imageForm.value.previewUrl = tempSelectedMaterial.value.file_url
    image2imageForm.value.image = null
  }
  materialDialogVisible.value = false
}

const clearSelectedMaterial = () => {
  image2imageForm.value.selectedMaterial = null
  image2imageForm.value.previewUrl = ''
}

const createTextToImage = async () => {
  if (!text2imageForm.value.prompt) {
    ElMessage.warning('请输入提示词')
    return
  }
  
  creating.value = true
  try {
    const res = await createTextToImageApi({
      prompt: text2imageForm.value.prompt,
      size: text2imageForm.value.size
    })
    if (res.code === 200) {
      if (res.data.status === 'success') {
        text2imageResult.value = res.data.output_urls || []
        ElMessage.success('生成成功')
      } else {
        ElMessage.info('任务已提交，请稍后查看结果')
        router.push('/tasks')
      }
    }
  } finally {
    creating.value = false
  }
}

const createImageToImage = async () => {
  const imageUrl = image2imageForm.value.selectedMaterial?.file_url
  
  if (!imageUrl && !image2imageForm.value.image) {
    ElMessage.warning('请选择或上传图片')
    return
  }
  
  creating.value = true
  try {
    let refImageUrl = imageUrl
    if (!refImageUrl && image2imageForm.value.image) {
      ElMessage.warning('请先在素材库上传图片，然后选择素材库中的图片')
      creating.value = false
      return
    }
    
    const res = await createImageToImageApi({
      prompt: image2imageForm.value.prompt,
      image_url: refImageUrl,
      size: image2imageForm.value.size
    })
    if (res.code === 200) {
      if (res.data.status === 'success') {
        image2imageResult.value = res.data.output_urls || []
        ElMessage.success('生成成功')
      } else {
        ElMessage.info('任务已提交，请稍后查看结果')
        router.push('/tasks')
      }
    }
  } finally {
    creating.value = false
  }
}

const createImageToVideo = async () => {
  if (!image2videoForm.value.selectedMaterial) {
    ElMessage.warning('请从素材库选择图片')
    return
  }
  
  creating.value = true
  try {
    const res = await createImageToVideoApi({
      image_url: image2videoForm.value.selectedMaterial.file_url,
      prompt: image2videoForm.value.prompt,
      duration: image2videoForm.value.duration
    })
    if (res.code === 200) {
      ElMessage.success('任务已提交，请稍后在任务列表查看结果')
      router.push('/tasks')
    }
  } finally {
    creating.value = false
  }
}

const selectFlow = async (flow) => {
  const res = await createWorkflowApi({
    flow_id: flow.id,
    input_params: {}
  })
  if (res.code === 200) {
    ElMessage.success('编排任务创建成功')
    router.push('/tasks')
  }
}
</script>

<style scoped>
.create-container {
  background: #fff;
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

/* 标签页头部 */
.tabs-header {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  background: var(--gray-50);
  padding: 0 24px;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 24px;
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-600);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all var(--transition-fast);
}

.tab-item:hover {
  color: var(--primary-500);
}

.tab-item.active {
  color: var(--primary-600);
  border-bottom-color: var(--primary-500);
  background: #fff;
}

/* 面板内容 */
.tabs-content {
  padding: 24px;
}

.panel-header {
  margin-bottom: 24px;
}

.panel-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--gray-800);
  margin: 0 0 8px;
}

.panel-desc {
  font-size: 14px;
  color: var(--gray-500);
  margin: 0;
}

/* 表单 */
.create-form {
  max-width: 640px;
}

.form-section {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-700);
  margin-bottom: 8px;
}

.form-label.required::after {
  content: '*';
  color: var(--error-500);
  margin-left: 4px;
}

.form-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--gray-400);
}

.prompt-input :deep(.el-textarea__inner) {
  padding: 14px 16px;
  font-size: 14px;
  line-height: 1.6;
  border-radius: var(--border-radius-md);
  border: 2px solid var(--border-color);
}

.prompt-input :deep(.el-textarea__inner:focus) {
  border-color: var(--primary-400);
  box-shadow: 0 0 0 3px var(--primary-100);
}

/* 尺寸选择 */
.size-options {
  display: flex;
  gap: 12px;
}

.size-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  min-width: 80px;
}

.size-item:hover {
  border-color: var(--primary-300);
}

.size-item.active {
  border-color: var(--primary-500);
  background: var(--primary-50);
}

.size-icon {
  width: 40px;
  background: var(--gray-100);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  color: var(--gray-500);
  margin-bottom: 8px;
  transition: all var(--transition-fast);
}

.size-item.active .size-icon {
  background: var(--primary-100);
  color: var(--primary-600);
}

.size-label {
  font-size: 12px;
  color: var(--gray-600);
}

.size-item.active .size-label {
  color: var(--primary-600);
  font-weight: 500;
}

/* 时长选择 */
.duration-selector {
  display: flex;
  gap: 8px;
}

.duration-item {
  padding: 10px 20px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-600);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.duration-item:hover {
  border-color: var(--primary-300);
}

.duration-item.active {
  border-color: var(--primary-500);
  background: var(--primary-500);
  color: #fff;
}

/* 来源选择 */
.source-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.source-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: 13px;
  color: var(--gray-600);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.source-tab:hover {
  border-color: var(--primary-300);
}

.source-tab.active {
  border-color: var(--primary-500);
  background: var(--primary-50);
  color: var(--primary-600);
}

/* 上传区域 */
.upload-area {
  margin-top: 8px;
}

.upload-dragger :deep(.el-upload-dragger) {
  border: 2px dashed var(--border-color);
  border-radius: var(--border-radius-lg);
  background: var(--gray-50);
  transition: all var(--transition-fast);
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-dragger :deep(.el-upload-dragger:hover) {
  border-color: var(--primary-400);
  background: var(--primary-50);
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  color: var(--gray-300);
  margin-bottom: 12px;
}

.upload-text {
  font-size: 14px;
  color: var(--gray-500);
}

.upload-text em {
  color: var(--primary-500);
  font-style: normal;
}

.upload-hint {
  font-size: 12px;
  color: var(--gray-400);
  margin-top: 8px;
}

.upload-preview {
  position: relative;
  width: 100%;
  height: 100%;
}

.upload-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.preview-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.upload-dragger :deep(.el-upload-dragger:hover) .preview-overlay {
  opacity: 1;
}

/* 素材选择 */
.material-select-area {
  margin-top: 8px;
}

.select-material-btn {
  border: 2px dashed var(--border-color);
  background: var(--gray-50);
  height: 120px;
  width: 100%;
  border-radius: var(--border-radius-lg);
  font-size: 14px;
  color: var(--gray-500);
}

.select-material-btn:hover {
  border-color: var(--primary-400);
  background: var(--primary-50);
  color: var(--primary-600);
}

.selected-material-card {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 12px;
  padding: 12px;
  background: var(--gray-50);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
}

.selected-material-card img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: var(--border-radius-md);
}

.material-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.material-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-700);
}

/* 生成按钮 */
.form-actions {
  margin-top: 32px;
}

.create-btn {
  height: 48px;
  padding: 0 32px;
  font-size: 15px;
  font-weight: 500;
  border-radius: var(--border-radius-md);
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.cost-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  margin-left: 8px;
}

/* 结果展示 */
.result-section {
  margin-top: 40px;
  padding-top: 32px;
  border-top: 1px solid var(--border-color);
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.result-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--gray-800);
  margin: 0;
}

.result-count {
  font-size: 13px;
  color: var(--gray-500);
}

.result-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.result-image-wrapper {
  border-radius: var(--border-radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.result-image-wrapper:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.result-image {
  width: 100%;
  aspect-ratio: 1;
  display: block;
}

/* 工作流 */
.workflow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.workflow-card {
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.workflow-card:hover {
  border-color: var(--primary-300);
  box-shadow: var(--shadow-md);
  transform: translateY(-4px);
}

.workflow-thumbnail {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.workflow-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.workflow-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.workflow-card:hover .workflow-overlay {
  opacity: 1;
}

.workflow-overlay .el-icon {
  color: #fff;
}

.workflow-info {
  padding: 16px;
}

.workflow-info h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--gray-800);
  margin: 0 0 8px;
}

.workflow-info p {
  font-size: 13px;
  color: var(--gray-500);
  margin: 0 0 12px;
  line-height: 1.5;
}

/* 弹窗素材网格 */
.dialog-material-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding: 4px;
}

.dialog-material-item {
  position: relative;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dialog-material-item:hover {
  border-color: var(--primary-300);
}

.dialog-material-item.selected {
  border-color: var(--primary-500);
}

.dialog-material-item img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  display: block;
}

.material-check {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  background: var(--primary-500);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.dialog-material-item .material-name {
  padding: 8px;
  font-size: 12px;
  color: var(--gray-600);
  background: var(--gray-50);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
