<template>
  <div class="app-container">
    <div class="main-content">
      <!-- 群聊管理与数据收集整合区域 -->
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <el-icon><Setting /></el-icon>
                  <span>群聊管理与数据收集</span>
                </div>
                <div class="header-status" v-if="managementEnabled">
                  <el-tag :type="dataCollectionEnabled ? 'success' : 'info'">
                    {{ dataCollectionEnabled ? '收集中' : '未启用' }}
                  </el-tag>
                </div>
              </div>
            </template>

            <el-form label-position="top">
              <!-- 群聊管理部分 -->
              <el-form-item label="群聊管理">
                <el-row :gutter="16" align="middle">
                  <el-col :span="16">
                    <el-input
                      v-model="selectedGroup"
                      placeholder="输入要管理的群聊名称"
                      clearable
                      @clear="handleClearGroup"
                    >
                      <template #prefix>
                        <el-icon><View /></el-icon>
                      </template>
                    </el-input>
                  </el-col>
                  <el-col :span="8">
                    <el-row align="middle" :gutter="8">
                      <el-col :span="10" class="switch-label">管理状态</el-col>
                      <el-col :span="14">
                        <el-switch
                          v-model="managementEnabled"
                          inline-prompt
                          active-text="启用"
                          inactive-text="禁用"
                          @change="handleManagementChange"
                        />
                      </el-col>
                    </el-row>
                  </el-col>
                </el-row>
              </el-form-item>

              <!-- 群消息数据收集部分 -->
              <el-divider />
              <el-form-item>
                <template #label>
                  <el-row justify="space-between" align="middle">
                    <span>群消息收集</span>
                    <el-switch
                      v-model="dataCollectionEnabled"
                      :disabled="!managementEnabled"
                      inline-prompt
                      active-text="启用"
                      inactive-text="禁用"
                      @change="handleDataCollectionChange"
                    />
                  </el-row>
                </template>
                <el-row :gutter="12">
                  <el-col :span="8">
                    <el-button type="success" @click="handleViewCollectionData" :disabled="!dataCollectionEnabled" style="width: 100%">
                      <el-icon><View /></el-icon>
                      查看收集数据
                    </el-button>
                  </el-col>
                  <el-col :span="8">
                    <el-button type="info" @click="handleConfigureCollection" :disabled="!managementEnabled" style="width: 100%">
                      <el-icon><Setting /></el-icon>
                      配置收集规则
                    </el-button>
                  </el-col>
                  <el-col :span="8">
                    <el-button type="primary" @click="showTemplateDialog" :disabled="!managementEnabled" style="width: 100%">
                      <el-icon><Edit /></el-icon>
                      设置模板
                    </el-button>
                  </el-col>
                </el-row>
              </el-form-item>


            </el-form>
          </el-card>
        </el-col>
      </el-row>

      <!-- 舆情监控区域 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <el-icon><View /></el-icon>
                  <span>舆情监控</span>
                </div>
                <div class="header-status" v-if="managementEnabled">
                  <el-tag :type="monitoringEnabled ? 'success' : 'info'">
                    {{ monitoringEnabled ? '监控中' : '未开启' }}
                  </el-tag>
                </div>
              </div>
            </template>

            <el-form label-position="top">
              <el-form-item>
                <el-card shadow="never">
                  <template #header>
                    <el-row justify="space-between" align="middle">
                      <div>
                        <h4 style="margin: 0">舆情监控状态</h4>
                        <p style="margin: 5px 0 0 0; color: #909399; font-size: 14px">实时监控群聊中的敏感信息</p>
                      </div>
                      <el-switch 
                        v-model="monitoringEnabled" 
                        @change="handleMonitoringChange" 
                        :disabled="!managementEnabled"
                        size="large"
                      />
                    </el-row>
                  </template>
                </el-card>
              </el-form-item>

              <el-form-item>
                <template #label>
                  <el-row justify="space-between" align="middle">
                    <span>敏感词设置</span>
                    <span class="word-count" v-if="sensitiveWords">
                      已添加 {{ wordCount }} 个敏感词
                    </span>
                  </el-row>
                </template>
                <el-input 
                  v-model="sensitiveWords" 
                  type="textarea" 
                  :rows="3" 
                  placeholder="输入敏感词，多个敏感词用逗号分隔"
                  :disabled="false"
                />
                <div class="word-tips">
                  <el-text type="info" size="small">提示：添加敏感词后，系统将自动监控群聊中包含这些词的消息</el-text>
                </div>
                <div class="action-buttons" style="margin-top: 10px;">
                  <el-button type="primary" @click="saveSensitiveWords" :disabled="!sensitiveWords.trim()">
                    <el-icon><Check /></el-icon>
                    保存敏感词
                  </el-button>
                  <el-button @click="resetSensitiveWords">
                    <el-icon><Refresh /></el-icon>
                    重置
                  </el-button>
                </div>
              </el-form-item>

              <el-form-item v-if="monitoringEnabled && monitoringResults.length > 0">
                <template #label>
                  <h4 style="margin: 0">监控结果</h4>
                </template>
                <el-table :data="monitoringResults" style="width: 100%" border size="small">
                  <el-table-column prop="time" label="时间" width="160" />
                  <el-table-column prop="sender" label="发送者" width="100" />
                  <el-table-column prop="content" label="消息内容" show-overflow-tooltip />
                  <el-table-column prop="matchedWords" label="匹配词" width="120">
                    <template #default="scope">
                      <el-tag type="danger" size="small">{{ scope.row.matchedWords }}</el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>

      <!-- 报表生成区域 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <el-icon><Edit /></el-icon>
                  <span>报表生成</span>
                </div>
              </div>
            </template>

            <el-form label-position="top">
              <el-form-item>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="报表类型">
                      <el-select v-model="reportType" placeholder="选择报表类型" :disabled="!managementEnabled" style="width: 100%">
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
                        :disabled="!managementEnabled"
                        style="width: 100%"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-form-item>

              <el-form-item>
                <el-row :gutter="12">
                  <el-col :span="12">
                    <el-button type="primary" @click="generateReport" :disabled="!managementEnabled || !reportType || !reportDateRange" style="width: 100%">
                      <el-icon><View /></el-icon> 生成报表
                    </el-button>
                  </el-col>
                  <el-col :span="12">
                    <el-button type="success" @click="exportReport" :disabled="!reportGenerated || !managementEnabled" style="width: 100%">
                      <el-icon><Setting /></el-icon> 导出报表
                    </el-button>
                  </el-col>
                </el-row>
              </el-form-item>

              <el-form-item v-if="reportGenerated">
                <el-card shadow="never">
                  <template #header>
                    <el-row justify="space-between" align="middle">
                      <h3 style="margin: 0">报表预览 - {{ getReportTypeName(reportType) }}</h3>
                      <el-text type="info">{{ reportDateRange[0] }} 至 {{ reportDateRange[1] }}</el-text>
                    </el-row>
                  </template>
                  <el-table :data="reportData" style="width: 100%" border>
                    <el-table-column prop="category" label="类别" width="180" />
                    <el-table-column prop="value" label="数值" width="120" />
                    <el-table-column prop="description" label="描述" />
                    <el-table-column label="趋势" width="100">
                      <template #default="scope">
                        <el-tag :type="getTrendType(scope.row.trend)" size="small">
                          {{ scope.row.trend }}
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
      title="设置收集模板"
      width="60%"
    >
      <el-form label-position="top">
        <el-form-item label="原始消息内容">
          <el-input
            v-model="originalMessage"
            type="textarea"
            :rows="4"
            placeholder="请输入原始消息示例"
          />
        </el-form-item>
        
        <el-form-item label="需要从中提取出来的内容">
          <el-input
            v-model="collectionTemplate"
            type="textarea"
            :rows="4"
            placeholder="请输入需要提取的内容，例如：姓名,电话,地址"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="autoLearnPattern" :disabled="!originalMessage.trim() || !collectionTemplate.trim()">
            <el-icon><View /></el-icon> 开始学习
          </el-button>
        </el-form-item>
        
        <el-form-item v-if="generatedRegex" label="正则表达式">
          <el-input
            v-model="generatedRegex"
            type="textarea"
            :rows="3"
            placeholder="生成的正则表达式将显示在这里，您可以手动编辑"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="templateDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveCollectionTemplate" :disabled="!generatedRegex">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 收集数据预览对话框 -->
    <el-dialog
      v-model="dataPreviewVisible"
      title="收集数据预览"
      width="70%"
    >
      <el-form label-position="top">
        <el-form-item>
          <el-row :gutter="12">
            <el-col :span="8">
              <el-date-picker 
                v-model="collectionDate" 
                type="date" 
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                @change="handleDateChange"
                style="width: 100%"
              />
            </el-col>
            <el-col :span="8">
              <el-select v-model="tableGroupFilter" placeholder="选择群聊" @change="handleGroupFilterChange" style="width: 100%">
                <el-option
                  v-for="group in availableGroups"
                  :key="group"
                  :label="group"
                  :value="group"
                />
              </el-select>
            </el-col>
            <el-col :span="8">
              <el-button @click="refreshData" style="width: 100%">
                <el-icon><View /></el-icon> 刷新
              </el-button>
            </el-col>
          </el-row>
        </el-form-item>
        
        <el-form-item>
          <el-table :data="collectedData" style="width: 100%" border v-loading="dataLoading" stripe>
            <el-table-column prop="time" label="时间" width="180" sortable />
            <el-table-column prop="sender" label="发送者" width="120" />
            <el-table-column prop="content" label="消息内容" show-overflow-tooltip />
            <el-table-column prop="type" label="类型" width="100">
              <template #default="scope">
                <el-tag :type="getMessageTypeTag(scope.row.type)" size="small">
                  {{ scope.row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button @click="viewMessageDetail(scope.row)" type="primary" link>查看</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="table-footer" v-if="collectedData.length > 0">
            <el-pagination
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              :current-page="currentPage"
              :page-sizes="[10, 20, 50, 100]"
              :page-size="pageSize"
              layout="total, sizes, prev, pager, next, jumper"
              :total="totalDataCount"
              small
            />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dataPreviewVisible = false">关闭</el-button>
          <el-button type="primary" @click="exportCollectedData">导出数据</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 消息详情对话框 -->
    <el-dialog
      v-model="messageDetailVisible"
      title="消息详情"
      width="40%"
    >
      <el-descriptions :column="1" border v-if="selectedMessage">
        <el-descriptions-item label="发送时间">{{ selectedMessage.time }}</el-descriptions-item>
        <el-descriptions-item label="发送者">{{ selectedMessage.sender }}</el-descriptions-item>
        <el-descriptions-item label="消息类型">{{ selectedMessage.type }}</el-descriptions-item>
        <el-descriptions-item label="消息内容">
          <div class="detail-content">{{ selectedMessage.content }}</div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="messageDetailVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import { View, Setting, Edit, Check, Refresh } from '@element-plus/icons-vue'

// ===== 响应式数据 =====
const selectedGroup = ref('')
const managementEnabled = ref(false)
const dataCollectionEnabled = ref(false)
const collectionDate = ref('')
const tableGroupFilter = ref('')
const availableGroups = ref(['测试群1', '测试群2', '工作群', '家庭群'])
const collectedData = ref([
  { time: '2023-06-01 10:30:25', sender: '张三', content: '大家好，今天天气不错', type: '文本' },
  { time: '2023-06-01 10:32:15', sender: '李四', content: '[图片]', type: '图片' },
  { time: '2023-06-01 10:35:42', sender: '王五', content: '明天有会议吗？', type: '文本' },
  { time: '2023-06-01 11:15:30', sender: '赵六', content: '收到，我会准时参加', type: '文本' },
  { time: '2023-06-01 11:20:45', sender: '钱七', content: '[文件]会议议程.docx', type: '文件' }
])
const hasCollectedData = ref(true)
const dataLoading = ref(false)
const sensitiveWords = ref('')
const monitoringEnabled = ref(false)
const monitoringResults = ref([
  { time: '2023-06-01 10:35:42', sender: '王五', content: '明天有会议吗？', matchedWords: '会议' }
])
const templateDialogVisible = ref(false)
const collectionTemplate = ref('')
const originalMessage = ref('')
const generatedRegex = ref('')
const reportType = ref('')
const reportDateRange = ref([])
const reportGenerated = ref(false)
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
const totalDataCount = ref(5)
const dataPreviewVisible = ref(false)

// ===== 计算属性 =====
const wordCount = computed(() => {
  if (!sensitiveWords.value.trim()) return 0
  return sensitiveWords.value.split(',').filter(word => word.trim()).length
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

const handleManagementChange = (value) => {
  if (!selectedGroup.value) {
    ElMessage.warning('请先输入群聊名称')
    managementEnabled.value = false
    return
  }
  
  ElMessage.success(`群聊管理已${value ? '开启' : '关闭'}`)
  
  if (!value) {
    dataCollectionEnabled.value = false
    monitoringEnabled.value = false
  }
}

const handleDataCollectionChange = (value) => {
  if (!managementEnabled.value) {
    ElMessage.warning('请先开启群聊管理')
    dataCollectionEnabled.value = false
    return
  }
  
  ElMessage.success(`数据收集已${value ? '开启' : '关闭'}`)
  
  if (value) {
    refreshData()
  }
}

const handleMonitoringChange = (value) => {
  if (!managementEnabled.value) {
    ElMessage.warning('请先开启群聊管理')
    monitoringEnabled.value = false
    return
  }
  
  if (!sensitiveWords.value.trim()) {
    ElMessage.warning('请输入敏感词')
    monitoringEnabled.value = false
    return
  }
  
  ElMessage.success(`舆情监控已${value ? '开启' : '关闭'}`)
  
  if (value) {
    monitoringResults.value = []
  }
}

const handleDateChange = (value) => {
  if (!value) return
  refreshData()
  ElMessage.info(`已选择日期: ${value}`)
}

const handleGroupFilterChange = (value) => {
  if (!value) return
  refreshData()
  ElMessage.info(`已选择群聊: ${value}`)
}

const refreshData = () => {
  if (!managementEnabled.value) return
  
  dataLoading.value = true
  
  setTimeout(() => {
    dataLoading.value = false
    hasCollectedData.value = true
    ElMessage.success('数据已刷新')
  }, 1000)
}

const viewMessageDetail = (message) => {
  selectedMessage.value = message
  messageDetailVisible.value = true
}

const showTemplateDialog = () => {
  templateDialogVisible.value = true
}

const saveCollectionTemplate = () => {
  if (!collectionTemplate.value.trim()) {
    ElMessage.warning('请输入收集模板')
    return
  }
  
  ElMessage.success('模板保存成功')
  templateDialogVisible.value = false
}

const autoLearnPattern = () => {
  if (!originalMessage.value.trim()) {
    ElMessage.warning('请输入原始消息示例')
    return
  }
  
  if (!collectionTemplate.value.trim()) {
    ElMessage.warning('请输入要收集的数据')
    return
  }
  
  setTimeout(() => {
    const fields = collectionTemplate.value.split(',').map(field => field.trim())
    const message = originalMessage.value
    const extractedValues = {}
    let regexPattern = ''
    
    if (fields.includes('姓名') || fields.includes('名字')) {
      const nameMatch = message.match(/我叫([^\s，,]+)/)
      if (nameMatch) {
        extractedValues['姓名'] = nameMatch[1]
      }
    }
    
    if (fields.includes('电话') || fields.includes('手机')) {
      const phoneMatch = message.match(/(1[3-9]\d{9})/)
      if (phoneMatch) {
        extractedValues['电话'] = phoneMatch[1]
      }
    }
    
    if (fields.includes('地址')) {
      const addressMatch = message.match(/住在([^\s，,]+)/)
      if (addressMatch) {
        extractedValues['地址'] = addressMatch[1]
      }
    }
    
    if (Object.keys(extractedValues).length === 0) {
      const parts = message.split(/[，,]/).map(part => part.trim())
      fields.forEach((field, index) => {
        if (index < parts.length) {
          extractedValues[field] = parts[index]
        }
      })
    }
    
    if (Object.keys(extractedValues).length > 0) {
      const patterns = []
      
      if (extractedValues['姓名']) {
        patterns.push(`姓名[:：]?\\s*([\\u4e00-\\u9fa5]{${extractedValues['姓名'].length}})`)
      }
      
      if (extractedValues['电话']) {
        patterns.push(`电话[:：]?\\s*(${extractedValues['电话']})`)
      }
      
      if (extractedValues['地址']) {
        patterns.push(`地址[:：]?\\s*([\\u4e00-\\u9fa5\\d]+)`)
      }
      
      Object.keys(extractedValues).forEach(field => {
        if (!['姓名', '电话', '地址'].includes(field)) {
          const value = extractedValues[field]
          if (/^\d+$/.test(value)) {
            patterns.push(`${field}[:：]?\\s*(\\d+)`)
          } else if (/^[\u4e00-\u9fa5]+$/.test(value)) {
            patterns.push(`${field}[:：]?\\s*([\\u4e00-\\u9fa5]+)`)
          } else {
            patterns.push(`${field}[:：]?\\s*([^\\s，,]+)`)
          }
        }
      })
      
      regexPattern = patterns.join('\\s*[，,]\\s*')
    } else {
      regexPattern = '(.+)'
    }
    
    generatedRegex.value = regexPattern
    ElMessage.success('正则表达式生成成功')
  }, 1000)
}

const handleViewCollectionData = () => {
  dataPreviewVisible.value = true
  refreshData()
}

const handleConfigureCollection = () => {
  showTemplateDialog()
}

const exportCollectedData = () => {
  if (!managementEnabled.value) {
    ElMessage.warning('请先开启群聊管理')
    return
  }
  
  if (!hasCollectedData.value) {
    ElMessage.warning('没有可导出的数据')
    return
  }
  
  ElMessage.success('数据导出成功')
}

const generateReport = () => {
  if (!managementEnabled.value) {
    ElMessage.warning('请先开启群聊管理')
    return
  }
  
  if (!reportType.value) {
    ElMessage.warning('请选择报表类型')
    return
  }
  
  if (!reportDateRange.value || reportDateRange.value.length !== 2) {
    ElMessage.warning('请选择时间范围')
    return
  }
  
  reportGenerated.value = true
  ElMessage.success('报表生成成功')
}

const exportReport = () => {
  if (!reportGenerated.value) {
    ElMessage.warning('请先生成报表')
    return
  }
  
  ElMessage.success('报表导出成功')
}

const handleSizeChange = (val) => {
  pageSize.value = val
  refreshData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  refreshData()
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

// 新增：保存敏感词功能
const saveSensitiveWords = () => {
  if (!sensitiveWords.value.trim()) {
    ElMessage.warning('请输入敏感词')
    return
  }
  
  // 这里可以添加保存到后端的逻辑
  ElMessage.success(`敏感词保存成功，共 ${wordCount.value} 个`)
}

// 新增：重置敏感词功能
const resetSensitiveWords = () => {
  sensitiveWords.value = ''
  ElMessage.info('敏感词已重置')
}

// ===== 生命周期钩子 =====
// 组件挂载时初始化
onMounted(() => {
  // 这里可以添加初始化逻辑
})
</script>

<style scoped>
.app-container {
  padding: 20px;
  background-color: var(--el-bg-color-page);
  min-height: 100vh;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
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
  font-size: 16px;
}

.header-status {
  display: flex;
  align-items: center;
}

.switch-label {
  font-weight: 500;
  color: var(--el-text-color-regular);
}

.word-count {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.word-tips {
  margin-top: 8px;
}

.table-footer {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.detail-content {
  background-color: var(--el-fill-color-light);
  padding: 12px;
  border-radius: var(--el-border-radius-base);
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-container {
    padding: 10px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>
