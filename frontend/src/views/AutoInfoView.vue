<template>
  <div class="auto-info-container">
    <section class="task-creation-section">
      <el-card class="task-creation-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>创建新任务</span>
          </div>
        </template>

        <el-form ref="taskForm" :model="formData" :rules="rules" label-width="100px">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="12" :lg="12">
              <el-form-item label="接收者" prop="recipient">
                <el-input v-model="formData.recipient" placeholder="输入接收者信息" clearable>
                  <template #prefix>
                    <el-icon>
                      <User />
                    </el-icon>
                  </template>
                </el-input>
                <div class="el-form-item__tip">多个接收者用逗号分隔</div>
              </el-form-item>
            </el-col>

            <el-col :xs="24" :sm="12" :md="12" :lg="12">
              <el-form-item label="发送时间" prop="sendTime">
                <el-date-picker v-model="formData.sendTime" type="datetime" placeholder="选择发送时间"
                  value-format="YYYY-MM-DDTHH:mm:ss" format="YYYY-MM-DD HH:mm:ss" :default-value="defaultDateTime" style="width: 100%" />
                <div class="el-form-item__tip">选择发送时间，精确到秒</div>
              </el-form-item>
            </el-col>

            <el-col :xs="24" :sm="12" :md="12" :lg="12">
              <el-form-item label="重复选项" prop="repeatType">
                <el-select v-model="formData.repeatType" placeholder="选择重复类型" style="width: 100%">
                  <el-option v-for="option in repeatOptions" :key="option.value" :label="option.label"
                    :value="option.value" />
                </el-select>
                <el-form-item v-if="formData.repeatType === 'custom'" prop="repeatDays" :rules="[{
                  validator: (_, value, callback) => {
                    if (formData.repeatType === 'custom' && (!value || value.length === 0)) {
                      callback(new Error('请至少选择一个重复日期'))
                    } else {
                      callback()
                    }
                  },
                  trigger: 'change'
                }]">
                  <p class="el-form-item__tip">选择重复日期：</p>
                  <el-checkbox-group v-model="formData.repeatDays">
                    <el-checkbox v-for="day in daysOfWeek" :key="day.value" :label="day.value">
                      {{ day.label }}
                    </el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                <el-form-item v-if="formData.repeatType === 'interval'" prop="repeatInterval" :rules="[{
                  validator: (_, value, callback) => {
                    if (formData.repeatType === 'interval' && (!value || value <= 0)) {
                      callback(new Error('请输入有效的时间间隔'))
                    } else {
                      callback()
                    }
                  },
                  trigger: 'blur'
                }]">
                  <div class="interval-input-container">
                    <span class="interval-label">每</span>
                    <el-input-number v-model="formData.repeatInterval" :min="1" :max="1440" placeholder="间隔时间" style="width: 120px" />
                    <span class="interval-label">分钟发送一次</span>
                  </div>
                  <div class="el-form-item__tip" style="padding-left: 20px;">范围：1-1440分钟（1分钟至24小时）</div>
                </el-form-item>
                <div class="el-form-item__tip">像定闹钟一样，选择重复日期</div>
              </el-form-item>
            </el-col>

            <el-col :xs="24" :sm="12" :md="12" :lg="12">
              <el-form-item label="过期任务" prop="importExpiredTask">
                <el-radio-group v-model="formData.importExpiredTask">
                  <el-radio label="1">依然导入</el-radio>
                  <el-radio label="2">阻止导入</el-radio>
                  <el-radio label="3">智能顺延</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>

            <el-col :span="24">
              <el-form-item label="信息内容" prop="messageContent">
                <el-input v-model="formData.messageContent" type="textarea" placeholder="输入要发送的消息内容或文件路径" :rows="4"
                  show-word-limit maxlength="800" />
                <div class="el-form-item__tip">
                  <p>发送文件：直接输入完整文件路径，如 <strong>D:\文档\报告.pdf</strong></p>
                  <p>发送表情：输入 <strong>SendEmotion:1</strong>，1为表情序号；随机表情范围用逗号分隔，如 <strong>SendEmotion:2,3,4</strong></p>
                </div>
              </el-form-item>

            </el-col>
          </el-row>

          <el-form-item>
            <el-button type="default" @click="resetForm">重置</el-button>
            <el-button type="primary" @click="submitForm">
              创建任务
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </section>

    <section class="task-list-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <div class="header-title">
              <span>任务列表</span>
              <span class="task-count">{{ tasks.length }}</span>
            </div>
            <div class="task-actions">
              <el-button-group>
                <el-button @click="refreshTasks">
                  <el-icon>
                    <Refresh />
                  </el-icon>刷新
                </el-button>
                <el-button @click="importTasks">
                  导入
                </el-button>
                <el-button :disabled="tasks.length === 0" @click="exportTasks">
                  导出
                </el-button>
                <el-button :disabled="tasks.length === 0" @click="clearAllTasks" type="danger">
                  清空
                </el-button>
                <el-button :disabled="tasks.length === 0" @click="toggleTaskScheduler"
                  :type="isSchedulerRunning ? 'danger' : 'primary'">
                  {{ isSchedulerRunning ? '停止执行' : '开始执行' }}
                </el-button>
              </el-button-group>
              <input type="file" ref="fileInput" style="display: none;" accept=".xlsx" @change="handleFileImport">
            </div>
          </div>
        </template>

        <el-table v-if="tasks.length > 0" :data="paginatedTasks" style="width: 100%" stripe fit
          :row-class-name="tableRowClassName">
          <el-table-column prop="recipient" label="接收者" min-width="20px" />
          <el-table-column prop="messageContent" label="内容" min-width="20px">
            <template #default="{ row }">
              <el-tooltip :content="row.filePath || row.messageContent" placement="top">
                <div class="message-content">
                  {{ row.filePath || row.messageContent }}
                </div>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="sendTime" label="发送时间" min-width="15px">
            <template #default="{ row }">
              {{ formatDateTime(row.sendTime) }}
            </template>
          </el-table-column>
          <el-table-column label="重复类型" min-width="20px">
            <template #default="{ row }">
              {{ getRepeatText(row.repeatType, row.repeatDays, row.repeatInterval) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" min-width="10px" fixed="right">
            <template #default="{ row }">
              <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'completed' ? 'success' : 'danger'"
                size="small">
                {{ row.status === 'pending' ? '待执行' : row.status === 'completed' ? '已完成' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="错误信息" min-width="20px" v-if="tasks.some(task => task.errorMessage)">
            <template #default="{ row }">
              <el-tooltip v-if="row.errorMessage" :content="row.errorMessage" placement="top">
                <el-tag type="danger" size="small">
                  <el-icon>
                    <Warning />
                  </el-icon>
                  查看错误
                </el-tag>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="16px" fixed="right">
            <template #default="{ row }">
              <div class="operation-buttons">
                <el-button type="primary" size="small" @click="editTask(row.id)" :icon="Edit">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteTask(row.id)" :icon="Delete">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页组件 -->
        <div v-if="tasks.length > 0" class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="tasks.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>

        <el-empty v-else description="快创建您的第一个自动信息任务">
        </el-empty>
      </el-card>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Delete, Refresh, Edit, Warning } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'

const taskForm = ref()
const formData = reactive({
  recipient: '',
  sendTime: '',
  repeatType: 'none',
  repeatDays: [],
  repeatInterval: 10, // 默认30分钟
  messageContent: '',
  importExpiredTask: '1'
})

const rules = {
  recipient: [
    { required: true, message: '请输入接收者', trigger: 'blur' },
    {
      validator: (_, value, callback) => {
        if (!value || !value.trim()) {
          callback(new Error('请输入接收者'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  sendTime: [
    { required: true, message: '请选择发送时间', trigger: 'change' }
  ],
  messageContent: [
    {
      validator: (_, value, callback) => {
        // 不再要求必须填写消息内容或文件，因为现在可以同时创建两个任务
        callback()
      },
      trigger: 'blur'
    }
  ],
  repeatType: [
    { required: true, message: '请选择重复类型', trigger: 'change' }
  ],
  importExpiredTask: [
    { required: true, message: '请选择过期任务处理方式', trigger: 'change' }
  ]
}

const tasks = ref([])
const isSchedulerRunning = ref(false)

// 分页相关变量
const currentPage = ref(1)
const pageSize = ref(10)

const repeatOptions = [
  { label: '不重复', value: 'none' },
  { label: '每天', value: 'daily' },
  { label: '法定工作日', value: 'workday' },
  { label: '法定节假日', value: 'holiday' },
  { label: '自定义', value: 'custom' },
  { label: '间隔循环', value: 'interval' }
]

const daysOfWeek = [
  { label: '周一', value: '1' },
  { label: '周二', value: '2' },
  { label: '周三', value: '3' },
  { label: '周四', value: '4' },
  { label: '周五', value: '5' },
  { label: '周六', value: '6' },
  { label: '周日', value: '0' }
]

const defaultDateTime = computed(() => {
  const now = new Date()
  now.setMinutes(now.getMinutes() + 30)
  return now
})

const sortedTasks = computed(() => {
  return [...tasks.value].sort((a, b) => new Date(a.sendTime) - new Date(b.sendTime))
})

// 分页后的任务列表
const paginatedTasks = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return sortedTasks.value.slice(startIndex, endIndex)
})

// 分页事件处理
const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1 // 重置到第一页
}

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
}

const resetForm = () => {
  taskForm.value?.resetFields()
  // 重置后保持importExpiredTask的默认值为"1"
  formData.importExpiredTask = '1'
}

const submitForm = async () => {
  try {
    await taskForm.value.validate()

    // 自定义验证：确保填写了消息内容
    if (!formData.messageContent) {
      ElMessage.error('请填写消息内容')
      return
    }

    // 创建任务
    const tasksToCreate = [{
      ...formData,
      repeatInterval: formData.repeatInterval, // 确保间隔分钟数字段被正确传递
      status: 'pending',
      createdAt: new Date().toISOString()
    }]

    // 批量创建任务
    let successCount = 0
    for (const taskData of tasksToCreate) {
      const response = await fetch('http://localhost:5000/api/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(taskData)
      })

      if (response.ok) {
        const responseData = await response.json()
        
        // 处理API返回格式
        let newTask
        if (responseData && responseData.success && responseData.data) {
          newTask = responseData.data
        } else if (responseData && responseData.id) {
          // 兼容旧版本直接返回任务对象
          newTask = responseData
        } else {
          console.warn('创建任务返回格式异常:', responseData)
          throw new Error('创建任务失败: 返回数据格式异常')
        }
        
        tasks.value.push(newTask)
        successCount++
      }
    }

    if (successCount === tasksToCreate.length) {
      ElMessage.success(`成功创建 ${successCount} 个任务`)
      resetForm()
      // 重置后保持importExpiredTask的默认值为"1"
      formData.importExpiredTask = '1'
    } else {
      ElMessage.error(`部分任务创建失败，成功创建 ${successCount}/${tasksToCreate.length} 个任务`)
    }
  } catch (error) {
    if (!error.errors) {
      console.error('创建任务失败:', error)
      ElMessage.error('创建任务失败')
    }
  }
}

const tableRowClassName = ({ row }) => {
  return row.status === 'pending' ? 'task-pending' : 'task-completed'
}

const editTask = async (taskId) => {
  const task = tasks.value.find(t => t.id === taskId)
  if (task) {
    formData.recipient = task.recipient
    formData.sendTime = task.sendTime
    formData.repeatType = task.repeatType
    formData.repeatDays = task.repeatDays
    formData.repeatInterval = task.repeatInterval || 30 // 默认30分钟
    formData.messageContent = task.messageContent
    // 保持默认的importExpiredTask值不变，因为这是导入时的设置，不是任务本身的属性

    // 删除原任务
    try {
      const response = await fetch(`http://localhost:5000/api/tasks/${taskId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        tasks.value = tasks.value.filter(t => t.id !== taskId)
        ElMessage({ message: '请修改任务信息', type: 'warning' })
      } else {
        ElMessage.error('删除原任务失败，请稍后重试')
      }
    } catch (error) {
      console.error('删除原任务失败:', error)
      ElMessage.error('删除原任务失败，请稍后重试')
    }
  }
}

const deleteTask = async (taskId) => {
  ElMessageBox.confirm('确定要删除这个任务吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/tasks/${taskId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        tasks.value = tasks.value.filter(task => task.id !== taskId)
        ElMessage.success('任务删除成功')
      } else {
        ElMessage.error('任务删除失败，请稍后重试')
      }
    } catch (error) {
      console.error('删除任务失败:', error)
      ElMessage.error('任务删除失败，请稍后重试')
    }
  }).catch(() => { })
}

const clearAllTasks = async () => {
  ElMessageBox.confirm('确定要清空所有任务吗？此操作不可恢复！', '提示', {
    confirmButtonText: '确定清空',
    cancelButtonText: '取消',
    type: 'warning',
    confirmButtonClass: 'el-button--danger'
  }).then(async () => {
    try {
      const response = await fetch('http://localhost:5000/api/tasks', {
        method: 'DELETE'
      })

      if (response.ok) {
        tasks.value = []
        ElMessage.success('所有任务已清空')
      } else {
        const errorText = await response.text()
        ElMessage.error(`清空任务失败: ${errorText || '未知错误'}`)
      }
    } catch (error) {
      console.error('清空任务失败:', error)
      ElMessage.error('清空任务失败，请检查网络连接')
    }
  }).catch(() => { })
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return dateString
  return `${date.getFullYear()}-${padZero(date.getMonth() + 1)}-${padZero(date.getDate())} ${padZero(date.getHours())}:${padZero(date.getMinutes())}:${padZero(date.getSeconds())}`
}

const padZero = (num) => {
  return num < 10 ? '0' + num : num
}

const refreshTasks = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/tasks')
    if (response.ok) {
      const data = await response.json()
      
      // 处理API返回格式
      let tasksData = []
      if (data && data.success && Array.isArray(data.data)) {
        tasksData = data.data
      } else if (Array.isArray(data)) {
        // 兼容旧版本直接返回数组
        tasksData = data
      } else {
        console.warn('获取任务列表格式异常:', data)
        ElMessage.error('获取任务列表失败: 数据格式异常')
        return
      }
      
      tasks.value = tasksData

      // 检查是否有待执行的任务，如果没有则自动停止调度器
      const pendingTasks = tasksData.filter(task => task.status === 'pending')
      if (pendingTasks.length === 0 && isSchedulerRunning.value) {
        // 没有待执行任务，自动停止调度器
        isSchedulerRunning.value = false
        ElMessage.success('所有任务已完成，调度器已自动停止')
      }
    } else {
      const errorText = await response.text()
      ElMessage.error(`刷新任务列表失败: ${errorText || '未知错误'}`)
    }
  } catch (error) {
    ElMessage.error(`刷新任务列表失败: ${error.message || '网络错误'}`)
  }
}

// 导出任务功能
const exportTasks = () => {
  if (tasks.value.length === 0) {
    ElMessage.warning('没有任务可导出')
    return
  }

  // 准备导出的数据（只包含需要的字段）
  const exportData = tasks.value.map(task => ({
    '发送时间': formatDateTime(task.sendTime),
    '接收者': task.recipient,
    '内容': task.filePath || task.messageContent,
    '重复类型': getRepeatText(task.repeatType, task.repeatDays, task.repeatInterval)
  }))

  // 创建工作簿和工作表
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '任务列表')

  // 设置所有单元格为文本格式
  const range = XLSX.utils.decode_range(ws['!ref'])
  for (let row = range.s.r; row <= range.e.r; row++) {
    for (let col = range.s.c; col <= range.e.c; col++) {
      const cellAddress = XLSX.utils.encode_cell({ r: row, c: col })
      if (!ws[cellAddress]) continue

      // 设置单元格格式为文本
      if (!ws[cellAddress].z) {
        ws[cellAddress].z = '@' // @ 表示文本格式
      }
    }
  }

  // 导出Excel文件
  XLSX.writeFile(wb, `tasks_export_${new Date().toISOString().slice(0, 10)}.xlsx`)

  ElMessage.success('任务导出成功')
}

// 导入任务功能
const fileInput = ref(null)

const importTasks = () => {
  fileInput.value?.click()
}

const handleFileImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  try {
    const reader = new FileReader()
    reader.onload = async (e) => {
      try {
        // 解析Excel文件
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]
        const importedData = XLSX.utils.sheet_to_json(worksheet)

        // 验证导入的数据格式
        if (!Array.isArray(importedData)) {
          throw new Error('导入的文件格式不正确')
        }

        // 转换Excel数据为任务格式
        const now = new Date()
        const validTasks = importedData.map(item => {
          // 处理重复类型
          let repeatType = 'none'
          let repeatDays = []
          let repeatInterval = 30 // 默认30分钟
          const repeatText = item['重复类型'] || ''

          if (repeatText.includes('每天')) {
            repeatType = 'daily'
          } else if (repeatText.includes('法定工作日')) {
            repeatType = 'workday'
          } else if (repeatText.includes('法定节假日')) {
            repeatType = 'holiday'
          } else if (repeatText.includes('自定义')) {
            repeatType = 'custom'
            // 提取重复天数（这里简化处理，实际可能需要更复杂的解析）
            const dayMap = {
              '周日': '0', '周一': '1', '周二': '2', '周三': '3',
              '周四': '4', '周五': '5', '周六': '6'
            }
            Object.keys(dayMap).forEach(day => {
              if (repeatText.includes(day)) {
                repeatDays.push(dayMap[day])
              }
            })
          } else if (repeatText.includes('每') && repeatText.includes('分钟')) {
            repeatType = 'interval'
            // 提取间隔分钟数
            const intervalMatch = repeatText.match(/每(\d+)分钟/)
            if (intervalMatch) {
              repeatInterval = parseInt(intervalMatch[1])
            }
          }

          // 解析发送时间，处理只有分钟的情况
          let sendTime = ''
          if (item['发送时间']) {
            const timeString = String(item['发送时间'])
            // 尝试解析时间字符串
            let dateObj = new Date(timeString)
            
            if (isNaN(dateObj.getTime())) {
              // 如果标准解析失败，尝试手动解析常见格式
              const timeMatch = timeString.match(/(\d{4})[-/](\d{1,2})[-/](\d{1,2})[\sT](\d{1,2}):(\d{1,2})(?::(\d{1,2}))?/)
              if (timeMatch) {
                const year = parseInt(timeMatch[1])
                const month = parseInt(timeMatch[2]) - 1
                const day = parseInt(timeMatch[3])
                const hours = parseInt(timeMatch[4])
                const minutes = parseInt(timeMatch[5])
                const seconds = timeMatch[6] ? parseInt(timeMatch[6]) : 0 // 如果没有秒，设置为0
                
                dateObj = new Date(year, month, day, hours, minutes, seconds)
              } else {
                // 如果还是无法解析，使用当前时间
                dateObj = new Date()
              }
            }
            
            // 确保秒数为00（如果只有分钟）
            if (dateObj.getSeconds() === 0) {
              // 已经是整分，不需要修改
            } else {
              // 如果不是整分，设置为整分00秒
              dateObj.setSeconds(0)
            }
            
            sendTime = dateObj.toISOString()
          }
          
          // 处理过期任务
          if (sendTime && new Date(sendTime) < now) {
            // 根据选择的处理方式处理过期任务
            if (formData.importExpiredTask === '2') {
              // 阻止导入 - 返回null，后续会被过滤掉
              return null
            } else if (formData.importExpiredTask === '3') {
              // 智能顺延 - 将时间顺延到明天同一时间
              const taskDate = new Date(sendTime)
              taskDate.setDate(taskDate.getDate() + 1)
              sendTime = taskDate.toISOString()
            }
            // 选项 '1' 是依然导入，不需要特殊处理
          }

          return {
            recipient: item['接收者'] || '',
            sendTime,
            messageContent: item['内容'] || '',
            repeatType,
            repeatDays,
            repeatInterval
          }
        }).filter(task => {
          // 过滤掉null值（被阻止导入的过期任务）和缺少必要字段的任务
          return task && task.recipient && task.sendTime && (task.messageContent || task.filePath)
        })

        // 上传到服务器
        const response = await fetch('http://localhost:5000/api/tasks/import', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(validTasks)
        })

        if (response.ok) {
          const data = await response.json()
          
          // 处理API返回格式
          if (data && data.success) {
            ElMessage.success(`成功导入 ${validTasks.length} 个任务`)
            refreshTasks()
          } else {
            throw new Error(data.error || '服务器导入失败')
          }
        } else {
          throw new Error('服务器导入失败')
        }
      } catch (error) {
        ElMessage.error(`导入失败: ${error.message}`)
      }
    }
    reader.readAsArrayBuffer(file)
  } catch (error) {
    ElMessage.error(`导入失败: ${error.message}`)
  }

  // 重置文件输入，以便可以重复选择同一个文件
  event.target.value = ''
}



const getRepeatText = (repeatType, repeatDays, repeatInterval) => {
  const dayMap = {
    '0': '周日', '1': '周一', '2': '周二', '3': '周三',
    '4': '周四', '5': '周五', '6': '周六'
  }

  switch (repeatType) {
    case 'none': return '不重复'
    case 'daily': return '每天'
    case 'workday': return '法定工作日'
    case 'holiday': return '法定节假日'
    case 'custom': return `自定义: ${repeatDays?.map(day => dayMap[day]).join(', ')}`
    case 'interval': return `每${repeatInterval || 30}分钟`
    default: return '不重复'
  }
}

const toggleTaskScheduler = async () => {
  try {
    if (isSchedulerRunning.value) {
      // 停止调度器
      const response = await fetch('http://localhost:5000/api/task-scheduler/stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        
        // 处理API返回格式
        if (data && data.success) {
          isSchedulerRunning.value = false
          ElMessage.success('任务调度器已停止')
        } else {
          ElMessage.error(`停止失败: ${data.error || '未知错误'}`)
        }
      } else {
        const errorData = await response.json()
        ElMessage.error(`停止失败: ${errorData.error || '未知错误'}`)
      }
    } else {
      // 检查是否有过时任务
      const now = new Date()
      const hasExpiredTasks = tasks.value.some(task => 
        task.status === 'pending' && new Date(task.sendTime) < now
      )

      if (hasExpiredTasks) {
        // 有过时任务，弹出确认对话框
        try {
          await ElMessageBox.confirm(
            '检测到有过期任务，这些任务会立即发送，确定继续吗？',
            '提示',
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'warning'
            }
          )
        } catch {
          // 用户点击了取消，不执行后续操作
          return
        }
      }

      // 启动调度器
      const response = await fetch('http://localhost:5000/api/task-scheduler/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        
        // 处理API返回格式
        if (data && data.success) {
          isSchedulerRunning.value = true
          ElMessage.success('任务调度器已启动')
        } else {
          ElMessage.error(`启动失败: ${data.error || '未知错误'}`)
        }
      } else {
        const errorData = await response.json()
        ElMessage.error(`启动失败: ${errorData.error || '未知错误'}`)
      }
    }
  } catch (error) {
    console.error('操作任务调度器失败:', error)
    ElMessage.error('操作失败，请检查网络连接')
  }
}

const checkSchedulerStatus = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/task-scheduler/status')
    if (response.ok) {
      const data = await response.json()
      
      // 处理API返回格式
      let isRunning = false
      if (data && data.success && data.data && data.data.isRunning !== undefined) {
        isRunning = data.data.isRunning
      } else if (data && data.isRunning !== undefined) {
        // 兼容旧版本直接返回状态对象
        isRunning = data.isRunning
      } else {
        console.warn('获取调度器状态格式异常:', data)
        return
      }
      
      isSchedulerRunning.value = isRunning
    }
  } catch (error) {
    console.error('获取调度器状态失败:', error)
  }
}

onMounted(() => {
  // 确保importExpiredTask的默认值为"1"
  formData.importExpiredTask = '1'
  
  refreshTasks()
  checkSchedulerStatus()

  // 定时检查调度器状态和刷新任务列表，确保界面同步
  const schedulerStatusInterval = setInterval(() => {
    checkSchedulerStatus()
    refreshTasks() // 无论调度器状态如何都刷新任务列表，确保状态实时更新
  }, 3000) // 每3秒检查一次，进一步提高刷新频率

  // 组件卸载时清除定时器
  onUnmounted(() => {
    clearInterval(schedulerStatusInterval)
  })
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


.task-pending .el-table__cell {
  background-color: rgba(59, 130, 246, 0.1);
}

.task-completed .el-table__cell {
  background-color: rgba(16, 185, 129, 0.1);
}


.task-creation-card,
.task-list-section .el-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  background-color: white;
}

.task-creation-card:hover,
.task-list-section .el-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px 0 rgba(0, 0, 0, 0.08), 0 2px 4px 0 rgba(0, 0, 0, 0.04);
  border-color: var(--primary-color);
}


.el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(30, 64, 175, 0.2);
}

.el-button {
  transition: all 0.2s ease;
}

.el-button--primary {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.el-button--primary:hover {
  background-color: #1e3a8a;
  border-color: #1e3a8a;
}

.auto-info-container {
  padding: 0;
  max-width: 100vw;
  margin: 0 auto;
  background-color: var(--light-color);
  min-height: 100vh;
}

.task-creation-section {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.card-header .span {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: var(--text-primary);
}

.task-count {
  font-size: 12px;
  color: var(--text-secondary);
  background-color: var(--light-color);
  padding: 2px 8px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.task-actions {
  display: flex;
  gap: 10px;
  padding: 5px 0;
}

.message-content {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

.custom-days {
  margin-top: 10px;
  padding: 12px;
  background-color: white;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.interval-input-container {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.interval-label {
  font-size: 14px;
  color: var(--text-primary);
  white-space: nowrap;
}

.el-form-item__tip {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
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
  background-color: rgba(59, 130, 246, 0.08);
}


.el-table__fixed-right {
  box-shadow: -2px 0 6px rgba(0, 0, 0, 0.05);
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

/* 分页样式 */
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

.pagination-container .el-pagination {
  background-color: white;
  border-radius: 8px;
  padding: 8px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.pagination-container .el-pagination .btn-prev,
.pagination-container .el-pagination .btn-next,
.pagination-container .el-pagination .number {
  border-radius: 6px;
  border: 1px solid var(--border-color);
  transition: all 0.2s ease;
}

.pagination-container .el-pagination .btn-prev:hover,
.pagination-container .el-pagination .btn-next:hover,
.pagination-container .el-pagination .number:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.pagination-container .el-pagination .number.active {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .task-actions {
    width: 100%;
  }

  .el-button-group {
    display: flex;
    width: 100%;
  }

  .el-button-group .el-button {
    flex: 1;
  }
  
  .pagination-container {
    padding: 12px 8px;
  }
  
  .pagination-container .el-pagination {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
