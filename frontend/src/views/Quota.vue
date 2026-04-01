<template>
  <div class="quota-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">额度中心</h2>
      <p class="page-desc">查看额度余额和消费明细</p>
    </div>
    
    <!-- 额度统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card primary">
        <div class="stat-icon">
          <el-icon><Coin /></el-icon>
        </div>
        <div class="stat-content">
          <span class="stat-label">剩余额度</span>
          <span class="stat-value">{{ quotaInfo.remaining_quota }}</span>
        </div>
        <div class="stat-decoration"></div>
      </div>
      
      <div class="stat-card success">
        <div class="stat-icon">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-content">
          <span class="stat-label">免费额度</span>
          <span class="stat-value">{{ quotaInfo.free_quota }}</span>
        </div>
        <div class="stat-decoration"></div>
      </div>
      
      <div class="stat-card warning">
        <div class="stat-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <span class="stat-label">累计充值</span>
          <span class="stat-value">{{ quotaInfo.total_recharge }}</span>
        </div>
        <div class="stat-decoration"></div>
      </div>
      
      <div class="stat-card danger">
        <div class="stat-icon">
          <el-icon><ShoppingCart /></el-icon>
        </div>
        <div class="stat-content">
          <span class="stat-label">累计使用</span>
          <span class="stat-value">{{ quotaInfo.total_used }}</span>
        </div>
        <div class="stat-decoration"></div>
      </div>
    </div>
    
    <!-- 充值区域 -->
    <div class="recharge-section">
      <div class="section-header">
        <h3>额度充值</h3>
        <span class="section-desc">选择套餐，快速获取额度</span>
      </div>
      
      <div class="recharge-grid">
        <div 
          v-for="option in rechargeOptions"
          :key="option.amount"
          :class="['recharge-card', { active: selectedRecharge === option.amount }]"
          @click="selectedRecharge = option.amount"
        >
          <div class="recharge-amount">
            <span class="amount-value">{{ option.quota }}</span>
            <span class="amount-unit">额度</span>
          </div>
          <div class="recharge-price">
            <span class="price-symbol">¥</span>
            <span class="price-value">{{ option.price }}</span>
          </div>
          <div v-if="option.bonus" class="recharge-bonus">
            <el-icon><Present /></el-icon>
            <span>送 {{ option.bonus }} 额度</span>
          </div>
          <div class="recharge-check" v-if="selectedRecharge === option.amount">
            <el-icon><Check /></el-icon>
          </div>
        </div>
      </div>
      
      <div class="payment-section">
        <div class="payment-methods">
          <span class="payment-label">支付方式</span>
          <div class="method-options">
            <div 
              :class="['method-option', { active: paymentMethod === 'alipay' }]"
              @click="paymentMethod = 'alipay'"
            >
              <svg viewBox="0 0 24 24" width="24" height="24">
                <path fill="#1677FF" d="M21.422 15.358c-3.248-1.39-6.16-3.018-6.907-3.398a7.26 7.26 0 0 0 1.363-4.09h-2.68V6.22h3.394V5.165h-3.394V2.82h-1.723c-.305 0-.55.246-.55.55v1.795H7.536v1.055h3.389v1.75H8.238v1.055h7.11c-.332 1.752-1.395 3.197-2.857 4.085a33.86 33.86 0 0 0-2.242-1.037l-.096-.04c-1.96 1.01-4.69 2.25-6.876 3.023v1.213c2.04-.67 4.352-1.652 6.133-2.59 2.023 1.06 4.312 2.156 6.57 2.897 2.055.677 3.93 1.04 5.53 1.04.378 0 .816-.03 1.278-.088v-1.13a18.21 18.21 0 0 1-1.266.05z"/>
              </svg>
              <span>支付宝</span>
            </div>
            <div 
              :class="['method-option', { active: paymentMethod === 'wechat' }]"
              @click="paymentMethod = 'wechat'"
            >
              <svg viewBox="0 0 24 24" width="24" height="24">
                <path fill="#07C160" d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.36 24 16.891 24 15.282c0-3.37-3.247-6.23-7.062-6.424zm-2.731 2.706c.535 0 .969.44.969.983a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.543.434-.983.97-.983zm4.846 0c.535 0 .969.44.969.983a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.543.434-.983.97-.983z"/>
              </svg>
              <span>微信支付</span>
            </div>
          </div>
        </div>
        <el-button type="primary" size="large" class="pay-btn" @click="handleRecharge">
          <span>立即支付 ¥{{ currentPrice }}</span>
        </el-button>
      </div>
    </div>
    
    <!-- 额度明细 -->
    <div class="logs-section">
      <div class="section-header">
        <h3>额度明细</h3>
        <span class="section-desc">查看额度变动记录</span>
      </div>
      
      <div class="logs-table">
        <div class="table-header">
          <div class="th time">时间</div>
          <div class="th type">类型</div>
          <div class="th amount">变动</div>
          <div class="th balance">余额</div>
          <div class="th desc">说明</div>
        </div>
        
        <div class="table-body">
          <div v-if="quotaLogs.length === 0" class="empty-row">
            <el-empty description="暂无记录" :image-size="60" />
          </div>
          <div v-else class="log-row" v-for="log in quotaLogs" :key="log.id">
            <div class="td time">{{ formatTime(log.created_at) }}</div>
            <div class="td type">
              <span :class="['type-tag', log.log_type]">
                {{ getLogTypeLabel(log.log_type) }}
              </span>
            </div>
            <div class="td amount" :class="log.amount > 0 ? 'positive' : 'negative'">
              {{ log.amount > 0 ? '+' : '' }}{{ log.amount }}
            </div>
            <div class="td balance">{{ log.balance_after }}</div>
            <div class="td desc">{{ log.description }}</div>
          </div>
        </div>
      </div>
      
      <div class="pagination-wrapper" v-if="total > size">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="size"
          :total="total"
          layout="total, prev, pager, next"
          background
          @current-change="loadQuotaLogs"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Coin, Money, Histogram, ShoppingCart, Present, Check } from '@element-plus/icons-vue'
