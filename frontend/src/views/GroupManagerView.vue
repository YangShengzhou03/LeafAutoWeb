<template>
  <div class="auto-info-container">
    <div class="main-content">
      <!-- 数据收集配置 -->
      <el-row :gutter="24">
        <el-col :span="24">
          <el-card shadow="hover" class="group-config-card">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span>群聊管家配置</span>
                </div>
              </div>
            </template>

            <el-form label-position="top" class="data-collection-form">
              <el-row :gutter="20" class="data-collection-row">
                <el-col :span="24">
                  <el-form-item label="系统功能控制" class="inline-form-item">
                    <div>
                      <el-input v-model="contactPerson" placeholder="输入待管理群聊" class="contact-input"></el-input>
                    </div>

                    <div class="controls-row inline-controls">
                      <!-- 管理状态开关 - 保持原生样式 -->
                      <div class="status-control">
                        <el-switch v-model="groupManagementStatus" active-color="#409eff" inactive-color="#dcdfe6"
                          @change="handleSwitchChange" :loading="isTakeoverLoading"></el-switch>
                        <span class="status-text">{{ groupManagementStatus ? '管理已启用' : '管理未开启' }}</span>
                      </div>

                      <!-- 数据收集开关 - 保持原生样式 -->
                      <div class="status-control">
                        <el-switch v-model="dataCollectionEnabled" active-color="#409eff" inactive-color="#dcdfe6"
                          @change="handleDataCollectionChange" :disabled="!groupManagementStatus"></el-switch>
                        <span class="status-text">{{ dataCollectionEnabled ? '数据收集已启用' : '数据收集未开启' }}</span>
                      </div>

                      <!-- 舆情监控开关 - 保持原生样式 -->
                      <div class="status-control">
                        <el-switch v-model="monitoringEnabled" active-color="#409eff" inactive-color="#dcdfe6"
                          @change="handleMonitoringChange" :disabled="!groupManagementStatus"></el-switch>
                        <span class="status-text">{{ monitoringEnabled ? '舆情监控已启用' : '舆情监控未开启' }}</span>
                      </div>
                    </div>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>

            <!-- 收集规则部分 -->
            <el-form label-position="top" class="rules-form">
              <el-form-item label="收集规则">
                <div class="rule-actions">
                  <el-button type="primary" size="mid" @click="showAddRuleDialog">
                    添加规则
                  </el-button>
                  <el-button size="mid" @click="showRegexHelp">
                    <el-icon>
                      <QuestionFilled />
                    </el-icon>
                    功能帮助
                  </el-button>
                </div>

                <!-- 正则规则表格 -->
                <el-table :data="regexRules" class="rules-table" empty-text="暂无规则，快添加试试吧" stripe>
                  <el-table-column prop="originalMessage" label="原始消息" width="250" />
                  <el-table-column prop="pattern" label="正则表达式" />
                  <el-table-column prop="extractedContent" label="提取内容" width="200" />
                  <el-table-column label="操作" width="120" align="center">
                    <template #default="scope">
                      <el-button type="danger" size="small" @click="deleteRegexRule(scope.$index)">
                        <el-icon>
                          <Delete />
                        </el-icon>
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
          <el-card shadow="hover" class="monitoring-config-card">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span>舆情监控</span>
                </div>
                <div class="header-status">
                  <el-tag :type="monitoringEnabled ? 'success' : 'info'" effect="light" size="mid">
                    {{ monitoringEnabled ? '监控中' : '未启用' }}
                  </el-tag>
                </div>
              </div>
            </template>

            <el-form label-position="top" class="monitoring-form">
              <!-- 敏感词管理区域 -->
              <el-form-item label="敏感词管理" class="monitoring-form-item">

                <!-- 添加敏感词区域 - 优化布局 -->
                <div class="sensitive-word-input-container">
                  <el-input v-model="newSensitiveWord" placeholder="输入敏感词" clearable @keyup.enter="addSensitiveWord"
                    size="mid" class="sensitive-word-input">
                    <template #prefix>
                      <el-icon>
                        <Key />
                      </el-icon>
                    </template>
                  </el-input>
                  <el-button type="primary" @click="addSensitiveWord" :disabled="!newSensitiveWord.trim()"
                    class="add-word-btn" size="mid">
                    <el-icon>
                      <Plus />
                    </el-icon>
                    添加
                  </el-button>
                </div>

                <!-- 敏感词列表区域 - 优化展示 -->
                <div class="sensitive-words-wrapper">
                  <div class="sensitive-words-list">
                    <transition-group name="fade-in" tag="div">
                      <el-tag v-for="(word, index) in sensitiveWordsList" :key="index" closable
                        @close="removeSensitiveWord(index)" type="danger" effect="plain" size="mid"
                        class="sensitive-word-tag">
                        <el-icon>
                          <Key />
                        </el-icon>
                        {{ word }}
                      </el-tag>
                    </transition-group>
                  </div>
                </div>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>

      <!-- 数据展示区域 -->
      <el-row :gutter="24">
        <el-col :span="24">
          <el-card shadow="hover" class="data-display-card">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <span>收集数据</span>
                </div>
                <div class="header-actions filter-row">
                  <el-select v-model="selectedGroupFilter" placeholder="筛选群聊" size="mid" class="filter-select"
                    clearable>
                    <el-option label="所有群聊" value="" />
                    <el-option v-for="group in availableGroups" :key="group" :label="group" :value="group" />
                  </el-select>
                  <el-date-picker v-model="dateRangeFilter" type="daterange" range-separator="至"
                    start-placeholder="开始日期" end-placeholder="结束日期" size="mid" class="date-picker-filter"
                    format="YYYY-MM-DD" value-format="YYYY-MM-DD" clearable />
                  <el-button type="primary" link @click="refreshData" :loading="dataLoading" class="refresh-btn">
                    <el-icon>
                      <Refresh />
                    </el-icon>
                    刷新
                  </el-button>
                  <el-button type="success" @click="exportCollectedData" :loading="exportLoading" class="export-btn">
                    <el-icon>
                      <Download />
                    </el-icon>
                    导出数据
                  </el-button>
                </div>
              </div>
            </template>

            <!-- 表格内容 -->
            <el-table :data="currentPageData" class="data-table" border v-loading="dataLoading" stripe max-height="400"
              @row-click="viewMessageDetail"
              :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#606266', fontWeight: '600' }">
              <el-table-column prop="time" label="时间" width="160" sortable>
                <template #default="{ row }">
                  <div class="time-cell">
                    <el-icon>
                      <Clock />
                    </el-icon>
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
              <el-table-column prop="group" label="群聊" width="120">
                <template #default="{ row }">
                  <div class="group-cell">
                    <el-icon>
                      <ChatDotRound />
                    </el-icon>
                    {{ row.group || '未知群聊' }}
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
              <el-table-column prop="type" label="提取数据" min-width="120">
                <template #default="{ row }">
                  <div class="extracted-content-status">
                    <el-icon class="success-icon" v-if="row.extractedContent && row.extractedContent !== '无提取内容'">
                      <Check />
                    </el-icon>
                    <el-icon class="warning-icon" v-else>
                      <InfoFilled />
                    </el-icon>
                    <span>{{ row.extractedContent || '无提取内容' }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link @click.stop="viewMessageDetail(row)" class="detail-btn">
                    详情
                  </el-button>
                  <el-button type="danger" link @click.stop="deleteCollectedMessage(row)" class="delete-btn">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="table-footer" v-if="collectedData.length > 0">
              <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange"
                :current-page="currentPage" :page-sizes="[5, 10, 20, 50]" :page-size="pageSize"
                layout="total, sizes, prev, pager, next, jumper" :total="totalDataCount" mid background
                class="pagination" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 收集模板对话框 -->
    <el-dialog v-model="templateDialogVisible" title="智能模板配置" width="60%" :close-on-click-modal="false">
      <el-form label-position="top">
        <el-form-item label="原始消息内容">
          <el-input v-model="originalMessage" type="textarea" :rows="4"
            placeholder="请输入原始消息示例，例如：'我叫张三，电话13800138000，住在北京市朝阳区'" show-word-limit maxlength="500" />
        </el-form-item>

        <el-form-item label="需要从中提取出来的内容">
          <el-input v-model="collectionTemplate" type="textarea" :rows="4"
            placeholder="请输入需要提取的内容，用逗号分隔，例如：张三，13800138000，北京市朝阳区" show-word-limit maxlength="200" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="autoLearnPattern"
            :disabled="!originalMessage.trim() || !collectionTemplate.trim()" :loading="patternLearning"
            class="learn-button">
            <el-icon>
              <MagicStick />
            </el-icon>
            智能学习
          </el-button>

          <el-button type="info" @click="showPatternHelp" link class="help-button">
            <el-icon>
              <QuestionFilled />
            </el-icon>
            如何使用？
          </el-button>
        </el-form-item>

        <el-form-item v-if="generatedRegex" label="生成的正则表达式">
          <el-input v-model="generatedRegex" type="textarea" :rows="3" placeholder="生成的正则表达式将显示在这里，您可以手动编辑"
            class="regex-input" />
          <div class="regex-tips">
            <el-icon>
              <InfoFilled />
            </el-icon>
            系统已自动学习并生成匹配规则，您可以根据需要进一步调整
          </div>
        </el-form-item>

        <el-form-item v-if="extractedValues && Object.keys(extractedValues).length > 0" label="提取结果预览">
          <el-card shadow="never">
            <el-descriptions :column="2" border>
              <el-descriptions-item v-for="(value, key) in extractedValues" :key="key" :label="key">
                {{ value }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="templateDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveCollectionTemplate" :disabled="!generatedRegex" class="save-button">
            保存模板
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 消息详情对话框 -->
    <el-dialog v-model="messageDetailVisible" title="消息详情" width="50%">
      <el-descriptions :column="1" border v-if="selectedMessage" class="message-details">
        <el-descriptions-item label="发送时间">
          <div class="detail-item">
            <el-icon>
              <Clock />
            </el-icon>
            {{ selectedMessage.time }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="发送者">
          <div class="detail-item">
            <el-avatar :size="32" :src="getAvatarUrl(selectedMessage.sender)" />
            <span>{{ selectedMessage.sender }}</span>
          </div>
        </el-descriptions-item>

        <el-descriptions-item label="消息内容">
          <div class="detail-content">{{ selectedMessage.content }}</div>
        </el-descriptions-item>

        <el-descriptions-item label="提取内容">
          <el-tag :type="getMessageTypeTag(selectedMessage.type)" size="mid">
            {{ selectedMessage.type }}
          </el-tag>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import {
  Plus, Key, Refresh, Clock, Document,
  QuestionFilled, InfoFilled, MagicStick, Picture,
  Message, Microphone, VideoCamera, Delete, Check, Download
} from '@element-plus/icons-vue'

// 响应式数据
const dataCollectionEnabled = ref(false)
const groupManagementStatus = ref(false) // 群聊管理状态（原aiStatus）
const isTakeoverLoading = ref(false) // 接管加载状态
const contactPerson = ref('文件传输助手') // 接管联系人，设置默认值
const regexRules = ref([])
const collectedData = ref([])
const dataLoading = ref(false)
const exportLoading = ref(false) // 导出加载状态
const newSensitiveWord = ref('')
const sensitiveWordsList = ref([])
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
const availableGroups = ref([])

// 计算属性
const filteredData = computed(() => {
  if (!Array.isArray(collectedData.value)) {
    console.warn('collectedData不是数组', collectedData.value)
    return []
  }

  let filtered = [...collectedData.value]

  // 群聊筛选
  if (selectedGroupFilter.value && selectedGroupFilter.value.trim()) {
    filtered = filtered.filter(item => {
      if (!item || !item.group) return false
      return item.group.includes(selectedGroupFilter.value)
    })
  }

  // 日期范围筛选
  if (dateRangeFilter.value && Array.isArray(dateRangeFilter.value) && dateRangeFilter.value.length === 2) {
    const [startDate, endDate] = dateRangeFilter.value
    if (startDate && endDate) {
      filtered = filtered.filter(item => {
        if (!item || !item.time) return false
        // 确保time是字符串类型
        const timeStr = String(item.time || '')
        if (!timeStr) return false
        const itemDate = timeStr.split(' ')[0] // 提取日期部分
        return itemDate >= startDate && itemDate <= endDate
      })
    }
  }

  return filtered
})

const currentPageData = computed(() => {
  if (!Array.isArray(filteredData.value)) {
    return []
  }

  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

const totalDataCount = computed(() => {
  if (!Array.isArray(filteredData.value)) {
    return 0
  }

  return filteredData.value.length
})

// 事件处理
// 调用后端API选择群聊
const selectGroupAPI = async (groupName) => {
  try {
    const response = await axios.post('/api/group/select', {
      group_name: groupName
    })
    if (response.data.success) {
      ElMessage.success('群聊选择成功')
    } else {
      ElMessage.error(response.data.error || '群聊选择失败')
    }
  } catch (error) {
    console.error('群聊选择失败:', error)
  }
}

// 调用后端API开始群聊管理
const startGroupManagementAPI = async (groupName, settings) => {
  try {
    const response = await axios.post('/api/group/start-management', {
      group_name: groupName,
      settings: settings
    })
    return response.data
  } catch (error) {
    console.error('启动群聊管理失败:', error)
    throw error
  }
}

// 调用后端API停止群聊管理
const stopGroupManagementAPI = async (groupName) => {
  try {
    const response = await axios.post('/api/group/stop-management', {
      group_name: groupName
    })
    return response.data
  } catch (error) {
    console.error('停止群聊管理失败:', error)
    throw error
  }
}

// 调用后端API更新配置状态
const updateConfigStatusAPI = async (configData) => {
  try {
    const response = await axios.post('/api/group/update-config-status', configData)
    return response.data
  } catch (error) {
    console.error('更新配置状态失败:', error)
    throw error
  }
}

const handleSwitchChange = (enabled) => {
  isTakeoverLoading.value = true

  if (enabled && !contactPerson.value.trim()) {
    isTakeoverLoading.value = false
    ElMessage.warning('请输入接管联系人姓名')
    groupManagementStatus.value = false
    return
  }

  if (enabled) {
    // 准备设置对象
    const settings = {
      data_collection_enabled: dataCollectionEnabled.value,
      monitoring_enabled: monitoringEnabled.value,
      sensitive_words: sensitiveWordsList.value,
      min_reply_interval: 0 // 默认设置
    }

    // 调用后端API
    startGroupManagementAPI(contactPerson.value, settings)
      .then(result => {
        isTakeoverLoading.value = false
        if (result.success) {
          ElMessage.success(result.message || '管理已启用')
          // 选择群聊
          selectGroupAPI(contactPerson.value)
        } else {
          ElMessage.error(result.error || '启用管理失败')
          groupManagementStatus.value = false
        }
      })
      .catch(error => {
        isTakeoverLoading.value = false
        ElMessage.error('启用管理失败: ' + (error.message || '未知错误'))
        groupManagementStatus.value = false
      })
  } else {
    // 调用后端API停止群聊管理
    stopGroupManagementAPI(contactPerson.value)
      .then(result => {
        isTakeoverLoading.value = false
        if (result.success) {
          ElMessage.success(result.message || '管理未开启')
        } else {
          ElMessage.error(result.error || '禁用管理失败')
          groupManagementStatus.value = true // 恢复状态
        }
      })
      .catch(error => {
        isTakeoverLoading.value = false
        ElMessage.error('禁用管理失败: ' + (error.message || '未知错误'))
        groupManagementStatus.value = true // 恢复状态
      })
  }
}

const handleDataCollectionChange = (enabled) => {
  if (enabled && !groupManagementStatus.value) {
    ElMessage.warning('请先启用管理功能')
    dataCollectionEnabled.value = false
    return
  }

  // 更新配置状态到后端
  updateConfigStatusAPI({
    data_collection_enabled: enabled,
    monitoring_enabled: monitoringEnabled.value
  })
    .then(result => {
      if (result.success) {
        if (enabled) {
          ElMessage.success('数据收集功能已启用')
        } else {
          ElMessage.info('数据收集功能未开启')
        }
      } else {
        ElMessage.error(result.error || '更新配置状态失败')
        dataCollectionEnabled.value = !enabled // 恢复原状态
      }
    })
    .catch(error => {
      console.error('更新配置状态失败:', error)
      ElMessage.error('更新配置状态失败')
      dataCollectionEnabled.value = !enabled // 恢复原状态
    })
}

const handleMonitoringChange = (enabled) => {
  if (enabled && !groupManagementStatus.value) {
    ElMessage.warning('请先启用管理功能')
    monitoringEnabled.value = false
    return
  }

  // 更新配置状态到后端
  updateConfigStatusAPI({
    data_collection_enabled: dataCollectionEnabled.value,
    monitoring_enabled: enabled
  })
    .then(result => {
      if (result.success) {
        if (enabled) {
          ElMessage.success('舆情监控功能已启用')
        } else {
          ElMessage.info('舆情监控功能未开启')
        }
      } else {
        ElMessage.error(result.error || '更新配置状态失败')
        monitoringEnabled.value = !enabled // 恢复原状态
      }
    })
    .catch(error => {
      console.error('更新配置状态失败:', error)
      ElMessage.error('更新配置状态失败')
      monitoringEnabled.value = !enabled // 恢复原状态
    })
}

const showAddRuleDialog = () => {
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

  // 保存要删除的规则用于回滚
  const removedRule = regexRules.value[index]

  ElMessageBox.confirm(
    `确定要删除这条规则吗？\n\n原始消息：${regexRules.value[index].originalMessage}\n正则表达式：${regexRules.value[index].pattern}`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 从本地数组中删除
    regexRules.value.splice(index, 1)

    // 调用后端API保存到文件
    saveRegexRulesAPI(regexRules.value)
      .then(() => {
        ElMessage.success('规则已删除并已保存')
      })
      .catch(error => {
        ElMessage.error(`保存失败：${error.message}`)
        // 如果保存失败，回滚本地操作
        regexRules.value.splice(index, 0, removedRule)
      })
  }).catch(() => {
    // 用户取消删除
  })
}

// 修改后的添加敏感词方法 - 调用后端API保存
const addSensitiveWord = () => {
  const word = newSensitiveWord.value.trim()

  if (!word) {
    ElMessage.warning('请输入敏感词')
    return
  }

  if (!Array.isArray(sensitiveWordsList.value)) {
    sensitiveWordsList.value = []
  }

  if (sensitiveWordsList.value.includes(word)) {
    ElMessage.warning('该敏感词已存在')
    return
  }

  // 添加到本地数组
  sensitiveWordsList.value.push(word)
  newSensitiveWord.value = ''

  // 调用后端API保存到文件
  saveSensitiveWordsAPI(sensitiveWordsList.value)
    .then(() => {
      ElMessage.success('敏感词添加成功并已保存')
    })
    .catch(error => {
      ElMessage.error(`保存失败：${error.message}`)
      // 如果保存失败，回滚本地操作
      sensitiveWordsList.value.pop()
    })
}

// 修改后的删除敏感词方法 - 调用后端API保存
const removeSensitiveWord = (index) => {
  if (!Array.isArray(sensitiveWordsList.value)) {
    console.warn('sensitiveWordsList不是数组')
    return
  }

  if (index < 0 || index >= sensitiveWordsList.value.length) {
    console.warn('无效的索引:', index)
    return
  }

  // 保存要删除的单词用于回滚
  const removedWord = sensitiveWordsList.value[index]

  // 从本地数组中删除
  sensitiveWordsList.value.splice(index, 1)

  // 调用后端API保存到文件
  saveSensitiveWordsAPI(sensitiveWordsList.value)
    .then(() => {
      ElMessage.info(`敏感词 "${removedWord}" 已删除并已保存`)
    })
    .catch(error => {
      ElMessage.error(`保存失败：${error.message}`)
      // 如果保存失败，回滚本地操作
      sensitiveWordsList.value.splice(index, 0, removedWord)
    })
}

// 其他方法保持不变
const refreshData = () => {
  dataLoading.value = true

  // 调用API获取最新数据，保持当前日期范围筛选
  getCollectedDataAPI(selectedGroupFilter.value, dateRangeFilter.value)
    .then(data => {
      collectedData.value = data
      ElMessage.success('数据已刷新')
    })
    .catch(error => {
      ElMessage.error(`刷新数据失败：${error}`)
    })
    .finally(() => {
      dataLoading.value = false
    })
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



// 删除已收集的消息
const deleteCollectedMessage = (row) => {
  ElMessageBox.confirm(
    '确定要删除这条消息记录吗？',
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    if (Array.isArray(collectedData.value)) {
      const index = collectedData.value.findIndex(item => item.time === row.time && item.sender === row.sender)
      if (index !== -1) {
        collectedData.value.splice(index, 1)
        ElMessage.success('消息记录已删除')
      }
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 导出收集的数据
const exportCollectedData = async () => {
  exportLoading.value = true

  try {
    // 准备导出参数
    const exportParams = {
      group_name: selectedGroupFilter.value || '',
      date: dateRangeFilter.value && dateRangeFilter.value.length > 0
        ? dateRangeFilter.value.join('_')
        : ''
    }

    // 调用后端API导出数据
    const response = await fetch('/api/group/export-collected-data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(exportParams)
    })

    if (!response.ok) {
      throw new Error('导出数据失败')
    }

    const result = await response.json()

    if (result.success) {
      // 创建下载链接
      const downloadLink = document.createElement('a')
      downloadLink.href = `/api/download-file?file_path=${encodeURIComponent(result.file_path)}`
      downloadLink.download = result.file_path.split('/').pop() || 'collected_data.csv'
      document.body.appendChild(downloadLink)
      downloadLink.click()
      document.body.removeChild(downloadLink)

      ElMessage.success('数据导出成功')
    } else {
      throw new Error(result.error || '导出数据失败')
    }
  } catch (error) {
    console.error('导出数据失败:', error)
    ElMessage.error(`导出数据失败: ${error.message}`)
  } finally {
    exportLoading.value = false
  }
}

// 工具函数
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

// 提取内容的逻辑函数
const extractContent = (message) => {
  // 如果直接传入的是提取内容字符串，直接返回
  if (typeof message === 'string' && message.trim()) {
    return message
  }
  
  // 如果传入的是消息对象，尝试获取提取内容
  if (typeof message === 'object' && message !== null) {
    // 优先使用extractedContent字段
    if (message.extractedContent && message.extractedContent.trim()) {
      return message.extractedContent
    }
    
    // 其次使用extracted_content字段
    if (message.extracted_content && message.extracted_content.trim()) {
      return message.extracted_content
    }
    
    // 如果都没有，尝试从content字段提取
    if (message.content && typeof message.content === 'string') {
      let extracted = ''
      
      // 匹配姓名
      const nameMatch = message.content.match(/我叫([^，,。；;\s]+)/)
      if (nameMatch && nameMatch[1]) {
        extracted += nameMatch[1]
      }

      // 匹配年龄
      const ageMatch = message.content.match(/我(\d+)岁/)
      if (ageMatch && ageMatch[1]) {
        if (extracted) extracted += '，'
        extracted += `${ageMatch[1]}岁`
      }
      
      return extracted || '无提取内容'
    }
  }
  
  return '无提取内容'
}

const autoLearnPattern = () => {
  if (!originalMessage.value.trim()) {
    ElMessage.warning('请先输入原始消息内容')
    return
  }

  if (!collectionTemplate.value.trim()) {
    ElMessage.warning('请先输入需要提取的内容')
    return
  }

  patternLearning.value = true

  // 使用统一的API函数调用后端Python服务进行智能学习
  autoLearnPatternAPI(originalMessage.value, collectionTemplate.value)
    .then(data => {
      patternLearning.value = false
      generatedRegex.value = data.regex || ''
      extractedValues.value = data.extracted_values || {}
      ElMessage.success('学习完成')
    })
    .catch(error => {
      patternLearning.value = false
      ElMessage.error(`学习失败：${error.message}`)
    })
}

const showPatternHelp = () => {
  ElMessageBox.alert(
    '智能模板使用说明：\n\n' +
    '1. 在"原始消息内容"中输入完整的消息示例\n' +
    '2. 在"需要提取的内容"中输入您想提取的内容，用逗号分隔\n' +
    '3. 点击"智能学习"让系统自动生成匹配规则\n' +
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

  if (!Array.isArray(regexRules.value)) {
    regexRules.value = []
  }

  // 添加到本地数组
  regexRules.value.push({
    originalMessage: originalMessage.value,
    pattern: generatedRegex.value,
    extractedContent: Object.values(extractedValues.value).join(', ')
  })

  // 调用后端API保存到文件
  saveRegexRulesAPI(regexRules.value)
    .then(() => {
      templateDialogVisible.value = false
      ElMessage.success('模板保存成功并已保存到服务器')
    })
    .catch(error => {
      ElMessage.error(`保存失败：${error.message}`)
      // 如果保存失败，回滚本地操作
      regexRules.value.pop()
    })
}

// 生命周期钩子
onMounted(() => {
  console.log('数据收集配置视图已加载')

  // 从API加载初始数据
  loadInitialData()
})

// 加载初始数据
const loadInitialData = async () => {
  try {
    dataLoading.value = true

    // 设置默认日期范围为2025-09-20至2025-09-22
    if (!dateRangeFilter.value || dateRangeFilter.value.length === 0) {
      dateRangeFilter.value = ['2025-09-20', '2025-09-22']
    }

    // 并行加载各项数据
    const [rulesData, groupsData, sensitiveWordsData, collectedDataResponse, configStatusData] = await Promise.all([
      getRegexRulesAPI(),
      getAvailableGroupsAPI(),
      getSensitiveWordsAPI(),
      getCollectedDataAPI('', dateRangeFilter.value),
      getConfigStatusAPI()
    ])

    console.log('加载初始数据 - 正则规则:', rulesData)
    console.log('加载初始数据 - 可用群聊:', groupsData)
    console.log('加载初始数据 - 敏感词:', sensitiveWordsData)
    console.log('加载初始数据 - 收集数据:', collectedDataResponse)
    console.log('加载初始数据 - 配置状态:', configStatusData)

    regexRules.value = rulesData
    availableGroups.value = groupsData
    sensitiveWordsList.value = sensitiveWordsData
    collectedData.value = collectedDataResponse

    // 设置配置状态
    if (configStatusData) {
      const configData = configStatusData
      console.log(configData)
      contactPerson.value = configData.group
      groupManagementStatus.value = configData.management_status !== undefined ? configData.management_status : groupManagementStatus.value
      dataCollectionEnabled.value = configData.data_collection_enabled !== undefined ? configData.data_collection_enabled : dataCollectionEnabled.value
      monitoringEnabled.value = configData.monitoring_enabled !== undefined ? configData.monitoring_enabled : monitoringEnabled.value
    }

  } catch (error) {
    console.error('加载初始数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
  } finally {
    dataLoading.value = false
  }
}

// 监听数据变化
watch(groupManagementStatus, (newVal) => {
  if (newVal) {
    console.log('管理功能已启用')
  }
})

watch([dataCollectionEnabled, monitoringEnabled], ([dataEnabled, monitorEnabled]) => {
  if (dataEnabled || monitorEnabled) {
    console.log('功能状态变化 - 数据收集:', dataEnabled, '舆情监控:', monitorEnabled)
  }
})

// API调用函数
function getCollectedDataAPI(groupId = '', dateRange = []) {
  const params = new URLSearchParams()
  if (groupId) params.append('group_id', groupId)
  if (dateRange && dateRange.length > 0) {
    params.append('start_date', dateRange[0])
    params.append('end_date', dateRange[1])
  }

  const url = `/api/group/get-collected-data${params.toString() ? '?' + params.toString() : ''}`

  return fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error('获取收集的数据失败')
      }
      return response.json()
    })
    .then(data => {
      // 确保返回的是数组数据，处理API返回格式
      if (data && data.success && Array.isArray(data.data)) {
        // 确保数据包含所需字段：时间、发送者、群聊、消息内容、提取数据
        const processedData = data.data.map(item => ({
          time: item.time || '',
          sender: item.sender || '',
          group: item.group || '',
          content: item.content || '',
          type: item.type || '',
          extractedContent: item.extractedContent || item.extracted_content || '',
          ...item // 保留其他字段
        }))
        return processedData
      } else if (Array.isArray(data)) {
        // 如果直接返回数组（兼容旧版本），同样处理字段
        const processedData = data.map(item => ({
          time: item.time || '',
          sender: item.sender || '',
          group: item.group || '',
          content: item.content || '',
          type: item.type || '',
          extractedContent: item.extractedContent || item.extracted_content || '',
          ...item // 保留其他字段
        }))
        return processedData
      } else {
        console.warn('获取的数据格式异常:', data)
        return []
      }
    })
}

// 获取配置状态API
function getConfigStatusAPI() {
  return fetch(`/api/group/get-config-status`)
    .then(response => {
      if (!response.ok) {
        throw new Error('获取配置状态失败')
      }
      return response.json()
    })
    .then(data => {
      // 直接返回配置状态数据，后端API返回的是配置对象本身
      if (data && (data.management_status !== undefined || data.group !== undefined)) {
        return data
      } else {
        console.warn('获取配置状态失败或格式不正确:', data)
        // 返回默认配置状态
        return {
          management_status: false,
          data_collection_enabled: false,
          monitoring_enabled: false,
          group: ""
        }
      }
    })
}

function getRegexRulesAPI() {
  return fetch(`/api/group/get-regex-rules`)
    .then(response => {
      if (!response.ok) {
        throw new Error('获取规则列表失败')
      }
      return response.json()
    })
    .then(data => {
      // 处理API返回格式
      if (data && data.success && Array.isArray(data.rules)) {
        return data.rules
      } else if (Array.isArray(data)) {
        // 兼容旧版本直接返回数组
        return data
      } else {
        console.warn('获取规则列表失败:', data)
        return []
      }
    })
}

function getSensitiveWordsAPI() {
  return fetch(`/api/group/get-sensitive-words`)
    .then(response => {
      if (!response.ok) {
        throw new Error('获取敏感词列表失败')
      }
      return response.json()
    })
    .then(data => {
      // 处理API返回格式
      if (data && data.success && Array.isArray(data.words)) {
        return data.words
      } else if (Array.isArray(data)) {
        // 兼容旧版本直接返回数组
        return data
      } else {
        console.warn('获取敏感词列表失败:', data)
        return []
      }
    })
}

function getAvailableGroupsAPI() {
  return fetch(`/api/group/get-available-groups`)
    .then(response => {
      if (!response.ok) {
        throw new Error('获取可用群组失败')
      }
      return response.json()
    })
    .then(data => {
      // 处理API返回格式
      if (data && data.success && Array.isArray(data.groups)) {
        return data.groups
      } else if (Array.isArray(data)) {
        // 兼容旧版本直接返回数组
        return data
      } else {
        console.warn('获取可用群组失败:', data)
        return []
      }
    })
}

function autoLearnPatternAPI(originalMessage, targetContent) {
  return fetch('/api/group/auto-learn-pattern', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      original_message: originalMessage,
      target_content: targetContent
    })
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('智能学习失败')
      }
      return response.json()
    })
    .then(data => {
      // 处理API返回格式
      if (data && data.success) {
        return data
      } else {
        console.warn('智能学习失败:', data)
        throw new Error(data.error || '智能学习失败')
      }
    })
}

// 保存敏感词API
function saveSensitiveWordsAPI(words) {
  return fetch('/api/group/save-sensitive-words', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      words: words
    })
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('保存敏感词失败')
      }
      return response.json()
    })
    .then(data => {
      // 处理API返回格式
      if (data && data.success) {
        return data
      } else {
        console.warn('保存敏感词失败:', data)
        throw new Error(data.error || '保存敏感词失败')
      }
    })
}

