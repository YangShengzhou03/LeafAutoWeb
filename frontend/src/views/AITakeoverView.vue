<template>
  <div class="app-container">

    <div class="main-content">

      <div class="top-row">

        <div class="config-card">
          <el-card class="config-card-inner" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span>AI 自动回复配置</span>
                </div>
              </div>
            </template>

            <el-form ref="aiForm" :model="formData" :rules="rules" class="custom-input">
              <div class="controls-row">
                <el-form-item label="接管状态" prop="aiStatus" class="inline-form-item">
                  <div class="status-toggle inline-status">
                    <el-switch v-model="formData.aiStatus" active-color="#3b82f6" inactive-color="#d1d5db"
                      @change="handleSwitchChange" :loading="isTakeoverLoading"></el-switch>
                  </div>
                </el-form-item>

                <el-form-item label="仅被@时触发" prop="onlyAtTrigger" class="inline-form-item">
                  <div class="status-toggle">
                    <el-switch v-model="formData.onlyAtTrigger" active-color="#3b82f6" inactive-color="#d1d5db"
                      @change="handleOnlyAtChange" :loading="isTakeoverLoading"></el-switch>
                  </div>
                </el-form-item>

                <el-form-item label="回复时@对方" prop="groupAtReply" class="inline-form-item">
                  <div class="status-toggle">
                    <el-switch v-model="formData.groupAtReply" active-color="#3b82f6" inactive-color="#d1d5db"
                      @change="handleGroupAtChange" :loading="isTakeoverLoading"></el-switch>
                  </div>
                </el-form-item>

                <el-form-item label="模型" prop="aiModel" class="inline-form-item">
                  <el-select v-model="formData.aiModel" placeholder="请选择" :loading="isTakeoverLoading">
                    <el-option label="禁用模型" value="disabled"></el-option>
                    <el-option label="文心一言" value="wenxin"></el-option>
                    <el-option label="月之暗面" value="moonshot"></el-option>
                    <el-option label="星火讯飞" value="xinghuoxunfei"></el-option>
                  </el-select>
                </el-form-item>
              </div>

              <el-form-item label="回复延迟(秒)" prop="replyDelay">
                <el-input-number v-model="formData.replyDelay" :min="0" :max="30" placeholder="输入回复延迟时间"
                  :disabled="isTakeoverLoading"></el-input-number>
              </el-form-item>

              <el-form-item label="相同内容最小回复间隔(秒)" prop="minReplyInterval">
                <el-input-number v-model="formData.minReplyInterval" :min="0" :max="3600" placeholder="输入相同内容最小回复间隔"
                  :disabled="isTakeoverLoading"></el-input-number>
              </el-form-item>

              <el-form-item label="接管联系人" prop="contactPerson">
                <el-input v-model="formData.contactPerson" placeholder="输入接管联系人姓名"
                  :disabled="isTakeoverLoading"></el-input>
              </el-form-item>

              <el-form-item label="AI人设" prop="aiPersona">
                <el-input v-model="formData.aiPersona" type="textarea" placeholder="描述AI的性格和回复风格" :rows="4"
                  :disabled="isTakeoverLoading"></el-input>
              </el-form-item>

              <div class="action-buttons">
                <el-button type="primary" :loading="isSubmitting" :loading-icon="Loading" @click="submitForm" class="gradient-btn"
                  :disabled="isTakeoverLoading">保存设置</el-button>
                <el-button @click="resetForm" :disabled="isTakeoverLoading">重置</el-button>
              </div>
            </el-form>
          </el-card>
        </div>


        <div class="insights-card">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span>AI 性能洞察</span>
                </div>
              </div>
            </template>

            <div class="card-body">
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-value counter">{{ stats.replyRate }}%</div>
                  <div class="stat-label">回复率</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value counter">{{ stats.averageTime }}s</div>
                  <div class="stat-label">平均响应时间</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value counter">{{ stats.satisfactionRate }}%</div>
                  <div class="stat-label">满意度</div>
                </div>
              </div>


              <div class="chart-container">
                <div class="chart-card">
                  <div class="chart-header">
                    <h3>近7天AI回复数量趋势</h3>
                    <div class="chart-actions">
                      <el-select v-model="chartRange" placeholder="选择范围" size="small" class="chart-select">
                        <el-option label="7天" value="7d"></el-option>
                        <el-option label="30天" value="30d"></el-option>
                        <el-option label="90天" value="90d"></el-option>
                      </el-select>
                    </div>
                  </div>

                  <div class="chart-content">
                    <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="180" viewBox="0 0 400 180">
                      <defs>
                        <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.4" />
                          <stop offset="100%" stop-color="#3b82f6" stop-opacity="0" />
                        </linearGradient>
                      </defs>

                      <!-- 动态路径 -->
                      <path :d="generateChartPath(chartData.counts)" fill="url(#areaGradient)" stroke="#3b82f6"
                        stroke-width="3" stroke-linecap="round" />

                      <!-- 基准线 -->
                      <path d="M0,150 L400,150" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="4" />

                      <!-- 动态数据点 -->
                      <circle v-for="(count, index) in chartData.counts" :key="index"
                        :cx="index * (400 / (chartData.counts.length - 1))" :cy="150 - (count / maxCount * 100)" r="4"
                        fill="#ffffff" stroke="#3b82f6" stroke-width="2" />

                      <!-- X轴标签 -->
                      <text v-for="(date, index) in chartData.dates" :key="'label-' + index"
                        :x="index * (400 / (chartData.dates.length - 1))" y="170" text-anchor="middle" font-size="10"
                        fill="#64748b">
                        {{ date }}
                      </text>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <el-card class="rules-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-title">
              <span>AI 自定义回复规则</span>
            </div>
          </div>
        </template>

        <div class="custom-rules-container">
          <div class="rule-actions">
            <el-button type="primary" @click="openAddRuleDialog" class="gradient-btn"
              :disabled="isTakeoverLoading">添加规则</el-button>
          </div>

          <el-table v-model:data="formData.customRules" class="rules-table" ref="rulesForm" row-key="id">
            <el-table-column prop="matchType" label="匹配类型" width="180">
              <template #default="{ row }">
                <span>{{ row.matchType === 'contains' ? '包含关键词' : row.matchType === 'equals' ? '完全匹配' : '正则表达式'
                  }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="keyword" label="关键词/规则" width="240">
              <template #default="{ row }">
                <span>{{ row.keyword }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="reply" label="回复内容">
              <template #default="{ row }">
                <span>{{ row.reply }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ $index }">
                <div class="operation-buttons">
                  <el-button type="danger" size="small" @click="removeRule($index)" class="delete-btn"
                    :disabled="isTakeoverLoading">删除</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>


      <el-dialog v-model="addRuleDialogVisible" title="添加回复规则" width="600px" custom-class="add-rule-dialog">
        <el-form ref="ruleForm" :model="newRule" :rules="ruleFormRules" class="custom-input">
          <el-form-item label="匹配类型" prop="matchType">
            <el-select v-model="newRule.matchType" placeholder="选择匹配类型" class="custom-select">
              <el-option label="包含关键词" value="contains"></el-option>
              <el-option label="完全匹配" value="equals"></el-option>
              <el-option label="正则表达式" value="regex"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="关键词/规则" prop="keyword">
            <el-input v-model="newRule.keyword" placeholder="输入关键词或规则" class="custom-input"></el-input>
          </el-form-item>
          <el-form-item label="回复内容" prop="reply">
            <el-input v-model="newRule.reply" type="textarea" placeholder="输入回复内容（文字，文件路径 或 SendEmotion:2）" :rows="4"
              class="custom-input"></el-input>
          </el-form-item>
        </el-form>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="addRuleDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmAddRule">确定</el-button>
          </div>
        </template>
      </el-dialog>


      <el-card class="history-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="header-title">
              <span>AI 回复历史</span>
            </div>
            <div class="history-controls">
              <el-input v-model="searchQuery" placeholder="搜索消息内容..." :prefix-icon="Search" size="small"
                class="search-input"></el-input>
            </div>
          </div>
        </template>

        <el-table v-if="filteredHistory.length > 0" v-loading="isLoadingHistory" :data="paginatedHistory"
          style="width: 100%" class="custom-table" stripe :row-class-name="tableRowClassName" :show-empty="false">
          <el-table-column prop="time" label="时间" width="180" sortable>
            <template #default="{ row }">
              <div class="time-cell">
                {{ formatDate(row.time) }} {{ formatTime(row.time) }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="原始消息" width="180">
            <template #default="{ row }">
              <el-tooltip :content="row.message" placement="top">
                <span class="message-content">{{ truncateText(row.message, 20) }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="aiReply" label="AI 回复">
            <template #default="{ row }">
              <el-tooltip :content="row.aiReply" placement="top">
                <span class="reply-cell">{{ truncateText(row.aiReply, 30) }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'replied' ? 'success' : 'warning'" size="small" class="status-tag">
                {{ row.status === 'replied' ? '已回复' : '未回复' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <div class="operation-buttons">
                <el-button type="danger" size="small" @click="deleteHistory(row)">
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container" v-if="filteredHistory.length > 0">
          <el-pagination v-model:current-page="currentPage" :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper" :total="filteredHistory.length"
            @size-change="handleSizeChange" @current-change="handleCurrentChange"
            class="custom-pagination"></el-pagination>
        </div>

        <el-empty v-else-if="!isLoadingHistory" description="暂无回复历史" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Loading } from '@element-plus/icons-vue'


const aiForm = ref(null)
const rulesForm = ref(null)


const formData = reactive({
  aiStatus: false,
  onlyAtTrigger: false,
  groupAtReply: false,
  replyDelay: 0,
  minReplyInterval: 0,
  contactPerson: '文件传输助手',
  aiPersona: '你是一个微信好友，全程隐藏 AI 身份，能类似真人般自然回应，具体按以下要求执行：对话风格：完全口语化，不用长句和书面词，带日常语气词（如"卧槽"等）或网络热梗。话题应对：懂的话题别 "掉书袋"，聊日常细节就行。应对 "AI 质疑"：如果用户说 "你怎么像机器人" "你是 AI 吧"，别辩解，不能掉入"自证陷阱"，要嘲讽对方。总之，你就是一个普通人，聊得随意、有烟火气，别让人觉得 "说话没温度、不像真人"。',
  aiModel: 'disabled',
  customRules: []
})

const isTakeoverLoading = ref(false)

const handleSwitchChange = async (newStatus) => {
  isTakeoverLoading.value = true

  try {
    if (newStatus) {
      // 先保存设置，确保传递到后端的是最新的设置数据
      await submitForm()
      
      // 发送开始接管请求
      const response = await fetch('http://localhost:5000/api/ai-takeover/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contactPerson: formData.contactPerson,
          aiPersona: formData.aiPersona,
          onlyAt: formData.onlyAtTrigger,
          groupAtReply: formData.groupAtReply,
          aiModel: formData.aiModel,
          replyDelay: formData.replyDelay,
          minReplyInterval: formData.minReplyInterval
        })
      })

      const result = await response.json()

      if (result.success) {
        // 使用API返回的状态确保同步
        formData.aiStatus = Boolean(result.aiStatus ?? true)
        ElMessage.success('开始监听并自动进行回复')
      } else {
        // 操作失败时恢复开关状态
        formData.aiStatus = false
        ElMessage.error(`开始接管失败: ${result.error || '未知错误'}`)
      }
    } else {
      // 发送停止接管请求
      const response = await fetch('http://localhost:5000/api/ai-takeover/stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contactPerson: formData.contactPerson,
          aiModel: formData.aiModel
        })
      })

      const result = await response.json()

      if (result.success) {
        // 使用API返回的状态确保同步
        formData.aiStatus = Boolean(result.aiStatus ?? false)
        ElMessage.warning('已停止消息监听与回复')
      } else {
        // 操作失败时恢复开关状态
        formData.aiStatus = true
        ElMessage.error(`停止接管失败: ${result.error || '未知错误'}`)
      }
    }
  } catch (error) {
    console.error('AI接管操作失败:', error)
    // 操作失败时恢复开关状态
    formData.aiStatus = !newStatus
    ElMessage.error(`AI接管操作失败: ${error.message || '网络错误'}`)
  } finally {
    isTakeoverLoading.value = false
  }
}




