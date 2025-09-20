<template>
  <div class="app-container">
    <div class="main-content">
      <!-- 群聊选择区域 -->
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card shadow="hover">
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
                  <el-col :span="20">
                    <el-input
                      v-model="selectedGroup"
                      placeholder="输入群聊名称或选择已有群聊"
                      clearable
                      @clear="handleClearGroup"
                      size="large">
                      <template #prefix>
                        <el-icon><View /></el-icon>
                      </template>
                    </el-input>
                  </el-col>
                  <el-col :span="4">
                    <el-switch
                      v-model="managementEnabled"
                      @change="handleManagementChange"
                      :disabled="!selectedGroup"
                      :loading="managementLoading"
                      active-color="var(--success-color)"
                      style="width: 100%"
                    />
                  </el-col>
                </el-row>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>

      <!-- 数据收集配置 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <el-icon class="feature-icon data-collection"><Collection /></el-icon>
                  <span>数据收集配置</span>
                </div>
              </div>
            </template>

            <el-form label-position="top">
              <el-form-item>
                <el-row justify="space-between" align="middle">
                  <span class="switch-label">启用数据收集</span>
                  <el-switch
                    v-model="dataCollectionEnabled"
                    @change="handleDataCollectionChange"
                    active-color="var(--success-color)"
                  />
                </el-row>
              </el-form-item>

              <el-form-item label="收集规则">
                <div class="rule-actions">
                  <el-button type="primary" size="small" @click="showAddRuleDialog">
                    <el-icon><Plus /></el-icon>
                    添加规则
                  </el-button>
                  <el-button size="small" @click="showRegexHelp">
                    <el-icon><QuestionFilled /></el-icon>
                    正则帮助
                  </el-button>
                </div>
                
                <!-- 正则规则表格 -->
                <el-table :data="regexRules" class="rules-table" empty-text="暂无规则，请添加">
                  <el-table-column prop="originalMessage" label="原始消息" width="250" />
                  <el-table-column prop="pattern" label="正则表达式" />
                  <el-table-column prop="extractedContent" label="提取内容" width="200" />
                  <el-table-column label="操作" width="120" align="center">
                    <template #default="scope">
                      <el-button type="danger" size="small" @click="deleteRegexRule(scope.$index)">
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>

      <!-- 舆情监控配置 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <el-card shadow="hover">
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
                      :disabled="!newSensitiveWord.trim()" 
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
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <el-icon class="feature-icon"><DataAnalysis /></el-icon>
                  <span>收集数据展示</span>
                </div>
                <div class="header-actions">
                  <el-select 
                    v-model="selectedGroupFilter" 
                    placeholder="筛选群聊" 
                    size="small" 
                    style="width: 120px; margin-right: 8px"
                    clearable>
                    <el-option label="所有群聊" value="" />
                    <el-option 
                      v-for="group in availableGroups" 
                      :key="group" 
                      :label="group" 
                      :value="group" />
                  </el-select>
                  <el-date-picker
                    v-model="dateRangeFilter"
                    type="daterange"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    size="small"
                    style="width: 240px; margin-right: 8px"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    clearable
                  />
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
              <el-table-column prop="type" label="提取内容" width="100">
                <template #default="{ row }">
                  <el-tag :type="getMessageTypeTag(row.type)" size="small" effect="light">
                    {{ row.type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button 
                    type="primary" 
                    link 
                    @click.stop="viewMessageDetail(row)"
                    class="detail-btn">
                    详情
                  </el-button>
                  <el-button 
                    type="danger" 
                    link 
                    @click.stop="deleteRule(row)"
                    class="delete-btn">
                    删除
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
    </div>

    <!-- 收集模板对话框 -->
    <el-dialog
      v-model="templateDialogVisible"
      title="智能模板配置"
      width="60%"
      :close-on-click-modal="false">
      <el-form label-position="top">
        <el-form-item label="原始消息内容">
          <el-input
            v-model="originalMessage"
            type="textarea"
            :rows="4"
            placeholder="请输入原始消息示例，例如：'我叫张三，电话13800138000，住在北京市朝阳区'"
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
      width="50%">
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
  </div>
</template>

<script setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, computed, onMounted, watch } from 'vue'
import { 
  View, Setting, Plus, Key, Refresh, Clock,
  Collection, Monitor, DataAnalysis, Document,
  QuestionFilled, InfoFilled, MagicStick, Picture, 
  Message, Microphone, VideoCamera, Delete
} from '@element-plus/icons-vue'

// ===== 响应式数据 =====
const selectedGroup = ref('')
const managementEnabled = ref(false)
const managementLoading = ref(false)
const dataCollectionEnabled = ref(false)
const regexRules = ref([
  { 
    originalMessage: '我叫张三，电话13800138000，住在北京市朝阳区', 
    pattern: '姓名[:：]?\\s*([^\\s，,]+)\\s*[，,]?\\s*电话[:：]?\\s*(1[3-9]\\d{9})', 
    extractedContent: '张三, 13800138000' 
  },
  { 
    originalMessage: '地址：北京市朝阳区建国门外大街1号', 
    pattern: '地址[:：]?\\s*([^\\s，,]+(?:省|市|区|县|镇|村|街道|路|号|室|单元))', 
    extractedContent: '北京市朝阳区建国门外大街1号' 
  },
  { 
    originalMessage: '会议：产品发布会 时间：2023-06-15 14:00', 
    pattern: '会议[:：]?\\s*([^\\s，,]+)\\s*时间[:：]?\\s*([^\\s，,]+)', 
    extractedContent: '产品发布会, 2023-06-15 14:00' 
  }
])
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
const messageDetailVisible = ref(false)
const selectedMessage = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)

