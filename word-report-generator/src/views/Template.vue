<template>
  <div class="template-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-checkbox v-if="templateList.length > 0" v-model="checkAll" :indeterminate="isIndeterminate" @change="handleCheckAllChange">全选</el-checkbox>
            <el-button v-if="selectedTemplates.length > 0" type="danger" size="small" @click="handleBatchDelete">
              批量删除 ({{ selectedTemplates.length }})
            </el-button>
          </div>
          <el-button type="primary" @click="showUploadDialog = true">
            上传模板
          </el-button>
        </div>
      </template>
      <el-table :data="templateList" v-loading="loading" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="模板名称" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="file_name" label="文件名称" width="200" />
        <el-table-column prop="file_size" label="大小" width="100">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="variables" label="变量" width="150">
          <template #default="{ row }">
            <el-tag v-if="row.variables && row.variables.length > 0" size="small">
              {{ row.variables.length }} 个变量
            </el-tag>
            <span v-else class="no-vars">无变量</span>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="showVariables(row)">变量</el-button>
            <el-button type="primary" link @click="handleDownload(row)">下载</el-button>
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

    <el-dialog v-model="showUploadDialog" title="上传模板" width="500px">
      <el-form ref="uploadFormRef" :model="uploadForm" :rules="uploadRules" label-width="100px">
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="uploadForm.name" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="uploadForm.category" placeholder="请选择分类">
            <el-option label="报表" value="报表" />
            <el-option label="项目" value="项目" />
            <el-option label="人事" value="人事" />
            <el-option label="财务" value="财务" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择文件" prop="file">
          <el-upload
            ref="uploadRef"
            class="template-upload"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            :before-upload="beforeUpload"
            accept=".docx"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="upload-tip">仅支持 .docx 格式，最大 100MB</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">上传</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showVarsDialog" title="模板变量" width="500px">
      <div v-if="currentTemplate && currentTemplate.variables">
        <el-tag v-for="v in currentTemplate.variables" :key="v" class="var-tag">
          {{ v }}
        </el-tag>
        <el-empty v-if="currentTemplate.variables.length === 0" description="无变量" />
      </div>
      <el-empty v-else description="无法获取变量信息" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTemplates, uploadTemplate, deleteTemplate, downloadTemplate } from '@/api/template'

const loading = ref(false)
const templateList = ref([])
const showUploadDialog = ref(false)
const showVarsDialog = ref(false)
const uploading = ref(false)
const currentTemplate = ref(null)
const uploadFormRef = ref()
const uploadRef = ref()
const uploadForm = reactive({
  name: '',
  category: '',
  file: null
})

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedTemplates = ref([])
const checkAll = ref(false)
const isIndeterminate = ref(false)

const uploadRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  const mb = bytes / 1024 / 1024
  return mb < 1 ? `${(bytes / 1024).toFixed(1)} KB` : `${mb.toFixed(2)} MB`
}

const loadTemplates = async () => {
  loading.value = true
  try {
    const res = await getTemplates({
      page: currentPage.value,
      page_size: pageSize.value
    })
    if (res.items) {
      templateList.value = res.items
      total.value = res.total || 0
    } else if (res.data) {
      templateList.value = res.data
      total.value = res.total || 0
    } else {
      templateList.value = res || []
      total.value = res?.length || 0
    }
  } catch (error) {
    ElMessage.error('加载模板失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  loadTemplates()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadTemplates()
}

const handleSelectionChange = (selection) => {
  selectedTemplates.value = selection
  checkAll.value = selection.length === templateList.value.length
  isIndeterminate.value = selection.length > 0 && selection.length < templateList.value.length
}

const handleCheckAllChange = (val) => {
  selectedTemplates.value = val ? [...templateList.value] : []
  isIndeterminate.value = false
}

const handleBatchDelete = async () => {
  if (selectedTemplates.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedTemplates.value.length} 个模板吗？`, '批量删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    for (const template of selectedTemplates.value) {
      await deleteTemplate(template.id)
    }
    
    ElMessage.success('批量删除成功')
    selectedTemplates.value = []
    checkAll.value = false
    loadTemplates()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const beforeUpload = (file) => {
  const isDocx = file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || 
                 file.name.endsWith('.docx')
  const isLt100M = file.size / 1024 / 1024 < 100
  
  if (!isDocx) {
    ElMessage.error('只能上传 .docx 格式的文件')
    return false
  }
  if (!isLt100M) {
    ElMessage.error('文件大小不能超过 100MB')
    return false
  }
  return false
}

const handleFileChange = (file) => {
  uploadForm.file = file.raw
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const handleUpload = async () => {
  if (!uploadForm.file) {
    ElMessage.warning('请选择文件')
    return
  }
  
  if (!uploadFormRef.value) return
  
  await uploadFormRef.value.validate(async (valid) => {
    if (valid) {
      uploading.value = true
      try {
        const formData = new FormData()
        formData.append('name', uploadForm.name)
        formData.append('category', uploadForm.category)
        formData.append('file', uploadForm.file)
        await uploadTemplate(formData)
        ElMessage.success('上传成功')
        showUploadDialog.value = false
        uploadFormRef.value?.resetFields()
        uploadForm.file = null
        uploadRef.value?.clearFiles()
        loadTemplates()
      } catch (error) {
        ElMessage.error(error.message || '上传失败，请检查文件格式')
      } finally {
        uploading.value = false
      }
    }
  })
}

const showVariables = (row) => {
  currentTemplate.value = row
  showVarsDialog.value = true
}

const handleDownload = async (row) => {
  try {
    const blob = await downloadTemplate(row.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = row.file_name
    document.body.appendChild(link)
    link.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(link)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该模板吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteTemplate(row.id)
      ElMessage.success('删除成功')
      loadTemplates()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.template-page {
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

.upload-tip {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.no-vars {
  color: #999;
  font-size: 12px;
}

.var-tag {
  margin: 4px;
}
</style>