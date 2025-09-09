<template>
  <div class="app-container">
    <div class="main-content">
      <div class="top-row">
        <div class="otherbox-section">
          <el-card class="otherbox-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span>数据导出中心</span>
                </div>
              </div>
            </template>

            <div class="function-grid">
              <!-- 导出功能卡片 -->
              <div class="function-card" @click="exportGroupMembers">
                <div class="card-icon">
                  <i class="el-icon-user-solid"></i>
                </div>
                <div class="card-title">群成员导出</div>
              </div>

              <div class="function-card" @click="exportGroupMessages">
                <div class="card-icon">
                  <i class="el-icon-chat-line-round"></i>
                </div>
                <div class="card-title">消息记录导出</div>
              </div>

              <div class="function-card" @click="exportGroupFiles">
                <div class="card-icon">
                  <i class="el-icon-folder"></i>
                </div>
                <div class="card-title">文件数据导出</div>
              </div>

              <div class="function-card" @click="exportGroupImages">
                <div class="card-icon">
                  <i class="el-icon-picture"></i>
                </div>
                <div class="card-title">图片数据导出</div>
              </div>

              <div class="function-card" @click="exportGroupVoices">
                <div class="card-icon">
                  <i class="el-icon-mic"></i>
                </div>
                <div class="card-title">语音数据导出</div>
              </div>

              <div class="function-card" @click="exportGroupVideos">
                <div class="card-icon">
                  <i class="el-icon-video-camera"></i>
                </div>
                <div class="card-title">视频数据导出</div>
              </div>

              <div class="function-card" @click="exportGroupLinks">
                <div class="card-icon">
                  <i class="el-icon-link"></i>
                </div>
                <div class="card-title">链接数据导出</div>
              </div>
            </div>
          </el-card>
        </div>

        <div class="otherbox-section">
          <el-card class="otherbox-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span>报表生成</span>
                </div>
              </div>
            </template>
            <div class="report-container">
              <div class="report-settings">
                <div class="setting-item">
                  <span class="setting-label">接收报表推送</span>
                  <el-switch v-model="reportPushEnabled" />
                </div>
                
                <div class="report-tabs">
                  <el-tabs v-model="activeReportTab" @tab-click="handleReportTabChange">
                    <el-tab-pane label="日报" name="daily">
                      <div class="tab-content">
                        <div class="date-selector">
                          <span class="selector-label">选择日期：</span>
                          <el-date-picker 
                            v-model="dailyDate" 
                            type="date" 
                            placeholder="选择日期"
                            format="YYYY-MM-DD"
                            value-format="YYYY-MM-DD"
                            @change="handleDailyDateChange"
                          />
                        </div>
                      </div>
                    </el-tab-pane>
                    <el-tab-pane label="周报" name="weekly">
                      <div class="tab-content">
                        <div class="week-selector">
                          <span class="selector-label">选择周：</span>
                          <el-select v-model="selectedWeek" placeholder="选择周" @change="handleWeekChange">
                            <el-option 
                              v-for="week in weekOptions" 
                              :key="week.value" 
                              :label="week.label" 
                              :value="week.value"
                            />
                          </el-select>
                        </div>
                      </div>
                    </el-tab-pane>
                    <el-tab-pane label="月报" name="monthly">
                      <div class="tab-content">
                        <div class="month-selector">
                          <span class="selector-label">选择月份：</span>
                          <el-date-picker 
                            v-model="monthlyDate" 
                            type="month" 
                            placeholder="选择月份"
                            format="YYYY-MM"
                            value-format="YYYY-MM"
                            @change="handleMonthlyDateChange"
                          />
                        </div>
                      </div>
                    </el-tab-pane>
                  </el-tabs>
                </div>
              </div>
              
              <div class="report-preview">
                <el-empty description="报表生成功能正在建设中" :image-size="200">
                  <template #image>
                    <el-icon :size="60" color="#909399"><Document /></el-icon>
                  </template>
                </el-empty>
              </div>
            </div>
          </el-card>
        </div>

        <div class="otherbox-section">
          <el-card class="otherbox-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span>数据提取与汇总</span>
                </div>
              </div>
            </template>
            <div class="function-grid">
              <div class="function-card" @click="extractDataSummary">
                <div class="card-icon">
                  <i class="el-icon-data-analysis"></i>
                </div>
                <div class="card-title">提取关键数据并分析</div>
              </div>
            </div>
          </el-card>
        </div>

        <div class="otherbox-section">
          <el-card class="otherbox-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span>知识库构建</span>
                </div>
              </div>
            </template>
            <div class="function-grid">
              <div class="function-card" @click="buildKnowledgeBase">
                <div class="card-icon">
                  <i class="el-icon-reading"></i>
                </div>
                <div class="card-title">构建AI知识库数据集</div>
              </div>
            </div>
          </el-card>
        </div>

        <div class="otherbox-section">
          <el-card class="otherbox-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span>舆情监控优化</span>
                </div>
              </div>
            </template>
            <div class="function-grid">
              <div class="function-card" @click="optimizeSentimentMonitoring">
                <div class="card-icon">
                  <i class="el-icon-warning"></i>
                </div>
                <div class="card-title">增强不当言论识别预警</div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { ref, onMounted } from 'vue'

