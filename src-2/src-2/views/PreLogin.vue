<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const handleLogin = () => {
  router.push('/login')
}

const handleRegister = () => {
  router.push('/register')
}
</script>

<template>
  <div class="prelogin-container">
    <!-- 背景图片 -->
    <div class="background-image"></div>
    
    <!-- 内容区域 -->
    <div class="content-wrapper">
      <!-- 中心文本 -->
      <h1 class="main-title">
        智慧党建<br>
        <span class="sub-line">以AI赋能时代篇章</span>
      </h1>
      
      <!-- 按钮区域 -->
      <div class="buttons-container">
        <button class="login-button" @click="handleLogin">登录</button>
        <button class="register-button" @click="handleRegister">注册</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.prelogin-container {
  position: relative;
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('@/background.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 0;
}

.background-image::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(200, 16, 46, 0.6) 0%, rgba(100, 10, 30, 0.7) 100%);
  z-index: 1;
}

.content-wrapper {
  position: relative;
  z-index: 2;
  text-align: center;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
  animation: fadeInUp 1s ease-out;
}

.main-title {
  font-family: '楷体', 'KaiTi', serif;
  font-size: 90px;
  color: #fff;
  font-weight: bold;
  text-shadow: 3px 3px 8px rgba(0, 0, 0, 0.6);
  line-height: 1.2;
  -webkit-text-stroke: 1px rgba(200, 16, 46, 0.4);
  text-stroke: 1px rgba(200, 16, 46, 0.4);
  margin: 0;
}

.main-title .sub-line {
  font-size: 48px;
  font-weight: normal;
  opacity: 0.95;
  display: block;
  margin-top: 15px;
  -webkit-text-stroke: 1px rgba(200, 16, 46, 0.3);
  text-stroke: 1px rgba(200, 16, 46, 0.3);
}

.buttons-container {
  display: flex;
  gap: 20px;
}

.login-button, .register-button {
  padding: 14px 35px;
  border: none;
  border-radius: 30px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.25);
  font-family: 'Microsoft YaHei', sans-serif;
}

.login-button {
  background-color: #C8102E;
  color: #fff;
}

.login-button:hover {
  background-color: #A50D23;
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 10px 20px rgba(200, 16, 46, 0.4);
}

.register-button {
  background-color: rgba(255, 255, 255, 0.15);
  color: #fff;
  border: 2px solid rgba(255, 255, 255, 0.8);
}

.register-button:hover {
  background-color: rgba(255, 255, 255, 0.25);
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 10px 20px rgba(200, 16, 46, 0.3);
  border-color: #fff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-title {
    font-size: 60px;
  }
  
  .main-title .sub-line {
    font-size: 32px;
    margin-top: 10px;
  }
  
  .buttons-container {
    flex-direction: column;
    gap: 15px;
  }
  
  .login-button, .register-button {
    padding: 12px 30px;
    font-size: 14px;
  }
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>