import { getQuotaInfo, getQuotaLogs } from '@/api/quota'

const quotaInfo = ref({
  free_quota: 0,
  remaining_quota: 0,
  total_recharge: 0,
  total_used: 0
})

const quotaLogs = ref([])
const page = ref(1)
const size = ref(20)
const total = ref(0)
const selectedRecharge = ref(100)
const paymentMethod = ref('alipay')

const rechargeOptions = [
  { amount: 100, quota: 100, price: 10 },
  { amount: 500, quota: 500, price: 45, bonus: 50 },
  { amount: 1000, quota: 1000, price: 80, bonus: 150 },
  { amount: 5000, quota: 5000, price: 350, bonus: 1000 }
]

const currentPrice = computed(() => {
  const option = rechargeOptions.find(o => o.amount === selectedRecharge.value)
  return option?.price || 0
})

onMounted(() => {
  loadQuotaInfo()
  loadQuotaLogs()
})

const loadQuotaInfo = async () => {
  const res = await getQuotaInfo()
  if (res.code === 200) {
    quotaInfo.value = res.data
  }
}

const loadQuotaLogs = async () => {
  const res = await getQuotaLogs({ page: page.value, size: size.value })
  if (res.code === 200) {
    quotaLogs.value = res.data.list
    total.value = res.data.total || 0
  }
}

const getLogTypeLabel = (type) => {
  const map = {
    'deduct': '扣费',
    'recharge': '充值',
    'gift': '赠送',
    'refund': '退款'
  }
  return map[type] || type
}

