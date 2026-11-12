<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import IconAuthenticated from '@/components/icons/IconAuthenticated.vue'
import IconNotAuthenticated from '@/components/icons/IconNotAuthenticated.vue'

const router = useRouter()
const userInfo = ref({ 
  name: '用户', 
  avatar: 'https://picsum.photos/id/64/100/100',
  position: '党员',
  joinDate: '2023-01-15',
  department: '组织部'
})

// 企业认证状态
const isAuthenticated = ref(false)
const enterpriseName = ref('')

// 认证表单数据
const authFormData = ref({
  realName: '',
  phone: ''
})

// 认证加载状态
const isAuthenticating = ref(false)



// 修改密码表单数据
const passwordFormData = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 控制表单显示的状态变量
const activePanel = ref('') // '' | 'password' | 'auth'

// 用户信息已精简，移除了统计数据、活动记录和快捷功能

const goBack = () => {
  router.push('/home')
}

const goToKnowledgeBase = () => {
  router.push('/knowledge-base-home')
}

// 企业认证相关方法
const openAuthPanel = () => {
  activePanel.value = 'auth'
}

const closePanel = () => {
  activePanel.value = ''
}

const submitAuth = async () => {
  if (!authFormData.value.realName || !authFormData.value.phone) {
    alert('请填写完整的认证信息')
    return
  }
  
  isAuthenticating.value = true
  try {
    // 模拟后端请求
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 假设认证成功
    isAuthenticated.value = true
    enterpriseName.value = 'XX科技有限公司'
    activePanel.value = ''
    alert('企业认证成功！')
  } catch (error) {
    alert('认证失败，请稍后重试')
  } finally {
    isAuthenticating.value = false
  }
}


const changePassword = () => {
  activePanel.value = 'password'
}

const savePassword = () => {
  // 验证密码一致性
  if (passwordFormData.value.newPassword && passwordFormData.value.newPassword !== passwordFormData.value.confirmPassword) {
    console.log('两次输入的密码不一致')
    return
  }
  
  // 保存密码（实际项目中应调用API）
  console.log('密码修改成功')
  // 重置密码字段
  passwordFormData.value.oldPassword = ''
  passwordFormData.value.newPassword = ''
  passwordFormData.value.confirmPassword = ''
  activePanel.value = ''
}

const about = () => {
  // 后续实现
  console.log('关于智慧党建')
}

const showSettings = () => {
  // 打开设置面板或跳转到设置页面
  console.log('显示设置')
  // 实际项目中可以打开设置面板或跳转到设置页面
}

const logout = () => {
  // 清除登录状态
  localStorage.removeItem('isLoggedIn');
  // 跳转到登录前的首页
  router.push('/');
}

onMounted(() => {
  // 从本地登录信息中显示当前账号
  const account = localStorage.getItem('account') || localStorage.getItem('phoneNumber')
  if (account) {
    userInfo.value.name = account
  }
})
</script>

