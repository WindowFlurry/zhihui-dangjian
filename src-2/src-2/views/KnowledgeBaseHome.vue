<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import kbAPI from '../api/kb.js'
import { Message, User } from '@element-plus/icons-vue'

// 用户信息
const userInfo = ref({
  name: '用户'
})

// 表单数据
const formData = ref({
  name: '',
  description: ''
})

// 文件上传相关变量
const files = ref([])
const isDragover = ref(false)
const isUploading = ref(false) // 上传状态
const uploadProgress = ref(0) // 上传进度
const fileInputRef = ref(null) // 文件输入框的引用

// 文件选择
const handleFileChange = (event) => {
  const selectedFiles = event.target.files
  if (selectedFiles.length) {
    files.value = [...files.value, ...Array.from(selectedFiles)]
  }
}

// 拖拽进入
const handleDragEnter = (event) => {
  event.preventDefault()
  isDragover.value = true
}

// 拖拽离开
const handleDragLeave = (event) => {
  event.preventDefault()
  isDragover.value = false
}

// 拖拽释放
const handleDrop = (event) => {
  event.preventDefault()
  isDragover.value = false
  const droppedFiles = event.dataTransfer.files
  if (droppedFiles.length) {
    files.value = [...files.value, ...Array.from(droppedFiles)]
  }
}

// 移除文件
const removeFile = (index) => {
  files.value = files.value.filter((_, i) => i !== index)
}

// 清空文件
const clearFiles = () => {
  files.value = []
}

// 检查表单
const isFormValid = () => {
  return formData.value.name && formData.value.description && files.value.length > 0
}

const router = useRouter()
const searchQuery = ref('')
const knowledgeBases = ref([
  // 添加静态样例数据
  {
    id: 'kb_001',
    name: '中国共产党章程',
    description: '包含中国共产党的纲领、组织机构、党员权利义务等基本内容',
    createdAt: '2023-06-15 09:30',
    fileId: 'file_001',
    fileSize: 1024 * 1024,
    fileType: 'pdf'
  },
  {
    id: 'kb_002',
    name: '党史学习资料汇编',
    description: '汇总中国共产党从成立至今的重要历史事件、会议和人物',
    createdAt: '2023-07-20 14:45',
    fileId: 'file_002',
    fileSize: 2048 * 1024,
    fileType: 'docx'
  },
  {
    id: 'kb_003',
    name: '习近平新时代中国特色社会主义思想',
    description: '深入解析习近平新时代中国特色社会主义思想的核心内容和实践要求',
    createdAt: '2023-08-10 11:20',
    fileId: 'file_003',
    fileSize: 3072 * 1024,
    fileType: 'pdf'
  },
  {
    id: 'kb_004',
    name: '党风廉政建设学习手册',
    description: '包含党的纪律处分条例、廉洁自律准则等重要内容',
    createdAt: '2023-09-05 16:10',
    fileId: 'file_004',
    fileSize: 1536 * 1024,
    fileType: 'docx'
  }
])
const isCreateModalVisible = ref(false)

// 切换到首页
const goToHome = () => {
  router.push('/home')
}



// 切换到个人首页
const goToPersonalHome = () => {
  router.push('/personal-home')
}

// 跳转到知识库详情页
const goToKnowledgeBaseDetail = (id) => {
  router.push(`/knowledge-base-detail/${id}`)
}

// 打开创建知识库模态框
const openCreateKnowledgeBaseModal = () => {
  isCreateModalVisible.value = true
}

// 删除知识库
const deleteKnowledgeBase = (id) => {
  knowledgeBases.value = knowledgeBases.value.filter(kb => kb.id !== id)
}

// 向知识库添加文件
const addFileToKnowledgeBase = (id) => {
  // 这里可以实现向特定知识库添加文件的逻辑
  console.log('向知识库添加文件:', id)
  alert(`选择文件添加到知识库: ${knowledgeBases.value.find(kb => kb.id === id)?.name}`)
  // 后续可以实现文件选择和上传逻辑
}

// 搜索知识库
const searchKnowledgeBases = () => {
  // 根据searchQuery过滤知识库
  if (!searchQuery.value.trim()) {
    // 如果搜索框为空，则显示所有知识库
    return knowledgeBases.value
  }
  
  const query = searchQuery.value.toLowerCase().trim()
  return knowledgeBases.value.filter(kb => 
    kb.name.toLowerCase().includes(query) || 
    kb.description.toLowerCase().includes(query)
  )
}

