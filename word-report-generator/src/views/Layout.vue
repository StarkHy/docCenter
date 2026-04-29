<template>
  <el-container class="layout-container">
    <el-aside class="sidebar" width="240px">
      <div class="logo">
        <span>报表生成器</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <!-- Icons added for a more polished navigation -->
        <el-menu-item index="/home">
          <el-icon><HomeFilled /></el-icon>
          <span class="menu-text">首页</span>
        </el-menu-item>
        <el-menu-item index="/template">
          <el-icon><Document /></el-icon>
          <span class="menu-text">模板管理</span>
        </el-menu-item>
        <el-menu-item index="/datasource">
          <el-icon><Connection /></el-icon>
          <span class="menu-text">数据源管理</span>
        </el-menu-item>
        <el-menu-item index="/database">
          <el-icon><DataBoard /></el-icon>
          <span class="menu-text">数据库配置</span>
        </el-menu-item>
        <el-menu-item index="/mapping">
          <el-icon><Setting /></el-icon>
          <span class="menu-text">参数映射</span>
        </el-menu-item>
        <el-menu-item index="/generate">
          <el-icon><Document /></el-icon>
          <span class="menu-text">文档生成</span>
        </el-menu-item>
        <el-menu-item index="/history">
          <el-icon><Clock /></el-icon>
          <span class="menu-text">历史记录</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/home' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-for="(item, index) in breadcrumbList" :key="index" :to="item.path">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <!-- Help icon -->
          <el-tooltip content="使用帮助" placement="bottom">
            <div class="header-icon-wrapper" @click="showHelpDialog = true">
              <el-icon color="#409eff"><QuestionFilled /></el-icon>
            </div>
          </el-tooltip>
          <!-- Notification icon -->
          <el-badge :value="notifications" class="header-icon" placement="top-end">
            <el-icon color="#409eff"><Bell /></el-icon>
          </el-badge>
          <!-- User avatar + dropdown -->
          <el-avatar size="32" :src="authStore.userInfo.avatar" v-if="authStore.userInfo.avatar"></el-avatar>
          <el-dropdown @command="handleCommand" class="user-dropdown">
            <span class="user-info">{{ authStore.userInfo.nickname || authStore.userInfo.username }}</span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
    
    <!-- Help Dialog -->
    <el-dialog v-model="showHelpDialog" title="使用帮助" width="750px" destroy-on-close>
      <div class="help-content">
        <h3>一、功能概述</h3>
        <p>Word报告生成系统是一个基于模板的自动化文档生成平台。用户上传Word模板（.docx），配置数据源和字段映射关系，系统即可自动生成包含动态内容、数据表格和图表的专业Word报告。</p>
        
        <h3>二、使用流程</h3>
        <ol>
          <li><strong>上传模板</strong>：在"模板管理"页面上传Word模板，模板中使用 <code>{{变量名}}</code> 格式定义占位符</li>
          <li><strong>配置数据源</strong>：在"数据源管理"页面配置数据源，支持HTTP API、静态JSON、数据库三种类型</li>
          <li><strong>创建映射</strong>：在"参数映射"页面配置模板变量与数据源字段的映射关系</li>
          <li><strong>生成文档</strong>：在"文档生成"页面选择映射配置，填写参数，生成Word文档</li>
        </ol>
        
        <h3>三、图表配置（重点）</h3>
        
        <h4>1. 支持的图表类型</h4>
        <ul>
          <li><code>bar</code> - <strong>柱状图</strong>：适用于不同类别数据的对比，如各区域销售额对比</li>
          <li><code>line</code> - <strong>折线图</strong>：适用于展示数据趋势，如月度收入变化</li>
          <li><code>pie</code> - <strong>饼图</strong>：适用于展示比例构成，如成本占比</li>
          <li><code>combo</code> - <strong>组合图</strong>：同时显示柱状和折线，如销售额和增长率对比</li>
        </ul>
        
        <h4>2. 图表配置参数说明</h4>
        <table class="help-table">
          <thead>
            <tr><th>参数</th><th>说明</th><th>示例</th></tr>
          </thead>
          <tbody>
            <tr><td>id</td><td>图表唯一标识</td><td>revenue_trend</td></tr>
            <tr><td>type</td><td>图表类型</td><td>bar/line/pie/combo</td></tr>
            <tr><td>title</td><td>图表标题（显示在图上方）</td><td>2024年收入趋势</td></tr>
            <tr><td>x_label</td><td>X轴标签</td><td>月份</td></tr>
            <tr><td>y_label</td><td>Y轴标签</td><td>金额（万元）</td></tr>
            <tr><td>x_data</td><td>X轴数据（数组）</td><td>["1月","2月","3月"]</td></tr>
            <tr><td>y_data</td><td>Y轴数据（数组，必须是数字）</td><td>[100, 120, 150]</td></tr>
          </tbody>
        </table>
        
        <h4>3. 配置示例</h4>
        <p><strong>示例1：柱状图（各区域销售对比）</strong></p>
        <pre>{
  "id": "sales_compare",
  "type": "bar",
  "title": "各区域销售对比",
  "x_label": "区域",
  "y_label": "销售额（万元）",
  "x_data": ["华东区", "华南区", "华北区", "西南区"],
  "y_data": [420, 310, 280, 150]
}</pre>
        
        <p><strong>示例2：折线图（收入趋势）</strong></p>
        <pre>{
  "id": "revenue_trend",
  "type": "line",
  "title": "2024年月度收入趋势",
  "x_label": "月份",
  "y_label": "收入（万元）",
  "x_data": ["1月", "2月", "3月", "4月", "5月", "6月"],
  "y_data": [85, 92, 98, 105, 112, 118]
}</pre>
        
        <p><strong>示例3：饼图（成本构成）</strong></p>
        <pre>{
  "id": "cost_structure",
  "type": "pie",
  "title": "成本构成分析",
  "x_label": "",
  "y_label": "",
  "x_data": ["人力成本", "原材料", "运营费用", "市场营销", "其他"],
  "y_data": [308, 246, 158, 106, 62]
}</pre>
        
        <p><strong>示例4：组合图（利润分析）</strong></p>
        <pre>{
  "id": "profit_analysis",
  "type": "combo",
  "title": "季度利润分析（柱状=利润，线条=利润率）",
  "x_label": "季度",
  "y_label": "利润（万元）",
  "x_data": ["Q1", "Q2", "Q3", "Q4"],
  "y_data": [85, 95, 88, 102]
}</pre>
        
        <h4>4. 在Word模板中使用图表</h4>
        <ol>
          <li>在Word文档中需要插入图表的位置，输入占位符：<code>CHART_PLACEHOLDER_{图表id}</code></li>
          <li>例如图表id为 "sales_compare"，则占位符为：<code>CHART_PLACEHOLDER_sales_compare</code></li>
          <li>占位符可以放在任意位置（段落、表格），系统会自动替换为图表图片</li>
        </ol>
        
        <h4>5. 添加图表到映射</h4>
        <p>在"参数映射"页面：</p>
        <ol>
          <li>点击"编辑"按钮编辑已有映射，或点击"新增映射"创建新映射</li>
          <li>填写基本信息（名称、模板、数据源）</li>
          <li>滑动到页面底部找到"图表配置"区域</li>
          <li>点击"+ 添加图表"按钮</li>
          <li>填写图表配置：
            <ul>
              <li>图表ID：唯一标识，如 <code>revenue_trend</code></li>
              <li>图表类型：选择柱状图/折线图/饼图/组合图</li>
              <li>图表标题：显示在图上方的标题</li>
              <li>X轴标签、Y轴标签：坐标轴名称</li>
              <li>X轴数据：填写逗号分隔的类别，如 <code>1月,2月,3月,4月</code></li>
              <li>Y轴数据：填写逗号分隔的数字，如 <code>85,92,98,105</code></li>
            </ul>
          </li>
          <li>点击"保存"</li>
        </ol>
        
        <h3>四、数据源参数（HTTP API）</h3>
        <p>对于HTTP API类型的数据源，可以配置动态参数：</p>
        
        <h4>1. 配置参数</h4>
        <ol>
          <li>在数据源列表中，点击对应数据源的"入参"按钮</li>
          <li>点击"添加参数"，填写参数名称和默认值</li>
          <li>参数名如：<code>deviceSn</code>，默认值：<code>286366089222017C</code></li>
        </ol>
        
        <h4>2. 使用参数</h4>
        <p>在以下位置使用 <code>:参数名</code> 格式引用：</p>
        <ul>
          <li><strong>URL参数</strong>：<code>https://api.example.com/data/:deviceSn</code></li>
          <li><strong>Params配置</strong>：<code>{"deviceSn": ":deviceSn"}</code></li>
          <li><strong>Headers</strong>：<code>{"X-Device": ":deviceSn"}</code></li>
        </ul>
        
        <h3>五、常见问题</h3>
        <dl>
          <dt>Q: 为什么生成的文档中变量没有替换？</dt>
          <dd>A: 检查映射配置是否包含该变量，以及数据源是否返回对应字段。可以在"文档生成"页面点击"预览数据"查看数据是否正确。</dd>
          
          <dt>Q: 为什么图表没有显示？</dt>
          <dd>A: 检查两点：1）模板中占位符是否正确（格式：CHART_PLACEHOLDER_图表id）；2）映射中是否添加了该图表配置。</dd>
          
          <dt>Q: HTTP API测试失败怎么办？</dt>
          <dd>A: 检查：1）URL是否正确；2）参数是否配置完整；3）Headers是否正确设置；4）可以先用Postman等工具测试API是否可用。</dd>
          
          <dt>Q: 饼图的百分比不对？</dt>
          <dd>A: y_data中的数字会被自动计算为百分比，确保所有数字加起来是100即可。</dd>
          
          <dt>Q: 图表中文显示为方块？</dt>
          <dd>A: 系统已配置中文字体（苹方、黑体），如仍有问题请检查系统是否安装了中文字体。</dd>
        </dl>
      </div>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { HomeFilled, Document, Connection, DataBoard, Setting, Clock, Bell, QuestionFilled } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// Simple in-app notification count (could be wired to real data later)
