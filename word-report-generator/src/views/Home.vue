<template>
  <div class="home-page">
    <!-- Welcome header with current date/time -->
    <div class="welcome-bar" v-if="userName">
      <div class="welcome-text">欢迎回来，<strong>{{ userName }}</strong>！</div>
      <div class="welcome-datetime">{{ currentDateTime }}</div>
    </div>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover" @click="$router.push('/template')" style="cursor: pointer">
          <div class="stat-icon gradient-blue">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.templateCount }}</div>
            <div class="stat-label">模板数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover" @click="$router.push('/datasource')" style="cursor: pointer">
          <div class="stat-icon gradient-teal">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.datasourceCount }}</div>
            <div class="stat-label">数据源</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card stat-card-action" shadow="hover" @click="$router.push('/generate')" style="cursor: pointer">
          <div class="stat-icon gradient-amber">
            <el-icon><Edit /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">生成文档</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover" @click="$router.push('/history')" style="cursor: pointer">
          <div class="stat-icon gradient-rose">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.todayGenerated }}</div>
            <div class="stat-label">今日生成</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近生成</span>
              <el-button type="primary" link @click="$router.push('/history')">查看更多</el-button>
            </div>
          </template>
          <div v-if="loading" v-loading="loading" style="min-height:200px"></div>
          <el-empty v-else-if="recentList.length === 0" description="暂无生成记录" />
          <el-table v-else :data="recentList">
            <el-table-column prop="name" label="文档名称" width="180" show-overflow-tooltip />
            <el-table-column prop="template" label="模板" width="100" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === '成功' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="时间" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/generate')">
              <el-icon><Edit /></el-icon>
              新建文档
            </el-button>
            <el-button @click="$router.push('/template')">
              <el-icon><Folder /></el-icon>
              管理模板
            </el-button>
            <el-button @click="$router.push('/datasource')">
              <el-icon><Connection /></el-icon>
              管理数据源
            </el-button>
            <el-button @click="$router.push('/mapping')">
              <el-icon><Setting /></el-icon>
              参数映射
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getTemplates } from '@/api/template'
import { getDataSources } from '@/api/datasource'
import { getHistory } from '@/api/document'
import { useAuthStore } from '@/stores/auth'
import { Document, Connection, Edit, Clock, Folder, Setting } from '@element-plus/icons-vue'

const loading = ref(true)
const recentList = ref([])
const now = ref(new Date())
const authStore = useAuthStore()
const userName = computed(() => authStore.userInfo?.nickname || authStore.userInfo?.username || '用户')
const currentDateTime = computed(() => now.value.toLocaleString())

const stats = ref({
  templateCount: 0,
  datasourceCount: 0,
  totalGenerated: 0,
  todayGenerated: 0
})

const loadStats = async () => {
  loading.value = true
  try {
    const today = new Date().toISOString().split('T')[0]
    
    const [templates, datasources, history] = await Promise.all([
      getTemplates({ page: 1, page_size: 1 }),
      getDataSources({ page: 1, page_size: 1 }),
      getHistory({ page: 1, page_size: 100 })
    ])
    
    const templateData = templates?.data || templates?.items || templates || []
    const datasourceData = datasources?.data || datasources?.items || datasources || []
    const historyData = history?.data || history?.items || history || []
    
    stats.value.templateCount = templates?.total || (Array.isArray(templateData) ? templateData.length : 0)
    stats.value.datasourceCount = datasources?.total || (Array.isArray(datasourceData) ? datasourceData.length : 0)
    stats.value.totalGenerated = history?.total || 0
    
    const todayCount = (historyData || []).filter(item => 
      item.create_time && item.create_time.startsWith(today)
    ).length
    stats.value.todayGenerated = todayCount
    
    recentList.value = (historyData || []).slice(0, 5)
  } catch (e) {
    console.error('加载统计数据失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
  // Update time every second for the welcome header
  setInterval(() => { now.value = new Date() }, 1000)
})
</script>

<style scoped>
.welcome-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0 6px 0;
  border-bottom: 1px solid #eef2f7;
  margin-bottom: 8px;
}
.welcome-text {
  font-size: 16px;
  color: #333;
}
.welcome-datetime {
  font-size: 12px;
  color: #888;
}
.home-page {
  padding: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-card-action {
  justify-content: flex-start;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 16px;
}

.stat-icon .el-icon {
  font-size: 24px;
}

/* Gradient accents for a polished, cohesive look */
.gradient-blue {
  background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
}
.gradient-teal {
  background: linear-gradient(135deg, #14b8a6 0%, #0f6f64 100%);
}
.gradient-amber {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}
.gradient-rose {
  background: linear-gradient(135deg, #f472b6 0%, #e11d48 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-actions .el-button {
  justify-content: flex-start;
  padding-left: 20px;
}
</style>