<template>
  <div class="personal-home-container">
    <!-- 党建主题装饰背景 -->
    <div class="party-decoration-bg"></div>
    
    <!-- 顶部导航栏 -->
    <header class="top-navigation">
      <div class="nav-container">
        <!-- 左侧内容：logo和文字 -->
        <div class="nav-logo">
          <img src="@/logo.jpg" alt="logo" class="logo-image">
          <span class="logo-text">智慧党建平台</span>
        </div>
        
        <!-- 右侧按钮组 -->
        <div class="nav-left-buttons">
          <button class="nav-button" @click="goToKnowledgeBase">
            <span class="kb-icon">📚</span>
            <span>知识库+</span>
          </button>
          <button class="nav-button" @click="goBack">
            <span class="back-icon">⬅️</span>
            <span>返回首页</span>
          </button>
        </div>
      </div>
    </header>

    <div v-show="!activePanel" class="right-background">
      <div class="background-image-1"></div>
      <div class="bg-img-2"></div>
    </div>
    <main class="content-wrapper">
      <!-- 左侧信息展示区 -->
      <div class="left-section">
        <!-- 用户信息卡片 -->
        <section class="profile-card">
          <div class="profile-header">
            <img :src="userInfo.avatar" alt="用户头像" class="avatar">
            <div class="profile-info">
              <div class="profile-main-info">
                <h1 class="user-name">{{ userInfo.name }}</h1>
                <span class="user-position">{{ userInfo.position }}</span>
              </div>
              <!-- 企业认证状态显示 -->
              <div v-if="isAuthenticated" class="auth-status">
                <IconAuthenticated class="auth-icon" />
                <span class="auth-text">已认证</span>
                <span class="enterprise-name">{{ enterpriseName }}</span>
              </div>
              <div v-else class="auth-status not-authenticated" @click="openAuthPanel">
                <IconNotAuthenticated class="auth-icon" />
                <span class="auth-text">未认证</span>
              </div>
            </div>
          </div>
          
        </section>

        <!-- 功能设置区 -->
        <section class="settings-section">
          <h2 class="section-title">账户管理</h2>
          <div class="settings-list">
            <button class="setting-button" @click="changePassword">
              <div class="setting-icon">🔐</div>
              <span>修改密码</span>
              <div class="setting-arrow">→</div>
            </button>
            
            <button class="setting-button" @click="about">
              <div class="setting-icon">ℹ️</div>
              <span>关于智慧党建</span>
              <div class="setting-arrow">→</div>
            </button>
            
            <button class="setting-button logout-button" @click="logout">
              <div class="setting-icon">🚪</div>
              <span>退出登录</span>
              <div class="setting-arrow">→</div>
            </button>
          </div>
        </section>
      </div>

      <!-- 右侧表单区域 -->
      <div class="right-section">
        <transition name="slide-fade">
          <div v-if="activePanel" class="form-panel">

            <!-- 修改密码表单 -->
            <div v-if="activePanel === 'password'" class="change-password-form">
              <div class="form-header">
                <h2 class="form-title">修改密码</h2>
                <button class="close-button" @click="closePanel">×</button>
              </div>
              <form @submit.prevent="savePassword" class="form-content">
                <div class="form-group">
                  <label class="form-label">当前密码</label>
                  <input v-model="passwordFormData.oldPassword" type="password" class="form-input" placeholder="请输入当前密码">
                </div>
                <div class="form-group">
                  <label class="form-label">新密码</label>
                  <input v-model="passwordFormData.newPassword" type="password" class="form-input" placeholder="请输入新密码">
                </div>
                <div class="form-group">
                  <label class="form-label">确认新密码</label>
                  <input v-model="passwordFormData.confirmPassword" type="password" class="form-input" placeholder="请再次输入新密码">
                </div>
                <div class="form-actions">
                  <button type="button" class="cancel-button" @click="closePanel">取消</button>
                  <button type="submit" class="save-button">保存</button>
                </div>
              </form>
            </div>

            <!-- 企业认证表单 -->
            <div v-if="activePanel === 'auth'" class="auth-form">
              <div class="form-header">
                <h2 class="form-title">企业认证</h2>
                <button class="close-button" @click="closePanel">×</button>
              </div>
              <form @submit.prevent="submitAuth" class="form-content">
                <div class="form-group">
                  <label class="form-label">真实姓名 <span class="required">*</span></label>
                  <input v-model="authFormData.realName" type="text" class="form-input" placeholder="请输入真实姓名" required>
                </div>
                <div class="form-group">
                  <label class="form-label">手机号 <span class="required">*</span></label>
                  <input v-model="authFormData.phone" type="tel" class="form-input" placeholder="请输入手机号" required>
                </div>
                <div class="form-actions">
                  <button type="button" class="cancel-button" @click="closePanel">取消</button>
                  <button type="submit" class="save-button" :disabled="isAuthenticating">
                    <span v-if="isAuthenticating" class="loading">⏳</span>
                    {{ isAuthenticating ? '认证中...' : '提交认证' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
          
          <!-- 无表单时显示的提示已删除 -->
    </transition>
    

  </div>
    </main>
  </div>
</template>

<style scoped>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.personal-home-container {
  min-height: 100vh;
  width: 100%;
  background: transparent;
  background-attachment: fixed;
  padding-bottom: 50px;
  position: relative;
}

/* 添加党建主题装饰背景 */
.party-decoration-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(circle at 10% 20%, rgba(255, 0, 0, 0.05) 0%, transparent 30%),
    radial-gradient(circle at 90% 80%, rgba(255, 0, 0, 0.05) 0%, transparent 30%);
  pointer-events: none;
  z-index: 0;
}

/* 右侧背景图片 */
.right-background {
  position: fixed;
  right: 192px;
  top: 15px;
  height: 100vh;
  width: 25%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 20px;
  pointer-events: none;
  z-index: 1;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

/* 第一张背景图片 */
.background-image-1 {
  width: 100%;
  height: calc(50% - 10px);
  background-image: url('@/assets/PersonHomebackground.png');
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
}

/* 第二张背景图片 */
.bg-img-2 {
  width: 100%;
  height: calc(50% - 10px);
  background-image: url('@/assets/PersonHomebackground2.png');
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
}

/* 添加装饰元素 */
.personal-home-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #ff0000, #ff0000, #ff0000);
  z-index: 1001;
}

/* 顶部导航栏 */
.top-navigation {
  background: white;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  z-index: 1000;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.3);
  border-bottom: 2px solid #ff0000;
}

