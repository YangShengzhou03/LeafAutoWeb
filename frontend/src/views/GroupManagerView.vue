<template>
  <div class="app-container">
    <div class="main-content">
      <!-- 数据收集配置 -->
      <el-row :gutter="24">
        <el-col :span="24">
          <el-card shadow="hover" class="section-card">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <el-icon class="feature-icon data-collection"><Collection /></el-icon>
                  <span>数据收集配置</span>
                </div>
              </div>
            </template>

            <el-form label-position="top" class="data-collection-form">
              <el-row :gutter="20" class="data-collection-row">
                <el-col :span="24">
                  <el-form-item label="数据收集配置" class="inline-form-item">
                    <div class="controls-row inline-controls">
                      <el-input v-model="contactPerson" placeholder="输入接管联系人姓名"
                        :disabled="isTakeoverLoading || !aiStatus" class="contact-input"></el-input>
                      <div class="status-control">
                        <el-switch v-model="aiStatus" active-color="#3b82f6" inactive-color="#d1d5db"
                          @change="handleSwitchChange" :loading="isTakeoverLoading"></el-switch>
                        <span class="status-text">{{ aiStatus ? '管理已启用' : '管理已禁用' }}</span>
                      </div>
                      <div class="status-control">
                        <el-switch v-model="dataCollectionEnabled" active-color="#3b82f6" inactive-color="#d1d5db"
                          @change="handleDataCollectionChange" :disabled="!aiStatus"></el-switch>
                        <span class="status-text">{{ dataCollectionEnabled ? '数据收集已启用' : '数据收集已禁用' }}</span>
                      </div>
                    </div>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>

            <!-- 其他内容保持不变 -->
            <el-form label-position="top" class="rules-form">
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
                <el-table :data="regexRules" class="rules-table" empty-text="暂无规则，请添加" stripe>
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
      <el-row :gutter="24">
        <el-col :span="24">
          <el-card shadow="hover" class="section-card">
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

            <el-form label-position="top" class="monitoring-form">
              <el-form-item class="monitoring-switch-item">
                <el-row justify="space-between" align="middle">
                  <span class="switch-label">启用舆情监控</span>
                  <el-switch
                    v-model="monitoringEnabled"
                    @change="handleMonitoringChange"
                    active-color="var(--success-color)"
                    class="monitoring-switch"
                  />
                </el-row>
              </el-form-item>

              <!-- 修改: 移除v-if条件，始终显示敏感词管理区域 -->
              <el-form-item label="敏感词管理">
                <div class="sensitive-word-header">
                  <span>敏感词列表</span>
                  <el-tooltip content="添加需要监控的敏感词汇" placement="top">
                    <el-icon><InfoFilled /></el-icon>
                  </el-tooltip>
                </div>
                
                <el-row :gutter="12" class="sensitive-word-input-row">
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
                      class="add-word-btn"
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
      <el-row :gutter="24">
        <el-col :span="24">
          <el-card shadow="hover" class="section-card">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <el-icon class="feature-icon"><DataAnalysis /></el-icon>
                  <span>收集数据展示</span>
                </div>
                <div class="header-actions filter-row">
              <el-select 
                v-model="selectedGroupFilter" 
                placeholder="筛选群聊" 
                size="small" 
                class="filter-select"
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
                class="date-picker-filter"
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

            <!-- 表格内容保持不变 -->
            <el-table 
              :data="currentPageData" 
              class="data-table" 
              border 
              v-loading="dataLoading" 
              stripe 
              max-height="400"
              @row-click="viewMessageDetail"
              :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#606266', fontWeight: '600' }">
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
              <el-table-column prop="type" label="消息类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="getMessageTypeTag(row.type)" size="small" effect="light">
                    {{ row.type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
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
              <el-button type="primary" @click="handleDataCollectionChange(true)" v-if="aiStatus">
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
      <!-- 对话框内容保持不变 -->
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
      <!-- 对话框内容保持不变 -->
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
// JavaScript 代码保持不变
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, computed, onMounted, watch } from 'vue'
import { 
  Plus, Key, Refresh, Clock,
  Collection, Monitor, DataAnalysis, Document,
  QuestionFilled, InfoFilled, MagicStick, Picture, 
  Message, Microphone, VideoCamera, Delete
} from '@element-plus/icons-vue'

const dataCollectionEnabled = ref(false)
const aiStatus = ref(false) // 管理状态
const isTakeoverLoading = ref(false) // 接管加载状态
const contactPerson = ref('') // 接管联系人
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
const dataLoading = ref(false)
const newSensitiveWord = ref('')
const sensitiveWordsList = ref(['会议', '机密', '内部', '紧急', '重要'])
const monitoringEnabled = ref(false)
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

// 筛选相关变量
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
  if (selectedGroupFilter.value && selectedGroupFilter.value.trim()) {
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

const hasCollectedData = computed(() => {
  return Array.isArray(collectedData.value) && collectedData.value.length > 0
})

// ===== 事件处理 =====
const handleSwitchChange = (enabled) => {
  isTakeoverLoading.value = true
  
  // 模拟API调用
  setTimeout(() => {
    isTakeoverLoading.value = false
    if (enabled && !contactPerson.value.trim()) {
      ElMessage.warning('请输入接管联系人姓名')
      aiStatus.value = false
      return
    }
    
    ElMessage.success(enabled ? '管理已启用' : '管理已禁用')
  }, 800)
}

const handleDataCollectionChange = (enabled) => {
  if (enabled && !aiStatus.value) {
    ElMessage.warning('请先启用管理功能')
    dataCollectionEnabled.value = false
    return
  }
  
  if (enabled) {
    ElMessage.success('数据收集功能已启用')
  } else {
    ElMessage.info('数据收集功能已禁用')
  }
}

const handleMonitoringChange = (enabled) => {
  if (enabled && !aiStatus.value) {
    ElMessage.warning('请先启用管理功能')
    monitoringEnabled.value = false
    return
  }
  
  if (enabled) {
    ElMessage.success('舆情监控功能已启用')
  } else {
    ElMessage.info('舆情监控功能已禁用')
  }
}

const showAddRuleDialog = () => {
  if (!dataCollectionEnabled.value) {
    ElMessage.warning('请先启用数据收集功能')
    return
  }
  
  templateDialogVisible.value = true
  // 重置对话框数据
  originalMessage.value = ''
  collectionTemplate.value = ''
  generatedRegex.value = ''
  extractedValues.value = {}
}

const showRegexHelp = () => {
  ElMessageBox.alert(
    '正则表达式帮助：\n\n' +
    '1. 使用 \\d+ 匹配数字\n' +
    '2. 使用 [a-zA-Z]+ 匹配字母\n' +
    '3. 使用 (.*?) 匹配任意内容\n' +
    '4. 使用 ^ 匹配开头，$ 匹配结尾\n\n' +
    '示例：姓名[:：]?\\s*([^\\s，,]+) 可以匹配"姓名：张三"中的"张三"',
    '正则表达式帮助',
    { confirmButtonText: '明白了' }
  )
}

const deleteRegexRule = (index) => {
  if (!Array.isArray(regexRules.value)) {
    ElMessage.error('规则数据异常')
    return
  }
  
  if (index < 0 || index >= regexRules.value.length) {
    ElMessage.error('无效的规则索引')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除这条规则吗？\n\n原始消息：${regexRules.value[index].originalMessage}\n正则表达式：${regexRules.value[index].pattern}`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    regexRules.value.splice(index, 1)
    ElMessage.success('规则已删除')
  }).catch(() => {
    // 用户取消删除
  })
}

const addSensitiveWord = () => {
  const word = newSensitiveWord.value.trim()
  
  if (!word) {
    ElMessage.warning('请输入敏感词')
    return
  }
  
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

// 删除收集的数据
const deleteRule = (row) => {
  if (!row) {
    ElMessage.error('无效的数据')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除这条数据吗？\n时间: ${row.time}\n发送者: ${row.sender}\n内容: ${row.content ? row.content.substring(0, 30) + (row.content.length > 30 ? '...' : '') : ''}`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 实现实际的删除逻辑
    const index = collectedData.value.findIndex(item => 
      item.time === row.time && 
      item.sender === row.sender && 
      item.content === row.content
    )
    
    if (index !== -1) {
      collectedData.value.splice(index, 1)
      ElMessage.success('数据已成功删除')
    } else {
      ElMessage.error('未找到要删除的数据')
    }
  }).catch(() => {
    // 用户取消删除
    ElMessage.info('操作已取消')
  })
}

const refreshData = () => {
  dataLoading.value = true
  // 模拟数据刷新
  setTimeout(() => {
    dataLoading.value = false
    ElMessage.success('数据已刷新')
  }, 1000)
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

const viewMessageDetail = (row) => {
  selectedMessage.value = row
  messageDetailVisible.value = true
}

const analyzeMessage = () => {
  ElMessage.info('深度分析功能开发中')
}

// ===== 工具函数 =====
const getAvatarUrl = (sender) => {
  return `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(sender)}`
}

const getMessageIcon = (type) => {
  const iconMap = {
    '图片': Picture,
    '文件': Document,
    '语音': Microphone,
    '视频': VideoCamera,
    '文本': Message
  }
  return iconMap[type] || Message
}

const getMessageTypeTag = (type) => {
  const typeMap = {
    '图片': 'success',
    '文件': 'warning',
    '语音': 'info',
    '视频': 'danger',
    '文本': ''
  }
  return typeMap[type] || ''
}

const getContentClass = (type) => {
  return `content-${type.toLowerCase()}`
}

const autoLearnPattern = () => {
  patternLearning.value = true
  // 模拟智能学习过程
  setTimeout(() => {
    patternLearning.value = false
    // 这里应该根据原始消息和提取内容生成正则表达式
    // 简化示例：生成一个基础的正则表达式
    generatedRegex.value = '姓名[:：]?\\s*([^\\s，,]+)\\s*[，,]?\\s*电话[:：]?\\s*(1[3-9]\\d{9})'
    extractedValues.value = {
      '姓名': '张三',
      '电话': '13800138000'
    }
    ElMessage.success('模式学习完成')
  }, 1500)
}

const showPatternHelp = () => {
  ElMessageBox.alert(
    '智能模板使用说明：\n\n' +
    '1. 在"原始消息内容"中输入完整的消息示例\n' +
    '2. 在"需要提取的内容"中输入您想提取的信息，用逗号分隔\n' +
    '3. 点击"智能学习模式"让系统自动生成匹配规则\n' +
    '4. 检查生成的规则并进行必要的调整\n' +
    '5. 保存模板后即可用于数据收集',
    '使用说明',
    { confirmButtonText: '明白了' }
  )
}

const saveCollectionTemplate = () => {
  if (!generatedRegex.value.trim()) {
    ElMessage.warning('请先生成正则表达式')
    return
  }
  
  if (!originalMessage.value.trim()) {
    ElMessage.warning('请输入原始消息内容')
    return
  }
  
  // 确保regexRules是数组
  if (!Array.isArray(regexRules.value)) {
    regexRules.value = []
  }
  
  regexRules.value.push({
    originalMessage: originalMessage.value,
    pattern: generatedRegex.value,
    extractedContent: Object.values(extractedValues.value).join(', ')
  })
  
  templateDialogVisible.value = false
  ElMessage.success('模板保存成功')
}

// ===== 生命周期钩子 =====
onMounted(() => {
  // 初始化操作
  console.log('数据收集配置视图已加载')
  
  // 确保所有响应式数据都是正确的类型
  if (!Array.isArray(regexRules.value)) {
    regexRules.value = []
  }
  if (!Array.isArray(collectedData.value)) {
    collectedData.value = []
  }
  if (!Array.isArray(sensitiveWordsList.value)) {
    sensitiveWordsList.value = []
  }
})

// 监听数据变化
watch(aiStatus, (newVal) => {
  if (newVal) {
    console.log('管理功能已启用')
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
  --primary-color: #1e40af;
  --secondary-color: #3b82f6;
  --accent-color: #2563eb;
  --light-color: #f8fafc;
  --dark-color: #1e293b;
  --text-primary: #0f172a;
  --text-secondary: #3b82f6;
  --success-color: #8b5cf6;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
  --border-color: #e2e8f0;
}

/* 主容器优化 */
.app-container {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 24px;
  background-color: var(--el-bg-color-page);
  min-height: 100vh;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding-right: 12px;
}

/* 卡片样式优化 */
.el-card {
  margin-bottom: 24px;
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
}

.el-card:hover {
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

/* 卡片头部优化 */
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
  gap: 12px;
  font-weight: 600;
  font-size: 18px;
  color: var(--text-primary);
}

.header-status {
  display: flex;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  padding: 0 20px;
}

/* 表单样式优化 */
.data-collection-form,
.rules-form,
.monitoring-form {
  padding: 20px 24px;
}

.el-form-item {
  margin-bottom: 24px;
  padding: 0 20px;
}

.el-form-item:last-child {
  margin-bottom: 0;
}

.el-form-item__label {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

/* 数据收集配置行 - 确保在同一行显示 */
.data-collection-row .el-col {
  display: flex;
  align-items: center;
}

.inline-form-item {
  width: 100%;
}

.inline-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  width: 100%;
}

.contact-input {
  flex: 1;
  min-width: 200px;
  margin-bottom: 0;
}

/* 状态控件优化 */
.status-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-text {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

/* 输入框和控件间距优化 */
.el-input,
.el-select,
.el-date-picker {
  margin-bottom: 16px;
}

.el-input__prefix {
  padding-right: 8px;
  color: var(--el-text-color-secondary);
}

/* 按钮组和操作区域优化 */
.rule-actions {
  margin-bottom: 20px;
  padding: 0 20px;
  display: flex;
  gap: 12px;
  align-items: center;
}

.sensitive-word-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  font-weight: 500;
  padding: 0 20px;
}

/* 敏感词列表优化 */
.sensitive-words-list {
  min-height: 80px;
  max-height: 150px;
  overflow-y: auto;
  padding: 16px 20px;
  background-color: var(--el-fill-color-lighter);
  border-radius: 8px;
  margin: 0 20px 16px 20px;
  border: 1px solid var(--el-border-color-light);
}

.sensitive-word-tag {
  margin: 6px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  transition: all 0.2s ease;
}

.sensitive-word-tag:hover {
  transform: scale(1.05);
  box-shadow: var(--el-box-shadow-light);
}

/* 表格区域优化 */
.data-table {
  margin-top: 20px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter);
}

.data-table .el-table__cell {
  padding: 16px 20px;
  font-size: 14px;
}

/* 表格单元格优化 */
.time-cell,
.sender-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.content-cell {
  line-height: 1.6;
  word-break: break-word;
  font-size: 14px;
  padding: 8px 0;
  color: var(--el-text-color-primary);
}

.content-icon {
  margin-right: 8px;
  font-size: 16px;
  color: var(--el-text-color-secondary);
}

/* 按钮样式优化 */
.detail-btn,
.delete-btn {
  font-size: 13px;
  padding: 8px 12px;
  border-radius: 6px;
  margin: 0 4px;
  transition: all 0.2s ease;
}

.detail-btn:hover,
.delete-btn:hover {
  transform: translateY(-1px);
}

.refresh-btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
}

/* 页脚和分页优化 */
.table-footer {
  padding: 24px 20px;
  border-top: 1px solid var(--el-border-color-lighter);
  margin-top: 20px;
  background-color: var(--el-fill-color-lighter);
}

.pagination {
  justify-content: flex-end;
  gap: 8px;
}

/* 空状态优化 */
.empty-state {
  padding: 60px 0;
  margin: 20px 0;
  color: var(--el-text-color-secondary);
}

/* 对话框优化 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding: 24px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.regex-tips {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 20px;
}

/* 详情展示优化 */
.detail-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  font-size: 14px;
}

.detail-content {
  line-height: 1.7;
  word-break: break-word;
  font-size: 14px;
  padding: 16px;
  background-color: var(--el-fill-color-lighter);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
}

/* 特殊状态优化 */
.word-count {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  text-align: right;
  padding: 0 20px;
  margin-top: 8px;
}

.feature-icon {
  margin-right: 10px;
  font-size: 20px;
  transition: all 0.3s ease;
}

.feature-icon.data-collection {
  color: var(--el-color-primary);
}

.feature-icon.monitoring {
  color: var(--el-color-warning);
}

.switch-label {
  font-weight: 500;
  font-size: 14px;
  color: var(--el-text-color-primary);
}

/* 舆情监控开关增加间距 */
.monitoring-switch-item {
  padding-bottom: 16px;
  border-bottom: 1px dashed var(--el-border-color-light);
  margin-bottom: 16px !important;
}

.monitoring-switch {
  margin-left: 20px;
}

/* 筛选行保持在同一行 */
.filter-row {
  flex-wrap: nowrap;
}

.filter-select {
  min-width: 180px;
  margin-bottom: 0;
}

.date-picker-filter {
  min-width: 300px;
  margin-bottom: 0;
}

/* 确保所有元素都有合适的间距 */
.el-button {
  margin: 4px;
  transition: all 0.2s ease;
}

.el-button:hover {
  transform: translateY(-1px);
}

.el-tag {
  margin: 6px;
  transition: all 0.2s ease;
}

.el-tag:hover {
  transform: scale(1.05);
}

/* 表格操作按钮间距 */
.el-table__cell .el-button {
  margin: 0 4px;
}

/* 对话框内表单间距 */
.el-dialog .el-form-item {
  padding: 0;
  margin-bottom: 24px;
}

.el-dialog .el-form-item:last-child {
  margin-bottom: 0;
}

/* 滚动条统一优化 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-thumb {
  background-color: var(--el-border-color);
  border-radius: 4px;
}

::-webkit-scrollbar-track {
  background-color: var(--el-fill-color-blank);
}

/* 响应式布局调整 */
@media (max-width: 768px) {
  .app-container {
    padding: 16px;
    height: calc(100vh - 32px);
  }
  
  .header-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .el-date-picker,
  .el-select {
    width: 100% !important;
    margin-right: 0 !important;
    margin-bottom: 12px;
  }
  
  .rule-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .el-form-item {
    padding: 0 16px;
  }
  
  .sensitive-words-list {
    margin: 0 16px 16px 16px;
  }
  
  .card-header {
    padding: 16px 20px;
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .header-title {
    font-size: 16px;
  }
  
  .data-collection-form,
  .rules-form,
  .monitoring-form {
    padding: 16px 20px;
  }
  
  .data-table .el-table__cell {
    padding: 12px 16px;
  }
  
  .table-footer {
    padding: 20px 16px;
  }
  
  .dialog-footer {
    padding: 20px;
    flex-direction: column;
    gap: 12px;
  }
  
  .el-button {
    width: 100%;
    margin: 4px 0;
  }
  
  /* 响应式下保持控件在一行但允许换行 */
  .inline-controls {
    flex-wrap: wrap;
  }
  
  .status-control {
    margin-bottom: 12px;
  }
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 加载状态优化 */
:deep(.el-loading-mask) {
  background-color: rgba(255, 255, 255, 0.8);
}

:deep(.el-loading-spinner .circular) {
  width: 42px;
  height: 42px;
}

/* 表单验证状态 */
:deep(.el-form-item.is-error .el-input__inner) {
  border-color: var(--el-color-error);
}

:deep(.el-form-item.is-success .el-input__inner) {
  border-color: var(--el-color-success);
}

/* 表格行悬停效果 */
:deep(.el-table__body tr:hover>td) {
  background-color: var(--el-color-primary-light-9) !important;
}
</style>
