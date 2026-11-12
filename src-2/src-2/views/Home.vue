<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElCollapse, ElCollapseItem, ElMenu, ElMenuItem, ElButton } from 'element-plus'
import { ArrowRight, ArrowLeft, Edit, Setting, Upload, Paperclip, Document, User, HomeFilled, UserFilled } from '@element-plus/icons-vue'
import * as agentApi from '../api/agent.js'
import * as qaApi from '../api/qa.js'


const router = useRouter()
const userInfo = ref({
  name: '用户'
})

// 左侧历史对话面板收缩状态
const isSidebarCollapsed = ref(false)

// 切换左侧历史对话面板收缩状态
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

// 初始欢迎消息
const initialWelcomeMessage = ref({
  id: 1,
  role: 'ai',
  content: '你好，我是智慧党建助手，随时为您提供党建知识、政策解读和工作辅助服务',
  isWelcome: true
})

// 消息数组
const messages = ref([initialWelcomeMessage.value])

// 跟踪是否是第一次发送消息
const isFirstMessage = ref(true)

// 是否处于初始状态（欢迎页面）
const isInitialState = ref(true)
// 引用对话消息容器元素
const chatMessagesRef = ref(null)
const inputMessage = ref('')
const agentMode = ref(false)
const conversationHistory = ref([
  {
    id: 1,
    title: '初始对话',
    summary: '智慧党建助手问候'
  }
])
const currentConversationId = ref(1)

// 控制右侧面板的显示状态
const isPanelCollapsed = ref(false)

// 文件选择器引用
const fileInputRef = ref(null)

// 切换面板显示状态
const togglePanel = () => {
  isPanelCollapsed.value = !isPanelCollapsed.value
  // 保存用户偏好到localStorage
  localStorage.setItem('panelCollapsed', isPanelCollapsed.value.toString())
}

// 回调链接信息
const callbackLinks = ref([
  {
    id: 1,
    url: 'http://110.42.60.168:8888/api/callback/abc123xyz',
    timestamp: '2025-03-20 14:30:00',
    status: '有效',
    statusClass: 'status-valid'
  },
  {
    id: 2,
    url: 'http://110.42.60.168:8888/api/callback/def456uvw',
    timestamp: '2025-03-19 10:15:00',
    status: '已过期',
    statusClass: 'status-expired'
  }
])

// 复制链接到剪贴板
const copyLink = (url) => {
  navigator.clipboard.writeText(url).then(() => {
    alert('链接已复制到剪贴板')
  }).catch(err => {
    console.error('复制失败:', err)
  })
}

// 移除AI生成文件相关引用

// 在组件挂载时获取用户信息和面板状态
onMounted(() => {
  // 从localStorage中获取用户名
  const account = localStorage.getItem('account') || localStorage.getItem('phoneNumber')
  if (account) {
    userInfo.value.name = account
  }
  
  // 从localStorage中获取面板状态
  const savedPanelState = localStorage.getItem('panelCollapsed')
  if (savedPanelState !== null) {
    isPanelCollapsed.value = savedPanelState === 'true'
  }
})

// 切换到个人首页
const goToPersonalHome = () => {
  router.push('/personal-home')
}

// 跳转到知识库首页
const goToKnowledgeBaseHome = () => {
  router.push('/knowledge-base-home')
}

// 发送消息
  // 动画常量配置
  const ANIMATION_DURATIONS = {
    fadeIn: 500,    // 消息进入动画持续时间
    fadeOut: 300,   // 消息淡出动画持续时间
    transition: 300, // 过渡状态持续时间
    typeSpeed: 40   // 伪流式输出打字速度（毫秒/字）
  }
  
  const sendMessage = async () => {
    if (!inputMessage.value.trim()) return

    // 发送消息后切换到非初始状态
    if (isInitialState.value) {
      isInitialState.value = false
    }

    // 添加用户消息
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage.value,
      entering: true // 添加进入动画标志
    }
    
    // 清空输入框
    inputMessage.value = ''
    
    // 如果是首次发送消息，需要移除欢迎消息
    if (isFirstMessage.value) {
      // 为欢迎消息添加淡出动画
      const welcomeMessage = messages.value.find(msg => msg.isWelcome)
      if (welcomeMessage) {
        welcomeMessage.fadingOut = true
      }
      
      // 等待淡出动画完成后再切换消息
      setTimeout(() => {
        // 清空消息数组
        messages.value = []
        isFirstMessage.value = false
        
        // 推送用户消息
        messages.value.push(userMessage)
        
        // 滚动到底部
        scrollToBottom()
        
        // 使用nextTick确保DOM更新后再处理动画
        nextTick(() => {
          // DOM更新后移除进入标志
          setTimeout(() => {
            const msg = messages.value.find(m => m.id === userMessage.id)
            if (msg) {
              msg.entering = false
            }
          }, ANIMATION_DURATIONS.transition)
          
          // 显示处理中状态并发送请求（确保用户消息动画完成）
          setTimeout(() => {
            showProcessingAndSendRequest(userMessage)
          }, ANIMATION_DURATIONS.transition)
        })
      }, ANIMATION_DURATIONS.fadeOut) // 使用统一的淡出时间常量
    } else {
      // 不是首次发送消息，直接推送用户消息
      messages.value.push(userMessage)
      
      // 滚动到底部
      scrollToBottom()
      
      // 使用nextTick确保DOM更新后再处理动画
      nextTick(() => {
        // DOM更新后移除进入标志
        setTimeout(() => {
          const msg = messages.value.find(m => m.id === userMessage.id)
          if (msg) {
            msg.entering = false
          }
        }, ANIMATION_DURATIONS.transition)
        
        // 显示处理中状态并发送请求
        showProcessingAndSendRequest(userMessage)
      })
    }
  }
  
  // 统一处理响应消息的函数
  const handleResponse = (processingMessage, content, isError = false) => {
    // 找到处理中消息并添加淡出效果
    const processingMsg = messages.value.find(msg => msg.id === processingMessage.id)
    if (processingMsg) {
      // 添加淡出类
      processingMsg.fadingOut = true
      
      // 等待淡出动画完成后移除处理中消息并添加AI响应消息
      setTimeout(() => {
        // 在DOM更新前先移除处理中消息
        const index = messages.value.findIndex(msg => msg.id === processingMessage.id)
        if (index !== -1) {
          messages.value.splice(index, 1)
        }
        
        // 添加AI响应消息
        const responseMessage = {
          id: Date.now() + 2,
          role: 'ai',
          content: '', // 初始为空，用于伪流式输出
          fullContent: String(content), // 存储完整内容
          isError: isError,
          entering: true, // 添加进入动画标志
          error: isError // 添加error类用于CSS样式选择
        }
        messages.value.push(responseMessage)
        
        // 滚动到底部
        scrollToBottom()
        
        // 使用nextTick确保DOM更新后再处理动画
        nextTick(() => {
          // DOM更新后移除进入标志
          setTimeout(() => {
            const msg = messages.value.find(m => m.id === responseMessage.id)
            if (msg) {
              msg.entering = false
              // 开始伪流式输出
              let index = 0
              const typeInterval = setInterval(() => {
                if (index < msg.fullContent.length) {
                  msg.content += msg.fullContent.charAt(index)
                  index++
                  // 每添加一个字符就滚动到底部
                  scrollToBottom()
                } else {
                  clearInterval(typeInterval)
                }
              }, ANIMATION_DURATIONS.typeSpeed)
            }
          }, ANIMATION_DURATIONS.transition)
        })
      }, ANIMATION_DURATIONS.fadeOut) // 使用统一的淡出时间常量
    }
  }

  // 显示处理中状态并发送请求
  const showProcessingAndSendRequest = async (userMessage) => {
    // 显示"处理中"状态
    const processingMessage = {
      id: Date.now() + 1,
      role: 'ai',
      content: '正在处理您的请求...',
      processing: true,
      entering: true // 添加进入动画标志
    }
    messages.value.push(processingMessage)
    
    // 滚动到底部
    scrollToBottom()
    
    // 使用nextTick确保DOM更新后再处理动画
    nextTick(() => {
      // DOM更新后移除进入标志
      setTimeout(() => {
        const msg = messages.value.find(m => m.id === processingMessage.id)
        if (msg) {
          msg.entering = false
        }
      }, ANIMATION_DURATIONS.transition)
    })

    try {
      let response
      if (agentMode.value) {
        // 使用代理模式发送请求
        response = await agentApi.agentChat({
          content: userMessage.content,
          conversation_id: currentConversationId.value
        })
        
        // 处理响应
        handleResponse(processingMessage, response.data?.output || response.output || '处理成功，但未获取到具体内容')
      } else {
        // 使用普通问答模式
        // 获取当前会话ID
        const sessionId = sessionStorage.getItem('session_id') || '';
        const content = await qaApi.askQuestion(userMessage.content, sessionId);
        
        // 处理响应
        handleResponse(processingMessage, content.answer || '处理成功，但未获取到具体内容');
        
        // 更新会话ID
        if (content.session_id) {
          sessionStorage.setItem('session_id', content.session_id);
        }
      }
    } catch (error) {
      console.error('发送消息时出错:', error)
      
      // 处理错误响应
      handleResponse(processingMessage, `智能问答服务暂时不可用：${error.message || '未知错误'}`, true)
    }
  }

