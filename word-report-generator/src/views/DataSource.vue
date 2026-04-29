<template>
  <div class="datasource-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-checkbox v-if="dataSourceList.length > 0" v-model="checkAll" :indeterminate="isIndeterminate" @change="handleCheckAllChange">全选</el-checkbox>
            <el-button v-if="selectedDataSources.length > 0" type="danger" size="small" @click="handleBatchDelete">
              批量删除 ({{ selectedDataSources.length }})
            </el-button>
          </div>
          <el-button type="primary" @click="showDialog = true; isEdit = false; resetForm()">
            新增数据源
          </el-button>
        </div>
      </template>
      <el-table :data="dataSourceList" v-loading="loading" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <template #empty>
          <el-empty description="暂无数据源">
            <template #extra>
              <el-button type="primary" @click="showDialog = true; isEdit = false; resetForm()">新增数据源</el-button>
            </template>
          </el-empty>
        </template>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="数据源名称" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag>{{ getTypeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : row.status === 'failed' ? 'danger' : 'info'" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="280">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleTest(row)">测试</el-button>
            <el-button 
              v-if="row.config?._fields?.length || row.type === 'json' || row.type === 'form'" 
              type="primary" 
              link 
              @click="showFields(row)"
            >变量</el-button>
            <el-button 
              v-if="row.config?.params?.length || row.config?.parameters?.length" 
              type="primary" 
              link 
              @click="showParams(row)"
            >入参</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="showDialog" :title="isEdit ? '编辑数据源' : '新增数据源'" width="700px" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="数据源名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入数据源名称" />
        </el-form-item>
        <el-form-item label="数据源类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择类型" @change="handleTypeChange">
            <el-option label="HTTP API" value="http_api" />
            <el-option label="静态JSON" value="json" />
            <el-option label="表单输入" value="form" />
            <el-option label="SQL 查询" value="sql" />
          </el-select>
        </el-form-item>

        <template v-if="form.type === 'http_api'">
          <el-divider>API 配置</el-divider>
          <el-form-item label="请求方法">
            <el-select v-model="form.config.method">
              <el-option label="GET" value="GET" />
              <el-option label="POST" value="POST" />
            </el-select>
          </el-form-item>
          <el-form-item label="接口地址">
            <el-input v-model="form.config.url" placeholder="https://api.example.com/data" />
          </el-form-item>
          <el-form-item label="请求头">
            <div v-for="(header, index) in form.config.headers" :key="index" class="kv-row">
              <el-input v-model="header.key" placeholder="Key" style="width:40%" />
              <el-input v-model="header.value" placeholder="Value" style="width:40%" />
              <el-button type="danger" link @click="removeHeader(index)">删除</el-button>
            </div>
            <el-button type="primary" link @click="addHeader">+ 添加请求头</el-button>
          </el-form-item>
          <el-form-item label="请求参数">
            <div v-for="(param, index) in form.config.params" :key="index" class="kv-row">
              <el-input v-model="param.key" placeholder="Key" style="width:40%" />
              <el-input v-model="param.value" placeholder="Value" style="width:40%" />
              <el-button type="danger" link @click="removeParam(index)">删除</el-button>
            </div>
            <el-button type="primary" link @click="addParam">+ 添加参数</el-button>
          </el-form-item>
          <el-form-item label="请求Body">
            <el-input v-model="form.config.body" type="textarea" :rows="4" placeholder='{"key": "value"}' />
          </el-form-item>
          <el-divider>动态参数配置</el-divider>
          <el-form-item label="参数列表">
            <div class="form-tip">
              支持在 URL、请求头、请求参数、请求体中使用 <code>:参数名</code> 格式
            </div>
            <div v-for="(param, index) in form.config.parameters" :key="index" class="param-row">
              <el-input v-model="param.name" placeholder="参数名" style="width:30%" />
              <el-input v-model="param.default" placeholder="默认值" style="width:30%" />
              <el-select v-model="param.type" placeholder="类型" style="width:20%">
                <el-option label="字符串" value="string" />
                <el-option label="日期" value="date" />
                <el-option label="整数" value="integer" />
              </el-select>
              <el-button type="danger" link @click="removeHttpParam(index)">删除</el-button>
            </div>
            <el-button type="primary" link @click="addHttpParam">+ 添加参数</el-button>
          </el-form-item>
        </template>

        <template v-if="form.type === 'json'">
          <el-divider>JSON 配置</el-divider>
          <el-form-item label="JSON文本">
            <el-input v-model="form.config.json_text" type="textarea" :rows="10" placeholder='{"data": [{"name": "张三", "age": 28}]}' />
          </el-form-item>
        </template>

        <template v-if="form.type === 'form'">
          <el-divider>表单字段配置</el-divider>
          <el-form-item label="自定义字段">
            <div v-for="(field, index) in form.config.fields" :key="index" class="kv-row">
              <el-input v-model="field.key" placeholder="字段名" style="width:40%" />
              <el-input v-model="field.value" placeholder="字段值" style="width:40%" />
              <el-button type="danger" link @click="removeField(index)">删除</el-button>
            </div>
            <el-button type="primary" link @click="addField">+ 添加字段</el-button>
          </el-form-item>
        </template>

        <template v-if="form.type === 'sql'">
          <el-divider>SQL 查询配置</el-divider>
          <el-form-item label="选择数据库">
            <el-select v-model="form.config.database_id" placeholder="请选择已配置的数据库" filterable>
              <el-option v-for="db in databaseList" :key="db.id" :label="db.name + ' (' + db.type + ')'" :value="db.id">
                <span>{{ db.name }}</span>
                <span style="color: #909399; font-size: 12px;"> ({{ db.type }})</span>
              </el-option>
            </el-select>
            <div class="form-tip">
              <router-link to="/database" target="_blank">配置新数据库</router-link>
            </div>
          </el-form-item>
          <el-form-item label="查询SQL">
            <el-input v-model="form.config.sql" type="textarea" :rows="5" placeholder="例如: SELECT * FROM users WHERE create_time >= :start_date" />
            <div class="form-tip">
              支持参数: <code>:start_date</code>, <code>:end_date</code>, <code>:year</code>, <code>:month</code> 等
            </div>
          </el-form-item>
          <el-form-item label="参数配置">
            <div v-for="(param, index) in form.config.params" :key="index" class="param-row">
              <el-input v-model="param.name" placeholder="参数名" style="width:30%" />
              <el-input v-model="param.default" placeholder="默认值" style="width:30%" />
              <el-select v-model="param.type" placeholder="类型" style="width:20%">
                <el-option label="字符串" value="string" />
                <el-option label="日期" value="date" />
                <el-option label="整数" value="integer" />
              </el-select>
              <el-button type="danger" link @click="removeParam(index)">删除</el-button>
            </div>
            <el-button type="primary" link @click="addParam">+ 添加参数</el-button>
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showTestDialog" title="测试结果" width="600px">
      <div v-if="testResult">
        <el-alert :type="testResult.success ? 'success' : 'error'" :title="testResult.message" :closable="false" />
        <div v-if="testResult.data" class="test-data">
          <pre>{{ JSON.stringify(testResult.data, null, 2) }}</pre>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="showFieldsDialog" title="变量" width="500px">
      <div v-if="currentDsFields.length > 0">
        <el-tag v-for="f in currentDsFields" :key="f" style="margin: 0 5px 5px 0">{{ f }}</el-tag>
      </div>
      <el-empty v-else description="暂无变量" />
    </el-dialog>

    <el-dialog v-model="showParamsDialog" title="入参" width="500px">
      <el-table v-if="currentDsParams.length > 0" :data="currentDsParams" border>
        <el-table-column prop="name" label="参数名" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="default" label="默认值" />
        <el-table-column prop="label" label="标签" />
      </el-table>
      <el-empty v-else description="暂无入参" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDataSources, createDataSource, updateDataSource, deleteDataSource, testDataSource } from '@/api/datasource'

const loading = ref(false)
const dataSourceList = ref([])
const databaseList = ref([])
const showDialog = ref(false)
const showTestDialog = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const testResult = ref(null)

const showFieldsDialog = ref(false)
const showParamsDialog = ref(false)
const currentDsFields = ref([])
const currentDsParams = ref([])

const showFields = (row) => {
  if (row.config?._fields?.length) {
    currentDsFields.value = row.config._fields
  } else if (row.type === 'json') {
    try {
      const data = JSON.parse(row.config?.json_text || '{}')
      currentDsFields.value = Object.keys(data)
    } catch {
      currentDsFields.value = []
    }
  } else if (row.type === 'form') {
    currentDsFields.value = (row.config?.fields || []).map(f => f.key).filter(k => k)
  } else {
    currentDsFields.value = []
  }
  showFieldsDialog.value = true
}

const showParams = (row) => {
  const params = row.config?.params || row.config?.parameters || []
  currentDsParams.value = params
  showParamsDialog.value = true
}
const formRef = ref()

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedDataSources = ref([])
const checkAll = ref(false)
const isIndeterminate = ref(false)

const form = reactive({
  name: '',
  type: 'http_api',
  config: {
    method: 'GET',
    url: '',
    headers: [],
    params: [],
    body: '',
    json_text: '',
    fields: []
  }
})

const rules = {
  name: [{ required: true, message: '请输入数据源名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择数据源类型', trigger: 'change' }]
}

const getTypeLabel = (type) => {
  const map = { http_api: 'HTTP API', json: '静态JSON', form: '表单输入', sql: 'SQL查询' }
  return map[type] || type
}

const getStatusLabel = (status) => {
  const map = { success: '成功', failed: '失败', unknown: '未测试' }
  return map[status] || '未测试'
}

const handleTypeChange = () => {
  if (form.type === 'http_api') {
    form.config = { method: 'GET', url: '', headers: [], params: [], body: '', parameters: [] }
  } else if (form.type === 'json') {
    form.config = { json_text: '' }
  } else if (form.type === 'form') {
    form.config = { fields: [] }
  } else if (form.type === 'sql') {
    form.config = { database_id: '', sql: '', params: [] }
  }
}

const addHeader = () => {
  form.config.headers.push({ key: '', value: '' })
}

const removeHeader = (index) => {
  form.config.headers.splice(index, 1)
}

const addParam = () => {
  form.config.params.push({ key: '', value: '' })
}

const removeParam = (index) => {
  form.config.params.splice(index, 1)
}

const addHttpParam = () => {
  if (!form.config.parameters) form.config.parameters = []
  form.config.parameters.push({ name: '', default: '', type: 'string' })
}

const removeHttpParam = (index) => {
  form.config.parameters.splice(index, 1)
}

const addField = () => {
  form.config.fields.push({ key: '', value: '' })
}

const removeField = (index) => {
  form.config.fields.splice(index, 1)
}

const resetForm = () => {
  form.name = ''
  form.type = 'http_api'
  form.config = { method: 'GET', url: '', headers: [], params: [], body: '', json_text: '', fields: [] }
}

const loadDataSources = async () => {
  loading.value = true
  try {
    const res = await getDataSources({
      page: currentPage.value,
      page_size: pageSize.value,
      type_filter: 'datasource'
    })
    if (res.items) {
      dataSourceList.value = res.items
      total.value = res.total || 0
    } else if (res.data) {
      dataSourceList.value = res.data
      total.value = res.total || 0
    } else {
      dataSourceList.value = res || []
      total.value = res?.length || 0
    }
  } catch (error) {
    ElMessage.error('加载数据源失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  loadDataSources()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadDataSources()
}

const handleSelectionChange = (selection) => {
  selectedDataSources.value = selection
  checkAll.value = selection.length === dataSourceList.value.length
  isIndeterminate.value = selection.length > 0 && selection.length < dataSourceList.value.length
}

const handleCheckAllChange = (val) => {
  selectedDataSources.value = val ? [...dataSourceList.value] : []
  isIndeterminate.value = false
}

const handleBatchDelete = async () => {
  if (selectedDataSources.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedDataSources.value.length} 个数据源吗？`, '批量删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    for (const ds of selectedDataSources.value) {
      await deleteDataSource(ds.id)
    }
    
    ElMessage.success('批量删除成功')
    selectedDataSources.value = []
    checkAll.value = false
    loadDataSources()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const config = { ...form.config }
        
        if (form.type === 'http_api') {
          config.headers = config.headers.filter(h => h.key)
          config.params = config.params.filter(p => p.key)
        } else if (form.type === 'form') {
          const fields = {}
          config.fields.forEach(f => {
            if (f.key) fields[f.key] = f.value
          })
          config.fields = fields
        }
        
        const data = {
          name: form.name,
          type: form.type,
          config
        }
        
        if (isEdit.value) {
          await updateDataSource(form.id, data)
          ElMessage.success('更新成功')
        } else {
          await createDataSource(data)
          ElMessage.success('创建成功')
        }
        
        showDialog.value = false
        loadDataSources()
      } catch (error) {
        ElMessage.error(error.message || '保存失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleEdit = (row) => {
  isEdit.value = true
  form.id = row.id
  form.name = row.name
  form.type = row.type
  
  const config = { ...row.config }
  if (row.type === 'http_api') {
    config.headers = config.headers || []
    config.params = config.params || []
  } else if (row.type === 'form') {
    const fields = []
    for (const [key, value] of Object.entries(config.fields || {})) {
      fields.push({ key, value })
    }
    config.fields = fields
  }
  form.config = config
  
  showDialog.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该数据源吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteDataSource(row.id)
      ElMessage.success('删除成功')
      loadDataSources()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleTest = async (row) => {
  loading.value = true
  testResult.value = null
  
  try {
    const config = { ...row.config }
    if (row.type === 'form' && config.fields) {
      if (Array.isArray(config.fields)) {
        const fields = {}
        config.fields.forEach(f => {
          if (f.key) fields[f.key] = f.value
        })
        config.fields = fields
      }
    }
    
    const res = await testDataSource({
      type: row.type,
      config,
      ds_id: row.id
    })
    testResult.value = res
    showTestDialog.value = true
    
    if (res.success) {
      row.status = 'success'
      const idx = dataSourceList.value.findIndex(d => d.id === row.id)
      if (idx !== -1) dataSourceList.value[idx].status = 'success'
    } else {
      row.status = 'failed'
      const idx = dataSourceList.value.findIndex(d => d.id === row.id)
      if (idx !== -1) dataSourceList.value[idx].status = 'failed'
    }
  } catch (error) {
    ElMessage.error('测试失败')
    row.status = 'failed'
  } finally {
    loading.value = false
  }
}

const loadDatabases = async () => {
  try {
    const res = await getDataSources({ page: 1, page_size: 100, type_filter: 'database' })
    databaseList.value = res.data || []
  } catch (error) {
    console.error('加载数据库列表失败', error)
  }
}

onMounted(() => {
  loadDataSources()
  loadDatabases()
})
</script>

<style scoped>
.datasource-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.kv-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.test-data {
  margin-top: 15px;
  max-height: 300px;
  overflow: auto;
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
}

.test-data pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.form-tip a {
  color: #409eff;
}

.form-tip code {
  background: #f0f2f5;
  padding: 2px 6px;
  border-radius: 3px;
  margin: 0 2px;
}

.param-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}
</style>