// ===== 响应式数据 =====
const reportPushEnabled = ref(false)
const activeReportTab = ref('daily')
const dailyDate = ref('')
const selectedWeek = ref('')
const monthlyDate = ref('')
const reportContent = ref('')
const reportTitle = ref('')
const weekOptions = ref([])

// ===== 工具函数 =====
// 初始化周选项
const initWeekOptions = () => {
  const options = []
  const currentYear = new Date().getFullYear()
  const currentMonth = new Date().getMonth() + 1
  
  // 获取当月的天数
  const daysInMonth = new Date(currentYear, currentMonth, 0).getDate()
  
  // 计算当月有几周
  const firstDay = new Date(currentYear, currentMonth - 1, 1)
  
  // 计算第一周的开始日期
  let startDay = 1
  if (firstDay.getDay() !== 1) {
    // 如果第一天不是周一，找到第一个周一
    startDay = 1 + (8 - firstDay.getDay()) % 7
  }
  
  // 生成周选项
  let weekCount = 1
  for (let day = startDay; day <= daysInMonth; day += 7) {
    const endDay = Math.min(day + 6, daysInMonth)
    options.push({
      value: `${currentMonth}月第${weekCount}周`,
      label: `${currentMonth}月第${weekCount}周 (${day}日-${endDay}日)`
    })
    weekCount++
  }
  
  weekOptions.value = options
}

// ===== 事件处理函数 =====
// 处理报表标签页切换
const handleReportTabChange = () => {
  // 清空报表内容
  reportContent.value = ''
  reportTitle.value = ''
}

// 处理日报日期变化
const handleDailyDateChange = () => {
  reportContent.value = ''
  reportTitle.value = ''
}

// 处理周报选择变化
const handleWeekChange = () => {
  reportContent.value = ''
  reportTitle.value = ''
}

// 处理月报日期变化
const handleMonthlyDateChange = () => {
  reportContent.value = ''
  reportTitle.value = ''
}

// ===== API 调用函数 =====
// 导出群成员
const exportGroupMembers = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/export/group-members')
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `group_members_export_${new Date().toISOString().slice(0, 10)}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      ElMessage.success('群成员导出成功')
    } else {
      throw new Error('群成员导出功能正在建设中')
    }
  } catch (error) {
    ElMessage.error(`${error.message}`)
  }
}

// 导出群消息
const exportGroupMessages = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/export/group-messages')
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `group_messages_export_${new Date().toISOString().slice(0, 10)}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      ElMessage.success('消息记录导出成功')
    } else {
      throw new Error('消息记录导出功能正在建设中')
    }
  } catch (error) {
    ElMessage.error(`${error.message}`)
  }
}

// 导出群文件
const exportGroupFiles = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/export/group-files')
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `group_files_export_${new Date().toISOString().slice(0, 10)}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      ElMessage.success('文件数据导出成功')
    } else {
      throw new Error('文件数据导出功能正在建设中')
    }
  } catch (error) {
    ElMessage.error(`${error.message}`)
  }
}

// 导出群图片
const exportGroupImages = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/export/group-images')
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `group_images_export_${new Date().toISOString().slice(0, 10)}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      ElMessage.success('图片数据导出成功')
    } else {
      throw new Error('图片数据导出功能正在建设中')
    }
  } catch (error) {
    ElMessage.error(`${error.message}`)
  }
}