// 切换Agent模式
const toggleAgentMode = () => {
  agentMode.value = !agentMode.value
}

// 打开文件选择器
const openFileSelector = () => {
  fileInputRef.value?.click()
}

// 处理文件选择
const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // 上传中消息对象
  const uploadingMessage = {
    id: Date.now(),
    role: 'user',
    content: `正在上传文件: ${file.name}`,
    isUploading: true,
    entering: true // 添加进入动画标志
  }
  
  // 添加上传中消息
  messages.value.push(uploadingMessage)
  
  // 滚动到底部
  scrollToBottom()
  
  // 使用nextTick确保DOM更新后再处理动画
  nextTick(() => {
    setTimeout(() => {
      const msg = messages.value.find(m => m.id === uploadingMessage.id)
      if (msg) {
        msg.entering = false
      }
    }, ANIMATION_DURATIONS.transition)
  })
  
  try {
    // 使用智能问答的上传文件接口
    const response = await qaApi.uploadFile(file)
    
    // 找到上传中消息并添加淡出效果
    const uploadingMsg = messages.value.find(msg => msg.isUploading)
    if (uploadingMsg) {
      uploadingMsg.fadingOut = true
      
      // 等待淡出动画完成后移除上传中消息
      setTimeout(() => {
        // 移除上传中消息
        messages.value = messages.value.filter(m => !m.isUploading)
        
        // 上传成功消息
        const successMessage = {
          id: Date.now() + 1,
          role: 'user',
          content: `已上传文件: ${file.name}`,
          entering: true // 添加进入动画标志
        }
        messages.value.push(successMessage)
        
        // 添加AI响应
        const aiResponseMessage = {
          id: Date.now() + 2,
          role: 'ai',
          content: `文件上传成功！我已经可以基于这个文件回答你的问题了。请输入你关于这个文件的问题。`,
          entering: true // 添加进入动画标志
        }
        messages.value.push(aiResponseMessage)
        
        // 滚动到底部
        scrollToBottom()
        
        // 使用nextTick确保DOM更新后再处理动画
        nextTick(() => {
          // 移除上传成功消息的进入标志
          setTimeout(() => {
            const msg = messages.value.find(m => m.id === successMessage.id)
            if (msg) {
              msg.entering = false
            }
          }, ANIMATION_DURATIONS.transition)
          
          // 移除AI响应消息的进入标志
          setTimeout(() => {
            const msg = messages.value.find(m => m.id === aiResponseMessage.id)
            if (msg) {
              msg.entering = false
            }
          }, ANIMATION_DURATIONS.transition)
        })
      }, ANIMATION_DURATIONS.fadeOut)
    }
    
    // 清空文件输入
    event.target.value = ''
    
  } catch (error) {
    console.error('文件上传失败:', error)
    
    // 找到上传中消息并添加淡出效果
    const uploadingMsg = messages.value.find(msg => msg.isUploading)
    if (uploadingMsg) {
      uploadingMsg.fadingOut = true
      
      // 等待淡出动画完成后移除上传中消息并显示错误消息
      setTimeout(() => {
        // 移除上传中消息
        messages.value = messages.value.filter(m => !m.isUploading)
        
        // 添加错误消息
          const errorMessage = {
            id: Date.now() + 1,
            role: 'ai',
            content: `文件上传失败: ${error.message || '请稍后重试'}`,
            isError: true,
            entering: true, // 添加进入动画标志
            error: true // 添加error类用于CSS样式选择
          }
        messages.value.push(errorMessage)
        
        // 滚动到底部
        scrollToBottom()
        
        // 使用nextTick确保DOM更新后再处理动画
        nextTick(() => {
          setTimeout(() => {
            const msg = messages.value.find(m => m.id === errorMessage.id)
            if (msg) {
              msg.entering = false
            }
          }, ANIMATION_DURATIONS.transition)
        })
      }, ANIMATION_DURATIONS.fadeOut)
    }
  }
}

