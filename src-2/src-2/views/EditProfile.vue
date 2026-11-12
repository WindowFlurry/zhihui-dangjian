<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const userInfo = ref({
  name: '张三',
  avatar: 'https://picsum.photos/id/64/100/100',
  unit: '模范出租车'
})

const name = ref(userInfo.value.name)
const unit = ref(userInfo.value.unit)

const saveProfile = () => {
  // 保存个人信息
  userInfo.value.name = name.value
  userInfo.value.unit = unit.value
  console.log('保存个人信息:', userInfo.value)
  router.push('/personal-home')
}

const goBack = () => {
  router.push('/personal-home')
}
</script>

<template>
  <div class="edit-profile-container">
    <header class="header">
      <button class="back-button" @click="goBack">返回</button>
      <div class="title">个人资料</div>
      <div class="empty"></div>
    </header>

    <main class="main-content">
      <div class="profile-section">
        <img :src="userInfo.avatar" alt="用户头像" class="avatar">
      </div>

      <div class="form-group">
        <label for="name">修改姓名<sup>*</sup></label>
        <input type="text" id="name" v-model="name" placeholder="请输入姓名">
      </div>

      <div class="form-group">
        <label for="unit">单位认证<sup>*</sup></label>
        <input type="text" id="unit" v-model="unit" placeholder="请输入单位名称">
      </div>

      <button class="submit-button" @click="saveProfile">完成</button>
    </main>
  </div>
</template>

<style scoped>
.edit-profile-container {
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

.back-button {
  padding: 8px 16px;
  background-color: rgba(255, 255, 255, 0.9);
  color: #333;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.title {
  font-size: 20px;
  font-weight: bold;
  color: #fff;
}

.empty {
  width: 80px;
}

.main-content {
  padding: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

.profile-section {
  display: flex;
  justify-content: center;
  margin: 20px 0 40px;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #f0f0f0;
}

.form-group {
  width: 100%;
  margin-bottom: 25px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-size: 16px;
  color: #333;
}

sup {
  color: #ff4d4f;
}

input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 16px;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #4096ff;
  box-shadow: 0 0 0 2px rgba(64, 154, 255, 0.2);
}

.submit-button {
  width: 100%;
  padding: 12px 0;
  background-color: #4096ff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 20px;
}

.submit-button:hover {
  background-color: #1890ff;
}
</style>