const notifications = ref(3)
const showHelpDialog = ref(false)

const pageTitle = computed(() => {
  return route.meta?.title || '首页'
})

const activeMenu = computed(() => route.path)

const breadcrumbList = computed(() => {
  const crumbs = []
  const path = route.path
  
  if (path !== '/home') {
    const menuItems = [
      { path: '/template', title: '模板管理' },
      { path: '/datasource', title: '数据源管理' },
      { path: '/database', title: '数据库配置' },
      { path: '/mapping', title: '参数映射' },
      { path: '/generate', title: '文档生成' },
      { path: '/history', title: '历史记录' }
    ]
    
    const matched = menuItems.find(m => path.startsWith(m.path) && m.path !== '/home')
    if (matched) {
      crumbs.push(matched)
    } else if (route.meta?.title) {
      crumbs.push({ path: path, title: route.meta.title })
    }
  }
  
  return crumbs
})

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-container {
  width: 100%;
  height: 100vh;
}

.sidebar {
  background-color: #2b3a4f;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: white;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.el-menu-item) {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  min-height: 44px;
}

:deep(.el-menu-item .el-icon) {
  font-size: 16px;
  width: 18px;
  height: 18px;
}

.menu-text {
  font-size: 14px;
}

.header {
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
}

.el-breadcrumb {
  font-size: 14px;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background 0.2s;
}