const rules = {
  replyDelay: [
    { required: true, message: '请输入回复延迟', trigger: 'blur' },
    { type: 'number', message: '回复延迟必须是数字', trigger: 'blur' }
  ],
  minReplyInterval: [
    { required: true, message: '请输入最小回复间隔时间', trigger: 'blur' },
    { type: 'number', message: '最小回复间隔必须是数字', trigger: 'blur' }
  ],
  contactPerson: [
    { required: true, message: '请输入接管联系人', trigger: 'blur' }
  ],
  aiPersona: [
    { required: true, message: '请输入AI人设', trigger: 'blur' },
    { min: 10, max: 500, message: 'AI人设长度必须在10-500个字符之间', trigger: 'blur' }
  ]
}


// 添加规则相关变量
const addRuleDialogVisible = ref(false)
const ruleForm = ref(null)
const newRule = reactive({
  matchType: 'contains',
  keyword: '',
  reply: ''
})

// 规则表单验证规则
const ruleFormRules = {
  keyword: [
    { required: true, message: '请输入关键词或规则', trigger: 'blur' },
    { min: 1, max: 100, message: '关键词长度必须在1-100个字符之间', trigger: 'blur' }
  ],
  reply: [
    { required: true, message: '请输入回复内容', trigger: 'blur' },
    { min: 5, max: 500, message: '回复内容长度必须在5-500个字符之间', trigger: 'blur' }
  ]
}

