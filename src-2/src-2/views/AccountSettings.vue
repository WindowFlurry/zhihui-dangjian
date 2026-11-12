<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const userInfo = ref({
  phone: '1234567899',
  password: '**********',
  avatar: 'https://picsum.photos/id/64/100/100'
})

const goBack = () => {
  router.push('/personal-home')
}

const saveSettings = () => {
  // 保存逻辑
  console.log('保存账号设置', userInfo.value)
  // 保存成功后返回个人首页
  router.push('/personal-home')
}
</script>

<template>
  <div class="account-settings-container">
    <header class="header">
      <div class="logo">智慧党建</div>
      <button class="back-button" @click="goBack">返回</button>
    </header>

    <main class="main-content">
      <h1>账号设置</h1>
      <div class="profile-picture">
        <img :src="userInfo.avatar" alt="用户头像" class="avatar">
      </div>

      <form class="settings-form">
        <div class="form-group">
          <label for="phone">已绑定的手机号 *</label>
          <input type="tel" id="phone" v-model="userInfo.phone" readonly>
        </div>

        <div class="form-group">
          <label for="password">修改密码 *</label>
          <input type="password" id="password" v-model="userInfo.password">
        </div>

        <button type="button" class="save-button" @click="saveSettings">完成</button>
      </form>
    </main>
  </div>
</template>

<style scoped>
.account-settings-container {
  min-height: 100vh;
  width: 100vw;
  background-color: #f5f5f5;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  position: relative;
  left: 50%;
  transform: translateX(-50%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  height: 70px;
  background-color: #FF9292;
  border-bottom: none;
  width: 100%;
  box-sizing: border-box;
}

.logo {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
  margin-left: 20px;
}

.back-button {
  padding: 8px 16px;
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 20px;
}

.main-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  font-size: 24px;
  color: #333;
  margin-bottom: 30px;
  align-self: flex-start;
  margin-left: calc(10% - 20px);
}

.profile-picture {
  display: flex;
  justify-content: center;
  margin-bottom: 40px;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #f0f0f0;
}

.settings-form {
  width: 80%;
  max-width: 500px;
  background-color: #fff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.form-group {
  margin-bottom: 30px;
}

label {
  display: block;
  margin-bottom: 10px;
  font-size: 16px;
  color: #333;
}

input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box;
}

input[readonly] {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.save-button {
  width: 100%;
  padding: 12px 0;
  background-color: #6c5ce7;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 20px;
}

.save-button:hover {
  background-color: #5d4fd2;
}
</style>