// 上传文件按钮点击事件
const uploadFile = () => {
  openFileSelector()
}

// 开启新对话
const startNewConversation = () => {
  // 保存当前对话到历史记录
  const currentConversation = conversationHistory.value.find(c => c.id === currentConversationId.value)
  if (currentConversation) {
    currentConversation.summary = messages.value.slice(-2).map(m => m.content).join('\n')
  }

  // 创建新对话
const newConversationId = Date.now()
currentConversationId.value = newConversationId
conversationHistory.value.unshift({
  id: newConversationId,
  title: '新对话',
  summary: '新开启的对话'
})
  
// 清空当前对话，重置状态并显示欢迎消息
isFirstMessage.value = true
messages.value = [
  {
    id: 1,
    role: 'ai',
    content: '你好，我是智慧党建助手，你想问我什么',
    isWelcome: true
  }
]
// 清除会话ID
localStorage.removeItem('session_id')
sessionStorage.removeItem('session_id')
// 滚动到底部
scrollToBottom()
}

// 发送消息
// 已经在第173行定义了sendMessage函数，这里删除重复定义

// 切换到历史对话
const switchToConversation = (id) => {
  currentConversationId.value = id
  // 这里应该根据对话ID加载对应的对话内容
  // 这里只做一个模拟
  messages.value = [
    {
      id: 1,
      role: 'ai',
      content: `这是ID为${id}的对话内容。在实际应用中，这里会加载真实的对话历史。`
    }
  ]
  isFirstMessage.value = false
  // 滚动到底部
  scrollToBottom()
}

// 滚动到底部 - 性能优化版本
const scrollToBottom = () => {
  // 使用requestAnimationFrame确保滚动平滑且不会导致布局抖动
  requestAnimationFrame(() => {
    const chatContainer = chatMessagesRef.value || document.querySelector('.chat-messages')
    if (chatContainer) {
      // 使用smooth滚动行为
      chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: 'smooth'
      })
    }
  })
}
</script>

<template>
  <div class="home-container">
    <!-- 党建主题导航栏 -->
    <!-- 顶部功能按钮 -->
    <div class="top-buttons left-aligned">
      <el-button 
        class="nav-button knowledge-base-button"
        @click="goToKnowledgeBaseHome"
        type="primary"
      >
        <Document />
        党建知识库
      </el-button>
      <el-button 
        class="nav-button personal-home-button"
        @click="goToPersonalHome"
        type="primary"
      >
        <User />
        党员空间
      </el-button>
    </div>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 左侧历史对话 -->
      <aside class="sidebar" :class="{ 'collapsed': isSidebarCollapsed }">
        <div class="sidebar-header">
          <button 
            class="sidebar-toggle-button"
            @click="toggleSidebar"
          >
            <ArrowRight v-if="isSidebarCollapsed" />
            <ArrowLeft v-else />
          </button>
          <div class="sidebar-header-content">
            <h2 class="sidebar-title" v-if="!isSidebarCollapsed">历史对话</h2>
          </div>
          <button 
            class="new-conversation-button"
            @click="startNewConversation"
            :class="{ 'collapsed': isSidebarCollapsed }"
          >
            开启新对话
          </button>
        </div>
        <div class="conversation-list">
          <div 
            v-for="conversation in conversationHistory"
            :key="conversation.id"
            class="conversation-item"
            :class="{ 'active': conversation.id === currentConversationId }"
            @click="switchToConversation(conversation.id)"
          >
            <div class="conversation-title">{{ conversation.title }}</div>
            <div class="conversation-summary">{{ conversation.summary }}</div>
          </div>
        </div>
      </aside>

      <!-- 中间对话区域 -->
      <section class="chat-area" :class="{ 'initial-state': isInitialState }">
        <div class="chat-messages" ref="chatMessagesRef">
            <div 
              v-for="message in messages" 
              :key="message.id" 
              class="message" 
              :class="[message.role, message.entering ? 'entering' : '', message.fadingOut ? 'fading-out' : '', message.error ? 'error' : '']"
            >
              <div v-if="!message.isWelcome" class="message-avatar">{{ message.role === 'ai' ? 'AI' : '我' }}</div>
              <div 
                class="message-content" 
                :data-is-welcome="message.isWelcome"
              >
                {{ message.content }}
              </div>
            </div>
          </div>

          <!-- 固定容器 -->
          <div 
            class="fixed-container"
            :class="{
              'fixed-bottom': !isInitialState,
              'sidebar-collapsed': !isInitialState && isSidebarCollapsed,
              'right-panel-expanded': !isInitialState && !isPanelCollapsed
            }"
          >
            <!-- 输入区域 -->
            <div class="input-area">
              <textarea
                v-model="inputMessage"
                placeholder="请输入您的问题..."
                class="message-input"
                :class="{'long-input': isFirstMessage && messages.length <= 1}"
                @keydown.enter="sendMessage"
              ></textarea>
              <!-- 隐藏的文件选择器 -->
              <input
                ref="fileInputRef"
                type="file"
                style="display: none"
                @change="handleFileSelect"
              />
            </div>
            
            <!-- 按钮区域 -->
            <div class="buttons-area">
            <div class="function-buttons">
              <el-button 
                :type="agentMode ? 'primary' : 'default'"
                @click="toggleAgentMode"
                size="default"
                class="agent-button"
              >
                <template #icon>
                  <Setting />
                </template>
                agent
              </el-button>
              <el-button 
                type="default"
                @click="uploadFile"
                size="default"
                class="upload-button"
              >
                <template #icon>
                  <Upload />
                </template>
                文件上传
              </el-button>
            </div>
            <div class="send-button-container">
              <el-button 
                type="primary"
                @click="sendMessage"
                size="default"
              >
                <template #icon>
                  <Paperclip />
                </template>
                发送
              </el-button>
            </div>
          </div>
        </div>
      </section>

      <!-- 右侧信息区域 -->
      <aside class="info-panel" :class="{ 'collapsed': isPanelCollapsed }">
        <div class="info-header">
          <div class="header-content">
            <h2 class="info-title">AI助手信息</h2>
            <el-button 
              type="text" 
              class="toggle-button"
              @click="togglePanel"
            >
              <template #icon>
                <ArrowLeft v-if="isPanelCollapsed" />
                <ArrowRight v-else />
              </template>
            </el-button>
          </div>
        </div>
        
        <div v-if="!isPanelCollapsed" class="info-content">
          <p class="welcome-text">欢迎使用智慧党建AI助手</p>

          <!-- 回调链接信息模块 -->
        <div class="callback-links-module">
          <h3>回调链接信息</h3>
          <div class="links-container">
            <div v-for="link in callbackLinks" :key="link.id" class="link-item">
              <div class="link-header">
                <div class="link-title">回调链接 #{{ link.id }}</div>
                <div :class="['link-status', link.statusClass]">{{ link.status }}</div>
              </div>
              <div class="link-url">
                <span class="url-text">{{ link.url }}</span>
                <button class="copy-button" @click="copyLink(link.url)" title="复制链接">复制</button>
              </div>
              <div class="link-meta">
                <span class="meta-item">生成时间: {{ link.timestamp }}</span>
              </div>
            </div>
            <div v-if="callbackLinks.length === 0" class="no-links">
              当前没有回调链接
            </div>
          </div>
        </div>
        </div>
        
        <!-- AI生成文件区域已移除 -->
      </aside>
    </main>


  </div>