// 打开添加规则对话框
const openAddRuleDialog = () => {
  // 重置表单
  if (ruleForm.value) {
    ruleForm.value.resetFields()
  }
  Object.assign(newRule, {
    matchType: 'contains',
    keyword: '',
    reply: ''
  })
  addRuleDialogVisible.value = true
}

// 添加规则
const confirmAddRule = async () => {
  try {
    await ruleForm.value.validate()
    formData.customRules.push({
      id: Date.now(),
      matchType: newRule.matchType,
      keyword: newRule.keyword,
      reply: newRule.reply
    })
    addRuleDialogVisible.value = false
    ElMessage.success('规则添加成功')
    await submitForm()
  } catch (error) {
    console.error('表单验证失败:', error)
    ElMessage.error('请检查表单填写是否正确')
  }
}


const removeRule = async (index) => {
  formData.customRules.splice(index, 1)
  await submitForm()
  ElMessage.success('规则删除成功')
}


const replyHistory = ref([])

// 获取回复历史数据
const fetchReplyHistory = async () => {
  try {
    isLoadingHistory.value = true
    const response = await fetch('http://localhost:5000/api/ai-history')
    if (response.ok) {
      const data = await response.json()
      // 转换数据格式以匹配前端表格
      replyHistory.value = data.map(item => ({
        time: item.time || item.timestamp, // 使用time字段或timestamp字段
        message: item.message,
        aiReply: item.reply,
        status: item.status
      }))
    } else {
      ElMessage.error('获取回复历史失败')
    }
  } catch (error) {
    console.error('获取回复历史失败:', error)
    ElMessage.error('网络错误，无法获取回复历史')
  } finally {
    isLoadingHistory.value = false
  }
}