// 新增筛选相关变量
const selectedGroupFilter = ref('')
const dateRangeFilter = ref([])
const availableGroups = ref(['技术交流群', '产品讨论组', '运营团队', '客服中心', '测试群组'])

// ===== 计算属性 =====
const filteredData = computed(() => {
  // 确保collectedData是数组
  if (!Array.isArray(collectedData.value)) {
    console.warn('collectedData不是数组', collectedData.value)
    return []
  }
  
  let filtered = [...collectedData.value]
  
  // 群聊筛选
  if (selectedGroupFilter.value) {
    filtered = filtered.filter(item => {
      if (!item || !item.sender) return false
      return item.sender.includes(selectedGroupFilter.value)
    })
  }
  
  // 日期范围筛选
  if (dateRangeFilter.value && Array.isArray(dateRangeFilter.value) && dateRangeFilter.value.length === 2) {
    const [startDate, endDate] = dateRangeFilter.value
    if (startDate && endDate) {
      filtered = filtered.filter(item => {
        if (!item || !item.time) return false
        const itemDate = item.time.split(' ')[0] // 提取日期部分
        return itemDate >= startDate && itemDate <= endDate
      })
    }
  }
  
  return filtered
})

const currentPageData = computed(() => {
  // 确保filteredData是数组
  if (!Array.isArray(filteredData.value)) {
    return []
  }
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

const totalDataCount = computed(() => {
  // 确保filteredData是数组
  if (!Array.isArray(filteredData.value)) {
    return 0
  }
  
  return filteredData.value.length
})

// ===== 事件处理函数 =====
const handleClearGroup = () => {
  selectedGroup.value = ''
  managementEnabled.value = false
  dataCollectionEnabled.value = false
  monitoringEnabled.value = false
  hasCollectedData.value = false
  ElMessage.info('已清除群聊选择')
}

const handleManagementChange = async (value) => {
  if (!selectedGroup.value) {
    ElMessage.warning('请先选择群聊')
    managementEnabled.value = false
    return
  }
  
  managementLoading.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 800))
    
    if (value) {
      ElMessage.success(`开始管理群聊 ${selectedGroup.value}`)
      await refreshData()
    } else {
      ElMessage.info(`停止管理群聊 ${selectedGroup.value}`)
      dataCollectionEnabled.value = false
      monitoringEnabled.value = false
    }
  } catch (error) {
    console.error('群聊管理操作失败:', error)
    ElMessage.error('群聊管理操作失败，请重试')
    managementEnabled.value = !value // 恢复原始状态
  } finally {
    managementLoading.value = false
  }
}