</template>

<style scoped>
/* 党建主题样式 */
.home-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100vw;
  background-color: var(--color-background-primary);
  background-image: 
    linear-gradient(to bottom, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.85)),
    url('data:image/svg+xml,%3Csvg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"%3E%3Cpath d="M50 50 C55 45 60 50 65 50 C60 55 55 60 50 65 C45 60 40 55 35 50 C40 45 45 40 50 50 Z" fill="%23c8102e" fill-opacity="0.05"/%3E%3C/svg%3E');
  background-size: cover;
  background-position: center;
  position: relative;
}

/* 党建主题导航栏 */
/* 顶部功能按钮 */
.top-buttons {
  display: flex;
  justify-content: flex-start;
  padding: 15px 30px;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  margin-left: 120px;
  background-color: white;
  height: 60px;
  border-bottom: none;
  align-items: center;
}

.top-buttons .nav-button {
  margin-left: 15px;
  border-radius: 20px;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(200, 16, 46, 0.3);
}

/* 装饰元素 */
.header-decoration-left,
.header-decoration-right {
  position: absolute;
  height: 100%;
  width: 120px;
  background-image: 
    linear-gradient(135deg, transparent 49%, var(--color-gold) 49%, var(--color-gold) 51%, transparent 51%),
    linear-gradient(45deg, transparent 49%, var(--color-gold) 49%, var(--color-gold) 51%, transparent 51%);
  background-size: 20px 20px;
  opacity: 0.15;
}

.header-decoration-left {
  left: 0;
  top: 0;
}

.header-decoration-right {
  right: 0;
  top: 0;
}

.logo-container {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
}

.logo-text {
  display: flex;
  align-items: center;
  gap: 12px;
}

.party-logo {
  width: 40px;
  height: 40px;
  background-color: var(--color-gold);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.3);
}

.logo-title {
  font-size: 22px;
  font-weight: bold;
  color: #fff;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.nav {
  display: flex;
  gap: 15px;
}

.nav-button {
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 1px solid transparent;
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
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.nav-button:hover::before {
  left: 100%;
}

.knowledge-base-button,
.personal-home-button {
  background-color: rgba(255, 255, 255, 0.2);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.3);
}

.knowledge-base-button:hover,
.personal-home-button:hover {
  background-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.knowledge-base-button:active,
.personal-home-button:active {
  transform: translateY(0);
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.user-role {
  font-size: 12px;
  color: var(--color-gold);
  font-weight: 500;
}

.username {
  font-size: 14px;
  color: #fff;
  background-color: rgba(255, 215, 0, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid rgba(255, 215, 0, 0.3);
}



.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
  transition: all 0.3s ease;
  background-color: var(--color-background-secondary);
  position: relative;
}

/* 侧边栏样式 - 党建主题 */
.sidebar {
  width: 260px;
  background-color: var(--color-background-primary);
  border-right: 1px solid var(--color-border-light);
  display: flex;
  flex-direction: column;
  position: relative;
  margin-top: 0;
  padding-top: 0;
}

/* 侧边栏装饰元素 */
.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  width: 3px;
  background: linear-gradient(to bottom, var(--color-primary), transparent, var(--color-gold), transparent);
}


.sidebar-header {
  padding: 20px 20px 0;
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--color-border-light);
  padding-bottom: 15px;
}

.sidebar-title {
  font-size: 18px;
  font-weight: bold;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.sidebar-title::before {
  content: '';
  width: 6px;
  height: 20px;
  background-color: var(--color-primary);
  border-radius: 3px;
}

.new-conversation-button {
  width: 200px;
  margin: 15px 20px 15px 10px;
  padding: 10px 20px;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 2px 6px rgba(200, 16, 46, 0.3);
}

.new-conversation-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.4);
}

.new-conversation-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(200, 16, 46, 0.3);
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px 20px;
}

/* 自定义滚动条 - 党建主题 */
.conversation-list::-webkit-scrollbar {
  width: 6px;
}

.conversation-list::-webkit-scrollbar-track {
  background: var(--color-background-secondary);
  border-radius: 3px;
}

.conversation-list::-webkit-scrollbar-thumb {
  background: var(--color-border-light);
  border-radius: 3px;
}

.conversation-list::-webkit-scrollbar-thumb:hover {
  background: var(--color-gold);
}