// 获取AI设置 ai接管状态 回复延迟 最小回复间隔 接管联系人 AI人设 自定义规则
const fetchAiSettings = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/ai-settings')
    if (response.ok) {
      const data = await response.json()
      const settingsData = Array.isArray(data) && data.length > 0 ? data[0] : data

      // 直接从API响应中获取aiStatus状态
      Object.assign(formData, {
        ...settingsData,
        replyDelay: Number(settingsData.replyDelay ?? 0),
        minReplyInterval: Number(settingsData.minReplyInterval ?? 0),
        customRules: settingsData.customRules || [],
        aiStatus: Boolean(settingsData.aiStatus ?? false) // 确保使用API返回的状态
      })

      await nextTick() // 确保UI更新
    } else {
      ElMessage.error('获取AI设置失败')
    }
  } catch (error) {
    console.error('获取AI设置失败:', error)
    ElMessage.error('网络错误，无法获取AI设置')
  }
}


const searchQuery = ref('')
const filterStatus = ref('all')
const currentPage = ref(1)
const pageSize = ref(5)
const isLoadingHistory = ref(false)
const isSubmitting = ref(false)
const chartRange = ref('7d')


const stats = reactive({
  replyRate: 0,
  averageTime: 0,
  satisfactionRate: 0
})


