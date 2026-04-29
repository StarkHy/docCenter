<template>
  <div class="database-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-checkbox v-if="dbList.length > 0" v-model="checkAll" :indeterminate="isIndeterminate" @change="handleCheckAllChange">全选</el-checkbox>
            <el-button v-if="selectedDbs.length > 0" type="danger" size="small" @click="handleBatchDelete">
              批量删除 ({{ selectedDbs.length }})
            </el-button>
          </div>
          <el-button type="primary" @click="showDialog = true; isEdit = false; resetForm()">
            新增数据库
          </el-button>
        </div>
      </template>
      <el-table :data="dbList" v-loading="loading" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <template #empty>
          <el-empty description="暂无数据库配置">
            <template #extra>
              <el-button type="primary" @click="showDialog = true; isEdit = false; resetForm()">新增数据库</el-button>
            </template>
          </el-empty>
        </template>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="数据库名称" />
        <el-table-column prop="db_type" label="数据库类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ getDbTypeLabel(row.db_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="host" label="主机" width="180">
          <template #default="{ row }">
            {{ row.host || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="database" label="数据库名" width="120">
          <template #default="{ row }">
            {{ row.database || row.service_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="200">
          <template #default="{ row }">
            {{ row.version || '-' }}
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
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleTest(row)">测试</el-button>
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

    <el-dialog v-model="showDialog" :title="isEdit ? '编辑数据库' : '新增数据库'" width="700px" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="130px">
        <el-form-item label="数据库名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入数据库名称，如：生产库" />
        </el-form-item>
        <el-form-item label="数据库类型" prop="db_type">
          <el-select v-model="form.db_type" placeholder="请选择类型" @change="handleTypeChange">
            <el-option label="Kingbase (人大金仓)" value="kingbase" />
            <el-option label="MySQL" value="mysql" />
            <el-option label="Oracle" value="oracle" />
            <el-option label="PostgreSQL" value="postgresql" />
          </el-select>
        </el-form-item>

        <template v-if="form.db_type === 'kingbase' || form.db_type === 'postgresql'">
          <el-divider>连接配置</el-divider>
          <el-form-item label="主机地址">
            <el-input v-model="form.host" placeholder="例如: 192.168.1.100" />
          </el-form-item>
          <el-form-item label="端口">
            <el-input v-model="form.port" :placeholder="form.db_type === 'kingbase' ? '默认: 54321' : '默认: 5432'" />
          </el-form-item>
          <el-form-item label="数据库名">
            <el-input v-model="form.database" placeholder="例如: mydb" />
          </el-form-item>
          <el-form-item label="用户名">
            <el-input v-model="form.user" placeholder="用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" placeholder="密码" show-password />
          </el-form-item>
        </template>

        <template v-if="form.db_type === 'mysql'">
          <el-divider>连接配置</el-divider>
          <el-form-item label="主机地址">
            <el-input v-model="form.host" placeholder="例如: 192.168.1.100" />
          </el-form-item>
          <el-form-item label="端口">
            <el-input v-model="form.port" placeholder="默认: 3306" />
          </el-form-item>
          <el-form-item label="数据库名">
            <el-input v-model="form.database" placeholder="例如: mydb" />
          </el-form-item>
          <el-form-item label="用户名">
            <el-input v-model="form.user" placeholder="用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" placeholder="密码" show-password />
          </el-form-item>
        </template>

        <template v-if="form.db_type === 'oracle'">
          <el-divider>连接配置</el-divider>
          <el-form-item label="连接方式">
            <el-radio-group v-model="form.connect_mode">
              <el-radio label="service">服务名</el-radio>
              <el-radio label="desc">连接描述</el-radio>
            </el-radio-group>
          </el-form-item>
          <template v-if="form.connect_mode === 'service'">
            <el-form-item label="主机地址">
              <el-input v-model="form.host" placeholder="例如: 192.168.1.100" />
            </el-form-item>
            <el-form-item label="端口">
              <el-input v-model="form.port" placeholder="默认: 1521" />
            </el-form-item>
            <el-form-item label="服务名">
              <el-input v-model="form.service_name" placeholder="例如: ORCL" />
            </el-form-item>
          </template>
          <template v-else>
            <el-form-item label="连接描述">
              <el-input v-model="form.service" type="textarea" :rows="2" placeholder="(description=(address=(host=xxx)(port=1521)(protocol=tcp))(connect_data=(service_name=orcl)))" />
            </el-form-item>
          </template>
          <el-form-item label="用户名">
            <el-input v-model="form.user" placeholder="用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" placeholder="密码" show-password />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="success" @click="handleTestConnection" :loading="testing" :disabled="!canTest">
          测试连接
        </el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting" :disabled="!testPassed">
          保存
        </el-button>
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDatabases, createDatabase, updateDatabase, deleteDatabase, testDatabase, testDatabaseConnection } from '@/api/database'

const loading = ref(false)
const dbList = ref([])
const showDialog = ref(false)
const showTestDialog = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const testing = ref(false)
const testPassed = ref(false)
const testResult = ref(null)
const formRef = ref()

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedDbs = ref([])
const checkAll = ref(false)

const form = reactive({
  id: null,
  name: '',
  db_type: 'postgresql',
  host: '',
  port: '5432',
  database: '',
  user: '',
  password: '',
  service_name: '',
  connect_mode: 'service'
})

const rules = {
  name: [{ required: true, message: '请输入数据库名称', trigger: 'blur' }],
  db_type: [{ required: true, message: '请选择数据库类型', trigger: 'change' }]
}

const canTest = computed(() => {
  return form.name && form.db_type && form.host && form.database && form.user
})

const resetTestPassed = () => {
  testPassed.value = false
}

watch(
  () => ({ ...form }),
  () => { testPassed.value = false },
  { deep: true }
)

const getDbTypeLabel = (type) => {
  const map = { kingbase: 'Kingbase', mysql: 'MySQL', oracle: 'Oracle', postgresql: 'PostgreSQL' }
  return map[type] || type || 'unknown'
}

const getStatusLabel = (status) => {
  const map = { success: '成功', failed: '失败', unknown: '未测试' }
  return map[status] || '未测试'
}

const handleTypeChange = () => {
  resetTestPassed()
  if (form.db_type === 'kingbase') {
    form.port = '54321'
  } else if (form.db_type === 'mysql') {
    form.port = '3306'
  } else if (form.db_type === 'oracle') {
    form.port = '1521'
  } else if (form.db_type === 'postgresql') {
    form.port = '5432'
  }
}

const loadDatabases = async () => {
  loading.value = true
  try {
    const res = await getDatabases({ page: currentPage.value, page_size: pageSize.value })
    dbList.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const handleTestConnection = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    testing.value = true
    testPassed.value = false
    try {
      const res = await testDatabaseConnection({
        name: form.name,
        db_type: form.db_type,
        host: form.host,
        port: form.port,
        database: form.database,
        user: form.user,
        password: form.password,
        service_name: form.service_name,
        connect_mode: form.connect_mode
      })
      testResult.value = res
      if (res.success) {
        testPassed.value = true
        ElMessage.success('连接测试成功')
      } else {
        ElMessage.error(res.message || '连接测试失败')
      }
    } catch (error) {
      ElMessage.error(error.message || '测试请求失败')
    } finally {
      testing.value = false
    }
  })
}

const handleTest = async (row) => {
  try {
    const res = await testDatabase(row.id)
    testResult.value = res
    showTestDialog.value = true
    if (res.success) {
      row.status = 'success'
    } else {
      row.status = 'failed'
    }
  } catch (error) {
    ElMessage.error(error.message || '测试失败')
    row.status = 'failed'
  }
}

const handleEdit = (row) => {
  isEdit.value = true
  form.id = row.id
  form.name = row.name
  form.db_type = row.db_type
  form.host = row.host
  form.port = row.port
  form.database = row.database
  form.user = row.user
  form.password = row.password
  form.service_name = row.service_name
  form.connect_mode = row.connect_mode || 'service'
  showDialog.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该数据库配置吗？', '提示', { type: 'warning' })
    await deleteDatabase(row.id)
    ElMessage.success('删除成功')
    loadDatabases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleSelectionChange = (selection) => {
  selectedDbs.value = selection
}

const handleCheckAllChange = (checked) => {
  selectedDbs.value = checked ? [...dbList.value] : []
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedDbs.value.length} 个数据库配置吗？`, '提示', { type: 'warning' })
    for (const db of selectedDbs.value) {
      await deleteDataSource(db.id)
    }
    ElMessage.success('批量删除成功')
    loadDatabases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  loadDatabases()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadDatabases()
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.db_type = 'postgresql'
  form.host = ''
  form.port = '5432'
  form.database = ''
  form.user = ''
  form.password = ''
  form.service_name = ''
  form.connect_mode = 'service'
}

const handleSubmit = async () => {
  if (!testPassed.value) {
    ElMessage.warning('请先测试连接，确保数据库可访问')
    return
  }
  try {
    await formRef.value.validate()
    submitting.value = true
    
    const data = {
      name: form.name,
      db_type: form.db_type,
      host: form.host,
      port: form.port,
      database: form.database,
      user: form.user,
      password: form.password,
      service_name: form.service_name,
      connect_mode: form.connect_mode
    }
    
    if (isEdit.value) {
      await updateDatabase(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await createDatabase(data)
      ElMessage.success('创建成功')
    }
    
    showDialog.value = false
    loadDatabases()
  } catch (error) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadDatabases()
})
</script>

<style scoped>
.database-page {
  width: 100%;
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

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
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
</style>