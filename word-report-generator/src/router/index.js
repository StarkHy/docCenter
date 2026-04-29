import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Layout from '@/views/Layout.vue'
import Home from '@/views/Home.vue'
import Template from '@/views/Template.vue'
import DataSource from '@/views/DataSource.vue'
import Database from '@/views/Database.vue'
import Mapping from '@/views/Mapping.vue'
import Generate from '@/views/Generate.vue'
import History from '@/views/History.vue'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/',
    component: Layout,
    redirect: '/home',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: Home,
        meta: { title: '首页' }
      },
      {
        path: 'template',
        name: 'Template',
        component: Template,
        meta: { title: '模板管理' }
      },
      {
        path: 'datasource',
        name: 'DataSource',
        component: DataSource,
        meta: { title: '数据源管理' }
      },
      {
        path: 'database',
        name: 'Database',
        component: Database,
        meta: { title: '数据库配置' }
      },
      {
        path: 'mapping',
        name: 'Mapping',
        component: Mapping,
        meta: { title: '参数映射' }
      },
      {
        path: 'generate',
        name: 'Generate',
        component: Generate,
        meta: { title: '文档生成' }
      },
      {
        path: 'history',
        name: 'History',
        component: History,
        meta: { title: '历史记录' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.path === '/login') {
    next()
  } else {
    if (authStore.isAuthenticated) {
      next()
    } else {
      next('/login')
    }
  }
})

export default router