<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>Word报表生成器</h1>
        <p>Word Report Generator</p>
      </div>
      <el-form ref="loginFormRef" :model="loginForm" :rules="rules" class="login-form">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" size="large" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width:100%" @click="handleLogin" :loading="loading">登 录</el-button>
        </el-form-item>
      </el-form>
      <div class="login-tip">
        <span>提示: 账号 admin, 密码 admin123</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { login } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await login(loginForm)
        authStore.login({
          token: res.token,
          user: res.user
        })
        ElMessage.success('登录成功')
        router.push('/home')
      } catch (error) {
        console.error('登录失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  /* Subtle, professional background */
  background: linear-gradient(135deg, #0f5b8f 0%, #0b2a3d 60%), radial-gradient(circle at 70% 20%, rgba(20,120,180,.25), transparent 40px);
}

.login-box {
  width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(6px);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
  font-weight: 600;
}

.login-header p {
  font-size: 14px;
  color: #999;
}

.login-form {
  margin-bottom: 20px;
}

.login-tip {
  text-align: center;
  font-size: 13px;
  color: #999;
}
</style>
