<template>
  <div class="history-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-checkbox v-if="historyList.length > 0" v-model="checkAll" :indeterminate="isIndeterminate" @change="handleCheckAllChange">全选</el-checkbox>
            <el-button v-if="selectedItems.length > 0" type="danger" size="small" @click="handleBatchDelete">
              批量删除 ({{ selectedItems.length }})
            </el-button>
          </div>
          <div class="header-actions">
            <el-input v-model="searchText" placeholder="搜索文档名称" style="width:200px" prefix-icon="Search" @input="handleSearch" />
            <el-select v-model="statusFilter" placeholder="状态筛选" style="margin-left:10px;width:120px" clearable @change="loadHistory">
              <el-option label="成功" value="成功" />
              <el-option label="失败" value="失败" />
            </el-select>
          </div>
        </div>
      </template>
      <el-table :data="historyList" v-loading="loading" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <template #empty>
          <el-empty description="暂无生成记录">
            <template #extra>
              <el-button type="primary" @click="$router.push('/generate')">前往生成</el-button>
            </template>
          </el-empty>
        </template>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="文档名称" width="200" show-overflow-tooltip />
        <el-table-column prop="template" label="模板" width="120" />
        <el-table-column prop="datasource" label="数据源" width="120" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === '成功' ? 'success' : row.status === '生成中' ? 'warning' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="生成时间" width="180" />
        <el-table-column prop="file_size" label="文件大小" width="100" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button v-if="row.status === '成功'" type="primary" link @click="handleDownload(row)">下载</el-button>
            <el-button type="primary" link @click="handleRegenerate(row)">重新生成</el-button>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getHistory, deleteHistory, regenerateDocument, downloadDocument } from '@/api/document'

const loading = ref(false)
const searchText = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const historyList = ref([])
const selectedItems = ref([])
const checkAll = ref(false)
const isIndeterminate = ref(false)

let searchTimer = null
const handleSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadHistory()
  }, 300)
}

const loadHistory = async () => {
  loading.value = true
  try {
    const res = await getHistory({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchText.value || undefined,
      status: statusFilter.value || undefined
    })
    
    historyList.value = res.data || []
    total.value = res.total || 0
  } catch (e) {
    ElMessage.error('加载历史记录失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  loadHistory()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadHistory()
}

const handleDownload = async (row) => {
  try {
    const response = await downloadDocument(row.id)
    
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    let fileName = row.name || `document_${row.id}`
    if (!fileName.endsWith('.docx')) {
      fileName += '.docx'
    }
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载成功')
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

const handleRegenerate = async (row) => {
  try {
    await ElMessageBox.confirm('确定要重新生成此文档吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const res = await regenerateDocument(row.id)
    ElMessage.success('重新生成成功')
    loadHistory()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || '重新生成失败')
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除此记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteHistory(row.id)
    ElMessage.success('删除成功')
    loadHistory()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || '删除失败')
    }
  }
}

const handleSelectionChange = (selection) => {
  selectedItems.value = selection
  checkAll.value = selection.length === historyList.value.length
  isIndeterminate.value = selection.length > 0 && selection.length < historyList.value.length
}

const handleCheckAllChange = (val) => {
  selectedItems.value = val ? [...historyList.value] : []
  isIndeterminate.value = false
}

const handleBatchDelete = async () => {
  if (selectedItems.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedItems.value.length} 条记录吗？`, '批量删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    for (const item of selectedItems.value) {
      await deleteHistory(item.id)
    }
    
    ElMessage.success('批量删除成功')
    selectedItems.value = []
    checkAll.value = false
    loadHistory()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-page {
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

.header-actions {
  display: flex;
  align-items: center;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>