// 打开文件对话框
const openFileDialog = () => {
  try {
    if (fileInputRef.value) {
      fileInputRef.value.click()
    }
  } catch (error) {
    console.error('打开文件对话框失败:', error)
    alert('打开文件选择框失败，请刷新页面重试。')
  }
}

// 获取文件列表
const fetchFileList = async () => {
  try {
    const fileList = await kbAPI.getFileList()
    console.log('获取文件列表成功:', fileList)
    
    // 如果API返回了数据，则更新知识库列表
    if (fileList && Array.isArray(fileList) && fileList.length > 0) {
      // 清空现有的知识库列表
      knowledgeBases.value = []
      
      // 所有知识库默认启用
      fileList.forEach((file, index) => {
        const knowledgeBase = {
          id: file.id || `kb_${Date.now()}_${index}`,
          name: file.name || `知识库_${index + 1}`,
          description: file.description || '从API获取的知识库',
          createdAt: file.createdAt || new Date().toLocaleString('zh-CN'),
          fileId: file.file_id,
          fileSize: file.size,
          fileType: file.type
        }
        
        // 所有知识库默认添加到列表中
        knowledgeBases.value.push(knowledgeBase)
      })
    } else {
      console.log('使用默认的知识库样例数据')
    }
  } catch (error) {
    console.error('获取文件列表失败:', error)
    console.warn('注意：知识库服务暂时不可用，显示静态样例数据')
    // 保留默认的静态样例数据
  }
}

// 组件加载时获取文件列表
// 添加一个延时重试机制
const retryFetchFileList = () => {
  const maxRetries = 3
  let retries = 0
  
  const attemptFetch = () => {
    retries++
    fetchFileList().catch(() => {
      if (retries < maxRetries) {
        console.log(`第${retries}次尝试获取文件列表失败，${5}秒后重试...`)
        setTimeout(attemptFetch, 5000)
      } else {
        console.log('已达到最大重试次数，停止尝试获取文件列表。')
      }
    })
  }
  
  attemptFetch()
}

// 组件加载时获取文件列表
retryFetchFileList()

// 从localStorage中获取用户名
const account = localStorage.getItem('account') || localStorage.getItem('phoneNumber')
if (account) {
  userInfo.value.name = account
}

// 创建知识库
const createKnowledgeBase = async () => {
  if (!isFormValid()) {
    alert('请填写完整的表单信息并选择文件！')
    return
  }

  try {
    isUploading.value = true
    uploadProgress.value = 0
    
    // 创建一个新的知识库对象
    const newKnowledgeBase = {
      id: Date.now(),
      name: formData.value.name,
      description: formData.value.description,
      createdAt: new Date().toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }),
      files: []
    }

    // 逐个上传文件
    const uploadPromises = files.value.map(async (file, index) => {
      try {
        const response = await kbAPI.uploadDocument(file, formData.value.description)
        newKnowledgeBase.files.push({
          id: response.file_id || `file_${Date.now()}_${index}`,
          name: file.name,
          size: file.size,
          type: file.type
        })
        uploadProgress.value = Math.round(((index + 1) / files.value.length) * 100)
        return response
      } catch (error) {
        console.error(`文件 ${file.name} 上传失败:`, error)
        // 继续上传其他文件，记录错误
        return { success: false, file: file.name, error: error.message }
      }
    })

    const results = await Promise.all(uploadPromises)
    
    // 检查是否有文件上传成功
    const hasSuccess = results.some(result => result.success !== false)
    
    if (hasSuccess) {
      // 创建成功后关闭模态框
      isCreateModalVisible.value = false
      // 重置表单
      formData.value = {
        name: '',
        description: ''
      }
      // 清空文件列表
      clearFiles()

      // 提示用户创建成功
      const failedFiles = results.filter(result => result.success === false)
      if (failedFiles.length > 0) {
        alert(`知识库创建成功，但有 ${failedFiles.length} 个文件上传失败。`)
      } else {
        alert('知识库创建成功！')
      }

      // 所有知识库默认添加到列表中
      knowledgeBases.value.push(newKnowledgeBase)
    } else {
      alert('所有文件上传失败，请稍后重试！')
    }
  } catch (error) {
    console.error('创建知识库失败:', error)
    alert('创建知识库失败：' + (error.message || '未知错误'))
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
  }
}
</script>