.conversation-item {
  padding: 15px;
  margin-bottom: 12px;
  background-color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.conversation-item:hover {
  background-color: var(--color-background-secondary);
  transform: translateX(3px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}

.conversation-item.active {
  border-left: 3px solid var(--color-primary);
  background-color: rgba(200, 16, 46, 0.05);
  box-shadow: 0 2px 8px rgba(200, 16, 46, 0.15);
}

.conversation-title {
  font-size: 15px;
  font-weight: bold;
  color: var(--color-text-primary);
  margin-bottom: 5px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.conversation-summary {
  font-size: 13px;
  color: var(--color-text-secondary);
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 聊天区域样式 - 党建主题 */
.chat-area {
  margin-top: 60px;
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: white;
  height: 100%;
  transition: all 0.3s ease;
  position: relative;
  border-right: 1px solid var(--color-border-light);
}

/* 初始状态下的居中布局 */
.chat-area.initial-state {
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.95);
}

.chat-area.initial-state .chat-messages {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 0;
  padding: 50px 0;
}

/* 发送消息后平滑过渡到正常状态 */
.chat-area:not(.initial-state) {
  justify-content: flex-start;
}

/* 党建主题装饰线 */
.chat-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 2px;
  background: linear-gradient(to bottom, transparent, var(--color-gold), transparent, var(--color-primary), transparent);
  opacity: 0.7;
}

.chat-messages {
  flex: 1;
  max-height: calc(100vh - 220px);
  overflow-y: auto;
  padding: 25px;
  display: flex;
  flex-direction: column;
  background-color: var(--color-background-primary);
}

/* 当输入区域固定时，调整聊天消息区域 */
.chat-area:not(.initial-state) .chat-messages {
  max-height: calc(100vh - 320px);
  padding-bottom: 150px;
}

/* 自定义滚动条 - 党建主题 */
.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: var(--color-background-secondary);
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background-color: var(--color-gold);
  border-radius: 4px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background-color: var(--color-gold-dark);
}

.message-wrapper {
  margin-bottom: 100px;
  padding-bottom: 20px;
  clear: both;
}

.message {
  display: flex;
  max-width: 75%;
  margin-bottom: 22px;
  opacity: 1;
  transform: translateY(0);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
}

/* 欢迎消息居中显示 - 党建主题 */
.message:has(.message-content[data-is-welcome="true"]) {
  align-self: center;
  max-width: 60%;
  opacity: 1;
  transition: opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1), transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

/* 所有消息淡出动画 */
.message.fading-out {
  opacity: 0 !important;
  transform: translateY(-10px);
  transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1), transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

/* 消息进入动画 */
.message.entering {
  opacity: 0;
  transform: translateY(15px);
  animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* 党建主题淡入动画增强 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 错误消息样式 - 使用更广泛支持的类选择器替代:has()选择器 */
.message.error .message-content {
  background-color: #fff1f0;
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.message.error .message-avatar {
  background-color: var(--color-primary);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* AI消息样式 */
.message.ai {
  align-self: flex-start;
}

/* 用户消息样式 */
.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

/* 头像样式 */
.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  margin-right: 12px;
  box-shadow: 0 2px 6px rgba(200, 16, 46, 0.3);
}

.message.user .message-avatar {
  background-color: #1E90FF;
  color: white;
  margin-right: 0;
  margin-left: 12px;
}

/* 消息内容样式 */
.message-content {
  padding: 14px 18px;
  border-radius: 18px;
  background-color: white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  word-break: break-word;
  line-height: 1.6;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  will-change: background-color, box-shadow, border-color;
  border: 1px solid var(--color-border-light);
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 欢迎消息特殊样式 - 党建主题 */
.message-content[data-is-welcome="true"] {
  background: linear-gradient(135deg, var(--color-background-secondary) 0%, var(--color-background-primary) 100%);
  color: var(--color-primary);
  font-size: 20px;
  font-weight: bold;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80px;
  padding: 20px 30px;
  border: 2px solid var(--color-gold);
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.1);
  border-radius: 12px;
}

/* 用户消息内容样式 - 党建主题 */
.message.user .message-content {
  background-color: #f5f5f5;
  color: #000000;
  border-color: #e0e0e0;
}

/* AI消息内容样式 - 党建主题 */
.message.ai .message-content {
  background-color: var(--color-background-secondary);
  border-color: var(--color-border-light);
  color: var(--color-text-primary);
}

/* 输入区域 - 党建主题 */
.input-area {
   padding: 15px 0;
   border-top: 1px solid var(--color-border-light);
   background-color: var(--color-background-secondary);
   position: relative;
   display: flex;
   flex-direction: column;
   align-items: center;
 }
 
 .fixed-container.fixed-bottom {
   position: fixed;
   bottom: 0;
   left: calc(260px + 150px);
   right: 150px;
   z-index: 100;
   transition: all 0.3s ease;
   max-width: calc(100vw - 260px - 300px);
 }
 
 /* 侧边栏折叠时的固定容器 */
 .fixed-container.fixed-bottom.sidebar-collapsed {
   left: calc(70px + 150px);
   right: 150px;
   max-width: calc(100vw - 70px - 300px);
 }

 /* 右侧面板展开时的固定容器 */
 .fixed-container.fixed-bottom.right-panel-expanded {
   right: calc(150px + 240px); /* 右侧面板宽度为240px */
   max-width: calc(100vw - 260px - (150px + 240px)); /* 260px为侧边栏宽度，150px为原右侧边距，240px为右侧面板宽度 */
 }

 /* 右侧面板展开且侧边栏折叠时的固定容器 */
 .fixed-container.fixed-bottom.right-panel-expanded.sidebar-collapsed {
   max-width: calc(100vw - 70px - (150px + 240px)); /* 70px为折叠后的侧边栏宽度 */
 }

 /* 适配小屏幕 */
 @media (max-width: 768px) {
   .fixed-container.fixed-bottom {
     left: 0;
     right: 0;
     max-width: 100vw;
   }
 
   .fixed-container.fixed-bottom.sidebar-collapsed {
     left: 0;
     right: 0;
     max-width: 100vw;
   }
 }

/* 输入区域装饰元素 */
.input-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(to right, transparent, var(--color-gold), transparent);
}

.message-input {
  width: 100%;
  height: 70px;
  padding: 15px;
  border: 2px solid var(--color-primary);
  border-radius: 8px;
  resize: none;
  font-size: 14px;
  margin-bottom: 12px;
  background-color: white;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(200, 16, 46, 0.2);
}

.message-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.1), 0 4px 12px rgba(200, 16, 46, 0.3);
}

/* 初始状态下的长输入框 */
.long-input {
   width: 800px;
   max-width: 90vw;
 }

.input-buttons {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 12px;
}

