<template>
  <div class="about-container">
    <div class="about-card">
      <!-- 头部 -->
      <div class="about-header">
        <div class="avatar">
          <el-icon :size="64"><User /></el-icon>
        </div>
        <h1 class="title">AI 创作平台</h1>
        <p class="subtitle">让 AI 创作更简单</p>
      </div>

      <!-- 作者信息 -->
      <div class="author-section">
        <h2 class="section-title">关于作者</h2>
        <div class="author-info">
          <div class="info-item">
            <div class="info-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="info-content">
              <span class="info-label">作者</span>
              <span class="info-value">duckzhou</span>
            </div>
          </div>

          <div class="info-item">
            <div class="info-icon">
              <el-icon><Phone /></el-icon>
            </div>
            <div class="info-content">
              <span class="info-label">联系电话</span>
              <span class="info-value">15001793929</span>
            </div>
          </div>

          <div class="info-item">
            <div class="info-icon">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="info-content">
              <span class="info-label">版本</span>
              <span class="info-value">v1.0.0</span>
            </div>
          </div>

          <div class="info-item">
            <div class="info-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="info-content">
              <span class="info-label">构建日期</span>
              <span class="info-value">2026 年 4 月</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 技术栈 -->
      <div class="tech-section">
        <h2 class="section-title">技术栈</h2>
        <div class="tech-tags">
          <el-tag type="primary" effect="plain">Vue 3</el-tag>
          <el-tag type="primary" effect="plain">FastAPI</el-tag>
          <el-tag type="success" effect="plain">Element Plus</el-tag>
          <el-tag type="success" effect="plain">Pinia</el-tag>
          <el-tag type="warning" effect="plain">Celery</el-tag>
          <el-tag type="warning" effect="plain">Redis</el-tag>
          <el-tag type="info" effect="plain">SQLAlchemy</el-tag>
          <el-tag type="info" effect="plain">PostgreSQL</el-tag>
        </div>
      </div>

      <!-- 功能介绍 -->
      <div class="features-section">
        <h2 class="section-title">核心功能</h2>
        <div class="feature-list">
          <div class="feature-item">
            <div class="feature-icon primary">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="feature-content">
              <h3>AI 对话</h3>
              <p>支持通义千问多个模型，具备深度思考和联网搜索能力</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon success">
              <el-icon><Picture /></el-icon>
            </div>
            <div class="feature-content">
              <h3>文生图</h3>
              <p>根据文字描述生成精美图片</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon warning">
              <el-icon><MagicStick /></el-icon>
            </div>
            <div class="feature-content">
              <h3>图生图</h3>
              <p>根据参考图片生成新图片</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon danger">
              <el-icon><VideoCamera /></el-icon>
            </div>
            <div class="feature-content">
              <h3>图生视频</h3>
              <p>将静态图片转换为动态视频</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 页脚 -->
      <div class="about-footer">
        <p>© 2026 AI 创作平台 · All Rights Reserved</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  User,
  Phone,
  Timer,
  Calendar,
  ChatDotRound,
  Picture,
  MagicStick,
  VideoCamera
} from '@element-plus/icons-vue'
</script>

<style scoped>
.about-container {
  min-height: calc(100vh - 84px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.about-card {
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 800px;
  width: 100%;
  overflow: hidden;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.about-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px 40px;
  text-align: center;
  color: #fff;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  backdrop-filter: blur(10px);
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 12px;
  letter-spacing: 2px;
}

.subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.author-section,
.tech-section,
.features-section {
  padding: 40px;
  border-bottom: 1px solid #f0f0f0;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0 0 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title::before {
  content: '';
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
}

.author-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s;
}

.info-item:hover {
  background: #fff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.info-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 24px;
  flex-shrink: 0;
}

.info-content {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tech-tags .el-tag {
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 8px;
  font-weight: 500;
}

.feature-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.feature-item {
  display: flex;
  gap: 16px;
  padding: 24px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s;
}

.feature-item:hover {
  background: #fff;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  transform: translateY(-4px);
}

.feature-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
  flex-shrink: 0;
}

.feature-icon.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.feature-icon.success {
  background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
}

.feature-icon.warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.feature-icon.danger {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.feature-content {
  flex: 1;
}

.feature-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px;
}

.feature-content p {
  font-size: 14px;
  color: #666;
  margin: 0;
  line-height: 1.6;
}

.about-footer {
  padding: 30px 40px;
  text-align: center;
  background: #f8f9fa;
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .about-container {
    padding: 20px 10px;
  }

  .about-header {
    padding: 40px 20px;
  }

  .title {
    font-size: 28px;
  }

  .author-section,
  .tech-section,
  .features-section {
    padding: 30px 20px;
  }

  .feature-list {
    grid-template-columns: 1fr;
  }

  .feature-item {
    flex-direction: column;
    text-align: center;
  }

  .feature-icon {
    margin: 0 auto;
  }
}
</style>