// 保存正则规则API
function saveRegexRulesAPI(rules) {
  return fetch('/api/group/save-regex-rules', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      rules: rules
    })
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('保存正则规则失败')
      }
      return response.json()
    })
    .then(data => {
      // 处理API返回格式
      if (data && data.success) {
        return data
      } else {
        console.warn('保存正则规则失败:', data)
        throw new Error(data.error || '保存正则规则失败')
      }
    })
}
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
.auto-info-container {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 100vh;
  padding: 0px;
  background-color: var(--light-color);
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding-right: 12px;
}

/* 卡片样式优化 - 统一间距和对齐 */
.group-config-card,
.monitoring-config-card,
.data-display-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  background-color: white;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.group-config-card:hover,
.monitoring-config-card:hover,
.data-display-card:hover {
  box-shadow: 0 12px 28px 0 rgba(0, 0, 0, 0.08), 0 2px 4px 0 rgba(0, 0, 0, 0.04);
  border-color: var(--primary-color);
}

/* 卡片头部优化 - 整齐对齐 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 12px;
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
}

/* 表单样式优化 - 统一内边距和对齐 */
.data-collection-form,
.rules-form,
.monitoring-form {
  padding: 0px;
}

.el-form-item {
  margin-bottom: 24px;
  padding: 0;
}

