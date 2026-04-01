<template>
  <div class="materials-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">素材管理</h2>
        <p class="page-desc">管理和组织您的创作素材</p>
      </div>
      <el-button type="primary" class="upload-btn" @click="uploadDialogVisible = true">
        <el-icon><Upload /></el-icon>
        <span>上传素材</span>
      </el-button>
    </div>
    
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="filter-group">
        <div class="type-tabs">
          <div 
            v-for="type in typeOptions" 
            :key="type.value"
            :class="['type-tab', { active: filterType === type.value }]"
            @click="filterType = type.value; loadMaterials()"
          >
            <el-icon><component :is="type.icon" /></el-icon>
            <span>{{ type.label }}</span>
            <span class="type-count" v-if="typeCounts[type.value]">{{ typeCounts[type.value] }}</span>
          </div>
        </div>
      </div>
      
      <div class="search-group">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索素材名称..."
          class="search-input"
          clearable
          @keyup.enter="loadMaterials"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>
    
    <!-- 素材网格 -->
    <div class="materials-grid" v-loading="loading">
      <div v-if="materials.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无素材">
          <el-button type="primary" @click="uploadDialogVisible = true">上传素材</el-button>
        </el-empty>
      </div>
      
      <div v-else class="grid-content">
        <div 
          v-for="material in materials" 
          :key="material.id" 
          class="material-card"
        >
          <div class="card-preview" @click="previewMaterial(material)">
            <img
              v-if="material.material_type === 'image'"
              :src="material.thumbnail_url || material.file_url"
            />
            <div v-else-if="material.material_type === 'video'" class="video-preview">
              <el-icon :size="40"><VideoPlay /></el-icon>
              <span>视频素材</span>
            </div>
            <div v-else class="file-preview">
              <el-icon :size="40"><Document /></el-icon>
              <span>{{ material.file_format || '文件' }}</span>
            </div>
            
            <div class="card-overlay">
              <el-icon :size="24"><ZoomIn /></el-icon>
              <span>预览</span>
            </div>
          </div>
          
          <div class="card-body">
            <div class="card-header">
              <h4 class="card-title">{{ material.name }}</h4>
              <el-dropdown trigger="click" @command="(cmd) => handleAction(cmd, material)">
                <el-icon class="more-btn"><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="preview">
                      <el-icon><View /></el-icon>
                      预览
                    </el-dropdown-item>
                    <el-dropdown-item command="download">
                      <el-icon><Download /></el-icon>
                      下载
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" divided>
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            
            <div class="card-meta">
              <span class="meta-type">
                <el-icon><component :is="getTypeIcon(material.material_type)" /></el-icon>
                {{ getTypeLabel(material.material_type) }}
              </span>
              <span class="meta-size">{{ formatSize(material.file_size) }}</span>
            </div>
            
            <div class="card-tags" v-if="material.tags && material.tags.length">
              <el-tag 
                v-for="tag in material.tags.slice(0, 3)" 
                :key="tag" 
                size="small"
                effect="light"
              >
                {{ tag }}
              </el-tag>
              <span v-if="material.tags.length > 3" class="more-tags">+{{ material.tags.length - 3 }}</span>
            </div>
            
            <div class="card-time">
              <el-icon><Clock /></el-icon>
              {{ formatTime(material.created_at) }}
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
        @current-change="loadMaterials"
      />
    </div>
    
    <!-- 上传弹窗 -->
    <el-dialog v-model="uploadDialogVisible" title="上传素材" width="560px" class="upload-dialog">
      <div class="upload-content">
        <div class="type-selector">
          <label class="form-label">素材类型</label>
          <div class="type-options">
            <div 
              v-for="type in typeOptions" 
              :key="type.value"
              :class="['type-option', { active: uploadForm.material_type === type.value }]"
              @click="uploadForm.material_type = type.value"
            >
              <el-icon :size="24"><component :is="type.icon" /></el-icon>
              <span>{{ type.label }}</span>
            </div>
          </div>
        </div>
        
        <div class="upload-area">
          <label class="form-label required">选择文件</label>
          <el-upload
            class="upload-dragger"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            :show-file-list="false"
          >
            <div v-if="!uploadForm.file" class="upload-placeholder">
              <el-icon class="upload-icon"><Upload /></el-icon>
              <div class="upload-text">
                <span>拖拽文件到此处或</span>
                <em>点击上传</em>
              </div>
              <div class="upload-hint">{{ getUploadHint(uploadForm.material_type) }}</div>
            </div>
            <div v-else class="upload-file-info">
              <el-icon class="file-icon"><Document /></el-icon>
              <div class="file-details">
                <span class="file-name">{{ uploadForm.file.name }}</span>
                <span class="file-size">{{ formatSize(uploadForm.file.size) }}</span>
              </div>
              <el-button type="danger" text size="small" @click.stop="uploadForm.file = null">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </el-upload>
        </div>
        
        <div class="form-row">
          <div class="form-item">
            <label class="form-label">素材名称</label>
            <el-input v-model="uploadForm.name" placeholder="输入素材名称" />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-item">
            <label class="form-label">分类</label>
            <el-select v-model="uploadForm.category" placeholder="选择分类" clearable>
              <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
            </el-select>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-item">
            <label class="form-label">标签</label>
            <el-select v-model="uploadForm.tags" multiple placeholder="选择标签" filterable allow-create>
              <el-option v-for="tag in allTags" :key="tag" :label="tag" :value="tag" />
            </el-select>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">
          <el-icon v-if="!uploading"><Upload /></el-icon>
          {{ uploading ? '上传中...' : '上传素材' }}
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 预览弹窗 -->
    <el-dialog v-model="previewVisible" title="素材预览" width="800px" class="preview-dialog">
      <div v-if="currentMaterial" class="preview-content">
        <div class="preview-main">
          <img
            v-if="currentMaterial.material_type === 'image'"
            :src="currentMaterial.file_url"
          />
          <video
            v-else-if="currentMaterial.material_type === 'video'"
            :src="currentMaterial.file_url"
            controls
          />
          <div v-else class="preview-file">
            <el-icon :size="64"><Document /></el-icon>
            <span>{{ currentMaterial.file_format || '文件' }}</span>
          </div>
        </div>
        
        <div class="preview-sidebar">
          <h4>素材信息</h4>
          <div class="info-item">
            <span class="info-label">名称</span>
            <span class="info-value">{{ currentMaterial.name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">类型</span>
            <span class="info-value">{{ getTypeLabel(currentMaterial.material_type) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">大小</span>
            <span class="info-value">{{ formatSize(currentMaterial.file_size) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">格式</span>
            <span class="info-value">{{ currentMaterial.file_format || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">上传时间</span>
            <span class="info-value">{{ formatTime(currentMaterial.created_at) }}</span>
          </div>
          
          <div class="preview-actions">
            <el-button type="primary" @click="downloadFile(currentMaterial.file_url, currentMaterial.name)">
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button type="danger" @click="deleteMaterial(currentMaterial.id); previewVisible = false">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { Plus, Search, Document, Upload, VideoPlay, ZoomIn, MoreFilled, View, Download, Delete, Clock, Picture, Film, Files } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMaterials, uploadMaterial, deleteMaterial as deleteMaterialApi, getCategories, getTags } from '@/api/material'

const materials = ref([])
const loading = ref(false)
const page = ref(1)
const size = ref(20)
const total = ref(0)
const filterType = ref('')
const searchKeyword = ref('')
const uploadDialogVisible = ref(false)
const previewVisible = ref(false)
const currentMaterial = ref(null)
const uploading = ref(false)
const typeCounts = reactive({})

const typeOptions = [
  { value: '', label: '全部', icon: 'Files' },
  { value: 'image', label: '图片', icon: 'Picture' },
  { value: 'video', label: '视频', icon: 'VideoPlay' },
  { value: 'text', label: '文本', icon: 'Document' },
]

const uploadForm = ref({
  material_type: 'image',
  name: '',
  category: '',
  tags: [],
  file: null
})

const categories = ref([])
const allTags = ref([])

onMounted(() => {
  loadMaterials()
  loadCategoriesAndTags()
})

const loadCategoriesAndTags = async () => {
  const [catRes, tagRes] = await Promise.all([getCategories(), getTags()])
  if (catRes.code === 200) categories.value = catRes.data.list
  if (tagRes.code === 200) allTags.value = tagRes.data.list
}

const loadMaterials = async () => {
  loading.value = true
  try {
    const res = await getMaterials({
      page: page.value,
      size: size.value,
      material_type: filterType.value,
      keyword: searchKeyword.value
    })
    if (res.code === 200) {
      materials.value = res.data.list
      total.value = res.data.total || 0
    }
  } finally {
    loading.value = false
  }
}

const handleFileChange = (file) => {
  uploadForm.value.file = file.raw
  if (!uploadForm.value.name) {
    uploadForm.value.name = file.name.replace(/\.[^/.]+$/, '')
  }
}

const handleUpload = async () => {
  if (!uploadForm.value.file) {
    ElMessage.warning('请选择文件')
    return
  }
  
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadForm.value.file)
    formData.append('name', uploadForm.value.name)
    formData.append('material_type', uploadForm.value.material_type)
    formData.append('category', uploadForm.value.category)
    formData.append('tags', uploadForm.value.tags.join(','))
    
    const res = await uploadMaterial(formData)
    if (res.code === 200) {
      ElMessage.success('上传成功')
      uploadDialogVisible.value = false
      loadMaterials()
      uploadForm.value = {
        material_type: 'image',
        name: '',
        category: '',
        tags: [],
        file: null
      }
    }
  } finally {
    uploading.value = false
  }
}

const handleAction = (command, material) => {
  switch (command) {
    case 'preview':
      previewMaterial(material)
      break
    case 'download':
      downloadFile(material.file_url, material.name)
      break
    case 'delete':
      deleteMaterial(material.id)
      break
  }
}

const previewMaterial = (material) => {
  currentMaterial.value = material
  previewVisible.value = true
}

const deleteMaterial = async (id) => {
  await ElMessageBox.confirm('确定删除该素材吗？', '提示', { type: 'warning' })
  const res = await deleteMaterialApi(id)
  if (res.code === 200) {
    ElMessage.success('删除成功')
    loadMaterials()
  }
}

const getTypeIcon = (type) => {
  const map = { image: 'Picture', video: 'VideoPlay', text: 'Document' }
  return map[type] || 'Document'
}

const getTypeLabel = (type) => {
  const map = { image: '图片', video: '视频', text: '文本' }
  return map[type] || type
}

const getUploadHint = (type) => {
  const hints = {
    image: '支持 JPG、PNG、GIF 格式，最大 10MB',
    video: '支持 MP4、MOV 格式，最大 100MB',
    text: '支持 TXT、MD、DOC 格式，最大 10MB'
  }
  return hints[type] || '选择文件上传'
}

const formatSize = (size) => {
  if (!size) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let index = 0
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024
    index++
  }
  return `${size.toFixed(1)} ${units[index]}`
}

const formatTime = (time) => {
  return new Date(time).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const downloadFile = (url, filename) => {
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.target = '_blank'
  a.click()
}
</script>

<style scoped>
.materials-container {
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

.upload-btn {
  height: 40px;
  padding: 0 20px;
  border-radius: var(--border-radius-md);
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: var(--gray-50);
  border-bottom: 1px solid var(--border-color);
}

.type-tabs {
  display: flex;
  gap: 8px;
}

.type-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: 13px;
  font-weight: 500;
  color: var(--gray-600);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.type-tab:hover {
  border-color: var(--primary-300);
  color: var(--primary-600);
}

.type-tab.active {
  background: var(--primary-500);
  border-color: var(--primary-500);
  color: #fff;
}

.type-count {
  background: rgba(0, 0, 0, 0.1);
  padding: 1px 6px;
  border-radius: 10px;
  font-size: 11px;
}

.type-tab.active .type-count {
  background: rgba(255, 255, 255, 0.2);
}

.search-input {
  width: 280px;
}

/* 素材网格 */
.materials-grid {
  min-height: 400px;
}

.empty-state {
  padding: 60px 0;
}

.grid-content {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
  padding: 24px;
}

.material-card {
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  transition: all var(--transition-fast);
}

.material-card:hover {
  border-color: var(--primary-300);
  box-shadow: var(--shadow-md);
}

.card-preview {
  position: relative;
  height: 180px;
  background: var(--gray-100);
  cursor: pointer;
  overflow: hidden;
}

.card-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-preview,
.file-preview {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--gray-400);
  font-size: 13px;
}

.card-overlay {
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

.card-preview:hover .card-overlay {
  opacity: 1;
}

.card-body {
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--gray-800);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.more-btn {
  padding: 4px;
  color: var(--gray-400);
  cursor: pointer;
  border-radius: var(--border-radius-sm);
  transition: all var(--transition-fast);
}

.more-btn:hover {
  background: var(--gray-100);
  color: var(--gray-600);
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.meta-type {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--gray-500);
}

.meta-size {
  font-size: 12px;
  color: var(--gray-400);
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.more-tags {
  font-size: 11px;
  color: var(--gray-400);
  padding: 2px 6px;
  background: var(--gray-100);
  border-radius: 4px;
}

.card-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--gray-400);
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 24px;
  border-top: 1px solid var(--border-color);
}

/* 上传弹窗 */
.upload-content {
  padding: 8px 0;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--gray-700);
  margin-bottom: 8px;
}

.form-label.required::after {
  content: '*';
  color: var(--error-500);
  margin-left: 4px;
}

.type-selector {
  margin-bottom: 20px;
}

.type-options {
  display: flex;
  gap: 12px;
}

.type-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: 13px;
  color: var(--gray-600);
}

.type-option:hover {
  border-color: var(--primary-300);
}

.type-option.active {
  border-color: var(--primary-500);
  background: var(--primary-50);
  color: var(--primary-600);
}

.upload-area {
  margin-bottom: 20px;
}

.upload-dragger :deep(.el-upload-dragger) {
  border: 2px dashed var(--border-color);
  border-radius: var(--border-radius-lg);
  background: var(--gray-50);
  width: 100%;
  height: auto;
  padding: 24px;
}

.upload-dragger :deep(.el-upload-dragger:hover) {
  border-color: var(--primary-400);
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  font-size: 40px;
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

.upload-file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  font-size: 32px;
  color: var(--primary-500);
}

.file-details {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-800);
}

.file-size {
  font-size: 12px;
  color: var(--gray-500);
}

.form-row {
  margin-bottom: 16px;
}

.form-item .el-select {
  width: 100%;
}

/* 预览弹窗 */
.preview-content {
  display: flex;
  gap: 24px;
}

.preview-main {
  flex: 1;
  background: var(--gray-100);
  border-radius: var(--border-radius-md);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.preview-main img,
.preview-main video {
  max-width: 100%;
  max-height: 500px;
}

.preview-file {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--gray-400);
}

.preview-sidebar {
  width: 240px;
  flex-shrink: 0;
}

.preview-sidebar h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--gray-800);
  margin: 0 0 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.info-label {
  font-size: 13px;
  color: var(--gray-500);
}

.info-value {
  font-size: 13px;
  font-weight: 500;
  color: var(--gray-800);
}

.preview-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 24px;
}

.preview-actions .el-button {
  width: 100%;
}
</style>
