<template>
  <div class="generate-page">
    <el-card>
      <template #header>
        <span>生成文档</span>
      </template>
      <div v-if="dataLoading" v-loading="dataLoading" style="min-height:200px"></div>
      <el-empty v-else-if="mappingList.length === 0 || templateList.length === 0 || dataSourceList.length === 0" :description="emptyMessage">
        <template #extra>
          <el-button type="primary" @click="goToConfig">前往配置</el-button>
        </template>
      </el-empty>
      <el-form v-else :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="映射配置" prop="mappingId">
          <el-select v-model="form.mappingId" placeholder="请选择映射配置" style="width:300px" @change="handleMappingChange">
            <el-option v-for="item in mappingList" :key="item.id" :label="item.name" :value="item.id">
              <span>{{ item.name }}</span>
              <span style="float:right;color:#999;font-size:12px">
                {{ getTemplateName(item.template_id) }} / {{ getDatasourceNames(item.datasource_ids) }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="文档名称" prop="outputName">
          <el-input v-model="form.outputName" placeholder="请输入文档名称（可选）" style="width:300px" />
        </el-form-item>
        
        <template v-if="requiredParams.length > 0">
          <el-divider>数据源参数</el-divider>
          <el-form-item v-for="param in requiredParams" :key="param.name" :label="param.label || param.name">
            <el-input 
              v-model="runtimeParams[param.name]" 
              :placeholder="param.required ? '必填' : '可选'"
              style="width:300px"
            />
            <span style="font-size:12px;color:#999;margin-left:10px">
              {{ param.datasource_name }}
            </span>
          </el-form-item>
        </template>
        
        <el-form-item>
          <el-button type="primary" @click="handleGenerate" :loading="generating" :disabled="!form.mappingId">
            生成文档
          </el-button>
          <el-button @click="handlePreview" :disabled="!form.mappingId" :loading="previewLoading">
            预览数据
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card v-if="showPreview" style="margin-top:20px">
      <template #header>
        <span>数据预览</span>
      </template>
      <div v-if="previewLoading" v-loading="previewLoading" style="min-height:200px"></div>
      <el-empty v-else-if="!previewData && !previewError" description="暂无数据" />
      <div v-else>
        <el-alert v-if="previewError" :title="previewError" type="error" :closable="false" style="margin-bottom:15px" show-icon />
        <el-table v-if="Array.isArray(previewData) && previewData.length > 0" :data="previewData" border max-height="400">
          <el-table-column v-for="col in previewColumns" :key="col" :prop="col" :label="col" show-overflow-tooltip />
        </el-table>
        <pre v-else-if="previewData && !Array.isArray(previewData)" class="json-preview">{{ JSON.stringify(previewData, null, 2) }}</pre>
        <el-empty v-else-if="!previewError" description="无数据" />
      </div>
    </el-card>
    
    <el-card v-if="result" style="margin-top:20px">
      <template #header>
        <span>生成结果</span>
      </template>
      <el-result
        :icon="result.status === '成功' ? 'success' : 'error'"
        :title="result.status"
        :sub-title="result.message"
      >
        <template #extra>
          <el-button v-if="result.download_url" type="primary" @click="handleDownload(result)">
            下载文档
          </el-button>
          <el-button @click="resetResult">重新生成</el-button>
        </template>
      </el-result>
      <div class="result-info" v-if="result.id">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文档名称">{{ result.name }}</el-descriptions-item>
          <el-descriptions-item label="模板">{{ result.template }}</el-descriptions-item>
          <el-descriptions-item label="数据源">{{ result.datasource }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ result.file_size }}</el-descriptions-item>
          <el-descriptions-item label="生成时间" :span="2">{{ result.create_time }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getMappings } from '@/api/mapping'
import { getTemplates } from '@/api/template'
import { getDataSources } from '@/api/datasource'
import { generateDocument, previewData as previewDataApi, downloadDocument, getMappingParams } from '@/api/document'

const router = useRouter()
const formRef = ref()
const generating = ref(false)
const dataLoading = ref(true)
const showPreview = ref(false)
const previewLoading = ref(false)
const previewError = ref('')
const previewData = ref(null)
const previewColumns = ref([])
const result = ref(null)

const paramsLoading = ref(false)
const requiredParams = ref([])
const runtimeParams = reactive({})

const form = reactive({
  mappingId: '',
  outputName: ''
})

const rules = {
  mappingId: [{ required: true, message: '请选择映射配置', trigger: 'change' }]
}

const mappingList = ref([])
const templateList = ref([])
const dataSourceList = ref([])
const templateMap = ref({})
const datasourceMap = ref({})

const emptyMessage = computed(() => {
  if (templateList.value.length === 0) return '暂无模板，请先上传模板'
  if (dataSourceList.value.length === 0) return '暂无数据源，请先配置数据源'
  if (mappingList.value.length === 0) return '暂无映射配置，请先创建映射'
  return '请先配置必要的资源'
})