const filteredHistory = computed(() => {
  return replyHistory.value
    .filter(item => {
      const matchesSearch = item.message.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        item.aiReply.toLowerCase().includes(searchQuery.value.toLowerCase())
      const matchesStatus = filterStatus.value === 'all' || item.status === filterStatus.value
      return matchesSearch && matchesStatus
    })
})


const paginatedHistory = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  return filteredHistory.value.slice(startIndex, startIndex + pageSize.value)
})

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (current) => {
  currentPage.value = current
}


const submitForm = async () => {
  isSubmitting.value = true
  try {
    if (!formData.contactPerson.trim()) {
      formData.contactPerson = '文件传输助手'
    }

    if (aiForm.value) {
      await aiForm.value.validate()
    }

    const submitData = {
      ...formData,
      // 确保数值类型
      replyDelay: Number(formData.replyDelay),
      minReplyInterval: Number(formData.minReplyInterval),
      customRules: Array.isArray(formData.customRules) ? formData.customRules : []
    }

    const response = await fetch('http://localhost:5000/api/ai-settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(submitData)
    })

    if (response.ok) {
      const data = await response.json()
      // 处理返回数据的格式（修复点2）
      const responseData = Array.isArray(data) && data.length > 0 ? data[0] : data
      formData.customRules = responseData.customRules || []
      // 确保UI状态与后端保存的状态同步（修复状态同步问题）
      formData.aiStatus = Boolean(responseData.aiStatus ?? false)
    } else {
      const errorData = await response.json().catch(() => ({}))
      ElMessage.error(`保存失败: ${errorData.error || '未知错误，请稍后重试'}`)
    }
  } catch (error) {
    console.error('保存设置失败:', error)
    if (error.name === 'ValidationError') {
      ElMessage.error(`表单验证失败: ${error.message}`)
    } else {
      ElMessage.error(`保存失败: ${error.message || '网络错误'}`)
    }
  } finally {
    isSubmitting.value = false
  }
}


const resetForm = async () => {
  ElMessageBox.confirm('确定要重置所有设置吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    formData.aiStatus = false
    formData.replyDelay = 5
    formData.minReplyInterval = 60
    formData.contactPerson = ''
    formData.aiPersona = '我是一个友好、专业的AI助手，致力于为用户提供准确、及时的帮助。'
    formData.customRules = []
    ElMessage.success('设置已重置')
  }).catch(() => { })
}


const deleteHistory = async (row) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条历史记录吗？此操作不可恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    const response = await fetch('http://localhost:5000/api/ai-history/delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        time: row.time,
        message: row.message
      })
    });
    
    if (response.ok) {
      ElMessage.success('历史记录删除成功');
      await fetchReplyHistory(); // 重新加载历史记录
    } else {
      const errorData = await response.json().catch(() => ({}));
      ElMessage.error(`删除失败: ${errorData.error || '未知错误'}`);
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除历史记录失败:', error);
      ElMessage.error(`删除失败: ${error.message || '网络错误'}`);
    }
  }
}

// 图表相关数据
const chartData = ref({
  dates: [],
  counts: []
})

// 获取图表数据的方法
const fetchChartData = async (range) => {
  // 创建一个AbortController实例
  const controller = new AbortController();
  const signal = controller.signal;

  // 存储当前请求的控制器，以便在需要时取消
  activeChartRequest.value = controller;

  try {
    const response = await fetch(`http://localhost:5000/api/stats/${range}`, { signal });
    if (response.ok) {
      const data = await response.json();
      chartData.value = data.chartData || { dates: [], counts: [] };

      if (data.stats) {
        Object.assign(stats, {
          replyRate: Number(data.stats.replyRate ?? 0),
          averageTime: Number(data.stats.averageTime ?? 0),
          satisfactionRate: Number(data.stats.satisfactionRate ?? 100)
        });
      }
    }
  } catch (error) {
    // 忽略由于取消请求而产生的错误
    if (error.name !== 'AbortError') {
      console.error('获取图表数据失败:', error);
    }
  } finally {
    // 如果当前请求是最后一个，则清除
    if (activeChartRequest.value === controller) {
      activeChartRequest.value = null;
    }
  }
};

