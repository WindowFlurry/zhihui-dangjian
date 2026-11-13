import axios from 'axios'

// RAG 服务与原有 mock 后端（5000）分开，避免影响登录/Agent 等既有接口
const baseURL = import.meta.env.VITE_RAG_API_BASE || 'http://127.0.0.1:8000'

const service = axios.create({
  baseURL,
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' }
})

service.interceptors.response.use(
  response => response.data,
  error => {
    const detail = error.response?.data?.detail
    const message = detail || error.response?.data?.message || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

export const askQuestion = (question, sessionId = '') =>
  service.post('/knowledge/ask', {
    question,
    session_id: sessionId || undefined
  })

export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return service.post('/knowledge/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 180000
  })
}

export const getHealth = () => service.get('/health')

export const getFiles = () => service.get('/knowledge/files')

export const getDocument = (docId) =>
  service.get(`/knowledge/documents/${encodeURIComponent(docId)}`)

export default { askQuestion, uploadFile, getHealth, getFiles, getDocument }