const handleRecharge = () => {
  ElMessage.info(`正在调起${paymentMethod.value === 'alipay' ? '支付宝' : '微信支付'}...`)
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
.quota-container {
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

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 24px;
}

.stat-card {
  position: relative;
  padding: 20px;
  border-radius: var(--border-radius-lg);
  display: flex;
  align-items: center;
  gap: 16px;
  overflow: hidden;
}

.stat-card.primary {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  color: #fff;
}

.stat-card.success {
  background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
  color: #fff;
}

.stat-card.warning {
  background: linear-gradient(135deg, #faad14 0%, #d48806 100%);
  color: #fff;
}

.stat-card.danger {
  background: linear-gradient(135deg, #ff4d4f 0%, #cf1322 100%);
  color: #fff;
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 13px;
  opacity: 0.9;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}

.stat-decoration {
  position: absolute;
  right: -20px;
  bottom: -20px;
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

/* 充值区域 */
.recharge-section {
  padding: 24px;
  border-top: 1px solid var(--border-color);
}

.section-header {
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--gray-800);
  margin: 0 0 4px;
}

.section-desc {
  font-size: 13px;
  color: var(--gray-500);
}

.recharge-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.recharge-card {
  position: relative;
  padding: 20px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.recharge-card:hover {
  border-color: var(--primary-300);
}

.recharge-card.active {
  border-color: var(--primary-500);
  background: var(--primary-50);
}

.recharge-amount {
  margin-bottom: 12px;
}

.amount-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--gray-800);
}

.amount-unit {
  font-size: 14px;
  color: var(--gray-500);
  margin-left: 4px;
}

.recharge-price {
  margin-bottom: 8px;
}

.price-symbol {
  font-size: 16px;
  color: var(--error-500);
}

.price-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--error-500);
}

.recharge-bonus {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  background: #fff7e6;
  color: #d48806;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.recharge-check {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  background: var(--primary-500);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
}

.payment-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.payment-methods {
  display: flex;
  align-items: center;
  gap: 16px;
}

.payment-label {
  font-size: 14px;
  color: var(--gray-600);
}

.method-options {
  display: flex;
  gap: 12px;
}

.method-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: 14px;
  color: var(--gray-600);
}

.method-option:hover {
  border-color: var(--gray-300);
}

.method-option.active {
  border-color: var(--primary-500);
  background: var(--primary-50);
  color: var(--primary-600);
}

.pay-btn {
  height: 44px;
  padding: 0 32px;
  font-size: 15px;
  font-weight: 500;
  border-radius: var(--border-radius-md);
}

/* 明细表格 */
.logs-section {
  padding: 24px;
  border-top: 1px solid var(--border-color);
}

.logs-table {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 140px 100px 100px 100px 1fr;
  background: var(--gray-50);
  border-bottom: 1px solid var(--border-color);
}

.th {
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--gray-700);
}

.table-body {
  max-height: 400px;
  overflow-y: auto;
}

.log-row {
  display: grid;
  grid-template-columns: 140px 100px 100px 100px 1fr;
  border-bottom: 1px solid var(--border-color);
  transition: background var(--transition-fast);
}

.log-row:last-child {
  border-bottom: none;
}

.log-row:hover {
  background: var(--gray-50);
}

.td {
  padding: 14px 16px;
  font-size: 13px;
  color: var(--gray-600);
}

.td.time {
  color: var(--gray-500);
}

.type-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.type-tag.deduct {
  background: #fff2f0;
  color: #cf1322;
}

.type-tag.recharge {
  background: #f6ffed;
  color: #389e0d;
}

.type-tag.gift {
  background: #fffbe6;
  color: #d48806;
}

.type-tag.refund {
  background: var(--gray-100);
  color: var(--gray-600);
}

.td.amount.positive {
  color: #52c41a;
  font-weight: 600;
}

.td.amount.negative {
  color: #ff4d4f;
  font-weight: 600;
}

.empty-row {
  padding: 40px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .recharge-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .recharge-grid {
    grid-template-columns: 1fr;
  }
  
  .payment-section {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .payment-methods {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
