<template>
  <div class="app-container">
    <div class="main-content">
      <!-- 群聊选择区域 -->
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card shadow="hover" class="group-selection-card">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <el-icon class="header-icon"><Setting /></el-icon>
                  <span>群聊选择</span>
                </div>
                <el-tooltip content="选择需要管理的群聊以启用相关功能" placement="top">
                  <el-icon><QuestionFilled /></el-icon>
                </el-tooltip>
              </div>
            </template>

            <el-form label-position="top">
              <el-form-item label="选择要管理的群聊">
                <el-row :gutter="16" align="middle">
                  <el-col :span="16">
                    <el-input
                      v-model="selectedGroup"
                      placeholder="输入群聊名称或选择已有群聊"
                      clearable
                      @clear="handleClearGroup"
                      size="large"
                      class="group-input">
                      <template #prefix>
                        <el-icon><View /></el-icon>
                      </template>
                      <template #append>
                        <el-button :icon="Search" @click="showGroupSelector">选择</el-button>
                      </template>
                    </el-input>
                  </el-col>
                  <el-col :span="8">
                    <el-switch
                      v-model="managementEnabled"
                      inline-prompt
                      active-text="管理中"
                      inactive-text="未管理"
                      @change="handleManagementChange"
                      :disabled="!selectedGroup"
                      :loading="managementLoading"
                      active-color="var(--success-color)"
                      style="width: 100%"
                      class="management-switch"
                    />
                  </el-col>
                </el-row>
              </el-form-item>
              
              <el-form-item v-if="selectedGroup" class="group-info">
                <el-row :gutter="16">
                  <el-col :span="8">
                    <div class="stat-item">
                      <div class="stat-label">成员数量</div>
                      <div class="stat-value">128</div>
                    </div>
                  </el-col>
                  <el-col :span="8">
                    <div class="stat-item">
                      <div class="stat-label">今日消息</div>
                      <div class="stat-value">342</div>
                    </div>
                  </el-col>
                  <el-col :span="8">
                    <div class="stat-item">
                      <div class="stat-label">活跃度</div>
                      <div class="stat-value">85%</div>
                    </div>
                  </el-col>
                </el-row>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>

      <!-- 功能区域 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <!-- 数据收集配置 -->
        <el-col :span="12">
          <el-card shadow="hover" class="feature-card" :class="{ 'disabled-card': !managementEnabled }">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <el-icon class="feature-icon data-collection"><Collection /></el-icon>
                  <span>数据收集配置</span>
                </div>
                <div class="header-status">
                  <el-tag :type="dataCollectionEnabled ? 'success' : 'info'" effect="light" size="small">
                    {{ dataCollectionEnabled ? '收集中' : '未启用' }}
                  </el-tag>
                </div>
              </div>
            </template>

            <el-form label-position="top">
              <el-form-item>
                <el-row justify="space-between" align="middle">
                  <span class="switch-label">启用数据收集</span>
                  <el-switch
                    v-model="dataCollectionEnabled"
                    inline-prompt
                    active-text="启用"
                    inactive-text="禁用"
                    @change="handleDataCollectionChange"
                    :disabled="!managementEnabled"
                    active-color="var(--success-color)"
                  />
                </el-row>
              </el-form-item>

              <el-form-item label="收集规则类型">
                <el-select 
                  v-model="collectionRuleType" 
                  placeholder="选择收集规则类型" 
                  style="width: 100%"
                  :disabled="!dataCollectionEnabled">
                  <el-option label="全消息收集" value="all" />
                  <el-option label="关键词过滤" value="keyword" />
                  <el-option label="用户过滤" value="user" />
                  <el-option label="模板提取" value="template" />
                </el-select>
              </el-form-item>

              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="showTemplateDialog" 
                  style="width: 100%"
                  :disabled="!dataCollectionEnabled"
                  class="action-button">
                  <el-icon><Edit /></el-icon>
                  配置收集规则
                </el-button>
              </el-form-item>

              <el-form-item>
                <el-button 
                  type="success" 
                  @click="exportCollectedData" 
                  :disabled="!hasCollectedData" 
                  style="width: 100%"
                  class="action-button">
                  <el-icon><Download /></el-icon>
                  导出收集数据
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <!-- 舆情监控配置 -->
        <el-col :span="12">
          <el-card shadow="hover" class="feature-card" :class="{ 'disabled-card': !managementEnabled }">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <el-icon class="feature-icon monitoring"><Monitor /></el-icon>
                  <span>舆情监控配置</span>
                </div>
                <div class="header-status">
                  <el-tag :type="monitoringEnabled ? 'success' : 'info'" effect="light" size="small">
                    {{ monitoringEnabled ? '监控中' : '未启用' }}
                  </el-tag>
                </div>
              </div>
            </template>

            <el-form label-position="top">
              <el-form-item>
                <el-row justify="space-between" align="middle">
                  <span class="switch-label">启用舆情监控</span>
                  <el-switch
                    v-model="monitoringEnabled"
                    @change="handleMonitoringChange"
                    inline-prompt
                    active-text="启用"
                    inactive-text="禁用"
                    :disabled="!managementEnabled"
                    active-color="var(--success-color)"
                  />
                </el-row>
              </el-form-item>

              <el-form-item label="敏感词管理">
                <div class="sensitive-word-header">
                  <span>敏感词列表</span>
                  <el-tooltip content="添加需要监控的敏感词汇" placement="top">
                    <el-icon><InfoFilled /></el-icon>
                  </el-tooltip>
                </div>
                
                <el-row :gutter="12" style="margin-bottom: 15px;">
                  <el-col :span="18">
                    <el-input
                      v-model="newSensitiveWord"
                      placeholder="输入敏感词"
                      clearable
                      @keyup.enter="addSensitiveWord"
                      :disabled="!monitoringEnabled"
                      size="small">
                      <template #prefix>
                        <el-icon><Key /></el-icon>
                      </template>
                    </el-input>
                  </el-col>
                  <el-col :span="6">
                    <el-button 
                      type="primary" 
                      @click="addSensitiveWord" 
                      :disabled="!newSensitiveWord.trim() || !monitoringEnabled" 
                      style="width: 100%"
                      size="small">
                      <el-icon><Plus /></el-icon>
                      添加
                    </el-button>
                  </el-col>
                </el-row>

                <div class="sensitive-words-list">
                  <el-tag
                    v-for="(word, index) in sensitiveWordsList"
                    :key="index"
                    closable
                    @close="removeSensitiveWord(index)"
                    type="danger"
                    effect="plain"
                    size="small"
                    :disabled="!monitoringEnabled"
                    class="sensitive-word-tag">
                    {{ word }}
                  </el-tag>
                  <el-empty 
                    v-if="sensitiveWordsList.length === 0" 
                    description="暂无敏感词" 
                    :image-size="60" 
                    class="empty-state" />
                </div>
                
                <div class="word-count" v-if="sensitiveWordsList.length > 0">
                  已添加 {{ sensitiveWordsList.length }} 个敏感词
                </div>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>

      <!-- 数据展示区域 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <el-card shadow="hover" class="data-display-card">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <el-icon class="feature-icon"><DataAnalysis /></el-icon>
                  <span>实时数据展示</span>
                </div>
                <div class="header-actions">
                  <el-badge :value="collectedData.length" type="primary" class="data-badge" />
                  <el-button 
                    type="primary" 
                    link 
                    @click="refreshData" 
                    :loading="dataLoading"
                    class="refresh-btn">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </div>
            </template>

            <el-table 
              :data="currentPageData" 
              style="width: 100%" 
              border 
              v-loading="dataLoading" 
              stripe 
              max-height="400"
              class="data-table"
              @row-click="viewMessageDetail">
              <el-table-column prop="time" label="时间" width="160" sortable>
                <template #default="{ row }">
                  <div class="time-cell">
                    <el-icon><Clock /></el-icon>
                    {{ row.time }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="sender" label="发送者" width="120">
                <template #default="{ row }">
                  <div class="sender-cell">
                    <el-avatar :size="24" :src="getAvatarUrl(row.sender)" />
                    <span>{{ row.sender }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="content" label="消息内容" min-width="200">
                <template #default="{ row }">
                  <div class="content-cell" :class="getContentClass(row.type)">
                    <el-icon v-if="row.type !== '文本'" class="content-icon">
                      <component :is="getMessageIcon(row.type)" />
                    </el-icon>
                    {{ row.content }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="type" label="类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="getMessageTypeTag(row.type)" size="small" effect="light">
                    {{ row.type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="{ row }">
                  <el-button 
                    type="primary" 
                    link 
                    @click.stop="viewMessageDetail(row)"
                    class="detail-btn">
                    详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="table-footer" v-if="collectedData.length > 0">
              <el-pagination
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
                :current-page="currentPage"
                :page-sizes="[5, 10, 20, 50]"
                :page-size="pageSize"
                layout="total, sizes, prev, pager, next, jumper"
                :total="totalDataCount"
                small
                background
                class="pagination"
              />
            </div>

            <el-empty 
              v-if="!hasCollectedData && !dataLoading" 
              description="暂无收集数据" 
              :image-size="100"
              class="empty-state">
              <template #image>
                <el-icon><Document /></el-icon>
              </template>
              <el-button type="primary" @click="handleDataCollectionChange(true)" v-if="managementEnabled">
                启用数据收集
              </el-button>
            </el-empty>
          </el-card>
        </el-col>
      </el-row>

      <!-- 报表生成区域 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <el-card shadow="hover" class="report-card">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <el-icon class="feature-icon"><Document /></el-icon>
                  <span>智能报表生成</span>
                </div>
                <el-tag type="info" effect="plain" size="small">高级功能</el-tag>
              </div>
            </template>

            <el-form label-position="top">
              <el-form-item>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="报表类型">
                      <el-select v-model="reportType" placeholder="选择报表类型" style="width: 100%">
                        <el-option label="群活跃度报表" value="activity" />
                        <el-option label="消息统计报表" value="message" />
                        <el-option label="成员参与度报表" value="participation" />
                        <el-option label="舆情分析报表" value="sentiment" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="时间范围">
                      <el-date-picker
                        v-model="reportDateRange"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                        style="width: 100%"
                        :disabled-date="disabledDate"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-form-item>

              <el-form-item>
                <el-row :gutter="12">
                  <el-col :span="12">
                    <el-button 
                      type="primary" 
                      @click="generateReport" 
                      :disabled="!reportType || !reportDateRange" 
                      style="width: 100%"
                      :loading="reportGenerating"
                      class="action-button">
                      <el-icon><View /></el-icon> 
                      生成报表
                    </el-button>
                  </el-col>
                  <el-col :span="12">
                    <el-button 
                      type="success" 
                      @click="exportReport" 
                      :disabled="!reportGenerated" 
                      style="width: 100%"
                      class="action-button">
                      <el-icon><Download /></el-icon> 
                      导出报表
                    </el-button>
                  </el-col>
                </el-row>
              </el-form-item>

              <el-form-item v-if="reportGenerated">
                <el-card shadow="never" class="report-preview">
                  <template #header>
                    <el-row justify="space-between" align="middle">
                      <h3 style="margin: 0">报表预览 - {{ getReportTypeName(reportType) }}</h3>
                      <el-text type="info">{{ reportDateRange[0] }} 至 {{ reportDateRange[1] }}</el-text>
                    </el-row>
                  </template>
                  <el-table :data="reportData" style="width: 100%" border class="report-table">
                    <el-table-column prop="category" label="类别" width="180" />
                    <el-table-column prop="value" label="数值" width="120" />
                    <el-table-column prop="description" label="描述" />
                    <el-table-column label="趋势" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getTrendType(row.trend)" size="small" effect="light">
                          <el-icon v-if="row.trend === '上升'"><Top /></el-icon>
                          <el-icon v-if="row.trend === '下降'"><Bottom /></el-icon>
                          <el-icon v-if="row.trend === '持平'"><Right /></el-icon>
                          {{ row.trend }}
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-card>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 收集模板对话框 -->
    <el-dialog
      v-model="templateDialogVisible"
      title="智能模板配置"
      width="60%"
      class="template-dialog"
      :close-on-click-modal="false">
      <el-form label-position="top">
        <el-form-item label="原始消息内容">
          <el-input
            v-model="originalMessage"
            type="textarea"
            :rows="4"
            placeholder="请输入原始消息示例，例如：‘我叫张三，电话13800138000，住在北京市朝阳区‘"
            show-word-limit
            maxlength="500"
          />
        </el-form-item>
        
        <el-form-item label="需要从中提取出来的内容">
          <el-input
            v-model="collectionTemplate"
            type="textarea"
            :rows="4"
            placeholder="请输入需要提取的内容，用逗号分隔，例如：张三，13800138000，北京市朝阳区"
            show-word-limit
            maxlength="200"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="autoLearnPattern" 
            :disabled="!originalMessage.trim() || !collectionTemplate.trim()"
            :loading="patternLearning"
            class="learn-button">
            <el-icon><MagicStick /></el-icon>
            智能学习模式
          </el-button>
          
          <el-button 
            type="info" 
            @click="showPatternHelp"
            link
            class="help-button">
            <el-icon><QuestionFilled /></el-icon>
            如何使用？
          </el-button>
        </el-form-item>
        
        <el-form-item v-if="generatedRegex" label="生成的正则表达式">
          <el-input
            v-model="generatedRegex"
            type="textarea"
            :rows="3"
            placeholder="生成的正则表达式将显示在这里，您可以手动编辑"
            class="regex-input"
          />
          <div class="regex-tips">
            <el-icon><InfoFilled /></el-icon>
            系统已自动学习并生成匹配规则，您可以根据需要进一步调整
          </div>
        </el-form-item>
        
        <el-form-item v-if="extractedValues && Object.keys(extractedValues).length > 0" label="提取结果预览">
          <el-card shadow="never">
            <el-descriptions :column="2" border>
              <el-descriptions-item 
                v-for="(value, key) in extractedValues" 
                :key="key" 
                :label="key">
                {{ value }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="templateDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="saveCollectionTemplate" 
            :disabled="!generatedRegex"
            class="save-button">
            保存模板
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 消息详情对话框 -->
    <el-dialog
      v-model="messageDetailVisible"
      title="消息详情"
      width="50%"
      class="message-dialog">
      <el-descriptions :column="1" border v-if="selectedMessage" class="message-details">
        <el-descriptions-item label="发送时间">
          <div class="detail-item">
            <el-icon><Clock /></el-icon>
            {{ selectedMessage.time }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="发送者">
          <div class="detail-item">
            <el-avatar :size="32" :src="getAvatarUrl(selectedMessage.sender)" />
            <span>{{ selectedMessage.sender }}</span>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="消息类型">
          <el-tag :type="getMessageTypeTag(selectedMessage.type)" size="small">
            {{ selectedMessage.type }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="消息内容">
          <div class="detail-content">{{ selectedMessage.content }}</div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="messageDetailVisible = false">关闭</el-button>
          <el-button type="primary" @click="analyzeMessage(selectedMessage)" v-if="selectedMessage">
            深度分析
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 操作反馈提示 -->
    <el-notification
      v-if="showNotification"
      :title="notificationTitle"
      :message="notificationMessage"
      :type="notificationType"
      @close="showNotification = false"
    />
  </div>
</template>

<script setup>
import { ElMessage, ElNotification } from 'element-plus'
import { ref, computed, onMounted, watch } from 'vue'
import { 
  View, Setting, Edit, Plus, Key, Download, Refresh, Clock,
  Collection, Monitor, DataAnalysis, Document, Search,
  QuestionFilled, InfoFilled, MagicStick, Top, Bottom, Right,
  Picture, Message, Microphone, VideoCamera
} from '@element-plus/icons-vue'

// ===== 响应式数据 =====
const selectedGroup = ref('')
const managementEnabled = ref(false)
const managementLoading = ref(false)
const dataCollectionEnabled = ref(false)
const collectionRuleType = ref('all')
const collectedData = ref([
  { 
    time: '2023-06-01 10:30:25', 
    sender: '张三', 
    content: '大家好，今天天气不错，适合户外活动', 
    type: '文本',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=zhangsan'
  },
  { 
    time: '2023-06-01 10:32:15', 
    sender: '李四', 
    content: '风景照片.jpg', 
    type: '图片', 
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=lisi'
  },
  { 
    time: '2023-06-01 10:35:42', 
    sender: '王五', 
    content: '明天上午9点有重要会议，请大家准时参加', 
    type: '文本',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=wangwu'
  },
  { 
    time: '2023-06-01 11:15:30', 
    sender: '赵六', 
    content: '收到，我会准时参加并准备好相关资料', 
    type: '文本',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=zhaoliu'
  },
  { 
    time: '2023-06-01 11:20:45', 
    sender: '钱七', 
    content: '会议议程.docx', 
    type: '文件',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=qianqi'
  }
])
const hasCollectedData = ref(true)
const dataLoading = ref(false)
const newSensitiveWord = ref('')
const sensitiveWordsList = ref(['会议', '机密', '内部', '紧急', '重要'])
const monitoringEnabled = ref(false)
const monitoringResults = ref([
  { time: '2023-06-01 10:35:42', sender: '王五', content: '明天有会议吗？', matchedWords: '会议' }
])
const templateDialogVisible = ref(false)
const collectionTemplate = ref('')
const originalMessage = ref('')
const generatedRegex = ref('')
const extractedValues = ref({})
const patternLearning = ref(false)
const reportType = ref('')
const reportDateRange = ref([])
const reportGenerated = ref(false)
const reportGenerating = ref(false)
const reportData = ref([
  { category: '活跃成员数', value: '25', description: '近7天内活跃的群成员数量', trend: '上升' },
  { category: '消息总数', value: '342', description: '近7天内群消息总数', trend: '上升' },
  { category: '图片消息', value: '87', description: '近7天内图片消息数量', trend: '持平' },
  { category: '文件分享', value: '23', description: '近7天内文件分享数量', trend: '下降' }
])
const messageDetailVisible = ref(false)
const selectedMessage = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const totalDataCount = ref(collectedData.value.length)

// 通知系统
const showNotification = ref(false)
const notificationTitle = ref('')
const notificationMessage = ref('')
const notificationType = ref('success')

// ===== 计算属性 =====
const currentPageData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return collectedData.value.slice(start, end)
})

// ===== 事件处理函数 =====
const handleClearGroup = () => {
  selectedGroup.value = ''
  managementEnabled.value = false
  dataCollectionEnabled.value = false
  monitoringEnabled.value = false
  hasCollectedData.value = false
  showNotificationMessage('info', '操作提示', '已清除群聊选择')
}

const handleManagementChange = async (value) => {
  if (!selectedGroup.value) {
    showNotificationMessage('warning', '操作提示', '请先选择群聊')
    managementEnabled.value = false
    return
  }
  
  managementLoading.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 800))
    
    if (value) {
      showNotificationMessage('success', '操作成功', `开始管理群聊 ${selectedGroup.value}`)
      await refreshData()
    } else {
      showNotificationMessage('info', '操作提示', `停止管理群聊 ${selectedGroup.value}`)
      dataCollectionEnabled.value = false
      monitoringEnabled.value = false
    }
  } catch (error) {
    showNotificationMessage('error', '操作失败', '群聊管理操作失败，请重试')
    managementEnabled.value = !value
  } finally {
    managementLoading.value = false
  }
}

const handleDataCollectionChange = async (value) => {
  if (value && !managementEnabled.value) {
    showNotificationMessage('warning', '操作提示', '请先启用群聊管理')
    dataCollectionEnabled.value = false
    return
  }
  
  showNotificationMessage('success', '操作成功', `数据收集已${value ? '开启' : '关闭'}`)
  
  if (value) {
    await refreshData()
  }
}

const handleMonitoringChange = (value) => {
  if (value && sensitiveWordsList.value.length === 0) {
    showNotificationMessage('warning', '操作提示', '请先添加敏感词')
    monitoringEnabled.value = false
    return
  }
  
  showNotificationMessage('success', '操作成功', `舆情监控已${value ? '开启' : '关闭'}`)
  
  if (value) {
    monitoringResults.value = []
    startMonitoring()
  }
}

const refreshData = async () => {
  dataLoading.value = true
  
  try {
    // 模拟数据加载
    await new Promise(resolve => setTimeout(resolve, 1200))
    hasCollectedData.value = collectedData.value.length > 0
    showNotificationMessage('success', '数据更新', '数据已刷新完成')
  } catch (error) {
    showNotificationMessage('error', '数据刷新失败', '请检查网络连接后重试')
  } finally {
    dataLoading.value = false
  }
}

const viewMessageDetail = (message) => {
  selectedMessage.value = message
  messageDetailVisible.value = true
}

const analyzeMessage = (message) => {
  showNotificationMessage('info', '深度分析', `正在分析消息: ${message.content.substring(0, 30)}...`)
  // 这里可以添加消息深度分析的逻辑
}

const showTemplateDialog = () => {
  templateDialogVisible.value = true
  // 重置对话框状态
  collectionTemplate.value = ''
  originalMessage.value = ''
  generatedRegex.value = ''
  extractedValues.value = {}
}

const saveCollectionTemplate = () => {
  if (!collectionTemplate.value.trim()) {
    showNotificationMessage('warning', '保存失败', '请输入收集模板')
    return
  }
  
  if (!generatedRegex.value.trim()) {
    showNotificationMessage('warning', '保存失败', '请先生成正则表达式')
    return
  }
  
  showNotificationMessage('success', '保存成功', '模板保存成功')
  templateDialogVisible.value = false
}

const autoLearnPattern = async () => {
  if (!originalMessage.value.trim()) {
    showNotificationMessage('warning', '学习失败', '请输入原始消息示例')
    return
  }
  
  if (!collectionTemplate.value.trim()) {
    showNotificationMessage('warning', '学习失败', '请输入要收集的数据')
    return
  }
  
  patternLearning.value = true
  
  try {
    // 模拟AI学习过程
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    const fields = collectionTemplate.value.split(',').map(field => field.trim())
    const message = originalMessage.value
    const extracted = {}
    
    // 智能提取逻辑
    if (fields.includes('姓名') || fields.includes('名字')) {
      const nameMatch = message.match(/我叫([^\s，,]+)/) || message.match(/姓名[:：]?\s*([^\s，,]+)/)
      if (nameMatch) extracted['姓名'] = nameMatch[1]
    }
    
    if (fields.includes('电话') || fields.includes('手机')) {
      const phoneMatch = message.match(/(1[3-9]\d{9})/) || message.match(/电话[:：]?\s*(\d+)/)
      if (phoneMatch) extracted['电话'] = phoneMatch[1]
    }
    
    if (fields.includes('地址')) {
      const addressMatch = message.match(/住在([^\s，,]+)/) || message.match(/地址[:：]?\s*([^\s，,]+)/)
      if (addressMatch) extracted['地址'] = addressMatch[1]
    }
    
    // 通用提取逻辑
    if (Object.keys(extracted).length === 0) {
      const parts = message.split(/[，,]/).map(part => part.trim())
      fields.forEach((field, index) => {
        if (index < parts.length) {
          extracted[field] = parts[index].replace(new RegExp(`^${field}[：: ]*`), '')
        }
      })
    }
    
    // 生成正则表达式
    let regexPattern = ''
    if (Object.keys(extracted).length > 0) {
      const patterns = []
      
      Object.keys(extracted).forEach(field => {
        const value = extracted[field]
        if (/^\d+$/.test(value)) {
          patterns.push(`${field}[:：]?\\s*(\\d+)`)
        } else if (/^[\u4e00-\u9fa5]+$/.test(value)) {
          patterns.push(`${field}[:：]?\\s*([\\u4e00-\\u9fa5]+)`)
        } else {
          patterns.push(`${field}[:：]?\\s*([^\\s，,]+)`)
        }
      })
      
      regexPattern = patterns.join('\\s*[，,]\\s*')
    } else {
      regexPattern = '(.+)'
    }
    
    generatedRegex.value = regexPattern
    extractedValues.value = extracted
    showNotificationMessage('success', '学习成功', '正则表达式生成成功')
  } catch (error) {
    showNotificationMessage('error', '学习失败', '智能学习过程中出现错误')
  } finally {
    patternLearning.value = false
  }
}

const showPatternHelp = () => {
  ElMessage.info({
    message: '智能学习模式使用说明：\n1. 输入原始消息示例\n2. 输入需要提取的字段（用逗号分隔）\n3. 系统会自动学习并生成匹配规则',
    duration: 8000
  })
}

const exportCollectedData = () => {
  if (!hasCollectedData.value) {
    showNotificationMessage('warning', '导出失败', '没有可导出的数据')
    return
  }
  
  // 模拟导出过程
  const exportLoading = ElMessage.loading('正在导出数据...', 0)
  
  setTimeout(() => {
    exportLoading.close()
    showNotificationMessage('success', '导出成功', '数据导出完成，共导出' + collectedData.value.length + '条记录')
  }, 2000)
}

const generateReport = async () => {
  if (!reportType.value) {
    showNotificationMessage('warning', '生成失败', '请选择报表类型')
    return
  }
  
  if (!reportDateRange.value || reportDateRange.value.length !== 2) {
    showNotificationMessage('warning', '生成失败', '请选择时间范围')
    return
  }
  
  reportGenerating.value = true
  
  try {
    // 模拟报表生成
    await new Promise(resolve => setTimeout(resolve, 1800))
    reportGenerated.value = true
    showNotificationMessage('success', '报表生成', `${getReportTypeName(reportType.value)}生成成功`)
  } catch (error) {
    showNotificationMessage('error', '生成失败', '报表生成过程中出现错误')
  } finally {
    reportGenerating.value = false
  }
}

const exportReport = () => {
  if (!reportGenerated.value) {
    showNotificationMessage('warning', '导出失败', '请先生成报表')
    return
  }
  
  // 模拟报表导出
  const exportLoading = ElMessage.loading('正在导出报表...', 0)
  
  setTimeout(() => {
    exportLoading.close()
    showNotificationMessage('success', '导出成功', '报表导出完成')
  }, 1500)
}

const handleSizeChange = (val) => {
  pageSize.value = val
  refreshData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

const showGroupSelector = () => {
  ElMessage.info('群聊选择功能开发中...')
}

const disabledDate = (time) => {
  return time.getTime() > Date.now()
}

const startMonitoring = () => {
  // 模拟实时监控
  setInterval(() => {
    if (monitoringEnabled.value && Math.random() > 0.7) {
      const mockMessages = [
        '明天有个重要会议',
        '这是内部机密信息',
        '紧急通知：请大家注意',
        '这个项目很关键'
      ]
      const mockSenders = ['张三', '李四', '王五', '赵六']
      
      const newResult = {
        time: new Date().toLocaleString(),
        sender: mockSenders[Math.floor(Math.random() * mockSenders.length)],
        content: mockMessages[Math.floor(Math.random() * mockMessages.length)],
        matchedWords: '重要'
      }
      
      monitoringResults.value.unshift(newResult)
      
      if (monitoringResults.value.length > 50) {
        monitoringResults.value.pop()
      }
    }
  }, 5000)
}

// ===== 辅助函数 =====
const showNotificationMessage = (type, title, message) => {
  notificationType.value = type
  notificationTitle.value = title
  notificationMessage.value = message
  showNotification.value = true
  
  setTimeout(() => {
    showNotification.value = false
  }, 3000)
}

const getMessageTypeTag = (type) => {
  const typeMap = {
    '文本': '',
    '图片': 'success',
    '文件': 'warning',
    '语音': 'info',
    '视频': 'danger'
  }
  return typeMap[type] || ''
}

const getContentClass = (type) => {
  const classMap = {
    '文本': 'text-content',
    '图片': 'image-content',
    '文件': 'file-content',
    '语音': 'audio-content',
    '视频': 'video-content'
  }
  return classMap[type] || 'text-content'
}

const getMessageIcon = (type) => {
  const iconMap = {
    '文本': Message,
    '图片': Picture,
    '文件': Document,
    '语音': Microphone,
    '视频': VideoCamera
  }
  return iconMap[type] || Message
}

const getAvatarUrl = (sender) => {
  const avatarMap = {
    '张三': 'https://api.dicebear.com/7.x/avataaars/svg?seed=zhangsan',
    '李四': 'https://api.dicebear.com/7.x/avataaars/svg?seed=lisi',
    '王五': 'https://api.dicebear.com/7.x/avataaars/svg?seed=wangwu',
    '赵六': 'https://api.dicebear.com/7.x/avataaars/svg?seed=zhaoliu',
    '钱七': 'https://api.dicebear.com/7.x/avataaars/svg?seed=qianqi'
  }
  return avatarMap[sender] || 'https://api.dicebear.com/7.x/avataaars/svg?seed=unknown'
}

const getReportTypeName = (type) => {
  const typeMap = {
    'activity': '群活跃度报表',
    'message': '消息统计报表',
    'participation': '成员参与度报表',
    'sentiment': '舆情分析报表'
  }
  return typeMap[type] || type
}

const getTrendType = (trend) => {
  const trendMap = {
    '上升': 'success',
    '下降': 'danger',
    '持平': 'info'
  }
  return trendMap[trend] || ''
}

// 敏感词管理功能
const addSensitiveWord = () => {
  if (!newSensitiveWord.value.trim()) {
    showNotificationMessage('warning', '添加失败', '请输入敏感词')
    return
  }
  
  if (sensitiveWordsList.value.includes(newSensitiveWord.value.trim())) {
    showNotificationMessage('warning', '添加失败', '该敏感词已存在')
    return
  }
  
  sensitiveWordsList.value.push(newSensitiveWord.value.trim())
  newSensitiveWord.value = ''
  showNotificationMessage('success', '添加成功', '敏感词添加成功')
}

const removeSensitiveWord = (index) => {
  sensitiveWordsList.value.splice(index, 1)
  showNotificationMessage('info', '删除成功', '敏感词已删除')
}

// ===== 生命周期钩子 =====
onMounted(() => {
  // 初始化操作
  console.log('群组管理视图已加载')
})

// 监听数据变化
watch(managementEnabled, (newVal) => {
  if (newVal) {
    console.log('群聊管理已启用:', selectedGroup.value)
  }
})

watch([dataCollectionEnabled, monitoringEnabled], ([dataEnabled, monitorEnabled]) => {
  if (dataEnabled || monitorEnabled) {
    console.log('功能状态变化 - 数据收集:', dataEnabled, '舆情监控:', monitorEnabled)
  }
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

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}


.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background-color: white;
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 10;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 18px;
  color: var(--primary-color);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}


.page-header-section {
  margin-bottom: 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  padding: 32px 0;
  color: white;
}

.page-header {
  text-align: center;
  padding: 1rem 0;
}

.page-header h1 {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
}

.page-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  max-width: 700px;
  margin: 0 auto;
}


.main-content {
  padding: 0;
  max-width: 100vw;
  margin: 0 auto;
}


.top-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 0px;
}

.config-card {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.config-card-inner {
  flex: 1;
  display: flex;
  flex-direction: column;
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


.el-row {
  margin-bottom: 20px;
}


.status-controls {
  display: flex;
  align-items: center;
}

/* 水平布局样式 */
.controls-row {
  display: flex;
  align-items: flex-start;
  gap: 0px;
  margin-bottom: 0px;
  flex-wrap: wrap;
}

.inline-form-item {
  display: flex;
  align-items: center;
  margin-bottom: 0;
  flex: 1;
  min-width: 0px;
  padding: 0 2px;
}

.inline-form-item .el-select {
  width: 100%;
  min-width: 0px;
}

.inline-form-item .el-form-item__label {
  margin-right: 4px;
  min-width: 0px;
  line-height: 32px;
  white-space: nowrap;
}

.inline-status {
  display: flex;
  align-items: center;
  gap: 0px;
}


.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  margin: 16px 0;
}

.stat-item {
  padding: 16px;
  border-radius: 12px;
  background-color: white;
  box-shadow: var(--shadow);
  text-align: center;
  transition: var(--transition);
  border: 1px solid var(--border-color);
}

.stat-item:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}


.chart-card {
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border-color);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-actions {
  display: flex;
  gap: 8px;
}

.chart-select {
  width: 100px;
}


.el-table .el-button {
  margin: 0 4px;
  padding: 4px 8px;
  font-size: 12px;
}


.custom-input .el-input__wrapper {
  border-radius: 8px;
  border: 1px solid var(--border-color);
  transition: var(--transition);
}

.custom-input .el-input__wrapper:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}


.custom-select .el-input__wrapper {
  border-radius: 8px;
  border: 1px solid var(--border-color);
}



.el-button {
  transition: all 0.2s ease;
  padding: 0 16px;
  min-width: 80px;
}

.el-button--primary {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  padding: 0 20px;
}

.el-button--primary:hover {
  background-color: #1e3a8a;
  border-color: #1e3a8a;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(30, 64, 175, 0.2);
}

/* 渐变按钮样式 */
.gradient-btn {
  position: relative;
  overflow: hidden;
  z-index: 1;
  padding: 0 20px !important;
}

.gradient-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  z-index: -1;
  transition: all 0.3s ease;
}