<template>
  <div class="knowledge-base-home-container">
    <!-- 导航栏 -->
    <header class="header">
      <div class="logo">
        智慧党建
        <img src="@/logo.jpg" alt="Logo" class="logo-image" />
        <nav class="nav">
          <el-button 
            class="nav-button home-button"
            @click="goToHome"
            type="primary"
          >
            <template #icon><Message /></template>
            智能对话
          </el-button>
          <el-button 
            class="nav-button"
            @click="goToPersonalHome"
            type="primary"
          >
            <template #icon><User /></template>
            个人首页
          </el-button>
        </nav>
      </div>
      <div class="user-info">
        <span class="username">{{ userInfo.name }}</span>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
    <div class="left-panel">
      <div class="search-area">
        <input
          v-model="searchQuery"
          placeholder="搜索知识库..."
          class="search-input"
          @input="searchKnowledgeBases"
        >
      </div>
      <button
        class="create-button"
        @click="openCreateKnowledgeBaseModal"
      >
        创建知识库
      </button>
    </div>
    <div class="right-panel">
      <div class="panel-header">
        <h2 class="panel-title">知识库</h2>
      </div>
      <div class="knowledge-bases">
        <div v-for="kb in searchKnowledgeBases()" :key="kb.id" class="knowledge-base-item">
          <div class="knowledge-base-icon">📚</div>
          <div class="knowledge-base-details">
            <div class="knowledge-base-name">{{ kb.name }}</div>
            <div class="knowledge-base-desc">{{ kb.description }}</div>
            <div class="knowledge-base-time">{{ kb.createdAt }}</div>
          </div>
          <div class="action-buttons">
            <button
              class="delete-button"
              @click="deleteKnowledgeBase(kb.id)"
              title="删除知识库"
            >
              删除文件
            </button>
            <button
              class="add-file-button"
              @click="addFileToKnowledgeBase(kb.id)"
              title="添加文件"
            >
              添加文件
            </button>
          </div>
        </div>
        <div v-if="searchKnowledgeBases().length === 0" class="empty-state">
          <p>暂无知识库数据</p>
        </div>
      </div>
    </div>
  </main>

    <!-- 创建知识库模态框 -->
    <div class="modal" v-if="isCreateModalVisible">
      <div class="modal-overlay" @click="isCreateModalVisible = false"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title">创建知识库</h3>
          <button class="close-button" @click="isCreateModalVisible = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">名称 *</label>
            <input
              type="text"
              class="form-input"
              placeholder="请输入知识库名称"
              v-model="formData.name"
            >
          </div>
          <div class="form-group">
            <label class="form-label">描述 *</label>
            <input
              type="text"
              class="form-input"
              placeholder="请输入知识库描述"
              v-model="formData.description"
            >
          </div>

          <div class="form-group">
            <label class="form-label">上传文件 *</label>
            <div
              class="upload-area"
              :class="{ dragover: isDragover }"
              @click="openFileDialog"
              @dragenter="handleDragEnter"
              @dragover="handleDragEnter"
              @dragleave="handleDragLeave"
              @drop="handleDrop"
            >
              <div class="upload-icon">📁</div>
              <div class="upload-text">点击或拖拽文件到这里上传</div>
              <div class="upload-hint">支持格式：rar, zip, doc, docx, pdf, ppt, pptx, xls, xlsx, txt, md</div>
            </div>
            <input
              type="file"
              ref="fileInputRef"
              class="file-input"
              multiple
              @change="handleFileChange"
            >

            <div class="file-list" v-if="files.length > 0">
              <div v-for="(file, index) in files" :key="index" class="file-item">
                <div class="file-name">{{ file.name }}</div>
                <button class="remove-file" @click="removeFile(index)">×</button>
              </div>
            </div>
          </div>

          <button
            class="create-button"
            @click="createKnowledgeBase"
            :disabled="!isFormValid() || isUploading"
          >
            <template v-if="isUploading">
              上传中... {{ uploadProgress }}%
            </template>
            <template v-else>
              创建并导入
            </template>
          </button>
          
          <!-- 上传进度条 -->
          <div v-if="isUploading" class="upload-progress-container">
            <div class="upload-progress-bar">
              <div 
                class="upload-progress-fill" 
                :style="{ width: uploadProgress + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.knowledge-base-home-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #fdf2e9 0%, #fff 100%);
  position: relative;
}

