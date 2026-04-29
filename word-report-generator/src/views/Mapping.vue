<template>
  <div class="mapping-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-checkbox v-if="mappingList.length > 0" v-model="checkAll" :indeterminate="isIndeterminate" @change="handleCheckAllChange">全选</el-checkbox>
            <el-button v-if="selectedMappings.length > 0" type="danger" size="small" @click="handleBatchDelete">
              批量删除 ({{ selectedMappings.length }})
            </el-button>
          </div>
          <el-button type="primary" @click="handleAdd">
            新增映射
          </el-button>
        </div>
      </template>
      <el-table :data="mappingList" v-loading="loading" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <template #empty>
          <el-empty :description="emptyDescription">
            <template #extra>
              <el-button type="primary" @click="handleAdd">新增映射</el-button>
            </template>
          </el-empty>
        </template>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="映射名称" />
        <el-table-column prop="template_id" label="模板" width="150">
          <template #default="{ row }">
            {{ getTemplateName(row.template_id) }}
          </template>
        </el-table-column>
        <el-table-column label="数据源" width="200">
          <template #default="{ row }">
            {{ getDataSourceNames(row.datasource_ids) }}
          </template>
        </el-table-column>
        <el-table-column prop="mappings" label="映射数量" width="100">
          <template #default="{ row }">
            {{ row.mappings?.length || 0 }} 个
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
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

    <el-dialog v-model="showDialog" :title="isEdit ? '编辑映射' : '新增映射'" width="900px" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="映射名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入映射名称" style="width:300px" />
        </el-form-item>
        <el-form-item label="选择模板" prop="template_id">
          <el-select v-model="form.template_id" placeholder="请选择模板" style="width:300px" @change="handleTemplateChange">
            <el-option v-for="t in templateList" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择数据源" prop="datasource_ids">
          <el-select
            v-model="form.datasource_ids"
            multiple
            placeholder="请选择数据源（可多选）"
            style="width:500px"
            @change="handleDataSourceChange"
          >
            <el-option v-for="ds in dataSourceList" :key="ds.id" :label="ds.name" :value="ds.id" />
          </el-select>
        </el-form-item>

        <el-divider>字段映射配置</el-divider>

        <div v-if="form.datasource_ids.length > 0" class="mapping-config">
          <div class="mapping-panel left">
            <div class="panel-header">
              <span>模板变量</span>
              <el-button type="primary" link @click="handleAutoMatch">自动匹配</el-button>
            </div>
            <div class="panel-content">
              <div v-if="templateVariables.length === 0" class="empty-tip">请先选择模板</div>
              <div v-else>
                <div v-for="v in templateVariables" :key="v" class="var-item" @click="addMappingWithVariable(v)">
                  {{ v }}
                </div>
              </div>
            </div>
          </div>

          <div class="mapping-arrows">
            <el-button type="primary" link @click="handleAutoMatch">
              自动匹配
            </el-button>
          </div>

          <div class="mapping-panel right">
            <div class="panel-header">
              <span>数据源字段</span>
              <el-icon v-if="fieldsLoading" class="is-loading"><Loading /></el-icon>
            </div>
            <div class="panel-content">
              <div v-if="fieldsLoading" class="empty-tip">加载中...</div>
              <div v-else-if="allDataSourceFields.length === 0" class="empty-tip">请先选择数据源</div>
              <div v-else>
                <div v-for="f in allDataSourceFields" :key="f.key" class="var-item">
                  <el-tag size="small" :type="getDatasourceTagType(f.datasourceId)" style="margin-right:6px">{{ f.datasourceName }}</el-tag>
                  {{ f.field }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <el-divider>映射关系</el-divider>

        <div class="mapping-list">
          <div v-for="(map, index) in form.mappings" :key="index" class="mapping-row">
            <el-select
              v-model="map.target"
              placeholder="选择模板变量"
              style="width:150px"
              allow-create
              filterable
              default-first-option
            >
              <el-option
                v-for="v in templateVariables"
                :key="v"
                :label="v"
                :value="v"
              />
            </el-select>
            <span class="arrow">←</span>
            <el-select
              v-model="map.datasource_id"
              placeholder="数据源"
              style="width:140px"
            >
              <el-option
                v-for="ds in selectedDataSources"
                :key="ds.id"
                :label="ds.name"
                :value="ds.id"
              />
            </el-select>
            <el-select
              v-model="map.source"
              placeholder="选择字段"
              style="width:200px"
              allow-create
              filterable
            >
              <el-option
                v-for="f in getFieldsForDatasource(map.datasource_id)"
                :key="f"
                :label="f"
                :value="f"
              />
            </el-select>
            <el-button type="danger" link @click="removeMapping(index)">删除</el-button>
          </div>
          <el-button type="primary" link @click="addMapping" v-if="templateVariables.length > 0">+ 添加映射</el-button>
        </div>
        
        <el-divider>图表配置</el-divider>
        
        <div class="chart-list">
          <div v-for="(chart, index) in form.charts" :key="index" class="chart-row">
            <el-row :gutter="16">
              <el-col :span="6">
                <el-input v-model="chart.id" placeholder="图表ID" />
              </el-col>
              <el-col :span="6">
                <el-select v-model="chart.type" placeholder="图表类型">
                  <el-option label="柱状图 (bar)" value="bar" />
                  <el-option label="折线图 (line)" value="line" />
                  <el-option label="饼图 (pie)" value="pie" />
                  <el-option label="组合图 (combo)" value="combo" />
                  <el-option label="堆叠柱状图 (stack)" value="stack" />
                  <el-option label="环形图 (donut)" value="donut" />
                  <el-option label="散点图 (scatter)" value="scatter" />
                  <el-option label="沉降历时曲线 (settlement_duration)" value="settlement_duration" />
                  <el-option label="水位历时曲线 (waterlevel_duration)" value="waterlevel_duration" />
                  <el-option label="沉降水位对比图 (comparison)" value="settlement_waterlevel_comparison" />
                </el-select>
              </el-col>
              <el-col :span="12">
                <el-input v-model="chart.title" placeholder="图表标题" />
              </el-col>
            </el-row>
            
            <el-row :gutter="16" style="margin-top:8px">
              <el-col :span="6">
                <el-select v-model="chart.datasource_id" placeholder="选择数据源" clearable @change="onChartDatasourceChange(index)">
                  <el-option v-for="ds in selectedDataSources" :key="ds.id" :label="ds.name" :value="ds.id" />
                </el-select>
              </el-col>
              <el-col :span="6">
                <el-select v-model="chart.x_field" placeholder="X轴字段" clearable filterable>
                  <el-option v-for="field in getFieldsForChart(index, 'x')" :key="field" :label="field" :value="field" />
                </el-select>
              </el-col>
              <el-col :span="6">
                <el-select v-model="chart.y_field" placeholder="Y轴字段" clearable filterable>
                  <el-option v-for="field in getFieldsForChart(index, 'y')" :key="field" :label="field" :value="field" />
                </el-select>
              </el-col>
            </el-row>
            
            <el-row :gutter="16" style="margin-top:8px">
              <el-col :span="6">
                <el-input v-model="chart.x_label" placeholder="X轴标签" />
              </el-col>
              <el-col :span="6">
                <el-input v-model="chart.y_label" placeholder="Y轴标签" />
              </el-col>
              <el-col :span="6">
                <el-input v-model="chart.unit" placeholder="单位，如: 万元" />
              </el-col>
            </el-row>
            
            <div v-if="!chart.datasource_id" style="margin-top:8px">
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-input v-model="chart.x_data" placeholder="X轴数据，逗号分隔，如: 1月,2月,3月" />
                </el-col>
                <el-col :span="12">
                  <el-input v-model="chart.y_data" placeholder="Y轴数据，逗号分隔，如: 100,120,150" />
                </el-col>
              </el-row>
            </div>
            
            <div v-if="['settlement_duration', 'waterlevel_duration', 'settlement_waterlevel_comparison'].includes(chart.type)" style="margin-top:8px; padding:12px; background:#f5f7fa; border-radius:4px">
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-input v-model="chart.station_name" placeholder="监测站名称，如: F8常德路站" />
                </el-col>
                <el-col :span="6" v-if="chart.type === 'settlement_duration'">
                  <el-select v-model="chart.subtype" placeholder="视图类型">
                    <el-option label="长期视图" value="long" />
                    <el-option label="近期视图" value="recent" />
                  </el-select>
                </el-col>
              </el-row>
              <el-row :gutter="16" style="margin-top:8px" v-if="chart.type === 'waterlevel_duration'">
                <el-col :span="24">
                  <el-input type="textarea" v-model="chart.layers_json" placeholder='含水层数据JSON，如: {"一含":{"dates":["2024-01"],"values":[1.5]}}' :rows="3" />
                </el-col>
              </el-row>
              <el-row :gutter="16" style="margin-top:8px" v-if="chart.type === 'settlement_waterlevel_comparison'">
                <el-col :span="24">
                  <el-input type="textarea" v-model="chart.comparison_json" placeholder='对比数据JSON，含settlement和waterlevel两个对象' :rows="4" />
                </el-col>
              </el-row>
            </div>
            
            <el-button type="danger" link @click="form.charts.splice(index, 1)" style="margin-top:8px">删除</el-button>
          </div>
          <el-button type="success" link @click="addChart">+ 添加图表</el-button>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { getMappings, createMapping, updateMapping, deleteMapping } from '@/api/mapping'
import { getTemplates } from '@/api/template'
import { getDataSources, testDataSource } from '@/api/datasource'

const loading = ref(false)
const mappingList = ref([])
const templateList = ref([])
const dataSourceList = ref([])
const showDialog = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref()
const loadingTemplates = ref(true)
const loadingDataSources = ref(true)

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedMappings = ref([])
const checkAll = ref(false)
const isIndeterminate = ref(false)

const emptyDescription = computed(() => {
  if (templateList.value.length === 0) return '暂无模板，请先上传模板'
  if (dataSourceList.value.length === 0) return '暂无数据源，请先配置数据源'
  return '暂无映射配置'
})

const form = reactive({
  id: null,
  name: '',
  template_id: null,
  datasource_ids: [],
  mappings: [],
  charts: []
})

const rules = {
  name: [{ required: true, message: '请输入映射名称', trigger: 'blur' }],
  template_id: [{ required: true, message: '请选择模板', trigger: 'change' }],
  datasource_ids: [{ required: true, message: '请选择数据源', trigger: 'change', type: 'array', min: 1 }]
}

const templateVariables = computed(() => {
  const t = templateList.value.find(t => t.id === form.template_id)
  return t?.variables || []
})

const selectedDataSources = computed(() => {
  return dataSourceList.value.filter(ds => form.datasource_ids.includes(ds.id))
})

const loadedDatasourceFields = ref({})
const fieldsLoading = ref(false)

const allDataSourceFields = computed(() => {
  const fields = []
  for (const dsId of form.datasource_ids) {
    const ds = dataSourceList.value.find(d => d.id === dsId)
    if (!ds) continue
    const dsFields = loadedDatasourceFields.value[dsId] || []
    for (const f of dsFields) {
      fields.push({
        key: `${dsId}_${f}`,
        datasourceId: dsId,
        datasourceName: ds.name,
        field: f
      })
    }
  }
  return fields
})

const datasourceTagTypes = ['', 'success', 'warning', 'danger', 'info']

const getDatasourceTagType = (dsId) => {
  const idx = form.datasource_ids.indexOf(dsId)
  return datasourceTagTypes[idx % datasourceTagTypes.length] || ''
}

const getDatasourceFieldsSync = (ds) => {
  if (!ds) return []
  if (ds.config?._fields && ds.config._fields.length > 0) {
    return ds.config._fields
  }
  if (ds.type === 'form') {
    return Object.keys(ds.config?.fields || {})
  } else if (ds.type === 'json') {
    try {
      const data = JSON.parse(ds.config?.json_text || '{}')
      if (Array.isArray(data)) {
        return data.length > 0 ? Object.keys(data[0]) : []
      }
      return Object.keys(data)
    } catch {
      return []
    }
  } else if (ds.type === 'sql') {
    const sql = ds.config?.test_sql || ds.config?.sql || ''
    const params = ds.config?.params || []
    if (!sql) return []
    const paramNames = params.map(p => p.name).filter(Boolean)
    const mockFields = sql.match(/SELECT\s+(.+?)\s+FROM/i)?.[1]
      ?.split(',')
      .map(s => s.trim().split(' ').pop())
      .filter(Boolean) || []
    if (mockFields.length > 0) return mockFields
    return paramNames.length > 0 ? paramNames : ['result']
  }
  return []
}

const isDatabaseType = (type) => {
  return ['postgresql', 'kingbase', 'mysql', 'oracle'].includes(type)
}

const loadDatasourceFields = async () => {
  fieldsLoading.value = true
  try {
    const newFields = {}
    for (const dsId of form.datasource_ids) {
      const ds = dataSourceList.value.find(d => d.id === dsId)
      if (!ds) continue
      if (ds.type === 'http_api' || isDatabaseType(ds.type)) {
        try {
          const res = await testDataSource({
            type: ds.type,
            config: ds.config,
            ds_id: dsId
          })
          if (res.success) {
            const data = res.data
            if (Array.isArray(data) && data.length > 0) {
              newFields[dsId] = Object.keys(data[0])
            } else if (data?.columns && Array.isArray(data.columns)) {
              newFields[dsId] = data.columns
            } else if (typeof data === 'object' && data !== null) {
              newFields[dsId] = Object.keys(data)
            } else {
              newFields[dsId] = []
            }
          } else {
            newFields[dsId] = []
          }
        } catch (e) {
          console.error('Failed to fetch fields:', e)
          newFields[dsId] = []
        }
      } else {
        newFields[dsId] = getDatasourceFieldsSync(ds)
      }
    }
    loadedDatasourceFields.value = newFields
  } finally {
    fieldsLoading.value = false
  }
}

const getFieldsForDatasource = (dsId) => {
  if (!dsId) return []
  const ds = dataSourceList.value.find(d => d.id === dsId)
  if (!ds) return []
  return loadedDatasourceFields.value[dsId] || getDatasourceFieldsSync(ds)
}

const getTemplateName = (id) => {
  const t = templateList.value.find(t => t.id === id)
  return t?.name || '-'
}

const getDataSourceNames = (ids) => {
  if (!ids || !Array.isArray(ids)) return '-'
  const names = ids.map(id => {
    const ds = dataSourceList.value.find(d => d.id === id)
    return ds?.name || `数据源${id}`
  })
  return names.join('、')
}

const handleTemplateChange = () => {
  form.mappings = []
}

const handleDataSourceChange = () => {
  form.mappings = form.mappings.filter(m => form.datasource_ids.includes(m.datasource_id))
  loadDatasourceFields()
}

const handleAutoMatch = () => {
  if (form.datasource_ids.length === 0) return

  const newMappings = []
  templateVariables.value.forEach(v => {
    for (const dsId of form.datasource_ids) {
      const fields = getFieldsForDatasource(dsId)
      const matched = fields.find(f => f.toLowerCase() === v.toLowerCase())
      if (matched) {
        newMappings.push({
          target: v,
          source: matched,
          datasource_id: dsId
        })
        break
      }
    }
  })
  form.mappings = newMappings
}

const addMapping = () => {
  const firstDsId = form.datasource_ids.length > 0 ? form.datasource_ids[0] : null
  form.mappings.push({
    target: '',
    source: '',
    datasource_id: firstDsId
  })
}

const addChart = () => {
  form.charts.push({
    id: '',
    type: 'bar',
    title: '',
    x_label: '',
    y_label: '',
    unit: '',
    x_data: '',
    y_data: '',
    datasource_id: null,
    x_field: '',
    y_field: ''
  })
}

const onChartDatasourceChange = (index) => {
  form.charts[index].x_field = ''
  form.charts[index].y_field = ''
}

const getFieldsForChart = (index, axis) => {
  const chart = form.charts[index]
  if (!chart.datasource_id) return []
  const ds = dataSourceList.value.find(d => d.id === chart.datasource_id)
  if (!ds) return []
  return loadedDatasourceFields.value[chart.datasource_id] || getDatasourceFieldsSync(ds)
}

const addMappingWithVariable = (varName) => {
  // Check if this variable is already mapped
  const exists = form.mappings.some(m => m.target === varName)
  if (exists) {
    ElMessage.warning('该变量已添加映射')
    return
  }
  const firstDsId = form.datasource_ids.length > 0 ? form.datasource_ids[0] : null
  form.mappings.push({
    target: varName,
    source: '',
    datasource_id: firstDsId
  })
}

const removeMapping = (index) => {
  form.mappings.splice(index, 1)
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.template_id = null
  form.datasource_ids = []
  form.mappings = []
  form.charts = []
}

const handleAdd = () => {
  showDialog.value = true
  isEdit.value = false
  resetForm()
}

const loadMappings = async () => {
  loading.value = true
  try {
    const res = await getMappings({
      page: currentPage.value,
      page_size: pageSize.value
    })
    if (res.items) {
      mappingList.value = res.items
      total.value = res.total || 0
    } else if (res.data) {
      mappingList.value = res.data
      total.value = res.total || 0
    } else {
      mappingList.value = res || []
      total.value = res?.length || 0
    }
  } catch (error) {
    ElMessage.error('加载映射失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  loadMappings()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadMappings()
}

const handleSelectionChange = (selection) => {
  selectedMappings.value = selection
  checkAll.value = selection.length === mappingList.value.length
  isIndeterminate.value = selection.length > 0 && selection.length < mappingList.value.length
}

const handleCheckAllChange = (val) => {
  selectedMappings.value = val ? [...mappingList.value] : []
  isIndeterminate.value = false
}

const handleBatchDelete = async () => {
  if (selectedMappings.value.length === 0) return

  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedMappings.value.length} 个映射吗？`, '批量删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    for (const mapping of selectedMappings.value) {
      await deleteMapping(mapping.id)
    }

    ElMessage.success('批量删除成功')
    selectedMappings.value = []
    checkAll.value = false
    loadMappings()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const loadTemplates = async () => {
  loadingTemplates.value = true
  try {
    const res = await getTemplates({ page: 1, page_size: 100 })
    const list = res?.items || res?.data || res || []
    templateList.value = Array.isArray(list) ? list : []
  } catch (error) {
    ElMessage.error('加载模板失败')
  } finally {
    loadingTemplates.value = false
  }
}

const loadDataSources = async () => {
  loadingDataSources.value = true
  try {
    const res = await getDataSources({ page: 1, page_size: 100 })
    const list = res?.items || res?.data || res || []
    dataSourceList.value = Array.isArray(list) ? list : []
  } catch (error) {
    ElMessage.error('加载数据源失败')
  } finally {
    loadingDataSources.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const data = {
          name: form.name,
          template_id: form.template_id,
          datasource_ids: form.datasource_ids,
          mappings: form.mappings
            .filter(m => m.target && m.source && m.datasource_id)
            .map(m => ({
              target: m.target,
              source: m.source,
              datasource_id: m.datasource_id
            })),
          charts: form.charts
            .filter(c => c.id && c.title)
            .map(c => {
              const chart = {
                id: c.id,
                type: c.type,
                title: c.title,
                x_label: c.x_label,
                y_label: c.y_label,
                unit: c.unit,
                datasource_id: c.datasource_id || null,
                x_field: c.x_field || '',
                y_field: c.y_field || '',
                x_data: c.datasource_id ? undefined : c.x_data.split(',').map(s => s.trim()).filter(Boolean),
                y_data: c.datasource_id ? undefined : c.y_data.split(',').map(s => s.trim()).filter(Boolean)
              }
              
              if (c.type === 'settlement_duration') {
                chart.station_name = c.station_name || ''
                chart.subtype = c.subtype || 'long'
              } else if (c.type === 'waterlevel_duration') {
                chart.station_name = c.station_name || ''
                if (c.layers_json) {
                  try {
                    chart.layers = JSON.parse(c.layers_json)
                  } catch {}
                }
              } else if (c.type === 'settlement_waterlevel_comparison') {
                chart.station_name = c.station_name || ''
                if (c.comparison_json) {
                  try {
                    const parsed = JSON.parse(c.comparison_json)
                    chart.settlement = parsed.settlement
                    chart.waterlevel = parsed.waterlevel
                  } catch {}
                }
              }
              
              return chart
            })
        }

        if (isEdit.value) {
          await updateMapping(form.id, data)
          ElMessage.success('更新成功')
        } else {
          await createMapping(data)
          ElMessage.success('创建成功')
        }

        showDialog.value = false
        loadMappings()
      } catch (error) {
        console.error('保存失败:', error)
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
  form.template_id = row.template_id
  form.datasource_ids = row.datasource_ids || [row.datasource_id].filter(Boolean)
  form.mappings = [...(row.mappings || [])].map(m => ({
    target: m.target || m.template_var || '',
    source: m.source || m.datasource_field || '',
    datasource_id: m.datasource_id || row.datasource_id || form.datasource_ids[0]
  }))
  
  // Load charts - convert arrays to comma-separated strings
  form.charts = (row.charts || []).map(c => {
    const chart = {
      id: c.id || '',
      type: c.type || 'bar',
      title: c.title || '',
      x_label: c.x_label || '',
      y_label: c.y_label || '',
      unit: c.unit || '',
      x_data: Array.isArray(c.x_data) ? c.x_data.join(',') : (c.x_data || ''),
      y_data: Array.isArray(c.y_data) ? c.y_data.join(',') : (c.y_data || ''),
      datasource_id: c.datasource_id || null,
      x_field: c.x_field || '',
      y_field: c.y_field || ''
    }
    
    if (c.type === 'settlement_duration') {
      chart.station_name = c.station_name || ''
      chart.subtype = c.subtype || 'long'
    } else if (c.type === 'waterlevel_duration') {
      chart.station_name = c.station_name || ''
      chart.layers_json = c.layers ? JSON.stringify(c.layers) : ''
    } else if (c.type === 'settlement_waterlevel_comparison') {
      chart.station_name = c.station_name || ''
      if (c.settlement || c.waterlevel) {
        chart.comparison_json = JSON.stringify({
          settlement: c.settlement,
          waterlevel: c.waterlevel
        })
      }
    }
    
    return chart
  })

  showDialog.value = true
  loadDatasourceFields()
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该映射配置吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteMapping(row.id)
      ElMessage.success('删除成功')
      loadMappings()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  loadMappings()
  loadTemplates()
  loadDataSources()
})
</script>

<style scoped>
.mapping-page {
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

.mapping-config {
  display: flex;
  gap: 20px;
  margin: 20px 0;
}

.mapping-panel {
  flex: 1;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
}

.panel-header {
  padding: 10px 15px;
  background: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.panel-content {
  padding: 15px;
  min-height: 200px;
  max-height: 300px;
  overflow-y: auto;
}

.empty-tip {
  color: #999;
  text-align: center;
  padding: 20px;
}

.var-item {
  padding: 8px 12px;
  margin: 4px 0;
  background: #f0f2f5;
  border-radius: 4px;
  font-size: 13px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
}

.var-item:hover {
  background: #e6f4ff;
  color: #1677ff;
}

.mapping-arrows {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
}

.mapping-list {
  margin-top: 15px;
}

.mapping-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.mapping-row .arrow {
  color: #999;
  font-weight: bold;
}

.chart-row {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 12px;
}

.chart-list {
  margin-top: 12px;
}
</style>