.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* 左侧按钮组 */
.nav-left-buttons {
  display: flex;
  align-items: center;
  gap: 15px;
}

/* 导航按钮样式 */
.nav-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: transparent;
  color: #000000;
  border: 1px solid rgba(255, 0, 0, 0.4);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.nav-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 0, 0, 0.2), transparent);
  transition: all 0.3s ease;
}

.nav-button:hover {
  background: rgba(0, 0, 0, 0.05);
  border-color: #ff0000;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.nav-button:hover::before {
  left: 100%;
}

.nav-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

/* 中间logo */
.nav-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 5px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(10px);
}

.logo-image {
  width: 36px;
  height: 36px;
  object-fit: contain;
  border-radius: 6px;
  border: 2px solid #ff0000;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #000000;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  font-family: 'Microsoft YaHei', sans-serif;
  letter-spacing: 1px;
}

/* 主内容区 - 改为左右布局 */
.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px 20px;
  padding-top: 90px; /* 添加上边距，避免被固定导航栏遮挡 */
  display: flex;
  gap: 30px;
  width: 100%;
}

/* 左侧信息展示区 */
.left-section {
  width: 45%;
  max-width: none;
  display: flex;
  flex-direction: column;
  gap: 30px;
  background-color: white;
  padding: 20px;
  border-radius: 16px;
}

/* 右侧表单区域 */
.right-section {
  width: 55%;
  min-width: none;
  max-width: none;
  position: sticky;
  top: 100px;
  height: fit-content;
  margin: 0 auto;
}

/* 空状态提示已删除 */

/* 表单面板 */
.form-panel {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  width: 100%;
  border-top: 3px solid #ff0000;
  position: relative;
}

.form-panel::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, transparent, #8b0000, transparent);
}

/* 表单头部 */
.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 40px;
  border-bottom: 1px solid rgba(139, 0, 0, 0.1);
  background: linear-gradient(135deg, #fff5f5 0%, #ffdee0 100%);
  position: relative;
}

.form-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, #8b0000, #b22222, transparent);
}

.form-title {
  font-size: 24px;
  font-weight: 700;
  color: #8b0000;
  margin: 0;
  position: relative;
  padding-left: 20px;
}

.form-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 24px;
  background: linear-gradient(180deg, #ff0000, #ff0000);
  border-radius: 2px;
}

.close-button {
  width: 30px;
  height: 30px;
  border: 1px solid #ff0000;
  background: white;
  font-size: 24px;
  cursor: pointer;
  color: #8b0000;
  border-radius: 50%;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background: #ff0000;
  color: #8b0000;
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 表单内容 */
.form-content {
  padding: 40px;
  position: relative;
}

.form-content::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, transparent 70%, rgba(255, 0, 0, 0.05) 100%);
  border-radius: 100% 0 0 0;
  pointer-events: none;
}

.form-group {
  margin-bottom: 25px;
  position: relative;
}