/* 党建主题装饰背景 */
.knowledge-base-home-container::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100" height="100" fill="none" stroke="%23dc143c" stroke-width="0.5" opacity="0.1"/></svg>');
  pointer-events: none;
  z-index: 0;
}

/* 导航栏 */
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    height: 72px;
    background: linear-gradient(90deg, #8b0000 0%, #a80000 100%);
    border-bottom: 3px solid #dc143c;
    box-shadow: 0 4px 16px rgba(139, 0, 0, 0.4);
    position: relative;
    z-index: 100;
  }
  
  .header::after {
    content: '';
    position: absolute;
    bottom: -3px;
    left: 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, #dc143c 50%, transparent 100%);
  }

  .header .logo {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .header .logo .nav {
    display: flex;
    gap: 10px;
  }

  .logo {
    font-size: 24px;
    font-weight: bold;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 8px;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  }

  .logo-image {
    width: 56px;
    height: 56px;
    vertical-align: middle;
    border-radius: 50%;
    border: 2px solid #dc143c;
    box-shadow: 0 0 15px rgba(139, 0, 0, 0.6);
    background-color: white;
    padding: 2px;
    transition: transform 0.3s ease;
  }
  
  .logo:hover .logo-image {
    transform: rotate(5deg);
  }

  .nav {
    display: flex;
    gap: 10px;
  }

  .nav-button {
    padding: 8px 16px;
    background-color: rgba(255, 255, 255, 0.9);
    color: #8b0000;
    border: 1px solid rgba(139, 0, 0, 0.6);
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    position: relative;
    overflow: hidden;
    font-family: 'Microsoft YaHei', sans-serif;
    letter-spacing: 0.5px;
  }

  .nav-button:hover {
    background: linear-gradient(135deg, #fff 0%, #fff8dc 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    border-color: #dc143c;
  }

  .nav-button:active {
    transform: translateY(0);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  }
  
  .home-button {
    background: linear-gradient(135deg, #fff 0%, #fff8dc 100%);
    color: #8b0000;
    border-color: #dc143c;
  }
  
  .home-button:hover {
    background: linear-gradient(135deg, #fff 0%, #ffebcd 100%);
    border-color: #dc143c;
    box-shadow: 0 4px 12px rgba(139, 0, 0, 0.3);
  }

  .user-info {
    display: flex;
    align-items: center;
    color: #fff;
  }

  .username {
    margin-left: 5px;
    font-size: 16px;
    font-weight: 500;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    background: linear-gradient(135deg, #dc143c 0%, #cd5c5c 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    padding: 2px 8px;
    border-radius: 12px;
    background-color: rgba(139, 0, 0, 0.2);
  }


.search-bar {
  width: 300px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
}

/* 主内容区 */
.main-content {
  display: flex;
  flex: 1;
  background: linear-gradient(135deg, #fdf2e9 0%, #fff 100%);
  position: relative;
  z-index: 1;
}

.left-panel {
  width: 300px;
  padding: 20px;
  background: linear-gradient(135deg, #fff 0%, #fff8dc 100%);
  border-right: 2px solid #dc143c;
  box-shadow: 2px 0 12px rgba(139, 0, 0, 0.15);
  position: relative;
}

.left-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(90deg, #8b0000 0%, #cd5c5c 100%);
}

.search-area {
  margin-bottom: 20px;
  position: relative;
  padding-top: 5px;
}

.search-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #8b0000 0%, #cd5c5c 100%);
  box-shadow: 0 1px 3px rgba(139, 0, 0, 0.2);
}

.search-input {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid rgba(139, 0, 0, 0.5);
    border-radius: 4px;
    font-size: 14px;
    transition: all 0.3s;
  }

.search-input:focus {
  outline: none;
  border-color: #8b0000;
  box-shadow: 0 0 0 3px rgba(139, 0, 0, 0.1);
}

.create-button {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #8b0000 0%, #a80000 100%);
  color: white;
  border: 1px solid rgba(139, 0, 0, 0.6);
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 20px;
  transition: all 0.3s;
  box-shadow: 0 3px 8px rgba(139, 0, 0, 0.4);
  font-family: 'Microsoft YaHei', sans-serif;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.create-button:hover {
  background: linear-gradient(135deg, #a30000 0%, #dc143c 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(139, 0, 0, 0.4);
  border-color: #dc143c;
}

.list-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #8b0000;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
  position: relative;
  padding-left: 12px;
  font-family: 'Microsoft YaHei', sans-serif;
}

.list-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: linear-gradient(180deg, #8b0000 0%, #cd5c5c 100%);
  border-radius: 2px;
}

.knowledge-base-info {
  flex: 1;
}

.knowledge-base-name {
  font-size: 15px;
  font-weight: bold;
  color: #8b0000;
  text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.1);
}

.knowledge-base-time {
  font-size: 13px;
  color: #999;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

.add-file-button {
  background: linear-gradient(135deg, #8b0000 0%, #cd5c5c 100%);
  color: white;
  border: 1px solid rgba(255, 215, 0, 0.6);
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  height: 30px;
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(139, 0, 0, 0.3);
}

.add-file-button:hover {
  background: linear-gradient(135deg, #a30000 0%, #dc143c 100%);
  border-color: #dc143c;
  transform: translateY(-1px);
  box-shadow: 0 3px 6px rgba(139, 0, 0, 0.4);
}

.add-file-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(139, 0, 0, 0.3);
}

.delete-button {
  background: linear-gradient(135deg, #8b0000 0%, #cd5c5c 100%);
  color: white;
  border: 1px solid rgba(255, 215, 0, 0.6);
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  height: 30px;
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(139, 0, 0, 0.3);
}

.delete-button:hover {
  background: linear-gradient(135deg, #a30000 0%, #dc143c 100%);
  border-color: #dc143c;
  transform: translateY(-1px);
  box-shadow: 0 3px 6px rgba(139, 0, 0, 0.4);
}

.right-panel {
  flex: 1;
  padding: 20px;
  background: linear-gradient(135deg, #fff 0%, #fff8dc 100%);
  box-shadow: -2px 0 12px rgba(139, 0, 0, 0.08);
  position: relative;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid rgba(139, 0, 0, 0.5);
  position: relative;
}

.panel-header::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100px;
  height: 2px;
  background: linear-gradient(90deg, #8b0000 0%, #cd5c5c 100%);
}

.panel-title {
  font-size: 22px;
  font-weight: bold;
  color: #8b0000;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  padding-left: 12px;
}

.panel-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 5px;
  height: 25px;
  background: linear-gradient(180deg, #8b0000 0%, #cd5c5c 100%);
  border-radius: 2px;
}

.add-button {
  padding: 8px 16px;
  background: linear-gradient(135deg, #8b0000 0%, #cd5c5c 100%);
  color: white;
  border: 1px solid rgba(139, 0, 0, 0.6);
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 6px rgba(139, 0, 0, 0.3);
}

.add-button:hover {
  background: linear-gradient(135deg, #a30000 0%, #dc143c 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(139, 0, 0, 0.4);
  border-color: #dc143c;
}

.knowledge-bases {
  margin-top: 20px;
}

.knowledge-base-item {
  display: flex;
  padding: 15px;
  margin-bottom: 15px;
  background: linear-gradient(135deg, #fff 0%, #fff8dc 100%);
  border-radius: 6px;
  border: 2px solid rgba(139, 0, 0, 0.3);
  box-shadow: 0 3px 12px rgba(139, 0, 0, 0.12);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.knowledge-base-item:hover {
  box-shadow: 0 6px 20px rgba(139, 0, 0, 0.2);
  border-color: #dc143c;
  transform: translateY(-2px);
}

.knowledge-base-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 5px;
  height: 100%;
  background: linear-gradient(180deg, #8b0000 0%, #cd5c5c 100%);
}

.knowledge-base-item:hover {
  box-shadow: 0 6px 16px rgba(139, 0, 0, 0.15);
  border-color: #ffd700;
  transform: translateY(-2px);
}

.knowledge-base-icon {
  font-size: 28px;
  margin-right: 15px;
  color: #8b0000;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.knowledge-base-details {
  flex: 1;
}

.knowledge-base-desc {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
  line-height: 1.6;
}

/* 模态框 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(2px);
}

.modal-content {
  position: relative;
  width: 600px;
  background: linear-gradient(135deg, #fff 0%, #fff8dc 100%);
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(139, 0, 0, 0.35);
  border: 2px solid rgba(139, 0, 0, 0.3);
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #8b0000 0%, #cd5c5c 100%);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: linear-gradient(135deg, #fff 0%, #fff8dc 100%);
  border-bottom: 2px solid rgba(139, 0, 0, 0.5);
  position: relative;
}

.modal-header::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 120px;
  height: 2px;
  background: linear-gradient(90deg, #8b0000 0%, #cd5c5c 100%);
}

.modal-title {
  font-size: 20px;
  font-weight: bold;
  color: #8b0000;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.close-button {
  background: linear-gradient(135deg, #8b0000 0%, #cd5c5c 100%);
  border: 1px solid rgba(139, 0, 0, 0.6);
  font-size: 18px;
  cursor: pointer;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(139, 0, 0, 0.3);
}

.close-button:hover {
  background: linear-gradient(135deg, #a30000 0%, #dc143c 100%);
  transform: scale(1.1);
  box-shadow: 0 3px 6px rgba(139, 0, 0, 0.4);
  border-color: #dc143c;
}

.modal-body {
  padding: 20px;
  background-color: white;
}

.form-group {
  margin-bottom: 20px;
  position: relative;
  padding-left: 5px;
}

.form-group::before {
  content: '';
  position: absolute;
  left: 0;
  top: 5px;
  bottom: 5px;
  width: 2px;
  background: linear-gradient(180deg, #8b0000 0%, #cd5c5c 100%);
  border-radius: 1px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 15px;
  font-weight: bold;
  color: #8b0000;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid rgba(139, 0, 0, 0.5);
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
  background-color: rgba(255, 255, 255, 0.9);
}

.form-input:focus {
  outline: none;
  border-color: #8b0000;
  box-shadow: 0 0 0 3px rgba(139, 0, 0, 0.1);
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 20px;
  margin-bottom: 15px;
  border: 2px dashed rgba(139, 0, 0, 0.5);
  border-radius: 4px;
  background: linear-gradient(135deg, #fff 0%, #fff8dc 100%);
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover,
.upload-area.dragover {
  border-color: #8b0000;
  background: linear-gradient(135deg, #fff 0%, #fff8dc 100%);
  box-shadow: 0 0 0 3px rgba(139, 0, 0, 0.05);
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: #8b0000;
  text-shadow: 2px 2px 4px rgba(139, 0, 0, 0.2);
  transition: all 0.3s;
}

.upload-area:hover .upload-icon {
  color: #cd5c5c;
  transform: scale(1.05);
}

.upload-text {
  font-size: 16px;
  color: #8b0000;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid rgba(139, 0, 0, 0.3);
}

.btn-cancel {
  padding: 10px 20px;
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
  color: #8b0000;
  border: 1px solid rgba(139, 0, 0, 0.5);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  font-weight: 500;
}

.btn-cancel:hover {
  background: linear-gradient(135deg, #e0e0e0 0%, #d0d0d0 100%);
  border-color: #dc143c;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
}

.btn-submit {
  padding: 10px 20px;
  background: linear-gradient(135deg, #8b0000 0%, #cd5c5c 100%);
  color: white;
  border: 1px solid rgba(139, 0, 0, 0.6);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 6px rgba(139, 0, 0, 0.3);
  font-weight: 500;
}

.btn-submit:hover {
  background: linear-gradient(135deg, #a30000 0%, #dc143c 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(139, 0, 0, 0.4);
  border-color: #dc143c;
}

.upload-hint {
  font-size: 12px;
  color: #999;
  text-align: center;
}

.file-input {
  display: none;
}

.file-list {
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 10px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  margin-bottom: 5px;
  background: linear-gradient(135deg, #f9f9f9 0%, #fff8dc 100%);
  border-radius: 4px;
  border-left: 3px solid transparent;
  transition: all 0.3s ease;
}

.file-item:hover {
  border-left: 3px solid #8b0000;
  background: linear-gradient(135deg, #fff 0%, #fff8dc 100%);
}

.file-name {
  flex: 1;
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-file {
  background: none;
  border: none;
  font-size: 16px;
  color: #999;
  cursor: pointer;
  padding: 0 5px;
}

.remove-file:hover {
  color: #f44336;
}

.create-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* 上传进度条 */
.upload-progress-container {
  margin-top: 15px;
}

.upload-progress-bar {
  width: 100%;
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.upload-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b0000 0%, #cd5c5c 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
  box-shadow: 0 0 10px rgba(139, 0, 0, 0.3);
}
</style>