/* 兼容ElementPlus按钮的样式 - 党建主题 */
.input-buttons :deep(.el-button) {
  margin-left: 0;
  margin-right: 0;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 党建主题按钮悬停效果 */
.input-buttons :deep(.el-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(200, 16, 46, 0.2);
}

/* 上传按钮 - 党建主题 */
.input-buttons :deep(.el-button i.el-icon-upload) {
  font-size: 16px;
}

/* 新按钮区域 - 党建主题 */
.buttons-area {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px 15px;
  gap: 15px;
}

/* agent和文件上传按钮 - 党建主题 */
.function-buttons {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 12px;
}

/* 发送按钮容器 - 党建主题 */
.send-button-container {
  display: flex;
  justify-content: flex-end;
}

/* 发送按钮样式增强 - 党建主题 */
.send-button-container .el-button {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border: none;
  color: white;
  padding: 10px 24px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.send-button-container .el-button:hover {
  background: linear-gradient(135deg, var(--color-primary-dark) 0%, var(--color-primary) 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.3);
}

/* 发送按钮容器 */
.send-button-container {
  display: flex;
  justify-content: flex-end;
}

/* 兼容ElementPlus按钮的样式 - 自定义美化 */
.function-buttons .el-button, .send-button-container .el-button {
  margin-left: 0;
  margin-right: 0;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
  justify-content: center;
}

/* agent和文件上传按钮默认白色样式 */
.function-buttons .el-button:default {
  background-color: white;
  color: #333;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* agent按钮启用时保持蓝色 */
.function-buttons .el-button:primary {
  background: linear-gradient(135deg, #6c63ff 0%, #5a4de0 100%);
  color: white;
  border: none;
}

.function-buttons .el-button:hover:not(:primary) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.function-buttons .el-button:hover:primary {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(108, 99, 255, 0.4);
}

.function-buttons .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(108, 99, 255, 0.4);
}

.function-buttons .el-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(108, 99, 255, 0.3);
}

.send-button-container .el-button {
  padding: 10px 24px;
  box-shadow: 0 2px 6px rgba(108, 99, 255, 0.2);
}

.send-button-container .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(108, 99, 255, 0.4);
}

.send-button-container .el-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(108, 99, 255, 0.3);
}

/* 上传按钮图标 */
.function-buttons .el-button i.el-icon-upload {
  font-size: 16px;
}

/* AI生成文件相关样式已移除 */

/* AI生成文件相关样式已移除 */

/* 信息面板样式 */
.info-panel {
  width: 280px;
  background-color: rgba(245, 245, 245, 0.85);
  border-left: 1px solid rgba(224, 224, 224, 0.5);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
  border-radius: 12px 0 0 12px;
  border-top: 1px solid rgba(224, 224, 224, 0.5);
  border-bottom: 1px solid rgba(224, 224, 224, 0.5);
  flex-shrink: 0;
  margin-top: 0;
  padding-top: 0;
}

.info-panel.collapsed {
  width: 50px;
  background-color: transparent;
  border: none;
  border-radius: 0;
}

.info-header {
  position: relative;
  padding: 15px;
  transition: all 0.3s ease;
}

.info-panel.collapsed .info-header {
  padding: 0;
  text-align: center;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.info-panel.collapsed .header-content {
  justify-content: center;
}

.toggle-button {
  background-color: var(--color-primary);
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.3s ease;
  display: flex !important;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  min-height: 32px;
  box-shadow: 0 2px 4px rgba(200, 16, 46, 0.2);
  visibility: visible !important;
  opacity: 1 !important;
  z-index: 1000;
  align-self: flex-start;
  flex-shrink: 0;
}
  
.toggle-button:hover {
  background-color: var(--color-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 3px 6px rgba(200, 16, 46, 0.3);
  color: white;
}
  
.toggle-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(200, 16, 46, 0.3);
}

/* 提示词容器 */
.prompt-container {
  width: 100%;
  padding: 15px;
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

/* 主伸缩面板样式 - 优化动画性能 */
.main-collapse {
  margin-top: 10px;
  background-color: rgba(255, 255, 255, 0.95);
  border: 2px solid var(--color-primary);
  border-radius: 12px;
  overflow: visible;
  contain: layout style paint; /* 添加contain属性优化渲染性能 */
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.1);
}

/* 覆盖Element Plus的默认动画持续时间，确保动画流畅 */
:root {
  --el-collapse-transition: height 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.main-collapse :deep(.el-collapse-item) {
  border-radius: 10px;
  margin-bottom: 15px;
  overflow: hidden;
  contain: layout style paint; /* 添加contain属性优化渲染性能 */
}

.main-collapse :deep(.el-collapse-item__header) {
  background-color: rgba(255, 255, 255, 0.98);
  border-radius: 12px 12px 0 0;
  padding: 18px 16px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-size: 17px;
  color: var(--color-text-primary);
  font-weight: 600;
  border: none;
  position: relative;
  overflow: hidden;
  will-change: transform, box-shadow;
}

.main-collapse :deep(.el-collapse-item__header)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 6px;
  background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-gold) 100%);
  border-radius: 12px 0 0 12px;
}

.main-collapse :deep(.el-collapse-item__header:hover) {
  background-color: rgba(235, 235, 235, 0.9);
  box-shadow: 0 4px 15px rgba(200, 16, 46, 0.15);
  transform: translateY(-1px);
}

.main-collapse :deep(.el-collapse-item__content) {
  padding: 15px;
  background-color: rgba(255, 255, 255, 0.95);
  box-shadow: none;
  border-radius: 0 0 10px 10px;
  border-top: none;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  will-change: opacity, transform;
  position: relative;
}

/* 内容区域党建主题装饰 */
.main-collapse :deep(.el-collapse-item__content)::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(to right, transparent, var(--color-primary), var(--color-gold), var(--color-primary), transparent);
}

/* 二级面板标题样式美化 - 党建主题 */
.sub-collapse {
  margin-top: 10px;
  min-height: 250px; /* 增加最小高度以完整展示四个二级标题 */
  max-height: 350px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--color-primary) var(--color-background-secondary);
  border-radius: 8px;
  background-color: transparent;
  padding: 8px;
  border: none;
}

.sub-collapse::-webkit-scrollbar {
  width: 6px;
}

.sub-collapse::-webkit-scrollbar-track {
  background: var(--color-background-secondary);
  border-radius: 3px;
}

.sub-collapse::-webkit-scrollbar-thumb {
  background-color: var(--color-primary);
  border-radius: 3px;
}