.gradient-btn:hover::before {
  transform: scale(1.05);
}

.gradient-btn span {
  position: relative;
  z-index: 1;
}

.operation-buttons {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.operation-buttons .el-button {
  padding: 4px 8px;
  font-size: 12px;
}

.delete-btn {
  background-color: #fee2e2;
  border-color: #fecaca;
  color: #dc2626;
  transition: all 0.2s ease;
}

.delete-btn:hover {
  background-color: #fecaca;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.2);
}


.el-card {
  border-radius: 8px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  overflow: hidden;
  background-color: white;
  margin-bottom: 24px;
}

.el-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  border-color: var(--primary-light);
}






.el-form-item {
  margin-bottom: 24px;
}

.el-form-item__description {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
  line-height: 1.4;
}

.status-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-toggle .el-form-item__content {
  flex: 1;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
  padding: 5px 0;
}


.el-table {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
}

.el-table th {
  background-color: rgba(30, 64, 175, 0.05);
  font-weight: 600;
  color: var(--text-primary);
  padding: 12px 0;
}

.el-table td {
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.el-table tr:last-child td {
  border-bottom: none;
}

.el-table--enable-row-hover .el-table__body tr:hover>td {
  background-color: var(--light-color);
}


.el-tag--info {
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--secondary-color);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 6px;
}