const loadData = async () => {
  dataLoading.value = true
  try {
    const [mappingRes, templateRes, datasourceRes] = await Promise.all([
      getMappings({ page: 1, page_size: 100 }),
      getTemplates({ page: 1, page_size: 100 }),
      getDataSources({ page: 1, page_size: 100 })
    ])
    
    const normalizeList = (res) => {
      if (Array.isArray(res)) return res
      if (Array.isArray(res?.items)) return res.items
      if (Array.isArray(res?.data)) return res.data
      return []
    }
    
    const mappings = normalizeList(mappingRes)
    const templates = normalizeList(templateRes)
    const datasources = normalizeList(datasourceRes)
    
    mappingList.value = mappings
    templateList.value = templates
    dataSourceList.value = datasources
    
    templates.forEach(t => { templateMap.value[t.id] = t.name })
    datasources.forEach(d => { datasourceMap.value[d.id] = d.name })
  } catch (e) {
    ElMessage.error('加载数据失败: ' + (e.message || '请检查网络连接'))
  } finally {
    dataLoading.value = false
  }
}

const getTemplateName = (id) => templateMap.value[id] || '未知'
const getDatasourceName = (id) => datasourceMap.value[id] || '未知'
const getDatasourceNames = (ids) => {
  if (!ids || !Array.isArray(ids)) {
    return getDatasourceName(ids) || '未知'
  }
  return ids.map(id => datasourceMap.value[id] || `数据源${id}`).join('、')
}

const goToConfig = () => {
  if (templateList.value.length === 0) {
    router.push('/template')
  } else if (dataSourceList.value.length === 0) {
    router.push('/datasource')
  } else {
    router.push('/mapping')
  }
}

const handleMappingChange = async () => {
  showPreview.value = false
  result.value = null
  
  if (!form.mappingId) return
  
  try {
    paramsLoading.value = true
    const res = await getMappingParams(form.mappingId)
    requiredParams.value = res.params || []
    
    requiredParams.value.forEach(p => {
      runtimeParams[p.name] = p.default || ''
    })
  } catch (e) {
    console.error('获取参数失败:', e)
  } finally {
    paramsLoading.value = false
  }
}

const fetchRequiredParams = async () => {
  if (!form.mappingId) return
  
  try {
    paramsLoading.value = true
    const res = await getMappingParams(form.mappingId)
    requiredParams.value = res.params || []
    
    requiredParams.value.forEach(p => {
      runtimeParams[p.name] = p.default || ''
    })
    await doGenerate(runtimeParams)
  } catch (e) {
    ElMessage.error('获取参数失败: ' + (e.message || '请检查网络连接'))
  } finally {
    paramsLoading.value = false
  }
}

const doGenerate = async (params) => {
  generating.value = true
  result.value = null
  
  try {
    const res = await generateDocument({
      mapping_id: form.mappingId,
      output_name: form.outputName || undefined,
      params: params
    })
    
    result.value = {
      ...res,
      status: '成功',
      message: '文档生成成功'
    }
    
    ElMessage.success('文档生成成功')
  } catch (e) {
    const errorMsg = e.message || '生成失败，请检查配置后重试'
    result.value = {
      status: '失败',
      message: errorMsg
    }
    ElMessage.error(errorMsg)
  } finally {
    generating.value = false
  }
}

const handleGenerate = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      await doGenerate(runtimeParams)
    }
  })
}

const handlePreview = async () => {
  if (!form.mappingId) return
  
  const mapping = mappingList.value.find(m => m.id === form.mappingId)
  if (!mapping) return
  
  showPreview.value = true
  previewLoading.value = true
  previewError.value = ''
  previewData.value = null
  previewColumns.value = []
  
  try {
    const dsIds = mapping.datasource_ids || (mapping.datasource_id ? [mapping.datasource_id] : [])
    if (dsIds.length === 0) {
      previewError.value = '未配置数据源'
      previewLoading.value = false
      return
    }
    
    if (dsIds.length === 1) {
      const res = await previewDataApi(dsIds[0])
      if (res.columns) {
        previewColumns.value = res.columns
        previewData.value = res.data
      } else if (res.data) {
        if (Array.isArray(res.data)) {
          previewColumns.value = res.data.length > 0 ? Object.keys(res.data[0]) : []
          previewData.value = res.data
        } else {
          previewData.value = res.data
        }
      }
    } else {
      const allData = {}
      const allColumns = []
      for (const dsId of dsIds) {
        try {
          const res = await previewDataApi(dsId)
          const dsName = datasourceMap.value[dsId] || `数据源${dsId}`
          const data = res.data || res
          allData[dsName] = data
          if (Array.isArray(data) && data.length > 0) {
            Object.keys(data[0]).forEach(k => {
              if (!allColumns.includes(k)) allColumns.push(k)
            })
          } else if (typeof data === 'object') {
            Object.keys(data).forEach(k => {
              if (!allColumns.includes(k)) allColumns.push(k)
            })
          }
        } catch (e) {
          allData[`数据源${dsId}`] = { error: e.message || '加载失败' }
        }
      }
      previewColumns.value = allColumns
      previewData.value = allData
    }
  } catch (e) {
    previewError.value = e.message || '预览失败，请检查数据源配置'
  } finally {
    previewLoading.value = false
  }
}

const handleDownload = async (item) => {
  try {
    const blob = await downloadDocument(item.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    let fileName = item.name || `document_${item.id}`
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

const resetResult = () => {
  result.value = null
  form.outputName = ''
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.generate-page {
  padding: 0;
}

.json-preview {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  max-height: 400px;
  overflow: auto;
  font-size: 12px;
}

.result-info {
  margin-top: 20px;
}
</style>