const handleDataCollectionChange = async (value) => {
  if (value && !managementEnabled.value) {
    ElMessage.warning('请先启用群聊管理')
    dataCollectionEnabled.value = false
    return
  }
  
  ElMessage.success(`数据收集已${value ? '开启' : '关闭'}`)
  
  if (value) {
    await refreshData()
  }
}

const handleMonitoringChange = (value) => {
  if (value && sensitiveWordsList.value.length === 0) {
    ElMessage.warning('请先添加敏感词')
    monitoringEnabled.value = false
    return
  }
  
  ElMessage.success(`舆情监控已${value ? '开启' : '关闭'}`)
  
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
    
    // 确保collectedData是数组
    if (!Array.isArray(collectedData.value)) {
      collectedData.value = []
    }
    
    hasCollectedData.value = collectedData.value.length > 0
    ElMessage.success('数据已刷新完成')
  } catch (error) {
    console.error('数据刷新失败:', error)
    ElMessage.error('数据刷新失败，请检查网络连接后重试')
  } finally {
    dataLoading.value = false
  }
}

const viewMessageDetail = (message) => {
  if (!message) {
    ElMessage.error('无效的消息数据')
    return
  }
  
  selectedMessage.value = message
  messageDetailVisible.value = true
}

const analyzeMessage = (message) => {
  if (!message || !message.content) {
    ElMessage.error('无效的消息数据')
    return
  }
  
  ElMessage.info(`正在分析消息: ${message.content.substring(0, 30)}${message.content.length > 30 ? '...' : ''}`)
  // 这里可以添加消息深度分析的逻辑
}

const saveCollectionTemplate = () => {
  if (!collectionTemplate.value.trim()) {
    ElMessage.warning('请输入收集模板')
    return
  }
  
  if (!generatedRegex.value.trim()) {
    ElMessage.warning('请先生成正则表达式')
    return
  }
  
  // 确保regexRules是数组
  if (!Array.isArray(regexRules.value)) {
    regexRules.value = []
  }
  
  // 添加新规则到表格
  const newRule = {
    originalMessage: originalMessage.value.trim(),
    pattern: generatedRegex.value.trim(),
    extractedContent: Object.values(extractedValues.value).join(', ')
  }
  
  regexRules.value.push(newRule)
  ElMessage.success('模板保存成功')
  templateDialogVisible.value = false
  
  // 清空对话框内容
  originalMessage.value = ''
  collectionTemplate.value = ''
  generatedRegex.value = ''
  extractedValues.value = {}
}