.el-tag--success {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 6px;
}

/* 优化状态标签样式 */
.status-tag {
  font-size: 12px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid transparent;
}

/* 已回复状态 - 绿色系 */
.el-tag--success.status-tag {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
  color: var(--success-color);
  border-color: rgba(16, 185, 129, 0.3);
}

.el-tag--success.status-tag:hover {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%);
  box-shadow: 0 2px 6px rgba(16, 185, 129, 0.2);
  transform: translateY(-1px);
}

/* 未回复状态 - 红色系 */
.el-tag--danger.status-tag {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
  color: var(--danger-color);
  border-color: rgba(239, 68, 68, 0.3);
}

.el-tag--danger.status-tag:hover {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%);
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.2);
  transform: translateY(-1px);
}

/* 被阻止状态 - 橙色系 */
.el-tag--warning.status-tag {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
  color: var(--warning-color);
  border-color: rgba(245, 158, 11, 0.3);
}

.el-tag--warning.status-tag:hover {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.2) 100%);
  box-shadow: 0 2px 6px rgba(245, 158, 11, 0.2);
  transform: translateY(-1px);
}


.custom-pagination {
  padding: 16px 0;
  display: flex;
  justify-content: flex-end;
}


.custom-rules-container {
  border: 0;
  border-radius: 12px;
  padding: 0;
  background-color: white;
}