.form-label {
  display: block;
  font-size: 16px;
  font-weight: 500;
  color: #8b0000;
  margin-bottom: 10px;
  padding-left: 5px;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 14px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: white;
  box-sizing: border-box;
  position: relative;
  z-index: 1;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #ff0000;
  box-shadow: 0 0 0 3px rgba(255, 0, 0, 0.2);
  background: #ffebee;
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
  line-height: 1.6;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  color: #4a5568;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid rgba(139, 0, 0, 0.1);
  position: relative;
  z-index: 2;
}

.cancel-button,
.save-button {
  padding: 14px 30px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e2e8f0;
  min-width: 120px;
  position: relative;
  overflow: hidden;
}

.cancel-button {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  color: #8b0000;
  border-color: #ff0000;
}

.cancel-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 0, 0, 0.2), transparent);
  transition: all 0.3s ease;
}

.cancel-button:hover {
  background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
  border-color: #ff0000;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.cancel-button:hover::before {
  left: 100%;
}

.save-button {
  background: linear-gradient(135deg, #8b0000 0%, #cd5c5c 100%);
  color: white;
  border-color: #ff0000;
  font-weight: 600;
}

.save-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: all 0.3s ease;
}

.save-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 0, 0, 0.4);
}

.save-button:hover::before {
  left: 100%;
}

/* 过渡动画 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* 通用标题样式 */
.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #8b0000;
  margin-bottom: 20px;
  position: relative;
  padding-left: 15px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 5px;
  height: 20px;
  background: linear-gradient(180deg, #ff0000, #ff0000);
  border-radius: 3px;
}

.section-title::after {
  content: '';
  position: absolute;
  left: 15px;
  bottom: -8px;
  width: 40px;
  height: 3px;
  background: linear-gradient(135deg, #8b0000 0%, #b22222 100%);
  border-radius: 3px;
}

/* 用户信息卡片 */
.profile-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  width: 100%;
  max-width: 700px;
  margin: 0 auto;
  border-top: 3px solid #ff0000;
  position: relative;
  overflow: hidden;
}

.profile-card::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, rgba(255, 0, 0, 0.15) 0%, transparent 70%);
  border-radius: 0 0 0 100%;
}

.profile-card::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, transparent, #8b0000, transparent);
}

.profile-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.2);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 35px;
  margin-bottom: 35px;
  justify-content: center;
  position: relative;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #ff0000;
  box-shadow: 0 6px 20px rgba(139, 0, 0, 0.3);
  position: relative;
  background: #ffebee;
}

.avatar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 2px solid rgba(139, 0, 0, 0.4);
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(255, 0, 0, 0.2);
}

.profile-info {
  flex: 1;
}

.profile-main-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.user-name {
  font-size: 32px;
  font-weight: 700;
  color: #8b0000;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  font-family: 'Microsoft YaHei', sans-serif;
}

.user-position {
  background: linear-gradient(135deg, #8b0000 0%, #b22222 100%);
  color: white;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(139, 0, 0, 0.3);
  border: 1px solid rgba(255, 0, 0, 0.3);
}

/* 企业认证状态样式 */
.auth-status {
  margin-top: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  color: #8b0000;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  font-size: 16px;
  border: 1px solid #ff0000;
}

.auth-status.not-authenticated {
  border-color: #ff0000;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.auth-status:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #ff0000;
}

.auth-status::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 0, 0, 0.2), transparent);
  transition: all 0.3s ease;
}

.auth-status:hover::before {
  left: 100%;
}

.auth-icon {
      margin-right: 8px;
      width: 20px;
      height: 20px;
      vertical-align: middle;
      fill: currentColor;
    }

.auth-text {
  font-size: 14px;
}

.enterprise-name {
  font-size: 14px;
  font-weight: 600;
  margin-left: 5px;
  color: #2d3748;
}

/* 认证表单样式 */
.required {
  color: #e53e3e;
  font-weight: 700;
}

.loading {
  margin-right: 5px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.profile-meta {
  display: flex;
  gap: 25px;
  padding-left: 2px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
}

.meta-label {
  color: #718096;
}

.meta-value {
  color: #8b0000;
  font-weight: 500;
}

.edit-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  color: #8b0000;
  border: 1px solid #ff0000;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.edit-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 0, 0, 0.2), transparent);
  transition: all 0.3s ease;
}