.el-form-item:last-child {
  margin-bottom: 0;
}

.el-form-item__label {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 12px;
  font-size: 15px;
}

/* 数据收集配置行 - 整齐排列控件 */
.data-collection-row .el-col {
  display: flex;
  align-items: center;
}

.inline-form-item {
  width: 100%;
}

/* 群聊管理区域样式 */
.group-management-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.section-label {
  font-weight: 500;
  color: var(--text-primary);
  min-width: 80px;
  font-size: 14px;
}

.controls-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 32px;
  width: 100%;
  padding: 12px 0;
}

.contact-input {
  flex: 1;
  min-width: 400px;
}

/* 状态控件优化 - 保持开关原生样式，优化文字对齐 */
.status-control {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

/* 统一文本框和开关的高度 */
.contact-input .el-input__wrapper {
  height: 40px;
}

.status-control .el-switch {
  align-self: center;
}

.status-text {
  font-size: 14px;
  color: var(--el-text-color-regular);
  white-space: nowrap;
}

/* 按钮样式优化 - 统一按钮大小和间距 */
.el-button {
  transition: all 0.2s ease;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  margin: 4px;
}

.el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
}

.el-button--primary {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.el-button--primary:hover {
  background-color: #1e3a8a;
  border-color: #1e3a8a;
}

/* 敏感词输入容器样式 - 确保文本框和按钮在一行显示 */
.sensitive-word-input-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.sensitive-word-input {
  flex: 1;
  min-width: 0;
}

.el-input,
.el-select,
.el-date-picker {
  margin-bottom: 0;
}

.el-input__prefix {
  padding-right: 8px;
  color: var(--el-text-color-secondary);
}

.rule-actions {
  margin-bottom: 24px;
  display: flex;
  gap: 16px;
  align-items: center;
}

/* 提取内容状态样式 */
.extracted-content-status {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f9ff;
  border: 1px solid #e6f7ff;
  border-radius: 6px;
  padding: 4px 8px;
  color: #1890ff;
  font-size: 12px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  max-width: 100%;
}

.extracted-content-status .success-icon {
  margin-right: 4px;
  color: #52c41a;
  font-size: 14px;
}

.extracted-content-status .warning-icon {
  margin-right: 4px;
  color: #faad14;
  font-size: 14px;
}

.sensitive-words-list {
  min-height: 75px;
  min-width: 75vw;
  overflow-y: auto;
  padding: 16px 20px;
  background-color: var(--el-fill-color-lighter);
  border-radius: 8px;
  margin: 0 0 16px 0;
  border: 1px solid var(--el-border-color-light);
}

.sensitive-word-tag {
  margin: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.sensitive-word-tag:hover {
  transform: scale(1.05);
  box-shadow: var(--el-box-shadow-light);
}

.data-table {
  margin-top: 20px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
}

.data-table .el-table__cell {
  padding: 12px 20px;
  font-size: 14px;
  border-bottom: 1px solid var(--border-color);
}

.data-table tr:last-child .el-table__cell {
  border-bottom: none;
}

.data-table th {
  background-color: rgba(30, 64, 175, 0.05);
  font-weight: 600;
  color: var(--text-primary);
  padding: 12px 0;
}

.time-cell,
.sender-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
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

/* 表格操作按钮样式优化 */
.detail-btn,
.delete-btn {
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 6px;
  margin: 0 8px;
  transition: all 0.2s ease;
}

.detail-btn:hover,
.delete-btn:hover {
  transform: translateY(-1px);
}

.refresh-btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 500;
}

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
}

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

/* 标签样式优化 */
.el-tag {
  margin: 6px;
  transition: all 0.2s ease;
  font-size: 14px;
  padding: 4px 12px;
}

.el-tag:hover {
  transform: scale(1.05);
}

.el-tag--info {
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--secondary-color);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.el-tag--success {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.el-table__cell .el-button {
  margin: 0 8px;
}

/* 表格行悬停效果 */
.el-table--enable-row-hover .el-table__body tr:hover>td {
  background-color: rgba(59, 130, 246, 0.08) !important;
}

/* 响应式优化 - 保持小屏幕上的整齐布局 */
@media (max-width: 768px) {
  .auto-info-container {
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

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .header-title {
    font-size: 16px;
  }

  .data-collection-form,
  .rules-form,
  .monitoring-form {
    padding: 16px;
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

  .controls-row {
    flex-wrap: wrap;
    gap: 16px;
  }

  .status-control {
    margin-bottom: 8px;
  }

  .contact-input {
    min-width: 100%;
  }
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 加载动画样式 */
:deep(.el-form-item.is-success .el-input__inner) {
  border-color: var(--el-color-success);
}
</style>