const autoLearnPattern = async () => {
  if (!originalMessage.value || !originalMessage.value.trim()) {
    ElMessage.warning('请输入原始消息示例')
    return
  }
  
  if (!collectionTemplate.value || !collectionTemplate.value.trim()) {
    ElMessage.warning('请输入要收集的数据')
    return
  }
  
  patternLearning.value = true
  
  try {
    // 模拟AI学习过程
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    const fields = collectionTemplate.value.split(',').map(field => field.trim()).filter(field => field)
    const message = originalMessage.value.trim()
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
      const parts = message.split(/[，,]/).map(part => part.trim()).filter(part => part)
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
    ElMessage.success('正则表达式生成成功')
  } catch (error) {
    console.error('智能学习过程中出现错误:', error)
    ElMessage.error('智能学习过程中出现错误')
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

const handleSizeChange = (val) => {
  pageSize.value = val
  refreshData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 正则规则管理
const showAddRuleDialog = () => {
  // 确保regexRules是数组
  if (!Array.isArray(regexRules.value)) {
    regexRules.value = []
  }
  
  ElMessageBox.prompt('请输入正则表达式规则', '添加规则', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPlaceholder: '例如：姓名[:：]?\\s*([^\\s，,]+)',
    inputType: 'textarea',
    inputValidator: (value) => {
      if (!value || !value.trim()) {
        return '请输入正则表达式'
      }
      return true
    }
  }).then(({ value }) => {
    // 添加新规则
    const newRule = {
      originalMessage: '用户自定义规则',
      pattern: value.trim(),
      extractedContent: '自定义提取内容'
    }
    regexRules.value.push(newRule)
    ElMessage.success('正则规则已添加')
  }).catch(() => {
    // 用户取消
  })
}

const deleteRegexRule = (index) => {
  // 确保regexRules是数组
  if (!Array.isArray(regexRules.value)) {
    console.warn('regexRules不是数组')
    return
  }
  
  // 确保索引有效
  if (index < 0 || index >= regexRules.value.length) {
    console.warn('无效的索引:', index)
    return
  }
  
  const ruleContent = regexRules.value[index]?.originalMessage || '未知规则'
  
  ElMessageBox.confirm(
    `确定要删除规则"${ruleContent.substring(0, 30)}${ruleContent.length > 30 ? '...' : ''}"吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    regexRules.value.splice(index, 1)
    ElMessage.success('正则规则已删除')
  }).catch(() => {
    // 用户取消
  })
}

const showRegexHelp = () => {
  ElMessageBox.alert(
    `正则表达式帮助：\n\n1. 匹配数字：\\d+\n2. 匹配中文：[\\u4e00-\\u9fa5]+\n3. 匹配邮箱：[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}\n4. 匹配手机号：1[3-9]\\d\n\n示例：匹配姓名和电话 - (.*?)电话：(\\d+)`,
    '正则表达式帮助',
    {
      confirmButtonText: '确定'
    }
  )
}

const startMonitoring = () => {
  // 确保monitoringResults是数组
  if (!Array.isArray(monitoringResults.value)) {
    monitoringResults.value = []
  }
  
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
      
      // 限制监控结果数量
      if (monitoringResults.value.length > 50) {
        monitoringResults.value.pop()
      }
    }
  }, 5000)
}

// ===== 辅助函数 =====
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
  if (!sender) {
    return 'https://api.dicebear.com/7.x/avataaars/svg?seed=unknown'
  }
  
  const avatarMap = {
    '张三': 'https://api.dicebear.com/7.x/avataaars/svg?seed=zhangsan',
    '李四': 'https://api.dicebear.com/7.x/avataaars/svg?seed=lisi',
    '王五': 'https://api.dicebear.com/7.x/avataaars/svg?seed=wangwu',
    '赵六': 'https://api.dicebear.com/7.x/avataaars/svg?seed=zhaoliu',
    '钱七': 'https://api.dicebear.com/7.x/avataaars/svg?seed=qianqi'
  }
  return avatarMap[sender] || `https://api.dicebear.com/7.x/avataaars/svg?seed=${sender.toLowerCase()}`
}

// 敏感词管理功能
const addSensitiveWord = () => {
  if (!newSensitiveWord.value || !newSensitiveWord.value.trim()) {
    ElMessage.warning('请输入敏感词')
    return
  }
  
  const word = newSensitiveWord.value.trim()
  
  // 确保sensitiveWordsList是数组
  if (!Array.isArray(sensitiveWordsList.value)) {
    sensitiveWordsList.value = []
  }
  
  if (sensitiveWordsList.value.includes(word)) {
    ElMessage.warning('该敏感词已存在')
    return
  }
  
  sensitiveWordsList.value.push(word)
  newSensitiveWord.value = ''
  ElMessage.success('敏感词添加成功')
}

const removeSensitiveWord = (index) => {
  // 确保sensitiveWordsList是数组
  if (!Array.isArray(sensitiveWordsList.value)) {
    console.warn('sensitiveWordsList不是数组')
    return
  }
  
  // 确保索引有效
  if (index < 0 || index >= sensitiveWordsList.value.length) {
    console.warn('无效的索引:', index)
    return
  }
  
  sensitiveWordsList.value.splice(index, 1)
  ElMessage.info('敏感词已删除')
}

// 删除规则
const deleteRule = (row) => {
  if (!row) {
    ElMessage.error('无效的规则数据')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除这条规则吗？\n时间: ${row.time}\n发送者: ${row.sender}\n内容: ${row.content ? row.content.substring(0, 30) + (row.content.length > 30 ? '...' : '') : ''}`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 这里实现实际的删除逻辑
    const index = collectedData.value.findIndex(item => 
      item.time === row.time && 
      item.sender === row.sender && 
      item.content === row.content
    )
    
    if (index !== -1) {
      collectedData.value.splice(index, 1)
      ElMessage.success('规则已成功删除')
    } else {
      ElMessage.error('未找到要删除的规则')
    }
  }).catch(() => {
    // 用户取消删除
    ElMessage.info('操作已取消')
  })
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
.app-container {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
}

/* 自定义滚动条样式 */
.main-content::-webkit-scrollbar {
  width: 6px;
}

.main-content::-webkit-scrollbar-thumb {
  background-color: var(--el-border-color-darker);
  border-radius: 3px;
}

.main-content::-webkit-scrollbar-track {
  background-color: var(--el-fill-color-blank);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.header-icon {
  color: var(--el-color-primary);
}

.feature-icon {
  margin-right: 8px;
}

.feature-icon.data-collection {
  color: var(--el-color-primary);
}

.feature-icon.monitoring {
  color: var(--el-color-warning);
}

.switch-label {
  font-weight: 500;
}

.rule-actions {
  margin-bottom: 16px;
}

.sensitive-word-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 500;
}

.sensitive-words-list {
  min-height: 60px;
  max-height: 120px;
  overflow-y: auto;
  padding: 12px;
  background-color: var(--el-fill-color-light);
  border-radius: var(--el-border-radius-base);
  margin-bottom: 12px;
}

/* 敏感词列表滚动条样式 */
.sensitive-words-list::-webkit-scrollbar {
  width: 4px;
}

.sensitive-words-list::-webkit-scrollbar-thumb {
  background-color: var(--el-border-color-darker);
  border-radius: 2px;
}

.sensitive-word-tag {
  margin: 4px;
}

.word-count {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  text-align: right;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.data-badge {
  margin-right: 8px;
}

.refresh-btn {
  padding: 6px 12px;
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sender-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.content-cell {
  line-height: 1.5;
  word-break: break-word;
}

.content-icon {
  margin-right: 6px;
}

.detail-btn {
  font-size: 13px;
  padding: 4px 8px;
}

.table-footer {
  padding: 16px 0;
  border-top: 1px solid var(--el-border-color-lighter);
}

.pagination {
  justify-content: flex-end;
}

.empty-state {
  padding: 40px 0;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-content {
  line-height: 1.6;
  word-break: break-word;
}

.regex-tips {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式布局调整 */
@media (max-width: 768px) {
  .app-container {
    padding: 10px;
    height: calc(100vh - 20px);
  }
  
  .header-actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .el-date-picker {
    width: 100% !important;
    margin-right: 0 !important;
    margin-bottom: 8px;
  }
  
  .el-select {
    width: 100% !important;
    margin-right: 0 !important;
    margin-bottom: 8px;
  }
}

/* 卡片间距优化 */
.el-row {
  margin-bottom: 16px;
}

.el-card {
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.el-card:hover {
  box-shadow: var(--el-box-shadow-light);
}

/* 表格区域优化 */
.data-display-section {
  background-color: #fff;
  border-radius: var(--el-border-radius-base);
  padding: 16px;
  box-shadow: var(--el-box-shadow-lighter);
}

.data-table {
  margin-top: 16px;
}

/* 规则表格优化 */
.rules-table {
  margin-top: 12px;
  max-height: 300px;
  overflow-y: auto;
}

/* 表单元素间距优化 */
.el-form-item {
  margin-bottom: 18px;
}

/* 按钮组样式优化 */
.rule-actions, .sensitive-word-header {
  margin-bottom: 16px;
}

/* 标签样式优化 */
.el-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

/* 对话框内容区域滚动条 */
.el-dialog__body {
  max-height: 70vh;
  overflow-y: auto;
}

.el-dialog__body::-webkit-scrollbar {
  width: 6px;
}

.el-dialog__body::-webkit-scrollbar-thumb {
  background-color: var(--el-border-color-darker);
  border-radius: 3px;
}
</style>