.sub-collapse :deep(.el-collapse-item) {
  margin-bottom: 12px;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.sub-collapse :deep(.el-collapse-item__header) {
  border-radius: 8px 8px 0 0;
  padding: 12px 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
  font-size: 14px;
  color: var(--color-text-primary);
  font-weight: 500;
  border: 1px solid var(--color-border-light);
  border-bottom: none;
  margin-bottom: 0;
  position: relative;
  overflow: hidden;
}

/* 为四个二级面板添加差异化左侧边框颜色 */
.sub-collapse :deep(.el-collapse-item:nth-child(1) .el-collapse-item__header) {
    background-color: #fff0f2 !important;
    border-color: #ffdee0 !important;
    border-bottom: 1px solid #ffdee0 !important;
  }

  .sub-collapse :deep(.el-collapse-item:nth-child(2) .el-collapse-item__header) {
    background-color: #fff8e6 !important;
    border-color: #ffeeba !important;
    border-bottom: 1px solid #ffeeba !important;
  }

  .sub-collapse :deep(.el-collapse-item:nth-child(3) .el-collapse-item__header) {
    background-color: #f1faf3 !important;
    border-color: #c3e6cb !important;
    border-bottom: 1px solid #c3e6cb !important;
  }

  .sub-collapse :deep(.el-collapse-item:nth-child(4) .el-collapse-item__header) {
    background-color: #e6f3ff !important;
    border-color: #b3d7ff !important;
    border-bottom: 1px solid #b3d7ff !important;
  }

  /* 为四个二级面板添加差异化内容背景色 */
  .sub-collapse :deep(.el-collapse-item:nth-child(1) .el-collapse-item__content) {
    background-color: #fff5f7 !important;
    border-color: #ffdee0 !important;
    border-left: 1px solid #ffdee0 !important;
    border-right: 1px solid #ffdee0 !important;
    border-bottom: 1px solid #ffdee0 !important;
  }

  .sub-collapse :deep(.el-collapse-item:nth-child(2) .el-collapse-item__content) {
    background-color: #fffae6 !important;
    border-color: #ffeeba !important;
    border-left: 1px solid #ffeeba !important;
    border-right: 1px solid #ffeeba !important;
    border-bottom: 1px solid #ffeeba !important;
  }

  .sub-collapse :deep(.el-collapse-item:nth-child(3) .el-collapse-item__content) {
    background-color: #f5fff8 !important;
    border-color: #c3e6cb !important;
    border-left: 1px solid #c3e6cb !important;
    border-right: 1px solid #c3e6cb !important;
    border-bottom: 1px solid #c3e6cb !important;
  }

  .sub-collapse :deep(.el-collapse-item:nth-child(4) .el-collapse-item__content) {
    background-color: #edf7ff !important;
    border-color: #b3d7ff !important;
    border-left: 1px solid #b3d7ff !important;
    border-right: 1px solid #b3d7ff !important;
    border-bottom: 1px solid #b3d7ff !important;
  }

/* 二级面板标题党建主题装饰 */
.sub-collapse :deep(.el-collapse-item__header)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 4px;
}