.user-info:hover {
  background: #f5f7fa;
}

.main-content {
  background: #f0f2f5;
  padding: 20px;
  min-height: calc(100vh - 60px);
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* New slide transition for section changes */
.slide-enter-active, .slide-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
}
.slide-enter-from {
  transform: translateX(8px);
  opacity: 0;
}
.slide-leave-to {
  transform: translateX(-8px);
  opacity: 0;
}

.header-icon {
  font-size: 20px;
  cursor: pointer;
  margin-right: 15px;
  transition: color 0.3s;
}

.header-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  margin-right: 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.3s;
}

.header-icon-wrapper:hover {
  background: rgba(255, 255, 255, 0.2);
}

.help-content {
  max-height: 500px;
  overflow-y: auto;
}

.help-content h3 {
  margin: 16px 0 8px;
  color: #303133;
  font-size: 16px;
}

.help-content p {
  margin: 8px 0;
  color: #606266;
  line-height: 1.6;
}

.help-content ol, .help-content ul {
  margin: 8px 0;
  padding-left: 20px;
  color: #606266;
}

.help-content li {
  margin: 4px 0;
  line-height: 1.6;
}

.help-content pre {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  margin: 8px 0;
}

.help-content code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
  color: #e6a23c;
}

.help-content dt {
  font-weight: 600;
  color: #303133;
  margin-top: 12px;
}

.help-content dd {
  margin: 4px 0 8px 16px;
  color: #606266;
}

.help-content h4 {
  margin: 16px 0 8px;
  color: #409eff;
  font-size: 14px;
}

.help-content .help-table {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0;
  font-size: 13px;
}

.help-content .help-table th,
.help-content .help-table td {
  border: 1px solid #ebeef5;
  padding: 8px 12px;
  text-align: left;
}

.help-content .help-table th {
  background: #f5f7fa;
  color: #303133;
  font-weight: 600;
}

.help-content .help-table td {
  color: #606266;
}
</style>