.rule-actions {
  margin-bottom: 16px;
}

.rules-table {
  margin-top: 15px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow);
}


@media (max-width: 1024px) {
  .top-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-header h1 {
    font-size: 1.8rem;
  }

  .logo span {
    display: none;
  }
}

/* 消息详情对话框样式 */
.message-detail-dialog .el-message-box {
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  border: 2px solid var(--border-color);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.message-detail-dialog .el-message-box__header {
  padding: 20px 24px 16px;
  border-bottom: 2px solid var(--border-color);
}

.message-detail-dialog .el-message-box__title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.message-detail-dialog .el-message-box__content {
  padding: 0 24px 20px;
}

.message-detail-container {
  padding: 8px 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--border-color);
}

.time-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  background: var(--light-color);
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  letter-spacing: -0.01em;
}

.time-badge .el-icon {
  font-size: 14px;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.status-replied {
  background: rgba(16, 185, 129, 0.12);
  color: var(--success-color);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-pending {
  background: rgba(245, 158, 11, 0.12);
  color: var(--warning-color);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.message-content {
  margin-bottom: 24px;
}

.message-section {
  margin-bottom: 20px;
}

.message-section:last-child {
  margin-bottom: 0;
}

.message-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  letter-spacing: -0.01em;
}

.message-label .el-icon {
  font-size: 16px;
  color: var(--primary-color);
}

.message-bubble {
  padding: 16px 20px;
  border-radius: 14px;
  line-height: 1.6;
  word-break: break-word;
  box-shadow: var(--shadow-sm);
  border: 1px solid transparent;
  font-size: 15px;
  letter-spacing: -0.01em;
}

.user-message {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border-color: rgba(59, 130, 246, 0.3);
  font-weight: 500;
}

.ai-message {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  color: var(--text-primary);
  border-color: var(--border-color);
  font-weight: 400;
}

.no-reply {
  color: var(--text-secondary);
  font-style: italic;
  font-size: 14px;
  font-weight: 400;
}

.detail-footer {
  padding-top: 20px;
  border-top: 2px solid var(--border-color);
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 10px;
  font-weight: 400;
  letter-spacing: -0.01em;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item .el-icon {
  font-size: 14px;
  color: var(--primary-color);
}

/* 对话框按钮样式 */
.message-detail-dialog .el-message-box__btns {
  padding: 16px 24px 20px;
  border-top: 1px solid var(--border-color);
}

.message-detail-dialog .el-button {
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 500;
  letter-spacing: -0.01em;
}

.message-detail-dialog .el-button--primary {
  background: var(--primary-color);
  border-color: var(--primary-color);
  font-weight: 600;
}

/* 添加回复规则对话框样式 */
.add-rule-dialog .el-dialog {
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  border: 2px solid var(--border-color);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.add-rule-dialog .el-dialog__header {
  padding: 20px 24px 16px;
  border-bottom: 2px solid var(--border-color);
  margin: 0;
}

.add-rule-dialog .el-dialog__title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.add-rule-dialog .el-dialog__headerbtn {
  top: 20px;
  right: 24px;
}

.add-rule-dialog .el-dialog__body {
  padding: 24px;
}

.add-rule-dialog .el-form-item {
  margin-bottom: 20px;
}

.add-rule-dialog .el-form-item__label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: -0.01em;
}

.add-rule-dialog .el-select,
.add-rule-dialog .el-input,
.add-rule-dialog .el-textarea {
  font-size: 15px;
  letter-spacing: -0.01em;
}

.add-rule-dialog .el-input__wrapper,
.add-rule-dialog .el-textarea__inner {
  border-radius: 10px;
  border: 1px solid var(--border-color);
  padding: 12px 16px;
  transition: all 0.2s ease;
}

.add-rule-dialog .el-input__wrapper:focus-within,
.add-rule-dialog .el-textarea__inner:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.add-rule-dialog .el-dialog__footer {
  padding: 16px 24px 20px;
  border-top: 1px solid var(--border-color);
}

.add-rule-dialog .el-button {
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 500;
  letter-spacing: -0.01em;
  font-size: 14px;
}

.add-rule-dialog .el-button--primary {
  background: var(--primary-color);
  border-color: var(--primary-color);
  font-weight: 600;
}

/* 响应式调整 */
@media (max-width: 600px) {
  .message-detail-dialog .el-message-box {
    width: 90vw !important;
    max-width: 400px;
  }

  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .message-bubble {
    padding: 10px 14px;
    font-size: 14px;
  }

  .add-rule-dialog .el-dialog {
    width: 90vw !important;
    max-width: 400px;
    margin: 20px auto;
  }

  .add-rule-dialog .el-dialog__body {
    padding: 16px;
  }

  .add-rule-dialog .el-form-item {
    margin-bottom: 16px;
  }
}
</style>