/* 为四个二级面板添加差异化左侧边框颜色 */
.sub-collapse :deep(.el-collapse-item:nth-child(1) .el-collapse-item__header)::before {
  background: linear-gradient(180deg, #c8102e 0%, #dc3545 100%);
}

.sub-collapse :deep(.el-collapse-item:nth-child(2) .el-collapse-item__header)::before {
  background: linear-gradient(180deg, #ffc107 0%, #fd7e14 100%);
}

.sub-collapse :deep(.el-collapse-item:nth-child(3) .el-collapse-item__header)::before {
  background: linear-gradient(180deg, #28a745 0%, #20c997 100%);
}

.sub-collapse :deep(.el-collapse-item:nth-child(4) .el-collapse-item__header)::before {
  background: linear-gradient(180deg, #007bff 0%, #17a2b8 100%);
}

.sub-collapse :deep(.el-collapse-item__header:hover) {
  box-shadow: 0 3px 8px rgba(200, 16, 46, 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
  transform: translateX(3px);
  background-color: #f8f9ff !important;
}

.sub-collapse :deep(.el-collapse-item__content) {
  padding: 15px;
  min-height: 50px; /* 确保内容区域有足够高度 */
  border-radius: 0 0 8px 8px;
  border-top: none;
  transition: all 0.3s ease;
  margin-bottom: 0;
}

/* 一级收缩面板样式 - 移除了下拉条 */
/* 已合并到上面的.main-collapse样式中 */

.prompt-content {
  cursor: pointer;
  padding: 12px;
  border-radius: 8px;
  background-color: rgba(245, 245, 245, 0.85);
  border: 1px solid var(--color-border-light);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.prompt-content::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  width: 0;
  background: linear-gradient(90deg, var(--color-primary) 0%, var(--color-gold) 100%);
  transition: width 0.3s ease;
}

.prompt-content:hover {
  background-color: #f8f9ff;
  border-color: var(--color-primary);
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(200, 16, 46, 0.1);
}

.prompt-content:hover::after {
  width: 100%;
}

.prompt-content p {
  margin: 0;
  color: #495057;
  line-height: 1.6;
  font-size: 13px;
}

/* 提示词列表样式 */
.prompt-list {
  padding-left: 20px;
  margin: 10px 0;
}

.prompt-list li {
  margin-bottom: 8px;
  line-height: 1.6;
  color: #495057;
  font-size: 13px;
  position: relative;
}

.prompt-list li::marker {
  color: var(--color-primary);
  font-weight: bold;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .info-panel {
    width: 240px;
    position: absolute;
    right: 0;
    top: 0;
    height: 100%;
    z-index: 50;
  }
  
  .info-panel.collapsed {
    width: 50px;
    display: flex;
    flex-direction: column;
  }
  
  .toggle-button {
    position: absolute;
    right: 10px;
    top: 10px;
    transform: none;
    background-color: var(--color-primary);
    border: none;
    color: white;
    font-size: 18px;
    cursor: pointer;
    padding: 8px 12px;
    border-radius: 4px;
    transition: all 0.3s ease;
    display: flex !important;
    align-items: center;
    justify-content: center;
    min-width: 32px;
    min-height: 32px;
    box-shadow: 0 2px 4px rgba(200, 16, 46, 0.2);
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 1000;
    align-self: flex-start;
  }
  
  .toggle-button:hover {
    background-color: var(--color-primary-hover);
    transform: translateY(-1px);
    box-shadow: 0 3px 6px rgba(200, 16, 46, 0.3);
  }
  
  .chat-area {
    width: 100%;
  }
}

.info-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-heading);
  margin-bottom: 20px;
  transition: all 0.3s ease;
  padding-left: 12px;
  border-left: 4px solid var(--color-border-accent);
  letter-spacing: 0.5px;
}

.info-panel.collapsed .info-title {
  display: none;
}

.info-panel.collapsed .header-content {
  justify-content: center;
}

.info-panel.collapsed .info-content {
  display: none;
}

.info-panel.collapsed .toggle-button {
  position: static;
  transform: none;
}

.info-content {
  padding: 0 15px 15px;
  flex: 1;
  overflow-y: auto;
  transition: all 0.3s ease;
  /* 确保滚动条在所有浏览器中都能正常显示 */
  scrollbar-width: thin;
  scrollbar-color: var(--color-primary) var(--color-background-secondary);
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 0 0 10px 10px;
}

.info-content::-webkit-scrollbar {
  width: 8px;
}

.info-content::-webkit-scrollbar-track {
  background: var(--color-background-secondary);
  border-radius: 4px;
}

.info-content::-webkit-scrollbar-thumb {
  background-color: var(--color-primary);
  border-radius: 4px;
}

.info-panel.collapsed .info-content {
  display: none;
}

/* 提示词区域样式 */
.welcome-text {
  font-size: 16px;
  color: var(--color-heading);
  font-weight: 600;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--color-border-accent);
  text-align: center;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.prompt-section-title {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
}

/* 标题前的党建主题装饰 */
.prompt-section-title::before {
  content: '◆';
  color: var(--color-gold);
  font-size: 10px;
  margin-right: 6px;
}

.prompt-categories {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.prompt-category {
  background-color: white;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid var(--color-border-light);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

/* 提示词类别党建主题装饰 */
.prompt-category::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, var(--color-primary) 0%, var(--color-gold) 100%);
}

.prompt-category:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
  border-color: var(--color-primary);
}

.prompt-category:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.prompt-category-title {
  font-size: 12px;
  font-weight: bold;
  color: var(--color-primary);
  margin-bottom: 6px;
  display: flex;
  align-items: center;
}

.prompt-description {
  font-size: 11px;
  color: #666;
  line-height: 1.5;
}

.prompt-list {
  padding-left: 15px;
  margin: 0;
}

.prompt-list li {
  margin-bottom: 4px;
  position: relative;
}

.prompt-list li:last-child {
  margin-bottom: 0;
}

/* 左侧历史对话面板收缩样式 */
.sidebar {
  position: relative;
  transition: width 0.3s ease;
  background-color: var(--color-background-secondary);
  border-right: 1px solid var(--color-border-light);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08);
}

.sidebar.collapsed {
  width: 70px;
}

.sidebar-header {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    padding: 15px;
    border-bottom: 1px solid var(--color-border-light);
    gap: 10px;
  }

.sidebar-header-content {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 10px;
}

.sidebar-toggle-button {
  background-color: var(--color-primary);
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.3s ease;
  display: flex !important;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  min-height: 32px;
  box-shadow: 0 2px 4px rgba(200, 16, 46, 0.2);
  visibility: visible !important;
  opacity: 1 !important;
  z-index: 1000;
  align-self: flex-start;
  flex-shrink: 0;
}

.sidebar-toggle-button:hover {
  background-color: var(--color-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 3px 6px rgba(200, 16, 46, 0.3);
}

.sidebar-toggle-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(200, 16, 46, 0.3);
}

.sidebar.collapsed .sidebar-title {
  display: none;
}

.sidebar.collapsed .new-conversation-button {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  padding: 0;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  margin-top: 10px;
}

.sidebar.collapsed .new-conversation-button::before {
  content: '+';
  font-size: 24px;
}

.sidebar.collapsed .new-conversation-button::after {
  content: none;
}

.sidebar.collapsed .conversation-title, 
.sidebar.collapsed .conversation-summary {
  display: none;
}

.sidebar.collapsed .conversation-item {
  padding: 10px 0;
  justify-content: center;
}

.sidebar.collapsed .conversation-list {
  display: none;
}

.sidebar.collapsed .sidebar-header-content {
  display: none;
}

.sidebar.collapsed .new-conversation-button {
  display: none;
}

.sidebar.collapsed .sidebar-header {
  padding: 10px;
  align-items: center;
}

/* 回调链接信息模块样式 */
.callback-links-module {
  margin-top: 25px;
  padding: 15px;
  border-top: 2px solid var(--color-border-accent);
  position: relative;
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 模块分隔线党建主题装饰 */
.callback-links-module::before {
  content: '';
  position: absolute;
  top: 0;
  left: 15px;
  right: 15px;
  height: 1px;
  background: linear-gradient(to right, transparent, var(--color-gold), transparent);
}

.callback-links-module h3 {
  font-size: 16px;
  color: var(--color-heading);
  margin-bottom: 15px;
  font-weight: 600;
  padding-left: 12px;
  border-left: 4px solid var(--color-primary);
}

.links-container {
  width: 100%;
}

.link-item {
  background-color: var(--color-background-secondary);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
  border: 1px solid var(--color-border-light);
  transition: all 0.3s ease;
}

.link-item:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(200, 16, 46, 0.1);
}

.link-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.link-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.link-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-valid {
  background-color: #e8f5e8;
  color: #4caf50;
  border: 1px solid #4caf50;
}

.status-expired {
  background-color: #ffebee;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.link-url {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
}

.url-text {
  flex: 1;
  font-size: 13px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.copy-button {
  padding: 4px 8px;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 3px;
  font-size: 12px;
  cursor: pointer;
  margin-left: 8px;
  transition: all 0.3s ease;
}

.copy-button:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(200, 16, 46, 0.3);
}

.link-meta {
  margin-top: 4px;
}

.meta-item {
  font-size: 12px;
  color: #666;
  display: block;
}

.no-links {
  text-align: center;
  color: #999;
  padding: 20px;
  font-size: 13px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

/* 高亮占位符样式 */
.prompt-description [class^="el-icon-"],
.prompt-description [class*=" el-icon-"] {
  vertical-align: middle;
  margin-right: 4px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .info-panel {
    width: 100%;
    border-left: none;
    border-top: 1px solid #e0e0e0;
  }

  .prompt-category {
    padding: 8px;
  }

  .prompt-category-title {
    font-size: 11px;
  }

  .prompt-description {
    font-size: 10px;
  }
}

.info-content p {
  margin-bottom: 10px;
  color: #666;
}

.info-content ul {
  margin-left: 20px;
  margin-bottom: 15px;
}

.info-content li {
  margin-bottom: 5px;
  color: #666;
}

.tip {
  font-size: 12px;
  color: #ff9800;
  background-color: #fff8e1;
  padding: 8px;
  border-radius: 4px;
}

/* 添加个人首页按钮样式 */
.personal-home-button {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
}

.personal-home-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
}

.personal-home-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(231, 76, 60, 0.3);
}
</style>