// 用于存储当前激活的图表请求控制器
const activeChartRequest = ref(null);

// 在组件卸载时取消请求
onUnmounted(() => {
  if (activeChartRequest.value) {
    activeChartRequest.value.abort();
    activeChartRequest.value = null;
  }
});

// 监听时间范围变化
watch(chartRange, (newVal) => {
  fetchChartData(newVal);
});

// 修改原有的 fetchAiStats 方法
const fetchAiStats = async () => {
  try {
    isLoadingHistory.value = true;
    await fetchChartData(chartRange.value);
  } catch (error) {
    console.error('获取AI看板数据失败:', error);
    ElMessage.error('网络错误，无法获取AI看板数据');
  } finally {
    isLoadingHistory.value = false;
  }
};

// 添加计算属性用于图表
const maxCount = computed(() => {
  return Math.max(...chartData.value.counts, 1);
});

// 生成SVG路径
const generateChartPath = (counts) => {
  if (!counts || counts.length === 0) return 'M0,150 L400,150';

  const points = counts.map((count, index) => {
    const x = index * (400 / (counts.length - 1));
    const y = 150 - (count / maxCount.value * 100);
    return `${x},${y}`;
  });

  // 平滑曲线
  let path = `M${points[0]}`;
  for (let i = 1; i < points.length; i++) {
    const prev = points[i - 1].split(',');
    const curr = points[i].split(',');
    const cpx1 = (Number(prev[0]) + Number(curr[0])) / 2;
    const cpy1 = Number(prev[1]);
    const cpx2 = cpx1;
    const cpy2 = Number(curr[1]);
    path += ` C${cpx1},${cpy1} ${cpx2},${cpy2} ${curr[0]},${curr[1]}`;
  }
  return path;
};



const formatDate = (dateTime) => {
  const date = new Date(dateTime)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const formatTime = (dateTime) => {
  const date = new Date(dateTime)
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}


const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? `${text.substring(0, length)}...` : text
}


const tableRowClassName = ({ row }) => {
  return row.status === 'pending' ? 'task-pending' : 'task-completed';
}

// 处理群回复时@对方开关变化
const handleGroupAtChange = async () => {
  isTakeoverLoading.value = true
  
  try {
    // 仅保存设置，不改变接管状态
    await submitForm()
    ElMessage.success('群回复时@对方设置已更新')
  } catch (error) {
    console.error('更新群回复时@对方设置失败:', error)
    ElMessage.error(`更新设置失败: ${error.message || '网络错误'}`)
  } finally {
    isTakeoverLoading.value = false
  }
}

// 处理仅被@时触发开关变化
const handleOnlyAtChange = async () => {
  isTakeoverLoading.value = true
  
  try {
    // 仅保存设置，不改变接管状态
    await submitForm()
    ElMessage.success('仅被@时触发设置已更新')
  } catch (error) {
    console.error('更新仅被@时触发设置失败:', error)
    ElMessage.error(`更新设置失败: ${error.message || '网络错误'}`)
  } finally {
    isTakeoverLoading.value = false
  }
}

onMounted(async () => {
  try {
    await fetchAiSettings();
  } catch (error) {
    ElMessage.error('初始化AI设置失败');
    console.error('初始化AI设置失败:', error);
  }

  try {
    await fetchReplyHistory() // 获取回复历史数据
  } catch (error) {
    ElMessage.error('初始化回复历史数据失败');
    console.error('初始化回复历史数据失败:', error);
  }

  try {
    await fetchAiStats();
  } catch (error) {
    ElMessage.error('初始化AI统计数据失败');
    console.error('初始化AI统计数据失败:', error);
  }
});</script>

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






