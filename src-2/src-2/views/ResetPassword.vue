<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const phone = ref('')
const code = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const step = ref(1) // 1: 验证手机号, 2: 设置新密码
const countdown = ref(0)
//不懂不懂
const sendCode = () => {
  if (!phone.value.trim()) {
    alert('请输入手机号')
    return
  }

  // 模拟发送验证码
  countdown.value = 60
  alert('验证码已发送到您的手机')

  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

const verifyPhone = () => {
  if (!phone.value.trim()) {
    alert('请输入手机号')
    return
  }

  if (!code.value.trim()) {
    alert('请输入验证码')
    return
  }

  // 模拟验证成功
  step.value = 2
}

const resetPassword = () => {
  if (!newPassword.value.trim()) {
    alert('请输入新密码')
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    alert('两次输入的密码不一致')
    return
  }

  // 模拟重置密码成功
  alert('密码重置成功，请使用新密码登录')
  router.push('/login')
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="reset-password-container">
    <div class="header">
      <h1 class="logo">智慧党建</h1>
    </div>

    <div class="main-content">
      <div class="reset-password-form">
        <h2 class="form-title">找回密码</h2>

        <div v-if="step === 1">
          <div class="form-group">
            <label for="phone">已绑定的手机号</label>
            <input
              type="tel"
              id="phone"
              v-model="phone"
              placeholder="请输入手机号"
              class="form-input"
            >
          </div>
          <div class="form-group code-group">
            <div class="code-input">
              <label for="code">验证码</label>
              <input
                type="text"
                id="code"
                v-model="code"
                placeholder="验证码"
                class="form-input"
              >
            </div>
            <button
              class="send-code-button"
              @click="sendCode"
              :disabled="countdown > 0"
            >
              {{ countdown > 0 ? `${countdown}秒后重新发送` : '发送验证码' }}
            </button>
          </div>
          <button class="next-button" @click="verifyPhone">确定</button>
        </div>

        <div v-else-if="step === 2">
          <div class="form-group">
            <label for="newPassword">新密码</label>
            <input
              type="password"
              id="newPassword"
              v-model="newPassword"
              placeholder="请输入新密码"
              class="form-input"
            >
          </div>
          <div class="form-group">
            <label for="confirmPassword">确认新密码</label>
            <input
              type="password"
              id="confirmPassword"
              v-model="confirmPassword"
              placeholder="请输入确认密码"
              class="form-input"
            >
          </div>
          <button class="submit-button" @click="resetPassword">确定</button>
        </div>

        <div class="form-links">
          <a href="#" class="link" @click.prevent="goToLogin">返回登录</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reset-password-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  background-color: #f8f9fa;
}

.header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px 0;
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0;
}

.logo {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.main-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.reset-password-form {
  width: 400px;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  border: 1px solid #e0e0e0;
}

.form-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 30px;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #6c63ff;
}

.code-group {
  display: flex;
  gap: 10px;
}

.code-input {
  flex: 1;
}

.send-code-button {
  width: 120px;
  padding: 12px;
  background-color: #f0f0f0;
  color: #666;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.send-code-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.next-button, .submit-button {
  width: 100%;
  padding: 12px;
  background-color: #6c63ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.next-button:hover, .submit-button:hover {
  background-color: #574bff;
}

.form-links {
  margin-top: 20px;
  text-align: center;
}

.link {
  color: #6c63ff;
  text-decoration: none;
  font-size: 14px;
}

.link:hover {
  text-decoration: underline;
}
</style>