// 导出群语音
const exportGroupVoices = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/export/group-voices')
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `group_voices_export_${new Date().toISOString().slice(0, 10)}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      ElMessage.success('语音数据导出成功')
    } else {
      throw new Error('语音数据导出功能正在建设中')
    }
  } catch (error) {
    ElMessage.error(`${error.message}`)
  }
}

// 导出群视频
const exportGroupVideos = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/export/group-videos')
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `group_videos_export_${new Date().toISOString().slice(0, 10)}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      ElMessage.success('视频数据导出成功')
    } else {
      throw new Error('视频数据导出功能正在建设中')
    }
  } catch (error) {
    ElMessage.error(`${error.message}`)
  }
}

// 导出群链接
const exportGroupLinks = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/export/group-links')
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `group_links_export_${new Date().toISOString().slice(0, 10)}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      ElMessage.success('链接数据导出成功')
    } else {
      throw new Error('链接数据导出功能正在建设中')
    }
  } catch (error) {
    ElMessage.error(`${error.message}`)
  }
}

// 提取数据汇总
const extractDataSummary = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/data/extract-summary')
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `data_summary_${new Date().toISOString().slice(0, 10)}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      ElMessage.success('数据提取与汇总成功')
    } else {
      throw new Error('数据提取与汇总功能正在建设中')
    }
  } catch (error) {
    ElMessage.error(`${error.message}`)
  }
}

// 构建知识库
const buildKnowledgeBase = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/knowledge/build')
    if (response.ok) {
      const data = await response.json()
      ElMessage.success(`知识库构建成功: ${data.message || '构建完成'}`)
    } else {
      throw new Error('知识库构建功能正在建设中')
    }
  } catch (error) {
    ElMessage.error(`${error.message}`)
  }
}

// 优化舆情监控
const optimizeSentimentMonitoring = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/sentiment/optimize')
    if (response.ok) {
      const data = await response.json()
      ElMessage.success(`舆情监控优化成功: ${data.message || '优化完成'}`)
    } else {
      throw new Error('舆情监控优化功能正在建设中')
    }
  } catch (error) {
    ElMessage.error(`${error.message}`)
  }
}

// ===== 生命周期钩子 =====
// 组件挂载时初始化
onMounted(() => {
  initWeekOptions()
})
</script>

<style scoped>
:root {
  --primary-color: #3b82f6;
  --primary-dark: #1d4ed8;
  --primary-light: #93c5fd;
  --secondary-color: #60a5fa;
  --accent-color: #2563eb;
  --light-color: #f8fafc;
  --dark-color: #1e293b;
  --text-primary: #0f172a;
  --text-secondary: #64748b;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
  --border-color: #e2e8f0;
  --card-bg: #ffffff;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --transition: all 0.3s ease;
}

.app-container {
  padding: 0;
}

.main-content {
  max-width: 100%;
  margin: 0 auto;
}

.top-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.otherbox-card {
  border-radius: 12px;
  border: 1px solid var(--border-color);
  transition: var(--transition);
  overflow: hidden;
  background-color: white;
  margin-bottom: 24px;
}

.otherbox-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  border-color: var(--primary-light);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background-color: white;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: var(--text-primary);
}

.function-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  padding: 16px;
}

.function-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  cursor: pointer;
  transition: var(--transition);
  border: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
}

.function-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.function-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-light);
}

.function-card:hover::before {
  transform: scaleX(1);
}

.function-card:active {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.card-icon {
  font-size: 32px;
  color: var(--primary-color);
  margin-bottom: 12px;
  transition: var(--transition);
}

.function-card:hover .card-icon {
  color: var(--primary-dark);
  transform: scale(1.1);
}

.card-title {
  font-size: 15px;
  color: var(--dark-color);
  text-align: center;
  font-weight: 500;
  transition: color 0.3s ease;
}

.function-card:hover .card-title {
  color: var(--primary-dark);
}

@media (max-width: 768px) {
  .function-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
  
  .report-container {
    flex-direction: column;
  }
  
  .report-settings {
    margin-bottom: 20px;
  }
}

/* 报表生成相关样式 */
.report-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.report-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: var(--light-color);
  border-radius: 8px;
}

.setting-label {
  font-weight: 500;
  color: var(--dark-color);
}

.report-tabs {
  margin-top: 10px;
}

.tab-content {
  padding: 16px 0;
}

.date-selector,
.week-selector,
.month-selector {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.selector-label {
  margin-right: 12px;
  font-weight: 500;
  color: var(--dark-color);
  min-width: 80px;
}

.report-actions {
  display: flex;
  justify-content: flex-end;
}

.report-preview {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 40px 16px;
  background-color: var(--card-bg);
  min-height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
