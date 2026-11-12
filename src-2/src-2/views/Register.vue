<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../api/index.js'

const router = useRouter()
const phoneNumber = ref('')
const password = ref('')
const agreeTerms = ref(false)
const loading = ref(false)

const handleRegister = async () => {
  try {
    loading.value = true
    
    if (!phoneNumber.value || !password.value) {
      alert('请填写完整信息')
      return
    }

    if (!agreeTerms.value) {
      alert('请同意用户协议和隐私政策')
      return
    }

    // 调用注册接口
    const response = await authAPI.register({
      phone_number: phoneNumber.value,
      password: password.value
    })
    
    if (response.success) {
      alert(response.message || '注册成功')
      router.push('/login')
    } else {
      alert(response.message || '注册失败，请重试')
    }
  } catch (error) {
    console.error('注册异常:', error)
    alert(error.message || '注册失败，请重试')
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="register-container">
    <div class="left-section">
      <h1 class="title">智慧党建</h1>
      <p class="subtitle">以AI赋能时代篇章</p>
    </div>
    <div class="right-section">
      <div class="register-form">
        <h2 class="form-title">欢迎注册</h2>
        <div class="form-group">
          <label for="phoneNumber">手机号</label>
          <input
            type="tel"
            id="phoneNumber"
            v-model="phoneNumber"
            placeholder="请输入手机号"
            class="form-input"
          >
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            v-model="password"
            placeholder="请输入密码"
            class="form-input"
          >
        </div>
        <div class="form-group agree-terms">
          <input type="checkbox" id="agreeTerms" v-model="agreeTerms">
          <label for="agreeTerms">我已阅读并同意 <a href="#" class="link">用户协议</a> 和 <a href="#" class="link">隐私政策</a></label>
        </div>
        <button class="register-button" @click="handleRegister" :disabled="loading">
          <i v-if="!loading" class="el-icon-user-plus el-icon--left"></i>
          {{ loading ? '注册中...' : '注册' }}
        </button>
        <div class="form-links">
          <a href="#" class="link" @click.prevent="goToLogin">已有账号？重新登录</a>
        </div>
      </div>
    </div>
  </div>
  </template>

<style scoped>
.register-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-image: url('../background2.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
}

/* 半透明遮罩层 */
.register-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 1;
}

.left-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  position: relative;
  z-index: 2;
}

.title {
    font-size: 56px;
    font-weight: bold;
    margin-bottom: 15px;
    text-shadow: 0 3px 8px rgba(0, 0, 0, 0.6);
    color: #fff;
    font-family: '楷体', 'KaiTi', serif;
  }

.subtitle {
  font-size: 18px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.right-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  z-index: 2;
}

.register-form {
  width: 380px;
  padding: 45px;
  border-radius: 12px;
  background-color: rgba(255, 255, 255, 0.98);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(20px);
}

.form-title {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 35px;
  text-align: center;
  letter-spacing: -0.5px;
}

.form-group {
  margin-bottom: 22px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-input {
  width: 100%;
  padding: 13px 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s;
  background-color: rgba(255, 255, 255, 0.8);
}

.form-input:focus {
  outline: none;
  border-color: #C8102E;
  box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.1);
}

.agree-terms {
  display: flex;
  align-items: flex-start;
}

.agree-terms input {
  margin-right: 10px;
  margin-top: 4px;
}

.register-button {
  width: 100%;
  padding: 12px;
  background-color: #C8102E;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.3);
}

.register-button:hover {
  background-color: #A50D23;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(200, 16, 46, 0.4);
}

.form-links {
  margin-top: 20px;
  text-align: center;
}

.link {
  color: #C8102E;
  text-decoration: none;
  transition: color 0.3s;
}

.link:hover {
  color: #A50D23;
  text-decoration: underline;
}
</style>