.edit-button:hover {
  background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
  border-color: #ff0000;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.edit-button:hover::before {
  left: 100%;
}

/* 已移除用户等级和积分相关样式 */

/* 已移除快捷功能、学习统计和最近活动相关样式 */

/* 功能设置区 */
.settings-section {
  background: #ffffff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 700px;
  margin: 0 auto;
  border-top: 3px solid #ff0000;
  position: relative;
  background: linear-gradient(180deg, rgba(255, 0, 0, 0.03) 0%, transparent 100%);
}

.settings-section::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, #8b0000, transparent);
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.setting-button {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 25px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 1px solid #ff0000;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  font-size: 18px;
  color: #8b0000;
  width: 100%;
  position: relative;
  overflow: hidden;
}

.setting-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 0, 0, 0.15), transparent);
  transition: all 0.3s ease;
}

.setting-button:hover {
  background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
  border-color: #ff0000;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transform: translateX(5px);
}

.setting-button:hover::before {
  left: 100%;
}

.setting-icon {
  margin-right: 15px;
  font-size: 20px;
  color: #8b0000;
}

.setting-arrow {
  color: #8b0000;
  font-size: 16px;
  opacity: 0.7;
}

.logout-button {
  background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
  border-color: #e53e3e;
  color: #8b0000;
}

.logout-button:hover {
  background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
  border-color: #c53030;
  transform: translateX(5px);
}

/* 响应式设计 */
/* 导航栏响应式调整 */
@media (max-width: 1200px) {
  .content-wrapper {
    flex-direction: column;
  }
  
  .right-section {
    min-width: auto;
    position: static;
    max-width: none;
  }
  
  .left-section {
    max-width: none;
  }
  
  /* 添加党建主题装饰 */
  .profile-card,
  .settings-section,
  .form-panel {
    border-top: 2px solid #ff0000;
  }
}

@media (max-width: 768px) {
    /* 导航栏响应式 */
    .nav-container {
      padding: 0 15px;
    }
    
    .logo-text {
      font-size: 16px;
      display: none; /* 在小屏幕上隐藏文字，只显示图标 */
    }
    
    .nav-button {
      padding: 6px 12px;
      font-size: 12px;
      border-color: rgba(255, 0, 0, 0.3);
    }
    
    .nav-button span:not(.kb-icon):not(.back-icon) {
      display: none; /* 在小屏幕上隐藏按钮文字 */
    }
    
    /* 内容区域响应式 */
    .content-wrapper {
      padding-top: 70px;
      padding-left: 15px;
      padding-right: 15px;
    }
    
    /* 小屏幕下优化党建主题元素 */
    .logo-image {
      border-width: 1px;
    }
    
    .nav-logo {
      padding: 3px;
    }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .avatar {
    border-width: 3px;
  }
  
  .profile-meta {
    justify-content: center;
    flex-wrap: wrap;
    gap: 15px;
  }
  
  .form-content {
    padding: 20px;
  }
  
  .form-header {
    padding: 15px 20px;
  }
  
  .form-title {
    font-size: 20px;
    padding-left: 15px;
  }
  
  .section-title {
    font-size: 18px;
  }
}

@media (max-width: 480px) {
    /* 小屏幕导航栏进一步调整 */
    .nav-container {
      padding: 0 10px;
    }
    
    .nav-left-buttons {
      gap: 8px;
    }
    
    .logo-image {
      width: 28px;
      height: 28px;
      border-width: 1px;
    }
  
  .main-content {
    padding: 20px 15px;
  }
  
  .profile-card,
  .settings-section {
    padding: 20px;
    border-top: 2px solid #ff0000;
  }
  
  .user-name {
    font-size: 24px;
    color: #8b0000;
  }
  
  .setting-button {
    padding: 15px 20px;
    font-size: 16px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .cancel-button,
  .save-button {
    width: 100%;
  }
  
  /* 小屏幕下增强党建主题视觉效果 */
  .meta-value,
  .setting-button {
    color: #8b0000;
  }
}
</style>